"""Historical evidence custody wiring; mutations stay in isolated fixtures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import current_documentary_workbook as documentary
import current_publication_preservation as publication
import current_retained_evidence as retained
import current_semantic_workbook as semantic


SOURCE_COMMIT = "dc314460fe3e875ba1c8ccfcb3c6840a7181e733"
UPDATE = "reports/current-documentary-workbook/updates/5f0e3bc5-b52e-4502-8fd5-f7f1c182913b.json"
UPDATE_SHA256 = "6dd57cd87fdd3dda457ead9cfd747ec94081c3967dd117ef5d2f6d907798f5e1"
DIFF = "reports/coms-vs-pre-coms-legacy-diff.md"
COVERAGE = "reports/coms-source-term-coverage.md"
DIFF_HISTORICAL_SHA256 = "7437af5ccb6b581a062ba6edcee530e6a068ccd676d10e821ac318c6727be860"
PRE_RECOVERY_COMMIT = "fe06c78b7290fd586b05c42145a57f32d84a8674"
DIFF_PRE_RECOVERY_SHA256 = "e3dd0e160c6cf2acf994f462dc9ccd631fc7e9a934e58307362e20d8a248c80d"
DIFF_CURRENT_SHA256 = "eed00cb5b90ffbe368cf92469fef970e98eac0f28372868408e4a57f1219801c"
COVERAGE_HISTORICAL_SHA256 = "11330ccd4bed83934a6520a6cb6024c7f31bc5ebf5d405f5045e58b7d8deb36c"
DECISION = "reports/current-human-decisions/2026-10-25-sample-pair/hasSample.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(logical: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{SOURCE_COMMIT}:{logical}"])


class RetainedEvidenceWiringTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        # The fixture may read the immutable source objects. It never invokes
        # a Git mutation, and all created evidence lives under the temp root.
        (self.root / ".git").symlink_to(ROOT / ".git", target_is_directory=True)

    def write(self, logical: str, data: bytes) -> Path:
        path = self.root / logical
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def evolved(self, logical: str = DIFF):
        original = git_bytes(logical)
        ref = {"path": logical, "sha256": digest(original)}
        live = self.write(logical, original)
        manifest = retained.retain_git(
            self.root, logical, ref["sha256"], SOURCE_COMMIT,
            creation_date="2026-10-26T12:00:00+00:00",
            reason="Isolated integration fixture for a changed historical evidence path")
        live.write_bytes(original + b"\nChanged current fixture bytes.\n")
        snapshot = retained.resolve(self.root, logical, ref["sha256"])
        self.assertNotEqual(snapshot, live)
        return ref, live, manifest, snapshot, original

    def test_documentary_unchanged_evidence_uses_live_path(self):
        data = git_bytes(DIFF)
        live = self.write(DIFF, data)
        ref = {"path": DIFF, "sha256": digest(data), "reference": "line 123"}
        documentary._evidence(self.root, [ref])
        self.assertEqual(documentary._bound_file(self.root, ref), live)
        self.assertEqual(documentary._evidence_paths(self.root, [ref]), {DIFF})
        self.assertFalse((self.root / retained.STORE).exists())

    def test_documentary_fallback_binds_selected_manifest_and_snapshot(self):
        ref, live, manifest, snapshot, original = self.evolved()
        documentary._evidence(self.root, [ref])
        self.assertEqual(documentary._bound_file(self.root, ref, allow_retained=True), snapshot)
        self.assertEqual(snapshot.read_bytes(), original)
        self.assertNotEqual(live.read_bytes(), original)
        self.assertEqual(documentary._evidence_paths(self.root, [ref]), {
            DIFF, manifest.relative_to(self.root).as_posix(),
            snapshot.relative_to(self.root).as_posix(),
        })

    def test_documentary_missing_retained_bytes_fail(self):
        ref, _live, _manifest, snapshot, _original = self.evolved()
        snapshot.unlink()
        with self.assertRaises(ValueError):
            documentary._evidence(self.root, [ref])

    def test_documentary_corrupt_retained_bytes_fail(self):
        ref, _live, _manifest, snapshot, _original = self.evolved()
        snapshot.write_bytes(snapshot.read_bytes() + b"corruption")
        with self.assertRaises(ValueError):
            documentary._evidence(self.root, [ref])

    def test_wrong_logical_binding_cannot_satisfy_documentary_or_publication_evidence(self):
        ref, _live, manifest, _snapshot, original = self.evolved()
        metadata = json.loads(manifest.read_bytes())
        metadata["logical_path"] = COVERAGE
        manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
        with self.assertRaises(ValueError):
            documentary._evidence(self.root, [ref])
        with self.assertRaises(ValueError):
            publication.retained_historical_reports(
                self.root, [DIFF], {DIFF: {"sha256": ref["sha256"], "bytes": len(original)}})

    def test_snapshot_cannot_excuse_immutable_decision_drift(self):
        ref, live, _manifest, snapshot, original = self.evolved(DECISION)
        # Establish that a valid retained copy really exists before testing
        # the deliberately stricter immutable-decision call path.
        self.assertEqual(retained.resolve(self.root, DECISION, ref["sha256"]), snapshot)
        self.assertEqual(snapshot.read_bytes(), original)
        self.assertNotEqual(digest(live.read_bytes()), ref["sha256"])
        with self.assertRaises(ValueError):
            documentary._bound_file(self.root, ref)

    def test_publication_accepts_both_current_reports_with_exact_old_bytes(self):
        expected, fixtures = {}, {}
        for logical in (DIFF, COVERAGE):
            ref, live, _manifest, snapshot, original = self.evolved(logical)
            expected[logical] = {"sha256": ref["sha256"], "bytes": len(original)}
            fixtures[logical] = (live, snapshot)
        historical_inventory = json.loads(json.dumps(expected))
        result = publication.retained_historical_reports(self.root, list(expected), expected)
        self.assertEqual(set(result), {DIFF, COVERAGE})
        self.assertEqual(expected, historical_inventory)
        for logical, (live, snapshot) in fixtures.items():
            self.assertEqual(result[logical], {
                "historical_snapshot_path": snapshot.relative_to(self.root).as_posix(),
                "sha256": expected[logical]["sha256"],
                "live_sha256": digest(live.read_bytes()),
            })
            self.assertNotEqual(result[logical]["sha256"], result[logical]["live_sha256"])

    def test_publication_unchanged_report_needs_no_retained_exception(self):
        original = git_bytes(DIFF)
        self.write(DIFF, original)
        expected = {DIFF: {"sha256": digest(original), "bytes": len(original)}}
        self.assertEqual(publication.retained_historical_reports(self.root, [DIFF], expected), {})
        self.assertFalse((self.root / retained.STORE).exists())

    def test_publication_snapshot_does_not_excuse_wrong_expected_size(self):
        ref, _live, _manifest, _snapshot, original = self.evolved()
        expected = {DIFF: {"sha256": ref["sha256"], "bytes": len(original) + 1}}
        with self.assertRaises(ValueError):
            publication.retained_historical_reports(self.root, [DIFF], expected)

    def test_publication_rejects_missing_snapshot(self):
        ref, _live, _manifest, snapshot, original = self.evolved()
        snapshot.unlink()
        with self.assertRaises(ValueError):
            publication.retained_historical_reports(
                self.root, [DIFF], {DIFF: {"sha256": ref["sha256"], "bytes": len(original)}})

    def test_publication_rejects_corrupt_snapshot(self):
        ref, _live, _manifest, snapshot, original = self.evolved()
        snapshot.write_bytes(original + b"corruption")
        with self.assertRaises(ValueError):
            publication.retained_historical_reports(
                self.root, [DIFF], {DIFF: {"sha256": ref["sha256"], "bytes": len(original)}})

    def test_publication_rejects_corrupt_manifest(self):
        ref, _live, manifest, _snapshot, original = self.evolved()
        manifest.write_text("{}\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            publication.retained_historical_reports(
                self.root, [DIFF], {DIFF: {"sha256": ref["sha256"], "bytes": len(original)}})

    def test_publication_retention_does_not_cover_other_protected_paths(self):
        for logical in (
            "legacy/workbooks/Current_SOSA-SSN to BFO-CCO.xlsx",
            "mappings/SSN2BFO-COMS.xlsx", DECISION, "imports/sosa.ttl",
        ):
            with self.subTest(logical=logical):
                ref, _live, _manifest, _snapshot, original = self.evolved(logical)
                expected = {logical: {"sha256": ref["sha256"], "bytes": len(original)}}
                self.assertEqual(publication.retained_historical_reports(
                    self.root, [logical], expected), {})
                # The historical-retention helper cannot erase this drift;
                # the ordinary byte-preservation comparison still reports it.
                self.assertEqual(publication.compare([logical], expected, self.root), [logical])


class RetainedRepositoryHistoryTests(unittest.TestCase):
    def test_four_documentary_bindings_retain_exact_history_and_live_report(self):
        original_record = (ROOT / UPDATE).read_bytes()
        current_report = (ROOT / DIFF).read_bytes()
        self.assertEqual(digest(original_record), UPDATE_SHA256)
        pre_recovery_report = subprocess.check_output(
            ["git", "--no-optional-locks", "-C", str(ROOT), "show", f"{PRE_RECOVERY_COMMIT}:{DIFF}"])
        self.assertEqual(digest(pre_recovery_report), DIFF_PRE_RECOVERY_SHA256)
        self.assertEqual(digest(current_report), DIFF_CURRENT_SHA256)
        update = json.loads(original_record)
        refs = [ref for change in update["changes"] for ref in change["evidence"]
                if ref["path"] == DIFF]
        self.assertEqual(len(refs), 4)
        self.assertEqual({ref["sha256"] for ref in refs}, {DIFF_HISTORICAL_SHA256})
        documentary._evidence(ROOT, refs)
        for ref in refs:
            resolved = documentary._bound_file(ROOT, ref, allow_retained=True)
            self.assertNotEqual(resolved, ROOT / DIFF)
            self.assertEqual(digest(resolved.read_bytes()), DIFF_HISTORICAL_SHA256)
            self.assertEqual(resolved.read_bytes(), git_bytes(DIFF))
        self.assertEqual((ROOT / UPDATE).read_bytes(), original_record)
        self.assertEqual((ROOT / DIFF).read_bytes(), current_report)

    def test_documentary_and_semantic_discovery_include_selected_custody_artifacts(self):
        selected = set(retained.evidence_paths(ROOT, DIFF, DIFF_HISTORICAL_SHA256))
        self.assertEqual(len(selected), 3)
        self.assertIn(DIFF, selected)
        self.assertTrue(any(path.startswith(retained.STORE + "/manifests/") for path in selected))
        self.assertTrue(any(path.startswith(retained.STORE + "/sha256/") for path in selected))
        self.assertLessEqual(selected, set(documentary.evidence_paths(ROOT)))
        self.assertLessEqual(selected, set(semantic.evidence_paths(ROOT)))

    def test_publication_current_reports_preserve_original_git_inventory(self):
        expected = {
            logical: {"sha256": historical_sha, "bytes": len(git_bytes(logical))}
            for logical, historical_sha in (
                (DIFF, DIFF_HISTORICAL_SHA256), (COVERAGE, COVERAGE_HISTORICAL_SHA256))
        }
        result = publication.retained_historical_reports(ROOT, list(expected), expected)
        self.assertEqual(set(result), {DIFF, COVERAGE})
        for logical in (DIFF, COVERAGE):
            snapshot = ROOT / result[logical]["historical_snapshot_path"]
            self.assertEqual(snapshot.read_bytes(), git_bytes(logical))
            self.assertEqual(result[logical]["sha256"], expected[logical]["sha256"])
            self.assertEqual(result[logical]["live_sha256"], digest((ROOT / logical).read_bytes()))

    def test_whole_suite_inputs_bind_retained_and_nested_decision_dependencies(self):
        import current_decision_applicability as applicability
        import current_publication_readiness as readiness
        inputs = readiness.validation_inputs(ROOT)
        self.assertLessEqual(set(retained.store_paths(ROOT)), inputs)
        self.assertLessEqual(set(applicability.evidence_paths(ROOT)), inputs)
        records = json.loads((ROOT / "mappings/current-ssn-sosa-assessment.json").read_text())["records"]
        for record in records:
            if not record.get("human_decision_record"):
                continue
            decision = documentary._json(documentary._bound_file(ROOT, record["human_decision_record"]))
            for key in ("assessment_snapshot", "review_packet_snapshot", "inheritance_sufficiency_evidence"):
                if decision.get(key):
                    self.assertIn(decision[key]["path"], inputs)


if __name__ == "__main__":
    unittest.main()
