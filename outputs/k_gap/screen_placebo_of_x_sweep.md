# Screening-rule fixes (placebo-of-X, structural False, development codes, population synonyms, role-aware placebo): 32-topic sweep, main -> this branch (served screen re-run on each topic's own inputs; nothing applied)

21 changed decisions over 32 topics
| topic | record | old | new | new reason |
|---|---|---|---|---|
| colchicine-secondary-cv-prevention | NCT03376698 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention colchicine, comparator placebo, population coronary — P/I/C/d |
| dpp4-mace-t2d | NCT00918879 | exclude/X3 | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention saxagliptin, comparator placebo (masks the intervention), pop |
| dpp4-mace-t2d | NCT02180334 | exclude/X2 | exclude/X3 | no eligible comparator (none of ['compared with placebo', 'as compared with placebo', 'placebo group', 'placebo groups', |
| dpp4-mace-t2d | NCT02192853 | exclude/X3 | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention sitagliptin, comparator placebo (masks the intervention), pop |
| dpp4-mace-t2d | NCT02792400 | exclude/X3 | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention linagliptin, comparator placebo (masks the intervention), pop |
| dpp4-mace-t2d | NCT04521049 | exclude/X2 | exclude/X3 | no eligible comparator (none of ['compared with placebo', 'as compared with placebo', 'placebo group', 'placebo groups', |
| dpp4-mace-t2d | NCT04626323 | exclude/X2 | exclude/X3 | the randomised intervention is not ['sitagliptin', 'saxagliptin', 'alogliptin', 'linagliptin', 'DPP-4', 'MK-0431', 'BI 1 |
| dpp4-mace-t2d | NCT06770894 | exclude/X2 | exclude/X3 | no eligible comparator (none of ['compared with placebo', 'as compared with placebo', 'placebo group', 'placebo groups', |
| empagliflozin-hfpef-hosp | NCT05138575 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention empagliflozin, comparator placebo, population preserved eject |
| esketamine-trd-madrs | NCT01998958 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention esketamine, comparator placebo, population treatment-resistan |
| finerenone-ckd-t2d-renal | NCT01968668 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention BAY94-8862, comparator placebo, population diabetic nephropat |
| melatonin-primary-insomnia-sol | NCT00816673 | exclude/X-CONTRAST | include/INCLUDE | eligible double-blind/placebo-controlled RCT: intervention circadin, comparator placebo, population primary insomnia — P |
| metformin-pcos-ovulation | 17287476 | exclude/X3 | include/INCLUDE | eligible randomised controlled trial: intervention metformin, comparator placebo (masks the intervention; shared backgro |
| metformin-pcos-ovulation | 18681789 | exclude/X3 | include/INCLUDE | eligible randomised controlled trial: intervention metformin, comparator placebo (masks the intervention; shared backgro |
| metformin-pcos-ovulation | 21193187 | exclude/X3 | exclude/X-DESIGN | required design/context absent: record does not mention any of ['ovulation induction', 'ovulation inducing', 'clomiphene |
| metformin-pcos-ovulation | NCT00694759 | exclude/X3 | exclude/X-DESIGN | required design/context absent: record does not mention any of ['ovulation induction', 'ovulation inducing', 'clomiphene |
| metformin-pcos-ovulation | NCT02280057 | exclude/X3 | exclude/X-DESIGN | required design/context absent: record does not mention any of ['ovulation induction', 'ovulation inducing', 'clomiphene |
| metformin-pcos-ovulation | NCT03792984 | exclude/X3 | exclude/X-DESIGN | required design/context absent: record does not mention any of ['ovulation induction', 'ovulation inducing', 'clomiphene |
| sglt2-primary-prevention-hf | 32745202 | exclude/X2 | exclude/X3 | the randomised intervention is not ['empagliflozin', 'canagliflozin', 'dapagliflozin', 'ertugliflozin', 'SGLT2', 'SGLT-2 |
| sglt2-primary-prevention-hf | NCT02920918 | exclude/X2 | exclude/X3 | no eligible comparator (none of ['placebo']). |
| sglt2-primary-prevention-hf | NCT04071626 | exclude/X2 | exclude/X-DESIGN | required design/context absent: record does not mention any of ['cardiovascular outcome', 'cardiovascular outcomes', 'ca |

## Flip counts per topic (decisions that change; INCLUDE = newly eligible by the record screen)

| topic | active | changed | -> INCLUDE | exclusion reason only |
|---|---|---|---|---|
| dpp4-mace-t2d | yes | 7 | 3 | 4 |
| metformin-pcos-ovulation | no | 6 | 2 | 4 |
| sglt2-primary-prevention-hf | yes | 3 | 0 | 3 |
| empagliflozin-hfpef-hosp | yes | 1 | 1 | 0 |
| esketamine-trd-madrs | yes | 1 | 1 | 0 |
| finerenone-ckd-t2d-renal | yes | 1 | 1 | 0 |
| melatonin-primary-insomnia-sol | yes | 1 | 1 | 0 |
| colchicine-secondary-cv-prevention | no | 1 | 1 | 0 |
| the other 24 topics | | 0 | 0 | 0 |

## G1 effect, stated BEFORE applying

| topic | G1 today | effect |
|---|---|---|
| **dpp4-mace-t2d** | G1_MATCHED | **AT RISK.** NCT00918879 (saxagliptin), NCT02192853 (sitagliptin) and NCT02792400 (linagliptin) are admitted by the role-aware placebo ('<gliptin> placebo' in the registration) -- correct under the protocol AS WRITTEN (P/I/C only), but they are glycaemic/mechanistic trials outside comparator 31462224. Under the literal rule dpp4 leaves G1_MATCHED; under the draft B-prime-style amendment (outputs/k_gap/v15_bprime_drafts.md, ruling 2) they are outside (MACE not an efficacy endpoint) and dpp4 stays matched. **This is the ruling-2 decision, now forced by a correct screen.** |
| empagliflozin-hfpef-hosp | G1_MATCHED | AT RISK unless SAK is named TARGET_RESULT_ABSENT (V15 K-3). |
| esketamine-trd-madrs | G1_MATCHED | NCT01998958 excluded by a typed span (29282469: 'Participants continued their existing antidepressant treatment' v protocol 'newly-initiated'); stays matched (V15 K-9). |
| finerenone-ckd-t2d-renal | G1_MATCHED | none (ARTS-DN Japan already named). |
| melatonin-primary-insomnia-sol | NOT_YET | none. |
| metformin-pcos-ovulation, colchicine-secondary | abandoned | none (Legro PPCOS I 17287476 now eligible: r27-B). |
