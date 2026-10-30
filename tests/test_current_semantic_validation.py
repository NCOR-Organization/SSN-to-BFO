#!/usr/bin/env python3
"""Current-track exact-input and real-HermiT deductive-difference regressions."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from rdflib import Graph, Namespace, OWL, RDF, RDFS, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_semantic_validation as validation
import current_semantic_invocation as custody


class ExactInputTests(unittest.TestCase):
    def test_flattening_only_removes_import_directives(self):
        graph, info = validation.load_exact_local_graph(validation.SOURCE_PATHS)
        expected = Graph()
        for p in validation.SOURCE_PATHS:
            expected.parse(ROOT / p, format="turtle")
        # Blank nodes are fresh on each parse; compare graph isomorphism.
        from rdflib.compare import isomorphic
        expected.remove((None, OWL.imports, None))
        self.assertTrue(isomorphic(graph, expected))
        sosa = Namespace("http://www.w3.org/ns/sosa/")
        self.assertIn((sosa.isSampleOf, RDF.type, OWL.FunctionalProperty), graph)
        self.assertIn((sosa.hasSample, RDF.type, OWL.InverseFunctionalProperty), graph)
        self.assertEqual(info["removed_logical_axioms"], 0)
        self.assertEqual({i["import"] for i in info["unresolved_imports"]}, {"http://www.w3.org/2004/02/skos/core"})

    def test_graph_identity_preserves_blank_node_sharing_and_multiplicity(self):
        from rdflib import BNode
        a, b, renamed = BNode(), BNode(), BNode()
        subject, other, predicate = URIRef("urn:s"), URIRef("urn:t"), URIRef("urn:p")
        shared, distinct, equivalent, duplicate = Graph(), Graph(), Graph(), Graph()
        for graph, left, right in ((shared, a, a), (distinct, a, b), (equivalent, renamed, renamed)):
            graph.add((subject, predicate, left))
            graph.add((other, predicate, right))
        duplicate += shared
        duplicate.add((subject, predicate, b))
        duplicate.add((other, predicate, b))
        self.assertEqual(validation.graph_identity(shared), validation.graph_identity(equivalent))
        self.assertNotEqual(validation.graph_identity(shared), validation.graph_identity(distinct))
        self.assertNotEqual(validation.graph_identity(shared), validation.graph_identity(duplicate))

    def test_corpus_is_eleven_and_synthetic_is_separate(self):
        examples = validation.source_examples()
        self.assertEqual(len(examples), 11)
        self.assertNotIn(validation.FIXTURE_PATH, examples)
        self.assertTrue((ROOT / validation.FIXTURE_PATH).exists())

    def test_source_fixture_matches_established_smoke_fixture(self):
        import test_instance_data
        from rdflib.compare import isomorphic
        expected = Graph()
        test_instance_data.add_sample_relationship_fixture(expected)
        actual = Graph().parse(ROOT / validation.FIXTURE_PATH, format="turtle")
        self.assertTrue(isomorphic(expected, actual))

    def test_classification_distinguishes_semantic_failure_from_unknown(self):
        for source, aligned, expected in (
            ("inconsistent", "consistent", "source-intrinsic inconsistency"),
            ("consistent", "inconsistent", "mapping-induced inconsistency"),
            ("consistent", "consistent", "aligned consistent"),
            ("technical_failure", "inconsistent", "technical/tool failure"),
            ("consistent", "technical_failure", "technical/tool failure"),
        ):
            self.assertEqual(validation.classify_example({"status": source}, {"status": aligned}), expected)

    def test_missing_result_is_not_zero_difference(self):
        result = validation.approximate_difference({"status": "technical_failure"}, {"status": "consistent"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["additions_count"])
        self.assertIsNone(result["losses_count"])

    def test_missing_materialization_is_not_empty_materialization(self):
        result = validation.approximate_difference(
            {"status": "consistent", "reasoner_result": {}},
            {"status": "consistent", "reasoner_result": {}})
        self.assertEqual(result["status"], "BLOCKED")

    def test_proposals_cover_positive_negative_and_required_cases(self):
        manifest = json.loads((ROOT / validation.MANIFEST_PATH).read_text())
        approved, proposed = validation.selected_expectations(manifest)
        self.assertEqual(approved, [])
        self.assertEqual(len(proposed), 16)
        self.assertEqual({item["expected_entailed"] for item in proposed}, {True, False})
        self.assertEqual({item["coverage"] for item in proposed}, {
            "simple_subsumption", "equivalence", "complex_class_expression", "existential_restriction",
            "object_property_subsumption", "property_chain", "deliberately_broad_source_term", "typing_only_no_direct_case"})
        for item in proposed:
            self.assertTrue(item["motivation"])
            for path in item["evidence"]: self.assertTrue((ROOT / path).exists(), path)

    def test_claimed_approval_without_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "human approval"):
            validation.selected_expectations({"expectations": [{"id": "x", "review_state": "approved"}]})

    def test_hash_drift_and_corpus_drift_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            file = root / "input.ttl"
            file.write_text("old")
            report = {"head": "test-head", "bound_files": [validation.fingerprint(file, root)], "examples": []}
            file.write_text("changed")
            with patch.object(validation, "git_value", return_value="test-head"):
                self.assertTrue(any("hash differs" in e for e in validation.validate_stored(report, root)))
            report["bound_files"] = []
            report["examples"] = [{"file": {"path": "missing.ttl"}}]
            with patch.object(validation, "git_value", return_value="test-head"):
                self.assertIn("Source example corpus membership changed", validation.validate_stored(report, root))

    def test_deleted_bindings_cannot_pass_vacuously(self):
        with patch.object(validation, "git_value", return_value="test-head"):
            errors = validation.validate_stored({"head": "test-head", "bound_files": [], "examples": []})
        self.assertIn("Required semantic evidence binding missing: imports/sosa.ttl", errors)
        self.assertIn("Required semantic evidence binding missing: config/current-semantic-expectations.json", errors)
        self.assertIn("Required semantic evidence binding missing: tools/java/CurrentSemanticReasoner.java", errors)
        self.assertIn("Pinned reasoner toolchain binding missing or incorrect", errors)
        self.assertIn("Raw semantic evidence manifest missing or empty", errors)

    def test_empty_or_mismatched_semantic_expectations_cannot_pass(self):
        manifest = {"expectations": []}
        errors = validation.validate_expectation_results({"expectations": {}}, manifest)
        self.assertIn("Approved positive and negative semantic expectations are both required", errors)
        item = {"id": "approved", "review_state": "approved", "approval_evidence": "synthetic test only",
                "expected_entailed": True, "evidence_role": "independent_semantic_expectation", "entailment_origin": "mapping_induced"}
        report = {"expectations": {"approved_count": 1, "proposed_count": 0, "proposed_positive_count": 0,
                                  "proposed_negative_count": 0, "proposed_ids": [], "approved_results": []}}
        errors = validation.validate_expectation_results(report, {"expectations": [item]})
        self.assertTrue(any("result IDs differ" in error for error in errors))


class StoredEvidenceAdversarialTests(unittest.TestCase):
    """Manually recorded execution facts, independent of the report builder."""

    ticketed = True

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.corpus = [validation.EXAMPLE_DIR / name for name in ("a.ttl", "b.ttl")]
        paths = {*validation.SOURCE_PATHS, *validation.TARGET_PATHS, validation.MAPPING_PATH,
                 validation.WORKBOOK_PATH, validation.MANIFEST_PATH, validation.FIXTURE_PATH,
                 validation.IDENTITY_PATH, validation.JAVA_SOURCE, validation.ROBOT_JAR, *self.corpus,
                 Path("tools/current_semantic_validation.py"), Path("tests/test_current_semantic_validation.py"),
                 *validation.CUSTODY_DEPENDENCIES,
                 Path("config/validation-toolchain.env")}
        if self.ticketed:
            paths.update((validation.INVOCATION_HELPER, validation.INVOCATION_TESTS))
        for path in paths:
            (self.root / path).parent.mkdir(parents=True, exist_ok=True)
            content = '<urn:fixture:' + path.name + '> a <http://www.w3.org/2002/07/owl#Class> .' if path.suffix == ".ttl" else "fixture input"
            (self.root / path).write_text(content)
        (self.root / validation.MANIFEST_PATH).write_text('{"expectations": []}')
        self.addCleanup(patch.stopall)
        patch.object(validation, "git_value", return_value="fixture-head").start()
        patch.object(validation, "ROBOT_SHA256", validation.sha256(self.root / validation.ROBOT_JAR)).start()
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.build = self.root / "build/execution-fixture"
        self.build.mkdir()
        compiler_stdout, compiler_stderr = self.evidence / "javac.stdout.log", self.evidence / "javac.stderr.log"
        compiler_stdout.write_text("")
        compiler_stderr.write_text("")
        compiler = {"command": [shutil.which("javac") or "javac", "-cp", str(self.root / validation.ROBOT_JAR),
                    "-d", str(self.build), str(self.root / validation.JAVA_SOURCE)],
                    "execution_status": "completed", "returncode": 0,
                    "stdout": validation.fingerprint(compiler_stdout, self.root),
                    "stderr": validation.fingerprint(compiler_stderr, self.root)}
        (self.evidence / "javac.command.json").write_text(json.dumps(compiler))
        hierarchy = {}
        for side, inputs in (("source", validation.SOURCE_PATHS), ("target", validation.TARGET_PATHS),
                             ("aligned", (*validation.SOURCE_PATHS, *validation.TARGET_PATHS, validation.MAPPING_PATH))):
            hierarchy[side] = self.record(side + "-hierarchy", "hierarchy", inputs, side=side, consistent=side == "target")
        examples = []
        for index, path in enumerate(self.corpus + [validation.FIXTURE_PATH]):
            role = "synthetic_fixture" if path == validation.FIXTURE_PATH else "source_example"
            runs = {}
            for phase in ("source", "aligned"):
                inputs = (*validation.SOURCE_PATHS, path) if phase == "source" else (*validation.SOURCE_PATHS, *validation.TARGET_PATHS, validation.MAPPING_PATH, path)
                runs[phase] = self.record(f"example-{index:02d}-{phase}", role, inputs,
                    phase="source-only" if phase == "source" else "aligned", corpus_id=str(path),
                    consistent=path != validation.FIXTURE_PATH)
            examples.append({"file": validation.fingerprint(path, self.root), **runs,
                             "classification": "technical/tool failure" if path == validation.FIXTURE_PATH else "aligned consistent"})
        self.report = {"head": "fixture-head", "executed_at_utc": "original execution time", "status": "FAIL",
            "toolchain": {"status": "ready", "jar": validation.fingerprint(validation.ROBOT_JAR, self.root),
                          "class_directory": str(self.build), "command": compiler},
            "bound_files": [validation.fingerprint(path, self.root) for path in sorted(paths - {validation.ROBOT_JAR})],
            "evidence_directory": "evidence", "examples": examples[:-1], "example_counts": {"aligned consistent": 2},
            "hierarchy_runs": hierarchy, "synthetic_fixture": examples[-1],
            "expectations": {"approved_count": 0, "proposed_count": 0, "proposed_positive_count": 0,
                             "proposed_negative_count": 0, "approved_independent_count": 0,
                             "approved_regression_count": 0, "proposed_independent_count": 0,
                             "proposed_regression_count": 0, "approved_results": [], "proposed_ids": []},
            "conservativity": {side: {"status": "BLOCKED", "additions_count": None, "losses_count": None,
                "additions": None, "losses": None, "affected_terms": None,
                "reason": "Both complete, consistent, OWL 2 DL reasoner results are required; unavailable is not zero."}
                for side in ("source", "target")}}
        self.refresh_evidence()
        (self.evidence / "summary.json").write_text(json.dumps(self.report))

    def refresh_evidence(self):
        if self.ticketed:
            # Build the fixture's initial selection after all its synthetic runs.
            # Mutation tests never use this helper to change custody artifacts.
            selected = {}
            for path in self.evidence.glob("*.result.json"):
                raw = json.loads(path.read_text())
                ticket = json.loads((self.root / raw["attempt"]["invocation"]["ticket"]["path"]).read_text())
                selected[ticket["slot"]] = ticket["invocation_id"]
            selection = self.evidence / "selected-invocations.json"
            selection.write_bytes(custody.canonical_bytes(custody.sealed({
                "schema": custody.SCHEMA, "selected_invocations": selected}, "selection_sha256")))
            self.report.update(execution_evidence_schema=2, selected_invocations=selected,
                               selection_record=validation.fingerprint(selection, self.root))
        self.report["evidence_files"] = [validation.fingerprint(path, self.root) for path in sorted(self.evidence.rglob("*"))
                                         if path.is_file() and path.name != "summary.json"]

    def record(self, identifier, role, inputs, *, side=None, phase=None, corpus_id=None, consistent=False, query=None):
        # These fixtures do not call the production plan, closure or run builders.
        graph = Graph()
        for path in inputs:
            graph.parse(self.root / path, format="turtle")
        closure = {"inputs": [validation.fingerprint(path, self.root) for path in inputs],
            "import_directives": [], "unresolved_imports": [], "removed_import_directive_count": 0,
            "removed_logical_axioms": 0, "triples": len(graph),
            "closure_policy": "All four current source modules for every example; CCO merged (including BFO) and integrated SSN2BFO product in aligned phase. Explicit local import expansion only; no remote resolution, no semantic cleanup."}
        mode = "hierarchy" if role == "hierarchy" else "consistency"
        identity = {"schema_version": 1, "id": identifier, "execution_role": role,
            "analysis_kind": "named_hierarchy" if role == "hierarchy" else "entailment" if query else "consistency",
            "comparison_side": side, "phase": phase, "corpus_id": corpus_id, "test_id": identifier,
            "query_id": query["id"] if query else None,
            "closure_identity": hashlib.sha256(json.dumps(closure, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "governed_inputs": closure["inputs"], "graph_identity": validation.graph_identity(graph),
            "queries": [query] if query else [], "command_identity": {"entrypoint": "CurrentSemanticReasoner",
                "mode": mode, "jvm_options": ["-Xmx4G"], "helper": validation.fingerprint(validation.JAVA_SOURCE, self.root),
                "jar": {"path": validation.ROBOT_JAR.as_posix(), "sha256": validation.ROBOT_SHA256}}}
        document = self.build / (identifier + ".rdf")
        graph.serialize(destination=document, format="xml")
        payload = {"status": "consistent" if consistent else "profile_failure", "owl2_dl_profile": consistent,
                   "profile_violations": [] if consistent else ["fixture violation"], "consistent": True}
        if consistent and mode == "hierarchy":
            payload.update(relations=[], signature={"classes": [str(s) for s in graph.subjects(RDF.type, OWL.Class)], "object_properties": []})
        if query:
            payload["expectations"] = [{"id": query["id"], "entailed": query["expected_entailed"], "passed": True}]
        stdout, stderr = self.evidence / (identifier + ".stdout.log"), self.evidence / (identifier + ".stderr.log")
        stdout.write_text(json.dumps(payload))
        stderr.write_text("")
        argv = [shutil.which("java") or "java", "-Xmx4G", "-cp", str(self.build) + ":" + str(self.root / validation.ROBOT_JAR),
                "CurrentSemanticReasoner", str(document), mode]
        raw = {"id": identifier, "status": "consistent" if consistent else "technical_failure", "closure": closure,
               "input_document": validation.fingerprint(document, self.root), "reasoner_result": payload,
               "execution_identity": identity, "execution_identity_origin": "recorded_before_execution"}
        if query:
            query_path = document.with_suffix(".queries.json")
            query_path.write_text(json.dumps([query]))
            raw["query_document"] = validation.fingerprint(query_path, self.root)
            argv.append(str(query_path))
        command = {"command": argv, "execution_status": "completed", "returncode": 0 if consistent else 2,
                   "stdout": validation.fingerprint(stdout, self.root), "stderr": validation.fingerprint(stderr, self.root)}
        if self.ticketed:
            slot = ("hierarchy/" + side if role == "hierarchy" else "expectations/" + query["id"] if query
                    else ("fixture" if role == "synthetic_fixture" else "examples/" + corpus_id)
                    + ("/source" if phase == "source-only" else "/aligned"))
            ticket = custody.create_ticket(root=self.root, evidence=self.evidence, slot=slot,
                identity=identity, closure=closure, graph_path=document,
                query_path=query_path if query else None, command=argv)
            with patch.object(custody.subprocess, "run", return_value=subprocess.CompletedProcess(
                    argv, command["returncode"], stdout.read_bytes(), stderr.read_bytes())):
                receipt = custody.execute_ticket(ticket, root=self.root)
            envelope, receipt_paths = receipt["envelope"], receipt["paths"]
            command.update(stdout=validation.fingerprint(receipt_paths["stdout"], self.root),
                           stderr=validation.fingerprint(receipt_paths["stderr"], self.root),
                           selected_invocation_id=envelope["invocation_id"], invocation_nonce=envelope["nonce"],
                           invocation={kind: validation.fingerprint(receipt_paths[kind], self.root)
                                       for kind in ("ticket", "capture", "envelope")})
            raw.update(selected_invocation_id=envelope["invocation_id"], invocation_nonce=envelope["nonce"])
        raw["attempt"] = command
        (self.evidence / (identifier + ".command.json")).write_text(json.dumps(command))
        (self.evidence / (identifier + ".result.json")).write_text(json.dumps(raw))
        summary = copy.deepcopy(raw)
        summary["reasoner_result"] = {"status": payload["status"], "owl2_dl_profile": consistent, "consistent": True,
            "profile_violation_count": 0 if consistent else 1, "profile_violation_examples": [] if consistent else ["fixture violation"],
            "relation_count": 0 if consistent and mode == "hierarchy" else None}
        if "signature" in payload:
            summary["reasoner_result"]["signature_counts"] = {key: len(value) for key, value in payload["signature"].items()}
        if query:
            summary["reasoner_result"]["expectations"] = payload["expectations"]
        return summary

    def errors(self):
        return validation.validate_stored(self.report, self.root)

    def test_honest_blocked_summary_with_matching_raw_evidence_passes(self):
        self.assertEqual(self.errors(), [])

    def test_summary_only_pass_attack_against_retained_profile_failure_rejected(self):
        self.report["status"] = "PASS"
        self.report["hierarchy_runs"]["source"]["status"] = "consistent"
        self.report["hierarchy_runs"]["source"]["reasoner_result"].update(status="consistent", profile_violation_count=0)
        errors = self.errors()
        self.assertTrue(any("execution summary contradicts" in error for error in errors), errors)
        self.assertTrue(any("gate contradicts" in error for error in errors), errors)

    def test_unknown_raw_differences_cannot_be_zero(self):
        for comparison in self.report["conservativity"].values():
            comparison.update(status="PASS", additions_count=0, losses_count=0, additions=[], losses=[])
        self.assertTrue(any("unavailable differences are not zero" in error for error in self.errors()))

    def test_example_aligned_consistent_cannot_override_raw_technical_failure(self):
        self.report["synthetic_fixture"]["classification"] = "aligned consistent"
        self.assertTrue(any("example classification contradicts" in error for error in self.errors()))

    def test_stored_raw_result_cannot_override_retained_stdout(self):
        path = self.evidence / "source-hierarchy.result.json"
        raw = json.loads(path.read_text())
        raw["status"] = "consistent"
        raw["reasoner_result"].update(status="consistent", owl2_dl_profile=True, profile_violations=[])
        path.write_text(json.dumps(raw))
        for index, item in enumerate(self.report["evidence_files"]):
            if item["path"] == "evidence/source-hierarchy.result.json":
                self.report["evidence_files"][index] = validation.fingerprint(path, self.root)
        errors = self.errors()
        self.assertTrue(any("retained reasoner stdout" in error for error in errors), errors)

    def test_missing_result_artifact_rejected(self):
        (self.evidence / "source-hierarchy.result.json").unlink()
        self.assertTrue(any("missing" in error for error in self.errors()))

    def test_historical_reconciliation_cannot_supply_current_slots(self):
        with self.assertRaisesRegex(ValueError, "cannot supply current evidence"):
            validation.reconcile_stored_report(self.report, self.root)
        self.report["reconciliation"] = {"publication_evidence_eligible": False}
        self.assertTrue(any("Historical reconciliation" in error for error in self.errors()))

    def test_changed_ontology_input_cannot_be_reconciled(self):
        (self.root / validation.SOURCE_PATHS[0]).write_text("changed ontology")
        with self.assertRaisesRegex(ValueError, "cannot supply current evidence"):
            validation.reconcile_stored_report(self.report, self.root)
        self.assertTrue(any("hash differs" in error for error in self.errors()))

    def test_missing_toolchain_can_be_recorded_but_cannot_be_successful_evidence(self):
        (self.root / validation.ROBOT_JAR).unlink()
        snapshot = validation.command_input_snapshot(self.root)
        jar = next(item for item in snapshot if item["path"] == str(validation.ROBOT_JAR))
        self.assertIsNone(jar["sha256"])
        self.assertTrue(any("input is missing" in error
                            for error in validation.validate_publication_execution_bindings(self.report, self.root)))

    def test_publication_command_binding_accepts_current_and_rejects_stale_or_missing(self):
        tool = self.root / "fixture-reasoner"
        tool.write_text("fixture executable identity")
        inputs = [item for item in self.report["bound_files"] if item["path"] != "tests/test_current_semantic_validation.py"]
        inputs.append(validation.fingerprint(validation.ROBOT_JAR, self.root))
        inputs.sort(key=lambda item: item["path"])
        command_files = [item for item in self.report["evidence_files"] if item["path"].endswith(".command.json")]
        for item in command_files:
            path = self.root / item["path"]
            command = json.loads(path.read_text())
            command.update(command=[str(tool)], returncode=0)
            command["execution_binding"] = {"expected_head": "fixture-head", "head_before": "fixture-head",
                "head_after": "fixture-head", "expected_inputs": inputs, "inputs_before": inputs,
                "inputs_after": inputs, "documents_before": [], "documents_after": [], "drift": False,
                "tool": {"path": str(tool), "sha256": validation.sha256(tool)}}
            path.write_text(json.dumps(command))
            item.update(validation.fingerprint(path, self.root))
        self.assertTrue(any("command" in error.lower() for error in
                            validation.validate_publication_execution_bindings(self.report, self.root)))
        selected = command_files[0]
        path = self.root / selected["path"]
        original = json.loads(path.read_text())
        for field, changed, message in (("head_before", "old-head", "HEAD binding"),
                                         ("inputs_before", [], "input binding"),
                                         ("drift", True, "drift"),
                                         ("execution_binding", None, "HEAD binding")):
            with self.subTest(field=field):
                command = copy.deepcopy(original)
                if field == "execution_binding":
                    command.pop(field)
                else:
                    command["execution_binding"][field] = changed
                path.write_text(json.dumps(command))
                selected.update(validation.fingerprint(path, self.root))
                self.assertTrue(any(message in error for error in validation.validate_publication_execution_bindings(self.report, self.root)))

    def mutate_raw(self, identifier, change):
        path = self.evidence / (identifier + ".result.json")
        raw = json.loads(path.read_text())
        change(raw)
        path.write_text(json.dumps(raw))
        self.refresh_evidence()

    def assert_slot_rejected(self):
        errors = self.errors()
        self.assertTrue(any("required execution slot" in error or "required slot" in error or "Invocation" in error or "invocation" in error for error in errors), errors)

    def test_source_summary_cannot_reference_target_execution(self):
        self.report["hierarchy_runs"]["source"] = copy.deepcopy(self.report["hierarchy_runs"]["target"])
        self.assert_slot_rejected()

    def test_target_summary_cannot_reference_source_execution(self):
        self.report["hierarchy_runs"]["target"] = copy.deepcopy(self.report["hierarchy_runs"]["source"])
        self.assert_slot_rejected()

    def test_example_cannot_reference_another_examples_valid_aligned_execution(self):
        self.report["examples"][0]["aligned"] = copy.deepcopy(self.report["examples"][1]["aligned"])
        self.assert_slot_rejected()

    def test_source_only_phase_cannot_reference_aligned_execution(self):
        self.report["examples"][0]["source"] = copy.deepcopy(self.report["examples"][0]["aligned"])
        self.assert_slot_rejected()

    def test_aligned_phase_cannot_reference_source_only_execution(self):
        self.report["examples"][0]["aligned"] = copy.deepcopy(self.report["examples"][0]["source"])
        self.assert_slot_rejected()

    def test_same_valid_raw_execution_cannot_fill_two_required_slots(self):
        first = self.report["examples"][0]["aligned"]
        self.report["examples"][1]["aligned"] = copy.deepcopy(first)
        self.assert_slot_rejected()

    def test_command_cannot_borrow_another_slots_valid_output(self):
        first = json.loads((self.evidence / "example-00-aligned.result.json").read_text())
        other = json.loads((self.evidence / "example-01-aligned.result.json").read_text())
        # Both payloads are successful and identical. Keep the first slot's
        # graph, role, ID and command, but borrow the second slot's stdout.
        self.assertEqual(first["reasoner_result"], other["reasoner_result"])
        first["attempt"]["stdout"] = other["attempt"]["stdout"]
        (self.evidence / "example-00-aligned.result.json").write_text(json.dumps(first))
        (self.evidence / "example-00-aligned.command.json").write_text(json.dumps(first["attempt"]))
        self.refresh_evidence()
        self.assert_slot_rejected()

    def test_correct_id_with_wrong_raw_role_is_rejected(self):
        self.mutate_raw("target-hierarchy", lambda raw: raw["execution_identity"].update(execution_role="source_example"))
        self.assert_slot_rejected()

    def test_correct_role_with_wrong_closure_or_input_identity_is_rejected(self):
        original = (self.evidence / "target-hierarchy.result.json").read_text()
        for field, value in (("closure_identity", "wrong-closure"), ("governed_inputs", []),
                             ("comparison_side", "source"), ("corpus_id", "another-corpus"),
                             ("test_id", "another-test"), ("query_id", "another-query")):
            with self.subTest(field=field):
                (self.evidence / "target-hierarchy.result.json").write_text(original)
                self.mutate_raw("target-hierarchy", lambda raw: raw["execution_identity"].update({field: value}))
                self.assert_slot_rejected()

    def test_correct_summary_values_cannot_conceal_other_underlying_slot(self):
        # Both example phases are successful, so all aggregate status values stay
        # correct. Relabeling a different execution still must fail.
        other = json.loads((self.evidence / "example-01-aligned.result.json").read_text())
        required = json.loads((self.evidence / "example-00-aligned.result.json").read_text())
        other.update(id=required["id"], execution_identity=required["execution_identity"])
        (self.evidence / "example-00-aligned.result.json").write_text(json.dumps(other))
        self.refresh_evidence()
        self.assertTrue(self.errors())

    def test_honest_source_failure_and_target_success_remain_bound(self):
        self.assertEqual(self.report["hierarchy_runs"]["source"]["status"], "technical_failure")
        self.assertEqual(self.report["hierarchy_runs"]["target"]["status"], "consistent")
        self.assertEqual(self.errors(), [])

    def test_two_distinct_valid_examples_in_correct_slots_pass(self):
        self.assertNotEqual(self.report["examples"][0]["aligned"]["id"], self.report["examples"][1]["aligned"]["id"])
        self.assertTrue(all(row["classification"] == "aligned consistent" for row in self.report["examples"]))
        self.assertEqual(self.errors(), [])

    def test_graph_change_cannot_hide_behind_updated_byte_fingerprint(self):
        document = self.build / "target-hierarchy.rdf"
        graph = Graph().parse(document, format="xml")
        graph.add((URIRef("urn:injected"), RDF.type, OWL.Class))
        graph.serialize(destination=document, format="xml")
        self.mutate_raw("target-hierarchy", lambda raw: raw.update(input_document=validation.fingerprint(document, self.root)))
        self.assertTrue(any("graph differs from required closure" in error for error in self.errors()))

    def test_command_cannot_use_another_mode_or_helper_directory(self):
        original = json.loads((self.evidence / "target-hierarchy.result.json").read_text())
        for index, value in ((6, "consistency"), (3, "/other/helper:" + str(self.root / validation.ROBOT_JAR))):
            with self.subTest(argument=index):
                changed = copy.deepcopy(original)
                changed["attempt"]["command"][index] = value
                (self.evidence / "target-hierarchy.result.json").write_text(json.dumps(changed))
                (self.evidence / "target-hierarchy.command.json").write_text(json.dumps(changed["attempt"]))
                self.refresh_evidence()
                self.assert_slot_rejected()

    def test_unrecorded_identity_requires_explicit_historical_reconciliation(self):
        self.mutate_raw("target-hierarchy", lambda raw: raw.pop("execution_identity"))
        self.assert_slot_rejected()

    def test_current_identity_is_never_reconstructed_from_mutable_legacy_metadata(self):
        for path in self.evidence.glob("*.result.json"):
            raw = json.loads(path.read_text())
            raw.pop("execution_identity")
            raw.pop("execution_identity_origin")
            path.write_text(json.dumps(raw))
        self.refresh_evidence()
        self.assert_slot_rejected()
        with self.assertRaisesRegex(ValueError, "cannot supply current evidence"):
            validation.reconcile_stored_report(self.report, self.root)

    def test_approved_query_cannot_execute_another_test(self):
        item = {"id": "manual-positive", "review_state": "approved", "approval_evidence": "test fixture only",
                "expected_entailed": True, "evidence_role": "independent_semantic_expectation", "entailment_origin": "mapping_induced",
                "query": {"kind": "class_subsumption", "subject": "urn:fixture:sosa.ttl", "object": "urn:fixture:sosa.ttl"}}
        manifest_path = self.root / validation.MANIFEST_PATH
        manifest_path.write_text(json.dumps({"expectations": [item]}))
        for index, binding in enumerate(self.report["bound_files"]):
            if binding["path"] == str(validation.MANIFEST_PATH):
                self.report["bound_files"][index] = validation.fingerprint(validation.MANIFEST_PATH, self.root)
        query = dict(item["query"], id=item["id"], expected_entailed=True)
        run = self.record("expectation-manual-positive", "semantic_expectation",
            (*validation.SOURCE_PATHS, *validation.TARGET_PATHS, validation.MAPPING_PATH),
            phase="aligned", corpus_id="approved-semantic-expectations", consistent=True, query=query)
        self.report["expectations"].update(approved_count=1, approved_independent_count=1, approved_results=[run])
        self.refresh_evidence()
        self.assertEqual(self.errors(), [])
        document = self.build / "expectation-manual-positive.queries.json"
        document.write_text(json.dumps([dict(query, id="another-test")]))
        self.mutate_raw("expectation-manual-positive", lambda raw: raw.update(query_document=validation.fingerprint(document, self.root)))
        self.assert_slot_rejected()


class ExpectationAttributionTests(unittest.TestCase):
    def test_restatements_are_mapping_induced_and_excluded_from_independent_count(self):
        manifest = json.loads((ROOT / validation.MANIFEST_PATH).read_text())
        approved, proposed = validation.selected_expectations(manifest)
        regressions = [item for item in proposed if item["evidence_role"] == "mapping_axiom_regression"]
        self.assertEqual({item["id"] for item in regressions}, {"equivalence-reverse-positive", "typing-sensor-positive"})
        self.assertTrue(all(item["entailment_origin"] == "mapping_induced" for item in regressions))
        self.assertEqual(validation.expectation_counts(approved, proposed)["proposed_independent_count"], 14)
        self.assertEqual(validation.expectation_counts(approved, proposed)["approved_independent_count"], 0)
        sensor = next(item for item in regressions if item["id"] == "typing-sensor-positive")
        self.assertIn("advisory schema:domainIncludes", sensor["motivation"])

    def test_approved_axiom_restatements_do_not_satisfy_independent_positive_negative_gate(self):
        items = [{"id": label, "expected_entailed": polarity, "review_state": "approved",
                  "approval_evidence": "synthetic fixture", "evidence_role": "mapping_axiom_regression",
                  "entailment_origin": "mapping_induced"} for label, polarity in (("positive", True), ("negative", False))]
        report = {"expectations": {"approved_count": 2, "proposed_count": 0,
                  "proposed_positive_count": 0, "proposed_negative_count": 0,
                  "approved_independent_count": 0, "approved_regression_count": 2,
                  "proposed_independent_count": 0, "proposed_regression_count": 0, "proposed_ids": [],
                  "approved_results": [{"status": "consistent", "reasoner_result": {"expectations": [
                      {"id": item["id"], "entailed": item["expected_entailed"], "passed": True}]}} for item in items]}}
        self.assertEqual(validation.validate_expectation_results(report, {"expectations": items}),
                         ["Approved positive and negative semantic expectations are both required"])


@unittest.skipUnless(shutil.which("java") and shutil.which("javac") and (ROOT / validation.ROBOT_JAR).exists(),
                     "Complete-reasoner synthetic regression needs local Java/Javac and pinned ROBOT jar")
class HermitIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="current-semantic-tests-")
        cls.base = Path(cls.temporary.name)
        cls.evidence = cls.base / "evidence"
        cls.evidence.mkdir()
        cls.build = cls.base / "build"
        cls.toolchain = validation.build_helper(cls.evidence, cls.build)
        if cls.toolchain["status"] != "ready": raise AssertionError("Pinned Java helper failed to build")
        S, T = Namespace("urn:source:"), Namespace("urn:target:")
        cls.S, cls.T = S, T
        source, target, combined = Graph(), Graph(), Graph()
        for c in (S.A, S.B, S.C, S.D, S.E, S.F): source.add((c, RDF.type, OWL.Class))
        for p in (S.p, S.q, S.r, S.s, S.u, S.v): source.add((p, RDF.type, OWL.ObjectProperty))
        source.add((S.C, RDFS.subClassOf, S.D))
        source.add((S.r, RDFS.subPropertyOf, S.s))
        for c in (T.A, T.B, T.C, T.D, T.E): target.add((c, RDF.type, OWL.Class))
        for p in (T.p, T.q, T.r, T.s, T.u): target.add((p, RDF.type, OWL.ObjectProperty))
        target.add((T.A, RDFS.subClassOf, T.B))
        target.add((T.p, RDFS.subPropertyOf, T.q))
        combined += source
        combined += target
        for left, right in ((S.A,T.A),(S.B,T.B),(S.C,T.C),(S.D,T.D),(S.E,T.E),(S.F,T.E)):
            combined.add((left, OWL.equivalentClass, right))
        for left, right in ((S.p,T.p),(S.q,T.q),(S.r,T.r),(S.s,T.s),(S.u,T.u),(S.v,T.u)):
            combined.add((left, OWL.equivalentProperty, right))
        queries = [
            {"id": "positive", "kind": "class_subsumption", "subject": str(S.C), "object": str(S.D), "expected_entailed": True},
            {"id": "negative", "kind": "class_subsumption", "subject": str(S.A), "object": str(S.B), "expected_entailed": False},
        ]
        cls.source_graph = source
        cls.source = cls.run_reasoner(source, "source", queries=queries)
        cls.target = cls.run_reasoner(target, "target")
        cls.combined = cls.run_reasoner(combined, "aligned")

    @classmethod
    def tearDownClass(cls): cls.temporary.cleanup()

    @classmethod
    def run_reasoner(cls, graph, name, closure=None, queries=None):
        return validation.run_graph(graph, closure or {"unresolved_imports": []}, name,
            cls.evidence, cls.build, cls.toolchain, hierarchy=True, queries=queries, timeout=30)

    def test_real_hermit_detects_source_class_property_and_equivalence_violation(self):
        self.assertEqual(self.source["status"], "consistent", self.source)
        self.assertEqual(self.combined["status"], "consistent", self.combined)
        result = validation.approximate_difference(self.source, self.combined)
        additions = {(r["kind"],r["subject"],r["object"]) for r in result["additions"]}
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(("class_subsumption", str(self.S.A),str(self.S.B)), additions)
        self.assertIn(("object_property_subsumption",str(self.S.p),str(self.S.q)), additions)
        self.assertIn(("class_equivalence",str(self.S.E),str(self.S.F)), additions)
        self.assertIn(("object_property_equivalence",str(self.S.u),str(self.S.v)), additions)
        self.assertEqual(result["losses_count"],0)
        self.assertTrue(all(r["deliberate_mapping_commitment"] == "human_review_required" for r in result["additions"]))

    def test_real_hermit_detects_target_signature_violation(self):
        result = validation.approximate_difference(self.target, self.combined)
        additions = {(r["kind"],r["subject"],r["object"]) for r in result["additions"]}
        self.assertIn(("class_subsumption",str(self.T.C),str(self.T.D)), additions)
        self.assertIn(("object_property_subsumption",str(self.T.r),str(self.T.s)), additions)
        self.assertEqual(result["status"], "FAIL")

    def test_actual_positive_and_negative_query_support(self):
        self.assertEqual(self.source["reasoner_result"]["expectations"], [
            {"id": "positive", "entailed": True, "passed": True},
            {"id": "negative", "entailed": False, "passed": True}])

    def test_unchanged_hierarchy_passes_and_loss_detects_corrupted_materialization(self):
        self.assertEqual(validation.approximate_difference(self.source,self.source)["status"],"PASS")
        corrupted = copy.deepcopy(self.source)
        corrupted["reasoner_result"]["relations"] = []
        result = validation.approximate_difference(self.source,corrupted)
        self.assertEqual(result["status"],"FAIL")
        self.assertGreater(result["losses_count"],0)

    def test_incomplete_import_even_consistent_reasoner_fails_closed(self):
        result = self.run_reasoner(self.source_graph, "incomplete", {"unresolved_imports": [{"import": "urn:missing"}]})
        self.assertEqual(result["reasoner_result"]["status"], "consistent")
        self.assertEqual(result["status"],"technical_failure")

    def test_out_of_profile_fails_closed(self):
        graph = Graph()
        graph.add((self.S.p,RDF.type,OWL.ObjectProperty))
        graph.add((self.S.p,RDF.type,OWL.TransitiveProperty))
        graph.add((self.S.p,RDF.type,OWL.FunctionalProperty))
        result = self.run_reasoner(graph,"profile-failure")
        self.assertFalse(result["reasoner_result"]["owl2_dl_profile"])
        self.assertEqual(result["status"],"technical_failure")
        self.assertNotIn("relations",result["reasoner_result"])

    def test_inconsistent_graph_has_no_explosive_entailment_evidence(self):
        graph = Graph()
        graph.add((self.S.A,RDF.type,OWL.Class))
        graph.add((self.S.B,RDF.type,OWL.Class))
        graph.add((self.S.A,OWL.disjointWith,self.S.B))
        graph.add((URIRef("urn:test:individual"),RDF.type,self.S.A))
        graph.add((URIRef("urn:test:individual"),RDF.type,self.S.B))
        result = self.run_reasoner(graph,"inconsistent")
        self.assertEqual(result["status"],"inconsistent",result)
        self.assertNotIn("relations",result["reasoner_result"])


if __name__ == "__main__": unittest.main()
