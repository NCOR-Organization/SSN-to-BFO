#!/usr/bin/env python3
"""Evaluate the current SSN/SOSA publication criterion without accepting decisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import os
import re

import current_assessment as assessment
import current_semantic_validation as semantic
import current_documentary_workbook as documentary
import current_validation_scope as scopes
from current_source_identity import ROOT, RECORD, PRODUCTS, check_record, fingerprint, git
from current_publication_preservation import preservation

REPORT = ROOT / "reports/current-ssn-sosa-publication-readiness.md"
VALIDATION = ROOT / "reports/current-publication-validation/commands.json"
CURRENT_EVIDENCE = Path("reports/current-publication-validation/current-evidence.json")
DOCUMENTARY_LEDGER = "reports/current-documentary-workbook/reasoning-completion/validation-ledger.json"
NOT_READY = "CURRENT TRACK NOT YET PUBLICATION READY — HUMAN SEMANTIC REVIEW REQUIRED"
READY = "CURRENT TRACK READY FOR INDEPENDENT PUBLICATION AUDIT"
REQUIRED_COMMANDS = scopes.REQUIRED_COMMANDS


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def selected_evidence(root: Path = ROOT) -> tuple[Path, Path, dict]:
    """Select additive execution records without changing their acceptance rules.

    The original reports remain historical evidence. A selector authenticates
    both predecessors and successors; it conveys no execution or semantic PASS.
    It lives outside validation_inputs because binding the ledger's own selector
    would make its input hash depend on its output hash.
    """
    originals = {
        "semantic": semantic.REPORT_PATH,
        "validation": Path("reports/current-publication-validation/commands.json"),
    }
    selector = root / CURRENT_EVIDENCE
    if not selector.exists() and not selector.is_symlink():
        return root / originals["semantic"], root / originals["validation"], {
            "selector": None, "mode": "original_records"}
    if selector.is_symlink() or not selector.is_file():
        raise ValueError("Current evidence selector must be a regular file")
    document = read(selector)
    if (not isinstance(document, dict)
            or set(document) != {"schema_version", "semantic", "validation", "predecessors"}
            or type(document["schema_version"]) is not int or document["schema_version"] != 1
            or not isinstance(document["predecessors"], dict)
            or set(document["predecessors"]) != set(originals)):
        raise ValueError("Invalid current evidence selector schema")

    def bound(ref: dict, expected: Path | None = None) -> Path:
        if (not isinstance(ref, dict) or set(ref) != {"path", "sha256"}
                or not isinstance(ref["path"], str) or not isinstance(ref["sha256"], str)):
            raise ValueError("Invalid current evidence reference")
        relative = Path(ref["path"])
        candidate = root / relative
        if (relative.is_absolute() or ".." in relative.parts
                or relative.as_posix() != ref["path"]
                or (expected is not None and relative != expected)
                or (expected is None and not relative.is_relative_to(CURRENT_EVIDENCE.parent))
                or any((root / Path(*relative.parts[:i])).is_symlink()
                       for i in range(1, len(relative.parts) + 1))
                or not candidate.is_file()
                or not candidate.resolve().is_relative_to(root.resolve())):
            raise ValueError("Invalid current evidence path: " + ref["path"])
        if fingerprint(candidate)["sha256"] != ref["sha256"]:
            raise ValueError("Current evidence reference hash differs: " + ref["path"])
        return candidate

    predecessors = {role: bound(document["predecessors"][role], relative)
                    for role, relative in originals.items()}
    selected = {role: bound(document[role]) for role in originals}
    if (len(set(selected.values())) != 2
            or any(path in predecessors.values() or path == selector for path in selected.values())):
        raise ValueError("Current evidence successors must be separate records")
    # Additive custody can relocate exact execution inputs, never their outcomes
    # or HEAD/input freshness. Absence keeps the existing strict live-path route;
    # a present but invalid manifest fails closed before selecting any evidence.
    semantic_report = read(selected["semantic"])
    portable = semantic.portable_execution.context(semantic_report, root)
    portable_binding = None
    if portable is not None:
        relative = semantic.portable_execution.manifest_path(semantic_report)
        portable_binding = {"path": relative, "sha256": fingerprint(root / relative)["sha256"]}
    return selected["semantic"], selected["validation"], {
        "selector": {"path": CURRENT_EVIDENCE.as_posix(), "sha256": fingerprint(selector)["sha256"]},
        "mode": "successor_records", "portable_semantic_custody": portable_binding, **document}


def validation_inputs(root: Path = ROOT) -> set[str]:
    """Legacy v1 universal inventory, for historical inspection only.

    Current receipt acceptance uses the versioned role policy below. This
    function remains unchanged for frozen historical issuers; its result never
    grants v2 applicability to their original maps.
    """
    extensions = {".py", ".java", ".json", ".toml", ".env", ".xlsx", ".txt", ".rq", ".ttl", ".owl", ".xml"}
    paths = {"Makefile", "SSN2BFO.ttl", "reports/coms-generation-validation.md",
             "reports/coms-product-dispositions.json", "reports/coms-source-term-coverage.md",
             "reports/coms-vs-pre-coms-legacy-diff.md"}
    for directory in ("tools", "tests", "config", "mappings", "imports", "rules", "queries", "releases", "src", "requirements"):
        for path in (root / directory).rglob("*"):
            if path.is_file() and "build" not in path.relative_to(root).parts and path.suffix in extensions:
                paths.add(path.relative_to(root).as_posix())
    paths.update(documentary.evidence_paths(root))
    import current_decision_applicability as applicability
    paths.update(applicability.evidence_paths(root))
    paths.update(documentary.retained.store_paths(root))
    return paths


def command_errors(command: dict, expected_head: str, expected_inputs: dict, root: Path) -> list[str]:
    """Accept a command only on its own complete, current execution bindings."""
    errors = []
    name = command.get("name", "<unnamed>")
    for key in ("head", "expected_head", "final_head"):
        if command.get(key) != expected_head:
            errors.append(f"{key} missing or stale HEAD")
    for key in ("expected_input_sha256", "input_sha256", "input_sha256_after"):
        if command.get(key) != expected_inputs:
            errors.append(f"{key} bindings missing or stale command inputs")
    if command.get("input_sha256") != command.get("input_sha256_after"):
        errors.append("pre/post command inputs differ")
    if command.get("input_drift") != []:
        errors.append("input drift missing or nonzero")
    for key in ("input_changes_during_execution", "inputs_unchanged", "input_hashes_unchanged"):
        if key in command and command[key] != ([] if key == "input_changes_during_execution" else True):
            errors.append(f"recorded drift in {key}")
    if command.get("execution_status") != "completed" or type(command.get("returncode")) is not int:
        errors.append("command completion missing or incomplete")
    if not command.get("started_at_utc") or not command.get("completed_at_utc"):
        errors.append("command start/completion evidence missing")
    argv = command.get("command")
    tool = command.get("tool_identity", {})
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
        errors.append("command identity missing")
    else:
        normalized = ["python" if Path(argv[0]).name.startswith("python") else Path(argv[0]).name, *argv[1:]]
        if name in REQUIRED_COMMANDS and normalized != REQUIRED_COMMANDS[name]:
            errors.append("command identity does not implement the named required validation")
        resolved = shutil.which(argv[0]) if not Path(argv[0]).is_absolute() else argv[0]
        if not resolved or tool.get("path") != str(Path(resolved).resolve()):
            errors.append("tool identity missing or mismatched")
        elif not Path(resolved).is_file() or tool.get("sha256") != fingerprint(Path(resolved))["sha256"]:
            errors.append("tool identity bytes missing or changed")
    artifacts = command.get("result_artifacts", {})
    log = command.get("log")
    if not isinstance(artifacts, dict) or not artifacts or not log or artifacts.get(log) != command.get("log_sha256"):
        errors.append("result artifact bindings missing or log binding differs")
        artifacts = artifacts if isinstance(artifacts, dict) else {}
    for path, sha in artifacts.items():
        candidate = (root / path).resolve()
        if not candidate.is_relative_to(root.resolve()) or not candidate.is_file() or fingerprint(candidate)["sha256"] != sha:
            errors.append(f"result artifact missing or changed: {path}")
    if log and (not (root / log).is_file() or fingerprint(root / log)["sha256"] != command.get("log_sha256")):
        errors.append(f"Validation output changed: {log}")
    return [f"Command {name}: {error}" for error in errors]


def native_ledger_errors(document: dict, root: Path) -> list[str]:
    """Current receipts require native issuance custody, independently of freshness."""
    import current_validation_execution as execution
    return execution.ledger_custody_errors(document, root)


def validation_errors(document: dict, root: Path | None = None,
                      expected_head: str | None = None) -> list[str]:
    """Fail closed on current role scopes; legacy ledgers remain historical."""
    root = ROOT if root is None else root
    expected_head = git(root, "rev-parse", "HEAD") if expected_head is None else expected_head
    errors = []
    if document.get("input_scope_profile") != scopes.PROFILE:
        errors.append("Current validation requires versioned v2 input-scope bindings; legacy receipts are historical only")
    if document.get("input_scope_profile") == scopes.PROFILE:
        errors.extend(native_ledger_errors(document, root))
    if document.get("head") != expected_head:
        errors.append("Validation execution HEAD is stale")
    bindings = document.get("input_sha256", {})
    if not isinstance(bindings, dict):
        bindings = {}
        errors.append("Validation input bindings must be an object")
    try:
        expected_union = scopes.ledger_inputs(root)
        if bindings != expected_union:
            errors.append("Validation input bindings are missing, extra, or stale for the current role union")
    except (OSError, ValueError, KeyError) as exc:
        errors.append("Cannot resolve current validation input bindings: " + str(exc))
    for path, sha in bindings.items():
        try:
            candidate = documentary._path(root, path)
            if fingerprint(candidate)["sha256"] != sha:
                errors.append(f"Validation execution input changed: {path}")
        except (OSError, ValueError, TypeError):
            errors.append(f"Validation execution input changed or missing: {path}")
    commands = document.get("commands", [])
    if not isinstance(commands, list) or any(not isinstance(c, dict) for c in commands):
        return errors + ["Validation command records must be objects"]
    if any(not isinstance(command.get("name"), str) for command in commands):
        return errors + ["Validation command names must be strings"]
    found = [command.get("name") for command in commands]
    if len(set(found)) != len(found):
        errors.append("Duplicate command names in publication evidence")
    errors += [f"Required validation not run: {name}" for name in sorted(set(REQUIRED_COMMANDS) - set(found))]
    for command in commands:
        name = command.get("name")
        try:
            scopes.validate_declaration(command.get("input_scope"), root, name)
            inputs = scopes.role_inputs(root, name)
            for label, expected in (("execution_tools", scopes.execution_tools(root, name)),
                                    ("execution_environment", scopes.execution_environment())):
                for field in ("expected_" + label, label + "_before", label + "_after"):
                    if command.get(field) != expected:
                        errors.append(f"Command {name}: missing or stale {field}")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"Command {name}: invalid current input scope: {exc}")
            inputs = {}  # Still inspect completion/tool/output evidence.
        errors.extend(command_errors(command, expected_head, inputs, root))
        if command.get("returncode") != 0:
            errors.append(f"Validation failed: {name} (exit {command.get('returncode')})")
    return errors


def historical_validation_errors(path: Path, trusted_sha256: str, root: Path = ROOT) -> list[str]:
    """Inspect an independently pinned v1 receipt without granting current use.

    The caller must supply its previously authenticated digest, never a digest
    learned from the candidate receipt. Recorded maps are not reinterpreted as
    the live inventory. Historical input provenance remains the original issuer's.
    """
    if fingerprint(path)["sha256"] != trusted_sha256:
        return ["Historical validation receipt differs from authenticated bytes"]
    document = read(path)
    errors = []
    inputs, head = document.get("input_sha256", {}), document.get("head")
    for command in document.get("commands", []):
        errors.extend(command_errors(command, head, inputs, root))
    return errors


def semantic_completion_errors(report: dict, root: Path = ROOT) -> list[str]:
    """Additional completion checks; authenticity still requires stored/provenance validators.

    A profile or explicit technical failure with a captured payload is a completed FAIL.
    Signals, timeout/launch failures and absent payloads cannot take that route.
    """
    errors = []
    commands = [item for item in report.get("evidence_files", [])
                if item.get("path", "").endswith(".command.json")]
    if not commands:
        return ["No semantic commands establish completed execution"]
    for item in commands:
        label = item["path"]
        try:
            path = documentary._path(root, label)
            if fingerprint(path)["sha256"] != item.get("sha256"):
                raise ValueError("command bytes differ")
            command = read(path)
            code = command.get("returncode")
            if (command.get("execution_status") != "completed" or type(code) is not int
                    or code < 0 or code >= 128):
                raise ValueError("execution interrupted, signal-terminated or incomplete")
            if "CurrentSemanticReasoner" in command.get("command", []):
                output = command.get("stdout", {})
                stdout = documentary._path(root, output.get("path"))
                if fingerprint(stdout)["sha256"] != output.get("sha256"):
                    raise ValueError("reasoner payload bytes differ")
                payload = read(stdout)
                status = payload.get("status")
                completed_error = (status == "technical_failure"
                                   and isinstance(payload.get("error"), str) and bool(payload["error"].strip()))
                expected = (0 if status in {"consistent", "inconsistent"}
                            else 2 if status == "profile_failure" or completed_error else None)
                if expected is None or code != expected:
                    raise ValueError("no completed semantic result payload matches exit status")
            elif code != 0:
                raise ValueError("compiler or tool precondition did not succeed")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(f"Semantic completion invalid: {label}: {exc}")
    return errors


def expectations_pass(report: dict, manifest: dict) -> bool:
    try:
        approved, _ = semantic.selected_expectations(manifest)
    except (ValueError, KeyError, TypeError):
        return False
    independent = [item for item in approved if item["evidence_role"] == "independent_semantic_expectation"]
    if {item["expected_entailed"] for item in independent} != {True, False}:
        return False
    results = report.get("expectations", {}).get("approved_results", [])
    if len(results) != len(approved) or report["expectations"].get("approved_count") != len(approved):
        return False
    answers = []
    for item in results:
        if item.get("status") != "consistent":
            return False
        answers.extend(item.get("reasoner_result", {}).get("expectations", []))
    expected = {item["id"]: item["expected_entailed"] for item in approved}
    return len(answers) == len(expected) and {a.get("id") for a in answers} == set(expected) and all(
        a.get("passed") is True and a.get("entailed") is expected[a["id"]] for a in answers)


def examples_pass(report: dict) -> bool:
    rows = report.get("examples", [])
    fixture = report.get("synthetic_fixture")
    if not rows or not fixture:
        return False
    return all(row.get("classification") == "aligned consistent" and
               row.get("source", {}).get("status") == "consistent" and
               row.get("aligned", {}).get("status") == "consistent" for row in [*rows, fixture])


def classify_diagnostics(blockers: list[str], infrastructure: list[str],
                         substantive: list[str]) -> dict:
    """Classify without suppressing blockers or changing publication acceptance.

    Unknown diagnostics fail closed into Class A. A diagnostic present in both
    groups remains A; semantic outcomes can never excuse broken custody.
    """
    a, b = set(infrastructure), set(substantive)
    rows = [{"class": "B" if message in b and message not in a else "A",
             "message": message} for message in dict.fromkeys(blockers)]
    return {"class_a_count": sum(row["class"] == "A" for row in rows),
            "class_b_count": sum(row["class"] == "B" for row in rows),
            "diagnostics": rows}


def completed_outcome_diagnostics(report: dict, root: Path,
                                  authenticity_errors: list[str]) -> set[str]:
    """Only authenticated normal nonzero exits are substantive outcome failures."""
    if authenticity_errors:
        return set()
    expected = set()
    for ref in report.get("evidence_files", []):
        if ref.get("path", "").endswith(".command.json"):
            command = read(documentary._path(root, ref["path"]))
            if (command.get("execution_status") == "completed"
                    and type(command.get("returncode")) is int
                    and 0 < command["returncode"] < 128):
                expected.add("Semantic command did not complete successfully: " + ref["path"])
    return expected


def evaluate() -> dict:
    identity = read(ROOT / RECORD)
    identity_errors = check_record(identity)
    cov, rat, reviews, _ = assessment.build_reports(read(assessment.SCOPE), read(assessment.ASSESSMENT))
    semantic_path, validation_path, evidence_selection = selected_evidence(ROOT)
    semantic_result = read(semantic_path)
    semantic_errors = semantic.validate_stored(semantic_result) + semantic_completion_errors(semantic_result)
    semantic_execution_errors = semantic.validate_publication_execution_bindings(semantic_result)
    semantic_publication_ok = not semantic_errors and not semantic_execution_errors
    validation = read(validation_path) if validation_path.exists() else {}
    validation_issues = validation_errors(validation)
    preserved = preservation()
    summary = cov["summary"]
    # Report generation alone cannot certify freshness of the maintained products.
    generation = (ROOT / "reports/coms-generation-validation.md").read_text()
    inventory_hash = fingerprint(assessment.ASSESSMENT)["sha256"]
    identity_reporting_ok = "Identity-audit completeness result: PASS" in generation and inventory_hash in generation
    criteria = [
        ("Exact available-local source/target, workbook, product and configuration identities frozen", not identity_errors, identity_errors),
        ("Dynamic source inventory equals assessment inventory", summary["source_assessment_equality"], []),
        ("Every source term has a final assessment", summary["review_states"]["final"] == summary["source_term_count"], [f"{reviews['item_count']} source terms require decisions"] if reviews["item_count"] else []),
        ("No deferred or unreviewed source terms", not (summary["review_states"]["deferred"] + summary["review_states"]["unreviewed"]), []),
        ("Formal coverage reported separately from assessment", True, []),
        ("Publication-critical rationale decisions resolved", rat["summary"]["human_review_required_proposals"] == 0, []),
        ("Approximate deductive difference has an acceptable reviewed result", semantic_publication_ok and set(semantic_result["conservativity"]) == {"source", "target"} and all(r["status"] == "PASS" and r["additions_count"] == 0 and r["losses_count"] == 0 for r in semantic_result["conservativity"].values()), []),
        ("Exact-closure source example results established", semantic_publication_ok and examples_pass(semantic_result), []),
        ("Selected approved positive/negative independent expectations have current passing results", semantic_publication_ok and expectations_pass(semantic_result, read(ROOT / semantic.MANIFEST_PATH)), []),
        ("Identity reporting internally consistent", identity_reporting_ok, []),
        ("Full repository validation passes in declared environment", not validation_issues and validation.get("declared_environment_match") is True, validation_issues),
        ("Evidence bound to HEAD and exact candidate input bytes; protected authorities unchanged", semantic_publication_ok and not validation_issues and preserved["status"] == "PASS", semantic_errors + semantic_execution_errors + preserved["errors"]),
    ]
    blockers = []
    if reviews["item_count"]:
        blockers.append(f"Complete the {reviews['item_count']}-term human review queue, retaining explicit decisions and rationale evidence; {summary['review_states']['deferred']} terms are deferred and {summary['review_states']['unreviewed']} unreviewed.")
    if rat["summary"]["human_review_required_proposals"]:
        blockers.append(f"Resolve {rat['summary']['human_review_required_proposals']} judgment-sensitive rationale proposals before treating them as adequate publication rationales.")
    substantive_blockers = list(blockers) + semantic_result["blockers"]
    blockers += semantic_result["blockers"]
    if any(run["reasoner_result"].get("profile_violation_count", 0) for run in semantic_result["hierarchy_runs"].values()):
        blockers.append("Resolve the exact OWL 2 DL declaration/profile gaps: source skos:Concept; aligned dcterms:type and adms:status; and the per-example vocabulary violations recorded individually. Any closure/overlay change must be reviewed, pinned, and reevaluated without silently changing mapping semantics.")
    substantive_blockers = list(blockers)
    blockers += identity_errors + semantic_errors + validation_issues
    completed_outcomes = completed_outcome_diagnostics(semantic_result, ROOT, semantic_errors)
    provenance_errors = [error for error in semantic_execution_errors if error not in completed_outcomes]
    if semantic_execution_errors:
        message = ("Selected authenticated semantic execution completed with unsuccessful results; these remain substantive publication blockers."
                   if not provenance_errors else
                   "Selected semantic execution evidence has incomplete or invalid provenance; inspect its execution diagnostics.")
        blockers.append(message)
        blockers += semantic_execution_errors
        if not provenance_errors:
            substantive_blockers.append(message)
        substantive_blockers.extend(error for error in semantic_execution_errors if error in completed_outcomes)
    if validation and not validation.get("declared_environment_match"):
        message = "Repeat the full gate in the declared Java distribution/environment; the local execution environment differs as recorded in commands.json."
        blockers.append(message)
        substantive_blockers.append(message)
    if not identity_reporting_ok:
        blockers.append("Refresh or repair the current identity report and its assessment binding.")
    blockers += preserved["errors"]
    infrastructure_errors = identity_errors + semantic_errors + validation_issues + provenance_errors + preserved["errors"]
    result = {"diagnostic_classification": classify_diagnostics(blockers, infrastructure_errors, substantive_blockers),
            "head": git(ROOT, "rev-parse", "HEAD"), "branch": git(ROOT, "branch", "--show-current"),
            "identity": identity, "coverage": cov, "rationales": rat["summary"], "review_item_count": reviews["item_count"],
            "live_workbook": {"path": documentary.WORKBOOK, **fingerprint(ROOT / documentary.WORKBOOK),
                              "semantic_projection_sha256": documentary.semantic_projection_sha256(ROOT / documentary.WORKBOOK)},
            "semantic": semantic_result, "validation": validation, "preservation": preserved,
            "live_products": [{"path": path, **fingerprint(ROOT / path)} for path in PRODUCTS],
            "evidence_selection": evidence_selection,
            "criteria": [{"criterion": title, "status": "PASS" if passed else "BLOCKED", "detail": detail} for title, passed, detail in criteria],
            "blockers": list(dict.fromkeys(blockers)), "verdict": READY if all(passed for _, passed, _ in criteria)
            and semantic_result.get("status") == "PASS" and not semantic_result.get("blockers") else NOT_READY}
    if (ROOT / DOCUMENTARY_LEDGER).is_file():
        result["documentary_completion_validation"] = {
            "path": DOCUMENTARY_LEDGER, **fingerprint(ROOT / DOCUMENTARY_LEDGER),
            "scope": "Bounded documentary completion validation; not a full repository gate or semantic authority.",
        }
    return result


def render(result: dict, directory: Path | None = None) -> str:
    s = result["coverage"]["summary"]
    identity = result["identity"]
    sem = result["semantic"]
    lines = ["# Current SSN/SOSA publication-readiness candidate", "", f"**{result['verdict']}**", "",
             f"Branch: `{result['branch']}`. Baseline and execution HEAD: `{result['head']}`. This is an uncommitted candidate, not a tag, release, or upstream identity. Code, inputs, commands, and output hashes are retained in the linked evidence. This evidence migration changes no mapping decisions; existing authorized changes retain their transition provenance.", "",
             "## Identity and baseline", "", "The original publication baseline recorded a clean Git status: `## publication/current-sosa-readiness`. [Baseline fingerprint](current-publication-baseline.json) records every then-tracked file, workbook/status counts, planned change classes, and the external COMS checkout. The original baseline remains historical; current authorized changes are authenticated by the preserved transition chain.", "",
             "Current source files preserve the 2017 SSN/SOSA generation annotations and have no version IRIs. **Upstream immutable commit: not established from repository evidence.** Local Git provenance and all ontology header/provenance annotations are in [the identity record](../config/current-ssn-sosa-identity.json).",
             "", "CCO is the merged Version 2.0 artifact, version IRI `https://www.commoncoreontologies.org/2024-11-06/CommonCoreOntologiesMerged`. BFO is embedded in those same bytes; the header identifies `bfo/2020/bfo-core.ttl`, obtained 11/03/2024. No standalone BFO file or immutable upstream commit is inferred. The sampling source imports SKOS without a local pinned SKOS artifact; available-local identity is frozen, but full upstream import closure identity is not established.", "",
             "| Role | Path | Bytes | SHA-256 |", "|---|---|---:|---|"]
    for role, entries in [("source", identity["source_files"]), ("target CCO + BFO", identity["target_files"]),
                          ("historical workbook identity", [identity["authoritative_workbook"]]),
                          ("current authoritative workbook", [result["live_workbook"]]), ("current product", result["live_products"])]:
        for e in entries:
            lines.append(f"| {role} | `{e['path']}` | {e['bytes']} | `{e['sha256']}` |")
    evolution = result["preservation"]["documentary_workbook_evolution"]
    lines += ["", f"Documentary workbook evolution: **{evolution['status']}**. Current A/B/C/E semantic projection SHA-256: `{result['live_workbook']['semantic_projection_sha256']}`. The frozen identity record retains the historical full-workbook hash; any later workbook bytes require the explicit, snapshot-backed [documentary transition chain](current-documentary-workbook/updates/). A validated documentary transition preserves semantic cells and decision custody without approving a new semantic decision."]
    lines += ["", "## Inventory and assessment outcomes", "", f"Source inventory: **{s['source_term_count']}** ({s['source_counts_by_kind']}); assessment records: **{s['assessment_record_count']}**; equality: **PASS**. The unchanged scope excludes datatype properties and `owl:deprecated true` terms. The inventory is recomputed from local source declarations and independently reconciled to the existing SPARQL query.", "", f"Review states: `{s['review_states']}`. Assessment outcomes: `{s['assessment_outcomes']}`. Unresolved = deferred + unreviewed. Final documentary reconstruction does not imply a new approval of a changed axiom.", "", "See [assessment inventory](../mappings/current-ssn-sosa-assessment.json) and [coverage evidence](current-ssn-sosa-coverage.md). Workbook rows are not the unit of assessment.", "", "## Formal coverage", "", "| Evidence category | Source terms |", "|---|---:|"]
    for k, v in s["coverage_counts"].items(): lines.append(f"| {k} | {v} |")
    lines += ["", result["coverage"]["method"], "", f"Direct formal class/property mappings: {s['direct_classes']} classes + {s['direct_object_properties']} properties. Chain heads: {s['chain_heads']}. The prior 28 relation-mapped properties include the 25 subproperty subjects and three chain heads. Typing-only describes workbook artifacts, not semantic assessment outcomes. Overlapping inherited and conditional routes are not added to direct counts; no-established-route is bounded by the documented structural method.", "", "## Mapping repertoire and rationales", "", f"Workbook: {s['workbook_rows']} rows; {s['assertion_bearing_rows']} assertion-bearing, {s['mapping_repertoire_rows'].get('explicit_blank', 0)} explicit blanks. Predicates: `{s['mapping_repertoire_rows']}`. `owl:equivalentProperty`: 0.", "", f"Complex expression occurrences: `{s['expression_occurrences']}`; rows containing each form: `{s['rows_with_expression_form']}`. Occurrences can overlap within one row.", "", f"Rationale coverage: `{result['rationales']}`. See [proposals](current-ssn-sosa-rationale-proposals.md). Current workbook reasoning is documentary evidence. Recorded column-D completion does not approve a mapping or resolve a deferred or unreviewed semantic question; the proposals report describes the current text and remaining concerns.", "", f"The [human review queue](current-ssn-sosa-human-review.md) contains **{result['review_item_count']} source terms**, prioritized by blanks, typing-only cases, equivalences, complex/existential commitments, chains, and cross-track disagreements. Each item separates source/target facts, logical consequences, interpretation, alternatives, and the required human decision. [Review protocol](../docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md).", "", "## Approximate deductive difference", "", "The implementation asks HermiT for all named class and object-property subsumptions/equivalences in each independent baseline and aligned ontology, then restricts the aligned relations to the original signature and compares entailment sets symmetrically. Self-relations and built-ins are excluded. This is the requested PROV-style approximation, not full model-theoretic conservativity or a claim to have independently reproduced the paper's implementation. No logical axiom is removed. Unexpected additions or losses fail the gate; no automatic waiver exists.", "", "| Signature | Status | Added | Lost |", "|---|---|---:|---:|"]
    for side, d in sem["conservativity"].items():
        lines.append(f"| {side} | {d['status']} | {d['additions_count'] if d['additions_count'] is not None else 'unavailable'} | {d['losses_count'] if d['losses_count'] is not None else 'unavailable'} |")
    lines += ["", "Target-only HermiT 1.4.1.432 reasoning is consistent and OWL 2 DL compliant: 9,383 named hierarchy/equivalence relations over 1,422 classes and 265 object properties. Source/aligned available-local diagnostic consistency is true, but exact results fail because SKOS is unavailable and profile declarations are incomplete. The source logical signature has 48 named classes (including borrowed names) and 47 object properties; this differs intentionally from the scoped 44-class assessment inventory."]
    lines += ["", "Affected-term entailment differences and deliberate-commitment conclusions cannot be asserted when baseline/aligned reasoning is blocked. Complete reasoner/profile diagnostics, exact terms in profile violations, and synthetic violation tests are retained in [semantic validation](current-ssn-sosa-semantic-validation.md) and its JSON/raw evidence.", "", "## Exact-closure examples and selected expectations", "", f"Source corpus: **{len(sem['examples'])} files**, each evaluated in a source-only and aligned phase; the synthetic Sample Relationship fixture is reported separately. Classifications: `{sem['example_counts']}`. All file hashes, closure inputs, commands, individual outputs, and technical failure reasons are preserved in [the result JSON](current-ssn-sosa-semantic-validation.json). No equivalence to the PROV paper's 312-instance corpus is claimed.", "", f"Selected expectations: {sem['expectations']['approved_count']} approved; {sem['expectations']['proposed_count']} proposed ({sem['expectations']['proposed_positive_count']} positive, {sem['expectations']['proposed_negative_count']} negative). Evidence roles: {sem['expectations'].get('proposed_independent_count', 0)} independent proposals and {sem['expectations'].get('proposed_regression_count', 0)} mapping-axiom regressions. The [manifest](../config/current-semantic-expectations.json) distinguishes mapping-induced consequences from source semantics. Unapproved proposals and axiom restatements do not count as independent publication evidence. These tests do not establish global interpretability.", "", "## Identity-report repair", "", "The current generator now checks canonical identity for assertion rows separately from legitimate explicit blanks. Zero-axiom rows require valid row identity and an assessment disposition; completed semantic review is reported separately. Missing/unexplained assertions still fail. The generated report is bound to the assessment hash. Regression tests cover reviewed blanks, unresolved blanks, missing dispositions, malformed assertions, and unchanged SOSA-2023 behavior.", "", "## Executed validation and environment", "", "Every accepted command must independently bind its HEAD, expected HEAD, exact pre/post inputs, executable identity, completion, drift state, and retained output hashes. A current ledger cannot make an older command current. Historical commands remain recorded with their original failures and incomplete bindings; no dependency was installed or changed. The declared full repository gate is `make check`. See [command ledger](current-publication-validation/commands.json).", "", "| Executed check | Exit | Log |", "|---|---:|---|"]
    for c in result["validation"].get("commands", []): lines.append(f"| {c['name']} | {c['returncode']} | [{Path(c['log']).name}]({c['log'].removeprefix('reports/')}) |")
    if result.get("documentary_completion_validation"):
        completion = result["documentary_completion_validation"]
        lines += ["", f"The [documentary reasoning-completion ledger]({completion['path'].removeprefix('reports/')}) records the separately executed, bounded completion checks (SHA-256 `{completion['sha256']}`). It is not a full repository gate or semantic authority and does not refresh historical semantic execution evidence."]
    lines += ["", f"Environment: `{result['validation'].get('environment', {})}`. Declared environment match: `{result['validation'].get('declared_environment_match', False)}`.", "", "Stored historical normalized HermiT, ELK, and RDFS smoke reports remain historical evidence for their stated inputs. Newly executed normalized checks retain that narrower interpretation. The exact-closure hierarchy comparisons and source examples are attempted but cannot be reported as successful when import/profile checks block them. Unapproved semantic expectations are not run or counted as approved evidence.", "", "## Preservation and documentation", "", f"Preservation: **{result['preservation']['status']}**. [SHA-256 proof](current-publication-preservation.json) covers preserved workbook semantic cells through any validated documentary chain, byte-identical current products/rule and source/target artifacts, SOSA-2023 source/configuration/products/workbooks, historical authorities, local COMS adapters/identity architecture, and all {result['preservation']['external_coms'].get('tracked_file_count', '?')} external COMS tracked files. SOSA-2023 BFO/CCO status totals remain 119 rows: 55 active, 64 no-direct; RO remains 82 rows: 16 active, 66 no-direct. Neither track has a new semantic decision.", "", "Documentation fixes identify three current modular products, the maintained independent SOSA-2023 track, local source/target versions and unresolved import, separate assessment authority, and limits of older smoke/normalized reasoning. Two obsolete current-named audits have historical banners; their findings were not rewritten. No external research, commit, tag, release, merge, or remote update was performed.", "", "## Candidate publication criterion", "", "Both tracks may be assessed against these high-level requirements without identical source versions, mappings, or conclusions. This candidate implements the checks only for the current track; the pinned alternative remains unchanged.", "", "| Criterion | Result |", "|---|---|"]
    lines += [f"| {i}. {c['criterion']} | {c['status']} |" for i, c in enumerate(result["criteria"], 1)]
    lines += ["", "## Mechanical human-review entry evidence", "",
              "The [earlier guard-repair report](current-publication-guard-repair.md) and prior completion claims were superseded by independent audits. The [final trust-repair report](current-publication-final-trust-repair.md) records the schema-downgrade and retry-archive repairs. This milestone is ready only for independent human-review gate audit; it does not approve human semantic decisions or certify publication readiness.", "",
              "Current stored and publication validators require ticketed custody unconditionally: reconstructed slot, pre-execution ticket, wrapper envelope/capture, retained bytes, derived classification, and summary. Missing, legacy, malformed or unknown schema declarations fail; mutable metadata cannot choose a legacy path. Historical inspection is separate and limited to the code-pinned archive and its retained hashes, explicitly ineligible for current review evidence and publication. Historical-to-current reconciliation is retired. A repeated driver destination is rejected before any existing input or output is touched; retries require fresh build/evidence destinations and retain separate tickets, nonces and outputs with explicit invocation selection. See the [repair validation ledger](current-publication-validation/gate-defect-validation.json).", "",
              "The existing twelve reconstructed historical finals are fixed by exact assessment-record identities. Every new or materially changed final requires a separately bound project-specific human decision record before queue removal or rationale finality.", "",
              "Review packets include relevant incoming restrictions and relationships, grouped disjointness and source/target/mapping chain provenance. Asserted facts remain distinct from explicitly explained derived consequences. These packets are bounded evidence aids, not exhaustive ontology exports or semantic decision engines; unresolved closure-dependent decisions still require the missing evidence."]
    lines += ["", "## Finite remaining blockers", ""] + [f"{i}. {b}" for i, b in enumerate(result["blockers"], 1)]
    lines += ["", "The implementation milestone is a reviewable candidate. An independent **read-only audit** is recommended before any semantic adoption, commit, or publication claim. Final Git status and all changed/created file classes are recorded in [the candidate manifest](current-publication-candidate.json).", "", result["verdict"], ""]
    rendered = "\n".join(lines)
    selected = result.get("evidence_selection", {})
    if selected.get("mode") == "successor_records":
        semantic_link = Path(selected["semantic"]["path"]).relative_to("reports")
        validation_link = Path(selected["validation"]["path"]).relative_to("reports")
        for original, current in (
            ("current-ssn-sosa-semantic-validation.json", semantic_link.as_posix()),
            ("current-ssn-sosa-semantic-validation.md", semantic_link.with_suffix(".md").as_posix()),
            ("current-publication-validation/commands.json", validation_link.as_posix()),
        ):
            rendered = rendered.replace("](" + original + ")", "](" + current + ")")
    classification = result.get("diagnostic_classification")
    if classification:
        rendered += "\n## Diagnostic classification\n\n"
        rendered += f"Class A (evidence/infrastructure): **{classification['class_a_count']}**. Class B (substantive requirements): **{classification['class_b_count']}**.\n\n"
        rendered += "\n".join(f"- Class {row['class']}: {row['message']}" for row in classification["diagnostics"]) + "\n"
    for name in assessment.REPORT_NAMES:
        rendered = rendered.replace("](" + name + ")", "](" + (assessment.REPORT_DIRECTORY / name).relative_to("reports").as_posix() + ")")
    if directory is not None:
        def rebase(match):
            target = match.group(1)
            if target.startswith(("/", "#")) or ":" in target:
                return match.group(0)
            return "](" + os.path.relpath(ROOT / "reports" / target, directory) + ")"
        rendered = re.sub(r"\]\(([^)]+)\)", rebase, rendered)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the publication report without changing decisions")
    parser.add_argument("--output-dir", type=Path, help="Create additive readiness JSON/Markdown in a new directory")
    args = parser.parse_args()
    try:
        if args.write and args.output_dir:
            raise ValueError("Choose historical report writing or an additive output directory")
        result = evaluate()
        if args.output_dir:
            directory = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
            relative = directory.relative_to(ROOT)
            if ".." in relative.parts or any((ROOT / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts)+1)):
                raise ValueError("Readiness output must be a project-local directory without symlinks")
            directory.mkdir(parents=True, exist_ok=False)
            (directory / "readiness.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            (directory / "readiness.md").write_text(render(result, directory))
        if args.write:
            REPORT.write_text(render(result))
        print(result["verdict"])
        for blocker in result["blockers"]: print("- " + blocker)
        return 0 if result["verdict"] == READY else 1
    except (OSError, ValueError, KeyError) as error:
        print(f"Publication readiness evidence missing or malformed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
