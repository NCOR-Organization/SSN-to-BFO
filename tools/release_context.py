#!/usr/bin/env python3
"""Validate explicit immutable formal-release identity inputs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable


RELEASE_IDENTIFIER_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
SOURCE_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
CONTEXT_FIELDS = (
    "release_identifier",
    "release_date",
    "git_tag",
    "source_commit",
)


@dataclass(frozen=True)
class FormalReleaseValidationIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class FormalReleaseContext:
    release_identifier: str
    release_date: str
    git_tag: str
    source_commit: str


class FormalReleaseContextError(ValueError):
    """One or more deterministic formal-release context failures."""

    def __init__(self, issues: Iterable[FormalReleaseValidationIssue]):
        self.issues = tuple(issues)
        super().__init__("; ".join(format_issue(issue) for issue in self.issues))


def format_issue(issue: FormalReleaseValidationIssue) -> str:
    return f"ERROR [{issue.code}] {issue.field}: {issue.message}"


def _issue(code: str, field: str, message: str) -> FormalReleaseValidationIssue:
    return FormalReleaseValidationIssue(code=code, field=field, message=message)


def _canonical_date_issue(value: object, field: str) -> FormalReleaseValidationIssue | None:
    if not isinstance(value, str) or RELEASE_IDENTIFIER_PATTERN.fullmatch(value) is None:
        return _issue(
            "RELEASE_DATE_FORMAT" if field == "release_date" else "RELEASE_ID_FORMAT",
            field,
            "expected exactly YYYY-MM-DD",
        )
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return _issue(
            "RELEASE_DATE_INVALID",
            field,
            f"invalid Gregorian calendar date: {value}",
        )
    if parsed.isoformat() != value:
        return _issue(
            "RELEASE_DATE_FORMAT" if field == "release_date" else "RELEASE_ID_FORMAT",
            field,
            "expected a zero-padded Gregorian date in YYYY-MM-DD form",
        )
    return None


def validate_release_identifier(value: object) -> str:
    """Return one canonical date release identifier or raise deterministic issues."""

    problem = _canonical_date_issue(value, "release_identifier")
    if problem is not None:
        raise FormalReleaseContextError((problem,))
    assert isinstance(value, str)
    return value


def expected_git_tag(release_identifier: object) -> str:
    return "v" + validate_release_identifier(release_identifier)


def formal_release_context_issues(
    release_identifier: object,
    release_date: object,
    git_tag: object,
    source_commit: object,
) -> tuple[FormalReleaseValidationIssue, ...]:
    """Return all context issues in stable field and policy order."""

    issues: list[FormalReleaseValidationIssue] = []
    identifier_problem = _canonical_date_issue(release_identifier, "release_identifier")
    if identifier_problem is not None:
        issues.append(identifier_problem)

    date_problem = _canonical_date_issue(release_date, "release_date")
    if date_problem is not None:
        issues.append(date_problem)

    if identifier_problem is None and date_problem is None and release_date != release_identifier:
        issues.append(
            _issue(
                "RELEASE_DATE_MISMATCH",
                "release_date",
                f"expected {release_identifier}, got {release_date}",
            )
        )

    if not isinstance(git_tag, str) or re.fullmatch(r"v[0-9]{4}-[0-9]{2}-[0-9]{2}", git_tag) is None:
        issues.append(_issue("GIT_TAG_FORMAT", "git_tag", "expected exactly vYYYY-MM-DD"))
    elif identifier_problem is None and git_tag != f"v{release_identifier}":
        issues.append(
            _issue(
                "RELEASE_TAG_MISMATCH",
                "git_tag",
                f"expected v{release_identifier}, got {git_tag}",
            )
        )

    if not isinstance(source_commit, str) or SOURCE_COMMIT_PATTERN.fullmatch(source_commit) is None:
        issues.append(
            _issue(
                "SOURCE_COMMIT_FORMAT",
                "source_commit",
                "expected exactly 40 lowercase hexadecimal characters",
            )
        )
    return tuple(issues)


def parse_formal_release_context(
    release_identifier: object = None,
    release_date: object = None,
    git_tag: object = None,
    source_commit: object = None,
) -> FormalReleaseContext:
    """Validate explicit values and return one frozen formal-release context."""

    issues = formal_release_context_issues(
        release_identifier,
        release_date,
        git_tag,
        source_commit,
    )
    if issues:
        raise FormalReleaseContextError(issues)
    assert isinstance(release_identifier, str)
    assert isinstance(release_date, str)
    assert isinstance(git_tag, str)
    assert isinstance(source_commit, str)
    return FormalReleaseContext(
        release_identifier=release_identifier,
        release_date=release_date,
        git_tag=git_tag,
        source_commit=source_commit,
    )


def validate_formal_release_context(context: object) -> FormalReleaseContext:
    if not isinstance(context, FormalReleaseContext):
        raise FormalReleaseContextError(
            (_issue("RELEASE_CONTEXT_TYPE", "release_context", "expected FormalReleaseContext"),)
        )
    return parse_formal_release_context(
        context.release_identifier,
        context.release_date,
        context.git_tag,
        context.source_commit,
    )


# Release identity stays immutable and independent of any workbook state. The
# companion below binds semantic expectations only after existing current-track
# custody and deterministic-product authentication have succeeded.
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class FormalProductExpectation:
    key: str
    serialized_bytes: bytes
    sha256: str
    byte_size: int
    logical_triple_count: int
    total_triple_count: int
    direct_governed_axiom_count: int
    governed_closure_axiom_count: int
    fixed_closure_triple_count: int
    profile_triple_count: int
    profile_declaration_completion_count: int


@dataclass(frozen=True)
class ReleaseExpectations:
    context: FormalReleaseContext
    repository_root: Path
    input_sha256: tuple[tuple[str, str], ...]
    products: tuple[FormalProductExpectation, ...]

    def product(self, key: str) -> FormalProductExpectation:
        return next(value for value in self.products if value.key == key)

    @property
    def fixed_closure_counts(self) -> tuple[tuple[str, int], ...]:
        return tuple((value.key, value.fixed_closure_triple_count) for value in self.products)


_ACTIVE_RELEASE: ContextVar[ReleaseExpectations | None] = ContextVar(
    "authenticated_current_release", default=None
)


def active_release_expectations() -> ReleaseExpectations | None:
    return _ACTIVE_RELEASE.get()


def _release_input_signature(root: Path) -> tuple[tuple[str, str], ...]:
    import current_source_identity as identity

    paths = {identity.WORKBOOK, str(identity.RECORD), *identity.PRODUCTS,
             *identity.SOURCES, *identity.TARGETS, *identity.CONFIGURATION,
             "reports/coms-product-dispositions.json",
             "mappings/current-ssn-sosa-assessment.json"}
    for directory in ("reports/current-documentary-workbook", "reports/current-semantic-workbook",
                      "reports/current-human-decisions", "reports/current-decision-applicability",
                      "reports/retained-evidence"):
        paths.update(path.relative_to(root).as_posix() for path in (root / directory).rglob("*")
                     if path.is_file())
    paths.update(path.relative_to(root).as_posix() for path in (root / "tools").glob("*.py"))
    result = []
    for relative in sorted(paths):
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"release preflight requires a regular governed input: {relative}")
        result.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(result)


@contextmanager
def authenticated_release_expectations(root: Path, context: FormalReleaseContext):
    """Bind current formal expectations to authenticated inputs, never candidates.

    Historical repositories keep their original exact release contract. Current
    semantic evolution must pass the existing mixed history and source/product
    identity authorities before it can supply different exact expectations.
    """
    import current_semantic_generation as generation
    import current_semantic_workbook as semantic
    import current_source_identity as identity
    import generate_mapping_from_coms as mapping
    import modular_products as modular
    from build_release import render_formal_products

    root = Path(root).resolve()
    context = validate_formal_release_context(context)
    if not (root / semantic.TRANSITIONS).exists():
        token = _ACTIVE_RELEASE.set(None)
        try:
            # A historical build nested inside a current build must also use
            # the original generation counts. Restore both scopes on exit.
            with generation._snapshot_context(None):
                yield None
        finally:
            _ACTIVE_RELEASE.reset(token)
        return
    signature = _release_input_signature(root)
    active = active_release_expectations()
    if (active is not None and active.repository_root == root and
            active.context == context and active.input_sha256 == signature):
        yield active
        if _release_input_signature(root) != signature:
            raise ValueError("release inputs changed after authenticated build/validation")
        return
    with generation.generated_expectations_context(root, root / identity.WORKBOOK):
        # Bind the identity document itself to trusted Git, then use its full
        # source/target/configuration/history/product checks, not just hashes
        # supplied by the candidate or an editable manifest.
        trusted = subprocess.check_output([
            "git", "-C", str(root), "show",
            f"{identity.ACCEPTED_CHECKPOINT_HEAD}:{identity.RECORD.as_posix()}",
        ])
        if (root / identity.RECORD).read_bytes() != trusted:
            raise ValueError("release preflight identity record differs from accepted Git bytes")
        errors = identity.check_record(json.loads(trusted), root)
        if errors:
            raise ValueError("release preflight authentication failed: " + " | ".join(errors))
        _, rendered = render_formal_products(
            context, root / identity.WORKBOOK, root / "config/publication-metadata.toml",
            root / "reports/coms-product-dispositions.json",
        )
        values = {key: getattr(rendered, key) for key in
                  ("integrated", "alignment_core", "strict_bfo_mapping", "cco_extension")}
        sources = tuple(root / path for path in mapping.SOURCE_IMPORTS)
        dependencies = (*sources, root / mapping.BFO_VALIDATION_DEPENDENCY)
        members = {"integrated": ("integrated",), "alignment_core": ("alignment_core",),
                   "strict_bfo_mapping": ("alignment_core", "strict_bfo_mapping"),
                   "cco_extension": ("alignment_core", "strict_bfo_mapping", "cco_extension")}
        counts = {
            "integrated": generation.expected_count("ROOT_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT", mapping.ROOT_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT),
            "alignment_core": generation.expected_count("ALIGNMENT_CORE_FIXED_CLOSURE_TRIPLE_COUNT", modular.ALIGNMENT_CORE_FIXED_CLOSURE_TRIPLE_COUNT) + 3,
            "strict_bfo_mapping": generation.expected_count("STRICT_BFO_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT", modular.STRICT_BFO_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT),
            "cco_extension": generation.expected_count("CCO_EXTENSION_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT", modular.CCO_EXTENSION_FORMAL_FIXED_CLOSURE_TRIPLE_COUNT),
        }
        products = []
        for key, result in values.items():
            closure = modular.build_fixed_validation_closure(
                (values[member].serialized_bytes for member in members[key]),
                sources if key == "alignment_core" else dependencies,
            )
            if len(closure) != counts[key]:
                raise ValueError(f"authenticated formal closure differs from transition: {key}")
            completions = sum(triple not in closure for triple in mapping.DL_PROFILE_DECLARATION_COMPLETION)
            products.append(FormalProductExpectation(
                key=key, serialized_bytes=result.serialized_bytes, sha256=result.sha256,
                byte_size=len(result.serialized_bytes), logical_triple_count=result.logical_triple_count,
                total_triple_count=result.total_triple_count,
                direct_governed_axiom_count=result.governed_axiom_count,
                governed_closure_axiom_count=sum(values[member].governed_axiom_count for member in members[key]),
                fixed_closure_triple_count=len(closure), profile_triple_count=len(closure) + completions,
                profile_declaration_completion_count=completions,
            ))
        if _release_input_signature(root) != signature:
            raise ValueError("release inputs changed during preflight authentication")
        expected = ReleaseExpectations(context, root, signature, tuple(products))
        token = _ACTIVE_RELEASE.set(expected)
        try:
            yield expected
        finally:
            _ACTIVE_RELEASE.reset(token)
        if _release_input_signature(root) != signature:
            raise ValueError("release inputs changed after authenticated build/validation")
