# LANE EN2 Report

## 1. What Was Wrong, Mechanism, Files

MEASURED from pre-fix review objects at `aa8ed28a`: endpoint keys were too generic on DOAC VTE and NOAC AF (`Endpoint = composite`), too narrow on SGLT2 CKD (`CKD progression / kidney composite outcome` while trial-defined composites include cardiovascular death), mixed HR/RR labels were displayed as a single clean HR label, trial literal analysis sets were promoted to ITT, and metformin PCOS collapsed an add-on clomifene contrast into a generic "metformin vs placebo" headline.

Implemented mechanism:
- `harness/endpoint_canonical.py`: canonical endpoint object, mixed-label effect label, analysis-set superclass, and diagnostics for the lane plants.
- `harness/compat.py`, `harness/pipeline.py`, `harness/page.py`: stamps/renders endpoint canonical objects, effect constituent labels, literal analysis-set superclass, treatment strategy, dose, and run-in dimensions.
- Topic/cache docs updated for the seven named topics; generated review pages rebuilt.
- Strand artifacts added:
  - `docs/sglt2_ckd_strands.json`: kidney-only HR strand computed from cached values: MEASURED `0.651079 (0.481802-0.87983)`, tau2 `0.00630994`.
  - `docs/sglt2_primary_prevention_hf_strands.json`: no-baseline-HF strand is `NOT_IN_COMMITTED_SOURCE`.
  - `docs/metformin_pcos_strands.json`: non-served metformin strategies declared empty.

Sweep result in `docs/endpoint_canonical_sweep.json`: MEASURED `key_over_claims = 0 of 44 outcomes`, `key_under_claims = 0 of 44 outcomes`. The sweep still records 3 corpus-wide `LABEL_HIDES_MIX` diagnostics outside this lane; they are not endpoint over/under claims.

Static-vs-dynamic disclosure:

| Item | Status | Source |
| --- | --- | --- |
| Endpoint component mappings | Static code rules | Derived from committed row `components` / named lane source facts |
| Kidney-only SGLT2 strand | Dynamic computed | Cached HR+CI values, pooled with `harness.synth.pool` |
| No-baseline-HF subgroup strand | Fail-closed | Marked `NOT_IN_COMMITTED_SOURCE`; no subgroup pool computed |
| Run-in counts | Reported evidence note | LoDoCo2 1006/6528 stated in report; rendered row flag avoids manuscript-number leakage |
| Pooling arithmetic | Unchanged | Existing pipeline/synth output |

## 2. Plants

New file: `tests/test_endpoint_canonical.py`.

Plant assertions:
- `test_doac_endpoint_underclaim_and_live_fix`: pre-fix `assert "KEY_UNDER_CLAIMS" in _codes(pre, "doac-vte-recurrence")`; post-fix `assert live["compat_key"]["endpoint"] == "SYMPTOMATIC_RECURRENT_VTE"` and no under-claim.
- `test_sglt2_ckd_endpoint_overclaim_and_live_fix`: pre-fix `assert "KEY_OVER_CLAIMS" in _codes(pre, "sglt2-ckd-progression")`; post-fix endpoint label is `TRIAL_DEFINED_PRIMARY_CARDIORENAL_COMPOSITE` with no over-claim.
- `test_mixed_effect_label_plant_and_live_labels`: pre-fix DOAC/NOAC assert `LABEL_HIDES_MIX`; post-fix labels are `pooled first-event ratio (5 HR + 1 RR)` and `pooled first-event ratio (3 HR + 1 RR)`.
- `test_analysis_set_superclass_plant_and_literal_retention`: pre-fix DOAC asserts `ANALYSIS_SET_PROMOTED`; post-fix compatibility key uses `RANDOMIZED_OR_FULL_ANALYSIS_SET` and Hokusai retains `mITT`.
- `test_metformin_strategy_split_plant_and_live_fix`: pre-fix asserts `STRATEGY_COLLAPSED`; post-fix pooled rows have only `METFORMIN_ADDON_CC`.
- `test_matched_rows_control_no_violation`: matched synthetic rows assert `EC.diagnose(...) == []`.

MEASURED plant output:

```text
python -m pytest tests\test_endpoint_canonical.py -q
......                                                                   [100%]
6 passed in 6.69s
```

## 3. Rebuilt Pages / Reworded Blocks

MEASURED rebuilt/replayed topics:
- `doac-vte-recurrence`: primary outcome renamed from `Trial-reported recurrent VTE composite` to `Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)`; compatibility endpoint now `SYMPTOMATIC_RECURRENT_VTE`; effect label now `pooled first-event ratio (5 HR + 1 RR)`; analysis set now superclass with literals retained. Pooled number unchanged: `k=6`, `0.9092 (0.7478-1.1054)`, tau2 `0.0`.
- `noac-vs-warfarin-af-stroke`: compatibility endpoint now `STROKE_OR_SYSTEMIC_EMBOLISM`; dose key `standard_dose`; effect label now `pooled first-event ratio (3 HR + 1 RR)`. Pooled number unchanged: `k=4`, `0.8069 (0.6611-0.985)`, tau2 `0.00741`.
- `sglt2-ckd-progression`: title/question/outcome now say trial-defined primary cardiorenal composite; endpoint canonical status `HETEROGENEOUS_DECLARED`; kidney-only strand added. Pooled primary unchanged: `k=3`, `0.6836 (0.5537-0.844)`, tau2 `0.00134`.
- `sglt2-primary-prevention-hf`: title/question now state mixed CVOT populations with and without baseline HF; no-baseline-HF strand declared `NOT_IN_COMMITTED_SOURCE`. Pooled number unchanged: `k=4`, `0.6956 (0.5763-0.8397)`, tau2 `0.0`.
- `colchicine-secondary-cv-prevention`: primary outcome now `Trial-defined major coronary/cardiovascular composite`; LoDoCo2 row has `run_in_enrichment=active_run_in_gi_intolerance_enriched` (evidence note: 1006 of 6528 excluded before randomisation, mostly GI intolerance). Pooled number unchanged: `k=3`, `0.8134 (0.5074-1.3039)`, tau2 `0.02669`.
- `esketamine-trd-madrs`: primary outcome now `Observed-case Day-28 raw change-score MADRS MD`; analysis-set superclass/literals retained. Pooled number unchanged: `k=4`, MD `-3.3445 (-6.0701--0.6189)`, tau2 `0.0`.
- `metformin-pcos-ovulation`: title/question/outcome now explicitly name metformin added to clomifene vs clomifene plus placebo; pooled rows carry `METFORMIN_ADDON_CC` and clomifene status. Pooled number unchanged: `k=3`, OR `2.0733 (0.0922-46.6008)`, tau2 `1.15872`.
- `probiotics-aad-prevention`: rebuilt because the pipeline now stamps canonical endpoint objects during replay; no lane content change intended. Replay passed.

All named topic replays passed. Example final replay outputs were `OK <slug>` and `1/1 reproduce (all reproducible)` for each of: DOAC VTE, NOAC AF, SGLT2 CKD, SGLT2 HF, colchicine secondary, esketamine, metformin, and probiotics.

## 4. Tests

MEASURED:

```text
python -m py_compile harness\endpoint_canonical.py harness\compat.py harness\pipeline.py harness\page.py scripts\endpoint_canonical_sweep.py tests\test_endpoint_canonical.py
# exit 0
```

```text
python -m pytest tests\test_endpoint_canonical.py -q
6 passed in 6.69s
```

```text
python -m pytest tests\test_compat_key.py -q
10 passed in 3.67s
```

```text
python -m pytest tests -q
722 passed in 967.71s (0:16:07)
```

Focused stale-artifact rerun before the final full pass:

```text
6 passed in 544.17s (0:09:04)
```

## 5. What I Did Not Do

- Did not commit.
- Did not add/remove pooled trials.
- Did not change pooling arithmetic, search, screening, harms extraction, or estimator code.
- Did not compute a no-baseline-HF SGLT2 subgroup from incomplete cache data; it is marked `NOT_IN_COMMITTED_SOURCE`.
- Did not write ratchet acknowledgements; reworded blocks are listed above for integrator signing.
- Did not run network fetches. Builds used committed cache.

## 6. Files Changed or Added

Changed:
- `cache/colchicine-secondary-cv-prevention/verified_effects.json`
- `cache/esketamine-trd-madrs/verified_arms.json`
- `cache/metformin-pcos-ovulation/verified_arms.json`
- `cache/sglt2-ckd-progression/verified_effects.json`
- `docs/error_rate.json`
- `docs/error_rate_sample.json`
- `docs/evidence/override-audit-2026-09-14/overrides.json`
- `docs/fix_ledger.json`
- `docs/index.html`
- `docs/m/m24cd09bc/index.html`
- `docs/m/m250220c2/index.html`
- `docs/m/m28cd9b74/index.html`
- `docs/m/m42da3313/index.html`
- `docs/m/m586876fa/index.html`
- `docs/m/m595c5e9f/index.html`
- `docs/m/m6c992fd1/index.html`
- `docs/m/m87167438/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/mabc6654a/index.html`
- `docs/m/maf69923c/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/me79cb3b0/index.html`
- `docs/reviews/colchicine-secondary-cv-prevention/REPRODUCTION.json`
- `docs/reviews/colchicine-secondary-cv-prevention/index.html`
- `docs/reviews/colchicine-secondary-cv-prevention/manifest.json`
- `docs/reviews/colchicine-secondary-cv-prevention/review.json`
- `docs/reviews/doac-vte-recurrence/REPRODUCTION.json`
- `docs/reviews/doac-vte-recurrence/index.html`
- `docs/reviews/doac-vte-recurrence/manifest.json`
- `docs/reviews/doac-vte-recurrence/review.json`
- `docs/reviews/esketamine-trd-madrs/REPRODUCTION.json`
- `docs/reviews/esketamine-trd-madrs/index.html`
- `docs/reviews/esketamine-trd-madrs/manifest.json`
- `docs/reviews/esketamine-trd-madrs/review.json`
- `docs/reviews/metformin-pcos-ovulation/REPRODUCTION.json`
- `docs/reviews/metformin-pcos-ovulation/index.html`
- `docs/reviews/metformin-pcos-ovulation/manifest.json`
- `docs/reviews/metformin-pcos-ovulation/review.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/REPRODUCTION.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/index.html`
- `docs/reviews/noac-vs-warfarin-af-stroke/manifest.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/review.json`
- `docs/reviews/probiotics-aad-prevention/REPRODUCTION.json`
- `docs/reviews/probiotics-aad-prevention/index.html`
- `docs/reviews/probiotics-aad-prevention/manifest.json`
- `docs/reviews/probiotics-aad-prevention/review.json`
- `docs/reviews/sglt2-ckd-progression/REPRODUCTION.json`
- `docs/reviews/sglt2-ckd-progression/index.html`
- `docs/reviews/sglt2-ckd-progression/manifest.json`
- `docs/reviews/sglt2-ckd-progression/review.json`
- `docs/reviews/sglt2-primary-prevention-hf/REPRODUCTION.json`
- `docs/reviews/sglt2-primary-prevention-hf/index.html`
- `docs/reviews/sglt2-primary-prevention-hf/manifest.json`
- `docs/reviews/sglt2-primary-prevention-hf/review.json`
- `harness/compat.py`
- `harness/page.py`
- `harness/pipeline.py`
- `registry/blind_map.json`
- `tests/test_estimand_naming.py`
- `topics/colchicine-secondary-cv-prevention.json`
- `topics/doac-vte-recurrence.json`
- `topics/esketamine-trd-madrs.json`
- `topics/metformin-pcos-ovulation.json`
- `topics/noac-vs-warfarin-af-stroke.json`
- `topics/sglt2-ckd-progression.json`
- `topics/sglt2-primary-prevention-hf.json`

Added:
- `LANE-EN2-REPORT.md`
- `docs/endpoint_canonical_sweep.json`
- `docs/metformin_pcos_strands.json`
- `docs/sglt2_ckd_strands.json`
- `docs/sglt2_primary_prevention_hf_strands.json`
- `harness/endpoint_canonical.py`
- `scripts/endpoint_canonical_sweep.py`
- `tests/test_endpoint_canonical.py`

Untracked lane input/log files left untouched:
- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
