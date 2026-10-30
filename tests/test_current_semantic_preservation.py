"""Historical byte custody and tightly bounded semantic-product advancement."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import current_documentary_workbook as documentary
import current_assessment as assessment
import current_publication_preservation as preservation
import current_retained_evidence as retained
import current_semantic_generation as generation
import current_semantic_workbook as semantic
import current_source_identity as identity


class SemanticPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((identity.ROOT / identity.RECORD).read_text())
        cls.baseline = json.loads(preservation.BASELINE.read_text())
        groups = preservation.protected_groups()
        cls.paths = {path for paths in groups.values() for path in paths}
        cls.paths.update({identity.WORKBOOK, *identity.SOURCES, *identity.TARGETS,
                          *identity.PRODUCTS, *identity.CONFIGURATION,
                          *documentary.evidence_paths(identity.ROOT)})
        # Regenerated reports retain their historical identity through exact
        # snapshots and logical-path bindings, including reports outside the
        # documentary workbook's own evidence references.
        historical = preservation.trusted_tree(identity.ROOT, preservation.EXPECTED_BASELINE_HEAD)
        for relative in groups["historical_authorities"]:
            cls.paths.update(retained.evidence_paths(
                identity.ROOT, relative, historical[relative]["sha256"]))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="semantic-preservation-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".git").symlink_to(identity.ROOT / ".git", target_is_directory=True)
        for relative in self.paths:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(identity.ROOT / relative, path)
        # Historical custody/mutation scenarios retain the accepted checkpoint
        # as their starting state. Live semantic decisions are tested separately.
        for relative in (identity.WORKBOOK, preservation.ASSESSMENT, *identity.PRODUCTS):
            (self.root / relative).write_bytes(subprocess.check_output([
                "git", "-C", str(identity.ROOT), "show",
                f"{identity.ACCEPTED_CHECKPOINT_HEAD}:{relative}"]))
        shutil.rmtree(self.root / semantic.TRANSITIONS, ignore_errors=True)
        self.expected = {entry["path"]: copy.deepcopy(entry) for entry in self.document["products"]}

    def test_accepted_checkpoint_keeps_original_baseline_and_identity(self):
        before = copy.deepcopy(self.document)
        self.assertEqual(identity.check_record(self.document, self.root), [])
        result = preservation.preservation(self.root, self.baseline)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["baseline_head"], identity.IDENTITY_BASELINE_HEAD)
        self.assertEqual(result["accepted_checkpoint_head"], identity.ACCEPTED_CHECKPOINT_HEAD)
        self.assertEqual(self.document, before)

    def test_arbitrary_head_is_not_authorized_by_checkpoint(self):
        original_git = identity.git
        def changed_head(root, *args):
            return "f" * 40 if args == ("rev-parse", "HEAD") else original_git(root, *args)
        with patch.object(identity, "git", side_effect=changed_head):
            self.assertTrue(identity.checkpoint_errors(self.root))
            self.assertTrue(any("HEAD" in item for item in identity.check_record(self.document, self.root)))
            self.assertEqual(preservation.preservation(self.root, self.baseline)["status"], "FAIL")

    def test_checkpoint_requires_retained_coverage_pair(self):
        logical = "reports/coms-source-term-coverage.md"
        historical = preservation.trusted_tree(self.root, preservation.EXPECTED_BASELINE_HEAD)
        dependencies = retained.evidence_paths(self.root, logical, historical[logical]["sha256"])
        retained_paths = [relative for relative in dependencies if relative != logical]
        self.assertEqual(len(retained_paths), 2)
        for relative in retained_paths:
            with self.subTest(missing=relative):
                path = self.root / relative
                original = path.read_bytes()
                try:
                    path.unlink()
                    result = preservation.preservation(self.root, self.baseline)
                    self.assertEqual(result["status"], "FAIL")
                    self.assertIn(logical, result["groups"]["historical_authorities"]["changed_paths"])
                    self.assertTrue(any(error.startswith("historical report custody:")
                                        and logical in error for error in result["errors"]))
                finally:
                    path.write_bytes(original)

    def test_freeze_cannot_replace_historical_identity(self):
        path = self.root / identity.RECORD
        before = path.read_bytes()
        with patch.object(identity, "ROOT", self.root), patch.object(sys, "argv", ["identity", "--freeze"]), \
                patch("builtins.print"):
            self.assertEqual(identity.main(), 1)
        self.assertEqual(path.read_bytes(), before)

    def test_checkpoint_custody_files_remain_exact(self):
        for relative in (
                "reports/current-human-decisions/2026-10-25-sample-pair/hasSample.json",
                "reports/current-documentary-workbook/updates/5f0e3bc5-b52e-4502-8fd5-f7f1c182913b.json"):
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                result = preservation.preservation(self.root, self.baseline)
                self.assertIn(relative, result["groups"]["checkpoint_custody_evidence"]["changed_paths"])
                self.assertEqual(result["status"], "FAIL")
                path.write_bytes(original)

    def test_product_drift_requires_semantic_transition(self):
        path = self.root / identity.PRODUCTS[0]
        path.write_bytes(path.read_bytes() + b"\n# Unexplained generated drift\n")
        self.assertTrue(any("byte identity drift" in error for error in identity.check_record(self.document, self.root)))
        result = preservation.preservation(self.root, self.baseline)
        self.assertEqual(result["semantic_product_evolution"]["status"], "FAIL")
        self.assertIn("no governed semantic transition", result["semantic_product_evolution"]["error"])

    def test_declared_transition_cannot_authorize_arbitrary_product_bytes(self):
        rendered = {path: (self.root / path).read_bytes() for path in identity.PRODUCTS}
        path = self.root / identity.PRODUCTS[0]
        path.write_bytes(path.read_bytes() + b"\n# Not generated from workbook\n")
        with patch.object(semantic, "resolve_history", return_value={"chain": [{"kind": "semantic"}]}), \
                patch.object(generation, "render_current_products", return_value=rendered):
            with self.assertRaisesRegex(ValueError, "differs from validated deterministic generation"):
                identity.validated_product_evolution(self.root, self.expected)

    def test_validated_exact_product_generation_preserves_historical_fingerprints(self):
        # Contract fixture: chain and renderer are covered by their own real
        # integration suites. This test isolates protection of the old identity.
        rendered = {path: (self.root / path).read_bytes() for path in identity.PRODUCTS}
        rendered[identity.PRODUCTS[0]] += b"\n# Deterministically rendered fixture\n"
        (self.root / identity.PRODUCTS[0]).write_bytes(rendered[identity.PRODUCTS[0]])
        before = copy.deepcopy(self.expected)
        history = semantic.resolve_history(self.root)
        history["chain"].append({"kind": "semantic"})
        with patch.object(semantic, "resolve_history", return_value=history), \
                patch.object(generation, "render_current_products", return_value=rendered):
            result = identity.validated_product_evolution(self.root, self.expected)
            self.assertEqual(result["status"], "VALIDATED")
            self.assertEqual(identity.check_record(self.document, self.root), [])
            preserved = preservation.preservation(self.root, self.baseline)
            self.assertEqual(preserved["status"], "PASS", preserved["errors"])
            self.assertEqual(preserved["semantic_product_evolution"]["status"], "VALIDATED")
        self.assertEqual(self.expected, before)
        self.assertNotEqual(result["products"][identity.PRODUCTS[0]]["sha256"],
                            self.expected[identity.PRODUCTS[0]]["sha256"])

    def test_forged_historical_product_identity_is_rejected(self):
        self.expected[identity.PRODUCTS[0]]["sha256"] = "f" * 64
        with patch.object(semantic, "resolve_history", return_value={"chain": [{"kind": "semantic"}]}):
            with self.assertRaisesRegex(ValueError, "historical product identity differs"):
                identity.validated_product_evolution(self.root, self.expected)

    def test_partial_product_inventory_is_rejected(self):
        self.expected.pop(identity.PRODUCTS[0])
        with self.assertRaisesRegex(ValueError, "all four"):
            identity.validated_product_evolution(self.root, self.expected)

    def test_semantic_product_exception_never_covers_source_target_or_other_tracks(self):
        for relative in (identity.SOURCES[0], identity.TARGETS[0], "src/sosa-next/imports/sosa.ttl"):
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\n# Protected ontology drift\n")
                with patch.object(preservation, "validated_product_evolution", return_value={"status": "VALIDATED"}):
                    result = preservation.preservation(self.root, self.baseline)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any(relative in group["changed_paths"] for group in result["groups"].values()))
                if relative in (*identity.SOURCES, *identity.TARGETS):
                    self.assertTrue(any(relative + ": byte identity drift" in error
                                        for error in identity.check_record(self.document, self.root)))
                path.write_bytes(original)

    def test_real_semantic_transition_advances_products_without_replacing_old_authorities(self):
        candidate = self.root / "candidate.xlsx"
        workbook = load_workbook(self.root / identity.WORKBOOK)
        workbook["Sheet2"]["B49"] = None
        workbook["Sheet2"]["C49"] = None
        workbook["Sheet2"]["D49"] = "Disposable restoration of the recorded rejection."
        workbook["Sheet2"].append([
            "sosa:madeBySensor", "rdfs:subPropertyOf", "cco:has_agent",
            "Disposable restoration of the retained sensor inclusion.",
            "urn:uuid:ce35979c-d166-45ea-afce-11491dbb975e"])
        workbook.save(candidate)
        workbook.close()
        evidence = "reports/mapping-consistency-resolution-plan.md"
        delta = semantic.workbook_delta(self.root / identity.WORKBOOK, candidate)
        authorities = {}
        for row in delta["changed_rows"]:
            added = row["old"] is None
            evidence = ("reports/inverse-side-direct-mapping-policy-review.md" if added else
                        "reports/mapping-consistency-resolution-plan.md")
            authorities[row["row_id"]] = {
                "authorization_type": ("RESTORE_PREVIOUSLY_APPROVED_DECISION" if added else
                                       "REMOVE_PREVIOUSLY_REJECTED_MAPPING"),
                "rationale": "Disposable restoration of an expressly retained historical decision.",
                "evidence": [{"path": evidence, "sha256": documentary.digest((self.root / evidence).read_bytes()),
                              "reference": "Retained sensor inclusion or explicit forProperty-chain rejection"}],
            }
        before = copy.deepcopy(self.document)
        transition = semantic.create_transition(
            self.root, self.root / identity.WORKBOOK, candidate, authorities,
            editor_identity="Isolated preservation test", timestamp="2026-10-26T01:00:00+00:00")
        shutil.copyfile(candidate, self.root / identity.WORKBOOK)
        assessment_path = self.root / preservation.ASSESSMENT
        original_assessment = json.loads(assessment_path.read_text())
        evolved = assessment.evolve_unreviewed_row_ids(self.root, original_assessment)
        assessment_path.write_text(assessment.json_text(evolved))
        # The workbook chain alone must not accept stale generated products.
        self.assertTrue(any("semantic workbook products" in error
                            for error in identity.check_record(self.document, self.root)))
        stale = preservation.preservation(self.root, self.baseline)
        self.assertEqual(stale["semantic_product_evolution"]["status"], "FAIL")
        self.assertEqual(stale["status"], "FAIL")
        self.assertEqual(stale["assessment_row_id_evolution"]["status"], "VALIDATED")
        assessment_path.write_text(assessment.json_text(original_assessment))
        for relative, data in generation.render_current_products(self.root, self.root / identity.WORKBOOK).items():
            (self.root / relative).write_bytes(data)
        self.assertEqual(identity.check_record(self.document, self.root), [])
        result = preservation.preservation(self.root, self.baseline)
        self.assertEqual(result["assessment_row_id_evolution"]["status"], "FAIL")
        assessment_path.write_text(assessment.json_text(evolved))
        result = preservation.preservation(self.root, self.baseline)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertFalse(result["documentary_workbook_evolution"]["semantic_projection_preserved"])
        self.assertEqual(result["semantic_product_evolution"]["status"], "VALIDATED")
        self.assertEqual(result["assessment_row_id_evolution"]["status"], "VALIDATED")
        self.assertEqual(self.document, before)
        changed = copy.deepcopy(evolved)
        changed["records"][0]["rationale"] = "Unauthorized rationale mutation."
        assessment_path.write_text(assessment.json_text(changed))
        self.assertEqual(preservation.preservation(self.root, self.baseline)["assessment_row_id_evolution"]["status"], "FAIL")
        assessment_path.write_text(assessment.json_text(evolved))
        forged = json.loads(transition.read_text())
        forged["delta"]["changed_rows"] = []
        transition.write_bytes(documentary.canonical_bytes(forged))
        self.assertTrue(any("byte identity drift" in error for error in identity.check_record(self.document, self.root)))
        self.assertEqual(preservation.preservation(self.root, self.baseline)["status"], "FAIL")

    def test_assessment_row_id_mutation_without_transition_fails(self):
        path = self.root / preservation.ASSESSMENT
        document = json.loads(path.read_text())
        document["records"][0]["mapping_row_ids"].append("urn:uuid:ce35979c-d166-45ea-afce-11491dbb975e")
        path.write_text(assessment.json_text(document))
        result = preservation.preservation(self.root, self.baseline)
        self.assertEqual(result["assessment_row_id_evolution"]["status"], "FAIL")
        self.assertIn(preservation.ASSESSMENT, result["groups"]["checkpoint_custody_evidence"]["changed_paths"])


class ExplicitHumanAssessmentPreservationTests(unittest.TestCase):
    """Isolate exact authority linkage; live integration authenticates packets."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="new-human-preservation-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.row_id = "urn:uuid:287f1392-ca8f-4dc2-9d42-b60b3962adfc"
        self.iri = "http://www.w3.org/ns/ssn/forProperty"
        self.before = {"source_iri": self.iri, "source_kind": "object_property",
                       "review_state": "unreviewed", "assessment_outcome": "unreviewed",
                       "mapping_row_ids": [self.row_id], "rationale": "Unresolved fixture.",
                       "evidence": ["fixture evidence"], "review": {"question": "Fixture question?"}}
        self.historical = {"schema_version": 1, "records": [copy.deepcopy(self.before)]}
        prior = self.root / "assessment-before.json"
        prior.write_text(assessment.json_text(self.historical))
        self.decision = {"source_iri": self.iri, "review_state": "final",
                         "assessment_outcome": "no_direct_mapping", "rationale": "Reviewed fixture rationale.",
                         "evidence_refs": ["reviewed fixture evidence"],
                         "input_hashes": {"workbook_sha256": "a" * 64},
                         "assessment_snapshot": {"path": prior.name, "sha256": assessment.sha(prior)}}
        self.decision_path = self.root / "decision.json"
        self.transition = {"kind": "semantic", "transition_id": "fixture-explicit-transition",
                           "new_workbook_sha256": "a" * 64, "authorities": {}}
        self.candidate = copy.deepcopy(self.historical)
        self.save_decision()
        self.candidate["records"][0].update(
            review_state="final", assessment_outcome="no_direct_mapping",
            rationale=self.decision["rationale"], evidence=self.decision["evidence_refs"])
        self.evolution = patch.object(assessment, "evolve_unreviewed_row_ids",
                                      side_effect=lambda root, document: copy.deepcopy(document))
        self.evolution.start()
        self.addCleanup(self.evolution.stop)
        self.history = patch.object(semantic, "resolve_history",
                                    side_effect=lambda root: {"chain": [self.transition]})
        self.history.start()
        self.addCleanup(self.history.stop)
        self.authentication = patch.object(preservation, "_authenticate_current_assessment")
        self.authenticate = self.authentication.start()
        self.addCleanup(self.authentication.stop)

    def save_decision(self):
        self.decision_path.write_text(assessment.json_text(self.decision))
        ref = {"path": self.decision_path.name, "sha256": assessment.sha(self.decision_path)}
        self.candidate["records"][0]["human_decision_record"] = ref
        self.transition["authorities"][self.row_id] = {
            "authorization_type": "EXPLICIT_NEW_HUMAN_DECISION", "human_decision": copy.deepcopy(ref)}

    def validate(self):
        return preservation.validated_assessment_evolution(self.root, self.historical, self.candidate)

    def test_exact_explicit_decision_is_derived_and_fully_authenticated(self):
        historical = copy.deepcopy(self.historical)
        result = self.validate()
        self.assertEqual(result["new_human_decisions"][0]["source_iri"], self.iri)
        self.authenticate.assert_called_once_with(self.root, self.candidate)
        self.assertEqual(self.historical, historical)

    def test_historical_authority_cannot_authorize_new_final(self):
        self.transition["authorities"][self.row_id]["authorization_type"] = "REMOVE_PREVIOUSLY_REJECTED_MAPPING"
        with self.assertRaisesRegex(ValueError, "exact explicit-human transition"):
            self.validate()
        self.authenticate.assert_not_called()

    def test_different_human_record_cannot_be_substituted(self):
        self.transition["authorities"][self.row_id]["human_decision"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "exact explicit-human transition"):
            self.validate()

    def test_unbound_and_other_transition_workbook_decisions_fail(self):
        self.decision["input_hashes"]["workbook_sha256"] = "b" * 64
        self.save_decision()
        with self.assertRaisesRegex(ValueError, "selected workbook"):
            self.validate()

    def test_duplicate_transition_authority_is_rejected(self):
        self.history.stop()
        self.history = patch.object(semantic, "resolve_history",
                                    return_value={"chain": [self.transition, copy.deepcopy(self.transition)]})
        self.history.start()
        self.addCleanup(self.history.stop)
        with self.assertRaisesRegex(ValueError, "one exact explicit-human"):
            self.validate()

    def test_unrelated_record_fields_and_inventory_metadata_are_protected(self):
        original = copy.deepcopy(self.candidate)
        for change in (lambda: self.candidate.update(schema_version=2),
                       lambda: self.candidate["records"][0]["review"].update(question="Rewritten question?"),
                       lambda: self.candidate["records"][0].update(source_kind="class"),
                       lambda: self.candidate["records"][0].update(extra="Unapproved fact")):
            with self.subTest(change=change):
                self.candidate = copy.deepcopy(original)
                change()
                with self.assertRaises(ValueError):
                    self.validate()

    def test_accepted_final_cannot_be_rewritten_even_with_new_authority(self):
        self.historical["records"][0].update(review_state="final", assessment_outcome="no_direct_mapping")
        with self.assertRaisesRegex(ValueError, "cannot alter an accepted final"):
            self.validate()

    def test_forged_predecision_snapshot_cannot_rewrite_prior_review(self):
        prior = self.root / "assessment-before.json"
        forged = copy.deepcopy(self.historical)
        forged["records"][0]["rationale"] = "Forged historical rationale."
        prior.write_text(assessment.json_text(forged))
        self.decision["assessment_snapshot"]["sha256"] = assessment.sha(prior)
        self.save_decision()
        with self.assertRaisesRegex(ValueError, "differs from trusted assessment"):
            self.validate()

    def test_full_packet_or_applicability_failure_is_not_waived(self):
        self.authenticate.side_effect = ValueError("Invalid packet or current applicability")
        with self.assertRaisesRegex(ValueError, "Invalid packet"):
            self.validate()


class LiveAdjudicationPreservationTests(unittest.TestCase):
    def test_three_current_new_decisions_preserve_the_checkpoint(self):
        historical = json.loads(subprocess.check_output([
            "git", "-C", str(identity.ROOT), "show",
            f"{identity.ACCEPTED_CHECKPOINT_HEAD}:{preservation.ASSESSMENT}"]))
        candidate = json.loads((identity.ROOT / preservation.ASSESSMENT).read_text())
        result = preservation.validated_assessment_evolution(identity.ROOT, historical, candidate)
        self.assertEqual({entry["source_iri"] for entry in result["new_human_decisions"]}, {
            "http://www.w3.org/ns/ssn/forProperty",
            "http://www.w3.org/ns/ssn/systems/SystemProperty",
            "http://www.w3.org/ns/ssn/systems/MeasurementRange"})


if __name__ == "__main__":
    unittest.main()
