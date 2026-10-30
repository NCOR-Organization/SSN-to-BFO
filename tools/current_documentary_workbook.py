#!/usr/bin/env python3
"""Snapshot-backed documentary evolution for this project's current workbook.

This is deliberately not a generalized COMS facility. Only literal Reasoning
cell values may evolve; semantic cells, row positions and sheet identity remain
bound to the original workbook. Decision records are never rewritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from uuid import UUID, uuid4
from zipfile import BadZipFile

from openpyxl import load_workbook

import current_retained_evidence as retained

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = "mappings/SSN2BFO-COMS.xlsx"
BASELINE = "config/current-documentary-workbook-baseline.json"
BASELINE_SHA256 = "3eab7aa7ce498efae7b1d31a33852134206d3ee7c63c804e023ae38d1de063e8"
VERSIONS = "reports/current-documentary-workbook/versions"
UPDATES = "reports/current-documentary-workbook/updates"
HEADERS = ("sssom:subject_id", "sssom:predicate_id", "coms:Target",
           "coms:Reasoning", "coms:RowID")
PROFILE = "current-ssn-sosa-workbook-abc-e-v1"
SHEETS = ("Sheet1", "Sheet2")


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def value_hash(value) -> str:
    return digest(canonical_bytes(value))


def _json(path: Path):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def _local_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("missing project-local evidence path")
    rel = Path(relative)
    result = root / rel
    if (rel.is_absolute() or ".." in rel.parts or rel.as_posix() != relative
            or not result.resolve().is_relative_to(root.resolve())
            or any((root / Path(*rel.parts[:n])).is_symlink() for n in range(1, len(rel.parts) + 1))):
        raise ValueError(f"non-project or noncanonical evidence path: {relative}")
    return result


def _path(root: Path, relative: str) -> Path:
    result = _local_path(root, relative)
    if not result.is_file():
        raise ValueError(f"missing retained evidence: {relative}")
    return result


def _sha(value) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("invalid SHA-256")
    return value


def _bound_file(root: Path, ref: dict, *, allow_retained: bool = False) -> Path:
    if not isinstance(ref, dict):
        raise ValueError("invalid evidence reference")
    # Physical workbook versions and immutable decisions remain strict. Only
    # historical supporting evidence may resolve its exact bytes elsewhere.
    return retained.resolve(root, ref.get("path"), ref.get("sha256"),
                            allow_retained=allow_retained)


def _evidence_paths(root: Path, refs) -> set[str]:
    return {path for ref in refs
            for path in retained.evidence_paths(root, ref["path"], ref["sha256"])}


def workbook_view(path: Path) -> dict:
    """Read literal values without normalizing whitespace or null/empty text."""
    data = path.read_bytes()
    try:
        workbook = load_workbook(BytesIO(data), read_only=False, data_only=False,
                                 keep_links=True)
    except (BadZipFile, KeyError) as exc:
        raise ValueError("invalid documentary workbook archive") from exc
    try:
        if tuple(workbook.sheetnames) != SHEETS:
            raise ValueError("unsupported workbook sheet identity/order")
        if workbook._external_links:
            raise ValueError("external workbook links are not documentary cells")
        sheets = []
        for worksheet in workbook:
            if worksheet.max_column != 5 or worksheet.max_row < 2:
                raise ValueError("unsupported workbook columns/rows")
            if worksheet.sheet_state != "visible" or worksheet.merged_cells.ranges:
                raise ValueError("unsupported hidden or merged worksheet")
            if tuple(worksheet.cell(1, c).value for c in range(1, 6)) != HEADERS:
                raise ValueError("current workbook headers differ")
            rows = []
            for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row,
                                           min_col=1, max_col=5):
                values = []
                for cell in row:
                    if cell.data_type == "f" or (cell.value is not None and not isinstance(cell.value, str)):
                        raise ValueError(f"unsupported nonliteral cell: {worksheet.title}!{cell.coordinate}")
                    # openpyxl exposes an explicitly empty inline string as
                    # None. Preserve its string type so it cannot impersonate
                    # an absent semantic value in the projection.
                    values.append("" if cell.data_type == "inlineStr" and cell.value is None else cell.value)
                rows.append(values)
            sheets.append({"name": worksheet.title, "rows": rows})
        return {"profile": PROFILE, "sheets": sheets}
    finally:
        workbook.close()


def semantic_projection(path: Path) -> dict:
    view = workbook_view(path)
    return {"profile": PROFILE, "columns": ["A", "B", "C", "E"],
            "sheets": [{"name": sheet["name"],
                        "rows": [{"row": n, "values": [row[i] for i in (0, 1, 2, 4)]}
                                 for n, row in enumerate(sheet["rows"], 1)]}
                       for sheet in view["sheets"]]}


def semantic_projection_sha256(path: Path) -> str:
    return value_hash(semantic_projection(path))


def _baseline(root: Path) -> dict:
    path = _path(root, BASELINE)
    if digest(path.read_bytes()) != BASELINE_SHA256:
        raise ValueError("immutable documentary baseline hash drift")
    document = _json(path)
    if (document.get("schema_version") != 1 or document.get("profile") != PROFILE
            or document.get("workbook_path") != WORKBOOK):
        raise ValueError("invalid documentary baseline")
    return document


def _snapshot(root: Path, sha256: str) -> Path:
    sha256 = _sha(sha256)
    return _bound_file(root, {"path": f"{VERSIONS}/{sha256}.xlsx", "sha256": sha256})


def _changes(old: Path, new: Path) -> list[dict]:
    before, after = workbook_view(old), workbook_view(new)
    if semantic_projection(old) != semantic_projection(new):
        raise ValueError("semantic workbook projection changed")
    changes = []
    for a, b in zip(before["sheets"], after["sheets"], strict=True):
        for index, (left, right) in enumerate(zip(a["rows"], b["rows"], strict=True), 1):
            if left[3] != right[3]:
                if index == 1:
                    raise ValueError("Reasoning header is not a documentary value")
                if not isinstance(left[0], str) or not left[0].strip():
                    raise ValueError("documentary changes require an existing source row")
                row_id = left[4]
                if not isinstance(row_id, str) or not row_id.startswith("urn:uuid:"):
                    raise ValueError("documentary changes require an existing RowID")
                _uuid(row_id.removeprefix("urn:uuid:"))
                changes.append({"sheet": a["name"], "cell": f"D{index}",
                                "row_id": left[4], "old_value": left[3],
                                "new_value": right[3], "old_value_sha256": value_hash(left[3]),
                                "new_value_sha256": value_hash(right[3])})
    if not changes:
        raise ValueError("documentary update must change at least one Reasoning cell")
    return changes


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError
        return parsed
    except (ValueError, TypeError):
        raise ValueError("documentary timestamp must include a timezone") from None


def _uuid(value: str) -> str:
    try:
        if str(UUID(value)) != value:
            raise ValueError
        return value
    except (ValueError, TypeError, AttributeError):
        raise ValueError("invalid canonical documentary update UUID") from None


def _evidence(root: Path, refs) -> None:
    if not isinstance(refs, list) or not refs:
        raise ValueError("each documentary value requires evidence")
    for ref in refs:
        if (not isinstance(ref, dict) or not {"path", "sha256"} <= set(ref)
                or set(ref) - {"path", "sha256", "reference"}
                or ("reference" in ref and (not isinstance(ref["reference"], str) or not ref["reference"].strip()))):
            raise ValueError("invalid documentary evidence reference")
        _bound_file(root, ref, allow_retained=True)


def _validate_update(root: Path, path: Path) -> dict:
    document = _json(path)
    expected_keys = {"schema_version", "profile", "update_id", "workbook_path",
                     "old_workbook_sha256", "new_workbook_sha256",
                     "old_semantic_projection_sha256", "new_semantic_projection_sha256",
                     "allowed_column", "semantic_columns_unchanged", "timestamp",
                     "editor_identity", "changes"}
    if not isinstance(document, dict) or set(document) != expected_keys:
        raise ValueError("invalid documentary update fields")
    if (document["schema_version"] != 1 or document["profile"] != PROFILE
            or document["workbook_path"] != WORKBOOK
            or document["allowed_column"] != "coms:Reasoning"
            or document["semantic_columns_unchanged"] is not True):
        raise ValueError("invalid documentary update scope")
    update_id = _uuid(document["update_id"])
    if path.name != update_id + ".json":
        raise ValueError("documentary update filename/ID mismatch")
    _timestamp(document["timestamp"])
    if not isinstance(document["editor_identity"], str) or not document["editor_identity"].strip():
        raise ValueError("documentary update requires an editor identity")
    old = _snapshot(root, document["old_workbook_sha256"])
    new = _snapshot(root, document["new_workbook_sha256"])
    old_projection, new_projection = semantic_projection_sha256(old), semantic_projection_sha256(new)
    if (old_projection != new_projection
            or document["old_semantic_projection_sha256"] != old_projection
            or document["new_semantic_projection_sha256"] != new_projection):
        raise ValueError("documentary semantic projection hash mismatch")
    actual = _changes(old, new)
    declared = document["changes"]
    if not isinstance(declared, list) or len(declared) != len(actual):
        raise ValueError("documentary changed-cell manifest is incomplete")
    for expected, entry in zip(actual, declared, strict=True):
        if not isinstance(entry, dict) or set(entry) != set(expected) | {"evidence"}:
            raise ValueError("invalid changed-cell fields")
        if {k: v for k, v in entry.items() if k != "evidence"} != expected:
            raise ValueError("documentary changed-cell manifest differs from snapshots")
        _evidence(root, entry["evidence"])
    return document


def _historical_snapshot(root: Path, baseline: dict) -> Path:
    historical = baseline["historical_workbook"]
    initial = _snapshot(root, historical["sha256"])
    if (historical.get("path") != initial.relative_to(root).as_posix()
            or semantic_projection_sha256(initial) != historical["semantic_projection_sha256"]):
        raise ValueError("historical workbook projection binding mismatch")
    return initial


def _history(root: Path) -> tuple[dict, list[dict], list[Path]]:
    baseline = _baseline(root)
    _historical_snapshot(root, baseline)
    historical = baseline["historical_workbook"]
    directory = _local_path(root, UPDATES)
    files = sorted(directory.iterdir()) if directory.exists() else []
    if any(not p.is_file() or p.is_symlink() or p.suffix != ".json" for p in files):
        raise ValueError("unsupported documentary update archive entry")
    documents = [_validate_update(root, p) for p in files]
    by_old = {}
    ids = set()
    for document in documents:
        old = document["old_workbook_sha256"]
        if old in by_old or document["update_id"] in ids:
            raise ValueError("duplicate or branching documentary update chain")
        by_old[old] = document
        ids.add(document["update_id"])
    chain, visited = [], {historical["sha256"]}
    current = historical["sha256"]
    while current in by_old:
        document = by_old[current]
        current = document["new_workbook_sha256"]
        if current in visited:
            raise ValueError("cyclic documentary update chain")
        if chain and _timestamp(document["timestamp"]) < _timestamp(chain[-1]["timestamp"]):
            raise ValueError("documentary update timestamps are out of order")
        visited.add(current)
        chain.append(document)
    if len(chain) != len(documents):
        raise ValueError("disconnected documentary update chain")
    return baseline, chain, files


def validate_workbook_evolution(root: Path, historical_sha256: str,
                                current_path: Path | None = None) -> Path:
    """Return verified historical bytes after validating an explicit transition."""
    root = Path(root)
    baseline, chain, _ = _history(root)
    current_path = Path(current_path) if current_path is not None else root / WORKBOOK
    live_hash = digest(current_path.read_bytes())
    historical_sha256 = _sha(historical_sha256)
    history_hashes = [baseline["historical_workbook"]["sha256"]] + [d["new_workbook_sha256"] for d in chain]
    if historical_sha256 not in history_hashes:
        raise ValueError("decision workbook is not in the anchored documentary history")
    if live_hash != history_hashes[-1]:
        raise ValueError("current workbook has no complete documentary update chain")
    historical = _snapshot(root, historical_sha256)
    if semantic_projection_sha256(current_path) != baseline["historical_workbook"]["semantic_projection_sha256"]:
        raise ValueError("current workbook semantic projection changed")
    return historical


def validate_immutable_decisions(root: Path, records: list[dict]) -> None:
    """Guard anchored records before the caller branches on review/finality."""
    try:
        _validate_immutable_decisions(Path(root), records)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise ValueError(f"immutable decision evidence failed: {exc}") from exc


def _validate_immutable_decisions(root: Path, records: list[dict]) -> None:
    baseline = _baseline(root)
    _historical_snapshot(root, baseline)
    for ref in baseline["immutable_evidence"]:
        _bound_file(root, ref)
    for entry in baseline["decisions"]:
        matching = [record for record in records if record.get("source_iri") == entry["source_iri"]]
        if len(matching) != 1:
            raise ValueError("immutable decision assessment is missing or duplicated")
        # Use the assessment module's established canonical serialization.
        encoded = (json.dumps(matching[0], indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
        if digest(encoded) != entry["assessment_record_sha256"]:
            raise ValueError(f"immutable decision assessment drift: {entry['source_iri']}")
        decision_path = _bound_file(root, {"path": entry["path"], "sha256": entry["sha256"]})
        decision = _json(decision_path)
        if (decision.get("decision_id") != entry["decision_id"]
                or decision.get("source_iri") != entry["source_iri"]
                or decision.get("input_hashes", {}).get("workbook_sha256") != baseline["historical_workbook"]["sha256"]):
            raise ValueError("immutable decision anchor mismatch")


def evidence_paths(root: Path) -> list[str]:
    root = Path(root)
    # Mixed history uses the semantic coordinator, but each documentary edge
    # still passes this module's unchanged D-only validator.
    if (root / "reports/current-semantic-workbook/transitions").exists():
        import current_semantic_workbook as semantic
        return semantic.evidence_paths(root)
    # Discovery also serves small report-only fixtures. Validation entry points
    # always require the immutable anchor, including when discovery is empty.
    if not (root / BASELINE).exists():
        return sorted(p.relative_to(root).as_posix()
                      for directory in (VERSIONS, UPDATES)
                      for p in (root / directory).glob("*") if p.is_file())
    baseline, chain, files = _history(root)
    paths = {BASELINE, baseline["historical_workbook"]["path"]}
    paths.update(ref["path"] for ref in baseline["immutable_evidence"])
    paths.update(path.relative_to(root).as_posix() for path in files)
    for document in chain:
        paths.update(f"{VERSIONS}/{document[key]}.xlsx" for key in ("old_workbook_sha256", "new_workbook_sha256"))
        paths.update(_evidence_paths(root, [ref for change in document["changes"]
                                           for ref in change["evidence"]]))
    return sorted(paths)


def create_update(root: Path, old_path: Path, new_path: Path, evidence: dict,
                  *, editor_identity: str, timestamp: str | None = None,
                  update_id: str | None = None) -> Path:
    """Record candidate bytes exclusively; never edit the live workbook."""
    root, old_path, new_path = Path(root), Path(old_path), Path(new_path)
    mixed = (root / "reports/current-semantic-workbook/transitions").exists()
    if mixed:
        import current_semantic_workbook as semantic
        history = semantic.resolve_history(root, require_live=False)
        baseline, chain = history["baseline"], history["chain"]
    else:
        baseline, chain, _ = _history(root)
    old_hash, new_hash = digest(old_path.read_bytes()), digest(new_path.read_bytes())
    tail = chain[-1]["new_workbook_sha256"] if chain else baseline["historical_workbook"]["sha256"]
    if old_hash != tail:
        raise ValueError("documentary update must extend the existing chain tail")
    if new_hash in {baseline["historical_workbook"]["sha256"], *(d["new_workbook_sha256"] for d in chain)}:
        raise ValueError("documentary update must not cycle to a prior workbook")
    changes = _changes(old_path, new_path)
    keys = {entry["sheet"] + "!" + entry["cell"] for entry in changes}
    if not isinstance(evidence, dict) or set(evidence) != keys:
        raise ValueError("evidence manifest must cover exactly the changed cells")
    for entry in changes:
        refs = evidence[entry["sheet"] + "!" + entry["cell"]]
        _evidence(root, refs)
        entry["evidence"] = refs
    document = {"schema_version": 1, "profile": PROFILE,
                "update_id": _uuid(update_id or str(uuid4())), "workbook_path": WORKBOOK,
                "old_workbook_sha256": old_hash, "new_workbook_sha256": new_hash,
                "old_semantic_projection_sha256": semantic_projection_sha256(old_path),
                "new_semantic_projection_sha256": semantic_projection_sha256(new_path),
                "allowed_column": "coms:Reasoning", "semantic_columns_unchanged": True,
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
                "editor_identity": editor_identity, "changes": changes}
    _timestamp(document["timestamp"])
    if not isinstance(editor_identity, str) or not editor_identity.strip():
        raise ValueError("documentary update requires an editor identity")
    if chain and _timestamp(document["timestamp"]) < _timestamp(chain[-1]["timestamp"]):
        raise ValueError("documentary update timestamps are out of order")
    destination = _local_path(root, UPDATES + "/" + document["update_id"] + ".json")
    if destination.exists():
        raise ValueError("documentary update ID already exists")
    snapshots = [(source, sha256, _local_path(root, VERSIONS + "/" + sha256 + ".xlsx"))
                 for source, sha256 in ((old_path, old_hash), (new_path, new_hash))]
    for _, sha256, snapshot in snapshots:
        if snapshot.exists():
            _snapshot(root, sha256)
    created = []
    try:
        for source, _, snapshot in snapshots:
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            if not snapshot.exists():
                with snapshot.open("xb") as stream:
                    created.append(snapshot)
                    stream.write(source.read_bytes())
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            created.append(destination)
            stream.write(canonical_bytes(document))
        if mixed:
            semantic.resolve_history(root, require_live=False)
        else:
            _history(root)
    except Exception:
        for path in reversed(created):
            path.unlink()
        raise
    return destination


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    projection = commands.add_parser("projection")
    projection.add_argument("--workbook", type=Path)
    check = commands.add_parser("check")
    check.add_argument("--historical-sha256")
    record = commands.add_parser("record")
    record.add_argument("--old", type=Path, required=True)
    record.add_argument("--new", type=Path, required=True)
    record.add_argument("--evidence-manifest", type=Path, required=True)
    record.add_argument("--editor", required=True)
    record.add_argument("--timestamp")
    record.add_argument("--update-id")
    args = parser.parse_args(argv)
    try:
        if args.command == "projection":
            path = args.workbook or args.root / WORKBOOK
            result = {"profile": PROFILE, "workbook_sha256": digest(path.read_bytes()),
                      "semantic_projection_sha256": semantic_projection_sha256(path)}
        elif args.command == "check":
            baseline = _baseline(args.root)
            path = validate_workbook_evolution(args.root, args.historical_sha256 or baseline["historical_workbook"]["sha256"])
            result = {"status": "PASS", "historical_workbook": path.relative_to(args.root).as_posix(),
                      "semantic_projection_sha256": semantic_projection_sha256(path)}
        else:
            path = create_update(args.root, args.old, args.new, _json(args.evidence_manifest),
                                 editor_identity=args.editor, timestamp=args.timestamp, update_id=args.update_id)
            result = {"status": "RECORDED", "path": path.relative_to(args.root).as_posix(),
                      "live_workbook_modified": False}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
