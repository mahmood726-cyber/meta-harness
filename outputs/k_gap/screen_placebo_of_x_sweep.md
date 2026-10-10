# screen.py placebo-of-X + structural-False fix: 32-topic sweep (served screen re-run on each topic's own inputs; nothing applied)

5 changed decisions over 32 topics
| topic | record | old | new | new reason |
|---|---|---|---|---|
| colchicine-secondary-cv-prevention | NCT03376698 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention colchicine, comparator placebo, population coronary — P/I/C/d |
| empagliflozin-hfpef-hosp | NCT05138575 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention empagliflozin, comparator placebo, population preserved eject |
| esketamine-trd-madrs | NCT01998958 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention esketamine, comparator placebo, population treatment-resistan |
| finerenone-ckd-t2d-renal | NCT01968668 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention BAY94-8862, comparator placebo, population diabetic nephropat |
| melatonin-primary-insomnia-sol | NCT00816673 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention circadin, comparator placebo, population primary insomnia — P |

## G1 effect of each changed decision (reported BEFORE applying)

| topic | record | G1 today | effect |
|---|---|---|---|
| empagliflozin-hfpef-hosp | NCT05138575 (SAK) | G1_MATCHED | Eligible trial outside comparator 37773799 -> ALL_ELIGIBLE_MATCHED fails unless named. Proposed TARGET_RESULT_ABSENT: recruiting, no results, primary is 6-week exercise endurance, crossover (V15 K-3). |
| finerenone-ckd-t2d-renal | NCT01968668 (ARTS-DN Japan) | G1_MATCHED | In the comparator's set; already named NOT_IN_COMPARATOR_OUTCOME_ANALYSIS. **No change.** |
| melatonin-primary-insomnia-sol | NCT00816673 (Circadin elderly) | NOT_YET | No status change. The family-reconcile count goes 1 -> 2, which matches review 12. |
| esketamine-trd-madrs | NCT01998958 (intranasal esketamine dose-finding) | G1_MATCHED | **AT RISK.** The record screen now includes it, but the protocol requires esketamine "added to a newly-initiated oral antidepressant", which the regex screen cannot check. The recorded dual readers split on it (verbatim prompt). Needs either an exclusion on that criterion (source span) or a name, else esketamine leaves G1_MATCHED. |
| colchicine-secondary-cv-prevention | NCT03376698 (dose-finding, T2D + CAD) | NOT_YET (abandoned) | None. |
