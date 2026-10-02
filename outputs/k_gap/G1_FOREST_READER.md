# G1 dual-model forest-plot reader (derived: scripts/g1_forest_reader.py)

Two model families read each forest figure (codex `gpt-6-astra`; agy `Gemini 3.1 Pro (High)`), every call recorded under evidence/model_calls/forest/ and replayed byte-identically. A row is PROPOSED only when both readings agree within the printed rounding; a figure is ACCEPTED only when the agreed rows, pooled by the meta's STATED model, reproduce its printed pool and CI. Accepted rows are SECONDARY rows: never pool inputs, never counted toward agreement with their own meta; another meta's rows feed the two-source rule.

- comparators of 32 tracker topics; other metas selected by the two-source sweep: 32
- ALL: figures read by both models 33; ACCEPTED 20, REFUSED 13 (pooled-reconstruction pass rate 20 of 33); rows proposed 236, refused (readings disagree) 30, accepted as secondary 169
- comparators: figures read by both models 25; ACCEPTED 16, REFUSED 9 (pooled-reconstruction pass rate 16 of 25); rows proposed 205, refused (readings disagree) 13, accepted as secondary 147
- other metas (two-source sweep): figures read by both models 8; ACCEPTED 4, REFUSED 4 (pooled-reconstruction pass rate 4 of 8); rows proposed 31, refused (readings disagree) 17, accepted as secondary 22

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
| colchicine-secondary-cv-prevention | PMID 39431112 | fig4 | **ACCEPTED** | 6 / 0 | STATED ['DL', 'FE'] | 1.09 (0.89-1.33) | DL 1.0840 (0.8437-1.3929); FE 1.0919 (0.8943-1.3333) | - |
| colchicine-secondary-cv-prevention | PMID 40314333 | ehaf174-F1 | **REFUSED** | 4 / 0 | STATED ['DL'] | 0.75 (0.56-0.93) | DL 0.7574 (0.5980-0.9591) | RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| dapagliflozin-hfpef-hosp | PMID 33859839 | fig3 | **REFUSED** | 5 / 10 | STATED ['MH-RE'] | 0.75 (0.68-0.84) | MH-RE 0.7541 (0.6771-0.8398) | ROWS_DISAGREE:10 |
| iv-iron-hfref-hosp | PMID 33586856 | ehf213146-fig-0002 | **ACCEPTED** | 3 / 0 | STATED ['MH-FE'] | 0.68 (0.54-0.84) | MH-FE 0.6750 (0.5423-0.8402) | - |
| iv-iron-hfref-hosp | PMID 37632415 | ehad586-ehad586_ga1 | **REFUSED** | 0 / 6 | NOT_RECONSTRUCTABLE [] |  (-) |  | ROWS_ARE_NOT_STUDIES:outcome/outcome, POOLED_ROW_DISAGREES, ROWS_DISAGREE:6 |
| melatonin-primary-insomnia-sol | PMID 32580450 | jcm-09-01949-f008 | **REFUSED** | 0 / 1 | STATED ['DL', 'PM', 'REML'] |  (-) |  | ROWS_ARE_NOT_STUDIES:subgroup/subgroup, POOLED_ROW_DISAGREES, ROWS_DISAGREE:1 |
| spironolactone-hfref-mortality | PMID 30921200 | F2 | **ACCEPTED** | 3 / 0 | STATED ['MH-FE'] | 0.90 (0.77-1.06) | MH-FE 0.9040 (0.7733-1.0567) | - |
| ticagrelor-vs-clopidogrel-acs | PMID 35155618 | F2 | **ACCEPTED** | 10 / 0 | STATED ['DL', 'PM', 'REML'] | 0.81 (0.60-1.08) | DL 0.8078 (0.6039-1.0805); PM 0.7774 (0.5428-1.1134); REML 0.7788 (0.5460-1.1110) | - |

## Not read (typed reason)

- balanced-crystalloids-vs-saline-mortality::40203016: PMID 40203016: NO_OUTCOME_FOREST_FIGURE
- colchicine-recurrent-pericarditis: PMID 22442198: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://heart.bmj.com/content/heartjnl/98/14/1078.full.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://heart.bmj.com/content/hear): a bot challenge is not solved)
- corticosteroids-cap-mortality: PMID 38128217: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (hybrid, https://doi.org/10.1016/j.jcrc.2023.154507: NOT_A_PDF (HTTP 200))
- dapagliflozin-hfpef-hosp::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- dapagliflozin-hfpef-hosp::36811901: PMID 36811901: NO_OUTCOME_FOREST_FIGURE
- denosumab-vertebral-fracture: PMID 36852077: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: direct and indirect head-to-head estimates (treatments), not trial rows
- doac-vte-recurrence: PMID 24963045: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://ashpublications.org/blood/article-pdf/124/12/1968/1379490/1968.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://ashpublications.org/blood/): a bot challenge is not solved)
- dpp4-mace-t2d: PMID 34754403: REFUSED_BEFORE_READING:NO_TOPIC_OUTCOME_PANEL: the comparator's only forest figure (panels A-F: MI, stroke, HHF, unstable angina, revascularisation, CV mortality) has no 3-point MACE panel
- empagliflozin-hfpef-hosp::35282455: PMID 35282455: NO_OUTCOME_FOREST_FIGURE
- esketamine-trd-madrs::36942150: PMID 36942150: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::29668577: PMID 29668577: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::36335326: PMID 36335326: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::39911073: PMID 39911073: NO_OUTCOME_FOREST_FIGURE:refused clc70065-fig-0002=MULTIPANEL_NO_UNIQUE_PANEL,clc70065-fig-0003=MULTIPANEL_NO_UNIQUE_PANEL,clc70065-fig-0004=MULTIPANEL_NO_UNIQUE_PANEL
- iv-iron-hfref-hosp::21942989: PMID 21942989: NO_OUTCOME_FOREST_FIGURE
- iv-iron-hfref-hosp::34011020: PMID 34011020: NO_OUTCOME_FOREST_FIGURE:refused F3=MULTIPANEL_NO_UNIQUE_PANEL,F4=MULTIPANEL_NO_UNIQUE_PANEL
- iv-iron-hfref-hosp::37010731: PMID 37010731: NO_OUTCOME_FOREST_FIGURE
- pcsk9-mace::29186504: PMID 29186504: NO_OUTCOME_FOREST_FIGURE
- sacubitril-valsartan-hfref: PMID 36722326: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: rows are treatments (network estimates), not trials
- sacubitril-valsartan-hfref::33257469: PMID 33257469: AMBIGUOUS_FIGURE:F4,F6,F8
- semaglutide-obesity-mace::36188627: PMID 36188627: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::36188627: PMID 36188627: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::39676787: PMID 39676787: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression: PMID 41203232: REFUSED_BEFORE_READING:NO_PER_TRIAL_TOPIC_FIGURE: the comparator's figures are CKD-progression / eGFR outcomes by baseline eGFR or UACR SUBGROUP, not per-trial rows of the trial-defined cardiorenal composite
- sglt2-ckd-progression::30412076: PMID 30412076: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::36811901: PMID 36811901: NO_OUTCOME_FOREST_FIGURE
- sglt2-hfref-hosp-cvdeath::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- sglt2-primary-prevention-hf::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- sglt2-primary-prevention-hf::36811901: PMID 36811901: NO_OUTCOME_FOREST_FIGURE
- spironolactone-hfref-mortality::30170387: PMID 30170387: NO_OUTCOME_FOREST_FIGURE
- ticagrelor-vs-clopidogrel-acs::29233189: PMID 29233189: NO_OUTCOME_FOREST_FIGURE

## Disagreements (both readings shown)

- colchicine-secondary-cv-prevention / Newton N–2019 / Mewton N-2019: LABEL_DISAGREES; codex {"effect": "0.90", "events_c": "5", "events_t": "5", "label": "Newton N–2019", "lower": "0.27", "n_c": "91", "n_t": "101", "upper": "3.01", "weight_pct": "6.5%"}; agy {"effect": "0.90", "events_c": "5", "events_t": "5", "label": "Mewton N-2019", "lower": "0.27", "n_c": "91", "n_t": "101", "upper": "3.01", "weight_pct": "6.5%"}
- dapagliflozin-hfpef-hosp / SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF: ONLY_IN_READING_A; codex {"effect": "0.63", "events_c": null, "events_t": null, "label": "SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF", "lower": "0.45", "n_c": "371", "n_t": "368", "upper": "0.88", "weight_pct": "9.6%"}; agy null
- dapagliflozin-hfpef-hosp / DELIVER Solomon et al(2022) HFpEF>60%: ONLY_IN_READING_A; codex {"effect": "0.78", "events_c": null, "events_t": null, "label": "DELIVER Solomon et al(2022) HFpEF>60%", "lower": "0.62", "n_c": "960", "n_t": "931", "upper": "0.98", "weight_pct": "20.7%"}; agy null
- dapagliflozin-hfpef-hosp / DELIVER Solomon et al(2022) HFpEF50-59%: ONLY_IN_READING_A; codex {"effect": "0.79", "events_c": null, "events_t": null, "label": "DELIVER Solomon et al(2022) HFpEF50-59%", "lower": "0.65", "n_c": "1123", "n_t": "1133", "upper": "0.97", "weight_pct": "27.0%"}; agy null
- dapagliflozin-hfpef-hosp / EMPEROR-P Anker et al (2021) HFpEF50-59%: ONLY_IN_READING_A; codex {"effect": "0.80", "events_c": null, "events_t": null, "label": "EMPEROR-P Anker et al (2021) HFpEF50-59%", "lower": "0.64", "n_c": "1030", "n_t": "1028", "upper": "0.99", "weight_pct": "22.8%"}; agy null
- dapagliflozin-hfpef-hosp / EMPEROR-P Anker et al (2021) HFpEF ≥60%: ONLY_IN_READING_A; codex {"effect": "0.87", "events_c": null, "events_t": null, "label": "EMPEROR-P Anker et al (2021) HFpEF ≥60%", "lower": "0.69", "n_c": "973", "n_t": "974", "upper": "1.10", "weight_pct": "19.9%"}; agy null
- dapagliflozin-hfpef-hosp / SOLOIST-WHF/SCORED Bhatt et al (2021) HFmrEF .: ONLY_IN_READING_A; codex {"effect": "0.61", "events_c": null, "events_t": null, "label": "SOLOIST-WHF/SCORED Bhatt et al (2021) HFmrEF .", "lower": "0.40", "n_c": "230", "n_t": "226", "upper": "0.94", "weight_pct": "10.5%"}; agy null
- dapagliflozin-hfpef-hosp / EMPEROR-P Anker et al (2021) HFmrEF: ONLY_IN_READING_A; codex {"effect": "0.71", "events_c": null, "events_t": null, "label": "EMPEROR-P Anker et al (2021) HFmrEF", "lower": "0.57", "n_c": "988", "n_t": "995", "upper": "0.88", "weight_pct": "40.7%"}; agy null
- dapagliflozin-hfpef-hosp / DELIVER Solomon et al (2022) HFmrEF: ONLY_IN_READING_A; codex {"effect": "0.88", "events_c": null, "events_t": null, "label": "DELIVER Solomon et al (2022) HFmrEF", "lower": "0.72", "n_c": "1049", "n_t": "1067", "upper": "1.07", "weight_pct": "48.8%"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Chen Jiao, 2020: ONLY_IN_READING_A; codex {"label": "Chen Jiao, 2020", "effect": "0.82", "lower": "0.26", "upper": "2.58", "weight_pct": "1.8", "events_t": "5", "n_t": "96", "events_c": "6", "n_c": "94"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Kato, 2019: ONLY_IN_READING_A; codex {"label": "Kato, 2019", "effect": "0.59", "lower": "0.37", "upper": "0.94", "weight_pct": "11.2", "events_t": "25", "n_t": "318", "events_c": "47", "n_c": "353"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / McMurray, 2019: ONLY_IN_READING_A; codex {"label": "McMurray, 2019", "effect": "0.83", "lower": "0.70", "upper": "0.98", "weight_pct": "85.6", "events_t": "227", "n_t": "2373", "events_c": "273", "n_c": "2371"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Nassif, 2019: ONLY_IN_READING_A; codex {"label": "Nassif, 2019", "effect": "1.01", "lower": "0.06", "upper": "15.94", "weight_pct": "0.3", "events_t": "1", "n_t": "131", "events_c": "1", "n_c": "132"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Yang Zhen, 2019: ONLY_IN_READING_A; codex {"label": "Yang Zhen, 2019", "effect": "0.74", "lower": "0.17", "upper": "3.13", "weight_pct": "1.1", "events_t": "3", "n_t": "53", "events_c": "4", "n_c": "52"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Chen Jiao, 2020: ONLY_IN_READING_A; codex {"label": "Chen Jiao, 2020", "effect": "0.38", "lower": "0.17", "upper": "0.87", "weight_pct": "2.9", "events_t": "7", "n_t": "96", "events_c": "18", "n_c": "94"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Kato, 2019: ONLY_IN_READING_A; codex {"label": "Kato, 2019", "effect": "0.72", "lower": "0.50", "upper": "1.04", "weight_pct": "15.0", "events_t": "41", "n_t": "318", "events_c": "63", "n_c": "353"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / McMurray, 2019: ONLY_IN_READING_A; codex {"label": "McMurray, 2019", "effect": "0.73", "lower": "0.62", "upper": "0.85", "weight_pct": "77.6", "events_t": "231", "n_t": "2373", "events_c": "318", "n_c": "2371"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Nassif, 2019: ONLY_IN_READING_A; codex {"label": "Nassif, 2019", "effect": "1.26", "lower": "0.51", "upper": "3.09", "weight_pct": "2.5", "events_t": "10", "n_t": "131", "events_c": "8", "n_c": "132"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Yang Zhen, 2019: ONLY_IN_READING_A; codex {"label": "Yang Zhen, 2019", "effect": "0.74", "lower": "0.27", "upper": "1.97", "weight_pct": "2.0", "events_t": "6", "n_t": "53", "events_c": "8", "n_c": "52"}; agy null
- iv-iron-hfref-hosp::37632415 / Total CV hospitalizations and CV death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"label": "Total CV hospitalizations and CV death", "effect": "0.86", "lower": "0.75", "upper": "0.98", "weight_pct": null, "events_t": null, "n_t": "2237", "events_c": null, "n_c": "2233"}; agy {"effect": "0.86", "events_c": "30.5%", "events_t": "27.6%", "label": "Total CV hospitalizations and CV death", "lower": "0.75", "n_c": "2233", "n_t": "2237", "upper": "0.98", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Total HF hospitalizations and CV death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"label": "Total HF hospitalizations and CV death", "effect": "0.87", "lower": "0.75", "upper": "1.01", "weight_pct": null, "events_t": null, "n_t": "2237", "events_c": null, "n_c": "2233"}; agy {"effect": "0.87", "events_c": "25.2%", "events_t": "22.5%", "label": "Total HF hospitalizations and CV death", "lower": "0.75", "n_c": "2233", "n_t": "2237", "upper": "1.01", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Total CV hospitalizations: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"label": "Total CV hospitalizations", "effect": "0.83", "lower": "0.73", "upper": "0.96", "weight_pct": null, "events_t": null, "n_t": "2237", "events_c": null, "n_c": "2233"}; agy {"effect": "0.83", "events_c": "26.4%", "events_t": "22.9%", "label": "Total CV hospitalizations", "lower": "0.73", "n_c": "2233", "n_t": "2237", "upper": "0.96", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Total HF hospitalizations: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"label": "Total HF hospitalizations", "effect": "0.84", "lower": "0.71", "upper": "0.98", "weight_pct": null, "events_t": null, "n_t": "2237", "events_c": null, "n_c": "2233"}; agy {"effect": "0.84", "events_c": "20.2%", "events_t": "17.0%", "label": "Total HF hospitalizations", "lower": "0.71", "n_c": "2233", "n_t": "2237", "upper": "0.98", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Time to CV death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"label": "Time to CV death", "effect": "0.97", "lower": "0.80", "upper": "1.17", "weight_pct": null, "events_t": null, "n_t": "2237", "events_c": null, "n_c": "2233"}; agy {"effect": "0.97", "events_c": "9.8%", "events_t": "9.2%", "label": "Time to CV death", "lower": "0.80", "n_c": "2233", "n_t": "2237", "upper": "1.17", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Time to all-cause death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"label": "Time to all-cause death", "effect": "0.93", "lower": "0.78", "upper": "1.10", "weight_pct": null, "events_t": null, "n_t": "2237", "events_c": null, "n_c": "2233"}; agy {"effect": "0.93", "events_c": "12.7%", "events_t": "11.5%", "label": "Time to all-cause death", "lower": "0.78", "n_c": "2233", "n_t": "2237", "upper": "1.10", "weight_pct": null}
- melatonin-primary-insomnia-sol::32580450 / Placebo/WL: LOWER_DISAGREES,UPPER_DISAGREES; codex {"label": "Placebo/WL", "effect": "0.00", "lower": null, "upper": null, "weight_pct": null, "events_t": null, "n_t": null, "events_c": null, "n_c": null}; agy {"label": "Placebo/WL", "effect": "0.00", "lower": null, "upper": null, "weight_pct": null, "events_t": null, "n_t": null, "events_c": null, "n_c": null}
- metformin-pcos-ovulation / Hemmings? / Heathcote 2013: LABEL_DISAGREES; codex {"effect": "1.33", "events_c": "10", "events_t": "10", "label": "Hemmings?", "lower": "0.24", "n_c": "14", "n_t": "13", "upper": "7.56", "weight_pct": "1.6"}; agy {"effect": "1.33", "events_c": "10", "events_t": "10", "label": "Heathcote 2013", "lower": "0.24", "n_c": "14", "n_t": "13", "upper": "7.56", "weight_pct": "1.6 %"}
- tocilizumab-covid19-mortality / COVIDSTORM: LOWER_DISAGREES,UPPER_DISAGREES; codex {"effect": "NAᵇ", "events_c": "0", "events_t": "0", "label": "COVIDSTORM", "lower": null, "n_c": "13", "n_t": "26", "upper": null, "weight_pct": null}; agy {"effect": "NAb", "events_c": "0", "events_t": "0", "label": "COVIDSTORM", "lower": null, "n_c": "13", "n_t": "26", "upper": null, "weight_pct": null}
- tocilizumab-covid19-mortality / COVITOZ: LOWER_DISAGREES,UPPER_DISAGREES; codex {"effect": "NAᵇ", "events_c": "0", "events_t": "0", "label": "COVITOZ", "lower": null, "n_c": "9", "n_t": "17", "upper": null, "weight_pct": null}; agy {"effect": "NAb", "events_c": "0", "events_t": "0", "label": "COVITOZ", "lower": null, "n_c": "9", "n_t": "17", "upper": null, "weight_pct": null}
- tocilizumab-covid19-mortality / TOCOVID: LOWER_DISAGREES,UPPER_DISAGREES; codex {"effect": "NAᵇ", "events_c": "0", "events_t": "0", "label": "TOCOVID", "lower": null, "n_c": "134", "n_t": "136", "upper": null, "weight_pct": null}; agy {"effect": "NAb", "events_c": "0", "events_t": "0", "label": "TOCOVID", "lower": null, "n_c": "134", "n_t": "136", "upper": null, "weight_pct": null}
