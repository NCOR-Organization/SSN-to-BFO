"""The ordinary local/CI gate retains all suites and the current contract."""

import argparse
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_validation_suite as validation
import workflow_check


# Existing canonical selectors are an independent regression anchor. The
# current wildcard intentionally includes newly added current-policy modules.
PREVIOUS_SELECTORS = (
    "test_current*.py", "test_coms_row_identity.py",
    "test_coms_framework_integration.py", "test_sosa_source_version.py",
    "test_product_role_policy.py", "test_sosa_release_scope.py",
    "test_check_sosa_next_mapping.py", "test_sosa_next_products.py",
    "test_sosa_next_consumer_stack.py", "test_sosa_2023_publication_metadata.py",
    "test_sosa_2023_release_rendering.py", "test_sosa_2023_release_manifest.py",
    "tests.test_sosa_2023_release_runtime", "tests.test_sosa_2023_build_release",
    "tests.test_sosa_2023_release_archive", "tests.test_sosa_2023_release_rehearsal",
    "test_product_dispositions.py", "test_modular_products.py",
    "test_strict_bfo_mapping.py", "test_cco_extension.py", "test_bfo_projection.py",
    "test_publication_metadata.py", "test_release_context.py",
    "test_release_rendering.py", "test_release_manifest.py", "test_build_release.py",
    "test_release_archive.py", "test_release_rehearsal.py",
    "test_placeholder_catalog_migration.py", "test_generate_mapping_from_coms.py",
    "tests.test_robot_template_generation_pilot",
    "tests.test_robot_property_chain_generation_pilot", "tests.test_robot_diff_pilot",
    "tests.test_robot_extract_pilot", "tests.test_robot_query_equivalence_pilot",
    "tests.test_robot_retained_example_validation_pilot", "tests.test_robot_verify_pilot",
    "tests.test_robot_reconstruction_validation",
)


class CanonicalValidationSelectionTests(unittest.TestCase):
    def capture(self, *, fail_contract=False):
        commands = []

        def record(name, command, **kwargs):
            commands.append(command)
            passed = not (fail_contract and "test_release_contract.py" in command)
            return validation.StepResult(name, passed)

        with mock.patch.object(validation, "run_command", side_effect=record), \
                mock.patch.object(validation, "parse_ttl_check",
                                  return_value=validation.StepResult("parse", True)), \
                mock.patch.object(validation, "compile_check",
                                  return_value=validation.StepResult("compile", True)), \
                mock.patch.object(validation, "print_summary", return_value=0):
            validation.run_validation_suite(argparse.Namespace(
                write_reports=False, tmp_dir="/tmp/selection-only-no-execution"))
        return commands

    def test_contract_is_selected_once_without_dropping_existing_suites(self):
        selectors = []
        for command in self.capture():
            if "unittest" not in command:
                continue
            if "discover" in command:
                selectors.append(command[command.index("-p") + 1])
            else:
                selectors.extend(command[command.index("unittest") + 1:])
        self.assertEqual(selectors.count("test_release_contract.py"), 1)
        self.assertEqual(tuple(x for x in selectors if x != "test_release_contract.py"),
                         PREVIOUS_SELECTORS)

    def test_contract_failure_stops_later_canonical_steps(self):
        commands = self.capture(fail_contract=True)
        self.assertEqual(commands[-1][-1], "test_release_contract.py")
        self.assertFalse(any("test_build_release.py" in command for command in commands))

    def test_compile_and_release_package_entry_points_include_contract(self):
        commands = []
        with mock.patch.object(validation, "run_command", side_effect=lambda name, command:
                               commands.append(command) or validation.StepResult(name, True)):
            validation.compile_check()
        self.assertIn("tests/test_release_contract.py", commands[0])
        self.assertIn("tests/test_release_contract.py", workflow_check.COMPILE_COMMAND)
        makefile = (ROOT / "Makefile").read_text()
        compile_recipe = makefile.split("\ncompile:\n", 1)[1].split("\n\n", 1)[0]
        package_recipe = makefile.split("\ncheck-release-package:\n", 1)[1].split("\n\n", 1)[0]
        self.assertIn("tests/test_release_contract.py", compile_recipe)
        self.assertIn("-p 'test_release_contract.py'", package_recipe)

    def test_active_ci_uses_the_same_canonical_local_entry_point(self):
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn("\ncheck: validate compile\n", makefile)
        validate_recipe = makefile.split("\nvalidate:\n", 1)[1].split("\n\n", 1)[0]
        self.assertIn("python tools/run_validation_suite.py", validate_recipe)
        workflow = (ROOT / ".github/workflows/test-mappings.yml").read_text()
        self.assertIn("run: make check", workflow)


if __name__ == "__main__":
    unittest.main()
