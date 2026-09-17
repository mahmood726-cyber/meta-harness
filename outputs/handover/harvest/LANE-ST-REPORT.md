# LANE ST REPORT

## 1. What was wrong, mechanism, files

MEASURED correction from `ad5e7c66`: the lane premise "STAREE is missing" was false. STAREE (PMID 42670961) was already screened-in and pooled in `statins-primary-prevention-elderly` at base.

- Base primary result: k=2, HR 0.6803, registered CI refused as `K2_SINGLE_DF`.
- Base pooled rows: JUPITER older-adult subgroup (PMID 20404379, HR 0.61) and STAREE (PMID 42670961, HR 0.70).
- Base defect: both rows lacked `population_basis`; STAREE lacked `endpoint_change`; HOPE-3/PROSPER/ALLHAT/comparator dispositions were not machine-readable; the age-threshold/subgroup basis was not carried as data.

Mechanism fixed:

- Added `population_basis` as a disclosed compatibility dimension in `harness/compat.py`.
- Carried `population_basis`, `subgroup_basis`, and `endpoint_change` from the topic spec through `harness/pipeline.py`.
- Rendered population basis, subgroup basis, endpoint-change details, declared strands, named dispositions, and known-missing age-subgroup evidence in `harness/page.py`.
- Mirrored the new overview banners in `harness/limitations.py` so honest-ratchet page/object parity stays exact.
- Amended `protocols/statins-primary-prevention-elderly.md` to state the population-basis dimension, executable age threshold, canonical endpoint rule, STAREE endpoint-change rule, and named HOPE-3/PROSPER/ALLHAT obligations.

Static-vs-dynamic disclosure:

| Item | Type | Source / validation |
| --- | --- | --- |
| STAREE arm counts 297/4984 vs 412/4987 | Static source-backed audit metadata | `cache/statins-primary-prevention-elderly/verified_arms.json`; test asserts not used as reconstructed pool input |
| STAREE HR 0.70 (0.61-0.82) | Dynamic extracted/preserved pooled row | Built review keeps `effect=0.7`, `scale=HR`, `derivation=reported` |
| Population-basis compatibility key | Dynamic generated field | `compat.outcome_key()` now emits heterogeneous `DIRECT` vs `SUBGROUP_OF_BROADER_TRIAL` |
| HOPE-3/PROSPER/ALLHAT/comparator dispositions | Static typed declarations | `topics/statins-primary-prevention-elderly.json`, rendered into review/page and tested |
| Population-basis sweep | Dynamic generated artifact | `scripts/population_basis_sweep.py` writes `docs/population_basis_sweep.json` over 32 review pages |

## 2. Plant

Test file: `tests/test_staree_recovery.py`.

Key pre-fix/base assertions:

```python
assert base_staree["effect"] == 0.7
assert "population_basis" not in base_staree
assert "endpoint_change" not in base_staree
assert "population_basis" not in (base_primary.get("compat_key") or {})
assert "strands" not in base
assert "EXTRA_PMIDS" not in {s["kind"] for s in base_ledger["sources"]}
```

Key post-fix assertions:

```python
assert staree["population_basis"] == "DIRECT"
assert jupiter["population_basis"] == "SUBGROUP_OF_BROADER_TRIAL"
assert jupiter["subgroup_basis"]["randomisation_preserved"] is True
assert staree["endpoint_change"]["code"] == "ENDPOINT_CHANGED_PRE_ANALYSIS"
assert screening["42670961"]["found_by"] == ["legacy_unrecorded#1"]
assert "EXTRA_PMIDS" not in {s["kind"] for s in ledger["sources"]}
assert dispositions["HOPE-3 older-age subgroup"]["status"] == "REACH_MISS(named)"
assert dispositions["PROSPER primary-prevention subgroup"]["status"] == "IN_SOURCE_NOT_HELD"
assert live["age_threshold"]["status"] == "EXECUTABLE"
```

Pre-fix output captured before applying the fix, after rewriting the plant against the true base state:

```text
.FFF
FAILED tests/test_staree_recovery.py::test_live_staree_recovery_contract... KeyError: 'population_basis'
FAILED tests/test_staree_recovery.py::test_statins_strands_and_named_trial_dispositions_are_machine_readable KeyError: 'trial_dispositions'
FAILED tests/test_staree_recovery.py::test_population_basis_sweep_counts_statins_page AssertionError: assert False
3 failed, 1 passed in 2.48s
```

Post-fix output:

```text
....                                                                     [100%]
4 passed in 1.72s
```

## 3. Rebuilt pages / bytes and before-after facts

MEASURED bytes, `ad5e7c66` -> final working tree:

| Artifact | Before bytes | After bytes |
| --- | ---: | ---: |
| `protocols/statins-primary-prevention-elderly.md` | 4112 | 6054 |
| `docs/reviews/statins-primary-prevention-elderly/review.json` | 120643 | 136455 |
| `docs/reviews/statins-primary-prevention-elderly/index.html` | 88391 | 94964 |
| `docs/reviews/statins-primary-prevention-elderly/manifest.json` | 2016 | 2016 |
| `docs/reviews/statins-primary-prevention-elderly/REPRODUCTION.json` | 2610 | 2610 |
| `docs/m/mb53e1ed5/index.html` | 71058 | 75483 |
| `docs/m/ma178f5d6/index.html` | 12204 | 12248 |
| `registry/blind_map.json` | 223 | 238 |
| `docs/fix_ledger.json` | 322761 | 323700 |

MEASURED result facts:

- Primary result unchanged: base k=2 HR 0.6803, CI `None-None`, `K2_SINGLE_DF`; final k=2 HR 0.6803, CI `None-None`, `K2_SINGLE_DF`.
- GRADE unchanged: base `moderate`, 1 downgrade; final `moderate`, 1 downgrade.
- Base pooled rows had no `population_basis`; final rows are JUPITER=`SUBGROUP_OF_BROADER_TRIAL` with age subgroup basis, STAREE=`DIRECT` with `ENDPOINT_CHANGED_PRE_ANALYSIS`.
- Final compatibility key records `population_basis` as heterogeneous: values `DIRECT` and `SUBGROUP_OF_BROADER_TRIAL`.
- Final named dispositions: HOPE-3 older-age subgroup=`REACH_MISS(named)`; PROSPER primary-prevention subgroup=`IN_SOURCE_NOT_HELD`; ALLHAT-LLT=`REFUSED_ON_PROTOCOL`; observational comparator=`CONTEXTUAL_ONLY`.
- Final age threshold object: `EXECUTABLE`, protocol minimum 70 years, recognized subgroup thresholds 65/70/75.
- Final sweep over 32 pages: statins has 2 pooled rows, 1 direct row, 1 subgroup-of-broader-trial row, `subgroup_only=false`.

Reworded/new page blocks needing integrator acknowledgement if the ratchet requires signatures:

- Statins overview: new "Known named age-subgroup evidence not yet consumed" absent block.
- Statins overview: new "Population-basis and endpoint strands" banner.
- Statins Results compatibility key: new Population basis row and limitation sentence.
- Statins trial input table: new compatibility row fields for population basis, subgroup basis, endpoint change, and components.
- Statins Screening tab: new Named trial dispositions table.
- Protocol tab text changed by the 2026-09-16 amendment.

## 4. Tests / commands

```text
python scripts/build_topic.py statins-primary-prevention-elderly --now 2026-09-11
PRIMARY: Major vascular events  k=2  RR=0.6803 (None-None)  tau2=0.0
```

```text
python scripts/reproduce_review.py statins-primary-prevention-elderly
  OK  statins-primary-prevention-elderly

1/1 reproduce (all reproducible)
```

```text
python -m pytest tests/test_staree_recovery.py -q
4 passed in 1.72s
```

```text
python -m pytest tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews -q
1 passed in 3.77s
```

```text
python -m pytest tests -x -q
720 passed in 240.69s (0:04:00)
```

## 5. What I did not do

- Did not commit.
- Did not fetch or use network.
- Did not edit `harness/synth.py`.
- Did not change K2 policy; the k=2 CI remains refused.
- Did not add STAREE as `EXTRA_PMIDS`; the integrator correction says that would fabricate provenance because STAREE was already held and pooled.
- Did not re-pool STAREE from crude counts; counts are audit metadata only, and the pooled input remains the published HR.
- Did not write ratchet acknowledgements; I listed the reworded/new blocks above for integrator handling.
- Did not push or deploy.

## 6. Files changed or added

Modified:

- `cache/statins-primary-prevention-elderly/retrieval_ledger.json`
- `docs/fix_ledger.json`
- `docs/m/ma178f5d6/index.html`
- `docs/m/mb53e1ed5/index.html`
- `docs/reviews/statins-primary-prevention-elderly/REPRODUCTION.json`
- `docs/reviews/statins-primary-prevention-elderly/index.html`
- `docs/reviews/statins-primary-prevention-elderly/manifest.json`
- `docs/reviews/statins-primary-prevention-elderly/review.json`
- `harness/compat.py`
- `harness/limitations.py`
- `harness/page.py`
- `harness/pipeline.py`
- `protocols/statins-primary-prevention-elderly.md`
- `registry/blind_map.json`
- `topics/statins-primary-prevention-elderly.json`

Added:

- `cache/statins-primary-prevention-elderly/verified_arms.json`
- `docs/population_basis_sweep.json`
- `docs/statins_population_strands.json`
- `scripts/population_basis_sweep.py`
- `tests/test_staree_recovery.py`
- `LANE-ST-REPORT.md`

Read/honored but not authored here:

- `LANE_PROMPT.md`
- `INTEGRATOR_CORRECTION.md`
