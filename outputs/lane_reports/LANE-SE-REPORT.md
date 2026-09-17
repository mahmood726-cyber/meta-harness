# LANE SE Report

## 1. What was wrong

[MEASURED] The corpus has 32 served review pages. `docs/scope_identity_sweep.json` reports `28 pages SCOPE_MISMATCH of 32`; the remaining 4 pages are `HAND_WRITTEN_KEYWORD_SCOPE` (`colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `corticosteroids-cap-mortality`, `probiotics-aad-prevention`).

[MEASURED] The defect was scope identity, not pooling math: open P/I/C/design eligibility was rendered as though it had been tested over an open search universe, while many pages were retrieved from a pre-identified PMID/title set. `harness/scope_identity.py` now derives `eligibility_scope`, `search_scope`, and a typed verdict. `harness/pipeline.py` stamps the object, `harness/page.py` renders the pre-identified-set qualification, and `harness/gate.py::check_scope_identity` refuses an unsafe rendered page.

[MEASURED] `docs/posthoc_amendment_sweep.json` reports 2 `POST_HOC_AMENDMENT` rows: `noac-vs-warfarin-af-stroke` (2026-09-12 after cache date 2026-09-11) and `spironolactone-hfref-mortality` (2026-09-16 after cache date 2026-09-11).

Static-vs-dynamic disclosure:

| Item | Static | Dynamic |
|---|---|---|
| Reach-miss names | Audit-supplied rows only; fetched=false, pooled=false | Attached only to the named slugs in the sweep |
| Scope verdicts | Verdict labels/constants | Derived from topic config, protocol text, review retrieval class, and retrieval ledger |
| Page qualification text | Fixed safety sentence | Search class and count come from the rebuilt review object |
| Post-hoc amendments | Noac required-render phrase is fixed by brief | Amendment dates, cache dates, git log, and standard-dose result read from committed files |

## 2. Plants

[MEASURED] `tests/test_scope_identity.py::test_doac_prefixed_known_item_scope_mismatch_fires_on_unsafe_text` loads `git show ad5e7c66:docs/reviews/doac-vte-recurrence/*`, asserts `KNOWN_ITEM_RETRIEVAL`, asserts the unsafe text `6 reported this outcome with an extractable number and were pooled`, asserts the new qualification is absent, and gets `['SCOPE_MISMATCH']`.

[MEASURED] `tests/test_scope_identity.py::test_noac_prefixed_scope_mismatch_and_posthoc_amendment_fire` loads `git show ad5e7c66:docs/reviews/noac-vs-warfarin-af-stroke/*`, gets `['SCOPE_MISMATCH']`, and asserts the noac amendment row is `POST_HOC_AMENDMENT` with required render `rule stated; both answers were known; standard-dose result AND all-dose result reported`.

[MEASURED] Post-fix tests `test_doac_rebuilt_scope_mismatch_is_qualified_and_passes_check` and `test_noac_rebuilt_scope_mismatch_is_qualified_and_passes_check` assert the rebuilt HTML contains `eligibility over the open scope was NOT tested` and `check_scope_identity(...) == []`.

[MEASURED] Synthetic concept-search test returns `OK` and no violation. The hand-written keyword test asserts 4 of 32 pages return `HAND_WRITTEN_KEYWORD_SCOPE`, not `SCOPE_MISMATCH`.

[MEASURED] `python -m pytest tests/test_scope_identity.py -q` -> `6 passed in 7.10s`.

## 3. Rebuilt bytes

[MEASURED] Rebuilt pages and replay checks:

- `doac-vte-recurrence`: `python scripts/reproduce_review.py doac-vte-recurrence` -> `1/1 reproduce (all reproducible)`. Primary unchanged: k=6, HR 0.9092 [0.7478, 1.1054]. Screened-in row changed from `5 trial families (6 publications) met P/I/C/design (screening); 6 reported...` to `5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 6 reported...`.
- `noac-vs-warfarin-af-stroke`: `python scripts/reproduce_review.py noac-vs-warfarin-af-stroke` -> `1/1 reproduce (all reproducible)`. Primary unchanged: k=4, HR 0.8069 [0.6611, 0.985]. Screened-in row changed from `9 trial families met P/I/C/design (screening); 4 reported...` to `9 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 4 reported...`.
- `probiotics-aad-prevention`: rebuilt to keep the real full-gate smoke page current after the canonical field was added. `python scripts/reproduce_review.py probiotics-aad-prevention` -> `1/1 reproduce (all reproducible)`. Primary unchanged: k=16, RR 0.702 [0.5352, 0.921]. Its sweep verdict is `HAND_WRITTEN_KEYWORD_SCOPE`; the screened-in row is unchanged.

[MEASURED] Generated metadata refreshed: `docs/fix_ledger.json`, `registry/gate_scorecard.json`, `docs/gate_scorecard.json`, `docs/index.html`, `registry/blind_map.json`, and the three harness blind pages.

## 4. Tests

[MEASURED] Targeted summaries:

- `python -m pytest tests/test_page.py::test_all_pooled_equals_screened_states_so -q` -> `1 passed in 12.76s`
- `python -m pytest tests/test_retrieval_join.py::test_build_review_core_joins_retrieval_ledger -q` -> `1 passed in 13.69s`
- `python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q` -> `1 passed in 27.87s`
- `python -m pytest tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews -q` -> `1 passed in 12.73s`
- `python -m pytest tests/test_fixstate.py::test_real_store_validates -q` -> `1 passed in 245.85s (0:04:05)`
- `python -m pytest tests/test_gate_scorecard.py::test_real_registry_passes -q` -> `1 passed in 5.26s`

[MEASURED] Full suite summary: `python -m pytest tests -x -q` -> `722 passed in 739.84s (0:12:19)`.

## 5. Not done

[MEASURED] No commit, stage, stash, checkout, reset, or clean was run.

[MEASURED] No network search was run. I did not fetch, screen in, extract, or pool any `REACH_MISS` row.

[MEASURED] I did not touch pooling math, search execution, screening decisions, or `harness/synth.py`.

[MEASURED] I did not compute a noac all-dose alternative: the committed cache contains RE-LY 110 mg and an ENGAGE low-dose edoxaban effect, but does not explicitly identify the lower-dose edoxaban arm as 30 mg in the committed source. The sweep records `NOT_COMPUTED_SOURCE_INCOMPLETE`.

[MEASURED] I did not rebuild all 28 `SCOPE_MISMATCH` pages; only the two named unsafe scope pages plus the real gate smoke page were rebuilt.

## 6. Files changed or added

Source/tests/report:

- `harness/scope_identity.py`
- `harness/pipeline.py`
- `harness/page.py`
- `harness/gate.py`
- `tests/test_scope_identity.py`
- `LANE-SE-REPORT.md`

Sweeps/registries/generated views:

- `docs/scope_identity_sweep.json`
- `docs/posthoc_amendment_sweep.json`
- `registry/gate_scorecard.json`
- `docs/gate_scorecard.json`
- `docs/fix_ledger.json`
- `registry/blind_map.json`
- `docs/index.html`

Rebuilt review artifacts:

- `docs/reviews/doac-vte-recurrence/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/reviews/noac-vs-warfarin-af-stroke/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/reviews/probiotics-aad-prevention/{review.json,index.html,manifest.json,REPRODUCTION.json}`
- `docs/m/m87167438/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/m586876fa/index.html`
