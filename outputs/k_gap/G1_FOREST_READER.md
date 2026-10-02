# G1 dual-model forest-plot reader (derived: scripts/g1_forest_reader.py)

Two model families read each forest figure (codex `gpt-6-astra`; agy `Gemini 3.1 Pro (High)`), every call recorded under evidence/model_calls/forest/ and replayed byte-identically. A row is PROPOSED only when both readings agree within the printed rounding; a figure is ACCEPTED only when the agreed rows, pooled by the meta's STATED model, reproduce its printed pool and CI. Accepted rows are SECONDARY rows: never pool inputs, never counted toward agreement with their own meta; another meta's rows feed the two-source rule.

- comparators of 32 tracker topics; other metas selected by the two-source sweep: 0
- ALL: figures read by both models 25; ACCEPTED 16, REFUSED 9 (pooled-reconstruction pass rate 16 of 25); rows proposed 205, refused (readings disagree) 13, accepted as secondary 147
- comparators: figures read by both models 25; ACCEPTED 16, REFUSED 9 (pooled-reconstruction pass rate 16 of 25); rows proposed 205, refused (readings disagree) 13, accepted as secondary 147
- other metas (two-source sweep): figures read by both models 0; ACCEPTED 0, REFUSED 0 (pooled-reconstruction pass rate 0 of 0); rows proposed 0, refused (readings disagree) 0, accepted as secondary 0

## Comparators

| topic | meta | figure | state | rows proposed / refused | stated model | printed pool | reconstructed | why |
|---|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | PMID 30140441 | Fig3 | **ACCEPTED** | 5 / 0 | STATED ['DL', 'PM', 'REML'] | 0.929 (0.851-1.014) | DL 0.9284 (0.8505-1.0136); PM 0.9284 (0.8505-1.0136); REML 0.9284 (0.8505-1.0136) | - |
| colchicine-postop-af | PMID 36050741 | Fig2 | **ACCEPTED** | 9 / 0 | STATED ['MH-RE'] | 0.62 (0.52-0.74) | MH-RE 0.6198 (0.5204-0.7383) | - |
| colchicine-secondary-cv-prevention | PMID 36176989 | F3 | **REFUSED** | 6 / 1 | STATED ['MH-FE'] | 0.54 (0.38-0.77) | MH-FE 0.6465 (0.5575-0.7496) | ROWS_DISAGREE:1, RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| corticosteroids-covid19-mortality | PMID 32876694 | joi200104f2 | **ACCEPTED** | 7 / 0 | STATED ['FE', 'PM', 'PM+HK'] | 0.66 (0.53-0.82) | FE 0.6593 (0.5323-0.8167); PM 0.6962 (0.5183-0.9350); PM+HK 0.6962 (0.4817-1.0061) | - |
| dapagliflozin-hfpef-hosp | PMID 36914068 | fig1 | **REFUSED** | 6 / 8 | STATED ['FE'] | 0.80 (0.74-0.86) | FE 0.7976 (0.7377-0.8624) | ROWS_DISAGREE:8 |
| empagliflozin-hfpef-hosp | PMID 37773799 | F2 | **ACCEPTED** | 6 / 0 | STATED ['DL'] | 0.80 (0.74-0.87) | DL 0.7981 (0.7360-0.8654) | - |
| esketamine-trd-madrs | PMID 42490943 | f4 | **ACCEPTED** | 4 / 0 | STATED ['DL', 'DL+HK', 'FE', 'REML', 'REML+HK'] | -2.99 (-5.10--0.89) | DL -2.9921 (-5.0972--0.8870); DL+HK -2.9921 (-6.6035-0.6193); FE -3.2159 (-4.6809--1.7508); REML -2.9989 (-5.0763--0.9215); REML+HK -2.9989 (-6.6022-0.6044) | - |
| finerenone-ckd-t2d-renal | PMID 36742404 | f2 | **ACCEPTED** | 2 / 0 | STATED ['DL', 'FE', 'PM', 'REML'] | 0.84 (0.77-0.92) | DL 0.8404 (0.7660-0.9219); FE 0.8404 (0.7660-0.9219); PM 0.8404 (0.7660-0.9219); REML 0.8404 (0.7660-0.9219) | - |
| glp1-ra-mace-t2d | PMID 34526024 | Fig3 | **ACCEPTED** | 8 / 0 | STATED ['PM', 'PM+HK'] | 0.86 (0.79-0.94) | PM 0.8610 (0.7993-0.9274); PM+HK 0.8610 (0.7872-0.9417) | - |
| iv-iron-hfref-hosp | PMID 39727669 | diseases-12-00339-f003 | **ACCEPTED** | 5 / 0 | STATED ['DL'] | 0.59 (0.40-0.88) | DL 0.5907 (0.3965-0.8800) | - |
| melatonin-primary-insomnia-sol | PMID 23691095 | pone-0063773-g001 | **REFUSED** | 0 / 0 | STATED ['DL', 'FE', 'PM', 'REML'] | 7.06 (4.37-9.75) |  | ROWS_ARE_NOT_STUDIES:mixed/study, FEWER_THAN_2_AGREED_ROWS |
| metformin-pcos-ovulation | PMID 31845767 | CD013505-fig-0024 | **REFUSED** | 20 / 1 | STATED ['FE', 'MH-FE'] | 1.65 (1.35-2.03) | FE 1.5805 (1.2734-1.9617); MH-FE 1.6598 (1.3507-2.0397) | ROWS_DISAGREE:1 |
| noac-vs-warfarin-af-stroke | PMID 34985309 | F1 | **REFUSED** | 0 / 0 | NOT_RECONSTRUCTABLE [] | 0.81 (0.74-0.89) |  | ROWS_ARE_NOT_STUDIES:outcome/outcome, STATED_MODEL_NOT_RECONSTRUCTABLE, FEWER_THAN_2_AGREED_ROWS |
| omega3-cardiovascular-events | PMID 35905212 | F2 | **ACCEPTED** | 22 / 0 | STATED ['DL', 'PM', 'REML'] | 0.94 (0.89-1.00) | DL 0.9439 (0.8909-1.0001); PM 0.9425 (0.8679-1.0237); REML 0.9439 (0.8923-0.9985) | - |
| pcsk9-mace | PMID 36531722 | F2 | **REFUSED** | 0 / 0 | STATED ['DL', 'FE', 'PM', 'REML'] | NNTB 36 (NNTB 29-NNTB 47) |  | ROWS_ARE_NOT_STUDIES:subgroup/subgroup, FEWER_THAN_2_AGREED_ROWS |
| probiotics-aad-prevention | PMID 34385227 | F3 | **ACCEPTED** | 42 / 0 | STATED ['MH-RE'] | 0.63 (0.54-0.73) | MH-RE 0.6256 (0.5356-0.7307) | - |
| semaglutide-obesity-mace | PMID 39345822 | fig2-17562864241281903 | **ACCEPTED** | 7 / 0 | STATED ['MH-RE'] | 0.79 (0.71-0.89) | MH-RE 0.7933 (0.7083-0.8884) | - |
| semaglutide-obesity-weight | PMID 42536519 | F3 | **REFUSED** | 0 / 0 | STATED ['DL', 'MH-RE', 'PM', 'REML'] |  (-) |  | NOT_LEGIBLE_IN_BOTH, POOLED_ROW_DISAGREES |
| sglt2-hfref-hosp-cvdeath | PMID 35112512 | ehf213805-fig-0002 | **ACCEPTED** | 3 / 0 | STATED ['DL'] | 0.74 (0.68-0.81) | DL 0.7437 (0.6793-0.8142) | - |
| sglt2-primary-prevention-hf | PMID 33519713 | f2 | **ACCEPTED** | 8 / 0 | STATED ['MH-RE'] | 0.63 (0.53-0.74) | MH-RE 0.6262 (0.5328-0.7360) | - |
| spironolactone-hfref-mortality | PMID 40959489 | F4 | **ACCEPTED** | 3 / 0 | STATED ['FE'] | 0.78 (0.72-0.85) | FE 0.7841 (0.7196-0.8544) | - |
| statins-primary-prevention-elderly | PMID 39076238 | S3.F2 | **ACCEPTED** | 11 / 0 | STATED ['DL', 'FE'] | 0.75 (0.66-0.85) | DL 0.7488 (0.6603-0.8493); FE 0.8751 (0.8566-0.8941) | - |
| ticagrelor-vs-clopidogrel-acs | PMID 28545073 | pone.0177872.g004 | **ACCEPTED** | 5 / 0 | STATED ['MH-FE'] | 0.83 (0.77-0.90) | MH-FE 0.8338 (0.7748-0.8972) | - |
| tocilizumab-covid19-mortality | PMID 34228774 | joi210079f1 | **REFUSED** | 26 / 3 | STATED ['FE', 'REML', 'REML+HK'] | 0.86 (0.79-0.95) | FE 0.8688 (0.7896-0.9560); REML 0.8945 (0.7749-1.0326); REML+HK 0.8945 (0.7741-1.0338) | ROWS_DISAGREE:3, ROW_COUNTS_DO_NOT_GIVE_PRINTED_LOWER:COVIDOSE2-SS-A |
| tranexamic-acid-pph | PMID 39461793 | F2 | **REFUSED** | 0 / 0 | NOT_STATED [] | 0.77 (0.63-0.93) |  | ROWS_ARE_NOT_STUDIES:mixed/mixed, STATED_MODEL_NOT_STATED, FEWER_THAN_2_AGREED_ROWS |

## Other open-access metas citing unmatched comparator trials (two-source sweep)

| topic | meta | figure | state | rows proposed / refused | stated model | printed pool | reconstructed | why |
|---|---|---|---|---|---|---|---|---|

## Not read (typed reason)

- colchicine-recurrent-pericarditis: PMID 22442198: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://heart.bmj.com/content/heartjnl/98/14/1078.full.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://heart.bmj.com/content/hear): a bot challenge is not solved)
- corticosteroids-cap-mortality: PMID 38128217: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (hybrid, https://doi.org/10.1016/j.jcrc.2023.154507: NOT_A_PDF (HTTP 200))
- denosumab-vertebral-fracture: PMID 36852077: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: direct and indirect head-to-head estimates (treatments), not trial rows
- doac-vte-recurrence: PMID 24963045: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://ashpublications.org/blood/article-pdf/124/12/1968/1379490/1968.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://ashpublications.org/blood/): a bot challenge is not solved)
- dpp4-mace-t2d: PMID 34754403: REFUSED_BEFORE_READING:NO_TOPIC_OUTCOME_PANEL: the comparator's only forest figure (panels A-F: MI, stroke, HHF, unstable angina, revascularisation, CV mortality) has no 3-point MACE panel
- sacubitril-valsartan-hfref: PMID 36722326: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: rows are treatments (network estimates), not trials
- sglt2-ckd-progression: PMID 41203232: REFUSED_BEFORE_READING:NO_PER_TRIAL_TOPIC_FIGURE: the comparator's figures are CKD-progression / eGFR outcomes by baseline eGFR or UACR SUBGROUP, not per-trial rows of the trial-defined cardiorenal composite

## Disagreements (both readings shown)

- colchicine-secondary-cv-prevention / Newton N–2019 / Mewton N-2019: LABEL_DISAGREES; codex {"label": "Newton N–2019", "effect": "0.90", "lower": "0.27", "upper": "3.01", "weight_pct": "6.5%", "events_t": "5", "n_t": "101", "events_c": "5", "n_c": "91"}; agy {"label": "Mewton N-2019", "effect": "0.90", "lower": "0.27", "upper": "3.01", "weight_pct": "6.5%", "events_t": "5", "n_t": "101", "events_c": "5", "n_c": "91"}
- dapagliflozin-hfpef-hosp / SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF: ONLY_IN_READING_A; codex {"label": "SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF", "effect": "0.63", "lower": "0.45", "upper": "0.88", "weight_pct": "9.6%", "events_t": null, "n_t": "368", "events_c": null, "n_c": "371"}; agy null
- dapagliflozin-hfpef-hosp / DELIVER Solomon et al(2022) HFpEF>60%: ONLY_IN_READING_A; codex {"label": "DELIVER Solomon et al(2022) HFpEF>60%", "effect": "0.78", "lower": "0.62", "upper": "0.98", "weight_pct": "20.7%", "events_t": null, "n_t": "931", "events_c": null, "n_c": "960"}; agy null
- dapagliflozin-hfpef-hosp / DELIVER Solomon et al(2022) HFpEF50-59%: ONLY_IN_READING_A; codex {"label": "DELIVER Solomon et al(2022) HFpEF50-59%", "effect": "0.79", "lower": "0.65", "upper": "0.97", "weight_pct": "27.0%", "events_t": null, "n_t": "1133", "events_c": null, "n_c": "1123"}; agy null
- dapagliflozin-hfpef-hosp / EMPEROR-P Anker et al (2021) HFpEF50-59%: ONLY_IN_READING_A; codex {"label": "EMPEROR-P Anker et al (2021) HFpEF50-59%", "effect": "0.80", "lower": "0.64", "upper": "0.99", "weight_pct": "22.8%", "events_t": null, "n_t": "1028", "events_c": null, "n_c": "1030"}; agy null
- dapagliflozin-hfpef-hosp / EMPEROR-P Anker et al (2021) HFpEF ≥60%: ONLY_IN_READING_A; codex {"label": "EMPEROR-P Anker et al (2021) HFpEF ≥60%", "effect": "0.87", "lower": "0.69", "upper": "1.10", "weight_pct": "19.9%", "events_t": null, "n_t": "974", "events_c": null, "n_c": "973"}; agy null
- dapagliflozin-hfpef-hosp / SOLOIST-WHF/SCORED Bhatt et al (2021) HFmrEF .: ONLY_IN_READING_A; codex {"label": "SOLOIST-WHF/SCORED Bhatt et al (2021) HFmrEF .", "effect": "0.61", "lower": "0.40", "upper": "0.94", "weight_pct": "10.5%", "events_t": null, "n_t": "226", "events_c": null, "n_c": "230"}; agy null
- dapagliflozin-hfpef-hosp / EMPEROR-P Anker et al (2021) HFmrEF: ONLY_IN_READING_A; codex {"label": "EMPEROR-P Anker et al (2021) HFmrEF", "effect": "0.71", "lower": "0.57", "upper": "0.88", "weight_pct": "40.7%", "events_t": null, "n_t": "995", "events_c": null, "n_c": "988"}; agy null
- dapagliflozin-hfpef-hosp / DELIVER Solomon et al (2022) HFmrEF: ONLY_IN_READING_A; codex {"label": "DELIVER Solomon et al (2022) HFmrEF", "effect": "0.88", "lower": "0.72", "upper": "1.07", "weight_pct": "48.8%", "events_t": null, "n_t": "1067", "events_c": null, "n_c": "1049"}; agy null
- metformin-pcos-ovulation / Hemmings? / Heathcote 2013: LABEL_DISAGREES; codex {"label": "Hemmings?", "effect": "1.33", "lower": "0.24", "upper": "7.56", "weight_pct": "1.6", "events_t": "10", "n_t": "13", "events_c": "10", "n_c": "14"}; agy {"label": "Heathcote 2013", "effect": "1.33", "lower": "0.24", "upper": "7.56", "weight_pct": "1.6 %", "events_t": "10", "n_t": "13", "events_c": "10", "n_c": "14"}
- tocilizumab-covid19-mortality / COVIDSTORM: LOWER_DISAGREES,UPPER_DISAGREES; codex {"label": "COVIDSTORM", "effect": "NAᵇ", "lower": null, "upper": null, "weight_pct": null, "events_t": "0", "n_t": "26", "events_c": "0", "n_c": "13"}; agy {"effect": "NAb", "events_c": "0", "events_t": "0", "label": "COVIDSTORM", "lower": null, "n_c": "13", "n_t": "26", "upper": null, "weight_pct": null}
- tocilizumab-covid19-mortality / COVITOZ: LOWER_DISAGREES,UPPER_DISAGREES; codex {"label": "COVITOZ", "effect": "NAᵇ", "lower": null, "upper": null, "weight_pct": null, "events_t": "0", "n_t": "17", "events_c": "0", "n_c": "9"}; agy {"effect": "NAb", "events_c": "0", "events_t": "0", "label": "COVITOZ", "lower": null, "n_c": "9", "n_t": "17", "upper": null, "weight_pct": null}
- tocilizumab-covid19-mortality / TOCOVID: LOWER_DISAGREES,UPPER_DISAGREES; codex {"label": "TOCOVID", "effect": "NAᵇ", "lower": null, "upper": null, "weight_pct": null, "events_t": "0", "n_t": "136", "events_c": "0", "n_c": "134"}; agy {"effect": "NAb", "events_c": "0", "events_t": "0", "label": "TOCOVID", "lower": null, "n_c": "134", "n_t": "136", "upper": null, "weight_pct": null}
