# LANE GRD — one defect, one increment on the served harness (base 75cc9a46 = main, increment 2): GRADE turns MISSING information into FAVOURABLE ratings. Missing → NOT_ASSESSABLE / REQUIRES_JUDGEMENT, never a pass. Plants proven pre-fix.

Report file: `LANE-GRD-REPORT.md`. Fresh checkout of main at 75cc9a46. Record `git rev-parse HEAD`. Never reset/checkout/stash.
No commit. No network. Extend `harness/grade.py` (and only the renderers that print its output: `harness/limitations.py::_grade_block`,
`harness/manuscript.py` certainty paragraph, `harness/page.py`) -- existing modules only; no new module. Do NOT change
`grade.render_certainty` semantics beyond what the requirement needs; do not touch the increment-3 arithmetic rule (a provisional
grade prints no downgrade count -- it is already on this base or arriving in the commit above it; keep it).

## The defect (URGENT audit, defect 6; memorandum: missing evidence never becomes a favourable state)
Measured by lane AUD2 on the candidate tree (`C:\mh-r-AUD2\LANE-AUD2-REPORT.md`, "Measured plants" table, and its `harness/grade.py`
diff -- read them, then re-measure on THIS base; do not assume): `{"pico_scoped": true}` alone => `assessed: true`, zero downgrades,
"0% unpublished from 0 of 0"; imprecision calls HR 0.60-0.99 "precise" with no clinical threshold and no information-size assessment;
assesses MD -10 to -0.01 with no MID; for HR 0.65-1.00 says both that null-crossing is uncertain by rounding and that the interval
excludes the null. Each is missing information rendered as a favourable judgement.

## Required end state
1. A domain whose inputs are missing or insufficient is `NOT_ASSESSABLE` (a typed state with the missing input named), never
   "assessed, 0 downgrades". Publication bias with no completed-trial denominator => NOT_ASSESSABLE, never 0%.
2. Imprecision: a decision-relevant "precise" rating needs an explicit clinical threshold (MID / decision boundary) AND an
   information-size statement; absent either => `REQUIRES_JUDGEMENT` (unassessed), with the interval and the missing input named.
   An interval whose bound sits at the null after rounding is `REQUIRES_JUDGEMENT`, and the page never says both "uncertain by
   rounding" and "excludes the null" about the same interval.
3. The overall certainty stays provisional (`render_certainty` PROVISIONAL / not rateable) whenever any domain is NOT_ASSESSABLE or
   REQUIRES_JUDGEMENT; unassessed never counts as favourable (that sentence already renders -- make it true).
4. Every rendered surface (limitations block, manuscript certainty paragraph, page GRADE table) shows the typed states.

## Plants (FIRST, untouched tree; `.tmp/grd/prefix_pytest.txt`) -- `tests/test_grade_missing_is_not_favourable.py`
- `{"pico_scoped": true}` through the production `grade.assess` (or whatever the builder calls -- name it) => not assessed, no
  downgrade count, publication-bias NOT_ASSESSABLE with fraction None (FIRES if assessed/0%);
- HR 0.60-0.99 with no threshold => imprecision REQUIRES_JUDGEMENT (FIRES if "precise");
- MD -10 to -0.01 with no MID => REQUIRES_JUDGEMENT (FIRES if assessed);
- HR 0.65-1.00 => REQUIRES_JUDGEMENT and the rendered text never contains both phrases (FIRES if both);
- positive control: HR 0.60-0.99 WITH an explicit synthetic threshold (say 0.90) that the CI spans => downgraded for imprecision
  despite excluding the null; WITH a threshold the CI clears and an information-size statement => assessed precise (HOLDS/ FIRES
  as measured -- report which).
Record FIRED / HELD per case. A fix that clears every failure is a loosened test: re-read each assertion after the fix.

## Then
- rebuild all 32 (`--now 2026-09-11`); table of every page's GRADE domain states before/after and its certainty word before/after --
  a certainty that RISES anywhere is a defect in your fix (report it, do not ship it); record which `review_sha256`/`html_sha256`
  moved;
- `python scripts/retraction_survival.py 75cc9a46` => 32 of 32 or STOP;
- targeted pytest (`-k "grade or limitation or manuscript or residue"`) counts; `python scripts/verify_all.py` if time allows; list
  every honest-ratchet block that changes with a proposed acknowledgement reason (do not sign).

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
Plants pre/post; the 32-page domain-state table; diff summary; what this increment does NOT establish. Never a backslash escape
through a heredoc; write regexes to files. No commit.
