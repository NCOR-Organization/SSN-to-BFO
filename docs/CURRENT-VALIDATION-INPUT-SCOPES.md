# Current validation input scopes

This contract separates an execution's inputs from its outputs and from the
evidence a later consumer must authenticate. It does not change ontology
semantics, human decisions, formal products, historical outcomes, or publication
acceptance criteria. A selected, completed semantic `FAIL` remains `FAIL` and
cannot establish publication readiness.

## Why the original inventory is insufficient

The original publication-validation contract used one input map for every
required command. It included relevant files under the source, tool, test,
configuration and mapping directories; documentary and human-decision evidence;
and every file discovered under `reports/retained-evidence`. Each receipt bound
that complete map before and after its execution. Current acceptance required
exact equality with the newly discovered repository-wide map.

The completed October 29 ledger recorded 316 inputs. Its eight commands passed.
The separate semantic execution completed with a substantive `FAIL`. Retaining
that execution requires 27 new RDF objects and one manifest, which would expand
the original inventory to 344 inputs without changing any of the original 316
bytes. Neither that expansion nor a later scope change retroactively changes
what those receipts authenticated.

The original assessment generator also included the complete retained store in
all three JSON report bindings. Thus adding an unrelated semantic execution
object changed assessment metadata even when the assessment never resolved that
object while constructing or authenticating its review packets.

The broad inventory alone does not establish semantic dependence. Conversely,
an actual read must not be hidden by narrowing an input map. In particular,
`release_context._release_input_signature` hashes the complete retained store
before and after a release operation. The unit and full repository suites
exercise that code, so their inputs continue to include the complete store.
The release guard is preserved unchanged.

## Dependency classes

| Class | Meaning | Required binding |
|---|---|---|
| Execution input | A file, membership rule, configuration, executable or authenticated authority that can affect the named execution | Exact declared scope and byte identities at execution; unchanged applicable inputs when accepting current evidence |
| Execution output | A result, generated document, log or receipt produced by that execution | Actual producer, completion state, outcome and output hashes; never invented as a pre-existing input |
| Custody evidence | Immutable objects and records that authenticate a particular earlier execution or authority | Exact content, logical role, producer, dependencies and source identity |
| Readiness dependency | A selected execution, its custody, an assessment or another condition consumed by the readiness evaluator | Current selection and applicability, complete custody, and the independently required outcome |

These classes are relative to an operation. A generated assessment report is an
output of assessment generation and an input to the later assessment freshness
check. A retained RDF graph is a semantic execution output and a custody input
to later reconciliation. A receipt is an output of its producer and an input to
readiness or checkpoint acceptance.

## Versioned execution contract

The original unversioned universal-map behavior is the historical version 1
contract. Its 316-input receipts and original issuer, tests, logs, STOP and
selection records remain immutable. They continue to describe their actual
executions. They are not silently reinterpreted as version 2 receipts, edited to
claim later inputs, or promoted to current evidence merely because a smaller
new scope is a subset of their old map.

Version 2 uses code-owned scopes for named execution roles. A receipt cannot
choose an arbitrary list of dependencies or grant itself a reduced scope. Its
scope declaration must match the governed version, role and policy identities;
its input map must match that scope. Unknown or forged declarations, missing
required files, changed tools, incorrect role/command identities and stale
bindings fail closed.

`tools/current_validation_scope.py` owns schema version `2` and profile
`current-validation-inputs-v2`. `role_paths(root, role)` discovers the declared
files; `role_inputs(root, role)` binds their hashes. `scope_declaration` and
`validate_declaration` bind and check the role, scope-policy bytes, custody-policy
bytes and required absence assertions. `ledger_inputs(root)` is the union of
the role scopes, not a replacement for each command's own map.
`required_executables(role)` identifies the executable families whose actual
resolved content identities must be captured. Discovery includes conditional
local imports and maintained file-family membership, rather than trusting a
trace of only one successful branch.

Repository input files and runtime tool identities have separate bindings.
`execution_tools(root, role)` records required executable paths, hashes and
sizes, including the fixed installer shell/interpreter and the pinned ROBOT JAR
for reasoning roles. The JAR at `build/lib/robot-1.9.7/robot.jar` is an ignored,
separately provisioned toolchain dependency. Its exact bytes must match the
governed pin and the receipt's expected, before and after runtime identities;
it is not a repository input that checkpoint preparation requires in the Git
candidate tree. This separation does not permit an absent, replaced or unpinned
JAR. The checkpoint retains the execution ledger's runtime bindings without
requiring force-addition of the JAR or an ignored execution directory.

Dependencies include executable identity and the relevant implementation and
configuration. A changed scope implementation is not automatically non-material
to an earlier execution. This migration requires fresh evidence for all eight
roles after the implementation and their inputs are final. The original
316-input ledger remains historical evidence.

Report-local receipt/log outputs and the future current-evidence selector are
not inputs to the execution that produces them. This does not exempt them from
later custody, readiness or checkpoint authentication. Nor does it exempt
rendered reports that a check actually opens.

## Role boundaries and retained evidence

The following table describes dependency boundaries, not permission to omit
implementation, configuration, workbook, source, product or expected-output
dependencies. Exact membership is determined by the governed scope functions.

| Role | Required execution | Retained evidence actually consumed |
|---|---|---|
| `unit_tests` | Exact unit discovery over `tests` | The complete retained store, because maintained release integration tests exercise the unchanged release input-signature guard; plus explicitly consumed authority and fixture dependencies |
| `assessment` | Current assessment validation and rendered-report freshness check | Only retained manifests/snapshots reached while authenticating documentary history, human decisions, review packets, sufficiency evidence and their dependencies; the check also binds the six rendered version 2 reports |
| `source_identity` | Current source, target, workbook, product and configuration identity checks | Authenticated documentary/semantic history and decision custody reached by those checks, including the applicable historical report pair |
| `generation_freshness` | COMS generation freshness in check-only mode | Authenticated current workbook/history and decision dependencies, including the applicable historical report pair; maintained generation outputs remain checked |
| `sosa_source_version` | Governed SOSA source-version checks | The pinned SOSA track's actual source/version authorities; unrelated current-track execution retention is not an input merely because it exists |
| `sosa_products` | Governed SOSA product checks | The pinned SOSA track's actual workbook, rule, source and product dependencies, plus the authenticated current-authority closure used by shared checking infrastructure; unrelated execution retention is not a universal dependency |
| `static_checks` | `make compile` | The Makefile and the implementation/test files actually compiled, with required tool identity; compilation does not consume arbitrary retained RDF bytes |
| `full_repository_gate` | `make check` | The complete retained store through the release guard, plus the full suite's consumed authority, report and fixture dependencies |

The semantic driver is separate from these eight roles. Its own governed
inputs, expected execution plan, invocation records, helper/tool identities and
raw evidence remain authenticated independently. Its generated RDF and any
subsequent retention manifest are not inputs to the semantic computation that
produced them. The driver is not rerun merely because it returned `FAIL`.

A completed diagnostic FAIL can include either an authenticated profile-failure
payload or a Java-emitted `technical_failure` payload with exit `2` and a
nonempty error. The helper deliberately emits that structured result after
catching a technical exception. Acceptance as completed evidence still requires
normal wrapper completion, every required invocation, matching captured payload
bytes and exit status, and the existing ticket/provenance checks. A nonzero
exit or self-declared completion flag alone proves none of these conditions.
Signals, timeouts, launch failures, missing slots and missing or mismatched
payloads remain incomplete or invalid evidence. A completed technical failure
does not establish a successful reasoning result or publication readiness.

Reachable historical custody uses `current_custody_dependencies`:

- `assessment_paths(root)` discovers the assessment's authenticated inputs.
- `authority_paths(root, publication=False)` discovers authenticated current
  authority dependencies.
- `authority_paths(root, publication=True)` additionally resolves publication
  preservation's trusted historical and checkpoint authorities.

At the audited pre-migration state, ordinary assessment, generation and source
authority consumption reaches one retained historical report pair: its manifest
and snapshot, two files. Publication preservation additionally consumes a
second pair, four files in total. These are dependency observations, not hardcoded
caps. A newly referenced authority must enter the appropriate scope, while an
unrelated object does not enter every scope by directory membership alone.
The original and new semantic execution objects are different from those
historical report pairs.

## Version 2 placeholder and catalog guard scope

The placeholder/catalog regression previously scanned `git ls-files`. That was
an actual byte dependency, not merely a list of test names: it hashed tracked
regular files for retired placeholder content and searched tracked text for
retired references. A tracked current selector or future execution report would
therefore become an input to a suite that must run before selecting its own
receipt. Conversely, untracked active implementation files escaped that scan.

The version 2 guard and the unit/full-suite input scopes share the code-owned
`migration_guard_paths(root)` function. Its membership is:

- All non-report tracked regular project files, together with nonignored
  untracked regular project files. Paths are deduplicated, so staging an unchanged
  file does not change membership. This includes active files such as
  `LICENSE`, `.gitattributes` and `release-notes`, as well as source, tools,
  tests and configuration.
- The fixed report-path inventory from accepted checkpoint
  `dc314460fe3e875ba1c8ccfcb3c6840a7181e733`, checked against the live bytes at
  those paths. Every previously scanned historical report remains in scope;
  immutable Git content alone is not a substitute for checking the live files.

The existing `tracked_paths` test helper is a compatibility name for this
shared guard scope, including its pattern filtering; it no longer means that
only Git-index members are inspected. Neither caller may independently widen
or shrink the shared file set. Missing required historical files, invalid paths
and symlink substitutions fail closed.

Future report outputs and the current selector are outside this placeholder
audit. They are authenticated by their specific report-freshness, receipt,
custody, selection and readiness consumers. This is an explicit audit boundary,
not an exemption from those checks. Fixed historical execution fixtures that
other tests actually consume still enter the corresponding suite scope through
their exact authenticated dependency closure.

Retired path normalization, distinctive legacy aliases, command/IRI checks and
the enumerated historical-reference allowance retain their existing meanings.
Files that intentionally define negative fixtures or the retired-name policy
have narrow textual-scan exceptions; their bytes remain execution dependencies,
and the retired-placeholder byte guard still applies. Adding an unrelated report
cannot silently extend the guard's input membership or create another
producer-output cycle.

## Assessment generation and freshness

`assessment_scope(root)` identifies schema version 2 and profile
`current-ssn-sosa-assessment-inputs-v2`, binds the scope policy, and describes
authenticated reachable custody. `current_assessment.REPORT_DIRECTORY` names
`reports/current-assessment/v2`; `REPORT_NAMES` identifies the six rendered
successor files. Existing historical report bytes remain in place.

The generator's binding excludes its own future outputs. It includes the
source/target, workbook, assessment, relevant tools and configuration, and every
authority or retained snapshot actually resolved to build and authenticate the
reports. Historical report references retain their recorded hashes and are
resolved through the existing custody mechanism. Merely deleting retained
evidence from the binding is not an acceptable implementation.

The later default assessment check regenerates expected content in memory and
requires exact canonical output equality. Its execution scope includes the six
already rendered files. Missing successor reports fail closed until migration
creates them. A material input or generator change makes the corresponding
reports stale; unrelated execution retention does not by itself change the
generator's dependency identity. No metadata-only exception permits substantive
report differences.

## Cycles and snapshot-specific dependencies

Under the universal contract, refreshing the semantic execution and then
retaining its outputs produces this feedback:

```text
universal current inputs -> semantic execution -> new retained output/manifest
          ^                                             |
          +--------------- whole-store inventory -------+
```

Every new semantic report has a new run identity and therefore a new retention
manifest, even if graph objects happen to deduplicate. Repeating that producer
to refresh its outer universal receipt does not solve the feedback.

Version 2 separates the semantic producer from downstream consumers. Retention
occurs once before the fresh unit/full-suite executions, whose actual complete
store input then remains fixed:

```text
semantic inputs -> completed semantic FAIL -> exact retained custody
                                               |
final code + authority/assessment fixtures -----+--> fresh role executions
                                                     |
                                                     v
                                        immutable receipts and ledger
                                                     |
semantic FAIL + custody -----------------------------+--> explicit selection
                                                             |
                                                             v
                                                     readiness evaluation
```

Those eight executions do not produce a new semantic run to retain. Their
receipt and log creation does not add files to their own input scopes. Adding
more retained objects later can invalidate the unit/full-suite applicability
because those roles genuinely consume the whole store; it does not require
inventing a fresh semantic execution to repair that later applicability.

The full suite must not secretly consume a mutable current selector while
declaring it absent. Checkpoint authority integration is separated from current
selection authentication, and selection behavior is tested with explicit
immutable fixtures. Actual checkpoint preparation and binding still
authenticate the selected semantic evidence and the current ledger. This keeps
the suite from depending on the selector that will point to its future receipt.

Historical assessment preservation is a different, finite dependency:
assessment version A0 can be retained before version A1 is generated. A1 binds
the specific retained A0 when it actually consumes it; it does not bind an
archive of its own future bytes. Likewise, the existing two-phase checkpoint
process binds a prepared candidate and then its actual committed SHA. Neither
snapshot-specific relationship grants publication readiness or rewrites prior
execution HEADs.

## Finite migration sequence

This is an execution order, not a claim that migration has run.

1. Finalize the versioned scope policy, its consumers and negative regression
   coverage. Preserve the original 316-input receipts, issuer, tests, STOP,
   selected historical records and semantic outcome. Keep the semantic
   execution's explicitly bound helper/tool dependencies unchanged when reusing
   that execution.
2. Run the focused dependency-contract tests and confirm stability: genuine
   input changes fail; unrelated retained outputs do not change producer
   identity; a consumer binds the exact evidence it reads; missing/corrupt
   custody and forged scopes fail. No full migration proceeds on a failed
   contract test or an unresolved dependency.
3. Retain the existing 27 runtime RDF artifacts through the governed portable
   custody mechanism. Authenticate every object, role, producer, dependency and
   tool, and prove fresh-checkout reconciliation without the original runtime
   tree. Preserve all previously retained objects. No new semantic execution is
   needed solely to preserve the completed FAIL.
4. Generate the six version 2 assessment outputs from their precise dependency
   scope. Authenticate the old reports independently and leave them unchanged.
   Validate the successor reports' canonical content and required freshness.
5. With code, fixtures, retained store and rendered reports final, execute and
   issue fresh version 2 receipts for all eight roles. Use a separately
   versioned native recorder that captures the code-owned role declaration,
   exact expected/before/after input maps, executable maps and environment,
   actual subprocess completion, and immutable output hashes. Finalize and test
   that recorder before freezing these execution inputs; do not modify or reuse
   the frozen v1 issuer to relabel historical runs. In particular, run unit
   discovery and the full repository gate after retention because their
   unchanged release guard reads the whole store. Bind actual outcomes and
   pre/post inputs. Do not relabel the old 316-input executions as these runs.
6. Authenticate the completed semantic FAIL and its portable custody separately
   from the eight-role PASS ledger. Missing, interrupted, signal-terminated,
   timed-out, forged or mismatched execution evidence remains ineligible.
   Preserve the actual FAIL and every substantive semantic blocker.
7. Activate an explicit, atomic current selection only after all eligibility
   checks pass. Preserve predecessor identities and the earlier STOP. The
   selection consumer reads the completed receipts; those receipts do not claim
   to have consumed this future selector.
8. Run readiness against that selection. Report its actual diagnostics and
   outcome. Publication remains `NOT_READY` while substantive semantic,
   human-review, expectation, import/profile or environment requirements remain
   unsatisfied. Authenticate checkpoint and preservation requirements separately
   without staging or committing.

This order terminates because each producer finishes before its outputs become
inputs to a later consumer. No step requires one of the eight role executions
to validate its own future receipt, or requires the completed semantic
execution to consume its later retention manifest. Any subsequent material
change starts a new, explicit applicability or execution obligation; it never
changes the recorded meaning of an earlier receipt.

## Native recorder and readiness output

`tools/current_validation_execution.py` implements the native
`current-validation-execution-v2` recorder. In a new `v2-*` directory beneath
`reports/current-publication-validation`, `prepare` freezes the eight scopes,
producer and test identities, authorization, runtime tools, and environment.
It retains actual Python and Java version measurements. A mismatch with the
declared toolchain remains an environment requirement; it cannot be asserted
away by a ledger field.

`run-role ROLE` executes the code-owned command in the required order. Each
attempt has a create-once prelaunch ticket, streamed log, actual completion
capture, and sealed receipt. A failure or input drift creates an immutable
`STOP.json` and prevents subsequent roles or ledger issuance. `ledger` requires
eight authenticated successful receipts; `authenticate` verifies their custody
and current applicability. No command accepts an externally supplied PASS or
reconstructs a result from a previous execution.

The ordinary readiness consumer requires this native custody for current v2
ledgers. `tools/current_publication_readiness.py --output-dir NEW_DIRECTORY`
creates additive JSON and Markdown without overwriting the historical report.
Every blocker is retained and classified: Class A covers evidence, applicability,
custody, portability and selection defects; Class B covers authenticated semantic
outcomes and outstanding review, approval, import/profile and environment
requirements. Unknown diagnostics remain Class A. Classification does not change
the publication acceptance criteria or the `NOT_READY` exit status.
