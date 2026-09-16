# Reviewable served meta-analyses — the URL list (2026-09-16)

Served surface `https://mahmood726-cyber.github.io/meta-harness/`, commit `aa8ed28a` (MEASURED from the served `_production/manifest.json`, re-checked at list time; 0 of 32 pages changed bytes between my first fetch and this one). Population: the **32** review links in the served index = 32 `review_page_bindings` in the served manifest = 32 `docs/reviews/*` directories (MEASURED, three independent counts agree). Every check is against fetched bytes. Pages are static: 0 of 32 fetch anything client-side, so the text on the page is the page.

## STALE at a glance

**32 of 32 served pages fly the banner "STALE — this topic's result is not current"** (MEASURED: `invalidation.stale=true` in every served `review.json`; banner text present in every served `index.html`). Root cause on **32 of 32**: `search_not_executed` — no genuine executed concept search (KNOWN_ITEM / TITLE_SEEDED / HAND_WRITTEN_KEYWORD retrieval; each page retracts any systematic-search claim). Second reason on 27 of 32: `eligible_declared_absent` (a screened-in trial not pooled in any outcome). Others: `known_eligible_missing` 6, `never_considered` 2, `no_checkable_claim` 1 (iv-iron), `identifier_single_agent_class_pool` 1 (spironolactone). **"Fresh numbers + STALE banner" is the state of every page, not of two.** It is one defect — the corpus never ran a discovery-capable search — wearing 32 hats.

STALE means the *evidence set* is not claimed current or complete. It does not mean the numbers are wrong: the 22 pooled estimates below regenerate from committed inputs (`reproduce_review.py` replay 32/32 and `--fresh-clone` 32/32, MEASURED) and reproduce under an independent PM+HKSJ recompute from raw per-trial inputs (22 of 22, MEASURED, plant fired).

## REVIEWABLE — 22 of 32

Best-first: pages a reader can recompute from 2×2 counts, with real heterogeneity, an independently written search, and a comparator with a distinct trial set rank higher; pages whose agreement with the comparator is arithmetic (identical trial sets) rank lower.

Criteria, each MEASURED on served bytes: real source object (`review.json`+`manifest.json`+`REPRODUCTION.json`+committed protocol/cache: 32/32); pools k≥2 with per-trial inputs (2×2 counts, published effect+CI, or mean/SD/n: 22/32); not quarantined (no quarantine register exists in this repo — see NOT CHECKED); no fabricated NCT (595/595 NCTs on served pages resolve on ClinicalTrials.gov; 74/74 pooled-trial NCTs sit in that trial's own source record; both planted); trial set its own (every pooled row carries `verify_basis` from a committed PubMed/CT.gov record — 100% of pooled rows, MEASURED; on 28/32 the set was pre-identified rather than found, disclosed on-page, not treated as disqualifying).

Estimate = served primary outcome (MEASURED from served `review.json`). Content hash = the `review_sha256` prefix printed in each page header under "Pinned audit identity", quoted verbatim.

| # | URL | Topic | k | Served pooled estimate [95% CI] | Inputs | Search class | Content hash (page header) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | https://mahmood726-cyber.github.io/meta-harness/reviews/probiotics-aad-prevention/ | Probiotics vs placebo/no probiotic for prevention of antibiotic-associated diarrhoea | 16 | RR 0.702 [0.5352, 0.921] | 2x2, effect+CI | HAND_WRITTEN_KEYWORD | `9e6a3aca11d196e8` | STALE |
| 2 | https://mahmood726-cyber.github.io/meta-harness/reviews/omega3-cardiovascular-events/ | Marine omega-3 fatty acids vs placebo/control for major cardiovascular events | 7 | RR 0.943 [0.846, 1.051] | 2x2, effect+CI | TITLE_SEEDED | `3bb18fe68ebafadb` | STALE |
| 3 | https://mahmood726-cyber.github.io/meta-harness/reviews/glp1-ra-mace-t2d/ | GLP-1 receptor agonists vs placebo for 3-point MACE in type 2 diabetes | 8 | HR 0.856 [0.8086, 0.9061] | effect+CI | KNOWN_ITEM | `d77d184aa10edacf` | STALE |
| 4 | https://mahmood726-cyber.github.io/meta-harness/reviews/colchicine-postop-af/ | Colchicine vs placebo for prevention of postoperative atrial fibrillation | 4 | RR 0.6735 [0.376, 1.2067] | 2x2, effect+CI | HAND_WRITTEN_KEYWORD | `1d645bc2ec5d8f3c` | STALE |
| 5 | https://mahmood726-cyber.github.io/meta-harness/reviews/doac-vte-recurrence/ | Direct oral anticoagulants vs VKA for recurrent VTE in acute symptomatic venous thromboembolism | 6 | HR 0.9092 [0.7478, 1.1054] | 2x2, effect+CI | KNOWN_ITEM | `246f79cd41e610f3` | STALE |
| 6 | https://mahmood726-cyber.github.io/meta-harness/reviews/noac-vs-warfarin-af-stroke/ | Direct oral anticoagulants vs warfarin for stroke prevention in atrial fibrillation | 4 | HR 0.8069 [0.6611, 0.985] | effect+CI | KNOWN_ITEM | `24adf8e91a9bebfc` | STALE |
| 7 | https://mahmood726-cyber.github.io/meta-harness/reviews/sglt2-primary-prevention-hf/ | SGLT2 inhibitors vs placebo for hospitalization for heart failure in type 2 diabetes or cardiovascular risk | 4 | HR 0.6956 [0.5763, 0.8397] | effect+CI | KNOWN_ITEM | `6c58c6c93da673db` | STALE |
| 8 | https://mahmood726-cyber.github.io/meta-harness/reviews/esketamine-trd-madrs/ | Esketamine nasal spray vs placebo for MADRS change in treatment-resistant depression | 4 | MD -3.3445 [-6.0701, -0.6189] | mean/SD | TITLE_SEEDED | `3a539eeca29ebc9d` | STALE |
| 9 | https://mahmood726-cyber.github.io/meta-harness/reviews/sglt2-ckd-progression/ | SGLT2 inhibitors vs placebo for CKD progression in chronic kidney disease | 3 | HR 0.6836 [0.5537, 0.844] | effect+CI | KNOWN_ITEM | `7993e997fcec59dd` | STALE |
| 10 | https://mahmood726-cyber.github.io/meta-harness/reviews/colchicine-secondary-cv-prevention/ | Colchicine vs placebo for secondary prevention of cardiovascular events | 3 | HR 0.8134 [0.5074, 1.3039] | effect+CI | TITLE_SEEDED | `d85056d5b0ba682b` | STALE |
| 11 | https://mahmood726-cyber.github.io/meta-harness/reviews/metformin-pcos-ovulation/ | Metformin vs placebo for ovulation in women with polycystic ovary syndrome | 3 | OR 2.0733 [0.0922, 46.6008] | 2x2 | TITLE_SEEDED | `16523e6129d2e165` | STALE |
| 12 | https://mahmood726-cyber.github.io/meta-harness/reviews/dpp4-mace-t2d/ | DPP-4 inhibitors vs placebo for 3-point MACE in type 2 diabetes | 3 | HR 1.0074 [0.8391, 1.2094] | effect+CI | KNOWN_ITEM | `aaba73ab39328868` | STALE |
| 13 | https://mahmood726-cyber.github.io/meta-harness/reviews/spironolactone-hfref-mortality/ | Mineralocorticoid receptor antagonists vs placebo for all-cause mortality in HFrEF | 3 | RR/HR 0.8685 [0.3062, 2.4635] | 2x2, effect+CI | KNOWN_ITEM | `0e485c16b5347ad5` | STALE |
| 14 | https://mahmood726-cyber.github.io/meta-harness/reviews/finerenone-ckd-t2d-renal/ | Finerenone vs placebo for kidney outcomes in chronic kidney disease and type 2 diabetes | 2 | HR 0.8407 [0.4625, 1.5281] | effect+CI | TITLE_SEEDED | `6e8833ec15ee014a` | STALE |
| 15 | https://mahmood726-cyber.github.io/meta-harness/reviews/pcsk9-mace/ | PCSK9 inhibitors vs placebo for major adverse cardiovascular events | 2 | HR 0.85 [0.5852, 1.2346] | effect+CI | TITLE_SEEDED | `1a477e05fe47692e` | STALE |
| 16 | https://mahmood726-cyber.github.io/meta-harness/reviews/sglt2-hfref-hosp-cvdeath/ | SGLT2 inhibitors vs placebo for cardiovascular death or heart-failure hospitalisation in HFrEF | 2 | RR 0.7755 [0.4457, 1.3493] | 2x2 | KNOWN_ITEM | `61aa23bb6f160276` | STALE |
| 17 | https://mahmood726-cyber.github.io/meta-harness/reviews/semaglutide-obesity-weight/ | Semaglutide 2.4 mg vs placebo for percent body-weight change in overweight/obesity without diabetes | 2 | MD -11.8449 [-25.1318, 1.442] | mean/SD | TITLE_SEEDED | `66982cfe15bbd544` | STALE |
| 18 | https://mahmood726-cyber.github.io/meta-harness/reviews/balanced-crystalloids-vs-saline-mortality/ | Balanced crystalloids vs saline for mortality in critically ill adults | 2 | RR 0.9774 [0.6521, 1.465] | 2x2, effect+CI | TITLE_SEEDED | `dc7201e4753b1062` | STALE |
| 19 | https://mahmood726-cyber.github.io/meta-harness/reviews/colchicine-recurrent-pericarditis/ | Colchicine vs placebo for prevention of pericarditis recurrence | 2 | RR 0.4813 [0.064, 3.6169] | 2x2, effect+CI | HAND_WRITTEN_KEYWORD | `929c580c13410374` | STALE |
| 20 | https://mahmood726-cyber.github.io/meta-harness/reviews/corticosteroids-cap-mortality/ | Systemic corticosteroids vs placebo or usual care for mortality in hospitalised community-acquired pneumonia | 2 | RR 0.5458 [0.0361, 8.2605] | 2x2 | HAND_WRITTEN_KEYWORD | `eb09279de9273db5` | STALE |
| 21 | https://mahmood726-cyber.github.io/meta-harness/reviews/statins-primary-prevention-elderly/ | Statins vs placebo/control for primary prevention in older adults | 2 | HR 0.6803 [0.2897, 1.5975] | effect+CI | TITLE_SEEDED | `448547b8c1b81d7d` | STALE |
| 22 | https://mahmood726-cyber.github.io/meta-harness/reviews/ticagrelor-vs-clopidogrel-acs/ | Ticagrelor vs clopidogrel for major adverse cardiovascular events in acute coronary syndrome | 2 | HR 1.0479 [0.0324, 33.8921] | effect+CI | KNOWN_ITEM | `78a62bbd717ce0cc` | STALE |

All 22 rows: STALE (MEASURED). k, estimate and CI on every row were confirmed equal to the served `index.html` text by the byte-level replay (the page is rendered from the same object).

## NOT REVIEWABLE — 10 of 32

| Bucket | n of 32 | Pages | Why |
|---|---|---|---|
| k=1: single-trial summary in meta-analysis apparatus (real object, reproduces, nothing pooled) | 9 of 32 | corticosteroids-covid19-mortality, tocilizumab-covid19-mortality, melatonin-primary-insomnia-sol, sacubitril-valsartan-hfref, dapagliflozin-hfpef-hosp, empagliflozin-hfpef-hosp, denosumab-vertebral-fracture, semaglutide-obesity-mace, tranexamic-acid-pph | the served "pooled" row is one trial's published estimate verbatim; nothing to recompute. Recoverable second trials exist in full text for the two COVID pages and melatonin (declared-absent lists of 7, 8, 8); the rest are scope- or protocol-bound. |
| k=2 but pool SUPPRESSED (estimand-incompatible) | 1 of 32 | iv-iron-hfref-hosp | first-event HR vs recurrent-event rate ratio; page serves four declared strands, no single pooled row; `Claims checked: 0`. Reviewable as strands, not as a pool. |
| No source object / apparatus only | 0 of 32 | — | none on this site (the "291 apparatus-only" figure belongs to the RapidMeta corpus, not meta-harness) |
| Quarantined or fabricated NCT | 0 of 32 | — | 595/595 NCTs resolve; no quarantine register exists here |
| Donor trial set | 0 of 32 | — | none asserts another review's evidence base; 28/32 pre-identified sets are disclosed, not disqualified |

## NOT CHECKED (named, not dropped)

- **Quarantine register**: `QUARANTINE_DECISIONS.md` does not exist in meta-harness; it exists in RapidMeta worktrees (`ssot/QUARANTINE_DECISIONS.md`). The criterion could not execute here; no pass is claimed.
- **Exact comparator trial-set overlap**: `shared_k` reads "not exactly verifiable (comparator trial table not machine-exposed)" on 32/32 pages. Overlap verdicts in the companion audit are INFERRED from parity text.
- **Per-trial numbers against the papers**: not done — that is the review.
- **Retraction status**: CLAIMED from the harness's 2026-09-13 PubMed pass, not re-run.
- **RapidMeta corpus** (the ~368-link / 291-apparatus population): a different repo; not examined.

Companion: `outputs/INDEPENDENT_REVIEW_SET_2026-09-16.md` (per-page checks and open defects for the 22). The seven-page deep audit is a separate file.
