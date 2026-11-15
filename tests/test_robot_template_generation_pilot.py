#!/usr/bin/env python3
"""Focused tests for normalized ROBOT Template generation from governed COMS rows."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from openpyxl import load_workbook

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import robot_template_generation_pilot as pilot  # noqa: E402
import robot_reconstruction_validation as reconstruction  # noqa: E402
import current_semantic_workbook as semantic  # noqa: E402
import current_semantic_generation as generation  # noqa: E402
from coms_row_identity import ExpressionNode  # noqa: E402


WORKBOOK = REPO_ROOT / "mappings/SSN2BFO-COMS.xlsx"

MAINTAINED_PRODUCTS = (
    REPO_ROOT / "SSN2BFO.ttl",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RobotTemplateGenerationPilotTests(unittest.TestCase):
    def test_normalized_expression_uses_generated_labels(self) -> None:
        class_a = "http://example.org/ClassA"
        class_b = "http://example.org/ClassB"
        property_a = "http://example.org/propertyA"

        expression = ExpressionNode(
            kind="intersection",
            children=(
                ExpressionNode(kind="named", iri=class_a),
                ExpressionNode(
                    kind="some",
                    property_iri=property_a,
                    filler=ExpressionNode(kind="named", iri=class_b),
                ),
            ),
        )

        labels = {
            ("class", class_a): pilot.deterministic_label("class", class_a),
            ("class", class_b): pilot.deterministic_label("class", class_b),
            ("property", property_a): pilot.deterministic_label(
                "property",
                property_a,
            ),
        }

        rendered = pilot.render_manchester_expression(expression, labels)

        self.assertNotIn(class_a, rendered)
        self.assertNotIn(class_b, rendered)
        self.assertNotIn(property_a, rendered)
        self.assertIn(labels[("class", class_a)], rendered)
        self.assertIn(labels[("class", class_b)], rendered)
        self.assertIn(labels[("property", property_a)], rendered)
        self.assertIn(" and ", rendered)
        self.assertIn(" some ", rendered)

    def test_governed_workbook_reconstructs_all_non_chain_axioms(self) -> None:
        before = {
            path.relative_to(REPO_ROOT).as_posix(): sha256(path)
            for path in MAINTAINED_PRODUCTS
        }

        with tempfile.TemporaryDirectory(
            prefix="robot-template-pilot-a-"
        ) as first_dir, tempfile.TemporaryDirectory(
            prefix="robot-template-pilot-b-"
        ) as second_dir:
            first_root = Path(first_dir)
            second_root = Path(second_dir)

            first = pilot.run_pilot(WORKBOOK, first_root)
            second = pilot.run_pilot(WORKBOOK, second_root)

            self.assertTrue(first["passed"], first)
            self.assertTrue(second["passed"], second)

            for summary in (first, second):
                self.assertEqual(summary["governed_row_count"], 108)
                self.assertEqual(summary["authenticated_active_mapping_count"], 102)
                self.assertEqual(summary["excluded_blank_rows"], 6)
                self.assertEqual(summary["attempted_non_chain_rows"], 100)
                self.assertEqual(summary["excluded_property_chain_rows"], 2)
                self.assertEqual(summary["expected_axiom_count"], 100)
                self.assertEqual(summary["actual_axiom_count"], 100)
                self.assertEqual(summary["robot_return_code"], 0)
                self.assertEqual(summary["missing_axiom_ids"], [])
                self.assertEqual(summary["extra_axiom_ids"], [])
                self.assertEqual(summary["mismatched_axiom_ids"], [])

            first_artifacts = pilot.artifact_paths(first_root)
            second_artifacts = pilot.artifact_paths(second_root)

            self.assertEqual(
                first_artifacts.resolver_path.read_bytes(),
                second_artifacts.resolver_path.read_bytes(),
            )
            self.assertEqual(
                first_artifacts.template_path.read_bytes(),
                second_artifacts.template_path.read_bytes(),
            )

        after = {
            path.relative_to(REPO_ROOT).as_posix(): sha256(path)
            for path in MAINTAINED_PRODUCTS
        }
        self.assertEqual(before, after)

    def test_historical_baseline_keeps_100_non_chain_axioms(self) -> None:
        history = semantic.resolve_history(REPO_ROOT)
        archived = semantic.snapshot(REPO_ROOT, history["version_sha256"][0])
        # Explicit history also overrides an enclosing current context and must
        # restore it afterwards. The ordinary current path rejects rollback.
        with generation.generated_expectations_context(REPO_ROOT, WORKBOOK):
            historical = reconstruction.load_governed_coms_rows(archived, historical=True)
            self.assertEqual(generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103), 102)
        self.assertEqual((historical.row_count, historical.active_count, historical.blank_count,
                          historical.property_chain_count, historical.non_chain_count),
                         (105, 103, 2, 3, 100))
        self.assertEqual(generation.expected_count("AUTHORITATIVE_AXIOM_COUNT", 103), 103)
        with self.assertRaisesRegex(ValueError, "current workbook"):
            reconstruction.load_governed_coms_rows(archived)
        with tempfile.TemporaryDirectory(prefix="robot-historical-template-") as directory:
            summary = pilot.run_pilot(archived, Path(directory), historical=True)
        self.assertTrue(summary["passed"], summary)
        self.assertEqual(summary["attempted_non_chain_rows"], 100)
        self.assertEqual(summary["excluded_property_chain_rows"], 3)
        self.assertEqual(summary["excluded_blank_rows"], 2)
        self.assertEqual(summary["actual_axiom_count"], 100)

    def test_current_partition_preserves_exact_two_chain_identities(self) -> None:
        governed = reconstruction.load_governed_coms_rows(WORKBOOK)
        self.assertEqual((governed.row_count, governed.active_count, governed.blank_count,
                          governed.property_chain_count, governed.non_chain_count),
                         (108, 102, 6, 2, 100))
        chains = {row.subject_iri: (row.row_id, row.property_chain)
                  for row in governed.canonical_rows if row.mapping_type == "property_chain"}
        bfo = "http://purl.obolibrary.org/obo/BFO_"
        self.assertEqual(chains, {
            "http://www.w3.org/ns/sosa/hosts": (
                "urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e",
                tuple(bfo + value for value in ("0000196", "0000054", "0000057"))),
            "http://www.w3.org/ns/sosa/isHostedBy": (
                "urn:uuid:e866de80-683d-4138-a713-be9646d37148",
                tuple(bfo + value for value in ("0000056", "0000055", "0000197"))),
        })
        chain_axioms = reconstruction.canonical_expected_axioms(governed.processed_rows, {"property_chain"})
        self.assertEqual(set(chain_axioms), {
            "sha256:90d2b3a965084a150dcd254003bbdd2e5d706d8dd1b7a941c44e44ee2ea1737e",
            "sha256:47859e2cfd5df437d1f55c83560793ab22f035de9b829ccdedcc4d3118cc4f3e",
        })
        non_chain = reconstruction.canonical_expected_axioms(governed.processed_rows, pilot.SUPPORTED_MAPPING_TYPES)
        all_axioms = reconstruction.canonical_expected_axioms(governed.processed_rows, reconstruction.ACTIVE_MAPPING_TYPES)
        blanks = reconstruction.canonical_expected_axioms(governed.processed_rows, {"explicit_blank"})
        self.assertEqual(blanks, {})
        self.assertFalse(set(non_chain) & set(chain_axioms))
        self.assertEqual(non_chain | chain_axioms, all_axioms)
        self.assertEqual(len(all_axioms), 102)

    def test_unauthorized_missing_active_mapping_fails_before_robot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="robot-unauthorized-drift-") as directory:
            root = Path(directory)
            workbook = load_workbook(WORKBOOK)
            # Remove an ordinary active row, without creating a transition.
            removed = False
            for sheet in workbook.worksheets:
                for cells in sheet.iter_rows(min_row=2):
                    if cells[1].value == "rdfs:subClassOf" and cells[2].value:
                        cells[1].value = cells[2].value = None
                        removed = True
                        break
                if removed:
                    break
            self.assertTrue(removed)
            changed = root / "unauthorized.xlsx"
            workbook.save(changed)
            workbook.close()
            with patch.object(reconstruction, "resolve_robot_path") as resolve_robot:
                with self.assertRaisesRegex(ValueError, "current workbook"):
                    pilot.run_pilot(changed, root / "pilot")
                resolve_robot.assert_not_called()

    def test_wrong_backend_row_selection_fails_before_robot(self) -> None:
        governed = reconstruction.load_governed_coms_rows(WORKBOOK)
        normal = tuple(row for row in governed.canonical_rows if row.mapping_type in pilot.SUPPORTED_MAPPING_TYPES)
        blank = next(row for row in governed.canonical_rows if row.mapping_type == "explicit_blank")
        chain = next(row for row in governed.canonical_rows if row.mapping_type == "property_chain")
        for label, selected in (("missing", normal[:-1]), ("blank", (*normal, blank)),
                                ("chain", (*normal, chain)), ("duplicate", (*normal, normal[0]))):
            with self.subTest(case=label), tempfile.TemporaryDirectory(prefix="robot-wrong-selection-") as directory:
                with patch.object(reconstruction, "load_governed_coms_rows", return_value=governed), \
                     patch.object(pilot, "write_template", return_value=selected), \
                     patch.object(reconstruction, "resolve_robot_path") as resolve_robot:
                    with self.assertRaisesRegex(ValueError, "backend partition"):
                        pilot.run_pilot(WORKBOOK, Path(directory))
                    resolve_robot.assert_not_called()

    def test_reconstruction_rejects_missing_extra_and_changed_expressions(self) -> None:
        governed = reconstruction.load_governed_coms_rows(WORKBOOK)
        expected = reconstruction.canonical_expected_axioms(governed.processed_rows, pilot.SUPPORTED_MAPPING_TYPES)
        first = next(iter(expected))
        cases = {
            "missing": {key: value for key, value in expected.items() if key != first},
            "extra": {**expected, "sha256:unexpected": "UnexpectedMapping"},
            "mismatched": {**expected, first: "ChangedExpression"},
        }
        for category, actual in cases.items():
            with self.subTest(category=category), tempfile.TemporaryDirectory(prefix="robot-reconstruction-drift-") as directory:
                root = Path(directory)
                def robot_run(*args, **kwargs):
                    pilot.artifact_paths(root).output_path.write_text("")
                    return SimpleNamespace(returncode=0, stdout="", stderr="")
                with patch.object(reconstruction, "load_governed_coms_rows", return_value=governed), \
                     patch.object(reconstruction, "resolve_robot_path", return_value="robot"), \
                     patch.object(pilot.subprocess, "run", side_effect=robot_run), \
                     patch.object(reconstruction, "canonical_axioms_from_turtle", return_value=actual):
                    summary = pilot.run_pilot(WORKBOOK, root)
                self.assertFalse(summary["passed"], summary)
                self.assertEqual(summary["expected_axiom_count"], 100)
                self.assertEqual(len(summary[category + "_axiom_ids"]), 1)


if __name__ == "__main__":
    unittest.main()
