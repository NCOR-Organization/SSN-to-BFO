#!/usr/bin/env python3
"""Project-local, exact-delta custody for semantic workbook evolution.

Historical documentary records remain D-only. This separate archive joins
authenticated documentary and semantic edges without rebinding any decision.
Recording an edge never installs a workbook or edits an assessment.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import current_documentary_workbook as documentary

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = documentary.WORKBOOK
PROFILE = "current-ssn-sosa-semantic-transition-v1"
TRANSITIONS = "reports/current-semantic-workbook/transitions"
VERSIONS = "reports/current-semantic-workbook/versions"
AUTHORIZATION_TYPES = frozenset({
    "RESTORE_PREVIOUSLY_APPROVED_DECISION",
    "REMOVE_PREVIOUSLY_REJECTED_MAPPING",
    "RESTORE_PREVIOUS_TECHNICAL_DEFERRAL",
    "EXPLICIT_NEW_HUMAN_DECISION",
})
SOURCE_TARGET_PATHS = ("imports/sosa.ttl", "imports/sosa-sampling.ttl",
                       "imports/ssn.ttl", "imports/ssn-systems.ttl", "imports/cco.ttl")
# These are existing immutable input identities, not permission to revise imports.
SOURCE_TARGET_SHA256 = {
    "imports/sosa.ttl": "0dad03b30c7fdd085e2629dfc0ebd10bb1dacbda73b2c375fb295ab6861ffb33",
    "imports/sosa-sampling.ttl": "f6e1d9451732bb132fa4ba567ca58fba752dcfbb43e66c5d4b660963bd0f7c1a",
    "imports/ssn.ttl": "434b50fecb32e14b30aac28310a76935a33fdc397e70fce887fd653069a59383",
    "imports/ssn-systems.ttl": "156870689643840c861aaead206458bcdfc9cded5f7107598dbf87e015861105",
    "imports/cco.ttl": "3ad8f098ecb3d7ca27464a1edf2795b90c69573843447d51f090e6f1b30694f4",
}
GOVERNED_INPUT_SHA256 = {
    "rules/ssn-hasproperty-conditional-mapping.rq": "b98376fc73f6c246e5f2567226ca1ba81536e4fbc2670905acfb2a43c991ff6d",
    "queries/source-classes-and-object-properties.rq": "6d00669a789d66a952674108924e831258706d1dd1c086cdc59412f422f427b9",
    "config/current-ssn-sosa-scope.json": "f9a1256e871c7421ecb75a37b23bcead31e505096ffe08adec0f7ad04acbf852",
    "mappings/SOSA-next-to-BFO-COMS.xlsx": "f3d81bad4dc3aa3cb2396571a4947951c1d443693135ccdca6c2787d074bc685",
}


def governed_input_hashes(root: Path) -> dict:
    values = {p: documentary.digest(documentary._path(root, p).read_bytes())
              for p in GOVERNED_INPUT_SHA256}
    if values != GOVERNED_INPUT_SHA256:
        raise ValueError("semantic transition cannot authorize governed rule/query/scope/parallel-track input changes")
    return values


def source_target_hashes(root: Path) -> dict:
    values = {p: documentary.digest(documentary._path(root, p).read_bytes())
              for p in SOURCE_TARGET_PATHS}
    if values != SOURCE_TARGET_SHA256:
        raise ValueError("semantic transition cannot authorize source/target identity changes; requires new review")
    return values


def snapshot(root: Path, sha256: str) -> Path:
    """Resolve exact archived bytes, rejecting ambiguous or modified snapshots."""
    sha256 = documentary._sha(sha256)
    found = []
    for directory in (documentary.VERSIONS, VERSIONS):
        relative = f"{directory}/{sha256}.xlsx"
        path = documentary._local_path(root, relative)
        if path.exists():
            found.append(documentary._bound_file(root, {"path": relative, "sha256": sha256}))
    if not found:
        raise ValueError(f"missing retained workbook snapshot: {sha256}")
    return found[0]


def workbook_rows(path: Path) -> dict:
    result = {}
    for sheet in documentary.workbook_view(path)["sheets"]:
        for number, row in enumerate(sheet["rows"][1:], 2):
            source, predicate, target, reasoning, row_id = row
            if not isinstance(source, str) or not source.strip():
                raise ValueError("semantic workbook row lacks source")
            if not isinstance(row_id, str) or not row_id.startswith("urn:uuid:"):
                raise ValueError("semantic workbook row lacks stable RowID")
            documentary._uuid(row_id.removeprefix("urn:uuid:"))
            if row_id in result:
                raise ValueError("duplicate semantic workbook RowID")
            if bool(predicate) != bool(target):
                raise ValueError("mapping predicate and target must both be present or blank")
            result[row_id] = {"worksheet": sheet["name"], "row": number,
                              "subject": source, "predicate": predicate, "target": target,
                              "reasoning": reasoning, "row_id": row_id}
    return result


def workbook_delta(old: Path, new: Path) -> dict:
    """Exact literal cell and RowID delta, including additions and removals."""
    before, after = workbook_rows(old), workbook_rows(new)
    fields = dict(zip("ABCDE", ("subject", "predicate", "target", "reasoning", "row_id")))
    changes, semantic, reasoning, added, removed, cleared = [], [], [], [], [], []
    for row_id in sorted(before.keys() | after.keys()):
        left, right = before.get(row_id), after.get(row_id)
        if left == right:
            continue
        cells = []
        moved = bool(left and right and (left["worksheet"], left["row"]) != (right["worksheet"], right["row"]))
        for column, field in fields.items():
            a, b = left[field] if left else None, right[field] if right else None
            if left is None or right is None or a != b or moved:
                cells.append({"column": column,
                              "old_cell": f"{left['worksheet']}!{column}{left['row']}" if left else None,
                              "new_cell": f"{right['worksheet']}!{column}{right['row']}" if right else None,
                              "old_value": a, "new_value": b})
        entry = {"row_id": row_id, "old": left, "new": right, "changed_cells": cells}
        changes.append(entry)
        if any(c["column"] in "ABCE" for c in cells):
            semantic.append(entry)
        if any(c["column"] == "D" for c in cells):
            reasoning.append({"row_id": row_id, "changes": [c for c in cells if c["column"] == "D"]})
        if left is None:
            added.append(right)
        if left and left["predicate"] and (right is None or left["subject"] != right["subject"]
                or left["predicate"] != right["predicate"] or left["target"] != right["target"]):
            removed.append(left)
            if right and not right["predicate"]:
                cleared.append(right)
    return {"changed_rows": changes, "semantic_changes": semantic,
            "documentary_reasoning_changes": reasoning, "added_rows": added,
            "removed_mapping_assertions": removed, "cleared_mapping_rows": cleared}


def _authority(root: Path, authorities: dict, delta: dict, new_path: Path) -> None:
    expected = {row["row_id"] for row in delta["changed_rows"]}
    if not isinstance(authorities, dict) or set(authorities) != expected:
        raise ValueError("semantic authority must cover exactly every changed RowID")
    for row in delta["changed_rows"]:
        value = authorities[row["row_id"]]
        if not isinstance(value, dict) or set(value) - {"authorization_type", "rationale", "evidence", "human_decision"}:
            raise ValueError("invalid semantic authority fields")
        category = value.get("authorization_type")
        if category not in AUTHORIZATION_TYPES:
            raise ValueError("unknown semantic authorization type")
        if not isinstance(value.get("rationale"), str) or not value["rationale"].strip():
            raise ValueError("semantic authority requires rationale")
        documentary._evidence(root, value.get("evidence"))
        for ref in value["evidence"]:
            if not ref.get("reference"):
                raise ValueError("semantic authority requires an exact historical evidence reference")
        if category in {"REMOVE_PREVIOUSLY_REJECTED_MAPPING", "RESTORE_PREVIOUS_TECHNICAL_DEFERRAL"}:
            if row["new"] and row["new"]["predicate"] and row in delta["semantic_changes"]:
                raise ValueError("removal/deferral authority cannot introduce a mapping")
        if category == "EXPLICIT_NEW_HUMAN_DECISION":
            decision = documentary._json(documentary._bound_file(root, value.get("human_decision")))
            own = row["new"] or row["old"]
            import generate_mapping_from_coms as mapping
            prefix, local = own["subject"].split(":", 1)
            subject = mapping.PREFIXES.get(prefix, "") + local
            if (decision.get("schema_version") != 1 or decision.get("review_state") != "final"
                    or decision.get("source_iri") != subject or not decision.get("reviewer_identity")
                    or not decision.get("question_response") or not decision.get("review_packet_snapshot")
                    or not decision.get("assessment_snapshot") or not decision.get("input_hashes")):
                raise ValueError("explicit semantic authorization requires an actual bound human decision")
            documentary._uuid(decision.get("decision_id", "").removeprefix("urn:uuid:"))
            documentary._timestamp(decision.get("review_timestamp"))
            inputs = decision["input_hashes"]
            if (not isinstance(inputs, dict)
                    or inputs.get("workbook_sha256") != documentary.digest(new_path.read_bytes())
                    or inputs.get("source_files_sha256") != {p: SOURCE_TARGET_SHA256[p] for p in SOURCE_TARGET_PATHS if p != "imports/cco.ttl"}
                    or inputs.get("target_sha256") != SOURCE_TARGET_SHA256["imports/cco.ttl"]):
                raise ValueError("new human decision does not approve the exact candidate inputs")
            for key in ("review_packet_snapshot", "assessment_snapshot"):
                documentary._bound_file(root, decision[key])
            rows = [r for r in workbook_rows(new_path).values() if r["subject"] == own["subject"]]
            formal = sorted(({"row_id": r["row_id"], "predicate": r["predicate"], "target": r["target"]}
                             for r in rows if r["predicate"] in mapping.MAPPING_PREDICATES),
                            key=lambda r: (r["row_id"], r["predicate"], r["target"]))
            if (decision.get("mapping_row_ids") != sorted(r["row_id"] for r in rows)
                    or decision.get("formal_mapping_assertions") != formal):
                raise ValueError("new human decision mapping approval differs from candidate")
            if formal:
                if (decision.get("decision_basis") != "formal_mapping_approval"
                        or decision.get("formal_mapping_approved") is not True
                        or decision.get("assessment_outcome") != "formal_mapping_adopted"):
                    raise ValueError("new human decision does not explicitly approve formal mapping")
            elif decision.get("assessment_outcome") == "inheritance_sufficient":
                if (decision.get("decision_basis") != "inheritance_sufficiency"
                        or decision.get("no_additional_direct_mapping_required") is not True):
                    raise ValueError("new human decision lacks explicit inheritance sufficiency")
                import current_assessment as assessment
                resolver = mapping.Resolver(root=root)
                raw, stats = mapping.read_workbook(new_path)
                processed = mapping.validate_and_process_rows(raw, resolver, stats)
                scope = documentary._json(root / "config/current-ssn-sosa-scope.json")
                terms = assessment.inventory(resolver.source_graph, scope)
                if subject not in terms:
                    raise ValueError("inheritance decision source is outside the governed inventory")
                route = assessment.coverage({subject: terms[subject]}, resolver.source_graph, processed)[0]
                if decision.get("formal_coverage_sha256") != assessment.canonical_sha(route):
                    raise ValueError("new inheritance decision has stale candidate formal coverage")
                assessment.validate_inheritance_sufficiency(
                    decision, route, root=root, workbook_path=new_path)
            elif (decision.get("decision_basis") != "semantic_rejection"
                    or decision.get("explicit_no_direct_mapping_adopted") is not True
                    or decision.get("assessment_outcome") != "no_direct_mapping"
                    or not decision.get("separate_semantic_conclusion")):
                raise ValueError("new human decision lacks explicit no-direct semantic conclusion")
        elif "human_decision" in value:
            raise ValueError("historical restoration must not impersonate a new decision")


def _validate_document(root: Path, document: dict, old: Path, new: Path) -> None:
    keys = {"schema_version", "profile", "transition_id", "workbook_path", "old_workbook_sha256",
            "new_workbook_sha256", "old_semantic_projection_sha256", "new_semantic_projection_sha256",
            "delta", "authorities", "editor_identity", "timestamp", "source_target_sha256",
            "generation_expectations", "governed_input_sha256", "prior_history_sha256"}
    if not isinstance(document, dict) or set(document) != keys:
        raise ValueError("invalid semantic transition fields")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1 or document["profile"] != PROFILE or document["workbook_path"] != WORKBOOK:
        raise ValueError("invalid semantic transition scope")
    documentary._uuid(document["transition_id"])
    documentary._timestamp(document["timestamp"])
    documentary._sha(document["prior_history_sha256"])
    if not isinstance(document["editor_identity"], str) or not document["editor_identity"].strip():
        raise ValueError("semantic transition requires editor identity")
    for prefix, path in (("old", old), ("new", new)):
        if documentary.digest(path.read_bytes()) != document[prefix + "_workbook_sha256"]:
            raise ValueError("semantic transition workbook hash mismatch")
        if documentary.semantic_projection_sha256(path) != document[prefix + "_semantic_projection_sha256"]:
            raise ValueError("semantic transition projection hash mismatch")
    if document["old_semantic_projection_sha256"] == document["new_semantic_projection_sha256"]:
        raise ValueError("semantic transition requires a semantic change; use documentary evolution")
    delta = workbook_delta(old, new)
    if not delta["semantic_changes"] or documentary.canonical_bytes(document["delta"]) != documentary.canonical_bytes(delta):
        raise ValueError("semantic transition declared delta differs from actual workbook delta")
    _authority(root, document["authorities"], delta, new)
    if document["source_target_sha256"] != source_target_hashes(root):
        raise ValueError("semantic transition source/target identity binding mismatch")
    if document["governed_input_sha256"] != governed_input_hashes(root):
        raise ValueError("semantic transition governed input binding mismatch")
    from current_semantic_generation import validate_expectations
    validate_expectations(root, old, new, document["generation_expectations"])


def validate_transition(root: Path, path: Path) -> dict:
    document = documentary._json(path)
    if path.name != document.get("transition_id", "") + ".json":
        raise ValueError("semantic transition filename/ID mismatch")
    old, new = (snapshot(root, document[key]) for key in ("old_workbook_sha256", "new_workbook_sha256"))
    _validate_document(root, document, old, new)
    return document


def _archive_files(root: Path, directory: str) -> list[Path]:
    path = documentary._local_path(root, directory)
    files = sorted(path.iterdir()) if path.exists() else []
    if any(not p.is_file() or p.is_symlink() or p.suffix != ".json" for p in files):
        raise ValueError("unsupported workbook transition archive entry")
    return files


def history_digest(bindings: list[dict]) -> str:
    """Bind ordered predecessor record bytes, in addition to workbook edges."""
    return documentary.digest(documentary.canonical_bytes(bindings))


def resolve_history(root: Path, current_path: Path | None = None, *, require_live: bool = True) -> dict:
    """Validate one unbranched mixed history rooted in the immutable baseline."""
    root = Path(root)
    baseline = documentary._baseline(root)
    documentary._historical_snapshot(root, baseline)
    records, paths, record_bindings = [], [], {}
    for directory, kind, validator in ((documentary.UPDATES, "documentary", documentary._validate_update),
                                        (TRANSITIONS, "semantic", validate_transition)):
        for path in _archive_files(root, directory):
            record = validator(root, path)
            records.append({**record, "kind": kind})
            relative = path.relative_to(root).as_posix()
            paths.append(relative)
            record_bindings[(kind, record.get("transition_id", record.get("update_id")))] = {
                "kind": kind, "path": relative, "sha256": documentary.digest(path.read_bytes())}
    initial = baseline["historical_workbook"]["sha256"]
    by_old, ids = {}, set()
    for record in records:
        old = record["old_workbook_sha256"]
        identity = record.get("transition_id", record.get("update_id"))
        if old in by_old or identity in ids:
            raise ValueError("duplicate or branching workbook transition chain")
        by_old[old] = record
        ids.add(identity)
    bindings = [{"kind": "baseline", "path": documentary.BASELINE,
                 "sha256": documentary.digest((root / documentary.BASELINE).read_bytes())}]
    chain, seen, tail = [], {initial}, initial
    while tail in by_old:
        record = by_old[tail]
        if record["kind"] == "semantic" and record["prior_history_sha256"] != history_digest(bindings):
            raise ValueError("semantic transition predecessor record bytes changed")
        tail = record["new_workbook_sha256"]
        if tail in seen:
            raise ValueError("cyclic workbook transition chain")
        if chain and documentary._timestamp(record["timestamp"]) < documentary._timestamp(chain[-1]["timestamp"]):
            raise ValueError("workbook transition timestamps are out of order")
        chain.append(record)
        bindings.append(record_bindings[(record["kind"], record.get("transition_id", record.get("update_id")))])
        seen.add(tail)
    if len(chain) != len(records):
        raise ValueError("missing or disconnected workbook transition chain")
    if require_live and documentary.digest(Path(current_path or root / WORKBOOK).read_bytes()) != tail:
        raise ValueError("current workbook has no complete documentary update chain or governed semantic transition chain")
    return {"baseline": baseline, "chain": chain, "paths": sorted(paths),
            "record_bindings": bindings,
            "tail_sha256": tail, "version_sha256": [initial, *(r["new_workbook_sha256"] for r in chain)]}


def validate_workbook_evolution(root: Path, historical_sha256: str, current_path: Path | None = None) -> Path:
    history = resolve_history(root, current_path)
    if historical_sha256 not in history["version_sha256"]:
        raise ValueError("decision workbook is not in anchored workbook history")
    return snapshot(root, historical_sha256)


def evidence_paths(root: Path) -> list[str]:
    history = resolve_history(root, require_live=False)
    paths = {documentary.BASELINE, *history["paths"]}
    paths.update(ref["path"] for ref in history["baseline"]["immutable_evidence"])
    for sha in history["version_sha256"]:
        paths.add(snapshot(root, sha).relative_to(root).as_posix())
    for record in history["chain"]:
        entries = record["authorities"].values() if record["kind"] == "semantic" else record["changes"]
        for entry in entries:
            paths.update(documentary._evidence_paths(root, entry["evidence"]))
            if "human_decision" in entry:
                ref = entry["human_decision"]
                decision = documentary._json(documentary._bound_file(root, ref))
                paths.add(ref["path"])
                for key in ("assessment_snapshot", "review_packet_snapshot", "inheritance_sufficiency_evidence"):
                    if decision.get(key):
                        documentary._bound_file(root, decision[key])
                        paths.add(decision[key]["path"])
    return sorted(paths)


def create_transition(root: Path, old_path: Path, new_path: Path, authorities: dict, *,
                      editor_identity: str, timestamp: str | None = None,
                      transition_id: str | None = None, generation_expectations: dict | None = None) -> Path:
    """Archive a fully checked transition; never install it or edit decisions."""
    root, old_path, new_path = Path(root), Path(old_path), Path(new_path)
    history = resolve_history(root, require_live=False)
    old_hash, new_hash = (documentary.digest(p.read_bytes()) for p in (old_path, new_path))
    if old_hash != history["tail_sha256"]:
        raise ValueError("semantic transition must extend existing chain tail")
    if new_hash in history["version_sha256"]:
        raise ValueError("semantic transition must not cycle to prior workbook")
    from current_semantic_generation import compute_expectations
    document = {"schema_version": 1, "profile": PROFILE,
                "transition_id": transition_id or str(uuid4()), "workbook_path": WORKBOOK,
                "old_workbook_sha256": old_hash, "new_workbook_sha256": new_hash,
                "prior_history_sha256": history_digest(history["record_bindings"]),
                "old_semantic_projection_sha256": documentary.semantic_projection_sha256(old_path),
                "new_semantic_projection_sha256": documentary.semantic_projection_sha256(new_path),
                "delta": workbook_delta(old_path, new_path), "authorities": authorities,
                "editor_identity": editor_identity, "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
                "source_target_sha256": source_target_hashes(root),
                "governed_input_sha256": governed_input_hashes(root),
                "generation_expectations": generation_expectations if generation_expectations is not None else compute_expectations(root, old_path, new_path)}
    _validate_document(root, document, old_path, new_path)
    if history["chain"] and documentary._timestamp(document["timestamp"]) < documentary._timestamp(history["chain"][-1]["timestamp"]):
        raise ValueError("workbook transition timestamps are out of order")
    destination = documentary._local_path(root, f"{TRANSITIONS}/{document['transition_id']}.json")
    if destination.exists():
        raise ValueError("semantic transition ID already exists")
    created = []
    try:
        for path, sha in ((old_path, old_hash), (new_path, new_hash)):
            target = documentary._local_path(root, f"{VERSIONS}/{sha}.xlsx")
            if target.exists():
                snapshot(root, sha)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                created.append(target)
                stream.write(path.read_bytes())
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            created.append(destination)
            stream.write(documentary.canonical_bytes(document))
        resolve_history(root, require_live=False)
    except Exception:
        for path in reversed(created):
            path.unlink()
        raise
    return destination


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    delta = commands.add_parser("delta")
    record = commands.add_parser("record")
    for sub in (delta, record):
        sub.add_argument("--old", type=Path, required=True)
        sub.add_argument("--new", type=Path, required=True)
    record.add_argument("--authorities", type=Path, required=True)
    record.add_argument("--editor", required=True)
    record.add_argument("--timestamp")
    record.add_argument("--transition-id")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            history = resolve_history(args.root)
            result = {"status": "PASS", "tail_sha256": history["tail_sha256"],
                      "semantic_transitions": sum(r["kind"] == "semantic" for r in history["chain"])}
        elif args.command == "delta":
            from current_semantic_generation import compute_expectations
            result = {"delta": workbook_delta(args.old, args.new),
                      "generation_expectations": compute_expectations(args.root, args.old, args.new)}
        else:
            path = create_transition(args.root, args.old, args.new, documentary._json(args.authorities),
                                     editor_identity=args.editor, timestamp=args.timestamp, transition_id=args.transition_id)
            result = {"transition": path.relative_to(args.root).as_posix(), "live_workbook_modified": False}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
