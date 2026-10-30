#!/usr/bin/env python3
"""Current-only identity reporting; unchanged SOSA-2023 product generation."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import generate_mapping_from_coms as current  # noqa: E402
import generate_sosa_next_products as next_products  # noqa: E402
import check_coms_mapping as current_checker  # noqa: E402


class CurrentIdentityReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resolver = current.Resolver()
        cls.rows, cls.stats = current.read_workbook(current.PRIMARY_WORKBOOK)
        cls.processed = current.validate_and_process_rows(cls.rows, cls.resolver, cls.stats)
        cls.audits = [item.identity_audit for item in cls.processed]
        cls.blanks = [audit for audit in cls.audits if audit.expression.mapping_type == "explicit_blank"]

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="current-identity-report-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.inventory = self.root / "assessment.json"

    def records(self, *, state: str = "final", outcome: str = "no_direct_mapping") -> list[dict]:
        return [{
            "source_iri": audit.expression.subject_iri,
            "mapping_row_ids": [audit.row_id],
            "review_state": state,
            "assessment_outcome": outcome,
            "rationale": "Synthetic reviewed zero-axiom decision for the regression fixture.",
            "evidence": ["synthetic fixture; not an adopted repository judgment"],
        } for audit in self.blanks]

    def report(self, *, records: list[dict] | None = None, audits: list | None = None) -> dict:
        self.inventory.write_text(json.dumps({
            "schema_version": 1,
            "track": "current-ssn-sosa",
            "records": self.records() if records is None else records,
        }), encoding="utf-8")
        return current.current_identity_reporting(
            self.stats,
            self.audits if audits is None else audits,
            self.inventory,
        )

    def test_reviewed_zero_axiom_rows_have_complete_identity_and_disposition(self) -> None:
        result = self.report()
        self.assertTrue(result["identity_audit_complete"])
        self.assertEqual(result["assertion_bearing_rows"], 100)
        self.assertEqual(result["explicit_zero_axiom_rows"], 5)
        self.assertTrue(result["zero_axiom_assessment_dispositions_complete"])
        self.assertEqual(result["reviewed_zero_axiom_decisions"], 5)
        self.assertEqual(result["malformed_or_missing_identity_row_ids"], [])

    def test_unreviewed_disposition_does_not_become_reviewed_semantics(self) -> None:
        result = self.report(records=self.records(state="unreviewed", outcome="unreviewed"))
        self.assertTrue(result["identity_audit_complete"])
        self.assertTrue(result["zero_axiom_assessment_dispositions_complete"])
        self.assertEqual(result["reviewed_zero_axiom_decisions"], 0)

    def test_missing_or_invalid_dispositions_fail_separately_from_identity(self) -> None:
        for mutation in ("absent", "wrong_row_id", "duplicate", "unexplained", "incompatible_state", "invented_formal_mapping"):
            with self.subTest(mutation=mutation):
                records = self.records()
                if mutation == "absent":
                    records.pop()
                elif mutation == "wrong_row_id":
                    records[0]["mapping_row_ids"] = []
                elif mutation == "duplicate":
                    records.append(dict(records[0]))
                elif mutation == "unexplained":
                    records[0]["rationale"] = ""
                elif mutation == "incompatible_state":
                    records[0]["review_state"] = "final"
                    records[0]["assessment_outcome"] = "unreviewed"
                else:
                    records[0]["assessment_outcome"] = "formal_mapping_adopted"
                result = self.report(records=records)
                self.assertTrue(result["identity_audit_complete"])
                self.assertFalse(result["zero_axiom_assessment_dispositions_complete"])

    def test_missing_inventory_does_not_become_an_identity_failure(self) -> None:
        result = current.current_identity_reporting(self.stats, self.audits, self.inventory)
        self.assertTrue(result["identity_audit_complete"])
        self.assertFalse(result["zero_axiom_assessment_dispositions_complete"])
        self.assertIsNotNone(result["assessment_inventory_error"])

    def test_assessment_edit_invalidates_current_report_freshness(self) -> None:
        result = self.report()
        metadata = {"current_assessment_inventory_sha256": result["assessment_inventory_sha256"]}
        with mock.patch.object(current, "CURRENT_ASSESSMENT_INVENTORY", self.inventory):
            self.assertEqual(current_checker.current_assessment_freshness_errors(metadata), [])
            self.inventory.write_text(self.inventory.read_text() + "\n")
            self.assertIn(
                "current assessment inventory hash differs from the generated report",
                current_checker.current_assessment_freshness_errors(metadata),
            )

    def test_current_check_rejects_missing_disposition_but_allows_recorded_deferral(self) -> None:
        for records, passes in (([], False), (self.records(state="deferred", outcome="deferred"), True)):
            with self.subTest(passes=passes):
                result = self.report(records=records)
                metadata = {"current_assessment_inventory_sha256": result["assessment_inventory_sha256"]}
                with mock.patch.object(current, "CURRENT_ASSESSMENT_INVENTORY", self.inventory):
                    errors = current_checker.current_assessment_freshness_errors(metadata)
                if passes:
                    self.assertEqual(errors, [])
                else:
                    self.assertIn("current-track zero-axiom rows lack valid assessment dispositions", errors)

    def test_missing_assertion_still_fails(self) -> None:
        audits = list(self.audits)
        index = next(index for index, audit in enumerate(audits) if audit.authoritative_axioms)
        audits[index] = replace(audits[index], authoritative_axioms=())
        result = self.report(audits=audits)
        self.assertFalse(result["identity_audit_complete"])
        self.assertIn(audits[index].row_id, result["malformed_or_missing_identity_row_ids"])

    def test_blank_cannot_hide_a_populated_predicate_or_target(self) -> None:
        for field in ("predicate_iri", "target"):
            with self.subTest(field=field):
                changed = replace(self.blanks[0].expression, **{field: "urn:test:unexplained"})
                audit = replace(self.blanks[0], expression=changed,
                                source_expression_sha256=current.source_expression_sha256(changed))
                audits = [audit if item.row_id == audit.row_id else item for item in self.audits]
                self.assertFalse(self.report(audits=audits)["identity_audit_complete"])

    def test_missing_or_malformed_row_identity_still_fails(self) -> None:
        for field, value in (("row_id", "malformed"), ("source_expression_sha256", "0" * 64)):
            with self.subTest(field=field):
                audits = list(self.audits)
                audits[0] = replace(audits[0], **{field: value})
                self.assertFalse(self.report(audits=audits)["identity_audit_complete"])
        self.assertFalse(self.report(audits=self.audits[:-1])["identity_audit_complete"])

    def test_malformed_workbook_assertion_is_not_reclassified_as_blank(self) -> None:
        assertion = next(row for row in self.rows if row.predicate_text)
        for predicate, target in ((assertion.predicate_text, ""), ("", assertion.target_text)):
            with self.subTest(predicate=predicate, target=target):
                row = replace(assertion, predicate_text=predicate, target_text=target)
                with self.assertRaisesRegex(current.GenerationError, "active axiom rows must populate"):
                    current.validate_and_process_rows([row], self.resolver, current.WorkbookStats())

    def test_markdown_and_json_use_the_same_identity_result(self) -> None:
        self.report()
        common = dict(
            workbook_path=current.PRIMARY_WORKBOOK,
            output_path=Path("SSN2BFO.ttl"),
            workbook_sha256="synthetic-workbook-hash",
            generator_sha256="synthetic-generator-hash",
            identity_module_sha256="synthetic-identity-hash",
            generation_timestamp="2026-10-10T00:00:00Z",
            candidate_sha256="synthetic-product-hash",
            stats=self.stats,
            identity_audits=self.audits,
            hermit=None,
            coverage=None,
            comparison=None,
            errors=["reasoning deliberately not run for report rendering test"],
            elapsed_seconds=0.0,
        )
        with mock.patch.object(current, "CURRENT_ASSESSMENT_INVENTORY", self.inventory):
            current.write_generation_report(
                self.root / "report.md", resolver=self.resolver, normalized_rows=[], **common,
            )
            current.write_summary_json(self.root / "summary.json", **common)
        markdown = (self.root / "report.md").read_text()
        summary = json.loads((self.root / "summary.json").read_text())
        self.assertIn("Identity-audit completeness result: PASS", markdown)
        self.assertIn("Zero-axiom assessment disposition completeness: PASS", markdown)
        self.assertIn("Reviewed zero-axiom decisions: 5 / 5", markdown)
        self.assertTrue(summary["current_identity_reporting"]["identity_audit_complete"])
        self.assertEqual(summary["status"], "FAIL")  # Identity PASS cannot hide reasoner failure.


class Sosa2023IdentityReportNonRegressionTests(unittest.TestCase):
    def test_sosa_2023_generation_and_status_counts_are_unchanged(self) -> None:
        protected = [next_products.WORKBOOK, next_products.METADATA_PATH,
                     next_products.mapping_checker.SOURCE_VERSION_CONFIG,
                     *next_products.mapping_checker.SOURCE_FILES,
                     *next_products.MAINTAINED_PRODUCTS.values()]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
        with tempfile.TemporaryDirectory(prefix="current-identity-sosa2023-") as directory:
            with mock.patch.object(current, "current_identity_reporting", side_effect=AssertionError(
                "SOSA-2023 must not consume current-track assessment reporting"
            )):
                result = next_products.build_candidate(Path(directory) / "candidate")
            self.assertEqual(result["governed_row_count"], 119)
            self.assertEqual(result["active_mapping_count"], 55)
            self.assertEqual(result["deferred_mapping_count"], 0)
            self.assertEqual(result["explicitly_unmapped_row_count"], 64)
            self.assertTrue(next_products.maintained_products_are_fresh(result))
            for key, maintained in next_products.MAINTAINED_PRODUCTS.items():
                self.assertEqual(Path(result["product_paths"][key]).read_bytes(), maintained.read_bytes())
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected})


if __name__ == "__main__":
    unittest.main()
