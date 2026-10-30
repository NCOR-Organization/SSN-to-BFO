#!/usr/bin/env python3
"""Focused tests for governed RDFLib versus ROBOT query equivalence."""
from __future__ import annotations

import csv
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rdflib import Graph, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, RDFS, SKOS

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import robot_query_equivalence_pilot as pilot  # noqa: E402
import current_semantic_generation as generation  # noqa: E402
import current_semantic_workbook as semantic  # noqa: E402
import generate_mapping_from_coms as coms  # noqa: E402
import robot_reconstruction_validation as reconstruction  # noqa: E402


WORKBOOK = REPO_ROOT / "mappings/SSN2BFO-COMS.xlsx"

MAINTAINED_PRODUCTS = (
    REPO_ROOT / "SSN2BFO.ttl",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl",
    REPO_ROOT / "releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl",
)
GOVERNED_SOURCE_PATHS = tuple(REPO_ROOT / path for path in coms.SOURCE_IMPORTS)
EXPECTED_IMPORTS = {
    (URIRef("http://www.w3.org/ns/sosa/sampling/"), OWL.imports,
     URIRef("http://www.w3.org/2004/02/skos/core")),
    (URIRef("http://www.w3.org/ns/sosa/sampling/"), OWL.imports,
     URIRef("http://www.w3.org/ns/sosa/")),
    (URIRef("http://www.w3.org/ns/ssn/"), OWL.imports,
     URIRef("http://www.w3.org/ns/sosa/")),
    (URIRef("http://www.w3.org/ns/ssn/systems/"), OWL.imports,
     URIRef("http://www.w3.org/ns/ssn/")),
}
COMPARISON_SCOPE = (
    "The query-equivalence workflow validates tool equivalence over the governed "
    "asserted current-source graph. It does not claim that the unresolved "
    "transitive import closure is locally complete."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_bytes(
    rows: tuple[tuple[str, ...], ...],
    columns: tuple[str, ...] = pilot.UNMAPPED_COLUMNS,
) -> bytes:
    if not rows:
        return b""
    text = io.StringIO(newline="")
    writer = csv.writer(text, lineterminator="\r\n")
    writer.writerow(columns)
    writer.writerows(rows)
    return text.getvalue().encode("utf-8")


class RobotQueryEquivalencePilotTests(unittest.TestCase):
    def test_execution_graph_removes_only_imports_and_preserves_local_skos_assertions(self) -> None:
        before = {path: sha256(path) for path in GOVERNED_SOURCE_PATHS}
        canonical = coms.build_source_graph()
        original = set(canonical)
        execution = pilot.asserted_query_graph(canonical)

        self.assertEqual(len(canonical), 1157)
        self.assertEqual(set(canonical.triples((None, OWL.imports, None))), EXPECTED_IMPORTS)
        self.assertEqual(set(execution), original - EXPECTED_IMPORTS)
        self.assertEqual(len(execution), 1153)
        self.assertFalse(list(execution.triples((None, OWL.imports, None))))
        self.assertEqual(set(canonical), original)
        self.assertIn(
            (URIRef("http://www.w3.org/ns/sosa/sampling/RelationshipNature"),
             RDFS.subClassOf, SKOS.Concept),
            execution,
        )
        for predicate in (SKOS.definition, SKOS.example, SKOS.note):
            annotations = set(canonical.triples((None, predicate, None)))
            self.assertTrue(annotations, predicate)
            self.assertEqual(set(execution.triples((None, predicate, None))), annotations)
        self.assertEqual(before, {path: sha256(path) for path in GOVERNED_SOURCE_PATHS})

    def test_queries_need_only_local_type_deprecation_and_coverage_triples(self) -> None:
        canonical = coms.build_source_graph()
        execution = pilot.asserted_query_graph(canonical)
        query_projection = Graph()
        for triple in canonical:
            if triple[1] in (RDF.type, OWL.deprecated):
                query_projection.add(triple)
        self.assertFalse(list(query_projection.triples((None, OWL.imports, None))))
        self.assertFalse(any(
            str(predicate).startswith(str(SKOS))
            for _, predicate, _ in query_projection
        ))
        source_rows = coms.run_select_query(canonical, pilot.SOURCE_QUERY)
        self.assertTrue(source_rows)
        self.assertEqual(coms.run_select_query(execution, pilot.SOURCE_QUERY), source_rows)
        self.assertEqual(coms.run_select_query(query_projection, pilot.SOURCE_QUERY), source_rows)

        governed = reconstruction.load_governed_coms_rows(WORKBOOK)
        coverage = pilot.build_coverage_graph(governed.processed_rows, source_rows)
        self.assertEqual(
            set(coverage.predicates()),
            {coms.COMS_COVERAGE.sourceKind, coms.COMS_COVERAGE.coverageStatus},
        )
        self.assertEqual(
            coms.run_select_query(coverage, pilot.UNMAPPED_QUERY),
            coms.run_select_query(pilot.asserted_query_graph(coverage), pilot.UNMAPPED_QUERY),
        )

    def test_robot_query_rejects_imports_before_starting_subprocess(self) -> None:
        with tempfile.TemporaryDirectory(prefix="robot-query-import-guard-") as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "source.ttl"
            input_path.write_bytes(pilot.canonical_graph_bytes(coms.build_source_graph()))
            with mock.patch.object(pilot.subprocess, "run") as subprocess_run:
                with self.assertRaisesRegex(
                    ValueError,
                    "asserted-graph ROBOT query input must not contain owl:imports",
                ):
                    pilot.run_robot_query(
                        "robot-must-not-be-started",
                        input_path,
                        pilot.SOURCE_QUERY,
                        directory / "result.csv",
                    )
                subprocess_run.assert_not_called()

    def test_zero_byte_robot_csv_represents_zero_rows(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="robot-query-empty-"
        ) as temp_dir:
            path = Path(temp_dir) / "empty.csv"
            path.write_bytes(b"")

            header, rows = pilot.read_robot_csv(
                path,
                pilot.UNMAPPED_COLUMNS,
            )

            self.assertEqual(header, ())
            self.assertEqual(rows, ())

    def test_governed_queries_match_rdflib_without_product_changes(self) -> None:
        protected_paths = (*GOVERNED_SOURCE_PATHS, *MAINTAINED_PRODUCTS)
        before = {
            path.relative_to(REPO_ROOT).as_posix(): sha256(path)
            for path in protected_paths
        }
        history = semantic.resolve_history(REPO_ROOT)
        transition = next(record for record in history["chain"] if
                          record.get("transition_id") == "58481ff2-4e56-4931-a3d4-383357b16561")
        canonical = coms.build_source_graph()
        expected_execution = pilot.asserted_query_graph(canonical)
        source_rows = coms.run_select_query(canonical, pilot.SOURCE_QUERY)
        expected_source_rows = pilot.ordered_rows(source_rows, pilot.SOURCE_COLUMNS)
        expected_source_csv = csv_bytes(expected_source_rows, pilot.SOURCE_COLUMNS)

        def coverage_rows(processed):
            graph = pilot.build_coverage_graph(processed, source_rows)
            return pilot.ordered_rows(
                coms.run_select_query(graph, pilot.UNMAPPED_QUERY),
                pilot.UNMAPPED_COLUMNS,
            )

        historical = reconstruction.load_governed_coms_rows(
            semantic.snapshot(REPO_ROOT, transition["old_workbook_sha256"]),
            historical=True,
        )
        historical_rows = coverage_rows(historical.processed_rows)
        self.assertEqual(len(historical_rows), 2)
        self.assertEqual(len(csv_bytes(historical_rows)), 173)
        with generation.generated_expectations_context(REPO_ROOT, WORKBOOK):
            governed = reconstruction.load_governed_coms_rows(WORKBOOK)
            expected_rows = coverage_rows(governed.processed_rows)
        expected_csv = csv_bytes(expected_rows)
        self.assertEqual(len(expected_rows), 5)
        self.assertEqual(len(expected_csv), 399)
        rdflib_inputs = []
        robot_inputs = []
        run_select_query = coms.run_select_query
        run_robot_query = pilot.run_robot_query

        def observe_rdflib(graph, query_path):
            # Authentication can separately query the original import-bearing
            # source graph. Capture execution inputs without relying on its cache.
            if query_path in (pilot.SOURCE_QUERY, pilot.UNMAPPED_QUERY) and not any(
                graph.triples((None, OWL.imports, None))
            ):
                snapshot = Graph()
                for triple in graph:
                    snapshot.add(triple)
                rdflib_inputs.append((query_path, snapshot))
            return run_select_query(graph, query_path)

        def observe_robot(robot, input_path, query_path, output_path):
            robot_inputs.append((query_path, Graph().parse(input_path, format="turtle"), input_path))
            return run_robot_query(robot, input_path, query_path, output_path)

        with tempfile.TemporaryDirectory(
            prefix="robot-query-pilot-a-"
        ) as first_dir, tempfile.TemporaryDirectory(
            prefix="robot-query-pilot-b-"
        ) as second_dir:
            with mock.patch.object(coms, "run_select_query", side_effect=observe_rdflib), \
                    mock.patch.object(pilot, "run_robot_query", side_effect=observe_robot):
                first = pilot.run_pilot(WORKBOOK, Path(first_dir))
                second = pilot.run_pilot(WORKBOOK, Path(second_dir))

            self.assertTrue(first["passed"], first)
            self.assertTrue(second["passed"], second)
            self.assertEqual(len(rdflib_inputs), 4)
            self.assertEqual(len(robot_inputs), 4)
            for (rdflib_query, rdflib_graph), (robot_query, robot_graph, input_path) in zip(
                rdflib_inputs, robot_inputs, strict=True
            ):
                self.assertEqual(rdflib_query, robot_query)
                self.assertTrue(isomorphic(rdflib_graph, robot_graph))
                self.assertFalse(list(robot_graph.triples((None, OWL.imports, None))))
                expected_filename = (
                    pilot.artifact_paths(input_path.parent).source_execution_graph_path.name
                    if robot_query == pilot.SOURCE_QUERY else "coverage-graph.ttl"
                )
                self.assertEqual(input_path.name, expected_filename)

            for summary, output_dir in ((first, Path(first_dir)), (second, Path(second_dir))):
                self.assertEqual(summary["governed_row_count"], 105)
                self.assertEqual(summary["comparison_scope"], COMPARISON_SCOPE)
                self.assertIs(summary["full_transitive_import_closure_locally_complete"], False)
                self.assertEqual(
                    summary["source_input_sha256"],
                    {path.relative_to(REPO_ROOT).as_posix(): before[
                        path.relative_to(REPO_ROOT).as_posix()
                    ] for path in GOVERNED_SOURCE_PATHS},
                )
                artifacts = pilot.artifact_paths(output_dir)
                original_round_trip = Graph().parse(artifacts.source_graph_path, format="turtle")
                execution_round_trip = Graph().parse(
                    artifacts.source_execution_graph_path, format="turtle"
                )
                self.assertTrue(isomorphic(canonical, original_round_trip))
                self.assertTrue(isomorphic(expected_execution, execution_round_trip))
                self.assertEqual(
                    set(original_round_trip.triples((None, OWL.imports, None))),
                    EXPECTED_IMPORTS,
                )
                self.assertEqual(
                    artifacts.source_graph_path.read_bytes(),
                    pilot.canonical_graph_bytes(canonical),
                )
                self.assertEqual(
                    artifacts.source_execution_graph_path.read_bytes(),
                    pilot.canonical_graph_bytes(expected_execution),
                )

                source_graph = summary["source_graph"]
                self.assertEqual(source_graph["triple_count"], 1157)
                self.assertEqual(
                    source_graph["round_trip_triple_count"],
                    1157,
                )
                self.assertTrue(source_graph["round_trip_isomorphic"])
                self.assertEqual(source_graph["owl_imports_count"], 4)

                execution_graph = summary["source_execution_graph"]
                self.assertEqual(execution_graph["triple_count"], 1153)
                self.assertEqual(execution_graph["removed_import_count"], 4)
                self.assertEqual(
                    execution_graph["removed_imports"],
                    sorted([str(subject), str(obj)] for subject, _, obj in EXPECTED_IMPORTS),
                )
                self.assertTrue(execution_graph["only_imports_removed"])
                self.assertTrue(execution_graph["round_trip_isomorphic"])
                self.assertEqual(execution_graph["owl_imports_count"], 0)

                coverage_graph = summary["coverage_graph"]
                self.assertEqual(coverage_graph["triple_count"], 182)
                self.assertEqual(
                    coverage_graph["round_trip_triple_count"],
                    182,
                )
                self.assertTrue(coverage_graph["round_trip_isomorphic"])

                source = summary["source_query"]
                self.assertTrue(source["passed"])
                self.assertEqual(source["robot_return_code"], 0)
                self.assertEqual(source["rdflib_row_count"], len(expected_source_rows))
                self.assertEqual(source["robot_row_count"], len(expected_source_rows))
                self.assertTrue(source["same_ordered_rows"])
                self.assertTrue(source["same_normalized_rows"])
                self.assertEqual(source["rdflib_only_rows"], [])
                self.assertEqual(source["robot_only_rows"], [])
                self.assertEqual(source["robot_header"], ["term", "kind"])
                self.assertGreater(source["robot_output_bytes"], 0)
                self.assertEqual(artifacts.rdflib_source_csv_path.read_bytes(), expected_source_csv)
                self.assertEqual(artifacts.robot_source_csv_path.read_bytes(), expected_source_csv)

                unmapped = summary["unmapped_query"]
                self.assertTrue(unmapped["passed"])
                self.assertEqual(unmapped["robot_return_code"], 0)
                self.assertEqual(unmapped["rdflib_row_count"], len(expected_rows))
                self.assertEqual(unmapped["robot_row_count"], len(expected_rows))
                self.assertTrue(unmapped["same_ordered_rows"])
                self.assertTrue(unmapped["same_normalized_rows"])
                self.assertEqual(unmapped["rdflib_only_rows"], [])
                self.assertEqual(unmapped["robot_only_rows"], [])
                self.assertEqual(
                    unmapped["robot_header"],
                    ["term", "kind", "coverageStatus"],
                )
                self.assertTrue(unmapped["robot_output_exists"])
                self.assertEqual(unmapped["robot_output_bytes"], len(expected_csv))
                self.assertEqual(
                    artifacts.robot_unmapped_csv_path.read_bytes(),
                    expected_csv,
                )
                self.assertEqual(artifacts.rdflib_unmapped_csv_path.read_bytes(), expected_csv)

            for section in (
                "source_query",
                "unmapped_query",
            ):
                self.assertEqual(first[section], second[section])

            for section in (
                "source_graph",
                "source_execution_graph",
                "coverage_graph",
            ):
                self.assertEqual(first[section], second[section])
            first_artifacts = pilot.artifact_paths(Path(first_dir))
            second_artifacts = pilot.artifact_paths(Path(second_dir))
            for field in ("source_graph_path", "source_execution_graph_path", "coverage_graph_path"):
                self.assertEqual(
                    getattr(first_artifacts, field).read_bytes(),
                    getattr(second_artifacts, field).read_bytes(),
                )

        after = {
            path.relative_to(REPO_ROOT).as_posix(): sha256(path)
            for path in protected_paths
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
