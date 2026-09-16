# Independently reviewable served meta-analyses — selection and verification (2026-09-16)

Served surface: `https://mahmood726-cyber.github.io/meta-harness/` — serving commit `aa8ed28a` (MEASURED, from the served `_production/manifest.json`; equals local HEAD and `origin/main`). Every check below was run against bytes fetched from that URL, not the working tree.

## Read this first — the population is not the one the brief describes

The brief's numbers (~368 index links, 291 apparatus-only pages, 55 object-backed, 122 donor evidence bases, 135 fabricated NCTs across 55 pages, `QUARANTINE_DECISIONS.md`, `self_reference`/`external_aggregate` comparator types, a bempedoic page, a client-side-injected benchmark card) **do not describe this site**:

| Brief says | This site (MEASURED unless marked) |
|---|---|
| ~368 index links | **41 `href`s** in the served index, of which **32** are review pages and 0 are `m/` pages |
| 291 apparatus-only pages | **0 of 32** — every review page ships `review.json` + `manifest.json` + `REPRODUCTION.json` + protocol (`topics/<slug>.json`) + committed cache |
| `QUARANTINE_DECISIONS.md` | **does not exist in this repo**; exists as `ssot/QUARANTINE_DECISIONS.md` in 10 RapidMeta worktrees (see below) |
| NCT detector / 135 fabricated NCTs | no such component here; substitute check run (below): **595 of 595** NCT IDs on served pages resolve on ClinicalTrials.gov |
| `self_reference` comparators | **0 of 32** — every comparator is a third-party publication with its own PMID; the field does not exist |
| bempedoic page | none; "bempedoic" occurs only inside cached search records |
| benchmark card injected client-side from JSON | **0 of 32** pages fetch anything — the sole `<script>` toggles tabs (grep for `fetch(`/`XMLHttpRequest`/`.json` in the script block: 0 hits) |

**Where those numbers do live (MEASURED, cross-drive search completed after the table above was drafted):** the RapidMeta project — `https://github.com/mahmood726-cyber/rapidmeta-finerenone` (local worktrees `C:/Projects/rm-enum-lane`, `F:/rapidmeta-main-fix`, `F:/rapidmeta-ssot-shell`, …), ~1,100 `*_REVIEW.html` pages, `ssot/QUARANTINE_DECISIONS.md`, `self_reference` typing in `DEFECT-REGISTRY.md` (e.g. LENACAPAVIR_PREP, CAB_PREP_HIV, NIRSEVIMAB rows), `RAPIDMETA-FABRICATED-NCT-SWEEP-2026-07-14.md`. **No RapidMeta worktree contains `reproduce_review.py`** — that is a meta-harness instrument. The brief therefore straddles two repos: criteria 1, 4 and 5 and all the quoted counts are RapidMeta's; criterion 3 (the definition of done) is meta-harness's. I was invoked in `C:\meta-harness` and this file covers meta-harness's 32 served pages in full. The RapidMeta selection is not done and is a separate job — see the last section.

I applied the five criteria as literally as they map onto the 32 pages that exist here, and say exactly where a criterion could not be executed.

## Corpus-wide checks (each 100% is a defect report — every instrument was planted and fired)

| Check | Result | How it was proved it can say "no" |
|---|---|---|
| Served bytes == committed bytes (index.html, review.json, manifest.json, REPRODUCTION.json) | **128 of 128** files, MEASURED (sha256) | planted: served pcsk9 vs local dpp4 → `False` |
| Served bytes == served `_production/manifest.json` per-file digest | **128 of 128**, MEASURED | same planted mismatch |
| `python scripts/reproduce_review.py` (replay from committed cache + protocol SHA, worktree clean at HEAD) | **32 of 32 OK, exit 0**, MEASURED, 40 s | planted one-byte edit (0.85→0.86) in pcsk9 `index.html` → `FAIL … does not byte-match`, exit 1; restored |
| `reproduce_review.py --fresh-clone` (git clone HEAD → temp dir → `build_topic.py` ×32 → byte-compare to committed pages) | **32 of 32 OK, `REPRODUCIBLE`, exit 0**, MEASURED | not separately planted — it reuses the same sha256 comparison the replay plant exercised; treat the plant as covering the comparator, not the clone/build path |
| `manifest.declared_method == manifest.served_method` | **32 of 32**, MEASURED | string equality; a differing string fails trivially |
| Independent recompute of every pooled primary from RAW per-trial inputs (own PM τ² + HKSJ t_{k-1} with floor, ignoring the harness's `study_effect`), tolerance 0.15% | **22 of 22** k≥2 pools agree on estimate and both CI bounds, MEASURED | planted +0.10 on one trial's RR → 0.7386 vs served 0.6735, DISAGREE |
| NCT IDs on served pages exist on ClinicalTrials.gov (v2 API, live) | **595 of 595** unique IDs, MEASURED | planted `NCT00000000` → HTTP 400, `NCT99999999` → 404 |
| NCT attributed to a pooled trial appears in that trial's own cached PubMed/CT.gov record (attribution, not just existence) | **74 of 74**, MEASURED | planted ODYSSEY's NCT against FOURIER's record → `False` |
| Retracted / expression-of-concern flags on pooled trials (harness `integrity` block, PubMed CommentsCorrections) | **0 of 32** pages flag any, CLAIMED (harness output, not re-run by me) | — |

Two things every one of the 32 pages carries and which are therefore not per-page defects: the blocking limitations `STALE_TOPIC`, `REPRODUCTION_RETRACTION`, `SEARCH_PROVENANCE` (and `SEARCH_ENUMERATION_ONLY` on the 11 known-item pages). They say: no protocol-only registration commit exists, the search was not a systematic concept search, and registration-time reproduction is retracted. The recompute above establishes "the numbers regenerate from committed inputs", not "the evidence set is complete".

**Retrieval class (MEASURED from `search.retrieval_class`)**: 11 KNOWN_ITEM (trials fetched by PMID), 17 TITLE_SEEDED, 4 HAND_WRITTEN_KEYWORD (colchicine-postop-af, colchicine-recurrent-pericarditis, corticosteroids-cap-mortality, probiotics-aad-prevention). Criterion 5 interpretation: every pooled trial on every page has its own source-verified extraction from a committed PubMed/CT.gov record (`verify_basis` set on 100% of pooled rows — MEASURED), so no page *asserts a donor review's evidence base* in the brief's sense. But on 28 of 32 the trial set was pre-identified rather than found, which is disclosed on-page. I did not exclude on this; I rank hand-written-keyword pages higher and flag the rest. Tighten if you disagree.

**Benchmark overlap (INFERRED throughout)**: `comparator.overlap.shared_k` reads "not exactly verifiable (comparator trial table not machine-exposed)" on **32 of 32** pages. Overlap verdicts below come from the page's parity decomposition text plus publication-date logic, not from a machine diff of two trial tables. "external-identical" = our pool is the comparator's comparable pool (agreement is arithmetic); "external-subset" = our pool ⊂ theirs; "external-distinct" = materially different sets. None is self-reference.

## Result

**22 of 32 served review pages qualify** (MEASURED against criteria 1–5 as mapped above). **1 almost** (iv-iron). **9 fail on k=1** (single-trial summaries, not pools). Denominator: the 32 review links in the served index, independently confirmed as the 32 `review_page_bindings` in the served manifest and the 32 directories under `docs/reviews/`.

Page displays: pooled effect, 95% CI, prediction interval, τ², method string. **I² is not rendered on any page**; the I² below is mine (MEASURED from the raw inputs, DL-Q based). Model on all 22: random-effects inverse-variance, Paule–Mandel τ², HKSJ CI on t_{k−1} with variance floor max(1, Q/(k−1)) — matches the Methods text on all 22 (MEASURED by recompute).

---

### 1. probiotics-aad-prevention
`https://mahmood726-cyber.github.io/meta-harness/reviews/probiotics-aad-prevention/`
Probiotics vs placebo/no probiotic for antibiotic-associated diarrhoea (RCTs, study end).
- **k=16, RR 0.702 [0.535, 0.921], PI [0.294, 1.676], τ²=0.150, I²=71%** (MEASURED). Inputs: 10 trials 2×2 counts, 6 published RR+CI. HAND_WRITTEN_KEYWORD search.
- Benchmark: Goodman 2021 BMJ Open PMID 34385227, RR 0.63 [0.54, 0.73], k=42. **External-distinct**: page says 9 of ours are in their table, 12 of ours postdate them (only_ours), 33 of theirs excluded by our screen (14 ineligible, 13 AAD-definition mismatch, 3 out of reach, 3 unrecoverable). INFERRED.
- **Check**: (a) the three hand overrides in trial sources — PMID 15740542 Can 2006 switched from any-diarrhoea 9/119 vs 29/127 to AAD 4/119 vs 22/127 (RR 0.19; blind second extractor read 0.3); PMID 40488914 switched from 14-day RR 0.47 to 56-day 0.46; PMID 18026577 Beausoleil switched from source OR 0.34 to count-RR 0.45. (b) "13 definition-mismatch" exclusions: the AAD definition (≥3 loose stools/24 h vs over ≥2 days) is doing a lot of the k=42→16 work.
- Open defects: 1 blind-extraction conflict on this page (page discloses count, not which row); parity text still says "our 15" while k=16 (one trial added later, disclosed); prevention-config re-screen owed (AUDIT_QUEUE "prevention topics at risk").

### 2. omega3-cardiovascular-events
`https://mahmood726-cyber.github.io/meta-harness/reviews/omega3-cardiovascular-events/`
Marine omega-3 vs placebo/control for major vascular events / MACE (double-blind RCTs).
- **k=7, RR 0.943 [0.846, 1.051], PI [0.728, 1.222], τ²=0.0093, I²=77%** (MEASURED). Inputs: STRENGTH 785/6539 vs 795/6539 (2×2); VITAL, REDUCE-IT, ASCEND, ORIGIN, Alpha Omega, SU.FOL.OM3 as published HR/RR+CI. TITLE_SEEDED.
- Benchmark: Jiang 2022 Medicine PMID 35905212, RR 0.94 [0.89, 1.00], k=28. **External-distinct** (theirs 28 vs ours 7; page names 6 open-label, 5 scope, 4 differing-composite exclusions). INFERRED.
- **Check**: (a) labels mixed — 6 of 7 inputs are HRs pooled under an RR label (`compatible_labels`; comparator-sweep OURS defect `mixed_ratio_labels_pooled_as_one`); (b) ORIGIN override — extractor first took the CV-death primary (HR 0.98), override pins major-vascular-events HR 1.01 — confirm against PMID 22686415; (c) three factorial trials (VITAL, ORIGIN, SU.FOL.OM3) pooled as marginal contrasts, not adjusted; (d) REDUCE-IT (mineral-oil comparator) sits in a "placebo" pool.
- Open defects: 4 pooled trials retrospectively registered per harness (20929341, 22686415, 30146932, 30415628 — check, ASCEND/REDUCE-IT retrospective looks wrong); OMEMI and OMEGA-REMODEL eligible-not-pooled.

### 3. glp1-ra-mace-t2d
`https://mahmood726-cyber.github.io/meta-harness/reviews/glp1-ra-mace-t2d/`
GLP-1 RAs vs placebo for 3-point MACE in T2D (double-blind RCTs).
- **k=8, HR 0.856 [0.809, 0.906], PI [0.807, 0.908], τ²=0.00004, I²=1%** (MEASURED). All 8 published HR+CI (PIONEER 6, SUSTAIN-6, LEADER, AMPLITUDE-O, REWIND, Harmony Outcomes, EXSCEL, SOUL). KNOWN_ITEM.
- Benchmark: Cardiovasc Diabetol 2021 PMID 34526024, HR 0.86 [0.79, 0.94], "eight CVOTs". **External-overlapping**: 7 shared; SOUL (2025) is only-ours; ELIXA is only-theirs (declared absent here as 4-point MACE). INFERRED.
- **Check**: (a) the 0.856 vs 0.86 agreement is near-arithmetic — 7 of 8 trials shared; (b) ELIXA exclusion (4-point MACE incl. unstable angina) vs inclusion of trials whose "3-point" definitions vary — read each primary definition.
- Open defects: AUDIT_QUEUE item 10 — comparator k re-labelled 7 while its published estimate was computed on k=8 (k-vs-estimate incoherence on the page's parity text); 5 of 8 numbers "reconcile" rather than "agree" with the blind second extractor.

### 4. colchicine-postop-af
`https://mahmood726-cyber.github.io/meta-harness/reviews/colchicine-postop-af/`
Peri-operative colchicine vs placebo/usual care for postoperative AF after cardiac surgery.
- **k=4, RR 0.674 [0.376, 1.207], PI [0.237, 1.914], τ²=0.074, I²=52%** (MEASURED). Inputs: COPPS-2 61/180 vs 75/180, END-AF 26/179 vs 37/181, END-AF-low-dose 13/81 vs 13/71 (2×2); PMID 42132185 "Post-CABG Arrhythmias" RR 0.37 [0.21, 0.66] (published). HAND_WRITTEN_KEYWORD. GRADE low.
- Benchmark: Zhao 2022 J Cardiothorac Surg PMID 36050741, RR 0.62 [0.52, 0.74], k=9 (comparable k=7). **External-distinct** (4 shared-or-equivalent; Bessissow, Zarpelon, Sarzaeem, COPPS AF substudy, COCS not pooled here, 2 PVI-ablation trials scope-excluded). INFERRED.
- **Check**: (a) PMID 42132185 is the most influential trial (leave-one-out range 0.61–0.79) and was recovered by a screening fix because its title omits "atrial fibrillation" — verify it is a cardiac-surgery RCT with POAF as an outcome and that RR 0.37 is the POAF result; (b) timepoint mixture (index-admission / 14-day / 30-day POAF) pooled as one.
- Open defects: none page-specific beyond the corpus-wide set; prevention-config re-screen done for this topic (AUDIT_QUEUE).

### 5. doac-vte-recurrence
`https://mahmood726-cyber.github.io/meta-harness/reviews/doac-vte-recurrence/`
DOACs vs VKA for recurrent VTE in acute symptomatic VTE.
- **k=6, HR 0.909 [0.748, 1.105], PI [0.748, 1.105], τ²=0, I²=0%** (MEASURED). Inputs: RE-COVER, RE-COVER II, EINSTEIN-DVT, EINSTEIN-PE, AMPLIFY as published HR+CI; Hokusai-VTE 59/2609 vs 71/2635 (2×2). KNOWN_ITEM.
- Benchmark: van Es 2014 Blood PMID 24963045, RR 0.90 [0.77, 1.06]. **External-identical (INFERRED)** — the 2014 phase-3 set is these 6 trials (comparator k not stated on page; full text not obtained — "open-access label failure").
- **Check**: (a) PI equals CI exactly — here both use t_{k−1} and τ²=0, so they coincide by construction; confirm the CI is HKSJ-t and not z (a z-CI with a t-PI would not coincide); (b) Hokusai-VTE reconstructed as count-RR and pooled under HR (`compatible_labels`; sweep OURS defect); (c) EINSTEIN-Extension excluded as extended-treatment estimand — agree?
- Open defects: RE-COVER (24344086) flagged retrospectively registered; comparator full text not retrievable despite OA flag.

### 6. noac-vs-warfarin-af-stroke
`https://mahmood726-cyber.github.io/meta-harness/reviews/noac-vs-warfarin-af-stroke/`
DOACs vs warfarin for stroke or systemic embolism in non-valvular AF (pairwise).
- **k=4, HR 0.807 [0.661, 0.985], PI [0.575, 1.132], τ²=0.0074, I²=42%** (MEASURED). Inputs: ROCKET AF 0.88 [0.74, 1.03], RE-LY 150 mg 0.66 [0.53, 0.82], ENGAGE AF 60 mg 0.87 [0.745, 1.016], ARISTOTLE 0.79 [0.66, 0.95]. KNOWN_ITEM.
- Benchmark: COMBINE-AF 2022 Circulation PMID 34985309, HR 0.81 [0.74, 0.89]. **External-identical**: same 4 trials (theirs is patient-level). INFERRED.
- **Check**: (a) **ROCKET AF: pooled ITT HR 0.88; the blind second extractor located the per-protocol on-treatment 0.79 in the abstract** (`docs/dual_extraction.json` disagreement) — which analysis you want is a decision, and it moves the pool; (b) RE-LY "approved-dose 150 mg" rule and ENGAGE 60 mg selection — a documented pre-specified rule, but verify.
- Open defects: **parity text on the served page quotes "Pooled RR 0.805 (0.658–0.984)" while the served pool is HR 0.807 [0.661, 0.985]** (MEASURED: both strings present on the served page) — stale text vs number.

### 7. sglt2-primary-prevention-hf
`https://mahmood726-cyber.github.io/meta-harness/reviews/sglt2-primary-prevention-hf/`
SGLT2i vs placebo for HF hospitalisation in T2D / CV risk (CVOTs).
- **k=4, HR 0.696 [0.576, 0.840], PI [0.576, 0.840], τ²=0, I²=0%** (MEASURED). CANVAS 0.67, EMPA-REG 0.65, VERTIS-CV 0.70, DECLARE 0.73 (published HR+CI). KNOWN_ITEM.
- Benchmark: Front Endocrinol 2020 PMID 33519713, RR 0.63 [0.53, 0.74], k=3. **External-subset-plus-one**: their 3 ⊂ our 4 (VERTIS-CV postdates them). INFERRED.
- **Check**: (a) 8 declared-absent eligible trials, incl. SCORED/SOLOIST/DAPA-HF-type entries — check whether any is a primary-prevention CVOT with HHF reported; (b) `only_ours` lists 4 PMIDs that are declared-absent, not pooled — the overlap field is counting non-pooled items.
- Open defects: prevention-config re-screen owed for this topic (AUDIT_QUEUE).

### 8. esketamine-trd-madrs
`https://mahmood726-cyber.github.io/meta-harness/reviews/esketamine-trd-madrs/`
Intranasal esketamine + oral AD vs placebo + oral AD, MADRS change at Day 28 (MD).
- **k=4, MD −3.34 [−6.07, −0.62], PI same, τ²=0, I²=0%** (MEASURED). Inputs: per-arm mean/SD/n for TRANSFORM-3 (37025256), TRANSFORM-2 (31109201), and two CT.gov-results-only entries NCT02422186 (phase-2 dose-finding) and NCT02417064 (TRANSFORM-1). TITLE_SEEDED.
- Benchmark: Front Psychiatry 2026 PMID 42490943, MD −2.99 [−5.10, −0.88], k=4 (number lives in the parity text; `comparator.reported` is empty). **External-identical (INFERRED)**.
- **Check**: (a) **internal contradiction on the served page**: parity text says "We pool 2 … TRANSFORM-1 and the phase-2 dose-finding … refused" while k=4 includes both (MEASURED: both strings on the served page); (b) TRANSFORM-1 row n=209 vs 108 — which fixed-dose arms were combined and how (56 mg + 84 mg pooled?); (c) TRANSFORM-3 is an elderly population pooled with adult trials.
- Open defects: the stale parity text above; SD values to 2 dp suggest SE→SD conversion — check.

### 9. sglt2-ckd-progression
`https://mahmood726-cyber.github.io/meta-harness/reviews/sglt2-ckd-progression/`
SGLT2i vs placebo for CKD progression / kidney composite in CKD.
- **k=3, HR 0.684 [0.554, 0.844], PI [0.525, 0.889], τ²=0.0013, I²=18%** (MEASURED). DAPA-CKD 0.61, CREDENCE 0.70, EMPA-KIDNEY 0.72 (published HR+CI; two SCALE-CORRECTION overrides replacing count-RRs). KNOWN_ITEM.
- Benchmark: JAMA 2026 PMID 41203232, HR 0.62 [0.57, 0.68], k=10 (IPD). **External-subset**: our 3 ⊂ their 10. INFERRED.
- **Check**: **DECLARE-TIMI 58 is excluded because its renal composite "includes cardiovascular death" — but all three pooled primaries include CV death too** (DAPA-CKD: renal/CV death; CREDENCE: renal or CV death; EMPA-KIDNEY: "kidney disease progression or CV death") — MEASURED from the trial `source` strings and `estimand_exclusions` on the page. Either the exclusion reason or the pool is wrong.
- Open defects: the above; comparator full text not retrievable despite OA flag.

### 10. colchicine-secondary-cv-prevention
`https://mahmood726-cyber.github.io/meta-harness/reviews/colchicine-secondary-cv-prevention/`
Low-dose colchicine vs placebo for MACE in coronary disease / recent MI.
- **k=3, HR 0.813 [0.507, 1.304], PI [0.349, 1.897], τ²=0.027, I²=78%** (MEASURED). COLCOT 0.77, LoDoCo2 0.69, CLEAR SYNERGY 0.99 (published HR+CI). TITLE_SEEDED.
- Benchmark: Front Cardiovasc Med 2022 PMID 36176989, RR 0.65 [0.38, 0.77] (k not stated). **External-overlapping (INFERRED)** — CLEAR SYNERGY (2024) postdates it; the comparator predates the null result.
- **Check**: (a) the comparator's CI [0.38, 0.77] around 0.65 is asymmetric on the log scale — likely a transcription error on our page or theirs; (b) CLEAR SYNERGY is 2×2 factorial (with spironolactone) pooled as a marginal contrast; (c) 8 declared-absent trials incl. 34876021 and 40263680 — are any MACE-reporting colchicine RCTs that should be in?
- Open defects: AUDIT_QUEUE items 5–6 (CLEAR SYNERGY GI harms refused with a wrong reason) — harms outcome, not primary; no parity row exists for this page.

### 11. metformin-pcos-ovulation
`https://mahmood726-cyber.github.io/meta-harness/reviews/metformin-pcos-ovulation/`
Metformin vs placebo for ovulation in PCOS (OR).
- **k=3, OR 2.07 [0.09, 46.6], PI [0.008, 550], τ²=1.16, I²=78%** (MEASURED). All 2×2: 10/16 vs 6/16 (19522426), 71/111 vs 82/114 (16769748), 9/12 vs 4/15 (11172832). TITLE_SEEDED. GRADE low.
- Benchmark: Cochrane CD013505 2019 PMID 31845767, OR 2.64 [1.85, 3.75], k=13. **External-distinct** (Cochrane 13 vs our 3). INFERRED.
- **Check**: (a) 16769748 (Moll 2006) is metformin+clomifene vs placebo+clomifene — is "metformin vs placebo" the right comparison label for a pool that mixes CC-background trials?; (b) per-woman vs per-cycle ovulation (`docs/cochrane_headtohead.json` says the Cochrane per-trial numbers are per-cycle; that file also still says our k=1 — stale); (c) with k=3 and τ²=1.16 the HKSJ interval is the page's honest answer, but the point estimate is meaningless.
- Open defects: `cochrane_headtohead.json` stale (k=1 vs served k=3); comparator full text not retrievable despite OA flag.

### 12. dpp4-mace-t2d
`https://mahmood726-cyber.github.io/meta-harness/reviews/dpp4-mace-t2d/`
DPP-4 inhibitors vs placebo for 3-point MACE in T2D.
- **k=3, HR 1.007 [0.839, 1.209], PI same, τ²=0, I²=0%** (MEASURED). SAVOR-TIMI 53 1.00, CARMELINA 1.02, PMID 28893244 1.00 [0.77, 1.29] (published). KNOWN_ITEM.
- Benchmark: World J Cardiol 2021 PMID 34754403 — **no comparator estimate on the page** (`reported: []`), so the benchmark is **not checkable** from the page (external by PMID only).
- **Check**: (a) identify PMID 28893244 (an omarigliptin CVOT? — a non-marketed DPP4i) and whether the protocol admits it; (b) TECOS declared absent as 4-point MACE — correct — but EXAMINE (23992602) declared absent for lacking a two-sided CI: is that a refusal you accept?
- Open defects: benchmark number absent.

### 13. spironolactone-hfref-mortality
`https://mahmood726-cyber.github.io/meta-harness/reviews/spironolactone-hfref-mortality/`
MRAs (spironolactone/eplerenone) vs placebo for all-cause mortality in HFrEF.
- **k=3, RR/HR 0.869 [0.306, 2.464], PI [0.128, 5.912], τ²=0.140, I²=63%** (MEASURED). RALES 0.70, EMPHASIS-HF 0.76 (published); J-EMPHASIS-HF 17/111 vs 10/110 reconstructed RR 1.68. KNOWN_ITEM. GRADE low.
- Benchmark: Front Cardiovasc Med 2025 PMID 40959489, HR 0.78 [0.72, 0.85], k=9. **External-subset** (RALES+EMPHASIS shared; EPHESUS scope-excluded). INFERRED.
- **Check**: (a) **AUDIT_QUEUE item 7**: J-EMPHASIS-HF was reconstructed from counts although the paper reports a time-to-event HR 1.77 [0.81, 3.87] — violates the page's own "published effect beats reconstruction" hierarchy; (b) the page carries a BLOCKS_CLAIM `IDENTIFIER_SCOPE` limitation: slug says spironolactone, 2 of 3 trials are eplerenone.
- Open defects: both above; **parity text "RALES + EMPHASIS = our pool" is on the served page while k=3 includes J-EMPHASIS-HF** (MEASURED); mixed RR/HR labels.

### 14. finerenone-ckd-t2d-renal
`https://mahmood726-cyber.github.io/meta-harness/reviews/finerenone-ckd-t2d-renal/`
Finerenone vs placebo, kidney composite in CKD + T2D.
- **k=2, HR 0.841 [0.463, 1.528], τ²=0, I²=0%** (MEASURED). FIDELIO-DKD 0.82 [0.73, 0.93] (SCALE-CORRECTION override from count-RR 0.84), FIGARO-DKD 0.87 [0.76, 1.01]. TITLE_SEEDED.
- Benchmark: Front Endocrinol 2023 PMID 36742404, HR 0.84 [0.77, 0.92]. **External-identical** — "FIDELIO+FIGARO = our exact pool" (page). Agreement is arithmetic. INFERRED.
- **Check**: the k=2 HKSJ CI (t on 1 df) is 3× wider than the comparator's; FIGARO's kidney composite was a *secondary* endpoint — is that within protocol?
- Open defects: none page-specific.

### 15. pcsk9-mace
`https://mahmood726-cyber.github.io/meta-harness/reviews/pcsk9-mace/`
PCSK9 inhibitors vs placebo for MACE (ASCVD).
- **k=2, HR 0.850 [0.585, 1.235], τ²=0, I²=0%** (MEASURED). FOURIER 0.85 [0.79, 0.92], ODYSSEY OUTCOMES 0.85 [0.78, 0.93]. TITLE_SEEDED.
- Benchmark: Rahhal 2022 PMID 36531722, RR 0.83 [0.79, 0.87], k=12. **External-subset** (2 of 12; ~87% of their patients per page). INFERRED.
- **Check**: FOURIER's and ODYSSEY's primary composites differ (FOURIER 5-point incl. revascularisation/hospitalised UA; ODYSSEY 4-point incl. UA) — pooled as one "MACE".
- Open defects: none page-specific.

### 16. sglt2-hfref-hosp-cvdeath
`https://mahmood726-cyber.github.io/meta-harness/reviews/sglt2-hfref-hosp-cvdeath/`
SGLT2i vs placebo, CV death or HF hospitalisation in HFrEF.
- **k=2, RR 0.776 [0.446, 1.349], τ²=0, I²=0%** (MEASURED). DAPA-HF 386/2373 vs 502/2371, EMPEROR-Reduced 361/1863 vs 462/1867 (2×2). KNOWN_ITEM.
- Benchmark: ESC Heart Fail 2022 PMID 35112512, HR 0.74 [0.68, 0.81]. **External-identical** for LVEF ≤40% (their gaps HFpEF/mixed). INFERRED.
- **Check**: count-derived RR pooled where both trials publish HRs (0.74 and 0.75) — the page's own hierarchy says published effect beats reconstruction.
- Open defects: none page-specific.

### 17. semaglutide-obesity-weight
`https://mahmood726-cyber.github.io/meta-harness/reviews/semaglutide-obesity-weight/`
Semaglutide 2.4 mg vs placebo, % body-weight change at Week 68 (MD).
- **k=2, MD −11.84 [−25.13, 1.44], τ²=1.86, I²=85%** (MEASURED). STEP 1 (33567185) −15.6 vs −2.8 %, n 1306/655; STEP 3 (33625476) −16.5 vs −5.8 %, n 407/204 (per-arm mean/SD/n). TITLE_SEEDED.
- Benchmark: Medicine 2026 PMID 42536519 — **no comparator estimate on the page** (`reported: []`); parity text says STEP-1 and STEP-3 are both in their 4. **External-subset**, benchmark number absent.
- **Check**: (a) the SDs (10.1 / 7.7 / 10.1 / 6.5) are to 1 dp and identical across the two semaglutide arms — likely back-converted from a CI or SE; verify against the papers; (b) STEP 3 adds intensive behavioural therapy in both arms — same estimand as STEP 1?
- Open defects: benchmark number absent; two regional trials refused for Week-44 timepoint.

### 18. balanced-crystalloids-vs-saline-mortality
`https://mahmood726-cyber.github.io/meta-harness/reviews/balanced-crystalloids-vs-saline-mortality/`
Balanced crystalloids vs saline for mortality in critically ill adults.
- **k=2, RR 0.977 [0.652, 1.465], τ²=0, I²=0%** (MEASURED). PLUS 530/2433 vs 530/2413 (2×2), BaSICS 0.97 [0.90, 1.05] (published HR labelled RR). TITLE_SEEDED.
- Benchmark: J Intensive Care 2018 PMID 30140441, OR 0.92 [0.85, 1.01], k=6 (mortality k=5). **External-distinct** — SMART, SALT, SPLIT are on their side and refused on ours. INFERRED.
- **Check**: the design refusal — SMART/SALT/SPLIT excluded as cluster-crossover with unadjusted SE. Defensible, but it removes ~3/5 of the comparator's evidence; BaSICS is a 2×2 factorial (infusion rate) pooled marginally.
- Open defects: comparator-sweep OURS defects ×2 (design variance; mixed HR/RR labels).

### 19. colchicine-recurrent-pericarditis
`https://mahmood726-cyber.github.io/meta-harness/reviews/colchicine-recurrent-pericarditis/`
Colchicine + conventional therapy vs placebo for recurrent pericarditis (double-blind).
- **k=2, RR 0.481 [0.064, 3.617], τ²=0, I²=0%** (MEASURED). CORP-2 26/120 vs 51/120 (2×2), CORP RR 0.44 [0.27, 0.73] (published). HAND_WRITTEN_KEYWORD.
- Benchmark: Imazio 2012 Heart PMID 22442198, RR 0.40 [0.30, 0.54], k=5 (comparable 4). **External-distinct** (CORE, COPE open-label excluded; Finkelstein scope-excluded). INFERRED.
- **Check**: (a) **2 of 4 abstract-checkable numbers conflicted with the blind second extractor** and the page does not say which — re-derive CORP's 0.44 and CORP-2's counts; (b) ICAP (23992557) is listed declared-absent with the reason text beginning "ELIGIBLE under the registered broad PICO" — an eligible trial not pooled.
- Open defects: both above; comparator full text not retrievable despite OA flag.

### 20. corticosteroids-cap-mortality
`https://mahmood726-cyber.github.io/meta-harness/reviews/corticosteroids-cap-mortality/`
Systemic corticosteroids vs placebo/usual care, all-cause mortality in hospitalised CAP.
- **k=2, RR 0.546 [0.036, 8.26], τ²=0, I²=0%** (MEASURED). CAPE COD 25/400 vs 47/395, Torres 2015 6/61 vs 9/59 (2×2). HAND_WRITTEN_KEYWORD. GRADE low.
- Benchmark: J Crit Care 2024 PMID 38128217, RR 0.69 [0.53, 0.89] (k not stated). **External-distinct** (INFERRED; 7 eligible trials declared absent here).
- **Check**: 7 declared-absent trials incl. Blum 2015 (25608756, n=785) and Meduri/ESCAPe (35723686) — mortality is in their full texts; k=2 vs the comparator's pool is a reach gap, not a scope gap. Torres flagged retrospectively registered.
- Open defects: comparator full text not retrievable despite OA flag.

### 21. statins-primary-prevention-elderly
`https://mahmood726-cyber.github.io/meta-harness/reviews/statins-primary-prevention-elderly/`
Statins vs placebo/control, major vascular events, ≥70 y primary prevention.
- **k=2, served as HR 0.680 [0.290, 1.598], τ²=0, I²=0%** (MEASURED). JUPITER ≥70 subgroup (20404379) 0.61 [0.46, 0.82]; PMID 42670961 0.70 [0.61, 0.82]. Both inputs labelled RR; result labelled HR. TITLE_SEEDED.
- Benchmark: Rev Cardiovasc Med 2022 PMID 39076238, HR 0.75 [0.66, 0.85] — **page itself marks the comparator INVALID (12 observational studies, 0 RCTs)**. Benchmark fails as an RCT-meta comparator.
- **Check**: (a) a *subgroup* (JUPITER ≥70) is pooled as a trial; (b) the RR-inputs → HR-result label flip; (c) identify 42670961 (2026) and its population.
- Open defects: comparator invalid; page still renders a "common-effect CI (k=2 sensitivity) 0.60–0.78".

### 22. ticagrelor-vs-clopidogrel-acs
`https://mahmood726-cyber.github.io/meta-harness/reviews/ticagrelor-vs-clopidogrel-acs/`
Ticagrelor vs clopidogrel, CV death/MI/stroke in ACS.
- **k=2, HR 1.048 [0.032, 33.9], τ²=0.122, I²=78%** (MEASURED). PLATO 0.84 [0.77, 0.92], PHILO 1.47 [0.88, 2.44]. KNOWN_ITEM.
- Benchmark: PLoS One 2017 PMID 28545073, OR 0.83 [0.77, 0.90], k=5 (page: 1 valid RCT = PLATO). **External-overlapping**: PLATO shared; PHILO only-ours. INFERRED.
- **Check**: AUDIT_QUEUE item 9 — direction conflict PLATO vs PHILO (I²≈78%) and GRADE did not downgrade for inconsistency ("τ²" reasoning); whether PHILO (East Asian, n≈800, efficacy secondary) belongs in a pool with PLATO.
- Open defects: the GRADE inconsistency gap; parity text "1 valid RCT (PLATO) = ours" while k=2.

---

## Almost qualified (1)

- **iv-iron-hfref-hosp** — k=2 with inputs present (CONFIRM-HF HR 0.39, FAIR-HF2 0.80) but the pool is **SUPPRESSED** as estimand-incompatible (first-event HR vs recurrent-event rate ratio); no pooled number, `CLAIM_CHECK_ZERO` and `SUPPRESSED_POOL` block. Reproduces (MEASURED). To get it in: pool the strands separately on the review page (the strands exist only as an index section; AUDIT_QUEUE notes their CIs were z-based until fixed) or decide one estimand and re-extract HEART-FID/AFFIRM-AHF accordingly.

## Failed on k=1 (9) — trial summaries in meta-analysis apparatus, and what would recover a second trial

| Page | k=1 trial | Declared-absent eligible | Recoverable? |
|---|---|---|---|
| corticosteroids-covid19-mortality | RECOVERY (OR 0.83, served under an RR label) | 7 (CoDEX, REMAP-CAP, CAPE COVID, Metcovid…) | yes — 28-day mortality is in full texts; PMC adapter did not run |
| tocilizumab-covid19-mortality | RECOVERY 621/2022 vs 729/2094 | 8 (REMAP-CAP, COVACTA, EMPACTA, TOCIBRAS…) | yes — same reason |
| melatonin-primary-insomnia-sol | Wade 2011 (65–80 y subgroup!) | 8 | partly; note the pooled row is an age *subgroup* |
| sacubitril-valsartan-hfref | PARADIGM-HF | 6 NCT-only | no published second HFrEF outcome RCT on this composite |
| dapagliflozin-hfpef-hosp | DELIVER | 4 | no (others are surrogate endpoints) |
| empagliflozin-hfpef-hosp | EMPEROR-Preserved | 3 NCT-only | no |
| denosumab-vertebral-fracture | FREEDOM | 0 (DIRECT excluded by protocol: mixed-sex) | only by loosening protocol |
| semaglutide-obesity-mace | SELECT | 0 | no |
| tranexamic-acid-pph | WOMAN | 3 (prophylaxis trials, scope-excluded) | only by changing PICO to prophylaxis |

## What I could not check, and why

1. **`QUARANTINE_DECISIONS.md` cross-check** — file does not exist anywhere searched; criterion 4a could not execute and reports no pass. If it lives in another repo, point me at it.
2. **"The NCT detector"** — no such component in this repo. Substitute: live CT.gov existence (595/595) + own-record attribution for pooled trials (74/74), both planted. Existence + attribution is not proof the NCT's *results* were the source of the number.
3. **Exact comparator trial-set overlap** — machine-unverifiable on 32/32 (comparator tables not exposed; per-trial effects are in figures on 14/21, full text not obtained on 6/21 despite OA flags). All "external-identical/-subset/-distinct" verdicts are INFERRED from page text.
4. **Per-trial numbers against the papers** — not done here; that is the review. I verified only that the served numbers regenerate from the committed inputs and that an independent estimator reproduces them from raw inputs.
5. **Retraction/concern status** — CLAIMED from the harness's PubMed check on 2026-09-13; not re-run.
6. **The brief's own counts** (368/291/55/122/135) — not reproducible on this site; see the first table.
7. **RapidMeta** — the corpus the brief's counts describe. Not examined here (different repo, ~1,100 pages, no `reproduce_review.py`). Needs its own reproduction instrument named before criterion 3 can be executed there.

## Fresh-clone result

`python scripts/reproduce_review.py --fresh-clone` at HEAD `aa8ed28a`: 32 of 32 `OK`, final line `REPRODUCIBLE`, exit 0 (MEASURED; log in scratchpad `reproduce_freshclone.log`). Combined with served == committed (128/128 files), the chain served page ⇐ committed page ⇐ fresh-clone rebuild holds for all 32 pages. Caveat repeated from the README: this is re-derivability from the *committed cache*, not from the protocol commit alone (no topic has a protocol-only registration commit; every page says so).

## What is NOT in this file — the RapidMeta selection

The brief's population (368 links / 291 apparatus-only / 55 object-backed / 122 donor / 135 fabricated NCTs / `QUARANTINE_DECISIONS.md` / `self_reference`) is RapidMeta's. Running the same selection there needs three decisions from you first: (1) which served URL is authoritative (the repo is `rapidmeta-finerenone`; several worktrees are on different commits — `rm-enum-lane` at `ed02ec53` 2026-09-04, `rapidmeta-main-fix` at `424e8aa0d` 2026-08-27); (2) what stands in for `reproduce_review.py` as the definition of done — RapidMeta has no such script, so "regenerates the served page from the protocol SHA" has no executable form there yet; (3) whether the 55 object-backed pages are the candidate set or whether the 291 MARKED pages should be re-examined.

## Method notes

- Instruments: `curl`/`urllib` fetch of served bytes → sha256 vs HEAD and vs served manifest; `scripts/reproduce_review.py` (replay, then `--fresh-clone`); own Python PM+HKSJ recompute from raw `ai/ci/n1i/n2i`, `effect/ci_low/ci_high`, or `mean/sd/n` (never from the harness's `study_effect`); CT.gov v2 `GET /api/v2/studies/{nct}`; cache record grep for attribution. Scratch outputs: `F:\claude-temp\claude\C--meta-harness\...\scratchpad\{served_check.json, recompute.json, nct_probe.json, reproduce_all.log, reproduce_freshclone.log}`.
- Ordering rationale: k, presence of heterogeneity (so the RE machinery is actually exercised), 2×2 inputs (fully recomputable), independence of the search (hand-written keyword first), and a benchmark with a distinct trial set — pages where agreement with the comparator is arithmetic (identical sets) rank lower because there is less to disagree with.
