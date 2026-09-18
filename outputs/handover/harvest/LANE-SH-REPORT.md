# LANE SH report

## 1. What was wrong, mechanism, files

MEASURED: the previous build path could reconstruct a crude count effect and pool it before applying a single source-hierarchy selector. That meant a committed source-reported effect plus 95% CI on the same declared estimand class could be present but not selected over the count reconstruction.

MEASURED files changed for the mechanism:

- `harness/design_key.py`: added `select_estimator_by_source_hierarchy()`, the single documented selector. It prefers a committed source-reported effect+CI when the candidate's estimand class matches the declared outcome class. HR, RR, and OR are treated as `FIRST_EVENT_RATIO`; RATE remains a mismatch for a first-event outcome.
- `harness/pipeline.py`: routes existing extracted candidates through the selector after each extraction branch. The selector only considers the selected row's own committed source span plus explicit committed `verified_effects`, so an unrelated abstract endpoint is not promoted.
- `harness/page.py`: renders row-level source-hierarchy disclosure, including not-selected alternatives and typed source-hierarchy limitations.
- `cache/spironolactone-hfref-mortality/verified_arms.json`: adds the typed limitation for J-EMPHASIS-HF because the claimed published HR is not in committed source bytes.
- `scripts/source_hierarchy_sweep.py`: adds the corpus-wide offline sweep.

CLAIMED by `AUDIT_QUEUE.md` item 7: J-EMPHASIS-HF has an all-cause mortality HR 1.77 [0.81, 3.87]. MEASURED in this clone: the committed `cache/spironolactone-hfref-mortality/` source bytes do not contain `1.77` or `1.77` with a middle-dot decimal variant. Therefore the J-EMPHASIS-HF row is not switched. MEASURED outcome: row remains reconstructed from 17/111 vs 10/110 and now carries `PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE` with `AUDIT_QUEUE.md item 7`.

Static-vs-dynamic disclosure:

| Item | Type | Basis |
| --- | --- | --- |
| Selector decision | Dynamic | Computed from committed row/candidate fields and `harness/estmeasure.py` classes. |
| Sweep counts | Dynamic | MEASURED by `python scripts\source_hierarchy_sweep.py` over the 32 served topics. |
| J-EMPHASIS-HF limitation | Static metadata, source-backed | CLAIMED HR from `AUDIT_QUEUE.md item 7`; MEASURED absence from committed cache; does not invent an effect. |
| Generated pages | Dynamic | Rebuilt from committed cache with `python scripts/build_topic.py <slug> --now 2026-09-11`. |

## 2. Plant

MEASURED plant tests added in `tests/test_source_hierarchy.py`:

- `test_published_target_effect_beats_reconstructed_counts`
  - Exact pre-fix-path assertion: `assert pre_fix.get("ai") == 20 and pre_fix.get("effect") is None`.
  - Exact post-fix assertions: `assert trial["effect"] == 0.80`; `assert trial["scale"] == "HR"`; `assert trial["selection_rule"] == "PUBLISHED_EFFECT_TARGET_CLASS"`; `assert trial["alternatives"][0]["ai"] == 20`.
  - MEASURED behavior: the unchanged pre-fix extractor path returns the count row (`ai=20`, no `effect`), while the pipeline selector returns the source HR 0.80 [0.70, 0.90] and discloses the count alternative.
- `test_counts_remain_when_no_published_effect_exists`
  - Exact assertions: `assert trial["ai"] == 20 and trial.get("effect") is None`; `assert trial["selection_rule"] == "KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT"`.
- `test_different_estimand_class_does_not_override_counts`
  - Exact assertions: `assert trial["ai"] == 20 and trial.get("effect") is None`; `assert trial["selection_rule"] == "KEEP_RECONSTRUCTION_EFFECT_CLASS_MISMATCH"`; `assert "estimand_class_mismatch:RATE!=FIRST_EVENT_RATIO" in trial["alternatives"][0]["not_selected_reason"]`.
- `test_prefix_j_emphasis_limitation_check_fires`
  - Exact assertion: `_j_emphasis_limitation_violations(_load_prefix_spironolactone_review()) == ["J-EMPHASIS-HF reconstructed row lacks PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE"]`.
- `test_rebuilt_j_emphasis_limitation_check_passes`
  - Exact assertion: `_j_emphasis_limitation_violations(_load_current_spironolactone_review()) == []`.

MEASURED pre-fix firing output, before the J-EMPHASIS limitation was added and the page rebuilt:

```text
....F
FAILED tests/test_source_hierarchy.py::test_rebuilt_j_emphasis_limitation_check_passes
assert ['J-EMPHASIS-HF reconstructed row lacks PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE'] == []
1 failed, 4 passed in 5.09s
```

MEASURED post-fix targeted output:

```text
........ 8 passed in 4.46s
```

## 3. Pages whose rebuilt bytes changed

MEASURED sweep summary:

```text
5 rows changed of 115 pooled rows over 32 topics
```

All 32 served review pages and their `docs/m/<token>/index.html` mirrors were rebuilt because trial rows now carry `selection_rule`, and the rendered source column now can disclose source-hierarchy alternatives or limitations. MEASURED common sentence/field change on rebuilt pages: before, row-level source-hierarchy selector output and not-selected alternatives were absent; after, rows include `selection_rule`, and pages render the selector code plus `source-hierarchy alternatives not selected` or `source-hierarchy limitation` when present.

MEASURED numeric switches:

| Slug | Outcome / trial | Before selected row | After selected row | Before pool | After pool | Source span |
| --- | --- | --- | --- | --- | --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | Mortality / PMID 34375394 | MEASURED reconstructed 1381/5230 vs 1439/5290, implied RR 0.9707041085733799 | MEASURED published HR 0.97 [0.90, 1.05] | MEASURED RR 0.9762 [0.6864, 1.3882] | MEASURED RR 0.9774 [0.6521, 1.465] | MEASURED: `abstract effect+CI (HR): abstract arm-level counts (percentage-corroborated): By day 90, 1381 of 5230 patients (26.4%) assigned to a balanced solution died vs 1439 of 5290 patients (27.2%) assigned...` |
| `colchicine-postop-af` | Postoperative atrial fibrillation / PMID 32720823 | MEASURED reconstructed 13/81 vs 13/71, implied RR 0.8765432098765431 | MEASURED published OR 0.85 [0.37, 1.99] | MEASURED RR 0.6735 [0.376, 1.2067] | MEASURED RR 0.6655 [0.3736, 1.1854] | MEASURED: `abstract effect+CI (OR): abstract arm-level counts (percentage-corroborated): POAF occurred in 13 patients (16.1%) in the colchicine group and 13 patients (18.3%) in the placebo group (odds ratio 0...` |
| `colchicine-recurrent-pericarditis` | Recurrent pericarditis / PMID 24694983 | MEASURED reconstructed 26/120 vs 51/120, implied RR 0.5098039215686275 | MEASURED published RR 0.49 [0.24, 0.65] | MEASURED RR 0.4813 [0.064, 3.6169] | MEASURED RR 0.4643 [0.0474, 4.5468] | MEASURED: `abstract effect+CI (RR): abstract arm-level counts (percentage-corroborated): The proportion of patients who had recurrent pericarditis was 26 (21.6%) of 120 in the colchicine group and 51 (42.5%) ...` |
| `omega3-cardiovascular-events` | Major vascular events / MACE / PMID 33190147 | MEASURED reconstructed 785/6539 vs 795/6539, implied RR 0.9874213836477986 | MEASURED published HR 0.99 [0.90, 1.09] | MEASURED RR 0.943 [0.846, 1.051] | MEASURED RR 0.9433 [0.8461, 1.0517] | MEASURED: `abstract effect+CI (HR): abstract arm-level counts (percentage-corroborated): The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (ha...` |
| `tocilizumab-covid19-mortality` | 28-day all-cause mortality / PMID 33933206 | MEASURED reconstructed 621/2022 vs 729/2094, implied RR 0.8821848554786239 | MEASURED published RR 0.85 [0.76, 0.94] | MEASURED OR 0.83 [0.7285, 0.9456] | MEASURED RR 0.85 [0.76, 0.94] | MEASURED: `abstract effect+CI (RR): abstract arm-level counts (percentage-corroborated): Overall, 621 (31%) of the 2022 patients allocated tocilizumab and 729 (35%) of the 2094 patients allocated to usual car...` |

MEASURED J-EMPHASIS-HF page change:

| Slug | Before | After |
| --- | --- | --- |
| `spironolactone-hfref-mortality` | MEASURED pre-fix object had a reconstructed J-EMPHASIS-HF row without `PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE`. | MEASURED row remains reconstructed because the claimed HR is not committed; row now discloses `PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE` citing `AUDIT_QUEUE.md item 7`. MEASURED pool remains k=3, RR/HR 0.8685 [0.3062, 2.4635]. |

MEASURED rebuilt pages with no numeric pool switch, only the row-level selection-rule disclosure/regenerated deterministic bytes:

`colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `dapagliflozin-hfpef-hosp`, `denosumab-vertebral-fracture`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `esketamine-trd-madrs`, `finerenone-ckd-t2d-renal`, `glp1-ra-mace-t2d`, `iv-iron-hfref-hosp`, `melatonin-primary-insomnia-sol`, `metformin-pcos-ovulation`, `noac-vs-warfarin-af-stroke`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-ckd-progression`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `statins-primary-prevention-elderly`, `ticagrelor-vs-clopidogrel-acs`, `tranexamic-acid-pph`.

## 4. Tests

MEASURED:

```text
python scripts\source_hierarchy_sweep.py
5 rows changed of 115 pooled rows over 32 topics
```

MEASURED:

```text
python scripts\reproduce_review.py
32/32 reproduce (all reproducible)
```

MEASURED:

```text
python scripts\render_fix_ledger.py
rendered docs/fix_ledger.json
```

MEASURED:

```text
python -m pytest tests\test_source_hierarchy.py -q
........ 8 passed in 4.46s
```

MEASURED required gate:

```text
python -m pytest tests -x -q
644 passed in 428.36s (0:07:08)
```

## 5. What I did not do and why

- MEASURED: did not fetch or search for the J-EMPHASIS-HF HR source. The lane says fetching is out of scope; the row is limited instead of invented.
- MEASURED: did not edit `harness/extract.py`; the extractor path is read-only for this lane.
- MEASURED: did not add or remove any pooled trial. Only the selected estimator for already-pooled trial rows changed.
- MEASURED: did not weaken the estimand gate. RATE effects remain disclosed alternatives for `FIRST_EVENT_RATIO` outcomes, not selected effects.
- MEASURED: did not touch `harness/synth.py`, `harness/rob_sensitivity.py`, `harness/grade.py`, `docs/refusals.json`, or search code.
- MEASURED: did not run network search scripts.
- MEASURED: did not run `git add`, `git commit`, `git stash`, `git checkout`, `git reset`, or `git clean`.

## 6. Files changed or added

MEASURED code/cache/test/report/sweep files changed or added:

- `LANE-SH-REPORT.md`
- `cache/spironolactone-hfref-mortality/verified_arms.json`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `docs/fix_ledger.json`
- `docs/source_hierarchy_sweep.json`
- `harness/design_key.py`
- `harness/page.py`
- `harness/pipeline.py`
- `scripts/source_hierarchy_sweep.py`
- `tests/test_source_hierarchy.py`

MEASURED review outputs changed for each slug below as `docs/reviews/<slug>/{REPRODUCTION.json,index.html,manifest.json,review.json}`:

- `balanced-crystalloids-vs-saline-mortality`
- `colchicine-postop-af`
- `colchicine-recurrent-pericarditis`
- `colchicine-secondary-cv-prevention`
- `corticosteroids-cap-mortality`
- `corticosteroids-covid19-mortality`
- `dapagliflozin-hfpef-hosp`
- `denosumab-vertebral-fracture`
- `doac-vte-recurrence`
- `dpp4-mace-t2d`
- `empagliflozin-hfpef-hosp`
- `esketamine-trd-madrs`
- `finerenone-ckd-t2d-renal`
- `glp1-ra-mace-t2d`
- `iv-iron-hfref-hosp`
- `melatonin-primary-insomnia-sol`
- `metformin-pcos-ovulation`
- `noac-vs-warfarin-af-stroke`
- `omega3-cardiovascular-events`
- `pcsk9-mace`
- `probiotics-aad-prevention`
- `sacubitril-valsartan-hfref`
- `semaglutide-obesity-mace`
- `semaglutide-obesity-weight`
- `sglt2-ckd-progression`
- `sglt2-hfref-hosp-cvdeath`
- `sglt2-primary-prevention-hf`
- `spironolactone-hfref-mortality`
- `statins-primary-prevention-elderly`
- `ticagrelor-vs-clopidogrel-acs`
- `tocilizumab-covid19-mortality`
- `tranexamic-acid-pph`

MEASURED mirror pages changed:

- `docs/m/m0594e053/index.html`
- `docs/m/m078be06c/index.html`
- `docs/m/m0c0e2bf1/index.html`
- `docs/m/m175bd0c3/index.html`
- `docs/m/m22bf81d5/index.html`
- `docs/m/m24cd09bc/index.html`
- `docs/m/m250220c2/index.html`
- `docs/m/m2da64325/index.html`
- `docs/m/m3c1155fb/index.html`
- `docs/m/m5384fd3c/index.html`
- `docs/m/m586876fa/index.html`
- `docs/m/m5b3fd56c/index.html`
- `docs/m/m5e5590d5/index.html`
- `docs/m/m612a48aa/index.html`
- `docs/m/m6dd4233b/index.html`
- `docs/m/m6e7e8ab7/index.html`
- `docs/m/m87167438/index.html`
- `docs/m/m89f8021b/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/m979b0810/index.html`
- `docs/m/ma0b91971/index.html`
- `docs/m/maf69923c/index.html`
- `docs/m/mb53e1ed5/index.html`
- `docs/m/mb6ceb13c/index.html`
- `docs/m/mc16cd596/index.html`
- `docs/m/md68c6ad6/index.html`
- `docs/m/mdd4bf0ae/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/me5d639f4/index.html`
- `docs/m/me79cb3b0/index.html`
- `docs/m/mf6cd36c2/index.html`

MEASURED untracked files present but not changed by me: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
