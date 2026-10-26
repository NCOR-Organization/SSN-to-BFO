"""Real sample-pair custody survives only explicitly recorded documentary edits.

Every mutation is confined to a disposable project copy. The maintained
workbook, assessment, approved decisions, and retained packets are read-only.
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

from openpyxl import load_workbook
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as audit
import current_documentary_workbook as documentary


class DocumentaryDecisionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = json.loads(audit.SCOPE.read_text())
        cls.document = json.loads(audit.ASSESSMENT.read_text())
        cls.graph = audit.source_graph()
        cls.target = Graph().parse(ROOT / audit.TARGET_PATH, format="turtle")
        cls.resolver = audit.mapping.Resolver()
        cls.workbook_relative = "mappings/SSN2BFO-COMS.xlsx"
        cls.pair_directory = Path("reports/current-human-decisions/2026-10-25-sample-pair")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="documentary-decision-integration-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.records = copy.deepcopy(self.document["records"])
        paths = {*audit.SOURCE_PATHS, audit.TARGET_PATH, self.workbook_relative,
                 "mappings/SOSA-next-to-BFO-COMS.xlsx", "mappings/current-ssn-sosa-assessment.json",
                 "queries/source-classes-and-object-properties.rq"}
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT / "config").glob("current-*.json"))
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT / self.pair_directory).rglob("*") if p.is_file())
        self.copy_paths(paths)
        self.copy_documentary_baseline()
        self.workbook = self.root / self.workbook_relative
        # These A–P scenarios model evolution from the original approved
        # evidence, independently of documentary changes installed since then.
        baseline = json.loads((self.root / documentary.BASELINE).read_text())
        shutil.copyfile(self.root / baseline["historical_workbook"]["path"], self.workbook)
        self.historical_sha = audit.sha(self.workbook)
        self.protected = {
            relative: (self.root / relative).read_bytes()
            for relative in paths
            if relative.startswith(str(self.pair_directory))
            or relative == "mappings/current-ssn-sosa-assessment.json"
        }
        self.patch_stack = ExitStack()
        self.addCleanup(self.patch_stack.close)
        for name, path in (("ROOT", self.root),
                           ("SOURCE_QUERY", self.root / "queries/source-classes-and-object-properties.rq"),
                           ("SCOPE", self.root / "config/current-ssn-sosa-scope.json"),
                           ("ASSESSMENT", self.root / "mappings/current-ssn-sosa-assessment.json"),
                           ("HISTORICAL_FINAL_BASELINE", self.root / "config/current-ssn-sosa-historical-finals.json")):
            self.patch_stack.enter_context(patch.object(audit, name, path))

    def copy_paths(self, paths):
        for relative in sorted(paths):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def copy_documentary_baseline(self):
        """Copy the immutable custody anchor and historical workbook evidence."""
        baseline = json.loads((ROOT / documentary.BASELINE).read_text())
        self.copy_paths({documentary.BASELINE, baseline["historical_workbook"]["path"],
                         *(ref["path"] for ref in baseline["immutable_evidence"])})

    def add_update(self, changes):
        """Change D in the disposable workbook and retain a complete transition."""
        candidate = self.root / "candidate-workbook.xlsx"
        book = load_workbook(self.workbook)
        try:
            for (sheet, cell), value in changes.items():
                book[sheet][cell] = value
            book.save(candidate)
        finally:
            book.close()
        # The fixture deliberately documents its own artificial prose. Real
        # approved-rationale replacements instead cite the unchanged decisions.
        evidence_path = self.root / f"fixture-documentary-evidence-{audit.sha(candidate)}.json"
        evidence_path.write_text(audit.json_text({
            "scope": "Disposable documentary test values; no semantic approval.",
            "values": {f"{sheet}!{cell}": value for (sheet, cell), value in changes.items()},
        }))
        evidence = {}
        for sheet, cell in changes:
            ref = evidence_path
            if (sheet, cell) in self.approved_changes() and changes[sheet, cell] == self.approved_changes()[sheet, cell]:
                ref = self.decision("hasSample" if cell == "D16" else "isSampleOf")[1]
            evidence[f"{sheet}!{cell}"] = [{"path": ref.relative_to(self.root).as_posix(),
                                            "sha256": audit.sha(ref), "reference": f"{sheet}!{cell}"}]
        update = documentary.create_update(
            self.root, self.workbook, candidate, evidence,
            editor_identity="Disposable test fixture editor", timestamp="2026-10-25T23:00:00+00:00")
        shutil.copyfile(candidate, self.workbook)
        return update

    def rows(self):
        rows, stats = audit.mapping.read_workbook(self.workbook)
        return audit.mapping.validate_and_process_rows(rows, self.resolver, stats)

    def validate(self):
        return audit.validate(self.scope, self.records, self.graph, self.rows())

    def pair_record(self, name):
        return next(r for r in self.records if r["source_iri"] == str(audit.mapping.SOSA[name]))

    def decision(self, name):
        record = self.pair_record(name)
        path = self.root / record["human_decision_record"]["path"]
        return json.loads(path.read_text()), path

    def approved_changes(self):
        return {("Sheet2", "D16"): self.decision("hasSample")[0]["rationale"],
                ("Sheet2", "D17"): self.decision("isSampleOf")[0]["rationale"]}

    def assert_pair_preserved(self):
        for relative, data in self.protected.items():
            self.assertEqual((self.root / relative).read_bytes(), data, relative)
        self.assertEqual(self.records, self.document["records"])
        rows = self.rows()
        for name in ("hasSample", "isSampleOf"):
            record = self.pair_record(name)
            self.assertEqual((record["review_state"], record["assessment_outcome"]),
                             ("final", "no_direct_mapping"))
            own = [r for r in rows if str(r.subject) == record["source_iri"]]
            self.assertEqual([r.row.stable_row_id for r in own], record["mapping_row_ids"])
            self.assertTrue(all(not r.predicate and not r.target for r in own))
            decision, _ = self.decision(name)
            self.assertEqual(decision["input_hashes"]["workbook_sha256"], self.historical_sha)
            self.assertEqual(decision["reviewer_identity"], "Alec Sculley")
        self.assertEqual(sum(r["review_state"] == "final" for r in self.records), 14)
        self.assertEqual(sum(r["review_state"] != "final" for r in self.records), 77)

    def test_a_unrelated_d_cell_preserves_real_pair_decisions(self):
        self.add_update({("Sheet1", "D2"): "Documentary fixture: preserve the existing mapping assertion."})
        self.assertNotEqual(audit.sha(self.workbook), self.historical_sha)
        self.assertEqual(len(self.validate()), 91)
        self.assert_pair_preserved()

    def test_b_many_d_cells_in_one_record_preserve_real_pair_decisions(self):
        changes = {(sheet, cell): "Documentary fixture: no semantic change."
                   for sheet, cell in (("Sheet1", "D2"), ("Sheet1", "D3"),
                                       ("Sheet1", "D4"), ("Sheet2", "D2"), ("Sheet2", "D11"))}
        self.add_update(changes)
        self.assertEqual(len(self.validate()), 91)
        self.assert_pair_preserved()

    def test_c_exact_approved_rationales_preserve_real_pair_decisions(self):
        self.add_update(self.approved_changes())
        self.assertEqual(len(self.validate()), 91)
        book = load_workbook(self.workbook, read_only=True, data_only=False)
        try:
            for (sheet, cell), value in self.approved_changes().items():
                self.assertEqual(book[sheet][cell].value, value)
        finally:
            book.close()
        self.assert_pair_preserved()

    def test_d_two_documentary_links_preserve_original_historical_binding(self):
        self.add_update({("Sheet1", "D2"): "First documentary fixture version."})
        middle_sha = audit.sha(self.workbook)
        self.add_update(self.approved_changes())
        self.assertNotEqual(middle_sha, self.historical_sha)
        self.assertNotEqual(audit.sha(self.workbook), middle_sha)
        self.assertEqual(len(self.validate()), 91)
        self.assert_pair_preserved()

    def test_e_changed_live_prose_does_not_rewrite_retained_predecision_packet(self):
        self.add_update(self.approved_changes())
        rows = self.rows()
        comparisons = audit.next_comparison(rows)
        for name in ("hasSample", "isSampleOf"):
            decision, _ = self.decision(name)
            original = json.loads((self.root / decision["assessment_snapshot"]["path"]).read_text())
            prior = next(r for r in original["records"] if r["source_iri"] == decision["source_iri"])
            retained = json.loads((self.root / decision["review_packet_snapshot"]["path"]).read_text())
            route = audit.coverage({prior["source_iri"]: prior["source_kind"]}, self.graph, rows)[0]
            own = [r for r in rows if str(r.subject) == prior["source_iri"]]
            _, _, live = audit.review_details(prior, self.graph, self.target, own, rows, route, comparisons, {})
            self.assertNotEqual(live, retained)
            self.assertEqual(live["current_mapping_state"][0]["existing_rationale"], decision["rationale"])
            self.assertEqual(audit.canonical_sha(retained), decision["review_packet_snapshot"]["item_sha256"])
        self.assertEqual(len(self.validate()), 91)
        self.assert_pair_preserved()

    def test_l_same_projection_without_transition_record_cannot_validate_decisions(self):
        book = load_workbook(self.workbook)
        book["Sheet1"]["D2"] = "Unrecorded documentary fixture."
        book.save(self.workbook)
        book.close()
        with self.assertRaises(ValueError):
            self.validate()

    def test_o_rewriting_decision_and_its_reference_cannot_hide_workbook_transition(self):
        self.add_update(self.approved_changes())
        decision, path = self.decision("hasSample")
        decision["input_hashes"]["workbook_sha256"] = audit.sha(self.workbook)
        path.write_text(audit.json_text(decision))
        self.pair_record("hasSample")["human_decision_record"]["sha256"] = audit.sha(path)
        with self.assertRaises(ValueError):
            self.validate()

    def test_p_documentary_record_cannot_change_finality_or_outcome(self):
        self.add_update(self.approved_changes())
        for changes in ({"review_state": "unreviewed", "assessment_outcome": "unreviewed"},
                        {"review_state": "deferred", "assessment_outcome": "deferred"},
                        {"review_state": "final", "assessment_outcome": "inheritance_sufficient"}):
            with self.subTest(changes=changes):
                self.records = copy.deepcopy(self.document["records"])
                self.pair_record("hasSample").update(changes)
                with patch.object(audit, "validate_human_decision", side_effect=AssertionError("Reached finality branch")):
                    with self.assertRaises(ValueError):
                        self.validate()

    def test_retained_packet_and_all_mutable_hashes_cannot_be_rewritten(self):
        self.add_update(self.approved_changes())
        decision, decision_path = self.decision("hasSample")
        packet_path = self.root / decision["review_packet_snapshot"]["path"]
        packet = json.loads(packet_path.read_text())
        packet["target_semantics"] = []
        packet_path.write_text(audit.json_text(packet))
        decision["review_packet_snapshot"]["sha256"] = audit.sha(packet_path)
        decision["review_packet_snapshot"]["item_sha256"] = audit.canonical_sha(packet)
        decision_path.write_text(audit.json_text(decision))
        self.pair_record("hasSample")["human_decision_record"]["sha256"] = audit.sha(decision_path)
        with self.assertRaises(ValueError):
            self.validate()


if __name__ == "__main__":
    unittest.main()
