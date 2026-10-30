"""Immutable evidence custody and authenticated current applicability.

A–D/H exercise the real inheritance approvals in the complete current history.
E–G exercise the same applicability engine with the existing sample-pair chain
context and its actual prepared approvals. The inheritance class packets have
no such chain context; these tests do not invent new real human determinations.
All mutations, transition creation and synthetic authorization are temporary.
"""
from __future__ import annotations

import copy
from contextlib import ExitStack
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from openpyxl import load_workbook
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import current_assessment as audit
import current_decision_applicability as applicability
import current_documentary_workbook as documentary
import current_semantic_workbook as semantic
import test_current_semantic_applicability as applicability_fixtures


class CurrentEvidenceFreshnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = audit.source_graph()
        cls.target = Graph().parse(ROOT / audit.TARGET_PATH, format="turtle")
        cls.scope = json.loads(audit.SCOPE.read_text())
        cls.document = json.loads(audit.ASSESSMENT.read_text())
        paths = {*semantic.evidence_paths(ROOT), *applicability.evidence_paths(ROOT),
                 *semantic.SOURCE_TARGET_PATHS, *semantic.GOVERNED_INPUT_SHA256,
                 "config/current-ssn-sosa-historical-finals.json",
                 "config/publication-metadata.toml", documentary.WORKBOOK,
                 "mappings/current-ssn-sosa-assessment.json",
                 "mappings/SOSA-next-to-BFO-COMS.xlsx"}
        paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / "imports").glob("*.ttl"))
        cls.original_files = {relative: (ROOT / relative).read_bytes() for relative in paths}
        # Compose the existing authentic historical fixture; do not subclass it
        # and accidentally rediscover or duplicate its unrelated test methods.
        applicability_fixtures.SemanticApplicabilityTests.setUpClass()

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="current-evidence-freshness-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for relative, data in self.original_files.items():
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        self.live = self.root / documentary.WORKBOOK
        self.records = copy.deepcopy(self.document["records"])
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, relative in (("ROOT", "."),
                               ("SCOPE", "config/current-ssn-sosa-scope.json"),
                               ("SOURCE_QUERY", "queries/source-classes-and-object-properties.rq"),
                               ("ASSESSMENT", "mappings/current-ssn-sosa-assessment.json"),
                               ("HISTORICAL_FINAL_BASELINE", "config/current-ssn-sosa-historical-finals.json")):
            self.stack.enter_context(patch.object(audit, name, self.root / relative))

    def rows(self):
        raw, stats = audit.mapping.read_workbook(self.live)
        return audit.mapping.validate_and_process_rows(raw, audit.mapping.Resolver(root=self.root), stats)

    def validate_current(self):
        return audit.validate(self.scope, self.records, self.graph, self.rows())

    def inheritance_records(self):
        records = [record for record in self.records
                   if record["assessment_outcome"] == "inheritance_sufficient"]
        self.assertEqual({record["source_iri"].rsplit("/", 1)[-1] for record in records},
                         {"MeasurementRange", "SystemProperty"})
        return records

    def assert_original_custody(self, *, except_paths=()):
        for relative, data in self.original_files.items():
            if relative.startswith("reports/") and relative not in except_paths:
                self.assertEqual((self.root / relative).read_bytes(), data, relative)

    def documentary_candidate(self, *, record_update):
        old = self.root / "fixture-before-documentary.xlsx"
        shutil.copyfile(self.live, old)
        book = load_workbook(self.live)
        before = book["Sheet1"]["D4"].value
        book["Sheet1"]["D4"] = "Documentary freshness fixture; no semantic cell change."
        self.assertNotEqual(before, book["Sheet1"]["D4"].value)
        book.save(self.live)
        book.close()
        self.assertNotEqual(audit.sha(old), audit.sha(self.live))
        self.assertEqual(documentary.semantic_projection_sha256(old),
                         documentary.semantic_projection_sha256(self.live))
        if record_update:
            evidence = "imports/sosa.ttl"
            update_path = documentary.create_update(
                self.root, old, self.live,
                {"Sheet1!D4": [{"path": evidence, "sha256": audit.sha(self.root / evidence),
                                "reference": "Disposable D-only freshness test"}]},
                editor_identity="Disposable freshness test fixture")
            history = semantic.resolve_history(self.root)
            self.assertEqual(history["tail_sha256"], audit.sha(self.live))
            self.assertEqual(history["chain"][-1]["kind"], "documentary")
            self.assertEqual(history["chain"][-1]["update_id"], json.loads(update_path.read_text())["update_id"])
        return old

    def test_a_exact_original_workbook_preserves_sufficiency(self):
        for record in self.inheritance_records():
            evidence = json.loads((self.root / record["inheritance_sufficiency_evidence"]["path"]).read_text())
            self.assertEqual(evidence["input_sha256"][documentary.WORKBOOK], audit.sha(self.live))
        self.assertEqual(len(self.validate_current()), 91)
        self.assert_original_custody()

    def test_b_authenticated_d_only_transition_preserves_sufficiency(self):
        old = self.documentary_candidate(record_update=True)
        for record in self.inheritance_records():
            evidence = json.loads((self.root / record["inheritance_sufficiency_evidence"]["path"]).read_text())
            self.assertEqual(evidence["input_sha256"][documentary.WORKBOOK], audit.sha(old))
            self.assertNotEqual(evidence["input_sha256"][documentary.WORKBOOK], audit.sha(self.live))
        self.assertEqual(len(self.validate_current()), 91)
        self.assert_original_custody()

    def test_c_unrecorded_d_only_mutation_fails(self):
        self.documentary_candidate(record_update=False)
        with self.assertRaisesRegex(ValueError, "complete documentary update chain"):
            self.validate_current()
        self.assert_original_custody()

    def test_d_unrecorded_semantic_cell_mutations_fail(self):
        original = self.live.read_bytes()
        original_projection = documentary.semantic_projection_sha256(self.live)
        for column in "ABCE":
            with self.subTest(column=column):
                self.live.write_bytes(original)
                book = load_workbook(self.live)
                cell = book["Sheet1"][column + "2"]
                if column == "A":
                    cell.value = "  " + cell.value + "  "
                elif column == "B":
                    cell.value = ("rdfs:subClassOf" if cell.value != "rdfs:subClassOf"
                                  else "owl:equivalentClass")
                elif column == "C":
                    cell.value = "bfo:Process" if cell.value != "bfo:Process" else "bfo:MaterialEntity"
                else:
                    cell.value = "urn:uuid:" + str(uuid4())
                book.save(self.live)
                book.close()
                self.assertNotEqual(documentary.semantic_projection_sha256(self.live), original_projection)
                with self.assertRaisesRegex(ValueError, "complete documentary update chain"):
                    self.validate_current()
        self.assert_original_custody()

    def historical_semantic_fixture(self):
        fixture = applicability_fixtures.SemanticApplicabilityTests(
            "test_real_five_term_transition_preserves_history_and_sample_decisions")
        self.addCleanup(fixture.doCleanups)
        fixture.setUp()
        before = {relative: (fixture.root / relative).read_bytes()
                  for relative in documentary.evidence_paths(fixture.root)
                  if "current-human-decisions/" in relative}
        additions = [["sosa:madeBySensor", "rdfs:subPropertyOf", "cco:has_agent", "Historical restoration fixture.",
                      "urn:uuid:2876e7da-9716-4fe9-ab0e-7f118e6f9146"],
                     ["sosa:madeObservation", "rdfs:subPropertyOf", "cco:agent_in", "Historical restoration fixture.",
                      "urn:uuid:b1d0b7d5-e004-4680-a738-1dc7d8d0edff"]]
        changes = [(sheet, f"{column}{row}", None)
                   for sheet, row in (("Sheet2", 49), ("Sheet1", 43), ("Sheet1", 45))
                   for column in "BC"]
        candidate = fixture.candidate(changes, additions)
        self.assertEqual(documentary.semantic_projection_sha256(candidate),
                         "101ff4cc24f493b90fadb70fb7cfcef26ba07f81c7b2670f7f8ce3f5c5172a45")
        transition_path = fixture.create_transition(fixture.live, candidate)
        transition = json.loads(transition_path.read_text())
        shutil.copyfile(candidate, fixture.live)
        history = semantic.resolve_history(fixture.root)
        self.assertEqual(history["chain"][-1]["transition_id"], transition["transition_id"])
        self.assertNotEqual(transition["old_semantic_projection_sha256"],
                            transition["new_semantic_projection_sha256"])
        return fixture, transition, before

    def validate_sample(self, fixture):
        decision = fixture.decision()
        record = next(record for record in fixture.records if record["source_iri"] == decision["source_iri"])
        raw, stats = audit.mapping.read_workbook(fixture.live)
        rows = audit.mapping.validate_and_process_rows(raw, fixture.resolver, stats)
        own = [row for row in rows if str(row.subject) == record["source_iri"]]
        route = audit.coverage({record["source_iri"]: record["source_kind"]}, fixture.graph, rows)[0]
        return audit.validate_human_decision(record, fixture.graph, fixture.target, rows, own,
                                             route, audit.next_comparison(rows), set())

    def assert_historical_approvals_unchanged(self, fixture, before):
        for relative, data in before.items():
            self.assertEqual((fixture.root / relative).read_bytes(), data, relative)

    def test_e_authenticated_semantic_transition_without_required_applicability_fails(self):
        fixture, _, before = self.historical_semantic_fixture()
        self.assertEqual(applicability._bound_records(fixture.root), [])
        with self.assertRaisesRegex(ValueError, "explicit non-material determination"):
            self.validate_sample(fixture)
        self.assert_historical_approvals_unchanged(fixture, before)

    def test_f_authenticated_material_determination_requires_reopening(self):
        fixture, transition, before = self.historical_semantic_fixture()
        prepared = fixture.root / applicability.PREPARED / "hasSample-forProperty.json"
        original_prepared = prepared.read_bytes()
        determination = json.loads(original_prepared)
        determination.update(
            applicability_id=str(uuid4()), classification=applicability.MATERIAL,
            reviewer_identity="Disposable fixture reviewer; not a real human determination",
            rationale="Synthetic explicit materiality determination for this isolated negative test.")
        relative = applicability.PREPARED + "/fixture-material-determination.json"
        path = fixture.root / relative
        path.write_bytes(documentary.canonical_bytes(determination))
        # Register exact synthetic authority only within this test. The real
        # parser, byte pin, binder, history and applicability validator all run.
        with patch.dict(applicability.PREPARED_SHA256, {relative: audit.sha(path)}):
            applicability.bind_prepared_applicability(fixture.root, path, transition["transition_id"])
            bound = applicability._bound_records(fixture.root)
            self.assertEqual(len(bound), 1)
            self.assertEqual(bound[0]["determination"]["classification"], applicability.MATERIAL)
            with self.assertRaisesRegex(ValueError, applicability.MATERIAL):
                self.validate_sample(fixture)
        self.assertEqual(prepared.read_bytes(), original_prepared)
        self.assert_historical_approvals_unchanged(fixture, before)

    def test_g_authenticated_non_material_determinations_preserve_decisions(self):
        fixture, transition, before = self.historical_semantic_fixture()
        for name in ("hasSample", "isSampleOf"):
            prepared = fixture.root / applicability.PREPARED / (name + "-forProperty.json")
            applicability.bind_prepared_applicability(fixture.root, prepared, transition["transition_id"])
        bound = applicability._bound_records(fixture.root)
        self.assertEqual(len(bound), 2)
        self.assertEqual({record["determination"]["classification"] for record in bound},
                         {applicability.NON_MATERIAL})
        evolved = audit.evolve_unreviewed_row_ids(fixture.root, fixture.document)
        raw, stats = audit.mapping.read_workbook(fixture.live)
        rows = audit.mapping.validate_and_process_rows(raw, fixture.resolver, stats)
        self.assertEqual(len(audit.validate(fixture.scope, evolved["records"], fixture.graph, rows)), 91)
        self.assert_historical_approvals_unchanged(fixture, before)

    def test_h_corrupt_original_sufficiency_evidence_fails_after_valid_documentary_evolution(self):
        self.documentary_candidate(record_update=True)
        record = next(record for record in self.inheritance_records()
                      if record["source_iri"].endswith("/MeasurementRange"))
        ref = copy.deepcopy(record["inheritance_sufficiency_evidence"])
        path = self.root / ref["path"]
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertNotEqual(audit.sha(path), ref["sha256"])
        with self.assertRaisesRegex(ValueError, "sufficiency evidence|retained evidence hash mismatch"):
            self.validate_current()
        self.assertEqual(record["inheritance_sufficiency_evidence"], ref)
        self.assert_original_custody(except_paths={ref["path"]})


if __name__ == "__main__":
    unittest.main()
