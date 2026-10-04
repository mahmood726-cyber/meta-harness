# G1-R reproduction (derived: scripts/g1r_reproduction.py)

Does OUR engine (harness.secondary_meta.pool: FE / DL / PM / REML, +/- HK; pool_mh: Mantel-Haenszel from counts) reproduce each comparator's printed pooled result from the comparator's OWN per-trial rows, under the comparator's STATED model? A separate metric from G1.

- tally: {'REPRODUCED': 24, 'NO_COMPARATOR_ROWS': 8}

| topic | comparator | rows (source) | stated model | printed pool | our engine (stated) | verdict | note |
|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | PMID 30140441 | 5 (DUAL_READ Fig3) | ['DL', 'PM', 'REML'] | 0.929 (0.851-1.014) | DL [0.9284, 0.8505, 1.0136]; PM [0.9284, 0.8505, 1.0136]; REML [0.9284, 0.8505, 1.0136] | **REPRODUCED** | by DL, PM, REML |
| colchicine-postop-af | PMID 36050741 | 9 (DUAL_READ Fig2) | ['MH-RE'] | 0.62 (0.52-0.74) | MH-RE [0.6198, 0.5204, 0.7383] | **REPRODUCED** | by MH-RE |
| colchicine-recurrent-pericarditis | PMID 22442198 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: NO_JATS |
| colchicine-secondary-cv-prevention | PMID 36176989 | 7 (DUAL_READ F3) | ['MH-FE', 'MH-RE'] | 0.54 (0.38-0.77) | MH-FE [0.6496, 0.5609, 0.7524]; MH-RE [0.5373, 0.3768, 0.7661] | **REPRODUCED** | by MH-RE |
| corticosteroids-cap-mortality | PMID 38128217 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: NO_JATS |
| corticosteroids-covid19-mortality | PMID 32876694 | 7 (DUAL_READ joi200104f2) | ['FE', 'PM', 'PM+HK'] | 0.66 (0.53-0.82) | FE [0.6628, 0.5346, 0.8218]; PM [0.6956, 0.5216, 0.9276]; PM+HK [0.6956, 0.4856, 0.9963] | **REPRODUCED** | by FE |
| dapagliflozin-hfpef-hosp | PMID 36914068 | 6 (DUAL_READ fig1) | ['FE'] | 0.80 (0.74-0.86) | FE [0.7976, 0.7377, 0.8624] | **REPRODUCED** | by FE |
| denosumab-vertebral-fracture | PMID 36852077 | 2 (DUAL_READ mmc1.pdf#p43) | ['REML'] | 0.32 (0.26-0.41) | REML [0.3201, 0.255, 0.4017] | **REPRODUCED** | by REML |
| doac-vte-recurrence | PMID 24963045 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: NO_JATS |
| dpp4-mace-t2d | PMID 34754403 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: REFUSED_BEFORE_READING:NO_TOPIC_OUTCOME_PANEL: the comparator's only forest figure (panels A-F: MI, stroke, HHF, unstable angina, revascularisation, CV mortality) has no 3-point MACE panel |
| empagliflozin-hfpef-hosp | PMID 37773799 | 6 (DUAL_READ F2) | ['DL'] | 0.80 (0.74-0.87) | DL [0.7981, 0.736, 0.8654] | **REPRODUCED** | by DL |
| esketamine-trd-madrs | PMID 42490943 | 4 (DUAL_READ f4) | ['DL', 'DL+HK', 'FE', 'REML', 'REML+HK'] | -2.99 (-5.10--0.89) | DL [-2.9921, -5.0972, -0.887]; DL+HK [-2.9921, -6.6035, 0.6193]; FE [-3.2159, -4.6809, -1.7508]; REML [-2.9989, -5.0763, -0.9215]; REML+HK [-2.9989, -6.6022, 0.6044] | **REPRODUCED** | by DL |
| finerenone-ckd-t2d-renal | PMID 36742404 | 2 (DUAL_READ f2) | ['DL', 'FE', 'PM', 'REML'] | 0.84 (0.77-0.92) | DL [0.8404, 0.766, 0.9219]; FE [0.8404, 0.766, 0.9219]; PM [0.8404, 0.766, 0.9219]; REML [0.8404, 0.766, 0.9219] | **REPRODUCED** | by DL, FE, PM, REML |
| glp1-ra-mace-t2d | PMID 34526024 | 8 (DUAL_READ Fig3) | ['PM', 'PM+HK'] | 0.86 (0.79-0.94) | PM [0.861, 0.7993, 0.9274]; PM+HK [0.861, 0.7872, 0.9417] | **REPRODUCED** | by PM+HK |
| iv-iron-hfref-hosp | PMID 39727669 | 5 (DUAL_READ diseases-12-00339-f003) | ['DL'] | 0.59 (0.40-0.88) | DL [0.5879, 0.3944, 0.8763] | **REPRODUCED** | by DL |
| melatonin-primary-insomnia-sol | PMID 23691095 | 15 (DUAL_READ pone-0063773-g001) | ['DL', 'FE', 'PM', 'REML'] | 7.06 (4.37-9.75) | DL [9.4873, 4.5092, 14.4653]; FE [7.0606, 4.3765, 9.7448]; PM [9.6253, 4.3752, 14.8754]; REML [9.5779, 4.4248, 14.731] | **REPRODUCED** | by FE |
| metformin-pcos-ovulation | PMID 31845767 | 21 (DUAL_READ CD013505-fig-0024) | ['MH-FE'] | 1.65 (1.35-2.03) | MH-FE [1.6547, 1.3485, 2.0305] | **REPRODUCED** | by MH-FE |
| noac-vs-warfarin-af-stroke | PMID 34985309 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | ROWS_NOT_AGREED_AS_TRIALS: ROWS_ARE_NOT_STUDIES:outcome/outcome |
| omega3-cardiovascular-events | PMID 35905212 | 22 (DUAL_READ F2) | ['DL', 'PM', 'REML'] | 0.94 (0.89-1.00) | DL [0.9439, 0.8909, 1.0001]; PM [0.9425, 0.8679, 1.0237]; REML [0.9439, 0.8923, 0.9985] | **REPRODUCED** | by DL, REML |
| pcsk9-mace | PMID 36531722 | 12 (DUAL_READ Data_Sheet_1.PDF#p7) | ['DL', 'FE', 'PM', 'REML'] | 0.83 (0.79-0.87) | DL [0.8298, 0.7866, 0.8753]; FE [0.8333, 0.7995, 0.8686]; PM [0.8319, 0.7943, 0.8712]; REML [0.8244, 0.7666, 0.8865] | **REPRODUCED** | by DL, FE, PM |
| probiotics-aad-prevention | PMID 34385227 | 42 (DUAL_READ F3) | ['MH-RE'] | 0.63 (0.54-0.73) | MH-RE [0.6256, 0.5356, 0.7307] | **REPRODUCED** | by MH-RE |
| sacubitril-valsartan-hfref | PMID 36722326 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: rows are treatments (network estimates), not trials |
| semaglutide-obesity-mace | PMID 39345822 | 7 (DUAL_READ fig2-17562864241281903) | ['MH-RE'] | 0.79 (0.71-0.89) | MH-RE [0.7933, 0.7083, 0.8884] | **REPRODUCED** | by MH-RE |
| semaglutide-obesity-weight | PMID 42536519 | 4 (TYPED_TABLE T3) | ['DL', 'PM', 'REML'] | -11.85 (-12.81--10.90) | DL [-11.8537, -12.8063, -10.9011]; PM [-11.8489, -12.8142, -10.8837]; REML [-11.8466, -12.8182, -10.875] | **REPRODUCED** | by DL |
| sglt2-ckd-progression | PMID 41203232 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: REFUSED_BEFORE_READING:NO_PER_TRIAL_TOPIC_FIGURE: the comparator's figures are CKD-progression / eGFR outcomes by baseline eGFR or UACR SUBGROUP, not per-trial rows of the trial-defined cardiorenal composite |
| sglt2-hfref-hosp-cvdeath | PMID 35112512 | 3 (DUAL_READ ehf213805-fig-0002) | ['DL'] | 0.74 (0.68-0.81) | DL [0.7437, 0.6793, 0.8142] | **REPRODUCED** | by DL |
| sglt2-primary-prevention-hf | PMID 33519713 | 8 (DUAL_READ f2) | ['MH-RE'] | 0.63 (0.53-0.74) | MH-RE [0.6262, 0.5328, 0.736] | **REPRODUCED** | by MH-RE |
| spironolactone-hfref-mortality | PMID 40959489 | 3 (DUAL_READ F4) | ['FE'] | 0.78 (0.72-0.85) | FE [0.7841, 0.7196, 0.8544] | **REPRODUCED** | by FE |
| statins-primary-prevention-elderly | PMID 39076238 | 11 (DUAL_READ S3.F2) | ['DL', 'FE'] | 0.75 (0.66-0.85) | DL [0.7488, 0.6603, 0.8493]; FE [0.8751, 0.8566, 0.8941] | **REPRODUCED** | by DL |
| ticagrelor-vs-clopidogrel-acs | PMID 28545073 | 5 (DUAL_READ pone.0177872.g004) | ['MH-FE'] | 0.83 (0.77-0.90) | MH-FE [0.8338, 0.7748, 0.8972] | **REPRODUCED** | by MH-FE |
| tocilizumab-covid19-mortality | PMID 34228774 | 29 (DUAL_READ joi210079f1) | ['FE', 'REML', 'REML+HK'] | 0.86 (0.79-0.95) | FE [0.8696, 0.7901, 0.9571]; REML [0.8964, 0.7767, 1.0347]; REML+HK [0.8964, 0.786, 1.0224] | **REPRODUCED** | by FE |
| tranexamic-acid-pph | PMID 39461793 | - (-) |  |  (-) |  | **NO_COMPARATOR_ROWS** | NOT_READ: REFUSED_BEFORE_READING:NO_TOPIC_OUTCOME_FIGURE: the comparator's figures are life-threatening bleeding (a composite of death or surgical intervention) and thromboembolic events; none is death due to bleeding |
