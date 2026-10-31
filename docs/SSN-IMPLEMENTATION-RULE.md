# SSN implementation mapping rule

The maintained [SPARQL CONSTRUCT rule](../rules/ssn-implementation-mapping.rq) implements the established process-mediated interpretation of `ssn:implementedBy` and `ssn:implements` for the current SSN/SOSA track. It runs separately from the OWL ontology products.

## Behavior and input assumptions

The exact pinned predicates are:

| Purpose | IRI |
|---|---|
| prescribes premise | `https://www.commoncoreontologies.org/ont00001942` |
| has_agent premise | `https://www.commoncoreontologies.org/ont00001833` |
| forward output | `http://www.w3.org/ns/ssn/implementedBy` |
| inverse output | `http://www.w3.org/ns/ssn/implements` |

The query joins a Procedure's `prescribes` edge to an execution's `has_agent` edge on the **same execution**. It constructs the Procedure-to-System `implementedBy` assertion and the System-to-Procedure `implements` assertion. Both directions follow the unchanged source inverse axiom in `imports/ssn.ttl`.

Both exact premise triples must be present in the input graph. They may be asserted or supplied by an earlier reasoning/materialization step. The query itself performs no automatic RDFS, OWL, subproperty, or inverse-property entailment. An inverse edge or a narrower predicate alone will not match until the exact premise is materialized.

This is one-way inference from the two premises. An existing implementation assertion does not cause the rule to invent an execution or decompose the assertion into premises. The rule does not construct a direct CCO prescription relationship between the Procedure and System. It neither introduces an OWL property-chain axiom nor embeds SWRL in the ontology.

## Execute and test

From the repository root, using the existing ROBOT installation:

```sh
robot query --input tests/fixtures/current-semantic/implementation-rule.ttl --query rules/ssn-implementation-mapping.rq /tmp/ssn-implementation-derived.ttl
```

This tested command writes only the constructed facts: **four triples** for the fixture's two matching Procedure/System pairs. It does not copy the input graph into the output. To retain the original facts, form an RDF graph union of the input and derived graph in a separate application/ABox dataset, then validate that dataset with the intended pinned ontology closure. This execution does not modify the maintained ontology products.

With the repository's configured Python environment and existing dependencies:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_ssn_implementation_rule.py' -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_implementation_rule_coverage.py' -v
```

The behavior tests execute the actual query. They cover the historical positive example, both inverse outputs, missing/mismatched/reversed premises, absence of implicit inference, absence of direct prescription output, lack of reverse decomposition, and idempotence. The coverage tests check the coordinated workbook rows and separate external-rule coverage, including rejection of artifact or row drift.

## Authority and workbook representation

The interpretation and typing representative come from these committed implementations:

- `b464cea20bae6d6c542ec1db459cc76b6b978beb`: process-mediated implementedBy inference.
- `091de44f6d61cc0d3f48e15e653d263a8dc8fbcb`: historical implementation-chain example.
- `8512004a3b911ac5711fb0cc8dfe70cb086e3b9b`: retained `implements` domain `ssn:System`.

The [explicit human instruction of 2026-10-30](../reports/current-semantic-workbook/implementation-rule-2026-10-30/authorized-instructions.txt) authorizes this external execution mechanism because the historical OWL chain fails the current global restrictions. [Bound authority evidence](../reports/current-semantic-workbook/implementation-rule-2026-10-30/authorities.json) records that implementation authorization. It does not create a new scientific adjudication or finalize the assessment records.

The authoritative `mappings/SSN2BFO-COMS.xlsx` representation preserves both RowIDs:

| Row | RowID | OWL predicate and target |
|---|---|---|
| Sheet2!57, `ssn:implementedBy` | `urn:uuid:4afaf231-5478-4a50-9a12-0cbf59d78d7e` | B/C deliberately blank; reasoning references the external rule |
| Sheet2!58, `ssn:implements` | `urn:uuid:6142726b-21b1-4dba-b5ec-a7d6dca4afab` | `rdfs:domain` / `ssn:System`; reasoning references the external rule |

The superseding direct inclusions into CCO `prescribes` and `prescribed_by` are removed. The [source-term coverage report](../reports/coms-source-term-coverage.md) records these two terms as **covered by external rule**, separately from direct OWL mapping and typing. The blank implementedBy OWL cells therefore do not mean that its mapping treatment is absent. The implements domain remains a typing representative, not a substitute for the executable rule.

## Focused validation evidence

The [seven original OWL 2 DL violations](../reports/current-semantic-workbook/implementation-rule-2026-10-30/owl2dl-violations.md) are documented individually with full IRIs, source locations, exact validator diagnostics, and a reproducible command. They comprise three simplicity failures and four implicated chain axioms across three regularity cycles; the profile failure does not demonstrate logical inconsistency.

The [external-rule ontology candidate](../reports/current-semantic-workbook/implementation-rule-2026-10-30/external-rule/validation-result.json) and [representative ABox after rule execution](../reports/current-semantic-workbook/implementation-rule-2026-10-30/after-rule/validation-result.json) pass the current local OWL 2 DL profile and HermiT gates with zero named unsatisfiable classes. All [13 before-rule](../reports/current-semantic-workbook/implementation-rule-2026-10-30/before-rule/entailment-result.json) and [15 after-rule](../reports/current-semantic-workbook/implementation-rule-2026-10-30/after-rule/entailment-result.json) HermiT entailment/non-entailment expectations pass. These are bounded mapping and ABox results, not a broader publication-readiness claim.
