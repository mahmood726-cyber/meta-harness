# LANE S8 Report

## 1. What was wrong

STEP 8 (PMID 35015037 / NCT04074161) was absent because the topic relied on title-shaped retrieval and the record title foregrounded semaglutide versus liraglutide. The semaglutide-versus-placebo contrast is inside the trial. I added it through `extra_pmids` and recorded `CONTRAST_HIDDEN_BY_TITLE` in `recovery_provenance`.

The continuous CT.gov path paired the selected observed mean/SD rows with top-level randomized/FAS denominators. For STEP 1 and STEP 3, the held structured class row gives Number Analyzed denominators, so the SD must pair with analysed n: STEP 1 1212/577 and STEP 3 373/189.

The page label also drifted: it called these rows treatment-policy/all randomized. They are now generated as observed in-trial Week-68 means among participants with available measurements.

## 2. Plant

Added `tests/test_step8_recovery.py`.

Pre-fix run:

```text
FF.FF
FAILED test_step8_absent_from_prefix_and_recovered_with_extra_pmid_provenance
assert step8 is not None
FAILED test_step5_extra_pmid_screens_in_then_refuses_week_104_timepoint
assert screen_row and screen_row["decision"] == "include"
FAILED test_continuous_sd_denominators_use_analysed_n_when_held
KeyError: 'n_kind'
FAILED test_population_label_is_generated_from_analysed_observed_case_rows
assert 'participants with available measurements' in 'in-trial / treatment-policy estimand (all randomized), baseline to Week 68'
4 failed, 1 passed
```

The test also protects the existing STEP 11 Week-44 refusal.

## 3. Rebuilt pages and numbers

Changed served semaglutide artifacts:

- `docs/reviews/semaglutide-obesity-weight/index.html`
- `docs/reviews/semaglutide-obesity-weight/review.json`
- `docs/reviews/semaglutide-obesity-weight/manifest.json`
- `docs/reviews/semaglutide-obesity-weight/REPRODUCTION.json`
- `docs/m/m5b3fd56c/index.html`
- `docs/index.html`

Primary result before (`ad5e7c66`):

- k=2
- MD -11.8449
- registered CI refused: `K2_SINGLE_DF`
- quarantined HKSJ audit interval -25.1318 to 1.442
- tau2 1.86306
- claim: no pooled significance/null-crossing claim
- GRADE: low

Primary result after:

- k=3
- MD -12.5801
- 95% CI -17.4021 to -7.7581
- tau2 3.01729
- prediction interval -21.4745 to -3.6857
- claim: benefit, significant, does not cross null
- GRADE: moderate, capped below high because D3 missing-outcome-data RoB remains structurally unassessed

Pooled continuous rows after:

- STEP 3 / PMID 33625476: -16.5 SD 10.1 n=373 vs -5.8 SD 7.7 n=189, `n_kind=ANALYSED`
- STEP 1 / PMID 33567185: -15.6 SD 10.1 n=1212 vs -2.8 SD 6.5 n=577, `n_kind=ANALYSED`
- STEP 8 / PMID 35015037: -16.4 SD 10.5 n=117 vs pooled placebo -1.6 SD 8.6 n=78, `n_kind=ANALYSED`

The k=2 refusal block is superseded by the k=3 served interval. Reworded blocks include the result summary, analysis population label, trial input denominator provenance, compatibility key lifestyle-intensity limitation, recovery provenance table, RoB2 coverage, GRADE certainty, error-rate sample freshness, and screening found-by rows for STEP 8/STEP 5.

## 4. STEP 5 and STEP 11

STEP 5 (PMID 36216945) is now in the ledger through `EXTRA_PMIDS`, screens in on P/I/C/design, and is refused as `TIMEPOINT_MISMATCH`: Week 104, not Week 68.

STEP 11 (PMID 40825340) remains refused as `TIMEPOINT_MISMATCH`: Week 44, not Week 68.

## 5. Sweep

`scripts/continuous_denominator_sweep.py` wrote `docs/continuous_denominator_sweep.json`.

```text
0 rows pairing an SD with a randomised n where an analysed n exists in held text of 8 continuous rows
0 rows labelled treatment-policy while observed-case of 8 continuous rows
```

The sweep scanned 32 topic pages and found 3 continuous outcomes / 8 continuous rows.

## 6. Static vs dynamic hardcode disclosure

| Item | Static or dynamic | Source |
| --- | --- | --- |
| STEP 8 / STEP 5 PMID recovery list | Static, declared | `topics/semaglutide-obesity-weight.json` `extra_pmids`; inlined lane prompt metadata |
| STEP 8 arm values | Dynamic extraction from held source | CT.gov structured results in `cache/semaglutide-obesity-weight/records.json` |
| STEP 5 refusal | Static override, source-backed | `verified_effects.json` plus abstract span |
| Denominator `n_kind` | Dynamic extraction | `harness/continuous_denominator.py` from CT.gov outcome/class denominator fields |
| Population label | Dynamic generated label | `harness/pipeline.py` from continuous `n_kind` |
| Lifestyle-intensity compatibility | Static annotations | Topic `trial_annotations`, rendered/disclosed only |

No matched-placebo publication table values were typed into the cache. The held build uses the CT.gov structured semaglutide-versus-pooled-placebo row. STEP 3 funding was not changed because I did not find the sponsor-involvement sentence in the held sources. Harms were not extracted into pools.

## 7. Tests

Final checks:

```text
python scripts/reproduce_review.py semaglutide-obesity-weight
OK semaglutide-obesity-weight
1/1 reproduce (all reproducible)

python scripts/continuous_denominator_sweep.py
0 rows pairing an SD with a randomised n where an analysed n exists in held text of 8 continuous rows
0 rows labelled treatment-policy while observed-case of 8 continuous rows

python -m pytest tests/test_step8_recovery.py tests/test_ctgov_continuous.py ... -q
17 passed

python -m pytest tests/test_fixstate.py::test_real_store_validates -q
1 passed

python -m pytest tests -x -q
721 passed in 197.71s

git diff --check
passed
```

Intermediate full-suite stops exposed generated sidecars that needed refreshing after adding a pooled trial: `fix_ledger.json`, `integrity.json`, override audit, RoB2, manuscript numerals, and error-rate sample freshness. All were fixed and the final full suite passed.

## 8. Files changed / added

Core code:

- `harness/continuous_denominator.py`
- `harness/ctgov_results.py`
- `harness/pipeline.py`
- `harness/page.py`
- `harness/compat.py`
- `scripts/continuous_denominator_sweep.py`
- `tests/test_step8_recovery.py`

Topic/source/protocol:

- `topics/semaglutide-obesity-weight.json`
- `protocols/semaglutide-obesity-weight.md`
- `cache/semaglutide-obesity-weight/records.json`
- `cache/semaglutide-obesity-weight/retrieval_ledger.json`
- `cache/semaglutide-obesity-weight/verified_effects.json`
- `cache/semaglutide-obesity-weight/arm_contrast.json`
- `cache/semaglutide-obesity-weight/rob2.json`
- `cache/semaglutide-obesity-weight/integrity.json`

Generated/audit artifacts:

- `docs/reviews/semaglutide-obesity-weight/*`
- `docs/m/m5b3fd56c/index.html`
- `docs/index.html`
- `docs/continuous_denominator_sweep.json`
- `docs/fix_ledger.json`
- `docs/error_rate.json`
- `docs/error_rate_sample.json`
- `docs/evidence/override-audit-2026-09-14/overrides.json`
- `registry/blind_map.json`
- `cache/embeddings.json`

Not committed.
