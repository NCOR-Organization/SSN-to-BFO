#!/usr/bin/env python3
"""Authenticated current release expectations and historical contract isolation."""

from __future__ import annotations

import dataclasses
import hashlib
import io
import json
import shutil
import sys
import tarfile
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_release as build  # noqa: E402
import current_semantic_generation as generation  # noqa: E402
import release_archive as archive  # noqa: E402
import release_context as context  # noqa: E402
import release_manifest as manifest  # noqa: E402
from tests.test_release_manifest import valid_manifest  # noqa: E402
from tests.test_release_rendering import (  # noqa: E402
    FORMAL_HASHES as HISTORICAL_FORMAL_HASHES,
    SYNTHETIC_CONTEXT,
    artifact_bytes,
    build_formal_products,
)


NOTES_RELATIVE = "release-notes/SYNTHETIC-2099-01-02.md"
TRANSITION_RELATIVE = (
    "reports/current-semantic-workbook/transitions/"
    "58481ff2-4e56-4931-a3d4-383357b16561.json"
)
# These formal identities were established independently before the release
# contract repair, for this explicit synthetic release context.
CURRENT_FORMAL_HASHES = {
    **HISTORICAL_FORMAL_HASHES,
    "integrated": "9d307178cf479087765608bba5dc6ef1983125631f32839fd0dc77764b6142f2",
    "cco_extension": "2a9dc45056d5186c5cf8c7924b8e7ed96f590f9a255dda2d8af727f96dd2d235",
}
CURRENT_COUNTS = {
    # Logical triples, total triples, direct axioms, project-closure axioms,
    # fixed reasoning closure, profile graph, declaration completions.
    "integrated": (1053, 1068, 100, 100, 15858, 15862, 4),
    "alignment_core": (53, 64, 29, 29, 1217, 1221, 4),
    "strict_bfo_mapping": (125, 137, 19, 48, 14994, 14998, 4),
    "cco_extension": (875, 887, 52, 100, 15880, 15884, 4),
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class ReleaseContractAuthenticationTests(unittest.TestCase):
    """Mutations affect isolated copies, never repository or custody files."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="release-contract-auth-")
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.repository = self.parent / "repository"
        shutil.copytree(
            REPO_ROOT,
            self.repository,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "*.pyc", "*.pyo", ".pytest_cache"
            ),
        )
        # Only immutable Git object reads use the original repository. All
        # mutations below are made to copied working files.
        (self.repository / ".git").symlink_to(
            REPO_ROOT / ".git", target_is_directory=True
        )
        self.output = self.parent / SYNTHETIC_CONTEXT.release_identifier
        with context.authenticated_release_expectations(
            self.repository, SYNTHETIC_CONTEXT
        ) as expectations:
            self.assertIsNotNone(expectations)
            self.assertEqual(
                expectations.product("integrated").sha256,
                CURRENT_FORMAL_HASHES["integrated"],
            )

    def assert_preflight_rejects_before_assembly(self) -> None:
        with mock.patch.object(build, "assemble_release_package") as assemble:
            with self.assertRaises(ValueError):
                build.build_release_package(
                    SYNTHETIC_CONTEXT,
                    self.repository / NOTES_RELATIVE,
                    self.output,
                    self.repository,
                )
            assemble.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_broken_semantic_transition_fails_before_packaging(self) -> None:
        path = self.repository / TRANSITION_RELATIVE
        record = json.loads(path.read_bytes())
        record["new_workbook_sha256"] = "0" * 64
        path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
        self.assert_preflight_rejects_before_assembly()

    def test_unauthorized_development_product_fails_before_packaging(self) -> None:
        path = self.repository / "SSN2BFO.ttl"
        path.write_bytes(path.read_bytes() + b"\n# unauthorized product mutation\n")
        self.assert_preflight_rejects_before_assembly()


class ReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Retain a raw historical fixture before entering any current context.
        cls.historical_products = artifact_bytes(build_formal_products()[-1])
        cls.historical_manifest = valid_manifest()
        cls.historical_document = manifest.manifest_document(cls.historical_manifest)
        cls.temporary = tempfile.TemporaryDirectory(prefix="release-contract-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.package = Path(cls.temporary.name) / SYNTHETIC_CONTEXT.release_identifier
        with context.authenticated_release_expectations(
            REPO_ROOT, SYNTHETIC_CONTEXT
        ) as expectations:
            if expectations is None:
                raise AssertionError("maintained current state lacks release expectations")
            cls.expectations = expectations
            # The real builder performs independent reasoning and reconstruction;
            # no reasoning, count, product, or package validator is mocked.
            cls.result = build.build_release_package(
                SYNTHETIC_CONTEXT,
                REPO_ROOT / NOTES_RELATIVE,
                cls.package,
                REPO_ROOT,
            )
            cls.current_manifest = manifest.load_and_validate_release_manifest(
                cls.package / "manifest.json"
            )
        cls.current_bytes = (cls.package / "manifest.json").read_bytes()
        cls.current_document = json.loads(cls.current_bytes)

    def test_authorized_current_expectations_are_exact_and_frozen(self) -> None:
        self.assertEqual(self.expectations.context, SYNTHETIC_CONTEXT)
        self.assertEqual(Path(self.expectations.repository_root), REPO_ROOT.resolve())
        self.assertEqual(
            tuple(product.key for product in self.expectations.products),
            manifest.PRODUCT_ORDER,
        )
        self.assertEqual(
            self.expectations.fixed_closure_counts,
            tuple((key, CURRENT_COUNTS[key][4]) for key in manifest.PRODUCT_ORDER),
        )
        for key in manifest.PRODUCT_ORDER:
            with self.subTest(product=key):
                product = self.expectations.product(key)
                self.assertEqual(product.sha256, CURRENT_FORMAL_HASHES[key])
                self.assertEqual(sha256(product.serialized_bytes), product.sha256)
                self.assertEqual(product.byte_size, len(product.serialized_bytes))
                self.assertEqual(
                    (self.package / build.PRODUCT_PACKAGE_PATHS[key]).read_bytes(),
                    product.serialized_bytes,
                )
                self.assertEqual(
                    (
                        product.logical_triple_count,
                        product.total_triple_count,
                        product.direct_governed_axiom_count,
                        product.governed_closure_axiom_count,
                        product.fixed_closure_triple_count,
                        product.profile_triple_count,
                        product.profile_declaration_completion_count,
                    ),
                    CURRENT_COUNTS[key],
                )
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    product.sha256 = "0" * 64
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.expectations.context = None
        for result in self.current_manifest.validation.hermit_results:
            with self.subTest(reasoning=result.product_key):
                self.assertEqual(result.status, "PASS")
                self.assertEqual(result.return_code, 0)
                self.assertTrue(result.reasoned_output_produced)
                self.assertEqual(result.named_unsatisfiable_class_count, 0)
                self.assertEqual(result.owl_nothing_equivalent_named_class_count, 0)
                self.assertEqual(
                    result.fixed_closure_triple_count,
                    CURRENT_COUNTS[result.product_key][4],
                )

    def test_historical_contract_and_raw_rejection_resume_after_context(self) -> None:
        self.assertEqual(
            manifest.FORMAL_FIXED_CLOSURE_TRIPLE_COUNTS,
            (("integrated", 15907), ("alignment_core", 1217),
             ("strict_bfo_mapping", 14994), ("cco_extension", 15929)),
        )
        self.assertEqual(
            manifest.validate_release_manifest_document(self.historical_document), ()
        )
        self.assertIn(
            "FIXED_CLOSURE_TRIPLE_COUNT_MISMATCH",
            {issue.code for issue in manifest.validate_release_manifest_document(
                self.current_document
            )},
        )
        with context.authenticated_release_expectations(REPO_ROOT, SYNTHETIC_CONTEXT):
            self.assertEqual(
                manifest.validate_release_manifest_document(self.current_document), ()
            )
            self.assertTrue(
                manifest.validate_release_manifest_document(self.historical_document)
            )
        self.assertEqual(
            manifest.validate_release_manifest_document(self.historical_document), ()
        )
        with self.assertRaises(manifest.ReleaseManifestError):
            manifest.load_and_validate_release_manifest(self.current_bytes)

    def test_nested_historical_context_restores_raw_generation_guards(self) -> None:
        self.assertEqual(generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103), 103)
        with tempfile.TemporaryDirectory(prefix="release-contract-historical-") as temporary:
            # Absence of a semantic archive selects the historical contract.
            # The renderer below still uses the accepted Git-pinned fixture.
            historical_root = Path(temporary)
            with context.authenticated_release_expectations(
                REPO_ROOT, SYNTHETIC_CONTEXT
            ) as current:
                self.assertIsNotNone(current)
                self.assertEqual(
                    generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103), 100
                )
                with context.authenticated_release_expectations(
                    historical_root, SYNTHETIC_CONTEXT
                ) as historical:
                    self.assertIsNone(historical)
                    self.assertIsNone(context.active_release_expectations())
                    self.assertEqual(
                        generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103),
                        103,
                    )
                    self.assertEqual(
                        artifact_bytes(build_formal_products()[-1]),
                        self.historical_products,
                    )
                    self.assertEqual(
                        manifest.validate_release_manifest_document(
                            self.historical_document
                        ),
                        (),
                    )
                self.assertIs(context.active_release_expectations(), current)
                self.assertEqual(
                    generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103), 100
                )
                self.assertEqual(
                    manifest.validate_release_manifest_document(self.current_document),
                    (),
                )
        self.assertIsNone(context.active_release_expectations())
        self.assertEqual(generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103), 103)

    def test_post_context_failure_cleans_only_its_published_directory(self) -> None:
        for replace_published_directory in (False, True):
            with self.subTest(replaced=replace_published_directory):
                with tempfile.TemporaryDirectory(prefix="release-contract-cleanup-") as temporary:
                    parent = Path(temporary)
                    output = parent / SYNTHETIC_CONTEXT.release_identifier
                    moved = parent / "moved-publication"

                    def publish_for_cleanup_boundary(
                        release_context, notes_source, destination, repository_root
                    ):
                        self.assertEqual(Path(destination), output)
                        output.mkdir()
                        (output / "owned").write_bytes(b"newly published package\n")
                        return dataclasses.replace(self.result, output_dir=output)

                    @contextmanager
                    def fail_fingerprint_on_exit(repository_root, release_context):
                        yield None
                        if replace_published_directory:
                            # A different directory appearing at the same path
                            # must never be deleted as if it were our publication.
                            output.rename(moved)
                            output.mkdir()
                            (output / "foreign").write_bytes(b"preserve replacement\n")
                        raise ValueError(
                            "release inputs changed after authenticated build/validation"
                        )

                    # These mocks isolate the exceptional cleanup boundary;
                    # successful package tests above use the real full builder.
                    with mock.patch.object(
                        build, "_build_release_package", side_effect=publish_for_cleanup_boundary
                    ) as inner, mock.patch.object(
                        build, "authenticated_release_expectations",
                        side_effect=fail_fingerprint_on_exit,
                    ):
                        with self.assertRaisesRegex(
                            ValueError, "release inputs changed after authenticated"
                        ):
                            build.build_release_package(
                                SYNTHETIC_CONTEXT,
                                REPO_ROOT / NOTES_RELATIVE,
                                output,
                                REPO_ROOT,
                            )
                        inner.assert_called_once()
                    if replace_published_directory:
                        self.assertEqual(
                            (output / "foreign").read_bytes(), b"preserve replacement\n"
                        )
                        self.assertEqual(
                            (moved / "owned").read_bytes(), b"newly published package\n"
                        )
                    else:
                        self.assertFalse(output.exists())

    def test_schema_valid_wrong_closure_counts_fail_current_semantics(self) -> None:
        with context.authenticated_release_expectations(REPO_ROOT, SYNTHETIC_CONTEXT):
            self.assertEqual(
                manifest.validate_release_manifest_document(self.current_document), ()
            )
            for index, key in enumerate(manifest.PRODUCT_ORDER):
                with self.subTest(product=key):
                    document = json.loads(self.current_bytes)
                    document["validation"]["hermit_results"][index][
                        "fixed_closure_triple_count"
                    ] = 999
                    self.assertEqual(
                        manifest.validate_release_manifest_document(
                            document, semantic=False
                        ),
                        (),
                    )
                    self.assertIn(
                        "FIXED_CLOSURE_TRIPLE_COUNT_MISMATCH",
                        {issue.code for issue in
                         manifest.validate_release_manifest_document(document)},
                    )

    def test_wrong_formal_product_hash_fails_current_semantics(self) -> None:
        with context.authenticated_release_expectations(REPO_ROOT, SYNTHETIC_CONTEXT):
            self.assertEqual(
                manifest.validate_release_manifest_document(self.current_document), ()
            )
            for index, key in enumerate(manifest.PRODUCT_ORDER):
                with self.subTest(product=key):
                    document = json.loads(self.current_bytes)
                    document["products"][index]["sha256"] = "0" * 64
                    self.assertEqual(
                        manifest.validate_release_manifest_document(
                            document, semantic=False
                        ),
                        (),
                    )
                    self.assertTrue(
                        manifest.validate_release_manifest_document(document)
                    )
                    with self.assertRaises(manifest.ReleaseManifestError):
                        manifest.load_and_validate_release_manifest(
                            manifest.canonical_manifest_bytes(document)
                        )

    def test_core_and_strict_members_preserve_historical_bytes(self) -> None:
        self.assertEqual(
            {key: sha256(value) for key, value in self.historical_products.items()},
            HISTORICAL_FORMAL_HASHES,
        )
        for key in ("alignment_core", "strict_bfo_mapping"):
            with self.subTest(product=key):
                self.assertEqual(
                    (self.package / build.PRODUCT_PACKAGE_PATHS[key]).read_bytes(),
                    self.historical_products[key],
                )

    def test_manifest_checksums_and_archive_bind_current_product_bytes(self) -> None:
        included = {value.path: value for value in self.current_manifest.included_files}
        products = {value.key: value for value in self.current_manifest.products}
        checksum_lines = (self.package / "SHA256SUMS").read_text(encoding="ascii").splitlines()
        checksums = {line[66:]: line[:64] for line in checksum_lines}
        self.assertEqual(tuple(checksums), build.CHECKSUM_PATHS)
        self.assertEqual(checksums["manifest.json"], sha256(self.current_bytes))
        self.assertEqual(self.result.manifest_sha256, sha256(self.current_bytes))
        for key in manifest.PRODUCT_ORDER:
            with self.subTest(product=key):
                expected = self.expectations.product(key)
                path = build.PRODUCT_PACKAGE_PATHS[key]
                self.assertEqual(products[key].sha256, expected.sha256)
                self.assertEqual(products[key].byte_size, expected.byte_size)
                self.assertEqual(included[path].sha256, expected.sha256)
                self.assertEqual(included[path].byte_size, expected.byte_size)
                self.assertEqual(checksums[path], expected.sha256)
        archive_bytes = archive.canonical_archive_bytes(
            self.package, SYNTHETIC_CONTEXT.release_identifier
        )
        self.assertEqual(
            archive_bytes,
            archive.canonical_archive_bytes(
                self.package, SYNTHETIC_CONTEXT.release_identifier
            ),
        )
        prefix = archive.archive_top_level(SYNTHETIC_CONTEXT.release_identifier) + "/"
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as package_archive:
            regular = [member for member in package_archive.getmembers() if member.isfile()]
            self.assertEqual(
                {member.name.removeprefix(prefix) for member in regular},
                set(build.PACKAGE_FILE_PATHS),
            )
            for member in regular:
                path = member.name.removeprefix(prefix)
                stream = package_archive.extractfile(member)
                self.assertIsNotNone(stream)
                self.assertEqual(stream.read(), (self.package / path).read_bytes())
                self.assertEqual(member.size, (self.package / path).stat().st_size)
        self.assertEqual(
            archive.canonical_sidecar_bytes(
                SYNTHETIC_CONTEXT.release_identifier, archive_bytes
            ),
            (sha256(archive_bytes) + "  " + archive.archive_filename(
                SYNTHETIC_CONTEXT.release_identifier
            ) + "\n").encode("ascii"),
        )


if __name__ == "__main__":
    unittest.main()
