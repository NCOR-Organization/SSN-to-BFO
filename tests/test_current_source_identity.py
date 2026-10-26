import copy
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_source_identity as identity
import current_documentary_workbook as documentary


class CurrentIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((identity.ROOT / identity.RECORD).read_text())

    def test_governed_bytes_and_headers(self):
        self.assertEqual(identity.check_record(self.document), [])

    def test_source_and_target_drift_fail(self):
        for group in ("source_files", "target_files", "products", "scope_and_configuration"):
            document = copy.deepcopy(self.document)
            document[group][0]["sha256"] = "0" * 64
            self.assertTrue(any("byte identity drift" in e for e in identity.check_record(document)))

    def test_missing_and_duplicate_governed_entries_fail(self):
        for operation in ("missing", "duplicate"):
            document = copy.deepcopy(self.document)
            if operation == "missing":
                document["source_files"].pop()
            else:
                document["source_files"].append(document["source_files"][0])
            self.assertTrue(any("governed paths" in e for e in identity.check_record(document)))

    def test_false_ontology_identity_fails(self):
        for field, value in (("ontology_iri", "urn:invented"), ("version_iris", ["urn:invented"]),
                             ("imports", [])):
            with self.subTest(field=field):
                document = copy.deepcopy(self.document)
                document["source_files"][1]["ontologies"][0][field] = value
                self.assertTrue(any("header identity differs" in e for e in identity.check_record(document)))

    def test_invented_upstream_and_local_provenance_fail(self):
        for group in ("source_files", "target_files", "products", "scope_and_configuration"):
            with self.subTest(group=group):
                document = copy.deepcopy(self.document)
                document[group][0]["local_git_provenance"]["latest_change"] = "f" * 40 + "|invented"
                self.assertTrue(any("local Git provenance differs" in e for e in identity.check_record(document)))
        document = copy.deepcopy(self.document)
        document["source_files"][0]["upstream_immutable_commit"] = "f" * 40
        self.assertTrue(any("unsupported upstream" in e for e in identity.check_record(document)))

    def test_false_component_description_and_provenance_fail(self):
        for component, field, value in (
            ("BFO", "identity_basis", "Independently downloaded and pinned BFO"),
            ("BFO", "provenance_annotation", "Obtained from an invented repository"),
            ("BFO", "upstream_immutable_commit", "f" * 40),
            ("CCO", "artifact", "imports/sosa.ttl"),
            ("CCO", "version_info", "Version 99"),
        ):
            with self.subTest(component=component, field=field):
                document = copy.deepcopy(self.document)
                document["target_components"][component][field] = value
                self.assertTrue(any("target_components" in e for e in identity.check_record(document)))

    def test_removed_or_false_unresolved_import_declaration_fails(self):
        for value in (None, [], ["urn:invented"]):
            with self.subTest(value=value):
                document = copy.deepcopy(self.document)
                if value is None:
                    del document["unresolved_external_imports"]
                else:
                    document["unresolved_external_imports"] = value
                self.assertTrue(any("unresolved_external_imports" in e for e in identity.check_record(document)))

    def test_source_target_roles_and_unverified_extra_metadata_fail(self):
        document = copy.deepcopy(self.document)
        document["source_files"], document["target_files"] = document["target_files"], document["source_files"]
        self.assertTrue(any("governed paths" in e for e in identity.check_record(document)))
        document = copy.deepcopy(self.document)
        document["source_files"][0]["role"] = "target"
        self.assertTrue(any("unsupported authoritative metadata" in e for e in identity.check_record(document)))

    def test_false_freeze_and_closure_claims_fail(self):
        for field in ("baseline_head", "branch_at_freeze", "closure_limitation", "identity_policy"):
            with self.subTest(field=field):
                document = copy.deepcopy(self.document)
                document[field] = "invented"
                self.assertTrue(any(field in e for e in identity.check_record(document)))

    def test_missing_import_is_visible_and_bfo_is_embedded(self):
        self.assertEqual(self.document["unresolved_external_imports"], ["http://www.w3.org/2004/02/skos/core"])
        self.assertEqual(self.document["target_components"]["BFO"]["artifact"], "imports/cco.ttl")

    @contextmanager
    def documentary_candidate(self):
        """Copied authorities only; the real workbook is never edited."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".git").symlink_to(identity.ROOT / ".git", target_is_directory=True)
            paths = {identity.WORKBOOK, *identity.SOURCES, *identity.TARGETS,
                     *identity.PRODUCTS, *identity.CONFIGURATION}
            for relative in paths:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(identity.ROOT / relative, destination)
            historical = root / "historical-workbook.xlsx"
            baseline = json.loads((identity.ROOT / documentary.BASELINE).read_text())
            # The configured identity belongs to this retained historical
            # workbook, not to any later documented live version.
            shutil.copyfile(identity.ROOT / baseline["historical_workbook"]["path"], historical)
            shutil.copyfile(historical, root / identity.WORKBOOK)
            book = load_workbook(root / identity.WORKBOOK)
            book["Sheet1"]["D4"] = "Documentary fixture, with no semantic cell change."
            book.save(root / identity.WORKBOOK)
            book.close()
            yield root, historical

    def test_documentary_chain_preserves_historical_workbook_identity(self):
        with self.documentary_candidate() as (root, historical):
            before = copy.deepcopy(self.document)
            with patch.object(identity, "validate_workbook_evolution", return_value=historical) as validate:
                self.assertEqual(identity.check_record(self.document, root), [])
            validate.assert_called_once_with(root, self.document["authoritative_workbook"]["sha256"],
                                             root / identity.WORKBOOK)
            self.assertEqual(self.document, before)

    def test_documentary_chain_failure_or_wrong_historical_bytes_fail(self):
        with self.documentary_candidate() as (root, historical):
            with patch.object(identity, "validate_workbook_evolution", side_effect=ValueError("missing transition")):
                errors = identity.check_record(self.document, root)
            self.assertTrue(any("byte identity drift" in error and "missing transition" in error for error in errors))
            historical.write_bytes(historical.read_bytes() + b"changed retained bytes")
            with patch.object(identity, "validate_workbook_evolution", return_value=historical):
                errors = identity.check_record(self.document, root)
            self.assertTrue(any("retained historical workbook fingerprint differs" in error for error in errors))

    def test_documentary_exception_does_not_cover_configuration_drift(self):
        with self.documentary_candidate() as (root, historical):
            scope = root / "config/current-ssn-sosa-scope.json"
            scope.write_bytes(scope.read_bytes() + b"\n")
            with patch.object(identity, "validate_workbook_evolution", return_value=historical):
                errors = identity.check_record(self.document, root)
            self.assertTrue(any("config/current-ssn-sosa-scope.json: byte identity drift" in error for error in errors))

    def test_real_documentary_chain_and_forged_manifest_integration(self):
        with self.documentary_candidate() as (root, historical):
            baseline = json.loads((identity.ROOT / documentary.BASELINE).read_text())
            paths = {documentary.BASELINE, baseline["historical_workbook"]["path"],
                     *(ref["path"] for ref in baseline["immutable_evidence"])}
            for relative in paths:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(identity.ROOT / relative, destination)
            evidence_path = "imports/sosa.ttl"
            transition = documentary.create_update(
                root, historical, root / identity.WORKBOOK,
                {"Sheet1!D4": [{"path": evidence_path,
                                "sha256": documentary.digest((root / evidence_path).read_bytes()),
                                "reference": "Test fixture evidence for documentary-only evolution"}]},
                editor_identity="Integration test fixture")
            self.assertEqual(identity.check_record(self.document, root), [])
            forged = json.loads(transition.read_text())
            forged["changes"] = []
            transition.write_bytes(documentary.canonical_bytes(forged))
            errors = identity.check_record(self.document, root)
            self.assertTrue(any("manifest is incomplete" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
