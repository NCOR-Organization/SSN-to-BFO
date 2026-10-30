#!/usr/bin/env python3
"""Record fresh bounded publication checks; never certify full publication readiness.

Each invocation executes one canonical command and retains its actual pre/post
bindings and output. Existing receipts are never refreshed or overwritten.
``finalize`` creates an additive ledger only from successful, still-current
receipts. Whole-suite testing, ``make check``, environment qualification, and
semantic reasoner invocation tickets are outside this recorder's scope.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import current_publication_readiness as readiness  # noqa: E402

NAMES = (
    "assessment",
    "source_identity",
    "generation_freshness",
    "sosa_source_version",
    "sosa_products",
    "static_checks",
    "scoped_authentication",
)
SEMANTIC_NAME = "semantic_execution"
PREDECESSOR = ROOT / "reports/current-publication-validation/commands.json"


def timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *arguments], text=True
    ).strip()


def inputs() -> dict[str, str]:
    return {
        path: digest(ROOT / path)
        for path in sorted(readiness.validation_inputs(ROOT))
    }


def write_new(path: Path, document: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")


def argv_for(name: str) -> list[str]:
    if name == SEMANTIC_NAME:
        return [
            sys.executable,
            "-B",
            "tools/current_semantic_validation.py",
            "--output",
            relative(DIRECTORY / "semantic.json"),
        ]
    if name == "scoped_authentication":
        return [sys.executable, "-B", str(DIRECTORY / "scoped_authentication.py")]
    command = list(readiness.REQUIRED_COMMANDS[name])
    if command[0] == "python":
        command[0] = sys.executable
    else:
        executable = shutil.which(command[0])
        if executable is None:
            raise RuntimeError("Required executable is unavailable: " + command[0])
        command[0] = executable
    return command


def artifact_sources(command: list[str]) -> dict[str, str]:
    paths = {Path(__file__).resolve()}
    for argument in command[1:]:
        if argument.endswith(".py"):
            path = Path(argument)
            if not path.is_absolute():
                path = ROOT / path
            if not path.is_file():
                raise RuntimeError("Command script is unavailable: " + str(path))
            paths.add(path.resolve())
    return {relative(path): digest(path) for path in sorted(paths)}


def record(name: str) -> int:
    record_path = DIRECTORY / (name + ".command.json")
    log_path = DIRECTORY / (name + ".log")
    if os.path.lexists(record_path) or os.path.lexists(log_path):
        raise RuntimeError("Fresh execution requires unused receipt and log paths: " + name)
    if name == SEMANTIC_NAME and any(
        os.path.lexists(DIRECTORY / filename) for filename in ("semantic.json", "semantic.md")
    ):
        raise RuntimeError("Fresh semantic execution requires unused output paths")

    command = argv_for(name)
    executable = Path(command[0]).resolve()
    expected_head = git("rev-parse", "HEAD")
    expected_inputs = inputs()
    tool_identity = {"path": str(executable), "sha256": digest(executable)}
    source_artifacts = artifact_sources(command)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")

    # A fresh external cache keeps make compile's bytecode outside the checkout.
    # The location is retained in the receipt; no existing cache is removed.
    cache = None
    if name == "static_checks":
        cache = tempfile.mkdtemp(prefix="ssn-publication-bytecode-")
        environment["PYTHONPYCACHEPREFIX"] = cache

    head = git("rev-parse", "HEAD")
    before = inputs()
    if head != expected_head or before != expected_inputs:
        raise RuntimeError("Inputs changed before command launch; no execution recorded")

    started = timestamp()
    start = time.monotonic()
    status = "completed"
    launch_error = None
    with log_path.open("xb") as stream:
        try:
            process = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
            )
            returncode = process.returncode
        except OSError as error:
            status = "launch_failed"
            returncode = 127
            launch_error = str(error)
            stream.write(("Command launch failed: " + str(error) + "\n").encode())
    completed = timestamp()
    elapsed = time.monotonic() - start
    final_head = git("rev-parse", "HEAD")
    after = inputs()
    drift = sorted(
        path for path in before.keys() | after.keys()
        if before.get(path) != after.get(path)
    )
    log_hash = digest(log_path)
    artifacts = dict(source_artifacts)
    artifacts[relative(log_path)] = log_hash
    if name == "scoped_authentication":
        result = DIRECTORY / "scoped-authentication.json"
        if result.is_file():
            artifacts[relative(result)] = digest(result)
    elif name == SEMANTIC_NAME:
        for filename in ("semantic.json", "semantic.md"):
            result = DIRECTORY / filename
            if result.is_file():
                artifacts[relative(result)] = digest(result)
    document = {
        "name": name,
        "head": head,
        "expected_head": expected_head,
        "final_head": final_head,
        "command": command,
        "tool_identity": tool_identity,
        "cwd": str(ROOT),
        "expected_input_sha256": expected_inputs,
        "input_sha256": before,
        "input_sha256_after": after,
        "input_drift": drift,
        "started_at_utc": started,
        "completed_at_utc": completed,
        "elapsed_seconds": elapsed,
        "execution_status": status,
        "returncode": returncode,
        "log": relative(log_path),
        "log_sha256": log_hash,
        "result_artifacts": artifacts,
        "recorder": {"path": relative(Path(__file__)), "sha256": source_artifacts[relative(Path(__file__))]},
        "execution_environment_overrides": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "python_bin_prepended_to_PATH": str(Path(sys.executable).parent),
            **({"PYTHONPYCACHEPREFIX": cache} if cache else {}),
        },
        "scope": "Fresh bounded execution; not a whole-suite, full repository, or environment-qualification result.",
    }
    if launch_error is not None:
        document["launch_error"] = launch_error
    errors = readiness.command_errors(document, final_head, after, ROOT)
    document["receipt_authentication_errors"] = errors
    write_new(record_path, document)
    print(json.dumps({"name": name, "returncode": returncode, "receipt": relative(record_path), "authentication_errors": errors}), flush=True)
    if returncode:
        return returncode
    # Preserve the gate's real returncode in the receipt; custody failures are
    # recorder failures and must stop a caller even if the gate itself passed.
    return 1 if errors else 0


def finalize() -> int:
    destination = DIRECTORY / "commands.json"
    if os.path.lexists(destination):
        raise RuntimeError("Refusing to overwrite an existing successor ledger")
    head = git("rev-parse", "HEAD")
    bound_inputs = inputs()
    commands = []
    receipt_artifacts = {}
    for name in NAMES:
        path = DIRECTORY / (name + ".command.json")
        document = json.loads(path.read_text())
        if document.get("name") != name or document.get("returncode") != 0:
            raise RuntimeError("Missing or unsuccessful actual receipt: " + name)
        errors = readiness.command_errors(document, head, bound_inputs, ROOT)
        if errors or document.get("receipt_authentication_errors") != []:
            raise RuntimeError("Receipt is not current: " + name + ": " + " | ".join(errors))
        if name == "scoped_authentication":
            result_path = relative(DIRECTORY / "scoped-authentication.json")
            if result_path not in document.get("result_artifacts", {}):
                raise RuntimeError("Scoped authentication output is not bound to its receipt")
            scoped_result = json.loads((ROOT / result_path).read_text())
            if scoped_result.get("status") != "PASS":
                raise RuntimeError("Scoped authentication output does not report PASS")
        commands.append(document)
        receipt_artifacts[relative(path)] = digest(path)
    diagnostic_commands = []
    semantic_receipt = DIRECTORY / (SEMANTIC_NAME + ".command.json")
    if semantic_receipt.exists():
        diagnostic = json.loads(semantic_receipt.read_text())
        errors = readiness.command_errors(diagnostic, head, bound_inputs, ROOT)
        if diagnostic.get("name") != SEMANTIC_NAME or errors:
            raise RuntimeError("Semantic driver receipt custody is not current: " + " | ".join(errors))
        # The real semantic exit (including independent profile/closure failure)
        # remains visible, outside the seven successful selected commands.
        diagnostic_commands.append(diagnostic)
        receipt_artifacts[relative(semantic_receipt)] = digest(semantic_receipt)
    if git("rev-parse", "HEAD") != head or inputs() != bound_inputs:
        raise RuntimeError("Candidate changed during successor-ledger finalization")
    predecessor = {"path": relative(PREDECESSOR), "sha256": digest(PREDECESSOR)}
    missing = sorted(set(readiness.REQUIRED_COMMANDS) - set(NAMES))
    document = {
        "head": head,
        "branch": git("branch", "--show-current"),
        "input_sha256": bound_inputs,
        "environment": {"qualification_status": "not_performed", "historical_environment_reference": {**predecessor, "json_pointer": "/environment"}},
        "declared_environment_match": False,
        "environment_note": "Environment qualification was not performed. Historical environment details remain only in the predecessor and are not asserted as current measurements.",
        "commands": commands,
        "blocked_diagnostic_commands": diagnostic_commands,
        "prior_attempts": [],
        "predecessor": {**predecessor, "role": "Immutable historical execution ledger; original hashes and results preserved."},
        "receipt_artifacts": receipt_artifacts,
        "finalized_at_utc": timestamp(),
        "binding_basis": "Each command was actually executed by this recorder with complete pre/post HEAD, inputs, executable, completion, zero-drift, and output bindings. No historical command or log was promoted.",
        "classification": "BOUNDED CURRENT THREE-TERM SUCCESSOR EXECUTION LEDGER — NOT FULL PUBLICATION READINESS",
        "not_run": missing,
        "remaining_independent_requirements": ["unit_tests", "full_repository_gate", "environment qualification", "independent semantic publication evidence"],
        "semantic_interpretation": "Recognizes authenticated existing semantic evolution only; no new mapping decision, full repository PASS, or semantic reasoner invocation is claimed.",
    }
    write_new(destination, document)
    print(json.dumps({"ledger": relative(destination), "sha256": digest(destination), "commands": len(commands), "missing_required_commands": missing}), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", choices=(*NAMES, SEMANTIC_NAME, "finalize"))
    arguments = parser.parse_args()
    return finalize() if arguments.name == "finalize" else record(arguments.name)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print("Execution recorder stopped: " + str(error), file=sys.stderr)
        raise SystemExit(1)
