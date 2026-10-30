#!/usr/bin/env python3
"""Regression contract for the independent SOSA-2023 release runtime."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import shutil
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_release as current  # noqa: E402
import sosa_2023_release_runtime as runtime  # noqa: E402
from tests import release_authority_fixture as authority  # noqa: E402


CURRENT_BUILD_HASH = (
    "3969aa59159dc5caf1c3f69b2ccef5ca9c9bd28d317b97dcb332e5a04fa2eb76"
)


def issue_signature(values):
    return tuple(
        (
            value.code,
            value.field,
            value.message,
        )
        for value in values
    )


class Sosa2023ReleaseRuntimeTests(unittest.TestCase):
    def test_release_note_policy_is_exactly_preserved(self) -> None:
        template = (
            REPO_ROOT
            / "release-notes/TEMPLATE.md"
        ).read_bytes()

        valid = (
            REPO_ROOT
            / "release-notes/SYNTHETIC-2099-01-02.md"
        ).read_bytes()

        cases = (
            valid,
            b"",
            b"\xff",
            valid.replace(b"\n", b"\r\n"),
            valid[:-1],
            valid + b"\n",
            valid.replace(b"Synthetic", b"Synthetic\x00", 1),
            template,
            valid.replace(b"Synthetic", b"Synthetic TODO", 1),
            valid.replace(b"# Dependencies", b"## Dependencies"),
        )

        for index, value in enumerate(cases):
            with self.subTest(index=index):
                self.assertEqual(
                    issue_signature(
                        runtime.validate_release_notes_bytes(
                            value,
                            template_bytes=template,
                        )
                    ),
                    issue_signature(
                        current.validate_release_notes_bytes(
                            value,
                            template_bytes=template,
                        )
                    ),
                )

    def test_required_release_note_headings_are_identical(self) -> None:
        self.assertEqual(
            runtime.REQUIRED_RELEASE_NOTE_HEADINGS,
            current.REQUIRED_RELEASE_NOTE_HEADINGS,
        )

    def test_offline_environment_is_identical(self) -> None:
        fixture = {
            "PATH": "/fixture/bin",
            "HTTP_PROXY": "http://example.invalid:1",
            "https_proxy": "http://example.invalid:2",
            "NO_PROXY": "localhost",
            "OTHER": "value",
        }

        self.assertEqual(
            runtime.offline_subprocess_environment(
                fixture
            ),
            current.offline_subprocess_environment(
                fixture
            ),
        )

    def test_resolved_toolchain_contract_matches_current_reference(self) -> None:
        expected = current.resolve_validation_toolchain(
            REPO_ROOT
        )
        observed = runtime.resolve_validation_toolchain(
            REPO_ROOT
        )

        expected_fields = {
            field.name
            for field in dataclasses.fields(expected)
        }

        observed_fields = {
            field.name
            for field in dataclasses.fields(observed)
        }

        self.assertEqual(
            observed_fields,
            expected_fields,
        )

        for field in sorted(expected_fields):
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(observed, field),
                    getattr(expected, field),
                )

        self.assertEqual(
            observed.java_robot_command(),
            expected.java_robot_command(),
        )

    def test_verified_launcher_uses_same_governed_runtime(self) -> None:
        toolchain = runtime.resolve_validation_toolchain(
            REPO_ROOT
        )

        with tempfile.TemporaryDirectory(
            prefix="sosa-2023-release-runtime-"
        ) as directory:
            root = Path(directory)

            with runtime.verified_robot_launcher(
                toolchain,
                root,
            ) as launcher:
                text = launcher.read_text(
                    encoding="utf-8"
                )

                self.assertIn(
                    str(toolchain.java_executable),
                    text,
                )
                self.assertIn(
                    str(toolchain.robot_jar),
                    text,
                )

                for option in runtime.OFFLINE_JAVA_OPTIONS:
                    self.assertIn(
                        option,
                        text,
                    )

                completed = subprocess.run(
                    [
                        str(launcher),
                        "--version",
                    ],
                    cwd=REPO_ROOT,
                    env=runtime.offline_subprocess_environment(),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                self.assertIn(
                    f"ROBOT version {toolchain.robot_version}",
                    completed.stdout + completed.stderr,
                )

    def test_runtime_has_no_current_builder_or_manifest_dependency(self) -> None:
        text = (
            REPO_ROOT
            / "tools/sosa_2023_release_runtime.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn(
            "import build_release",
            text,
        )
        self.assertNotIn(
            "from build_release",
            text,
        )
        self.assertNotIn(
            "release_manifest",
            text,
        )

    def test_current_builder_remains_byte_locked(self) -> None:
        identities = authority.authenticate_role(
            REPO_ROOT, "current_release_builder", "tools/build_release.py")
        self.assertEqual(identities["historical"], CURRENT_BUILD_HASH)
        self.assertEqual(identities["current"], hashlib.sha256(
            (REPO_ROOT / "tools/build_release.py").read_bytes()).hexdigest())


class ReleaseImplementationRoleTests(unittest.TestCase):
    """Approval belongs to exact implementation bytes and their logical role."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="release-role-evidence-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".git").symlink_to(REPO_ROOT / ".git", target_is_directory=True)
        self.record = json.loads((REPO_ROOT / authority.CURRENT_AUTHORITY_FIXTURE).read_bytes())
        self.evidence_paths = {
            authority.CURRENT_AUTHORITY_FIXTURE,
            *(self.record[key]["path"] for key in ("authorization", "provenance")),
            authority.FOLLOWUP_REQUEST["path"], authority.FOLLOWUP_RESULT["path"],
        }
        for relative in {*authority.RELEASE_ROLES.values(), *self.evidence_paths}:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / relative, destination)

    def builder(self):
        return authority.authenticate_role(self.root, "current_release_builder", "tools/build_release.py")

    def test_historical_and_current_roles_validate_without_rewriting_evidence(self):
        before = {p: (self.root / p).read_bytes() for p in self.evidence_paths}
        for role, relative in authority.RELEASE_ROLES.items():
            with self.subTest(role=role):
                result = authority.authenticate_role(self.root, role, relative)
                self.assertNotEqual(result["historical"], result["current"])
                self.assertEqual(result["current"], authority.sha256((self.root / relative).read_bytes()))
        self.assertEqual(self.builder()["historical"], CURRENT_BUILD_HASH)
        self.assertEqual({p: (self.root / p).read_bytes() for p in self.evidence_paths}, before)

    def test_one_byte_mutation_of_each_current_role_is_rejected(self):
        for role, relative in authority.RELEASE_ROLES.items():
            with self.subTest(role=role):
                path = self.root / relative
                data = path.read_bytes()
                try:
                    path.write_bytes(bytes([data[0] ^ 1]) + data[1:])
                    with self.assertRaises(ValueError):
                        authority.authenticate_role(self.root, role, relative)
                finally:
                    path.write_bytes(data)

    def test_right_builder_path_with_wrong_tool_bytes_is_rejected(self):
        (self.root / "tools/build_release.py").write_bytes(
            (self.root / "tools/release_archive.py").read_bytes())
        with self.assertRaises(ValueError):
            self.builder()

    def test_wrong_builder_role_or_logical_path_is_rejected(self):
        for role, relative in (
            ("current_release_archiver", "tools/build_release.py"),
            ("sosa_2023_release_builder", "tools/build_release.py"),
            ("current_release_builder", "tools/release_archive.py"),
        ):
            with self.subTest(role=role, path=relative):
                with self.assertRaisesRegex(ValueError, "role/path mismatch"):
                    authority.authenticate_role(self.root, role, relative)

    def test_forged_current_evidence_cannot_self_authorize_builder(self):
        relative = "tools/build_release.py"
        replacement = b"forged current builder"
        (self.root / relative).write_bytes(replacement)
        prior_path = self.root / self.record["provenance"]["path"]
        prior = json.loads(prior_path.read_bytes())
        prior["repository_hashes"][relative] = authority.sha256(replacement)
        prior_path.write_bytes(authority.retained._canonical(prior))
        self.record["provenance"].update(sha256=authority.sha256(prior_path.read_bytes()), bytes=prior_path.stat().st_size)
        self.record["current_sha256"][relative] = authority.sha256(replacement)
        (self.root / authority.CURRENT_AUTHORITY_FIXTURE).write_bytes(authority.retained._canonical(self.record))
        with self.assertRaises(ValueError):
            self.builder()

    def test_missing_current_authority_or_followup_evidence_is_rejected(self):
        for relative in self.evidence_paths:
            with self.subTest(path=relative):
                path = self.root / relative
                data = path.read_bytes()
                try:
                    path.unlink()
                    with self.assertRaises(ValueError):
                        authority.authenticate_role(self.root, "current_release_rehearsal_regressions", "tests/test_release_rehearsal.py")
                finally:
                    path.write_bytes(data)

    def test_tampered_historical_builder_authority_is_rejected(self):
        with patch.dict(authority.CURRENT_AUTHORITY_HASHES, {"tools/build_release.py": "0" * 64}):
            with self.assertRaisesRegex(ValueError, "historical release role hash mismatch"):
                self.builder()

    def test_unrelated_task_evidence_cannot_authorize_builder(self):
        # A valid receipt from another authorized task is not this builder's
        # implementation approval, even if placed at the expected filename.
        (self.root / self.record["provenance"]["path"]).write_bytes(
            (self.root / authority.FOLLOWUP_RESULT["path"]).read_bytes())
        with self.assertRaises(ValueError):
            self.builder()

    def test_unauthorized_descendant_builder_is_rejected(self):
        path = self.root / "tools/build_release.py"
        path.write_bytes(path.read_bytes() + b"\n# later unauthenticated implementation\n")
        with self.assertRaises(ValueError):
            self.builder()

    def test_historical_builder_validates_when_current_builder_is_absent(self):
        (self.root / "tools/build_release.py").unlink()
        self.assertEqual(authority.historical_role_authority(
            self.root, "current_release_builder", "tools/build_release.py"), CURRENT_BUILD_HASH)
        with self.assertRaises(ValueError):
            self.builder()

    def test_wrong_followup_predecessor_cannot_be_self_resealed(self):
        path = self.root / self.record["provenance"]["path"]
        prior = json.loads(path.read_bytes())
        prior["repository_hashes"]["tests/test_release_rehearsal.py"] = "0" * 64
        path.write_bytes(authority.retained._canonical(prior))
        with self.assertRaises(ValueError):
            authority.authenticate_role(self.root, "current_release_rehearsal_regressions", "tests/test_release_rehearsal.py")

    def test_correct_builder_bytes_via_symlink_are_rejected(self):
        path = self.root / "tools/build_release.py"
        path.unlink()
        path.symlink_to(REPO_ROOT / "tools/build_release.py")
        with self.assertRaises(ValueError):
            self.builder()


if __name__ == "__main__":
    unittest.main()
