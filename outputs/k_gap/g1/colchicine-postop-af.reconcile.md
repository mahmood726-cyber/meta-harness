# G1 reconciliation: colchicine-postop-af (comparator PMID 36050741)

Every number is a comparator printed row, a served row, or counts read from a quoted span (scripts/g1_reconcile.py).

| comparator trial | class | verdict | comparator row | ours | span |
|---|---|---|---|---|---|
| Bessissow [17] (PMID 29237033) | TRUE_SCOPE_DIFFERENCE:PROTOCOL_EXCLUDES_POPULATION | out of the registered protocol's scope; the record states it | RR 0.74 (0.25-2.19) | / vs / | Colchicine for Prevention of Perioperative Atrial Fibrillation in patients undergoing lung resection surgery: a pilot randomized controlled study.. |
| Deftereos [15] (PMID 23040570) | TRUE_SCOPE_DIFFERENCE:PROTOCOL_EXCLUDES_POPULATION | out of the registered protocol's scope; the record states it | RR 0.48 (0.26-0.85) | / vs / | Colchicine for prevention of early atrial fibrillation recurrence after pulmonary vein isolation: a randomized controlled study.. |
| Deftereos [16] (PMID 24508207) | TRUE_SCOPE_DIFFERENCE:PROTOCOL_EXCLUDES_POPULATION | out of the registered protocol's scope; the record states it | RR 0.63 (0.44-0.89) | / vs / | Colchicine for prevention of atrial fibrillation recurrence after pulmonary vein isolation: mid-term efficacy and effect on quality of life.. |
| Imazio [19] (PMID 22090167) | SCREENER_ERROR:SECONDARY_REPORT_OF_RCT | our screen is wrong: the record is a randomised report of an eligible trial; its result is NOT extractable from the held abstract (percentages only, arm sizes not stated): full text required | RR 0.54 (0.28-1.05) | / vs / | Colchicine reduces postoperative atrial fibrillation: results of the Colchicine for the Prevention of the Postpericardiotomy Syndrome (COPPS) atrial fibrillatio |
| Imazio [18] (PMID 25172965) | ANALYSIS_SET_DIFFERENCE | both numbers are in the report: we pool the all randomised (no analysis set named) counts (registered estimand: intention-to-treat); the comparator's row is nearest to, but is not reproduced by, the on-treatment analysis | RR 0.66 (0.45-0.96) | 61/180 vs 75/180 | There were no significant differences between the colchicine and placebo groups for the secondary end points of postoperative AF (colchicine, 61 patients [33.9% |
| Sarzaeem [23] (PMID None) | IDENTITY_UNRESOLVED | the comparator's label resolves to no held record |   (-) | / vs / |  |
| Tabbalat [22] (PMID 27502857) | TRUE_SCOPE_DIFFERENCE:OPEN_LABEL_STATED | out of the registered protocol's scope; the record states it | RR 0.71 (0.45-1.12) | / vs / | METHODS: In this multicenter prospective randomized open-label study, consecutive patients with no history of AF and scheduled to undergo elective cardiac surge |
| Tabbalat [21] (PMID 32720823) | SAME_NUMBER | both sides hold the same result | RR 0.88 (0.44-1.76) | 13/81 vs 13/71 |  |
| Zarpelon [20] (PMID 27223641) | TRUE_SCOPE_DIFFERENCE:OPEN_DESIGN_STATED_FOR_THIS_STUDY | out of the registered protocol's scope; the held OA FULL TEXT states it (the abstract did not) | RR 0.54 (0.19-1.53) | / vs / | Methods Study Design and Participants This is a prospective, randomized, open, single-center clinical assay, whose 140 participants were recruited from the Hosp |

## Does the comparator's conclusion survive?

Method: FE (the tracker reproduced the comparator with it).

| scenario | trials | RR (95% CI) | conclusion | provenance |
|---|---|---|---|---|
| A_shared_trials_comparator_rows | Imazio [18], Tabbalat [21] | 0.7051 (0.5057-0.9832) | BENEFIT | |
| B_shared_trials_our_rows_ITT | Imazio [18], Tabbalat [21] | 0.8211 (0.6396-1.0541) | NULL_INCLUDED | |
| C_shared_trials_our_rows_with_the_comparators_analysis_set | Imazio [18], Tabbalat [21] | 0.6903 (0.511-0.9323) | BENEFIT | |
| D_comparator_rows_all_printed | Bessissow [17], Deftereos [15], Deftereos [16], Imazio [19], Imazio [18], Tabbalat [22], Tabbalat [21], Zarpelon [20] | 0.6402 (0.5314-0.7712) | BENEFIT | comparator-only (unverified) rows: Bessissow [17], Deftereos [15], Deftereos [16], Imazio [19], Tabbalat [22] |
| E_comparator_rows_protocol_scope_only | Imazio [19], Imazio [18], Tabbalat [21] | 0.6682 (0.4965-0.8992) | BENEFIT | comparator-only (unverified) rows: Imazio [19] |
| F_protocol_scope_only_with_ITT_where_held | Imazio [19], Imazio [18], Tabbalat [21] | 0.7792 (0.6168-0.9843) | BENEFIT | comparator-only (unverified) rows: Imazio [19] |

**On the shared trials: DOES_NOT_SURVIVE.** the shared-trial benefit depends on which analysis set of the Imazio [18] report is pooled
