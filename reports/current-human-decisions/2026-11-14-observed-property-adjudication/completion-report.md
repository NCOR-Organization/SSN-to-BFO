# observedProperty human typing adjudication — completion report

The interrupted task was inspected before resuming. The authoritative workbook, assessment and generated products still had the previous blank/technical-deferral treatment. Prepared governance support and an isolated candidate were retained. The saved candidate was then encoded once through the semantic-workbook transition workflow; no duplicate decision or RowID was created.

## Approved result

```turtle
sosa:observedProperty rdfs:domain sosa:Observation .
sosa:observedProperty rdfs:range sosa:ObservableProperty .
```

The existing domain row is `Sheet2!36`, RowID `urn:uuid:f7b8b133-2846-4627-9f8d-1ba39c13b9d1`. The appended range row is `Sheet2!65`, RowID `urn:uuid:763e4066-4999-491d-8f7e-7dc0a86eeebc`. Only existing cells B36/C36/D36 changed; the new row contains its source, predicate, target, approved rationale and RowID. All 107 preexisting RowIDs and 106 unrelated workbook rows are preserved.

The logical delta is exactly two added ObjectPropertyDomain/ObjectPropertyRange axioms, with no removed axioms. No observedProperty superproperty is asserted. HermiT does not entail the former has_input inclusion or the corresponding instance edge. The new typing does not establish the same-FeatureOfInterest correlation. These are global OWL typing commitments, not SHACL constraints.

## Human provenance and assessment

Reviewer: Alec Sculley. Decision: `urn:uuid:d875c53c-a2c8-49a9-8f3b-3a68c8adb0b5`; explicit new human decision, `final / formal_mapping_adopted`. The approval is retained in `approved-instructions.txt`. The record uses approval date 2026-11-14; its encoding timestamp is `2026-11-15T13:59:56.822679-05:00`. It binds the exact two RowIDs, assertions, workbook and review packet. The semantic transition is `reports/current-semantic-workbook/transitions/dce2fe18-42da-44f8-9e45-25861dfb92d8.json`.

The previous assessment, review packet and technical-deferral rationale are retained in the before snapshots and comparison. Historical context is not the active outcome: the new explicit source-class typing decision supersedes the technical deferral. All 90 other assessment records and all 126 previous human-decision files remain byte-identical.

Final counts: 91 terms, 108 governed rows, 102 OWL assertions, six deliberate blank rows; 22 final, zero deferred, 69 unreviewed/unresolved; 15 formal_mapping_adopted, five no_direct_mapping, two inheritance_sufficient. Coverage remains separately classified: this is typing-only treatment, not a BFO/CCO/RO superproperty alignment.

The existing validators previously rejected final/formal_mapping_adopted for all typing-only rows. Minimal authentication support now accepts an explicit `formal_typing_approval` only when the approval flag and exact domain/range assertions are bound, no competing mapping assertion exists, and all normal provenance/authentication checks pass. Existing direct-mapping classification and prior approval checks are unchanged. The two governance documents and focused regression tests describe and verify this bounded compatibility addition.

## Focused validation

- The exact candidate passed OWL 2 DL and HermiT for all four maintained current products, with zero named unsatisfiable classes.
- All 13 focused HermiT entailment expectations passed, including domain/range classification of untyped individuals, absence of has_input and same-feature entailments, satisfiability of Observation/ObservableProperty/Sensor/Stimulus, the preserved Observation-to-PlannedAct classification, and the historical sensor-agent pair.
- Independent repeated rendering was byte-identical. Integrated and alignment-core products gained precisely the two approved triples; strict-BFO and CCO-extension product bytes are unchanged.
- The isolated actual encoding passed semantic-transition authentication, generation and assessment generation/authentication.
- Final working-tree commands passed: `python -B tools/current_semantic_workbook.py check`, `python -B tools/check_coms_mapping.py --check-only`, and `python -B tools/current_assessment.py`. The last command confirmed assessment report freshness and decision authentication. The generation check validated the complete local closures and did not rewrite maintained outputs.
- Eight of nine selected regression tests passed. The existing `test_queue_complete_and_rationales_separate_documentation_from_approval` still fails at `tests/test_current_assessment.py:806`, requiring at least two alternatives where one exists. The four remaining affected cases are madeBySensor, madeObservation, implementedBy and implements. Their alternatives are identical to the clean baseline; observedProperty has left the queue. This known failure was not bypassed or repaired. See `validation/preexisting-queue-failure.json` and `validation/focused-tests.log`.
- Independent preservation audit: all 175 preexisting untracked files, six pinned inputs, 89 SOSA-next/2023 named paths and 45 historical deferral/recovery files remain byte-identical. Observation and ObservableProperty mappings are unchanged.
- `git diff --check` passes. HEAD remains `f16fe2130bb4f50d9c1e4bd41452e25cb5d05963`; the index is empty. No staging, commit, tag or push was performed.

The validation directory retains exact execution logs, reasoner results, focused entailment queries and the candidate harness. Temporary execution paths in captured logs are historical execution locations, not maintained product locations. Product/workbook hashes and the exact changed/new file inventory are in `validation-manifest.json`. No publication-readiness, migration or unrelated semantic repair was performed.
