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

## 5 Oct: two more typed rules (decisions under Mahmood's delegation) — applied

### RULE WEIGHTS: printed % weights are a valid but WEAKER gate

**Rule.** It applies to a figure that prints no pooled row. Rows that pass may count only as the SECOND source in
TWO_SOURCE, never alone, as with POOL_UNCHECKABLE.

**How the check works** (`weights_gate` in the reader):
- The two readings' printed weights must agree within printed rounding (otherwise `WEIGHTS_DISAGREE`).
- Every printed weight must lie inside the range the rows allow. The range comes from inverse-variance weights built
  from each row's CI, with each bound moved within its printed half-unit, plus the printed weight's own half-unit.
- The check passes under FE or DL (`WEIGHTS_REPRODUCED:<model>`); otherwise the figure is refused
  (`WEIGHTS_NOT_REPRODUCED`).

**Which figures it covers.** A no-pool figure that prints weights must pass it. One that prints no weights keeps the
earlier POOL_UNCHECKABLE treatment.

**Applied.** tocilizumab 35802687 passes under FE: 14 rows, still `ACCEPTED_SECOND_SOURCE_ONLY`. Each row now carries
the finding `META_POOL_UNCHECKABLE: ... printed % weights are reproduced (WEIGHTS_REPRODUCED:FE) -- a weaker gate,
so second source only`.

### RULE SINGLE_NUMBER: a single-number reader disagreement is settled by the row's own numbers

**Rule.** It applies when the two readings differ in exactly ONE number of a row, and the label and every other value
agree. A candidate is taken only if EXACTLY ONE of the two reproduces the row's own printed effect and CI within
printed rounding:
- with counts: the counts must give the printed effect and CI;
- without counts: the CI must be centred on the printed effect.

The settled row records `value_basis: SINGLE_NUMBER_RESOLVED_BY_ROW ...`. If both candidates fit, or neither, or one
reader printed nothing, the row is `READER_DISAGREEMENT_UNRESOLVED:<FIELD>`. A blank is not a second reading.

**Applied.** 9 rows were settled across all recorded figures, and 5 figures moved from REFUSED to ACCEPTED (58 rows):

| figure | rows | settled row |
|---|---|---|
| tocilizumab 35038318 | 10 | NCT04320615: control deaths 28 vs 29; only 28 gives the printed RR 1.01 |
| tocilizumab 39633779 | 17 | Lescure: upper 2.32 vs "232" |
| tocilizumab 34768455 | 9 | REMAP-CAP: lower 0.49 vs 0.48; only 0.48 fits, and the pool then reproduces |
| colchicine-secondary 37608812 | 4 | Hennessy 2019: control events 1 vs 2 |
| spironolactone 26891235 | 18 | Montalescot 2014: n_c 305 vs 306 |

The 4 other settled rows sit in figures still refused for other reasons. 17 rows remain READER_DISAGREEMENT_UNRESOLVED;
the Einvik 1.45 / 1.44 case is one of them, since both values fit.

### Tests

**New plants**, each failing before its change:
- `test_rule_single_number_*`: a count settled; a dropped decimal settled; both fitting = UNRESOLVED; an omission =
  UNRESOLVED;
- `test_rule_weights_*`: the real 35802687 readings give WEIGHTS_REPRODUCED; RECOVERY's weight set to 40.00 in both
  readings gives REFUSED, WEIGHTS_NOT_REPRODUCED.

**Rewritten to the new requirement.** Two older plants asserted "any single disagreement refuses". They now assert that
the perturbed number is never proposed, and that the printed value is recovered with its recorded basis:
- `test_PLANT_one_perturbed_reading_never_yields_the_perturbed_number`;
- `test_REAL_FIGURE_PLANT_one_perturbed_reading_never_yields_the_perturbed_number`.

REPLAY_OK; 98 passed, with basetemp on F:.

## 5 Oct: metformin and probiotics — the blocker is identification, not missing meta rows

**The new search.** `g1_ss_targets.py --topic` adds a topic-words search. It finds open-access meta-analyses by topic
query, holds their JATS, and checks whether their own reference lists contain a target's PMID. It is recorded and
frozen in `g1_ss_selection_topic.json`, with the queries in `g1_ss_search/`.
- **metformin:** 156 hits. The high-coverage ones are network meta-analyses already read and refused (28143834,
  34280195, 28630466). Every other hit cites at most 1 target and has no per-trial ovulation plot.
- **probiotics:** 122 hits. The high-coverage ones are already read. 41821810, 23981066 and 26596269 have no forest
  plot at all; 26955289 and 27025619 plot *C. difficile*, a different outcome.

**The finding that matters.** At acq/k-gap `f7d4278e`, every UNVERIFIED / NO_ROW target in six of the seven
SECONDARY_SINGLE topics is `NOT_IN_OUR_POOL`:
- metformin 38/38;
- probiotics 26/26;
- pcsk9 10/10;
- omega3 24/24;
- ticagrelor 20/20;
- melatonin 18/18.

A meta's row supplies the VALUE for a trial already in our pool. For a trial our search/screen never admitted, no
number of meta rows changes G1. probiotics Can, Cindoruk, Gao and Sampalis are already in accepted meta rows
(24348885, 29023420) and still read `NOT_IN_OUR_POOL`.

Only tocilizumab's targets are in our pool (`NO_PRIMARY_ROW` ×12, `AGREE` ×2). That is why the two new rules moved
tocilizumab.

**Where those trials stop, from your tracker:**

| topic | identification at screen | unresolved identity | screen / eligibility | acquisition / extraction | other |
|---|---|---|---|---|---|
| metformin | 17 | 13 | 4 | 1 | 3 (2 genuinely unavailable open, 1 scope mismatch) |
| probiotics | 0 | 5 | 9 | 9 | 3 (2 genuinely unavailable open, 1 measure mismatch) |

**The lever is upstream, in your lane:** identity resolution, screen and acquisition. Until those trials enter our
pool, my meta reads cannot count for them. I have stopped spending codex calls on metformin/probiotics metas for
that reason.

## 5 Oct: every accepted row mapped to a trial identity, ready for REVIEW_REFERENCE_LIST admission

**The file.** `registry/model_proposals/g1_forest_row_identity.json`, produced by `scripts/g1_row_identity.py` and
pinned to acq/k-gap `f7d4278e`. It is deterministic, offline and uses no model. It holds one record per accepted row:
`pmid`, `doi`, `nct`, `comparator_label`, `tracker_family`, `in_our_pool`, `route_now`, `methods`, `reference` (the
cited text), and `why` when the row is unmapped.

**Methods, strongest first:**
- `META_REFERENCE_NUMBER` — the citation number in the label, taken only if its first author is in the label too;
- `META_REFERENCE_SURNAME_YEAR` — the row's surname and year, unique in its own meta's JATS reference list;
- `META_REFERENCE_TITLE_ACRONYM` — the whole acronym, at least 4 characters, in a reference title;
- `NCT_IN_LABEL`;
- tracker attachment:
  - `TRACKER_ID` — same family PMID or NCT;
  - `TRACKER_NAME_EXACT` — same compact name, e.g. "CONFIRM HF" = "CONFIRM-HF [2]";
  - `TRACKER_ACRONYM`;
  - `TRACKER_SURNAME_YEAR` — a name ONLY with a year on both sides;
- `TABLE_NCT` — the single NCT your trial table holds for that PMID.

Ambiguity is recorded (`AMBIGUOUS_REFERENCE:n`, `AMBIGUOUS_ACRONYM_IN_TITLES:n`, `TRACKER_AMBIGUOUS`) and never
guessed. A PMID found through a meta's reference is the report that meta CITES, which may be a secondary analysis.
`reference` keeps that visible.

**Coverage, rows (1,008 accepted rows):**

| measure | rows |
|---|---|
| mapped to at least one id | 535 |
| with a PMID | 408 |
| with an NCT | 229 |
| attached to a comparator trial in your tracker | 393 |

**Coverage, target trials** (your UNVERIFIED / NO_ROW comparator trials, 255 across 22 topics):

| measure | trials |
|---|---|
| with at least one accepted row mapped | 144 |
| with a row from a NON-comparator meta that passed the gate | **56** |

The 56 are the ones that count under the new route (data from non-comparator sources only).

**Per topic, non-comparator gated / targets:**

| topic | rows | topic | rows |
|---|---|---|---|
| colchicine-secondary | 9/13 | omega3 | 7/24 |
| tocilizumab | 6/14 (+ second-source-only rows) | colchicine-postop-af | 5/6 |
| dapagliflozin-hfpef | 5/6 | probiotics | 5/26 |
| balanced-crystalloids | 3/6 | iv-iron | 3/4 |
| spironolactone | 3/5 | melatonin | 2/18 |
| corticosteroids-covid19 | 2/3 | glp1 | 1/1 |
| esketamine | 1/3 | sacubitril | 1/8 |
| sglt2-ckd | 1/9 | sglt2-primary | 1/3 |
| ticagrelor | 1/20 | metformin | 0/38 |
| pcsk9 | 0/10 | statins | 0/27 |
| semaglutide-mace | 0/9 | sglt2-hfref | 0/2 |

metformin, pcsk9 and statins have rows mapped only from their COMPARATORS (16, 10 and 8 trials), which the new route
excludes.

**How to attach on admission.** When REVIEW_REFERENCE_LIST admits a trial, join this file on `pmid` or `nct` (or on
`comparator_label` for your tracker's label). The rows then reach the secondary tier with their findings intact,
including POOL_UNCHECKABLE, the 99% interval level and resolved-value bases.

## 5 Oct: admission-first — counted only by the tracker's own gate

**The check.** `scripts/g1_admission_check.py` builds every accepted row EXACTLY as the secondary-tier dual hook does,
then runs the tracker's own gates with the topic's registered spec and the build's family resolver:
`sm.admit` (measure, outcome, timepoint, family), then `sm.consolidate`. Nothing is loosened. Results are in
`registry/model_proposals/g1_forest_admission.json`.

Caveat: `our_trials` runs here without the untracked local AACT store, so family resolution can only be weaker than
yours. My counts are a lower bound.

**The pre-filter.** It runs before any read and spends reads only on figures whose own words pass the
measure / outcome / timepoint gates (`g1_admission_check.prefilter`). New reads:

| figure | reader result | admitted |
|---|---|---|
| tocilizumab 34050796 Fig3 panel A (mortality, counts) | ACCEPTED (MH-RE) | 5 of 9 |
| tocilizumab 34768455 f004 (28-day mortality, counts; its f002 was refused TIMEPOINT_30_NE_28) | ACCEPTED (FE) | 5 of 9 |
| omega3 39238993 F1 (icosapent ethyl, primary composite, counts) | ACCEPTED (MH-RE) | 2 of 3 |

The remaining refusals are all FAMILY_NOT_RESOLVED (trials not in our pool).

**Admitted-by-tracker, NON-comparator rows (the new route's source):**

| topic | admitted | of N |
|---|---|---|
| tocilizumab | 19 | 149 |
| omega3 | 11 | 53 |
| probiotics | 4 | 64 |
| ticagrelor | 0 | 68 |
| pcsk9 | 0 | 16 |
| metformin | 0 | 17 |

These counts include comparator rows: none. Admitted means the rows reach verification. TWO_SOURCE or SECONDARY_SINGLE
is still yours to decide downstream.

**Why the zeros stay zero under unchanged gates:**
- **ticagrelor and pcsk9** — estimand HR:
  - The pre-filter over every recorded candidate (43 and 96 metas) finds NO per-trial MACE plot printing hazard ratios
    with a stated timepoint. The open metas print RR/OR from counts, which cannot become HR.
  - ticagrelor's protocol timepoint ("12 months or longest") together with core `death` makes timepoint_identity read
    only a mortality-style statement ("N-day mortality"). No MACE meta states one.
- **metformin:** every candidate that passes the outcome words is a different intervention (acupuncture, vitamin D,
  herbal formulas, L-carnitine, letrozole). No open meta plots metformin + clomifene vs clomifene ovulation per trial,
  except the comparator itself.
- **probiotics:** no unread candidate passes. The admitted 4 come from 29023420.

## 5 Oct: pushing admitted rows through to the tracker (merged acq/k-gap 7d0d3fcc, which contains fe689f08)

### A gap in the merged build: forest-lane rows lost their timepoint

**What happened.** `forest_lane_metas` builds lane rows WITHOUT the timepoint inference that every figure row of the
build gets (`meta_timepoint` of the caption, else of the meta's text for a core-mortality topic). As a result, all 135
tocilizumab lane rows read `TIMEPOINT_NOT_STATED_BY_META`, including the 28-day figures.

**The fix.** `secondary_meta_build.lane_timepoint(r, spec)` runs before `sm.admit` on each lane row. It uses the same
derivation as the build applies to its own figure rows. The timepoint gate itself is unchanged: a 30-day figure still
reads `TIMEPOINT_30 days_NE_28 days`.

**Plant:** `test_a_forest_lane_row_gets_the_timepoint_its_caption_states_like_every_figure_row` (fails before).

### Recount in this clone (tracker's own build + g1_tracker; lower bound)

The environment has no AACT store and no topic-lane import, so tocilizumab's pool here is 7 trials. The committed
tracker lists REACT's 19.

**tocilizumab:**

| | admitted lane rows | TWO_SOURCE_VERIFIED rows | matched trials (k_matched) |
|---|---|---|---|
| before the fix | 0 | 0 | 1 |
| after the fix | 19 (34768455 ×7, 35343397 ×7, 34050796 ×5) | 14 | 5 |

**Trials that flip to TWO_SOURCE (5):**
- CORIMUNO-TOCI (PMID 33080017): was NO_ROW;
- TOCIBRAS (33472855): was UNVERIFIED;
- COVINTOC (33676589): was UNVERIFIED;
- COVACTA (33631066): was UNVERIFIED;
- EMPACTA (33332779): was UNVERIFIED.

Each is supported by 2–3 independent non-comparator metas (34050796, 34768455, 35343397). BACC Bay stays BLOCKED
(two metas disagree).

**omega3:** k_matched 4 → 5. GISSI-P and Nilsen became SWEEP_SECONDARY_SINGLE through your sweep, not through my rows.
My 37031750 is a cross-check dissenter on GISSI-P.

**Please regenerate tocilizumab with the lane-import inputs** to get the authoritative recount on REACT's 19 trials.

## 2026-10-05 — flip_plan #4 / #6 / #10 (forest-reader, commit after be4a2e78)

1. **Build outputs had silently reverted (fixed).** At HEAD, `registry/secondary_meta/tocilizumab-covid19-mortality.json` was still fe689f08's version, built before `lane_timepoint`, so every forest-lane row read `TIMEPOINT_NOT_STATED_BY_META` and the tracker counted **1 of 7**. Rebuilt from the recorded ledger (replay, no new calls) and committed: tocilizumab is **5 of 7** (CORIMUNO-TOCI, TOCIBRAS, COVINTOC, COVACTA, EMPACTA by TWO_SOURCE; RECOVERY by PRIMARY). The 06:17 recount had used an uncommitted rebuild.
2. **Tracker defect for k-gap to decide (I did not change it):** `g1_tracker.secondary_single` admits only rows with `state == UNVERIFIED`. After the rebuild, 37031750's OMEGA row is `TWO_SOURCE_VERIFIED`, but its second source is the **comparator's** own Rauch 2010 row (35905212). Anti-circularity rightly gives that pairing no TWO_SOURCE credit, yet the pairing also removes the row from SECONDARY_SINGLE. So omega3 Rauch 2010 goes from SECONDARY_SINGLE to UNVERIFIED (`NO_ADMITTED_ROW_FROM_A_SELF_REPRODUCING_META`), and omega3 drops from 5 to **4 of 28**. Corroboration by the comparator should neither add nor remove standing; suggested fix: treat a row that is TWO_SOURCE only *with the comparator* as UNVERIFIED for `secondary_single`. Plant: the OMEGA/Rauch pair.
3. **#4 pcsk9 AACT bindings:** 0 of 9 bindable (6 post only LDL or atheroma; ODYSSEY JAPAN and PACMAN post nothing; ODYSSEY LONG TERM's MACE posting is refused by ARMS, percentages only). PMC per-trial primary verification (worker): **0 of 9**, with 4 LOCATOR_NOT_REPORTED (COMBO I, FH II, HIGH FH, GLAGOV: their reports state no MACE counts), 4 REPORT_AMBIGUOUS, and 1 NOT_FOUND (ODYSSEY JAPAN). pcsk9 stays **2 of 12** (ODYSSEY OUTCOMES, FOURIER).
4. **#10 omega3 AACT:** 0 bindable (5 NO_POSTED_RESULTS; Pahor's outcomes are not named). **JELIS (correction):** no mapping anomaly. NCT00231738 is JELIS (AACT official title names the Japan EPA Lipid Intervention Study); it just has NO_POSTED_RESULTS (registered 2005, completed 2004).
5. **#6 tocilizumab per-trial primary verification (`registry/model_proposals/g1_primary_verify_tocilizumab-covid19-mortality.json`):** 3 of 19 PRIMARY_VERIFIED with counts at 28 days: EMPACTA 26/249 vs 11/128 (PMID 33332779); RECOVERY 621/2022 vs 729/2094 (33933206); TOCIBRAS 14/65 vs 6/64 (33472855). COVACTA's report gives only a weighted difference (58 [19.7%] vs 28 [19.4%], no denominators in the span), so it is VERIFIED_NO_COUNTS. These are the values for a served-pool notice that Mahmood signs; they are not a tracker route on their own.
6. **For the user:** `C:\Projects\worker\run-remote.ps1` fails because Windows OpenSSH rejects `~/.ssh/id_ed25519` (file permissions too open). I did not change the ACL (a security setting). Worker jobs ran via Git Bash ssh instead.

## 2026-10-05 (later) — Evidence lane two's flip-plan items taken over: #3 corticosteroids, #7 iv-iron, tocilizumab 14

**Tracker recount (no flips):** corticosteroids **2 of 5**, iv-iron **1 of 5**, tocilizumab **5 of 19** (the lane-owned file), pcsk9 2 of 12, omega3 4 of 28.

1. **LICENCE INCIDENT (this lane), public repo.** Porting finish-line's record-licence guard (9cf9841bc) and auditing all 6293 tracked records turned up 7 records written by *this* lane. They are `primary_value` locator prompts that carried full text from **NOT_OPEN** copies: BACC-Bay ×2, COVACTA, REMAP-CAP IL-6 and EMPACTA (NEJM COVID-era deposits), and COVIDSTORM ×2 (Elsevier COVID centre). They were **quarantined at HEAD** in 7db4edf9a, moved to `C:\mh-tmp\forest\quarantine`, and their ledger entries were removed. **They remain in git history**: a purge needs a history rewrite and force-push, which I have not done. That is for Mahmood or the captain, as was done at 09:11 for finish-line's 8. The code path is closed: `harness/copy_licence.locator_text` gives a model full text only from a CC copy (PMC permissions, or an Unpaywall `cc-*`/public-domain licence). The typed full-text rung now reads only CC or author-manuscript copies, matching finish-line's HELD_COPY_NOT_OPEN rule. Exception list: **empty**.
2. **History rewrite noticed:** origin/g1/forest-reader was force-updated at 09:11, purging finish-line's 8 records. I rebased only my new commits onto it, did not force anything, and pushed fast-forward only.
3. **CoDEX PRIMARY in corticosteroids rests on a NOT_OPEN copy.** The held-source pool reads CoDEX from `pmc_fulltext` (PMC7489411, "Copyright 2020 AMA. All Rights Reserved"). Under finish-line's rule, a deterministic reader may not admit a value from that copy. Captain or k-gap to decide; I did not change the served pipeline. (My clone holds no cached copy, so its local recount gives 1 of 5. I did not commit that.)
4. **#3 corticosteroids:** all five trials' PMC copies (COVID collection) are NOT_OPEN, including REMAP-CAP hydrocortisone (PMC7489418, AMA), so no model or typed read of their full text. From the abstracts alone:
   - **RECOVERY:** 482/2104 vs 1110/4321 died within 28 days, giving **OR 0.86 (0.76–0.97)**. The comparator's RECOVERY row is the **invasive-ventilation subgroup** (95/324 vs 283/683, OR 0.59), so the OR comparison names a **population difference**.
   - **CAPE COVID:** 11/76 vs 20/73 at **day 21** (the protocol registers 28 days); the tracker has no comparator row joined for CAPE.
   - **CoDEX, REMAP-CAP and Metcovid:** no per-arm death counts in the abstract.
   - Abstract-only locator: 0 of 3.
   - Suggestion for k-gap: where an abstract states per-arm deaths and Ns (RECOVERY), the pool row could carry the counts beside the adjusted rate ratio, so the comparison can be made on the comparator's OR.
5. **#7 iv-iron:** EFFECT-HF's copy (PMC5642327) is **CC**. It states 11 vs 6 patients hospitalised for worsening HF, with 86 per arm given in separate sentences, so the single-quote locator gate refuses it (`LOCATOR_INCOMPLETE`); the gate is kept as is. HEART-FID, AFFIRM-AHF and FAIR-HF have no open copy (abstract only: 0 verified).
6. **Tocilizumab:** my earlier "5 of 7" was counted on the wrong object. Running `g1_tracker.py` on this lane-owned slug had overwritten lane two's 19-trial import (restored in 7b0b6786a). Correct count: **5 of 19**. The 14 unmatched trials ran one codex job each, split across this machine and the worker: **0 verified** (6 report not found, 5 not reported or incomplete, ARCHITECTS and REMDACTA both chose 33195318 so both were refused once the merge saw it, CORIMUNO-TOCI-ICU ambiguous). COVACTA: AACT posts "Mortality Rate at Day 28" only as a percentage (counts reconstructed from percentages stay refused), and its NEJM supplement is NOT_OPEN. The lane file already carries COVACTA as PRIMARY with counts.
7. **Bug fixed** (k-gap's `k_gap_counterfactual.pmc_fulltext_cached`): it replaced the whole index entry when caching text, which dropped the copy's licence mark, and it wrote back a stale index. Plant added (`tests/test_fulltext_index_licence_kept.py`).
8. **Pre-existing failure, not mine:** `test_g1_forest_adjudicate::test_importer_applies_a_resolution_and_names_a_rounding_boundary` (it fails with my changes stashed).

## 2026-10-05 night — URGENT for the captain: corticosteroids-covid19 4/5 on the consolidation is overstated

1. **False timepoint admission, introduced through this lane's `lane_timepoint` (c4b520e9).** Fixed in 6a007a314, with a plant.
   - `meta_timepoint` returned the only day-count found anywhere in a meta's text.
   - Meta 33612824 defines its own primary outcome as "all-cause mortality at the **longest follow-up, defined by the individual trial**". Its only day-count is the **REACT** meta's "28-day", quoted in its background and discussion.
   - Its rows for CAPE COVID (a **day-21** trial), REMAP-CAP hydrocortisone, Metcovid and CoDEX were therefore admitted under the 28-day protocol and became SECONDARY_SINGLE. That is the "3 SECONDARY_SINGLE rows restored" in your consolidation.
   - Fix: a meta that states a varying timepoint (longest, last or end of follow-up, or defined by each trial) has no single timepoint.
   - Class audit over every core-mortality topic: **only 33612824** had admitted rows that depended on it.
   - **Corrected count on this branch: corticosteroids 2 of 5.** RECOVERY is PRIMARY. CoDEX is SECONDARY_SINGLE from 36333729 Fig 4 ("The effect of corticosteroids on Mortality at 28 days…", dual-read ACCEPTED, MH-FE reproduces), with 85/151 vs 91/148, identical to 33612824's row. CAPE COVID and Metcovid are NO_ROW; REMAP-CAP is UNVERIFIED.
   - Please regenerate corticosteroids-covid19 on the consolidation from 6a007a314 or later.
2. **The tracker's `primary_open` is licence-blind** (for your decision; I did not change it). It counts any HELD full text as an open primary (`_ft` / `_upw` caches), whatever its licence. So SECONDARY_SINGLE depends on the machine: refused where a NOT_OPEN PMC copy is cached, allowed where it isn't. Under the licence rule (models read only CC; deterministic readers only CC or author manuscripts), a NOT_OPEN copy is not an openly available primary. Deciding which way to make it consistent changes counts, so it is yours or Mahmood's.
3. **New typed rule: INTERVENTION_NOT_THE_TOPICS** (8b39e109e, 93f19d4ea). A lane figure enters a topic only if its caption or the meta's own title names the topic's drug (or a listed single-drug class: SGLT2, IL-6, IV iron, PCSK9). It applies both in the build and before any read.
   - Found because IL-6 meta 35343397 was ACCEPTED under corticosteroids. Its REMAP-CAP and RECOVERY rows (the IL-6 domains: same registrations, different drug) were blocking the corticosteroid rows by cross-check.
   - Audit of 105 accepted lane figures: 16 had the wrong intervention (pericardiotomy under colchicine, convalescent plasma under tocilizumab, finerenone under spironolactone, …). **Every one of their rows was already refused** by another gate, so no count used them.
4. **Lane importer fixed:** `apply_resolutions` had lost its `return o` on this branch (your consolidation keeps it), so every lane import crashed. That also turns out to be the root cause of the long-failing `test_importer_applies_a_resolution_and_names_a_rounding_boundary`, which now passes.
5. **Reader citation matching now includes DOIs.** Many JATS reference lists carry DOIs only. For corticosteroids this made no difference: those 100 candidates genuinely don't cite the trials. The citation network (your k-gap sweep's `metas_found`) is the right discovery route.
6. **Tocilizumab (lane-owned, re-imported from g1/tocilizumab ac7b959df): 5 of 19.** **10 of the 14 unmatched trials are NOT_ASSESSED by our screen** (COV-AID, COVIDOSE2-SS-A, COVIDSTORM, COVINTOC, COVITOZ, PreToVid, REMAP-CAP, REMDACTA, TOCOVID and one more), and HMO-020-0224 is NOT_ELIGIBLE. No source can count these until k-gap's identification and our screen assess them. BACC-Bay's sweep row (3/82 placebo deaths) is **contradicted** by the trial's own 4/82 and stays refused.
7. **iv-iron:** three HF-hospitalisation panels were read and accepted (33586856 panel B, 38643833 Fig 8 panel B; 36178088 panel A was refused). The build then refuses them all as `OUTCOME_NOT_THE_TOPICS`: the protocol registers hospitalisation **for worsening HF**, and the panels print "heart failure hospitalisation". The gate stays; whether those are the same outcome is a protocol question for Mahmood.
8. **Worker:** the lanes now use my own worktree, `C:\mh-worker\forest-wt`, not the shared checkout. The worker's agy gave no answer (it is set to Gemini 3.5 Flash), so the worker runs codex-only jobs. I copied the public AACT snapshot (6 files) to `C:\mh-worker\AACT\2026-08-30`, because the k-gap sweep fails closed without it.
