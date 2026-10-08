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

---

## Part B: comparator swaps on the 12 ACTIVE unmatched topics, all 12 decided (7 Oct, branch g1/binding-on-d0848a72 @ bc4707883)

Rebased onto v8/comparator-switches-2026-10-06. Rule SHAs were committed before any search: 262d0ea08 for 6 topics, c5ecb6640 for 6 (statins / melatonin / denosumab are round 2, `.r2`; the 5 Oct rules are untouched). Screening used the fixed scripts/g1_swap.py: 1073 recorded swap-screen calls, 5 local + 5 worker, all passing record_licence. Selection is by the rule alone (g1_comparator_select.py).

### FOR V9: one adopted swap, doac-vte-recurrence, 24963045 -> 29795629 (commit bc4707883)

- **Pick.** 519 on-topic candidates; only one passes C1-C6: PMC5967718 (PLoS One 2018, CC BY 4.0).
- **R0 retired 24963045.** Reason: C1_OPEN_LICENCE FAIL (Unpaywall bronze, no CC licence). Its C2-C6 were not read, because a non-CC text is never read.
- **Enumeration.** Recorded call mc-2174b137, ENUMERATED with k=5 and 0 refused. Each trial is bound to the PMID its own reference list prints: RE-COVER 19966341, EINSTEIN-DVT 21128814, AMPLIFY 23808982, Hokusai-VTE 23991658, RE-COVER II 24344086.
- **Pooled, as printed.** OR 0.88 (0.75-1.03), "five Phase 3 studies".
- **Typed comparator rows.** From Table 1 (events/N), with arm order taken from the table header: 30/1274 v 27/1265, 36/1731 v 51/1718, 59/2609 v 71/2635, 130/4118 v 146/4122, 30/1279 v 28/1289. They are re-checked by g1_tracker.typed_comparator_rows (digest + spans).
- **Every changed outcome (local recount, gates unchanged, shared outputs restored):**

| | before (24963045) | after (29795629) |
|---|---|---|
| N comparator trials | 7 | 5 |
| eligible / matched / verified | 6 / 6 / 6 | 5 / 5 / 5 |
| ours not in comparator | - | EINSTEIN-PE 22449293 (NOT_EXPLAINED_BY_DATE) |
| same-trials RESULT | MEASURE_DIFFERENCE (k 6, no comparator rows) | MEASURE_DIFFERENCE_SAME_CONCLUSION (k 5, typed rows): our HRs v their OR, never converted |
| per-trial agreement | NO_COMPARATOR_ROW x6 | HR_VS_OR x4, RR_VS_OR x1 |
| G1 | NOT_YET (RESULT_AGREES false) | NOT_YET (RESULT_AGREES false) |
| comparator identity | van Es 2014, RR 0.90 (0.77-1.06) | 2018 SR/MA, OR 0.88 (0.75-1.03) |

- **The swap does NOT flip G1.** The rule's T1 (estimand match) scored 0, because no CC BY candidate pooled HR and passed. The move: a comparator we cannot hold openly is replaced by one we hold under CC BY, with an enumerated set and typed rows. The remaining block is the measure difference, which is not to be converted.
- **Served numbers change** (comparator, N). Lane branch only; nothing landed. The notice is for you to derive (derive_outcome_notices) for Mahmood's signature.
- **Stale year.** `docs/reviews/doac-vte-recurrence/review.json` still names the old comparator, so the tracker's `ours_not_in_comparator_detail.comparator_year` reads 2014 (old) until you regenerate. No verdict changes here (2012 < both years). It is still a class: g1_tracker line 3801 takes the comparator year from review.json, not from the current comparator. Reported, not changed.

### NO_ACHIEVABLE_COMPARATOR: 11 topics keep their current comparator (rule if_none_pass; no served change)

These show the closest candidate and what it failed (ties broken by most recent). The R0 column records why the current comparator itself would not qualify as a swap target.

| topic | rule | cands | R0 on current | closest candidate (n tied) | its non-PASS |
|---|---|---|---|---|---|
| iv-iron | 262d0ea08 | 35 | 39727669: C5, C6 UNCLEAR (rows only in figures) | 41711738 (1) at 4/6 | C3 UNCLEAR, C6 UNCLEAR (forest plot) |
| corticosteroids-covid19 | 262d0ea08 | 380 | 32876694: C1 FAIL | **38124031 (1) at 5/6** | **C6 UNCLEAR: rows only in supplement Figure S5 (docx)** |
| sacubitril-valsartan | 262d0ea08 | 139 | 36722326: C1 FAIL | 38013641 (3) at 4/6 | C5 FAIL, C6 FAIL |
| semaglutide-mace | 262d0ea08 | 196 | 39345822: C1 FAIL | 41276951 (1) at 4/6 | C3 FAIL (CKD population) |
| sglt2-ckd | 262d0ea08 | 570 | 41203232: C1 FAIL | 42109728 (17) at 4/6 | C5 FAIL (creatinine-doubling composite), C6 FAIL |
| tranexamic-acid | 262d0ea08 | 726 | 39461793: C3 FAIL | 40719896 (54) at 3/6 | C3 FAIL (sICH) |
| colchicine-recurrent-pericarditis | c5ecb6640 | 206 | 22442198: C1 FAIL | 31477020 (2) at 4/6 | C3 FAIL (mixed pericarditis), C5 UNCLEAR |
| sglt2-primary-prevention-hf | c5ecb6640 | 586 | 33519713: C3 FAIL | 40005319 (3) at 5/6 | C3 FAIL (T2DM, HF or CKD) |
| statins@r2 | c5ecb6640 | 429 | 32529863: C1 FAIL | 41655587 (34) at 3/6 | C3, C5, C6 FAIL |
| melatonin@r2 | c5ecb6640 | 315 | 35691474: not read (no CC text delivered) | 41602948 (27) at 3/6 | C3 FAIL (delirium) |
| denosumab@r2 | c5ecb6640 | 163 | 32492050: C3, C5 FAIL | 42494861 (1) at 4/6 | C5 FAIL (BMD), C6 FAIL |

**Decision for you or Mahmood (not taken by me).** C6 allows "a forest plot with counts or effects … in the article or its own open supplement", but the screen reader sees text only, so rows that exist only as an image read UNCLEAR. This binds for exactly one candidate, corticosteroids **38124031**: a network meta-analysis of glucocorticoid regimens with C1-C5 PASS, whose rows are in supplement Figure S5. I did NOT read that figure: adding a figure read after the search, for the one candidate that came close, would be a selective post-hoc procedure change. A ratified figure-read extension would have to apply to every candidate. The lane already has a recorded, CC-BY-gated forest-figure reader in secondary_meta_build.

### Harness defects found on the way (each fixed as a class, with a plant that fails first)

- **8ef29d1e8: unread candidates.** 151 candidates passed C1 on an Unpaywall CC BY location with no PMC id and were never read. They are now read from k_gap.unpaywall_text, but only when the location that DELIVERED the text is CC BY/CC0; the guard checks that location. 37 became readable; the rest fail closed.
- **8ef29d1e8: worker refusals.** 48 worker jobs were refused licence='NOT_HELD', with 0 refused locally. The guard reads the declared comparator JATS, which submit() never shipped. The declared JATS are now tarred to my own worker worktree (untracked there).
- **8acfaf449: record_licence DOI regex.** A DOI containing parentheses, '10.1016/s2213-8587(25)...', was cut at the first ')' and refused. Your guard is still fail-closed.
- **612b5559c: pooled gate k.** 'five Phase 3 studies' was refused as k=5 while k=3 would have PASSED (the '3' in 'Phase 3'). k may now transfer from a verbatim set quote only when that quote carries every stated estimate and bound.
- **86e8a6ad7, four fixes:**
  - Enumeration spans are written in held_norm form; k_gap_table had refused all 5 doac rows.
  - The R0 retirement reason lists only the criteria that FAILED.
  - The adoption date is the run date.
  - New `g1_swap rows` / type_rows: arm order from the header only.
- **Tests.** 826 g1/licence/swap/comparator tests pass.

### Still with you from earlier

- The record_licence words-licence fix.
- The TECOS record history purge.
- The NC-licence policy gap.
- fulltext_index entries without a pmcid never verify.
- A request for a CT.gov declared-ref form.

---

## D10 multi-outcome: 12 active topics (8 Oct, branch g1/binding-on-d0848a72 @ 0e5fb4b0c)

**Order of work (each step committed and pushed before the next):**
1. The rule was committed before any inventory: a40e00850.
2. Comparator outcome inventories and deterministic proposals: 10878e620.
3. **Dated protocol amendments: f70d28ff8, registered BEFORE any extraction.**
4. Extraction, the recorded rung and comparisons: a7935a7d7 to 4e1626e3d.

**What was used:**
- 104 recorded codex calls: 24 for the inventory, 80 for extraction. All pass record_licence.
- All calls ran locally at concurrency 5. The worker (100.80.183.43) has been unreachable since about 12:40 on 7 Oct (ssh connect timeout); nothing ran there.

### Amendments: 17 new outcomes in 6 topics, plus 4 links (`protocols/<slug>.md` "Amendment 2026-10-07 (D10 …)" and `topics/<slug>.json`)

These moved protocol_sha for the 6 topics, so the served build needs your rebuild.

| topic | new outcomes (family) | linked to an already-registered outcome |
|---|---|---|
| iv-iron | total deaths (P1); serious adverse events (P2); non-HF hospitalizations, CV hospitalization or death composite, 6MWT distance (P3) | - |
| tranexamic | death within 24 h (P1); MI, stroke, sepsis, seizures (P2) | Thromboembolic events |
| sglt2-ppHF | death from any cause (P1); MACE, cardiovascular death (P3) | - |
| doac-vte | total mortality (P1); net clinical benefit (P3) | - |
| statins | all-cause mortality (P1) | - |
| colchicine-pericarditis | drug withdrawals (P2) | Adverse events (gastrointestinal) |

**Nothing admissible under the rule** (each exclusion is recorded with its reason in the topic's proposal.json):
- corticosteroids: the comparator splits results by steroid; its class mortality is our primary.
- sacubitril: nothing beyond the primary is printed with a CI in the abstract we may read.
- semaglutide: the comparator is a GLP-1 / GIP-GLP-1 class meta, not semaglutide.
- melatonin: the copy is not CC; neither the abstract nor the held text gives a pooled non-primary result.
- sglt2-ckd: subgroups only.
- denosumab: a network meta-analysis whose denosumab results are secondary-prevention only (the same reason R0 gave, C3).

### Results: our pool vs the comparator's printed pool, on its measure (comparison.json per topic)

The comparator printed a pooled result only, so the trial sets can differ; both k values are given.

| topic / outcome | ours | comparator | verdict | our rows |
|---|---|---|---|---|
| iv-iron / Total deaths | k=2 of 9, OR 0.97 (0.37-2.51) | OR 0.85 (0.70-1.03) | SAME_CONCLUSION_DIFFERENT_ESTIMATE | AFFIRM-AHF CT.gov structured 98/558 v 96/550 (ladder); HEART-FID AACT 'Total, all-cause mortality' 354/1532 v 367/1533 (typed) |
| iv-iron / Serious adverse events | k=2 of 9, OR 0.91 (0.14-6.07) | OR 0.73 (0.49-1.10) | SAME_CONCLUSION_DIFFERENT_ESTIMATE | AFFIRM-AHF abstract 250/559 v 282/551 (ladder); HEART-FID AACT 'Total, serious adverse events' 413/1532 v 401/1533 (typed) |
| statins / All-cause mortality | k=1 of 5, HR 0.80 (0.62-1.04) | OR 0.94 (0.76-1.16) | MEASURE_DIFFERENCE_SAME_CONCLUSION (never converted) | JUPITER ≥70 years, abstract (ladder) |
| sglt2-ppHF / Death from any cause | k=1 of 7, RR 0.90 (0.69-1.19) | RR 0.77 (0.59-1.01) | SAME_CONCLUSION_DIFFERENT_ESTIMATE | CANVAS AACT totals 134/2886 v 74/1441 (typed; the two canagliflozin doses summed, the control counted once) |
| the other 13 outcomes | - | printed | NO_ROWS | no open source holds them (see below) |
| iv-iron / 6MWT | - | MD 14.03 | MEASURE_DIFFERENCE_NOT_POOLABLE | only an LS-mean ± SE row |

**Why 13 outcomes are NO_ROWS** (recorded per trial in acquired.json):
- The trial reports are non-CC journal articles, so their full text is never shown to a model.
- AACT 'Total, all-cause mortality' rows for pre-2017 results carry no counts.
- The posted effects are HRs where the registered measure is the comparator's OR/RR.
- Recorded-rung verdicts:
  - SOURCE_ABSENT 65
  - NO_OPEN_SOURCE 22
  - gate refusals 12: AACT arms, a typed match not found beside the outcome terms, a quote not verbatim
  - UNSURE 2

### BLOCKER before you rebuild these 6 topics: the served ladder mis-binds four new-outcome rows

The served pipeline would put another outcome's number under the new outcome's name. My comparison sets these rows aside by name (`g1_outcomes.ladder_misbound`, 6 plants), but the served build does not:

1. **iv-iron "Non-HF hospitalizations" gets AFFIRM-AHF's CT.gov "HF Hospitalisations" HR 0.73 (0.59-0.92).** The structured target-endpoint binding loses the negation; binding_verdict refuses it (OUTCOME_NOT_NAMED).
2. **sglt2-ppHF "Death from any cause" gets DECLARE's RENAL HR 0.76 (0.67-0.87).** That effect is printed in the clause before "death from any cause occurred in 6.2% and 6.6%".
3. **iv-iron "Serious adverse events" includes IRONMAN's "cardiac serious adverse events" 200 v 243**, a qualified subset.
4. **statins "All-cause mortality" gets STAREE's composite "death from any cause, dementia, or persistent physical disability" HR 0.94.** The stored source sentence is cut before the HR, so its clause cannot even be checked.

Classes:
- (1) the structured-title binder accepts a title naming no keyword of the outcome;
- (2) the abstract extractor takes an effect from a clause that does not name the outcome;
- (3) a qualified subset;
- (4) a composite list.

The served extractors are yours (harness/extract, target_endpoint). I changed nothing there, because any fix moves other topics' served numbers. The four sentences above are ready-made plants.

### For V9 / notices (all for Mahmood's signature; nothing landed, nothing served by this lane)

- **New served outcomes.** After a rebuild with the four mis-bindings fixed or refused:
  - iv-iron Total deaths (AFFIRM-AHF row) and SAE (AFFIRM-AHF row);
  - statins All-cause mortality (JUPITER ≥70 row).

  Each is a new pooled claim, "a pooled estimate is now served where none was served before". Derive them with derive_outcome_notices after the rebuild.
- **Proposed served-pool additions** (typed rows from AACT, read deterministically; they need the signed-addition route):
  - HEART-FID deaths 354/1532 v 367/1533 and SAE 413/1532 v 401/1533 (NCT03037931);
  - CANVAS deaths 134/2886 v 74/1441 (NCT01032629, doses summed).
- **New harm outcomes** (iv-iron SAE; tranexamic MI, stroke, sepsis, seizures; colchicine drug withdrawals) face gate.check_harms_complete. Trials whose source mentions a harm without a poolable value need typed refusals (the held_harms_adjudication style) before they serve.
- **Ratchet gap (from the pipeline map).** honest_ratchet.compare_results loops over BASE outcomes only, so a new outcome passes the ratchet unchecked. Completeness is enforced only by signing_packet.completeness_problems.

### Lane fixes made along the way (each with a plant that failed first)

- **Inventory (R1 regex):** middle-dot decimals, the PDF '¼' standing for '=', bracketed abbreviations, CI without 95%.
- **Pooled gate:** a middle dot between digits is a decimal point (all 21 tranexamic claims had been refused).
- **Inventory v2:** every result now carries its contrast and population (v1 had proposed risedronate's and canagliflozin-only results).
- **Proposal filters:** a class topic needs the class result, not one agent's split; a single-agent comparator is the whole analysis; our-primary identity uses Jaccard.
- **Counts:** arm counts are read from ai/n1i/ci/n2i (my reader had dropped every count).
- **g1_trial_acquire._num_in:** a (thin-)space thousands separator such as '10 033'.
- **Tests:** 929 g1/licence/swap/comparator/outcome tests pass.

---

## CLOSE-4: binding share, counts STAGED (8 Oct, branch g1/binding-on-d0848a72 @ 48af986a1)

Nothing below is used for matching until Mahmood signs D12 COUNTS_FOR_MATCHING. The counts are staged in `outputs/k_gap/g1_binding/bindings_counts.json` (`scripts/g1_binding_counts.py`):
- **K1:** AACT posted participant counts. The title must pass binding_verdict; the timepoint is the treatment period; arms are mapped by our terms; denominators are posted.
- **K2:** the trial's own abstract, percent-corroborated, with the arm named beside each number.
- **K3:** recorded codex over open sources, through g1_trial_acquire's gates.

The comparator's numbers are never an input.

### 2. doac-vte-recurrence: all 6 trials staged. FLIP-READY ON D12.

| trial | ours (DOAC v warfarin/VKA) | source |
|---|---|---|
| RE-COVER | 30/1274 v 27/1265 | AACT NCT00291330 outcome 258389495, "up to day 180" |
| RE-COVER II | 30/1279 v 28/1289 | AACT NCT00680186 outcome 258441058, day 180 |
| Hokusai-VTE | 130/4118 v 146/4122 | AACT NCT00986154 outcome 258387756 |
| AMPLIFY | 59/2609 v 71/2635 | PMID 23808982 abstract |
| EINSTEIN-DVT | 36/1731 v 51/1718 | PMID 21128814 abstract (N "1731 given rivaroxaban and 1718 given enoxaparin") |
| EINSTEIN-PE | 50/2419 v 44/2413 | PMID 22449293 abstract events + AACT NCT00439777 posted N, percent-corroborated |

- **What-if under D12 (not applied):** the 5 trials shared with comparator 29795629's Table 1 are identical to it, row for row. They were found without it. Pooled OR is 0.881 (0.700-1.108) on both sides, so result_verdict = AGREE. RESULT_AGREES would be met.
- EINSTEIN-PE is ours, not in the comparator; it is already named.

### 3. semaglutide-obesity-mace: SELECT staged

- **SELECT:** 569/8803 v 701/8801, from AACT NCT03574597 outcome 258769011 (3-point MACE, the primary).
- **What-if:** OR 0.7985 (0.712-0.896) v the comparator's 0.80 (0.71-0.90), AGREE.
- **Not flip-ready alone:**
  - ALL_ELIGIBLE_MATCHED still needs k-gap's O'Neil X-DOSE amendment;
  - the comparator row's TIMEPOINT_NOT_STATED_BY_META refusal is unchanged.

### 1. sglt2-primary-prevention-hf: NO per-arm HHF counts exist in any open source. It stays a named measure difference.

**Your probe's "EMPA-REG and VERTIS-CV BINDABLE" is title binding only.** Their posted HHF rows are not counts:
- EMPA-REG 258266632 posts a **percentage of participants** (4.1 / 2.6 / 2.8);
- VERTIS-CV 258751223 posts **events per 100 person-years** (0.75 / 0.72 / 1.05).

A count is never computed from either.

**Other sources:**
- CANVAS, CANVAS-R and DECLARE post the CV death or HHF composite only.
- The abstracts print no HHF arm counts.
- None of the four NEJM reports is open. CANVAS's Unpaywall "copy" is the King's College London repository landing page, which carries the abstract only.
- 124 regulatory documents are now held for the topic (FDA 65 text, EMA 15, NICE 23). The typed reader finds no e/N row: labels print "212 (2.5)" with N only in the header.

**K3, recorded (5 calls):**
- EMPA-REG: REFUSED:AACT_MULTIPLE_TIME_FRAMES.
- CANVAS and CANVAS-R: SOURCE_ABSENT.
- VERTIS-CV: the gate admitted an **effect**, AACT HR 0.70 (0.539-0.902). It corroborates our served HR 0.70 (0.54-0.90) from an independent posted source, but it is not counts.
- DECLARE: UNSURE. **Finding:** FDA review 202293Orig1s018 states "hospitalization for heart failure ... (HR 0.83; 95% CI 0.73, 0.95)". AACT assigns that exact estimate and CI to the composite CV death or HHF. The FDA text is not taken.

### Also for V10

- **tranexamic (D10 outcome binding).** Our primary "Death due to bleeding" binds to the comparator's own printed row:

  > "Death due to bleeding | WOMAN, WOMAN-2, TRAAP, TRAAP-2 and TXA-MFMU | 159/27 307 | 194/27 097 | 0·81 (0·66–1·00)"

  The orientation comes from its header ("Tranexamic acid group (n/N) | Placebo group (n/N)"). This is recorded in `registry/comparator_results.json` (`scripts/g1_comparator_table_result.py`).
  - g1_tracker now **sets aside a served comparator result that is about another outcome**. reported[0] was the comparator's own primary, life-threatening bleeding. The set-aside is named in `comparator_reported_set_aside`, with a plant.
  - The comparator prints no per-trial death-due-to-bleeding rows, so the WOMAN1 comparison is pooled (k=5) v our k=1. Four of their five trials are already named scope differences.
- **CONFIRM-HF (iv-iron), a decision.** Table 2 (FCM n=150, placebo n=151) prints "Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)".
  - The header labels each arm's columns as "Total number of events" and "Incidence/100 patient-years at risk".
  - Events 10 v 32 are labelled, and they are what the comparator pooled over the 150/151 participants. Patients with an event (10 v 25) appear only inside the incidence cell, with no "patients" label, so I have not bound them.
  - Accept "the incidence numerator is patients with a first event"? If yes, the comparator's 32 is events (same class as AFFIRM-AHF's SECONDARY_WRONG).
- **EFFECT-HF (iv-iron), a decision.** The text prints "26 of them for worsening HF (13 in each group) in 17 patients (11 patients on FCM and 6 on usual care)".
  - The comparator's 13 v 13 are hospitalisations, not patients.
  - The safety-set N per arm is not printed: the FAS is 86 v 86, and the FCM administrations sum to 88. Not bound until the N is decided.
- **cortico-covid.** Your fetch fix resolves the four silent failures to NO_BODY, so there is no text to bind from. They stay as they are.
- **Fixes with plants that failed first:**
  - K2 read the generic "primary outcome" as ours. For sglt2-pp ours is HHF and the trials' primary is MACE, so it now counts only when the trial's own definition names our outcome.
  - Generic keywords ("hazard ratio") never name an outcome.
  - AACT is read once per table, not about 90 times.
  - Results-table rows need two arm cells, and a header that omits the row-label column is handled.
- **Process note.** A stopped background run's python child survived and overwrote the staged file. It was restored from the commit and K3 replayed with no new calls; nothing was lost.
- **Worker:** still unreachable, so everything ran here at 5.
