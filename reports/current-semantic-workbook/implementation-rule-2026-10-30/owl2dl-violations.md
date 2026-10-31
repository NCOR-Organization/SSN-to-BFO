# Original implementation-chain OWL 2 DL violations

The exact historical implementation candidate was reconstructed on 2026-10-30 against the current complete available pinned local closure, including the restored sensor mappings. This is a structural diagnosis of an authorized historical implementation, not a new semantic adjudication.

The fresh [candidate mapping](historical-chain/mapping.ttl), [mapping delta](historical-chain/rdf-delta.json), [validation result](historical-chain/validation-result.json), and [unaltered validator output](historical-chain/profile-output.txt) are retained. The earlier recovery's validator result is separately retained in [prior-chain-validation-result.json](prior-chain-validation-result.json).

## Reproduction and scope

From the repository root, run the same profile check on the retained input:

```sh
/usr/local/bin/robot validate-profile --profile DL --input reports/current-semantic-workbook/implementation-rule-2026-10-30/historical-chain/validation/coms-candidate-full-closure-owl2dl-profile.ttl
```

The expected result for this historical candidate is exit status **1**, with the seven diagnostics below. Diagnostic enumeration/order is a presentation detail; the full diagnostic set is what must match.

The fresh mapping has 1,070 RDF triples. The assembled local closure has 15,860 triples; its profile-check copy has 15,864. The established validation tool copies every closure triple and adds only these four declarations:

```turtle
<http://purl.org/dc/terms/issued> a <http://www.w3.org/2002/07/owl#AnnotationProperty> .
<http://purl.org/dc/terms/type> a <http://www.w3.org/2002/07/owl#AnnotationProperty> .
<http://www.w3.org/2004/02/skos/core#Concept> a <http://www.w3.org/2002/07/owl#Class> .
<http://www.w3.org/ns/adms#status> a <http://www.w3.org/2002/07/owl#AnnotationProperty> .
```

An RDF graph-isomorphism comparison confirms zero removals and exactly those four additions between the retained closure and profile copy. These metadata-vocabulary declarations do not remove or weaken source restrictions. The local closure assembly removes import directives after loading the available pinned dependencies, while retaining source logical axioms, including sample-property functionality/inverse-functionality. No source minimum cardinality or property chain was removed.

The profile gate failed before HermiT. `return_code` and `owl_nothing_count` are null and `reasoned_output_produced` is false. The empty `unsat_classes` array does **not** establish satisfiability. These seven failures establish that this candidate is outside OWL 2 DL; they do not establish logical inconsistency or unsatisfiable classes. The earlier candidate had 15,859/15,863 triples because it preceded the coordinated sensor restoration; its output is historical evidence, not the fresh execution.

## Applicable W3C provisions

[OWL 2 Structural Specification, Section 11.1](https://www.w3.org/TR/owl2-syntax/#Property_Hierarchy_and_Simple_Object_Property_Expressions) defines composite properties, the inverse-aware property hierarchy, and simple properties. A chain head is composite; a property with a composite predecessor in that hierarchy is not simple.

[Section 11.2](https://www.w3.org/TR/owl2-syntax/#The_Restrictions_on_the_Axiom_Closure), **Restriction on Simple Roles**, requires simple properties in `ObjectMinCardinality`. Its **Restriction on the Property Hierarchy** requires a strict partial order compatible with the hierarchy and the permitted forms of chain axioms. Neither the transitivity exception nor permitted endpoint recursion applies to the distinct operands and heads here.

The following axiom-level derivations apply those provisions to the repository's actual axioms. They do not treat every property cycle as illegal: the exact hierarchy dependencies matter.

## Seven actual violations

The entries follow the order of the fresh retained validator output. Each diagnostic below is copied verbatim, including its containing axiom and ontology identifier. Full IRIs are expanded in each standalone axiom.

### 1. Sampler minimum cardinality

```text
SubClassOf(
  <http://www.w3.org/ns/sosa/Sampler>
  ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> <http://www.w3.org/2002/07/owl#Thing>)
)
```

Source: `imports/ssn.ttl:560–563` (property at line 561). This is a source-native restriction, not generated from a workbook row.

Restriction and dependency: Section 11.2, Restriction on Simple Roles. The restored chain and source inverse make `ssn:implements` non-simple through the common simplicity dependency explained below. The unchanged Sampler cardinality then becomes impermissible.

Actual diagnostic:

```text
Use of non-simple property in a restriction: ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> owl:Thing) [SubClassOf(<http://www.w3.org/ns/sosa/Sampler> ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> owl:Thing)) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

### 2. Actuator minimum cardinality

```text
SubClassOf(
  <http://www.w3.org/ns/sosa/Actuator>
  ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> <http://www.w3.org/2002/07/owl#Thing>)
)
```

Source: `imports/ssn.ttl:397–400` (property at line 398). Source-native; no workbook row creates this restriction.

Restriction and dependency: Section 11.2, Restriction on Simple Roles. The same restored-chain/inverse dependency makes `ssn:implements` non-simple in the unchanged Actuator cardinality.

Actual diagnostic:

```text
Use of non-simple property in a restriction: ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> owl:Thing) [SubClassOf(<http://www.w3.org/ns/sosa/Actuator> ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> owl:Thing)) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

### 3. Sensor minimum cardinality

```text
SubClassOf(
  <http://www.w3.org/ns/sosa/Sensor>
  ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> <http://www.w3.org/2002/07/owl#Thing>)
)
```

Source: `imports/ssn.ttl:618–621` (property at line 619). Source-native; no workbook row creates this restriction.

Restriction and dependency: Section 11.2, Restriction on Simple Roles. The same restored-chain/inverse dependency makes `ssn:implements` non-simple in the unchanged Sensor cardinality.

Actual diagnostic:

```text
Use of non-simple property in a restriction: ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> owl:Thing) [SubClassOf(<http://www.w3.org/ns/sosa/Sensor> ObjectMinCardinality(1 <http://www.w3.org/ns/ssn/implements> owl:Thing)) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

### 4. Sensor usedProcedure chain

```text
SubObjectPropertyOf(
  ObjectPropertyChain(<http://www.w3.org/ns/sosa/madeBySensor> <http://www.w3.org/ns/ssn/implements>)
  <http://www.w3.org/ns/sosa/usedProcedure>
)
```

Source: `imports/ssn.ttl:181–183`. This chain is source-native; no workbook row creates it. Its mapped dependency `usedProcedure subPropertyOf prescribed_by` is Sheet2!12, RowID `urn:uuid:377fa547-ff5c-4ffa-af6f-40d291ab2ab9`.

Restriction and dependency: Section 11.2, Restriction on the Property Hierarchy. This is the Sensor instance of the precise `Q -> J -> U -> Q` dependency cycle derived below. The checker identifies the `implements` operand, not the `madeBySensor` operand.

Actual diagnostic:

```text
Use of property in chain causes cycle: <http://www.w3.org/ns/ssn/implements> [SubObjectPropertyOf(ObjectPropertyChain(<http://www.w3.org/ns/sosa/madeBySensor> <http://www.w3.org/ns/ssn/implements>) <http://www.w3.org/ns/sosa/usedProcedure>) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

### 5. Historical implementedBy chain

```text
SubObjectPropertyOf(
  ObjectPropertyChain(<https://www.commoncoreontologies.org/ont00001942> <https://www.commoncoreontologies.org/ont00001833>)
  <http://www.w3.org/ns/ssn/implementedBy>
)
```

Source: Fresh reconstructed candidate `historical-chain/mapping.ttl:124`. Historical commit `b464cea20bae6d6c542ec1db459cc76b6b978beb`, workbook `Current_SOSA-SSN to BFO-CCO.xlsx`, Common OPs row 16. The current COMS row associated with replacement of the superseding direct mapping is Sheet2!57, RowID `urn:uuid:4afaf231-5478-4a50-9a12-0cbf59d78d7e`; the historical chain was never installed in that current row. The workbook locations are documented in `reports/all-mapping-changes-and-rationales.md:152`.

Restriction and dependency: Section 11.2, Restriction on the Property Hierarchy. This common historical chain participates in all three source-chain cycles below. The checker identifies `ont00001942` (prescribes). This is also the chain that creates the composite/non-simple head responsible for violations 1–3.

Actual diagnostic:

```text
Use of property in chain causes cycle: <https://www.commoncoreontologies.org/ont00001942> [SubObjectPropertyOf(ObjectPropertyChain(<https://www.commoncoreontologies.org/ont00001942> <https://www.commoncoreontologies.org/ont00001833>) <http://www.w3.org/ns/ssn/implementedBy>) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

### 6. Actuator usedProcedure chain

```text
SubObjectPropertyOf(
  ObjectPropertyChain(<http://www.w3.org/ns/sosa/madeByActuator> <http://www.w3.org/ns/ssn/implements>)
  <http://www.w3.org/ns/sosa/usedProcedure>
)
```

Source: `imports/ssn.ttl:175–177`. Source-native; no workbook row creates the chain. The relevant mapped dependency is Sheet2!12, RowID `urn:uuid:377fa547-ff5c-4ffa-af6f-40d291ab2ab9`.

Restriction and dependency: Section 11.2, Restriction on the Property Hierarchy. This is the Actuator instance of `Q -> J -> U -> Q`. The checker identifies the `implements` operand.

Actual diagnostic:

```text
Use of property in chain causes cycle: <http://www.w3.org/ns/ssn/implements> [SubObjectPropertyOf(ObjectPropertyChain(<http://www.w3.org/ns/sosa/madeByActuator> <http://www.w3.org/ns/ssn/implements>) <http://www.w3.org/ns/sosa/usedProcedure>) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

### 7. Sampler usedProcedure chain

```text
SubObjectPropertyOf(
  ObjectPropertyChain(<http://www.w3.org/ns/sosa/madeBySampler> <http://www.w3.org/ns/ssn/implements>)
  <http://www.w3.org/ns/sosa/usedProcedure>
)
```

Source: `imports/ssn.ttl:178–180`. Source-native; no workbook row creates the chain. The relevant mapped dependency is Sheet2!12, RowID `urn:uuid:377fa547-ff5c-4ffa-af6f-40d291ab2ab9`.

Restriction and dependency: Section 11.2, Restriction on the Property Hierarchy. This is the Sampler instance of `Q -> J -> U -> Q`. The checker identifies the `implements` operand.

Actual diagnostic:

```text
Use of property in chain causes cycle: <http://www.w3.org/ns/ssn/implements> [SubObjectPropertyOf(ObjectPropertyChain(<http://www.w3.org/ns/sosa/madeBySampler> <http://www.w3.org/ns/ssn/implements>) <http://www.w3.org/ns/sosa/usedProcedure>) in OntologyID(OntologyIRI(<http://www.sks.ai/SSN2BFO/>) VersionIRI(<null>))]
```

## Shared simplicity dependency

The restored length-two chain has `<http://www.w3.org/ns/ssn/implementedBy>` as its superproperty. This makes that property composite and non-simple. The unchanged source axiom is:

```text
InverseObjectProperties(
  <http://www.w3.org/ns/ssn/implementedBy>
  <http://www.w3.org/ns/ssn/implements>
)
```

It occurs at `imports/ssn.ttl:264–265`. In the inverse-aware hierarchy, the composite inverse of implementedBy and the named property implements are equivalent. Thus implements is non-simple as well. Each of the three separately asserted minimum-cardinality expressions uses that same non-simple property. A cardinality of one does not exempt a syntactically expressed `ObjectMinCardinality` from the global restriction. No class mapping row or rewritten Sensor definition is needed to reproduce these three diagnostics.

## Exact regularity cycles

The following symbols abbreviate only the full pinned IRIs shown here:

| Symbol | IRI | Pinned name |
|---|---|---|
| P | `https://www.commoncoreontologies.org/ont00001942` | prescribes |
| Q | `https://www.commoncoreontologies.org/ont00001920` | prescribed_by |
| H | `https://www.commoncoreontologies.org/ont00001833` | has_agent |
| A | `https://www.commoncoreontologies.org/ont00001787` | agent_in |
| I | `http://www.w3.org/ns/ssn/implementedBy` | implementedBy |
| J | `http://www.w3.org/ns/ssn/implements` | implements |
| U | `http://www.w3.org/ns/sosa/usedProcedure` | usedProcedure |

The supporting axioms and exact locations are:

```text
InverseObjectProperties(
  <https://www.commoncoreontologies.org/ont00001920>
  <https://www.commoncoreontologies.org/ont00001942>
)
```

`imports/cco.ttl:2297–2299`: Q is inverse to P.

```text
InverseObjectProperties(
  <https://www.commoncoreontologies.org/ont00001787>
  <https://www.commoncoreontologies.org/ont00001833>
)
```

`imports/cco.ttl:975–977`: A is inverse to H. The SSN inverse I/J is shown above.

```text
SubObjectPropertyOf(
  <http://www.w3.org/ns/sosa/usedProcedure>
  <https://www.commoncoreontologies.org/ont00001920>
)
```

This unchanged mapping is in the candidate at `historical-chain/mapping.ttl:100`, governed by `mappings/SSN2BFO-COMS.xlsx#Sheet2!12`, RowID `urn:uuid:377fa547-ff5c-4ffa-af6f-40d291ab2ab9`.

The historical chain is `P o H subPropertyOf I`. Taking inverses and applying the pinned inverse relationships yields the dependency `A o Q subPropertyOf J`. This inverse-normalized form is used here to expose the same role hierarchy; **no separate inverse chain was asserted in the candidate**.

Each source chain is `madeByX o J subPropertyOf U`. The necessary strict chain precedence, after accounting for inverses, is therefore `Q < J < U`. Yet the ordinary property hierarchy already has `U subPropertyOf Q`. The required precedence would put Q strictly below a property that is already a subproperty of Q. The strict chain order cannot coexist with that reverse hierarchy path.

There are three concrete prohibited dependency cycles:

| Cycle | Historical-chain dependency | Source-chain dependency | Closing ordinary inclusion |
|---|---|---|---|
| Sensor | Q -> J, through inverse-normalized `P o H -> I` | J -> U, through `madeBySensor o J -> U` | U -> Q |
| Actuator | Q -> J, through inverse-normalized `P o H -> I` | J -> U, through `madeByActuator o J -> U` | U -> Q |
| Sampler | Q -> J, through inverse-normalized `P o H -> I` | J -> U, through `madeBySampler o J -> U` | U -> Q |

The first two arrows denote strict chain dependencies; the final arrow is the ordinary subproperty inclusion, not a separate chain. The inverse presentation of each cycle is `P -> I -> inverse(U) -> P`, using the inverse source chain and the inverse of `U subPropertyOf Q`.

The checker consequently flags four chain axioms: the three source chains and the common historical chain. These are **four implicated axioms across three concrete cycles**, not four independent cycles. The `has_agent`/`agent_in` inverse identifies the other operand in the inverse-normalized chain; the offending loop is closed through prescribes/prescribed_by, implementedBy/implements, and usedProcedure. It does not depend on adding or changing a hosting mapping, a Sensor class definition, or a madeByX mapping to CCO.

## Typing representative and interpretation boundary

The restored historical typing axiom is:

```text
ObjectPropertyDomain(
  <http://www.w3.org/ns/ssn/implements>
  <http://www.w3.org/ns/ssn/System>
)
```

It is at `historical-chain/mapping.ttl:421`. Historical authority is Common OPs row 17, retained in commit `8512004a3b911ac5711fb0cc8dfe70cb086e3b9b` and documented in `reports/all-mapping-changes-and-rationales.md:153`. The associated current COMS row is Sheet2!58, RowID `urn:uuid:6142726b-21b1-4dba-b5ec-a7d6dca4afab`. The domain is not one of the seven offending axioms and does not close a regularity cycle.

The replacement's executable CONSTRUCT rule is a separate operational artifact. It does not assert a universal OWL property-chain axiom. Its generated individual assertions must be validated with the representative ABox; that validation is distinct from this intentionally failing historical-chain reconstruction. This document makes no logical inconsistency claim about the historical candidate and no claim that an old HermiT-only pass established its OWL 2 DL profile conformance.
