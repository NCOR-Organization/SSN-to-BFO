#!/usr/bin/env python3
"""Current applicability, separate from immutable human-review authentication.

This project-local layer compares every governed version, never just the net
delta. A transition is authorization to change a workbook, not permission to
carry a prior conclusion over materially changed evidence.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import current_documentary_workbook as documentary

PREPARED = "reports/current-decision-applicability/prepared"
RECORDS = "reports/current-decision-applicability/records"
PROFILE = "current-ssn-sosa-decision-applicability-v1"
NON_MATERIAL = "NON_MATERIAL_TO_DECISION"
MATERIAL = "MATERIAL_REQUIRES_REOPEN"
# Explicit human authorization from this task. These are additive determinations,
# not edits to the original sample decisions. Future approvals need new records.
PREPARED_SHA256 = {
    f"{PREPARED}/hasSample-forProperty.json": "9d04174ff90b91dd48311189bd07d4bfac9eca46985d448cef569125d478e2de",
    f"{PREPARED}/isSampleOf-forProperty.json": "f6d98b784719251cd7a7f0ea8da14c5e7dfe7cad900b95152a0f8e64e9fb4213",
    # Same explicit Part 6 approval, bound additively to the October 26
    # three-term candidate. The original five-term plans remain immutable;
    # the actual packet comparison still permits only that exact chain removal.
    f"{PREPARED}/hasSample-forProperty-three-term-2026-10-26.json": "09e17d3bf0a6c09e2c184db66aaaae331f610d7f78db33d5308a0df19890a80c",
    f"{PREPARED}/isSampleOf-forProperty-three-term-2026-10-26.json": "da1f762851c24de45db6537bbf31fcd113a51382bd75040004fdbf92ca874ff2",
}


def semantic_packet(packet: dict) -> dict:
    """Column-D prose may evolve only through the independent custody chain."""
    result = copy.deepcopy(packet)
    for row in result.get("current_mapping_state", []):
        row.pop("existing_rationale", None)
    return result


def own_semantic_rows(workbook: Path, source_iri: str) -> list[dict]:
    # Literal A/B/C/E values and physical locations matter, including typing,
    # blank rows and membership. Processed mapping assertions alone omit these.
    import generate_mapping_from_coms as mapping
    names = {source_iri, mapping.compact_iri(mapping.URIRef(source_iri))}
    return [{"sheet": sheet["name"], "row": n,
             "values": [values[i] for i in (0, 1, 2, 4)]}
            for sheet in documentary.workbook_view(workbook)["sheets"]
            for n, values in enumerate(sheet["rows"], 1)
            if n > 1 and mapping.normalize_cell(values[0]) in names]


def _version(path: Path) -> dict:
    return {"sha256": documentary.digest(path.read_bytes()),
            "semantic_projection_sha256": documentary.semantic_projection_sha256(path)}


def _validate_prepared(root: Path, path: Path) -> dict:
    relative = path.relative_to(root).as_posix()
    # A self-authored file claiming a human identity is not new authorization.
    # Future materiality judgments require a new explicit approval and an
    # additive registry entry; relocating a known record cannot evade its pin.
    if relative not in PREPARED_SHA256:
        raise ValueError("unregistered human applicability determination")
    if documentary.digest(path.read_bytes()) != PREPARED_SHA256[relative]:
        raise ValueError("immutable prepared applicability authorization drift")
    document = documentary._json(path)
    fields = {"schema_version", "profile", "applicability_id", "status",
              "decision_id", "source_iri", "old_workbook", "new_workbook",
              "changed_dependency", "old_dependency_state", "new_dependency_state",
              "classification", "rationale", "supporting_evidence",
              "reviewer_identity", "timestamp"}
    if not isinstance(document, dict) or set(document) != fields:
        raise ValueError("invalid prepared applicability fields")
    if (document["schema_version"] != 1 or document["profile"] != PROFILE
            or document["status"] != "PREPARED_NOT_ACTIVE"):
        raise ValueError("invalid prepared applicability scope")
    documentary._uuid(document["applicability_id"])
    documentary._uuid(document["decision_id"].removeprefix("urn:uuid:"))
    if document["classification"] not in {NON_MATERIAL, MATERIAL}:
        raise ValueError("invalid dependency materiality classification")
    for key in ("source_iri", "rationale", "reviewer_identity"):
        if not isinstance(document[key], str) or not document[key].strip():
            raise ValueError(f"applicability requires {key}")
    documentary._timestamp(document["timestamp"])
    if set(document["old_workbook"]) != {"sha256", "semantic_projection_sha256"}:
        raise ValueError("invalid old applicability version")
    for value in document["old_workbook"].values():
        documentary._sha(value)
    if (set(document["new_workbook"]) != {"sha256", "semantic_projection_sha256"}
            or document["new_workbook"]["sha256"] is not None):
        raise ValueError("prepared applicability must await full-byte version binding")
    documentary._sha(document["new_workbook"]["semantic_projection_sha256"])
    if document["changed_dependency"] != "mapping_property_chains":
        raise ValueError("only explicitly reviewed packet-chain context is supported")
    if document["old_dependency_state"] == document["new_dependency_state"]:
        raise ValueError("applicability record requires an exact changed dependency")
    documentary._evidence(root, document["supporting_evidence"])
    return document


def validate_prepared_records(root: Path) -> None:
    for relative in PREPARED_SHA256:
        path = root / relative
        if path.exists():
            _validate_prepared(root, path)


def _bound_records(root: Path) -> list[dict]:
    directory = documentary._local_path(root, RECORDS)
    paths = sorted(directory.iterdir()) if directory.exists() else []
    results, ids = [], set()
    for path in paths:
        if not path.is_file() or path.is_symlink() or path.suffix != ".json":
            raise ValueError("unsupported applicability archive entry")
        record = documentary._json(path)
        if (not isinstance(record, dict) or set(record) != {
                "schema_version", "profile", "binding_id", "prepared_record",
                "transition_id", "old_workbook", "new_workbook", "timestamp"}
                or record["schema_version"] != 1 or record["profile"] != PROFILE):
            raise ValueError("invalid bound applicability record")
        ident = documentary._uuid(record["binding_id"])
        if path.name != ident + ".json" or ident in ids:
            raise ValueError("duplicate or mismatched applicability binding ID")
        ids.add(ident)
        documentary._uuid(record["transition_id"])
        documentary._timestamp(record["timestamp"])
        prepared_path = documentary._bound_file(root, record["prepared_record"])
        prepared = _validate_prepared(root, prepared_path)
        if (record["old_workbook"] != prepared["old_workbook"]
                or record["new_workbook"].get("semantic_projection_sha256") !=
                prepared["new_workbook"]["semantic_projection_sha256"]
                or set(record["new_workbook"]) != {"sha256", "semantic_projection_sha256"}):
            raise ValueError("applicability binding changes its human determination")
        documentary._sha(record["new_workbook"]["sha256"])
        results.append({**record, "determination": prepared})
    return results


def validate_step(root: Path, decision: dict, old: Path, new: Path,
                  transition: dict, old_state: dict, new_state: dict) -> None:
    """A generic semantic transition never authorizes material carry-forward."""
    iri = decision["source_iri"]
    if not new_state.get("source_exists"):
        raise ValueError(f"{MATERIAL}: reviewed source term no longer exists: {iri}")
    if own_semantic_rows(old, iri) != own_semantic_rows(new, iri):
        raise ValueError(f"{MATERIAL}: reviewed A/B/C/E rows or RowID membership changed: {iri}")
    if old_state["coverage"] != new_state["coverage"]:
        raise ValueError(f"{MATERIAL}: direct/inherited/rule coverage changed: {iri}")
    before, after = semantic_packet(old_state["packet"]), semantic_packet(new_state["packet"])
    changed = {key for key in before.keys() | after.keys() if before.get(key) != after.get(key)}
    for dependency in sorted(changed):
        if dependency != "mapping_property_chains":
            raise ValueError(f"{MATERIAL}: packet dependency changed ({dependency}): {iri}")
        # A stated premise cannot be demoted by a generic transition or a
        # contextual carry-forward record. Existing approvals can explicitly
        # identify these packet fields as premises; all other semantic packet
        # fields above already require reopening unconditionally.
        if dependency in decision.get("rationale_dependency_keys", []):
            raise ValueError(f"{MATERIAL}: recorded rationale premise changed ({dependency}): {iri}")
        import generate_mapping_from_coms as mapping
        rationale = decision.get("rationale", "") + " " + decision.get("question_response", "")
        heads = {chain["superproperty"] for chain in before.get(dependency, []) + after.get(dependency, [])}
        if any(token and token in rationale for head in heads
               for token in (head, mapping.compact_iri(mapping.URIRef(head)), head.rsplit("/", 1)[-1])):
            raise ValueError(f"{MATERIAL}: changed chain is mentioned in the recorded rationale: {iri}")
        matches = [record for record in _bound_records(root)
                   if record["transition_id"] == transition.get("transition_id")
                   and record["old_workbook"] == _version(old)
                   and record["new_workbook"] == _version(new)
                   and record["determination"]["decision_id"] == decision["decision_id"]
                   and record["determination"]["source_iri"] == iri
                   and record["determination"]["changed_dependency"] == dependency
                   and record["determination"]["old_dependency_state"] == before.get(dependency)
                   and record["determination"]["new_dependency_state"] == after.get(dependency)]
        if len(matches) != 1 or matches[0]["determination"]["classification"] != NON_MATERIAL:
            raise ValueError(f"{MATERIAL}: changed dependency requires an explicit non-material determination ({dependency}): {iri}")


def validate_current_applicability(root: Path, decision: dict, historical: Path,
                                   current: Path, state_for_workbook) -> None:
    """Authenticate the complete path, then compare each intermediate state."""
    import current_semantic_workbook as semantic
    validate_prepared_records(root)
    original = documentary.digest(historical.read_bytes())
    if original == documentary.digest(current.read_bytes()):
        semantic.resolve_history(root, current_path=current)
        return
    history = semantic.resolve_history(root, current_path=current)
    states = {original: state_for_workbook(historical)}
    reached = False
    for transition in history["chain"]:
        if transition["old_workbook_sha256"] == original:
            reached = True
        if not reached:
            continue
        old = semantic.snapshot(root, transition["old_workbook_sha256"])
        new = semantic.snapshot(root, transition["new_workbook_sha256"])
        prior_state = states.get(transition["old_workbook_sha256"])
        if prior_state is None:
            prior_state = state_for_workbook(old)
        new_state = state_for_workbook(new)
        validate_step(root, decision, old, new, transition, prior_state, new_state)
        states[transition["new_workbook_sha256"]] = new_state
    if not reached:
        raise ValueError("historical decision is not on the complete current version chain")


def bind_prepared_applicability(root: Path, prepared_path: Path,
                                transition_id: str, *, timestamp: str | None = None) -> Path:
    """Bind an approved determination to exact archived bytes; never edit it.

    This operation does not authorize or install a workbook, nor does it change
    an assessment or original decision. Applicability still validates actual
    packet dependencies independently when the current decision is checked.
    """
    import current_semantic_workbook as semantic
    prepared_path = Path(prepared_path)
    if not prepared_path.resolve().is_relative_to(root.resolve()):
        raise ValueError("prepared applicability must be project-local")
    prepared = _validate_prepared(root, prepared_path)
    chain = semantic.resolve_history(root, require_live=False)["chain"]
    matches = [item for item in chain if item.get("transition_id") == transition_id]
    if len(matches) != 1:
        raise ValueError("applicability requires a validated semantic transition")
    transition = matches[0]
    old = semantic.snapshot(root, transition["old_workbook_sha256"])
    new = semantic.snapshot(root, transition["new_workbook_sha256"])
    if (_version(old) != prepared["old_workbook"] or
            _version(new)["semantic_projection_sha256"] != prepared["new_workbook"]["semantic_projection_sha256"]):
        raise ValueError("transition does not match the prepared materiality determination")
    ident = str(uuid4())
    document = {"schema_version": 1, "profile": PROFILE, "binding_id": ident,
                "prepared_record": {"path": prepared_path.relative_to(root).as_posix(),
                                    "sha256": documentary.digest(prepared_path.read_bytes())},
                "transition_id": transition_id, "old_workbook": _version(old),
                "new_workbook": _version(new),
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat()}
    documentary._timestamp(document["timestamp"])
    if any(r["transition_id"] == transition_id and
           r["determination"]["decision_id"] == prepared["decision_id"] and
           r["determination"]["changed_dependency"] == prepared["changed_dependency"]
           for r in _bound_records(root)):
        raise ValueError("applicability determination is already bound")
    output = documentary._local_path(root, f"{RECORDS}/{ident}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(documentary.canonical_bytes(document))
    return output


def evidence_paths(root: Path) -> list[str]:
    result = set()
    for folder in (PREPARED, RECORDS):
        for path in (root / folder).glob("*.json"):
            result.add(path.relative_to(root).as_posix())
            if folder == PREPARED:
                result.update(documentary._evidence_paths(
                    root, _validate_prepared(root, path)["supporting_evidence"]))
    return sorted(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--bind-prepared", type=Path, required=True)
    parser.add_argument("--transition-id", required=True)
    args = parser.parse_args()
    path = args.bind_prepared if args.bind_prepared.is_absolute() else args.root / args.bind_prepared
    print(bind_prepared_applicability(args.root, path, args.transition_id))


if __name__ == "__main__":
    main()
