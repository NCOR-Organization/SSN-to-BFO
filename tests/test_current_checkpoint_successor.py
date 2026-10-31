"""Checkpoint protocol tests use real commits in disposable repositories.

Synthetic execution receipts are test fixtures only. Existing ontology and
command-receipt validators have independent suites; this module checks the
successor protocol, exact Git tree binding, and fail-closed integration.
"""
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_checkpoint_successor as successor
import current_documentary_workbook as documentary
import current_publication_readiness as readiness
import current_source_identity as identity


class CheckpointSuccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool_identities = {}
        for command in readiness.REQUIRED_COMMANDS.values():
            resolved = Path(shutil.which(command[0])).resolve()
            cls.tool_identities[command[0]] = {
                "path": str(resolved), "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.raw_root = Path(self.temporary.name)
        self.root = self.raw_root.resolve()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Checkpoint protocol fixture")
        self.git("config", "user.email", "checkpoint-fixture@example.invalid")
        self.write("governed.txt", b"historical semantic/product bytes\n")
        self.write("tools/fixture.py", b"# governed implementation fixture\n")
        self.write("authorization.txt", b"Synthetic human authorization; test fixture only.\n")
        self.predecessor = self.commit("Historical accepted checkpoint")
        self.addCleanup(patch.stopall)
        patch.object(readiness, "native_ledger_errors", return_value=[]).start()
        patch.object(identity, "IDENTITY_BASELINE_HEAD", self.predecessor).start()
        patch.object(identity, "ACCEPTED_CHECKPOINT_HEAD", self.predecessor).start()
        patch.object(readiness.scopes, "role_inputs", side_effect=lambda root, role: {
            p: hashlib.sha256((root / p).read_bytes()).hexdigest()
            for p in ("governed.txt", "tools/fixture.py")}).start()
        patch.object(readiness.scopes, "ledger_inputs", side_effect=lambda root:
                     readiness.scopes.role_inputs(root, "assessment")).start()
        patch.object(readiness.scopes, "scope_declaration", side_effect=lambda root, role:
                     {"schema_version": 2, "profile": readiness.scopes.PROFILE, "role": role}).start()
        patch.object(readiness.scopes, "execution_tools", return_value={}).start()
        patch.object(readiness.scopes, "execution_environment", return_value={}).start()
        self.state = patch.object(successor, "_authenticated_state", side_effect=self.authenticated_state).start()
        self.write("governed.txt", b"authenticated semantic/product successor bytes\n")
        self.ledger = "reports/validation/commands.json"
        self.write_ledger()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE).decode().strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD")

    def authenticated_state(self, root):
        digest = hashlib.sha256((root / "governed.txt").read_bytes()).hexdigest()
        return {"semantic_projection_sha256": digest,
                "products": {"governed.txt": digest},
                "history": [{"kind": "semantic", "sha256": digest}]}, {"governed.txt"}

    def write_ledger(self):
        inputs = {p: hashlib.sha256((self.root / p).read_bytes()).hexdigest()
                  for p in sorted(readiness.scopes.role_inputs(self.root, "assessment"))}
        commands = []
        for name, command in readiness.REQUIRED_COMMANDS.items():
            log = f"reports/validation/{name}.log"
            data = ("Synthetic successful receipt fixture: " + name + "\n").encode()
            self.write(log, data)
            digest = hashlib.sha256(data).hexdigest()
            commands.append({"name": name, "command": command,
                             "input_scope": readiness.scopes.scope_declaration(self.root, name),
                             **{field: {} for field in (
                                 "expected_execution_tools", "execution_tools_before", "execution_tools_after",
                                 "expected_execution_environment", "execution_environment_before", "execution_environment_after")},
                             "head": self.predecessor, "expected_head": self.predecessor,
                             "final_head": self.predecessor, "expected_input_sha256": inputs,
                             "input_sha256": inputs, "input_sha256_after": inputs,
                             "input_drift": [], "execution_status": "completed", "returncode": 0,
                             "started_at_utc": "2026-10-28T12:00:00+00:00",
                             "completed_at_utc": "2026-10-28T12:01:00+00:00",
                             "tool_identity": self.tool_identities[command[0]],
                             "log": log, "log_sha256": digest, "result_artifacts": {log: digest}})
        document = {"input_scope_profile": readiness.scopes.PROFILE, "head": self.predecessor, "input_sha256": inputs, "commands": commands}
        self.write(self.ledger, documentary.canonical_bytes(document))

    def prepare(self, root=None):
        root = self.root if root is None else root
        return successor.prepare_successor(
            root, self.ledger, successor._ref(root, "authorization.txt"),
            reviewer_identity="Synthetic fixture reviewer",
            prepared_id="73d00c23-59e3-46b0-a7e0-79f5c7a67e72",
            timestamp="2026-10-28T12:02:00+00:00")

    def bind(self, root=None):
        root = self.root if root is None else root
        prepared = self.prepare(root)
        actual = self.commit("Exact validated candidate and prepared authorization")
        bound = successor.bind_successor(root, prepared.relative_to(self.root).as_posix(), actual)
        return prepared, actual, bound

    def external_alias(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        alias = Path(temporary.name).resolve() / "checkout"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("External directory symlinks unavailable: " + str(exc))
        return alias

    def assert_relative_preparation(self, prepared, *roots):
        raw = prepared.read_bytes()
        document = json.loads(raw)
        paths = [*document["candidate_files"], *document["validation"]["input_sha256"],
                 document["authorization"]["path"], document["validation"]["ledger"]["path"]]
        for path in paths:
            with self.subTest(path=path):
                self.assertFalse(Path(path).is_absolute())
                self.assertNotIn("..", Path(path).parts)
                self.assertEqual(path, Path(path).as_posix())
        for root in (self.raw_root, self.root, *roots):
            self.assertNotIn(str(root).encode(), raw)

    def test_external_root_alias_preserves_prepared_bytes_and_bind_round_trip(self):
        alias = self.external_alias()
        self.assertNotEqual(alias, self.root)
        self.assertTrue(alias.samefile(self.root))
        prepared = self.prepare(alias)
        self.assertEqual(prepared.parent.parent.parent, self.root / "reports")
        alias_bytes = prepared.read_bytes()
        self.assert_relative_preparation(prepared, alias)
        prepared.unlink()
        canonical = self.prepare()
        self.assertEqual(canonical.read_bytes(), alias_bytes)
        self.assertEqual(hashlib.sha256(canonical.read_bytes()).hexdigest(),
                         hashlib.sha256(alias_bytes).hexdigest())
        actual = self.commit("Exact candidate prepared through equivalent roots")
        bound = successor.bind_successor(alias, canonical.relative_to(self.root).as_posix(), actual)
        self.assertEqual(bound.parent.parent.parent, self.root / "reports")
        self.assertEqual(successor.validate_successor(alias)["successor_commit"], actual)
        self.assertEqual(identity.checkpoint_errors(alias), [])

    def test_macos_var_private_var_alias_round_trip(self):
        if sys.platform != "darwin" or not self.root.is_relative_to(Path("/private/var")):
            self.skipTest("A macOS temporary directory under /private/var is required")
        alias = Path("/var") / self.root.relative_to("/private/var")
        if not alias.is_dir() or not alias.samefile(self.root):
            self.skipTest("The actual /var and /private/var directory aliases are unavailable")
        self.assertNotEqual(alias, self.root)
        prepared, actual, _ = self.bind(alias)
        self.assert_relative_preparation(prepared, alias)
        self.assertEqual(successor.validate_successor(alias)["successor_commit"], actual)
        self.assertEqual(identity.checkpoint_errors(alias), [])

    def test_external_root_alias_retains_tamper_rejection(self):
        alias = self.external_alias()
        prepared, actual, bound = self.bind(alias)
        governed = (self.root / "governed.txt").read_bytes()
        self.write("governed.txt", b"unauthorized content through an alias\n")
        self.assertTrue(identity.checkpoint_errors(alias))
        self.write("governed.txt", governed)

        binding_bytes = bound.read_bytes()
        binding = json.loads(binding_bytes)
        binding["predecessor_checkpoint"] = actual
        bound.write_bytes(documentary.canonical_bytes(binding))
        self.assertTrue(identity.checkpoint_errors(alias))
        bound.write_bytes(binding_bytes)

        state = copy.deepcopy(self.authenticated_state(self.root)[0])
        state["semantic_projection_sha256"] = "wrong semantic identity"
        with patch.object(successor, "_authenticated_state", return_value=(state, {"governed.txt"})):
            self.assertTrue(identity.checkpoint_errors(alias))

        prepared_bytes = prepared.read_bytes()
        document = json.loads(prepared_bytes)
        document["reviewer_identity"] = "different reviewer"
        prepared.write_bytes(documentary.canonical_bytes(document))
        self.assertTrue(identity.checkpoint_errors(alias))
        prepared.write_bytes(prepared_bytes)
        self.assertEqual(identity.checkpoint_errors(alias), [])

    def test_distinct_temporary_roots_remain_distinct(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        other = Path(temporary.name).resolve()
        self.assertNotEqual(other, self.root)
        self.assertFalse(other.samefile(self.root))
        (other / "governed.txt").write_bytes((self.root / "governed.txt").read_bytes())
        self.assertNotEqual((other / "governed.txt").resolve(), (self.root / "governed.txt").resolve())
        with self.assertRaises(ValueError):
            successor._ref(self.root, str(other / "governed.txt"))

    def test_logical_references_still_reject_absolute_traversal_and_internal_symlinks(self):
        expected = {"path": "authorization.txt",
                    "sha256": hashlib.sha256((self.root / "authorization.txt").read_bytes()).hexdigest()}
        self.assertEqual(successor._ref(self.root, "authorization.txt"), expected)
        for path in ("../authorization.txt", str(self.root / "authorization.txt")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                successor._ref(self.root, path)
        link = self.root / "linked-authorization.txt"
        try:
            link.symlink_to(self.root / "authorization.txt")
        except (OSError, NotImplementedError) as exc:
            self.skipTest("Internal file symlinks unavailable: " + str(exc))
        with self.assertRaises(ValueError):
            successor._ref(self.root, link.name)

    def test_existing_checkpoint_remains_valid(self):
        self.assertEqual(identity.checkpoint_errors(self.root), [])
        self.assertEqual(self.git("rev-parse", "HEAD"), self.predecessor)

    def test_unauthorized_new_head_fails(self):
        self.commit("Unapproved descendant")
        self.assertTrue(identity.checkpoint_errors(self.root))

    def test_preparation_has_no_fabricated_commit_and_does_not_stage(self):
        before = self.git("diff", "--cached", "--name-only")
        prepared = json.loads(self.prepare().read_text())
        self.assertEqual(prepared["status"], "PREPARED_NOT_COMMITTED")
        self.assertNotIn("successor_commit", prepared)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), before)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.predecessor)

    def test_prepared_but_unbound_content_commit_is_not_accepted(self):
        self.prepare()
        self.commit("Prepared but not finalized")
        self.assertTrue(identity.checkpoint_errors(self.root))

    def test_properly_authorized_successor_passes_with_actual_sha(self):
        _, actual, bound = self.bind()
        document = json.loads(bound.read_text())
        self.assertEqual(document["successor_commit"], actual)
        self.assertEqual(document["predecessor_checkpoint"], self.predecessor)
        self.assertEqual(identity.checkpoint_errors(self.root), [])
        result = successor.validate_successor(self.root)
        self.assertFalse(result["publication_readiness_granted"])

    def test_receipt_only_finalization_commit_passes_but_its_descendant_does_not(self):
        _, actual, _ = self.bind()
        receipt = self.commit("Retain actual-SHA binding only")
        result = successor.validate_successor(self.root)
        self.assertEqual(result["successor_commit"], actual)
        self.assertEqual(result["receipt_carrier"], receipt)
        self.write("unapproved.txt", b"An arbitrary later commit is not accepted.\n")
        self.commit("Unauthorized descendant of finalized receipt")
        self.assertTrue(identity.checkpoint_errors(self.root))

    def test_receipt_carrier_must_have_no_other_tree_change(self):
        self.bind()
        self.write("unapproved.txt", b"Not part of the prepared content commit.\n")
        self.commit("Receipt plus unauthorized change")
        self.assertTrue(identity.checkpoint_errors(self.root))

    def test_wrong_predecessor_fails(self):
        _, actual, bound = self.bind()
        document = json.loads(bound.read_text())
        document["predecessor_checkpoint"] = actual
        bound.write_bytes(documentary.canonical_bytes(document))
        self.assertTrue(identity.checkpoint_errors(self.root))

    def test_wrong_semantic_or_product_identity_fails(self):
        self.bind()
        for field in ("semantic_projection_sha256", "products", "history"):
            state = copy.deepcopy(self.authenticated_state(self.root)[0])
            state[field] = "wrong identity"
            with patch.object(successor, "_authenticated_state", return_value=(state, {"governed.txt"})):
                with self.subTest(field=field):
                    self.assertTrue(identity.checkpoint_errors(self.root))

    def test_tampered_binding_and_live_preparation_fail(self):
        prepared, _, bound = self.bind()
        original = bound.read_bytes()
        document = json.loads(original)
        document["successor_tree"] = "0" * 40
        bound.write_bytes(documentary.canonical_bytes(document))
        self.assertTrue(identity.checkpoint_errors(self.root))
        bound.write_bytes(original)
        document = json.loads(prepared.read_text())
        document["reviewer_identity"] = "different reviewer"
        prepared.write_bytes(documentary.canonical_bytes(document))
        self.assertTrue(identity.checkpoint_errors(self.root))

    def test_candidate_commit_must_match_prepared_inventory_exactly(self):
        prepared = self.prepare()
        self.write("governed.txt", b"unauthorized content after validation\n")
        actual = self.commit("Drift after preparation")
        with self.assertRaisesRegex(ValueError, "prepared candidate inventory"):
            successor.bind_successor(self.root, prepared.relative_to(self.root).as_posix(), actual)

    def test_missing_failed_and_stale_required_validation_fail(self):
        original = (self.root / self.ledger).read_bytes()
        for mutation in ("missing", "failed", "stale"):
            document = json.loads(original)
            if mutation == "missing":
                document["commands"] = [c for c in document["commands"] if c["name"] != "full_repository_gate"]
            elif mutation == "failed":
                document["commands"][-1]["returncode"] = 1
            else:
                document["commands"][-1]["input_sha256_after"] = {}
            self.write(self.ledger, documentary.canonical_bytes(document))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.prepare()
            self.assertFalse((self.root / successor.PREPARED).exists())

    def test_fabricated_commit_sha_is_rejected(self):
        prepared = self.prepare()
        with self.assertRaises(subprocess.CalledProcessError):
            successor.bind_successor(self.root, prepared.relative_to(self.root).as_posix(), "f" * 40)

    def test_runtime_tool_is_authenticated_without_becoming_a_commit_candidate(self):
        runtime = self.write("build/lib/robot.jar", b"synthetic runtime tool; not source")
        self.write(".gitignore", b"build/\n")
        def tools(root, role):
            data = runtime.read_bytes()
            return {"robot_jar": {"path": str(runtime), "bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest()}}
        document = json.loads((self.root / self.ledger).read_bytes())
        for command in document["commands"]:
            for field in ("expected_execution_tools", "execution_tools_before", "execution_tools_after"):
                command[field] = tools(self.root, command["name"])
        self.write(self.ledger, documentary.canonical_bytes(document))
        with patch.object(readiness.scopes, "execution_tools", side_effect=tools):
            prepared = json.loads(self.prepare().read_bytes())
            self.assertNotIn("build/lib/robot.jar", prepared["candidate_files"])
            self.assertNotIn("build/lib/robot.jar", prepared["validation"]["input_sha256"])
            runtime.write_bytes(b"different runtime executable")
            with self.assertRaisesRegex(ValueError, "execution_tools"):
                successor._validation(self.root, self.ledger, self.predecessor)

    def test_changed_bound_validation_log_fails(self):
        self.bind()
        self.write("reports/validation/full_repository_gate.log", b"changed receipt output\n")
        self.assertTrue(identity.checkpoint_errors(self.root))


class CurrentCheckpointIntegrationTests(unittest.TestCase):
    def test_qualified_release_preserves_historical_protocol_and_governed_files(self):
        root = identity.ROOT
        protected = (identity.WORKBOOK, "mappings/current-ssn-sosa-assessment.json", *identity.PRODUCTS)
        before = {path: identity.fingerprint(root / path) for path in protected}
        # The completed October baseline has separately authorized query bytes.
        # Its acceptance must not silently broaden the older receipt protocol.
        self.assertTrue(identity.qualified_release_checkpoint(root))
        self.assertEqual(identity.checkpoint_errors(root), [])
        with self.assertRaisesRegex(ValueError, "non-evolvable governed input: queries/unmapped-source-terms.rq"):
            successor._authenticated_authorities(root)
        self.assertEqual(before, {path: identity.fingerprint(root / path) for path in protected})


if __name__ == "__main__":
    unittest.main()
