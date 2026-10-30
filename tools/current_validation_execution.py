"""Create-once native executions for the existing v2 validation contract.

This recorder executes only the eight code-owned commands. Tickets precede
launch; raw captures and logs preserve actual outcomes. It creates no semantic
approval, environment qualification waiver, selector, or checkpoint authority.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from uuid import uuid4

import current_validation_scope as scopes


NATIVE_PROFILE = "current-validation-execution-v2"
RECORDER = "tools/current_validation_execution.py"
RECORDER_TESTS = "tests/test_current_validation_execution.py"
_LOADED_RECORDER = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
ROOT = Path(__file__).resolve().parents[1]
PARENT = Path("reports/current-publication-validation")
OVERRIDES = {"PYTHONDONTWRITEBYTECODE": "1"}


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def local(root: Path, relative: str, *, required: bool = True) -> Path:
    return scopes._path(Path(root).resolve(), relative, required=required)


def reference(root: Path, path: Path) -> dict:
    relative = path.relative_to(Path(root).resolve()).as_posix()
    data = local(root, relative).read_bytes()
    return {"path": relative, "sha256": digest(data), "bytes": len(data)}


def bound(root: Path, ref: dict) -> Path:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256", "bytes"}:
        raise ValueError("invalid native evidence reference")
    path = local(root, ref["path"])
    if reference(root, path) != ref:
        raise ValueError("native evidence bytes differ: " + ref["path"])
    return path


def write_new(root: Path, path: Path, value: dict | bytes) -> None:
    path = local(root, path.relative_to(Path(root).resolve()).as_posix(), required=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(value if isinstance(value, bytes) else canonical(value))
        stream.flush()
        os.fsync(stream.fileno())


def read_canonical(root: Path, path: Path) -> dict:
    data = local(root, path.relative_to(Path(root).resolve()).as_posix()).read_bytes()
    value = json.loads(data)
    if not isinstance(value, dict) or data != canonical(value):
        raise ValueError("native evidence is not a canonical JSON object")
    return value


def run_directory(root: Path, directory: Path | str) -> Path:
    root = Path(root).resolve()
    directory = Path(directory)
    if directory.is_absolute():
        try:
            directory = directory.relative_to(root)
        except ValueError as exc:
            raise ValueError("native run directory is outside repository") from exc
    if directory.parent != PARENT or not re.fullmatch(r"v2-[A-Za-z0-9][A-Za-z0-9_-]*", directory.name):
        raise ValueError("native run directory must be a new v2-* publication-validation directory")
    return local(root, directory.as_posix(), required=False)


def head(root: Path) -> str:
    return subprocess.check_output(["git", "--no-optional-locks", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def producer_bindings(root: Path) -> dict:
    result = {name: reference(root, local(root, name)) for name in (RECORDER, RECORDER_TESTS)}
    if result[RECORDER]["sha256"] != _LOADED_RECORDER:
        raise ValueError("native recorder disk bytes differ from loaded implementation")
    return result


def command_argv(role: str) -> list[str]:
    if role not in scopes.REQUIRED_COMMANDS:
        raise ValueError("unknown native validation role")
    argv = list(scopes.REQUIRED_COMMANDS[role])
    if argv[0] == "python":
        argv[0] = sys.executable
    return argv


def snapshot(root: Path, role: str) -> dict:
    return {"head": head(root), "input_scope": scopes.scope_declaration(root, role),
            "inputs": scopes.role_inputs(root, role), "execution_tools": scopes.execution_tools(root, role),
            "execution_environment": scopes.execution_environment()}


def _time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("native timestamp lacks timezone")
    return parsed


def _stop(root: Path, directory: Path, role: str, reason: str) -> None:
    path = directory / "STOP.json"
    if path.exists() or path.is_symlink():
        return
    write_new(root, path, {"native_execution_profile": NATIVE_PROFILE, "stopped_at_utc": stamp(),
                           "role": role, "reason": reason, "policy": "No subsequent execution or ledger issuance in this run."})


def _open(root: Path, directory: Path) -> None:
    if (directory / "STOP.json").exists() or (directory / "STOP.json").is_symlink():
        raise ValueError("native run is stopped; preserve STOP and start no later roles")
    if (directory / "commands.json").exists():
        raise ValueError("native run already has an immutable ledger")


def _terminate(child: subprocess.Popen) -> None:
    if child.poll() is not None:
        return
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        child.wait()


def _execute(root: Path, argv: list[str], log: Path, timeout: float | None) -> dict:
    """Stream actual output; preserve negative codes and incomplete states."""
    started, clock = stamp(), time.monotonic()
    child, status, error, returncode = None, "launch_error", None, None
    with log.open("xb") as stream:
        try:
            child = subprocess.Popen(argv, cwd=root, env={**os.environ, **OVERRIDES},
                                     stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            returncode = child.wait(timeout=timeout)
            status = "completed" if returncode >= 0 else "signal_terminated"
        except subprocess.TimeoutExpired:
            status = "timed_out"
            _terminate(child)
            returncode = child.returncode
        except KeyboardInterrupt:
            status = "interrupted"
            if child is not None:
                _terminate(child)
                returncode = child.returncode
        except OSError as exc:
            status, error = "launch_error", f"{type(exc).__name__}: {exc}"
        finally:
            stream.flush()
            os.fsync(stream.fileno())
    return {"started_at_utc": started, "completed_at_utc": stamp(),
            "elapsed_seconds": time.monotonic() - clock, "execution_status": status,
            "returncode": returncode, "pid": child.pid if child else None, "launch_error": error}


def _version_commands(expectations: dict) -> dict[str, list[str]]:
    tools = expectations["unit_tests"]["execution_tools"]
    return {"python": [sys.executable, "--version"], "java": [tools["java"]["path"], "-version"]}


def _qualification(root: Path, measurements: dict) -> dict:
    declared = {}
    for line in local(root, "config/validation-toolchain.env").read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            declared[key] = value
    python_text = bound(root, measurements["python"]["log"]).read_text(errors="replace")
    java_text = bound(root, measurements["java"]["log"]).read_text(errors="replace")
    python = re.search(r"Python (\d+\.\d+)(?:\.\d+)?", python_text)
    java = re.search(r'(?:openjdk|java) version "(\d+)', java_text, re.IGNORECASE)
    measured = {"python_major_minor": python.group(1) if python else None,
                "java_major": java.group(1) if java else None,
                "java_distribution": "temurin" if "temurin" in java_text.lower() else "unconfirmed"}
    matched = (measured["python_major_minor"] == declared.get("VALIDATION_PYTHON_VERSION")
               and measured["java_major"] == declared.get("VALIDATION_JAVA_VERSION")
               and measured["java_distribution"] == declared.get("VALIDATION_JAVA_DISTRIBUTION"))
    return {"declared": declared, "measured": measured, "declared_environment_match": bool(matched),
            "note": "Actual Python and Java version output is retained; mismatch remains an independent readiness requirement."}


def prepare_run(root: Path, directory: Path | str, authorization_path: Path) -> dict:
    root = Path(root).resolve()
    directory = run_directory(root, directory)
    if directory.exists():
        raise ValueError("native run directory already exists; historical evidence is immutable")
    producers = producer_bindings(root)
    expectations = {role: snapshot(root, role) for role in scopes.REQUIRED_COMMANDS}
    if len({item["head"] for item in expectations.values()}) != 1:
        raise ValueError("HEAD changed while preparing native execution inputs")
    authorization = Path(authorization_path).read_bytes()
    if not authorization:
        raise ValueError("native execution authorization is empty")
    directory.mkdir(parents=True, exist_ok=False)
    write_new(root, directory / "authorization.txt", authorization)
    run_id, created = str(uuid4()), stamp()
    # The preparation ticket is create-once and predates even the independent
    # environment measurement children. It is not a validation PASS receipt.
    preparation = {"native_execution_profile": NATIVE_PROFILE, "run_id": run_id, "created_at_utc": created,
                   "root": root.as_posix(), "producers": producers, "expectations": expectations,
                   "authorization": reference(root, directory / "authorization.txt"),
                   "process_environment_overrides": OVERRIDES}
    write_new(root, directory / "preparation.json", preparation)
    measurements = {}
    for name, argv in _version_commands(expectations).items():
        log = directory / ("environment-" + name + ".log")
        result = _execute(root, argv, log, 30)
        result.update({"command": argv, "log": reference(root, log), "preparation": reference(root, directory / "preparation.json")})
        output = directory / ("environment-" + name + ".json")
        write_new(root, output, result)
        measurements[name] = {**result, "record": reference(root, output)}
        if result["execution_status"] != "completed" or result["returncode"] != 0:
            _stop(root, directory, "environment_" + name, "Environment measurement did not complete successfully")
            raise ValueError("native environment measurement failed; stopped")
    final = {role: snapshot(root, role) for role in scopes.REQUIRED_COMMANDS}
    if final != expectations or producer_bindings(root) != producers:
        _stop(root, directory, "prepare", "Inputs or producer changed during preparation")
        raise ValueError("native preparation inputs drifted")
    manifest = {**preparation, "preparation": reference(root, directory / "preparation.json"),
                "measurements": measurements, "environment": _qualification(root, measurements)}
    write_new(root, directory / "run.json", manifest)
    return manifest


def _manifest(root: Path, directory: Path) -> dict:
    manifest = read_canonical(root, directory / "run.json")
    recorded_root = manifest.get("root")
    if (not isinstance(recorded_root, str) or not Path(recorded_root).is_absolute()
            or ".." in Path(recorded_root).parts or Path(recorded_root).as_posix() != recorded_root):
        raise ValueError("native recorded execution root is invalid")
    if (manifest.get("native_execution_profile") != NATIVE_PROFILE
            or set(manifest.get("expectations", {})) != set(scopes.REQUIRED_COMMANDS)
            or manifest.get("producers") != producer_bindings(root)
            or manifest.get("process_environment_overrides") != OVERRIDES):
        raise ValueError("native run identity, roles, producer or environment contract differs")
    bound(root, manifest["authorization"])
    preparation = read_canonical(root, bound(root, manifest["preparation"]))
    if preparation != {key: value for key, value in manifest.items() if key not in {"preparation", "measurements", "environment"}}:
        raise ValueError("native prepared expectations differ from run manifest")
    expected_commands = _version_commands(manifest["expectations"])
    if set(manifest["measurements"]) != set(expected_commands):
        raise ValueError("native environment measurement membership differs")
    for name, measurement in manifest["measurements"].items():
        record = read_canonical(root, bound(root, measurement["record"]))
        if record != {key: value for key, value in measurement.items() if key != "record"}:
            raise ValueError("native environment measurement inline identity differs")
        bound(root, measurement["log"])
        if (measurement["command"] != expected_commands[name] or measurement["preparation"] != manifest["preparation"]
                or measurement["execution_status"] != "completed" or type(measurement["returncode"]) is not int
                or measurement["returncode"] != 0
                or not (_time(manifest["created_at_utc"]) <= _time(measurement["started_at_utc"]) <= _time(measurement["completed_at_utc"]))):
            raise ValueError("native environment measurement is not a genuine completed measurement")
    if manifest["environment"] != _qualification(root, manifest["measurements"]):
        raise ValueError("native environment qualification differs from measured outputs")
    return manifest


def _sealed(document: dict) -> dict:
    return {**document, "receipt_sha256": digest(canonical(document))}


def _command(root: Path, directory: Path, ticket: dict, capture: dict) -> dict:
    expected, before, after = ticket["expected"], ticket["before"], capture["after"]
    errors = capture["post_snapshot_errors"]
    after = after or {}
    artifacts = {ref["path"]: ref["sha256"] for ref in (
        ticket["run_manifest"], reference(root, directory / (ticket["role"] + ".ticket.json")),
        reference(root, directory / (ticket["role"] + ".capture.json")), capture["log"], *ticket["producers"].values())}
    result = {"name": ticket["role"], "command": ticket["command"], "cwd": ticket["cwd"],
              "native_execution_profile": NATIVE_PROFILE, "input_scope": expected["input_scope"],
              "expected_head": expected["head"], "head": before["head"], "final_head": after.get("head"),
              "expected_input_sha256": expected["inputs"], "input_sha256": before["inputs"],
              "input_sha256_after": after.get("inputs"),
              "input_drift": [] if before == after and not errors else ["execution snapshot changed or could not be authenticated"],
              "started_at_utc": capture["started_at_utc"], "completed_at_utc": capture["completed_at_utc"],
              "elapsed_seconds": capture["elapsed_seconds"], "execution_status": capture["execution_status"],
              "returncode": capture["returncode"], "tool_identity": before["execution_tools"]["python" if Path(ticket["command"][0]).name.startswith("python") else Path(ticket["command"][0]).name],
              "log": capture["log"]["path"], "log_sha256": capture["log"]["sha256"], "result_artifacts": artifacts,
              "ticket": reference(root, directory / (ticket["role"] + ".ticket.json")),
              "capture": reference(root, directory / (ticket["role"] + ".capture.json")),
              "run_manifest": ticket["run_manifest"], "recorder": ticket["producers"][RECORDER]}
    for label in ("execution_tools", "execution_environment"):
        result["expected_" + label] = expected[label]
        result[label + "_before"] = before[label]
        result[label + "_after"] = after.get(label)
    return _sealed(result)


def run_role(root: Path, directory: Path | str, role: str, *, timeout: float | None = None) -> dict:
    if timeout is not None and (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
                                or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("native execution timeout must be finite and positive")
    root = Path(root).resolve()
    directory = run_directory(root, directory)
    _open(root, directory)
    manifest = _manifest(root, directory)
    if manifest["root"] != root.as_posix():
        raise ValueError("native execution cannot relocate its prepared root")
    if role not in scopes.REQUIRED_COMMANDS:
        raise ValueError("unknown native validation role")
    for previous in scopes.REQUIRED_COMMANDS:
        if previous == role:
            break
        authenticate_receipt(root, directory, previous)
    ticket_path = directory / (role + ".ticket.json")
    if any((directory / (role + suffix)).exists() for suffix in (".ticket.json", ".capture.json", ".command.json", ".log")):
        raise ValueError("native role already attempted; preserve its original evidence")
    try:
        before = snapshot(root, role)
        if before != manifest["expectations"][role]:
            raise ValueError("current role inputs differ from predeclared run expectations")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        _stop(root, directory, role, "Preflight: " + str(exc))
        raise
    ticket = {"native_execution_profile": NATIVE_PROFILE, "run_id": manifest["run_id"],
              "execution_id": str(uuid4()), "issued_at_utc": stamp(), "role": role,
              "command": command_argv(role), "cwd": root.as_posix(), "expected": manifest["expectations"][role],
              "before": before, "run_manifest": reference(root, directory / "run.json"),
              "producers": manifest["producers"], "process_environment_overrides": OVERRIDES, "timeout_seconds": timeout}
    write_new(root, ticket_path, ticket)
    result = _execute(root, ticket["command"], directory / (role + ".log"), timeout)
    after, errors = None, []
    try:
        after = snapshot(root, role)
        if producer_bindings(root) != manifest["producers"]:
            errors.append("native producer bytes changed during execution")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    capture = {**result, "native_execution_profile": NATIVE_PROFILE, "execution_id": ticket["execution_id"],
               "ticket": reference(root, ticket_path), "log": reference(root, directory / (role + ".log")),
               "after": after, "post_snapshot_errors": errors}
    write_new(root, directory / (role + ".capture.json"), capture)
    command = _command(root, directory, ticket, capture)
    write_new(root, directory / (role + ".command.json"), command)
    if result["execution_status"] != "completed" or result["returncode"] != 0 or before != after or errors:
        _stop(root, directory, role, f"Actual outcome {result['execution_status']} exit {result['returncode']}; drift={bool(before != after or errors)}")
    return command


def authenticate_receipt(root: Path, directory: Path | str, role: str, *, require_success: bool = True) -> dict:
    root = Path(root).resolve()
    directory = run_directory(root, directory)
    manifest = _manifest(root, directory)
    if role not in scopes.REQUIRED_COMMANDS:
        raise ValueError("unknown native validation role")
    ticket_path, capture_path = (directory / (role + suffix) for suffix in (".ticket.json", ".capture.json"))
    ticket, capture = read_canonical(root, ticket_path), read_canonical(root, capture_path)
    receipt = read_canonical(root, directory / (role + ".command.json"))
    if (ticket.get("native_execution_profile") != NATIVE_PROFILE or ticket.get("run_id") != manifest["run_id"]
            or ticket.get("role") != role or ticket.get("cwd") != manifest["root"]
            or ticket.get("command") != command_argv(role) or ticket.get("producers") != manifest["producers"]
            or ticket.get("process_environment_overrides") != OVERRIDES
            or ticket.get("run_manifest") != reference(root, directory / "run.json")
            or ticket.get("expected") != manifest["expectations"][role] or ticket.get("before") != ticket["expected"]):
        raise ValueError("native ticket differs from predeclared role, inputs, producer or command")
    if (capture.get("native_execution_profile") != NATIVE_PROFILE or capture.get("ticket") != reference(root, ticket_path)
            or capture.get("execution_id") != ticket.get("execution_id")
            or capture.get("log") != reference(root, directory / (role + ".log"))):
        raise ValueError("native raw capture identity or log differs")
    if not (_time(manifest["created_at_utc"]) <= _time(ticket["issued_at_utc"]) <= _time(capture["started_at_utc"]) <= _time(capture["completed_at_utc"])):
        raise ValueError("native completion chronology differs")
    if receipt != _command(root, directory, ticket, capture):
        raise ValueError("native command receipt differs from original ticket/raw capture")
    if (capture["execution_status"] != "completed" or type(capture["returncode"]) is not int
            or not 0 <= capture["returncode"] < 128 or type(capture.get("pid")) is not int or capture["pid"] <= 0
            or capture.get("launch_error") is not None or capture["post_snapshot_errors"]
            or capture["after"] != ticket["before"]):
        raise ValueError("native execution is interrupted, incomplete, signaled or drifted")
    if require_success and capture["returncode"] != 0:
        raise ValueError("native execution completed with a nonzero outcome")
    return receipt


def ledger_custody_errors(document: dict, root: Path) -> list[str]:
    """Authenticate native custody only; never recurse into readiness policy."""
    try:
        root = Path(root).resolve()
        if document.get("native_execution_profile") != NATIVE_PROFILE:
            raise ValueError("current ledger lacks native execution custody")
        run_path = bound(root, document["run_manifest"])
        directory = run_directory(root, run_path.parent)
        if run_path.name != "run.json" or (directory / "STOP.json").exists():
            raise ValueError("native ledger uses the wrong manifest or a stopped run")
        manifest = _manifest(root, directory)
        if document.get("environment") != manifest["environment"] or document.get("declared_environment_match") is not manifest["environment"]["declared_environment_match"]:
            raise ValueError("native ledger environment claim differs from actual measurement")
        commands = document.get("commands")
        if not isinstance(commands, list) or [c.get("name") for c in commands] != list(scopes.REQUIRED_COMMANDS):
            raise ValueError("native ledger role membership or order differs")
        expected = {}
        for command in commands:
            role = command["name"]
            original = authenticate_receipt(root, directory, role)
            if original != command:
                raise ValueError("native ledger command differs from original receipt: " + role)
            ref = reference(root, directory / (role + ".command.json"))
            expected[ref["path"]] = ref["sha256"]
        if document.get("receipt_artifacts") != expected:
            raise ValueError("native ledger receipt hash membership differs")
        return []
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return ["Native validation custody: " + str(exc)]


def finalize_ledger(root: Path, directory: Path | str) -> dict:
    root = Path(root).resolve()
    directory = run_directory(root, directory)
    _open(root, directory)
    manifest = _manifest(root, directory)
    commands = [authenticate_receipt(root, directory, role) for role in scopes.REQUIRED_COMMANDS]
    receipts = [reference(root, directory / (role + ".command.json")) for role in scopes.REQUIRED_COMMANDS]
    document = {"native_execution_profile": NATIVE_PROFILE, "input_scope_profile": scopes.PROFILE,
                "head": head(root), "input_sha256": scopes.ledger_inputs(root), "commands": commands,
                "receipt_artifacts": {ref["path"]: ref["sha256"] for ref in receipts},
                "run_manifest": reference(root, directory / "run.json"), "finalized_at_utc": stamp(),
                "environment": manifest["environment"],
                "declared_environment_match": manifest["environment"]["declared_environment_match"]}
    from current_publication_readiness import validation_errors
    errors = ledger_custody_errors(document, root) + validation_errors(document, root, document["head"])
    if errors:
        _stop(root, directory, "ledger", " | ".join(errors))
        raise ValueError("native ledger did not authenticate: " + " | ".join(errors))
    write_new(root, directory / "commands.json", document)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--directory", type=Path, required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--authorization", type=Path, required=True)
    execute = sub.add_parser("run-role")
    execute.add_argument("role", choices=list(scopes.REQUIRED_COMMANDS))
    execute.add_argument("--timeout", type=float)
    sub.add_parser("ledger")
    sub.add_parser("authenticate")
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            value = prepare_run(args.root, args.directory, args.authorization)
        elif args.action == "run-role":
            value = run_role(args.root, args.directory, args.role, timeout=args.timeout)
            print(json.dumps({key: value[key] for key in ("name", "execution_status", "returncode", "input_drift")}, indent=2))
            return 0 if value["execution_status"] == "completed" and value["returncode"] == 0 and not value["input_drift"] else 1
        elif args.action == "ledger":
            value = finalize_ledger(args.root, args.directory)
        else:
            directory = run_directory(args.root, args.directory)
            value = read_canonical(args.root, directory / "commands.json")
            from current_publication_readiness import validation_errors
            errors = ledger_custody_errors(value, args.root) + validation_errors(value, args.root)
            if errors:
                raise ValueError(" | ".join(errors))
        print(json.dumps({"native_execution_profile": NATIVE_PROFILE, "action": args.action,
                          "directory": str(args.directory), "declared_environment_match": value.get("declared_environment_match", value.get("environment", {}).get("declared_environment_match"))}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
