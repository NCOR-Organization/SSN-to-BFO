#!/usr/bin/env python3
"""Regression gates for retired placeholders and development catalogs."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import fnmatch
import json
import posixpath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from rdflib import Graph, OWL, RDFS


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_release  # noqa: E402
import current_source_identity as identity  # noqa: E402
import current_validation_scope as validation_scope  # noqa: E402
import publication_metadata  # noqa: E402
import release_archive  # noqa: E402
import release_context  # noqa: E402
import workflow_check as workflow  # noqa: E402


CATALOG_NAMESPACE = "urn:oasis:names:tc:entity:xmlns:xml:catalog"
REMOVED_PATHS = (
    "imports/catalog-v001.xml",
    "releases/current-ssn-sosa/ssn-sosa-bfo-directmappings.ttl",
    "releases/current-ssn-sosa/ssn-sosa-cco-directmappings.ttl",
    "releases/sosa-next/sosa-bfo-directmappings.ttl",
    "releases/sosa-next/sosa-cco-directmappings.ttl",
    "src/current-ssn-sosa/catalog-v001.xml",
    "src/current-ssn-sosa/ssn-sosa-mappings-edit.ttl",
    "src/current-ssn-sosa/sparql/artifact-metadata.rq",
    "src/current-ssn-sosa/sparql/construct/README.md",
    "src/current-ssn-sosa/sparql/construct/derive-bfo-from-cco.rq",
    "src/current-ssn-sosa/sparql/report/unprojectable-cco-targets.rq",
)
RETIRED_IGNORED_OUTPUTS = (
    "src/current-ssn-sosa/build/artifacts/current-ssn-sosa-bfo-only-generated.ttl",
    "src/current-ssn-sosa/build/artifacts/current-ssn-sosa-bfo-only-skipped-cco-targets.csv",
    "src/current-ssn-sosa/build/artifacts/current-ssn-sosa-projection-catalog.xml",
)
RETIRED_PLACEHOLDER_HASHES = frozenset(
    {
        "397fc7a1566afddc271fee066dc55311f9b61c4be887212be84d6ae9462df3e8",
        "33e616a74bd959fec6128779dddee7fb52e2faca8f5669d9ff5faab079a408f1",
        "0e814b9e9bdb03cca73bb15e307b2d0ca13424f0c19775aa0feaf440c2879a18",
        "1bf9de31bf344c9b90c673cf3bab05467a7bb1026f8cb36d27e25cb9fabcfd2b",
    }
)
RETIRED_REFERENCE_TERMS = (
    "ssn-sosa-bfo-directmappings.ttl",
    "ssn-sosa-cco-directmappings.ttl",
    "sosa-bfo-directmappings.ttl",
    "sosa-cco-directmappings.ttl",
    "ssn-sosa-mappings-edit.ttl",
    "derive-bfo-from-cco",
    "unprojectable-cco-targets",
    "current-ssn-sosa-bfo-only-generated.ttl",
    "current-ssn-sosa-bfo-only-skipped-cco-targets.csv",
    "current-ssn-sosa-projection-catalog.xml",
    "https://w3id.org/ssn-sosa-bfo-cco-mapping/current-ssn-sosa/bfo",
    "https://w3id.org/ssn-sosa-bfo-cco-mapping/current-ssn-sosa/cco",
    "https://w3id.org/ssn-sosa-bfo-cco-mapping/current-ssn-sosa/edit",
    "https://w3id.org/ssn-sosa-bfo-cco-mapping/sosa-next/bfo",
    "https://w3id.org/ssn-sosa-bfo-cco-mapping/sosa-next/cco",
    "https://w3id.org/ssn-sosa-bfo-cco-mapping/sosa-next/edit",
)
HISTORICAL_REFERENCE_ALLOWLIST = frozenset(
    {
        "reports/current-ssn-sosa-release-readiness-audit.md",
        "reports/prov-functional-parity-audit.md",
        "reports/publication-product-and-import-policy.md",
        "reports/sosa-import-closure-fidelity-audit.md",
        "reports/sosa-next-product-contract.md",
    }
)
NEGATIVE_GUARD_PATHS = frozenset(
    {
        "tests/test_placeholder_catalog_migration.py",
        "tools/workflow_check.py",
        "tools/current_validation_scope.py",
    }
)

SOSA_NEXT_ARTIFACT_HASHES = {
    "releases/sosa-next/sosa-integrated.ttl":
        "3f502821476478252cdd9feb316b47612daa473e511597970a1351617d5cfc12",
    "releases/sosa-next/sosa-bfo-mapping.ttl":
        "1ae415bc96940e4007d064102f556aa544593616a0eff984534406028b846efb",
    "releases/sosa-next/sosa-cco-extension.ttl":
        "53a7cc6c0f664e51bf9f7ac28e3d067fc4fdcc750e22a34fe5c12c766e51dc19",
    "releases/sosa-next/sosa-ro-mapping.ttl":
        "1747563c4bba01a0c6b34bd61660a1f0c9026c266cc147991e74bc1d314ac388",
    "src/sosa-next/sosa-mappings-edit.ttl":
        "4999c2e73ef3b4959f4d0c3b4d0a133a1293dcc5920363ae9c34c7182d2dde76",
}

SOSA_NEXT_RELEASE_FILES = (
    "../../releases/sosa-next/sosa-integrated.ttl",
    "../../releases/sosa-next/sosa-bfo-mapping.ttl",
    "../../releases/sosa-next/sosa-cco-extension.ttl",
    "../../releases/sosa-next/sosa-ro-mapping.ttl",
)
DEPENDENCY_HASHES = {
    "imports/cco.ttl": "3ad8f098ecb3d7ca27464a1edf2795b90c69573843447d51f090e6f1b30694f4",
    "imports/sosa.ttl": "0dad03b30c7fdd085e2629dfc0ebd10bb1dacbda73b2c375fb295ab6861ffb33",
    "imports/sosa-sampling.ttl": "f6e1d9451732bb132fa4ba567ca58fba752dcfbb43e66c5d4b660963bd0f7c1a",
    "imports/ssn.ttl": "434b50fecb32e14b30aac28310a76935a33fdc397e70fce887fd653069a59383",
    "imports/ssn-systems.ttl": "156870689643840c861aaead206458bcdfc9cded5f7107598dbf87e015861105",
}
# Immutable development-product identities at the accepted checkpoint.
HISTORICAL_PRODUCT_HASHES = {
    "SSN2BFO.ttl": "c31997d7e7b8c5e0bffd3f23a4597ab4be80786978462fefe800c4c7a5dc0c11",
    "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl":
        "17695ef17379924449153b2c92ffaed6b57d497a1b2d1e854f584614cebec770",
    "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl":
        "676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af",
    "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl":
        "2908f89648d42dc928f7225056216f1cbf3bcdc79de1bcf770b40a017a5e9bf5",
}
SOSA_NEXT_CATALOG_MAPPINGS = (
    (
        "http://www.w3.org/ns/sosa/",
        "imports/sosa.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/common/",
        "imports/sosa-common.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/act/",
        "imports/sosa-actuation.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/dep/",
        "imports/sosa-deprecated.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/obs/",
        "imports/sosa-observation.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/sam/",
        "imports/sosa-sampling.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/systems/",
        "imports/sosa-system.ttl",
    ),
    (
        "http://www.w3.org/ns/sosa/sampling/",
        "imports/sample-relations.ttl",
    ),
    (
        "http://www.sks.ai/SSN2BFO/development/"
        "sosa-next/source-declaration-overlay",
        "imports/sosa-source-declaration-overlay.ttl",
    ),
    (
        "https://www.commoncoreontologies.org/"
        "CommonCoreOntologiesMerged",
        "imports/cco.ttl",
    ),
    (
        "http://purl.obolibrary.org/obo/"
        "ro/ro-full.owl",
        "imports/ro-full.owl",
    ),
    (
        "http://purl.obolibrary.org/obo/"
        "ro/releases/2025-12-17/ro-full.owl",
        "imports/ro-full.owl",
    ),
    (
        "http://www.sks.ai/SSN2BFO/development/"
        "sosa-next/integrated",
        "../../releases/sosa-next/sosa-integrated.ttl",
    ),
    (
        "http://www.sks.ai/SSN2BFO/development/"
        "sosa-next/bfo-mapping",
        "../../releases/sosa-next/sosa-bfo-mapping.ttl",
    ),
    (
        "http://www.sks.ai/SSN2BFO/development/"
        "sosa-next/cco-extension",
        "../../releases/sosa-next/sosa-cco-extension.ttl",
    ),
    (
        "http://www.sks.ai/SSN2BFO/development/"
        "sosa-next/ro-mapping",
        "../../releases/sosa-next/sosa-ro-mapping.ttl",
    ),
    (
        "http://www.sks.ai/SSN2BFO/development/"
        "sosa-next/edit",
        "sosa-mappings-edit.ttl",
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checkpoint_bytes(relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "show",
         f"{identity.ACCEPTED_CHECKPOINT_HEAD}:{relative}"]
    )


def tracked_paths(pattern: str | None = None) -> tuple[str, ...]:
    """Versioned migration-guard inputs, independent of future evidence/index.

    Keep every checkpoint report previously scanned; inspect all maintained
    non-report candidates, including untracked files, before publication. The
    scope policy and this consumer share exactly the same dependency inventory.
    """
    paths = validation_scope.migration_guard_paths(REPO_ROOT)
    return tuple(sorted(path for path in paths
                        if pattern is None or fnmatch.fnmatchcase(path, pattern)))


def reference_tokens(text: str) -> list[str]:
    """Separate exact structured paths from punctuation in unquoted prose."""
    structured = re.compile(
        r"\[[^\]\n]*\]\((?P<link>(?:\\.|[^\\()\n]|\((?:\\.|[^\\()\n])*\))*)\)"
        r'|(?P<json>"(?:\\.|[^"\\])*")'
        r"|(?<!\w)'(?P<quoted>[^'\n]*)'(?!\w)"
        r"|(?<!`)(?P<ticks>`+)(?!`)(?P<code>[^\n]*?)(?P=ticks)(?!`)"
        r"|<(?P<angle>[^\s<>]+)>",
        re.DOTALL,
    )
    tokens: list[str] = []
    prose = list(text)
    for match in structured.finditer(text):
        if match.group("json") is not None:
            try:
                value = json.loads(match.group("json"))
            except json.JSONDecodeError:
                value = match.group("json")[1:-1]
        elif match.group("link") is not None:
            value = match.group("link").strip()
            if value.startswith("<") and ">" in value:
                value = value[1:value.index(">")]
            else:
                # A Markdown title is not part of its destination. Escaped
                # punctuation in the destination is an actual path character.
                value = re.split(r"\s+['\"]", value, maxsplit=1)[0]
            value = re.sub(r"\\([\\`*{}\[\]()#+\-.!_> ])", r"\1", value)
        else:
            value = next(match.group(name) for name in ("quoted", "code", "angle")
                         if match.group(name) is not None)
        if (match.group("link") is None and match.group("angle") is None
                and re.search(r"\s", value)):
            # A structured field/span can hold prose or a command rather than
            # one path. Parse its contents again so embedded path references
            # remain visible, including exact quoted arguments within commands.
            tokens.extend(reference_tokens(value))
        else:
            tokens.append(value)
        prose[match.start():match.end()] = " " * (match.end() - match.start())

    # Only bare text tokens have sentence punctuation. A single quoted/code
    # path, link destination or percent-encoded filename is kept exact; there
    # a final '.', ':', ')' or similar character belongs to the path.
    for token in re.findall(r"[^\s`\"'<>|]+", "".join(prose)):
        while token:
            if token[-1] in ".,;:":
                token = token[:-1]
            elif token[0] in ("(", "[", "{") and token[-1] == {
                    "(": ")", "[": "]", "{": "}"}[token[0]]:
                token = token[1:-1]
            elif token[-1] in ")]}" and token.count(token[-1]) > token.count(
                    {")": "(", "]": "[", "}": "{"}[token[-1]]):
                token = token[:-1]
            else:
                break
        if token:
            tokens.append(token)
    return tokens


def retired_references(text: str, relative: str) -> list[str]:
    """Match retired logical paths, retaining separate command/name/IRI guards."""
    paths: set[str] = set()
    for token in reference_tokens(text):
        try:
            reference = urlsplit(token)
        except ValueError:
            continue
        if reference.scheme not in {"", "file"} or reference.netloc not in {"", "localhost"}:
            continue
        path = posixpath.normpath(unquote(reference.path))
        if path.startswith("/"):
            paths.add(posixpath.relpath(path, REPO_ROOT.as_posix()))
        else:
            paths.add(path)
            paths.add(posixpath.normpath(posixpath.join(posixpath.dirname(relative), path)))
    matched = paths.intersection((*REMOVED_PATHS, *RETIRED_IGNORED_OUTPUTS))
    matched.update(term for term in RETIRED_REFERENCE_TERMS if term in text)
    return sorted(matched)


class PlaceholderCatalogMigrationTests(unittest.TestCase):
    def authenticated_current_product_identities(self) -> dict[str, dict]:
        trusted = checkpoint_bytes(identity.RECORD.as_posix())
        self.assertEqual((REPO_ROOT / identity.RECORD).read_bytes(), trusted)
        historical = {item["path"]: item for item in json.loads(trusted)["products"]}
        self.assertEqual(
            {path: item["sha256"] for path, item in historical.items()},
            HISTORICAL_PRODUCT_HASHES,
        )
        evolution = identity.validated_product_evolution(REPO_ROOT, historical)
        self.assertEqual(evolution["status"], "VALIDATED")
        self.assertEqual(set(evolution["products"]), set(HISTORICAL_PRODUCT_HASHES))
        return evolution["products"]

    def test_retired_current_paths_and_ignored_outputs_are_absent(self) -> None:
        for relative in (*REMOVED_PATHS, *RETIRED_IGNORED_OUTPUTS):
            with self.subTest(path=relative):
                path = REPO_ROOT / relative
                self.assertFalse(path.exists())
                self.assertFalse(path.is_symlink())

    def test_retired_placeholder_bytes_do_not_survive_as_tracked_regular_files(self) -> None:
        matches: list[str] = []
        for relative in tracked_paths():
            path = REPO_ROOT / relative
            try:
                mode = path.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISREG(mode) and sha256(path) in RETIRED_PLACEHOLDER_HASHES:
                matches.append(relative)
        self.assertEqual(matches, [])

    def assert_retired_reference_locations(self, occurrences: dict[str, list[str]]) -> None:
        retained = set(occurrences).intersection(HISTORICAL_REFERENCE_ALLOWLIST)
        active = {path: terms for path, terms in occurrences.items()
                  if path not in HISTORICAL_REFERENCE_ALLOWLIST}
        self.assertEqual(retained, set(HISTORICAL_REFERENCE_ALLOWLIST), occurrences)
        self.assertEqual(len(retained), 5)
        self.assertEqual(active, {}, "Active retired references: " + repr(active))

    def test_retired_path_matching_disambiguates_shared_basename(self) -> None:
        retired = "src/current-ssn-sosa/sparql/artifact-metadata.rq"
        maintained = "src/sosa-next/sparql/artifact-metadata.rq"
        self.assertEqual(PurePosixPath(retired).name, PurePosixPath(maintained).name)
        for reference in (
            retired, "./" + retired,
            "src/sosa-next/../current-ssn-sosa/sparql/artifact-metadata.rq",
            str(REPO_ROOT / retired), (REPO_ROOT / retired).as_uri(),
            f"`{retired}`", f"[query]({retired}#L1)",
            json.dumps({"path": retired}),
            json.dumps(retired).replace("/", r"\/"),
            json.dumps(retired).replace("/", r"\u002f"),
            retired.replace("/", "%2F"),
        ):
            with self.subTest(retired_reference=reference):
                self.assertIn(retired, retired_references(reference, "README.md"))
        self.assertIn(retired, retired_references(
            "../src/current-ssn-sosa/sparql/artifact-metadata.rq", "docs/guide.md"))
        for reference in (
            maintained, str(REPO_ROOT / maintained),
            (REPO_ROOT / maintained).as_uri(), f"[query]({maintained})",
            json.dumps({"path": maintained}),
            "artifact-metadata.rq", "src/*/sparql/artifact-metadata.rq",
            "other/" + retired, retired + ".bak", retired + "/child",
            "src/current-ssn-sosa/../sosa-next/sparql/artifact-metadata.rq",
        ):
            with self.subTest(other_reference=reference):
                self.assertEqual(retired_references(reference, "README.md"), [])
        retained = {path: [REMOVED_PATHS[0]] for path in HISTORICAL_REFERENCE_ALLOWLIST}
        self.assert_retired_reference_locations(retained)
        active = "docs/new-active-reference.md"
        with self.assertRaisesRegex(AssertionError, "Active retired references"):
            self.assert_retired_reference_locations({
                **retained, active: retired_references(f"[query](../{retired})", active),
            })

    def test_retired_references_occur_only_in_enumerated_historical_reports(self) -> None:
        occurrences: dict[str, list[str]] = {}
        for relative in tracked_paths():
            if relative in NEGATIVE_GUARD_PATHS:
                continue
            path = REPO_ROOT / relative
            try:
                if not stat.S_ISREG(path.lstat().st_mode):
                    continue
                text = path.read_text(encoding="utf-8")
            except (FileNotFoundError, UnicodeDecodeError):
                continue
            matched = retired_references(text, relative)
            if matched:
                occurrences[relative] = matched
        self.assert_retired_reference_locations(occurrences)

    def test_retired_paths_accept_prose_punctuation_without_trimming_literal_paths(self) -> None:
        retired = "src/current-ssn-sosa/sparql/artifact-metadata.rq"
        maintained = "src/sosa-next/sparql/artifact-metadata.rq"
        for punctuation in (".", ",", ";", ":", ")", "]", ").", "]:"):
            for path in (retired, maintained):
                with self.subTest(path=path, punctuation=punctuation):
                    self.assertEqual(
                        retired_references(f"Use {path}{punctuation} Then continue.", "README.md"),
                        [retired] if path == retired else [],
                    )
        for reference in (
            f"({retired}).", f"[{retired}];", f"`{retired}`.", f"``{retired}``:",
            f'"{retired}",', f"'{retired}';", f"<{retired}>.",
            f"[query]({retired}).", f'[query]({retired} "Query title");',
            json.dumps({"path": retired}),
            f"```text\n{retired}\n```", f"```json\n{json.dumps({'path': retired})}\n```",
        ):
            with self.subTest(reference=reference):
                self.assertEqual(retired_references(reference, "README.md"), [retired])

        # Explicit string/link boundaries and encoding disambiguate a literal
        # trailing path character from sentence punctuation. Internal path
        # punctuation and distinct filename suffixes must likewise survive.
        for suffix in (".", ",", ";", ":", ")", "]", ".bak", ":backup", ";backup",
                       ",backup", ")backup", "]backup", "/child"):
            distinct = retired + suffix
            for reference in (json.dumps(distinct), f"`{distinct}`",
                              f"'{distinct}'", f"<{distinct}>"):
                with self.subTest(literal_reference=reference):
                    self.assertEqual(retired_references(reference, "README.md"), [])
        for reference in (
            retired + ".bak", retired + ":backup", retired + ";backup",
            retired + ",backup", retired + ")backup", retired + "]backup",
            retired + "%2E", retired + "%3A", retired + "%29",
            f"[different]({retired}.bak)", f"[different]({retired}.)",
            f"[different]({retired}\\))", "prefix,with;punctuation/" + retired,
            "prefix(with)[punctuation]/" + retired, "(" + retired, "[" + retired,
        ):
            with self.subTest(distinct_reference=reference):
                self.assertEqual(retired_references(reference, "README.md"), [])

    def test_quoted_prose_and_commands_preserve_embedded_reference_detection(self) -> None:
        retired = "src/current-ssn-sosa/sparql/artifact-metadata.rq"
        maintained = "src/sosa-next/sparql/artifact-metadata.rq"
        for path in (retired, maintained):
            for reference in (
                json.dumps({"description": f"Use {path}."}),
                json.dumps(f"Use `{path}`; then continue."),
                f'"Use {path}."', f"'Use {path}; then continue.'",
                f"`python {path}`", f"``python {path}``",
                json.dumps({"command": f"python {path}"}),
                f"`python '{path}'`",
            ):
                with self.subTest(reference=reference):
                    self.assertEqual(retired_references(reference, "README.md"),
                                     [retired] if path == retired else [])
        for suffix in (".", ":", ")", ".bak", ";backup"):
            distinct = retired + suffix
            for reference in (
                f"`python '{distinct}'`",
                json.dumps({"command": f'python "{distinct}"'}),
                json.dumps({"description": f"Use `{distinct}` instead."}),
            ):
                with self.subTest(literal_argument=reference):
                    self.assertEqual(retired_references(reference, "README.md"), [])

    def test_sosa_next_products_and_editor_are_byte_preserved_and_parseable(self) -> None:
        for relative, expected_hash in SOSA_NEXT_ARTIFACT_HASHES.items():
            with self.subTest(path=relative):
                path = REPO_ROOT / relative
                self.assertTrue(
                    stat.S_ISREG(
                        path.lstat().st_mode
                    )
                )
                self.assertEqual(
                    sha256(path),
                    expected_hash,
                )
                self.assertGreater(
                    len(
                        Graph().parse(
                            path,
                            format="turtle",
                        )
                    ),
                    0,
                )

    def test_sosa_next_makefile_exposes_exact_maintained_products(self) -> None:
        output = subprocess.check_output(
            [
                "make",
                "-s",
                "output-release-filepaths",
            ],
            cwd=REPO_ROOT / "src/sosa-next",
            text=True,
        )
        self.assertEqual(
            tuple(output.splitlines()),
            SOSA_NEXT_RELEASE_FILES,
        )

    def test_pinned_dependencies_are_preserved_parseable_and_logically_nonempty(self) -> None:
        parsed: dict[str, Graph] = {}
        for relative, expected_hash in DEPENDENCY_HASHES.items():
            with self.subTest(path=relative):
                path = REPO_ROOT / relative
                self.assertTrue(stat.S_ISREG(path.lstat().st_mode))
                self.assertEqual(sha256(path), expected_hash)
                parsed[relative] = Graph().parse(path, format="turtle")
                self.assertGreater(len(parsed[relative]), 0)
        cco_path = REPO_ROOT / "imports/cco.ttl"
        self.assertGreater(cco_path.stat().st_size, 1_000_000)
        logical_predicates = {RDFS.subClassOf, RDFS.subPropertyOf, OWL.equivalentClass}
        self.assertTrue(any(predicate in logical_predicates for _, predicate, _ in parsed["imports/cco.ttl"]))

    def test_remaining_tracked_catalog_is_safe_and_has_exact_sosa_next_mappings(self) -> None:
        catalogs = tuple(
            relative
            for relative in tracked_paths("*catalog*.xml")
            if (REPO_ROOT / relative).is_file()
        )
        self.assertEqual(catalogs, ("src/sosa-next/catalog-v001.xml",))
        catalog_path = REPO_ROOT / catalogs[0]
        root = ElementTree.parse(catalog_path).getroot()
        self.assertEqual(root.tag, f"{{{CATALOG_NAMESPACE}}}catalog")
        entries = tuple(
            (child.attrib["name"], child.attrib["uri"])
            for child in root.findall(
                f".//{{{CATALOG_NAMESPACE}}}uri"
            )
        )

        self.assertEqual(
            len(entries),
            len(SOSA_NEXT_CATALOG_MAPPINGS),
        )
        self.assertEqual(
            len({name for name, _ in entries}),
            len(entries),
        )
        self.assertEqual(
            dict(entries),
            dict(SOSA_NEXT_CATALOG_MAPPINGS),
        )

        for name, target in entries:
            with self.subTest(name=name, target=target):
                self.assertTrue(name)
                self.assertFalse(PurePosixPath(target).is_absolute())
                self.assertNotIn("\\", target)
                self.assertNotIn("/Users/", target)

                resolved = (catalog_path.parent / target).resolve()
                self.assertTrue(resolved.is_file())
                self.assertTrue(
                    resolved.is_relative_to(REPO_ROOT.resolve())
                )

    def test_formal_package_catalog_uses_production_generator_and_governed_order(self) -> None:
        metadata = publication_metadata.load_metadata(REPO_ROOT / "config/publication-metadata.toml")
        context = release_context.parse_formal_release_context(
            "2099-01-02",
            "2099-01-02",
            "v2099-01-02",
            "0123456789abcdef0123456789abcdef01234567",
        )
        value = build_release.canonical_catalog_bytes(metadata, context)
        self.assertEqual(build_release.validate_catalog_bytes(value, metadata, context), ())
        root = ElementTree.fromstring(value)
        entries = tuple(
            (child.attrib["name"], child.attrib["uri"])
            for child in root.findall(f"{{{CATALOG_NAMESPACE}}}uri")
        )
        expected = tuple(
            (
                publication_metadata.release_version_iri(metadata, key, context),
                build_release.PRODUCT_PACKAGE_PATHS[key],
            )
            for key in publication_metadata.PRODUCT_ORDER
        )
        self.assertEqual(entries, expected)
        self.assertEqual(len(entries), 4)
        for _, target in entries:
            self.assertFalse(PurePosixPath(target).is_absolute())
            self.assertNotIn("\\", target)

    def test_maintained_product_bytes_are_unchanged(self) -> None:
        # Catalog retirement does not freeze later authorized product evolution.
        for relative, expected in self.authenticated_current_product_identities().items():
            with self.subTest(path=relative):
                self.assertEqual(identity.fingerprint(REPO_ROOT / relative), expected)

    def test_catalog_generation_preserves_historical_and_current_product_bytes(self) -> None:
        current = self.authenticated_current_product_identities()
        metadata_path = "config/publication-metadata.toml"
        context = release_context.parse_formal_release_context(
            "2099-01-02", "2099-01-02", "v2099-01-02",
            "0123456789abcdef0123456789abcdef01234567",
        )
        for historical in (True, False):
            with self.subTest(historical=historical), tempfile.TemporaryDirectory(
                prefix="catalog-product-identity-"
            ) as temporary:
                root = Path(temporary)
                for relative in (*HISTORICAL_PRODUCT_HASHES, metadata_path):
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(
                        checkpoint_bytes(relative) if historical
                        else (REPO_ROOT / relative).read_bytes()
                    )
                before = {
                    path: (root / path).read_bytes() for path in HISTORICAL_PRODUCT_HASHES
                }
                expected = HISTORICAL_PRODUCT_HASHES if historical else {
                    path: item["sha256"] for path, item in current.items()
                }
                self.assertEqual(
                    {path: hashlib.sha256(data).hexdigest() for path, data in before.items()},
                    expected,
                )
                # The migration was a completed repository change, not a CLI.
                # Exercise its surviving production catalog renderer without
                # rewriting either state's development products as formal ones.
                metadata = publication_metadata.load_metadata(root / metadata_path)
                catalog = build_release.canonical_catalog_bytes(metadata, context)
                self.assertEqual(build_release.validate_catalog_bytes(catalog, metadata, context), ())
                (root / "catalog-v001.xml").write_bytes(catalog)
                self.assertEqual(
                    {path: (root / path).read_bytes() for path in before}, before
                )

    def test_package_and_archive_layout_authorities_remain_12_and_16_members(self) -> None:
        self.assertEqual(len(build_release.PACKAGE_FILE_PATHS), 12)
        self.assertEqual(len(release_archive.ARCHIVE_MEMBER_TEMPLATES), 16)
        self.assertEqual(
            release_archive.canonical_member_names("2099-01-02"),
            tuple(
                template.format(release_id="2099-01-02")
                for template in release_archive.ARCHIVE_MEMBER_TEMPLATES
            ),
        )


POLICY_DOCUMENTS = {
    "docs/VALIDATION-AND-RELEASES.md": "## Dependency and catalog policy",
    "reports/coms-automatic-validation-setup.md": "## Placeholder And Catalog Migration",
    "src/current-ssn-sosa/docs/README.md": "# Current SSN/SOSA source notes",
}
SOURCE_NOTES = "src/current-ssn-sosa/docs/README.md"
SCOPE = "config/sosa-release-scope.toml"
CATALOG = "src/sosa-next/catalog-v001.xml"


class WorkflowPublicationPolicyTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory(prefix="workflow-publication-policy-") as directory:
            root = Path(directory)
            # The copied scope is checked against the canonical source-version
            # and role-policy loaders' real-repository defaults intentionally.
            for relative in (*POLICY_DOCUMENTS, SCOPE, CATALOG):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO_ROOT / relative, destination)
            yield root

    def replace(self, root, relative, old, new):
        path = root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, relative)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def add_policy_paragraph(self, root, relative, paragraph):
        heading = POLICY_DOCUMENTS[relative]
        self.replace(root, relative, heading, heading + "\n\n" + paragraph)

    def replace_catalog_assertion(self, root, relative, replacement):
        path = root / relative
        text, replacements = re.subn(
            r"(?:does\s+not\s+require\s+a|requires\s+no)\s+development\s+XML\s+catalog",
            replacement,
            path.read_text(encoding="utf-8"),
            count=1,
        )
        self.assertEqual(replacements, 1, relative)
        path.write_text(text, encoding="utf-8")

    def assert_policy_rejected(self, root, relative):
        issues = workflow.publication_policy_issues(root)
        self.assertTrue(issues)
        self.assertTrue(any(relative in issue for issue in issues), issues)

    def test_current_documents_and_full_integration_are_accepted(self):
        self.assertEqual(workflow.publication_policy_issues(REPO_ROOT), [])
        self.assertIsNone(workflow.check_release_tooling_integration())
        with self.fixture() as root:
            self.assertEqual(workflow.publication_policy_issues(root), [])

    def test_case_line_wrapping_and_inline_markup_do_not_change_policy(self):
        with self.fixture() as root:
            for relative in POLICY_DOCUMENTS:
                path = root / relative
                text = path.read_text(encoding="utf-8")
                text = re.sub(r"development\s+XML\s+catalog", "**development**\nXML `catalog`", text)
                text = text.replace("package-relative", "**package-relative**")
                path.write_text(text.swapcase(), encoding="utf-8")
            self.assertEqual(workflow.publication_policy_issues(root), [])

    def test_missing_or_duplicate_current_policy_heading_is_rejected(self):
        for relative, heading in POLICY_DOCUMENTS.items():
            for duplicate in (False, True):
                with self.subTest(document=relative, duplicate=duplicate), self.fixture() as root:
                    if duplicate:
                        path = root / relative
                        path.write_text(path.read_text() + "\n" + heading + "\n", encoding="utf-8")
                    else:
                        self.replace(root, relative, heading, "## Unrelated documentation")
                    self.assert_policy_rejected(root, relative)

    def test_current_track_requiring_development_catalog_is_rejected(self):
        for relative in POLICY_DOCUMENTS:
            with self.subTest(document=relative), self.fixture() as root:
                self.replace_catalog_assertion(root, relative, "requires a development XML catalog")
                self.assert_policy_rejected(root, relative)

    def test_positive_catalog_requirement_cannot_hide_behind_negative_statement(self):
        for relative in POLICY_DOCUMENTS:
            for ending in (".", ", unlike sosa-next."):
                with self.subTest(document=relative, ending=ending), self.fixture() as root:
                    self.add_policy_paragraph(
                        root, relative,
                        "The current SSN/SOSA track requires a development XML catalog" + ending,
                    )
                    self.assert_policy_rejected(root, relative)

    def test_other_track_catalog_statement_cannot_supply_current_policy(self):
        for relative in POLICY_DOCUMENTS:
            with self.subTest(document=relative), self.fixture() as root:
                self.replace_catalog_assertion(root, relative, "uses explicit local dependencies")
                self.add_policy_paragraph(
                    root, relative,
                    "The sosa-next track requires no development XML catalog.",
                )
                self.assert_policy_rejected(root, relative)

    def test_inactive_track_claim_cannot_coexist_with_maintained_track_policy(self):
        with self.fixture() as root:
            self.add_policy_paragraph(
                root, SOURCE_NOTES,
                "The sosa-next scaffold remains intentionally inactive.",
            )
            self.assert_policy_rejected(root, SOURCE_NOTES)

    def test_negated_track_maintenance_is_rejected(self):
        for replacement in ("is not maintained with", "is no longer maintained with"):
            with self.subTest(statement=replacement), self.fixture() as root:
                self.replace(root, SOURCE_NOTES, "is maintained with", replacement)
                self.assert_policy_rejected(root, SOURCE_NOTES)

    def test_unrelated_separate_work_cannot_supply_track_separation(self):
        with self.fixture() as root:
            self.replace(
                root, SOURCE_NOTES,
                "The separate `sosa-next` track is maintained",
                "The shared `sosa-next` track is maintained",
            )
            # The paragraph still says actual publication is "separate work".
            # That cannot establish a separately maintained source track.
            self.assert_policy_rejected(root, SOURCE_NOTES)

    def test_missing_sosa_2023_identity_context_is_rejected(self):
        with self.fixture() as root:
            self.replace(root, SOURCE_NOTES, "pinned SOSA-2023 source identity", "pinned source identity")
            self.assert_policy_rejected(root, SOURCE_NOTES)

    def test_formal_catalog_requires_package_relative_qualification(self):
        for relative in POLICY_DOCUMENTS:
            with self.subTest(document=relative), self.fixture() as root:
                self.replace(root, relative, "package-relative", "absolute-path")
                self.assert_policy_rejected(root, relative)

    def test_contradictory_formal_catalog_qualification_is_rejected(self):
        for negation in ("not", "no longer"):
            with self.subTest(negation=negation), self.fixture() as root:
                self.add_policy_paragraph(
                    root, SOURCE_NOTES,
                    "The formal package catalog is " + negation + " package-relative.",
                )
                self.assert_policy_rejected(root, SOURCE_NOTES)

    def test_structured_scope_rejects_combined_package_or_wrong_track(self):
        cases = (
            ('publication_model = "separate_package"', 'publication_model = "combined_package"'),
            ('development_alias = "sosa-next"', 'development_alias = "current-ssn-sosa"'),
            ('status = "approved"', 'status = "draft"'),
        )
        for old, new in cases:
            with self.subTest(change=new), self.fixture() as root:
                self.replace(root, SCOPE, old, new)
                self.assert_policy_rejected(root, SCOPE)

    def test_missing_or_symlinked_governed_track_catalog_is_rejected(self):
        for symlinked in (False, True):
            with self.subTest(symlinked=symlinked), self.fixture() as root:
                path = root / CATALOG
                path.unlink()
                if symlinked:
                    path.symlink_to(REPO_ROOT / CATALOG)
                self.assert_policy_rejected(root, CATALOG)

    def test_historical_statement_outside_current_policy_section_is_not_reinterpreted(self):
        with self.fixture() as root:
            path = root / "docs/VALIDATION-AND-RELEASES.md"
            path.write_text(
                path.read_text() + "\n## Historical lifecycle evidence\n\n"
                "The sosa-next scaffold remains intentionally inactive.\n",
                encoding="utf-8",
            )
            self.assertEqual(workflow.publication_policy_issues(root), [])


if __name__ == "__main__":
    unittest.main()
