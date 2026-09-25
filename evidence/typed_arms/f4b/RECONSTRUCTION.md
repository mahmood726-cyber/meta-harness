# The F4 producer evid2 ran -- how the code tree was reconstructed

evid2 does not own or land the F4 code. To produce DATA that survives `observation_mismatch()` (supplied observations
must equal the producer's own re-extraction), evid2 ran the F4 lane's producer in a scratch worktree. The schema note
says `F4D.patch` is "cumulative against a4e556e3"; it is not applicable to `a4e556e3` alone, so the tree was rebuilt
and the rebuild was checked against the F4 lane's own test results before any output was used.

## Steps (scratch worktree, never committed, never pushed)
1. `git worktree add --detach <scratch> a4e556e3` (sparse: harness/, tests/, scripts/, reproducible_ai/, topics/,
   protocols/, registry/, and cache/<slug>/ without snapshots for the 18 slugs of the held entries).
2. Applied, in order, the F4 lane's prerequisite patches from its artefact directory: `ARM_final.patch`,
   `POOL_F2_F3.patch`, `MASKING.patch`, `REGSPAN.patch` (each `git apply --check` clean first).
3. `F4D.patch` (byte-identical to the canonical copy in the F4 artefact directory -- checked with `cmp`):
   - 8 of its 11 files applied cleanly;
   - `harness/arm_ownership.py`: the whole F4D diff for this file REVERSE-applies, i.e. `ARM_final.patch` already
     produced F4D's post-image; nothing to apply;
   - `harness/pipeline.py`: 5 hunks did not apply; for each, every line it adds is already present in the file
     (checked line by line), i.e. the prerequisites already carry them;
   - `tests/test_arm_ownership.py`: partially applicable; left as the prerequisites produced it (see below).

## Check against the F4 lane's own result
F4 lane (F4D_REPORT.md): 73 of 74 passed, 1 skipped (`test_complete_publication_contract`, publication gate not
reachable in its tree).
Reconstruction: `tests/test_count_observations.py tests/test_f4d.py tests/test_arm_ownership.py` -> **72 passed,
2 failed**, both explained:
- `test_complete_publication_contract`: the publication gate is NOT_REACHED (served `docs/` is not in the sparse tree);
  the producer half of the test matches F4's report exactly -- ORIGINAL 1 row bound, AUTHENTIC_PAIR_SWAP refused
  `ARM_OWNERSHIP_MISMATCH`, WHOLE_CONTRAST_REVERSED refused `CONTRAST_REVERSED_POLICY`.
- `test_rewind_producer_estimate_is_unchanged_and_swap_is_refused`: F4D changes this test's expected refusal code to
  `ARM_OWNERSHIP_MISMATCH`; that hunk is in the part of the test file that did not apply, so the old assertion
  (`ARM_OWNERSHIP_CONTRADICTED`) ran against the new producer. The producer refused the swap, as F4D intends.

## Limit
This is a reconstruction, not the F4 lane's tree. Any observation evid2 supplies must be re-derived by the F4 lane's
own code when it lands; `observation_mismatch()` will refuse it if the two differ, which is the intended protection.

## Note, 2026-09-25 (after the gate review)
The G1-G7 gate was hardened after a fresh-eyes review (11 findings). Re-gating the 18 held extractions under the new
gate changes one state: SMART (balanced crystalloids, 29485925) BOUND -> SET_ASIDE (G6: 'saline' is an active
comparator, so only one direction vote remains). The records in `f4b/records/` are the v1 data and predate the review;
they are superseded by the v2 token witnesses (`../v2/`), where SMART is refused as a derived union anyway.
