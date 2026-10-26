#!/usr/bin/env python3
"""Disposable driver-level retry/archive regressions; no actual reasoner runs."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from rdflib import Graph, OWL, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_semantic_invocation as custody
import current_semantic_validation as validation


class RetryArchiveTests(unittest.TestCase):
    """The real driver and custody wrapper run with synthetic Java output."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        original_fingerprint = validation.fingerprint
        for replacement in (
            patch.object(validation, "ROOT", self.root),
            patch.object(validation, "git_value", return_value="synthetic-head"),
            patch.object(validation, "command_input_snapshot", return_value=[]),
            patch.object(validation, "fingerprint", side_effect=lambda path, root=None:
                         original_fingerprint(path, root or self.root)),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)

    def graph(self, marker="first"):
        graph = Graph()
        graph.add((URIRef("urn:retry:" + marker), RDF.type, OWL.Class))
        return graph

    def attempt(self, destination, *, marker="first", queries=None, failed=False):
        directory = self.root / destination
        evidence, build = directory / "evidence", directory / "build"
        graph = self.graph(marker)
        closure = {"inputs": [], "unresolved_imports": []}
        expected = {"slot": "diagnostic/shared-slot", "closure": closure,
                    "identity": {"id": "shared-slot", "graph_identity": validation.graph_identity(graph),
                                 "governed_inputs": [], "command_identity": {"mode": "consistency"}}}
        payload = {"status": "consistent", "consistent": True,
                   "owl2_dl_profile": True, "profile_violations": []}
        process = subprocess.CompletedProcess([], 0, custody.canonical_bytes(payload), b"")
        behavior = {"side_effect": OSError("synthetic launch failure")} if failed else {"return_value": process}
        with patch.object(custody.subprocess, "run", **behavior):
            raw = validation.run_graph(graph, closure, "shared-slot", evidence, build,
                {"status": "ready"}, queries=queries, expected_execution=expected)
        return {"directory": directory, "evidence": evidence, "build": build,
                "raw": raw, "expected": expected}

    def snapshot(self, directory):
        snapshot = {}
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                snapshot[path.relative_to(directory).as_posix()] = ("symlink", str(path.readlink()))
            elif path.is_file():
                stat = path.stat()
                snapshot[path.relative_to(directory).as_posix()] = (path.read_bytes(), stat.st_mtime_ns, stat.st_mode)
        return snapshot

    def verify(self, attempt):
        raw = attempt["raw"]
        ticket = self.root / raw["attempt"]["invocation"]["ticket"]["path"]
        return custody.verify_result(ticket, root=self.root, expected_slot=attempt["expected"]["slot"],
                                     expected_invocation_id=raw["selected_invocation_id"])

    def selection(self, attempt):
        raw, expected = attempt["raw"], attempt["expected"]
        directory = attempt["evidence"].relative_to(self.root)
        selected = {expected["slot"]: raw["selected_invocation_id"]}
        selection_path = attempt["evidence"] / "selected-invocations.json"
        custody.create_once(selection_path, custody.canonical_bytes(custody.sealed({
            "schema": custody.SCHEMA, "selected_invocations": selected}, "selection_sha256")))
        report = {"selected_invocations": selected,
                  "selection_record": validation.fingerprint(selection_path, self.root)}
        evidence = {path.relative_to(self.root).as_posix(): validation.fingerprint(path, self.root)
                    for path in attempt["evidence"].rglob("*") if path.is_file()}
        errors = validation.verify_selection_record(report, directory, evidence, self.root,
                                                     {expected["slot"]: expected})
        self.assertEqual(errors, [])
        validation.verify_invocation_chain(raw["attempt"], raw, expected, report, directory, evidence, self.root)
        return selection_path

    def test_a_same_destination_retry_fails_before_touching_first_archive(self):
        first = self.attempt("first", queries=[{"id": "query-a"}])
        before = self.snapshot(first["directory"])
        with patch.object(custody.subprocess, "run", side_effect=AssertionError("retry launched")):
            with self.assertRaisesRegex(FileExistsError, "new build/evidence"):
                validation.run_graph(self.graph("different"), {"inputs": []}, "shared-slot",
                    first["evidence"], first["build"], {"status": "ready"}, queries=[{"id": "query-b"}])
        self.assertEqual(before, self.snapshot(first["directory"]))
        self.verify(first)

    def test_b_explicit_retry_with_different_graph_preserves_both_archives(self):
        first = self.attempt("first")
        before = self.snapshot(first["directory"])
        second = self.attempt("second", marker="different")
        second_before = self.snapshot(second["directory"])
        self.assertEqual(before, self.snapshot(first["directory"]))
        self.assertNotEqual(first["raw"]["input_document"]["sha256"], second["raw"]["input_document"]["sha256"])
        self.verify(first)
        self.verify(second)
        self.assertEqual(second_before, self.snapshot(second["directory"]))

    def test_c_same_inputs_receive_distinct_identity_nonce_and_archive(self):
        first = self.attempt("first", queries=[{"id": "query-a"}])
        before = self.snapshot(first["directory"])
        second = self.attempt("second", queries=[{"id": "query-a"}])
        self.assertEqual(before, self.snapshot(first["directory"]))
        for key in ("input_document", "query_document"):
            self.assertEqual(first["raw"][key]["sha256"], second["raw"][key]["sha256"])
            self.assertNotEqual(first["raw"][key]["path"], second["raw"][key]["path"])
        for key in ("selected_invocation_id", "invocation_nonce"):
            self.assertNotEqual(first["raw"][key], second["raw"][key])
        self.verify(first)
        self.verify(second)

    def test_d_failed_second_execution_preserves_first(self):
        first = self.attempt("first")
        before = self.snapshot(first["directory"])
        second = self.attempt("second", failed=True)
        self.assertEqual(second["raw"]["status"], "technical_failure")
        self.assertEqual(before, self.snapshot(first["directory"]))
        self.verify(first)
        self.verify(second)

    def test_e_selection_can_name_first_successful_attempt(self):
        first = self.attempt("first")
        second = self.attempt("second")
        second_before = self.snapshot(second["directory"])
        selection = self.selection(first)
        self.assertEqual(second_before, self.snapshot(second["directory"]))
        self.verify(second)
        with self.assertRaises(FileExistsError):
            custody.create_once(selection, b"replace selection")

    def test_f_selection_can_name_second_successful_attempt(self):
        first = self.attempt("first")
        before = self.snapshot(first["directory"])
        second = self.attempt("second")
        self.selection(second)
        self.assertEqual(before, self.snapshot(first["directory"]))
        self.verify(first)

    def test_g_selected_failed_attempt_is_honest_custody_but_not_semantic_success(self):
        self.attempt("first")
        failed = self.attempt("second", failed=True)
        self.selection(failed)
        raw = failed["raw"]
        self.assertEqual(validation.execution_status(raw["attempt"], raw["reasoner_result"], raw["closure"]),
                         "technical_failure")
        self.assertEqual(validation.approximate_difference(raw, raw)["status"], "BLOCKED")

    def test_h_mutating_or_deleting_first_input_invalidates_only_first(self):
        for action in ("mutate", "delete"):
            with self.subTest(action=action):
                first = self.attempt("first-" + action)
                second = self.attempt("second-" + action)
                second_before = self.snapshot(second["directory"])
                graph = self.root / first["raw"]["input_document"]["path"]
                graph.write_bytes(graph.read_bytes() + b"altered") if action == "mutate" else graph.unlink()
                with self.assertRaisesRegex(ValueError, "graph bytes differ"):
                    self.verify(first)
                self.verify(second)
                self.assertEqual(second_before, self.snapshot(second["directory"]))

    def test_i_graph_query_capture_envelope_cannot_be_overwritten(self):
        first = self.attempt("first", queries=[{"id": "query-a"}])
        second = self.attempt("second", queries=[{"id": "query-a"}])
        for attempt in (first, second):
            raw = attempt["raw"]
            paths = [self.root / raw[key]["path"] for key in ("input_document", "query_document")]
            paths += [self.root / raw["attempt"]["invocation"][key]["path"] for key in ("capture", "envelope")]
            before = self.snapshot(attempt["directory"])
            for path in paths:
                with self.subTest(path=path.name):
                    with self.assertRaises(FileExistsError):
                        custody.create_once(path, b"overwrite")
            self.assertEqual(before, self.snapshot(attempt["directory"]))
            self.verify(attempt)

    def test_preexisting_output_or_dangling_symlink_fails_before_any_write(self):
        targets = [("build", "shared-slot.rdf"), ("build", "shared-slot.queries.json")]
        targets += [("evidence", "shared-slot." + suffix) for suffix in (
            "attempt.json", "result.json", "command.json", "stdout.log", "stderr.log",
            "ticket.json", "capture.json", "envelope.json")]
        for directory_name, name in targets:
            for broken_symlink in (False, True):
                with self.subTest(destination=name, broken_symlink=broken_symlink):
                    directory = self.root / (name + "-" + str(broken_symlink))
                    path = directory / directory_name / name
                    path.parent.mkdir(parents=True)
                    path.symlink_to(directory / "missing-target") if broken_symlink else path.write_bytes(b"retained")
                    before = self.snapshot(directory)
                    with patch.object(Graph, "serialize", side_effect=AssertionError("serialized before preflight")):
                        with self.assertRaises(FileExistsError):
                            validation.run_graph(self.graph(), {}, "shared-slot", directory / "evidence",
                                directory / "build", {"status": "ready"})
                    self.assertEqual(before, self.snapshot(directory))

    def test_reusing_either_build_or_evidence_destination_is_rejected(self):
        first = self.attempt("first")
        before = self.snapshot(first["directory"])
        for evidence, build in ((first["evidence"], self.root / "new-build"),
                                (self.root / "new-evidence", first["build"])):
            with self.subTest(evidence=str(evidence), build=str(build)):
                with self.assertRaises(FileExistsError):
                    validation.run_graph(self.graph(), {}, "shared-slot", evidence, build, {"status": "ready"})
        self.assertEqual(before, self.snapshot(first["directory"]))
        self.assertFalse((self.root / "new-build").exists())
        self.assertFalse((self.root / "new-evidence").exists())

    def test_toolchain_failure_result_is_create_once(self):
        evidence, build = self.root / "evidence", self.root / "build"
        result = validation.run_graph(self.graph(), {}, "shared-slot", evidence, build,
                                      {"status": "technical_failure"})
        self.assertEqual(result["status"], "technical_failure")
        before = self.snapshot(self.root)
        with self.assertRaises(FileExistsError):
            validation.run_graph(self.graph("second"), {}, "shared-slot", evidence, build,
                                 {"status": "technical_failure"})
        self.assertEqual(before, self.snapshot(self.root))


if __name__ == "__main__":
    unittest.main()
