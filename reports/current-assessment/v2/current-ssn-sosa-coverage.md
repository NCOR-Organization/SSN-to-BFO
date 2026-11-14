# Current SSN/SOSA assessment and formal coverage

Bound to authenticated content SHA-256 `fe5566eb8ad96d0581cdb92c03abd53e79af59573a86f92bd1388fd2059f7ba7` and exact input hashes in the JSON companion. This reproducible report is independent of the commit that stores it; execution receipts retain their own HEAD provenance.

Structural evidence over named source subclass/subproperty, named equivalence, and inverse paths plus governed direct mappings; chain heads and separately executed conditional query routes. Overlaps retained. No established route means none in this bounded method, not a complete OWL non-entailment proof. Domain/range alone never supplies relation coverage.

## Inventory and assessment

Dynamic source terms: **91**; assessment records: **91**; equality: **PASS**.

Kinds: `{'class': 44, 'object_property': 47}`. Review states: `{'deferred': 0, 'final': 21, 'unreviewed': 70}`. Outcomes: `{'deferred': 0, 'formal_mapping_adopted': 14, 'inheritance_sufficient': 2, 'no_direct_mapping': 5, 'unreviewed': 70}`.

These assessments describe unchanged workbook mapping assertions; registered documentary reasoning updates do not change assessment semantics. Final records reconstruct supported existing decisions; unresolved records do not reject or remove active axioms.

## Formal coverage

| Category | Terms |
|---|---:|
| direct_formal_mapping | 66 |
| inherited_formal_mapping | 41 |
| rule_or_chain_route | 11 |
| typing_only_in_workbook | 16 |
| explicit_blank | 7 |
| no_established_formal_route | 15 |

Direct classes: 42; direct object properties: 24; chain heads: 2. The historical 28 relation-mapped properties comprise 25 direct subproperties and 3 chain heads. A chain head is an incoming entailment route, not a source-to-target edge inclusion.

Categories overlap: a directly mapped class can inherit additional constraints; a typing-only workbook property can be eligible for a separate conditional query. The query is not executed by the OWL product, and eligibility does not prove every assertion has suitable typing. Inherited coverage does not assert that inheritance is a sufficient final assessment outcome.

## Mapping repertoire (rows)

| Predicate | Rows |
|---|---:|
| `explicit_blank` | 7 |
| `owl:equivalentClass` | 10 |
| `owl:equivalentProperty` | 0 |
| `owl:propertyChainAxiom` | 2 |
| `rdfs:domain` | 17 |
| `rdfs:range` | 15 |
| `rdfs:subClassOf` | 32 |
| `rdfs:subPropertyOf` | 24 |

Expression occurrences: `{'intersection': 86, 'named': 191, 'some': 96, 'union': 15}`; rows containing each form: `{'intersection': 35, 'named': 74, 'some': 35, 'union': 14}`.

## Per-term coverage

| Source | Direct | Inherited | Rule/chain | Typing-only artifact | No established route |
|---|---|---|---|---|---|
| `sosa:ActuatableProperty` | yes | yes | — | — | — |
| `sosa:Actuation` | yes | — | — | — | — |
| `sosa:Actuator` | yes | yes | — | — | — |
| `sosa:FeatureOfInterest` | yes | — | — | — | — |
| `sosa:ObservableProperty` | yes | yes | — | — | — |
| `sosa:Observation` | yes | — | — | — | — |
| `sosa:Platform` | yes | — | — | — | — |
| `sosa:Procedure` | yes | — | — | — | — |
| `sosa:Result` | yes | — | — | — | — |
| `sosa:Sample` | yes | yes | — | — | — |
| `sosa:Sampler` | yes | yes | — | — | — |
| `sosa:Sampling` | yes | — | — | — | — |
| `sosa:Sensor` | yes | yes | — | — | — |
| `sosa:actsOnProperty` | yes | yes | — | — | — |
| `sosa:hasFeatureOfInterest` | — | — | — | yes | yes |
| `sosa:hasResult` | yes | yes | — | — | — |
| `sosa:hasSample` | — | — | — | — | yes |
| `sosa:hosts` | — | — | yes | — | — |
| `sosa:isActedOnBy` | yes | yes | — | — | — |
| `sosa:isFeatureOfInterestOf` | — | — | — | yes | yes |
| `sosa:isHostedBy` | — | — | yes | — | — |
| `sosa:isObservedBy` | — | — | — | yes | yes |
| `sosa:isResultOf` | yes | yes | — | — | — |
| `sosa:isSampleOf` | — | — | — | — | yes |
| `sosa:madeActuation` | — | — | — | yes | yes |
| `sosa:madeByActuator` | — | — | — | yes | yes |
| `sosa:madeBySampler` | yes | yes | — | — | — |
| `sosa:madeBySensor` | yes | yes | — | — | — |
| `sosa:madeObservation` | yes | yes | — | — | — |
| `sosa:madeSampling` | yes | yes | — | — | — |
| `sosa:observedProperty` | — | — | — | — | yes |
| `sosa:observes` | — | — | — | yes | yes |
| `sosa:phenomenonTime` | yes | — | — | — | — |
| `sampling:RelationshipNature` | yes | — | — | — | — |
| `sampling:SampleRelationship` | yes | — | — | — | — |
| `sampling:hasSampleRelationship` | yes | — | — | — | — |
| `sampling:natureOfRelationship` | yes | — | — | — | — |
| `sampling:relatedSample` | yes | — | — | — | — |
| `sosa:usedProcedure` | yes | — | — | — | — |
| `ssn:Deployment` | yes | — | — | — | — |
| `ssn:Input` | yes | — | — | — | — |
| `ssn:Output` | yes | — | — | — | — |
| `ssn:Property` | yes | — | — | — | — |
| `ssn:Stimulus` | yes | — | — | — | — |
| `ssn:System` | yes | — | — | — | — |
| `ssn:deployedOnPlatform` | yes | yes | — | — | — |
| `ssn:deployedSystem` | yes | yes | — | — | — |
| `ssn:detects` | yes | — | — | — | — |
| `ssn:forProperty` | — | — | — | — | yes |
| `ssn:hasDeployment` | yes | yes | — | — | — |
| `ssn:hasInput` | — | — | — | yes | yes |
| `ssn:hasOutput` | — | — | — | yes | yes |
| `ssn:hasProperty` | — | — | yes | yes | — |
| `ssn:hasSubSystem` | yes | — | — | — | — |
| `ssn:implementedBy` | — | — | yes | — | — |
| `ssn:implements` | — | — | yes | yes | — |
| `ssn:inDeployment` | yes | yes | — | — | — |
| `ssn:isPropertyOf` | — | — | — | yes | yes |
| `ssn:isProxyFor` | — | — | — | yes | yes |
| `ssn-system:Accuracy` | yes | yes | — | — | — |
| `ssn-system:ActuationRange` | yes | yes | — | — | — |
| `ssn-system:BatteryLifetime` | yes | yes | — | — | — |
| `ssn-system:Condition` | yes | yes | — | — | — |
| `ssn-system:DetectionLimit` | yes | yes | — | — | — |
| `ssn-system:Drift` | yes | yes | — | — | — |
| `ssn-system:Frequency` | yes | yes | — | — | — |
| `ssn-system:Latency` | yes | yes | — | — | — |
| `ssn-system:MaintenanceSchedule` | yes | yes | — | — | — |
| `ssn-system:MeasurementRange` | — | yes | — | — | — |
| `ssn-system:OperatingPowerRange` | yes | yes | — | — | — |
| `ssn-system:OperatingProperty` | yes | yes | — | — | — |
| `ssn-system:OperatingRange` | yes | yes | — | — | — |
| `ssn-system:Precision` | yes | yes | — | — | — |
| `ssn-system:Resolution` | yes | yes | — | — | — |
| `ssn-system:ResponseTime` | yes | yes | — | — | — |
| `ssn-system:Selectivity` | yes | yes | — | — | — |
| `ssn-system:Sensitivity` | yes | yes | — | — | — |
| `ssn-system:SurvivalProperty` | yes | yes | — | — | — |
| `ssn-system:SurvivalRange` | yes | yes | — | — | — |
| `ssn-system:SystemCapability` | yes | yes | — | — | — |
| `ssn-system:SystemLifetime` | yes | yes | — | — | — |
| `ssn-system:SystemProperty` | — | yes | — | — | — |
| `ssn-system:hasOperatingProperty` | yes | — | yes | — | — |
| `ssn-system:hasOperatingRange` | — | — | yes | yes | — |
| `ssn-system:hasSurvivalProperty` | yes | — | yes | — | — |
| `ssn-system:hasSurvivalRange` | — | — | yes | yes | — |
| `ssn-system:hasSystemCapability` | — | — | yes | yes | — |
| `ssn-system:hasSystemProperty` | yes | — | yes | — | — |
| `ssn-system:inCondition` | — | — | — | yes | yes |
| `ssn-system:qualityOfObservation` | yes | — | — | — | — |
| `ssn:wasOriginatedBy` | yes | — | — | — | — |
