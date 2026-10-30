#!/usr/bin/env python3
"""Prove this milestone preserved its mapping and historical authorities."""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import copy
import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess

from openpyxl import load_workbook

from current_source_identity import (ROOT, SOURCES, TARGETS, PRODUCTS, WORKBOOK,
                                     ACCEPTED_CHECKPOINT_HEAD, checkpoint_errors,
                                     fingerprint, git, validated_product_evolution)
from current_semantic_workbook import validate_workbook_evolution
from current_documentary_workbook import semantic_projection_sha256

BASELINE = ROOT / "reports/current-publication-baseline.json"
# These are the independently accepted pre-repair repository identities. A
# candidate report is evidence to check, never permission to replace either.
EXPECTED_BASELINE_HEAD = "c3f9b05593727bd13854bf1830cc09b4a653b41f"
EXTERNAL_COMS_HEAD = "f391a9201398dc0f9954f3cb08ffb0354a9e0f6d"
EXTERNAL_COMS_ROOT = ROOT.parent / "CommonOntologyMappingSpecification"
# These reports already acquired historical-context banners or current COMS
# identity-report corrections in the audited candidate. They are not
# byte-preserved historical semantic authorities.
DOCUMENTARY_REPORTS = {
    "reports/current-full-sosa-baseline-summary.md",
    "reports/current-ssn-sosa-release-readiness-audit.md",
    "reports/coms-generation-validation.md",
    "reports/coms-product-dispositions.json",
}
PROTECTED_PATH_PREFIXES = (
    "rules/", "imports/", "src/sosa-next/", "releases/sosa-next/",
    "releases/current-ssn-sosa/", "mappings/SOSA-next", "config/sosa-",
    "queries/sosa-", "legacy/", "tools/coms_", "docs/COMS-",
)
CHECKPOINT_EVIDENCE_PREFIXES = (
    "reports/current-human-decisions/", "reports/current-documentary-workbook/",
)
CHECKPOINT_EVIDENCE_FILES = {
    "config/current-documentary-workbook-baseline.json",
    "config/current-ssn-sosa-identity.json",
    "config/current-ssn-sosa-historical-finals.json",
    "mappings/current-ssn-sosa-assessment.json",
}
ASSESSMENT = "mappings/current-ssn-sosa-assessment.json"


@lru_cache(maxsize=8)
def trusted_tree(root: Path, head: str) -> dict[str, dict]:
    """Read the complete immutable blob inventory, independent of JSON/index."""
    listing = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "-z", head])
    objects = []
    for item in listing.split(b"\0"):
        if not item:
            continue
        metadata, path = item.split(b"\t", 1)
        _mode, kind, oid = metadata.decode().split()
        if kind != "blob":
            raise ValueError(f"unsupported protected Git object: {path.decode()}")
        objects.append((path.decode(), oid))
    raw = subprocess.check_output(["git", "-C", str(root), "cat-file", "--batch"],
                                  input="".join(oid + "\n" for _, oid in objects).encode())
    result, offset = {}, 0
    for path, oid in objects:
        end = raw.index(b"\n", offset)
        actual_oid, kind, size = raw[offset:end].decode().split()
        if actual_oid != oid or kind != "blob":
            raise ValueError(f"missing trusted Git blob: {path}")
        data = raw[end + 1:end + 1 + int(size)]
        result[path] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        offset = end + 2 + int(size)
    return result


def protected_groups(baseline: dict | None = None, root: Path = ROOT) -> dict[str, list[str]]:
    """Keep the original tree and additive accepted-checkpoint evidence."""
    paths = trusted_tree(root, EXPECTED_BASELINE_HEAD)
    checkpoint = trusted_tree(root, ACCEPTED_CHECKPOINT_HEAD)
    sosa_paths = [p for p in paths if p.startswith(("src/sosa-next/", "releases/sosa-next/", "mappings/SOSA-next", "config/sosa-", "queries/sosa-", "reports/sosa-"))]
    return {
        "current_mapping_semantics": [WORKBOOK, *PRODUCTS, *[p for p in paths if p.startswith("rules/")]],
        "current_sources_and_targets": [*SOURCES, *TARGETS],
        "pinned_sosa_2023": sosa_paths,
        "historical_authorities": [p for p in paths if p.startswith("legacy/") or
                                   (p.startswith("reports/") and p not in DOCUMENTARY_REPORTS and p not in sosa_paths)],
        "local_coms_architecture": [p for p in paths if p.startswith(("tools/coms_", "docs/COMS-"))],
        "checkpoint_custody_evidence": [p for p in checkpoint if p not in paths and
                                        (p.startswith(CHECKPOINT_EVIDENCE_PREFIXES) or
                                         p in CHECKPOINT_EVIDENCE_FILES)],
    }


def compare(paths: list[str], expected: dict, root: Path) -> list[str]:
    return [p for p in paths if (root / p).is_symlink() or not (root / p).is_file()
            or fingerprint(root / p) != expected[p]]


def retained_historical_reports(root: Path, paths: list[str], expected: dict) -> dict:
    """Preserve historical report bytes without treating them as live outputs.

    Eligibility comes from canonical workflow output registries. Protected
    decisions, sources, workbooks and products still use their own strict gates.
    Current report freshness remains a separate, live-byte validation.
    """
    from check_coms_mapping import MAINTAINED_OUTPUTS, REPO_ROOT
    from current_semantic_validation import REPORT_PATH
    import current_retained_evidence as retained

    regenerable = {p.relative_to(REPO_ROOT).as_posix() for p in MAINTAINED_OUTPUTS.values()
                   if p.relative_to(REPO_ROOT).parts[0] == "reports"}
    regenerable.update((REPORT_PATH.as_posix(), REPORT_PATH.with_suffix(".md").as_posix()))
    result = {}
    for path in sorted(set(paths) & regenerable):
        historical = retained.resolve(root, path, expected[path]["sha256"])
        if fingerprint(historical) != expected[path]:
            raise ValueError(f"retained historical report differs from trusted Git bytes: {path}")
        if historical != root / path:
            result[path] = {"historical_snapshot_path": historical.relative_to(root).as_posix(),
                            "sha256": expected[path]["sha256"],
                            "live_sha256": fingerprint(root / path)["sha256"]
                            if (root / path).is_file() else None}
    return result


def inventory_errors(recorded: dict, expected: dict, label: str) -> list[str]:
    """An omitted or forged baseline entry must fail even if bytes are intact."""
    errors = []
    if set(recorded) != set(expected):
        errors.append(f"{label}: missing or extra paths relative to trusted Git tree")
    for path in sorted(set(recorded) & set(expected)):
        value = recorded[path]
        sha256 = value.get("sha256") if isinstance(value, dict) else value
        if sha256 != expected[path]["sha256"] or (isinstance(value, dict) and value.get("bytes") != expected[path]["bytes"]):
            errors.append(f"{label}: {path}: mutable hash differs from trusted Git blob")
    return errors


def workbook_counts(root: Path, head: str, path: str) -> dict:
    data = subprocess.check_output(["git", "-C", str(root), "show", f"{head}:{path}"])
    book = load_workbook(BytesIO(data), read_only=True, data_only=True)
    result = {}
    for sheet in book:
        rows = list(sheet.values)
        headers = list(rows[0])
        records = [dict(zip(headers, row)) for row in rows[1:] if any(value is not None for value in row)]
        result[sheet.title] = {
            "row_count": len(records), "headers": headers,
            "predicate_counts": dict(Counter(str(row.get("sssom:predicate_id") or "") for row in records)),
            "mapping_status_counts": dict(Counter(str(row.get("coms:MappingStatus") or "") for row in records)),
        }
    book.close()
    return result


def validated_assessment_evolution(root: Path, historical: dict, candidate: dict) -> dict:
    """Derive only RowID maintenance and newly authenticated human finals.

    The accepted assessment remains the starting authority. A transition's
    existence alone cannot authorize an assessment edit: each new final must
    name the exact human artifact bound by that explicit-decision transition.
    """
    import current_assessment as assessment
    import current_documentary_workbook as documentary
    import current_semantic_workbook as semantic

    derived = assessment.evolve_unreviewed_row_ids(root, historical)
    if candidate == derived:
        return {"new_human_decisions": []}
    if (not isinstance(candidate, dict)
            or {k: v for k, v in candidate.items() if k != "records"}
            != {k: v for k, v in derived.items() if k != "records"}
            or not isinstance(candidate.get("records"), list)
            or len(candidate["records"]) != len(derived["records"])):
        raise ValueError("assessment evolution changed inventory metadata or record membership")
    history = semantic.resolve_history(root)
    adopted = []
    for before, current in zip(derived["records"], candidate["records"]):
        if before == current:
            continue
        iri = before["source_iri"]
        if (before["review_state"] not in {"unreviewed", "deferred"}
                or before["assessment_outcome"] != before["review_state"]
                or before.get("human_decision_record")):
            raise ValueError(f"assessment evolution cannot alter an accepted final: {iri}")
        if not isinstance(current, dict) or current.get("source_iri") != iri:
            raise ValueError("assessment evolution changed record order or subject")
        ref = current.get("human_decision_record")
        decision = documentary._json(documentary._bound_file(root, ref))
        matches = []
        for transition in history["chain"]:
            if transition["kind"] != "semantic":
                continue
            authorities = [authority for row_id, authority in transition["authorities"].items()
                           if row_id in before["mapping_row_ids"]
                           and authority.get("authorization_type") == "EXPLICIT_NEW_HUMAN_DECISION"
                           and authority.get("human_decision") == ref]
            if authorities:
                matches.append(transition)
        if len(matches) != 1:
            raise ValueError(f"new final lacks one exact explicit-human transition authority: {iri}")
        transition = matches[0]
        if (decision.get("source_iri") != iri or decision.get("review_state") != "final"
                or decision.get("assessment_outcome") not in assessment.FINAL_OUTCOMES
                or decision.get("input_hashes", {}).get("workbook_sha256")
                != transition["new_workbook_sha256"]):
            raise ValueError(f"new final is not bound to the transition's selected workbook: {iri}")
        snapshot = documentary._json(documentary._bound_file(root, decision.get("assessment_snapshot")))
        prior = [r for r in snapshot.get("records", []) if r.get("source_iri") == iri]
        if prior != [before]:
            raise ValueError(f"new final pre-decision assessment differs from trusted assessment: {iri}")
        expected = copy.deepcopy(before)
        expected.update(review_state="final", assessment_outcome=decision["assessment_outcome"],
                        rationale=decision.get("rationale"), evidence=decision.get("evidence_refs"),
                        human_decision_record=ref)
        if decision["assessment_outcome"] == "inheritance_sufficient":
            expected["inheritance_sufficiency_evidence"] = decision.get("inheritance_sufficiency_evidence")
        if current != expected:
            raise ValueError(f"new final changed fields outside its exact human decision: {iri}")
        adopted.append({"source_iri": iri, "human_decision_record": ref,
                        "transition_id": transition["transition_id"]})

    _authenticate_current_assessment(root, candidate)
    return {"new_human_decisions": adopted}


def _authenticate_current_assessment(root: Path, candidate: dict) -> None:
    # The established validator authenticates the complete packet, source and
    # target identities, sufficiency evidence, and current applicability. Its
    # project paths predate the root-parameterized custody helpers; bind them
    # narrowly for a disposable checkout and restore them even on rejection.
    import current_assessment as assessment
    names = ("ROOT", "SCOPE", "ASSESSMENT", "SOURCE_QUERY", "HISTORICAL_FINAL_BASELINE")
    saved = {name: getattr(assessment, name) for name in names}
    try:
        for name, value in saved.items():
            setattr(assessment, name, root if name == "ROOT" else root / value.relative_to(saved["ROOT"]))
        scope = json.loads(assessment.SCOPE.read_text())
        graph = assessment.source_graph()
        rows, stats = assessment.mapping.read_workbook(root / WORKBOOK)
        processed = assessment.mapping.validate_and_process_rows(rows, assessment.mapping.Resolver(root=root), stats)
        assessment.validate(scope, candidate["records"], graph, processed)
    finally:
        for name, value in saved.items():
            setattr(assessment, name, value)


def preservation(root: Path = ROOT, baseline: dict | None = None) -> dict:
    baseline = json.loads((root / BASELINE.relative_to(ROOT)).read_text()) if baseline is None else baseline
    original = trusted_tree(root, EXPECTED_BASELINE_HEAD)
    expected = dict(original)
    checkpoint = trusted_tree(root, ACCEPTED_CHECKPOINT_HEAD)
    expected.update({p: checkpoint[p] for p in protected_groups(root=root)["checkpoint_custody_evidence"]})
    errors = inventory_errors(baseline.get("tracked_files", {}), original, "baseline inventory")
    if baseline.get("head") != EXPECTED_BASELINE_HEAD:
        errors.append("mutable baseline HEAD differs from trusted baseline HEAD")
    # Include staged additions and ordinary untracked semantic files, while
    # respecting ignored generated build trees and new publication reports.
    candidate_paths = set(git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")) - {""}
    extra_paths = sorted(p for p in candidate_paths - set(expected) if p.startswith(PROTECTED_PATH_PREFIXES))
    errors.extend(f"extra protected path absent from trusted Git tree: {path}" for path in extra_paths)
    groups = {name: {"file_count": len(paths), "changed_paths": compare(paths, expected, root),
                     "expected_sha256": {p: expected[p]["sha256"] for p in paths}}
              for name, paths in protected_groups(root=root).items()}
    retained_reports = {}
    try:
        retained_reports = retained_historical_reports(
            root, groups["historical_authorities"]["changed_paths"], expected)
        for path in retained_reports:
            groups["historical_authorities"]["changed_paths"].remove(path)
    except (ValueError, OSError) as exc:
        errors.append(f"historical report custody: {exc}")
    workbook_evolution = {
        "status": "NOT_NEEDED", "workbook_path": WORKBOOK,
        "historical_sha256": expected[WORKBOOK]["sha256"],
        "current_sha256": fingerprint(root / WORKBOOK)["sha256"] if (root / WORKBOOK).is_file() else None,
    }
    if WORKBOOK in groups["current_mapping_semantics"]["changed_paths"]:
        # The original Git blob remains the trust root. Documentary or semantic
        # transitions explain later workbook bytes without redefining history.
        try:
            if (root / WORKBOOK).is_symlink():
                raise ValueError("documentary workbook may not be a symlink")
            historical = validate_workbook_evolution(root, expected[WORKBOOK]["sha256"], root / WORKBOOK)
            if fingerprint(historical) != expected[WORKBOOK]:
                raise ValueError("retained historical workbook differs from trusted Git blob")
            groups["current_mapping_semantics"]["changed_paths"].remove(WORKBOOK)
            workbook_evolution.update(status="VALIDATED", semantic_projection_preserved=(
                                          semantic_projection_sha256(historical) ==
                                          semantic_projection_sha256(root / WORKBOOK)),
                                      historical_snapshot_path=str(historical.relative_to(root)))
        except (ValueError, OSError, TypeError) as exc:
            workbook_evolution.update(status="FAIL", error=str(exc))
    product_evolution = {"status": "NOT_NEEDED"}
    changed_products = [path for path in PRODUCTS
                        if path in groups["current_mapping_semantics"]["changed_paths"]]
    if changed_products or workbook_evolution.get("semantic_projection_preserved") is False:
        try:
            product_evolution = validated_product_evolution(root, {path: original[path] for path in PRODUCTS})
            for path in changed_products:
                groups["current_mapping_semantics"]["changed_paths"].remove(path)
        except (ValueError, OSError, TypeError) as exc:
            product_evolution = {"status": "FAIL", "error": str(exc)}
            errors.append(f"semantic product evolution: {exc}")
    assessment_evolution = {"status": "NOT_NEEDED"}
    assessment_changed = ASSESSMENT in groups["checkpoint_custody_evidence"]["changed_paths"]
    if assessment_changed or workbook_evolution.get("semantic_projection_preserved") is False:
        try:
            from current_assessment import json_text
            historical_assessment = subprocess.check_output(
                ["git", "-C", str(root), "show", f"{ACCEPTED_CHECKPOINT_HEAD}:{ASSESSMENT}"])
            candidate = root / ASSESSMENT
            if candidate.is_symlink() or not candidate.is_file():
                raise ValueError("assessment must be a retained regular file")
            document = json.loads(candidate.read_text())
            if candidate.read_bytes() != json_text(document).encode("utf-8"):
                raise ValueError("assessment differs from canonical inventory serialization")
            advancement = validated_assessment_evolution(root, json.loads(historical_assessment), document)
            if assessment_changed:
                groups["checkpoint_custody_evidence"]["changed_paths"].remove(ASSESSMENT)
            assessment_evolution = {"status": "VALIDATED", "historical_head": ACCEPTED_CHECKPOINT_HEAD,
                                    "historical_sha256": expected[ASSESSMENT]["sha256"],
                                    "current_sha256": fingerprint(candidate)["sha256"], **advancement}
        except (ValueError, OSError, TypeError) as exc:
            assessment_evolution = {"status": "FAIL", "error": str(exc)}
            errors.append(f"assessment RowID evolution: {exc}")
    external = baseline.get("external_coms", {})
    if external.get("head") != EXTERNAL_COMS_HEAD or external.get("path") != str(EXTERNAL_COMS_ROOT):
        errors.append("external COMS mutable identity differs from trusted repository identity")
    if EXTERNAL_COMS_ROOT.is_dir():
        external_expected = trusted_tree(EXTERNAL_COMS_ROOT, EXTERNAL_COMS_HEAD)
        external_errors = inventory_errors(external.get("tracked_file_hashes", {}), external_expected, "external COMS inventory")
        changes = compare(list(external_expected), external_expected, EXTERNAL_COMS_ROOT)
        external_head = git(EXTERNAL_COMS_ROOT, "rev-parse", "HEAD")
        index_paths = set(git(EXTERNAL_COMS_ROOT, "ls-files", "-z").split("\0")) - {""}
        if index_paths != set(external_expected):
            external_errors.append("external COMS tracked path inventory differs from trusted Git tree")
        if changes or external_head != EXTERNAL_COMS_HEAD:
            external_errors.append("external COMS checkout differs from its trusted Git tree")
        errors.extend(external_errors)
        external_result = {
            "status": "FAIL" if external_errors else "PASS", "baseline_head": EXTERNAL_COMS_HEAD,
            "head": external_head, "changed_paths": changes, "errors": external_errors,
            "tracked_file_count": len(external_expected),
        }
    else:
        external_result = {"status": "NOT_CHECKED", "baseline_head": EXTERNAL_COMS_HEAD,
                           "reason": "Recorded external editable COMS checkout is not present on this host"}
    errors.extend(f"{name}: {path}" for name, group in groups.items() for path in group["changed_paths"])
    current_head = git(root, "rev-parse", "HEAD")
    errors.extend(checkpoint_errors(root))
    counts = {p: workbook_counts(root, EXPECTED_BASELINE_HEAD, p)
              for p in expected if p.startswith("mappings/SOSA-next") and p.endswith(".xlsx")}
    for path, value in counts.items():
        if baseline.get("workbook_baselines", {}).get(path) != value:
            errors.append(f"{path}: recorded workbook baseline counts differ from trusted Git bytes")
    return {"baseline_head": EXPECTED_BASELINE_HEAD, "accepted_checkpoint_head": ACCEPTED_CHECKPOINT_HEAD,
            "head": current_head,
            "branch": git(root, "branch", "--show-current"), "groups": groups,
            "external_coms": external_result, "errors": errors,
            "status": "FAIL" if errors else ("PASS" if external_result["status"] == "PASS" else "NOT_CHECKED"),
            "proof_basis": "Original protected paths and hashes remain derived from the c3 baseline Git tree. Additive decision and documentary custody evidence is pinned to the accepted dc checkpoint. Governed workbook history may advance current products only when all four match deterministic validated generation; historical identities remain unchanged. Mutable baseline inventory/hashes cannot replace either trust root. External COMS is checked against its own pinned Git tree.",
            "documentary_workbook_evolution": workbook_evolution,
            "semantic_product_evolution": product_evolution,
            "assessment_row_id_evolution": assessment_evolution,
            "retained_historical_evidence": retained_reports,
            "documentary_report_exclusions": sorted(DOCUMENTARY_REPORTS),
            "sosa_2023_workbook_baseline_counts": counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = preservation()
    if args.write:
        (ROOT / "reports/current-publication-preservation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return int(result["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
