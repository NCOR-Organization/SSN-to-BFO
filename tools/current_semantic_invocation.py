"""Create-once invocation custody for the current SSN/SOSA Java reasoner.

The ticket exists before Java starts. This module, which launches Java, checks
the planned slot and exact input bytes and writes the captured bytes and result
envelope itself. Local files are not signatures or protection from an actor who
can rewrite the entire checkout; they prevent post-hoc rebinding while the
ticket and envelope remain intact.
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import uuid


SCHEMA = "current-ssn-sosa-invocation-v1"
BEGIN = "BEGIN CURRENT SEMANTIC INVOCATION"
END = "END CURRENT SEMANTIC INVOCATION"


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sealed(value: dict, field: str) -> dict:
    record = dict(value)
    record[field] = digest(canonical_bytes(value))
    return record


def verify_seal(value: dict, field: str) -> None:
    payload = dict(value)
    recorded = payload.pop(field, None)
    if not isinstance(recorded, str) or recorded != digest(canonical_bytes(payload)):
        raise ValueError("Invocation " + field + " is missing or differs from canonical content")


def create_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def invocation_paths(ticket_path: Path) -> dict[str, Path]:
    prefix = ticket_path.with_suffix("").with_suffix("")
    return {kind: prefix.with_name(prefix.name + suffix) for kind, suffix in {
        "ticket": ".ticket.json", "stdout": ".stdout.log", "stderr": ".stderr.log",
        "capture": ".capture.json", "envelope": ".envelope.json"}.items()}


def create_ticket(*, root: Path, evidence: Path, slot: str, identity: dict, closure: dict,
                  graph_path: Path, query_path: Path | None, command: list[str]) -> Path:
    """Record a planned invocation before the helper is allowed to start Java."""
    invocation_id = str(uuid.uuid4())
    path = evidence / "invocations" / (invocation_id + ".ticket.json")
    graph_bytes = graph_path.read_bytes()
    query_bytes = query_path.read_bytes() if query_path is not None else None
    helper_path = Path(__file__).resolve()
    ticket = sealed({
        "schema": SCHEMA, "invocation_id": invocation_id,
        "nonce": secrets.token_hex(32), "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "slot": slot, "execution_identity": identity, "closure": closure,
        "graph": {"path": str(graph_path.absolute()), "sha256": digest(graph_bytes), "bytes": len(graph_bytes)},
        "query": None if query_path is None else {"path": str(query_path.absolute()),
            "sha256": digest(query_bytes), "bytes": len(query_bytes)},
        "command": command,
        "helper": {"path": str(helper_path), "sha256": digest(helper_path.read_bytes())},
        "governed_inputs": identity["governed_inputs"],
    }, "ticket_sha256")
    create_once(path, canonical_bytes(ticket))
    return path


def read_ticket(path: Path) -> dict:
    ticket = json.loads(path.read_bytes())
    if not isinstance(ticket, dict):
        raise ValueError("Invocation ticket is not an object")
    verify_seal(ticket, "ticket_sha256")
    if ticket.get("schema") != SCHEMA or not isinstance(ticket.get("nonce"), str) or len(ticket["nonce"]) != 64:
        raise ValueError("Invocation ticket schema or nonce invalid")
    return ticket


def verify_ticket_for_execution(ticket: dict, root: Path) -> tuple[Path, Path | None]:
    """Independently reconstruct the slot; never accept a report's chosen plan."""
    # Import here to keep the wrapper usable as a small standalone custody layer.
    import current_semantic_validation as validation

    slot = ticket["slot"]
    diagnostic = slot.startswith("diagnostic/")
    if not diagnostic:
        plan = validation.expected_execution_plan(root, only_slot=slot)
        if slot not in plan or ticket["execution_identity"] != plan[slot]["identity"]:
            raise ValueError("Invocation ticket differs from required execution slot")
        if ticket["closure"] != plan[slot]["closure"] or ticket["governed_inputs"] != plan[slot]["identity"]["governed_inputs"]:
            raise ValueError("Invocation ticket closure differs from required execution slot")
        identity = plan[slot]["identity"]
    else:
        identity = ticket["execution_identity"]
        if identity.get("id") != slot.removeprefix("diagnostic/") or identity.get("governed_inputs") != ticket["governed_inputs"]:
            raise ValueError("Diagnostic invocation identity differs from ticket")
    graph = Path(ticket["graph"]["path"])
    query = Path(ticket["query"]["path"]) if ticket.get("query") else None
    if not graph.is_file() or digest(graph.read_bytes()) != ticket["graph"]["sha256"] or graph.stat().st_size != ticket["graph"]["bytes"]:
        raise ValueError("Invocation graph bytes differ from pre-execution ticket")
    if query is not None and (not query.is_file() or digest(query.read_bytes()) != ticket["query"]["sha256"]
                              or query.stat().st_size != ticket["query"]["bytes"]):
        raise ValueError("Invocation query bytes differ from pre-execution ticket")
    if digest(Path(__file__).resolve().read_bytes()) != ticket["helper"]["sha256"]:
        raise ValueError("Invocation wrapper identity changed")
    if ticket["helper"]["path"] != str(Path(__file__).resolve()):
        raise ValueError("Invocation wrapper path changed")
    arguments = ticket["command"]
    if (len(arguments) != (8 if query is not None else 7) or
            arguments[1:3] != ["-Xmx4G", "-cp"] or arguments[4] != "CurrentSemanticReasoner"):
        raise ValueError("Invocation command is not the planned Java reasoner launch")
    graph_arg = arguments[-3] if query is not None else arguments[-2]
    mode_arg = arguments[-2] if query is not None else arguments[-1]
    query_arg = arguments[-1] if query is not None else None
    if (Path(graph_arg).absolute() != graph or mode_arg != identity["command_identity"]["mode"] or
            (query is not None and Path(query_arg).absolute() != query)):
        raise ValueError("Invocation command does not consume ticketed graph/query")
    if diagnostic:
        from rdflib import Graph
        if validation.graph_identity(Graph().parse(graph, format="xml")) != identity["graph_identity"]:
            raise ValueError("Diagnostic invocation graph differs from ticket")
    else:
        raw = {"id": identity["id"], "closure": ticket["closure"],
               "execution_identity": ticket["execution_identity"],
               "input_document": validation.fingerprint(graph, root),
               "query_document": validation.fingerprint(query, root) if query else None,
               "attempt": {"command": ticket["command"]}}
        build = graph.parent
        validation.validate_execution_slot(raw, plan[slot], {"toolchain": {"status": "ready", "class_directory": str(build)}}, root)
    return graph, query


def execute_ticket(ticket_path: Path, *, root: Path, timeout: int = 120) -> dict:
    """Only this wrapper launches the reasoner and produces its result envelope."""
    ticket = read_ticket(ticket_path)
    paths = invocation_paths(ticket_path)
    if paths["ticket"] != ticket_path:
        raise ValueError("Invocation ticket filename does not match custody paths")
    if any(paths[kind].exists() for kind in ("stdout", "stderr", "capture", "envelope")):
        raise FileExistsError("Invocation result already exists; reexecution needs a new ticket")
    graph, query = verify_ticket_for_execution(ticket, root)
    start = time.monotonic()
    status = "completed"
    try:
        process = subprocess.run(ticket["command"], cwd=root, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout, check=False)
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as error:
        status, code = "timeout", None
        stdout = error.stdout or b""
        stderr = (error.stderr or b"") + ("\nTimed out after %d seconds." % timeout).encode()
    except OSError as error:
        status, code, stdout, stderr = "launch_failure", None, b"", str(error).encode()
    elapsed = round(time.monotonic() - start, 3)
    capture = sealed({
        "schema": SCHEMA, "begin": BEGIN, "end": END,
        "invocation_id": ticket["invocation_id"], "nonce": ticket["nonce"],
        "ticket_sha256": ticket["ticket_sha256"], "slot": ticket["slot"],
        "returncode": code, "execution_status": status,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
    }, "capture_sha256")
    capture_bytes = canonical_bytes(capture)
    envelope = sealed({
        "schema": SCHEMA, "invocation_id": ticket["invocation_id"], "nonce": ticket["nonce"],
        "ticket_sha256": ticket["ticket_sha256"], "slot": ticket["slot"],
        "execution_identity": ticket["execution_identity"],
        "graph_sha256": digest(graph.read_bytes()),
        "query_sha256": digest(query.read_bytes()) if query else None,
        "command": ticket["command"], "command_sha256": digest(canonical_bytes({"command": ticket["command"]})),
        "helper": ticket["helper"], "returncode": code, "execution_status": status,
        "stdout_sha256": digest(stdout), "stderr_sha256": digest(stderr),
        "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
        "capture_sha256": digest(capture_bytes), "elapsed_seconds": elapsed,
    }, "envelope_sha256")
    create_once(paths["stdout"], stdout)
    create_once(paths["stderr"], stderr)
    create_once(paths["capture"], capture_bytes)
    create_once(paths["envelope"], canonical_bytes(envelope))
    return {"ticket": ticket, "capture": capture, "envelope": envelope, "paths": paths}


def verify_result(ticket_path: Path, *, root: Path, expected_slot: str,
                  expected_invocation_id: str) -> dict:
    """Verify unchanged ticket/envelope against exact retained captured bytes."""
    ticket = read_ticket(ticket_path)
    paths = invocation_paths(ticket_path)
    if ticket["slot"] != expected_slot or ticket["invocation_id"] != expected_invocation_id or (
            paths["ticket"].name != expected_invocation_id + ".ticket.json"):
        raise ValueError("Invocation ticket differs from selected execution")
    graph, query = verify_ticket_for_execution(ticket, root)
    capture = json.loads(paths["capture"].read_bytes())
    envelope = json.loads(paths["envelope"].read_bytes())
    verify_seal(capture, "capture_sha256")
    verify_seal(envelope, "envelope_sha256")
    if capture.get("schema") != SCHEMA or envelope.get("schema") != SCHEMA:
        raise ValueError("Invocation capture or result envelope schema invalid")
    if envelope["capture_sha256"] != digest(paths["capture"].read_bytes()):
        raise ValueError("Invocation captured result differs from helper envelope")
    common = ("invocation_id", "nonce", "ticket_sha256", "slot")
    if any(capture.get(key) != ticket[key] or envelope.get(key) != ticket[key] for key in common):
        raise ValueError("Invocation challenge or slot differs across ticket, capture, and envelope")
    if capture.get("begin") != BEGIN or capture.get("end") != END:
        raise ValueError("Invocation capture markers invalid")
    if envelope.get("execution_identity") != ticket["execution_identity"] or envelope.get("command") != ticket["command"] or (
            envelope.get("helper") != ticket["helper"] or
            envelope.get("command_sha256") != digest(canonical_bytes({"command": ticket["command"]}))):
        raise ValueError("Invocation execution identity differs from ticket")
    if envelope.get("graph_sha256") != digest(graph.read_bytes()) or envelope.get("query_sha256") != (
            digest(query.read_bytes()) if query else None):
        raise ValueError("Invocation consumed input digest differs from ticket")
    if any(capture.get(key) != envelope.get(key) for key in ("returncode", "execution_status")):
        raise ValueError("Invocation exit state differs from capture")
    outputs = {}
    for channel in ("stdout", "stderr"):
        raw = base64.b64decode(capture[channel + "_base64"], validate=True)
        if raw != paths[channel].read_bytes() or digest(raw) != envelope[channel + "_sha256"] or len(raw) != envelope[channel + "_bytes"]:
            raise ValueError("Invocation " + channel + " differs from captured execution")
        outputs[channel] = raw
    return {"ticket": ticket, "capture": capture, "envelope": envelope, "paths": paths, **outputs}
