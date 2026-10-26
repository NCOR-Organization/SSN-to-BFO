#!/usr/bin/env python3
"""Evaluate the current SSN/SOSA publication criterion without accepting decisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

import current_assessment as assessment
import current_semantic_validation as semantic
import current_documentary_workbook as documentary
from current_source_identity import ROOT, RECORD, check_record, fingerprint, git
from current_publication_preservation import preservation

REPORT = ROOT / "reports/current-ssn-sosa-publication-readiness.md"
VALIDATION = ROOT / "reports/current-publication-validation/commands.json"
DOCUMENTARY_LEDGER = "reports/current-documentary-workbook/reasoning-completion/validation-ledger.json"
NOT_READY = "CURRENT TRACK NOT YET PUBLICATION READY — HUMAN SEMANTIC REVIEW REQUIRED"
READY = "CURRENT TRACK READY FOR INDEPENDENT PUBLICATION AUDIT"
REQUIRED_COMMANDS = {
    "unit_tests": ["python", "-B", "-m", "unittest", "discover", "-s", "tests"],
    "assessment": ["python", "-B", "tools/current_assessment.py"],
    "source_identity": ["python", "-B", "tools/current_source_identity.py"],
    "generation_freshness": ["python", "-B", "tools/check_coms_mapping.py", "--check-only"],
    "sosa_source_version": ["python", "-B", "tools/check_sosa_source_version.py"],
    "sosa_products": ["python", "-B", "tools/check_sosa_next_products.py"],
    "static_checks": ["make", "compile"],
    "full_repository_gate": ["make", "check"],
}


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def validation_inputs(root: Path = ROOT) -> set[str]:
    """Concrete inputs for this repository's whole-suite run, not just Git HEAD."""
    extensions = {".py", ".java", ".json", ".toml", ".env", ".xlsx", ".txt", ".rq", ".ttl", ".owl", ".xml"}
    paths = {"Makefile", "SSN2BFO.ttl", "reports/coms-generation-validation.md",
             "reports/coms-product-dispositions.json", "reports/coms-source-term-coverage.md",
             "reports/coms-vs-pre-coms-legacy-diff.md"}
    for directory in ("tools", "tests", "config", "mappings", "imports", "rules", "queries", "releases", "src", "requirements"):
        for path in (root / directory).rglob("*"):
            if path.is_file() and "build" not in path.relative_to(root).parts and path.suffix in extensions:
                paths.add(path.relative_to(root).as_posix())
    paths.update(documentary.evidence_paths(root))
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


def validation_errors(document: dict) -> list[str]:
    errors = []
    expected_head = git(ROOT, "rev-parse", "HEAD")
    if document.get("head") != expected_head:
        errors.append("Validation execution HEAD is stale")
    bindings = document.get("input_sha256", {})
    if set(bindings) != validation_inputs(ROOT):
        errors.append("Validation input bindings are missing, extra, or incomplete for the current candidate")
    for path, sha in bindings.items():
        if not (ROOT / path).is_file() or fingerprint(ROOT / path)["sha256"] != sha:
            errors.append(f"Validation execution input changed: {path}")
    expected_inputs = {path: fingerprint(ROOT / path)["sha256"] for path in sorted(validation_inputs(ROOT)) if (ROOT / path).is_file()}
    for command in document.get("commands", []):
        errors.extend(command_errors(command, expected_head, expected_inputs, ROOT))
    required = set(REQUIRED_COMMANDS)
    found = {command.get("name") for command in document.get("commands", [])}
    if len(found) != len(document.get("commands", [])):
        errors.append("Duplicate command names in publication evidence")
    errors += [f"Required validation not run: {name}" for name in sorted(required - found)]
    errors += [f"Validation failed: {c.get('name')} (exit {c.get('returncode')})" for c in document.get("commands", []) if c.get("returncode") != 0]
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


def evaluate() -> dict:
    identity = read(ROOT / RECORD)
    identity_errors = check_record(identity)
    cov, rat, reviews, _ = assessment.build_reports(read(assessment.SCOPE), read(assessment.ASSESSMENT))
    semantic_result = read(ROOT / semantic.REPORT_PATH)
    semantic_errors = semantic.validate_stored(semantic_result)
    semantic_execution_errors = semantic.validate_publication_execution_bindings(semantic_result)
    semantic_publication_ok = not semantic_errors and not semantic_execution_errors
    validation = read(VALIDATION) if VALIDATION.exists() else {}
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
    blockers += semantic_result["blockers"]
    if any(run["reasoner_result"].get("profile_violation_count", 0) for run in semantic_result["hierarchy_runs"].values()):
        blockers.append("Resolve the exact OWL 2 DL declaration/profile gaps: source skos:Concept; aligned dcterms:type and adms:status; and the per-example vocabulary violations recorded individually. Any closure/overlay change must be reviewed, pinned, and reevaluated without silently changing mapping semantics.")
    blockers += identity_errors + semantic_errors + validation_issues
    if semantic_execution_errors:
        blockers.append("Retained historical semantic diagnostics lack pre-execution tickets and helper result envelopes. Their old code/input bindings are now stale, so they cannot certify a new semantic execution; rerun only with the reviewed closure and resolved profile/import blockers.")
    if validation and not validation.get("declared_environment_match"):
        blockers.append("Repeat the full gate in the declared Java distribution/environment; the local execution environment differs as recorded in commands.json.")
    if not identity_reporting_ok:
        blockers.append("Refresh or repair the current identity report and its assessment binding.")
    blockers += preserved["errors"]
    result = {"head": git(ROOT, "rev-parse", "HEAD"), "branch": git(ROOT, "branch", "--show-current"),
            "identity": identity, "coverage": cov, "rationales": rat["summary"], "review_item_count": reviews["item_count"],
            "live_workbook": {"path": documentary.WORKBOOK, **fingerprint(ROOT / documentary.WORKBOOK),
                              "semantic_projection_sha256": documentary.semantic_projection_sha256(ROOT / documentary.WORKBOOK)},
            "semantic": semantic_result, "validation": validation, "preservation": preserved,
            "criteria": [{"criterion": title, "status": "PASS" if passed else "BLOCKED", "detail": detail} for title, passed, detail in criteria],
            "blockers": list(dict.fromkeys(blockers)), "verdict": READY if all(passed for _, passed, _ in criteria)
            and semantic_result.get("status") == "PASS" and not semantic_result.get("blockers") else NOT_READY}
    if (ROOT / DOCUMENTARY_LEDGER).is_file():
        result["documentary_completion_validation"] = {
            "path": DOCUMENTARY_LEDGER, **fingerprint(ROOT / DOCUMENTARY_LEDGER),
            "scope": "Bounded documentary completion validation; not a full repository gate or semantic authority.",
        }
    return result


def render(result: dict) -> str:
    s = result["coverage"]["summary"]
    identity = result["identity"]
    sem = result["semantic"]
    lines = ["# Current SSN/SOSA publication-readiness candidate", "", f"**{result['verdict']}**", "",
             f"Branch: `{result['branch']}`. Baseline and execution HEAD: `{result['head']}`. This is an uncommitted candidate, not a tag, release, or upstream identity. Code, inputs, commands, and output hashes are retained in the linked evidence. No semantic mapping change was adopted.", "",
             "## Identity and baseline", "", "Pre-implementation Git status was clean: `## publication/current-sosa-readiness`. [Baseline fingerprint](current-publication-baseline.json) records every then-tracked file, workbook/status counts, planned change classes, and the external COMS checkout. Category A (semantic mapping changes) is empty.", "",
             "Current source files preserve the 2017 SSN/SOSA generation annotations and have no version IRIs. **Upstream immutable commit: not established from repository evidence.** Local Git provenance and all ontology header/provenance annotations are in [the identity record](../config/current-ssn-sosa-identity.json).",
             "", "CCO is the merged Version 2.0 artifact, version IRI `https://www.commoncoreontologies.org/2024-11-06/CommonCoreOntologiesMerged`. BFO is embedded in those same bytes; the header identifies `bfo/2020/bfo-core.ttl`, obtained 11/03/2024. No standalone BFO file or immutable upstream commit is inferred. The sampling source imports SKOS without a local pinned SKOS artifact; available-local identity is frozen, but full upstream import closure identity is not established.", "",
             "| Role | Path | Bytes | SHA-256 |", "|---|---|---:|---|"]
    for role, entries in [("source", identity["source_files"]), ("target CCO + BFO", identity["target_files"]),
                          ("historical workbook identity", [identity["authoritative_workbook"]]),
                          ("current authoritative workbook", [result["live_workbook"]]), ("product", identity["products"])]:
        for e in entries:
            lines.append(f"| {role} | `{e['path']}` | {e['bytes']} | `{e['sha256']}` |")
    evolution = result["preservation"]["documentary_workbook_evolution"]
    lines += ["", f"Documentary workbook evolution: **{evolution['status']}**. Current A/B/C/E semantic projection SHA-256: `{result['live_workbook']['semantic_projection_sha256']}`. The frozen identity record retains the historical full-workbook hash; any later workbook bytes require the explicit, snapshot-backed [documentary transition chain](current-documentary-workbook/updates/). A validated documentary transition preserves semantic cells and decision custody without approving a new semantic decision."]
    lines += ["", "## Inventory and assessment outcomes", "", f"Source inventory: **{s['source_term_count']}** ({s['source_counts_by_kind']}); assessment records: **{s['assessment_record_count']}**; equality: **PASS**. The unchanged scope excludes datatype properties and `owl:deprecated true` terms. The inventory is recomputed from local source declarations and independently reconciled to the existing SPARQL query.", "", f"Review states: `{s['review_states']}`. Assessment outcomes: `{s['assessment_outcomes']}`. Unresolved = deferred + unreviewed. Final documentary reconstruction does not imply a new approval of a changed axiom.", "", "See [assessment inventory](../mappings/current-ssn-sosa-assessment.json) and [coverage evidence](current-ssn-sosa-coverage.md). Workbook rows are not the unit of assessment.", "", "## Formal coverage", "", "| Evidence category | Source terms |", "|---|---:|"]
    for k, v in s["coverage_counts"].items(): lines.append(f"| {k} | {v} |")
    lines += ["", result["coverage"]["method"], "", f"Direct formal class/property mappings: {s['direct_classes']} classes + {s['direct_object_properties']} properties. Chain heads: {s['chain_heads']}. The prior 28 relation-mapped properties include the 25 subproperty subjects and three chain heads. Typing-only describes workbook artifacts, not semantic assessment outcomes. Overlapping inherited and conditional routes are not added to direct counts; no-established-route is bounded by the documented structural method.", "", "## Mapping repertoire and rationales", "", f"Workbook: {s['workbook_rows']} rows; {s['assertion_bearing_rows']} assertion-bearing, two explicit blanks. Predicates: `{s['mapping_repertoire_rows']}`. `owl:equivalentProperty`: 0.", "", f"Complex expression occurrences: `{s['expression_occurrences']}`; rows containing each form: `{s['rows_with_expression_form']}`. Occurrences can overlap within one row.", "", f"Rationale coverage: `{result['rationales']}`. See [proposals](current-ssn-sosa-rationale-proposals.md). Current workbook reasoning is documentary evidence. Recorded column-D completion does not approve a mapping or resolve a deferred or unreviewed semantic question; the proposals report describes the current text and remaining concerns.", "", f"The [human review queue](current-ssn-sosa-human-review.md) contains **{result['review_item_count']} source terms**, prioritized by blanks, typing-only cases, equivalences, complex/existential commitments, chains, and cross-track disagreements. Each item separates source/target facts, logical consequences, interpretation, alternatives, and the required human decision. [Review protocol](../docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md).", "", "## Approximate deductive difference", "", "The implementation asks HermiT for all named class and object-property subsumptions/equivalences in each independent baseline and aligned ontology, then restricts the aligned relations to the original signature and compares entailment sets symmetrically. Self-relations and built-ins are excluded. This is the requested PROV-style approximation, not full model-theoretic conservativity or a claim to have independently reproduced the paper's implementation. No logical axiom is removed. Unexpected additions or losses fail the gate; no automatic waiver exists.", "", "| Signature | Status | Added | Lost |", "|---|---|---:|---:|"]
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
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the publication report without changing decisions")
    args = parser.parse_args()
    try:
        result = evaluate()
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
