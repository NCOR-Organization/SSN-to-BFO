#!/usr/bin/env python3
"""Project-local current SSN/SOSA assessment and structural coverage audit.

This reads existing mapping mechanisms. It does not generate or change mappings,
COMS, source ontologies, or the independent SOSA-2023 track.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime
from uuid import UUID

from rdflib import BNode, Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.collection import Collection

import generate_mapping_from_coms as mapping
import current_documentary_workbook as documentary
import current_decision_applicability as applicability
import current_custody_dependencies as custody

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "config/current-ssn-sosa-scope.json"
ASSESSMENT = ROOT / "mappings/current-ssn-sosa-assessment.json"
HISTORICAL_FINAL_BASELINE = ROOT / "config/current-ssn-sosa-historical-finals.json"
REPORT_DIRECTORY = Path(custody.ASSESSMENT_OUTPUT_DIRECTORY)
REPORT_NAMES = tuple(f"current-ssn-sosa-{name}.{suffix}" for name in
                     ("coverage", "rationale-proposals", "human-review") for suffix in ("json", "md"))
REPORT_BINDING_PROFILE = "current-ssn-sosa-assessment-content-v1"
# Pin the complete, deliberately closed set of twelve reconstructed historical
# finals. An edit to the JSON cannot silently grandfather another decision.
HISTORICAL_FINAL_BASELINE_SHA256 = "6198ca1aa91b594f55d15a1e82673c06e3f4a21730fe393da04516ae87482769"
SOURCE_QUERY = ROOT / "queries/source-classes-and-object-properties.rq"
STATES = {"final", "deferred", "unreviewed"}
OUTCOMES = {"formal_mapping_adopted", "inheritance_sufficient", "no_direct_mapping", "deferred", "unreviewed"}
FINAL_OUTCOMES = OUTCOMES - {"deferred", "unreviewed"}
DIRECT = {"rdfs:subClassOf", "owl:equivalentClass", "rdfs:subPropertyOf", "owl:equivalentProperty"}
SOURCE_PATHS = tuple(str(p) for p in mapping.SOURCE_IMPORTS)
TARGET_PATH = "imports/cco.ttl"
# Existing historical candidates needed to understand typing/blank decisions.
# These are facts about candidate targets, never adopted mappings.
REVIEW_TARGETS = {
    "sosa:hasSample": ["cco:ont00001873", "bfo:BFO_0000084"],
    "sosa:isSampleOf": ["bfo:BFO_0000101", "cco:ont00001938"],
    "sosa:observes": ["bfo:BFO_0000057"],
    "sosa:isObservedBy": ["bfo:BFO_0000056"],
    "sosa:madeActuation": ["cco:ont00001787"],
    "sosa:madeByActuator": ["cco:ont00001833"],
    "sosa:madeObservation": ["cco:ont00001787"],
    "sosa:madeBySensor": ["cco:ont00001833"],
    "ssn:hasProperty": ["bfo:BFO_0000196", "bfo:BFO_0000117"],
    "ssn:isPropertyOf": ["bfo:BFO_0000197", "bfo:BFO_0000132"],
    "ssn-system:hasOperatingRange": ["bfo:BFO_0000196", "bfo:BFO_0000117"],
    "ssn-system:hasSurvivalRange": ["bfo:BFO_0000196", "bfo:BFO_0000117"],
    "ssn-system:hasSystemCapability": ["bfo:BFO_0000196", "bfo:BFO_0000117"],
}
RULE_PATH = "rules/ssn-hasproperty-conditional-mapping.rq"
RULE_SHA256 = "b98376fc73f6c246e5f2567226ca1ba81536e4fbc2670905acfb2a43c991ff6d"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_text(value) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def signature(terms: dict[str, str]) -> str:
    return hashlib.sha256(json_text(terms).encode()).hexdigest()


def canonical_sha(value) -> str:
    return hashlib.sha256(json_text(value).encode()).hexdigest()


def historical_finals() -> dict[str, dict]:
    """The fixed documentary exceptions are exact records, not an open policy."""
    if sha(HISTORICAL_FINAL_BASELINE) != HISTORICAL_FINAL_BASELINE_SHA256:
        raise ValueError("historical-final baseline hash drift")
    baseline = json.loads(HISTORICAL_FINAL_BASELINE.read_text())
    entries = baseline.get("entries")
    if baseline.get("schema_version") != 1 or not isinstance(entries, list) or len(entries) != 12:
        raise ValueError("historical-final baseline must contain exactly twelve entries")
    by_iri = {e["source_iri"]: e for e in entries}
    if len(by_iri) != 12 or any(e.get("accepted_outcome") not in FINAL_OUTCOMES
                                or not e.get("historical_basis") or not e.get("historical_evidence_ref")
                                or not e.get("assessment_record_sha256") for e in entries):
        raise ValueError("invalid historical-final baseline")
    return by_iri


def project_evidence(ref: dict, label: str, iri: str) -> Path:
    if not isinstance(ref, dict) or not isinstance(ref.get("path"), str) or not ref.get("sha256"):
        raise ValueError(f"missing bound {label}: {iri}")
    try:
        # Decision artifacts are immutable physical records, unlike historical
        # supporting reports. Sharing authentication must not hide their drift.
        return documentary._bound_file(ROOT, ref)
    except (ValueError, OSError) as exc:
        raise ValueError(f"stale or missing bound {label}: {iri}: {exc}") from exc


def decision_mapping_assertions(rows) -> list[dict[str, str]]:
    return sorted(({"row_id": row.row.stable_row_id, "predicate": row.predicate,
                    "target": row.target} for row in rows if row.predicate in mapping.MAPPING_PREDICATES),
                  key=lambda r: (r["row_id"], r["predicate"], r["target"]))


def decision_typing_assertions(rows) -> list[dict[str, str]]:
    """Keep approved OWL typing separate from target-relation mappings."""
    return sorted(({"row_id": row.row.stable_row_id, "predicate": row.predicate,
                    "target": row.target} for row in rows if row.predicate in mapping.DOMAIN_RANGE_PREDICATES),
                  key=lambda r: (r["row_id"], r["predicate"], r["target"]))


def validate_formal_typing_approval(decision: dict, formal: list, typing: list,
                                    iri: str) -> None:
    """Validate the explicit typing-only approval after binding its evidence.

    This does not change direct-mapping coverage or reinterpret older decisions.
    Both callers still authenticate the complete decision and workbook inputs.
    """
    if (decision.get("decision_basis") != "formal_typing_approval"
            or decision.get("formal_typing_approved") is not True
            or decision.get("review_state") != "final"
            or decision.get("assessment_outcome") != "formal_mapping_adopted"
            or formal or decision.get("formal_mapping_assertions") != []
            or not typing or decision.get("formal_typing_assertions") != typing):
        raise ValueError(f"human decision does not approve exact typing-only assertions: {iri}")


def decision_input_hashes() -> dict:
    source = {p: sha(ROOT / p) for p in SOURCE_PATHS}
    return {"source_identity_sha256": canonical_sha(source), "source_files_sha256": source,
            "target_sha256": sha(ROOT / TARGET_PATH),
            "workbook_sha256": sha(ROOT / "mappings/SSN2BFO-COMS.xlsx"),
            "scope_sha256": sha(ROOT / "config/current-ssn-sosa-scope.json"),
            "source_query_sha256": sha(SOURCE_QUERY)}


def authenticate_human_decision(record: dict, graph: Graph, target: Graph, all_rows: list,
                                own_rows: list, route: dict, comparisons: dict,
                                seen_ids: set[str]) -> dict:
    """Authenticate the exact historical evidence, independently of applicability."""
    iri = record["source_iri"]
    decision_path = project_evidence(record.get("human_decision_record"), "human decision record", iri)
    decision = json.loads(decision_path.read_text())
    if not isinstance(decision, dict) or decision.get("schema_version") != 1:
        raise ValueError(f"invalid human decision schema: {iri}")
    decision_id = decision.get("decision_id")
    try:
        UUID(str(decision_id).removeprefix("urn:uuid:"))
    except (ValueError, AttributeError, TypeError):
        raise ValueError(f"invalid human decision ID: {iri}") from None
    if decision_id in seen_ids:
        raise ValueError(f"reused human decision ID: {iri}")
    seen_ids.add(decision_id)
    if (decision.get("source_iri") != iri or decision.get("review_state") != "final"
            or decision.get("assessment_outcome") != record["assessment_outcome"]
            or decision.get("rationale") != record["rationale"]):
        raise ValueError(f"human decision/assessment mismatch: {iri}")
    if not isinstance(decision.get("reviewer_identity"), str) or not decision["reviewer_identity"].strip():
        raise ValueError(f"missing human reviewer identity: {iri}")
    try:
        reviewed_at = datetime.fromisoformat(decision["review_timestamp"])
        if reviewed_at.tzinfo is None:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"invalid human review timestamp: {iri}") from None
    question = decision.get("review_question")
    response = decision.get("question_response")
    if not isinstance(question, str) or not question.strip() or not isinstance(response, str) or not response.strip() or response.strip() == question.strip():
        raise ValueError(f"human decision lacks an explicit packet-question response: {iri}")
    refs = decision.get("evidence_refs")
    if not isinstance(refs, list) or not refs or any(not isinstance(v, str) or not v.strip() for v in refs) or refs != record["evidence"]:
        raise ValueError(f"human decision evidence/assessment mismatch: {iri}")
    historical_inputs = decision.get("input_hashes")
    current_inputs = decision_input_hashes()
    if (not isinstance(historical_inputs, dict)
            or set(historical_inputs) != set(current_inputs)
            or any(historical_inputs[k] != v for k, v in current_inputs.items()
                   if k != "workbook_sha256")):
        raise ValueError(f"stale human decision governed inputs: {iri}")
    historical_workbook = ROOT / "mappings/SSN2BFO-COMS.xlsx"
    reviewed_rows, reviewed_own, reviewed_route = all_rows, own_rows, route
    if historical_inputs["workbook_sha256"] != current_inputs["workbook_sha256"]:
        import current_semantic_workbook as semantic
        # Authenticity of the immutable original evidence does not depend on
        # whether today's workbook transition is valid. Applicability below
        # separately requires the complete chain to the current bytes.
        baseline = documentary._baseline(ROOT)
        if historical_inputs["workbook_sha256"] == baseline["historical_workbook"]["sha256"]:
            historical_workbook = documentary._historical_snapshot(ROOT, baseline)
        else:
            history = semantic.resolve_history(ROOT, require_live=False)
            if historical_inputs["workbook_sha256"] not in history["version_sha256"]:
                raise ValueError(f"human decision workbook lacks historical custody: {iri}")
            historical_workbook = semantic.snapshot(ROOT, historical_inputs["workbook_sha256"])
        raw_rows, stats = mapping.read_workbook(historical_workbook)
        reviewed_rows = mapping.validate_and_process_rows(raw_rows, mapping.Resolver(), stats)
        reviewed_own = [row for row in reviewed_rows if str(row.subject) == iri]
        reviewed_route = coverage({iri: record["source_kind"]}, graph, reviewed_rows)[0]
    if (decision.get("mapping_row_ids") != sorted(row.row.stable_row_id for row in reviewed_own)
            or decision.get("formal_mapping_assertions") != decision_mapping_assertions(reviewed_own)):
        raise ValueError(f"human decision historical mapping state mismatch: {iri}")
    if decision.get("formal_coverage_sha256") != canonical_sha(reviewed_route):
        raise ValueError(f"stale human decision formal coverage: {iri}")
    if any(item.get("artifact") == RULE_PATH for item in reviewed_route.get("rule_routes", [])):
        if sha(ROOT / RULE_PATH) != RULE_SHA256:
            raise ValueError(f"MATERIAL_REQUIRES_REOPEN: governed rule semantics changed: {iri}")

    snapshot_path = project_evidence(decision.get("assessment_snapshot"), "pre-decision assessment snapshot", iri)
    snapshot = json.loads(snapshot_path.read_text())
    prior = [r for r in snapshot.get("records", []) if r.get("source_iri") == iri]
    if len(prior) != 1 or decision["assessment_snapshot"].get("record_sha256") != canonical_sha(prior[0]):
        raise ValueError(f"pre-decision assessment record mismatch: {iri}")
    prior_state = prior[0].get("review_state")
    if prior_state in {"unreviewed", "deferred"}:
        if prior[0].get("assessment_outcome") != prior_state or not prior[0].get("review", {}).get("question"):
            raise ValueError(f"invalid unresolved pre-decision assessment: {iri}")
    else:
        raise ValueError(f"decision requires an unresolved pre-decision assessment: {iri}")
    allowed_change = {"review_state", "assessment_outcome", "rationale", "evidence",
                      "human_decision_record", "inheritance_sufficiency_evidence"}
    if {k: v for k, v in prior[0].items() if k not in allowed_change} != {k: v for k, v in record.items() if k not in allowed_change}:
        raise ValueError(f"human decision changed unreviewed assessment facts: {iri}")
    packet_path = project_evidence(decision.get("review_packet_snapshot"), "review packet snapshot", iri)
    packet = json.loads(packet_path.read_text())
    # Reconstruct what was reviewed, including historical D prose. Do not
    # delete packet fields or pretend later approved prose was reviewed earlier.
    _, _, expected_packet = review_details(prior[0], graph, target, reviewed_own, reviewed_rows,
                                           reviewed_route, next_comparison(reviewed_rows), {})
    if packet != expected_packet or packet.get("human_question") != question:
        raise ValueError(f"human decision review packet mismatch: {iri}")
    if decision["review_packet_snapshot"].get("item_sha256") != canonical_sha(packet):
        raise ValueError(f"review packet item hash mismatch: {iri}")

    outcome = record["assessment_outcome"]
    if outcome == "formal_mapping_adopted":
        if decision.get("decision_basis") == "formal_typing_approval":
            validate_formal_typing_approval(
                decision, decision_mapping_assertions(reviewed_own),
                decision_typing_assertions(reviewed_own), iri)
        elif (decision.get("decision_basis") != "formal_mapping_approval"
                or decision.get("formal_mapping_approved") is not True
                or not decision_mapping_assertions(reviewed_own)):
            raise ValueError(f"human decision does not approve current formal mapping: {iri}")
    elif outcome == "no_direct_mapping":
        if (decision.get("decision_basis") != "semantic_rejection"
                or decision.get("explicit_no_direct_mapping_adopted") is not True
                or not isinstance(decision.get("separate_semantic_conclusion"), str)
                or not decision["separate_semantic_conclusion"].strip()
                or decision_mapping_assertions(reviewed_own)):
            raise ValueError(f"human decision lacks a separate semantic no-direct conclusion: {iri}")
    elif outcome == "inheritance_sufficient":
        # The full workbook hash authenticates the original approval context.
        # Current freshness is established by the complete governed evolution
        # and decision applicability below, including documentary-only edges.
        validate_inheritance_sufficiency(record, reviewed_route, root=ROOT,
                                        workbook_path=historical_workbook)
        if (decision.get("decision_basis") != "inheritance_sufficiency"
                or decision.get("no_additional_direct_mapping_required") is not True
                or decision.get("inheritance_sufficiency_evidence") != record.get("inheritance_sufficiency_evidence")):
            raise ValueError(f"human decision lacks bound inheritance sufficiency: {iri}")
    return {"decision": decision, "prior": prior[0], "workbook": historical_workbook,
            "rows": reviewed_rows, "coverage": reviewed_route, "packet": packet}


def validate_human_decision(record: dict, graph: Graph, target: Graph, all_rows: list,
                            own_rows: list, route: dict, comparisons: dict,
                            seen_ids: set[str]) -> None:
    """Authenticate history, then establish applicability through every version."""
    authenticated = authenticate_human_decision(record, graph, target, all_rows,
                                                own_rows, route, comparisons, seen_ids)
    iri = record["source_iri"]

    def state(workbook):
        raw, stats = mapping.read_workbook(workbook)
        rows = mapping.validate_and_process_rows(raw, mapping.Resolver(), stats)
        own = [row for row in rows if str(row.subject) == iri]
        current_route = coverage({iri: record["source_kind"]}, graph, rows)[0]
        _, _, packet = review_details(authenticated["prior"], graph, target, own, rows,
                                      current_route, next_comparison(rows), {})
        return {"source_exists": any(graph.triples((URIRef(iri), RDF.type, None))),
                "packet": packet, "coverage": current_route}

    applicability.validate_current_applicability(
        ROOT, authenticated["decision"], authenticated["workbook"],
        ROOT / "mappings/SSN2BFO-COMS.xlsx", state)


def evolve_unreviewed_row_ids(root: Path, document: dict,
                              current_path: Path | None = None, *,
                              from_workbook_sha256: str | None = None) -> dict:
    """Return a mechanical RowID-only proposal; never write an assessment.

    Every membership change must be explained by the authenticated version
    chain. Finalized and deferred records are deliberately ineligible; their
    evidence/applicability must be handled through the decision workflow.
    """
    import copy
    import current_semantic_workbook as semantic
    root = Path(root)
    history = semantic.resolve_history(root, current_path=current_path)
    result = copy.deepcopy(document)
    start = from_workbook_sha256 or history["baseline"]["historical_workbook"]["sha256"]
    if start not in history["version_sha256"]:
        raise ValueError("assessment RowID evolution start is outside governed history")

    def memberships(path):
        raw, stats = mapping.read_workbook(path)
        rows = mapping.validate_and_process_rows(raw, mapping.Resolver(), stats)
        by_iri = defaultdict(set)
        for row in rows:
            by_iri[str(row.subject)].add(row.row.stable_row_id)
        return by_iri

    initial = memberships(semantic.snapshot(root, start))
    for record in result["records"]:
        values = record["mapping_row_ids"]
        if len(values) != len(set(values)) or set(values) != initial[record["source_iri"]]:
            raise ValueError(f"assessment RowID evolution requires exact starting membership: {record['source_iri']}")
    for transition in history["chain"][history["version_sha256"].index(start):]:
        before = memberships(semantic.snapshot(root, transition["old_workbook_sha256"]))
        after = memberships(semantic.snapshot(root, transition["new_workbook_sha256"]))
        for record in result["records"]:
            iri = record["source_iri"]
            if before[iri] == after[iri]:
                continue
            if record["review_state"] != "unreviewed" or record["assessment_outcome"] != "unreviewed" or record.get("human_decision_record"):
                raise ValueError(f"MATERIAL_REQUIRES_REOPEN: finalized/deferred RowID evolution is forbidden: {iri}")
            membership = record["mapping_row_ids"]
            if len(membership) != len(set(membership)):
                raise ValueError(f"duplicate assessment RowID: {iri}")
            if set(membership) != before[iri]:
                raise ValueError(f"assessment RowID evolution requires the exact prior membership: {iri}")
            record["mapping_row_ids"] = sorted(after[iri])
    final = memberships(semantic.snapshot(root, history["tail_sha256"]))
    for record in result["records"]:
        if set(record["mapping_row_ids"]) != final[record["source_iri"]]:
            raise ValueError(f"assessment RowID evolution did not reach current membership: {record['source_iri']}")
    return result


def source_graph() -> Graph:
    return mapping.build_source_graph()


def inventory(graph: Graph, scope: dict) -> dict[str, str]:
    """Derive every named term in the declared namespaces; reject ambiguous kinds."""
    terms: dict[str, str] = {}
    types = {"class": OWL.Class, "object_property": OWL.ObjectProperty,
             "datatype_property": OWL.DatatypeProperty}
    for kind in scope["term_kinds"]:
        for term in graph.subjects(RDF.type, types[kind]):
            if not isinstance(term, URIRef) or not any(str(term).startswith(p) for p in scope["namespaces"]):
                continue
            if scope["deprecated_policy"] == "exclude_owl_deprecated_true" and any(
                isinstance(v, Literal) and v.toPython() is True for v in graph.objects(term, OWL.deprecated)
            ):
                continue
            if str(term) in terms and terms[str(term)] != kind:
                raise ValueError(f"type inconsistency for {term}")
            terms[str(term)] = kind
    return dict(sorted(terms.items()))


def processed_rows():
    # Existing project reader/parser; no generic COMS changes or write operations.
    rows, stats = mapping.read_workbook(mapping.PRIMARY_WORKBOOK)
    return mapping.validate_and_process_rows(rows, mapping.Resolver(), stats)


def validate(scope: dict, records: list[dict], graph: Graph, rows) -> dict[str, str]:
    # Check accepted records before branching on finality: a state downgrade
    # must not evade the decision guard or rewrite the historical evidence.
    documentary.validate_immutable_decisions(ROOT, records)
    if scope["source_files"] != list(SOURCE_PATHS):
        raise ValueError("source-scope drift: source files differ from current generator")
    if scope["query_sha256"] != sha(SOURCE_QUERY):
        raise ValueError("source-scope drift: governed query bytes changed")
    if scope["term_kinds"] != ["class", "object_property"] or scope["deprecated_policy"] != "exclude_owl_deprecated_true":
        raise ValueError("source-scope drift: current query scope must remain explicit")
    terms = inventory(graph, scope)
    queried = {str(r.term): str(r.kind) for r in graph.query(SOURCE_QUERY.read_text())}
    if terms != queried:
        raise ValueError("source-scope drift: dynamic policy differs from existing project query")
    if signature(terms) != scope["source_signature_sha256"]:
        raise ValueError("source-scope drift: governed source signature changed")
    ids = [r["source_iri"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate assessment subject")
    if set(ids) != set(terms):
        raise ValueError(f"assessment inventory mismatch; missing={sorted(set(terms)-set(ids))}; extra={sorted(set(ids)-set(terms))}")
    by_subject = defaultdict(set)
    for row in rows:
        by_subject[str(row.subject)].add(row.row.stable_row_id)
    baseline = historical_finals()
    finals = [r for r in records if r["review_state"] == "final"]
    route_by_iri = {r["source_iri"]: r for r in coverage(terms, graph, rows)} if finals else {}
    seen_decision_ids: set[str] = set()
    target_graph = None
    comparisons = None
    legacy_history = None
    legacy_coverage = {}
    for r in records:
        iri = r["source_iri"]
        if r["source_kind"] != terms[iri]:
            raise ValueError(f"type inconsistency: assessment {iri}")
        if r["review_state"] not in STATES or r["assessment_outcome"] not in OUTCOMES:
            raise ValueError(f"invalid state/outcome: {iri}")
        if r["review_state"] == "final" and r["assessment_outcome"] not in FINAL_OUTCOMES:
            raise ValueError(f"final assessment has unresolved outcome: {iri}")
        if r["review_state"] != "final" and r["assessment_outcome"] != r["review_state"]:
            raise ValueError(f"unresolved state/outcome mismatch: {iri}")
        if set(r["mapping_row_ids"]) != by_subject[iri] or len(r["mapping_row_ids"]) != len(set(r["mapping_row_ids"])):
            raise ValueError(f"mapping RowID mismatch: {iri}")
        if r["assessment_outcome"] == "formal_mapping_adopted" and not any(str(row.subject) == iri and row.predicate in mapping.MAPPING_PREDICATES for row in rows):
            # A domain/range-only artifact is not automatically an adopted
            # outcome. Require its separate explicit, byte-bound approval;
            # complete historical authentication still runs below.
            own_rows = [row for row in rows if str(row.subject) == iri]
            typing = decision_typing_assertions(own_rows)
            if not typing:
                raise ValueError(f"formal outcome lacks a mapping: {iri}")
            decision_path = project_evidence(r.get("human_decision_record"), "human decision record", iri)
            decision = json.loads(decision_path.read_text())
            validate_formal_typing_approval(
                decision, decision_mapping_assertions(own_rows), typing, iri)
        if r["assessment_outcome"] == "no_direct_mapping" and any(str(row.subject) == iri and row.predicate in mapping.MAPPING_PREDICATES for row in rows):
            raise ValueError(f"no-direct outcome conflicts with mapping: {iri}")
        if r["assessment_outcome"] == "inheritance_sufficient":
            route = route_by_iri[iri]
            if not route["inherited_formal_mapping"] or not route["inherited_routes"]:
                raise ValueError(f"inheritance_sufficient lacks an inherited formal route: {iri}")
        if not r["rationale"] or not r["evidence"]:
            raise ValueError(f"missing rationale/evidence: {iri}")
        if r["review_state"] == "final":
            historical = baseline.get(iri)
            unchanged_historical = (historical is not None
                                    and historical["accepted_outcome"] == r["assessment_outcome"]
                                    and historical["assessment_record_sha256"] == canonical_sha(r)
                                    and historical["historical_evidence_ref"] in r["evidence"])
            if not unchanged_historical:
                if target_graph is None:
                    target_graph = Graph().parse(ROOT / TARGET_PATH, format="turtle")
                    comparisons = next_comparison(rows)
                validate_human_decision(r, graph, target_graph, rows,
                                        [row for row in rows if str(row.subject) == iri],
                                        route_by_iri[iri], comparisons, seen_decision_ids)
            else:
                # The twelve closed historical exceptions have no reconstructed
                # human packet to rewrite. Their grandfathered approval is not
                # permission to evolve their own mappings or formal coverage.
                import current_semantic_workbook as semantic
                if legacy_history is None:
                    legacy_history = semantic.resolve_history(ROOT)
                for transition in legacy_history["chain"]:
                    if transition["kind"] != "semantic":
                        continue
                    paths = [semantic.snapshot(ROOT, transition[key + "_workbook_sha256"])
                             for key in ("old", "new")]
                    if applicability.own_semantic_rows(paths[0], iri) != applicability.own_semantic_rows(paths[1], iri):
                        raise ValueError(f"MATERIAL_REQUIRES_REOPEN: historical-final semantic rows changed: {iri}")
                    for path in paths:
                        if path not in legacy_coverage:
                            raw, stats = mapping.read_workbook(path)
                            historical_rows = mapping.validate_and_process_rows(raw, mapping.Resolver(), stats)
                            legacy_coverage[path] = {v["source_iri"]: v for v in coverage(terms, graph, historical_rows)}
                    if legacy_coverage[paths[0]][iri] != legacy_coverage[paths[1]][iri]:
                        raise ValueError(f"MATERIAL_REQUIRES_REOPEN: historical-final formal coverage changed: {iri}")
        if r["review_state"] != "final":
            for key in ("question", "alternatives", "recommendation", "confidence"):
                if not r["review"][key]:
                    raise ValueError(f"missing review {key}: {iri}")
    return terms


def sufficiency_inputs(*, root: Path | None = None,
                       workbook_path: Path | None = None) -> dict[str, str]:
    """Actual governed inputs supporting a live or candidate sufficiency decision."""
    root = Path(root) if root is not None else ROOT
    paths = set(SOURCE_PATHS) | {TARGET_PATH, "mappings/SSN2BFO-COMS.xlsx",
                                "queries/source-classes-and-object-properties.rq"}
    workbook_path = Path(workbook_path) if workbook_path is not None else root / "mappings/SSN2BFO-COMS.xlsx"
    return {p: sha(workbook_path if p == "mappings/SSN2BFO-COMS.xlsx" else root / p)
            for p in sorted(paths)}


def validate_inheritance_sufficiency(record: dict, route: dict, *,
                                    root: Path | None = None,
                                    workbook_path: Path | None = None) -> None:
    """Authenticate exact approval-context inputs; evolution determines freshness."""
    root = Path(root) if root is not None else ROOT
    iri = record["source_iri"]
    if route["source_iri"] != iri or not route["inherited_formal_mapping"] or not route["inherited_routes"]:
        raise ValueError(f"inheritance_sufficient lacks an inherited formal route: {iri}")
    ref = record.get("inheritance_sufficiency_evidence")
    if not isinstance(ref, dict) or not all(ref.get(k) for k in ("path", "sha256")):
        raise ValueError(f"inheritance_sufficient lacks bound sufficiency evidence: {iri}")
    try:
        path = documentary._bound_file(root, ref)
    except (ValueError, OSError) as exc:
        raise ValueError(f"stale sufficiency evidence hash: {iri}: {exc}") from exc
    evidence = json.loads(path.read_text())
    if not isinstance(evidence, dict) or evidence.get("source_iri") != iri:
        raise ValueError(f"sufficiency evidence refers to the wrong term: {iri}")
    if (evidence.get("assessment_outcome") != "inheritance_sufficient"
            or evidence.get("no_additional_direct_mapping_required") is not True
            or not isinstance(evidence.get("rationale"), str)
            or evidence["rationale"].strip().lower() in {"", "inherited", "inheritance", "inheritance sufficient"}):
        raise ValueError(f"sufficiency evidence lacks an explicit sufficiency rationale: {iri}")
    if evidence.get("input_sha256") != sufficiency_inputs(root=root, workbook_path=workbook_path):
        raise ValueError(f"stale sufficiency evidence inputs: {iri}")
    route_hash = hashlib.sha256(json_text(route["inherited_routes"]).encode()).hexdigest()
    if evidence.get("inherited_routes_sha256") != route_hash:
        raise ValueError(f"stale sufficiency evidence inherited routes: {iri}")


def compact(iri) -> str:
    return mapping.compact_iri(iri)


def rdf_text(graph: Graph, node, seen=frozenset()) -> str:
    if isinstance(node, URIRef):
        return compact(node)
    if isinstance(node, Literal):
        return node.n3()
    if node in seen:
        return "[recursive expression]"
    seen = seen | {node}
    for p, op in [(OWL.intersectionOf, " and "), (OWL.unionOf, " or ")]:
        head = graph.value(node, p)
        if head is not None:
            return "(" + op.join(rdf_text(graph, n, seen) for n in Collection(graph, head)) + ")"
    prop = graph.value(node, OWL.onProperty)
    if prop is not None:
        restrictions = []
        for p in [OWL.someValuesFrom, OWL.allValuesFrom, OWL.minCardinality, OWL.maxCardinality,
                  OWL.cardinality, OWL.minQualifiedCardinality, OWL.maxQualifiedCardinality,
                  OWL.qualifiedCardinality, OWL.hasValue, OWL.onClass, OWL.onDataRange, OWL.hasSelf]:
            for v in graph.objects(node, p):
                restrictions.append(f"{compact(p)} {rdf_text(graph, v, seen)}")
        return f"({rdf_text(graph, prop, seen)} {'; '.join(restrictions)})"
    inv = graph.value(node, OWL.inverseOf)
    if inv is not None:
        return f"inverse({rdf_text(graph, inv, seen)})"
    return "[" + "; ".join(sorted(f"{compact(p)} {rdf_text(graph, v, seen)}" for p, v in graph.predicate_objects(node))) + "]"


def chain_fact(head, members: list[str], provenance: str) -> dict:
    return {"provenance": provenance, "assertion_status": "asserted",
            "superproperty": str(head), "member_sequence": members,
            "direction": "member_path_entails_superproperty",
            "axiom": " o ".join(members) + " -> " + compact(head)}


def property_chain_facts(graph: Graph, iri: str, provenance: str) -> list[dict]:
    """Keep chains involving the term, its named superproperties, or inverses.

    This is review evidence, not a new structural coverage route. Membership in
    a chain never turns a path-to-head entailment into a head-to-path inclusion.
    """
    related = {URIRef(iri)} | {URIRef(parent) for parent, _, _ in ancestors(graph, iri, "object_property")}
    chains = []
    for head, collection in graph.subject_objects(OWL.propertyChainAxiom):
        members = list(Collection(graph, collection))
        involved = {head, *members}
        # OWL chain members can be inverse-property expressions.
        involved.update(v for member in members for v in graph.objects(member, OWL.inverseOf))
        matches = involved & related
        if matches:
            chains.append({**chain_fact(head, [rdf_text(graph, m) for m in members], provenance),
                           "relevant_properties": sorted(str(p) for p in matches)})
    return sorted(chains, key=json_text)


def mapping_chain_facts(rows, relevant_iris: set[str]) -> list[dict]:
    return sorted(({**chain_fact(row.subject, [compact(p) for p in row.property_chain], "mapping"),
                    "mapping_row_id": row.row.stable_row_id}
                   for row in rows if row.property_chain
                   and ({str(row.subject), *(str(p) for p in row.property_chain)} & relevant_iris)),
                  key=json_text)


LOGICAL_PREDICATES = {RDFS.subClassOf, RDFS.subPropertyOf, RDFS.domain, RDFS.range,
                      OWL.equivalentClass, OWL.equivalentProperty, OWL.inverseOf,
                      OWL.disjointWith, OWL.propertyDisjointWith, RDF.type}
EXPRESSION_PREDICATES = {RDF.first, RDF.rest, OWL.intersectionOf, OWL.unionOf,
                         OWL.complementOf, OWL.oneOf, OWL.onProperty, OWL.inverseOf,
                         OWL.someValuesFrom, OWL.allValuesFrom, OWL.hasValue,
                         OWL.onClass, OWL.onDataRange}


def contextual_axioms(graph: Graph, iri: str, provenance: str) -> list[dict]:
    """Retain asserted axioms that mention the term outside their subject.

    Walk backwards through anonymous expressions only. Stop at the named axiom
    subject: an incoming subclass is evidence about that subclass, not a new
    superclass or a constraint on every instance of the reviewed class. This
    bounds extraction to directly participating axioms rather than a recursive
    neighborhood of named classes/properties.
    """
    node = URIRef(iri)
    todo, seen, result = [node], set(), {}
    while todo:
        current = todo.pop()
        if current in seen:
            continue
        seen.add(current)
        for subject, predicate in graph.subject_predicates(current):
            if isinstance(subject, URIRef) and predicate in LOGICAL_PREDICATES:
                if subject == node:
                    continue  # Already retained as an outgoing axiom.
                item = {"provenance": provenance, "assertion_status": "asserted",
                        "subject": str(subject), "predicate": str(predicate),
                        "object": rdf_text(graph, current),
                        "relation_to_reviewed_term": "incoming" if current == node else "expression_reference",
                        "axiom": f"{compact(subject)} {compact(predicate)} {rdf_text(graph, current)}"}
                result[json_text(item)] = item
            elif isinstance(subject, BNode) and predicate in EXPRESSION_PREDICATES:
                todo.append(subject)
    return [result[key] for key in sorted(result)]


def grouped_disjointness(graph: Graph, iri: str, provenance: str) -> list[dict]:
    """Expose a relevant disjoint group with its complete asserted member list."""
    node, groups = URIRef(iri), []
    for group in graph.subjects(RDF.type, OWL.AllDisjointClasses):
        for head in graph.objects(group, OWL.members):
            members = list(Collection(graph, head))
            if node in members:
                rendered = [rdf_text(graph, member) for member in members]
                groups.append({"provenance": provenance, "assertion_status": "asserted",
                               "type": str(OWL.AllDisjointClasses), "members": rendered,
                               "axiom": "owl:AllDisjointClasses owl:members (" + ", ".join(rendered) + ")"})
    return sorted(groups, key=json_text)


def restriction_range_consequences(graph: Graph, iri: str, provenance: str, domain_rows=None) -> list[dict]:
    """Explain the bounded domain-cover/all-values range pattern, with premises.

    This is not a reasoner run or a mapping proposal. For a declared domain C
    (or union of named C_i), each C_i must explicitly require all P values to
    belong to the same filler. Domains come from the native graph unless
    explicit processed mapping rows are supplied; those premises keep their
    mapping RowIDs. A missing branch, existential or cardinality alone cannot
    establish this pattern. Anonymous subclass intersections are safely
    decomposed; unions and other expressions are not.
    """
    node, result = URIRef(iri), []

    def universal_restrictions(expression):
        head = graph.value(expression, OWL.intersectionOf)
        if head is not None:
            for member in Collection(graph, head):
                yield from universal_restrictions(member)
        elif graph.value(expression, OWL.onProperty) == node:
            for filler in graph.objects(expression, OWL.allValuesFrom):
                yield filler

    domain_cases = []
    if domain_rows is None:
        for domain in graph.objects(node, RDFS.domain):
            union = graph.value(domain, OWL.unionOf)
            branches = list(Collection(graph, union)) if union is not None else [domain]
            domain_cases.append((branches, {"provenance": provenance, "assertion_status": "asserted",
                                 "axiom": f"{compact(node)} rdfs:domain {rdf_text(graph, domain)}"}))
    else:
        for row in domain_rows:
            if row.subject != node or row.predicate != "rdfs:domain" or row.expr is None:
                continue
            expressions = row.expr.children if row.expr.kind == "union" else [row.expr]
            if all(expr.kind == "named" for expr in expressions):
                domain_cases.append(([expr.iri for expr in expressions], {
                    "provenance": "mapping", "assertion_status": "asserted",
                    "mapping_row_id": row.row.stable_row_id,
                    "axiom": f"{compact(node)} rdfs:domain {row.target}"}))
    for branches, domain_premise in domain_cases:
        if not branches or not all(isinstance(branch, URIRef) for branch in branches):
            continue
        premises_by_branch = []
        for branch in branches:
            constraints = defaultdict(list)
            for predicate in (RDFS.subClassOf, OWL.equivalentClass):
                for expression in graph.objects(branch, predicate):
                    for filler in universal_restrictions(expression):
                        constraints[filler].append(f"{compact(branch)} {compact(predicate)} {rdf_text(graph, expression)}")
            premises_by_branch.append(constraints)
        common_fillers = set.intersection(*(set(premises) for premises in premises_by_branch))
        for filler in sorted(common_fillers, key=str):
            result.append({"provenance": "generated_inference",
                           "premise_provenance": sorted({provenance, domain_premise["provenance"]}),
                           "assertion_status": "derived", "method": "domain_cover_and_universal_restrictions",
                           "axiom": f"{compact(node)} rdfs:range {rdf_text(graph, filler)}",
                           "range_expression": rdf_text(graph, filler),
                           "explicit_range_asserted": (node, RDFS.range, filler) in graph,
                           "premises": [domain_premise] +
                                       [{"provenance": provenance, "assertion_status": "asserted", "axiom": p}
                                        for p in sorted({p for constraints in premises_by_branch for p in constraints[filler]})],
                           "explanation": "Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision."})
    return sorted(result, key=json_text)


def facts(graph: Graph, iri: str, provenance: str) -> dict:
    node = URIRef(iri)
    definitions = sorted({str(v) for p, v in graph.predicate_objects(node) if isinstance(v, Literal)
                          and (str(p).endswith("definition") or str(p).endswith("IAO_0000115"))})
    if not definitions:
        definitions = sorted(str(v) for v in graph.objects(node, RDFS.comment))
    logical = []
    for p, v in graph.predicate_objects(node):
        if p in LOGICAL_PREDICATES:
            logical.append(f"{compact(p)} {rdf_text(graph, v)}")
    includes = sorted(f"{compact(p)} {rdf_text(graph,v)}" for p,v in graph.predicate_objects(node)
                      if str(p).endswith(("domainIncludes", "rangeIncludes")))
    return {"iri": iri, "label": str(graph.value(node, RDFS.label) or ""),
            "provenance": provenance, "assertion_status": "asserted_except_derived_consequences",
            "definitions": definitions, "logical_axioms": sorted(logical),
            "nonlogical_domain_range_notes": includes,
            "contextual_axioms": contextual_axioms(graph, iri, provenance),
            "grouped_disjointness": grouped_disjointness(graph, iri, provenance),
            "derived_consequences": restriction_range_consequences(graph, iri, provenance),
            "property_chains": property_chain_facts(graph, iri, provenance)}


def rationale_mapping_conflicts(text: str, rows) -> list[str]:
    """Conservative documentary check; ambiguous prose goes to human review."""
    if not any(row.predicate in mapping.MAPPING_PREDICATES for row in rows):
        return []
    patterns = (r"direct\s+(?:alignment|mapping)\s+(?:is\s+)?deferred",
                r"(?:no|without)\s+(?:a\s+)?direct\s+(?:alignment|mapping)",
                r"no[_-]direct[_-]mapping")
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
        return ["Prose describes direct alignment as deferred/absent despite an active formal mapping row."]
    return []


def validate_safe_rationale(proposal: dict, rows) -> None:
    if proposal["status"] == "safe_to_adopt" and rationale_mapping_conflicts(
            proposal["proposed_documentary_rationale"], rows):
        raise ValueError(f"safe rationale conflicts with active mapping: {proposal['source_iri']}")


def expression_iris(expr):
    if expr is None:
        return set()
    result = {str(i) for i in (expr.iri, expr.prop) if i is not None}
    for child in expr.children:
        result |= expression_iris(child)
    if expr.filler:
        result |= expression_iris(expr.filler)
    return result


def expression_forms(expr) -> Counter:
    result = Counter()
    if expr is None:
        return result
    result[expr.kind] += 1
    for child in expr.children:
        result.update(expression_forms(child))
    if expr.filler:
        result.update(expression_forms(expr.filler))
    return result


def ancestors(graph: Graph, start: str, kind: str):
    """Named superclass/superproperty paths, with equivalences and inverse parity.

No domain/range edge participates. Chains are not traversed backwards: a chain
headed by a superproperty does not cover each subproperty instance.
"""
    hierarchy = RDFS.subClassOf if kind == "class" else RDFS.subPropertyOf
    equivalence = OWL.equivalentClass if kind == "class" else OWL.equivalentProperty
    seen = {(start, False)}
    todo = deque([(start, False, [])])
    while todo:
        current, inverse, path = todo.popleft()
        neighbors = []
        for target in graph.objects(URIRef(current), hierarchy):
            if isinstance(target, URIRef):
                neighbors.append((str(target), inverse, f"{compact(current)} {compact(hierarchy)} {compact(target)}"))
        for target in set(graph.objects(URIRef(current), equivalence)) | set(graph.subjects(equivalence, URIRef(current))):
            if isinstance(target, URIRef):
                neighbors.append((str(target), inverse, f"{compact(current)} {compact(equivalence)} {compact(target)}"))
        if kind == "object_property":
            for target in set(graph.objects(URIRef(current), OWL.inverseOf)) | set(graph.subjects(OWL.inverseOf, URIRef(current))):
                if isinstance(target, URIRef):
                    neighbors.append((str(target), not inverse, f"{compact(current)} owl:inverseOf {compact(target)}"))
        for target, inv, edge in sorted(neighbors):
            if (target, inv) not in seen:
                seen.add((target, inv))
                new_path = path + [edge]
                yield target, inv, new_path
                todo.append((target, inv, new_path))


def coverage(terms: dict, graph: Graph, rows) -> list[dict]:
    by_subject = defaultdict(list)
    for row in rows:
        by_subject[str(row.subject)].append(row)
    result = []
    rule_head = str(mapping.SSN.hasProperty)
    implementation_rule_heads = mapping.implementation_rule_terms(rows)
    for iri, kind in sorted(terms.items()):
        own = by_subject[iri]
        direct = [r.row.stable_row_id for r in own if r.predicate in DIRECT]
        typing = [r.row.stable_row_id for r in own if r.predicate in mapping.DOMAIN_RANGE_PREDICATES]
        chains = [r.row.stable_row_id for r in own if r.predicate == "owl:propertyChainAxiom"]
        inherited = []
        rule_routes = []
        if kind == "object_property" and URIRef(iri) in implementation_rule_heads:
            rule_routes.append({"artifact": mapping.IMPLEMENTATION_RULE_PATH,
                                "artifact_sha256": mapping.IMPLEMENTATION_RULE_SHA256,
                                "mode": "external_construct_rule",
                                "conditions": "Explicit or previously materialized CCO prescribes followed by has_agent yields ssn:implementedBy and inverse ssn:implements assertions. Requires executing the query; not an OWL-product entailment or a direct prescription inclusion."})
        # A conditional query can consume forward explicit subproperty edges only.
        if kind == "object_property" and (iri == rule_head or (URIRef(iri), RDFS.subPropertyOf * "*", URIRef(rule_head)) in graph):
            rule_routes.append({"artifact": RULE_PATH, "mode": "conditional_external_query",
                                "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."})
        for parent, inverse, path in ancestors(graph, iri, kind):
            for r in by_subject[parent]:
                if r.predicate in DIRECT:
                    inherited.append({"via_source": parent, "source_path": path,
                                      "mapping_row_id": r.row.stable_row_id,
                                      "target": ("inverse(" + r.target + ")") if inverse else r.target,
                                      "inverse_target_expression": inverse})
                elif inverse and r.predicate == "owl:propertyChainAxiom" and not any("rdfs:subPropertyOf" in edge for edge in path):
                    # Inverse(chain) <= inverse(head), valid inverse counterpart.
                    rule_routes.append({"mapping_row_id": r.row.stable_row_id,
                                        "mode": "inverse_chain_head", "source_path": path,
                                        "conditions": "Reverse each chain relation and order; this infers source edges from target paths, not target edges from arbitrary source assertions."})
        established = bool(direct or inherited or chains or rule_routes)
        result.append({"source_iri": iri, "source_kind": kind,
                       "direct_formal_mapping": bool(direct), "direct_mapping_row_ids": direct,
                       "inherited_formal_mapping": bool(inherited), "inherited_routes": inherited,
                       "chain_mapping_row_ids": chains, "rule_routes": rule_routes,
                       "rule_or_chain_route": bool(chains or rule_routes),
                       "typing_row_ids": typing,
                       "typing_only_in_workbook": bool(typing) and not direct and not chains,
                       "explicit_blank": any(not r.predicate for r in own),
                       "no_established_formal_route": not established})
    return result


def mapping_row(row) -> dict:
    return {"row_id": row.row.stable_row_id, "location": row.row.row_id,
            "provenance": "mapping", "assertion_status": "asserted" if row.predicate else "explicit_blank",
            "predicate": row.predicate, "target": row.target,
            "existing_rationale": row.row.reasoning_text,
            "expression_forms": dict(expression_forms(row.expr))}


def consequences(row) -> list[str]:
    s = compact(row.subject)
    target = row.target
    if row.predicate == "owl:equivalentClass":
        return [f"Every {s} satisfies {target}; every instance satisfying that full expression is also {s}. Existential fillers denote actual individuals, including anonymous witnesses."]
    if row.predicate == "rdfs:subClassOf":
        return [f"Every {s} satisfies {target}; the reverse classification is not asserted." +
                (" Each 'some' requires at least one actual filler; this is not merely a capability or possible realization." if expression_forms(row.expr)["some"] else "")]
    if row.predicate in {"rdfs:subPropertyOf", "owl:equivalentProperty"}:
        return [f"Every {s}(x,y) entails {target}(x,y), including target domain/range and superproperty consequences." +
                (" The reverse relation inclusion also holds." if row.predicate == "owl:equivalentProperty" else "")]
    if row.predicate == "owl:propertyChainAxiom":
        return [f"A path {target} from x to y entails {s}(x,y). The axiom does not decompose an arbitrary {s} edge into that path and does not itself give {s} a target superproperty."]
    if row.predicate in mapping.DOMAIN_RANGE_PREDICATES:
        return [f"An asserted {s}(x,y) types {'x' if row.predicate == 'rdfs:domain' else 'y'} as {target}; no BFO/CCO relation edge is entailed by this typing axiom alone."]
    return [f"{s} contributes zero mapping axioms; native source axioms remain present."]


def next_comparison(rows):
    other, _ = mapping.read_workbook(ROOT / "mappings/SOSA-next-to-BFO-COMS.xlsx")
    other_by_name = {r.subject_text: r for r in other}
    result = {}
    for r in rows:
        name = r.row.subject_text
        aliases = [name]
        if name.startswith("ssn:"):
            aliases.append("sosa:" + name.split(":", 1)[1])
        n = next((other_by_name[a] for a in aliases if a in other_by_name), None)
        if n:
            item = {"source_term": n.subject_text, "match_kind": "same lexical term" if n.subject_text == name else "local-name comparison only; distinct namespace/source version",
                    "location": n.row_id, "row_id": n.stable_row_id, "status": n.mapping_status_text,
                    "predicate": n.predicate_text, "target": n.target_text, "rationale": n.reasoning_text}
            result[str(r.subject)] = item
    return result


def review_details(record: dict, graph: Graph, target: Graph, own: list, all_rows: list,
                   route: dict, comparisons: dict, glossary: dict) -> tuple[list[str], list[str], dict | None]:
    """One source of truth for the complete generated per-term review packet."""
    iri = record["source_iri"]
    target_iris = set()
    for row in own:
        target_iris |= expression_iris(row.expr)
        target_iris.update(str(x) for x in row.property_chain)
        if row.target_property:
            target_iris.add(str(row.target_property))
    candidate_iris = {str(mapping.URIRef(mapping.PREFIXES[token.split(":", 1)[0]] + token.split(":", 1)[1]))
                      for token in REVIEW_TARGETS.get(own[0].row.subject_text if own else compact(iri), [])}
    target_iris |= candidate_iris
    target_iris = {x for x in target_iris if x.startswith((str(mapping.BFO), str(mapping.CCO)))}
    relevant_chain_iris = {iri} | target_iris | {
        parent for parent, _, _ in ancestors(graph, iri, record["source_kind"])}
    for x in target_iris:
        relevant_chain_iris.update(parent for parent, _, _ in ancestors(target, x, "object_property"))
        glossary[x] = facts(target, x, "target_native")
    existing = [r.row.reasoning_text for r in own if r.row.reasoning_text]
    flags = []
    if any(r.predicate == "owl:equivalentClass" for r in own): flags.append("strong_equivalence")
    if any(expression_forms(r.expr)["some"] for r in own): flags.append("existential_restriction")
    if any(expression_forms(r.expr)["intersection"] or expression_forms(r.expr)["union"] for r in own): flags.append("complex_expression")
    if any(r.property_chain for r in own): flags.append("property_chain")
    if route["typing_only_in_workbook"]: flags.append("typing_only_artifact")
    if route["explicit_blank"]: flags.append("explicit_blank")
    if record.get("cross_track_review"): flags.append("material_cross_track_difference")
    if record["source_kind"] == "object_property" and any(r.predicate in DIRECT for r in own): flags.append("relation_interpretation")
    if record["source_kind"] == "class": flags.append("target_category_commitment")
    if record["review_state"] == "final":
        return flags, existing, None

    priority = (1 if "explicit_blank" in flags else 2 if "typing_only_artifact" in flags else
                3 if "strong_equivalence" in flags else 4 if "complex_expression" in flags else
                5 if "existential_restriction" in flags else 6 if "property_chain" in flags else
                7 if "material_cross_track_difference" in flags else 8)
    source_facts = facts(graph, iri, "source_native")
    combined_consequences = restriction_range_consequences(graph, iri, "source_native", own)
    clarifications = []
    if (source_facts["derived_consequences"] or combined_consequences) and not any(r.predicate == "rdfs:range" for r in own):
        explicit = any(graph.objects(URIRef(iri), RDFS.range))
        clarifications.append(
            f"The current workbook has no explicit rdfs:range row for {compact(iri)}. " +
            ("The source has an explicit range assertion. " if explicit else "The source also has no explicit rdfs:range assertion. ") +
            ("The source universal restrictions together with the current mapping's domain row already entail a range constraint; this is an aligned consequence, not a source-only range assertion. " if combined_consequences else
             "The source domain and universal restrictions already entail a range constraint. ") +
            "An absent explicit row is therefore not evidence of unconstrained objects. Read the retained review question with this distinction; no mapping decision is made.")
    packet = {"source_iri": iri, "priority": priority, "review_state": record["review_state"],
              "current_mapping_state": [mapping_row(r) for r in own],
              "source_semantics": source_facts,
              "derived_consequences": combined_consequences,
              "review_clarifications": clarifications,
              "target_semantics": [{**glossary[x], "role": "historical_or_review_candidate_only" if x in candidate_iris else "asserted_target_expression"} for x in sorted(target_iris)],
              "mapping_property_chains": mapping_chain_facts(all_rows, relevant_chain_iris),
              "formal_consequences": [x for r in own for x in consequences(r)],
              "coverage_evidence": route, "critical_features": flags,
              "human_question": record["review"]["question"], "available_alternatives": record["review"]["alternatives"],
              "recommendation": record["review"]["recommendation"], "confidence": record["review"]["confidence"],
              "evidence": record["evidence"], "notes": record["notes"],
              "pinned_track_comparison": comparisons.get(iri)}
    return flags, existing, packet


def report_binding(root: Path | None = None) -> dict:
    """Bind reproducible reports to authenticated content, not their own commit.

    The custody inventory still authenticates the complete decision/workbook
    history and excludes generated reports. Execution receipts retain their
    separate HEAD binding; committing these reports cannot change their inputs.
    """
    root = ROOT if root is None else root
    evidence_paths = custody.assessment_paths(root)
    content = {"profile": REPORT_BINDING_PROFILE,
               "input_scope": custody.assessment_scope(root),
               "input_sha256": {p: sha(root / p) for p in sorted(evidence_paths)},
               "assessment_tool_sha256": sha(Path(__file__))}
    return {**content, "content_sha256": canonical_sha(content)}


def build_reports(scope, document):
    graph = source_graph()
    target = Graph().parse(ROOT / TARGET_PATH, format="turtle")
    rows = processed_rows()
    records = document["records"]
    terms = validate(scope, records, graph, rows)
    routes = coverage(terms, graph, rows)
    by_subject = defaultdict(list)
    for row in rows:
        by_subject[str(row.subject)].append(row)
    route_by_iri = {r["source_iri"]: r for r in routes}
    comparisons = next_comparison(rows)
    binding = report_binding()
    repertoire = Counter({predicate: 0 for predicate in mapping.ALLOWED_PREDICATES})
    repertoire.update(r.predicate or "explicit_blank" for r in rows)
    forms = Counter()
    rows_with_forms = Counter()
    for row in rows:
        f = expression_forms(row.expr)
        forms.update(f)
        rows_with_forms.update(f.keys())
    summary = {"source_term_count": len(terms), "source_counts_by_kind": dict(Counter(terms.values())),
               "assessment_record_count": len(records), "source_assessment_equality": True,
               "review_states": {k: sum(r["review_state"] == k for r in records) for k in sorted(STATES)},
               "assessment_outcomes": {k: sum(r["assessment_outcome"] == k for r in records) for k in sorted(OUTCOMES)},
               "workbook_rows": len(rows), "assertion_bearing_rows": sum(bool(r.predicate) for r in rows),
               "mapping_repertoire_rows": dict(sorted(repertoire.items())),
               "expression_occurrences": dict(sorted(forms.items())), "rows_with_expression_form": dict(sorted(rows_with_forms.items())),
               "coverage_counts": {k: sum(bool(r[k]) for r in routes) for k in ["direct_formal_mapping", "inherited_formal_mapping", "rule_or_chain_route", "typing_only_in_workbook", "explicit_blank", "no_established_formal_route"]},
               "direct_classes": sum(r["source_kind"] == "class" and r["direct_formal_mapping"] for r in routes),
               "direct_object_properties": sum(r["source_kind"] == "object_property" and r["direct_formal_mapping"] for r in routes),
               "chain_heads": sum(bool(r["chain_mapping_row_ids"]) for r in routes)}
    cov = {"binding": binding, "summary": summary, "terms": routes,
           "method": "Structural evidence over named source subclass/subproperty, named equivalence, and inverse paths plus governed direct mappings; chain heads and separately executed conditional query routes. Overlaps retained. No established route means none in this bounded method, not a complete OWL non-entailment proof. Domain/range alone never supplies relation coverage."}
    proposals, queue, glossary = [], [], {}
    for record in records:
        iri = record["source_iri"]
        own = by_subject[iri]
        flags, existing, packet = review_details(record, graph, target, own, rows,
                                                 route_by_iri[iri], comparisons, glossary)
        # A validated human decision supersedes workbook-era documentary prose;
        # retain that prose separately as historical evidence without rewriting it.
        proposed_text = (record["rationale"] if record.get("human_decision_record")
                         else " ".join(existing) if existing else record["rationale"])
        conflicts = rationale_mapping_conflicts(proposed_text, own)
        safe = (record["review_state"] == "final" or bool(existing)) and not conflicts
        # Safe prose may document a deferral/fact without endorsing its semantic resolution.
        proposal = {"source_iri": iri, "mapping_row_ids": record["mapping_row_ids"],
                    "critical_features": flags, "existing_workbook_rationales": existing,
                    "existing_evidence": record["evidence"],
                    "status": "safe_to_adopt" if safe else "human_review_required",
                    "proposed_documentary_rationale": proposed_text,
                    "documentary_consistency_issues": conflicts,
                    "semantic_decision_still_required": record["review_state"] != "final",
                    "scope": "Documentary reconstruction only; safe_to_adopt does not approve a target, predicate, or outstanding semantic decision."}
        validate_safe_rationale(proposal, own)
        proposals.append(proposal)
        if packet is not None:
            queue.append(packet)
    queue.sort(key=lambda r: (r["priority"], r["source_iri"]))
    rationales = {"binding": binding, "summary": {"existing_workbook_rationale_rows": sum(bool(r.row.reasoning_text) for r in rows),
                 "existing_workbook_rationale_terms": sum(bool(p["existing_workbook_rationales"]) for p in proposals),
                 "safe_documentary_proposals": sum(p["status"] == "safe_to_adopt" for p in proposals),
                 "human_review_required_proposals": sum(p["status"] == "human_review_required" for p in proposals),
                 "semantic_review_terms": len(queue)}, "proposals": proposals}
    reviews = {"binding": binding, "item_count": len(queue), "items": queue}
    return cov, rationales, reviews, glossary


def md_text(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_coverage(cov):
    s = cov["summary"]
    lines = ["# Current SSN/SOSA assessment and formal coverage", "", f"Bound to authenticated content SHA-256 `{cov['binding']['content_sha256']}` and exact input hashes in the JSON companion. This reproducible report is independent of the commit that stores it; execution receipts retain their own HEAD provenance.", "", cov["method"], "", "## Inventory and assessment", "", f"Dynamic source terms: **{s['source_term_count']}**; assessment records: **{s['assessment_record_count']}**; equality: **PASS**.", "", f"Kinds: `{s['source_counts_by_kind']}`. Review states: `{s['review_states']}`. Outcomes: `{s['assessment_outcomes']}`.", "", "These assessments describe unchanged workbook mapping assertions; registered documentary reasoning updates do not change assessment semantics. Final records reconstruct supported existing decisions; unresolved records do not reject or remove active axioms.", "", "## Formal coverage", "", "| Category | Terms |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k,v in s["coverage_counts"].items()]
    lines += ["", f"Direct classes: {s['direct_classes']}; direct object properties: {s['direct_object_properties']}; chain heads: {s['chain_heads']}. The historical 28 relation-mapped properties comprise 25 direct subproperties and 3 chain heads. A chain head is an incoming entailment route, not a source-to-target edge inclusion.", "", "Categories overlap: a directly mapped class can inherit additional constraints; a typing-only workbook property can be eligible for a separate conditional query. The query is not executed by the OWL product, and eligibility does not prove every assertion has suitable typing. Inherited coverage does not assert that inheritance is a sufficient final assessment outcome.", "", "## Mapping repertoire (rows)", "", "| Predicate | Rows |", "|---|---:|"]
    lines += [f"| `{k}` | {v} |" for k,v in s["mapping_repertoire_rows"].items()]
    lines += ["", f"Expression occurrences: `{s['expression_occurrences']}`; rows containing each form: `{s['rows_with_expression_form']}`.", "", "## Per-term coverage", "", "| Source | Direct | Inherited | Rule/chain | Typing-only artifact | No established route |", "|---|---|---|---|---|---|"]
    for r in cov["terms"]:
        lines.append(f"| `{compact(r['source_iri'])}` | " + " | ".join("yes" if r[k] else "—" for k in ["direct_formal_mapping", "inherited_formal_mapping", "rule_or_chain_route", "typing_only_in_workbook", "no_established_formal_route"]) + " |")
    return "\n".join(lines) + "\n"


def render_rationales(data):
    lines = ["# Current SSN/SOSA proposed rationales", "", "This report describes current workbook prose and documentary proposals; generating it does not edit the workbook. `safe_to_adopt` permits documentary prose only; a deferral explanation may be safely documented while the decision remains unresolved. Historical reports are evidence of prior decisions, not fresh reasoning runs.", "", f"Counts: `{data['summary']}`.", "", "| Source | Proposal status | Documentary rationale / unresolved concern | Evidence |", "|---|---|---|---|"]
    for p in data["proposals"]:
        issue = " ".join(p["documentary_consistency_issues"])
        lines.append(f"| `{compact(p['source_iri'])}` | {p['status']} | {md_text(p['proposed_documentary_rationale'])}{' **Documentary conflict: ' + md_text(issue) + '**' if issue else ''} | {'; '.join('`'+e+'`' for e in p['existing_evidence'])} |")
    return "\n".join(lines) + "\n"


def render_contextual_facts(facts):
    lines = []
    context = facts["contextual_axioms"] + facts["grouped_disjointness"]
    if context:
        lines += ["", "Asserted context (actual axiom subject and direction retained):"]
        lines += [f"- `{fact['provenance']}` / asserted: `{fact['axiom']}`." for fact in context]
    return lines + render_derived_facts(facts["derived_consequences"])


def render_derived_facts(consequences):
    lines = []
    for fact in consequences:
        lines += ["", f"**Derived evidence** (`{fact['provenance']}`, premises from {', '.join(fact['premise_provenance'])}): `{fact['axiom']}`. {fact['explanation']}",
                  "", "Asserted premises:"]
        lines += [f"- `{premise['provenance']}`: `{premise['axiom']}`" +
                  (f" (RowID `{premise['mapping_row_id']}`)." if premise.get("mapping_row_id") else ".")
                  for premise in fact["premises"]]
    return lines


def render_reviews(data, glossary):
    lines = ["# Current SSN/SOSA human semantic review", "", f"**{data['item_count']} finite unresolved source-term decisions.** Ordered: blanks, typing-only terms, strong equivalences, complex expressions, existentials, chains, cross-track differences, remaining target commitments.", "", "Workbook assertions remain unchanged. Repository facts and logical consequences below are separated from proposed alternatives. Recommendations do not approve a semantic change. Historical report claims are not current validation results. The JSON companion contains every RowID, bounded material source/target facts, exact target definitions, coverage path, and input hash. These evidence aids do not claim every ontology axiom or decide semantic adequacy. Incoming relations, restrictions and grouped disjointness retain their asserted subject and direction; derived evidence is separately labelled with its premises. Relevant source-native, target-native, and mapping property chains retain their distinct origins, ordered members, and resulting superproperties. Each chain runs from a member path to its superproperty; it does not decompose a superproperty edge.", "", "Target facts are deduplicated in the glossary after the queue; each item identifies its exact target IRIs. A missing direct target means no BFO/CCO relation was adopted, not an invitation to manufacture one. N-track comparisons are evidence to consider, not instructions to copy a different source/target interpretation.", "", "## Decision index", "", "| Priority | Source | Question |", "|---|---|---|"]
    for r in data["items"]:
        lines.append(f"| {r['priority']} | `{compact(r['source_iri'])}` | {md_text(r['human_question'])} |")
    for r in data["items"]:
        source = r["source_semantics"]
        lines += ["", f"## {compact(r['source_iri'])}", "", f"State: **{r['review_state']}**; priority {r['priority']}; evidence confidence: {r['confidence']}.", "", "**Repository facts — mapping:**"]
        for row in r["current_mapping_state"]:
            lines += ["", f"- `{row['location']}` / `{row['row_id']}`: `{row['predicate'] or '[blank]'}` {row['target'] or '(zero axioms)'}." ]
        lines += ["", "**Source semantics:** " + " ".join(source["definitions"] or ["No definition annotation found; see source logical axioms in JSON."]), "", "Source structure: " + "; ".join(source["logical_axioms"]), "", "Source advisory signature: " + ("; ".join(source["nonlogical_domain_range_notes"]) or "none recorded"), "", "**Target semantics:** " + ("; ".join(f"`{compact(t['iri'])}` ({t['label']}; {t['role']}; glossary)" for t in r["target_semantics"]) or "No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping."), "", "**Logical consequences:** " + " ".join(r["formal_consequences"])]
        lines += render_contextual_facts(source)
        lines += render_derived_facts(r["derived_consequences"])
        for clarification in r["review_clarifications"]:
            lines += ["", "**Review clarification:** " + clarification]
        chains = source["property_chains"] + r["mapping_property_chains"]
        chains += list({json_text(c): c for t in r["target_semantics"] for c in t["property_chains"]}.values())
        if chains:
            lines += ["", "**Relevant property chains (ordered path → superproperty):**"]
            lines += [f"- `{c['provenance']}`: `{c['axiom']}`" +
                      (f" (RowID `{c['mapping_row_id']}`)." if c.get("mapping_row_id") else ".") for c in chains]
        if r["coverage_evidence"]["rule_routes"]:
            lines += ["", "Additional route evidence: " + json.dumps(r["coverage_evidence"]["rule_routes"], ensure_ascii=False)]
        n = r["pinned_track_comparison"]
        if n and "material_cross_track_difference" in r["critical_features"]:
            lines += ["", f"**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#{n['location']}`: `{n['source_term']}` — `{n['status']}`, `{n['predicate']}` {n['target']}. {n['rationale']} Comparison basis: {n['match_kind']}."]
        lines += ["", f"**Human decision:** {r['human_question']}", "", "**Alternatives:**"]
        lines += [f"- {a}" for a in r["available_alternatives"]]
        lines += ["", f"**Proposed recommendation:** {r['recommendation']}", "", f"**Evidence:** {'; '.join('`'+e+'`' for e in r['evidence'])}.", "", f"**Notes:** {r['notes']}"]
    lines += ["", "## Target fact glossary", "", f"All facts below are extracted from `{TARGET_PATH}`; labels are display aids and IRIs control identity."]
    for iri, f in sorted(glossary.items()):
        lines += ["", f"### {compact(iri)} — {f['label']}", "", " ".join(f["definitions"] or ["No definition annotation present."]), "", "; ".join(f["logical_axioms"])]
        lines += render_contextual_facts(f)
        if f["property_chains"]:
            lines += ["", "Target-native chains: " + "; ".join(c["axiom"] for c in f["property_chains"])]
    return "\n".join(lines) + "\n"


def check_report_outputs(outputs: dict[str, str], directory: Path) -> None:
    """Check retained packets against the current facts, including every chain."""
    stale = [str(directory / name) for name, value in outputs.items()
             if not (directory / name).is_file() or (directory / name).read_text() != value]
    if stale:
        raise ValueError("stale assessment reports: " + ", ".join(stale))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write project assessment reports only; never changes inventory or mappings")
    parser.add_argument("--require-final", action="store_true", help="Fail readiness when any human semantic decision remains")
    args = parser.parse_args()
    try:
        scope = json.loads(SCOPE.read_text())
        doc = json.loads(ASSESSMENT.read_text())
        cov, rat, review, glossary = build_reports(scope, doc)
        outputs = {"current-ssn-sosa-coverage.json": json_text(cov), "current-ssn-sosa-coverage.md": render_coverage(cov),
                   "current-ssn-sosa-rationale-proposals.json": json_text(rat), "current-ssn-sosa-rationale-proposals.md": render_rationales(rat),
                   "current-ssn-sosa-human-review.json": json_text(review), "current-ssn-sosa-human-review.md": render_reviews(review, glossary)}
        if args.write:
            (ROOT / REPORT_DIRECTORY).mkdir(parents=True, exist_ok=True)
            for name, value in outputs.items():
                (ROOT / REPORT_DIRECTORY / name).write_text(value)
        else:
            check_report_outputs(outputs, ROOT / REPORT_DIRECTORY)
        print(json_text({"status": "PASS", "summary": cov["summary"], "rationales": rat["summary"]}), end="")
        if args.require_final and review["item_count"]:
            print("CURRENT TRACK NOT YET PUBLICATION READY — HUMAN SEMANTIC REVIEW REQUIRED")
            return 1
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
