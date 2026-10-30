"""Reachable v2 custody and successor reports; mutations use disposable copies."""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as assessment
import current_custody_dependencies as custody
import current_documentary_workbook as documentary
import current_retained_evidence as retained
import current_semantic_workbook as semantic


class CurrentCustodyDependenciesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual_paths = custody.assessment_paths(ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in self.actual_paths:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, path)

    def write(self, relative: str, data: bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_unreferenced_retention_and_successor_outputs_do_not_change_generation_scope(self):
        before = custody.assessment_paths(self.root)
        unrelated = self.write(retained.STORE + "/execution/sha256/" + "a" * 64, b"unselected RDF")
        manifest = self.write(retained.STORE + "/execution/manifests/unselected.json", b"not a selected manifest")
        for name in assessment.REPORT_NAMES:
            self.write((assessment.REPORT_DIRECTORY / name).as_posix(), b"subsequent output")
        self.assertEqual(custody.assessment_paths(self.root), before)
        unrelated.write_bytes(b"changed unreferenced bytes")
        manifest.unlink()
        self.assertEqual(custody.assessment_paths(self.root), before)
        self.assertFalse(any(path.startswith(retained.STORE + "/execution/") for path in before))

    def test_imported_implementation_changes_assessment_input_binding(self):
        before = {path: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
                  for path in custody.assessment_paths(self.root)}
        for relative in ("tools/generate_mapping_from_coms.py", "tools/publication_metadata.py",
                         "tools/coms_row_identity.py", "tools/current_semantic_generation.py"):
            self.assertIn(relative, before)
        helper = "tools/coms_row_identity.py"
        path = self.root / helper
        path.write_bytes(path.read_bytes() + b"\n# Isolated implementation change.\n")
        after = {name: hashlib.sha256((self.root / name).read_bytes()).hexdigest()
                 for name in custody.assessment_paths(self.root)}
        self.assertEqual(set(before), set(after))
        self.assertEqual([name for name in before if before[name] != after[name]], [helper])

    def test_selected_historical_snapshot_and_manifest_are_required_and_authenticated(self):
        paths = custody.authority_paths(self.root)
        manifests = [p for p in paths if p.startswith(retained.STORE + "/manifests/")]
        self.assertEqual(len(manifests), 1)
        manifest = self.root / manifests[0]
        document = json.loads(manifest.read_bytes())
        snapshot = self.root / document["snapshot_path"]
        self.assertIn(document["snapshot_path"], paths)
        self.assertEqual(hashlib.sha256(snapshot.read_bytes()).hexdigest(), document["sha256"])
        for target in (manifest, snapshot):
            original = target.read_bytes()
            for mode in ("missing", "corrupt"):
                with self.subTest(path=target.name, mode=mode):
                    if mode == "missing":
                        target.unlink()
                    else:
                        target.write_bytes(b"corruption")
                    try:
                        with self.assertRaises((ValueError, OSError)):
                            custody.authority_paths(self.root)
                    finally:
                        target.write_bytes(original)

    def test_missing_live_historical_report_uses_exact_snapshot_without_rebinding(self):
        logical = "reports/coms-vs-pre-coms-legacy-diff.md"
        self.write(logical, (ROOT / logical).read_bytes())
        before = custody.authority_paths(self.root)
        (self.root / logical).unlink()
        after = custody.authority_paths(self.root)
        self.assertEqual(after, before)
        self.assertNotIn(logical, after)
        self.assertTrue(any(p.endswith("/coms-vs-pre-coms-legacy-diff.md") for p in after))

    def test_live_workbook_and_cited_evidence_cannot_silently_disappear(self):
        for relative in (documentary.WORKBOOK, "mappings/SOSA-next-to-RO-COMS.xlsx"):
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaises((ValueError, OSError)):
                        custody.assessment_paths(self.root)
                finally:
                    path.write_bytes(original)

    def test_immutable_human_decision_and_nested_packet_corruption_fail(self):
        document = json.loads((self.root / custody.ASSESSMENT).read_bytes())
        record = next(r for r in document["records"] if r.get("human_decision_record"))
        decision_path = self.root / record["human_decision_record"]["path"]
        decision = json.loads(decision_path.read_bytes())
        for path in (decision_path, self.root / decision["review_packet_snapshot"]["path"]):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                try:
                    with self.assertRaises(ValueError):
                        custody.authority_paths(self.root)
                finally:
                    path.write_bytes(original)

    def test_new_history_or_applicability_members_are_not_ignored(self):
        for relative, data in (
                (semantic.TRANSITIONS + "/unexpected.txt", b"unsupported archive entry"),
                ("reports/current-decision-applicability/prepared/unregistered.json", b"{}")):
            with self.subTest(path=relative):
                path = self.write(relative, data)
                try:
                    with self.assertRaises(ValueError):
                        custody.authority_paths(self.root)
                finally:
                    path.unlink()

    def test_required_evidence_symlink_is_not_a_portable_alias(self):
        relative = "mappings/SOSA-next-to-RO-COMS.xlsx"
        path = self.root / relative
        path.unlink()
        path.symlink_to(ROOT / relative)
        with self.assertRaises(ValueError):
            custody.assessment_paths(self.root)

    def test_publication_scope_includes_actual_preservation_history(self):
        paths = custody.authority_paths(ROOT, publication=True)
        self.assertIn("reports/current-publication-baseline.json", paths)
        for name in ("coms-source-term-coverage.md", "coms-vs-pre-coms-legacy-diff.md"):
            self.assertIn("reports/" + name, paths)
            self.assertTrue(any(path.startswith(retained.STORE + "/sha256/")
                                and path.endswith("/" + name) for path in paths))
        self.assertFalse(any(path.startswith(retained.STORE + "/execution/") for path in paths))

    def command(self, *argv):
        # Routing is isolated from expensive report computation. Authority
        # authentication above uses real repository-derived history, not mocks.
        with ExitStack() as stack:
            stack.enter_context(patch.object(assessment, "ROOT", self.root))
            stack.enter_context(patch.object(assessment, "SCOPE", self.root / "config/current-ssn-sosa-scope.json"))
            stack.enter_context(patch.object(assessment, "ASSESSMENT", self.root / custody.ASSESSMENT))
            stack.enter_context(patch.object(sys, "argv", ["current_assessment.py", *argv]))
            stack.enter_context(patch.object(assessment, "build_reports", return_value=(
                {"summary": {}, "binding": {"input_scope": custody.assessment_scope(self.root)}},
                {"summary": {}}, {"item_count": 0}, {})))
            for name in ("render_coverage", "render_rationales", "render_reviews"):
                stack.enter_context(patch.object(assessment, name, return_value="successor report\n"))
            stack.enter_context(patch("sys.stdout", new_callable=io.StringIO))
            return assessment.main()

    def test_write_uses_v2_successor_and_preserves_every_legacy_report(self):
        legacy = {name: self.write("reports/" + name, b"immutable legacy bytes\n")
                  for name in assessment.REPORT_NAMES}
        self.assertEqual(self.command("--write"), 0)
        for name, path in legacy.items():
            self.assertEqual(path.read_bytes(), b"immutable legacy bytes\n")
            self.assertTrue((self.root / assessment.REPORT_DIRECTORY / name).is_file())
        report = json.loads((self.root / assessment.REPORT_DIRECTORY / "current-ssn-sosa-coverage.json").read_bytes())
        self.assertEqual(report["binding"]["input_scope"]["schema_version"], 2)
        self.assertEqual(report["binding"]["input_scope"]["profile"], custody.ASSESSMENT_SCOPE_PROFILE)
        self.assertEqual(self.command(), 0)

    def test_legacy_reports_cannot_satisfy_default_v2_freshness(self):
        for name in assessment.REPORT_NAMES:
            self.write("reports/" + name, b"legacy report\n")
        self.assertEqual(self.command(), 1)


if __name__ == "__main__":
    unittest.main()
