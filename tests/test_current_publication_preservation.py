import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_publication_preservation as preservation
import current_documentary_workbook as documentary
from current_source_identity import fingerprint


class CurrentPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start with the independently retained baseline, not a new checker-
        # generated fixture. Git objects supply a separate expected authority.
        cls.baseline = json.loads(preservation.BASELINE.read_text())
        cls.protected = {path for paths in preservation.protected_groups().values() for path in paths}

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Read-only access to the real immutable object database; test mutations
        # go exclusively into copied candidate files and JSON dictionaries.
        (self.root / ".git").symlink_to(preservation.ROOT / ".git", target_is_directory=True)
        for relative in self.protected:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(preservation.ROOT / relative, path)
        # These fixtures test the pinned Git baseline and isolated transitions
        # from it, rather than inheriting the maintained live documentary chain.
        documentary_baseline = json.loads((preservation.ROOT / documentary.BASELINE).read_text())
        shutil.copyfile(preservation.ROOT / documentary_baseline["historical_workbook"]["path"],
                        self.root / preservation.WORKBOOK)
        self.baseline = copy.deepcopy(type(self).baseline)

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
        path = self.root / "reports/new-publication-evidence.json"
        path.write_text('{"status": "blocked"}\n')
        self.assertEqual(self.check()["status"], "PASS")

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
        historical = self.documentary_candidate()
        documentary_baseline = json.loads((preservation.ROOT / documentary.BASELINE).read_text())
        paths = {documentary.BASELINE, documentary_baseline["historical_workbook"]["path"],
                 *(ref["path"] for ref in documentary_baseline["immutable_evidence"])}
        for relative in paths:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(preservation.ROOT / relative, destination)
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
        forged = json.loads(transition.read_text())
        forged["changes"] = []
        transition.write_bytes(documentary.canonical_bytes(forged))
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(preservation.WORKBOOK, result["groups"]["current_mapping_semantics"]["changed_paths"])
        self.assertIn("manifest is incomplete", result["documentary_workbook_evolution"]["error"])


if __name__ == "__main__":
    unittest.main()
