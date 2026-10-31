"""Bounded external implementation-rule coverage, separate from OWL mapping."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as assessment
import generate_mapping_from_coms as mapping


class ImplementationRuleCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = mapping.Resolver()
        cls.graph = cls.resolver.source_graph
        # Retained pre-rule snapshot: its coverage must never change merely
        # because the maintained external artifact is now present on disk.
        historical = ROOT / "reports/current-semantic-workbook/versions/88835c763ce79f3ad54b076be1836b1a821dc31f984bbfe467deee3c40034ef2.xlsx"
        raw, stats = mapping.read_workbook(historical)
        cls.historical_rows = mapping.validate_and_process_rows(raw, cls.resolver, stats)
        cls.approved_rows = list(cls.historical_rows)
        for subject, (_, predicate, target) in mapping.IMPLEMENTATION_RULE_ROWS.items():
            cls.approved_rows = cls.changed(cls.approved_rows, subject,
                                            predicate=predicate, target=target,
                                            reasoning="Authorized external mapping: `" + mapping.IMPLEMENTATION_RULE_PATH + "`.")
        cls.terms = {str(row.subject): row.subject_kind for row in cls.historical_rows}

    @staticmethod
    def changed(rows, subject, *, predicate=None, target=None, reasoning=None, row_id=None):
        result = []
        for row in rows:
            if row.subject == subject:
                p = row.predicate if predicate is None else predicate
                t = row.target if target is None else target
                raw = replace(row.row, predicate_text=p, target_text=t,
                              reasoning_text=row.row.reasoning_text if reasoning is None else reasoning,
                              stable_row_id=row.row.stable_row_id if row_id is None else row_id)
                row = replace(row, row=raw, predicate=p, target=t)
            result.append(row)
        return result

    def test_both_authorized_rows_recognized(self):
        self.assertEqual(mapping.implementation_rule_terms(self.approved_rows),
                         {mapping.SSN.implementedBy, mapping.SSN.implements})

    def test_missing_or_altered_marker_never_recognized(self):
        for subject in mapping.IMPLEMENTATION_RULE_ROWS:
            for marker in ("", "Historical chain only", mapping.IMPLEMENTATION_RULE_PATH + ".bak"):
                with self.subTest(subject=subject, marker=marker):
                    rows = self.changed(self.approved_rows, subject, reasoning=marker)
                    self.assertEqual(mapping.implementation_rule_terms(rows), set())

    def test_wrong_shape_or_row_identity_never_recognized(self):
        changes = [
            (mapping.SSN.implementedBy, {"predicate": "rdfs:subPropertyOf", "target": "cco:prescribes"}),
            (mapping.SSN.implementedBy, {"target": "ssn:System"}),
            (mapping.SSN.implements, {"predicate": "rdfs:range"}),
            (mapping.SSN.implements, {"target": "sosa:Procedure"}),
            (mapping.SSN.implements, {"row_id": "urn:uuid:00000000-0000-4000-8000-000000000001"}),
        ]
        for subject, delta in changes:
            with self.subTest(subject=subject, delta=delta):
                self.assertEqual(mapping.implementation_rule_terms(self.changed(self.approved_rows, subject, **delta)), set())
        own = next(row for row in self.approved_rows if row.subject == mapping.SSN.implementedBy)
        self.assertEqual(mapping.implementation_rule_terms(self.approved_rows + [own]), set())
        self.assertEqual(mapping.implementation_rule_terms([row for row in self.approved_rows if row is not own]), set())

    def test_missing_or_modified_rule_rejected(self):
        with tempfile.TemporaryDirectory(prefix="implementation-rule-coverage-") as directory:
            root = Path(directory)
            with self.assertRaisesRegex(mapping.GenerationError, "missing"):
                mapping.implementation_rule_terms(self.approved_rows, root=root)
            path = root / mapping.IMPLEMENTATION_RULE_PATH
            path.parent.mkdir()
            path.write_bytes((ROOT / mapping.IMPLEMENTATION_RULE_PATH).read_bytes())
            self.assertEqual(mapping.implementation_rule_terms(self.approved_rows, root=root), set(mapping.IMPLEMENTATION_RULE_ROWS))
            path.write_bytes(path.read_bytes() + b"\n# drift\n")
            with self.assertRaisesRegex(mapping.GenerationError, "hash mismatch"):
                mapping.implementation_rule_terms(self.approved_rows, root=root)

    def test_historical_snapshot_has_no_new_rule_dependency(self):
        with tempfile.TemporaryDirectory(prefix="implementation-rule-historical-") as directory:
            self.assertEqual(mapping.implementation_rule_terms(self.historical_rows, root=Path(directory)), set())
        routes = assessment.coverage(self.terms, self.graph, self.historical_rows)
        for route in routes:
            self.assertFalse(any(item.get("artifact") == mapping.IMPLEMENTATION_RULE_PATH
                                 for item in route["rule_routes"]))

    def test_assessment_changes_only_pair_coverage(self):
        old = {item["source_iri"]: item for item in assessment.coverage(self.terms, self.graph, self.historical_rows)}
        new = {item["source_iri"]: item for item in assessment.coverage(self.terms, self.graph, self.approved_rows)}
        pair = {str(term) for term in mapping.IMPLEMENTATION_RULE_ROWS}
        self.assertEqual({key: value for key, value in old.items() if key not in pair},
                         {key: value for key, value in new.items() if key not in pair})
        for iri in pair:
            self.assertTrue(new[iri]["rule_or_chain_route"])
            self.assertFalse(new[iri]["direct_formal_mapping"])
            self.assertFalse(new[iri]["no_established_formal_route"])
        self.assertTrue(new[str(mapping.SSN.implements)]["typing_only_in_workbook"])
        self.assertTrue(new[str(mapping.SSN.implementedBy)]["explicit_blank"])

    def test_generator_reports_external_route_separately(self):
        with tempfile.TemporaryDirectory(prefix="implementation-rule-report-") as directory:
            report = Path(directory) / "coverage.md"
            result = mapping.build_coverage(self.approved_rows, [], report)
            self.assertEqual(result.external_rule_terms, set(mapping.IMPLEMENTATION_RULE_ROWS))
            for term in mapping.IMPLEMENTATION_RULE_ROWS:
                self.assertNotIn(term, result.mapped_object_properties)
                self.assertNotIn(term, result.unmapped_object_properties)
            self.assertIn(mapping.SSN.implements, result.property_typing_only_terms)
            self.assertIn(mapping.SSN.implementedBy, result.explicit_blank_terms)
            self.assertEqual(result.query_unmapped_count,
                             len(result.unmapped_classes) + len(result.unmapped_object_properties))
            self.assertIn("## External Mapping Rule Coverage", report.read_text())
            self.assertIn("| object properties covered by external mapping rule | 2 |", report.read_text())


class InstalledImplementationRuleCoverageTests(unittest.TestCase):
    """Run after installing the approved workbook through its transition."""

    def test_live_workbook_has_both_external_routes(self):
        raw, stats = mapping.read_workbook(mapping.PRIMARY_WORKBOOK)
        resolver = mapping.Resolver()
        rows = mapping.validate_and_process_rows(raw, resolver, stats)
        self.assertEqual(mapping.implementation_rule_terms(rows), set(mapping.IMPLEMENTATION_RULE_ROWS))
        terms = {str(subject): "object_property" for subject in mapping.IMPLEMENTATION_RULE_ROWS}
        routes = assessment.coverage(terms, resolver.source_graph, rows)
        self.assertTrue(all(route["rule_or_chain_route"] and not route["no_established_formal_route"]
                            and not route["direct_formal_mapping"] for route in routes))


if __name__ == "__main__":
    unittest.main()
