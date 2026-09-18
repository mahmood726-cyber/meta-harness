# LANE KM report

## 1. What was wrong, mechanism, files

MEASURED failure mechanism: pages could set `known_eligible_missing` or name eligible declared-absent trials in `invalidation.reasons`, but the primary outcome had no structured `known_missing_sensitivity` object and the page rendered only a generic STALE banner. The reader saw that the pool was incomplete, but not what the named missing evidence could do.

Implemented mechanism:
- `harness/known_missing.py` builds a dependency-stamped `known_missing_sensitivity` object after invalidation.
- `harness/pipeline.py` invokes that builder before limitations are frozen.
- `harness/page.py` renders the panel under the primary result and links to it from the STALE banner.
- `harness/gate.py::check_known_missing_panel` refuses pages that name known missing evidence without a panel, and refuses numeric panel rows without committed-source span and verify basis.
- `harness/limitations.py` now reuses the page stale-banner helper so limitation objects and rendered blocks stay byte-consistent.
- `registry/gate_scorecard.json` and `docs/gate_scorecard.json` record the new gate.

Static-vs-dynamic disclosure:

| Item | Status | Basis |
| --- | --- | --- |
| COCS row counts `21/113 vs 39/127` | MEASURED/static | Extracted from committed `cache/colchicine-postop-af/records.json#36286314.abstract`; used only for the sensitivity panel. |
| COPPS row counts `20/169 vs 37/167` | MEASURED/static reconstruction | Reconstructed from committed abstract percentages and denominator in `cache/colchicine-postop-af/records.json#22090167.abstract`; used only for the sensitivity panel. |
| FLOW/FREEDOM-CVO effects | MEASURED absent | Not in the committed topic cache as target-estimand values; rows are `NOT_IN_COMMITTED_SOURCE` and compute no number. |
| Pooling calculations | MEASURED/dynamic | Computed with `harness.synth.pool`, same estimator as the page primary result. |

## 2. Plants

Plant tests added in `tests/test_known_missing_panel.py`.

Exact pre-fix assertions:
- `test_gate_fires_on_prefix_glp1_named_missing_without_panel`: `assert any("known_missing_sensitivity panel" in r for r in reasons), reasons`
- `test_gate_fires_on_prefix_colchicine_eligible_declared_absent_without_panel`: `assert any("known_missing_sensitivity panel" in r for r in reasons), reasons`
- `test_uncommitted_missing_trial_has_no_numeric_fields`: asserts `value_status == "NOT_IN_COMMITTED_SOURCE"`, no `sensitivity`, and no numeric fields.
- `test_committed_counts_sensitivity_equals_direct_synth_pool`: asserts the panel sensitivity equals a direct `synth.pool` call.

MEASURED pre-fix gate output on `aa8ed28a` objects:

```text
PREFIX glp1-ra-mace-t2d ['L1: known eligible missing evidence is named but the primary outcome has no known_missing_sensitivity panel']
PREFIX colchicine-postop-af ['L1: known eligible missing evidence is named but the primary outcome has no known_missing_sensitivity panel']
```

MEASURED post-fix gate output:

```text
POSTFIX glp1-ra-mace-t2d []
POSTFIX colchicine-postop-af []
```

MEASURED plant test run:

```text
......                                                                   [100%]
6 passed in 2.77s
```

## 3. Pages whose rebuilt bytes changed

MEASURED rebuilt lane set: `6 of 32` pages with `known_eligible_missing`: `glp1-ra-mace-t2d`, `colchicine-postop-af`, `corticosteroids-cap-mortality`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `iv-iron-hfref-hosp`.

MEASURED hashes changed:
- `glp1-ra-mace-t2d`: `d77d184aa10edacf25ae55a4426cf790eb37268d6f26d1523326cdb2a00ac2e2` -> `e97529036a7dbce4a75c3a2809b88ad909e71db333886d2d576d527ba07fcb5e`
- `colchicine-postop-af`: `1d645bc2ec5d8f3c3c2b3d0b5eceabf10b18680445061f23c1337378c8507b26` -> `1b8070a4ac6557ca64a88736145a457c119720afde10c4ffb595dad7a5013849`
- `corticosteroids-cap-mortality`: `eb09279de9273db5c73a20517c597a844967dccaeca0c5b3294ad334a8e247ff` -> `726476cabd63770835c36945fc1bc4f6e7849de2a0c6b6b89eb7278af5a17da1`
- `dpp4-mace-t2d`: `aaba73ab39328868f497fd7ce4411fd900e9451bec43ed1f984657f5e1988379` -> `789f5421ee2122ebc0174a43936ef525ce5eb743f926724718cb07784d49bb52`
- `empagliflozin-hfpef-hosp`: `3da9508c15b1f6590e66b042b927030bf73bdf7bd3ff15ebe7af4bc571b3d60d` -> `55012542b6b9e76b7c03cb57695a7a53912ad112607f5d379f7ed32a9d9eecf9`
- `iv-iron-hfref-hosp`: `b7f9ff4e7a5babc3cee14b435789f8f6c37f4f348954312c30f9cc81176c616d` -> `e6d53d62eff55bcaebdbe4822b71bcfecc1b637729531fa6eda3a12e1f563552`
- `probiotics-aad-prevention`: `9e6a3aca11d196e8d4767b28a638dee8a038ccd2bf93e006f54564cf3505cd05` -> `c6984e656d0591254149aeaf4bce4e4a838e5887ef9c8d903d8ce46bc07f73df`

MEASURED page deltas:
- `glp1-ra-mace-t2d`: primary unchanged at `k=8`, `HR 0.856 [0.8086, 0.9061]`, `tau2=0.00004`. Before: no known-missing panel. After: panel headline `NOT_COMPUTABLE`; rows `FLOW` and `FREEDOM-CVO` are `NOT_IN_COMMITTED_SOURCE` with no sensitivity; row `26630143` is `EXTRACTION_DEBT` but no target-estimand value; components render as `CV_DEATH | NONFATAL_MI | NONFATAL_STROKE`. STALE banner now links to the panel.
- `colchicine-postop-af`: primary unchanged at `k=4`, `RR 0.6735 [0.376, 1.2067]`, `tau2=0.07415`. Before: no known-missing panel. After: COCS row `21/113 vs 39/127`, sensitivity `k=5 RR 0.6664 [0.4527, 0.9812]`; COPPS row `20/169 vs 37/167`, sensitivity `k=5 RR 0.6492 [0.431, 0.9777]`; combined sensitivity `k=6 RR 0.6488 [0.4782, 0.8802]`, `tau2=0.02843`, PI `0.3819-1.1023`, `conclusion_effect=CHANGES_CI_NULL_CROSSING`. STALE banner now says the served conclusion is invalidated by named, in-source evidence and links to the panel.
- `corticosteroids-cap-mortality`: primary unchanged at `k=2`, `RR 0.5458 [0.0361, 8.2605]`, `tau2=0.0`. Before: no known-missing panel. After: panel rows for named missing trials are `NOT_IN_COMMITTED_SOURCE` or non-computable extraction debt; no sensitivity number is computed.
- `dpp4-mace-t2d`: primary unchanged at `k=3`, `HR 1.0074 [0.8391, 1.2094]`, `tau2=0.0`. Before: no known-missing panel. After: `TECOS (3-point MACE from primary publication)` and `23992602` compute no number; `26052984` is `IN_SOURCE_DIFFERENT_ESTIMAND`; headline `NOT_COMPUTABLE`.
- `empagliflozin-hfpef-hosp`: primary unchanged at `k=1`, `HR 0.79 [0.69, 0.9]`. Before: no known-missing panel. After: panel rows `EMPA-VISION`, `NCT05138575`, `NCT06249945`, and `NCT03448406` are `NOT_IN_COMMITTED_SOURCE`, no sensitivity number.
- `iv-iron-hfref-hosp`: primary unchanged as suppressed/incompatible: `k=2`, scale `INCOMPATIBLE (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO)`, no pooled estimate. Before: no known-missing panel. After: all named rows are `NOT_IN_COMMITTED_SOURCE`, no sensitivity number.
- `probiotics-aad-prevention`: rebuilt only because the shared page template changed and `tests/test_gate.py` uses it as the real-review replay fixture. Primary unchanged at `k=16`, `RR 0.702 [0.5352, 0.921]`, `tau2=0.15045`. Specific sentence/storage change: stale limitation `rendered_text` now stores a literal rendered dash instead of `&mdash;`, and page CSS adds `.kms-panel`; no known-missing panel was added.

MEASURED reproduce outputs for the six lane pages:

```text
  OK  glp1-ra-mace-t2d
1/1 reproduce (all reproducible)
  OK  colchicine-postop-af
1/1 reproduce (all reproducible)
  OK  corticosteroids-cap-mortality
1/1 reproduce (all reproducible)
  OK  dpp4-mace-t2d
1/1 reproduce (all reproducible)
  OK  empagliflozin-hfpef-hosp
1/1 reproduce (all reproducible)
  OK  iv-iron-hfref-hosp
1/1 reproduce (all reproducible)
```

## 4. Tests

MEASURED final full-suite command:

```text
python -m pytest tests -x -q
645 passed in 157.90s (0:02:37)
```

MEASURED focused checks:

```text
python -m pytest tests/test_known_missing_panel.py tests/test_gate.py tests/test_page.py tests/test_limitations_legacy_compare.py -q
33 passed in 15.76s
```

MEASURED generated-artifact repairs needed during verification:
- `python scripts/render_gate_scorecard.py` after adding `gate.check_known_missing_panel`.
- `python scripts/rewrite_fixstate_lines.py` and `python scripts/render_fix_ledger.py` after page/template rebuilds.

## 5. What I did not do

- Did not commit, stage, stash, reset, checkout, or clean.
- Did not run network search or any network-dependent script.
- Did not add or remove trials from any primary pool. The panel is labelled `SENSITIVITY` and does not replace the primary result.
- Did not touch `harness/synth.py`, `harness/estmeasure.py`, search code, or extractor code.
- Did not import FLOW or FREEDOM-CVO effect values, because the target-estimand values were not in committed topic sources.
- Did not weaken endpoint or estimand gates to make any trial poolable.

## 6. Files changed or added

Added:
- `LANE-KM-REPORT.md`
- `harness/known_missing.py`
- `tests/test_known_missing_panel.py`

Modified code/registry:
- `harness/gate.py`
- `harness/limitations.py`
- `harness/page.py`
- `harness/pipeline.py`
- `registry/gate_scorecard.json`
- `registry/blind_map.json`

Modified generated/served artefacts:
- `docs/gate_scorecard.json`
- `docs/fix_ledger.json`
- `docs/index.html`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`

Modified canonical review artefacts:
- `docs/reviews/glp1-ra-mace-t2d/REPRODUCTION.json`
- `docs/reviews/glp1-ra-mace-t2d/index.html`
- `docs/reviews/glp1-ra-mace-t2d/manifest.json`
- `docs/reviews/glp1-ra-mace-t2d/review.json`
- `docs/reviews/colchicine-postop-af/REPRODUCTION.json`
- `docs/reviews/colchicine-postop-af/index.html`
- `docs/reviews/colchicine-postop-af/manifest.json`
- `docs/reviews/colchicine-postop-af/review.json`
- `docs/reviews/corticosteroids-cap-mortality/REPRODUCTION.json`
- `docs/reviews/corticosteroids-cap-mortality/index.html`
- `docs/reviews/corticosteroids-cap-mortality/manifest.json`
- `docs/reviews/corticosteroids-cap-mortality/review.json`
- `docs/reviews/dpp4-mace-t2d/REPRODUCTION.json`
- `docs/reviews/dpp4-mace-t2d/index.html`
- `docs/reviews/dpp4-mace-t2d/manifest.json`
- `docs/reviews/dpp4-mace-t2d/review.json`
- `docs/reviews/empagliflozin-hfpef-hosp/REPRODUCTION.json`
- `docs/reviews/empagliflozin-hfpef-hosp/index.html`
- `docs/reviews/empagliflozin-hfpef-hosp/manifest.json`
- `docs/reviews/empagliflozin-hfpef-hosp/review.json`
- `docs/reviews/iv-iron-hfref-hosp/REPRODUCTION.json`
- `docs/reviews/iv-iron-hfref-hosp/index.html`
- `docs/reviews/iv-iron-hfref-hosp/manifest.json`
- `docs/reviews/iv-iron-hfref-hosp/review.json`
- `docs/reviews/probiotics-aad-prevention/REPRODUCTION.json`
- `docs/reviews/probiotics-aad-prevention/index.html`
- `docs/reviews/probiotics-aad-prevention/manifest.json`
- `docs/reviews/probiotics-aad-prevention/review.json`

Modified blind-page artefacts:
- `docs/m/m031db369/index.html`
- `docs/m/m0594e053/index.html`
- `docs/m/m09091404/index.html`
- `docs/m/m0effd17d/index.html`
- `docs/m/m586876fa/index.html`
- `docs/m/m660dc5c7/index.html`
- `docs/m/m6e7e8ab7/index.html`
- `docs/m/m7d28b3cd/index.html`
- `docs/m/m971790c1/index.html`
- `docs/m/ma0b91971/index.html`
- `docs/m/mb6ceb13c/index.html`
- `docs/m/mc16cd596/index.html`
- `docs/m/md7fd1d6e/index.html`
- `docs/m/mdd4bf0ae/index.html`

Pre-existing untracked lane-control files not edited as deliverables: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
