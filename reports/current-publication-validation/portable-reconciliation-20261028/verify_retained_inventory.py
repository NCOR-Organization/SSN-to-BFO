#!/usr/bin/env python3
"""Verify retained execution custody in an isolated, runtime-free checkout.

This helper does not execute Java, regenerate evidence, update old receipts, or
grant freshness/publication readiness. Its report is create-once execution
output. The verifier subprocess cannot read the original checkout or start any
child process. Only setup provisions the independently pinned ROBOT dependency.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback


DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
MANIFEST = "reports/retained-evidence/execution/manifests/66262154210cb9e41136bd28622d915eac4df7d498ed87d2a5d08eeb2a99b38a.json"
MANIFEST_SHA256 = "36879ba5baf9bc48984f1c91ba9eb5cd720866a5a52e118dd5c7802b4b0f57ed"
EXCLUSION_AUTHORITY_SHA256 = "099e8b273ae26227cbcbbc1fdca58e226f056910e3f47c748ea31394b0ca2eda"
EXCLUSION_AUTHORITY = "checkpoint-path-resume-20261028 final-integrity.json"
# Exact exclusions copied from the preceding authenticated task inventory.
# Embedded here so execution does not depend on an external temporary report.
EXCLUDED_PATHS = (
    'reports/current-publication-validation/three-term-20261028/classify_remaining.py',
    'reports/current-publication-validation/three-term-20261028/independent_final_invariants.py',
    'reports/current-publication-validation/three-term-20261028/preexisting-sosa-output-preservation.json',
    'reports/current-publication-validation/three-term-20261028/prepare_reconciliation_report.py',
    'reports/current-semantic-workbook/five-historical-restorations/README.md',
    'reports/current-semantic-workbook/five-historical-restorations/RestorationProfile.java',
    'reports/current-semantic-workbook/five-historical-restorations/authorized-instructions.txt',
    'reports/current-semantic-workbook/five-historical-restorations/baseline-closure.json',
    'reports/current-semantic-workbook/five-historical-restorations/baseline-command.json',
    'reports/current-semantic-workbook/five-historical-restorations/baseline-profile.json',
    'reports/current-semantic-workbook/five-historical-restorations/baseline-test-manifest.json',
    'reports/current-semantic-workbook/five-historical-restorations/baseline-test-runner.py',
    'reports/current-semantic-workbook/five-historical-restorations/candidate-closure.json',
    'reports/current-semantic-workbook/five-historical-restorations/candidate-command.json',
    'reports/current-semantic-workbook/five-historical-restorations/candidate-evidence.json',
    'reports/current-semantic-workbook/five-historical-restorations/candidate-profile.json',
    'reports/current-semantic-workbook/five-historical-restorations/cco-hermit-diagnostic.json',
    'reports/current-semantic-workbook/five-historical-restorations/cco-hermit-diagnostic.log',
    'reports/current-semantic-workbook/five-historical-restorations/compile-command.json',
    'reports/current-semantic-workbook/five-historical-restorations/completion-report.md',
    'reports/current-semantic-workbook/five-historical-restorations/evidence-manifest.json',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/candidate-products/alignment_core.ttl',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/candidate-products/cco_extension.ttl',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/candidate-products/integrated.ttl',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/candidate-products/strict_bfo_mapping.ttl',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/current_publication_readiness.attempted.py',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/reports/current-decision-applicability/records/deb81f0c-b9a5-4c56-8eb9-21932286e63b.json',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/reports/current-decision-applicability/records/e651dfbf-55d4-43cc-95d9-8812ded497a1.json',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/reports/current-semantic-workbook/transitions/db676afa-aae7-4fb5-aa57-e950fb101ffe.json',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/reports/current-semantic-workbook/versions/5465730d1d20f186b0d2c853eb48e81135bdf4abd383a639f30e833a0ba08675.xlsx',
    'reports/current-semantic-workbook/five-historical-restorations/failed-attempt/reports/current-semantic-workbook/versions/9e526e5705fc84571e03616f74c59fe8654fcc073a1c45a281109cf22c276e14.xlsx',
    'reports/current-semantic-workbook/five-historical-restorations/generation-update.log',
    'reports/current-semantic-workbook/five-historical-restorations/independent-per-term-coverage.json',
    'reports/current-semantic-workbook/five-historical-restorations/initial-file-hashes.json',
    'reports/current-semantic-workbook/five-historical-restorations/installation.json',
    'reports/current-semantic-workbook/five-historical-restorations/preconditions.json',
    'reports/current-semantic-workbook/five-historical-restorations/preinstall-validation.json',
    'reports/current-semantic-workbook/five-historical-restorations/profile-comparison.json',
    'reports/current-semantic-workbook/five-historical-restorations/readiness-renderer-audit.json',
    'reports/current-semantic-workbook/five-historical-restorations/recorded-transition.json',
    'reports/current-semantic-workbook/five-historical-restorations/required-cco-hermit/cco-extension-pinned-merged-cco-bfo-closure-owl2dl-profile.ttl',
    'reports/current-semantic-workbook/five-historical-restorations/required-cco-hermit/cco-extension-pinned-merged-cco-bfo-closure.ttl',
    'reports/current-semantic-workbook/five-historical-restorations/required-hermit-failure-audit.json',
    'reports/current-semantic-workbook/five-historical-restorations/restoration-baseline-coms.log',
    'reports/current-semantic-workbook/five-historical-restorations/restoration-baseline-current-hermit7.log',
    'reports/current-semantic-workbook/five-historical-restorations/restoration-baseline-current.log',
    'reports/current-semantic-workbook/five-historical-restorations/restoration-baseline-publication.log',
    'reports/current-semantic-workbook/five-historical-restorations/restoration-baseline-sosa94.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-assessment.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-documentary-history.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-generation-freshness.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-git-diff-check.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-independent-audit.json',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-preservation.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-readiness-tests.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-semantic-history.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-source-identity.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-validation-results.json',
    'reports/current-semantic-workbook/five-historical-restorations/rollback-validation.log',
    'reports/current-semantic-workbook/five-historical-restorations/rollback.json',
    'reports/current-semantic-workbook/five-historical-restorations/xlsx-preservation.json',
)
EXPECTED_DOCUMENTS = 27
EXPECTED_BYTES = 29443721
JAR_PATH = "build/lib/robot-1.9.7/robot.jar"
JAR_SHA256 = "91890c2e83d0f092dd08731376f154b36610544cfbe8685337a1bf7244ccaa2d"
RUNTIME = "build/current-semantic-validation"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(path):
    data = Path(path).read_bytes()
    return {"sha256": digest(data), "bytes": len(data)}


def read_json(path):
    return json.loads(Path(path).read_bytes())


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def local(root, relative):
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts
            and path.as_posix() == relative, "noncanonical candidate path: " + relative)
    actual = root / path
    require(actual.resolve().is_relative_to(root), "candidate escapes checkout: " + relative)
    return actual


def regular(path):
    require(stat.S_ISREG(path.lstat().st_mode), "non-regular candidate: " + str(path))


def copy_regular(source, destination):
    regular(source)
    data = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(data)
    destination.chmod(stat.S_IMODE(source.stat().st_mode))
    return {"sha256": digest(data), "bytes": len(data)}


def tree_fingerprints(root):
    result = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "unexpected symlink in isolated checkout")
        if path.is_file():
            regular(path)
            result[path.relative_to(root).as_posix()] = fingerprint(path)
    return result


def install_access_guard(original):
    """Deny original content access and all verifier-side process/network use."""
    original = original.resolve()
    blocked = []

    def forbidden_path(value):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        path = Path(os.fsdecode(value))
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve().is_relative_to(original)

    def audit(event, arguments):
        denied = False
        if event in {"open", "os.listdir", "os.scandir", "os.chdir"}:
            denied = bool(arguments) and forbidden_path(arguments[0])
        elif (event in {"subprocess.Popen", "os.system", "os.posix_spawn",
                        "os.exec", "socket.connect", "socket.connect_ex"}
              or event.startswith("os.spawn")):
            denied = True
        if denied:
            blocked.append({"event": event, "argument": str(arguments[0]) if arguments else None})
            raise PermissionError("isolated custody verifier denied " + event)

    sys.addaudithook(audit)
    try:
        (original / "SSN2BFO.ttl").read_bytes()
    except PermissionError:
        pass
    else:
        raise ValueError("original checkout content guard did not reject its probe")
    require(len(blocked) == 1, "unexpected guard behavior during installation")
    return blocked


def worker(args):
    fresh = Path(args.fresh_root).resolve()
    original = Path(args.original_root).resolve()
    result_path = Path(args.worker_output).resolve()
    require(not fresh.is_relative_to(original), "isolated checkout is inside original repository")
    require(result_path.parent == fresh.parent, "worker output must be outside copied checkout")
    result = {"status": "FAIL", "phase": "install_access_guard", "documents": []}
    blocked = []
    try:
        blocked = install_access_guard(original)
        sys.path.insert(0, str(fresh / "tools"))
        import current_portable_execution_evidence as portable
        import current_semantic_invocation as invocation
        import current_semantic_validation as semantic
        import current_retained_evidence as retained

        for module in (portable, invocation, semantic, retained):
            require(Path(module.__file__).resolve().is_relative_to(fresh),
                    "verifier imported code outside isolated checkout")
        result["imported_verifiers"] = {
            module.__name__: Path(module.__file__).resolve().relative_to(fresh).as_posix()
            for module in (portable, invocation, semantic, retained)}
        result["phase"] = "authenticate_manifest"
        require(not (fresh / ".git").exists(), "Git metadata was copied")
        require(not (fresh / RUNTIME).exists(), "semantic runtime tree was copied")
        manifest_path = fresh / MANIFEST
        require(fingerprint(manifest_path)["sha256"] == MANIFEST_SHA256, "retained manifest changed")
        manifest = read_json(manifest_path)
        report = read_json(portable.bound_file(fresh, manifest["source_report"]))
        require(report["status"] == "FAIL", "historical semantic result is no longer FAIL")
        context = portable.context(report, fresh)
        require(context is not None, "portable evidence context is missing")
        require(len(context.documents) == EXPECTED_DOCUMENTS, "retained document count differs")
        require(sum(ref["bytes"] for ref in context.documents.values()) == EXPECTED_BYTES,
                "retained document byte total differs")

        result["phase"] = "independent_execution_plan"
        plan = semantic.expected_execution_plan(fresh)
        require(set(plan) == set(report["selected_invocations"]), "required invocation membership differs")
        require(len(plan) == EXPECTED_DOCUMENTS, "independent slot count differs")
        require({ref["slot"] for ref in context.documents.values()} == set(plan),
                "retained slot membership differs")
        evidence = {ref["path"]: ref for ref in report["evidence_files"]}
        directory = Path(report["evidence_directory"])
        for ref in sorted(context.documents.values(), key=lambda value: value["logical_path"]):
            result["phase"] = "document:" + ref["logical_path"]
            require(ref["role"] == "execution_graph", "unexpected retained role")
            require(not (fresh / ref["logical_path"]).exists(), "runtime RDF was recreated")
            expected = plan[ref["slot"]]
            require(ref["execution_identity"] == expected["identity"], "execution identity differs")
            require(ref["source_inputs"] == expected["identity"]["governed_inputs"],
                    "source-input inventory differs")
            for source in ref["source_inputs"]:
                portable.bound_file(fresh, source)
            graph = context.resolve({"path": ref["logical_path"], "sha256": ref["sha256"],
                                     "bytes": ref["bytes"]})
            require(graph.relative_to(fresh).as_posix() == ref["retained_path"],
                    "resolver returned a non-retained object")
            require(fingerprint(graph) == {"sha256": ref["sha256"], "bytes": ref["bytes"]},
                    "retained object byte identity differs")
            require(len(ref["dependent_records"]) == 7, "dependent receipt inventory differs")
            for dependency in ref["dependent_records"]:
                require(evidence.get(dependency["path"]) == dependency,
                        "dependent receipt lacks source-report binding")
                portable.bound_file(fresh, dependency)
            command = read_json(portable.bound_file(fresh, ref["producer"]))
            name = expected["identity"]["id"]
            raw = read_json(portable.bound_file(fresh, evidence[
                (directory / (name + ".result.json")).as_posix()]))
            require(raw["attempt"] == command, "producer/raw execution disagree")
            semantic.validate_execution_slot(raw, expected, report, fresh, portable=context)
            semantic.verify_invocation_chain(
                command, raw, expected, report, directory, evidence, fresh, portable=context)
            ticket_path = fresh / directory / "invocations" / (ref["invocation_id"] + ".ticket.json")
            receipt = context.verify_result(ticket_path, expected=expected)
            require(receipt["ticket"]["slot"] == ref["slot"], "selected ticket slot differs")
            result["documents"].append({
                **ref, "verified": True,
                "checks": ["exact_hash_and_size", "role_and_slot", "independent_execution_identity",
                           "source_input_bytes", "producer_and_seven_bound_dependents",
                           "RDF_identity_and_command_plan", "ticket_capture_envelope_and_output_seals",
                           "current_executable_identity"],
                "recorded_returncode": receipt["envelope"]["returncode"],
                "recorded_execution_status": receipt["envelope"]["execution_status"]})

        result["phase"] = "toolchain"
        configuration = dict(line.split("=", 1) for line in
                             (fresh / "config/validation-toolchain.env").read_text().splitlines()
                             if line and not line.startswith("#"))
        require(configuration["VALIDATION_ROBOT_SHA256"] == JAR_SHA256 == semantic.ROBOT_SHA256,
                "governed JAR policies disagree")
        chain = manifest["toolchain"]
        require(chain["reasoner_jar"]["path"] == JAR_PATH
                and chain["reasoner_jar"]["sha256"] == JAR_SHA256,
                "retained JAR binding differs")
        for key in ("configured_environment", "reasoner_source", "reasoner_jar", "version_command"):
            portable.bound_file(fresh, chain[key])
        for ref in chain["version_outputs"]:
            portable.bound_file(fresh, ref)
        tool_results = []
        for tool in manifest["tools"]:
            command = read_json(portable.bound_file(fresh, tool["producer"]))
            context.verify_tool(command)
            require(context.command(command["command"]) == tool["command"],
                    "portable tool command differs")
            executable = Path(shutil.which(tool["executable"]["name"])).resolve()
            require(fingerprint(executable) == {
                "sha256": tool["executable"]["sha256"], "bytes": tool["executable"]["bytes"]},
                "actual tool binary differs")
            tool_results.append({**tool, "verified": True, "actual_executable": str(executable)})
        result["tools"] = tool_results
        result["toolchain"] = chain

        result["phase"] = "canonical_reconciliation"
        derived, errors = semantic.reconcile_raw_evidence(report, fresh)
        result["custody_errors"] = errors
        require(not errors, "canonical raw-evidence custody reconciliation failed: " + repr(errors))
        require(derived["status"] == report["status"] == "FAIL",
                "retention changed the original semantic outcome")
        require(not (fresh / RUNTIME).exists(), "canonical verifier recreated runtime artifacts")
        require(all(not (fresh / ref["logical_path"]).exists()
                    for ref in context.documents.values()), "a runtime document was recreated")
        require(len(blocked) == 1, "verifier attempted forbidden original/process/network access")
        result.update(status="PASS", phase="complete", document_count=len(context.documents),
                      document_bytes=sum(ref["bytes"] for ref in context.documents.values()),
                      required_slot_count=len(plan), original_status=report["status"],
                      reconciled_status=derived["status"], runtime_absent=True,
                      git_metadata_absent=True, original_access_guard_probe_passed=True,
                      fresh_execution=False, freshness_or_readiness_granted=False)
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
        result["traceback"] = traceback.format_exc()
    finally:
        result["blocked_access_events"] = blocked
        write_new(result_path, result)
    return 0 if result["status"] == "PASS" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--fresh-root")
    parser.add_argument("--original-root")
    parser.add_argument("--worker-output")
    args = parser.parse_args()
    if args.worker:
        return worker(args)
    output = DIRECTORY / "retained-inventory.json"
    require(not output.exists(), "verification output already exists; preserve prior execution")
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    result = {"status": "FAIL", "started_at_utc": started,
              "scope": "Exact retained historical custody; no execution freshness or semantic PASS grant.",
              "exclusion_authority": EXCLUSION_AUTHORITY,
              "exclusion_authority_sha256": EXCLUSION_AUTHORITY_SHA256}
    protected_before = {}
    try:
        require(len(EXCLUDED_PATHS) == len(set(EXCLUDED_PATHS)) == 61,
                "exclusion inventory must contain exactly 61 paths")
        require(sum(p.startswith("reports/current-semantic-workbook/five-historical-restorations/")
                    for p in EXCLUDED_PATHS) == 57, "historical archive exclusion count differs")
        listed = subprocess.check_output(
            ["git", "--no-optional-locks", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT)
        inventory = sorted(set(p.decode() for p in listed.split(b"\0") if p))
        require(set(EXCLUDED_PATHS) <= set(inventory), "declared excluded path is absent from inventory")
        candidates = [p for p in inventory if p not in EXCLUDED_PATHS]
        require(not any(p == ".git" or p.startswith((".git/", "build/")) for p in candidates),
                "Git metadata or runtime/build output entered candidate inventory")
        helper_relative = Path(__file__).resolve().relative_to(ROOT).as_posix()
        own_directory = DIRECTORY.relative_to(ROOT).as_posix() + "/"
        result["candidate_paths"] = candidates
        result["excluded_paths"] = list(EXCLUDED_PATHS)
        with tempfile.TemporaryDirectory(prefix="portable-retained-inventory-") as temporary:
            temporary = Path(temporary).resolve()
            fresh = temporary / "checkout"
            fresh.mkdir()
            copied = {}
            for relative in candidates:
                copied[relative] = copy_regular(local(ROOT, relative), fresh / relative)
                # The current recorder's streaming log is output, not immutable
                # input. Freeze its helpers, plus every input outside this run.
                if not relative.startswith(own_directory) or relative.endswith(".py"):
                    protected_before[relative] = copied[relative]
            original_manifest = read_json(ROOT / MANIFEST)
            require(fingerprint(ROOT / MANIFEST)["sha256"] == MANIFEST_SHA256,
                    "retained manifest differs before setup")
            require(original_manifest["toolchain"]["reasoner_jar"]["sha256"] == JAR_SHA256,
                    "manifest JAR differs from governed pin")
            jar_identity = copy_regular(local(ROOT, JAR_PATH), fresh / JAR_PATH)
            require(jar_identity["sha256"] == JAR_SHA256, "setup JAR has wrong governed hash")
            protected_before[JAR_PATH] = jar_identity
            copied[JAR_PATH] = jar_identity
            result["setup_dependency"] = {"path": JAR_PATH, **jar_identity}
            require(not (fresh / ".git").exists() and not (fresh / RUNTIME).exists(),
                    "forbidden runtime data entered isolated setup")
            result_path = temporary / "worker-result.json"
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            environment.pop("PYTHONPATH", None)
            command = [sys.executable, "-B", str(fresh / helper_relative), "--worker",
                       "--fresh-root", str(fresh), "--original-root", str(ROOT),
                       "--worker-output", str(result_path)]
            completed = subprocess.run(command, cwd=fresh, env=environment,
                                       capture_output=True, close_fds=True)
            result["worker_command"] = command
            result["worker_returncode"] = completed.returncode
            result["worker_stdout"] = completed.stdout.decode(errors="replace")
            result["worker_stderr"] = completed.stderr.decode(errors="replace")
            require(result_path.is_file(), "isolated verifier did not produce its report")
            result["verification"] = read_json(result_path)
            after_copy = tree_fingerprints(fresh)
            result["fresh_copy_changed_paths"] = sorted(
                p for p in copied.keys() | after_copy.keys() if copied.get(p) != after_copy.get(p))
            require(not result["fresh_copy_changed_paths"], "isolated verifier mutated/recreated checkout files")
            require(completed.returncode == 0 and result["verification"]["status"] == "PASS",
                    "isolated retained-inventory verification failed")
        result["status"] = "PASS"
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
        result["traceback"] = traceback.format_exc()
    finally:
        protected_after = {}
        for relative in protected_before:
            try:
                protected_after[relative] = fingerprint(ROOT / relative)
            except OSError as error:
                protected_after[relative] = {"error": str(error)}
        result["protected_before"] = protected_before
        result["protected_after"] = protected_after
        result["protected_changed_paths"] = sorted(
            p for p in protected_before if protected_before[p] != protected_after[p])
        if result["protected_changed_paths"]:
            result["status"] = "FAIL"
        result["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        result["elapsed_seconds"] = time.monotonic() - timer
        write_new(output, result)
    print(json.dumps({"status": result["status"], "report": output.relative_to(ROOT).as_posix()}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
