"""Portable custody retains original results and fails closed on missing identities."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_portable_execution_evidence as portable
import current_retained_evidence as retained
import current_semantic_invocation as invocation
import current_semantic_validation as semantic
import current_publication_readiness as readiness
from tests import test_current_semantic_validation as existing


def portable_fixture():
    # Keep the synthetic wrapper identity inside its synthetic checkout, like a
    # real execution. The existing builder independently records raw RDF/slots
    # and mocks Java only at its subprocess boundary; no validator is mocked.
    class Fixture(existing.StoredEvidenceAdversarialTests):
        def record(self, *args, **kwargs):
            with patch.object(invocation, "__file__", str(self.root / semantic.INVOCATION_HELPER)):
                return super().record(*args, **kwargs)
    return Fixture("test_honest_blocked_summary_with_matching_raw_evidence_passes")


class PortableExecutionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.bin = self.directory / "original-tool-location"
        self.bin.mkdir()
        for name in ("java", "javac"):
            (self.bin / name).write_bytes(("synthetic pinned executable " + name).encode())
        self.which = patch.object(shutil, "which", side_effect=lambda name: str(self.bin / Path(name).name))
        self.which.start()
        self.addCleanup(self.which.stop)
        self.fixture = portable_fixture()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root, self.report = self.fixture.root, self.fixture.report
        for path in self.fixture.evidence.glob("*.command.json"):
            command = json.loads(path.read_bytes())
            command["execution_binding"] = {"tool": semantic.fingerprint(Path(command["command"][0]), self.root)}
            path.write_text(json.dumps(command))
            if path.name == "javac.command.json":
                self.report["toolchain"]["command"] = command
            else:
                raw_path = path.with_name(path.name.replace(".command.json", ".result.json"))
                raw = json.loads(raw_path.read_bytes())
                raw["attempt"] = command
                raw_path.write_text(json.dumps(raw))
                self._replace_summary(raw)
        self.fixture.refresh_evidence()
        self.report_path = "evidence/summary.json"
        (self.root / self.report_path).write_text(json.dumps(self.report))
        self.original = {p.relative_to(self.root).as_posix(): p.read_bytes()
                         for p in self.fixture.evidence.rglob("*") if p.is_file()}
        self.manifest = portable.retain(self.root, self.report_path, created_at="2026-10-28T20:00:00+00:00")

    def _replace_summary(self, raw):
        summary = semantic.compact_result(raw)
        for side, value in self.report["hierarchy_runs"].items():
            if value["id"] == raw["id"]:
                self.report["hierarchy_runs"][side] = summary
                return
        for row in self.report["examples"] + [self.report["synthetic_fixture"]]:
            for phase in ("source", "aligned"):
                if row[phase]["id"] == raw["id"]:
                    row[phase] = summary
                    return
        raise AssertionError(raw["id"])

    def _context(self, root=None):
        return portable.context(self.report, root or self.root)

    def test_exact_documents_roles_producers_and_inputs_are_bound(self):
        context = self._context()
        self.assertEqual(len(context.documents), 9)
        for ref in context.manifest["documents"]:
            self.assertEqual(ref["role"], "execution_graph")
            self.assertTrue(ref["source_inputs"])
            self.assertEqual(len(ref["dependent_records"]), 7)
            self.assertTrue(ref["producer"]["path"].endswith(".command.json"))
            self.assertEqual(context.resolve({"path": ref["logical_path"], "sha256": ref["sha256"],
                                              "bytes": ref["bytes"]}).read_bytes(),
                             (self.root / ref["logical_path"]).read_bytes())
        first = next(iter(context.documents.values()))
        binding = {"path": first["logical_path"], "sha256": first["sha256"], "bytes": first["bytes"]}
        for field, wrong in (("sha256", "0" * 64), ("bytes", first["bytes"] + 1),
                             ("path", "build/execution-fixture/unrelated-role.rdf")):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "exact portable retention binding"):
                context.resolve({**binding, field: wrong})

    def test_retention_never_rewrites_reports_receipts_or_outcomes(self):
        self.assertEqual(self.report["status"], "FAIL")
        self.assertEqual(self.original, {p: (self.root / p).read_bytes() for p in self.original})
        with self.assertRaisesRegex(ValueError, "already exists"):
            portable.retain(self.root, self.report_path)

    def test_fresh_checkout_without_execution_tree_reconciles_original_fail(self):
        original_report = copy.deepcopy(self.report)
        manifest_bytes = self.manifest.read_bytes()
        source = next(ref for ref in self._context().manifest["documents"]
                      if ref["slot"] == "hierarchy/source")
        self.assertEqual(source["role"], "execution_graph")
        destination = self.directory / "relocated-checkout"
        shutil.copytree(self.root, destination)
        shutil.rmtree(destination / "build/execution-fixture")
        shutil.rmtree(self.root)
        self.assertNotEqual(destination.resolve(), self.root.resolve())
        self.assertFalse(self.root.exists())
        self.assertFalse((destination / "build/execution-fixture").exists())
        context = self._context(destination)
        ticket_path = destination / "evidence/invocations" / (source["invocation_id"] + ".ticket.json")
        ticket = invocation.read_ticket(ticket_path)
        self.assertFalse(Path(ticket["graph"]["path"]).exists())
        graph = context.resolve(ticket["graph"])
        self.assertEqual(graph, destination / source["retained_path"])
        self.assertEqual(portable.digest(graph.read_bytes()), source["sha256"])
        self.assertEqual(graph.stat().st_size, source["bytes"])
        derived, errors = semantic.reconcile_raw_evidence(self.report, destination)
        self.assertEqual(errors, [])
        self.assertEqual(derived["status"], "FAIL")
        self.assertEqual({key: value["status"] for key, value in derived["hierarchy_runs"].items()},
                         {key: value["status"] for key, value in original_report["hierarchy_runs"].items()})
        self.assertEqual([row["classification"] for row in derived["examples"]],
                         [row["classification"] for row in original_report["examples"]])
        self.assertEqual(derived["synthetic_fixture"]["classification"],
                         original_report["synthetic_fixture"]["classification"])
        self.assertEqual(self.report, original_report)
        self.assertEqual(self.original, {p: (destination / p).read_bytes() for p in self.original})
        self.assertEqual((destination / portable.manifest_path(self.report)).read_bytes(), manifest_bytes)
        self.assertFalse((destination / "build/execution-fixture").exists())

    def test_missing_retained_graph_fails_without_live_fallback(self):
        context = self._context()
        first = next(iter(context.documents.values()))
        retained.resolve_execution_object(self.root, first["sha256"], first["bytes"]).unlink()
        self.assertTrue((self.root / first["logical_path"]).exists())
        with self.assertRaisesRegex(ValueError, "missing retained execution object"):
            self._context()
        self.assertTrue(semantic.reconcile_raw_evidence(self.report, self.root)[1])

    def test_corrupt_retained_graph_fails(self):
        context = self._context()
        first = next(iter(context.documents.values()))
        path = retained.resolve_execution_object(self.root, first["sha256"], first["bytes"])
        original = path.read_bytes()
        mutations = {"same_size_wrong_hash": bytes([original[0] ^ 1]) + original[1:],
                     "wrong_size": b"corrupt"}
        for label, data in mutations.items():
            with self.subTest(mutation=label):
                path.write_bytes(data)
                try:
                    with self.assertRaisesRegex(ValueError, "hash or size mismatch"):
                        self._context()
                finally:
                    path.write_bytes(original)

    def test_same_tool_bytes_at_new_absolute_location_pass(self):
        old_bin = self.bin
        self.bin = self.directory / "another-tool-location"
        shutil.copytree(old_bin, self.bin)
        shutil.rmtree(old_bin)
        derived, errors = semantic.reconcile_raw_evidence(self.report, self.root)
        self.assertEqual(errors, [])
        self.assertEqual(derived["status"], "FAIL")

    def test_changed_tool_identity_fails(self):
        for name in ("java", "javac"):
            path = self.bin / name
            original = path.read_bytes()
            with self.subTest(tool=name, mutation="changed"):
                path.write_bytes(b"different executable")
                try:
                    errors = semantic.reconcile_raw_evidence(self.report, self.root)[1]
                    self.assertTrue(any("executable identity" in error for error in errors), errors)
                finally:
                    path.write_bytes(original)
            with self.subTest(tool=name, mutation="missing"):
                with patch.object(shutil, "which", side_effect=lambda value, missing=name:
                                  None if Path(value).name == missing else str(self.bin / Path(value).name)):
                    errors = semantic.reconcile_raw_evidence(self.report, self.root)[1]
                self.assertTrue(any("executable identity" in error for error in errors), errors)
        for relative in (Path("config/validation-toolchain.env"), semantic.ROBOT_JAR, semantic.JAVA_SOURCE):
            path = self.root / relative
            original = path.read_bytes()
            with self.subTest(governed_toolchain=relative.as_posix()):
                path.write_bytes(original + b"\nchanged governed toolchain identity\n")
                try:
                    with self.assertRaisesRegex(ValueError, "source hash or size mismatch"):
                        self._context()
                finally:
                    path.write_bytes(original)

    def test_same_helper_bytes_at_wrong_logical_role_fail(self):
        context = self._context()
        ticket_path = next((self.fixture.evidence / "invocations").glob("*.ticket.json"))
        ticket = invocation.read_ticket(ticket_path)
        alias = self.root / "tools/unrelated_helper.py"
        alias.write_bytes((self.root / semantic.INVOCATION_HELPER).read_bytes())
        ticket["helper"]["path"] = str(alias)
        ticket.pop("ticket_sha256")
        ticket_path.write_bytes(invocation.canonical_bytes(invocation.sealed(ticket, "ticket_sha256")))
        expected = semantic.expected_execution_plan(self.root, only_slot=ticket["slot"])[ticket["slot"]]
        with self.assertRaisesRegex(ValueError, "source hash or size mismatch"):
            context.verify_result(ticket_path, expected=expected)

    def test_manifest_role_or_slot_tampering_fails(self):
        original = self.manifest.read_bytes()
        for field, value in (("role", "unrelated_input"), ("slot", "hierarchy/unrelated"),
                             ("logical_path", "build/execution-fixture/unrelated-role.rdf"),
                             ("retained_path", retained.execution_object_path("0" * 64))):
            manifest = retained._json(original)
            manifest["documents"][0][field] = value
            with self.subTest(field=field):
                self.manifest.write_bytes(retained._canonical(manifest))
                try:
                    with self.assertRaisesRegex(ValueError, "metadata/binding differs"):
                        self._context()
                finally:
                    self.manifest.write_bytes(original)
        manifest = retained._json(original)
        manifest["toolchain"]["version_outputs"] = [{"path": "evidence/other-version.log",
                                                     "sha256": "0" * 64, "bytes": 0}]
        self.manifest.write_bytes(retained._canonical(manifest))
        with self.assertRaisesRegex(ValueError, "metadata/binding differs"):
            self._context()

    def test_manifest_path_escape_fails(self):
        manifest = retained._json(self.manifest.read_bytes())
        manifest["source_report"]["path"] = "../outside.json"
        self.manifest.write_bytes(retained._canonical(manifest))
        with self.assertRaisesRegex(ValueError, "non-project"):
            self._context()

    def test_symlink_object_escape_fails(self):
        context = self._context()
        first = next(iter(context.documents.values()))
        path = retained.resolve_execution_object(self.root, first["sha256"], first["bytes"])
        external = self.directory / Path(first["logical_path"]).name
        external.write_bytes(path.read_bytes())
        with self.assertRaisesRegex(ValueError, "outside the recorded/current checkout"):
            context.resolve({"path": str(external), "sha256": first["sha256"], "bytes": first["bytes"]})
        with self.assertRaisesRegex(ValueError, "outside the recorded/current checkout"):
            portable.logical_path(str(external), context.origin, self.root)
        path.unlink()
        path.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "non-project"):
            self._context()

    def test_changed_raw_receipt_fails_even_with_retained_graph(self):
        path = self.fixture.evidence / "source-hierarchy.command.json"
        command = json.loads(path.read_bytes())
        original = path.read_bytes()
        command["returncode"] = 0
        path.write_text(json.dumps(command))
        with self.assertRaisesRegex(ValueError, "source hash or size mismatch"):
            self._context()
        path.write_bytes(original)
        context = self._context()
        identifier = self.report["selected_invocations"]["hierarchy/source"]
        ticket_path = self.fixture.evidence / "invocations" / (identifier + ".ticket.json")
        original_ticket = ticket_path.read_bytes()
        expected = semantic.expected_execution_plan(self.root, only_slot="hierarchy/source")["hierarchy/source"]
        for field in ("graph", "helper"):
            ticket = invocation.read_ticket(ticket_path)
            ticket[field]["path"] = str(self.directory / ("different-historical-" + field))
            ticket.pop("ticket_sha256")
            with self.subTest(historical_absolute_path=field):
                ticket_path.write_bytes(invocation.canonical_bytes(invocation.sealed(ticket, "ticket_sha256")))
                try:
                    with self.assertRaisesRegex(ValueError, "source hash or size mismatch"):
                        self._context()
                    with self.assertRaisesRegex(ValueError, "source hash or size mismatch"):
                        context.verify_result(ticket_path, expected=expected)
                finally:
                    ticket_path.write_bytes(original_ticket)

    def test_portable_custody_does_not_waive_head_freshness(self):
        with patch.object(semantic, "git_value", return_value="different-head"):
            errors = semantic.validate_stored(self.report, self.root)
        self.assertIn("Stored semantic evidence HEAD differs from current HEAD", errors)
        path = self.root / semantic.SOURCE_PATHS[0]
        original = path.read_bytes()
        path.write_bytes(original + b"\n<urn:changed:dependency> a <http://www.w3.org/2002/07/owl#Class> .\n")
        try:
            with self.assertRaisesRegex(ValueError, "source hash or size mismatch"):
                self._context()
            errors = semantic.reconcile_raw_evidence(self.report, self.root)[1]
            self.assertTrue(any("source hash or size mismatch" in error for error in errors), errors)
        finally:
            path.write_bytes(original)

    def test_current_readiness_consumer_authenticates_portable_manifest(self):
        # Use an ordinary successor selector: no portability switch or PASS field
        # is accepted from the selector itself.
        base = self.root / "reports/current-publication-validation"
        base.mkdir(parents=True, exist_ok=True)
        original_semantic = self.root / semantic.REPORT_PATH
        original_semantic.write_text('{"historical": true}')
        original_commands = base / "commands.json"
        original_commands.write_text('{"historical": true}')
        selected_semantic = base / "portable-run.json"
        selected_semantic.write_bytes((self.root / self.report_path).read_bytes())
        selected_commands = base / "portable-commands.json"
        selected_commands.write_text('{"commands": []}')
        def ref(path):
            value = semantic.fingerprint(path, self.root)
            return {k: value[k] for k in ("path", "sha256")}
        selector = {"schema_version": 1, "semantic": ref(selected_semantic),
                    "validation": ref(selected_commands), "predecessors": {
                        "semantic": ref(original_semantic), "validation": ref(original_commands)}}
        (self.root / readiness.CURRENT_EVIDENCE).write_text(json.dumps(selector))
        _, _, metadata = readiness.selected_evidence(self.root)
        self.assertEqual(metadata["portable_semantic_custody"]["path"], portable.manifest_path(self.report))
        self.manifest.unlink()
        self.assertIsNone(readiness.selected_evidence(self.root)[2]["portable_semantic_custody"])
        shutil.rmtree(self.root / "build/execution-fixture")
        self.assertTrue(semantic.reconcile_raw_evidence(self.report, self.root)[1])


if __name__ == "__main__":
    unittest.main()
