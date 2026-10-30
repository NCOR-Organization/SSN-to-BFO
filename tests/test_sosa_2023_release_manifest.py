#!/usr/bin/env python3
"""SOSA-2023 release-manifest evidence-model regressions."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import sosa_2023_release_manifest as manifest  # noqa: E402
import current_retained_evidence as retained  # noqa: E402


HASH = "a" * 64
SYNTHETIC_DATE = "2099-01-02"
SYNTHETIC_COMMIT = "0123456789abcdef0123456789abcdef01234567"

FORMAL_HASHES = {
    "integrated":
        "539c07541bf20e5305fa675fa34b54899fe2bd3be31cc33c865d367b3e7dbe43",
    "strict_bfo_mapping":
        "8eadb56c78b215fb7b623dede6071b6b412e2ed7eb2a85e694a372310a700125",
    "cco_extension":
        "d3b6f3324fa2b8931760c1d743e37984d1198a124abc7c7bdcf2195370428f3d",
    "ro_mapping":
        "faba756dc6480c2088cc6ad3e514524736130f90365f1ab7e40c3d909877ca69",
}

from tests.release_authority_fixture import (  # noqa: E402
    CURRENT_AUTHORITY_HASHES, HISTORICAL_AUTHORITY_COMMIT,
    CURRENT_AUTHORITY_FIXTURE, CURRENT_AUTHORITY_FIXTURE_SHA256,
    approved_current_release_authority, current_release_authority,
    historical_release_authority, sha256,
)


def file_record(
    key: str,
    source_path: str,
    package_path: str | None,
) -> manifest.ReleaseManifestInput:
    source = REPO_ROOT / source_path
    content = source.read_bytes()

    return manifest.ReleaseManifestInput(
        key=key,
        source_path=source_path,
        package_path=package_path,
        sha256=sha256(content),
        byte_size=len(content),
    )


def valid_manifest() -> manifest.ReleaseManifest:
    inputs = []

    for key, source_path, package_path in manifest.INPUT_POLICIES:
        if key == "release_notes":
            source_path = "release-notes/SYNTHETIC-2099-01-02.md"

        assert source_path is not None

        inputs.append(
            file_record(
                key,
                source_path,
                package_path,
            )
        )

    products = tuple(
        manifest.ReleaseManifestProduct(
            key=key,
            path=manifest.PRODUCT_PACKAGE_PATHS[key],
            stable_ontology_iri=(
                manifest.PRODUCT_STABLE_ONTOLOGY_IRIS[key]
            ),
            version_iri=manifest.expected_version_iri(
                key,
                SYNTHETIC_DATE,
            ),
            imports=manifest.expected_product_imports(
                key,
                SYNTHETIC_DATE,
            ),
            sha256=FORMAL_HASHES[key],
            **manifest.PRODUCT_STATIC_EVIDENCE[key],
        )
        for key in manifest.PRODUCT_ORDER
    )

    dependencies = tuple(
        manifest.ReleaseManifestDependency(
            key=key,
            role=role,
            path=source_path,
            ontology_iri=ontology_iri,
            version_iri=None,
            sha256=sha256(
                (REPO_ROOT / source_path).read_bytes()
            ),
            byte_size=(
                REPO_ROOT / source_path
            ).stat().st_size,
        )
        for (
            key,
            role,
            source_path,
            ontology_iri,
        ) in manifest.DEPENDENCY_POLICIES
    )

    environment = manifest.ReleaseManifestValidationEnvironment(
        python_implementation="CPython",
        python_version="3.12.4",
        java_vendor="Fixture Java Vendor",
        java_version="22.0.2",
        java_vm_name="Fixture Java VM",
        robot_artifact="https://example.invalid/robot.jar",
        robot_version="1.9.7",
        robot_sha256=HASH,
        toolchain_path="config/validation-toolchain.env",
        toolchain_sha256=HASH,
        requirements_path="requirements/validation.txt",
        requirements_sha256=HASH,
    )

    validation = manifest.ReleaseManifestValidation(
        strict_turtle_parsing=True,
        formal_metadata_validation=True,
        serialized_header_validation=True,
        governed_axiom_reconciliation=True,
        import_graph_validation=True,
        catalog_validation=True,
        checksum_validation=True,
        development_artifact_nonmutation=True,
        deterministic_package_rebuild=True,
        hermit_results=tuple(
            manifest.ReleaseManifestHermitResult(
                product_key=key,
                status="PASS",
                fixed_closure_triple_count=count,
                return_code=0,
                reasoned_output_produced=True,
                named_unsatisfiable_class_count=0,
                owl_nothing_equivalent_named_class_count=0,
            )
            for key, count in (
                manifest.FORMAL_FIXED_CLOSURE_TRIPLE_COUNTS
            )
        ),
    )

    included_files = tuple(
        manifest.ReleaseManifestIncludedFile(
            path=value,
            role="governed SOSA-2023 formal package member",
            sha256=HASH,
            byte_size=1,
        )
        for value in manifest.INCLUDED_FILE_PATH_ORDER
    )

    return manifest.build_release_manifest(
        release_identifier=SYNTHETIC_DATE,
        release_date=SYNTHETIC_DATE,
        git_tag="v" + SYNTHETIC_DATE,
        source_commit=SYNTHETIC_COMMIT,
        repository_iri=manifest.REPOSITORY_IRI,
        inputs=tuple(inputs),
        product_order=manifest.PRODUCT_ORDER,
        products=products,
        dependencies=dependencies,
        validation_environment=environment,
        validation=validation,
        included_files=included_files,
    )


class Sosa2023ReleaseManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = valid_manifest()
        cls.serialized = manifest.canonical_manifest_bytes(
            cls.value
        )
        cls.document = json.loads(cls.serialized)
        cls.schema = json.loads(
            (
                REPO_ROOT
                / "config/sosa-2023-release-manifest-schema-v1.json"
            ).read_text(encoding="utf-8")
        )

    def test_exact_track_inventory_and_closure_authority(self) -> None:
        self.assertEqual(
            manifest.PRODUCT_ORDER,
            (
                "integrated",
                "strict_bfo_mapping",
                "cco_extension",
                "ro_mapping",
            ),
        )
        self.assertEqual(
            manifest.FORMAL_FIXED_CLOSURE_TRIPLE_COUNTS,
            (
                ("integrated", 15243),
                ("strict_bfo_mapping", 15120),
                ("cco_extension", 15254),
                ("ro_mapping", 12864),
            ),
        )
        self.assertEqual(
            manifest.PRODUCT_IMPORT_COUNTS,
            {
                "integrated": 4,
                "strict_bfo_mapping": 0,
                "cco_extension": 1,
                "ro_mapping": 0,
            },
        )

    def test_schema_and_python_authorities_are_synchronized(self) -> None:
        self.assertEqual(manifest.SCHEMA_VERSION, 1)
        self.assertEqual(
            self.schema["properties"]["schema_version"],
            {"const": 1},
        )
        self.assertEqual(
            tuple(
                self.schema["properties"][
                    "product_order"
                ]["const"]
            ),
            manifest.PRODUCT_ORDER,
        )
        self.assertEqual(
            tuple(
                self.schema["$defs"]["product"][
                    "properties"
                ]["key"]["enum"]
            ),
            manifest.PRODUCT_ORDER,
        )
        self.assertEqual(
            tuple(
                self.schema["$defs"]["hermitResult"][
                    "properties"
                ]["product_key"]["enum"]
            ),
            manifest.PRODUCT_ORDER,
        )

        expected_arrays = (
            (
                "inputs",
                manifest.INPUT_KEY_ORDER,
                "key",
            ),
            (
                "products",
                manifest.PRODUCT_ORDER,
                "key",
            ),
            (
                "dependencies",
                manifest.DEPENDENCY_KEY_ORDER,
                "key",
            ),
            (
                "included_files",
                manifest.INCLUDED_FILE_PATH_ORDER,
                "path",
            ),
        )

        for field, expected, identity_field in expected_arrays:
            value = self.schema["properties"][field]

            with self.subTest(field=field):
                self.assertEqual(
                    (
                        value["minItems"],
                        value["maxItems"],
                    ),
                    (
                        len(expected),
                        len(expected),
                    ),
                )
                self.assertFalse(value["items"])
                self.assertEqual(
                    tuple(
                        item["allOf"][1]["properties"][
                            identity_field
                        ]["const"]
                        for item in value["prefixItems"]
                    ),
                    expected,
                )

        hermit = self.schema["$defs"]["validation"][
            "properties"
        ]["hermit_results"]

        self.assertEqual(
            (
                hermit["minItems"],
                hermit["maxItems"],
            ),
            (4, 4),
        )

        self.assertEqual(
            tuple(
                (
                    item["allOf"][1]["properties"][
                        "product_key"
                    ]["const"],
                    item["allOf"][1]["properties"][
                        "fixed_closure_triple_count"
                    ]["const"],
                )
                for item in hermit["prefixItems"]
            ),
            manifest.FORMAL_FIXED_CLOSURE_TRIPLE_COUNTS,
        )

    def test_valid_manifest_round_trips_canonically(self) -> None:
        self.assertEqual(
            manifest.validate_release_manifest_document(
                self.document
            ),
            (),
        )
        loaded = manifest.load_and_validate_release_manifest(
            self.serialized
        )
        self.assertEqual(loaded, self.value)
        self.assertEqual(
            manifest.canonical_manifest_bytes(loaded),
            self.serialized,
        )
        self.assertTrue(
            self.serialized.endswith(b"\n")
        )
        self.assertFalse(
            self.serialized.endswith(b"\n\n")
        )

    def test_reordered_models_have_identical_canonical_bytes(self) -> None:
        reordered = replace(
            self.value,
            inputs=tuple(reversed(self.value.inputs)),
            products=tuple(reversed(self.value.products)),
            dependencies=tuple(
                reversed(self.value.dependencies)
            ),
            validation=replace(
                self.value.validation,
                hermit_results=tuple(
                    reversed(
                        self.value.validation.hermit_results
                    )
                ),
            ),
            included_files=tuple(
                reversed(self.value.included_files)
            ),
        )

        self.assertEqual(
            manifest.canonical_manifest_bytes(reordered),
            self.serialized,
        )

    def test_synthetic_formal_product_evidence_is_exact(self) -> None:
        observed = {
            value.key: value
            for value in self.value.products
        }

        for key in manifest.PRODUCT_ORDER:
            product = observed[key]

            self.assertEqual(
                product.sha256,
                FORMAL_HASHES[key],
            )
            self.assertEqual(
                product.byte_size,
                manifest.PRODUCT_STATIC_EVIDENCE[
                    key
                ]["byte_size"],
            )
            self.assertEqual(
                product.version_iri,
                manifest.expected_version_iri(
                    key,
                    SYNTHETIC_DATE,
                ),
            )
            self.assertEqual(
                product.imports,
                manifest.expected_product_imports(
                    key,
                    SYNTHETIC_DATE,
                ),
            )

            formal_text = "\n".join(
                (
                    product.path,
                    product.stable_ontology_iri,
                    product.version_iri,
                    *product.imports,
                )
            )

            self.assertNotIn(
                "sosa-next",
                formal_text,
            )
            self.assertNotIn(
                "/development/",
                formal_text,
            )

    def test_all_source_and_development_evidence_is_represented(self) -> None:
        records = {
            value.key: value
            for value in self.value.inputs
        }

        self.assertEqual(
            tuple(records),
            manifest.INPUT_KEY_ORDER,
        )

        for key, source_path, package_path in (
            manifest.INPUT_POLICIES
        ):
            record = records[key]

            if key == "release_notes":
                source_path = (
                    "release-notes/"
                    "SYNTHETIC-2099-01-02.md"
                )

            assert source_path is not None

            content = (
                REPO_ROOT / source_path
            ).read_bytes()

            self.assertEqual(
                record.source_path,
                source_path,
            )
            self.assertEqual(
                record.package_path,
                package_path,
            )
            self.assertEqual(
                record.sha256,
                sha256(content),
            )
            self.assertEqual(
                record.byte_size,
                len(content),
            )

        pinned_keys = {
            "pinned_sosa",
            "pinned_sosa_common",
            "pinned_sosa_observation",
            "pinned_sosa_actuation",
            "pinned_sosa_sampling",
            "pinned_sosa_deprecated",
            "pinned_sosa_system",
            "pinned_sample_relations",
            "source_declaration_overlay",
        }

        self.assertTrue(
            pinned_keys <= set(records)
        )

    def test_dependency_ontology_identities_match_pinned_files(self) -> None:
        from rdflib import Graph, OWL, RDF, URIRef

        for (
            key,
            _role,
            source_path,
            expected_ontology_iri,
        ) in manifest.DEPENDENCY_POLICIES:
            with self.subTest(dependency=key):
                graph = Graph().parse(
                    REPO_ROOT / source_path,
                    format=(
                        "xml"
                        if key == "relations_ontology"
                        else "turtle"
                    ),
                )

                observed = tuple(
                    sorted(
                        str(value)
                        for value in graph.subjects(
                            RDF.type,
                            OWL.Ontology,
                        )
                        if isinstance(value, URIRef)
                    )
                )

                self.assertEqual(
                    observed,
                    (expected_ontology_iri,),
                )


    def test_package_engine_modules_are_governed_inputs(self) -> None:
        records = {
            value.key: value
            for value in self.value.inputs
        }

        expected = (
            (
                "module_sosa_2023_release_runtime",
                "tools/sosa_2023_release_runtime.py",
            ),
            (
                "module_sosa_2023_build_release",
                "tools/sosa_2023_build_release.py",
            ),
            (
                "module_sosa_2023_check_release",
                "tools/sosa_2023_check_release.py",
            ),
        )

        self.assertEqual(
            len(self.value.inputs),
            37,
        )

        for key, source_path in expected:
            with self.subTest(input=key):
                record = records[key]
                content = (
                    REPO_ROOT / source_path
                ).read_bytes()

                self.assertEqual(
                    record.source_path,
                    source_path,
                )
                self.assertIsNone(
                    record.package_path,
                )
                self.assertEqual(
                    record.sha256,
                    sha256(content),
                )
                self.assertEqual(
                    record.byte_size,
                    len(content),
                )

                self.assertNotIn(
                    source_path,
                    manifest.INCLUDED_FILE_PATH_ORDER,
                )


    def test_exact_policy_mutations_are_rejected(self) -> None:
        variants = []

        wrong_input = json.loads(self.serialized)
        wrong_input["inputs"][0]["source_path"] = (
            "mappings/wrong.xlsx"
        )
        variants.append(
            (
                "wrong input",
                wrong_input,
                "INPUT_SOURCE_POLICY",
            )
        )

        wrong_product_path = json.loads(self.serialized)
        wrong_product_path["products"][0]["path"] = (
            "sosa-next/sosa-integrated.ttl"
        )
        variants.append(
            (
                "wrong product path",
                wrong_product_path,
                "PRODUCT_PATH_POLICY",
            )
        )

        wrong_stable = json.loads(self.serialized)
        wrong_stable["products"][0][
            "stable_ontology_iri"
        ] = "http://www.sks.ai/SSN2BFO/development/sosa-next/integrated"
        variants.append(
            (
                "wrong stable IRI",
                wrong_stable,
                "PRODUCT_STABLE_IRI_POLICY",
            )
        )

        wrong_version = json.loads(self.serialized)
        wrong_version["products"][1]["version_iri"] = (
            "http://www.sks.ai/SSN2BFO/releases/"
            "2099-01-02/wrong"
        )
        variants.append(
            (
                "wrong version IRI",
                wrong_version,
                "PRODUCT_VERSION_IRI_POLICY",
            )
        )

        wrong_import = json.loads(self.serialized)
        wrong_import["products"][2]["imports"] = []
        wrong_import["products"][2]["import_count"] = 0
        variants.append(
            (
                "wrong import",
                wrong_import,
                "PRODUCT_IMPORT_POLICY",
            )
        )

        wrong_count = json.loads(self.serialized)
        wrong_count["products"][0][
            "logical_triple_count"
        ] = 274
        variants.append(
            (
                "wrong evidence",
                wrong_count,
                "PRODUCT_EVIDENCE_POLICY",
            )
        )

        wrong_dependency = json.loads(self.serialized)
        wrong_dependency["dependencies"][0]["path"] = (
            "imports/wrong.ttl"
        )
        variants.append(
            (
                "wrong dependency",
                wrong_dependency,
                "DEPENDENCY_POLICY",
            )
        )

        wrong_included = json.loads(self.serialized)
        wrong_included["included_files"][2]["path"] = (
            "sosa-next/catalog-v001.xml"
        )
        variants.append(
            (
                "development package path",
                wrong_included,
                "DEVELOPMENT_IDENTITY_LEAK",
            )
        )

        for label, document, expected_code in variants:
            with self.subTest(label=label):
                codes = {
                    value.code
                    for value in (
                        manifest
                        .validate_release_manifest_document(
                            document
                        )
                    )
                }
                self.assertIn(
                    expected_code,
                    codes,
                )

    def test_reasoning_evidence_is_product_specific_and_fixed(self) -> None:
        observed = tuple(
            (
                value.product_key,
                value.fixed_closure_triple_count,
                value.return_code,
                value.reasoned_output_produced,
                value.named_unsatisfiable_class_count,
            )
            for value in self.value.validation.hermit_results
        )

        self.assertEqual(
            observed,
            (
                (
                    "integrated",
                    15243,
                    0,
                    True,
                    0,
                ),
                (
                    "strict_bfo_mapping",
                    15120,
                    0,
                    True,
                    0,
                ),
                (
                    "cco_extension",
                    15254,
                    0,
                    True,
                    0,
                ),
                (
                    "ro_mapping",
                    12864,
                    0,
                    True,
                    0,
                ),
            ),
        )

        changed = json.loads(self.serialized)
        changed["validation"]["hermit_results"][2][
            "fixed_closure_triple_count"
        ] = 15140

        codes = {
            value.code
            for value in (
                manifest.validate_release_manifest_document(
                    changed
                )
            )
        }

        self.assertIn(
            "FIXED_CLOSURE_TRIPLE_COUNT_MISMATCH",
            codes,
        )

    def test_included_files_are_formal_only_and_anti_circular(self) -> None:
        self.assertEqual(
            tuple(sorted(manifest.INCLUDED_FILE_PATH_ORDER)),
            manifest.INCLUDED_FILE_PATH_ORDER,
        )

        self.assertNotIn(
            "manifest.json",
            manifest.INCLUDED_FILE_PATH_ORDER,
        )
        self.assertNotIn(
            "SHA256SUMS",
            manifest.INCLUDED_FILE_PATH_ORDER,
        )

        for value in manifest.INCLUDED_FILE_PATH_ORDER:
            self.assertNotIn(
                "sosa-next",
                value,
            )

    def test_current_release_authorities_remain_byte_locked(self) -> None:
        historical_release_authority(REPO_ROOT)
        current = approved_current_release_authority(REPO_ROOT)
        for relative in CURRENT_AUTHORITY_HASHES:
            with self.subTest(relative=relative):
                selected = retained.resolve(REPO_ROOT, relative, current[relative], allow_retained=False)
                self.assertEqual(sha256(selected.read_bytes()), current[relative])

    def test_module_has_no_external_json_schema_dependency(self) -> None:
        source = (
            REPO_ROOT
            / "tools/sosa_2023_release_manifest.py"
        ).read_text(encoding="utf-8")

        package_name = "json" + "schema"

        self.assertNotIn(
            f"import {package_name}",
            source,
        )
        self.assertNotIn(
            f"from {package_name}",
            source,
        )


class CurrentReleaseAuthorityFixtureTests(unittest.TestCase):
    """Reject tampered current evidence without weakening the historical lock."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="release-authority-fixture-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        # Read trusted Git objects only. No fixture operation writes Git state.
        (self.root / ".git").symlink_to(REPO_ROOT / ".git", target_is_directory=True)
        self.record = json.loads((REPO_ROOT / CURRENT_AUTHORITY_FIXTURE).read_bytes())
        paths = {*CURRENT_AUTHORITY_HASHES, CURRENT_AUTHORITY_FIXTURE,
                 *(self.record[key]["path"] for key in ("authorization", "provenance"))}
        for relative in paths:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / relative, destination)

    def write_record(self) -> None:
        (self.root / CURRENT_AUTHORITY_FIXTURE).write_bytes(retained._canonical(self.record))

    def test_historical_and_current_authorities_validate_independently(self) -> None:
        historical = historical_release_authority(self.root)
        current = current_release_authority(self.root)
        self.assertEqual(set(current), set(historical))
        self.assertEqual(len(current), 7)
        self.assertTrue(all(current[p] != historical[p] for p in current))
        # Live changes cannot rewrite or invalidate the independent historical
        # object check; they must still fail the maintained-current check.
        (self.root / "tools/release_manifest.py").write_bytes(b"unapproved descendant")
        self.assertEqual(historical_release_authority(self.root), historical)
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_each_unauthorized_current_file_is_rejected(self) -> None:
        for relative in CURRENT_AUTHORITY_HASHES:
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"\n# unauthorized change\n")
                    with self.assertRaises(ValueError):
                        current_release_authority(self.root)
                finally:
                    path.write_bytes(original)

    def test_correct_filename_with_other_file_bytes_is_rejected(self) -> None:
        (self.root / "tools/build_release.py").write_bytes((self.root / "tools/check_release.py").read_bytes())
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_task_entry_hash_cannot_self_authorize_changed_bytes(self) -> None:
        relative = "tools/release_manifest.py"
        replacement = b"self-authorized replacement"
        (self.root / relative).write_bytes(replacement)
        prior_path = self.root / self.record["provenance"]["path"]
        prior = json.loads(prior_path.read_bytes())
        prior["repository_hashes"][relative] = sha256(replacement)
        prior_path.write_bytes(retained._canonical(prior))
        self.record["current_sha256"][relative] = sha256(replacement)
        self.record["provenance"].update(sha256=sha256(prior_path.read_bytes()), bytes=prior_path.stat().st_size)
        self.write_record()
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_wrong_predecessor_is_rejected(self) -> None:
        self.record["historical_predecessor"] = "0" * 40
        self.write_record()
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_missing_current_authority_or_required_evidence_is_rejected(self) -> None:
        # Model C requires reviewed current implementation evidence, not a
        # fictitious prepared/committed successor record.
        for relative in (CURRENT_AUTHORITY_FIXTURE, self.record["authorization"]["path"],
                         self.record["provenance"]["path"]):
            with self.subTest(relative=relative):
                path = self.root / relative
                data = path.read_bytes()
                try:
                    path.unlink()
                    with self.assertRaises(ValueError):
                        current_release_authority(self.root)
                finally:
                    path.write_bytes(data)

    def test_cross_track_schema_substitution_is_rejected(self) -> None:
        (self.root / "config/release-manifest-schema-v2.json").write_bytes(
            (REPO_ROOT / "config/sosa-2023-release-manifest-schema-v1.json").read_bytes())
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_historical_blob_tampering_is_rejected(self) -> None:
        with patch.object(retained, "_git_source", return_value=("0" * 40, b"wrong historical bytes")):
            with self.assertRaisesRegex(ValueError, "historical release-authority hash mismatch"):
                historical_release_authority(self.root)

    def test_historical_and_current_fixture_tampering_is_rejected(self) -> None:
        relative = "tools/release_manifest.py"
        for field in ("historical_sha256", "current_sha256"):
            with self.subTest(field=field):
                original = self.record[field][relative]
                try:
                    self.record[field][relative] = "0" * 64
                    self.write_record()
                    with self.assertRaises(ValueError):
                        current_release_authority(self.root)
                finally:
                    self.record[field][relative] = original
                    self.write_record()

    def test_authorizing_request_tampering_is_rejected(self) -> None:
        (self.root / self.record["authorization"]["path"]).write_bytes(b"replacement authorization")
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_symlink_cannot_supply_even_correct_current_bytes(self) -> None:
        path = self.root / "tools/release_manifest.py"
        path.unlink()
        path.symlink_to(REPO_ROOT / "tools/release_manifest.py")
        with self.assertRaises(ValueError):
            current_release_authority(self.root)

    def test_historical_commit_is_fixed_independently_of_live_head(self) -> None:
        with patch.object(retained, "_git_source", wraps=retained._git_source) as read:
            historical_release_authority(self.root)
        self.assertEqual(read.call_count, 7)
        self.assertEqual({call.args[2] for call in read.call_args_list}, {HISTORICAL_AUTHORITY_COMMIT})


if __name__ == "__main__":
    unittest.main()
