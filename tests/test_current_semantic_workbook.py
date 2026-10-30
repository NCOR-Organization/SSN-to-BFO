"""Disposable real-workbook tests for exact project-local semantic custody."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from uuid import uuid4

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_documentary_workbook as documentary
import current_semantic_workbook as semantic
import current_assessment as assessment

HISTORICAL_START_SHA = "9e526e5705fc84571e03616f74c59fe8654fcc073a1c45a281109cf22c276e14"


class SemanticWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="semantic-workbook-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        paths = set(documentary.evidence_paths(ROOT)) | {
            semantic.WORKBOOK, "config/publication-metadata.toml", "config/product-role-policy.toml",
            *semantic.SOURCE_TARGET_PATHS, *semantic.GOVERNED_INPUT_SHA256}
        for relative in paths:
            if relative.startswith(semantic.TRANSITIONS + "/"):
                continue
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.live = self.root / semantic.WORKBOOK
        # Exercise new transitions from the fixed pre-semantic checkpoint,
        # independently of later real decisions in the production workbook.
        shutil.copyfile(ROOT / documentary.VERSIONS / (HISTORICAL_START_SHA + ".xlsx"), self.live)
        self.original = self.live.read_bytes()
        self.ref = {"path": "reports/current-human-decisions/2026-10-25-sample-pair/approved-instructions.txt",
                    "sha256": documentary.digest((self.root / "reports/current-human-decisions/2026-10-25-sample-pair/approved-instructions.txt").read_bytes()),
                    "reference": "Disposable fixture authority; no production semantic approval"}

    def candidate(self, edits=(), source=None, append=None, delete=None):
        output = self.root / (str(uuid4()) + ".xlsx")
        workbook = load_workbook(source or self.live)
        for sheet, cell, value in edits:
            workbook[sheet][cell] = value
        if append:
            workbook[append[0]].append(append[1])
        if delete:
            workbook[delete[0]].delete_rows(delete[1])
        workbook.save(output)
        workbook.close()
        return output

    def cleared(self, row=49, source=None):
        return self.candidate([("Sheet2", f"B{row}", None), ("Sheet2", f"C{row}", None)], source)

    def authorities(self, old, new):
        return {r["row_id"]: {"authorization_type": "RESTORE_PREVIOUSLY_APPROVED_DECISION",
                              "rationale": "Disposable exact-delta fixture",
                              "evidence": [self.ref]}
                for r in semantic.workbook_delta(old, new)["changed_rows"]}

    def record(self, candidate, old=None, **kwargs):
        old = old or self.live
        return semantic.create_transition(self.root, old, candidate, self.authorities(old, candidate),
                                          editor_identity="Fixture editor", **kwargs)

    def install(self, candidate):
        shutil.copyfile(candidate, self.live)

    def inheritance_authorities(self, candidate):
        """Build disposable evidence for candidate-input guard tests only."""
        resolver = assessment.mapping.Resolver(root=self.root)
        raw, stats = assessment.mapping.read_workbook(candidate)
        rows = assessment.mapping.validate_and_process_rows(raw, resolver, stats)
        scope = json.loads((self.root / "config/current-ssn-sosa-scope.json").read_text())
        terms = assessment.inventory(resolver.source_graph, scope)
        routes = {r["source_iri"]: r for r in assessment.coverage(terms, resolver.source_graph, rows)}
        placeholder = self.root / "fixture-predecision.json"
        placeholder.write_text('{"scope":"Disposable authority-guard fixture, not a human approval."}\n')
        snapshot = {"path": placeholder.name, "sha256": assessment.sha(placeholder)}
        authorities = self.authorities(self.live, candidate)
        for entry in semantic.workbook_delta(self.live, candidate)["changed_rows"]:
            prefix, local = entry["new"]["subject"].split(":", 1)
            iri = assessment.mapping.PREFIXES[prefix] + local
            own = [row for row in rows if str(row.subject) == iri]
            route = routes[iri]
            evidence = {
                "source_iri": iri, "assessment_outcome": "inheritance_sufficient",
                "no_additional_direct_mapping_required": True,
                "rationale": "Fixture explicitly approves this exact inherited route without a direct mapping.",
                "input_sha256": assessment.sufficiency_inputs(root=self.root, workbook_path=candidate),
                "inherited_routes_sha256": assessment.canonical_sha(route["inherited_routes"]),
            }
            evidence_path = self.root / (local + "-sufficiency.json")
            evidence_path.write_text(assessment.json_text(evidence))
            decision = {
                "schema_version": 1, "decision_id": "urn:uuid:" + str(uuid4()),
                "source_iri": iri, "review_state": "final",
                "assessment_outcome": "inheritance_sufficient",
                "reviewer_identity": "Disposable test reviewer",
                "review_timestamp": "2099-01-01T00:00:00+00:00",
                "question_response": "Fixture approval of inherited treatment for the candidate.",
                "review_packet_snapshot": snapshot, "assessment_snapshot": snapshot,
                "mapping_row_ids": sorted(row.row.stable_row_id for row in own),
                "formal_mapping_assertions": assessment.decision_mapping_assertions(own),
                "formal_coverage_sha256": assessment.canonical_sha(route),
                "decision_basis": "inheritance_sufficiency",
                "no_additional_direct_mapping_required": True,
                "inheritance_sufficiency_evidence": {"path": evidence_path.name,
                                                    "sha256": assessment.sha(evidence_path)},
                "input_hashes": {
                    "workbook_sha256": assessment.sha(candidate),
                    "source_files_sha256": {p: semantic.SOURCE_TARGET_SHA256[p]
                                            for p in semantic.SOURCE_TARGET_PATHS if p != "imports/cco.ttl"},
                    "target_sha256": semantic.SOURCE_TARGET_SHA256["imports/cco.ttl"],
                },
            }
            decision_path = self.root / (local + "-decision.json")
            decision_path.write_text(assessment.json_text(decision))
            authorities[entry["row_id"]].update({
                "authorization_type": "EXPLICIT_NEW_HUMAN_DECISION",
                "human_decision": {"path": decision_path.name, "sha256": assessment.sha(decision_path)},
            })
        return authorities

    def test_creation_keeps_live_and_historical_bytes_unchanged(self):
        candidate = self.cleared()
        record = self.record(candidate)
        self.assertEqual(self.live.read_bytes(), self.original)
        document = json.loads(record.read_text())
        self.assertEqual(document["delta"], semantic.workbook_delta(self.live, candidate))
        self.assertNotEqual(document["old_semantic_projection_sha256"], document["new_semantic_projection_sha256"])
        self.assertEqual(len(document["delta"]["cleared_mapping_rows"]), 1)
        self.install(candidate)
        history = semantic.resolve_history(self.root)
        self.assertEqual([r["kind"] for r in history["chain"]], ["documentary", "semantic"])
        historical = history["baseline"]["historical_workbook"]
        self.assertEqual(documentary.digest(semantic.validate_workbook_evolution(self.root, historical["sha256"]).read_bytes()), historical["sha256"])

    def test_unauthorized_semantic_edit_and_documentary_impersonation_fail(self):
        candidate = self.cleared()
        with self.assertRaisesRegex(ValueError, "projection"):
            documentary.create_update(self.root, self.live, candidate, {}, editor_identity="Fixture")
        self.install(candidate)
        with self.assertRaisesRegex(ValueError, "complete"):
            semantic.resolve_history(self.root)

    def test_documentary_only_edit_cannot_be_semantic(self):
        candidate = self.candidate([("Sheet2", "D49", "Updated documentary text")])
        with self.assertRaisesRegex(ValueError, "requires a semantic change"):
            self.record(candidate)
        self.assertFalse((self.root / semantic.TRANSITIONS).exists())

    def test_exact_manifest_rejects_omitted_cells_and_forged_states(self):
        candidate = self.cleared()
        path = self.record(candidate)
        original = json.loads(path.read_text())
        self.install(candidate)
        for mutation in ("omit", "old_target", "new_predicate", "projection", "count", "axiom_delta", "coverage"):
            with self.subTest(mutation=mutation):
                document = copy.deepcopy(original)
                if mutation == "omit": document["delta"]["changed_rows"][0]["changed_cells"].pop()
                elif mutation == "old_target": document["delta"]["changed_rows"][0]["old"]["target"] = "cco:has_agent"
                elif mutation == "new_predicate": document["delta"]["changed_rows"][0]["new"]["predicate"] = "owl:equivalentProperty"
                elif mutation == "projection": document["new_semantic_projection_sha256"] = "0" * 64
                elif mutation == "count": document["generation_expectations"]["after"]["counts"]["GOVERNED_ROW_COUNT"] += 1
                elif mutation == "axiom_delta": document["generation_expectations"]["logical_axiom_delta"]["removed"] = []
                else: document["generation_expectations"]["coverage_delta"]["direct_formal_mapping"] += 1
                path.write_bytes(documentary.canonical_bytes(document))
                with self.assertRaises(ValueError): semantic.resolve_history(self.root)
        path.write_bytes(documentary.canonical_bytes(original))

    def test_added_and_removed_rows_keep_exact_stable_identity(self):
        row_id = "urn:uuid:" + str(uuid4())
        added = self.candidate(append=("Sheet2", ["sosa:madeBySensor", "rdfs:subPropertyOf", "cco:has_agent", "Retained sensor mapping", row_id]))
        path = self.record(added)
        document = json.loads(path.read_text())
        self.assertEqual(document["delta"]["added_rows"][0]["row_id"], row_id)
        self.assertEqual(document["generation_expectations"]["count_delta"]["GOVERNED_ROW_COUNT"], 1)
        removed = self.candidate(source=added, delete=("Sheet2", 63))
        path2 = self.record(removed, old=added)
        second = json.loads(path2.read_text())
        self.assertEqual(second["delta"]["removed_mapping_assertions"][0]["row_id"], row_id)
        self.install(removed)
        self.assertEqual(len(semantic.resolve_history(self.root)["chain"]), 3)

    def test_duplicate_missing_and_invalid_row_ids_fail(self):
        baseline_id = semantic.workbook_rows(self.live)
        first = next(iter(baseline_id))
        for invalid in (None, "bad", first):
            with self.subTest(value=invalid):
                candidate = self.candidate([("Sheet2", "E49", invalid)])
                with self.assertRaises(ValueError): semantic.workbook_delta(self.live, candidate)

    def test_authority_is_exact_and_new_decision_cannot_be_invented(self):
        candidate = self.cleared()
        authorities = self.authorities(self.live, candidate)
        for invalid in ({}, {**authorities, "extra": {}}, {next(iter(authorities)): {
                **next(iter(authorities.values())), "authorization_type": "EXPLICIT_NEW_HUMAN_DECISION"}}):
            with self.subTest(authorities=invalid):
                with self.assertRaises(ValueError):
                    semantic.create_transition(self.root, self.live, candidate, invalid, editor_identity="Fixture")

    def test_explicit_inheritance_approvals_bind_exact_candidate_routes(self):
        candidate = self.candidate([(sheet, f"{column}{row}", None)
                                    for sheet, row in (("Sheet1", 43), ("Sheet1", 45))
                                    for column in "BC"])
        authorities = self.inheritance_authorities(candidate)
        record = semantic.create_transition(self.root, self.live, candidate, authorities,
                                            editor_identity="Disposable test reviewer")
        self.assertEqual(self.live.read_bytes(), self.original)
        self.assertEqual(len(json.loads(record.read_text())["delta"]["cleared_mapping_rows"]), 2)
        self.install(candidate)
        self.assertEqual(semantic.resolve_history(self.root)["tail_sha256"], assessment.sha(candidate))

    def test_inheritance_evidence_cannot_be_forged_or_rebound(self):
        candidate = self.candidate([("Sheet1", "B45", None), ("Sheet1", "C45", None)])
        for mutation in ("term", "rationale", "approval", "workbook", "routes", "coverage", "basis"):
            with self.subTest(mutation=mutation):
                authorities = self.inheritance_authorities(candidate)
                authority = next(iter(authorities.values()))
                decision_path = self.root / authority["human_decision"]["path"]
                decision = json.loads(decision_path.read_text())
                evidence_path = self.root / decision["inheritance_sufficiency_evidence"]["path"]
                evidence = json.loads(evidence_path.read_text())
                if mutation == "term": evidence["source_iri"] = str(assessment.mapping.SOSA.Sensor)
                elif mutation == "rationale": evidence["rationale"] = "inherited"
                elif mutation == "approval": evidence["no_additional_direct_mapping_required"] = False
                elif mutation == "workbook": evidence["input_sha256"][semantic.WORKBOOK] = assessment.sha(self.live)
                elif mutation == "routes": evidence["inherited_routes_sha256"] = "0" * 64
                elif mutation == "coverage": decision["formal_coverage_sha256"] = "0" * 64
                else: decision["decision_basis"] = "semantic_rejection"
                evidence_path.write_text(assessment.json_text(evidence))
                decision["inheritance_sufficiency_evidence"]["sha256"] = assessment.sha(evidence_path)
                decision_path.write_text(assessment.json_text(decision))
                authority["human_decision"]["sha256"] = assessment.sha(decision_path)
                with self.assertRaises(ValueError):
                    semantic._authority(self.root, authorities, semantic.workbook_delta(self.live, candidate), candidate)

    def test_inheritance_requires_route_and_cannot_approve_direct_mapping(self):
        absent_route = self.cleared()
        direct = self.candidate([("Sheet1", "C45", "bfo:SpecificallyDependentContinuant")])
        for candidate in (absent_route, direct):
            with self.subTest(candidate=candidate.name):
                authorities = self.inheritance_authorities(candidate)
                with self.assertRaises(ValueError):
                    semantic._authority(self.root, authorities, semantic.workbook_delta(self.live, candidate), candidate)

    def test_removal_authority_cannot_add_mapping(self):
        candidate = self.candidate(append=("Sheet2", ["sosa:madeBySensor", "rdfs:subPropertyOf", "cco:has_agent", "Fixture", "urn:uuid:" + str(uuid4())]))
        authorities = self.authorities(self.live, candidate)
        next(iter(authorities.values()))["authorization_type"] = "REMOVE_PREVIOUSLY_REJECTED_MAPPING"
        with self.assertRaisesRegex(ValueError, "cannot introduce"):
            semantic.create_transition(self.root, self.live, candidate, authorities, editor_identity="Fixture")

    def test_multiple_semantic_and_documentary_transitions(self):
        first = self.cleared()
        self.record(first)
        second = self.candidate([("Sheet1", "B45", None), ("Sheet1", "C45", None)], source=first)
        self.record(second, old=first)
        third = self.candidate([("Sheet2", "D49", "Reasoning after semantic restoration")], source=second)
        documentary.create_update(self.root, second, third, {"Sheet2!D49": [self.ref]}, editor_identity="Fixture")
        self.install(third)
        self.assertEqual([r["kind"] for r in semantic.resolve_history(self.root)["chain"]], ["documentary", "semantic", "semantic", "documentary"])
        self.assertIn(semantic.TRANSITIONS, " ".join(documentary.evidence_paths(self.root)))

    def test_branching_and_missing_transitions_fail(self):
        first = self.cleared()
        path = self.record(first)
        second = self.candidate([("Sheet1", "B45", None), ("Sheet1", "C45", None)], source=first)
        self.record(second, old=first)
        self.install(second)
        original = path.read_bytes()
        document = json.loads(original)
        document["transition_id"] = str(uuid4())
        duplicate = path.parent / (document["transition_id"] + ".json")
        duplicate.write_bytes(documentary.canonical_bytes(document))
        with self.assertRaisesRegex(ValueError, "branching"): semantic.resolve_history(self.root)
        duplicate.unlink()
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing|disconnected"): semantic.resolve_history(self.root)
        path.write_bytes(original)

    def test_later_transition_binds_exact_predecessor_record_bytes(self):
        first = self.cleared()
        path = self.record(first)
        second = self.candidate([("Sheet1", "B45", None), ("Sheet1", "C45", None)], source=first)
        self.record(second, old=first)
        self.install(second)
        semantic.resolve_history(self.root)
        original = path.read_bytes()
        document = json.loads(original)
        document["editor_identity"] = "Rewritten editor"
        next(iter(document["authorities"].values()))["rationale"] = "Rewritten historical rationale"
        path.write_bytes(documentary.canonical_bytes(document))
        with self.assertRaisesRegex(ValueError, "predecessor record bytes"):
            semantic.resolve_history(self.root)
        path.write_bytes(original)
        semantic.resolve_history(self.root)

    def test_cycle_attempt_and_stale_old_version_fail(self):
        first = self.cleared()
        self.record(first)
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.record(self.live, old=first)
        another = self.candidate([("Sheet1", "B45", None), ("Sheet1", "C45", None)])
        with self.assertRaisesRegex(ValueError, "tail"):
            self.record(another)

    def test_source_target_rule_and_evidence_tampering_fail(self):
        candidate = self.cleared()
        record = self.record(candidate)
        self.install(candidate)
        for relative in ("imports/cco.ttl", "imports/ssn.ttl", "rules/ssn-hasproperty-conditional-mapping.rq", self.ref["path"]):
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\n# changed\n")
                with self.assertRaises(ValueError): semantic.resolve_history(self.root)
                path.write_bytes(original)
        self.assertTrue(record.exists())

    def test_snapshot_tampering_fails_even_with_unchanged_live(self):
        candidate = self.cleared()
        path = self.record(candidate)
        document = json.loads(path.read_text())
        archived = semantic.snapshot(self.root, document["new_workbook_sha256"])
        archived.write_bytes(archived.read_bytes() + b"tamper")
        with self.assertRaisesRegex(ValueError, "hash mismatch"): semantic.resolve_history(self.root, require_live=False)


if __name__ == "__main__":
    unittest.main()
