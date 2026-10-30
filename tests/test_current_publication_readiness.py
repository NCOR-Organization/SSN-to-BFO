import copy
import hashlib
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
    def setUp(self):
        custody = patch.object(readiness, "native_ledger_errors", return_value=[])
        custody.start()
        self.addCleanup(custody.stop)

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
            item = {**copy.deepcopy(record), "name": name,
                    "input_scope": {"schema_version": 2, "profile": readiness.scopes.PROFILE, "role": name}}
            executable = str(Path(sys.executable if expected[0] == "python" else shutil.which(expected[0])).resolve())
            item["command"] = [executable, *expected[1:]]
            item["tool_identity"] = {"path": executable, "sha256": readiness.fingerprint(Path(executable))["sha256"]}
            item.update({field: {} for field in (
                "expected_execution_tools", "execution_tools_before", "execution_tools_after",
                "expected_execution_environment", "execution_environment_before", "execution_environment_after")})
            commands.append(item)
        return {"input_scope_profile": readiness.scopes.PROFILE, "head": "candidate", "input_sha256": inputs,
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
                 patch.object(readiness.scopes, "execution_tools", return_value={}), \
                 patch.object(readiness.scopes, "execution_environment", return_value={}), \
                 patch.object(readiness.scopes, "ledger_inputs", return_value=good["input_sha256"]), \
                 patch.object(readiness.scopes, "role_inputs", return_value=good["input_sha256"]), \
                 patch.object(readiness.scopes, "scope_declaration", side_effect=lambda root, role:
                              {"schema_version": 2, "profile": readiness.scopes.PROFILE, "role": role}):
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

    def selection_fixture(self, root, ledger=None):
        # These records exercise evidence selection, not semantic approval.
        payloads = {
            "reports/current-ssn-sosa-semantic-validation.json": b'{"historical": "semantic"}\n',
            "reports/current-publication-validation/commands.json": b'{"historical": "commands"}\n',
            "reports/current-publication-validation/successor/semantic.json":
                b'{"execution_evidence_schema": 2, "status": "FAIL"}\n',
            "reports/current-publication-validation/successor/commands.json":
                (json.dumps(ledger if ledger is not None else {"commands": []}) + "\n").encode(),
        }
        for relative, payload in payloads.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)

        def reference(relative):
            return {"path": relative, "sha256": hashlib.sha256(payloads[relative]).hexdigest()}

        document = {
            "schema_version": 1,
            "semantic": reference("reports/current-publication-validation/successor/semantic.json"),
            "validation": reference("reports/current-publication-validation/successor/commands.json"),
            "predecessors": {
                "semantic": reference("reports/current-ssn-sosa-semantic-validation.json"),
                "validation": reference("reports/current-publication-validation/commands.json"),
            },
        }
        self.write_selector(root, document)
        return document, payloads

    def write_selector(self, root, document):
        path = root / readiness.CURRENT_EVIDENCE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document) + "\n")

    def test_no_selector_keeps_original_evidence_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            semantic, validation, metadata = readiness.selected_evidence(root)
            self.assertEqual(semantic, root / "reports/current-ssn-sosa-semantic-validation.json")
            self.assertEqual(validation, root / "reports/current-publication-validation/commands.json")
            self.assertEqual(metadata, {"selector": None, "mode": "original_records"})
            self.assertEqual(list(root.iterdir()), [])

    def test_successor_selection_preserves_all_evidence_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document, original_bytes = self.selection_fixture(root)
            selector = root / readiness.CURRENT_EVIDENCE
            selector_bytes = selector.read_bytes()
            semantic, validation, metadata = readiness.selected_evidence(root)
            self.assertEqual(semantic, root / document["semantic"]["path"])
            self.assertEqual(validation, root / document["validation"]["path"])
            self.assertEqual(metadata["mode"], "successor_records")
            self.assertEqual(metadata["predecessors"], document["predecessors"])
            self.assertEqual(metadata["selector"], {
                "path": readiness.CURRENT_EVIDENCE.as_posix(),
                "sha256": hashlib.sha256(selector_bytes).hexdigest(),
            })
            self.assertEqual(selector.read_bytes(), selector_bytes)
            for relative, payload in original_bytes.items():
                self.assertEqual((root / relative).read_bytes(), payload, relative)

    def test_present_malformed_selector_never_falls_back_to_originals(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good, _ = self.selection_fixture(root)
            attacks = {
                "unknown version": lambda d: d.update(schema_version=2),
                "boolean version": lambda d: d.update(schema_version=True),
                "unknown field": lambda d: d.update(allow_stale=True),
                "missing successor": lambda d: d.pop("semantic"),
                "missing predecessor": lambda d: d["predecessors"].pop("validation"),
                "unknown predecessor": lambda d: d["predecessors"].update(other=d["semantic"]),
                "unknown reference field": lambda d: d["semantic"].update(approved=True),
                "missing reference hash": lambda d: d["validation"].pop("sha256"),
                "nonstring hash": lambda d: d["semantic"].update(sha256=1),
                "nonobject predecessor": lambda d: d.update(predecessors=[]),
            }
            for label, mutate in attacks.items():
                with self.subTest(attack=label):
                    bad = copy.deepcopy(good)
                    mutate(bad)
                    self.write_selector(root, bad)
                    with self.assertRaises(ValueError):
                        readiness.selected_evidence(root)
            for invalid in ("not JSON", "[]", "null"):
                with self.subTest(document=invalid):
                    (root / readiness.CURRENT_EVIDENCE).write_text(invalid)
                    with self.assertRaises(ValueError):
                        readiness.selected_evidence(root)

    def test_missing_or_changed_successor_and_predecessor_are_rejected(self):
        for role in ("semantic", "validation"):
            for historical in (False, True):
                for mutation in ("missing", "changed"):
                    with self.subTest(role=role, historical=historical, mutation=mutation), \
                         tempfile.TemporaryDirectory() as temporary:
                        root = Path(temporary)
                        document, _ = self.selection_fixture(root)
                        reference = document["predecessors"][role] if historical else document[role]
                        path = root / reference["path"]
                        if mutation == "missing":
                            path.unlink()
                        else:
                            path.write_bytes(path.read_bytes() + b" ")
                        with self.assertRaises(ValueError):
                            readiness.selected_evidence(root)

    def test_selector_rejects_escape_alias_and_historical_substitution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good, _ = self.selection_fixture(root)
            relative = good["semantic"]["path"]
            attacks = {
                "absolute path": lambda d: d["semantic"].update(path=str(root / relative)),
                "parent traversal": lambda d: d["semantic"].update(
                    path="reports/current-publication-validation/../current-publication-validation/successor/semantic.json"),
                "dot alias": lambda d: d["semantic"].update(
                    path="reports/current-publication-validation/./successor/semantic.json"),
                "outside evidence directory": lambda d: d.update(semantic=copy.deepcopy(d["predecessors"]["semantic"])),
                "wrong predecessor identity": lambda d: d["predecessors"].update(semantic=copy.deepcopy(d["semantic"])),
                "historical command substitution": lambda d: d.update(validation=copy.deepcopy(d["predecessors"]["validation"])),
                "same successor for both roles": lambda d: d.update(validation=copy.deepcopy(d["semantic"])),
            }
            for label, mutate in attacks.items():
                with self.subTest(attack=label):
                    bad = copy.deepcopy(good)
                    mutate(bad)
                    self.write_selector(root, bad)
                    with self.assertRaises(ValueError):
                        readiness.selected_evidence(root)

    def test_selector_rejects_symlinked_selector_records_and_parent(self):
        cases = ("selector", "semantic successor", "validation successor",
                 "semantic predecessor", "validation predecessor", "successor directory")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                document, _ = self.selection_fixture(root)
                if case == "selector":
                    path = root / readiness.CURRENT_EVIDENCE
                elif case == "successor directory":
                    path = (root / document["semantic"]["path"]).parent
                else:
                    role, kind = case.split()
                    path = root / (document["predecessors"][role] if kind == "predecessor" else document[role])["path"]
                target = path.with_name(path.name + ".retained")
                path.rename(target)
                path.symlink_to(target, target_is_directory=target.is_dir())
                with self.assertRaises(ValueError):
                    readiness.selected_evidence(root)

    def test_selected_successor_does_not_waive_stale_command_bindings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = self.command_fixture(root)
            ledger["commands"][0]["input_sha256"]["tool.py"] = "pre-transition"
            self.selection_fixture(root, ledger)
            _, selected, _ = readiness.selected_evidence(root)
            with patch.object(readiness, "ROOT", root), patch.object(readiness, "git", return_value="candidate"), \
                 patch.object(readiness.scopes, "execution_tools", return_value={}), \
                 patch.object(readiness.scopes, "execution_environment", return_value={}), \
                 patch.object(readiness.scopes, "ledger_inputs", return_value=ledger["input_sha256"]), \
                 patch.object(readiness.scopes, "role_inputs", return_value=ledger["input_sha256"]), \
                 patch.object(readiness.scopes, "scope_declaration", side_effect=lambda root, role:
                              {"schema_version": 2, "profile": readiness.scopes.PROFILE, "role": role}):
                errors = readiness.validation_errors(readiness.read(selected))
            self.assertTrue(any("Command unit_tests" in error and "stale command inputs" in error
                                for error in errors), errors)

    def test_selected_partial_ledger_keeps_full_validation_outstanding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = self.command_fixture(root)
            ledger["commands"] = [command for command in ledger["commands"]
                                  if command["name"] not in {"unit_tests", "full_repository_gate"}]
            self.selection_fixture(root, ledger)
            _, selected, _ = readiness.selected_evidence(root)
            with patch.object(readiness, "ROOT", root), patch.object(readiness, "git", return_value="candidate"), \
                 patch.object(readiness.scopes, "execution_tools", return_value={}), \
                 patch.object(readiness.scopes, "execution_environment", return_value={}), \
                 patch.object(readiness.scopes, "ledger_inputs", return_value=ledger["input_sha256"]), \
                 patch.object(readiness.scopes, "role_inputs", return_value=ledger["input_sha256"]), \
                 patch.object(readiness.scopes, "scope_declaration", side_effect=lambda root, role:
                              {"schema_version": 2, "profile": readiness.scopes.PROFILE, "role": role}):
                errors = readiness.validation_errors(readiness.read(selected))
            self.assertCountEqual(errors, ["Required validation not run: unit_tests",
                                           "Required validation not run: full_repository_gate"])

    def test_selected_semantic_record_still_requires_current_execution_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document, _ = self.selection_fixture(root)
            legacy = b'{"schema_version": 1, "status": "PASS"}\n'
            (root / document["semantic"]["path"]).write_bytes(legacy)
            document["semantic"]["sha256"] = hashlib.sha256(legacy).hexdigest()
            self.write_selector(root, document)
            selected, _, _ = readiness.selected_evidence(root)
            self.assertTrue(readiness.semantic.current_schema_errors(readiness.read(selected)))


if __name__ == "__main__":
    unittest.main()
