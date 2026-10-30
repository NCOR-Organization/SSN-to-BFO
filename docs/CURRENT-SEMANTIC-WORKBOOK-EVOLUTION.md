# Current SSN/SOSA semantic workbook evolution

This is project-local custody infrastructure. It does not change COMS, the
SOSA-2023 track, any ontology, or any human mapping decision. The authoritative
workbook remains `mappings/SSN2BFO-COMS.xlsx`. A transition record archives a
candidate; it never installs that workbook or edits an assessment.

## Two independent questions

Historical authentication reconstructs exactly what a reviewer approved using
the original workbook bytes, assessment snapshot, review packet, decision body,
reviewer, evidence references, and original input hashes. Those artifacts and
hashes are never replaced by current versions.

Current applicability then examines every intervening governed workbook version.
It compares complete own A/B/C/E rows (including typing, location and RowIDs),
source existence, formal coverage, and the packet's semantic dependencies.
Checking only own source IRIs or only a net final delta is insufficient.

A material change raises `MATERIAL_REQUIRES_REOPEN`. A generic transition cannot
carry a final decision through changed own mappings, changed coverage, a premise
dependency, or changed protected ontology inputs. Contextual chain changes can
carry forward only through an exact, additive `NON_MATERIAL_TO_DECISION`
determination and its binding to the particular validated transition.

## Separate archives and an authenticated chain

`tools/current_documentary_workbook.py` still validates D-only edits: equal
semantic projections and exact changed reasoning cells are mandatory. Semantic
edits cannot use that record type.

`tools/current_semantic_workbook.py` joins documentary and semantic edges into
one unbranched, acyclic history rooted in the unchanged documentary baseline.
It rejects duplicate IDs, disconnected edges, missing snapshots, hash drift,
out-of-order timestamps and an unrecorded live workbook. Old files are retained.
Documentary updates after semantic updates retain their original D-only checks.
Every semantic edge additionally binds the ordered exact bytes of the baseline
and all preceding transition records. This detects predecessor metadata edits,
including authority rationales, when a later semantic edge exists. Archives are
written exclusively without overwriting existing records. A trusted checkpoint
is still needed to anchor newly created records against wholesale rewriting;
hash chaining alone is not a signature or independent approval authority.

Semantic records are stored in
`reports/current-semantic-workbook/transitions/<transition-id>.json`; exact
workbook snapshots are content-addressed under the sibling `versions` directory.
The infrastructure implementation did not itself create an active semantic
transition. The later approved three-term adjudication is recorded by
`58481ff2-4e56-4931-a3d4-383357b16561`; it removes exactly three mappings and
adds none, leaving 105 rows, 100 active mappings and five blank mapping rows.

## Semantic transition schema, version 1

The validator requires exactly these top-level fields:

| Field | Required content |
|---|---|
| `schema_version`, `profile` | `1`, `current-ssn-sosa-semantic-transition-v1` |
| `transition_id`, `workbook_path` | Canonical UUID and the fixed current workbook path |
| `old_workbook_sha256`, `new_workbook_sha256` | Full archived byte identities |
| `prior_history_sha256` | Hash of ordered baseline/predecessor record paths, kinds and full byte hashes |
| `old_semantic_projection_sha256`, `new_semantic_projection_sha256` | Exact A/B/C/E projections; must differ |
| `delta` | Recomputed exact changed rows/cells, old/new predicates/targets, additions, removed assertions, cleared rows, associated D changes |
| `authorities` | Exactly one authority entry per changed RowID, including affected reasoning-only rows |
| `editor_identity`, `timestamp` | Nonempty editor and timezone-aware timestamp |
| `source_target_sha256` | Exact unchanged four source modules and CCO/BFO dependency |
| `governed_input_sha256` | Exact rule, inventory query, current scope, and parallel-track workbook |
| `generation_expectations` | Exact recomputed before/after metrics, canonical logical axioms and their delta, disposition counts and coverage counts/delta |

Each authority has an `authorization_type`, rationale and nonempty bound
evidence list. Every reference includes a project-local path, SHA-256 and a
specific historical reference. Supported authorization types are:

- `RESTORE_PREVIOUSLY_APPROVED_DECISION`
- `REMOVE_PREVIOUSLY_REJECTED_MAPPING`
- `RESTORE_PREVIOUS_TECHNICAL_DEFERRAL`
- `EXPLICIT_NEW_HUMAN_DECISION`

The final category additionally requires a retained human decision artifact;
it must not be used to relabel historical restoration as a new judgment.
Removal/deferral authority cannot introduce a formal mapping.

New `inheritance_sufficient` decisions require an explicit sufficiency approval,
no remaining direct assertion, and bound evidence for an actual inherited
formal route in the exact candidate workbook. Source, target, rule/query and
workbook inputs and the inherited-route hash are independently checked. A blank
row or the presence of a hierarchy path alone does not constitute approval.

Assessment evolution may finalize an unresolved record only through the exact
human decision referenced by a validated `EXPLICIT_NEW_HUMAN_DECISION` edge.
The preserved pre-decision record, immutable input/packet evidence, full current
applicability and every unrelated assessment field remain subject to validation.

Neither declared deltas nor counts are trusted: validators recompute them from
the authenticated workbook snapshots. Unexplained changes fail. Product
selection and structural checks remain active, with baseline expectations used
unless a validated semantic history supplies exact new expectations.
The generator and freshness commands establish this validated context. The
project-local `render_current_formal_products` helper can also render a candidate
under it. Release building and package checking now establish an authenticated
current context too. Historical default hashes, counts and closure contracts
remain fixed; the current context independently derives exact formal product
hashes, sizes, mapping partitions, closure counts and declaration completions
from the validated transition. Schema-valid counts alone cannot satisfy this
contract. Full package profile, reasoning, archive and rehearsal gates still
apply. Rendering is not permission to publish a package or a claim that those
independent gates have been satisfied. See
[the current release contract](VALIDATION-AND-RELEASES.md#authenticated-current-release-expectations).

## Current validation and evidence architecture

Documentary evolution remains limited to D-only changes with equal semantic
projections. Semantic evolution authenticates changed A/B/C/E rows, exact
before/after snapshots and explicit authority. Both form the same ordered
history; neither can be used to bypass the other's checks. Decision
applicability checks the full intervening history and preserves the original
human records, including the sample pair's separately approved non-material
chain-removal determination.

[Retained evidence](CURRENT-RETAINED-EVIDENCE.md) resolves immutable historical
report bytes when a regenerable current report has changed. That proves custody,
not freshness. Current execution must still bind the actual source, target,
workbook, tools and validation inputs; an old receipt cannot become current by
changing its recorded hashes. Portable execution retention likewise preserves
the original receipt and semantic result while authenticating its exact input
documents independently of an ignored build directory.

The current release/package reasoning contract is transition-aware. Its raw
historical defaults remain available for historical fixtures; only authenticated
current context supplies evolved expectations. SOSA-2023 keeps separate source,
workbook and product identities. Cross-track generation and reasoning verify
that protected current-track files are unchanged throughout their transaction.

ROBOT reconstruction checks the current governed partition exactly: 98 ordinary
mappings plus two property chains. Missing, extra or mismatched expressions fail;
an unexplained workbook change cannot obtain different expected counts. The
RDFLib/ROBOT query-equivalence pilot compares the same local asserted execution
graphs, with import directives removed only from those temporary query inputs.
It does not establish complete imported ontology closure or resolve the missing
local SKOS dependency.

Scoped readiness reconciliation selects additive successor evidence and retains
the previous run as historical evidence. Selection never overrides command
freshness, execution custody, semantic status or an outstanding whole-repository
gate. The recorded three-term reconciliation has no Class A blockers; its
independent Class B work remains open. Subsequent source changes and commits
require fresh validation bindings before making a new current-evidence claim.

Three-term adjudication fully validated within scope; overall current-track publication readiness remains blocked by independent Class B work.

## Prepared sample-pair applicability

The two files under `reports/current-decision-applicability/prepared` retain
Alec Sculley's explicit non-material determination for removal of the
`described_by o is_about -> ssn:forProperty` context chain. They bind the exact
original decision, old workbook, planned new semantic projection, dependency
states, rationale, evidence and reviewer. They are `PREPARED_NOT_ACTIVE`.

These prepared records do not authorize another dependency change, alter the
original decisions, or activate a semantic transition. An additive binding
record must identify the actual validated transition and its exact new full
workbook hash. The application check independently compares actual old/new
packet context. No semantic restoration or applicability activation occurs in
the infrastructure task.
Their exact paths and byte hashes are registered in the project-local validator;
copying or modifying one cannot create another approved determination.

The additive `*-forProperty-three-term-2026-10-26.json` records reuse the explicit
Part 6 approval for the same exact contextual chain removal with the narrower
three-term candidate projection. They retain the original dependency states,
reviewer and rationale and cite the immutable original determination. They do
not approve another dependency change. The original five-term prepared records
remain unchanged and are not used for this candidate.

## Mechanically derived unreviewed RowIDs

`current_assessment.evolve_unreviewed_row_ids` returns a copy whose RowID lists
are derived from the validated workbook history. It does not write an
assessment file. Only unreviewed records may change membership through this
helper, and their state, outcome, rationale and decision status are preserved.
Finalized membership changes cannot bypass applicability validation.

## Historical five-term application plan

The following is the earlier plan, retained as context. The October 26
three-term adjudication is a new explicit human decision and does not authorize
the sensor additions or treat the July outcomes as its authority.

1. Confirm the accepted Git checkpoint, unchanged live workbook and historical
   custody. Retain all existing archives and source/target identities.
2. Construct the separately authorized five-term candidate, retaining the four
   sensor typing rows; append the two sensor subproperty rows at Sheet2!63–64;
   clear B/C only at Sheet2!49, Sheet1!43 and Sheet1!45; update only their
   historically supported reasoning. Do not change implementedBy/implements.
3. Reuse the preflight's planned sensor RowIDs
   `urn:uuid:2876e7da-9716-4fe9-ab0e-7f118e6f9146` and
   `urn:uuid:b1d0b7d5-e004-4680-a738-1dc7d8d0edff`. The prepared applicability
   records bind the resulting semantic projection
   `101ff4cc24f493b90fadb70fb7cfcef26ba07f81c7b2670f7f8ce3f5c5172a45`.
4. Inspect `tools/current_semantic_workbook.py delta --old OLD --new CANDIDATE`.
   Provide exact historical authority for every changed RowID, then use
   `record --old OLD --new CANDIDATE --authorities AUTHORITY_JSON --editor ...`.
   This archives validated evidence without installing the candidate.
5. Use `tools/current_decision_applicability.py --bind-prepared PATH
   --transition-id UUID` for each prepared sample record. Each binding must
   match the approved old version, planned semantic projection and dependency.
6. Install the authorized workbook and persist only the mechanically derived
   unreviewed sensor RowID metadata. Revalidate sample applicability; preserve
   all assessment states, outcomes and original decision evidence.
7. Regenerate products and current reports. Verify exactly two added and three
   removed axioms, 107 rows, 102 axioms and five blank rows, all governed product
   counts, coverage, input identities, preservation, and requested regressions.
   Report profile/closure limitations explicitly; count validation is not a
   reasoner success claim.

## Explicit successor checkpoints

The original freeze and accepted checkpoint remain immutable historical
authorities. `tools/current_checkpoint_successor.py` provides a separate
two-phase successor process; ordinary ancestry does not grant acceptance.

First, while HEAD is already accepted, `prepare` authenticates the current
semantic history, assessment evolution and deterministic products. It requires
an explicit project-local human authorization and a complete fresh ledger of
the commands required by publication validation, including the full unit suite
and `make check`. It binds the predecessor, semantic projection, product and
history identities, exact validation inputs and outputs, and the exact candidate
file inventory. The record has status `PREPARED_NOT_COMMITTED` and contains no
predicted successor SHA. Additional intended files must be supplied with
`--include`; unrelated untracked work is not implicitly authorized.

After the separately authorized content commit actually exists, `bind` takes
its full SHA and checks its tree against the prepared inventory plus the
prepared record. The binding records that actual SHA and tree. An unbound
content commit is rejected. To retain the binding in Git without a
self-referential commit identity, one immediate child may contain exactly the
binding addition and no other tree change. Further descendants require another
explicit preparation and binding. Missing, corrupt, mismatched or stale
authority/validation records fail closed.

The commands are:

```text
python -B tools/current_checkpoint_successor.py prepare --validation LEDGER --authorization AUTHORIZATION --reviewer REVIEWER [--include PATH ...]
python -B tools/current_checkpoint_successor.py bind --prepared PREPARED_RECORD --commit ACTUAL_COMMITTED_SHA
python -B tools/current_checkpoint_successor.py check
```

These commands never stage or commit. Existing receipts retain their actual
execution HEAD and bytes; acceptance of a checkpoint does not relabel them as
post-commit executions or grant publication readiness. No successor can be
finalized before its real content commit exists.
