"""Resolve historical path/hash bindings without replacing current outputs.

The binding's expected hash remains its authority. A retained manifest only
locates those exact bytes and records how they were recovered. Portable copies
can authenticate the bytes and Git blob identity without a local Git database;
when one is present, the recorded commit/path binding is checked as well.
"""
from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess


STORE = "reports/retained-evidence"
EXECUTION_OBJECTS = STORE + "/execution/sha256"
PROFILE = "current-ssn-sosa-retained-evidence-v1"
CLASSIFICATION = "immutable retained historical evidence"
FIELDS = {"schema_version", "profile", "logical_path", "snapshot_path", "sha256",
          "bytes", "source_git_commit", "source_git_blob", "reason", "creation_date",
          "custody_classification"}


def _sha(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("invalid retained-evidence SHA-256")
    return value


def _local(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or "\0" in relative:
        raise ValueError("invalid retained-evidence project path")
    rel = Path(relative)
    path = root / rel
    if (rel.is_absolute() or ".." in rel.parts or rel.as_posix() != relative
            or relative == "." or not path.resolve().is_relative_to(root.resolve())
            or any((root / Path(*rel.parts[:n])).is_symlink()
                   for n in range(1, len(rel.parts) + 1))):
        raise ValueError(f"non-project or noncanonical retained-evidence path: {relative}")
    return path


def _canonical(document: dict) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _json(data: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate retained-evidence JSON key: {key}")
            result[key] = value
        return result
    try:
        document = json.loads(data.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid retained-evidence manifest JSON") from exc
    if not isinstance(document, dict) or data != _canonical(document):
        raise ValueError("retained-evidence manifest is not canonical JSON")
    return document


def _object_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        raise ValueError("retained-evidence Git identity must be a full object ID")
    return value


def _creation_date(value: str) -> None:
    if not isinstance(value, str):
        raise ValueError("invalid retained-evidence creation date")
    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            date.fromisoformat(value)
        else:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if "T" not in value or parsed.tzinfo is None:
                raise ValueError("creation timestamp requires a timezone")
    except ValueError as exc:
        raise ValueError("invalid retained-evidence creation date") from exc


def _locations(logical_path: str, expected_sha256: str) -> tuple[str, str]:
    key = hashlib.sha256(logical_path.encode("utf-8")).hexdigest()
    return (f"{STORE}/manifests/{key}/{expected_sha256}.json",
            f"{STORE}/sha256/{expected_sha256}/{Path(logical_path).name}")


def _blob_id(data: bytes, identity_length: int) -> str:
    payload = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return (hashlib.sha1(payload) if identity_length == 40 else hashlib.sha256(payload)).hexdigest()


def _git_source(root: Path, logical_path: str, commit: str) -> tuple[str, bytes]:
    _object_id(commit)
    try:
        actual = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--verify", commit + "^{commit}"],
            stderr=subprocess.PIPE).decode().strip()
        if actual != commit:
            raise ValueError("retained-evidence source is not the exact recorded commit")
        listing = subprocess.check_output(
            ["git", "-C", str(root), "ls-tree", "-z", commit, "--", logical_path],
            stderr=subprocess.PIPE)
        entries = [entry for entry in listing.split(b"\0") if entry]
        if len(entries) != 1:
            raise ValueError("retained-evidence source Git path is missing or ambiguous")
        metadata, path = entries[0].split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        if path.decode("utf-8") != logical_path or mode not in {"100644", "100755"} or kind != "blob":
            raise ValueError("retained-evidence source must be an exact regular Git file")
        _object_id(blob)
        data = subprocess.check_output(
            ["git", "-C", str(root), "cat-file", "blob", blob], stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError) as exc:
        raise ValueError("retained-evidence source Git provenance cannot be verified") from exc
    if len(commit) != len(blob) or _blob_id(data, len(blob)) != blob:
        raise ValueError("retained-evidence source Git blob identity mismatch")
    return blob, data


def _snapshot(root: Path, logical_path: str, expected_sha256: str) -> tuple[Path, Path]:
    manifest_relative, expected_snapshot = _locations(logical_path, expected_sha256)
    manifest_path = _local(root, manifest_relative)
    if not manifest_path.is_file():
        raise ValueError(f"missing retained evidence snapshot manifest: {logical_path}")
    document = _json(manifest_path.read_bytes())
    if (set(document) != FIELDS or type(document["schema_version"]) is not int
            or document["schema_version"] != 1 or document["profile"] != PROFILE
            or document["logical_path"] != logical_path or document["sha256"] != expected_sha256
            or document["snapshot_path"] != expected_snapshot
            or document["custody_classification"] != CLASSIFICATION
            or type(document["bytes"]) is not int or document["bytes"] < 0
            or not isinstance(document["reason"], str) or not document["reason"].strip()):
        raise ValueError("retained-evidence manifest binding or metadata mismatch")
    _creation_date(document["creation_date"])
    commit, blob = (_object_id(document[key]) for key in ("source_git_commit", "source_git_blob"))
    if len(commit) != len(blob):
        raise ValueError("retained-evidence Git object formats differ")
    snapshot = _local(root, document["snapshot_path"])
    if not snapshot.is_file():
        raise ValueError(f"missing retained evidence snapshot: {logical_path}")
    data = snapshot.read_bytes()
    if len(data) != document["bytes"] or hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError(f"retained evidence snapshot hash or size mismatch: {logical_path}")
    if _blob_id(data, len(blob)) != blob:
        raise ValueError("retained-evidence intrinsic Git blob identity mismatch")
    if (root / ".git").exists():
        source_blob, source_bytes = _git_source(root, logical_path, commit)
        if source_blob != blob or source_bytes != data:
            raise ValueError("retained-evidence source commit/path binding mismatch")
    return manifest_path, snapshot


def resolve(root: Path, logical_path: str, expected_sha256: str, *, allow_retained: bool = True) -> Path:
    """Return exact bound bytes, never accept a changed live path as history."""
    root = Path(root)
    expected_sha256 = _sha(expected_sha256)
    live = _local(root, logical_path)
    if live.exists() and not live.is_file():
        raise ValueError(f"retained evidence must be a regular file: {logical_path}")
    live_exists = live.is_file()
    if live_exists and hashlib.sha256(live.read_bytes()).hexdigest() == expected_sha256:
        return live
    failure = ("retained evidence hash mismatch" if live_exists else "missing retained evidence") + f": {logical_path}"
    if not allow_retained:
        raise ValueError(failure)
    try:
        return _snapshot(root, logical_path, expected_sha256)[1]
    except (ValueError, OSError) as exc:
        raise ValueError(f"{failure}; {exc}") from exc


def evidence_paths(root: Path, logical_path: str, expected_sha256: str) -> list[str]:
    """List the live binding and any retained files needed to authenticate it."""
    root = Path(root)
    selected = resolve(root, logical_path, expected_sha256)
    paths = {logical_path}
    if selected != root / logical_path:
        manifest, _ = _locations(logical_path, expected_sha256)
        paths.update((manifest, selected.relative_to(root).as_posix()))
    return sorted(paths)


def store_paths(root: Path) -> list[str]:
    """Discover custody inputs; callers must still authenticate their bindings."""
    root = Path(root)
    store = _local(root, STORE)
    if not store.exists():
        return []
    if not store.is_dir():
        raise ValueError("retained-evidence store must be a directory")
    paths = []
    for path in sorted(store.rglob("*")):
        relative = path.relative_to(root).as_posix()
        _local(root, relative)
        if path.is_file():
            paths.append(relative)
        elif not path.is_dir():
            raise ValueError(f"unsupported retained-evidence store entry: {relative}")
    return paths


def execution_object_path(expected_sha256: str) -> str:
    """A format-neutral immutable object, authenticated by a separate run manifest."""
    return f"{EXECUTION_OBJECTS}/{_sha(expected_sha256)}"


def resolve_execution_object(root: Path, expected_sha256: str, size: int) -> Path:
    """Resolve exact serialized execution bytes without consulting a runtime path."""
    if type(size) is not int or size < 0:
        raise ValueError("invalid retained execution byte size")
    path = _local(Path(root), execution_object_path(expected_sha256))
    if not path.is_file():
        raise ValueError("missing retained execution object: " + expected_sha256)
    data = path.read_bytes()
    if len(data) != size or hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("retained execution object hash or size mismatch")
    return path


def retain_execution_object(root: Path, data: bytes, expected_sha256: str) -> Path:
    """Exclusively retain bytes; metadata/producer authority belongs to the run manifest."""
    if hashlib.sha256(data).hexdigest() != _sha(expected_sha256):
        raise ValueError("execution bytes differ from recorded SHA-256")
    path = _local(Path(root), execution_object_path(expected_sha256))
    if path.exists():
        return resolve_execution_object(root, expected_sha256, len(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    _local(Path(root), path.relative_to(root).as_posix())
    with path.open("xb") as stream:
        stream.write(data)
    return path


def retain_git(root: Path, logical_path: str, expected_sha256: str, source_commit: str, *,
               creation_date: str, reason: str) -> Path:
    """Exclusively retain exact Git bytes; never rewrite a live or retained file."""
    root = Path(root)
    _local(root, logical_path)
    expected_sha256 = _sha(expected_sha256)
    _creation_date(creation_date)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("retained-evidence snapshot requires a reason")
    blob, data = _git_source(root, logical_path, source_commit)
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("historical Git bytes do not match the requested evidence hash")
    manifest_relative, snapshot_relative = _locations(logical_path, expected_sha256)
    manifest, snapshot = (_local(root, value) for value in (manifest_relative, snapshot_relative))
    if manifest.exists():
        raise ValueError("immutable retained-evidence manifest already exists")
    if snapshot.exists() and (not snapshot.is_file() or snapshot.read_bytes() != data):
        raise ValueError("existing immutable retained snapshot differs from exact Git bytes")
    document = {"schema_version": 1, "profile": PROFILE, "logical_path": logical_path,
                "snapshot_path": snapshot_relative, "sha256": expected_sha256, "bytes": len(data),
                "source_git_commit": source_commit, "source_git_blob": blob,
                "reason": reason, "creation_date": creation_date,
                "custody_classification": CLASSIFICATION}
    created = []
    try:
        for target, content in ((snapshot, data), (manifest, _canonical(document))):
            target.parent.mkdir(parents=True, exist_ok=True)
            _local(root, target.relative_to(root).as_posix())
            if target == snapshot and target.exists():
                if not target.is_file() or target.read_bytes() != data:
                    raise ValueError("existing immutable retained snapshot changed during creation")
                continue
            with target.open("xb") as stream:
                created.append(target)
                stream.write(content)
    except BaseException:
        for target in reversed(created):
            target.unlink()
        raise
    return manifest
