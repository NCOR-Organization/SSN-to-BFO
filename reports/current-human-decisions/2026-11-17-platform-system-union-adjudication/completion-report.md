# Platform/System union adjudication — completion report

Baseline: `3376e1c74e846e40e6863ec8b1f1c255349aa2d3`; branch: `publication/current-sosa-readiness`.

The two approved union mappings are implemented. They retain `owl:equivalentClass`, their existing RowIDs, and their existential witnesses. This is an approved semantic revision, not a syntax repair or a new interpretation selected by the implementer. Nothing is staged, committed, tagged, pushed, or released.

## Exact workbook and assessment changes

Only `Sheet1!C9`, `D9`, `C36`, and `D36` changed relative to the preserved intermediate Platform adjudication. The predicates, RowIDs, other workbook cells, and formatting are unchanged. Exact prior and replacement rationale text is preserved in [changes.json](validation/changes.json); original HEAD and intermediate assertions and history are preserved in [before-after.json](before-after.json).

| Term | RowID | Final target expression |
| --- | --- | --- |
| `sosa:Platform` | `urn:uuid:b4508c03-1b79-4f53-b525-d5db6d80c7cb` | `(bfo:MaterialEntity or cco:InformationContentEntity) and (sosa:hosts some ssn:System)` |
| `ssn:System` | `urn:uuid:66010702-8134-4e08-a972-f0767ec8dead` | `(bfo:MaterialEntity or cco:InformationContentEntity) and (ssn:implements some sosa:Procedure)` |

Both records are `final / formal_mapping_adopted`, reviewed by Alec Sculley. Counts: **91 terms; 108 rows; 102 mapping assertions; six deliberate blanks; 25 final; 66 unreviewed/unresolved; zero deferred; 18 formal mappings, five no-direct-mapping outcomes, two inheritance-sufficient outcomes.** The other 89 assessment records remain unchanged. Relative to HEAD, Platform and System become final; relative to the intermediate state, only System adds a final assessment, while Platform receives a superseding decision.

The rationale cells explain the adopted exhaustive union, ICE/bearer distinction, direct source relations on appropriate ICEs, necessary witnesses, source-supported converses, and intentional exclusion of Sites and continuants outside the union. They do not present the exhaustive union or existence commitments as entailments of the source definitions or DUL alignment.

## Decision provenance and preservation

- New Platform decision: `urn:uuid:5f5f7444-692c-445a-8ada-c22d5c83efc7`, [Platform.json](Platform.json).
- New System decision: `urn:uuid:110fc48f-862b-4d7a-834e-9047ce8341e8`, [System.json](System.json).
- Earlier approved Platform Continuant decision: `urn:uuid:160e16e0-eedf-4dde-b3be-0ee5deddd9cc`, retained byte-identically in [the preceding adjudication](../2026-11-17-platform-adjudication/Platform.json). It is explicitly superseded, not deleted or represented as never approved.
- Semantic transition: `94598afb-94dd-4888-b7cc-402c6ba742a6`, in the existing semantic-workbook transition directory.
- Workbook archive: `0f1ad87f3b48f0001bbe157d83f1a33447348c094a016cc2276730a10103ee5b.xlsx`, in the existing semantic-workbook versions directory.

The existing authentication schema requires an unresolved predecision anchor. Platform's new record truthfully uses its original historical unresolved anchor and separately binds its immediate final predecessor and superseded decision. It does not fabricate an unreviewed current state. [assessment-before.json](assessment-before.json) preserves the actual immediate state: final Platform and unreviewed System. Original material-only assertions/rationales, intermediate Continuant approval, previous workbook versions, and RowID-linked history remain available. All hash-bound references resolve.

## Logical delta and generated products

Against HEAD, exactly two equivalence axioms are replaced: each original MaterialEntity conjunct becomes `(MaterialEntity or InformationContentEntity)`. Against the intermediate state, Platform's Continuant conjunct narrows to the explicit union, while System's MaterialEntity conjunct broadens to it. No other integrated mapping assertion changes. The respective hosting and implementation restrictions remain intact.

The established generator moves these two now-mixed BFO/CCO expressions from the strict BFO product to the CCO extension. This is deterministic partitioning of the approved expressions, not two extra mappings. Core remains 32 assertions; strict BFO changes 19 to 17; CCO extension changes 51 to 53; total remains 102. The alignment core is byte-identical. The strict-BFO-only product no longer supplies these two direct class correspondences; consumers need the integrated product or the CCO extension with its imports for the approved unions. See [logical-delta.json](validation/focused/logical-delta.json) and [generation-counts.json](validation/focused/generation-counts.json).

| Maintained product | SHA-256 |
| --- | --- |
| `SSN2BFO.ttl` | `b78c7fde8d73c167ed2808947b4be2fdbdbe1ab8f9bb3a71c67725ccb6a89401` |
| `ssn-sosa-alignment-core.ttl` | `cb5a7d89b0a54cd3a0bbf0b7644d0e8b0ab8c77f8878e7d9fc0e29de5b7a4ee5` |
| `ssn-sosa-bfo-mapping.ttl` | `a00acdc8eb2c78b3b91847f104298bf51dc089ec21b2d7661a0396848eee3243` |
| `ssn-sosa-cco-extension.ttl` | `1dce64184c4b2c4b5cba84cf576fb1d0a6538eeaa8291f7d3faa52972d806e49` |

## Satisfiability and entailments

All four maintained products pass fresh OWL 2 DL/HermiT checks with zero named unsatisfiable classes. A fresh replay against the actual generated integrated product passes **58 candidate expectations, four native-source expectations, and the distinct-individual nested-Platform ABox**. See [focused validation](validation/focused/README.md), including a portable replay command. The 263 answers in retained earlier comparison evidence are not represented as 263 fresh candidate tests.

| Tested combination or inference | Result |
| --- | --- |
| Material or ICE Platform; material or ICE System | Satisfiable |
| ICE System implementing a Procedure | Satisfiable; no forced material classification |
| A Platform hosting another explicitly distinct ICE Platform | Consistent; the hosted Platform is also a System under the unchanged source restriction |
| Platform without a hosted System; System without an implemented Procedure | Unsatisfiable, preserving the required witnesses |
| Platform/System as Site, spatial region, other immaterial independent continuant, specifically dependent continuant, or occurrent | Unsatisfiable, as intended by the exhaustive union and BFO distinctions |
| Source-only converse: hosting a System implies Platform; implementing a Procedure implies System | Entailed from inverse relations and class-local universal restrictions |
| Source alone entails either existential witness | Not entailed; necessity remains an adopted mapping commitment |
| System also classified as Procedure | Satisfiable; not a forced identity |

A supplemental fresh ABox explicitly types both outer and inner individuals as Platform and ICE, asserts `outer hosts inner`, and declares them different. It passes OWL 2 DL and HermiT consistency under the exact installed integrated product and pinned closure. This strengthens the earlier nested-Platform evidence without altering its original record. See [supplemental result](validation/focused/distinct-ice-platforms/results/summary.json); its adjacent driver and probe provide a portable replay.

The source-supported converses also make the exclusions relevant to relationship assertions: a Site hosting a System would be inferred to be a Platform and therefore conflict with the union; an excluded continuant implementing a Procedure would likewise be inferred to be a System. Explicit Platform/System type assertions are not required for these consequences. This follows from the tested converse entailments and exclusion checks.

The following inherited limitations remain and were not repaired:

- **ICE Sensor, Actuator, or Sampler is unsatisfiable** under their unchanged MaterialEntity and bearer-of mappings. Generic informational Systems are allowed; these specialized combinations remain prohibited.
- **ICE System linked by `hasSystemCapability` to a SystemCapability is unsatisfiable.** Existing `hasProperty`/`isPropertyOf` and FeatureOfInterest classification impose a conflicting type. An ICE System bearing a Function is also unsatisfiable.
- **Mixed material/ICE subsystem relationships are unsatisfiable** under the retained BFO mereology. ICE-to-ICE subsystem relationships are satisfiable.
- **ICE System participating as `agent_in` a Process is formally satisfiable** with the pinned participation-domain axioms; adding CCO Agent typing would introduce its separate material commitment.
- The informational branch requires CCO ICE, including its pinned aboutness conditions. It does not admit every generically dependent continuant or identify information with its physical bearer.

These are specific incompatible combinations, not newly unsatisfiable named ontology classes. They are retained limitations of related mappings, not evidence that the union ontology as a whole is inconsistent.

## Authentication, freshness, and generation

Decision authentication, applicability, semantic history, assessment-report freshness, and deterministic generation pass. Fresh generation is byte-deterministic; generated mappings match the authoritative workbook. Retained logs are under `validation/`; [independent-governance-reference-audit.json](validation/independent-governance-reference-audit.json) verifies reference hashes and preservation. The installed files match the focused-validated candidate exactly.

## Complete gate comparisons — not passing

`make check` was executed and **did not pass**: 488 tests, 25 failures, 22 errors, seven skips, exit code 2. Both HEAD and the intermediate Platform-only state had 24 failures and 22 errors. Against either comparison state, all 47 candidate diagnostics are accounted for: **39 identical preexisting diagnostics, seven changed preexisting diagnostics attributable to approved data, and one newly failing stale assessment-count fixture** (25 actual final assessments versus 24 expected). No unexplained regression was demonstrated.

The separate mapping-integrity suites also **did not pass**: 165 tests, 18 failures and one setup error. HEAD had 13 failures and one setup error; the intermediate state had 16 failures and one setup error. Against HEAD, the 19 diagnostics comprise six equivalent preexisting diagnostics (five exact and one differing only in set display order), eight changed preexisting approved-data diagnostics, and five newly failing approved-data fixtures. Against the intermediate state, they comprise six equivalent preexisting diagnostics, eleven changed approved-data diagnostics, and two newly failing approved-data fixtures. The obsolete fixtures are identified below; none was modified or waived.

These are **66 diagnostic records across two scopes**, not 66 independent defects. There are no duplicate test IDs across the scopes, but some share causes. For example, the canonical cross-track preservation test and the integrity alignment-core preservation test both retain an obsolete core digest even though the actual core is unchanged. Eleven CCO test methods were blocked by the setup error. The standalone documentary-chain check retains the identical baseline `disconnected documentary update chain` failure; it is separately disclosed, not presented as an extra independent unit-test defect.

Only the canonical Turtle parse step and current-publication regression step executed. The subsequent **44 conditional stages, compilation check, and Makefile tail were not reached**. Separately passing focused checks do not make the canonical gate pass. No commit-only exception or release waiver is granted by this report.

The completed gate applies to the isolated selected candidate: all 1,101 role inputs match the final candidate and their corresponding main-tree bytes. The broader frozen checkout manifest has 2,037 files; it is not the 1,101-input role scope. The main tree has one additional role input, the preexisting excluded Excel lock `mappings/~$SSN2BFO-COMS.xlsx`, preserved unchanged and not copied into the test checkout. This report does not claim that the literal dirty-main 1,102-input scope was tested.

Exact cases, classifications, raw output, blocked/unreached stages, input preservation, and reused evidence are retained in [canonical comparison](validation/gates/canonical-gate-comparison.json), [integrity comparison](validation/gates/mapping-integrity-comparison.json), [exception inventory](validation/gates/exception-inventory.json), [input-scope qualification](validation/gates/final-source-scope-equivalence.json), and [retention manifest](validation/gates/retention-manifest.json).

## Outdated expectations identified, not changed

The three strict-product expectations already failing in the intermediate Platform state remain outdated: `RawStrictBfoGuardTests.test_current_context_preserves_baseline_strict_axioms_and_bytes` assumes current strict bytes equal HEAD; `StrictBfoMappingTests.test_exact_selection_identity_lock_and_distribution` assumes the former 19-row selection; `test_processed_row_and_audit_order_do_not_affect_strict_bfo_output` locks the former serialization digest, but the current run stops first at its outdated 19-row expectation (`tests/test_strict_bfo_mapping.py:515`), before reaching the digest assertion at line 527. The unions require a 17-row strict product, with both approved expressions in the CCO extension.

Two additional integrity fixtures now fail: the mocked validator in `ComsAuthorityMigrationTests.test_first_successful_update_creates_initially_absent_strict_bfo_mapping` requires 134 total triples (`tests/test_generate_mapping_from_coms.py:2713`), while the new product has 114; `StrictBfoMappingTests.test_direct_graph_identity_import_counts_and_structures` requires 125 logical triples (`tests/test_strict_bfo_mapping.py:401`), while it now has 105. These are test expectations, not production-validator requirements. Assertions after the failing assertion were not reached and are not represented as passing.

The unchanged `CurrentAssessmentTests.test_historical_final_baseline_is_exact_and_fixed` later-decision cohort omits the newly approved System final, so its derived expectation is 24 while the current count is 25. Its original historical twelve-record integrity checks are preserved. Other occurrences of these numbers in deliberately historical fixtures have not been assumed stale merely because they contain the same literals. No test correction is included in this union amendment.

## Whitespace finding

A separate new formatting diagnostic is confined to the final blank line of `approved-instructions.txt`: `new blank line at EOF` (line 75). It is not a baseline test failure or a semantic defect. The capture is already hash-bound by the archived decision records and semantic transition. Existing immutable-evidence rules prohibit overwriting those archived bindings; the bytes have been preserved and the finding disclosed. No whitespace exemption is claimed or requested by this implementation task. See [instruction-eof-dependency-review.json](validation/instruction-eof-dependency-review.json).

## Final preservation and scope

The final [file inventory](validation/file-inventory.json) records **14 modified files relative to the initial intermediate Platform state and 81 added union-task files**, including this completion report and its inventory. The 81 files contain authority/history records, the archived workbook and transition, and selected validation evidence; completed prior evidence is reused by reference rather than recopied. The earlier 104 untracked Platform-task files and all 178 excluded files (the original 175 plus three omitted redundant Deployment captures) remain byte-identical.

Git status relative to HEAD is **15 modified tracked files, 363 untracked files, and zero staged files**. The untracked files comprise 104 preserved prior task files, 81 union-task files, and 178 excluded files. The fifteenth tracked modification is the preexisting authorized Platform assessment-count test edit, preserved unchanged; the union amendment changes no test. The index entries, branch, and HEAD remain unchanged.

All other tracked bytes, all 89 unrelated assessment records, pinned source/import files, and SOSA-2023 artifacts remain unchanged. Exact original and intermediate workbook states, rationale text, and prior approval remain preserved. Post-installation main-tree assessment freshness, semantic-history authentication, and generation/mapping-integrity checks pass and match the validated candidate. The separate test-suite failures are reported above. Tracked `git diff --check` passes; checking all 81 new files yields only the disclosed instruction-capture EOF diagnostic. No file was normalized to conceal it.

No semantic decisions beyond these two approved unions were introduced. No source ontology, SOSA-2023 artifact, unrelated assessment, validator, or test was modified by this union amendment. The earlier authorized Platform assessment-test edit remains as found. No new snapshot expectation was corrected without authorization.

This report is for review of the completed uncommitted adjudication; it does not establish release readiness or waive a failing gate.
