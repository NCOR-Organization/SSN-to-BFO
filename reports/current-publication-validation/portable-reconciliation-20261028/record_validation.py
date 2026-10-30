#!/usr/bin/env python3
"""Retain actual portable-reconciliation repair executions; stop on failure.

Create-once receipts bind the complete current input map and actual command.
This recorder never refreshes old receipts, stages files, or certifies semantic
approval. Its own exact bytes are retained as an execution artifact.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import current_publication_readiness as readiness

FOCUSED = {
    "focused_cco": ["python", "-B", "-m", "unittest", "tests.test_cco_extension"],
    "focused_selection": ["python", "-B", "-m", "unittest", "tests.test_current_validation_selection"],
    "focused_placeholder": ["python", "-B", "-m", "unittest", "tests.test_placeholder_catalog_migration"],
    "focused_checkpoint": ["python", "-B", "-m", "unittest", "tests.test_current_checkpoint_successor"],
    "focused_portable": ["python", "-B", "-m", "unittest", "tests.test_current_portable_execution_evidence"],
    "focused_retained": ["python", "-B", "-m", "unittest", "tests.test_current_retained_evidence",
                         "tests.test_current_retained_evidence_integration"],
    "focused_custody": ["python", "-B", "-m", "unittest", "tests.test_current_semantic_validation",
                        "tests.test_current_semantic_invocation", "tests.test_current_semantic_schema",
                        "tests.test_current_semantic_retry"],
    "focused_preservation": ["python", "-B", "-m", "unittest", "tests.test_current_source_identity",
                             "tests.test_current_publication_preservation", "tests.test_current_semantic_preservation",
                             "tests.test_current_publication_readiness"],
    "focused_release_contract": ["python", "-B", "-m", "unittest", "tests.test_release_contract"],
    "diff_check": ["git", "diff", "--check"],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def head():
    return subprocess.check_output(["git", "--no-optional-locks", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def inputs():
    return {path: sha(ROOT / path) for path in sorted(readiness.validation_inputs(ROOT))}


def write_new(path, document):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    name = sys.argv[1]
    if (DIRECTORY / "STOP.json").exists():
        raise RuntimeError("Validation sequence already stopped on its first failure")
    commands = {**readiness.REQUIRED_COMMANDS, **FOCUSED}
    command = list(sys.argv[2:]) if name.startswith("focused_") and len(sys.argv) > 2 else list(commands[name])
    if name.startswith("focused_") and "unittest" in command:
        command.insert(command.index("unittest") + 1, "-f")
    command[0] = sys.executable if command[0] == "python" else shutil.which(command[0])
    if not command[0]:
        raise RuntimeError("Required executable unavailable")
    receipt, log = DIRECTORY / (name + ".command.json"), DIRECTORY / (name + ".log")
    if receipt.exists() or log.exists():
        raise RuntimeError("Refusing to overwrite an existing execution")
    before_head, before_inputs = head(), inputs()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0")
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    executable = Path(command[0]).resolve()
    tool_identity = {"path": str(executable), "sha256": sha(executable)}
    source_hash = sha(__file__)
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    print(json.dumps({"started": name, "command": command}), flush=True)
    with log.open("xb") as stream:
        result = subprocess.run(command, cwd=ROOT, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    completed = datetime.now(timezone.utc).isoformat()
    after_head, after_inputs = head(), inputs()
    drift = sorted(path for path in before_inputs.keys() | after_inputs.keys()
                   if before_inputs.get(path) != after_inputs.get(path))
    log_name, log_hash = relative(log), sha(log)
    document = {
        "name": name, "command": command, "cwd": str(ROOT),
        "head": before_head, "expected_head": before_head, "final_head": after_head,
        "expected_input_sha256": before_inputs, "input_sha256": before_inputs,
        "input_sha256_after": after_inputs, "input_drift": drift,
        "tool_identity": tool_identity, "execution_status": "completed", "returncode": result.returncode,
        "started_at_utc": started, "completed_at_utc": completed,
        "elapsed_seconds": time.monotonic() - timer, "log": log_name, "log_sha256": log_hash,
        "result_artifacts": {log_name: log_hash, relative(__file__): source_hash},
        "recorder": {"path": relative(__file__), "sha256": source_hash},
        "scope": "Actual named code/test execution; no independent semantic approval or publication-readiness grant.",
    }
    for value in command[1:]:
        candidate = ROOT / value
        if value.endswith(".py") and not Path(value).is_absolute() and candidate.is_file():
            document["result_artifacts"][value] = sha(candidate)
    if name == "focused_inventory":
        inventory = DIRECTORY / "retained-inventory.json"
        if inventory.is_file():
            document["result_artifacts"][relative(inventory)] = sha(inventory)
    errors = readiness.command_errors(document, after_head, after_inputs, ROOT)
    if sha(__file__) != source_hash:
        errors.append("Recorder changed during execution")
    document["receipt_authentication_errors"] = errors
    write_new(receipt, document)
    failed = result.returncode != 0 or bool(errors)
    if failed:
        write_new(DIRECTORY / "STOP.json", {"first_failure": name, "receipt": relative(receipt),
                                          "returncode": result.returncode, "authentication_errors": errors})
    print(json.dumps({"completed": name, "returncode": result.returncode,
                      "receipt": relative(receipt), "authentication_errors": errors}), flush=True)
    return result.returncode or (1 if errors else 0)


if __name__ == "__main__":
    raise SystemExit(main())
