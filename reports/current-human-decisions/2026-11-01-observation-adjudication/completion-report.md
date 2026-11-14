# Observation adjudication completion

Implemented Alec Sculley's explicit human approval dated 2026-11-01 for the current SSN/SOSA track.

Row: `Sheet1!8`. RowID: `urn:uuid:d973063c-f3a7-4a0b-ab0f-e0ee1fb9eeaa`. Only workbook target cell `C8` and reasoning cell `D8` changed.

## Exact logical change

Removed:
```text
sosa:Observation rdfs:subClassOf cco:PlannedAct and (cco:has_process_part some (cco:ActOfMeasuring and cco:ActOfObservation))
```

Added:
```text
sosa:Observation rdfs:subClassOf cco:PlannedAct
```

This deliberately weakens the necessary conditions. The old expression requires one process part in both CCO classes; it does not merely require potentially distinct parts. The revision preserves PlannedAct classification and does not prohibit measuring or sensory observation. The original expression, rationale, predecision assessment and original review packet remain in the bound history.

Integrated and CCO-extension products each replace exactly this one axiom. Independent RDF comparison confirms that only its obsolete expression/list structure was removed (seven blank nodes; net 15 fewer triples). All unrelated mappings, domain/range axioms and chains are unchanged. Alignment-core and strict-BFO files are byte-identical.

## Decision provenance

Reviewer: `Alec Sculley`. Encoding timestamp: `2026-11-01T00:26:27.231836-04:00`. Decision: `urn:uuid:af760628-27de-4579-91a6-c6c04d28aad7`. Semantic transition: `c7561942-ba35-4f19-84fc-1103091239df`.

Authority: `EXPLICIT_NEW_HUMAN_DECISION`; outcome: `final / formal_mapping_adopted`. `approved-instructions.txt`, `Observation.json`, and `before-after.json` retain exact authorization and comparison. Existing assessment review/notes fields remain predecision context, as required by the existing schema; the new final state, rationale and decision govern the resolution.

## Counts and validation

91 source terms; 107 workbook rows; 100 OWL mapping assertions; seven deliberate blank rows. Assessments: 21 final, 70 unreviewed/unresolved, zero deferred. Outcomes: 14 formal_mapping_adopted, five no_direct_mapping, two inheritance_sufficient.

PASS: semantic transition; deterministic generation and freshness; assessment and decision authentication; focused inventory and historical-final preservation regressions; OWL 2 DL and HermiT for all four maintained products, with zero named unsatisfiable classes. The original required process-part restriction is absent from the Observation mapping.

One focused queue regression fails on its unchanged requirement for two alternatives per unresolved item. The identical failure was reproduced in the clean baseline checkout at ff6d8ab626013bd63b0ba61842d24b919a8902d9. Five historically authorized treatments already have one alternative in both baseline and current packets (observedProperty, madeBySensor, madeObservation, implementedBy and implements). This is not introduced by Observation. No unrelated decisions were reopened and the test was not relaxed. Exact evidence is in validation/preexisting-queue-test-failure.json.

All 90 unrelated assessment records, all existing human decisions and source ontologies, all 51 explicitly identified SOSA-2023 paths, and all 175 preexisting untracked files remain byte-identical. No implementation-rule or infrastructure code changed. The existing assessment tests were updated only for the approved final-term membership and counts.

Validation command logs and independent graph/preservation evidence are under `validation/`; hashes and command results are in `validation-results.json`. The auxiliary historical-baseline helper invocation rejected an unsuitable immediate-prior snapshot; the normal current assessment workflow authenticated the installed state without any bypass or infrastructure repair.

## Product hashes

| Product | SHA-256 |
|---|---|
| `SSN2BFO.ttl` | `31891c62505276432b95870363d23afa076066cd71f80767e4fc83339ad2f844` |
| `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl` | `d346e19bdb7c82b649411650b606eb41b72c397b892eeb274628f21d758b06ef` |
| `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl` | `676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af` |
| `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl` | `aae3d5a2b45f1a19fcfab2ba90ee7945b2c662329610c865793263096dfa875e` |

Workbook SHA-256: `0ce3ec7d4b161619b23a2bb42793859726345a90e9946e68164588fa78e81f7a`.

## Exact changed files

14 modified files and 22 added files. No preexisting untracked file is included in this change inventory.

Modified:

- `SSN2BFO.ttl`
- `mappings/SSN2BFO-COMS.xlsx`
- `mappings/current-ssn-sosa-assessment.json`
- `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl`
- `reports/coms-generation-validation.md`
- `reports/coms-product-dispositions.json`
- `reports/coms-vs-pre-coms-legacy-diff.md`
- `reports/current-assessment/v2/current-ssn-sosa-coverage.json`
- `reports/current-assessment/v2/current-ssn-sosa-coverage.md`
- `reports/current-assessment/v2/current-ssn-sosa-human-review.json`
- `reports/current-assessment/v2/current-ssn-sosa-human-review.md`
- `reports/current-assessment/v2/current-ssn-sosa-rationale-proposals.json`
- `reports/current-assessment/v2/current-ssn-sosa-rationale-proposals.md`
- `tests/test_current_assessment.py`

Added:

- `reports/current-human-decisions/2026-11-01-observation-adjudication/Observation-before-review-packet.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/Observation-review-packet.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/Observation.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/approved-instructions.txt`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/assessment-before.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/before-after.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/changed-files.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/completion-report.md`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/transition-authorities.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation-results.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/assessment-freshness.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/assessment-write.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/baseline-queue-test.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/focused-assessment-tests.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/generation-freshness.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/generation-update.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/independent-audit.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/preexisting-queue-test-failure.json`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/semantic-transition-check.log`
- `reports/current-human-decisions/2026-11-01-observation-adjudication/validation/workbook-preservation.json`
- `reports/current-semantic-workbook/transitions/c7561942-ba35-4f19-84fc-1103091239df.json`
- `reports/current-semantic-workbook/versions/0ce3ec7d4b161619b23a2bb42793859726345a90e9946e68164588fa78e81f7a.xlsx`

HEAD and index are unchanged. Nothing was staged, committed, tagged or pushed. No publication-readiness, migration or release-packaging workflow was run.
