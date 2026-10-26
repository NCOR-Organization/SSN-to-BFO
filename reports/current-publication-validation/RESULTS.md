# Earlier mechanical repair validation — historical

**Superseded gate-completion claims:** the final independent audit found schema downgrade and retry archive defects. The follow-up repair and fresh bounded verification are recorded in [the final trust-repair report](../current-publication-final-trust-repair.md) and [gate-defect validation ledger](gate-defect-validation.json). Older logs below retain their original scope and do not certify current execution custody or publication readiness.

The independent human-review-gate audit subsequently found that copied reasoner stdout could satisfy a different required execution after mutable hashes were refreshed, and that two final assessment outcomes lacked bound decision evidence. The test counts below describe the earlier candidate; they do not establish that its mechanical trust gates were complete. See [the final trust-repair report](../current-publication-final-trust-repair.md) for the corrective milestone.

The final frozen candidate passed **119 focused + 128 affected COMS integration + 44 SOSA-2023 non-regression tests = 291 tests**. Compilation, whitespace, assessment, identity, generation freshness, SOSA source/product and preservation checks passed. Accepted commands have matching current HEAD/input bindings and zero drift. See [commands.json](commands.json) and the `final-mechanical-final-` command/log pairs.

Stored semantic execution-slot and raw-evidence consistency passes. The publication semantic check exits **1**, correctly retaining import/profile, historical execution freshness, conservativity, exact-example and human-expectation blockers. No current production reasoning success or publication readiness is claimed.

Cross-role, cross-example, cross-phase, raw-role, closure/input/graph, query/test, helper-mode and output-artifact substitutions are rejected; honest blocked and distinct valid fixtures pass. The earlier A–K guards remain passing. Review packet tests cover incoming restrictions, inverse/symmetric relationships, grouped and target incoming disjointness, and source/target/mapping chains.

The independent re-audit had invalidated the earlier claim of complete mechanical repair. This milestone adds the missing execution/output bindings and material packet facts, and is ready only for independent human-review-gate re-audit. [Repair report](../current-publication-guard-repair.md).

The earlier executions below remain historical evidence, with their original failures and scope. They are not the final candidate command ledger. The exact previous ledger is retained in [final-mechanical-prior-commands.json](final-mechanical-prior-commands.json).

---

# Current publication validation results

Full discovery and make check were attempted; full PASS is not claimed. Stable discovery ran 621 tests with 5 failures and 2 errors: three fingerprint failures were subsequently corrected and all 25 affected tests passed; the unresolved results are one missing-SKOS query failure and three incomplete RO validations (one failure and two errors). Fourteen package tests were not entered because package setUpClass could not complete. The final make check result is retained independently; its command record discloses the explanatory manifest edit during execution, with an unchanged executable query/ontology payload. One earlier temporary SOSA-2023 candidate recorded all four HermiT products PASS; repeated expensive RO runs were bounded externally and remain incomplete, not semantic inconsistencies. A final read-only audit also corrected three inaccurate target descriptions in unapproved expectation motivations; queries, premises, approval states and mappings were unchanged, and focused tests plus exact semantic diagnostics were rerun. Installed Oracle Java 22 differs from declared Temurin 22.

| Executed check | Exit | Result/log |
|---|---:|---|
| unit_tests | 1 | [unit_tests_final.log](unit_tests_final.log) |
| source_identity | 0 | [source_identity.log](source_identity.log) |
| assessment | 0 | [assessment.log](assessment.log) |
| generation_freshness | 0 | [generation_freshness.log](generation_freshness.log) |
| sosa_source_version | 0 | [sosa_source_version.log](sosa_source_version.log) |
| sosa_products | 0 | [sosa_products.log](sosa_products.log) |
| static_checks | 0 | [static_checks.log](static_checks.log) |
| full_repository_gate | 2 | [full_repository_gate_final.log](full_repository_gate_final.log) |
| whitespace | 0 | [whitespace.log](whitespace.log) |
| dependency_check | 0 | [dependency_check.log](dependency_check.log) |
| current_focused_tests | 0 | [current_focused_final.log](current_focused_final.log) |
| coms-framework-fingerprint-rerun | 0 | [coms-framework-fingerprint-rerun.log](coms-framework-fingerprint-rerun.log) |
| post-audit-focused | 0 | [post-audit-focused.log](post-audit-focused.log) |

## Unit output summaries

- Stable discovery before fingerprint correction: Ran 621 tests in 2198.299s; FAILED (failures=5, errors=2)
- Affected fingerprint tests after correction: Ran 25 tests in 19.212s; OK
- New focused regressions: Ran 56 tests in 30.598s; OK
- Post-audit focused regressions: Ran 56 tests in 29.471s; OK
- Earlier in-flight discovery: Ran 619 tests in 2466.120s; FAILED (failures=5, errors=3)

## Final full-gate result

`make check` exited **2** at SOSA-2023 release-package validation. Its repeated RO HermiT process was externally stopped after **5 minutes 3 seconds** (planned cap: 300 seconds), producing process exit **143** and a package `setUpClass` error. Earlier gate phases passed, including the 56 current tests, canonical identity, all 25 corrected COMS integration tests, and SOSA-next product/metadata checks. Later gate phases were not run. This is incomplete runtime validation, not an ontology inconsistency.

## Evidence interpretation

- The final candidate snapshot contains 186 declared validation inputs. Complete hashes, command snapshots, and log hashes are in [commands.json](commands.json). No dependency was installed or changed.
- This is composite evidence: the post-audit focused run uses the final snapshot; the full-gate attempt and affected 25-test rerun predate a correction to three explanatory motivation strings in the unapproved expectation manifest. The gate record discloses any in-flight edit. Stable discovery and the earlier focused run also predate the subsequently corrected fingerprint test file. Query structure, premises, expected polarities and approval states did not change; exact semantic diagnostics were refreshed afterward. Original failed logs and snapshots have not been rewritten as passing evidence. The earlier in-flight sequence is retained in [initial-command-sequence.json](initial-command-sequence.json).
- The three corrected assertions concerned the intentionally modified current generator and its two reports. Ontology/workbook/COMS architecture constants were unchanged. The original current-package subprocess error did not recur in the stable discovery; its truncated earlier traceback does not establish a cause.
- The isolated [query-equivalence diagnostic](query-equivalence-diagnostic.log) identifies `UnloadableImportException` for `http://www.w3.org/2004/02/skos/core`. RDFLib returns 91 scoped source terms; the separate unmapped query returns the expected 2 rows. This is an unresolved local import dependency, not evidence for a changed mapping.
- The first temporary SOSA-2023 candidate recorded HermiT PASS for integrated/strict-BFO/CCO-extension/RO closures of 15,243 / 15,120 / 15,254 / 12,864 triples. Its [manifest](initial-sosa-2023-first-candidate-manifest.json) is a diagnostic copy of a synthetic test artifact; [the accompanying note](initial-sosa-2023-first-candidate-note.json) explains why it does not certify the entire package test.
- Runtime caps are external operational limits. Saved closure bytes, hashes, commands, actual observed elapsed times and signals are retained for capped attempts. Some observations exceeded the planned 300-second cap; no exact-deadline claim is made. A capped attempt is NOT COMPLETED, not a semantic inconsistency. No ontology or dependency was altered to make a check pass.
- The final repository gate stopped where [its output](full_repository_gate_final.log) records failure; later gate phases were not executed. Separate discovery/focused commands provide only their own recorded coverage. Final-gate command, closure snapshots and any operational cap are in [its command record](full_repository_gate_final.command.json).
- The exact current-track semantic run is separately retained in [the semantic report](../current-ssn-sosa-semantic-validation.md). Its import/profile blockers are not replaced by older normalized or RDFS smoke results. Proposed semantic expectations remain unapproved and are not publication evidence.
- No full-suite or intended-environment PASS is asserted. Repeat complete validation with the reviewed local closure/import solution, adequate reasoning runtime, and declared Temurin 22 environment.

The candidate remains uncommitted. An independent read-only audit is recommended.
