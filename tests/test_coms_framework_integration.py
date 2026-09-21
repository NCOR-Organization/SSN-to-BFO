#!/usr/bin/env python3
"""Shadow-mode equivalence tests for the project-neutral COMS framework."""

from __future__ import annotations

import builtins
import hashlib
import io
import shutil
import sys
import unittest
from collections import Counter
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import coms.mapping_compiler as framework_compiler
import coms.mapping_parser as framework_parser
import coms.mapping_predicates as framework_predicates
import coms.mapping_record_builder as framework_record_builder
import coms.ontology_document as framework_document
import coms.row_identity as framework_identity
import coms.workbook_batch as framework_batch
import coms.workbook_mapping as framework_workbook_mapping
from coms.adapters.xlsx import (
    WorkbookSourceRow,
    XlsxAdapterDependencyError,
    XlsxAdapterError,
    read_xlsx_source_rows,
)
from coms.mapping_expression import ExpressionNode
from coms.mapping_record import GovernedMappingRecord
from coms.mapping_parser import EntityResolutionError
from coms.row_identity import (
    AuthoritativeAxiomIdentity as FrameworkAuthoritativeAxiomIdentity,
    CanonicalRowAudit as FrameworkCanonicalRowAudit,
    CanonicalRowExpression as FrameworkCanonicalRowExpression,
    RowLocation as FrameworkRowLocation,
    canonical_row_json as framework_canonical_row_json,
)
from coms.workbook_batch import (
    AuditedWorkbookRow,
    build_governed_workbook_batch,
    validate_workbook_source_row_ids,
)
from rdflib import URIRef


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import coms_framework_integration as integration  # noqa: E402
import coms_row_identity as legacy_identity  # noqa: E402
import generate_mapping_from_coms as legacy  # noqa: E402
import product_dispositions as dispositions  # noqa: E402


WORKBOOK_PATH = REPO_ROOT / "mappings/SSN2BFO-COMS.xlsx"
WORKBOOK_SHA256 = "e32c6b5691bf4aa00b4ec564731e0364edc2567658bb21c46f83c1e3f0d9a4f6"
GENERATOR_SHA256 = "f4c15b8d5e4f6c86e1d22a24a9dcd9f0c76af2acfab0dfff21818578a6c726b6"
ROW_IDENTITY_MODULE_SHA256 = (
    "9af9f9ed5b9321040428960e1293cffe27ebb48cc7a68a71f53f84cf18a60425"
)
DISPOSITION_MODULE_SHA256 = (
    "6de4f8bb02e979e3559f03503319ec54fae7200b9b271aef66db043918258e1e"
)
PUBLICATION_METADATA_SHA256 = (
    "bb818ab88d2dbcfd8a11eddcfc846c81609c4e9a9c6819def44f950da423e8f9"
)
ARTIFACT_SHA256 = {
    REPO_ROOT / "SSN2BFO.ttl": "c31997d7e7b8c5e0bffd3f23a4597ab4be80786978462fefe800c4c7a5dc0c11",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl": (
        "17695ef17379924449153b2c92ffaed6b57d497a1b2d1e854f584614cebec770"
    ),
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl": (
        "676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af"
    ),
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl": (
        "2908f89648d42dc928f7225056216f1cbf3bcdc79de1bcf770b40a017a5e9bf5"
    ),
    REPO_ROOT / "reports/coms-product-dispositions.json": (
        "c6f61271e573705882fa6a0f92f54c7731d6358739dc39ad66882ba6a737b0db"
    ),
    REPO_ROOT / "reports/coms-generation-validation.md": (
        "17a5070cd0023ced0de10c3fca97daf45dc6c4e1e9ae733525d619f618fff357"
    ),
}
EXPECTED_MAPPING_TYPES = {
    "class_mapping": 44,
    "object_property_mapping": 25,
    "property_chain": 3,
    "domain": 16,
    "range": 15,
    "explicit_blank": 2,
}
FIXED_DISPOSITION_HASHES = dispositions.RequiredInputHashes(
    workbook_sha256=WORKBOOK_SHA256,
    generator_sha256=GENERATOR_SHA256,
    row_identity_module_sha256=ROW_IDENTITY_MODULE_SHA256,
    disposition_module_sha256=DISPOSITION_MODULE_SHA256,
    publication_metadata_sha256=PUBLICATION_METADATA_SHA256,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_key(row_id: str, worksheet: str, row_number: int) -> tuple[str, str, int]:
    return row_id, worksheet, row_number


def disposition_input_fields(
    item: dispositions.DispositionRowInput,
) -> dict[str, object]:
    return {
        "row_id": item.row_id,
        "location": (
            item.location.worksheet,
            item.location.row_number,
        ),
        "subject_lexical": item.subject_lexical,
        "predicate_lexical": item.predicate_lexical,
        "authoritative_target_lexical": item.authoritative_target_lexical,
        "canonical_row": (
            item.canonical_row.canonicalization,
            item.canonical_row.mapping_type,
            item.canonical_row.predicate_iri,
            item.canonical_row.subject_iri,
            item.canonical_row.target,
        ),
        "source_expression_sha256": item.source_expression_sha256,
        "mapping_type": item.mapping_type,
        "reasoning": item.reasoning,
        "authoritative_axioms": tuple(
            (
                axiom.identity.canonical_axiom,
                axiom.identity.sha256,
                axiom.subject_iri,
                axiom.predicate_iri,
                axiom.target_iris,
            )
            for axiom in item.authoritative_axioms
        ),
    }


def _expression_kinds(expression: legacy.Expr | None) -> set[str]:
    if expression is None:
        return set()
    kinds = {expression.kind}
    for child in expression.children:
        kinds.update(_expression_kinds(child))
    kinds.update(_expression_kinds(expression.filler))
    return kinds


SYNTHETIC_HEADERS = (
    "sssom:subject_id",
    "sssom:predicate_id",
    "coms:Target",
    "coms:Reasoning",
    "coms:RowID",
)


def _test_row_id(number: int) -> str:
    return f"urn:uuid:00000000-0000-4000-8000-{number:012d}"


def _write_test_workbook(
    path: Path,
    sheet1_rows: tuple[tuple[str, str, str, str, str], ...],
    sheet2_rows: tuple[tuple[str, str, str, str, str], ...] = (),
) -> None:
    workbook = legacy.openpyxl.Workbook()
    sheet1 = workbook.active
    sheet1.title = "Sheet1"
    sheet1.append(SYNTHETIC_HEADERS)
    for row in sheet1_rows:
        sheet1.append(row)
    sheet2 = workbook.create_sheet("Sheet2")
    sheet2.append(SYNTHETIC_HEADERS)
    for row in sheet2_rows:
        sheet2.append(row)
    workbook.save(path)
    workbook.close()


class CountingResolver(legacy.Resolver):
    def __init__(self) -> None:
        self.source_resolution_calls = 0
        self.entity_resolution_calls = 0
        super().__init__()

    def resolve_source_subject(self, token: str, row_id: str) -> tuple[URIRef, str]:
        self.source_resolution_calls += 1
        return super().resolve_source_subject(token, row_id)

    def resolve(self, token: str, expected_kind: str, row_id: str) -> legacy.Resolution:
        self.entity_resolution_calls += 1
        return super().resolve(token, expected_kind, row_id)


class ComsFrameworkShadowIntegrationTests(unittest.TestCase):
    def test_primary_workbook_semantic_identity_equivalence(self) -> None:
        workbook_hash_before = sha256_file(WORKBOOK_PATH)
        workbook_mtime_before = WORKBOOK_PATH.stat().st_mtime_ns
        artifact_hashes_before = {
            path: sha256_file(path)
            for path in ARTIFACT_SHA256
        }

        source_rows = read_xlsx_source_rows(
            integration.PRIMARY_WORKBOOK_PROFILE,
            base_directory=REPO_ROOT,
        )
        self.assertEqual(len(source_rows), 105)
        validate_workbook_source_row_ids(source_rows)
        self.assertEqual(len({row.row_id_text for row in source_rows}), 105)

        legacy_rows, legacy_stats = legacy.read_workbook(WORKBOOK_PATH)
        legacy_processed = legacy.validate_and_process_rows(
            legacy_rows,
            legacy.Resolver(),
            legacy_stats,
        )

        resolver = legacy.Resolver()
        row_context = integration.SsnWorkbookResolutionContext(source_rows)
        audited_rows = build_governed_workbook_batch(
            source_rows,
            integration.SsnSourceResolverAdapter(
                resolver,
                row_context=row_context,
            ),
            integration.SsnTargetResolverAdapter(
                resolver,
                row_context=row_context,
            ),
        )
        row_context.assert_complete()
        self.assertEqual(len(audited_rows), 105)

        source_keys = [
            audit_key(
                row.row_id_text,
                row.location.worksheet,
                row.location.row_number,
            )
            for row in source_rows
        ]
        legacy_keys = [
            audit_key(
                row.stable_row_id,
                row.sheet,
                row.row_number,
            )
            for row in legacy_rows
        ]
        self.assertEqual(source_keys, legacy_keys)
        self.assertEqual(
            [
                (
                    row.subject_text,
                    row.predicate_text,
                    row.target_text,
                    row.reasoning_text,
                    row.status_text,
                )
                for row in source_rows
            ],
            [
                (
                    row.subject_text,
                    row.predicate_text,
                    row.target_text,
                    row.reasoning_text,
                    None,
                )
                for row in legacy_rows
            ],
        )

        legacy_by_key = {
            audit_key(
                item.row.stable_row_id,
                item.row.sheet,
                item.row.row_number,
            ): item
            for item in legacy_processed
        }
        framework_by_key = {
            audit_key(
                item.source_row.row_id_text,
                item.source_row.location.worksheet,
                item.source_row.location.row_number,
            ): item
            for item in audited_rows
        }
        self.assertEqual(list(framework_by_key), source_keys)
        self.assertEqual(set(framework_by_key), set(legacy_by_key))

        canonical_row_matches = 0
        expression_hash_matches = 0
        authoritative_axiom_matches = 0
        axiom_hash_matches = 0

        for key in source_keys:
            framework_audit = framework_by_key[key].row_audit
            legacy_audit = legacy_by_key[key].identity_audit
            self.assertIsNotNone(legacy_audit)
            assert legacy_audit is not None

            framework_payload = framework_canonical_row_json(
                framework_audit.expression
            )
            legacy_payload = legacy_identity.canonical_row_json(
                legacy_audit.expression
            )
            if framework_payload == legacy_payload:
                canonical_row_matches += 1
            if (
                framework_audit.source_expression_sha256
                == legacy_audit.source_expression_sha256
            ):
                expression_hash_matches += 1

            framework_axioms = tuple(
                axiom.canonical_axiom
                for axiom in framework_audit.authoritative_axioms
            )
            legacy_axioms = tuple(
                axiom.canonical_axiom
                for axiom in legacy_audit.authoritative_axioms
            )
            if framework_axioms == legacy_axioms:
                authoritative_axiom_matches += 1

            framework_axiom_hashes = tuple(
                axiom.sha256
                for axiom in framework_audit.authoritative_axioms
            )
            legacy_axiom_hashes = tuple(
                axiom.sha256
                for axiom in legacy_audit.authoritative_axioms
            )
            if framework_axiom_hashes == legacy_axiom_hashes:
                axiom_hash_matches += 1

        self.assertEqual(canonical_row_matches, 105)
        self.assertEqual(expression_hash_matches, 105)
        self.assertEqual(authoritative_axiom_matches, 105)
        self.assertEqual(axiom_hash_matches, 105)

        mapping_types = Counter(
            item.governed_record.mapping_type
            for item in audited_rows
        )
        self.assertEqual(dict(mapping_types), EXPECTED_MAPPING_TYPES)
        self.assertEqual(
            sum(len(item.row_audit.authoritative_axioms) for item in audited_rows),
            103,
        )
        explicit_blank_rows = [
            item
            for item in audited_rows
            if item.governed_record.mapping_type == "explicit_blank"
        ]
        self.assertEqual(len(explicit_blank_rows), 2)
        for item in explicit_blank_rows:
            key = audit_key(
                item.source_row.row_id_text,
                item.source_row.location.worksheet,
                item.source_row.location.row_number,
            )
            self.assertEqual(item.row_audit.authoritative_axioms, ())
            legacy_audit = legacy_by_key[key].identity_audit
            self.assertIsNotNone(legacy_audit)
            assert legacy_audit is not None
            self.assertEqual(legacy_audit.authoritative_axioms, ())

        self.assertEqual(workbook_hash_before, WORKBOOK_SHA256)
        self.assertEqual(sha256_file(WORKBOOK_PATH), WORKBOOK_SHA256)
        self.assertEqual(WORKBOOK_PATH.stat().st_mtime_ns, workbook_mtime_before)
        self.assertEqual(artifact_hashes_before, ARTIFACT_SHA256)
        self.assertEqual(
            {path: sha256_file(path) for path in ARTIFACT_SHA256},
            ARTIFACT_SHA256,
        )

    def test_target_adapter_translates_legacy_resolution_failure(self) -> None:
        class FailingResolver:
            def resolve_source_subject(
                self,
                token: str,
                row_id: str,
            ) -> tuple[URIRef, str]:
                return URIRef("http://example.org/Observation"), "class"

            def resolve(self, token: str, expected_kind: str, row_id: str) -> None:
                raise legacy.GenerationError(
                    f"{row_id}: unresolved {expected_kind} token {token!r}"
                )

        row = WorkbookSourceRow(
            location=FrameworkRowLocation("Mappings", 2),
            row_id_text=_test_row_id(1),
            subject_text="sosa:Observation",
            predicate_text="rdfs:subClassOf",
            target_text="bfo:Missing",
            reasoning_text="",
            status_text=None,
        )
        row_context = integration.SsnWorkbookResolutionContext((row,))
        resolver = FailingResolver()
        source_adapter = integration.SsnSourceResolverAdapter(  # type: ignore[arg-type]
            resolver,
            row_context=row_context,
        )
        target_adapter = integration.SsnTargetResolverAdapter(  # type: ignore[arg-type]
            resolver,
            row_context=row_context,
        )
        source_adapter.resolve_source_entity(row.subject_text)
        with self.assertRaises(EntityResolutionError) as raised:
            target_adapter.resolve_entity("bfo:Missing", "class")
        self.assertIn(
            f"{row.location.text} [{row.row_id_text}]",
            str(raised.exception),
        )
        row_context.assert_complete()


class ComsCompatibilityProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_rows = read_xlsx_source_rows(
            integration.PRIMARY_WORKBOOK_PROFILE,
            base_directory=REPO_ROOT,
        )

        legacy_rows, legacy_stats = legacy.read_workbook(WORKBOOK_PATH)
        cls.legacy_resolver = legacy.Resolver()
        cls.legacy_processed = legacy.validate_and_process_rows(
            legacy_rows,
            cls.legacy_resolver,
            legacy_stats,
        )

        cls.framework_resolver = legacy.Resolver()
        cls.row_context = integration.SsnWorkbookResolutionContext(cls.source_rows)
        cls.audited_rows = build_governed_workbook_batch(
            cls.source_rows,
            integration.SsnSourceResolverAdapter(
                cls.framework_resolver,
                row_context=cls.row_context,
            ),
            integration.SsnTargetResolverAdapter(
                cls.framework_resolver,
                row_context=cls.row_context,
            ),
        )
        cls.row_context.assert_complete()
        cls.projected_rows = integration.project_audited_workbook_rows(
            cls.audited_rows,
            cls.row_context.source_kind_by_row_id,
        )
        cls.legacy_disposition_inputs = tuple(
            legacy.disposition_input_for_processed_row(item)
            for item in cls.legacy_processed
        )
        cls.native_disposition_inputs = tuple(
            integration.disposition_input_for_audited_workbook_row(item)
            for item in cls.audited_rows
        )

    def test_row_aware_adapters_preserve_context_and_source_kinds(self) -> None:
        rows = (
            WorkbookSourceRow(
                location=FrameworkRowLocation("Mappings", 2),
                row_id_text="urn:uuid:00000000-0000-4000-8000-000000000001",
                subject_text="  sosa:Observation  ",
                predicate_text="rdfs:subClassOf",
                target_text="bfo:Entity",
                reasoning_text="",
                status_text=None,
            ),
            WorkbookSourceRow(
                location=FrameworkRowLocation("Mappings", 3),
                row_id_text="urn:uuid:00000000-0000-4000-8000-000000000002",
                subject_text="sosa:hasFeatureOfInterest",
                predicate_text="",
                target_text="",
                reasoning_text="unmapped",
                status_text=None,
            ),
        )

        class RecordingResolver:
            def __init__(self) -> None:
                self.calls: list[tuple[str, str, str, str]] = []

            def resolve_source_subject(self, token: str, row_id: str) -> tuple[URIRef, str]:
                self.calls.append(("source", token, "", row_id))
                kind = "class" if token == "sosa:Observation" else "object_property"
                return URIRef(f"http://example.org/{token.split(':', 1)[1]}"), kind

            def resolve(self, token: str, expected_kind: str, row_id: str) -> legacy.Resolution:
                self.calls.append(("target", token, expected_kind, row_id))
                if token == "bfo:Missing":
                    raise legacy.GenerationError(
                        f"{row_id}: unresolved {expected_kind} token {token!r}"
                    )
                return legacy.Resolution(
                    token=token,
                    iri=URIRef("http://example.org/Entity"),
                    kind=expected_kind,
                    method="direct",
                )

        resolver = RecordingResolver()
        context = integration.SsnWorkbookResolutionContext(rows)
        source_adapter = integration.SsnSourceResolverAdapter(  # type: ignore[arg-type]
            resolver,
            row_context=context,
        )
        target_adapter = integration.SsnTargetResolverAdapter(  # type: ignore[arg-type]
            resolver,
            row_context=context,
        )

        with self.assertRaises(legacy.GenerationError):
            target_adapter.resolve_entity("bfo:Entity", "class")
        with self.assertRaises(legacy.GenerationError):
            source_adapter.resolve_source_entity("sosa:Wrong")
        self.assertEqual(resolver.calls, [])

        first_diagnostic = f"Mappings!2 [{rows[0].row_id_text}]"
        source_adapter.resolve_source_entity("sosa:Observation")
        with self.assertRaises(EntityResolutionError) as raised:
            target_adapter.resolve_entity("bfo:Missing", "class")
        self.assertIn(first_diagnostic, str(raised.exception))
        target_adapter.resolve_entity("bfo:Entity", "class")
        source_adapter.resolve_source_entity("sosa:hasFeatureOfInterest")
        context.assert_complete()

        second_diagnostic = f"Mappings!3 [{rows[1].row_id_text}]"
        self.assertEqual(
            resolver.calls,
            [
                ("source", "sosa:Observation", "", first_diagnostic),
                ("target", "bfo:Missing", "class", first_diagnostic),
                ("target", "bfo:Entity", "class", first_diagnostic),
                ("source", "sosa:hasFeatureOfInterest", "", second_diagnostic),
            ],
        )
        self.assertEqual(
            dict(context.source_kind_by_row_id),
            {
                rows[0].row_id_text: "class",
                rows[1].row_id_text: "object_property",
            },
        )
        with self.assertRaises(legacy.GenerationError):
            source_adapter.resolve_source_entity("sosa:Observation")

    def test_expression_projection_preserves_supported_shapes_and_order(self) -> None:
        expression = ExpressionNode(
            kind="intersection",
            children=(
                ExpressionNode(kind="named", iri="http://example.org/Z"),
                ExpressionNode(
                    kind="union",
                    children=(
                        ExpressionNode(kind="named", iri="http://example.org/B"),
                        ExpressionNode(kind="named", iri="http://example.org/A"),
                    ),
                ),
                ExpressionNode(
                    kind="some",
                    property_iri="http://example.org/p",
                    filler=ExpressionNode(
                        kind="intersection",
                        children=(
                            ExpressionNode(kind="named", iri="http://example.org/D"),
                            ExpressionNode(kind="named", iri="http://example.org/C"),
                        ),
                    ),
                ),
            ),
        )
        expected = legacy.Expr(
            kind="intersection",
            children=(
                legacy.Expr(kind="named", iri=URIRef("http://example.org/Z")),
                legacy.Expr(
                    kind="union",
                    children=(
                        legacy.Expr(kind="named", iri=URIRef("http://example.org/B")),
                        legacy.Expr(kind="named", iri=URIRef("http://example.org/A")),
                    ),
                ),
                legacy.Expr(
                    kind="some",
                    prop=URIRef("http://example.org/p"),
                    filler=legacy.Expr(
                        kind="intersection",
                        children=(
                            legacy.Expr(kind="named", iri=URIRef("http://example.org/D")),
                            legacy.Expr(kind="named", iri=URIRef("http://example.org/C")),
                        ),
                    ),
                ),
            ),
        )
        self.assertEqual(integration.project_expression_node(expression), expected)
        self.assertIsNone(integration.project_expression_node(None))

    def test_row_and_audit_projection_are_verbatim_legacy_values(self) -> None:
        source_row = WorkbookSourceRow(
            location=FrameworkRowLocation("Mappings", 7),
            row_id_text="sentinel-row-id-that-must-not-be-revalidated",
            subject_text=" sosa:Observation ",
            predicate_text=" rdfs:subClassOf ",
            target_text=" bfo:Entity ",
            reasoning_text=" preserve lexical text ",
            status_text=" reviewed ",
        )
        self.assertEqual(
            integration.project_workbook_source_row(source_row),
            legacy.WorkbookRow(
                sheet="Mappings",
                row_number=7,
                subject_text=" sosa:Observation ",
                predicate_text=" rdfs:subClassOf ",
                target_text=" bfo:Entity ",
                reasoning_text=" preserve lexical text ",
                stable_row_id=source_row.row_id_text,
                mapping_status_text=" reviewed ",
            ),
        )

        framework_audit = FrameworkCanonicalRowAudit(
            row_id=source_row.row_id_text,
            location=source_row.location,
            reasoning=" sentinel audit reasoning ",
            expression=FrameworkCanonicalRowExpression(
                canonicalization="sentinel-canonicalization",
                mapping_type="sentinel-mapping-type",
                predicate_iri="sentinel-predicate-iri",
                subject_iri="sentinel-subject-iri",
                target="sentinel-canonical-target",
            ),
            source_expression_sha256="sentinel-source-expression-hash",
            authoritative_axioms=(
                FrameworkAuthoritativeAxiomIdentity(
                    canonical_axiom="sentinel-authoritative-axiom",
                    sha256="sentinel-authoritative-axiom-hash",
                ),
            ),
        )
        audited_row = AuditedWorkbookRow(
            source_row=source_row,
            governed_record=GovernedMappingRecord(
                row_id=source_row.row_id_text,
                subject_iri="http://example.org/subject",
                predicate_iri="http://www.w3.org/2000/01/rdf-schema#subClassOf",
                mapping_type="class_mapping",
                reasoning=" sentinel record reasoning ",
                expression=ExpressionNode(
                    kind="named",
                    iri="http://example.org/target",
                ),
            ),
            row_audit=framework_audit,
        )
        projected_row = integration.project_audited_workbook_rows(
            (audited_row,),
            {source_row.row_id_text: "class"},
        )[0]
        projected_audit = projected_row.identity_audit
        self.assertIsInstance(projected_audit, legacy_identity.CanonicalRowAudit)
        assert projected_audit is not None
        self.assertIsInstance(projected_audit.location, legacy_identity.RowLocation)
        self.assertIsInstance(
            projected_audit.expression,
            legacy_identity.CanonicalRowExpression,
        )
        for axiom in projected_audit.authoritative_axioms:
            self.assertIsInstance(
                axiom,
                legacy_identity.AuthoritativeAxiomIdentity,
            )
        self.assertEqual(
            projected_audit,
            legacy_identity.CanonicalRowAudit(
                row_id=source_row.row_id_text,
                location=legacy_identity.RowLocation("Mappings", 7),
                reasoning=" sentinel audit reasoning ",
                expression=legacy_identity.CanonicalRowExpression(
                    canonicalization="sentinel-canonicalization",
                    mapping_type="sentinel-mapping-type",
                    predicate_iri="sentinel-predicate-iri",
                    subject_iri="sentinel-subject-iri",
                    target="sentinel-canonical-target",
                ),
                source_expression_sha256="sentinel-source-expression-hash",
                authoritative_axioms=(
                    legacy_identity.AuthoritativeAxiomIdentity(
                        canonical_axiom="sentinel-authoritative-axiom",
                        sha256="sentinel-authoritative-axiom-hash",
                    ),
                ),
            ),
        )

        forbidden = AssertionError(
            "native disposition adapter invoked a legacy semantic authority"
        )
        with (
            mock.patch.object(
                legacy,
                "disposition_input_for_processed_row",
                side_effect=forbidden,
            ),
            mock.patch.object(
                legacy,
                "canonical_input_for_processed_row",
                side_effect=forbidden,
            ),
            mock.patch.object(
                integration,
                "project_audited_workbook_rows",
                side_effect=forbidden,
            ),
            mock.patch.object(
                integration,
                "project_expression_node",
                side_effect=forbidden,
            ),
            mock.patch.object(
                integration,
                "project_canonical_row_audit",
                side_effect=forbidden,
            ),
            mock.patch.object(
                legacy_identity,
                "canonicalize_processed_row",
                side_effect=forbidden,
            ),
            mock.patch.object(
                legacy_identity,
                "source_expression_sha256",
                side_effect=forbidden,
            ),
            mock.patch.object(
                legacy_identity,
                "canonical_authoritative_axioms",
                side_effect=forbidden,
            ),
            mock.patch.object(
                legacy_identity,
                "build_row_audit",
                side_effect=forbidden,
            ),
            mock.patch.object(
                integration,
                "canonical_input_for_mapping_record",
                wraps=framework_identity.canonical_input_for_mapping_record,
            ) as canonical_view,
        ):
            native_input = integration.disposition_input_for_audited_workbook_row(
                audited_row
            )
        canonical_view.assert_called_once_with(
            audited_row.governed_record,
            source_row.location,
        )
        self.assertEqual(
            native_input,
            dispositions.DispositionRowInput(
                row_id=source_row.row_id_text,
                location=legacy_identity.RowLocation("Mappings", 7),
                subject_lexical=" sosa:Observation ",
                predicate_lexical=" rdfs:subClassOf ",
                authoritative_target_lexical=" bfo:Entity ",
                canonical_row=legacy_identity.CanonicalRowExpression(
                    canonicalization="sentinel-canonicalization",
                    mapping_type="sentinel-mapping-type",
                    predicate_iri="sentinel-predicate-iri",
                    subject_iri="sentinel-subject-iri",
                    target="sentinel-canonical-target",
                ),
                source_expression_sha256="sentinel-source-expression-hash",
                mapping_type="class_mapping",
                reasoning=" preserve lexical text ",
                authoritative_axioms=(
                    dispositions.DispositionAxiomInput(
                        identity=legacy_identity.AuthoritativeAxiomIdentity(
                            canonical_axiom="sentinel-authoritative-axiom",
                            sha256="sentinel-authoritative-axiom-hash",
                        ),
                        subject_iri="http://example.org/subject",
                        predicate_iri=(
                            "http://www.w3.org/2000/01/rdf-schema#subClassOf"
                        ),
                        target_iris=("http://example.org/target",),
                    ),
                ),
            ),
        )
        self.assertIsInstance(native_input.location, legacy_identity.RowLocation)
        self.assertIsInstance(
            native_input.canonical_row,
            legacy_identity.CanonicalRowExpression,
        )
        self.assertIsInstance(
            native_input.authoritative_axioms[0].identity,
            legacy_identity.AuthoritativeAxiomIdentity,
        )

    def test_primary_workbook_projection_is_structurally_identical(self) -> None:
        self.assertEqual(len(self.projected_rows), 105)
        self.assertEqual(len(self.legacy_processed), 105)

        projected_order = [
            (item.row.stable_row_id, item.row.sheet, item.row.row_number)
            for item in self.projected_rows
        ]
        legacy_order = [
            (item.row.stable_row_id, item.row.sheet, item.row.row_number)
            for item in self.legacy_processed
        ]
        self.assertEqual(projected_order, legacy_order)

        mismatches = Counter()
        for projected, expected in zip(self.projected_rows, self.legacy_processed):
            mismatches["row_id_location"] += (
                projected.row.stable_row_id,
                projected.row.sheet,
                projected.row.row_number,
            ) != (
                expected.row.stable_row_id,
                expected.row.sheet,
                expected.row.row_number,
            )
            mismatches["workbook_row_lexical"] += (
                projected.row.subject_text,
                projected.row.predicate_text,
                projected.row.target_text,
                projected.row.reasoning_text,
                projected.row.mapping_status_text,
            ) != (
                expected.row.subject_text,
                expected.row.predicate_text,
                expected.row.target_text,
                expected.row.reasoning_text,
                expected.row.mapping_status_text,
            )
            mismatches["subject"] += projected.subject != expected.subject
            mismatches["source_kind"] += projected.subject_kind != expected.subject_kind
            mismatches["predicate"] += projected.predicate != expected.predicate
            mismatches["target_lexical"] += projected.target != expected.target
            mismatches["expression_tree"] += projected.expr != expected.expr
            mismatches["target_property"] += projected.target_property != expected.target_property
            mismatches["property_chain"] += projected.property_chain != expected.property_chain
            mismatches["identity_audit"] += projected.identity_audit != expected.identity_audit
        self.assertEqual(
            dict(mismatches),
            {
                "row_id_location": 0,
                "workbook_row_lexical": 0,
                "subject": 0,
                "source_kind": 0,
                "predicate": 0,
                "target_lexical": 0,
                "expression_tree": 0,
                "target_property": 0,
                "property_chain": 0,
                "identity_audit": 0,
            },
        )
        self.assertEqual(self.projected_rows, self.legacy_processed)

        projected_by_location = {
            (item.row.sheet, item.row.row_number): item
            for item in self.projected_rows
        }
        legacy_by_location = {
            (item.row.sheet, item.row.row_number): item
            for item in self.legacy_processed
        }
        representative_locations = (
            ("Sheet1", 2),   # named class
            ("Sheet1", 5),   # intersection
            ("Sheet1", 4),   # union
            ("Sheet1", 13),  # nested existential
            ("Sheet2", 2),   # direct object-property target
            ("Sheet2", 18),  # ordered property chain
            ("Sheet2", 6),   # domain
            ("Sheet2", 7),   # range
            ("Sheet2", 16),  # explicit blank
        )
        for location in representative_locations:
            self.assertEqual(
                projected_by_location[location],
                legacy_by_location[location],
            )

        self.assertEqual(projected_by_location[("Sheet1", 2)].expr.kind, "named")
        self.assertEqual(projected_by_location[("Sheet1", 5)].expr.kind, "intersection")
        self.assertEqual(projected_by_location[("Sheet1", 4)].expr.kind, "union")
        self.assertIn(
            "some",
            _expression_kinds(projected_by_location[("Sheet1", 13)].expr),
        )
        self.assertIsNotNone(projected_by_location[("Sheet2", 2)].target_property)
        self.assertGreater(len(projected_by_location[("Sheet2", 18)].property_chain), 1)
        self.assertEqual(projected_by_location[("Sheet2", 6)].predicate, "rdfs:domain")
        self.assertEqual(projected_by_location[("Sheet2", 7)].predicate, "rdfs:range")

    def test_resolution_report_matches_legacy_row_attribution(self) -> None:
        self.assertGreater(len(self.legacy_resolver.records), 0)
        self.assertEqual(
            self.framework_resolver.records,
            self.legacy_resolver.records,
        )

    def test_both_explicit_blank_rows_project_without_targets(self) -> None:
        blank_rows = [item for item in self.projected_rows if not item.predicate]
        self.assertEqual(
            {(item.row.sheet, item.row.row_number, item.row.stable_row_id) for item in blank_rows},
            {
                (
                    "Sheet2",
                    16,
                    "urn:uuid:2ae25d88-9551-45e7-a2b9-7735575e4d8f",
                ),
                (
                    "Sheet2",
                    17,
                    "urn:uuid:637399a9-a264-49f7-bab8-33f2128646ab",
                ),
            },
        )
        legacy_by_row_id = {
            item.row.stable_row_id: item
            for item in self.legacy_processed
        }
        for item in blank_rows:
            self.assertEqual(item, legacy_by_row_id[item.row.stable_row_id])
            self.assertEqual(item.subject_kind, "object_property")
            self.assertEqual(item.predicate, "")
            self.assertEqual(item.target, "")
            self.assertIsNone(item.expr)
            self.assertIsNone(item.target_property)
            self.assertEqual(item.property_chain, ())
            self.assertIsNotNone(item.identity_audit)
            assert item.identity_audit is not None
            self.assertEqual(item.identity_audit.authoritative_axioms, ())

    def test_native_disposition_inputs_match_legacy_field_by_field_for_all_rows(
        self,
    ) -> None:
        self.assertEqual(len(self.native_disposition_inputs), 105)
        self.assertEqual(len(self.legacy_disposition_inputs), 105)
        self.assertEqual(
            [item.row_id for item in self.native_disposition_inputs],
            [item.row_id for item in self.legacy_disposition_inputs],
        )

        mismatches = Counter()
        for native, expected in zip(
            self.native_disposition_inputs,
            self.legacy_disposition_inputs,
        ):
            native_fields = disposition_input_fields(native)
            expected_fields = disposition_input_fields(expected)
            for field in native_fields:
                mismatches[field] += (
                    native_fields[field] != expected_fields[field]
                )
        self.assertEqual(
            dict(mismatches),
            {
                field: 0
                for field in disposition_input_fields(
                    self.native_disposition_inputs[0]
                )
            },
        )

    def test_native_disposition_classification_and_explicit_blanks_match_legacy(
        self,
    ) -> None:
        def classification_evidence(
            row_inputs: tuple[dispositions.DispositionRowInput, ...],
        ) -> tuple[list[tuple[object, ...]], Counter[str]]:
            evidence: list[tuple[object, ...]] = []
            categories: Counter[str] = Counter()
            for row in row_inputs:
                for axiom in row.authoritative_axioms:
                    category = dispositions.classify_target_category(axiom)
                    categories[category] += 1
                    evidence.append(
                        (
                            row.row_id,
                            axiom.identity,
                            dispositions.referenced_iris(axiom),
                            category,
                            dispositions.derive_product_dispositions(
                                category,
                                dispositions.PRODUCT_ROLE_ORDER,
                            ),
                        )
                    )
            return evidence, categories

        legacy_evidence, legacy_categories = classification_evidence(
            self.legacy_disposition_inputs
        )
        native_evidence, native_categories = classification_evidence(
            self.native_disposition_inputs
        )
        self.assertEqual(len(native_evidence), 103)
        self.assertEqual(native_evidence, legacy_evidence)
        self.assertEqual(native_categories, legacy_categories)
        self.assertEqual(
            native_categories,
            Counter(
                {
                    "target_neutral": 29,
                    "bfo_bearing": 19,
                    "cco_bearing": 25,
                    "mixed_bfo_cco": 30,
                }
            ),
        )

        native_blanks = {
            item.row_id: item
            for item in self.native_disposition_inputs
            if not item.authoritative_axioms
        }
        legacy_blanks = {
            item.row_id: item
            for item in self.legacy_disposition_inputs
            if not item.authoritative_axioms
        }
        expected_blanks = {
            "urn:uuid:2ae25d88-9551-45e7-a2b9-7735575e4d8f": (
                "Sheet2",
                16,
                "sosa:hasSample",
                "78883d8f62ff3dc679b238f1a17e47db6cc0b481a2859aa729723dea670aadb6",
            ),
            "urn:uuid:637399a9-a264-49f7-bab8-33f2128646ab": (
                "Sheet2",
                17,
                "sosa:isSampleOf",
                "46baaa1e5b7a959dbb7cc484f1c977f95487847d7ea493abe60fd55d4df42876",
            ),
        }
        self.assertEqual(set(native_blanks), set(expected_blanks))
        for row_id, (sheet, row_number, source, source_hash) in expected_blanks.items():
            native = native_blanks[row_id]
            expected = legacy_blanks[row_id]
            self.assertEqual(disposition_input_fields(native), disposition_input_fields(expected))
            self.assertEqual((native.location.worksheet, native.location.row_number), (sheet, row_number))
            self.assertEqual(native.subject_lexical, source)
            self.assertIsNone(native.predicate_lexical)
            self.assertIsNone(native.authoritative_target_lexical)
            self.assertEqual(native.mapping_type, "explicit_blank")
            self.assertIsNone(native.canonical_row.predicate_iri)
            self.assertIsNone(native.canonical_row.target)
            self.assertEqual(native.source_expression_sha256, source_hash)
            self.assertEqual(native.authoritative_axioms, ())

        document = dispositions.build_disposition_document(
            self.native_disposition_inputs,
            legacy.load_metadata(legacy.PUBLICATION_METADATA),
            FIXED_DISPOSITION_HASHES,
        )
        document_blanks = {
            row.row_id: row
            for row in document.rows
            if not row.authoritative_axioms
        }
        self.assertEqual(set(document_blanks), set(expected_blanks))
        for row in document_blanks.values():
            self.assertEqual(row.authoritative_axioms, ())
            assert row.row_product_dispositions is not None
            self.assertEqual(len(row.row_product_dispositions), 5)
            for _, disposition in row.row_product_dispositions:
                self.assertEqual(disposition.status, "deferred")
                self.assertEqual(
                    disposition.reason_code,
                    "EXPLICITLY_UNMAPPED_SOURCE_ROW",
                )

    def test_native_canonical_inputs_render_all_authoritative_axioms_exactly(
        self,
    ) -> None:
        comparisons = 0
        for audited, processed in zip(
            self.audited_rows,
            self.legacy_processed,
        ):
            native_input = framework_identity.canonical_input_for_mapping_record(
                audited.governed_record,
                audited.source_row.location,
            )
            legacy_input = legacy.canonical_input_for_processed_row(processed)
            assert processed.identity_audit is not None
            self.assertEqual(
                len(audited.row_audit.authoritative_axioms),
                len(processed.identity_audit.authoritative_axioms),
            )
            for native_identity, expected_identity in zip(
                audited.row_audit.authoritative_axioms,
                processed.identity_audit.authoritative_axioms,
            ):
                self.assertEqual(native_identity.sha256, expected_identity.sha256)
                axiom_id = f"sha256:{native_identity.sha256}"
                self.assertEqual(
                    legacy.render_authoritative_axiom_lines(
                        native_input,
                        axiom_id,
                    ),
                    legacy.render_authoritative_axiom_lines(
                        legacy_input,
                        axiom_id,
                    ),
                )
                comparisons += 1
        self.assertEqual(comparisons, 103)

    def test_native_disposition_document_matches_fixed_provenance_bytes(
        self,
    ) -> None:
        publication_metadata = legacy.load_metadata(legacy.PUBLICATION_METADATA)
        maintained_path = REPO_ROOT / "reports/coms-product-dispositions.json"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            legacy_path = root / "legacy-dispositions.json"
            native_path = root / "native-dispositions.json"
            with mock.patch.object(
                legacy,
                "build_and_write_disposition_report_from_inputs",
                wraps=legacy.build_and_write_disposition_report_from_inputs,
            ) as shared_writer:
                legacy_document, legacy_inputs = (
                    legacy.build_and_write_disposition_report(
                        self.legacy_processed,
                        legacy_path,
                        FIXED_DISPOSITION_HASHES,
                        publication_metadata,
                    )
                )
            shared_writer.assert_called_once()
            delegated_inputs = shared_writer.call_args.args[0]
            self.assertEqual(
                [disposition_input_fields(item) for item in delegated_inputs],
                [
                    disposition_input_fields(item)
                    for item in self.legacy_disposition_inputs
                ],
            )

            native_document, native_inputs = (
                legacy.build_and_write_disposition_report_from_inputs(
                    self.native_disposition_inputs,
                    native_path,
                    FIXED_DISPOSITION_HASHES,
                    publication_metadata,
                )
            )

            self.assertEqual(
                [disposition_input_fields(item) for item in legacy_inputs],
                [disposition_input_fields(item) for item in native_inputs],
            )
            self.assertEqual(native_document, legacy_document)
            self.assertEqual(native_path.read_bytes(), legacy_path.read_bytes())
            self.assertEqual(native_path.read_bytes(), maintained_path.read_bytes())
            self.assertEqual(
                hashlib.sha256(native_path.read_bytes()).hexdigest(),
                ARTIFACT_SHA256[maintained_path],
            )

    def test_projection_invokes_no_legacy_semantic_authority(self) -> None:
        forbidden = AssertionError("projection invoked a legacy semantic authority")
        with (
            mock.patch.object(legacy, "ManchesterParser", side_effect=forbidden),
            mock.patch.object(legacy, "parse_property_chain", side_effect=forbidden),
            mock.patch.object(legacy.Resolver, "resolve_source_subject", side_effect=forbidden),
            mock.patch.object(legacy.Resolver, "resolve", side_effect=forbidden),
            mock.patch.object(legacy, "validate_workbook_row_ids", side_effect=forbidden),
            mock.patch.object(legacy, "build_row_audit", side_effect=forbidden),
            mock.patch.object(legacy_identity, "build_row_audit", side_effect=forbidden),
            mock.patch.object(legacy, "attach_canonical_identities", side_effect=forbidden),
            mock.patch.object(framework_parser, "parse_class_expression", side_effect=forbidden),
            mock.patch.object(framework_parser, "parse_property_chain", side_effect=forbidden),
            mock.patch.object(
                framework_identity,
                "canonical_input_for_mapping_record",
                side_effect=forbidden,
            ),
            mock.patch.object(framework_identity, "build_row_audit", side_effect=forbidden),
            mock.patch.object(
                framework_batch,
                "canonical_input_for_mapping_record",
                side_effect=forbidden,
            ),
            mock.patch.object(framework_batch, "build_row_audit", side_effect=forbidden),
            mock.patch.object(
                framework_batch,
                "validate_workbook_source_row_ids",
                side_effect=forbidden,
            ),
        ):
            projected = integration.project_audited_workbook_rows(
                self.audited_rows,
                self.row_context.source_kind_by_row_id,
            )
        self.assertEqual(projected, self.legacy_processed)

        with self.assertRaisesRegex(
            legacy.GenerationError,
            "source-kind sidecar entry is missing",
        ):
            integration.project_audited_workbook_rows(self.audited_rows, {})


class ComsPrimaryWorkbookWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        legacy_rows, cls.legacy_stats = legacy.read_workbook(WORKBOOK_PATH)
        cls.legacy_resolver = CountingResolver()
        cls.legacy_processed = legacy.validate_and_process_rows(
            legacy_rows,
            cls.legacy_resolver,
            cls.legacy_stats,
        )

        cls.framework_resolver = CountingResolver()
        cls.framework_result = integration.process_primary_workbook_with_coms_result(
            WORKBOOK_PATH,
            cls.framework_resolver,
        )
        cls.framework_processed = cls.framework_result.processed_rows
        cls.framework_stats = cls.framework_result.stats

    @staticmethod
    def _legacy_process(path: Path) -> tuple[list[legacy.ProcessedRow], legacy.WorkbookStats]:
        rows, stats = legacy.read_workbook(path)
        processed = legacy.validate_and_process_rows(rows, legacy.Resolver(), stats)
        return processed, stats

    @staticmethod
    def _main_arguments(root: Path, workbook_path: Path) -> list[str]:
        return [
            "--input",
            str(workbook_path),
            "--output",
            str(root / "integrated.ttl"),
            "--report",
            str(root / "generation-report.md"),
            "--disposition-report",
            str(root / "product-dispositions.json"),
            "--alignment-core-output",
            str(root / "alignment-core.ttl"),
            "--strict-bfo-output",
            str(root / "strict-bfo.ttl"),
            "--cco-extension-output",
            str(root / "cco-extension.ttl"),
            "--coverage-report",
            str(root / "coverage.md"),
            "--diff-report",
            str(root / "comparison.md"),
            "--tmp-dir",
            str(root / "reasoner"),
            "--summary-json",
            str(root / "summary.json"),
        ]

    @staticmethod
    def _passing_hermit_result(root: Path) -> legacy.HermitResult:
        return legacy.HermitResult(
            graph_path=root / "closure.ttl",
            reasoned_path=root / "reasoned.ttl",
            generated_triple_count=1114,
            closure_triple_count=15904,
            return_code=0,
            reasoned_output_produced=True,
            owl_nothing_count=0,
            unsat_classes=[],
            robot_output="",
            robot_path="synthetic-test-robot",
        )

    def _assert_temp_product_hashes(self, root: Path) -> None:
        expected = {
            "integrated.ttl": ARTIFACT_SHA256[REPO_ROOT / "SSN2BFO.ttl"],
            "alignment-core.ttl": ARTIFACT_SHA256[
                REPO_ROOT
                / "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl"
            ],
            "strict-bfo.ttl": ARTIFACT_SHA256[
                REPO_ROOT
                / "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl"
            ],
            "cco-extension.ttl": ARTIFACT_SHA256[
                REPO_ROOT
                / "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl"
            ],
        }
        self.assertEqual(
            {
                name: sha256_file(root / name)
                for name in expected
            },
            expected,
        )

    def test_primary_wrapper_matches_legacy_rows_stats_and_resolution_state(self) -> None:
        compatibility_resolver = legacy.Resolver()
        with mock.patch.object(
            integration,
            "process_primary_workbook_with_coms_result",
            return_value=self.framework_result,
        ) as rich_processor:
            wrapper_processed, wrapper_stats = (
                integration.process_primary_workbook_with_coms(
                    WORKBOOK_PATH,
                    compatibility_resolver,
                )
            )
        rich_processor.assert_called_once_with(
            WORKBOOK_PATH,
            compatibility_resolver,
        )
        self.assertIs(wrapper_processed, self.framework_result.processed_rows)
        self.assertIs(wrapper_stats, self.framework_result.stats)
        self.assertIsInstance(
            self.framework_result,
            integration.PrimaryWorkbookComsResult,
        )
        self.assertIsInstance(self.framework_result.audited_rows, tuple)
        self.assertEqual(len(self.framework_result.audited_rows), 105)
        self.assertEqual(len(self.framework_processed), 105)
        self.assertEqual(self.framework_processed, self.legacy_processed)
        self.assertEqual(self.framework_stats, self.legacy_stats)
        self.assertEqual(
            self.framework_resolver.records,
            self.legacy_resolver.records,
        )
        self.assertEqual(len(self.framework_resolver.records), 60)
        self.assertEqual(
            sum(
                len(record.rows)
                for record in self.framework_resolver.records.values()
            ),
            265,
        )
        self.assertEqual(self.legacy_resolver.source_resolution_calls, 105)
        self.assertEqual(self.framework_resolver.source_resolution_calls, 105)
        self.assertEqual(self.legacy_resolver.entity_resolution_calls, 499)
        self.assertEqual(self.framework_resolver.entity_resolution_calls, 499)
        self.assertEqual(self.framework_stats.rows_by_sheet["Sheet1"], 44)
        self.assertEqual(self.framework_stats.rows_by_sheet["Sheet2"], 61)
        self.assertEqual(self.framework_stats.mapped_rows, 72)
        self.assertEqual(self.framework_stats.blank_mapping_rows, 2)
        self.assertEqual(self.framework_stats.active_axiom_rows, 103)

    def test_wrapper_uses_no_legacy_generic_front_half_authorities(self) -> None:
        resolver = legacy.Resolver()
        forbidden = AssertionError("COMS wrapper invoked a legacy front-half authority")
        with (
            mock.patch.object(legacy, "read_workbook", side_effect=forbidden),
            mock.patch.object(legacy, "validate_and_process_rows", side_effect=forbidden),
            mock.patch.object(legacy, "ManchesterParser", side_effect=forbidden),
            mock.patch.object(legacy, "parse_property_chain", side_effect=forbidden),
            mock.patch.object(legacy, "validate_workbook_row_ids", side_effect=forbidden),
            mock.patch.object(legacy, "attach_canonical_identities", side_effect=forbidden),
            mock.patch.object(legacy, "build_row_audit", side_effect=forbidden),
            mock.patch.object(legacy_identity, "build_row_audit", side_effect=forbidden),
            mock.patch.object(legacy, "Resolver", side_effect=forbidden),
            mock.patch.object(
                legacy,
                "validate_primary_domain_range_authoring_row",
                wraps=legacy.validate_primary_domain_range_authoring_row,
            ) as domain_policy,
            mock.patch.object(
                legacy,
                "validate_incompatible_duplicate_mappings",
                wraps=legacy.validate_incompatible_duplicate_mappings,
            ) as incompatible_policy,
        ):
            processed, stats = integration.process_primary_workbook_with_coms(
                WORKBOOK_PATH,
                resolver,
            )
        self.assertEqual(len(processed), 105)
        self.assertEqual(stats, self.legacy_stats)
        self.assertEqual(domain_policy.call_count, 31)
        incompatible_policy.assert_called_once_with(processed)

    def test_canonical_primary_main_uses_coms_front_half_and_legacy_renderers(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            resolver = CountingResolver()
            hermit = self._passing_hermit_result(root)
            captured: dict[str, object] = {}
            real_rich_processor = integration.process_primary_workbook_with_coms_result
            real_input_writer = legacy.build_and_write_disposition_report_from_inputs

            def recording_rich_processor(
                workbook_path: Path,
                shared_resolver: legacy.Resolver,
            ) -> integration.PrimaryWorkbookComsResult:
                result = real_rich_processor(workbook_path, shared_resolver)
                captured["result"] = result
                captured["processed"] = result.processed_rows
                captured["stats"] = result.stats
                captured["resolver"] = shared_resolver
                return result

            def recording_input_writer(
                disposition_inputs: list[dispositions.DispositionRowInput],
                path: Path,
                input_hashes: dispositions.RequiredInputHashes,
                publication_metadata: legacy.PublicationMetadata,
            ) -> tuple[
                dispositions.DispositionDocument,
                list[dispositions.DispositionRowInput],
            ]:
                result = real_input_writer(
                    disposition_inputs,
                    path,
                    input_hashes,
                    publication_metadata,
                )
                captured["native_inputs"] = result[1]
                captured["disposition_document"] = result[0]
                return result

            forbidden = AssertionError(
                "primary production invoked a forbidden semantic or COMS renderer authority"
            )
            with ExitStack() as stack:
                resolver_type = stack.enter_context(
                    mock.patch.object(legacy, "Resolver", return_value=resolver)
                )
                rich_processor = stack.enter_context(mock.patch.object(
                    integration,
                    "process_primary_workbook_with_coms_result",
                    side_effect=recording_rich_processor,
                ))
                compatibility_processor = stack.enter_context(mock.patch.object(
                    integration,
                    "process_primary_workbook_with_coms",
                    side_effect=forbidden,
                ))
                stack.enter_context(
                    mock.patch.object(legacy, "read_workbook", side_effect=forbidden)
                )
                stack.enter_context(mock.patch.object(
                    legacy,
                    "validate_and_process_rows",
                    side_effect=forbidden,
                ))
                stack.enter_context(
                    mock.patch.object(legacy, "ManchesterParser", side_effect=forbidden)
                )
                stack.enter_context(
                    mock.patch.object(legacy, "parse_property_chain", side_effect=forbidden)
                )
                stack.enter_context(mock.patch.object(
                    legacy,
                    "validate_workbook_row_ids",
                    side_effect=forbidden,
                ))
                stack.enter_context(mock.patch.object(
                    legacy,
                    "attach_canonical_identities",
                    side_effect=forbidden,
                ))
                stack.enter_context(
                    mock.patch.object(legacy, "build_row_audit", side_effect=forbidden)
                )
                stack.enter_context(mock.patch.object(
                    legacy_identity,
                    "build_row_audit",
                    side_effect=forbidden,
                ))
                domain_policy = stack.enter_context(mock.patch.object(
                    legacy,
                    "validate_primary_domain_range_authoring_row",
                    wraps=legacy.validate_primary_domain_range_authoring_row,
                ))
                incompatible_policy = stack.enter_context(mock.patch.object(
                    legacy,
                    "validate_incompatible_duplicate_mappings",
                    wraps=legacy.validate_incompatible_duplicate_mappings,
                ))
                native_disposition_adapter = stack.enter_context(mock.patch.object(
                    integration,
                    "disposition_input_for_audited_workbook_row",
                    wraps=integration.disposition_input_for_audited_workbook_row,
                ))
                legacy_disposition_adapter = stack.enter_context(mock.patch.object(
                    legacy,
                    "disposition_input_for_processed_row",
                    side_effect=forbidden,
                ))
                compatibility_writer = stack.enter_context(mock.patch.object(
                    legacy,
                    "build_and_write_disposition_report",
                    side_effect=forbidden,
                ))
                shared_writer = stack.enter_context(mock.patch.object(
                    legacy,
                    "build_and_write_disposition_report_from_inputs",
                    side_effect=recording_input_writer,
                ))
                compiler_renderer = stack.enter_context(mock.patch.object(
                    framework_compiler,
                    "render_mapping_record_turtle",
                    side_effect=forbidden,
                ))
                document_record_renderer = stack.enter_context(mock.patch.object(
                    framework_document,
                    "render_mapping_record_turtle",
                    side_effect=forbidden,
                ))
                document_header_renderer = stack.enter_context(mock.patch.object(
                    framework_document,
                    "render_ontology_header_bytes",
                    side_effect=forbidden,
                ))
                document_renderer = stack.enter_context(mock.patch.object(
                    framework_document,
                    "render_ontology_document",
                    side_effect=forbidden,
                ))
                stack.enter_context(mock.patch.object(
                    legacy,
                    "run_alignment_core_hermit",
                    return_value=hermit,
                ))
                stack.enter_context(mock.patch.object(
                    legacy,
                    "run_strict_bfo_hermit",
                    return_value=hermit,
                ))
                stack.enter_context(mock.patch.object(
                    legacy,
                    "run_cco_extension_hermit",
                    return_value=hermit,
                ))
                stack.enter_context(mock.patch.object(
                    legacy,
                    "run_candidate_hermit",
                    return_value=hermit,
                ))
                stack.enter_context(redirect_stdout(io.StringIO()))
                return_code = legacy.main(
                    self._main_arguments(root, WORKBOOK_PATH)
                )

            self.assertEqual(return_code, 0)
            resolver_type.assert_called_once_with()
            rich_processor.assert_called_once_with(WORKBOOK_PATH, resolver)
            compatibility_processor.assert_not_called()
            self.assertEqual(domain_policy.call_count, 31)
            incompatible_policy.assert_called_once_with(captured["processed"])
            self.assertEqual(native_disposition_adapter.call_count, 105)
            result = captured["result"]
            self.assertIsInstance(result, integration.PrimaryWorkbookComsResult)
            assert isinstance(result, integration.PrimaryWorkbookComsResult)
            self.assertEqual(
                [call.args[0] for call in native_disposition_adapter.call_args_list],
                list(result.audited_rows),
            )
            legacy_disposition_adapter.assert_not_called()
            compatibility_writer.assert_not_called()
            shared_writer.assert_called_once()
            compiler_renderer.assert_not_called()
            document_record_renderer.assert_not_called()
            document_header_renderer.assert_not_called()
            document_renderer.assert_not_called()

            processed = captured["processed"]
            stats = captured["stats"]
            self.assertEqual(processed, self.legacy_processed)
            self.assertEqual(stats, self.legacy_stats)
            self.assertIs(captured["resolver"], resolver)
            self.assertEqual(resolver.records, self.legacy_resolver.records)
            self.assertEqual(len(resolver.records), 60)
            self.assertEqual(
                sum(len(record.rows) for record in resolver.records.values()),
                265,
            )
            self.assertEqual(resolver.source_resolution_calls, 105)
            self.assertEqual(resolver.entity_resolution_calls, 499)
            self.assertEqual(sum(not item.predicate for item in processed), 2)
            self.assertEqual(
                sum(
                    len(item.identity_audit.authoritative_axioms)
                    for item in processed
                ),
                103,
            )
            native_inputs = captured["native_inputs"]
            self.assertIsInstance(native_inputs, list)
            assert isinstance(native_inputs, list)
            self.assertEqual(len(native_inputs), 105)
            self.assertEqual(
                [item.row_id for item in native_inputs],
                [item.source_row.row_id_text for item in result.audited_rows],
            )
            blank_inputs = [
                item
                for item in native_inputs
                if item.mapping_type == "explicit_blank"
            ]
            self.assertEqual(len(blank_inputs), 2)
            self.assertTrue(
                all(not item.authoritative_axioms for item in blank_inputs)
            )
            disposition_document = captured["disposition_document"]
            self.assertIsInstance(
                disposition_document,
                dispositions.DispositionDocument,
            )
            assert isinstance(
                disposition_document,
                dispositions.DispositionDocument,
            )
            blank_records = [
                item
                for item in disposition_document.rows
                if item.mapping_type == "explicit_blank"
            ]
            self.assertEqual(len(blank_records), 2)
            for item in blank_records:
                self.assertEqual(item.authoritative_axioms, ())
                assert item.row_product_dispositions is not None
                self.assertEqual(len(item.row_product_dispositions), 5)
                self.assertTrue(all(
                    disposition.status == "deferred"
                    and disposition.reason_code
                    == "EXPLICITLY_UNMAPPED_SOURCE_ROW"
                    for _, disposition in item.row_product_dispositions
                ))
            self._assert_temp_product_hashes(root)

    def test_nonprimary_main_retains_legacy_front_half(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            copied_workbook = root / WORKBOOK_PATH.name
            shutil.copy2(WORKBOOK_PATH, copied_workbook)
            self.assertNotEqual(copied_workbook.resolve(), WORKBOOK_PATH.resolve())

            resolver = CountingResolver()
            hermit = self._passing_hermit_result(root)
            captured: dict[str, object] = {}
            real_process = legacy.validate_and_process_rows

            def recording_process(
                rows: list[legacy.WorkbookRow],
                shared_resolver: legacy.Resolver,
                stats: legacy.WorkbookStats,
            ) -> list[legacy.ProcessedRow]:
                processed = real_process(rows, shared_resolver, stats)
                captured["processed"] = processed
                captured["stats"] = stats
                captured["resolver"] = shared_resolver
                return processed

            with (
                mock.patch.object(legacy, "Resolver", return_value=resolver),
                mock.patch.object(
                    integration,
                    "process_primary_workbook_with_coms_result",
                    side_effect=AssertionError(
                        "non-primary production invoked the rich COMS processor"
                    ),
                ) as rich_processor,
                mock.patch.object(
                    integration,
                    "process_primary_workbook_with_coms",
                    side_effect=AssertionError(
                        "non-primary production invoked the COMS primary wrapper"
                    ),
                ) as wrapper,
                mock.patch.object(
                    legacy,
                    "read_workbook",
                    wraps=legacy.read_workbook,
                ) as read_workbook,
                mock.patch.object(
                    legacy,
                    "validate_and_process_rows",
                    side_effect=recording_process,
                ) as process_rows,
                mock.patch.object(
                    integration,
                    "disposition_input_for_audited_workbook_row",
                    side_effect=AssertionError(
                        "non-primary production invoked the native disposition adapter"
                    ),
                ) as native_disposition_adapter,
                mock.patch.object(
                    legacy,
                    "disposition_input_for_processed_row",
                    wraps=legacy.disposition_input_for_processed_row,
                ) as legacy_disposition_adapter,
                mock.patch.object(
                    legacy,
                    "build_and_write_disposition_report",
                    wraps=legacy.build_and_write_disposition_report,
                ) as compatibility_writer,
                mock.patch.object(
                    legacy,
                    "build_and_write_disposition_report_from_inputs",
                    wraps=legacy.build_and_write_disposition_report_from_inputs,
                ) as shared_writer,
                mock.patch.object(
                    legacy,
                    "validate_primary_domain_range_authoring_row",
                    wraps=legacy.validate_primary_domain_range_authoring_row,
                ) as domain_policy,
                mock.patch.object(
                    legacy,
                    "run_alignment_core_hermit",
                    return_value=hermit,
                ),
                mock.patch.object(
                    legacy,
                    "run_strict_bfo_hermit",
                    return_value=hermit,
                ),
                mock.patch.object(
                    legacy,
                    "run_cco_extension_hermit",
                    return_value=hermit,
                ),
                mock.patch.object(
                    legacy,
                    "run_candidate_hermit",
                    return_value=hermit,
                ),
                redirect_stdout(io.StringIO()),
            ):
                return_code = legacy.main(
                    self._main_arguments(root, copied_workbook)
                )

            self.assertEqual(return_code, 0)
            rich_processor.assert_not_called()
            wrapper.assert_not_called()
            read_workbook.assert_called_once_with(copied_workbook)
            process_rows.assert_called_once()
            native_disposition_adapter.assert_not_called()
            self.assertEqual(legacy_disposition_adapter.call_count, 105)
            self.assertEqual(
                [call.args[0] for call in legacy_disposition_adapter.call_args_list],
                captured["processed"],
            )
            compatibility_writer.assert_called_once()
            shared_writer.assert_called_once()
            self.assertEqual(len(shared_writer.call_args.args[0]), 105)
            self.assertEqual(domain_policy.call_count, 31)
            self.assertEqual(captured["processed"], self.legacy_processed)
            self.assertEqual(captured["stats"], self.legacy_stats)
            self.assertIs(captured["resolver"], resolver)
            self.assertEqual(resolver.records, self.legacy_resolver.records)
            self.assertEqual(len(resolver.records), 60)
            self.assertEqual(
                sum(len(record.rows) for record in resolver.records.values()),
                265,
            )
            self.assertEqual(resolver.source_resolution_calls, 105)
            self.assertEqual(resolver.entity_resolution_calls, 499)
            self._assert_temp_product_hashes(root)

    def test_rowid_preflight_fails_before_batch_or_resolution(self) -> None:
        with TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "invalid-row-id.xlsx"
            malformed_row_id = "not-a-canonical-row-id"
            _write_test_workbook(
                workbook_path,
                ((
                    "sosa:Observation",
                    "rdfs:subClassOf",
                    "cco:InformationContentEntity",
                    "",
                    malformed_row_id,
                ),),
            )
            resolver = mock.Mock(spec=legacy.Resolver)
            with (
                mock.patch.object(
                    integration,
                    "validate_workbook_source_row_ids",
                    wraps=integration.validate_workbook_source_row_ids,
                ) as preflight,
                mock.patch.object(
                    integration,
                    "build_governed_workbook_batch",
                    side_effect=AssertionError("semantic batch must not run"),
                ),
                self.assertRaises(legacy.GenerationError) as raised,
            ):
                integration.process_primary_workbook_with_coms(
                    workbook_path,
                    resolver,
                )

        preflight.assert_called_once()
        resolver.resolve_source_subject.assert_not_called()
        resolver.resolve.assert_not_called()
        self.assertIsInstance(
            raised.exception.__cause__,
            framework_identity.ComsRowIdentityError,
        )
        self.assertIn("MALFORMED_ROW_ID", str(raised.exception))
        self.assertIn("Sheet1!2", str(raised.exception))
        self.assertIn(malformed_row_id, str(raised.exception))

    def test_unresolved_source_preserves_project_generation_error(self) -> None:
        row_id = _test_row_id(1)
        with TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "unresolved-source.xlsx"
            _write_test_workbook(
                workbook_path,
                ((
                    "sosa:DefinitelyMissingSource",
                    "rdfs:subClassOf",
                    "cco:InformationContentEntity",
                    "",
                    row_id,
                ),),
            )
            with self.assertRaises(legacy.GenerationError) as legacy_raised:
                self._legacy_process(workbook_path)
            with self.assertRaises(legacy.GenerationError) as framework_raised:
                integration.process_primary_workbook_with_coms(
                    workbook_path,
                    legacy.Resolver(),
                )

        self.assertEqual(
            str(framework_raised.exception),
            str(legacy_raised.exception),
        )
        self.assertIn(f"Sheet1!2 [{row_id}]", str(framework_raised.exception))
        self.assertIn("sosa:DefinitelyMissingSource", str(framework_raised.exception))
        self.assertIn("cannot be resolved", str(framework_raised.exception))

    def test_expected_coms_row_failures_translate_with_notes(self) -> None:
        row_id = _test_row_id(2)
        cases = (
            (
                "target",
                "sosa:Observation",
                "rdfs:subClassOf",
                "bfo:DefinitelyMissingTarget",
                framework_parser.EntityResolutionError,
                "unresolved class token",
            ),
            (
                "parse",
                "sosa:Observation",
                "rdfs:subClassOf",
                "(",
                framework_parser.MappingParseError,
                "unexpected end of expression",
            ),
            (
                "build",
                "sosa:Observation",
                "rdfs:subPropertyOf",
                "cco:is_about",
                framework_record_builder.MappingRecordBuildError,
                "requires subject kind 'object_property'",
            ),
            (
                "predicate",
                "sosa:Observation",
                "owl:notSupported",
                "cco:InformationContentEntity",
                framework_predicates.MappingPredicateTokenError,
                "unsupported mapping predicate token",
            ),
            (
                "blank-source",
                "",
                "rdfs:subClassOf",
                "cco:InformationContentEntity",
                framework_workbook_mapping.WorkbookMappingError,
                "requires nonblank subject text",
            ),
        )
        for (
            name,
            subject,
            predicate,
            target,
            expected_cause,
            expected_fragment,
        ) in cases:
            with self.subTest(name=name), TemporaryDirectory() as directory:
                workbook_path = Path(directory) / f"{name}.xlsx"
                _write_test_workbook(
                    workbook_path,
                    ((subject, predicate, target, "", row_id),),
                )
                with self.assertRaises(legacy.GenerationError) as raised:
                    integration.process_primary_workbook_with_coms(
                        workbook_path,
                        legacy.Resolver(),
                    )

                self.assertIsInstance(raised.exception.__cause__, expected_cause)
                message = str(raised.exception)
                self.assertIn(expected_cause.__name__, message)
                self.assertIn(expected_fragment, message)
                self.assertIn(f"Workbook source row: Sheet1!2 [{row_id}]", message)
                if name == "target":
                    self.assertIn(target, message)
                    self.assertIsInstance(
                        raised.exception.__cause__.__cause__,
                        legacy.GenerationError,
                    )
                if name == "predicate":
                    self.assertIn(predicate, message)

    def test_duplicate_authoritative_axiom_is_coms_owned(self) -> None:
        first_row_id = _test_row_id(3)
        second_row_id = _test_row_id(4)
        with TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "duplicate-axiom.xlsx"
            _write_test_workbook(
                workbook_path,
                (
                    (
                        "sosa:FeatureOfInterest",
                        "rdfs:subClassOf",
                        "bfo:MaterialEntity or bfo:Process",
                        "",
                        first_row_id,
                    ),
                    (
                        "sosa:FeatureOfInterest",
                        "rdfs:subClassOf",
                        "bfo:Process or bfo:MaterialEntity",
                        "",
                        second_row_id,
                    ),
                ),
            )
            forbidden = AssertionError("project authoring policy ran too early")
            with (
                mock.patch.object(
                    legacy,
                    "validate_primary_domain_range_authoring_row",
                    side_effect=forbidden,
                ),
                mock.patch.object(
                    legacy,
                    "validate_incompatible_duplicate_mappings",
                    side_effect=forbidden,
                ),
                self.assertRaises(legacy.GenerationError) as raised,
            ):
                integration.process_primary_workbook_with_coms(
                    workbook_path,
                    legacy.Resolver(),
                )

        self.assertIsInstance(
            raised.exception.__cause__,
            framework_identity.ComsRowIdentityError,
        )
        message = str(raised.exception)
        self.assertIn("DUPLICATE_AUTHORITATIVE_AXIOM", message)
        self.assertIn(first_row_id, message)
        self.assertIn(second_row_id, message)
        self.assertIn("Sheet1!2", message)
        self.assertIn("Sheet1!3", message)

    def test_shared_domain_range_policy_matches_legacy(self) -> None:
        def expected_duplicate_message(predicate: str, axiom_name: str) -> str:
            return (
                "Sheet1!3 "
                "[urn:uuid:00000000-0000-4000-8000-000000000006]: "
                f"duplicate {predicate} row for sosa:hasFeatureOfInterest; "
                f"the first {axiom_name} row is Sheet1!2 "
                "[urn:uuid:00000000-0000-4000-8000-000000000005]. "
                f"Multiple OWL {axiom_name} axioms are conjunctive; write "
                "alternatives with Manchester 'or' in one target expression."
            )

        duplicate_cases = (
            (
                "domain",
                "rdfs:domain",
                "sosa:Observation",
                "sosa:Actuation",
                "domain",
            ),
            (
                "range",
                "rdfs:range",
                "sosa:FeatureOfInterest",
                "sosa:Platform",
                "range",
            ),
        )
        for (
            name,
            predicate,
            first_target,
            second_target,
            axiom_name,
        ) in duplicate_cases:
            with self.subTest(name=name), TemporaryDirectory() as directory:
                workbook_path = Path(directory) / f"duplicate-{name}.xlsx"
                _write_test_workbook(
                    workbook_path,
                    (
                        (
                            "sosa:hasFeatureOfInterest",
                            predicate,
                            first_target,
                            "",
                            _test_row_id(5),
                        ),
                        (
                            "sosa:hasFeatureOfInterest",
                            predicate,
                            second_target,
                            "",
                            _test_row_id(6),
                        ),
                    ),
                )
                with self.assertRaises(legacy.GenerationError) as legacy_raised:
                    self._legacy_process(workbook_path)
                with self.assertRaises(legacy.GenerationError) as framework_raised:
                    integration.process_primary_workbook_with_coms(
                        workbook_path,
                        legacy.Resolver(),
                    )
                expected_message = expected_duplicate_message(
                    predicate,
                    axiom_name,
                )
                self.assertEqual(
                    str(legacy_raised.exception),
                    expected_message,
                )
                self.assertEqual(str(framework_raised.exception), expected_message)

        overlap_cases = (
            ("domain", "rdfs:domain", "sosa:Observation"),
            ("range", "rdfs:range", "sosa:FeatureOfInterest"),
        )
        failure_cases = (
            ("malformed-second-target", "{target} or"),
            ("identical-authoritative-axiom", "{target}"),
        )
        for axiom_name, predicate, first_target in overlap_cases:
            for failure_name, second_target_template in failure_cases:
                second_target = second_target_template.format(target=first_target)
                with (
                    self.subTest(
                        axiom=axiom_name,
                        failure=failure_name,
                    ),
                    TemporaryDirectory() as directory,
                ):
                    workbook_path = (
                        Path(directory)
                        / f"duplicate-{axiom_name}-{failure_name}.xlsx"
                    )
                    _write_test_workbook(
                        workbook_path,
                        (
                            (
                                "sosa:hasFeatureOfInterest",
                                predicate,
                                first_target,
                                "",
                                _test_row_id(5),
                            ),
                            (
                                "sosa:hasFeatureOfInterest",
                                predicate,
                                second_target,
                                "",
                                _test_row_id(6),
                            ),
                        ),
                    )
                    with self.assertRaises(legacy.GenerationError) as legacy_raised:
                        self._legacy_process(workbook_path)
                    with self.assertRaises(legacy.GenerationError) as framework_raised:
                        integration.process_primary_workbook_with_coms(
                            workbook_path,
                            legacy.Resolver(),
                        )
                    expected_message = expected_duplicate_message(
                        predicate,
                        axiom_name,
                    )
                    self.assertEqual(str(legacy_raised.exception), expected_message)
                    self.assertEqual(str(framework_raised.exception), expected_message)
                    self.assertIsNone(framework_raised.exception.__cause__)

        with TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "duplicate-before-blank-source.xlsx"
            _write_test_workbook(
                workbook_path,
                (
                    (
                        "sosa:hasFeatureOfInterest",
                        "rdfs:domain",
                        "sosa:Observation",
                        "",
                        _test_row_id(5),
                    ),
                    (
                        "sosa:hasFeatureOfInterest",
                        "rdfs:domain",
                        "sosa:Actuation",
                        "",
                        _test_row_id(6),
                    ),
                    (
                        "",
                        "rdfs:subClassOf",
                        "sosa:Observation",
                        "",
                        _test_row_id(7),
                    ),
                ),
            )
            with self.assertRaises(legacy.GenerationError) as legacy_raised:
                self._legacy_process(workbook_path)
            with self.assertRaises(legacy.GenerationError) as framework_raised:
                integration.process_primary_workbook_with_coms(
                    workbook_path,
                    legacy.Resolver(),
                )
            expected_message = expected_duplicate_message(
                "rdfs:domain",
                "domain",
            )
            self.assertEqual(str(legacy_raised.exception), expected_message)
            self.assertEqual(str(framework_raised.exception), expected_message)

        with TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "domain-and-range.xlsx"
            _write_test_workbook(
                workbook_path,
                (
                    (
                        "sosa:hasFeatureOfInterest",
                        "rdfs:domain",
                        "sosa:Observation",
                        "",
                        _test_row_id(7),
                    ),
                    (
                        "sosa:hasFeatureOfInterest",
                        "rdfs:range",
                        "sosa:FeatureOfInterest",
                        "",
                        _test_row_id(8),
                    ),
                ),
            )
            legacy_processed, legacy_stats = self._legacy_process(workbook_path)
            framework_processed, framework_stats = (
                integration.process_primary_workbook_with_coms(
                    workbook_path,
                    legacy.Resolver(),
                )
            )
        self.assertEqual(framework_processed, legacy_processed)
        self.assertEqual(framework_stats, legacy_stats)
        self.assertNotIn(
            self.framework_processed[0].predicate,
            legacy.DOMAIN_RANGE_PREDICATES,
        )
        unrelated = self.framework_processed[0]
        first_by_key: dict[tuple[str, str], legacy.WorkbookRow] = {}
        legacy.validate_primary_domain_range_authoring_row(
            unrelated.row,
            unrelated.subject,
            first_by_key,
        )
        legacy.validate_primary_domain_range_authoring_row(
            unrelated.row,
            unrelated.subject,
            first_by_key,
        )
        self.assertEqual(first_by_key, {})

    def test_existing_incompatible_mapping_policy_is_retained(self) -> None:
        with TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "incompatible-mapping.xlsx"
            _write_test_workbook(
                workbook_path,
                (
                    (
                        "sosa:FeatureOfInterest",
                        "rdfs:subClassOf",
                        "bfo:MaterialEntity",
                        "",
                        _test_row_id(9),
                    ),
                    (
                        "sosa:FeatureOfInterest",
                        "rdfs:subClassOf",
                        "bfo:Process",
                        "",
                        _test_row_id(10),
                    ),
                ),
            )
            with self.assertRaises(legacy.GenerationError) as legacy_raised:
                self._legacy_process(workbook_path)
            with self.assertRaises(legacy.GenerationError) as framework_raised:
                integration.process_primary_workbook_with_coms(
                    workbook_path,
                    legacy.Resolver(),
                )
        self.assertEqual(
            str(framework_raised.exception),
            str(legacy_raised.exception),
        )
        self.assertIn("incompatible target", str(framework_raised.exception))

    def test_extraction_errors_translate_and_unexpected_failures_propagate(self) -> None:
        resolver = mock.Mock(spec=legacy.Resolver)
        extraction_failures = (
            XlsxAdapterError("synthetic extraction failure"),
            XlsxAdapterDependencyError("synthetic dependency failure"),
        )
        for failure in extraction_failures:
            with (
                self.subTest(error_type=type(failure).__name__),
                mock.patch.object(
                    integration,
                    "read_xlsx_source_rows",
                    side_effect=failure,
                ),
                self.assertRaises(legacy.GenerationError) as translated,
            ):
                integration.process_primary_workbook_with_coms(
                    WORKBOOK_PATH,
                    resolver,
                )
            self.assertIs(translated.exception.__cause__, failure)
            self.assertIn(type(failure).__name__, str(translated.exception))
            self.assertIn(str(failure), str(translated.exception))

        unexpected = RuntimeError("synthetic programming failure")
        with (
            mock.patch.object(
                integration,
                "read_xlsx_source_rows",
                side_effect=unexpected,
            ),
            self.assertRaises(RuntimeError) as propagated,
        ):
            integration.process_primary_workbook_with_coms(
                WORKBOOK_PATH,
                resolver,
            )
        self.assertIs(propagated.exception, unexpected)

    def test_wrapper_is_read_only(self) -> None:
        locked_paths = (WORKBOOK_PATH, *ARTIFACT_SHA256)
        hashes_before = {
            path: sha256_file(path)
            for path in locked_paths
        }
        workbook_mtime_before = WORKBOOK_PATH.stat().st_mtime_ns
        resolver = legacy.Resolver()
        forbidden = AssertionError("wrapper attempted a file write")

        original_builtin_open = builtins.open
        original_path_open = Path.open

        def guarded_builtin_open(
            file: object,
            mode: str = "r",
            *args: object,
            **kwargs: object,
        ) -> object:
            if any(flag in mode for flag in ("w", "a", "x", "+")):
                raise forbidden
            return original_builtin_open(file, mode, *args, **kwargs)

        def guarded_path_open(
            path: Path,
            mode: str = "r",
            *args: object,
            **kwargs: object,
        ) -> object:
            if any(flag in mode for flag in ("w", "a", "x", "+")):
                raise forbidden
            return original_path_open(path, mode, *args, **kwargs)

        with (
            mock.patch.object(builtins, "open", new=guarded_builtin_open),
            mock.patch.object(Path, "open", new=guarded_path_open),
            mock.patch.object(Path, "write_text", side_effect=forbidden),
            mock.patch.object(Path, "write_bytes", side_effect=forbidden),
            mock.patch.object(
                legacy.openpyxl.Workbook,
                "save",
                side_effect=forbidden,
            ),
        ):
            processed, stats = integration.process_primary_workbook_with_coms(
                WORKBOOK_PATH,
                resolver,
            )
        self.assertEqual(len(processed), 105)
        self.assertEqual(stats, self.legacy_stats)
        self.assertEqual(
            {path: sha256_file(path) for path in locked_paths},
            hashes_before,
        )
        self.assertEqual(WORKBOOK_PATH.stat().st_mtime_ns, workbook_mtime_before)

        self.assertEqual(
            sha256_file(Path(legacy.__file__).resolve()),
            GENERATOR_SHA256,
        )
