"""Current project inventory equality, scope drift, and sound coverage directions."""
from __future__ import annotations

import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from uuid import uuid4
from types import SimpleNamespace
from unittest.mock import patch

from rdflib import Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.collection import Collection

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_assessment as audit
import current_semantic_workbook as semantic


class CurrentAssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = json.loads(audit.SCOPE.read_text())
        cls.document = json.loads(audit.ASSESSMENT.read_text())
        cls.graph = audit.source_graph()
        cls.rows = audit.processed_rows()

    def validate(self, records=None, scope=None, graph=None):
        return audit.validate(scope if scope is not None else self.scope,
                              records if records is not None else self.document["records"],
                              graph if graph is not None else self.graph, self.rows)

    def predecision_inputs(self, iri: str):
        """Use retained unresolved inputs when the real term has since been decided."""
        record = next(r for r in self.document["records"] if r["source_iri"] == iri)
        if record.get("human_decision_record"):
            decision = json.loads((ROOT / record["human_decision_record"]["path"]).read_text())
            document = json.loads((ROOT / decision["assessment_snapshot"]["path"]).read_text())
            packet = json.loads((ROOT / decision["review_packet_snapshot"]["path"]).read_text())
        else:
            document = copy.deepcopy(self.document)
            packet = next(p for p in json.loads((ROOT / "reports/current-ssn-sosa-human-review.json").read_text())["items"]
                          if p["source_iri"] == iri)
        return document, packet

    @contextmanager
    def synthetic_final_decision(self, iri: str, outcome: str):
        """Disposable current fixture; preserve any existing approval's custody."""
        maintained = next(r for r in self.document["records"] if r["source_iri"] == iri)
        before_document, packet = self.predecision_inputs(iri)
        records = copy.deepcopy(self.document["records"] if maintained.get("human_decision_record")
                                else before_document["records"])
        record = next(r for r in records if r["source_iri"] == iri)
        original = copy.deepcopy(record)
        if not maintained.get("human_decision_record"):
            record.update(review_state="final", assessment_outcome=outcome,
                          rationale=f"Synthetic reviewed decision for {iri}; fixture only.")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_paths = {*audit.SOURCE_PATHS, audit.TARGET_PATH, "mappings/SSN2BFO-COMS.xlsx",
                           "mappings/SOSA-next-to-BFO-COMS.xlsx", "config/current-ssn-sosa-scope.json",
                           "config/publication-metadata.toml", *semantic.GOVERNED_INPUT_SHA256}
            input_paths.update(audit.documentary.evidence_paths(ROOT))
            input_paths.update(audit.applicability.evidence_paths(ROOT))
            for current in records:
                if current.get("human_decision_record"):
                    relative = current["human_decision_record"]["path"]
                    input_paths.add(relative)
                    human = json.loads((ROOT / relative).read_text())
                    input_paths.update(human[key]["path"] for key in
                                       ("assessment_snapshot", "review_packet_snapshot"))
                    if current.get("inheritance_sufficiency_evidence"):
                        input_paths.add(current["inheritance_sufficiency_evidence"]["path"])
            for relative in sorted(input_paths):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            approved_decision = None
            if maintained.get("human_decision_record"):
                # Authenticate the copied mixed history without rewinding its
                # live tail. Applicability approvals belong to this original
                # decision ID and its exact historical inputs and rationale.
                approved_decision = audit.documentary._json(audit.documentary._bound_file(
                    root, maintained["human_decision_record"]))
                self.assertEqual(approved_decision["assessment_outcome"], outcome)
                self.assertTrue(any((root / semantic.TRANSITIONS).glob("*.json")))
                historical = semantic.validate_workbook_evolution(
                    root, approved_decision["input_hashes"]["workbook_sha256"])
                self.assertEqual(audit.sha(historical), approved_decision["input_hashes"]["workbook_sha256"])
                self.assertEqual(audit.sha(root / semantic.WORKBOOK), audit.sha(ROOT / semantic.WORKBOOK))
            raw_rows, stats = audit.mapping.read_workbook(root / "mappings/SSN2BFO-COMS.xlsx")
            fixture_rows = audit.mapping.validate_and_process_rows(raw_rows, audit.mapping.Resolver(), stats)
            if approved_decision is None:
                before_path = root / "assessment-before.json"
                before_path.write_text(audit.json_text(before_document))
                packet_path = root / "review-packet.json"
                packet_path.write_text(audit.json_text(packet))
            own = [row for row in fixture_rows if str(row.subject) == iri]
            route = next(r for r in audit.coverage({iri: original["source_kind"]}, self.graph, fixture_rows)
                         if r["source_iri"] == iri)
            # Only the disposable assessment points to the mutable test copy.
            # Original bound decision artifacts and complete history stay
            # intact; real immutable-record attacks use the documentary suite.
            with patch.object(audit, "ROOT", root), patch.object(
                    audit, "SOURCE_QUERY", root / audit.SOURCE_QUERY.relative_to(ROOT)), patch.object(
                    self, "rows", fixture_rows), patch.object(
                    audit.documentary, "validate_immutable_decisions", return_value=None):
                decision = approved_decision if approved_decision is not None else {
                    "schema_version": 1, "decision_id": "urn:uuid:" + str(uuid4()),
                    "source_iri": iri, "review_state": "final", "assessment_outcome": outcome,
                    "rationale": record["rationale"], "review_question": packet["human_question"],
                    "question_response": "I considered the source meaning and exact current mapping state; this fixture explicitly selects the stated outcome.",
                    "reviewer_identity": "Fixture reviewer; not a real human decision",
                    "review_timestamp": "2026-10-25T12:00:00+00:00",
                    "evidence_refs": record["evidence"],
                    "mapping_row_ids": sorted(record["mapping_row_ids"]),
                    "formal_mapping_assertions": audit.decision_mapping_assertions(own),
                    "input_hashes": audit.decision_input_hashes(),
                    "formal_coverage_sha256": audit.canonical_sha(route),
                    "assessment_snapshot": {"path": "assessment-before.json", "sha256": audit.sha(before_path),
                                            "record_sha256": audit.canonical_sha(original)},
                    "review_packet_snapshot": {"path": "review-packet.json", "sha256": audit.sha(packet_path),
                                               "item_sha256": audit.canonical_sha(packet)},
                }
                if approved_decision is None and outcome == "formal_mapping_adopted":
                    decision.update(decision_basis="formal_mapping_approval", formal_mapping_approved=True)
                elif approved_decision is None and outcome == "no_direct_mapping":
                    decision.update(decision_basis="semantic_rejection", explicit_no_direct_mapping_adopted=True,
                                    separate_semantic_conclusion="The source meaning does not warrant an adopted direct target relation in this fixture.")
                decision_path = root / "human-decision.json"

                def save():
                    decision_path.write_text(audit.json_text(decision))
                    record["human_decision_record"] = {"path": "human-decision.json", "sha256": audit.sha(decision_path)}

                save()
                yield records, record, decision, save, root

    def test_current_inventory_is_exact_and_independent_of_row_count(self):
        terms = self.validate()
        self.assertEqual(len(terms), 91)
        self.assertEqual(list(terms.values()).count("class"), 44)
        self.assertEqual(list(terms.values()).count("object_property"), 47)
        self.assertEqual(len(self.rows), 108)

    def test_missing_extra_and_duplicate_records_fail(self):
        records = copy.deepcopy(self.document["records"])
        cases = [records[:-1], records + [dict(records[0], source_iri="urn:extra")], records + [records[0]]]
        for case in cases:
            with self.subTest(case=len(case)), self.assertRaises(ValueError):
                self.validate(case)

    def test_kind_mismatch_fails(self):
        records = copy.deepcopy(self.document["records"])
        records[0]["source_kind"] = "object_property"
        with self.assertRaisesRegex(ValueError, "type inconsistency"):
            self.validate(records)

    def test_new_source_term_fails_signature_even_before_record_match(self):
        graph = Graph()
        for triple in self.graph:
            graph.add(triple)
        graph.add((URIRef("http://www.w3.org/ns/sosa/NewClass"), RDF.type, OWL.Class))
        with self.assertRaisesRegex(ValueError, "source-scope drift"):
            self.validate(graph=graph)

    def test_query_namespace_and_kind_scope_drift_fail(self):
        for key, value in [("query_sha256", "0" * 64), ("namespaces", ["urn:wrong:"]),
                           ("term_kinds", ["class"]), ("source_files", ["imports/sosa.ttl"])]:
            scope = copy.deepcopy(self.scope)
            scope[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "source-scope drift"):
                self.validate(scope=scope)

    def test_deprecated_and_datatype_policy_explicit(self):
        graph = Graph()
        p = "http://www.w3.org/ns/sosa/"
        graph.add((URIRef(p + "Deprecated"), RDF.type, OWL.Class))
        graph.add((URIRef(p + "Deprecated"), OWL.deprecated, Literal(True)))
        graph.add((URIRef(p + "Data"), RDF.type, OWL.DatatypeProperty))
        graph.add((URIRef(p + "Active"), RDF.type, OWL.ObjectProperty))
        self.assertEqual(audit.inventory(graph, self.scope), {p + "Active": "object_property"})

    def test_ambiguous_source_typing_fails(self):
        graph = Graph()
        term = URIRef("http://www.w3.org/ns/sosa/Ambiguous")
        graph.add((term, RDF.type, OWL.Class))
        graph.add((term, RDF.type, OWL.ObjectProperty))
        with self.assertRaisesRegex(ValueError, "type inconsistency"):
            audit.inventory(graph, self.scope)

    def test_row_id_and_unresolved_final_mismatch_fail(self):
        for change in [{"mapping_row_ids": []}, {"review_state": "final", "assessment_outcome": "unreviewed"},
                       {"assessment_outcome": "typing_only"}]:
            records = copy.deepcopy(self.document["records"])
            records[0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate(records)

    def test_no_direct_outcome_cannot_mask_active_axiom(self):
        records = copy.deepcopy(self.document["records"])
        records[0].update(review_state="final", assessment_outcome="no_direct_mapping")
        with self.assertRaisesRegex(ValueError, "no-direct outcome conflicts"):
            self.validate(records)

    def test_historical_final_baseline_is_exact_and_fixed(self):
        baseline = audit.historical_finals()
        finals = [r for r in self.document["records"] if r["review_state"] == "final"]
        historical = [r for r in finals if r["source_iri"] in baseline]
        self.assertEqual(set(baseline), {r["source_iri"] for r in historical})
        self.assertEqual(len(historical), 12)
        # The historical cohort stays fixed; later explicit approvals extend the live inventory.
        expected_later_finals = (
            {str(audit.mapping.SOSA[name]) for name in ("hasSample", "isSampleOf", "Observation", "observedProperty", "Platform")} |
            {"http://www.w3.org/ns/ssn/forProperty",
             "http://www.w3.org/ns/ssn/Deployment",
             "http://www.w3.org/ns/ssn/System",
             "http://www.w3.org/ns/ssn/systems/SystemProperty",
             "http://www.w3.org/ns/ssn/systems/MeasurementRange"} |
            {"http://www.w3.org/ns/sosa/sampling/" + name for name in
             ("SampleRelationship", "hasSampleRelationship", "relatedSample")}
        )
        self.assertEqual(len(finals), len(baseline) + len(expected_later_finals))
        self.assertEqual({r["source_iri"] for r in finals} - set(baseline), expected_later_finals)
        for record in historical:
            self.assertEqual(baseline[record["source_iri"]]["assessment_record_sha256"],
                             audit.canonical_sha(record))
        records = copy.deepcopy(self.document["records"])
        record = next(r for r in records if r["source_iri"] in baseline)
        record["rationale"] += " Altered documentary decision."
        with self.assertRaisesRegex(ValueError, "human decision record"):
            self.validate(records)
        with tempfile.TemporaryDirectory() as tmp:
            forged = Path(tmp) / "baseline.json"
            forged.write_text(audit.HISTORICAL_FINAL_BASELINE.read_text().replace("twelve", "thirteen"))
            with patch.object(audit, "HISTORICAL_FINAL_BASELINE", forged), self.assertRaisesRegex(ValueError, "baseline hash drift"):
                self.validate()

    def test_formal_mapping_finality_bypass_matrix(self):
        iri = str(audit.mapping.SOSA.Actuation)
        records = copy.deepcopy(self.document["records"])
        record = next(r for r in records if r["source_iri"] == iri)
        self.assertTrue(audit.decision_mapping_assertions([row for row in self.rows if str(row.subject) == iri]))
        record.update(review_state="final", assessment_outcome="formal_mapping_adopted")
        for label, mutation in (("A state and outcome", lambda: None),
                                ("B arbitrary rationale", lambda: record.update(rationale="Arbitrary final rationale")),
                                ("C nonexistent path", lambda: record.update(human_decision_record={"path": "missing.json", "sha256": "0" * 64}))):
            with self.subTest(label=label):
                mutation()
                with self.assertRaisesRegex(ValueError, "human decision record"):
                    self.validate(records)
        with self.synthetic_final_decision(iri, "formal_mapping_adopted") as (records, _, decision, save, root):
            # This fixture retains the actual inheritance decisions and their
            # history, so their bound query is a required copied dependency.
            query_relative = audit.SOURCE_QUERY.relative_to(root).as_posix()
            query_bytes = (ROOT / query_relative).read_bytes()
            self.assertEqual(audit.SOURCE_QUERY.read_bytes(), query_bytes)
            self.assertEqual(audit.sha(audit.SOURCE_QUERY), semantic.GOVERNED_INPUT_SHA256[query_relative])
            inherited = [r for r in records if r["assessment_outcome"] == "inheritance_sufficient"]
            self.assertEqual(len(inherited), 2)
            for inherited_record in inherited:
                evidence = audit.documentary._json(audit.documentary._bound_file(
                    root, inherited_record["inheritance_sufficiency_evidence"]))
                self.assertEqual(evidence["input_sha256"][query_relative], audit.sha(audit.SOURCE_QUERY))
            audit.SOURCE_QUERY.unlink()
            try:
                with self.assertRaisesRegex(FileNotFoundError, "source-classes-and-object-properties.rq"):
                    semantic.resolve_history(root)
            finally:
                audit.SOURCE_QUERY.write_bytes(query_bytes)
            self.validate(records)  # Valid fixture; no real assessment file is changed.
            for label, key, value, error in (
                ("D wrong term", "source_iri", str(audit.mapping.SOSA.Sampler), "decision/assessment mismatch"),
                ("E stale inputs", "input_hashes", {}, "stale human decision governed inputs"),
                ("F wrong outcome", "assessment_outcome", "no_direct_mapping", "decision/assessment mismatch"),
                ("no mapping approval", "formal_mapping_approved", False, "does not approve current formal mapping")):
                with self.subTest(label=label):
                    original = copy.deepcopy(decision[key])
                    decision[key] = value
                    save()
                    with self.assertRaisesRegex(ValueError, error):
                        self.validate(records)
                    decision[key] = original
                    save()
            self.validate(records)

    def test_no_direct_finality_bypass_matrix(self):
        iri = str(audit.mapping.SOSA.hasSample)
        before_document, _ = self.predecision_inputs(iri)
        records = copy.deepcopy(before_document["records"])
        record = next(r for r in records if r["source_iri"] == iri)
        record.update(review_state="final", assessment_outcome="no_direct_mapping")
        with self.assertRaisesRegex(ValueError, "human decision record|immutable"):
            self.validate(records)  # G deferred blank -> final by state edit.
        record["rationale"] = "Arbitrary rationale only."
        with self.assertRaisesRegex(ValueError, "human decision record|immutable"):
            self.validate(records)  # H rationale text is not a decision.
        with self.synthetic_final_decision(iri, "no_direct_mapping") as (records, _, decision, save, _):
            self.validate(records)
            for basis in ("implementation_or_profile_limitation", "inheritance_sufficiency"):
                with self.subTest(basis=basis):
                    decision["decision_basis"] = basis
                    save()
                    with self.assertRaisesRegex(ValueError, "separate semantic no-direct conclusion"):
                        self.validate(records)
            decision["decision_basis"] = "semantic_rejection"
            decision["separate_semantic_conclusion"] = ""
            save()
            with self.assertRaisesRegex(ValueError, "separate semantic no-direct conclusion"):
                self.validate(records)

    def test_refreshed_packet_hash_cannot_hide_omitted_target_or_cross_track_facts(self):
        iri = str(audit.mapping.SOSA.Actuation)
        for field, replacement in (("target_semantics", []), ("pinned_track_comparison", None)):
            with self.subTest(field=field), self.synthetic_final_decision(iri, "formal_mapping_adopted") as (records, _, decision, save, root):
                packet_path = root / "review-packet.json"
                packet = json.loads(packet_path.read_text())
                self.assertTrue(packet[field])
                packet[field] = replacement
                packet_path.write_text(audit.json_text(packet))
                decision["review_packet_snapshot"]["sha256"] = audit.sha(packet_path)
                decision["review_packet_snapshot"]["item_sha256"] = audit.canonical_sha(packet)
                save()  # All mutable hashes agree with the truncated packet.
                with self.assertRaisesRegex(ValueError, "review packet mismatch"):
                    self.validate(records)

    def test_current_formal_row_or_historical_recommendation_cannot_finalize_without_record(self):
        # I: current workbook assertion; J: prior review recommendation. Neither is a new decision.
        for iri in (str(audit.mapping.SOSA.Actuation), str(audit.mapping.SOSA.Sampler)):
            with self.subTest(iri=iri):
                records = copy.deepcopy(self.document["records"])
                record = next(r for r in records if r["source_iri"] == iri)
                record.update(review_state="final", assessment_outcome="formal_mapping_adopted")
                with self.assertRaisesRegex(ValueError, "human decision record"):
                    self.validate(records)

    def test_invalid_finality_transition_fails_before_queue_or_rationale_generation(self):
        altered = copy.deepcopy(self.document)
        record = next(r for r in altered["records"] if r["source_iri"] == str(audit.mapping.SOSA.Actuation))
        record.update(review_state="final", assessment_outcome="formal_mapping_adopted")
        with self.assertRaisesRegex(ValueError, "human decision record"):
            audit.build_reports(self.scope, altered)
        _, rationales, queue, _ = audit.build_reports(self.scope, self.document)
        self.assertIn(record["source_iri"], {item["source_iri"] for item in queue["items"]})
        proposal = next(item for item in rationales["proposals"] if item["source_iri"] == record["source_iri"])
        # Documentary completion may make the prose safe to adopt while the
        # attempted semantic finalization is still rejected and queued.
        queued = next(item for item in queue["items"] if item["source_iri"] == record["source_iri"])
        self.assertEqual(queued["review_state"], "unreviewed")
        self.assertTrue(proposal["semantic_decision_still_required"])

    def test_audit_observes_cannot_be_final_inheritance_sufficient(self):
        records = copy.deepcopy(self.document["records"])
        observed = next(r for r in records if r["source_iri"] == str(audit.mapping.SOSA.observes))
        observed.update(review_state="final", assessment_outcome="inheritance_sufficient")
        with self.assertRaisesRegex(ValueError, "lacks an inherited formal route"):
            self.validate(records)

    @contextmanager
    def synthetic_sufficiency(self):
        """Manually state one reviewed decision and its actual source-to-target route."""
        child, parent = map(URIRef, [str(audit.mapping.SOSA) + name for name in ("FixtureChild", "FixtureParent")])
        graph = Graph()
        for iri in (child, parent):
            graph.add((iri, RDF.type, OWL.ObjectProperty))
        graph.add((child, RDFS.subPropertyOf, parent))
        row = SimpleNamespace(subject=parent, predicate="rdfs:subPropertyOf", target="bfo:BFO_0000057",
                              expr=None, property_chain=[], target_property=None,
                              row=SimpleNamespace(stable_row_id="urn:fixture:parent-row",
                                                  row_id="Sheet1!2", reasoning_text="",
                                                  subject_text="sosa:FixtureParent"))
        terms = {str(child): "object_property", str(parent): "object_property"}
        scope = copy.deepcopy(self.scope)
        scope["source_signature_sha256"] = hashlib.sha256(audit.json_text(terms).encode()).hexdigest()
        inherited_routes = [{"via_source": str(parent),
                             "source_path": ["sosa:FixtureChild rdfs:subPropertyOf sosa:FixtureParent"],
                             "mapping_row_id": "urn:fixture:parent-row", "target": "bfo:BFO_0000057",
                             "inverse_target_expression": False}]
        records = [dict(source_iri=str(child), source_kind="object_property", review_state="final",
                        assessment_outcome="inheritance_sufficient", mapping_row_ids=[],
                        rationale="The parent route supplies the adopted relation inclusion.", evidence=["decision.json"],
                        notes="Synthetic fixture.",
                        review={"question": "Does the inherited route suffice?", "alternatives": ["yes", "no"],
                                "recommendation": "Review the inherited route.", "confidence": "fixture"}),
                   dict(source_iri=str(parent), source_kind="object_property", review_state="final",
                        assessment_outcome="formal_mapping_adopted", mapping_row_ids=["urn:fixture:parent-row"],
                        rationale="Synthetic parent mapping.", evidence=["mappings/SSN2BFO-COMS.xlsx"],
                        notes="Synthetic fixture.",
                        review={"question": "Should the direct parent mapping be adopted?", "alternatives": ["yes", "no"],
                                "recommendation": "Review the direct route.", "confidence": "fixture"})]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            query = root / "queries/source-classes-and-object-properties.rq"
            input_paths = set(audit.SOURCE_PATHS) | {audit.TARGET_PATH, "mappings/SSN2BFO-COMS.xlsx",
                                                     "queries/source-classes-and-object-properties.rq"}
            for relative in input_paths:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Synthetic fixture bytes for " + relative)
            shutil.copyfile(ROOT / "mappings/SOSA-next-to-BFO-COMS.xlsx",
                            root / "mappings/SOSA-next-to-BFO-COMS.xlsx")
            (root / audit.SOURCE_PATHS[0]).write_text(graph.serialize(format="turtle"))
            (root / audit.TARGET_PATH).write_text("@prefix : <urn:fixture:> .\n")
            query.write_text(audit.SOURCE_QUERY.read_text())
            (root / "config/current-ssn-sosa-scope.json").parent.mkdir(parents=True, exist_ok=True)
            (root / "config/current-ssn-sosa-scope.json").write_text(audit.json_text(scope))
            before = copy.deepcopy(records)
            for record in before:
                record.update(review_state="unreviewed", assessment_outcome="unreviewed")
            before_path = root / "assessment-before.json"
            before_path.write_text(audit.json_text({"records": before}))
            decision = {"source_iri": str(child), "assessment_outcome": "inheritance_sufficient",
                        "no_additional_direct_mapping_required": True,
                        "rationale": "The reviewed fixture requires only the parent inclusion; the inherited inclusion supplies it without another direct assertion.",
                        "input_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(input_paths)},
                        "inherited_routes_sha256": hashlib.sha256(audit.json_text(inherited_routes).encode()).hexdigest()}
            path = root / "decision.json"

            def save_evidence():
                path.write_text(json.dumps(decision))
                records[0]["inheritance_sufficiency_evidence"] = {
                    "path": "decision.json", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

            save_evidence()
            # Independent synthetic source inventory; it contains neither of
            # the actual accepted sample decisions governed by the local pin.
            with patch.object(audit, "ROOT", root), patch.object(audit, "SOURCE_QUERY", query), patch.object(
                    audit.documentary, "validate_immutable_decisions", return_value=None), patch.object(
                    audit.applicability, "validate_current_applicability", return_value=None):
                # This unit fixture uses synthetic graph and non-XLSX input
                # bytes. Real version custody is covered by integration tests.
                routes = {r["source_iri"]: r for r in audit.coverage(terms, graph, [row])}
                target = Graph().parse(root / audit.TARGET_PATH, format="turtle")
                comparisons = audit.next_comparison([row])
                for index, record in enumerate(records):
                    prior = before[index]
                    _, _, packet = audit.review_details(
                        prior, graph, target, [r for r in [row] if str(r.subject) == record["source_iri"]],
                        [row], routes[record["source_iri"]], comparisons, {})
                    packet_name = f"packet-{index}.json"
                    packet_path = root / packet_name
                    packet_path.write_text(audit.json_text(packet))
                    outcome = record["assessment_outcome"]
                    human = {"schema_version": 1, "decision_id": "urn:uuid:" + str(uuid4()),
                             "source_iri": record["source_iri"], "review_state": "final",
                             "assessment_outcome": outcome, "rationale": record["rationale"],
                             "review_question": packet["human_question"],
                             "question_response": "The fixture evidence supports this selected relation or sufficiency conclusion.",
                             "reviewer_identity": "Fixture reviewer; not a real human decision",
                             "review_timestamp": "2026-10-25T12:00:00+00:00",
                             "evidence_refs": record["evidence"],
                             "mapping_row_ids": sorted(record["mapping_row_ids"]),
                             "formal_mapping_assertions": audit.decision_mapping_assertions([r for r in [row] if str(r.subject) == record["source_iri"]]),
                             "input_hashes": audit.decision_input_hashes(),
                             "formal_coverage_sha256": audit.canonical_sha(routes[record["source_iri"]]),
                             "assessment_snapshot": {"path": "assessment-before.json", "sha256": audit.sha(before_path),
                                                     "record_sha256": audit.canonical_sha(prior)},
                             "review_packet_snapshot": {"path": packet_name, "sha256": audit.sha(packet_path),
                                                        "item_sha256": audit.canonical_sha(packet)}}
                    if outcome == "inheritance_sufficient":
                        human.update(decision_basis="inheritance_sufficiency",
                                     no_additional_direct_mapping_required=True,
                                     inheritance_sufficiency_evidence=records[0]["inheritance_sufficiency_evidence"])
                    else:
                        human.update(decision_basis="formal_mapping_approval", formal_mapping_approved=True)
                    human_name = f"human-decision-{index}.json"
                    human_path = root / human_name
                    human_path.write_text(audit.json_text(human))
                    record["human_decision_record"] = {"path": human_name, "sha256": audit.sha(human_path)}
                yield scope, records, graph, [row], decision, save_evidence, path

    def test_valid_synthetic_inheritance_sufficient_requires_route_and_bound_evidence(self):
        with self.synthetic_sufficiency() as (scope, records, graph, rows, _, _, _):
            self.assertEqual(len(audit.validate(scope, records, graph, rows)), 2)

    def test_inherited_route_without_sufficiency_evidence_fails(self):
        with self.synthetic_sufficiency() as (scope, records, graph, rows, _, _, _):
            records[0].pop("inheritance_sufficiency_evidence")
            with self.assertRaisesRegex(ValueError, "lacks bound sufficiency evidence"):
                audit.validate(scope, records, graph, rows)

    def test_wrong_term_stale_and_generic_sufficiency_evidence_fail(self):
        cases = [("source_iri", "urn:another-term", "wrong term"),
                 ("input_sha256", {}, "stale sufficiency evidence inputs"),
                 ("inherited_routes_sha256", "0" * 64, "stale sufficiency evidence inherited routes"),
                 ("rationale", "inherited", "explicit sufficiency rationale"),
                 ("no_additional_direct_mapping_required", False, "explicit sufficiency rationale")]
        for key, value, message in cases:
            with self.subTest(key=key), self.synthetic_sufficiency() as (scope, records, graph, rows, decision, save, _):
                decision[key] = value
                save()  # Even a fresh file hash must not authorize a wrong/stale decision.
                with self.assertRaisesRegex(ValueError, message):
                    audit.validate(scope, records, graph, rows)

    def test_missing_or_modified_sufficiency_artifact_fails(self):
        for missing in (False, True):
            with self.subTest(missing=missing), self.synthetic_sufficiency() as (scope, records, graph, rows, _, _, path):
                if missing:
                    path.unlink()
                else:
                    path.write_text(path.read_text() + "\n")
                with self.assertRaisesRegex(ValueError, "sufficiency evidence"):
                    audit.validate(scope, records, graph, rows)

    def test_domain_range_never_counts_as_direct(self):
        terms = self.validate()
        records = {r["source_iri"]: r for r in audit.coverage(terms, self.graph, self.rows)}
        prop = records[str(audit.mapping.SSN.hasInput)]
        self.assertTrue(prop["typing_only_in_workbook"])
        self.assertFalse(prop["direct_formal_mapping"])
        self.assertFalse(prop["inherited_formal_mapping"])
        self.assertTrue(prop["no_established_formal_route"])

    def test_chain_head_does_not_cover_source_subproperty_or_its_inverse(self):
        terms = self.validate()
        # Retain the historical chain fixture to test the direction rule even
        # after the human decision removes that chain from the live workbook.
        baseline = audit.documentary._baseline(ROOT)
        workbook = audit.documentary._historical_snapshot(ROOT, baseline)
        rows, stats = audit.mapping.read_workbook(workbook)
        historical_rows = audit.mapping.validate_and_process_rows(rows, audit.mapping.Resolver(), stats)
        records = {r["source_iri"]: r for r in audit.coverage(terms, self.graph, historical_rows)}
        for name in ["observes", "isObservedBy"]:
            record = records[str(audit.mapping.SOSA[name])]
            self.assertFalse(record["rule_or_chain_route"])
            self.assertFalse(record["inherited_formal_mapping"])
        self.assertTrue(records[str(audit.mapping.SSN.forProperty)]["rule_or_chain_route"])
        self.assertFalse(records[str(audit.mapping.SSN.forProperty)]["direct_formal_mapping"])

    def test_adjudicated_forproperty_has_no_mapping_route(self):
        iri = str(audit.mapping.SSN.forProperty)
        record = next(r for r in audit.coverage(self.validate(), self.graph, self.rows)
                      if r["source_iri"] == iri)
        self.assertTrue(record["explicit_blank"])
        self.assertTrue(record["no_established_formal_route"])
        self.assertFalse(record["rule_or_chain_route"])
        self.assertFalse(record["direct_formal_mapping"])

    def test_conditional_route_has_separate_typing_only_status(self):
        terms = self.validate()
        records = {r["source_iri"]: r for r in audit.coverage(terms, self.graph, self.rows)}
        prop = records[str(audit.mapping.SSN.hasProperty)]
        self.assertTrue(prop["typing_only_in_workbook"])
        self.assertTrue(prop["rule_or_chain_route"])
        self.assertFalse(prop["direct_formal_mapping"])
        self.assertFalse(records[str(audit.mapping.SSN.isPropertyOf)]["rule_or_chain_route"])

    def test_synthetic_inheritance_equivalence_and_inverse(self):
        graph = Graph()
        child, parent, inverse = map(URIRef, ["urn:child", "urn:parent", "urn:inverse"])
        graph.add((child, RDFS.subPropertyOf, parent))
        graph.add((parent, OWL.inverseOf, inverse))
        row = SimpleNamespace(subject=inverse, predicate="rdfs:subPropertyOf", target="urn:target",
                              row=SimpleNamespace(stable_row_id="urn:row"))
        result = audit.coverage({str(child): "object_property"}, graph, [row])[0]
        self.assertTrue(result["inherited_formal_mapping"])
        self.assertEqual(result["inherited_routes"][0]["target"], "inverse(urn:target)")
        self.assertFalse(result["direct_formal_mapping"])
        graph2 = Graph()
        graph2.add((child, OWL.equivalentClass, parent))
        row2 = SimpleNamespace(subject=parent, predicate="rdfs:subClassOf", target="urn:targetClass",
                               row=SimpleNamespace(stable_row_id="urn:row2"))
        self.assertTrue(audit.coverage({str(child): "class"}, graph2, [row2])[0]["inherited_formal_mapping"])

    def test_approved_blank_pair_has_bound_decisions_and_preserved_row_evidence(self):
        records = {r["source_iri"]: r for r in self.document["records"]}
        for name in ["hasSample", "isSampleOf"]:
            r = records[str(audit.mapping.SOSA[name])]
            self.assertEqual((r["review_state"], r["assessment_outcome"]), ("final", "no_direct_mapping"))
            self.assertEqual(len(r["mapping_row_ids"]), 1)
            self.assertIn("chain", r["review"]["question"].lower())
            own = [row for row in self.rows if str(row.subject) == r["source_iri"]]
            self.assertEqual(audit.decision_mapping_assertions(own), [])
            self.assertTrue(all(not row.predicate and not row.target for row in own))
            decision = json.loads((ROOT / r["human_decision_record"]["path"]).read_text())
            self.assertEqual(decision["reviewer_identity"], "Alec Sculley")
            before, packet = self.predecision_inputs(r["source_iri"])
            prior = next(item for item in before["records"] if item["source_iri"] == r["source_iri"])
            self.assertEqual((prior["review_state"], prior["assessment_outcome"]), ("deferred", "deferred"))
            self.assertEqual(prior["mapping_row_ids"], r["mapping_row_ids"])
            self.assertEqual(packet["human_question"], decision["review_question"])

    def test_legitimate_zero_axiom_no_direct_decision_requires_blank_row_identity(self):
        with self.synthetic_final_decision(str(audit.mapping.SOSA.hasSample), "no_direct_mapping") as (records, blank, _, _, _):
            self.assertEqual(len(blank["mapping_row_ids"]), 1)
            self.validate(records)
            blank["mapping_row_ids"] = []
            with self.assertRaisesRegex(ValueError, "mapping RowID mismatch"):
                self.validate(records)

    def test_hosts_packet_contains_source_deployment_chain_and_distinct_mapping_chain(self):
        _, _, queue, glossary = audit.build_reports(self.scope, self.document)
        hosts = next(r for r in queue["items"] if r["source_iri"] == str(audit.mapping.SOSA.hosts))
        source_chain = next(c for c in hosts["source_semantics"]["property_chains"]
                            if c["superproperty"] == str(audit.mapping.SOSA.hosts))
        self.assertEqual(source_chain["provenance"], "source_native")
        self.assertEqual(source_chain["member_sequence"], ["ssn:inDeployment", "ssn:deployedSystem"])
        self.assertEqual(source_chain["direction"], "member_path_entails_superproperty")
        self.assertTrue(hosts["mapping_property_chains"])
        self.assertTrue(all(c["provenance"] == "mapping" for c in hosts["mapping_property_chains"]))
        self.assertEqual({c["superproperty"] for c in hosts["mapping_property_chains"]},
                         {str(audit.mapping.SOSA.hosts), str(audit.mapping.SOSA.isHostedBy)})
        rendered = audit.render_reviews(queue, glossary)
        self.assertIn("ssn:inDeployment o ssn:deployedSystem -> sosa:hosts", rendered)

    def test_tampered_stored_packet_missing_native_chain_fails_freshness(self):
        _, _, queue, _ = audit.build_reports(self.scope, self.document)
        expected = {"current-ssn-sosa-human-review.json": audit.json_text(queue)}
        tampered = copy.deepcopy(queue)
        hosts = next(r for r in tampered["items"] if r["source_iri"] == str(audit.mapping.SOSA.hosts))
        hosts["source_semantics"].pop("property_chains")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            packet = directory / "current-ssn-sosa-human-review.json"
            packet.write_text(audit.json_text(tampered))
            with self.assertRaisesRegex(ValueError, "stale assessment reports"):
                audit.check_report_outputs(expected, directory)
            packet.write_text(expected[packet.name])
            audit.check_report_outputs(expected, directory)

    def test_native_target_chains_include_members_and_superproperty_dependencies(self):
        graph = Graph()
        head, first, second, child = map(URIRef, ["urn:head", "urn:first", "urn:second", "urn:child"])
        chain = Collection(graph, None, [first, second])
        graph.add((head, OWL.propertyChainAxiom, chain.uri))
        graph.add((child, RDFS.subPropertyOf, first))
        for term in (head, first, second, child):
            with self.subTest(term=term):
                extracted = audit.facts(graph, str(term), "target_native")["property_chains"]
                self.assertEqual(len(extracted), 1)
                self.assertEqual(extracted[0]["member_sequence"], ["<urn:first>", "<urn:second>"])
                self.assertEqual(extracted[0]["superproperty"], "urn:head")
                self.assertEqual(extracted[0]["provenance"], "target_native")

    def test_incoming_restrictions_include_quantifiers_values_cardinalities_and_class_fillers(self):
        graph = Graph().parse(data='''
            @prefix : <urn:fixture:> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            :Some rdfs:subClassOf [ owl:onProperty :p; owl:someValuesFrom :Filler ] .
            :All rdfs:subClassOf [ owl:onProperty :p; owl:allValuesFrom :Filler ] .
            :Value rdfs:subClassOf [ owl:onProperty :p; owl:hasValue :individual ] .
            :Minimum rdfs:subClassOf [ owl:onProperty :p; owl:minCardinality 1 ] .
            :Maximum rdfs:subClassOf [ owl:onProperty :p; owl:maxCardinality 2 ] .
            :Exact rdfs:subClassOf [ owl:onProperty :p; owl:cardinality 1 ] .
            :Qualified rdfs:subClassOf [ owl:onProperty :p; owl:minQualifiedCardinality 1; owl:onClass :Filler ] .
            :Nested owl:equivalentClass [ owl:intersectionOf (:Other [ owl:onProperty :p; owl:allValuesFrom :Filler ]) ] .
            :Inverse rdfs:subClassOf [ owl:onProperty [ owl:inverseOf :p ]; owl:allValuesFrom :Filler ] .
            :Unrelated rdfs:subClassOf [ owl:onProperty :q; owl:allValuesFrom :Elsewhere ] .
        ''', format="turtle")
        facts = audit.facts(graph, "urn:fixture:p", "source_native")
        context = facts["contextual_axioms"]
        self.assertEqual({c["subject"] for c in context}, {"urn:fixture:" + name for name in
                         ("Some", "All", "Value", "Minimum", "Maximum", "Exact", "Qualified", "Nested", "Inverse")})
        self.assertTrue(all(c["assertion_status"] == "asserted" and c["provenance"] == "source_native" for c in context))
        self.assertTrue(all(c["relation_to_reviewed_term"] == "expression_reference" for c in context))
        qualified = next(c for c in context if c["subject"] == "urn:fixture:Qualified")
        self.assertIn("owl:minQualifiedCardinality", qualified["axiom"])
        self.assertIn("owl:onClass <urn:fixture:Filler>", qualified["axiom"])
        filler_context = audit.facts(graph, "urn:fixture:Filler", "source_native")["contextual_axioms"]
        self.assertEqual({c["subject"] for c in filler_context}, {"urn:fixture:" + name for name in
                         ("Some", "All", "Qualified", "Nested", "Inverse")})

    def test_incoming_relations_preserve_direction_and_symmetric_typing(self):
        graph = Graph().parse(data='''
            @prefix : <urn:fixture:> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            :other owl:inverseOf :p .
            :equivalent owl:equivalentProperty :p .
            :child rdfs:subPropertyOf :p .
            :p a owl:SymmetricProperty; rdfs:subPropertyOf :parent .
            :Subclass rdfs:subClassOf :Class .
            :EquivalentClass owl:equivalentClass :Class .
        ''', format="turtle")
        facts = audit.facts(graph, "urn:fixture:p", "source_native")
        self.assertIn("rdf:type owl:SymmetricProperty", facts["logical_axioms"])
        self.assertEqual({c["axiom"] for c in facts["contextual_axioms"]}, {
            "<urn:fixture:other> owl:inverseOf <urn:fixture:p>",
            "<urn:fixture:equivalent> owl:equivalentProperty <urn:fixture:p>",
            "<urn:fixture:child> rdfs:subPropertyOf <urn:fixture:p>"})
        self.assertNotIn("rdfs:subPropertyOf <urn:fixture:child>", facts["logical_axioms"])
        classes = audit.facts(graph, "urn:fixture:Class", "source_native")["contextual_axioms"]
        self.assertEqual({c["subject"] for c in classes}, {"urn:fixture:Subclass", "urn:fixture:EquivalentClass"})

    def test_grouped_and_incoming_target_disjointness_preserve_provenance(self):
        graph = Graph().parse(data='''
            @prefix : <urn:fixture:> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            [] a owl:AllDisjointClasses; owl:members (:Target :Other :Third) .
            :Incoming owl:disjointWith :Target .
            [] a owl:AllDisjointClasses; owl:members (:Unrelated :Elsewhere) .
        ''', format="turtle")
        facts = audit.facts(graph, "urn:fixture:Target", "target_native")
        self.assertEqual(len(facts["grouped_disjointness"]), 1)
        group = facts["grouped_disjointness"][0]
        self.assertEqual(group["members"], ["<urn:fixture:Target>", "<urn:fixture:Other>", "<urn:fixture:Third>"])
        self.assertEqual((group["provenance"], group["assertion_status"]), ("target_native", "asserted"))
        incoming = facts["contextual_axioms"][0]
        self.assertEqual(incoming["axiom"], "<urn:fixture:Incoming> owl:disjointWith <urn:fixture:Target>")
        self.assertEqual(incoming["provenance"], "target_native")

    def test_incondition_packet_exposes_three_universal_restrictions_and_separate_range_consequence(self):
        _, _, queue, glossary = audit.build_reports(self.scope, self.document)
        item = next(r for r in queue["items"] if r["source_iri"] == "http://www.w3.org/ns/ssn/systems/inCondition")
        facts = item["source_semantics"]
        expected = {f"ssn-system:{name} rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)"
                    for name in ("OperatingRange", "SurvivalRange", "SystemCapability")}
        self.assertTrue(expected <= {f["axiom"] for f in facts["contextual_axioms"]})
        self.assertFalse(any(f.startswith("rdfs:range ") for f in facts["logical_axioms"]))
        self.assertFalse(any(r["predicate"] == "rdfs:range" for r in item["current_mapping_state"]))
        self.assertEqual(facts["derived_consequences"], [])  # No source-only domain-cover premise.
        consequence = next(f for f in item["derived_consequences"] if f["range_expression"] == "ssn-system:Condition")
        self.assertFalse(consequence["explicit_range_asserted"])
        self.assertEqual(consequence["assertion_status"], "derived")
        self.assertEqual(consequence["provenance"], "generated_inference")
        self.assertEqual(consequence["premise_provenance"], ["mapping", "source_native"])
        self.assertEqual(len(consequence["premises"]), 4)
        self.assertTrue(expected <= {p["axiom"] for p in consequence["premises"]})
        domain_premise = next(p for p in consequence["premises"] if p["provenance"] == "mapping")
        self.assertEqual(domain_premise["mapping_row_id"], "urn:uuid:79e12baa-9467-4494-bdf3-b6906f5a81a7")
        self.assertIn("no explicit rdfs:range", item["review_clarifications"][0])
        self.assertIn("already entail a range constraint", item["review_clarifications"][0])
        self.assertIn("aligned consequence", item["review_clarifications"][0])
        rendered = audit.render_reviews(queue, glossary)
        self.assertTrue(all(axiom in rendered for axiom in expected))
        self.assertIn("generated_inference", rendered)
        original = next(r for r in self.document["records"] if r["source_iri"] == item["source_iri"])
        self.assertEqual(item["human_question"], original["review"]["question"])
        self.assertEqual(item["review_state"], original["review_state"])

    def test_range_consequence_requires_every_domain_branch_and_universal_constraint(self):
        template = '''
            @prefix : <urn:fixture:> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            :p rdfs:domain [ owl:unionOf (:A :B) ] .
            :A rdfs:subClassOf [ owl:onProperty :p; owl:allValuesFrom :Filler ] .
            REPLACEMENT
        '''
        for restriction in ("", ":B rdfs:subClassOf [ owl:onProperty :p; owl:someValuesFrom :Filler ] .",
                            ":B rdfs:subClassOf [ owl:onProperty :p; owl:minCardinality 1 ] .",
                            ":B rdfs:subClassOf [ owl:onProperty :p; owl:allValuesFrom :Different ] ."):
            graph = Graph().parse(data=template.replace("REPLACEMENT", restriction), format="turtle")
            with self.subTest(restriction=restriction):
                self.assertEqual(audit.facts(graph, "urn:fixture:p", "source_native")["derived_consequences"], [])
        graph = Graph().parse(data=template.replace("REPLACEMENT", ":B rdfs:subClassOf [ owl:onProperty :p; owl:allValuesFrom :Filler ] ."), format="turtle")
        self.assertEqual(len(audit.facts(graph, "urn:fixture:p", "source_native")["derived_consequences"]), 1)

    def test_actual_procedure_disjointness_and_bfo_groups_are_in_target_facts(self):
        _, _, queue, glossary = audit.build_reports(self.scope, self.document)
        procedure = next(r for r in queue["items"] if r["source_iri"] == str(audit.mapping.SOSA.Procedure))
        target = next(t for t in procedure["target_semantics"] if t["iri"] == str(audit.mapping.CCO.ont00000965))
        incoming = [f for f in target["contextual_axioms"] if f["predicate"] == str(OWL.disjointWith)]
        self.assertEqual(len(incoming), 2)
        self.assertTrue(all(f["provenance"] == "target_native" for f in incoming))
        for identifier in ("BFO_0000020", "BFO_0000008", "BFO_0000015"):
            with self.subTest(identifier=identifier):
                self.assertTrue(glossary[str(audit.mapping.BFO[identifier])]["grouped_disjointness"])

    def test_missing_contextual_facts_are_rejected_as_stale_packets(self):
        _, _, queue, _ = audit.build_reports(self.scope, self.document)
        expected = {"current-ssn-sosa-human-review.json": audit.json_text(queue)}
        for field in ("contextual_axioms", "derived_consequences"):
            tampered = copy.deepcopy(queue)
            item = next(r for r in tampered["items"] if r["source_iri"].endswith("/inCondition"))
            (item if field == "derived_consequences" else item["source_semantics"])[field] = []
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                (directory / "current-ssn-sosa-human-review.json").write_text(audit.json_text(tampered))
                with self.assertRaisesRegex(ValueError, "stale assessment reports"):
                    audit.check_report_outputs(expected, directory)

    def test_feature_of_interest_stale_prose_cannot_be_safe(self):
        _, rationales, _, _ = audit.build_reports(self.scope, self.document)
        proposal = next(p for p in rationales["proposals"]
                        if p["source_iri"] == str(audit.mapping.SOSA.FeatureOfInterest))
        self.assertEqual(proposal["status"], "human_review_required")
        self.assertTrue(proposal["semantic_decision_still_required"])
        self.assertTrue(proposal["documentary_consistency_issues"])
        own = [r for r in self.rows if str(r.subject) == proposal["source_iri"]]
        self.assertEqual(own[0].predicate, "rdfs:subClassOf")
        for text in ("Direct alignment deferred", "No direct mapping", "no_direct_mapping"):
            tampered = dict(proposal, status="safe_to_adopt", proposed_documentary_rationale=text)
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "safe rationale conflicts"):
                audit.validate_safe_rationale(tampered, own)

    def test_no_direct_documentary_prose_remains_valid_for_a_blank_row(self):
        own = [r for r in self.rows if r.subject == audit.mapping.SOSA.hasSample]
        proposal = {"source_iri": str(audit.mapping.SOSA.hasSample), "status": "safe_to_adopt",
                    "proposed_documentary_rationale": "Direct alignment deferred; this explicit row contributes zero axioms."}
        audit.validate_safe_rationale(proposal, own)

    def test_queue_complete_and_rationales_separate_documentation_from_approval(self):
        cov, rationale, queue, glossary = audit.build_reports(self.scope, self.document)
        unresolved = {r["source_iri"] for r in self.document["records"] if r["review_state"] != "final"}
        self.assertEqual({r["source_iri"] for r in queue["items"]}, unresolved)
        self.assertEqual(len(queue["items"]), len(unresolved))
        self.assertEqual(len(unresolved), 66)
        self.assertEqual(queue["items"][0]["priority"], 1)
        for item in queue["items"]:
            self.assertTrue(item["source_semantics"]["definitions"])
            self.assertTrue(item["formal_consequences"])
            self.assertTrue(item["human_question"])
            self.assertGreaterEqual(len(item["available_alternatives"]), 2)
            for ref in item["evidence"]:
                self.assertTrue((ROOT / ref.split("#")[0]).is_file(), ref)
        for p in rationale["proposals"]:
            if p["source_iri"] in {str(audit.mapping.SOSA[name]) for name in ("hasSample", "isSampleOf")}:
                self.assertEqual(p["status"], "safe_to_adopt")
                self.assertFalse(p["semantic_decision_still_required"])
                record = next(r for r in self.document["records"] if r["source_iri"] == p["source_iri"])
                self.assertEqual(p["proposed_documentary_rationale"], record["rationale"])
                self.assertTrue(p["existing_workbook_rationales"])
        self.assertEqual(cov["summary"]["coverage_counts"]["direct_formal_mapping"], 66)
        self.assertEqual(cov["summary"]["coverage_counts"]["typing_only_in_workbook"], 17)
        self.assertEqual(cov["summary"]["coverage_counts"]["rule_or_chain_route"], 11)
        self.assertEqual(cov["summary"]["coverage_counts"]["no_established_formal_route"], 15)
        self.assertEqual(cov["summary"]["review_states"], {"final": 25, "deferred": 0, "unreviewed": 66})
        self.assertEqual(cov["summary"]["assessment_outcomes"], {"formal_mapping_adopted": 18,
                         "no_direct_mapping": 5, "inheritance_sufficient": 2, "deferred": 0, "unreviewed": 66})
        self.assertEqual(cov["summary"]["coverage_counts"]["inherited_formal_mapping"], 41)
        self.assertEqual(cov["summary"]["coverage_counts"]["explicit_blank"], 6)
        self.assertEqual(cov["summary"]["assertion_bearing_rows"], 102)


if __name__ == "__main__":
    unittest.main()
