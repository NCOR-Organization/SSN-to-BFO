#!/usr/bin/env python3
"""Byte identity of this project's current SSN/SOSA assessment closure only.

This record is not an upstream release identity or a COMS facility. Updating it
is a deliberate governance action; ordinary validation never updates hashes.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
import subprocess
from pathlib import Path

from rdflib import BNode, Graph, OWL, RDF, RDFS, URIRef
from rdflib.compare import to_canonical_graph

from current_documentary_workbook import validate_workbook_evolution

ROOT = Path(__file__).resolve().parents[1]
RECORD = Path("config/current-ssn-sosa-identity.json")
SOURCES = ("imports/sosa.ttl", "imports/sosa-sampling.ttl", "imports/ssn.ttl", "imports/ssn-systems.ttl")
TARGETS = ("imports/cco.ttl",)
WORKBOOK = "mappings/SSN2BFO-COMS.xlsx"
PRODUCTS = ("SSN2BFO.ttl", "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl",
            "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl",
            "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl")
CONFIGURATION = ("queries/source-classes-and-object-properties.rq", "queries/unmapped-source-terms.rq",
                 "config/current-ssn-sosa-scope.json", "config/publication-metadata.toml",
                 "config/product-role-policy.toml", "config/validation-toolchain.env",
                 "requirements/validation.txt", "requirements/coms-integration.txt")
UNKNOWN_UPSTREAM = "not established from repository evidence"


def fingerprint(path: Path) -> dict:
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


@lru_cache(maxsize=8)
def ontology_graph(data: bytes, public_id: str) -> Graph:
    # Cache only by the complete input bytes, never by an editable path or a
    # recorded checksum. Repeated validation still reads each governed file.
    return to_canonical_graph(Graph().parse(data=data, publicID=public_id, format="turtle"))


def artifact(path: str, root: Path = ROOT, *, ontology: bool = False) -> dict:
    result = {"path": path, **fingerprint(root / path)}
    history = git(root, "log", "--follow", "--format=%H|%aI|%s", "--", path).splitlines()
    result["local_git_provenance"] = {
        "latest_change": history[0] if history else None,
        "earliest_recoverable_change": history[-1] if history else None,
        "evidence_command": f"git log --follow --format='%H|%aI|%s' -- {path}",
    }
    if ontology:
        graph = ontology_graph((root / path).read_bytes(), (root / path).as_uri())
        result["upstream_immutable_commit"] = UNKNOWN_UPSTREAM
        result["ontologies"] = []
        for subject in sorted(set(graph.subjects(RDF.type, OWL.Ontology)), key=str):
            annotation_triples = set()
            def visit(node):
                for predicate, value in graph.predicate_objects(node):
                    triple = (node.n3(), predicate.n3(), value.n3())
                    if triple in annotation_triples:
                        continue
                    annotation_triples.add(triple)
                    if isinstance(value, BNode):
                        visit(value)
            visit(subject)
            result["ontologies"].append({
                "ontology_iri": str(subject),
                "version_iris": sorted(map(str, graph.objects(subject, OWL.versionIRI))),
                "imports": sorted(map(str, graph.objects(subject, OWL.imports))),
                "annotations_and_header_triples": sorted(annotation_triples),
            })
    return result


def target_components(root: Path = ROOT) -> dict:
    """Recover the redundant component claims from the actual merged header."""
    graph = ontology_graph((root / TARGETS[0]).read_bytes(), (root / TARGETS[0]).as_uri())
    ontology = URIRef("https://www.commoncoreontologies.org/CommonCoreOntologiesMerged")
    versions = sorted(map(str, graph.objects(ontology, OWL.versionIRI)))
    annotations = sorted(map(str, graph.objects(ontology, OWL.versionInfo)))
    versions_info = [value for value in annotations if value.startswith("Version ")]
    bfo_provenance = [value for value in annotations if value.startswith("Depends on http://purl.obolibrary.org/obo/bfo/")]
    embedded = any("Common Core Ontologies plus BFO" in str(value)
                   for value in graph.objects(ontology, RDFS.comment)) and any(
                       str(subject).startswith("http://purl.obolibrary.org/obo/BFO_")
                       for subject in graph.subjects(RDF.type, OWL.Class))
    return {
        "CCO": {"artifact": TARGETS[0], "version_iri": versions[0] if len(versions) == 1 else versions,
                "version_info": versions_info[0] if len(versions_info) == 1 else versions_info},
        "BFO": {"artifact": TARGETS[0],
                "identity_basis": "Embedded in merged CCO artifact, not a separately pinned BFO download" if embedded else UNKNOWN_UPSTREAM,
                "provenance_annotation": bfo_provenance[0] if len(bfo_provenance) == 1 else bfo_provenance,
                "upstream_immutable_commit": UNKNOWN_UPSTREAM},
    }


def build_record(root: Path = ROOT) -> dict:
    sources = [artifact(path, root, ontology=True) for path in SOURCES]
    targets = [artifact(path, root, ontology=True) for path in TARGETS]
    ontology_iris = {o["ontology_iri"] for a in sources + targets for o in a["ontologies"]}
    missing = sorted({i for a in sources + targets for o in a["ontologies"] for i in o["imports"]} - ontology_iris)
    return {
        "project": "SSN-to-BFO current SSN/SOSA publication assessment",
        "baseline_head": git(root, "rev-parse", "HEAD"),
        "branch_at_freeze": git(root, "branch", "--show-current"),
        "identity_policy": "Local byte identities; no upstream immutable commit is inferred from local Git history or version text.",
        "source_files": sources,
        "target_files": targets,
        "target_components": target_components(root),
        "unresolved_external_imports": missing,
        "closure_limitation": "The governed local closure contains all five listed artifacts. SKOS is imported by the sampling artifact but has no local byte-pinned copy; full upstream import closure identity is incomplete. Do not fetch or silently substitute another track's dependencies.",
        "authoritative_workbook": artifact(WORKBOOK, root),
        "products": [artifact(path, root) for path in PRODUCTS],
        "scope_and_configuration": [artifact(path, root) for path in CONFIGURATION],
    }


def check_record(document: dict, root: Path = ROOT) -> list[str]:
    errors = []
    groups = [("source_files", SOURCES), ("target_files", TARGETS), ("products", PRODUCTS),
              ("scope_and_configuration", CONFIGURATION)]
    entries = [document.get("authoritative_workbook", {})]
    if entries[0].get("path") != WORKBOOK:
        errors.append("authoritative workbook path differs")
    for name, expected in groups:
        values = document.get(name, [])
        paths = [entry.get("path") for entry in values]
        if sorted(paths) != sorted(expected):
            errors.append(f"{name}: missing, extra, or duplicate governed paths")
        entries.extend(values)
    for entry in entries:
        path = entry.get("path", "")
        if not path or not (root / path).is_file():
            errors.append(f"{path}: missing governed file")
            continue
        actual_fingerprint = fingerprint(root / path)
        if any(entry.get(key) != value for key, value in actual_fingerprint.items()):
            # Preserve the original full-workbook identity. Only a validated,
            # snapshot-backed documentary chain can explain its later bytes;
            # source, target, product and configuration identities stay exact.
            try:
                if path != WORKBOOK:
                    raise ValueError("not the governed documentary workbook")
                if (root / path).is_symlink():
                    raise ValueError("documentary workbook may not be a symlink")
                historical = validate_workbook_evolution(root, entry.get("sha256"), root / path)
                if any(entry.get(key) != value for key, value in fingerprint(historical).items()):
                    raise ValueError("retained historical workbook fingerprint differs")
            except (ValueError, OSError, TypeError) as exc:
                errors.append(f"{path}: byte identity drift; {exc}")
    # Recompute each redundant claim from governed bytes, Git history, and the
    # project-local role contract. Correct checksums do not license false prose.
    governed = {WORKBOOK, *SOURCES, *TARGETS, *PRODUCTS, *CONFIGURATION}
    if not all((root / path).is_file() for path in governed):
        return errors
    actual_record = json.loads(json.dumps(build_record(root)))
    actual_entries = {entry["path"]: entry for name, _ in groups for entry in actual_record[name]}
    actual_entries[WORKBOOK] = actual_record["authoritative_workbook"]
    for entry in entries:
        path = entry.get("path", "")
        actual = actual_entries.get(path)
        if actual is None:
            continue
        if entry.get("local_git_provenance") != actual["local_git_provenance"]:
            errors.append(f"{path}: local Git provenance differs")
        if path in SOURCES + TARGETS:
            if entry.get("ontologies") != actual["ontologies"]:
                errors.append(f"{path}: ontology header identity differs")
            if entry.get("upstream_immutable_commit") != UNKNOWN_UPSTREAM:
                errors.append(f"{path}: unsupported upstream immutable identity")
        if set(entry) != set(actual):
            errors.append(f"{path}: missing or unsupported authoritative metadata fields")
    for name in set(actual_record) - {"authoritative_workbook", *(name for name, _ in groups)}:
        if document.get(name) != actual_record[name]:
            errors.append(f"{name}: identity metadata differs from governed artifacts or local Git")
    if set(document) != set(actual_record):
        errors.append("missing or unsupported authoritative identity fields")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="Explicitly replace the project identity record after review")
    args = parser.parse_args()
    if args.freeze:
        (ROOT / RECORD).write_text(json.dumps(build_record(), indent=2) + "\n")
    errors = check_record(json.loads((ROOT / RECORD).read_text()))
    print("\n".join(errors) if errors else "Current source/target/workbook/product/configuration identities: PASS")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
