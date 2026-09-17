# LANE FIX1 report

Base / measured HEAD: `2f8705a8e81e3eacf0c47bcfe5af69a88cc130ac`. Requested base: `refs/lanes/landing4-wip-pm` = `2f8705a8e81e3eacf0c47bcfe5af69a88cc130ac`.

Offline repairs to the nine confirmed findings. No commit or staging. `harness/synth.py` and `harness/gate.py` are unchanged. Only the GLP-1 page was rebuilt; shared-code effects on other pages are listed below, without rebuilding them.

MEASURED denotes reproduced local results. INFERRED denotes interpretation or prospective effects on pages not rebuilt. CLAIMED denotes the prior page/protocol assertions challenged by the audit. This is a repair report, not publication certification. The gate verdict and full-suite failures are reported separately from individual repair checks.

The auditor's `.tmp/audit.py` was copied unchanged from the audit checkout. All nine pre-fix commands ran before the first code edit. Its fixed line-number slices and literal `CODE` captions are pasted unchanged below; those captions are not new claims about the repaired code. Tests verify the current implementation.

| Ingredient | Static/dynamic | Hardcode disclosure |
|---|---|---|
| Publication, regulatory, registry and retrieval-ledger inputs | Static held evidence | No new retrieval, invented effects, or edits to clinical source records |
| Existing axis-evidence trial-name register | Static source-backed identity mapping | Used to identify live pooled rows; never supplies the intersection or pooled values |
| Comparator trial aliases; named search obligations | Static matching/declaration vocabulary | Counts and MET/UNMET states are derived from held text, live membership and the ledger |
| Effect types, overlaps, harm signals, refusal states and estimates | Dynamic | Recomputed from the selected rows and held evidence |
| Title mutation, unlocated spans, numeric corruption | Artificial test plants | In memory / temporary test files only, never represented as real evidence |

## 1. Outcome-specific harm reporting

Change: Removed generic adverse-event expansion for specific harm outcomes; discontinuation due to adverse events requires both the action and harm cause. A negative search carries the searched text. FLOW has typed absence in both panels; FREEDOM-CVO has a genuine GI sentence and typed absence for AE discontinuation. Complete matched sentences are retained instead of truncating away the matching term.

Added regression in `tests/test_lane_fix1.py`: `test_generic_adverse_events_are_not_specific_harms (two cases); test_discontinuation_requires_harm_cause`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py harms
```

```text
OUTCOME Gastrointestinal adverse events claimed source-reporting count 10
PMID 30291013 KNOWN_REPORTED_NOT_YET_EXTRACTED 'The incidence of acute pancreatitis (ten patients in the albiglutide group and seven patients in the placebo group), pancreatic cancer (six patients in the albiglutide group and five patients in the placebo group), medullary thyroid carcinoma (zero patients in both groups), and other serious adverse'
span rendered= True reproduced signal= None
PMID 38785209 KNOWN_REPORTED_NOT_YET_EXTRACTED 'Serious adverse events were reported in a lower percentage of participants in the semaglutide group than in the placebo group (49.6% vs. 53.8%).'
span rendered= True reproduced signal= {'reported': True, 'kind': 'numeric_signal', 'span': 'Serious adverse events were reported in a lower percentage of participants in the semaglutide group than in the placebo group (49.6% vs. 53.8%).'}
PMID 34873344 KNOWN_REPORTED_NOT_YET_EXTRACTED 'Serious adverse events were similar between the two groups.'
span rendered= True reproduced signal= {'reported': True, 'kind': 'term_signal', 'span': 'Serious adverse events were similar between the two groups.'}
OUTCOME Adverse events leading to discontinuation claimed source-reporting count 9
PMID 30291013 KNOWN_REPORTED_NOT_YET_EXTRACTED 'On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1.5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018.'
span rendered= True reproduced signal= {'reported': True, 'kind': 'term_signal', 'span': 'On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1.5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018.'}
PMID 38785209 KNOWN_REPORTED_NOT_YET_EXTRACTED 'Serious adverse events were reported in a lower percentage of participants in the semaglutide group than in the placebo group (49.6% vs. 53.8%).'
span rendered= True reproduced signal= {'reported': True, 'kind': 'numeric_signal', 'span': 'Serious adverse events were reported in a lower percentage of participants in the semaglutide group than in the placebo group (49.6% vs. 53.8%).'}
PMID 34873344 KNOWN_REPORTED_NOT_YET_EXTRACTED 'Serious adverse events were similar between the two groups.'
span rendered= True reproduced signal= {'reported': True, 'kind': 'term_signal', 'span': 'Serious adverse events were similar between the two groups.'}
CODE harness/harms.py:_terms and reporting_signal use any adverse-event/discontinuation term, not the complete outcome.
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py harms
```

```text
OUTCOME Gastrointestinal adverse events claimed source-reporting count 6
PMID 30291013 RETRIEVED_OUTCOME_NOT_REPORTED 'BACKGROUND: Glucagon-like peptide 1 receptor agonists differ in chemical structure, duration of action, and in their effects on clinical outcomes. The cardiovascular effects of once-weekly albiglutide in type 2 diabetes are unknown. We aimed to determine the safety and efficacy of albiglutide in preventing cardiovascular death, myocardial infarction, or stroke. METHODS: We did a double-blind, randomised, placebo-controlled trial in 610 sites across 28 countries. We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease (at a 1:1 ratio) to groups that either received a subcutaneous injection of albiglutide (30-50 mg, based on glycaemic response and tolerability) or of a matched volume of placebo once a week, in addition to their standard care. Investigators used an interactive voice or web response system to obtain treatment assignment, and patients and all study investigators were masked to their treatment allocation. We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population. If non-inferiority was confirmed by an upper limit of the 95% CI for a hazard ratio of less than 1·30, closed testing for superiority was prespecified. This study is registered with ClinicalTrials.gov, number NCT02465515. FINDINGS: Patients were screened between July 1, 2015, and Nov 24, 2016. 10\u2008793 patients were screened and 9463 participants were enrolled and randomly assigned to groups: 4731 patients were assigned to receive albiglutide and 4732 patients to receive placebo. On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome. The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4·6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5·9 events per 100 person-years in the placebo group (hazard ratio 0·78, 95% CI 0·68-0·90), which indicated that albiglutide was superior to placebo (p<0·0001 for non-inferiority; p=0·0006 for superiority). The incidence of acute pancreatitis (ten patients in the albiglutide group and seven patients in the placebo group), pancreatic cancer (six patients in the albiglutide group and five patients in the placebo group), medullary thyroid carcinoma (zero patients in both groups), and other serious adverse events did not differ between the two groups. There were three (<1%) deaths in the placebo group that were assessed by investigators, who were masked to study drug assignment, to be treatment-related and two (<1%) deaths in the albiglutide group. INTERPRETATION: In patients with type 2 diabetes and cardiovascular disease, albiglutide was superior to placebo with respect to major adverse cardiovascular events. Evidence-based glucagon-like peptide 1 receptor agonists should therefore be considered as part of a comprehensive strategy to reduce the risk of cardiovascular events in patients with type 2 diabetes. FUNDING: GlaxoSmithKline.'
span rendered= True reproduced signal= None
PMID 38785209 RETRIEVED_OUTCOME_NOT_REPORTED 'Patients with type 2 diabetes and chronic kidney disease are at high risk for kidney failure, cardiovascular events, and death. Whether treatment with semaglutide would mitigate these risks is unknown. We randomly assigned patients with type 2 diabetes and chronic kidney disease (defined by an estimated glomerular filtration rate [eGFR] of 50 to 75 ml per minute per 1.73 m2 of body-surface area and a urinary albumin-to-creatinine ratio [with albumin measured in milligrams and creatinine measured in grams] of >300 and <5000 or an eGFR of 25 to <50 ml per minute per 1.73 m2 and a urinary albumin-to-creatinine ratio of >100 and <5000) to receive subcutaneous semaglutide at a dose of 1.0 mg weekly or placebo. The primary outcome was major kidney disease events, a composite of the onset of kidney failure (dialysis, transplantation, or an eGFR of <15 ml per minute per 1.73 m2), at least a 50% reduction in the eGFR from baseline, or death from kidney-related or cardiovascular causes. Prespecified confirmatory secondary outcomes were tested hierarchically. Among the 3533 participants who underwent randomization (1767 in the semaglutide group and 1766 in the placebo group), median follow-up was 3.4 years, after early trial cessation was recommended at a prespecified interim analysis. The risk of a primary-outcome event was 24% lower in the semaglutide group than in the placebo group (331 vs. 410 first events; hazard ratio, 0.76; 95% confidence interval [CI], 0.66 to 0.88; P\u2009=\u20090.0003). Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89). The results for all confirmatory secondary outcomes favored semaglutide: the mean annual eGFR slope was less steep (indicating a slower decrease) by 1.16 ml per minute per 1.73 m2 in the semaglutide group (P<0.001), the risk of major cardiovascular events 18% lower (hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P\u2009=\u20090.029), and the risk of death from any cause 20% lower (hazard ratio, 0.80; 95% CI, 0.67 to 0.95, P\u2009=\u20090.01). Serious adverse events were reported in a lower percentage of participants in the semaglutide group than in the placebo group (49.6% vs. 53.8%). Semaglutide reduced the risk of clinically important kidney outcomes and death from cardiovascular causes in patients with type 2 diabetes and chronic kidney disease. (Funded by Novo Nordisk; FLOW ClinicalTrials.gov number, NCT03819153.).'
span rendered= True reproduced signal= None
PMID 34873344 KNOWN_REPORTED_NOT_YET_EXTRACTED 'Adverse events were more frequent in the ITCA 650 group (72%, 1,491/2,074) than in the placebo group (63.9%, 1,325/2,070), mainly due to an increase in gastrointestinal events and disorders while on ITCA 650.'
span rendered= True reproduced signal= {'reported': True, 'kind': 'numeric_signal', 'span': 'Adverse events were more frequent in the ITCA 650 group (72%, 1,491/2,074) than in the placebo group (63.9%, 1,325/2,070), mainly due to an increase in gastrointestinal events and disorders while on ITCA 650.'}
OUTCOME Adverse events leading to discontinuation claimed source-reporting count 3
PMID 30291013 RETRIEVED_OUTCOME_NOT_REPORTED 'BACKGROUND: Glucagon-like peptide 1 receptor agonists differ in chemical structure, duration of action, and in their effects on clinical outcomes. The cardiovascular effects of once-weekly albiglutide in type 2 diabetes are unknown. We aimed to determine the safety and efficacy of albiglutide in preventing cardiovascular death, myocardial infarction, or stroke. METHODS: We did a double-blind, randomised, placebo-controlled trial in 610 sites across 28 countries. We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease (at a 1:1 ratio) to groups that either received a subcutaneous injection of albiglutide (30-50 mg, based on glycaemic response and tolerability) or of a matched volume of placebo once a week, in addition to their standard care. Investigators used an interactive voice or web response system to obtain treatment assignment, and patients and all study investigators were masked to their treatment allocation. We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population. If non-inferiority was confirmed by an upper limit of the 95% CI for a hazard ratio of less than 1·30, closed testing for superiority was prespecified. This study is registered with ClinicalTrials.gov, number NCT02465515. FINDINGS: Patients were screened between July 1, 2015, and Nov 24, 2016. 10\u2008793 patients were screened and 9463 participants were enrolled and randomly assigned to groups: 4731 patients were assigned to receive albiglutide and 4732 patients to receive placebo. On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome. The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4·6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5·9 events per 100 person-years in the placebo group (hazard ratio 0·78, 95% CI 0·68-0·90), which indicated that albiglutide was superior to placebo (p<0·0001 for non-inferiority; p=0·0006 for superiority). The incidence of acute pancreatitis (ten patients in the albiglutide group and seven patients in the placebo group), pancreatic cancer (six patients in the albiglutide group and five patients in the placebo group), medullary thyroid carcinoma (zero patients in both groups), and other serious adverse events did not differ between the two groups. There were three (<1%) deaths in the placebo group that were assessed by investigators, who were masked to study drug assignment, to be treatment-related and two (<1%) deaths in the albiglutide group. INTERPRETATION: In patients with type 2 diabetes and cardiovascular disease, albiglutide was superior to placebo with respect to major adverse cardiovascular events. Evidence-based glucagon-like peptide 1 receptor agonists should therefore be considered as part of a comprehensive strategy to reduce the risk of cardiovascular events in patients with type 2 diabetes. FUNDING: GlaxoSmithKline.'
span rendered= True reproduced signal= None
PMID 38785209 RETRIEVED_OUTCOME_NOT_REPORTED 'Patients with type 2 diabetes and chronic kidney disease are at high risk for kidney failure, cardiovascular events, and death. Whether treatment with semaglutide would mitigate these risks is unknown. We randomly assigned patients with type 2 diabetes and chronic kidney disease (defined by an estimated glomerular filtration rate [eGFR] of 50 to 75 ml per minute per 1.73 m2 of body-surface area and a urinary albumin-to-creatinine ratio [with albumin measured in milligrams and creatinine measured in grams] of >300 and <5000 or an eGFR of 25 to <50 ml per minute per 1.73 m2 and a urinary albumin-to-creatinine ratio of >100 and <5000) to receive subcutaneous semaglutide at a dose of 1.0 mg weekly or placebo. The primary outcome was major kidney disease events, a composite of the onset of kidney failure (dialysis, transplantation, or an eGFR of <15 ml per minute per 1.73 m2), at least a 50% reduction in the eGFR from baseline, or death from kidney-related or cardiovascular causes. Prespecified confirmatory secondary outcomes were tested hierarchically. Among the 3533 participants who underwent randomization (1767 in the semaglutide group and 1766 in the placebo group), median follow-up was 3.4 years, after early trial cessation was recommended at a prespecified interim analysis. The risk of a primary-outcome event was 24% lower in the semaglutide group than in the placebo group (331 vs. 410 first events; hazard ratio, 0.76; 95% confidence interval [CI], 0.66 to 0.88; P\u2009=\u20090.0003). Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89). The results for all confirmatory secondary outcomes favored semaglutide: the mean annual eGFR slope was less steep (indicating a slower decrease) by 1.16 ml per minute per 1.73 m2 in the semaglutide group (P<0.001), the risk of major cardiovascular events 18% lower (hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P\u2009=\u20090.029), and the risk of death from any cause 20% lower (hazard ratio, 0.80; 95% CI, 0.67 to 0.95, P\u2009=\u20090.01). Serious adverse events were reported in a lower percentage of participants in the semaglutide group than in the placebo group (49.6% vs. 53.8%). Semaglutide reduced the risk of clinically important kidney outcomes and death from cardiovascular causes in patients with type 2 diabetes and chronic kidney disease. (Funded by Novo Nordisk; FLOW ClinicalTrials.gov number, NCT03819153.).'
span rendered= True reproduced signal= None
PMID 34873344 RETRIEVED_OUTCOME_NOT_REPORTED 'Glucagon-like peptide 1 receptor agonists (GLP-1RAs) injected periodically have been shown to not increase and, for some members of this class, decrease the risk of cardiovascular events. The cardiovascular safety of delivering a continuous subcutaneous infusion of the GLP-1RA exenatide (ITCA 650) is unknown. Here, we randomly assigned patients with type 2 diabetes with, or at risk for, atherosclerotic cardiovascular disease (ASCVD) to receive ITCA 650 or placebo to assess cardiovascular safety in a pre-approval trial ( NCT01455896 ). The primary outcome was a composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke or hospitalization for unstable angina. On the basis of 2008 guidance from the US Food and Drug Administration, a non-inferiority margin of 1.8 for the upper bound of the 95% confidence interval (CI) of the hazard ratio (HR) was used. We randomized 4,156 patients (2,075 assigned to receive ITCA 650 and 2,081 assigned to receive placebo) who were followed for a median of 16 months. The primary outcome occurred in 4.6% (95/2,075) of patients in the ITCA 650 group and 3.8% (79/2,081) of patients in the placebo group, meeting the pre-specified non-inferiority criterion (HR = 1.21, 95% CI, 0.90-1.63, Pnon-inferiority\u2009=\u20090.004). Serious adverse events were similar between the two groups. Adverse events were more frequent in the ITCA 650 group (72%, 1,491/2,074) than in the placebo group (63.9%, 1,325/2,070), mainly due to an increase in gastrointestinal events and disorders while on ITCA 650. In patients with type 2 diabetes with, or at risk for, ASCVD, ITCA 650 was non-inferior to placebo. A larger and longer-duration cardiovascular outcomes trial is needed to define more precisely the cardiovascular effects of ITCA 650 in this population.'
span rendered= True reproduced signal= None
CODE harness/harms.py:_terms and reporting_signal use any adverse-event/discontinuation term, not the complete outcome.
```

## 2. Deduplicated missing trials and preserved typing debt

Change: Reconcile named signals through screening family/registry identity before deduplication. Prefer the detailed declared/refused row. The value builder reads held effect_type_refusals and emits HELD_VALUE_TYPE_REFUSED / EFFECT_TYPE_REFUSED with the exact unification reason. Numeric evidence is nested in held_refused_effect, not exposed as a poolable sensitivity input. No refused row is added to a pool.

Added regression in `tests/test_lane_fix1.py`: `test_missing_deduplicates_family_and_preserves_refusal`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py missing
```

```text
Known-missing per-item debt states: {'EXTRACTION_DEBT': 3, 'NOT_IN_COMMITTED_SOURCE': 1}.
Known-missing per-item value states: {'NOT_IN_COMMITTED_SOURCE': 4}.
Known-missing per-item debt states: {'EXTRACTION_DEBT': 3, 'NOT_IN_COMMITTED_SOURCE': 1}.
Known-missing per-item value states: {'NOT_IN_COMMITTED_SOURCE': 4}.
{"name": "Effects of Semaglutide on Chronic Kidney Disease in Patients with Type 2 Diabetes.", "trial_key": "FLOW", "value_status": "NOT_IN_COMMITTED_SOURCE", "missing_class": "NOT_IN_COMMITTED_SOURCE", "source_ref": "cache/glp1-ra-mace-t2d/records.json#38785209.abstract", "verify_basis": "committed source does not carry an extractable target-estimand value"}
{"name": "Cardiovascular and Renal Outcomes with Efpeglenatide in Type 2 Diabetes.", "trial_key": "34215025", "value_status": "NOT_IN_COMMITTED_SOURCE", "missing_class": "EXTRACTION_DEBT", "source_ref": "cache/glp1-ra-mace-t2d/records.json#34215025.abstract", "verify_basis": "committed source does not carry an extractable target-estimand value"}
{"name": "Albiglutide and cardiovascular outcomes in patients with type 2 diabetes and cardiovascular disease (Harmony Outcomes): a double-blind, randomised placebo-controlled trial.", "trial_key": "30291013", "value_status": "NOT_IN_COMMITTED_SOURCE", "missing_class": "EXTRACTION_DEBT", "source_ref": "cache/glp1-ra-mace-t2d/records.json#30291013.abstract", "verify_basis": "committed source does not carry an extractable target-estimand value"}
{"name": "Effects of Semaglutide on Chronic Kidney Disease in Patients with Type 2 Diabetes.", "trial_key": "38785209", "value_status": "NOT_IN_COMMITTED_SOURCE", "missing_class": "EXTRACTION_DEBT", "source_ref": "cache/glp1-ra-mace-t2d/records.json#38785209.abstract", "verify_basis": "committed source does not carry an extractable target-estimand value"}
HELD REFUSED EFFECT PMID 34215025 0.73 0.58 0.92 {'status': 'UNKNOWN_FAILS_CLOSED', 'axis': 8, 'axis_name': 'censoring', 'reason': 'UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD'}
HELD REFUSED EFFECT PMID 30291013 0.78 0.68 0.9 {'status': 'REFUSE', 'axis': 4, 'axis_name': 'endpoint_components', 'reason': "axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion"}
HELD REFUSED EFFECT PMID 38785209 0.82 0.68 0.98 {'status': 'UNKNOWN_FAILS_CLOSED', 'axis': 8, 'axis_name': 'censoring', 'reason': 'UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR'}
screen FLOW [{'id': 'FLOW · 38785209', 'decision': 'include', 'trial_family_id': 'FLOW'}]
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py missing
```

```text
Known-missing per-item debt states: {'EFFECT_TYPE_REFUSED': 3}.
Known-missing per-item value states: {'HELD_VALUE_TYPE_REFUSED': 3}.
Known-missing per-item debt states: {'EFFECT_TYPE_REFUSED': 3}.
Known-missing per-item value states: {'HELD_VALUE_TYPE_REFUSED': 3}.
{"name": "Cardiovascular and Renal Outcomes with Efpeglenatide in Type 2 Diabetes.", "trial_key": "34215025", "value_status": "HELD_VALUE_TYPE_REFUSED", "missing_class": "EFFECT_TYPE_REFUSED", "source_ref": "cache/glp1-ra-mace-t2d/records.json", "verify_basis": "UNTYPED \u2014 axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD"}
{"name": "Albiglutide and cardiovascular outcomes in patients with type 2 diabetes and cardiovascular disease (Harmony Outcomes): a double-blind, randomised placebo-controlled trial.", "trial_key": "30291013", "value_status": "HELD_VALUE_TYPE_REFUSED", "missing_class": "EFFECT_TYPE_REFUSED", "source_ref": "cache/glp1-ra-mace-t2d/records.json", "verify_basis": "axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion"}
{"name": "Effects of Semaglutide on Chronic Kidney Disease in Patients with Type 2 Diabetes.", "trial_key": "38785209", "value_status": "HELD_VALUE_TYPE_REFUSED", "missing_class": "EFFECT_TYPE_REFUSED", "source_ref": "outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml", "verify_basis": "UNTYPED \u2014 axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR"}
HELD REFUSED EFFECT PMID 34215025 0.73 0.58 0.92 {'status': 'UNKNOWN_FAILS_CLOSED', 'axis': 8, 'axis_name': 'censoring', 'reason': 'UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD'}
HELD REFUSED EFFECT PMID 30291013 0.78 0.68 0.9 {'status': 'REFUSE', 'axis': 4, 'axis_name': 'endpoint_components', 'reason': "axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion"}
HELD REFUSED EFFECT PMID 38785209 0.82 0.68 0.98 {'status': 'UNKNOWN_FAILS_CLOSED', 'axis': 8, 'axis_name': 'censoring', 'reason': 'UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR'}
screen FLOW [{'id': 'FLOW · 38785209', 'decision': 'include', 'trial_family_id': 'FLOW'}]
```

## 3. Live comparator overlap

Change: Removed the GLP-1 shared/only lists from the profile. At build time intersect the current pooled trial identities with the held comparator enumeration. MEASURED result: 6 of 7 live pooled trial families shared, also 6 of 8 enumerated comparator families; SOUL only in ours, HARMONY Outcomes and AMPLITUDE-O only in theirs. Trial-set overlap remains separate from endpoint compatibility.

Added regression in `tests/test_lane_fix1.py`: `test_overlap_is_recomputed_when_pool_changes`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py parity
```

```text
STORED overlap {"ours_k": 7, "theirs_k": 8, "shared_k": 7, "only_ours": ["SOUL"], "only_theirs": ["ELIXA"], "method": "cached comparator text trial-set enumeration", "note": "Comparator trial set was measured from cached comparator abstract/full text.", "theirs_k_source": "6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina. Characteristics of trials and patients are reported, respectively, in Table 1 . The populations studied ranged in size from 3297 (SUSTAIN-6) to 14,752 (EXSCEL), were of similar age (mean age was 64.0 \u00b1 1.97 years), 37,117 were mal", "shared_k_measurement": "MEASURED", "shared_trials": ["LEADER", "SUSTAIN-6", "EXSCEL", "HARMONY Outcomes", "REWIND", "PIONEER 6", "AMPLITUDE-O"]}
POOLED IDs ['PMID 31185157', 'PMID 27633186', 'PMID 27295427', 'PMID 31189511', 'PMID 28910237', 'PMID 26630143', 'PMID 40162642']
Parity enumeration check: 7 pooled trial families; 7 recorded shared labels and 1 only-ours labels enumerate 8 distinct labels. UNRENDERABLE parity relation: the recorded overlap does not reconcile with the current pool; adjudication OWED.
HELD comparator trial list: tudy drug/mean follow up (years) Participants (n) Age mean (years) Male sex (n, %) Participants with established CV disease (n, %) History of heart failure (n, %) eGFR < 60 ml/min per 1.73 m 2 (n, %) ELIXA Lixisenatide 6068 60.3 3174 (69.3%) 6068 (100%) 1922 (20.3%) 1407 (23.2%) 2015 2.1 year LEADER Liraglutide 9340 64.3 6003 (64.3%) 6764 (72.4%) 1667 (17.8%) 2158 (23.1%) 2016 3.8 year SUSTAIN-6 Semaglutide 3297 64.6 2002 (60.7%) 2735 (83%) 777 (23.6%) 939 (28.5%) 2016 3.1 year EXSCEL Eenatide OW 14,752 62.0 9149 (62%) 10,792 (73.1%) 2389 (16.2%) 3191 (21.6%) 2017 3.2 year HARMONY Albiglutide 
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py parity
```

```text
STORED overlap {"ours_k": 7, "theirs_k": 8, "shared_k": 6, "only_ours": ["SOUL"], "only_theirs": ["AMPLITUDE-O", "HARMONY Outcomes"], "method": "cached comparator text trial-set enumeration", "note": "Comparator trial set was measured from cached comparator abstract/full text.", "theirs_k_source": "6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina. Characteristics of trials and patients are reported, respectively, in Table 1 . The populations studied ranged in size from 3297 (SUSTAIN-6) to 14,752 (EXSCEL), were of similar age (mean age was 64.0 \u00b1 1.97 years), 37,117 were mal", "shared_k_measurement": "MEASURED", "shared_trials": ["ELIXA", "EXSCEL", "LEADER", "PIONEER 6", "REWIND", "SUSTAIN-6"]}
POOLED IDs ['PMID 31185157', 'PMID 27633186', 'PMID 27295427', 'PMID 31189511', 'PMID 28910237', 'PMID 26630143', 'PMID 40162642']
Parity enumeration check: 7 pooled trial families; 6 recorded shared labels and 1 only-ours labels enumerate 7 distinct labels. Counts reconcile; identifier-level trial-set validation remains owed.
HELD comparator trial list: tudy drug/mean follow up (years) Participants (n) Age mean (years) Male sex (n, %) Participants with established CV disease (n, %) History of heart failure (n, %) eGFR < 60 ml/min per 1.73 m 2 (n, %) ELIXA Lixisenatide 6068 60.3 3174 (69.3%) 6068 (100%) 1922 (20.3%) 1407 (23.2%) 2015 2.1 year LEADER Liraglutide 9340 64.3 6003 (64.3%) 6764 (72.4%) 1667 (17.8%) 2158 (23.1%) 2016 3.8 year SUSTAIN-6 Semaglutide 3297 64.6 2002 (60.7%) 2735 (83%) 777 (23.6%) 939 (28.5%) 2016 3.1 year EXSCEL Eenatide OW 14,752 62.0 9149 (62%) 10,792 (73.1%) 2389 (16.2%) 3191 (21.6%) 2017 3.2 year HARMONY Albiglutide 
```

## 4. Executable title-independent screening

Change: Added title_independent machinery that examines title, abstract, conditions, interventions and evidenced arm-object spans before lexical exclusion. Enabled it for GLP-1 and disabled its intervention title anchor. The LEADER title mutation is included by both screen_record and screen.run; removing its abstract leaves it excluded. Eligibility prose now describes the operative fields.

Added regression in `tests/test_lane_fix1.py`: `test_title_only_leader_plant`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py screen
```

```text
PROTOCOL: - **Screening.** The **clinical eligibility rule** (above) is separate from the **machine screening heuristic**. Title and registry-condition term matching is a first-pass heuristic only; final eligibility is decided from abstract, then registry record, then full text/protocol as needed, on a canonical trial object (trial / arm / drug / dose / route / background therapy / population / timepoint / analysis set). A trial must not become ineligible because a term is absent from its title. Every screening decision carries the source span it rests on.
Held LEADER title: Liraglutide and Cardiovascular Outcomes in Type 2 Diabetes.
baseline ('include', 'INCLUDE', 'eligible randomised controlled trial: intervention liraglutide, comparator placebo, population type 2 diabetes — P/I/C/design met.', 'population “…diovascular Outcomes in Type 2 Diabetes.”; comparator “…receive liraglutide or placebo. The primary composite…”')
IN-MEMORY TITLE-ONLY PLANT; same abstract, ID, other fields: ('exclude', 'X2', "population not on-topic: title/conditions do not mention any of ['type 2 diabetes', 'type 2 diabetic', 'type 2 diabetes mellitus', 'diabetes mellitus, type 2', 't2d', 't2dm'] (an incidental abstract mention does not qualify).", 'examined title/conditions: “Cardiovascular outcomes”')
full screen.run title-only plant [('exclude', 'X2')]
CONFIG {'population_any': ['type 2 diabetes', 'type 2 diabetic', 'type 2 diabetes mellitus', 'diabetes mellitus, type 2', 't2d', 't2dm'], 'population_none': ['without diabetes', 'no diabetes', 'obesity without diabetes', 'overweight or obesity but without diabetes', 'type 1 diabetes', 'gestational diabetes'], 'intervention_any': ['liraglutide', 'semaglutide', 'dulaglutide', 'albiglutide', 'efpeglenatide', 'exenatide', 'lixisenatide'], 'intervention_in_title': True, 'comparator_any': ['placebo'], 'design_double_blind': False}
screen.run signature (all_recs: 'list', config: 'dict') -> 'dict'
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py screen
```

```text
PROTOCOL: - **Screening.** The **clinical eligibility rule** (above) is separate from the **machine screening heuristic**. Title and registry-condition term matching is a first-pass heuristic only; final eligibility is decided from abstract, then registry record, then full text/protocol as needed, on a canonical trial object (trial / arm / drug / dose / route / background therapy / population / timepoint / analysis set). A trial must not become ineligible because a term is absent from its title. Every screening decision carries the source span it rests on.
Held LEADER title: Liraglutide and Cardiovascular Outcomes in Type 2 Diabetes.
baseline ('include', 'INCLUDE', 'eligible randomised controlled trial: intervention liraglutide, comparator placebo, population type 2 diabetes — P/I/C/design met.', 'population “…diovascular Outcomes in Type 2 Diabetes. BACKGROUND: The cardio…”; comparator “…receive liraglutide or placebo. The primary composite…”')
IN-MEMORY TITLE-ONLY PLANT; same abstract, ID, other fields: ('include', 'INCLUDE', 'eligible randomised controlled trial: intervention liraglutide, comparator placebo, population type 2 diabetes — P/I/C/design met.', 'population “…d care in patients with type 2 diabetes, remains unknown. METHO…”; comparator “…receive liraglutide or placebo. The primary composite…”')
full screen.run title-only plant [('include', 'INCLUDE')]
CONFIG {'population_any': ['type 2 diabetes', 'type 2 diabetic', 'type 2 diabetes mellitus', 'diabetes mellitus, type 2', 't2d', 't2dm'], 'population_none': ['without diabetes', 'no diabetes', 'obesity without diabetes', 'overweight or obesity but without diabetes', 'type 1 diabetes', 'gestational diabetes'], 'intervention_any': ['liraglutide', 'semaglutide', 'dulaglutide', 'albiglutide', 'efpeglenatide', 'exenatide', 'lixisenatide'], 'intervention_in_title': False, 'comparator_any': ['placebo'], 'design_double_blind': False, 'title_independent': True}
screen.run signature (all_recs: 'list', config: 'dict') -> 'dict'
```

## 5. Adjustment labels require typed evidence

Change: Reported estimates default to ADJUSTMENT_UNKNOWN. PUBLISHED_ADJUSTED / PUBLISHED_UNADJUSTED require known typed estimator and adjustment axes with source spans; a substring such as multiplicity adjustment does not assign either label. The existing design-key test now expects unknown for the source that does not identify adjustment.

Added regression in `tests/test_lane_fix1.py`: `test_adjustment_unknown_without_typed_evidence; updated tests/test_design_key.py expectation`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py estimator
```

```text
PROTOCOL: - **Source hierarchy for every extracted value (recorded and rendered as `source_level`):** 1 the trial's own publication and supplement; 2 regulatory review (FDA, EMA) -- primary re-analysis of trial data; 3 registry results (ClinicalTrials.gov / AACT) -- sponsor-posted structured data; 4 HTA assessment (NICE); 5 older meta-analyses -- **pointers only, never the number itself** (several published reviews relabelled ELIXA's 4-point MACE as 3-point; a value found in a meta is traced to a level 1-4 source or refused). A label such as `PUBLISHED_UNADJUSTED` is assigned only after the estimator is read at the source.
PMID 31185157 design estimator= PUBLISHED_UNADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 27633186 design estimator= PUBLISHED_UNADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 27295427 design estimator= PUBLISHED_ADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 31189511 design estimator= PUBLISHED_UNADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 28910237 design estimator= PUBLISHED_UNADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 26630143 design estimator= PUBLISHED_UNADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 40162642 design estimator= PUBLISHED_UNADJUSTED typed adjustment= UNKNOWN typed estimator= UNKNOWN
CODE harness/design_key.py:578-582
    alt = _published_alternative(trial.get("source") or "")
    interaction = _interaction_evidence(text + " " + str(trial.get("source") or ""))
    estimator_source = "RECONSTRUCTED"
    if derivation == "reported":
        estimator_source = "PUBLISHED_ADJUSTED" if "adjust" in (trial.get("source") or "").lower() else "PUBLISHED_UNADJUSTED"
LEADER held fulltext: with a margin of 1.30 for the upper boundary of the 95% confidence interval of the hazard ratio. No adjustments for multiplicity were performed for the prespecified exploratory outcomes. RESULTS A total of 9340 patients underwent randomization. The median follow-up was 3.8 years. The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) th
LEADER held fulltext: The primary and exploratory analyses for the outcomes in the time-to-event analyses were based on a Cox proportional-hazards model with treatment as a covariate. The primary hypothesis was that liraglutide would be noninferior to placebo with regard to the primary outcome, with a margin of 1.30 for the upper boundary of the 95% confidence interval of the hazard ratio. We used a hierarchical testin
LEADER held fulltext: , prespecified sensitivity analyses were conducted (see the protocol). For exploratory outcomes, no adjustments of P values for multiplicity were performed. All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; ev
LEADER held fulltext: ystolic and diastolic blood pressure, and pulse using a mixed model for repeated measurements, with adjustment for baseline covariates. RESULTS OVERVIEW OF TRIAL CONDUCT A total of 9340 patients underwent randomization from September 2010 through April 2012; 4668 patients were randomly assigned to receive liraglutide and 4672 to receive placebo. The planned closeout of follow-up of the patients wa
LEADER held fulltext: rence was not significant. Sensitivity analyses suggested that our findings were robust to baseline adjustment and alternative censoring. Cardiovascular benefits were observed in the context of generally acceptable levels of cardiovascular risk-factor management at baseline and during the trial. There were fewer add-on therapies for diabetes medications, lipid-lowering medications, and diuretics i
LEADER held fulltext: % or more, the observed benefits and risks may not apply to patients at lower risk. Furthermore, no adjustments were made for multiplicity of exploratory outcomes. In conclusion, among patients with type 2 diabetes who were at high risk for cardiovascular events while they were taking standard therapy, those in the liraglutide group had lower rates of cardiovascular events and death from any cause
LEADER held fulltext: s were estimated with the use of the Kaplan–Meier method, and the hazard ratios with the use of the Cox proportional-hazard regression model. The data analyses are truncated at 54 months, because less than 10% of the patients had an observation time beyond 54 months. The insets show the same data on an enlarged y axis. Figure 2 Primary Composite Outcomes in Various Demographic and Clinical Subgrou
LEADER held fulltext: xis. Figure 2 Primary Composite Outcomes in Various Demographic and Clinical Subgroups Prespecified Cox proportional-hazard regression analyses were performed for subgroups of patients with respect to the primary outcome (first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke). P values signify tests of homogeneity for between-group differences wit
LEADER held fulltext: n, or nonfatal stroke). P values signify tests of homogeneity for between-group differences with no adjustment for multiple testing. The percentages of patients with a first primary outcome between the randomization date and the date of last follow-up are shown. Race and ethnic group were self-reported. There were missing data for the body-mass index (the weight in kilograms divided by the square 
LEADER held fulltext:  337 (7.2) 1.9 0.78 (0.67–0.92) 0.003 * Hazard ratios and P values were estimated with the use of a Cox proportional-hazards model with treatment as a covariate. † The primary composite outcome in the time-to-event analysis consisted of the first occurrence of death from cardiovascular causes (181 patients in the liraglutide group vs. 227 in the placebo group), nonfatal (including silent) myocardi
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py estimator
```

```text
PROTOCOL: - **Source hierarchy for every extracted value (recorded and rendered as `source_level`):** 1 the trial's own publication and supplement; 2 regulatory review (FDA, EMA) -- primary re-analysis of trial data; 3 registry results (ClinicalTrials.gov / AACT) -- sponsor-posted structured data; 4 HTA assessment (NICE); 5 older meta-analyses -- **pointers only, never the number itself** (several published reviews relabelled ELIXA's 4-point MACE as 3-point; a value found in a meta is traced to a level 1-4 source or refused). A label such as `PUBLISHED_UNADJUSTED` is assigned only after the estimator is read at the source.
PMID 31185157 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 27633186 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 27295427 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 31189511 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 28910237 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 26630143 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
PMID 40162642 design estimator= ADJUSTMENT_UNKNOWN typed adjustment= UNKNOWN typed estimator= UNKNOWN
CODE harness/design_key.py:578-582
    alt = _published_alternative(trial.get("source") or "")
    interaction = _interaction_evidence(text + " " + str(trial.get("source") or ""))
    estimator_source = "RECONSTRUCTED"
    if derivation == "reported":
        from .effect_type import build_effect, known
LEADER held fulltext: with a margin of 1.30 for the upper boundary of the 95% confidence interval of the hazard ratio. No adjustments for multiplicity were performed for the prespecified exploratory outcomes. RESULTS A total of 9340 patients underwent randomization. The median follow-up was 3.8 years. The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) th
LEADER held fulltext: The primary and exploratory analyses for the outcomes in the time-to-event analyses were based on a Cox proportional-hazards model with treatment as a covariate. The primary hypothesis was that liraglutide would be noninferior to placebo with regard to the primary outcome, with a margin of 1.30 for the upper boundary of the 95% confidence interval of the hazard ratio. We used a hierarchical testin
LEADER held fulltext: , prespecified sensitivity analyses were conducted (see the protocol). For exploratory outcomes, no adjustments of P values for multiplicity were performed. All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; ev
LEADER held fulltext: ystolic and diastolic blood pressure, and pulse using a mixed model for repeated measurements, with adjustment for baseline covariates. RESULTS OVERVIEW OF TRIAL CONDUCT A total of 9340 patients underwent randomization from September 2010 through April 2012; 4668 patients were randomly assigned to receive liraglutide and 4672 to receive placebo. The planned closeout of follow-up of the patients wa
LEADER held fulltext: rence was not significant. Sensitivity analyses suggested that our findings were robust to baseline adjustment and alternative censoring. Cardiovascular benefits were observed in the context of generally acceptable levels of cardiovascular risk-factor management at baseline and during the trial. There were fewer add-on therapies for diabetes medications, lipid-lowering medications, and diuretics i
LEADER held fulltext: % or more, the observed benefits and risks may not apply to patients at lower risk. Furthermore, no adjustments were made for multiplicity of exploratory outcomes. In conclusion, among patients with type 2 diabetes who were at high risk for cardiovascular events while they were taking standard therapy, those in the liraglutide group had lower rates of cardiovascular events and death from any cause
LEADER held fulltext: s were estimated with the use of the Kaplan–Meier method, and the hazard ratios with the use of the Cox proportional-hazard regression model. The data analyses are truncated at 54 months, because less than 10% of the patients had an observation time beyond 54 months. The insets show the same data on an enlarged y axis. Figure 2 Primary Composite Outcomes in Various Demographic and Clinical Subgrou
LEADER held fulltext: xis. Figure 2 Primary Composite Outcomes in Various Demographic and Clinical Subgroups Prespecified Cox proportional-hazard regression analyses were performed for subgroups of patients with respect to the primary outcome (first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke). P values signify tests of homogeneity for between-group differences wit
LEADER held fulltext: n, or nonfatal stroke). P values signify tests of homogeneity for between-group differences with no adjustment for multiple testing. The percentages of patients with a first primary outcome between the randomization date and the date of last follow-up are shown. Race and ethnic group were self-reported. There were missing data for the body-mass index (the weight in kilograms divided by the square 
LEADER held fulltext:  337 (7.2) 1.9 0.78 (0.67–0.92) 0.003 * Hazard ratios and P values were estimated with the use of a Cox proportional-hazards model with treatment as a covariate. † The primary composite outcome in the time-to-event analysis consisted of the first occurrence of death from cardiovascular causes (181 patients in the liraglutide group vs. 227 in the placebo group), nonfatal (including silent) myocardi
```

## 6. Publication-time evidence relocation

Change: check_review relocates binding-axis source spans, verifies document digests/JSON paths via held_axis, recomputes the content-derived effect_type_id from axes and numeric fields, and re-unifies. It checks both the primary outcome and additional strand members. The existing gate.check_effect_types delegates to it unchanged. Corrupted span and numeric-content plants refuse; intact held GLP-1 evidence passes this subcheck.

Added regression in `tests/test_lane_fix1.py`: `test_gate_relocates_span_and_recomputes_id`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py plant
```

```text
IN-MEMORY plant only; no data edited
effect_type.check_review: []
same corrupted basis through held_axis: {'value': 'UNKNOWN', 'basis': {'absence_code': 'UNLOCATED_AXIS_SPAN'}}
CODE check_review: def check_review(review):
    errors = []
    for o in review.get("outcomes", []):
        result = o.get("result") or {}
        if result.get("present") is False or result.get("suppressed_incompatible") or not result.get("k"):
            continue
        if result["k"] != len(o.get("trials", [])):
            errors.append(f"EFFECT_TYPE_COUNT_MISMATCH {o.get('name')}: k differs from trial rows")
        effects = {e["effect_type_id"]: e for e in o.get("effect_types", [])}
        for row in o.get("trials", []):
            e = effects.get(row.get("effect_type_id"))
            v = unify(o.get("effect_type_target") or {}, e or {}, o.get("coercions", []))
            if not e or v["status"] not in ACCEPTED or row.get("unification") != v or e.get("unification") != v:
                errors.append(f"EFFECT_TYPE_REFUSED {o.get('name')} / {row.get('id')}: {v.get('reason', 'missing or stale type verdict')}")
    return errors

```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py plant
```

```text
IN-MEMORY plant only; no data edited
effect_type.check_review: ['EFFECT_TYPE_ID_MISMATCH 3-point major adverse cardiovascular events / PMID 31185157', 'EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 31185157: UNTYPED — axis 8 unknown: UNLOCATED_AXIS_SPAN']
same corrupted basis through held_axis: {'value': 'UNKNOWN', 'basis': {'absence_code': 'UNLOCATED_AXIS_SPAN'}}
CODE check_review: def check_review(review):
    errors = []
    outcomes = list(review.get("outcomes", []))
    primary = next((o for o in outcomes if o.get('primary')), None)
    if primary:
        all_effects = list(primary.get('effect_types', [])) + list((review.get('strands') or {}).get('additional_effect_types', []))
        for strand in (review.get('strands') or {}).get('strands', []):
            outcomes.append({'name': strand['strand'], 'result': {'k': strand.get('k')},
                             'trials': strand.get('members', []), 'effect_types': all_effects,
                             'effect_type_target': primary.get('effect_type_target'),
                             'coercions': primary.get('coercions', [])})
    for o in outcomes:
        result = o.get("result") or {}
        if result.get("present") is False or result.get("suppressed_incompatible") or not result.get("k"):
            continue
        if result["k"] != len(o.get("trials", [])):
            errors.append(f"EFFECT_TYPE_COUNT_MISMATCH {o.get('name')}: k differs from trial rows")
        effects = {e["effect_type_id"]: e for e in o.get("effect_types", [])}
        for row in o.get("trials", []):
            e = effects.get(row.get("effect_type_id"))
            target = o.get("effect_type_target") or {}
            checked = copy.deepcopy(e or {})
            for axis in target.get("binding_axes", []):
                f = checked.get("axes", {}).get(axis) or field()
                # Derived axes carry a rule rather than a source span. Document
                # claims must always relocate; a rule cannot validate a span.
                if (f.get("basis") or {}).get("span"):
                    checked["axes"][axis] = held_axis(f)
            if e:
                obj = {"trial": e["trial"], "axes": checked["axes"]}
                digest = "effect-type:" + _digest({"type": obj, "effect": {
                    k: row.get(k) for k in ("effect", "ci_low", "ci_high", "ai", "ci", "n1i", "n2i")}})
                if digest != e.get("effect_type_id"):
                    errors.append(f"EFFECT_TYPE_ID_MISMATCH {o.get('name')} / {row.get('id')}")
            v = unify(target, checked, o.get("coercions", []))
            if not e or v["status"] not in ACCEPTED or row.get("unification") != v or e.get("unification") != v:
                errors.append(f"EFFECT_TYPE_REFUSED {o.get('name')} / {row.get('id')}: {v.get('reason', 'missing or stale type verdict')}")
    return errors

```

## 7. Endpoint-specific reason audit

Change: The MACE value search requires the MACE endpoint instead of generic cardiovascular/composite words. A typed refusal is preserved before lexical absence classification; its reason audit reports the same binding-axis reason. FLOW remains refused for absent effect-linked censoring evidence. Its kidney-specific HR is not cited as MACE evidence. The state-basis string uses the existing deterministic rendering contract.

Added regression in `tests/test_lane_fix1.py`: `test_reason_audit_requires_same_endpoint_and_preserves_flow_refusal; render-order check in test_missing_deduplicates_family_and_preserves_refusal`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py reason
```

```text
PMID 34215025 actual refusal= UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD declared state= EXTRACTION_NOT_PERFORMED reason audit= {"verdict": "REASON_FALSE_VALUE_HELD", "detail": "REASON_FALSE_VALUE_HELD(abstract:34215025, \"During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p...\")", "stated_reason_code": "EXTRACTION_NOT_PERFORMED", "source_id": "abstract:34215025", "source_kind": "abstract", "source_span": "During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p...", "source_contains": "During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p..."}
PMID 30291013 actual refusal= axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion declared state= EXTRACTION_NOT_PERFORMED reason audit= {"verdict": "REASON_FALSE_VALUE_HELD", "detail": "REASON_FALSE_VALUE_HELD(abstract:30291013, \"The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i...\")", "stated_reason_code": "EXTRACTION_NOT_PERFORMED", "source_id": "abstract:30291013", "source_kind": "abstract", "source_span": "The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i...", "source_contains": "The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i..."}
PMID 38785209 actual refusal= UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR declared state= EXTRACTION_NOT_PERFORMED reason audit= {"verdict": "REASON_FALSE_VALUE_HELD", "detail": "REASON_FALSE_VALUE_HELD(abstract:38785209, \"Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).\")", "stated_reason_code": "EXTRACTION_NOT_PERFORMED", "source_id": "abstract:38785209", "source_kind": "abstract", "source_span": "Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).", "source_contains": "Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89)."}
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py reason
```

```text
PMID 34215025 actual refusal= UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD declared state= EFFECT_TYPE_REFUSED reason audit= {"verdict": "REASON_TRUE", "detail": "UNTYPED \u2014 axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD", "stated_reason_code": "EFFECT_TYPE_REFUSED", "binding_axis": "censoring", "effect_type_id": "effect-type:b66b2ab98e1e074ae8bf5ea18a2444b0a326b5be2983e87ce3928ecd61cd6fa1", "unification": {"status": "UNKNOWN_FAILS_CLOSED", "axis": 8, "axis_name": "censoring", "reason": "UNTYPED \u2014 axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD"}}
PMID 30291013 actual refusal= axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion declared state= EFFECT_TYPE_REFUSED reason audit= {"verdict": "REASON_TRUE", "detail": "axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion", "stated_reason_code": "EFFECT_TYPE_REFUSED", "binding_axis": "endpoint_components", "effect_type_id": "effect-type:47485673f8695da69f3d1fe50802f7f853e9286c9370ade2725c2f750841ba42", "unification": {"status": "REFUSE", "axis": 4, "axis_name": "endpoint_components", "reason": "axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion"}}
PMID 38785209 actual refusal= UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR declared state= EFFECT_TYPE_REFUSED reason audit= {"verdict": "REASON_TRUE", "detail": "UNTYPED \u2014 axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR", "stated_reason_code": "EFFECT_TYPE_REFUSED", "binding_axis": "censoring", "effect_type_id": "effect-type:33fc202be0e95933a12e0db77de36e045ca40a3efd640e31c32f7c31a1a92086", "unification": {"status": "UNKNOWN_FAILS_CLOSED", "axis": 8, "axis_name": "censoring", "reason": "UNTYPED \u2014 axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR"}}
REASON_FALSE_VALUE_HELD
REASON_FALSE_VALUE_HELD
```

## 8. Explicit unmet search obligations

Change: Added declared independent-search obligations for PubMed/MEDLINE, Europe PMC, Cochrane CENTRAL, ClinicalTrials.gov/AACT, WHO ICTRP, ISRCTN and citation chasing. Each object records ledger execution states, source IDs and discovery capability. All 7 of 7 named obligations are UNMET in this ledger. The page renders the object alongside KNOWN_ITEM_RETRIEVAL / PRE_IDENTIFIED_SET. No search was fabricated or executed.

Added regression in `tests/test_lane_fix1.py`: `test_search_obligations_are_ledger_derived`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py search
```

```text
PROTOCOL: - **Search.** Independent concept search across all seven eligible agents in PubMed/MEDLINE and Europe PMC, **the Cochrane CENTRAL register** (free; carries Embase-derived records), ClinicalTrials.gov via the local AACT snapshot (queried symmetrically across agents, not only efpeglenatide), **WHO ICTRP** (non-US registries) and ISRCTN, plus citation chasing and the trial-family assembly of every report, registry record, supplement and regulatory document. **No trial-name seed list is the primary retrieval mechanism.** Every retrieved record carries `entered_via` (executed query / seeded identifier / manual addition) and the rejection trail (families retrieved and refused, each with a typed reason) is rendered.
SERVED sources [{"name": "PubMed", "queries": ["27295427[uid] OR 27633186[uid] OR 31185157[uid]", "31189511[uid] OR 30291013[uid] OR 34215025[uid]", "28910237[uid] OR 26630143[uid]"]}, {"name": "ClinicalTrials.gov", "queries": ["{\"cond\": \"type 2 diabetes cardiovascular\", \"intr\": \"efpeglenatide\"}"]}]
SERVED statuses {'PubMed': 'RAN_OK', 'Europe PMC (OA + metadata)': 'RAN_OK', 'ClinicalTrials.gov': 'RAN_OK', 'Citation chase': 'NOT_RUN', 'Registry-first (AACT)': 'RAN_OK', 'PMC full text': 'NOT_RUN', 'Legacy unrecorded retrieval': 'RAN_OK'}
SERVED discovery capable sources 0
scope_identity: eligibility_scope: OPEN_PIC_DESIGN; search_scope: PRE_IDENTIFIED_SET [adjudication: OWED]
Retrieval classification: KNOWN_ITEM_RETRIEVAL [adjudication: OWED]
fetch.ensure cache branch: def ensure(config: dict, now: str):
    """Fetch into the committed cache if absent; return the loaded records dict."""
    path = cache_path(config["slug"])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py search
```

```text
PROTOCOL: - **Search.** Independent concept search across all seven eligible agents in PubMed/MEDLINE and Europe PMC, **the Cochrane CENTRAL register** (free; carries Embase-derived records), ClinicalTrials.gov via the local AACT snapshot (queried symmetrically across agents, not only efpeglenatide), **WHO ICTRP** (non-US registries) and ISRCTN, plus citation chasing and the trial-family assembly of every report, registry record, supplement and regulatory document. **No trial-name seed list is the primary retrieval mechanism.** Every retrieved record carries `entered_via` (executed query / seeded identifier / manual addition) and the rejection trail (families retrieved and refused, each with a typed reason) is rendered.
SERVED sources [{"name": "PubMed", "queries": ["27295427[uid] OR 27633186[uid] OR 31185157[uid]", "31189511[uid] OR 30291013[uid] OR 34215025[uid]", "28910237[uid] OR 26630143[uid]"]}, {"name": "ClinicalTrials.gov", "queries": ["{\"cond\": \"type 2 diabetes cardiovascular\", \"intr\": \"efpeglenatide\"}"]}]
SERVED statuses {'PubMed': 'RAN_OK', 'Europe PMC (OA + metadata)': 'RAN_OK', 'ClinicalTrials.gov': 'RAN_OK', 'Citation chase': 'NOT_RUN', 'Registry-first (AACT)': 'RAN_OK', 'PMC full text': 'NOT_RUN', 'Legacy unrecorded retrieval': 'RAN_OK'}
SERVED discovery capable sources 0
scope_identity: eligibility_scope: OPEN_PIC_DESIGN; search_scope: PRE_IDENTIFIED_SET [adjudication: OWED]
Retrieval classification: KNOWN_ITEM_RETRIEVAL [adjudication: OWED]
fetch.ensure cache branch: def ensure(config: dict, now: str):
    """Fetch into the committed cache if absent; return the loaded records dict."""
    path = cache_path(config["slug"])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    
```

## 9. Selected-endpoint composite warning

Change: Stopped concatenating the abstract with the selected source. For typed endpoints the component signature comes from that selected effect type; other rows use selected-source text. All 7 of 7 primary pooled endpoint signatures are the same three components, so the mixed-primary-composite warning disappears. ELIXA remains the held FDA three-point MACE effect.

Added regression in `tests/test_lane_fix1.py`: `test_composite_describes_selected_endpoint`.

### pre-fix reproduction

```powershell
python -X utf8 .tmp/audit.py composite
```

```text
pooled trials use each trial's OWN primary composite; component sets differ across trials (varying extra components across trials: unstable angina) — the pooled estimate mixes composite definitions (disclosed, not adjusted) [adjudication: OWED]
PMID 31185157 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 27633186 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 27295427 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 31189511 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 28910237 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 26630143 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 40162642 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
ELIXA selected 1.02 0.887 1.172
SOURCE ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal 

MI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the 

similarity is that only 0.3% of subjects in the ITT population experienced hospitalization for 

unstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and 

lixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, 

1.172) with a point estimate of 1.02.
CODE harness/pipeline.py:1553-1563
        _ch_srcs = []
        for t in trials:
            _pid = str(t.get("id", "")).replace("PMID ", "").strip() or str(t.get("label", ""))
            _ab = (rec_by_id.get(_pid) or rec_by_id.get(t.get("label")) or {}).get("abstract", "")
            _ch_srcs.append({
                "source": (_ab or "") + " " + (t.get("source", "") or ""),
                "endpoint_definition": t.get("endpoint_definition"),
            })
        _ch = extract.composite_heterogeneity(spec.get("name", ""), _ch_srcs)
        if _ch:
            out["result"]["composite_heterogeneity"] = _ch
```

### post-fix reproduction

```powershell
python -X utf8 .tmp/audit.py composite
```

```text
PMID 31185157 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 27633186 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 27295427 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 31189511 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 28910237 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 26630143 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
PMID 40162642 ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
ELIXA selected 1.02 0.887 1.172
SOURCE ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal 

MI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the 

similarity is that only 0.3% of subjects in the ITT population experienced hospitalization for 

unstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and 

lixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, 

1.172) with a point estimate of 1.02.
CODE harness/pipeline.py:1553-1563
        _ch_srcs = []
        for t in trials:
            _ch_srcs.append({
                "source": t.get("source", "") or "",
                "endpoint_definition": next((" | ".join(e["axes"]["endpoint_components"]["value"])
                    for e in effect_types if e["effect_type_id"] == t.get("effect_type_id")
                    and isinstance(e["axes"]["endpoint_components"].get("value"), list)),
                    t.get("endpoint_definition")),
            })
        _ch = extract.composite_heterogeneity(spec.get("name", ""), _ch_srcs)
        if _ch:
```

## Measured strands and source validation

- CONVENTIONAL_GLP1RA: k=7 HR 0.8884 (0.8284–0.9527); 7 of 7 admitted member rows.
- GLP1RA_ANY_DELIVERY: k=8 HR 0.8984 (0.8158–0.9894); 8 of 8 admitted member rows.

Membership is unchanged. The title plant changes a counterfactual decision, not a held record. The three existing binding-axis refusals remain refused. Source validation is against held documents, not a new clinical adjudication.

```powershell
python -X utf8 .tmp/audit.py axes
```

```text
PMID 31185157
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 0, 'abstract']
SPAN: The primary outcome in a time-to-event analysis was the first occurrence of a major adverse cardiovascular event (death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke)
effect_measure HR digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 0, 'abstract']
SPAN: hazard ratio, 0.79
censoring end-of-study digest+located_span= True outputs/handover/typg/outcomes.json ['rows', 104, 'description']
SPAN: Number of participants experiencing a first event of a MACE, defined as cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke are presented. Results are based on the in-trial observation period which started at the date of randomisation, included the period after permanent trial product discontinuation, if any and ended at the date of the follow-up visit regardless of adherence to treatment.
PMID 27633186
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 1, 'abstract']
SPAN: The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke
effect_measure HR digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 1, 'abstract']
SPAN: hazard ratio, 0.74
censoring end-of-study digest+located_span= True outputs/handover/typg/outcomes.json ['rows', 0, 'time_frame']
SPAN: Time from randomisation up to end of follow-up (scheduled at week 109)
PMID 27295427
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 2, 'abstract']
SPAN: The primary composite outcome in the time-to-event analysis was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke
effect_measure HR digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 2, 'abstract']
SPAN: hazard ratio, 0.87
censoring end-of-study digest+located_span= True cache/glp1-ra-mace-t2d/ft_27295427.txt []
SPAN: All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; events occurring after that visit were not included.
PMID 31189511
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 4, 'abstract']
SPAN: The primary outcome was the first occurrence of the composite endpoint of non-fatal myocardial infarction, non-fatal stroke, or death from cardiovascular causes (including unknown causes), which was assessed in the intention-to-treat population
effect_measure HR digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 4, 'abstract']
SPAN: hazard ratio [HR] 0·88, 95% CI 0·79-0·99
censoring end-of-study digest+located_span= True outputs/handover/typg/outcomes.json ['rows', 48, 'time_frame']
SPAN: From randomization to first occurrence or death from any cause or study completion (Median Follow-Up of 5.4 Years)
PMID 28910237
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 6, 'abstract']
SPAN: The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke
effect_measure HR digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 6, 'abstract']
SPAN: hazard ratio, 0.91
censoring end-of-study digest+located_span= True cache/glp1-ra-mace-t2d/ft_28910237.txt []
SPAN: The planned closeout of follow-up of the patients was from December 5, 2016, to May 11, 2017, after the prespecified required minimum of 1360 patients were confirmed to have had a primary composite outcome event.
PMID 26630143
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt []
SPAN: MACE, defined as cardiovascular death, non-fatal 

MI, and non-fatal stroke
effect_measure HR digest+located_span= True outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt []
SPAN: hazard ratio is (0.887, 

1.172) with a point estimate of 1.02.
censoring end-of-study digest+located_span= True outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt []
SPAN: MACE endpoint (on-study) 1.02 

(0.89, 1.18) 

 No. of patients with event (%) 392 (12.9%) 400 (13.2%) 

 Total Person Year 6340.2 6368.7 

 Incidence Rate 6.18 6.28
PMID 40162642
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 10, 'abstract']
SPAN: The primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis
effect_measure HR digest+located_span= True cache/glp1-ra-mace-t2d/records.json ['records', 10, 'abstract']
SPAN: hazard ratio, 0.86
censoring end-of-study digest+located_span= True outputs/handover/typg/outcomes.json ['rows', 54, 'description']
SPAN: Number of participants with first occurrence of EAC (event adjudication committee) confirmed major adverse cardiovascular event (MACE), a composite end-point. i.e., from time of randomization to first occurrence of cardiovascular (CV) death, non-fatal myocardial infarction and non-fatal stroke combined data during in-trial period were reported. In-trial observation period was defined as the period from date of randomization to the first of (both inclusive): date of follow-up visit, date when participant withdrew consent, date of last contact with participant (for participant lost to follow-up), and date of death.
PMID 34873344
endpoint_components ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'] digest+located_span= True outputs/handover/glp1_regulatory/fda_media_172242_ITCA650.pdf.txt []
SPAN: Table 19. Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke)
effect_measure HR digest+located_span= True outputs/handover/glp1_regulatory/fda_media_172242_ITCA650.pdf.txt []
SPAN: IR (n/100 PY) HR (95% CI)** 

3-Point MACE* 85/2075 (4.1%) 

2.94 

69/2081 (3.3%) 

2.37 1.24 (0.90, 1.70)
censoring end-of-study digest+located_span= True outputs/handover/glp1_regulatory/fda_media_172242_ITCA650.pdf.txt []
SPAN: Table 19. Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke) and 4-Point MACE (CV 

Death, Nonfatal MI, Nonfatal Stroke, Unstable Angina) – ITT Population End of Study, FREEDOM (CLP-107)
```

```powershell
python -X utf8 .tmp/audit.py numbers
```

```text
PMID 31185157 [0.79, 0.57, 1.11] cache/glp1-ra-mace-t2d/records.json
numeric token 0.79 present= True
numeric token 0.57 present= True
numeric token 1.11 present= True
PMID 27633186 [0.74, 0.58, 0.95] cache/glp1-ra-mace-t2d/records.json
numeric token 0.74 present= True
numeric token 0.58 present= True
numeric token 0.95 present= True
PMID 27295427 [0.87, 0.78, 0.97] cache/glp1-ra-mace-t2d/records.json
numeric token 0.87 present= True
numeric token 0.78 present= True
numeric token 0.97 present= True
PMID 31189511 [0.88, 0.79, 0.99] cache/glp1-ra-mace-t2d/records.json
numeric token 0.88 present= True
numeric token 0.79 present= True
numeric token 0.99 present= True
PMID 28910237 [0.91, 0.83, 1.0] cache/glp1-ra-mace-t2d/records.json
numeric token 0.91 present= True
numeric token 0.83 present= True
numeric token 1.0 present= True
PMID 26630143 [1.02, 0.887, 1.172] outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf
numeric token 1.02 present= True
numeric token 0.887 present= True
numeric token 1.172 present= True
PMID 40162642 [0.86, 0.77, 0.96] cache/glp1-ra-mace-t2d/records.json
numeric token 0.86 present= True
numeric token 0.77 present= True
numeric token 0.96 present= True
PMID 34873344 [1.24, 0.9, 1.7] outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf
numeric token 1.24 present= True
numeric token 0.9 present= True
numeric token 1.7 present= True
PMID 34215025 [0.73, 0.58, 0.92] cache/glp1-ra-mace-t2d/records.json
numeric token 0.73 present= True
numeric token 0.58 present= True
numeric token 0.92 present= True
PMID 30291013 [0.78, 0.68, 0.9] cache/glp1-ra-mace-t2d/records.json
numeric token 0.78 present= True
numeric token 0.68 present= True
numeric token 0.9 present= True
PMID 38785209 [0.82, 0.68, 0.98] outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml
numeric token 0.82 present= True
numeric token 0.68 present= True
numeric token 0.98 present= True
REPOOL PoolResult(scale='HR', k=7, tau2=0.0012001907170997583, mu_log=np.float64(-0.11833804907311492), se_log=0.028578796354009322, ci_low=0.8283927970084116, ci_high=0.9527447462128897, pi_low=0.795941424211435, pi_high=0.9915891561144685, Q=np.float64(7.115904969906649), estimate=0.8883956805108663, per_study=[('31185157', -0.23572233352106983, np.float64(0.0289079090459586)), ('27633186', -0.3011050927839216, np.float64(0.015845347193396333)), ('27295427', -0.13926206733350766, np.float64(0.0030928965019372356)), ('31189511', -0.12783337150988489, np.float64(0.003314356141013421)), ('28910237', -0.09431067947124129, np.float64(0.002259474416463122)), ('26630143', 0.01980262729617973, np.float64(0.00505213095625821)), ('SOUL', -0.15082288973458366, np.float64(0.003165406392427))], ci_low_fixed=0.8481604436632771, ci_high_fixed=0.933302886344278, estimate_fixed=0.8897137686660694, ci_provenance='synth.pool:PM-tau2+HKSJ-t(k-1)+floor-max(1,Q/(k-1)):v1')
SERVED {'k': 7, 'estimate': 0.8884, 'ci_low': 0.8284, 'ci_high': 0.9527, 'tau2': 0.0012, 'pi_low': 0.7959, 'pi_high': 0.9916}
```

## Required verification

### build

```powershell
python -X utf8 scripts/build_topic.py glp1-ra-mace-t2d
```

```text
protocol_sha=bf99a91652e74347e4e10cf6b9f1962aee4e596d
PRIMARY: 3-point major adverse cardiovascular events  k=7  HR=0.8884 (0.8284-0.9527)  tau2=0.0012
included trials: ['31185157', '27633186', '27295427', '31189511', '28910237', '26630143', 'SOUL']
declared-absent trials: ['34215025', '30291013', 'FLOW']
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

### regression

```powershell
python -X utf8 -m pytest tests/test_lane_fix1.py -q --disable-warnings
```

```text
...........                                                              [100%]
11 passed in 14.54s
```

### gate

```powershell
python -X utf8 -c "from scripts.verify_all import limb_gate_every_page; v,d=limb_gate_every_page('glp1-ra-mace-t2d'); print(v); print(d)"
```

```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=2f8705a8e81e3eacf0c47bcfe5af69a88cc130ac base=none tree=dirty:28 files files=1 docs/reviews/glp1-ra-mace-t2d/review.json
glp1-ra-mace-t2d: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: SENTENCE_WITHOUT_OBJECT : Reproducible meta-analysis harness — auditability, not authority; L1: SENTENCE_WITHOUT_OBJECT : Pinned audit identity — content hash of the canonical review object (review_sha256) 0587d3e282ee11a7; exact served bytes are attested separately (html_sha256 in manifest.json and the production record on the production-records branch). Cite this hash when auditing; a different hash is a different version of this page.; L1: SENTENCE_WITHOUT_OBJECT : 31185157; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27633186; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27295427; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 31189511; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 28910237; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 26630143; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : SOUL; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : endpoint_components; L1: SENTENCE_WITHOUT_OBJECT : axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : FLOW; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : 31185157; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27633186; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27295427; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 31189511; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 28910237; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 26630143; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : SOUL; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : FREEDOM-CVO; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : endpoint_components; L1: SENTENCE_WITHOUT_OBJECT : axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : FLOW; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT glp1-freedom-sensitivity: [FACT] PMID 34873344: HR 1.36 (0.96, 1.92).; L1: SENTENCE_WITHOUT_OBJECT : Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.; L1: SENTENCE_WITHOUT_OBJECT : Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.; L1: SENTENCE_WITHOUT_OBJECT : Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.; L1: SENTENCE_WITHOUT_OBJECT : The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.; L1: SENTENCE_WITHOUT_OBJECT : bf99a91652e74347e4e10cf6b9f1962aee4e596d; L1: SENTENCE_WITHOUT_OBJECT : 2026-09-11; L1: SENTENCE_WITHOUT_OBJECT : Random-effects inverse-variance on the log ratio (log RR/OR/HR/IRR as configured for the outcome); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1 (this canonical code path; every rendered interval is gate-checked to originate here).; L1: SENTENCE_WITHOUT_OBJECT : Included iff ALL hold: a randomised controlled trial; population (in title/registry conditions/abstract/arm evidence) mentions one of ['type 2 diabetes', 'type 2 diabetic', 'type 2 diabetes mellitus', 'diabetes mellitus, type 2', 't2d', 't2dm']; and none of ['without diabetes', 'no diabetes', 'obesity without diabetes', 'overweight or obesity but without diabetes', 'type 1 diabetes', 'gestational diabetes']; randomised intervention is one of ['liraglutide', 'semaglutide', 'dulaglutide', 'albiglutide', 'efpeglenatide', 'exenatide', 'lixisenatide'] (present in the record); a comparator among ['placebo']. Excluded (rule id + verbatim span on each record): X1 not an RCT · X2 wrong/off-topic population · X3 wrong intervention/comparator.; L1: SENTENCE_WITHOUT_OBJECT : # Protocol - GLP-1 receptor agonists for 3-point MACE in type 2 diabetes **Registration.** The commit that adds this file is the registration of this review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab. Committed BEFORE the synthesis is run. ## PICO - **P** - adults with type 2 diabetes. - **I** - GLP-1 receptor agonist therapy (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, or lixisenatide) added to usual care. - **C** - placebo added to usual care. - **O (primary)** - 3-point major adverse cardiovascular events, defined as cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. - **O (harms / secondary)** - gastrointestinal adverse events, discontinuation for adverse events, and any further harm outcome the resolved comparator reports. ## Estimand / population / timepoint - **Estimand** - hazard ratio (HR), GLP-1 receptor agonist vs placebo. - **Population** - intention-to-treat as randomised. - **Timepoint** - trial end / longest primary cardiovascular outcome follow-up. ## Eligibility - on P/I/C/DESIGN ONLY Include a record iff **all** hold: - **I1** - randomised controlled trial; - **I2** - population is adults with type 2 diabetes, judged from the title or registry conditions; - **I3** - a GLP-1 receptor agonist vs placebo contrast; - **design** - double-blind, placebo-controlled. Exclude (reason must be true of the record): - **X1** - not an RCT (review, guideline, observational, protocol-only); - **X2** - wrong population (e.g. obesity without diabetes, type 1 diabetes, or gestational diabetes); - **X3** - wrong intervention/comparison (no GLP-1 receptor agonist-vs-placebo contrast); - **X-DESIGN** - not double-blind and placebo-controlled; - **X5** - off-topic: a primary trial of another topic in this set (negative control). > **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives > a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as > an exclusion. A published effect + 95% CI is a poolable input. ## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline) - PubMed: exact-title sweeps for the large GLP-1 receptor agonist cardiovascular outcome trials in type 2 diabetes (LEADER, SUSTAIN-6, REWIND, HARMONY Outcomes, AMPLITUDE-O, PIONEER-6, EXSCEL, and ELIXA). - ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention "efpeglenatide". - Fixed-screen note: several PubMed abstracts for verified double-blind CVOTs do not use the literal phrase "double-blind"; the config therefore does not require that literal abstract/title string, while the protocol eligibility criterion remains double-blind placebo-controlled design. ## Synthesis method (DECLARED; served method must equal this - gate limb 1) Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI path on the same ratio/log scale; 2x2 extraction is available but is not required when a trial reports an HR + CI. ## Comparator (resolved; open-access confirmed) Giugliano et al., *Cardiovascular Diabetology* 2021, "GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs" (PMID 34526024, DOI 10.1186/s12933-021-01366-8; Unpaywall is_oa=true; PubMed Central PMC8442438). It reports pooled MACE HR 0.86 (95% CI 0.79-0.94) over 8 cardiovascular outcome trials. ## Controls - **Positive** - the search must recover and include LEADER, SUSTAIN-6, and REWIND. - **Negative** - SELECT (semaglutide, double-blind, placebo-controlled, but obesity without diabetes - another disease population) must be recovered and EXCLUDED by the population rule. ## Amendment 2026-09-16 (eligibility, estimand, effect measure, timepoint, screening, search, comparator, harms, RoB 2, GRADE -- "B-prime") Executable strand declarations (delivery boundaries only; all members must also pass P/I/C/design eligibility, held-source verification and binding effect axes): `CONVENTIONAL_GLP1RA` is primary and excludes PMID 34873344 (FREEDOM-CVO, continuous delivery); `GLP1RA_ANY_DELIVERY` is non-primary and has no delivery exclusions. These correspond to `membership_rule.exclude_ids: ["34873344"]` and `membership_rule.exclude_ids: []` in the topic JSON. Neither declaration overrides a refused binding axis. End-of-treatment sensitivity values are never pool candidates. Refused rows remain visible with their axis and reason. **Status: RETROSPECTIVE.** Registered under Mahmood's authority ("fix all in reproducible harness", 16 Sep 2026, via Dispatch) after an independent protocol audit of registration commit `4091958ce4af7f1ca9ed4c30e1021672b0c21223` found that the registered eligibility (a broad GLP-1 review; eligibility explicitly not on the outcome axis) and the registered search (exact-title sweeps for eight named cardiovascular outcome trials) define two different reviews. This amendment is appended before the page is rebuilt against it and does not rename the pinned slug/URL. **Both alternative answers were known when this rule was written**, and are disclosed below; that disclosure is the point of the RETROSPECTIVE label. - **Question.** Among adults with type 2 diabetes, what is the effect of GLP-1 receptor agonist therapy versus placebo on time to first adjudicated 3-point MACE? - **Eligibility (B-prime).** Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes **in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained** -- preferably with blinded or independent adjudication. Eligibility does **not** depend on the direction, statistical significance or published availability of the MACE result. **If MACE was measured but the result is unavailable, the trial is retained and the result is pursued** through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held. - **Alternatives disclosed.** Under **A** (the literal registered rule: outcome not an eligibility axis) the universe would additionally include SUSTAIN-1, PIONEER-1, AWARD-8, LEAD-2, Harmony 1, AMPLITUDE-M, GetGoal-P, GetGoal-L, GetGoal-Mono, FREEDOM-1 and others, entering screening and exiting on outcome availability. Under **B** ("large cardiovascular outcome trials") the universe would be the eight seeded CVOTs, with "large" and "CVOT" undefined. B-prime yields the intended small universe by a stated, executable criterion (prospective systematic ascertainment of the outcome), not by a label or by which results are convenient. FLOW (semaglutide, T2D with CKD; MACE prospectively adjudicated) is eligible under B-prime; FREEDOM-CVO (ITCA 650) is eligible under B-prime on the intervention-class strand that admits continuous delivery (see the class-boundary decision: `CONVENTIONAL_GLP1RA` primary strand, `GLP1RA_ANY_DELIVERY` rendered alongside); ELIXA (lixisenatide; 4-point primary, 3-point components prospectively ascertained) is eligible, its 3-point result pursued from the primary supplement or regulatory record, never from a secondary meta-analysis. - **Estimand.** Intention-to-treat effect of assignment to GLP-1 RA versus placebo on **time to first** occurrence of cardiovascular death, nonfatal myocardial infarction or nonfatal stroke during the prespecified randomised cardiovascular follow-up. Trial definitions that count **undetermined death as cardiovascular death** are accepted as each trial's prespecified adjudicated definition and recorded per trial in the compatibility key (`undetermined_death_counted_as_cv: yes/no/unstated`); no re-adjudication is attempted. - **Effect measure.** The primary analysis pools **log-HRs only** (published, or validly reconstructed from a time-to-event analysis). Ordinary RRs, ORs and IRRs do not enter the primary pool. Where only fixed-time counts are recoverable, a separate RR sensitivity analysis is reported. (Supersedes the registered synthesis sentence "random-effects inverse-variance on log(RR)", which contradicted the registered HR estimand.) - **Timepoint.** The trial's prespecified primary cardiovascular analysis **at the end of randomised, blinded follow-up**. Post-trial and extension follow-up are analysed separately and never substitute for the primary analysis. - **Screening.** The **clinical eligibility rule** (above) is separate from the **machine screening heuristic**. Title and registry-condition term matching is a first-pass heuristic only; final eligibility is decided from abstract, then registry record, then full text/protocol as needed, on a canonical trial object (trial / arm / drug / dose / route / background therapy / population / timepoint / analysis set). A trial must not become ineligible because a term is absent from its title. Every screening decision carries the source span it rests on. - **Search.** Independent concept search across all seven eligible agents in PubMed/MEDLINE and Europe PMC, **the Cochrane CENTRAL register** (free; carries Embase-derived records), ClinicalTrials.gov via the local AACT snapshot (queried symmetrically across agents, not only efpeglenatide), **WHO ICTRP** (non-US registries) and ISRCTN, plus citation chasing and the trial-family assembly of every report, registry record, supplement and regulatory document. **No trial-name seed list is the primary retrieval mechanism.** Every retrieved record carries `entered_via` (executed query / seeded identifier / manual addition) and the rejection trail (families retrieved and refused, each with a typed reason) is rendered. - **Declared scope boundary (not a defect): no Embase.** This review does not search Embase. Its unique contribution over MEDLINE is mainly conference abstracts and European/pharma-journal reports; for large registered cardiovascular outcome trials -- this topic -- the marginal yield is low because every such trial is MEDLINE-indexed and registered, and CENTRAL + registries recover part of Embase's unique yield. The completeness claim is therefore for **registered trials**; Embase-equivalent coverage of conference and grey literature is not claimed. (For topics dominated by small or older trials the gap matters considerably more; each topic's protocol states which kind it is.) - **Source hierarchy for every extracted value (recorded and rendered as `source_level`):** 1 the trial's own publication and supplement; 2 regulatory review (FDA, EMA) -- primary re-analysis of trial data; 3 registry results (ClinicalTrials.gov / AACT) -- sponsor-posted structured data; 4 HTA assessment (NICE); 5 older meta-analyses -- **pointers only, never the number itself** (several published reviews relabelled ELIXA's 4-point MACE as 3-point; a value found in a meta is traced to a level 1-4 source or refused). A label such as `PUBLISHED_UNADJUSTED` is assigned only after the estimator is read at the source. - **Full-text reachability ladder.** Before `abstract only` may be recorded the extractor tries, in order: PMC / Europe PMC deposits; supplementary appendices (where exact secondary endpoints such as ELIXA's and FREEDOM-CVO's 3-point MACE live); publisher open-access versions; author accepted manuscripts in institutional repositories; regulatory documents (FDA, EMA); ClinicalTrials.gov / AACT results. The route that succeeded is recorded; `abstract only` is replaced by `full text not reachable after N named attempts`, listing them. An unreachability claim with no attempt log is the same defect as an absence claim with no negative citation. - **Comparator.** The published comparator meta-analysis is resolved **only after the independent evidence search is locked**; published meta-analyses are used for reference checking, never for seeding. Parity compares the comparator's eligibility rules, not only its trial list. - **Harms.** Gastrointestinal adverse events and discontinuation due to adverse events are prespecified harm outcomes. Any further harm outcome a resolved comparator happens to report is **exploratory**, not prespecified, and is labelled so. - **Risk of bias.** Full outcome-specific RoB 2 on the primary result (effect of assignment): five domains, signalling questions, information sources (protocol, statistical analysis plan, registry record, primary publication and supplement), adjudication method (two assessors, disagreements recorded, not silently resolved), and a planned sensitivity analysis restricted to low-risk-of-bias trials. Registry-derived machine signals are rendered as `machine signal consistent with low risk; formal RoB 2 not assessed` until the sources above have been read; they are never rendered as RoB 2 judgements. - **GRADE.** Prespecified across all five domains (risk of bias, inconsistency, imprecision, indirectness, publication bias). **No certainty category is issued while any domain is unassessed**; the page renders `GRADE provisional -- not yet fully assessable` instead. Imprecision reflects whether the confidence interval permits materially different clinical conclusions, not a mechanical significance test; a prediction interval approaching 1 is not by itself grounds for downgrading. - **Pre-specified list (intervention agents).** liraglutide; semaglutide (subcutaneous and oral); dulaglutide; albiglutide; efpeglenatide; exenatide (immediate- and extended-release; ITCA 650 continuous subcutaneous delivery on the `GLP1RA_ANY_DELIVERY` strand); lixisenatide. ## Retrospective executable clarification — 2026-09-17 This states which existing B-prime rules bind effect-type unification; it changes no clinical rule. Endpoint components (3-point MACE), effect measure (HR, pooled on the log scale), and timepoint/censoring (end of randomised follow-up) are binding. Analysis set, adjustment, estimator, time origin, and follow-up length are disclosed, not binding. All other axes are non-binding. Unknown evidence remains UNKNOWN with its absence code; a missing binding value cannot be filled from this target. ```effect-type-binding { "schema_version": 1, "outcomes": { "3-point major adverse cardiovascular events": { "endpoint_components": [ "CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE" ], "effect_measure": "HR", "censoring": "end-of-study" } } } ```; L1: SENTENCE_WITHOUT_OBJECT : Snapshot: records_sha256 1e0282f5; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query retrieved which record was not recorded; every record's found_by names this single source.; L1: SENTENCE_WITHOUT_OBJECT : This page replays the committed retrieval snapshot; it is not a claim that the protocol SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present).; L1: SENTENCE_WITHOUT_OBJECT : No search was run for this topic: every PubMed source is a PMID enumeration.; L1: SENTENCE_WITHOUT_OBJECT : Citation chase: NOT_RUN · ClinicalTrials.gov: RAN_OK · Europe PMC (OA + metadata): RAN_OK · Legacy unrecorded retrieval: RAN_OK · PMC full text: NOT_RUN · PubMed: RAN_OK · Registry-first (AACT): RAN_OK — RAN_OK = ran and returned records; RAN_ZERO = ran, none matched; RAN_ERROR = attempted but failed; NOT_RUN = not attempted for this topic.; L1: SENTENCE_WITHOUT_OBJECT : KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this topic. an auditable screening ledger attached to an unauditable retrieval process.; L1: SENTENCE_WITHOUT_OBJECT : Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK; its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications (UID/PMID-anchored queries for pre-identified trials), which cannot discover an unknown eligible trial. A fetch of named identifiers is not a systematic search. We retract any claim of a registry-first or systematic search for this topic.; L1: SENTENCE_WITHOUT_OBJECT : Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.; L1: SENTENCE_WITHOUT_OBJECT : Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).; L1: SENTENCE_WITHOUT_OBJECT : Identifier scope: identifier leading token matches class term GLP-1RA. Verdict: NOT_APPLICABLE.; L1: SENTENCE_WITHOUT_OBJECT : Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.; L1: SENTENCE_WITHOUT_OBJECT : Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.; L1: SENTENCE_WITHOUT_OBJECT : Positive: Recovered & included the canonical trials ['27295427', '27633186', '31189511'] that a comparator includes; none missed.; L1: SENTENCE_WITHOUT_OBJECT : Negative: Cross-topic trial(s) ['37952131'] recovered by the search and correctly EXCLUDED ['37952131'] by rule (same drug/design, wrong topic).; L1: SENTENCE_WITHOUT_OBJECT : 2 of 25 declared-absent/refusal reason code(s) have a numeric value in a held source; 0 wrong-kind code(s); 0 not verifiable from held sources. Registered-outcome sweep: 4 of 33 included-trial/outcome pair(s) are held-but-not-extracted.; L1: SENTENCE_WITHOUT_OBJECT : 34873344; L1: SENTENCE_WITHOUT_OBJECT : Gastrointestinal adverse events; L1: SENTENCE_WITHOUT_OBJECT : OUTCOME_NOT_IN_SOURCE; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : abstract:34873344; L1: SENTENCE_WITHOUT_OBJECT : Adverse events were more frequent in the ITCA 650 group (72%, 1,491/2,074) than in the placebo group (63.9%, 1,325/2,070), mainly due to an increase in gastrointestinal events and disorders while on ITCA 650.; L1: SENTENCE_WITHOUT_OBJECT : 27295427; L1: SENTENCE_WITHOUT_OBJECT : Adverse events leading to discontinuation; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : fulltext:27295427; L1: SENTENCE_WITHOUT_OBJECT : The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) than in the placebo group (694 of 4672 [14.9%]) (hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97; P&lt;0.00...; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : PMID 34215025; L1: SENTENCE_WITHOUT_OBJECT : not extracted (see reason); L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : EFFECT_TYPE_REFUSED; L1: SENTENCE_WITHOUT_OBJECT : reason-code audit: REASON_TRUE; L1: SENTENCE_WITHOUT_OBJECT : basis: EFFECT_TYPE_REFUSED: effect_type.unify: UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : completeness: eligible+completed+results_available; L1: SENTENCE_WITHOUT_OBJECT : completeness basis: CT.gov status/results dates from local AACT snapshot; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : PMID 30291013; L1: SENTENCE_WITHOUT_OBJECT : not extracted (see reason); L1: SENTENCE_WITHOUT_OBJECT : axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : EFFECT_TYPE_REFUSED; L1: SENTENCE_WITHOUT_OBJECT : reason-code audit: REASON_TRUE; L1: SENTENCE_WITHOUT_OBJECT : basis: EFFECT_TYPE_REFUSED: effect_type.unify: axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : completeness: eligible+completed+results_available; L1: SENTENCE_WITHOUT_OBJECT : completeness basis: CT.gov status/results dates from local AACT snapshot; L1: SENTENCE_WITHOUT_OBJECT : FLOW; L1: SENTENCE_WITHOUT_OBJECT : PMID 38785209; L1: SENTENCE_WITHOUT_OBJECT : not extracted — abstract only, full text not retrieved; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : EFFECT_TYPE_REFUSED; L1: SENTENCE_WITHOUT_OBJECT : reason-code audit: REASON_TRUE; L1: SENTENCE_WITHOUT_OBJECT : basis: EFFECT_TYPE_REFUSED: effect_type.unify: UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : completeness: eligible+completed+results_available; L1: SENTENCE_WITHOUT_OBJECT : completeness basis: CT.gov status/results dates from local AACT snapshot; L1: SENTENCE_WITHOUT_OBJECT : Candidate rows, including type refusals.; L1: SENTENCE_WITHOUT_OBJECT : Protocol-declared binding axes: endpoint_components, effect_measure, censoring. All remaining axes are non-binding.; L1: SENTENCE_WITHOUT_OBJECT : 1. population; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 2. randomised_contrast; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 3. analysis_set; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: intention-to-treat; L1: SENTENCE_WITHOUT_OBJECT : record:31189511.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: intention-to-treat; L1: SENTENCE_WITHOUT_OBJECT : record:30291013.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: intention-to-treat; L1: SENTENCE_WITHOUT_OBJECT : record:28910237.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: ITT; L1: SENTENCE_WITHOUT_OBJECT : record:26630143.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 4. endpoint_components; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome in a time-to-event analysis was the first occurrence of a major adverse cardiovascular event (death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke); L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary composite outcome in the time-to-event analysis was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome was the first major adverse cardiovascular event (MACE; a composite of nonfatal myocardial infarction, nonfatal stroke, or death from cardiovascular or undetermined causes); L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome was the first occurrence of the composite endpoint of non-fatal myocardial infarction, non-fatal stroke, or death from cardiovascular causes (including unknown causes), which was assessed in the intention-to-treat population; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED']; L1: SENTENCE_WITHOUT_OBJECT : span: We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: MACE, defined as cardiovascular death, non-fatal MI, and non-fatal stroke; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: Number of Participants From Time of Randomization to Time to First Occurrence of a Major Adverse Cardiovascular Event (MACE): Acute Myocardial Infarction (Non Fatal); Non-fatal Stroke; and CV Death; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : 5. first_or_recurrent; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:31185157.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:27633186.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:27295427.source; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:31189511.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:30291013.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:28910237.source; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: time-to-first; L1: SENTENCE_WITHOUT_OBJECT : record:40162642.source; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 6. time_origin; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 7. follow_up; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : median follow-up was 3.8 years; L1: SENTENCE_WITHOUT_OBJECT : span: median follow-up was 3.8 years; L1: SENTENCE_WITHOUT_OBJECT : record:27295427.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : median follow-up of 1.81 years; L1: SENTENCE_WITHOUT_OBJECT : span: median follow-up of 1.81 years; L1: SENTENCE_WITHOUT_OBJECT : record:34215025.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : followed for a median of 3.2 years; L1: SENTENCE_WITHOUT_OBJECT : span: followed for a median of 3.2 years; L1: SENTENCE_WITHOUT_OBJECT : record:28910237.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : followed for a median of 25 months; L1: SENTENCE_WITHOUT_OBJECT : span: followed for a median of 25 months; L1: SENTENCE_WITHOUT_OBJECT : record:26630143.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : median follow-up was 3.4 years; L1: SENTENCE_WITHOUT_OBJECT : span: median follow-up was 3.4 years; L1: SENTENCE_WITHOUT_OBJECT : record:38785209.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : 8. censoring; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: Number of participants experiencing a first event of a MACE, defined as cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke are presented. Results are based on the in-trial observation period which started at the date of randomisation, included the period after permanent trial product discontinuation, if any and ended at the date of the follow-up visit regardless of adherence to treatment.; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: Time from randomisation up to end of follow-up (scheduled at week 109); L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; events occurring after that visit were not included.; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/ft_27295427.txt; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: From randomization to first occurrence or death from any cause or study completion (Median Follow-Up of 5.4 Years); L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome.; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: The planned closeout of follow-up of the patients was from December 5, 2016, to May 11, 2017, after the prespecified required minimum of 1360 patients were confirmed to have had a primary composite outcome event.; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/ft_28910237.txt; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: MACE endpoint (on-study) 1.02 (0.89, 1.18) No. of patients with event (%) 392 (12.9%) 400 (13.2%) Total Person Year 6340.2 6368.7 Incidence Rate 6.18 6.28; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: Number of participants with first occurrence of EAC (event adjudication committee) confirmed major adverse cardiovascular event (MACE), a composite end-point. i.e., from time of randomization to first occurrence of cardiovascular (CV) death, non-fatal myocardial infarction and non-fatal stroke combined data during in-trial period were reported. In-trial observation period was defined as the period from date of randomization to the first of (both inclusive): date of follow-up visit, date when participant withdrew consent, date of last contact with participant (for participant lost to follow-up), and date of death.; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : 9. effect_measure; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.79; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.74; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.87; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.73; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio [HR] 0·88, 95% CI 0·79-0·99; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio 0·78, 95% CI 0·68-0·90; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.91; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio is (0.887, 1.172) with a point estimate of 1.02.; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.86; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P&#x2009;=&#x2009;0.029); L1: SENTENCE_WITHOUT_OBJECT : outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml; L1: SENTENCE_WITHOUT_OBJECT : 10. adjustment; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 11. estimator; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 12. report; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "2fc31abdf24b1a27d1ee79dd424b3faac680c376e1c86b819c0d0f1bd6c89e40", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : PMID 31185157: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 27633186: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 27295427: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 34215025: UNKNOWN_FAILS_CLOSED — UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : PMID 31189511: MATCH — axis 1 unstated; axis 2 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 30291013: REFUSE — axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : PMID 28910237: MATCH — axis 1 unstated; axis 2 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 26630143: MATCH — axis 1 unstated; axis 2 unstated; axis 5 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 40162642: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 38785209: UNKNOWN_FAILS_CLOSED — UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : No declared coercions.; L1: SENTENCE_WITHOUT_OBJECT : GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs. (2021), Cardiovasc Diabetol; L1: SENTENCE_WITHOUT_OBJECT : PMID 34526024; L1: SENTENCE_WITHOUT_OBJECT : True; L1: SENTENCE_WITHOUT_OBJECT : https://doi.org/10.1186/s12933-021-01366-8; L1: SENTENCE_WITHOUT_OBJECT : Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94; L1: SENTENCE_WITHOUT_OBJECT : ✓ same question. Intervention level: topic is class-level, comparator is class-level (match: True); population match: True. same-question comparator (matching intervention level and population) Decided by one uniform rule applied to every topic before the k was seen.; L1: SENTENCE_WITHOUT_OBJECT : 7; L1: SENTENCE_WITHOUT_OBJECT : 8; L1: SENTENCE_WITHOUT_OBJECT : 6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina. Characteristics of trials and patients are reported, respectively, in Table 1 . The populations studied ranged in size from 3297 (SUSTAIN-6) to 14,752 (EXSCEL), were of similar age (mean age was 64.0 ± 1.97 years), 37,117 were mal; L1: SENTENCE_WITHOUT_OBJECT : 6; L1: SENTENCE_WITHOUT_OBJECT : SOUL; L1: SENTENCE_WITHOUT_OBJECT : AMPLITUDE-O, HARMONY Outcomes; L1: SENTENCE_WITHOUT_OBJECT : cached comparator text trial-set enumeration; L1: SENTENCE_WITHOUT_OBJECT : Comparator trial set was measured from cached comparator abstract/full text.; L1: SENTENCE_WITHOUT_OBJECT : MEASURED; L1: SENTENCE_WITHOUT_OBJECT : named table rows; L1: SENTENCE_WITHOUT_OBJECT : ELIXA, LEADER, SUSTAIN-6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6, AMPLITUDE-O; L1: SENTENCE_WITHOUT_OBJECT : COMPARATOR_PREDATES_POOLED_TRIAL(SOUL); L1: SENTENCE_WITHOUT_OBJECT : Comparator search ran to 2021-06-30; SOUL is a 2025 pooled trial.; L1: SENTENCE_WITHOUT_OBJECT : The comparator k above is auto-extracted from the comparator's own text and may reference a sub-analysis rather than its same-scope pooled total; the enumerated same-scope comparator k (scope-classified, the finishing metric) is the figure in the parity table, which governs where these differ.; L1: SENTENCE_WITHOUT_OBJECT : Compliance with the PRISMA 2020 reporting items, derived from the review object so it cannot drift from the page. Every item is rendered or declared absent with a reason.; L1: SENTENCE_WITHOUT_OBJECT : 5 Eligibility criteria; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.; L1: SENTENCE_WITHOUT_OBJECT : 6 Information sources + dates; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Search tab — PubMed, ClinicalTrials.gov; run 2026-09-11; AACT snapshot dated on the ghost/recall blocks.; L1: SENTENCE_WITHOUT_OBJECT : 7 Full search strategy, verbatim, every source; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Search tab — the exact PubMed and ClinicalTrials.gov queries are printed verbatim and are re-runnable.; L1: SENTENCE_WITHOUT_OBJECT : 8 Selection process (screeners, disagreement); L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Two independently-implemented rule screeners; disagreement rate 0.0% (0/13); rule-based adjudicates. CAVEAT: both rule sets share an author and the same criteria, so they are NOT statistically independent and this agreement overstates reliability — a genuinely independent model screener is the next step.; L1: SENTENCE_WITHOUT_OBJECT : 9 Data collection process; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Results tab + per-trial Source column — source hierarchy (abstract > CT.gov structured > full text > hand-verified AACT arms), round-trip validation on every extraction, outcome-identity gating; refuse on ambiguity.; L1: SENTENCE_WITHOUT_OBJECT : 15 Certainty assessment; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Results tab — the machine-computable certainty signals are shown: imprecision via the 95% CI and the prediction interval, inconsistency via tau^2. A PARTIAL, object-derived GRADE is now rendered on the Risk-of-bias tab (risk-of-bias, inconsistency and imprecision computed from committed fields; publication bias is NOT ASSESSED automatically; any registry ghost census is descriptive until a PICO-scoped denominator is available; indirectness left to human judgement) — a graded certainty label with each domain's basis, not a full hand-graded GRADE.; L1: SENTENCE_WITHOUT_OBJECT : 16a Flow with counts at every stage; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Screening tab — PRISMA flow: identified -> screened -> excluded-by-rule (counts) -> eligible -> pooled k -> declared-absent.; L1: SENTENCE_WITHOUT_OBJECT : 16b Exclusions with reasons; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Screening tab — every excluded record lists its rule id, a reason true of the record, and a verbatim span.; L1: SENTENCE_WITHOUT_OBJECT : 24a-c Registration & protocol; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Protocol + Reproducibility tabs — the protocol first entered the repository inside a BUILD commit (SHA bf99a91652), so prospective precedence is NOT demonstrated here and protocol-SHA byte-for-byte reproduction is not claimed; eligibility is generated from the structured object.; L1: SENTENCE_WITHOUT_OBJECT : 0; L1: SENTENCE_WITHOUT_OBJECT : NOT demonstrated for this topic — no protocol-only commit exists; the protocol first entered the repository inside a build commit (bf99a91652e74347e4e10cf6b9f1962aee4e596d), so this repository's history does not show the protocol preceding synthesis. The PICO is still fixed and replay from the committed cache is deterministic; only prospective PRECEDENCE is unproven here.; L1: SENTENCE_WITHOUT_OBJECT : bf99a91652e74347e4e10cf6b9f1962aee4e596d; L1: SENTENCE_WITHOUT_OBJECT : 0587d3e282ee11a79d619d50b2216a3cb5964eb26d75992475f3d9d29cfc7fed; L1: SENTENCE_WITHOUT_OBJECT : True; L1: SENTENCE_WITHOUT_OBJECT : Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.; L1: SENTENCE_WITHOUT_OBJECT : Each stated result on this page — whether it is statistically significant, whether its interval spans no effect — is derived from a single claim object, not recomputed per surface. At build the rendered page and manuscript are scanned for any wording that asserts the opposite of that object; the build is refused on a contradiction. Claims checked: 3; contradictions caught: 0; scope: grade=1, outcome_result=1, rob_sensitivity=3, strand_pool=2; surfaces checked=3; not in scope: verbatim source quotations, external comparator prose.; L1: SENTENCE_WITHOUT_OBJECT : Beyond significance, the build also refuses object-backed proposition contradictions: publication-bias state, declared-vs-enforced eligibility, protocol-SHA byte replay, pooled/rated/retracted counts, search-found membership, and state-label collapses. Proposition contradictions caught: 0; scope: publication_bias_state=1, declared_equals_enforced=1, byte_reproducible=1, pooled_count=1, rated_count=1, retracted_count=1, search_found=0, state_collapsed=0; not in scope: verbatim source quotations, external comparator prose without a committed object row.; L1: SENTENCE_WITHOUT_OBJECT : The prose protocol and executable config agree on these checked dimensions: none. Compared as separate sources.; L1: SENTENCE_WITHOUT_OBJECT : RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.; L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 6 known reported outcome(s) unresolved (31185157, 27633186, 27295427, 34215025, 31189511, FREEDOM-CVO) among 6 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.; Adverse events leading to discontinuation: HARMS_INCOMPLETE -- 3 known reported outcome(s) unresolved (31185157, 27633186, 27295427) among 3 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
```

### reproduce

```powershell
python -X utf8 scripts/reproduce_review.py glp1-ra-mace-t2d
```

```text
  OK  glp1-ra-mace-t2d

1/1 reproduce (all reproducible)
```

### scope

```powershell
python -X utf8 scripts/claim_scope_sweep.py
```

```text
UNVERIFIED_FACT: 27 of 38 verified_effects rows
Pages scanned: 32; scope_complete=false
```

### ui

```powershell
python -X utf8 -m pytest tests/test_glp1_ui.py -q --disable-warnings
```

```text
.                                                                        [100%]
1 passed in 32.38s
```

### affected

```powershell
python -X utf8 -m pytest tests/test_lane_fix1.py tests/test_design_key.py tests/test_cgx3c_sections.py tests/test_effect_type.py tests/test_typg_axis_evidence.py tests/test_comparator_second_pass.py -q --disable-warnings
```

```text
..............................................                           [100%]
46 passed in 72.94s (0:01:12)
```

### remaining

```powershell
python -X utf8 .tmp/check_remaining.py  # seven failing nodes named in STUCK_FAILURES.md
```

```text
FFFFFFF                                                                  [100%]
================================== FAILURES ===================================
__________________________ test_real_store_validates __________________________

    def test_real_store_validates() -> None:
        ok, reasons = fixstate.check(ROOT)
    
>       assert ok, "\n".join(reasons)
E       AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
E         docs/evidence/search-acquisition-2026-09-14/README.md fix-state line is stale; run python scripts/rewrite_fixstate_lines.py
E         docs/evidence/search-v2-measurement-2026-09-15/README.md fix-state line is stale; run python scripts/rewrite_fixstate_lines.py
E       assert False

tests\test_fixstate.py:457: AssertionError
___________________ test_valid_page_passes_non_replay_limbs ___________________

    def test_valid_page_passes_non_replay_limbs():
        # The synthetic fixture has no committed topic/cache, so the Level-B replay limb cannot
        # run against it (correctly: a page with no reproducible pipeline is not publishable).
        # Here we assert the fixture satisfies every OTHER limb; full reproduction is tested
        # against a real committed review below.
        from harness.gate import check_limb1, check_limb2, check_primary_result, _load
        with tempfile.TemporaryDirectory() as tmp:
            d = _build(tmp)
            manifest, html, rep = _load(d)
            reasons = (check_limb1(d, manifest, html, rep)
                       + check_primary_result(d) + check_limb2(manifest, html))
>           assert not reasons, f"valid page should pass non-replay limbs, got: {reasons}"
E           AssertionError: valid page should pass non-replay limbs, got: ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects']
E           assert not ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects']

tests\test_gate.py:98: AssertionError
__________________________ test_real_registry_passes __________________________

    def test_real_registry_passes():
        ok, reasons = gate_scorecard.check(ROOT)
>       assert ok, "\n".join(reasons)
E       AssertionError: registry/gate_scorecard.json missing entry for enumerated gate gate.check_effect_types
E         registry/gate_scorecard.json missing entry for enumerated gate gate.check_typed_renderings
E       assert False

tests\test_gate_scorecard.py:356: AssertionError
___________ test_committed_integrity_is_fresh_for_every_live_topic ____________

    def test_committed_integrity_is_fresh_for_every_live_topic():
        """Corpus invariant (the durable fix for the stale-n_pooled defect the fair blind re-judge
        flagged): for every live topic that carries an integrity.json, its n_pooled and the PMIDs it
        actually checked (per_pmid keys) MUST equal the current all-outcome pooled PMID union. A pool
        change (a recovery added, a dedup drop) that is not followed by a fresh integrity run makes the
        retraction line report a wrong count — exactly the class this test forbids from returning."""
        reviews = os.path.join(ROOT, "docs", "reviews")
        if not os.path.isdir(reviews):
            return  # not a full repo checkout; nothing to assert
        checked = 0
        stale = []
        for slug in sorted(os.listdir(reviews)):
            rp = os.path.join(reviews, slug, "review.json")
            ip = os.path.join(ROOT, "cache", slug, "integrity.json")
            if not (os.path.exists(rp) and os.path.exists(ip)):
                continue
            rev = json.load(open(rp, encoding="utf-8"))
            integ = json.load(open(ip, encoding="utf-8"))
            union = _pooled_pmid_union(rev)
            checked += 1
            if integ.get("n_pooled") != len(union):
                stale.append(f"{slug}: n_pooled={integ.get('n_pooled')} != pooled union {len(union)}")
            elif set(integ.get("per_pmid", {})) != union:
                missing = union - set(integ.get("per_pmid", {}))
                extra = set(integ.get("per_pmid", {})) - union
                stale.append(f"{slug}: per_pmid coverage drifted (missing={sorted(missing)} extra={sorted(extra)})")
>       assert not stale, "stale integrity.json (re-run scripts/integrity_check.py): " + "; ".join(stale)
E       AssertionError: stale integrity.json (re-run scripts/integrity_check.py): glp1-ra-mace-t2d: n_pooled=10 != pooled union 7
E       assert not ['glp1-ra-mace-t2d: n_pooled=10 != pooled union 7']

tests\test_integrity.py:80: AssertionError
__ test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews __

    def test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews():
        rows = []
        for review_dir in _review_dirs():
            review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
            assert "limitations" in review, review["slug"]
            page_texts = _page_limitation_block_texts(review)
            object_texts = _limitation_block_texts(review)
            rows.append((review["slug"], sum(page_texts.values()), sum(object_texts.values())))
            if object_texts == page_texts:
                continue
            stale_codes = {v["code"] for v in claimgraph.check(review)}
            extra_objects = object_texts - page_texts
            extra_pages = page_texts - object_texts
>           assert not review.get("claimgraph"), review["slug"]
E           AssertionError: balanced-crystalloids-vs-saline-mortality
E           assert not {'objects': [{'claim_id': 'a29165ecd31799dd', 'depends_on': {'input_set_version': 'b6c7145842a2d8ea1b8c83b26799692a4bb..._version': 'b6c7145842a2d8ea1b8c83b26799692a4bb8428a12358195beba01e4cb46a9d2'}, 'kind': 'manuscript_result_sentence'}]}
E            +  where {'objects': [{'claim_id': 'a29165ecd31799dd', 'depends_on': {'input_set_version': 'b6c7145842a2d8ea1b8c83b26799692a4bb..._version': 'b6c7145842a2d8ea1b8c83b26799692a4bb8428a12358195beba01e4cb46a9d2'}, 'kind': 'manuscript_result_sentence'}]} = <built-in method get of dict object at 0x000002537E860A40>('claimgraph')
E            +    where <built-in method get of dict object at 0x000002537E860A40> = {'arm_contrast': {'current_pooled_trial_ids': ['34375394', '35041780'], 'metric_label': 'parser-confirmed contrast', '... for this build; refused trials remain screened-in eligible records but are named exclusions, not pooled counts.', ...}.get

tests\test_limitations_legacy_compare.py:49: AssertionError
_____________ test_override_audit_covers_every_committed_override _____________

    def test_override_audit_covers_every_committed_override():
        audited = json.loads(AUDIT.read_text(encoding="utf-8"))
        audited_by_key = {_key(row): row for row in audited}
        required = {_key(row) for row in _override_rows_in_cache()}
    
        missing = sorted(required - set(audited_by_key))
        extra = sorted(set(audited_by_key) - required)
>       assert not missing, "override(s) missing from audit: " + repr(missing)
E       AssertionError: override(s) missing from audit: [('esketamine-trd-madrs', 'verified_arms.json', 'NCT02417064', 'Observed-case Day-28 raw change-score MADRS MD'), ('sglt2-ckd-progression', 'verified_effects.json', '32970396', 'Trial-defined primary cardiorenal composite'), ('sglt2-ckd-progression', 'verified_effects.json', '36331190', 'Trial-defined primary cardiorenal composite')]
E       assert not [('esketamine-trd-madrs', 'verified_arms.json', 'NCT02417064', 'Observed-case Day-28 raw change-score MADRS MD'), ('sg...osite'), ('sglt2-ckd-progression', 'verified_effects.json', '36331190', 'Trial-defined primary cardiorenal composite')]

tests\test_override_audit.py:34: AssertionError
_________ test_error_rate_is_fresh_against_current_pooled_population __________

    def test_error_rate_is_fresh_against_current_pooled_population():
        """A measured-once figure that looks live is the stale-number class in a new costume. The committed
        error_rate.json must have been measured against exactly the current pooled population; if a pooled
        number was added/removed/renamed since, this fails and the census must be re-run."""
        ep = os.path.join(DOCS, "error_rate.json")
        sp = os.path.join(DOCS, "error_rate_sample.json")
        if not os.path.exists(ep):
            return
        d = json.load(open(ep, encoding="utf-8"))
        assert os.path.exists(sp), "error_rate.json exists but the committed sample docs/error_rate_sample.json does not"
        sample = json.load(open(sp, encoding="utf-8"))
        sample_ids = {row["row_id"] for row in sample["rows"]}
        pop = _pooled_population()
        assert d.get("population") == len(sample_ids), "error_rate.json population != committed sample size"
        # EVERY currently-pooled number must be in the committed census sample: a new pooled number that was
        # never censused makes the live rate stale and fails here (re-run the census).
        uncensused = sorted(pop - sample_ids)
>       assert not uncensused, (f"pooled numbers not in the error-rate census sample: {uncensused[:5]} — "
                                "re-run scripts/error_rate_compare.py + error_rate_pass2.py and rebuild the sample")
E       AssertionError: pooled numbers not in the error-rate census sample: ['glp1-ra-mace-t2d::3-point major adverse cardiovascular events::26630143'] — re-run scripts/error_rate_compare.py + error_rate_pass2.py and rebuild the sample
E       assert not ['glp1-ra-mace-t2d::3-point major adverse cardiovascular events::26630143']

tests\test_stage_additions.py:271: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
7 failed in 72.39s (0:01:12)
```

### full-suite

```powershell
python -X utf8 -m pytest -q --disable-warnings
```

```text

=================================== ERRORS ====================================
_______________ ERROR collecting tests/test_search_v2_isrctn.py _______________
import file mismatch:
imported module 'test_search_v2_isrctn' has this __file__ attribute:
  C:\mh-r-FIX1\outputs\search_v2\lanes\R2\test_search_v2_isrctn.py
which is not the same as the test file we want to collect:
  C:\mh-r-FIX1\tests\test_search_v2_isrctn.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
=========================== short test summary info ===========================
ERROR tests/test_search_v2_isrctn.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 11.20s
```

### full-suite-tests

```powershell
python -X utf8 -m pytest tests -q --disable-warnings
```

```text
=========================== short test summary info ===========================
FAILED tests/test_cgx3c_sections.py::test_parity_contradiction_is_computed_not_repeated
FAILED tests/test_design_key.py::test_reported_unadjusted_cluster_crossover_needs_refusal
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
9 failed, 958 passed in 1145.14s (0:19:05)
```

A wrapper exit of zero for the gate only means the returned verdict was printed. It does not mean publication passed. The root-level pytest command encountered a duplicate archived test module; `tests/` is the suite used by `scripts/verify_all.py::limb_unit_tests`. The full run collected the prior parity and design-label expectations before those two tests were corrected; the affected-test rerun above tests their final versions. The other seven failures remain logged, not waived. No final full-suite PASS is claimed.

## Other-page impact inventory (no other page rebuilt)

MEASURED read-only function probes against held objects; INFERRED prospective page changes on a future rebuild. No new clinical output for these pages is certified. Estimator labels are re-evaluated from typed evidence; harm states compare baseline and fixed functions on identical held source inputs. Composite probes use the current selected rows and typed endpoint signatures.

### balanced-crystalloids-vs-saline-mortality

- Mortality / PMID 34375394: estimator_source PUBLISHED_ADJUSTED -> ADJUSTMENT_UNKNOWN

### colchicine-postop-af

- Postoperative atrial fibrillation / PMID 42132185: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### colchicine-recurrent-pericarditis

- Recurrent pericarditis / PMID 24694983: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Recurrent pericarditis / PMID 21873705: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Symptom persistence at 72 hours / PMID 21873705: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Adverse events (gastrointestinal) / PMID 21873705: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation

### colchicine-secondary-cv-prevention

- Trial-defined major coronary/cardiovascular composite / PMID 31733140: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Trial-defined major coronary/cardiovascular composite / PMID 32865380: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Trial-defined major coronary/cardiovascular composite / PMID 39555823: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Gastrointestinal adverse effects / PMID 40263680: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Gastrointestinal adverse effects / PMID 1593057: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Non-cardiovascular death / PMID 32865380: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### corticosteroids-cap-mortality

- Hyperglycaemia / PMID 25608756: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### corticosteroids-covid19-mortality

- 28-day all-cause mortality / PMID 32678530: estimator_source PUBLISHED_ADJUSTED -> ADJUSTMENT_UNKNOWN

### dapagliflozin-hfpef-hosp

- Composite cardiovascular death or worsening heart failure / PMID 36027570: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### denosumab-vertebral-fracture

- New vertebral fracture / PMID 19671655: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Nonvertebral fracture / PMID 19671655: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Hip fracture / PMID 19671655: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### doac-vte-recurrence

- Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 24344086: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 19966341: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 22449293: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 21128814: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23991658: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23808982: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### dpp4-mace-t2d

- 3-point major adverse cardiovascular events / PMID 23992601: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- 3-point major adverse cardiovascular events / PMID 30418475: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- 3-point major adverse cardiovascular events / PMID 28893244: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### empagliflozin-hfpef-hosp

- Composite cardiovascular death or worsening heart failure / PMID 34449189: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### finerenone-ckd-t2d-renal

- Kidney composite outcome / PMID 33264825: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Kidney composite outcome / PMID 34449181: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### iv-iron-hfref-hosp

- Heart-failure hospitalization / PMID 40159390: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Heart-failure hospitalization / PMID 25176939: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### metformin-pcos-ovulation

- Gastrointestinal adverse events / PMID 16769748: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation

### noac-vs-warfarin-af-stroke

- Stroke or systemic embolism / PMID 21830957: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Stroke or systemic embolism / PMID 19717844: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Stroke or systemic embolism / PMID 24251359: estimator_source PUBLISHED_ADJUSTED -> ADJUSTMENT_UNKNOWN
- Stroke or systemic embolism / PMID 21870978: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major bleeding / PMID 21830957: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major bleeding / PMID 19717844: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major bleeding / PMID 24251359: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major bleeding / PMID 21870978: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### omega3-cardiovascular-events

- Major vascular events / MACE / PMID 33190147: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE / PMID 30415637: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE / PMID 30415628: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE / PMID 30146932: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE / PMID 22686415: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE / PMID 20929341: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE / PMID 21115589: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / MACE: composite warning recalculates from selected endpoint; new="pooled trials use each trial's OWN primary composite; component sets differ across trials (endpoint definitions: ASCEND: serious vascular event adds TIA, excludes intracranial haemorrhage.; DISCLOSED (composite-heterogeneity note); Alpha Omega: composite includes cardiac interventions/revascularization.; DISCLOSED (composite-heterogeneity note); Major cardiovascular events, defined as a composite of non-fatal myocardial infarction, stroke, or death from cardiovascular disease; Major vascular events / MACE; REDUCE-IT: 5-point primary (adds unstable angina, revascularization).; DISCLOSED (composite-heterogeneity note on the pool); STRENGTH: 5-point primary.; DISCLOSED (composite-heterogeneity note); primary outcome was death from cardiovascular causes) -- the pooled estimate mixes composite definitions (disclosed, not adjusted)"

### pcsk9-mace

- Major adverse cardiovascular events / PMID 28304224: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major adverse cardiovascular events / PMID 30403574: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major adverse cardiovascular events / PMID 41211925: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major adverse cardiovascular events: composite warning recalculates from selected endpoint; new="pooled trials use each trial's OWN primary composite; component sets differ across trials (endpoint definitions: FOURIER: 5-point primary (adds unstable angina, revascularization).; DISCLOSED (composite-heterogeneity note); Major adverse cardiovascular events; ODYSSEY: 4-point primary (adds unstable angina requiring hospitalization).; DISCLOSED (composite-heterogeneity note)) -- the pooled estimate mixes composite definitions (disclosed, not adjusted)"
- Adverse events leading to discontinuation / PMID 28304224: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Adverse events leading to discontinuation / PMID 30403574: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Adverse events leading to discontinuation / PMID 25773378: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation

### probiotics-aad-prevention

- Antibiotic-associated diarrhoea / PMID 40488914: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Antibiotic-associated diarrhoea / PMID 35727573: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Antibiotic-associated diarrhoea / PMID 24772726: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Antibiotic-associated diarrhoea / PMID 23932219: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Antibiotic-associated diarrhoea / PMID 18701826: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Antibiotic-associated diarrhoea / PMID 18410562: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Antibiotic-associated diarrhoea / PMID 7872284: estimator_source PUBLISHED_ADJUSTED -> ADJUSTMENT_UNKNOWN
- Any adverse events / PMID 40716758: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 39935568: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 35727573: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 32035998: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 30149135: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 18701826: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 18410562: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 16572062: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 15740542: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 9570649: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 2184848: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Any adverse events / PMID 23932219: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_REFUSED_WITH_REASON on reannotation
- Serious adverse events / PMID 42608299: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 41699149: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 40716758: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 40488914: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 39935568: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 39529939: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 39497860: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 39429834: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 38258024: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 35727573: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 32035998: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 30912409: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 30149135: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 27169634: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 24772726: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 18701826: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 18410562: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 16572062: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 15740542: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 9570649: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 2184848: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 21165295: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation
- Serious adverse events / PMID 16292090: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation

### sacubitril-valsartan-hfref

- Composite cardiovascular death or heart-failure hospitalization / PMID 25176015: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Composite cardiovascular death or heart-failure hospitalization / NCT02468232: estimator_source PUBLISHED_ADJUSTED -> ADJUSTMENT_UNKNOWN

### semaglutide-obesity-mace

- 3-point major adverse cardiovascular events / PMID 37952131: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Gastrointestinal adverse events / PMID 37952131: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation

### sglt2-ckd-progression

- Trial-defined primary cardiorenal composite / PMID 32970396: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Trial-defined primary cardiorenal composite / PMID 30990260: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Trial-defined primary cardiorenal composite / PMID 36331190: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Trial-defined primary cardiorenal composite: composite warning recalculates from selected endpoint; new="pooled trials use each trial's OWN primary composite; component sets differ across trials (endpoint definitions: primary outcome was a composite of a sustained decline in the estimated GFR of at least 50%, end-stage kidney disease, or death from renal or cardiovascular causes; primary outcome was a composite of end-stage kidney disease (dialysis, transplantation, or a sustained estimated GFR of <15 ml per minute per 1; primary outcome was a composite of progression of kidney disease (defined as end-stage kidney disease, a sustained decrease in eGFR to <10 ml per minute per 1) -- the pooled estimate mixes composite definitions (disclosed, not adjusted)"

### sglt2-hfref-hosp-cvdeath

- Composite cardiovascular death or hospitalisation for heart failure / PMID 31535829: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Composite cardiovascular death or hospitalisation for heart failure / PMID 32865377: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Diabetic ketoacidosis / PMID 31535829: harm state KNOWN_REPORTED_NOT_YET_EXTRACTED -> RETRIEVED_OUTCOME_NOT_REPORTED on reannotation

### sglt2-primary-prevention-hf

- Hospitalization for heart failure / PMID 28605608: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Hospitalization for heart failure / PMID 26378978: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Hospitalization for heart failure / PMID 32966714: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Hospitalization for heart failure / PMID 30415602: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### spironolactone-hfref-mortality

- All-cause mortality / PMID 10471456: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- All-cause mortality / PMID 21073363: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- All-cause mortality / PMID 28824029: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### statins-primary-prevention-elderly

- Major vascular events / PMID 20404379: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events / PMID 42670961: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major vascular events: composite warning recalculates from selected endpoint; new="pooled trials use each trial's OWN primary composite; component sets differ across trials (endpoint definitions: JUPITER >=70 subgroup: 5-point composite; age cut chosen post-hoc.; DISCLOSED (subgroup + component note); Major vascular events) -- the pooled estimate mixes composite definitions (disclosed, not adjusted)"

### ticagrelor-vs-clopidogrel-acs

- Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke / PMID 19717846: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN
- Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke / PMID 26376600: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### tocilizumab-covid19-mortality

- 28-day all-cause mortality / PMID 33933206: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

### tranexamic-acid-pph

- Death due to bleeding / PMID 28456509: estimator_source PUBLISHED_UNADJUSTED -> ADJUSTMENT_UNKNOWN

## Remaining blockers and scope

See `STUCK_FAILURES.md` for final verification blockers. This lane does not complete harm extraction, execute the amended search, or repair the broader prose-claim registry. No Overmind PASS or publication-ready status is asserted. Project/submission status and the protected rewrite workbook were not changed.
