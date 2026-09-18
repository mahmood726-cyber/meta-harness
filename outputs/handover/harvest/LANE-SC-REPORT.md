# LANE SC Report

## 1. What was wrong, mechanism, files

MEASURED from `cache/<slug>/records.json`, rebuilt review objects, and `git show aa8ed28a:docs/reviews/<slug>/review.json`.

- Randomised contrast was not consumed by screening. MIRO-CKD (`sglt2-ckd-progression`, `NCT06350123`) was included because the record mentioned CKD/dapagliflozin/placebo, even though every structured CT.gov arm carried dapagliflozin and the randomised contrast was balcinrenone. Fixed in `harness/screen.py` by consuming `harness/armcontrast.py` before I/C eligibility and adding a CT.gov intervention-list fallback for records without AACT arm rows.
- The metformin PCOS "truncated title" symptom was a negation bug, not a loader truncation. PMID `19552097` loaded the full title, but `_NEGATION` treated `non-obese women with polycystic ovary syndrome` as negating PCOS. Fixed by removing bare `non` from the negation pattern.
- Protocol criteria were declared but not executable on named pages. Added dated `PROTOCOL_CONFIG_DIVERGENCE` amendments and corresponding config rules/overrides for CVOT scope, phase 2/II exclusion, ovulation-induction/gonadotrophin context, cardiac-surgery/perioperative exclusions, prevention-vs-treatment probiotic scope, and duplicate/secondary/economic reports.
- Four-state completeness is now attached to included-not-pooled rows: `eligible+completed+results_available`, `eligible+completed+results_unavailable`, `eligible+ongoing`, `eligible+not_yet_recruiting`. `harness/invalidation.py` now excludes `eligible+ongoing` and `eligible+not_yet_recruiting` from `eligible_declared_absent`.
- Adjudicator disagreements are no longer silent. `harness/pipeline.py` consumes `cache/<slug>/screen_adjudication.json` into `ADJUDICATOR_DISAGREES` rows plus `screening.adjudicator_pending`; `harness/page.py` renders the pending state in the screening ledger.
- The search seal was preserved: screening-only population vocabulary was kept in `population_any_extra` rather than `population_any`, so `python scripts/seal_search_vocabulary.py --check` still reports `SEAL OK: 32 of 32`.

Static-vs-dynamic hardcode disclosure:

| Item | Kind | Why acceptable / boundary |
| --- | --- | --- |
| ORGANON `NCT02935855` override | Static, source-backed | Cached registry describes consecutive anticoagulant patients, not randomised DOAC-vs-warfarin allocation. Screening only. |
| DIAMOND `NCT03190694` override | Static, source-backed | Cached registry has CKD/proteinuria and dapagliflozin crossover eligibility but sparse comparator labelling. It is included then declared absent/incompatible, not pooled. |
| Protocol config amendments | Static criteria | Retrospective known-answer amendments are declared in `protocols/*.md` under `PROTOCOL_CONFIG_DIVERGENCE`; they make existing protocol criteria executable. |
| Four-state completeness | Dynamic local data | Derived from local AACT status/results dates and committed cache metadata at build time. |
| Screening delta | Dynamic offline replay | Generated from `git show aa8ed28a` pre-fix review objects plus current cache/config replay; no network. |
| Adjudicator pending state | Dynamic committed cache | Reads existing `screen_adjudication.json`; served decision is not silently changed by the adjudicator. |

## 2. Plant

Plant file: `tests/test_screen_contrast_and_ledger.py`.

Exact assertions covered:

- `sglt2-ckd-progression` `NCT06350123`: pre-fix object has `decision == include`; current replay has `decision == exclude`, `rule_id == X-CONTRAST`, and the reason contains `Balcinrenone` and `Dapagliflozin`.
- `sglt2-ckd-progression` `NCT03190694`: pre-fix `X2`; current replay `INCLUDE`.
- `metformin-pcos-ovulation` `19552097`: pre-fix `X2`; current replay `INCLUDE`; span contains `polycystic ovary syndrome`; direct `_has(...)` no longer treats `non-obese` as negation.
- `noac-vs-warfarin-af-stroke` `NCT02935855`: pre-fix `INCLUDE`; current replay `X1` with `consecutive patients` in the reason.
- `noac-vs-warfarin-af-stroke` `NCT05006287`: pre-fix `INCLUDE`; current replay `X2` with `Cardiac Surgery` in the span.
- Control: `NCT07060417` remains `INCLUDE`, not `X-CONTRAST`.
- Completeness gate: `NCT07060417` is `eligible+not_yet_recruiting` and does not appear in the `eligible_declared_absent` detail; `NCT03190694` as `eligible+completed+results_available` still counts when unpooled.
- Adjudicator consumer: synthetic served include for probiotics `34585011` becomes `ADJUDICATOR_DISAGREES`, recommended `exclude`.
- Artefact check: `docs/screening_delta.json` records 32 topics, 3,143 old screening rows, and the required named decision transitions.

Outputs:

- Initial plant run: `5 passed in 89.96s (0:01:29)`.
- Final targeted bundle after rebuild/ledger/search-seal fixes: `19 passed in 680.31s (0:11:20)`.
- Full final suite: `721 passed in 1376.16s (0:22:56)`.

## 3. Rebuilt pages changed

MEASURED `docs/screening_delta.json`: 49 decision changes of 3,143 old screening rows across 32 topics; 41 include->exclude, 8 exclude->include, 0 missing rows, 0 new rows. Same-decision rule changes: 11. Decision changes touched 15 topics; decision-or-rule changes touched 20 topics. All 20 affected pages were rebuilt with `python scripts/build_topic.py <slug> --now 2026-09-11` and replayed with `python scripts/reproduce_review.py <slug>`; all build/replay exit codes were 0.

Before/after primary-page metrics are `(eligible screening rows, primary k, primary declared-absent rows, invalidation reason codes)`:

| Page | Before | After |
| --- | --- | --- |
| `colchicine-postop-af` | `(8, 4, 4, search_not_executed,known_eligible_missing,eligible_declared_absent)` | `(8, 4, 4, search_not_executed,known_eligible_missing,eligible_declared_absent)` |
| `colchicine-recurrent-pericarditis` | `(3, 2, 1, search_not_executed,eligible_declared_absent)` | `(3, 2, 1, search_not_executed,eligible_declared_absent)` |
| `colchicine-secondary-cv-prevention` | `(29, 3, 26, search_not_executed,eligible_declared_absent)` | `(25, 3, 22, search_not_executed,eligible_declared_absent)` |
| `corticosteroids-covid19-mortality` | `(8, 1, 7, search_not_executed,eligible_declared_absent)` | `(7, 1, 6, search_not_executed,eligible_declared_absent)` |
| `doac-vte-recurrence` | `(6, 6, 0, search_not_executed)` | `(6, 6, 0, search_not_executed)` |
| `empagliflozin-hfpef-hosp` | `(4, 1, 3, search_not_executed,known_eligible_missing,eligible_declared_absent)` | `(3, 1, 2, search_not_executed,known_eligible_missing,eligible_declared_absent)` |
| `esketamine-trd-madrs` | `(6, 4, 2, search_not_executed,eligible_declared_absent)` | `(4, 4, 0, search_not_executed)` |
| `finerenone-ckd-t2d-renal` | `(6, 2, 4, search_not_executed,eligible_declared_absent)` | `(5, 2, 3, search_not_executed,eligible_declared_absent)` |
| `melatonin-primary-insomnia-sol` | `(9, 1, 8, search_not_executed,eligible_declared_absent)` | `(8, 1, 7, search_not_executed,eligible_declared_absent)` |
| `metformin-pcos-ovulation` | `(9, 3, 6, search_not_executed,eligible_declared_absent)` | `(7, 3, 4, search_not_executed,eligible_declared_absent)` |
| `noac-vs-warfarin-af-stroke` | `(9, 4, 5, search_not_executed,eligible_declared_absent)` | `(7, 4, 3, search_not_executed,eligible_declared_absent)` |
| `omega3-cardiovascular-events` | `(22, 7, 15, search_not_executed,eligible_declared_absent)` | `(20, 7, 13, search_not_executed,eligible_declared_absent)` |
| `probiotics-aad-prevention` | `(60, 16, 44, search_not_executed,eligible_declared_absent)` | `(57, 16, 41, search_not_executed,eligible_declared_absent)` |
| `semaglutide-obesity-weight` | `(14, 2, 12, search_not_executed,eligible_declared_absent)` | `(13, 2, 11, search_not_executed,eligible_declared_absent)` |
| `sglt2-ckd-progression` | `(8, 3, 5, search_not_executed,eligible_declared_absent)` | `(10, 3, 7, search_not_executed,eligible_declared_absent)` |
| `sglt2-primary-prevention-hf` | `(20, 4, 16, search_not_executed,eligible_declared_absent)` | `(6, 4, 2, search_not_executed,eligible_declared_absent)` |
| `spironolactone-hfref-mortality` | `(3, 3, 0, search_not_executed,identifier_single_agent_class_pool)` | `(3, 3, 0, search_not_executed)` |
| `statins-primary-prevention-elderly` | `(5, 2, 3, search_not_executed,eligible_declared_absent)` | `(4, 2, 2, search_not_executed,eligible_declared_absent)` |
| `ticagrelor-vs-clopidogrel-acs` | `(3, 2, 1, search_not_executed,eligible_declared_absent)` | `(3, 2, 1, search_not_executed,eligible_declared_absent)` |
| `tranexamic-acid-pph` | `(4, 1, 3, search_not_executed,eligible_declared_absent)` | `(4, 1, 3, search_not_executed,eligible_declared_absent)` |

Specific named outcomes:

- MIRO-CKD `NCT06350123`: `INCLUDE -> X-CONTRAST`.
- DIAMOND `NCT03190694`: `X2 -> INCLUDE`; declared absent, not pooled.
- EMPA-CKD `NCT07060417`: remains `INCLUDE`; screening and declared-absent rows carry `eligible+not_yet_recruiting`, `registry_status=NOT_YET_RECRUITING`, `completion_date=2029-09-30`; it is not in the `eligible_declared_absent` stale detail.
- Metformin `19552097`: `X2 -> INCLUDE`; declared absent, not pooled.
- ORGANON `NCT02935855`: `INCLUDE -> X1`.
- `NCT05006287`: `INCLUDE -> X2`.
- Probiotics `14627358`: `X3 -> INCLUDE`; declared absent, not pooled.
- Zarpelon `27223641`: `X2 -> INCLUDE`; declared absent, not pooled.
- SGLT2 primary prevention CVOT criterion reduced eligible rows from 20 to 6 while primary k stayed 4.

Adjudicator pending state after rebuild: MEASURED 5 pending disagreements across 4 topics:

- `colchicine-postop-af`: `39266309`, `22090167`
- `colchicine-recurrent-pericarditis`: `22430920`
- `omega3-cardiovascular-events`: `41201837`
- `probiotics-aad-prevention`: `40716758`

## 4. Tests

Commands run and final summaries:

- `python -m py_compile harness/screen.py harness/pipeline.py harness/invalidation.py harness/page.py` -> pass.
- `python scripts/seal_search_vocabulary.py --check` -> `SEAL OK: 32 of 32 sealed vocabularies match the working tree, 0 of 32 collide (sealed from 41a466fb35bdc470d73c479e878bbbc9f0979f9a)`.
- `python -m pytest tests/test_fixstate.py::test_real_store_validates tests/test_search_v2_guard.py tests/test_screen_contrast_and_ledger.py -q` -> `19 passed in 680.31s (0:11:20)`.
- `python -m pytest tests -x -q` -> `721 passed in 1376.16s (0:22:56)`.

Earlier verification failures and fixes:

- Full suite first failed because `docs/fix_ledger.json` was stale after rebuild; fixed by `python scripts/render_fix_ledger.py`.
- Full suite then failed because new screening vocabulary in `population_any` drifted the sealed search vocabulary for `colchicine-postop-af`; fixed by moving screening-only additions to `population_any_extra`, preserving the search seal and the no-search boundary.

## 5. What I did not do and why

- Did not commit, stage, stash, reset, checkout, clean, or push.
- Did not run network searches or change search queries.
- Did not touch `harness/synth.py`, harms, extraction code, or pooling code.
- Did not add new pooled trials. Newly included false-exclude records are declared absent/incompatible where extraction cannot pool them.
- Did not write ratchet acknowledgements; the lane prompt says the integrator signs those if needed.
- Did not update `F:\ProjectIndex\INDEX.md` or `F:\E156\rewrite-workbook.txt` because this lane did not change project status or submission state.

## 6. Files changed or added

Code:

- `harness/screen.py`
- `harness/pipeline.py`
- `harness/invalidation.py`
- `harness/page.py`

New artefacts/tests:

- `docs/screening_delta.json`
- `tests/test_screen_contrast_and_ledger.py`
- `LANE-SC-REPORT.md`

Topic configs:

- `topics/colchicine-postop-af.json`
- `topics/colchicine-secondary-cv-prevention.json`
- `topics/esketamine-trd-madrs.json`
- `topics/metformin-pcos-ovulation.json`
- `topics/noac-vs-warfarin-af-stroke.json`
- `topics/probiotics-aad-prevention.json`
- `topics/sglt2-ckd-progression.json`
- `topics/sglt2-primary-prevention-hf.json`

Protocols:

- `protocols/colchicine-postop-af.md`
- `protocols/colchicine-secondary-cv-prevention.md`
- `protocols/esketamine-trd-madrs.md`
- `protocols/metformin-pcos-ovulation.md`
- `protocols/noac-vs-warfarin-af-stroke.md`
- `protocols/probiotics-aad-prevention.md`
- `protocols/sglt2-ckd-progression.md`
- `protocols/sglt2-primary-prevention-hf.md`

Generated corpus/page artefacts:

- `docs/fix_ledger.json`
- `docs/index.html`
- `registry/blind_map.json`
- For each rebuilt slug below: `docs/reviews/<slug>/review.json`, `index.html`, `manifest.json`, `REPRODUCTION.json`.
  - `colchicine-postop-af`
  - `colchicine-recurrent-pericarditis`
  - `colchicine-secondary-cv-prevention`
  - `corticosteroids-covid19-mortality`
  - `doac-vte-recurrence`
  - `empagliflozin-hfpef-hosp`
  - `esketamine-trd-madrs`
  - `finerenone-ckd-t2d-renal`
  - `melatonin-primary-insomnia-sol`
  - `metformin-pcos-ovulation`
  - `noac-vs-warfarin-af-stroke`
  - `omega3-cardiovascular-events`
  - `probiotics-aad-prevention`
  - `semaglutide-obesity-weight`
  - `sglt2-ckd-progression`
  - `sglt2-primary-prevention-hf`
  - `spironolactone-hfref-mortality`
  - `statins-primary-prevention-elderly`
  - `ticagrelor-vs-clopidogrel-acs`
  - `tranexamic-acid-pph`
- Blind HTML pages:
  - `docs/m/m22bf81d5/index.html`
  - `docs/m/m24cd09bc/index.html`
  - `docs/m/m250220c2/index.html`
  - `docs/m/m2da64325/index.html`
  - `docs/m/m3c1155fb/index.html`
  - `docs/m/m586876fa/index.html`
  - `docs/m/m5b3fd56c/index.html`
  - `docs/m/m5e5590d5/index.html`
  - `docs/m/m612a48aa/index.html`
  - `docs/m/m87167438/index.html`
  - `docs/m/m8db5253b/index.html`
  - `docs/m/m979b0810/index.html`
  - `docs/m/ma0b91971/index.html`
  - `docs/m/maf69923c/index.html`
  - `docs/m/mb53e1ed5/index.html`
  - `docs/m/mb6ceb13c/index.html`
  - `docs/m/md68c6ad6/index.html`
  - `docs/m/me0751432/index.html`
  - `docs/m/me17c0a34/index.html`
  - `docs/m/me79cb3b0/index.html`

Pre-existing untracked files left untouched: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
