# G1 finish line: what blocks G1_MATCHED, per topic (branch g1/finish-line on acq/k-gap)

Scope (3 Oct): the COVERAGE_COMPLETE topics that are not G1_MATCHED, plus the four topics nearest to matched.
- The tracker at dba285e3 has **4** COVERAGE_COMPLETE topics that are not G1_MATCHED (not 7): doac-vte-recurrence,
  iv-iron-hfref-hosp, sglt2-primary-prevention-hf and tocilizumab-covid19-mortality.
- The near set adds colchicine-postop-af and dpp4-mace-t2d. doac and sglt2-pp are in both.

Each blocker is a trial plus the route it lacks, or a criterion plus why. Every claim below was checked against a primary
source (AACT 2026-08-30, ClinicalTrials.gov API v2, PubMed efetch, or open full text), or is marked as not checkable.

## Closed on this branch
| topic | what closed | how |
|---|---|---|
| sglt2-primary-prevention-hf | Isreb (19) named out of scope | The comparator's ref 19 is a LETTER (31509682). PubMed's CommentOn link resolves it to CREDENCE (30990260), which our own screen excludes: X2, `population_none` 'nephropathy'. Span: "Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy." Rule: `registry/comment_on.json` + `g1_tracker.topic`. **ALL_ELIGIBLE_MATCHED is now met** (5 of 5). |
| (all topics) | figure rows join their trial-list entries | `family_of_factory` now strips the list label's reference number. 'Zinman (8)' never led 'Zinman 2016', so none of sglt2-pp's 8 accepted comparator rows joined. Reference numbers are not compared (melatonin's comparator numbers its figure differently from its list). A first author + year confirmation outranks a bare name (two 'Young' entries). A combined row ('SOLOIST-WHF/SCORED') binds to neither. Corpus: 23 rows newly joined, 0 lost. |
| (all topics) | registry outcome named by the topic's own outcome NAME | iv-iron's keywords all say 'worsening', so HEART-FID's primary 'Number of Hospitalizations for Heart Failure' was refused OUTCOME_NOT_NAMED. Corpus: 2 candidates newly named: HEART-FID, and DAPA-HF's composite, which the ESTIMAND gate still refuses. |

## Still blocked, by topic

### doac-vte-recurrence: only RESULT_AGREES is unmet; a MEASURE decision is needed
- **All 6 eligible are matched.** AACT corroborates all six of our rows exactly: RE-COVER HR 1.10 (0.65-1.84),
  RE-COVER II 1.08 (0.64-1.80), Hokusai 0.89 (0.70-1.13), AMPLIFY RR 0.839 (0.597-1.180), EINSTEIN-DVT 0.68 (0.44-1.04),
  EINSTEIN-PE 1.12 (0.75-1.68).
- **The comparator's per-trial rows are unreachable.** Its PDF (24963045, bronze OA at ashpublications.org) returns
  403 Cloudflare; it is not in PMC. No per-trial pairs means no per-trial same-trials comparison.
- **The whole pools are the same trials.** The comparator's abstract states "6 phase 3 trials", exactly our six; the one
  named difference is a pooled bleeding analysis, not a trial.
- **But they are different measures.** Ours is HR 0.909 (0.748-1.105): five trials state only an HR (text and AACT),
  and AMPLIFY an RR. Theirs is RR 0.90 (0.77-1.06). AACT posts percentages, not counts, for 5 of 6, and a converted
  percentage is never a count.
- **DECISION NEEDED (not applied):** if HR may stand for RR on a rare outcome (2.0% vs 2.2%), the whole-pool verdict is
  AGREE (gap 0.063 of the comparator's CI half-width) and doac flips.

### sglt2-primary-prevention-hf: only RESULT_AGREES is unmet (MIXED_MEASURES)
- **Measures differ.** Our rows state HRs (AACT posts HHF for these trials only as HRs). The comparator pools RRs from
  counts.
- **The comparator has an error on EMPA-REG.** Its Zinman row prints 95/4687 vs 126/2333 (RR 0.38). The trial's posted
  HHF is empagliflozin 2.7% of 4687 and placebo 4.1% of 2333 (CT.gov NCT01131676). The comparator's row matches only
  with the arms SWAPPED; the trial's own ratio is about 0.66.
- **A HR≈RR rule would not be enough.** On the 3 pairs that joined before the join fix, it would give AGREE (gap 0.004),
  but the arm-swapped EMPA-REG row now joins.
- **DECISION NEEDED:** the measure question as for doac; plus whether a comparator row shown to be arm-swapped is
  excluded from the same-trials comparison (with the finding stated).

### iv-iron-hfref-hosp: cannot flip on open sources
- **HEART-FID:** AACT ITT 297/1532 vs 332/1533 (= the comparator's row). Now NAMED by the binding gate, but posted
  results alone are AACT_ONLY_SINGLE_SOURCE under the sweep's rule ("recorded, never counted"). The 2 Oct "one bound
  primary verifies a row" decision has been applied to trial texts, not to AACT-only rows. **DECISION:** extend it to
  AACT rows whose posted N equals the randomised total (HEART-FID 3065 = 1532 + 1533)?
- **AFFIRM-AHF:** AACT participants with ≥1 HF hospitalisation 142/558 vs 178/550 (OTHER_PRE_SPECIFIED; title 'HF
  Hospitalisations' uses the abbreviation, so it is not named). The comparator used TOTAL EVENTS 217/294 as if they were
  participants (an OR on events). Population: acute HF, LVEF <50%; no topic rule excludes mildly reduced EF, which is
  the topic owner's call.
- **EFFECT-HF:** open CC BY text (PMC5642327), participants 11/88 vs 6/86. The comparator used events 13/88 vs 13/86.
- **FAIR-HF:** no posted results, not in PMC, no open primary. **This alone blocks the flip.**

### dpp4-mace-t2d: G1 is impossible against this comparator
- **No MACE analysis.** The comparator (34754403) analyses only components (MI, stroke, HHF, UA, revascularisation,
  CV death); it prints no pooled MACE (NO_PRINTED_POOL is correct). RESULT_AGREES can never be met for 3-point MACE.
- **Its trial set is 6, not 5.** CAROLINA (31536101, linagliptin vs glimepiride) is missing from the tracker's
  REFERENCE_SEED. It should be named X3 (active comparator).
- **Two blocker labels are swapped.** EXAMINE has OUTCOME_NOT_IN_SOURCE and TECOS has ESTIMAND_CLASS_MISMATCH.
  - EXAMINE's primary IS 3-point MACE (HR 0.96, one-sided 97.5% upper 1.16; no two-sided CI printed).
  - TECOS's primary is 4-point MACE; its 3-point MACE HR 0.99 (0.89-1.10) is posted in AACT (outcome 258888999,
    SECONDARY) and was missed.
- Proposal: a typed COMPARATOR_DOES_NOT_POOL_OUTCOME state, instead of NOT_YET forever.

### colchicine-postop-af: comparator error plus unreachable primaries
- **DIFFERENT_CONCLUSION is caused entirely by one comparator row.** Imazio [18] = COPPS-2: the comparator printed
  35/180 vs 53/180, which is COPPS-2's postpericardiotomy-syndrome endpoint. The POAF result is 61/180 vs 75/180. With
  POAF the same-trials pool is exactly ours, 0.80 (0.63-1.02); with their numbers, exactly theirs, 0.69 (0.50-0.94).
  This is already typed SECONDARY_WRONG.
- **Imazio [19]** (COPPS POAF substudy, 22090167): in scope. The abstract gives percentages only (12.0% vs 22.0%), there
  are no AACT results, and the PDF is behind Cloudflare: no counts. The comparator's 12/169 vs 22/167 look like the
  percentages copied in as counts.
- **Sarzaeem [23]:** Tehran Univ Med J 2014, no PMID/DOI; the source sits behind an ArvanCloud bot check.

### tocilizumab-covid19-mortality: see the g1/tocilizumab lane
- 5 of 19 independently confirmed. The other 14 are trialist-supplied data, a contradicted meta, or posted percentages.

## Found while closing (not fixed on this branch)
- **pcsk9-mace, ODYSSEY FH II (NCT01709500):** reads blocker IDENTIFICATION. Yet it is in our own build (family
  PMID 26330422) and not pooled, with no refusal recorded. A missing refusal falls through to IDENTIFICATION: a
  pre-existing class, distinct from the seeding fix below.
- **Rebuild environment:** a fresh worktree lacks the gitignored caches (`outputs/k_gap/_aact_results.json`, `_ctgov/`,
  `_ft/`, `_upw/`, `_reg/`, `_aact_store.json`). A tracker rebuild here silently loses pool rows that rest on them:
  probiotics Ehrhardt, corticosteroids-covid19 CoDEX, and one non-comparator pool trial in colchicine-postop-af. Those
  three files are kept at upstream's version and need a rebuild in the full-cache environment. Every file committed
  here was checked: pool membership and values are unchanged against dba285e3.

## Seeding every non-pooled trial (harness fix)
The step that seeds comparator references through our own screen ran only for route NO_ROW, so 45 trials in 12 topics
that had a comparator row joined (route UNVERIFIED) never saw our screen. When the label join attached Radholm (9)'s row,
it lost its SCREENED_VIA_OTHER_REPORT match to the CANVAS pool row. Now every trial not in our pool is seeded.
- dapagliflozin-hfpef: DECLARE and DELIVER now show X1, audited INSUFFICIENT_RECORD (they read IDENTIFICATION /
  EXTRACTION_FROM_TABLE).
- esketamine: Trial B now reads DECLARED_ABSENT, KNOWN_REPORTED_NOT_YET_EXTRACTED.
- melatonin: with every figure row joined, upstream's NOT_IN_COMPARATOR_OUTCOME_ANALYSIS names Garzón [26], Lemoine
  [27] and Ellis [37]. None of them is among the 15 rows of the comparator's mortality figure, which reproduces its own
  printed pool. melatonin goes from 11 open gaps to 8.
