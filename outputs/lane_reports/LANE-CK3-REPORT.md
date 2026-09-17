# LANE CK3 REPORT

## 1. What was wrong, mechanism, files

The compatibility key had one direction of sight: it could disclose or suppress incompatibility, but it did not record whether the page/key was wrong because it overstated homogeneity or because a warning overstated heterogeneity. I added `harness/compat_direction.py`, attached its per-dimension `key_direction` rows in `harness/pipeline.py`, rendered them in `harness/page.py`, and wrote `scripts/compat_direction_sweep.py` to emit `docs/compat_direction_sweep.json`.

Mechanism:
- Per dimension, derive per-trial underlying values from explicit trial annotations, source-span cues, and narrow lane source facts.
- Compare the underlying values with the compatibility key and endpoint-specific rendered warnings.
- Emit exactly one of `ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS`, `ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS`, `CONSISTENT`, or `NOT_DERIVABLE`.
- Explicit endpoint definitions now drive composite-heterogeneity wording before the older source-window heuristic in `harness/extract.py`.

Static-vs-dynamic disclosure:

| Item | Source | Status |
|---|---|---|
| `compat_direction` classification | computed from live review objects | dynamic |
| Per-trial annotations in topic JSON | source-backed lane facts copied into trial rows | static, disclosed |
| Fallback facts in `harness/compat_direction.py` | narrow pre-fix plant support for named lane pages | static, disclosed in basis strings |
| Pooling estimates, membership, screening | existing harness outputs | unchanged |

## 2. Plants

`test_finerenone_underclaim_plant_and_rebuilt_consistent`
- Pre-fix assertion: committed `ad5e7c66` page sentence includes `component sets differ across trials` and `40% eGFR-decline threshold`; direction is `ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS`.
- Post-fix assertion: live direction is `CONSISTENT`; underlying values are `KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH`; no `composite_heterogeneity` remains.

`test_spironolactone_effect_model_not_derivable_without_rales_cox_span`
- Pre-fix assertion: RALES source span says `relative risk of death, 0.70` but does not say `Cox` or `proportional-hazards`.
- Output/class: `NOT_DERIVABLE`, missing `10471456`; I did not change `harness/estmeasure.py`. Integrator line if a model class is later desired: `harness/estmeasure.py:34` (`_CLASS`) plus the Cox note at `harness/estmeasure.py:47`.

`test_colchicine_postop_overclaim_fires_on_endpoint_and_analysis_set`
- Pre-fix assertion: endpoint values are `POAF_5_MIN`, `POAF_GE_5_MIN`, `POAF_GE_30_SEC`, `POAF_GE_10_MIN`; analysis values are `AVAILABLE_CASE`, `INTENTION_TO_TREAT`.
- Output/class: both dimensions fire as `ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS`.

`test_synthetic_controls_for_all_key_direction_classes`
- Covers all four classes: over-claim, under-claim, consistent, and not-derivable.

Plant output:
- `python -m pytest tests\test_compat_direction.py -q`
- `5 passed in 2.32s`

## 3. Rebuilt Pages And Changed Blocks

Measured HTML bytes:
- `finerenone-ckd-t2d-renal`: 80482 -> 80917 (+435). Before: false composite warning `component sets differ...40% eGFR-decline threshold`. After: no composite warning; audit row `CONSISTENT` with `KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH`. Primary result unchanged: k=2, estimate 0.8407.
- `doac-vte-recurrence`: 155663 -> 156506 (+843). Before: comparator note said `small outcome-definition difference`. After: note says all six rows share `SYMPTOMATIC_RECURRENT_VTE`; audit row endpoint `CONSISTENT`, analysis set over-claim `INTENTION_TO_TREAT`, `MODIFIED_INTENTION_TO_TREAT`. Primary result unchanged: k=6, 0.9092 (0.7478-1.1054).
- `noac-vs-warfarin-af-stroke`: 87763 -> 88437 (+674). After: audit row `CONSISTENT` with `STROKE_OR_SYSTEMIC_EMBOLISM`. Primary result unchanged: k=4, 0.8069 (0.6611-0.985).
- `balanced-crystalloids-vs-saline-mortality`: 102407 -> 102858 (+451). Before: key timepoint `28-90 day or in-hospital`. After: audit row under-claim with shared `90_DAY_MORTALITY`. Primary result unchanged: k=2, 0.9774.
- `colchicine-postop-af`: 102814 -> 104002 (+1188). After: audit rows show endpoint over-claim (`POAF_5_MIN`, `POAF_GE_5_MIN`, `POAF_GE_30_SEC`, `POAF_GE_10_MIN`), follow-up consistent heterogeneous (`INDEX_ADMISSION`, `IN_HOSPITAL`, `30_DAY`), and analysis-set over-claim (`AVAILABLE_CASE`, `INTENTION_TO_TREAT`). Primary result unchanged: k=4, 0.6735 (0.376-1.2067).
- `pcsk9-mace`: 70888 -> 71588 (+700). Before: generic composite warning. After: warning names endpoint definitions `CHD_DEATH | MI | ISCHEMIC_STROKE | UNSTABLE_ANGINA_HOSPITALIZATION` vs `CV_DEATH | MI | STROKE | UNSTABLE_ANGINA_HOSPITALIZATION | CORONARY_REVASCULARIZATION`; audit row over-claim. Primary result unchanged: k=2, 0.85.
- `sglt2-ckd-progression`: 93496 -> 94489 (+993). Before: generic varying components. After: warning names all three endpoint definitions; audit row over-claim. Primary result unchanged: k=3, 0.6836 (0.5537-0.844).
- `semaglutide-obesity-weight`: 129071 -> 129702 (+631). After: audit row over-claim on `background_lifestyle_intensity`: `INTENSIVE_BEHAVIORAL_THERAPY_30_VISITS_LOW_CALORIE_DIET` vs `STANDARD_LIFESTYLE_INTERVENTION_STEP1`. Primary result unchanged: k=2, -11.8449.
- `spironolactone-hfref-mortality`: 136350 -> 136934 (+584). After: trial rows preserve source labels; effect-model class audit is `NOT_DERIVABLE` because RALES held span does not state Cox/proportional hazards. Primary result unchanged: k=3, 0.8685 (0.3062-2.4635).

Sweep output in `docs/compat_direction_sweep.json`:
- `10 (page, dimension) over-claiming of 19 derivable`
- `1 (page, dimension) under-claiming of 19 derivable`
- `4 NOT_DERIVABLE of 23`

## 4. Tests

- `python -m py_compile harness\compat_direction.py scripts\compat_direction_sweep.py tests\test_compat_direction.py` passed.
- Replayed all nine rebuilt pages with `python scripts/reproduce_review.py <slug>`; each printed `1/1 reproduce (all reproducible)`.
- `python -m pytest tests\test_fixstate.py::test_real_store_validates tests\test_compat_direction.py -q`: `6 passed in 287.52s (0:04:47)`.
- `python -m pytest tests\test_compat_direction.py -q`: `5 passed in 2.32s`.
- `python -m pytest tests -x -q`: `721 passed in 599.41s (0:09:59)`.

## 5. What I Did Not Do

- Did not commit, stage, stash, checkout, reset, clean, push, or touch `.git`.
- Did not change pooling, membership, screening, search, or `harness/synth.py`.
- Did not force spironolactone RALES into `TIME_TO_FIRST_DEATH_COX_RATIO`; the held RALES span lacks Cox/proportional-hazards language, so the class is reported as `NOT_DERIVABLE`.
- Did not rebuild unrelated sweep-hit pages (`colchicine-secondary-cv-prevention`, `dpp4-mace-t2d`, `glp1-ra-mace-t2d`, `sglt2-hfref-hosp-cvdeath`, etc.); they are named by the sweep for integrator triage.

## 6. Files Changed Or Added

Added:
- `harness/compat_direction.py`
- `scripts/compat_direction_sweep.py`
- `tests/test_compat_direction.py`
- `docs/compat_direction_sweep.json`
- `LANE-CK3-REPORT.md`

Changed source/config:
- `harness/extract.py`
- `harness/page.py`
- `harness/pipeline.py`
- `topics/balanced-crystalloids-vs-saline-mortality.json`
- `topics/colchicine-postop-af.json`
- `topics/doac-vte-recurrence.json`
- `topics/finerenone-ckd-t2d-renal.json`
- `topics/noac-vs-warfarin-af-stroke.json`
- `topics/pcsk9-mace.json`
- `topics/semaglutide-obesity-weight.json`
- `topics/sglt2-ckd-progression.json`
- `topics/spironolactone-hfref-mortality.json`

Changed generated artifacts:
- `docs/fix_ledger.json`
- `registry/blind_map.json`
- `docs/reviews/{balanced-crystalloids-vs-saline-mortality,colchicine-postop-af,doac-vte-recurrence,finerenone-ckd-t2d-renal,noac-vs-warfarin-af-stroke,pcsk9-mace,semaglutide-obesity-weight,sglt2-ckd-progression,spironolactone-hfref-mortality}/REPRODUCTION.json`
- `docs/reviews/{balanced-crystalloids-vs-saline-mortality,colchicine-postop-af,doac-vte-recurrence,finerenone-ckd-t2d-renal,noac-vs-warfarin-af-stroke,pcsk9-mace,semaglutide-obesity-weight,sglt2-ckd-progression,spironolactone-hfref-mortality}/index.html`
- `docs/reviews/{balanced-crystalloids-vs-saline-mortality,colchicine-postop-af,doac-vte-recurrence,finerenone-ckd-t2d-renal,noac-vs-warfarin-af-stroke,pcsk9-mace,semaglutide-obesity-weight,sglt2-ckd-progression,spironolactone-hfref-mortality}/manifest.json`
- `docs/reviews/{balanced-crystalloids-vs-saline-mortality,colchicine-postop-af,doac-vte-recurrence,finerenone-ckd-t2d-renal,noac-vs-warfarin-af-stroke,pcsk9-mace,semaglutide-obesity-weight,sglt2-ckd-progression,spironolactone-hfref-mortality}/review.json`
- `docs/m/m3c1155fb/index.html`
- `docs/m/m5b3fd56c/index.html`
- `docs/m/m5e5590d5/index.html`
- `docs/m/m87167438/index.html`
- `docs/m/m89f8021b/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/mb6ceb13c/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/mf6cd36c2/index.html`
