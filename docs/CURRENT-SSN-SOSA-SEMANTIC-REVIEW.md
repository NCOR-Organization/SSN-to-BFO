# Current SSN/SOSA semantic review protocol

This is a project-specific codification for the assertion-oriented `mappings/SSN2BFO-COMS.xlsx` track. It does not define COMS architecture, change the pinned SOSA-2023 track, or claim conceptual analysis is novel relative to PROV-BFO. No external research was used. References to older reports concern recorded practice and decisions; those reports may use historical inputs or reduced closures and are not current validation evidence.

## Scope and assessment authority

`config/current-ssn-sosa-scope.json` preserves the existing `queries/source-classes-and-object-properties.rq` policy: named OWL classes and object properties in the four declared SOSA/SSN namespaces, from the four current local source files, excluding `owl:deprecated true`. Datatype properties are outside the existing assessment scope; no completeness claim extends to them. The gate independently computes this inventory and compares it with both the existing SPARQL query and the frozen source signature. Ontology byte identity is separately governed by `config/current-ssn-sosa-identity.json`.

`mappings/current-ssn-sosa-assessment.json` contains exactly one record per source IRI. It records review state (`final`, `deferred`, `unreviewed`) independently of assessment outcome (`formal_mapping_adopted`, `inheritance_sufficient`, `no_direct_mapping`, `deferred`, `unreviewed`). The twelve historical final records reconstruct explicit earlier decisions whose relevant assertions still match the workbook. Additional finals require the evidence-bound human approval described below. A recorded rejection of a specific target relation does not reject the native source relation. An artifact's domain/range-only status is reported as `typing_only_in_workbook`, never as a semantic assessment outcome.

The workbook remains the authority for assertions and can have multiple rows for one term. Review-state edits occur in the assessment inventory; predicate, target, expression, chain, domain/range, or other formal-axiom changes require explicit human approval and normal regeneration. No formal mapping should be invented to improve a percentage.

## Human decision records and final-state guard

The twelve documentary historical finals are listed, and only those twelve are listed, in `config/current-ssn-sosa-historical-finals.json`. The assessment validator pins that file's exact SHA-256 and checks each final against the complete canonical assessment-record SHA-256, selected outcome, and historical evidence reference. These exceptions reconstruct recorded prior decisions; they are not a new review. Any changed final record, including materially changed rationale, loses the exception. A currently deferred or unreviewed term never gains an exception from a historical recommendation or a workbook assertion.

Every other `final` assessment requires a project-specific `human_decision_record` reference with `path` and `sha256`. The referenced JSON has schema version 1 and records a unique UUID decision ID; the exact source IRI, `final` state, selected outcome and assessment rationale; a reviewer identity and time with timezone; the packet's open question and an explicit answer; the assessment evidence references; exact RowIDs and formal mapping predicates/targets; current source-file hashes and their aggregate identity hash; current target, workbook, scope and source-query hashes; and the current formal-coverage hash. It also references a full **pre-decision assessment snapshot** and the exact **per-term packet snapshot**, each by path and SHA-256. The pre-decision record and packet item have separate canonical SHA-256 values. Binding to the pre-decision snapshot avoids a circular hash of an assessment file that itself contains the decision-record reference.

The validator compares the decision with the final assessment, live workbook rows, current non-workbook input hashes, formal coverage and pre-decision record. The historical full-workbook hash remains immutable. A different live workbook requires an authenticated documentary or project-local semantic transition. Historical authentication retains the original inputs; current applicability separately examines each intervening version, as specified in [Semantic workbook evolution](CURRENT-SEMANTIC-WORKBOOK-EVOLUTION.md). The validator reconstructs the **complete per-term review packet** from the same extractor used by report generation, using the exact historical workbook when workbook evolution has occurred, and requires exact equality with the saved snapshot, including target facts, chains, derived consequences and pinned-track comparison. It rejects a missing, stale, cross-term or cross-outcome artifact before generating a shortened queue or a newly safe rationale. A final `formal_mapping_adopted` decision must have a real current formal assertion and explicitly approve it. A final `no_direct_mapping` decision must have no direct mapping assertion, explicitly adopt that outcome, and contain a separate semantic non-adoption conclusion; a profile/tool limitation or inheritance sufficiency alone is not such a conclusion. A final `inheritance_sufficient` decision must also satisfy the existing inherited-route and bound sufficiency-evidence checks. This guard applies only to the current SSN/SOSA assessment, not to generalized COMS architecture.

For an explicitly approved typing-only treatment, a `final / formal_mapping_adopted`
decision uses `decision_basis: formal_typing_approval`, `formal_typing_approved: true`,
an empty `formal_mapping_assertions` list, and an exact `formal_typing_assertions`
list of domain/range predicates, targets and RowIDs. Competing direct mappings,
missing typing assertions or mismatched approvals fail authentication. All ordinary
reviewer, input, packet, snapshot, history and applicability checks still apply.
This records adoption of global OWL typing commitments; it does not introduce
SHACL constraints or change the separate `typing_only_in_workbook` coverage
classification. Existing decisions and their original assertion lists remain unchanged.

## Documentary workbook evolution

`tools/current_documentary_workbook.py` governs only
`mappings/SSN2BFO-COMS.xlsx`. Its versioned semantic projection preserves sheet
identity/order, row positions/order, and exact A/B/C/E values. Deterministic
UTF-8 JSON supplies the SHA-256 input. It does not trim or normalize those
values. Canonical JSON sorts object keys, uses comma/colon separators, retains
Unicode characters, disallows non-finite numbers, and ends with one newline.
Explicit empty strings remain distinct from absent/null cells. The five
expected headers and two-sheet profile are checked; formulas
and unsupported columns are rejected. Only existing identified data-row D
cells (`coms:Reasoning`) can be documentary changes.

The code-pinned `config/current-documentary-workbook-baseline.json` anchors the
original workbook snapshot, the two accepted sample decisions and their final
assessment records, and their retained pre-decision evidence. Existing decision
JSON, old full-workbook hashes, packet snapshots, approved rationales, reviewer
identity and timestamps are not rewritten. Accepted-record integrity is checked
before branching on assessment state, so changing a final to unreviewed cannot
evade it. This local baseline adds custody, not a new semantic decision.

Each documentary update retains actual old/new XLSX bytes under
`reports/current-documentary-workbook/versions/` and a create-once record under
`reports/current-documentary-workbook/updates/`. The record identifies its
schema, UUID, exact governed path, full hashes, identical semantic hashes,
allowed column, exact changed cells and old/new values with hashes, supporting
evidence references, timestamp and editor. It states that A/B/C/E are unchanged.
Validation recomputes hashes and the complete D-cell difference from the
snapshots; claims in the record are not substitutes for those bytes. Missing,
extra or duplicate changed cells, semantic changes, disconnected links and
unrecorded workbook transitions fail. Each transition requires actual D changes.

The retained packet remains the evidence actually reviewed. After a valid D
update the live packet may contain newer rationale text, but the saved packet
is compared with a reconstruction from the historical workbook. No packet
fields are dropped from validation. All source, target, scope, query, coverage,
RowID, predicate/target and outcome checks remain in force. For the sample pair,
copying the already-approved rationales into D16/D17 neither creates a decision
nor pretends those rationales were present in the pre-decision workbook.

Source-identity and preservation checks accept this workbook-specific D-only
transition or the separately governed semantic transition; their historical
full-file identities remain unchanged.
Other files still require their original identity checks. Generation and report
freshness must be rerun for a later documentary update. Invocation custody and
semantic reasoning evidence are not silently rebound. Rationale completion does
not settle outstanding semantic questions or establish publication readiness.

The tool's `projection` and `check` commands are read-only. Its `record` command
records a prepared old/new candidate transition and its evidence; it does not
edit or install the authoritative workbook. A subsequent authorized reasoning
completion task must prepare the audited 104 D assignments, validate and record
the transition, then install that exact candidate and refresh affected reports.
Sheet1!D6 and all A/B/C/E values remain outside that edit set.

For a prepared candidate, the evidence manifest is an object keyed by exact
locations such as `Sheet2!D16`. Every changed location has a nonempty list of
objects with project-relative `path`, exact file `sha256`, and an optional
`reference` (for example `JSON rationale`). The manifest must name exactly the
changed cells. Values and value hashes are derived from the two workbooks,
not trusted from caller claims. A registration command is:

```bash
python tools/current_documentary_workbook.py record \
  --old mappings/SSN2BFO-COMS.xlsx \
  --new /tmp/ssn-reasoning-completion.xlsx \
  --evidence-manifest /tmp/ssn-reasoning-evidence.json \
  --editor "Codex, authorized documentary editor"
```

This example requires a separately prepared, authorized candidate and evidence
manifest. Registration leaves the live workbook untouched; the new chain tail
becomes current only when that exact candidate is installed. The editor field
attributes the documentary edit, not a new human semantic review.

For a currently unresolved term, the intended sequence is:

1. Open the generated human-review packet and assess its source meaning, target meaning, workbook rows, alternatives and open question. Keep a byte-exact copy of that term's packet and a copy of the assessment *before* changing state. To change a historical final, first reopen it into an unresolved assessment with a specific review question and regenerate its packet; a prior final record is not a substitute for a reviewed unresolved packet.
2. A human reviewer makes and explicitly records the semantic decision, including the question response, outcome-specific conclusion, rationale, identity, time and cited evidence. Codex or another tool may encode that decision only after explicit human instruction.
3. Generate the decision JSON with hashes of the retained assessment and packet snapshots, current source/target/workbook/scope/query inputs, and formal coverage. Add its path and SHA-256 to the assessment record, then set that record's final state, outcome and matching rationale.
4. Run `python tools/current_assessment.py` before `--write`. The validator must accept the exact decision, mapping state and evidence hashes. Only then regenerate reports; the term leaves the queue after validation succeeds.

Generating these mechanics does not make a human decision. Alec Sculley approved the coordinated `sosa:hasSample` / `sosa:isSampleOf` review as `final` / `no_direct_mapping`; the two guarded records and pre-decision evidence are indexed in [the sample-pair decision manifest](../reports/current-human-decisions/2026-10-25-sample-pair/manifest.json). The subsequent [three-term adjudication](../reports/current-human-decisions/2026-10-26-three-term-adjudication/manifest.json) finalized `ssn:forProperty` as `no_direct_mapping` and `ssn-system:SystemProperty` and `ssn-system:MeasurementRange` as `inheritance_sufficient`. The current assessment is **17 final, 0 deferred, 74 unreviewed, 74 unresolved**, with **10 formal mappings, 5 no-direct mappings, and 2 inheritance-sufficient outcomes**. Both sample-pair workbook predicate/target pairs remain blank; the three-term transition removed exactly three logical mappings and added none. The four evidence holds for `sampling:RelationshipNature`, `sampling:natureOfRelationship`, `sosa:madeActuation`, and `sosa:madeByActuator` remain open.

Three-term adjudication fully validated within scope; overall current-track publication readiness remains blocked by independent Class B work.

This local guard proves that a new final state is accompanied by a matching decision artifact. It cannot cryptographically prove that a person reasoned about the term, or establish nonrepudiation against someone who can rewrite all local files and validator code. A transient reopening followed by byte-for-byte restoration of an unchanged grandfathered record is indistinguishable from a record that was never reopened; detecting that event would require independent append-only custody. Any *persisted* reopened state or changed re-finalized record is outside the exact historical baseline and must pass the new-decision guard.

## Current execution custody and historical archives

Current semantic execution validation has a fixed ticketed-custody contract. Both `reconcile_raw_evidence()` and `validate_stored()`, and the publication-readiness pipeline, require integer `execution_evidence_schema=2` and the complete expected-slot → ticket → wrapper envelope/capture → retained stdout/stderr → derived classification → summary chain. The report field is only a cross-check: missing, null, malformed, legacy and unknown values fail. No mutable field can select a legacy validator or waive a missing ticket, envelope or capture.

Historical inspection is separate. `python tools/current_semantic_validation.py --read-historical` reads only the legacy archive whose path and original-summary SHA-256 are pinned in validator code. It also verifies the raw files against that pinned summary's manifest. The returned archive is `HISTORICAL_ONLY`, explicitly current-review-evidence-ineligible and publication-ineligible. It cannot supply a current required execution slot, even if its summary or eligibility flags are copied into a current report. The former `--reconcile` route is retired; old execution hashes and timestamps are not refreshed into current evidence. Reading history makes no fresh reasoner or semantic assertion.

The driver uses the fail-before-touching retry policy. Calling `run_graph()` again for an occupied slot/build/evidence destination fails before serialization or any write. Graphs, queries, attempt reservations and results use exclusive create-once writes. To retry, provide explicitly fresh build and evidence destinations (the normal top-level command already creates timestamped destinations). The retry gets its own ticket, UUID, nonce and captured outputs; the earlier attempt remains intact. A create-once selection record explicitly names the selected invocation. An honest failed attempt may be retained and selected as failed custody evidence, but cannot become a successful semantic or publication result. The wrapper also supports separately ticketed reexecution against unchanged retained inputs; this does not permit the driver to overwrite them.

These controls establish local custody while the ticket/capture/envelope/selection artifacts and validator remain intact. They do not establish cryptographic nonrepudiation against an actor rewriting all local files, validator code and history. External append-only or signed custody remains a separate stronger guarantee.

## Reconstructing historical finality

The reconstruction threshold is documentary, not a fresh semantic endorsement. A prior record is sufficient evidence of an earlier adopted decision when it identifies the exact current-track term and direction, explicitly adopts/retains/rejects the relevant assertion, and its predicate, target expression, or deliberate absence matches the current workbook. A concrete historical recommendation can also document adoption when the workbook implements that exact recommendation and no cited later record supersedes or reopens it. This is the limited basis used for `usedProcedure` and `hasSubSystem` in `reports/straightforward-op-mapping-candidates-review.md`. The word “Recommendation” in a heading is neither automatically sufficient nor automatically disqualifying. General candidate lists, alternative proposals, a successful reasoner run, lexical similarity, and a decision for another track remain history or recommendations by themselves.

An explicit historical mapping therefore clears the *prior-decision evidence* threshold; it does not override a separately recorded current reopening. Reopening requires identifying a concrete unresolved question about that decision's applicability or commitments, retaining the prior decision as evidence, and awaiting human disposition. A changed source or target, a superseding decision, conflicting adoption records, or a stated unresolved necessary/sufficient-condition question may require this reconciliation. Mere existence of a cross-track difference is not an automatic reopening rule. The existing inventory's reopenings are recorded state, not a policy applied afresh by this guard repair.

**Sampler is a flagged reconstruction ambiguity.** `reports/sampler-equivalentclass-decision.md` explicitly supersedes the earlier conservative recommendation and accepts necessary-and-sufficient equivalence. It qualifies as evidence of an adopted prior mapping. The current assessment nevertheless already asks whether that decision should remain final given unused samplers and the pinned track's removal of actual Sampling existentials. Thus `Sampler` remains `unreviewed` because the inventory contains a current reopening question, not because its historical decision was merely a recommendation or failed the prior-decision threshold. The supplied evidence does not independently settle whether that reopening should take precedence; doing so would be a human assessment decision. This discrepancy remains flagged for review. It cannot be repaired by mechanically promoting `Sampler`, demoting other historical decisions, or treating the pinned track as authoritative for this track. All current review states remain unchanged.

## Evidence required for inheritance sufficiency

`final` / `inheritance_sufficient` requires an actual inherited route for that exact source IRI under the current structural coverage calculation, plus a separate explicit sufficiency rationale. The route establishes coverage only. It does not establish that another direct mapping is unnecessary.

The dedicated assessment field `inheritance_sufficiency_evidence` must contain a project-relative `path` to an existing JSON decision record and that file's `sha256`. The decision record must identify the same `source_iri`, set `assessment_outcome` to `inheritance_sufficient` and `no_additional_direct_mapping_required` to `true`, and provide an explicit `rationale`. Generic “inherited” prose is insufficient. Its `input_sha256` map must equal the current source ontology, target ontology, C workbook, and source-inventory-query hashes. Its `inherited_routes_sha256` must equal SHA-256 of the exact current inherited-route list serialized with the assessment tool's canonical JSON format. A missing record, wrong term, modified record, changed governed input, or changed route invalidates the reference. This binding records the scope of a reviewed decision; creating a valid fixture or passing a guard does not authorize a real semantic decision. There are still zero real `inheritance_sufficient` outcomes.

## Review procedure

1. **Establish the source meaning.** Read preserved definitions, named and anonymous hierarchy axioms, source restrictions, domain/range and advisory `schema:domainIncludes`/`schema:rangeIncludes`, examples, and source documentation. Advisory annotations are not global OWL domain/range axioms. This codifies the source-versus-mapping separation in `reports/hermit-source-vs-mapping-isolation.md` and `reports/isResultOf-hasResult-full-closure-analysis.md`.
2. **Identify the exact target interpretation.** Use current local BFO/CCO IRIs, definitions, hierarchy, disjointness, and relation signatures. Record alternatives without introducing a new ontology. This codifies `reports/reasoner-safe-replacement-mapping-review.md` and `reports/ssn-systems-property-split-mapping-review.md`.
3. **Separate necessary and sufficient conditions.** Ask which conditions every source instance must satisfy and which would be enough to classify an instance as the source. This codifies `reports/sampler-subclass-vs-equivalentclass-review.md` and the deliberate decision in `reports/sampler-equivalentclass-decision.md`.
4. **Test both directions before accepting equivalence.** Seek counterexamples to each direction; consistency alone does not establish equivalence. A new term-by-term counterexample log is proposed hardening of the existing Sampler relation-strength review. The pinned track's different decision is a comparison prompt, not permission to change this track.
5. **Inspect all commitments.** Check actual witnesses from existentials, universals where present, category commitments, domain/range propagation, continuant/occurrent compatibility, functional/simplicity conditions, and source/target disjointness. For example, capability is not an actual realization, and a chain `p o q` headed by `r` entails `r` from a path, not the path from an `r` assertion. This codifies the failure isolation in `reports/hermit-input-output-mapping-evaluation.md`, `reports/hosts-implementedby-complex-mapping-review.md`, and current blank-row explanations; a uniform checklist is proposed hardening.
6. **Inspect inherited alignment.** Ask whether mapped source superclasses, superproperties, equivalences, or inverse relations already supply sufficient alignment. The existing inverse-side policy is evidence (`reports/inverse-side-direct-mapping-policy-review.md`). Applying an explicit inheritance-sufficiency outcome to every current term is proposed hardening; structural inherited coverage alone does not decide that outcome.
7. **Prefer the weakest defensible assertion.** Consider a one-way necessary inclusion before equivalence, a justified upper category before an undocumented conjunction, and no direct property mapping before a category-conflicting uniform relation. This codifies the rejected upper mapping in `reports/observes-upper-mapping-decision.md` and the alternatives in `reports/reasoner-safe-replacement-mapping-review.md`.
8. **Permit no direct mapping.** Record an explicit reviewed no-direct outcome when appropriate. Do not equate an empty row with an accidentally missing assertion. Existing evidence includes the rejected process-input/output mappings in `reports/input-output-cco-mapping-rationale-cleanup.md`.
9. **Name the reason for non-adoption.** Distinguish semantic rejection, inheritance sufficiency, implementation/profile limits, and unresolved review in the rationale and review state. This codifies the input/output rejection versus sample-chain profile deferral; the consistent one-term inventory is proposed hardening. An external conditional query is not part of the OWL mapping closure (`reports/ssn-hasproperty-rule-mapping-artifact.md`).
10. **Validate and retain exact evidence.** Bind accepted assertions, the source/target closure, source examples, selected semantic expectations, named-hierarchy deductive differences, and fresh test outputs to hashes and HEAD. Existing project generation/HermiT practice supports validation; two-phase exact-closure examples, both-signature deductive differences, and hash-bound reports are proposed publication hardening. Do not treat a reasoner/profile failure as a semantic refutation, a failed ontology as a source inconsistency without source-only comparison, or a small expectation set as global interpretability.

## Reports and counting rules

Run `python tools/current_assessment.py --write` after a justified assessment change to refresh only project reports. `python tools/current_assessment.py` checks equality, types, RowIDs, source scope and report freshness. `--require-final` also fails while any deferred or unreviewed source term remains. Mutation tests cover missing, extra and duplicate subjects, type and scope drift, and the direction of structural coverage.

`reports/current-ssn-sosa-coverage.json` and its Markdown companion separate assessment outcomes from artifact coverage. Direct coverage includes class and relation inclusions/equivalences. A chain head is a separate incoming route. Inherited coverage follows explicit named source hierarchy/equivalence/inverse paths to a direct mapping; it is a sound structural lower bound, not an exhaustive OWL classification result. Domain/range does not establish relation coverage. Conditional-query eligibility means a route exists only when its typing assumptions are met and the separate query is executed. No established route is relative to these documented routes; it is not a global non-entailment proof. Overlaps are preserved rather than inflated into an exclusive mapped/unmapped total.

`reports/current-ssn-sosa-rationale-proposals.json` inventories every term's existing prose and publication-critical forms. `safe_to_adopt` means the prose can document an existing supported fact or decision; it does not imply that an unresolved semantic question has been answered. Existing explanations for blank-row deferrals can therefore be safe documentary proposals while review remains required. Nothing is automatically written into the workbook.

A safe proposal must also be consistent with the active mapping rows. Wording that describes a direct alignment as deferred or absent while a formal mapping is active is routed to `human_review_required`. In particular, the existing `FeatureOfInterest` workbook wording “Direct alignment deferred” conflicts with its active subclass-to-union assertion. That prose is retained as history and flagged, but its proposal is demoted from safe status. This documentary demotion neither endorses nor rejects the union mapping and does not alter its assessment state.

`reports/current-ssn-sosa-human-review.md` is the finite queue. Its JSON companion supplies bounded material facts, RowIDs, routes, exact target definitions, and input hashes. Items are ordered by blank rows, typing-only terms, equivalences, complex expressions, existentials, chains, cross-track differences, then remaining target commitments. The target glossary deduplicates repeated definitions for readability. Each decision must identify its own question and concrete alternative; historical reports are explicitly separated from current assertions. The queue closes only when the evidence justifies a final outcome, not when a test happens to pass.

Property-chain facts include source-native, target-native, and mapping chains with distinct provenance labels, ordered members, and resulting superproperty. Native facts include chains involving the reviewed property or a named superproperty, equivalent property, or inverse reachable by the existing structural traversal; target facts apply the same rule to each reviewed target. Mapping-chain facts preserve workbook RowIDs. A chain always entails its head from the member path, never an arbitrary path from a head edge. For example, the `hosts` packet includes the source-native `ssn:inDeployment o ssn:deployedSystem -> sosa:hosts` separately from the mapping chain. Stored packet comparison rejects removal of these facts just as it rejects altered row identities or stale input hashes.

## Materially complete review evidence

A review packet should contain all readily computable source, target and mapping facts that could materially change the answer to its stated review question, including relevant incoming and grouped axioms. This standard does not claim that a packet contains every ontology axiom or every possible entailment. Outgoing-neighborhood extraction alone is insufficient: a material fact may have another class or property as its syntactic subject. Packets are evidence aids, not semantic decision engines; questions that exceed the retained evidence must remain open or cite additional evidence.

The local extractor retains outgoing logical axioms and annotations, incoming named hierarchy/equivalence/inverse/disjointness statements, and named axioms whose anonymous expressions directly mention the reviewed term. It follows anonymous expression and list structure to the enclosing named axiom, including existential/universal/value/cardinality restrictions on a reviewed property and restrictions using a reviewed class as filler. It stops at that named subject rather than expanding unrelated named neighborhoods. An incoming `Child subClassOf ReviewedClass` stays in that direction; it is not reported as a superclass of ReviewedClass or as a universal restriction on all ReviewedClass instances. `owl:SymmetricProperty` remains an asserted type. Relevant `owl:AllDisjointClasses` groups retain their complete `owl:members` lists, separately from direct and incoming `owl:disjointWith` facts.

Every contextual fact carries `source_native` or `target_native` provenance and an asserted status. Workbook rows and chains carry mapping provenance and their RowIDs. Derived facts are stored separately as `generated_inference`, with the origin of their premises, the bounded inference method and exact asserted premises. Advisory `domainIncludes`/`rangeIncludes` annotations stay nonlogical. These provenance labels describe where evidence comes from; they neither approve a mapping nor assert that a historical reasoner result is current.

The `inCondition` packet illustrates the assertion/consequence distinction. The unchanged source and workbook have no explicit `rdfs:range` assertion for that property. The current mapping workbook asserts a domain union of `OperatingRange`, `SurvivalRange` and `SystemCapability` (RowID `urn:uuid:79e12baa-9467-4494-bdf3-b6906f5a81a7`); this domain is not a source-native assertion. The source restricts all `inCondition` values to `Condition` for each of those three classes. Taken together, those source and mapping premises entail that every `inCondition` object is a `Condition` in the aligned theory. The packet displays all three restrictions and the mapping domain with separate provenance, then explains this consequence separately from asserted facts. It does not claim the source alone entails a global range. The retained question about an omitted explicit range must be read with this clarification; it does not start from an absence of aligned object typing and does not authorize adding a mapping row. The bounded derivation requires a universal restriction in every domain branch; existentials, cardinalities or an uncovered branch do not suffice.

## Candidate publication-readiness criterion

The current track can be the principal empirical subject only when all twelve conditions hold:

1. Exact current source/target bytes and recoverable provenance are frozen; unknown upstream commits are explicitly unknown.
2. The dynamically computed source inventory equals the assessment inventory exactly.
3. Every source term has a defensible final assessment.
4. No source term remains deferred or unreviewed.
5. Formal coverage is reported independently of assessment completeness, including typing-only and absent routes.
6. Publication-critical mappings have adequate, supported rationales, including deliberate strengthening and cross-track disagreements.
7. Approximate deductive differences on both source and target signatures have a reviewed result; unexpected differences fail readiness. This is not model-theoretic conservativity.
8. Every exact-closure source example has a current source-only and aligned result, with failures classified separately.
9. Selected approved positive and negative semantic expectations have current results; unapproved expectations remain proposals.
10. Assertion-bearing and legitimate zero-axiom rows have coherent identities and assessment dispositions; unexplained missing assertions fail.
11. The declared full repository validation gate passes in the intended environment; blockers and unexecuted checks are visible.
12. All evidence is bound to the current HEAD and exact source, target, workbook, and product hashes, and the protected SOSA-2023 and COMS artifacts are unchanged.

Structural completeness is necessary but does not establish publication readiness. While any semantic decision remains unresolved, the verdict is **CURRENT TRACK NOT YET PUBLICATION READY — HUMAN SEMANTIC REVIEW REQUIRED**. An independent read-only audit is required before making a publication-readiness claim.

## Appendix: retained decisions with material C/N differences

Two current decisions remain final on the strength of their explicit historical retain decisions, but differ materially from the pinned N track. They are documented here separately from the **79 unresolved current source-term decisions**. A different source definition or target snapshot can support a different mapping conclusion; disagreement alone does not reopen an accepted current decision or authorize changing either workbook. “Final” records the accepted current outcome, not a claim that its interpretation is risk-free or that all publication validation has passed.

| Term | Current C workbook (`mappings/SSN2BFO-COMS.xlsx`) | Pinned N workbook (`mappings/SOSA-next-to-BFO-COMS.xlsx`) |
|---|---|---|
| `sosa:actsOnProperty` | `Sheet2!5`, RowID `urn:uuid:69e972da-23ad-4e50-822b-e41198c95795`: `rdfs:subPropertyOf cco:affects` (`cco:ont00001834`). | `Sheet2!13`, RowID `urn:uuid:27ce3724-23eb-4a3d-b2a1-e2615a139a81`: `no_direct_mapping`. Its rationale rejects a uniform relation across the specifically-dependent-continuant and ProcessProfile readings of N `sosa:Property`. |
| `sosa:isActedOnBy` | `Sheet2!20`, RowID `urn:uuid:8c9662e8-a69c-4ce1-9d17-381ec3cdc162`: `rdfs:subPropertyOf cco:is_affected_by` (`cco:ont00001886`). | `Sheet2!40`, RowID `urn:uuid:9ecbbdbb-c876-43c8-89b1-271ee720b45f`: `no_direct_mapping`. Its rationale rejects process-oriented inverse affects for a capability relation whose object is an Actuator. |

**Exact source difference.** In current `imports/sosa.ttl`, `actsOnProperty` is defined as “Relation between an Actuation and the property of a FeatureOfInterest it is acting upon.” Its declared inverse `isActedOnBy` is “Relation between an ActuatableProperty of a FeatureOfInterest and an Actuation changing its state.” The advisory signatures are Actuation → ActuatableProperty and ActuatableProperty → Actuation. In `src/sosa-next/imports/sosa-actuation.ttl`, `actsOnProperty` is “relation from an Actuation to the Property it acted upon” and is inverse to **`wasActedOnBy`**; its advisory domain also includes ActuationCollection. N `isActedOnBy` instead means “relation from a Property to an Actuator that may change its state” and is inverse to **`actsOn`**. Thus the identically spelled `isActedOnBy` has different process-versus-capability meaning across the sources. Advisory signature annotations are not asserted global OWL domains/ranges.

**Exact target difference.** Current `imports/cco.ttl` defines `cco:ont00001834` (`affects`) as a Process influencing a Continuant, typically producing a change, and asserts Process domain / Continuant range. Its inverse `cco:ont00001886` has Continuant domain / Process range. The N target, `src/sosa-next/imports/cco.ttl`, retains the same IRIs but its textual `is affected by` definition specifies an Independent Continuant other than a Spatial Region. The N workbook rationale summarizes that textual condition as an Independent Continuant requirement. The actual N OWL domain of `is affected by` and range of `affects` is broader than that textual summary: **SpecificallyDependentContinuant or GenericallyDependentContinuant or (IndependentContinuant and not SpatialRegion)**. This exact definition/signature distinction is retained as a comparison caveat; no N rationale or ontology is rewritten here. Both target signatures exclude the ProcessProfile category.

**Accepted current decision and remaining caveat.** `reports/isActedOnBy-actsOnProperty-full-closure-analysis.md`, “Recommendation,” explicitly retains both current mappings; its interpretation section distinguishes a process changing a property from an agent/device making an actuation. `reports/inverse-side-direct-mapping-policy-review.md`, “Decision,” separately retains the inverse-side assertion. The pair report also explicitly acknowledges that current `sosa:ActuatableProperty` permits a ProcessProfile branch whereas CCO `affects` requires a Continuant. A current `actsOnProperty` edge therefore selects the continuant-compatible branch for its object; it does not preserve an unrestricted process-profile interpretation of that edge. Historical consistency checks do not establish that this restriction captures every intended use, and their normalized closure is not fresh exact-closure publication evidence.

The accepted outcome remains a deliberate current interpretation with that documented limitation. The narrower current actuation/property pattern and N's changed capability relation explain why N's decisions are not transferable automatically; they do not supply a new proof of global semantic adequacy. A future human decision may explicitly reopen the current pair if the required scope includes acting on ProcessProfiles. Such a change must address the `ActuatableProperty` interpretation, the target signature, and the inverse pair together, and requires approval before any predicate or target changes. No additional unresolved term, formal axiom, or semantic conclusion is silently introduced by this appendix.
