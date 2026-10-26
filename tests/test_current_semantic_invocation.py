#!/usr/bin/env python3
"""Adversarial custody tests for current-track reasoner execution evidence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_semantic_invocation as custody
import current_semantic_validation as validation
from tests import test_current_semantic_validation as semantic_tests


class InvocationCustodyTests(unittest.TestCase):
    """Build retained slots independently, then let the actual wrapper capture outputs."""

    def setUp(self):
        self.fixture = semantic_tests.StoredEvidenceAdversarialTests("test_honest_blocked_summary_with_matching_raw_evidence_passes")
        # This builder deliberately starts with raw records, then creates all
        # current tickets/captures below before asking either current validator.
        self.fixture.ticketed = False
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root, self.evidence = self.fixture.root, self.fixture.evidence
        wrapper_copy = self.root / validation.INVOCATION_HELPER
        wrapper_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(custody.__file__, wrapper_copy)
        self.fixture.report["bound_files"].append(validation.fingerprint(wrapper_copy, self.root))
        test_copy = self.root / validation.INVOCATION_TESTS
        test_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(__file__, test_copy)
        self.fixture.report["bound_files"].append(validation.fingerprint(test_copy, self.root))
        self.fixture.report["bound_files"].sort(key=lambda item: item["path"])
        self.report = self.fixture.report
        approved = []
        for name, expected in (("query-a", True), ("query-b", False)):
            approved.append({"id": name, "review_state": "approved", "approval_evidence": "synthetic test only",
                "expected_entailed": expected, "evidence_role": "independent_semantic_expectation",
                "entailment_origin": "mapping_induced", "query": {"kind": "class_subsumption",
                    "subject": "urn:fixture:sosa.ttl", "object": "urn:fixture:" + name}})
        manifest_path = self.root / validation.MANIFEST_PATH
        manifest_path.write_text(json.dumps({"expectations": approved}))
        self.report["bound_files"] = [validation.fingerprint(manifest_path, self.root) if item["path"] ==
            validation.MANIFEST_PATH.as_posix() else item for item in self.report["bound_files"]]
        results = []
        for item in approved:
            query = dict(item["query"], id=item["id"], expected_entailed=item["expected_entailed"])
            results.append(self.fixture.record("expectation-" + item["id"], "semantic_expectation",
                (*validation.SOURCE_PATHS, *validation.TARGET_PATHS, validation.MAPPING_PATH),
                phase="aligned", corpus_id="approved-semantic-expectations", consistent=True, query=query))
        self.report["expectations"].update(validation.expectation_counts(approved, []))
        self.report["expectations"]["approved_results"] = results
        self.selected = {}
        self._upgrade_all()
        self.assertEqual(validation.validate_stored(self.report, self.root), [])

    def _slot(self, raw):
        identity = raw["execution_identity"]
        if identity["execution_role"] == "hierarchy":
            return "hierarchy/" + identity["comparison_side"]
        if identity["execution_role"] == "semantic_expectation":
            return "expectations/" + identity["query_id"]
        prefix = "fixture" if identity["execution_role"] == "synthetic_fixture" else "examples/" + identity["corpus_id"]
        return prefix + ("/source" if identity["phase"] == "source-only" else "/aligned")

    def _refresh(self):
        self.report["evidence_files"] = [validation.fingerprint(path, self.root)
            for path in sorted(self.evidence.rglob("*")) if path.is_file() and path.name != "summary.json"]

    def _summary(self, raw):
        identifier = raw["id"]
        compact = validation.compact_result(raw)
        for side in ("source", "target", "aligned"):
            if self.report["hierarchy_runs"][side]["id"] == identifier:
                self.report["hierarchy_runs"][side] = compact
                return
        for row in self.report["examples"] + [self.report["synthetic_fixture"]]:
            for phase in ("source", "aligned"):
                if row[phase]["id"] == identifier:
                    row[phase] = compact
                    return
        for index, row in enumerate(self.report["expectations"]["approved_results"]):
            if row["id"] == identifier:
                self.report["expectations"]["approved_results"][index] = compact
                return
        raise AssertionError(identifier)

    def _upgrade_all(self):
        for path in sorted(self.evidence.glob("*.result.json")):
            raw = json.loads(path.read_text())
            old_command = raw["attempt"]
            old_stdout = (self.root / old_command["stdout"]["path"]).read_bytes()
            payload = json.loads(old_stdout)
            payload["execution_marker"] = raw["id"]
            stdout = custody.canonical_bytes(payload)
            stderr = (self.root / old_command["stderr"]["path"]).read_bytes()
            graph = self.root / raw["input_document"]["path"]
            query = self.root / raw["query_document"]["path"] if raw.get("query_document") else None
            slot = self._slot(raw)
            ticket_path = custody.create_ticket(root=self.root, evidence=self.evidence,
                slot=slot, identity=raw["execution_identity"], closure=raw["closure"],
                graph_path=graph, query_path=query, command=old_command["command"])
            process = subprocess.CompletedProcess(old_command["command"], old_command["returncode"], stdout, stderr)
            with patch.object(custody.subprocess, "run", return_value=process):
                receipt = custody.execute_ticket(ticket_path, root=self.root)
            envelope, paths = receipt["envelope"], receipt["paths"]
            attempt = dict(old_command,
                stdout=validation.fingerprint(paths["stdout"], self.root),
                stderr=validation.fingerprint(paths["stderr"], self.root),
                selected_invocation_id=envelope["invocation_id"], invocation_nonce=envelope["nonce"],
                invocation={kind: validation.fingerprint(paths[kind], self.root)
                            for kind in ("ticket", "capture", "envelope")})
            raw.update(attempt=attempt, selected_invocation_id=envelope["invocation_id"],
                       invocation_nonce=envelope["nonce"], reasoner_result=payload)
            path.write_text(json.dumps(raw))
            (self.evidence / (raw["id"] + ".command.json")).write_text(json.dumps(attempt))
            self._summary(raw)
            self.selected[slot] = envelope["invocation_id"]
        selection_path = self.evidence / "selected-invocations.json"
        custody.create_once(selection_path, custody.canonical_bytes(custody.sealed({
            "schema": custody.SCHEMA, "selected_invocations": self.selected}, "selection_sha256")))
        self.report.update(execution_evidence_schema=2, selected_invocations=copy.deepcopy(self.selected),
                           selection_record=validation.fingerprint(selection_path, self.root))
        self._refresh()

    def _raw(self, identifier):
        return json.loads((self.evidence / (identifier + ".result.json")).read_text())

    def _save_raw(self, raw):
        identifier = raw["id"]
        (self.evidence / (identifier + ".result.json")).write_text(json.dumps(raw))
        (self.evidence / (identifier + ".command.json")).write_text(json.dumps(raw["attempt"]))
        self._summary(raw)
        self._refresh()

    def _copy_output_and_refresh(self, victim, donor):
        target, source = self._raw(victim), self._raw(donor)
        target_path = self.root / target["attempt"]["stdout"]["path"]
        source_path = self.root / source["attempt"]["stdout"]["path"]
        target_path.write_bytes(source_path.read_bytes())
        target["attempt"]["stdout"] = validation.fingerprint(target_path, self.root)
        target["reasoner_result"] = copy.deepcopy(source["reasoner_result"])
        self._save_raw(target)

    def _custody_errors(self):
        return [error for error in validation.validate_stored(self.report, self.root)
                if "Invocation" in error or "invocation" in error]

    def test_honest_blocked_and_successful_invocations_pass_stored_custody(self):
        self.assertEqual(self.report["hierarchy_runs"]["source"]["status"], "technical_failure")
        self.assertEqual(self.report["hierarchy_runs"]["target"]["status"], "consistent")
        self.assertEqual(validation.validate_stored(self.report, self.root), [])
        self.assertEqual(len(self.selected), len(set(self.selected.values())))

    def test_a_cross_example_stdout_with_mutable_hashes_refreshed_fails(self):
        self._copy_output_and_refresh("example-00-aligned", "example-01-aligned")
        self.assertTrue(self._custody_errors())

    def test_b_cross_role_stdout_with_mutable_hashes_refreshed_fails(self):
        self._copy_output_and_refresh("example-00-aligned", "target-hierarchy")
        self.assertTrue(self._custody_errors())

    def test_c_source_only_to_aligned_stdout_fails(self):
        self._copy_output_and_refresh("example-00-aligned", "example-00-source")
        self.assertTrue(self._custody_errors())

    def test_d_aligned_to_source_only_stdout_fails(self):
        self._copy_output_and_refresh("example-00-source", "example-00-aligned")
        self.assertTrue(self._custody_errors())

    def test_f_different_input_graph_stdout_fails(self):
        self._copy_output_and_refresh("source-hierarchy", "target-hierarchy")
        self.assertTrue(self._custody_errors())

    def test_e_cross_query_stdout_with_mutable_hashes_refreshed_fails(self):
        self._copy_output_and_refresh("expectation-query-a", "expectation-query-b")
        self.assertTrue(self._custody_errors())

    def test_e_same_query_id_but_different_query_bytes_fails(self):
        victim = self._raw("expectation-query-a")
        alternative_query = self.fixture.build / "alternative.queries.json"
        changed = json.loads((self.root / victim["query_document"]["path"]).read_text())
        changed[0]["object"] = "urn:fixture:other-object"
        alternative_query.write_text(json.dumps(changed))
        command = [*victim["attempt"]["command"][:-1], str(alternative_query)]
        identity = {"id": victim["id"], "graph_identity": victim["execution_identity"]["graph_identity"],
            "governed_inputs": victim["closure"]["inputs"], "command_identity": {"mode": "consistency"}}
        ticket = custody.create_ticket(root=self.root, evidence=self.evidence,
            slot="diagnostic/" + victim["id"], identity=identity, closure=victim["closure"],
            graph_path=self.root / victim["input_document"]["path"],
            query_path=alternative_query, command=command)
        foreign = custody.canonical_bytes({**victim["reasoner_result"], "execution_marker": "same-id-other-query"})
        with patch.object(custody.subprocess, "run", return_value=subprocess.CompletedProcess(command, 0, foreign, b"")):
            donor = custody.execute_ticket(ticket, root=self.root)
        target_path = self.root / victim["attempt"]["stdout"]["path"]
        target_path.write_bytes(donor["paths"]["stdout"].read_bytes())
        victim["attempt"]["stdout"] = validation.fingerprint(target_path, self.root)
        victim["reasoner_result"] = json.loads(foreign)
        self._save_raw(victim)
        self.assertTrue(self._custody_errors())

    def test_h_foreign_stdout_with_all_mutable_report_hashes_fails(self):
        self._copy_output_and_refresh("example-00-aligned", "example-01-aligned")
        # Rebinding the summary, raw result, command, manifest, and an optional
        # publication ledger does not alter the wrapper's envelope/capture.
        victim = self._raw("example-00-aligned")
        self.report["publication_ledger"] = {"stdout_sha256": victim["attempt"]["stdout"]["sha256"]}
        self.assertTrue(self._custody_errors())

    def test_i_foreign_envelope_and_stdout_fails(self):
        victim, donor = self._raw("example-00-aligned"), self._raw("example-01-aligned")
        for kind in ("stdout", "envelope"):
            to_path = self.root / victim["attempt"][kind]["path"] if kind == "stdout" else self.root / victim["attempt"]["invocation"][kind]["path"]
            from_path = self.root / donor["attempt"][kind]["path"] if kind == "stdout" else self.root / donor["attempt"]["invocation"][kind]["path"]
            to_path.write_bytes(from_path.read_bytes())
            binding = validation.fingerprint(to_path, self.root)
            if kind == "stdout": victim["attempt"]["stdout"] = binding
            else: victim["attempt"]["invocation"]["envelope"] = binding
        victim["reasoner_result"] = donor["reasoner_result"]
        self._save_raw(victim)
        self.assertTrue(self._custody_errors())

    def test_j_mutable_summary_nonce_change_fails(self):
        self.report["examples"][0]["aligned"]["invocation_nonce"] = "0" * 64
        self.assertTrue(any("summary contradicts" in error for error in validation.validate_stored(self.report, self.root)))

    def test_k_reused_nonce_fails(self):
        first, second = list(self.selected.values())[:2]
        source = self.evidence / "invocations" / (first + ".ticket.json")
        target = self.evidence / "invocations" / (second + ".ticket.json")
        donor, duplicate = json.loads(source.read_text()), json.loads(target.read_text())
        duplicate["nonce"] = donor["nonce"]
        duplicate.pop("ticket_sha256")
        target.write_bytes(custody.canonical_bytes(custody.sealed(duplicate, "ticket_sha256")))
        self._refresh()
        self.assertTrue(any("nonce reused" in error for error in validation.validate_stored(self.report, self.root)))

    def test_same_slot_reexecution_has_new_challenge_and_fixed_selection(self):
        raw = self._raw("example-00-aligned")
        first_id = raw["selected_invocation_id"]
        second_ticket = custody.create_ticket(root=self.root, evidence=self.evidence,
            slot=self._slot(raw), identity=raw["execution_identity"], closure=raw["closure"],
            graph_path=self.root / raw["input_document"]["path"], query_path=None,
            command=raw["attempt"]["command"])
        second_bytes = custody.canonical_bytes({**raw["reasoner_result"], "execution_marker": "second-run"})
        with patch.object(custody.subprocess, "run", return_value=subprocess.CompletedProcess(
                raw["attempt"]["command"], 0, second_bytes, b"")):
            second = custody.execute_ticket(second_ticket, root=self.root)
        self.assertNotEqual(first_id, second["ticket"]["invocation_id"])
        self.assertNotEqual(raw["invocation_nonce"], second["ticket"]["nonce"])
        self.assertEqual(custody.verify_result(second_ticket, root=self.root,
            expected_slot=self._slot(raw), expected_invocation_id=second["ticket"]["invocation_id"])["stdout"], second_bytes)
        self._refresh()
        self.assertEqual(validation.validate_stored(self.report, self.root), [])
        # G: copying the second output into the first selected invocation fails.
        selected_path = self.root / raw["attempt"]["stdout"]["path"]
        selected_path.write_bytes(second_bytes)
        raw["attempt"]["stdout"] = validation.fingerprint(selected_path, self.root)
        raw["reasoner_result"] = json.loads(second_bytes)
        self._save_raw(raw)
        self.assertTrue(self._custody_errors())
        # A report-only selection switch also disagrees with the create-once selection record.
        self.report["selected_invocations"][self._slot(raw)] = second["ticket"]["invocation_id"]
        self.assertTrue(any("Selected invocation record" in error for error in validation.validate_stored(self.report, self.root)))

    def test_ticket_and_capture_are_create_once(self):
        raw = self._raw("example-00-aligned")
        ticket = self.evidence / "invocations" / (raw["selected_invocation_id"] + ".ticket.json")
        with self.assertRaises(FileExistsError):
            custody.create_once(ticket, b"replacement")
        with self.assertRaises(FileExistsError):
            custody.execute_ticket(ticket, root=self.root)

    def test_helper_refuses_changed_graph_before_launch(self):
        raw = self._raw("example-00-aligned")
        graph = self.root / raw["input_document"]["path"]
        ticket = custody.create_ticket(root=self.root, evidence=self.evidence,
            slot=self._slot(raw), identity=raw["execution_identity"], closure=raw["closure"],
            graph_path=graph, query_path=None, command=raw["attempt"]["command"])
        graph.write_bytes(graph.read_bytes() + b"changed after ticket")
        with patch.object(custody.subprocess, "run", side_effect=AssertionError("Java launched")):
            with self.assertRaisesRegex(ValueError, "graph bytes differ"):
                custody.execute_ticket(ticket, root=self.root)

    def test_helper_refuses_changed_query_before_launch(self):
        raw = self._raw("expectation-query-a")
        graph = self.root / raw["input_document"]["path"]
        query = self.root / raw["query_document"]["path"]
        ticket = custody.create_ticket(root=self.root, evidence=self.evidence,
            slot=self._slot(raw), identity=raw["execution_identity"], closure=raw["closure"],
            graph_path=graph, query_path=query, command=raw["attempt"]["command"])
        query.write_bytes(query.read_bytes() + b"changed after ticket")
        with patch.object(custody.subprocess, "run", side_effect=AssertionError("Java launched")):
            with self.assertRaisesRegex(ValueError, "query bytes differ"):
                custody.execute_ticket(ticket, root=self.root)

    def test_diagnostic_ticket_cannot_fill_governed_publication_slot(self):
        raw = self._raw("example-00-aligned")
        identity = {"id": raw["id"], "graph_identity": raw["execution_identity"]["graph_identity"],
            "governed_inputs": raw["closure"]["inputs"], "command_identity": {"mode": "consistency"}}
        ticket = custody.create_ticket(root=self.root, evidence=self.evidence,
            slot="diagnostic/" + raw["id"], identity=identity, closure=raw["closure"],
            graph_path=self.root / raw["input_document"]["path"], query_path=None,
            command=raw["attempt"]["command"])
        stdout = custody.canonical_bytes(raw["reasoner_result"])
        with patch.object(custody.subprocess, "run", return_value=subprocess.CompletedProcess(
                raw["attempt"]["command"], 0, stdout, b"")):
            diagnostic = custody.execute_ticket(ticket, root=self.root)
        with self.assertRaisesRegex(ValueError, "selected execution"):
            custody.verify_result(ticket, root=self.root, expected_slot=self._slot(raw),
                expected_invocation_id=diagnostic["ticket"]["invocation_id"])


if __name__ == "__main__":
    unittest.main()
