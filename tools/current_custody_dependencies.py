"""Version-two reachable current-track custody, separate from output storage.

The existing validators remain the authority for workbook and decision history.
This module describes their required files; it never admits an artifact merely
because it was stored beside other evidence. Historical v1 inventories and
retention manifests are unchanged.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import current_decision_applicability as applicability
import current_documentary_workbook as documentary
import current_retained_evidence as retained
import current_semantic_workbook as semantic


POLICY_PATH = "tools/current_custody_dependencies.py"
ASSESSMENT = "mappings/current-ssn-sosa-assessment.json"
ASSESSMENT_SCOPE_PROFILE = "current-ssn-sosa-assessment-inputs-v2"
ASSESSMENT_OUTPUT_DIRECTORY = "reports/current-assessment/v2"
ASSESSMENT_INPUTS = frozenset({
    *semantic.SOURCE_TARGET_PATHS, *semantic.GOVERNED_INPUT_SHA256,
    ASSESSMENT, documentary.WORKBOOK, "SSN2BFO.ttl",
    "config/current-ssn-sosa-historical-finals.json", "config/publication-metadata.toml",
    POLICY_PATH, "tools/current_assessment.py", "tools/current_documentary_workbook.py",
    "tools/current_retained_evidence.py", "tools/current_semantic_workbook.py",
    "tools/current_decision_applicability.py",
})


def _required(root: Path, paths) -> set[str]:
    """Do not silently omit missing dependencies or admit symlink aliases."""
    return {documentary._path(root, path).relative_to(root).as_posix()
            for path in paths}


def python_paths(root: Path, entries: set[str]) -> set[str]:
    """Bind transitive local imports, including guarded/function-local imports.

    This conservative code closure does not execute modules or discover their
    output directories. Installed third-party libraries remain governed by the
    execution environment rather than being mistaken for repository files.
    """
    root = Path(root)
    pending, result = list(entries), set()
    while pending:
        relative = pending.pop()
        if relative in result:
            continue
        path = documentary._path(root, relative)
        result.add(relative)
        try:
            tree = ast.parse(path.read_text(), filename=relative)
        except (SyntaxError, UnicodeError) as exc:
            raise ValueError("cannot derive assessment Python dependency closure: " + relative) from exc
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
                modules.update(node.module + "." + alias.name for alias in node.names if alias.name != "*")
        for module in sorted(modules):
            stem = module.replace(".", "/")
            for candidate in (f"tools/{stem}.py", f"{stem}.py",
                              f"tools/{stem}/__init__.py", f"{stem}/__init__.py"):
                imported = documentary._local_path(root, candidate)
                if imported.exists():
                    documentary._path(root, candidate)
                    pending.append(candidate)
    return result


def _bound_paths(root: Path, ref: dict, *, historical: bool = False) -> set[str]:
    selected = documentary._bound_file(root, ref, allow_retained=historical)
    result = {selected.relative_to(root).as_posix()}
    if historical and selected != root / ref["path"]:
        # The resolver authenticates both the manifest and selected bytes,
        # including the logical path and source Git identity. The current file
        # at the logical path is not a substitute for those historical bytes.
        result.update(set(retained.evidence_paths(root, ref["path"], ref["sha256"]))
                      - {ref["path"]})
    return _required(root, result)


def _decision_paths(root: Path, records: list[dict]) -> set[str]:
    result = set()
    for record in records:
        if record.get("inheritance_sufficiency_evidence"):
            result.update(_bound_paths(root, record["inheritance_sufficiency_evidence"]))
        ref = record.get("human_decision_record")
        if not ref:
            continue
        result.update(_bound_paths(root, ref))
        decision = documentary._json(documentary._bound_file(root, ref))
        for key in ("assessment_snapshot", "review_packet_snapshot", "inheritance_sufficiency_evidence"):
            if decision.get(key):
                result.update(_bound_paths(root, decision[key]))
    return result


def _history_paths(root: Path) -> set[str]:
    # These calls authenticate the full closed history, including archive
    # membership, rather than following a caller-supplied whitelist of edges.
    paths = set(documentary.evidence_paths(root)) | set(applicability.evidence_paths(root))
    baseline = documentary._baseline(root)
    strict = {documentary.BASELINE}
    for ref in baseline["immutable_evidence"]:
        strict.update(_bound_paths(root, ref))
    support = []
    versions = {baseline["historical_workbook"]["sha256"]}
    for directory, key in ((documentary.UPDATES, "changes"), (semantic.TRANSITIONS, "authorities")):
        for path in semantic._archive_files(root, directory):
            record = documentary._json(path)
            versions.update(record[name] for name in ("old_workbook_sha256", "new_workbook_sha256"))
            entries = record[key].values() if key == "authorities" else record[key]
            for entry in entries:
                support.extend(entry["evidence"])
                if entry.get("human_decision"):
                    strict.update(_decision_paths(root, [{"human_decision_record": entry["human_decision"]}]))
    # The snapshot resolver inspects either possible physical location. Bind
    # both if both exist, so a second conflicting copy cannot evade custody.
    for digest in versions:
        semantic.snapshot(root, digest)
        for directory in (documentary.VERSIONS, semantic.VERSIONS):
            relative = f"{directory}/{digest}.xlsx"
            if documentary._local_path(root, relative).exists():
                strict.update(_bound_paths(root, {"path": relative, "sha256": digest}))
    for path in semantic._archive_files(root, applicability.PREPARED):
        support.extend(applicability._validate_prepared(root, path)["supporting_evidence"])
    # Authenticate all discovered bindings, including records that must not be
    # accepted merely because no current decision happens to use their ID.
    applicability._bound_records(root)
    for ref in support:
        paths.discard(ref["path"])
    for ref in support:
        paths.update(_bound_paths(root, ref, historical=True))
    paths.update(strict)
    return _required(root, paths)


def _publication_paths(root: Path) -> set[str]:
    import current_publication_preservation as preservation
    from check_coms_mapping import MAINTAINED_OUTPUTS, REPO_ROOT
    from current_semantic_validation import REPORT_PATH

    expected = preservation.trusted_tree(root, preservation.EXPECTED_BASELINE_HEAD)
    groups = preservation.protected_groups(root=root)
    paths = {preservation.BASELINE.relative_to(preservation.ROOT).as_posix(),
             *groups["checkpoint_custody_evidence"]}
    regenerable = {path.relative_to(REPO_ROOT).as_posix() for path in MAINTAINED_OUTPUTS.values()
                   if path.relative_to(REPO_ROOT).parts[0] == "reports"}
    regenerable.update((REPORT_PATH.as_posix(), REPORT_PATH.with_suffix(".md").as_posix()))
    for relative in groups["historical_authorities"]:
        if relative in regenerable:
            paths.update(_bound_paths(root, {"path": relative, "sha256": expected[relative]["sha256"]},
                                      historical=True))
            # Preservation also compares a present maintained report against
            # the old bytes. This later consumer must bind that live output.
            if documentary._local_path(root, relative).exists():
                paths.add(relative)
        else:
            paths.add(relative)
    return _required(root, paths)


def authority_paths(root: Path, publication: bool = False) -> set[str]:
    """Required authority files, with optional genuine preservation inputs."""
    root = Path(root)
    paths = _history_paths(root)
    document = documentary._json(documentary._path(root, ASSESSMENT))
    paths.update((ASSESSMENT,))
    paths.update(_decision_paths(root, document["records"]))
    if publication:
        paths.update(_publication_paths(root))
    return _required(root, paths)


def assessment_paths(root: Path) -> set[str]:
    """Inputs to assessment generation; its six output files are not inputs."""
    root = Path(root)
    paths = set(ASSESSMENT_INPUTS) | authority_paths(root)
    paths.update(python_paths(root, {"tools/current_assessment.py"}))
    document = documentary._json(documentary._path(root, ASSESSMENT))
    for record in document["records"]:
        for reference in record["evidence"]:
            if not reference.startswith("urn:"):
                paths.add(reference.split("#", 1)[0].split(":", 1)[0])
    return _required(root, paths)


def assessment_scope(root: Path) -> dict:
    """Code-owned policy identity; no caller-defined dependency exclusions."""
    policy = documentary._path(Path(root), POLICY_PATH)
    return {"schema_version": 2, "profile": ASSESSMENT_SCOPE_PROFILE,
            "policy": {"path": POLICY_PATH, "sha256": hashlib.sha256(policy.read_bytes()).hexdigest()},
            "custody": "authenticated_reachable_authorities",
            "outputs": ASSESSMENT_OUTPUT_DIRECTORY}
