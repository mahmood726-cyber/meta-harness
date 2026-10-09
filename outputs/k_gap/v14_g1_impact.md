# V14 candidates from the evidence-completeness sprint: G1 impact, reported BEFORE anything is applied (k-gap, 9 Oct ~23:00)

Nothing below is applied. Each item needs the captain's packet and Mahmood's signature where it moves a served number.
Strict status is computed with render_g1_tracker.recompute on main's tracker files (beb73a487).

| Item | Topic (G1 now) | In the comparator's set? | Effect on G1 | Effect on the served page |
|---|---|---|---|---|
| ARTS-DN Japan NCT01968668 (Katayama 2017, PMID 28025025): re-screen flip X-CONTRAST -> include (F1: a Placebo arm beside BAY94-8862); dual codex ELIGIBLE | finerenone (MATCHED 2/2) | yes, "Katayama et al. (17)", already named NOT_IN_COMPARATOR_OUTCOME_ANALYSIS (G1-OUTCOME-SET) | **none**: the name rests on the comparator's outcome set, not on our screen | screening record changes exclude -> include; a phase 2b UACR trial, so the kidney composite would be declared absent; no pooled number expected to move |
| SAK HFpEF NCT05138575: re-screen flip X-CONTRAST -> include (F2: 'Placebo for Empagliflozin' is a placebo arm); dual ELIGIBLE | empagliflozin-hfpef (MATCHED 1/1) | no | none unless it is pooled (then it must be named as ours-not-in-comparator) | screening record exclude -> include; HHF result not expected (short factorial mechanistic trial) |
| Circadin elderly NCT00816673: re-screen flip X-CONTRAST -> include; dual ELIGIBLE | melatonin (NOT) | no | none (topic already unmatched; the comparator prints no result) | screening exclude -> include; sleep-onset latency status to extract |
| FLOW NCT03819153: 3-point MACE posted in AACT, 212/1767 v 254/1766 (non-fatal MI, non-fatal stroke, CV death; weeks 0-234) | glp1 (MATCHED 7/7) | no | none on ALL_ELIGIBLE (the comparator's set); if pooled it is ours-not-in-comparator and must be named (date-explained if the comparator predates it) | **a new served number**: FLOW is eligible under the registered protocol (T2D, semaglutide v placebo, double-blind) and carries 3-point MACE counts -> the pooled GLP-1 MACE estimate changes |
| omarigliptin first HHF (AACT exploratory 20/2092 v 33/2100; HR 0.60 (0.35-1.05)) + CARMELINA HHF (captain-verified PubMed) | dpp4 (MATCHED) | omarigliptin not in the set | none (a new outcome, not the matched one) | **a new served outcome** (dpp4 HF, audit R6 P2) |
| FREEDOM serious AEs (AACT totals: placebo 972/3876, denosumab 1004/3886; safety set) | denosumab (MATCHED) | yes (the matched trial) | none (harm outcome) | **a new served harm number** (audit R4) |
| FIDELIO-DKD hyperkalaemia (AACT: other 422/2827 v 212/2831; serious 42 v 12) v FDA label ADR 516/2827 v 255/2831 | finerenone (MATCHED) | yes | none (harm outcome) | **a new served harm**; which definition is served is a protocol decision |
| ELIXA 3-point MACE | glp1 | yes (named ESTIMAND_DIFFERENCE on its 4-point primary) | none | NOT_FOUND in open typed sources (AACT 4-point only; FDA lixisenatide documents 4-point; NICE values in figures) -> the existing name stands |
| DETERMINE-R/P, EMPERIAL-R/P | dapagliflozin- / empagliflozin-hfpef | outcome state | none | REPORTED_OTHER_ENDPOINT (functional / PRO outcomes only in AACT) |

Ledgers: outputs/k_gap/v14_targets_acquired.json (typed, AACT snapshot 2026-08-30 + digest), outputs/k_gap/rescreen/,
outputs/k_gap/concept/. DISAGREE flips (5) need a captain call: 4 dpp4 (INDORSE, NCT00918879, NCT02192853, NCT02792400)
and colchicine-secondary NCT03376698.

## 2026-10-09 ~23:45 -- concept-search dual screen, (a) topics doac + esketamine (verbatim-protocol prompt; 184 recorded calls)

Result: 92 regex-included concept records -> ELIGIBLE 5, EXCLUDED 64, DISAGREE 23 (ledger outputs/k_gap/concept/_dual_a_doac_esketamine.json).
G1 effect computed per trial BEFORE applying. **Nothing is applied.**

**esketamine-trd-madrs (G1_MATCHED 3/3): no change.**
- 31290965 TRANSFORM-1 is ALREADY in the comparator set (37377288) and matched.
  - It came back as "new" because concept dedup is by record id, not by trial identity.
  - Defect noted: identity-level dedup is needed before newly-eligible counts are trusted.
- NCT03852160 is CT.gov WITHDRAWN, enrollment 0 ACTUAL ("a new study has replaced 5413541TRD3011").
  - Eligible on design, but it has no participants to pool.
  - Proposed name: WITHDRAWN_NO_PARTICIPANTS. With that name, no ALL_ELIGIBLE_MATCHED change.

**doac-vte-recurrence (G1_MATCHED 5/5): AT RISK.** Three new eligible trials are outside comparator 29795629's set of 5:
- 18541000 BOTTICELLI DVT (J Thromb Haemost 2008). Apixaban dose-ranging, phase 2, 84-91 days. A known recall miss, now found.
- 31455473 (J Coll Physicians Surg Pak 2019). Open-label RCT, rivaroxaban v warfarin in DVT.
- NCT02506985 XENITH. Rivaroxaban v heparin-warfarin after catheter-directed thrombolysis for PE. TERMINATED at n=10; has posted results; primary outcome is biomarkers.

The comparator restricts itself to phase 3 trials: its title is "...evidence from phase 3 trials" (protocol line 70). Our protocol's eligibility has no phase restriction.
- Unless each trial is NAMED with a typed reason, doac's ALL_ELIGIBLE_MATCHED fails and the topic drops from G1_MATCHED.
- Proposed reason: NOT_IN_COMPARATOR_SCOPE:PHASE_3_ONLY, citing the comparator's own title span. XENITH might instead be NOT_IN_OUTCOME_ANALYSIS (n=10, biomarker endpoint). Captain to rule (V14).
- 23 doac DISAGREE records need a third read or a ruling. They include J-EINSTEIN 25717286 (Japanese phase 3, NCT01516814/NCT01516840): reader A said NOT_DECIDABLE_FROM_RECORD, reader B MEETS_ALL. If eligible it is a fourth unnamed trial for doac.

## 2026-10-10 ~00:40 -- noac-vs-warfarin-af-stroke dual screen (221 records after trial-identity dedup; 442 recorded calls)

Result: ELIGIBLE 41, EXCLUDED 171, DISAGREE 9 (outputs/k_gap/concept/_dual_a_noac.json). **Nothing applied; no G1 count computed as final.**

The 41 are mostly NOAC-v-VKA RCTs whose endpoints are not stroke/SEE. Examples:
- cognition: 36284318, NCT03061006, NCT03839355, NCT04073316;
- plaque progression: 39122204, NCT02090075;
- kidney function: NCT03789695 (RE-ELECT);
- biomarkers: NCT03490994, 32577819;
- phase-2 dose finding: 20694273, 22664798, NCT00787150, NCT00973323, NCT01227629;
- probably a translated report of RE-LY: 19845524 (its record carries no NCT, so identity dedup could not catch it).

So noac is NOT outcome-intrinsic. The same flood B-prime prevented for GLP-1 would happen here: under the literal rule, noac's ALL_ELIGIBLE_MATCHED cannot hold.

- **Moved to (b):** the literal universe is reported in the V14 question, not applied.
- **Plausibly in a stroke/SEE analysis** (if the captain wants a typed endpoint-axis rule): J-ROCKET AF 22664783, ROCKET AF China 23929423, RIVER 33196155, RENAL-AF NCT02942407, AXADIA NCT02933697, and the Japanese/Asian phase 2 safety trials.

## 2026-10-10 ~01:30 -- semaglutide-obesity-weight dual screen (66 records after identity dedup; 132 recorded calls)

Result: ELIGIBLE 1, EXCLUDED 40, DISAGREE 25 (outputs/k_gap/concept/_dual_a_semaglutide_weight.json).
- **STEP 5** (36216945; NCT03693430; Garvey 2022, 2-year) is a recall miss: it is not in our pool and not in comparator 42536519's set.
  - Its CT.gov posted results give the body-weight change at **Week 104 only** (primary: "Percentage Change From Baseline (Week 0) to Week 104 in Body Weight").
  - Under protocol line 18 ("If an otherwise eligible trial does not report the Week-68 percent body-weight change ... it is declared absent rather than substituted with another endpoint or timepoint"), STEP 5 is ELIGIBLE with its OUTCOME DECLARED ABSENT.
  - **G1 effect (not applied):** semaglutide-obesity-weight is G1_MATCHED (2/2 eligible matched; O'Neil and Rubino named). A fourth eligible trial outside the comparator keeps ALL_ELIGIBLE_MATCHED only if it is named. Proposed name: OUTCOME_ABSENT_AT_PROTOCOL_TIMEPOINT (Week 104 only; span = the posted primary title). No pooled number changes.
- The 25 DISAGREE records need a third read or a ruling before any is counted.
