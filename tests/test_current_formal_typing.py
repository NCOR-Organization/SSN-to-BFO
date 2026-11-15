"""Explicit typing decisions retain evidence guards and mapping distinctions."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from openpyxl import Workbook
from rdflib import Graph, OWL, RDF

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as audit
import current_semantic_workbook as semantic


class FormalTypingApprovalTests(unittest.TestCase):
    """Disposable decisions only; no production decision or artifact is edited."""

    @classmethod
    def setUpClass(cls):
        cls.resolver = audit.mapping.Resolver()
        cls.target = Graph().parse(ROOT / audit.TARGET_PATH, format="turtle")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="formal-typing-decision-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for relative in (*audit.SOURCE_PATHS, audit.TARGET_PATH,
                         "config/current-ssn-sosa-scope.json",
                         "mappings/SOSA-next-to-BFO-COMS.xlsx",
                         audit.SOURCE_QUERY.relative_to(ROOT).as_posix()):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.iri = str(audit.mapping.SOSA.observedProperty)
        self.graph = Graph()
        self.graph.add((audit.mapping.SOSA.observedProperty, RDF.type, OWL.ObjectProperty))
        self.live = self.root / semantic.WORKBOOK
        self.make_workbook()
        self.before = {
            "source_iri": self.iri, "source_kind": "object_property",
            "source_label": "observed property", "review_state": "unreviewed",
            "assessment_outcome": "unreviewed", "rationale": "Disposable prior rationale.",
            "mapping_row_ids": sorted(row.row.stable_row_id for row in self.rows),
            "evidence": ["fixture-instructions.txt"], "notes": "Disposable test evidence.",
            "review": {"question": "Adopt these exact source-class typing assertions?",
                       "alternatives": ["Retain unresolved", "Approve explicit typing"],
                       "recommendation": "Requires explicit approval", "confidence": "Fixture"},
        }
        (self.root / "fixture-instructions.txt").write_text("Disposable test authorization only.\n")
        self.record = copy.deepcopy(self.before)
        self.record.update(review_state="final", assessment_outcome="formal_mapping_adopted",
                           rationale="Fixture explicitly approves OWL source-class typing.")
        self.patches = [patch.object(audit, "ROOT", self.root),
                        patch.object(audit, "SOURCE_QUERY", self.root / audit.SOURCE_QUERY.relative_to(ROOT))]
        for context in self.patches:
            context.start()
            self.addCleanup(context.stop)
        self.make_decision()

    def make_workbook(self, formal=False):
        book = Workbook()
        book.active.title = "Sheet1"
        book.active.append(audit.documentary.HEADERS)
        book.active.append(["sosa:Observation", "rdfs:subClassOf", "cco:PlannedAct",
                            "Unrelated fixture row", "urn:uuid:" + str(uuid4())])
        sheet = book.create_sheet("Sheet2")
        sheet.append(audit.documentary.HEADERS)
        assertions = [("rdfs:domain", "sosa:Observation"),
                      ("rdfs:range", "sosa:ObservableProperty")]
        if formal:
            assertions.append(("rdfs:subPropertyOf", "cco:has_input"))
        for predicate, target in assertions:
            sheet.append(["sosa:observedProperty", predicate, target,
                          "Disposable test assertion", "urn:uuid:" + str(uuid4())])
        self.live.parent.mkdir(parents=True, exist_ok=True)
        book.save(self.live)
        book.close()
        raw, stats = audit.mapping.read_workbook(self.live)
        processed = audit.mapping.validate_and_process_rows(raw, self.resolver, stats)
        self.rows = [row for row in processed if str(row.subject) == self.iri]
        self.route = audit.coverage({self.iri: "object_property"}, self.graph, self.rows)[0]

    def bind(self, name, value):
        path = self.root / name
        path.write_text(audit.json_text(value))
        return {"path": name, "sha256": audit.sha(path)}

    def make_decision(self, formal=False):
        self.before["mapping_row_ids"] = sorted(row.row.stable_row_id for row in self.rows)
        self.record["mapping_row_ids"] = self.before["mapping_row_ids"][:]
        self.packet = audit.review_details(
            self.before, self.graph, self.target, self.rows, self.rows,
            self.route, audit.next_comparison(self.rows), {})[2]
        self.decision = {
            "schema_version": 1, "decision_id": "urn:uuid:" + str(uuid4()),
            "source_iri": self.iri, "review_state": "final",
            "assessment_outcome": "formal_mapping_adopted",
            "rationale": self.record["rationale"],
            "reviewer_identity": "Disposable fixture reviewer",
            "review_timestamp": "2026-11-14T12:00:00+00:00",
            "review_question": self.packet["human_question"],
            "question_response": "The fixture expressly approves the exact assertions.",
            "evidence_refs": self.record["evidence"],
            "mapping_row_ids": self.record["mapping_row_ids"],
            "formal_mapping_assertions": audit.decision_mapping_assertions(self.rows),
            "formal_coverage_sha256": audit.canonical_sha(self.route),
            "input_hashes": audit.decision_input_hashes(),
            "assessment_snapshot": {**self.bind("assessment-before.json", {"records": [self.before]}),
                                    "record_sha256": audit.canonical_sha(self.before)},
            "review_packet_snapshot": {**self.bind("review-packet.json", self.packet),
                                       "item_sha256": audit.canonical_sha(self.packet)},
        }
        if formal:
            self.decision.update(decision_basis="formal_mapping_approval", formal_mapping_approved=True)
        else:
            self.decision.update(decision_basis="formal_typing_approval", formal_typing_approved=True,
                                 formal_typing_assertions=audit.decision_typing_assertions(self.rows))
        self.save_decision()

    def save_decision(self):
        self.record["human_decision_record"] = self.bind("decision.json", self.decision)

    def authenticate(self):
        return audit.authenticate_human_decision(
            self.record, self.graph, self.target, self.rows, self.rows,
            self.route, audit.next_comparison(self.rows), set())

    def validate_assessment(self):
        scope = json.loads((self.root / "config/current-ssn-sosa-scope.json").read_text())
        scope["source_signature_sha256"] = audit.signature({self.iri: "object_property"})
        # Isolate this new assessment/authentication boundary from the unrelated
        # production inventory and historical-workbook applicability machinery.
        with patch.object(audit.documentary, "validate_immutable_decisions"), \
                patch.object(audit, "historical_finals", return_value={}), \
                patch.object(audit, "validate_human_decision", side_effect=audit.authenticate_human_decision):
            return audit.validate(scope, [self.record], self.graph, self.rows)

    def authority(self):
        row_values = [row for row in semantic.workbook_rows(self.live).values()
                      if row["subject"] == "sosa:observedProperty"]
        delta = {"changed_rows": [{"row_id": row["row_id"], "old": None, "new": row}
                                  for row in row_values], "semantic_changes": []}
        evidence = {"path": "fixture-instructions.txt",
                    "sha256": audit.sha(self.root / "fixture-instructions.txt"),
                    "reference": "Disposable exact-typing authorization"}
        authorities = {row["row_id"]: {
            "authorization_type": "EXPLICIT_NEW_HUMAN_DECISION",
            "rationale": self.record["rationale"], "evidence": [evidence],
            "human_decision": self.record["human_decision_record"],
        } for row in row_values}
        semantic._authority(self.root, authorities, delta, self.live)

    def test_exact_typing_approval_authenticates_and_preserves_coverage_distinction(self):
        self.authenticate()
        self.assertEqual(self.validate_assessment(), {self.iri: "object_property"})
        self.authority()
        self.assertEqual(audit.decision_mapping_assertions(self.rows), [])
        self.assertEqual(len(audit.decision_typing_assertions(self.rows)), 2)
        self.assertTrue(self.route["typing_only_in_workbook"])
        self.assertFalse(self.route["direct_formal_mapping"])
        self.assertTrue(self.route["no_established_formal_route"])
        self.assertFalse(audit.mapping.MAPPING_PREDICATES & audit.mapping.DOMAIN_RANGE_PREDICATES)

    def test_no_bound_decision_cannot_finalize_typing(self):
        self.record.pop("human_decision_record")
        with self.assertRaisesRegex(ValueError, "human decision record"):
            self.validate_assessment()

    def test_approval_flag_and_exact_assertions_are_required_at_both_boundaries(self):
        original = copy.deepcopy(self.decision)
        mutations = [lambda d: d.pop("formal_typing_approved"),
                     lambda d: d.update(formal_typing_approved=False),
                     lambda d: d.pop("formal_typing_assertions"),
                     lambda d: d.update(formal_typing_assertions=d["formal_typing_assertions"][:1]),
                     lambda d: d["formal_typing_assertions"][0].update(target="sosa:Sensor"),
                     lambda d: d["formal_typing_assertions"][0].update(row_id="urn:uuid:" + str(uuid4())),
                     lambda d: d.update(decision_basis="formal_mapping_approval", formal_mapping_approved=True)]
        for number, mutate in enumerate(mutations):
            with self.subTest(mutation=number):
                self.decision = copy.deepcopy(original)
                mutate(self.decision)
                self.save_decision()
                for check in (self.authenticate, self.validate_assessment, self.authority):
                    with self.assertRaises(ValueError):
                        check()

    def test_typing_approval_cannot_cover_a_competing_superproperty(self):
        self.make_workbook(formal=True)
        self.make_decision()
        for check in (self.authenticate, self.authority):
            with self.assertRaisesRegex(ValueError, "typing-only assertions"):
                check()

    def test_formal_mapping_approval_keeps_previous_assertions_and_guards(self):
        self.make_workbook(formal=True)
        self.make_decision(formal=True)
        self.assertNotIn("formal_typing_assertions", self.decision)
        self.authenticate()
        self.authority()
        self.decision["formal_mapping_approved"] = False
        self.save_decision()
        for check in (self.authenticate, self.authority):
            with self.assertRaisesRegex(ValueError, "approve.*formal mapping"):
                check()

    def test_typing_path_still_requires_exact_packet_and_decision_bytes(self):
        (self.root / "decision.json").write_text((self.root / "decision.json").read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "human decision record"):
            self.authenticate()
        self.save_decision()
        self.packet["formal_consequences"] = []
        self.decision["review_packet_snapshot"] = {
            **self.bind("review-packet.json", self.packet),
            "item_sha256": audit.canonical_sha(self.packet)}
        self.save_decision()
        with self.assertRaisesRegex(ValueError, "review packet mismatch"):
            self.authenticate()


if __name__ == "__main__":
    unittest.main()
