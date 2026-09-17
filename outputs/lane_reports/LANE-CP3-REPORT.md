# LANE CP3 Report

## 1. What was wrong

Comparator parity was being treated too much like a k-level label check. The falsifier was arithmetic:

- SGLT2 HFrEF: old page/parity said `IDENTICAL_SET` (MEASURED from `git show ad5e7c66:docs/parity.json`). Held Pandey comparator text reports LVEF <=40 subgroup `n=9199` (MEASURED from cached comparator text). Our two shared rows are DAPA-HF `n=4744` plus EMPEROR-Reduced `n=3730`, total `n=8474` (MEASURED from review rows). Difference: `725` (MEASURED arithmetic). So k=2 overlap cannot be called identical.
- PCSK9 MACE: old comparator scope had `comparator_is_class=false` (MEASURED from `git show ad5e7c66:docs/reviews/pcsk9-mace/review.json`). Held comparator text names both `alirocumab and evolocumab` (MEASURED span), so the comparator is class-level. It also predates named eligible `VESALIUS-CV` in `2025-11` (CLAIMED by lane prompt; record presence checked in committed search-v2 candidates).
- Spironolactone/MRA HFrEF: comparator text searches to September 10, 2024 (MEASURED), includes EPHESUS as post-myocardial-infarction LV dysfunction (MEASURED), but omits known eligible `J-EMPHASIS-HF` (MEASURED absent from held comparator text; known eligible from committed `docs/search_test_set.json`).
- Finerenone: comparator text says only two conforming renal-composite citations and names FIDELIO/FIGARO (MEASURED), matching our 2-trial pool. This one is a true `IDENTICAL_SET`, now source-backed rather than inferred from an unexposed table.

Changed mechanism/files:

- Added comparator-truth engine in `harness/comparator_truth.py`.
- Hooked the four lane pages in `harness/pipeline.py`; deliberately scoped by `PAGE_ANNOTATION_SLUGS` so unrelated pages still replay byte-for-byte.
- Rendered comparator-truth rows in `harness/page.py`.
- Added `PARITY_REFUTED_BY_N` to `harness/parity_relation.py`.
- Updated `docs/parity.json` for SGLT2.
- Added sweep script `scripts/comparator_truth_sweep.py` and output `docs/comparator_truth_sweep.json`.

## 2. Plant tests

Added `tests/test_comparator_truth.py`.

Test names and exact assertions:

- `test_PLANT_sglt2_hfref_parity_refuted_by_participant_n`
  - PRE-FIX assertion: `ad5e7c66` parity status was `IDENTICAL_SET` (MEASURED).
  - POST-FIX assertions: `PARITY_REFUTED_BY_N`; `theirs_n=9199`; `ours_n=8474`; `excess=725`; comparator n span is `FOUND`; current rebuilt review overlap carries the same reconciliation.
- `test_pcsk9_agent_scope_class_level_and_recency_from_local_evidence`
  - PRE-FIX assertion: `ad5e7c66` had `scope.comparator_is_class is False` (MEASURED).
  - POST-FIX assertions: `agent_scope_from_text` returns `class-level`; sentence contains `alirocumab` and `evolocumab`; recency returns `COMPARATOR_PREDATES_KNOWN_TRIAL(VESALIUS-CV)`; rebuilt page has `comparator_agent_scope=class-level`.
- `test_spironolactone_incomplete_and_ephesus_contradiction`
  - POST-FIX assertions: comparator completeness is `COMPARATOR_INCOMPLETE`; missing list contains `J-EMPHASIS-HF`; contradictions contain `EPHESUS`; rebuilt review matches.
- `test_finerenone_identical_set_from_only_two_conforming_text`
  - PRE-FIX assertion: `ad5e7c66` overlap had `shared_k="not exactly verifiable..."` (MEASURED).
  - POST-FIX assertions: completeness relation is `IDENTICAL_SET`; expected-count span is `FOUND`; rebuilt overlap has `shared_k=2`.
- `test_synthetic_equal_n_and_equal_named_set_allows_parity`
  - POST-FIX assertions: equal n gives `N_RECONCILIATION_MATCH`; exact named set gives `IDENTICAL_SET`; absent numeric span returns `NOT_IN_HELD_TEXT`.

Pre-fix failing run was not executed; the tests read `ad5e7c66` directly for the pre-fix plant state. Post-fix output:

```text
.....                                                                    [100%]
5 passed in 6.53s
```

## 3. Rebuilt pages and changed blocks

Build commands run with `--now 2026-09-11` (MEASURED):

- `sglt2-hfref-hosp-cvdeath`: before `IDENTICAL_SET`; after `PARITY_REFUTED_BY_N(theirs=9199, ours=8474, excess=725)`. `docs/parity.json` also changed from `IDENTICAL_SET` to `PARITY_REFUTED_BY_N`.
- `pcsk9-mace`: before `comparator_is_class=false`; after `comparator_is_class=true`, `comparator_agent_scope=class-level`, and recency truth includes `COMPARATOR_PREDATES_KNOWN_TRIAL(VESALIUS-CV)`.
- `spironolactone-hfref-mortality`: after comparator truth block says `COMPARATOR_INCOMPLETE(missing: J-EMPHASIS-HF)` and records EPHESUS scope contradiction.
- `finerenone-ckd-t2d-renal`: before shared set was not exactly verifiable; after `theirs_k=2`, `shared_k=2`, method `comparator-truth: named conforming renal-composite trials located in cached comparator text`.

Replay outputs:

```text
OK  sglt2-hfref-hosp-cvdeath
1/1 reproduce (all reproducible)

OK  pcsk9-mace
1/1 reproduce (all reproducible)

OK  spironolactone-hfref-mortality
1/1 reproduce (all reproducible)

OK  finerenone-ckd-t2d-renal
1/1 reproduce (all reproducible)
```

Sweep output:

```text
comparator truth sweep: n-refuted 1/1; rendered values without span 12/136; predating known eligible 1/32
```

All sweep counts are MEASURED from `docs/reviews/*/review.json` plus held comparator text.

## 4. Tests

Passing commands:

```text
python -m py_compile harness\comparator_truth.py harness\pipeline.py harness\page.py harness\parity_relation.py scripts\comparator_truth_sweep.py tests\test_comparator_truth.py
```

No output, exit code 0 (MEASURED).

```text
python -m pytest tests/test_comparator_truth.py -q
.....                                                                    [100%]
5 passed in 6.53s
```

```text
python -m pytest tests/test_comparator_truth.py tests/test_gate.py -q
........                                                 [100%]
24 passed in 56.20s
```

```text
python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q
.                                                                        [100%]
1 passed in 37.77s
```

```text
python -m pytest tests/test_funding.py tests/test_gate.py -x -vv
============================= 34 passed in 49.27s =============================
```

```text
python -m pytest tests/test_gate.py tests/test_gate_controls.py tests/test_gate_scorecard.py tests/test_grade_global_fixes.py tests/test_grade_integration_floor.py tests/test_grade_unassessed.py tests/test_hazard_consumers.py tests/test_heldout.py tests/test_heterogeneity_derived.py tests/test_honest_ratchet.py tests/test_honest_states_renderable.py -x -q
92 passed in 142.82s (0:02:22)
```

Broad-suite note: `python -m pytest tests -x -q` was attempted more than once. After reaching the low 30% range it became silent inside the existing repo-wide `tests/test_fixstate.py::test_real_store_validates` path; the verbose run confirmed the exact test, and a direct `fixstate.check(ROOT)` timing call also exceeded 90 seconds with no output before I interrupted it. I am not claiming the full suite passed.

## 5. What I did not do

- Did not commit, stage, stash, reset, checkout, or clean.
- Did not run `scripts/verify_all.py`.
- Did not use network.
- Did not change `YOUR REWRITE` workbook sections.
- Did not broaden comparator-truth page annotations beyond the four CP3 lane pages; the corpus-wide work is in the sweep JSON.

## 6. Files changed or added

Core:

- `harness/comparator_truth.py` (added)
- `harness/pipeline.py`
- `harness/page.py`
- `harness/parity_relation.py`
- `scripts/comparator_truth_sweep.py` (added)
- `tests/test_comparator_truth.py` (added)

Data/output:

- `docs/parity.json`
- `docs/comparator_truth_sweep.json` (added)
- `docs/reviews/sglt2-hfref-hosp-cvdeath/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/reviews/pcsk9-mace/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/reviews/spironolactone-hfref-mortality/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/reviews/finerenone-ckd-t2d-renal/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- Blind mirrors: `docs/m/m3c1155fb/index.html`, `docs/m/m5e5590d5/index.html`, `docs/m/m6dd4233b/index.html`, `docs/m/mf6cd36c2/index.html`
- `docs/index.html`
- `registry/blind_map.json`

Existing untracked lane files left untouched:

- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`

## 7. Static-vs-dynamic hardcode disclosure

| Item | Type | Why it exists | Fail-closed behavior |
| --- | --- | --- | --- |
| `PAGE_ANNOTATION_SLUGS` | Static lane scope | Limits rendered page annotation to the four CP3 pages; avoids invalidating unrelated committed page replay. | Other pages are not annotated in builds; sweep still assesses them. |
| `KNOWN_ELIGIBLE_BY_SLUG` | Static named controls | Encodes lane-required known eligible trial names for spironolactone and finerenone. | Missing names produce `COMPARATOR_INCOMPLETE`; no silent parity claim. |
| `NAMED_TRIALS_BY_SLUG["pcsk9-mace"]` | Static named recency sentinel | Encodes `VESALIUS-CV` date `2025-11` from the lane prompt and committed candidate evidence. | Emits `COMPARATOR_PREDATES_KNOWN_TRIAL`; does not alter pooling. |
| SGLT2 comparator `theirs_n` | Dynamic | Parsed from held Pandey comparator text by LVEF <=40 span search. | If span not found, n reconciliation is not asserted. |
| Our participant n | Dynamic | Summed from current pooled trial rows. | If row n is unavailable, participant reconciliation is not asserted. |
| Rendered comparator value spans | Dynamic | Swept from review JSON and matched against cached comparator text. | Values become `NOT_IN_HELD_TEXT` instead of assumed source-backed. |
| Sweep denominators | Dynamic | Derived from current `docs/reviews` corpus. | Summary reports measured denominators, including `32` served review pages. |
