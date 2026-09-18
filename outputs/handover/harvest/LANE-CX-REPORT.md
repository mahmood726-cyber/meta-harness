# LANE CX Report

## 1. What was wrong, mechanism, files

[MEASURED] On the pre-fix object `ad5e7c66:docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json`, SMART/SALT/SPLIT were analytically refused by the design key, but their absence states were mixed:

| trial | pre-fix state | post-fix state |
|---|---:|---:|
| SMART / PMID 29485925 | `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH` | `ENGINE_CANNOT_CONSUME` |
| SALT / PMID 27749094 | `REFUSED_ON_EVIDENCE` | `ENGINE_CANNOT_CONSUME` |
| SPLIT / PMID 26444692 | `EXTRACTION_NOT_PERFORMED` | `ENGINE_CANNOT_CONSUME` |

[INFERRED] The detector was mostly right; the downstream consumers were wrong. A design refusal means the engine lacks a design-aware variance model, not that mortality evidence is absent.

Main implementation:

- Added `harness/design_variance.py`: `ENGINE_CANNOT_CONSUME`, ICC design-effect inflation, refusal rows, design-consumption summaries, stale-consumer checks.
- Wired `harness/pipeline.py` additively: source-reported adjusted effects still use `design_key`; ICC design-effect rows become consumable only with held ICC/cluster size; otherwise rows are preserved as `ENGINE_CANNOT_CONSUME(missing=design_adjusted_effect|ICC)`.
- Updated `harness/absence.py`, `harness/page.py`, `harness/limitations.py`, `harness/hazard_consumers.py`, and `harness/claimgraph.py` so absence labels, GRADE rationale, limitation objects, hazard consumers, and claimgraph stamps all read the new state.
- Added `scripts/design_refusal_sweep.py` and wrote `docs/design_refusal_sweep.json`.

Static-vs-dynamic disclosure:

| item | kind | disclosure |
|---|---|---|
| `ENGINE_CANNOT_CONSUME` / `design_adjusted_effect|ICC` | static code vocabulary | State labels only; not evidence claims. |
| ICC formula `1 + (m-1)*ICC` | static statistical formula | Only applied when `design_adjustment` holds ICC and cluster size. |
| k/counts/headlines | dynamic | Derived from rebuilt `review.json`, not typed into page prose. |
| sweep counts | dynamic | Derived by `scripts/design_refusal_sweep.py` from 32 served `docs/reviews/*/review.json` files. |
| FISSH ledger line | static ledger annotation | Ledger-only `REACH_MISS(registry, completed, no results)`; no screening or pool membership change. |

## 2. The plant

[MEASURED] `tests/test_design_variance.py::test_prefix_object_fires_and_rebuilt_object_passes_design_variance_check` loads the committed pre-fix object with `git show ad5e7c66...` and asserts these failures fire:

`HEADLINE_MISSING_DESIGN_CONSUMPTION`, `DESIGN_REFUSAL_NOT_ENGINE_CODE`, `GRADE_MISSING_DESIGN_VARIANCE_RATIONALE`, `STALE_ARM_CONTRAST_DENOMINATOR`, `STALE_PROTOCOL_CONTROL_EXPECTATION`.

[MEASURED] The same check on the rebuilt object returns `[]`.

[MEASURED] The raw SPLIT 2x2 plant remains refused: `Study.yi_vi()` raises before a naive cluster-crossover reconstructed SE can enter the parallel engine.

[MEASURED] ICC synthetic plant: variance equals raw 2x2 variance multiplied by `1 + (50 - 1) * 0.02`.

[MEASURED] Focused lane tests:

`python -m pytest tests/test_design_variance.py tests/test_design_key.py -q`

`12 passed in 5.96s`

## 3. Rebuilt pages and reworded blocks

[MEASURED] Rebuilt:

- `docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html`
- `docs/m/m89f8021b/index.html`

[MEASURED] Replay:

- `python scripts/reproduce_review.py balanced-crystalloids-vs-saline-mortality`
- `OK balanced-crystalloids-vs-saline-mortality`
- `1/1 reproduce (all reproducible)`

[MEASURED] Reworded/generated blocks:

- Overview/Results: `pooled: the subset this engine can safely consume (k=2 of 5 eligible with mortality data; 3 refused for want of a variance model)`.
- Results design refusal: `ENGINE_CANNOT_CONSUME design variance`; evidence is not absent, but the engine lacks a held design-adjusted effect or ICC design-effect variance.
- PRISMA flow: added `Eligible with outcome retrieved but refused (engine cannot consume design variance)` with `[MEASURED] 3` rows; the old not-extracted bucket no longer includes SMART/SALT/SPLIT.
- Risk-of-bias arm contrast: stale `2 of 5` block is `UNRENDERABLE`; current block says `[MEASURED] 2 of 2` pooled trials have registry-confirmed contrast.
- Protocol tab: stale BaSICS expected-fail-closed control is `UNRENDERABLE` because live screening includes BaSICS.
- GRADE basis now includes: evidence refused for want of a variance model is distinct from evidence absent.

[MEASURED] Sweep output from `docs/design_refusal_sweep.json`:

- `n_pages`: 32.
- design-refused trials: `3 of 100` eligible-with-outcome trials.
- by design: `CLUSTER_CROSSOVER: 3`.
- design-adjusted effect held: `not_held: 3`.
- pages whose headline k is a consumable subset: `1 of 32`.
- pages mixing estimands against declared protocol estimand: `8 of 32`.

## 4. Tests

[MEASURED] Full suite:

`python -m pytest tests -x -q`

`725 passed in 487.89s (0:08:07)`

[MEASURED] Additional checks run:

- `python scripts/reproduce_review.py probiotics-aad-prevention` -> `1/1 reproduce (all reproducible)` after tightening generic drift.
- `python -m pytest tests/test_design_variance.py tests/test_design_key.py tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews tests/test_fixstate.py::test_real_store_validates -q` -> `14 passed in 177.08s`.

## 5. What I did not do

- Did not commit.
- Did not modify `harness/synth.py`.
- Did not run network retrieval or alter screening/search membership for CRUSADERS or other trials.
- Did not implement TBI/non-TBI strands or the lane-TE RR-only estimand repair; this CX lane measures estimand mixing in the sweep but only changes design-variance consumption.
- Did not write ratchet acknowledgements; reworded blocks are listed above for the integrator to sign.

## 6. Files changed or added

Changed:

- `docs/evidence/design-key-2026-09-14/README.md`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/fix_ledger.json`
- `docs/m/m89f8021b/index.html`
- `docs/never_considered.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/REPRODUCTION.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/manifest.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json`
- `harness/absence.py`
- `harness/claimgraph.py`
- `harness/design_key.py`
- `harness/hazard_consumers.py`
- `harness/limitations.py`
- `harness/page.py`
- `harness/pipeline.py`
- `registry/blind_map.json`
- `tests/test_design_key.py`

Added:

- `LANE-CX-REPORT.md`
- `docs/design_refusal_sweep.json`
- `harness/design_variance.py`
- `scripts/design_refusal_sweep.py`
- `tests/test_design_variance.py`
