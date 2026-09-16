# LANE CG Report

## 1. What Was Wrong

[MEASURED] The pre-fix graph failures at `aa8ed28a` were not pooling math failures. They were stale or unwired consumers of the current trial set:

- `harness/rob_sensitivity.py` joined RoB2 ratings on `trial["label"]`; recovered trials with acronym labels (`CLEAR SYNERGY`, `PHILO`, `J-EMPHASIS-HF`, `SOUL`) were rated in `rob2` by PMID/NCT but absent from RoB sensitivity levels.
- `iv-iron-hfref-hosp` attached strand pools late, outside claim counting and membership checks.
- `docs/refusals.json` still refused Torres 2015 while the primary CAP outcome pooled it.
- `page.py` and `limitations.py` rendered the "fewer trials than the full pool" predicate when low-only and full RoB pools were identical.
- Parity rows from `docs/parity.json` were treated as inert prose, so stale `= ours` / `= our pool` text survived pool changes.

[MEASURED] Implemented `harness/claimgraph.py` and wired it through `pipeline`, `census`, `reproduce_review`, and `gate`. Result-bearing objects now carry `input_set_version`, `claim_id`, and `depends_on`, and `claimgraph.check(review)` returns typed violations: `ROB_JOIN_MISS`, `STALE_DEPENDENT`, `REFUSED_AND_POOLED`, `STRAND_OUTSIDE_CLAIMS`, `PROSE_PREDICATE_FALSE`, `MEMBERSHIP_CONFLICT`.

[MEASURED] On active violations, stale registry/prose objects are rendered as `UNRENDERABLE claimgraph object` blocks with code and `claim_id`, with stale numbers/prose suppressed.

[INFERRED from targeted grep/read] Label-join audit:

- Fixed: `harness/rob_sensitivity.py` now uses `trial_key(t)` for RoB2 joins and sensitivity `levels`.
- `harness/funding.py` uses `trial["id"]` -> PMID for `rec_by_id`; no label side-table join found.
- `harness/armcontrast.py` uses NCT/AACT arm structure; no pooled-label side-table join found.
- `harness/spec_curve.py` and `harness/manuscript.py` use labels only as display/study labels.
- `harness/pipeline.py` has label fallbacks for display/abstract fallback paths, but the RoB side-table join candidate was fixed.

Static-vs-dynamic disclosure:

| Item | Static | Dynamic |
|---|---|---|
| Trial identity rule | `trial_key()` strips PMID prefixes and preserves NCT IDs | Derived from `trial["id"]`, never `label` |
| Claim IDs | hash kind/outcome/version | Recomputed during build/replay |
| Input versions | none hardcoded | sha256 of sorted consumed trial inputs |
| Refusals/parity | hand registries remain source files | Stamped and checked against current trial set |
| Numbers in report | none invented | All before/after values below measured from `git show aa8ed28a:...` and rebuilt files |

## 2. Plants

[MEASURED] `tests/test_claimgraph.py` uses `git show aa8ed28a:...` for the pre-fix objects. Exact assertions include `assert code in _codes(review)`, set inclusion for IV iron, and `assert claimgraph.check(review) == []` for the clean synthetic object.

Pre-fix fixture outputs:

| Test/fixture | Assertion target | Output |
|---|---:|---|
| `test_prefixed_named_pages_fire[colchicine-secondary-cv-prevention]` | `ROB_JOIN_MISS` | `['ROB_JOIN_MISS']` |
| `test_prefixed_named_pages_fire[ticagrelor-vs-clopidogrel-acs]` | `ROB_JOIN_MISS` | `['ROB_JOIN_MISS', 'PROSE_PREDICATE_FALSE']` |
| `test_prefixed_named_pages_fire[spironolactone-hfref-mortality]` | `ROB_JOIN_MISS` | `['ROB_JOIN_MISS', 'PROSE_PREDICATE_FALSE']` |
| `test_prefixed_named_pages_fire[glp1-ra-mace-t2d]` | `ROB_JOIN_MISS` | `['ROB_JOIN_MISS']` |
| `test_prefixed_named_pages_fire[dpp4-mace-t2d]` | `PROSE_PREDICATE_FALSE` | `['PROSE_PREDICATE_FALSE']` |
| `test_prefixed_iv_iron_strands_fire` | `STRAND_OUTSIDE_CLAIMS`, `MEMBERSHIP_CONFLICT` | `['STRAND_OUTSIDE_CLAIMS', 'STRAND_OUTSIDE_CLAIMS', 'MEMBERSHIP_CONFLICT', 'MEMBERSHIP_CONFLICT', 'MEMBERSHIP_CONFLICT']` |
| `test_prefixed_corticosteroids_refusal_fire` | `REFUSED_AND_POOLED` | `['REFUSED_AND_POOLED']` |

Synthetic outputs:

| Synthetic case | Output |
|---|---|
| clean negative | `[]` |
| RoB join miss | `['ROB_JOIN_MISS']` |
| stale dependent | `['STALE_DEPENDENT']` |
| refused and pooled | `['REFUSED_AND_POOLED']` |
| strand outside claims | `['STRAND_OUTSIDE_CLAIMS']` |
| prose predicate false | `['PROSE_PREDICATE_FALSE']` |
| membership conflict | `['MEMBERSHIP_CONFLICT']` |

[MEASURED] Post-fix `claimgraph.check()` output for all seven named pages, plus the refreshed gate fixture page, is `[]`.

## 3. Rebuilt Byte Changes

[MEASURED] Seven requested pages were rebuilt and replayed. Each `python scripts/reproduce_review.py <slug>` returned `1/1 reproduce (all reproducible)`.

| Page | Before | After |
|---|---|---|
| `colchicine-secondary-cv-prevention` | low-only `k=2`, HR `0.7215 [0.2824, 1.8432]`, `tau2=0.0` | low-only `k=3`, HR `0.8134 [0.5074, 1.3039]`, `tau2=0.02669` |
| `ticagrelor-vs-clopidogrel-acs` | low-only `k=1`, HR `0.84 [0.7685, 0.9182]`; parity prose said `1 valid RCT (PLATO) = ours` | low-only `k=2`, HR `1.0479 [0.0324, 33.8921]`; parity row is `UNRENDERABLE`, code `PROSE_PREDICATE_FALSE`, `claim_id 8957e0adaf0704f6` |
| `spironolactone-hfref-mortality` | low-only `k=2`, RR/HR `0.7218 [0.3236, 1.6097]`; parity prose said `RALES + EMPHASIS = our pool` | low-only `k=3`, RR/HR `0.8685 [0.3062, 2.4635]`; parity row is `UNRENDERABLE`, code `PROSE_PREDICATE_FALSE`, `claim_id 15d7881e578cd98d` |
| `glp1-ra-mace-t2d` | low-only `k=6`, HR `0.8321 [0.7668, 0.9029]`, `tau2=0.0` | low-only `k=7`, HR `0.8388 [0.7839, 0.8975]`, `tau2=0.0` |
| `iv-iron-hfref-hosp` | `Claims checked: 0`; strands not counted; strand members still reported not pooled | `claims_checked=4`, `scope_counts={'outcome_result': 0, 'strand_pool': 4, 'rob_sensitivity': 0, 'grade': 1}`; strand membership conflicts removed |
| `corticosteroids-cap-mortality` | refusals table contained Torres 2015 and Meduri/ESCAPe | Torres row removed; Meduri/ESCAPe remains and is stamped with `claim_id 0b1a708d24d8fbb7` |
| `dpp4-mace-t2d` | low-only cell: `k=3, HR 1.0074 [0.8391, 1.2094] (fewer trials than the full pool - see coverage)` | low-only cell: `k=3, HR 1.0074 [0.8391, 1.2094]` |

[MEASURED] Additional page refresh required by the full gate fixture:

- `probiotics-aad-prevention` was rebuilt and replayed after the new gate made its old RoB prose stale. Primary result stayed `k=16`, RR `0.702 [0.5352, 0.921]`; low-only stayed `k=16`, RR `0.702 [0.5352, 0.921]`. The stale `see coverage` suffix is gone and the page now carries claimgraph metadata.

[MEASURED] Canonical pages whose rebuilt bytes changed:

- `docs/reviews/colchicine-secondary-cv-prevention/index.html`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html`
- `docs/reviews/spironolactone-hfref-mortality/index.html`
- `docs/reviews/glp1-ra-mace-t2d/index.html`
- `docs/reviews/iv-iron-hfref-hosp/index.html`
- `docs/reviews/corticosteroids-cap-mortality/index.html`
- `docs/reviews/dpp4-mace-t2d/index.html`
- `docs/reviews/probiotics-aad-prevention/index.html`

[MEASURED] Tracked blind/index pages whose bytes changed:

- `docs/m/maf69923c/index.html`
- `docs/m/m2da64325/index.html`
- `docs/m/m3c1155fb/index.html`
- `docs/m/mc16cd596/index.html`
- `docs/m/mdd4bf0ae/index.html`
- `docs/m/m0594e053/index.html`
- `docs/m/m6e7e8ab7/index.html`
- `docs/m/m586876fa/index.html`
- `docs/index.html`

## 4. Tests

[MEASURED] Rebuild/replay:

- Requested seven `build_topic.py <slug> --now 2026-09-11` commands completed.
- Requested seven `reproduce_review.py <slug>` commands returned `1/1 reproduce (all reproducible)`.
- `probiotics-aad-prevention` extra fixture replay also returned `1/1 reproduce (all reproducible)`.

[MEASURED] Pytest summaries:

- `python -m pytest tests/test_claimgraph.py -q` -> `14 passed in 2.14s`
- `python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q` -> `1 passed in 24.84s`
- `python -m pytest tests/test_gate_scorecard.py::test_real_registry_passes -q` -> `1 passed in 2.79s`
- `python -m pytest tests/test_limitations_legacy_compare.py -q` -> `1 passed in 2.63s`
- `python -m pytest tests -x -q` -> `653 passed in 364.64s (0:06:04)`

Existing tests changed because they defended legacy artifacts rather than the new requirement:

- `tests/test_stage_additions.py::test_rob_sensitivity_recomputes` now requires exact recomputation for claimgraph-aware reviews, while legacy stale RoB objects must be detected as `ROB_JOIN_MISS`.
- `tests/test_limitations_legacy_compare.py` now excludes claimgraph `UNRENDERABLE` replacement blocks from the legacy limitation mirror and treats legacy-only RoB sensitivity text drift as stale only when confined to that block.

## 5. Not Done

[MEASURED] No commit was made.

[MEASURED] No network search was run and `scripts/verify_all.py` was not run.

[MEASURED] I did not edit `harness/synth.py`, `harness/extract.py`, `harness/estmeasure.py`, `harness/grade.py`, pooling math, or search code.

[MEASURED] I did not rewrite stale parity prose to be true. Ticagrelor and spironolactone parity rows are intentionally unrenderable for the integrator to rewrite.

[INFERRED] I did not rebuild every legacy page that `claimgraph.check()` can now diagnose, because the lane named seven pages. The only extra rebuild was `probiotics-aad-prevention`, required to keep the repository's real gate fixture passing after the new gate was added.

## 6. Files Changed Or Added

Source and tests:

- `harness/claimgraph.py` (new)
- `harness/rob_sensitivity.py`
- `harness/pipeline.py`
- `harness/invalidation.py`
- `harness/census.py`
- `harness/page.py`
- `harness/limitations.py`
- `harness/gate.py`
- `scripts/reproduce_review.py`
- `tests/test_claimgraph.py` (new)
- `tests/test_stage_additions.py`
- `tests/test_limitations_legacy_compare.py`

Registries/generated metadata:

- `docs/refusals.json`
- `registry/gate_scorecard.json`
- `docs/gate_scorecard.json`
- `docs/fix_ledger.json`
- `docs/evidence/design-key-2026-09-14/README.md`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `registry/blind_map.json`

Generated review artifacts:

- `docs/reviews/{colchicine-secondary-cv-prevention,ticagrelor-vs-clopidogrel-acs,spironolactone-hfref-mortality,glp1-ra-mace-t2d,iv-iron-hfref-hosp,corticosteroids-cap-mortality,dpp4-mace-t2d,probiotics-aad-prevention}/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/m/{maf69923c,m2da64325,m3c1155fb,mc16cd596,mdd4bf0ae,m0594e053,m6e7e8ab7,m586876fa}/index.html`
- `docs/index.html`

Report:

- `LANE-CG-REPORT.md`
