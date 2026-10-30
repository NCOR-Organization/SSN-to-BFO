#!/usr/bin/env python3
"""Shared helpers for independent ROBOT reconstruction of governed COMS axioms."""

from __future__ import annotations

import hashlib
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from rdflib import Graph

import generate_mapping_from_coms as coms
import current_semantic_generation as generation
import current_semantic_workbook as semantic
import modular_products as modular
from coms_row_identity import CanonicalRowInput

REPO_ROOT = Path(__file__).resolve().parents[1]
NON_CHAIN_MAPPING_TYPES = frozenset({"class_mapping", "object_property_mapping", "domain", "range"})
ACTIVE_MAPPING_TYPES = NON_CHAIN_MAPPING_TYPES | {"property_chain"}


@dataclass(frozen=True)
class GovernedComsRows:
    processed_rows: tuple[coms.ProcessedRow, ...]
    canonical_rows: tuple[CanonicalRowInput, ...]
    row_count: int
    active_count: int
    blank_count: int
    property_chain_count: int

    @property
    def non_chain_count(self) -> int:
        return self.active_count - self.property_chain_count


@dataclass(frozen=True)
class CanonicalAxiomComparison:
    expected: dict[str, str]
    actual: dict[str, str]
    missing_axiom_ids: tuple[str, ...]
    extra_axiom_ids: tuple[str, ...]
    mismatched_axiom_ids: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return (
            not self.missing_axiom_ids
            and not self.extra_axiom_ids
            and not self.mismatched_axiom_ids
        )


@contextmanager
def _authenticated_expectations(workbook_path: Path, historical: bool):
    if not historical:
        with generation.generated_expectations_context(REPO_ROOT, workbook_path):
            yield
        return

    # Historical use is explicit: accepting an archived hash on the default
    # current path would silently permit rollback of an authorized transition.
    history = semantic.resolve_history(REPO_ROOT)
    digest = hashlib.sha256(workbook_path.read_bytes()).hexdigest()
    if digest not in history["version_sha256"]:
        raise ValueError("historical ROBOT workbook is not in authenticated history")
    if workbook_path.read_bytes() != semantic.snapshot(REPO_ROOT, digest).read_bytes():
        raise ValueError("historical ROBOT workbook differs from authenticated snapshot")
    expected = None
    if digest != history["version_sha256"][0]:
        for record in history["chain"]:
            if record["kind"] == "semantic":
                expected = record["generation_expectations"]["after"]
            if record["new_workbook_sha256"] == digest:
                break
    # Documentary-only history retains the original baseline counts. For a
    # semantic version, use its authenticated expectations, never the live tail's.
    with generation._snapshot_context(expected):
        yield


def load_governed_coms_rows(workbook_path: Path, *, historical: bool = False) -> GovernedComsRows:
    """Authenticate the workbook, then validate its complete row/axiom partition."""
    workbook_path = workbook_path.resolve()
    workbook_digest = hashlib.sha256(workbook_path.read_bytes()).hexdigest()
    with _authenticated_expectations(workbook_path, historical):
        row_count = generation.expected_count("GOVERNED_ROW_COUNT", 105)
        active_count = generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103)
        blank_count = generation.expected_count("ZERO_AXIOM_ROW_COUNT", 2)
        # These three products partition the authoritative mapping axioms.
        chain_count = sum(generation.expected_count(name, baseline) for name, baseline in (
            ("ALIGNMENT_CORE_PROPERTY_CHAIN_COUNT", 0),
            ("STRICT_BFO_PROPERTY_CHAIN_COUNT", 2),
            ("CCO_EXTENSION_PROPERTY_CHAIN_COUNT", 1),
        ))
        workbook_rows, stats = coms.read_workbook(workbook_path)
        processed_rows = tuple(coms.validate_and_process_rows(workbook_rows, coms.Resolver(), stats))
        audits = tuple(row.identity_audit for row in processed_rows)
        if any(audit is None for audit in audits):
            raise ValueError("governed ROBOT row is missing its canonical identity audit")
        generation.validate_row_counts(stats, audits)
        canonical_rows = tuple(coms.canonical_input_for_processed_row(row) for row in processed_rows)

    if hashlib.sha256(workbook_path.read_bytes()).hexdigest() != workbook_digest:
        raise ValueError("governed ROBOT workbook changed during authentication or processing")
    for row, audit in zip(canonical_rows, audits):
        if row.mapping_type not in ACTIVE_MAPPING_TYPES | {"explicit_blank"}:
            raise ValueError(f"{row.row_id}: unsupported active ROBOT mapping type {row.mapping_type}")
        expected_size = 0 if row.mapping_type == "explicit_blank" else 1
        if len(audit.authoritative_axioms) != expected_size:
            raise ValueError(f"{row.row_id}: ROBOT row/axiom cardinality differs")
    identities = canonical_expected_axioms(processed_rows, ACTIVE_MAPPING_TYPES)
    if (
        len(processed_rows) != row_count
        or len({row.row_id for row in canonical_rows}) != row_count
        or len(identities) != active_count
        or sum(row.mapping_type == "explicit_blank" for row in canonical_rows) != blank_count
        or sum(row.mapping_type == "property_chain" for row in canonical_rows) != chain_count
        or row_count != active_count + blank_count
    ):
        raise ValueError("ROBOT row partitions differ from authenticated generation expectations")
    return GovernedComsRows(
        processed_rows=processed_rows,
        canonical_rows=canonical_rows,
        row_count=row_count,
        active_count=active_count,
        blank_count=blank_count,
        property_chain_count=chain_count,
    )


def validate_selected_rows(governed: GovernedComsRows, selected: Iterable[CanonicalRowInput],
                           mapping_types: Iterable[str]) -> None:
    """Reject omissions, duplicates, substitutions, blanks, or wrong-backend rows."""
    selected_types = frozenset(mapping_types)
    expected = tuple(sorted((row for row in governed.canonical_rows
                             if row.mapping_type in selected_types), key=lambda row: row.row_id))
    if tuple(sorted(selected, key=lambda row: row.row_id)) != expected:
        raise ValueError("ROBOT selected rows differ from the authenticated backend partition")


def canonical_expected_axioms(
    processed_rows: Iterable[coms.ProcessedRow],
    mapping_types: Iterable[str],
) -> dict[str, str]:
    """Return authoritative canonical axioms for the selected mapping types."""

    selected_types = frozenset(mapping_types)
    expected: dict[str, str] = {}

    for processed in processed_rows:
        row = coms.canonical_input_for_processed_row(processed)
        if row.mapping_type not in selected_types:
            continue
        if processed.identity_audit is None:
            raise ValueError(
                f"{row.row_id}: canonical identity audit is missing"
            )

        for identity in processed.identity_audit.authoritative_axioms:
            axiom_id = (
                "sha256:"
                + hashlib.sha256(
                    identity.canonical_axiom.encode("utf-8")
                ).hexdigest()
            )
            previous = expected.get(axiom_id)
            if previous is not None and previous != identity.canonical_axiom:
                raise ValueError(
                    f"{row.row_id}: canonical axiom hash collision"
                )
            expected[axiom_id] = identity.canonical_axiom

    return expected


def canonical_axioms_from_turtle(path: Path) -> dict[str, str]:
    """Canonicalize supported OWL axioms from a ROBOT-produced Turtle graph."""

    graph = Graph().parse(path, format="turtle")
    return {
        axiom_id: value[0]
        for axiom_id, value in modular._canonical_graph_axioms(
            graph,
            ignore_unsupported=True,
        ).items()
    }


def compare_canonical_axioms(
    expected: dict[str, str],
    actual: dict[str, str],
) -> CanonicalAxiomComparison:
    """Compare exact canonical axiom identities and expressions."""

    shared = set(expected) & set(actual)
    return CanonicalAxiomComparison(
        expected=expected,
        actual=actual,
        missing_axiom_ids=tuple(sorted(set(expected) - set(actual))),
        extra_axiom_ids=tuple(sorted(set(actual) - set(expected))),
        mismatched_axiom_ids=tuple(
            sorted(
                axiom_id
                for axiom_id in shared
                if expected[axiom_id] != actual[axiom_id]
            )
        ),
    )


def resolve_robot_path(robot_path: str | None = None) -> str:
    """Return the explicit or PATH-resolved ROBOT executable."""

    resolved = robot_path or shutil.which("robot")
    if resolved is None:
        raise RuntimeError("ROBOT executable not found on PATH")
    return resolved


def combined_process_output(stdout: str, stderr: str) -> str:
    """Combine subprocess output using the repository's existing convention."""

    return "\n".join(
        part
        for part in (
            stdout.strip(),
            stderr.strip(),
        )
        if part
    )
