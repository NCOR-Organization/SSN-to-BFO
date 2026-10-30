#!/usr/bin/env python3
"""Byte identity of this project's current SSN/SOSA assessment closure only.

This record is not an upstream release identity or a COMS facility. Its accepted
historical bytes remain fixed; governed evolution is recorded separately.
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

from current_semantic_workbook import validate_workbook_evolution
from current_documentary_workbook import semantic_projection_sha256

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
# The identity document describes the original freeze. The later, explicitly
# accepted checkpoint records that freeze and its documentary history; it does
# not retrospectively replace either. Arbitrary descendants remain unaccepted.
IDENTITY_BASELINE_HEAD = "c3f9b05593727bd13854bf1830cc09b4a653b41f"
ACCEPTED_CHECKPOINT_HEAD = "dc314460fe3e875ba1c8ccfcb3c6840a7181e733"


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


def artifact(path: str, root: Path = ROOT, *, ontology: bool = False,
             history_head: str | None = None) -> dict:
    result = {"path": path, **fingerprint(root / path)}
    revision = [history_head] if history_head else []
    history = git(root, "log", "--follow", "--format=%H|%aI|%s", *revision, "--", path).splitlines()
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


def build_record(root: Path = ROOT, *, history_head: str | None = None) -> dict:
    sources = [artifact(path, root, ontology=True, history_head=history_head) for path in SOURCES]
    targets = [artifact(path, root, ontology=True, history_head=history_head) for path in TARGETS]
    ontology_iris = {o["ontology_iri"] for a in sources + targets for o in a["ontologies"]}
    missing = sorted({i for a in sources + targets for o in a["ontologies"] for i in o["imports"]} - ontology_iris)
    return {
        "project": "SSN-to-BFO current SSN/SOSA publication assessment",
        "baseline_head": history_head or git(root, "rev-parse", "HEAD"),
        "branch_at_freeze": git(root, "branch", "--show-current"),
        "identity_policy": "Local byte identities; no upstream immutable commit is inferred from local Git history or version text.",
        "source_files": sources,
        "target_files": targets,
        "target_components": target_components(root),
        "unresolved_external_imports": missing,
        "closure_limitation": "The governed local closure contains all five listed artifacts. SKOS is imported by the sampling artifact but has no local byte-pinned copy; full upstream import closure identity is incomplete. Do not fetch or silently substitute another track's dependencies.",
        "authoritative_workbook": artifact(WORKBOOK, root, history_head=history_head),
        "products": [artifact(path, root, history_head=history_head) for path in PRODUCTS],
        "scope_and_configuration": [artifact(path, root, history_head=history_head) for path in CONFIGURATION],
    }


def checkpoint_errors(root: Path) -> list[str]:
    """Keep historical checkpoints fixed; descendants need an exact successor."""
    head = git(root, "rev-parse", "HEAD")
    if head not in {IDENTITY_BASELINE_HEAD, ACCEPTED_CHECKPOINT_HEAD}:
        try:
            from current_checkpoint_successor import validate_successor
            validate_successor(root, head)
            return []
        except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
            return ["HEAD differs from the accepted publication checkpoints: " + str(exc)]
    if head == ACCEPTED_CHECKPOINT_HEAD and subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor",
             IDENTITY_BASELINE_HEAD, ACCEPTED_CHECKPOINT_HEAD], capture_output=True).returncode:
        return ["accepted checkpoint does not retain the original publication baseline"]
    return []


def validated_product_evolution(root: Path, expected: dict[str, dict]) -> dict:
    """Authenticate old Git bytes and require exact current native generation.

    A semantic manifest does not itself authorize arbitrary generated bytes.
    Only the four existing current products may advance, and each must equal
    deterministic generation from the fully validated current workbook chain.
    """
    from current_semantic_workbook import resolve_history
    from current_semantic_generation import render_current_products

    if set(expected) != set(PRODUCTS):
        raise ValueError("semantic product evolution requires all four governed products")
    history = resolve_history(root)
    if not any(item.get("kind") == "semantic" for item in history["chain"]):
        raise ValueError("product byte drift has no governed semantic transition")
    for path, recorded in expected.items():
        original = subprocess.check_output(
            ["git", "-C", str(root), "show", f"{IDENTITY_BASELINE_HEAD}:{path}"])
        original_fingerprint = {"sha256": hashlib.sha256(original).hexdigest(), "bytes": len(original)}
        if {key: recorded.get(key) for key in original_fingerprint} != original_fingerprint:
            raise ValueError(f"{path}: historical product identity differs from trusted Git bytes")
    rendered = render_current_products(root, root / WORKBOOK)
    if set(rendered) != set(PRODUCTS):
        raise ValueError("semantic generation did not produce exactly the governed products")
    for path, data in rendered.items():
        candidate = root / path
        if candidate.is_symlink() or not candidate.is_file() or candidate.read_bytes() != data:
            raise ValueError(f"{path}: current product differs from validated deterministic generation")
    return {"status": "VALIDATED", "historical_head": IDENTITY_BASELINE_HEAD,
            "current_workbook_sha256": fingerprint(root / WORKBOOK)["sha256"],
            "products": {path: fingerprint(root / path) for path in PRODUCTS}}


def check_record(document: dict, root: Path = ROOT) -> list[str]:
    errors = checkpoint_errors(root)
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
    product_validation = None
    product_validation_error = None
    semantic_workbook_changed = False
    for entry in entries:
        path = entry.get("path", "")
        if not path or not (root / path).is_file():
            errors.append(f"{path}: missing governed file")
            continue
        actual_fingerprint = fingerprint(root / path)
        if any(entry.get(key) != value for key, value in actual_fingerprint.items()):
            # Preserve original identities. Workbook evolution is snapshot-
            # backed; changed products must match native generation. Sources,
            # targets and configuration receive no evolution exemption.
            try:
                if path in PRODUCTS:
                    if product_validation_error is not None:
                        raise ValueError(product_validation_error)
                    if product_validation is None:
                        try:
                            product_validation = validated_product_evolution(
                                root, {item["path"]: item for item in document.get("products", [])})
                        except (ValueError, OSError, TypeError) as exc:
                            product_validation_error = str(exc)
                            raise
                    continue
                if path != WORKBOOK:
                    raise ValueError("not an evolvable governed workbook/product")
                if (root / path).is_symlink():
                    raise ValueError("documentary workbook may not be a symlink")
                historical = validate_workbook_evolution(root, entry.get("sha256"), root / path)
                if any(entry.get(key) != value for key, value in fingerprint(historical).items()):
                    raise ValueError("retained historical workbook fingerprint differs")
                semantic_workbook_changed = (semantic_projection_sha256(historical) !=
                                             semantic_projection_sha256(root / path))
            except (ValueError, OSError, TypeError) as exc:
                errors.append(f"{path}: byte identity drift; {exc}")
    if semantic_workbook_changed and product_validation is None and product_validation_error is None:
        try:
            validated_product_evolution(root, {item["path"]: item for item in document.get("products", [])})
        except (ValueError, OSError, TypeError) as exc:
            errors.append(f"semantic workbook products: {exc}")
    # Recompute each redundant claim from governed bytes, Git history, and the
    # project-local role contract. Correct checksums do not license false prose.
    governed = {WORKBOOK, *SOURCES, *TARGETS, *PRODUCTS, *CONFIGURATION}
    if not all((root / path).is_file() for path in governed):
        return errors
    actual_record = json.loads(json.dumps(build_record(root, history_head=IDENTITY_BASELINE_HEAD)))
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
    parser.add_argument("--freeze", action="store_true", help="Retired: historical identity is immutable; use a governed workbook transition")
    args = parser.parse_args()
    if args.freeze:
        print("Historical source identity cannot be re-frozen; record governed workbook evolution separately.")
        return 1
    errors = check_record(json.loads((ROOT / RECORD).read_text()))
    print("\n".join(errors) if errors else "Current source/target/workbook/product/configuration identities: PASS")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
