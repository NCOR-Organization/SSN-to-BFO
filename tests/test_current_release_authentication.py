"""Qualified artifact acceptance remains exact without changing old receipts."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_source_identity as identity
import release_context


class QualifiedReleaseAuthenticationTests(unittest.TestCase):
    """Real commits in disposable repositories; production anchors stay fixed."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="qualified-release-auth-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Release authentication test")
        self.git("config", "user.email", "fixture@example.invalid")
        self.write("imports/sosa.ttl", b"# exact source bytes\n")
        self.write(identity.AUTHORIZED_QUERY, b"# original query\n")
        self.write("mappings/current-ssn-sosa-assessment.json", b"[]\n")
        self.receipt = "reports/current-checkpoint-successors/bindings/old.json"
        self.write(self.receipt, b'{"historical":"immutable"}\n')
        self.parent = self.commit("Historical fixture checkpoint")
        self.write(identity.AUTHORIZED_QUERY, b"# explicitly approved query\n")
        self.base = self.commit("Approved completed artifact fixture")
        authorization = b"Synthetic fixture authorizes only technical release repairs.\n"
        self.write(identity.RELEASE_REPAIR_AUTHORIZATION, authorization)
        for name, value in (
            ("ARTIFACT_RELEASE_BASELINE", self.base),
            ("ARTIFACT_RELEASE_PARENT", self.parent),
            ("ACCEPTED_CHECKPOINT_HEAD", self.parent),
            ("RELEASE_REPAIR_AUTHORIZATION_SHA256", hashlib.sha256(authorization).hexdigest()),
        ):
            self.enterContext(patch.object(identity, name, value))

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def write(self, path, data):
        actual = self.root / path
        actual.parent.mkdir(parents=True, exist_ok=True)
        actual.write_bytes(data)

    def commit(self, message):
        paths = self.git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
        self.git("add", "--", *paths)
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_approved_baseline_detached_and_repair_successors_pass(self):
        self.assertTrue(identity.qualified_release_checkpoint(self.root))
        self.write("tools/current_source_identity.py", b"# authorized repair fixture\n")
        self.commit("Technical repair fixture only")
        self.write("release-notes/2099-01-02.md", b"# Explicitly qualified synthetic release\n")
        final = self.commit("Release notes fixture only")
        self.git("checkout", "--quiet", "--detach", final)
        self.assertTrue(identity.qualified_release_checkpoint(self.root))

    def test_live_query_source_and_assessment_drift_fail(self):
        for path in (identity.AUTHORIZED_QUERY, "imports/sosa.ttl",
                     "mappings/current-ssn-sosa-assessment.json", self.receipt):
            with self.subTest(path=path):
                original = (self.root / path).read_bytes()
                self.write(path, original + b"unauthorized\n")
                with self.assertRaisesRegex(ValueError, "byte/mode drift"):
                    identity.qualified_release_checkpoint(self.root)
                self.write(path, original)

    def test_committed_query_drift_is_not_authorized_by_lineage(self):
        self.write(identity.AUTHORIZED_QUERY, b"# unauthorized committed query\n")
        self.commit("Unauthorized query fixture")
        with self.assertRaisesRegex(ValueError, "unauthorized committed"):
            identity.qualified_release_checkpoint(self.root)

    def test_forbidden_committed_change_then_revert_still_fails(self):
        original = (self.root / identity.AUTHORIZED_QUERY).read_bytes()
        self.write(identity.AUTHORIZED_QUERY, b"# unauthorized intermediate query\n")
        self.commit("Unauthorized intermediate query fixture")
        self.write(identity.AUTHORIZED_QUERY, original)
        self.commit("Restore approved query bytes fixture")
        self.assertEqual((self.root / identity.AUTHORIZED_QUERY).read_bytes(), original)
        with self.assertRaisesRegex(ValueError, "unauthorized committed.*lineage"):
            identity.qualified_release_checkpoint(self.root)

    def test_new_forged_successor_receipt_fails(self):
        self.write("reports/current-checkpoint-successors/bindings/forged.json", b"{}\n")
        with self.assertRaisesRegex(ValueError, "receipt inventory"):
            identity.qualified_release_checkpoint(self.root)

    def test_arbitrary_descendant_path_is_not_whitelisted(self):
        self.write("unapproved-runtime.py", b"# not a release repair surface\n")
        self.commit("Unapproved implementation fixture")
        with self.assertRaisesRegex(ValueError, "unauthorized committed"):
            identity.qualified_release_checkpoint(self.root)

    def test_missing_or_modified_authorization_fails(self):
        path = self.root / identity.RELEASE_REPAIR_AUTHORIZATION
        path.unlink()
        with self.assertRaisesRegex(ValueError, "authorization"):
            identity.qualified_release_checkpoint(self.root)
        path.write_bytes(b"forged authorization\n")
        with self.assertRaisesRegex(ValueError, "authorization"):
            identity.qualified_release_checkpoint(self.root)

    def test_wrong_parent_and_unrelated_source_commit_fail(self):
        with patch.object(identity, "ARTIFACT_RELEASE_PARENT", self.base):
            with self.assertRaisesRegex(ValueError, "lineage"):
                identity.qualified_release_checkpoint(self.root)
        self.git("checkout", "--quiet", "--detach", self.parent)
        self.assertFalse(identity.qualified_release_checkpoint(self.root))

    def test_symlink_source_is_rejected_even_with_matching_bytes(self):
        source = self.root / "imports/sosa.ttl"
        replacement = self.root / "copy.ttl"
        replacement.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(replacement)
        with self.assertRaisesRegex(ValueError, "byte/mode drift"):
            identity.qualified_release_checkpoint(self.root)

    @contextmanager
    def active_release(self):
        """Supply cached rendering only; exercise the real checkpoint guard."""
        self.assertTrue(identity.qualified_release_checkpoint(self.root))
        # This folder selects the current-track branch, not the historical
        # no-transition fallback. No production evidence is created or copied.
        (self.root / "reports/current-semantic-workbook/transitions").mkdir(parents=True)
        context = release_context.FormalReleaseContext(
            "2099-01-02", "2099-01-02", "v2099-01-02", self.base)
        signature = (("synthetic-rendered-input", "unchanged"),)
        active = release_context.ReleaseExpectations(context, self.root.resolve(), signature, ())
        token = release_context._ACTIVE_RELEASE.set(active)
        try:
            # A stable byte signature deliberately cannot detect HEAD, modes,
            # or forged receipts. Their real Git/file checks must still run.
            with patch.object(release_context, "_release_input_signature", return_value=signature):
                yield context, active
        finally:
            release_context._ACTIVE_RELEASE.reset(token)

    def test_active_context_reuse_accepts_unchanged_checkpoint(self):
        with self.active_release() as (context, active):
            with release_context.authenticated_release_expectations(self.root, context) as actual:
                self.assertIs(actual, active)

    def test_active_context_rejects_forged_receipt_at_entry(self):
        with self.active_release() as (context, _):
            self.write("reports/current-checkpoint-successors/bindings/forged.json", b"{}\n")
            with self.assertRaisesRegex(ValueError, "receipt inventory"):
                with release_context.authenticated_release_expectations(self.root, context):
                    self.fail("Forged receipt was accepted by active-context reuse")

    def test_active_context_rejects_forged_receipt_at_exit(self):
        with self.active_release() as (context, _):
            with self.assertRaisesRegex(ValueError, "receipt inventory"):
                with release_context.authenticated_release_expectations(self.root, context):
                    self.write("reports/current-checkpoint-successors/bindings/forged.json", b"{}\n")

    def test_active_context_rejects_executable_mode_change_at_entry(self):
        with self.active_release() as (context, _):
            source = self.root / "imports/sosa.ttl"
            source.chmod(source.stat().st_mode | 0o111)
            with self.assertRaisesRegex(ValueError, "byte/mode drift"):
                with release_context.authenticated_release_expectations(self.root, context):
                    self.fail("Executable-mode drift was accepted by active-context reuse")

    def test_active_context_rejects_executable_mode_change_at_exit(self):
        with self.active_release() as (context, _):
            with self.assertRaisesRegex(ValueError, "byte/mode drift"):
                with release_context.authenticated_release_expectations(self.root, context):
                    source = self.root / "imports/sosa.ttl"
                    source.chmod(source.stat().st_mode | 0o111)

    def test_active_context_rejects_unrelated_same_tree_head_at_entry(self):
        with self.active_release() as (context, _):
            tree = self.git("rev-parse", "HEAD^{tree}")
            unrelated = self.git("commit-tree", tree, "-m", "Unrelated identical-tree fixture")
            self.git("checkout", "--quiet", "--detach", unrelated)
            self.assertEqual(self.git("rev-parse", "HEAD^{tree}"), tree)
            with self.assertRaisesRegex(ValueError, "release checkpoint authentication failed"):
                with release_context.authenticated_release_expectations(self.root, context):
                    self.fail("Unrelated source identity was accepted by active-context reuse")

    def test_active_context_rejects_head_change_at_exit_even_if_successor_is_allowed(self):
        with self.active_release() as (context, _):
            with self.assertRaisesRegex(ValueError, "source HEAD changed"):
                with release_context.authenticated_release_expectations(self.root, context):
                    # This commits only the authorized repair instruction; the
                    # descendant itself passes, but an in-flight HEAD swap may not.
                    self.commit("Allowed repair successor during active operation fixture")
                    self.assertTrue(identity.qualified_release_checkpoint(self.root))


if __name__ == "__main__":
    unittest.main()
