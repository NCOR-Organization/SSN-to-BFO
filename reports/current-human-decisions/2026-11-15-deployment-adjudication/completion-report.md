# Deployment adjudication — completion report

**Approved mapping implementation and focused semantic validation: PASS. Canonical `make check`: DID NOT PASS on either baseline or candidate. No gate waiver is granted.**

The approved current-track `ssn:Deployment` revision has been applied from baseline `45b98f30854a623f752a3bbdd1c69df8f0779a82`. The main working tree contains 13 modified tracked files and 67 new governance, preservation and validation-evidence files. All 1,890 inputs to the completed candidate gate match the main working tree; the added completion evidence is recorded separately in the final manifest. No staging, commit, tag or push was performed.

Only `mappings/SSN2BFO-COMS.xlsx` cells `Sheet1!C31` and `Sheet1!D31` changed. Predicate `owl:equivalentClass`, subject `ssn:Deployment`, and RowID `urn:uuid:1c52d7ee-ee3d-4eb7-ae42-4df1912ee8eb` are preserved.

**Exact logical change**

One equivalent-class axiom was replaced; every other mapping assertion is unchanged.

```text
Removed: EquivalentClasses(ssn:Deployment ObjectIntersectionOf(cco:PlannedAct ObjectSomeValuesFrom(ssn:deployedSystem ssn:System) ObjectSomeValuesFrom(ssn:deployedOnPlatform bfo:MaterialEntity)))
Added:   EquivalentClasses(ssn:Deployment ObjectIntersectionOf(cco:PlannedAct ObjectSomeValuesFrom(ssn:deployedSystem ssn:System)))
```

The removed condition is `ssn:deployedOnPlatform some bfo:MaterialEntity`. The PlannedAct classification, required deployed-System witness and equivalence are retained. Source-native inverse and universal restrictions remain unchanged. Integrated and CCO-extension products each have five fewer RDF triples encoding the removed restriction/list member; the logical mapping-assertion count remains 102.

This is a strict logical weakening relative to the retained source and mapping closure. The source already entails the converse of the shorter expression: `x deployedSystem y` and `y a System` imply `y hasDeployment x`, and the System universal restriction classifies `x` as Deployment. The baseline therefore entails the new equivalence; the candidate permits a Deployment without any `deployedOnPlatform` fillers and does not entail the former mandatory-Platform condition. A Platform-based Deployment remains permitted.

**Authoritative reasoning**

Previous `D31` text is retained verbatim in `before-after.json`, the before workbook archive and original review packet:

> ssn:Deployment is modeled as a cco:PlannedAct because it involves intentional positioning or installation of systems for a purpose, rather than constituting a structural relation such as parthood. The equivalentTo axiom captures that deploying at least one system on at least one material entity is both necessary and sufficient for being a deployment.

New `D31` text:

> SSN defines Deployment as deploying one or more Systems for a particular purpose and explicitly states that deployment may occur on a Platform. The alignment interprets purposeful positioning or installation of Systems as a CCO PlannedAct. The restriction ssn:deployedSystem some ssn:System requires at least one deployed System, reflecting the source definition's one-or-more commitment; the source universal restriction alone does not require such a witness. The converse is supported by the source axioms: ssn:hasDeployment is inverse to ssn:deployedSystem, and ssn:System restricts all hasDeployment values to ssn:Deployment. Thus an individual related by deployedSystem to a System is a Deployment, including an individual satisfying the proposed PlannedAct intersection. Platform involvement is optional, so a deployedOnPlatform existential is not a necessary condition. The retained source universal restriction still classifies any deployedOnPlatform value of a Deployment as a Platform. Removing the mandatory Platform witness does not prohibit Platform-based deployments.

**Pinned semantic evidence**

- `imports/ssn.ttl:626–643`: Deployment definition and its class-local universal restrictions. The natural-language definition supplies “one or more Systems” and makes Platform involvement optional; the universal restrictions alone do not assert existence.
- `imports/ssn.ttl:197–202`: `deployedSystem` is inverse to `hasDeployment`.
- `imports/ssn.ttl:717–744`: System restricts every `hasDeployment` value to Deployment, yielding the source-only converse.
- `imports/cco.ttl:5803–5809`: the pinned CCO Planned Act definition supports the retained purposeful-act interpretation. This alignment commitment is distinguished from a source-only OWL entailment.

**Decision and assessment history**

Reviewer: **Alec Sculley**. Explicit new human decision `urn:uuid:b85b63f3-4ab3-4d31-8773-3f376111310b` was encoded at `2026-11-15T22:24:29.306783-05:00` as `final / formal_mapping_adopted`. It is retained in `reports/current-human-decisions/2026-11-15-deployment-adjudication/Deployment.json`, with the exact human instruction, original assessment snapshot, original packet, approved-candidate packet, before/after comparison and transition authorities. Semantic transition: `reports/current-semantic-workbook/transitions/bd69b546-6ef2-4704-8f05-325ec9bc1862.json`.

Original workbook SHA-256: `825dc90460ddc056c89b5b7af3030b4c615a0c5e00c5cfae89057029c10cfc2d`. Approved workbook SHA-256: `e7e2ec225e326b0b2bb232591f4949b378876937e6bcb90a3917bfd82d5e87dd`. Both byte-exact workbooks are retained in the semantic version archive. All previous governance records remain byte-identical, and all prior decisions authenticated without a new applicability exception.

Only Deployment’s `review_state`, `assessment_outcome`, `rationale`, `evidence` and `human_decision_record` fields changed. Its existing `review`, `notes` and cross-track fields remain verbatim as pre-decision historical context under the existing schema; their unresolved wording is not the active outcome. The bound final decision and approved rationale express the adopted resolution. All 90 other assessment records, their statuses, and all RowIDs are unchanged.

Counts: **91 terms; 108 workbook rows; 102 OWL mapping assertions; six deliberate blank rows; 23 final, zero deferred, 68 unreviewed/68 unresolved; 16 formal_mapping_adopted, five no_direct_mapping and two inheritance_sufficient.**

**Focused validation**

- The four maintained products pass OWL 2 DL profile and HermiT checks against their current complete pinned-local closures, with zero named unsatisfiable classes. The baseline integrated closure also passed.
- All 32 focused expectations pass: 15 on the baseline, 15 on the candidate and two in a separate source-only run. The latter loads no mapping axioms or BFO/CCO target ontology; it establishes the source-derived converse and confirms that source universal restrictions alone do not require a deployed-System witness.
- The candidate retains PlannedAct/System commitments and source universal restrictions; Deployment, System and Platform remain satisfiable. A Deployment constrained to have no deployedOnPlatform fillers is satisfiable in the candidate and was unsatisfiable under the baseline mapping. The old expression remains sufficient but is no longer necessary.
- Independent deterministic rendering and exact graph comparisons pass: only the approved equivalent-class replacement appears. Core and strict-BFO product bytes are unchanged.
- Semantic/documentary history coordination, all decision authentication and prior-decision applicability, and six assessment-report freshness checks pass.
- `python -B tools/check_coms_mapping.py` and `python -B tools/check_coms_mapping.py --check-only` pass in the isolated candidate checkout. The latter confirms fresh maintained outputs without rewriting tracked files. Pre/post-update `git diff --check` passes.
- Pinned source ontologies, SOSA-2023 artifacts, previous governance records and all 175 excluded local files remain unchanged. The index remains unchanged.

The legacy standalone `python -B tools/current_documentary_workbook.py check` fails on both the clean baseline and candidate with `disconnected documentary update chain`. The current mixed semantic/documentary coordinator passes. This legacy command failure is recorded rather than waived or repaired.

**Focused regression suites — not a clean pass**

The six existing mapping-integrity suites ran 165 tests on each checkout. Both produced 13 failures and one class-setup error, with exactly the same 14 failing cases. Eight normalized tracebacks are identical; one additional failure has the identical 32-RowID set printed in a different order; five diagnostics differ only in approved data (the revised CCO product hash, current semantic-transition ID, and historical removed-assertion count). There are no newly failing cases in these six suites and no demonstrated new regression. Full tracebacks and classifications are retained in `validation/mapping-integrity-comparison.json`.

The same obsolete transition expectation prevents 11 CCO-extension test methods from running on both checkouts. The CCO extension's direct complete-closure OWL 2 DL and HermiT checks passed separately; this does not convert the blocked suite into a passing suite. Tests, validators and historical evidence were not edited, and no gate exception was granted.

**Assessment refresh ordering**

An intermediate assessment check detected a stale binding because reports had first been generated before the ontology products. The existing assessment write/check workflow was rerun after ontology generation, and all six reports now bind the current 185 input hashes. The final checks pass in both the candidate checkout and the main working tree. The earlier incomplete candidate gate run was stopped and retained outside the repository; the final full-gate comparison uses only the fresh run after report authentication passed.

**Canonical full gate — failed, compared without waiver**

Both clean-baseline and isolated-candidate executions of `make check` completed. Each ran 488 tests with seven skips and returned exit code 2. Baseline produced **24 failures and 22 errors**; candidate produced **25 failures and 22 errors**.

Of the 46 shared failing cases, **39 complete normalized tracebacks are identical**, and **seven have independently explained diagnostic differences caused by the approved workbook, generated-report, assessment-count or dependency-inventory changes**. Only exact checkout-root paths were normalized; hashes, counts, transition IDs, exception types, messages and set contents were retained and compared. No demonstrated new regression or inconclusive difference remains in this comparison.

The sole additional failing case is `test_historical_final_baseline_is_exact_and_fixed` (`tests/test_current_assessment.py:218`): its unchanged assertion expects 22 current final assessments, while the sole approved Deployment finalization yields 23. The following hardcoded final-term set also omits Deployment, but that assertion was not reached. This is a newly failing test due to a stale current-inventory expectation; it is not reported as an identical preexisting failure, and the test was not changed.

The preexisting queue failure remains. Baseline reaches the minimum-two-alternatives assertion and fails at one; candidate first fails the old 69-item queue expectation because 68 terms remain unresolved. Direct comparison confirms the same four one-alternative entries on both sides: implementedBy, implements, madeBySensor and madeObservation. The earlier count failure masks, and does not resolve, the existing queue defect.

The other changed diagnostics concern the approved workbook/projection/report hashes, current assessment counts, and an input set that adds exactly seven approved Deployment governance files while removing none. Both runs still omit the same historical sampling-relationship snapshot from that input set. Unrelated stale documentation and historical fixture expectations were preserved.

**`make check` was executed and did not pass.** Only the initial Turtle parse and current-assessment regression stage executed. Subsequent conditional validation stages, the Makefile compile prerequisite and the final check recipe were **not reached**. The separately passing focused ontology checks do not turn the canonical gate into a pass. No exception, release-readiness claim or unrelated repair is made.

Full logs, all traceback blocks, case-by-case attribution and input-state evidence are retained under `validation/canonical-gate/`. All 158 tracked files under `tests/` and `tools/` are byte-identical to baseline. All 1,890 gate-input files remained byte-identical throughout the candidate run and match the main working tree.

**Maintained product SHA-256 values**

| Product | SHA-256 after adjudication | Byte status |
|---|---|---|
| `SSN2BFO.ttl` | `c1a58cc8467becabb352da185f44d7911a76e580c983639d3e3152260a50518e` | Changed by the approved axiom replacement |
| `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl` | `cb5a7d89b0a54cd3a0bbf0b7644d0e8b0ab8c77f8878e7d9fc0e29de5b7a4ee5` | Unchanged |
| `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl` | `676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af` | Unchanged |
| `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl` | `87a64e6bf7a78593ef94f48da0bb17458929b47a9f9d3ac9612c9811b766e428` | Changed by the approved axiom replacement |

**Final preservation and file inventory**

Final verification preserves HEAD `45b98f30854a623f752a3bbdd1c69df8f0779a82`, branch `publication/current-sosa-readiness` and the exact index entries. Nothing is staged. All 175 preexisting excluded untracked files and all 1,842 unrelated tracked files remain byte-identical. This includes pinned source ontologies, SOSA-2023 artifacts, previous decision records, tests, validators and the external implementation rule. All 108 workbook RowIDs and all 90 unrelated assessment records are preserved. Assessment-report input bindings remain fresh. `git diff --check` passes.

The final SHA-256 inventory, before/after hashes for modified files, hashes of all excluded files and preservation results are recorded in `validation/final-preservation-manifest.json`. The manifest excludes its own bytes from its hash inventory to avoid a self-reference.

Modified tracked files (13):

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

Added task files (67):

- `reports/current-human-decisions/2026-11-15-deployment-adjudication/Deployment-before-review-packet.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/Deployment-review-packet.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/Deployment.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/approved-instructions.txt`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/assessment-before.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/before-after.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/completion-report.md`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/transition-authorities.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/baseline-documentary-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/baseline-queries.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/candidate-queries.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/candidate-verification.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/baseline/clone-metadata.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/baseline/failure-inventory.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/baseline/make-check-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/baseline/make-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/candidate/failure-inventory.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/candidate/input-manifest.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/candidate/input-preservation.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/candidate/make-check-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/candidate/make-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/candidate/report-binding-preflight.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/canonical-comparison-approved-data.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/canonical-gate/canonical-gate-comparison.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/changes.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/final-preservation-manifest.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/baseline/entailment-queries.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/baseline/entailment-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/baseline/integrated-validation-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/candidate/alignment_core-validation-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/candidate/cco_extension-validation-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/candidate/entailment-queries.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/candidate/entailment-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/candidate/integrated-validation-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/candidate/strict_bfo_mapping-validation-result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/generation-snapshots.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/product-deltas.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/focused-validation/summary.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/generation-check-only.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/generation-update.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/independent-governance-audit.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/main-documentary-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/main-final-assessment-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/main-generation-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/main-independent-preservation.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/main-semantic-history-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/mapping-integrity-baseline.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/mapping-integrity-baseline/results.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/mapping-integrity-candidate.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/mapping-integrity-candidate/results.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/mapping-integrity-comparison.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/post-generation-assessment-bindings.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/post-generation-assessment-check.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/post-generation-assessment-write.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/post-generation-report-install.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/probe-definitions.ttl`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/source-converse-validation.log`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/source-converse-validation/closure-manifest.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/source-converse-validation/queries.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/source-converse-validation/result.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/source-converse-validation/summary.json`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/validate_deployment_candidate.py`
- `reports/current-human-decisions/2026-11-15-deployment-adjudication/validation/validate_source_converse.py`
- `reports/current-semantic-workbook/transitions/bd69b546-6ef2-4704-8f05-325ec9bc1862.json`
- `reports/current-semantic-workbook/versions/825dc90460ddc056c89b5b7af3030b4c615a0c5e00c5cfae89057029c10cfc2d.xlsx`
- `reports/current-semantic-workbook/versions/e7e2ec225e326b0b2bb232591f4949b378876937e6bcb90a3917bfd82d5e87dd.xlsx`

No source ontology, SOSA-2023 artifact, unrelated mapping, validation code or historical authority was edited. The completed change is left unstaged for human review; no commit, tag or push was performed.
