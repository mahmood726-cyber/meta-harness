# LANE CK3 — the assert-vs-underlying compatibility sweep must run in BOTH directions and report them separately: a key that overstates homogeneity is a defect, and a warning that overstates incompatibility is a defect too. Four pages now under-claim their own compatibility.

Report file: `LANE-CK3-REPORT.md`. Base `ad5e7c66`. Lane CK's `harness/compat_check.py` (assert-vs-underlying sweep) is NOT in your clone (integrator holds `CK.patch`); lane EN's dimensions and `components` ARE (`harness/compat*.py`, `LANE-EN-REPORT.md`); EN2 and CK2 run concurrently (canonical endpoints both ways; eligibility chain). Build `harness/compat_direction.py` additively; name fields exactly: `key_direction ∈ {ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS, ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS, CONSISTENT, NOT_DERIVABLE}` per dimension per page.

## Under-claim cases (the key/warning says "differs" where the underlying values are the same; CLAIMED until re-measured from cached text)
1. doac-vte-recurrence: `SYMPTOMATIC_RECURRENT_VTE` is the shared canonical endpoint (EN2 case) — the page warns of endpoint heterogeneity.
2. noac-vs-warfarin-af-stroke: stroke or systemic embolism is the shared primary across the four trials — warned as differing.
3. spironolactone-hfref-mortality: RALES's "relative risk 0.70 (0.60–0.82)" is from a Cox model, i.e. a hazard ratio; EMPHASIS HR; J-EMPHASIS HR 1.77 (0.81–3.87) once corrected → all three are `TIME_TO_FIRST_DEATH_COX_RATIO`. Introduce that compatibility class, preserve each source's literal label (`source_label: "relative risk"`, `class: HR`). Coordinate with OC's estimand classes (`harness/estmeasure.py`, read-only for you: add the class only if a mapping hook exists; otherwise report the exact line the integrator must change).
4. finerenone-ckd-t2d-renal: page says "component sets differ across trials, including the 40% eGFR-decline threshold"; both use `KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH` (FIDELIO primary, FIGARO first secondary). Render the literal shared enumeration.

## Over-claim cases (key says single/homogeneous where the values differ — CK's original direction; re-measure on this base)
colchicine-postop-af `follow_up_window`, `analysis_set` (ITT over available-case rows), `endpoint_definition` (5 min / ≥5 min / ≥30 s / ≥10 min); pcsk9 `Endpoint = composite` over 5-, 4-component primaries; Hokusai mITT under ITT; sglt2-ckd cardiorenal vs kidney-only.

## Build
1. Per dimension, derive the underlying per-trial values from cached text (EN's extractors) and compare with the asserted key AND with any rendered heterogeneity warning; classify the direction. Where the underlying values cannot be derived → `NOT_DERIVABLE(dimension, trials)`, never a verdict.
2. Plants (pre-fix `ad5e7c66`): `tests/test_compat_direction.py` — finerenone under-claim fires (quote the page sentence pre-fix; post-fix `CONSISTENT` with the literal enumeration); spironolactone RR/HR class under-claim → `TIME_TO_FIRST_DEATH_COX_RATIO` (assert that the RALES span says "Cox" or "proportional-hazards" in held text — if it does not, the class is `NOT_DERIVABLE` and you say so); colchicine-postop over-claim fires; synthetic controls for each of the four classes.
3. Sweep `scripts/compat_direction_sweep.py` → `docs/compat_direction_sweep.json`: `n (page, dimension) over-claiming of N derivable` and `n under-claiming of N derivable`, reported SEPARATELY, pages named; `n NOT_DERIVABLE of N`.
4. Rebuild affected pages; replay; list reworded blocks.

Do not touch: pooling, membership, screening, search, `harness/synth.py`. No network.
