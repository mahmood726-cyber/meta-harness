# LANE GRD2 — correct lane GRD's GRADE fix: a missing clinical threshold must never REMOVE a downgrade. Base 75cc9a46; the GRD tree is at `C:\mh-r-GRD` (read-only for you: read `LANE-GRD-REPORT.md`, its `.tmp/grd/`, and `git -C C:\mh-r-GRD diff`).

Report file: `LANE-GRD2-REPORT.md`. Fresh checkout of main at 75cc9a46. Record `git rev-parse HEAD`. Never reset/checkout/stash.
No commit. No network. Extend `harness/grade.py`, `harness/limitations.py`, `harness/manuscript.py` only (plus tests).

## What GRD got right (keep, re-derive on this tree; its diff is CRLF-polluted -- write LF, never copy its files byte-for-byte)
Missing information is never a favourable rating: `{"pico_scoped": true}` alone => publication bias NOT_ASSESSABLE (fraction None,
no "0 of 0 => 0%"); HR 0.60-0.99 with no threshold is not "precise" (REQUIRES_JUDGEMENT with the missing inputs named); MD with no MID
is not assessed; an interval whose limit sits at the null after rounding is REQUIRES_JUDGEMENT and the text never says both
"uncertain by rounding" and "excludes the null". Every page stays provisional. Its 6 plants (`.tmp/grd/prefix_pytest.txt`).

## What GRD got wrong (MEASURED by the integrator on its tree, 2026-09-19 00:05)
It deleted the default appreciable-effect rule (ratio CI spanning BOTH an appreciable benefit <=0.75 AND an appreciable harm >=1.25,
or reaching an appreciable effect while crossing the null => imprecision downgrade 1). With no registered threshold it now returns
REQUIRES_JUDGEMENT with downgrade 0 -- so five served pages LOST an imprecision downgrade (colchicine-postop-af,
colchicine-secondary-cv-prevention, dapagliflozin-hfpef-hosp, doac-vte-recurrence, metformin-pcos-ovulation: 1 -> 0). That is the
deletion invariant violated inside the fix: missing information became favourable in the other direction. Five existing tests
caught it and GRD reported them as "legacy-contract failures": `tests/test_grade_global_fixes.py::test_genuine_null_cross_still_downgrades`,
`tests/test_stage_additions.py::test_grade_imprecision_not_mechanical_on_tight_null` (the `wide` and `onesidenull` cases),
`::test_grade_imprecision_uses_appreciable_threshold_not_bare_crossing`. Those assert the REQUIREMENT, not the defect. Do not weaken them.

## Required semantics (imprecision, ratio scales; MD/SMD analogous with a registered MID)
1. If the CI crosses the null AND reaches an appreciable effect on either side at the registered threshold -- or, when none is
   registered, at the GRADE default (0.75 / 1.25) -- the domain is ASSESSED with downgrade 1; the basis states which threshold was
   used ("GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered"). A missing registered threshold can
   only make the rating LESS favourable or leave it a judgement, never remove a downgrade the default rule gives.
2. If the CI crosses the null and lies within (0.75, 1.25) ("precision about no effect"): downgrade 0 mechanically, but with no
   registered threshold AND no information-size statement the state is REQUIRES_JUDGEMENT (not "assessed precise").
3. If the CI excludes the null: no mechanical downgrade; with no registered threshold or information-size statement the state is
   REQUIRES_JUDGEMENT naming both; with a registered threshold the CI spans => downgrade 1 (GRD's positive control); with a
   threshold it clears and an adequate information statement => ASSESSED precise.
4. A limit that sits at the null after rounding => REQUIRES_JUDGEMENT, downgrade 0, basis names the rounding; never "excludes the null".
5. Publication bias: a census missing its completed-trial denominator or ongoing/recent inputs => NOT_ASSESSABLE; a COMPLETE
   pico-scoped census with a high ghost fraction still downgrades (update the fixture in
   `test_contaminated_ghost_census_does_not_downgrade` to supply the complete inputs; keep its assertion).
6. `render_certainty` stays provisional while any domain is REQUIRES_JUDGEMENT or NOT_ASSESSABLE; "unassessed never counts as
   favourable" stays true.

## Plants (FIRST on the untouched base, `.tmp/grd2/prefix_pytest.txt`): GRD's six, plus
- corpus invariant `tests/test_grade_missing_is_not_favourable.py::test_no_served_page_loses_a_downgrade`: for every served page,
  every domain's downgrade after rebuild >= before (compare with `git show HEAD:docs/reviews/<slug>/review.json`) -- this is the
  test that would have caught GRD; it must pass after your fix with exactly 0 pages losing a downgrade;
- the five legacy tests above must pass unchanged (except the pubbias fixture completion).

## Then
Rebuild all 32 (`--now 2026-09-11`); table per page: each domain's (downgrade, state) before/after; `python
scripts/retraction_survival.py 75cc9a46` => 32 of 32 or STOP; `python -m pytest tests -q -p no:cacheprovider` full counts
verbatim (no "legacy" bucket: every failure is either fixed or explained as a test that asserts the defect, with the assertion quoted);
list every honest-ratchet block that changes with a proposed reason (unsigned).

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
Never a backslash escape through a heredoc; write regexes to files; LF line endings. No commit.
