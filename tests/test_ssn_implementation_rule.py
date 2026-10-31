"""Execute the maintained external rule; these tests do not simulate OWL DL."""
from pathlib import Path
import unittest

from rdflib import Graph, Namespace


ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "rules/ssn-implementation-mapping.rq"
FIXTURE = ROOT / "tests/fixtures/current-semantic/implementation-rule.ttl"
CCO = Namespace("https://www.commoncoreontologies.org/")
SSN = Namespace("http://www.w3.org/ns/ssn/")
EX = Namespace("https://example.org/property-chain-mapping-fixture/")
PREFIXES = """
@prefix cco: <https://www.commoncoreontologies.org/> .
@prefix ssn: <http://www.w3.org/ns/ssn/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <https://example.org/property-chain-mapping-fixture/> .
"""


class ImplementationRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.query = RULE.read_text(encoding="utf-8")

    def apply(self, graph):
        result = graph.query(self.query)
        self.assertEqual(result.type, "CONSTRUCT")
        return result.graph

    def graph(self, body):
        return Graph().parse(data=PREFIXES + body, format="turtle")

    def test_historical_positive_component_and_inverse_direction(self):
        graph = self.graph("""
            ex:procedure cco:ont00001942 ex:implemented-by-step .
            ex:implemented-by-step cco:ont00001833 ex:implementing-system .
        """)
        self.assertEqual(set(self.apply(graph)), {
            (EX.procedure, SSN.implementedBy, EX["implementing-system"]),
            (EX["implementing-system"], SSN.implements, EX.procedure),
        })

    def test_fixture_produces_exactly_two_pairs_and_no_cross_join(self):
        graph = Graph().parse(FIXTURE, format="turtle")
        pairs = ((EX.procedure, EX["implementing-system"]),
                 (EX["second-procedure"], EX["second-system"]))
        expected = {(procedure, SSN.implementedBy, system)
                    for procedure, system in pairs}
        expected.update((system, SSN.implements, procedure)
                        for procedure, system in pairs)
        self.assertEqual(set(self.apply(graph)), expected)

    def test_missing_mismatched_and_reversed_premises_do_not_match(self):
        cases = {
            "missing_has_agent": "ex:p cco:ont00001942 ex:e .",
            "missing_prescribes": "ex:e cco:ont00001833 ex:s .",
            "mismatched_execution": "ex:p cco:ont00001942 ex:e1 . ex:e2 cco:ont00001833 ex:s .",
            "reversed_prescribes": "ex:e cco:ont00001942 ex:p . ex:e cco:ont00001833 ex:s .",
            "reversed_has_agent": "ex:p cco:ont00001942 ex:e . ex:s cco:ont00001833 ex:e .",
        }
        for name, body in cases.items():
            with self.subTest(name=name):
                self.assertEqual(len(self.apply(self.graph(body))), 0)

    def test_no_implicit_subproperty_or_inverse_materialization(self):
        cases = {
            "subproperty": """
                ex:narrow rdfs:subPropertyOf cco:ont00001942 .
                ex:p ex:narrow ex:e . ex:e cco:ont00001833 ex:s .
            """,
            "inverse": """
                ex:e cco:ont00001920 ex:p . ex:s cco:ont00001787 ex:e .
            """,
        }
        for name, body in cases.items():
            with self.subTest(name=name):
                graph = self.graph(body)
                self.assertEqual(len(self.apply(graph)), 0)
                # Simulate premises supplied by a separate prior reasoner.
                graph.add((EX.p, CCO.ont00001942, EX.e))
                graph.add((EX.e, CCO.ont00001833, EX.s))
                self.assertEqual(set(self.apply(graph)), {
                    (EX.p, SSN.implementedBy, EX.s),
                    (EX.s, SSN.implements, EX.p),
                })

    def test_repeated_execution_is_idempotent(self):
        graph = Graph().parse(FIXTURE, format="turtle")
        first = self.apply(graph)
        graph += first
        after_first = set(graph)
        second = self.apply(graph)
        self.assertEqual(set(second), set(first))
        graph += second
        self.assertEqual(set(graph), after_first)

    def test_no_direct_prescription_is_constructed(self):
        output = self.apply(Graph().parse(FIXTURE, format="turtle"))
        self.assertEqual(set(output.predicates()), {SSN.implementedBy, SSN.implements})
        for procedure, system in ((EX.procedure, EX["implementing-system"]),
                                  (EX["second-procedure"], EX["second-system"])):
            self.assertNotIn((procedure, CCO.ont00001942, system), output)
            self.assertNotIn((system, CCO.ont00001920, procedure), output)

    def test_existing_implementation_does_not_decompose_into_premises(self):
        graph = self.graph("ex:p ssn:implementedBy ex:s . ex:s ssn:implements ex:p .")
        self.assertEqual(len(self.apply(graph)), 0)


if __name__ == "__main__":
    unittest.main()
