# LANE DEL2 — land the deletion-invariant family (lane DEL, base 237e9094) on the served harness (base ca63b7cf) WITHOUT the git-snapshot check, with the verified-effect case restated as the invariant actually requires.

Report file: `LANE-DEL2-REPORT.md`. Fresh checkout of main at ca63b7cf. Record `git rev-parse HEAD`. Never reset/checkout/stash. No commit.
No network. Extend `harness/census.py` (and only what the cases need) -- existing modules only.

## Source
Lane DEL's tree is parked at `F:\claude-temp\lanes-parked\mh-r-DEL` (read `LANE-DEL-REPORT.md`, `tests/test_deletion_invariant.py`, and
`git -C F:\claude-temp\lanes-parked\mh-r-DEL diff -- harness`). Its `harness/census.py` change (+21: typed refusals MISSING_ENDPOINT_SUPPORT
/ MISSING_GRADE_DOMAIN; the standing REPRODUCTION_RETRACTION limitation restored before hashing and rendering) is harvestable.
Its `harness/verified_inputs.py` change (+23: compare the working verified_effects.json with `git show HEAD:` of the same file) is NOT:
a build must not depend on `.git` being present (exported trees, CI artefacts), and it only guards uncommitted deletions -- a
committed deletion passes it. Drop it.

## The verified-effect case, restated
Deleting a trial's verified (hand-transcribed) effect must never IMPROVE assurance. On this base the pipeline may re-supply the same
trial from a lower-ranked route (abstract extraction, registry). That is not an assurance improvement IF the row now carries the
lower route's provenance/rank and its binding (`endpoint_binding`, `admissibility`) is re-derived and rendered -- and it IS a
defect if the row keeps `provenance: verified` / the hand-verified label, or if the pooled k and estimate are unchanged with no
provenance change. Assert exactly that: after deletion, for that trial either (a) it is absent from the pool (k falls) or (b) its row's
provenance rank is strictly lower than before and the served page shows the new provenance; never (c) identical row. Same for
`sacubitril-valsartan-hfref` (S) and `glp1-ra-mace-t2d` (G).

## Plants (FIRST, untouched base; `.tmp/del2/prefix_pytest.txt`) -- `tests/test_deletion_invariant.py` re-derived for this base
The 12 cases of DEL (2 topics x 6 objects: endpoint_definition_span, endpoint_result_span, grade domain, verified effect, registered
search candidate file (standalone gate), REPRODUCTION_RETRACTION limitation) through the production route named in DEL's report
(`pipeline.build_review_core` -> `census.build_review_dir(..., certify=True)`). Record FIRED / HELD / NOT_CONSTRUCTIBLE per case on
THIS base (do not copy DEL's table: measure). A fix that clears every failure is a loosened test.

## Then
Rebuild the two topics (`--now 2026-09-11`) and report hash movement (expected none: the fix refuses mutations, it does not change
served pages); `python -m pytest tests -q -p no:cacheprovider -k "deletion or census or verified"` counts, then the full suite if
time allows (counts verbatim); `python scripts/retraction_survival.py ca63b7cf` => 32 of 32 or STOP.

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
The 12-case table on this base, diff summary, what the increment does NOT establish. Never a backslash escape through a heredoc; write
regexes to files; LF line endings. No commit.
