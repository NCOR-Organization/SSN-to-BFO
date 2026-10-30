"""The SOSA-2023 generator authenticates and preserves the current track."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import current_documentary_workbook as documentary
import current_semantic_generation as generation
import current_semantic_workbook as semantic
import current_source_identity as identity
import generate_sosa_next_products as products


class CurrentCrossTrackPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="current-cross-track-")
        cls.addClassCleanup(temporary.cleanup)
        cls.root = Path(temporary.name)
        # The fixture reads trusted Git blobs but never modifies Git state.
        (cls.root / ".git").symlink_to(ROOT / ".git", target_is_directory=True)
        paths = {*identity.PRODUCTS, identity.WORKBOOK,
                 "config/publication-metadata.toml", *semantic.SOURCE_TARGET_SHA256,
                 *semantic.GOVERNED_INPUT_SHA256, *semantic.evidence_paths(ROOT)}
        for relative in sorted(paths):
            destination = cls.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        cls.product_paths = {
            key: path.relative_to(ROOT).as_posix()
            for key, path in products.CURRENT_SOSA_PRODUCTS.items()
        }
        cls.transition_paths = sorted(
            path.relative_to(cls.root).as_posix()
            for path in (cls.root / semantic.TRANSITIONS).glob("*.json")
        )
        cls.original = {
            relative: (cls.root / relative).read_bytes()
            for relative in {*identity.PRODUCTS, identity.WORKBOOK,
                             *cls.transition_paths}
        }

    def setUp(self):
        self.restore_fixture()
        self.addCleanup(self.restore_fixture)
        self.enterContext(patch.object(products, "REPO_ROOT", self.root))
        self.enterContext(patch.object(products, "CURRENT_SOSA_PRODUCTS", {
            key: self.root / relative for key, relative in self.product_paths.items()
        }))

    def restore_fixture(self):
        for relative, data in self.original.items():
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)

    def state_hashes(self):
        return {
            **{key: hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
               for key, relative in self.product_paths.items()},
            "workbook_sha256": hashlib.sha256(
                (self.root / identity.WORKBOOK).read_bytes()).hexdigest(),
            "semantic_projection_sha256": documentary.semantic_projection_sha256(
                self.root / identity.WORKBOOK),
        }

    def mutate_artifact(self, relative):
        path = self.root / relative
        if relative == identity.WORKBOOK:
            workbook = load_workbook(path)
            try:
                workbook.worksheets[0].cell(2, 3).value = "urn:test:unauthorized-current-target"
                workbook.save(path)
            finally:
                workbook.close()
        else:
            path.write_bytes(path.read_bytes() + b"\n# Unauthorized fixture mutation.\n")

    def test_no_semantic_transition_retains_baseline_behavior(self):
        # This independent historical fixture contains documentary history,
        # its checkpoint workbook, and the corresponding historical products.
        for relative in (identity.WORKBOOK, *identity.PRODUCTS):
            (self.root / relative).write_bytes(subprocess.check_output([
                "git", "-C", str(ROOT), "show",
                f"{identity.ACCEPTED_CHECKPOINT_HEAD}:{relative}",
            ]))
        for relative in self.transition_paths:
            (self.root / relative).unlink()
        self.assertFalse(any(item["kind"] == "semantic"
                             for item in semantic.resolve_history(self.root)["chain"]))
        expected = self.state_hashes()
        self.assertEqual({key: expected[key] for key in self.product_paths},
                         products.EXPECTED_CURRENT_SOSA_SHA256)
        self.assertEqual(products.authenticate_current_sosa_state(), expected)
        self.assertEqual(self.state_hashes(), expected)

    def test_authorized_current_history_passes_before_and_after_generation(self):
        self.assertTrue(self.transition_paths, "fixture requires real semantic history")
        before = self.state_hashes()
        for key in ("alignment_core", "strict_bfo_mapping"):
            self.assertEqual(before[key], products.EXPECTED_CURRENT_SOSA_SHA256[key])
        output = self.root / "authorized-candidate"
        result = {"fixture": "candidate"}

        def candidate_body(*args, **kwargs):
            # Current-track count overrides must end before 2023 generation.
            self.assertEqual(generation.expected_count("CCO_EXTENSION_AXIOM_COUNT", 55), 55)
            return result

        with patch.object(products, "_build_candidate", side_effect=candidate_body) as build:
            self.assertIs(products.build_candidate(output, reverse_input=True), result)
        build.assert_called_once_with(output, reverse_input=True)
        self.assertEqual(self.state_hashes(), before)

    def test_unauthorized_products_and_workbook_fail_before_generation(self):
        # All four products are protected, including unchanged core/strict.
        for relative in (*self.product_paths.values(), identity.WORKBOOK):
            with self.subTest(path=relative):
                try:
                    before = self.state_hashes()
                    self.mutate_artifact(relative)
                    if relative == identity.WORKBOOK:
                        self.assertNotEqual(self.state_hashes()["semantic_projection_sha256"],
                                            before["semantic_projection_sha256"])
                    with patch.object(products, "_build_candidate") as build:
                        with self.assertRaises((ValueError, RuntimeError)):
                            products.build_candidate(self.root / "rejected-candidate")
                    build.assert_not_called()
                finally:
                    self.restore_fixture()

    def test_missing_or_broken_transition_fails_before_generation(self):
        self.assertTrue(self.transition_paths)
        path = self.root / self.transition_paths[-1]
        for operation in ("missing", "broken predecessor binding"):
            with self.subTest(operation=operation):
                try:
                    if operation == "missing":
                        path.unlink()
                    else:
                        record = json.loads(path.read_text())
                        record["prior_history_sha256"] = "0" * 64
                        path.write_bytes(documentary.canonical_bytes(record))
                    with patch.object(products, "_build_candidate") as build:
                        with self.assertRaises(ValueError):
                            products.build_candidate(self.root / "rejected-history")
                    build.assert_not_called()
                finally:
                    self.restore_fixture()

    def test_generation_mutation_of_any_protected_artifact_is_rejected(self):
        for relative in (*self.product_paths.values(), identity.WORKBOOK):
            with self.subTest(path=relative):
                try:
                    def candidate_body(*args, **kwargs):
                        self.mutate_artifact(relative)
                        return {"fixture": "mutated candidate"}

                    with patch.object(products, "_build_candidate", side_effect=candidate_body) as build:
                        with self.assertRaises((ValueError, RuntimeError)):
                            products.build_candidate(self.root / "mutated-candidate")
                    build.assert_called_once()
                finally:
                    self.restore_fixture()

    def test_transaction_rejects_mutation_during_reasoning(self):
        output = self.root / "mutated-transaction"

        def reason(*args, **kwargs):
            self.mutate_artifact(self.product_paths["integrated"])
            return {"fixture": "reasoning"}

        with patch.object(products, "build_candidate", return_value={"fixture": "candidate"}) as build, \
                patch.object(products, "compare_candidate_builds") as compare, \
                patch.object(products, "reason_products", side_effect=reason) as reasoning:
            with self.assertRaises((ValueError, RuntimeError)):
                products.run_transaction(output, robot_path="unused-fixture-robot")
        self.assertEqual(build.call_count, 2)
        compare.assert_called_once()
        reasoning.assert_called_once()
        self.assertFalse((output / "transaction-summary.json").exists())

    def test_two_authenticated_but_different_states_are_not_preservation(self):
        # Successful authentication of each endpoint is insufficient: even a
        # newly authorized state must not appear during a 2023 generation run.
        before = self.state_hashes()
        after = {**before, "integrated": hashlib.sha256(b"another authenticated state").hexdigest()}
        with patch.object(products, "authenticate_current_sosa_state", side_effect=[before, after]) as auth, \
                patch.object(products, "_build_candidate", return_value={"fixture": "candidate"}) as build:
            with self.assertRaisesRegex(RuntimeError, "changed during generation"):
                products.build_candidate(self.root / "changed-authorized-state")
        self.assertEqual(auth.call_count, 2)
        build.assert_called_once()

    def test_mutation_during_authentication_prevents_generation(self):
        validate = products.validate_current_sosa_products

        def validate_then_mutate():
            result = validate()
            self.mutate_artifact(self.product_paths["alignment_core"])
            return result

        with patch.object(products, "validate_current_sosa_products", side_effect=validate_then_mutate) as auth, \
                patch.object(products, "_build_candidate") as build:
            with self.assertRaisesRegex(RuntimeError, "changed during authentication"):
                products.build_candidate(self.root / "authentication-race")
        auth.assert_called_once()
        build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
