"""Content-bound assessment reports survive commits but reject input drift."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as assessment


class CurrentAssessmentFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = {
            "inputs/assessment.json": b'{"review_state":"unreviewed"}\n',
            "inputs/source.ttl": b'<urn:source> <urn:predicate> <urn:target> .\n',
            "inputs/workbook.xlsx": b"fixture workbook bytes\n",
            "inputs/decision.json": b'{"reviewer_identity":"fixture"}\n',
            "tools/current_assessment.py": Path(assessment.__file__).read_bytes(),
            assessment.custody.POLICY_PATH: (ROOT / assessment.custody.POLICY_PATH).read_bytes(),
        }
        for relative, content in self.inputs.items():
            self.write(relative, content)
        # This narrow fixture selects a bounded custody inventory. Its scope
        # descriptor, hashing, rendering and freshness validation are real; the
        # separate custody/decision suites exercise full authority resolution.
        self.paths = patch.object(assessment.custody, "assessment_paths", return_value=set(self.inputs))
        self.paths.start()
        self.addCleanup(self.paths.stop)
        self.output = self.root / "reports" / "assessment.json"
        self.output.parent.mkdir()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def expected(self):
        return {self.output.name: assessment.json_text({
            "binding": assessment.report_binding(self.root),
            "result": "unchanged fixture assessment",
        })}

    def retain(self):
        expected = self.expected()
        self.output.write_text(expected[self.output.name])
        return expected

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True).strip()

    def test_committing_report_and_subsequent_commit_do_not_stale_binding(self):
        self.git("init", "-q")
        self.git("config", "user.name", "Assessment fixture")
        self.git("config", "user.email", "assessment-fixture@example.invalid")
        self.git("add", "--", *sorted(self.inputs))
        self.git("commit", "-q", "-m", "Fixture inputs")
        first_head = self.git("rev-parse", "HEAD")
        expected = self.retain()
        self.git("add", "--", "reports/assessment.json")
        self.git("commit", "-q", "-m", "Retain generated fixture report")
        report_head = self.git("rev-parse", "HEAD")
        self.assertNotEqual(first_head, report_head)
        self.assertEqual(self.expected(), expected)
        assessment.check_report_outputs(self.expected(), self.output.parent)
        self.write("unrelated.txt", b"unrelated subsequent change\n")
        self.git("add", "--", "unrelated.txt")
        self.git("commit", "-q", "-m", "Unrelated subsequent commit")
        self.assertNotEqual(report_head, self.git("rev-parse", "HEAD"))
        self.assertEqual(self.expected(), expected)
        assessment.check_report_outputs(self.expected(), self.output.parent)
        self.git("checkout", "-q", "--detach", "HEAD")
        self.assertEqual(self.expected(), expected)
        assessment.check_report_outputs(self.expected(), self.output.parent)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_content_digest_is_canonical_and_has_no_head(self):
        binding = assessment.report_binding(self.root)
        self.assertEqual(binding["profile"], assessment.REPORT_BINDING_PROFILE)
        self.assertNotIn("head", binding)
        content = {key: value for key, value in binding.items() if key != "content_sha256"}
        self.assertEqual(binding["content_sha256"], assessment.canonical_sha(content))
        self.assertEqual(set(binding["input_sha256"]), set(self.inputs))

    def test_assessment_source_workbook_decision_and_policy_drift_stale_reports(self):
        expected = self.retain()
        for relative, original in self.inputs.items():
            with self.subTest(path=relative):
                self.write(relative, original + b"changed bytes\n")
                try:
                    self.assertNotEqual(self.expected(), expected)
                    with self.assertRaisesRegex(ValueError, "stale assessment reports"):
                        assessment.check_report_outputs(self.expected(), self.output.parent)
                finally:
                    self.write(relative, original)
        assessment.check_report_outputs(self.expected(), self.output.parent)

    def test_report_tampering_and_legacy_head_binding_fail(self):
        expected = self.retain()
        original = json.loads(expected[self.output.name])
        for kind in ("output", "digest", "legacy_head"):
            tampered = json.loads(json.dumps(original))
            if kind == "output":
                tampered["result"] = "altered assessment"
            elif kind == "digest":
                tampered["binding"]["content_sha256"] = "0" * 64
            else:
                tampered["binding"].pop("content_sha256")
                tampered["binding"].pop("profile")
                tampered["binding"]["head"] = "1" * 40
            self.output.write_text(assessment.json_text(tampered))
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "stale assessment reports"):
                assessment.check_report_outputs(expected, self.output.parent)

    def test_custody_authentication_failure_is_not_replaced_by_content_hashing(self):
        with patch.object(assessment.custody, "assessment_paths", side_effect=ValueError("invalid decision custody")):
            with self.assertRaisesRegex(ValueError, "invalid decision custody"):
                assessment.report_binding(self.root)

    def test_invalid_final_assessment_fails_before_binding_or_reports(self):
        with patch.object(assessment, "source_graph", return_value=Graph()), \
                patch.object(assessment, "processed_rows", return_value=[]), \
                patch.object(assessment, "validate", side_effect=ValueError("missing human decision record")), \
                patch.object(assessment, "report_binding") as binding:
            with self.assertRaisesRegex(ValueError, "missing human decision record"):
                assessment.build_reports({}, {"records": []})
            binding.assert_not_called()


if __name__ == "__main__":
    unittest.main()
