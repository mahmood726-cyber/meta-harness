# G1 dual-model forest-plot reader (derived: scripts/g1_forest_reader.py)

Two model families read each comparator forest figure (codex `gpt-6-astra`; agy `Gemini 3.1 Pro (High)`), every call recorded under evidence/model_calls/forest/ and replayed byte-identically. A row is PROPOSED only when both readings agree within the printed rounding; a figure is ACCEPTED only when the agreed rows, pooled by the meta's STATED model, reproduce its printed pool and CI. Accepted rows are SECONDARY comparator rows: never pool inputs, never counted toward agreement with their own meta.

- topics: 16; figures read by both models: 10; ACCEPTED 5, REFUSED 5, not read 6
- rows: proposed 91, refused (readings disagree) 2, accepted as secondary comparator rows 65
- pooled-reconstruction pass rate: 5 of 10 figures read

| topic | comparator | figure | state | rows proposed / refused | stated model | printed pool | reconstructed | why |
|---|---|---|---|---|---|---|---|---|
| colchicine-secondary-cv-prevention | PMID 36176989 | F3 | **REFUSED** | 6 / 1 | STATED ['MH-FE'] | 0.54 (0.38-0.77) | MH-FE 0.6465 (0.5575-0.7496) | ROWS_DISAGREE:1, RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL |
| corticosteroids-covid19-mortality | PMID 32876694 | joi200104f2 | **ACCEPTED** | 7 / 0 | STATED ['FE', 'PM', 'PM+HK'] | 0.66 (0.53-0.82) | FE 0.6593 (0.5323-0.8167); PM 0.6962 (0.5183-0.9350); PM+HK 0.6962 (0.4817-1.0061) | - |
| iv-iron-hfref-hosp | PMID 39727669 | diseases-12-00339-f003 | **ACCEPTED** | 5 / 0 | STATED ['DL'] | 0.59 (0.40-0.88) | DL 0.5907 (0.3965-0.8800) | - |
| metformin-pcos-ovulation | PMID 31845767 | CD013505-fig-0024 | **REFUSED** | 20 / 1 | STATED ['FE', 'MH-FE'] | 1.65 (1.35-2.03) | FE 1.5805 (1.2734-1.9617); MH-FE 1.6598 (1.3507-2.0397) | ROWS_DISAGREE:1 |
| noac-vs-warfarin-af-stroke | PMID 34985309 | F1 | **REFUSED** | 0 / 0 | NOT_RECONSTRUCTABLE [] | 0.81 (0.74-0.89) |  | ROWS_ARE_NOT_STUDIES:outcome/outcome, STATED_MODEL_NOT_RECONSTRUCTABLE, FEWER_THAN_2_AGREED_ROWS |
| pcsk9-mace | PMID 36531722 | F2 | **REFUSED** | 0 / 0 | STATED ['DL', 'FE', 'PM', 'REML'] | NNTB 36 (NNTB 29-NNTB 47) |  | ROWS_ARE_NOT_STUDIES:subgroup/subgroup, FEWER_THAN_2_AGREED_ROWS |
| probiotics-aad-prevention | PMID 34385227 | F3 | **ACCEPTED** | 42 / 0 | STATED ['MH-RE'] | 0.63 (0.54-0.73) | MH-RE 0.6256 (0.5356-0.7307) | - |
| sglt2-primary-prevention-hf | PMID 33519713 | f2 | **ACCEPTED** | 8 / 0 | STATED ['MH-RE'] | 0.63 (0.53-0.74) | MH-RE 0.6262 (0.5328-0.7360) | - |
| spironolactone-hfref-mortality | PMID 40959489 | F4 | **ACCEPTED** | 3 / 0 | STATED ['FE'] | 0.78 (0.72-0.85) | FE 0.7841 (0.7196-0.8544) | - |
| tranexamic-acid-pph | PMID 39461793 | F2 | **REFUSED** | 0 / 0 | NOT_STATED [] | 0.77 (0.63-0.93) |  | ROWS_ARE_NOT_STUDIES:mixed/mixed, STATED_MODEL_NOT_STATED, FEWER_THAN_2_AGREED_ROWS |

## Not read (typed reason)

- colchicine-recurrent-pericarditis: PMID 22442198: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://heart.bmj.com/content/heartjnl/98/14/1078.full.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://heart.bmj.com/content/hear): a bot challenge is not solved)
- corticosteroids-cap-mortality: PMID 38128217: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (hybrid, https://doi.org/10.1016/j.jcrc.2023.154507: NOT_A_PDF (HTTP 200))
- doac-vte-recurrence: PMID 24963045: NO_JATS -- no PMC full text; OPEN_BUT_NOT_SCRIPT_READABLE (bronze, https://ashpublications.org/blood/article-pdf/124/12/1968/1379490/1968.pdf: REFUSED_BY_HOST (GET failed after 1 tries: https://ashpublications.org/blood/): a bot challenge is not solved)
- dpp4-mace-t2d: PMID 34754403: REFUSED_BEFORE_READING:NO_TOPIC_OUTCOME_PANEL: the comparator's only forest figure (panels A-F: MI, stroke, HHF, unstable angina, revascularisation, CV mortality) has no 3-point MACE panel
- sacubitril-valsartan-hfref: PMID 36722326: REFUSED_BEFORE_READING:NETWORK_META_ANALYSIS_FIGURE: rows are treatments (network estimates), not trials
- sglt2-ckd-progression: PMID 41203232: REFUSED_BEFORE_READING:NO_PER_TRIAL_TOPIC_FIGURE: the comparator's figures are CKD-progression / eGFR outcomes by baseline eGFR or UACR SUBGROUP, not per-trial rows of the trial-defined cardiorenal composite

## Disagreements (both readings shown)

- colchicine-secondary-cv-prevention / Newton N–2019 / Mewton N-2019: LABEL_DISAGREES; codex {"label": "Newton N–2019", "effect": "0.90", "lower": "0.27", "upper": "3.01", "weight_pct": "6.5%", "events_t": "5", "n_t": "101", "events_c": "5", "n_c": "91"}; agy {"label": "Mewton N-2019", "effect": "0.90", "lower": "0.27", "upper": "3.01", "weight_pct": "6.5%", "events_t": "5", "n_t": "101", "events_c": "5", "n_c": "91"}
- metformin-pcos-ovulation / Hemmings? / Heathcote 2013: LABEL_DISAGREES; codex {"label": "Hemmings?", "effect": "1.33", "lower": "0.24", "upper": "7.56", "weight_pct": "1.6", "events_t": "10", "n_t": "13", "events_c": "10", "n_c": "14"}; agy {"label": "Heathcote 2013", "effect": "1.33", "lower": "0.24", "upper": "7.56", "weight_pct": "1.6 %", "events_t": "10", "n_t": "13", "events_c": "10", "n_c": "14"}
