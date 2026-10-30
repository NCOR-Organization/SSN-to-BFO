"""Current policy prose must match authority and preserve its evidence limits.

Eight architecture facets are checked in their current-policy section: separate
evolution kinds, authenticated products, custody versus freshness, applicability,
cross-track preservation, ROBOT reconstruction, asserted-query scope, and scoped
readiness. Historical reports are deliberately outside these checks.
"""
from collections import Counter
import ast
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = "docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md"
EVOLUTION = "docs/CURRENT-SEMANTIC-WORKBOOK-EVOLUTION.md"
RETAINED = "docs/CURRENT-RETAINED-EVIDENCE.md"
SCOPED_STATUS = (
    "Three-term adjudication fully validated within scope; overall current-track "
    "publication readiness remains blocked by independent Class B work."
)


def text(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def prose(value):
    return " ".join(value.replace("`", "").replace("*", "").split())


def section(document, heading):
    matches = list(re.finditer(r"^## " + re.escape(heading) + r"\s*$", document, re.M))
    if len(matches) != 1:
        raise AssertionError("Expected one current policy section: " + heading)
    remaining = document[matches[0].end():]
    return prose(re.split(r"^## ", remaining, maxsplit=1, flags=re.M)[0])


class CurrentDocumentationPolicyTests(unittest.TestCase):
    def test_live_assessment_summary_matches_actual_records(self):
        records = json.loads(text("mappings/current-ssn-sosa-assessment.json"))["records"]
        states = Counter(record["review_state"] for record in records)
        outcomes = Counter(record["assessment_outcome"] for record in records)
        summary = re.findall(
            r"The current assessment is (\d+) final, (\d+) deferred, (\d+) unreviewed, "
            r"(\d+) unresolved, with (\d+) formal mappings, (\d+) no-direct mappings, "
            r"and (\d+) inheritance-sufficient outcomes\.", prose(text(REVIEW)))
        self.assertEqual(len(summary), 1, "Missing or duplicate live assessment summary")
        expected = (states["final"], states["deferred"], states["unreviewed"],
                    len(records) - states["final"], outcomes["formal_mapping_adopted"],
                    outcomes["no_direct_mapping"], outcomes["inheritance_sufficient"])
        self.assertEqual(tuple(map(int, summary[0])), expected)

    def test_current_documents_preserve_scoped_status_and_no_completion_claim(self):
        for relative in (REVIEW, EVOLUTION):
            with self.subTest(document=relative):
                document = prose(text(relative))
                self.assertIn(SCOPED_STATUS, document)
                self.assertNotRegex(document.lower(),
                    r"overall (?:current-track )?publication readiness (?:is |has been )?"
                    r"(?:complete|completed|established|achieved|passed)\b")
        self.assertNotRegex(prose(text(EVOLUTION)).lower(),
                            r"release (?:integration|building|builder) remains unchanged")

    def test_eight_current_architecture_boundaries_remain_explicit(self):
        policy = section(text(EVOLUTION), "Current validation and evidence architecture")
        facets = {
            "separate documentary and semantic evolution": (
                "Documentary evolution remains limited to D-only changes with equal semantic projections.",
                "Semantic evolution authenticates changed A/B/C/E rows"),
            "authenticated transition-aware release products": (
                "release/package reasoning contract is transition-aware",
                "only authenticated current context supplies evolved expectations"),
            "retained custody does not establish freshness": (
                "immutable historical report bytes", "custody, not freshness",
                "an old receipt cannot become current by changing its recorded hashes"),
            "decision applicability": (
                "Decision applicability checks the full intervening history",
                "preserves the original human records"),
            "cross-track preservation": (
                "SOSA-2023 keeps separate source, workbook and product identities",
                "protected current-track files are unchanged throughout their transaction"),
            "ROBOT current reconstruction": (
                "ROBOT reconstruction checks the current governed partition exactly",
                "Missing, extra or mismatched expressions fail"),
            "asserted query scope": (
                "same local asserted execution graphs",
                "does not establish complete imported ontology closure",
                "missing local SKOS dependency"),
            "scoped readiness": (
                "Selection never overrides command freshness, execution custody, semantic status",
                "outstanding whole-repository gate", "independent Class B work remains open"),
        }
        for facet, assertions in facets.items():
            with self.subTest(facet=facet):
                for assertion in assertions:
                    self.assertIn(assertion, policy)
        release = prose(text("docs/VALIDATION-AND-RELEASES.md"))
        self.assertIn("fixed_closure_triple_count counts asserted RDF", release)
        self.assertIn("It does not count inferred output", release)

    def test_portable_custody_keeps_tool_identity_and_historical_failure_boundaries(self):
        policy = section(text(RETAINED), "Portable execution custody")
        for assertion in (
            "reports/retained-evidence/execution/sha256/",
            "producing command", "source inputs", "byte size",
            "present manifest cannot silently fall back to runtime files",
            "original absolute paths remain unchanged in historical receipts",
            "Executable content identity remains required",
            "recorded Java version, configured environment, reasoner JAR and helper source",
            "does not certify a new environment merely because a tool moved",
            "No selector flag can waive custody or promote a failed result",
            "New executions require additive receipts",
        ):
            with self.subTest(assertion=assertion):
                self.assertIn(assertion, policy)

    def test_documented_successor_and_retention_commands_exist_and_match_cli(self):
        cases = (
            (EVOLUTION, "tools/current_checkpoint_successor.py", {
                "prepare": {"--validation", "--authorization", "--reviewer", "--include"},
                "bind": {"--prepared", "--commit"}, "check": set()}),
            (RETAINED, "tools/current_portable_execution_evidence.py", {
                "": {"--report", "--retain"}}),
        )
        for document, script, commands in cases:
            with self.subTest(script=script):
                self.assertTrue((ROOT / script).is_file())
                tree = ast.parse(text(script))
                declarations = {kind: set() for kind in ("add_argument", "add_parser")}
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                        if node.func.attr in declarations:
                            declarations[node.func.attr].update(
                                arg.value for arg in node.args
                                if isinstance(arg, ast.Constant) and isinstance(arg.value, str))
                for command, required_flags in commands.items():
                    prefix = "python -B " + script + (" " + command if command else "")
                    lines = [line.strip() for line in text(document).splitlines()
                             if line.strip() == prefix or line.strip().startswith(prefix + " ")]
                    self.assertEqual(len(lines), 1, prefix)
                    flags = set(re.findall(r"--[a-z][a-z-]*", lines[0]))
                    self.assertEqual(flags, required_flags)
                    self.assertLessEqual(flags, declarations["add_argument"])
                    if command:
                        self.assertIn(command, declarations["add_parser"])


if __name__ == "__main__":
    unittest.main()
