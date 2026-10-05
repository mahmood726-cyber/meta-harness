# Dispatch from g1/forest-reader to acq/k-gap

## 4 Oct: the seven RESULT_AGREES priority topics

The k-gap lane asked for comparator per-trial rows (dual-model, recorded, pooled-reconstruction gate) for seven
topics. Each was checked against acq/k-gap `016928fc`.

Outcome: no new figure can be read legitimately for any of the seven.

- Two already have accepted comparator rows, and both reproduce the printed pool. For one of them (esketamine), the
  tracker has no comparator pooled result.
- One is already G1_MATCHED.
- Four have no readable per-trial figure for the topic outcome.

### Already supplied (rows at `521ed499`; G1-R REPRODUCED)

**esketamine-trd-madrs** (PMID 42490943)
- **Figure:** f4, "Acute induction: MADRS change from baseline to day 28 (random-effects)".
- **Rows:** 4, labelled Trial A, B, C and "D (older adults)".
- **Pooled:** MD −2.99 (−5.10 to −0.89). This is printed in the comparator's own text (its summary table: 937
  participants, 4 RCTs). The figure's rows reproduce it under DL.
- **For you:** the tracker's `comparator` block is empty (estimate null). Use this pool as the compared result.
- **Uncovered trials:** Trial E and Trial F are not in f4, which lists Trials A–D only. f4 is the comparator's only
  per-trial MADRS day-28 plot; its supplement figure 5 is an age-subgroup pool. Trial D is in the rows under the label
  "Trial D (older adults)", so it is a join miss.

**iv-iron-hfref-hosp** (PMID 39727669)
- **Figure:** diseases-12-00339-f003, total HF hospitalizations.
- **Rows:** 5.
- **Pooled:** OR 0.59 (0.40–0.88), also printed in the comparator's text. It reproduces under DL and equals the served
  `comparator.reported`.
- **For you:** RESULT_AGREES fails on OUR side, where "ours" is INCOMPATIBLE (first-event HR + incidence-rate ratio).
  It is not a missing comparator row.

### Already matched

**noac-vs-warfarin-af-stroke** (PMID 34985309, COMBINE AF)
- **Status:** G1_MATCHED; RESULT_AGREES is already true.
- **Why no rows:** its only forest figure (F1) has outcome rows from a one-stage individual-patient model. It has no
  trial rows to read. It was read, and refused as NOT_RECONSTRUCTABLE.
- **Supplement:** NIHMS1764416-supplement is absent from the PMC OA bucket.

### Not readable from a legitimate open source (probe records under `cache/comparators/<pmid>/`)

| topic | PMID | every open location tried | result |
|---|---|---|---|
| doac-vte-recurrence | 24963045 | ASH publisher PDF (Unpaywall, OpenAlex); CORE holds only a Swepub metadata record | publisher Cloudflare challenge; CORE has no file |
| corticosteroids-cap-mortality | 38128217 | Elsevier landing (cc-by-nc); Cardiff ORCA PDF; CORE download 595560423 | landing is HTML only; ORCA and CORE are Cloudflare challenges; the CORE API has no full text |
| colchicine-recurrent-pericarditis | 22442198 | BMJ Heart PDF; Milan AIR repository; CORE download 195773452 | all Cloudflare challenges; the CORE API has no full text |

A challenge is recorded, never solved. Rows come only if Mahmood (or someone with legitimate access) places a copy
of these papers in the cache, for example by downloading them himself from the open publisher pages.

### No per-trial topic-outcome figure exists

**dpp4-mace-t2d** (PMID 34754403)
- The comparator has one forest figure (F1). Its panels A–F are MI, stroke, HF hospitalisation, unstable angina,
  revascularisation and CV mortality.
- It has no tables and no supplement.
- Its text never reports a pooled 3-point MACE.
- So there is no MACE row to read. RESULT_AGREES cannot be met against this comparator for a MACE estimand. The
  served MACE comparator value, if any, should be checked against the paper; MACE appears only in its background.

### Join misses (rows exist in accepted comparator figures, but your tracker leaves the trial uncovered)

| topic | your trial label | accepted row label |
|---|---|---|
| probiotics | Lönnermark | Lnnermark 2010 |
| colchicine-secondary | Akrami, Mewton | Mehdi Akrami–2012, Mewton N-2019 |
| corticosteroids-covid19 | hydrocortisone 21-day mortality trial | CAPE COVID |
| dapagliflozin-hfpef | SOLOIST-WHF, SCORED, EMPEROR-Preserved | combined SOLOIST-WHF/SCORED row; EMPEROR-P |
| empagliflozin-hfpef | EMPEROR-Preserved (your labels are titles) | EMPEROR Preserved 2021 |
| esketamine | Trial D | Trial D (older adults) |
| sglt2-hfref | EMPEROR-Reduced, SOLOIST-WHF | EMPEROR-Reduced †, SOLOIST-WHF ‡ |
| sglt2-primary-prevention | Zinman | Zinman 2016 |
| statins | Alpérovitch | Alperovitch et al 2015 |

### Rows you have not merged yet

`521ed499` adds two more comparator figures:

| figure | rows | pooled reproduces |
|---|---|---|
| colchicine-secondary F11 | Akodad 2017, Shah 2020 | 0.90 (0.54–1.51), MH |
| spironolactone F2 panel D | TOPCAT (+ 3 finerenone trials) | 0.91 (0.85–0.99), FE |

Both appear in `meta_results` with role `comparator` and key `<slug>::<pmid>::<fig>`. `accepted_rows(slug)` returns
them with `meta_pmid` set to the comparator's PMID.

## 4 Oct (night): SECONDARY_SINGLE supply for six topics

These are non-comparator metas covering the tracker's UNVERIFIED / NO_ROW trials.

**How they were selected.** `scripts/g1_ss_targets.py` read the targets at acq/k-gap `f34580f9`. It then searched
Europe PMC for open-access, in-EPMC meta-analyses:
- for a target with a PMID, metas whose reference list cites it (`CITES:<pmid>_MED`);
- for a target with only an NCT number, metas whose full text contains it.

Every query is recorded in `registry/model_proposals/g1_ss_search/<slug>.json`. Candidates are ranked by how many
targets they cite (`g1_ss_selection.json`).

**How they were read.** The figure is the one whose caption names the topic outcome, caption-checked in `TARGETS`.
Both readers also got the topic-outcome note. Two recorded readings were taken for each figure, followed by the
pooled-reconstruction gate. The comparator is never used.

### Accepted (rows in `meta_results`; `accepted_rows(slug)` returns them)

| figure | rows | gate |
|---|---|---|
| omega3 29387889 hoi170076f2 (major vascular events, by trial) | 10 | FE 0.967 (0.929–1.007) reproduces 0.97 (0.93–1.01) |
| pcsk9 39259104 F7 (MACE) | 12 | MH-FE reproduces 0.87 (0.83–0.91) |
| ticagrelor 30013323 f7 (MACE at 180 days) | 5 | FE reproduces 0.27 (0.15–0.46) |
| ticagrelor 30412125 F2 (primary efficacy) | 5 | MH-RE reproduces 0.64 (0.41–1.01) |

- **omega3 29387889:** the 10 rows are DOIT, AREDS-2, SU.FOL.OM3, JELIS, Alpha Omega, OMEGA, R&P, GISSI-HF, ORIGIN and
  GISSI-P, which covers about 8 of omega3's targets by acronym.
  - **Caution:** these trial rows print **99% CIs**. The caption and methods say so, and the totals are 95%. Each row
    carries `ci_level: "99%"` and a finding `ROW_CI_IS_99_PERCENT`.
  - `SecondaryRow` has no interval-level field, so derive no SE from these rows as if they were 95%.
- **pcsk9 39259104:** its rows are labelled by surname, so the join to the ODYSSEY targets is for you to judge.
- **ticagrelor:** the five Chinese trials in 30013323 and Bonello/Park/Tang/Vercellino/Xia in 30412125 may not be the
  numbered targets. Their join is yours.

### Refused, with the reason

| figure | agreed rows | why refused |
|---|---|---|
| tocilizumab 35802687 g003 | 14 | the figure prints **no pooled row** (see below) |
| tocilizumab 35038318 f1 panel A | 9 | 1 row disagrees, so the whole figure is refused |
| tocilizumab 34768455 f002 | 8 | 1 row disagrees, and the pool is not reproduced |
| omega3 39076869 S3.F2 panel A | 12 | 1 row disagrees (DL reproduces on the agreed rows) |
| omega3 42144851 | 11 log-ORs | DL 0.015 (−0.131 to 0.162) vs printed 0.04 (−0.06 to 0.14) |
| pcsk9 41235335 F4 panel A | — | 7 rows disagree, and the counts do not give 3 printed rows |
| ticagrelor 42524293 F2 panel b | — | the readers disagree on the pooled row |
| metformin 28630466 Fig4 panel c | — | the readers disagree on the rows and the pool |

**tocilizumab 35802687, for the captain and Mahmood.** Both readers agree on all 14 tocilizumab-vs-usual-care trial
rows: ARCHITECTS, CORIMUNO-TOCI-ICU, COV-AID, COVACTA, COVIDOSE2-SS-A, COVIDSTORM, EMPACTA, HMO-020-0224, ImmCoVA,
PreToVid, RECOVERY, REMAP-CAP (a), REMDACTA and TOCIBRAS. These are the NO_NON_COMPARATOR_META_ROW trials. But the
figure is a network meta-analysis's direct-evidence plot: it prints per-trial ORs and % weights, and **no pooled
row**. The paper's text prints no pairwise pool either. So the reconstruction gate cannot run, and the rows are NOT
accepted.
- **A possible decision:** let the printed % weights serve as the gate (inverse-variance weights recomputed from the
  rows must reproduce them).
- That is a rule change, so it is not taken here.

### No source found

| topic | why |
|---|---|
| probiotics-aad | every open meta of antibiotic-associated diarrhoea that cites the targets is already read. The higher-coverage metas plot *C. difficile* diarrhoea, a different outcome. |
| metformin-pcos | the high-coverage metas plot other outcomes (endometrium, metabolic markers) or are network metas. |
| pcsk9 | the high-coverage metas are network meta-analyses, or plot dementia, neurocognitive outcomes or LDL. |

### Second sweep, same night (all ranked candidates, not just the top 15)

| figure | outcome |
|---|---|
| ticagrelor 31000178 fig2 panel A | read; the readers agreed and the pool reproduced. Then **refused** on what it is: a meta of observational studies (its abstract), so it has no trial rows. Same precedent as the CAPA plot. |
| tocilizumab 34026583 F2 | refused: 5 rows disagree. Its rows are observational cohorts anyway. |
| tocilizumab 39633779 fig4 (immunomodulators) | refused: 1 of 17 rows disagrees. |

**Study design of the accepted figures.** Of the four accepted SECONDARY_SINGLE figures, only omega3 29387889 is
all-RCT. The other three mix designs:
- pcsk9 39259104: RCTs, retrospective studies and prospective studies;
- ticagrelor 30013323: 14 RCTs and 1 observational study;
- ticagrelor 30412125: the abstract does not say.

Use only the rows that your identity check joins to a comparator RCT.

**Arm-level source for tocilizumab's NCT-only trials.** BMJ Medicine 2022 (PMID 36936570) supplement 1 prints
arm-level death counts by steroid stratum for COVIDOSE2, HMO-020-0224, COVITOZ, ImmCoVA, PreToVid, COVIDSTORM and
others. It is open through Europe PMC `/PMC9978750/supplementaryFiles`.
- Its only pooled values are Bayesian network-meta-analysis direct estimates, given as credible intervals.
- None of our gate's methods (FE / DL / PM / REML / MH) is expected to reproduce those, so it was **not read**.
- If a rule allowing arm counts without a pooled anchor is ever adopted, this is the source.

### Third sweep, 5 Oct: wide search (systematic reviews and PUB_TYPE meta-analyses, any title)

**Search.** `g1_ss_targets.py --wide` records its own queries and keeps a separate frozen selection
(`g1_ss_selection_wide.json`, up to 15 unread candidates per topic). Every candidate's figure captions were scanned
for a per-trial plot of the topic outcome. Read:

| figure | result |
|---|---|
| ticagrelor 40051435 F3 panel b (MACE, ACS with CKD) | **ACCEPTED**: 5 rows (Chien-Ho 2019, Ji 2021, Stefan 2010, Yun 2022, Yun-S 2022); FE reproduces 0.89 (0.80–0.99). The meta mixes cohort studies and RCTs. |
| ticagrelor 38371311 f0015, ticagrelor subgroup 3.1.3 | refused: 11 of 12 rows agree, but 1 disagrees. The 11 agreed rows are ALPHEUS, ESTATE, Li et al., PHILO, PLATO, POPular AGE, TAILOR-PCI, TALOS-AMI, TICAKOREA, Turgeon 2020 and Yun et al. MH-FE on them reproduces the subtotal 0.96 (0.91–1.01). |
| probiotics 30078376 Fig3 (AAD by composition) | refused: the readers split on whether the multi-study rows are studies. |

**Not read** (each checked):
- omega3 37031750 fig3 is an outcome summary, not trials.
- ticagrelor 40489021 is prasugrel.
- pcsk9: none of the 15 wide candidates has a per-trial MACE plot (they are pooled ODYSSEY analyses, network meta-analyses and LDL figures).
- metformin and tocilizumab: no per-trial topic-outcome plot among the wide candidates.

### Fourth sweep, 5 Oct: candidates' open supplements

**Scan.** Supplement bundles of the top candidates per topic were taken from Europe PMC `supplementaryFiles`. Their
PDF and Word text was searched for forest-plot captions naming the topic outcome.

**Read: omega3 37031750, Supplemental Figure 3 (3-point MACE by trial). ACCEPTED.**
- **Where:** an image embedded in the meta's own Word supplement `mmc1.docx`. The file is listed in its JATS and held
  in the PMC OA bucket; the image was extracted unchanged.
- **Rows:** 10 with counts — GISSI-Prevenzione, OMEGA, SU.FOL.OM3, ORIGIN, Risk & Prevention, COS, VITAL, STRENGTH,
  JELIS and REDUCE-IT.
- **Gate:** DL 0.964 (0.889–1.044) reproduces 0.96 (0.89–1.04), and so do PM and REML.
- **Value:** a second independent meta, beside 29387889, for GISSI-P, OMEGA (Rauch), ORIGIN, R&P and JELIS
  (Yokoyama).

**Not read:**
- omega3 29387889 eFigure 3: the same trials without JELIS.
- tocilizumab 33915284 / 33161150: sensitivity plots of adjusted (observational) estimates.
- tocilizumab 34019122: an ICU subgroup.
- tocilizumab 39633779: drug-class plots.
- No pcsk9, metformin, ticagrelor or probiotics supplement had a per-trial topic-outcome plot.

**SECONDARY_SINGLE running total:** 19 figures read, 6 ACCEPTED (47 rows).

### Single-number disagreements: refusals stand (5 Oct)

**The trial.** Five refused figures fail on exactly one disputed value. I tried a deterministic rule: take the
candidate value that makes the row's own printed numbers consistent. It was **reverted**.
- The rule contradicts the goal's requirement that "a row is PROPOSED only if both readings agree within printed
  rounding".
- The planted test `test_REAL_FIGURE_PLANT_one_perturbed_reading_refuses` (RALES upper 0.82 perturbed to 0.84) went
  from REFUSED to ACCEPTED under it. That test defends the requirement, so the rule went, not the test.

**For information only.** None of these rows is accepted:

| figure | disputed row | readings | which value the row's own numbers support |
|---|---|---|---|
| tocilizumab 35038318 | NCT04320615 | 28 vs 29 control deaths | 28 (58/294 vs 28/144 gives the printed RR 1.01) |
| tocilizumab 39633779 | Lescure (sarilumab 400 mg) | upper 2.32 vs "232" | 2.32 (a dropped decimal) |
| tocilizumab 34768455 | REMAP-CAP | lower 0.49 vs 0.48 | 0.48 (87/353 vs 134/402 gives 0.476) |
| omega3 39076869 | Einvik 2010 | upper 1.45 vs 1.44 | both consistent: undecidable |
| ticagrelor 38371311 | KAMIR-NIH | label "2016" vs "2018", all values equal | the reference list does not resolve it |

If Mahmood wants these resolved, the rule needs his decision.

### 5 Oct: exhaustive candidate scan, and melatonin

**Melatonin targets.** 18, read from acq/k-gap `8cd651a4`. Every candidate of every recorded search, strict and
wide, for all seven topics was caption-scanned.

**pcsk9 39126262 F0001, PCSK9-inhibitor group. ACCEPTED.**
- **Rows:** 4 — Schwartz 2018 (ODYSSEY OUTCOMES), Koskinas 2019, Räber 2022 and Yan 2022.
- **Gate:** DL reproduces 0.88 (0.80–0.95).

**melatonin 36079069 f002, sleep latency block. ACCEPTED on the second recorded pair.**
- **Rows:** 14. DL 0.739 (0.149–1.328) reproduces 0.74 (0.15–1.33).
- **Why a second pair:** the first pair split only on bound order. The figure's column headed "Upper limit" holds the
  smaller numbers, and the clarification given to both readers names no value.
- **Caution:**
  - The rows are DOSE ARMS, so one study can have several rows (e.g. "Haimov 1995; 1.0 mg").
  - Rows marked * (Roth 2007, PennTakeda 2006, Jha 2016 8.0 mg*) are RAMELTEON, not melatonin.
  - The metric is a standardised difference in means.
  - Match only the melatonin arms to your trials. Almeida Montes appears as "Almeda 2003"; Haimov and Zhdanova are
    targets.

**Melatonin, other candidates (not read):**
- 36387478 (REM sleep behaviour disorder) supplementary figure 3: its sleep-latency data are baseline-versus-after
  within-group comparisons, not melatonin versus placebo.
- 32580450: a network meta-analysis whose sleep-latency figure was refused for subgroup rows.
- 37457117: plots quality of sleep and daytime functioning only.
- No other open candidate has a per-trial sleep-onset-latency plot.

**Lane state.** Every recorded candidate for pcsk9, ticagrelor, metformin, omega3, probiotics, tocilizumab and
melatonin has been checked. Further rows here need one of the two rule decisions above:
- tocilizumab 35802687 checked against its printed % weights;
- single-number disagreements settled by a row's own printed numbers.

## 5 Oct: typed rule POOL_UNCHECKABLE (decision under Mahmood's delegation) — applied

**The rule.** A meta whose pooled reconstruction cannot be checked never counts as SECONDARY_SINGLE on its own. Its
rows may serve only as the SECOND source in TWO_SOURCE, agreeing with an independent primary or with another meta
that passed the gate.

### Where it lives

`harness/secondary_meta.py`:
- `POOL_UNCHECKABLE = "META_POOL_UNCHECKABLE"` is a typed finding carried in `SecondaryRow.findings`, so it survives
  every hand-off. `pool_uncheckable(row)` tests for it.
- `secondary_single`: such a row stays queued, with `SECONDARY_SINGLE_REFUSED:POOL_UNCHECKABLE`.
- `two_source`: a pair in which BOTH metas are uncheckable is not independent support (`BOTH_POOLS_UNCHECKABLE`). An
  uncheckable meta paired with a gated meta does make TWO_SOURCE. A trial with an independent primary is already
  PRIMARY; the row adds nothing there.

`scripts/g1_forest_reader.py`:
- **Typing:** `NO_POOLED_ROW_PRINTED` means both readers report no pooled row, and is typed separately from
  `POOLED_ROW_DISAGREES`.
- **New state `ACCEPTED_SECOND_SOURCE_ONLY`.** It is given only when every row agreed, the rows are trials, every row
  is internally consistent, and the rows are ONE analysis (no repeated trial label). Each row carries the finding.
- **Hand-over:** `accepted_rows()` returns these rows WITH the finding.
- **Hook:** `secondary_meta_build` records `positive_control.reproduced = False (META_POOL_UNCHECKABLE)` for such a
  meta. This is a second guard, beside the finding.

### Plants (each failed before the change)

- `test_a_meta_whose_pool_cannot_be_checked_is_only_ever_a_second_source`, harness-level:
  - two uncheckable metas: no TWO_SOURCE;
  - uncheckable + gated: TWO_SOURCE;
  - uncheckable alone: never SECONDARY_SINGLE.
- `test_rows_agreed_but_no_printed_pool_are_marked_second_source_only_never_accepted`, on the real recorded
  35802687 readings: 14 rows, all marked. A figure that repeats trial labels stays REFUSED, and so does one whose
  readers disagree on the pool.

### Applied

**tocilizumab 35802687** went REFUSED → `ACCEPTED_SECOND_SOURCE_ONLY`. Its 14 rows (ARCHITECTS, CORIMUNO-TOCI-ICU,
COV-AID, COVACTA, COVIDOSE2-SS-A, COVIDSTORM, EMPACTA, HMO-020-0224, ImmCoVA, PreToVid, RECOVERY, REMAP-CAP (a),
REMDACTA, TOCIBRAS) now reach you marked. They count only if an independent gated meta, or a primary, agrees.

**Refused, with a typed reason:** glp1 30223891 and sacubitril 34617669 also print no pooled row. But they are
one-block-per-outcome figures that repeat trial labels, so they get `ROWS_NOT_ONE_ANALYSIS:REPEATED_TRIAL_LABELS`.
Nothing else changed.

**Disk:** C: has about 310 MB free. See `lane_status/disk.md`. Put TMP/TEMP and pytest `--basetemp` on F: until that
file says FIXED.
