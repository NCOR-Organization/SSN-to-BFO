The workbook’s main publication-documentation gap is **`coms:Reasoning`**. I identified **104 cells with supported documentary values**: 102 blank cells and two outdated sample-pair explanations. One existing explanation, for `sosa:FeatureOfInterest`, needs documentary clarification.

**No files were modified.** All 1,057 inventoried repository files retained their hashes; HEAD, branch, working-tree status, and tags were unchanged.

## 1. Actual workbook schema

The authoritative workbook contains **105 rows representing 91 source terms**:

- `Sheet1`: 44 data rows, rows 2–45.
- `Sheet2`: 61 data rows, rows 2–62.
- Both sheets have exactly the same five columns.
- All 105 RowIDs are populated and unique.

Source: :codex-file-citation{path="/Users/alecsculley/Documents/GitHub/SSN-to-BFO/mappings/SSN2BFO-COMS.xlsx" purpose="source" artifact_kind="workbook"}

| Column | Field | Meaning | Required by current tooling/generation | Optional value? | Emission | Validation |
|---|---|---|---|---|---|---|
| A | `sssom:subject_id` | Source class/property | Header and value required | No | Logical assertion subject and reports | Source resolution, scope/type compatibility |
| B | `sssom:predicate_id` | Mapping predicate | Header required; value required for an assertion | Only when C is also deliberately blank | Logical predicate and reports | Supported predicate, source/target compatibility, paired-blank rule |
| C | `coms:Target` | Target entity, Manchester expression, or ordered property-chain expression | Header required; value required for an assertion | Only when B is also deliberately blank | Logical target/expression and reports | Entity resolution, expression parsing and mapping constraints |
| D | `coms:Reasoning` | Documentary explanation | Header required; nonblank value not required for generation | Yes, mechanically | Reports/audit data; **not emitted as ontology rationale** | Some contradiction checks; no general supported-rationale completeness check |
| E | `coms:RowID` | Persistent assertion-row identity | Header and value required | No | Identity/disposition reports; not a logical mapping axiom | Canonical UUIDv4 identity, uniqueness and preservation |

This is the repository’s actual profile, not a generalized COMS schema. See the [primary workbook profile](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/tools/coms_framework_integration.py:52), [required headers](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/tools/generate_mapping_from_coms.py:102), and [row-identity rules](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/MAPPING-GOVERNANCE.md:34).

`MappingStatus` is supported by a legacy reader path but is **not a column in this workbook or its current primary profile**.

## 2. Missing and incomplete content

| Finding | Count | Interpretation |
|---|---:|---|
| Blank `coms:Reasoning` | 102 cells | Documentary omissions; not evidence that 102 mappings lack prior decisions |
| Existing but ambiguous reasoning | 1 cell | `Sheet1!D6`, `FeatureOfInterest` |
| Existing but outdated reasoning | 2 cells | `Sheet2!D16:D17`, finalized sample pair |
| Deliberately blank predicates | 2 cells | `Sheet2!B16:B17` |
| Deliberately blank targets | 2 cells | `Sheet2!C16:C17` |
| Missing source identifiers or RowIDs | 0 | No completion needed |
| Half-blank predicate/target pairs | 0 | No malformed partial mapping rows |
| Placeholder values, formulas or inconsistent surrounding whitespace | 0 found | No mechanical replacement set identified |

There are no hidden sheets, comments, tables, merged cells, or defined names carrying an alternative documentary schema.

The historical audit separates the 77 unresolved assessment records as follows:

| Historical category | Terms | Workbook rows | Documentary treatment |
|---|---:|---:|---|
| Prior decisions already implemented | 61 | 69 | Recover rationale and provenance without new semantic approval |
| Genuinely unresolved questions | 4 | 4 | Record supported provisional facts; leave the semantic conclusion open |
| Historical/current discrepancies | 8 | 10 | Record both versions without choosing; exclude ambiguous `D6` from automatic replacement |
| Evidence holds | 4 | 6 | Record the hold and established implementation history |
| Already-final assessments, outside those 77 | 14 | 16 | Copy existing supported/approved rationales |

Thus, the 104 proposed cells comprise **85 supported historical/final rationale values** and **19 neutral unresolved/discrepancy/hold notes**.

## 3. Publication information absent as workbook columns

Absence of a column does not establish missing project metadata. The repository already assigns several kinds of information to separate authorities.

| Information investigated | What is needed | Existing repository authority/evidence | Correct location |
|---|---|---|---|
| Rationale | Supported explanation of the assertion or deliberate absence | Existing D column; [publication criterion 6](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md:97) | **Populate D** |
| Assessment state/outcome | Distinguish final, unresolved, no direct mapping, etc. | [Assessment file](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/mappings/current-ssn-sosa-assessment.json); [governance separation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/MAPPING-GOVERNANCE.md:11) | Existing assessment artifact; no new workbook column |
| Product disposition | Identify direct inclusion, imported coverage, or product-specific exclusion | [Product-disposition governance](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/MAPPING-GOVERNANCE.md:58) | Generated disposition report |
| Decision provenance/evidence | Trace explanations to retained artifacts and commits | Historical workbook/reports and the evidence references below; [provenance requirement](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md:89) | Existing evidence artifacts and publication provenance; documentary references can accompany D |
| Decision date/version/commit | Preserve known historical provenance accurately | Retained Git history and decision records | Evidence/decision artifact; do not turn commit dates into human-review dates |
| Reviewer/authority | Required for newly recorded human decisions | [Human-decision requirements](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md:17) | Existing human-decision record; no inferred historical reviewer |
| Source/target identity | Exact local bytes, version information and known provenance | [Current identity configuration](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/config/current-ssn-sosa-identity.json) | Identity configuration and publication manifests |
| Mapping strength/type | Preserve subclass, equivalence, subproperty, typing and chain distinctions | B/C already encode these; generation derives classifications | Existing B/C and generated reports |
| Technical/profile qualification | Distinguish implementation limitations from semantic rejection | Historical reports; [non-adoption distinctions](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md:65) | D explanation plus supporting report |
| Historical/deprecated note | Explain a retained change without restoring historical axioms | Historical workbook and Git/report evidence | D where relevant |
| No-direct-mapping rationale | Explain deliberate absence | Assessment records and approved sample decisions | D; outcome remains in assessment artifact |
| Evidence-hold reason | Preserve what evidence is unavailable | Existing validation/review reports | D note and evidence report |
| Ontology publication metadata | Titles, descriptions, licensing and release identity | [Publication metadata policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/VALIDATION-AND-RELEASES.md:286) | `config/publication-metadata.toml` |
| SSSOM export metadata/accounting | Export only faithfully representable mappings and account for omissions | [MAP-06 requirement](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/prov-functional-parity-audit.md:399) | Separate generated export/accounting artifact |

**No genuinely necessary new workbook column was established.**

The publication audit does identify rationale availability to consumers as a concern and suggests a separate generated provenance artifact. That does not justify putting reviewer, version, license, or product-disposition columns into the authoritative workbook. See [AUTH-04 and MAP-06](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/prov-functional-parity-audit.md:128).

Complex restrictions, unions, chains and typing rows must not be flattened into simple SSSOM mappings. Nor does a generic `ManualMappingCuration` export value identify a particular reviewer or establish a human decision.

## 4. What remains unresolved

These are limits on a **conclusive semantic rationale**, not obstacles to writing the neutral documentary notes proposed below.

| Terms / cells | Established facts that can be documented | What cannot be finalized from those facts | Action for that unresolved conclusion |
|---|---|---|---|
| `SampleRelationship`, `Sheet1!D3` | Provisional information-content interpretation and current subclass assertion | Whether that interpretation is the intended final semantic commitment | REQUIRES SEMANTIC RECONCILIATION |
| `hasSampleRelationship`, `Sheet2!D2` | Current `is_subject_of` inclusion and provisional model | General justification of that inclusion | REQUIRES SEMANTIC RECONCILIATION |
| `relatedSample`, `Sheet2!D4` | Current `is_about` inclusion and provisional model | General justification of that inclusion | REQUIRES SEMANTIC RECONCILIATION |
| `phenomenonTime`, `Sheet2!D11` | Earlier result-applicability-time explanation; later temporal-occupancy mapping | Why the time to which a result applies must be occupied by the execution | REQUIRES SEMANTIC RECONCILIATION |
| `FeatureOfInterest`, `Sheet1!D6` | Active subclass union and existing “Direct alignment deferred” text | What the deferral text was intended to qualify | NEEDS DOCUMENTARY CLARIFICATION |
| `madeBySensor`, `Sheet2!D32:D33` | Earlier retained `has_agent`; current typing-only rows | Reconcile the earlier inclusion with its current omission | REQUIRES SEMANTIC RECONCILIATION |
| `madeObservation`, `Sheet2!D34:D35` | Earlier retained `agent_in`; current typing-only rows | Same inverse-side discrepancy | REQUIRES SEMANTIC RECONCILIATION |
| `forProperty`, `Sheet2!D49` | Earlier explicit rejection; current restored chain | Reconcile those opposed commitments | REQUIRES SEMANTIC RECONCILIATION |
| `implementedBy`, `Sheet2!D57` | Earlier process-mediated chain; current direct `prescribes` inclusion | Reconcile direct and mediated meanings | REQUIRES SEMANTIC RECONCILIATION |
| `implements`, `Sheet2!D58` | Earlier inverse mediated interpretation; current direct inclusion | Same inverse-side discrepancy | REQUIRES SEMANTIC RECONCILIATION |
| `MeasurementRange`, `Sheet1!D43` | Historical `is_affected_by`; current `caused_by` restriction | Explain/reconcile the changed relation | REQUIRES SEMANTIC RECONCILIATION |
| `SystemProperty`, `Sheet1!D45` | Earlier rejection of an over-specific prescription; current restoration | Explain/reconcile that restoration | REQUIRES SEMANTIC RECONCILIATION |
| `RelationshipNature`, `Sheet1!D2`; `natureOfRelationship`, `Sheet2!D3` | Provisional interpretation and missing resolving local SKOS closure | A conclusion requiring that missing closure | EVIDENCE HOLD |
| `madeActuation`, `Sheet2!D26:D27`; `madeByActuator`, `Sheet2!D28:D29` | Technical deferral and current typing | A final semantic conclusion from incomplete/conflicting exact-closure evidence | EVIDENCE HOLD |

For all of these, **the current predicate and target are preserved**. Recording a discrepancy is not permission to restore an earlier mapping.

## 5. Row-level field-completion matrix

The matrix is normalized to keep long expressions and repeated rationale text readable:

- Every row below concerns **D, `coms:Reasoning`**.
- Current D is **blank**, except `Sheet1!D6` and `Sheet2!D16:D17`, whose exact current values appear immediately afterward.
- Proposed D and its evidence are given by the matching destination in the separate exact-value catalog in section 6.
- **Semantics change: NO for every proposed documentary edit.**
- Action **S** = **SAFE TO POPULATE FROM EXISTING EVIDENCE**.
- Action **C** = **NEEDS DOCUMENTARY CLARIFICATION**.
- Confidence **E** = **exact**; **R** = **reconstructable**; **A** = **ambiguous**.
- RowID values below have the common prefix **`urn:uuid:`**.
- Predicate abbreviations: **SC** `rdfs:subClassOf`; **EC** `owl:equivalentClass`; **SP** `rdfs:subPropertyOf`; **D** `rdfs:domain`; **Rng** `rdfs:range`; **CH** `owl:propertyChainAxiom`.
- `Tn` is the exact class target expression listed after the matrix.
- `EXEC` means exactly `(sosa:Observation or sosa:Actuation or sosa:Sampling)`.
- `PROP` means exactly `(bfo:SpecificallyDependentContinuant or bfo:ProcessProfile)`.

### Sheet1

| Row | RowID suffix | Source | Predicate | Current target | Proposed D / confidence / action |
|---:|---|---|---|---|---|
| 2 | f475ef3c-12f0-4925-ad21-419ebd96406b | sampling:RelationshipNature | SC | T2 | D2 / R / S |
| 3 | bc709fe5-c239-494c-9b88-c14e5a8fc79e | sampling:SampleRelationship | SC | T3 | D3 / R / S |
| 4 | 1b7c27d4-1b0e-461f-8a77-7a81631ab342 | sosa:ActuatableProperty | SC | T4 | D4 / E / S |
| 5 | 2a4f78b4-92cb-4095-9a6b-2ae03e00be4a | sosa:Actuation | EC | T5 | D5 / E / S |
| 6 | 06782965-88c5-4345-ab99-ea027513ec86 | sosa:FeatureOfInterest | SC | T6 | Preserve existing text / A / C |
| 7 | 99b22791-b2d1-4667-901e-861a44f2b8a2 | sosa:ObservableProperty | SC | T7 | D7 / E / S |
| 8 | d973063c-f3a7-4a0b-ab0f-e0ee1fb9eeaa | sosa:Observation | SC | T8 | D8 / E / S |
| 9 | b4508c03-1b79-4f53-b525-d5db6d80c7cb | sosa:Platform | EC | T9 | D9 / E / S |
| 10 | b05ab84c-eeff-45d1-a95d-39cf2d9f084f | sosa:Result | EC | T10 | D10 / E / S |
| 11 | 326ad20d-f954-44e0-b94f-dccf0fd76ebb | sosa:Sample | EC | T11 | D11 / E / S |
| 12 | 7b3f908b-b717-4336-9968-8b1083f847d3 | sosa:Sampling | EC | T12 | D12 / E / S |
| 13 | 8897fadf-b70f-4d81-a08c-a072f873f82b | ssn-system:Accuracy | SC | T13 | D13 / E / S |
| 14 | b15038bf-7e69-4e62-9cdd-50edb029d88b | ssn-system:Condition | SC | T14 | D14 / E / S |
| 15 | 86e97aa4-dc26-4d62-bef6-52cf36869bc8 | ssn-system:DetectionLimit | SC | T15 | D15 / E / S |
| 16 | 823bbbdf-b4f1-4e45-8b0a-5597306e6b69 | ssn-system:Drift | SC | T16 | D16 / E / S |
| 17 | 124e6b06-906a-47be-a459-92babef3992e | ssn-system:Frequency | SC | T17 | D17 / E / S |
| 18 | 1a25c5c5-795c-444c-ba3b-e0578f9e715b | ssn-system:Latency | SC | T18 | D18 / E / S |
| 19 | afc3498b-5446-4c8b-928f-822a8e148b63 | ssn-system:MaintenanceSchedule | SC | T19 | D19 / E / S |
| 20 | 335606ce-18b3-43d9-b13e-7301015c9d26 | ssn-system:OperatingPowerRange | SC | T20 | D20 / E / S |
| 21 | 206e2eaa-765b-491b-ad9c-73f144f048a1 | ssn-system:OperatingProperty | SC | T21 | D21 / E / S |
| 22 | dbdcee3f-bbdf-4a35-b92e-a14dd26e6239 | ssn-system:OperatingRange | SC | T22 | D22 / E / S |
| 23 | 2befdb79-d016-45f8-8c35-69ee93fa731f | ssn-system:Precision | SC | T23 | D23 / E / S |
| 24 | 3ac135c9-bfd7-49cf-9c51-4d6e9ed56d87 | ssn-system:Resolution | SC | T24 | D24 / E / S |
| 25 | b891bb2b-0093-49ff-aa86-2a68a732686d | ssn-system:ResponseTime | SC | T25 | D25 / E / S |
| 26 | 3ddcc935-040b-450b-8ffa-8b0972e33c3b | ssn-system:Selectivity | SC | T26 | D26 / E / S |
| 27 | 624eaef2-892a-4b9d-8ed6-08c79571710f | ssn-system:Sensitivity | SC | T27 | D27 / E / S |
| 28 | 304f62a7-9160-4857-9c39-04a7215b1bb0 | ssn-system:SurvivalProperty | SC | T28 | D28 / E / S |
| 29 | c912bc86-4ac6-4200-8606-7fda6005542f | ssn-system:SystemCapability | SC | T29 | D29 / E / S |
| 30 | ad8cba71-f987-4e6a-b9c0-7660d5cbc8a7 | ssn-system:SystemLifetime | SC | T30 | D30 / E / S |
| 31 | 1c52d7ee-ee3d-4eb7-ae42-4df1912ee8eb | ssn:Deployment | EC | T31 | D31 / E / S |
| 32 | 282b2a18-f710-4eac-a5c8-43894a242f23 | ssn:Input | SC | T32 | D32 / E / S |
| 33 | 89f70432-c87d-41dd-bff2-e6120c02b5a4 | ssn:Output | SC | T33 | D33 / E / S |
| 34 | b1421726-3675-4b2a-9824-150e108157e4 | ssn:Property | EC | T34 | D34 / E / S |
| 35 | 23915904-0174-4f2f-b6cf-6a8671b92d7e | ssn:Stimulus | EC | T35 | D35 / R / S |
| 36 | 66010702-8134-4e08-a972-f0767ec8dead | ssn:System | EC | T36 | D36 / E / S |
| 37 | ee7f2f05-bc8e-4477-bb58-0f40e6da81d0 | sosa:Actuator | SC | T37 | D37 / E / S |
| 38 | 2902e2b3-44f8-4f81-8ca9-2def4b68befd | sosa:Sensor | SC | T38 | D38 / R / S |
| 39 | d88535da-ab7c-409c-b928-a9b0760b4607 | sosa:Procedure | SC | T39 | D39 / R / S |
| 40 | 98b1044d-6bfe-41d2-89aa-cdc87e524e4c | sosa:Sampler | EC | T40 | D40 / E / S |
| 41 | 7caa02f4-26a1-4e81-b709-5c2116636f65 | ssn-system:ActuationRange | SC | T41 | D41 / R / S |
| 42 | d8b4d0f0-d8d4-4f22-ae7c-2bbdebcdd51f | ssn-system:BatteryLifetime | SC | T42 | D42 / R / S |
| 43 | d180e765-d4d1-4578-a33a-6e96308e01db | ssn-system:MeasurementRange | SC | T43 | D43 / R / S |
| 44 | c15208c5-847f-4de3-a456-4037142ca542 | ssn-system:SurvivalRange | SC | T44 | D44 / R / S |
| 45 | 9ea02b02-c86b-4a0b-a56b-47c1dea0bfa4 | ssn-system:SystemProperty | SC | T45 | D45 / R / S |

### Sheet2

| Row | RowID suffix | Source | Predicate | Current target | Proposed D / confidence / action |
|---:|---|---|---|---|---|
| 2 | 5ec3234d-bd10-4f5b-89f9-f2abb75764ec | sampling:hasSampleRelationship | SP | cco:is_subject_of | D2 / R / S |
| 3 | f293250d-b1e8-4467-8b7d-a94fb2b9b705 | sampling:natureOfRelationship | SP | cco:is_about | D3 / R / S |
| 4 | 3734c3b6-e62e-4ae5-be42-8fef0b10d2f4 | sampling:relatedSample | SP | cco:is_about | D4 / R / S |
| 5 | 69e972da-23ad-4e50-822b-e41198c95795 | sosa:actsOnProperty | SP | cco:affects | D5 / E / S |
| 6 | b16f1d3a-3d10-4b75-9f12-2331e6c46d74 | sosa:hasFeatureOfInterest | D | EXEC | D6 / R / S |
| 7 | 01b1aff2-a12b-430b-9775-b43241c3a7cf | sosa:hasFeatureOfInterest | Rng | sosa:FeatureOfInterest | D7 / R / S |
| 8 | cbbba7df-22ee-4393-b4fd-46019697192a | sosa:hasResult | SP | cco:has_output | D8 / E / S |
| 9 | b5a532fc-5dea-4a47-9323-0a78a849c078 | sosa:isFeatureOfInterestOf | D | sosa:FeatureOfInterest | D9 / R / S |
| 10 | e15cfee1-3c8e-4519-bce0-ec62729fd2fd | sosa:isFeatureOfInterestOf | Rng | EXEC | D10 / R / S |
| 11 | 2abe4468-736d-4db8-99d7-1670730a6710 | sosa:phenomenonTime | SP | bfo:occupies_temporal_region | D11 / R / S |
| 12 | 377fa547-ff5c-4ffa-af6f-40d291ab2ab9 | sosa:usedProcedure | SP | cco:prescribed_by | D12 / E / S |
| 13 | 79e12baa-9467-4494-bdf3-b6906f5a81a7 | ssn-system:inCondition | D | `(ssn-system:SystemCapability or ssn-system:OperatingRange or ssn-system:SurvivalRange)` | D13 / R / S |
| 14 | 2018c5db-cb41-4a54-aa97-df5df82f0286 | ssn-system:qualityOfObservation | SP | cco:has_output | D14 / E / S |
| 15 | 02294d3c-f88d-4d3d-921e-8d6c00457476 | ssn:isPropertyOf | D | PROP | D15 / R / S |
| 16 | 2ae25d88-9551-45e7-a2b9-7735575e4d8f | sosa:hasSample | blank | blank | Approved rationale / E / S |
| 17 | 637399a9-a264-49f7-bab8-33f2128646ab | sosa:isSampleOf | blank | blank | Approved rationale / E / S |
| 18 | 3af8734c-ac86-46b0-8c0c-27a19525bc1e | sosa:hosts | CH | `bfo:bearer_of o bfo:has_realization o bfo:has_participant` | D18 / R / S |
| 19 | e866de80-683d-4138-a713-be9646d37148 | sosa:isHostedBy | CH | `bfo:participates_in o bfo:realizes o bfo:inheres_in` | D19 / R / S |
| 20 | 8c9662e8-a69c-4ce1-9d17-381ec3cdc162 | sosa:isActedOnBy | SP | cco:is_affected_by | D20 / E / S |
| 21 | d5712b64-a526-4112-ba23-520ec8dc5066 | sosa:isObservedBy | D | sosa:ObservableProperty | D21 / R / S |
| 22 | 37fac05e-0d70-420d-a0c0-78bc1d87cd63 | sosa:isObservedBy | Rng | sosa:Sensor | D22 / R / S |
| 23 | 61fc3404-f33a-4c4c-a25c-412d9972016c | sosa:observes | D | sosa:Sensor | D23 / R / S |
| 24 | 5ce06556-de99-44be-922d-a3d092a00dbb | sosa:observes | Rng | sosa:ObservableProperty | D24 / R / S |
| 25 | b4fc5247-7d44-4619-9d0b-8466f45218bf | sosa:isResultOf | SP | cco:is_output_of | D25 / E / S |
| 26 | 01085646-1b07-4c69-a39a-0c5c8ab53d33 | sosa:madeActuation | D | sosa:Actuator | D26 / R / S |
| 27 | 0f9d6fa9-00b9-4602-b31d-9e205f53e67d | sosa:madeActuation | Rng | sosa:Actuation | D27 / R / S |
| 28 | 675bb221-ad63-4033-9f22-5190d0b6d545 | sosa:madeByActuator | D | sosa:Actuation | D28 / R / S |
| 29 | ac95c1e2-0d93-48de-be9d-4defbe6525f0 | sosa:madeByActuator | Rng | sosa:Actuator | D29 / R / S |
| 30 | a63a89a9-d9e6-4e7d-ba06-96ff17833866 | sosa:madeBySampler | SP | cco:has_agent | D30 / E / S |
| 31 | 9c14f13e-16c8-4afd-bcee-8b4bb9d3f0ca | sosa:madeSampling | SP | cco:agent_in | D31 / E / S |
| 32 | 434602eb-cfc3-4bca-9fb3-92154e87c6bc | sosa:madeBySensor | D | sosa:Observation | D32 / R / S |
| 33 | 99f8aba6-abaa-49de-a126-da1573f24c39 | sosa:madeBySensor | Rng | sosa:Sensor | D33 / R / S |
| 34 | 839fa73d-6601-4b17-9331-062846ba0f3e | sosa:madeObservation | D | sosa:Sensor | D34 / R / S |
| 35 | e2d7f509-a5ee-477a-9660-f608b518ea3f | sosa:madeObservation | Rng | sosa:Observation | D35 / R / S |
| 36 | f7b8b133-2846-4627-9f8d-1ba39c13b9d1 | sosa:observedProperty | SP | cco:has_input | D36 / R / S |
| 37 | 37576663-68e9-4298-8652-a3c614c34ae3 | ssn-system:hasOperatingProperty | SP | bfo:specifically_depended_on_by | D37 / R / S |
| 38 | 265137eb-a279-4f9a-b1b9-e85d7ecb02a7 | ssn-system:hasOperatingRange | D | ssn:System | D38 / R / S |
| 39 | 8b87dd5b-298e-4ae7-8724-3778c0a67234 | ssn-system:hasOperatingRange | Rng | ssn-system:OperatingRange | D39 / R / S |
| 40 | f0fbd0af-655a-46c8-bda9-1c2adb24a10a | ssn-system:hasSurvivalProperty | SP | bfo:specifically_depended_on_by | D40 / R / S |
| 41 | 82ce9316-b7a7-4655-9c98-e16c314a0244 | ssn-system:hasSurvivalRange | D | ssn:System | D41 / R / S |
| 42 | bd5a2014-f338-49b8-b7ef-27f5b933d93b | ssn-system:hasSurvivalRange | Rng | ssn-system:SurvivalRange | D42 / R / S |
| 43 | 5f25dce9-54a0-442e-a9de-f18cd21aab1d | ssn-system:hasSystemCapability | D | ssn:System | D43 / R / S |
| 44 | 1e9432ec-0bfb-4c05-8a16-c4295d545f81 | ssn-system:hasSystemCapability | Rng | ssn-system:SystemCapability | D44 / R / S |
| 45 | d8f45381-cd95-4251-ae69-803a033a8f49 | ssn-system:hasSystemProperty | SP | bfo:specifically_depended_on_by | D45 / R / S |
| 46 | af48aae7-263f-436d-a76a-4e7232c609c5 | ssn:deployedOnPlatform | SP | bfo:has_participant | D46 / R / S |
| 47 | c0a94c70-33c7-41ac-8906-49ad2efe48b5 | ssn:deployedSystem | SP | bfo:has_participant | D47 / R / S |
| 48 | 6335c13d-fb23-49fd-9662-fd682c79f172 | ssn:detects | SP | cco:is_affected_by | D48 / R / S |
| 49 | 287f1392-ca8f-4dc2-9d42-b60b3962adfc | ssn:forProperty | CH | `cco:described_by o cco:is_about` | D49 / R / S |
| 50 | 6c58598b-8de6-4559-82fa-53a6efc6a3c4 | ssn:hasDeployment | SP | bfo:participates_in | D50 / E / S |
| 51 | ac30440d-7146-4db0-a8d0-8a5bf549b607 | ssn:hasInput | D | sosa:Procedure | D51 / E / S |
| 52 | ab19659f-7e70-4f35-87f1-46b59ae80884 | ssn:hasInput | Rng | ssn:Input | D52 / E / S |
| 53 | 27ab2a4a-15a3-4585-885a-bbac1fe0a5bb | ssn:hasOutput | D | sosa:Procedure | D53 / E / S |
| 54 | 766c2e20-d125-448b-bc37-642daebaf088 | ssn:hasOutput | Rng | ssn:Output | D54 / E / S |
| 55 | 43ad1a14-e8a4-48d5-ae2b-3b5a5b28f8d3 | ssn:hasProperty | Rng | PROP | D55 / R / S |
| 56 | 158c0cce-2c1d-4baf-90b5-243d7cdce34d | ssn:hasSubSystem | SP | bfo:has_continuant_part | D56 / E / S |
| 57 | 4afaf231-5478-4a50-9a12-0cbf59d78d7e | ssn:implementedBy | SP | cco:prescribes | D57 / R / S |
| 58 | 6142726b-21b1-4dba-b5ec-a7d6dca4afab | ssn:implements | SP | cco:prescribed_by | D58 / R / S |
| 59 | 17528e16-1f22-4c6e-9e29-e3b3c6699804 | ssn:inDeployment | SP | bfo:participates_in | D59 / E / S |
| 60 | ebf4115f-fe96-4959-89a4-98c3a6031cff | ssn:isProxyFor | D | ssn:Stimulus | D60 / R / S |
| 61 | b7873da3-fc78-4a2a-92e1-ef83efb6d600 | ssn:isProxyFor | Rng | ssn:Property | D61 / R / S |
| 62 | 51c8556f-9b82-4113-a9d7-c733e70cf8cd | ssn:wasOriginatedBy | SP | cco:process_started_by | D62 / R / S |

### Exact current nonblank reasoning values

**`Sheet1!D6`:**

> Direct alignment deferred because SOSA permits a FeatureOfInterest to be property-like. Restricting every FeatureOfInterest to a material entity or process makes the SSN survival-range pattern unsatisfiable.

Proposed value: **unchanged**, pending clarification. The ambiguity is documented in the [current review policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md:77).

**`Sheet2!D16`:**

> Property-chain mapping deferred because an owl:propertyChainAxiom makes sosa:hasSample non-simple, which conflicts with the pinned SOSA/SSN inverse-functional declaration. The source ontology remains unchanged; the representation intent belongs in a rule, SHACL, or annotation layer rather than the OWL 2 DL mapping product.

**`Sheet2!D17`:**

> Property-chain mapping deferred because an owl:propertyChainAxiom makes sosa:isSampleOf non-simple, which conflicts with the pinned SOSA/SSN functional declaration and the minimum-cardinality restriction on sosa:Sample. The source ontology remains unchanged; the representation intent belongs in a rule, SHACL, or annotation layer rather than the OWL 2 DL mapping product.

Those last two values describe the earlier technical deferral and omit the subsequently approved semantic no-direct decisions.

### Deliberate blanks

| Cells | Source / RowID | Current value | Proposed value | Confidence | Semantics change | Action |
|---|---|---|---|---|---|---|
| Sheet2!B16, C16 | hasSample / `urn:uuid:2ae25d88-9551-45e7-a2b9-7735575e4d8f` | blank | blank | exact | NO | LEAVE AS DELIBERATE BLANK |
| Sheet2!B17, C17 | isSampleOf / `urn:uuid:637399a9-a264-49f7-bab8-33f2128646ab` | blank | blank | exact | NO | LEAVE AS DELIBERATE BLANK |

### Exact Sheet1 target-expression register

These are current values, **not proposed edits**.

```text
T2 = T3 = T32 = T33 =
cco:InformationContentEntity

T4 = T7 =
(bfo:SpecificallyDependentContinuant and bfo:inheres_in some sosa:FeatureOfInterest) or (bfo:ProcessProfile and bfo:occurrent_part_of some sosa:FeatureOfInterest)

T5 =
cco:PlannedAct and (sosa:actsOnProperty some sosa:ActuatableProperty)

T6 =
(bfo:SpecificallyDependentContinuant or bfo:ProcessProfile or bfo:MaterialEntity or bfo:Process)

T8 =
cco:PlannedAct and (cco:has_process_part some (cco:ActOfMeasuring and cco:ActOfObservation))

T9 =
bfo:MaterialEntity and (sosa:hosts some ssn:System)

T10 =
(cco:InformationContentEntity or bfo:MaterialEntity) and (cco:is_output_of some (sosa:Observation or sosa:Actuation or sosa:Sampling))

T11 =
bfo:MaterialEntity and (cco:is_object_of some sosa:Sampling)

T12 =
cco:PlannedAct and (cco:prescribed_by some sosa:Procedure) and (cco:has_output some sosa:Sample)

T13 = T15 =
bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:VeracityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification)))

T14 = T29 =
(bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and (cco:condition_described_by some cco:PerformanceSpecification)

T16 = T24 =
bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:DeviationMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification)))

T17 =
bfo:Function and bfo:has_realization some (cco:PlannedAct and bfo:has_occurrent_part some (cco:Frequency and cco:prescribed_by some cco:ArtifactFunctionSpecification))

T18 = T25 =
bfo:Function and bfo:has_realization some (cco:PlannedAct and (cco:has_process_part some cco:Cause) and (cco:has_process_part some cco:Effect) and (bfo:occupies_temporal_region some (bfo:TemporalRegion and cco:prescribed_by some cco:ArtifactFunctionSpecification)))

T19 =
bfo:Disposition and bfo:has_realization some (cco:Change and cco:affects some (bfo:SpecificallyDependentContinuant and bfo:participates_in some (cco:ActOfMaintenance and bfo:has_occurrent_part some (cco:Frequency and cco:prescribed_by some cco:ArtifactDesign))))

T20 =
bfo:Function and bfo:has_realization some (bfo:Process and bfo:has_occurrent_part some (cco:Power and cco:prescribed_by some cco:ArtifactDesign))

T21 = T22 =
(bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and cco:prescribed_by some cco:ArtifactDesign

T23 =
bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:ReliabilityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification)))

T26 =
bfo:Function and bfo:has_realization some (cco:PlannedAct and bfo:has_participant some (bfo:Continuant and cco:prescribed_by some cco:ArtifactFunctionSpecification))

T27 =
bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:RatioMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification)))

T28 =
bfo:Function and bfo:has_realization some (bfo:Process and cco:caused_by some (bfo:Process and bfo:realizes some (cco:Affordance and cco:prescribed_by some cco:ArtifactDesign)))

T30 =
bfo:Function and bfo:has_realization some (cco:StasisOfArtifactOperationality and (cco:caused_by some (bfo:Process and bfo:realizes some (cco:Affordance and cco:prescribed_by some cco:ArtifactDesign))))

T31 =
cco:PlannedAct and (ssn:deployedSystem some ssn:System) and (ssn:deployedOnPlatform some bfo:MaterialEntity)

T34 =
(bfo:SpecificallyDependentContinuant or bfo:ProcessProfile)

T35 =
cco:Cause and (cco:is_cause_of some sosa:Observation)

T36 =
bfo:MaterialEntity and (ssn:implements some sosa:Procedure)

T37 =
bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Actuation))) and (cco:agent_in some sosa:Actuation)

T38 =
bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Observation))) and (cco:agent_in some sosa:Observation)

T39 =
cco:DirectiveInformationContentEntity and (cco:prescribes some bfo:Process)

T40 =
bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Sampling))) and (cco:agent_in some sosa:Sampling)

T41 =
bfo:Function and (bfo:has_realization some (sosa:Actuation and ((cco:has_output some bfo:SpecificallyDependentContinuant) and (cco:prescribed_by some cco:ArtifactFunctionSpecification))))

T42 =
bfo:Function and (bfo:has_realization some (cco:StasisOfArtifactOperationality and (bfo:has_occurrent_part some cco:Power) and (cco:caused_by some (bfo:Process and (bfo:realizes some (cco:Affordance and (cco:prescribed_by some cco:ArtifactDesign)))))))

T43 =
bfo:Function and (bfo:has_realization some (sosa:Observation and (cco:caused_by some (ssn:Stimulus and (cco:prescribed_by some cco:ArtifactFunctionSpecification)))))

T44 =
bfo:Function and (bfo:has_realization some (bfo:Process and (cco:caused_by some (bfo:Process and (bfo:realizes some (cco:Affordance and (cco:prescribed_by some cco:ArtifactDesign)))))))

T45 =
(bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and (cco:prescribed_by some cco:ArtifactFunctionSpecification)
```

## 6. Separate safe auto-fill set: exact values and evidence

The following catalog contains **only the 104 proposed documentary assignments**. Each text is the proposed complete cell value. Grouped destinations receive identical text. Evidence references are separate from the cell text.

**H** below means the retained [historical current-track workbook](</Users/alecsculley/Documents/GitHub/SSN-to-BFO/legacy/workbooks/Current_SOSA-SSN to BFO-CCO.xlsx>). Historical rationale copies were checked against commit **`8bcabba`, 2026-06-19**, unless another commit is specified.

### Sheet1: class explanations

| Destination | Exact proposed value | Evidence |
|---|---|---|
| D2 | Provisional mapping for instance-data testing: RelationshipNature is treated as descriptive/information content identifying the nature of a reified sample relationship. The evidence hold remains open because the source declares a skos:Concept superclass but the imported SKOS ontology has no resolving local artifact; exact transitive closure evidence is unavailable. | H, `Sample Relationship!F5`; [provisional model](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sample-relationship-deferral.md:3); [source](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/imports/sosa-sampling.ttl:47); [closure limitation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/current-ssn-sosa-semantic-validation.md:60); `cedee99`, 2026-07-03 |
| D3 | The historical implementation treats SampleRelationship as a reified descriptive/information-content structure about a relationship involving samples. It was explicitly provisional for instance-data testing. The current row retains the InformationContentEntity subclass assertion; whether that interpretation becomes authoritative remains unresolved. | H, `Sample Relationship!F6`; [provisional model](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sample-relationship-deferral.md:3); `cedee99`, 2026-07-03 |
| D4 | This class is modeled as either a specifically dependent continuant or a process profile to align with SSN/SOSA’s treatment of properties that may be continuant features or features of processes, both of which can be the target of intentional change. | H, `Common Classes!F2` |
| D5 | Actuation is modeled as a planned process because it is intentionally carried out according to a procedure in order to change the state of the world, which aligns directly with the CCO notion of a PlannedAct. | H, `Common Classes!F3` |
| D7 | ObservableProperty mirrors ActuatableProperty in being modeled as either a specifically dependent continuant or a process profile, reflecting that observable aspects may be features of continuants or temporally extended features of processes. | H, `Common Classes!F8` |
| D8 | sosa:Observation is modeled as a cco:PlannedAct with internal structure because it involves intentional acts of observation and measurement carried out according to a procedure. The cco:has_process_part restriction captures the necessary internal structure without overcommitting to an equivalentTo axiom, since observations may have additional process parts. | H, `Common Classes!F9` |
| D9 | sosa:Platform is modeled as a bfo:MaterialEntity defined by its role in hosting systems, without committing to parthood, attachment, or containment as necessary conditions. The equivalentTo axiom captures that hosting at least one system is both necessary and sufficient for being a platform. | H, `Common Classes!F11` |
| D10 | Result is allowed to be either informational or material because SOSA results include both informational outputs (e.g., measurements) and material outputs (e.g., samples). | H, `Common Classes!F14` |
| D11 | Sample is modeled as a material entity because it is a physical thing intentionally produced or selected to stand in for a feature of interest. | H, `Common Classes!F15` |
| D12 | sosa:Sampling is modeled as a cco:PlannedAct because it is intentionally carried out according to a procedure to create or transform samples. The equivalentTo axiom captures that being prescribed by a procedure and producing a sample as output is both necessary and sufficient for being a sampling. | H, `Common Classes!F17`; [output-target correction](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/mapping-consistency-target-mismatch-review.md:236); `5080932`, 2026-07-01 |
| D31 | ssn:Deployment is modeled as a cco:PlannedAct because it involves intentional positioning or installation of systems for a purpose, rather than constituting a structural relation such as parthood. The equivalentTo axiom captures that deploying at least one system on at least one material entity is both necessary and sufficient for being a deployment. | H, `Common Classes!F5` |
| D32 | Input is mapped to InformationContentEntity because SSN inputs are informational resources made available to procedures, not material participants or process parts. | H, `Common Classes!F7` |
| D33 | Output is modeled as an information content entity because SSN outputs are informational artifacts produced by executing procedures, regardless of whether they later influence material processes. | H, `Common Classes!F10` |
| D34 | ssn:Property is modeled as the union of bfo:SpecificallyDependentContinuant and bfo:ProcessProfile in order to accommodate both intrinsic qualities that inhere in independent continuants and temporal properties that are process profiles of occurrents within a single SOSA abstraction. | H, `Common Classes!F13` |
| D35 | The retained mapping characterizes Stimulus as a CCO Cause that is the cause of some Observation. The historical rationale treats a stimulus as an event or happening that causally contributes to an observation and expressly selects necessary-and-sufficient equivalence for this characterization. | H, `Common Classes!C19:F19` |
| D36 | ssn:System is modeled as a bfo:MaterialEntity defined by its capability to implement procedures. The equivalentTo axiom captures that being a material entity that implements at least one procedure is both necessary and sufficient for being a system, reflecting the functional rather than structural definition in SOSA. | H, `Common Classes!F20` |
| D37 | sosa:Actuator is a bfo:MaterialEntity because actuators are physical devices. The bfo:RealizableEntity it bears is realized in actuation processes, capturing the functional rather than purely structural definition of actuators. The cco:agent_in restriction captures that the actuator plays a causative role in the actuation. | H, `Common Classes!F4`; [realization-direction correction](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/mapping-consistency-target-mismatch-review.md:166); `a74f983`, 2026-07-01 |
| D38 | This row retains the explicit Sensor subclass expression for the current local CCO profile: material entity, bearer of a realizable entity realized in an Observation, and agent in an Observation. The historical cco:Sensor equivalence concerned a separate forward-looking target-version profile. This note documents the retained current-profile expression without settling that separate question. | [Version-specific resolution](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sosa-sensor-version-alignment-resolution.md:180); [profile qualification](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sosa-sensor-version-alignment-deferral.md:49); `491c258`, 2026-07-14 |
| D39 | The retained mapping treats Procedure as information content prescribing how a process is to be carried out and retains the prescribes-some-Process restriction. Its target is the stable IRI cco:ont00000965, called Prescriptive Information Content Entity in historical workbook prose and labelled Directive Information Content Entity in the current imported target. | H, `Common Classes!C12:F12`; [current target identity](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/imports/cco.ttl:12847); `eca12b2`, 2026-07-01 |
| D40 | sosa:Sampler is modeled analogously to sosa:Sensor and sosa:Actuator as a bfo:MaterialEntity bearing a bfo:RealizableEntity realized in a sampling process and functioning as an agent. The equivalentTo axiom captures that these conditions are both necessary and sufficient for being a sampler. | H, `Common Classes!F16`; [explicit equivalence decision](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sampler-equivalentclass-decision.md:3); `bf779d7`, 2026-07-02 |

### Sheet1: system-capability explanations

| Destination | Exact proposed value | Evidence |
|---|---|---|
| D13 | Accuracy is modeled as a function rather than a quality because it concerns how well a system performs relative to truth conditions when realized in processes. The use of measurement information entities reflects that accuracy is assessed through evaluative measurement, not directly observed as an intrinsic quality. | H, `System Capability!F2` |
| D14 | This is mapped as a specifically dependent continuant or process profile because conditions are not standalone entities but aspects of a system or its operation that depend on something else and characterize circumstances under which performance is evaluated. The link to PerformanceSpecification reflects that conditions are specified and constrained rather than independently realized. | H, `System Capability!F5` |
| D15 | DetectionLimit is modeled as a function because it characterizes the system’s ability to distinguish presence or absence under uncertainty when realized in processes. The reliance on veracity measurement reflects that detection limits are probabilistic performance characteristics rather than simple qualities. | H, `System Capability!F6` |
| D16 | Drift is modeled as a function because it concerns systematic behavior over time that is manifested through processes rather than existing as a static property. The realization through deviation measurement reflects that drift is assessed by analyzing changes relative to expected values. | H, `System Capability!F7` |
| D17 | Frequency is modeled as a function because it constrains how often a system can perform actions when realized in planned acts. Treating frequency as an occurrent part of realizations reflects that it is manifested through repeated execution rather than existing independently. | H, `System Capability!F8`; [corrected nesting](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/coms-frequency-correction-validation.md:25) |
| D18 | Latency is modeled as a function because it characterizes temporal performance behavior that is only manifested when the system operates. The cause–effect structure and temporal region reflect that latency is measured through realized processes rather than inherent qualities. | H, `System Capability!F16` |
| D19 | MaintenanceSchedule is modeled as a disposition because it represents a tendency or requirement for maintenance to occur under certain conditions. Its realization through maintenance acts reflects that the schedule itself is not a process but is realized in processes. | H, `System Capability!F17` |
| D20 | OperatingPowerRange is modeled as a function because it constrains operational capability with respect to power when realized in processes. Power appears as an occurrent part of realizations rather than as an independent entity. | H, `System Capability!F19` |
| D21 | OperatingProperty is modeled as a specifically dependent continuant or process profile because it characterizes how a system operates under given conditions without being a realizable capability. Its prescription by design reflects engineering intent rather than measured performance. | H, `System Capability!F20` |
| D22 | OperatingRange is modeled as a specifically dependent continuant or process profile because it describes permissible conditions for normal operation rather than behavior itself. The link to ArtifactDesign reflects that operating ranges are design-specified constraints. | H, `System Capability!F21` |
| D23 | Precision is modeled as a function because it concerns consistency across repeated realizations of system behavior. The reliance on reliability measurement reflects that precision is assessed statistically across processes, not as a single intrinsic property. | H, `System Capability!F22` |
| D24 | Resolution is modeled as a function because it characterizes the system’s capacity to discriminate differences when realized in operational processes. The use of deviation measurement reflects that resolution is evaluated by analyzing minimal detectable change through realized behavior. | H, `System Capability!F24` |
| D25 | ResponseTime is modeled as a function because it characterizes temporal system behavior that emerges during operation. The realization via cause–effect process structure reflects that response time is only meaningful when the system is acting. | H, `System Capability!F25` |
| D26 | Selectivity is modeled as a function because it describes how a system behaves during operation with respect to isolating intended properties. The realization in planned acts reflects that selectivity is manifested through operational behavior involving participants. | H, `System Capability!F26` |
| D27 | Sensitivity is modeled as a function because it concerns proportional relationships between input changes and output changes when realized in processes. The ratio-based measurement reflects that sensitivity is an evaluative performance characteristic, not a basic quality. | H, `System Capability!F27`; [nesting comparison](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/coms-vs-pre-coms-legacy-diff.md:123) |
| D28 | SurvivalProperty is modeled as a function because it concerns the system’s capacity to remain viable over time under conditions. The affordance-based realization reflects that survival characteristics emerge from design-enabled processes. | H, `System Capability!F28` |
| D29 | SystemCapability is modeled as a specifically dependent continuant or process profile because capabilities are dependent characteristics of a system that describe what it can do, not processes themselves. The use of PerformanceSpecification captures that capabilities are defined relative to stated performance criteria and conditions. | H, `System Capability!F30` |
| D30 | SystemLifetime is modeled as a function because it characterizes the extent of operational viability rather than a static attribute. Its realization in stasis of operationality reflects that lifetime is manifested as sustained functioning over time. | H, `System Capability!F31` |
| D41 | The implemented simplification retains the Function with an Actuation realization having a specifically dependent continuant output and an ArtifactFunctionSpecification prescription. It removes the former affects some ProcessProfile alternative. Historical reasoner results remain limited to the profile evaluated. | [Implemented simplification](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/actuation-range-simplification-implementation.md:73); `80b4ba1`, 2026-07-09 |
| D42 | BatteryLifetime was modeled as a function characterizing how long a battery supports system operation, realized through operational stasis and continued energy provision. The current COMS expression retains the historical workbook's placement of Power within the realization. Historical reasoner-driven deferral and later COMS restoration are implementation history, not a new semantic rejection or a current reasoner result. | H, `System Capability!D4:F4`; [technical deferral](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/reasoner-unsafe-system-mapping-deferral.md:15); restoration `e0a177c`, 2026-07-13 |
| D43 | Documentary discrepancy: the historical workbook expression and rationale use cco:is_affected_by for the Observation-to-Stimulus restriction; the current COMS expression uses cco:caused_by. A retained semantic explanation reconciling that change was not identified. This note records the discrepancy without endorsing either form or changing the current expression. | H, `System Capability!D18:F18`; [comparison](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/coms-vs-pre-coms-legacy-diff.md:88); `e0a177c`, 2026-07-13 |
| D44 | SurvivalRange was modeled as a function characterizing conditions a system can endure without losing operational integrity, manifested through affordance-realizing processes. Its historical technical deferral explicitly preserved that intended semantics. The expression was subsequently restored in COMS; historical reasoner findings retain their original profile limitations. | H, `System Capability!E29:F29`; [preserved semantic intent](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/hermit-survival-range-deferral-evaluation.md:7); restoration `e0a177c`, 2026-07-13 |
| D45 | Documentary discrepancy: the implemented historical decision removed the direct class expression because its ArtifactFunctionSpecification prescription was over-specific, retaining broader typing through ssn:Property. Current COMS reinstates that prescription. A retained semantic explanation reconciling the reinstatement was not identified. This note records the discrepancy without endorsing either treatment or changing the current expression. | [Historical removal](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/system-property-direct-mapping-deferral.md:109); `42b6dac`, 2026-07-09; restoration `e0a177c`, 2026-07-13 |

### Sheet2: historical, provisional and discrepancy explanations

| Destination | Exact proposed value | Evidence |
|---|---|---|
| D2 | The current is_subject_of assertion uses the provisional information-content interpretation of sample relationships. Retained documentation does not establish a final justification for this property inclusion. | [Provisional interpretation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sample-relationship-deferral.md:3); initial COMS `116890b`, 2026-07-13 |
| D3 | The current is_about assertion remains subject to the existing evidence hold. Relationship-nature interpretation was provisional, and a pinned local SKOS closure is unavailable. This note does not finalize the mapping. | [Provisional interpretation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sample-relationship-deferral.md:15); [closure limitation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/current-ssn-sosa-semantic-validation.md:60) |
| D4 | The current is_about assertion follows a provisional interpretation of SampleRelationship as information content about relations involving samples. A final justification of this property inclusion remains unresolved. | [Provisional interpretation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/sample-relationship-deferral.md:17); `116890b`, 2026-07-13 |
| D6, D7 | The historical workbook deliberately retained hasFeatureOfInterest as a standalone relation and rejected cco:has_input because its endpoint restrictions do not preserve the general feature-of-interest interpretation. The input mapping was removed in dc117689 (2026-07-01); current rows retain only execution-to-feature typing. | H, `Common OPs!C8:F8`; [retained omission](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/updated-spreadsheet-ttl-only-assertions-review.md:27) |
| D9, D10 | The historical workbook retained isFeatureOfInterestOf as the inverse of the standalone hasFeatureOfInterest relation. The rejected has_input interpretation does not justify an inverse BFO/CCO inclusion; current rows retain feature-to-execution typing. | H, `Common OPs!C20:F20` and `C8:F8`; [retained omission](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/updated-spreadsheet-ttl-only-assertions-review.md:27); `dc117689`, 2026-07-01 |
| D11 | COMS introduced occupies_temporal_region in July 2026. Earlier documentation describes the time to which a result applies; justification identifying that time as a temporal region occupied by the execution remains unresolved. | H, `Common OPs!35`; [changed assertion](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/coms-vs-pre-coms-legacy-diff.md:93); `491c258`, 2026-07-14 |
| D13 | inCondition links a capability or range specification to its environmental context without asserting ontological dependence between them. The incorrect historical property chain was removed. The current row supplies the SystemCapability-or-OperatingRange-or-SurvivalRange domain and does not assert a direct BFO/CCO relation mapping. | H, `System Capability!D15:F15`; chain removal `4b654f7`, 2026-07-01; [comparison](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/coms-vs-pre-coms-legacy-diff.md:153); domain introduction `491c258` |
| D14 | If an observation x qualityOfObservation y, then y is an information output produced by x that assesses the quality of the observation’s result. | H, `System Capability!F23` |
| D15 | The domain records the specifically dependent continuant and process-profile categories. isPropertyOf retains its source inverse relationship to hasProperty; the separate conditional rule handles the two cases without a global BFO subproperty inclusion. | H, `Common OPs!11,23`; [conditional mapping](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/ssn-hasproperty-rule-mapping-artifact.md:24); `17d94dc`, 2026-07-04 |
| D18 | The retained hosting interpretation uses role-mediated support. The bearer_of, has_realization, has_participant path entails hosts; the chain does not require a matching path for every asserted hosts edge. | H, `Common OPs!15`; [hosting analysis](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/isHostedBy-hosts-full-closure-analysis.md:100); `b464cea`, 2026-07-03 |
| D19 | This retained inverse-side hosting chain uses participates_in, realizes and inheres_in. A matching path entails isHostedBy; the chain does not require a matching path for every asserted isHostedBy edge. | H, `Common OPs!21`; [hosting analysis](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/isHostedBy-hosts-full-closure-analysis.md:100); `b464cea`, 2026-07-03 |
| D21, D22 | These rows supply source typing for the inverse of observes. The retained decision preserves the sensor-capability relation through source-native observes subPropertyOf ssn:forProperty, without a direct BFO/CCO relation mapping. | [Retained decision](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/observes-upper-mapping-decision.md:21); [source assertion](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/imports/ssn.ttl:166) |
| D23, D24 | These rows supply Sensor/ObservableProperty typing. The prior decision rejected the BFO has_participant inclusion and retained observes subPropertyOf ssn:forProperty, which remains asserted in the imported SSN source. | [Retained decision](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/observes-upper-mapping-decision.md:21); [source assertion](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/imports/ssn.ttl:166); `bdec6d9`, 2026-07-03 |
| D26, D27 | These rows retain Actuator-to-Actuation typing. The former agent_in inclusion was technically deferred with its inverse; technical deferral does not establish semantic rejection. The existing exact-closure evidence hold remains. | [Technical deferral](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/actuation-agent-property-mapping-deferral.md); [closure rerun](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/rerun-prior-clean-decisions-full-sosa.md); `bf0f97e`, 2026-07-09 |
| D28, D29 | These rows retain Actuation-to-Actuator typing. The former has_agent inclusion was technically deferred with its inverse; the source range was separately restored. The existing evidence hold remains without a final semantic rejection. | [Technical deferral](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/actuation-agent-property-mapping-deferral.md); [range restoration](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/madeByActuator-range-after-agent-deferral.md); `bf0f97e`, 2026-07-09; `59d68ce`, 2026-07-10 |
| D32, D33 | Documentary discrepancy: current COMS provides typing only, while the retained decision kept madeBySensor subPropertyOf cco:has_agent. Reconciliation remains unresolved; this note neither restores nor rejects the historical inclusion. | [Earlier retained pair](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/madeObservation-madeBySensor-agent-pair-full-closure-analysis.md:96); `854174b`, 2026-07-10; current rows `491c258`, 2026-07-14 |
| D34, D35 | Documentary discrepancy: current COMS provides typing only, while the retained decision kept madeObservation subPropertyOf cco:agent_in. Reconciliation remains unresolved; this note neither restores nor rejects the historical inclusion. | [Earlier retained pair](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/madeObservation-madeBySensor-agent-pair-full-closure-analysis.md:96); `854174b`, 2026-07-10; current rows `491c258`, 2026-07-14 |
| D36 | The retained intended semantics treat the observed property as an input to the Observation. Earlier OWL removal was a technical deferral that preserved those semantics. Current exact-closure validation remains a separate requirement. | [Preserved semantic intent](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/hermit-observedProperty-deferral-evaluation.md:5); `b21d1fa`, 2026-07-06; restoration `491c258`, 2026-07-14 |
| D37 | The documented intended dependence runs from the operating property object to the operating range subject. Therefore the selected forward target is specifically_depended_on_by, the inverse of specifically_depends_on. Historical technical deferral retained this intended semantics; COMS later restored the corrected direction. Historical scope and reasoner qualifications remain applicable to their original evidence. | H, `System Capability!E9:F9`, `0a99ef0`, 2026-07-05; [dependence direction](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/ssn-systems-dependence-reactivation-results.md:71); [scope](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/system-property-process-profile-scope-review.md:251); restoration `491c258` |
| D38, D39 | The former direct bearer_of mapping was deliberately replaced by domain-and-range coverage: ssn:System subjects and ssn-system:OperatingRange objects. These typing assertions do not by themselves assert a BFO/CCO relation edge. | Workbook/ontology change `c020298`, 2026-07-14, “Replace system bearer mappings with typing coverage”; current B38:C39 |
| D40 | The documented intended dependence runs from the survival property object to the survival range subject. Therefore the selected forward target is specifically_depended_on_by, the inverse of specifically_depends_on. Historical technical deferral retained this intended semantics; COMS later restored the corrected direction. Historical reasoner findings retain their original profile limitations. | H, `System Capability!E11:F11`, `0a99ef0`, 2026-07-05; [dependence direction](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/ssn-systems-dependence-reactivation-results.md:71); restoration `491c258` |
| D41, D42 | The former direct bearer_of mapping was deliberately replaced by domain-and-range coverage: ssn:System subjects and ssn-system:SurvivalRange objects. These typing assertions do not by themselves assert a BFO/CCO relation edge. | Workbook/ontology change `c020298`, 2026-07-14; current B41:C42 |
| D43, D44 | The former direct bearer_of mapping was deliberately replaced by domain-and-range coverage: ssn:System subjects and ssn-system:SystemCapability objects. These typing assertions do not by themselves assert a BFO/CCO relation edge. | Workbook/ontology change `c020298`, 2026-07-14; current B43:C44 |
| D45 | The documented intended dependence runs from the system property object to the system capability subject. Therefore the selected forward target is specifically_depended_on_by, the inverse of specifically_depends_on. Historical technical deferral retained this intended semantics; COMS later restored the corrected direction. Historical scope and reasoner qualifications remain applicable to their original evidence. | H, `System Capability!E14:F14`, `c0be300`, 2026-07-05; [dependence direction](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/ssn-systems-dependence-reactivation-results.md:71); [scope](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/system-property-process-profile-scope-review.md:229); restoration `491c258` |
| D46 | The retained interpretation states that the Platform on which Systems are deployed participates in the Deployment. This row preserves that has_participant inclusion and its documented inverse-side consequences. | H, `Common OPs!3`; [inverse policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md:37); `8512004`, 2026-07-11 |
| D47 | The retained interpretation states that the deployed System participates in its Deployment. This row preserves that has_participant inclusion and its documented inverse-side consequences. | H, `Common OPs!4`; [inverse policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md:37); `8512004`, 2026-07-11 |
| D48 | The retained interpretation treats a detected Stimulus as causally triggering a response in the Sensor. The Sensor is therefore represented as affected by the Stimulus, preserving the existing is_affected_by inclusion. | H, `Common OPs!5`; [change history](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/all-mapping-changes-and-rationales.md:154); `8512004` and `a6b8037`, 2026-07-11 |
| D49 | Documentary discrepancy: current COMS asserts the described_by followed by is_about chain, while retained human review explicitly rejected that chain. Reconciliation remains unresolved; this note does not choose either mapping version. | [Explicit rejection](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/mapping-consistency-resolution-plan.md:66); `38cb960`, 2026-07-01; current chain `491c258`, 2026-07-14 |
| D55 | The range records specifically dependent continuants and process profiles. The separate conditional rule produces bearer_of or has_occurrent_part from suitable endpoint typing, avoiding an unconditional dual BFO subproperty mapping. | [Conditional interpretation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/ssn-hasproperty-rule-mapping-artifact.md:24); [rule](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/rules/ssn-hasproperty-conditional-mapping.rq:29); `17d94dc`, 2026-07-04 |
| D57 | Documentary discrepancy: current COMS asserts implementedBy subPropertyOf prescribes. The retained earlier mapping instead used prescribes followed by has_agent to entail implementedBy. Reconciliation of these different commitments remains unresolved. | H, `Common OPs!16`; [history](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/all-mapping-changes-and-rationales.md:152); chain `b464cea`, 2026-07-03; direct inclusion `491c258`, 2026-07-14 |
| D58 | Documentary discrepancy: current COMS asserts implements subPropertyOf prescribed_by. The retained earlier interpretation was the inverse of a process-mediated implementedBy mapping. Reconciliation of the direct and mediated commitments remains unresolved. | H, `Common OPs!16–17`; [history](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/all-mapping-changes-and-rationales.md:152); `b464cea`; `491c258` |
| D60, D61 | These rows retain source typing for the Stimulus-to-Property proxy relation. Historical documentation describes an information-mediated interpretation without adopting an unconditional direct BFO/CCO relation mapping for isProxyFor. | H, `Common OPs!24`; [history](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/all-mapping-changes-and-rationales.md:155); `8512004` and `a6b8037`, 2026-07-11 |
| D62 | The retained interpretation treats the originating Stimulus as an occurrent that causally initiates the Observation process. This row preserves the corresponding process_started_by inclusion. | H, `Common OPs!37`; [history](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/all-mapping-changes-and-rationales.md:156); `8512004` and `a6b8037`, 2026-07-11 |

### Sheet2: existing final-assessment rationale copies

Each following value is copied exactly from the corresponding `rationale` in the [current assessment artifact](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/mappings/current-ssn-sosa-assessment.json).

| Destination | Exact proposed value | Retained supporting evidence |
|---|---|---|
| D5 | The existing pair review retains the actuation-to-affected-property mapping and its inverse; the current inclusion records the effect relation without asserting property equivalence. | [actsOnProperty pair review](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/isActedOnBy-actsOnProperty-full-closure-analysis.md) |
| D8 | The existing pair review documents results as outputs of observations, actuations, or samplings and retains the process-to-output direction. The current direct mapping is unchanged; historical HermiT results are not promoted to current evidence. | [hasResult pair review](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/isResultOf-hasResult-full-closure-analysis.md) |
| D12 | The existing review treats use of a Procedure as being carried out according to its prescriptions and explicitly recommends the now-adopted cco:prescribed_by inclusion. | [Straightforward-property review](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/straightforward-op-mapping-candidates-review.md) |
| D20 | The explicit inverse-side policy retains the inverse affects mapping. The current source and CCO inverse pairs preserve this direction without an equivalence commitment. | [Inverse-side policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md) |
| D25 | The explicit inverse-side policy retains this inverse output mapping. Current source hasResult/isResultOf and target has_output/is_output_of inverse pairs supply the same consequence. | [Inverse-side policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md) |
| D30 | The existing sampling-pair review retains the Sampling-to-Sampler has_agent mapping. This documents the active relation between an actual sampling and its sampler; it does not decide whether every sampler must actually sample. | [Sampling-pair review](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/madeSampling-madeBySampler-full-closure-analysis.md) |
| D31 | The explicit inverse-side policy retains this inverse agent mapping, supported by source madeBySampler/madeSampling and target has_agent/agent_in inverse pairs. | [Inverse-side policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md) |
| D50 | The explicit inverse-side policy retains participation in a Deployment as the inverse of deployedSystem under has_participant. The current assertion exactly preserves that decision. | [Inverse-side policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md) |
| D51, D52 | The recorded decision rejects cco:has_input for a Procedure-to-Input relation; the current workbook retains only its source domain/range. This is semantic rejection of that process-input superproperty, not a pending implementation. | [Input/output rejection](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/input-output-cco-mapping-rationale-cleanup.md) |
| D53, D54 | The recorded decision rejects cco:has_output for a Procedure-to-Output relation; the current workbook retains only its source domain/range. This is semantic rejection of that process-output superproperty, not a pending implementation. | [Input/output rejection](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/input-output-cco-mapping-rationale-cleanup.md) |
| D56 | The existing review identifies subsystems as structural components and explicitly recommends the now-adopted continuant-parthood inclusion. It asserts only the necessary direction. | [Straightforward-property review](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/straightforward-op-mapping-candidates-review.md) |
| D59 | The explicit inverse-side policy retains participation in a Deployment as the inverse of deployedOnPlatform under has_participant. The current assertion exactly preserves that decision. | [Inverse-side policy](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/inverse-side-direct-mapping-policy-review.md) |

### Sheet2!D16 and D17: approved sample rationales

The exact assignment is **the complete JSON `rationale` string, preserving its text and paragraph breaks, with no prefix, suffix, or paraphrase**:

| Destination | Exact value source | Verified record SHA-256 |
|---|---|---|
| Sheet2!D16 | [`hasSample.json`, key `rationale`](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/current-human-decisions/2026-10-25-sample-pair/hasSample.json) | `e5c7d7f313c69ff291b32e69c0fd4ba8c593edbcad6fdac5f6f86efda6a7839f` |
| Sheet2!D17 | [`isSampleOf.json`, key `rationale`](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/current-human-decisions/2026-10-25-sample-pair/isSampleOf.json) | `03d5e3396de3c85a121361085b8dd2dd28bce3d1a60b06df75fac60f78f84ba2` |

These are exact copy specifications, not requests to draft new rationales. Both strings already match their assessment records.

Both records retain:

- `reviewer_identity: "Alec Sculley"`
- `review_state: "final"`
- `assessment_outcome: "no_direct_mapping"`
- Their existing evidence, RowIDs, decision IDs and review snapshots.

The remaining workbook defect is the outdated D text. **B16, C16, B17 and C17 are complete as deliberate blanks.** No new mapping axiom follows from this documentary completion.

## 7. Distinctions preserved

This audit applies all seven distinctions explicitly:

- An existing semantic decision does **not** require a new decision merely to document it.
- A missing rationale does **not** establish a missing semantic decision.
- An `unreviewed` assessment flag does **not** establish that the term was historically undecided.
- A technical deferral does **not** establish semantic rejection.
- A SKOS documentary correspondence does **not** constitute an OWL mapping.
- A historical/current discrepancy does **not** authorize restoration of the historical assertion.
- A deliberate no-direct blank does **not** make the mapping row incomplete.

The 61 historical decisions are therefore documentary evidence for 69 rows, without a new ratification requirement.

## 8. Concrete dependency before a write task

The proposed content is semantically safe, but **the current validation machinery does not treat an XLSX rationale edit as custody-neutral**.

[`decision_input_hashes()`](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/tools/current_assessment.py:108) binds each sample decision to the **entire workbook hash**. [Decision validation](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/tools/current_assessment.py:156) rejects a changed hash, and [packet comparison](/Users/alecsculley/Documents/GitHub/SSN-to-BFO/tools/current_assessment.py:176) also reconstructs a packet containing existing reasoning.

Consequently, even editing an unrelated D cell would invalidate those existing input bindings under the present checks. Editing D16/D17 additionally changes the reconstructed packet prose. I found no existing documentary-only rebinding mechanism.

This is a **validation/custody dependency**, not a reason to reopen the approved semantics or demand new approval of the 61 historical decisions. The next write task must account for it while preserving the approved records and their historical evidence. This audit does not claim that the 104 edits can pass the existing checks with all bindings left unchanged.

## 9. Requested totals

1. **Total authoritative workbook rows: 105** — 44 in Sheet1 and 61 in Sheet2.
2. **Rows with no missing or incomplete documentary fields: 0** under this publication-documentation audit: 102 blank explanations, two outdated explanations, one ambiguous explanation.
3. **Rows with safely fillable documentary fields: 104.**
4. **Safe field assignments proposed: 104** — 102 blank fills and two exact approved-rationale replacements.
5. **Deliberate blanks: 4 cells in 2 rows** — Sheet2 B16/C16 and B17/C17.
6. **Ambiguous documentary fields: 1** — Sheet1 D6.
7. **Fields whose conclusive rationale requires semantic resolution: 13** — four genuinely unresolved cases and nine row-level historical/current discrepancies. Of these, **nine require reconciliation of conflicting retained/current commitments**; four require the still-open substantive judgment. D6 is counted separately as documentary ambiguity first.
8. **Evidence-held fields: 6** across four terms. Supported hold notes can still be populated in those cells.
9. **Exact column to populate next: D, `coms:Reasoning`, on both sheets.**
10. **Genuinely necessary new workbook columns: 0 established.** Assessment, reviewer, identity, publication metadata and product disposition already have separate repository authorities.

The semantic-resolution and evidence-hold counts overlap the safely fillable neutral-note set; they are **not additional missing cells**. Assessment counts remain **14 final, 0 deferred, 77 unreviewed/unresolved; 10 formal mappings adopted, 4 no direct mapping, 0 inheritance sufficient**.

## SAFE WRITE PLAN

- Populate **`Sheet1!D2:D5`** with the exact corresponding values in section 6.
- Populate **`Sheet1!D7:D45`** with the exact corresponding values in section 6.
- Populate **`Sheet2!D2:D15`** with the exact corresponding values in section 6.
- Replace **`Sheet2!D16`** with the complete, unmodified `rationale` string from the existing approved `hasSample.json`.
- Replace **`Sheet2!D17`** with the complete, unmodified `rationale` string from the existing approved `isSampleOf.json`.
- Populate **`Sheet2!D18:D62`** with the exact corresponding values in section 6.
