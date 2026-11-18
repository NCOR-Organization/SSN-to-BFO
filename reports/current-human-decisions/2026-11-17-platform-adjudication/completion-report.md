# Approved current SSN/SOSA Platform adjudication — completion evidence

Baseline: `3376e1c74e846e40e6863ec8b1f1c255349aa2d3`; branch: `publication/current-sosa-readiness`.

This work implements the explicit human approval for Platform only. It does not establish release readiness. Nothing was staged, committed, tagged, or pushed.

## Authority and exact workbook edits

The workbook `mappings/SSN2BFO-COMS.xlsx` changes only `Sheet1!C9` (target expression) and `Sheet1!D9` (`coms:Reasoning`). The `owl:equivalentClass` predicate, stable RowID `urn:uuid:b4508c03-1b79-4f53-b525-d5db6d80c7cb`, and all other workbook cells are preserved. Only `xl/worksheets/sheet1.xml` differs in the XLSX archive; all other archive members are byte-identical.

[Before/after evidence](before-after.json) preserves the complete original assertion, rationale, assessment and review history. [Human decision](Platform.json), decision ID `urn:uuid:160e16e0-eedf-4dde-b3be-0ee5deddd9cc`, records reviewer `Alec Sculley` and the explicit approval on 2026-11-17. This is a new human decision, not a historical restoration. The authenticated semantic transition is `reports/current-semantic-workbook/transitions/9f891d92-ae02-4a2d-872b-7e4fc3468cf7.json`. Both workbook versions are retained under `reports/current-semantic-workbook/versions/`.

The Platform assessment changes from `unreviewed / unreviewed` to `final / formal_mapping_adopted`. Exactly 90 other assessment records remain identical. Existing review and notes fields remain historical evidence under the governed schema; the authenticated new decision and current rationale establish the active assessment.

Counts remain **91 terms, 108 workbook rows, 102 mapping assertions and six deliberate blank rows**. Final assessments increase from 23 to **24**, and unreviewed/unresolved decrease from 68 to **67**, with zero deferred. Outcomes are 17 formal mappings adopted, five no direct mapping, and two inheritance sufficient.

The sole test update adds `Platform` to `expected_later_finals` in `CurrentAssessmentTests.test_historical_final_baseline_is_exact_and_fixed`. The expected live count remains derived from the exact fixed historical cohort and later approvals; historical count, identity, hash and tamper checks are unchanged. The test passes.

## Exact rationale text

Previous `Sheet1!D9` (preserved in the authenticated history):

> sosa:Platform is modeled as a bfo:MaterialEntity defined by its role in hosting systems, without committing to parthood, attachment, or containment as necessary conditions. The equivalentTo axiom captures that hosting at least one system is both necessary and sufficient for being a platform.

Replacement `Sheet1!D9`:

> SOSA's Platform definition and its DUL Object alignment do not justify restricting all Platforms to material entities. Under the approved interpretation, a Platform is a BFO Continuant that actually hosts at least one SSN System. The hosting existential remains necessary; merely being capable of hosting does not suffice. Continuant allows material and appropriate nonmaterial hosts while excluding occurrents. The converse is supported by the source inverse relationship between hosts and isHostedBy and the System restriction that all isHostedBy values are Platforms: an individual hosting a System is therefore a Platform. The equivalence retains this converse and the actual-hosting requirement without classifying every Continuant as a Platform.

## Semantic and logical results

The approved revision replaces exactly one equivalence axiom:

```text
Before: sosa:Platform ≡ bfo:MaterialEntity ⊓ ∃sosa:hosts.ssn:System
After:  sosa:Platform ≡ bfo:Continuant ⊓ ∃sosa:hosts.ssn:System
```

The equivalence and hosting existential are preserved. Exact RDF comparison confirms this replacement is the only mapping-axiom change, appearing in the integrated and strict-BFO products. Alignment-core and CCO-extension remain byte-identical. Fresh uncached generation is deterministic. See [product delta evidence](validation/focused/results-v3/product-deltas.json).

All four candidate products pass the existing pinned-local OWL 2 DL and HermiT workflow with **zero named unsatisfiable classes**; baseline integrated validation also passes. **All 70 focused expectations pass:** 34 baseline, 34 candidate, and two native-source converse checks. See the [consolidated results](validation/focused/results-v3/summary.json) and [complete final driver log](validation/focused/validation-v3.log).

| Fresh probe intersection | Baseline | Revised candidate |
|---|---|---|
| Platform and MaterialEntity | Satisfiable | Satisfiable |
| Platform and ImmaterialEntity | Unsatisfiable | Satisfiable |
| Platform and SpatialRegion | Unsatisfiable | Satisfiable |
| Platform with no hosted System | Unsatisfiable | Unsatisfiable |
| Platform and Occurrent | Unsatisfiable | Unsatisfiable |

These are satisfiability tests, not assertions that every immaterial entity or spatial region is a Platform. Actual hosting remains required. The intentionally contradictory probe classes are separate from the unaugmented product closures whose named-unsatisfiable count is zero.

The converse has independent native-source support: `sosa:hosts owl:inverseOf sosa:isHostedBy` (`imports/sosa.ttl:155–165`) and `ssn:System ⊑ ∀sosa:isHostedBy.sosa:Platform` (`imports/ssn.ttl:717–721`) imply `∃sosa:hosts.ssn:System ⊑ sosa:Platform`. The Platform restriction `∀sosa:hosts.ssn:System` (`imports/ssn.ttl:497–505`) constrains fillers but does not itself assert a witness. Both facts are confirmed by the [source-only results](validation/focused/results-v3/source-converse/result.json), using the complete SOSA and SSN premise files with an [exact input manifest](validation/focused/results-v3/source-converse/input-manifest.json). The Continuant interpretation remains the approved alignment judgment; the native converse does not independently establish that upper-level classification.

System, Sensor, Actuator, and Sampler remain satisfiable and material, with their existing System classifications unchanged. The emitted named hierarchy changes only `Platform → MaterialEntity` to `Platform → Continuant`. Sensor and Sampler already classify as Platform on the baseline, and retain that classification; System and Actuator are not automatically Platforms. The preexisting Sensor/Sampler route combines their bearer-of/realization existentials, source Observation/Sampling restrictions requiring Sensor/Sampler agents, the retained `madeBySensor`/`madeBySampler ⊑ cco:has_agent ⊑ bfo:has_participant` mappings, and the retained hosting chain. This provides a hosted System, enabling the native converse. See the [bounded hierarchy comparison and derivation](validation/focused/related-class-comparison.json). This comparison does not claim general model-theoretic conservativity.

| Maintained product | Candidate SHA256 | Status |
|---|---|---|
| `SSN2BFO.ttl` | `7bc3d7990837cf3d178ec5d1d622666c79123d56ed8cdec9e15df0c947654669` | Approved replacement |
| `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl` | `2e29952e36faffde6a592ebb9f9217d2199897c44b7d311940ee6d540bb6a9c0` | Approved replacement |
| `releases/current-ssn-sosa/ssn-sosa-alignment-core.ttl` | `cb5a7d89b0a54cd3a0bbf0b7644d0e8b0ab8c77f8878e7d9fc0e29de5b7a4ee5` | Byte-identical |
| `releases/current-ssn-sosa/ssn-sosa-cco-extension.ttl` | `87a64e6bf7a78593ef94f48da0bb17458929b47a9f9d3ac9612c9811b766e428` | Byte-identical |

DUL Object is approved interpretive context, not an axiom loaded from these pinned dependencies; see the [source/target evidence qualification](validation/focused/source-target-evidence.json). Earlier diagnostic attempts are retained transparently: two initial probe expectations incorrectly assumed baseline Sensor/Sampler were not Platforms, then were corrected to the demonstrated baseline behavior ([correction record](validation/focused/probe-expectation-correction.json)). A four-source-only attempt passed logical/profile checks but its wrapper reported the preexisting unresolved SKOS import. The final minimal native-source proof is import-complete and does not replace complete-product validation ([scope record](validation/focused/source-proof-scope-note.json)). No validator, source ontology, or unrelated mapping was changed to obtain these results.

## Governance, generation and preservation

The established workbook transition, deterministic generator, and assessment refresh workflows produced the installed candidate. Semantic-transition authentication, decision authentication, all prior final-decision applicability checks, assessment freshness, and deterministic generation pass. The generator's retained log includes OWL 2 DL/HermiT and mapping-integrity checks. The separate standalone documentary checker fails with `disconnected documentary update chain` identically on the clean baseline and candidate; it is not reported as passing.

The isolated candidate's 14 modified tracked files and nine new authority/governance files were validated before installation. Additional new files retain validation evidence only. Exact-copy installation preserves source bytes and the Git index. All 178 preexisting excluded files (175 prior exclusions plus three omitted Deployment captures), pinned source ontologies, SOSA-2023 files, prior decision records and unrelated mapping artifacts remain unchanged. Alignment-core and CCO-extension are byte-identical.

## Full-gate baseline comparison

Fresh clean-baseline and isolated-candidate runs completed. **`make check` did not pass** on either checkout; no validation exception is inferred or granted by this implementation task. The [complete exception inventory](validation/gates/exception-inventory.json) and [independent comparison audit](validation/independent-gate-review.json) preserve every diagnostic and its classification.

| Validation scope | Clean baseline | Candidate | Complete classification |
|---|---|---|---|
| Canonical `make check` | 488 tests; 24 failures, 22 errors, seven skips; exit 2 | Same totals; exit 2 | 39 baseline-identical diagnostics; seven changed diagnostics attributable to approved workbook, projection, report, count and dependency data; no newly failing cases |
| Six separate mapping-integrity suites | 165 tests; 13 failures and one setup error | 165 tests; 16 failures and one setup error | Nine normalized tracebacks identical, one identical case with only set-display order variation, four approved-data differences in already failing cases, and three newly failing strict-BFO historical locks |
| Standalone documentary chain | Exit 1: disconnected documentary update chain | Identical exit and output | Preexisting; same error also appears in five canonical cases |

The three newly failing tests are explicitly **not baseline-identical**:

- `test_strict_bfo_mapping.StrictBfoMappingTests.test_exact_selection_identity_lock_and_distribution` locks the former Platform axiom identity.
- `test_strict_bfo_mapping.StrictBfoMappingTests.test_processed_row_and_audit_order_do_not_affect_strict_bfo_output` reaches a fixed historical product hash after the input-order determinism comparisons pass.
- `test_strict_bfo_mapping.RawStrictBfoGuardTests.test_current_context_preserves_baseline_strict_axioms_and_bytes` compares the revised working product to the old HEAD product bytes.

Independent full-input comparison confirms that all 19 strict-BFO RowIDs and the other 18 canonical axiom inputs are unchanged. The sole changed identity is Platform: `sha256:480ce3257f6b1baaaacee7b06ce730cdf63a7dd14c16b4a1bedc09597a5d96ef` becomes `sha256:863a559642f2d14feb06c876f8f8da4ccf3ed2a290a1264de3fd761c4b36094a`. The strict product changes from `676b31620df10db5c26c46bcc44b2dfd5939d606b16e0fa8a910926e8497c3af` to the approved candidate hash above. These are demonstrated consequences of approved mapping data. The fixtures were left untouched because only assessment-count test maintenance was authorized. No unexplained semantic, implementation, or test regression was demonstrated.

The two scopes contain **63 diagnostic records: 62 test methods and one class-setup error**, with zero duplicate test identities. They are not necessarily 63 independent defects. Eleven CCO test methods were blocked by the class-setup failure and are not counted as eleven additional failures. The separate documentary failure shares a cause with five canonical records and is not added as another independent defect. See [exact cross-scope accounting](validation/gates/exception-inventory.json).

The canonical run completed Turtle parsing and stopped in the current-assessment regression stage. Its 44 later conditional stages, final compile stages and Makefile tail were not reached; the [stage inventory](validation/gates/canonical-stage-boundary.json) identifies each one. Independently passing focused checks do not make the canonical gate pass. No unrelated repair, test weakening or waiver was performed.

All 1,092 declared full-gate inputs match installed main bytes, and test snapshots remained byte-preserved. Retained raw logs, commands, environment inventories, input hashes, full comparisons and bounded task scripts are listed in the [42-file gate evidence manifest](validation/gates/retention-manifest.json). Nine redundant external captures remain untouched outside the repository. Temporary checkout paths in raw evidence record execution provenance; they are not required distribution dependencies.

## Modified tracked inventory

- `SSN2BFO.ttl`
- `mappings/SSN2BFO-COMS.xlsx`
- `mappings/current-ssn-sosa-assessment.json`
- `releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl`
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

## Final task scope and review status

The [complete file inventory](file-inventory.json) lists each modified or newly retained task file with its SHA256 and preservation checks. It excludes all 178 preexisting local files. Fourteen tracked files are modified; the only code edit is the approved assessment-count fixture change. New files preserve the RowID-linked decision, semantic transition, workbook version and validation evidence. The nine new authority/governance files are identified in [the validated candidate inventory](validation/validated-candidate-inventory.json); additional retained files are supporting evidence, not additional ontology development.

HEAD and branch remain at the baseline; the Git index is unchanged and no task files are staged. All unrelated tracked files, including pinned sources, SOSA-2023, the implementation rule and previous decision history, remain byte-identical. The final inventory records the exact added-file count and full selected paths. The implementation is ready for human review with the validation limitations above; no commit, push, tag or release was performed.
