"""Native receipts use real short children; no repository gate runs here."""
from __future__ import annotations

import copy
import hashlib
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
import current_validation_execution as execution
import current_validation_scope as scopes


class NativeExecutionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="current-native-execution-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.directory = execution.PARENT / "v2-fixture"
        for relative in (execution.RECORDER, execution.RECORDER_TESTS):
            self.write(relative, (ROOT / relative).read_bytes())
        self.write("input.txt", b"fixed execution input\n")
        self.authorization = self.write("request.txt", b"Execute the isolated native receipt fixture.\n")
        self.write("config/validation-toolchain.env", b"VALIDATION_PYTHON_VERSION=3.12\nVALIDATION_JAVA_VERSION=22\nVALIDATION_JAVA_DISTRIBUTION=temurin\n")
        self.history = self.write("reports/historical/STOP.json", b'{"outcome":"FAIL","immutable":true}\n')
        self.history_bytes = self.history.read_bytes()
        self.roles = list(scopes.REQUIRED_COMMANDS)
        commands = {role: ["python", "-B", "-c", "print('actual fixture " + role + "')"] for role in self.roles}
        self.start(patch.dict(scopes.REQUIRED_COMMANDS, commands, clear=True))
        self.start(patch.object(execution, "head", return_value="a" * 40))
        self.start(patch.object(scopes, "scope_declaration", side_effect=lambda root, role: {
            "schema_version": 2, "profile": scopes.PROFILE, "role": role, "fixture_contract": "isolated-real-child"}))
        self.start(patch.object(scopes, "role_inputs", side_effect=lambda root, role: self.inputs(root)))
        self.start(patch.object(scopes, "ledger_inputs", side_effect=lambda root: self.inputs(root)))
        self.start(patch.object(scopes, "execution_tools", side_effect=lambda root, role: self.tools()))
        self.start(patch.object(execution, "_version_commands", return_value={
            "python": [sys.executable, "-B", "-c", "print('Python 3.13.0')"],
            "java": [sys.executable, "-B", "-c", "print('openjdk version \\\"22.0.1\\\"')"],
        }))

    def start(self, context):
        result = context.start()
        self.addCleanup(context.stop)
        return result

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def inputs(self, root):
        return {"input.txt": hashlib.sha256((Path(root) / "input.txt").read_bytes()).hexdigest()}

    def tools(self):
        path = Path(sys.executable).resolve()
        data = path.read_bytes()
        return {"python": {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}}

    def prepare(self):
        return execution.prepare_run(self.root, self.directory, self.authorization)

    def path(self, name):
        return self.root / self.directory / name

    def command(self, code):
        scopes.REQUIRED_COMMANDS[self.roles[0]] = ["python", "-B", "-c", code]

    def finish(self):
        for role in self.roles:
            execution.run_role(self.root, self.directory, role)
        return execution.finalize_ledger(self.root, self.directory)

    def test_actual_children_produce_eight_authenticated_receipts_and_ledger(self):
        manifest = self.prepare()
        before = self.inputs(self.root)
        ledger = self.finish()
        self.assertEqual(len(ledger["commands"]), 8)
        self.assertEqual(execution.ledger_custody_errors(ledger, self.root), [])
        for command in ledger["commands"]:
            self.assertEqual(command["execution_status"], "completed")
            self.assertEqual(command["returncode"], 0)
            self.assertEqual(command["input_drift"], [])
            self.assertIn("actual fixture " + command["name"], (self.root / command["log"]).read_text())
            ticket = json.loads(execution.bound(self.root, command["ticket"]).read_bytes())
            self.assertLessEqual(ticket["issued_at_utc"], command["started_at_utc"])
            self.assertEqual(ticket["expected"], manifest["expectations"][command["name"]])
        self.assertEqual(before, self.inputs(self.root))
        self.assertEqual(self.history.read_bytes(), self.history_bytes)

    def test_real_measurements_preserve_environment_mismatch_without_inventing_qualification(self):
        manifest = self.prepare()
        environment = manifest["environment"]
        self.assertEqual(environment["measured"]["python_major_minor"], "3.13")
        self.assertIs(environment["declared_environment_match"], False)
        self.assertIn("Python 3.13.0", self.path("environment-python.log").read_text())
        ledger = self.finish()
        self.assertIs(ledger["declared_environment_match"], False)
        forged = copy.deepcopy(ledger)
        forged["declared_environment_match"] = True
        self.assertTrue(execution.ledger_custody_errors(forged, self.root))

    def test_completed_nonzero_is_preserved_and_stops_every_later_role(self):
        self.command("print('real validation failure'); raise SystemExit(7)")
        self.prepare()
        receipt = execution.run_role(self.root, self.directory, self.roles[0])
        self.assertEqual(receipt["returncode"], 7)
        self.assertEqual(receipt["execution_status"], "completed")
        self.assertEqual(execution.authenticate_receipt(self.root, self.directory, self.roles[0], require_success=False), receipt)
        self.assertTrue(self.path("STOP.json").is_file())
        with self.assertRaisesRegex(ValueError, "stopped"):
            execution.run_role(self.root, self.directory, self.roles[1])
        with self.assertRaisesRegex(ValueError, "stopped"):
            execution.finalize_ledger(self.root, self.directory)
        self.assertFalse(self.path(self.roles[1] + ".ticket.json").exists())

    def test_signal_terminated_child_cannot_masquerade_as_completed_fail(self):
        self.command("import os,signal; os.kill(os.getpid(),signal.SIGTERM)")
        self.prepare()
        receipt = execution.run_role(self.root, self.directory, self.roles[0])
        self.assertLess(receipt["returncode"], 0)
        self.assertEqual(receipt["execution_status"], "signal_terminated")
        with self.assertRaisesRegex(ValueError, "interrupted|incomplete|signaled"):
            execution.authenticate_receipt(self.root, self.directory, self.roles[0], require_success=False)
        self.assertTrue(self.path("STOP.json").is_file())

    def test_shell_signal_style_status_cannot_authenticate_as_completed_failure(self):
        self.command("raise SystemExit(143)")
        self.prepare()
        receipt = execution.run_role(self.root, self.directory, self.roles[0])
        self.assertEqual(receipt["returncode"], 143)
        self.assertEqual(receipt["execution_status"], "completed")
        with self.assertRaisesRegex(ValueError, "signaled"):
            execution.authenticate_receipt(self.root, self.directory, self.roles[0], require_success=False)
        self.assertTrue(self.path("STOP.json").is_file())

    def test_timeout_must_be_finite_and_positive_before_any_child_launches(self):
        self.prepare()
        for timeout in (0, -1, float("inf"), float("nan"), True, "1"):
            with self.subTest(timeout=timeout), self.assertRaisesRegex(ValueError, "finite and positive"):
                execution.run_role(self.root, self.directory, self.roles[0], timeout=timeout)
            self.assertFalse(self.path(self.roles[0] + ".ticket.json").exists())

    def test_timeout_preserves_raw_termination_and_incomplete_status(self):
        self.command("import time; print('started',flush=True); time.sleep(30)")
        self.prepare()
        receipt = execution.run_role(self.root, self.directory, self.roles[0], timeout=0.1)
        self.assertEqual(receipt["execution_status"], "timed_out")
        self.assertIn("started", self.path(self.roles[0] + ".log").read_text())
        with self.assertRaises(ValueError):
            execution.authenticate_receipt(self.root, self.directory, self.roles[0], require_success=False)

    def test_parent_interruption_terminates_real_owned_child_and_is_not_completed(self):
        self.command("import time; time.sleep(30)")
        self.prepare()
        original_popen = subprocess.Popen
        children = []
        def popen(*args, **kwargs):
            # Preserve the canonical constructor wrapper and instrument only
            # the real owned child, without assuming Popen is a class.
            child = original_popen(*args, **kwargs)
            children.append(child)
            original_wait = child.wait
            interrupted = False
            def wait(*args, **kwargs):
                nonlocal interrupted
                if not interrupted:
                    interrupted = True
                    raise KeyboardInterrupt()
                return original_wait(*args, **kwargs)
            def cleanup():
                if child.poll() is None:
                    child.kill()
                original_wait(timeout=5)
            self.addCleanup(cleanup)
            child.wait = wait
            return child
        with patch.object(subprocess, "Popen", popen):
            receipt = execution.run_role(self.root, self.directory, self.roles[0])
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll(), "Interrupted recorder left its owned child running")
        self.assertEqual(receipt["returncode"], children[0].returncode)
        self.assertEqual(receipt["execution_status"], "interrupted")
        with self.assertRaises(ValueError):
            execution.authenticate_receipt(self.root, self.directory, self.roles[0], require_success=False)

    def test_launch_error_is_captured_without_fabricating_an_exit_code(self):
        self.prepare()
        with patch.object(subprocess, "Popen", side_effect=FileNotFoundError("fixture launch failure")):
            receipt = execution.run_role(self.root, self.directory, self.roles[0])
        self.assertEqual(receipt["execution_status"], "launch_error")
        self.assertIsNone(receipt["returncode"])
        self.assertTrue(self.path("STOP.json").exists())
        with self.assertRaises(ValueError):
            execution.authenticate_receipt(self.root, self.directory, self.roles[0], require_success=False)

    def test_changed_input_before_launch_stops_without_a_false_execution_receipt(self):
        self.prepare()
        self.write("input.txt", b"new unvalidated input\n")
        with self.assertRaisesRegex(ValueError, "predeclared"):
            execution.run_role(self.root, self.directory, self.roles[0])
        self.assertTrue(self.path("STOP.json").exists())
        self.assertFalse(self.path(self.roles[0] + ".command.json").exists())

    def test_child_input_mutation_is_recorded_as_drift_even_with_exit_zero(self):
        self.command("from pathlib import Path; Path('input.txt').write_text('changed by actual child')")
        self.prepare()
        receipt = execution.run_role(self.root, self.directory, self.roles[0])
        self.assertEqual(receipt["returncode"], 0)
        self.assertTrue(receipt["input_drift"])
        self.assertNotEqual(receipt["input_sha256"], receipt["input_sha256_after"])
        self.assertTrue(self.path("STOP.json").exists())

    def test_forged_receipt_result_seal_and_log_are_rejected(self):
        self.prepare()
        role = self.roles[0]
        execution.run_role(self.root, self.directory, role)
        receipt_path = self.path(role + ".command.json")
        original = receipt_path.read_bytes()
        for field, value in (("returncode", 9), ("receipt_sha256", "0" * 64), ("command", [sys.executable, "-c", "print('different')"])):
            with self.subTest(field=field):
                document = json.loads(original)
                document[field] = value
                receipt_path.write_bytes(execution.canonical(document))
                with self.assertRaises(ValueError):
                    execution.authenticate_receipt(self.root, self.directory, role)
                receipt_path.write_bytes(original)
        self.path(role + ".log").write_bytes(b"forged successful output\n")
        with self.assertRaisesRegex(ValueError, "log differs"):
            execution.authenticate_receipt(self.root, self.directory, role)

    def test_wrong_ticket_role_predecessor_scope_and_capture_are_rejected(self):
        self.prepare()
        role = self.roles[0]
        execution.run_role(self.root, self.directory, role)
        path = self.path(role + ".ticket.json")
        original = path.read_bytes()
        for field, value in (("role", self.roles[1]), ("run_id", "unrelated"), ("expected", {}), ("cwd", "/wrong/root")):
            with self.subTest(field=field):
                ticket = json.loads(original)
                ticket[field] = value
                path.write_bytes(execution.canonical(ticket))
                with self.assertRaises(ValueError):
                    execution.authenticate_receipt(self.root, self.directory, role)
                path.write_bytes(original)
        capture = self.path(role + ".capture.json")
        document = json.loads(capture.read_bytes())
        document["execution_id"] = "another invocation"
        capture.write_bytes(execution.canonical(document))
        with self.assertRaises(ValueError):
            execution.authenticate_receipt(self.root, self.directory, role)

    def test_producer_and_authorization_bytes_cannot_change_after_preparation(self):
        self.prepare()
        for path in (self.root / execution.RECORDER_TESTS, self.path("authorization.txt")):
            with self.subTest(path=path):
                original = path.read_bytes()
                path.write_bytes(original + b"changed")
                with self.assertRaises(ValueError):
                    execution.run_role(self.root, self.directory, self.roles[0])
                path.write_bytes(original)

    def test_create_once_records_and_history_cannot_be_replaced(self):
        self.prepare()
        before = self.path("run.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.prepare()
        execution.run_role(self.root, self.directory, self.roles[0])
        with self.assertRaisesRegex(ValueError, "already attempted"):
            execution.run_role(self.root, self.directory, self.roles[0])
        self.assertEqual(self.path("run.json").read_bytes(), before)
        self.assertEqual(self.history.read_bytes(), self.history_bytes)

    def test_missing_duplicate_and_mixed_ledger_commands_fail_custody(self):
        self.prepare()
        ledger = self.finish()
        for mode in ("missing", "duplicate", "inline", "receipt_hash", "run_manifest"):
            with self.subTest(mode=mode):
                candidate = copy.deepcopy(ledger)
                if mode == "missing":candidate["commands"].pop()
                elif mode == "duplicate":candidate["commands"][1] = candidate["commands"][0]
                elif mode == "inline":candidate["commands"][0]["returncode"] = 3
                elif mode == "receipt_hash":candidate["receipt_artifacts"] = {}
                else:candidate["run_manifest"]["sha256"] = "0" * 64
                self.assertTrue(execution.ledger_custody_errors(candidate, self.root))

    def test_incomplete_run_cannot_issue_ledger_or_skip_required_execution_order(self):
        self.prepare()
        with self.assertRaises((ValueError, OSError)):
            execution.run_role(self.root, self.directory, self.roles[1])
        with self.assertRaises((ValueError, OSError)):
            execution.finalize_ledger(self.root, self.directory)
        self.assertFalse(self.path("commands.json").exists())

    def test_wrong_run_directory_and_symlink_or_traversal_references_fail(self):
        for directory in ("reports/old-history", "reports/current-publication-validation/../v2-x", "/outside/v2-x"):
            with self.subTest(directory=directory), self.assertRaises(ValueError):
                execution.prepare_run(self.root, directory, self.authorization)
        self.prepare()
        log = self.path("environment-python.log")
        original = log.read_bytes()
        log.unlink()
        replacement = self.write("replacement.log", original)
        log.symlink_to(replacement)
        with self.assertRaisesRegex(ValueError, "symlink"):
            execution.run_role(self.root, self.directory, self.roles[0])

    def test_native_custody_does_not_call_readiness_validation_recursively(self):
        self.prepare()
        ledger = self.finish()
        import current_publication_readiness as readiness
        with patch.object(readiness, "validation_errors", side_effect=AssertionError("recursive readiness call")):
            self.assertEqual(execution.ledger_custody_errors(ledger, self.root), [])

    def test_copied_checkout_authenticates_custody_without_relocating_execution(self):
        self.prepare()
        with tempfile.TemporaryDirectory(prefix="current-native-custody-copy-") as temporary:
            copied = Path(temporary).resolve() / "checkout"
            shutil.copytree(self.root, copied)
            with self.assertRaisesRegex(ValueError, "cannot relocate"):
                execution.run_role(copied, self.directory, self.roles[0])
            ledger = self.finish()
            original_cwd = self.root.as_posix()
            shutil.copytree(self.root, copied, dirs_exist_ok=True)
            shutil.rmtree(self.root)
            self.assertEqual(execution.ledger_custody_errors(ledger, copied), [])
            for command in ledger["commands"]:
                self.assertEqual(command["cwd"], original_cwd)
                self.assertEqual(execution.authenticate_receipt(copied, self.directory, command["name"]), command)


if __name__ == "__main__":
    unittest.main()
