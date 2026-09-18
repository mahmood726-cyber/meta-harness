# AUD2 — assurance deletion and receipt accounting

**Status: implementation and targeted verification delivered; the full requested
real-evidence finish condition is BLOCKED, not claimed complete.** No commit,
network acquisition, reset, checkout or stash was performed. HEAD:
`3f8add72d50b84eae2000625387e3194137a06ea`.

The session-start index/workbook were read from F:. Neither was edited: this is
lane repair work, not a submission or project-status promotion. Existing dirty
worktree changes were preserved. No source identifiers, study dates, effect
estimates or adjudications were invented as research evidence.

## What changed

* `harness/census.py`: significance receipts contain `check_id`, `surface`,
  `state`, and `detail`. Outcome and strand checks actually execute; renderer and
  checker exceptions are failed receipts. Counts come from completed receipts.
  Canonical-engine labels require a successful replay receipt bound to member
  inputs and result values. The single-trial label cannot certify k=8. Required
  endpoint spans, domain assessments, held-document digests and attached ADJ
  references are checked before building. Existing certificate-bound context
  cannot silently lose a failed receipt during a rebuild.
* `harness/grade.py`: no decision-relevant precision rating without an explicit
  clinical threshold and information-size assessment. A boundary exactly at the
  null requires judgement. Missing/invalid completed-trial denominators never
  become 0% unpublished. Missing GRADE domains fail validation. `render_certainty`
  was not edited.
* `harness/search_completeness.py`: held record sets, source/query joins, raw
  response files/digests and counts derived from record membership are required.
  Every published topic's support is validated; measurement-split counts remain
  separate. Malformed/unavailable evidence refuses.
* `harness/certificate.py`: binds the entire certificate-free rendered review,
  including reproduction tallies and receipts, rendered page bytes, full
  scientific member inputs under existing dependency references, and relevant
  working source files. Four named assurance kinds appear in its rendered JSON:
  **Integrity**, **Execution**, **Semantic compatibility**, **Scientific adequacy**.
  The object says a hash establishes identity, not truth. Execution states its
  local-process trust model. Scientific adequacy retains reviewer trust inputs
  and `REQUIRES_JUDGEMENT`; no hash is presented as human scientific approval.
* `harness/gate.py`: added required-support and registered-search-support checks;
  no existing gate was weakened. `scripts/verify_all.py` emits limb receipts and
  derives failures from their states, including exceptions.

## Measured plants: before and after

Pre-edit measurements are in [.tmp/aud2/before.json](.tmp/aud2/before.json).
The search/old-certificate probe in [.tmp/aud2/preprobe.json](.tmp/aud2/preprobe.json)
loads HEAD implementations in memory with current local supporting dependencies;
it is explicitly not a pristine historical full-environment replay.

| Plant | Before | After | Evidence status |
|---|---|---|---|
| IV-iron significance coverage | **“claims checked: 4”; actual checker calls: 0** | **4 completed claim receipts / 4 calls / 4 strand claims** | MEASURED; spy around the actual checker |
| k=8 carrying `source-reported-CI:k=1-verbatim` | violation list `[]` | rejected | MEASURED mutation |
| `{"pico_scoped": true}` | `assessed: true`, downgrade 0, `ghost_fraction: 0.0`; “0 of ~0 … upper bound 0%” | `assessed: false`, `NOT_ASSESSABLE`, fraction `null` | MEASURED mutation |
| HR 0.60–0.99 without precision support | assessed, downgrade 0; “excludes the null … precise” | unassessed, `REQUIRES_JUDGEMENT` | MEASURED mutation |
| MD −10 to −0.01 without MID | assessed, downgrade 0 | unassessed, `REQUIRES_JUDGEMENT` | MEASURED mutation |
| HR 0.65–1.00 | both rounding uncertainty and “excludes the null … precise” | unassessed; rounding uncertainty retained, exclusion/precision assertion removed | MEASURED mutation |
| Search: no records/sources, counts 999 | PASS, `RAN_OK 2 of 2` | REFUSED: candidate record sets missing | MEASURED synthetic fixture |
| Independent-extraction tally becomes 999 | old certificate unchanged | evidence digest, rendered-page digest and release digest change | MEASURED mutation of real IV-iron review context |

The explicit-threshold positive control also checks that HR 0.60–0.99 spans a
declared clinical decision boundary and is downgraded despite excluding the null.
Those test thresholds are synthetic; no clinical threshold was inserted into a
real review.

## Deletion family: exact coverage and limitations

`tests/test_deletion_invariant.py` contains the two-topic/six-object family.
These are not twelve successful pristine green-to-red scientific demonstrations.

| Deleted object | Pre-fix evidence | Post-fix route/result for each review |
|---|---|---|
| Endpoint-definition span | Full pre-fix deletion route not measured; no claim of historical PASS | 2 of 2 real-object scratch mutations refused at production `build_review_dir`, specifically for missing endpoint support |
| `grade.domains.indirectness` | Full pre-fix deletion route not measured; missing-information favourable behavior measured separately above | 2 of 2 real-object scratch mutations refused at production build for missing GRADE domain |
| Search denominator | Count-only empty-record artefact passed the old checker | 2 of 2 copied registered candidate artefacts refused by the production search gate; not full review build/replay chains |
| Failed-check receipt | No real failed receipt existed to delete in the input contract | 2 of 2 explicitly synthetic failure supplements refused after deleting the bound receipt; production build called |
| `document_sha256` | Full pre-fix deletion route not measured | 2 of 2 real-object scratch mutations refused at production build for missing document digest |
| Referenced ADJ record | No attached referenced ADJ record map exists in either selected review | 2 of 2 explicitly synthetic ADJ supplements refused by production build after deletion |

Thus 6 of 12 cases delete actual review support through the production build;
4 of 12 use labelled synthetic supplements through that entry point; 2 of 12
exercise the production search gate. Refusal before downstream rendering is
intentional. The tests verify specific refusal reasons rather than accepting any
unrelated exception. A separate synthetic held-search positive control passes
with source/query/raw joins, then refuses after its records file is deleted.

**Not established:** a healthy full build→gate→certificate/census baseline for
both real reviews and every deletion; genuine failed-receipt/ADJ deletions for
both reviews; exhaustive receipts for every legacy checker/nested sensitivity
surface. These are outstanding requirements, not inferred successes.

## Real-evidence verification

Both requested rebuild commands were run with `--now 2026-09-11`.

* IV-iron: rebuild succeeds. Canonical-engine replay receipts are in
  `reproduction.claim_check`, preserving the scientific core and the existing
  replay reconstruction route. An intermediate gate passed after this correction;
  the final gate additionally enforces registered search support.
* GLP-1: rebuild refuses upstream in `envelope.build` →
  `claimgraph.regulatory_fact` → `_held_path`:
  `ValueError: provenance paths must be repository-relative`. These files are
  outside AUD2 edit ownership. Its prior artefacts remain stale and its gate
  refuses; no successful rebuild is claimed.
* Registered search: absent snapshot `records.json` files and measured/current
  search-engine drift. These are MEASURED local evidence gaps. Restoring real
  snapshots is required; no network or substitute records were used.

Final command exits and full output are recorded in
[.tmp/aud2/final-verification.json](.tmp/aud2/final-verification.json) and its
`final-build-iv.txt`, `final-gates.txt`, and `final-tests.txt` sibling logs.
The GLP-1 failure is in [.tmp/aud2/build-glp1.txt](.tmp/aud2/build-glp1.txt).

Final combined targeted verification: **30 of 30 tests passed** (exit 0), covering
deletion, assurance, consumer consistency, receipt exceptions and the browser
contract. Final gates: **0 of 2 PASS** (exit 1). IV-iron's only final refusal is
registered search support; GLP-1 also has stale certificate, replay and typed
transformation failures following its blocked rebuild. The browser used the
local installed Chrome, `127.0.0.1:8000`, blocked
nonlocal requests, checked all four assurance kinds, and verified rendered JSON
equals the downloaded certificate. No browser was installed or globally killed.

Broader legacy tests: **19 of 24 passed; 5 of 24 failed**. The failing assertions
expect automatic precision/denominator assumptions or a count-only search
fixture to pass. Details: [.tmp/aud2/legacy-tests.txt](.tmp/aud2/legacy-tests.txt).
Those existing tests were not edited (ownership permits tests added by this lane).
Scoped `git diff --check` passed. No full-suite, Overmind PASS or release claim.

The requested IV-iron build also regenerated its two blind HTML pages, the
generated review index and blind-map registry through `scripts/build_topic.py`.
These generated outputs are left for integration review alongside its review
bundle; unrelated pre-existing edits were not reset. The bounded verification
loop ended after the final build/gate/test run; missing-source blockers were not
retried indefinitely or bypassed.

## Static versus dynamic disclosure and remaining boundaries

| Item | Static/dynamic | Meaning |
|---|---|---|
| Check IDs, domain names, refusal states | Static | Validation contracts |
| Clinical decision threshold | Dynamic declared input | No default MID/relative-effect threshold supplies missing evidence |
| Check counts, search counts, hashes, replay values | Dynamic | Actual receipts, held records and computation |
| 999, synthetic ADJ and failure receipts | Synthetic test-only | Never written as real scientific evidence |
| Scientific adequacy | Human trust input, explicitly unresolved | Reviewer identity/rationale/scope cannot be replaced by a hash |
| Existing `input_set_version` | Existing numeric-input dependency machinery | Its own implementation was not edited; complete scientific input binding is additional certificate coverage |

Second-pass review: mutations preserve original IDs/dates/estimates except named
test plants; tests use existing member IDs for support joins. This was not an
independent bibliographic/source revalidation of every trial. No scientific
numeric conclusion was promoted. See [STUCK_FAILURES.md](STUCK_FAILURES.md) for
the unresolved integration and coverage work.
