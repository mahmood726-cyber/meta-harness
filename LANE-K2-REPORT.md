# LANE K2 REPORT

All counts, page values, test outputs, and file lists below are tagged as `[MEASURED]` when read from this clone or command output, `[INFERRED]` when derived from those measured objects, and `[CLAIMED]` when they come from the lane brief rather than a fresh measurement.

## 1. What was wrong, mechanism, files

- `[CLAIMED]` The registered interval is Paule-Mandel `tau^2` plus HKSJ on `t(k-1)`; at `k=2`, this is `t(1)=12.71`, the same single-degree-of-freedom mechanism already used to refuse prediction intervals.
- `[MEASURED]` At `aa8ed28a`, `docs/reviews/*/review.json` contained `10 of 32` primary outcomes with `result.k == 2`; `9 of 10` served a primary pooled CI or pooled row. The exception was `iv-iron-hfref-hosp`, already `suppressed_incompatible: true` with no estimate and no CI, so it was not one of the `9 of 10` served primary k=2 pages.
- `[MEASURED]` `ticagrelor-vs-clopidogrel-acs` served a pooled HR `1.0479 [0.0324, 33.8921]` even though PLATO was HR `0.84 [0.77, 0.92]` and PHILO was HR `1.47 [0.88, 2.44]`; the rebuilt object computes Q-derived `I^2=77.7%` and refuses the pooled row.
- `[INFERRED]` The old claim surfaces treated a refused or unreliable k=2 HKSJ interval as a normal claim object, so manuscript/index/GRADE language could say "crosses the null", "non-significant", or imprecision based on the quarantined interval.
- `[INFERRED]` GRADE inconsistency had been using prediction-interval availability as a proxy; because prediction intervals are absent at k=2, it could convert "not computable" into "no inconsistency detected".
- `[CLAIMED]` I chose the lane's material heterogeneity rule as `tau^2 > 0` and `I^2 > 25%`. `[CLAIMED]` The automatic k=2 inconsistency alert uses the lane's `I^2 > 50%` threshold or direction conflict.

Files involved in the fix:

- `[MEASURED]` `harness/k2.py` centralizes typed k=2 refusal checks, direction-conflict diagnostics, Q-derived `I^2`, and common-effect caveat rules.
- `[MEASURED]` `harness/pipeline.py` applies the k=2 policy after pooling, preserves the unserved HKSJ interval under `ci_hksj_unserved`, skips leave-one-out when a pool is refused, and does not call RoB sensitivity on refused k=2 results.
- `[MEASURED]` `harness/claim.py`, `harness/grade.py`, `harness/page.py`, `harness/manuscript.py`, `harness/limitations.py`, `harness/spec_curve.py`, and `harness/index.py` route refused k=2 objects through no-pooled-claim/no-pool states rather than recomputing significance.
- `[MEASURED]` `topics/ticagrelor-vs-clopidogrel-acs.json` names PLATO as the pre-specified k=1 anchor and PHILO as the named remainder when the k=2 pool is refused.

## 2. Plant checks

Plant command:

```text
[MEASURED] python -m pytest tests/test_k2_refusal.py tests/test_claim_object.py tests/test_grade_global_fixes.py tests/test_stage_additions.py -x -q
[MEASURED] 45 passed in 14.13s
```

The plant reads pre-fix page objects with read-only `git show aa8ed28a:docs/reviews/<slug>/review.json`.

### Corticosteroids primary k=2 CI served before, refused after

Exact assertion:

```python
assert pre["k"] == 2 and pre["ci_low"] == 0.0361 and pre["ci_high"] == 8.2605
assert k2.k2_check(pre) == k2.K2_SINGLE_DF_CI_SERVED
assert live["k"] == 2 and live["ci_low"] is None and live["ci_high"] is None
assert live["pooled_ci_refused"]["code"] == k2.K2_SINGLE_DF
assert live["ci_hksj_unserved"]["ci_low"] == 0.0361
assert k2.k2_check(live) is None
```

Quoted outputs:

- `[MEASURED]` pre-fix `k=2`, `ci_low=0.0361`, `ci_high=8.2605`, `k2_check=K2_SINGLE_DF_CI_SERVED`.
- `[MEASURED]` post-fix `k=2`, `ci_low=None`, `ci_high=None`, `pooled_ci_refused.code=K2_SINGLE_DF`, `ci_hksj_unserved.ci_low=0.0361`, `k2_check=None`.

### Ticagrelor direction conflict before, pooled row refused after

Exact assertion:

```python
assert k2.k2_check(pre_o["result"], pre_o["trials"]) == k2.DIRECTION_CONFLICT_K2
assert live["pool_refused"]["code"] == k2.DIRECTION_CONFLICT_K2
assert live.get("estimate") is None and live.get("ci_low") is None and live.get("ci_high") is None
assert live["pool_refused"]["honest_k1_anchor"]["name"] == "PLATO"
assert [x["label"] for x in live["pool_refused"]["named_remainders"]] == ["PHILO"]
assert "Pooled result REFUSED" in html and "Honest k=1 anchor" in html
assert "PLATO" in html and "PHILO" in html
```

Quoted outputs:

- `[MEASURED]` pre-fix `k2_check=DIRECTION_CONFLICT_K2`.
- `[MEASURED]` post-fix `pool_refused.code=DIRECTION_CONFLICT_K2`, `estimate=None`, `ci_low=None`, `ci_high=None`, honest k=1 anchor `PLATO`, named remainder `PHILO`, rendered text contains `Pooled result REFUSED` and `Honest k=1 anchor`.

### Ticagrelor GRADE inconsistency missing before, state present after

Exact assertion:

```python
assert pre_inc["downgrade"] == 0 and pre_inc["assessed"] is True
assert k2.k2_grade_check(_primary(pre)["result"], pre_inc) == k2.INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY
assert live_inc["not_assessable_automatically"] is True
assert live_inc["assessed"] is False
assert k2.k2_grade_check(_primary(live)["result"], live_inc) is None
```

Quoted outputs:

- `[MEASURED]` pre-fix GRADE inconsistency `downgrade=0`, `assessed=True`; `k2_grade_check=INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY`.
- `[MEASURED]` post-fix `not_assessable_automatically=True`, `assessed=False`, `k2_grade_check=None`.

### Synthetic k>=3 unchanged

Exact assertion:

```python
assert res["k"] == 3 and res["ci_low"] is not None and res["ci_high"] is not None
assert "pooled_ci_refused" not in res and k2.k2_check(res) is None
```

Quoted output:

- `[MEASURED]` synthetic k=3 output: `{'k': 3, 'estimate': 0.8005, 'ci_low': 0.652, 'ci_high': 0.9828, 'pooled_ci_refused': None} check None`.

### Synthetic k=2 concordant refusal and caveat threshold

Exact assertion:

```python
assert res["ci_low"] is None and res["pooled_ci_refused"]["code"] == k2.K2_SINGLE_DF
assert "Common-effect sensitivity (z-based; not the registered interval)" in html
assert "heterogeneity caveat" not in html
assert "heterogeneity caveat" in html2
```

Quoted output:

- `[MEASURED]` synthetic k=2 output: `{'k': 2, 'estimate': 0.8102, 'ci_low': None, 'ci_high': None, 'pooled_ci_refused': {'code': 'K2_SINGLE_DF', 'detail': 'Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here.'}, 'estimate_fixed': 0.8102, 'ci_low_fixed': 0.7236, 'ci_high_fixed': 0.9072} common_label True caveat_plain False caveat_material True`.

### Concordant k=2 GRADE still not assessed as clean

Exact assertion:

```python
assert inc["not_assessable_automatically"] is True
assert inc["assessed"] is False
assert "two concordant trials" in inc["basis"]
```

Quoted output:

- `[MEASURED]` concordant k=2 GRADE output: `{'downgrade': 0, 'not_assessable_automatically': True, 'assessed': False, 'direction_conflict': False, 'i2': 0.0, 'basis': 'k=2: inconsistency is not assessable automatically; Q-derived I^2=0.0%; tau^2=0.0; two concordant trials; prediction interval absence is not evidence of no inconsistency, so downgrade is left to human judgement'}`.

## 3. Rebuilt pages and before/after page deltas

Rebuild commands used `python scripts/build_topic.py <slug> --now 2026-09-11`. `[MEASURED]` `12 of 32` review pages were rebuilt: the `9 of 10` served primary k=2 pages, plus `2 of 32` pages with secondary k=2 outcomes, plus `1 of 32` replay-stale page needed by the gate. The paired blind pages under `docs/m/` changed with the same generated content.

### Primary k=2 pages

All values in this table are `[MEASURED]` from `aa8ed28a` review objects and rebuilt review objects.

| slug | outcome | before served primary result | after served primary result | refusal and GRADE inconsistency basis | manuscript result sentence |
|---|---|---|---|---|---|
| `balanced-crystalloids-vs-saline-mortality` | Mortality | RR `0.9774 [0.6521, 1.465]` | RR point `0.9774`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.9774 [0.9183, 1.0404]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; basis: `k=2: inconsistency is not assessable automatically; Q-derived I^2=0.0%; tau^2=0.0; two concordant trials; prediction interval absence is not evidence of no inconsistency, so downgrade is left to human judgement` | Before: `Pooling 2 trials gave RR 0.98 (95% CI 0.65 to 1.47), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (RR 0.98), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `colchicine-recurrent-pericarditis` | Recurrent pericarditis | RR `0.4813 [0.064, 3.6169]` | RR point `0.4813`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.4813 [0.3526, 0.6569]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; same concordant k=2 basis with Q-derived `I^2=0.0%` and `tau^2=0.0` | Before: `Pooling 2 trials gave RR 0.48 (95% CI 0.06 to 3.62), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (RR 0.48), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `corticosteroids-cap-mortality` | All-cause mortality | RR `0.5458 [0.0361, 8.2605]` | RR point `0.5458`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.5458 [0.3589, 0.8299]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; same concordant k=2 basis with Q-derived `I^2=0.0%` and `tau^2=0.0` | Before: `Pooling 2 trials gave RR 0.55 (95% CI 0.04 to 8.26), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (RR 0.55), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `finerenone-ckd-t2d-renal` | Kidney composite outcome | HR `0.8407 [0.4625, 1.5281]` | HR point `0.8407`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.8407 [0.7666, 0.9218]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; same concordant k=2 basis with Q-derived `I^2=0.0%` and `tau^2=0.0` | Before: `Pooling 2 trials gave HR 0.84 (95% CI 0.46 to 1.53), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (HR 0.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `pcsk9-mace` | Major adverse cardiovascular events | HR `0.85 [0.5852, 1.2346]` | HR point `0.85`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.85 [0.8024, 0.9004]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; same concordant k=2 basis with Q-derived `I^2=0.0%` and `tau^2=0.0` | Before: `Pooling 2 trials gave HR 0.85 (95% CI 0.59 to 1.23), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (HR 0.85), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `semaglutide-obesity-weight` | Percent change in body weight | MD `-11.8449 [-25.1318, 1.442]` | MD point `-11.8449`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `-12.3621 [-13.0206, -11.7036]`; caveat present | `pooled_ci_refused=K2_SINGLE_DF`; basis: `k=2: inconsistency is not assessable automatically; Q-derived I^2=84.5%; tau^2=1.86306; I^2 > 50%; prediction interval absence is not evidence of no inconsistency, so downgrade is left to human judgement` | Before: `Pooling 2 trials gave MD -11.84 (95% CI -25.13 to 1.44), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (MD -11.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `sglt2-hfref-hosp-cvdeath` | Composite cardiovascular death or hospitalisation for heart failure | RR `0.7755 [0.4457, 1.3493]` | RR point `0.7755`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.7755 [0.712, 0.8447]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; same concordant k=2 basis with Q-derived `I^2=0.0%` and `tau^2=0.0` | Before: `Pooling 2 trials gave RR 0.78 (95% CI 0.45 to 1.35), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (RR 0.78), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `statins-primary-prevention-elderly` | Major vascular events | HR `0.6803 [0.2897, 1.5975]` | HR point `0.6803`; `ci_low=None`; `ci_high=None`; common-effect sensitivity `0.6803 [0.5964, 0.776]`; no caveat | `pooled_ci_refused=K2_SINGLE_DF`; same concordant k=2 basis with Q-derived `I^2=0.0%` and `tau^2=0.0` | Before: `Pooling 2 trials gave HR 0.68 (95% CI 0.29 to 1.6), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `Pooling 2 trials retained the point estimate (HR 0.68), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made.` |
| `ticagrelor-vs-clopidogrel-acs` | Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke | HR `1.0479 [0.0324, 33.8921]`; `tau^2=0.12171` | pooled row refused; `estimate=None`; `ci_low=None`; `ci_high=None`; honest k=1 anchor PLATO HR `0.84 [0.77, 0.92]`; named remainder PHILO | `pool_refused=DIRECTION_CONFLICT_K2`; basis: `k=2: inconsistency is not assessable automatically; Q-derived I^2=77.7%; tau^2=0.12171; trial point estimates conflict in direction and/or their CIs do not overlap; prediction interval absence is not evidence of no inconsistency, so downgrade is left to human judgement` | Before: `Pooling 2 trials gave HR 1.05 (95% CI 0.03 to 33.89), random-effects (Paule-Mandel with a Hartung-Knapp interval).` After: `The two eligible trials conflict in direction, so no pooled effect is reported. The pre-named k=1 anchor is PLATO: HR 0.84 (95% CI 0.77 to 0.92); the named remainder is PHILO.` |

`[MEASURED]` `iv-iron-hfref-hosp` remains a primary `k==2` object but was already suppressed as incompatible at `aa8ed28a`; before and after it has no served estimate/CI, so it is not counted among the `9 of 10` served primary k=2 pages.

### Secondary k=2 outcomes across all topics

All values in this table are `[MEASURED]` from all rebuilt `docs/reviews/*/review.json` files.

| slug | secondary outcome | before served secondary result | after served secondary result | caveat |
|---|---|---|---|---|
| `corticosteroids-cap-mortality` | Hyperglycaemia | RR `1.8752 [0.175, 20.0938]` | RR point `1.8752`; `ci_low=None`; `ci_high=None`; `pooled_ci_refused=K2_SINGLE_DF`; common-effect sensitivity `1.8752 [1.3007, 2.7036]` | none; Q-derived `I^2=0.0%`, `tau^2=0.0` |
| `noac-vs-warfarin-af-stroke` | Major bleeding | HR `0.7464 [0.2922, 1.9068]` | HR point `0.7464`; `ci_low=None`; `ci_high=None`; `pooled_ci_refused=K2_SINGLE_DF`; common-effect sensitivity `0.7511 [0.6837, 0.8251]` | heterogeneity caveat present: `tau^2=0.00624`, `I^2=57.1%`, threshold `tau^2 > 0` and `I^2 > 25%` |
| `tocilizumab-covid19-mortality` | Serious adverse events | OR `0.8109 [0.0943, 6.9756]` | OR point `0.8109`; `ci_low=None`; `ci_high=None`; `pooled_ci_refused=K2_SINGLE_DF`; common-effect sensitivity `0.8109 [0.5819, 1.1302]` | none; Q-derived `I^2=0.0%`, `tau^2=0.0` |

### Other rebuilt page

- `[MEASURED]` `probiotics-aad-prevention` was rebuilt because the full gate found stale replay bytes after renderer changes. Its primary manuscript result sentence was unchanged: before and after, `Pooling 16 trials gave RR 0.7 (95% CI 0.54 to 0.92), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.29 to 1.68.` The changed bytes are regenerated review/manifest/reproduction/blind-page bytes, not a k=2 analytic change.

### Reproduction checks for rebuilt pages

`[MEASURED]` Each rebuilt slug below ended with `OK <slug>` and `1/1 reproduce (all reproducible)`:

- `balanced-crystalloids-vs-saline-mortality`
- `colchicine-recurrent-pericarditis`
- `corticosteroids-cap-mortality`
- `finerenone-ckd-t2d-renal`
- `noac-vs-warfarin-af-stroke`
- `pcsk9-mace`
- `probiotics-aad-prevention`
- `semaglutide-obesity-weight`
- `sglt2-hfref-hosp-cvdeath`
- `statins-primary-prevention-elderly`
- `ticagrelor-vs-clopidogrel-acs`
- `tocilizumab-covid19-mortality`

## 4. Tests

Targeted plant suite:

```text
[MEASURED] 45 passed in 14.13s
```

Full suite:

```text
[MEASURED] 646 passed in 330.86s (0:05:30)
```

Other measured checks:

- `[MEASURED]` `python scripts/spec_curve.py` output: `wrote docs/spec_curve.json: 13 topics k>=2; direction stable 13/13; significance stable 9/13`.
- `[MEASURED]` `python scripts/external_agreement.py` output: `same-ESTIMAND agreement (the only same-question agreement): 12/26`; same-estimand diverge `3`; cross-estimand pending `10`; opposite `0`; non-comparable `1`.
- `[MEASURED]` `python -m harness.index docs` output: `wrote docs\index.html`.
- `[MEASURED]` `python scripts/rewrite_fixstate_lines.py` output: `rewrote evidence README fix-state lines`.
- `[MEASURED]` `python scripts/render_fix_ledger.py` output: `rendered docs/fix_ledger.json`.
- `[MEASURED]` `python -m pytest tests/test_fixstate.py::test_real_store_validates -q` output after regenerated ledgers: `1 passed in 181.53s (0:03:01)`.
- `[MEASURED]` `python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q` output after rebuilding `probiotics-aad-prevention`: `1 passed in 19.20s`.
- `[MEASURED]` `python -m pytest tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews -q` output after aligning page/limitations text: `1 passed in 2.14s`.

Existing tests changed only where the new requirement invalidated the old assertion:

- `[MEASURED]` `tests/test_claim_object.py` no longer expects a refused k=2 HKSJ interval to produce an ordinary "not significant/crosses null" state; the k=2 case now asserts the no-pooled-claim state, while k>=3 CI behavior is still tested.

## 5. What I did not do

- `[MEASURED]` I did not run `git add`, `git commit`, `git stash`, `git checkout`, `git reset`, or `git clean`.
- `[MEASURED]` I did not change which trials are pooled.
- `[MEASURED]` I did not touch `harness/rob_sensitivity.py`.
- `[MEASURED]` I did not touch `harness/estmeasure.py`.
- `[MEASURED]` I did not change the PM/HKSJ arithmetic; the unserved interval is still preserved for auditability under `ci_hksj_unserved`.
- `[MEASURED]` I did not run searches, network retrieval, extractor rebuilds, or `scripts/verify_all.py`.
- `[MEASURED]` I did not delete or clean untracked lane-control files (`LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`).

## 6. Changed or added files

All paths below are `[MEASURED]` from the working tree after the lane edits, grouped by purpose.

Code and config:

- `harness/k2.py`
- `harness/claim.py`
- `harness/grade.py`
- `harness/index.py`
- `harness/limitations.py`
- `harness/manuscript.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/spec_curve.py`
- `topics/ticagrelor-vs-clopidogrel-acs.json`

Tests and report:

- `tests/test_k2_refusal.py`
- `tests/test_claim_object.py`
- `LANE-K2-REPORT.md`

Generated corpus/index files:

- `docs/index.html`
- `docs/spec_curve.json`
- `docs/external_agreement.json`
- `docs/fix_ledger.json`
- `registry/blind_map.json`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`

Generated review files, each with `REPRODUCTION.json`, `index.html`, `manifest.json`, and `review.json`:

- `docs/reviews/balanced-crystalloids-vs-saline-mortality/REPRODUCTION.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/manifest.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json`
- `docs/reviews/colchicine-recurrent-pericarditis/REPRODUCTION.json`
- `docs/reviews/colchicine-recurrent-pericarditis/index.html`
- `docs/reviews/colchicine-recurrent-pericarditis/manifest.json`
- `docs/reviews/colchicine-recurrent-pericarditis/review.json`
- `docs/reviews/corticosteroids-cap-mortality/REPRODUCTION.json`
- `docs/reviews/corticosteroids-cap-mortality/index.html`
- `docs/reviews/corticosteroids-cap-mortality/manifest.json`
- `docs/reviews/corticosteroids-cap-mortality/review.json`
- `docs/reviews/finerenone-ckd-t2d-renal/REPRODUCTION.json`
- `docs/reviews/finerenone-ckd-t2d-renal/index.html`
- `docs/reviews/finerenone-ckd-t2d-renal/manifest.json`
- `docs/reviews/finerenone-ckd-t2d-renal/review.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/REPRODUCTION.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/index.html`
- `docs/reviews/noac-vs-warfarin-af-stroke/manifest.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/review.json`
- `docs/reviews/pcsk9-mace/REPRODUCTION.json`
- `docs/reviews/pcsk9-mace/index.html`
- `docs/reviews/pcsk9-mace/manifest.json`
- `docs/reviews/pcsk9-mace/review.json`
- `docs/reviews/probiotics-aad-prevention/REPRODUCTION.json`
- `docs/reviews/probiotics-aad-prevention/index.html`
- `docs/reviews/probiotics-aad-prevention/manifest.json`
- `docs/reviews/probiotics-aad-prevention/review.json`
- `docs/reviews/semaglutide-obesity-weight/REPRODUCTION.json`
- `docs/reviews/semaglutide-obesity-weight/index.html`
- `docs/reviews/semaglutide-obesity-weight/manifest.json`
- `docs/reviews/semaglutide-obesity-weight/review.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/REPRODUCTION.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/index.html`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/manifest.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/review.json`
- `docs/reviews/statins-primary-prevention-elderly/REPRODUCTION.json`
- `docs/reviews/statins-primary-prevention-elderly/index.html`
- `docs/reviews/statins-primary-prevention-elderly/manifest.json`
- `docs/reviews/statins-primary-prevention-elderly/review.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/REPRODUCTION.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/manifest.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json`
- `docs/reviews/tocilizumab-covid19-mortality/REPRODUCTION.json`
- `docs/reviews/tocilizumab-covid19-mortality/index.html`
- `docs/reviews/tocilizumab-covid19-mortality/manifest.json`
- `docs/reviews/tocilizumab-covid19-mortality/review.json`

Generated blind-page mirrors:

- `docs/m/m0594e053/index.html` - corticosteroids page
- `docs/m/m175bd0c3/index.html` - tocilizumab page
- `docs/m/m2da64325/index.html` - ticagrelor page
- `docs/m/m586876fa/index.html` - probiotics page
- `docs/m/m5b3fd56c/index.html` - semaglutide page
- `docs/m/m5e5590d5/index.html` - finerenone page
- `docs/m/m6dd4233b/index.html` - SGLT2 HFrEF page
- `docs/m/m89f8021b/index.html` - balanced crystalloids page
- `docs/m/m8db5253b/index.html` - NOAC page
- `docs/m/m979b0810/index.html` - colchicine page
- `docs/m/mb53e1ed5/index.html` - statins page
- `docs/m/mf6cd36c2/index.html` - PCSK9 page
