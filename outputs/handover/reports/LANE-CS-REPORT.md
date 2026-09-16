# LANE CS Report

Base: `ad5e7c66e97cf0e328daf7b3e15e7e4d4dda3b1d`.

## 1. What Was Wrong

`eligible_declared_absent` was a single STALE reason for multiple different truths. A page could say screened-in trials were not pooled and make all of them read as clinically threatening missing outcome data, even when the trial was still recruiting, terminated, surrogate-only, or not classifiable from committed evidence.

Mechanism added:

- `harness/completeness.py` classifies each eligible-but-unpooled entry into the requested five states plus `NOT_CLASSIFIABLE(...)` and orthogonal `REACH_MISS(named)`.
- `harness/invalidation.py` still emits `eligible_declared_absent`, but now its detail is a state distribution derived from the classifier.
- `harness/page.py` renders the required sentence: `search-incomplete: yes/no; clinically incomplete for this outcome: yes/no (states 1-2 count; states 3-5 do not)`.
- `harness/pipeline.py` passes committed registry records and publication records to invalidation.
- `harness/limitations.py` reuses the page STALE block, keeping limitation objects and rendered page blocks aligned.

I read `harness/invalidation.py`, `harness/absence.py`, `docs/known_eligible_missing.json`, `docs/never_considered.json`, and `LANE-RR-REPORT.md`. `LANE-SC-REPORT.md` and `LANE-SE-REPORT.md` were not present in the clone root. RR's row-level absence/refusal ontology remains separate; CS supersedes the old one-bucket eligible-unpooled completeness layer.

Measured sweep:

- MEASURED: `docs/completeness_sweep.json` covers 38 current `docs/reviews/*/review.json` pages. The prompt expected 32; the working tree currently has 38 review pages, including six pages absent at base.
- MEASURED state counts: `COMPLETED_OUTCOME_ABSENT_BY_DESIGN=17`, `COMPLETED_OUTCOME_HELD_NOT_EXTRACTED=26`, `COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=126`, `NOT_CLASSIFIABLE=73`, `ONGOING_OR_NOT_YET_RECRUITING=16`, `TERMINATED_OR_WITHDRAWN_NO_RESULTS=5`.
- MEASURED page counts: clinically incomplete `31 of 38`; search-incomplete `38 of 38`.
- MEASURED pages with zero clinically relevant states 1-2: `empagliflozin-hfpef-hosp`, `finerenone-ckd-t2d-renal`, `sacubitril-valsartan-hfref`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `tranexamic-acid-pph`.
- MEASURED `REACH_MISS(named)` entries: Sarzaeem 2014; CONFIDENCE 2025; Botticelli-DVT; ODIXa-DVT; J-ROCKET AF; ARISTOTLE-J; PETRO; Nestler 1998. Zarpelon is not listed as a reach miss.

Static-vs-dynamic disclosure:

| Item | Type | Disclosure |
| --- | --- | --- |
| Five state names | Static ontology | Constants in `harness/completeness.py`; no measured data encoded in the labels. |
| `REACH_MISS(named)` list | Static audit input | Prompt/audit-named trials only; not used to change pools. |
| Registry status/phase/completion | Dynamic committed evidence | Read from cached CT.gov JSON/raw records; missing fields produce `NOT_CLASSIFIABLE(...)`. |
| Publication/row absence codes | Dynamic committed evidence | Read from held review objects and RR row-level absence/refusal codes. |
| Page state distributions and clinical/search flags | Dynamic output | Recomputed during build and sweep; not typed into pages. |
| Corpus denominator | Dynamic output | Tests with stale `32`/`31` hardcodes were updated to live review counts after the measured corpus was 38 pages. |

## 2. Plant

New plant file: `tests/test_completeness.py`.

Assertions:

- Prefix plant loads `git show ad5e7c66:docs/reviews/finerenone-ckd-t2d-renal/review.json` and asserts the old object has exactly one `eligible_declared_absent` reason containing `NCT01874431`, `REC:NCT01968668`, `REC:NCT07775846`, and `FINECARE`, with no new state labels.
- Postfix finerenone assertion requires `NCT01874431` and `REC:NCT01968668` as `COMPLETED_OUTCOME_ABSENT_BY_DESIGN`, and `REC:NCT07775846` and `FINECARE` as `ONGOING_OR_NOT_YET_RECRUITING`.
- `NCT06229678` assertion requires state `ONGOING_OR_NOT_YET_RECRUITING`, phase `EARLY_PHASE1`, primary completion `2026-11-01`, enrollment `71`.
- COCS assertion requires `NCT04224545` as `COMPLETED_OUTCOME_HELD_NOT_EXTRACTED` with `COUNTS_PRESENT_NOT_CORROBORATED` in the basis.
- Synthetic assertion covers states 1-5 plus `NOT_CLASSIFIABLE(missing: registry.status)`.

Pre-fix quote from the test object assertion: the prefix object had one `eligible_declared_absent` bucket containing all four finerenone entries and no five-state labels. Post-fix quote from the rebuilt object: `{'NCT01874431': 'COMPLETED_OUTCOME_ABSENT_BY_DESIGN', 'REC:NCT01968668': 'COMPLETED_OUTCOME_ABSENT_BY_DESIGN', 'REC:NCT07775846': 'ONGOING_OR_NOT_YET_RECRUITING', 'FINECARE': 'ONGOING_OR_NOT_YET_RECRUITING'}`.

Targeted output:

```text
.....                                                                    [100%]
5 passed in 8.93s
```

## 3. Rebuilt Pages And STALE Blocks

Every current review page has a changed or added STALE block because the overview now appends the computed five-state distribution and the search/clinical sentence. For six pages, old = absent at `HEAD` because those review directories were not in base.

| Page | Old STALE block | New STALE block |
| --- | --- | --- |
| `antibiotics-vs-appendectomy-appendicitis` | absent at HEAD | n=7; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=4, NOT_CLASSIFIABLE=3; search=yes; clinical=yes |
| `azithromycin-copd-exacerbation` | absent at HEAD | n=7; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=4, NOT_CLASSIFIABLE=3; search=yes; clinical=yes |
| `balanced-crystalloids-vs-saline-mortality` | single eligible_declared_absent: NCT02444988, NCT02345486, PMID:26444692, PMID:27604335, NCT01270854, CRUSADERS | n=6; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=5, ONGOING_OR_NOT_YET_RECRUITING=1; search=yes; clinical=yes |
| `colchicine-postop-af` | single eligible_declared_absent: NCT04224545, REC:NCT07611019, REC:NCT07287345 | n=3; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1, ONGOING_OR_NOT_YET_RECRUITING=2; search=yes; clinical=yes |
| `colchicine-recurrent-pericarditis` | single eligible_declared_absent: NCT00128453 | n=1; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1; search=yes; clinical=yes |
| `colchicine-secondary-cv-prevention` | single eligible_declared_absent: 22 entries | n=22; COMPLETED_OUTCOME_ABSENT_BY_DESIGN=5, COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=8, NOT_CLASSIFIABLE=4, ONGOING_OR_NOT_YET_RECRUITING=4, TERMINATED_OR_WITHDRAWN_NO_RESULTS=1; search=yes; clinical=yes |
| `corticosteroids-cap-mortality` | single eligible_declared_absent: PMID:15557131, PMID:8339624, NCT01283009, PMID:21406101, NCT01743755, NCT00471640 | n=6; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=6; search=yes; clinical=yes |
| `corticosteroids-covid19-mortality` | single eligible_declared_absent: 7 entries | n=7; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=5, NOT_CLASSIFIABLE=1, TERMINATED_OR_WITHDRAWN_NO_RESULTS=1; search=yes; clinical=yes |
| `dapagliflozin-hfpef-hosp` | single eligible_declared_absent: NCT03030235, NCT04730947, STADIA-HFPEF, REC:NCT03877224 | n=4; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1, NOT_CLASSIFIABLE=3; search=yes; clinical=yes |
| `denosumab-vertebral-fracture` | STALE without eligible-unpooled state distribution | n=0; none; search=yes; clinical=no |
| `doac-vte-recurrence` | STALE without eligible-unpooled state distribution | n=0; none; search=yes; clinical=no |
| `dpp4-mace-t2d` | single eligible_declared_absent: NCT00968708, NCT00790205 | n=2; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=2; search=yes; clinical=yes |
| `empagliflozin-hfpef-hosp` | single eligible_declared_absent: SAK, EMPA-PRED, REC:NCT03448406 | n=3; NOT_CLASSIFIABLE=1, ONGOING_OR_NOT_YET_RECRUITING=2; search=yes; clinical=yes |
| `esketamine-trd-madrs` | single eligible_declared_absent: NCT02918318, SYNAPSE | n=2; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1, NOT_CLASSIFIABLE=1; search=yes; clinical=yes |
| `finerenone-ckd-t2d-renal` | single eligible_declared_absent: NCT01874431, REC:NCT01968668, REC:NCT07775846, FINECARE | n=4; COMPLETED_OUTCOME_ABSENT_BY_DESIGN=2, ONGOING_OR_NOT_YET_RECRUITING=2; search=yes; clinical=no |
| `glp1-ra-mace-t2d` | single eligible_declared_absent: NCT01147250 | n=1; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1; search=yes; clinical=yes |
| `hfnc-vs-conventional-o2-reintubation` | absent at HEAD | n=10; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=4, NOT_CLASSIFIABLE=6; search=yes; clinical=yes |
| `iv-iron-hfref-hosp` | single eligible_declared_absent: NCT03037931, PMID:34080008, NCT01394562, NCT00520780, NCT00125996 | n=5; NOT_CLASSIFIABLE=5; search=yes; clinical=yes |
| `melatonin-primary-insomnia-sol` | single eligible_declared_absent: 8 entries | n=8; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=7, NOT_CLASSIFIABLE=1; search=yes; clinical=yes |
| `metformin-pcos-ovulation` | single eligible_declared_absent: PMID:22419702, PMID:20925997, PMID:19692630, PMID:16827766, PMID:11994052, PMID:11473953 | n=6; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=6; search=yes; clinical=yes |
| `noac-vs-warfarin-af-stroke` | single eligible_declared_absent: REC:NCT00504556, ORGANON, REC:NCT00806624, REC:NCT05006287, REC:NCT00829933 | n=5; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1, NOT_CLASSIFIABLE=4; search=yes; clinical=yes |
| `omega3-cardiovascular-events` | single eligible_declared_absent: 14 entries | n=14; COMPLETED_OUTCOME_ABSENT_BY_DESIGN=2, COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=6, NOT_CLASSIFIABLE=5, ONGOING_OR_NOT_YET_RECRUITING=1; search=yes; clinical=yes |
| `pcsk9-mace` | STALE without eligible-unpooled state distribution | n=0; none; search=yes; clinical=no |
| `probiotics-aad-prevention` | single eligible_declared_absent: 42 entries | n=42; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=33, NOT_CLASSIFIABLE=9; search=yes; clinical=yes |
| `prone-positioning-ards-mortality` | absent at HEAD | n=5; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=3, NOT_CLASSIFIABLE=2; search=yes; clinical=yes |
| `sacubitril-valsartan-hfref` | single eligible_declared_absent: EVALUATE-HF, OUTSTEP-HF, ANSWER-HF, PRESENT-HF, PARALLEL-HF, PIONEER-HF | n=6; NOT_CLASSIFIABLE=6; search=yes; clinical=yes |
| `semaglutide-obesity-mace` | STALE without eligible-unpooled state distribution | n=0; none; search=yes; clinical=no |
| `semaglutide-obesity-weight` | single eligible_declared_absent: 11 entries | n=11; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=8, NOT_CLASSIFIABLE=2, ONGOING_OR_NOT_YET_RECRUITING=1; search=yes; clinical=yes |
| `sglt2-ckd-progression` | single eligible_declared_absent: REC:NCT07344922, DAPABALCI-LEAP, MIRO-CKD, EMPA-CKD, REC:NCT05614115 | n=5; COMPLETED_OUTCOME_ABSENT_BY_DESIGN=2, COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1, NOT_CLASSIFIABLE=1, ONGOING_OR_NOT_YET_RECRUITING=1; search=yes; clinical=yes |
| `sglt2-hfref-hosp-cvdeath` | single eligible_declared_absent: REC:NCT06229678 | n=1; ONGOING_OR_NOT_YET_RECRUITING=1; search=yes; clinical=no |
| `sglt2-primary-prevention-hf` | single eligible_declared_absent: 15 entries | n=15; COMPLETED_OUTCOME_ABSENT_BY_DESIGN=5, NOT_CLASSIFIABLE=10; search=yes; clinical=yes |
| `spironolactone-hfref-mortality` | STALE without eligible-unpooled state distribution | n=0; none; search=yes; clinical=no |
| `statins-primary-prevention-elderly` | single eligible_declared_absent: PMID:30251369, NCT00000542, NIA-PLAQUE | n=3; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=2, NOT_CLASSIFIABLE=1; search=yes; clinical=yes |
| `ticagrelor-vs-clopidogrel-acs` | single eligible_declared_absent: PMID:17980250 | n=1; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=1; search=yes; clinical=yes |
| `tocilizumab-covid19-mortality` | single eligible_declared_absent: 9 entries | n=9; COMPLETED_OUTCOME_ABSENT_BY_DESIGN=1, COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=5, NOT_CLASSIFIABLE=1, TERMINATED_OR_WITHDRAWN_NO_RESULTS=2; search=yes; clinical=yes |
| `tranexamic-acid-pph` | single eligible_declared_absent: NCT02805426, NCT02797119, TA TEG | n=3; NOT_CLASSIFIABLE=2, TERMINATED_OR_WITHDRAWN_NO_RESULTS=1; search=yes; clinical=yes |
| `vitamin-d-acute-respiratory-infection` | absent at HEAD | n=16; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=12, NOT_CLASSIFIABLE=3, ONGOING_OR_NOT_YET_RECRUITING=1; search=yes; clinical=yes |
| `zinc-common-cold-duration` | absent at HEAD | n=23; COMPLETED_OUTCOME_IN_SOURCE_NOT_HELD=22, NOT_CLASSIFIABLE=1; search=yes; clinical=yes |

Named cases measured from cache:

- Finerenone: ARTS-DN and ARTS-DN Japan -> state 3; FineCaRe and QUARTET-DKD -> state 4.
- SGLT2 HFrEF: `REC:NCT06229678` -> state 4 with `EARLY_PHASE1`, primary completion `2026-11-01`, enrollment `71`.
- SGLT2 CKD: EMPA-CKD -> state 4, `PHASE2`, primary completion `2029-03-31`.
- DPP4: `NCT00968708` and `NCT00790205` -> state 2.
- Colchicine postop AF: COCS `NCT04224545` -> state 1; Sarzaeem -> `REACH_MISS(named)`.

## 4. Tests

Commands and final outputs:

```text
python -m pytest tests/test_completeness.py -q
.....                                                                    [100%]
5 passed in 8.93s
```

```text
python scripts/completeness_sweep.py
OUT_WRITTEN C:\mh-r-CS\docs\completeness_sweep.json topics=38 clinically=31/38 search=38/38
```

```text
python scripts/reproduce_review.py
38/38 reproduce (all reproducible)
```

```text
python -m pytest tests -x -q
721 passed in 622.78s (0:10:22)
```

Additional full-suite repairs required by the current 38-page corpus:

- Added explicit `arm_contrast.json` and `rob2.json` cache files for `antibiotics-vs-appendectomy-appendicitis`, `hfnc-vs-conventional-o2-reintubation`, and `prone-positioning-ards-mortality` so pooled trials are not silently unassessed.
- Refreshed generated aggregate docs: `docs/evidence_base.json`, `docs/error_rate.json`, `docs/error_rate_sample.json`, `docs/fix_ledger.json`, and `docs/index.html`.
- Updated three tests that had stale hardcoded corpus counts or base-ref assumptions: `tests/test_limitations_legacy_compare.py`, `tests/test_publication_unit.py`, `tests/test_rob_sensitivity_predicate.py`.

## 5. Not Done

- Did not commit, stage, push, stash, reset, checkout, clean, or touch `.git/`.
- Did not rerun search, add/remove screened records, or change pooling logic.
- Did not extract missing outcomes; state 1 remains extraction debt and state 2 remains acquisition debt.
- Did not write ratchet acknowledgements; this report lists the reworded blocks for the integrator to sign.
- Did not run `scripts/verify_all.py`; the lane prompt reserves that for the integrator.
- `scripts/rob2_build.py` loaded local model weights and printed an HF unauthenticated-warning line while generating RoB caches for three already-built topics; no search retrieval was run.

## 6. Files Changed Or Added

Primary CS code and tests:

- `harness/completeness.py`
- `harness/invalidation.py`
- `harness/pipeline.py`
- `harness/page.py`
- `harness/limitations.py`
- `scripts/completeness_sweep.py`
- `tests/test_completeness.py`

Count/base-ref test maintenance required by the measured 38-page corpus:

- `tests/test_limitations_legacy_compare.py`
- `tests/test_publication_unit.py`
- `tests/test_rob_sensitivity_predicate.py`

Generated CS artefact:

- `docs/completeness_sweep.json`

Generated cache/support files from full-suite repairs:

- `cache/antibiotics-vs-appendectomy-appendicitis/arm_contrast.json`
- `cache/antibiotics-vs-appendectomy-appendicitis/rob2.json`
- `cache/hfnc-vs-conventional-o2-reintubation/arm_contrast.json`
- `cache/hfnc-vs-conventional-o2-reintubation/rob2.json`
- `cache/prone-positioning-ards-mortality/arm_contrast.json`
- `cache/prone-positioning-ards-mortality/rob2.json`
- `cache/embeddings.json` (8 added embedding keys from RoB generation)
- `docs/evidence_base.json`
- `docs/error_rate.json`
- `docs/error_rate_sample.json`
- `docs/fix_ledger.json`
- `docs/index.html`
- `registry/blind_map.json`

Rebuilt review artefacts:

- Existing modified review directories: `balanced-crystalloids-vs-saline-mortality`, `colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `dapagliflozin-hfpef-hosp`, `denosumab-vertebral-fracture`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `esketamine-trd-madrs`, `finerenone-ckd-t2d-renal`, `glp1-ra-mace-t2d`, `iv-iron-hfref-hosp`, `melatonin-primary-insomnia-sol`, `metformin-pcos-ovulation`, `noac-vs-warfarin-af-stroke`, `omega3-cardiovascular-events`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-ckd-progression`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `spironolactone-hfref-mortality`, `statins-primary-prevention-elderly`, `ticagrelor-vs-clopidogrel-acs`, `tocilizumab-covid19-mortality`, `tranexamic-acid-pph`.
- New/untracked review directories relative to base: `antibiotics-vs-appendectomy-appendicitis`, `azithromycin-copd-exacerbation`, `hfnc-vs-conventional-o2-reintubation`, `prone-positioning-ards-mortality`, `vitamin-d-acute-respiratory-infection`, `zinc-common-cold-duration`.
- Each rebuilt review directory contains the usual generated `REPRODUCTION.json`, `index.html`, `manifest.json`, and `review.json` files.

Generated blind-review pages:

- Modified existing `docs/m/*/index.html` pages and new `docs/m/` token directories created by `scripts/build_topic.py` during page rebuilds.

Untracked lane-control files left untouched:

- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
