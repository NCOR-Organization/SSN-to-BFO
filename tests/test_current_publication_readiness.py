import copy
import json
import shutil
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_publication_readiness as readiness


class PublicationEvidenceTests(unittest.TestCase):
    def test_documentary_custody_evidence_is_part_of_validation_inputs(self):
        baseline = json.loads((readiness.ROOT / readiness.documentary.BASELINE).read_text())
        expected = {readiness.documentary.BASELINE, baseline["historical_workbook"]["path"],
                    *(ref["path"] for ref in baseline["immutable_evidence"])}
        self.assertTrue(expected <= readiness.validation_inputs())
        # Newly registered transition evidence must enter whole-suite custody,
        # not only the assessment report's local input binding.
        with patch.object(readiness.documentary, "evidence_paths", return_value=[
                "reports/current-documentary-workbook/updates/fixture.json"]):
            self.assertIn("reports/current-documentary-workbook/updates/fixture.json",
                          readiness.validation_inputs())

    def command_fixture(self, root):
        # Construct execution evidence independently of any ledger builder.
        (root / "tool.py").write_text("print('PASS')\n")
        (root / "log").write_text("PASS\n")
        inputs = {"tool.py": readiness.fingerprint(root / "tool.py")["sha256"]}
        log_hash = readiness.fingerprint(root / "log")["sha256"]
        executable = str(Path(sys.executable).resolve())
        record = {"name": "assessment", "head": "candidate", "expected_head": "candidate",
                  "final_head": "candidate", "command": [executable, "tool.py"],
                  "tool_identity": {"path": executable, "sha256": readiness.fingerprint(Path(executable))["sha256"]},
                  "expected_input_sha256": inputs.copy(), "input_sha256": inputs.copy(),
                  "input_sha256_after": inputs.copy(), "input_drift": [],
                  "execution_status": "completed", "returncode": 0,
                  "started_at_utc": "2026-10-10T00:00:00Z", "completed_at_utc": "2026-10-10T00:00:01Z",
                  "log": "log", "log_sha256": log_hash, "result_artifacts": {"log": log_hash}}
        commands = []
        for name, expected in readiness.REQUIRED_COMMANDS.items():
            item = {**copy.deepcopy(record), "name": name}
            executable = str(Path(sys.executable if expected[0] == "python" else shutil.which(expected[0])).resolve())
            item["command"] = [executable, *expected[1:]]
            item["tool_identity"] = {"path": executable, "sha256": readiness.fingerprint(Path(executable))["sha256"]}
            commands.append(item)
        return {"head": "candidate", "input_sha256": inputs,
                "commands": commands}

    def test_current_outer_ledger_cannot_launder_stale_command_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good = self.command_fixture(root)
            attacks = {
                "old command HEAD": lambda c: c.update(head="old"),
                "missing command HEAD": lambda c: c.pop("head"),
                "old command inputs": lambda c: c["input_sha256"].update({"tool.py": "old"}),
                "old expected inputs": lambda c: c["expected_input_sha256"].update({"tool.py": "old"}),
                "recorded drift": lambda c: c.update(input_drift=["tool.py"]),
                "numeric drift": lambda c: c.update(input_drift=1),
                "missing command binding": lambda c: c.pop("input_sha256"),
                "missing post snapshot": lambda c: c.pop("input_sha256_after"),
                "post snapshot drift": lambda c: c["input_sha256_after"].update({"tool.py": "old"}),
                "missing completion": lambda c: c.pop("execution_status"),
                "missing tool identity": lambda c: c.pop("tool_identity"),
                "wrong named command": lambda c: c.update(command=[str(Path(sys.executable).resolve()), "-c", "print('PASS')"]),
                "missing result": lambda c: c.update(result_artifacts={"absent": "old"}),
            }
            with patch.object(readiness, "ROOT", root), patch.object(readiness, "git", return_value="candidate"), \
                 patch.object(readiness, "validation_inputs", return_value={"tool.py"}):
                self.assertEqual(readiness.validation_errors(good), [])
                for attack, mutate in attacks.items():
                    with self.subTest(attack=attack):
                        bad = copy.deepcopy(good)
                        mutate(bad["commands"][0])
                        errors = readiness.validation_errors(bad)
                        self.assertTrue(errors, attack)
                        self.assertTrue(any("Command unit_tests" in e for e in errors), errors)

    def test_examples_require_both_phases_and_separate_fixture(self):
        row = {"classification": "aligned consistent", "source": {"status": "consistent"}, "aligned": {"status": "consistent"}}
        self.assertFalse(readiness.examples_pass({"examples": [row]}))
        self.assertTrue(readiness.examples_pass({"examples": [row], "synthetic_fixture": row}))
        broken = {**row, "aligned": {"status": "technical_failure"}}
        self.assertFalse(readiness.examples_pass({"examples": [row], "synthetic_fixture": broken}))
        self.assertFalse(readiness.examples_pass({"examples": [broken], "synthetic_fixture": row}))

    def test_generation_reports_are_required_execution_inputs(self):
        paths = readiness.validation_inputs(readiness.ROOT)
        self.assertIn("reports/coms-generation-validation.md", paths)
        self.assertIn("reports/coms-product-dispositions.json", paths)

    def test_absent_validation_is_not_pass(self):
        errors = readiness.validation_errors({})
        self.assertTrue(any("not run: full_repository_gate" in e for e in errors))
        self.assertTrue(any("HEAD" in e for e in errors))
        self.assertTrue(any("bindings" in e for e in errors))

    def test_expectations_require_both_polarities_and_actual_answers(self):
        self.assertFalse(readiness.expectations_pass({"expectations": {"approved_count": 1}}, {"expectations": []}))
        approved = [{"id": "positive", "expected_entailed": True, "review_state": "approved", "approval_evidence": "synthetic test"},
                    {"id": "negative", "expected_entailed": False, "review_state": "approved", "approval_evidence": "synthetic test"}]
        for item in approved:
            item.update(evidence_role="independent_semantic_expectation", entailment_origin="mapping_induced")
        report = {"expectations": {"approved_count": 2, "approved_results": []}}
        self.assertFalse(readiness.expectations_pass(report, {"expectations": approved}))
        report["expectations"]["approved_results"] = [
            {"status": "consistent", "reasoner_result": {"expectations": [{"id": item["id"], "passed": True, "entailed": item["expected_entailed"]}]}}
            for item in approved]
        self.assertTrue(readiness.expectations_pass(report, {"expectations": approved}))
        restatements = copy.deepcopy(approved)
        for item in restatements:
            item["evidence_role"] = "mapping_axiom_regression"
        self.assertFalse(readiness.expectations_pass(report, {"expectations": restatements}))
        report["expectations"]["approved_results"][1]["reasoner_result"]["expectations"][0]["entailed"] = True
        self.assertFalse(readiness.expectations_pass(report, {"expectations": approved}))

    def test_stale_input_and_tampered_log_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tool.py").write_text("changed")
            (root / "log").write_text("changed")
            document = {"head": "head", "input_sha256": {"tool.py": "old"},
                        "commands": [{"name": "full_repository_gate", "log": "log", "log_sha256": "old", "returncode": 0}]}
            with patch.object(readiness, "ROOT", root), patch.object(readiness, "git", return_value="head"):
                errors = readiness.validation_errors(document)
            self.assertTrue(any("input changed" in e for e in errors))
            self.assertTrue(any("output changed" in e for e in errors))

    def test_nonzero_gate_cannot_be_hidden_by_present_log(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "log").write_text("FAIL")
            document = {"head": "head", "commands": [{"name": "full_repository_gate", "log": "log", "log_sha256": readiness.fingerprint(root / "log")["sha256"], "returncode": 1}]}
            with patch.object(readiness, "ROOT", root), patch.object(readiness, "git", return_value="head"):
                self.assertTrue(any("Validation failed: full_repository_gate" in e for e in readiness.validation_errors(document)))


if __name__ == "__main__":
    unittest.main()
