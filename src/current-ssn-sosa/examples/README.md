# Current SSN/SOSA examples

Current SSN/SOSA example instance data lives under `examples/sosa-instance-data/`.

These files are example/instance data for review and testing. They are not ontology imports, and they are not currently imported into the current SSN/SOSA editor ontology.

To parse-check all Turtle examples without modifying them, run:

```sh
make validate-examples
```

From the repository root, the same check can be run with:

```sh
make -C src validate-examples
```

The target writes only generated temporary parse outputs under `build/artifacts/`.

There are 11 retained Turtle source examples. The existing smoke test additionally constructs one synthetic Sample Relationship fixture; that fixture is not a twelfth source example. Parsing and RDFS smoke results do not establish OWL DL consistency. The publication evaluation runs source-only and aligned attempts separately with the unchanged local logical axioms, records per-file hashes, and distinguishes consistency results from import/profile/tool failures. See `reports/current-ssn-sosa-semantic-validation.md` and the consolidated publication-readiness report for the current results and exact-closure limitations.
