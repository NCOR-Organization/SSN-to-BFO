#!/usr/bin/env python3
"""Prove this milestone preserved its mapping and historical authorities."""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess

from openpyxl import load_workbook

from current_source_identity import ROOT, SOURCES, TARGETS, PRODUCTS, WORKBOOK, fingerprint, git
from current_documentary_workbook import validate_workbook_evolution

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
    """Select only paths that existed in the trusted tree; ignore mutable claims."""
    paths = trusted_tree(root, EXPECTED_BASELINE_HEAD)
    sosa_paths = [p for p in paths if p.startswith(("src/sosa-next/", "releases/sosa-next/", "mappings/SOSA-next", "config/sosa-", "queries/sosa-", "reports/sosa-"))]
    return {
        "current_mapping_semantics": [WORKBOOK, *PRODUCTS, *[p for p in paths if p.startswith("rules/")]],
        "current_sources_and_targets": [*SOURCES, *TARGETS],
        "pinned_sosa_2023": sosa_paths,
        "historical_authorities": [p for p in paths if p.startswith("legacy/") or
                                   (p.startswith("reports/") and p not in DOCUMENTARY_REPORTS and p not in sosa_paths)],
        "local_coms_architecture": [p for p in paths if p.startswith(("tools/coms_", "docs/COMS-"))],
    }


def compare(paths: list[str], expected: dict, root: Path) -> list[str]:
    return [p for p in paths if (root / p).is_symlink() or not (root / p).is_file()
            or fingerprint(root / p) != expected[p]]


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


def preservation(root: Path = ROOT, baseline: dict | None = None) -> dict:
    baseline = json.loads((root / BASELINE.relative_to(ROOT)).read_text()) if baseline is None else baseline
    expected = trusted_tree(root, EXPECTED_BASELINE_HEAD)
    errors = inventory_errors(baseline.get("tracked_files", {}), expected, "baseline inventory")
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
    workbook_evolution = {
        "status": "NOT_NEEDED", "workbook_path": WORKBOOK,
        "historical_sha256": expected[WORKBOOK]["sha256"],
        "current_sha256": fingerprint(root / WORKBOOK)["sha256"] if (root / WORKBOOK).is_file() else None,
    }
    if WORKBOOK in groups["current_mapping_semantics"]["changed_paths"]:
        # The trust root remains the pinned Git blob. An explicit documentary
        # transition explains changed workbook bytes without replacing it.
        try:
            if (root / WORKBOOK).is_symlink():
                raise ValueError("documentary workbook may not be a symlink")
            historical = validate_workbook_evolution(root, expected[WORKBOOK]["sha256"], root / WORKBOOK)
            if fingerprint(historical) != expected[WORKBOOK]:
                raise ValueError("retained historical workbook differs from trusted Git blob")
            groups["current_mapping_semantics"]["changed_paths"].remove(WORKBOOK)
            workbook_evolution.update(status="VALIDATED", semantic_projection_preserved=True,
                                      historical_snapshot_path=str(historical.relative_to(root)))
        except (ValueError, OSError, TypeError) as exc:
            workbook_evolution.update(status="FAIL", error=str(exc))
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
    if current_head != EXPECTED_BASELINE_HEAD:
        errors.append("HEAD differs from no-commit milestone baseline")
    counts = {p: workbook_counts(root, EXPECTED_BASELINE_HEAD, p)
              for p in expected if p.startswith("mappings/SOSA-next") and p.endswith(".xlsx")}
    for path, value in counts.items():
        if baseline.get("workbook_baselines", {}).get(path) != value:
            errors.append(f"{path}: recorded workbook baseline counts differ from trusted Git bytes")
    return {"baseline_head": EXPECTED_BASELINE_HEAD, "head": current_head,
            "branch": git(root, "branch", "--show-current"), "groups": groups,
            "external_coms": external_result, "errors": errors,
            "status": "FAIL" if errors else ("PASS" if external_result["status"] == "PASS" else "NOT_CHECKED"),
            "proof_basis": "Protected paths and expected SHA-256 hashes are derived from the pinned Git tree; candidate bytes are compared to Git blobs. Mutable baseline inventory/hashes are independently checked and cannot replace the trust root. External COMS is checked against its own pinned Git tree.",
            "documentary_workbook_evolution": workbook_evolution,
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
