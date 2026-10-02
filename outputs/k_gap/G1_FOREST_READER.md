# G1 dual-model forest-plot reader (derived: scripts/g1_forest_reader.py)

Two model families read each forest figure (codex `gpt-6-astra`; agy `Gemini 3.1 Pro (High)`), every call recorded under evidence/model_calls/forest/ and replayed byte-identically. A row is PROPOSED only when both readings agree within the printed rounding; a figure is ACCEPTED only when the agreed rows, pooled by the meta's STATED model, reproduce its printed pool and CI. Accepted rows are SECONDARY rows: never pool inputs, never counted toward agreement with their own meta; another meta's rows feed the two-source rule.

- comparators of 32 tracker topics; other metas selected by the two-source sweep: 105
- ALL: figures read by both models 57; ACCEPTED 32, REFUSED 25 (pooled-reconstruction pass rate 32 of 57); rows proposed 414, refused (readings disagree) 67, accepted as secondary 267
- comparators: figures read by both models 25; ACCEPTED 17, REFUSED 8 (pooled-reconstruction pass rate 17 of 25); rows proposed 208, refused (readings disagree) 10, accepted as secondary 176
- other metas (two-source sweep): figures read by both models 32; ACCEPTED 15, REFUSED 17 (pooled-reconstruction pass rate 15 of 32); rows proposed 206, refused (readings disagree) 57, accepted as secondary 91

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
| tocilizumab-covid19-mortality | PMID 34228774 | joi210079f1 | **ACCEPTED** | 29 / 0 | STATED ['FE', 'REML', 'REML+HK'] | 0.86 (0.79-0.95) | FE 0.8688 (0.7896-0.9560); REML 0.8945 (0.7749-1.0326); REML+HK 0.8945 (0.7741-1.0338) | - |
| tranexamic-acid-pph | PMID 39461793 | F2 | **REFUSED** | 0 / 0 | NOT_STATED [] | 0.77 (0.63-0.93) |  | ROWS_ARE_NOT_STUDIES:mixed/mixed, STATED_MODEL_NOT_STATED, FEWER_THAN_2_AGREED_ROWS |

## Other open-access metas citing unmatched comparator trials (two-source sweep)

| topic | meta | figure | state | rows proposed / refused | stated model | printed pool | reconstructed | why |
|---|---|---|---|---|---|---|---|---|
| colchicine-postop-af | PMID 36531704 | F4 | **ACCEPTED** | 12 / 0 | STATED ['MH-RE'] | 0.65 (0.56-0.75) | MH-RE 0.6499 (0.5608-0.7532) | - |
| colchicine-secondary-cv-prevention | PMID 38505729 | fig3 | **REFUSED** | 6 / 0 | STATED ['FE'] | 0.70 (0.60-0.83) | FE 0.7097 (0.6007-0.8384) | ROW_COUNTS_DO_NOT_GIVE_PRINTED_UPPER:COLCOT 2019, ROW_COUNTS_DO_NOT_GIVE_PRINTED_EFFECT_LOWER_UPPER:COLIN 2017, ROW_COUNTS_DO_NOT_GIVE_PRINTED_EFFECT_LOWER_UPPER:COPS 2020, ROW_COUNTS_DO_NOT_GIVE_PRINTED_EFFECT_LOWER:LoDoCo 2013, ROW_COUNTS_DO_NOT_GIVE_PRINTED_EFFECT_UPPER:LoDoCo-MI 2019 |
| colchicine-secondary-cv-prevention | PMID 39431112 | fig4 | **ACCEPTED** | 6 / 0 | STATED ['DL', 'FE'] | 1.09 (0.89-1.33) | DL 1.0840 (0.8437-1.3929); FE 1.0919 (0.8943-1.3333) | - |
| colchicine-secondary-cv-prevention | PMID 40314333 | ehaf174-F1 | **REFUSED** | 4 / 0 | STATED ['DL'] | 0.75 (0.56-0.93) | DL 0.7574 (0.5980-0.9591) | RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| dapagliflozin-hfpef-hosp | PMID 33859839 | fig3 | **REFUSED** | 5 / 10 | STATED ['MH-RE'] | 0.75 (0.68-0.84) | MH-RE 0.7541 (0.6771-0.8398) | ROWS_DISAGREE:10 |
| dapagliflozin-hfpef-hosp | PMID 39731023 | Fig8 | **ACCEPTED** | 3 / 0 | STATED ['MH-RE'] | 0.84 (0.30-2.33) | MH-RE 0.8376 (0.3007-2.3338) | - |
| empagliflozin-hfpef-hosp | PMID 39400108 | fig3-17539447241289067 | **ACCEPTED** | 7 / 0 | STATED ['FE'] | 0.78 (0.72-0.85) | FE 0.7834 (0.7221-0.8499) | - |
| empagliflozin-hfpef-hosp | PMID 41999103 | edm270203-fig-0004 | **REFUSED** | 6 / 0 | STATED ['DL', 'PM', 'REML'] | 0.70 (0.55-0.86) |  | ROW_CI_ASYMMETRIC:C Wanner(2016), ROW_CI_ASYMMETRIC:J Butler(2019), ROW_NOT_NUMERIC:SD Anker(2021), ROW_CI_ASYMMETRIC:F Zannad(2021), ROW_NOT_NUMERIC:A Sharma(2023), ROW_CI_ASYMMETRIC:G Filippatos(2023), STATED_MODEL_NOT_COMPUTABLE_FROM_ROWS |
| esketamine-trd-madrs | PMID 36514492 | f0003 | **ACCEPTED** | 10 / 0 | STATED ['FE'] | -2.68 (-3.98--1.37) | FE -2.6753 (-3.9804--1.3701) | - |
| esketamine-trd-madrs | PMID 37194806 | f4 | **REFUSED** | 2 / 1 | STATED ['FE'] | 2.94 (0.89-4.99) | FE 2.8621 (0.6042-5.1200) | ROWS_DISAGREE:1, RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| esketamine-trd-madrs | PMID 40020133 | F2 | **ACCEPTED** | 4 / 0 | STATED ['DL'] | -3.88 (-5.71--2.05) | DL -3.8828 (-5.7144--2.0511) | - |
| esketamine-trd-madrs | PMID 40303446 | f3 | **REFUSED** | 13 / 0 | STATED ['MH-FE'] | -0.08 (-0.10--0.05) |  | STATED_MODEL_NOT_COMPUTABLE_FROM_ROWS |
| finerenone-ckd-t2d-renal | PMID 41272492 | Fig10 | **ACCEPTED** | 5 / 0 | STATED ['MH-RE'] | 0.65 (0.46-0.91) | MH-RE 0.6494 (0.4613-0.9142) | - |
| finerenone-ckd-t2d-renal | PMID 41578591 | F3 | **ACCEPTED** | 5 / 0 | STATED ['FE'] | 0.76 (0.70-0.83) | FE 0.7624 (0.7036-0.8261) | - |
| glp1-ra-mace-t2d | PMID 30223891 | Fig4 | **REFUSED** | 16 / 0 | STATED ['DL', 'FE', 'MH-FE', 'MH-RE'] |  (-) |  | POOLED_ROW_DISAGREES |
| glp1-ra-mace-t2d | PMID 39746343 | F4 | **REFUSED** | 9 / 0 | STATED ['REML'] | 0.89 (0.78-1.02) | REML 0.8905 (0.7852-1.0099) | ROW_CI_ASYMMETRIC:AMPLITUDE–O, ROW_CI_ASYMMETRIC:ELIXA, RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| glp1-ra-mace-t2d | PMID 40652242 | Fig2 | **REFUSED** | 15 / 19 | STATED ['DL', 'DL+HK', 'FE', 'PM', 'PM+HK', 'REML', 'REML+HK'] |  (-) |  | POOLED_ROW_DISAGREES, ROWS_DISAGREE:19 |
| glp1-ra-mace-t2d | PMID 40886073 | pvaf037-F1 | **ACCEPTED** | 10 / 0 | STATED ['DL', 'PM', 'REML'] | 0.87 (0.81-0.93) | DL 0.8685 (0.8062-0.9356); PM 0.8669 (0.7971-0.9429); REML 0.8689 (0.8081-0.9342) | - |
| iv-iron-hfref-hosp | PMID 29174251 | fig0010 | **REFUSED** | 2 / 6 | STATED ['MH-RE'] |  (-) |  | POOLED_ROW_DISAGREES, ROWS_DISAGREE:6 |
| iv-iron-hfref-hosp | PMID 33586856 | ehf213146-fig-0002 | **ACCEPTED** | 3 / 0 | STATED ['MH-FE'] | 0.68 (0.54-0.84) | MH-FE 0.6750 (0.5423-0.8402) | - |
| iv-iron-hfref-hosp | PMID 37632415 | ehad586-ehad586_ga1 | **REFUSED** | 0 / 6 | NOT_RECONSTRUCTABLE [] |  (-) |  | ROWS_ARE_NOT_STUDIES:outcome/outcome, POOLED_ROW_DISAGREES, ROWS_DISAGREE:6 |
| iv-iron-hfref-hosp | PMID 39527395 | Fig5 | **ACCEPTED** | 3 / 0 | STATED ['DL'] | 0.87 (0.69-1.09) | DL 0.8688 (0.6928-1.0896) | - |
| iv-iron-hfref-hosp | PMID 41711738 | xvaf018-F3 | **REFUSED** | 6 / 0 | STATED ['PM'] | 0.75 (0.60-0.94) | PM 0.6864 (0.4835-0.9745) | RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| melatonin-primary-insomnia-sol | PMID 32580450 | jcm-09-01949-f008 | **REFUSED** | 0 / 0 | STATED ['DL', 'PM', 'REML'] |  (-) |  | ROWS_ARE_NOT_STUDIES:subgroup/subgroup, POOLED_ROW_DISAGREES |
| melatonin-primary-insomnia-sol | PMID 36104141 | F5 | **REFUSED** | 8 / 1 | STATED ['DL'] | -0.18 (-0.62-0.26) | DL -0.2219 (-0.8409-0.3970) | ROWS_DISAGREE:1, RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| sacubitril-valsartan-hfref | PMID 34617669 | prp2844-fig-0002 | **REFUSED** | 18 / 0 | STATED ['MH-FE'] |  (-) |  | POOLED_ROW_DISAGREES |
| sacubitril-valsartan-hfref | PMID 36574300 | F2 | **REFUSED** | 0 / 4 | STATED ['DL', 'FE', 'PM', 'REML'] | 0.89 (0.84-0.94) |  | ROWS_DISAGREE:4, FEWER_THAN_2_AGREED_ROWS |
| semaglutide-obesity-weight | PMID 40732345 | pharmaceuticals-18-01058-f004 | **ACCEPTED** | 7 / 0 | STATED ['DL', 'DL+HK'] | -11.57 (-12.94--10.19) | DL -11.5648 (-12.6083--10.5214); DL+HK -11.5648 (-12.9352--10.1945) | - |
| sglt2-ckd-progression | PMID 34349651 | F4 | **ACCEPTED** | 3 / 0 | STATED ['DL', 'FE', 'PM', 'REML'] | 0.64 (0.54-0.75) | DL 0.6355 (0.5404-0.7472); FE 0.6355 (0.5404-0.7472); PM 0.6355 (0.5404-0.7472); REML 0.6355 (0.5404-0.7472) | - |
| sglt2-primary-prevention-hf | PMID 33859839 | fig3 | **REFUSED** | 5 / 10 | STATED ['MH-RE'] |  (-) |  | POOLED_ROW_DISAGREES, ROWS_DISAGREE:10 |
| spironolactone-hfref-mortality | PMID 30921200 | F2 | **ACCEPTED** | 3 / 0 | STATED ['MH-FE'] | 0.90 (0.77-1.06) | MH-FE 0.9040 (0.7733-1.0567) | - |
| ticagrelor-vs-clopidogrel-acs | PMID 35155618 | F2 | **ACCEPTED** | 10 / 0 | STATED ['DL', 'PM', 'REML'] | 0.81 (0.60-1.08) | DL 0.8078 (0.6039-1.0805); PM 0.7774 (0.5428-1.1134); REML 0.7788 (0.5460-1.1110) | - |

## Not read (typed reason)

- balanced-crystalloids-vs-saline-mortality::40203016: PMID 40203016: NO_OUTCOME_FOREST_FIGURE
- colchicine-recurrent-pericarditis: PMID 22442198: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://heart.bmj.com/content/heartjnl/98/14/1078.full.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://heart.bmj.com/content/hear): a bot challenge is not solved)
- colchicine-secondary-cv-prevention::36050741: PMID 36050741: NO_OUTCOME_FOREST_FIGURE
- colchicine-secondary-cv-prevention::36531704: PMID 36531704: NO_OUTCOME_FOREST_FIGURE
- corticosteroids-cap-mortality: PMID 38128217: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (hybrid, https://doi.org/10.1016/j.jcrc.2023.154507: NOT_A_PDF (HTTP 200))
- dapagliflozin-hfpef-hosp::34190162: PMID 34190162: NO_OUTCOME_FOREST_FIGURE
- dapagliflozin-hfpef-hosp::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- dapagliflozin-hfpef-hosp::36811901: PMID 36811901: NO_OUTCOME_FOREST_FIGURE
- dapagliflozin-hfpef-hosp::36994345: PMID 36994345: NO_OUTCOME_FOREST_FIGURE
- denosumab-vertebral-fracture: PMID 36852077: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: direct and indirect head-to-head estimates (treatments), not trial rows
- doac-vte-recurrence: PMID 24963045: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://ashpublications.org/blood/article-pdf/124/12/1968/1379490/1968.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://ashpublications.org/blood/): a bot challenge is not solved)
- dpp4-mace-t2d: PMID 34754403: REFUSED_BEFORE_READING:NO_TOPIC_OUTCOME_PANEL: the comparator's only forest figure (panels A-F: MI, stroke, HHF, unstable angina, revascularisation, CV mortality) has no 3-point MACE panel
- dpp4-mace-t2d::28275958: PMID 28275958: NO_OUTCOME_FOREST_FIGURE
- dpp4-mace-t2d::28432619: PMID 28432619: NO_OUTCOME_FOREST_FIGURE
- empagliflozin-hfpef-hosp::35282455: PMID 35282455: NO_OUTCOME_FOREST_FIGURE
- empagliflozin-hfpef-hosp::39578752: PMID 39578752: NO_OUTCOME_FOREST_FIGURE
- esketamine-trd-madrs::36942150: PMID 36942150: NO_OUTCOME_FOREST_FIGURE
- esketamine-trd-madrs::41235115: PMID 41235115: NO_OUTCOME_FOREST_FIGURE
- esketamine-trd-madrs::41244961: PMID 41244961: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::29668577: PMID 29668577: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::36303247: PMID 36303247: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::36335326: PMID 36335326: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::37811017: PMID 37811017: AMBIGUOUS_FIGURE:F3,F4,F5
- finerenone-ckd-t2d-renal::38273834: PMID 38273834: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::39911073: PMID 39911073: NO_OUTCOME_FOREST_FIGURE:refused clc70065-fig-0002=MULTIPANEL_NO_UNIQUE_PANEL,clc70065-fig-0003=MULTIPANEL_NO_UNIQUE_PANEL,clc70065-fig-0004=MULTIPANEL_NO_UNIQUE_PANEL
- finerenone-ckd-t2d-renal::40213686: PMID 40213686: NO_OUTCOME_FOREST_FIGURE
- finerenone-ckd-t2d-renal::41020003: PMID 41020003: NO_OUTCOME_FOREST_FIGURE
- glp1-ra-mace-t2d::33986377: PMID 33986377: NO_OUTCOME_FOREST_FIGURE
- glp1-ra-mace-t2d::34397684: PMID 34397684: NO_OUTCOME_FOREST_FIGURE
- glp1-ra-mace-t2d::35546664: PMID 35546664: NO_OUTCOME_FOREST_FIGURE
- glp1-ra-mace-t2d::37734450: PMID 37734450: AMBIGUOUS_FIGURE:fig2-01410768231198442,fig3-01410768231198442,fig4-01410768231198442
- glp1-ra-mace-t2d::38953365: PMID 38953365: NO_OUTCOME_FOREST_FIGURE
- iv-iron-hfref-hosp::21942989: PMID 21942989: NO_OUTCOME_FOREST_FIGURE
- iv-iron-hfref-hosp::34011020: PMID 34011020: NO_OUTCOME_FOREST_FIGURE:refused F3=MULTIPANEL_NO_UNIQUE_PANEL,F4=MULTIPANEL_NO_UNIQUE_PANEL
- iv-iron-hfref-hosp::37010731: PMID 37010731: NO_OUTCOME_FOREST_FIGURE
- iv-iron-hfref-hosp::38982752: PMID 38982752: NO_OUTCOME_FOREST_FIGURE
- melatonin-primary-insomnia-sol::35450525: PMID 35450525: NO_OUTCOME_FOREST_FIGURE
- melatonin-primary-insomnia-sol::36079069: PMID 36079069: NO_OUTCOME_FOREST_FIGURE
- melatonin-primary-insomnia-sol::37457117: PMID 37457117: NO_OUTCOME_FOREST_FIGURE
- omega3-cardiovascular-events::34664872: PMID 34664872: NO_OUTCOME_FOREST_FIGURE
- omega3-cardiovascular-events::38317191: PMID 38317191: NO_OUTCOME_FOREST_FIGURE
- pcsk9-mace::27882214: PMID 27882214: NO_OUTCOME_FOREST_FIGURE
- pcsk9-mace::29186504: PMID 29186504: NO_OUTCOME_FOREST_FIGURE
- pcsk9-mace::37007377: PMID 37007377: NO_OUTCOME_FOREST_FIGURE
- pcsk9-mace::40026525: PMID 40026525: NO_OUTCOME_FOREST_FIGURE:refused S3.F3=MULTIPANEL_NO_UNIQUE_PANEL,S3.F4=MULTIPANEL_NO_UNIQUE_PANEL,S3.F5=MULTIPANEL_NO_UNIQUE_PANEL,S3.F6=MULTIPANEL_NO_UNIQUE_PANEL
- pcsk9-mace::40351996: PMID 40351996: AMBIGUOUS_FIGURE:FIG2,FIG3
- sacubitril-valsartan-hfref: PMID 36722326: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: rows are treatments (network estimates), not trials
- sacubitril-valsartan-hfref::33257469: PMID 33257469: AMBIGUOUS_FIGURE:F4,F6,F8
- sacubitril-valsartan-hfref::34993450: PMID 34993450: AMBIGUOUS_FIGURE:fig2,fig3,fig4
- sacubitril-valsartan-hfref::35859597: PMID 35859597: NO_OUTCOME_FOREST_FIGURE
- sacubitril-valsartan-hfref::36353496: PMID 36353496: NO_OUTCOME_FOREST_FIGURE
- sacubitril-valsartan-hfref::36527023: PMID 36527023: NO_OUTCOME_FOREST_FIGURE
- sacubitril-valsartan-hfref::37313196: PMID 37313196: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-mace::36188627: PMID 36188627: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-mace::36769420: PMID 36769420: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-mace::37891683: PMID 37891683: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::36188627: PMID 36188627: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::39676787: PMID 39676787: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::39776746: PMID 39776746: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::40890879: PMID 40890879: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::41820778: PMID 41820778: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::41850241: PMID 41850241: NO_OUTCOME_FOREST_FIGURE
- semaglutide-obesity-weight::42673571: PMID 42673571: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression: PMID 41203232: REFUSED_BEFORE_READING:NO_PER_TRIAL_TOPIC_FIGURE: the comparator's figures are CKD-progression / eGFR outcomes by baseline eGFR or UACR SUBGROUP, not per-trial rows of the trial-defined cardiorenal composite
- sglt2-ckd-progression::29524188: PMID 29524188: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::30412076: PMID 30412076: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::33859839: PMID 33859839: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::36034443: PMID 36034443: NO_OUTCOME_FOREST_FIGURE:refused f3=MULTIPANEL_NO_UNIQUE_PANEL,f5=MULTIPANEL_NO_UNIQUE_PANEL
- sglt2-ckd-progression::36811901: PMID 36811901: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::36994345: PMID 36994345: NO_OUTCOME_FOREST_FIGURE
- sglt2-ckd-progression::37840144: PMID 37840144: AMBIGUOUS_FIGURE:Fig7,Fig9,Fig2
- sglt2-hfref-hosp-cvdeath::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- sglt2-primary-prevention-hf::35282455: PMID 35282455: NO_OUTCOME_FOREST_FIGURE
- sglt2-primary-prevention-hf::36030328: PMID 36030328: NO_OUTCOME_FOREST_FIGURE
- sglt2-primary-prevention-hf::36034443: PMID 36034443: NO_OUTCOME_FOREST_FIGURE:refused f3=MULTIPANEL_NO_UNIQUE_PANEL,f5=MULTIPANEL_NO_UNIQUE_PANEL
- sglt2-primary-prevention-hf::36811901: PMID 36811901: NO_OUTCOME_FOREST_FIGURE
- sglt2-primary-prevention-hf::36994345: PMID 36994345: NO_OUTCOME_FOREST_FIGURE
- spironolactone-hfref-mortality::30170387: PMID 30170387: NO_OUTCOME_FOREST_FIGURE
- ticagrelor-vs-clopidogrel-acs::29233189: PMID 29233189: NO_OUTCOME_FOREST_FIGURE

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
- dapagliflozin-hfpef-hosp::33859839 / Chen Jiao, 2020: ONLY_IN_READING_A; codex {"effect": "0.82", "events_c": "6", "events_t": "5", "label": "Chen Jiao, 2020", "lower": "0.26", "n_c": "94", "n_t": "96", "upper": "2.58", "weight_pct": "1.8"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Kato, 2019: ONLY_IN_READING_A; codex {"effect": "0.59", "events_c": "47", "events_t": "25", "label": "Kato, 2019", "lower": "0.37", "n_c": "353", "n_t": "318", "upper": "0.94", "weight_pct": "11.2"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / McMurray, 2019: ONLY_IN_READING_A; codex {"effect": "0.83", "events_c": "273", "events_t": "227", "label": "McMurray, 2019", "lower": "0.70", "n_c": "2371", "n_t": "2373", "upper": "0.98", "weight_pct": "85.6"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Nassif, 2019: ONLY_IN_READING_A; codex {"effect": "1.01", "events_c": "1", "events_t": "1", "label": "Nassif, 2019", "lower": "0.06", "n_c": "132", "n_t": "131", "upper": "15.94", "weight_pct": "0.3"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Yang Zhen, 2019: ONLY_IN_READING_A; codex {"effect": "0.74", "events_c": "4", "events_t": "3", "label": "Yang Zhen, 2019", "lower": "0.17", "n_c": "52", "n_t": "53", "upper": "3.13", "weight_pct": "1.1"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Chen Jiao, 2020: ONLY_IN_READING_A; codex {"effect": "0.38", "events_c": "18", "events_t": "7", "label": "Chen Jiao, 2020", "lower": "0.17", "n_c": "94", "n_t": "96", "upper": "0.87", "weight_pct": "2.9"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Kato, 2019: ONLY_IN_READING_A; codex {"effect": "0.72", "events_c": "63", "events_t": "41", "label": "Kato, 2019", "lower": "0.50", "n_c": "353", "n_t": "318", "upper": "1.04", "weight_pct": "15.0"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / McMurray, 2019: ONLY_IN_READING_A; codex {"effect": "0.73", "events_c": "318", "events_t": "231", "label": "McMurray, 2019", "lower": "0.62", "n_c": "2371", "n_t": "2373", "upper": "0.85", "weight_pct": "77.6"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Nassif, 2019: ONLY_IN_READING_A; codex {"effect": "1.26", "events_c": "8", "events_t": "10", "label": "Nassif, 2019", "lower": "0.51", "n_c": "132", "n_t": "131", "upper": "3.09", "weight_pct": "2.5"}; agy null
- dapagliflozin-hfpef-hosp::33859839 / Yang Zhen, 2019: ONLY_IN_READING_A; codex {"effect": "0.74", "events_c": "8", "events_t": "6", "label": "Yang Zhen, 2019", "lower": "0.27", "n_c": "52", "n_t": "53", "upper": "1.97", "weight_pct": "2.0"}; agy null
- esketamine-trd-madrs::37194806 / Canuso et al. 2018: LOWER_DISAGREES; codex {"effect": "3.30", "events_c": null, "events_t": null, "label": "Canuso et al. 2018", "lower": "-1.58", "n_c": "31", "n_t": "35", "upper": "8.19", "weight_pct": "17.6%"}; agy {"effect": "3.30", "events_c": null, "events_t": null, "label": "Canuso et al. 2018", "lower": "-1.59", "n_c": "31", "n_t": "35", "upper": "8.19", "weight_pct": "17.6%"}
- glp1-ra-mace-t2d::40652242 / Gerstein et al. 2019: ONLY_IN_READING_A; codex {"effect": "1.29", "events_c": "20", "events_t": "26", "label": "Gerstein et al. 2019", "lower": "0.72", "n_c": "4793", "n_t": "4817", "upper": "2.31", "weight_pct": "33.0%"}; agy null
- glp1-ra-mace-t2d::40652242 / Pinget et al. 2013: ONLY_IN_READING_A; codex {"effect": "0.16", "events_c": "1", "events_t": "0", "label": "Pinget et al. 2013", "lower": "0.01", "n_c": "137", "n_t": "288", "upper": "3.87", "weight_pct": "2.5%"}; agy null
- glp1-ra-mace-t2d::40652242 / Riddle et al. 2013: ONLY_IN_READING_A; codex {"effect": "0.36", "events_c": "1", "events_t": "0", "label": "Riddle et al. 2013", "lower": "0.01", "n_c": "211", "n_t": "194", "upper": "8.85", "weight_pct": "2.5%"}; agy null
- glp1-ra-mace-t2d::40652242 / Holman et al. 2017: ONLY_IN_READING_A; codex {"effect": "1.31", "events_c": "13", "events_t": "17", "label": "Holman et al. 2017", "lower": "0.64", "n_c": "7093", "n_t": "7094", "upper": "2.69", "weight_pct": "26.9%"}; agy null
- glp1-ra-mace-t2d::40652242 / Marso et al. 2016: ONLY_IN_READING_A; codex {"effect": "0.61", "events_c": "28", "events_t": "17", "label": "Marso et al. 2016", "lower": "0.33", "n_c": "4672", "n_t": "4668", "upper": "1.11", "weight_pct": "32.1%"}; agy null
- glp1-ra-mace-t2d::40652242 / Husain et al. 2019: ONLY_IN_READING_A; codex {"effect": "0.12", "events_c": "4", "events_t": "0", "label": "Husain et al. 2019", "lower": "0.01", "n_c": "1435", "n_t": "1347", "upper": "2.20", "weight_pct": "3.0%"}; agy null
- glp1-ra-mace-t2d::40652242 / Lincoff et al. 2023: ONLY_IN_READING_A; codex {"effect": "0.73", "events_c": "322", "events_t": "234", "label": "Lincoff et al. 2023", "lower": "0.62", "n_c": "8801", "n_t": "8803", "upper": "0.86", "weight_pct": "14.7%"}; agy null
- glp1-ra-mace-t2d::40652242 / Ruff et al. 2022: ONLY_IN_READING_A; codex {"effect": "1.33", "events_c": "28", "events_t": "37", "label": "Ruff et al. 2022", "lower": "0.81", "n_c": "2081", "n_t": "2075", "upper": "2.16", "weight_pct": "3.3%"}; agy null
- glp1-ra-mace-t2d::40652242 / Gerstein et al. 2019: ONLY_IN_READING_A; codex {"effect": "0.96", "events_c": "212", "events_t": "205", "label": "Gerstein et al. 2019", "lower": "0.80", "n_c": "4793", "n_t": "4817", "upper": "1.16", "weight_pct": "13.1%"}; agy null
- glp1-ra-mace-t2d::40652242 / Pfeffer et al. 2015: ONLY_IN_READING_A; codex {"effect": "1.03", "events_c": "247", "events_t": "255", "label": "Pfeffer et al. 2015", "lower": "0.87", "n_c": "2916", "n_t": "2922", "upper": "1.22", "weight_pct": "14.6%"}; agy null
- glp1-ra-mace-t2d::40652242 / Frias et al. 2019: ONLY_IN_READING_A; codex {"effect": "0.36", "events_c": "1", "events_t": "1", "label": "Frias et al. 2019", "lower": "0.02", "n_c": "71", "n_t": "199", "upper": "5.63", "weight_pct": "0.1%"}; agy null
- glp1-ra-mace-t2d::40652242 / Le Roux et al. 2017: ONLY_IN_READING_A; codex {"effect": "1.25", "events_c": "1", "events_t": "3", "label": "Le Roux et al. 2017", "lower": "0.13", "n_c": "327", "n_t": "783", "upper": "12.00", "weight_pct": "0.2%"}; agy null
- glp1-ra-mace-t2d::40652242 / Pan et al. 2014: ONLY_IN_READING_A; codex {"effect": "3.08", "events_c": "0", "events_t": "1", "label": "Pan et al. 2014", "lower": "0.13", "n_c": "184", "n_t": "179", "upper": "75.20", "weight_pct": "0.1%"}; agy null
- glp1-ra-mace-t2d::40652242 / Gerstein et al. 2021: ONLY_IN_READING_A; codex {"effect": "0.80", "events_c": "53", "events_t": "85", "label": "Gerstein et al. 2021", "lower": "0.57", "n_c": "1359", "n_t": "2717", "upper": "1.12", "weight_pct": "6.2%"}; agy null
- glp1-ra-mace-t2d::40652242 / Marso et al. 2016: ONLY_IN_READING_A; codex {"effect": "0.89", "events_c": "317", "events_t": "281", "label": "Marso et al. 2016", "lower": "0.76", "n_c": "4672", "n_t": "4668", "upper": "1.04", "weight_pct": "15.6%"}; agy null
- glp1-ra-mace-t2d::40652242 / Husain et al. 2019: ONLY_IN_READING_A; codex {"effect": "1.27", "events_c": "31", "events_t": "37", "label": "Husain et al. 2019", "lower": "0.79", "n_c": "1435", "n_t": "1347", "upper": "2.04", "weight_pct": "3.5%"}; agy null
- glp1-ra-mace-t2d::40652242 / Marso et al. 2016: ONLY_IN_READING_A; codex {"effect": "0.78", "events_c": "133", "events_t": "105", "label": "Marso et al. 2016", "lower": "0.61", "n_c": "1609", "n_t": "1623", "upper": "1.00", "weight_pct": "9.6%"}; agy null
- glp1-ra-mace-t2d::40652242 / Perkovic et al. 2024: ONLY_IN_READING_A; codex {"effect": "0.81", "events_c": "64", "events_t": "52", "label": "Perkovic et al. 2024", "lower": "0.57", "n_c": "1766", "n_t": "1767", "upper": "1.16", "weight_pct": "5.6%"}; agy null
- glp1-ra-mace-t2d::40652242 / McGuire et al. 2025: ONLY_IN_READING_A; codex {"effect": "0.75", "events_c": "253", "events_t": "191", "label": "McGuire et al. 2025", "lower": "0.63", "n_c": "4825", "n_t": "4825", "upper": "0.91", "weight_pct": "13.4%"}; agy null
- iv-iron-hfref-hosp::29174251 / CONFIRM-HF: ONLY_IN_READING_A; codex {"effect": "0.51", "events_c": "51", "events_t": "26", "label": "CONFIRM-HF", "lower": "0.34", "n_c": "151", "n_t": "150", "upper": "0.78", "weight_pct": "70.7%"}; agy null
- iv-iron-hfref-hosp::29174251 / FAIR-HF: ONLY_IN_READING_A; codex {"effect": "0.45", "events_c": "18", "events_t": "16", "label": "FAIR-HF", "lower": "0.24", "n_c": "154", "n_t": "305", "upper": "0.86", "weight_pct": "29.3%"}; agy null
- iv-iron-hfref-hosp::29174251 / CONFIRM-HF: ONLY_IN_READING_A; codex {"effect": "1.34", "events_c": "3", "events_t": "4", "label": "CONFIRM-HF", "lower": "0.31", "n_c": "151", "n_t": "150", "upper": "5.90", "weight_pct": "59.5%"}; agy null
- iv-iron-hfref-hosp::29174251 / FAIR-HF: ONLY_IN_READING_A; codex {"effect": "0.07", "events_c": "3", "events_t": "0", "label": "FAIR-HF", "lower": "0.00", "n_c": "154", "n_t": "305", "upper": "1.39", "weight_pct": "40.5%"}; agy null
- iv-iron-hfref-hosp::29174251 / CONFIRM-HF: ONLY_IN_READING_A; codex {"effect": "0.92", "events_c": "12", "events_t": "11", "label": "CONFIRM-HF", "lower": "0.42", "n_c": "151", "n_t": "150", "upper": "2.03", "weight_pct": "75.3%"}; agy null
- iv-iron-hfref-hosp::29174251 / FAIR-HF: ONLY_IN_READING_A; codex {"effect": "0.50", "events_c": "4", "events_t": "4", "label": "FAIR-HF", "lower": "0.13", "n_c": "154", "n_t": "305", "upper": "1.99", "weight_pct": "24.7%"}; agy null
- iv-iron-hfref-hosp::37632415 / Total CV hospitalizations and CV death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.86", "events_c": null, "events_t": null, "label": "Total CV hospitalizations and CV death", "lower": "0.75", "n_c": "2233", "n_t": "2237", "upper": "0.98", "weight_pct": null}; agy {"effect": "0.86", "events_c": "30.5%", "events_t": "27.6%", "label": "Total CV hospitalizations and CV death", "lower": "0.75", "n_c": "2233", "n_t": "2237", "upper": "0.98", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Total HF hospitalizations and CV death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.87", "events_c": null, "events_t": null, "label": "Total HF hospitalizations and CV death", "lower": "0.75", "n_c": "2233", "n_t": "2237", "upper": "1.01", "weight_pct": null}; agy {"effect": "0.87", "events_c": "25.2%", "events_t": "22.5%", "label": "Total HF hospitalizations and CV death", "lower": "0.75", "n_c": "2233", "n_t": "2237", "upper": "1.01", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Total CV hospitalizations: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.83", "events_c": null, "events_t": null, "label": "Total CV hospitalizations", "lower": "0.73", "n_c": "2233", "n_t": "2237", "upper": "0.96", "weight_pct": null}; agy {"effect": "0.83", "events_c": "26.4%", "events_t": "22.9%", "label": "Total CV hospitalizations", "lower": "0.73", "n_c": "2233", "n_t": "2237", "upper": "0.96", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Total HF hospitalizations: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.84", "events_c": null, "events_t": null, "label": "Total HF hospitalizations", "lower": "0.71", "n_c": "2233", "n_t": "2237", "upper": "0.98", "weight_pct": null}; agy {"effect": "0.84", "events_c": "20.2%", "events_t": "17.0%", "label": "Total HF hospitalizations", "lower": "0.71", "n_c": "2233", "n_t": "2237", "upper": "0.98", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Time to CV death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.97", "events_c": null, "events_t": null, "label": "Time to CV death", "lower": "0.80", "n_c": "2233", "n_t": "2237", "upper": "1.17", "weight_pct": null}; agy {"effect": "0.97", "events_c": "9.8%", "events_t": "9.2%", "label": "Time to CV death", "lower": "0.80", "n_c": "2233", "n_t": "2237", "upper": "1.17", "weight_pct": null}
- iv-iron-hfref-hosp::37632415 / Time to all-cause death: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.93", "events_c": null, "events_t": null, "label": "Time to all-cause death", "lower": "0.78", "n_c": "2233", "n_t": "2237", "upper": "1.10", "weight_pct": null}; agy {"effect": "0.93", "events_c": "12.7%", "events_t": "11.5%", "label": "Time to all-cause death", "lower": "0.78", "n_c": "2233", "n_t": "2237", "upper": "1.10", "weight_pct": null}
- melatonin-primary-insomnia-sol::36104141 / Seely et al 2021: N_T_DISAGREES,N_C_DISAGREES; codex {"effect": "-0.01", "events_c": null, "events_t": null, "label": "Seely et al 2021", "lower": "-0.16", "n_c": "253", "n_t": "156", "upper": "0.13", "weight_pct": "13.7%"}; agy {"effect": "-0.01", "events_c": null, "events_t": null, "label": "Seely et al 2021", "lower": "-0.16", "n_c": "353", "n_t": "356", "upper": "0.13", "weight_pct": "13.7%"}
- metformin-pcos-ovulation / Hemmings? / Heathcote 2013: LABEL_DISAGREES; codex {"label": "Hemmings?", "effect": "1.33", "lower": "0.24", "upper": "7.56", "weight_pct": "1.6", "events_t": "10", "n_t": "13", "events_c": "10", "n_c": "14"}; agy {"label": "Heathcote 2013", "effect": "1.33", "lower": "0.24", "upper": "7.56", "weight_pct": "1.6 %", "events_t": "10", "n_t": "13", "events_c": "10", "n_c": "14"}
- sacubitril-valsartan-hfref::36574300 / PARAMOUNT, 2012: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.64", "events_c": "8", "events_t": "5", "label": "PARAMOUNT, 2012", "lower": "0.21", "n_c": null, "n_t": null, "upper": "1.90", "weight_pct": "0.31"}; agy {"effect": "0.64", "events_c": null, "events_t": null, "label": "PARAMOUNT, 2012", "lower": "0.21", "n_c": null, "n_t": null, "upper": "1.90", "weight_pct": "0.31"}
- sacubitril-valsartan-hfref::36574300 / PARAGON, 2019: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.89", "events_c": "1146", "events_t": "1032", "label": "PARAGON, 2019", "lower": "0.84", "n_c": null, "n_t": null, "upper": "0.95", "weight_pct": "95.74"}; agy {"effect": "0.89", "events_c": null, "events_t": null, "label": "PARAGON, 2019", "lower": "0.84", "n_c": null, "n_t": null, "upper": "0.95", "weight_pct": "95.74"}
- sacubitril-valsartan-hfref::36574300 / PARALLAX, 2020: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.83", "events_c": "54", "events_t": "98", "label": "PARALLAX, 2020", "lower": "0.61", "n_c": null, "n_t": null, "upper": "1.15", "weight_pct": "3.68"}; agy {"effect": "0.83", "events_c": null, "events_t": null, "label": "PARALLAX, 2020", "lower": "0.61", "n_c": null, "n_t": null, "upper": "1.15", "weight_pct": "3.68"}
- sacubitril-valsartan-hfref::36574300 / Shi et al., 2020: EVENTS_T_DISAGREES,EVENTS_C_DISAGREES; codex {"effect": "0.37", "events_c": "9", "events_t": "3", "label": "Shi et al., 2020", "lower": "0.12", "n_c": null, "n_t": null, "upper": "1.17", "weight_pct": "0.28"}; agy {"effect": "0.37", "events_c": null, "events_t": null, "label": "Shi et al., 2020", "lower": "0.12", "n_c": null, "n_t": null, "upper": "1.17", "weight_pct": "0.28"}
- sglt2-primary-prevention-hf::33859839 / Chen Jiao, 2020: ONLY_IN_READING_A; codex {"effect": "0.82", "events_c": "6", "events_t": "5", "label": "Chen Jiao, 2020", "lower": "0.26", "n_c": "94", "n_t": "96", "upper": "2.58", "weight_pct": "1.8"}; agy null
- sglt2-primary-prevention-hf::33859839 / Kato, 2019: ONLY_IN_READING_A; codex {"effect": "0.59", "events_c": "47", "events_t": "25", "label": "Kato, 2019", "lower": "0.37", "n_c": "353", "n_t": "318", "upper": "0.94", "weight_pct": "11.2"}; agy null
- sglt2-primary-prevention-hf::33859839 / McMurray, 2019: ONLY_IN_READING_A; codex {"effect": "0.83", "events_c": "273", "events_t": "227", "label": "McMurray, 2019", "lower": "0.70", "n_c": "2371", "n_t": "2373", "upper": "0.98", "weight_pct": "85.6"}; agy null
- sglt2-primary-prevention-hf::33859839 / Nassif, 2019: ONLY_IN_READING_A; codex {"effect": "1.01", "events_c": "1", "events_t": "1", "label": "Nassif, 2019", "lower": "0.06", "n_c": "132", "n_t": "131", "upper": "15.94", "weight_pct": "0.3"}; agy null
- sglt2-primary-prevention-hf::33859839 / Yang Zhen, 2019: ONLY_IN_READING_A; codex {"effect": "0.74", "events_c": "4", "events_t": "3", "label": "Yang Zhen, 2019", "lower": "0.17", "n_c": "52", "n_t": "53", "upper": "3.13", "weight_pct": "1.1"}; agy null
- sglt2-primary-prevention-hf::33859839 / Chen Jiao, 2020: ONLY_IN_READING_A; codex {"effect": "0.38", "events_c": "18", "events_t": "7", "label": "Chen Jiao, 2020", "lower": "0.17", "n_c": "94", "n_t": "96", "upper": "0.87", "weight_pct": "2.9"}; agy null
- sglt2-primary-prevention-hf::33859839 / Kato, 2019: ONLY_IN_READING_A; codex {"effect": "0.72", "events_c": "63", "events_t": "41", "label": "Kato, 2019", "lower": "0.50", "n_c": "353", "n_t": "318", "upper": "1.04", "weight_pct": "15.0"}; agy null
- sglt2-primary-prevention-hf::33859839 / McMurray, 2019: ONLY_IN_READING_A; codex {"effect": "0.73", "events_c": "318", "events_t": "231", "label": "McMurray, 2019", "lower": "0.62", "n_c": "2371", "n_t": "2373", "upper": "0.85", "weight_pct": "77.6"}; agy null
- sglt2-primary-prevention-hf::33859839 / Nassif, 2019: ONLY_IN_READING_A; codex {"effect": "1.26", "events_c": "8", "events_t": "10", "label": "Nassif, 2019", "lower": "0.51", "n_c": "132", "n_t": "131", "upper": "3.09", "weight_pct": "2.5"}; agy null
- sglt2-primary-prevention-hf::33859839 / Yang Zhen, 2019: ONLY_IN_READING_A; codex {"effect": "0.74", "events_c": "8", "events_t": "6", "label": "Yang Zhen, 2019", "lower": "0.27", "n_c": "52", "n_t": "53", "upper": "1.97", "weight_pct": "2.0"}; agy null
