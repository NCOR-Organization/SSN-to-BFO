"""Materiality and real sample-pair carry-forward in disposable workbooks only."""
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
import current_assessment as audit
import current_decision_applicability as applicability
import current_documentary_workbook as documentary
import current_semantic_workbook as semantic

HISTORICAL_START_SHA = "9e526e5705fc84571e03616f74c59fe8654fcc073a1c45a281109cf22c276e14"
HISTORICAL_ASSESSMENT = "reports/current-human-decisions/2026-10-26-three-term-adjudication/assessment-before.json"
HISTORICAL_ASSESSMENT_SHA = "f3680339a8661aead8c6a4bc359857fd948fadc4de2f096b33144ae97f9c0689"


class SemanticApplicabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = audit.source_graph()
        cls.target = Graph().parse(ROOT / audit.TARGET_PATH, format="turtle")
        cls.resolver = audit.mapping.Resolver()
        cls.scope = json.loads(audit.SCOPE.read_text())
        historical = ROOT / HISTORICAL_ASSESSMENT
        if audit.sha(historical) != HISTORICAL_ASSESSMENT_SHA:
            raise ValueError("historical semantic applicability fixture drift")
        cls.document = json.loads(historical.read_text())

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="semantic-applicability-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        paths = set(documentary.evidence_paths(ROOT)) | set(applicability.evidence_paths(ROOT))
        paths.update(semantic.SOURCE_TARGET_PATHS)
        paths.update({"config/current-ssn-sosa-scope.json", "config/publication-metadata.toml",
                      "config/current-ssn-sosa-historical-finals.json", "mappings/SSN2BFO-COMS.xlsx",
                      "mappings/SOSA-next-to-BFO-COMS.xlsx", "mappings/current-ssn-sosa-assessment.json",
                      "queries/source-classes-and-object-properties.rq", audit.RULE_PATH})
        paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / "imports").glob("*.ttl"))
        for relative in paths:
            if relative.startswith((semantic.TRANSITIONS + "/", applicability.RECORDS + "/")):
                continue
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.live = self.root / documentary.WORKBOOK
        shutil.copyfile(ROOT / documentary.VERSIONS / (HISTORICAL_START_SHA + ".xlsx"), self.live)
        shutil.copyfile(ROOT / HISTORICAL_ASSESSMENT, self.root / "mappings/current-ssn-sosa-assessment.json")
        self.records = copy.deepcopy(self.document["records"])
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, path in (("ROOT", self.root), ("SCOPE", self.root / "config/current-ssn-sosa-scope.json"),
                           ("SOURCE_QUERY", self.root / "queries/source-classes-and-object-properties.rq"),
                           ("ASSESSMENT", self.root / "mappings/current-ssn-sosa-assessment.json"),
                           ("HISTORICAL_FINAL_BASELINE", self.root / "config/current-ssn-sosa-historical-finals.json")):
            self.stack.enter_context(patch.object(audit, name, path))

    def decision(self, name="hasSample"):
        base = self.root / "reports/current-human-decisions/2026-10-25-sample-pair"
        return json.loads((base / (name + ".json")).read_text())

    def state(self, name="hasSample"):
        decision = self.decision(name)
        packet = json.loads((self.root / decision["review_packet_snapshot"]["path"]).read_text())
        return {"source_exists": True, "coverage": packet["coverage_evidence"], "packet": packet}

    def candidate(self, changes=(), append=(), source=None):
        path = self.root / (str(uuid4()) + ".xlsx")
        book = load_workbook(source or self.live)
        for sheet, cell, value in changes:
            book[sheet][cell] = value
        for row in append:
            book["Sheet2"].append(row)
        book.save(path)
        book.close()
        return path

    def check_step(self, old, new, before=None, after=None, decision=None):
        applicability.validate_step(self.root, decision or self.decision(), old, new,
                                    {"transition_id": str(uuid4())},
                                    before or self.state(), after or self.state())

    def create_transition(self, old, new):
        evidence = self.root / "fixture-transition-authorization.json"
        evidence.write_text('{"scope":"Explicit disposable fixture only; no repository semantic decision."}\n')
        ref = {"path": evidence.relative_to(self.root).as_posix(), "sha256": audit.sha(evidence),
               "reference": "Isolated test fixture authorization"}
        authorities = {}
        for row in semantic.workbook_delta(old, new)["changed_rows"]:
            category = "RESTORE_PREVIOUSLY_APPROVED_DECISION"
            if row["old"] and (not row["new"] or not row["new"]["predicate"]):
                category = "REMOVE_PREVIOUSLY_REJECTED_MAPPING"
            authorities[row["row_id"]] = {"authorization_type": category,
                                          "rationale": "Disposable transition fixture.", "evidence": [ref]}
        return semantic.create_transition(self.root, old, new, authorities,
                                          editor_identity="Disposable test editor")

    def test_own_predicate_target_typing_and_rowid_changes_are_material(self):
        cases = [[("Sheet2", "B16", "rdfs:subPropertyOf"), ("Sheet2", "C16", "cco:represented_by")],
                 [("Sheet2", "C16", "new target")],
                 [("Sheet2", "B16", "rdfs:domain"), ("Sheet2", "C16", "sosa:Sample")],
                 [("Sheet2", "E16", "urn:uuid:" + str(uuid4()))]]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN.*A/B/C/E"):
                self.check_step(self.live, self.candidate(changes))

    def test_own_new_formal_mapping_and_removed_approved_mapping_require_reopen(self):
        candidate = self.candidate(append=[["sosa:hasSample", "rdfs:subPropertyOf", "cco:represented_by", "Fixture", "urn:uuid:" + str(uuid4())]])
        with self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN"):
            self.check_step(self.live, candidate)
        with self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN"):
            self.check_step(candidate, self.live)

    def test_padded_subject_is_selected_without_normalizing_compared_semantic_cells(self):
        padded = self.candidate([("Sheet2", "A16", "  sosa:hasSample  ")])
        iri = self.decision()["source_iri"]
        own = applicability.own_semantic_rows(padded, iri)
        self.assertEqual(len(own), 1)
        self.assertEqual(own[0]["values"][0], "  sosa:hasSample  ")
        changed = self.candidate([("Sheet2", "C16", "  ")], source=padded)
        with self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN.*A/B/C/E"):
            self.check_step(padded, changed)

    def test_direct_inherited_and_rule_coverage_changes_are_material(self):
        for key in ("direct_formal_mapping", "inherited_formal_mapping", "rule_or_chain_route"):
            after = self.state()
            after["coverage"][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN.*coverage"):
                self.check_step(self.live, self.live, after=after)

    def test_source_disappearance_and_source_target_packet_semantics_require_reopen(self):
        after = self.state()
        after["source_exists"] = False
        with self.assertRaisesRegex(ValueError, "source term no longer exists"):
            self.check_step(self.live, self.live, after=after)
        for key in ("source_semantics", "target_semantics"):
            after = self.state()
            after["packet"][key] = {"changed": True}
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN.*packet dependency"):
                self.check_step(self.live, self.live, after=after)

    def test_changed_context_requires_record_and_premise_cannot_be_demoted(self):
        after = self.state()
        after["packet"]["mapping_property_chains"] = []
        with self.assertRaisesRegex(ValueError, "explicit non-material determination"):
            self.check_step(self.live, self.live, after=after)
        for field, value in (("rationale_dependency_keys", ["mapping_property_chains"]),
                             ("rationale", "The ssn:forProperty chain is a premise of this conclusion.")):
            decision = self.decision()
            decision[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN.*(premise|rationale)"):
                self.check_step(self.live, self.live, after=after, decision=decision)

    def test_unrelated_row_absent_from_packet_is_nonmaterial(self):
        candidate = self.candidate([("Sheet1", "C2", "bfo:Process")])
        self.check_step(self.live, candidate)

    def test_prepared_determinations_are_not_active_and_cannot_be_tampered(self):
        for name in ("hasSample", "isSampleOf"):
            path = self.root / applicability.PREPARED / (name + "-forProperty.json")
            record = applicability._validate_prepared(self.root, path)
            self.assertEqual(record["classification"], applicability.NON_MATERIAL)
            self.assertEqual(record["reviewer_identity"], "Alec Sculley")
            self.assertIsNone(record["new_workbook"]["sha256"])
            relocated = self.root / applicability.PREPARED / ("forged-" + name + ".json")
            relocated.write_bytes(path.read_bytes())
            with self.assertRaisesRegex(ValueError, "unregistered human"):
                applicability._validate_prepared(self.root, relocated)
            relocated.unlink()
            with self.assertRaisesRegex(ValueError, "validated semantic transition"):
                applicability.bind_prepared_applicability(self.root, path, str(uuid4()))
            record["rationale"] = "Forged premise change is unrelated."
            path.write_bytes(documentary.canonical_bytes(record))
            with self.assertRaisesRegex(ValueError, "immutable prepared"):
                applicability._validate_prepared(self.root, path)

    def test_historical_authentication_is_independent_of_unrecorded_current_change(self):
        candidate = self.candidate([("Sheet1", "C2", "bfo:Process")])
        shutil.copyfile(candidate, self.live)
        decision = self.decision()
        record = next(r for r in self.records if r["source_iri"] == decision["source_iri"])
        raw, stats = audit.mapping.read_workbook(self.live)
        rows = audit.mapping.validate_and_process_rows(raw, self.resolver, stats)
        own = [r for r in rows if str(r.subject) == record["source_iri"]]
        route = audit.coverage({record["source_iri"]: record["source_kind"]}, self.graph, rows)[0]
        authenticated = audit.authenticate_human_decision(
            record, self.graph, self.target, rows, own, route, audit.next_comparison(rows), set())
        self.assertEqual(audit.sha(authenticated["workbook"]), decision["input_hashes"]["workbook_sha256"])
        with self.assertRaisesRegex(ValueError, "complete documentary update chain"):
            audit.validate_human_decision(record, self.graph, self.target, rows, own,
                                          route, audit.next_comparison(rows), set())

    def test_real_five_term_transition_preserves_history_and_sample_decisions(self):
        before_files = {p: (self.root / p).read_bytes()
                        for p in documentary.evidence_paths(self.root)
                        if "current-human-decisions" in p}
        additions = [["sosa:madeBySensor", "rdfs:subPropertyOf", "cco:has_agent", "Historical restoration fixture.",
                      "urn:uuid:2876e7da-9716-4fe9-ab0e-7f118e6f9146"],
                     ["sosa:madeObservation", "rdfs:subPropertyOf", "cco:agent_in", "Historical restoration fixture.",
                      "urn:uuid:b1d0b7d5-e004-4680-a738-1dc7d8d0edff"]]
        changes = [(sheet, f"{column}{row}", None)
                   for sheet, row in (("Sheet2", 49), ("Sheet1", 43), ("Sheet1", 45))
                   for column in "BC"]
        candidate = self.candidate(changes, additions)
        self.assertEqual(documentary.semantic_projection_sha256(candidate),
                         "101ff4cc24f493b90fadb70fb7cfcef26ba07f81c7b2670f7f8ce3f5c5172a45")
        transition_path = self.create_transition(self.live, candidate)
        transition = json.loads(transition_path.read_text())
        shutil.copyfile(candidate, self.live)
        evolved = audit.evolve_unreviewed_row_ids(self.root, self.document)
        self.assertEqual(audit.evolve_unreviewed_row_ids(
            self.root, evolved, from_workbook_sha256=transition["new_workbook_sha256"]), evolved)
        with self.assertRaisesRegex(ValueError, "exact starting membership"):
            audit.evolve_unreviewed_row_ids(self.root, evolved)
        changed = [r["source_iri"] for old, r in zip(self.document["records"], evolved["records"], strict=True) if old != r]
        self.assertEqual(set(changed), {str(audit.mapping.SOSA.madeBySensor), str(audit.mapping.SOSA.madeObservation)})
        for old, new in zip(self.document["records"], evolved["records"], strict=True):
            self.assertEqual({k: v for k, v in old.items() if k != "mapping_row_ids"},
                             {k: v for k, v in new.items() if k != "mapping_row_ids"})
        raw, stats = audit.mapping.read_workbook(self.live)
        rows = audit.mapping.validate_and_process_rows(raw, self.resolver, stats)
        with self.assertRaisesRegex(ValueError, "explicit non-material determination"):
            audit.validate(self.scope, evolved["records"], self.graph, rows)
        for name in ("hasSample", "isSampleOf"):
            prepared = self.root / applicability.PREPARED / (name + "-forProperty.json")
            applicability.bind_prepared_applicability(self.root, prepared, transition["transition_id"])
        self.assertEqual(len(audit.validate(self.scope, evolved["records"], self.graph, rows)), 91)
        self.assertNotEqual(audit.sha(self.live), self.decision()["input_hashes"]["workbook_sha256"])
        for relative, original in before_files.items():
            self.assertEqual((self.root / relative).read_bytes(), original)
        for name in ("hasSample", "isSampleOf"):
            decision = self.decision(name)
            record = next(r for r in evolved["records"] if r["source_iri"] == decision["source_iri"])
            self.assertEqual(record, next(r for r in self.document["records"] if r["source_iri"] == decision["source_iri"]))
        # A later unrelated semantic link must be checked independently, and
        # must not require rewriting or rebinding either historical approval.
        second = self.candidate([("Sheet1", "C2", "bfo:Process")])
        self.create_transition(self.live, second)
        shutil.copyfile(second, self.live)
        raw, stats = audit.mapping.read_workbook(self.live)
        rows = audit.mapping.validate_and_process_rows(raw, self.resolver, stats)
        self.assertEqual(len(audit.validate(self.scope, evolved["records"], self.graph, rows)), 91)

    def test_unreviewed_membership_derivation_rejects_finalized_and_unrecorded_changes(self):
        candidate = self.candidate(append=[["sosa:hasSample", "rdfs:domain", "sosa:FeatureOfInterest", "Fixture",
                                            "urn:uuid:" + str(uuid4())]])
        with self.assertRaisesRegex(ValueError, "complete documentary update chain"):
            audit.evolve_unreviewed_row_ids(self.root, self.document, candidate)
        # Isolate the mechanical membership boundary from transition-schema
        # tests: even a governed transition cannot mutate a finalized record.
        step = {"old_workbook_sha256": "old", "new_workbook_sha256": "new"}
        history = {"chain": [step], "baseline": {"historical_workbook": {"sha256": "old"}},
                   "version_sha256": ["old", "new"], "tail_sha256": "new"}
        with patch.object(semantic, "resolve_history", return_value=history), patch.object(
                semantic, "snapshot", side_effect=lambda root, sha: self.live if sha == "old" else candidate):
            with self.assertRaisesRegex(ValueError, "MATERIAL_REQUIRES_REOPEN.*RowID evolution"):
                audit.evolve_unreviewed_row_ids(self.root, self.document)

    def test_rowid_evolution_rejects_unrelated_bad_starting_membership(self):
        document = copy.deepcopy(self.document)
        document["records"][0]["mapping_row_ids"] = ["urn:uuid:" + str(uuid4())]
        with self.assertRaisesRegex(ValueError, "exact starting membership"):
            audit.evolve_unreviewed_row_ids(self.root, document)


if __name__ == "__main__":
    unittest.main()
