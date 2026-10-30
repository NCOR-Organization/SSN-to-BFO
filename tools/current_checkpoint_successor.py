#!/usr/bin/env python3
"""Explicit, two-phase acceptance of a validated current-track checkpoint.

Prepare while HEAD is already accepted, after the normal required executions.
Commit the prepared record with exactly its inventoried candidate files. Bind
only the actual resulting commit SHA afterwards. A binding may be distributed
alongside that commit, or committed in one strictly receipt-only child commit.
Neither preparation nor binding stages files, creates commits, or grants
publication readiness. Historical execution HEADs and receipts are unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from uuid import uuid4

import current_documentary_workbook as documentary

DIRECTORY = "reports/current-checkpoint-successors"
PREPARED = DIRECTORY + "/prepared"
BINDINGS = DIRECTORY + "/bindings"
PROFILE = "current-ssn-sosa-checkpoint-successor-v1"


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode().strip()


def _commit(root: Path, value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("checkpoint requires an actual full Git commit SHA")
    if _git(root, "rev-parse", "--verify", value + "^{commit}") != value:
        raise ValueError("checkpoint commit identity does not resolve exactly")
    return value


def _bytes(root: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{path}"], stderr=subprocess.PIPE)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate checkpoint record key")
            result[key] = value
        return result
    result = json.loads(data, object_pairs_hook=unique)
    if not isinstance(result, dict) or documentary.canonical_bytes(result) != data:
        raise ValueError("checkpoint record must be canonical JSON")
    return result


def _ref(root: Path, path: str) -> dict:
    actual = documentary._path(root, path)
    return {"path": path, "sha256": _hash(actual.read_bytes())}


def _live_inventory(root: Path, paths) -> dict:
    result = {}
    for path in sorted(set(paths)):
        actual = documentary._path(root, path)
        result[path] = {"sha256": _hash(actual.read_bytes()),
                        "mode": "100755" if actual.stat().st_mode & 0o111 else "100644"}
    return result


def _tree(root: Path, commit: str) -> dict:
    listing = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "-z", commit])
    result = {}
    for entry in filter(None, listing.split(b"\0")):
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        path = raw_path.decode()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("checkpoint tree contains a non-regular file: " + path)
        data = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", blob])
        result[path] = {"sha256": _hash(data), "mode": mode}
    return result


def _authenticated_authorities(root: Path) -> tuple[dict, set[str]]:
    """Reapply existing semantic/product/assessment authorities, without HEAD recursion."""
    import current_source_identity as identity
    import current_semantic_workbook as semantic
    import current_publication_preservation as preservation
    import current_decision_applicability as applicability
    from current_custody_dependencies import authority_paths

    trusted = _bytes(root, identity.ACCEPTED_CHECKPOINT_HEAD, identity.RECORD.as_posix())
    if (root / identity.RECORD).read_bytes() != trusted:
        raise ValueError("checkpoint identity authority differs from accepted historical Git bytes")
    document = json.loads(trusted)
    paths = {identity.RECORD.as_posix(), identity.WORKBOOK, *identity.PRODUCTS,
             "mappings/current-ssn-sosa-assessment.json"}
    for group in ("source_files", "target_files", "scope_and_configuration"):
        for record in document[group]:
            actual = documentary._path(root, record["path"])
            if identity.fingerprint(actual) != {key: record[key] for key in ("sha256", "bytes")}:
                raise ValueError("checkpoint changes a non-evolvable governed input: " + record["path"])
            paths.add(record["path"])
    history = semantic.resolve_history(root)
    if not any(edge["kind"] == "semantic" for edge in history["chain"]):
        raise ValueError("checkpoint successor requires authenticated semantic evolution")
    products = identity.validated_product_evolution(root, {r["path"]: r for r in document["products"]})
    assessment_path = "mappings/current-ssn-sosa-assessment.json"
    previous = json.loads(_bytes(root, identity.ACCEPTED_CHECKPOINT_HEAD, assessment_path))
    assessment = json.loads((root / assessment_path).read_text())
    preservation.validated_assessment_evolution(root, previous, assessment)
    preservation._authenticate_current_assessment(root, assessment)
    paths.update(semantic.evidence_paths(root))
    paths.update(applicability.evidence_paths(root))
    paths.update(authority_paths(root, publication=True))
    state = {"workbook_sha256": _hash((root / identity.WORKBOOK).read_bytes()),
             "semantic_projection_sha256": documentary.semantic_projection_sha256(root / identity.WORKBOOK),
             "assessment_sha256": _hash((root / assessment_path).read_bytes()),
             "products": products["products"], "history": history["record_bindings"],
             "history_tail_sha256": history["tail_sha256"]}
    return state, paths


def _authenticated_state(root: Path) -> tuple[dict, set[str]]:
    """Checkpoint preparation consumes the selected evidence after execution."""
    import current_publication_readiness as readiness
    state, paths = _authenticated_authorities(root)
    semantic_path, _, selection = readiness.selected_evidence(root)
    paths.add(semantic_path.relative_to(root).as_posix())
    if selection.get("selector"):
        paths.add(selection["selector"]["path"])
    if selection.get("portable_semantic_custody"):
        manifest = selection["portable_semantic_custody"]["path"]
        paths.add(manifest)
        # The authenticated manifest supplies the exact retained output closure.
        document = json.loads((root / manifest).read_text())
        for item in document["documents"]:
            paths.add(item["retained_path"])
    state.update(selected_evidence=selection,
                 semantic_report=_ref(root, semantic_path.relative_to(root).as_posix()))
    return state, paths


def _validation(root: Path, path: str, execution_head: str) -> tuple[dict, set[str]]:
    """Require the existing complete command policy, never a claimed PASS flag."""
    import current_publication_readiness as readiness
    ledger = json.loads(documentary._path(root, path).read_text())
    errors = readiness.validation_errors(ledger, root, execution_head)
    if errors:
        raise ValueError("checkpoint validation failed: " + " | ".join(errors))
    inputs = readiness.scopes.ledger_inputs(root)
    paths = {path, *inputs}
    for command in ledger["commands"]:
        paths.update(command["result_artifacts"])
    return {"ledger": _ref(root, path), "execution_head": execution_head,
            "input_sha256": inputs, "required_commands": readiness.REQUIRED_COMMANDS}, paths


def _validate_prepared(document: dict) -> None:
    fields = {"schema_version", "profile", "prepared_id", "status", "predecessor_checkpoint",
              "authorization", "reviewer_identity", "timestamp", "state", "validation", "candidate_files"}
    if set(document) != fields or type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("invalid prepared checkpoint fields")
    if document["profile"] != PROFILE or document["status"] != "PREPARED_NOT_COMMITTED":
        raise ValueError("invalid prepared checkpoint scope")
    documentary._uuid(document["prepared_id"])
    documentary._timestamp(document["timestamp"])
    if not isinstance(document["reviewer_identity"], str) or not document["reviewer_identity"].strip():
        raise ValueError("checkpoint preparation requires reviewer identity")
    if not isinstance(document["candidate_files"], dict) or not document["candidate_files"]:
        raise ValueError("checkpoint candidate inventory is empty")


def prepare_successor(root: Path, validation_path: str, authorization: dict, *,
                      reviewer_identity: str, include_paths=(), prepared_id: str | None = None,
                      timestamp: str | None = None) -> Path:
    """Record exact validated bytes; never predict a commit SHA or install files."""
    import current_source_identity as identity
    root = Path(root).resolve()
    predecessor = _git(root, "rev-parse", "HEAD")
    if predecessor in {identity.IDENTITY_BASELINE_HEAD, identity.ACCEPTED_CHECKPOINT_HEAD}:
        errors = identity.checkpoint_errors(root)
        if errors:
            raise ValueError("checkpoint predecessor is not accepted: " + " | ".join(errors))
    else:
        # Authenticate the committed predecessor independently of the pending
        # successor's live bytes. Those bytes are reauthenticated below; they
        # cannot retrospectively change the predecessor's committed inventory.
        _accepted_link(root, predecessor, set())
    documentary._bound_file(root, authorization)
    state, paths = _authenticated_state(root)
    validation, evidence = _validation(root, validation_path, predecessor)
    paths.update(evidence)
    paths.add(authorization["path"])
    paths.update(include_paths)
    paths.update(filter(None, _git(root, "ls-files", "-z").split("\0")))
    ident = prepared_id or str(uuid4())
    relative = f"{PREPARED}/{ident}.json"
    paths.discard(relative)
    document = {"schema_version": 1, "profile": PROFILE, "prepared_id": ident,
                "status": "PREPARED_NOT_COMMITTED", "predecessor_checkpoint": predecessor,
                "authorization": authorization, "reviewer_identity": reviewer_identity,
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
                "state": state, "validation": validation,
                "candidate_files": _live_inventory(root, paths)}
    _validate_prepared(document)
    if _git(root, "rev-parse", "HEAD") != predecessor or _authenticated_state(root)[0] != state:
        raise ValueError("checkpoint state changed during preparation")
    if _validation(root, validation_path, predecessor)[0] != validation:
        raise ValueError("checkpoint validation changed during preparation")
    if _live_inventory(root, document["candidate_files"]) != document["candidate_files"]:
        raise ValueError("checkpoint candidate files changed during preparation")
    destination = documentary._local_path(root, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(documentary.canonical_bytes(document))
    return destination


def _bound_preparation(root: Path, binding: dict) -> tuple[dict, dict]:
    fields = {"schema_version", "profile", "status", "prepared_record", "predecessor_checkpoint",
              "successor_commit", "successor_tree"}
    if (set(binding) != fields or type(binding["schema_version"]) is not int
            or binding["schema_version"] != 1 or binding["profile"] != PROFILE
            or binding["status"] != "BOUND_TO_COMMITTED_SUCCESSOR"):
        raise ValueError("invalid committed checkpoint binding")
    successor = _commit(root, binding["successor_commit"])
    predecessor = _commit(root, binding["predecessor_checkpoint"])
    if successor == predecessor or subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", predecessor, successor],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode:
        raise ValueError("checkpoint successor does not descend from its exact predecessor")
    ref = binding["prepared_record"]
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise ValueError("checkpoint preparation binding is missing")
    path = ref["path"]
    documentary._local_path(root, path)
    raw = _bytes(root, successor, path)
    if _hash(raw) != ref["sha256"]:
        raise ValueError("committed checkpoint preparation hash mismatch")
    prepared = _json(raw)
    _validate_prepared(prepared)
    if path != f"{PREPARED}/{prepared['prepared_id']}.json":
        raise ValueError("checkpoint prepared path/ID mismatch")
    if prepared["predecessor_checkpoint"] != predecessor:
        raise ValueError("checkpoint predecessor differs from prepared authorization")
    if _git(root, "rev-parse", successor + "^{tree}") != binding["successor_tree"]:
        raise ValueError("checkpoint committed tree identity mismatch")
    tree = _tree(root, successor)
    if tree.pop(path, None) != {"sha256": ref["sha256"], "mode": "100644"} or tree != prepared["candidate_files"]:
        raise ValueError("checkpoint commit differs from exact prepared candidate inventory")
    authorization = prepared["authorization"]
    if tree.get(authorization.get("path"), {}).get("sha256") != authorization.get("sha256"):
        raise ValueError("checkpoint human authorization differs from committed bytes")
    validation = prepared["validation"]
    if validation.get("execution_head") != predecessor:
        raise ValueError("checkpoint validation execution did not use its predecessor")
    ref = validation.get("ledger", {})
    if tree.get(ref.get("path"), {}).get("sha256") != ref.get("sha256"):
        raise ValueError("checkpoint validation ledger differs from committed bytes")
    for path, digest in validation.get("input_sha256", {}).items():
        if tree.get(path, {}).get("sha256") != digest:
            raise ValueError("checkpoint validated input differs from committed candidate: " + path)
    return prepared, tree


def bind_successor(root: Path, prepared_path: str, successor_commit: str) -> Path:
    """Bind a prepared record to an existing exact commit, without committing."""
    root = Path(root).resolve()
    successor = _commit(root, successor_commit)
    prepared_bytes = _bytes(root, successor, prepared_path)
    prepared = _json(prepared_bytes)
    binding = {"schema_version": 1, "profile": PROFILE,
               "status": "BOUND_TO_COMMITTED_SUCCESSOR",
               "prepared_record": {"path": prepared_path, "sha256": _hash(prepared_bytes)},
               "predecessor_checkpoint": prepared["predecessor_checkpoint"],
               "successor_commit": successor,
               "successor_tree": _git(root, "rev-parse", successor + "^{tree}")}
    _bound_preparation(root, binding)
    _accepted_link(root, prepared["predecessor_checkpoint"], set())
    if _git(root, "rev-parse", "HEAD") != successor:
        raise ValueError("finalize the actual checked-out content commit, not another revision")
    _check_live(root, prepared)
    destination = documentary._local_path(root, f"{BINDINGS}/{successor}.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(documentary.canonical_bytes(binding))
    return destination


def _accepted_link(root: Path, head: str, seen: set[str]) -> dict | None:
    import current_source_identity as identity
    if head in {identity.IDENTITY_BASELINE_HEAD, identity.ACCEPTED_CHECKPOINT_HEAD}:
        return None
    if head in seen:
        raise ValueError("cyclic checkpoint successor chain")
    seen.add(head)
    directory = documentary._local_path(root, BINDINGS)
    candidates = []
    for path in sorted(directory.glob("*.json")):
        binding = _json(documentary._path(root, path.relative_to(root).as_posix()).read_bytes())
        if path.name != binding.get("successor_commit", "") + ".json":
            raise ValueError("checkpoint binding filename/commit mismatch")
        target = binding.get("successor_commit")
        if target == head:
            candidates.append((binding, None))
            continue
        parents = _git(root, "rev-list", "--parents", "-n", "1", head).split()[1:]
        if parents == [target]:
            # A receipt cannot name the SHA of the commit that contains itself.
            # Permit only this one exact receipt-only carrier, never descendants.
            relative = path.relative_to(root).as_posix()
            before, after = _tree(root, target), _tree(root, head)
            expected = {**before, relative: {"sha256": _hash(path.read_bytes()), "mode": "100644"}}
            if relative not in before and after == expected:
                candidates.append((binding, head))
    if len(candidates) != 1:
        raise ValueError("HEAD lacks one authenticated checkpoint successor binding")
    binding, carrier = candidates[0]
    prepared, _ = _bound_preparation(root, binding)
    _accepted_link(root, prepared["predecessor_checkpoint"], seen)
    return {"prepared": prepared, "binding": binding, "receipt_carrier": carrier}


def _check_live(root: Path, prepared: dict) -> None:
    path = f"{PREPARED}/{prepared['prepared_id']}.json"
    if documentary._path(root, path).read_bytes() != documentary.canonical_bytes(prepared):
        raise ValueError("live checkpoint preparation differs from committed authorization")
    if _live_inventory(root, prepared["candidate_files"]) != prepared["candidate_files"]:
        raise ValueError("live checkpoint bytes differ from prepared candidate")
    if _authenticated_state(root)[0] != prepared["state"]:
        raise ValueError("checkpoint semantic/product/history identity differs from authorization")
    validation = prepared["validation"]
    if _validation(root, validation["ledger"]["path"], validation["execution_head"])[0] != validation:
        raise ValueError("checkpoint validation differs from prepared evidence")


def validate_successor(root: Path, head: str | None = None) -> dict:
    root = Path(root).resolve()
    actual = _git(root, "rev-parse", "HEAD")
    if head is not None and actual != head:
        raise ValueError("checkpoint validation HEAD does not match checkout")
    accepted = _accepted_link(root, actual, set())
    if accepted is None:
        raise ValueError("historical checkpoint does not need a successor binding")
    _check_live(root, accepted["prepared"])
    return {"status": "VALIDATED", "head": actual,
            "successor_commit": accepted["binding"]["successor_commit"],
            "predecessor_checkpoint": accepted["prepared"]["predecessor_checkpoint"],
            "receipt_carrier": accepted["receipt_carrier"], "publication_readiness_granted": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--validation", required=True, help="Fresh complete canonical command ledger")
    prepare.add_argument("--authorization", required=True, help="Project-local explicit human authorization")
    prepare.add_argument("--reviewer", required=True)
    prepare.add_argument("--include", action="append", default=[], help="Additional exact file intended for the content commit")
    bind = commands.add_parser("bind")
    bind.add_argument("--prepared", required=True)
    bind.add_argument("--commit", required=True, help="Actual committed full SHA, never a prediction")
    commands.add_parser("check")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare_successor(args.root, args.validation, _ref(args.root, args.authorization),
                                       reviewer_identity=args.reviewer, include_paths=args.include)
        elif args.command == "bind":
            result = bind_successor(args.root, args.prepared, args.commit)
        else:
            result = validate_successor(args.root)
        print(json.dumps(result if isinstance(result, dict) else {"record": str(result)}, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print("Checkpoint successor: FAIL (" + str(exc) + ")")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
