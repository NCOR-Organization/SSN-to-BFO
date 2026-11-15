#!/usr/bin/env python3
"""Focused governance tests for the non-materialized BFO Projection role."""

from __future__ import annotations

import dataclasses
import hashlib
import sys
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import generate_mapping_from_coms as coms  # noqa: E402
import modular_products as modular  # noqa: E402
import current_semantic_workbook as semantic  # noqa: E402
from coms_row_identity import RowLocation  # noqa: E402
from current_semantic_generation import (  # noqa: E402
    expected_count,
    generated_expectations_context,
    selection_policy,
)
from product_dispositions import (  # noqa: E402
    PRODUCT_ROLE_ORDER,
    ProductDisposition,
    classify_target_category,
    derive_product_dispositions,
    load_disposition_document,
)
from publication_metadata import load_metadata  # noqa: E402


class BfoProjectionRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.enterClassContext(generated_expectations_context(
            REPO_ROOT, REPO_ROOT / "mappings/SSN2BFO-COMS.xlsx"
        ))
        rows, stats = coms.read_workbook(
            REPO_ROOT / "mappings/SSN2BFO-COMS.xlsx"
        )
        cls.processed = coms.validate_and_process_rows(
            rows,
            coms.Resolver(),
            stats,
        )
        cls.canonical_rows = tuple(
            coms.canonical_input_for_processed_row(row)
            for row in cls.processed
        )
        cls.audits = tuple(
            row.identity_audit
            for row in cls.processed
        )
        cls.disposition = load_disposition_document(
            REPO_ROOT / "reports/coms-product-dispositions.json"
        )
        cls.metadata = load_metadata(
            REPO_ROOT / "config/publication-metadata.toml"
        )
        cls.reconciliation = modular.reconcile_product_axioms(
            modular.BFO_PROJECTION_KEY,
            cls.canonical_rows,
            cls.audits,
            cls.disposition,
        )

        core_selected = modular.select_product_axioms(
            "alignment_core",
            cls.canonical_rows,
            cls.audits,
            cls.disposition,
        )
        strict_selected = modular.select_product_axioms(
            "strict_bfo_mapping",
            cls.canonical_rows,
            cls.audits,
            cls.disposition,
        )
        cco_selected = modular.select_product_axioms(
            "cco_extension",
            cls.canonical_rows,
            cls.audits,
            cls.disposition,
        )

        cls.core_result = modular.build_alignment_core(
            core_selected,
            cls.metadata,
        )
        cls.strict_result = modular.build_strict_bfo_mapping(
            strict_selected,
            cls.metadata,
        )
        cls.cco_result = modular.build_cco_extension(
            cco_selected,
            cls.metadata,
        )

    @staticmethod
    def error_codes(
        error: modular.ModularProductError,
    ) -> set[str]:
        return {
            value.code
            for value in error.issues
        }

    def replace_disposition_row(
        self,
        replacement,
    ):
        return dataclasses.replace(
            self.disposition,
            rows=tuple(
                replacement
                if row.row_id == replacement.row_id
                else row
                for row in self.disposition.rows
            ),
        )

    def test_exact_disposition_reconciliation_selects_no_direct_axioms(
        self,
    ) -> None:
        self.assertEqual(
            self.reconciliation.product_key,
            "bfo_projection",
        )
        self.assertEqual(
            self.reconciliation.governed_axiom_count,
            expected_count("AUTHORITATIVE_AXIOM_COUNT", 103),
        )
        self.assertEqual(
            self.reconciliation.selected_axioms,
            (),
        )
        self.assertEqual(
            tuple(
                (
                    value.target_category,
                    value.status,
                    value.reason_code,
                    value.count,
                )
                for value in self.reconciliation.disposition_totals
            ),
            selection_policy("bfo_projection", modular.PRODUCT_SELECTION["bfo_projection"])
            .expected_disposition_totals,
        )
        self.assertEqual(
            {(value.target_category, value.status, value.reason_code)
             for value in self.reconciliation.disposition_totals},
            {("target_neutral", "provided_transitively", None),
             ("bfo_bearing", "provided_through_import", None),
             ("cco_bearing", "deferred", "NO_APPROVED_TRANSFORMATION_RULE"),
             ("mixed_bfo_cco", "deferred", "NO_APPROVED_TRANSFORMATION_RULE")},
        )
        self.assertEqual(self.reconciliation.governed_axiom_count,
                         sum(len(audit.authoritative_axioms) for audit in self.audits))
        self.assertEqual(sum(not audit.authoritative_axioms for audit in self.audits),
                         expected_count("ZERO_AXIOM_ROW_COUNT", 2))
        self.assertEqual(len(self.processed), expected_count("GOVERNED_ROW_COUNT", 105))

    def test_reordered_processed_rows_and_audits_are_stable(
        self,
    ) -> None:
        reordered = modular.reconcile_product_axioms(
            "bfo_projection",
            reversed(self.canonical_rows),
            reversed(self.audits),
            self.disposition,
        )
        self.assertEqual(
            reordered,
            self.reconciliation,
        )

    def test_identity_reconciliation_rejects_row_and_axiom_substitutions(
        self,
    ) -> None:
        replacement = dataclasses.replace(
            self.canonical_rows[0],
            row_id="urn:uuid:ffffffff-ffff-4fff-8fff-ffffffffffff",
        )

        row_cases = (
            self.canonical_rows[1:],
            (*self.canonical_rows, self.canonical_rows[0]),
            (replacement, *self.canonical_rows[1:]),
        )

        for values in row_cases:
            with self.subTest(
                row_count=len(values),
            ):
                with self.assertRaises(
                    modular.ModularProductError
                ):
                    modular.reconcile_product_axioms(
                        "bfo_projection",
                        values,
                        self.audits,
                        self.disposition,
                    )

        source = self.disposition.rows[0]
        source_axiom = source.authoritative_axioms[0]

        axiom_cases = (
            dataclasses.replace(
                source,
                authoritative_axioms=(),
            ),
            dataclasses.replace(
                source,
                authoritative_axioms=(
                    dataclasses.replace(
                        source_axiom,
                        axiom_id="sha256:" + "0" * 64,
                    ),
                ),
            ),
            dataclasses.replace(
                source,
                authoritative_axioms=(
                    source_axiom,
                    source_axiom,
                ),
            ),
        )

        for replacement_row in axiom_cases:
            with self.subTest(
                axiom_count=len(
                    replacement_row.authoritative_axioms
                ),
            ):
                with self.assertRaises(
                    modular.ModularProductError
                ):
                    modular.reconcile_product_axioms(
                        "bfo_projection",
                        self.canonical_rows,
                        self.audits,
                        self.replace_disposition_row(
                            replacement_row
                        ),
                    )

    def test_location_hash_row_and_axiom_mismatches_are_fatal(
        self,
    ) -> None:
        row = self.canonical_rows[0]

        moved = dataclasses.replace(
            row,
            location=RowLocation(
                "Other",
                row.location.row_number,
            ),
        )

        audit_cases = (
            (
                moved,
                self.audits[0],
            ),
            (
                row,
                dataclasses.replace(
                    self.audits[0],
                    source_expression_sha256="0" * 64,
                ),
            ),
            (
                row,
                dataclasses.replace(
                    self.audits[0],
                    expression=dataclasses.replace(
                        self.audits[0].expression,
                        target=(
                            self.audits[0].expression.target
                            or ""
                        )
                        + " changed",
                    ),
                ),
            ),
        )

        for changed_row, changed_audit in audit_cases:
            with self.subTest(
                location=changed_row.location.text,
            ):
                with self.assertRaises(
                    modular.ModularProductError
                ):
                    modular.reconcile_product_axioms(
                        "bfo_projection",
                        (
                            changed_row,
                            *self.canonical_rows[1:],
                        ),
                        (
                            changed_audit,
                            *self.audits[1:],
                        ),
                        self.disposition,
                    )

        disposition_row = self.disposition.rows[0]
        axiom = disposition_row.authoritative_axioms[0]

        changed = dataclasses.replace(
            disposition_row,
            authoritative_axioms=(
                dataclasses.replace(
                    axiom,
                    canonical_expression=(
                        axiom.canonical_expression
                        + " changed"
                    ),
                ),
            ),
        )

        with self.assertRaises(
            modular.ModularProductError
        ) as raised:
            modular.reconcile_product_axioms(
                "bfo_projection",
                self.canonical_rows,
                self.audits,
                self.replace_disposition_row(
                    changed
                ),
            )

        self.assertIn(
            "CANONICAL_EXPRESSION_MISMATCH",
            self.error_codes(
                raised.exception
            ),
        )

    def test_wrong_status_reason_or_category_is_fatal(
        self,
    ) -> None:
        cases = []

        for row in self.disposition.rows[:3]:
            axiom = row.authoritative_axioms[0]

            changed_dispositions = tuple(
                (
                    key,
                    ProductDisposition(
                        "emitted_unchanged"
                    ),
                )
                if key == "bfo_projection"
                else (
                    key,
                    value,
                )
                for key, value in axiom.product_dispositions
            )

            cases.append(
                dataclasses.replace(
                    row,
                    authoritative_axioms=(
                        dataclasses.replace(
                            axiom,
                            product_dispositions=(
                                changed_dispositions
                            ),
                        ),
                    ),
                )
            )

        deferred_row = next(
            row
            for row in self.disposition.rows
            if dict(
                row.authoritative_axioms[
                    0
                ].product_dispositions
            )["bfo_projection"].status
            == "deferred"
        )

        deferred_axiom = (
            deferred_row.authoritative_axioms[0]
        )

        changed_reason = tuple(
            (
                key,
                ProductDisposition(
                    "deferred",
                    "TARGET_SPECIFIC",
                ),
            )
            if key == "bfo_projection"
            else (
                key,
                value,
            )
            for key, value in deferred_axiom.product_dispositions
        )

        cases.append(
            dataclasses.replace(
                deferred_row,
                authoritative_axioms=(
                    dataclasses.replace(
                        deferred_axiom,
                        product_dispositions=(
                            changed_reason
                        ),
                    ),
                ),
            )
        )

        cases.append(
            dataclasses.replace(
                deferred_row,
                authoritative_axioms=(
                    dataclasses.replace(
                        deferred_axiom,
                        target_category="target_neutral",
                    ),
                ),
            )
        )

        for changed in cases:
            with self.subTest(
                row_id=changed.row_id,
            ):
                with self.assertRaises(
                    modular.ModularProductError
                ) as raised:
                    modular.reconcile_product_axioms(
                        "bfo_projection",
                        self.canonical_rows,
                        self.audits,
                        self.replace_disposition_row(
                            changed
                        ),
                    )

                self.assertTrue(
                    self.error_codes(
                        raised.exception
                    )
                    & {
                        "WRONG_PRODUCT_DISPOSITION",
                        "TARGET_CATEGORY_MISMATCH",
                    }
                )

    def test_existing_materialized_module_bytes_remain_protected(
        self,
    ) -> None:
        self.assertEqual(
            hashlib.sha256(
                self.core_result.serialized_bytes
            ).hexdigest(),
            "17695ef17379924449153b2c92ffaed6b57d497a1b2d1e854f584614cebec770",
        )
        self.assertEqual(
            hashlib.sha256(
                self.strict_result.serialized_bytes
            ).hexdigest(),
            "676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af",
        )
        self.assertEqual(
            self.cco_result.sha256,
            "5c95807b4a2299c06647320a532afe0beff553b0dd0e46a95c38af67db9d5d28",
        )
        for filename, result in (
            ("ssn-sosa-alignment-core.ttl", self.core_result),
            ("ssn-sosa-bfo-mapping.ttl", self.strict_result),
            ("ssn-sosa-cco-extension.ttl", self.cco_result),
        ):
            self.assertEqual(result.serialized_bytes,
                             (REPO_ROOT / "releases/current-ssn-sosa" / filename).read_bytes())

    def test_projection_role_policy_is_zero_axiom_and_not_published(
        self,
    ) -> None:
        self.assertEqual(
            modular.BFO_PROJECTION_KEY,
            "bfo_projection",
        )
        self.assertEqual(
            modular.BFO_PROJECTION_AXIOM_COUNT,
            0,
        )
        self.assertNotIn(
            "bfo_projection",
            tuple(
                product.key
                for product in self.metadata.products
            ),
        )


class RawProjectionTransitionTests(unittest.TestCase):
    def test_three_deferred_removals_preserve_zero_projection_and_raw_guard(self) -> None:
        history = semantic.resolve_history(REPO_ROOT)
        transition = [record for record in history["chain"] if record["kind"] == "semantic"][-1]
        self.assertEqual(transition["transition_id"], "58481ff2-4e56-4931-a3d4-383357b16561")

        def workbook_inventory(path):
            rows, stats = coms.read_workbook(path)
            processed = coms.validate_and_process_rows(rows, coms.Resolver(), stats)
            inventory, signatures, blanks = {}, {}, set()
            for processed_row in processed:
                row = coms.disposition_input_for_processed_row(processed_row)
                if not row.authoritative_axioms:
                    self.assertIsNone(row.predicate_lexical)
                    self.assertIsNone(row.authoritative_target_lexical)
                    blanks.add(row.row_id)
                for axiom in row.authoritative_axioms:
                    category = classify_target_category(axiom)
                    disposition = dict(derive_product_dispositions(category, PRODUCT_ROLE_ORDER))["bfo_projection"]
                    pair = (row.row_id, "sha256:" + axiom.identity.sha256)
                    inventory[pair] = (axiom.identity.canonical_axiom, category,
                                       disposition.status, disposition.reason_code)
                    signatures[pair] = (row.canonical_row.subject_iri, row.mapping_type, category)
            return processed, inventory, signatures, blanks

        baseline, before, signatures, before_blanks = workbook_inventory(
            semantic.snapshot(REPO_ROOT, transition["old_workbook_sha256"])
        )
        workbook = REPO_ROOT / "mappings/SSN2BFO-COMS.xlsx"
        processed, after, _, after_blanks = workbook_inventory(workbook)
        removed = before.keys() - after.keys()
        cleared = {row["row_id"] for row in transition["delta"]["cleared_mapping_rows"]}
        self.assertEqual(len(removed), 3)
        self.assertEqual({row_id for row_id, _ in removed}, cleared)
        self.assertEqual(after.keys() - before.keys(), set())
        self.assertEqual(after, {pair: value for pair, value in before.items() if pair not in removed})
        delta = transition["generation_expectations"]["logical_axiom_delta"]
        self.assertEqual(sorted(before[pair][0] for pair in removed), delta["removed"])
        self.assertEqual(delta["added"], [])
        self.assertEqual({signatures[pair] for pair in removed}, {
            ("http://www.w3.org/ns/ssn/forProperty", "property_chain", "cco_bearing"),
            ("http://www.w3.org/ns/ssn/systems/SystemProperty", "class_mapping", "mixed_bfo_cco"),
            ("http://www.w3.org/ns/ssn/systems/MeasurementRange", "class_mapping", "mixed_bfo_cco"),
        })
        self.assertEqual({before[pair][2:] for pair in removed},
                         {("deferred", "NO_APPROVED_TRANSFORMATION_RULE")})
        self.assertEqual((len(baseline), len(processed)), (105, 108))
        self.assertEqual((len(before), len(after)), (103, 102))
        self.assertEqual((len(before_blanks), len(after_blanks)), (2, 6))
        self.assertEqual(after_blanks - before_blanks, cleared)
        self.assertEqual(before_blanks - after_blanks, set())
        self.assertEqual(Counter(value[1] for value in before.values()),
                         {"target_neutral": 29, "bfo_bearing": 19, "cco_bearing": 25, "mixed_bfo_cco": 30})
        self.assertEqual(Counter(value[1] for value in after.values()),
                         {"target_neutral": 32, "bfo_bearing": 19, "cco_bearing": 24, "mixed_bfo_cco": 28})
        self.assertEqual((sum(value[2] == "deferred" for value in before.values()),
                          sum(value[2] == "deferred" for value in after.values())), (55, 52))
        for status, count in (("provided_transitively", 32), ("provided_through_import", 19),
                              ("emitted_unchanged", 0)):
            old_members = {pair: value for pair, value in before.items() if value[2] == status}
            new_members = {pair: value for pair, value in after.items() if value[2] == status}
            self.assertEqual(old_members, new_members)
            self.assertEqual(len(new_members), count)

        canonical_rows = tuple(coms.canonical_input_for_processed_row(row) for row in processed)
        audits = tuple(row.identity_audit for row in processed)
        disposition = load_disposition_document(REPO_ROOT / "reports/coms-product-dispositions.json")

        def assert_raw_baseline_rejects() -> None:
            policy = modular.PRODUCT_SELECTION["bfo_projection"]
            self.assertEqual(policy.categories, ())
            self.assertEqual(policy.expected_count, 0)
            self.assertEqual({category: count for category, _, _, count in policy.expected_disposition_totals},
                             {"target_neutral": 29, "bfo_bearing": 19, "cco_bearing": 25, "mixed_bfo_cco": 30})
            with self.assertRaises(modular.ModularProductError) as raised:
                modular.reconcile_product_axioms("bfo_projection", canonical_rows, audits, disposition)
            self.assertEqual({issue.code for issue in raised.exception.issues},
                             {"PRODUCT_DISPOSITION_COUNT_MISMATCH"})

        assert_raw_baseline_rejects()
        with generated_expectations_context(REPO_ROOT, workbook):
            result = modular.reconcile_product_axioms("bfo_projection", canonical_rows, audits, disposition)
            self.assertEqual(result.governed_axiom_count, len(after))
            self.assertEqual(result.selected_axioms, ())
            self.assertEqual(
                {(value.target_category, value.status, value.reason_code): value.count
                 for value in result.disposition_totals},
                Counter(value[1:] for value in after.values()),
            )
            # This role has no standalone generated bytes, closure, or profile.
            metadata = load_metadata(REPO_ROOT / "config/publication-metadata.toml")
            self.assertNotIn("bfo_projection", {product.key for product in metadata.products})
        assert_raw_baseline_rejects()


if __name__ == "__main__":
    unittest.main()
