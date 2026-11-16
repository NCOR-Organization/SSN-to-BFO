# Approved COMS semantic rationales — batch 1

Applied the ten approved Reasoning replacements. No semantic decisions, mapping expressions, assessment records or source ontologies changed.

## Validation and preservation

- Documentary transition: `reports/current-documentary-workbook/updates/28022a81-0a85-485d-be5e-a75cc61e0ab5.json`.
- Workbook SHA-256: `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b` → `825dc90460ddc056c89b5b7af3030b4c615a0c5e00c5cfae89057029c10cfc2d`.
- Unchanged A/B/C/E semantic projection: `1f55e9c01cf93a9d680fe05c53716c9639ccd92b02db6841a0f28aa9fa4ec9ae`.
- All four maintained current-track ontology products are byte-identical. Logical delta: zero added and zero removed axioms.
- Counts unchanged: 91 terms; 108 rows; 102 assertions; six deliberate blank OWL rows.
- Assessment states unchanged: 22 final, 69 unreviewed, zero deferred. Outcomes: 15 formal_mapping_adopted, five no_direct_mapping, two inheritance_sufficient, 69 unreviewed.
- Documentary mixed-history validation, decision authentication/report freshness, generation/update and deterministic generation checks passed. The existing generation workflow reports HermiT PASS with zero named unsatisfiable classes.
- Focused regression tests: 38 passed, one identical baseline failure. `test_maintained_live_workbook_resolves_to_immutable_decision_snapshot` expects obsolete projection `566d6a6ba6200458eab5ea7561c86d0eb2483765fa5a1a7c2e8ff0526654eb44`; both baseline and final workbook have `1f55e9c01cf93a9d680fe05c53716c9639ccd92b02db6841a0f28aa9fa4ec9ae`. The test suite did not fully pass. No test or validator was changed.
- No full publication gate was run. No new OWL profile claim is inferred from documentary tests; maintained OWL products and their pinned dependencies are byte-identical.
- 1839 preexisting tracked files and all 175 preexisting untracked files are byte-identical. Git index content, branch and HEAD are unchanged. Literal index bytes changed during checks, but all 1,847 index entries match HEAD and nothing is staged. SOSA-2023 is unchanged.
- The initial generation attempt identified the existing requirement for an exact rule filename in both implementation rationale cells. The final shared wording retains `(rules/ssn-implementation-mapping.rq)` so external-rule coverage is preserved. Temporary unpublished trial registrations were consolidated into the single final documentary update; preexisting history was untouched.

Every exact original rationale remains in tracked reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx and the unchanged authority records cited in rationale-changes.json. The new documentary record additionally archives both complete workbooks and all ten before/after values.

[Machine-readable validation results](validation-results.json) and [exact changes and preservation references](rationale-changes.json) retain the full details.

## Exact before/after rationales

### 1. ssn:implementedBy [deliberate blank OWL mapping]

RowID: `urn:uuid:4afaf231-5478-4a50-9a12-0cbf59d78d7e`. Cell: `Sheet2!D57`.

**Before — exact text**

Historical process-mediated interpretation from b464cea20bae6d6c542ec1db459cc76b6b978beb, with positive example 091de44f6d61cc0d3f48e15e653d263a8dc8fbcb and typing representative 8512004a3b911ac5711fb0cc8dfe70cb086e3b9b. Alec Sculley explicitly authorized the external implementation on 2026-10-30: rules/ssn-implementation-mapping.rq constructs implementedBy and inverse implements from explicit or previously materialized CCO prescribes followed by has_agent premises. The rule is executed separately; it is not an OWL property-chain axiom or a direct Procedure-to-System prescription inclusion. This records an implementation authorization preserving the historical interpretation, not a new scientific adjudication. The OWL predicate and target are deliberately blank because the inference is supplied by the external rule. This term has external-rule mapping coverage; it is not wholly unmapped. The exact historical OWL chain violates three simplicity and four regularity restrictions in the current complete pinned closure.

**After — exact text**

SSN implementedBy relates a Procedure to its implementing System; implements expresses the inverse relationship. The source restriction Procedure ⊑ ∀implementedBy.System supports classifying implementers as Systems. The retained implements domain axiom makes System typing global for the implementing endpoint. Under the process-mediated interpretation, a System's participation as agent in a process prescribed by a Procedure is sufficient for inferring both implementation directions. This condition is sufficient, not necessary: an implementation relation does not imply that a particular execution has occurred. Implementation is therefore not identified with a direct CCO prescription relation between the Procedure and System. The implementedBy OWL predicate and target remain deliberately blank, with process-mediated inference supplied by the external rule (rules/ssn-implementation-mapping.rq). The implements row retains its OWL domain axiom, separately from that external-rule coverage.

**Existing preservation evidence**

- `reports/current-semantic-workbook/implementation-rule-2026-10-30/authorities.json`; SHA-256 `9c73e332082f316248c68de976f39c82e60572847c33e087af61815e23052396`.
- `reports/current-semantic-workbook/transitions/035e5877-1b9d-444c-a970-239ce3bcb97c.json`; SHA-256 `d999ed7feb3a2f58e7e91340e5919ad5b40678b85e10deee4d53edafad2ea0fb`.
- `docs/SSN-IMPLEMENTATION-RULE.md`; SHA-256 `4b2e3a577e18f86dd3c96e7ccfd1a8dacd94a096c9de7e4c88f2a49514ed33e2`.
- `reports/current-semantic-workbook/implementation-rule-2026-10-30/authorized-instructions.txt`; SHA-256 `477b62e02e9c1113781a332bc716ae76ae0788e17a910b82758f6794cd058bd3`.
- `reports/current-semantic-workbook/implementation-rule-2026-10-30/completion-report.md`; SHA-256 `969485ce29fbf00d18e2bf17f0db56610a25f00e1c3df480a3d469ffff76b69a`.
- `reports/current-semantic-workbook/implementation-rule-2026-10-30/owl2dl-violations.md`; SHA-256 `422c3e556e226019582e33ebf90c819a6d6b35b72193e5815c5439217bbc39a3`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 2. ssn:implements rdfs:domain ssn:System

RowID: `urn:uuid:6142726b-21b1-4dba-b5ec-a7d6dca4afab`. Cell: `Sheet2!D58`.

**Before — exact text**

Historical process-mediated interpretation from b464cea20bae6d6c542ec1db459cc76b6b978beb, with positive example 091de44f6d61cc0d3f48e15e653d263a8dc8fbcb and typing representative 8512004a3b911ac5711fb0cc8dfe70cb086e3b9b. Alec Sculley explicitly authorized the external implementation on 2026-10-30: rules/ssn-implementation-mapping.rq constructs implementedBy and inverse implements from explicit or previously materialized CCO prescribes followed by has_agent premises. The rule is executed separately; it is not an OWL property-chain axiom or a direct Procedure-to-System prescription inclusion. This records an implementation authorization preserving the historical interpretation, not a new scientific adjudication. Retain ssn:implements rdfs:domain ssn:System as the historically documented typing representative. The source inverse relationship remains unchanged, and the external rule constructs the System-to-Procedure direction. The direct inclusion in CCO prescribed_by is removed.

**After — exact text**

SSN implementedBy relates a Procedure to its implementing System; implements expresses the inverse relationship. The source restriction Procedure ⊑ ∀implementedBy.System supports classifying implementers as Systems. The retained implements domain axiom makes System typing global for the implementing endpoint. Under the process-mediated interpretation, a System's participation as agent in a process prescribed by a Procedure is sufficient for inferring both implementation directions. This condition is sufficient, not necessary: an implementation relation does not imply that a particular execution has occurred. Implementation is therefore not identified with a direct CCO prescription relation between the Procedure and System. The implementedBy OWL predicate and target remain deliberately blank, with process-mediated inference supplied by the external rule (rules/ssn-implementation-mapping.rq). The implements row retains its OWL domain axiom, separately from that external-rule coverage.

**Existing preservation evidence**

- `reports/current-semantic-workbook/implementation-rule-2026-10-30/authorities.json`; SHA-256 `9c73e332082f316248c68de976f39c82e60572847c33e087af61815e23052396`.
- `reports/current-semantic-workbook/transitions/035e5877-1b9d-444c-a970-239ce3bcb97c.json`; SHA-256 `d999ed7feb3a2f58e7e91340e5919ad5b40678b85e10deee4d53edafad2ea0fb`.
- `docs/SSN-IMPLEMENTATION-RULE.md`; SHA-256 `4b2e3a577e18f86dd3c96e7ccfd1a8dacd94a096c9de7e4c88f2a49514ed33e2`.
- `reports/current-semantic-workbook/implementation-rule-2026-10-30/authorized-instructions.txt`; SHA-256 `477b62e02e9c1113781a332bc716ae76ae0788e17a910b82758f6794cd058bd3`.
- `reports/current-semantic-workbook/implementation-rule-2026-10-30/completion-report.md`; SHA-256 `969485ce29fbf00d18e2bf17f0db56610a25f00e1c3df480a3d469ffff76b69a`.
- `reports/current-semantic-workbook/implementation-rule-2026-10-30/owl2dl-violations.md`; SHA-256 `422c3e556e226019582e33ebf90c819a6d6b35b72193e5815c5439217bbc39a3`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 3. ssn:hasInput rdfs:domain sosa:Procedure

RowID: `urn:uuid:ac30440d-7146-4db0-a8d0-8a5bf549b607`. Cell: `Sheet2!D51`.

**Before — exact text**

The recorded decision rejects cco:has_input for a Procedure-to-Input relation; the current workbook retains only its source domain/range. This is semantic rejection of that process-input superproperty, not a pending implementation.

**After — exact text**

ssn:hasInput links a Procedure to information provided for its use. A Procedure specifies how an activity is carried out and is represented here as directive information content, making sosa:Procedure the intended subject class. This domain axiom applies that classification to every subject of the relation; it does not require every Procedure to have an input. cco:has_input instead relates a process to a continuant needed at its start. Treating the procedure-level relation as its subproperty would impose process typing on the Procedure, conflating the specification with its execution.

**Existing preservation evidence**

- `mappings/current-ssn-sosa-assessment.json`; SHA-256 `7d24058c14a0d86ff8362cc5d81b3a51e1434638ae252f53b2fbbfc173a132fb`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.
- `reports/input-output-cco-mapping-rationale-cleanup.md`; SHA-256 `251b7b672c36dc19c06f60c00fdc9e9bd101dc4c9783f91e8947f9d51d3d9f1f`.
- `reports/hermit-input-output-mapping-evaluation.md`; SHA-256 `7bd33f231e5eb561b9be84a9fb80382e3f7f2da847a316afb5395ffe3783e6c5`.
- `Current_SOSA-SSN to BFO-CCO.xlsx`; SHA-256 `2c8fbee3a80d67d0e08b761706e0d939ab001864ee29c3384b53de065ae08d87`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 4. ssn:hasInput rdfs:range ssn:Input

RowID: `urn:uuid:ab19659f-7e70-4f35-87f1-46b59ae80884`. Cell: `Sheet2!D52`.

**Before — exact text**

The recorded decision rejects cco:has_input for a Procedure-to-Input relation; the current workbook retains only its source domain/range. This is semantic rejection of that process-input superproperty, not a pending implementation.

**After — exact text**

The range axiom types every object of ssn:hasInput as ssn:Input, reflecting SSN's description of Input as information provided to a Procedure for its use. This classification is already entailed by the adopted global hasInput domain sosa:Procedure together with the source restriction that a Procedure's hasInput values are Inputs. The explicit range assertion is logically redundant in that context and is retained to state the intended endpoint classification directly, without requiring readers to reconstruct it from the domain and class-local restriction. It introduces no CCO superproperty. In particular, cco:has_input concerns a process and a continuant required at its start, whereas the subject of the SSN relation is a procedure specification. The range axiom does not by itself require the existence of an input.

**Existing preservation evidence**

- `mappings/current-ssn-sosa-assessment.json`; SHA-256 `7d24058c14a0d86ff8362cc5d81b3a51e1434638ae252f53b2fbbfc173a132fb`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.
- `reports/input-output-cco-mapping-rationale-cleanup.md`; SHA-256 `251b7b672c36dc19c06f60c00fdc9e9bd101dc4c9783f91e8947f9d51d3d9f1f`.
- `reports/hermit-input-output-mapping-evaluation.md`; SHA-256 `7bd33f231e5eb561b9be84a9fb80382e3f7f2da847a316afb5395ffe3783e6c5`.
- `Current_SOSA-SSN to BFO-CCO.xlsx`; SHA-256 `2c8fbee3a80d67d0e08b761706e0d939ab001864ee29c3384b53de065ae08d87`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 5. ssn:hasOutput rdfs:domain sosa:Procedure

RowID: `urn:uuid:27ab2a4a-15a3-4585-885a-bbac1fe0a5bb`. Cell: `Sheet2!D53`.

**Before — exact text**

The recorded decision rejects cco:has_output for a Procedure-to-Output relation; the current workbook retains only its source domain/range. This is semantic rejection of that process-output superproperty, not a pending implementation.

**After — exact text**

ssn:hasOutput links a Procedure to information reported from it. A Procedure specifies how an activity is carried out and is represented here as directive information content, making sosa:Procedure the intended subject class. This domain axiom applies that classification to every subject of the relation; it does not require every Procedure to have an output. cco:has_output instead relates a process to a continuant required at its completion. Treating the procedure-level relation as its subproperty would impose process typing on the Procedure, conflating the specification with its execution.

**Existing preservation evidence**

- `mappings/current-ssn-sosa-assessment.json`; SHA-256 `7d24058c14a0d86ff8362cc5d81b3a51e1434638ae252f53b2fbbfc173a132fb`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.
- `reports/input-output-cco-mapping-rationale-cleanup.md`; SHA-256 `251b7b672c36dc19c06f60c00fdc9e9bd101dc4c9783f91e8947f9d51d3d9f1f`.
- `reports/hermit-input-output-mapping-evaluation.md`; SHA-256 `7bd33f231e5eb561b9be84a9fb80382e3f7f2da847a316afb5395ffe3783e6c5`.
- `Current_SOSA-SSN to BFO-CCO.xlsx`; SHA-256 `2c8fbee3a80d67d0e08b761706e0d939ab001864ee29c3384b53de065ae08d87`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 6. ssn:hasOutput rdfs:range ssn:Output

RowID: `urn:uuid:766c2e20-d125-448b-bc37-642daebaf088`. Cell: `Sheet2!D54`.

**Before — exact text**

The recorded decision rejects cco:has_output for a Procedure-to-Output relation; the current workbook retains only its source domain/range. This is semantic rejection of that process-output superproperty, not a pending implementation.

**After — exact text**

The range axiom types every object of ssn:hasOutput as ssn:Output, reflecting SSN's description of Output as information reported from a Procedure. This classification is already entailed by the adopted global hasOutput domain sosa:Procedure together with the source restriction that a Procedure's hasOutput values are Outputs. The explicit range assertion is logically redundant in that context and is retained to state the intended endpoint classification directly, without requiring readers to reconstruct it from the domain and class-local restriction. It introduces no CCO superproperty. In particular, cco:has_output concerns a process and a continuant required at its completion, whereas the subject of the SSN relation is a procedure specification. The range axiom does not by itself require the existence of an output.

**Existing preservation evidence**

- `mappings/current-ssn-sosa-assessment.json`; SHA-256 `7d24058c14a0d86ff8362cc5d81b3a51e1434638ae252f53b2fbbfc173a132fb`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.
- `reports/input-output-cco-mapping-rationale-cleanup.md`; SHA-256 `251b7b672c36dc19c06f60c00fdc9e9bd101dc4c9783f91e8947f9d51d3d9f1f`.
- `reports/hermit-input-output-mapping-evaluation.md`; SHA-256 `7bd33f231e5eb561b9be84a9fb80382e3f7f2da847a316afb5395ffe3783e6c5`.
- `Current_SOSA-SSN to BFO-CCO.xlsx`; SHA-256 `2c8fbee3a80d67d0e08b761706e0d939ab001864ee29c3384b53de065ae08d87`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 7. sosa:madeBySensor rdfs:domain sosa:Observation

RowID: `urn:uuid:434602eb-cfc3-4bca-9fb3-92154e87c6bc`. Cell: `Sheet2!D32`.

**Before — exact text**

Restore the historical sensor-agent solution from commits b21d1fa82f41327aee07a03c412aca29faebd526 and 854174b2a1a23e1ebfe1f152fe967b16d3139c4d. The Observation-to-Sensor relation is included in cco:has_agent. Retain the source inverse and existing domain/range typing. The coordinated restoration also defers the direct observedProperty-to-has_input inclusion. Current complete local OWL 2 DL, HermiT and focused entailment checks pass; this restores historical authority without a new semantic adjudication.

**After — exact text**

SOSA defines madeBySensor as the relation from an Observation to the Sensor that made it. The domain axiom applies this endpoint meaning to every use of the relation: every subject of this relation is inferred to be a sosa:Observation. This is an explicit OWL typing commitment based on the source definition and its schema:domainIncludes note, rather than an entailment of that annotation alone. Typing does not itself require any instance of the relation to exist; the cco:has_agent inclusion is a separate mapping.

**Existing preservation evidence**

- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/authorized-instruction.txt`; SHA-256 `368d4c83b3f6757d98db31eedef139622793a28dc448de95326816b97553eaab`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/entailment-result.json`; SHA-256 `397426c7beb9f4e371359d3df2d082e0fbde1e07336d4b15bd736ff7fb8868a7`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 8. sosa:madeBySensor rdfs:range sosa:Sensor

RowID: `urn:uuid:99f8aba6-abaa-49de-a126-da1573f24c39`. Cell: `Sheet2!D33`.

**Before — exact text**

Restore the historical sensor-agent solution from commits b21d1fa82f41327aee07a03c412aca29faebd526 and 854174b2a1a23e1ebfe1f152fe967b16d3139c4d. The Observation-to-Sensor relation is included in cco:has_agent. Retain the source inverse and existing domain/range typing. The coordinated restoration also defers the direct observedProperty-to-has_input inclusion. Current complete local OWL 2 DL, HermiT and focused entailment checks pass; this restores historical authority without a new semantic adjudication.

**After — exact text**

SOSA defines madeBySensor as the relation from an Observation to the Sensor that made it. The range axiom applies this endpoint meaning to every use of the relation: every object of this relation is inferred to be a sosa:Sensor. This is an explicit OWL typing commitment based on the source definition and its schema:rangeIncludes note, rather than an entailment of that annotation alone. Typing does not itself require any instance of the relation to exist; the cco:has_agent inclusion is a separate mapping.

**Existing preservation evidence**

- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/authorized-instruction.txt`; SHA-256 `368d4c83b3f6757d98db31eedef139622793a28dc448de95326816b97553eaab`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/entailment-result.json`; SHA-256 `397426c7beb9f4e371359d3df2d082e0fbde1e07336d4b15bd736ff7fb8868a7`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 9. sosa:madeObservation rdfs:domain sosa:Sensor

RowID: `urn:uuid:839fa73d-6601-4b17-9331-062846ba0f3e`. Cell: `Sheet2!D34`.

**Before — exact text**

Restore the historical sensor-agent solution from commits b21d1fa82f41327aee07a03c412aca29faebd526 and 854174b2a1a23e1ebfe1f152fe967b16d3139c4d. The Sensor-to-Observation relation is included in cco:agent_in. Retain the source inverse and existing domain/range typing. The coordinated restoration also defers the direct observedProperty-to-has_input inclusion. Current complete local OWL 2 DL, HermiT and focused entailment checks pass; this restores historical authority without a new semantic adjudication.

**After — exact text**

SOSA defines madeObservation as the relation from a Sensor to an Observation made by that Sensor. The domain axiom applies this endpoint meaning to every use of the relation: every subject of this relation is inferred to be a sosa:Sensor. This is an explicit OWL typing commitment based on the source definition and its schema:domainIncludes note, rather than an entailment of that annotation alone. Typing does not itself require any instance of the relation to exist; the cco:agent_in inclusion is a separate mapping.

**Existing preservation evidence**

- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/authorized-instruction.txt`; SHA-256 `368d4c83b3f6757d98db31eedef139622793a28dc448de95326816b97553eaab`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/entailment-result.json`; SHA-256 `397426c7beb9f4e371359d3df2d082e0fbde1e07336d4b15bd736ff7fb8868a7`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

### 10. sosa:madeObservation rdfs:range sosa:Observation

RowID: `urn:uuid:e2d7f509-a5ee-477a-9660-f608b518ea3f`. Cell: `Sheet2!D35`.

**Before — exact text**

Restore the historical sensor-agent solution from commits b21d1fa82f41327aee07a03c412aca29faebd526 and 854174b2a1a23e1ebfe1f152fe967b16d3139c4d. The Sensor-to-Observation relation is included in cco:agent_in. Retain the source inverse and existing domain/range typing. The coordinated restoration also defers the direct observedProperty-to-has_input inclusion. Current complete local OWL 2 DL, HermiT and focused entailment checks pass; this restores historical authority without a new semantic adjudication.

**After — exact text**

SOSA defines madeObservation as the relation from a Sensor to an Observation made by that Sensor. The range axiom applies this endpoint meaning to every use of the relation: every object of this relation is inferred to be a sosa:Observation. This is an explicit OWL typing commitment based on the source definition and its schema:rangeIncludes note, rather than an entailment of that annotation alone. Typing does not itself require any instance of the relation to exist; the cco:agent_in inclusion is a separate mapping.

**Existing preservation evidence**

- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/authorized-instruction.txt`; SHA-256 `368d4c83b3f6757d98db31eedef139622793a28dc448de95326816b97553eaab`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; SHA-256 `232d714911a130068cb280726428c4d95a2ce731db7fbe9e7321f5b2af16f25e`.
- `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; SHA-256 `e6ca14409fbd4df59ecbcbf3c36fb09cc762919225d8e0d288f755c723d9d2b9`.
- `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/entailment-result.json`; SHA-256 `397426c7beb9f4e371359d3df2d082e0fbde1e07336d4b15bd736ff7fb8868a7`.
- `reports/current-semantic-workbook/versions/64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b.xlsx`; SHA-256 `64a0864d5c58f698fc441e00cb8f0dc27500a268eb6353a49e0b82ccba31c71b`.

## Changed files

- `mappings/SSN2BFO-COMS.xlsx`
- `reports/coms-generation-validation.md`
- `reports/coms-product-dispositions.json`
- `reports/current-assessment/v2/current-ssn-sosa-coverage.json`
- `reports/current-assessment/v2/current-ssn-sosa-coverage.md`
- `reports/current-assessment/v2/current-ssn-sosa-human-review.json`
- `reports/current-assessment/v2/current-ssn-sosa-rationale-proposals.json`
- `reports/current-assessment/v2/current-ssn-sosa-rationale-proposals.md`

## Generated ontology hashes

- `SSN2BFO.ttl`: `d98206745a1d4383c0f79125f1681af83b25e2f7b314c8f42cd8255d8185eabd`
- `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl`: `cb5a7d89b0a54cd3a0bbf0b7644d0e8b0ab8c77f8878e7d9fc0e29de5b7a4ee5`
- `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl`: `676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af`
- `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl`: `aae3d5a2b45f1a19fcfab2ba90ee7945b2c662329610c865793263096dfa875e`

No staging, commit, tag, push, new semantic decision, or infrastructure repair was performed.
