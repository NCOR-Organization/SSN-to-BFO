"""Exact generation expectations use disposable historical-restoration fixtures."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from uuid import uuid4

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_documentary_workbook as documentary
import current_semantic_workbook as semantic
import current_semantic_generation as generation
import generate_mapping_from_coms as mapping

HISTORICAL_START_SHA = "9e526e5705fc84571e03616f74c59fe8654fcc073a1c45a281109cf22c276e14"


class SemanticGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.root = Path(cls.directory.name)
        baseline = json.loads((ROOT / documentary.BASELINE).read_text())
        files = {documentary.BASELINE, documentary.WORKBOOK,
                 baseline["historical_workbook"]["path"],
                 "config/publication-metadata.toml",
                 *semantic.SOURCE_TARGET_SHA256, *semantic.GOVERNED_INPUT_SHA256}
        files.update(ref["path"] for ref in baseline["immutable_evidence"])
        files.update(documentary.evidence_paths(ROOT))
        files.update(path.relative_to(ROOT).as_posix()
                     for dirname in (documentary.UPDATES, documentary.VERSIONS)
                     for path in (ROOT / dirname).rglob("*") if path.is_file())
        for relative in files:
            if relative.startswith(semantic.TRANSITIONS + "/"):
                continue
            target = cls.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        cls.old = cls.root / "old.xlsx"
        cls.new = cls.root / "candidate.xlsx"
        shutil.copyfile(ROOT / documentary.VERSIONS / (HISTORICAL_START_SHA + ".xlsx"),
                        cls.root / documentary.WORKBOOK)
        shutil.copyfile(cls.root / documentary.WORKBOOK, cls.old)
        workbook = load_workbook(cls.old)
        for sheet, row in (("Sheet2", 49), ("Sheet1", 43), ("Sheet1", 45)):
            workbook[sheet].cell(row, 2).value = None
            workbook[sheet].cell(row, 3).value = None
        workbook["Sheet2"].append(["sosa:madeBySensor", "rdfs:subPropertyOf", "cco:has_agent", "Historical fixture", "urn:uuid:" + str(uuid4())])
        workbook["Sheet2"].append(["sosa:madeObservation", "rdfs:subPropertyOf", "cco:agent_in", "Historical fixture", "urn:uuid:" + str(uuid4())])
        workbook.save(cls.new)
        workbook.close()
        cls.expectations = generation.compute_expectations(cls.root, cls.old, cls.new)

    def test_baseline_exact_bytes_and_counts_are_unchanged(self):
        with generation.generated_expectations_context(self.root, self.old):
            self.assertEqual(generation.expected_count("ROOT_LOGICAL_TRIPLE_COUNT", 1102), 1102)
        products = generation.render_current_products(ROOT, ROOT / documentary.WORKBOOK)
        self.assertEqual(set(products), set(generation.PRODUCT_PATHS.values()))
        for relative, data in products.items():
            self.assertEqual(data, (ROOT / relative).read_bytes(), relative)

    def test_exact_restoration_axiom_counts_and_coverage_delta(self):
        before, after = self.expectations["before"], self.expectations["after"]
        self.assertEqual(before["counts"]["GOVERNED_ROW_COUNT"], 105)
        self.assertEqual(after["counts"]["GOVERNED_ROW_COUNT"], 107)
        self.assertEqual(after["counts"]["AUTHORITATIVE_AXIOM_COUNT"], 102)
        self.assertEqual(after["counts"]["ZERO_AXIOM_ROW_COUNT"], 5)
        self.assertEqual(after["counts"]["CCO_EXTENSION_AXIOM_COUNT"], 54)
        self.assertEqual(after["counts"]["CCO_EXTENSION_DIRECT_SUBPROPERTY_COUNT"], 18)
        self.assertEqual(after["counts"]["CCO_EXTENSION_PROPERTY_CHAIN_COUNT"], 0)
        self.assertEqual(len(self.expectations["logical_axiom_delta"]["added"]), 2)
        self.assertEqual(len(self.expectations["logical_axiom_delta"]["removed"]), 3)
        self.assertEqual(self.expectations["coverage_delta"]["direct_classes"], -2)
        self.assertEqual(self.expectations["coverage_delta"]["direct_object_properties"], 2)
        self.assertEqual(self.expectations["coverage_delta"]["rule_or_chain_route"], -1)

    def test_tampered_counts_or_axiom_delta_fail_exact_validation(self):
        for field in ("count", "axiom", "coverage", "disposition", "count_type"):
            declared = copy.deepcopy(self.expectations)
            if field == "count":
                declared["after"]["counts"]["GOVERNED_ROW_COUNT"] += 1
            elif field == "axiom":
                declared["logical_axiom_delta"]["removed"].pop()
            elif field == "coverage":
                declared["coverage_delta"]["rule_or_chain_route"] = 0
            elif field == "disposition":
                declared["after"]["disposition_counts"]["cco_extension"][0]["count"] += 1
            else:
                declared["after"]["counts"]["ROOT_ONTOLOGY_DECLARATION_COUNT"] = True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "exact workbook"):
                generation.validate_expectations(self.root, self.old, self.new, declared)

    def test_unrecorded_semantic_workbook_cannot_obtain_count_overrides(self):
        with self.assertRaisesRegex(ValueError, "complete documentary update chain"):
            with generation.generated_expectations_context(self.root, self.new):
                self.fail("unauthorized context was entered")

    def test_candidate_still_fails_original_baseline_checks(self):
        _, serialized = generation._snapshot(self.root, self.new)
        with self.assertRaisesRegex(ValueError, "GOVERNED_ROW_COUNT"):
            generation._validate_rendered(self.root, self.new, serialized)

    def test_validated_transition_enables_exact_counts_and_rendering(self):
        ref = copy.deepcopy(next(ref for ref in json.loads((self.root / documentary.BASELINE).read_text())["immutable_evidence"]
                                 if ref["path"].endswith("approved-instructions.txt")))
        ref["reference"] = "Disposable generation test fixture evidence"
        authorities = {}
        for row in semantic.workbook_delta(self.old, self.new)["changed_rows"]:
            authorities[row["row_id"]] = {
                "authorization_type": "RESTORE_PREVIOUSLY_APPROVED_DECISION" if row["old"] is None else "RESTORE_PREVIOUS_TECHNICAL_DEFERRAL",
                "rationale": "Disposable exact-delta generation fixture", "evidence": [ref],
            }
        record = semantic.create_transition(self.root, self.old, self.new, authorities,
                    editor_identity="Generation test", generation_expectations=self.expectations)
        try:
            with generation.generated_expectations_context(self.root, self.new):
                self.assertEqual(generation.expected_count("GOVERNED_ROW_COUNT", 105), 107)
                self.assertEqual(generation.expected_count("CCO_EXTENSION_AXIOM_COUNT", 55), 54)
            products = generation.render_current_products(self.root, self.new)
            self.assertEqual(set(products), set(generation.PRODUCT_PATHS.values()))
            self.assertNotEqual(products["SSN2BFO.ttl"], (ROOT / "SSN2BFO.ttl").read_bytes())
            self.assertEqual(products[generation.PRODUCT_PATHS["alignment_core"]], (ROOT / generation.PRODUCT_PATHS["alignment_core"]).read_bytes())
            # The formal callable must obtain the same validated expectations;
            # it is not entered through either development CLI wrapper.
            from modular_products import ModularProductError
            from product_dispositions import RequiredInputHashes, build_disposition_document, serialize_disposition_document
            from release_context import parse_formal_release_context
            result, _, metadata = generation._inputs(self.root, self.new)
            disposition = build_disposition_document(
                [mapping.disposition_input_for_processed_row(row) for row in result.processed_rows],
                metadata, RequiredInputHashes(*("0" * 64 for _ in range(5))))
            disposition_path = self.root / "candidate-dispositions.json"
            disposition_path.write_bytes(serialize_disposition_document(disposition))
            context = parse_formal_release_context("2099-01-02", "2099-01-02", "v2099-01-02", "0" * 40)
            audits = [row.identity_audit for row in result.processed_rows]
            with self.assertRaisesRegex(ModularProductError, "PRODUCT_.*COUNT_MISMATCH"):
                mapping.render_formal_product_set(result.processed_rows, audits, disposition, metadata, context)
            live = self.root / documentary.WORKBOOK
            shutil.copyfile(self.new, live)
            try:
                _, formal = generation.render_current_formal_products(
                    self.root, context, live, self.root / "config/publication-metadata.toml", disposition_path)
                self.assertEqual(formal.integrated.governed_axiom_count, 102)
                self.assertEqual(formal.cco_extension.governed_axiom_count, 54)
                self.assertEqual(formal.integrated.total_triple_count,
                                 self.expectations["after"]["counts"]["ROOT_FORMAL_TOTAL_TRIPLE_COUNT"])
                self.assertEqual(formal.cco_extension.total_triple_count,
                                 self.expectations["after"]["counts"]["CCO_EXTENSION_FORMAL_TOTAL_TRIPLE_COUNT"])
            finally:
                shutil.copyfile(self.old, live)
        finally:
            record.unlink()
        self.assertEqual(generation.expected_count("GOVERNED_ROW_COUNT", 105), 105)

    def test_active_context_rejects_missing_or_invalid_counts_and_resets(self):
        for value in ({}, {"X": -1}, {"X": True}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                with generation._snapshot_context({"counts": value}):
                    generation.expected_count("X", 42)
            self.assertEqual(generation.expected_count("X", 42), 42)

    def test_cached_snapshots_are_isolated_and_recheck_input_bytes(self):
        first, _ = generation._snapshot(self.root, self.old)
        first["counts"]["GOVERNED_ROW_COUNT"] = 999
        second, _ = generation._snapshot(self.root, self.old)
        self.assertEqual(second["counts"]["GOVERNED_ROW_COUNT"], 105)
        path = self.root / "config/current-ssn-sosa-scope.json"
        before = path.read_bytes()
        key = generation._snapshot_key(self.root, self.old)
        try:
            path.write_bytes(before + b"\n")
            self.assertNotEqual(generation._snapshot_key(self.root, self.old), key)
        finally:
            path.write_bytes(before)


if __name__ == "__main__":
    unittest.main()
