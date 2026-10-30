"""Exact, project-local generation expectations for governed workbook evolution.

Computing a proposal is not authorization. Production count overrides are only
activated after the workbook history (including these expectations) validates.
The ordinary COMS selection rules and every product structural check still run.
"""
from __future__ import annotations

from collections import Counter, OrderedDict
import copy
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from rdflib import Graph, OWL, RDFS


_ACTIVE: ContextVar[dict | None] = ContextVar("ssn_semantic_generation", default=None)
_SNAPSHOTS: OrderedDict[tuple, tuple[dict, dict[str, bytes]]] = OrderedDict()
PRODUCT_PATHS = {
    "integrated": "SSN2BFO.ttl",
    "alignment_core": "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl",
    "strict_bfo_mapping": "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl",
    "cco_extension": "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl",
}


def expected_count(name: str, baseline: int) -> int:
    """No ambient authorization means the original exact baseline applies."""
    active = _ACTIVE.get()
    if active is None:
        return baseline
    if name not in active["counts"]:
        raise ValueError(f"semantic generation expectation missing: {name}")
    value = active["counts"][name]
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid semantic generation count: {name}")
    return value


def selection_policy(product_key: str, baseline):
    active = _ACTIVE.get()
    if active is None or baseline is None:
        return baseline
    categories = active["category_counts"]
    totals = active["disposition_counts"][product_key]
    return replace(
        baseline,
        expected_count=sum(categories.get(key, 0) for key in baseline.categories),
        expected_category_counts=tuple((key, categories.get(key, 0)) for key in baseline.categories),
        expected_disposition_totals=tuple(
            (item["category"], item["status"], item["reason_code"], item["count"])
            for item in totals
        ),
    )


@contextmanager
def _snapshot_context(snapshot: dict):
    token = _ACTIVE.set(snapshot)
    try:
        yield
    finally:
        _ACTIVE.reset(token)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inputs(root: Path, workbook_path: Path):
    import generate_mapping_from_coms as mapping
    from coms_framework_integration import process_primary_workbook_with_coms_result
    from publication_metadata import load_metadata

    resolver = mapping.Resolver(root=root)
    result = process_primary_workbook_with_coms_result(workbook_path, resolver)
    metadata = load_metadata(root / "config/publication-metadata.toml")
    return result, resolver, metadata


def _snapshot_key(root: Path, workbook_path: Path) -> tuple:
    # Full input identities, not mtimes, keep the cache safe for mutation tests
    # and later transitions. Code identities invalidate changed derivations.
    inputs = (
        "imports/sosa.ttl", "imports/sosa-sampling.ttl", "imports/ssn.ttl",
        "imports/ssn-systems.ttl", "imports/cco.ttl", "config/publication-metadata.toml",
        "config/current-ssn-sosa-scope.json", "queries/source-classes-and-object-properties.rq",
        "rules/ssn-hasproperty-conditional-mapping.rq",
    )
    code = ("current_semantic_generation.py", "generate_mapping_from_coms.py",
            "coms_framework_integration.py", "coms_row_identity.py",
            "modular_products.py", "product_dispositions.py", "current_assessment.py",
            "publication_metadata.py")
    return (str(root.resolve()), _sha(workbook_path),
            tuple((path, _sha(root / path)) for path in inputs),
            tuple((path, _sha(Path(__file__).parent / path)) for path in code))


def _snapshot(root: Path, workbook_path: Path) -> tuple[dict, dict[str, bytes]]:
    root, workbook_path = Path(root), Path(workbook_path)
    key = _snapshot_key(root, workbook_path)
    if key not in _SNAPSHOTS:
        value = _snapshot_uncached(root, workbook_path)
        if _snapshot_key(root, workbook_path) != key:
            raise ValueError("generation inputs changed during expectation calculation")
        _SNAPSHOTS[key] = value
        if len(_SNAPSHOTS) > 64:
            _SNAPSHOTS.popitem(last=False)
    _SNAPSHOTS.move_to_end(key)
    snapshot, products = _SNAPSHOTS[key]
    return copy.deepcopy(snapshot), dict(products)


def _snapshot_uncached(root: Path, workbook_path: Path) -> tuple[dict, dict[str, bytes]]:
    """Measure deterministic products without authorizing or writing them."""
    import current_assessment as assessment
    import generate_mapping_from_coms as mapping
    import modular_products as modular
    from product_dispositions import axiom_input_from_canonical_row, classify_target_category, derive_product_dispositions, PRODUCT_ROLE_ORDER
    from publication_metadata import strip_emitted_ontology_header

    result, resolver, metadata = _inputs(root, workbook_path)
    rows = result.processed_rows
    categories: Counter = Counter()
    selected = {key: [] for key in modular.PRODUCT_SELECTION}
    dispositions = {key: Counter() for key in selected}
    canonical_axioms = []
    for row in rows:
        canonical = mapping.canonical_input_for_processed_row(row)
        audit = row.identity_audit
        for identity in audit.authoritative_axioms:
            canonical_axioms.append(identity.canonical_axiom)
            category = classify_target_category(axiom_input_from_canonical_row(identity, canonical))
            categories[category] += 1
            by_product = dict(derive_product_dispositions(category, PRODUCT_ROLE_ORDER))
            for key, policy in modular.PRODUCT_SELECTION.items():
                disposition = by_product[key]
                dispositions[key][(category, disposition.status, disposition.reason_code)] += 1
                if category in policy.categories and disposition.status == "emitted_unchanged":
                    selected[key].append(modular.SelectedProductAxiom(
                        row_id=audit.row_id, location=canonical.location,
                        source_expression_sha256=audit.source_expression_sha256,
                        canonical_row=audit.expression, canonical_input=canonical,
                        identity=identity, target_category=category, disposition=disposition,
                    ))
    selected = {key: tuple(sorted(values, key=lambda item: item.axiom_id)) for key, values in selected.items()}
    counts = {
        "GOVERNED_ROW_COUNT": len(rows),
        "AUTHORITATIVE_AXIOM_COUNT": len(canonical_axioms),
        "ZERO_AXIOM_ROW_COUNT": sum(not row.identity_audit.authoritative_axioms for row in rows),
        "BFO_PROJECTION_AXIOM_COUNT": len(selected["bfo_projection"]),
    }
    serialized = {"integrated": mapping._root_turtle_bytes(rows, metadata)}
    graphs = {}
    source_paths = tuple(root / path for path in mapping.SOURCE_IMPORTS)
    dependencies = (*source_paths, root / mapping.BFO_VALIDATION_DEPENDENCY)
    source_graph = resolver.source_graph
    product_spec = (
        ("alignment_core", "ALIGNMENT_CORE", (), modular.PREFIXES),
        ("strict_bfo_mapping", "STRICT_BFO", (modular.ALIGNMENT_CORE_IMPORT_IRI,), modular.STRICT_BFO_PREFIXES),
        ("cco_extension", "CCO_EXTENSION", (modular.STRICT_BFO_IMPORT_IRI,), modular.CCO_EXTENSION_PREFIXES),
    )
    for key, prefix, imports, prefixes in product_spec:
        values = selected[key]
        product_metadata = modular._product_metadata(metadata, key)
        serialized[key] = modular._turtle_bytes(metadata, product_metadata, values, imports=imports, prefixes=prefixes)
        graph = Graph().parse(data=serialized[key].decode(), format="turtle")
        graphs[key] = graph
        logical = strip_emitted_ontology_header(graph, metadata, key, imports)
        def number(suffix, value):
            counts[f"{prefix}_{suffix}_COUNT"] = value
        number("AXIOM", len(values))
        number("DOMAIN", sum(v.canonical_input.mapping_type == "domain" for v in values))
        number("RANGE", sum(v.canonical_input.mapping_type == "range" for v in values))
        number("LOGICAL_TRIPLE", len(logical))
        number("TOTAL_TRIPLE", len(graph))
        number("FORMAL_TOTAL_TRIPLE", len(graph) + 3)
        named = sum(v.canonical_input.target_property_iri is not None or (v.canonical_input.expression is not None and v.canonical_input.expression.kind == "named") for v in values)
        number("NAMED_TARGET", named)
        number("UNION_TARGET", sum(v.canonical_input.expression is not None and v.canonical_input.expression.kind == "union" for v in values))
        for suffix, predicate in (("SUBCLASS", RDFS.subClassOf), ("EQUIVALENT_CLASS", OWL.equivalentClass), ("DIRECT_SUBPROPERTY", RDFS.subPropertyOf)):
            number(suffix, sum(v.canonical_input.predicate_iri == str(predicate) for v in values))
        chains = sum(v.canonical_input.mapping_type == "property_chain" for v in values)
        number("PROPERTY_CHAIN", chains)
        kinds = {kind: sum(modular._expression_kind_count(v.canonical_input.expression, kind) for v in values) for kind in ("union", "intersection", "some")}
        number("UNION", kinds["union"])
        number("INTERSECTION", kinds["intersection"])
        number("EXISTENTIAL", kinds["some"])
        number("RDF_LIST", kinds["union"] + kinds["intersection"] + chains)
        number("COMPLEX_TARGET", len(values) - named)
        if key == "alignment_core":
            number("FIXED_CLOSURE_TRIPLE", len(modular.build_fixed_source_closure(serialized[key], source_paths)))
        else:
            keys = ("alignment_core", "strict_bfo_mapping") if key == "strict_bfo_mapping" else ("alignment_core", "strict_bfo_mapping", "cco_extension")
            project = Graph()
            for member in keys:
                for triple in graphs[member]:
                    project.add(triple)
            number("PROJECT_CLOSURE_AXIOM", sum(len(selected[member]) for member in keys))
            number("PROJECT_GRAPH_TRIPLE", len(project))
            number("FORMAL_PROJECT_GRAPH_TRIPLE", len(project) + 3 * len(keys))
            for triple in list(project.triples((None, OWL.imports, None))):
                project.remove(triple)
            number("LOCAL_PROJECT_GRAPH_TRIPLE", len(project))
            number("FORMAL_LOCAL_PROJECT_GRAPH_TRIPLE", len(project) + 3 * len(keys))
            closure = modular.build_fixed_validation_closure((serialized[member] for member in keys), dependencies)
            number("FIXED_CLOSURE_TRIPLE", len(closure))
            number("FORMAL_FIXED_CLOSURE_TRIPLE", len(closure) + 3 * len(keys))
    counts["CCO_EXTENSION_CCO_BEARING_COUNT"] = categories["cco_bearing"]
    counts["CCO_EXTENSION_MIXED_COUNT"] = categories["mixed_bfo_cco"]
    referenced = set()
    for value in selected["cco_extension"]:
        item = axiom_input_from_canonical_row(value.identity, value.canonical_input)
        referenced.update((item.subject_iri, *item.target_iris))
    counts["CCO_EXTENSION_SOURCE_TERM_COUNT"] = sum(iri.startswith(modular.SOURCE_NAMESPACES) for iri in referenced)
    counts["CCO_EXTENSION_CCO_TERM_COUNT"] = sum(iri.startswith(modular.CCO_NAMESPACE) for iri in referenced)
    counts["CCO_EXTENSION_BFO_TERM_COUNT"] = sum(iri.startswith(modular.BFO_NAMESPACE) for iri in referenced)
    root_graph = Graph().parse(data=serialized["integrated"].decode(), format="turtle")
    root_logical = strip_emitted_ontology_header(root_graph, metadata, "integrated", mapping.ROOT_ORDERED_IMPORTS)
    counts.update({
        "ROOT_ONTOLOGY_DECLARATION_COUNT": 1, "ROOT_IMPORT_COUNT": 4,
        "ROOT_METADATA_ANNOTATION_COUNT": 7,
        "ROOT_LOGICAL_TRIPLE_COUNT": len(root_logical),
        "ROOT_TOTAL_TRIPLE_COUNT": len(root_graph),
        "ROOT_FORMAL_TOTAL_TRIPLE_COUNT": len(root_graph) + 3,
        "ROOT_FIXED_CLOSURE_TRIPLE_COUNT": len(modular.build_fixed_validation_closure((serialized["integrated"],), dependencies)),
    })
    counts["ROOT_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT"] = counts["ROOT_FIXED_CLOSURE_TRIPLE_COUNT"] + 3
    terms = {str(row["term"]): str(row["kind"]) for row in mapping.run_select_query(source_graph, root / "queries/source-classes-and-object-properties.rq")}
    coverage = assessment.coverage(terms, source_graph, rows)
    coverage_counts = {name: sum(bool(row[name]) for row in coverage) for name in (
        "direct_formal_mapping", "inherited_formal_mapping", "rule_or_chain_route",
        "typing_only_in_workbook", "explicit_blank", "no_established_formal_route",
    )}
    coverage_counts["source_terms"] = len(terms)
    coverage_counts["direct_classes"] = sum(row["direct_formal_mapping"] and row["source_kind"] == "class" for row in coverage)
    coverage_counts["direct_object_properties"] = sum(row["direct_formal_mapping"] and row["source_kind"] == "object_property" for row in coverage)
    snapshot = {
        "workbook_sha256": _sha(workbook_path), "counts": dict(sorted(counts.items())),
        "canonical_axioms": sorted(canonical_axioms), "category_counts": dict(sorted(categories.items())),
        "disposition_counts": {
            key: [{"category": category, "status": status, "reason_code": reason, "count": count}
                  for (category, status, reason), count in sorted(values.items(), key=lambda item: str(item[0]))]
            for key, values in sorted(dispositions.items())
        }, "coverage_counts": coverage_counts,
    }
    return snapshot, serialized


def compute_expectations(root: Path, old_path: Path, new_path: Path) -> dict:
    before, _ = _snapshot(root, old_path)
    after, _ = _snapshot(root, new_path)
    return {
        "schema_version": 1, "before": before, "after": after,
        "logical_axiom_delta": {
            "added": sorted(set(after["canonical_axioms"]) - set(before["canonical_axioms"])),
            "removed": sorted(set(before["canonical_axioms"]) - set(after["canonical_axioms"])),
        },
        "count_delta": {key: after["counts"][key] - before["counts"][key] for key in before["counts"]},
        "coverage_delta": {key: after["coverage_counts"][key] - before["coverage_counts"][key] for key in before["coverage_counts"]},
    }


def validate_expectations(root: Path, old_path: Path, new_path: Path, declared: dict) -> None:
    # JSON equality is type-exact (Python equality treats True and 1 as equal).
    actual = compute_expectations(root, old_path, new_path)
    if json.dumps(declared, sort_keys=True, allow_nan=False) != json.dumps(actual, sort_keys=True, allow_nan=False):
        raise ValueError("semantic generation expectations do not match exact workbook axiom/count/coverage delta")


@contextmanager
def generated_expectations_context(root: Path, workbook_path: Path):
    from current_semantic_workbook import resolve_history

    history = resolve_history(root, current_path=workbook_path)
    semantic = [record for record in history["chain"] if record.get("kind") == "semantic"]
    if not semantic:
        yield
        return
    expected = semantic[-1]["generation_expectations"]["after"]
    actual, _ = _snapshot(root, workbook_path)
    # A subsequent governed D-only transition can change full bytes, never metrics.
    if {k: v for k, v in actual.items() if k != "workbook_sha256"} != {k: v for k, v in expected.items() if k != "workbook_sha256"}:
        raise ValueError("current workbook generation expectations differ from validated transition")
    with _snapshot_context(expected):
        yield


def validate_row_counts(stats, audits) -> None:
    actual = {"GOVERNED_ROW_COUNT": stats.governed_row_id_count,
              "AUTHORITATIVE_AXIOM_COUNT": sum(len(a.authoritative_axioms) for a in audits),
              "ZERO_AXIOM_ROW_COUNT": sum(not a.authoritative_axioms for a in audits)}
    for name, baseline in (("GOVERNED_ROW_COUNT", 105), ("AUTHORITATIVE_AXIOM_COUNT", 103), ("ZERO_AXIOM_ROW_COUNT", 2)):
        if actual[name] != expected_count(name, baseline):
            raise ValueError(f"generation count mismatch for {name}: {actual[name]} != {expected_count(name, baseline)}")


def render_current_products(root: Path, workbook_path: Path) -> dict[str, bytes]:
    """Render and structurally validate all maintained products; never write."""
    with generated_expectations_context(root, workbook_path):
        actual, serialized = _snapshot(root, workbook_path)
        for name, count in actual["counts"].items():
            # Every measured count is bound once a semantic context is active.
            if _ACTIVE.get() is not None and expected_count(name, count) != count:
                raise ValueError(f"rendered product count drift: {name}")
        _validate_rendered(root, workbook_path, serialized)
        return {PRODUCT_PATHS[key]: value for key, value in serialized.items()}


def render_current_formal_products(root: Path, context, workbook_path: Path,
                                   metadata_path: Path, disposition_path: Path):
    """Project-local formal rendering; leave the byte-pinned builder intact.

    This does not advance the independent formal package/manifest authorities.
    """
    from build_release import render_formal_products
    with generated_expectations_context(root, workbook_path):
        return render_formal_products(context, workbook_path, metadata_path, disposition_path)


def _validate_rendered(root: Path, workbook_path: Path, serialized: dict[str, bytes]) -> None:
    import generate_mapping_from_coms as mapping
    import modular_products as modular
    from product_dispositions import build_disposition_document, RequiredInputHashes

    result, _, metadata = _inputs(root, workbook_path)
    rows = result.processed_rows
    audits = [row.identity_audit for row in rows]
    validate_row_counts(result.stats, audits)
    hashes = RequiredInputHashes(
        workbook_sha256=_sha(workbook_path),
        generator_sha256=_sha(Path(mapping.__file__)),
        row_identity_module_sha256=_sha(Path(__file__).parent / "coms_row_identity.py"),
        disposition_module_sha256=_sha(Path(__file__).parent / "product_dispositions.py"),
        publication_metadata_sha256=_sha(root / "config/publication-metadata.toml"),
    )
    document = build_disposition_document([mapping.disposition_input_for_processed_row(row) for row in rows], metadata, hashes)
    canonical = [mapping.canonical_input_for_processed_row(row) for row in rows]
    selected = {key: modular.reconcile_product_axioms(key, canonical, audits, document).selected_axioms for key in modular.PRODUCT_SELECTION}
    graph = Graph().parse(data=serialized["integrated"].decode(), format="turtle")
    if len(graph) != expected_count("ROOT_TOTAL_TRIPLE_COUNT", mapping.ROOT_TOTAL_TRIPLE_COUNT):
        raise ValueError("integrated-root total triple count mismatch")
    core = modular.build_alignment_core(selected["alignment_core"], metadata)
    strict = modular.build_strict_bfo_mapping(selected["strict_bfo_mapping"], metadata)
    cco = modular.build_cco_extension(selected["cco_extension"], metadata)
    for key, product in (("alignment_core", core), ("strict_bfo_mapping", strict), ("cco_extension", cco)):
        if product.serialized_bytes != serialized[key]:
            raise ValueError(f"deterministic rendering mismatch: {key}")
    issues = (
        *modular.validate_alignment_core(core.serialized_bytes, selected["alignment_core"], metadata, integrated_graph=graph),
        *modular.validate_strict_bfo_mapping(strict.serialized_bytes, selected["strict_bfo_mapping"], core.serialized_bytes, selected["alignment_core"], metadata, integrated_graph=graph),
        *modular.validate_cco_extension(cco.serialized_bytes, selected["cco_extension"], strict.serialized_bytes, selected["strict_bfo_mapping"], core.serialized_bytes, selected["alignment_core"], metadata, integrated_graph=graph),
    )
    if issues:
        raise ValueError("semantic product validation failed: " + " | ".join(modular.format_issue(value) for value in issues))
