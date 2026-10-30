# Retained historical evidence

A historical supporting-evidence reference identifies a logical path and an
exact SHA-256. Some such paths are also canonical current report outputs.
Regenerating a report must neither rewrite its old evidence reference nor make
the new report impersonate its historical contents.

`tools/current_retained_evidence.py` resolves matching live bytes first. When
those bytes differ, it requires a manifest binding the same logical path and
hash to an exact content-addressed snapshot under
`reports/retained-evidence/sha256/`. Missing, corrupt, misbound, noncanonical,
or symlinked evidence fails. Manifests also retain byte size, recovery commit
and blob, creation date, reason, and custody classification. Recovery verifies
the Git commit's file and blob before creating files exclusively; existing
snapshots and manifests are never overwritten.

Documentary and semantic supporting-evidence references use this resolver.
Physical workbook versions, human decision records, prepared applicability
authorizations, and sufficiency artifacts still require unchanged live bytes.
Their supporting evidence can use historical resolution. Publication
preservation permits retained resolution for canonical report outputs only;
its original Git inventories and expected hashes remain authoritative. Source,
target, mapping-product, and execution-freshness checks keep their existing
separate gates. A retained historical report cannot establish that today's
generated report or reasoner execution is current.

The initial snapshots recover two reports from commit
`dc314460fe3e875ba1c8ccfcb3c6840a7181e733`:

- `reports/coms-vs-pre-coms-legacy-diff.md`, historical SHA-256
  `7437af5ccb6b581a062ba6edcee530e6a068ccd676d10e821ac318c6727be860`.
- `reports/coms-source-term-coverage.md`, historical SHA-256
  `11330ccd4bed83934a6520a6cb6024c7f31bc5ebf5d405f5045e58b7d8deb36c`.

The first supports four references in documentary update
`5f0e3bc5-b52e-4502-8fd5-f7f1c182913b`; both preserve publication-baseline
authorities. The update and all its hashes remain unchanged. The live reports
remain canonical regenerable outputs. The same update also references
`reports/current-ssn-sosa-semantic-validation.md`; those bytes still match, so
no snapshot is currently needed for that report.

Evidence discovery includes selected manifests and snapshots. Current
assessment and publication-validation input inventories also bind the retained
store, including snapshots needed only by publication preservation. This keeps
historical custody dependencies visible without substituting them for live
input hashes.

## Portable execution custody

`tools/current_portable_execution_evidence.py` retains exact RDF/query input
bytes from an already recorded ticketed execution. Content-addressed objects
live under `reports/retained-evidence/execution/sha256/`; a canonical manifest
under the sibling `manifests/` directory binds the original report, logical
document roles and paths, SHA-256, byte size, producing command, execution slot,
source inputs and dependent ticket/capture/envelope/result records. Objects
shared by several bindings are stored once. Missing, corrupt or misbound objects
fail; a present manifest cannot silently fall back to runtime files.

The selected October 28 execution has 27 RDF input documents. Their retained
objects make exact custody verification independent of its ignored execution
directory. The original absolute paths remain unchanged in historical receipts.
The adapter normalizes their authenticated checkout and executable locations
when comparing commands, while retaining argument order, graph/query identities,
wrapper role and bytes, captured outputs, seals and semantic results. Executable
content identity remains required. The manifest also carries references to the
recorded Java version, configured environment, reasoner JAR and helper source;
it does not certify a new environment merely because a tool moved.

Historical physical paths, portable retained-object paths, and logical evidence
references have separate roles. For example, a historical `source-hierarchy`
ticket names the graph consumed at its original absolute location; its manifest
binds the logical execution path, slot, producer, dependencies, hash and size to
the exact retained object. Reconciliation reads that retained object in the new
checkout without requiring the original graph or execution directory to exist.
Neither a filename nor an execution role alone establishes identity.

The invocation wrapper's historical absolute path can also have a different
filesystem spelling from the recorded graph root. Portable reconciliation first
authenticates the selected ticket and its dependent records, then binds the
recorded wrapper hash to the report's governed logical helper reference and the
same helper bytes in the new checkout. It does not resolve or rewrite that old
physical path, infer the helper role from its basename, or trust an arbitrary
external file. Live-file containment and exact retained-object bindings remain
separate checks. Changing a historical path changes the receipt bytes and fails
custody authentication; changing a current dependency or required tool identity
does not become acceptable merely because the checkout moved.

Create retention once with:

```text
python -B tools/current_portable_execution_evidence.py --report REPORT_PATH --retain
```

The existing readiness selector and semantic evidence validators discover and
authenticate the manifest for their selected report. No selector flag can waive
custody or promote a failed result. Freshness remains a separate requirement:
current HEAD, exact material inputs, required commands and environment checks
still apply. Portable historical evidence is not a claim that the current
checkout reran the reasoner. New executions require additive receipts; original
reports and execution outcomes are never rewritten.
