# LANE XS2 Report

## 1. What Was Wrong

MEASURED: `aa8ed28a:docs/reviews/pcsk9-mace/review.json` rendered both PCSK9 cross-source rows as corroboration without an outcome-identity object: FOURIER had CT.gov RR `0.666` and ODYSSEY had CT.gov RR `0.818`, both with the note `shown for corroboration only`.

MEASURED: `ad5e7c66:docs/reviews/pcsk9-mace/review.json` had the XS fix for FOURIER (`DIFFERENT_ENDPOINT`, not corroborated) but still labelled ODYSSEY as `SAME_ENDPOINT` and `corroborates_endpoint: true` even though its CT.gov value was a `PERCENTAGE` ratio (`9.5 / 11.1 = 0.856`), not a risk ratio or hazard ratio. Page-change before/after quotes below use `ad5e7c66` as the pre-XS2 object unless explicitly marked `aa8ed28a`.

Mechanism: XS still allowed magnitude agreement to rescue a different measure. XS2 adds a typed identity object per cross-source row:

`identity = {title_match, component_match, measure_type, population_match, verdict}`

Corroboration is now allowed only for `identity.verdict == IDENTICAL_ENDPOINT`; agreement statistics in `docs/second_source_sweep.json` are computed only over that class.

Files for the mechanism:

- `harness/second_source.py`: typed title/component/measure/population identity and `SECOND_SOURCE_*` verdicts.
- `harness/ctgov_results.py`: carries CT.gov outcome descriptions and raw selected values so component and measure provenance can be rendered.
- `harness/pipeline.py`: writes `identity`, `second_source_verdict`, `registry_effect_label`, and refreshes identity after trial component annotations are copied.
- `harness/page.py`: renders non-identical rows as `SECOND_SOURCE_DIFFERENT_ENDPOINT` / `SECOND_SOURCE_DIFFERENT_MEASURE` with pooled and registry values shown, no agreement word.
- `scripts/second_source_sweep.py`: corpus sweep over all served review pages.

Static-vs-dynamic disclosure:

| Item | Source | Disclosure |
|---|---|---|
| Verdict names | Static code | `harness/second_source.py` constants. |
| Log tolerance | Existing static constant | `CROSS_SOURCE_LOG_TOL = 0.12` in `harness/pipeline.py`. |
| Component sets | Dynamic committed topic data | Trial annotations copied from `topics/*.json`; registry components read from committed CT.gov outcome title/description. |
| Sweep denominator | Dynamic committed review set | MEASURED 10 cross-source rows over 32 topics via `scripts/second_source_sweep.py`; no network. |

## 2. Plant

Test file: `tests/test_second_source_identity.py`.

MEASURED pre-fix plant assertions:

- `test_aa8ed28a_served_fourier_and_odyssey_corroboration_has_no_identity_gate` loads `git show aa8ed28a:docs/reviews/pcsk9-mace/review.json` and asserts FOURIER `ctgov_rr == 0.666`, ODYSSEY `ctgov_rr == 0.818`, both notes contain `shown for corroboration only`, and neither row has `identity`.
- `test_ad5e7c66_odyssey_percentage_ratio_was_still_labelled_corroboration` loads `git show ad5e7c66:docs/reviews/pcsk9-mace/review.json` and asserts ODYSSEY has `registry_measure_type == "PERCENTAGE"`, `endpoint_match == "SAME_ENDPOINT"`, `corroborates_endpoint is True`, and no `identity`. It also records that FOURIER was already non-corroborating in XS but still lacked typed identity.
- `test_served_fourier_0666_is_value_not_reproducible_from_current_cache` asserts the old served source was `2/13784` vs `3/13780`, while the rebuilt cache-backed selected values are `2.74` vs `3.11` and `ctgov_rr == 0.881`. I report the old `0.666` as `VALUE_NOT_REPRODUCIBLE_FROM_CACHE` as an event count; it is explained by the old truncation of KM percentages, not by a count row in the current cache.

MEASURED post-fix assertions:

- `test_postfix_pcsk9_second_source_rows_are_different_measure_not_corroboration` rebuilds `pcsk9-mace` from committed cache and asserts FOURIER `SECOND_SOURCE_DIFFERENT_MEASURE`, measure type `KM estimate ratio`, `component_match is True`, and `corroborates_endpoint is False`.
- The same test asserts ODYSSEY `SECOND_SOURCE_DIFFERENT_MEASURE`, measure type `percentage ratio`, `registry_effect_label == "CT.gov percentage ratio"`, and `corroborates_endpoint is False`.
- `test_synthetic_identical_endpoint_allows_corroboration` builds a count-derived RR control and asserts `IDENTICAL_ENDPOINT`, the exact identity object, `corroborates_endpoint is True`, and `ctgov_rr == 0.8`.

Targeted run:

```text
python -m pytest tests/test_cross_source.py tests/test_cross_source_endpoint.py tests/test_second_source_identity.py -q
13 passed in 19.45s
```

## 3. Rebuilt Pages And Changed Blocks

MEASURED sweep:

```text
python scripts/second_source_sweep.py
0 rows labelled corroboration whose endpoint identity is unverified or wrong of 10 cross-source rows over 32 topics
C:\mh-r-XS2\docs\second_source_sweep.json
```

MEASURED verdict counts: `IDENTICAL_ENDPOINT=1`, `SECOND_SOURCE_DIFFERENT_MEASURE=5`, `SECOND_SOURCE_DIFFERENT_ENDPOINT=4`. Agreement statistics are computed only on `IDENTICAL_ENDPOINT`: `rows_considered=1`, `rows_excluded=9`, `max_abs_log_delta=0.014857823842445142`.

Rows named by sweep:

| Row | Verdict | Corroboration |
|---|---|---|
| `denosumab-vertebral-fracture::New vertebral fracture::PMID 19671655` | `IDENTICAL_ENDPOINT` | true |
| `denosumab-vertebral-fracture::Nonvertebral fracture::PMID 19671655` | `SECOND_SOURCE_DIFFERENT_MEASURE` | false |
| `denosumab-vertebral-fracture::Hip fracture::PMID 19671655` | `SECOND_SOURCE_DIFFERENT_MEASURE` | false |
| `omega3-cardiovascular-events::Major vascular events / MACE::PMID 33190147` | `SECOND_SOURCE_DIFFERENT_ENDPOINT` | false |
| `omega3-cardiovascular-events::Major vascular events / MACE::PMID 30415637` | `SECOND_SOURCE_DIFFERENT_MEASURE` | false |
| `omega3-cardiovascular-events::Major vascular events / MACE::PMID 30146932` | `SECOND_SOURCE_DIFFERENT_ENDPOINT` | false |
| `pcsk9-mace::Major adverse cardiovascular events::PMID 28304224` | `SECOND_SOURCE_DIFFERENT_MEASURE` | false |
| `pcsk9-mace::Major adverse cardiovascular events::PMID 30403574` | `SECOND_SOURCE_DIFFERENT_MEASURE` | false |
| `semaglutide-obesity-mace::3-point major adverse cardiovascular events::PMID 37952131` | `SECOND_SOURCE_DIFFERENT_ENDPOINT` | false |
| `spironolactone-hfref-mortality::All-cause mortality::PMID 21073363` | `SECOND_SOURCE_DIFFERENT_ENDPOINT` | false |

Rebuilt pages and before/after blocks:

- `denosumab-vertebral-fracture`: new vertebral fracture stays corroborated but is now `IDENTICAL_ENDPOINT`; nonvertebral and hip fracture changed from `SAME_ENDPOINT` corroboration to `SECOND_SOURCE_DIFFERENT_MEASURE` because the registry value is a risk ratio from counts while the pooled value is HR.
- `omega3-cardiovascular-events`: rows for PMID 33190147 and PMID 30146932 changed from `SAME_ENDPOINT` corroboration to `SECOND_SOURCE_DIFFERENT_ENDPOINT` because registry component sets do not match or cannot verify the pooled trial component set; PMID 30415637 changed to `SECOND_SOURCE_DIFFERENT_MEASURE` because CT.gov count RR is not pooled HR.
- `pcsk9-mace`: FOURIER changed from XS `DIFFERENT_ENDPOINT` wording to typed `SECOND_SOURCE_DIFFERENT_MEASURE` (`KM estimate ratio`, 0.881); ODYSSEY changed from `SAME_ENDPOINT` corroboration to `SECOND_SOURCE_DIFFERENT_MEASURE` (`percentage ratio`, 0.856).
- `semaglutide-obesity-mace`: SELECT changed from `SAME_ENDPOINT` corroboration to `SECOND_SOURCE_DIFFERENT_ENDPOINT` because the declared composite component set is not available for the cross-source identity check.
- `spironolactone-hfref-mortality`: EPHESUS remains non-corroborating but is now typed as `SECOND_SOURCE_DIFFERENT_ENDPOINT` with the pooled HR/RR and CT.gov risk ratio shown.

Replay checks:

```text
python scripts/reproduce_review.py denosumab-vertebral-fracture
  OK  denosumab-vertebral-fracture
1/1 reproduce (all reproducible)

python scripts/reproduce_review.py omega3-cardiovascular-events
  OK  omega3-cardiovascular-events
1/1 reproduce (all reproducible)

python scripts/reproduce_review.py pcsk9-mace
  OK  pcsk9-mace
1/1 reproduce (all reproducible)

python scripts/reproduce_review.py semaglutide-obesity-mace
  OK  semaglutide-obesity-mace
1/1 reproduce (all reproducible)

python scripts/reproduce_review.py spironolactone-hfref-mortality
  OK  spironolactone-hfref-mortality
1/1 reproduce (all reproducible)
```

## 4. Tests

MEASURED targeted XS2 run:

```text
python -m pytest tests/test_cross_source.py tests/test_cross_source_endpoint.py tests/test_second_source_identity.py -q
13 passed in 19.45s
```

MEASURED first full run exposed only generated fix-state staleness:

```text
python -m pytest tests -x -q
1 failed, 212 passed in 902.17s (0:15:02)
FAILED tests/test_fixstate.py::test_real_store_validates
docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
```

MEASURED generated refresh and targeted recheck:

```text
python scripts/render_fix_ledger.py
rendered docs/fix_ledger.json

python -m pytest tests/test_fixstate.py::test_real_store_validates -q
1 passed in 454.51s (0:07:34)
```

MEASURED final full run:

```text
python -m pytest tests -x -q
721 passed in 1215.00s (0:20:14)
```

MEASURED: `git diff --check` passed with no output.

## 5. What I Did Not Do

- Did not commit.
- Did not run network searches or fetches.
- Did not touch pooling, membership, screening, search, `harness/synth.py`, or trial inclusion.
- Did not write ratchet acknowledgements.
- Did not run `scripts/verify_all.py`.

## 6. Files Changed Or Added

Code/tests/scripts:

- `harness/second_source.py`
- `harness/ctgov_results.py`
- `harness/pipeline.py`
- `harness/page.py`
- `scripts/second_source_sweep.py`
- `tests/test_second_source_identity.py`
- `tests/test_cross_source_endpoint.py`

Generated sweep/report:

- `docs/second_source_sweep.json`
- `LANE-XS2-REPORT.md`

Rebuilt pages and replay artefacts:

- `docs/m/m078be06c/index.html`
- `docs/m/m3c1155fb/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/me5d639f4/index.html`
- `docs/m/mf6cd36c2/index.html`
- `docs/reviews/denosumab-vertebral-fracture/REPRODUCTION.json`
- `docs/reviews/denosumab-vertebral-fracture/index.html`
- `docs/reviews/denosumab-vertebral-fracture/manifest.json`
- `docs/reviews/denosumab-vertebral-fracture/review.json`
- `docs/reviews/omega3-cardiovascular-events/REPRODUCTION.json`
- `docs/reviews/omega3-cardiovascular-events/index.html`
- `docs/reviews/omega3-cardiovascular-events/manifest.json`
- `docs/reviews/omega3-cardiovascular-events/review.json`
- `docs/reviews/pcsk9-mace/REPRODUCTION.json`
- `docs/reviews/pcsk9-mace/index.html`
- `docs/reviews/pcsk9-mace/manifest.json`
- `docs/reviews/pcsk9-mace/review.json`
- `docs/reviews/semaglutide-obesity-mace/REPRODUCTION.json`
- `docs/reviews/semaglutide-obesity-mace/index.html`
- `docs/reviews/semaglutide-obesity-mace/manifest.json`
- `docs/reviews/semaglutide-obesity-mace/review.json`
- `docs/reviews/spironolactone-hfref-mortality/REPRODUCTION.json`
- `docs/reviews/spironolactone-hfref-mortality/index.html`
- `docs/reviews/spironolactone-hfref-mortality/manifest.json`
- `docs/reviews/spironolactone-hfref-mortality/review.json`
- `registry/blind_map.json`

Generated fix-state artefact:

- `docs/fix_ledger.json`

Pre-existing untracked lane-control files were not created as part of the change set: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
