# LANE CP2 Report

## 1. What Was Wrong

Mechanism:
- The comparator object always emitted `shared_k = "not exactly verifiable (comparator trial table not machine-exposed)"` unless older parity prose happened to repair the interpretation later.
- That was false for reader-exposed comparator text: the NOAC COMBINE-AF abstract names all four pivotal AF trials, esketamine Table 2 enumerates four acute-induction coded trial rows, GLP-1 Table 1 names eight CVOTs, and Zhang 2021 lists eight SGLT2 trials in Table 1.
- The old comparator k parser could read a nearby count instead of the included-trial table. [MEASURED] Zhang 2021 was rendered as comparator `theirs_k=3` in the pre-fix page, but its cached Table 1 has `k=8`.
- Same-set comparators were being worded as if numerical agreement were independent corroboration, even when the quantities differ. NOAC and DOAC-VTE are now labelled as method/quantity tests.
- Recency, treatment strategy, and outcome identity were missing from the comparator object, so CLEAR SYNERGY / OMEGA-REMODEL / SOUL recency and the metformin add-on versus monotherapy contrast were not first-class checks.
- Scope validity stayed true for two selection failures: Zhang 2021 includes protocol-excluded HF/CKD-entry trials, and SMART-C is a broader IPD consortium rather than a same-scope CKD systematic-review comparator.

Files carrying the mechanism:
- Added `harness/comparator_second_pass.py`.
- Wired profiled-topic enrichment in `harness/pipeline.py`.
- Rendered compact CP2 audit fields in `harness/page.py`.
- Added `scripts/comparator_second_pass_sweep.py`.
- Added `tests/test_comparator_second_pass.py`.
- Wrote `docs/comparator_second_pass.json`.

Static-vs-dynamic disclosure:

| Item | Static or dynamic | Disclosure |
|---|---|---|
| CP2 profile vocabulary | Static | Fixed per-slug source-backed profiles in `harness/comparator_second_pass.py` for the lane-named comparators only. |
| Trial-set activation | Dynamic | A profile only becomes a page field when required terms are found in cached comparator abstract/full text. |
| Sweep denominator | Dynamic from committed pages | `scripts/comparator_second_pass_sweep.py` reads `aa8ed28a:docs/reviews/*/review.json` to count baseline pages saying not-exposed. |
| Reported metformin add-on effects | Dynamic source-gated override | The OR 1.65 and OR 4.26 rows are used only when the cached Cochrane abstract contains the add-on contrast text. |
| Trial pools / synthesis | Not changed | No search, screening, pooling, harms, or `harness/synth.py` changes. |

Corpus sweep:
- Command: `python scripts/comparator_second_pass_sweep.py`
- Output: `comparator second-pass: 4 of 32 baseline not-exposed pages have trial sets stated in cached text`
- [MEASURED] Stated-in-text pages: `esketamine-trd-madrs`, `glp1-ra-mace-t2d`, `noac-vs-warfarin-af-stroke`, `sglt2-primary-prevention-hf`.
- JSON: `docs/comparator_second_pass.json`.

## 2. Plant

Plant file: `tests/test_comparator_second_pass.py`

Exact assertions:
- `test_PLANT_noac_not_machine_exposed_refused_when_text_enumerates_four_trials`: pre-fix `shared_k` contains `not exactly verifiable`; post-fix `comparator_trial_set.status == "MEASURED"`, `k == 4`, `overlap.shared_k == 4`, `shared_k_measurement == "MEASURED"`, and `quantity_match == "SAME_SET_DIFFERENT_QUANTITY"`.
- `test_colchicine_secondary_recency_fires_for_clear_synergy`: `comparator_recency.status == "COMPARATOR_PREDATES_POOLED_TRIAL(CLEAR SYNERGY)"`.
- `test_PLANT_zhang_k3_parser_is_refused_by_table_count`: pre-fix Zhang page has `theirs_k == 3`; post-fix `theirs_k == 8`, `shared_k == 4`, `shared_k_measurement == "MEASURED"`, and `scope_valid is False`.
- `test_metformin_strategy_mismatch_fires_and_uses_add_on_contrast`: pre-fix ovulation comparator estimate is OR 2.64; post-fix `treatment_strategy_match == "MISMATCH_CORRECTED"`, ovulation OR is 1.65, and GI adverse-events OR is 4.26.
- `test_control_true_no_enumeration_stays_not_exposed`: denosumab direct apply remains `NOT_EXPOSED` with `MEASURED_ABSENCE`.
- `test_control_noac_has_no_recency_flag_when_comparator_is_current_for_pool`: NOAC recency remains `NO_RECENCY_FLAG`.

Pre-fix object findings [MEASURED from `git show aa8ed28a:...`]:
- NOAC before: `theirs_k=not stated`, `shared_k=not exactly verifiable`.
- Zhang/SGLT2-primary before: `theirs_k=3`, `shared_k=not exactly verifiable`, `scope_valid=True`.
- Metformin before: ovulation OR 2.64 [1.85, 3.75] and GI OR 4.00 [2.63, 6.09], the monotherapy contrast.

Post-fix plant output:
- `python -m pytest tests/test_comparator_second_pass.py -q`
- Summary: `6 passed in 4.08s`

Additional focused output:
- `python -m pytest tests/test_comparator_second_pass.py tests/test_parity_relation.py tests/test_comparator_atomic.py -q`
- Summary: `25 passed in 5.00s`
- `python scripts/reproduce_review.py probiotics-aad-prevention`
- Summary: `1/1 reproduce (all reproducible)`
- `python -m pytest tests/test_comparator_second_pass.py tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q`
- Summary: `7 passed in 25.05s`

## 3. Rebuilt Pages And Before/After

All rebuilt pages below were built with `python scripts/build_topic.py <slug> --now 2026-09-11` and replayed with `python scripts/reproduce_review.py <slug>`. Each replay printed `1/1 reproduce (all reproducible)`.

| Slug | Before | After |
|---|---|---|
| `noac-vs-warfarin-af-stroke` | `theirs_k=not stated`; `shared_k=not exactly verifiable` | `theirs_k=4`; `shared_k=4 MEASURED`; `quantity_match=SAME_SET_DIFFERENT_QUANTITY`; `outcome_match=MATCH` |
| `esketamine-trd-madrs` | `theirs_k=not stated`; `shared_k=not exactly verifiable` | `theirs_k=4`; `shared_k=4 MEASURED`; `quantity_match=SAME_SET_DIFFERENT_IMPLEMENTATION`; `outcome_match=MATCH` |
| `doac-vte-recurrence` | `theirs_k=not stated`; `shared_k=not exactly verifiable`; recurrent VTE RR 0.90 [0.77, 1.06] | `theirs_k=6`; `shared_k=6 MEASURED_COUNT_ONLY`; `quantity_match=SAME_SET_DIFFERENT_QUANTITY`; `outcome_match=NEAR_MATCH` |
| `colchicine-secondary-cv-prevention` | no recency field; `shared_k=not exactly verifiable` | `comparator_recency=COMPARATOR_PREDATES_POOLED_TRIAL(CLEAR SYNERGY)`; `trial_set=NOT_EXPOSED`; `shared_k_measurement=MEASURED_ABSENCE` |
| `omega3-cardiovascular-events` | no recency field; comparator k source still 28; `shared_k=not exactly verifiable` | `comparator_recency=COMPARATOR_PREDATES_POOLED_TRIAL(OMEGA-REMODEL)`; `trial_set=NOT_EXPOSED`; `shared_k_measurement=MEASURED_ABSENCE` |
| `glp1-ra-mace-t2d` | `theirs_k=not stated`; `shared_k=not exactly verifiable`; no outcome mismatch field | `theirs_k=8`; `shared_k=7 MEASURED`; `only_theirs=ELIXA`; `comparator_recency=COMPARATOR_PREDATES_POOLED_TRIAL(SOUL)`; `outcome_match=NEAR_MATCH_ONE_TRIAL_ENDPOINT_MISMATCH` |
| `sglt2-primary-prevention-hf` | `theirs_k=3`; `shared_k=not exactly verifiable`; `scope_valid=True` | `theirs_k=8`; `shared_k=4 MEASURED`; `scope_valid=False`; note names DAPA-HF, EMPEROR-Reduced, CREDENCE as protocol-excluded comparator inclusions |
| `sglt2-ckd-progression` | `theirs_k=10`; `scope_valid=True`; reported label `CKD progression / kidney composite outcome` | `trial_set=COUNT_MEASURED`; `scope_valid=False`; `quantity_match=BROADER_IPD_CONSORTIUM`; `outcome_match=DIFFERENT_QUANTITY`; reported label aligned to trial-defined major kidney/cardiorenal composite |
| `metformin-pcos-ovulation` | ovulation OR 2.64 [1.85, 3.75]; GI OR 4.00 [2.63, 6.09]; no strategy field | `treatment_strategy_match=MISMATCH_CORRECTED`; ovulation OR 1.65 [1.35, 2.03]; GI OR 4.26 [2.83, 6.40] |

Generated side effects:
- Rebuilt blind pages and `registry/blind_map.json` for the nine rebuilt slugs.
- Refreshed `docs/fix_ledger.json` with `python scripts/render_fix_ledger.py`, then `python scripts/rewrite_fixstate_lines.py`, after the full suite reported a stale fix ledger.
- No ratchet acknowledgements were written. I did not intentionally reword absent/banner blocks; the visible text additions are the generated Comparator-tab CP2 audit rows.

## 4. Tests

Targeted:
- `python -m pytest tests/test_comparator_second_pass.py -q`
- Summary: `6 passed in 4.08s`

CP-adjacent:
- `python -m pytest tests/test_comparator_second_pass.py tests/test_parity_relation.py tests/test_comparator_atomic.py -q`
- Summary: `25 passed in 5.00s`

Fix-state after generator refresh:
- `python -m pytest tests/test_fixstate.py -q`
- Summary: `13 passed in 457.80s (0:07:37)`

Full:
- First full run stopped on stale fix ledger after [MEASURED] `218 passed`: `1 failed, 218 passed in 606.91s (0:10:06)`.
- Second full run stopped on the unprofiled probiotics replay mismatch after [MEASURED] `242 passed`: `1 failed, 242 passed in 501.21s (0:08:21)`.
- After scoping pipeline enrichment to CP2-profiled topics only, final full run:
- `python -m pytest tests -x -q`
- Summary: `722 passed in 991.33s (0:16:31)`

## 5. What I Did Not Do

- Did not commit.
- Did not run network searches.
- Did not touch pooling, screening, search, harms, `harness/synth.py`, or trial inclusion/exclusion.
- Did not add or remove any trial from any pool.
- Did not run `scripts/verify_all.py`.
- Did not use `git add`, `git commit`, `git stash`, `git checkout`, `git reset`, or `git clean`.
- Did not write ratchet acknowledgements; integrator owns any acknowledgement signing.

## 6. Files Changed Or Added

New source/test/script/report files:
- `harness/comparator_second_pass.py`
- `scripts/comparator_second_pass_sweep.py`
- `tests/test_comparator_second_pass.py`
- `docs/comparator_second_pass.json`
- `LANE-CP2-REPORT.md`

Modified source files:
- `harness/pipeline.py`
- `harness/page.py`

Modified generated portfolio files:
- `docs/index.html`
- `docs/fix_ledger.json`
- `registry/blind_map.json`

Modified rebuilt review directories, four files each (`REPRODUCTION.json`, `index.html`, `manifest.json`, `review.json`):
- `docs/reviews/colchicine-secondary-cv-prevention/`
- `docs/reviews/doac-vte-recurrence/`
- `docs/reviews/esketamine-trd-madrs/`
- `docs/reviews/glp1-ra-mace-t2d/`
- `docs/reviews/metformin-pcos-ovulation/`
- `docs/reviews/noac-vs-warfarin-af-stroke/`
- `docs/reviews/omega3-cardiovascular-events/`
- `docs/reviews/sglt2-ckd-progression/`
- `docs/reviews/sglt2-primary-prevention-hf/`

Modified blind pages:
- `docs/m/m24cd09bc/index.html`
- `docs/m/m250220c2/index.html`
- `docs/m/m87167438/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/maf69923c/index.html`
- `docs/m/mc16cd596/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/me79cb3b0/index.html`

Pre-existing untracked lane files left unmodified/uncommitted:
- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
