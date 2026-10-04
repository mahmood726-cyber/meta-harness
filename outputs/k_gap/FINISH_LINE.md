# G1 finish line: what blocks G1_MATCHED, per topic (branch g1/finish-line on acq/k-gap)

Scope (3 Oct): the COVERAGE_COMPLETE topics that are not G1_MATCHED, plus the four topics nearest to matched.
- The tracker at dba285e3 has **4** COVERAGE_COMPLETE topics that are not G1_MATCHED (not 7): doac-vte-recurrence,
  iv-iron-hfref-hosp, sglt2-primary-prevention-hf and tocilizumab-covid19-mortality.
- The near set adds colchicine-postop-af and dpp4-mace-t2d. doac and sglt2-pp are in both.

Each blocker is a trial plus the route it lacks, or a criterion plus why. Every claim below was checked against a primary
source (AACT 2026-08-30, ClinicalTrials.gov API v2, PubMed efetch, or open full text), or is marked as not checkable.

## State on acq/k-gap e89dfe86 + this branch (4 Oct): every target topic's blocker is NAMED in G1_TRACKER.json
`result_blocker` (canonical schema v2) says why RESULT_AGREES is unmet; per-trial `blocker`s say why each open gap is open.

| topic | G1 | RESULT_AGREES blocker | open gaps (typed) | comparator findings |
|---|---|---|---|---|
| doac-vte-recurrence | NOT_YET | MEASURE_DIFFERS_WHOLE_POOL: ours HR 0.909 (0.748-1.105), theirs RR 0.90 (0.77-1.06); the comparator states '6 phase 3 trials' = our matched set | none | none |
| sglt2-primary-prevention-hf | NOT_YET | MEASURE_DIFFERS_PER_TRIAL (HR vs RR, 4 pairs) | none (Isreb (19) = CREDENCE, named X2) | EMPA-REG: the comparator's 'Zinman 2016' row (95/4687 vs 126/2333) is arm-swapped against the trial's posted HHF (2.7% of 4687, 4.1% of 2333; `tests/test_comparator_arm_check.py`). Not typed on the topic: upstream's surname-core join refuses that row for 'Zinman (8)' because the years differ (our report is 2015), so it is not attached |
| dpp4-mace-t2d | NOT_YET | COMPARATOR_PRINTS_NO_RESULT_FOR_OUTCOME (it pools MACE components only) | EXAMINE, TECOS (labels swapped: see below) | COMPARATOR_STATED_K_ABOVE_ENUMERATED_N ('6 trials' vs 5: CAROLINA missing from ours) |
| colchicine-postop-af | NOT_YET | RESULT_DIFFERS:DIFFERENT_CONCLUSION, caused by Imazio [18] (the comparator pooled COPPS-2's PPS counts as POAF) | Sarzaeem [23] IDENTITY_UNRESOLVED (no PMID/DOI); Imazio [19] INSUFFICIENT_RECORD (percentages only, PDF bot-blocked) | COMPARATOR_ROW_DIFFERS_FROM_TRIAL_REPORT |
| iv-iron-hfref-hosp | NOT_YET | FEWER_THAN_2_COMPARABLE_PAIRS (CONFIRM-HF HR vs OR) | HEART-FID, AFFIRM-AHF, EFFECT-HF (sources exist, see below), FAIR-HF (none open) | COMPARATOR_STATED_K_ABOVE_ENUMERATED_N ('six RCTs'; its own tables list five: the comparator's count is wrong) |
| pcsk9-mace | NOT_YET | MEASURE_DIFFERS_PER_TRIAL | 9: JAPAN IDENTIFICATION:COMPARATOR_NCT_NOT_IN_REGISTRY (cited NCT02017898; real NCT02107898); DESCARTES / PACMAN-AMI IDENTIFICATION (reports not held: 24678979, 35368058); FH II IDENTIFICATION (the identity reader picks 24842558, not the FH I+II results paper 26330422); COMBO I / FH I OUTCOME_NOT_IN_SOURCE; LONG TERM post-hoc MACE; HIGH FH population not stated; GLAGOV via its design paper; OSLER-1 named X3 | COMPARATOR_CITES_NCT_NOT_IN_REGISTRY |

Decisions only Mahmood can take (none applied): (1) may HR stand for RR in the same-trials comparison for a rare outcome --
this one rule is the ONLY blocker of doac-vte and sglt2-pp (sglt2-pp also needs (2)) and blocks 8 topics in all;
(2) is a comparator row our primary proves wrong (EMPA-REG arms swapped, COPPS-2 PPS-as-POAF) excluded from the
same-trials comparison, with the finding stated?; (3) does the 2 Oct 'one bound primary verifies a row' cover posted
registry results whose N equals the randomised total (HEART-FID)?

Harness on this branch since the rebase: canonical v2 (`result_blocker`, `comparator_findings`); whole-pool comparison when
the comparator states its pool k; `COMPARATOR_STATED_K_ABOVE_ENUMERATED_N`; a comparator row belongs to ONE comparator
trial (5 copies in 4 topics fixed: pcsk9 FH II / FH I and PACMAN-AMI / LONG TERM, semaglutide STEP 1 / SELECT,
ticagrelor two / PLATO, balanced Semler [15] / SMART); comparator-cited NCTs checked against AACT (137 cited, 1 invalid);
letters resolved by CommentOn; registry outcomes named by the topic's outcome name.

## Round 3 (4 Oct, "full bore"): harness classes fixed in code, no tracker regeneration
Each takes effect on the next table/tracker build in the full-cache environment; measured here in memory or on the corpus.

| commit | class | trials it moves | corpus impact |
|---|---|---|---|
| 1ddd89c3 | a reference published before the trial STARTED is not its result (`k_gap_table.published_before_start`) | pcsk9 PACMAN-AMI: its registration types ODYSSEY LONG TERM / FH I-II (2015) as RESULT; it started 2017 | 1 trial, 11 refs dropped, 9 kept (JAMA 35368058 kept) |
| 0853c324 | a trial reached through ANOTHER report inherits that report's declaration (`via_report_absent`) | pcsk9 GLAGOV: blocker SCREENED_VIA_OTHER_REPORT -> EXTRACTION:outcome_not_reported:VIA_OTHER_REPORT:DECLARED_WITHOUT_FULL_TEXT (JAMA 27846344 declared from its abstract, no full text held) | label only |
| af4972d2 | report pick never falls back to a paper its own main-report test rejects (`shown_pmid`) | pcsk9 FH II: design-and-rationale 24842558 -> joint results paper 26330422 (pubmed_ncts keeps ONE NCT per PMID); blocker IDENTIFICATION -> EXTRACTION:OUTCOME_NOT_IN_SOURCE | 1 of 307 picks |
| be3efe3e | 'ACRONYM YYYY' normalises to the acronym (`k_gap.norm_acronym`) | omega3 ASCEND (NCT00135226), ORIGIN (NCT00069784), GISSI-HF (NCT00336336); metformin PCOSMIC (NCT00795808) -- all were UNRESOLVED once the table's shifted xrefs were distrusted | 5 labels |
| 247ae55c | a registration typing EVERY reference BACKGROUND keeps those whose own PubMed record names its NCT (`ensure_background_refs`, `background_self_reports`) | pcsk9 DESCARTES: 12 refs all BACKGROUND, NEJM report 24678979 among them | 1 NCT |
| 2f8c0a72 | X-DESIGN audit: 'randomized, open, single-center' states open-label (`OPEN`) | colchicine-postop Zarpelon [20]: full text PMC4976950 says "randomized, open, single-center" -> TRUE_SCOPE_DIFFERENCE once `k_gap_exclusion_fulltext.py` reruns (its last run predates this row) | 4 abstracts newly match, all open-label |

Named, NOT fixed (each needs a decision or a source, not code):
- **POPULATION_VOCABULARY is a protocol decision, not a screener bug** (codex's recorded class, reproduced here). X2 does
  what the protocol says; the vocabulary is the question. probiotics `population_any` lists only OUTCOME phrases
  ('antibiotic-associated diarr*'); Cindoruk, Plomer, Shimbo (H. pylori eradication) and Plummer (patients on
  antibiotics) never say them. Adding 'antibiotic therapy/treatment', 'eradication therapy', 'Helicobacter pylori'
  flips **20 of 449** records to INCLUDE (most are H. pylori trials with GI-symptom outcomes) -- a scope change.
  omega3: adding 'angina', 'reinfarction' moves DART (2571009) and DART-2 (12571649) from X2 to **X3** (dietary advice is
  not the protocol intervention): they stay excluded either way, and X3 is the honest reason.
- **omega3 'Risk & Prevention 2013'**: no acronym; AACT has TWO n-3 registrations titled 'Risk and Prevention Study'
  (NCT00317707, NCT02103517) -- a name route would be AMBIGUOUS, so it stays IDENTITY_UNRESOLVED. GISSI-P (1999) predates
  registries.
- **pcsk9 ODYSSEY LONG TERM**: MACE is post hoc in its report; our rule does not pool a post-hoc outcome as the primary.
  Codex calls this gate unsupported by the protocol; it is a stated rule, so changing it is a decision.
- **iv-iron AFFIRM-AHF**: its effect is a RATE ratio (total hospitalisations), not a risk ratio -- a true estimand
  difference. HEART-FID needs decision (3).
- **spironolactone RALES**: our row is labelled RR because the NEJM text says "relative risk", but it is a Cox estimate
  (an HR) -- it belongs under decision (1), not a separate fix.

Decisions now open for Mahmood (none applied): (1)-(3) above, plus **(4)** may the probiotics population include patients
on antibiotic / H. pylori eradication therapy whose record never names AAD (20 records flip)?

## Closed on this branch
| topic | what closed | how |
|---|---|---|
| sglt2-primary-prevention-hf | Isreb (19) named out of scope | The comparator's ref 19 is a LETTER (31509682). PubMed's CommentOn link resolves it to CREDENCE (30990260), which our own screen excludes: X2, `population_none` 'nephropathy'. Span: "Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy." Rule: `registry/comment_on.json` + `g1_tracker.topic`. **ALL_ELIGIBLE_MATCHED is now met** (5 of 5). |
| (all topics) | figure rows join their trial-list entries | Fixed upstream in e89dfe86 (surname-core fallback join). This branch's own version was dropped at the rebase. `tests/test_family_join_labels.py` keeps the cases found here (Zinman (8) / Zinman 2016, two Youngs, Semler (SALT trial), SOLOIST-WHF/SCORED combined row) as regression tests; all pass against upstream's join. |
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
- **pcsk9-mace, ODYSSEY FH II (NCT01709500):** fixed in round 3 (af4972d2): the identity reader picked the design paper.
- **Rebuild environment:** a fresh worktree lacks the gitignored caches (`outputs/k_gap/_aact_results.json`, `_ctgov/`,
  `_ft/`, `_upw/`, `_reg/`, `_aact_store.json`). A tracker rebuild here silently loses pool rows that rest on them:
  probiotics Ehrhardt, corticosteroids-covid19 CoDEX, and one non-comparator pool trial in colchicine-postop-af. Those
  three files are kept at upstream's version and need a rebuild in the full-cache environment. Every file committed
  here was checked: pool membership and values are unchanged against dba285e3.

## Seeding every non-pooled trial
Fixed upstream in f2fd773e (`needs_seed`). This branch found the same class independently: Radholm (9) lost its
same-trial match once a comparator row joined. `tests/test_g1_finish_line.py` asserts Radholm stays matched.

## Comparator arm check (scripts/g1_comparator_arm_check.py -> registry/comparator_arm_check.json)
Every joined comparator row with per-arm counts on a trial with a registration was refereed against the trial's posted
result for the topic outcome (CT.gov API v2, request + sha256 recorded): 29 rows -- CONSISTENT 1 (HEART-FID 297/1532 vs
332/1533 = its posted counts), SWAPPED 0, UNDECIDED 8 (posted outcomes are composites or rates, never the single outcome),
NO_POSTED_OUTCOME 19, FETCH_FAILED 1 (ODYSSEY JAPAN's cited NCT02017898: 404). The one swap known (EMPA-REG) sits on a row
the join does not attach.
