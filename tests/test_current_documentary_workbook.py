"""Real-workbook, isolated tests for the project-local documentary guard."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from uuid import uuid4

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_documentary_workbook as guard
import current_semantic_workbook as semantic


class DocumentaryWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.baseline = json.loads((ROOT / guard.BASELINE).read_text())
        paths = [guard.BASELINE, guard.WORKBOOK,
                 self.baseline["historical_workbook"]["path"]]
        paths += [ref["path"] for ref in self.baseline["immutable_evidence"]]
        for relative in paths:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.live = self.root / guard.WORKBOOK
        # Historical mutation scenarios start at the immutable decision-time
        # workbook, even after the maintained live workbook has evolved.
        shutil.copyfile(self.root / self.baseline["historical_workbook"]["path"], self.live)
        self.original = self.live.read_bytes()
        self.historical_hash = guard.digest(self.original)
        self.ref = copy.deepcopy(next(ref for ref in self.baseline["immutable_evidence"]
                                     if ref["path"].endswith("approved-instructions.txt")))
        self.ref["reference"] = "Isolated test fixture documentary evidence"

    def candidate(self, edits, source=None):
        path = self.root / ("candidate-" + str(uuid4()) + ".xlsx")
        workbook = load_workbook(source or self.live)
        try:
            for sheet, cell, value in edits:
                workbook[sheet][cell] = value
            workbook.save(path)
        finally:
            workbook.close()
        return path

    def record(self, candidate, edits, old=None, **kwargs):
        evidence = {sheet + "!" + cell: [self.ref] for sheet, cell, _ in edits}
        return guard.create_update(self.root, old or self.live, candidate, evidence,
                                   editor_identity="Documentary guard test", **kwargs)

    def install(self, candidate):
        shutil.copyfile(candidate, self.live)

    def validate(self):
        return guard.validate_workbook_evolution(self.root, self.historical_hash)

    def save_record(self, path, document):
        path.write_bytes(guard.canonical_bytes(document))

    def reset_history(self):
        self.live.write_bytes(self.original)
        shutil.rmtree(self.root / guard.UPDATES, ignore_errors=True)
        for path in (self.root / guard.VERSIONS).glob("*.xlsx"):
            if path.stem != self.historical_hash:
                path.unlink()

    def test_projection_is_deterministic_and_baseline_is_bound(self):
        self.assertEqual(guard.digest((self.root / guard.BASELINE).read_bytes()),
                         guard.BASELINE_SHA256)
        self.assertEqual(guard.semantic_projection_sha256(self.live),
                         "d42340112492fa033216870de64848d899ffd39041be013b7ecc1b655d68136b")
        self.assertEqual(guard.semantic_projection_sha256(self.live),
                         guard.semantic_projection_sha256(self.live))
        view = guard.semantic_projection(self.live)
        self.assertEqual([sheet["name"] for sheet in view["sheets"]], ["Sheet1", "Sheet2"])
        self.assertEqual(sum(len(sheet["rows"]) - 1 for sheet in view["sheets"]), 105)
        self.assertEqual(self.validate().read_bytes(), self.original)

    def test_maintained_live_workbook_resolves_to_immutable_decision_snapshot(self):
        # Exercise the actual mixed history separately from the isolated
        # historical scenarios; an unrecorded live edit must still fail.
        historical = self.baseline["historical_workbook"]
        snapshot = semantic.validate_workbook_evolution(ROOT, historical["sha256"])
        self.assertEqual(snapshot, ROOT / historical["path"])
        self.assertEqual(guard.digest(snapshot.read_bytes()), historical["sha256"])
        self.assertEqual(guard.semantic_projection_sha256(snapshot), historical["semantic_projection_sha256"])
        # Preserve the former live projection as an immutable historical check.
        prior = semantic.snapshot(ROOT, "778a567168143160c152110e79a32a86eea318710dbde078fa0525482bbccb4c")
        self.assertEqual(guard.digest(prior.read_bytes()), prior.stem)
        self.assertEqual(guard.semantic_projection_sha256(prior),
                         "566d6a6ba6200458eab5ea7561c86d0eb2483765fa5a1a7c2e8ff0526654eb44")
        self.assertEqual(guard.semantic_projection_sha256(ROOT / guard.WORKBOOK),
                         "3c373fa8d28164bd116be0779815c823cf457c4853147982a039dc08caf214ff")

    def test_one_unrelated_reasoning_cell_passes_without_editing_live(self):
        edits = [("Sheet1", "D13", "Documentary description from retained evidence.")]
        candidate = self.candidate(edits)
        record = self.record(candidate, edits)
        self.assertEqual(self.live.read_bytes(), self.original)
        document = json.loads(record.read_text())
        self.assertEqual(document["changes"][0]["new_value"], edits[0][2])
        self.assertEqual(document["changes"][0]["new_value_sha256"], guard.value_hash(edits[0][2]))
        self.assertEqual(document["old_semantic_projection_sha256"], document["new_semantic_projection_sha256"])
        self.install(candidate)
        self.assertEqual(self.validate().read_bytes(), self.original)
        self.assertIn(record.relative_to(self.root).as_posix(), guard.evidence_paths(self.root))

    def test_many_reasoning_cells_pass(self):
        edits = [("Sheet1", "D13", "First documented rationale"),
                 ("Sheet1", "D14", "Second documented rationale"),
                 ("Sheet2", "D15", "Third documented rationale")]
        candidate = self.candidate(edits)
        record = self.record(candidate, edits)
        self.assertEqual(len(json.loads(record.read_text())["changes"]), 3)
        self.install(candidate)
        self.validate()

    def test_exact_approved_pair_rationale_passes(self):
        edits = []
        for cell, name in (("D16", "hasSample"), ("D17", "isSampleOf")):
            entry = next(e for e in self.baseline["decisions"] if e["source_iri"].endswith("/" + name))
            decision = json.loads((self.root / entry["path"]).read_text())
            edits.append(("Sheet2", cell, decision["rationale"]))
        candidate = self.candidate(edits)
        self.record(candidate, edits)
        self.install(candidate)
        self.validate()
        for entry in self.baseline["immutable_evidence"]:
            self.assertEqual(guard.digest((self.root / entry["path"]).read_bytes()), entry["sha256"])

    def test_two_version_chain_passes_and_resolves_intermediate(self):
        first_edits = [("Sheet1", "D13", "First documentary version")]
        first = self.candidate(first_edits)
        self.record(first, first_edits, timestamp="2026-10-25T21:00:00+00:00")
        second_edits = [("Sheet2", "D14", "Second documentary version")]
        second = self.candidate(second_edits, source=first)
        self.record(second, second_edits, old=first, timestamp="2026-10-25T21:01:00+00:00")
        self.install(second)
        self.assertEqual(self.validate().read_bytes(), self.original)
        resolved = guard.validate_workbook_evolution(self.root, guard.digest(first.read_bytes()))
        self.assertEqual(resolved.read_bytes(), first.read_bytes())

    def test_semantic_columns_fail_even_with_forged_equal_projection_claims(self):
        for column, value in (("A", "sosa:WrongSource"), ("B", "owl:equivalentClass"),
                              ("C", "bfo:BFO_9999999"),
                              ("E", "urn:uuid:00000000-0000-4000-8000-000000000001")):
            with self.subTest(column=column):
                edits = [("Sheet1", "D13", "Documentary change")]
                candidate = self.candidate(edits)
                record = self.record(candidate, edits)
                document = json.loads(record.read_text())
                forged = self.candidate([("Sheet1", column + "13", value)], source=candidate)
                forged_hash = guard.digest(forged.read_bytes())
                (self.root / guard.VERSIONS / (forged_hash + ".xlsx")).write_bytes(forged.read_bytes())
                document["new_workbook_sha256"] = forged_hash
                # Both declared projection hashes still claim the baseline value.
                self.save_record(record, document)
                self.install(forged)
                with self.assertRaisesRegex(ValueError, "projection"):
                    self.validate()
                self.reset_history()

    def test_semantic_edits_are_rejected_before_any_record_is_written(self):
        for column in "ABCE":
            with self.subTest(column=column):
                candidate = self.candidate([("Sheet1", column + "13", "changed semantic content")])
                with self.assertRaisesRegex(ValueError, "projection"):
                    self.record(candidate, [("Sheet1", "D13", "unused")])
                self.assertFalse((self.root / guard.UPDATES).exists())

    def test_row_order_sheet_identity_and_sheet_order_fail(self):
        for kind in ("rows", "sheet_name", "sheet_order"):
            with self.subTest(kind=kind):
                candidate = self.root / "order.xlsx"
                workbook = load_workbook(self.live)
                if kind == "rows":
                    sheet = workbook["Sheet1"]
                    a, b = [[sheet.cell(row, col).value for col in range(1, 6)] for row in (13, 14)]
                    for col in range(1, 6):
                        sheet.cell(13, col).value, sheet.cell(14, col).value = b[col - 1], a[col - 1]
                elif kind == "sheet_name":
                    workbook["Sheet1"].title = "Renamed"
                else:
                    workbook.move_sheet("Sheet2", offset=-1)
                workbook.save(candidate)
                workbook.close()
                with self.assertRaises(ValueError):
                    self.record(candidate, [("Sheet1", "D13", "unused")])

    def test_unrecorded_reasoning_change_fails_despite_equal_projection(self):
        candidate = self.candidate([("Sheet1", "D13", "Unrecorded rationale")])
        self.assertEqual(guard.semantic_projection_sha256(candidate),
                         guard.semantic_projection_sha256(self.live))
        self.install(candidate)
        with self.assertRaisesRegex(ValueError, "complete documentary update chain"):
            self.validate()

    def test_forged_projection_hash_and_forged_full_hash_fail(self):
        for field in ("old_semantic_projection_sha256", "new_semantic_projection_sha256",
                      "old_workbook_sha256", "new_workbook_sha256"):
            with self.subTest(field=field):
                edits = [("Sheet1", "D13", "Documentary change")]
                candidate = self.candidate(edits)
                record = self.record(candidate, edits)
                document = json.loads(record.read_text())
                document[field] = "0" * 64
                self.save_record(record, document)
                self.install(candidate)
                with self.assertRaises(ValueError):
                    self.validate()
                self.reset_history()

    def test_omitted_duplicate_and_inexact_changed_cells_fail(self):
        for mutation in ("omitted", "duplicate", "old_value", "new_hash", "cell", "row_id"):
            with self.subTest(mutation=mutation):
                edits = [("Sheet1", "D13", "First change"), ("Sheet1", "D14", "Second change")]
                candidate = self.candidate(edits)
                record = self.record(candidate, edits)
                document = json.loads(record.read_text())
                changes = document["changes"]
                if mutation == "omitted":
                    changes.pop()
                elif mutation == "duplicate":
                    changes[1] = copy.deepcopy(changes[0])
                elif mutation == "old_value":
                    changes[0]["old_value"] = "false history"
                    changes[0]["old_value_sha256"] = guard.value_hash("false history")
                elif mutation == "new_hash":
                    changes[0]["new_value_sha256"] = "0" * 64
                elif mutation == "cell":
                    changes[0]["cell"] = "B13"
                else:
                    changes[0]["row_id"] = changes[1]["row_id"]
                self.save_record(record, document)
                self.install(candidate)
                with self.assertRaises(ValueError):
                    self.validate()
                self.reset_history()

    def test_evidence_is_complete_existing_and_hash_bound_before_writes(self):
        edits = [("Sheet1", "D13", "Documentary value")]
        candidate = self.candidate(edits)
        for evidence in ({}, {"Sheet1!D13": []},
                         {"Sheet1!D13": [{"path": "missing.txt", "sha256": "0" * 64}]},
                         {"Sheet1!D13": [{**self.ref, "sha256": "0" * 64}]},
                         {"Sheet1!D13": [{**self.ref, "unsupported": "field"}]},
                         {"Sheet1!D13": [{**self.ref, "reference": ""}]},
                         {"Sheet1!D13": [{**self.ref, "path": "../outside.txt"}]}):
            with self.subTest(evidence=evidence):
                with self.assertRaises(ValueError):
                    guard.create_update(self.root, self.live, candidate, evidence, editor_identity="Test")
                self.assertFalse((self.root / guard.UPDATES).exists())
                self.assertEqual(len(list((self.root / guard.VERSIONS).iterdir())), 1)

    def test_retained_bytes_are_checked_not_only_filenames_and_claims(self):
        edits = [("Sheet1", "D13", "Documentary value")]
        candidate = self.candidate(edits)
        self.record(candidate, edits)
        self.install(candidate)
        snapshot = self.root / guard.VERSIONS / (guard.digest(candidate.read_bytes()) + ".xlsx")
        snapshot.write_bytes(self.original)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.validate()

    def test_missing_retained_snapshot_fails(self):
        edits = [("Sheet1", "D13", "Documentary value")]
        candidate = self.candidate(edits)
        self.record(candidate, edits)
        self.install(candidate)
        (self.root / self.baseline["historical_workbook"]["path"]).unlink()
        with self.assertRaisesRegex(ValueError, "missing retained evidence"):
            self.validate()

    def test_immutable_decision_validation_requires_historical_workbook_even_without_transition(self):
        records = json.loads((ROOT / "mappings/current-ssn-sosa-assessment.json").read_text())["records"]
        guard.validate_immutable_decisions(self.root, records)
        snapshot = self.root / self.baseline["historical_workbook"]["path"]
        snapshot.write_bytes(b"tampered historical bytes")
        with self.assertRaisesRegex(ValueError, "immutable"):
            guard.validate_immutable_decisions(self.root, records)
        snapshot.unlink()
        with self.assertRaisesRegex(ValueError, "immutable"):
            guard.validate_immutable_decisions(self.root, records)
        self.assertEqual(self.live.read_bytes(), self.original)

    def test_unanchored_history_and_baseline_rewrite_fail(self):
        path = self.root / guard.BASELINE
        baseline = json.loads(path.read_text())
        baseline["historical_workbook"]["semantic_projection_sha256"] = "0" * 64
        path.write_bytes(guard.canonical_bytes(baseline))
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.validate()
        path.unlink()
        self.assertTrue(all((self.root / p).is_file() for p in guard.evidence_paths(self.root)))
        with self.assertRaises(ValueError):
            self.validate()

    def test_chain_branching_and_disconnected_links_fail(self):
        for mutation in ("branch", "orphan"):
            with self.subTest(mutation=mutation):
                edits = [("Sheet1", "D13", "Documentary value")]
                candidate = self.candidate(edits)
                record = self.record(candidate, edits)
                document = json.loads(record.read_text())
                document["update_id"] = str(uuid4())
                destination = record.with_name(document["update_id"] + ".json")
                if mutation == "orphan":
                    document["old_workbook_sha256"], document["new_workbook_sha256"] = document["new_workbook_sha256"], document["old_workbook_sha256"]
                    for change in document["changes"]:
                        change["old_value"], change["new_value"] = change["new_value"], change["old_value"]
                        change["old_value_sha256"], change["new_value_sha256"] = change["new_value_sha256"], change["old_value_sha256"]
                    record.unlink()
                self.save_record(destination, document)
                self.install(candidate)
                with self.assertRaises(ValueError):
                    self.validate()
                self.reset_history()

    def test_timestamp_identity_and_exact_record_shape_are_enforced(self):
        for field, value in (("timestamp", "2026-10-25T21:00:00"),
                             ("editor_identity", "  "), ("update_id", "not-a-uuid"),
                             ("allowed_column", "coms:Target"),
                             ("semantic_columns_unchanged", False), ("workbook_path", "other.xlsx")):
            with self.subTest(field=field):
                edits = [("Sheet1", "D13", "Documentary value")]
                candidate = self.candidate(edits)
                record = self.record(candidate, edits)
                document = json.loads(record.read_text())
                document[field] = value
                self.save_record(record, document)
                self.install(candidate)
                with self.assertRaises(ValueError):
                    self.validate()
                self.reset_history()

    def test_formula_extra_column_sheet_and_non_string_fail(self):
        for kind in ("formula", "column", "sheet", "number", "malformed"):
            with self.subTest(kind=kind):
                candidate = self.root / "unsupported.xlsx"
                if kind == "malformed":
                    candidate.write_bytes(b"not an xlsx archive")
                else:
                    workbook = load_workbook(self.live)
                    if kind == "formula":
                        workbook["Sheet1"]["D13"] = "=1+1"
                    elif kind == "column":
                        workbook["Sheet1"]["F13"] = "unrepresented column"
                    elif kind == "sheet":
                        workbook.create_sheet("Extra")
                    else:
                        workbook["Sheet1"]["D13"] = 42
                    workbook.save(candidate)
                    workbook.close()
                with self.assertRaises(ValueError):
                    guard.semantic_projection(candidate)

    def test_symbolic_link_archive_components_are_rejected(self):
        versions = self.root / guard.VERSIONS
        moved = versions.with_name("actual-versions")
        versions.rename(moved)
        versions.symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "non-project or noncanonical"):
            self.validate()

    def test_semantic_projection_preserves_exact_strings_and_null(self):
        for value in (" sosa:Thing", "sosa:Thing ", "", None):
            candidate = self.candidate([("Sheet1", "A13", value)])
            self.assertNotEqual(guard.semantic_projection_sha256(candidate),
                                guard.semantic_projection_sha256(self.live))
        edits = [("Sheet1", "D13", "  documentary whitespace\n")]
        candidate = self.candidate(edits)
        record = self.record(candidate, edits)
        self.assertEqual(json.loads(record.read_text())["changes"][0]["new_value"], edits[0][2])

    def test_explicit_empty_string_cannot_impersonate_absent_semantic_value(self):
        original_view = guard.workbook_view(self.live)
        self.assertIsNone(original_view["sheets"][1]["rows"][15][1])
        candidate = self.candidate([("Sheet2", "B16", "")])
        self.assertEqual(guard.workbook_view(candidate)["sheets"][1]["rows"][15][1], "")
        self.assertNotEqual(guard.semantic_projection_sha256(candidate),
                            guard.semantic_projection_sha256(self.live))
        with self.assertRaisesRegex(ValueError, "projection"):
            self.record(candidate, [("Sheet2", "D16", "unused")])

    def test_creator_does_not_persist_invalid_or_out_of_order_identity(self):
        edits = [("Sheet1", "D13", "Documentary value")]
        candidate = self.candidate(edits)
        for options in ({"timestamp": "2026-10-25T21:00:00"},
                        {"update_id": "not-a-uuid"}):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    self.record(candidate, edits, **options)
                self.assertFalse((self.root / guard.UPDATES).exists())
        self.record(candidate, edits, timestamp="2026-10-25T21:00:00+00:00")
        next_edits = [("Sheet1", "D14", "Second documentary value")]
        next_candidate = self.candidate(next_edits, source=candidate)
        with self.assertRaisesRegex(ValueError, "timestamps are out of order"):
            self.record(next_candidate, next_edits, old=candidate,
                        timestamp="2026-10-25T20:00:00+00:00")
        self.assertEqual(len(list((self.root / guard.UPDATES).iterdir())), 1)
        self.assertEqual(len(list((self.root / guard.VERSIONS).iterdir())), 2)


if __name__ == "__main__":
    unittest.main()
