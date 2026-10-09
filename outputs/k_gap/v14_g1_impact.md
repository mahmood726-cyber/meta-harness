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
