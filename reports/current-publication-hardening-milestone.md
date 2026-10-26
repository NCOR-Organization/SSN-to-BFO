# Current SSN/SOSA publication-hardening milestone

This checkpoint preserves current-track publication hardening, human-review and semantic-evidence custody guards, documentary workbook evolution, the two approved sample-pair decisions, 104 completed `coms:Reasoning` cells, and associated reports, tests and documentation. No new semantic decisions were made during checkpoint preparation.

- Branch: `publication/current-sosa-readiness`
- Pre-commit HEAD: `c3f9b05593727bd13854bf1830cc09b4a653b41f`
- Authoritative workbook: `mappings/SSN2BFO-COMS.xlsx`
- Workbook SHA-256: `9e526e5705fc84571e03616f74c59fe8654fcc073a1c45a281109cf22c276e14`
- A/B/C/E semantic projection SHA-256: `d42340112492fa033216870de64848d899ffd39041be013b7ecc1b655d68136b`
- Documentary transition: `5f0e3bc5-b52e-4502-8fd5-f7f1c182913b`

Exactly 104 reasoning cells retain their previously audited completion values. `Sheet1!D6`, all A/B/C/E values, sheet and row order, and 105 RowIDs remain unchanged. The workbook matches its retained transition snapshot. The historical workbook SHA-256 remains `e32c6b5691bf4aa00b4ec564731e0364edc2567658bb21c46f83c1e3f0d9a4f6`.

Assessment remains at 91 source terms: **14 final, 0 deferred, 77 unreviewed and unresolved; 10 formal_mapping_adopted, 4 no_direct_mapping, and 0 inheritance_sufficient**. Unresolved membership is unchanged.

The approved `sosa:hasSample` and `sosa:isSampleOf` decisions remain **final / no_direct_mapping**, reviewed by **Alec Sculley**. `Sheet2!B16/C16` and `Sheet2!B17/C17` remain blank; no mapping axiom was added. Both decision records, seven immutable evidence files and the historical workbook snapshot remain intact. The documentary transition chain validates.

All four current logical mapping products retain their validated hashes. The mapping rule, source and target ontologies, SOSA-2023 protected artifacts, historical authorities, protected local COMS architecture, and 55 tracked external COMS files are preserved. No semantic mapping changes occurred beyond the two already-approved sample-pair no-direct decisions.

## Fresh pre-commit validation

| Suite | Tests | Result |
|---|---:|---|
| Publication hardening | 195 | PASS |
| Documentary guard | 33 | PASS |
| COMS integration | 128 | PASS |
| SOSA-2023 non-regression | 44 | PASS |
| Total | 400 | PASS |

Assessment validation, source identity, generation/freshness (`--check-only`), preservation, documentary chain, in-memory compilation of 110 Python files, and `git diff --check` all passed. Every command preserved its 239 input hashes and the pre-commit HEAD. No expensive unrelated RO reasoning was run.

The [checkpoint audit](current-publication-checkpoint-audit.json) records the initial Git inventory, individual classification and hashes for all 561 existing candidate files, verified test commands/results, and excluded runtime artifacts. This report and that audit are the two added checkpoint records. A narrowly scoped `.gitattributes` update preserves terminal blank lines in exactly two retained raw logs: `final-mechanical-final-semantic_stored_consistency.log` and `package-cli-diagnostic.log`, both under `reports/current-publication-validation/`. Their hash-bound bytes are unchanged; only `blank-at-eof` checking is exempted for those exact paths. Other whitespace checks remain active. This attributes change does not affect the 239 validated inputs. Only intended milestone files are eligible for staging. Final staging verification and `git diff --cached --check` are required before the checkpoint commit.

Historical baseline and execution-evidence bindings retain their original HEADs, timestamps, hashes and eligibility labels when the checkpoint advances HEAD. These pre-commit tests validate the recorded bytes; committing does not promote historical blocked diagnostics into successful current publication evidence.

## Remaining exceptions

**Documentary ambiguity:**

- sosa:FeatureOfInterest

**Genuine provisional questions:**

- sampling:SampleRelationship
- sampling:hasSampleRelationship
- sampling:relatedSample
- sosa:phenomenonTime

**Reconciliation cases:**

- sosa:madeBySensor
- sosa:madeObservation
- ssn:forProperty
- ssn:implementedBy
- ssn:implements
- ssn-system:MeasurementRange
- ssn-system:SystemProperty

**Evidence holds:**

- sampling:RelationshipNature
- sampling:natureOfRelationship
- sosa:madeActuation
- sosa:madeByActuator

Broader publication/runtime/profile/full-gate blockers remain. This checkpoint is not a release or a declaration of publication readiness.
