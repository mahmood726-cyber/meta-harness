# G1 reconciliation: doac-vte-recurrence (comparator PMID 24963045)

Every number is a comparator printed row, a served row, or counts read from a quoted span (scripts/g1_reconcile.py).

| comparator trial | class | verdict | comparator row | ours | span |
|---|---|---|---|---|---|
| Dabigatran versus warfarin in the treatment of acute venous  (PMID 19966341) | MATCHED_NO_COMPARATOR_ROW | matched; the comparator prints no per-trial row |   (-) | None/None vs None/None |  |
| Treatment of acute venous thromboembolism with dabigatran or (PMID 24344086) | MATCHED_NO_COMPARATOR_ROW | matched; the comparator prints no per-trial row |   (-) | None/None vs None/None |  |
| Edoxaban versus warfarin for the treatment of symptomatic ve (PMID 23991658) | MATCHED_NO_COMPARATOR_ROW | matched; the comparator prints no per-trial row |   (-) | None/None vs None/None |  |
| Oral apixaban for the treatment of acute venous thromboembol (PMID 23808982) | MATCHED_NO_COMPARATOR_ROW | matched; the comparator prints no per-trial row |   (-) | None/None vs None/None |  |
| Oral rivaroxaban for symptomatic venous thromboembolism. (PMID 21128814) | MATCHED_NO_COMPARATOR_ROW | matched; the comparator prints no per-trial row |   (-) | None/None vs None/None |  |
| Oral rivaroxaban for the treatment of symptomatic pulmonary  (PMID 22449293) | MATCHED_NO_COMPARATOR_ROW | matched; the comparator prints no per-trial row |   (-) | None/None vs None/None |  |
| Management and outcomes of major bleeding during treatment w (PMID 24081972) | TRUE_SCOPE_DIFFERENCE:SECONDARY_ANALYSIS_OF_TRIALS_STATED | out of the registered protocol's scope; the record states it |   (-) | / vs / |  |

## Does the comparator's conclusion survive?

Method: FE (the tracker reproduced the comparator with it).

| scenario | trials | RR (95% CI) | conclusion | provenance |
|---|---|---|---|---|
| A_shared_trials_comparator_rows | - | fewer than 2 poolable rows | - |
| B_shared_trials_our_rows_ITT | - | fewer than 2 poolable rows | - |
| C_shared_trials_held_set_nearest_the_comparator_row | - | fewer than 2 poolable rows | - |
| D_comparator_rows_all_printed | - | fewer than 2 poolable rows | - |
| E_comparator_rows_protocol_scope_only | - | fewer than 2 poolable rows | - |
| F_protocol_scope_only_with_ITT_where_held | - | fewer than 2 poolable rows | - |

**On the shared trials: NOT_TESTABLE_ON_SHARED_ROWS.** 

## Whole pools (the same trials, different measures)

- ours: {'k': 6, 'estimate': 0.9091, 'ci_low': 0.7479, 'ci_high': 1.105, 'scale': 'HR'}
- comparator: {'outcome': 'Recurrent VTE', 'estimate': 0.9, 'ci_low': 0.77, 'ci_high': 1.06, 'scale': 'RR'}
- WHOLE_POOL_MEASURE_DIFFERS
- event-total check: **EVENTS_INCOMPATIBLE_WITH_COMPARATOR_RATES** -- the trials' held abstracts report 702 primary-outcome events; the comparator's printed rates (2.0% / 2.2%) over its stated 27023 patients hold at most 608.0 -- numerically incompatible: a different outcome definition, window, population or rate construction, not resolved here
  - comparator: "Recurrent VTE occurred in 2.0% of DOAC recipients compared with 2.2% in VKA recipients (relative risk [RR] 0.90, 95% confidence interval [CI] 0.77-1.06)."
  - PMID 19966341: [30, 27] -- "RESULTS: A total of 30 of the 1274 patients randomly assigned to receive dabigatran (2.4%), as compared with 27 of the 1265 patients randomly assigned to warfarin (2.1%), had recurrent venous thromboembolism; the differe"
  - PMID 24344086: [30, 28] -- "The primary outcome, recurrent symptomatic, objectively confirmed VTE and related deaths during 6 months of treatment occurred in 30 of the 1279 dabigatran patients (2.3%) compared with 28 of the 1289 warfarin patients ("
  - PMID 23991658: [130, 146] -- "Edoxaban was noninferior to warfarin with respect to the primary efficacy outcome, which occurred in 130 patients in the edoxaban group (3.2%) and 146 patients in the warfarin group (3.5%) (hazard ratio, 0.89; 95% confid"
  - PMID 23808982: [59, 71] -- "RESULTS: The primary efficacy outcome occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2635 (2.7%) in the conventional-therapy group (relative risk, 0.84; 95% confidence interval [CI],"
  - PMID 21128814: [36, 51] -- "Rivaroxaban had noninferior efficacy with respect to the primary outcome (36 events [2.1%], vs. 51 events with enoxaparin-vitamin K antagonist [3.0%]; hazard ratio, 0.68; 95% confidence interval [CI], 0.44 to 1.04;"
  - PMID 22449293: [50, 44] -- "P=0.003) for the primary efficacy outcome, with 50 events in the rivaroxaban group (2.1%) versus 44 events in the standard-therapy group (1.8%) (hazard ratio, 1.12; 95% confidence interval [CI], 0.75 to 1.68)."
