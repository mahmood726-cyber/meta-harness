# G1 tracker (derived: scripts/g1_tracker.py; one source file per topic in outputs/k_gap/g1/)

| topic | k matched | named differences | open gaps | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator |
|---|---|---|---|---|---|---|---|---|---|---|---|
| glp1-ra-mace-t2d | 7 of 7 eligible (comparator N=8) | 1: ELIXA (ESTIMAND_DIFFERENCE) | 0 | 8 | 0 | 0 | 0 | {'AGREE': 6, 'DISAGREE': 1} | HR 0.85 (0.80 to 0.90) vs 0.85 (0.80 to 0.90), k=7, DL: **AGREE** | HR 0.86 (0.81 to 0.91) k=8 | HR 0.86 (0.79 to 0.94) |
| semaglutide-obesity-weight | 2 of 2 eligible (comparator N=4) | 2: O’Neil, 2018 (PROTOCOL_SCOPE_DIFFERENCE), Rubino, 2021 (PROTOCOL_SCOPE_DIFFERENCE) | 0 | 2 | 0 | 0 | 2 | {'AGREE': 2} | MD -11.47 (-13.52 to -9.43) vs -11.49 (-13.58 to -9.41), k=2, DL: **AGREE** | MD -11.47 (no CI) k=2 | MD -11.85 (-12.81 to -10.90) |
| sglt2-hfref-hosp-cvdeath | 2 of 2 eligible (comparator N=4) | 2: EMPEROR‐Preserved (n = 5988) (PROTOCOL_SCOPE_DIFFERENCE), SOLOIST‐WHF (n = 1222) (PROTOCOL_SCOPE_DIFFERENCE) | 0 | 2 | 0 | 0 | 2 | {'AGREE': 1, 'READERS_DIFFER:result=DISAGREE/result_reader2=AGREE': 1} | HR 0.75 (0.68 to 0.83) vs 0.75 (0.68 to 0.83), k=2, FE: **AGREE** | HR 0.75 (no CI) k=2 | HR 0.74 (0.68 to 0.81) |
| tocilizumab-covid19-mortality | 4 of 19 eligible (comparator N=19) | 0:  | 15 | 2 | 2 | 3 | 12 | {'AGREE': 4} | OR [COVERAGE-LIMITED RECONCILIATION, NOT A FINDING: 4 of 19 trials, 13% of REACT's participants; missing RECOVERY (n=4116), REMAP-CAP (n=711)] 1.19 (0.83 to 1.71) vs 1.19 (0.83 to 1.71), k=4, FE: **AGREE** | not printed k=4 | OR 0.83 (0.74 to 0.92) |

## glp1-ra-mace-t2d (comparator PMID 34526024)

- ELIXA: **PRIMARY** - meta 34526024 PRIMARY_VERIFIED PRIMARY_TEXT; vs comparator row: NOT_IN_OUR_POOL; our refusal: no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract
- LEADER: **PRIMARY** - our branch extraction PMID 27295427 (abstract); vs comparator row: AGREE
- SUSTAIN-6: **PRIMARY** - our branch extraction PMID 27633186 (abstract); vs comparator row: AGREE
- EXSCEL: **PRIMARY** - our branch extraction PMID 28910237 (abstract); vs comparator row: AGREE
- HARMONY: **PRIMARY** - our branch extraction PMID 30291013 (abstract); vs comparator row: AGREE
- REWIND: **PRIMARY** - our branch extraction PMID 31189511 (abstract); vs comparator row: AGREE
- PIONEER 6: **PRIMARY** - our branch extraction PMID 31185157 (abstract); vs comparator row: DISAGREE; side: SECONDARY_WRONG (primary numbers are in the primary's own span)
- AMPLITUDE-O: **PRIMARY** - our branch extraction PMID 34215025 (abstract); vs comparator row: AGREE
- NAMED ESTIMAND_DIFFERENCE: ELIXA -- harness.extract.composite_component_mismatch: 3-point MACE outcome but the source composite adds a 4th component (unstable angina) -- a 4-point estimate; refuse rather than pool a different composite under a 3-point label. Registry (AACT 2026-08-30): 'Time to First Occurence of Primary CV Event: CV Death, Non-Fatal MI, Non-Fatal Stroke or Hospitalization for Unstable Angina', arms Placebo 399/3034, Lixisenatide 406/3034, Hazard Ratio (HR) 1.017 (0.886-1.168); the comparator pooled it as {'effect': '1.02', 'lower': '0.89', 'upper': '1.17', 'events_t': None, 'n_t': None, 'events_c': None, 'n_c': None, 'measure': 'HR'}
- COMPARATOR FINDING COMPARATOR_ROW_DIFFERS_FROM_TRIAL_REPORT: PIONEER 6 -- comparator row {'effect': '0.79', 'lower': '0.57', 'upper': '1.10', 'events_t': None, 'n_t': None, 'events_c': None, 'n_c': None, 'measure': 'HR'} vs trial report {'measure': 'HR', 'effect': '0.79', 'lower': '0.57', 'upper': '1.11', 'events_t': None, 'n_t': None, 'events_c': None, 'n_c': None} (SECONDARY_WRONG (primary numbers are in the primary's own span))
- pooled by us, not listed by the comparator: PMID 40162642 (2025; comparator 2021): PUBLISHED_AFTER_COMPARATOR

## semaglutide-obesity-weight (comparator PMID 42536519)

- O’Neil, 2018: **NO_ROW** - IDENTIFICATION (secondary refused: ['OUTCOME_NOT_THE_TOPICS', 'TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL; our refusal: SEEDED PMID 30122305: SCREENED_OUT X2: wrong population: title/conditions mention 'liraglutide'.
- Rubino, 2021: **NO_ROW** - IDENTIFICATION (secondary refused: ['OUTCOME_NOT_THE_TOPICS', 'TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL; our refusal: SEEDED PMID 33755728: SCREENED_OUT X2: wrong population: title/conditions mention 'maintenance'.; comparator row finding: [{'finding': 'ROW_CI_NOT_FROM_ARMS', 'printed_vs_arm_derived': {'lower': ['-14.75', -13.75], 'upper': ['-10.05', -11.05]}}]
- Wadden, 2021: **PRIMARY** - our branch extraction PMID 33625476 (abstract); vs comparator row: AGREE
- Wilding, 2021: **PRIMARY** - our branch extraction PMID 33567185 (abstract); vs comparator row: AGREE
- NAMED PROTOCOL_SCOPE_DIFFERENCE: O’Neil, 2018 -- screen X2 (wrong population: title/conditions mention 'liraglutide'.); protocol rule include.population_none[20] = 'liraglutide'; registered eligibility: Double-blind placebo-controlled RCTs in adults with overweight/obesity without diabetes where once-weekly semaglutide 2.4 mg is compared with placebo (both plus lifestyle). Eligibility is P/I/C/design only. Weight-loss-maintenance/withdrawal designs and diabetes populations are excluded (different estimand/population); a single CT.gov estimand (in-trial/treatment-policy) is pooled consistently.
- NAMED PROTOCOL_SCOPE_DIFFERENCE: Rubino, 2021 -- screen X2 (wrong population: title/conditions mention 'maintenance'.); protocol rule include.population_none[7] = 'maintenance'; registered eligibility: Double-blind placebo-controlled RCTs in adults with overweight/obesity without diabetes where once-weekly semaglutide 2.4 mg is compared with placebo (both plus lifestyle). Eligibility is P/I/C/design only. Weight-loss-maintenance/withdrawal designs and diabetes populations are excluded (different estimand/population); a single CT.gov estimand (in-trial/treatment-policy) is pooled consistently.
- COMPARATOR FINDING ROW_CI_NOT_FROM_ARMS: Rubino, 2021 -- comparator row {'effect': '-12.40', 'lower': '-14.75', 'upper': '-10.05', 'events_t': None, 'n_t': 535, 'events_c': None, 'n_c': 268, 'measure': 'MD'}; {'lower': ['-14.75', -13.75], 'upper': ['-10.05', -11.05]}

## sglt2-hfref-hosp-cvdeath (comparator PMID 35112512)

- DAPA‐HF (n = 4744): **PRIMARY** - our branch extraction PMID 31535829 (ctgov_results); vs comparator row: AGREE
- EMPEROR‐Preserved (n = 5988): **NO_ROW** - IDENTIFICATION; vs comparator row: NOT_IN_OUR_POOL; our refusal: SEEDED PMID 34449189: SCREENED_OUT X2: wrong population: title/conditions mention 'preserved ejection fraction'.
- EMPEROR‐Reduced (n = 3730): **PRIMARY** - our branch extraction PMID 32865377 (abstract); vs comparator row: READERS_DIFFER:result=DISAGREE/result_reader2=AGREE
- SOLOIST‐WHF (n = 1222): **NO_ROW** - UNRESOLVED_IDENTITY; vs comparator row: NOT_IN_OUR_POOL; our refusal: SEEDED PMID 33200892: SCREENED_OUT X3: the randomised intervention is not ['SGLT2', 'SGLT-2', 'sodium-glucose cotransporter 2', 'sodium-glucose co-transporter 2', 'dapagliflozin',
- NAMED PROTOCOL_SCOPE_DIFFERENCE: EMPEROR‐Preserved (n = 5988) -- screen X2 (wrong population: title/conditions mention 'preserved ejection fraction'.); protocol rule include.population_none[0] = 'preserved ejection fraction'; registered eligibility: None
- NAMED PROTOCOL_SCOPE_DIFFERENCE: SOLOIST‐WHF (n = 1222) -- screen X3 (the randomised intervention is not ['SGLT2', 'SGLT-2', 'sodium-glucose cotransporter 2', 'sodium-glucose co-transporter 2', 'dapagliflozin',); protocol rule include.intervention_any = ['SGLT2', 'SGLT-2', 'sodium-glucose cotransporter 2', 'sodium-glucose co-transporter 2', 'dapagliflozin', 'empagliflozin']; registered eligibility: None

## tocilizumab-covid19-mortality (comparator PMID 34228774)

- ARCHITECTS: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- BACC-Bay: **NO_ROW** - only a SAFETY-population count is held (SECONDARY meta 34019122: Stone (BACC) OR 1.15 (0.34-3.87) reproduced from these counts; TEXT PMID 33085857 (safety-population table)); no efficacy-population 28-day count stated; vs comparator row: NO_PRIMARY_ROW; comparator row finding: [{'finding': 'COMPARATOR_ROW_IS_SAFETY_POPULATION', 'source': 'TEXT PMID 33085857 (safety-population table)'}]
- CORIMUNO-TOCI-1: **TWO_SOURCE** - two independent sources: AACT + META; vs comparator row: AGREE
- CORIMUNO-TOCI-ICU: **UNVERIFIED** - one primary source: AACT; no independent second source held; vs comparator row: AGREE
- COV-AID: **NO_ROW** - no held primary source states 28-day deaths per arm (PMID 34756178 (acquired: NCT04330638[si])); vs comparator row: NO_PRIMARY_ROW
- COVACTA: **PRIMARY** - two independent sources: AACT + META + TEXT; vs comparator row: AGREE
- COVIDOSE2-SS-A: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- COVIDSTORM: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- COVINTOC: **NO_ROW** - no held primary source states 28-day deaths per arm (PMID 33676589 (acquired: COVINTOC[tiab])); vs comparator row: NO_PRIMARY_ROW
- COVITOZ: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- EMPACTA: **PRIMARY** - two independent sources: AACT + META + TEXT; vs comparator row: AGREE
- HMO-020-0224: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- ImmCoVA: **NO_ROW** - no held primary source states 28-day deaths per arm (PMID 38157348 + acquired full text); vs comparator row: NO_PRIMARY_ROW
- PreToVid: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- RECOVERY: **UNVERIFIED** - one primary source: TEXT; no independent second source held; vs comparator row: AGREE
- REMAP-CAP: **NO_ROW** - no held primary source states 28-day deaths per arm (PMID 33631065 (acquired: NCT02735707[si] AND (tocilizumab OR interleukin-6)); PMID 40360262 (acquired: cascade:D1+D2+D3)); vs comparator row: NO_PRIMARY_ROW
- REMDACTA: **UNVERIFIED** - one primary source: AACT; no independent second source held; vs comparator row: AGREE
- TOCIBRAS: **TWO_SOURCE** - two independent sources: META + TEXT; vs comparator row: AGREE
- TOCOVID: **NO_ROW** - no primary report held after the full cascade; vs comparator row: NO_PRIMARY_ROW
- COMPARATOR FINDING COMPARATOR_ROW_IS_SAFETY_POPULATION: BACC-Bay -- comparator row {'measure': 'OR', 'effect': None, 'lower': None, 'upper': None, 'events_t': 9, 'n_t': 161, 'events_c': 4, 'n_c': 82} vs trial report {'deaths_t': 9, 'n_t': 161, 'deaths_c': 4, 'n_c': 82}; the comparator's row equals the trial report's SAFETY-population death count (TEXT PMID 33085857 (safety-population table))
