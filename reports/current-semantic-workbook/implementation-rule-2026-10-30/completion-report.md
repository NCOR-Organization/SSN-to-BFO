# Implementation mapping completion — 2026-10-30

**IMPLEMENTATION MAPPING COMPLETE — OWL 2 DL VALIDATED**

The explicitly authorized external SPARQL implementation is installed. The historical process-mediated interpretation is preserved without asserting its incompatible OWL property-chain axiom. No new scientific adjudication or assessment finalization was created. The exact human instruction, historical committed evidence, executable rule, and successful candidate validation are bound by the existing [semantic transition](../../../reports/current-semantic-workbook/transitions/035e5877-1b9d-444c-a970-239ce3bcb97c.json).

## Exact authoritative changes

Only six workbook cells changed: Sheet2!B57/C57/D57 and B58/C58/D58. Both subjects and RowIDs are unchanged; all other values and styles are preserved.

| Term / row | Unchanged RowID | Current OWL row |
|---|---|---|
| `ssn:implementedBy`, Sheet2!57 | `urn:uuid:4afaf231-5478-4a50-9a12-0cbf59d78d7e` | B/C deliberately blank; D references `rules/ssn-implementation-mapping.rq` |
| `ssn:implements`, Sheet2!58 | `urn:uuid:6142726b-21b1-4dba-b5ec-a7d6dca4afab` | `rdfs:domain` / `ssn:System`; D references the same rule |

The exact logical delta, also verified independently by RDF graph isomorphism, is:

```text
- SubObjectPropertyOf(<http://www.w3.org/ns/ssn/implementedBy> <https://www.commoncoreontologies.org/ont00001942>)
- SubObjectPropertyOf(<http://www.w3.org/ns/ssn/implements> <https://www.commoncoreontologies.org/ont00001920>)
+ ObjectPropertyDomain(<http://www.w3.org/ns/ssn/implements> <http://www.w3.org/ns/ssn/System>)
```

The integrated product contains all three changes. The CCO extension loses only the two subproperty inclusions. The alignment core gains only the domain axiom. The strict-BFO product remains byte-identical. No unrelated OWL axioms changed; no implementation chain or SWRL axiom was added.

Only the two corresponding assessment records' `rationale`, `notes`, `review`, and `evidence` fields changed. All states/outcomes and other 89 records remain identical. Counts remain **20 final, 71 unreviewed, zero deferred**: **13 formal_mapping_adopted, five no_direct_mapping, two inheritance_sufficient**. These unchanged administrative states do not erase the recorded implementation authorization.

## Maintained rule and execution

Rule: [`rules/ssn-implementation-mapping.rq`](../../../rules/ssn-implementation-mapping.rq). [Usage and assumptions](../../../docs/SSN-IMPLEMENTATION-RULE.md) describe its exact numeric vocabulary IRIs and separately executed status.

```sparql
PREFIX ssn: <http://www.w3.org/ns/ssn/>
PREFIX cco: <https://www.commoncoreontologies.org/>
CONSTRUCT {
  ?procedure ssn:implementedBy ?system .
  ?system ssn:implements ?procedure .
}
WHERE {
  ?procedure cco:ont00001942 ?execution .
  ?execution cco:ont00001833 ?system .
}
```

From the repository root:

```sh
robot query --input tests/fixtures/current-semantic/implementation-rule.ttl --query rules/ssn-implementation-mapping.rq /tmp/ssn-implementation-derived.ttl
```

The tested ROBOT command and RDFLib execution produce the same four fixture triples. The output contains derived assertions only. Exact premise triples must be asserted or previously materialized. The query performs no implicit OWL/RDFS reasoning and creates no execution witnesses. Both directions are emitted under the unchanged source inverse relationship. An implementation edge alone is not decomposed into prescription/agent premises. These terms are reported as covered by external rule, separately from OWL mappings and domain typing.

## Seven historical-chain violations

The fresh exact historical candidate fails the profile gate with seven diagnostics. [The complete axiom-level dossier](owl2dl-violations.md) gives every full IRI, source line, workbook RowID, original diagnostic, and reproduction command; [unaltered output](historical-chain/profile-output.txt) is retained.

| No. | Offending axiom | Actual failure |
|---|---|---|
| 1 | `Sampler subClassOf implements min 1 owl:Thing` | Non-simple `implements` in minimum cardinality |
| 2 | `Actuator subClassOf implements min 1 owl:Thing` | Same simplicity violation, distinct source restriction |
| 3 | `Sensor subClassOf implements min 1 owl:Thing` | Same simplicity violation, distinct source restriction |
| 4 | `madeBySensor o implements subPropertyOf usedProcedure` | `implements` participates in prohibited regularity dependency cycle |
| 5 | `prescribes o has_agent subPropertyOf implementedBy` | `prescribes` participates in the shared prohibited cycle |
| 6 | `madeByActuator o implements subPropertyOf usedProcedure` | Actuator instance of the cycle |
| 7 | `madeBySampler o implements subPropertyOf usedProcedure` | Sampler instance of the cycle |

The historical chain makes `implementedBy` composite and its source inverse `implements` non-simple, conflicting with all three unchanged minimum-cardinality axioms. Inverse normalization of the historical chain requires `prescribed_by < implements`; each source chain requires `implements < usedProcedure`; the retained `usedProcedure subPropertyOf prescribed_by` closes the prohibited dependency. There are three concrete cycles and four implicated chain axioms, not four independent cycles. These are [OWL 2 Structural Specification §11.1](https://www.w3.org/TR/owl2-syntax/#Property_Hierarchy_and_Simple_Object_Property_Expressions) / [§11.2](https://www.w3.org/TR/owl2-syntax/#The_Restrictions_on_the_Axiom_Closure) failures. HermiT was gated off for that candidate; these diagnostics are **not** an inconsistency or unsatisfiability result.

## Focused validation

| Current product | Direct governed axioms | RDF triples | Pinned local closure triples | OWL 2 DL | HermiT / named unsatisfiable |
|---|---:|---:|---:|---|---|
| `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl` | 30 | 62 | 1215 | PASS | PASS / 0 |
| `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl` | 51 | 883 | 15871 | PASS | PASS / 0 |
| `SSN2BFO.ttl` | 100 | 1065 | 15855 | PASS | PASS / 0 |
| `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl` | 19 | 134 | 14989 | PASS | PASS / 0 |

The [existing generation gate](generation.log) and [freshness/determinism gate](generation-freshness.log) pass. Their PASS result requires profile success, retained pinned sample declarations, successful HermiT output, and zero unsatisfiable named classes. The [retained generated validation report](generated-products-validation.md) and [summary](generation-validation-summary.json) record all product checks. The integrated graph is isomorphic to the independently validated complete-closure candidate. Existing declaration-only profile completion is retained; no source logical restriction was removed or weakened.

The [20 focused unit tests](focused-tests.log) pass: seven rule behavior tests, eight coverage tests, and five existing coverage/domain/range regression tests. All [13 before-rule](before-rule/entailment-result.json) and [15 after-rule](after-rule/entailment-result.json) HermiT queries pass. The positive implementation assertions are not entailed before execution and are entailed afterward; both removed direct inclusions and the direct Procedure-to-System prescription assertions remain non-entailed. The restored sensor-agent inclusions remain entailed. Observation, Sensor, Stimulus, Procedure, and System remain satisfiable. Both expected endpoint types follow after execution.

The representative ABox with constructed assertions separately passes [profile and HermiT validation](after-rule/validation-result.json) with zero named unsatisfiable classes. Negative tests check absence of unwanted rule outputs/non-entailment, not closed-world falsity. Idempotence and matching the same execution are tested explicitly.

[Semantic-transition authentication](semantic-transition-check.log) and [final assessment authentication/report freshness](assessment-authentication.log) pass. An initial assessment freshness check detected three JSON reports still bound to pre-generation product bytes; the existing assessment command refreshed them after generation. The [initial freshness diagnostic](assessment-freshness-before-postgeneration-refresh.log) and [successful refresh](assessment-postgeneration-write.log) are retained. No infrastructure repair was needed.

## Counts and preservation

Final workbook: **107 governed rows, 100 active OWL assertions, seven blank OWL rows**, with all 107 existing RowIDs preserved. Two properties additionally receive the new external-rule coverage. The seven blank OWL rows are not all absence-of-mapping decisions.

[Independent final verification](verification.json) confirms that the other 1864 of 1882 starting files remain byte-identical. All unrelated workbook values and assessment records are unchanged, including the sensor restoration and observedProperty deferral, three sampling-relationship decisions, phenomenonTime mapping and potential counterexample, restored Property equivalence, and finalized forProperty/SystemProperty/MeasurementRange treatments. All 6 tracked/retained import paths and 87 SOSA-next/SOSA-2023 paths present in the starting manifest remain byte-identical.

Only the small external-rule coverage integration was added to the existing generator, assessment coverage, and unmapped-term query. It recognizes the coordinated exact RowIDs, row shapes, workbook references, and pinned rule bytes. It does not generate an OWL axiom or reclassify historical workbook snapshots.

No remaining blocker exists for this requested implementation. This is not a publication-readiness declaration. No source restrictions, unrelated decisions, or separate-track products changed. No staging, commit, tag, push, full publication validation, or evidence migration was performed. HEAD remains `fe06c78b7290fd586b05c42145a57f32d84a8674`; the pre-existing dirty worktree was preserved. [Final Git status](git-status.txt).

## SHA-256 identities

Workbook: `f5a34921289677a6c846f6f25d9645ea8d48220220704bfa44429adffc4f9c59`.

Rule: `c1d3ea7afd47369782f81e38f0ad21272bf419a5d89defc176c7e82e09f3f2dd`.

| Product | SHA-256 |
|---|---|
| `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl` | `d346e19bdb7c82b649411650b606eb41b72c397b892eeb274628f21d758b06ef` |
| `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl` | `019c1ec14ba31c48d415d1ec9f0207b16a79e2117e536cefa0ab82a1c383a3f5` |
| `SSN2BFO.ttl` | `0905533ef416b72366c588820173a2be56d299679f08387cad6650f410f1b810` |
| `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl` | `676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af` |

IMPLEMENTATION MAPPING COMPLETE — OWL 2 DL VALIDATED
