# Current SSN/SOSA publication-readiness candidate

**CURRENT TRACK NOT YET PUBLICATION READY — HUMAN SEMANTIC REVIEW REQUIRED**

Branch: `publication/current-sosa-readiness`. Baseline and execution HEAD: `dc314460fe3e875ba1c8ccfcb3c6840a7181e733`. This is an uncommitted candidate, not a tag, release, or upstream identity. Code, inputs, commands, and output hashes are retained in the linked evidence. This evidence migration changes no mapping decisions; existing authorized changes retain their transition provenance.

## Identity and baseline

The original publication baseline recorded a clean Git status: `## publication/current-sosa-readiness`. [Baseline fingerprint](../../../current-publication-baseline.json) records every then-tracked file, workbook/status counts, planned change classes, and the external COMS checkout. The original baseline remains historical; current authorized changes are authenticated by the preserved transition chain.

Current source files preserve the 2017 SSN/SOSA generation annotations and have no version IRIs. **Upstream immutable commit: not established from repository evidence.** Local Git provenance and all ontology header/provenance annotations are in [the identity record](../../../../config/current-ssn-sosa-identity.json).

CCO is the merged Version 2.0 artifact, version IRI `https://www.commoncoreontologies.org/2024-11-06/CommonCoreOntologiesMerged`. BFO is embedded in those same bytes; the header identifies `bfo/2020/bfo-core.ttl`, obtained 11/03/2024. No standalone BFO file or immutable upstream commit is inferred. The sampling source imports SKOS without a local pinned SKOS artifact; available-local identity is frozen, but full upstream import closure identity is not established.

| Role | Path | Bytes | SHA-256 |
|---|---|---:|---|
| source | `imports/sosa.ttl` | 34854 | `0dad03b30c7fdd085e2629dfc0ebd10bb1dacbda73b2c375fb295ab6861ffb33` |
| source | `imports/sosa-sampling.ttl` | 3604 | `f6e1d9451732bb132fa4ba567ca58fba752dcfbb43e66c5d4b660963bd0f7c1a` |
| source | `imports/ssn.ttl` | 38450 | `434b50fecb32e14b30aac28310a76935a33fdc397e70fce887fd653069a59383` |
| source | `imports/ssn-systems.ttl` | 41076 | `156870689643840c861aaead206458bcdfc9cded5f7107598dbf87e015861105` |
| target CCO + BFO | `imports/cco.ttl` | 1229197 | `3ad8f098ecb3d7ca27464a1edf2795b90c69573843447d51f090e6f1b30694f4` |
| historical workbook identity | `mappings/SSN2BFO-COMS.xlsx` | 12372 | `e32c6b5691bf4aa00b4ec564731e0364edc2567658bb21c46f83c1e3f0d9a4f6` |
| current authoritative workbook | `mappings/SSN2BFO-COMS.xlsx` | 21434 | `778a567168143160c152110e79a32a86eea318710dbde078fa0525482bbccb4c` |
| current product | `SSN2BFO.ttl` | 170023 | `98cdfd366963175bc71a84431634f632e5cd5b93815c1b511369b4976d8a898c` |
| current product | `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl` | 7623 | `17695ef17379924449153b2c92ffaed6b57d497a1b2d1e854f584614cebec770` |
| current product | `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl` | 19183 | `676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af` |
| current product | `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl` | 145888 | `5c95807b4a2299c06647320a532afe0beff553b0dd0e46a95c38af67db9d5d28` |

Documentary workbook evolution: **VALIDATED**. Current A/B/C/E semantic projection SHA-256: `566d6a6ba6200458eab5ea7561c86d0eb2483765fa5a1a7c2e8ff0526654eb44`. The frozen identity record retains the historical full-workbook hash; any later workbook bytes require the explicit, snapshot-backed [documentary transition chain](../../../current-documentary-workbook/updates). A validated documentary transition preserves semantic cells and decision custody without approving a new semantic decision.

## Inventory and assessment outcomes

Source inventory: **91** ({'class': 44, 'object_property': 47}); assessment records: **91**; equality: **PASS**. The unchanged scope excludes datatype properties and `owl:deprecated true` terms. The inventory is recomputed from local source declarations and independently reconciled to the existing SPARQL query.

Review states: `{'deferred': 0, 'final': 17, 'unreviewed': 74}`. Assessment outcomes: `{'deferred': 0, 'formal_mapping_adopted': 10, 'inheritance_sufficient': 2, 'no_direct_mapping': 5, 'unreviewed': 74}`. Unresolved = deferred + unreviewed. Final documentary reconstruction does not imply a new approval of a changed axiom.

See [assessment inventory](../../../../mappings/current-ssn-sosa-assessment.json) and [coverage evidence](../../../current-assessment/v2/current-ssn-sosa-coverage.md). Workbook rows are not the unit of assessment.

## Formal coverage

| Evidence category | Source terms |
|---|---:|
| direct_formal_mapping | 67 |
| inherited_formal_mapping | 41 |
| rule_or_chain_route | 9 |
| typing_only_in_workbook | 17 |
| explicit_blank | 5 |
| no_established_formal_route | 16 |

Structural evidence over named source subclass/subproperty, named equivalence, and inverse paths plus governed direct mappings; chain heads and separately executed conditional query routes. Overlaps retained. No established route means none in this bounded method, not a complete OWL non-entailment proof. Domain/range alone never supplies relation coverage.

Direct formal class/property mappings: 42 classes + 25 properties. Chain heads: 2. The prior 28 relation-mapped properties include the 25 subproperty subjects and three chain heads. Typing-only describes workbook artifacts, not semantic assessment outcomes. Overlapping inherited and conditional routes are not added to direct counts; no-established-route is bounded by the documented structural method.

## Mapping repertoire and rationales

Workbook: 105 rows; 100 assertion-bearing, 5 explicit blanks. Predicates: `{'explicit_blank': 5, 'owl:equivalentClass': 10, 'owl:equivalentProperty': 0, 'owl:propertyChainAxiom': 2, 'rdfs:domain': 16, 'rdfs:range': 15, 'rdfs:subClassOf': 32, 'rdfs:subPropertyOf': 25}`. `owl:equivalentProperty`: 0.

Complex expression occurrences: `{'intersection': 88, 'named': 192, 'some': 97, 'union': 15}`; rows containing each form: `{'intersection': 36, 'named': 73, 'some': 36, 'union': 14}`. Occurrences can overlap within one row.

Rationale coverage: `{'existing_workbook_rationale_rows': 105, 'existing_workbook_rationale_terms': 91, 'safe_documentary_proposals': 90, 'human_review_required_proposals': 1, 'semantic_review_terms': 74}`. See [proposals](../../../current-assessment/v2/current-ssn-sosa-rationale-proposals.md). Current workbook reasoning is documentary evidence. Recorded column-D completion does not approve a mapping or resolve a deferred or unreviewed semantic question; the proposals report describes the current text and remaining concerns.

The [human review queue](../../../current-assessment/v2/current-ssn-sosa-human-review.md) contains **74 source terms**, prioritized by blanks, typing-only cases, equivalences, complex/existential commitments, chains, and cross-track disagreements. Each item separates source/target facts, logical consequences, interpretation, alternatives, and the required human decision. [Review protocol](../../../../docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md).

## Approximate deductive difference

The implementation asks HermiT for all named class and object-property subsumptions/equivalences in each independent baseline and aligned ontology, then restricts the aligned relations to the original signature and compares entailment sets symmetrically. Self-relations and built-ins are excluded. This is the requested PROV-style approximation, not full model-theoretic conservativity or a claim to have independently reproduced the paper's implementation. No logical axiom is removed. Unexpected additions or losses fail the gate; no automatic waiver exists.

| Signature | Status | Added | Lost |
|---|---|---:|---:|
| source | BLOCKED | unavailable | unavailable |
| target | BLOCKED | unavailable | unavailable |

Target-only HermiT 1.4.1.432 reasoning is consistent and OWL 2 DL compliant: 9,383 named hierarchy/equivalence relations over 1,422 classes and 265 object properties. Source/aligned available-local diagnostic consistency is true, but exact results fail because SKOS is unavailable and profile declarations are incomplete. The source logical signature has 48 named classes (including borrowed names) and 47 object properties; this differs intentionally from the scoped 44-class assessment inventory.

Affected-term entailment differences and deliberate-commitment conclusions cannot be asserted when baseline/aligned reasoning is blocked. Complete reasoner/profile diagnostics, exact terms in profile violations, and synthetic violation tests are retained in [semantic validation](../../readiness-reconciliation-20261029/semantic.md) and its JSON/raw evidence.

## Exact-closure examples and selected expectations

Source corpus: **11 files**, each evaluated in a source-only and aligned phase; the synthetic Sample Relationship fixture is reported separately. Classifications: `{'technical/tool failure': 11}`. All file hashes, closure inputs, commands, individual outputs, and technical failure reasons are preserved in [the result JSON](../../readiness-reconciliation-20261029/semantic.json). No equivalence to the PROV paper's 312-instance corpus is claimed.

Selected expectations: 0 approved; 16 proposed (8 positive, 8 negative). Evidence roles: 14 independent proposals and 2 mapping-axiom regressions. The [manifest](../../../../config/current-semantic-expectations.json) distinguishes mapping-induced consequences from source semantics. Unapproved proposals and axiom restatements do not count as independent publication evidence. These tests do not establish global interpretability.

## Identity-report repair

The current generator now checks canonical identity for assertion rows separately from legitimate explicit blanks. Zero-axiom rows require valid row identity and an assessment disposition; completed semantic review is reported separately. Missing/unexplained assertions still fail. The generated report is bound to the assessment hash. Regression tests cover reviewed blanks, unresolved blanks, missing dispositions, malformed assertions, and unchanged SOSA-2023 behavior.

## Executed validation and environment

Every accepted command must independently bind its HEAD, expected HEAD, exact pre/post inputs, executable identity, completion, drift state, and retained output hashes. A current ledger cannot make an older command current. Historical commands remain recorded with their original failures and incomplete bindings; no dependency was installed or changed. The declared full repository gate is `make check`. See [command ledger](../commands.json).

| Executed check | Exit | Log |
|---|---:|---|
| unit_tests | 0 | [unit_tests.log](../unit_tests.log) |
| assessment | 0 | [assessment.log](../assessment.log) |
| source_identity | 0 | [source_identity.log](../source_identity.log) |
| generation_freshness | 0 | [generation_freshness.log](../generation_freshness.log) |
| sosa_source_version | 0 | [sosa_source_version.log](../sosa_source_version.log) |
| sosa_products | 0 | [sosa_products.log](../sosa_products.log) |
| static_checks | 0 | [static_checks.log](../static_checks.log) |
| full_repository_gate | 0 | [full_repository_gate.log](../full_repository_gate.log) |

The [documentary reasoning-completion ledger](../../../current-documentary-workbook/reasoning-completion/validation-ledger.json) records the separately executed, bounded completion checks (SHA-256 `b85ac10bacc431282c52af9a0d135e61066822eac9e76885b9783bd6a84541c0`). It is not a full repository gate or semantic authority and does not refresh historical semantic execution evidence.

Environment: `{'declared': {'VALIDATION_JAVA_DISTRIBUTION': 'temurin', 'VALIDATION_JAVA_VERSION': '22', 'VALIDATION_PYTHON_VERSION': '3.12', 'VALIDATION_ROBOT_JAVA_HEAP': '4G', 'VALIDATION_ROBOT_SHA256': '91890c2e83d0f092dd08731376f154b36610544cfbe8685337a1bf7244ccaa2d', 'VALIDATION_ROBOT_URL': 'https://github.com/ontodev/robot/releases/download/v1.9.7/robot.jar', 'VALIDATION_ROBOT_VERSION': '1.9.7'}, 'declared_environment_match': False, 'measured': {'java_distribution': 'unconfirmed', 'java_major': '22', 'python_major_minor': '3.12'}, 'note': 'Actual Python and Java version output is retained; mismatch remains an independent readiness requirement.'}`. Declared environment match: `False`.

Stored historical normalized HermiT, ELK, and RDFS smoke reports remain historical evidence for their stated inputs. Newly executed normalized checks retain that narrower interpretation. The exact-closure hierarchy comparisons and source examples are attempted but cannot be reported as successful when import/profile checks block them. Unapproved semantic expectations are not run or counted as approved evidence.

## Preservation and documentation

Preservation: **PASS**. [SHA-256 proof](../../../current-publication-preservation.json) covers preserved workbook semantic cells through any validated documentary chain, byte-identical current products/rule and source/target artifacts, SOSA-2023 source/configuration/products/workbooks, historical authorities, local COMS adapters/identity architecture, and all 55 external COMS tracked files. SOSA-2023 BFO/CCO status totals remain 119 rows: 55 active, 64 no-direct; RO remains 82 rows: 16 active, 66 no-direct. Neither track has a new semantic decision.

Documentation fixes identify three current modular products, the maintained independent SOSA-2023 track, local source/target versions and unresolved import, separate assessment authority, and limits of older smoke/normalized reasoning. Two obsolete current-named audits have historical banners; their findings were not rewritten. No external research, commit, tag, release, merge, or remote update was performed.

## Candidate publication criterion

Both tracks may be assessed against these high-level requirements without identical source versions, mappings, or conclusions. This candidate implements the checks only for the current track; the pinned alternative remains unchanged.

| Criterion | Result |
|---|---|
| 1. Exact available-local source/target, workbook, product and configuration identities frozen | PASS |
| 2. Dynamic source inventory equals assessment inventory | PASS |
| 3. Every source term has a final assessment | BLOCKED |
| 4. No deferred or unreviewed source terms | BLOCKED |
| 5. Formal coverage reported separately from assessment | PASS |
| 6. Publication-critical rationale decisions resolved | BLOCKED |
| 7. Approximate deductive difference has an acceptable reviewed result | BLOCKED |
| 8. Exact-closure source example results established | BLOCKED |
| 9. Selected approved positive/negative independent expectations have current passing results | BLOCKED |
| 10. Identity reporting internally consistent | PASS |
| 11. Full repository validation passes in declared environment | BLOCKED |
| 12. Evidence bound to HEAD and exact candidate input bytes; protected authorities unchanged | BLOCKED |

## Mechanical human-review entry evidence

The [earlier guard-repair report](../../../current-publication-guard-repair.md) and prior completion claims were superseded by independent audits. The [final trust-repair report](../../../current-publication-final-trust-repair.md) records the schema-downgrade and retry-archive repairs. This milestone is ready only for independent human-review gate audit; it does not approve human semantic decisions or certify publication readiness.

Current stored and publication validators require ticketed custody unconditionally: reconstructed slot, pre-execution ticket, wrapper envelope/capture, retained bytes, derived classification, and summary. Missing, legacy, malformed or unknown schema declarations fail; mutable metadata cannot choose a legacy path. Historical inspection is separate and limited to the code-pinned archive and its retained hashes, explicitly ineligible for current review evidence and publication. Historical-to-current reconciliation is retired. A repeated driver destination is rejected before any existing input or output is touched; retries require fresh build/evidence destinations and retain separate tickets, nonces and outputs with explicit invocation selection. See the [repair validation ledger](../../gate-defect-validation.json).

The existing twelve reconstructed historical finals are fixed by exact assessment-record identities. Every new or materially changed final requires a separately bound project-specific human decision record before queue removal or rationale finality.

Review packets include relevant incoming restrictions and relationships, grouped disjointness and source/target/mapping chain provenance. Asserted facts remain distinct from explicitly explained derived consequences. These packets are bounded evidence aids, not exhaustive ontology exports or semantic decision engines; unresolved closure-dependent decisions still require the missing evidence.

## Finite remaining blockers

1. Complete the 74-term human review queue, retaining explicit decisions and rationale evidence; 0 terms are deferred and 74 unreviewed.
2. Resolve 1 judgment-sensitive rationale proposals before treating them as adequate publication rationales.
3. No local artifact resolves imported ontology: http://www.w3.org/2004/02/skos/core. Exact transitive import closure is unavailable; no network fetch was attempted.
4. Source hierarchy: technical_failure; Unresolved imported ontology; available-local-graph output is diagnostic only. See individual profile/reasoner outputs.
5. Aligned hierarchy: technical_failure; Unresolved imported ontology; available-local-graph output is diagnostic only. See individual profile/reasoner outputs.
6. Exact-closure example success is not established for every source example and the separate fixture.
7. Source and target approximate deductive-difference comparisons do not both have a valid PASS result.
8. Human approval of selected positive and negative semantic expectations is outstanding.
9. Resolve the exact OWL 2 DL declaration/profile gaps: source skos:Concept; aligned dcterms:type and adms:status; and the per-example vocabulary violations recorded individually. Any closure/overlay change must be reviewed, pinned, and reevaluated without silently changing mapping semantics.
10. Selected authenticated semantic execution completed with unsuccessful results; these remain substantive publication blockers.
11. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/aligned-hierarchy.command.json
12. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-00-aligned.command.json
13. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-00-source.command.json
14. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-01-aligned.command.json
15. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-01-source.command.json
16. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-02-aligned.command.json
17. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-02-source.command.json
18. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-03-aligned.command.json
19. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-03-source.command.json
20. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-04-aligned.command.json
21. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-04-source.command.json
22. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-05-aligned.command.json
23. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-05-source.command.json
24. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-06-aligned.command.json
25. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-06-source.command.json
26. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-07-aligned.command.json
27. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-07-source.command.json
28. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-08-aligned.command.json
29. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-08-source.command.json
30. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-09-aligned.command.json
31. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-09-source.command.json
32. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-10-aligned.command.json
33. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-10-source.command.json
34. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-11-aligned.command.json
35. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-11-source.command.json
36. Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/source-hierarchy.command.json
37. Repeat the full gate in the declared Java distribution/environment; the local execution environment differs as recorded in commands.json.

The implementation milestone is a reviewable candidate. An independent **read-only audit** is recommended before any semantic adoption, commit, or publication claim. Final Git status and all changed/created file classes are recorded in [the candidate manifest](../../../current-publication-candidate.json).

CURRENT TRACK NOT YET PUBLICATION READY — HUMAN SEMANTIC REVIEW REQUIRED

## Diagnostic classification

Class A (evidence/infrastructure): **0**. Class B (substantive requirements): **37**.

- Class B: Complete the 74-term human review queue, retaining explicit decisions and rationale evidence; 0 terms are deferred and 74 unreviewed.
- Class B: Resolve 1 judgment-sensitive rationale proposals before treating them as adequate publication rationales.
- Class B: No local artifact resolves imported ontology: http://www.w3.org/2004/02/skos/core. Exact transitive import closure is unavailable; no network fetch was attempted.
- Class B: Source hierarchy: technical_failure; Unresolved imported ontology; available-local-graph output is diagnostic only. See individual profile/reasoner outputs.
- Class B: Aligned hierarchy: technical_failure; Unresolved imported ontology; available-local-graph output is diagnostic only. See individual profile/reasoner outputs.
- Class B: Exact-closure example success is not established for every source example and the separate fixture.
- Class B: Source and target approximate deductive-difference comparisons do not both have a valid PASS result.
- Class B: Human approval of selected positive and negative semantic expectations is outstanding.
- Class B: Resolve the exact OWL 2 DL declaration/profile gaps: source skos:Concept; aligned dcterms:type and adms:status; and the per-example vocabulary violations recorded individually. Any closure/overlay change must be reviewed, pinned, and reevaluated without silently changing mapping semantics.
- Class B: Selected authenticated semantic execution completed with unsuccessful results; these remain substantive publication blockers.
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/aligned-hierarchy.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-00-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-00-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-01-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-01-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-02-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-02-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-03-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-03-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-04-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-04-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-05-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-05-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-06-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-06-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-07-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-07-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-08-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-08-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-09-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-09-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-10-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-10-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-11-aligned.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/example-11-source.command.json
- Class B: Semantic command did not complete successfully: reports/current-publication-validation/semantic-20261029T210428413149Z/source-hierarchy.command.json
- Class B: Repeat the full gate in the declared Java distribution/environment; the local execution environment differs as recorded in commands.json.
