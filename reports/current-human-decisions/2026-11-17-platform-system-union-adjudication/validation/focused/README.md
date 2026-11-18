# Focused Platform/System union validation

Four fresh maintained-product OWL 2 DL/HermiT validations passed, each with zero named unsatisfiable classes. A separate fresh replay against the actual generated candidate passed all **58 candidate expectations and four native-source expectations**, plus the explicit distinct-individual nested-Platform ABox. Intentional unsatisfiable probe classes are diagnostic combinations; they are not newly unsatisfiable classes in the maintained ontology. See `summary.json`, the four product result files, and `replay-results/`.

The exact generated graph is identical to the previously assessed both-union candidate. Pinned closure dependencies and the reasoner API/helper were verified unchanged before reusing historical observations. Selected original records remain byte-identical in `reused-impact/`; their original absolute paths and temporary output references are historical execution provenance. The original exploratory query builder used placeholder expected values, so some original `passed` flags are false even though their actual entailment answers were established. The fresh replay explicitly checks those actual answers as expectations. The broader **263** historical comparison answers are not presented as 263 fresh final-candidate tests.

## Logical delta and modular placement

`logical-delta.json` proves exactly two equivalence replacements against both the committed material-only baseline and preserved intermediate Platform-Continuant state. Platform and System now each have the union MaterialEntity-or-InformationContentEntity plus their unchanged hosting/implementation existential. No other integrated mapping graph change occurred. Both mixed expressions move from the strict-BFO product into the CCO extension under the existing generator partition; the alignment core is byte-identical. Counts remain 108 governed rows, 102 assertions, and six deliberately blank rows. Fresh uncached generation was byte-deterministic.

## Replay without external historical snapshots

Run from a checkout containing the final generated product and pinned dependencies, using the existing Python/RDF/Java environment:

```sh
python reports/current-human-decisions/2026-11-17-platform-system-union-adjudication/validation/focused/reused-impact/replay_focused_queries.py --root "$PWD" --output /tmp/ssn-union-focused-replay
```

The output directory must be new and outside the repository. The wrapper imports the retained original query builder without executing its historical candidate-generation main. It reads the final `SSN2BFO.ttl`, retained query evidence and pinned dependencies; it does not require an absent original temporary ontology or workbook. The historical structural-comparison driver `validate_union_candidate.py` deliberately requires baseline HEAD `3376e1c74e846e40e6863ec8b1f1c255349aa2d3` and caller-supplied intermediate/final workbooks; its output is retained as executed evidence, not represented as an arbitrary-HEAD replay command.

## Scope and qualifications

Material and ICE Platform/System combinations are satisfiable; both classes remain continuants and retain their existential witnesses. A Platform hosting another, explicitly different, ICE Platform is consistent. The inner entity is also classified as a System by the unchanged source hosting restriction. ICE Systems can implement Procedures; System-and-Procedure overlap is satisfiable. The GDC branch of either union requires ICE and therefore the pinned CCO aboutness restriction; this is not permission for every nonmaterial continuant or an identification of information content with its material bearer.

Sites, spatial regions, other immaterial independent continuants, specifically dependent continuants, and occurrents cannot satisfy these union classifications. ICE Sensor/Actuator/Sampler combinations remain impossible under their unchanged material mappings. ICE System with SystemCapability, ICE System bearing a Function, and mixed material/ICE subsystem directions remain incompatible; ICE-to-ICE subsystems and ICE System agent-in Process are satisfiable. These previously identified conditional conflicts were tested and disclosed, not repaired or mistaken for ontology inconsistency.

The native-source converse proof uses only complete pinned SOSA and SSN files. `imports/sosa.ttl:156` supplies hosts/isHostedBy inverse; `imports/ssn.ttl:717-721` supplies System only isHostedBy Platform, proving exists-hosts-System subclass Platform. `imports/ssn.ttl:264-265` supplies implementedBy/implements inverse; `imports/ssn.ttl:517-520` supplies Procedure only implementedBy System, proving exists-implements-Procedure subclass System. Source alone does not require either existential witness; those necessities remain adopted mapping commitments. DUL Object is historical interpretive context, not an axiom claimed present in the loaded pinned closure.
