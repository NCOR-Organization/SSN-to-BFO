# Current SSN/SOSA human semantic review

**66 finite unresolved source-term decisions.** Ordered: blanks, typing-only terms, strong equivalences, complex expressions, existentials, chains, cross-track differences, remaining target commitments.

Workbook assertions remain unchanged. Repository facts and logical consequences below are separated from proposed alternatives. Recommendations do not approve a semantic change. Historical report claims are not current validation results. The JSON companion contains every RowID, bounded material source/target facts, exact target definitions, coverage path, and input hash. These evidence aids do not claim every ontology axiom or decide semantic adequacy. Incoming relations, restrictions and grouped disjointness retain their asserted subject and direction; derived evidence is separately labelled with its premises. Relevant source-native, target-native, and mapping property chains retain their distinct origins, ordered members, and resulting superproperties. Each chain runs from a member path to its superproperty; it does not decompose a superproperty edge.

Target facts are deduplicated in the glossary after the queue; each item identifies its exact target IRIs. A missing direct target means no BFO/CCO relation was adopted, not an invitation to manufacture one. N-track comparisons are evidence to consider, not instructions to copy a different source/target interpretation.

## Decision index

| Priority | Source | Question |
|---|---|---|
| 1 | `ssn:implementedBy` | Is the authorized external implementation faithful to the historical process-mediated inference and current OWL 2 DL requirements? Focused execution and logical checks pass. |
| 2 | `sosa:hasFeatureOfInterest` | Does relating an execution to what its result concerns warrant any target relation, or is source domain/range typing the complete intended mapping outcome? |
| 2 | `sosa:isFeatureOfInterestOf` | Can the inverse FeatureOfInterest-to-execution relation receive a sound target inclusion across material, process, and property-like features, or should it remain no-direct? |
| 2 | `sosa:isObservedBy` | Should the inverse capability relation be final no-direct, following observes, rather than be treated as a relation mapping solely because its domain/range are present? |
| 2 | `sosa:madeActuation` | Is current Actuator-to-Actuation typing the final outcome or a deferred agent relation? The pinned track adopts agent_in, while historical current-track tests documented conflicts. |
| 2 | `sosa:madeByActuator` | Should the absent has_agent inclusion be classified as semantic rejection or implementation/profile deferral for this exact source/target closure? |
| 2 | `sosa:observes` | Does capability-level observes need only its native forProperty hierarchy and typing, or is another target route intended? The chain headed by forProperty does not map arbitrary observes assertions outward. |
| 2 | `ssn:hasProperty` | Is no uniform target superproperty the final decision, with the two typed branches supplied only by the external query? |
| 2 | `ssn:implements` | Is the authorized external implementation faithful to the historical process-mediated inference and current OWL 2 DL requirements? Focused execution and logical checks pass. |
| 2 | `ssn:isPropertyOf` | Should the inverse of the mixed continuant/occurrent hasProperty relation remain no-direct, and is an inverse conditional query needed as separate future work? |
| 2 | `ssn:isProxyFor` | Does the source relation from a Stimulus to a detectable Property justify a target relation, or only the present source typing? |
| 2 | `ssn-system:hasOperatingRange` | Should a System-to-OperatingRange relation have a fixed bearer relation when OperatingRange also permits ProcessProfile, or only conditional query support? |
| 2 | `ssn-system:hasSurvivalRange` | Is a uniform System-to-SurvivalRange bearer relation justified by the current Function realization mapping, or is domain/range plus a conditional route the intended final state? |
| 2 | `ssn-system:hasSystemCapability` | Does every SystemCapability qualify for a uniform bearer relation despite its continuant-or-ProcessProfile union, or must the conditional query remain separate? |
| 2 | `ssn-system:inCondition` | Is a domain-only row an intentional final outcome for the relation to environmental Conditions, and is the omitted range intentional? |
| 3 | `sosa:Actuation` | Does every PlannedAct affecting an ActuatableProperty qualify as a SOSA Actuation, or are those only necessary conditions? |
| 3 | `sosa:Result` | Does every result have to be information content or a material entity, and does every such output of the listed executions qualify as a SOSA Result? |
| 3 | `sosa:Sample` | Must all current SOSA Samples be material and objects of Sampling, and are those conditions sufficient for samplehood, including statistical samples in source examples? |
| 3 | `sosa:Sampler` | Should the earlier explicit necessary-and-sufficient Sampler decision remain final given unused samplers and the pinned track’s removal of actual Sampling existentials? |
| 3 | `sosa:Sampling` | Are a PlannedAct, an actual prescribed Procedure, and an output Sample jointly sufficient for Sampling rather than merely necessary? |
| 3 | `ssn:Property` | Is every BFO specifically dependent continuant and every ProcessProfile necessarily an SSN Property, as the equivalence asserts? |
| 3 | `ssn:Stimulus` | Is every cause of an Observation a detectable change that qualifies as a source Stimulus, or only some causes? |
| 4 | `sosa:ActuatableProperty` | Does every actuatable property actually inhere in or form an occurrent part of a FeatureOfInterest, and do the two BFO branches exhaust its source meaning? |
| 4 | `sosa:Actuator` | Can an unused Actuator exist without an actual Actuation, despite the current realization and agent_in existential commitments? |
| 4 | `sosa:FeatureOfInterest` | Is the four-category union a deliberate necessary upper bound for every FeatureOfInterest, including abstract or informational features, and does the wording “direct alignment deferred” accurately describe an active axiom? |
| 4 | `sosa:ObservableProperty` | Does every observable property require an actual bearer/process FeatureOfInterest through exactly these two relations, rather than just being a quality that can be observed? |
| 4 | `sosa:Procedure` | Does every reusable Procedure prescribe an actual Process, or does the source support only its information-content category? |
| 4 | `sosa:Sensor` | Does the current Sensor interpretation require actual Observation and agency, or should an unused capable sensor qualify without actual realization? |
| 4 | `ssn-system:Accuracy` | Does accuracy in comparison with a reference justify the current commitment to Function, an actual Process, descriptive content, and a VeracityMeasurementInformationContentEntity, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:ActuationRange` | Does the range of actuation values justify the current commitment to Function and an actual Actuation producing a specifically dependent continuant under an ArtifactFunctionSpecification, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:BatteryLifetime` | Does total useful battery life justify the current commitment to Function, an actual operational stasis containing Power, and a causal process realizing a design-prescribed Affordance, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Condition` | Does environmental conditions affecting performance justify the current commitment to SDC-or-ProcessProfile plus an actual PerformanceSpecification, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:DetectionLimit` | Does the smallest detectable change justify the current commitment to Function and a VeracityMeasurementInformationContentEntity, using the same pattern as Accuracy, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Drift` | Does change in response over time justify the current commitment to Function and a DeviationMeasurementInformationContentEntity through an actual realization/description, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Frequency` | Does the smallest time between consecutive observations justify the current commitment to Function with an actual PlannedAct having a Frequency process part prescribed by a function specification, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Latency` | Does elapsed time before an observation result is available justify the current commitment to Function with an actual PlannedAct, both Cause and Effect process parts, and a prescribed occupied TemporalRegion, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:MaintenanceSchedule` | Does maintenance needed to keep a system operating justify the current commitment to Disposition with an actual Change affecting a dependent continuant that participates in actual maintenance with a design-prescribed Frequency, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:OperatingPowerRange` | Does power conditions for operation justify the current commitment to Function with an actual Process whose Power part is prescribed by an ArtifactDesign, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:OperatingProperty` | Does an identifiable characteristic of normal operation justify the current commitment to SDC-or-ProcessProfile and actual prescription by an ArtifactDesign, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:OperatingRange` | Does conditions within which operation is expected justify the current commitment to SDC-or-ProcessProfile and actual prescription by an ArtifactDesign, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Precision` | Does repeatability or consistency of observations justify the current commitment to Function and a ReliabilityMeasurementInformationContentEntity through actual realization and description, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Resolution` | Does the smallest distinguishable change justify the current commitment to Function and a DeviationMeasurementInformationContentEntity, using the same target pattern as Drift, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:ResponseTime` | Does time from stimulus change to settled result justify the current commitment to Function and an actual PlannedAct with Cause/Effect parts, using the same target pattern as Latency, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Selectivity` | Does distinguishing a Property from other influences justify the current commitment to Function with an actual PlannedAct and a participating Continuant prescribed by an ArtifactFunctionSpecification, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:Sensitivity` | Does change in result relative to change in observed property justify the current commitment to Function and a RatioMeasurementInformationContentEntity through actual realization and description, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:SurvivalProperty` | Does extent of useful life under specified conditions justify the current commitment to Function with an actual realization caused by another Process realizing a design-prescribed Affordance, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:SurvivalRange` | Does conditions under which a System can be exposed without damage justify the current commitment to Function with an actual realization and causal/design Affordance chain, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:SystemCapability` | Does capability of a system under conditions justify the current commitment to SDC-or-ProcessProfile and an actual PerformanceSpecification describing its condition, or does it describe a property/capability without those actual individuals? |
| 4 | `ssn-system:SystemLifetime` | Does useful system life justify the current commitment to Function with an actual operational stasis caused by a Process realizing a design-prescribed Affordance, or does it describe a property/capability without those actual individuals? |
| 6 | `sosa:hosts` | Does every bearer-realization-participant path establish hosting, and does the current chain direction match the intended platform-support interpretation? |
| 6 | `sosa:isHostedBy` | Does every participates_in-realizes-inheres_in path establish being hosted, and is it the intended inverse of the hosts-chain interpretation? |
| 7 | `sosa:madeBySensor` | Does the current implementation preserve the historically authorized treatment? The focused recovery checks confirm it. |
| 7 | `sosa:madeObservation` | Does the current implementation preserve the historically authorized treatment? The focused recovery checks confirm it. |
| 7 | `sosa:phenomenonTime` | Must the time to which a result applies equal the temporal region occupied by the observation/actuation/sampling itself? |
| 7 | `sampling:natureOfRelationship` | Does connecting a relationship to its nature express CCO aboutness between information content and its subject, or classify the relationship instead? |
| 7 | `ssn:wasOriginatedBy` | Does every originating Stimulus temporally start the Observation, as CCO process_started_by requires, or does source meaning establish only causation? |
| 8 | `sampling:RelationshipNature` | Is the nature of a sample relationship an information-content entity, or does the source Concept class permit a broader conceptual/category interpretation? |
| 8 | `ssn:Input` | Does every Input to a Procedure denote information content, or can the source class also denote a concrete input object/specification of such an object? |
| 8 | `ssn:Output` | Does every Output of a Procedure denote information content rather than a concrete thing described as output? |
| 8 | `ssn:deployedOnPlatform` | Does every Deployment-to-Platform relation require that the Platform participate in a process under the chosen PlannedAct reading? |
| 8 | `ssn:deployedSystem` | Does every Deployment-to-System relation establish participation in a process under the source arrangement/deployment interpretation? |
| 8 | `ssn:detects` | Does the source sensor-detects-stimulus relation always mean the sensor is causally affected by that stimulus in CCO’s sense? |
| 8 | `ssn-system:hasOperatingProperty` | Does OperatingRange-to-Property use require the Property to specifically depend on that container, and is the BFO dependence direction/category valid for all its source cases? |
| 8 | `ssn-system:hasSurvivalProperty` | Does SurvivalRange-to-Property use require the Property to specifically depend on that container, and is the BFO dependence direction/category valid for all its source cases? |
| 8 | `ssn-system:hasSystemProperty` | Does SystemCapability-to-Property use require the Property to specifically depend on that container, and is the BFO dependence direction/category valid for all its source cases? |
| 8 | `ssn-system:qualityOfObservation` | Is the quality associated with an Observation necessarily an output produced by that process, or a quality/description of it? |

## ssn:implementedBy

State: **unreviewed**; priority 1; evidence confidence: Historical authority, explicit implementation authorization and focused technical validation verified; administrative review state unchanged..

**Repository facts — mapping:**

- `Sheet2!57` / `urn:uuid:4afaf231-5478-4a50-9a12-0cbf59d78d7e`: `[blank]` (zero axioms).

**Source semantics:** Relation between a Procedure (an algorithm, procedure or method) and an entity that implements that Procedure in some executable way.

Source structure: owl:inverseOf ssn:implements; rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping.

**Logical consequences:** ssn:implementedBy contributes zero mapping axioms; native source axioms remain present.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Procedure rdfs:subClassOf (ssn:implementedBy owl:allValuesFrom ssn:System)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `sosa:madeByActuator o ssn:implements -> sosa:usedProcedure`.
- `source_native`: `sosa:madeBySampler o ssn:implements -> sosa:usedProcedure`.
- `source_native`: `sosa:madeBySensor o ssn:implements -> sosa:usedProcedure`.

Additional route evidence: [{"artifact": "rules/ssn-implementation-mapping.rq", "artifact_sha256": "c1d3ea7afd47369782f81e38f0ad21272bf419a5d89defc176c7e82e09f3f2dd", "mode": "external_construct_rule", "conditions": "Explicit or previously materialized CCO prescribes followed by has_agent yields ssn:implementedBy and inverse ssn:implements assertions. Requires executing the query; not an OWL-product entailment or a direct prescription inclusion."}]

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!35`: `sosa:implementedBy` — `active`, `owl:propertyChainAxiom` cco:prescribes o cco:has_agent. Replace the misdirected chain with cco:prescribes o cco:has_agent. The pinned CCO confirms that prescribes is inverse to prescribed_by and has_agent is inverse to agent_in. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Is the authorized external implementation faithful to the historical process-mediated inference and current OWL 2 DL requirements? Focused execution and logical checks pass.

**Alternatives:**
- Retain the explicitly authorized external rule and historical typing representative.

**Proposed recommendation:** Use the separately executed external rule; do not restore the impermissible OWL chain or the non-equivalent direct prescription inclusions.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!57`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/implementedBy`; `imports/cco.ttl`; `reports/hosts-implementedby-complex-mapping-review.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`; `reports/current-semantic-workbook/transitions/035e5877-1b9d-444c-a970-239ce3bcb97c.json`; `rules/ssn-implementation-mapping.rq`; `reports/current-semantic-workbook/implementation-rule-2026-10-30/authorized-instructions.txt`; `reports/current-semantic-workbook/implementation-rule-2026-10-30/after-rule/validation-result.json`.

**Notes:** Explicit implementation authorization, Alec Sculley, 2026-10-30. Preserve the historical process-mediated interpretation using a separate SPARQL CONSTRUCT rule because the OWL chain fails current DL global restrictions. This does not create a new scientific decision or finalize the assessment. External-rule mapping coverage is separate from direct OWL inclusion and the retained implements domain typing. Current and SOSA-2023 tracks remain separately governed.

## sosa:hasFeatureOfInterest

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!6` / `urn:uuid:b16f1d3a-3d10-4b75-9f12-2331e6c46d74`: `rdfs:domain` (sosa:Observation or sosa:Actuation or sosa:Sampling).

- `Sheet2!7` / `urn:uuid:01b1aff2-a12b-430b-9775-b43241c3a7cf`: `rdfs:range` sosa:FeatureOfInterest.

**Source semantics:** A relation between an Observation and the entity whose quality was observed, or between an Actuation and the entity whose property was modified, or between an act of Sampling and the entity that was sampled.

Source structure: owl:inverseOf sosa:isFeatureOfInterestOf; rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Actuation; <http://schema.org/domainIncludes> sosa:Observation; <http://schema.org/domainIncludes> sosa:Sampling; <http://schema.org/rangeIncludes> sosa:FeatureOfInterest; <http://schema.org/rangeIncludes> sosa:Sample

**Target semantics:** No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping.

**Logical consequences:** An asserted sosa:hasFeatureOfInterest(x,y) types x as (sosa:Observation or sosa:Actuation or sosa:Sampling); no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:hasFeatureOfInterest(x,y) types y as sosa:FeatureOfInterest; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `sosa:Sampling rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `sosa:Sampling rdfs:subClassOf (sosa:hasFeatureOfInterest owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:hasFeatureOfInterest rdfs:range sosa:FeatureOfInterest`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:hasFeatureOfInterest rdfs:domain (sosa:Observation or sosa:Actuation or sosa:Sampling)` (RowID `urn:uuid:b16f1d3a-3d10-4b75-9f12-2331e6c46d74`).
- `source_native`: `sosa:Actuation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native`: `sosa:Observation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native`: `sosa:Sampling rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!21`: `sosa:hasFeatureOfInterest` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:hasFeatureOfInterest is a polymorphic subject relation from an Execution or Deployment to its FeatureOfInterest: depending on the source subtype, the feature may be observed, acted on, sampled, or targeted by a deployment. BFO participation is not entailed for all such features, CCO process-object relations impose stronger conditions, and CCO aboutness requires an Information Content Entity subject. No single reviewed target relation uniformly captures the source semantics. Comparison basis: same lexical term.

**Human decision:** Does relating an execution to what its result concerns warrant any target relation, or is source domain/range typing the complete intended mapping outcome?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Adopt no_direct_mapping while retaining source typing, or justify a specific process-to-subject/aboutness pattern that covers all Observation, Actuation, and Sampling uses.

**Proposed recommendation:** Retain the artifact during review. Adopt no_direct_mapping while retaining source typing, or justify a specific process-to-subject/aboutness pattern that covers all Observation, Actuation, and Sampling uses.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!6`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!7`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/hasFeatureOfInterest`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/hasFeatureOfInterest`; `imports/cco.ttl`; `reports/object-property-domain-range-fallback-policy-audit.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:isFeatureOfInterestOf

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!9` / `urn:uuid:b5a532fc-5dea-4a47-9323-0a78a849c078`: `rdfs:domain` sosa:FeatureOfInterest.

- `Sheet2!10` / `urn:uuid:e15cfee1-3c8e-4519-bce0-ec62729fd2fd`: `rdfs:range` (sosa:Observation or sosa:Actuation or sosa:Sampling).

**Source semantics:** A relation between a FeatureOfInterest and an Observation about it, an Actuation acting on it, or an act of Sampling that sampled it.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:FeatureOfInterest; <http://schema.org/domainIncludes> sosa:Sample; <http://schema.org/rangeIncludes> sosa:Actuation; <http://schema.org/rangeIncludes> sosa:Observation; <http://schema.org/rangeIncludes> sosa:Sampling

**Target semantics:** No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping.

**Logical consequences:** An asserted sosa:isFeatureOfInterestOf(x,y) types x as sosa:FeatureOfInterest; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:isFeatureOfInterestOf(x,y) types y as (sosa:Observation or sosa:Actuation or sosa:Sampling); no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:hasFeatureOfInterest owl:inverseOf sosa:isFeatureOfInterestOf`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!42`: `sosa:isFeatureOfInterestOf` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:isFeatureOfInterestOf is the inverse polymorphic relation from a FeatureOfInterest to an Execution, ExecutionCollection, or Deployment for which it is the subject. Reversing participation, process-object, or aboutness candidates does not remove their unsupported participation, agentive-object, or Information Content Entity conditions. No reviewed target relation uniformly captures the source semantics. Comparison basis: same lexical term.

**Human decision:** Can the inverse FeatureOfInterest-to-execution relation receive a sound target inclusion across material, process, and property-like features, or should it remain no-direct?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Record no_direct_mapping with the inverse source signature, or first approve a forward hasFeatureOfInterest interpretation and derive its inverse.

**Proposed recommendation:** Retain the artifact during review. Record no_direct_mapping with the inverse source signature, or first approve a forward hasFeatureOfInterest interpretation and derive its inverse.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!9`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!10`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/isFeatureOfInterestOf`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/isFeatureOfInterestOf`; `imports/cco.ttl`; `reports/object-property-domain-range-fallback-policy-audit.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:isObservedBy

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!21` / `urn:uuid:d5712b64-a526-4112-ba23-520ec8dc5066`: `rdfs:domain` sosa:ObservableProperty.

- `Sheet2!22` / `urn:uuid:37fac05e-0d70-420d-a0c0-78bc1d87cd63`: `rdfs:range` sosa:Sensor.

**Source semantics:** Relation between an ObservableProperty and the Sensor able to observe it.

Source structure: owl:inverseOf sosa:observes; rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:ObservableProperty; <http://schema.org/rangeIncludes> sosa:Sensor

**Target semantics:** `bfo:BFO_0000056` (participates in; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted sosa:isObservedBy(x,y) types x as sosa:ObservableProperty; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:isObservedBy(x,y) types y as sosa:Sensor; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:ObservableProperty rdfs:subClassOf (sosa:isObservedBy owl:allValuesFrom sosa:Sensor)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:isObservedBy rdfs:range sosa:Sensor`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:isObservedBy rdfs:domain sosa:ObservableProperty` (RowID `urn:uuid:d5712b64-a526-4112-ba23-520ec8dc5066`).
- `source_native`: `sosa:ObservableProperty rdfs:subClassOf (sosa:isObservedBy owl:allValuesFrom sosa:Sensor)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!45`: `sosa:isObservedBy` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:isObservedBy is a capability-level relation from a Property to a Sensor able to observe it. Reversing BFO/CCO process relations still produces a Process relatum rather than a Sensor, while capability and disposition relations do not relate the Property being sensed to the bearer of the capability. No reviewed BFO/CCO relation preserves the SOSA semantics and signature. Comparison basis: same lexical term.

**Human decision:** Should the inverse capability relation be final no-direct, following observes, rather than be treated as a relation mapping solely because its domain/range are present?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Record the inverse capability interpretation with no_direct_mapping, or evaluate an approved forward observes mapping before deriving an inverse target.

**Proposed recommendation:** Retain the artifact during review. Record the inverse capability interpretation with no_direct_mapping, or evaluate an approved forward observes mapping before deriving an inverse target.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!21`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!22`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/isObservedBy`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/isObservedBy`; `imports/cco.ttl`; `reports/isObservedBy-observes-full-closure-analysis.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:madeActuation

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!26` / `urn:uuid:01085646-1b07-4c69-a39a-0c5c8ab53d33`: `rdfs:domain` sosa:Actuator.

- `Sheet2!27` / `urn:uuid:0f9d6fa9-00b9-4602-b31d-9e205f53e67d`: `rdfs:range` sosa:Actuation.

**Source semantics:** Relation between an Actuator and the Actuation it has made.

Source structure: owl:inverseOf sosa:madeByActuator; rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Actuator; <http://schema.org/rangeIncludes> sosa:Actuation

**Target semantics:** `cco:ont00001787` (agent in; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted sosa:madeActuation(x,y) types x as sosa:Actuator; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:madeActuation(x,y) types y as sosa:Actuation; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuator rdfs:subClassOf (sosa:madeActuation owl:allValuesFrom sosa:Actuation)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:madeActuation rdfs:range sosa:Actuation`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:madeActuation rdfs:domain sosa:Actuator` (RowID `urn:uuid:01085646-1b07-4c69-a39a-0c5c8ab53d33`).
- `source_native`: `sosa:Actuator rdfs:subClassOf (sosa:madeActuation owl:allValuesFrom sosa:Actuation)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `sosa:madeByActuator o ssn:implements -> sosa:usedProcedure`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!57`: `sosa:madeActuation` — `active`, `rdfs:subPropertyOf` cco:agent_in.  Comparison basis: same lexical term.

**Human decision:** Is current Actuator-to-Actuation typing the final outcome or a deferred agent relation? The pinned track adopts agent_in, while historical current-track tests documented conflicts.

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain typing with an explicit deferred/no-direct outcome, or request a separately approved current-closure trial of agent_in; do not copy the pinned-track result.

**Proposed recommendation:** Retain the artifact during review. Retain typing with an explicit deferred/no-direct outcome, or request a separately approved current-closure trial of agent_in; do not copy the pinned-track result.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!26`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!27`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/madeActuation`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/madeActuation`; `imports/cco.ttl`; `reports/actuation-agent-property-mapping-deferral.md`; `reports/madeByActuator-agent-mapping-adjustment-evaluation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:madeByActuator

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!28` / `urn:uuid:675bb221-ad63-4033-9f22-5190d0b6d545`: `rdfs:domain` sosa:Actuation.

- `Sheet2!29` / `urn:uuid:ac95c1e2-0d93-48de-be9d-4defbe6525f0`: `rdfs:range` sosa:Actuator.

**Source semantics:** Relation linking an Actuation to the Actuator that made that Actuation.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Actuation; <http://schema.org/rangeIncludes> sosa:Actuator

**Target semantics:** `cco:ont00001833` (has agent; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted sosa:madeByActuator(x,y) types x as sosa:Actuation; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:madeByActuator(x,y) types y as sosa:Actuator; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:madeByActuator owl:allValuesFrom sosa:Actuator)`.
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:madeByActuator owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `sosa:madeActuation owl:inverseOf sosa:madeByActuator`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:madeByActuator rdfs:range sosa:Actuator`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:madeByActuator rdfs:domain sosa:Actuation` (RowID `urn:uuid:675bb221-ad63-4033-9f22-5190d0b6d545`).
- `source_native`: `sosa:Actuation rdfs:subClassOf (sosa:madeByActuator owl:allValuesFrom sosa:Actuator)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `sosa:madeByActuator o ssn:implements -> sosa:usedProcedure`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!58`: `sosa:madeByActuator` — `active`, `rdfs:subPropertyOf` cco:has_agent.  Comparison basis: same lexical term.

**Human decision:** Should the absent has_agent inclusion be classified as semantic rejection or implementation/profile deferral for this exact source/target closure?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Keep source Actuation-to-Actuator typing and record the chosen disposition; any has_agent restoration requires a new approved semantic change and exact-closure evidence.

**Proposed recommendation:** Retain the artifact during review. Keep source Actuation-to-Actuator typing and record the chosen disposition; any has_agent restoration requires a new approved semantic change and exact-closure evidence.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!28`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!29`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/madeByActuator`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/madeByActuator`; `imports/cco.ttl`; `reports/actuation-agent-property-mapping-deferral.md`; `reports/madeByActuator-range-after-agent-deferral.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:observes

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!23` / `urn:uuid:61fc3404-f33a-4c4c-a25c-412d9972016c`: `rdfs:domain` sosa:Sensor.

- `Sheet2!24` / `urn:uuid:5ce06556-de99-44be-922d-a3d092a00dbb`: `rdfs:range` sosa:ObservableProperty.

**Source semantics:** Relation between a Sensor and an ObservableProperty that it is capable of sensing.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:forProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Sensor; <http://schema.org/rangeIncludes> sosa:ObservableProperty

**Target semantics:** `bfo:BFO_0000057` (has participant; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted sosa:observes(x,y) types x as sosa:Sensor; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:observes(x,y) types y as sosa:ObservableProperty; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Sensor rdfs:subClassOf (sosa:observes owl:allValuesFrom sosa:ObservableProperty)`.
- `source_native` / asserted: `sosa:isObservedBy owl:inverseOf sosa:observes`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:observes rdfs:range sosa:ObservableProperty`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:observes rdfs:domain sosa:Sensor` (RowID `urn:uuid:61fc3404-f33a-4c4c-a25c-412d9972016c`).
- `source_native`: `sosa:Sensor rdfs:subClassOf (sosa:observes owl:allValuesFrom sosa:ObservableProperty)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!68`: `sosa:observes` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:observes is a capability-level relation from a Sensor to a Property that the sensor is capable of sensing. BFO/CCO process relations require a Process subject, while CCO capability and disposition relations relate a bearer to an Agent Capability or Disposition rather than to the Property that capability concerns. No reviewed BFO/CCO relation preserves the SOSA semantics and signature. Comparison basis: same lexical term.

**Human decision:** Does capability-level observes need only its native forProperty hierarchy and typing, or is another target route intended? The chain headed by forProperty does not map arbitrary observes assertions outward.

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Finalize no_direct_mapping for a target superproperty while retaining native observes subPropertyOf forProperty; do not equate capability with actual process participation.

**Proposed recommendation:** Retain the artifact during review. Finalize no_direct_mapping for a target superproperty while retaining native observes subPropertyOf forProperty; do not equate capability with actual process participation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!23`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!24`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/observes`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/observes`; `imports/cco.ttl`; `reports/observes-upper-mapping-decision.md`; `reports/hasproperty-observes-mapping-review.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn:hasProperty

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!55` / `urn:uuid:43ad1a14-e8a4-48d5-ae2b-3b5a5b28f8d3`: `rdfs:range` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile).

**Source semantics:** Relation between an entity and a Property of that entity.

Source structure: owl:inverseOf ssn:isPropertyOf; rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000117` (has occurrent part; historical_or_review_candidate_only; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `bfo:BFO_0000196` (bearer of; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted ssn:hasProperty(x,y) types y as (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile); no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:FeatureOfInterest rdfs:subClassOf (ssn:hasProperty owl:allValuesFrom ssn:Property)`.
- `source_native` / asserted: `sosa:FeatureOfInterest rdfs:subClassOf (ssn:hasProperty owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn-system:hasOperatingProperty rdfs:subPropertyOf ssn:hasProperty`.
- `source_native` / asserted: `ssn-system:hasOperatingRange rdfs:subPropertyOf ssn:hasProperty`.
- `source_native` / asserted: `ssn-system:hasSurvivalProperty rdfs:subPropertyOf ssn:hasProperty`.
- `source_native` / asserted: `ssn-system:hasSurvivalRange rdfs:subPropertyOf ssn:hasProperty`.
- `source_native` / asserted: `ssn-system:hasSystemCapability rdfs:subPropertyOf ssn:hasProperty`.
- `source_native` / asserted: `ssn-system:hasSystemProperty rdfs:subPropertyOf ssn:hasProperty`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!28`: `sosa:hasProperty` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:hasProperty relates a FeatureOfInterest to a sosa:Property. The governed sosa:Property extension includes both specifically dependent continuants and ProcessProfiles. BFO bearer_of applies only to specifically dependent continuants, and aggregate-bearer relations are likewise category-specific. A uniform subproperty mapping would therefore impose unsupported continuant typing on the ProcessProfile branch. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Is no uniform target superproperty the final decision, with the two typed branches supplied only by the external query?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Finalize no_direct_mapping in OWL and explicitly delimit query eligibility; do not assert both bearer_of and has_occurrent_part globally.

**Proposed recommendation:** Retain the artifact during review. Finalize no_direct_mapping in OWL and explicitly delimit query eligibility; do not assert both bearer_of and has_occurrent_part globally.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!55`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/hasProperty`; `imports/cco.ttl`; `reports/ssn-hasproperty-rule-mapping-artifact.md`; `reports/ssn-hasproperty-modeling-options.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn:implements

State: **unreviewed**; priority 2; evidence confidence: Historical authority, explicit implementation authorization and focused technical validation verified; administrative review state unchanged..

**Repository facts — mapping:**

- `Sheet2!58` / `urn:uuid:6142726b-21b1-4dba-b5ec-a7d6dca4afab`: `rdfs:domain` ssn:System.

**Source semantics:** Relation between an entity that implements a Procedure in some executable way and the Procedure (an algorithm, procedure or method).

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping.

**Logical consequences:** An asserted ssn:implements(x,y) types x as ssn:System; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuator rdfs:subClassOf (ssn:implements owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `sosa:Sampler rdfs:subClassOf (ssn:implements owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `sosa:Sensor rdfs:subClassOf (ssn:implements owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn:implements owl:allValuesFrom sosa:Procedure)`.
- `source_native` / asserted: `ssn:implementedBy owl:inverseOf ssn:implements`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `ssn:implements rdfs:range sosa:Procedure`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `ssn:implements rdfs:domain ssn:System` (RowID `urn:uuid:6142726b-21b1-4dba-b5ec-a7d6dca4afab`).
- `source_native`: `ssn:System rdfs:subClassOf (ssn:implements owl:allValuesFrom sosa:Procedure)`.

**Review clarification:** The current workbook has no explicit rdfs:range row for ssn:implements. The source also has no explicit rdfs:range assertion. The source universal restrictions together with the current mapping's domain row already entail a range constraint; this is an aligned consequence, not a source-only range assertion. An absent explicit row is therefore not evidence of unconstrained objects. Read the retained review question with this distinction; no mapping decision is made.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `sosa:madeByActuator o ssn:implements -> sosa:usedProcedure`.
- `source_native`: `sosa:madeBySampler o ssn:implements -> sosa:usedProcedure`.
- `source_native`: `sosa:madeBySensor o ssn:implements -> sosa:usedProcedure`.

Additional route evidence: [{"artifact": "rules/ssn-implementation-mapping.rq", "artifact_sha256": "c1d3ea7afd47369782f81e38f0ad21272bf419a5d89defc176c7e82e09f3f2dd", "mode": "external_construct_rule", "conditions": "Explicit or previously materialized CCO prescribes followed by has_agent yields ssn:implementedBy and inverse ssn:implements assertions. Requires executing the query; not an OWL-product entailment or a direct prescription inclusion."}]

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!36`: `sosa:implements` — `active`, `owl:propertyChainAxiom` cco:agent_in o cco:prescribed_by. Replace the category-incompatible chain with cco:agent_in o cco:prescribed_by. This follows the path from a system through an execution in which it is an agent to the procedure prescribing that execution. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Is the authorized external implementation faithful to the historical process-mediated inference and current OWL 2 DL requirements? Focused execution and logical checks pass.

**Alternatives:**
- Retain the explicitly authorized external rule and historical typing representative.

**Proposed recommendation:** Use the separately executed external rule; do not restore the impermissible OWL chain or the non-equivalent direct prescription inclusions.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!58`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/implements`; `imports/cco.ttl`; `reports/hosts-implementedby-complex-mapping-review.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`; `reports/current-semantic-workbook/transitions/035e5877-1b9d-444c-a970-239ce3bcb97c.json`; `rules/ssn-implementation-mapping.rq`; `reports/current-semantic-workbook/implementation-rule-2026-10-30/authorized-instructions.txt`; `reports/current-semantic-workbook/implementation-rule-2026-10-30/after-rule/validation-result.json`.

**Notes:** Explicit implementation authorization, Alec Sculley, 2026-10-30. Preserve the historical process-mediated interpretation using a separate SPARQL CONSTRUCT rule because the OWL chain fails current DL global restrictions. This does not create a new scientific decision or finalize the assessment. External-rule mapping coverage is separate from direct OWL inclusion and the retained implements domain typing. Current and SOSA-2023 tracks remain separately governed.

## ssn:isPropertyOf

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!15` / `urn:uuid:02294d3c-f88d-4d3d-921e-8d6c00457476`: `rdfs:domain` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile).

**Source semantics:** Relation between a Property and the entity it belongs to.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000132` (occurrent part of; historical_or_review_candidate_only; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `bfo:BFO_0000197` (inheres in; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted ssn:isPropertyOf(x,y) types x as (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile); no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn:Property rdfs:subClassOf (ssn:isPropertyOf owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `ssn:hasProperty owl:inverseOf ssn:isPropertyOf`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!48`: `sosa:isPropertyOf` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:isPropertyOf relates a sosa:Property to its FeatureOfInterest. Although BFO inheres_in is appropriate for specifically dependent continuants, the governed sosa:Property extension also includes ProcessProfiles, which are occurrent-side entities and do not inhere in a bearer. No reviewed target relation uniformly covers both branches of the source class. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Should the inverse of the mixed continuant/occurrent hasProperty relation remain no-direct, and is an inverse conditional query needed as separate future work?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Finalize no_direct_mapping with retained union-domain typing; the current forward query does not itself consume arbitrary inverse assertions.

**Proposed recommendation:** Retain the artifact during review. Finalize no_direct_mapping with retained union-domain typing; the current forward query does not itself consume arbitrary inverse assertions.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!15`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/isPropertyOf`; `imports/cco.ttl`; `reports/ssn-hasproperty-rule-mapping-artifact.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn:isProxyFor

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!60` / `urn:uuid:ebf4115f-fe96-4959-89a4-98c3a6031cff`: `rdfs:domain` ssn:Stimulus.

- `Sheet2!61` / `urn:uuid:b7873da3-fc78-4a2a-92e1-ef83efb6d600`: `rdfs:range` ssn:Property.

**Source semantics:** A relation from a Stimulus to the Property that the Stimulus is serving as a proxy for.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping.

**Logical consequences:** An asserted ssn:isProxyFor(x,y) types x as ssn:Stimulus; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted ssn:isProxyFor(x,y) types y as ssn:Property; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:ObservableProperty rdfs:subClassOf (inverse(ssn:isProxyFor) owl:allValuesFrom ssn:Stimulus)`.
- `source_native` / asserted: `ssn:Stimulus rdfs:subClassOf (ssn:isProxyFor owl:allValuesFrom sosa:ObservableProperty)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `ssn:isProxyFor rdfs:range sosa:ObservableProperty`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `ssn:isProxyFor rdfs:domain ssn:Stimulus` (RowID `urn:uuid:ebf4115f-fe96-4959-89a4-98c3a6031cff`).
- `source_native`: `ssn:Stimulus rdfs:subClassOf (ssn:isProxyFor owl:allValuesFrom sosa:ObservableProperty)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!49`: `sosa:isProxyFor` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:isProxyFor relates a Stimulus to the Property for which it serves as proxy. CCO represents requires a Representational Information Content Entity subject, and CCO is_about requires an Information Content Entity subject. A SOSA Stimulus is not thereby either kind of information content entity, so the apparent representation candidates have incompatible typing. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Does the source relation from a Stimulus to a detectable Property justify a target relation, or only the present source typing?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Record no_direct_mapping for the Stimulus-to-Property proxy relation unless a specific target relation is defended; do not treat proxying as causal process initiation.

**Proposed recommendation:** Retain the artifact during review. Record no_direct_mapping for the Stimulus-to-Property proxy relation unless a specific target relation is defended; do not treat proxying as causal process initiation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!60`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!61`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/isProxyFor`; `imports/cco.ttl`; `reports/object-property-domain-range-fallback-policy-audit.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn-system:hasOperatingRange

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!38` / `urn:uuid:265137eb-a279-4f9a-b1b9-e85d7ecb02a7`: `rdfs:domain` ssn:System.

- `Sheet2!39` / `urn:uuid:8b87dd5b-298e-4ae7-8724-3778c0a67234`: `rdfs:range` ssn-system:OperatingRange.

**Source semantics:** Relation from a System to an OperatingRange describing the normal operating environment of the System.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:hasProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000117` (has occurrent part; historical_or_review_candidate_only; glossary); `bfo:BFO_0000196` (bearer of; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted ssn-system:hasOperatingRange(x,y) types x as ssn:System; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted ssn-system:hasOperatingRange(x,y) types y as ssn-system:OperatingRange; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf (inverse(ssn-system:hasOperatingRange) owl:allValuesFrom ssn:System)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn-system:hasOperatingRange owl:allValuesFrom ssn-system:OperatingRange)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `ssn-system:hasOperatingRange rdfs:range ssn-system:OperatingRange`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `ssn-system:hasOperatingRange rdfs:domain ssn:System` (RowID `urn:uuid:265137eb-a279-4f9a-b1b9-e85d7ecb02a7`).
- `source_native`: `ssn:System rdfs:subClassOf (ssn-system:hasOperatingRange owl:allValuesFrom ssn-system:OperatingRange)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Human decision:** Should a System-to-OperatingRange relation have a fixed bearer relation when OperatingRange also permits ProcessProfile, or only conditional query support?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Finalize no_direct_mapping with conditional hasProperty-query eligibility; any uniform bearer_of alternative must explain the process-profile branch.

**Proposed recommendation:** Retain the artifact during review. Finalize no_direct_mapping with conditional hasProperty-query eligibility; any uniform bearer_of alternative must explain the process-profile branch.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!38`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!39`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/hasOperatingRange`; `imports/cco.ttl`; `reports/ssn-systems-property-split-mapping-review.md`; `reports/ssn-hasproperty-rule-mapping-artifact.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:hasSurvivalRange

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!41` / `urn:uuid:82ce9316-b7a7-4655-9c98-e16c314a0244`: `rdfs:domain` ssn:System.

- `Sheet2!42` / `urn:uuid:bd5a2014-f338-49b8-b7ef-27f5b933d93b`: `rdfs:range` ssn-system:SurvivalRange.

**Source semantics:** Relation from a System to a SurvivalRange.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:hasProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000117` (has occurrent part; historical_or_review_candidate_only; glossary); `bfo:BFO_0000196` (bearer of; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted ssn-system:hasSurvivalRange(x,y) types x as ssn:System; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted ssn-system:hasSurvivalRange(x,y) types y as ssn-system:SurvivalRange; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf (inverse(ssn-system:hasSurvivalRange) owl:allValuesFrom ssn:System)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn-system:hasSurvivalRange owl:allValuesFrom ssn-system:SurvivalRange)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `ssn-system:hasSurvivalRange rdfs:range ssn-system:SurvivalRange`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `ssn-system:hasSurvivalRange rdfs:domain ssn:System` (RowID `urn:uuid:82ce9316-b7a7-4655-9c98-e16c314a0244`).
- `source_native`: `ssn:System rdfs:subClassOf (ssn-system:hasSurvivalRange owl:allValuesFrom ssn-system:SurvivalRange)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Human decision:** Is a uniform System-to-SurvivalRange bearer relation justified by the current Function realization mapping, or is domain/range plus a conditional route the intended final state?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain no-direct typing pending SurvivalRange category review, or justify a category-specific relation after that review.

**Proposed recommendation:** Retain the artifact during review. Retain no-direct typing pending SurvivalRange category review, or justify a category-specific relation after that review.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!41`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!42`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/hasSurvivalRange`; `imports/cco.ttl`; `reports/ssn-systems-property-split-mapping-review.md`; `reports/ssn-hasproperty-rule-mapping-artifact.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:hasSystemCapability

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!43` / `urn:uuid:5f25dce9-54a0-442e-a9de-f18cd21aab1d`: `rdfs:domain` ssn:System.

- `Sheet2!44` / `urn:uuid:1e9432ec-0bfb-4c05-8a16-c4295d545f81`: `rdfs:range` ssn-system:SystemCapability.

**Source semantics:** Relation from a System to a SystemCapability describing the capabilities of the System under certain Conditions.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:hasProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000117` (has occurrent part; historical_or_review_candidate_only; glossary); `bfo:BFO_0000196` (bearer of; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted ssn-system:hasSystemCapability(x,y) types x as ssn:System; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted ssn-system:hasSystemCapability(x,y) types y as ssn-system:SystemCapability; no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:ActuationRange rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Actuator))`.
- `source_native` / asserted: `ssn-system:DetectionLimit rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor))`.
- `source_native` / asserted: `ssn-system:MeasurementRange rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor))`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom ssn:System)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn-system:hasSystemCapability owl:allValuesFrom ssn-system:SystemCapability)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `ssn-system:hasSystemCapability rdfs:range ssn-system:SystemCapability`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `ssn-system:hasSystemCapability rdfs:domain ssn:System` (RowID `urn:uuid:5f25dce9-54a0-442e-a9de-f18cd21aab1d`).
- `source_native`: `ssn:System rdfs:subClassOf (ssn-system:hasSystemCapability owl:allValuesFrom ssn-system:SystemCapability)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Human decision:** Does every SystemCapability qualify for a uniform bearer relation despite its continuant-or-ProcessProfile union, or must the conditional query remain separate?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Finalize no_direct_mapping with explicit query conditions, or review the capability category before any stronger target property.

**Proposed recommendation:** Retain the artifact during review. Finalize no_direct_mapping with explicit query conditions, or review the capability category before any stronger target property.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!43`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!44`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/hasSystemCapability`; `imports/cco.ttl`; `reports/ssn-systems-property-split-mapping-review.md`; `reports/ssn-hasproperty-rule-mapping-artifact.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:inCondition

State: **unreviewed**; priority 2; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!13` / `urn:uuid:79e12baa-9467-4494-bdf3-b6906f5a81a7`: `rdfs:domain` (ssn-system:SystemCapability or ssn-system:OperatingRange or ssn-system:SurvivalRange).

**Source semantics:** Describes the prevailing environmental conditions for SystemCapabilites, OperatingRanges and SurvivalRanges.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** No target relation or class expression is asserted by these rows. Native source types alone do not establish a BFO/CCO relation mapping.

**Logical consequences:** An asserted ssn-system:inCondition(x,y) types x as (ssn-system:SystemCapability or ssn-system:OperatingRange or ssn-system:SurvivalRange); no BFO/CCO relation edge is entailed by this typing axiom alone.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf (ssn-system:inCondition owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf (ssn-system:inCondition owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf (ssn-system:inCondition owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `ssn-system:inCondition rdfs:range ssn-system:Condition`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `ssn-system:inCondition rdfs:domain (ssn-system:SystemCapability or ssn-system:OperatingRange or ssn-system:SurvivalRange)` (RowID `urn:uuid:79e12baa-9467-4494-bdf3-b6906f5a81a7`).
- `source_native`: `ssn-system:OperatingRange rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native`: `ssn-system:SurvivalRange rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native`: `ssn-system:SystemCapability rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.

**Review clarification:** The current workbook has no explicit rdfs:range row for ssn-system:inCondition. The source also has no explicit rdfs:range assertion. The source universal restrictions together with the current mapping's domain row already entail a range constraint; this is an aligned consequence, not a source-only range assertion. An absent explicit row is therefore not evidence of unconstrained objects. Read the retained review question with this distinction; no mapping decision is made.

**Human decision:** Is a domain-only row an intentional final outcome for the relation to environmental Conditions, and is the omitted range intentional?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Record no_direct_mapping with the existing domain-only assertion, or propose a justified target relation separately; a new range would itself require approval.

**Proposed recommendation:** Retain the artifact during review. Record no_direct_mapping with the existing domain-only assertion, or propose a justified target relation separately; a new range would itself require approval.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!13`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/inCondition`; `imports/cco.ttl`; `reports/all-source-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## sosa:Actuation

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!5` / `urn:uuid:2a4f78b4-92cb-4095-9a6b-2ae03e00be4a`: `owl:equivalentClass` cco:PlannedAct and (sosa:actsOnProperty some sosa:ActuatableProperty).

**Source semantics:** An Actuation carries out an (Actuation) Procedure to change the state of the world using an Actuator.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:actsOnProperty owl:allValuesFrom sosa:ActuatableProperty); rdfs:subClassOf (sosa:actsOnProperty owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest); rdfs:subClassOf (sosa:hasFeatureOfInterest owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:hasResult owl:allValuesFrom sosa:Result); rdfs:subClassOf (sosa:hasResult owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:madeByActuator owl:allValuesFrom sosa:Actuator); rdfs:subClassOf (sosa:madeByActuator owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:resultTime owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:usedProcedure owl:allValuesFrom sosa:Procedure)

Source advisory signature: none recorded

**Target semantics:** `cco:ont00000228` (Planned Act; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Actuation satisfies cco:PlannedAct and (sosa:actsOnProperty some sosa:ActuatableProperty); every instance satisfying that full expression is also sosa:Actuation. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:ActuatableProperty rdfs:subClassOf (sosa:isActedOnBy owl:allValuesFrom sosa:Actuation)`.
- `source_native` / asserted: `sosa:Actuator rdfs:subClassOf (sosa:madeActuation owl:allValuesFrom sosa:Actuation)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!3`: `sosa:Actuation` — `active`, `owl:equivalentClass` cco:PlannedAct and (sosa:actsOnProperty some sosa:Property).  Comparison basis: same lexical term.

**Human decision:** Does every PlannedAct affecting an ActuatableProperty qualify as a SOSA Actuation, or are those only necessary conditions?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Weaken equivalence to subclass with the same target expression if the reverse implication lacks evidence.

**Proposed recommendation:** Retain the artifact during review. Weaken equivalence to subclass with the same target expression if the reverse implication lacks evidence.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!5`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Actuation`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Actuation`; `imports/cco.ttl`; `reports/actuation-range-mapping-correction-evaluation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Result

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!10` / `urn:uuid:b05ab84c-eeff-45d1-a95d-39cf2d9f084f`: `owl:equivalentClass` (cco:InformationContentEntity or bfo:MaterialEntity) and (cco:is_output_of some (sosa:Observation or sosa:Actuation or sosa:Sampling)).

**Source semantics:** The Result of an Observation, Actuation, or act of Sampling. To store an observation's simple result value one can use the hasSimpleResult property.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:isResultOf owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000040` (material entity; asserted_target_expression; glossary); `cco:ont00000958` (Information Content Entity; asserted_target_expression; glossary); `cco:ont00001816` (is output of; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Result satisfies (cco:InformationContentEntity or bfo:MaterialEntity) and (cco:is_output_of some (sosa:Observation or sosa:Actuation or sosa:Sampling)); every instance satisfying that full expression is also sosa:Result. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:hasResult owl:allValuesFrom sosa:Result)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:hasResult owl:allValuesFrom sosa:Result)`.
- `source_native` / asserted: `sosa:Sample rdfs:subClassOf sosa:Result`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!38`: `sosa:Result` — `no_direct_mapping`, `` . No direct BFO/CCO class mapping is adopted. sosa:Result is deprecated in the SOSA 2023 Edition, and its broad outcome semantics do not justify a new cross-ontology class commitment. Result interoperability is handled through the governed result relations. Comparison basis: same lexical term.

**Human decision:** Does every result have to be information content or a material entity, and does every such output of the listed executions qualify as a SOSA Result?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Weaken equivalence to subclass or a broader Continuant interpretation if abstract results exceed the selected union.

**Proposed recommendation:** Retain the artifact during review. Weaken equivalence to subclass or a broader Continuant interpretation if abstract results exceed the selected union.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!10`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Result`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Result`; `imports/cco.ttl`; `reports/isResultOf-hasResult-full-closure-analysis.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Sample

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!11` / `urn:uuid:326ad20d-f954-44e0-b94f-dccf0fd76ebb`: `owl:equivalentClass` bfo:MaterialEntity and (cco:is_object_of some sosa:Sampling).

**Source semantics:** Feature which is intended to be representative of a FeatureOfInterest on which Observations may be made.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:isResultOf owl:allValuesFrom sosa:Sampling); rdfs:subClassOf (sosa:isResultOf owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:isSampleOf owl:allValuesFrom sosa:FeatureOfInterest); rdfs:subClassOf (sosa:isSampleOf owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf sosa:FeatureOfInterest; rdfs:subClassOf sosa:Result

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000040` (material entity; asserted_target_expression; glossary); `cco:ont00001936` (is object of; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Sample satisfies bfo:MaterialEntity and (cco:is_object_of some sosa:Sampling); every instance satisfying that full expression is also sosa:Sample. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:FeatureOfInterest rdfs:subClassOf (sosa:hasSample owl:allValuesFrom sosa:Sample)`.
- `source_native` / asserted: `sosa:Sampling rdfs:subClassOf (sosa:hasResult owl:allValuesFrom sosa:Sample)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!17`: `sosa:Sample` — `active`, `rdfs:subClassOf` bfo:Continuant and (sosa:isSampleOf some sosa:FeatureOfInterest).  Comparison basis: same lexical term.

**Human decision:** Must all current SOSA Samples be material and objects of Sampling, and are those conditions sufficient for samplehood, including statistical samples in source examples?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Consider a Continuant subclass and source isSampleOf relation, distinguishing a sampled object from an output; any change requires current-source review.

**Proposed recommendation:** Retain the artifact during review. Consider a Continuant subclass and source isSampleOf relation, distinguishing a sampled object from an output; any change requires current-source review.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!11`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Sample`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Sample`; `imports/cco.ttl`; `reports/sample-representation-property-chains-review.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Sampler

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!40` / `urn:uuid:98b1044d-6bfe-41d2-89aa-cdc87e524e4c`: `owl:equivalentClass` bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Sampling))) and (cco:agent_in some sosa:Sampling).

**Source semantics:** A device that is used by, or implements, a Sampling Procedure to create or transform one or more samples.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:madeSampling owl:allValuesFrom sosa:Sampling); rdfs:subClassOf (ssn:implements owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:System

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000017` (realizable entity; asserted_target_expression; glossary); `bfo:BFO_0000040` (material entity; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000196` (bearer of; asserted_target_expression; glossary); `cco:ont00001787` (agent in; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Sampler satisfies bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Sampling))) and (cco:agent_in some sosa:Sampling); every instance satisfying that full expression is also sosa:Sampler. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Sampling rdfs:subClassOf (sosa:madeBySampler owl:allValuesFrom sosa:Sampler)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!19`: `sosa:Sampler` — `active`, `rdfs:subClassOf` bfo:MaterialEntity. Replace the current equivalent-class mapping with sosa:Sampler rdfs:subClassOf bfo:MaterialEntity. Remove the reverse implication and the bearer_of, has_realization, and agent_in existential restrictions. This preserves the project's deliberate materiality commitment without requiring an actual Sampling. Comparison basis: same lexical term.

**Human decision:** Should the earlier explicit necessary-and-sufficient Sampler decision remain final given unused samplers and the pinned track’s removal of actual Sampling existentials?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain the historical equivalence only with a renewed current-source defense; otherwise propose MaterialEntity subclass or a genuinely dispositional reading.

**Proposed recommendation:** Retain the artifact during review. Retain the historical equivalence only with a renewed current-source defense; otherwise propose MaterialEntity subclass or a genuinely dispositional reading.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!40`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Sampler`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Sampler`; `imports/cco.ttl`; `reports/sampler-equivalentclass-decision.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Sampling

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!12` / `urn:uuid:7b3f908b-b717-4336-9968-8b1083f847d3`: `owl:equivalentClass` cco:PlannedAct and (cco:prescribed_by some sosa:Procedure) and (cco:has_output some sosa:Sample).

**Source semantics:** An act of Sampling carries out a sampling Procedure to create or transform one or more samples.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest); rdfs:subClassOf (sosa:hasFeatureOfInterest owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:hasResult owl:allValuesFrom sosa:Sample); rdfs:subClassOf (sosa:hasResult owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:madeBySampler owl:allValuesFrom sosa:Sampler); rdfs:subClassOf (sosa:madeBySampler owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:resultTime owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (sosa:usedProcedure owl:allValuesFrom sosa:Procedure)

Source advisory signature: none recorded

**Target semantics:** `cco:ont00000228` (Planned Act; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary); `cco:ont00001986` (has output; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Sampling satisfies cco:PlannedAct and (cco:prescribed_by some sosa:Procedure) and (cco:has_output some sosa:Sample); every instance satisfying that full expression is also sosa:Sampling. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Sample rdfs:subClassOf (sosa:isResultOf owl:allValuesFrom sosa:Sampling)`.
- `source_native` / asserted: `sosa:Sampler rdfs:subClassOf (sosa:madeSampling owl:allValuesFrom sosa:Sampling)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Are a PlannedAct, an actual prescribed Procedure, and an output Sample jointly sufficient for Sampling rather than merely necessary?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Weaken to a one-way subclass if non-sampling acts can satisfy the target conditions; retain equivalence only with a reverse-direction argument.

**Proposed recommendation:** Retain the artifact during review. Weaken to a one-way subclass if non-sampling acts can satisfy the target conditions; retain equivalence only with a reverse-direction argument.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!12`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Sampling`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Sampling`; `imports/cco.ttl`; `reports/sosa-next-crosswalk-reconciliation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn:Property

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!34` / `urn:uuid:b1421726-3675-4b2a-9824-150e108157e4`: `owl:equivalentClass` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile).

**Source semantics:** A quality of an entity. An aspect of an entity that is intrinsic to and cannot exist without the entity.

Source structure: rdf:type owl:Class; rdfs:subClassOf (ssn:isPropertyOf owl:allValuesFrom sosa:FeatureOfInterest)

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:Property satisfies (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile); every instance satisfying that full expression is also ssn:Property. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:ActuatableProperty rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `sosa:FeatureOfInterest rdfs:subClassOf (ssn:hasProperty owl:allValuesFrom ssn:Property)`.
- `source_native` / asserted: `sosa:ObservableProperty rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:Condition rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:OperatingProperty rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:SurvivalProperty rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf (ssn:forProperty owl:allValuesFrom ssn:Property)`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn-system:SystemProperty rdfs:subClassOf ssn:Property`.
- `source_native` / asserted: `ssn:Deployment rdfs:subClassOf (ssn:forProperty owl:allValuesFrom ssn:Property)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!16`: `sosa:Property` — `active`, `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile). Weaken the current equivalence to sosa:Property rdfs:subClassOf (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile). The two-branch union remains the project's necessary upper bound for continuant and occurrent properties, but the reverse implications are unsupported: not every specifically dependent continuant or process profile is a SOSA Property. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Is every BFO specifically dependent continuant and every ProcessProfile necessarily an SSN Property, as the equivalence asserts?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Weaken equivalence to the same union as a necessary upper bound if the reverse direction is unsupported.

**Proposed recommendation:** Retain the artifact during review. Weaken equivalence to the same union as a necessary upper bound if the reverse direction is unsupported.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!34`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/Property`; `imports/cco.ttl`; `reports/ssn-hasproperty-modeling-options.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn:Stimulus

State: **unreviewed**; priority 3; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!35` / `urn:uuid:23915904-0174-4f2f-b6cf-6a8671b92d7e`: `owl:equivalentClass` cco:Cause and (cco:is_cause_of some sosa:Observation).

**Source semantics:** An event in the real world that 'triggers' the Sensor. The properties associated to the Stimulus may be different to the eventual observed ObservableProperty. It is the event, not the object, that triggers the Sensor.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn:detects) owl:allValuesFrom sosa:Sensor); rdfs:subClassOf (inverse(ssn:wasOriginatedBy) owl:allValuesFrom sosa:Observation); rdfs:subClassOf (ssn:isProxyFor owl:allValuesFrom sosa:ObservableProperty)

Source advisory signature: none recorded

**Target semantics:** `cco:ont00000978` (Cause; asserted_target_expression; glossary); `cco:ont00001803` (is cause of; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:Stimulus satisfies cco:Cause and (cco:is_cause_of some sosa:Observation); every instance satisfying that full expression is also ssn:Stimulus. Existential fillers denote actual individuals, including anonymous witnesses.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:ObservableProperty rdfs:subClassOf (inverse(ssn:isProxyFor) owl:allValuesFrom ssn:Stimulus)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (ssn:wasOriginatedBy owl:allValuesFrom ssn:Stimulus)`.
- `source_native` / asserted: `sosa:Sensor rdfs:subClassOf (ssn:detects owl:allValuesFrom ssn:Stimulus)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!26`: `sosa:Stimulus` — `active`, `rdfs:subClassOf` cco:Cause and (cco:is_cause_of some sosa:Observation). Replace the equivalent-class axiom with a one-way subclass axiom. Every SOSA Stimulus may be modeled as a CCO Cause that is cause of some Observation, but not every cause of an Observation is thereby a SOSA Stimulus. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Is every cause of an Observation a detectable change that qualifies as a source Stimulus, or only some causes?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Weaken equivalence to subclass with the same Cause/existential expression if the reverse implication overclassifies unrelated causes.

**Proposed recommendation:** Retain the artifact during review. Weaken equivalence to subclass with the same Cause/existential expression if the reverse implication overclassifies unrelated causes.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!35`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/Stimulus`; `imports/cco.ttl`; `reports/hermit-observation-sensor-stimulus-evaluation.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:ActuatableProperty

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!4` / `urn:uuid:1b7c27d4-1b0e-461f-8a77-7a81631ab342`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant and bfo:inheres_in some sosa:FeatureOfInterest) or (bfo:ProcessProfile and bfo:occurrent_part_of some sosa:FeatureOfInterest).

**Source semantics:** An actuatable quality (property, characteristic) of a FeatureOfInterest.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:isActedOnBy owl:allValuesFrom sosa:Actuation); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000132` (occurrent part of; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `bfo:BFO_0000197` (inheres in; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:ActuatableProperty satisfies (bfo:SpecificallyDependentContinuant and bfo:inheres_in some sosa:FeatureOfInterest) or (bfo:ProcessProfile and bfo:occurrent_part_of some sosa:FeatureOfInterest); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:actsOnProperty owl:allValuesFrom sosa:ActuatableProperty)`.
- `source_native` / asserted: `sosa:Actuator rdfs:subClassOf (ssn:forProperty owl:allValuesFrom sosa:ActuatableProperty)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!35`: `sosa:ActuatableProperty` — `no_direct_mapping`, `` . No additional direct BFO/CCO mapping is adopted. The pinned source already declares sosa:ActuatableProperty rdfs:subClassOf sosa:Property, so this class inherits the governed cross-ontology upper bound for sosa:Property without requiring a more specific BFO commitment. Comparison basis: same lexical term.

**Human decision:** Does every actuatable property actually inhere in or form an occurrent part of a FeatureOfInterest, and do the two BFO branches exhaust its source meaning?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain a necessary upper union without the existential fillers, or rely on the reviewed ssn:Property superclass if sufficient.

**Proposed recommendation:** Retain the artifact during review. Retain a necessary upper union without the existential fillers, or rely on the reviewed ssn:Property superclass if sufficient.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!4`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/ActuatableProperty`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/ActuatableProperty`; `imports/cco.ttl`; `reports/hermit-survival-property-source-restriction-explanation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Actuator

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!37` / `urn:uuid:ee7f2f05-bc8e-4477-bb58-0f40e6da81d0`: `rdfs:subClassOf` bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Actuation))) and (cco:agent_in some sosa:Actuation).

**Source semantics:** A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:madeActuation owl:allValuesFrom sosa:Actuation); rdfs:subClassOf (ssn:forProperty owl:allValuesFrom sosa:ActuatableProperty); rdfs:subClassOf (ssn:implements owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:System

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000017` (realizable entity; asserted_target_expression; glossary); `bfo:BFO_0000040` (material entity; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000196` (bearer of; asserted_target_expression; glossary); `cco:ont00001787` (agent in; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Actuator satisfies bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Actuation))) and (cco:agent_in some sosa:Actuation); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:madeByActuator owl:allValuesFrom sosa:Actuator)`.
- `source_native` / asserted: `ssn-system:ActuationRange rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Actuator))`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!5`: `sosa:Actuator` — `active`, `rdfs:subClassOf` bfo:MaterialEntity. Replace the current composite subclass mapping with sosa:Actuator rdfs:subClassOf bfo:MaterialEntity. Remove the bearer_of, has_realization, and agent_in existential restrictions. This preserves the project's deliberate materiality commitment without requiring an actual Actuation. Comparison basis: same lexical term.

**Human decision:** Can an unused Actuator exist without an actual Actuation, despite the current realization and agent_in existential commitments?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain MaterialEntity alone if the source supports potential action rather than actual action; preserve the current restrictions only with explicit acceptance of actual witnesses.

**Proposed recommendation:** Retain the artifact during review. Retain MaterialEntity alone if the source supports potential action rather than actual action; preserve the current restrictions only with explicit acceptance of actual witnesses.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!37`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Actuator`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Actuator`; `imports/cco.ttl`; `reports/madeByActuator-agent-mapping-adjustment-evaluation.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:FeatureOfInterest

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!6` / `urn:uuid:06782965-88c5-4345-ab99-ea027513ec86`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile or bfo:MaterialEntity or bfo:Process).

**Source semantics:** The thing whose property is being estimated or calculated in the course of an Observation to arrive at a Result or whose property is being manipulated by an Actuator, or which is being sampled or transformed in an act of Sampling.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:hasSample owl:allValuesFrom sosa:Sample); rdfs:subClassOf (ssn:hasProperty owl:allValuesFrom ssn:Property); rdfs:subClassOf (ssn:hasProperty owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000040` (material entity; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:FeatureOfInterest satisfies (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile or bfo:MaterialEntity or bfo:Process); the reverse classification is not asserted.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `sosa:Sample rdfs:subClassOf (sosa:isSampleOf owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `sosa:Sample rdfs:subClassOf sosa:FeatureOfInterest`.
- `source_native` / asserted: `sosa:Sampling rdfs:subClassOf (sosa:hasFeatureOfInterest owl:allValuesFrom sosa:FeatureOfInterest)`.
- `source_native` / asserted: `ssn:Property rdfs:subClassOf (ssn:isPropertyOf owl:allValuesFrom sosa:FeatureOfInterest)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!9`: `sosa:FeatureOfInterest` — `active`, `owl:equivalentClass` bfo:Entity and (sosa:isFeatureOfInterestOf some (sosa:Execution or sosa:ExecutionCollection or sosa:Deployment)). Widen the current equivalent-class filler from Observation-or-Sampling-or-Actuation to Execution-or-ExecutionCollection-or-Deployment. This matches the exact pinned isFeatureOfInterestOf signature: the narrower execution classes are already subclasses of Execution, and their collection classes are subclasses of ExecutionCollection. Comparison basis: same lexical term.

**Human decision:** Is the four-category union a deliberate necessary upper bound for every FeatureOfInterest, including abstract or informational features, and does the wording “direct alignment deferred” accurately describe an active axiom?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain and document the broad union if accepted, or propose a weaker BFO Entity bound; do not narrow it to material/process only.

**Proposed recommendation:** Retain the artifact during review. Retain and document the broad union if accepted, or propose a weaker BFO Entity bound; do not narrow it to material/process only.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!6`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/FeatureOfInterest`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/FeatureOfInterest`; `imports/cco.ttl`; `reports/hermit-survival-property-source-restriction-explanation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:ObservableProperty

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!7` / `urn:uuid:99b22791-b2d1-4667-901e-861a44f2b8a2`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant and bfo:inheres_in some sosa:FeatureOfInterest) or (bfo:ProcessProfile and bfo:occurrent_part_of some sosa:FeatureOfInterest).

**Source semantics:** An observable quality (property, characteristic) of a FeatureOfInterest.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(sosa:observedProperty) owl:allValuesFrom sosa:Observation); rdfs:subClassOf (inverse(ssn:isProxyFor) owl:allValuesFrom ssn:Stimulus); rdfs:subClassOf (sosa:isObservedBy owl:allValuesFrom sosa:Sensor); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000132` (occurrent part of; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `bfo:BFO_0000197` (inheres in; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:ObservableProperty satisfies (bfo:SpecificallyDependentContinuant and bfo:inheres_in some sosa:FeatureOfInterest) or (bfo:ProcessProfile and bfo:occurrent_part_of some sosa:FeatureOfInterest); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:observedProperty owl:allValuesFrom sosa:ObservableProperty)`.
- `source_native` / asserted: `sosa:Sensor rdfs:subClassOf (sosa:observes owl:allValuesFrom sosa:ObservableProperty)`.
- `source_native` / asserted: `ssn:Stimulus rdfs:subClassOf (ssn:isProxyFor owl:allValuesFrom sosa:ObservableProperty)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!37`: `sosa:ObservableProperty` — `no_direct_mapping`, `` . No additional direct BFO/CCO mapping is adopted. The pinned source already declares sosa:ObservableProperty rdfs:subClassOf sosa:Property, so this class inherits the governed cross-ontology upper bound for sosa:Property without requiring a more specific BFO commitment. Comparison basis: same lexical term.

**Human decision:** Does every observable property require an actual bearer/process FeatureOfInterest through exactly these two relations, rather than just being a quality that can be observed?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Use only the necessary upper union or inherited ssn:Property alignment if justified; retain actual bearer/part existentials only with source-specific evidence.

**Proposed recommendation:** Retain the artifact during review. Use only the necessary upper union or inherited ssn:Property alignment if justified; retain actual bearer/part existentials only with source-specific evidence.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!7`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/ObservableProperty`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/ObservableProperty`; `imports/cco.ttl`; `reports/hermit-observation-sensor-stimulus-evaluation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Procedure

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!39` / `urn:uuid:d88535da-ab7c-409c-b928-a9b0760b4607`: `rdfs:subClassOf` cco:DirectiveInformationContentEntity and (cco:prescribes some bfo:Process).

**Source semantics:** A workflow, protocol, plan, algorithm, or computational method specifying how to make an Observation, create a Sample, or make a change to the state of the world (via an Actuator). A Procedure is re-usable, and might be involved in many Observations, Samplings, or Actuations. It explains the steps to be carried out to arrive at reproducible results.

Source structure: rdf:type owl:Class; rdfs:subClassOf (ssn:hasInput owl:allValuesFrom ssn:Input); rdfs:subClassOf (ssn:hasOutput owl:allValuesFrom ssn:Output); rdfs:subClassOf (ssn:implementedBy owl:allValuesFrom ssn:System)

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `cco:ont00000965` (Directive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001942` (prescribes; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Procedure satisfies cco:DirectiveInformationContentEntity and (cco:prescribes some bfo:Process); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Actuation rdfs:subClassOf (sosa:usedProcedure owl:allValuesFrom sosa:Procedure)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:usedProcedure owl:allValuesFrom sosa:Procedure)`.
- `source_native` / asserted: `sosa:Sampling rdfs:subClassOf (sosa:usedProcedure owl:allValuesFrom sosa:Procedure)`.
- `source_native` / asserted: `ssn:Input rdfs:subClassOf (inverse(ssn:hasInput) owl:allValuesFrom sosa:Procedure)`.
- `source_native` / asserted: `ssn:Output rdfs:subClassOf (inverse(ssn:hasOutput) owl:allValuesFrom sosa:Procedure)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn:implements owl:allValuesFrom sosa:Procedure)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!15`: `sosa:Procedure` — `active`, `rdfs:subClassOf` cco:ont00000965. Map sosa:Procedure to the stable CCO class IRI cco:ont00000965. In the explicitly selected CCO target snapshot at upstream commit 010c99847a856e2fb70eb1b1b1287d19556c9290, this class is labelled Prescriptive Information Content Entity; the repository-wide current CCO dependency labels the same stable IRI Directive Information Content Entity. Using the canonical ont00000965 token avoids label-dependent resolution. Retain only the subclass mapping and no additional cco:prescribes some bfo:Process restriction because a reusable SOSA Procedure does not require an actually prescribed Process. Comparison basis: same lexical term.

**Human decision:** Does every reusable Procedure prescribe an actual Process, or does the source support only its information-content category?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Use the existing CCO DirectiveInformationContentEntity category without the extra Process-specific existential if that is the supported necessary commitment.

**Proposed recommendation:** Retain the artifact during review. Use the existing CCO DirectiveInformationContentEntity category without the extra Process-specific existential if that is the supported necessary commitment.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!39`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Procedure`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Procedure`; `imports/cco.ttl`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:Sensor

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!38` / `urn:uuid:2902e2b3-44f8-4f81-8ca9-2def4b68befd`: `rdfs:subClassOf` bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Observation))) and (cco:agent_in some sosa:Observation).

**Source semantics:** Device, agent (including humans), or software (simulation) involved in, or implementing, a Procedure. Sensors respond to a stimulus, e.g., a change in the environment, or input data composed from the results of prior Observations, and generate a Result. Sensors can be hosted by Platforms.

Source structure: rdf:type owl:Class; rdfs:subClassOf (sosa:madeObservation owl:allValuesFrom sosa:Observation); rdfs:subClassOf (sosa:observes owl:allValuesFrom sosa:ObservableProperty); rdfs:subClassOf (ssn:detects owl:allValuesFrom ssn:Stimulus); rdfs:subClassOf (ssn:implements owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:System

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000017` (realizable entity; asserted_target_expression; glossary); `bfo:BFO_0000040` (material entity; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000196` (bearer of; asserted_target_expression; glossary); `cco:ont00001787` (agent in; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:Sensor satisfies bfo:MaterialEntity and (bfo:bearer_of some (bfo:RealizableEntity and (bfo:has_realization some sosa:Observation))) and (cco:agent_in some sosa:Observation); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:ObservableProperty rdfs:subClassOf (sosa:isObservedBy owl:allValuesFrom sosa:Sensor)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:madeBySensor owl:allValuesFrom sosa:Sensor)`.
- `source_native` / asserted: `ssn-system:DetectionLimit rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor))`.
- `source_native` / asserted: `ssn-system:MeasurementRange rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor))`.
- `source_native` / asserted: `ssn:Stimulus rdfs:subClassOf (inverse(ssn:detects) owl:allValuesFrom sosa:Sensor)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet1!23`: `sosa:Sensor` — `active`, `owl:equivalentClass` cco:Sensor. Adopt the expert-crosswalk equivalence sosa:Sensor owl:equivalentClass cco:Sensor against the explicitly selected CCO development snapshot at upstream commit 010c99847a856e2fb70eb1b1b1287d19556c9290. In that snapshot cco:Sensor is equivalently characterized using a Material Entity bearing a Sensor Function or Sensor Role, matching the dispositional Sensor interpretation selected for this SOSA-2023 mapping track. The dependency is pinned by exact commit and SHA-256 and is not the repository-wide current SSN/SOSA CCO dependency. Comparison basis: same lexical term.

**Human decision:** Does the current Sensor interpretation require actual Observation and agency, or should an unused capable sensor qualify without actual realization?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review MaterialEntity-only/dispositional placement against the current CCO bytes; the N-track Sensor equivalence uses a different CCO snapshot and is not interchangeable.

**Proposed recommendation:** Retain the artifact during review. Review MaterialEntity-only/dispositional placement against the current CCO bytes; the N-track Sensor equivalence uses a different CCO snapshot and is not interchangeable.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!38`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/Sensor`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/Sensor`; `imports/cco.ttl`; `reports/sosa-sensor-version-alignment-resolution.md`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn-system:Accuracy

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!13` / `urn:uuid:8897fadf-b70f-4d81-a08c-a072f873f82b`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:VeracityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** The closeness of agreement between the Result of an Observation (resp. the command of an Actuation) and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000592` (Veracity Measurement Information Content Entity; asserted_target_expression; glossary); `cco:ont00000853` (Descriptive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001801` (is subject of; asserted_target_expression; glossary); `cco:ont00001904` (is measured by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Accuracy satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:VeracityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does accuracy in comparison with a reference justify the current commitment to Function, an actual Process, descriptive content, and a VeracityMeasurementInformationContentEntity, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Accuracy restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Accuracy restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!13`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Accuracy`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:ActuationRange

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!41` / `urn:uuid:7caa02f4-26a1-4e81-b709-5c2116636f65`: `rdfs:subClassOf` bfo:Function and (bfo:has_realization some (sosa:Actuation and ((cco:has_output some bfo:SpecificallyDependentContinuant) and (cco:prescribed_by some cco:ArtifactFunctionSpecification)))).

**Source semantics:** The set of values that the Actuator can return as the Result of an Actuation under the defined Conditions with the defined system properties.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Actuator)); rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary); `cco:ont00001986` (has output; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:ActuationRange satisfies bfo:Function and (bfo:has_realization some (sosa:Actuation and ((cco:has_output some bfo:SpecificallyDependentContinuant) and (cco:prescribed_by some cco:ArtifactFunctionSpecification)))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does the range of actuation values justify the current commitment to Function and an actual Actuation producing a specifically dependent continuant under an ArtifactFunctionSpecification, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional ActuationRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional ActuationRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!41`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/ActuationRange`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:BatteryLifetime

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!42` / `urn:uuid:d8b4d0f0-d8d4-4f22-ae7c-2bbdebcdd51f`: `rdfs:subClassOf` bfo:Function and (bfo:has_realization some (cco:StasisOfArtifactOperationality and (bfo:has_occurrent_part some cco:Power) and (cco:caused_by some (bfo:Process and (bfo:realizes some (cco:Affordance and (cco:prescribed_by some cco:ArtifactDesign))))))).

**Source semantics:** Total useful life of a System's battery in the specified Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SurvivalProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000055` (realizes; asserted_target_expression; glossary); `bfo:BFO_0000117` (has occurrent part; asserted_target_expression; glossary); `cco:ont00000177` (Affordance; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00000503` (Power; asserted_target_expression; glossary); `cco:ont00001213` (Stasis of Artifact Operationality; asserted_target_expression; glossary); `cco:ont00001819` (caused by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:BatteryLifetime satisfies bfo:Function and (bfo:has_realization some (cco:StasisOfArtifactOperationality and (bfo:has_occurrent_part some cco:Power) and (cco:caused_by some (bfo:Process and (bfo:realizes some (cco:Affordance and (cco:prescribed_by some cco:ArtifactDesign))))))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does total useful battery life justify the current commitment to Function, an actual operational stasis containing Power, and a causal process realizing a design-prescribed Affordance, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional BatteryLifetime restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional BatteryLifetime restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!42`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/BatteryLifetime`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Condition

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!14` / `urn:uuid:b15038bf-7e69-4e62-9cdd-50edb029d88b`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and (cco:condition_described_by some cco:PerformanceSpecification).

**Source semantics:** Used to specify ranges for qualities that act as conditions on a system/sensor's operation.  For example, wind speed of 10-60m/s may be used as the condition on a SystemProperty, for example, to state that a sensor has a particular accuracy in that condition.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `cco:ont00000127` (Performance Specification; asserted_target_expression; glossary); `cco:ont00001884` (condition described by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Condition satisfies (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and (cco:condition_described_by some cco:PerformanceSpecification); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition)`.

**Relevant property chains (ordered path → superproperty):**
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does environmental conditions affecting performance justify the current commitment to SDC-or-ProcessProfile plus an actual PerformanceSpecification, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Condition restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Condition restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!14`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Condition`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:DetectionLimit

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!15` / `urn:uuid:86e97aa4-dc26-4d62-bef6-52cf36869bc8`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:VeracityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** An observed value for which the probability of falsely claiming the absence of a component in a material is beta, given a probability alpha of falsely claiming its presence.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor)); rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000592` (Veracity Measurement Information Content Entity; asserted_target_expression; glossary); `cco:ont00000853` (Descriptive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001801` (is subject of; asserted_target_expression; glossary); `cco:ont00001904` (is measured by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:DetectionLimit satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:VeracityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does the smallest detectable change justify the current commitment to Function and a VeracityMeasurementInformationContentEntity, using the same pattern as Accuracy, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional DetectionLimit restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional DetectionLimit restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!15`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/DetectionLimit`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Drift

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!16` / `urn:uuid:823bbbdf-b4f1-4e45-8b0a-5597306e6b69`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:DeviationMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** As a Sensor Property: a continuous or incremental change in the reported values of Observations over time for an unchanging Property under the defined Conditions.

      As an Actuator Property: a continuous or incremental change in the true value of the acted on ActuatableProperty over time for an unchanging command under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000731` (Deviation Measurement Information Content Entity; asserted_target_expression; glossary); `cco:ont00000853` (Descriptive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001801` (is subject of; asserted_target_expression; glossary); `cco:ont00001904` (is measured by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Drift satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:DeviationMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does change in response over time justify the current commitment to Function and a DeviationMeasurementInformationContentEntity through an actual realization/description, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Drift restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Drift restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!16`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Drift`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Frequency

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!17` / `urn:uuid:124e6b06-906a-47be-a459-92babef3992e`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (cco:PlannedAct and bfo:has_occurrent_part some (cco:Frequency and cco:prescribed_by some cco:ArtifactFunctionSpecification)).

**Source semantics:** The smallest possible time between one Observation, Actuation, or Sampling and the next, under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000117` (has occurrent part; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000228` (Planned Act; asserted_target_expression; glossary); `cco:ont00001047` (Frequency; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Frequency satisfies bfo:Function and bfo:has_realization some (cco:PlannedAct and bfo:has_occurrent_part some (cco:Frequency and cco:prescribed_by some cco:ArtifactFunctionSpecification)); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does the smallest time between consecutive observations justify the current commitment to Function with an actual PlannedAct having a Frequency process part prescribed by a function specification, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Frequency restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Frequency restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!17`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Frequency`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Latency

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!18` / `urn:uuid:1a25c5c5-795c-444c-ba3b-e0578f9e715b`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (cco:PlannedAct and (cco:has_process_part some cco:Cause) and (cco:has_process_part some cco:Effect) and (bfo:occupies_temporal_region some (bfo:TemporalRegion and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** The time between a command for an Observation (resp. Actuation) and the Sensor providing a Result (resp. the Actuator operating the Actuation), under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000008` (temporal region; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000199` (occupies temporal region; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000228` (Planned Act; asserted_target_expression; glossary); `cco:ont00000660` (Effect; asserted_target_expression; glossary); `cco:ont00000978` (Cause; asserted_target_expression; glossary); `cco:ont00001777` (has process part; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Latency satisfies bfo:Function and bfo:has_realization some (cco:PlannedAct and (cco:has_process_part some cco:Cause) and (cco:has_process_part some cco:Effect) and (bfo:occupies_temporal_region some (bfo:TemporalRegion and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does elapsed time before an observation result is available justify the current commitment to Function with an actual PlannedAct, both Cause and Effect process parts, and a prescribed occupied TemporalRegion, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Latency restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Latency restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!18`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Latency`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:MaintenanceSchedule

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!19` / `urn:uuid:afc3498b-5446-4c8b-928f-822a8e148b63`: `rdfs:subClassOf` bfo:Disposition and bfo:has_realization some (cco:Change and cco:affects some (bfo:SpecificallyDependentContinuant and bfo:participates_in some (cco:ActOfMaintenance and bfo:has_occurrent_part some (cco:Frequency and cco:prescribed_by some cco:ArtifactDesign)))).

**Source semantics:** Schedule of maintenance for a System in the specified Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:OperatingProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000016` (disposition; asserted_target_expression; glossary); `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000056` (participates in; asserted_target_expression; glossary); `bfo:BFO_0000117` (has occurrent part; asserted_target_expression; glossary); `cco:ont00000004` (Change; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00000950` (Act of Maintenance; asserted_target_expression; glossary); `cco:ont00001047` (Frequency; asserted_target_expression; glossary); `cco:ont00001834` (affects; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:MaintenanceSchedule satisfies bfo:Disposition and bfo:has_realization some (cco:Change and cco:affects some (bfo:SpecificallyDependentContinuant and bfo:participates_in some (cco:ActOfMaintenance and bfo:has_occurrent_part some (cco:Frequency and cco:prescribed_by some cco:ArtifactDesign)))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does maintenance needed to keep a system operating justify the current commitment to Disposition with an actual Change affecting a dependent continuant that participates in actual maintenance with a design-prescribed Frequency, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional MaintenanceSchedule restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional MaintenanceSchedule restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!19`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/MaintenanceSchedule`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:OperatingPowerRange

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!20` / `urn:uuid:335606ce-18b3-43d9-b13e-7301015c9d26`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and bfo:has_occurrent_part some (cco:Power and cco:prescribed_by some cco:ArtifactDesign)).

**Source semantics:** Power range in which a System is expected to operate in the specified Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:OperatingProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000117` (has occurrent part; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00000503` (Power; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:OperatingPowerRange satisfies bfo:Function and bfo:has_realization some (bfo:Process and bfo:has_occurrent_part some (cco:Power and cco:prescribed_by some cco:ArtifactDesign)); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does power conditions for operation justify the current commitment to Function with an actual Process whose Power part is prescribed by an ArtifactDesign, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional OperatingPowerRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional OperatingPowerRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!20`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/OperatingPowerRange`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:OperatingProperty

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!21` / `urn:uuid:206e2eaa-765b-491b-ad9c-73f144f048a1`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and cco:prescribed_by some cco:ArtifactDesign.

**Source semantics:** An identifiable characteristic that represents how the System operates under the specified Conditions. May describe power ranges, power sources, standard configurations, attachments and the like.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasOperatingProperty) owl:allValuesFrom ssn-system:OperatingRange); rdfs:subClassOf (inverse(ssn-system:hasOperatingProperty) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:OperatingProperty satisfies (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and cco:prescribed_by some cco:ArtifactDesign; the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:MaintenanceSchedule rdfs:subClassOf ssn-system:OperatingProperty`.
- `source_native` / asserted: `ssn-system:OperatingPowerRange rdfs:subClassOf ssn-system:OperatingProperty`.
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf (ssn-system:hasOperatingProperty owl:allValuesFrom ssn-system:OperatingProperty)`.

**Human decision:** Does an identifiable characteristic of normal operation justify the current commitment to SDC-or-ProcessProfile and actual prescription by an ArtifactDesign, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional OperatingProperty restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional OperatingProperty restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!21`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/OperatingProperty`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:OperatingRange

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!22` / `urn:uuid:dbdcee3f-bbdf-4a35-b92e-a14dd26e6239`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and cco:prescribed_by some cco:ArtifactDesign.

**Source semantics:** Describes normal OperatingProperties of a System under some specified Conditions. For example, to the power requirement or maintenance schedule of a System under a specified temperature range.

    In the absence of OperatingProperties, it simply describes the Conditions in which a System is expected to operate.

    The System continues to operate as defined using SystemCapability. If, however, the SurvivalRange is violated, the System is 'damaged' and SystemCapability specifications may no longer hold.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasOperatingRange) owl:allValuesFrom ssn:System); rdfs:subClassOf (ssn-system:hasOperatingProperty owl:allValuesFrom ssn-system:OperatingProperty); rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition); rdfs:subClassOf (ssn-system:inCondition owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:OperatingRange satisfies (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and cco:prescribed_by some cco:ArtifactDesign; the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:OperatingProperty rdfs:subClassOf (inverse(ssn-system:hasOperatingProperty) owl:allValuesFrom ssn-system:OperatingRange)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn-system:hasOperatingRange owl:allValuesFrom ssn-system:OperatingRange)`.

**Human decision:** Does conditions within which operation is expected justify the current commitment to SDC-or-ProcessProfile and actual prescription by an ArtifactDesign, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional OperatingRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional OperatingRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!22`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/OperatingRange`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Precision

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!23` / `urn:uuid:2befdb79-d016-45f8-8c35-69ee93fa731f`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:ReliabilityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** As a Sensor Property: the closeness of agreement between replicate Observations on an unchanged or similar Property value: i.e., a measure of a Sensor's ability to consistently reproduce an Observation, under the defined Conditions.

      As an Actuator Property: the closeness of agreement between replicate Actuations for an unchanged or similar command: i.e., a measure of an Actuator's ability to consistently reproduce an Actuation, under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000853` (Descriptive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001256` (Reliability Measurement Information Content Entity; asserted_target_expression; glossary); `cco:ont00001801` (is subject of; asserted_target_expression; glossary); `cco:ont00001904` (is measured by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Precision satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:ReliabilityMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does repeatability or consistency of observations justify the current commitment to Function and a ReliabilityMeasurementInformationContentEntity through actual realization and description, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Precision restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Precision restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!23`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Precision`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Resolution

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!24` / `urn:uuid:3ac135c9-bfd7-49cf-9c51-4d6e9ed56d87`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:DeviationMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** As a Sensor Property: the smallest difference in the value of a ObservableProperty being observed that would result in perceptably different values of Observation Results, under the defined Conditions.

      As an Actuator Property: the smallest difference in the value of an Actuation command that would result in a value change of the ActuatableProperty being acted on, under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000731` (Deviation Measurement Information Content Entity; asserted_target_expression; glossary); `cco:ont00000853` (Descriptive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001801` (is subject of; asserted_target_expression; glossary); `cco:ont00001904` (is measured by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Resolution satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:DeviationMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does the smallest distinguishable change justify the current commitment to Function and a DeviationMeasurementInformationContentEntity, using the same target pattern as Drift, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Resolution restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Resolution restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!24`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Resolution`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:ResponseTime

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!25` / `urn:uuid:b891bb2b-0093-49ff-aa86-2a68a732686d`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (cco:PlannedAct and (cco:has_process_part some cco:Cause) and (cco:has_process_part some cco:Effect) and (bfo:occupies_temporal_region some (bfo:TemporalRegion and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** As a Sensor Property: the time between a (step) change in the value of an observed ObservableProperty and a Sensor (possibly with specified error) 'settling' on an observed value, under the defined Conditions.

      As an Actuator property: the time between a (step) change in the command of an Actuator and the 'settling' of the value of the acted on ActuatableProperty, under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000008` (temporal region; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000199` (occupies temporal region; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000228` (Planned Act; asserted_target_expression; glossary); `cco:ont00000660` (Effect; asserted_target_expression; glossary); `cco:ont00000978` (Cause; asserted_target_expression; glossary); `cco:ont00001777` (has process part; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:ResponseTime satisfies bfo:Function and bfo:has_realization some (cco:PlannedAct and (cco:has_process_part some cco:Cause) and (cco:has_process_part some cco:Effect) and (bfo:occupies_temporal_region some (bfo:TemporalRegion and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does time from stimulus change to settled result justify the current commitment to Function and an actual PlannedAct with Cause/Effect parts, using the same target pattern as Latency, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional ResponseTime restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional ResponseTime restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!25`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/ResponseTime`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Selectivity

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!26` / `urn:uuid:3ddcc935-040b-450b-8ffa-8b0972e33c3b`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (cco:PlannedAct and bfo:has_participant some (bfo:Continuant and cco:prescribed_by some cco:ArtifactFunctionSpecification)).

**Source semantics:** As a Sensor Property: Selectivity is a Property of a Sensor whereby it provides observed values for one or more ObservableProperties such that the Results for each ObservableProperty are independent of other Properties in the FeatureOfInterest being investigated,  under the defined Conditions.

      As an Actuator Property: Selectivity is a Property of an Actuator whereby it acts on one or more ActuatableProperties such as the Results for each ActuatableProperty are independent of other Properties in the FeatureOfInterest being acted on, under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000002` (continuant; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000057` (has participant; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000228` (Planned Act; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Selectivity satisfies bfo:Function and bfo:has_realization some (cco:PlannedAct and bfo:has_participant some (bfo:Continuant and cco:prescribed_by some cco:ArtifactFunctionSpecification)); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does distinguishing a Property from other influences justify the current commitment to Function with an actual PlannedAct and a participating Continuant prescribed by an ArtifactFunctionSpecification, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Selectivity restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Selectivity restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!26`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Selectivity`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:Sensitivity

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!27` / `urn:uuid:624eaef2-892a-4b9d-8ed6-08c79571710f`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:RatioMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))).

**Source semantics:** As a Sensor Property: Sensitivity is the quotient of the change in a Result of Observation and the corresponding change in a value of an ObservableProperty being observed, under the defined Conditions.

       As an Actuator Property: Sensitivity is the quotient of the change in a command of Actuation and the corresponding change in a value of an ActuatableProperty being acted on, under the defined Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SystemProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `cco:ont00000118` (Artifact Function Specification; asserted_target_expression; glossary); `cco:ont00000853` (Descriptive Information Content Entity; asserted_target_expression; glossary); `cco:ont00001022` (Ratio Measurement Information Content Entity; asserted_target_expression; glossary); `cco:ont00001801` (is subject of; asserted_target_expression; glossary); `cco:ont00001904` (is measured by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:Sensitivity satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:is_subject_of some (cco:DescriptiveInformationContentEntity and cco:is_measured_by some (cco:RatioMeasurementInformationContentEntity and cco:prescribed_by some cco:ArtifactFunctionSpecification))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does change in result relative to change in observed property justify the current commitment to Function and a RatioMeasurementInformationContentEntity through actual realization and description, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional Sensitivity restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional Sensitivity restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!27`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/Sensitivity`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:SurvivalProperty

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!28` / `urn:uuid:304f62a7-9160-4857-9c39-04a7215b1bb0`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (bfo:Process and cco:caused_by some (bfo:Process and bfo:realizes some (cco:Affordance and cco:prescribed_by some cco:ArtifactDesign))).

**Source semantics:** An identifiable characteristic that represents the extent of the System's useful life under the specified Conditions. May describe for example total battery life or number of recharges, or, for Sensors that are used only a fixed number of times, the number of observations that can be made before the sensing capability is depleted.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasSurvivalProperty) owl:allValuesFrom ssn-system:SurvivalRange); rdfs:subClassOf (inverse(ssn-system:hasSurvivalProperty) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000055` (realizes; asserted_target_expression; glossary); `cco:ont00000177` (Affordance; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00001819` (caused by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:SurvivalProperty satisfies bfo:Function and bfo:has_realization some (bfo:Process and cco:caused_by some (bfo:Process and bfo:realizes some (cco:Affordance and cco:prescribed_by some cco:ArtifactDesign))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:BatteryLifetime rdfs:subClassOf ssn-system:SurvivalProperty`.
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf (ssn-system:hasSurvivalProperty owl:allValuesFrom ssn-system:SurvivalProperty)`.
- `source_native` / asserted: `ssn-system:SystemLifetime rdfs:subClassOf ssn-system:SurvivalProperty`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does extent of useful life under specified conditions justify the current commitment to Function with an actual realization caused by another Process realizing a design-prescribed Affordance, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional SurvivalProperty restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional SurvivalProperty restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!28`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/SurvivalProperty`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:SurvivalRange

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!44` / `urn:uuid:c15208c5-847f-4de3-a456-4037142ca542`: `rdfs:subClassOf` bfo:Function and (bfo:has_realization some (bfo:Process and (cco:caused_by some (bfo:Process and (bfo:realizes some (cco:Affordance and (cco:prescribed_by some cco:ArtifactDesign))))))).

**Source semantics:** Describes SurvivalProperties of a System under some specified Conditions. For example, the lifetime of a System under a specified temperature range.

    In the absence of SurvivalProperties, simply describes the Conditions a System can be exposed to without damage. For example, the temperature range a System can withstand before being considered damaged.

    The System continues to operate as defined using SystemCapability. If, however, the SurvivalRange is violated, the System is 'damaged' and SystemCapability specifications may no longer hold.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasSurvivalRange) owl:allValuesFrom ssn:System); rdfs:subClassOf (ssn-system:hasSurvivalProperty owl:allValuesFrom ssn-system:SurvivalProperty); rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition); rdfs:subClassOf (ssn-system:inCondition owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000055` (realizes; asserted_target_expression; glossary); `cco:ont00000177` (Affordance; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00001819` (caused by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:SurvivalRange satisfies bfo:Function and (bfo:has_realization some (bfo:Process and (cco:caused_by some (bfo:Process and (bfo:realizes some (cco:Affordance and (cco:prescribed_by some cco:ArtifactDesign))))))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:SurvivalProperty rdfs:subClassOf (inverse(ssn-system:hasSurvivalProperty) owl:allValuesFrom ssn-system:SurvivalRange)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn-system:hasSurvivalRange owl:allValuesFrom ssn-system:SurvivalRange)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does conditions under which a System can be exposed without damage justify the current commitment to Function with an actual realization and causal/design Affordance chain, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional SurvivalRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional SurvivalRange restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!44`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/SurvivalRange`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:SystemCapability

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!29` / `urn:uuid:c912bc86-4ac6-4200-8606-7fda6005542f`: `rdfs:subClassOf` (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and (cco:condition_described_by some cco:PerformanceSpecification).

**Source semantics:** Describes normal measurement, actuation, sampling properties such as accuracy, range, precision, etc. of a System under some specified Conditions such as a temperature range.

    The capabilities specified here are those that affect the primary purpose of the System, while those in OperatingRange represent the system's normal operating environment, including conditions that don't affect the observations or the actuations.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom ssn:System); rdfs:subClassOf (ssn-system:hasSystemProperty owl:allValuesFrom ssn-system:SystemProperty); rdfs:subClassOf (ssn-system:inCondition owl:allValuesFrom ssn-system:Condition); rdfs:subClassOf (ssn-system:inCondition owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>); rdfs:subClassOf (ssn:forProperty owl:allValuesFrom ssn:Property); rdfs:subClassOf ssn:Property

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000020` (specifically dependent continuant; asserted_target_expression; glossary); `bfo:BFO_0000144` (Process Profile; asserted_target_expression; glossary); `cco:ont00000127` (Performance Specification; asserted_target_expression; glossary); `cco:ont00001884` (condition described by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:SystemCapability satisfies (bfo:SpecificallyDependentContinuant or bfo:ProcessProfile) and (cco:condition_described_by some cco:PerformanceSpecification); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:SystemProperty rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom ssn-system:SystemCapability)`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (ssn-system:hasSystemCapability owl:allValuesFrom ssn-system:SystemCapability)`.

**Relevant property chains (ordered path → superproperty):**
- `target_native`: `bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980`.
- `target_native`: `cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884`.

**Human decision:** Does capability of a system under conditions justify the current commitment to SDC-or-ProcessProfile and an actual PerformanceSpecification describing its condition, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional SystemCapability restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional SystemCapability restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!29`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/SystemCapability`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:SystemLifetime

State: **unreviewed**; priority 4; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!30` / `urn:uuid:ad8cba71-f987-4e6a-b9c0-7660d5cbc8a7`: `rdfs:subClassOf` bfo:Function and bfo:has_realization some (cco:StasisOfArtifactOperationality and (cco:caused_by some (bfo:Process and bfo:realizes some (cco:Affordance and cco:prescribed_by some cco:ArtifactDesign)))).

**Source semantics:** Total useful life of a System (expressed as total life since manufacture, time in use, number of operations, etc.) in the specified Conditions.

Source structure: rdf:type owl:Class; rdfs:subClassOf ssn-system:SurvivalProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000015` (process; asserted_target_expression; glossary); `bfo:BFO_0000034` (function; asserted_target_expression; glossary); `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000055` (realizes; asserted_target_expression; glossary); `cco:ont00000177` (Affordance; asserted_target_expression; glossary); `cco:ont00000319` (Artifact Design; asserted_target_expression; glossary); `cco:ont00001213` (Stasis of Artifact Operationality; asserted_target_expression; glossary); `cco:ont00001819` (caused by; asserted_target_expression; glossary); `cco:ont00001920` (prescribed by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:SystemLifetime satisfies bfo:Function and bfo:has_realization some (cco:StasisOfArtifactOperationality and (cco:caused_by some (bfo:Process and bfo:realizes some (cco:Affordance and cco:prescribed_by some cco:ArtifactDesign)))); the reverse classification is not asserted. Each 'some' requires at least one actual filler; this is not merely a capability or possible realization.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does useful system life justify the current commitment to Function with an actual operational stasis caused by a Process realizing a design-prescribed Affordance, or does it describe a property/capability without those actual individuals?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review the inherited source superclass alignment before retaining the additional SystemLifetime restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Proposed recommendation:** Retain the artifact during review. Review the inherited source superclass alignment before retaining the additional SystemLifetime restrictions; if it is sufficient, propose removing only the unsupported direct strengthening through an approved mapping change.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!30`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/SystemLifetime`; `imports/cco.ttl`; `reports/system-property-process-profile-scope-review.md`; `reports/ssn-systems-domain-range-operationalization-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## sosa:hosts

State: **unreviewed**; priority 6; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!18` / `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`: `owl:propertyChainAxiom` bfo:bearer_of o bfo:has_realization o bfo:has_participant.

**Source semantics:** Relation between a Platform and a Sensor, Actuator, Sampler, or Platform, hosted or mounted on it.

Source structure: owl:inverseOf sosa:isHostedBy; rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Platform; <http://schema.org/rangeIncludes> sosa:Actuator; <http://schema.org/rangeIncludes> sosa:Platform; <http://schema.org/rangeIncludes> sosa:Sampler; <http://schema.org/rangeIncludes> sosa:Sensor

**Target semantics:** `bfo:BFO_0000054` (has realization; asserted_target_expression; glossary); `bfo:BFO_0000057` (has participant; asserted_target_expression; glossary); `bfo:BFO_0000196` (bearer of; asserted_target_expression; glossary)

**Logical consequences:** A path bfo:bearer_of o bfo:has_realization o bfo:has_participant from x to y entails sosa:hosts(x,y). The axiom does not decompose an arbitrary sosa:hosts edge into that path and does not itself give sosa:hosts a target superproperty.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Platform rdfs:subClassOf (sosa:hosts owl:allValuesFrom ssn:System)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `ssn:inDeployment o ssn:deployedSystem -> sosa:hosts`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

Additional route evidence: [{"mapping_row_id": "urn:uuid:e866de80-683d-4138-a713-be9646d37148", "mode": "inverse_chain_head", "source_path": ["sosa:hosts owl:inverseOf sosa:isHostedBy"], "conditions": "Reverse each chain relation and order; this infers source edges from target paths, not target edges from arbitrary source assertions."}]

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!34`: `sosa:hosts` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:hosts relates a Platform to an Asset hosted or mounted on it. BFO located-in/location-of encode spatial containment, which is not entailed by all hosting or mounting arrangements; BFO parthood is likewise not required, and process participation does not express hosting. The previously considered role-realization chain overgenerates hosts for arbitrary participants in a realization. No reviewed direct BFO/CCO relation preserves the source semantics. Comparison basis: same lexical term.

**Human decision:** Does every bearer-realization-participant path establish hosting, and does the current chain direction match the intended platform-support interpretation?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain the incoming chain only if sufficient for hosting; otherwise propose a separate mediated/explanatory pattern without treating hosts edges as outgoing target paths.

**Proposed recommendation:** Retain the artifact during review. Retain the incoming chain only if sufficient for hosting; otherwise propose a separate mediated/explanatory pattern without treating hosts edges as outgoing target paths.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!18`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/hosts`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/hosts`; `imports/cco.ttl`; `reports/hosts-implementedby-complex-mapping-review.md`; `reports/isHostedBy-hosts-full-closure-analysis.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:isHostedBy

State: **unreviewed**; priority 6; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!19` / `urn:uuid:e866de80-683d-4138-a713-be9646d37148`: `owl:propertyChainAxiom` bfo:participates_in o bfo:realizes o bfo:inheres_in.

**Source semantics:** Relation between a Sensor, Actuator, Sampler, or Platform, and the Platform that it is mounted on or hosted by.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Actuator; <http://schema.org/domainIncludes> sosa:Platform; <http://schema.org/domainIncludes> sosa:Sampler; <http://schema.org/domainIncludes> sosa:Sensor; <http://schema.org/rangeIncludes> sosa:Platform

**Target semantics:** `bfo:BFO_0000055` (realizes; asserted_target_expression; glossary); `bfo:BFO_0000056` (participates in; asserted_target_expression; glossary); `bfo:BFO_0000197` (inheres in; asserted_target_expression; glossary)

**Logical consequences:** A path bfo:participates_in o bfo:realizes o bfo:inheres_in from x to y entails sosa:isHostedBy(x,y). The axiom does not decompose an arbitrary sosa:isHostedBy edge into that path and does not itself give sosa:isHostedBy a target superproperty.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:hosts owl:inverseOf sosa:isHostedBy`.
- `source_native` / asserted: `ssn:System rdfs:subClassOf (sosa:isHostedBy owl:allValuesFrom sosa:Platform)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `ssn:inDeployment o ssn:deployedSystem -> sosa:hosts`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

Additional route evidence: [{"mapping_row_id": "urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e", "mode": "inverse_chain_head", "source_path": ["sosa:isHostedBy owl:inverseOf sosa:hosts"], "conditions": "Reverse each chain relation and order; this infers source edges from target paths, not target edges from arbitrary source assertions."}]

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!43`: `sosa:isHostedBy` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sosa:isHostedBy relates an Asset to a Platform on which it is hosted or mounted. Reversing the previously considered spatial or parthood relations does not remove their excess strength: hosting or mounting does not entail spatial containment or parthood. Process participation likewise does not express hosting. No reviewed direct BFO/CCO relation preserves the source semantics. Comparison basis: same lexical term.

**Human decision:** Does every participates_in-realizes-inheres_in path establish being hosted, and is it the intended inverse of the hosts-chain interpretation?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain the inverse incoming chain if hosting sufficiency is defended; otherwise review both chain heads together.

**Proposed recommendation:** Retain the artifact during review. Retain the inverse incoming chain if hosting sufficiency is defended; otherwise review both chain heads together.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!19`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/isHostedBy`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/isHostedBy`; `imports/cco.ttl`; `reports/hosts-implementedby-complex-mapping-review.md`; `reports/isHostedBy-hosts-full-closure-analysis.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sosa:madeBySensor

State: **unreviewed**; priority 7; evidence confidence: Historical implementation and current technical validation verified; assessment review state unchanged..

**Repository facts — mapping:**

- `Sheet2!32` / `urn:uuid:434602eb-cfc3-4bca-9fb3-92154e87c6bc`: `rdfs:domain` sosa:Observation.

- `Sheet2!33` / `urn:uuid:99f8aba6-abaa-49de-a126-da1573f24c39`: `rdfs:range` sosa:Sensor.

- `Sheet2!63` / `urn:uuid:409597ab-258b-47fd-9f51-c50d22b405bd`: `rdfs:subPropertyOf` cco:has_agent.

**Source semantics:** Relation between an Observation and the Sensor which made the Observation.

Source structure: owl:inverseOf sosa:madeObservation; rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Observation; <http://schema.org/rangeIncludes> sosa:Sensor

**Target semantics:** `cco:ont00001833` (has agent; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted sosa:madeBySensor(x,y) types x as sosa:Observation; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:madeBySensor(x,y) types y as sosa:Sensor; no BFO/CCO relation edge is entailed by this typing axiom alone. Every sosa:madeBySensor(x,y) entails cco:has_agent(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:madeBySensor owl:allValuesFrom sosa:Sensor)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:madeBySensor owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:madeBySensor rdfs:range sosa:Sensor`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:madeBySensor rdfs:domain sosa:Observation` (RowID `urn:uuid:434602eb-cfc3-4bca-9fb3-92154e87c6bc`).
- `source_native`: `sosa:Observation rdfs:subClassOf (sosa:madeBySensor owl:allValuesFrom sosa:Sensor)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `sosa:madeBySensor o ssn:implements -> sosa:usedProcedure`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!60`: `sosa:madeBySensor` — `active`, `rdfs:subPropertyOf` cco:has_agent.  Comparison basis: same lexical term.

**Human decision:** Does the current implementation preserve the historically authorized treatment? The focused recovery checks confirm it.

**Alternatives:**
- Preserve the historically authorized treatment recorded in the semantic transition.

**Proposed recommendation:** Retain this recovered historical implementation; this task opens no new semantic adjudication.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!32`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!33`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/madeBySensor`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/madeBySensor`; `imports/cco.ttl`; `reports/sosa-sensor-version-alignment-resolution.md`; `reports/madeObservation-madeBySensor-agent-pair-full-closure-analysis.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!63`; `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/entailment-result.json`.

**Notes:** Historical implementation recovery authorized on 2026-10-30 and validated against the complete available pinned local ontology. This records historical decision provenance; no new scientific decision or assessment finalization is created. Source-native axioms and separately governed SOSA-2023 products are unchanged.

## sosa:madeObservation

State: **unreviewed**; priority 7; evidence confidence: Historical implementation and current technical validation verified; assessment review state unchanged..

**Repository facts — mapping:**

- `Sheet2!34` / `urn:uuid:839fa73d-6601-4b17-9331-062846ba0f3e`: `rdfs:domain` sosa:Sensor.

- `Sheet2!35` / `urn:uuid:e2d7f509-a5ee-477a-9660-f608b518ea3f`: `rdfs:range` sosa:Observation.

- `Sheet2!64` / `urn:uuid:418db51e-342f-441d-8706-00a107266dcc`: `rdfs:subPropertyOf` cco:agent_in.

**Source semantics:** Relation between a Sensor and an Observation made by the Sensor.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Sensor; <http://schema.org/rangeIncludes> sosa:Observation

**Target semantics:** `cco:ont00001787` (agent in; historical_or_review_candidate_only; glossary)

**Logical consequences:** An asserted sosa:madeObservation(x,y) types x as sosa:Sensor; no BFO/CCO relation edge is entailed by this typing axiom alone. An asserted sosa:madeObservation(x,y) types y as sosa:Observation; no BFO/CCO relation edge is entailed by this typing axiom alone. Every sosa:madeObservation(x,y) entails cco:agent_in(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Sensor rdfs:subClassOf (sosa:madeObservation owl:allValuesFrom sosa:Observation)`.
- `source_native` / asserted: `sosa:madeBySensor owl:inverseOf sosa:madeObservation`.

**Derived evidence** (`generated_inference`, premises from mapping, source_native): `sosa:madeObservation rdfs:range sosa:Observation`. Every property subject belongs to the declared domain or one of its union branches; each branch restricts all values of this property to the stated class. Thus every object has that type. This derived consequence is separate from an explicit range assertion and makes no mapping decision.

Asserted premises:
- `mapping`: `sosa:madeObservation rdfs:domain sosa:Sensor` (RowID `urn:uuid:839fa73d-6601-4b17-9331-062846ba0f3e`).
- `source_native`: `sosa:Sensor rdfs:subClassOf (sosa:madeObservation owl:allValuesFrom sosa:Observation)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `sosa:madeBySensor o ssn:implements -> sosa:usedProcedure`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!63`: `sosa:madeObservation` — `active`, `rdfs:subPropertyOf` cco:agent_in. Explicit inverse-derived mapping. The pinned SOSA source declares sosa:madeObservation owl:inverseOf sosa:madeBySensor; the governed COMS mapping asserts sosa:madeBySensor rdfs:subPropertyOf cco:has_agent; and the pinned BFO/CCO target declares cco:has_agent owl:inverseOf cco:agent_in. Therefore sosa:madeObservation rdfs:subPropertyOf cco:agent_in is entailed. The direct COMS axiom is materialized explicitly under the project policy for inverse-derived mappings. Comparison basis: same lexical term.

**Human decision:** Does the current implementation preserve the historically authorized treatment? The focused recovery checks confirm it.

**Alternatives:**
- Preserve the historically authorized treatment recorded in the semantic transition.

**Proposed recommendation:** Retain this recovered historical implementation; this task opens no new semantic adjudication.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!34`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!35`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/madeObservation`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/madeObservation`; `imports/cco.ttl`; `reports/madeObservation-madeBySensor-agent-pair-full-closure-analysis.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`; `mappings/SSN2BFO-COMS.xlsx#Sheet2!64`; `reports/current-semantic-workbook/transitions/d572d028-9788-4e8e-a87a-085f64f399e8.json`; `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/validation-result.json`; `reports/current-semantic-workbook/historical-recovery-2026-10-30/sensor/entailment-result.json`.

**Notes:** Historical implementation recovery authorized on 2026-10-30 and validated against the complete available pinned local ontology. This records historical decision provenance; no new scientific decision or assessment finalization is created. Source-native axioms and separately governed SOSA-2023 products are unchanged.

## sosa:phenomenonTime

State: **unreviewed**; priority 7; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!11` / `urn:uuid:2abe4468-736d-4db8-99d7-1670730a6710`: `rdfs:subPropertyOf` bfo:occupies_temporal_region.

**Source semantics:** The time that the Result of an Observation, Actuation or Sampling applies to the FeatureOfInterest. Not necessarily the same as the resultTime. May be an Interval or an Instant, or some other compound TemporalEntity.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sosa:Actuation; <http://schema.org/domainIncludes> sosa:Observation; <http://schema.org/domainIncludes> sosa:Sampling; <http://schema.org/rangeIncludes> <http://www.w3.org/2006/time#TemporalEntity>

**Target semantics:** `bfo:BFO_0000199` (occupies temporal region; asserted_target_expression; glossary)

**Logical consequences:** Every sosa:phenomenonTime(x,y) entails bfo:occupies_temporal_region(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (sosa:phenomenonTime owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!72`: `sosa:phenomenonTime` — `active`, `rdfs:range` bfo:TemporalRegion. Replace the explicitly unmapped disposition with rdfs:range bfo:TemporalRegion. The pinned source declares phenomenonTime as an owl:ObjectProperty from an Execution or ExecutionCollection to the time at which its result applies. No BFO or CCO temporal superproperty is adopted because this time may differ from the Execution's own occupied temporal region. Comparison basis: same lexical term.

**Human decision:** Must the time to which a result applies equal the temporal region occupied by the observation/actuation/sampling itself?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Keep the earlier-interval scenario documented as a potential counterexample without declaring a demonstrated inconsistency or a settled refutation. No alternative mapping is authorized by this instruction.

**Proposed recommendation:** Per explicit human instruction, retain the existing sosa:phenomenonTime rdfs:subPropertyOf bfo:BFO_0000199 mapping unchanged. Potential counterexample: An Observation may produce a Result whose phenomenonTime refers to an earlier temporal interval than the interval occupied by the Observation process itself. For example, an observation conducted today may estimate a phenomenon from yesterday. In that case, the result-applicability time would differ from the process's temporal occupancy, potentially undermining the universal subproperty inclusion. This is a potential counterexample, not a demonstrated inconsistency or a settled refutation. The instruction does not definitively validate the interpretation; the assessment remains unreviewed.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!11`; `imports/sosa.ttl#http://www.w3.org/ns/sosa/phenomenonTime`; `imports/ssn.ttl#http://www.w3.org/ns/sosa/phenomenonTime`; `imports/cco.ttl`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`; `reports/current-documentary-workbook/phenomenon-time-retention-2026-10-30/authorized-instructions.txt`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sampling:natureOfRelationship

State: **unreviewed**; priority 7; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!3` / `urn:uuid:f293250d-b1e8-4467-8b7d-a94fb2b9b705`: `rdfs:subPropertyOf` cco:is_about.

**Source semantics:** Links a SampleRelationship to an indication of the nature of the relationship

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: <http://schema.org/domainIncludes> sampling:SampleRelationship; <http://schema.org/rangeIncludes> sampling:RelationshipNature

**Target semantics:** `cco:ont00001808` (is about; asserted_target_expression; glossary)

**Logical consequences:** Every sampling:natureOfRelationship(x,y) entails cco:is_about(x,y), including target domain/range and superproperty consequences.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!6`: `sampling:natureOfRelationship` — `no_direct_mapping`, `` . No direct BFO/CCO object-property mapping is adopted. sampling:natureOfRelationship links a reified SampleRelationship to an indication of its RelationshipNature. The source relation does not entail that the nature indicator is an Information Content Entity, measurement, description, or specifically dependent continuant of the relationship. CCO descriptive, measurement, aboutness, and BFO dependence relations therefore impose unsupported typing or stronger semantics. Comparison basis: same lexical term.

**Human decision:** Does connecting a relationship to its nature express CCO aboutness between information content and its subject, or classify the relationship instead?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Keep is_about only with an explicit account of what information content is about here; review classification/annotation alternatives separately.

**Proposed recommendation:** Retain the artifact during review. Keep is_about only with an explicit account of what information content is about here; review classification/annotation alternatives separately.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!3`; `imports/sosa-sampling.ttl#http://www.w3.org/ns/sosa/sampling/natureOfRelationship`; `imports/cco.ttl`; `reports/sample-relationship-deferral.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## ssn:wasOriginatedBy

State: **unreviewed**; priority 7; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!62` / `urn:uuid:51c8556f-9b82-4113-a9d7-c733e70cf8cd`: `rdfs:subPropertyOf` cco:process_started_by.

**Source semantics:** Relation between an Observation and the Stimulus that originated it.

Source structure: rdf:type owl:FunctionalProperty; rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `cco:ont00001962` (process started by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:wasOriginatedBy(x,y) entails cco:process_started_by(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (ssn:wasOriginatedBy owl:allValuesFrom ssn:Stimulus)`.
- `source_native` / asserted: `sosa:Observation rdfs:subClassOf (ssn:wasOriginatedBy owl:cardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn:Stimulus rdfs:subClassOf (inverse(ssn:wasOriginatedBy) owl:allValuesFrom sosa:Observation)`.

**Pinned-track comparison:** `mappings/SOSA-next-to-BFO-COMS.xlsx#Sheet2!83`: `sosa:wasOriginatedBy` — `active`, `rdfs:subPropertyOf` cco:caused_by. Replace cco:process_started_by with cco:caused_by. This is the inverse-side counterpart of adapting sosa:originated to cco:is_cause_of. The source supports Observation-to-Stimulus causal direction but does not entail the stronger temporal-start conditions of cco:process_started_by. Comparison basis: local-name comparison only; distinct namespace/source version.

**Human decision:** Does every originating Stimulus temporally start the Observation, as CCO process_started_by requires, or does source meaning establish only causation?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review caused_by as a weaker candidate, preserving direction; do not automatically adopt the N-track decision.

**Proposed recommendation:** Retain the artifact during review. Review caused_by as a weaker candidate, preserving direction; do not automatically adopt the N-track decision.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!62`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/wasOriginatedBy`; `imports/cco.ttl`; `reports/sosa-next-crosswalk-reconciliation.md`; `mappings/SOSA-next-to-BFO-COMS.xlsx`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted. The pinned-track comparison records different assertions; the same local name is not proof of equivalent source meaning or identical target identity.

## sampling:RelationshipNature

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!2` / `urn:uuid:f475ef3c-12f0-4925-ad21-419ebd96406b`: `rdfs:subClassOf` cco:InformationContentEntity.

**Source semantics:** Members of this class indicate the nature of a relationship between two samples

Source structure: rdf:type owl:Class; rdfs:subClassOf <http://www.w3.org/2004/02/skos/core#Concept>

Source advisory signature: none recorded

**Target semantics:** `cco:ont00000958` (Information Content Entity; asserted_target_expression; glossary)

**Logical consequences:** Every sampling:RelationshipNature satisfies cco:InformationContentEntity; the reverse classification is not asserted.

**Human decision:** Is the nature of a sample relationship an information-content entity, or does the source Concept class permit a broader conceptual/category interpretation?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Keep the ICE subclass as a deliberate information-content interpretation only after closing the original provisional review.

**Proposed recommendation:** Retain the artifact during review. Keep the ICE subclass as a deliberate information-content interpretation only after closing the original provisional review.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!2`; `imports/sosa-sampling.ttl#http://www.w3.org/ns/sosa/sampling/RelationshipNature`; `imports/cco.ttl`; `reports/sample-relationship-deferral.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn:Input

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!32` / `urn:uuid:282b2a18-f710-4eac-a5c8-43894a242f23`: `rdfs:subClassOf` cco:InformationContentEntity.

**Source semantics:** Any information that is provided to a Procedure for its use.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn:hasInput) owl:allValuesFrom sosa:Procedure); rdfs:subClassOf (inverse(ssn:hasInput) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)

Source advisory signature: none recorded

**Target semantics:** `cco:ont00000958` (Information Content Entity; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:Input satisfies cco:InformationContentEntity; the reverse classification is not asserted.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Procedure rdfs:subClassOf (ssn:hasInput owl:allValuesFrom ssn:Input)`.

**Human decision:** Does every Input to a Procedure denote information content, or can the source class also denote a concrete input object/specification of such an object?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain ICE subclass only for the information-specification reading; otherwise review a broader category or no direct mapping.

**Proposed recommendation:** Retain the artifact during review. Retain ICE subclass only for the information-specification reading; otherwise review a broader category or no direct mapping.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!32`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/Input`; `imports/cco.ttl`; `reports/input-output-cco-mapping-rationale-cleanup.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn:Output

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet1!33` / `urn:uuid:89f70432-c87d-41dd-bff2-e6120c02b5a4`: `rdfs:subClassOf` cco:InformationContentEntity.

**Source semantics:** Any information that is reported from a Procedure.

Source structure: rdf:type owl:Class; rdfs:subClassOf (inverse(ssn:hasOutput) owl:allValuesFrom sosa:Procedure); rdfs:subClassOf (inverse(ssn:hasOutput) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)

Source advisory signature: none recorded

**Target semantics:** `cco:ont00000958` (Information Content Entity; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:Output satisfies cco:InformationContentEntity; the reverse classification is not asserted.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Procedure rdfs:subClassOf (ssn:hasOutput owl:allValuesFrom ssn:Output)`.

**Human decision:** Does every Output of a Procedure denote information content rather than a concrete thing described as output?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain ICE subclass only if the procedure-output specification reading is intended; do not infer the category from the rejected process-output relation.

**Proposed recommendation:** Retain the artifact during review. Retain ICE subclass only if the procedure-output specification reading is intended; do not infer the category from the rejected process-output relation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet1!33`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/Output`; `imports/cco.ttl`; `reports/input-output-cco-mapping-rationale-cleanup.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn:deployedOnPlatform

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!46` / `urn:uuid:af48aae7-263f-436d-a76a-4e7232c609c5`: `rdfs:subPropertyOf` bfo:has_participant.

**Source semantics:** Relation between a Deployment and the Platform on which the Systems are deployed.

Source structure: owl:inverseOf ssn:inDeployment; rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000057` (has participant; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:deployedOnPlatform(x,y) entails bfo:has_participant(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn:Deployment rdfs:subClassOf (ssn:deployedOnPlatform owl:allValuesFrom sosa:Platform)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `ssn:inDeployment o ssn:deployedSystem -> sosa:hosts`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does every Deployment-to-Platform relation require that the Platform participate in a process under the chosen PlannedAct reading?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain has_participant if the deployment process reading is intended; otherwise review the Deployment class interpretation before this relation.

**Proposed recommendation:** Retain the artifact during review. Retain has_participant if the deployment process reading is intended; otherwise review the Deployment class interpretation before this relation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!46`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/deployedOnPlatform`; `imports/cco.ttl`; `reports/inverse-side-direct-mapping-policy-review.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn:deployedSystem

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!47` / `urn:uuid:c0a94c70-33c7-41ac-8906-49ad2efe48b5`: `rdfs:subPropertyOf` bfo:has_participant.

**Source semantics:** Relation between a Deployment and a deployed System.

Source structure: owl:inverseOf ssn:hasDeployment; rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000057` (has participant; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:deployedSystem(x,y) entails bfo:has_participant(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn:Deployment rdfs:subClassOf (ssn:deployedSystem owl:allValuesFrom ssn:System)`.

**Relevant property chains (ordered path → superproperty):**
- `source_native`: `ssn:inDeployment o ssn:deployedSystem -> sosa:hosts`.
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does every Deployment-to-System relation establish participation in a process under the source arrangement/deployment interpretation?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain has_participant if the deployment process reading is adopted; otherwise review the class and relation together.

**Proposed recommendation:** Retain the artifact during review. Retain has_participant if the deployment process reading is adopted; otherwise review the class and relation together.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!47`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/deployedSystem`; `imports/cco.ttl`; `reports/inverse-side-direct-mapping-policy-review.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn:detects

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!48` / `urn:uuid:6335c13d-fb23-49fd-9662-fd682c79f172`: `rdfs:subPropertyOf` cco:is_affected_by.

**Source semantics:** A relation from a Sensor to the Stimulus that the Sensor detects. The Stimulus itself will be serving as a proxy for some ObservableProperty.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `cco:ont00001886` (is affected by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn:detects(x,y) entails cco:is_affected_by(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `sosa:Sensor rdfs:subClassOf (ssn:detects owl:allValuesFrom ssn:Stimulus)`.
- `source_native` / asserted: `ssn:Stimulus rdfs:subClassOf (inverse(ssn:detects) owl:allValuesFrom sosa:Sensor)`.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Does the source sensor-detects-stimulus relation always mean the sensor is causally affected by that stimulus in CCO’s sense?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain is_affected_by only with the causal-detection commitment made explicit, or record no-direct mapping.

**Proposed recommendation:** Retain the artifact during review. Retain is_affected_by only with the causal-detection commitment made explicit, or record no-direct mapping.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!48`; `imports/ssn.ttl#http://www.w3.org/ns/ssn/detects`; `imports/cco.ttl`; `reports/hermit-observation-sensor-stimulus-evaluation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:hasOperatingProperty

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!37` / `urn:uuid:37576663-68e9-4298-8652-a3c614c34ae3`: `rdfs:subPropertyOf` bfo:specifically_depended_on_by.

**Source semantics:** Relation from an OperatingRange of a System to a OperatingPropery describing the operating range of the System.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:hasProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000194` (specifically depended on by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:hasOperatingProperty(x,y) entails bfo:specifically_depended_on_by(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:OperatingProperty rdfs:subClassOf (inverse(ssn-system:hasOperatingProperty) owl:allValuesFrom ssn-system:OperatingRange)`.
- `source_native` / asserted: `ssn-system:OperatingProperty rdfs:subClassOf (inverse(ssn-system:hasOperatingProperty) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn-system:OperatingRange rdfs:subClassOf (ssn-system:hasOperatingProperty owl:allValuesFrom ssn-system:OperatingProperty)`.

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Human decision:** Does OperatingRange-to-Property use require the Property to specifically depend on that container, and is the BFO dependence direction/category valid for all its source cases?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain specifically_depended_on_by only if the dependence and direction are defended; otherwise propose no-direct with typed conditional support or another explicitly reviewed relation.

**Proposed recommendation:** Retain the artifact during review. Retain specifically_depended_on_by only if the dependence and direction are defended; otherwise propose no-direct with typed conditional support or another explicitly reviewed relation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!37`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/hasOperatingProperty`; `imports/cco.ttl`; `reports/ssn-systems-property-split-mapping-review.md`; `reports/ssn-systems-dependence-reactivation-results.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:hasSurvivalProperty

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!40` / `urn:uuid:f0fbd0af-655a-46c8-bda9-1c2adb24a10a`: `rdfs:subPropertyOf` bfo:specifically_depended_on_by.

**Source semantics:** Relation from a SurvivalRange of a System to a SurvivalProperty describing the survival range of the System.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:hasProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000194` (specifically depended on by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:hasSurvivalProperty(x,y) entails bfo:specifically_depended_on_by(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:SurvivalProperty rdfs:subClassOf (inverse(ssn-system:hasSurvivalProperty) owl:allValuesFrom ssn-system:SurvivalRange)`.
- `source_native` / asserted: `ssn-system:SurvivalProperty rdfs:subClassOf (inverse(ssn-system:hasSurvivalProperty) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.
- `source_native` / asserted: `ssn-system:SurvivalRange rdfs:subClassOf (ssn-system:hasSurvivalProperty owl:allValuesFrom ssn-system:SurvivalProperty)`.

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Human decision:** Does SurvivalRange-to-Property use require the Property to specifically depend on that container, and is the BFO dependence direction/category valid for all its source cases?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain specifically_depended_on_by only if the dependence and direction are defended; otherwise propose no-direct with typed conditional support or another explicitly reviewed relation.

**Proposed recommendation:** Retain the artifact during review. Retain specifically_depended_on_by only if the dependence and direction are defended; otherwise propose no-direct with typed conditional support or another explicitly reviewed relation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!40`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/hasSurvivalProperty`; `imports/cco.ttl`; `reports/ssn-systems-property-split-mapping-review.md`; `reports/ssn-systems-dependence-reactivation-results.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:hasSystemProperty

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!45` / `urn:uuid:d8f45381-cd95-4251-ae69-803a033a8f49`: `rdfs:subPropertyOf` bfo:specifically_depended_on_by.

**Source semantics:** Relation from an SystemCapability of a System to a SystemProperty describing the capabilities of the System.

Source structure: rdf:type owl:ObjectProperty; rdfs:subPropertyOf ssn:hasProperty

Source advisory signature: none recorded

**Target semantics:** `bfo:BFO_0000194` (specifically depended on by; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:hasSystemProperty(x,y) entails bfo:specifically_depended_on_by(x,y), including target domain/range and superproperty consequences.

Asserted context (actual axiom subject and direction retained):
- `source_native` / asserted: `ssn-system:ActuationRange rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Actuator))`.
- `source_native` / asserted: `ssn-system:DetectionLimit rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor))`.
- `source_native` / asserted: `ssn-system:MeasurementRange rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom (inverse(ssn-system:hasSystemCapability) owl:allValuesFrom sosa:Sensor))`.
- `source_native` / asserted: `ssn-system:SystemCapability rdfs:subClassOf (ssn-system:hasSystemProperty owl:allValuesFrom ssn-system:SystemProperty)`.
- `source_native` / asserted: `ssn-system:SystemProperty rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:allValuesFrom ssn-system:SystemCapability)`.
- `source_native` / asserted: `ssn-system:SystemProperty rdfs:subClassOf (inverse(ssn-system:hasSystemProperty) owl:minCardinality "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>)`.

Additional route evidence: [{"artifact": "rules/ssn-hasproperty-conditional-mapping.rq", "mode": "conditional_external_query", "conditions": "Forward property assertion with source subproperty path to ssn:hasProperty; subject/object typed as independent continuant/SDC or occurrent/ProcessProfile. Requires executing query; not an OWL-product entailment."}]

**Human decision:** Does SystemCapability-to-Property use require the Property to specifically depend on that container, and is the BFO dependence direction/category valid for all its source cases?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Retain specifically_depended_on_by only if the dependence and direction are defended; otherwise propose no-direct with typed conditional support or another explicitly reviewed relation.

**Proposed recommendation:** Retain the artifact during review. Retain specifically_depended_on_by only if the dependence and direction are defended; otherwise propose no-direct with typed conditional support or another explicitly reviewed relation.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!45`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/hasSystemProperty`; `imports/cco.ttl`; `reports/ssn-systems-property-split-mapping-review.md`; `reports/ssn-systems-dependence-reactivation-results.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## ssn-system:qualityOfObservation

State: **unreviewed**; priority 8; evidence confidence: high for extracted assertions and stated logical consequences; unresolved for the ontological decision.

**Repository facts — mapping:**

- `Sheet2!14` / `urn:uuid:2018c5db-cb41-4a54-aa97-df5df82f0286`: `rdfs:subPropertyOf` cco:has_output.

**Source semantics:** Relation linking an Observation to the adjudged quality of the Result. This is complimentary to the SystemCapability information recorded for the Sensor that made the Observation.

Source structure: rdf:type owl:ObjectProperty

Source advisory signature: none recorded

**Target semantics:** `cco:ont00001986` (has output; asserted_target_expression; glossary)

**Logical consequences:** Every ssn-system:qualityOfObservation(x,y) entails cco:has_output(x,y), including target domain/range and superproperty consequences.

**Relevant property chains (ordered path → superproperty):**
- `mapping`: `bfo:BFO_0000056 o bfo:BFO_0000055 o bfo:BFO_0000197 -> sosa:isHostedBy` (RowID `urn:uuid:e866de80-683d-4138-a713-be9646d37148`).
- `mapping`: `bfo:BFO_0000196 o bfo:BFO_0000054 o bfo:BFO_0000057 -> sosa:hosts` (RowID `urn:uuid:3af8734c-ac86-46b0-8c0c-27a19525bc1e`).

**Human decision:** Is the quality associated with an Observation necessarily an output produced by that process, or a quality/description of it?

**Alternatives:**
- Retain the exact current rows shown, with a source-specific argument for their necessary/sufficient conditions or their deliberate absence.
- Review an aboutness/quality interpretation or no direct relation rather than automatically treating every quality assertion as produced output.

**Proposed recommendation:** Retain the artifact during review. Review an aboutness/quality interpretation or no direct relation rather than automatically treating every quality assertion as produced output.

**Evidence:** `mappings/SSN2BFO-COMS.xlsx#Sheet2!14`; `imports/ssn-systems.ttl#http://www.w3.org/ns/ssn/systems/qualityOfObservation`; `imports/cco.ttl`; `reports/sosa-next-crosswalk-reconciliation.md`.

**Notes:** Exact workbook facts control the current mapping state. Earlier reports may describe superseded assertions or reduced reasoning closures and are supplied as decision history, not as fresh validation. No semantic change is adopted.

## Target fact glossary

All facts below are extracted from `imports/cco.ttl`; labels are display aids and IRIs control identity.

### bfo:BFO_0000002 — continuant

(Elucidation) A continuant is an entity that persists, endures, or continues to exist through time while maintaining its identity

owl:disjointWith bfo:BFO_0000003; rdf:type owl:Class; rdfs:subClassOf (bfo:BFO_0000176 owl:allValuesFrom bfo:BFO_0000002); rdfs:subClassOf bfo:BFO_0000001

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000004 rdfs:subClassOf bfo:BFO_0000002`.
- `target_native` / asserted: `bfo:BFO_0000020 rdfs:subClassOf bfo:BFO_0000002`.
- `target_native` / asserted: `bfo:BFO_0000031 rdfs:subClassOf bfo:BFO_0000002`.
- `target_native` / asserted: `bfo:BFO_0000176 rdfs:domain bfo:BFO_0000002`.
- `target_native` / asserted: `bfo:BFO_0000176 rdfs:range bfo:BFO_0000002`.
- `target_native` / asserted: `bfo:BFO_0000178 rdfs:domain bfo:BFO_0000002`.
- `target_native` / asserted: `bfo:BFO_0000178 rdfs:range bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00000740 rdfs:subClassOf bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00001816 rdfs:domain bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00001834 rdfs:range bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00001841 rdfs:domain bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00001886 rdfs:domain bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00001921 rdfs:range bfo:BFO_0000002`.
- `target_native` / asserted: `cco:ont00001986 rdfs:range bfo:BFO_0000002`.

### bfo:BFO_0000008 — temporal region

(Elucidation) A temporal region is an occurrent over which processes can unfold

rdf:type owl:Class; rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom bfo:BFO_0000008); rdfs:subClassOf (bfo:BFO_0000139 owl:allValuesFrom bfo:BFO_0000008); rdfs:subClassOf bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000038 rdfs:subClassOf bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000108 rdfs:range bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000148 rdfs:subClassOf bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000153 rdfs:range bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000199 rdfs:range bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000221 rdfs:range bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000222 rdfs:domain bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000223 rdfs:range bfo:BFO_0000008`.
- `target_native` / asserted: `bfo:BFO_0000224 rdfs:domain bfo:BFO_0000008`.
- `target_native` / asserted: `cco:ont00000399 owl:equivalentClass (cco:ont00000686 and (cco:ont00001916 owl:someValuesFrom bfo:BFO_0000008))`.
- `target_native` / asserted: `cco:ont00001874 rdfs:domain bfo:BFO_0000008`.
- `target_native` / asserted: `owl:AllDisjointClasses owl:members (bfo:BFO_0000008, bfo:BFO_0000011, bfo:BFO_0000015, bfo:BFO_0000035)`.

### bfo:BFO_0000015 — process

(Elucidation) p is a process means p is an occurrent that has some temporal proper part and for some time t, p has some material entity as participant

rdf:type owl:Class; rdfs:subClassOf (bfo:BFO_0000117 owl:allValuesFrom (bfo:BFO_0000015 or bfo:BFO_0000035)); rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom bfo:BFO_0000015); rdfs:subClassOf (bfo:BFO_0000139 owl:allValuesFrom bfo:BFO_0000015); rdfs:subClassOf bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000035 rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom (bfo:BFO_0000015 or bfo:BFO_0000035))`.
- `target_native` / asserted: `bfo:BFO_0000035 rdfs:subClassOf (bfo:BFO_0000139 owl:allValuesFrom (bfo:BFO_0000015 or bfo:BFO_0000035))`.
- `target_native` / asserted: `bfo:BFO_0000054 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `bfo:BFO_0000055 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `bfo:BFO_0000056 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `bfo:BFO_0000057 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `bfo:BFO_0000058 rdfs:range (bfo:BFO_0000015 or bfo:BFO_0000020)`.
- `target_native` / asserted: `bfo:BFO_0000059 rdfs:domain (bfo:BFO_0000015 or bfo:BFO_0000020)`.
- `target_native` / asserted: `bfo:BFO_0000066 rdfs:domain (bfo:BFO_0000015 or bfo:BFO_0000035)`.
- `target_native` / asserted: `bfo:BFO_0000182 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `bfo:BFO_0000183 rdfs:range (bfo:BFO_0000015 or bfo:BFO_0000035)`.
- `target_native` / asserted: `bfo:BFO_0000199 rdfs:domain (bfo:BFO_0000015 or bfo:BFO_0000035)`.
- `target_native` / asserted: `bfo:BFO_0000200 rdfs:domain (bfo:BFO_0000015 or bfo:BFO_0000035)`.
- `target_native` / asserted: `cco:ont00000004 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00000005 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00000007 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00000110 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00000553 owl:equivalentClass (cco:ont00001324 and (cco:ont00001800 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00000660 owl:equivalentClass (bfo:BFO_0000015 and (cco:ont00001819 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00000660 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00000751 owl:equivalentClass (cco:ont00001324 and (cco:ont00001910 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00000819 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00000978 owl:equivalentClass (bfo:BFO_0000015 and (cco:ont00001803 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00000978 rdfs:subClassOf bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001224 owl:equivalentClass (cco:ont00001324 and (cco:ont00001974 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00001777 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001777 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001800 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001805 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001805 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001807 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001816 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001817 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001830 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001834 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001841 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001845 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001852 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001857 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001857 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001866 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001874 rdfs:range (bfo:BFO_0000015 or bfo:BFO_0000035)`.
- `target_native` / asserted: `cco:ont00001886 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001888 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001888 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001895 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001910 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001918 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001921 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001949 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001959 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001959 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001970 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001970 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001974 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001984 rdfs:range bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001986 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `cco:ont00001998 rdfs:domain bfo:BFO_0000015`.
- `target_native` / asserted: `owl:AllDisjointClasses owl:members (bfo:BFO_0000008, bfo:BFO_0000011, bfo:BFO_0000015, bfo:BFO_0000035)`.

### bfo:BFO_0000016 — disposition

(Elucidation) A disposition b is a realizable entity such that if b ceases to exist then its bearer is physically changed & b's realization occurs when and because this bearer is in some special physical circumstances & this realization occurs in virtue of the bearer's physical make-up

owl:disjointWith bfo:BFO_0000023; rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000017

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000034 rdfs:subClassOf bfo:BFO_0000016`.
- `target_native` / asserted: `bfo:BFO_0000127 rdfs:range bfo:BFO_0000016`.
- `target_native` / asserted: `bfo:BFO_0000218 rdfs:domain bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00000318 rdfs:subClassOf bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00000609 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000016)))`.
- `target_native` / asserted: `cco:ont00000628 rdfs:subClassOf bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00000632 rdfs:subClassOf bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00000997 rdfs:subClassOf bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00001118 rdfs:subClassOf bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00001829 rdfs:domain bfo:BFO_0000016`.
- `target_native` / asserted: `cco:ont00001956 rdfs:range bfo:BFO_0000016`.

### bfo:BFO_0000017 — realizable entity

(Elucidation) A realizable entity is a specifically dependent continuant that inheres in some independent continuant which is not a spatial region & which is of a type some instances of which are realized in processes of a correlated type

owl:disjointWith bfo:BFO_0000019; rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000020

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000016 rdfs:subClassOf bfo:BFO_0000017`.
- `target_native` / asserted: `bfo:BFO_0000023 rdfs:subClassOf bfo:BFO_0000017`.
- `target_native` / asserted: `bfo:BFO_0000054 rdfs:domain bfo:BFO_0000017`.
- `target_native` / asserted: `bfo:BFO_0000055 rdfs:range bfo:BFO_0000017`.
- `target_native` / asserted: `cco:ont00000177 rdfs:subClassOf bfo:BFO_0000017`.
- `target_native` / asserted: `cco:ont00000284 rdfs:subClassOf bfo:BFO_0000017`.
- `target_native` / asserted: `cco:ont00000642 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000017)))`.
- `target_native` / asserted: `cco:ont00001193 rdfs:subClassOf bfo:BFO_0000017`.
- `target_native` / asserted: `cco:ont00001379 rdfs:subClassOf bfo:BFO_0000017`.

### bfo:BFO_0000020 — specifically dependent continuant

b is a specifically dependent continuant =Def b is a continuant & there is some independent continuant c which is not a spatial region & which is such that b specifically depends on c

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000002

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000017 rdfs:subClassOf bfo:BFO_0000020`.
- `target_native` / asserted: `bfo:BFO_0000019 rdfs:subClassOf bfo:BFO_0000020`.
- `target_native` / asserted: `bfo:BFO_0000056 rdfs:domain (bfo:BFO_0000020 or bfo:BFO_0000031 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]))`.
- `target_native` / asserted: `bfo:BFO_0000057 rdfs:range (bfo:BFO_0000020 or bfo:BFO_0000031 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]))`.
- `target_native` / asserted: `bfo:BFO_0000058 rdfs:range (bfo:BFO_0000015 or bfo:BFO_0000020)`.
- `target_native` / asserted: `bfo:BFO_0000059 rdfs:domain (bfo:BFO_0000015 or bfo:BFO_0000020)`.
- `target_native` / asserted: `bfo:BFO_0000194 rdfs:domain (bfo:BFO_0000020 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]))`.
- `target_native` / asserted: `bfo:BFO_0000194 rdfs:range bfo:BFO_0000020`.
- `target_native` / asserted: `bfo:BFO_0000195 rdfs:domain bfo:BFO_0000020`.
- `target_native` / asserted: `bfo:BFO_0000195 rdfs:range (bfo:BFO_0000020 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]))`.
- `target_native` / asserted: `bfo:BFO_0000196 rdfs:range bfo:BFO_0000020`.
- `target_native` / asserted: `bfo:BFO_0000197 rdfs:domain bfo:BFO_0000020`.
- `target_native` / asserted: `cco:ont00000395 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000020)))`.
- `target_native` / asserted: `cco:ont00001809 rdfs:domain (bfo:BFO_0000020 or bfo:BFO_0000031)`.
- `target_native` / asserted: `cco:ont00001836 rdfs:range (bfo:BFO_0000020 or bfo:BFO_0000031)`.
- `target_native` / asserted: `owl:AllDisjointClasses owl:members (bfo:BFO_0000004, bfo:BFO_0000020, bfo:BFO_0000031)`.

### bfo:BFO_0000034 — function

(Elucidation) A function is a disposition that exists in virtue of its bearer's physical make-up & this physical make-up is something the bearer possesses because it came into being either through evolution (in the case of natural biological entities) or through intentional design (in the case of artefacts) in order to realize processes of a certain sort

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000016

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000323 rdfs:subClassOf bfo:BFO_0000034`.
- `target_native` / asserted: `cco:ont00000462 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000034)))`.

### bfo:BFO_0000040 — material entity

(Elucidation) A material entity is an independent continuant has some portion of matter as continuant part

owl:disjointWith bfo:BFO_0000141; rdf:type owl:Class; rdfs:subClassOf (bfo:BFO_0000176 owl:allValuesFrom bfo:BFO_0000040); rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom (bfo:BFO_0000029 or bfo:BFO_0000040 or bfo:BFO_0000140)); rdfs:subClassOf bfo:BFO_0000004

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000024 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000027 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000029 rdfs:subClassOf (bfo:BFO_0000176 owl:allValuesFrom (bfo:BFO_0000029 or bfo:BFO_0000040))`.
- `target_native` / asserted: `bfo:BFO_0000030 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000066 rdfs:range (bfo:BFO_0000029 or bfo:BFO_0000040)`.
- `target_native` / asserted: `bfo:BFO_0000115 rdfs:domain bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000115 rdfs:range bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000127 rdfs:domain bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000129 rdfs:domain bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000129 rdfs:range bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000183 rdfs:domain (bfo:BFO_0000029 or bfo:BFO_0000040)`.
- `target_native` / asserted: `bfo:BFO_0000184 rdfs:range bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000185 rdfs:domain bfo:BFO_0000040`.
- `target_native` / asserted: `bfo:BFO_0000218 rdfs:range bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00000544 owl:equivalentClass (bfo:BFO_0000040 and (cco:ont00001936 owl:someValuesFrom cco:ont00000741))`.
- `target_native` / asserted: `cco:ont00000544 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00000556 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00000574 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00000627 owl:equivalentClass (bfo:BFO_0000040 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00001141))`.
- `target_native` / asserted: `cco:ont00000627 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00000870 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00000995 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00001017 owl:equivalentClass (bfo:BFO_0000040 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00001379))`.
- `target_native` / asserted: `cco:ont00001017 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00001168 rdfs:subClassOf bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00001830 rdfs:range bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00001852 rdfs:domain bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00001895 rdfs:domain bfo:BFO_0000040`.
- `target_native` / asserted: `cco:ont00001949 rdfs:range bfo:BFO_0000040`.

### bfo:BFO_0000054 — has realization

b has realization c =Def c realizes b

owl:inverseOf bfo:BFO_0000055; rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000017; rdfs:range bfo:BFO_0000015

### bfo:BFO_0000055 — realizes

(Elucidation) realizes is a relation between a process b and realizable entity c such that c inheres in some d & for all t, if b has participant d then c exists & the type instantiated by b is correlated with the type instantiated by c

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000015; rdfs:range bfo:BFO_0000017

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000054 owl:inverseOf bfo:BFO_0000055`.

### bfo:BFO_0000056 — participates in

(Elucidation) participates in holds between some b that is either a specifically dependent continuant or generically dependent continuant or independent continuant that is not a spatial region & some process p such that b participates in p some way

owl:inverseOf bfo:BFO_0000057; rdf:type owl:ObjectProperty; rdfs:domain (bfo:BFO_0000020 or bfo:BFO_0000031 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class])); rdfs:range bfo:BFO_0000015

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001787 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001816 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001841 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001852 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001886 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001895 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001936 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001978 rdfs:subPropertyOf bfo:BFO_0000056`.
- `target_native` / asserted: `cco:ont00001993 rdfs:subPropertyOf bfo:BFO_0000056`.

### bfo:BFO_0000057 — has participant

p has participant c =Def c participates in p

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000015; rdfs:range (bfo:BFO_0000020 or bfo:BFO_0000031 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]))

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000056 owl:inverseOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00000013 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000101 owl:someValuesFrom bfo:BFO_0000031)))`.
- `target_native` / asserted: `cco:ont00000395 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000020)))`.
- `target_native` / asserted: `cco:ont00000462 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000034)))`.
- `target_native` / asserted: `cco:ont00000609 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000016)))`.
- `target_native` / asserted: `cco:ont00000642 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000017)))`.
- `target_native` / asserted: `cco:ont00001068 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000019)))`.
- `target_native` / asserted: `cco:ont00001194 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000023)))`.
- `target_native` / asserted: `cco:ont00001778 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001830 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001833 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001834 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001844 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001921 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001922 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001949 rdfs:subPropertyOf bfo:BFO_0000057`.
- `target_native` / asserted: `cco:ont00001986 rdfs:subPropertyOf bfo:BFO_0000057`.

### bfo:BFO_0000084 — generically depends on

b generically depends on c =Def b is a generically dependent continuant & c is an independent continuant that is not a spatial region & at some time t there inheres in c a specifically dependent continuant which concretizes b at t

owl:inverseOf bfo:BFO_0000101; rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000031; rdfs:range (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class])

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001837 rdfs:subPropertyOf bfo:BFO_0000084`.
- `target_native` / asserted: `cco:ont00001961 rdfs:subPropertyOf bfo:BFO_0000084`.
- `target_native` / asserted: `cco:ont00001997 rdfs:subPropertyOf bfo:BFO_0000084`.

### bfo:BFO_0000101 — is carrier of

b is carrier of c =Def there is some time t such that c generically depends on b at t

rdf:type owl:ObjectProperty; rdfs:domain (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]); rdfs:range bfo:BFO_0000031

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000084 owl:inverseOf bfo:BFO_0000101`.
- `target_native` / asserted: `cco:ont00000013 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000101 owl:someValuesFrom bfo:BFO_0000031)))`.
- `target_native` / asserted: `cco:ont00000253 owl:equivalentClass (bfo:BFO_0000030 and (bfo:BFO_0000101 owl:someValuesFrom cco:ont00000958))`.
- `target_native` / asserted: `cco:ont00000798 rdfs:subClassOf (bfo:BFO_0000101 owl:someValuesFrom cco:ont00000958)`.
- `target_native` / asserted: `cco:ont00001863 rdfs:subPropertyOf bfo:BFO_0000101`.
- `target_native` / asserted: `cco:ont00001908 rdfs:subPropertyOf bfo:BFO_0000101`.
- `target_native` / asserted: `cco:ont00001912 rdfs:subPropertyOf bfo:BFO_0000101`.

### bfo:BFO_0000117 — has occurrent part

b has occurrent part c =Def c occurrent part of b

owl:inverseOf bfo:BFO_0000132; rdf:type owl:ObjectProperty; rdf:type owl:TransitiveProperty; rdfs:domain bfo:BFO_0000003; rdfs:range bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000015 rdfs:subClassOf (bfo:BFO_0000117 owl:allValuesFrom (bfo:BFO_0000015 or bfo:BFO_0000035))`.
- `target_native` / asserted: `bfo:BFO_0000035 rdfs:subClassOf (bfo:BFO_0000117 owl:allValuesFrom bfo:BFO_0000035)`.
- `target_native` / asserted: `bfo:BFO_0000121 rdfs:subPropertyOf bfo:BFO_0000117`.
- `target_native` / asserted: `cco:ont00001777 rdfs:subPropertyOf bfo:BFO_0000117`.

### bfo:BFO_0000132 — occurrent part of

(Elucidation) occurrent part of is a relation between occurrents b and c when b is part of c

rdf:type owl:ObjectProperty; rdf:type owl:TransitiveProperty; rdfs:domain bfo:BFO_0000003; rdfs:range bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000008 rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom bfo:BFO_0000008)`.
- `target_native` / asserted: `bfo:BFO_0000011 rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom bfo:BFO_0000011)`.
- `target_native` / asserted: `bfo:BFO_0000015 rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom bfo:BFO_0000015)`.
- `target_native` / asserted: `bfo:BFO_0000035 rdfs:subClassOf (bfo:BFO_0000132 owl:allValuesFrom (bfo:BFO_0000015 or bfo:BFO_0000035))`.
- `target_native` / asserted: `bfo:BFO_0000117 owl:inverseOf bfo:BFO_0000132`.
- `target_native` / asserted: `bfo:BFO_0000139 rdfs:subPropertyOf bfo:BFO_0000132`.
- `target_native` / asserted: `cco:ont00000223 rdfs:subClassOf (bfo:BFO_0000132 owl:someValuesFrom cco:ont00000800)`.
- `target_native` / asserted: `cco:ont00000359 rdfs:subClassOf (bfo:BFO_0000132 owl:someValuesFrom cco:ont00000498)`.
- `target_native` / asserted: `cco:ont00000855 rdfs:subClassOf (bfo:BFO_0000132 owl:someValuesFrom cco:ont00000065)`.
- `target_native` / asserted: `cco:ont00001857 rdfs:subPropertyOf bfo:BFO_0000132`.

### bfo:BFO_0000144 — Process Profile

An occurrent that is an occurrent part of some process by virtue of the rate, or pattern, or amplitude of change in an attribute of one or more participants of said process.

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000278 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000503 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000570 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000712 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000752 owl:equivalentClass (bfo:BFO_0000144 and (cco:ont00001857 owl:someValuesFrom cco:ont00000099))`.
- `target_native` / asserted: `cco:ont00000752 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000763 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000772 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000830 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000862 owl:equivalentClass (bfo:BFO_0000144 and (cco:ont00001857 owl:someValuesFrom cco:ont00000675))`.
- `target_native` / asserted: `cco:ont00000862 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00000910 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00001047 rdfs:subClassOf bfo:BFO_0000144`.
- `target_native` / asserted: `cco:ont00001219 rdfs:subClassOf bfo:BFO_0000144`.

### bfo:BFO_0000178 — has continuant part

b has continuant part c =Def c continuant part of b

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000002; rdfs:range bfo:BFO_0000002

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000009 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom (bfo:BFO_0000009 or bfo:BFO_0000018 or bfo:BFO_0000026))`.
- `target_native` / asserted: `bfo:BFO_0000018 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom bfo:BFO_0000018)`.
- `target_native` / asserted: `bfo:BFO_0000026 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom (bfo:BFO_0000018 or bfo:BFO_0000026))`.
- `target_native` / asserted: `bfo:BFO_0000028 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom bfo:BFO_0000006)`.
- `target_native` / asserted: `bfo:BFO_0000029 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom (bfo:BFO_0000029 or bfo:BFO_0000140))`.
- `target_native` / asserted: `bfo:BFO_0000040 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom (bfo:BFO_0000029 or bfo:BFO_0000040 or bfo:BFO_0000140))`.
- `target_native` / asserted: `bfo:BFO_0000115 rdfs:subPropertyOf bfo:BFO_0000178`.
- `target_native` / asserted: `bfo:BFO_0000140 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom bfo:BFO_0000140)`.
- `target_native` / asserted: `bfo:BFO_0000142 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom (bfo:BFO_0000142 or bfo:BFO_0000147))`.
- `target_native` / asserted: `bfo:BFO_0000146 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom bfo:BFO_0000140)`.
- `target_native` / asserted: `bfo:BFO_0000147 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom bfo:BFO_0000147)`.
- `target_native` / asserted: `bfo:BFO_0000176 owl:inverseOf bfo:BFO_0000178`.
- `target_native` / asserted: `cco:ont00000833 rdfs:subClassOf (bfo:BFO_0000178 owl:someValuesFrom cco:ont00000589)`.
- `target_native` / asserted: `cco:ont00000833 rdfs:subClassOf (bfo:BFO_0000178 owl:someValuesFrom cco:ont00000749)`.
- `target_native` / asserted: `cco:ont00000914 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom cco:ont00001262)`.
- `target_native` / asserted: `cco:ont00000914 rdfs:subClassOf (bfo:BFO_0000178 owl:someValuesFrom cco:ont00001262)`.
- `target_native` / asserted: `cco:ont00000974 rdfs:subClassOf (bfo:BFO_0000178 owl:someValuesFrom cco:ont00000476)`.
- `target_native` / asserted: `cco:ont00001125 rdfs:subClassOf (bfo:BFO_0000178 owl:someValuesFrom cco:ont00000500)`.
- `target_native` / asserted: `cco:ont00001239 rdfs:subClassOf (bfo:BFO_0000178 owl:allValuesFrom cco:ont00001180)`.
- `target_native` / asserted: `cco:ont00001239 rdfs:subClassOf (bfo:BFO_0000178 owl:someValuesFrom cco:ont00001180)`.
- `target_native` / asserted: `cco:ont00001855 rdfs:subPropertyOf bfo:BFO_0000178`.

Target-native chains: bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980; cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884

### bfo:BFO_0000194 — specifically depended on by

b specifically depended on by c =Def c specifically depends on b

owl:inverseOf bfo:BFO_0000195; rdf:type owl:ObjectProperty; rdfs:domain (bfo:BFO_0000020 or (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class])); rdfs:range bfo:BFO_0000020

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000196 rdfs:subPropertyOf bfo:BFO_0000194`.

### bfo:BFO_0000196 — bearer of

b bearer of c =Def c inheres in b

owl:inverseOf bfo:BFO_0000197; rdf:type owl:ObjectProperty; rdfs:domain (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]); rdfs:range bfo:BFO_0000020; rdfs:subPropertyOf bfo:BFO_0000194

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000176 owl:equivalentClass (cco:ont00001180 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000898))`.
- `target_native` / asserted: `cco:ont00000348 owl:equivalentClass (cco:ont00000995 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00001999))`.
- `target_native` / asserted: `cco:ont00000388 owl:equivalentClass (cco:ont00001262 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000987))`.
- `target_native` / asserted: `cco:ont00000395 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000020)))`.
- `target_native` / asserted: `cco:ont00000443 owl:equivalentClass (cco:ont00001180 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000485))`.
- `target_native` / asserted: `cco:ont00000462 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000034)))`.
- `target_native` / asserted: `cco:ont00000609 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000016)))`.
- `target_native` / asserted: `cco:ont00000627 owl:equivalentClass (bfo:BFO_0000040 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00001141))`.
- `target_native` / asserted: `cco:ont00000642 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000017)))`.
- `target_native` / asserted: `cco:ont00000645 owl:equivalentClass (cco:ont00001262 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000917))`.
- `target_native` / asserted: `cco:ont00000647 owl:equivalentClass (cco:ont00001262 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000175))`.
- `target_native` / asserted: `cco:ont00000666 owl:equivalentClass (cco:ont00001262 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000486))`.
- `target_native` / asserted: `cco:ont00000697 owl:equivalentClass (cco:ont00001262 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000279))`.
- `target_native` / asserted: `cco:ont00000860 owl:equivalentClass (cco:ont00001262 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000587))`.
- `target_native` / asserted: `cco:ont00001017 owl:equivalentClass (bfo:BFO_0000040 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00001379))`.
- `target_native` / asserted: `cco:ont00001068 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000019)))`.
- `target_native` / asserted: `cco:ont00001194 rdfs:subClassOf (bfo:BFO_0000057 owl:someValuesFrom (bfo:BFO_0000004 and (bfo:BFO_0000196 owl:someValuesFrom bfo:BFO_0000023)))`.
- `target_native` / asserted: `cco:ont00001302 owl:equivalentClass (cco:ont00001180 and (bfo:BFO_0000196 owl:someValuesFrom cco:ont00000173))`.
- `target_native` / asserted: `cco:ont00001954 rdfs:subPropertyOf bfo:BFO_0000196`.

### bfo:BFO_0000197 — inheres in

b inheres in c =Def b is a specifically dependent continuant & c is an independent continuant that is not a spatial region & b specifically depends on c

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000020; rdfs:range (bfo:BFO_0000004 and [owl:complementOf bfo:BFO_0000006; rdf:type owl:Class]); rdfs:subPropertyOf bfo:BFO_0000195

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `bfo:BFO_0000196 owl:inverseOf bfo:BFO_0000197`.
- `target_native` / asserted: `cco:ont00000044 rdfs:subClassOf (bfo:BFO_0000197 owl:someValuesFrom cco:ont00000404)`.
- `target_native` / asserted: `cco:ont00000314 rdfs:subClassOf (bfo:BFO_0000197 owl:someValuesFrom cco:ont00000253)`.
- `target_native` / asserted: `cco:ont00000323 rdfs:subClassOf (bfo:BFO_0000197 owl:someValuesFrom cco:ont00000995)`.
- `target_native` / asserted: `cco:ont00000898 rdfs:subClassOf (bfo:BFO_0000197 owl:someValuesFrom cco:ont00001180)`.
- `target_native` / asserted: `cco:ont00001071 rdfs:subClassOf (bfo:BFO_0000197 owl:someValuesFrom cco:ont00000713)`.
- `target_native` / asserted: `cco:ont00001273 rdfs:subClassOf (bfo:BFO_0000197 owl:someValuesFrom cco:ont00000569)`.
- `target_native` / asserted: `cco:ont00001889 rdfs:subPropertyOf bfo:BFO_0000197`.

### bfo:BFO_0000199 — occupies temporal region

p occupies temporal region t =Def p is a process or process boundary & the spatiotemporal region occupied by p temporally projects onto t

owl:inverseOf cco:ont00001874; rdf:type owl:FunctionalProperty; rdf:type owl:ObjectProperty; rdfs:domain (bfo:BFO_0000015 or bfo:BFO_0000035); rdfs:range bfo:BFO_0000008

### cco:ont00000004 — Change

A Process in which some independent continuant endures and 1) one or more of the dependent entities it bears increase or decrease in intensity, 2) the entity begins to bear some dependent entity or 3) the entity ceases to bear some dependent entity.

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000015

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000554 rdfs:subClassOf cco:ont00000004`.
- `target_native` / asserted: `cco:ont00000644 rdfs:subClassOf cco:ont00000004`.
- `target_native` / asserted: `cco:ont00000726 rdfs:subClassOf cco:ont00000004`.
- `target_native` / asserted: `cco:ont00000876 rdfs:subClassOf cco:ont00000004`.
- `target_native` / asserted: `cco:ont00001048 rdfs:subClassOf cco:ont00000004`.

### cco:ont00000118 — Artifact Function Specification

A Directive Information Content Entity that prescribes some Artifact Function and which is part of some Artifact Model.

owl:equivalentClass (cco:ont00000965 and (cco:ont00001942 owl:someValuesFrom cco:ont00000323)); rdf:type owl:Class; rdfs:subClassOf cco:ont00000965

### cco:ont00000127 — Performance Specification

A Directive Information Content Entity that prescribes some aspect of the behavior of a participant in a Process given one or more operating conditions.

rdf:type owl:Class; rdfs:subClassOf (cco:ont00001980 owl:someValuesFrom bfo:BFO_0000001); rdfs:subClassOf cco:ont00000965

### cco:ont00000177 — Affordance

A Realizable Entity of an Independent Continuant that creates an opportunity for an Agent to realize some Agent Capability or Disposition in some Act.

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000017

### cco:ont00000228 — Planned Act

An Act in which at least one Agent plays a causative role and which is prescribed by some Directive Information Content Entity held by at least one of the Agents.

rdf:type owl:Class; rdfs:subClassOf cco:ont00000005

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000037 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000109 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000142 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000165 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000234 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000345 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000357 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000366 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000371 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000402 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000511 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000566 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000676 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000741 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000908 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00000949 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00001144 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00001147 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00001232 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00001251 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00001314 rdfs:subClassOf cco:ont00000228`.
- `target_native` / asserted: `cco:ont00001327 rdfs:subClassOf cco:ont00000228`.

### cco:ont00000319 — Artifact Design

A Directive Information Content Entity that is a specification of an object, manifested by an agent, intended to accomplish goals, in a particular environment, using a set of primitive components, satisfying a set of requirements, subject to constraints.

rdf:type owl:Class; rdfs:subClassOf (cco:ont00001942 owl:someValuesFrom cco:ont00000995); rdfs:subClassOf cco:ont00000965

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001045 rdfs:subClassOf cco:ont00000319`.

### cco:ont00000503 — Power

A Process Profile that is characterized by the rate of Work, or Energy consumed, done in a given time period.

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000144

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000138 rdfs:subClassOf cco:ont00000503`.

### cco:ont00000592 — Veracity Measurement Information Content Entity

A Measurement Information Content Entity that is a measurement of the extent to which a description conforms to the reality it describes.

rdf:type owl:Class; rdfs:subClassOf cco:ont00001163

### cco:ont00000660 — Effect

A Process that follows and is caused by some previous Process.

owl:equivalentClass (bfo:BFO_0000015 and (cco:ont00001819 owl:someValuesFrom bfo:BFO_0000015)); rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000015

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000855 rdfs:subClassOf cco:ont00000660`.

### cco:ont00000731 — Deviation Measurement Information Content Entity

A Measurement Information Content Entity that is a measurement of the extent to which an entity conforms to how it is expected or supposed to be.

rdf:type owl:Class; rdfs:subClassOf cco:ont00001163

### cco:ont00000853 — Descriptive Information Content Entity

An Information Content Entity that consists of a set of propositions that describe some Entity.

owl:disjointWith cco:ont00000965; rdf:type owl:Class; rdfs:subClassOf cco:ont00000958

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000120 rdfs:subClassOf cco:ont00000853`.
- `target_native` / asserted: `cco:ont00000398 rdfs:subClassOf cco:ont00000853`.
- `target_native` / asserted: `cco:ont00000626 rdfs:subClassOf cco:ont00000853`.
- `target_native` / asserted: `cco:ont00000686 owl:disjointWith cco:ont00000853`.
- `target_native` / asserted: `cco:ont00001163 owl:equivalentClass (cco:ont00000853 and (cco:ont00001966 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00001163 rdfs:subClassOf cco:ont00000853`.
- `target_native` / asserted: `cco:ont00001917 rdfs:range cco:ont00000853`.
- `target_native` / asserted: `cco:ont00001982 rdfs:domain cco:ont00000853`.

### cco:ont00000950 — Act of Maintenance

An Act of Artifact Modification in which an Artifact is modified in order to preserve or restore one or more of its designed Qualities or Functions.

rdf:type owl:Class; rdfs:subClassOf cco:ont00000970

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000783 rdfs:subClassOf (cco:ont00001819 owl:someValuesFrom cco:ont00000950)`.

### cco:ont00000958 — Information Content Entity

A Generically Dependent Continuant that generically depends on some Information Bearing Entity and stands in relation of aboutness to some Entity.

owl:equivalentClass (bfo:BFO_0000031 and (cco:ont00001808 owl:someValuesFrom bfo:BFO_0000001)); rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000031

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000253 owl:equivalentClass (bfo:BFO_0000030 and (bfo:BFO_0000101 owl:someValuesFrom cco:ont00000958))`.
- `target_native` / asserted: `cco:ont00000616 rdfs:subClassOf cco:ont00000958`.
- `target_native` / asserted: `cco:ont00000686 owl:equivalentClass (cco:ont00000958 and (cco:ont00001916 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00000686 rdfs:subClassOf cco:ont00000958`.
- `target_native` / asserted: `cco:ont00000696 rdfs:subClassOf cco:ont00000958`.
- `target_native` / asserted: `cco:ont00000798 rdfs:subClassOf (bfo:BFO_0000101 owl:someValuesFrom cco:ont00000958)`.
- `target_native` / asserted: `cco:ont00000853 rdfs:subClassOf cco:ont00000958`.
- `target_native` / asserted: `cco:ont00000965 owl:equivalentClass (cco:ont00000958 and (cco:ont00001942 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00000965 rdfs:subClassOf cco:ont00000958`.
- `target_native` / asserted: `cco:ont00001069 owl:equivalentClass (cco:ont00000958 and (cco:ont00001938 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00001069 rdfs:subClassOf cco:ont00000958`.
- `target_native` / asserted: `cco:ont00001801 rdfs:range cco:ont00000958`.
- `target_native` / asserted: `cco:ont00001808 rdfs:domain cco:ont00000958`.

### cco:ont00000965 — Directive Information Content Entity

An Information Content Entity that consists of a set of propositions or images (as in the case of a blueprint) that prescribe some Entity.

owl:equivalentClass (cco:ont00000958 and (cco:ont00001942 owl:someValuesFrom bfo:BFO_0000001)); rdf:type owl:Class; rdfs:subClassOf cco:ont00000958

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000118 owl:equivalentClass (cco:ont00000965 and (cco:ont00001942 owl:someValuesFrom cco:ont00000323))`.
- `target_native` / asserted: `cco:ont00000118 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000127 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000319 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000476 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000575 owl:equivalentClass (cco:ont00000965 and (cco:ont00001942 owl:someValuesFrom bfo:BFO_0000019))`.
- `target_native` / asserted: `cco:ont00000575 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000653 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000686 owl:disjointWith cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000853 owl:disjointWith cco:ont00000965`.
- `target_native` / asserted: `cco:ont00000974 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00001175 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00001324 rdfs:subClassOf cco:ont00000965`.
- `target_native` / asserted: `cco:ont00001920 rdfs:range cco:ont00000965`.
- `target_native` / asserted: `cco:ont00001942 rdfs:domain cco:ont00000965`.

### cco:ont00000978 — Cause

A Process that is the cause of or one of the causes of some other Process.

owl:equivalentClass (bfo:BFO_0000015 and (cco:ont00001803 owl:someValuesFrom bfo:BFO_0000015)); rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000015

### cco:ont00001022 — Ratio Measurement Information Content Entity

A Measurement Information Content Entity that consists of a symbol that places a Quality of an Entity onto an interval scale having a true zero value.

owl:disjointWith cco:ont00001364; owl:equivalentClass (cco:ont00001163 and (cco:ont00001983 owl:someValuesFrom bfo:BFO_0000001)); rdf:type owl:Class; rdfs:subClassOf cco:ont00001163

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000293 owl:disjointWith cco:ont00001022`.
- `target_native` / asserted: `cco:ont00000539 rdfs:subClassOf cco:ont00001022`.
- `target_native` / asserted: `cco:ont00000669 rdfs:subClassOf cco:ont00001022`.
- `target_native` / asserted: `cco:ont00000845 rdfs:subClassOf cco:ont00001022`.
- `target_native` / asserted: `cco:ont00001010 owl:disjointWith cco:ont00001022`.
- `target_native` / asserted: `cco:ont00001965 rdfs:range cco:ont00001022`.
- `target_native` / asserted: `cco:ont00001983 rdfs:domain cco:ont00001022`.

### cco:ont00001047 — Frequency

A Process Profile that is characterized by the number of repetitive processes during a particular time period.

rdf:type owl:Class; rdfs:subClassOf bfo:BFO_0000144

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000008 rdfs:subClassOf cco:ont00001047`.
- `target_native` / asserted: `cco:ont00000754 rdfs:subClassOf cco:ont00001047`.

### cco:ont00001213 — Stasis of Artifact Operationality

A Stasis of Realizable Entity that holds during a Temporal Interval when an Artifact's designed set of Artifact Functions (or at least its primary functions) or the realizations of those functions remain unchanged.

rdf:type owl:Class; rdfs:subClassOf cco:ont00000246

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000106 rdfs:subClassOf cco:ont00001213`.
- `target_native` / asserted: `cco:ont00000847 rdfs:subClassOf cco:ont00001213`.
- `target_native` / asserted: `cco:ont00000936 rdfs:subClassOf cco:ont00001213`.
- `target_native` / asserted: `cco:ont00000999 rdfs:subClassOf cco:ont00001213`.
- `target_native` / asserted: `cco:ont00001191 rdfs:subClassOf cco:ont00001213`.

### cco:ont00001256 — Reliability Measurement Information Content Entity

A Measurement Information Content Entity that is a measurement of the extent to which an entity can consistently produce an outcome.

rdf:type owl:Class; rdfs:subClassOf cco:ont00001163

### cco:ont00001777 — has process part

x has_process_part y iff x and y are instances of Process, such that y occurs during the temporal interval of x, and y either provides an input to x or receives an output of x, or both.

owl:inverseOf cco:ont00001857; rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000015; rdfs:range bfo:BFO_0000015; rdfs:subPropertyOf bfo:BFO_0000117

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000099 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000752)`.
- `target_native` / asserted: `cco:ont00000368 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000296)`.
- `target_native` / asserted: `cco:ont00000675 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00001227)`.
- `target_native` / asserted: `cco:ont00000712 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000763)`.
- `target_native` / asserted: `cco:ont00000789 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000763)`.
- `target_native` / asserted: `cco:ont00000889 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000558)`.
- `target_native` / asserted: `cco:ont00000951 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000514)`.
- `target_native` / asserted: `cco:ont00000983 owl:equivalentClass (cco:ont00001028 and (cco:ont00001777 owl:someValuesFrom cco:ont00000514))`.
- `target_native` / asserted: `cco:ont00001219 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000763)`.
- `target_native` / asserted: `cco:ont00001246 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000566)`.
- `target_native` / asserted: `cco:ont00001330 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000345)`.
- `target_native` / asserted: `cco:ont00001330 rdfs:subClassOf (cco:ont00001777 owl:someValuesFrom cco:ont00000517)`.

### cco:ont00001787 — agent in

x agent_in y iff y is an instance of Process and x is an instance of Agent, such that x is causally active in y.

owl:inverseOf cco:ont00001833; rdf:type owl:ObjectProperty; rdfs:subPropertyOf bfo:BFO_0000056

### cco:ont00001801 — is subject of

A primitive relationship between an instance of an Entity and an instance of an Information Content Entity.

owl:inverseOf cco:ont00001808; rdf:type owl:ObjectProperty; rdfs:range cco:ont00000958

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001873 rdfs:subPropertyOf cco:ont00001801`.
- `target_native` / asserted: `cco:ont00001879 rdfs:subPropertyOf cco:ont00001801`.
- `target_native` / asserted: `cco:ont00001884 rdfs:subPropertyOf cco:ont00001801`.
- `target_native` / asserted: `cco:ont00001917 rdfs:subPropertyOf cco:ont00001801`.
- `target_native` / asserted: `cco:ont00001920 rdfs:subPropertyOf cco:ont00001801`.

### cco:ont00001803 — is cause of

x is_cause_of y iff x and y are instances of Occurrent, and y is a consequence of x.

owl:inverseOf cco:ont00001819; rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000003; rdfs:range bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000191 rdfs:subClassOf (cco:ont00001803 owl:someValuesFrom cco:ont00000920)`.
- `target_native` / asserted: `cco:ont00000978 owl:equivalentClass (bfo:BFO_0000015 and (cco:ont00001803 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00001236 rdfs:subClassOf (cco:ont00001803 owl:someValuesFrom cco:ont00000920)`.
- `target_native` / asserted: `cco:ont00001933 rdfs:subPropertyOf cco:ont00001803`.

### cco:ont00001808 — is about

A primitive relationship between an Information Content Entity and some Entity.

rdf:type owl:ObjectProperty; rdfs:domain cco:ont00000958; rdfs:range bfo:BFO_0000001

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000958 owl:equivalentClass (bfo:BFO_0000031 and (cco:ont00001808 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00001801 owl:inverseOf cco:ont00001808`.
- `target_native` / asserted: `cco:ont00001916 rdfs:subPropertyOf cco:ont00001808`.
- `target_native` / asserted: `cco:ont00001938 rdfs:subPropertyOf cco:ont00001808`.
- `target_native` / asserted: `cco:ont00001942 rdfs:subPropertyOf cco:ont00001808`.
- `target_native` / asserted: `cco:ont00001980 rdfs:subPropertyOf cco:ont00001808`.
- `target_native` / asserted: `cco:ont00001982 rdfs:subPropertyOf cco:ont00001808`.

### cco:ont00001816 — is output of

x is_output_of y iff x is an instance of Continuant and y is an instance of Process, such that the presence of x at the end of y is a necessary condition for the completion of y.

owl:inverseOf cco:ont00001986; rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000002; rdfs:range bfo:BFO_0000015; rdfs:subPropertyOf bfo:BFO_0000056

### cco:ont00001819 — caused by

x caused_by y iff x and y are instances of Occurrent, and x is a consequence of y.

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000003; rdfs:range bfo:BFO_0000003

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000660 owl:equivalentClass (bfo:BFO_0000015 and (cco:ont00001819 owl:someValuesFrom bfo:BFO_0000015))`.
- `target_native` / asserted: `cco:ont00000783 rdfs:subClassOf (cco:ont00001819 owl:someValuesFrom cco:ont00000950)`.
- `target_native` / asserted: `cco:ont00000855 rdfs:subClassOf (cco:ont00001819 owl:someValuesFrom cco:ont00000065)`.
- `target_native` / asserted: `cco:ont00001803 owl:inverseOf cco:ont00001819`.
- `target_native` / asserted: `cco:ont00001962 rdfs:subPropertyOf cco:ont00001819`.

### cco:ont00001833 — has agent

x has_agent y iff x is an instance of Process and y is an instance of Agent, such that y is causally active in x.

rdf:type owl:ObjectProperty; rdfs:subPropertyOf bfo:BFO_0000057

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001787 owl:inverseOf cco:ont00001833`.

### cco:ont00001834 — affects

x affects y iff x is an instance of Process and y is an instance of Continuant, and x influences y in some manner, most often by producing a change in y.

owl:inverseOf cco:ont00001886; rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000015; rdfs:range bfo:BFO_0000002; rdfs:subPropertyOf bfo:BFO_0000057

### cco:ont00001873 — represented by

y represented_by x iff x is an instance of Information Content Entity, and y is an instance of Entity, and z is carrier of x, such that x is about y in virtue of there existing an isomorphism between characteristics of z and y.

owl:inverseOf cco:ont00001938; rdf:type owl:ObjectProperty; rdfs:range cco:ont00001069; rdfs:subPropertyOf cco:ont00001801

### cco:ont00001884 — condition described by

c condition_described_by p iff p is an instance of a Performance Specification, and p has part d, and d is an instance of a Descriptive Information Content Entity, and p prescribes an entity s, and d describes c, and c is an entity that is causally relevant to s existing as prescribed by p.

owl:inverseOf cco:ont00001980; rdf:type owl:ObjectProperty; rdfs:subPropertyOf cco:ont00001801

Target-native chains: bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980; cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884

### cco:ont00001886 — is affected by

x is_affected_by y iff x is an instance of Continuant and y is an instance of Process, and y influences x in some manner, most often by producing a change in x.

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000002; rdfs:range bfo:BFO_0000015; rdfs:subPropertyOf bfo:BFO_0000056

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001834 owl:inverseOf cco:ont00001886`.

### cco:ont00001904 — is measured by

y is_measured_by x iff x is an instance of Information Content Entity and y is an instance of Entity, such that x describes some attribute of y relative to some scale or classification scheme.

owl:inverseOf cco:ont00001966; rdf:type owl:ObjectProperty; rdfs:range cco:ont00001163; rdfs:subPropertyOf cco:ont00001917

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001914 rdfs:subPropertyOf cco:ont00001904`.
- `target_native` / asserted: `cco:ont00001963 rdfs:subPropertyOf cco:ont00001904`.
- `target_native` / asserted: `cco:ont00001964 rdfs:subPropertyOf cco:ont00001904`.
- `target_native` / asserted: `cco:ont00001965 rdfs:subPropertyOf cco:ont00001904`.

Target-native chains: bfo:BFO_0000178 o cco:ont00001982 -> cco:ont00001980; cco:ont00001917 o bfo:BFO_0000176 -> cco:ont00001884

### cco:ont00001920 — prescribed by

x prescribed_by y iff y is an instance of Information Content Entity and x is an instance of Entity, such that y serves as a rule or guide for x if x is an Occurrent, or y serves as a model for x if x is a Continuant.

owl:inverseOf cco:ont00001942; rdf:type owl:ObjectProperty; rdfs:range cco:ont00000965; rdfs:subPropertyOf cco:ont00001801

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001807 rdfs:subPropertyOf cco:ont00001920`.
- `target_native` / asserted: `cco:ont00001817 rdfs:subPropertyOf cco:ont00001920`.
- `target_native` / asserted: `cco:ont00001976 rdfs:subPropertyOf cco:ont00001920`.
- `target_native` / asserted: `cco:ont00001998 rdfs:subPropertyOf cco:ont00001920`.

### cco:ont00001936 — is object of

If p is a process and c is a continuant, then c is object of p if and only if the c is part of the projected state that the agent intends to achieve by performing p.

rdf:type owl:ObjectProperty; rdfs:subPropertyOf bfo:BFO_0000056

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000544 owl:equivalentClass (bfo:BFO_0000040 and (cco:ont00001936 owl:someValuesFrom cco:ont00000741))`.
- `target_native` / asserted: `cco:ont00001778 owl:inverseOf cco:ont00001936`.

### cco:ont00001938 — represents

x represents y iff x is an instance of Information Content Entity, y is an instance of Entity, and z is carrier of x, such that x is about y in virtue of there existing an isomorphism between characteristics of z and y.

rdf:type owl:ObjectProperty; rdfs:domain cco:ont00001069; rdfs:subPropertyOf cco:ont00001808

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001069 owl:equivalentClass (cco:ont00000958 and (cco:ont00001938 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00001873 owl:inverseOf cco:ont00001938`.

### cco:ont00001942 — prescribes

x prescribes y iff x is an instance of Information Content Entity and y is an instance of Entity, such that x serves as a rule or guide for y if y an Occurrent, or x serves as a model for y if y is a Continuant.

rdf:type owl:ObjectProperty; rdfs:domain cco:ont00000965; rdfs:subPropertyOf cco:ont00001808

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00000118 owl:equivalentClass (cco:ont00000965 and (cco:ont00001942 owl:someValuesFrom cco:ont00000323))`.
- `target_native` / asserted: `cco:ont00000319 rdfs:subClassOf (cco:ont00001942 owl:someValuesFrom cco:ont00000995)`.
- `target_native` / asserted: `cco:ont00000575 owl:equivalentClass (cco:ont00000965 and (cco:ont00001942 owl:someValuesFrom bfo:BFO_0000019))`.
- `target_native` / asserted: `cco:ont00000965 owl:equivalentClass (cco:ont00000958 and (cco:ont00001942 owl:someValuesFrom bfo:BFO_0000001))`.
- `target_native` / asserted: `cco:ont00001800 rdfs:subPropertyOf cco:ont00001942`.
- `target_native` / asserted: `cco:ont00001899 rdfs:subPropertyOf cco:ont00001942`.
- `target_native` / asserted: `cco:ont00001910 rdfs:subPropertyOf cco:ont00001942`.
- `target_native` / asserted: `cco:ont00001920 owl:inverseOf cco:ont00001942`.
- `target_native` / asserted: `cco:ont00001974 rdfs:subPropertyOf cco:ont00001942`.

### cco:ont00001962 — process started by

x process_started_by y iff x and y are instances of processes, and x is caused_by y, and i is an instance of a temporal instant, and r is an instant of a temporal interval, and x has starting instance i, and y occurs on r, and r interval contains i.

rdf:type owl:ObjectProperty; rdfs:subPropertyOf cco:ont00001819

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001933 owl:inverseOf cco:ont00001962`.

### cco:ont00001986 — has output

y has_output x iff x is an instance of Continuant and y is an instance of Process, such that the presence of x at the end of y is a necessary condition for the completion of y.

rdf:type owl:ObjectProperty; rdfs:domain bfo:BFO_0000015; rdfs:range bfo:BFO_0000002; rdfs:subPropertyOf bfo:BFO_0000057

Asserted context (actual axiom subject and direction retained):
- `target_native` / asserted: `cco:ont00001816 owl:inverseOf cco:ont00001986`.
