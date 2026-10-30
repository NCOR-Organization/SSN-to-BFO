"""Code-owned role scopes distinguish producer inputs from later consumers."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_validation_scope as scope


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ValidationScopeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="current-validation-scope-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for directory in ("tools", "tests", "config", "mappings", "imports", "rules", "queries",
                          "releases/current-ssn-sosa", "releases/sosa-next", "src/sosa-next",
                          "requirements", "legacy", "docs", ".github"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self.write(scope.POLICY_PATH, (ROOT / scope.POLICY_PATH).read_bytes())
        self.write(scope.CUSTODY_POLICY_PATH, b'"""Synthetic authority resolver identity."""\n')
        self.write("Makefile", b"compile:\n\tpython -m py_compile tools/current_*.py tests/test_current*.py\n\ncheck: compile\n")
        self.write("tests/test_current_example.py", b"VALUE = 'fixture'\n")
        for path in ("tools/check_sosa_source_version.py", "tools/current_source_identity.py",
                     "tools/current_assessment.py", "tools/check_coms_mapping.py",
                     "tools/generate_mapping_from_coms.py", "tools/check_sosa_next_products.py"):
            self.write(path, b"VALUE = 'fixture'\n")
        self.write("tools/check_sosa_source_version.py", b"import sosa_source_version\n")
        self.write("tools/sosa_source_version.py", b"VERSION = 1\n")
        self.write("config/sosa-source-version.toml", b'[[source_files]]\nlocal_path="src/sosa-next/source.ttl"\n[local_overlay]\npath="src/sosa-next/overlay.ttl"\n')
        for path in ("src/sosa-next/source.ttl", "src/sosa-next/overlay.ttl", "SSN2BFO.ttl",
                     "legacy/SSN2BFO-pre-COMS.ttl", "README.md", ".gitignore",
                     "config/authority.json", "config/assessment-source.json",
                     "requirements/validation.txt", "tools/install_validation_robot.sh",
                     "config/validation-toolchain.env", scope.REASONER_JAR):
            self.write(path, b"fixture bytes\n")
        for path in scope.GENERATION_REPORTS:
            self.write(path, b"maintained report\n")
        for name in scope.ASSESSMENT_NAMES:
            self.write(scope.ASSESSMENT_DIRECTORY + "/" + name, b"checked assessment output\n")
        # Exercise the actual fixed-family resolver against synthetic raw
        # records. Only its code-pinned digest is fixture-specific; its path,
        # membership, byte authentication and containment code run unchanged.
        evidence = str(Path(scope.HISTORICAL_TEST_REPORT).parent / "original.stdout.log")
        data = b"original completed FAIL\n"
        self.write(evidence, data)
        report = json.dumps({"evidence_files": [{"path": evidence, "sha256": digest(data), "bytes": len(data)}]}).encode()
        self.write(scope.HISTORICAL_TEST_REPORT, report)
        self.archive_hash = patch.object(scope, "HISTORICAL_TEST_SHA256", digest(report))
        self.archive_hash.start()
        self.addCleanup(self.archive_hash.stop)
        checkpoint_report = "reports/checkpoint-original.md"
        self.write(checkpoint_report, b"accepted checkpoint report\n")
        def fixture_git_paths(root, *arguments):
            if arguments[0] == "ls-tree":
                return {checkpoint_report}
            return {p.relative_to(root).as_posix() for p in Path(root).rglob("*")
                    if p.is_file() and p.relative_to(root).parts[0] != "build"}
        context = patch.object(scope, "_git_paths", side_effect=fixture_git_paths)
        context.start()
        self.addCleanup(context.stop)
        log = str(Path(scope.HISTORICAL_LEDGER).parent / "original.log")
        log_bytes = b"original completed PASS\n"
        self.write(log, log_bytes)
        ledger = json.dumps({"input_sha256": {"then-only": "a" * 64}, "commands": [
            {"log": log, "log_sha256": digest(log_bytes), "result_artifacts": {log: digest(log_bytes)}}]}).encode()
        self.write(scope.HISTORICAL_LEDGER, ledger)
        context = patch.object(scope, "HISTORICAL_LEDGER_SHA256", digest(ledger))
        context.start()
        self.addCleanup(context.stop)
        # Scope derivation is the subject here. The authority resolver has its
        # own real-chain tests; these substitutes provide fixed authenticated
        # fixture paths, never a mocked role scope or declared subset.
        import current_custody_dependencies as custody
        for name, value in (("assessment_paths", {"config/assessment-source.json"}),
                            ("authority_paths", {"config/authority.json"})):
            context = patch.object(custody, name, return_value=value)
            context.start()
            self.addCleanup(context.stop)

    def write(self, relative: str, data: bytes):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_all_eight_roles_are_code_owned_and_unknown_roles_fail(self):
        self.assertEqual(set(scope.REQUIRED_COMMANDS), {
            "unit_tests", "assessment", "source_identity", "generation_freshness",
            "sosa_source_version", "sosa_products", "static_checks", "full_repository_gate"})
        for role in scope.REQUIRED_COMMANDS:
            with self.subTest(role=role):
                inputs = scope.role_inputs(self.root, role)
                self.assertIn(scope.POLICY_PATH, inputs)
                self.assertIn(scope.CUSTODY_POLICY_PATH, inputs)
                scope.validate_declaration(scope.scope_declaration(self.root, role), self.root, role)
        with self.assertRaisesRegex(ValueError, "unknown"):
            scope.role_inputs(self.root, "invented_success")

    def test_genuine_source_and_imported_tool_changes_invalidate_role_inputs(self):
        for path in ("src/sosa-next/source.ttl", "tools/sosa_source_version.py",
                     "config/sosa-source-version.toml"):
            with self.subTest(path=path):
                before = scope.role_inputs(self.root, "sosa_source_version")
                original = (self.root / path).read_bytes()
                # All three formats accept a comment, preserving parseability.
                self.write(path, original + b"\n# changed material dependency\n")
                after = scope.role_inputs(self.root, "sosa_source_version")
                self.assertNotEqual(before[path], after[path])
                self.write(path, original)

    def test_unrelated_retention_does_not_rewrite_producer_or_compile_scope(self):
        roles = ("assessment", "source_identity", "generation_freshness",
                 "sosa_source_version", "sosa_products", "static_checks")
        before = {role: scope.role_inputs(self.root, role) for role in roles}
        self.write("reports/retained-evidence/execution/sha256/unrelated.rdf", b"new immutable output\n")
        for role in roles:
            with self.subTest(role=role):
                self.assertEqual(before[role], scope.role_inputs(self.root, role))

    def test_later_whole_suite_consumers_bind_retained_bytes_and_membership(self):
        roles = ("unit_tests", "full_repository_gate")
        before = {role: scope.role_inputs(self.root, role) for role in roles}
        path = "reports/retained-evidence/execution/sha256/later.rdf"
        self.write(path, b"first retained bytes\n")
        for role in roles:
            with self.subTest(role=role):
                after = scope.role_inputs(self.root, role)
                self.assertNotIn(path, before[role])
                self.assertEqual(after[path], digest(b"first retained bytes\n"))
                self.write(path, b"changed retained bytes\n")
                self.assertNotEqual(after[path], scope.role_inputs(self.root, role)[path])
                self.write(path, b"first retained bytes\n")

    def test_fixed_historical_archive_missing_corrupt_and_extra_records_fail(self):
        report = json.loads((self.root / scope.HISTORICAL_TEST_REPORT).read_bytes())
        path = report["evidence_files"][0]["path"]
        original = (self.root / path).read_bytes()
        for action in ("missing", "corrupt", "extra"):
            with self.subTest(action=action):
                extra = self.root / Path(scope.HISTORICAL_TEST_REPORT).parent / "unbound.log"
                if action == "missing":
                    (self.root / path).unlink()
                elif action == "corrupt":
                    self.write(path, b"forged outcome\n")
                else:
                    extra.write_bytes(b"unbound\n")
                with self.assertRaises(ValueError):
                    scope.historical_test_paths(self.root)
                self.write(path, original)
                extra.unlink(missing_ok=True)

    def test_caller_supplied_subsets_versions_roles_and_policy_claims_fail(self):
        original = scope.scope_declaration(self.root, "static_checks")
        changes = (
            ("schema_version", 1), ("schema_version", 2.0), ("profile", "universal-316"),
            ("role", "assessment"), ("input_paths", ["Makefile"]),
            ("policy", {"path": scope.POLICY_PATH, "sha256": "0" * 64}),
            ("custody_policy", {"path": scope.CUSTODY_POLICY_PATH, "sha256": "0" * 64}),
            ("migration_report_checkpoint", "0" * 40),
        )
        for key, value in changes:
            with self.subTest(key=key):
                forged = copy.deepcopy(original)
                forged[key] = value
                with self.assertRaisesRegex(ValueError, "incompatible"):
                    scope.validate_declaration(forged, self.root, "static_checks")

    def test_legacy_receipt_is_unchanged_and_cannot_claim_v2_execution(self):
        legacy = {"head": "historical", "input_sha256": {"old-input": "a" * 64}, "returncode": 0}
        encoded = json.dumps(legacy, sort_keys=True).encode()
        path = self.write("reports/historical-316/commands.json", encoded)
        with self.assertRaisesRegex(ValueError, "incompatible"):
            scope.validate_declaration(legacy.get("input_scope"), self.root, "static_checks")
        self.assertEqual(path.read_bytes(), encoded)

    def test_receipt_snapshot_cannot_claim_a_future_discovered_test(self):
        old = scope.role_inputs(self.root, "unit_tests")
        frozen = copy.deepcopy(old)
        new = "tests/test_added_after_execution.py"
        self.write(new, b"NEW_TEST = True\n")
        current = scope.role_inputs(self.root, "unit_tests")
        self.assertNotIn(new, old)
        self.assertIn(new, current)
        self.assertNotEqual(old, current)
        self.assertEqual(old, frozen)

    def test_assessment_check_binds_every_compared_output_and_missing_fails(self):
        before = scope.role_inputs(self.root, "assessment")
        for name in scope.ASSESSMENT_NAMES:
            path = scope.ASSESSMENT_DIRECTORY + "/" + name
            with self.subTest(path=path):
                self.assertIn(path, before)
                original = (self.root / path).read_bytes()
                self.write(path, original + b"changed\n")
                self.assertNotEqual(before[path], scope.role_inputs(self.root, "assessment")[path])
                (self.root / path).unlink()
                with self.assertRaisesRegex(ValueError, "missing"):
                    scope.role_inputs(self.root, "assessment")
                self.write(path, original)

    def test_receipts_logs_and_selection_are_not_their_own_future_inputs(self):
        roles = tuple(scope.REQUIRED_COMMANDS)
        before = {role: scope.role_inputs(self.root, role) for role in roles}
        for path in ("reports/current-publication-validation/future/commands.json",
                     "reports/current-publication-validation/future/unit_tests.log",
                     "reports/current-publication-validation/current-evidence.json"):
            self.write(path, b"later output or selection\n")
        for role in roles:
            with self.subTest(role=role):
                self.assertEqual(before[role], scope.role_inputs(self.root, role))

    def test_compile_scope_tracks_makefile_operands_and_glob_membership_only(self):
        before = scope.role_inputs(self.root, "static_checks")
        self.assertIn("tests/test_current_example.py", before)
        self.assertNotIn("src/sosa-next/source.ttl", before)
        self.write("src/sosa-next/source.ttl", b"unrelated ontology edit\n")
        self.assertEqual(before, scope.role_inputs(self.root, "static_checks"))
        self.write("tools/current_added.py", b"NEW = 1\n")
        self.assertIn("tools/current_added.py", scope.role_inputs(self.root, "static_checks"))
        self.write("Makefile", b"compile:\n\tpython -m py_compile tests/test_current_example.py\n")
        after = scope.role_inputs(self.root, "static_checks")
        self.assertNotIn("tools/current_added.py", after)
        self.assertNotEqual(before["Makefile"], after["Makefile"])

    def test_compile_dynamic_commands_and_missing_operands_fail_closed(self):
        for recipe in (b"compile:\n\tpython -m py_compile $(FILES)\n",
                       b"compile:\n\tpython -m py_compile tools/missing.py\n",
                       b"compile:\n\tpython -m py_compile tools/no-match-*.py\n"):
            with self.subTest(recipe=recipe):
                self.write("Makefile", recipe)
                with self.assertRaises(ValueError):
                    scope.role_inputs(self.root, "static_checks")

    def test_paths_reject_symlinks_absolute_and_traversal_without_widening_scope(self):
        for path in ("../outside", "/tmp/outside", "tools/../outside", "tools//x.py", "tools\\x.py"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                scope._path(self.root, path, required=False)
        original = self.root / "src/sosa-next/source.ttl"
        original.unlink()
        original.symlink_to(self.root / "src/sosa-next/overlay.ttl")
        with self.assertRaisesRegex(ValueError, "symlink"):
            scope.role_inputs(self.root, "sosa_source_version")

    def test_loaded_policy_must_match_declared_on_disk_policy(self):
        self.write(scope.POLICY_PATH, (ROOT / scope.POLICY_PATH).read_bytes() + b"\n# forged policy\n")
        with self.assertRaisesRegex(ValueError, "loaded implementation"):
            scope.scope_declaration(self.root, "static_checks")

    def test_retired_artifact_absence_and_reasoner_jar_have_separate_bindings(self):
        role = "unit_tests"
        original = scope.scope_declaration(self.root, role)
        retired = scope.RETIRED_PATHS[-1]
        self.assertIn(retired, original["absent_paths"])
        self.write(retired, b"unexpected retired artifact\n")
        self.assertNotIn(retired, scope.scope_declaration(self.root, role)["absent_paths"])
        self.assertIn(retired, scope.role_inputs(self.root, role))
        for role in scope.REASONING_ROLES:
            with self.subTest(role=role):
                self.assertNotIn(scope.REASONER_JAR, scope.role_inputs(self.root, role))
        executable = self.write("fixture-bin/tool", b"synthetic executable\n")
        self.write("build/lib/robot-1.9.7/bin/robot", b"synthetic installed wrapper\n")
        jar_bytes = (self.root / scope.REASONER_JAR).read_bytes()
        with patch.object(scope, "REASONER_JAR_SHA256", digest(jar_bytes)), patch.object(
                scope.shutil, "which", side_effect=lambda name: sys.executable if name == "python" else str(executable)):
            tools = scope.execution_tools(self.root, "sosa_products")
            self.assertEqual(tools["robot_jar"], {
                "path": str(self.root / scope.REASONER_JAR), "sha256": digest(jar_bytes), "bytes": len(jar_bytes)})
            self.write(scope.REASONER_JAR, b"changed executable dependency\n")
            with self.assertRaisesRegex(ValueError, "JAR differs"):
                scope.execution_tools(self.root, "sosa_products")

    def test_missing_or_wrong_reasoner_jar_fails_before_executable_discovery(self):
        with patch.object(scope.shutil, "which", side_effect=AssertionError("must bind JAR first")):
            with self.assertRaisesRegex(ValueError, "JAR differs"):
                scope.execution_tools(self.root, "sosa_products")
            (self.root / scope.REASONER_JAR).unlink()
            with self.assertRaisesRegex(ValueError, "missing regular validation input"):
                scope.execution_tools(self.root, "sosa_products")

    def test_ledger_union_is_exactly_the_code_owned_role_snapshots(self):
        expected = {}
        for role in scope.REQUIRED_COMMANDS:
            expected.update(scope.role_inputs(self.root, role))
        self.assertEqual(scope.ledger_inputs(self.root), expected)

    def test_historical_ledger_results_are_bound_without_promoting_original_input_map(self):
        paths = scope.historical_ledger_paths(self.root)
        self.assertIn(scope.HISTORICAL_LEDGER, paths)
        self.assertNotIn("then-only", paths)
        log = str(Path(scope.HISTORICAL_LEDGER).parent / "original.log")
        self.write(log, b"forged PASS\n")
        with self.assertRaisesRegex(ValueError, "artifact differs"):
            scope.historical_ledger_paths(self.root)

    def test_executable_bytes_and_environment_are_measured_not_claimed(self):
        executable = Path(sys.executable).resolve()
        fake = self.write("fixture-bin/make", b"synthetic make executable\n")
        def resolve(name):
            return str(executable if name == "python" else fake)
        with patch.object(scope.shutil, "which", side_effect=resolve):
            before = scope.execution_tools(self.root, "static_checks")
            self.assertEqual(before["python"]["sha256"], digest(executable.read_bytes()))
            self.assertEqual(before["sh"]["path"], str(Path("/bin/sh").resolve()))
            self.assertEqual(before["sh"]["sha256"], digest(Path("/bin/sh").read_bytes()))
            self.write("fixture-bin/make", b"changed executable\n")
            self.assertNotEqual(before["make"], scope.execution_tools(self.root, "static_checks")["make"])
        with patch.dict(os.environ, {"JAVA_TOOL_OPTIONS": "-Dfixture=one"}):
            before = scope.execution_environment()
        with patch.dict(os.environ, {"JAVA_TOOL_OPTIONS": "-Dfixture=two"}):
            self.assertNotEqual(before, scope.execution_environment())

    def test_missing_executable_or_different_path_python_fails_closed(self):
        with patch.object(scope.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "missing required"):
                scope.execution_tools(self.root, "sosa_source_version")
        fake = self.write("fixture-bin/python", b"different interpreter\n")
        with patch.object(scope.shutil, "which", return_value=str(fake)):
            with self.assertRaisesRegex(ValueError, "PATH Python differs"):
                scope.execution_tools(self.root, "sosa_source_version")


class MigrationGuardInventoryTests(unittest.TestCase):
    """Real temporary Git index changes must not introduce future report cycles."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="current-scope-git-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.git("init", "-q")
        self.write("LICENSE", b"license\n")
        self.write(".gitattributes", b"*.ttl text\n")
        self.write(".gitignore", b"build/\n")
        self.write("reports/accepted.md", b"accepted report\n")
        self.git("add", ".")
        self.git("-c", "user.name=Scope fixture", "-c", "user.email=scope@example.invalid",
                 "commit", "--no-gpg-sign", "-qm", "immutable fixture")
        checkpoint = self.git("rev-parse", "HEAD").decode().strip()
        context = patch.object(scope, "MIGRATION_REPORT_CHECKPOINT", checkpoint)
        context.start()
        self.addCleanup(context.stop)

    def git(self, *arguments):
        return subprocess.check_output(["git", "-C", str(self.root), *arguments], stderr=subprocess.PIPE)

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_newly_tracked_selector_and_receipts_never_enter_fixed_report_inventory(self):
        before = scope.migration_guard_paths(self.root)
        selector = "reports/current-publication-validation/current-evidence.json"
        self.write(selector, b"future selector\n")
        self.write("reports/future/commands.json", b"future receipt\n")
        self.assertEqual(before, scope.migration_guard_paths(self.root))
        self.git("add", "reports")
        self.assertEqual(before, scope.migration_guard_paths(self.root))
        self.git("-c", "user.name=Scope fixture", "-c", "user.email=scope@example.invalid",
                 "commit", "--no-gpg-sign", "-qm", "later evidence")
        self.assertEqual(before, scope.migration_guard_paths(self.root))
        self.assertIn("reports/accepted.md", before)

    def test_new_nonreport_member_and_bytes_are_inputs_independent_of_staging(self):
        before = scope.migration_guard_paths(self.root)
        self.assertLessEqual({"LICENSE", ".gitattributes", ".gitignore"}, before)
        path = "release-notes/current.txt"
        self.write(path, b"active release notes\n")
        after = scope.migration_guard_paths(self.root)
        self.assertEqual(after, before | {path})
        first = scope._sha(self.root, path)
        self.git("add", path)
        self.assertEqual(after, scope.migration_guard_paths(self.root))
        self.write(path, b"changed active release notes\n")
        self.assertNotEqual(first, scope._sha(self.root, path))
        self.write("build/transient.log", b"ignored runtime output\n")
        self.assertEqual(after, scope.migration_guard_paths(self.root))

    def test_missing_checkpoint_report_and_nonreport_symlink_fail(self):
        report = self.root / "reports/accepted.md"
        report.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            scope.migration_guard_paths(self.root)
        self.write("reports/accepted.md", b"accepted report\n")
        (self.root / "linked-license").symlink_to(self.root / "LICENSE")
        with self.assertRaisesRegex(ValueError, "symlink"):
            scope.migration_guard_paths(self.root)


if __name__ == "__main__":
    unittest.main()
