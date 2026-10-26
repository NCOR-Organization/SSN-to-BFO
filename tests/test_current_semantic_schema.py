#!/usr/bin/env python3
"""Current evidence cannot opt out of custody through mutable report metadata.

Every adversarial case is checked directly at both stored-evidence entry points.
Fixtures use the real ticket creator and capture wrapper with synthetic process
results; no ontology judgment, production execution, or approval is fabricated.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_semantic_invocation as custody
import current_semantic_validation as validation
from tests import test_current_semantic_invocation as invocation_tests


class CurrentSchemaBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = invocation_tests.InvocationCustodyTests(
            "test_honest_blocked_and_successful_invocations_pass_stored_custody")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root, self.evidence, self.report = self.fixture.root, self.fixture.evidence, self.fixture.report
        self.assert_both_pass()

    def assert_both_pass(self):
        self.assertEqual(validation.reconcile_raw_evidence(self.report, self.root)[1], [])
        self.assertEqual(validation.validate_stored(self.report, self.root), [])

    def assert_both_reject(self, *messages):
        self._assert_entrypoint_errors(messages)
        if type(self.report.get("execution_evidence_schema")) is int and self.report["execution_evidence_schema"] == 2:
            # Repeat every intact-schema substitution with downgraded mutable
            # declarations as well, without restoring the foreign artifacts.
            missing = object()
            try:
                for schema in (missing, None, 1, 3, "2"):
                    with self.subTest(additional_schema_downgrade="missing" if schema is missing else schema):
                        if schema is missing:
                            self.report.pop("execution_evidence_schema", None)
                        else:
                            self.report["execution_evidence_schema"] = schema
                        self._assert_entrypoint_errors(("schema",))
            finally:
                self.report["execution_evidence_schema"] = 2

    def _assert_entrypoint_errors(self, messages):
        for label, errors in (
            ("reconcile_raw_evidence", validation.reconcile_raw_evidence(self.report, self.root)[1]),
            ("validate_stored", validation.validate_stored(self.report, self.root)),
        ):
            with self.subTest(entrypoint=label):
                self.assertTrue(errors, label + " accepted invalid current evidence")
                self.assertTrue(any(any(message.lower() in error.lower() for message in messages)
                                    for error in errors), (label, errors))
        if "schema" in messages:
            errors = validation.validate_publication_execution_bindings(self.report, self.root)
            self.assertTrue(any("schema" in error.lower() for error in errors), errors)

    def _legacy_locations(self):
        """Refresh every mutable location, as the reproduced downgrade did."""
        for path in sorted(self.evidence.glob("*.result.json")):
            raw = json.loads(path.read_text())
            for channel in ("stdout", "stderr"):
                original = self.root / raw["attempt"][channel]["path"]
                legacy = self.evidence / (raw["id"] + "." + channel + ".log")
                legacy.write_bytes(original.read_bytes())
                raw["attempt"][channel] = validation.fingerprint(legacy, self.root)
            self.fixture._save_raw(raw)

    def _copy_and_refresh(self, victim, donor):
        self.fixture._copy_output_and_refresh(victim, donor)
        # These redundant mutable reports cannot supersede custody artifacts.
        raw = self.fixture._raw(victim)
        self.report["publication_ledger"] = {
            "stdout_sha256": raw["attempt"]["stdout"]["sha256"],
            "raw_result_sha256": validation.sha256(self.evidence / (victim + ".result.json")),
        }
        (self.evidence / "summary.json").write_text(json.dumps(self.report))
        self.report["publication_ledger"]["summary_sha256"] = validation.sha256(self.evidence / "summary.json")

    def _same_slot_retry(self):
        raw = self.fixture._raw("example-00-aligned")
        ticket_path = custody.create_ticket(root=self.root, evidence=self.evidence,
            slot=self.fixture._slot(raw), identity=raw["execution_identity"], closure=raw["closure"],
            graph_path=self.root / raw["input_document"]["path"], query_path=None,
            command=raw["attempt"]["command"])
        stdout = custody.canonical_bytes({**raw["reasoner_result"], "execution_marker": "separate-second-invocation"})
        with patch.object(custody.subprocess, "run", return_value=subprocess.CompletedProcess(
                raw["attempt"]["command"], 0, stdout, b"")):
            receipt = custody.execute_ticket(ticket_path, root=self.root)
        self.assertNotEqual(receipt["ticket"]["invocation_id"], raw["selected_invocation_id"])
        self.assertNotEqual(receipt["ticket"]["nonce"], raw["invocation_nonce"])
        self.fixture._refresh()
        self.assert_both_pass()  # A retained unselected retry is not itself invalid.
        return receipt

    def _replace_with_retry(self, receipt):
        raw = self.fixture._raw("example-00-aligned")
        path = self.root / raw["attempt"]["stdout"]["path"]
        path.write_bytes(receipt["paths"]["stdout"].read_bytes())
        raw["attempt"]["stdout"] = validation.fingerprint(path, self.root)
        raw["reasoner_result"] = json.loads(path.read_bytes())
        self.fixture._save_raw(raw)

    def _rewrite_envelope(self, change):
        raw = self.fixture._raw("example-00-aligned")
        path = self.root / raw["attempt"]["invocation"]["envelope"]["path"]
        envelope = json.loads(path.read_bytes())
        envelope.pop("envelope_sha256")
        change(envelope)
        path.write_bytes(custody.canonical_bytes(custody.sealed(envelope, "envelope_sha256")))
        raw["attempt"]["invocation"]["envelope"] = validation.fingerprint(path, self.root)
        self.fixture._save_raw(raw)

    def test_a_missing_schema_fails_both_current_entrypoints(self):
        self.report.pop("execution_evidence_schema")
        self.assert_both_reject("schema")

    def test_b_null_schema_fails_both_current_entrypoints(self):
        self.report["execution_evidence_schema"] = None
        self.assert_both_reject("schema")

    def test_c_legacy_schema_fails_both_current_entrypoints(self):
        self.report["execution_evidence_schema"] = 1
        self.assert_both_reject("schema")

    def test_d_future_schema_fails_both_current_entrypoints(self):
        self.report["execution_evidence_schema"] = 3
        self.assert_both_reject("schema")

    def test_e_malformed_schema_values_fail_both_current_entrypoints(self):
        for value in ("2", "legacy", True, False, 2.0, [], {}, {"version": 2}):
            with self.subTest(value=value):
                self.report["execution_evidence_schema"] = value
                self.assert_both_reject("schema")

    def test_f_missing_schema_and_legacy_cross_example_rebinding_fails(self):
        immutable = {path: path.read_bytes() for path in (self.evidence / "invocations").iterdir()}
        self._legacy_locations()
        self.report.pop("execution_evidence_schema")
        self._copy_and_refresh("example-00-aligned", "example-01-aligned")
        self.assertEqual(immutable, {path: path.read_bytes() for path in immutable})
        self.assert_both_reject("schema")

    def test_g_legacy_schema_and_legacy_cross_role_rebinding_fails(self):
        self._legacy_locations()
        self.report["execution_evidence_schema"] = 1
        self._copy_and_refresh("example-00-aligned", "target-hierarchy")
        self.assert_both_reject("schema")

    def test_h_missing_schema_and_cross_phase_rebinding_fails(self):
        self._legacy_locations()
        self.report.pop("execution_evidence_schema")
        self._copy_and_refresh("example-00-aligned", "example-00-source")
        self.assert_both_reject("schema")
        self._copy_and_refresh("example-01-source", "example-01-aligned")
        self.assert_both_reject("schema")

    def test_i_missing_schema_and_same_slot_retry_rebinding_fails(self):
        retry = self._same_slot_retry()
        self._legacy_locations()
        self.report.pop("execution_evidence_schema")
        self._replace_with_retry(retry)
        self.assert_both_reject("schema")

    def test_j_removing_all_custody_and_refreshing_mutable_metadata_fails(self):
        self._legacy_locations()
        raw = self.fixture._raw("example-00-aligned")
        for kind in ("ticket", "envelope", "capture"):
            (self.root / raw["attempt"]["invocation"][kind]["path"]).unlink()
        raw["attempt"].pop("invocation")
        self.report.pop("execution_evidence_schema")
        self.fixture._save_raw(raw)
        self.assert_both_reject("schema")

    def test_k_current_schema_with_missing_custody_artifact_fails(self):
        raw = self.fixture._raw("example-00-aligned")
        for kind in ("ticket", "envelope", "capture", "stdout", "stderr"):
            with self.subTest(kind=kind):
                binding = raw["attempt"].get(kind) or raw["attempt"]["invocation"][kind]
                path = self.root / binding["path"]
                content = path.read_bytes()
                path.unlink()
                self.fixture._refresh()
                self.assert_both_reject("invocation")
                path.write_bytes(content)
                self.fixture._refresh()
                self.assert_both_pass()

    def test_l_current_schema_with_wrong_ticket_envelope_linkage_fails(self):
        self._rewrite_envelope(lambda envelope: envelope.update(ticket_sha256="f" * 64))
        self.assert_both_reject("Invocation challenge or slot")

    def test_full_matrix_cross_example_stdout_fails_both(self):
        self._copy_and_refresh("example-00-aligned", "example-01-aligned")
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_cross_role_stdout_fails_both(self):
        self._copy_and_refresh("example-00-aligned", "target-hierarchy")
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_source_stdout_in_aligned_fails_both(self):
        self._copy_and_refresh("example-00-aligned", "example-00-source")
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_aligned_stdout_in_source_fails_both(self):
        self._copy_and_refresh("example-00-source", "example-00-aligned")
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_different_query_stdout_fails_both(self):
        self._copy_and_refresh("expectation-query-a", "expectation-query-b")
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_different_graph_stdout_fails_both(self):
        self._copy_and_refresh("source-hierarchy", "target-hierarchy")
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_same_slot_retry_stdout_fails_both(self):
        self._replace_with_retry(self._same_slot_retry())
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_foreign_envelope_and_stdout_fails_both(self):
        raw, donor = self.fixture._raw("example-00-aligned"), self.fixture._raw("example-01-aligned")
        for kind in ("stdout", "envelope"):
            target_binding = raw["attempt"].get(kind) or raw["attempt"]["invocation"][kind]
            donor_binding = donor["attempt"].get(kind) or donor["attempt"]["invocation"][kind]
            target = self.root / target_binding["path"]
            target.write_bytes((self.root / donor_binding["path"]).read_bytes())
            target_binding.update(validation.fingerprint(target, self.root))
        raw["reasoner_result"] = copy.deepcopy(donor["reasoner_result"])
        self.fixture._save_raw(raw)
        self.assert_both_reject("Invocation captured result differs", "Invocation challenge or slot")

    def test_full_matrix_summary_nonce_alteration_fails_both(self):
        self.report["examples"][0]["aligned"]["invocation_nonce"] = "0" * 64
        self.assert_both_reject("summary contradicts raw evidence")

    def test_full_matrix_nonce_reuse_fails_both(self):
        first, second = list(self.fixture.selected.values())[:2]
        donor = json.loads((self.evidence / "invocations" / (first + ".ticket.json")).read_bytes())
        path = self.evidence / "invocations" / (second + ".ticket.json")
        changed = json.loads(path.read_bytes())
        changed.pop("ticket_sha256")
        changed["nonce"] = donor["nonce"]
        path.write_bytes(custody.canonical_bytes(custody.sealed(changed, "ticket_sha256")))
        self.fixture._refresh()
        self.assert_both_reject("nonce reused")

    def test_full_matrix_correct_slot_wrong_ticket_sha_fails_both(self):
        self._rewrite_envelope(lambda envelope: envelope.update(ticket_sha256="a" * 64))
        self.assert_both_reject("Invocation challenge or slot")

    def test_full_matrix_altered_stdout_bytes_fails_both(self):
        raw = self.fixture._raw("example-00-aligned")
        path = self.root / raw["attempt"]["stdout"]["path"]
        path.write_bytes(path.read_bytes() + b"\n")
        raw["attempt"]["stdout"] = validation.fingerprint(path, self.root)
        self.fixture._save_raw(raw)
        self.assert_both_reject("Invocation stdout differs from captured execution")

    def test_full_matrix_altered_envelope_invocation_id_fails_both(self):
        self._rewrite_envelope(lambda envelope: envelope.update(invocation_id="ffffffff-ffff-4fff-bfff-ffffffffffff"))
        self.assert_both_reject("Invocation challenge or slot")

    def test_honest_success_and_blocked_current_outputs_pass_both(self):
        self.assertEqual(self.report["hierarchy_runs"]["target"]["status"], "consistent")
        self.assertEqual(self.report["hierarchy_runs"]["source"]["status"], "technical_failure")
        self.assert_both_pass()

    def test_retained_unselected_same_slot_retry_is_valid_both(self):
        retry = self._same_slot_retry()
        selected = self.report["selected_invocations"][self.fixture._slot(self.fixture._raw("example-00-aligned"))]
        self.assertNotEqual(selected, retry["ticket"]["invocation_id"])
        self.assert_both_pass()


class HistoricalSchemaBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="current-historical-schema-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive = validation.HISTORICAL_ARCHIVE_PATH
        shutil.copytree(ROOT / self.archive.parent, self.root / self.archive.parent)

    def test_fixed_historical_archive_reads_only_as_ineligible_history(self):
        before = {path.relative_to(self.root): path.read_bytes()
                  for path in (self.root / self.archive.parent).rglob("*") if path.is_file()}
        result = validation.read_historical_archive(root=self.root)
        self.assertEqual(result["kind"], "historical_legacy_archive")
        self.assertEqual(result["status"], "HISTORICAL_ONLY")
        self.assertIs(result["current_review_evidence_eligible"], False)
        self.assertIs(result["publication_evidence_eligible"], False)
        self.assertEqual(result["original_execution_summary"], json.loads((self.root / self.archive).read_bytes()))
        self.assertEqual(before, {path.relative_to(self.root): path.read_bytes()
                                 for path in (self.root / self.archive.parent).rglob("*") if path.is_file()})

    def test_historical_reader_rejects_changed_pinned_summary(self):
        path = self.root / self.archive
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaises(ValueError):
            validation.read_historical_archive(root=self.root)

    def test_historical_reader_rejects_changed_retained_output(self):
        original = json.loads((self.root / self.archive).read_bytes())
        binding = next(item for item in original["evidence_files"] if item["path"].endswith(".stdout.log"))
        path = self.root / binding["path"]
        path.write_bytes(path.read_bytes() + b"changed historical bytes")
        with self.assertRaises(ValueError):
            validation.read_historical_archive(root=self.root)

    def test_recognized_history_cannot_satisfy_current_slots(self):
        original = validation.read_historical_archive(root=self.root)["original_execution_summary"]
        # Current entry points reject by their contract before missing current
        # fixture inputs can supply an unrelated reason to reject this archive.
        for errors in (validation.reconcile_raw_evidence(original, self.root)[1],
                       validation.validate_stored(original, self.root)):
            self.assertTrue(any("execution_evidence_schema=2" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
