import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_publication_preservation as preservation
import current_documentary_workbook as documentary
import current_decision_applicability as applicability
import current_retained_evidence as retained
import current_semantic_workbook as semantic
import current_source_identity as identity
from current_source_identity import fingerprint


class CurrentPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start with the independently retained baseline, not a new checker-
        # generated fixture. Git objects supply a separate expected authority.
        cls.baseline = json.loads(preservation.BASELINE.read_text())
        groups = preservation.protected_groups()
        cls.protected = {path for paths in groups.values() for path in paths}
        historical = preservation.trusted_tree(preservation.ROOT, preservation.EXPECTED_BASELINE_HEAD)
        cls.historical_bytes = {}
        for relative in cls.protected:
            head = (preservation.EXPECTED_BASELINE_HEAD if relative in historical
                    else identity.ACCEPTED_CHECKPOINT_HEAD)
            cls.historical_bytes[relative] = subprocess.check_output([
                "git", "-C", str(preservation.ROOT), "show", f"{head}:{relative}"])
        # Dependency discovery does not enlarge the immutable protection set.
        cls.current_paths = {
            *cls.protected, identity.WORKBOOK, preservation.ASSESSMENT,
            *identity.CONFIGURATION, *semantic.SOURCE_TARGET_SHA256,
            *semantic.GOVERNED_INPUT_SHA256, *semantic.evidence_paths(preservation.ROOT),
            *applicability.evidence_paths(preservation.ROOT),
        }
        for relative in groups["historical_authorities"]:
            cls.current_paths.update(retained.evidence_paths(
                preservation.ROOT, relative, historical[relative]["sha256"]))

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Read-only access to the real immutable object database; test mutations
        # go exclusively into copied candidate files and JSON dictionaries.
        (self.root / ".git").symlink_to(preservation.ROOT / ".git", target_is_directory=True)
        # Historical unit scenarios use exact original protected bytes and
        # additive checkpoint custody, not live post-transition artifacts.
        for relative, data in self.historical_bytes.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.baseline = copy.deepcopy(type(self).baseline)

    def install_current_state(self):
        """Copy the governed current state and its complete authentication closure."""
        for relative in self.current_paths:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(preservation.ROOT / relative, path)

    def check(self):
        return preservation.preservation(self.root, self.baseline)

    def test_unchanged_protected_bytes_pass(self):
        result = self.check()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["baseline_head"], preservation.EXPECTED_BASELINE_HEAD)
        self.assertEqual(sum(group["file_count"] for group in result["groups"].values()), len(self.protected))

    def test_remove_required_mutable_baseline_entry_fails(self):
        relative = "src/sosa-next/imports/sosa.ttl"
        del self.baseline["tracked_files"][relative]
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("missing or extra paths" in error for error in result["errors"]))
        self.assertIn(relative, result["groups"]["pinned_sosa_2023"]["expected_sha256"])

    def test_changed_workbook_and_forged_matching_baseline_hash_fail(self):
        path = self.root / preservation.WORKBOOK
        path.write_bytes(path.read_bytes() + b"tampered protected workbook")
        self.baseline["tracked_files"][preservation.WORKBOOK] = fingerprint(path)
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])
        self.assertTrue(any("mutable hash differs from trusted Git blob" in error for error in result["errors"]))

    def test_changed_sosa_2023_and_forged_matching_baseline_hash_fail(self):
        relative = "src/sosa-next/imports/sosa.ttl"
        path = self.root / relative
        path.write_bytes(path.read_bytes() + b"\n<urn:changed> <urn:predicate> <urn:object> .\n")
        self.baseline["tracked_files"][relative] = fingerprint(path)
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(relative, result["groups"]["pinned_sosa_2023"]["changed_paths"])

    def test_missing_protected_candidate_file_fails(self):
        (self.root / preservation.WORKBOOK).unlink()
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])

    def test_extra_protected_candidate_path_fails_with_or_without_baseline_claim(self):
        relative = "src/sosa-next/imports/extra.ttl"
        path = self.root / relative
        path.write_text("<urn:extra> <urn:predicate> <urn:object> .\n")
        for add_claim in (False, True):
            with self.subTest(add_claim=add_claim):
                if add_claim:
                    self.baseline["tracked_files"][relative] = fingerprint(path)
                result = self.check()
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any("extra protected path" in error for error in result["errors"]))

    def test_candidate_publication_evidence_is_not_historical_protected_content(self):
        self.install_current_state()
        before = self.check()
        self.assertEqual(before["status"], "PASS", before["errors"])
        relative = "reports/new-publication-evidence.json"
        path = self.root / relative
        path.write_text('{"status": "blocked"}\n')
        result = self.check()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(path.is_file())
        self.assertEqual(result["groups"], before["groups"])
        self.assertNotIn(relative, self.protected)
        for group in result["groups"].values():
            self.assertNotIn(relative, group["expected_sha256"])

    def test_mutable_repository_heads_cannot_change_trust_root(self):
        for location in (self.baseline, self.baseline["external_coms"]):
            with self.subTest(location="external" if location is self.baseline["external_coms"] else "local"):
                original = location["head"]
                location["head"] = "f" * 40
                self.assertEqual(self.check()["status"], "FAIL")
                location["head"] = original

    def test_external_coms_mutable_hash_cannot_redefine_expected_bytes(self):
        relative = next(iter(self.baseline["external_coms"]["tracked_file_hashes"]))
        self.baseline["external_coms"]["tracked_file_hashes"][relative] = "f" * 64
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("external COMS inventory" in error for error in result["errors"]))

    def documentary_candidate(self):
        historical = self.root / "reports/documentary-historical-workbook.xlsx"
        shutil.copyfile(self.root / preservation.WORKBOOK, historical)
        book = load_workbook(self.root / preservation.WORKBOOK)
        book["Sheet1"]["D4"] = "Documentary fixture, with no semantic cell change."
        book.save(self.root / preservation.WORKBOOK)
        book.close()
        return historical

    def test_valid_documentary_chain_preserves_pinned_baseline(self):
        historical = self.documentary_candidate()
        original = copy.deepcopy(self.baseline)
        with patch.object(preservation, "validate_workbook_evolution", return_value=historical) as validate:
            result = self.check()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(self.baseline, original)
        self.assertNotIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])
        self.assertEqual(result["documentary_workbook_evolution"]["status"], "VALIDATED")
        self.assertEqual(result["groups"]["current_mapping_semantics"]["expected_sha256"][preservation.WORKBOOK],
                         original["tracked_files"][preservation.WORKBOOK]["sha256"])
        validate.assert_called_once_with(self.root, original["tracked_files"][preservation.WORKBOOK]["sha256"],
                                         self.root / preservation.WORKBOOK)

    def test_documentary_chain_failure_retains_workbook_drift(self):
        self.documentary_candidate()
        with patch.object(preservation, "validate_workbook_evolution", side_effect=ValueError("unaccounted D cell")):
            result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])
        self.assertEqual(result["documentary_workbook_evolution"]["status"], "FAIL")
        self.assertEqual(result["documentary_workbook_evolution"]["error"], "unaccounted D cell")

    def test_documentary_exception_does_not_cover_other_protected_changes(self):
        historical = self.documentary_candidate()
        relative = "src/sosa-next/imports/sosa.ttl"
        path = self.root / relative
        path.write_bytes(path.read_bytes() + b"\n# Changed protected source\n")
        with patch.object(preservation, "validate_workbook_evolution", return_value=historical):
            result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(relative, result["groups"]["pinned_sosa_2023"]["changed_paths"])

    def test_wrong_historical_snapshot_cannot_replace_git_trust_root(self):
        historical = self.documentary_candidate()
        historical.write_bytes(historical.read_bytes() + b"changed retained bytes")
        with patch.object(preservation, "validate_workbook_evolution", return_value=historical):
            result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])
        self.assertIn("differs from trusted Git blob", result["documentary_workbook_evolution"]["error"])

    def test_real_documentary_chain_and_forged_manifest_integration(self):
        # The accepted checkpoint's existing documentary records are now
        # immutable protected evidence. Extend their tail instead of inventing
        # a competing history from the original workbook.
        self.install_current_state()
        historical = self.documentary_candidate()
        current = self.root / preservation.WORKBOOK
        old_book = load_workbook(historical, read_only=True)
        new_book = load_workbook(current, read_only=True)
        try:
            self.assertNotEqual(old_book["Sheet1"]["D4"].value,
                                new_book["Sheet1"]["D4"].value)
        finally:
            old_book.close()
            new_book.close()
        self.assertNotEqual(fingerprint(historical)["sha256"], fingerprint(current)["sha256"])
        self.assertEqual(documentary.semantic_projection_sha256(historical),
                         documentary.semantic_projection_sha256(current))
        evidence_path = "imports/sosa.ttl"
        transition = documentary.create_update(
            self.root, historical, self.root / preservation.WORKBOOK,
            {"Sheet1!D4": [{"path": evidence_path,
                            "sha256": documentary.digest((self.root / evidence_path).read_bytes()),
                            "reference": "Test fixture evidence for documentary-only evolution"}]},
            editor_identity="Integration test fixture")
        result = self.check()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["documentary_workbook_evolution"]["status"], "VALIDATED")
        custody = result["assessment_row_id_evolution"]
        self.assertEqual(custody["status"], "VALIDATED")
        self.assertIn("http://www.w3.org/ns/ssn/systems/MeasurementRange",
                      {item["source_iri"] for item in custody["new_human_decisions"]})
        print("D4 documentary integration: D4 changed; full workbook SHA changed; "
              "semantic projection unchanged; documentary transition authenticated; "
              "MeasurementRange sufficiency evidence current; assessment custody authenticated.",
              flush=True)
        forged = json.loads(transition.read_text())
        forged["changes"] = []
        transition.write_bytes(documentary.canonical_bytes(forged))
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])
        self.assertIn("manifest is incomplete", result["documentary_workbook_evolution"]["error"])


if __name__ == "__main__":
    unittest.main()
