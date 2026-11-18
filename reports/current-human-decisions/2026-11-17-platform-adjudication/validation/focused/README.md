# Platform focused validation evidence

The reproducible driver `validate_platform_candidate.py` reuses existing repository generation, OWL 2 DL/HermiT, and ticket-bound entailment APIs. It changes no repository files.

Final run: `results-v3`, with `validation-v3.log`. Use the repository-root-relative archive `reports/current-semantic-workbook/versions/b9c674c762a748184d3ca4770a7dd769a55344db18fb8174ced035306b73cef7.xlsx` for `--workbook` and `reports/current-semantic-workbook/versions/e7e2ec225e326b0b2bb232591f4949b378876937e6bcb90a3917bfd82d5e87dd.xlsx` for `--baseline-workbook`; pass the repository root with `--root`. Each invocation requires a new external --output directory; existing evidence is never overwritten.

The final run checks the exact one-equivalence replacement in integrated and strict-BFO products, byte identity of alignment-core and CCO-extension products, stable counts, fresh uncached deterministic generation, five product closures (baseline integrated plus all four candidate products), 34 baseline and 34 candidate entailments, and two native-source-only converse checks.

The minimal source proof loads both full premise files (imports/sosa.ttl and imports/ssn.ttl) with existing metadata declaration completion. It does not claim to validate the entire source module distribution. Complete product validation is separate.

Earlier diagnostics remain intact:

- `results`: all complete-product checks passed. Two initial new probe expectations were incorrect about baseline Sensor/Sampler classification as Platform. The baseline already entails both classifications. See probe-expectation-correction.json and related-class-comparison.json; final queries preserve that existing behavior.
- `results-v2`: complete-product and all 68 entailment checks passed. The four-source-only proof had consistent/profile-compliant HermiT results with both expectations passing, but its wrapper correctly recorded technical_failure for the preexisting unresolved SKOS import. See source-proof-scope-note.json. No validator was weakened or source modified.

Zero unsatisfiable named classes refers to unaugmented product closures. Fresh probe classes intentionally denote contradictions (hostless Platform and occurrent Platform; plus nonmaterial Platform in baseline), and their unsatisfiability is an expected test result.

The independent related-class comparison finds only Platform subClassOf MaterialEntity removed and Platform subClassOf Continuant added among emitted named hierarchy edges; System, Sensor, Actuator, and Sampler edges remain identical. It is a bounded hierarchy comparison, not a claim of general model-theoretic conservativity.
