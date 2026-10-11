# G1 binding lane → Captain (lane v3): 4 topics where trials are missing or disagree

**Branch.** `g1/binding-4topics`, based on acq/k-gap `f34580f90` + g1/confirm-unverified. Code + typed findings only.
**Trackers are not regenerated.** The captain regenerates.

**Source order, as asked.** AACT posted results, then the trial's own held open text (PMC OA / Unpaywall / abstract),
then SECONDARY_SINGLE.

**Model calls.** One recorded `codex exec </dev/null` call per trial, concurrency 3, through the EXISTING
table-location machinery.
- The same prompt, schema, recorder, runs ledger and `harness.secondary_meta.gate_table_location`
  (`scripts/g1_binding_locate.py`).
- **Anti-circularity:** the comparator's numbers are never shown to the model.
- **Names:** every name in this report carries a rule and a span.

## n of N per topic (the named trials)

| Topic | Named trials | New verified rows | Typed findings | Blocked (named) |
|---|---|---|---|---|
| colchicine-secondary-cv-prevention | 8 (O'Keefe, Deftereos ×2, Hennessy, Mewton, Shah, Akrami, Tong) + COLCOT check | **0 of 8** | COLCOT F1 | 8 (below) |
| melatonin-primary-insomnia-sol | orientation (Wade [22] + 14 MD rows) | n/a | **F2 on 15 of 15 MD rows; F3 on Wade [22]** | — |
| esketamine-trd-madrs | Trial B, Trial E | **0 of 2** | Trial B F4, Trial E F5 | 2 |
| corticosteroids-cap-mortality | 7 NO_ROW | **0 of 7** | — | 7 |

## Findings (scripts/g1_binding_findings.py, outputs/k_gap/g1_binding/findings_*.json, 13 plants)

### F1, COLCOT (Tardif 2019, NCT02551094): "lands on the other side of no difference"

| | Value | Interval crosses 1? |
|---|---|---|
| Ours (the trial's primary composite) | HR 0.77 (0.61–0.96) | no |
| Comparator | RR 0.81 (0.64–1.03) from 114/2366 vs 141/2379 | yes |

**AACT 2026-08-30 posted results decide it.** The comparator's counts equal, in both arms, the SUM of three separately
posted outcomes:

| Posted outcome | Colchicine | Placebo |
|---|---|---|
| Cardiovascular Death | 20 | 24 |
| Myocardial Infarction | 89 | 98 |
| Stroke | 5 | 19 |
| **Sum = the comparator's row** | **114** | **141** |

The trial's own posted first-event composites are 131/170 (the PRIMARY) and 111/130 (CV death / arrest / MI / stroke).
Summed components count a patient with two events twice. **Our row stands; the comparator's row is not the trial's
composite.**

**Rule detail.**
- Arms are matched by posted N.
- Components are restricted to the trial's own declared components (topics/*.json trial_annotations). The real posted
  outcomes also hold a COINCIDENTAL decomposition (total death + angina + VTE + AF = 114/141), which the restriction
  excludes.
- Asserted only when the decomposition is unique.

### F2 + F3, melatonin: ours −17.4 vs theirs +11.2. **Neither sign is wrong.**

**F2: the conventions are mirrored.** The comparator (PMID 23691095) states its direction itself:
- "mean improvement in sleep onset latency";
- "efficacy in reducing sleep latency (weighted mean difference (WMD) = 7.06 minutes [95% CI 4.37 to 9.75])".

So a positive value means a reduction with melatonin, i.e. placebo minus melatonin. Ours is intervention minus control
(`harness/secondary_meta.py`: `md = mean_t - mean_c`). This holds for all 15 MD rows of the comparator. Any sign
comparison must mirror one side.

**F3: the magnitude gap is a different report of the same trial.**

| | Row label / report | PMID | Population |
|---|---|---|---|
| Comparator | "Wade AG, 2011 [21]": Curr Med Res Opin 2011, age cut-off analysis | 21091391 | 18–80 cohort and subsets |
| Ours | BMC Med 2010 | 20712869 | 65–80 subgroup, 3 weeks |

Both PubMed DataBank lists name **NCT00397189**: one trial, two analyses. The 17.4 vs 11.2 gap is a population /
report difference, not a value error.

### F4, esketamine Trial B (TRANSFORM-1, NCT02417064)

- **Registry:** 2 EXPERIMENTAL arms (56 mg, 84 mg) and 1 comparator.
- **Posted contrasts:** LS-mean (MMRM) 56 mg −4.1 (−7.67, −0.49) and 84 mg −3.2 (−6.88, 0.45).
- **Comparator:** −5.00 (−8.10, −1.90), equal to neither.
- **Rule:** the harness refuses the trial by its own rule, `harness/ctgov_results.py` MULTI-ARM GUARD ("esketamine
  56 mg / 84 mg / placebo ... the CANTOS/TRANSFORM-1 class").
- **Estimand:** the posted values are MMRM, while the topic estimand is observed-case Day-28 raw change.
- **Blocked:** MULTI_ARM_UNRESOLVED.

### F5, esketamine Trial E (SUSTAIN-2, NCT02497287)

- **AACT designs row 227554268:** allocation NA, SINGLE_GROUP, masking NONE; one EXPERIMENTAL group.
- **Consequence:** no randomised comparator exists, so no between-arm MD can come from it.
- **Proposed name:** NOT_ELIGIBLE by design (rule: protocol requires a randomised comparator; span: the designs row).

## Blocked trials, each with its reason

**colchicine**

| Trial | Reason |
|---|---|
| O'Keefe (PMID 1593057), Deftereos (25) (23500260), Deftereos (19) (26265659) | Paywalled; abstract only; NOT_REPORTED by arm in the abstract; no AACT results. Deftereos (19) NCT01936285 posts nothing. |
| Tong (COPS, 32862667) | Abstract prints "24 events … 38 events" without N: gate REFUSED INCOMPLETE. |
| Hennessy (31284074) | Unpaywall copy held: NOT_REPORTED. |
| Mewton (COVERT-MI, 34420373; NCT03156816 posts nothing) | PMC OA held: NOT_REPORTED. Its primary is infarct size. |
| Shah (COLCHICINE-PCI, 32295417) | PMC OA held: gate REFUSED INCOMPLETE. AACT NCT02594111 posts "All-cause Mortality, Non-fatal MI, or TVR" at six timepoints; abbreviated "MI" does not name the topic outcome, and the timepoint is not chosen. The PubMed record lists TWO registrations (NCT01709981, NCT02594111). |
| Akrami (34876021, BMC CC BY) | Gate REFUSED RATIO_DIRECTION_CONTRADICTS_ARM_EVENTS: HR 3.52 (1.60–7.74) quoted against 8 vs 28 events. |

**esketamine:** Trial B (F4 / multi-arm), Trial E (F5 / single arm).

**corticosteroids-CAP:** all 7 trials are paywalled with no OA copy, and the abstract does not report deaths by arm
(NOT_REPORTED).

| Trial | PMID | AACT |
|---|---|---|
| Confalonieri | 15557131 | — |
| Marik | 8339624 | — |
| McHardy & Schonell 1972 BMJ (corrected: earlier mislabelled "Wagner 1956") | 4404939 | — |
| Snijders | 20133929 | NCT00170196, no posted results |
| Meijvis | 21636122 | NCT00471640, no posted results |
| Mikami | 17710485 | — |
| Blum | 25608756 | NCT00973154, no posted results |

**SECONDARY_SINGLE (sweep re-run, `--need=4`):**
- 0 new reads were due; all discovered metas' figures were already read or have no outcome figure.
- The read figures FAIL the self-reproduction gate, except one (PMID 30917856 Fig 2), whose rows are influenza
  observational studies; no join.
- The unread figure-only metas (colchicine 14, esketamine 10, corticosteroids 8) belong to the forest-reader lane
  (g1/forest-reader).

## Records

**Committed:** 13 of 16 new call records (evidence/model_calls/table_locator), plus the runs ledger. Their prompts hold
only PubMed abstracts, or a CC BY text (Akrami, BMC).

**Held locally, NOT committed:** 3 records whose prompts embed full texts under other or unclear licences. They are in
F:/claude-temp/held_records; the captain decides.

| Trial | Record |
|---|---|
| Mewton | mc-01fa07f5 |
| Hennessy | mc-9983ab25 |
| Trial B | mc-339ccd01 |

## Update (overnight, 5 Oct): all 29 unmatched in-scope trials of the 4 topics worked

### n of N: unmatched in-scope trials newly verified

| Topic | Newly verified | Matched before → after | Remaining blocked, named |
|---|---|---|---|
| colchicine-secondary-cv-prevention | **3 of 9** | 2 → 5 of 15 | Section below |
| melatonin-primary-insomnia-sol | **0 of 11** | — | All paywalled (abstract only); no AACT; sweep finds no outcome forest figure in the citing metas; 4 have no citing open meta |
| esketamine-trd-madrs | **0 of 2** | — | Trial B (F4 multi-arm rule), Trial E (F5 single-arm) |
| corticosteroids-cap-mortality | **0 of 7** | — | Paywalled; abstracts do not report deaths by arm; no AACT results |

### colchicine: the 3 new rows

| Trial | Value | How it binds (`scripts/g1_binding_bind.py`, deterministic) |
|---|---|---|
| **Shah 2020 (COLCHICINE-PCI)** | 30-day MACE 24/206 vs 25/194 | PMC OA Table 3 "Outcomes in patients undergoing PCI …". The header gives Colchicine (n=206) / Placebo (n=194), and the % equal e/N. |
| **Akrami 2021** | Total MACE 8/120 vs 28/129 | BMC CC BY Table 2 "Major clinical end points (ITT)". The N comes from Table 1's header for the identical arm labels (rule T3b, cited in the span). The row's printed HR 3.52 (1.60–7.74) contradicts its own counts and is NOT bound. |
| **Nidorf 2013 (LoDoCo)** | 15/282 vs 40/250 | Rule P1: the topic outcome is declared "Trial-defined …", and the abstract defines the primary as the composite of acute coronary syndrome / cardiac arrest / stroke. Arm-labelled "e of n (p%)". |

**Agreement with the comparator, computed:**
- **Nidorf 2013: DISAGREE.** The comparator's row 14/282 vs 48/250 is not the trial's own primary (15/282 vs 40/250).
- **Shah, Akrami:** the comparator prints no row for them.

**Measured.** A/B on the colchicine tracker, restored afterwards: k 2 → 5. All 3 are routed PRIMARY via
single_primary_source.

### Tracker hook

An OWN-TUPLE binding (the trial's own tuple, not the comparator's) may bind a NO_ROW trial. The comparator-keyed kind
still binds UNVERIFIED rows only (plant).

### Recorded codex locate (12 new calls, 29 replayed through gate_table_location)

0 accepted:
- NOT_REPORTED: 23.
- INCOMPLETE: 3 (events without N).
- Nidorf (13): OUTCOME_DOES_NOT_GOVERN_THE_NUMBERS. The P1 rule above binds it deterministically instead.
- Luthringer: MD 9 min without CI.
- Wade [28]: group means only.

**Records.** 23 are committed. 5 embedding non-CC-BY full texts are held locally and git-excluded.

### Still blocked in colchicine, each with its reason

- **O'Keefe, Deftereos ×2:** paywalled; the abstracts do not report it by arm.
- **Tong (COPS):** prints "24 events … 38 events": events, not patients.
- **Hennessy:** Unpaywall copy, NOT_REPORTED.
- **Mewton (COVERT-MI):** its primary is infarct size; MACE is not printed by arm.

## Update (5 Oct, later): statins-elderly and denosumab

### statins-elderly: G1 is unattainable against this comparator

- **12 of 12** of our observational rows are confirmed out of scope by their OWN abstracts: rule F6 scope audit
  (`scripts/g1_binding_findings.py`); the span is each abstract's design sentence (cohort / case-control).
- The comparator pools **0 RCTs**; its own abstract says "Twelve eligible observational studies". There are no
  comparator RCTs to identify.
- The 15 QRISK rows are table fragments, not trials.
- **Decision for the captain:** re-point this topic to an RCT comparator, or retire it from G1.

### denosumab: COMPARATOR_NOT_ENUMERATED, now enumerated

- **Source:** the comparator's OWN supplementary trial table (PMID 36852077, mmc1). Enumerated by
  `scripts/g1_binding_enumerate.py` (deterministic regex, 3 plants), output `enumeration_denosumab-vertebral-fracture.json`.
- **11** denosumab RCTs. **6** are in scope (placebo arm). **5** are named OUT_OF_SCOPE: COMPARATOR_NOT_PLACEBO
  (active control only; the span is the arm lines).
- **Identity:** each PMID is CONFIRMED by exact title + first author + year from the supplement's reference list.

| In-scope trial | PMID | NCT | Result |
|---|---|---|---|
| Cummings 2009 (FREEDOM) | 19671655 | — | **matched** |
| McClung 2006a | 16495394 | NCT00043186 | AACT posts only BMD/marker outcomes, no fracture outcome; abstract NOT_REPORTED |
| Bone 2008 | 18381571 | — | abstract NOT_REPORTED; no OA |
| Seeman 2010 | 20222106 | NCT00293813 | AACT posts XtremeCT outcomes only; Unpaywall copy held: NOT_REPORTED |
| Koh 2016 | 27189284 | — | PMC4951467 (CC BY-NC) held: NOT_REPORTED |
| Nakamura 2012a | 21927920 | — | abstract: "No new vertebral fracture was observed on spinal radiographs in either group." Named **ZERO_EVENTS_BOTH_ARMS**: no ratio is estimable; the gate refused NO_NUMBERS_COPIED. |

**n of N: 1 of 6 matched (FREEDOM). 0 of 5 newly verified.**

**Open.**
- Which in-scope trials the comparator actually pooled for vertebral fracture: its eFigure 5 is image-only (no text
  layer), so this is not assumed.
- The tracker carries N=0 for this topic until the captain integrates the enumeration.

**Records.**
- 3 new recorded calls are committed (abstract-only prompts).
- **Held, NOT committed** (F:/claude-temp/held_records, git-excluded):

| Trial | Record | Reason |
|---|---|---|
| Koh | mc-1450a895 | CC BY-NC |
| Seeman | mc-ad533f04 | Unpaywall, licence unclear |

## Update (5 Oct, 04:00): esketamine 2 of 2 named; cortico-CAP 3 of 7 SECONDARY_SINGLE

### esketamine: both trials named by NEW rules F7 / F8 (`scripts/g1_binding_findings.py`, 4 plants)

**Trial E: F7 COMPARATOR_ROW_CONTRADICTS_ITS_CITATION + F7-SCOPE.**
- The comparator's own Table 2 row reads "RW, double-blind maintenance after open-label induction/stabilization",
  primary endpoint "Time to relapse".
- The report it cites, [25] Wajs 2020, is the open-label SUSTAIN-2; AACT designs is SINGLE_GROUP.
- On either reading the trial is out of scope: the endpoint is not the topic's Day-28 MADRS. Proposed name: NOT_ELIGIBLE.
- **Bonus: Trial F** (SUSTAIN-1, NCT02493868), same F7-SCOPE (Time to relapse).

**Trial B: F8 COMPARATOR_DECLARED_ARM.** The comparator's regimen cell declares "Fixed-dose 84 mg"; its row is N 114/109.
Recomputed from the trial's posted observed-case Day-28 means (AACT outcome 258346928):

| Contrast | MD (95% CI) |
|---|---|
| 84 mg (−18.8, SD 14.12, n 98) − placebo (−14.8, SD 15.07, n 108) | **−4.0 (−7.99, −0.01)** |
| both doses combined (Cochrane Handbook 6.5.2.10) − placebo | −4.11 (−7.52, −0.69) |
| **comparator** | **−5.00 (−8.10, −1.90)** |

- DECLARED_ARM_VALUE_NOT_REPRODUCED.
- The topic's multi-arm rule still refuses binding; the captain may decide whether the comparator's own dose
  declaration resolves it.

### cortico-CAP: 3 of 7 newly verified as SECONDARY_SINGLE (k 3 → 6 of 11, A/B, tracker restored)

**Source.**
- PMID 42402602 (Crit Care 2026, PMC13613698), a dose network meta-analysis. **Not the comparator** (38128217).
- Per-trial deaths by arm are in its open supplementary eTable 4 (Europe PMC supplementaryFiles). The main-text tables
  of all 5 open CAP metas found are characteristics only.
- The supplement is CC BY-NC-ND: it is held gitignored, and only typed numbers + supplement sha256 are committed
  (`secondary_corticosteroids-cap-mortality.json`).

**Positive control** (`scripts/g1_binding_secondary.py` S2). The meta's own printed results are reproduced from its own
34 rows under its own printed rules, equal at printed precision:
- the rules: ≥ 7.5 mg/d dexamethasone-equivalent = higher dose; 0.5 for single-zero; double-zero excluded; τ² printed 0,
  so inverse-variance common effect;
- the results: higher dose RR 0.83 (0.74–0.92), lower dose 0.84 (0.75–0.95).

| Trial | Result |
|---|---|
| Marik 1993 | **1/14 vs 3/16** SECONDARY_SINGLE |
| McHardy & Schonell 1972 | **3/40 vs 9/86** SECONDARY_SINGLE (4-group trial: both steroid arms vs both non-steroid arms, as the meta combines them) |
| Blum 2015 (STEP) | **16/392 vs 13/393** SECONDARY_SINGLE |
| Confalonieri 2005 | refused ARM_N_INCONSISTENT_WITHIN_SOURCE (mortality control N 22; the same source's other rows 23) |
| Mikami 2007 | refused ARM_N_SWAPPED_WITHIN_SOURCE (mortality 16/15; other rows 15/16) |
| Snijders 2010 | refused SUBGROUP_SPLIT_ROWS (two '*' subgroup rows whose N sum is the swap of its other rows) |
| Meijvis 2011 | refused SECONDARY_OF_SECONDARY (the source's own data-source column: "Secondary source (Pitre 2025)") |

**Tracker hook** `apply_secondary_bindings` re-checks offline: not the comparator (PMID/DOI); control reproduced; binds
NO_ROW/UNVERIFIED only. Agreement: NOT_COMPARABLE (the tracker holds no comparator values for these trials).

**Correction.** PMID 4404939 is McHardy & Schonell 1972, not "Wagner 1956" as the earlier blocked table said.

## Update (5 Oct): denosumab comparator set reaches the tracker through k_gap_table (`99ed07c12`)

**Your refusal was right:** the tracker reads the comparator set only from k_gap_table, which said NOT_ENUMERABLE_OPEN.
Now:

**Input.** `registry/comparator_enumerations/denosumab-vertebral-fracture.json`:
- status **ENUMERATED**; enumerated_from = the comparator's own supplementary trial table (PMID 36852077, Europe PMC
  supplementaryFiles, typed text `cache/comparators/36852077/2026-09-29_kgap_supplements.txt`, sha256 e2b9205a…);
- 11 typed units: label, the comparator's reference number, CONFIRMED PMID, the row's arm lines verbatim as span,
  scope.

**k_gap_table.**
- New candidate source SUPPLEMENT_ENUMERATION in the existing unit schema → `comparator_set_state: ENUMERATED`,
  `enumerated_from` cited.
- The whole file is refused if the held source digest changes.

**Tracker.** Measured, offline k_gap_table for this topic + `g1_tracker.topic`:

| | Before | After |
|---|---|---|
| Comparator N | 0 | **11** |
| Eligible | 0 | **6** |
| Matched | — | **1 of 11** (FREEDOM) |
| Scope-citation violations | — | 0 |

**The 5 active-controlled trials are NAMED** PROTOCOL_SCOPE_DIFFERENCE, rule **E2:COMPARATOR_NOT_PLACEBO**: Miller
2016b, Brown 2009, Roux 2014, Recknor 2013, Kendler 2010.
- Span: the comparator's own row (active-drug arms only).
- Re-derived inside `cite_or_demote` (digest + verbatim span), so a tampered span is demoted.

**Performance fix.** `topic()` now ensures all comparator NCTs in ONE AACT pass. registry_binding re-read the snapshot
once per trial (> 1 h for this topic on the busy F:; 19 s once indexed).

**Plant.** `tests/test_g1_denosumab_enumeration.py` was written first; 3 tests failed before the change. All 230
g1/k_gap tests pass.

**Please regenerate** k_gap_table + the tracker on merge (I did not commit either output).

### denosumab: the 5 in-scope unmatched trials, fracture counts: 0 of 5 newly verified, each named

| Trial | Why no open count |
|---|---|
| McClung 2006a (16495394, NCT00043186) | Phase 2, 8 dose arms. AACT posts BMD/marker outcomes only; abstract NOT_REPORTED; paywalled. |
| Bone 2008 (18381571) | Abstract NOT_REPORTED; no OA copy. |
| Seeman 2010 (20222106, NCT00293813) | Held Unpaywall text mentions vertebral fracture only as baseline exclusion/assessment (deterministic grep), so NOT_REPORTED; AACT posts XtremeCT only. |
| Koh 2016 (27189284, PMC CC BY-NC) | 6-month double-blind phase; the held full text's AE table has no vertebral fracture by arm (deterministic grep + recorded codex: NOT_REPORTED). |
| Nakamura 2012a (21927920) | Abstract: "No new vertebral fracture was observed on spinal radiographs in either group". Zero events stated, but no arm N (226 randomised / 212 dosed across 3 doses + placebo). INCOMPLETE; the comparator's 157/55 cannot be the source (anti-circularity). |

**Open secondaries checked** (text layers): Front Pharmacol 2021 (PMC8080120), BMJ 2023 (PMC10152340 supplement
PDF), J Clin Med 2021 (PMC8305263 supplement PDF), Front Endocrinol 2026, Med Sci Monit 2022, Front Aging 2022. They
hold characteristics tables only; per-trial fracture counts are in forest images (forest-reader lane).

## Update (5 Oct): statins-elderly, comparator 32529863 adopted (COMPARATOR_NO_PER_TRIAL_ROWS)

**Decision.** Mahmood, 2026-10-05: "go with a".
- Recorded as a ratified exception to rule C6 (per-trial rows) for 32529863 only: `registry/comparator_selection/
  statins-primary-prevention-elderly.ratification.json`.
- The pre-registered rule (6713b9d17) and its 26-candidate table are unchanged. `selection.json` shows both results:
  NO_ACHIEVABLE_COMPARATOR under the rule alone, PICKED_BY_RATIFIED_EXCEPTION with it.

**Type** (`…adoption.json`, `g1_tracker.apply_no_rows_comparator`).
- k matching uses the comparator's result trial set.
- Every per-trial comparison is **NOT_AVAILABLE_FROM_COMPARATOR**; `comparator_data_confirmation: NONE`.
- RESULT_AGREES compares OUR pooled OR (DL), from our verified count rows for the same 7 trials, with its printed
  OR 0.88 (0.72–1.06). Until all 7 are verified it is OUR_ROWS_INCOMPLETE (unmet).

**Ledger.** `g1_denominator_ledger` kind COMPARATOR_RETIRED.
- 39076238 is retired **COMPARATOR_POOLS_NO_RCT**, spans verbatim in its held text: "A total of 12 observational
  studies incorporating 1,627,434 population were eligible for this analysis"; "Study design: observational study".
- The baseline's 27 statins rows (12 observational studies + 15 QRISK fragments) leave under it. The 7 new rows carry
  their enumeration spans.

**Enumeration.** The comparator's primary-prevention result sentence cites refs 29, 35–40 (7 trials). Each ref's own
PMID and title is the span (`registry/comparator_enumerations/…`). The typed enumeration precedes Table 1, which lists
all 16 trials, primary and secondary.

**Measured** (offline k_gap_table + topic): **comparator N 7, ENUMERATED; matched 1 of 7** (JUPITER ≥70, in our pool);
result OUR_ROWS_INCOMPLETE (0 of 7 verified count rows).

**Acquisition: 0 of 7 new verified rows.**
- **AACT:** NCT00000542 (ALLHAT-LLT), NCT00211705 (MEGA), NCT00327418 (CARDS) post no results; the others have no NCT
  (ISRCTN trials).
- **Open text:** ALLHAT-LLT (Unpaywall) and JUPITER (PMC). The other 5 are abstract only.
- **Recorded codex locate** (7 calls, concurrency 3), every result refused or not reported:

| Trial | Gate result |
|---|---|
| PROSPER | REFUSED: "primary endpoint" 408 vs 473, no arm N, generic outcome; whole trial incl. secondary prevention |
| HPS diabetes | REFUSED NON_NUMERIC: % reduction; 601 vs 748 events, no arm N |
| CARDS 65–75 | REFUSED NON_NUMERIC: % only |
| JUPITER ≥70 | REFUSED OUTCOME_NOT_NAMED: its table row "Primary end point" 75 vs 119; the topic outcome is not trial-defined, so a generic label cannot bind |
| ASCOT-LLA older, ALLHAT-LLT older, MEGA older | NOT_REPORTED |

- **Independent metas:** the open ones with per-trial rows (BMC 2026, Brugts 2009) report whole trials of all ages, or
  single outcomes, not the older primary-prevention composite. None is usable.
- **Records:** 5 committed (abstract-only prompts). ALLHAT-LLT (mc-bf1135de) and JUPITER (mc-e2d9b11d) are held locally
  (non-CC-BY text) in C:\mh-tmp\binding\held_records, git-excluded.

**Served notice queued for Mahmood.** `docs/reviews/statins-primary-prevention-elderly/review.json` still names
39076238 and was NOT edited. Changing the served comparator needs his signature.

## 2026-10-05 night — overnight Goal 1 run (Mahmood: "use it hard all night")

**Local recount (gates unchanged; false-positive classes fixed with plants). Two topics are G1_MATCHED.**

| topic (comparator) | matched | RESULT_AGREES | state | last step |
|---|---|---|---|---|
| esketamine (37377288) | 3 / 3 | yes: k2 pooled MD ours −4.24 (−6.73, −1.76) vs −4.18 (−6.00, −2.35) | **G1_MATCHED** | TRANSFORM-1 combined both dose arms (Handbook 6.5.2.10, AACT observed Day 28) |
| dpp4 (31462224) | 4 / 4 | yes: k3 pooled HR AGREE | **G1_MATCHED** | EXAMINE from the FDA NESINA label Table 12: HR 0.96 (98% CI 0.80, 1.16), re-expressed at 95% |
| melatonin (35691474) | 1 / 2 | **yes** (was no): Dawson −1.7 vs −1.70 | NOT_YET | Dawson mirrored by F2 (23691095 states positive = reduction); James 1990 open |
| denosumab (32492050) | 1 / 2 | yes | NOT_YET | Bone 2008 open |
| statins (32529863) | 1 / 7 | no (our counts 0/7) | NOT_YET | 6 open |

**Every open route tried for the remaining trials:**
- **James 1990** (melatonin):
  - AACT: none.
  - PMC/EPMC: no full text; no DOI.
  - Metas: 23691095 cites another report; 25380732 is qualitative only.
  - AHRQ evidence report 2004 (NBK37431, US government): NCBI served a reCAPTCHA, Europe PMC returned 403, and archive.ahrq.gov has no DNS. None was bypassed.
  - EMA Circadin/Slenyto EPARs: James is not named.
- **Bone 2008** (denosumab):
  - AACT NCT00091793: no fracture outcome.
  - JCEM text: not open.
  - EMA Prolia EPAR: study 20040132 is described (BMD, n 332) but no fracture counts are printed.
  - FDA BLA 125320 2010 medical, statistical and summary reviews: the study is not named with fractures.
  - Open metas citing it: 33195764 (its only fracture forest plot is bisphosphonate) and 42494861 (league tables, no forest plot). Both were refused at figure selection; no call was made.
- **Statins:** the earlier dispatch still holds. The only open meta citing the older-adult subgroup reports is the comparator itself (anti-circularity).

**For review (tracker changes, all with plants):**
- `refresh_same_trials_after_bindings`: the RESULT comparison was built before the binding hooks ran.
- `comparator_one_sided`: a comparator row with one bound is AGREE_ON_POINT, never DISAGREE, and is set aside by name.
- `ci_at_95`: a stated non-95% two-sided CI.
- `oriented_secondary_row`: F2 on a secondary meta.
- ARMS_COMBINED: C1–C6.
- The regulatory binder: R1–R4.

Commits: 6ef2a9eee, then the melatonin commit. g1 + k_gap suites: 278 pass. Nothing landed; no served number changed.

## Final-5, binding lane: "use codex hard" (2026-10-08 23:14 GMTDT, g1/final5-binding @ 2eb4cff58, cut from main 96921df40; FOR V11/V12)
Codex ran 8 recorded readers at concurrency 8 plus 3 review passes (r1a, r1b, and r2 running now). Every call is licence-guarded at call time; no non-CC text was shown to a model. Regex and table typing come first, and the recorded readers are independent second readers. Tests (subset): 1510 passed, 3 xfailed. The shared outputs were restored after the local recounts. **No served number changes.**

**Flip-relevant (local recount on this branch):**
- **corticosteroids-covid19-mortality: RESULT_AGREES is now MET.**
  - RECOVERY's own supplementary appendix, Table S2 (28-day mortality, ventilated subgroup), prints **95/324 v 283/683**. This is exactly the comparator's RECOVERY row.
  - It enters the same-trials comparison under D12 through a new kind, **K5** (a held document's table row). Same trials: OR 0.586 (0.442-0.779) v 0.59 (0.44-0.78), AGREE, BENEFIT. D2 share 1007/1263 = 79.7%, which passes.
  - Pristine main today: unmet ALL_ELIGIBLE_MATCHED + RESULT_AGREES. **What remains is ALL_ELIGIBLE_MATCHED only**: k-gap's CAPE COVID, REMAP-CAP hydrocortisone and Metcovid. Cortico flips once those 3 are matched or named.
  - Licence: the appendix is the PMC OA COVID licence (NEJM), **not CC**. It is held locally, git-ignored (outputs/k_gap/_supp/), pinned by pdf sha256 ba84d546..., and never in a prompt. Two PDF engines (poppler -raw, MuPDF) hold the identical row. **The captain's regenerating machine needs the local copy** (python scripts/g1_final5_typed.py --fetch). Without it, K5 is unused and fails closed, and cortico reverts to RESULT_AGREES unmet.
- **iv-iron-hfref-hosp: no flip possible** (FAIR-HF has no open source).
  - **D14 applied:** CONFIRM-HF Table 2 (CC BY) gives 10/150 v 25/151 patients (events 10 v 32). It enters as K5 matching counts with 2 recorded readers. The signed finding COMPARATOR_COUNTS_ARE_EVENTS is named in the tracker, verified at build, including verbatim unit spans.
  - **D15 applied:** EFFECT-HF 11/86 v 6/86 admitted in registry/g1_acquired as an own tuple. iv-iron same trials move from DIFFERENT_CONCLUSION to SAME_CONCLUSION_DIFFERENT_ESTIMATE (k=4, OR 0.775 v 0.610).
  - **But DIVERGENCES_NAMED becomes unmet:** EFFECT-HF is now a matched DISAGREE against the comparator's 13/88 v 13/86.

**Decisions needed (V12 questions, typed and ready):**
1. **D15 conflict (P0 from both codex review passes; both recorded readers raised it too).** The paper states "All-cause mortality and hospitalization for worsening HF and other cardiovascular reasons were analyzed for the safety set". The 11 v 6 are safety-set patients; the safety set is the FAS (86) plus 2 FCM patients, and its N is not printed. D15 as signed binds the FAS denominators 86/86. It is applied as signed and the caveat is carried on the row. **Re-present D15 with this caveat?**
2. **EFFECT-HF comparator side:** the comparator's 13 v 13 are the 26 worsening-HF **hospitalisations** ("26 of them for worsening HF (13 in each group) in 17 patients (11 patients on FCM and 6 on usual care)"), the same class as D14. Its 88 is the safety-set FCM N. It is staged as PROPOSED in registry/g1_signed_comparator_findings.json; signing it closes iv-iron DIVERGENCES_NAMED.
3. **CANVAS side (sglt2-pp):** the comparator's cited report, Radholm 2018 (CC BY; text plus Figures 1-2, read by 2 recorded readers), prints **no per-arm HHF counts**, only 5.5 v 8.7 per 1000 patient-years and HR 0.67. The comparator's 87/117 appear in no held source; 123/120 are in FDA review Table 30. The existing side rule cannot name a side. The rule-scope question (may it read a held regulatory report?) stands. Main's D12 has no K4 kind, so on main CANVAS stays a measure difference.

**NOT_FOUND, reported for the captain's ledger:**
- **ENGAGE (D16 C, AACT route): NOT_FOUND.** The ITT primary (outcome 258761856, high dose v warfarin) is posted as HR 0.87 with a **99%** CI (0.709-1.068). The 97.5% CIs are mITT/PP non-inferiority analyses. The 95% CIs belong to secondary outcomes (e.g. stroke/SEE/CV death 0.87, 0.786-0.959: a different outcome, REFUSED). Per-analysis ledger: outputs/k_gap/g1_binding/final5_typed.json items.ENGAGE (k-gap holds the FDA/EMA/open-copy routes for outputs/k_gap/engage_ci_search.json).
- **CoDEX 28-day: NOT_FOUND,** every route read: AACT has no posted results; the held abstract's 28-day mortality sentences give no counts or percentages; PMC body FETCH_EMPTY and not open.

**Codex review:** r1a (5) and r1b (6) on 44cc3308d. Every finding was reproduced. Fixed with plants that failed first: K5 percentage cells, reader-gate percentages, ENGAGE arm and endpoint checks, CoDEX routes now read, signed-finding column meanings. The D15 conflict goes to Mahmood (above). r2 on the fixes is running.

**For the captain, outside this range:**
- (a) cache/corticosteroids-covid19-mortality/ft_32678530.txt, the RECOVERY NEJM full text (fulltext_index copy_licence NOT_OPEN), is **tracked on main**. This looks like a non-CC full text committed (D8 / "only excerpts, CC BY/CC0 or US-gov"). Not touched here.
- (b) The older binding range (g1/binding-on-d0848a72: tranexamic D10 binding, held D10 amendments) still needs its rebase PR; that is next on this lane.

### Final-5 binding, closing update (2026-10-08 23:40 GMTDT, g1/final5-binding @ 997f90b09)
- Codex review rounds: r1a (5 findings), r1b (6), r2 (4), r3 (2), r4 (3). Every finding was reproduced and fixed with a plant that failed first, except the D15 conflict, which is a signed decision and goes to Mahmood. **The loop was stopped by rule after r4.** The residual class is free-prose regex coverage in the CoDEX absence detector; it fails toward CANDIDATE (a read), never toward an admission.
- Tests: subset **1519 passed**, 3 xfailed, 0 failed. Recount results are unchanged from the report above:
  - cortico: RESULT_AGREES met; ALL_ELIGIBLE_MATCHED left.
  - iv-iron: D14 named, D15 applied, EFFECT-HF side proposed.
  - ENGAGE (AACT) and CoDEX: NOT_FOUND. CANVAS: side not nameable.
- **Ready to merge as a range:** 96921df40..997f90b09. Regenerate with python scripts/g1_final5_typed.py --fetch first, which pulls the pinned RECOVERY appendix into the git-ignored outputs/k_gap/_supp.
