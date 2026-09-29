# V1.0.1 integrated candidate (evid2/v101-integrated), 27 Sep 2026

This branch supersedes `evid2/v101-overlap`, `evid2/v101-colchicine` and `evid2/v101-population`. It carries their
work together with the fixtures from the colchicine-secondary, CAP, COVID-corticosteroids, dapagliflozin, denosumab and
DOAC-VTE reviews. All counts below are measured against V1 (`9eacfe09`) on a full 32-page rebuild; the JSON beside this
file holds the rows.

## Result-level

- **Pooled results moved: none** (`LABEL_CHANGES.json`). No pooled estimate, interval or pooled trial set changed on
  any page.
- Computed comparator overlap relation served on 32 of 32 pages: DISJOINT 2, IDENTICAL_SET 1, NOT_ENUMERABLE 19,
  OVERLAPPING 6, SUBSET 3, SUPERSET 1.

## Label changes, n of N

| Change | n of N | File |
|---|---|---|
| Funding labels (typed funders / material support / funder-role statement) | 171 of 273 rows, 31 topics | `FUNDING_LABEL_CHANGES.json` |
| X2 comorbidity exclusions that flip | 6 of 539 (2 now included, 4 now excluded on X3, the comparator axis) | `COUNTS.json` |
| Registry IDs resolved to a publication before any results-only / ghost label | 59 NCTs in 13 topics | `COUNTS.json` |
| Comparator full texts refused (a citing article held under the comparator's PMID) | 3 of 32 | `COUNTS.json` |

- **Funding.** Against V1, no row whose V1 label was industry loses its tie. 126 rows carry an established tie, and no
  row is labelled "no industry tie": a public funder named "and others" never establishes absence.
- **Funding audit** (`FUNDING_AUDIT.json`). Four codex lanes read the funding evidence independently. Every quote
  was located, and every disagreement was traced to a root cause.
  - On the 61 held full texts, 11 of 12 missed industry ties are recovered. The misses came from a reach cap, the
    sentence splitter, RX-OL9, author-contribution lines, and missing statement and supply phrasings. The twelfth
    (a branded product named in the methods) is not a tie, by decision.
  - One served row goes from PRESENT to NOT_ESTABLISHED: tocilizumab PMID 33472855. Its PRESENT rested only on
    author disclosures read as funders.
  - Author disclosures now stay out of funder lists. An author's company directorship blocks "no industry tie".
  - On the 222 rows without full text, a registry non-industry class now outranks a bare company suffix
    (TriHealth Inc. is a non-profit hospital system).
  - Open question for the captain: the Novo Nordisk Foundation is classed as industry by name (semaglutide PMID
    42070571).
- **ARTS-DN Japan harms.** Linking Katayama 2017 exposed its hyperkalaemia statement to the harm panel: "no patients
  developed hyperkalemia", across seven doses and a shared placebo. It is recorded as a sourced typed refusal
  (RETRIEVED_INCOMPATIBLE_STRUCTURE, as for ARTS-DN), not as an open HARMS_INCOMPLETE.
- **X2 flips.** CARDIA-STIFF (NCT04739215, dapagliflozin) and NCT05057806 (empagliflozin) are included at screening;
  neither is pooled.
- **Colchicine-secondary: flip deferred.** The comorbidity rule is checked there, and Raju 2012 would be included.
  But Raju reports an excess of diarrhoea with no arm counts in any held source, and the harms gate refuses such a
  page. The topic keeps its V1 screening; see `registry/population_witness_topics.json`.
- **Registry relinks.** A relink changes the GRADE publication-bias census wording. That domain is NOT_ASSESSED on
  every affected page, so no certainty rating moves. Example: tocilizumab 20 of ~38 → 18 of ~38 completed
  unpublished.

## Comparator full texts refused

`records.json` `comparator_fulltext` for van Es 2014 (doac-vte-recurrence), Imazio 2012
(colchicine-recurrent-pericarditis) and Cheema 2024 (corticosteroids-cap-mortality) were citing articles. They were
fetched before the same-article PMC link rule (f32c307a). `harness/held_text_identity.py` refuses them using
`cache/<slug>/pmc_links.json`.

- No served value came from those bytes.
- The DOAC and CAP comparator panels, which had certified the bytes as their held document, are now NOT HELD.
- The 61 held trial full texts were re-checked: each is the right article.

## GLP-1: the B-prime outcome-ascertainment clause is executed

The amendment admits a trial only if "3-point MACE, or its exact three components, was prospectively specified and
systematically ascertained". `screen_family` had skipped that half, so "145 eligible" counted STRUCTURAL passes.

- **Three states** (`harness/ascertainment.py`, `cache/glp1-ra-mace-t2d/ascertainment_evidence.json`):
  - STRUCTURAL_PASS 145.
  - FULL_ELIGIBLE 9: both halves evidenced from held bytes, the prospective source dated before the results.
  - PENDING 136: never eligible, never excluded; each carries a retrieval task for its protocol, SAP or supplement.
  - ADMISSIBLE_RESULT per analysis: MACE 7 of the 8 pooled.
- **SUSTAIN-6 is pooled but PENDING.** Its EU register record names MACE, but the register shows the current
  protocol version, so the date doesn't date that text. The pooled result is rendered as conditional on it; it is not
  removed.
- **Date tiers.** Harmony Outcomes' and PIONEER 6's design papers post-date trial completion but precede the results.
  They are marked DATED_BEFORE_RESULTS_ONLY, so the stricter reading stays visible.
- **Programme evidence.** Husain 2020 states that the SUSTAIN 1–5 and PIONEER 1–5, 7–10 glycaemic trials recorded
  MACE as adjudicated events. That supports ascertainment only. Their prospective specification needs each protocol,
  and the post-hoc pooled estimate never enters a pool.
- **PIONEER 8** (NCT03021187) is linked to Zinman 2019, PMID 31530667, by the token "PIONEER 8" printed in the
  registry acronym and the paper. Its two harm statements are sourced typed refusals.
- **Search execution records** (`harness/search_execution.py`): one row per declared source.
  - CENTRAL and ICTRP: NOT_EXECUTED.
  - PubMed, Europe PMC and citation chasing: EXECUTED_IDS_NOT_HELD. The 15 Sep search_v2 run's funnels and queries
    are recorded, its response bodies are not, and it is not this page's retrieval.
  - ISRCTN: CALLED_NO_RESULT_RECORD.
  - AACT: EXECUTED.
  - Trial-family assembly: MANUAL_ONLY.
  - Seeded, manual and legacy rows are rendered distinct. The source-status table's "Europe PMC: RAN_OK" was
    inferred from merged records, not a recorded execution.
- **Pooled results unchanged** (MACE HR 0.856, 0.8086–0.9061, k 8).

## Melatonin (Ferracioli-Oda 2013)

- **Scope, in its own words:** 19 studies in adults and children with primary sleep disorders (14 insomnia, 4
  delayed sleep phase, 1 REM sleep behaviour), 15 in the latency plot. "19 vs 1" is not 18 missing trials.
  - The stated count had been read as "not stated": the extractor knew only "trials"/"RCTs". `_K_STUDIES` now reads
    "N studies … were included".
  - A pre-existing off-by-one that cut the first letter of a quote at text start is fixed.
- **only_ours** comes from the pooled set (empty). Live main still lists the screened Xu and cancer studies.
- **Wade:** one trial at identity level (NCT00397189). Its inputs differ: all adults with PSQI-Q2 (reported by the
  review, not held) versus our 65–80 diary SOL (registry-held).
- **Display vs calculation** (`harness/comparator_display.py`; figure image held with sha256):
  - COMPARATOR_DISPLAY_ERROR for the swapped weights (Smits 2003 printed 3.97 vs 0.29 reconstructed; Almeida Montes
    printed 0.28 vs 3.94).
  - COMPARATOR_DISPLAY_ERROR for the objective-subgroup interval: 7.81 in the figure, 8.71 in the text and the
    reconstruction.
  - The pooled calculation reproduces: FE 7.0606 (4.3765–9.7448) vs published 7.06 (4.37–9.75). It is a positive
    control of our engine (`registry/positive_controls.json`).
- **Search:** "melatonin"[Title] is a title-restricted concept query, not seeding.
- **Cancer-insomnia study (27559258):** it enrolled DSM-IV primary insomnia, and "cancer" never excludes it. Its
  Athens Insomnia Scale is never converted to minutes; that is recorded as a sourced typed refusal.

## DOAC-VTE (van Es 2014)

- 6 trials shared by name: 5 input-identical, 1 with different inputs. Hokusai-VTE enters van Es with on-treatment
  counts and ours with the overall-study result; its window and analysis set differ.
- Positive control, reproduced by our engine: RR 0.901688 (0.766115-1.061252), tau2 0, Q 4.155222. The result is
  conditional on the one row not held (Hokusai on-treatment 66/4,118 vs 80/4,122).
- With our held Hokusai row the same pool is 0.913907 (0.78938-1.05808).
- The comparator's phase-3 scope is recorded as the comparator's; our screening has no phase rule.

## Metformin-PCOS (Sharpe 2019, Cochrane)

- **Wrong comparison:** the protocol benchmarked OR 2.64, metformin vs placebo/no treatment. Analysis 2.4 (metformin
  plus clomiphene vs clomiphene alone; OR 1.65, 1.35–2.03; 21 studies; 1,568 women) now governs. 2.64 is kept,
  labelled WRONG_COMPARISON. Labelled protocol erratum, protocol-only commit.
- **Same question:** a `contrast` dimension is added. The two questions are RELATED, differing on control
  ("clomiphene alone" is broader than placebo).
- **Membership:** 21 rows are read from the forest plot (Cochrane's image, not held; URL and sha256 recorded). Row
  count and 789 + 779 women are checked against the stated totals. All 3 of our trials are shared, with the same
  counts (SUBSET).
- **Legro 2007:** the plot's 108/209 vs 106/209 disagrees with the paper's ovulated rows (174 vs 157), so it is
  COMPARATOR_ROW_UNRECONCILED and never copied.
- **Search:** a row joining separate queries with ` || ` is now classified query by query. It had been read as one
  title reconstruction.

## NOAC-AF (COMBINE AF, Carnicelli 2022)

- IDENTICAL_SET, 4 of 4: RE-LY is now bound by the acronym in the held registry record's title.
- **Same trials, different model:** IPD, a trial-stratified Cox model with random effects, and 32-month censoring are
  quoted from the held text. Its narrower interval (0.81, 0.74–0.89) is that model's. Agreement is a checkpoint on
  the same trials, not an independent result.
- J-ROCKET AF is a V1.1 recall case (`evid2/v11-discovery-glp1`, 93013008).

## PCSK9 (Wang 2022, Frontiers)

- **Enumerated:** its trial table identifies rows by printed NCT, not reference links. A registry-ID route in
  `scripts/comparator_trial_tables.py` binds each row by the NCT printed in the same located `<tr>`. There are 12
  rows, shared 2 (FOURIER, ODYSSEY OUTCOMES), ours-only 0.
- **Scope, in its own words:**
  - OSLER-1's control is standards of care, not placebo (the abstract's "25 812 received placebos" does not hold for
    that row).
  - Eight of the others are 1–1.5-year lipid or imaging trials, and one is PACMAN-AMI.
  - All are pooled as RRs.
  - So 12 vs 2 is not 10 omissions.
- **Not independent:** FOURIER and ODYSSEY OUTCOMES hold 46,488 of its 53,486 patients.
- **Panel note:** the seeded note "trial membership remain unknown" is no longer printed where the set is enumerated
  (it contradicted the overlap on every such page).

## Trials named by a held comparator enter screening (`harness/comparator_named.py`)

- Every enumerated comparator row we did not hold is fetched by its identifier:
  - a PMID row, by the cited PMID;
  - an NCT row, by every PubMed record whose DataBank lists that NCT and is attributed to a named trial.
- The records enter screening with `found_by: COMPARATOR_NAMED`.
- Records are re-derived from the held XML (sha256 checked).
- A candidate never displaces a record or trial we hold, which is why seeding had been disabled.
- Rows with no identifier are listed as not screened.
- 17 topics have an enumerated comparator.

| Topic | Screening includes | Families |
|---|---|---|
| pcsk9-mace | 5 → 7 (PACMAN-AMI 35368058, ODYSSEY FH I 24842558) | 11 → 20 |
| melatonin-primary-insomnia-sol | 8 → 10 | 92 → 106 |
| semaglutide-obesity-mace | 1 → 2 (STEP 8) | 41 → 57 |
| colchicine-recurrent-pericarditis | 3 → 3 | 41 → 44 |
| esketamine-trd-madrs | 4 → 4 | 103 → 104 |
| omega3-cardiovascular-events | 20 → 20 | 105 → 113 |
| statins-primary-prevention-elderly | 4 → 4 | 27 → 39 |
| ticagrelor-vs-clopidogrel-acs | 3 → 3 | 25 → 26 |

- **No pooled result moved** (32 pages compared with HEAD).
- **Held out: sglt2-primary-prevention-hf.** Its candidate Kosiborod 2017 (PMID 28284707) is a post-hoc analysis of
  patients WITH heart failure, pooled from five dapagliflozin trials. Screening admitted it as an "eligible
  double-blind/placebo-controlled RCT", and it moved HF hospitalisation from k 4 (0.6956, 0.5763–0.8397) to k 5
  (0.6920). That is a screening false inclusion (a pooled analysis, and the wrong population), not a trial. The
  candidate file is not committed. The screening defect is for the captain.
- **Harms of the entrants:** there are four typed refusals (`cache/<slug>/verified_effects.json`, each span in the
  held PubMed XML).
  - PACMAN-AMI discontinuation.
  - STEP 8 GI AEs (MULTI_ARM_UNRESOLVED) and STEP 8 discontinuation.
  - Ellis 1996 AEs.
  - No harm is left KNOWN_REPORTED_NOT_YET_EXTRACTED on any page.
- **Codex REV-R2:** it found 7 defects in this round's modules, all reproduced, fixed and pinned (quote tag-stripping,
  held DOI at merge, ALREADY_HELD recheck, unreconciled row binding, excluded-table route, DOI-only rows, `<tbody>`
  attributes).
- **Round-3 leak fixed:** population-excluded GLP-1 family rows no longer print the topic's ascertainment evidence
  map.

## Sacubitril/valsartan HFrEF (Ji 2023, network meta-analysis)

- **Enumerated from its own outcome-level list:** "The composite CV outcome in patients with HFrEF was available in 10
  trials." is followed by exactly ten cited references, each with a PMID.
  - New route: `scripts/comparator_outcome_list_members.py`. `comparator_panel.validate` re-proves that the span
    prints "10 trials" and cites exactly ten references including each member.
  - Result: SUBSET, 10 comparator trials, shared 2 (PARADIGM-HF, PARALLEL-HF), ours-only 0. Before this it was
    NOT_ENUMERABLE.
- **PARALLEL-HF:** we pool it from its registry record (NCT02468232) and hold its Circ J paper (33731544) as an
  unlinked report-only family. Ji's row binds to the registered trial by the acronym printed in the cited title.
  - JATS prints the acronym with a Unicode hyphen, which is now read as '-'.
  - The unlinked paper is disclosed.
  - Linking the paper to the registration (a `family_pub_links` entry) was measured: it moves the pool (k 2 -> 1,
    HR 0.80), because screening excludes the paper X-DESIGN (its abstract never says "double-blind") and dedup then
    lets the paper replace the registry record. Not landed; a decision for the captain.
- **Scope, in its own words:**
  - 17 studies network-wide, over HFrEF and HFpEF and three classes.
  - 10 in the HFrEF composite.
  - "three trials comparing ARNI with RASi" — PARADIGM-HF, PARALLEL-HF, and PARAGON-HF, an HFpEF trial.
  - So the direct HFrEF evidence is exactly our two trials. Our control stays a RAS inhibitor.
- **Not validation:** its 0.83 is a frequentist network RR of event proportions, combining direct and indirect evidence.
  We pool hazard ratios of the same two direct trials (PARADIGM-HF alone: HR 0.80). They are different
  representations of largely the same evidence.
- The abstract's "compared with placebo" for the same RR stays COMPARATOR_INTERNAL_MISMATCH (recorded earlier).
- **Comparator-named:** all 10 rows are already held, so nothing new entered screening. No pooled result moved.
- **LIFE** (NCT02816736, 34730769) is a V1.1 recall case (`evid2/v11-discovery-glp1`, a3475bd7). Its primary endpoint
  is NT-proBNP, yet its report states a clinical-event composite and hyperkalaemia by arm.

## Semaglutide obesity MACE (Stefanou 2024)

- **Membership:** Figure 2 (the MACE forest plot) is held (CC BY-NC, sha256-pinned) and read row by row. There are 7
  rows, and the column totals 13,696 / 11,008 match the plot's Total. Each row names its row in the comparator's 16-row
  table.
  - The outcome's pool is those 7: SUBSET, shared 1 (SELECT), ours-only 0.
  - The other 9 are listed as out of scope, not dropped.
- **WEIGHT CONCENTRATION** (`comparator_analysis.weight_concentration`, general, from any counted plot) is computed as
  log-OR inverse variance, with 0.5 added to rows with a zero cell. SELECT carries 97.44% (crude OR 0.7985), so
  agreement is agreement with SELECT, not 7-trial corroboration.
- **Positive control** `stefanou-2024-glp1-obesity-mace`: our engine reproduces OR 0.793265 (0.708299–0.888423),
  τ² 0, Q 1.374405 at 5e-7. The comparator used DL; with Q < df the DL τ² is 0 and DL equals the common effect. Our
  engine implements no DL estimator.
- **COMPARATOR_METHOD_INCONSISTENCY** (a new code): its methods set Egger p < 0.10, yet it reports p = 0.0795 for MACE
  and concludes "no asymmetry". Both sides are held and quoted. Neither the reassuring wording nor a bias claim is
  made.
  - This exposed the REV-R2 tag-strip defect in `comparator_models`: its normaliser deleted "p < 0.10 … >". Fixed.
- **"Per-trial inputs are not machine-exposed"** was a fixed sentence on every page. It is now derived from what is
  held (page and `transparency_score.py`).
- **V1.1 discovery** (`evid2/v11-discovery-glp1`, 17e3fcc9): the search is PMID/title anchors on SELECT alone. All
  eight semaglutide RCTs Stefanou includes are unreachable by it.

## Semaglutide obesity weight (Medicine 2026)

- **WRITTEN vs EXECUTABLE** (`harness/rule_trace.py`): every executable exclusion term is TRACED_LITERAL,
  TRACED_BY_CLAUSE (`registry/rule_trace/<slug>.json`, quote located in the protocol) or UNTRACED.
  - **On an enforced topic** an untraced term is flagged and not applied. A record it would have caught, if otherwise
    included, is NEEDS_ADJUDICATION (decision `adjudicate`, rule X-UNTRACED).
    - Weight is enforced, with 5 untraced terms: type 1 diabetes, knee osteoarthritis, heart failure, bimagrumab,
      cagrilintide.
    - 4 records now await adjudication. The pool is unchanged.
    - Served eligibility lists only the applied terms.
  - **Fixture:** STEP 9 (39476339, held) is adjudicated under the trace and was keyword-excluded without it.
  - **Every other page** lists its untraced terms. They are still applied, because no trace exists yet. Codex lane
    TRACE-T1 is proposing traces for the remaining 350 terms (unverified).
- **Comparator:** Table 1 rows print "Surname, year". Each binds to the one reference in the held JATS with that first
  author and year, re-proved in `comparator_panel.validate`.
  - Result: SUBSET, 2 of 4 (STEP 1, STEP 3).
  - O'Neil 2018 (daily dose-ranging, 52 weeks) and STEP 4 (withdrawal) answer other questions, so 4 vs 2 ≠ 2
    omissions.
  - Its MD -11.85 vs our -11.84 is a coincidence of different sets and methods, not validation.
  - It is RELATED, not SAME_QUESTION.

## SGLT2 CKD (SMART-C, JAMA 2026)

- **Comparator type** `CONSORTIUM_ANALYSIS`: a consortium's pooled analysis of its own member trials, not a systematic
  review. Its list is never used as a discovery source; `comparator_named` skips consortium comparators.
- **Membership, as the comparator states it:** the 10 member trials are named in the PMC full text (PMC12595549).
  - That text carries no open licence, so it is recorded as `VERIFIED_NOT_HELD`: PMC ID, body sha256 and a short
    quote that prints every name.
  - Result: SUBSET, shared 3 of our 3 (CREDENCE, DAPA-CKD, EMPA-KIDNEY).
- **Not the same outcome:** its 0.62 is a harmonised kidney-only outcome (cardiovascular death excluded). It was served
  beside our trial-defined composite and is now labelled `DIFFERENT_OUTCOME`.
  - Our results are the composite (0.684) and a kidney-only sensitivity (0.651). Same-question endpoint = NO.
  - The review's cardiovascular-death-inclusive 0.75 is not in the text we read, and is attributed to the review.

## SGLT2 HFrEF (Pandey 2022)

- **Participant totals** now derive from the same contributing set as the pool.
  - An effect-only row counts its arms from its own located result sentence, and a missing n refuses the total.
  - A set/sum invariant is pinned by a plant.
  - ours_n: 4,744 (DAPA-HF alone) → 8,474. Excess: 4,455 → 725.
- **Membership:** Pandey's Table 1 is bound from the committed transcription by printed acronyms that name exactly one
  family. SUBSET, shared 2.
  - SOLOIST-WHF (sotagliflozin) is outside our dapagliflozin-or-empagliflozin scope, and EMPEROR-Preserved is an
    LVEF > 40% trial.
  - So the excess is not missing evidence. Its HR 0.74 is a checkpoint only.
- **Comparison-level contrast** (`harness/comparison_contrast.py`, rule X3-CONTRAST). NCT04385589 (Ibrahim; paper
  33426003 now linked) had a "Placebo group" whose only intervention is the experimental arm's background insulin.
  - Refusal needs three facts: a background-only arm, no placebo product, and the trial's own publication never
    mentioning placebo or blinding.
  - Measured over all 32 topics, it fires on this family, plus one probiotics family that was already excluded.
  - A first, intervention-only version fired on dozens of genuine placebo trials (VERTIS CV, ODYSSEY, lixisenatide)
    and was discarded.
- **V1.1 recall cases** (26f6cc4f): DEFINE-HF and EMPERIAL-Reduced.

## SGLT2 HHF in CVOTs (Zhang 2020)

- **Overlap:** SUBSET, all 4 of our trials shared (this branch had served 2 since before round 3).
  - EMPA-REG is cited through a NEJM correspondence whose title equals the trial's own title.
  - CANVAS is cited through Rådholm 2018, whose own PubMed record registers NCT01032629, a registration named by our
    report-only CANVAS Program family.
  - Both routes bind only to exactly one family, and an unlinked cited item is disclosed.
- **COMPARATOR_ARM_REVERSAL:** Zhang's plot prints EMPA-REG as 95/4,687 vs 126/2,333. EMPA-REG's own held report
  (pmc_26819227) prints 126/4,687 vs 95/2,333. Our EMPA-REG HR (0.65) is unchanged.
- **Positive controls** (DerSimonian-Laird, used only for published-analysis reproduction):
  - as printed: 0.6262 (0.5328–0.7359), I² 73.6%;
  - corrected: 0.6951 (0.6444–0.7497), I² 0.
- **Input types:** Kosiborod 2017 is a `POOLED_ANALYSIS` (quoted from its own record).
- **Setting vs outcome:** SIMPLE and EMPA-HEART are now X-SETTING. A background sentence never establishes a CVOT;
  only a title or a primary-outcome sentence does (labelled protocol erratum).
  - This also resolves the round-4 hold-out: the comparator-named candidates for this topic are now committed, and
    Kosiborod 2017 is refused as X-SETTING.

## MRA HFrEF (Zhang 2025, Frontiers)

- **Governing analysis:** Figure 4D (HFrEF all-cause mortality): RALES, EPHESUS, EMPHASIS-HF. The comparator's 9
  trials are not our target. OVERLAPPING, shared 2 (RALES, EMPHASIS-HF).
  - EPHESUS (acute post-MI LV dysfunction) is X2 by our protocol: a scope difference, not a missed trial.
  - J-EMPHASIS-HF (ours) is not in Figure 4D.
- **Membership:** the comparator's Table 1 transcribed (`comparator_table_spec.json`). RALES binds through the
  comparator's own prose citation (`RALES (...) ( <xref rid="B1"> )`, reference B1 = PMID 10471456): a pre-registration
  trial has no acronym in our records, so its name cannot bind it. New alias type `cited_name_span`, validated in
  `harness/comparator_panel.py`.
- **Generic inverse-variance rows** (`harness/comparator_analysis.py`): Figure 4D prints log[HR] and SE, not counts.
  Each row's printed HR/interval and weight are checked from log[HR] and SE, and the rows' common effect against the
  printed total, to the plot's own precision. The figure is held (CC BY 4.0).
- **Positive control:** FE inverse-variance through our engine: HR 0.782269 (0.717895–0.852414), Q 3.530321,
  I² 43.35%, exact. It controls the engine; one of its three rows is outside our population.

## Statins older adults (Huang 2022)

- **CONDITION_AS_OUTCOME** (`harness/condition_role.py`). PREVENTABLE (NCT04262206) was X2 because its registry
  conditions list "Dementia", which is what it aims to prevent: its own exclusion criteria refuse "Dementia
  (clinically evident or previously diagnosed)".
  - A population_none term is a prevention target only when an exclusion criterion names the registered condition
    itself, unqualified, no inclusion criterion names it, and the title does not.
  - `population_witness` never reads such a condition as a diagnosis.
  - Over all 32 topics this changes one decision. The first, looser versions matched qualified subsets ("diabetes
    insipidus", "metastatic breast cancer") and were tightened before landing.
  - PREVENTABLE is eligible, ongoing (RECRUITING), and has no results: no pooled input.
- **Root cause found on the way:** `design_key.registry_designs` stored each ctgov record object and then `update()`d
  it with the cached AACT design row, overwriting the record's own `id` with the design-row id. Any included
  registry-only record then lost its NCT, and PREVENTABLE was labelled "completed".
  - Fixed with a copy.
  - With registry records intact, `identity` unioned registrations on acronyms alone (PAPERS NCT04906720 +
    NCT06731595) and relabelled 271 registry rows. A registry record's family is now its own registration, which
    restores every served label.
  - STAREE-HEART's role is now read from its own title ("Heart Sub-study": secondary). The HM3 pinned control
    admits exactly these declared differences.
  - On the pinned pages, 20 included registry records now show their real AACT status (for example NOT_YET_RECRUITING) instead of the
    "completed" fallback.
- **Parent registration** (`harness/parent_registration.py`, `cache/<slug>/parent_registrations.json`).
  - JUPITER's older-adults report (20404379) is NCT00239681, located in the report's own text and in the held
    registration.
  - ALLHAT-LLT's report (30251369, ALLHAT NCT00000542) is the same class but is not linked this round. With the link,
    `pipeline._dedup` collapsed it into ALLHAT's other report (28531241) and it vanished from screening, with no row
    saying so. The link waits until that collapse is disclosed.
  - The recovery panel no longer calls a blank AACT link "unregistered / pre-registration-era".
  - Family ledger: contributing 2 of 26, pooled 2, matching the pooled k of 2. NCT00239681 is disclosed as
    contributing without established structural eligibility (its AACT arm rows are not in this topic's family
    registry).
- **Comparator:** Huang 2022 is observational; shared RCT inputs: none.
- **RCT checkpoint:** Ridker 2017 (JUPITER + HOPE-3, aged ≥ 70), expected 0.7441 (0.6053–0.9147).
  - The letter is not held: it is not in PMC, and the publisher answers with a bot check, which was not bypassed.
  - So the control is PENDING_SOURCE and is never run from memory.
  - Its HOPE-3 ≥ 70 stratum is a discovery case, recorded in the labelled protocol erratum (7eb31d5e).

## Round 7b: the three statins fixes as harness code (regex first; a model only as a gated proposal)

- **Plants:** `scripts/plants_round7.py` builds each defect's input and runs it against a chosen harness. On the
  pre-fix harness (a sparse worktree of `1801d205`) all 8 fire; on this harness none fire
  (`round7_plants.json`, and a test re-runs the HEAD side).
- **CONDITION_AS_OUTCOME** (`harness/condition_role.py`, regex on the eligibility criteria).
  - Corpus: 1 of 28 X2 exclusions of registry records that rest only on a registered condition was a prevention
    target (PREVENTABLE). The population is the served screening at the pre-fix commit (`condition_role_sweep.json`).
  - Of the other 27: 9 have an inclusion criterion naming the condition (it is the entry population), and 2 have an
    exclusion that names it only qualified. 16 have criteria that never mention it, so the regex cannot decide.
  - Those 16 went to `gpt-6-astra` as recorded calls (`scripts/condition_role_proposals.py`; verifier
    `model_source.verify_condition_role`). All 16 pass the verifier and all are PROPOSED; the queue never enters a
    build.
  - The model agrees with the rule on 9, says NOT_STATED on 5, and disagrees on 2, each needing an individual
    countersignature: probiotics NCT02817165 ("acute diarrhea") and colchicine NCT05726019 ("postpericardiotomy").
- **Parent registration** (`harness/parent_registration.propose`, regex SELF_ANALYSIS plus exactly one held
  registration). The links file is generated (`scripts/parent_registrations.py`), never hand-written.
  - Corpus: 13 reports name themselves an analysis of a named trial and carry no registration.
    - 1 LINKED: JUPITER, NCT00239681.
    - 3 WITHHELD_SAME_REGISTRATION: two SELECT reports and one PARADIGM-HF report. Another report already holds that
      NCT, and the same-registration de-duplication would fold them in silently.
    - 9 UNRESOLVED: no held registration carries the name.
  - A generic abbreviation never links. A first version linked "subgroup analysis of subjects with AAD" to a
    registration whose acronym is AAD; it was tightened before landing.
  - Recovery panel: 1 of 20 missed "no registry link" reports is registered through a parent.
- **RCT checkpoint** (`harness/positive_control.py`).
  - A non-randomised comparator is typed from its own abstract: 1 of 32 topics (statins). That topic has an
    RCT_CHECKPOINT, which renders on its page.
  - A PENDING_SOURCE control must carry recorded requests on every route (`scripts/positive_control_acquire.py` →
    `registry/positive_control_acquisition.json`). A route reporting open full text makes it un-acquired and refused;
    a failed request is not evidence.
  - Ridker 2017: not in PMC; not open access in Europe PMC; the publisher returned a Cloudflare bot check (not
    bypassed).

## Round 8: ticagrelor-ACS and tocilizumab-COVID, as harness code

- **Plants:** `scripts/plants_round8.py`. All 7 fire on the pre-fix harness `a838d818` and none on this one
  (`round8_plants.json`).
- **D5 registered-outcome identity** (`harness/rob2.py`). Death from vascular causes is typed as CV death; an outcome
  ABOUT bleeding is typed BLEEDING; TIA is a component (ASCEND's serious vascular event is not 3-point MACE).
  - A match now yields identity → timing → judgment, never an automatic "low". Timing needs the historical registry,
    the protocol or the SAP.
  - Corpus (`d5_identity_sweep.json`, 99 served D5 signals at `a838d818`):
    - false reassurance 1 of 74 served matches: PLATO, whose CV composite had "matched" Non-CABG major bleeding;
    - false concern 1 of 25 served non-matches: PHILO, whose registered MACE was missed.
  - The caches were re-derived for D5 ONLY (`scripts/rob2_rederive_d5.py`, 78 trials). `rob2_build.py` would also have
    refreshed D1–D4 on 10 trials from drift since their last build, a different change, not made here.
- **Comparator wording** (`harness/term_normal.py`). Hyphens are read as spaces, and an abbreviation is expanded only
  where the record defines it AND the expansion is a comparator term.
  - Corpus: 1 of 145 served X3 "no eligible comparator" exclusions flips (Talaschian 2024). It adds no mortality input:
    its HR is for clinical improvement.
  - A first version also expanded "AAD", which pushed "without" out of the negation window and passed a non-randomised
    "patients without AAD" control. It was tightened before landing.
- **Nested reports of one trial** (`harness/comparator_nesting.py`). Tan 2017 Figure 4 pools Wallentin 2009 (PLATO,
  18,624) and Cannon 2010 (PLATO planned-invasive, "13 408 (72.0%) of 18 624"): DUPLICATED_POPULATION. Report
  overlap 2, trial overlap 1 (PLATO); OR vs HR is not like-for-like.
  - Corpus: 1 of 18 comparators whose rows resolve to registrations has two rows of one registration.
- **REACT (tocilizumab):** the class count is 27 (held abstract); the drug count, 19, is VERIFIED_NOT_HELD (free PMC
  page, no open licence, body sha256 recorded). Figure 1 was read from the image.
  - PreToVid's row is day-30 (TIMEPOINT_EXCEPTION).
  - ImmCoVA's 2023 paper was already analysed in 2021 (ALREADY_ANALYSED).
- **Positive control:** FE log OR over 16 estimable trials → 0.825251 (0.742354–0.917405), I² 3.34%, exact.
- **No membership by date** (`harness/date_membership.py`, gated). Corpus: 0 of 32 served pages carry such a claim.
- **Codex (recorded, gated, never admitted):**
  - D5 identity: 942 pairs × 2 readers; 853 and 852 agree with the rule.
  - Comparator arm: 145 × 2. The substantive disagreement is 25 items where both readers see a comparator the rule
    excluded; several are protocol questions the model cannot see (e.g. metformin's placebo requirement vs
    "clomiphene alone").
  - Condition role: 16 × 2; 15 of 16 agree between readers. Both readers read a prevented outcome for probiotics
    NCT02817165 and colchicine NCT05726019.
  - Trial identity: 443 row pairs × 2. Both readers name exactly one same-trial subgroup pair, Cannon 2010 inside
    Wallentin 2009, the pair the rule proves, and no other; the rest are DIFFERENT_TRIALS or NOT_STATED (no held
    report for the row).
  - Every disagreement is an individual-countersignature item.
- **GRADE hold (needs your countersignature):** ticagrelor's risk-of-bias downgrade (1) rested on PHILO's false D5
  concern. With PHILO's registered MACE found, the computed downgrade is 0.
  - A served downgrade is not removed unsigned, so it is HELD at 1 (`registry/grade_holds.json`, rendered with its
    reason; `harness/grade.py::_held`). It lifts only when the hold is countersigned.
  - `tests/test_grade_missing_is_not_favourable.py` still guards every other page.
- **Ticagrelor overlap stays NOT_ENUMERABLE.** Figure 4's rows bind PLATO (twice) and DISPERSE-2 / Hansson. Liu 2014
  (Chinese Journal of Gerontology 2014;(10):2638-41) has no PMID or DOI, so by typed identity it cannot be ruled out as
  PHILO.
  - A reference year is never used to exclude it: that would decide membership by date.
  - Shared is at least PLATO; your "shared = 1" is consistent with it but not provable here.

## Round 9 (G1: trial-for-trial match): comparator memberships from the comparator's own words

- **Codex task `comparator_membership`**, blind, 2 readers, recorded and gated. For each of 12 comparators with an
  included-trial table but no membership for OUR outcome, which table rows are in its analysis of that outcome, each
  with a quote located in the held text (`model_source.verify_comparator_membership`).
  - Both readers named the same rows on 10 of 12.
  - They disagree on colchicine-secondary (reader 1 used subgroup sentences, not the main MACE analysis) and omega-3
    (reader 2 names none). Neither names rows for melatonin.
- **Bound after my check:** a new text-membership kind in `harness/comparator_analysis.py`. Each row names its panel row
  and a quote located in the held full text or JATS, with no per-row numbers.
  - Six topics are bound: colchicine-postop-af (9), colchicine-recurrent-pericarditis (3 of 5: COPE, CORE, CORP, the
    secondary-prevention analysis), finerenone (2 of 4), IV iron (5), probiotics (42), statins (8 of 12).
  - Esketamine, GLP-1 and balanced crystalloids already carried a per-outcome panel binding. A second membership emptied
    their sets (the endpoint labels disagree), so it was removed, and a test now refuses the combination.
  - Codex names 8 GLP-1 CVOTs in MACE; the served binding has 7. Worth a look.
- **Relations:** recurrent pericarditis is now compared on 3 trials (OVERLAPPING, shared 1), statins on 8 (DISJOINT).
  No pooled result moved.
- **Codex task `comparator_trial_names`** (6 comparators with no trial table). Both readers name the same 6 trials for
  dapagliflozin HFpEF, but our pool there is empty. Empagliflozin and tranexamic acid are single-reader only. All are
  PROPOSED.

## Round 10 (G1): the GLP-1 CVOT comparator is compared on its own MACE analysis, ELIXA included

- **The defect.** Giugliano 2021 (PMID 34526024) pools all eight CVOTs on MACE. The Fig. 3 caption reads "Forest plots
  of meta-analysis of the eight CVOTs with GLP-1RA on MACE", overall HR 0.86 (0.79-0.94).
  - The panel binds our outcome to "3-point MACE". ELIXA's own endpoint is 4-point MACE, so the per-row binding dropped
    ELIXA from THEIR analysis.
  - The page said SUPERSET ("every comparator trial is in our pool"). That is false: ELIXA is in their pool and not in
    ours.
- **The fix is harness code** (`harness/overlap_relation.py::_members`). When the comparator's governing-analysis
  membership is bound, its label is the expected endpoint. Before, the per-row binding took precedence, and beside a
  membership it always emptied the set.
  - This is the conflict round 9 worked around by removing the GLP-1 membership. It is now fixed at the source, and the
    round-9 guard test is replaced by an assertion that the bound k equals theirs_k.
- **Plant** `scripts/plants_round10.py` (`round10_plants/`):
  - On the pre-fix harness (f7c4e5b2), Q1 FIRED: all 8 members out, 0 in.
  - On the fixed harness, it does not fire.
  - Control C1 (no membership, so the per-row binding still excludes ELIXA) passes on both harnesses.
- **Membership**: `cache/glp1-ra-mace-t2d/comparator_analysis.json`, a text membership of 8 rows, each quoting the
  located Fig. 3 caption.
  - It is proposed blind by both codex readers (`comparator_membership`, both name the same 8) and bound after my read.
- **n of N**: 3 topics carry a per-outcome endpoint binding.
  - glp1: wrong, ELIXA dropped.
  - balanced crystalloids: right. Both readers also exclude Ratanarat 2017, which reports no mortality.
  - sacubitril: not applicable, a network meta-analysis.
  - Wrong in 1 of the 2 where the binding applies.
- **Result**: GLP-1 moves from SUPERSET (ours 8, theirs 7, shared 7) to OVERLAPPING (8, 8, 7). Only theirs: ELIXA
  (NCT01147250). Only ours: SOUL (NCT03914326, 2025).
  - No pooled result moved. Families 32/32 byte-identical. No other relation changed.
  - Our exclusion of ELIXA is our own eligibility decision (4-point MACE). This round does not change it.

## Round 11 (G1): the conditions the HFpEF withdrawals named, as harness code

The dapagliflozin and empagliflozin HFpEF pages were withdrawn on 2026-09-19 (Mahmood's decision). Both served a
cardiovascular-death-only registry measure as the composite primary. The notices name what must land before a
corrected estimate may be served. This round builds those conditions. **It does not lift either withdrawal.** That
needs Mahmood's countersignature and its own correction record.

- **Found first by execution.** Dropping the withdrawal on the pre-fix harness (41239b94) re-serves the same wrong
  number, HR 0.88 (0.74-1.05), CV death only, classed EXACT_TARGET. The topic's name still read as
  {cardiovascular death}: the notices' two conditions were necessary but not sufficient.
- **Four defects, four plants** (`scripts/plants_round11.py`, all built from held registry data). All fired on
  41239b94 (`round11_plants/prefix_41239b94.json`); none fire on the fix.
  - Controls hold on both: the served PARALLEL-HF row stays at 1.0881, and DELIVER's full-population measure stays at
    0.82.
  - Q1 (vocabulary): "worsening heart failure" was unread, so the composite's target was {CV death}. It is now a named
    component, met by an HF hospitalisation and/or an urgent HF visit.
  - Q2 (subpopulation): DELIVER registers its primary twice. The second is "for LVEF <60% Subpopulation" on 2200/2172
    of 3131/3132, and both are labelled "Full analysis set". It was served (0.83) when listed first. A measure is now a
    subpopulation when its title says so, or when it extends a sibling measure's title with every arm's denominator
    smaller. It is disclosed among the candidates and never selected.
  - Q3 (interval level): EMPEROR-Preserved's registered primary is HR 0.79 at a 95.03% alpha-adjusted level. It was
    rendered and pooled as a 95% CI. A registry interval is now read only at a stated, two-sided 95%. A level that is
    not stated is not assumed.
  - Q4 (array order): with PARALLEL-HF's component analyses listed first, the CV-death HR 1.1701 was taken. Analyses
    are now chosen by identity: one whose own label names a strict component subset of the target is a component
    analysis, and exactly one value must remain.
- **The withdrawal's own history is pinned.** Once the selector reads the composite, the withdrawn row's
  `withdrawn_effect` ("what was published") would have been recomputed as 0.82 and 0.79, restating the history as the
  corrected number. `tests/test_result_withdrawn.py` already asserted 0.88/0.91; it is the instrument that would have
  caught this.
  - The family cache is regenerated for these two topics only (`build_families.py --offline`). Their registry rows now
    classify against the composite: DELIVER's outcome row moves from the CV-death measure to the composite, and DAPA-HF
    gains an extractable worsening-HF measure. Nothing becomes poolable. The other 30 family caches stay byte-identical.
  - A first cut folded a bare "worsening heart failure" into HF hospitalisation for every target. That read
    "increase in diuretic dose due to worsening heart failure" as a hospitalisation, and 5 more family caches moved. It
    was caught by the offline family check before commit. For a target that does not name worsening HF, the words are
    now simply not a component, so those targets classify exactly as before.
  - Each topic's declaration now carries `published_row`, the served row verbatim. A test ties the pin to the number
    the signed notice quotes.
  - The corrected selection is disclosed as `selection_now` and is not served.
- **What a countersigned lift would serve**, from each trial's own abstract (EXACT_TARGET):
  - DELIVER: HR 0.82 (95% CI 0.73 to 0.92), 512/3131 vs 610/3132.
  - EMPEROR-Preserved: HR 0.79 (95% CI 0.69 to 0.90), 415/2997 vs 511/2991.
- **n of N** (held registry data, all topics):
  - Ratio analyses with a CI: 30 of 488 are not a two-sided 95% (95.02 to 98.7), and 0 are in a served pool.
  - Measures with more than one distinct ratio analysis: 93. Exactly 1 is in a served pool (PARALLEL-HF), and identity
    selection keeps it at 1.0881.
  - Names read as a single component although they name two: 3. Two are fixed here. NOAC "Stroke or systemic embolism"
    reads as {stroke}. It is left as found: adding "systemic embolism" to the vocabulary could move served NOAC rows,
    so it needs its own plant and a signed notice.

## Round 12 (G1): "Stroke or systemic embolism" is read as two components

- **The defect** (the last collapse the round-11 sweep named). NOAC's outcome "Stroke or systemic embolism" read as
  {stroke}, so a stroke-only measure matched the composite EXACT.
- **Plant** `scripts/plants_round12.py` (`round12_plants/`):
  - On bb6f9b27, Q1 FIRED: components ['stroke'], and a stroke-only measure was EXACT.
  - On the fix, Q1 does not fire, and a stroke-only measure is NEAR_MATCH.
  - Controls: a measure naming both stays EXACT (C1); RE-LY's registered "Stroke/SEE" stays EXACT (C2); the English
    word "see" is never embolism (C3).
- **A first cut broke C2.** It read only the words "systemic embol-", so RE-LY's registered composite (it abbreviates
  systemic embolic event as SEE) lost its extractable status. The offline family check caught it before commit
  (`round12_plants/first_cut.json`). SEE is now read only beside "stroke" or in parentheses.
- **The family caches move the intended way** (noac and doac-vte only; 30 of 32 byte-identical):
  - NCT01924065's "Hemorrhagic Stroke" row no longer counts as an extractable "Stroke or systemic embolism" result.
  - A stroke-only registered outcome no longer counts as an exact registered match.
  - RE-LY, ROCKET-AF, ARISTOTLE and ENGAGE AF keep their composite rows.
- **The instrument had the same blindness in time.** `scripts/pooled_class_sweep.py` compared a historic ref's STORED
  row components (read by that ref's lexicon) with today's target. At 316d2e48 that manufactured "ARISTOTLE lacks
  systemic embolism" although its own definition span names it.
  - Rows are now re-read from their stored definition span with the lexicon in force, and the difference is reported as
    `lexicon_drift`, never as a missing component.
  - A row with no stored components (a trial-defined composite, an unbound row) is not re-read: that would invent a
    comparison the producer never made.
  - At 316d2e48, C2 is exactly the three true rows (DELIVER, EMPEROR-Preserved, ODYSSEY). The served state must have
    zero drift, which `test_the_served_state_has_no_lexicon_drift` asserts. That test failed before this rebuild and
    passes after it.
- **n of N**: held records mentioning systemic embolism are in 2 topics (noac, doac-vte). Served pooled rows whose class
  changes: 0. No pooled result moved.

## Round 13 (Mahmood, 2026-09-29: "use codex. hard"): the registry-match paired plant, screening normalisation, overlap identity

Every codex call is a recorded `reproducible_ai` record, and every reading is a PROPOSED queue entry
(`registry/model_proposals/`). Two blind readers are used throughout (gpt-6-astra, then gpt-5.5 on the same frozen
population). Nothing a model says enters a build.

### 1. The registry-match paired plant (D5), as harness code

- **Readers**: `d5_identity_v2` + reader 2, 942 (pooled outcome, registered outcome) pairs from the round-12 served
  pages (834c6d83). The two readers agree with each other on 929 pairs. Against the rule in force they disagree on 83:
  43 false reassurance (rule SAME, both readers DIFFERENT) and 40 false concern (rule DIFFERENT, both SAME).
- **Root causes, each a plant** (`scripts/plants_round13.py`, texts copied from served registry rows). All 12 fire on
  834c6d83 and none on the fix; 7 controls hold on both.
  - All-cause death in other words: "all causes mortality", "death from any cause", and "all deaths" only as a
    composite member, never the adjudication sentence "All deaths … were adjudicated". All-cause hospitalisation is a
    component.
  - Worsening HF: a named component, as in round 11. HF hospitalisation and urgent visits fold into it only when the
    pooled outcome names it; otherwise "worsening of HF in outpatients" stays an EXTRA component (PARALLEL-HF's triple
    composite). An urgent HF visit is a component.
  - Systemic embolism, including RE-LY's "SEE" beside stroke; major bleeding as a member of a composite.
  - CV death as "CV-related death" (TECOS) and "fatal cardiovascular diseases"; cardiac interventions (PCI, CABG) as
    revascularisation.
  - "Heart-failure hospitalization": the hyphen hid it, as did the plural "HF hospitalizations".
  - Recurrent DVT alone and recurrent PE alone are their own components, never the recurrent-VTE composite. The measure
    TITLE decides the VTE components, not the description's adjudication boilerplate ("All suspected recurrent VTEs
    … were evaluated", which made an ACS measure "recurrent VTE").
  - Atrial fibrillation as the outcome, read only when nothing else is named (in stroke-prevention texts AF is the
    population).
  - British spellings folded before a text comparison (diarrhoea, haem-, oedem-, hospitalis-), each named pair, never a
    character class.
  - A registered measure of another kind (severity, duration of the condition, an average, "without" / "excluding" a
    cause) is not the pooled outcome by words. "Duration of the study / treatment / follow-up" is not such a measure.
- **n of N** (942 pairs, both readers): disagreements with the rule go from 83 to 25 (false reassurance 43 → 9, false
  concern 40 → 16), with **0 created**; the rule's decision changes on 60 pairs.
  - Two cuts were corrected on the way, each caught by this n-of-N before anything was built.
  - An "episodes / time to" guard reversed readers' SAME on first-event outcomes.
  - Typing cardiac arrest would have moved COLCOT's served D5, which no reader asked for. It is deliberately left untyped.
- **Served D5** (`scripts/rob2_rederive_d5.py --write`; D1–D4 untouched): 20 trials' D5 objects change, and only 2
  change level. Each was read by hand.
  - colchicine-secondary 39555823: "not assessed" → "some concerns". It had matched a registered co-primary "CV death,
    new or worsening HF, recurrent MI, or stroke" as plain MACE. False reassurance, corrected.
  - sacubitril PARADIGM-HF 25176015: "some concerns" → "not assessed". The hyphen hid HF hospitalisation, so the
    registered primary looked unregistered. False concern, corrected.
- **Left, and why**: the 25 remaining disagreements are listed in `round13_codex/d5_remaining.json`.
  - Pericarditis "Recurrence rate at 18 months" and semaglutide %-change vs kg-change: a text rule cannot settle these
    without the topic.
  - The trial-defined kidney composites: no canonical set exists.
  - HF hospitalisation inside a registered secondary composite: a deliberate design rule (`SECONDARY_COMPONENT_SUBSET_ALLOWED`).
  - The embedding matcher's own matches (CORP's "tamponade / constrictive pericarditis") are not changed here.
- **GRADE**: the sacubitril risk-of-bias downgrade would go from 1 to 0 (PARADIGM-HF was its only "some concerns"). A
  served downgrade is never removed unsigned: it is HELD at 1 in `registry/grade_holds.json` (OPEN), with the computed
  0 disclosed beside it. colchicine-secondary's downgrades are unchanged. No pooled result moved; families 32/32.

### 2. Screening normalisation: two blind readers on the k-gap lane's 55 exclusions (+ its 28 X1s)

- **`screen_eligibility`**: the population is `origin/acq/k-gap@a9b2b12b:outputs/k_gap/screen_audit.json`, every row
  with a screening rule (55). Each item carries the question, the protocol terms and the rule's own reason; the held
  text is the record alone.
  - Both readers: FAILS 30, MEETS 16, NOT_STATED 4, split 5.
  - They independently confirm the lane's 5 probiotics condition-as-outcome flips.
  - They confirm 3 of its 4 hand-found vocabulary gaps (Nidorf "stable coronary disease", Burr 1989 "men who had
    recovered from MI", Burr 2003 "men with angina").
  - New: an X1 miss (Wu 2020, "prospective, randomized, controlled study"), a comparator miss (PCOSMIC, "placebo
    ('standard care')"), 4 H. pylori-eradication probiotic trials whose abstracts DO name antibiotic-associated
    diarrhoea, and the COPPS POAF substudy.
  - Neither reader contradicts a single protocol scope or design exclusion.
- **`screen_x1`**: 28 of the 30 seeded reports X1 excluded (`origin/acq/k-gap@e1e7d3e4`, records from its
  `member_records.json`).
  - Both readers: not randomised 12, not stated 8, randomised 4, split 4.
  - Of the 4 "randomised", 2 are X1 misses (metformin 16764619 "randomly divided", 19892338 "randomly allocated").
  - The other 2 are pooled analyses of RCTs: X1 is right and the readers over-call them.
- **Handoff** (read from origin, never pushed to acq/k-gap): `evidence/v101_integrated/round13_codex/
  screen_eligibility_for_kgap.json` and `screen_x1_for_kgap.json`, each row carrying both readings, quotes and record
  ids. A flip changes screening and so k, which is a served change that needs a signature. Nothing is applied here.

### 3. Comparator trial-identity overlap

- **`overlap_identity`**: 93 pairs. Every SHARED member against the family it binds to (rule SAME_TRIAL, 47), and every
  only-theirs member against every only-ours family (rule DIFFERENT_TRIALS, 46: a missed match would hide there). Each
  item shows the cited reference's article title and our reports' titles.
  - The readers agree with each other on 90, and with the served relation on all 90: no false shared trial and no
    missed match.
  - 9 readings were refused by the verifier (a quote not located) and are not counted.

### 4. A third reader on what is still contested (D5)

- **`d5_adjudicate`**: gpt-6-astra at HIGH effort, blind. It reads the 38 pairs still contested after the fix: the 25
  where both readers disagree with the rule, and the 13 where the two readers split.
  - It sides with the first two readers on all 25.
  - On the splits, the three-reader majority is with the rule on 10 and against it on 3.
  - So 28 pairs are left with a three-reader majority against the rule, listed with every reading in
    `registry/model_proposals/d5_adjudicate.json`. They are captain items: most are the classes named above (a topic
    needed; a trial-defined composite; the deliberate HHF-subset rule).
- **Codex calls this round**: 69 recorded model calls (`registry/model_calls`). Every one is logged in
  `evid2-scratch/codex/codex_calls.jsonl`; no transcript is committed.
