# LANE XS Report

## 1. What Was Wrong

MEASURED: `pcsk9-mace` / FOURIER (`PMID 28304224`, `NCT01764633`) rendered the CT.gov cross-source row as `second source (· corroboration)` even though the committed pre-fix row had `CT.gov RR 0.666` beside the pooled published `HR 0.85`.

Mechanism: `harness/pipeline.py::_cross_source` treated any selected CT.gov structured outcome as cross-source corroboration when the abstract row had no count-derived RR. `harness/page.py` then rendered `agree is None` as `· corroboration`. `harness/ctgov_results.py` also did not carry enough registry outcome metadata to distinguish participant counts from CT.gov `NUMBER`/KM percentage rows.

Files changed for the mechanism:

- `harness/ctgov_results.py`: carries registry title, CT.gov type/param type, selected measure type, selected timepoint, time frame, population, raw values, and registry-implied effect.
- `harness/pipeline.py`: adds endpoint-match classification with `CROSS_SOURCE_LOG_TOL = 0.12`; writes `endpoint_match`, reason, and `corroborates_endpoint`.
- `harness/page.py`: only `corroborates_endpoint` renders as corroboration; other rows render `registry reports a DIFFERENT measure: <title>`.
- `scripts/cross_source_endpoint_sweep.py`: corpus-wide sweep.
- `docs/cross_source_endpoint_sweep.json`: generated sweep artefact.

Static-vs-dynamic disclosure:

| Item | Source | Disclosure |
|---|---|---|
| Endpoint-match tolerance | Static code constant | `CROSS_SOURCE_LOG_TOL = 0.12` in `harness/pipeline.py`; tests assert the FOURIER pre-fix mismatch exceeds it. |
| Registry rows and values | Dynamic, committed cache | Rebuilt from `cache/<slug>/records.json`; no network. |
| Sweep denominator | Dynamic, served review set | `docs/reviews/*/review.json`; MEASURED 32 topics. |

## 2. Plant

Test file: `tests/test_cross_source_endpoint.py`.

Plant assertion: `test_prefix_fourier_corroboration_plant_refuses_endpoint_mismatch` loads the committed pre-fix object with read-only `git show aa8ed28a:docs/reviews/pcsk9-mace/review.json` and the committed pre-fix HTML with `git show aa8ed28a:docs/reviews/pcsk9-mace/index.html`.

MEASURED pre-fix facts from the plant:

- `old_cs["ctgov_rr"] == 0.666`
- `old_row["effect"] == 0.85`
- `abs(log(0.85 / 0.666)) > 0.12`
- old HTML contained: `second source (· corroboration): CT.gov RR 0.666... shown for corroboration only`

MEASURED check output on the pre-fix object: `_classify_endpoint_match(...)` returns `DIFFERENT_ENDPOINT` with reason containing `registry-implied value 0.666 differs from pooled 0.85 ... > tolerance 0.12`.

MEASURED post-fix rebuilt object: `test_rebuilt_fourier_row_is_different_measure_not_corroboration` rebuilds `pcsk9-mace` from committed cache and asserts:

- `endpoint_match == "DIFFERENT_ENDPOINT"`
- `corroborates_endpoint is False`
- `registry_measure_type == "KM_ESTIMATE"`

MEASURED synthetic control: `test_synthetic_same_endpoint_control_is_counted` builds a registry row whose proportions reproduce the pooled effect and asserts `SAME_ENDPOINT`, `corroborates_endpoint is True`, and `ctgov_rr == 0.8`.

Targeted plant run:

```text
........                                                                 [100%]
8 passed in 7.38s
```

## 3. Rebuilt Pages And Changed Sentences

MEASURED sweep artefact: `python scripts/cross_source_endpoint_sweep.py`

```text
2 mismatched of 10 cross-source registry rows over 32 topics
C:\mh-r-XS\docs\cross_source_endpoint_sweep.json
```

MEASURED sweep table:

| slug | trial_key | pooled | registry-implied | registry type | verdict |
|---|---:|---:|---:|---|---|
| denosumab-vertebral-fracture | PMID 19671655 | RR 0.32 | 0.32479 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| denosumab-vertebral-fracture | PMID 19671655 | HR 0.8 | 0.813119 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| denosumab-vertebral-fracture | PMID 19671655 | HR 0.6 | 0.605271 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| omega3-cardiovascular-events | PMID 33190147 | RR 0.987421 | 0.987421 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| omega3-cardiovascular-events | PMID 30415637 | HR 0.92 | 0.921597 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| omega3-cardiovascular-events | PMID 30146932 | RR 0.97 | 0.967697 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| pcsk9-mace | PMID 28304224 | HR 0.85 | 0.881029 | KM_ESTIMATE | DIFFERENT_ENDPOINT |
| pcsk9-mace | PMID 30403574 | HR 0.85 | 0.855856 | PERCENTAGE | SAME_ENDPOINT |
| semaglutide-obesity-mace | PMID 37952131 | HR 0.8 | 0.811513 | COUNT_OF_PARTICIPANTS | SAME_ENDPOINT |
| spironolactone-hfref-mortality | PMID 21073363 | HR 0.76 | 0.722813 | COUNT_OF_PARTICIPANTS | DIFFERENT_ENDPOINT |

MEASURED rebuilt pages and primary estimates:

- `denosumab-vertebral-fracture`: k=1, estimate 0.32 RR; cross-source rows now render `✓ corroborated` with `SAME_ENDPOINT`.
- `omega3-cardiovascular-events`: k=7, estimate 0.943 RR; three cross-source rows now render same-endpoint metadata.
- `pcsk9-mace`: k=2, estimate 0.85 HR; FOURIER changed from `second source (· corroboration): CT.gov RR 0.666... shown for corroboration only` to `registry reports a DIFFERENT measure: Time to Cardiovascular Death... CT.gov RR 0.881. type KM_ESTIMATE; timepoint KM estimate at 6 months... DIFFERENT_ENDPOINT`.
- `semaglutide-obesity-mace`: k=1, estimate 0.8 HR; row now renders same-endpoint metadata.
- `spironolactone-hfref-mortality`: k=3, estimate 0.8685 RR/HR; EPHESUS registry row now renders `registry reports a DIFFERENT measure: Number of Participants With First Occurrence of All-Cause Mortality or Heart Failure...`.

MEASURED replay checks:

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

MEASURED: first full run exposed stale generated fix-state artefacts:

```text
1 failed, 187 passed in 518.86s (0:08:38)
```

The failure named generated-state repairs only:

- `python scripts/render_fix_ledger.py`
- `python scripts/rewrite_fixstate_lines.py`

MEASURED after running those scripts:

```text
python -m pytest tests/test_fixstate.py::test_real_store_validates -q
.                                                                        [100%]
1 passed in 234.34s (0:03:54)
```

Final required lane command, verbatim summary:

```text
python -m pytest tests -x -q
642 passed in 548.95s (0:09:08)
```

MEASURED: `git diff --check` passed with no output.

## 5. What I Did Not Do

- Did not commit.
- Did not run network searches or fetches.
- Did not change pooling, `harness/synth.py`, `harness/extract.py`, `harness/rob_sensitivity.py`, `harness/grade.py`, search code, or which trials are pooled.
- Did not run `scripts/verify_all.py`.
- Did not add/remove any trial from any pool.

## 6. Files Changed Or Added

Code/tests/scripts:

- `harness/ctgov_results.py`
- `harness/page.py`
- `harness/pipeline.py`
- `scripts/cross_source_endpoint_sweep.py`
- `tests/test_cross_source_endpoint.py`

Generated sweep/report:

- `docs/cross_source_endpoint_sweep.json`
- `LANE-XS-REPORT.md`

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

Generated fix-state artefacts required for the final full test pass:

- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `docs/fix_ledger.json`

Pre-existing untracked lane files (`LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`) were not created by this change set.
