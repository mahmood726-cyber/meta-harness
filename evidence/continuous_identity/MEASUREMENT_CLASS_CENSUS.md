# Measurement-class census

Pinned review state: 3876a62dca66764dff1b4f84d6b43356a1a9e3bb. Report only; no code/tests/cache/git modifications.

## Denominator and scope

**32 reviews; 3 declared continuous outcomes; N=19 included review-record/outcome slots (6 served, 13 declared absent).** The 29 reviews without continuous outcomes are listed below. N is not independent trials: it includes a pooled post-hoc report. Class memberships can overlap.

The outcome-class census requires source wording tied to the target outcome. Methods mentioned for other outcomes, and misassociated text, do not count. NOT_STATED includes either missing target data or ambiguous ascertainment. PSG in this table is a documented target method without a numerical latency result.

| Class | Included n / N=19 | Served n / N=6 | Numeric target held n / N=19 |
|---|---:|---:|---:|
| PSG | 1/19 | 0/6 | 0/19 |
| DIARY | 2/19 | 1/6 | 2/19 |
| QUESTIONNAIRE | 1/19 | 0/6 | 1/19 |
| ACTIGRAPHY | 0/19 | 0/6 | 0/19 |
| OTHER | 4/19 | 3/6 | 4/19 |
| NOT_STATED | 12/19 | 2/6 | 6/19 |

OTHER here is explicitly clinician-rated MADRS. Weight names the construct; held text does not state a weighing method/device, so it stays NOT_STATED. PSQI question 2 (minutes) and component 2 (ordinal score) share a category but are not the same measurement scale.

## Findings

1. Three of 32 pinned reviews declare continuous outcomes: 19 included review records (6 served, 13 absent), not necessarily 19 independent randomized trials.
2. Wade PMID 20712869 / NCT00397189 has two confirmed target classes: DIARY and QUESTIONNAIRE (PSQI). Served: raw age-65–80 diary difference -19.1 - (-1.7) = -17.4 minutes, n=137/144. Adjusted diary: -15.6 (95% CI -25.3 to -6.0).
3. Wade low-excretor long-term diary: -6.7 (-16.4, 3.0), p=0.174; PSQI question 2: -11.6 (-22.0, -1.1), p=0.030. Keep separate. The user-mentioned all-adult -11.2 versus -6.7 pair is not established by held sources; the located -6.7 is explicitly low-excretor.
4. PSQI component 2 is ordinal; PSQI question 2 is minutes. Same broad class does not make these scales interchangeable.
5. PMID 12790159 documents EEG and daily sleep logs, but held XML has no body/tables and no numeric SOL tuple. Dual study methods do not establish two numerical SOL results.
6. PMID 17875243 gives -24.3 versus -12.9 minutes without explicit instrument binding. PMID 19584739 gives a 9-minute benefit after describing PSG/EEG and questionnaires, without explicitly binding that number. Numeric-result class is unresolved.
7. MADRS is explicitly clinician-rated: OTHER, not a patient-completed questionnaire. Raw, adjusted, LOCF, earlier timepoints and named subgroups stay separate.
8. Both served semaglutide rows have NOT_STATED ascertainment method/device. Weight is a construct, not a documented procedure. STEP 1 serves n=1306/655 versus raw observed n=1212/577; STEP 3 serves n=407/204 versus observed n=373/189.
9. Six embedded-text keys are misassociated: 33157425: four-arm ARE/Ashwagandha plus melatonin actigraphy trial, not 97-person Shanghai PSG trial; 31109201: ELLIPSE prospective observational cohort, not TRANSFORM-2; 31734084: same ELLIPSE text as 31109201, not TRANSFORM-3; 37019044: ResisToday non-interventional study in Portugal, not pooled TRANSFORM predictor analysis; 36273682: systematic review of postoperative delirium, not TRANSFORM irritability analysis; 40825340: obesity pharmacotherapy review, not STEP 11. They are quarantined even where they contain the same measurement scale.
10. PMID 22346363 is a post hoc pooled antihypertensive subgroup report. Table 3 raw changes: -23.3 (SD 2.9) / -7.5 (SD 3.6), n=121/36; narrative decreases: 25.89/7.54, ANCOVA, Cohen d=0.39. Preserve both rather than silently choosing.
11. No attributable target ACTIGRAPHY result confirmed. Wade explicitly reports lack of polysomnographic or actigraphic data.
12. PMID 21091391 explicitly links to NCT00397189 and supplies age-55–80 diary changes -15.4/-5.5 (p=0.014), not the unlocated all-adult -11.2 comparison.
13. A secondary TRANSFORM-2 report (PMID 34293233) prints LS mean -21.4 with CI [-21.2,-18.3], which excludes its own point estimate; retain as a source inconsistency, do not silently repair.

## All included trial records

| Review / record | Served or absent | Target classes | Population | Notes |
|---|---|---|---|---|
| esketamine-trd-madrs / PMID 37025256 | SERVED OTHER | OTHER | full analysis set (FAS/mITT) |  |
| esketamine-trd-madrs / PMID 31109201 | SERVED OTHER | OTHER | full analysis set (FAS/mITT) | Quarantined fulltext key 31109201: ELLIPSE prospective observational cohort, not TRANSFORM-2. Quarantined fulltext key 36273682: systematic review of postoperative delirium, not TRANSFORM irritability analysis. Quarantined fulltext key 37019044: ResisToday non-interventional study in Portugal, not pooled TRANSFORM predictor analysis. |
| esketamine-trd-madrs / NCT02422186 | SERVED OTHER | OTHER | Full eligible elderly TRD (age >=65), with age/onset subgroups retained | PMID 31734084 title explicitly names TRANSFORM-3; linkage is by trial name. Quarantined fulltext key 31734084: same ELLIPSE text as 31109201, not TRANSFORM-3. |
| esketamine-trd-madrs / NCT02417064 | DECLARED ABSENT | OTHER | full analysis set (FAS/mITT) | Quarantined fulltext key 36273682: systematic review of postoperative delirium, not TRANSFORM irritability analysis. Quarantined fulltext key 37019044: ResisToday non-interventional study in Portugal, not pooled TRANSFORM predictor analysis. |
| melatonin-primary-insomnia-sol / PMID 20712869 | SERVED DIARY | DIARY, QUESTIONNAIRE | Age 65-80 subgroup served; low-excretor and other populations kept separate | Question 2 is minutes; component 2 is ordinal. No all-adult -11.2 located; Table 4 -6.7 is low-excretor long-term diary. |
| melatonin-primary-insomnia-sol / PMID 33157425 | DECLARED ABSENT | PSG | Full trial: middle-aged primary insomnia; randomized 51/46 | Also documented study methods: QUESTIONNAIRE. PSG SOL described without numeric estimate. PSQI/ISI/ESS totals are different endpoints. Quarantined fulltext key 33157425: four-arm ARE/Ashwagandha plus melatonin actigraphy trial, not 97-person Shanghai PSG trial. |
| melatonin-primary-insomnia-sol / PMID 22346363 | DECLARED ABSENT | DIARY | Post hoc antihypertensive-treated subgroup, age >=55, pooled reports; not an independent new RCT |  |
| melatonin-primary-insomnia-sol / PMID 27559258 | DECLARED ABSENT | NOT_STATED | Cancer patients with insomnia, age 20-65; 50 randomized, 48 completed | Also documented study methods: QUESTIONNAIRE. AIS includes sleep induction but source says onset/maintenance were not stratified. No isolated numeric SOL result. |
| melatonin-primary-insomnia-sol / PMID 19584739 | DECLARED ABSENT | NOT_STATED | Full eligible trial, age >=55; N=40 | Also documented study methods: PSG, QUESTIONNAIRE. 9-minute SOL benefit is not explicitly bound to an instrument in the abstract. |
| melatonin-primary-insomnia-sol / PMID 18036082 | DECLARED ABSENT | NOT_STATED | Full eligible trial, age >=55; N=170; severity subgroup mentioned | Also documented study methods: QUESTIONNAIRE.  |
| melatonin-primary-insomnia-sol / PMID 17875243 | DECLARED ABSENT | NOT_STATED | Full eligible trial, age 55-80; randomized 177/177; completers 169/165 | Also documented study methods: QUESTIONNAIRE, DIARY. Abstract -24.3 versus -12.9 minutes, p=0.028: does not explicitly bind to PSQI versus diary/LSEQ. |
| melatonin-primary-insomnia-sol / PMID 12790159 | DECLARED ABSENT | NOT_STATED | Full crossover sample, N=10; age 30-72, mean 50; each receives placebo, 0.3 mg and 1 mg | Also documented study methods: PSG, DIARY. Held XML has no body/tables; no numeric EEG/log SOL result can be read. |
| semaglutide-obesity-weight / PMID 33625476 | SERVED NOT_STATED | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 | Served n uses overall FAS; matching mean/SD registry class has smaller observed n. |
| semaglutide-obesity-weight / PMID 33567185 | SERVED NOT_STATED | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 | Served n uses overall FAS; matching mean/SD registry class has smaller observed n. |
| semaglutide-obesity-weight / PMID 42070571 | DECLARED ABSENT | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 |  |
| semaglutide-obesity-weight / NCT07731256 | DECLARED ABSENT | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 |  |
| semaglutide-obesity-weight / NCT06390501 | DECLARED ABSENT | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 |  |
| semaglutide-obesity-weight / PMID 40825340 | DECLARED ABSENT | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 | Quarantined fulltext key 40825340: obesity pharmacotherapy review, not STEP 11. |
| semaglutide-obesity-weight / NCT05040971 | DECLARED ABSENT | NOT_STATED | in-trial / treatment-policy estimand (all randomized), baseline to Week 68 |  |

## Multiple classes and served NOT_STATED rows

- **Confirmed target multi-class trial:** PMID 20712869 / NCT00397189: DIARY and QUESTIONNAIRE (PSQI question 2 and component 2). Served class DIARY; the alternatives stay separate.
- **Dual methods, target numeric linkage absent:** PMID 12790159: EEG and sleep logs; PMID 19584739: PSG/EEG plus questionnaires; PMID 17875243: diary, PSQI and LSEQ. Their abstracts do not support assigning a numeric result to each instrument.
- **Served NOT_STATED:** PMID 33567185 (STEP 1) and PMID 33625476 (STEP 3). Both have body-weight values but no held ascertainment procedure. Their raw observed n also differs from served n.

## Static versus dynamic disclosure

| Component | Kind | Evidence |
|---|---|---|
| Membership and served values | dynamic read | Pinned git objects |
| Source values/quotes | dynamic read | Held files hashed against pinned blobs |
| Class adjudication | static source-based judgment | Explicit wording; unresolved is NOT_STATED |
| Counts | dynamic calculation | Membership plus adjudicated classes |

The named-result ledger transcribes source-labeled values and keeps original quotes. Those adjudications are static; registry enumeration, source hashes and census counts are calculated. No research outputs are simulated.

## All 32 review definitions

| Review | Continuous outcome |
|---|---|
| balanced-crystalloids-vs-saline-mortality | None declared in pinned review.json |
| colchicine-postop-af | None declared in pinned review.json |
| colchicine-recurrent-pericarditis | None declared in pinned review.json |
| colchicine-secondary-cv-prevention | None declared in pinned review.json |
| corticosteroids-cap-mortality | None declared in pinned review.json |
| corticosteroids-covid19-mortality | None declared in pinned review.json |
| dapagliflozin-hfpef-hosp | None declared in pinned review.json |
| denosumab-vertebral-fracture | None declared in pinned review.json |
| doac-vte-recurrence | None declared in pinned review.json |
| dpp4-mace-t2d | None declared in pinned review.json |
| empagliflozin-hfpef-hosp | None declared in pinned review.json |
| esketamine-trd-madrs | Observed-case Day-28 raw change-score MADRS MD |
| finerenone-ckd-t2d-renal | None declared in pinned review.json |
| glp1-ra-mace-t2d | None declared in pinned review.json |
| iv-iron-hfref-hosp | None declared in pinned review.json |
| melatonin-primary-insomnia-sol | Sleep-onset latency |
| metformin-pcos-ovulation | None declared in pinned review.json |
| noac-vs-warfarin-af-stroke | None declared in pinned review.json |
| omega3-cardiovascular-events | None declared in pinned review.json |
| pcsk9-mace | None declared in pinned review.json |
| probiotics-aad-prevention | None declared in pinned review.json |
| sacubitril-valsartan-hfref | None declared in pinned review.json |
| semaglutide-obesity-mace | None declared in pinned review.json |
| semaglutide-obesity-weight | Percent change in body weight |
| sglt2-ckd-progression | None declared in pinned review.json |
| sglt2-hfref-hosp-cvdeath | None declared in pinned review.json |
| sglt2-primary-prevention-hf | None declared in pinned review.json |
| spironolactone-hfref-mortality | None declared in pinned review.json |
| statins-primary-prevention-elderly | None declared in pinned review.json |
| ticagrelor-vs-clopidogrel-acs | None declared in pinned review.json |
| tocilizumab-covid19-mortality | None declared in pinned review.json |
| tranexamic-acid-pph | None declared in pinned review.json |

## Named numerical results

Every registry arm/category/model is listed. The text ledger adds raw, adjusted, baseline, endpoint, median/range and subgroup results; table headers and quotes define every column. Duplicated reporting is not independent evidence. Secondary depression scales and binary responders remain contextual, not MADRS results.

| Result | Trial | Class | Population / analysis / n | Named values |
|---|---|---|---|---|
| R0001 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28); Baseline up to end of the double-blind treatment phase (Day 28); Intranasal Esketamine + Oral Antidepressant (AD) | PMID 37025256 | OTHER | Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="109" | {"arm_mean_or_median": "-10.1", "dispersion": "10.80", "dispersion_type": "Standard Deviation"} Units on a Scale |
| R0002 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28); Baseline up to end of the double-blind treatment phase (Day 28); Intranasal Placebo + Oral AD | PMID 37025256 | OTHER | Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="106" | {"arm_mean_or_median": "-8.1", "dispersion": "10.26", "dispersion_type": "Standard Deviation"} Units on a Scale |
| R0003 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28); Baseline up to end of the double-blind treatment phase (Day 28); registry_analysis | PMID 37025256 | OTHER | Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-2.0", "ciLowerLimit": "-4.64", "ciUpperLimit": "0.55", "ciPctValue": "95", "pValue": "0.123"} Units on a Scale |
| R0004 Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2); Baseline (Day 1: predose) to 24 hours post first dose (Day 2); Intranasal Esketamine + Oral Antidepressant (AD) | PMID 37025256 | OTHER | Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="123" | {"arm_mean_or_median": "-8.0", "dispersion": "9.01", "dispersion_type": "Standard Deviation"} Units on a Scale |
| R0005 Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2); Baseline (Day 1: predose) to 24 hours post first dose (Day 2); Intranasal Placebo + Oral AD | PMID 37025256 | OTHER | Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="125" | {"arm_mean_or_median": "-4.4", "dispersion": "7.66", "dispersion_type": "Standard Deviation"} Units on a Scale |
| R0006 Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2); Baseline (Day 1: predose) to 24 hours post first dose (Day 2); registry_analysis | PMID 37025256 | OTHER | Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-3.3", "ciLowerLimit": "-5.33", "ciUpperLimit": "-1.33", "ciPctValue": "95"} Units on a Scale |
| R0007 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Esketamine (Esk) Plus Oral Antidepressant (AD) | PMID 31109201 | OTHER | Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="101" | {"arm_mean_or_median": "-21.4", "dispersion": "12.32", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0008 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Placebo Plus Oral AD | PMID 31109201 | OTHER | Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="100" | {"arm_mean_or_median": "-17.0", "dispersion": "13.88", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0009 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; registry_analysis | PMID 31109201 | OTHER | Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-4.0", "dispersionValue": "1.69", "ciLowerLimit": "-7.31", "ciUpperLimit": "-0.64", "ciPctValue": "95", "pValue": "=0.020"} Units on a scale |
| R0010 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline up to Endpoint (Double-blind Induction Phase [Day 28]); Intranasal Esketamine (Esk) Plus Oral Antidepressant (AD) | PMID 31109201 | OTHER | FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="112" | {"arm_mean_or_median": "-19.6", "dispersion": "13.58", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0011 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline up to Endpoint (Double-blind Induction Phase [Day 28]); Intranasal Placebo Plus Oral AD | PMID 31109201 | OTHER | FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="109" | {"arm_mean_or_median": "-16.3", "dispersion": "14.24", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0012 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline up to Endpoint (Double-blind Induction Phase [Day 28]); registry_analysis | PMID 31109201 | OTHER | FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-3.5", "ciLowerLimit": "-6.67", "ciUpperLimit": "-0.26", "ciPctValue": "95", "pValue": "=0.034"} Units on a scale |
| R0013 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Endpoint (Double-blind Induction Phase[Day 28]); Intranasal Esketamine Plus Oral Antidepressant (AD) | NCT02422186 | OTHER | The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; ; RAW_DESCRIPTIVE_ARM; n="63" | {"arm_mean_or_median": "-10.0", "dispersion": "12.74", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0014 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Endpoint (Double-blind Induction Phase[Day 28]); Oral AD Plus Intranasal Placebo | NCT02422186 | OTHER | The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; ; RAW_DESCRIPTIVE_ARM; n="60" | {"arm_mean_or_median": "-6.3", "dispersion": "8.86", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0015 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Endpoint (Double-blind Induction Phase[Day 28]); registry_analysis | NCT02422186 | OTHER | The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-3.6", "ciLowerLimit": "-7.20", "ciUpperLimit": "0.07", "ciPctValue": "95", "pValue": "=0.059"} Units on a scale |
| R0016 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline and Endpoint (Double-blind Induction Phase [Day 28]); Intranasal Esketamine Plus Oral Antidepressant (AD) | NCT02422186 | OTHER | The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; ; RAW_DESCRIPTIVE_ARM; n="71" | {"arm_mean_or_median": "-9.3", "dispersion": "12.28", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0017 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline and Endpoint (Double-blind Induction Phase [Day 28]); Oral AD Plus Intranasal Placebo | NCT02422186 | OTHER | The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; ; RAW_DESCRIPTIVE_ARM; n="64" | {"arm_mean_or_median": "-5.6", "dispersion": "9.11", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0018 Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline and Endpoint (Double-blind Induction Phase [Day 28]); registry_analysis | NCT02422186 | OTHER | The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-3.6", "ciLowerLimit": "-7.16", "ciUpperLimit": "-0.03", "ciPctValue": "95", "pValue": "=0.052"} Units on a scale |
| R0019 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Esketamine 56 mg Plus Oral Antidepressant | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="111" | {"arm_mean_or_median": "-19.0", "dispersion": "13.86", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0020 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Esketamine 84 mg Plus Oral AD | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="98" | {"arm_mean_or_median": "-18.8", "dispersion": "14.12", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0021 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Oral AD Plus Intranasal Placebo | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="108" | {"arm_mean_or_median": "-14.8", "dispersion": "15.07", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0022 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; registry_analysis | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-3.2", "ciLowerLimit": "-6.88", "ciUpperLimit": "0.45", "ciPctValue": "95", "pValue": "0.088"} Units on a scale |
| R0023 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; registry_analysis | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-4.1", "ciLowerLimit": "-7.67", "ciUpperLimit": "-0.49", "ciPctValue": "95"} Units on a scale |
| R0024 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); Intranasal Esketamine 56 mg Plus Oral Antidepressant | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="115" | {"arm_mean_or_median": "-18.3", "dispersion": "14.21", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0025 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); Intranasal Esketamine 84 mg Plus Oral AD | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="113" | {"arm_mean_or_median": "-17.4", "dispersion": "14.25", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0026 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); Oral AD Plus Intranasal Placebo | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="113" | {"arm_mean_or_median": "-14.3", "dispersion": "15.00", "dispersion_type": "Standard Deviation"} Units on a scale |
| R0027 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); registry_analysis | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-2.0", "ciLowerLimit": "-5.52", "ciUpperLimit": "1.42", "ciPctValue": "95", "pValue": "= 0.250"} Units on a scale |
| R0028 Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); registry_analysis | NCT02417064 | OTHER | Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-4.1", "ciLowerLimit": "-7.53", "ciUpperLimit": "-0.6", "ciPctValue": "95"} Units on a scale |
| R0029 Combined-dose verified arm derivation; ; verified_input | NCT02417064 | OTHER | full analysis set (FAS/mITT); DERIVED_COMBINED_ARMS; n={"nc1": 209, "nc2": 108} | {"mean1": -18.91, "sd1": 13.95, "nc1": 209, "mean2": -14.8, "sd2": 15.07, "nc2": 108} MADRS points |
| R0030 The Change From Baseline in Subjective Sleep Latency.; Baseline and 3 weeks; Circadin | PMID 20712869 | DIARY | Pre-planned analysis on ITT population age 65-80; ; ; RAW_DESCRIPTIVE_ARM; n="137" | {"arm_mean_or_median": "-19.1", "dispersion": "47.3", "dispersion_type": "Standard Deviation"} minutes |
| R0031 The Change From Baseline in Subjective Sleep Latency.; Baseline and 3 weeks; Placebo | PMID 20712869 | DIARY | Pre-planned analysis on ITT population age 65-80; ; ; RAW_DESCRIPTIVE_ARM; n="144" | {"arm_mean_or_median": "-1.7", "dispersion": "47.8", "dispersion_type": "Standard Deviation"} minutes |
| R0032 The Change From Baseline in Subjective Sleep Latency.; Baseline and 3 weeks; registry_analysis | PMID 20712869 | DIARY | Pre-planned analysis on ITT population age 65-80; The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-15.6", "dispersionValue": "47", "ciLowerLimit": "-25.3", "ciUpperLimit": "-6", "ciPctValue": "95", "pValue": "<0.05"} minutes |
| R0033 Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33625476 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; ; RAW_DESCRIPTIVE_ARM; n="373" | {"arm_mean_or_median": "-16.5", "dispersion": "10.1", "dispersion_type": "Standard Deviation"} Percentage |
| R0034 Change in Body Weight (%); Baseline (week 0) to week 68; Placebo | PMID 33625476 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; ; RAW_DESCRIPTIVE_ARM; n="189" | {"arm_mean_or_median": "-5.8", "dispersion": "7.7", "dispersion_type": "Standard Deviation"} Percentage |
| R0035 Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33625476 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; ; RAW_DESCRIPTIVE_ARM; n="334" | {"arm_mean_or_median": "-17.6", "dispersion": "9.6", "dispersion_type": "Standard Deviation"} Percentage |
| R0036 Change in Body Weight (%); Baseline (week 0) to week 68; Placebo | PMID 33625476 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; ; RAW_DESCRIPTIVE_ARM; n="164" | {"arm_mean_or_median": "-6.1", "dispersion": "7.6", "dispersion_type": "Standard Deviation"} Percentage |
| R0037 Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis | PMID 33625476 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Treatment policy estimand; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-10.27", "ciLowerLimit": "-11.97", "ciUpperLimit": "-8.57", "ciPctValue": "95", "pValue": "<.0001"} Percentage |
| R0038 Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis | PMID 33625476 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Hypothetical estimand; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-12.67", "ciLowerLimit": "-14.34", "ciUpperLimit": "-11.00", "ciPctValue": "95", "pValue": "<0.0001"} Percentage |
| R0039 Change in Body Weight (Kg); Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33625476 | NOT_STATED | FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="373" | {"arm_mean_or_median": "-17.5", "dispersion": "11.4", "dispersion_type": "Standard Deviation"} Kilogram (kg) |
| R0040 Change in Body Weight (Kg); Baseline (week 0) to week 68; Placebo | PMID 33625476 | NOT_STATED | FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="189" | {"arm_mean_or_median": "-6.2", "dispersion": "8.6", "dispersion_type": "Standard Deviation"} Kilogram (kg) |
| R0041 Change in Body Weight; Baseline (week 0) to week 8; Semaglutide 2.4 mg | PMID 33625476 | NOT_STATED | FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="396" | {"arm_mean_or_median": "-7.8", "dispersion": "3.1", "dispersion_type": "Standard Deviation"} Percentage |
| R0042 Change in Body Weight; Baseline (week 0) to week 8; Placebo | PMID 33625476 | NOT_STATED | FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="197" | {"arm_mean_or_median": "-6.0", "dispersion": "3.6", "dispersion_type": "Standard Deviation"} Percentage |
| R0043 Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33567185 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; ; RAW_DESCRIPTIVE_ARM; n="1212" | {"arm_mean_or_median": "-15.6", "dispersion": "10.1", "dispersion_type": "Standard Deviation"} Percentage point |
| R0044 Change in Body Weight (%); Baseline (week 0) to week 68; Placebo | PMID 33567185 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; ; RAW_DESCRIPTIVE_ARM; n="577" | {"arm_mean_or_median": "-2.8", "dispersion": "6.5", "dispersion_type": "Standard Deviation"} Percentage point |
| R0045 Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33567185 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; ; RAW_DESCRIPTIVE_ARM; n="1059" | {"arm_mean_or_median": "-16.9", "dispersion": "9.4", "dispersion_type": "Standard Deviation"} Percentage point |
| R0046 Change in Body Weight (%); Baseline (week 0) to week 68; Placebo | PMID 33567185 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; ; RAW_DESCRIPTIVE_ARM; n="499" | {"arm_mean_or_median": "-3.1", "dispersion": "6.4", "dispersion_type": "Standard Deviation"} Percentage point |
| R0047 Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis | PMID 33567185 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Treatment policy estimand; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-12.44", "ciLowerLimit": "-13.37", "ciUpperLimit": "-11.51", "ciPctValue": "95", "pValue": "<.0001"} Percentage point |
| R0048 Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis | PMID 33567185 | NOT_STATED | Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Hypothetical estimand; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-14.42", "ciLowerLimit": "-15.29", "ciUpperLimit": "-13.55", "ciPctValue": "95", "pValue": "<0.0001"} Percentage point |
| R0049 Change in Body Weight (kg); Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33567185 | NOT_STATED | FAS included all randomized participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="1212" | {"arm_mean_or_median": "-16.1", "dispersion": "10.6", "dispersion_type": "Standard Deviation"} Kilogram (kg) |
| R0050 Change in Body Weight (kg); Baseline (week 0) to week 68; Placebo | PMID 33567185 | NOT_STATED | FAS included all randomized participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="577" | {"arm_mean_or_median": "-2.9", "dispersion": "7.2", "dispersion_type": "Standard Deviation"} Kilogram (kg) |
| R0051 Change in Body Weight (%) - DEXA Subpopulation; Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33567185 | NOT_STATED | DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="89" | {"arm_mean_or_median": "-15.8", "dispersion": "11.1", "dispersion_type": "Standard Deviation"} Percentage point |
| R0052 Change in Body Weight (%) - DEXA Subpopulation; Baseline (week 0) to week 68; Placebo | PMID 33567185 | NOT_STATED | DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="42" | {"arm_mean_or_median": "-3.4", "dispersion": "6.1", "dispersion_type": "Standard Deviation"} Percentage point |
| R0053 Change in Body Weight (kg) - DEXA Subpopulation; Baseline (week 0) to week 68; Semaglutide 2.4 mg | PMID 33567185 | NOT_STATED | DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="89" | {"arm_mean_or_median": "-15.5", "dispersion": "11.4", "dispersion_type": "Standard Deviation"} Kilograms |
| R0054 Change in Body Weight (kg) - DEXA Subpopulation; Baseline (week 0) to week 68; Placebo | PMID 33567185 | NOT_STATED | DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="42" | {"arm_mean_or_median": "-3.2", "dispersion": "6.1", "dispersion_type": "Standard Deviation"} Kilograms |
| R0055 Change in Body Weight (%) : In-trial Observation Period; Baseline (week 0), end of treatment (week 44); Semaglutide | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="100" | {"arm_mean_or_median": "-16.4", "dispersion": "7.3", "dispersion_type": "Standard Deviation"} Percentage of body weight |
| R0056 Change in Body Weight (%) : In-trial Observation Period; Baseline (week 0), end of treatment (week 44); Placebo | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="48" | {"arm_mean_or_median": "-2.6", "dispersion": "5.8", "dispersion_type": "Standard Deviation"} Percentage of body weight |
| R0057 Change in Body Weight (%) : In-trial Observation Period; Baseline (week 0), end of treatment (week 44); registry_analysis | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-12.99", "ciLowerLimit": "-15.28", "ciUpperLimit": "-10.70", "ciPctValue": "95", "pValue": "<0.0001"} Percentage of body weight |
| R0058 Change in Body Weight (%) : On-treatment Observation Period; Baseline (week 0), end of treatment (week 44); Semaglutide | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="96" | {"arm_mean_or_median": "-16.4", "dispersion": "7.4", "dispersion_type": "Standard Deviation"} Percentage of body weight |
| R0059 Change in Body Weight (%) : On-treatment Observation Period; Baseline (week 0), end of treatment (week 44); Placebo | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="47" | {"arm_mean_or_median": "-2.7", "dispersion": "5.8", "dispersion_type": "Standard Deviation"} Percentage of body weight |
| R0060 Change in Body Weight (%) : On-treatment Observation Period; Baseline (week 0), end of treatment (week 44); registry_analysis | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-13.40", "ciLowerLimit": "-15.70", "ciUpperLimit": "-11.11", "ciPctValue": "95", "pValue": "<0.0001"} Percentage of body weight |
| R0061 Change in Body Weight (kg); Baseline (week 0), end of treatment (week 44); Semaglutide | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="100" | {"arm_mean_or_median": "-13.0", "dispersion": "5.5", "dispersion_type": "Standard Deviation"} Kg |
| R0062 Change in Body Weight (kg); Baseline (week 0), end of treatment (week 44); Placebo | PMID 40825340 | NOT_STATED | FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; ; RAW_DESCRIPTIVE_ARM; n="48" | {"arm_mean_or_median": "-2.0", "dispersion": "5.1", "dispersion_type": "Standard Deviation"} Kg |
| R0063 Change in Body Weight (Percentage [%]); From randomisation (week 0) to end of treatment (week 52); Semaglutide 2.4 mg | NCT05040971 | NOT_STATED | Full analysis set (FAS) included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="129" | {"arm_mean_or_median": "-14.4", "dispersion": "7.9", "dispersion_type": "Standard Deviation"} Percentage (%) of body weight |
| R0064 Change in Body Weight (Percentage [%]); From randomisation (week 0) to end of treatment (week 52); Placebo | NCT05040971 | NOT_STATED | Full analysis set (FAS) included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="66" | {"arm_mean_or_median": "-2.7", "dispersion": "4.3", "dispersion_type": "Standard Deviation"} Percentage (%) of body weight |
| R0065 Change in Body Weight (Percentage [%]); From randomisation (week 0) to end of treatment (week 52); registry_analysis | NCT05040971 | NOT_STATED | Full analysis set (FAS) included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; Treatment policy estimand; ADJUSTED_MODEL; n="NOT_SEPARATELY_STATED; measure denominator is not automatically model n" | {"paramValue": "-11.19", "ciLowerLimit": "-12.97", "ciUpperLimit": "-9.42", "ciPctValue": "95", "pValue": "<0.0001"} Percentage (%) of body weight |
| R0066 Change in Body Weight (Kilogram [Kg]); From randomisation (week 0) to week 52; Semaglutide 2.4 mg | NCT05040971 | NOT_STATED | FAS included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="129" | {"arm_mean_or_median": "-15.8", "dispersion": "9.3", "dispersion_type": "Standard Deviation"} kilogram (Kg) |
| R0067 Change in Body Weight (Kilogram [Kg]); From randomisation (week 0) to week 52; Placebo | NCT05040971 | NOT_STATED | FAS included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; ; RAW_DESCRIPTIVE_ARM; n="66" | {"arm_mean_or_median": "-2.8", "dispersion": "5.0", "dispersion_type": "Standard Deviation"} kilogram (Kg) |
| R0068 Baseline diary SOL | PMID 20712869 | DIARY | Low excretors (6-SMT <=8 microg/night), age 18-80; RAW; n=[86, 86] | {"PRM_mean": 74.1, "PRM_SD": 54.9, "placebo_mean": 75.5, "placebo_SD": 58.5} minutes |
| R0069 Week 3 absolute diary SOL | PMID 20712869 | DIARY | Low excretors (6-SMT <=8 microg/night), age 18-80; RAW; n=[86, 86] | {"PRM_mean": 65.1, "PRM_SD": 59.9, "placebo_mean": 66.5, "placebo_SD": 51.6} minutes |
| R0070 Week 3 change diary SOL | PMID 20712869 | DIARY | Low excretors (6-SMT <=8 microg/night), age 18-80; RAW; n=[86, 86] | {"PRM_mean": -9, "PRM_SD": 50.5, "placebo_mean": -9, "placebo_SD": 48.7} minutes |
| R0071 Week 3 adjusted diary SOL contrast | PMID 20712869 | DIARY | Low excretors (6-SMT <=8 microg/night), age 18-80; ADJUSTED linear regression: baseline; age group only for low excretors; n=[86, 86] | {"MD": -0.6, "CI95_low": -14, "CI95_high": 12.7, "p": 0.924} minutes |
| R0072 Baseline diary SOL | PMID 20712869 | DIARY | Age 65-80 regardless of melatonin excretion; RAW; n=[137, 144] | {"PRM_mean": 76.7, "PRM_SD": 63.7, "placebo_mean": 72.5, "placebo_SD": 51.4} minutes |
| R0073 Week 3 absolute diary SOL | PMID 20712869 | DIARY | Age 65-80 regardless of melatonin excretion; RAW; n=[137, 144] | {"PRM_mean": 57.6, "PRM_SD": 51.8, "placebo_mean": 70.9, "placebo_SD": 54} minutes |
| R0074 Week 3 change diary SOL | PMID 20712869 | DIARY | Age 65-80 regardless of melatonin excretion; RAW; n=[137, 144] | {"PRM_mean": -19.1, "PRM_SD": 47.3, "placebo_mean": -1.7, "placebo_SD": 47.8} minutes |
| R0075 Week 3 adjusted diary SOL contrast | PMID 20712869 | DIARY | Age 65-80 regardless of melatonin excretion; ADJUSTED linear regression: baseline; age group only for low excretors; n=[137, 144] | {"MD": -15.6, "CI95_low": -25.3, "CI95_high": -6, "p": 0.002} minutes |
| R0076 Visit 7 diary change | PMID 20712869 | DIARY | Low excretors age 18-80; RAW; n={"N_MAX_PRM": 99, "N_MAX_placebo": 31, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -23.6, "PRM_SD": 42.1, "placebo_mean": -19.4, "placebo_SD": 79.5} minutes |
| R0077 26-week global diary effect | PMID 20712869 | DIARY | Low excretors age 18-80; ADJUSTED MMRM over visits 3-7, not a single Visit 7 contrast; n="NOT_STATED model-specific n" | {"MD": -6.7, "CI95_low": -16.4, "CI95_high": 3.0, "p": 0.174} minutes |
| R0078 Visit 7 diary change | PMID 20712869 | DIARY | Age 65-80; RAW; n={"N_MAX_PRM": 159, "N_MAX_placebo": 61, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -25.9, "PRM_SD": 46.4, "placebo_mean": -8.3, "placebo_SD": 61.5} minutes |
| R0079 26-week global diary effect | PMID 20712869 | DIARY | Age 65-80; ADJUSTED MMRM over visits 3-7, not a single Visit 7 contrast; n="NOT_STATED model-specific n" | {"MD": -14.5, "CI95_low": -21.4, "CI95_high": -7.7, "p": "<0.001"} minutes |
| R0080 PSQI component 2 Visit 3 change | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; RAW; n={"N_MAX_PRM": 86, "N_MAX_placebo": 86, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -0.37, "PRM_SD": 0.72, "placebo_mean": -0.26, "placebo_SD": 0.71} ordinal component points |
| R0081 PSQI component 2 Visit 7 change | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; RAW; n={"N_MAX_PRM": 101, "N_MAX_placebo": 31, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -0.9, "PRM_SD": 1.02, "placebo_mean": -0.68, "placebo_SD": 0.79} ordinal component points |
| R0082 PSQI component 2 Short term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; ADJUSTED linear regression adjusted for baseline and age; n="NOT_STATED model-specific n" | {"MD": -0.12, "CI95_low": -0.33, "CI95_high": 0.1, "p": 0.278} ordinal component points |
| R0083 PSQI component 2 Long term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; ADJUSTED MMRM global treatment effect adjusted for baseline, age and visit; n="NOT_STATED model-specific n" | {"MD": -0.17, "CI95_low": -0.36, "CI95_high": 0.02, "p": 0.08} ordinal component points |
| R0084 PSQI question 2 Visit 3 change | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; RAW; n={"N_MAX_PRM": 86, "N_MAX_placebo": 86, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -18.3, "PRM_SD": 52.4, "placebo_mean": -18.5, "placebo_SD": 51.7} minutes |
| R0085 PSQI question 2 Visit 7 change | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; RAW; n={"N_MAX_PRM": 101, "N_MAX_placebo": 31, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -41.3, "PRM_SD": 59, "placebo_mean": -33.1, "placebo_SD": 92.2} minutes |
| R0086 PSQI question 2 Short term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; ADJUSTED linear regression adjusted for baseline and age; n="NOT_STATED model-specific n" | {"MD": -0.2, "CI95_low": -13.2, "CI95_high": 12.8, "p": 0.98} minutes |
| R0087 PSQI question 2 Long term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Low excretors age 18-80; ADJUSTED MMRM global treatment effect adjusted for baseline, age and visit; n="NOT_STATED model-specific n" | {"MD": -11.6, "CI95_low": -22, "CI95_high": -1.1, "p": 0.03} minutes |
| R0088 PSQI component 2 Visit 3 change | PMID 20712869 | QUESTIONNAIRE | Age 65-80; RAW; n={"N_MAX_PRM": 136, "N_MAX_placebo": 144, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -0.43, "PRM_SD": 0.87, "placebo_mean": -0.22, "placebo_SD": 0.74} ordinal component points |
| R0089 PSQI component 2 Visit 7 change | PMID 20712869 | QUESTIONNAIRE | Age 65-80; RAW; n={"N_MAX_PRM": 164, "N_MAX_placebo": 62, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -0.75, "PRM_SD": 0.99, "placebo_mean": -0.52, "placebo_SD": 0.95} ordinal component points |
| R0090 PSQI component 2 Short term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Age 65-80; ADJUSTED linear regression adjusted for baseline and age; n="NOT_STATED model-specific n" | {"MD": -0.23, "CI95_low": -0.41, "CI95_high": -0.04, "p": 0.018} ordinal component points |
| R0091 PSQI component 2 Long term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Age 65-80; ADJUSTED MMRM global treatment effect adjusted for baseline, age and visit; n="NOT_STATED model-specific n" | {"MD": -0.24, "CI95_low": -0.38, "CI95_high": -0.1, "p": 0.001} ordinal component points |
| R0092 PSQI question 2 Visit 3 change | PMID 20712869 | QUESTIONNAIRE | Age 65-80; RAW; n={"N_MAX_PRM": 136, "N_MAX_placebo": 144, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -25.4, "PRM_SD": 50.9, "placebo_mean": -8.9, "placebo_SD": 48} minutes |
| R0093 PSQI question 2 Visit 7 change | PMID 20712869 | QUESTIONNAIRE | Age 65-80; RAW; n={"N_MAX_PRM": 164, "N_MAX_placebo": 62, "outcome_specific_n": "NOT_STATED"} | {"PRM_mean": -32.7, "PRM_SD": 49.3, "placebo_mean": -19, "placebo_SD": 65.8} minutes |
| R0094 PSQI question 2 Short term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Age 65-80; ADJUSTED linear regression adjusted for baseline and age; n="NOT_STATED model-specific n" | {"MD": -13.7, "CI95_low": -23.5, "CI95_high": -3.9, "p": 0.006} minutes |
| R0095 PSQI question 2 Long term adjusted contrast | PMID 20712869 | QUESTIONNAIRE | Age 65-80; ADJUSTED MMRM global treatment effect adjusted for baseline, age and visit; n="NOT_STATED model-specific n" | {"MD": -12.1, "CI95_low": -19.1, "CI95_high": -5.1, "p": 0.001} minutes |
| R0096 Linked PMID 21091391, week-3 diary changes | PMID 20712869 | DIARY | Age 55-80 subgroup of NCT00397189; Raw/adjusted arm-change status NOT_STATED in abstract; n="NOT_STATED for this subgroup" | {"PRM_change": -15.4, "placebo_change": -5.5, "p": 0.014} minutes |
| R0097 Week-3 latency change | PMID 17875243 | NOT_STATED | Age 55-80 full eligible trial; NOT_STATED; n={"randomized": {"PRM": 177, "placebo": 177}, "outcome_n": "NOT_STATED"} | {"PRM_change": -24.3, "placebo_change": -12.9, "p": 0.028} minutes |
| R0098 Shorter sleep-onset latency | PMID 19584739 | NOT_STATED | Age >=55 full eligible trial; NOT_STATED; n={"trial_N": 40, "arm_or_analysis_n": "NOT_STATED"} | {"reported_benefit_minutes": 9, "p": 0.02} minutes |
| R0099 Diary Baseline | PMID 22346363 | DIARY | Antihypertensive-treated, age >=55 subgroup; RAW; n=[134, 39] | {"PRM_mean": 73.6, "PRM_SD_as_labelled": 5.6, "placebo_mean": 73.5, "placebo_SD_as_labelled": 4.3} minutes |
| R0100 Diary 6 months | PMID 22346363 | DIARY | Antihypertensive-treated, age >=55 subgroup; RAW; n=[121, 36] | {"PRM_mean": 51, "PRM_SD_as_labelled": 3.6, "placebo_mean": 65.2, "placebo_SD_as_labelled": 4.4} minutes |
| R0101 Diary Change from baseline | PMID 22346363 | DIARY | Antihypertensive-treated, age >=55 subgroup; RAW; n=[121, 36] | {"PRM_mean": -23.3, "PRM_SD_as_labelled": 2.9, "placebo_mean": -7.5, "placebo_SD_as_labelled": 3.6} minutes |
| R0102 Narrative six-month decreases and standardized effect | PMID 22346363 | DIARY | Antihypertensive-treated, age >=55; ANCOVA named; adjustment status of the two reported decreases NOT_STATED; n="NOT_STATED for narrative estimates" | {"PRM_decrease": 25.89, "placebo_decrease": 7.54, "df": 1, "F": 8.74, "p": 0.02, "Cohen_d": 0.39} minutes |
| R0103 Baseline Mean (SD) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["124", "126"] | {"column_1": "36.5 (5.21)", "column_2": "35.9 (4.50)"} MADRS points |
| R0104 Baseline Median (range) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["124", "126"] | {"column_1": "36.0 (25, 50)", "column_2": "36.0 (27, 48)"} MADRS points |
| R0105 Day 28 Mean (SD) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["109", "106"] | {"column_1": "26.5 (10.33)", "column_2": "27.9 (10.04)"} MADRS points |
| R0106 Day 28 Median (range) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["109", "106"] | {"column_1": "28.0 (0, 43)", "column_2": "30.0 (0, 44)"} MADRS points |
| R0107 Change from baseline to Day 28 Mean (SD) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["109", "106"] | {"column_1": "−10.1 (10.80)", "column_2": "−8.1 (10.26)"} MADRS points |
| R0108 Change from baseline to Day 28 Median (range) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["109", "106"] | {"column_1": "−7.0 (−42, 10)", "column_2": "−6.0 (−38, 8)"} MADRS points |
| R0109 Change from baseline to Day 28 Difference of LS means (SE) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; ADJUSTED MMRM; n=["109", "106"] | {"column_1": "−2.0 (1.32)"} MADRS points |
| R0110 Change from baseline to Day 28 95% CI on difference | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; ADJUSTED MMRM; n=["109", "106"] | {"column_1": "−4.64, 0.55"} MADRS points |
| R0111 Change from baseline to Day 28 2-sided p-value | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; ADJUSTED MMRM; n=["109", "106"] | {"column_1": "0.123"} MADRS points |
| R0112 Baseline Mean (SD) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["124", "126"] | {"column_1": "36.5 (5.21)", "column_2": "35.9 (4.50)"} MADRS points |
| R0113 Baseline Median (range) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["124", "126"] | {"column_1": "36.0 (25, 50)", "column_2": "36.0 (27, 48)"} MADRS points |
| R0114 Day 2 (24 hours) Mean (SD) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["123", "125"] | {"column_1": "28.5 (9.39)", "column_2": "31.5 (8.30)"} MADRS points |
| R0115 Day 2 (24 hours) Median (range) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["123", "125"] | {"column_1": "30.0 (0, 47)", "column_2": "33.0 (1, 49)"} MADRS points |
| R0116 Change from baseline to Day 2 (24 hours) Mean (SD) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["123", "125"] | {"column_1": "−8.0 (9.01)", "column_2": "−4.4 (7.66)"} MADRS points |
| R0117 Change from baseline to Day 2 (24 hours) Median (range) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; RAW; n=["123", "125"] | {"column_1": "−6.0 (−38, 13)", "column_2": "−3.0 (−31, 12)"} MADRS points |
| R0118 Change from baseline to Day 2 (24 hours) Difference of LS means (SE) | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; ADJUSTED MMRM; n=["123", "125"] | {"column_1": "−3.3 (1.02)"} MADRS points |
| R0119 Change from baseline to Day 2 (24 hours) 95% CI on difference | PMID 37025256 | OTHER | Full eligible FAS; China/USA trial; ADJUSTED MMRM; n=["123", "125"] | {"column_1": "−5.33, −1.33"} MADRS points |
| R0120 35441931 Table 2 Baseline Baseline | PMID 31109201 | OTHER | TRANSFORM-2 full eligible; observed n at each timepoint; RAW arm values; mean difference from reported ANOVA; n={"placebo": "109", "esketamine": "114"} | {"column_1": "109", "column_2": "37.3 (5.66)", "column_3": "114", "column_4": "37.0 (5.69)", "column_5": "", "column_6": "", "column_7": "", "column_8": "", "column_9": ""} MADRS points |
| R0121 35441931 Table 2 Baseline Day 15 | PMID 31109201 | OTHER | TRANSFORM-2 full eligible; observed n at each timepoint; RAW arm values; mean difference from reported ANOVA; n={"placebo": "102", "esketamine": "107"} | {"column_1": "102", "column_2": "27.2 (11.37)", "column_3": "107", "column_4": "24.8 (10.06)", "column_5": "− 10.0 (11.63)", "column_6": "− 12.1 (10.58)", "column_7": "− 2.0 (1.54)", "column_8": "− 5.06 to 1.00", "column_9": "0.189"} MADRS points |
| R0122 35441931 Table 2 Baseline Day 28 | PMID 31109201 | OTHER | TRANSFORM-2 full eligible; observed n at each timepoint; RAW arm values; mean difference from reported ANOVA; n={"placebo": "100", "esketamine": "101"} | {"column_1": "100", "column_2": "20.6 (12.70)", "column_3": "101", "column_4": "15.5 (10.67)", "column_5": "− 17.0 (13.88)", "column_6": "− 21.4 (12.32)", "column_7": "− 4.4 (1.85)", "column_8": "− 8.10 to − 0.80", "column_9": "0.017"} MADRS points |
| R0123 34973081 Table 4 Baseline Mean (SD) | NCT02417064 / PMID 31109201 / NCT02422186 | OTHER | Separate sex groups; TRANSFORM-1/2 pooled (never split) and TRANSFORM-3 separately; RAW or unadjusted comparison; see source method; n=["235", "144", "108", "78", "45", "40", "27", "25"] | {"column_1": "37.7 (5.49)", "column_2": "37.7 (6.11)", "column_3": "36.9 (5.02)", "column_4": "36.7 (5.50)", "column_5": "35.7 (5.90)", "column_6": "34.5 (6.97)", "column_7": "35.2 (6.04)", "column_8": "35.1 (5.60)"} MADRS points |
| R0124 34973081 Table 4 Change to day 28 Mean (SD) | NCT02417064 / PMID 31109201 / NCT02422186 | OTHER | Separate sex groups; TRANSFORM-1/2 pooled (never split) and TRANSFORM-3 separately; RAW or unadjusted comparison; see source method; n=["215", "138", "95", "70", "39", "36", "24", "24"] | {"column_1": "-20.3 (13.19)", "column_2": "-15.8 (14.67)", "column_3": "-18.3 (14.08)", "column_4": "-16.0 (14.30)", "column_5": "-9.9 (13.34)", "column_6": "-6.9 (9.65)", "column_7": "-10.3 (11.96)", "column_8": "-5.5 (7.64)"} MADRS points |
| R0125 34973081 Table 4 MMRM analysis a Diff. of LS means b (SE) | NCT02417064 / PMID 31109201 / NCT02422186 | OTHER | Separate sex groups; TRANSFORM-1/2 pooled (never split) and TRANSFORM-3 separately; ADJUSTED model; n=["215", "138", "95", "70", "39", "36", "24", "24"] | {"column_1": "-4.5 (1.41)", "column_2": "", "column_3": "-1.6 (2.04)", "column_4": "", "column_5": "-3.4 (2.41)", "column_6": "", "column_7": "-5.0 (3.05)", "column_8": ""} MADRS points |
| R0126 34973081 Table 4 MMRM analysis a 95% CI on difference | NCT02417064 / PMID 31109201 / NCT02422186 | OTHER | Separate sex groups; TRANSFORM-1/2 pooled (never split) and TRANSFORM-3 separately; ADJUSTED model; n=["215", "138", "95", "70", "39", "36", "24", "24"] | {"column_1": "-7.26, − 1.70", "column_2": "", "column_3": "-5.60, 2.41", "column_4": "", "column_5": "-8.14, 1.41", "column_6": "", "column_7": "-11.05, 1.03", "column_8": ""} MADRS points |
| R0127 34293233 Table 2 Baseline Mean (SD) | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; RAW or unadjusted comparison; see source method; n=["83", "79", "31", "30"] | {"column_1": "37.4 (5.42)", "column_2": "38.5 (5.48)", "column_3": "36.0 (6.33)", "column_4": "34.1 (4.92)"} MADRS points |
| R0128 34293233 Table 2 Change from baseline to day 28 Mean (SD) | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; RAW or unadjusted comparison; see source method; n=["72", "72", "29", "28"] | {"column_1": "−21.0 (12.51)", "column_2": "−18.3 (13.99)", "column_3": "−22.7 (11.98)", "column_4": "−13.6 (13.25)"} MADRS points |
| R0129 34293233 Table 2 Change from baseline to day 28 p value based on pared t‐test | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; RAW or unadjusted comparison; see source method; n=["72", "72", "29", "28"] | {"column_1": "< .001", "column_2": "< .001", "column_3": "< .001", "column_4": "< .001"} MADRS points |
| R0130 34293233 Table 2 ANCOVA analysis a of treatment groups within same status of comorbid anxiety Difference of LS means b (SE) | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; ADJUSTED model; n=["72", "72", "29", "28"] | {"column_1": "−4.2 (1.97)", "column_2": "", "column_3": "−7.5 (3.12)", "column_4": ""} MADRS points |
| R0131 34293233 Table 2 ANCOVA analysis a of treatment groups within same status of comorbid anxiety 95% CI on difference | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; ADJUSTED model; n=["72", "72", "29", "28"] | {"column_1": "−8.1 to −0.3", "column_2": "", "column_3": "−13.7 to − 1.3", "column_4": ""} MADRS points |
| R0132 34293233 Table 2 ANCOVA analysis a of treatment groups within same status of comorbid anxiety p value on difference | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; ADJUSTED model; n=["72", "72", "29", "28"] | {"column_1": ".036", "column_2": "", "column_3": ".017", "column_4": ""} MADRS points |
| R0133 34293233 Table 2 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no Difference of LS means d (SE) | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; ADJUSTED model; n=["72", "72", "29", "28"] | {"column_1": "", "column_2": "", "column_3": "", "column_4": "3.3 (3.71)"} MADRS points |
| R0134 34293233 Table 2 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no 95% CI on difference | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; ADJUSTED model; n=["72", "72", "29", "28"] | {"column_1": "", "column_2": "", "column_3": "", "column_4": "−4.0 to 10.6"} MADRS points |
| R0135 34293233 Table 2 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no p value | PMID 31109201 | OTHER | TRANSFORM-2 comorbid anxiety vs no comorbid anxiety; ADJUSTED model; n=["72", "72", "29", "28"] | {"column_1": "", "column_2": "", "column_3": "", "column_4": ".371"} MADRS points |
| R0136 32367114 Table 2  Day 2 | NCT02417064 / PMID 31109201 | OTHER | TRANSFORM-1/2 pooled genotype subset; additive minor allele effect, not randomized treatment effect; ADJUSTED additive genotype regression; not a treatment contrast; n="NOT_STATED" | {"column_1": "0.13", "column_2": "229", "column_3": "−0.63", "column_4": ".69", "column_5": "<0.5 %", "column_6": "None", "column_7": "169", "column_8": "−6.59", "column_9": "<.001", "column_10": "10%", "column_11": "Greater response"} MADRS points |
| R0137 32367114 Table 2  Day 28 | NCT02417064 / PMID 31109201 | OTHER | TRANSFORM-1/2 pooled genotype subset; additive minor allele effect, not randomized treatment effect; ADJUSTED additive genotype regression; not a treatment contrast; n="NOT_STATED" | {"column_1": "0.13", "column_2": "232", "column_3": "−1.81", "column_4": ".34", "column_5": "<0.5 %", "column_6": "None", "column_7": "172", "column_8": "−4.30", "column_9": ".07", "column_10": "2%", "column_11": "None"} MADRS points |
| R0138 Day-28 adjusted MADRS contrast | NCT02422186 | OTHER | Full age >=65; ADJUSTED; full primary median-unbiased weighted-combination interval, subgroup adjusted; n="NOT_STATED in abstract" | {"MD": -3.6, "CI95_low": -7.2, "CI95_high": 0.07, "p": 0.059} MADRS points |
| R0139 Day-28 adjusted MADRS contrast | NCT02422186 | OTHER | Age 65-74; ADJUSTED; full primary median-unbiased weighted-combination interval, subgroup adjusted; n="NOT_STATED in abstract" | {"MD": -4.9, "CI95_low": -8.96, "CI95_high": -0.89, "p": 0.017} MADRS points |
| R0140 Day-28 adjusted MADRS contrast | NCT02422186 | OTHER | Age >=75; ADJUSTED; full primary median-unbiased weighted-combination interval, subgroup adjusted; n="NOT_STATED in abstract" | {"MD": -0.4, "CI95_low": -10.38, "CI95_high": 9.5, "p": 0.93} MADRS points |
| R0141 Day-28 adjusted MADRS contrast | NCT02422186 | OTHER | Depression onset <55; ADJUSTED; full primary median-unbiased weighted-combination interval, subgroup adjusted; n="NOT_STATED in abstract" | {"MD": -6.1, "CI95_low": -10.33, "CI95_high": -1.81, "p": 0.006} MADRS points |
| R0142 Day-28 adjusted MADRS contrast | NCT02422186 | OTHER | Depression onset >=55; ADJUSTED; full primary median-unbiased weighted-combination interval, subgroup adjusted; n="NOT_STATED in abstract" | {"MD": 3.1, "CI95_low": -4.51, "CI95_high": 10.8, "p": 0.407} MADRS points |
| R0143 Genotype-specific raw MADRS changes esketamine | NCT02417064 / PMID 31109201 | OTHER | Pooled TRANSFORM-1/2 AA versus AG/GG, days 2 and 28; RAW mean (SD); n="Outcome-specific genotype n NOT_STATED in narrative; baseline n is not substituted" | {"day2_AA": [-9.62, 10.14], "day2_AG_GG": [-10.49, 10.79], "day28_AA": [-20.95, 12.75], "day28_AG_GG": [-23.16, 13.53]} MADRS points |
| R0144 Genotype-specific raw MADRS changes placebo | NCT02417064 / PMID 31109201 | OTHER | Pooled TRANSFORM-1/2 AA versus AG/GG, days 2 and 28; RAW mean (SD); n="Outcome-specific genotype n NOT_STATED in narrative; baseline n is not substituted" | {"day2_AA": [-4.37, 8.08], "day2_AG_GG": [-11.28, 10.44], "day28_AA": [-15.75, 14.67], "day28_AG_GG": [-20.77, 14.59]} MADRS points |
| R0145 Published weight estimates (distinct from raw registry) | PMID 33567185 | NOT_STATED | Full eligible trial; details/age in abstract; Treatment-policy estimates; model-adjusted contrasts where identified. STEP11 arm means not explicitly typed adjusted in abstract.; n={"randomized_N": 1961, "analysis_arm_n": "NOT_STATED in abstract"} | {"percent_means": [-14.9, -2.4], "percent_MD": -12.4, "percent_CI95": [-13.4, -11.5], "kg_means": [-15.3, -2.6], "kg_MD": -12.7, "kg_CI95": [-13.7, -11.7]} percent body-weight change; kg labelled separately |
| R0146 Published weight estimates (distinct from raw registry) | PMID 33625476 | NOT_STATED | Full eligible trial; details/age in abstract; Treatment-policy estimates; model-adjusted contrasts where identified. STEP11 arm means not explicitly typed adjusted in abstract.; n={"randomized": [407, 204], "analysis_n": "NOT_STATED in abstract"} | {"percent_means": [-16, -5.7], "percent_MD": -10.3, "percent_CI95": [-12, -8.6], "baseline_weight_mean_SD": [105.8, 22.9]} percent body-weight change; kg labelled separately |
| R0147 Published weight estimates (distinct from raw registry) | PMID 40825340 | NOT_STATED | Full eligible trial; details/age in abstract; Treatment-policy estimates; model-adjusted contrasts where identified. STEP11 arm means not explicitly typed adjusted in abstract.; n={"randomized": [101, 49], "analysis_n": "NOT_STATED in abstract"} | {"percent_means": [-16, -3.1], "arm_SE": [0.7, 0.9], "baseline_weight_mean_SD": [83.8, 18.1]} percent body-weight change; kg labelled separately |

## Numeric ledger quotations

### R0001 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28); Baseline up to end of the double-blind treatment phase (Day 28); Intranasal Esketamine + Oral Antidepressant (AD)

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0002

> {"groupId": "OG000", "value": "-10.1", "spread": "10.80"}

### R0002 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28); Baseline up to end of the double-blind treatment phase (Day 28); Intranasal Placebo + Oral AD

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0003

> {"groupId": "OG001", "value": "-8.1", "spread": "10.26"}

### R0003 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28); Baseline up to end of the double-blind treatment phase (Day 28); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0/analyses/0. Registry class n and overall n kept separate; see E0004

> {"groupIds": ["OG000"], "nonInferiorityType": "SUPERIORITY", "pValue": "0.123", "pValueComment": "2-sided", "statisticalMethod": "Mixed-effects Model for Repeated Measure", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-2.0", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-4.64", "ciUpperLimit": "0.55"}

### R0004 — Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2); Baseline (Day 1: predose) to 24 hours post first dose (Day 2); Intranasal Esketamine + Oral Antidepressant (AD)

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/1/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0005

> {"groupId": "OG000", "value": "-8.0", "spread": "9.01"}

### R0005 — Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2); Baseline (Day 1: predose) to 24 hours post first dose (Day 2); Intranasal Placebo + Oral AD

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/1/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0006

> {"groupId": "OG001", "value": "-4.4", "spread": "7.66"}

### R0006 — Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2); Baseline (Day 1: predose) to 24 hours post first dose (Day 2); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/1/analyses/0. Registry class n and overall n kept separate; see E0007

> {"groupIds": ["OG000"], "nonInferiorityType": "SUPERIORITY", "paramType": "Difference of LS Means", "paramValue": "-3.3", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-5.33", "ciUpperLimit": "-1.33"}

### R0007 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Esketamine (Esk) Plus Oral Antidepressant (AD)

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0069

> {"groupId": "OG000", "value": "-21.4", "spread": "12.32"}

### R0008 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Placebo Plus Oral AD

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0070

> {"groupId": "OG001", "value": "-17.0", "spread": "13.88"}

### R0009 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/analyses/0. Registry class n and overall n kept separate; see E0071

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "SUPERIORITY", "pValue": "=0.020", "statisticalMethod": "Mixed Model for Repeated Measures", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-4.0", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.31", "ciUpperLimit": "-0.64", "dispersionType": "STANDARD_ERROR_OF_MEAN", "dispersionValue": "1.69"}

### R0010 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline up to Endpoint (Double-blind Induction Phase [Day 28]); Intranasal Esketamine (Esk) Plus Oral Antidepressant (AD)

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/1/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0072

> {"groupId": "OG000", "value": "-19.6", "spread": "13.58"}

### R0011 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline up to Endpoint (Double-blind Induction Phase [Day 28]); Intranasal Placebo Plus Oral AD

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/1/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0073

> {"groupId": "OG001", "value": "-16.3", "spread": "14.24"}

### R0012 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline up to Endpoint (Double-blind Induction Phase [Day 28]); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/1/analyses/0. Registry class n and overall n kept separate; see E0074

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "SUPERIORITY", "pValue": "=0.034", "statisticalMethod": "ANCOVA", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-3.5", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-6.67", "ciUpperLimit": "-0.26"}

### R0013 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Endpoint (Double-blind Induction Phase[Day 28]); Intranasal Esketamine Plus Oral Antidepressant (AD)

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0194

> {"groupId": "OG000", "value": "-10.0", "spread": "12.74"}

### R0014 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Endpoint (Double-blind Induction Phase[Day 28]); Oral AD Plus Intranasal Placebo

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0195

> {"groupId": "OG001", "value": "-6.3", "spread": "8.86"}

### R0015 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Endpoint (Double-blind Induction Phase[Day 28]); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0/analyses/0. Registry class n and overall n kept separate; see E0196

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "SUPERIORITY", "pValue": "=0.059", "statisticalMethod": "Mixed Model for Repeated Measures", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-3.6", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.20", "ciUpperLimit": "0.07"}

### R0016 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline and Endpoint (Double-blind Induction Phase [Day 28]); Intranasal Esketamine Plus Oral Antidepressant (AD)

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/1/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0197

> {"groupId": "OG000", "value": "-9.3", "spread": "12.28"}

### R0017 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline and Endpoint (Double-blind Induction Phase [Day 28]); Oral AD Plus Intranasal Placebo

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/1/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0198

> {"groupId": "OG001", "value": "-5.6", "spread": "9.11"}

### R0018 — Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis; Baseline and Endpoint (Double-blind Induction Phase [Day 28]); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/1/analyses/0. Registry class n and overall n kept separate; see E0199

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "OTHER", "pValue": "=0.052", "statisticalMethod": "ANCOVA", "paramType": "Least Square (LS) Mean Difference", "paramValue": "-3.6", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.16", "ciUpperLimit": "-0.03"}

### R0019 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Esketamine 56 mg Plus Oral Antidepressant

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0240

> {"groupId": "OG000", "value": "-19.0", "spread": "13.86"}

### R0020 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Intranasal Esketamine 84 mg Plus Oral AD

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0241

> {"groupId": "OG001", "value": "-18.8", "spread": "14.12"}

### R0021 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; Oral AD Plus Intranasal Placebo

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/classes/0/categories/0/measurements/2. Registry class n and overall n kept separate; see E0242

> {"groupId": "OG002", "value": "-14.8", "spread": "15.07"}

### R0022 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/analyses/0. Registry class n and overall n kept separate; see E0243

> {"groupIds": ["OG001", "OG002"], "nonInferiorityType": "SUPERIORITY", "pValue": "0.088", "statisticalMethod": "Mixed Model for Repeated Measures", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-3.2", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-6.88", "ciUpperLimit": "0.45"}

### R0023 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 of Double- Blind Induction Phase- Mixed- Effects Model Using Repeated Measures (MMRM) Analysis; Baseline up to Day 28 of Double-blind Induction Phase; registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/analyses/1. Registry class n and overall n kept separate; see E0244

> {"groupIds": ["OG000", "OG002"], "nonInferiorityType": "SUPERIORITY", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-4.1", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.67", "ciUpperLimit": "-0.49"}

### R0024 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); Intranasal Esketamine 56 mg Plus Oral Antidepressant

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0245

> {"groupId": "OG000", "value": "-18.3", "spread": "14.21"}

### R0025 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); Intranasal Esketamine 84 mg Plus Oral AD

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0246

> {"groupId": "OG001", "value": "-17.4", "spread": "14.25"}

### R0026 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); Oral AD Plus Intranasal Placebo

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/classes/0/categories/0/measurements/2. Registry class n and overall n kept separate; see E0247

> {"groupId": "OG002", "value": "-14.3", "spread": "15.00"}

### R0027 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/analyses/0. Registry class n and overall n kept separate; see E0248

> {"groupIds": ["OG001", "OG002"], "nonInferiorityType": "SUPERIORITY", "pValue": "= 0.250", "statisticalMethod": "ANCOVA", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-2.0", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-5.52", "ciUpperLimit": "1.42"}

### R0028 — Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis; Baseline up to Double-blind Endpoint (Day 28); registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/analyses/1. Registry class n and overall n kept separate; see E0249

> {"groupIds": ["OG000", "OG002"], "nonInferiorityType": "SUPERIORITY", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-4.1", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.53", "ciUpperLimit": "-0.6"}

### R0029 — Combined-dose verified arm derivation; ; verified_input

Source: cache/esketamine-trd-madrs/verified_arms.json#/NCT02417064. Registry class n and overall n kept separate; see E0250

> {"outcome": "Observed-case Day-28 raw change-score MADRS MD", "mean1": -18.91, "sd1": 13.95, "nc1": 209, "mean2": -14.8, "sd2": 15.07, "nc2": 108, "provenance": "fulltext_verified_arms", "source": "TRANSFORM-1 (NCT02417064) committed CT.gov MADRS Day-28 (MMRM) per-arm change scores: intranasal esketamine 56 mg + oral AD -19.0 (SD 13.86, n=111); 84 mg + oral AD -18.8 (SD 14.12, n=98); oral AD + intranasal placebo -14.8 (SD 15.07, n=108). MULTI-ARM COMBINATION (Cochrane RevMan 6.5.2.10): the two intranasal esketamine dose arms are combined against the SHARED placebo to avoid double-counting it: combined esketamine mean -18.91, SD 13.95, n=209 (weighted mean of -19.0/-18.8; pooled SD from (n1-1)s1^2+(n2-1)s2^2 + n1*n2/(n1+n2)*(m1-m2)^2 over N-1). Both dose arms are INTRANASAL (route matches the protocol intranasal PICO). vs placebo -14.8 (SD 15.07, n=108). MD = -4.11.", "verification": "Per-arm values verbatim in committed cache/esketamine-trd-madrs/records.json ctgov_results NCT02417064; combined arm -18.91/13.95/209 computed by the standard subgroup-combination formula. Recovered because the automated CT.gov extractor takes a single arm pair and cannot combine 3 arms.", "override": true}

### R0030 — The Change From Baseline in Subjective Sleep Latency.; Baseline and 3 weeks; Circadin

Source: cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0301

> {"groupId": "OG000", "value": "-19.1", "spread": "47.3"}

### R0031 — The Change From Baseline in Subjective Sleep Latency.; Baseline and 3 weeks; Placebo

Source: cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0302

> {"groupId": "OG001", "value": "-1.7", "spread": "47.8"}

### R0032 — The Change From Baseline in Subjective Sleep Latency.; Baseline and 3 weeks; registry_analysis

Source: cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/analyses/0. Registry class n and overall n kept separate; see E0303

> {"groupIds": ["OG000", "OG001"], "groupDescription": "The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.", "nonInferiorityType": "SUPERIORITY_OR_OTHER", "pValue": "<0.05", "statisticalMethod": "ANCOVA", "paramType": "Mean Difference (Final Values)", "paramValue": "-15.6", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-25.3", "ciUpperLimit": "-6", "dispersionType": "STANDARD_DEVIATION", "dispersionValue": "47"}

### R0033 — Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0378

> {"groupId": "OG000", "value": "-16.5", "spread": "10.1"}

### R0034 — Change in Body Weight (%); Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0379

> {"groupId": "OG001", "value": "-5.8", "spread": "7.7"}

### R0035 — Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/1/categories/0/measurements/0. Registry class n and overall n kept separate; see E0380

> {"groupId": "OG000", "value": "-17.6", "spread": "9.6"}

### R0036 — Change in Body Weight (%); Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/1/categories/0/measurements/1. Registry class n and overall n kept separate; see E0381

> {"groupId": "OG001", "value": "-6.1", "spread": "7.6"}

### R0037 — Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/analyses/0. Registry class n and overall n kept separate; see E0382

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-10.27", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-11.97", "ciUpperLimit": "-8.57"}

### R0038 — Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/analyses/1. Registry class n and overall n kept separate; see E0383

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Hypothetical estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "MMRM (mixed model repeated measurement)", "paramType": "Treatment difference", "paramValue": "-12.67", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-14.34", "ciUpperLimit": "-11.00"}

### R0039 — Change in Body Weight (Kg); Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/8/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0384

> {"groupId": "OG000", "value": "-17.5", "spread": "11.4"}

### R0040 — Change in Body Weight (Kg); Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/8/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0385

> {"groupId": "OG001", "value": "-6.2", "spread": "8.6"}

### R0041 — Change in Body Weight; Baseline (week 0) to week 8; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/24/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0386

> {"groupId": "OG000", "value": "-7.8", "spread": "3.1"}

### R0042 — Change in Body Weight; Baseline (week 0) to week 8; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/24/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0387

> {"groupId": "OG001", "value": "-6.0", "spread": "3.6"}

### R0043 — Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0389

> {"groupId": "OG000", "value": "-15.6", "spread": "10.1"}

### R0044 — Change in Body Weight (%); Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0390

> {"groupId": "OG001", "value": "-2.8", "spread": "6.5"}

### R0045 — Change in Body Weight (%); Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/1/categories/0/measurements/0. Registry class n and overall n kept separate; see E0391

> {"groupId": "OG000", "value": "-16.9", "spread": "9.4"}

### R0046 — Change in Body Weight (%); Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/1/categories/0/measurements/1. Registry class n and overall n kept separate; see E0392

> {"groupId": "OG001", "value": "-3.1", "spread": "6.4"}

### R0047 — Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/analyses/0. Registry class n and overall n kept separate; see E0393

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-12.44", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-13.37", "ciUpperLimit": "-11.51"}

### R0048 — Change in Body Weight (%); Baseline (week 0) to week 68; registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/analyses/1. Registry class n and overall n kept separate; see E0394

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Hypothetical estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-14.42", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-15.29", "ciUpperLimit": "-13.55"}

### R0049 — Change in Body Weight (kg); Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/9/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0395

> {"groupId": "OG000", "value": "-16.1", "spread": "10.6"}

### R0050 — Change in Body Weight (kg); Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/9/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0396

> {"groupId": "OG001", "value": "-2.9", "spread": "7.2"}

### R0051 — Change in Body Weight (%) - DEXA Subpopulation; Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/32/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0397

> {"groupId": "OG000", "value": "-15.8", "spread": "11.1"}

### R0052 — Change in Body Weight (%) - DEXA Subpopulation; Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/32/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0398

> {"groupId": "OG001", "value": "-3.4", "spread": "6.1"}

### R0053 — Change in Body Weight (kg) - DEXA Subpopulation; Baseline (week 0) to week 68; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/33/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0399

> {"groupId": "OG000", "value": "-15.5", "spread": "11.4"}

### R0054 — Change in Body Weight (kg) - DEXA Subpopulation; Baseline (week 0) to week 68; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/33/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0400

> {"groupId": "OG001", "value": "-3.2", "spread": "6.1"}

### R0055 — Change in Body Weight (%) : In-trial Observation Period; Baseline (week 0), end of treatment (week 44); Semaglutide

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0403

> {"groupId": "OG000", "value": "-16.4", "spread": "7.3"}

### R0056 — Change in Body Weight (%) : In-trial Observation Period; Baseline (week 0), end of treatment (week 44); Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0404

> {"groupId": "OG001", "value": "-2.6", "spread": "5.8"}

### R0057 — Change in Body Weight (%) : In-trial Observation Period; Baseline (week 0), end of treatment (week 44); registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/0/analyses/0. Registry class n and overall n kept separate; see E0405

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-12.99", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-15.28", "ciUpperLimit": "-10.70"}

### R0058 — Change in Body Weight (%) : On-treatment Observation Period; Baseline (week 0), end of treatment (week 44); Semaglutide

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/1/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0406

> {"groupId": "OG000", "value": "-16.4", "spread": "7.4"}

### R0059 — Change in Body Weight (%) : On-treatment Observation Period; Baseline (week 0), end of treatment (week 44); Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/1/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0407

> {"groupId": "OG001", "value": "-2.7", "spread": "5.8"}

### R0060 — Change in Body Weight (%) : On-treatment Observation Period; Baseline (week 0), end of treatment (week 44); registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/1/analyses/0. Registry class n and overall n kept separate; see E0408

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "MMRM", "paramType": "Treatment Difference", "paramValue": "-13.40", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-15.70", "ciUpperLimit": "-11.11"}

### R0061 — Change in Body Weight (kg); Baseline (week 0), end of treatment (week 44); Semaglutide

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/8/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0409

> {"groupId": "OG000", "value": "-13.0", "spread": "5.5"}

### R0062 — Change in Body Weight (kg); Baseline (week 0), end of treatment (week 44); Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/8/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0410

> {"groupId": "OG001", "value": "-2.0", "spread": "5.1"}

### R0063 — Change in Body Weight (Percentage [%]); From randomisation (week 0) to end of treatment (week 52); Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/0/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0436

> {"groupId": "OG000", "value": "-14.4", "spread": "7.9"}

### R0064 — Change in Body Weight (Percentage [%]); From randomisation (week 0) to end of treatment (week 52); Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/0/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0437

> {"groupId": "OG001", "value": "-2.7", "spread": "4.3"}

### R0065 — Change in Body Weight (Percentage [%]); From randomisation (week 0) to end of treatment (week 52); registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/0/analyses/0. Registry class n and overall n kept separate; see E0438

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy estimand", "nonInferiorityType": "SUPERIORITY", "nonInferiorityComment": "Week 52 responses were analysed using an analysis of covariance model (ANCOVA) with randomised treatment as factor and baseline body weight as covariate.", "pValue": "<0.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-11.19", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-12.97", "ciUpperLimit": "-9.42"}

### R0066 — Change in Body Weight (Kilogram [Kg]); From randomisation (week 0) to week 52; Semaglutide 2.4 mg

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/11/classes/0/categories/0/measurements/0. Registry class n and overall n kept separate; see E0439

> {"groupId": "OG000", "value": "-15.8", "spread": "9.3"}

### R0067 — Change in Body Weight (Kilogram [Kg]); From randomisation (week 0) to week 52; Placebo

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/11/classes/0/categories/0/measurements/1. Registry class n and overall n kept separate; see E0440

> {"groupId": "OG001", "value": "-2.8", "spread": "5.0"}

### R0068 — Baseline diary SOL

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0069 — Week 3 absolute diary SOL

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0070 — Week 3 change diary SOL

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0071 — Week 3 adjusted diary SOL contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0072 — Baseline diary SOL

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0073 — Week 3 absolute diary SOL

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0074 — Week 3 change diary SOL

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0075 — Week 3 adjusted diary SOL contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T3. 

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

### R0076 — Visit 7 diary change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T4. Long-term extension; rerandomization and changing n; N MAX cannot be treated as exact SOL n.

> Table 4 Sleep diary parameters in the low excretors. Treatment effects Change from baseline Mean (SD) Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 99 Placebo 86 31 Sleep latency PRM -9.0 (50.5) -23.6 (42.1) -0.6 (-14.0, 12.7) -6.7 (-16.4, 3.0) (min) Placebo -9.0 (48.7) -19.4 (79.5) P = 0.924 P = 0.174 Sleep PRM -0.27 (0.77) -0.31 (1.08) -0.16 (-0.39, 0.08) -0.04 (-0.24, 0.16) maintenance Placebo -0.12 (1.04) -0.34 (0.71) P = 0.185 P = 0.677 Total sleep PRM 0.34 (0.88) 0.70 (1.00) 9.1 (-6.1, 24.4) 13.1 (1.0, 25.2) time (h) Placebo 0.20 (0.91) 0.47 (1.18) P = 0.236 P = 0.035 Sleep onset PRM -0.15 (0.89) -0.46 (0.79) -0.08 (-0.33, 0.17) -0.16 (-0.34, 0.03) (h) Placebo -0.05 (0.80) -0.24 (1.11) P = 0.530 P = 0.096 Sleep offset PRM 0.09 (0.79) 0.08 (0.84) 0.04 (-0.18, 0.25) 0.07 (-0.09, 0.22) (h) Placebo 0.10 (0.75) 0.20 (1.00) P = 0.744 P = 0.392 Refreshed on PRM -0.09 (0.46) -0.23 (0.43) -0.01 (-0.13, 0.11) -0.03 (-0.12, 0.06) waking Placebo -0.09 (0.40) -0.29 (0.47) P = 0.830 P = 0.540 Morning PRM -0.14 (0.67) -0.42 (0.65) 0.01 (-0.18, 0.19) -0.06 (-0.19, 0.08) alertness Placebo -0.19 (0.63) -0.35 (0.73) P = 0.936 P = 0.426 Sleep quality PRM -0.20 (0.67) -0.43 (0.70) -0.04 (-0.24, 0.16) -0.08 (-0.23, 0.06) Placebo -0.16 (0.70) -0.34 (0.60) P = 0.688 P = 0.266 *The global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness C, confidence interval; SD, standard deviation; PRM, prolonged release melatonin.

### R0077 — 26-week global diary effect

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T4. 

> Table 4 Sleep diary parameters in the low excretors. Treatment effects Change from baseline Mean (SD) Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 99 Placebo 86 31 Sleep latency PRM -9.0 (50.5) -23.6 (42.1) -0.6 (-14.0, 12.7) -6.7 (-16.4, 3.0) (min) Placebo -9.0 (48.7) -19.4 (79.5) P = 0.924 P = 0.174 Sleep PRM -0.27 (0.77) -0.31 (1.08) -0.16 (-0.39, 0.08) -0.04 (-0.24, 0.16) maintenance Placebo -0.12 (1.04) -0.34 (0.71) P = 0.185 P = 0.677 Total sleep PRM 0.34 (0.88) 0.70 (1.00) 9.1 (-6.1, 24.4) 13.1 (1.0, 25.2) time (h) Placebo 0.20 (0.91) 0.47 (1.18) P = 0.236 P = 0.035 Sleep onset PRM -0.15 (0.89) -0.46 (0.79) -0.08 (-0.33, 0.17) -0.16 (-0.34, 0.03) (h) Placebo -0.05 (0.80) -0.24 (1.11) P = 0.530 P = 0.096 Sleep offset PRM 0.09 (0.79) 0.08 (0.84) 0.04 (-0.18, 0.25) 0.07 (-0.09, 0.22) (h) Placebo 0.10 (0.75) 0.20 (1.00) P = 0.744 P = 0.392 Refreshed on PRM -0.09 (0.46) -0.23 (0.43) -0.01 (-0.13, 0.11) -0.03 (-0.12, 0.06) waking Placebo -0.09 (0.40) -0.29 (0.47) P = 0.830 P = 0.540 Morning PRM -0.14 (0.67) -0.42 (0.65) 0.01 (-0.18, 0.19) -0.06 (-0.19, 0.08) alertness Placebo -0.19 (0.63) -0.35 (0.73) P = 0.936 P = 0.426 Sleep quality PRM -0.20 (0.67) -0.43 (0.70) -0.04 (-0.24, 0.16) -0.08 (-0.23, 0.06) Placebo -0.16 (0.70) -0.34 (0.60) P = 0.688 P = 0.266 *The global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness C, confidence interval; SD, standard deviation; PRM, prolonged release melatonin.

### R0078 — Visit 7 diary change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T6. Long-term extension; rerandomization and changing n; N MAX cannot be treated as exact SOL n.

> Table 6 Sleep Diary parameters in the 65-80 age group. Treatment effects Change from baseline Mean (SD) Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 137 159 Placebo 144 61 Sleep latency PRM -19.1 (47.3) -25.9 (46.4) -15.6 (-25.3, -6.0) -14.5 (-21.4, -7.7) (min) Placebo -1.7 (47.8) -8.3 (61.5) P = 0.002 P < 0.001 Sleep PRM -0.24 (0.80) -0.31 (0.94) -0.17 (-0.33, 0.00) -0.09 (-0.22, 0.03) maintenance Placebo -0.09 (0.78) -0.20 (0.70) P = 0.046 P = 0.148 Total sleep PRM 0.34 (0.75) 0.64 (0.99) 7.0 (-3.4, 17.4) 7.5 (-0.7, 15.7) time (h) Placebo 0.20 (0.79) 0.41 (1.06) P = 0.186 P = 0.073 Sleep onset PRM -0.22 (0.80) -0.41 (0.75) -0.22 (-0.39, -0.05) -0.21 (-0.33, -0.08) (hours) Placebo 0.00 (0.71) -0.12 (1.06) P = 0.012 P = 0.002 Sleep offset PRM 0.03 (0.81) 0.03 (0.84) -0.16 (-0.33, 0.02) -0.12 (-0.24, 0.00) (h) Placebo 0.19 (0.79) 0.21 (0.91) P = 0.076 P = 0.051 Refreshed on PRM -0.10 (0.36) -0.22 (0.42) 0.00 (-0.08, 0.08) -0.06 (-0.12, 0.00) waking Placebo -0.09 (0.37) -0.11 (0.42) P = 0.994 P = 0.053 Morning PRM -0.18 (0.52) -0.36 (0.69) -0.04 (-0.16, 0.07) -0.10 (-0.19, -0.01) alertness Placebo -0.11 (0.51) -0.09 (0.60) P = 0.453 P = 0.032 PRM -0.20 (0.56) -0.39 (0.71) -0.06 (-0.19, 0.07) -0.08 (-0.18, 0.01) Sleep quality Placebo -0.12 (0.57) -0.17 (0.54) P = 0.356 P = 0.082 Mean (SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness. CI, confidence interval

### R0079 — 26-week global diary effect

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T6. 

> Table 6 Sleep Diary parameters in the 65-80 age group. Treatment effects Change from baseline Mean (SD) Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 137 159 Placebo 144 61 Sleep latency PRM -19.1 (47.3) -25.9 (46.4) -15.6 (-25.3, -6.0) -14.5 (-21.4, -7.7) (min) Placebo -1.7 (47.8) -8.3 (61.5) P = 0.002 P < 0.001 Sleep PRM -0.24 (0.80) -0.31 (0.94) -0.17 (-0.33, 0.00) -0.09 (-0.22, 0.03) maintenance Placebo -0.09 (0.78) -0.20 (0.70) P = 0.046 P = 0.148 Total sleep PRM 0.34 (0.75) 0.64 (0.99) 7.0 (-3.4, 17.4) 7.5 (-0.7, 15.7) time (h) Placebo 0.20 (0.79) 0.41 (1.06) P = 0.186 P = 0.073 Sleep onset PRM -0.22 (0.80) -0.41 (0.75) -0.22 (-0.39, -0.05) -0.21 (-0.33, -0.08) (hours) Placebo 0.00 (0.71) -0.12 (1.06) P = 0.012 P = 0.002 Sleep offset PRM 0.03 (0.81) 0.03 (0.84) -0.16 (-0.33, 0.02) -0.12 (-0.24, 0.00) (h) Placebo 0.19 (0.79) 0.21 (0.91) P = 0.076 P = 0.051 Refreshed on PRM -0.10 (0.36) -0.22 (0.42) 0.00 (-0.08, 0.08) -0.06 (-0.12, 0.00) waking Placebo -0.09 (0.37) -0.11 (0.42) P = 0.994 P = 0.053 Morning PRM -0.18 (0.52) -0.36 (0.69) -0.04 (-0.16, 0.07) -0.10 (-0.19, -0.01) alertness Placebo -0.11 (0.51) -0.09 (0.60) P = 0.453 P = 0.032 PRM -0.20 (0.56) -0.39 (0.71) -0.06 (-0.19, 0.07) -0.08 (-0.18, 0.01) Sleep quality Placebo -0.12 (0.57) -0.17 (0.54) P = 0.356 P = 0.082 Mean (SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness. CI, confidence interval

### R0080 — PSQI component 2 Visit 3 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0081 — PSQI component 2 Visit 7 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0082 — PSQI component 2 Short term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0083 — PSQI component 2 Long term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0084 — PSQI question 2 Visit 3 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0085 — PSQI question 2 Visit 7 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0086 — PSQI question 2 Short term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0087 — PSQI question 2 Long term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T5. 

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

### R0088 — PSQI component 2 Visit 3 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0089 — PSQI component 2 Visit 7 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0090 — PSQI component 2 Short term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0091 — PSQI component 2 Long term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0092 — PSQI question 2 Visit 3 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0093 — PSQI question 2 Visit 7 change

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0094 — PSQI question 2 Short term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0095 — PSQI question 2 Long term adjusted contrast

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#T7. 

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### R0096 — Linked PMID 21091391, week-3 diary changes

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/83/abstract. 

> OBJECTIVES: The authors recently reported on efficacy and safety of prolonged-release melatonin formulation (PRM; Circadin 2  mg) in elderly insomnia patients. The age cut-off for response to PRM and the long-term maintenance of efficacy and safety were further evaluated by looking at the total cohort (age 18-80 years) from that study and subsets of patients aged 18-54 and 55-80 years (for whom the drug is currently indicated). DESIGN: Randomised, double-blind, placebo controlled trial. SETTING: Multicentre, outpatients, primary care setting. METHODS: A total of 930 males and females aged 18-80 years with primary insomnia who reported mean nightly sleep latency (SL) >20  min were enrolled and 791 entered the active phase of the study. The study comprised a 2-week, single-blind placebo run-in period followed by 3 week's double-blind treatment with PRM or placebo, one tablet per day at 2 hours before bedtime. PRM patients continued whereas placebo completers were re-randomised 1:1 to PRM or placebo for 26 weeks followed by 2-weeks run-out on placebo. MAIN OUTCOME MEASURES: SL and other sleep variables derived from sleep diary, Pittsburgh Sleep Quality Index (PSQI), Quality of life (WHO-5), Clinical Global Impression of Improvement (CGI-I) and adverse effects, recorded each visit, withdrawal and rebound effects during run-out. RESULTS: In all, 746 patients completed the 3-week and 555 (421 PRM, 134 placebo) completed the 6-month period. The principal reason for drop-out was patient decision. At 3 weeks, significant differences in SL (diary, primary variable) in favour of PRM vs. placebo treatment were found for the 55-80-year group (-15.4 vs. -5.5  min, p = 0.014) but not the 18-80-year cut-off which included younger patients. Other variables (SL-PSQI, PSQI, WHO-5, CGI-I scores) improved significantly with PRM in the 18-80-year population, more so than in the 55-80-year age group. Improvements were maintained or enhanced over the 6-month period with no signs of tolerance. No withdrawal symptoms or rebound insomnia were detected. Most adverse events were mild with no significant differences between PRM and placebo groups in any safety outcome. CONCLUSIONS: The results demonstrate short- and long-term efficacy of PRM in insomnia patients aged 18-80 years, particularly those aged 55 and over. PRM was well-tolerated over the entire 6-month period with no rebound or withdrawal symptoms following discontinuation. Study Registry No: ClinicalTrials.gov ID: NCT00397189.

### R0097 — Week-3 latency change

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/87/abstract. 

> OBJECTIVE: Melatonin, the hormone produced nocturnally by the pineal gland, serves as a circadian time cue and sleep-anticipating signal in humans. With age, melatonin production declines and the prevalence of sleep disorders, particularly insomnia, increases. The efficacy and safety of a prolonged release melatonin formulation (PR-melatonin; Circadin* 2 mg) were examined in insomnia patients aged 55 years and older. DESIGN: Randomised, double blind, placebo-controlled. SETTING: Primary care. METHODOLOGY: From 1248 patients pre-screened and 523 attending visit 1, 354 males and females aged 55-80 years were admitted to the study, 177 to active medication and 177 to placebo. The study was conducted by primary care physicians in the West of Scotland and consisted of a 2-week, single blind, placebo run-in period followed by a 3-week double blind treatment period with PR-melatonin or placebo, one tablet per day at 2 hours before bedtime. MAIN OUTCOME MEASURES: Responder rate (concomitant improvement in sleep quality and morning alertness on Leeds Sleep Evaluation Questionnaire [LSEQ]), other LSEQ assessments, Pittsburgh Sleep Quality Index (PSQI) global score, other PSQI assessments, Quality of Night and Quality of Day derived from a diary, Clinical Global Improvement scale (CGI) score and quality of life (WHO-5 well being index). RESULTS: Of the 354 patients entering the active phase of the study, 20 failed to complete visit 3 (eight PR-melatonin; 12 Placebo). The principal reasons for drop-out were patient decision and lost to follow-up. Significant differences in favour of PR-melatonin vs. placebo treatment were found in concomitant and clinically relevant improvements in quality of sleep and morning alertness, demonstrated by responder analysis (26% vs. 15%; p = 0.014) as well as on each of these parameters separately. A significant and clinically relevant shortening of sleep latency to the same extent as most frequently used sleep medications was also found (-24.3 vs.-12.9 minutes; p = 0.028). Quality of life also improved significantly (p = 0.034). CONCLUSIONS: PR-melatonin results in significant and clinically meaningful improvements in sleep quality, morning alertness, sleep onset latency and quality of life in primary insomnia patients aged 55 years and over. TRIAL REGISTRATION: The trial was conducted prior to registration being introduced.

### R0098 — Shorter sleep-onset latency

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/85/abstract. PSG likely from context, but tuple not explicitly assigned; no silent inference.

> Objectives of this study were to investigate the effects of prolonged-release melatonin 2 mg (PRM) on sleep and subsequent daytime psychomotor performance in patients aged > or =55 years with primary insomnia, as defined by fourth revision of the Diagnostic and Statistical Manual of Mental Disorders of the American Psychiatric Association. Patients (N = 40) were treated nightly single-blind with placebo (2 weeks), randomized double-blind to PRM or placebo (3 weeks) followed by withdrawal period (3 weeks). Sleep was assessed by polysomnography, all-night sleep electroencephalography spectral analysis and questionnaires. Psychomotor performance was assessed by the Leeds Psychomotor Test battery. By the end of the double-blind treatment, the PRM group had significantly shorter sleep onset latency (9 min; P = 0.02) compared with the placebo group and scored significantly better in the Critical Flicker Fusion Test (P = 0.008) without negatively affecting sleep structure and architecture. Half of the patients reported substantial improvement in sleep quality at home with PRM compared with 15% with placebo (P = 0.018). No rebound effects were observed during withdrawal. In conclusion, nightly treatment with PRM effectively induced sleep and improved perceived quality of sleep in patients with primary insomnia aged > or =55 years. Daytime psychomotor performance was not impaired and was consistently better with PRM compared with placebo. PRM was well tolerated with no evidence of rebound effects.

### R0099 — Diary Baseline

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#t3-ibpc-5-009. 

> Table 3 Efficacy of prolonged-release melatonin (PRM) compared with placebo (6 months): improvement in sleep latency (daily sleep diary) Daily sleep diary score PRM Placebo N Mean length of time (minutes) SD N Mean length of time (minutes) SD Baseline 134 73.6 5.6 39 73.5 4.3 6 months 121 51.0 3.6 36 65.2 4.4 Mean change from baseline 121 −23.3 2.9 36 −7.5 3.6 Significance for PRM vs placebo P = 0.02 Abbreviations: PRM, prolonged-release melatonin; SD, standard deviation.

### R0100 — Diary 6 months

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#t3-ibpc-5-009. 

> Table 3 Efficacy of prolonged-release melatonin (PRM) compared with placebo (6 months): improvement in sleep latency (daily sleep diary) Daily sleep diary score PRM Placebo N Mean length of time (minutes) SD N Mean length of time (minutes) SD Baseline 134 73.6 5.6 39 73.5 4.3 6 months 121 51.0 3.6 36 65.2 4.4 Mean change from baseline 121 −23.3 2.9 36 −7.5 3.6 Significance for PRM vs placebo P = 0.02 Abbreviations: PRM, prolonged-release melatonin; SD, standard deviation.

### R0101 — Diary Change from baseline

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#t3-ibpc-5-009. 

> Table 3 Efficacy of prolonged-release melatonin (PRM) compared with placebo (6 months): improvement in sleep latency (daily sleep diary) Daily sleep diary score PRM Placebo N Mean length of time (minutes) SD N Mean length of time (minutes) SD Baseline 134 73.6 5.6 39 73.5 4.3 6 months 121 51.0 3.6 36 65.2 4.4 Mean change from baseline 121 −23.3 2.9 36 −7.5 3.6 Significance for PRM vs placebo P = 0.02 Abbreviations: PRM, prolonged-release melatonin; SD, standard deviation.

### R0102 — Narrative six-month decreases and standardized effect

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#Results. 

> By the end of the 6-month treatment period, the mean improvement (decrease) in patients’ evaluated sleep latency (reported in the daily sleep diary) was significantly higher with PRM (25.89 minutes) than with placebo (7.54 minutes) (df = 1; F = 8.74; P = 0.02, ANCOVA) ( Table 3 ). The Cohen’s d effect size was 0.39.

### R0103 — Baseline Mean (SD)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0104 — Baseline Median (range)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0105 — Day 28 Mean (SD)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0106 — Day 28 Median (range)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0107 — Change from baseline to Day 28 Mean (SD)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0108 — Change from baseline to Day 28 Median (range)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0109 — Change from baseline to Day 28 Difference of LS means (SE)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0110 — Change from baseline to Day 28 95% CI on difference

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0111 — Change from baseline to Day 28 2-sided p-value

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0002. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0112 — Baseline Mean (SD)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0113 — Baseline Median (range)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0114 — Day 2 (24 hours) Mean (SD)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0115 — Day 2 (24 hours) Median (range)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0116 — Change from baseline to Day 2 (24 hours) Mean (SD)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0117 — Change from baseline to Day 2 (24 hours) Median (range)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0118 — Change from baseline to Day 2 (24 hours) Difference of LS means (SE)

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0119 — Change from baseline to Day 2 (24 hours) 95% CI on difference

Source: cache/esketamine-trd-madrs/ft_37025256.txt#t0003. Columns follow source: esketamine, placebo; one-column LS contrasts compare those arms.

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

### R0120 — 35441931 Table 2 Baseline Baseline

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: PHQ-9 and MADRS total score and change from baseline score at days 15 and 28
> Time point | Absolute score | Change from baseline | Treatment difference
> Placebo plus AD | Esketamine plus AD | Placebo plus AD | Esketamine plus AD
> n | Mean (SD) | N | Mean (SD) | Mean (SD) | Mean (SD) | Mean (SE) | 95% CI | p value
> PHQ-9
> Baseline | 109 | 20.4 (3.73) | 114 | 20.2 (3.63) |  |  |  |  | 
> Day 15 | 104 | 13.2 (7.20) | 111 | 11.2 (6.33) | − 7.1 (6.87) | − 9.0 (6.45) | − 1.8 (0.91) | − 3.62 to − 0.04 | 0.045
> Day 28 | 100 | 10.2 (7.68) | 104 | 7.3 (5.74) | − 10.2 (7.80) | − 13.0 (6.42) | − 2.8 (1.00) | − 4.75 to − 0.81 | 0.006
> MADRS
> Baseline | 109 | 37.3 (5.66) | 114 | 37.0 (5.69) |  |  |  |  | 
> Day 15 | 102 | 27.2 (11.37) | 107 | 24.8 (10.06) | − 10.0 (11.63) | − 12.1 (10.58) | − 2.0 (1.54) | − 5.06 to 1.00 | 0.189
> Day 28 | 100 | 20.6 (12.70) | 101 | 15.5 (10.67) | − 17.0 (13.88) | − 21.4 (12.32) | − 4.4 (1.85) | − 8.10 to − 0.80 | 0.017

### R0121 — 35441931 Table 2 Baseline Day 15

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: PHQ-9 and MADRS total score and change from baseline score at days 15 and 28
> Time point | Absolute score | Change from baseline | Treatment difference
> Placebo plus AD | Esketamine plus AD | Placebo plus AD | Esketamine plus AD
> n | Mean (SD) | N | Mean (SD) | Mean (SD) | Mean (SD) | Mean (SE) | 95% CI | p value
> PHQ-9
> Baseline | 109 | 20.4 (3.73) | 114 | 20.2 (3.63) |  |  |  |  | 
> Day 15 | 104 | 13.2 (7.20) | 111 | 11.2 (6.33) | − 7.1 (6.87) | − 9.0 (6.45) | − 1.8 (0.91) | − 3.62 to − 0.04 | 0.045
> Day 28 | 100 | 10.2 (7.68) | 104 | 7.3 (5.74) | − 10.2 (7.80) | − 13.0 (6.42) | − 2.8 (1.00) | − 4.75 to − 0.81 | 0.006
> MADRS
> Baseline | 109 | 37.3 (5.66) | 114 | 37.0 (5.69) |  |  |  |  | 
> Day 15 | 102 | 27.2 (11.37) | 107 | 24.8 (10.06) | − 10.0 (11.63) | − 12.1 (10.58) | − 2.0 (1.54) | − 5.06 to 1.00 | 0.189
> Day 28 | 100 | 20.6 (12.70) | 101 | 15.5 (10.67) | − 17.0 (13.88) | − 21.4 (12.32) | − 4.4 (1.85) | − 8.10 to − 0.80 | 0.017

### R0122 — 35441931 Table 2 Baseline Day 28

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: PHQ-9 and MADRS total score and change from baseline score at days 15 and 28
> Time point | Absolute score | Change from baseline | Treatment difference
> Placebo plus AD | Esketamine plus AD | Placebo plus AD | Esketamine plus AD
> n | Mean (SD) | N | Mean (SD) | Mean (SD) | Mean (SD) | Mean (SE) | 95% CI | p value
> PHQ-9
> Baseline | 109 | 20.4 (3.73) | 114 | 20.2 (3.63) |  |  |  |  | 
> Day 15 | 104 | 13.2 (7.20) | 111 | 11.2 (6.33) | − 7.1 (6.87) | − 9.0 (6.45) | − 1.8 (0.91) | − 3.62 to − 0.04 | 0.045
> Day 28 | 100 | 10.2 (7.68) | 104 | 7.3 (5.74) | − 10.2 (7.80) | − 13.0 (6.42) | − 2.8 (1.00) | − 4.75 to − 0.81 | 0.006
> MADRS
> Baseline | 109 | 37.3 (5.66) | 114 | 37.0 (5.69) |  |  |  |  | 
> Day 15 | 102 | 27.2 (11.37) | 107 | 24.8 (10.06) | − 10.0 (11.63) | − 12.1 (10.58) | − 2.0 (1.54) | − 5.06 to 1.00 | 0.189
> Day 28 | 100 | 20.6 (12.70) | 101 | 15.5 (10.67) | − 17.0 (13.88) | − 21.4 (12.32) | − 4.4 (1.85) | − 8.10 to − 0.80 | 0.017

### R0123 — 34973081 Table 4 Baseline Mean (SD)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#TABLE-4. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 |

### R0124 — 34973081 Table 4 Change to day 28 Mean (SD)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#TABLE-4. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 |

### R0125 — 34973081 Table 4 MMRM analysis a Diff. of LS means b (SE)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#TABLE-4. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 |

### R0126 — 34973081 Table 4 MMRM analysis a 95% CI on difference

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#TABLE-4. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 |

### R0127 — 34293233 Table 2 Baseline Mean (SD)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0128 — 34293233 Table 2 Change from baseline to day 28 Mean (SD)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0129 — 34293233 Table 2 Change from baseline to day 28 p value based on pared t‐test

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0130 — 34293233 Table 2 ANCOVA analysis a of treatment groups within same status of comorbid anxiety Difference of LS means b (SE)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0131 — 34293233 Table 2 ANCOVA analysis a of treatment groups within same status of comorbid anxiety 95% CI on difference

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0132 — 34293233 Table 2 ANCOVA analysis a of treatment groups within same status of comorbid anxiety p value on difference

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0133 — 34293233 Table 2 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no Difference of LS means d (SE)

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0134 — 34293233 Table 2 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no 95% CI on difference

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0135 — 34293233 Table 2 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no p value

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371

### R0136 — 32367114 Table 2  Day 2

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2.: Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score
>  |  | Esketamine + AD | AD + placebo
>  | Minor allele frequency | n | Slope | P value | R 2 partial | Minor allele effect | n | Slope | P value | R 2 partial | Minor allele effect
> Day 2 | 0.13 | 229 | −0.63 | .69 | <0.5 % | None | 169 | −6.59 | <.001 | 10% | Greater response
> Day 28 | 0.13 | 232 | −1.81 | .34 | <0.5 % | None | 172 | −4.30 | .07 | 2% | None

### R0137 — 32367114 Table 2  Day 28

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#TABLE-2. Columns explicitly defined by retained source headers; pooled results cannot be assigned separately.

> TABLE Table 2.: Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score
>  |  | Esketamine + AD | AD + placebo
>  | Minor allele frequency | n | Slope | P value | R 2 partial | Minor allele effect | n | Slope | P value | R 2 partial | Minor allele effect
> Day 2 | 0.13 | 229 | −0.63 | .69 | <0.5 % | None | 169 | −6.59 | <.001 | 10% | Greater response
> Day 28 | 0.13 | 232 | −1.81 | .34 | <0.5 % | None | 172 | −4.30 | .07 | 2% | None

### R0138 — Day-28 adjusted MADRS contrast

Source: cache/esketamine-trd-madrs/records.json#/records/18/abstract. 

> BACKGROUND: Elderly patients with major depression have a poorer prognosis, are less responsive to treatment, and show greater functional decline compared with younger patients, highlighting the need for effective treatment. METHODS: This phase 3 double-blind study randomized patients with treatment-resistant depression (TRD) ≥65 years (1:1) to flexibly dosed esketamine nasal spray and new oral antidepressant (esketamine/antidepressant) or new oral antidepressant and placebo nasal spray (antidepressant/placebo). The primary endpoint was change in the Montgomery-Åsberg Depression Rating Scale (MADRS) from baseline to day 28. Analyses included a preplanned analysis by age (65-74 versus ≥75 years) and post-hoc analyses including age at depression onset. RESULTS: For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059. Adjusted mean (95% CI) difference for change in MADRS score between treatment groups was -4.9 (-8.96, -0.89; t = -2.4, df = 127; two-sided nominal p = 0.017) for patients 65 to 74 years versus -0.4 (-10.38, 9.50; t = -0.09, two-sided nominal p = 0.930) for those ≥75 years, and -6.1 (-10.33, -1.81; t = -2.8, df = 127; two-sided nominal p = 0.006) for patients with depression onset <55 years and 3.1 (-4.51, 10.80; t = 0.8, two-sided nominal p = 0.407) for those ≥55 years. Patients who rolled over into the long-term open-label study showed continued improvement with esketamine following 4 additional treatment weeks. CONCLUSIONS: Esketamine/antidepressant did not achieve statistical significance for the primary endpoint. Greater differences between treatment arms were seen for younger patients (65-74 years) and patients with earlier onset of depression (<55 years).

### R0139 — Day-28 adjusted MADRS contrast

Source: cache/esketamine-trd-madrs/records.json#/records/18/abstract. 

> BACKGROUND: Elderly patients with major depression have a poorer prognosis, are less responsive to treatment, and show greater functional decline compared with younger patients, highlighting the need for effective treatment. METHODS: This phase 3 double-blind study randomized patients with treatment-resistant depression (TRD) ≥65 years (1:1) to flexibly dosed esketamine nasal spray and new oral antidepressant (esketamine/antidepressant) or new oral antidepressant and placebo nasal spray (antidepressant/placebo). The primary endpoint was change in the Montgomery-Åsberg Depression Rating Scale (MADRS) from baseline to day 28. Analyses included a preplanned analysis by age (65-74 versus ≥75 years) and post-hoc analyses including age at depression onset. RESULTS: For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059. Adjusted mean (95% CI) difference for change in MADRS score between treatment groups was -4.9 (-8.96, -0.89; t = -2.4, df = 127; two-sided nominal p = 0.017) for patients 65 to 74 years versus -0.4 (-10.38, 9.50; t = -0.09, two-sided nominal p = 0.930) for those ≥75 years, and -6.1 (-10.33, -1.81; t = -2.8, df = 127; two-sided nominal p = 0.006) for patients with depression onset <55 years and 3.1 (-4.51, 10.80; t = 0.8, two-sided nominal p = 0.407) for those ≥55 years. Patients who rolled over into the long-term open-label study showed continued improvement with esketamine following 4 additional treatment weeks. CONCLUSIONS: Esketamine/antidepressant did not achieve statistical significance for the primary endpoint. Greater differences between treatment arms were seen for younger patients (65-74 years) and patients with earlier onset of depression (<55 years).

### R0140 — Day-28 adjusted MADRS contrast

Source: cache/esketamine-trd-madrs/records.json#/records/18/abstract. 

> BACKGROUND: Elderly patients with major depression have a poorer prognosis, are less responsive to treatment, and show greater functional decline compared with younger patients, highlighting the need for effective treatment. METHODS: This phase 3 double-blind study randomized patients with treatment-resistant depression (TRD) ≥65 years (1:1) to flexibly dosed esketamine nasal spray and new oral antidepressant (esketamine/antidepressant) or new oral antidepressant and placebo nasal spray (antidepressant/placebo). The primary endpoint was change in the Montgomery-Åsberg Depression Rating Scale (MADRS) from baseline to day 28. Analyses included a preplanned analysis by age (65-74 versus ≥75 years) and post-hoc analyses including age at depression onset. RESULTS: For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059. Adjusted mean (95% CI) difference for change in MADRS score between treatment groups was -4.9 (-8.96, -0.89; t = -2.4, df = 127; two-sided nominal p = 0.017) for patients 65 to 74 years versus -0.4 (-10.38, 9.50; t = -0.09, two-sided nominal p = 0.930) for those ≥75 years, and -6.1 (-10.33, -1.81; t = -2.8, df = 127; two-sided nominal p = 0.006) for patients with depression onset <55 years and 3.1 (-4.51, 10.80; t = 0.8, two-sided nominal p = 0.407) for those ≥55 years. Patients who rolled over into the long-term open-label study showed continued improvement with esketamine following 4 additional treatment weeks. CONCLUSIONS: Esketamine/antidepressant did not achieve statistical significance for the primary endpoint. Greater differences between treatment arms were seen for younger patients (65-74 years) and patients with earlier onset of depression (<55 years).

### R0141 — Day-28 adjusted MADRS contrast

Source: cache/esketamine-trd-madrs/records.json#/records/18/abstract. 

> BACKGROUND: Elderly patients with major depression have a poorer prognosis, are less responsive to treatment, and show greater functional decline compared with younger patients, highlighting the need for effective treatment. METHODS: This phase 3 double-blind study randomized patients with treatment-resistant depression (TRD) ≥65 years (1:1) to flexibly dosed esketamine nasal spray and new oral antidepressant (esketamine/antidepressant) or new oral antidepressant and placebo nasal spray (antidepressant/placebo). The primary endpoint was change in the Montgomery-Åsberg Depression Rating Scale (MADRS) from baseline to day 28. Analyses included a preplanned analysis by age (65-74 versus ≥75 years) and post-hoc analyses including age at depression onset. RESULTS: For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059. Adjusted mean (95% CI) difference for change in MADRS score between treatment groups was -4.9 (-8.96, -0.89; t = -2.4, df = 127; two-sided nominal p = 0.017) for patients 65 to 74 years versus -0.4 (-10.38, 9.50; t = -0.09, two-sided nominal p = 0.930) for those ≥75 years, and -6.1 (-10.33, -1.81; t = -2.8, df = 127; two-sided nominal p = 0.006) for patients with depression onset <55 years and 3.1 (-4.51, 10.80; t = 0.8, two-sided nominal p = 0.407) for those ≥55 years. Patients who rolled over into the long-term open-label study showed continued improvement with esketamine following 4 additional treatment weeks. CONCLUSIONS: Esketamine/antidepressant did not achieve statistical significance for the primary endpoint. Greater differences between treatment arms were seen for younger patients (65-74 years) and patients with earlier onset of depression (<55 years).

### R0142 — Day-28 adjusted MADRS contrast

Source: cache/esketamine-trd-madrs/records.json#/records/18/abstract. 

> BACKGROUND: Elderly patients with major depression have a poorer prognosis, are less responsive to treatment, and show greater functional decline compared with younger patients, highlighting the need for effective treatment. METHODS: This phase 3 double-blind study randomized patients with treatment-resistant depression (TRD) ≥65 years (1:1) to flexibly dosed esketamine nasal spray and new oral antidepressant (esketamine/antidepressant) or new oral antidepressant and placebo nasal spray (antidepressant/placebo). The primary endpoint was change in the Montgomery-Åsberg Depression Rating Scale (MADRS) from baseline to day 28. Analyses included a preplanned analysis by age (65-74 versus ≥75 years) and post-hoc analyses including age at depression onset. RESULTS: For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059. Adjusted mean (95% CI) difference for change in MADRS score between treatment groups was -4.9 (-8.96, -0.89; t = -2.4, df = 127; two-sided nominal p = 0.017) for patients 65 to 74 years versus -0.4 (-10.38, 9.50; t = -0.09, two-sided nominal p = 0.930) for those ≥75 years, and -6.1 (-10.33, -1.81; t = -2.8, df = 127; two-sided nominal p = 0.006) for patients with depression onset <55 years and 3.1 (-4.51, 10.80; t = 0.8, two-sided nominal p = 0.407) for those ≥55 years. Patients who rolled over into the long-term open-label study showed continued improvement with esketamine following 4 additional treatment weeks. CONCLUSIONS: Esketamine/antidepressant did not achieve statistical significance for the primary endpoint. Greater differences between treatment arms were seen for younger patients (65-74 years) and patients with earlier onset of depression (<55 years).

### R0143 — Genotype-specific raw MADRS changes esketamine

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114. 

> ted on either day 2 ( Table 2 ; Figure 1 ) or day 28 ( Table 2 ; Figure 2 ). The mean (SD) reduction from baseline in MADRS total score was −9.62 (10.14) (AA genotype) and −10.49 (10.79) (AG/GG genotype) on day 2 and −20.95 (12.75) (AA genotype) and −23.16 (13.53) (AG/GG genotype) on day 28. Table 2. Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score Esketamine + AD AD + placebo Minor allele frequency n Slope P value R 2 partial Minor allele effect n Slope P value R 2 partial 

### R0144 — Genotype-specific raw MADRS changes placebo

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114. 

>  a significant interaction on day 2 ( P < .05) but not on day 28 ( P = .52). The mean (SD) reduction from baseline in MADRS total score was −4.37 (8.08) (AA genotype) and −11.28 (10.44) (AG/GG genotype) on day 2 and −15.75 (14.67) (AA genotype) and −20.77 (14.59) (AG/GG genotype) on day 28. When broken down by trial, further post hoc testing showed that the placebo associations with rs1799971 (A118G) polymorphism were largely driven by 1 of the 2 cohorts. In TRANSFORM-2, at day 2 visit, patients treated with AD + placebo responded with an additional improvement of 10.5

### R0145 — Published weight estimates (distinct from raw registry)

Source: cache/semaglutide-obesity-weight/records.json#/records/118/abstract. 

> BACKGROUND: Obesity is a global health challenge with few pharmacologic options. Whether adults with obesity can achieve weight loss with once-weekly semaglutide at a dose of 2.4 mg as an adjunct to lifestyle intervention has not been confirmed. METHODS: In this double-blind trial, we enrolled 1961 adults with a body-mass index (the weight in kilograms divided by the square of the height in meters) of 30 or greater (≥27 in persons with ≥1 weight-related coexisting condition), who did not have diabetes, and randomly assigned them, in a 2:1 ratio, to 68 weeks of treatment with once-weekly subcutaneous semaglutide (at a dose of 2.4 mg) or placebo, plus lifestyle intervention. The coprimary end points were the percentage change in body weight and weight reduction of at least 5%. The primary estimand (a precise description of the treatment effect reflecting the objective of the clinical trial) assessed effects regardless of treatment discontinuation or rescue interventions. RESULTS: The mean change in body weight from baseline to week 68 was -14.9% in the semaglutide group as compared with -2.4% with placebo, for an estimated treatment difference of -12.4 percentage points (95% confidence interval [CI], -13.4 to -11.5; P<0.001). More participants in the semaglutide group than in the placebo group achieved weight reductions of 5% or more (1047 participants [86.4%] vs. 182 [31.5%]), 10% or more (838 [69.1%] vs. 69 [12.0%]), and 15% or more (612 [50.5%] vs. 28 [4.9%]) at week 68 (P<0.001 for all three comparisons of odds). The change in body weight from baseline to week 68 was -15.3 kg in the semaglutide group as compared with -2.6 kg in the placebo group (estimated treatment difference, -12.7 kg; 95% CI, -13.7 to -11.7). Participants who received semaglutide had a greater improvement with respect to cardiometabolic risk factors and a greater increase in participant-reported physical functioning from baseline than those who received placebo. Nausea and diarrhea were the most common adverse events with semaglutide; they were typically transient and mild-to-moderate in severity and subsided with time. More participants in the semaglutide group than in the placebo group discontinued treatment owing to gastrointestinal events (59 [4.5%] vs. 5 [0.8%]). CONCLUSIONS: In participants with overweight or obesity, 2.4 mg of semaglutide once weekly plus lifestyle intervention was associated with sustained, clinically relevant reduction in body weight. (Funded by Novo Nordisk; STEP 1 ClinicalTrials.gov number, NCT03548935).

### R0146 — Published weight estimates (distinct from raw registry)

Source: cache/semaglutide-obesity-weight/records.json#/records/117/abstract. 

> IMPORTANCE: Weight loss improves cardiometabolic risk factors in people with overweight or obesity. Intensive lifestyle intervention and pharmacotherapy are the most effective noninvasive weight loss approaches. OBJECTIVE: To compare the effects of once-weekly subcutaneous semaglutide, 2.4 mg vs placebo for weight management as an adjunct to intensive behavioral therapy with initial low-calorie diet in adults with overweight or obesity. DESIGN, SETTING, AND PARTICIPANTS: Randomized, double-blind, parallel-group, 68-week, phase 3a study (STEP 3) conducted at 41 sites in the US from August 2018 to April 2020 in adults without diabetes (N = 611) and with either overweight (body mass index ≥27) plus at least 1 comorbidity or obesity (body mass index ≥30). INTERVENTIONS: Participants were randomized (2:1) to semaglutide, 2.4 mg (n = 407) or placebo (n = 204), both combined with a low-calorie diet for the first 8 weeks and intensive behavioral therapy (ie, 30 counseling visits) during 68 weeks. MAIN OUTCOMES AND MEASURES: The co-primary end points were percentage change in body weight and the loss of 5% or more of baseline weight by week 68. Confirmatory secondary end points included losses of at least 10% or 15% of baseline weight. RESULTS: Of 611 randomized participants (495 women [81.0%], mean age 46 years [SD, 13], body weight 105.8 kg [SD, 22.9], and body mass index 38.0 [SD, 6.7]), 567 (92.8%) completed the trial, and 505 (82.7%) were receiving treatment at trial end. At week 68, the estimated mean body weight change from baseline was -16.0% for semaglutide vs -5.7% for placebo (difference, -10.3 percentage points [95% CI, -12.0 to -8.6]; P < .001). More participants treated with semaglutide vs placebo lost at least 5% of baseline body weight (86.6% vs 47.6%, respectively; P < .001). A higher proportion of participants in the semaglutide vs placebo group achieved weight losses of at least 10% or 15% (75.3% vs 27.0% and 55.8% vs 13.2%, respectively; P < .001). Gastrointestinal adverse events were more frequent with semaglutide (82.8%) vs placebo (63.2%). Treatment was discontinued owing to these events in 3.4% of semaglutide participants vs 0% of placebo participants. CONCLUSIONS AND RELEVANCE: Among adults with overweight or obesity, once-weekly subcutaneous semaglutide compared with placebo, used as an adjunct to intensive behavioral therapy and initial low-calorie diet, resulted in significantly greater weight loss during 68 weeks. Further research is needed to assess the durability of these findings. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT03611582.

### R0147 — Published weight estimates (distinct from raw registry)

Source: cache/semaglutide-obesity-weight/records.json#/records/32/abstract. 

> BACKGROUND: Consistent with WHO recommendations, obesity is defined as BMI ≥25 kg/m2 in many Asian populations because of increased health risks at lower BMIs than in other populations. We aimed to investigate the efficacy and safety of once-weekly subcutaneous semaglutide 2·4 mg versus placebo in an Asian population with BMI ≥25 kg/m2, together with lifestyle interventions. METHODS: STEP 11 was a 44-week, randomised, double-blind, placebo-controlled, phase 3 trial conducted at 12 clinical sites in South Korea and Thailand. Adults (aged ≥18 years in Thailand and ≥19 years in South Korea) with obesity (BMI ≥25 kg/m2) of Asian descent, without diabetes, were randomly assigned 2:1 with a computer-generated sequence and block randomisation to once-weekly subcutaneous semaglutide 2·4 mg or placebo, with a reduced-calorie diet and increased physical activity. Participants, care providers, investigators, and assessors were masked to allocation. Coprimary endpoints, measured in all randomly assigned participants by intention to treat, were percentage bodyweight change and the proportion of participants reaching ≥5% bodyweight reduction. Confirmatory secondary endpoints were the proportion of participants with ≥10% and ≥15% bodyweight reductions and change in waist circumference. Safety was assessed via the assessment of adverse events in all participants who received at least one dose of semaglutide or placebo. This trial was registered at ClinicalTrials.gov (NCT04998136). FINDINGS: Between Aug 15, 2022, and Nov 20, 2023, 150 participants were randomly assigned (101 to semaglutide 2·4 mg and 49 to placebo). Six (6%) in the semaglutide group and two (4%) in the placebo group discontinued treatment before week 44. 111 (74%) were female and 39 (26%) male, with a mean age of 39 years (SD 11), mean bodyweight of 83·8 kg (18·1), and mean BMI of 31·3 kg/m2 (5·2). At week 44, mean change in bodyweight was -16·0% (SE 0·7) in the semaglutide 2·4 mg group versus -3·1% (0·9) in the placebo group (p<0·0001), and a greater proportion of participants reached bodyweight reductions of ≥5% (96 [96%] vs 12 [25%]; p<0·0001), ≥10% (78 [78%] vs 5 [10%]; p<0·0001), and ≥15% (53 [53·0%] vs 2 [4·2%]; p<0·0001) in the semaglutide 2·4 mg group. Mean change in waist circumference was -11·9 cm (SE 0·7) with semaglutide versus -3·0 cm (1·0) with placebo (p<0·0001). Adverse events were reported by 90 (89%) of 101 participants in the semaglutide 2·4 mg group and 38 (78%) of 49 participants in the placebo group, with 13 (13%) reporting serious adverse events in the semaglutide 2·4 mg group versus four (8%) in the placebo group. Gastrointestinal adverse events were the most common adverse events in participants in the semaglutide group. INTERPRETATION: In this Asian population with obesity (BMI ≥25·0 kg/m2), once-weekly semaglutide 2·4 mg significantly reduced bodyweight and was well tolerated. The results have meaningful clinical and policy implications for Asian countries, where lower BMI thresholds are used to define obesity compared with other populations. The efficacy and safety of semaglutide 2·4 mg support its inclusion in local treatment guidelines. These findings might also inform reimbursement policies and national obesity strategies, highlighting the importance of population-specific approaches. FUNDING: Novo Nordisk. TRANSLATIONS: For the Thai and Korean translations of the abstract see Supplementary Materials section.

## Additional subgroup numeric results

| Result | Trial / population | Raw or adjusted / n | Named values |
|---|---|---|---|
| R0148 China subgroup Day 28 adjusted contrast | PMID 37025256; China subgroup of NCT03434041 | ADJUSTED MMRM; {"subgroup_N": 222, "model_arm_n": "NOT_STATED"} | {"MD": -0.7, "CI95": [-3.35, 1.94]} |
| R0149 China subgroup Day 2 adjusted contrast | PMID 37025256; China subgroup of NCT03434041 | ADJUSTED MMRM; "NOT_STATED outcome/model-specific n" | {"MD": -2.6, "CI95": [-4.64, -0.6]} |
| R0150 China follow-up week 8 absolute means | PMID 37025256; China patients continuing to follow-up; prior randomized groups | RAW/ADJUSTED NOT_STATED; "NOT_STATED week-8 n" | {"prior_esketamine_mean": 20.5, "prior_placebo_mean": 24.6} |
| R0151 Day-2 genotype narrative comparison | PMID 31109201; TRANSFORM-2 placebo/AD subgroup, G-allele carriers/noncarriers | NOT_STATED for these narrative additional-improvement estimates; "NOT_STATED genotype/timepoint n" | {"G_carrier_additional_improvement": 10.53, "G_carrier_p": "<.001", "noncarrier_comparison": 1.39, "noncarrier_p": 0.53} |

### R0148

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[31]. 

> The mean (SD) MADRS total score at baseline was 36.5 (5.21) for the esketamine plus AD group and 35.9 (4.50) for the AD plus placebo group, and at Day 28 was 26.5 (10.33) and 27.9 (10.04), respectively ( Table 2 ). The mean change (SD) in MADRS total score from baseline at Day 28 was -10.1 (10.80) for the esketamine plus AD group and −8.1 (10.26) for the AD plus placebo group. The least squares (LS) mean difference (95% confidence interval [CI]) at Day 28 between the two treatment groups analyzed by MMRM was −2.0 (−4.64, 0.55); this difference was not statistically significant (2-sided p = 0.123). In the China population (n = 222), the LS mean difference (95% CI) was -0.7 (−3.35, 1.94). The MADRS change over time in the overall population and China population during the double-blind treatment phase is shown in Figure 2 . China patients continued to the 8-week follow-up phase, during which the mean MADRS total score continuously improved. Patients who were previously on esketamine showed a larger reduction in MADRS total score compared with those who were previously on placebo, with a mean score at week 8 of 20.5 versus 24.6, respectively ( Figure S1 ). Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor. Figure 2 LS mean change in MADRS total score over time a in the double-blind treatment phase in the overall population ( A ) and China population ( B ). Note : a LS mean and SE were based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; ESK, esketamine; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.


### R0149

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[36]. 

> The 2 key secondary endpoints were designed to assess the effect of esketamine on the rapid reduction of depressive symptoms and on patient-reported functioning and associated disability. Based on the predefined testing sequence of the primary and key secondary endpoints, the change from baseline in MADRS total score at 24 hours (Day 2) and the change from baseline in SDS total score at Day 28 could not be formally tested. The change in MADRS total score at 24 hours numerically favored esketamine plus AD over AD plus placebo. Using an MMRM model, the LS mean difference (95% CI) between the 2 treatment groups was −3.3 (−5.33, −1.33) ( Table 3 ). In the China population, the LS mean difference (95% CI) between esketamine plus AD and AD plus placebo was −2.6 (−4.64, −0.60). The LS mean difference (95% CI) of change in SDS total score from baseline to Day 28 between the 2 treatment groups was −1.0 (−2.96, 0.97) based on MMRM analysis ( Table 3 ). In the China population, the LS mean difference (95% CI) between the 2 treatment groups was −0.1 (−2.09, 1.93). Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.


### R0150

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[31]. Follow-up means are not Day-28 randomized induction contrasts.

> The mean (SD) MADRS total score at baseline was 36.5 (5.21) for the esketamine plus AD group and 35.9 (4.50) for the AD plus placebo group, and at Day 28 was 26.5 (10.33) and 27.9 (10.04), respectively ( Table 2 ). The mean change (SD) in MADRS total score from baseline at Day 28 was -10.1 (10.80) for the esketamine plus AD group and −8.1 (10.26) for the AD plus placebo group. The least squares (LS) mean difference (95% confidence interval [CI]) at Day 28 between the two treatment groups analyzed by MMRM was −2.0 (−4.64, 0.55); this difference was not statistically significant (2-sided p = 0.123). In the China population (n = 222), the LS mean difference (95% CI) was -0.7 (−3.35, 1.94). The MADRS change over time in the overall population and China population during the double-blind treatment phase is shown in Figure 2 . China patients continued to the 8-week follow-up phase, during which the mean MADRS total score continuously improved. Patients who were previously on esketamine showed a larger reduction in MADRS total score compared with those who were previously on placebo, with a mean score at week 8 of 20.5 versus 24.6, respectively ( Figure S1 ). Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor. Figure 2 LS mean change in MADRS total score over time a in the double-blind treatment phase in the overall population ( A ) and China population ( B ). Note : a LS mean and SE were based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; ESK, esketamine; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.


### R0151

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[76]. Quote retained verbatim; do not reinterpret as randomized treatment effect.

> In TRANSFORM-2, at day 2 visit, patients treated with AD + placebo responded with an additional improvement of 10.53 points on MADRS total scores ( P < .001) for the G-allele carriers compared with 1.39 ( P = .53) for noncarriers.


## Complete source-context inventory

Each number in each quoted block also has a literal, offset and local wording in JSON. These context inventories include eligibility thresholds, study-design assumptions, references and non-target endpoints; they must not be treated as a dataset of target effects. Quarantine labels take precedence over the class named in a misassociated source.

### esketamine-trd-madrs — PMID 37025256

Pinned served row:
~~~json
{
  "id": "PMID 37025256",
  "mean1": -10.1,
  "sd1": 10.8,
  "nc1": 109,
  "mean2": -8.1,
  "sd2": 10.26,
  "nc2": 106,
  "source": "ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery Asberg Depression Rating Scale (MAD' mean -10.1 (SD 10.8, n=109) [Intranasal Esketamine ] vs -8.1 (SD 10.26, n=106) [Intranasal Placebo + O] Units on a Scale — population: Full analysis set included all randomized participants who received a least 1 do",
  "timeframe": "Baseline up to end of the double-blind treatment phase (Day 28)"
}
~~~

#### E0001 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/4/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **PRIMARY_REPORT**.

Population: full analysis set (FAS/mITT). Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> PURPOSE: This Phase 3, multicenter study (NCT03434041) was conducted in primarily Chinese patients with treatment-resistant depression (TRD) to support the registration of esketamine nasal spray in China. PATIENTS AND METHODS: This randomized, double-blind, active-controlled study was conducted in China and the United States (US) in patients with TRD (single or recurrent episode). Eligible patients were randomized 1:1 to receive intranasal esketamine or matching placebo, each in conjunction with a newly initiated oral antidepressant (AD; duloxetine, escitalopram, sertraline, and venlafaxine extended release) (ie, esketamine plus AD or AD plus placebo). The primary endpoint, change from baseline in Montgomery-Åsberg Depression Rating Scale (MADRS) total score at Day 28, was analyzed using a mixed-effects model for repeated measures. Secondary endpoints including safety were also evaluated. RESULTS: Of 252 randomized patients (China, 224; US, 28), 214 completed the double-blind treatment phase. The difference between treatment groups at Day 28 was not statistically significant (difference in least-square means [95% CI]: -2.0 [-4.64, 0.55]; 2-sided p = 0.123). However, esketamine plus AD demonstrated a clinically meaningful treatment difference compared with AD plus placebo in MADRS total score at 24 hours after first dose for the study overall population and China sub-population (difference in least-square mean [95% CI]: -3.3 [-5.33, -1.33] and -2.6 [-4.64, -0.60], respectively). No new safety signals were observed. CONCLUSION: Esketamine plus AD was not statistically superior to AD plus placebo in improving depressive symptoms in TRD patients at Day 28. Rapid reduction in depressive symptoms within 24 hours was observed for TRD patients treated with esketamine plus AD in the overall population and China sub-population. Safety was consistent with the established safety profile of esketamine.

#### E0002 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "109".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupId": "OG000", "value": "-10.1", "spread": "10.80"}

#### E0003 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "106".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupId": "OG001", "value": "-8.1", "spread": "10.26"}

#### E0004 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupIds": ["OG000"], "nonInferiorityType": "SUPERIORITY", "pValue": "0.123", "pValueComment": "2-sided", "statisticalMethod": "Mixed-effects Model for Repeated Measure", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-2.0", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-4.64", "ciUpperLimit": "0.55"}

#### E0005 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/1/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "123".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupId": "OG000", "value": "-8.0", "spread": "9.01"}

#### E0006 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/1/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "125".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupId": "OG001", "value": "-4.4", "spread": "7.66"}

#### E0007 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/1/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupIds": ["OG000"], "nonInferiorityType": "SUPERIORITY", "paramType": "Difference of LS Means", "paramValue": "-3.3", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-5.33", "ciUpperLimit": "-1.33"}

#### E0008 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[2]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> This randomized, double-blind, active-controlled study was conducted in China and the United States (US) in patients with TRD (single or recurrent episode). Eligible patients were randomized 1:1 to receive intranasal esketamine or matching placebo, each in conjunction with a newly initiated oral antidepressant (AD; duloxetine, escitalopram, sertraline, and venlafaxine extended release) (ie, esketamine plus AD or AD plus placebo). The primary endpoint, change from baseline in Montgomery-Åsberg Depression Rating Scale (MADRS) total score at Day 28, was analyzed using a mixed-effects model for repeated measures. Secondary endpoints including safety were also evaluated.

#### E0009 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[3]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Of 252 randomized patients (China, 224; US, 28), 214 completed the double-blind treatment phase. The difference between treatment groups at Day 28 was not statistically significant (difference in least-square means [95% CI]: −2.0 [−4.64, 0.55]; 2-sided p = 0.123). However, esketamine plus AD demonstrated a clinically meaningful treatment difference compared with AD plus placebo in MADRS total score at 24 hours after first dose for the study overall population and China sub-population (difference in least-square mean [95% CI]: −3.3 [−5.33, −1.33] and −2.6 [−4.64, −0.60], respectively). No new safety signals were observed.

#### E0010 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[7]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In a pivotal, phase 3, global, multicenter study (TRANSFORM-2, NCT02418585 ), esketamine nasal spray (either 56 or 84 mg) plus a newly initiated oral AD showed a statistically significant and clinically relevant improvement in depressive symptoms based on change in Montgomery-Åsberg Depression Rating Scale (MADRS) 16 total score after 28 days in adult patients with TRD versus oral AD plus placebo, and clinically meaningful benefit 24 hours after the first dose. 17 This phase 3, multicenter study ( NCT03434041 ), with almost identical design features as TRANSFORM-2, 17 evaluated the efficacy and safety of flexibly dosed intranasal esketamine (56 or 84 mg) plus a newly initiated oral AD for a 4-week treatment period in mainly Chinese adult patients with TRD to support regulatory requirements for registration of intranasal esketamine in China.

#### E0011 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[11]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The study population included adults aged 18–64 years, who met the Diagnostic and Statistical Manual of Mental Disorders, 5th Edition (DSM-5) criteria for single-episode MDD or recurrent MDD without psychotic features, based on clinical assessment and confirmed by the Mini International Neuropsychiatric Interview (MINI). TRD was defined as lack of clinically meaningful improvement after treatment with at least 2 different ADs at adequate dose and duration (≥6 weeks) in the current depressive episode. At the start of the 4-week screening/prospective observational phase, patients were required to have had documented nonresponse (≤25% improvement) to treatment with 1–5 oral ADs at adequate dose and duration based on the Massachusetts General Hospital – Antidepressant Treatment Response Questionnaire (MGH-ATRQ) for the current depressive episode and confirmed by documented records. In addition, patients were currently receiving a different oral AD (on the MGH-ATRQ), to which they had been adherent for at least the previous 2 weeks at or above the minimum therapeutic dose. Patients who were non-responders to their current oral AD(s) were eligible for randomization if all other entry criteria were met. Nonresponse at the end of the screening/prospective observational phase was defined as ≤25% improvement in the MADRS total score from Week 1 to Week 4 and a MADRS total score of ≥28 on Week 2 and Week 4 during the screening/prospective observational phase.

#### E0012 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[16]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Efficacy assessments included (1) MADRS, a clinician-rated measure of depression severity, 16 and scored by independent, remote (by phone), blinded MADRS raters to ensure an unbiased efficacy evaluation; (2) Sheehan Disability Scale (SDS), a patient-reported measure of functional impairment and associated disability; 18 , 19 (3) Clinical Global Impression of Severity (CGI-S), a clinician-rated measure of illness severity; 20 (4) 7-Item Generalized Anxiety Disorder Scale (GAD-7), a patient-reported measure of anxiety symptoms; 21 and (5) 5-level EQ-5D (EQ-5D-5L), a patient-reported measure of health outcome. 22

#### E0013 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[17]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary endpoint was change in MADRS total score (7-day recall) from baseline to Day 28 (end of double-blind treatment phase). Two key secondary endpoints were (1) change from baseline in MADRS total score (24-hour recall) at 24 hours post first dose (Day 2) 23 and (2) change from baseline in SDS total score at Day 28. Other secondary endpoints were change from baseline to Day 28 in CGI-S, GAD-7, and EQ-5D-5L, respectively.

#### E0014 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[20]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Planned sample size was calculated assuming a treatment difference for the double-blind treatment phase of 6.5 points in MADRS total score between esketamine and the active comparator, a standard deviation (SD) of 12, a 1-sided significance level of 0.025, and a dropout rate of 25%. The treatment difference and SD used in this calculation were based on results from a Phase 2 study evaluating intranasal esketamine for TRD 27 and on clinical judgement. Approximately 117 patients were to be randomized to each treatment group to achieve greater than 90% power, with a sample size of 105 Chinese patients per treatment arm (n = 210 total) plus 12 non-Chinese patients per treatment arm (n = 24 total).

#### E0015 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[23]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> For the primary efficacy analysis, change from baseline in MADRS total score at Day 28 in the double-blind phase was analyzed using a mixed-effects model for repeated measures (MMRM) based on observed case data. The model included the baseline MADRS total score as a covariate and treatment, country, class of AD (SNRI or SSRI), day, and day-by-treatment interaction as fixed effects. The key secondary endpoints and other secondary endpoint (ie, CGI-S) were analyzed using a model similar to the one described for the primary efficacy analysis. The change from baseline in GAD-7 total score at Day 28 was analyzed using an analysis of covariance (ANCOVA) model with treatment, country, and class of AD (SNRI or SSRI) as factors, and the baseline score as the covariate. Descriptive statistics of actual values and changes from baseline by treatment group were provided for EQ-5D-5L.

#### E0016 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[27]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Esketamine plus AD and AD plus placebo groups were comparable based on demographic and baseline clinical characteristics ( Table 1 , Table S2 ), with similar mean age (36.9 vs 37.8 years), gender mix (male: 53.2% vs 56.3%), disease severity (mean MADRS total scores: 36.5 vs 35.9), and mean duration of the current depressive episode (225.3 vs 218.6 weeks) ( Table 1 ). Most patients (≥81%) in each treatment group received intranasal study medication on all 8 dosing days during the double-blind phase. Most patients (≥85%) in each group were exposed to intranasal study medication for at least 22 days. Table 1 Demographic and Baseline Clinical Characteristics a Characteristic Esketamine Plus AD (n=124) AD Plus Placebo (n=126) Total (n=250) Age, years – mean (SD) 36.9 (12.04) 37.8 (12.36) 37.3 (12.19) Sex – n (%) Male 66 (53.2) 71 (56.3) 137 (54.8) Female 58 (46.8) 55 (43.7) 113 (45.2) Race – n (%) Asian 110 (88.7) 112 (88.9) 222 (88.8) White 12 (9.7) 9 (7.1) 21 (8.4) Black or African American 1 (0.8) 4 (3.2) 5 (2.0) Multiple 1 (0.8) 0 (0) 1 (0.4) Not reported 0 (0) 1 (0.8) 1 (0.4) Country – n (%) China 110 (88.7) 112 (88.9) 222 (88.8) United States 14 (11.3) 14 (11.1) 28 (11.2) BMI, calculated as kg/m 2 – mean (SD) 24.8 (4.98) 24.2 (4.32) 24.5 (4.66) Employment status – n (%) b Any type of employment 86 (69.4) 79 (62.7) 165 (66.0) Any type of unemployment 27 (21.8) 38 (30.2) 65 (26.0) Other 11 (8.9) 9 (7.1) 20 (8.0) Age when diagnosed with MDD, years – mean (SD) 27.2 (11.53) 28.2 (11.87) 27.7 (11.69) Duration of current episode, weeks – mean (SD) 225.3 (317.75) 218.6 (274.20) 221.9 (296.02) MADRS total score – mean (SD) 36.5 (5.21) 35.9 (4.50) 36.2 (4.87) CGI-S – mean (SD) 5.1 (0.61) 5.2 (0.68) 5.1 (0.65) CGI-S category – n (%) Mildly ill 1 (0.8) 1 (0.8) 2 (0.8) Moderately ill 15 (12.1) 16 (12.7) 31 (12.4) Markedly ill 81 (65.3) 74 (58.7) 155 (62.0) Severely ill 27 (21.8) 33 (26.2) 60 (24.0) Most extremely ill 0 (0) 2 (1.6) 2 (0.8) Class of oral AD – n (%) SNRI 68 (54.8) 69 (54.8) 137 (54.8) SSRI 56 (45.2) 57 (45.2) 113 (45.2) Oral AD – n (%) Duloxetine 36 (29.0) 40 (31.7) 76 (30.4) Escitalopram 30 (24.2) 34 (27.0) 64 (25.6) Venlafaxine extended release 31 (25.0) 29 (23.0) 60 (24.0) Sertraline 27 (21.8) 23 (18.3) 50 (20.0) Number of previous treatment failures in current episode – n (%) c 1 38 (30.6) 38 (30.2) 76 (30.4) 2 46 (37.1) 47 (37.3) 93 (37.2) 3 29 (23.4) 31 (24.6) 60 (24.0) 4 7 (5.6) 8 (6.3) 15 (6.0) 5 4 (3.2) 2 (1.6) 6 (2.4) Notes : a Data generated from the efficacy analysis set. b Any type of employment includes any category containing “employed”, sheltered work, housewife or dependent husband, and student; any type of unemployment includes any category containing “unemployed”; “other” includes retired or no information available. c Number of AD medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained from MGH-ATRQ at screening. Abbreviations : AD, antidepressant; BMI, body mass index; CGI-S, Clinical Global Impression of Severity; MADRS, Montgomery-Åsberg Depression Rating Scale; MDD, major depressive disorder; MGH-ATRQ, Massachusetts General Hospital – Antidepressant Treatment Response Questionnaire; SD, standard deviation; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0017 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[30]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Abbreviations : AD, antidepressant; BMI, body mass index; CGI-S, Clinical Global Impression of Severity; MADRS, Montgomery-Åsberg Depression Rating Scale; MDD, major depressive disorder; MGH-ATRQ, Massachusetts General Hospital – Antidepressant Treatment Response Questionnaire; SD, standard deviation; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0018 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[31]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean (SD) MADRS total score at baseline was 36.5 (5.21) for the esketamine plus AD group and 35.9 (4.50) for the AD plus placebo group, and at Day 28 was 26.5 (10.33) and 27.9 (10.04), respectively ( Table 2 ). The mean change (SD) in MADRS total score from baseline at Day 28 was -10.1 (10.80) for the esketamine plus AD group and −8.1 (10.26) for the AD plus placebo group. The least squares (LS) mean difference (95% confidence interval [CI]) at Day 28 between the two treatment groups analyzed by MMRM was −2.0 (−4.64, 0.55); this difference was not statistically significant (2-sided p = 0.123). In the China population (n = 222), the LS mean difference (95% CI) was -0.7 (−3.35, 1.94). The MADRS change over time in the overall population and China population during the double-blind treatment phase is shown in Figure 2 . China patients continued to the 8-week follow-up phase, during which the mean MADRS total score continuously improved. Patients who were previously on esketamine showed a larger reduction in MADRS total score compared with those who were previously on placebo, with a mean score at week 8 of 20.5 versus 24.6, respectively ( Figure S1 ). Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor. Figure 2 LS mean change in MADRS total score over time a in the double-blind treatment phase in the overall population ( A ) and China population ( B ). Note : a LS mean and SE were based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; ESK, esketamine; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0019 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[32]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase

#### E0020 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[33]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine.

#### E0021 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[34]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0022 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[35]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> LS mean change in MADRS total score over time a in the double-blind treatment phase in the overall population ( A ) and China population ( B ).

#### E0023 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[36]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The 2 key secondary endpoints were designed to assess the effect of esketamine on the rapid reduction of depressive symptoms and on patient-reported functioning and associated disability. Based on the predefined testing sequence of the primary and key secondary endpoints, the change from baseline in MADRS total score at 24 hours (Day 2) and the change from baseline in SDS total score at Day 28 could not be formally tested. The change in MADRS total score at 24 hours numerically favored esketamine plus AD over AD plus placebo. Using an MMRM model, the LS mean difference (95% CI) between the 2 treatment groups was −3.3 (−5.33, −1.33) ( Table 3 ). In the China population, the LS mean difference (95% CI) between esketamine plus AD and AD plus placebo was −2.6 (−4.64, −0.60). The LS mean difference (95% CI) of change in SDS total score from baseline to Day 28 between the 2 treatment groups was −1.0 (−2.96, 0.97) based on MMRM analysis ( Table 3 ). In the China population, the LS mean difference (95% CI) between the 2 treatment groups was −0.1 (−2.09, 1.93). Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0024 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[38]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement.

#### E0025 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[39]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0026 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[56]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> This active-controlled study investigating the efficacy and safety of esketamine versus placebo, each in combination with a newly initiated oral AD, in predominantly Chinese patients with TRD did not achieve statistical significance for the primary endpoint, change in MADRS total score from baseline to Day 28, although a 2-point difference was observed. The average 2-point difference from placebo at endpoint in short-term studies has been used to establish the clinical relevance of an AD against placebo. 28 , 29 Although the first key secondary endpoint could not be formally evaluated due to the prespecified testing hierarchy, esketamine-treated patients experienced clinically important, rapid reduction in depressive symptoms within 24 hours after the first intranasal dose (LS mean difference [95% CI]: −3.3 [−5.33, −1.33]). A rapid reduction in depressive symptoms was also observed in the China population (LS mean difference [95% CI]: −2.6 [−4.64, −0.60]). These data are consistent with previous findings from esketamine studies for TRD and MDD with acute suicidal ideation or behavior, 30 , 31 and reflect the characteristics of a rapid-acting antidepressant (ie, efficacy generally demonstrated within hours to 1 week). 32 Efficacy data in this study are in contrast to the effects of standard oral ADs, which typically require several weeks before conferring clinical benefit.

#### E0027 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[57]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In contrast to a previous report in a global population, 17 this study conducted in a primarily Chinese population did not demonstrate a therapeutic effect after 4-week double-blind treatment with esketamine. The observed 2-point difference in MADRS total score was driven primarily by data from US patients. A smaller magnitude of change was observed in the China subgroup compared with the US subgroup and global phase 3 TRD studies. 17 , 33

#### E0028 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[59]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The use of remote blinded independent raters to administer the MADRS assessment by telephone was hypothesized as a potential contributing factor. Since independent remote raters did not know individual subjects and their baseline characteristics well and were unable to see the participants in order to judge affect or change in affect during the rating process, the use of independent remote raters may have reduced the sensitivity of detecting change in depressive symptoms. Remote independent rating had not been used in prior MDD registrational trials in China. According to an earlier pilot study in the China population, 34 remote raters tended to rate patients slightly higher at the same visit than site-based raters, especially when patients demonstrated lower overall symptom severity. However, this finding was not observed in another similar pilot study in a US population, which demonstrated that remote blinded ratings were comparable to site-based ratings in this US population with TRD at all timepoints. 35 This may be partly due to cultural and ethnic differences in a Western versus Chinese population in how patients express their depressive symptoms, especially to a stranger by telephone.

#### E0029 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In addition, the hypothesis that remote rating may be less sensitive to change in depression may be supported by the observed outcomes in some PROs included in this study. In a post-hoc analysis of the percentage of patients with clinically meaningful improvement in MADRS and patient-reported outcomes (PROs) (GAD-7, EQ-5D-5L, and EQ-VAS) in the China population at Day 28, the PROs results appeared to favor esketamine over placebo ( Figure S7 ), whereas similar response rates were seen for the clinician-rated MADRS for both treatment groups. This suggests that patients may have experienced some improvement not captured by the remote clinical rating.

#### E0030 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[61]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Another potential factor was the heterogeneity of site experiences. In a post-hoc analysis of MADRS change over time in the China population, higher enrolling sites ( Figure S8 ) showed a numerically greater treatment difference (favoring esketamine) in MADRS total score compared with lower enrolling sites. Higher enrolling sites tended to have more experience with MDD clinical trials and/or the treatment and management of patients with TRD compared with lower enrolling sites.

#### E0031 — fulltext_paragraph

Source: cache/esketamine-trd-madrs/ft_37025256.txt#p[63]. Class: OTHER; MADRS, clinician-rated scale. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Several limitations of the study merit comment. As esketamine has known transient dissociative effects that are difficult to blind (the dissociative effects are not possible to mimic adequately using an active placebo), these specific treatment-emergent events could have biased the staff who provided and observed the dosing. Therefore, to ensure an unbiased efficacy evaluation, independent, remote (by telephone), blinded MADRS raters were used to assess the treatment response. However, the use of remote raters may have reduced the sensitivity of detecting change in depressive symptoms as discussed above. In addition, as this was a flexible-dose study, dose–response relationships could not be evaluated because direct comparisons between dose groups could not be made.

#### E0032 — fulltext_table

Source: cache/esketamine-trd-madrs/ft_37025256.txt#table-wrap[@id=t0001]. Class: OTHER; MADRS, clinician-rated scale. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: full analysis set (FAS/mITT). Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 1 Demographic and Baseline Clinical Characteristics a Characteristic Esketamine Plus AD (n=124) AD Plus Placebo (n=126) Total (n=250) Age, years – mean (SD) 36.9 (12.04) 37.8 (12.36) 37.3 (12.19) Sex – n (%) Male 66 (53.2) 71 (56.3) 137 (54.8) Female 58 (46.8) 55 (43.7) 113 (45.2) Race – n (%) Asian 110 (88.7) 112 (88.9) 222 (88.8) White 12 (9.7) 9 (7.1) 21 (8.4) Black or African American 1 (0.8) 4 (3.2) 5 (2.0) Multiple 1 (0.8) 0 (0) 1 (0.4) Not reported 0 (0) 1 (0.8) 1 (0.4) Country – n (%) China 110 (88.7) 112 (88.9) 222 (88.8) United States 14 (11.3) 14 (11.1) 28 (11.2) BMI, calculated as kg/m 2 – mean (SD) 24.8 (4.98) 24.2 (4.32) 24.5 (4.66) Employment status – n (%) b Any type of employment 86 (69.4) 79 (62.7) 165 (66.0) Any type of unemployment 27 (21.8) 38 (30.2) 65 (26.0) Other 11 (8.9) 9 (7.1) 20 (8.0) Age when diagnosed with MDD, years – mean (SD) 27.2 (11.53) 28.2 (11.87) 27.7 (11.69) Duration of current episode, weeks – mean (SD) 225.3 (317.75) 218.6 (274.20) 221.9 (296.02) MADRS total score – mean (SD) 36.5 (5.21) 35.9 (4.50) 36.2 (4.87) CGI-S – mean (SD) 5.1 (0.61) 5.2 (0.68) 5.1 (0.65) CGI-S category – n (%) Mildly ill 1 (0.8) 1 (0.8) 2 (0.8) Moderately ill 15 (12.1) 16 (12.7) 31 (12.4) Markedly ill 81 (65.3) 74 (58.7) 155 (62.0) Severely ill 27 (21.8) 33 (26.2) 60 (24.0) Most extremely ill 0 (0) 2 (1.6) 2 (0.8) Class of oral AD – n (%) SNRI 68 (54.8) 69 (54.8) 137 (54.8) SSRI 56 (45.2) 57 (45.2) 113 (45.2) Oral AD – n (%) Duloxetine 36 (29.0) 40 (31.7) 76 (30.4) Escitalopram 30 (24.2) 34 (27.0) 64 (25.6) Venlafaxine extended release 31 (25.0) 29 (23.0) 60 (24.0) Sertraline 27 (21.8) 23 (18.3) 50 (20.0) Number of previous treatment failures in current episode – n (%) c 1 38 (30.6) 38 (30.2) 76 (30.4) 2 46 (37.1) 47 (37.3) 93 (37.2) 3 29 (23.4) 31 (24.6) 60 (24.0) 4 7 (5.6) 8 (6.3) 15 (6.0) 5 4 (3.2) 2 (1.6) 6 (2.4) Notes : a Data generated from the efficacy analysis set. b Any type of employment includes any category containing “employed”, sheltered work, housewife or dependent husband, and student; any type of unemployment includes any category containing “unemployed”; “other” includes retired or no information available. c Number of AD medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained from MGH-ATRQ at screening. Abbreviations : AD, antidepressant; BMI, body mass index; CGI-S, Clinical Global Impression of Severity; MADRS, Montgomery-Åsberg Depression Rating Scale; MDD, major depressive disorder; MGH-ATRQ, Massachusetts General Hospital – Antidepressant Treatment Response Questionnaire; SD, standard deviation; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0033 — fulltext_table

Source: cache/esketamine-trd-madrs/ft_37025256.txt#table-wrap[@id=t0002]. Class: OTHER; MADRS, clinician-rated scale. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: full analysis set (FAS/mITT). Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0034 — fulltext_table

Source: cache/esketamine-trd-madrs/ft_37025256.txt#table-wrap[@id=t0003]. Class: OTHER; MADRS, clinician-rated scale. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: full analysis set (FAS/mITT). Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement. b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. c SDS total score ranges from 0 to 30; a higher score indicates greater impairment. Negative change in score indicates improvement. Abbreviations : AD, antidepressant; CI, confidence interval; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SDS, Sheehan Disability Scale; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

#### E0035 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[10]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 14 , 15 In a pivotal, phase 3, global, multicenter study (TRANSFORM-2, NCT02418585 ), esketamine nasal spray (either 56 or 84 mg) plus a newly initiated oral AD showed a statistically significant and clinically relevant improvement in depressive symptoms based on change in Montgomery-Åsberg Depression Rating Scale (MADRS) 16 total score after 28 days in adult patients with TRD versus oral AD plus placebo, and clinically meaningful benefit 24 hours after the first dose.

#### E0036 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[26]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Nonresponse at the end of the screening/prospective observational phase was defined as ≤25% improvement in the MADRS total score from Week 1 to Week 4 and a MADRS total score of ≥28 on Week 2 and Week 4 during the screening/prospective observational phase.

#### E0037 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[42]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Efficacy Assessments Efficacy assessments included (1) MADRS, a clinician-rated measure of depression severity, 16 and scored by independent, remote (by phone), blinded MADRS raters to ensure an unbiased efficacy evaluation; (2) Sheehan Disability Scale (SDS), a patient-reported measure of functional impairment and associated disability; 18 , 19 (3) Clinical Global Impression of Severity (CGI-S), a clinician-rated measure of illness severity; 20 (4) 7-Item Generalized Anxiety Disorder Scale (GAD-7), a patient-reported measure of anxiety symptoms; 21 and (5) 5-level EQ-5D (EQ-5D-5L), a patient-reported measure of health outcome.

#### E0038 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[43]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 22 The primary endpoint was change in MADRS total score (7-day recall) from baseline to Day 28 (end of double-blind treatment phase).

#### E0039 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[44]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Two key secondary endpoints were (1) change from baseline in MADRS total score (24-hour recall) at 24 hours post first dose (Day 2) 23 and (2) change from baseline in SDS total score at Day 28.

#### E0040 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[51]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 26 Statistical Analysis Sample Size Determination Planned sample size was calculated assuming a treatment difference for the double-blind treatment phase of 6.5 points in MADRS total score between esketamine and the active comparator, a standard deviation (SD) of 12, a 1-sided significance level of 0.025, and a dropout rate of 25%.

#### E0041 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[63]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> For the primary efficacy analysis, change from baseline in MADRS total score at Day 28 in the double-blind phase was analyzed using a mixed-effects model for repeated measures (MMRM) based on observed case data.

#### E0042 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[83]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Esketamine plus AD and AD plus placebo groups were comparable based on demographic and baseline clinical characteristics ( Table 1 , Table S2 ), with similar mean age (36.9 vs 37.8 years), gender mix (male: 53.2% vs 56.3%), disease severity (mean MADRS total scores: 36.5 vs 35.9), and mean duration of the current depressive episode (225.3 vs 218.6 weeks) ( Table 1 ).

#### E0043 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[86]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 1 Demographic and Baseline Clinical Characteristics a Characteristic Esketamine Plus AD (n=124) AD Plus Placebo (n=126) Total (n=250) Age, years – mean (SD) 36.9 (12.04) 37.8 (12.36) 37.3 (12.19) Sex – n (%) Male 66 (53.2) 71 (56.3) 137 (54.8) Female 58 (46.8) 55 (43.7) 113 (45.2) Race – n (%) Asian 110 (88.7) 112 (88.9) 222 (88.8) White 12 (9.7) 9 (7.1) 21 (8.4) Black or African American 1 (0.8) 4 (3.2) 5 (2.0) Multiple 1 (0.8) 0 (0) 1 (0.4) Not reported 0 (0) 1 (0.8) 1 (0.4) Country – n (%) China 110 (88.7) 112 (88.9) 222 (88.8) United States 14 (11.3) 14 (11.1) 28 (11.2) BMI, calculated as kg/m 2 – mean (SD) 24.8 (4.98) 24.2 (4.32) 24.5 (4.66) Employment status – n (%) b Any type of employment 86 (69.4) 79 (62.7) 165 (66.0) Any type of unemployment 27 (21.8) 38 (30.2) 65 (26.0) Other 11 (8.9) 9 (7.1) 20 (8.0) Age when diagnosed with MDD, years – mean (SD) 27.2 (11.53) 28.2 (11.87) 27.7 (11.69) Duration of current episode, weeks – mean (SD) 225.3 (317.75) 218.6 (274.20) 221.9 (296.02) MADRS total score – mean (SD) 36.5 (5.21) 35.9 (4.50) 36.2 (4.87) CGI-S – mean (SD) 5.1 (0.61) 5.2 (0.68) 5.1 (0.65) CGI-S category – n (%) Mildly ill 1 (0.8) 1 (0.8) 2 (0.8) Moderately ill 15 (12.1) 16 (12.7) 31 (12.4) Markedly ill 81 (65.3) 74 (58.7) 155 (62.0) Severely ill 27 (21.8) 33 (26.2) 60 (24.0) Most extremely ill 0 (0) 2 (1.6) 2 (0.8) Class of oral AD – n (%) SNRI 68 (54.8) 69 (54.8) 137 (54.8) SSRI 56 (45.2) 57 (45.2) 113 (45.2) Oral AD – n (%) Duloxetine 36 (29.0) 40 (31.7) 76 (30.4) Escitalopram 30 (24.2) 34 (27.0) 64 (25.6) Venlafaxine extended release 31 (25.0) 29 (23.0) 60 (24.0) Sertraline 27 (21.8) 23 (18.3) 50 (20.0) Number of previous treatment failures in current episode – n (%) c 1 38 (30.6) 38 (30.2) 76 (30.4) 2 46 (37.1) 47 (37.3) 93 (37.2) 3 29 (23.4) 31 (24.6) 60 (24.0) 4 7 (5.6) 8 (6.3) 15 (6.0) 5 4 (3.2) 2 (1.6) 6 (2.4) Notes : a Data generated from the efficacy analysis set. b Any type of employment includes any category containing “employed”, sheltered work, housewife or dependent husband, and student; any type of unemployment includes any category containing “unemployed”; “other” includes retired or no information available. c Number of AD medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained from MGH-ATRQ at screening.

#### E0044 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[88]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Efficacy MADRS Primary Efficacy Analysis and Follow-Up Results The mean (SD) MADRS total score at baseline was 36.5 (5.21) for the esketamine plus AD group and 35.9 (4.50) for the AD plus placebo group, and at Day 28 was 26.5 (10.33) and 27.9 (10.04), respectively ( Table 2 ).

#### E0045 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[89]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean change (SD) in MADRS total score from baseline at Day 28 was -10.1 (10.80) for the esketamine plus AD group and −8.1 (10.26) for the AD plus placebo group.

#### E0046 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[92]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The MADRS change over time in the overall population and China population during the double-blind treatment phase is shown in Figure 2 .

#### E0047 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[93]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> China patients continued to the 8-week follow-up phase, during which the mean MADRS total score continuously improved.

#### E0048 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[94]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Patients who were previously on esketamine showed a larger reduction in MADRS total score compared with those who were previously on placebo, with a mean score at week 8 of 20.5 versus 24.6, respectively ( Figure S1 ).

#### E0049 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[95]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 2 Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28 N 109 106 Mean (SD) 26.5 (10.33) 27.9 (10.04) Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28 N 109 106 Mean (SD) −10.1 (10.80) −8.1 (10.26) Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b Difference of LS means (SE) −2.0 (1.32) 95% CI on difference −4.64, 0.55 2-sided p-value 0.123 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition.

#### E0050 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[99]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 2 LS mean change in MADRS total score over time a in the double-blind treatment phase in the overall population ( A ) and China population ( B ).

#### E0051 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[104]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Based on the predefined testing sequence of the primary and key secondary endpoints, the change from baseline in MADRS total score at 24 hours (Day 2) and the change from baseline in SDS total score at Day 28 could not be formally tested.

#### E0052 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[105]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The change in MADRS total score at 24 hours numerically favored esketamine plus AD over AD plus placebo.

#### E0053 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[110]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 3 Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Change in MADRS total score a from baseline to Day 2 (24 hours) Baseline N 124 126 Mean (SD) 36.5 (5.21) 35.9 (4.50) Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 2 (24 hours) N 123 125 Mean (SD) 28.5 (9.39) 31.5 (8.30) Median (range) 30.0 (0, 47) 33.0 (1, 49) Change from baseline to Day 2 (24 hours) N 123 125 Mean (SD) −8.0 (9.01) −4.4 (7.66) Median (range) −6.0 (−38, 13) −3.0 (−31, 12) MMRM analysis b Difference of LS means (SE) −3.3 (1.02) 95% CI on difference −5.33, −1.33 Change in SDS total score c from baseline to Day 28 Baseline N 119 122 Mean (SD) 22.9 (5.18) 22.5 (5.20) Median (range) 24.0 (6, 30) 23.5 (8, 30) Day 28 N 100 99 Mean (SD) 16.6 (8.34) 17.1 (8.31) Median (range) 17.0 (0, 30) 18.0 (0, 30) Change from baseline to Day 28 N 99 98 Mean (SD) −6.3 (7.54) −5.3 (7.03) Median (range) −4.0 (−30, 6) −4.0 (−22, 10) MMRM analysis b Difference of LS means (SE) −1.0 (1.00) 95% CI on difference −2.96, 0.97 Notes : a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition.

#### E0054 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[151]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Discussion This active-controlled study investigating the efficacy and safety of esketamine versus placebo, each in combination with a newly initiated oral AD, in predominantly Chinese patients with TRD did not achieve statistical significance for the primary endpoint, change in MADRS total score from baseline to Day 28, although a 2-point difference was observed.

#### E0055 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[158]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The observed 2-point difference in MADRS total score was driven primarily by data from US patients.

#### E0056 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[163]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 17 , 33 The use of remote blinded independent raters to administer the MADRS assessment by telephone was hypothesized as a potential contributing factor.

#### E0057 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[170]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In a post-hoc analysis of the percentage of patients with clinically meaningful improvement in MADRS and patient-reported outcomes (PROs) (GAD-7, EQ-5D-5L, and EQ-VAS) in the China population at Day 28, the PROs results appeared to favor esketamine over placebo ( Figure S7 ), whereas similar response rates were seen for the clinician-rated MADRS for both treatment groups.

#### E0058 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[173]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In a post-hoc analysis of MADRS change over time in the China population, higher enrolling sites ( Figure S8 ) showed a numerically greater treatment difference (favoring esketamine) in MADRS total score compared with lower enrolling sites.

#### E0059 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37025256#sentence-window[185]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Safety findings, including types and incidences of TEAEs, SAEs, and TEAEs leading to treatment discontinuation, as well as laboratory assessments, vital sign measurements, and scale data (including CADSS, C-SSRS, and PWC-20), were consistent with the established safety profile of esketamine assessed in the completed global phase 3 studies and no new safety signal was identified.
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1: Demographic and Baseline Clinical Characteristics a
> Characteristic | Esketamine Plus AD (n=124) | AD Plus Placebo (n=126) | Total (n=250)
> Age, years – mean (SD) | 36.9 (12.04) | 37.8 (12.36) | 37.3 (12.19)
> Sex – n (%) |  |  | 
> Male | 66 (53.2) | 71 (56.3) | 137 (54.8)
> Female | 58 (46.8) | 55 (43.7) | 113 (45.2)
> Race – n (%) |  |  | 
> Asian | 110 (88.7) | 112 (88.9) | 222 (88.8)
> White | 12 (9.7) | 9 (7.1) | 21 (8.4)
> Black or African American | 1 (0.8) | 4 (3.2) | 5 (2.0)
> Multiple | 1 (0.8) | 0 (0) | 1 (0.4)
> Not reported | 0 (0) | 1 (0.8) | 1 (0.4)
> Country – n (%) |  |  | 
> China | 110 (88.7) | 112 (88.9) | 222 (88.8)
> United States | 14 (11.3) | 14 (11.1) | 28 (11.2)
> BMI, calculated as kg/m 2 – mean (SD) | 24.8 (4.98) | 24.2 (4.32) | 24.5 (4.66)
> Employment status – n (%) b |  |  | 
> Any type of employment | 86 (69.4) | 79 (62.7) | 165 (66.0)
> Any type of unemployment | 27 (21.8) | 38 (30.2) | 65 (26.0)
> Other | 11 (8.9) | 9 (7.1) | 20 (8.0)
> Age when diagnosed with MDD, years – mean (SD) | 27.2 (11.53) | 28.2 (11.87) | 27.7 (11.69)
> Duration of current episode, weeks – mean (SD) | 225.3 (317.75) | 218.6 (274.20) | 221.9 (296.02)
> MADRS total score – mean (SD) | 36.5 (5.21) | 35.9 (4.50) | 36.2 (4.87)
> CGI-S – mean (SD) | 5.1 (0.61) | 5.2 (0.68) | 5.1 (0.65)
> CGI-S category – n (%) |  |  | 
> Mildly ill | 1 (0.8) | 1 (0.8) | 2 (0.8)
> Moderately ill | 15 (12.1) | 16 (12.7) | 31 (12.4)
> Markedly ill | 81 (65.3) | 74 (58.7) | 155 (62.0)
> Severely ill | 27 (21.8) | 33 (26.2) | 60 (24.0)
> Most extremely ill | 0 (0) | 2 (1.6) | 2 (0.8)
> Class of oral AD – n (%) |  |  | 
> SNRI | 68 (54.8) | 69 (54.8) | 137 (54.8)
> SSRI | 56 (45.2) | 57 (45.2) | 113 (45.2)
> Oral AD – n (%) |  |  | 
> Duloxetine | 36 (29.0) | 40 (31.7) | 76 (30.4)
> Escitalopram | 30 (24.2) | 34 (27.0) | 64 (25.6)
> Venlafaxine extended release | 31 (25.0) | 29 (23.0) | 60 (24.0)
> Sertraline | 27 (21.8) | 23 (18.3) | 50 (20.0)
> Number of previous treatment failures in current episode – n (%) c |  |  | 
> 1 | 38 (30.6) | 38 (30.2) | 76 (30.4)
> 2 | 46 (37.1) | 47 (37.3) | 93 (37.2)
> 3 | 29 (23.4) | 31 (24.6) | 60 (24.0)
> 4 | 7 (5.6) | 8 (6.3) | 15 (6.0)
> 5 | 4 (3.2) | 2 (1.6) | 6 (2.4)
> 
> TABLE Table 2: Change in MADRS Total Score a from Baseline to Day 28 in the Double-Blind Treatment Phase
>  | Esketamine Plus AD | AD Plus Placebo
> Baseline |  | 
> N | 124 | 126
> Mean (SD) | 36.5 (5.21) | 35.9 (4.50)
> Median (range) | 36.0 (25, 50) | 36.0 (27, 48)
> Day 28 |  | 
> N | 109 | 106
> Mean (SD) | 26.5 (10.33) | 27.9 (10.04)
> Median (range) | 28.0 (0, 43) | 30.0 (0, 44)
> Change from baseline to Day 28 |  | 
> N | 109 | 106
> Mean (SD) | −10.1 (10.80) | −8.1 (10.26)
> Median (range) | −7.0 (−42, 10) | −6.0 (−38, 8)
> MMRM analysis b | 
> Difference of LS means (SE) | −2.0 (1.32)
> 95% CI on difference | −4.64, 0.55
> 2-sided p-value | 0.123
> 
> TABLE Table 3: Key Secondary Efficacy Endpoints Assessed in the Double-Blind Treatment Phase
>  | Esketamine Plus AD | AD Plus Placebo
> Change in MADRS total score a from baseline to Day 2 (24 hours) |  | 
> Baseline |  | 
> N | 124 | 126
> Mean (SD) | 36.5 (5.21) | 35.9 (4.50)
> Median (range) | 36.0 (25, 50) | 36.0 (27, 48)
> Day 2 (24 hours) |  | 
> N | 123 | 125
> Mean (SD) | 28.5 (9.39) | 31.5 (8.30)
> Median (range) | 30.0 (0, 47) | 33.0 (1, 49)
> Change from baseline to Day 2 (24 hours) |  | 
> N | 123 | 125
> Mean (SD) | −8.0 (9.01) | −4.4 (7.66)
> Median (range) | −6.0 (−38, 13) | −3.0 (−31, 12)
> MMRM analysis b | 
> Difference of LS means (SE) | −3.3 (1.02)
> 95% CI on difference | −5.33, −1.33
> Change in SDS total score c from baseline to Day 28 |  | 
> Baseline |  | 
> N | 119 | 122
> Mean (SD) | 22.9 (5.18) | 22.5 (5.20)
> Median (range) | 24.0 (6, 30) | 23.5 (8, 30)
> Day 28 |  | 
> N | 100 | 99
> Mean (SD) | 16.6 (8.34) | 17.1 (8.31)
> Median (range) | 17.0 (0, 30) | 18.0 (0, 30)
> Change from baseline to Day 28 |  | 
> N | 99 | 98
> Mean (SD) | −6.3 (7.54) | −5.3 (7.03)
> Median (range) | −4.0 (−30, 6) | −4.0 (−22, 10)
> MMRM analysis b | 
> Difference of LS means (SE) | −1.0 (1.00)
> 95% CI on difference | −2.96, 0.97
> 
> TABLE Table 4: Safety Summary During the Double-Blind Treatment Phase
>  | Esketamine Plus AD (n=126) | AD Plus Placebo (n=126)
> TEAEs | 120 (95.2) | 89 (70.6)
> Most common (≥10% of patients in either group) |  | 
> Dizziness | 97 (77.0) | 25 (19.8)
> Dissociation | 75 (59.5) | 8 (6.3)
> Nausea | 53 (42.1) | 17 (13.5)
> Blood pressure increased | 38 (30.2) | 13 (10.3)
> Hypoesthesia | 25 (19.8) | 1 (0.8)
> Vomiting | 23 (18.3) | 2 (1.6)
> Vision blurred | 23 (18.3) | 1 (0.8)
> Somnolence | 20 (15.9) | 11 (8.7)
> Headache | 16 (12.7) | 14 (11.1)
> Dysgeusia | 14 (11.1) | 6 (4.8)
> TEAEs possibly related to intranasal drug a | 117 (92.9) | 55 (43.7)
> TEAEs leading to death b | 1 (0.8) | 0 (0)
> Treatment-emergent SAEs | 3 (2.4) | 3 (2.4)
> Completed suicide b | 1 (0.8) | 0 (0)
> Depression | 1 (0.8) | 3 (2.4)
> Suicide attempt | 1 (0.8) | 0 (0)
> TEAEs leading to discontinuation of intranasal study medication c | 7 (5.6) | 2 (1.6)
> Nausea | 2 (1.6) | 1 (0.8)
> Vomiting | 2 (1.6) | 0 (0)
> Dissociation | 2 (1.6) | 0 (0)
> Dizziness | 2 (1.6) | 2 (1.6)
> Depressional suicide | 1 (0.8) | 0 (0)
> Headache | 1 (0.8) | 0 (0)
> Asthenia | 1 (0.8) | 0 (0)
> Blood pressure increased | 1 (0.8) | 0 (0)
> Decreased appetite | 1 (0.8) | 0 (0)
> Myalgia | 1 (0.8) | 0 (0)
> Diarrhea | 0 (0) | 1 (0.8)
> Parosmia | 0 (0) | 1 (0.8)
> Insomnia | 0 (0) | 2 (1.6)

### esketamine-trd-madrs — PMID 31109201

Pinned served row:
~~~json
{
  "id": "PMID 31109201",
  "mean1": -21.4,
  "sd1": 12.32,
  "nc1": 101,
  "mean2": -17.0,
  "sd2": 13.88,
  "nc2": 100,
  "source": "ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery-Asberg Depression Rating Scale (MAD' mean -21.4 (SD 12.32, n=101) [Intranasal Esketamine ] vs -17.0 (SD 13.88, n=100) [Intranasal Placebo Plu] Units on a scale — population: Full analysis set (FAS) defined as all randomized participants who received at l",
  "timeframe": "Baseline up to Day 28 of Double-blind Induction Phase"
}
~~~

#### E0060 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/19/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **PRIMARY_REPORT**.

Population: full analysis set (FAS/mITT). Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: About one-third of patients with depression fail to achieve remission despite treatment with multiple antidepressants. This study compared the efficacy and safety of switching patients with treatment-resistant depression from an ineffective antidepressant to flexibly dosed esketamine nasal spray plus a newly initiated antidepressant or to a newly initiated antidepressant (active comparator) plus placebo nasal spray. METHODS: This was a phase 3, double-blind, active-controlled, multicenter study conducted at 39 outpatient referral centers. The study enrolled adults with moderate to severe nonpsychotic depression and a history of nonresponse to at least two antidepressants in the current episode, with one antidepressant assessed prospectively. Confirmed nonresponders were randomly assigned to treatment with esketamine nasal spray (56 or 84 mg twice weekly) and an antidepressant or antidepressant and placebo nasal spray. The primary efficacy endpoint, change from baseline to day 28 in Montgomery-Åsberg Depression Rating Scale (MADRS) score, was assessed by a mixed-effects model using repeated measures. RESULTS: Of 435 patients screened, 227 underwent randomization and 197 completed the 28-day double-blind treatment phase. Change in MADRS score with esketamine plus antidepressant was significantly greater than with antidepressant plus placebo at day 28 (difference of least square means=-4.0, SE=1.69, 95% CI=-7.31, -0.64); likewise, clinically meaningful improvement was observed in the esketamine plus antidepressant arm at earlier time points. The five most common adverse events (dissociation, nausea, vertigo, dysgeusia, and dizziness) all were observed more frequently in the esketamine plus antidepressant arm than in the antidepressant plus placebo arm; 7% and 0.9% of patients in the respective treatment groups discontinued study drug because of an adverse event. Adverse events in the esketamine plus antidepressant arm generally appeared shortly after dosing and resolved by 1.5 hours after dosing. CONCLUSIONS: Current treatment options for treatment-resistant depression have considerable limitations in terms of efficacy and patient acceptability. Esketamine is expected to address an unmet medical need in this population through its novel mechanism of action and rapid onset of antidepressant efficacy. The study supports the efficacy and safety of esketamine nasal spray as a rapidly acting antidepressant for patients with treatment-resistant depression.

#### E0061 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/5/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> This exploratory post hoc analysis of two pooled 4-week, phase 3, double-blind, placebo- and active-controlled studies that compared esketamine nasal spray plus a newly initiated oral antidepressant (ESK+AD; n = 310) with a newly initiated oral AD plus placebo nasal spray (AD+PBO; n = 208) in patients with treatment-resistant depression (TRD) examined baseline patient demographic and psychiatric characteristics as potential predictors of response (≥50% reduction from baseline in Montgomery-Åsberg Depression Rating Scale [MADRS] total score) and remission (MADRS total score ≤12) at day 28. Overall, younger age, any employment, fewer failed ADs in the current depressive episode, and reduction in Clinical Global Impression-Severity (CGI-S) score at day 8 were significant positive predictors of response and remission at day 28. Treatment assignment was an important predictor of both response and remission. Patients treated with ESK+AD had 68% and 55% increased odds of achieving response and remission, respectively, versus those treated with AD+PBO. In the ESK+AD group, attainment of response and remission was more likely in patients who were employed, without significant anxiety at baseline, and who experienced a reduction in CGI-S score at day 8. Identification of predictors of response and remission may facilitate identification of those patients with TRD most likely to benefit from ESK+AD. Trial Registration: ClinicalTrials.gov: NCT02417064 (clinicaltrials.gov/ct2/show/NCT02417064) and NCT02418585 (clinicaltrials.gov/ct2/show/NCT02418585).

#### E0062 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/6/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: To evaluate the impact of baseline irritability on clinical outcomes in adults with treatment-resistant depression (TRD) treated with fixed or flexible doses of esketamine nasal spray plus a newly initiated oral antidepressant (ESK+AD) and to explore whether treatment with ESK affects irritability symptoms over time. METHODS: This was a post hoc analysis of pooled data from two 4-week, double-blind, phase 3 studies: TRANSFORM-1 (NCT02417064) and TRANSFORM-2 (NCT02418585). Adults with TRD (n = 560) were randomly assigned to ESK+AD or placebo nasal spray plus oral antidepressant (AD+PBO). Irritability was assessed with Item 6 of the 7-item Generalized Anxiety Disorder scale at screening and baseline. Changes in depression severity (Montgomery-Åsberg Depression Rating Scale [MADRS] total score) were evaluated by analysis of covariance (ANCOVA) models. Rates of MADRS response (≥50 % decrease from baseline total score) and remission (total score ≤ 12) were examined using multiple logistic regression models. RESULTS: Of 560 participants with TRD, 52.9 %, 23.2 %, and 23.9 % had high, low, and varying levels of irritability, respectively. No significant interaction between baseline irritability and treatment group was observed for change in MADRS total score, treatment response, or remission at day 28; numerically greater improvement was observed on all outcomes with ESK+AD versus AD+PBO at day 28 regardless of baseline irritability level. Percentages of patients reporting adverse events were similar across the three baseline irritability groups. LIMITATIONS: TRANSFORM-1 and TRANSFORM-2 were not designed to prospectively evaluate predetermined irritability outcomes. CONCLUSIONS: These post hoc results support efficacy of ESK+AD in patients with TRD, regardless of baseline irritability. TRIAL REGISTRATION: ClinicalTrials.gov identifiers: NCT02417064 (TRANSFORM-1), NCT02418585 (TRANSFORM-2).

#### E0063 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/9/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: The objective of this study was to determine which symptoms measured by the Patient Health Questionnaire (PHQ-9) and Montgomery-Asberg Depression Rating Scale (MADRS) improve in those treated with esketamine nasal spray in combination with oral antidepressant (AD) compared with those treated with placebo plus AD for adult patients with treatment-resistant depression (TRD). These results complement the interpretation of PHQ-9 and MADRS total scores. METHODS: The TRANSFORM 2 study evaluated the efficacy and safety of esketamine nasal spray in combination with AD. This post-hoc analysis used PHQ-9 and MADRS data to evaluate symptom changes. The total scores change and proportions of individual item change scores on the PHQ-9 and MADRS were evaluated at days 15 and 28; analysis of variance was used to test differences on total scores. Generalized estimation equations of logistic regression models were used to estimate the likelihood of improvement on instrument items. RESULTS: The mean total score reduction of the PHQ-9, indicating improvement, was greater in the esketamine plus AD arm compared with placebo plus AD at day 15 (- 1.8; p = 0.045) and day 28 (- 2.8; p = 0.006). Proportions of those who improved (≥ 1 point on a 4-point scale and ≥ 2 points on a 7-point scale for the PHQ-9 and MADRS, respectively) was greater in the esketamine plus AD group compared with the placebo plus AD group across all items. The odds of improving for those in the esketamine plus AD group compared with the placebo plus AD group were over two times greater on the PHQ-9 items: "Little interest/pleasure in things" (OR 2.252, 95% CI 1.165-4.355); "Feeling down, depressed, or hopeless" (OR 2.767, 95% CI 1.400-5.470); and "Feeling tired or having little energy" (OR 2.171, 95% CI 1.153-4.087). The mean reduction in total scores on the MADRS, indicating improvement, was numerically greater at day 15 (- 2.0; p = 0.189) and statistically significantly greater at day 28 (- 4.4; p = 0.017) in the esketamine plus AD arm compared with placebo plus AD. The odds of improving for those in the esketamine plus AD group compared with the placebo plus AD group were over two times greater on the MADRS items measuring "Apparent sadness" (OR 2.007, 95% CI 1.096-3.674); and "Inability to feel" (OR 2.099, 95% CI 1.180-3.735). CONCLUSION: Improvement in mean total scores in those treated with esketamine plus AD compared with placebo plus AD are important results to confirm efficacy. The odds of improving in those treated with esketamine plus AD was at least two times greater than with placebo plus AD on three patient- and two clinician-reported individual symptoms of TRD. These findings provide patient-relevant quantification of the esketamine plus AD treatment benefit, adding understanding as to which symptoms are most improved with treatment. TRIAL REGISTRATION: ClinicalTrials.gov identifier: NCT02418585; first posted 16 April 2015.

#### E0064 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/10/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> The objective of this analysis was to determine if there are sex differences with esketamine for treatment-resistant depression (TRD). Post hoc analyses of three randomized, controlled studies of esketamine in patients with TRD (TRANSFORM-1, TRANSFORM-2 [18-64 years], TRANSFORM-3 [≥ 65 years]) were performed. In each 4-week study, adults with TRD were randomized to esketamine or placebo nasal spray, each with a newly initiated oral antidepressant. Change from baseline to day 28 in Montgomery-Åsberg Depression Rating Scale (MADRS) total score was assessed by sex in pooled data from TRANSFORM-1/TRANSFORM-2 and separately in data from TRANSFORM-3 using a mixed-effects model for repeated measures. Use of hormonal therapy was assessed in all women, and menopausal status was assessed in women in TRANSFORM-1/TRANSFORM-2. Altogether, 702 adults (464 women) received ≥ 1 dose of intranasal study drug and antidepressant. Mean MADRS total score (SD) decreased from baseline to day 28, more so among patients treated with esketamine/antidepressant vs. antidepressant/placebo in both women and men: TRANSFORM-1/TRANSFORM-2 women-esketamine/antidepressant -20.3 (13.19) vs. antidepressant/placebo -15.8 (14.67), men-esketamine/antidepressant -18.3 (14.08) vs. antidepressant/placebo -16.0 (14.30); TRANSFORM-3 women-esketamine/antidepressant -9.9 (13.34) vs. antidepressant/placebo -6.9 (9.65), men-esketamine/antidepressant -10.3 (11.96) vs. antidepressant/placebo -5.5 (7.64). There was no significant sex effect or treatment-by-sex interaction (p > 0.35). The most common adverse events in esketamine-treated patients were nausea, dissociation, dizziness, and vertigo, each reported at a rate higher in women than men. The analyses support antidepressant efficacy and overall safety of esketamine nasal spray are similar between women and men with TRD. The TRANSFORM studies are registered at clinicaltrials.gov (identifiers: NCT02417064 (first posted 15 April 2015; last updated 4 May 2020), NCT02418585 (first posted 16 April 2015; last updated 2 June 2020), and NCT02422186 (first posted 21 April 2015; last updated 29 September 2021)).

#### E0065 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/13/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Comorbid anxiety is generally associated with poorer response to antidepressant treatment. This post hoc analysis explored the efficacy of esketamine plus an antidepressant in patients with treatment-resistant depression (TRD) with or without comorbid anxiety. METHODS: TRANSFORM-2, a double-blind, flexible-dose, 4-week study (NCT02418585), randomized adults with TRD to placebo or esketamine nasal spray, each with a newly-initiated oral antidepressant. Comorbid anxiety was defined as clinically noteworthy anxiety symptoms (7-item Generalized Anxiety Disorder scale [GAD-7] score ≥10) at screening and baseline or comorbid anxiety disorder diagnosis at screening. Treatment effect based on change in Montgomery-Åsberg Depression Rating Scale (MADRS) total score, and response and remission were examined by presence/absence of comorbid anxiety using analysis of covariance and logistic regression models. RESULTS: Approximately 72% (162/223) of patients had baseline comorbid anxiety. Esketamine-treated patients with and without anxiety demonstrated significant reductions in MADRS (mean [SD] change from baseline at day 28: -21.0 [12.51] and -22.7 [11.98], respectively). Higher rates of response and remission, and a significantly greater decrease in MADRS score at day 28 were observed compared to antidepressant/placebo, regardless of comorbid anxiety (with anxiety: difference in LS means [95% CI] -4.2 [-8.1, -0.3]; without anxiety: -7.5 [-13.7, -1.3]). There was no significant interaction of treatment and comorbid anxiety (p = .371). Notably, in the antidepressant/placebo group improvement was similar in those with and without comorbid anxiety. CONCLUSION: Post hoc data support efficacy of esketamine plus an oral antidepressant in patients with TRD, regardless of comorbid anxiety.

#### E0066 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/17/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: At ketamine and esketamine doses at which antidepressant doses are achieved, these agents are relatively selective, noncompetitive, N-methyl-D-aspartate receptor antagonists. However, at substantially higher doses, ketamine has shown mu-opioid receptor (MOR-gene symbol: OPRM1) agonist effects. Preliminary clinical studies showed conflicting results on whether naltrexone, a MOR antagonist, blocks the antidepressant action of ketamine. We examined drug-induced or endogenous MOR involvement in the antidepressant and dissociative responses to esketamine by assessing the effects of a functional single nucleotide polymorphism rs1799971 (A118G) of OPRM1, which is known to alter MOR agonist-mediated responses. METHODS: Participants with treatment-resistant depression from 2 phase III, double-blind, controlled trials of esketamine (or placebo) nasal spray plus an oral antidepressant were genotyped for rs1799971. Participants received the experimental agents twice weekly for 4 weeks. Antidepressant responses were rated using the change in Montgomery-Åsberg Depression Rating Scale (MADRS) score on days 2 and 28 post-dose initiation, and dissociative side effects were assessed using the Clinician-Administered Dissociative-States Scale at 40 minutes post-dose on days 1 and 25. RESULTS: In the esketamine + antidepressant arm, no significant genotype effect of single nucleotide polymorphism rs1799971 (A118G) on MADRS score reductions was detected on either day 2 or 28. By contrast, in the antidepressant + placebo arm, there was a significant genotype effect on MADRS score reductions on day 2 and a nonsignificant trend on day 28 towards an improvement in depression symptoms in G-allele carriers. No significant genotype effects on dissociative responses were detected. CONCLUSIONS: Variation in rs1799971 (A118G) did not affect the antidepressant response to esketamine + antidepressant. Antidepressant response to antidepressant + placebo was increased in G-allele carriers, compatible with previous reports that release of endorphins/enkephalins may play a role in mediating placebo effect. TRIAL REGISTRATION: NCT02417064 and NCT02418585; www.clinicaltrials.gov.

#### E0067 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/68/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: To examine the effect of esketamine nasal spray (ESK) plus newly initiated oral antidepressant (OAD) versus OAD plus placebo nasal spray (PBO) on the association between Montgomery-Åsberg Depression Rating Scale (MADRS) and 9-item Patient Health Questionnaire (PHQ-9) scores in adults with treatment-resistant depression (TRD). METHODS: Data from TRANSFORM-1 and TRANSFORM-2 (two similarly designed, randomized, active-controlled TRD studies) and SUSTAIN-1 (relapse prevention study) were analyzed. Group differences for mean changes in PHQ-9 total score from baseline were compared using analysis of covariance. Associations between MADRS and PHQ-9 total scores from TRANSFORM-1/TRANSFORM-2 were assessed using simple parametric, nonparametric, and multiple regression models. RESULTS: In TRANSFORM-1/TRANSFORM-2 (ESK + OAD, n = 343; OAD + PBO, n = 222), baseline PHQ-9 mean scores were 20.4 for ESK + OAD and 20.6 for OAD + PBO (severe depression). At day 28, significant group differences were observed in least squares mean change (SE) in PHQ-9 scores from baseline (-12.8 [0.46] vs -10.3 [0.53], P < .001) and in clinically substantial change in PHQ-9 scores (≥6 points; 77.1% vs 64%, P < .001) in ESK + OAD and OAD + PBO groups, respectively. A nonlinear relationship between MADRS and PHQ-9 was observed; total scores demonstrated increased correlation over time. In SUSTAIN-1, 57.3% of patients receiving ESK + OAD (n = 89) versus 44.2% receiving OAD + PBO (n = 86) retained remission status (PHQ-9 score ≤4) at maintenance treatment end point (P = .044). CONCLUSIONS: In adults with TRD, ESK + OAD significantly improved severity of depressive symptoms, and more patients achieved clinically meaningful changes in depressive symptoms based on PHQ-9, versus OAD + PBO. PHQ-9 outcomes were consistent with those of clinician-rated MADRS. TRIAL REGISTRATION: ClinicalTrials.gov: NCT02417064, NCT02418585, NCT02493868.

#### E0068 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/82/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> Objective: To evaluate response to esketamine nasal spray plus an oral antidepressant (ESK + AD) at day 28 in patients with major depressive disorder (DSM-5) and treatment-resistant depression (TRD) who did not meet response criteria within the first week of treatment. Methods: The current study is a pooled post hoc analysis of two phase 3, double-blind, active-controlled studies, conducted between August 2015 and February 2018, comparing ESK + AD with an oral antidepressant plus placebo (AD + PBO). Early treatment response was defined as a ≥ 50% decrease in Montgomery-Åsberg Depression Rating Scale total score at day 2 or days 2 and 8. Response rates at day 28 were determined among those not meeting early response criteria. Results: 518 patients in the analysis had day 28 observations (ESK + AD, n = 310; AD + PBO, n = 208). A greater percentage of patients treated with ESK + AD versus AD + PBO met response criteria beginning at day 2 (17.3% [55/318] vs 9.4% [19/203]) and at all subsequent timepoints, including day 28 (58.7% [182/310] vs 45.2% [94/208]). In day 2 nonresponders, 54.9% vs 44.3% (ESK + AD vs AD + PBO, respectively) achieved response at day 28 (P < .01). Similarly, among day 2 and 8 nonresponders, 52.1% vs 42.4% achieved response by day 28 (P = .01). In nonresponders at day 2 and at days 2 and 8, the odds ratio for a response at day 28 was 1.61 (95% CI, 1.09-2.40) with ESK + AD versus 1.56 (95% CI, 1.04-2.35) with AD + PBO. Conclusions: Patients with TRD without a demonstrated response within the first week of treatment may still derive benefit from a full 4-week induction course of esketamine nasal spray. Trial Registration: ClinicalTrials.gov identifiers NCT02417064 and NCT02418585.

#### E0069 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "101".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. 

> {"groupId": "OG000", "value": "-21.4", "spread": "12.32"}

#### E0070 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "100".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. 

> {"groupId": "OG001", "value": "-17.0", "spread": "13.88"}

#### E0071 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. 

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "SUPERIORITY", "pValue": "=0.020", "statisticalMethod": "Mixed Model for Repeated Measures", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-4.0", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.31", "ciUpperLimit": "-0.64", "dispersionType": "STANDARD_ERROR_OF_MEAN", "dispersionValue": "1.69"}

#### E0072 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/1/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "112".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. The last post baseline observation during the phase was carried forward as "End Point" for that phase. 

> {"groupId": "OG000", "value": "-19.6", "spread": "13.58"}

#### E0073 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/1/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "109".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. The last post baseline observation during the phase was carried forward as "End Point" for that phase. 

> {"groupId": "OG001", "value": "-16.3", "spread": "14.24"}

#### E0074 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/1/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. The last post baseline observation during the phase was carried forward as "End Point" for that phase. 

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "SUPERIORITY", "pValue": "=0.034", "statisticalMethod": "ANCOVA", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-3.5", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-6.67", "ciUpperLimit": "-0.26"}

#### E0075 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[16]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Both short-term and long-term (up to 12 months or longer) efficacy and safety was demonstrated against placebo in the TRANSFORM and SUSTAIN trials which reported significant improvements in depressive symptoms (mean decrease of −21.4 (12.3) of the Montgomery–Åsberg Depression Rating Scale (MADRS) from initiation to day 28 11 ), sustained symptom remission and a low relapse rate in patients who were in remission (26.7% 12 ).

#### E0076 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[42]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Treatment response was defined either by a ⩾50% relative reduction in MADRS total score from baseline or by an MADRS total score ⩽10.

#### E0077 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[44]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Relapse was defined as the occurrence of a MADRS score ⩾22 at any follow‑up assessment in a patient who had previously achieved remission.

#### E0078 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[57]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Another sensitivity analysis was conducted by defining remission with MADRS ⩽ 12 instead of ⩽10.

#### E0079 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[72]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Characteristics, n (%) otherwise specified N = 200 Demographics and physical examination Age, years Mean (SD) 46.6 (15.5) Median (IQR) 48 (35–58) <65 years 177 (88.5) Female 113 (56.5) Normal blood pressure at baseline 178/195 (91.3) Lifetime history of depression Time between first diagnosis of lifetime depression and inclusion (years) N = 142 Median (IQR) 10 (3.2–22.8) Lifetime number of previous MDE (excluding the current episode) N = 198 Mean (SD) 3.0 (2.9) Lifetime number of treatment-resistant depressive episodes (failure of at least 2 lines of treatment, excluding current depressive episode) N = 158 Mean (SD) 1.8 (2.1) Patients with at least one previous MDE N = 160 Lifetime history of suicide attempt 78 (39.0) Current MDE 200 (100.0) Duration of MDE, years N = 184 Mean (SD) 2.9 (3.7) Median (IQR) 1.8 (0.9–3.2) Typology N = 200 Suicidal ideation 102 (51.0) Risk behaviors 21 (10.5) Deterioration of general physical condition 36 (18.0) Functional disability 84 (42.0) Unknown 27 (13.5) Clinical subtype Anxiety feature 116 (58.0) Melancholic features 42 (21.0) Psychotic features 4 (2.0) Atypical features 12 (6.0) Catatonic features 4 (2.0) Seasonal features 5 (2.5) At least one full-time hospitalization since the onset of the current MDE 115 (57.5) Treatment-resistant (clinician’s judgment) 195 (97.5) MADRS at baseline N = 198 Total mean (SD) 31.9 (7.0) Mild depression (7–19 points) 8 (4.0) Moderate depression (20–34 points) 118 (59.6) Severe depression (>34 points) 72 (36.4) CGI-SS-R score at baseline N = 197 Mean (SD) 1.9 (1.4) 0 Normal, no at all suicidal 46 (23.4) 1 Questionably suicidal 32 (16.2) 2 Mildly suicidal 43 (21.8) 3 Moderately suicidal 45 (22.8) 4 Markedly suicidal 28 (14.2) 5 Severely suicidal 2 (1.0) 6 Among the most extremely suicidal participants 1 (0.5) C-SSRS at baseline in patients with CGI-SS-R > 1 at baseline N = 146 Question 4: Active suicidal ideation with some intent to act without specific plan 79 (54.1) Question 5: Active suicidal ideation with specific plan and intent 33 (22.6) QLDS Score at baseline N = 190 Mean (SD) 20.8 (3.8) Severity of the current MDE (clinician’s judgment) Mild 1 (0.5) Moderate 63 (31.5) Severe 136 (68.0) Comorbidities at baseline Other psychiatric comorbidity 144 (72.0) Anxiety disorders 79/144 (54.9) Posttraumatic stress disorder 48/144 (33.3) Current substance use-related disorders and addictive disorders 40/144 (27.8) Obsessive-compulsive and related disorders 11/144 (7.6) Conduct and Impulse Control Disorders 7/144 (4.9) Neurodevelopmental disorders 5/144 (3.5) Endocrine disorder 19/199 (9.5) Cardiac disease 31/199 (15.6) Vascular disease 8/199 (4.0) Respiratory, thoracic, and mediastinal disorders 14/199 (7.0) Nervous system disorders 26/199 (13.1) Hepatobiliary disorders 9/199 (4.5) Previous well-conducted treatment lines of AD N = 182 Median number (IQR) 3 (2–5) ⩾2 145/182 (79.7) ⩾5 52/182 (28.6) Details of previous well-conducted lines of AD 182 (91.0) A single AD without augmentation 129 (64.5) A single AD with augmentation 61 (30.5) Combination of AD without augmentation 59 (29.5) Combination of AD with augmentation 74 (37.0) A single augmentation therapy drug 63 (31.5) Combination of augmentation therapy drugs 18 (9.0) Neurostimulation (ECT, rTMS, tDCS) 45 (22.5) No treatment 6 (3.0) AD, antidepressant; CGI-SS-R, Clinical Global Impression- Suicidality Severity–Revised; ECT, electroconvulsive therapy; IQR, interquartile range; MADRS, Montgomery–Åsberg Depression Rating Scale; MDE, major depressive episode; QLDS, Quality of Life in Depression Scale; rTMS, repetitive transcranial magnetic stimulation; tDCS, transcranial direct current stimulation.

#### E0080 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[76]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean baseline MADRS score was 31.9 ( SD = 7.0).

#### E0081 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[77]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Based on clinician judgment, 68.0% of episodes were classified as severe, and 31.5% as moderate, while 36.4% met the MADRS threshold for severe depression and 59.6% met the MADRS threshold for moderate depression.

#### E0082 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[114]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean MADRS score decreased from 31.9 ( SD = 7.0) at baseline to 18.9 ( SD = 9.1 at the M1 visit (end of the initiation phase), corresponding to a mean absolute change of −13.0 points (95% CI: −14.6 to −11.4; Figure 2 ).

#### E0083 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[117]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The lowest mean MADRS score was observed at M12, reaching 12.4 ( SD = 9.4), with a mean absolute change of −17.9 (95% CI: −21.6 to −14.2).

#### E0084 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[118]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS items all showed improvement over the 12-month follow-up.

#### E0085 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[119]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At baseline, the most severe MADRS items were Reported Sadness (4.2, SD = 1.1) and Apparent Sadness (4.0, SD = 1.2), followed by lassitude (3.7, SD = 1.1), inability to feel (3.7, SD = 1.1), and inner tension (3.3, SD = 1.3), while symptoms such as suicidal thoughts (2.5, SD = 1.5), reduced sleep (2.4, SD = 1.8), and reduced appetite (1.5, SD = 1.6) were least pronounced.

#### E0086 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[134]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Remission sensitivity analyses with a higher MADRS threshold (⩽12 instead of ⩽10) also showed consistent results, with slightly higher rates when the threshold was set to ⩽12 ( Figures S7 and S8 ).

#### E0087 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[136]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS response and remission rates in patients still under esketamine with MADRS available up to month 12.

#### E0088 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[138]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Alt text: Rate of MADRS response and remission in esketamine-treated patients up to 12 months.

#### E0089 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[204]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In ELLIPSE, the MADRS decreased consistently in patients still under treatment during the induction phase and stabilized by M2 (mean MADRS 15.6 (9.0)), with sustained improvements through M12.

#### E0090 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[209]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The REAL-ESK cohort also reported a significant reduction in the MADRS score in patients still under esketamine was observed at month 1 (mean, 22.27 ± 9.81) and month 3 ( n = 91; mean, 14.69 ± 9.88) compared to baseline ((T0); mean, 35 ± 8.53).

#### E0091 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[211]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the ESCAPE-TRD trial, the absolute rate of remission (score of 10 or less on the MADRS) was 27.1% at month 2.

#### E0092 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[256]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Relapse was defined on the basis of a MADRS score ⩾22 observed at any follow-up assessment after remission, without confirmation across consecutive visits.

#### E0093 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31109201#sentence-window[268]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Characteristics, n (%) otherwise specified | N = 200
> Demographics and physical examination
> Age, years
> Mean (SD) | 46.6 (15.5)
> Median (IQR) | 48 (35–58)
> <65 years | 177 (88.5)
> Female | 113 (56.5)
> Normal blood pressure at baseline | 178/195 (91.3)
> Lifetime history of depression
> Time between first diagnosis of lifetime depression and inclusion (years) | N = 142
> Median (IQR) | 10 (3.2–22.8)
> Lifetime number of previous MDE (excluding the current episode) | N = 198
> Mean (SD) | 3.0 (2.9)
> Lifetime number of treatment-resistant depressive episodes (failure of at least 2 lines of treatment, excluding current depressive episode) | N = 158
> Mean (SD) | 1.8 (2.1)
> Patients with at least one previous MDE | N = 160
> Lifetime history of suicide attempt | 78 (39.0)
> Current MDE | 200 (100.0)
> Duration of MDE, years | N = 184
> Mean (SD) | 2.9 (3.7)
> Median (IQR) | 1.8 (0.9–3.2)
> Typology | N = 200
> Suicidal ideation | 102 (51.0)
> Risk behaviors | 21 (10.5)
> Deterioration of general physical condition | 36 (18.0)
> Functional disability | 84 (42.0)
> Unknown | 27 (13.5)
> Clinical subtype | 
> Anxiety feature | 116 (58.0)
> Melancholic features | 42 (21.0)
> Psychotic features | 4 (2.0)
> Atypical features | 12 (6.0)
> Catatonic features | 4 (2.0)
> Seasonal features | 5 (2.5)
> At least one full-time hospitalization since the onset of the current MDE | 115 (57.5)
> Treatment-resistant (clinician’s judgment) | 195 (97.5)
> MADRS at baseline | N = 198
> Total mean (SD) | 31.9 (7.0)
> Mild depression (7–19 points) | 8 (4.0)
> Moderate depression (20–34 points) | 118 (59.6)
> Severe depression (>34 points) | 72 (36.4)
> CGI-SS-R score at baseline | N = 197
> Mean (SD) | 1.9 (1.4)
> 0 Normal, no at all suicidal | 46 (23.4)
> 1 Questionably suicidal | 32 (16.2)
> 2 Mildly suicidal | 43 (21.8)
> 3 Moderately suicidal | 45 (22.8)
> 4 Markedly suicidal | 28 (14.2)
> 5 Severely suicidal | 2 (1.0)
> 6 Among the most extremely suicidal participants | 1 (0.5)
> C-SSRS at baseline in patients with CGI-SS-R > 1 at baseline | N = 146
> Question 4: Active suicidal ideation with some intent to act without specific plan | 79 (54.1)
> Question 5: Active suicidal ideation with specific plan and intent | 33 (22.6)
> QLDS Score at baseline | N = 190
> Mean (SD) | 20.8 (3.8)
> Severity of the current MDE (clinician’s judgment) | 
> Mild | 1 (0.5)
> Moderate | 63 (31.5)
> Severe | 136 (68.0)
> Comorbidities at baseline
> Other psychiatric comorbidity | 144 (72.0)
> Anxiety disorders | 79/144 (54.9)
> Posttraumatic stress disorder | 48/144 (33.3)
> Current substance use-related disorders and addictive disorders | 40/144 (27.8)
> Obsessive-compulsive and related disorders | 11/144 (7.6)
> Conduct and Impulse Control Disorders | 7/144 (4.9)
> Neurodevelopmental disorders | 5/144 (3.5)
> Endocrine disorder | 19/199 (9.5)
> Cardiac disease | 31/199 (15.6)
> Vascular disease | 8/199 (4.0)
> Respiratory, thoracic, and mediastinal disorders | 14/199 (7.0)
> Nervous system disorders | 26/199 (13.1)
> Hepatobiliary disorders | 9/199 (4.5)
> Previous well-conducted treatment lines of AD | N = 182
> Median number (IQR) | 3 (2–5)
> ⩾2 | 145/182 (79.7)
> ⩾5 | 52/182 (28.6)
> Details of previous well-conducted lines of AD | 182 (91.0)
> A single AD without augmentation | 129 (64.5)
> A single AD with augmentation | 61 (30.5)
> Combination of AD without augmentation | 59 (29.5)
> Combination of AD with augmentation | 74 (37.0)
> A single augmentation therapy drug | 63 (31.5)
> Combination of augmentation therapy drugs | 18 (9.0)
> Neurostimulation (ECT, rTMS, tDCS) | 45 (22.5)
> No treatment | 6 (3.0)
> 
> TABLE Table 2.: Concomitant antidepressant treatments started before or/at esketamine initiation and ended after.

#### E0094 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[18]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> A Montgomery-Åsberg Depression Rating Scale (MADRS) score of ≥22, denoting moderate or severe depression, was also required for inclusion; moderate and severe depression were defined as a MADRS score of 20–34 and >34, respectively.

#### E0095 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[29]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary objective was to evaluate clinical response, defined as ≥50% improvement in the MADRS total score from baseline to Week 4.

#### E0096 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[30]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Clinical response, remission (defined as MADRS total score of ≤10) and change in disease severity (assessed by CGI-S score) were also evaluated through Week 20.

#### E0097 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[33]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS total score ranges from 0 to 60, with higher values indicating more severe depression ( 27 ).

#### E0098 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[62]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> All patients were classified as having moderate or severe depression, as assessed by MADRS score (moderate: 57.5%; severe: 42.5%; mean: 33.5; Figure 1 ).

#### E0099 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[64]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 1 Severity shifts in MADRS score over time.

#### E0100 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[69]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Mean MADRS score (±SD) declines over time, indicated by a purple line, from 33.5±6.0 at baseline to 19.5±10.6 at week 20.

#### E0101 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[100]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Clinical outcomes Mean MADRS score, and corresponding disease severity, decreased over time (MADRS at Baseline: 33.5; Week 4: 25.5; Week 20: 19.5; Figure 1 ).

#### E0102 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[101]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Numerical reductions in individual MADRS item scores were also observed through Week 20 ( Figure 4 ).

#### E0103 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[102]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 4 MADRS item score evolution over time.

#### E0104 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[103]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> FAS; reporting individual item mean MADRS scores at baseline (N = 153), Week 4 (N = 131; Data missing for one patient), and Week 20 (N = 79).

#### E0105 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[107]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean percentage change in MADRS from baseline (Week 4: −23.8%; Week 20: −40.5%) was statistically significant at both timepoints (p<0.001).

#### E0106 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[108]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> After GEE adjustment, only employment/occupational status was associated with percentage change in MADRS: employed patients (p=0.008) and patients dependent on their partner/spouse or students (p=0.016) demonstrated a greater reduction compared to unemployed patients.

#### E0107 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[109]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At Week 20, patients taking SNRIs or other antidepressants at baseline showed a statistically significant regression (B=–11.146; p=0.038) and had a mean MADRS score percent change of –37.8 compared with patients taking an antipsychotic plus SNRI or other antidepressant (mean MADRS score percent change of –27.0).

#### E0108 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[110]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Employed patients (B=–18.212; p=0.003) demonstrated a statistically significant reduction in mean MADRS score percent change at Week 20 of –35.9 compared with a –19.7 change in unemployed patients.

#### E0109 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[118]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> These results broadly align with other studies in Portugal and Europe more widely; reductions in MADRS and CGI-S scores were seen, but clinical response and remission rates were below 50% and 30%, respectively ( 19 , 20 , 33 ).

#### E0110 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[0]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Key Points Evaluating group-level total score change on the Patient Health Questionnaire (PHQ-9) and Montgomery-Asberg Depression Rating Scale (MADRS) are important assessments of efficacy in adult patients with TRD treated with esketamine plus AD compared with placebo plus AD.

#### E0111 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[2]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Adult patients treated with esketamine plus AD compared with placebo plus AD had improved total scores on both the PHQ-9 and MADRS, and were over two times more likely to improve on symptoms such as having little interest/pleasure in things; feeling down, depressed, or hopeless; and feeling tired or having little energy, as measured by the PHQ-9.

#### E0112 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[15]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The Montgomery-Asberg Depression Rating Scale (MADRS), a 10-item questionnaire reported by the clinician, also mirrors the DSM-5 criteria.

#### E0113 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[18]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Clinicians, patients, and researchers often attempt to interpret the total scores without understanding the contribution of the individual items [ 12 ], which in the PHQ-9 and MADRS are also symptoms.

#### E0114 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[27]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The objective of the analyses was to determine whether individual items in the PHQ-9 and MADRS instruments that measure symptoms show differences by treatment arm over the course of treatment for patients with TRD.

#### E0115 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[55]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS data were collected by independent, remote raters < 2 days prior to the study visit.

#### E0116 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Total scores and change from baseline on the PHQ-9 and MADRS were displayed by treatment arm from baseline to days 15 and 28; treatment differences were calculated using analysis of variance (ANOVA).

#### E0117 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[61]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Categorical distributions of change from baseline in each item of the PHQ-9 and MADRS were displayed graphically for days 15 and 28.

#### E0118 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[63]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The within-patient MCTs for the PHQ-9 and MADRS are 6 points, or 22% of the total score range and 10 points, or 17% of the total score range, respectively [ 14 ].

#### E0119 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[64]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> For example, the minimal important difference (MID) of the MADRS is generally agreed to be 2 points [ 15 ].

#### E0120 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[65]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Individual patients were classified as improved if they had a decrease of at least 1 point on the PHQ-9 items (representing a 25% shift, measured on a 4-point scale) or 2 points on the MADRS items (representing a 29% shift, measured on a 7-point scale).

#### E0121 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[68]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The proportions of patients with categorical improvement from baseline of PHQ-9 and MADRS items, by treatment arm, were calculated at Days 15 and 28.

#### E0122 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[73]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Patient demographic and clinical characteristics, including baseline PHQ-9 and MADRS scores, were similar across all treatment groups (Tables 1 and 2 ).

#### E0123 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 1 Baseline demographic and clinical information Variable Esketamine plus AD n = 114 Placebo plus AD n = 109 Overall N = 223 Age (years) Mean (SD) 44.9 (12.58) 46.4 (11.14) 45.7 (11.89) Time since diagnosis (years) Mean (SD) 12.9 (10.35) 11.1 (10.02) 12.0 (10.21) Sex, n (%) Male 39 (34.2) 46 (42.2) 85 (38.1) Female 75 (65.8) 63 (57.8) 138 (61.9) Race, n (%) White 106 (93.0) 102 (93.6) 208 (93.3) Black or African American 6 (5.3) 5 (4.6) 11 (4.9) Asian 1 (0.9) 1 (0.9) 2 (0.9) Multiple 1 (0.9) 1 (0.9) 2 (0.9) Ethnicity, n (%) Not Hispanic or Latino 108 (94.7) 99 (90.8) 207 (92.8) Hispanic or Latino 5 (4.4) 7 (6.4) 12 (5.4) Not reported 0 (0.0) 1 (0.9) 1 (0.4) Unknown 1 (0.9) 2 (1.8) 3 (1.3) AD antidepressant, SD standard deviation Table 2 PHQ-9 and MADRS total score and change from baseline score at days 15 and 28 Time point Absolute score Change from baseline Treatment difference Placebo plus AD Esketamine plus AD Placebo plus AD Esketamine plus AD n Mean (SD) N Mean (SD) Mean (SD) Mean (SD) Mean (SE) 95% CI p value PHQ-9 Baseline 109 20.4 (3.73) 114 20.2 (3.63) Day 15 104 13.2 (7.20) 111 11.2 (6.33) − 7.1 (6.87) − 9.0 (6.45) − 1.8 (0.91) − 3.62 to − 0.04 0.045 Day 28 100 10.2 (7.68) 104 7.3 (5.74) − 10.2 (7.80) − 13.0 (6.42) − 2.8 (1.00) − 4.75 to − 0.81 0.006 MADRS Baseline 109 37.3 (5.66) 114 37.0 (5.69) Day 15 102 27.2 (11.37) 107 24.8 (10.06) − 10.0 (11.63) − 12.1 (10.58) − 2.0 (1.54) − 5.06 to 1.00 0.189 Day 28 100 20.6 (12.70) 101 15.5 (10.67) − 17.0 (13.88) − 21.4 (12.32) − 4.4 (1.85) − 8.10 to − 0.80 0.017 AD antidepressant, MADRS Montgomery-Asberg Depression Rating Scale, PHQ-9 Patient Health Questionnaire 9-item, SE standard error PHQ-9 Patient-Reported Outcome Findings Total scores on the PHQ-9 improved from baseline to each post-baseline time point in both treatment groups (Table 2 ).

#### E0124 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[91]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> AD antidepressant, CI confidence interval MADRS Clinical-Reported Outcome Findings Total scores on the MADRS improved from baseline to each post-baseline time point in both treatment groups (Table 2 ).

#### E0125 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[92]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> However, the magnitude of change in MADRS was numerically larger in the esketamine/oral AD treatment arm compared with placebo plus AD at day 15 (− 2.0-point mean difference [SE 1.54] between arms; p = 0.189 [95% CI − 5.06 to 1.00]) and statistically significantly larger at day 28 (− 4.4-point mean difference [SE 1.85] between arms; p = 0.017 [95% CI − 8.10 to − 0.80]).

#### E0126 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[99]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 3 Proportions of categorical change from baseline to day 15 and day 28 of Montgomery-Asberg Depression Rating Scale (MADRS) items by treatment group.

#### E0127 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[100]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The MADRS is a 10-item clinician-rated scale used to measure depression severity with each item rated on a 7-point scale.

#### E0128 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[102]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> AD antidepressant More patients in the esketamine plus AD group were rated as having improved by at least 2 points compared with placebo plus AD for all items on the MADRS at both day 15 and day 28 (Fig.

#### E0129 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[104]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Furthermore, the likelihood of experiencing any improvement over the course of the study was larger in the esketamine plus AD treatment arm compared with the placebo plus AD arm for five of the ten MADRS items (nominal p < 0.05): Item 1—“Reported sadness”: OR 1.844 (95% CI 1.014–3.354) Item 2—“Apparent sadness”: OR 2.007 (95% CI 1.096–3.674) Item 3—“Inner tension”: OR 1.891 (95% CI 1.080–3.313) Item 6—“Concentration difficulties”: OR 1.880 (95% CI 1.054–3.354) Item 8—“Inability to feel”: OR 2.099 (95% CI 1.180–3.735).

#### E0130 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[106]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 4 Montgomery-Asberg Depression Rating Scale (MADRS) items from baseline to days 15/28 in esketamine plus AD versus placebo plus AD. *The odds ratio represents the likelihood of improving over the course of the study and includes both day 15 and day 28 data.

#### E0131 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[108]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> AD antidepressant, CI confidence interval Discussion This study demonstrates a pattern of item-level results congruent with the total PHQ-9 and MADRS score change, favoring treatment with esketamine nasal spray plus oral AD versus oral AD plus intranasal placebo.

#### E0132 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[109]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Four out of the nine items on the PHQ-9 and five of the ten items on the MADRS achieved statistical significance, providing a detailed account of the magnitude of which specific depressive symptoms, as measured by single items, are likely to improve from treatment with esketamine nasal spray.

#### E0133 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[110]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In this study, there was a favorable response to all items on both the PHQ-9 and MADRS, indicating overall improvement in depression for those treated with esketamine nasal spray plus oral AD.

#### E0134 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[116]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The particularly favorable results in PHQ-9 items 1, 2, 4, and 6 and MADRS items 1, 2, 3, 6 and 8 suggest improved efficacy of esketamine/oral AD over placebo plus AD in these specific symptoms among TRD adult patients.

#### E0135 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[123]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Similarly, on the MADRS, the likelihood of improving was greatest (OR > 2.0) on the items measuring apparent sadness (item 2) and anhedonia (item 8).

#### E0136 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[124]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> On both instruments, the symptom that was least likely to improve (other than suicidal thoughts) was having a reduced appetite, as measured by item 5 for both the PHQ-9 and MADRS.

#### E0137 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[133]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> This analysis shows the likelihood of improving the individual items on the PHQ-9 and MADRS, enhancing the interpretability of the overall score change for patients and clinicians.

#### E0138 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[135]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> For the MADRS, the greatest improvement was seen on inability to feel, as reported by clinicians [ 21 ].
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE
> Evaluating group-level total score change on the Patient Health Questionnaire (PHQ-9) and Montgomery-Asberg Depression Rating Scale (MADRS) are important assessments of efficacy in adult patients with TRD treated with esketamine plus AD compared with placebo plus AD.

#### E0139 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[137]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Adult patients treated with esketamine plus AD compared with placebo plus AD had improved total scores on both the PHQ-9 and MADRS, and were over two times more likely to improve on symptoms such as having little interest/pleasure in things; feeling down, depressed, or hopeless; and feeling tired or having little energy, as measured by the PHQ-9.

#### E0140 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/35441931#sentence-window[139]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> TABLE Table 1: Baseline demographic and clinical information
> Variable | Esketamine plus AD n = 114 | Placebo plus AD n = 109 | Overall N = 223
> Age (years)
> Mean (SD) | 44.9 (12.58) | 46.4 (11.14) | 45.7 (11.89)
> Time since diagnosis (years)
> Mean (SD) | 12.9 (10.35) | 11.1 (10.02) | 12.0 (10.21)
> Sex, n (%)
> Male | 39 (34.2) | 46 (42.2) | 85 (38.1)
> Female | 75 (65.8) | 63 (57.8) | 138 (61.9)
> Race, n (%)
> White | 106 (93.0) | 102 (93.6) | 208 (93.3)
> Black or African American | 6 (5.3) | 5 (4.6) | 11 (4.9)
> Asian | 1 (0.9) | 1 (0.9) | 2 (0.9)
> Multiple | 1 (0.9) | 1 (0.9) | 2 (0.9)
> Ethnicity, n (%)
> Not Hispanic or Latino | 108 (94.7) | 99 (90.8) | 207 (92.8)
> Hispanic or Latino | 5 (4.4) | 7 (6.4) | 12 (5.4)
> Not reported | 0 (0.0) | 1 (0.9) | 1 (0.4)
> Unknown | 1 (0.9) | 2 (1.8) | 3 (1.3)
> 
> TABLE Table 2: PHQ-9 and MADRS total score and change from baseline score at days 15 and 28
> Time point | Absolute score | Change from baseline | Treatment difference
> Placebo plus AD | Esketamine plus AD | Placebo plus AD | Esketamine plus AD
> n | Mean (SD) | N | Mean (SD) | Mean (SD) | Mean (SD) | Mean (SE) | 95% CI | p value
> PHQ-9
> Baseline | 109 | 20.4 (3.73) | 114 | 20.2 (3.63) |  |  |  |  | 
> Day 15 | 104 | 13.2 (7.20) | 111 | 11.2 (6.33) | − 7.1 (6.87) | − 9.0 (6.45) | − 1.8 (0.91) | − 3.62 to − 0.04 | 0.045
> Day 28 | 100 | 10.2 (7.68) | 104 | 7.3 (5.74) | − 10.2 (7.80) | − 13.0 (6.42) | − 2.8 (1.00) | − 4.75 to − 0.81 | 0.006
> MADRS
> Baseline | 109 | 37.3 (5.66) | 114 | 37.0 (5.69) |  |  |  |  | 
> Day 15 | 102 | 27.2 (11.37) | 107 | 24.8 (10.06) | − 10.0 (11.63) | − 12.1 (10.58) | − 2.0 (1.54) | − 5.06 to 1.00 | 0.189
> Day 28 | 100 | 20.6 (12.70) | 101 | 15.5 (10.67) | − 17.0 (13.88) | − 21.4 (12.32) | − 4.4 (1.85) | − 8.10 to − 0.80 | 0.017

#### E0141 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[58]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At the end of the screening phase, non-responders (≤ 25% improvement in Montgomery-Åsberg Depression Rating Scale [MADRS] total score from week 1 to week 4) discontinued all current antidepressant treatment(s) and were randomized to double-blind treatment, consisting of twice-weekly esketamine nasal spray or matching (appearance, taste, and packaging) placebo nasal spray, each combined with a newly initiated oral antidepressant (SSRI or SNRI) taken daily.

#### E0142 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Assessments Improvement in symptoms of depression was assessed by the MADRS (Williams and Kobak 2008 ), which was administered by independent, blinded raters at baseline and subsequent visits during the double-blind treatment phase.

#### E0143 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[73]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary efficacy endpoint in the TRANSFORM studies—change from baseline to endpoint (day 28) in MADRS total score—was analyzed by sex using a mixed-effects model for repeated measures (MMRM).

#### E0144 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The model included baseline MADRS total score as a covariate, and treatment, study (TRANSFORM-1/TRANSFORM-2 only), region, oral antidepressant class (SNRI or SSRI), day, sex, day-by-treatment, treatment-by-sex, and day-by-treatment-by-sex interaction as fixed effects, and a random patient effect.

#### E0145 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[77]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Response rate (defined as ≥ 50% decrease from baseline MADRS total score) and remission rate (defined as MADRS ≤ 12) at day 28 were analyzed by treatment group and sex using the generalized Cochran-Mantel–Haenszel (CMH) test.

#### E0146 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[90]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 1 Demographic and baseline characteristics by sex in short-term randomized, controlled TRD trials TRANSFORM-1/TRANSFORM-2 TRANSFORM-3 Characteristic Women N = 379 Men N = 186 Total N = 565 Women N = 85 Men N = 52 Total N = 137 Age, years Mean (SD) 46.6 (11.05) 44.9 (12.22) 46.1 (11.46) 70.3 (4.9) 69.5 (3.8) 70.0 (4.52) Range (18; 64) (18; 64) (18; 64) (65; 86) (65; 79) (65; 86) Race, n (%) American Indian or Alaskan Native 1 (0.3) 0 1 (0.2) 0 0 0 Asian 5 (1.3) (1.2) 2 (1.1) 7 (1.2) 0 0 0 Black or African American 23 (6.1) 7 (3.8) 30 (5.3) 0 0 0 White 302 (79.7) 168 (90.3) 470 (83.2) 81 (95.3) 49 (94.2) 130 (94.9) Other 25 (6.6) 4 (2.2) 29 (5.1) 0 0 0 Multiple 1 (0.3) 2 (1.1) 3 (0.5) 2 (2.4) 2 (3.8) 4 (2.9) Not reported 22 (5.8) 3 (1.6) 25 (4.4) 1 (1.2) 1 (1.9) 2 (1.5) Unknown 0 0 0 1 (1.2) 0 1 (0.7) Body mass index (kg/m 2 ) Mean (SD) 28.4 (6.60) 28.7 (5.59) 28.5 (6.28) 28.9 (6.3) 28.9 (4.5) 28.9 (5.64) Range (17; 56) (16; 56) (16; 56) (16; 45) (22; 42) (16; 45) Menopause status a , n (%) Pre-menopausal 182 (48.0) NA NA NA Peri-menopausal 24 (6.3) NA NA NA Post-menopausal—non-surgical 120 (31.7) NA NA NA Post-menopausal—surgical 53 (14.0) NA NA NA Regular menstrual cycles, n (%) N = 203 Yes 160 a (78.8) NA NA NA No 43 (21.2) NA NA NA Median length of typical menstrual cycle (days) 28.0 NA NA NA History of worsening luteal phase, n (%) N = 203 Yes 43 (21.2) NA NA NA No 160 a (78.8) NA NA NA Employment status b , n (%) Any type of employment 218 (57.5) 107 (57.5) 325 (57.5) 14 (16.5) 10 (19.2) 24 (17.5) Any type of unemployment 122 (32.2) 65 (34.9) 187 (33.1) 4 (4.7) 4 (7.7) 8 (5.8) Other 39 (10.3) 14 (7.5) 53 (9.4) 67 (78.8) 38 (73.1) 105 (76.6) Region, n (%) Europe 1542 (37.5) 77 (41.4) 219 (38.8) 40 (47.1) 19 (36.5) 59 (43.1) North America 151 (39.8) 93 (50.0) 244 (43.2) 40 (47.1) 30 (57.7) 70 (51.1) Age when diagnosed with MDD, years Mean (SD) 32.8 (12.69) 31.2 (132.69) 32.3 (12.70) 41.6 (15.9) 45.6 (16.5) 43.1 (16.2) Range (9; 61) (5; 64) (5; 64) (10; 75) (11; 77) (10; 77) Duration of current episode, weeks Mean (SD) 161.5 (236.4) 181.4 (276.5) 168.1 (250.2) 188.6 (279.5) 260.3 (423.6) 215.8 (341.7) Range (6; 2288) (12; 2028) (6; 2288) (8; 1700) (8; 2184) (8; 2184) No. of previous antidepressants c,d , n (%) 1 or 2 245 (65.0) 110 (59.2) 355(63.1) 54 (63.5) 30 (57.7) 84 (61.3) ≥ 3 132 (35.0) 76 (40.8) 208 (36.9) 31 (36.4) 22 (42.3) 53 (38.7) Class of oral antidepressant e , n (%) SNRI 236 (63.3) 112 (60.2) 348 (61.6) 34 (40.0) 27 (51.9) 61 (44.5) SSRI 143 (37.7) 74 (39.8) 217 (38.4) 51 (60.0) 25 (48.1) 76 (55.5) Oral antidepressant, n (%) Duloxetine 174 (45.9) 83 (44.6) 257 (45.5) 25 (29.4) 23 (44.2) 48 (35.0) Escitalopram 74 (19.5) 37 (19.9) 111 (19.6) 36 (42.4) 14 (26.9) 50 (36.5) Sertraline 68 (17.9) 37 (19.9) 105 (18.6) 14 (16.5) 11 (21.2) 25 (18.2) Venlafaxine XR 63 (16.6) 29 (15.6) 92 (16.3) 10 (11.8) 4 (7.7) 14 (10.2) CGI-S Mean (SD) 5.1 (0.67) 5.1 (0.72) 5.1 (0.68) 5.0 (0.75) 5.0 (0.85) 5.0 (0.79) MADRS total score Mean (SD) 37.7 (5.73) 36.8 (5.21) 37.4 (5.57) 35.2 (6.41) 35.2 (5.78) 35.2 (6.16) PHQ-9 total score Mean (SD) 20.6 (3.67) 20.3 (3.91) 20.5 (3.75) 17.6 (5.53) 17.4 (5.87) 17.5 (5.65) SDS total score Mean (SD) 24.5 (4.09) 23.9 (4.40) 24.3 (4.20) 23.2 (5.12) 21.3 (5.49) 22.3 (5.36) GAD-7 total score Mean (SD) 13.4 (5.23) 12.9 (5.02) 13.2 (5.16) NA NA NA Abbreviations: CGI-S Clinical Global Impression–Severity; MDD major depressive disorder; NA not applicable or not available, not administered; PHQ Patient Health Questionnaire; SNRI serotonin and norepinephrine reuptake inhibitor; SSRI selective serotonin reuptake inhibitor; TRD treatment-resistant depression a Data from the Massachusetts General Hospital Female Reproductive Lifecycle and Hormones Questionnaire, Module I (Freeman et al.

#### E0147 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[100]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> GAD-7 was not conducted in the TRANSFORM-3 study Table 3 Concomitant medications most frequently used during double-blind treatment in short-term randomized, controlled TRD trials Women Men Specific or category of concomitant medication Esketamine + antidepressant N = 282 Antidepressant + placebo N = 184 Esketamine + antidepressant N = 136 Antidepressant + placebo N = 103 Benzodiazepine 140 (49.6%) 86 (46.7%) 66 (48.5%) 36 (35.0%) Analgesic 79 (28.0%) 57 (31.0%) 34 (25.0%) 24 (23.3%) Antihypertensive 62 (22.0%) 53 (28.8%) 33 (24.3%) 32 (31.1%) Lipid-lowering agent 45 (16.0%) 36 (19.6%) 32 (23.5%) 28 (27.2%) Proton pump inhibitor 40 (14.2%) 28 (15.2%) 24 (17.6%) 11 (10.7%) Beta-blocker 34 (12.1%) 21 (11.4%) 21 (15.4%) 9 (8.7%) Thyroid medications 37 (13.1%) 35 (19.0%) 5 (3.7%) 8 (7.8%) Levothyroxine 36 (12.8%) 33 (17.9%) 5 (3.7%) 7 (6.8%) Hormonal therapy a 49 (17.4%) 24 (13.0%) NA NA TRANSFORM-1/2 Pre-menopausal 39/112 (34.8%) 15/70 (21.4%) Peri-menopausal 6/15 (40.0%) 2/9 (22.2%) Post-menopausal 4/108 (3.7%) 4/65 (6.2%) TRANSFORM-3 0/45 (0.0%) 3/40 (7.5%) The table lists, in descending order of frequency for all patients, all specific or categories of concomitant medication with a usage rate during double-blind treatment of ≥ 10% in either treatment group, without regard to sex a Includes hormone replacement therapy and oral contraceptives Mean MADRS total score decreased from baseline to day 28, with greater improvement among those treated with esketamine/antidepressant compared to antidepressant/placebo among both women and men.

#### E0148 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[101]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean MADRS change (SD) at day 28 for the esketamine/antidepressant and antidepressant/placebo groups were -20.3 (13.19) vs. -15.8 (14.67), respectively, among the women and -18.3 (14.08) vs. -16.0 (14.30), respectively, among the men in TRANSFORM-1/TRANSFORM-2; and -9.9 (13.34) vs. -6.9 (9.65), respectively, among the women and -10.3 (11.96) vs. -5.5 (7.64), respectively, among the men in TRANSFORM-3 (Table 4 ).

#### E0149 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[103]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 4 MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group TRANSFORM-1/TRANSFORM-2 TRANSFORM-3 Women Men Women Men Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Baseline N 235 144 108 78 45 40 27 25 Mean (SD) 37.7 (5.49) 37.7 (6.11) 36.9 (5.02) 36.7 (5.50) 35.7 (5.90) 34.5 (6.97) 35.2 (6.04) 35.1 (5.60) Change to day 28 N 215 138 95 70 39 36 24 24 Mean (SD) -20.3 (13.19) -15.8 (14.67) -18.3 (14.08) -16.0 (14.30) -9.9 (13.34) -6.9 (9.65) -10.3 (11.96) -5.5 (7.64) MMRM analysis a Diff. of LS means b (SE) -4.5 (1.41) -1.6 (2.04) -3.4 (2.41) -5.0 (3.05) 95% CI on difference -7.26, − 1.70 -5.60, 2.41 -8.14, 1.41 -11.05, 1.03 MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition.

#### E0150 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[106]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The p -values were 0.6574 and 0.3993 for sex, and 0.3546 and 0.4937 for treatment-by-sex interaction in the TRANSFORM-1/2 and TRANSFORM-3 studies, respectively CI confidence interval; LS least squares; MADRS Montgomery-Asberg Depression Rating Scale; TRD treatment-resistant depression a Mixed model for repeated measures (MMRM) analysis with change from baseline as the response variable and the fixed effect model terms for study number (pooled only), treatment (esketamine + antidepressant, antidepressant + placebo) day, region, class of antidepressant (SNRI or SSRI), sex, and treatment-by-day, treatment-by-sex, and treatment-by-day-by-sex, and baseline value as a covariate b Esketamine + antidepressant minus antidepressant + placebo In the TRANSFORM trials, the proportions of patients who were responders at day 28 and the proportion of patients in remission at day 28 were numerically higher among both women and men treated with esketamine/antidepressant as compared to antidepressant/placebo (Fig.

#### E0151 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[116]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes: Response defined as ≥ 50% decrease from baseline Montgomery-Asberg Depression Rating Scale (MADRS) total score.

#### E0152 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[117]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Remission defined as MADRS total score ≤ 12.

#### E0153 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[120]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes: Response defined as ≥ 50% decrease from baseline Montgomery-Asberg Depression Rating Scale (MADRS) total score Treatment benefit of esketamine was also observed in terms of functioning and self-reported depression for both women and men in the pooled TRANSFORM-1/TRANSFORM-2 trials (Table 5 , Fig.

#### E0154 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[144]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Furthermore, the between-group difference observed vs. antidepressant/placebo for both sex subgroups in TRANSFORM-1/TRANSFORM-2 and TRANSFORM-3 was in the range considered clinically meaningful (2-point to 3-point difference) (Montgomery and Möller 2009 ; Kim et al.

#### E0155 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[194]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> These findings add to the existing literature and support data-informed decision-making for women with TRD.
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1: Demographic and baseline characteristics by sex in short-term randomized, controlled TRD trials
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
> Characteristic | Women N = 379 | Men N = 186 | Total N = 565 | Women N = 85 | Men N = 52 | Total N = 137
> Age, years |  |  |  |  |  | 
> Mean (SD) | 46.6 (11.05) | 44.9 (12.22) | 46.1 (11.46) | 70.3 (4.9) | 69.5 (3.8) | 70.0 (4.52)
> Range | (18; 64) | (18; 64) | (18; 64) | (65; 86) | (65; 79) | (65; 86)
> Race, n (%) |  |  |  |  |  | 
> American Indian or Alaskan Native | 1 (0.3) | 0 | 1 (0.2) | 0 | 0 | 0
> Asian | 5 (1.3) (1.2) | 2 (1.1) | 7 (1.2) | 0 | 0 | 0
> Black or African American | 23 (6.1) | 7 (3.8) | 30 (5.3) | 0 | 0 | 0
> White | 302 (79.7) | 168 (90.3) | 470 (83.2) | 81 (95.3) | 49 (94.2) | 130 (94.9)
> Other | 25 (6.6) | 4 (2.2) | 29 (5.1) | 0 | 0 | 0
> Multiple | 1 (0.3) | 2 (1.1) | 3 (0.5) | 2 (2.4) | 2 (3.8) | 4 (2.9)
> Not reported | 22 (5.8) | 3 (1.6) | 25 (4.4) | 1 (1.2) | 1 (1.9) | 2 (1.5)
> Unknown | 0 | 0 | 0 | 1 (1.2) | 0 | 1 (0.7)
> Body mass index (kg/m 2 ) |  |  |  |  |  | 
> Mean (SD) | 28.4 (6.60) | 28.7 (5.59) | 28.5 (6.28) | 28.9 (6.3) | 28.9 (4.5) | 28.9 (5.64)
> Range | (17; 56) | (16; 56) | (16; 56) | (16; 45) | (22; 42) | (16; 45)
> Menopause status a , n (%) |  |  |  |  |  | 
> Pre-menopausal | 182 (48.0) | NA |  | NA | NA | 
> Peri-menopausal | 24 (6.3) | NA |  | NA | NA | 
> Post-menopausal—non-surgical | 120 (31.7) | NA |  | NA | NA | 
> Post-menopausal—surgical | 53 (14.0) | NA |  | NA | NA | 
> Regular menstrual cycles, n (%) | N = 203 |  |  |  |  | 
> Yes | 160 a (78.8) | NA |  | NA | NA | 
> No | 43 (21.2) | NA |  | NA | NA | 
> Median length of typical menstrual cycle (days) | 28.0 | NA |  | NA | NA | 
> History of worsening luteal phase, n (%) | N = 203 |  |  |  |  | 
> Yes | 43 (21.2) | NA |  | NA | NA | 
> No | 160 a (78.8) | NA |  | NA | NA | 
> Employment status b , n (%) |  |  |  |  |  | 
> Any type of employment | 218 (57.5) | 107 (57.5) | 325 (57.5) | 14 (16.5) | 10 (19.2) | 24 (17.5)
> Any type of unemployment | 122 (32.2) | 65 (34.9) | 187 (33.1) | 4 (4.7) | 4 (7.7) | 8 (5.8)
> Other | 39 (10.3) | 14 (7.5) | 53 (9.4) | 67 (78.8) | 38 (73.1) | 105 (76.6)
> Region, n (%) |  |  |  |  |  | 
> Europe | 1542 (37.5) | 77 (41.4) | 219 (38.8) | 40 (47.1) | 19 (36.5) | 59 (43.1)
> North America | 151 (39.8) | 93 (50.0) | 244 (43.2) | 40 (47.1) | 30 (57.7) | 70 (51.1)
> Age when diagnosed with MDD, years |  |  |  |  |  | 
> Mean (SD) | 32.8 (12.69) | 31.2 (132.69) | 32.3 (12.70) | 41.6 (15.9) | 45.6 (16.5) | 43.1 (16.2)
> Range | (9; 61) | (5; 64) | (5; 64) | (10; 75) | (11; 77) | (10; 77)
> Duration of current episode, weeks |  |  |  |  |  | 
> Mean (SD) | 161.5 (236.4) | 181.4 (276.5) | 168.1 (250.2) | 188.6 (279.5) | 260.3 (423.6) | 215.8 (341.7)
> Range | (6; 2288) | (12; 2028) | (6; 2288) | (8; 1700) | (8; 2184) | (8; 2184)
> No. of previous antidepressants c,d , n (%) |  |  |  |  |  | 
> 1 or 2 | 245 (65.0) | 110 (59.2) | 355(63.1) | 54 (63.5) | 30 (57.7) | 84 (61.3)
> ≥ 3 | 132 (35.0) | 76 (40.8) | 208 (36.9) | 31 (36.4) | 22 (42.3) | 53 (38.7)
> Class of oral antidepressant e , n (%) |  |  |  |  |  | 
> SNRI | 236 (63.3) | 112 (60.2) | 348 (61.6) | 34 (40.0) | 27 (51.9) | 61 (44.5)
> SSRI | 143 (37.7) | 74 (39.8) | 217 (38.4) | 51 (60.0) | 25 (48.1) | 76 (55.5)
> Oral antidepressant, n (%) |  |  |  |  |  | 
> Duloxetine | 174 (45.9) | 83 (44.6) | 257 (45.5) | 25 (29.4) | 23 (44.2) | 48 (35.0)
> Escitalopram | 74 (19.5) | 37 (19.9) | 111 (19.6) | 36 (42.4) | 14 (26.9) | 50 (36.5)
> Sertraline | 68 (17.9) | 37 (19.9) | 105 (18.6) | 14 (16.5) | 11 (21.2) | 25 (18.2)
> Venlafaxine XR | 63 (16.6) | 29 (15.6) | 92 (16.3) | 10 (11.8) | 4 (7.7) | 14 (10.2)
> CGI-S |  |  |  |  |  | 
> Mean (SD) | 5.1 (0.67) | 5.1 (0.72) | 5.1 (0.68) | 5.0 (0.75) | 5.0 (0.85) | 5.0 (0.79)
> MADRS total score |  |  |  |  |  | 
> Mean (SD) | 37.7 (5.73) | 36.8 (5.21) | 37.4 (5.57) | 35.2 (6.41) | 35.2 (5.78) | 35.2 (6.16)
> PHQ-9 total score |  |  |  |  |  | 
> Mean (SD) | 20.6 (3.67) | 20.3 (3.91) | 20.5 (3.75) | 17.6 (5.53) | 17.4 (5.87) | 17.5 (5.65)
> SDS total score |  |  |  |  |  | 
> Mean (SD) | 24.5 (4.09) | 23.9 (4.40) | 24.3 (4.20) | 23.2 (5.12) | 21.3 (5.49) | 22.3 (5.36)
> GAD-7 total score |  |  |  |  |  | 
> Mean (SD) | 13.4 (5.23) | 12.9 (5.02) | 13.2 (5.16) | NA | NA | NA
> 
> TABLE Table 2: Comorbidities of study patients in short-term randomized, controlled TRD trials
>  | Number (%) of patients
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
> Comorbidities | Women N = 379 | Men N = 186 | Total N = 565 | Women N = 85 | Men N = 52 | Total N = 137
> Anxiety a | 272 (71.8%) | 132 (71.0%) | 404 (71.5%) | NA | NA | NA
> Incidental surgery | 166 (43.8%) | 55 (29.6%) | 221 (39.1%) | 37 (43.5%) | 19 (36.5%) | 56 (40.9%)
> Hypertension | 79 (20.8%) | 38 (20.4%) | 117 (20.7%) | 46 (54.1%) | 28 (53.8%) | 74 (54.0%)
> Allergies | 69 (18.2%) | 31 (16.7%) | 100 (17.7%) | 11 (12.9%) | 4 (7.7%) | 15 (10.9%)
> Thyroid disease | 57 (15.0%) | 10 (5.4%) | 67 (11.9%) | 23 (27.1%) | 6 (11.5%) | 29 (21.2%)
> GERD | 48 (12.7%) | 15 (8.1%) | 63 (11.2%) | 13 (15.3%) | 8 (15.4%) | 21 (15.3%)
> Trauma | 27 (7.1%) | 31 (16.7%) | 58 (10.3%) | 5 (5.9%) | 3 (5.8%) | 8 (5.8%)
> Cardiovascular disease | 24 (6.3%) | 13 (7.0%) | 37 (6.5%) | 10 (11.8%) | 12 (23.1%) | 22 (16.1%)
> Diabetes | 25 (6.6%) | 8 (4.3%) | 33 (5.8%) | 13 (15.3%) | 13 (25.0%) | 26 (19.0%)
> Oncology | 13 (3.4%) | 5 (2.7%) | 18 (3.2%) | 16 (18.8%) | 11 (21.2%) | 27 (19.7%)
> Skin disorder | 23 (6.1%) | 13 (7.0%) | 36 (6.4%) | 3 (3.5%) | 4 (7.7%) | 7 (5.1%)
> Infection | 25 (6.6%) | 6 (3.2%) | 31 (5.5%) | 2 (2.4%) | 2 (3.8%) | 4 (2.9%)
> Respiratory disease | 12 (3.2%) | 2 (1.1%) | 14 (2.5%) | 1 (1.2%) | 0 | 1 (0.7%)
> Parathyroid disease | 2 (0.5%) | 1 (0.5%) | 3 (0.5%) | 0 | 1 (1.9%) | 1 (0.7%)
> 
> TABLE Table 3: Concomitant medications most frequently used during double-blind treatment in short-term randomized, controlled TRD trials
>  | Women | Men
> Specific or category of concomitant medication | Esketamine + antidepressant N = 282 | Antidepressant + placebo N = 184 | Esketamine + antidepressant N = 136 | Antidepressant + placebo N = 103
> Benzodiazepine | 140 (49.6%) | 86 (46.7%) | 66 (48.5%) | 36 (35.0%)
> Analgesic | 79 (28.0%) | 57 (31.0%) | 34 (25.0%) | 24 (23.3%)
> Antihypertensive | 62 (22.0%) | 53 (28.8%) | 33 (24.3%) | 32 (31.1%)
> Lipid-lowering agent | 45 (16.0%) | 36 (19.6%) | 32 (23.5%) | 28 (27.2%)
> Proton pump inhibitor | 40 (14.2%) | 28 (15.2%) | 24 (17.6%) | 11 (10.7%)
> Beta-blocker | 34 (12.1%) | 21 (11.4%) | 21 (15.4%) | 9 (8.7%)
> Thyroid medications | 37 (13.1%) | 35 (19.0%) | 5 (3.7%) | 8 (7.8%)
> Levothyroxine | 36 (12.8%) | 33 (17.9%) | 5 (3.7%) | 7 (6.8%)
> Hormonal therapy a | 49 (17.4%) | 24 (13.0%) | NA | NA
> TRANSFORM-1/2 |  |  |  | 
> Pre-menopausal | 39/112 (34.8%) | 15/70 (21.4%) |  | 
> Peri-menopausal | 6/15 (40.0%) | 2/9 (22.2%) |  | 
> Post-menopausal | 4/108 (3.7%) | 4/65 (6.2%) |  | 
> TRANSFORM-3 | 0/45 (0.0%) | 3/40 (7.5%) |  | 
> 
> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 | 
> 
> TABLE Table 5: Mean (SD) change from baseline to day 28 for SDS, PHQ-9, and GAD-7 total score by sex in pooled TRANSFORM-1/TRANSFORM-2 trials
>  | TRANSFORM-1/TRANSFORM-2
>  | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> SDS total score |  |  |  | 
> N | 177 | 115 | 84 | 60
> Mean (SD) | -12.5 (9.30) | -9.6 (9.50) | -10.6 (9.22) | -7.4 (8.12)
> PHQ-9 total score |  |  |  | 
> N | 218 | 138 | 95 | 70
> Mean (SD) | -12.3 (7.39) | -10.1 (7.99) | -10.9 (7.62) | -8.6 (8.25)
> GAD-7 total score |  |  |  | 
> N | 227 | 139 | 103 | 74
> Mean (SD) | -8.1 (5.90) | -6.9 (5.78) | -6.7 (5.84) | -5.4 (5.98)
> 
> TABLE Table 6: Most frequently reported treatment-emergent adverse events in the double-blind treatment phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant N = 237 | Antidepressant + placebo N = 144 | Esketamine + antidepressant N = 109 | Antidepressant + placebo N = 78 | Esketamine + antidepressant N = 45 | Antidepressant + placebo N = 40 | Esketamine + antidepressant N = 27 | Antidepressant + placebo N = 25
> Total with AEs | 209 (88.2%) | 96 (66.7%) | 92 (84.4%) | 47 (60.3%) | 34 (75.6%) | 23 (57.5%) | 17 (63.0%) | 16 (64.0%)
> Nausea | 72 (30.4%) | 11 (7.6%) | 26 (23.9%) | 8 (10.3%) | 9 (20.0%) | 3 (7.5%) | 4 (14.8%) | 0
> Headache | 52 (21.9%) | 21 (14.6%) | 18 (16.5%) | 17 (21.8%) | 6 (13.3%) | 1 (2.5%) | 3 (11.1%) | 1 (4.0%)
> Dizziness | 53 (22.4%) | 10 (6.9%) | 29 (26.6%) | 5 (6.4%) | 13 (28.9%) | 4 (10.0%) | 2 (7.4%) | 1 (4.0%)
> Dissociation | 68 (28.7%) | 7 (4.9%) | 24 (22.2%) | 1 (1.3%) | 7 (15.6%) | 1 (2.5%) | 2 (7.4%) | 0
> Vertigo | 62 (26.2%) | 5 (3.5%) | 16 (14.7%) | 0 | 4 (8.9%) | 2 (5.0%) | 4 (14.8%) | 0
> Dysgeusia | 46 (19.4%) | 19 (13.2%) | 19 (17.4%) | 11 (14.1%) | 2 (4.4%) | 3 (7.5%) | 2 (7.4%) | 0
> Somnolence | 39 (16.5%) | 15 (10.4%) | 21 (19.3%) | 5 (6.4%) | 1 (2.2%) | 3 (7.5%) | 0 | 0
> Paresthesia | 31 (13.1%) | 2 (1.4%) | 12 (11.0%) | 2 (2.6%) | 2 (4.4%) | 2 (5.0%) | 2 (7.4%) | 0
> Anxiety | 19 (8.0%) | 10 (6.9%) | 12 (11.0%) | 2 (2.6%) | 2 (4.4%) | 2 (5.0%) | 0 | 3 (12.0%)
> Fatigue | 19 (8.0%) | 9 (6.3%) | 6 (5.5%) | 2 (2.6%) | 7 (15.6%) | 4 (10.0%) | 2 (7.4%) | 1 (4.0%)
> BP increased | 16 (6.8%) | 3 (2.1%) | 14 (12.8%) | 2 (2.6%) | 8 (17.8%) | 3 (7.5%) | 1 (3.7%) | 0
> Hypoesthesia | 25 (10.5%) | 1 (0.7%) | 13 (11.9%) | 2 (2.6%) | 3 (6.7%) | 1 (2.5%) | 1 (3.7%) | 0
> Hypoesthesia oral | 29 (12.2%) | 2 (1.4%) | 8 (7.3%) | 1 (1.3%) | 4 (8.9%) | 0 | 1 (3.7%) | 0
> Vomiting | 27 (11.4%) | 3 (2.1%) | 5 (4.6%) | 1 (1.3%) | 5 (11.1%) | 0 | 0 | 1 (4.0%)
> UTI | 6 (2.5%) | 2 (1.4%) | 0 | 1 (1.3%) | 6 (13.3%) | 1 (2.5%) | 0 | 0

#### E0156 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[11]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> This approval was based, in large part, on the results of the pivotal, flexible‐dose short‐term TRANSFORM‐2 study in which mean Montgomery–Åsberg Depression Rating Scale (MADRS) total score decreased from 37 at baseline through day 28 with esketamine/antidepressant (LS mean change [95% CI]: −21.4 [−21.2 to −18.3]) and with antidepressant/placebo (−15.8 [−17.6 to −14.1]), with greater improvement among the esketamine‐treated patients (difference of LS means at day 28: −4.0, 95% CI: −7.3 to −0.6, p = .020) (Popova et al., 2019 ).

#### E0157 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[24]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The MADRS (Williams & Kobak, 2008 ) was administered at baseline and on days 2, 8, 15, 22, and 28 of the double‐blind treatment phase by off‐site, independent blinded raters.

#### E0158 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[36]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Change in MADRS total score from baseline to day 28 was compared within treatment groups by paired t test and between treatment groups using analysis of covariance (ANCOVA) with fixed effects for treatment group, comorbid anxiety condition, and baseline value as a covariate.

#### E0159 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[39]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Response (defined as ≥50% improvement in MADRS total score from baseline) and remission (defined as MADRS total score ≤12) rates at day 28 were compared between treatment groups using the Cochran–Mantel–Haenzsel (CMH) test controlling for region, and class of oral antidepressant (SNRI or SSRI).

#### E0160 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[50]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Patients with comorbid anxiety appeared to have more chronic depressive symptoms compared to patients without comorbid anxiety based on longer mean duration of current episode and higher mean MADRS score at baseline (Table 1 ).

#### E0161 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[52]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 1 Baseline demographics and disease characteristics by status of comorbid anxiety among patients with treatment‐resistant depression Comorbid anxiety No comorbid anxiety Parameter Esketamine + Antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo n = 83 n = 79 n = 31 n = 30 Mean age, years (SD) 44.9 (12.91) 45.4 (11.09) 45.1 (11.84) 49.1 (11.01) Sex, n (%) Female 32 (38.5) 31 (39.2) 7 (22.6) 15 (50.0) Male 51 (61.5) 48 (60.8) 24 (77.4) 15 (50.0) Race, n (%) White 77 (92.8) 74 (93.7) 29 (93.6) 28 (93.3) Black/African American 5 (6.0) 3 (3.8) 1 (3.2) 2 (6.7) Other 1 (1.2) 2 (2.5) 1 (3.2) 0 (0) Region Europe 52 (62.7) 52 (65.8) 17 (54.8) 13 (43.3) North America 31 (37.3) 27 (34.2) 14 (45.2) 17 (56.7) Mean duration of current episode, weeks (SD) 122.3 (133.6) 130.6 (208.9) 82.3 (90.4) 84.8 (108.7) History of suicidal ideation during prior 6 months, assessed by C‐SSRS, n (%) 29 (34.9) 23 (29.1) 8 (25.8) 11 (36.7) No. of previous antidepressants, n (%) a 1 or 2 75 (90.4) 68 (86.1) 27 (87.1) 26 (86.7) ≥3 8 (9.6) 11 (13.9) 4 (12.9) 4 (13.3) Class of oral antidepressant, n (%) SNRI 57 (68.7) 58 (73.4) 20 (64.5) 17 (56.7) SSRI 26 (31.3) 21 (26.6) 11 (35.5) 13 (43.3) Mean MADRS total score (SD) 37.4 (5.43) 38.5 (5.48) 36.0 (6.33) 34.1 (4.92) GAD‐7 total score at baseline Mean (SD) 15.2 (4.0) 15.1 (3.5) 7.8 (3.7) 7.7 (3.6) ≥10 b , n (%) 80 (96.4) 74 (93.7) 0 0 Comorbid anxiety disorder c at screening, n (%) 17 (20.5) 13 (16.5) 0 0 Note : Comorbid anxiety was determined if the patient had one of the following at screening: generalized anxiety disorder current, panic disorder current, social anxiety disorder current, posttraumatic stress disorder current, or obsessive‐compulsive disorder current by MINI, or GAD‐7 total score of ≥10 at screening and baseline.

#### E0162 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[53]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Abbreviations: C‐SSRS, Columbia‐Suicide Severity Rating Scale; GAD‐7, Generalized Anxiety Disorder 7‐item scale; MADRS, Montgomery‐Åsberg Depression Rating Scale; MGH‐ATRQ, Massachusetts General Hospital Antidepressant Treatment Response Questionnaire; MINI, Mini‐International Neuropsychiatric Interview; SD, standard deviation; SNRI, serotonin‐norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor. a Number of antidepressant medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained at screening from MGH‐ATRQ. b At screening and at baseline. c Comorbid anxiety disorder was determined if the patient had one of generalized anxiety disorder current, panic disorder current, social anxiety disorder current, posttraumatic stress disorder current, or obsessive‐compulsive disorder current by MINI.

#### E0163 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[56]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At day 28, esketamine‐treated patients with and without anxiety demonstrated significant reductions in MADRS (mean [SD] change from baseline: patients with comorbid anxiety [ n = 72]: −21.0 [12.51], 95% CI: −23.6 to −18.1; and patients without comorbid anxiety [ n = 29]: −22.7 [11.98], 95% CI: −28.4 to −19.8).

#### E0164 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[57]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In analyses of depressive symptoms by comorbid anxiety status (either symptoms or disorder) across both treatment groups, treatment effect based on change in MADRS total score from baseline to day 28 was significantly different, with a greater improvement in MADRS scores among those treated with esketamine/antidepressant as compared to antidepressant/placebo (Figure 1 ) (difference of LS means – patients with comorbid anxiety [ n = 144 at day 28]: −4.2, 95% CI: −8.1 to −0.3; patients without comorbid anxiety [ n = 57 at day 28]: −7.5, 95% CI: −13.7 to −1.3).

#### E0165 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[59]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 1 Least square mean change (SE) in Montgomery–Åsberg depression rating scale total score over time in the double‐blind treatment phase.

#### E0166 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Note: Treatment effect based on change in Montgomery–Åsberg depression rating scale (MADRS) total score from baseline to day 28 was not statistically significantly different (interaction term p = .371) between the without/with anxiety groups (difference in LS means 3.3, 95% CI −4.0 to 10.6), with a greater improvement in MADRS scores among those treated with esketamine/antidepressant as compared to antidepressant/placebo (patients without comorbid anxiety: −7.5, −13.7 to −1.3; p = .017; patients with comorbid anxiety: −4.2, −8.1 to −0.3; p = .036).

#### E0167 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[61]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Abbreviations: AD, antidepressant; ESK, esketamine; LS, least squares; PBO, placebo; SE, standard error Table 2 Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety Comorbid Anxiety No comorbid anxiety Esketamine + antidepressant Antidepressant + Placebo Esketamine + Antidepressant Antidepressant + Placebo Baseline N 83 79 31 30 Mean (SD) 37.4 (5.42) 38.5 (5.48) 36.0 (6.33) 34.1 (4.92) Change from baseline to day 28 N 72 72 29 28 Mean (SD) −21.0 (12.51) −18.3 (13.99) −22.7 (11.98) −13.6 (13.25) p value based on pared t‐test < .001 < .001 < .001 < .001 ANCOVA analysis a of treatment groups within same status of comorbid anxiety Difference of LS means b (SE) −4.2 (1.97) −7.5 (3.12) 95% CI on difference −8.1 to −0.3 −13.7 to − 1.3 p value on difference .036 .017 ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no Difference of LS means d (SE) 3.3 (3.71) 95% CI on difference −4.0 to 10.6 p value .371 Notes : Anxious depression was determined if the patient had one of the following at screening: generalized anxiety disorder current, panic disorder current social anxiety disorder current, posttraumatic stress disorder current, or obsessive‐compulsive disorder current, or had GAD‐7 total ≥10 both at screening and at baseline.

#### E0168 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[62]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition.

#### E0169 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 2 Response and remission rates at day 28 based on Montgomery–Åsberg depression rating scale total score. * p < .05 from CMH test.

#### E0170 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[75]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Note: Response was defined as a ≥50% improvement in MADRS total score from baseline.

#### E0171 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[76]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Remission was defined as MADRS total score ≤12.

#### E0172 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[78]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> CI, confidence interval; CMH, Cochran–Mantel–Haenzsel; MADRS, Montgomery–Åsberg depression rating scale In terms of safety, the most common adverse events reported for esketamine‐treated patients (>10% of all patients) were anxiety, blurred vision, dissociation, dizziness, dysgeusia (metallic taste), headache, nausea, paresthesia, somnolence, and vertigo (Table 3 ), with a higher incidence in the esketamine/antidepressant group than the antidepressant/placebo group.

#### E0173 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[96]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> After 4 weeks of treatment, higher response and remission rates and a significantly greater decrease in MADRS total score were observed in the esketamine/antidepressant group than in the antidepressant/placebo group, with or without comorbid anxiety.

#### E0174 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34293233#sentence-window[153]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> PEER REVIEW The peer review history for this article is available at https://publons.com/publon/10.1002/da.23193
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1: Baseline demographics and disease characteristics by status of comorbid anxiety among patients with treatment‐resistant depression
>  | Comorbid anxiety | No comorbid anxiety
> Parameter | Esketamine + Antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> n = 83 | n = 79 | n = 31 | n = 30
> Mean age, years (SD) | 44.9 (12.91) | 45.4 (11.09) | 45.1 (11.84) | 49.1 (11.01)
> Sex, n (%) |  |  |  | 
> Female | 32 (38.5) | 31 (39.2) | 7 (22.6) | 15 (50.0)
> Male | 51 (61.5) | 48 (60.8) | 24 (77.4) | 15 (50.0)
> Race, n (%) |  |  |  | 
> White | 77 (92.8) | 74 (93.7) | 29 (93.6) | 28 (93.3)
> Black/African American | 5 (6.0) | 3 (3.8) | 1 (3.2) | 2 (6.7)
> Other | 1 (1.2) | 2 (2.5) | 1 (3.2) | 0 (0)
> Region |  |  |  | 
> Europe | 52 (62.7) | 52 (65.8) | 17 (54.8) | 13 (43.3)
> North America | 31 (37.3) | 27 (34.2) | 14 (45.2) | 17 (56.7)
> Mean duration of current episode, weeks (SD) | 122.3 (133.6) | 130.6 (208.9) | 82.3 (90.4) | 84.8 (108.7)
> History of suicidal ideation during prior 6 months, assessed by C‐SSRS, n (%) | 29 (34.9) | 23 (29.1) | 8 (25.8) | 11 (36.7)
> No. of previous antidepressants, n (%) a |  |  |  | 
> 1 or 2 | 75 (90.4) | 68 (86.1) | 27 (87.1) | 26 (86.7)
> ≥3 | 8 (9.6) | 11 (13.9) | 4 (12.9) | 4 (13.3)
> Class of oral antidepressant, n (%) |  |  |  | 
> SNRI | 57 (68.7) | 58 (73.4) | 20 (64.5) | 17 (56.7)
> SSRI | 26 (31.3) | 21 (26.6) | 11 (35.5) | 13 (43.3)
> Mean MADRS total score (SD) | 37.4 (5.43) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> GAD‐7 total score at baseline |  |  |  | 
> Mean (SD) | 15.2 (4.0) | 15.1 (3.5) | 7.8 (3.7) | 7.7 (3.6)
> ≥10 b , n (%) | 80 (96.4) | 74 (93.7) | 0 | 0
> Comorbid anxiety disorder c at screening, n (%) | 17 (20.5) | 13 (16.5) | 0 | 0
> 
> TABLE Table 2: Change in MADRS total score from baseline to day 28 in patients with TRD and comorbid anxiety
>  | Comorbid Anxiety | No comorbid anxiety
>  | Esketamine + antidepressant | Antidepressant + Placebo | Esketamine + Antidepressant | Antidepressant + Placebo
> Baseline |  |  |  | 
> N | 83 | 79 | 31 | 30
> Mean (SD) | 37.4 (5.42) | 38.5 (5.48) | 36.0 (6.33) | 34.1 (4.92)
> Change from baseline to day 28 |  |  |  | 
> N | 72 | 72 | 29 | 28
> Mean (SD) | −21.0 (12.51) | −18.3 (13.99) | −22.7 (11.98) | −13.6 (13.25)
> p value based on pared t‐test | < .001 | < .001 | < .001 | < .001
> ANCOVA analysis a of treatment groups within same status of comorbid anxiety |  |  |  | 
> Difference of LS means b (SE) | −4.2 (1.97) |  | −7.5 (3.12) | 
> 95% CI on difference | −8.1 to −0.3 |  | −13.7 to − 1.3 | 
> p value on difference | .036 |  | .017 | 
> ANCOVA analysis c of treatment groups under comorbid anxiety, yes versus no |  |  |  | 
> Difference of LS means d (SE) |  |  |  | 3.3 (3.71)
> 95% CI on difference |  |  |  | −4.0 to 10.6
> p value |  |  |  | .371
> 
> TABLE Table 3: Most frequently reported treatment‐emergent adverse events in the double‐blind treatment phase of randomized controlled trials of treatment‐resistant depression
>  | Number (%) of patients
>  | Comorbid anxiety | No comorbid anxiety
> Adverse event | Esketamine + antidepressant n = 83 | Antidepressant + placebo n = 79 | Esketamine + antidepressant n = 31 | Antidepressant + placebo n = 30
> Nausea | 24 (28.9) | 6 (7.6) | 6 (19.4) | 1 (3.3)
> Dissociation | 22 (26.5) | 2 (2.5) | 8 (25.8) | 2 (6.7)
> Vertigo | 20 (24.1) | 3 (3.8) | 10 (32.3) | 0
> Dysgeusia | 18 (21.1) | 10 (12.7) | 10 (32.3) | 3 (10.0)
> Dizziness | 16 (19.3) | 3 (3.8) | 7 (22.6) | 2 (6.7)
> Headache | 15 (18.1) | 16 (20.3) | 8 (25.8) | 3 (10.0)
> Somnolence | 14 (16.9) | 3 (3.8) | 1 (3.2) | 4 (13.3)
> Anxiety | 11 (13.3) | 4 (5.1) | 1 ((3.2) | 1 (3.3)
> Paresthesia | 11 (13.3) | 1 (1.3) | 2 (6.5) | 0
> Insomnia | 10 (12.1) | 5 (6.3) | 1 (3.2) | 0
> Vomiting | 10 (12.1) | 1 (1.3) | 1 (3.2) | 1 (3.3)
> Paresthesia oral | 9 (10.8) | 1 (1.3) | 0 | 0
> Vision blurred | 9 (10.8) | 2 (2.5) | 5 (16.1) | 1 (3.3)
> Hypoesthesia oral | 8 (9.6) | 0 | 1 (3.2) | 1 (3.3)
> Nasal discomfort | 8 (9.6) | 1 (1.3) | 0 | 1 (3.3)
> Blood pressure increased | 7 (8.4) | 0 | 4 (12.9) | 1 (2.1)
> Diarrhea | 7 (8.4) | 7 (8.9) | 3 (9.7) | 3 (10.0)
> Dry mouth | 7 (8.4) | 2 (2.5) | 2 (6.5) | 1 (3.3)
> Hypoesthesia | 7 (8.4) | 0 | 1 (3.2) | 1 (3.3)
> Throat irritation | 7 (8.4) | 2 (2.5) | 2 (6.5) | 3 (10.0)
> Feeling drunk | 6 (7.2) | 1 (1.3) | 2 (6.5) | 0
> Sedation | 5 (6.0) | 0 | 0 | 1 (3.3)
> Dizziness postural | 4 (4.8) | 1 (1.3) | 4 (12.9) | 0
> Fatigue | 3 (3.6) | 5 (6.3) | 2 (6.5) | 1 (3.3)
> Irritability | 3 (3.6) | 0 | 2 (6.5) | 1 (3.3)

#### E0175 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[4]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Using data from 2 phase III studies of esketamine, we found no significant genotype effect on reductions in Montgomery–Åsberg Depression Rating Scale total score or on dissociative responses in patients with treatment-resistant depression treated with esketamine + oral antidepressant.

#### E0176 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[39]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The antidepressant effect was assessed by the difference in the change in Montgomery–Åsberg Depression Rating Scale (MADRS) total score on day 2 (24 hours after the initial esketamine dose) and day 28 (study endpoint) between depressed patients randomized to receive esketamine nasal spray plus a newly initiated oral antidepressant (esketamine + antidepressant [AD]) vs patients randomized to receive placebo nasal spray plus a newly initiated oral antidepressant (AD + placebo).

#### E0177 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[42]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Potential associations between the OPRM1 SNP and changes in MADRS total score at day 2 and day 28 were evaluated to test the a priori hypothesis.

#### E0178 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[48]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary outcome consisted of the MADRS total score change from baseline at day 2 and day 28.

#### E0179 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[59]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Baseline Demographics and Clinical Characteristics of Patients with OPRM1 SNP rs1799971 (A118G) Alleles Esketamine + AD AD + placebo AA (n = 176) AG/GG (n = 57) AA (n = 129) AG/GG (n = 44) Age, year Mean (SD) 45.6 (11.27) 46.1 (12.76) 48.1 (10.65) 46.1 (11.27) Range 18–64 19–64 22–64 22–63 Sex, n (%) Male 58 (33.0) 15 (26.3) 47 (36.4) 14 (31.8) Female 118 (67.0) 42 (73.7) 82 (63.6) 30 (68.2) Race, n (%) American Indian or Alaskan Native 1 (0.6) 0 0 0 Asian 2 (1.1) 2 (3.5) 2 (1.6) 1 (2.3) Black or African American 15 (8.5) 0 5 (3.9) 1 (2.3) White 142 (80.7) 52 (91.2) 117 (90.7) 36 (81.8) Multiple, not reported, other 16 (9.1) 3 (5.3) 5 (3.9) 6 (13.6) Age when diagnosed with MDD, year Mean (SD) 31.3 (12.26) 34.2 (13.97) 35.9 (13.30) 32.2 (12.20) Range 9–59 10–60 9–64 5–57 Duration of current episode, weeks Mean (SD) 158.2 (270.06) 192.4 (210.08) 126.5 (221.79) 135.3 (172.51) Range 9–2288 15–1080 6–1720 14–832 No. of previous antidepressant medications a , n (%) 1 or 2 118 (67.0) 28 (49.1) 83 (64.3) 27 (61.4) ≥3 58 (33.0) 29 (50.9) 46 (35.7) 17 (38.6) Class of oral antidepressant, n (%) SNRI 108 (61.4) 34 (59.6) 83 (64.3) 27 (61.4) SSRI 68 (38.6) 23 (40.4) 46 (35.7) 17 (38.6) Baseline CGI-S Mean (SD) 5.1 (0.71) 5.2 (0.68) 5.1 (0.66) 5.2 (0.76) Range 4–7 4–7 4–7 4–7 Baseline PHQ-9 total score Mean (SD) 20.5 (3.46) 20.1 (4.46) 20.4 (3.68) 21.2 (3.67) Range 9–27 5–27 10–27 10–27 Baseline MADRS total score Mean (SD) 37.7 (5.45) 37.8 (5.68) 37.2 (6.14) 38.2 (5.44) Range 22–49 26–48 18–52 29–53 Abbreviations: AD, antidepressant; CGI-S, Clinical Global Impression–Severity; MADRS, Montgomery–Åsberg Depression Rating Scale; MGH-ATRQ, Massachusetts General Hospital Antidepressant Treatment Response Questionnaire; PHQ-9, Patient Health Questionnaire 9-Item; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor. a Number of antidepressant medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained from MGH-ATRQ, in addition to one prospective antidepressant.

#### E0180 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the esketamine + AD arm, no significant genotype effects of SNP rs1799971 (A118G) on MADRS score reductions were detected on either day 2 ( Table 2 ; Figure 1 ) or day 28 ( Table 2 ; Figure 2 ).

#### E0181 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[61]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean (SD) reduction from baseline in MADRS total score was −9.62 (10.14) (AA genotype) and −10.49 (10.79) (AG/GG genotype) on day 2 and −20.95 (12.75) (AA genotype) and −23.16 (13.53) (AG/GG genotype) on day 28.

#### E0182 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[63]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score Esketamine + AD AD + placebo Minor allele frequency n Slope P value R 2 partial Minor allele effect n Slope P value R 2 partial Minor allele effect Day 2 0.13 229 −0.63 .69 <0.5 % None 169 −6.59 <.001 10% Greater response Day 28 0.13 232 −1.81 .34 <0.5 % None 172 −4.30 .07 2% None Abbreviations: AD, antidepressant; MADRS, Montgomery–Åsberg Depression Rating Scale; P value, probability of rejecting H0: slope = 0 while H0 is true; R 2 partial , proportion of variance explained by the SNP regressor; Slope, regression coefficient for the SNP regressor; SNP, single nucleotide polymorphism.

#### E0183 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[66]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of OPRM1 single nucleotide polymorphism (SNP) rs1799971 (A118G) alleles on improvements in depression severity, assessed as reductions from baseline in the Montgomery–Åsberg Depression Rating Scale (MADRS) total score on day 2.

#### E0184 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[69]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of OPRM1 single nucleotide polymorphism (SNP) rs1799971 (A118G) alleles on improvements in depression severity, assessed as reductions from baseline in the Montgomery–Åsberg Depression Rating Scale (MADRS) total score on day 28.

#### E0185 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[71]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the AD + placebo arm, a significant genotype effect of SNP rs1799971 (A118G) on the MADRS score reduction on day 2 was detected ( Table 2 ; Figure 1 ) such that the patients with the AG and GG genotypes showed a greater reduction on MADRS total scores than those with the AA genotype.

#### E0186 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[72]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> There was a nonsignificant trend towards a similar effect of SNP rs1799971 (A118G) on MADRS score reductions on day 28, with the reductions in patients with the AG/GG genotypes being numerically greater than those in patients with the AA genotype ( Figure 2 ).

#### E0187 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean (SD) reduction from baseline in MADRS total score was −4.37 (8.08) (AA genotype) and −11.28 (10.44) (AG/GG genotype) on day 2 and −15.75 (14.67) (AA genotype) and −20.77 (14.59) (AG/GG genotype) on day 28.

#### E0188 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[76]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In TRANSFORM-2, at day 2 visit, patients treated with AD + placebo responded with an additional improvement of 10.53 points on MADRS total scores ( P < .001) for the G-allele carriers compared with 1.39 ( P = .53) for noncarriers.

#### E0189 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[92]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Although not significant, the 2-point (esketamine + AD arm) and 5-point (AD + placebo arm) difference between the AA and AG/GG genotypes with regard to reduction in the MADRS total score on day 28 may be clinically relevant.

#### E0190 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[98]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean reduction in MADRS scores was −6 for both doses tested of ETS6103 compared with −11 for amitriptyline.

#### E0191 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[145]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Supplementary Material pyaa030_suppl_Supplementary_Table_1 Click here for additional data file.
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1.: Baseline Demographics and Clinical Characteristics of Patients with OPRM1 SNP rs1799971 (A118G) Alleles
>  | Esketamine + AD | AD + placebo
>  | AA (n = 176) | AG/GG (n = 57) | AA (n = 129) | AG/GG (n = 44)
> Age, year |  |  |  | 
> Mean (SD) | 45.6 (11.27) | 46.1 (12.76) | 48.1 (10.65) | 46.1 (11.27)
> Range | 18–64 | 19–64 | 22–64 | 22–63
> Sex, n (%) |  |  |  | 
> Male | 58 (33.0) | 15 (26.3) | 47 (36.4) | 14 (31.8)
> Female | 118 (67.0) | 42 (73.7) | 82 (63.6) | 30 (68.2)
> Race, n (%) |  |  |  | 
> American Indian or Alaskan Native | 1 (0.6) | 0 | 0 | 0
> Asian | 2 (1.1) | 2 (3.5) | 2 (1.6) | 1 (2.3)
> Black or African American | 15 (8.5) | 0 | 5 (3.9) | 1 (2.3)
> White | 142 (80.7) | 52 (91.2) | 117 (90.7) | 36 (81.8)
> Multiple, not reported, other | 16 (9.1) | 3 (5.3) | 5 (3.9) | 6 (13.6)
> Age when diagnosed with MDD, year |  |  |  | 
> Mean (SD) | 31.3 (12.26) | 34.2 (13.97) | 35.9 (13.30) | 32.2 (12.20)
> Range | 9–59 | 10–60 | 9–64 | 5–57
> Duration of current episode, weeks |  |  |  | 
> Mean (SD) | 158.2 (270.06) | 192.4 (210.08) | 126.5 (221.79) | 135.3 (172.51)
> Range | 9–2288 | 15–1080 | 6–1720 | 14–832
> No. of previous antidepressant medications a , n (%) |  |  |  | 
> 1 or 2 | 118 (67.0) | 28 (49.1) | 83 (64.3) | 27 (61.4)
> ≥3 | 58 (33.0) | 29 (50.9) | 46 (35.7) | 17 (38.6)
> Class of oral antidepressant, n (%) |  |  |  | 
> SNRI | 108 (61.4) | 34 (59.6) | 83 (64.3) | 27 (61.4)
> SSRI | 68 (38.6) | 23 (40.4) | 46 (35.7) | 17 (38.6)
> Baseline CGI-S |  |  |  | 
> Mean (SD) | 5.1 (0.71) | 5.2 (0.68) | 5.1 (0.66) | 5.2 (0.76)
> Range | 4–7 | 4–7 | 4–7 | 4–7
> Baseline PHQ-9 total score |  |  |  | 
> Mean (SD) | 20.5 (3.46) | 20.1 (4.46) | 20.4 (3.68) | 21.2 (3.67)
> Range | 9–27 | 5–27 | 10–27 | 10–27
> Baseline MADRS total score |  |  |  | 
> Mean (SD) | 37.7 (5.45) | 37.8 (5.68) | 37.2 (6.14) | 38.2 (5.44)
> Range | 22–49 | 26–48 | 18–52 | 29–53
> 
> TABLE Table 2.: Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score
>  |  | Esketamine + AD | AD + placebo
>  | Minor allele frequency | n | Slope | P value | R 2 partial | Minor allele effect | n | Slope | P value | R 2 partial | Minor allele effect
> Day 2 | 0.13 | 229 | −0.63 | .69 | <0.5 % | None | 169 | −6.59 | <.001 | 10% | Greater response
> Day 28 | 0.13 | 232 | −1.81 | .34 | <0.5 % | None | 172 | −4.30 | .07 | 2% | None
> 
> TABLE Table 3.: Effects of OPRM1 SNP rs1799971 (A118G) Variation on Dissociative Symptoms Assessed Using the CADSS a
>  |  | Esketamine + AD | AD + placebo
>  | Minor allele frequency | n | Slope | P value | R 2 partial | Minor allele effect | n | Slope | P value | R 2 partial | Minor allele effect
> Day 1 | 0.13 | 258 | 1.43 | .27 | <0.5 % | None | 182 | 0.27 | .64 | <0.5 % | None
> Day 25 | 0.13 | 228 | 0.68 | .50 | <0.5 % | None | 171 | −0.15 | .64 | <0.5 % | None
> Change | 0.13 | 225 | 0.31 | .74 | <0.5 % | None | 167 | −0.19 | .55 | <0.5 % | None

### esketamine-trd-madrs — NCT02422186

Pinned served row:
~~~json
{
  "id": "NCT02422186",
  "mean1": -10.0,
  "sd1": 12.74,
  "nc1": 63,
  "mean2": -6.3,
  "sd2": 8.86,
  "nc2": 60,
  "source": "ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery Asberg Depression Rating Scale (MAD' mean -10.0 (SD 12.74, n=63) [Intranasal Esketamine ] vs -6.3 (SD 8.86, n=60) [Oral AD Plus Intranasa] Units on a scale — population: The full analysis set (FAS) was defined as all randomized participants who recei",
  "timeframe": "Baseline up to Endpoint (Double-blind Induction Phase[Day 28])"
}
~~~

#### E0192 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/18/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **PRIMARY_REPORT**.

Population: full analysis set (FAS/mITT). Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Elderly patients with major depression have a poorer prognosis, are less responsive to treatment, and show greater functional decline compared with younger patients, highlighting the need for effective treatment. METHODS: This phase 3 double-blind study randomized patients with treatment-resistant depression (TRD) ≥65 years (1:1) to flexibly dosed esketamine nasal spray and new oral antidepressant (esketamine/antidepressant) or new oral antidepressant and placebo nasal spray (antidepressant/placebo). The primary endpoint was change in the Montgomery-Åsberg Depression Rating Scale (MADRS) from baseline to day 28. Analyses included a preplanned analysis by age (65-74 versus ≥75 years) and post-hoc analyses including age at depression onset. RESULTS: For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059. Adjusted mean (95% CI) difference for change in MADRS score between treatment groups was -4.9 (-8.96, -0.89; t = -2.4, df = 127; two-sided nominal p = 0.017) for patients 65 to 74 years versus -0.4 (-10.38, 9.50; t = -0.09, two-sided nominal p = 0.930) for those ≥75 years, and -6.1 (-10.33, -1.81; t = -2.8, df = 127; two-sided nominal p = 0.006) for patients with depression onset <55 years and 3.1 (-4.51, 10.80; t = 0.8, two-sided nominal p = 0.407) for those ≥55 years. Patients who rolled over into the long-term open-label study showed continued improvement with esketamine following 4 additional treatment weeks. CONCLUSIONS: Esketamine/antidepressant did not achieve statistical significance for the primary endpoint. Greater differences between treatment arms were seen for younger patients (65-74 years) and patients with earlier onset of depression (<55 years).

#### E0193 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/10/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> The objective of this analysis was to determine if there are sex differences with esketamine for treatment-resistant depression (TRD). Post hoc analyses of three randomized, controlled studies of esketamine in patients with TRD (TRANSFORM-1, TRANSFORM-2 [18-64 years], TRANSFORM-3 [≥ 65 years]) were performed. In each 4-week study, adults with TRD were randomized to esketamine or placebo nasal spray, each with a newly initiated oral antidepressant. Change from baseline to day 28 in Montgomery-Åsberg Depression Rating Scale (MADRS) total score was assessed by sex in pooled data from TRANSFORM-1/TRANSFORM-2 and separately in data from TRANSFORM-3 using a mixed-effects model for repeated measures. Use of hormonal therapy was assessed in all women, and menopausal status was assessed in women in TRANSFORM-1/TRANSFORM-2. Altogether, 702 adults (464 women) received ≥ 1 dose of intranasal study drug and antidepressant. Mean MADRS total score (SD) decreased from baseline to day 28, more so among patients treated with esketamine/antidepressant vs. antidepressant/placebo in both women and men: TRANSFORM-1/TRANSFORM-2 women-esketamine/antidepressant -20.3 (13.19) vs. antidepressant/placebo -15.8 (14.67), men-esketamine/antidepressant -18.3 (14.08) vs. antidepressant/placebo -16.0 (14.30); TRANSFORM-3 women-esketamine/antidepressant -9.9 (13.34) vs. antidepressant/placebo -6.9 (9.65), men-esketamine/antidepressant -10.3 (11.96) vs. antidepressant/placebo -5.5 (7.64). There was no significant sex effect or treatment-by-sex interaction (p > 0.35). The most common adverse events in esketamine-treated patients were nausea, dissociation, dizziness, and vertigo, each reported at a rate higher in women than men. The analyses support antidepressant efficacy and overall safety of esketamine nasal spray are similar between women and men with TRD. The TRANSFORM studies are registered at clinicaltrials.gov (identifiers: NCT02417064 (first posted 15 April 2015; last updated 4 May 2020), NCT02418585 (first posted 16 April 2015; last updated 2 June 2020), and NCT02422186 (first posted 21 April 2015; last updated 29 September 2021)).

#### E0194 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "63".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupId": "OG000", "value": "-10.0", "spread": "12.74"}

#### E0195 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "60".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupId": "OG001", "value": "-6.3", "spread": "8.86"}

#### E0196 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement. 

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "SUPERIORITY", "pValue": "=0.059", "statisticalMethod": "Mixed Model for Repeated Measures", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-3.6", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.20", "ciUpperLimit": "0.07"}

#### E0197 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/1/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "71".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during the double-blind induction phase was carried forward as the "End Point" for that phase. 

> {"groupId": "OG000", "value": "-9.3", "spread": "12.28"}

#### E0198 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/1/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "64".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during the double-blind induction phase was carried forward as the "End Point" for that phase. 

> {"groupId": "OG001", "value": "-5.6", "spread": "9.11"}

#### E0199 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/1/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during the double-blind induction phase was carried forward as the "End Point" for that phase. 

> {"groupIds": ["OG000", "OG001"], "nonInferiorityType": "OTHER", "pValue": "=0.052", "statisticalMethod": "ANCOVA", "paramType": "Least Square (LS) Mean Difference", "paramValue": "-3.6", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.16", "ciUpperLimit": "-0.03"}

#### E0200 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[16]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Both short-term and long-term (up to 12 months or longer) efficacy and safety was demonstrated against placebo in the TRANSFORM and SUSTAIN trials which reported significant improvements in depressive symptoms (mean decrease of −21.4 (12.3) of the Montgomery–Åsberg Depression Rating Scale (MADRS) from initiation to day 28 11 ), sustained symptom remission and a low relapse rate in patients who were in remission (26.7% 12 ).

#### E0201 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[42]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Treatment response was defined either by a ⩾50% relative reduction in MADRS total score from baseline or by an MADRS total score ⩽10.

#### E0202 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[44]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Relapse was defined as the occurrence of a MADRS score ⩾22 at any follow‑up assessment in a patient who had previously achieved remission.

#### E0203 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[57]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Another sensitivity analysis was conducted by defining remission with MADRS ⩽ 12 instead of ⩽10.

#### E0204 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[72]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Characteristics, n (%) otherwise specified N = 200 Demographics and physical examination Age, years Mean (SD) 46.6 (15.5) Median (IQR) 48 (35–58) <65 years 177 (88.5) Female 113 (56.5) Normal blood pressure at baseline 178/195 (91.3) Lifetime history of depression Time between first diagnosis of lifetime depression and inclusion (years) N = 142 Median (IQR) 10 (3.2–22.8) Lifetime number of previous MDE (excluding the current episode) N = 198 Mean (SD) 3.0 (2.9) Lifetime number of treatment-resistant depressive episodes (failure of at least 2 lines of treatment, excluding current depressive episode) N = 158 Mean (SD) 1.8 (2.1) Patients with at least one previous MDE N = 160 Lifetime history of suicide attempt 78 (39.0) Current MDE 200 (100.0) Duration of MDE, years N = 184 Mean (SD) 2.9 (3.7) Median (IQR) 1.8 (0.9–3.2) Typology N = 200 Suicidal ideation 102 (51.0) Risk behaviors 21 (10.5) Deterioration of general physical condition 36 (18.0) Functional disability 84 (42.0) Unknown 27 (13.5) Clinical subtype Anxiety feature 116 (58.0) Melancholic features 42 (21.0) Psychotic features 4 (2.0) Atypical features 12 (6.0) Catatonic features 4 (2.0) Seasonal features 5 (2.5) At least one full-time hospitalization since the onset of the current MDE 115 (57.5) Treatment-resistant (clinician’s judgment) 195 (97.5) MADRS at baseline N = 198 Total mean (SD) 31.9 (7.0) Mild depression (7–19 points) 8 (4.0) Moderate depression (20–34 points) 118 (59.6) Severe depression (>34 points) 72 (36.4) CGI-SS-R score at baseline N = 197 Mean (SD) 1.9 (1.4) 0 Normal, no at all suicidal 46 (23.4) 1 Questionably suicidal 32 (16.2) 2 Mildly suicidal 43 (21.8) 3 Moderately suicidal 45 (22.8) 4 Markedly suicidal 28 (14.2) 5 Severely suicidal 2 (1.0) 6 Among the most extremely suicidal participants 1 (0.5) C-SSRS at baseline in patients with CGI-SS-R > 1 at baseline N = 146 Question 4: Active suicidal ideation with some intent to act without specific plan 79 (54.1) Question 5: Active suicidal ideation with specific plan and intent 33 (22.6) QLDS Score at baseline N = 190 Mean (SD) 20.8 (3.8) Severity of the current MDE (clinician’s judgment) Mild 1 (0.5) Moderate 63 (31.5) Severe 136 (68.0) Comorbidities at baseline Other psychiatric comorbidity 144 (72.0) Anxiety disorders 79/144 (54.9) Posttraumatic stress disorder 48/144 (33.3) Current substance use-related disorders and addictive disorders 40/144 (27.8) Obsessive-compulsive and related disorders 11/144 (7.6) Conduct and Impulse Control Disorders 7/144 (4.9) Neurodevelopmental disorders 5/144 (3.5) Endocrine disorder 19/199 (9.5) Cardiac disease 31/199 (15.6) Vascular disease 8/199 (4.0) Respiratory, thoracic, and mediastinal disorders 14/199 (7.0) Nervous system disorders 26/199 (13.1) Hepatobiliary disorders 9/199 (4.5) Previous well-conducted treatment lines of AD N = 182 Median number (IQR) 3 (2–5) ⩾2 145/182 (79.7) ⩾5 52/182 (28.6) Details of previous well-conducted lines of AD 182 (91.0) A single AD without augmentation 129 (64.5) A single AD with augmentation 61 (30.5) Combination of AD without augmentation 59 (29.5) Combination of AD with augmentation 74 (37.0) A single augmentation therapy drug 63 (31.5) Combination of augmentation therapy drugs 18 (9.0) Neurostimulation (ECT, rTMS, tDCS) 45 (22.5) No treatment 6 (3.0) AD, antidepressant; CGI-SS-R, Clinical Global Impression- Suicidality Severity–Revised; ECT, electroconvulsive therapy; IQR, interquartile range; MADRS, Montgomery–Åsberg Depression Rating Scale; MDE, major depressive episode; QLDS, Quality of Life in Depression Scale; rTMS, repetitive transcranial magnetic stimulation; tDCS, transcranial direct current stimulation.

#### E0205 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[76]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean baseline MADRS score was 31.9 ( SD = 7.0).

#### E0206 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[77]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Based on clinician judgment, 68.0% of episodes were classified as severe, and 31.5% as moderate, while 36.4% met the MADRS threshold for severe depression and 59.6% met the MADRS threshold for moderate depression.

#### E0207 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[114]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean MADRS score decreased from 31.9 ( SD = 7.0) at baseline to 18.9 ( SD = 9.1 at the M1 visit (end of the initiation phase), corresponding to a mean absolute change of −13.0 points (95% CI: −14.6 to −11.4; Figure 2 ).

#### E0208 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[117]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The lowest mean MADRS score was observed at M12, reaching 12.4 ( SD = 9.4), with a mean absolute change of −17.9 (95% CI: −21.6 to −14.2).

#### E0209 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[118]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS items all showed improvement over the 12-month follow-up.

#### E0210 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[119]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At baseline, the most severe MADRS items were Reported Sadness (4.2, SD = 1.1) and Apparent Sadness (4.0, SD = 1.2), followed by lassitude (3.7, SD = 1.1), inability to feel (3.7, SD = 1.1), and inner tension (3.3, SD = 1.3), while symptoms such as suicidal thoughts (2.5, SD = 1.5), reduced sleep (2.4, SD = 1.8), and reduced appetite (1.5, SD = 1.6) were least pronounced.

#### E0211 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[134]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Remission sensitivity analyses with a higher MADRS threshold (⩽12 instead of ⩽10) also showed consistent results, with slightly higher rates when the threshold was set to ⩽12 ( Figures S7 and S8 ).

#### E0212 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[136]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS response and remission rates in patients still under esketamine with MADRS available up to month 12.

#### E0213 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[138]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Alt text: Rate of MADRS response and remission in esketamine-treated patients up to 12 months.

#### E0214 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[204]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In ELLIPSE, the MADRS decreased consistently in patients still under treatment during the induction phase and stabilized by M2 (mean MADRS 15.6 (9.0)), with sustained improvements through M12.

#### E0215 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[209]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The REAL-ESK cohort also reported a significant reduction in the MADRS score in patients still under esketamine was observed at month 1 (mean, 22.27 ± 9.81) and month 3 ( n = 91; mean, 14.69 ± 9.88) compared to baseline ((T0); mean, 35 ± 8.53).

#### E0216 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[211]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the ESCAPE-TRD trial, the absolute rate of remission (score of 10 or less on the MADRS) was 27.1% at month 2.

#### E0217 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[256]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Relapse was defined on the basis of a MADRS score ⩾22 observed at any follow-up assessment after remission, without confirmation across consecutive visits.

#### E0218 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/31734084#sentence-window[268]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Characteristics, n (%) otherwise specified | N = 200
> Demographics and physical examination
> Age, years
> Mean (SD) | 46.6 (15.5)
> Median (IQR) | 48 (35–58)
> <65 years | 177 (88.5)
> Female | 113 (56.5)
> Normal blood pressure at baseline | 178/195 (91.3)
> Lifetime history of depression
> Time between first diagnosis of lifetime depression and inclusion (years) | N = 142
> Median (IQR) | 10 (3.2–22.8)
> Lifetime number of previous MDE (excluding the current episode) | N = 198
> Mean (SD) | 3.0 (2.9)
> Lifetime number of treatment-resistant depressive episodes (failure of at least 2 lines of treatment, excluding current depressive episode) | N = 158
> Mean (SD) | 1.8 (2.1)
> Patients with at least one previous MDE | N = 160
> Lifetime history of suicide attempt | 78 (39.0)
> Current MDE | 200 (100.0)
> Duration of MDE, years | N = 184
> Mean (SD) | 2.9 (3.7)
> Median (IQR) | 1.8 (0.9–3.2)
> Typology | N = 200
> Suicidal ideation | 102 (51.0)
> Risk behaviors | 21 (10.5)
> Deterioration of general physical condition | 36 (18.0)
> Functional disability | 84 (42.0)
> Unknown | 27 (13.5)
> Clinical subtype | 
> Anxiety feature | 116 (58.0)
> Melancholic features | 42 (21.0)
> Psychotic features | 4 (2.0)
> Atypical features | 12 (6.0)
> Catatonic features | 4 (2.0)
> Seasonal features | 5 (2.5)
> At least one full-time hospitalization since the onset of the current MDE | 115 (57.5)
> Treatment-resistant (clinician’s judgment) | 195 (97.5)
> MADRS at baseline | N = 198
> Total mean (SD) | 31.9 (7.0)
> Mild depression (7–19 points) | 8 (4.0)
> Moderate depression (20–34 points) | 118 (59.6)
> Severe depression (>34 points) | 72 (36.4)
> CGI-SS-R score at baseline | N = 197
> Mean (SD) | 1.9 (1.4)
> 0 Normal, no at all suicidal | 46 (23.4)
> 1 Questionably suicidal | 32 (16.2)
> 2 Mildly suicidal | 43 (21.8)
> 3 Moderately suicidal | 45 (22.8)
> 4 Markedly suicidal | 28 (14.2)
> 5 Severely suicidal | 2 (1.0)
> 6 Among the most extremely suicidal participants | 1 (0.5)
> C-SSRS at baseline in patients with CGI-SS-R > 1 at baseline | N = 146
> Question 4: Active suicidal ideation with some intent to act without specific plan | 79 (54.1)
> Question 5: Active suicidal ideation with specific plan and intent | 33 (22.6)
> QLDS Score at baseline | N = 190
> Mean (SD) | 20.8 (3.8)
> Severity of the current MDE (clinician’s judgment) | 
> Mild | 1 (0.5)
> Moderate | 63 (31.5)
> Severe | 136 (68.0)
> Comorbidities at baseline
> Other psychiatric comorbidity | 144 (72.0)
> Anxiety disorders | 79/144 (54.9)
> Posttraumatic stress disorder | 48/144 (33.3)
> Current substance use-related disorders and addictive disorders | 40/144 (27.8)
> Obsessive-compulsive and related disorders | 11/144 (7.6)
> Conduct and Impulse Control Disorders | 7/144 (4.9)
> Neurodevelopmental disorders | 5/144 (3.5)
> Endocrine disorder | 19/199 (9.5)
> Cardiac disease | 31/199 (15.6)
> Vascular disease | 8/199 (4.0)
> Respiratory, thoracic, and mediastinal disorders | 14/199 (7.0)
> Nervous system disorders | 26/199 (13.1)
> Hepatobiliary disorders | 9/199 (4.5)
> Previous well-conducted treatment lines of AD | N = 182
> Median number (IQR) | 3 (2–5)
> ⩾2 | 145/182 (79.7)
> ⩾5 | 52/182 (28.6)
> Details of previous well-conducted lines of AD | 182 (91.0)
> A single AD without augmentation | 129 (64.5)
> A single AD with augmentation | 61 (30.5)
> Combination of AD without augmentation | 59 (29.5)
> Combination of AD with augmentation | 74 (37.0)
> A single augmentation therapy drug | 63 (31.5)
> Combination of augmentation therapy drugs | 18 (9.0)
> Neurostimulation (ECT, rTMS, tDCS) | 45 (22.5)
> No treatment | 6 (3.0)
> 
> TABLE Table 2.: Concomitant antidepressant treatments started before or/at esketamine initiation and ended after.

#### E0219 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[58]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At the end of the screening phase, non-responders (≤ 25% improvement in Montgomery-Åsberg Depression Rating Scale [MADRS] total score from week 1 to week 4) discontinued all current antidepressant treatment(s) and were randomized to double-blind treatment, consisting of twice-weekly esketamine nasal spray or matching (appearance, taste, and packaging) placebo nasal spray, each combined with a newly initiated oral antidepressant (SSRI or SNRI) taken daily.

#### E0220 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Assessments Improvement in symptoms of depression was assessed by the MADRS (Williams and Kobak 2008 ), which was administered by independent, blinded raters at baseline and subsequent visits during the double-blind treatment phase.

#### E0221 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[73]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary efficacy endpoint in the TRANSFORM studies—change from baseline to endpoint (day 28) in MADRS total score—was analyzed by sex using a mixed-effects model for repeated measures (MMRM).

#### E0222 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The model included baseline MADRS total score as a covariate, and treatment, study (TRANSFORM-1/TRANSFORM-2 only), region, oral antidepressant class (SNRI or SSRI), day, sex, day-by-treatment, treatment-by-sex, and day-by-treatment-by-sex interaction as fixed effects, and a random patient effect.

#### E0223 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[77]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Response rate (defined as ≥ 50% decrease from baseline MADRS total score) and remission rate (defined as MADRS ≤ 12) at day 28 were analyzed by treatment group and sex using the generalized Cochran-Mantel–Haenszel (CMH) test.

#### E0224 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[90]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 1 Demographic and baseline characteristics by sex in short-term randomized, controlled TRD trials TRANSFORM-1/TRANSFORM-2 TRANSFORM-3 Characteristic Women N = 379 Men N = 186 Total N = 565 Women N = 85 Men N = 52 Total N = 137 Age, years Mean (SD) 46.6 (11.05) 44.9 (12.22) 46.1 (11.46) 70.3 (4.9) 69.5 (3.8) 70.0 (4.52) Range (18; 64) (18; 64) (18; 64) (65; 86) (65; 79) (65; 86) Race, n (%) American Indian or Alaskan Native 1 (0.3) 0 1 (0.2) 0 0 0 Asian 5 (1.3) (1.2) 2 (1.1) 7 (1.2) 0 0 0 Black or African American 23 (6.1) 7 (3.8) 30 (5.3) 0 0 0 White 302 (79.7) 168 (90.3) 470 (83.2) 81 (95.3) 49 (94.2) 130 (94.9) Other 25 (6.6) 4 (2.2) 29 (5.1) 0 0 0 Multiple 1 (0.3) 2 (1.1) 3 (0.5) 2 (2.4) 2 (3.8) 4 (2.9) Not reported 22 (5.8) 3 (1.6) 25 (4.4) 1 (1.2) 1 (1.9) 2 (1.5) Unknown 0 0 0 1 (1.2) 0 1 (0.7) Body mass index (kg/m 2 ) Mean (SD) 28.4 (6.60) 28.7 (5.59) 28.5 (6.28) 28.9 (6.3) 28.9 (4.5) 28.9 (5.64) Range (17; 56) (16; 56) (16; 56) (16; 45) (22; 42) (16; 45) Menopause status a , n (%) Pre-menopausal 182 (48.0) NA NA NA Peri-menopausal 24 (6.3) NA NA NA Post-menopausal—non-surgical 120 (31.7) NA NA NA Post-menopausal—surgical 53 (14.0) NA NA NA Regular menstrual cycles, n (%) N = 203 Yes 160 a (78.8) NA NA NA No 43 (21.2) NA NA NA Median length of typical menstrual cycle (days) 28.0 NA NA NA History of worsening luteal phase, n (%) N = 203 Yes 43 (21.2) NA NA NA No 160 a (78.8) NA NA NA Employment status b , n (%) Any type of employment 218 (57.5) 107 (57.5) 325 (57.5) 14 (16.5) 10 (19.2) 24 (17.5) Any type of unemployment 122 (32.2) 65 (34.9) 187 (33.1) 4 (4.7) 4 (7.7) 8 (5.8) Other 39 (10.3) 14 (7.5) 53 (9.4) 67 (78.8) 38 (73.1) 105 (76.6) Region, n (%) Europe 1542 (37.5) 77 (41.4) 219 (38.8) 40 (47.1) 19 (36.5) 59 (43.1) North America 151 (39.8) 93 (50.0) 244 (43.2) 40 (47.1) 30 (57.7) 70 (51.1) Age when diagnosed with MDD, years Mean (SD) 32.8 (12.69) 31.2 (132.69) 32.3 (12.70) 41.6 (15.9) 45.6 (16.5) 43.1 (16.2) Range (9; 61) (5; 64) (5; 64) (10; 75) (11; 77) (10; 77) Duration of current episode, weeks Mean (SD) 161.5 (236.4) 181.4 (276.5) 168.1 (250.2) 188.6 (279.5) 260.3 (423.6) 215.8 (341.7) Range (6; 2288) (12; 2028) (6; 2288) (8; 1700) (8; 2184) (8; 2184) No. of previous antidepressants c,d , n (%) 1 or 2 245 (65.0) 110 (59.2) 355(63.1) 54 (63.5) 30 (57.7) 84 (61.3) ≥ 3 132 (35.0) 76 (40.8) 208 (36.9) 31 (36.4) 22 (42.3) 53 (38.7) Class of oral antidepressant e , n (%) SNRI 236 (63.3) 112 (60.2) 348 (61.6) 34 (40.0) 27 (51.9) 61 (44.5) SSRI 143 (37.7) 74 (39.8) 217 (38.4) 51 (60.0) 25 (48.1) 76 (55.5) Oral antidepressant, n (%) Duloxetine 174 (45.9) 83 (44.6) 257 (45.5) 25 (29.4) 23 (44.2) 48 (35.0) Escitalopram 74 (19.5) 37 (19.9) 111 (19.6) 36 (42.4) 14 (26.9) 50 (36.5) Sertraline 68 (17.9) 37 (19.9) 105 (18.6) 14 (16.5) 11 (21.2) 25 (18.2) Venlafaxine XR 63 (16.6) 29 (15.6) 92 (16.3) 10 (11.8) 4 (7.7) 14 (10.2) CGI-S Mean (SD) 5.1 (0.67) 5.1 (0.72) 5.1 (0.68) 5.0 (0.75) 5.0 (0.85) 5.0 (0.79) MADRS total score Mean (SD) 37.7 (5.73) 36.8 (5.21) 37.4 (5.57) 35.2 (6.41) 35.2 (5.78) 35.2 (6.16) PHQ-9 total score Mean (SD) 20.6 (3.67) 20.3 (3.91) 20.5 (3.75) 17.6 (5.53) 17.4 (5.87) 17.5 (5.65) SDS total score Mean (SD) 24.5 (4.09) 23.9 (4.40) 24.3 (4.20) 23.2 (5.12) 21.3 (5.49) 22.3 (5.36) GAD-7 total score Mean (SD) 13.4 (5.23) 12.9 (5.02) 13.2 (5.16) NA NA NA Abbreviations: CGI-S Clinical Global Impression–Severity; MDD major depressive disorder; NA not applicable or not available, not administered; PHQ Patient Health Questionnaire; SNRI serotonin and norepinephrine reuptake inhibitor; SSRI selective serotonin reuptake inhibitor; TRD treatment-resistant depression a Data from the Massachusetts General Hospital Female Reproductive Lifecycle and Hormones Questionnaire, Module I (Freeman et al.

#### E0225 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[100]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> GAD-7 was not conducted in the TRANSFORM-3 study Table 3 Concomitant medications most frequently used during double-blind treatment in short-term randomized, controlled TRD trials Women Men Specific or category of concomitant medication Esketamine + antidepressant N = 282 Antidepressant + placebo N = 184 Esketamine + antidepressant N = 136 Antidepressant + placebo N = 103 Benzodiazepine 140 (49.6%) 86 (46.7%) 66 (48.5%) 36 (35.0%) Analgesic 79 (28.0%) 57 (31.0%) 34 (25.0%) 24 (23.3%) Antihypertensive 62 (22.0%) 53 (28.8%) 33 (24.3%) 32 (31.1%) Lipid-lowering agent 45 (16.0%) 36 (19.6%) 32 (23.5%) 28 (27.2%) Proton pump inhibitor 40 (14.2%) 28 (15.2%) 24 (17.6%) 11 (10.7%) Beta-blocker 34 (12.1%) 21 (11.4%) 21 (15.4%) 9 (8.7%) Thyroid medications 37 (13.1%) 35 (19.0%) 5 (3.7%) 8 (7.8%) Levothyroxine 36 (12.8%) 33 (17.9%) 5 (3.7%) 7 (6.8%) Hormonal therapy a 49 (17.4%) 24 (13.0%) NA NA TRANSFORM-1/2 Pre-menopausal 39/112 (34.8%) 15/70 (21.4%) Peri-menopausal 6/15 (40.0%) 2/9 (22.2%) Post-menopausal 4/108 (3.7%) 4/65 (6.2%) TRANSFORM-3 0/45 (0.0%) 3/40 (7.5%) The table lists, in descending order of frequency for all patients, all specific or categories of concomitant medication with a usage rate during double-blind treatment of ≥ 10% in either treatment group, without regard to sex a Includes hormone replacement therapy and oral contraceptives Mean MADRS total score decreased from baseline to day 28, with greater improvement among those treated with esketamine/antidepressant compared to antidepressant/placebo among both women and men.

#### E0226 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[101]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean MADRS change (SD) at day 28 for the esketamine/antidepressant and antidepressant/placebo groups were -20.3 (13.19) vs. -15.8 (14.67), respectively, among the women and -18.3 (14.08) vs. -16.0 (14.30), respectively, among the men in TRANSFORM-1/TRANSFORM-2; and -9.9 (13.34) vs. -6.9 (9.65), respectively, among the women and -10.3 (11.96) vs. -5.5 (7.64), respectively, among the men in TRANSFORM-3 (Table 4 ).

#### E0227 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[103]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 4 MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group TRANSFORM-1/TRANSFORM-2 TRANSFORM-3 Women Men Women Men Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Baseline N 235 144 108 78 45 40 27 25 Mean (SD) 37.7 (5.49) 37.7 (6.11) 36.9 (5.02) 36.7 (5.50) 35.7 (5.90) 34.5 (6.97) 35.2 (6.04) 35.1 (5.60) Change to day 28 N 215 138 95 70 39 36 24 24 Mean (SD) -20.3 (13.19) -15.8 (14.67) -18.3 (14.08) -16.0 (14.30) -9.9 (13.34) -6.9 (9.65) -10.3 (11.96) -5.5 (7.64) MMRM analysis a Diff. of LS means b (SE) -4.5 (1.41) -1.6 (2.04) -3.4 (2.41) -5.0 (3.05) 95% CI on difference -7.26, − 1.70 -5.60, 2.41 -8.14, 1.41 -11.05, 1.03 MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition.

#### E0228 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[106]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The p -values were 0.6574 and 0.3993 for sex, and 0.3546 and 0.4937 for treatment-by-sex interaction in the TRANSFORM-1/2 and TRANSFORM-3 studies, respectively CI confidence interval; LS least squares; MADRS Montgomery-Asberg Depression Rating Scale; TRD treatment-resistant depression a Mixed model for repeated measures (MMRM) analysis with change from baseline as the response variable and the fixed effect model terms for study number (pooled only), treatment (esketamine + antidepressant, antidepressant + placebo) day, region, class of antidepressant (SNRI or SSRI), sex, and treatment-by-day, treatment-by-sex, and treatment-by-day-by-sex, and baseline value as a covariate b Esketamine + antidepressant minus antidepressant + placebo In the TRANSFORM trials, the proportions of patients who were responders at day 28 and the proportion of patients in remission at day 28 were numerically higher among both women and men treated with esketamine/antidepressant as compared to antidepressant/placebo (Fig.

#### E0229 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[116]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes: Response defined as ≥ 50% decrease from baseline Montgomery-Asberg Depression Rating Scale (MADRS) total score.

#### E0230 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[117]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Remission defined as MADRS total score ≤ 12.

#### E0231 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[120]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes: Response defined as ≥ 50% decrease from baseline Montgomery-Asberg Depression Rating Scale (MADRS) total score Treatment benefit of esketamine was also observed in terms of functioning and self-reported depression for both women and men in the pooled TRANSFORM-1/TRANSFORM-2 trials (Table 5 , Fig.

#### E0232 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[144]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Furthermore, the between-group difference observed vs. antidepressant/placebo for both sex subgroups in TRANSFORM-1/TRANSFORM-2 and TRANSFORM-3 was in the range considered clinically meaningful (2-point to 3-point difference) (Montgomery and Möller 2009 ; Kim et al.

#### E0233 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[194]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> These findings add to the existing literature and support data-informed decision-making for women with TRD.
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1: Demographic and baseline characteristics by sex in short-term randomized, controlled TRD trials
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
> Characteristic | Women N = 379 | Men N = 186 | Total N = 565 | Women N = 85 | Men N = 52 | Total N = 137
> Age, years |  |  |  |  |  | 
> Mean (SD) | 46.6 (11.05) | 44.9 (12.22) | 46.1 (11.46) | 70.3 (4.9) | 69.5 (3.8) | 70.0 (4.52)
> Range | (18; 64) | (18; 64) | (18; 64) | (65; 86) | (65; 79) | (65; 86)
> Race, n (%) |  |  |  |  |  | 
> American Indian or Alaskan Native | 1 (0.3) | 0 | 1 (0.2) | 0 | 0 | 0
> Asian | 5 (1.3) (1.2) | 2 (1.1) | 7 (1.2) | 0 | 0 | 0
> Black or African American | 23 (6.1) | 7 (3.8) | 30 (5.3) | 0 | 0 | 0
> White | 302 (79.7) | 168 (90.3) | 470 (83.2) | 81 (95.3) | 49 (94.2) | 130 (94.9)
> Other | 25 (6.6) | 4 (2.2) | 29 (5.1) | 0 | 0 | 0
> Multiple | 1 (0.3) | 2 (1.1) | 3 (0.5) | 2 (2.4) | 2 (3.8) | 4 (2.9)
> Not reported | 22 (5.8) | 3 (1.6) | 25 (4.4) | 1 (1.2) | 1 (1.9) | 2 (1.5)
> Unknown | 0 | 0 | 0 | 1 (1.2) | 0 | 1 (0.7)
> Body mass index (kg/m 2 ) |  |  |  |  |  | 
> Mean (SD) | 28.4 (6.60) | 28.7 (5.59) | 28.5 (6.28) | 28.9 (6.3) | 28.9 (4.5) | 28.9 (5.64)
> Range | (17; 56) | (16; 56) | (16; 56) | (16; 45) | (22; 42) | (16; 45)
> Menopause status a , n (%) |  |  |  |  |  | 
> Pre-menopausal | 182 (48.0) | NA |  | NA | NA | 
> Peri-menopausal | 24 (6.3) | NA |  | NA | NA | 
> Post-menopausal—non-surgical | 120 (31.7) | NA |  | NA | NA | 
> Post-menopausal—surgical | 53 (14.0) | NA |  | NA | NA | 
> Regular menstrual cycles, n (%) | N = 203 |  |  |  |  | 
> Yes | 160 a (78.8) | NA |  | NA | NA | 
> No | 43 (21.2) | NA |  | NA | NA | 
> Median length of typical menstrual cycle (days) | 28.0 | NA |  | NA | NA | 
> History of worsening luteal phase, n (%) | N = 203 |  |  |  |  | 
> Yes | 43 (21.2) | NA |  | NA | NA | 
> No | 160 a (78.8) | NA |  | NA | NA | 
> Employment status b , n (%) |  |  |  |  |  | 
> Any type of employment | 218 (57.5) | 107 (57.5) | 325 (57.5) | 14 (16.5) | 10 (19.2) | 24 (17.5)
> Any type of unemployment | 122 (32.2) | 65 (34.9) | 187 (33.1) | 4 (4.7) | 4 (7.7) | 8 (5.8)
> Other | 39 (10.3) | 14 (7.5) | 53 (9.4) | 67 (78.8) | 38 (73.1) | 105 (76.6)
> Region, n (%) |  |  |  |  |  | 
> Europe | 1542 (37.5) | 77 (41.4) | 219 (38.8) | 40 (47.1) | 19 (36.5) | 59 (43.1)
> North America | 151 (39.8) | 93 (50.0) | 244 (43.2) | 40 (47.1) | 30 (57.7) | 70 (51.1)
> Age when diagnosed with MDD, years |  |  |  |  |  | 
> Mean (SD) | 32.8 (12.69) | 31.2 (132.69) | 32.3 (12.70) | 41.6 (15.9) | 45.6 (16.5) | 43.1 (16.2)
> Range | (9; 61) | (5; 64) | (5; 64) | (10; 75) | (11; 77) | (10; 77)
> Duration of current episode, weeks |  |  |  |  |  | 
> Mean (SD) | 161.5 (236.4) | 181.4 (276.5) | 168.1 (250.2) | 188.6 (279.5) | 260.3 (423.6) | 215.8 (341.7)
> Range | (6; 2288) | (12; 2028) | (6; 2288) | (8; 1700) | (8; 2184) | (8; 2184)
> No. of previous antidepressants c,d , n (%) |  |  |  |  |  | 
> 1 or 2 | 245 (65.0) | 110 (59.2) | 355(63.1) | 54 (63.5) | 30 (57.7) | 84 (61.3)
> ≥ 3 | 132 (35.0) | 76 (40.8) | 208 (36.9) | 31 (36.4) | 22 (42.3) | 53 (38.7)
> Class of oral antidepressant e , n (%) |  |  |  |  |  | 
> SNRI | 236 (63.3) | 112 (60.2) | 348 (61.6) | 34 (40.0) | 27 (51.9) | 61 (44.5)
> SSRI | 143 (37.7) | 74 (39.8) | 217 (38.4) | 51 (60.0) | 25 (48.1) | 76 (55.5)
> Oral antidepressant, n (%) |  |  |  |  |  | 
> Duloxetine | 174 (45.9) | 83 (44.6) | 257 (45.5) | 25 (29.4) | 23 (44.2) | 48 (35.0)
> Escitalopram | 74 (19.5) | 37 (19.9) | 111 (19.6) | 36 (42.4) | 14 (26.9) | 50 (36.5)
> Sertraline | 68 (17.9) | 37 (19.9) | 105 (18.6) | 14 (16.5) | 11 (21.2) | 25 (18.2)
> Venlafaxine XR | 63 (16.6) | 29 (15.6) | 92 (16.3) | 10 (11.8) | 4 (7.7) | 14 (10.2)
> CGI-S |  |  |  |  |  | 
> Mean (SD) | 5.1 (0.67) | 5.1 (0.72) | 5.1 (0.68) | 5.0 (0.75) | 5.0 (0.85) | 5.0 (0.79)
> MADRS total score |  |  |  |  |  | 
> Mean (SD) | 37.7 (5.73) | 36.8 (5.21) | 37.4 (5.57) | 35.2 (6.41) | 35.2 (5.78) | 35.2 (6.16)
> PHQ-9 total score |  |  |  |  |  | 
> Mean (SD) | 20.6 (3.67) | 20.3 (3.91) | 20.5 (3.75) | 17.6 (5.53) | 17.4 (5.87) | 17.5 (5.65)
> SDS total score |  |  |  |  |  | 
> Mean (SD) | 24.5 (4.09) | 23.9 (4.40) | 24.3 (4.20) | 23.2 (5.12) | 21.3 (5.49) | 22.3 (5.36)
> GAD-7 total score |  |  |  |  |  | 
> Mean (SD) | 13.4 (5.23) | 12.9 (5.02) | 13.2 (5.16) | NA | NA | NA
> 
> TABLE Table 2: Comorbidities of study patients in short-term randomized, controlled TRD trials
>  | Number (%) of patients
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
> Comorbidities | Women N = 379 | Men N = 186 | Total N = 565 | Women N = 85 | Men N = 52 | Total N = 137
> Anxiety a | 272 (71.8%) | 132 (71.0%) | 404 (71.5%) | NA | NA | NA
> Incidental surgery | 166 (43.8%) | 55 (29.6%) | 221 (39.1%) | 37 (43.5%) | 19 (36.5%) | 56 (40.9%)
> Hypertension | 79 (20.8%) | 38 (20.4%) | 117 (20.7%) | 46 (54.1%) | 28 (53.8%) | 74 (54.0%)
> Allergies | 69 (18.2%) | 31 (16.7%) | 100 (17.7%) | 11 (12.9%) | 4 (7.7%) | 15 (10.9%)
> Thyroid disease | 57 (15.0%) | 10 (5.4%) | 67 (11.9%) | 23 (27.1%) | 6 (11.5%) | 29 (21.2%)
> GERD | 48 (12.7%) | 15 (8.1%) | 63 (11.2%) | 13 (15.3%) | 8 (15.4%) | 21 (15.3%)
> Trauma | 27 (7.1%) | 31 (16.7%) | 58 (10.3%) | 5 (5.9%) | 3 (5.8%) | 8 (5.8%)
> Cardiovascular disease | 24 (6.3%) | 13 (7.0%) | 37 (6.5%) | 10 (11.8%) | 12 (23.1%) | 22 (16.1%)
> Diabetes | 25 (6.6%) | 8 (4.3%) | 33 (5.8%) | 13 (15.3%) | 13 (25.0%) | 26 (19.0%)
> Oncology | 13 (3.4%) | 5 (2.7%) | 18 (3.2%) | 16 (18.8%) | 11 (21.2%) | 27 (19.7%)
> Skin disorder | 23 (6.1%) | 13 (7.0%) | 36 (6.4%) | 3 (3.5%) | 4 (7.7%) | 7 (5.1%)
> Infection | 25 (6.6%) | 6 (3.2%) | 31 (5.5%) | 2 (2.4%) | 2 (3.8%) | 4 (2.9%)
> Respiratory disease | 12 (3.2%) | 2 (1.1%) | 14 (2.5%) | 1 (1.2%) | 0 | 1 (0.7%)
> Parathyroid disease | 2 (0.5%) | 1 (0.5%) | 3 (0.5%) | 0 | 1 (1.9%) | 1 (0.7%)
> 
> TABLE Table 3: Concomitant medications most frequently used during double-blind treatment in short-term randomized, controlled TRD trials
>  | Women | Men
> Specific or category of concomitant medication | Esketamine + antidepressant N = 282 | Antidepressant + placebo N = 184 | Esketamine + antidepressant N = 136 | Antidepressant + placebo N = 103
> Benzodiazepine | 140 (49.6%) | 86 (46.7%) | 66 (48.5%) | 36 (35.0%)
> Analgesic | 79 (28.0%) | 57 (31.0%) | 34 (25.0%) | 24 (23.3%)
> Antihypertensive | 62 (22.0%) | 53 (28.8%) | 33 (24.3%) | 32 (31.1%)
> Lipid-lowering agent | 45 (16.0%) | 36 (19.6%) | 32 (23.5%) | 28 (27.2%)
> Proton pump inhibitor | 40 (14.2%) | 28 (15.2%) | 24 (17.6%) | 11 (10.7%)
> Beta-blocker | 34 (12.1%) | 21 (11.4%) | 21 (15.4%) | 9 (8.7%)
> Thyroid medications | 37 (13.1%) | 35 (19.0%) | 5 (3.7%) | 8 (7.8%)
> Levothyroxine | 36 (12.8%) | 33 (17.9%) | 5 (3.7%) | 7 (6.8%)
> Hormonal therapy a | 49 (17.4%) | 24 (13.0%) | NA | NA
> TRANSFORM-1/2 |  |  |  | 
> Pre-menopausal | 39/112 (34.8%) | 15/70 (21.4%) |  | 
> Peri-menopausal | 6/15 (40.0%) | 2/9 (22.2%) |  | 
> Post-menopausal | 4/108 (3.7%) | 4/65 (6.2%) |  | 
> TRANSFORM-3 | 0/45 (0.0%) | 3/40 (7.5%) |  | 
> 
> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 | 
> 
> TABLE Table 5: Mean (SD) change from baseline to day 28 for SDS, PHQ-9, and GAD-7 total score by sex in pooled TRANSFORM-1/TRANSFORM-2 trials
>  | TRANSFORM-1/TRANSFORM-2
>  | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> SDS total score |  |  |  | 
> N | 177 | 115 | 84 | 60
> Mean (SD) | -12.5 (9.30) | -9.6 (9.50) | -10.6 (9.22) | -7.4 (8.12)
> PHQ-9 total score |  |  |  | 
> N | 218 | 138 | 95 | 70
> Mean (SD) | -12.3 (7.39) | -10.1 (7.99) | -10.9 (7.62) | -8.6 (8.25)
> GAD-7 total score |  |  |  | 
> N | 227 | 139 | 103 | 74
> Mean (SD) | -8.1 (5.90) | -6.9 (5.78) | -6.7 (5.84) | -5.4 (5.98)
> 
> TABLE Table 6: Most frequently reported treatment-emergent adverse events in the double-blind treatment phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant N = 237 | Antidepressant + placebo N = 144 | Esketamine + antidepressant N = 109 | Antidepressant + placebo N = 78 | Esketamine + antidepressant N = 45 | Antidepressant + placebo N = 40 | Esketamine + antidepressant N = 27 | Antidepressant + placebo N = 25
> Total with AEs | 209 (88.2%) | 96 (66.7%) | 92 (84.4%) | 47 (60.3%) | 34 (75.6%) | 23 (57.5%) | 17 (63.0%) | 16 (64.0%)
> Nausea | 72 (30.4%) | 11 (7.6%) | 26 (23.9%) | 8 (10.3%) | 9 (20.0%) | 3 (7.5%) | 4 (14.8%) | 0
> Headache | 52 (21.9%) | 21 (14.6%) | 18 (16.5%) | 17 (21.8%) | 6 (13.3%) | 1 (2.5%) | 3 (11.1%) | 1 (4.0%)
> Dizziness | 53 (22.4%) | 10 (6.9%) | 29 (26.6%) | 5 (6.4%) | 13 (28.9%) | 4 (10.0%) | 2 (7.4%) | 1 (4.0%)
> Dissociation | 68 (28.7%) | 7 (4.9%) | 24 (22.2%) | 1 (1.3%) | 7 (15.6%) | 1 (2.5%) | 2 (7.4%) | 0
> Vertigo | 62 (26.2%) | 5 (3.5%) | 16 (14.7%) | 0 | 4 (8.9%) | 2 (5.0%) | 4 (14.8%) | 0
> Dysgeusia | 46 (19.4%) | 19 (13.2%) | 19 (17.4%) | 11 (14.1%) | 2 (4.4%) | 3 (7.5%) | 2 (7.4%) | 0
> Somnolence | 39 (16.5%) | 15 (10.4%) | 21 (19.3%) | 5 (6.4%) | 1 (2.2%) | 3 (7.5%) | 0 | 0
> Paresthesia | 31 (13.1%) | 2 (1.4%) | 12 (11.0%) | 2 (2.6%) | 2 (4.4%) | 2 (5.0%) | 2 (7.4%) | 0
> Anxiety | 19 (8.0%) | 10 (6.9%) | 12 (11.0%) | 2 (2.6%) | 2 (4.4%) | 2 (5.0%) | 0 | 3 (12.0%)
> Fatigue | 19 (8.0%) | 9 (6.3%) | 6 (5.5%) | 2 (2.6%) | 7 (15.6%) | 4 (10.0%) | 2 (7.4%) | 1 (4.0%)
> BP increased | 16 (6.8%) | 3 (2.1%) | 14 (12.8%) | 2 (2.6%) | 8 (17.8%) | 3 (7.5%) | 1 (3.7%) | 0
> Hypoesthesia | 25 (10.5%) | 1 (0.7%) | 13 (11.9%) | 2 (2.6%) | 3 (6.7%) | 1 (2.5%) | 1 (3.7%) | 0
> Hypoesthesia oral | 29 (12.2%) | 2 (1.4%) | 8 (7.3%) | 1 (1.3%) | 4 (8.9%) | 0 | 1 (3.7%) | 0
> Vomiting | 27 (11.4%) | 3 (2.1%) | 5 (4.6%) | 1 (1.3%) | 5 (11.1%) | 0 | 0 | 1 (4.0%)
> UTI | 6 (2.5%) | 2 (1.4%) | 0 | 1 (1.3%) | 6 (13.3%) | 1 (2.5%) | 0 | 0

### esketamine-trd-madrs — NCT02417064

#### E0234 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/5/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> This exploratory post hoc analysis of two pooled 4-week, phase 3, double-blind, placebo- and active-controlled studies that compared esketamine nasal spray plus a newly initiated oral antidepressant (ESK+AD; n = 310) with a newly initiated oral AD plus placebo nasal spray (AD+PBO; n = 208) in patients with treatment-resistant depression (TRD) examined baseline patient demographic and psychiatric characteristics as potential predictors of response (≥50% reduction from baseline in Montgomery-Åsberg Depression Rating Scale [MADRS] total score) and remission (MADRS total score ≤12) at day 28. Overall, younger age, any employment, fewer failed ADs in the current depressive episode, and reduction in Clinical Global Impression-Severity (CGI-S) score at day 8 were significant positive predictors of response and remission at day 28. Treatment assignment was an important predictor of both response and remission. Patients treated with ESK+AD had 68% and 55% increased odds of achieving response and remission, respectively, versus those treated with AD+PBO. In the ESK+AD group, attainment of response and remission was more likely in patients who were employed, without significant anxiety at baseline, and who experienced a reduction in CGI-S score at day 8. Identification of predictors of response and remission may facilitate identification of those patients with TRD most likely to benefit from ESK+AD. Trial Registration: ClinicalTrials.gov: NCT02417064 (clinicaltrials.gov/ct2/show/NCT02417064) and NCT02418585 (clinicaltrials.gov/ct2/show/NCT02418585).

#### E0235 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/6/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: To evaluate the impact of baseline irritability on clinical outcomes in adults with treatment-resistant depression (TRD) treated with fixed or flexible doses of esketamine nasal spray plus a newly initiated oral antidepressant (ESK+AD) and to explore whether treatment with ESK affects irritability symptoms over time. METHODS: This was a post hoc analysis of pooled data from two 4-week, double-blind, phase 3 studies: TRANSFORM-1 (NCT02417064) and TRANSFORM-2 (NCT02418585). Adults with TRD (n = 560) were randomly assigned to ESK+AD or placebo nasal spray plus oral antidepressant (AD+PBO). Irritability was assessed with Item 6 of the 7-item Generalized Anxiety Disorder scale at screening and baseline. Changes in depression severity (Montgomery-Åsberg Depression Rating Scale [MADRS] total score) were evaluated by analysis of covariance (ANCOVA) models. Rates of MADRS response (≥50 % decrease from baseline total score) and remission (total score ≤ 12) were examined using multiple logistic regression models. RESULTS: Of 560 participants with TRD, 52.9 %, 23.2 %, and 23.9 % had high, low, and varying levels of irritability, respectively. No significant interaction between baseline irritability and treatment group was observed for change in MADRS total score, treatment response, or remission at day 28; numerically greater improvement was observed on all outcomes with ESK+AD versus AD+PBO at day 28 regardless of baseline irritability level. Percentages of patients reporting adverse events were similar across the three baseline irritability groups. LIMITATIONS: TRANSFORM-1 and TRANSFORM-2 were not designed to prospectively evaluate predetermined irritability outcomes. CONCLUSIONS: These post hoc results support efficacy of ESK+AD in patients with TRD, regardless of baseline irritability. TRIAL REGISTRATION: ClinicalTrials.gov identifiers: NCT02417064 (TRANSFORM-1), NCT02418585 (TRANSFORM-2).

#### E0236 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/10/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> The objective of this analysis was to determine if there are sex differences with esketamine for treatment-resistant depression (TRD). Post hoc analyses of three randomized, controlled studies of esketamine in patients with TRD (TRANSFORM-1, TRANSFORM-2 [18-64 years], TRANSFORM-3 [≥ 65 years]) were performed. In each 4-week study, adults with TRD were randomized to esketamine or placebo nasal spray, each with a newly initiated oral antidepressant. Change from baseline to day 28 in Montgomery-Åsberg Depression Rating Scale (MADRS) total score was assessed by sex in pooled data from TRANSFORM-1/TRANSFORM-2 and separately in data from TRANSFORM-3 using a mixed-effects model for repeated measures. Use of hormonal therapy was assessed in all women, and menopausal status was assessed in women in TRANSFORM-1/TRANSFORM-2. Altogether, 702 adults (464 women) received ≥ 1 dose of intranasal study drug and antidepressant. Mean MADRS total score (SD) decreased from baseline to day 28, more so among patients treated with esketamine/antidepressant vs. antidepressant/placebo in both women and men: TRANSFORM-1/TRANSFORM-2 women-esketamine/antidepressant -20.3 (13.19) vs. antidepressant/placebo -15.8 (14.67), men-esketamine/antidepressant -18.3 (14.08) vs. antidepressant/placebo -16.0 (14.30); TRANSFORM-3 women-esketamine/antidepressant -9.9 (13.34) vs. antidepressant/placebo -6.9 (9.65), men-esketamine/antidepressant -10.3 (11.96) vs. antidepressant/placebo -5.5 (7.64). There was no significant sex effect or treatment-by-sex interaction (p > 0.35). The most common adverse events in esketamine-treated patients were nausea, dissociation, dizziness, and vertigo, each reported at a rate higher in women than men. The analyses support antidepressant efficacy and overall safety of esketamine nasal spray are similar between women and men with TRD. The TRANSFORM studies are registered at clinicaltrials.gov (identifiers: NCT02417064 (first posted 15 April 2015; last updated 4 May 2020), NCT02418585 (first posted 16 April 2015; last updated 2 June 2020), and NCT02422186 (first posted 21 April 2015; last updated 29 September 2021)).

#### E0237 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/17/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: At ketamine and esketamine doses at which antidepressant doses are achieved, these agents are relatively selective, noncompetitive, N-methyl-D-aspartate receptor antagonists. However, at substantially higher doses, ketamine has shown mu-opioid receptor (MOR-gene symbol: OPRM1) agonist effects. Preliminary clinical studies showed conflicting results on whether naltrexone, a MOR antagonist, blocks the antidepressant action of ketamine. We examined drug-induced or endogenous MOR involvement in the antidepressant and dissociative responses to esketamine by assessing the effects of a functional single nucleotide polymorphism rs1799971 (A118G) of OPRM1, which is known to alter MOR agonist-mediated responses. METHODS: Participants with treatment-resistant depression from 2 phase III, double-blind, controlled trials of esketamine (or placebo) nasal spray plus an oral antidepressant were genotyped for rs1799971. Participants received the experimental agents twice weekly for 4 weeks. Antidepressant responses were rated using the change in Montgomery-Åsberg Depression Rating Scale (MADRS) score on days 2 and 28 post-dose initiation, and dissociative side effects were assessed using the Clinician-Administered Dissociative-States Scale at 40 minutes post-dose on days 1 and 25. RESULTS: In the esketamine + antidepressant arm, no significant genotype effect of single nucleotide polymorphism rs1799971 (A118G) on MADRS score reductions was detected on either day 2 or 28. By contrast, in the antidepressant + placebo arm, there was a significant genotype effect on MADRS score reductions on day 2 and a nonsignificant trend on day 28 towards an improvement in depression symptoms in G-allele carriers. No significant genotype effects on dissociative responses were detected. CONCLUSIONS: Variation in rs1799971 (A118G) did not affect the antidepressant response to esketamine + antidepressant. Antidepressant response to antidepressant + placebo was increased in G-allele carriers, compatible with previous reports that release of endorphins/enkephalins may play a role in mediating placebo effect. TRIAL REGISTRATION: NCT02417064 and NCT02418585; www.clinicaltrials.gov.

#### E0238 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/68/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: To examine the effect of esketamine nasal spray (ESK) plus newly initiated oral antidepressant (OAD) versus OAD plus placebo nasal spray (PBO) on the association between Montgomery-Åsberg Depression Rating Scale (MADRS) and 9-item Patient Health Questionnaire (PHQ-9) scores in adults with treatment-resistant depression (TRD). METHODS: Data from TRANSFORM-1 and TRANSFORM-2 (two similarly designed, randomized, active-controlled TRD studies) and SUSTAIN-1 (relapse prevention study) were analyzed. Group differences for mean changes in PHQ-9 total score from baseline were compared using analysis of covariance. Associations between MADRS and PHQ-9 total scores from TRANSFORM-1/TRANSFORM-2 were assessed using simple parametric, nonparametric, and multiple regression models. RESULTS: In TRANSFORM-1/TRANSFORM-2 (ESK + OAD, n = 343; OAD + PBO, n = 222), baseline PHQ-9 mean scores were 20.4 for ESK + OAD and 20.6 for OAD + PBO (severe depression). At day 28, significant group differences were observed in least squares mean change (SE) in PHQ-9 scores from baseline (-12.8 [0.46] vs -10.3 [0.53], P < .001) and in clinically substantial change in PHQ-9 scores (≥6 points; 77.1% vs 64%, P < .001) in ESK + OAD and OAD + PBO groups, respectively. A nonlinear relationship between MADRS and PHQ-9 was observed; total scores demonstrated increased correlation over time. In SUSTAIN-1, 57.3% of patients receiving ESK + OAD (n = 89) versus 44.2% receiving OAD + PBO (n = 86) retained remission status (PHQ-9 score ≤4) at maintenance treatment end point (P = .044). CONCLUSIONS: In adults with TRD, ESK + OAD significantly improved severity of depressive symptoms, and more patients achieved clinically meaningful changes in depressive symptoms based on PHQ-9, versus OAD + PBO. PHQ-9 outcomes were consistent with those of clinician-rated MADRS. TRIAL REGISTRATION: ClinicalTrials.gov: NCT02417064, NCT02418585, NCT02493868.

#### E0239 — abstract

Source: cache/esketamine-trd-madrs/records.json#/records/82/abstract. Class: OTHER; MADRS, clinician-rated scale. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> Objective: To evaluate response to esketamine nasal spray plus an oral antidepressant (ESK + AD) at day 28 in patients with major depressive disorder (DSM-5) and treatment-resistant depression (TRD) who did not meet response criteria within the first week of treatment. Methods: The current study is a pooled post hoc analysis of two phase 3, double-blind, active-controlled studies, conducted between August 2015 and February 2018, comparing ESK + AD with an oral antidepressant plus placebo (AD + PBO). Early treatment response was defined as a ≥ 50% decrease in Montgomery-Åsberg Depression Rating Scale total score at day 2 or days 2 and 8. Response rates at day 28 were determined among those not meeting early response criteria. Results: 518 patients in the analysis had day 28 observations (ESK + AD, n = 310; AD + PBO, n = 208). A greater percentage of patients treated with ESK + AD versus AD + PBO met response criteria beginning at day 2 (17.3% [55/318] vs 9.4% [19/203]) and at all subsequent timepoints, including day 28 (58.7% [182/310] vs 45.2% [94/208]). In day 2 nonresponders, 54.9% vs 44.3% (ESK + AD vs AD + PBO, respectively) achieved response at day 28 (P < .01). Similarly, among day 2 and 8 nonresponders, 52.1% vs 42.4% achieved response by day 28 (P = .01). In nonresponders at day 2 and at days 2 and 8, the odds ratio for a response at day 28 was 1.61 (95% CI, 1.09-2.40) with ESK + AD versus 1.56 (95% CI, 1.04-2.35) with AD + PBO. Conclusions: Patients with TRD without a demonstrated response within the first week of treatment may still derive benefit from a full 4-week induction course of esketamine nasal spray. Trial Registration: ClinicalTrials.gov identifiers NCT02417064 and NCT02418585.

#### E0240 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "111".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.  

> {"groupId": "OG000", "value": "-19.0", "spread": "13.86"}

#### E0241 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "98".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.  

> {"groupId": "OG001", "value": "-18.8", "spread": "14.12"}

#### E0242 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/classes/0/categories/0/measurements/2. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "108".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.  

> {"groupId": "OG002", "value": "-14.8", "spread": "15.07"}

#### E0243 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.  

> {"groupIds": ["OG001", "OG002"], "nonInferiorityType": "SUPERIORITY", "pValue": "0.088", "statisticalMethod": "Mixed Model for Repeated Measures", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-3.2", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-6.88", "ciUpperLimit": "0.45"}

#### E0244 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/0/analyses/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.  

> {"groupIds": ["OG000", "OG002"], "nonInferiorityType": "SUPERIORITY", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-4.1", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.67", "ciUpperLimit": "-0.49"}

#### E0245 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/classes/0/categories/0/measurements/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "115".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during double-blind induction phase was carried forward as "End Point" for that phase.  

> {"groupId": "OG000", "value": "-18.3", "spread": "14.21"}

#### E0246 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/classes/0/categories/0/measurements/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "113".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during double-blind induction phase was carried forward as "End Point" for that phase.  

> {"groupId": "OG001", "value": "-17.4", "spread": "14.25"}

#### E0247 — registry_arm

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/classes/0/categories/0/measurements/2. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "113".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during double-blind induction phase was carried forward as "End Point" for that phase.  

> {"groupId": "OG002", "value": "-14.3", "spread": "15.00"}

#### E0248 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/analyses/0. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during double-blind induction phase was carried forward as "End Point" for that phase.  

> {"groupIds": ["OG001", "OG002"], "nonInferiorityType": "SUPERIORITY", "pValue": "= 0.250", "statisticalMethod": "ANCOVA", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-2.0", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-5.52", "ciUpperLimit": "1.42"}

#### E0249 — registry_analysis

Source: cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02417064/1/analyses/1. Class: OTHER; MADRS, clinician-rated scale. Binding: **DIRECT**.

Population: Full analysis set (FAS): all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during double-blind induction phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.; . Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition. Missing data was imputed using Last Observation Carried Forward (LOCF) method and last post baseline observation during double-blind induction phase was carried forward as "End Point" for that phase.  

> {"groupIds": ["OG000", "OG002"], "nonInferiorityType": "SUPERIORITY", "paramType": "Difference of Least Square (LS) Means", "paramValue": "-4.1", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-7.53", "ciUpperLimit": "-0.6"}

#### E0250 — verified_input

Source: cache/esketamine-trd-madrs/verified_arms.json#/NCT02417064. Class: OTHER; MADRS, clinician-rated scale. Binding: **DERIVATION_NOT_INDEPENDENT_SOURCE**.

Population: full analysis set (FAS/mITT). Raw/adjusted: DERIVED_COMBINED_ARMS. n: {"nc1": 209, "nc2": 108}.

> {"outcome": "Observed-case Day-28 raw change-score MADRS MD", "mean1": -18.91, "sd1": 13.95, "nc1": 209, "mean2": -14.8, "sd2": 15.07, "nc2": 108, "provenance": "fulltext_verified_arms", "source": "TRANSFORM-1 (NCT02417064) committed CT.gov MADRS Day-28 (MMRM) per-arm change scores: intranasal esketamine 56 mg + oral AD -19.0 (SD 13.86, n=111); 84 mg + oral AD -18.8 (SD 14.12, n=98); oral AD + intranasal placebo -14.8 (SD 15.07, n=108). MULTI-ARM COMBINATION (Cochrane RevMan 6.5.2.10): the two intranasal esketamine dose arms are combined against the SHARED placebo to avoid double-counting it: combined esketamine mean -18.91, SD 13.95, n=209 (weighted mean of -19.0/-18.8; pooled SD from (n1-1)s1^2+(n2-1)s2^2 + n1*n2/(n1+n2)*(m1-m2)^2 over N-1). Both dose arms are INTRANASAL (route matches the protocol intranasal PICO). vs placebo -14.8 (SD 15.07, n=108). MD = -4.11.", "verification": "Per-arm values verbatim in committed cache/esketamine-trd-madrs/records.json ctgov_results NCT02417064; combined arm -18.91/13.95/209 computed by the standard subgroup-combination formula. Recovered because the automated CT.gov extractor takes a single arm pair and cannot combine 3 arms.", "override": true}

#### E0251 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[18]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> A Montgomery-Åsberg Depression Rating Scale (MADRS) score of ≥22, denoting moderate or severe depression, was also required for inclusion; moderate and severe depression were defined as a MADRS score of 20–34 and >34, respectively.

#### E0252 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[29]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary objective was to evaluate clinical response, defined as ≥50% improvement in the MADRS total score from baseline to Week 4.

#### E0253 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[30]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Clinical response, remission (defined as MADRS total score of ≤10) and change in disease severity (assessed by CGI-S score) were also evaluated through Week 20.

#### E0254 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[33]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> MADRS total score ranges from 0 to 60, with higher values indicating more severe depression ( 27 ).

#### E0255 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[62]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> All patients were classified as having moderate or severe depression, as assessed by MADRS score (moderate: 57.5%; severe: 42.5%; mean: 33.5; Figure 1 ).

#### E0256 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[64]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 1 Severity shifts in MADRS score over time.

#### E0257 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[69]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Mean MADRS score (±SD) declines over time, indicated by a purple line, from 33.5±6.0 at baseline to 19.5±10.6 at week 20.

#### E0258 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[100]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Clinical outcomes Mean MADRS score, and corresponding disease severity, decreased over time (MADRS at Baseline: 33.5; Week 4: 25.5; Week 20: 19.5; Figure 1 ).

#### E0259 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[101]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Numerical reductions in individual MADRS item scores were also observed through Week 20 ( Figure 4 ).

#### E0260 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[102]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Figure 4 MADRS item score evolution over time.

#### E0261 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[103]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> FAS; reporting individual item mean MADRS scores at baseline (N = 153), Week 4 (N = 131; Data missing for one patient), and Week 20 (N = 79).

#### E0262 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[107]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean percentage change in MADRS from baseline (Week 4: −23.8%; Week 20: −40.5%) was statistically significant at both timepoints (p<0.001).

#### E0263 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[108]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> After GEE adjustment, only employment/occupational status was associated with percentage change in MADRS: employed patients (p=0.008) and patients dependent on their partner/spouse or students (p=0.016) demonstrated a greater reduction compared to unemployed patients.

#### E0264 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[109]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At Week 20, patients taking SNRIs or other antidepressants at baseline showed a statistically significant regression (B=–11.146; p=0.038) and had a mean MADRS score percent change of –37.8 compared with patients taking an antipsychotic plus SNRI or other antidepressant (mean MADRS score percent change of –27.0).

#### E0265 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[110]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Employed patients (B=–18.212; p=0.003) demonstrated a statistically significant reduction in mean MADRS score percent change at Week 20 of –35.9 compared with a –19.7 change in unemployed patients.

#### E0266 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/37019044#sentence-window[118]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> These results broadly align with other studies in Portugal and Europe more widely; reductions in MADRS and CGI-S scores were seen, but clinical response and remission rates were below 50% and 30%, respectively ( 19 , 20 , 33 ).

#### E0267 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[58]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> At the end of the screening phase, non-responders (≤ 25% improvement in Montgomery-Åsberg Depression Rating Scale [MADRS] total score from week 1 to week 4) discontinued all current antidepressant treatment(s) and were randomized to double-blind treatment, consisting of twice-weekly esketamine nasal spray or matching (appearance, taste, and packaging) placebo nasal spray, each combined with a newly initiated oral antidepressant (SSRI or SNRI) taken daily.

#### E0268 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Assessments Improvement in symptoms of depression was assessed by the MADRS (Williams and Kobak 2008 ), which was administered by independent, blinded raters at baseline and subsequent visits during the double-blind treatment phase.

#### E0269 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[73]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary efficacy endpoint in the TRANSFORM studies—change from baseline to endpoint (day 28) in MADRS total score—was analyzed by sex using a mixed-effects model for repeated measures (MMRM).

#### E0270 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The model included baseline MADRS total score as a covariate, and treatment, study (TRANSFORM-1/TRANSFORM-2 only), region, oral antidepressant class (SNRI or SSRI), day, sex, day-by-treatment, treatment-by-sex, and day-by-treatment-by-sex interaction as fixed effects, and a random patient effect.

#### E0271 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[77]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Response rate (defined as ≥ 50% decrease from baseline MADRS total score) and remission rate (defined as MADRS ≤ 12) at day 28 were analyzed by treatment group and sex using the generalized Cochran-Mantel–Haenszel (CMH) test.

#### E0272 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[90]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 1 Demographic and baseline characteristics by sex in short-term randomized, controlled TRD trials TRANSFORM-1/TRANSFORM-2 TRANSFORM-3 Characteristic Women N = 379 Men N = 186 Total N = 565 Women N = 85 Men N = 52 Total N = 137 Age, years Mean (SD) 46.6 (11.05) 44.9 (12.22) 46.1 (11.46) 70.3 (4.9) 69.5 (3.8) 70.0 (4.52) Range (18; 64) (18; 64) (18; 64) (65; 86) (65; 79) (65; 86) Race, n (%) American Indian or Alaskan Native 1 (0.3) 0 1 (0.2) 0 0 0 Asian 5 (1.3) (1.2) 2 (1.1) 7 (1.2) 0 0 0 Black or African American 23 (6.1) 7 (3.8) 30 (5.3) 0 0 0 White 302 (79.7) 168 (90.3) 470 (83.2) 81 (95.3) 49 (94.2) 130 (94.9) Other 25 (6.6) 4 (2.2) 29 (5.1) 0 0 0 Multiple 1 (0.3) 2 (1.1) 3 (0.5) 2 (2.4) 2 (3.8) 4 (2.9) Not reported 22 (5.8) 3 (1.6) 25 (4.4) 1 (1.2) 1 (1.9) 2 (1.5) Unknown 0 0 0 1 (1.2) 0 1 (0.7) Body mass index (kg/m 2 ) Mean (SD) 28.4 (6.60) 28.7 (5.59) 28.5 (6.28) 28.9 (6.3) 28.9 (4.5) 28.9 (5.64) Range (17; 56) (16; 56) (16; 56) (16; 45) (22; 42) (16; 45) Menopause status a , n (%) Pre-menopausal 182 (48.0) NA NA NA Peri-menopausal 24 (6.3) NA NA NA Post-menopausal—non-surgical 120 (31.7) NA NA NA Post-menopausal—surgical 53 (14.0) NA NA NA Regular menstrual cycles, n (%) N = 203 Yes 160 a (78.8) NA NA NA No 43 (21.2) NA NA NA Median length of typical menstrual cycle (days) 28.0 NA NA NA History of worsening luteal phase, n (%) N = 203 Yes 43 (21.2) NA NA NA No 160 a (78.8) NA NA NA Employment status b , n (%) Any type of employment 218 (57.5) 107 (57.5) 325 (57.5) 14 (16.5) 10 (19.2) 24 (17.5) Any type of unemployment 122 (32.2) 65 (34.9) 187 (33.1) 4 (4.7) 4 (7.7) 8 (5.8) Other 39 (10.3) 14 (7.5) 53 (9.4) 67 (78.8) 38 (73.1) 105 (76.6) Region, n (%) Europe 1542 (37.5) 77 (41.4) 219 (38.8) 40 (47.1) 19 (36.5) 59 (43.1) North America 151 (39.8) 93 (50.0) 244 (43.2) 40 (47.1) 30 (57.7) 70 (51.1) Age when diagnosed with MDD, years Mean (SD) 32.8 (12.69) 31.2 (132.69) 32.3 (12.70) 41.6 (15.9) 45.6 (16.5) 43.1 (16.2) Range (9; 61) (5; 64) (5; 64) (10; 75) (11; 77) (10; 77) Duration of current episode, weeks Mean (SD) 161.5 (236.4) 181.4 (276.5) 168.1 (250.2) 188.6 (279.5) 260.3 (423.6) 215.8 (341.7) Range (6; 2288) (12; 2028) (6; 2288) (8; 1700) (8; 2184) (8; 2184) No. of previous antidepressants c,d , n (%) 1 or 2 245 (65.0) 110 (59.2) 355(63.1) 54 (63.5) 30 (57.7) 84 (61.3) ≥ 3 132 (35.0) 76 (40.8) 208 (36.9) 31 (36.4) 22 (42.3) 53 (38.7) Class of oral antidepressant e , n (%) SNRI 236 (63.3) 112 (60.2) 348 (61.6) 34 (40.0) 27 (51.9) 61 (44.5) SSRI 143 (37.7) 74 (39.8) 217 (38.4) 51 (60.0) 25 (48.1) 76 (55.5) Oral antidepressant, n (%) Duloxetine 174 (45.9) 83 (44.6) 257 (45.5) 25 (29.4) 23 (44.2) 48 (35.0) Escitalopram 74 (19.5) 37 (19.9) 111 (19.6) 36 (42.4) 14 (26.9) 50 (36.5) Sertraline 68 (17.9) 37 (19.9) 105 (18.6) 14 (16.5) 11 (21.2) 25 (18.2) Venlafaxine XR 63 (16.6) 29 (15.6) 92 (16.3) 10 (11.8) 4 (7.7) 14 (10.2) CGI-S Mean (SD) 5.1 (0.67) 5.1 (0.72) 5.1 (0.68) 5.0 (0.75) 5.0 (0.85) 5.0 (0.79) MADRS total score Mean (SD) 37.7 (5.73) 36.8 (5.21) 37.4 (5.57) 35.2 (6.41) 35.2 (5.78) 35.2 (6.16) PHQ-9 total score Mean (SD) 20.6 (3.67) 20.3 (3.91) 20.5 (3.75) 17.6 (5.53) 17.4 (5.87) 17.5 (5.65) SDS total score Mean (SD) 24.5 (4.09) 23.9 (4.40) 24.3 (4.20) 23.2 (5.12) 21.3 (5.49) 22.3 (5.36) GAD-7 total score Mean (SD) 13.4 (5.23) 12.9 (5.02) 13.2 (5.16) NA NA NA Abbreviations: CGI-S Clinical Global Impression–Severity; MDD major depressive disorder; NA not applicable or not available, not administered; PHQ Patient Health Questionnaire; SNRI serotonin and norepinephrine reuptake inhibitor; SSRI selective serotonin reuptake inhibitor; TRD treatment-resistant depression a Data from the Massachusetts General Hospital Female Reproductive Lifecycle and Hormones Questionnaire, Module I (Freeman et al.

#### E0273 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[100]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> GAD-7 was not conducted in the TRANSFORM-3 study Table 3 Concomitant medications most frequently used during double-blind treatment in short-term randomized, controlled TRD trials Women Men Specific or category of concomitant medication Esketamine + antidepressant N = 282 Antidepressant + placebo N = 184 Esketamine + antidepressant N = 136 Antidepressant + placebo N = 103 Benzodiazepine 140 (49.6%) 86 (46.7%) 66 (48.5%) 36 (35.0%) Analgesic 79 (28.0%) 57 (31.0%) 34 (25.0%) 24 (23.3%) Antihypertensive 62 (22.0%) 53 (28.8%) 33 (24.3%) 32 (31.1%) Lipid-lowering agent 45 (16.0%) 36 (19.6%) 32 (23.5%) 28 (27.2%) Proton pump inhibitor 40 (14.2%) 28 (15.2%) 24 (17.6%) 11 (10.7%) Beta-blocker 34 (12.1%) 21 (11.4%) 21 (15.4%) 9 (8.7%) Thyroid medications 37 (13.1%) 35 (19.0%) 5 (3.7%) 8 (7.8%) Levothyroxine 36 (12.8%) 33 (17.9%) 5 (3.7%) 7 (6.8%) Hormonal therapy a 49 (17.4%) 24 (13.0%) NA NA TRANSFORM-1/2 Pre-menopausal 39/112 (34.8%) 15/70 (21.4%) Peri-menopausal 6/15 (40.0%) 2/9 (22.2%) Post-menopausal 4/108 (3.7%) 4/65 (6.2%) TRANSFORM-3 0/45 (0.0%) 3/40 (7.5%) The table lists, in descending order of frequency for all patients, all specific or categories of concomitant medication with a usage rate during double-blind treatment of ≥ 10% in either treatment group, without regard to sex a Includes hormone replacement therapy and oral contraceptives Mean MADRS total score decreased from baseline to day 28, with greater improvement among those treated with esketamine/antidepressant compared to antidepressant/placebo among both women and men.

#### E0274 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[101]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean MADRS change (SD) at day 28 for the esketamine/antidepressant and antidepressant/placebo groups were -20.3 (13.19) vs. -15.8 (14.67), respectively, among the women and -18.3 (14.08) vs. -16.0 (14.30), respectively, among the men in TRANSFORM-1/TRANSFORM-2; and -9.9 (13.34) vs. -6.9 (9.65), respectively, among the women and -10.3 (11.96) vs. -5.5 (7.64), respectively, among the men in TRANSFORM-3 (Table 4 ).

#### E0275 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[103]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Table 4 MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group TRANSFORM-1/TRANSFORM-2 TRANSFORM-3 Women Men Women Men Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Esketamine + antidepressant Antidepressant + placebo Baseline N 235 144 108 78 45 40 27 25 Mean (SD) 37.7 (5.49) 37.7 (6.11) 36.9 (5.02) 36.7 (5.50) 35.7 (5.90) 34.5 (6.97) 35.2 (6.04) 35.1 (5.60) Change to day 28 N 215 138 95 70 39 36 24 24 Mean (SD) -20.3 (13.19) -15.8 (14.67) -18.3 (14.08) -16.0 (14.30) -9.9 (13.34) -6.9 (9.65) -10.3 (11.96) -5.5 (7.64) MMRM analysis a Diff. of LS means b (SE) -4.5 (1.41) -1.6 (2.04) -3.4 (2.41) -5.0 (3.05) 95% CI on difference -7.26, − 1.70 -5.60, 2.41 -8.14, 1.41 -11.05, 1.03 MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition.

#### E0276 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[106]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The p -values were 0.6574 and 0.3993 for sex, and 0.3546 and 0.4937 for treatment-by-sex interaction in the TRANSFORM-1/2 and TRANSFORM-3 studies, respectively CI confidence interval; LS least squares; MADRS Montgomery-Asberg Depression Rating Scale; TRD treatment-resistant depression a Mixed model for repeated measures (MMRM) analysis with change from baseline as the response variable and the fixed effect model terms for study number (pooled only), treatment (esketamine + antidepressant, antidepressant + placebo) day, region, class of antidepressant (SNRI or SSRI), sex, and treatment-by-day, treatment-by-sex, and treatment-by-day-by-sex, and baseline value as a covariate b Esketamine + antidepressant minus antidepressant + placebo In the TRANSFORM trials, the proportions of patients who were responders at day 28 and the proportion of patients in remission at day 28 were numerically higher among both women and men treated with esketamine/antidepressant as compared to antidepressant/placebo (Fig.

#### E0277 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[116]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes: Response defined as ≥ 50% decrease from baseline Montgomery-Asberg Depression Rating Scale (MADRS) total score.

#### E0278 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[117]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Remission defined as MADRS total score ≤ 12.

#### E0279 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[120]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Notes: Response defined as ≥ 50% decrease from baseline Montgomery-Asberg Depression Rating Scale (MADRS) total score Treatment benefit of esketamine was also observed in terms of functioning and self-reported depression for both women and men in the pooled TRANSFORM-1/TRANSFORM-2 trials (Table 5 , Fig.

#### E0280 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[144]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Furthermore, the between-group difference observed vs. antidepressant/placebo for both sex subgroups in TRANSFORM-1/TRANSFORM-2 and TRANSFORM-3 was in the range considered clinically meaningful (2-point to 3-point difference) (Montgomery and Möller 2009 ; Kim et al.

#### E0281 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/34973081#sentence-window[194]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> These findings add to the existing literature and support data-informed decision-making for women with TRD.
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1: Demographic and baseline characteristics by sex in short-term randomized, controlled TRD trials
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
> Characteristic | Women N = 379 | Men N = 186 | Total N = 565 | Women N = 85 | Men N = 52 | Total N = 137
> Age, years |  |  |  |  |  | 
> Mean (SD) | 46.6 (11.05) | 44.9 (12.22) | 46.1 (11.46) | 70.3 (4.9) | 69.5 (3.8) | 70.0 (4.52)
> Range | (18; 64) | (18; 64) | (18; 64) | (65; 86) | (65; 79) | (65; 86)
> Race, n (%) |  |  |  |  |  | 
> American Indian or Alaskan Native | 1 (0.3) | 0 | 1 (0.2) | 0 | 0 | 0
> Asian | 5 (1.3) (1.2) | 2 (1.1) | 7 (1.2) | 0 | 0 | 0
> Black or African American | 23 (6.1) | 7 (3.8) | 30 (5.3) | 0 | 0 | 0
> White | 302 (79.7) | 168 (90.3) | 470 (83.2) | 81 (95.3) | 49 (94.2) | 130 (94.9)
> Other | 25 (6.6) | 4 (2.2) | 29 (5.1) | 0 | 0 | 0
> Multiple | 1 (0.3) | 2 (1.1) | 3 (0.5) | 2 (2.4) | 2 (3.8) | 4 (2.9)
> Not reported | 22 (5.8) | 3 (1.6) | 25 (4.4) | 1 (1.2) | 1 (1.9) | 2 (1.5)
> Unknown | 0 | 0 | 0 | 1 (1.2) | 0 | 1 (0.7)
> Body mass index (kg/m 2 ) |  |  |  |  |  | 
> Mean (SD) | 28.4 (6.60) | 28.7 (5.59) | 28.5 (6.28) | 28.9 (6.3) | 28.9 (4.5) | 28.9 (5.64)
> Range | (17; 56) | (16; 56) | (16; 56) | (16; 45) | (22; 42) | (16; 45)
> Menopause status a , n (%) |  |  |  |  |  | 
> Pre-menopausal | 182 (48.0) | NA |  | NA | NA | 
> Peri-menopausal | 24 (6.3) | NA |  | NA | NA | 
> Post-menopausal—non-surgical | 120 (31.7) | NA |  | NA | NA | 
> Post-menopausal—surgical | 53 (14.0) | NA |  | NA | NA | 
> Regular menstrual cycles, n (%) | N = 203 |  |  |  |  | 
> Yes | 160 a (78.8) | NA |  | NA | NA | 
> No | 43 (21.2) | NA |  | NA | NA | 
> Median length of typical menstrual cycle (days) | 28.0 | NA |  | NA | NA | 
> History of worsening luteal phase, n (%) | N = 203 |  |  |  |  | 
> Yes | 43 (21.2) | NA |  | NA | NA | 
> No | 160 a (78.8) | NA |  | NA | NA | 
> Employment status b , n (%) |  |  |  |  |  | 
> Any type of employment | 218 (57.5) | 107 (57.5) | 325 (57.5) | 14 (16.5) | 10 (19.2) | 24 (17.5)
> Any type of unemployment | 122 (32.2) | 65 (34.9) | 187 (33.1) | 4 (4.7) | 4 (7.7) | 8 (5.8)
> Other | 39 (10.3) | 14 (7.5) | 53 (9.4) | 67 (78.8) | 38 (73.1) | 105 (76.6)
> Region, n (%) |  |  |  |  |  | 
> Europe | 1542 (37.5) | 77 (41.4) | 219 (38.8) | 40 (47.1) | 19 (36.5) | 59 (43.1)
> North America | 151 (39.8) | 93 (50.0) | 244 (43.2) | 40 (47.1) | 30 (57.7) | 70 (51.1)
> Age when diagnosed with MDD, years |  |  |  |  |  | 
> Mean (SD) | 32.8 (12.69) | 31.2 (132.69) | 32.3 (12.70) | 41.6 (15.9) | 45.6 (16.5) | 43.1 (16.2)
> Range | (9; 61) | (5; 64) | (5; 64) | (10; 75) | (11; 77) | (10; 77)
> Duration of current episode, weeks |  |  |  |  |  | 
> Mean (SD) | 161.5 (236.4) | 181.4 (276.5) | 168.1 (250.2) | 188.6 (279.5) | 260.3 (423.6) | 215.8 (341.7)
> Range | (6; 2288) | (12; 2028) | (6; 2288) | (8; 1700) | (8; 2184) | (8; 2184)
> No. of previous antidepressants c,d , n (%) |  |  |  |  |  | 
> 1 or 2 | 245 (65.0) | 110 (59.2) | 355(63.1) | 54 (63.5) | 30 (57.7) | 84 (61.3)
> ≥ 3 | 132 (35.0) | 76 (40.8) | 208 (36.9) | 31 (36.4) | 22 (42.3) | 53 (38.7)
> Class of oral antidepressant e , n (%) |  |  |  |  |  | 
> SNRI | 236 (63.3) | 112 (60.2) | 348 (61.6) | 34 (40.0) | 27 (51.9) | 61 (44.5)
> SSRI | 143 (37.7) | 74 (39.8) | 217 (38.4) | 51 (60.0) | 25 (48.1) | 76 (55.5)
> Oral antidepressant, n (%) |  |  |  |  |  | 
> Duloxetine | 174 (45.9) | 83 (44.6) | 257 (45.5) | 25 (29.4) | 23 (44.2) | 48 (35.0)
> Escitalopram | 74 (19.5) | 37 (19.9) | 111 (19.6) | 36 (42.4) | 14 (26.9) | 50 (36.5)
> Sertraline | 68 (17.9) | 37 (19.9) | 105 (18.6) | 14 (16.5) | 11 (21.2) | 25 (18.2)
> Venlafaxine XR | 63 (16.6) | 29 (15.6) | 92 (16.3) | 10 (11.8) | 4 (7.7) | 14 (10.2)
> CGI-S |  |  |  |  |  | 
> Mean (SD) | 5.1 (0.67) | 5.1 (0.72) | 5.1 (0.68) | 5.0 (0.75) | 5.0 (0.85) | 5.0 (0.79)
> MADRS total score |  |  |  |  |  | 
> Mean (SD) | 37.7 (5.73) | 36.8 (5.21) | 37.4 (5.57) | 35.2 (6.41) | 35.2 (5.78) | 35.2 (6.16)
> PHQ-9 total score |  |  |  |  |  | 
> Mean (SD) | 20.6 (3.67) | 20.3 (3.91) | 20.5 (3.75) | 17.6 (5.53) | 17.4 (5.87) | 17.5 (5.65)
> SDS total score |  |  |  |  |  | 
> Mean (SD) | 24.5 (4.09) | 23.9 (4.40) | 24.3 (4.20) | 23.2 (5.12) | 21.3 (5.49) | 22.3 (5.36)
> GAD-7 total score |  |  |  |  |  | 
> Mean (SD) | 13.4 (5.23) | 12.9 (5.02) | 13.2 (5.16) | NA | NA | NA
> 
> TABLE Table 2: Comorbidities of study patients in short-term randomized, controlled TRD trials
>  | Number (%) of patients
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
> Comorbidities | Women N = 379 | Men N = 186 | Total N = 565 | Women N = 85 | Men N = 52 | Total N = 137
> Anxiety a | 272 (71.8%) | 132 (71.0%) | 404 (71.5%) | NA | NA | NA
> Incidental surgery | 166 (43.8%) | 55 (29.6%) | 221 (39.1%) | 37 (43.5%) | 19 (36.5%) | 56 (40.9%)
> Hypertension | 79 (20.8%) | 38 (20.4%) | 117 (20.7%) | 46 (54.1%) | 28 (53.8%) | 74 (54.0%)
> Allergies | 69 (18.2%) | 31 (16.7%) | 100 (17.7%) | 11 (12.9%) | 4 (7.7%) | 15 (10.9%)
> Thyroid disease | 57 (15.0%) | 10 (5.4%) | 67 (11.9%) | 23 (27.1%) | 6 (11.5%) | 29 (21.2%)
> GERD | 48 (12.7%) | 15 (8.1%) | 63 (11.2%) | 13 (15.3%) | 8 (15.4%) | 21 (15.3%)
> Trauma | 27 (7.1%) | 31 (16.7%) | 58 (10.3%) | 5 (5.9%) | 3 (5.8%) | 8 (5.8%)
> Cardiovascular disease | 24 (6.3%) | 13 (7.0%) | 37 (6.5%) | 10 (11.8%) | 12 (23.1%) | 22 (16.1%)
> Diabetes | 25 (6.6%) | 8 (4.3%) | 33 (5.8%) | 13 (15.3%) | 13 (25.0%) | 26 (19.0%)
> Oncology | 13 (3.4%) | 5 (2.7%) | 18 (3.2%) | 16 (18.8%) | 11 (21.2%) | 27 (19.7%)
> Skin disorder | 23 (6.1%) | 13 (7.0%) | 36 (6.4%) | 3 (3.5%) | 4 (7.7%) | 7 (5.1%)
> Infection | 25 (6.6%) | 6 (3.2%) | 31 (5.5%) | 2 (2.4%) | 2 (3.8%) | 4 (2.9%)
> Respiratory disease | 12 (3.2%) | 2 (1.1%) | 14 (2.5%) | 1 (1.2%) | 0 | 1 (0.7%)
> Parathyroid disease | 2 (0.5%) | 1 (0.5%) | 3 (0.5%) | 0 | 1 (1.9%) | 1 (0.7%)
> 
> TABLE Table 3: Concomitant medications most frequently used during double-blind treatment in short-term randomized, controlled TRD trials
>  | Women | Men
> Specific or category of concomitant medication | Esketamine + antidepressant N = 282 | Antidepressant + placebo N = 184 | Esketamine + antidepressant N = 136 | Antidepressant + placebo N = 103
> Benzodiazepine | 140 (49.6%) | 86 (46.7%) | 66 (48.5%) | 36 (35.0%)
> Analgesic | 79 (28.0%) | 57 (31.0%) | 34 (25.0%) | 24 (23.3%)
> Antihypertensive | 62 (22.0%) | 53 (28.8%) | 33 (24.3%) | 32 (31.1%)
> Lipid-lowering agent | 45 (16.0%) | 36 (19.6%) | 32 (23.5%) | 28 (27.2%)
> Proton pump inhibitor | 40 (14.2%) | 28 (15.2%) | 24 (17.6%) | 11 (10.7%)
> Beta-blocker | 34 (12.1%) | 21 (11.4%) | 21 (15.4%) | 9 (8.7%)
> Thyroid medications | 37 (13.1%) | 35 (19.0%) | 5 (3.7%) | 8 (7.8%)
> Levothyroxine | 36 (12.8%) | 33 (17.9%) | 5 (3.7%) | 7 (6.8%)
> Hormonal therapy a | 49 (17.4%) | 24 (13.0%) | NA | NA
> TRANSFORM-1/2 |  |  |  | 
> Pre-menopausal | 39/112 (34.8%) | 15/70 (21.4%) |  | 
> Peri-menopausal | 6/15 (40.0%) | 2/9 (22.2%) |  | 
> Post-menopausal | 4/108 (3.7%) | 4/65 (6.2%) |  | 
> TRANSFORM-3 | 0/45 (0.0%) | 3/40 (7.5%) |  | 
> 
> TABLE Table 4: MADRS total score: change from baseline to day 28 of double-blind phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> Baseline |  |  |  |  |  |  |  | 
> N | 235 | 144 | 108 | 78 | 45 | 40 | 27 | 25
> Mean (SD) | 37.7 (5.49) | 37.7 (6.11) | 36.9 (5.02) | 36.7 (5.50) | 35.7 (5.90) | 34.5 (6.97) | 35.2 (6.04) | 35.1 (5.60)
> Change to day 28 |  |  |  |  |  |  |  | 
> N | 215 | 138 | 95 | 70 | 39 | 36 | 24 | 24
> Mean (SD) | -20.3 (13.19) | -15.8 (14.67) | -18.3 (14.08) | -16.0 (14.30) | -9.9 (13.34) | -6.9 (9.65) | -10.3 (11.96) | -5.5 (7.64)
> MMRM analysis a |  |  |  |  |  |  |  | 
> Diff. of LS means b (SE) | -4.5 (1.41) |  | -1.6 (2.04) |  | -3.4 (2.41) |  | -5.0 (3.05) | 
> 95% CI on difference | -7.26, − 1.70 |  | -5.60, 2.41 |  | -8.14, 1.41 |  | -11.05, 1.03 | 
> 
> TABLE Table 5: Mean (SD) change from baseline to day 28 for SDS, PHQ-9, and GAD-7 total score by sex in pooled TRANSFORM-1/TRANSFORM-2 trials
>  | TRANSFORM-1/TRANSFORM-2
>  | Women | Men
>  | Esketamine + antidepressant | Antidepressant + placebo | Esketamine + antidepressant | Antidepressant + placebo
> SDS total score |  |  |  | 
> N | 177 | 115 | 84 | 60
> Mean (SD) | -12.5 (9.30) | -9.6 (9.50) | -10.6 (9.22) | -7.4 (8.12)
> PHQ-9 total score |  |  |  | 
> N | 218 | 138 | 95 | 70
> Mean (SD) | -12.3 (7.39) | -10.1 (7.99) | -10.9 (7.62) | -8.6 (8.25)
> GAD-7 total score |  |  |  | 
> N | 227 | 139 | 103 | 74
> Mean (SD) | -8.1 (5.90) | -6.9 (5.78) | -6.7 (5.84) | -5.4 (5.98)
> 
> TABLE Table 6: Most frequently reported treatment-emergent adverse events in the double-blind treatment phase of short-term randomized, controlled TRD trials by sex and treatment group
>  | TRANSFORM-1/TRANSFORM-2 | TRANSFORM-3
>  | Women | Men | Women | Men
>  | Esketamine + antidepressant N = 237 | Antidepressant + placebo N = 144 | Esketamine + antidepressant N = 109 | Antidepressant + placebo N = 78 | Esketamine + antidepressant N = 45 | Antidepressant + placebo N = 40 | Esketamine + antidepressant N = 27 | Antidepressant + placebo N = 25
> Total with AEs | 209 (88.2%) | 96 (66.7%) | 92 (84.4%) | 47 (60.3%) | 34 (75.6%) | 23 (57.5%) | 17 (63.0%) | 16 (64.0%)
> Nausea | 72 (30.4%) | 11 (7.6%) | 26 (23.9%) | 8 (10.3%) | 9 (20.0%) | 3 (7.5%) | 4 (14.8%) | 0
> Headache | 52 (21.9%) | 21 (14.6%) | 18 (16.5%) | 17 (21.8%) | 6 (13.3%) | 1 (2.5%) | 3 (11.1%) | 1 (4.0%)
> Dizziness | 53 (22.4%) | 10 (6.9%) | 29 (26.6%) | 5 (6.4%) | 13 (28.9%) | 4 (10.0%) | 2 (7.4%) | 1 (4.0%)
> Dissociation | 68 (28.7%) | 7 (4.9%) | 24 (22.2%) | 1 (1.3%) | 7 (15.6%) | 1 (2.5%) | 2 (7.4%) | 0
> Vertigo | 62 (26.2%) | 5 (3.5%) | 16 (14.7%) | 0 | 4 (8.9%) | 2 (5.0%) | 4 (14.8%) | 0
> Dysgeusia | 46 (19.4%) | 19 (13.2%) | 19 (17.4%) | 11 (14.1%) | 2 (4.4%) | 3 (7.5%) | 2 (7.4%) | 0
> Somnolence | 39 (16.5%) | 15 (10.4%) | 21 (19.3%) | 5 (6.4%) | 1 (2.2%) | 3 (7.5%) | 0 | 0
> Paresthesia | 31 (13.1%) | 2 (1.4%) | 12 (11.0%) | 2 (2.6%) | 2 (4.4%) | 2 (5.0%) | 2 (7.4%) | 0
> Anxiety | 19 (8.0%) | 10 (6.9%) | 12 (11.0%) | 2 (2.6%) | 2 (4.4%) | 2 (5.0%) | 0 | 3 (12.0%)
> Fatigue | 19 (8.0%) | 9 (6.3%) | 6 (5.5%) | 2 (2.6%) | 7 (15.6%) | 4 (10.0%) | 2 (7.4%) | 1 (4.0%)
> BP increased | 16 (6.8%) | 3 (2.1%) | 14 (12.8%) | 2 (2.6%) | 8 (17.8%) | 3 (7.5%) | 1 (3.7%) | 0
> Hypoesthesia | 25 (10.5%) | 1 (0.7%) | 13 (11.9%) | 2 (2.6%) | 3 (6.7%) | 1 (2.5%) | 1 (3.7%) | 0
> Hypoesthesia oral | 29 (12.2%) | 2 (1.4%) | 8 (7.3%) | 1 (1.3%) | 4 (8.9%) | 0 | 1 (3.7%) | 0
> Vomiting | 27 (11.4%) | 3 (2.1%) | 5 (4.6%) | 1 (1.3%) | 5 (11.1%) | 0 | 0 | 1 (4.0%)
> UTI | 6 (2.5%) | 2 (1.4%) | 0 | 1 (1.3%) | 6 (13.3%) | 1 (2.5%) | 0 | 0

#### E0282 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[4]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Using data from 2 phase III studies of esketamine, we found no significant genotype effect on reductions in Montgomery–Åsberg Depression Rating Scale total score or on dissociative responses in patients with treatment-resistant depression treated with esketamine + oral antidepressant.

#### E0283 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[39]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The antidepressant effect was assessed by the difference in the change in Montgomery–Åsberg Depression Rating Scale (MADRS) total score on day 2 (24 hours after the initial esketamine dose) and day 28 (study endpoint) between depressed patients randomized to receive esketamine nasal spray plus a newly initiated oral antidepressant (esketamine + antidepressant [AD]) vs patients randomized to receive placebo nasal spray plus a newly initiated oral antidepressant (AD + placebo).

#### E0284 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[42]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Potential associations between the OPRM1 SNP and changes in MADRS total score at day 2 and day 28 were evaluated to test the a priori hypothesis.

#### E0285 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[48]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary outcome consisted of the MADRS total score change from baseline at day 2 and day 28.

#### E0286 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[59]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Baseline Demographics and Clinical Characteristics of Patients with OPRM1 SNP rs1799971 (A118G) Alleles Esketamine + AD AD + placebo AA (n = 176) AG/GG (n = 57) AA (n = 129) AG/GG (n = 44) Age, year Mean (SD) 45.6 (11.27) 46.1 (12.76) 48.1 (10.65) 46.1 (11.27) Range 18–64 19–64 22–64 22–63 Sex, n (%) Male 58 (33.0) 15 (26.3) 47 (36.4) 14 (31.8) Female 118 (67.0) 42 (73.7) 82 (63.6) 30 (68.2) Race, n (%) American Indian or Alaskan Native 1 (0.6) 0 0 0 Asian 2 (1.1) 2 (3.5) 2 (1.6) 1 (2.3) Black or African American 15 (8.5) 0 5 (3.9) 1 (2.3) White 142 (80.7) 52 (91.2) 117 (90.7) 36 (81.8) Multiple, not reported, other 16 (9.1) 3 (5.3) 5 (3.9) 6 (13.6) Age when diagnosed with MDD, year Mean (SD) 31.3 (12.26) 34.2 (13.97) 35.9 (13.30) 32.2 (12.20) Range 9–59 10–60 9–64 5–57 Duration of current episode, weeks Mean (SD) 158.2 (270.06) 192.4 (210.08) 126.5 (221.79) 135.3 (172.51) Range 9–2288 15–1080 6–1720 14–832 No. of previous antidepressant medications a , n (%) 1 or 2 118 (67.0) 28 (49.1) 83 (64.3) 27 (61.4) ≥3 58 (33.0) 29 (50.9) 46 (35.7) 17 (38.6) Class of oral antidepressant, n (%) SNRI 108 (61.4) 34 (59.6) 83 (64.3) 27 (61.4) SSRI 68 (38.6) 23 (40.4) 46 (35.7) 17 (38.6) Baseline CGI-S Mean (SD) 5.1 (0.71) 5.2 (0.68) 5.1 (0.66) 5.2 (0.76) Range 4–7 4–7 4–7 4–7 Baseline PHQ-9 total score Mean (SD) 20.5 (3.46) 20.1 (4.46) 20.4 (3.68) 21.2 (3.67) Range 9–27 5–27 10–27 10–27 Baseline MADRS total score Mean (SD) 37.7 (5.45) 37.8 (5.68) 37.2 (6.14) 38.2 (5.44) Range 22–49 26–48 18–52 29–53 Abbreviations: AD, antidepressant; CGI-S, Clinical Global Impression–Severity; MADRS, Montgomery–Åsberg Depression Rating Scale; MGH-ATRQ, Massachusetts General Hospital Antidepressant Treatment Response Questionnaire; PHQ-9, Patient Health Questionnaire 9-Item; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor. a Number of antidepressant medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained from MGH-ATRQ, in addition to one prospective antidepressant.

#### E0287 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[60]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the esketamine + AD arm, no significant genotype effects of SNP rs1799971 (A118G) on MADRS score reductions were detected on either day 2 ( Table 2 ; Figure 1 ) or day 28 ( Table 2 ; Figure 2 ).

#### E0288 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[61]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean (SD) reduction from baseline in MADRS total score was −9.62 (10.14) (AA genotype) and −10.49 (10.79) (AG/GG genotype) on day 2 and −20.95 (12.75) (AA genotype) and −23.16 (13.53) (AG/GG genotype) on day 28.

#### E0289 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[63]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score Esketamine + AD AD + placebo Minor allele frequency n Slope P value R 2 partial Minor allele effect n Slope P value R 2 partial Minor allele effect Day 2 0.13 229 −0.63 .69 <0.5 % None 169 −6.59 <.001 10% Greater response Day 28 0.13 232 −1.81 .34 <0.5 % None 172 −4.30 .07 2% None Abbreviations: AD, antidepressant; MADRS, Montgomery–Åsberg Depression Rating Scale; P value, probability of rejecting H0: slope = 0 while H0 is true; R 2 partial , proportion of variance explained by the SNP regressor; Slope, regression coefficient for the SNP regressor; SNP, single nucleotide polymorphism.

#### E0290 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[66]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of OPRM1 single nucleotide polymorphism (SNP) rs1799971 (A118G) alleles on improvements in depression severity, assessed as reductions from baseline in the Montgomery–Åsberg Depression Rating Scale (MADRS) total score on day 2.

#### E0291 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[69]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of OPRM1 single nucleotide polymorphism (SNP) rs1799971 (A118G) alleles on improvements in depression severity, assessed as reductions from baseline in the Montgomery–Åsberg Depression Rating Scale (MADRS) total score on day 28.

#### E0292 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[71]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the AD + placebo arm, a significant genotype effect of SNP rs1799971 (A118G) on the MADRS score reduction on day 2 was detected ( Table 2 ; Figure 1 ) such that the patients with the AG and GG genotypes showed a greater reduction on MADRS total scores than those with the AA genotype.

#### E0293 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[72]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> There was a nonsignificant trend towards a similar effect of SNP rs1799971 (A118G) on MADRS score reductions on day 28, with the reductions in patients with the AG/GG genotypes being numerically greater than those in patients with the AA genotype ( Figure 2 ).

#### E0294 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[74]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean (SD) reduction from baseline in MADRS total score was −4.37 (8.08) (AA genotype) and −11.28 (10.44) (AG/GG genotype) on day 2 and −15.75 (14.67) (AA genotype) and −20.77 (14.59) (AG/GG genotype) on day 28.

#### E0295 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[76]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In TRANSFORM-2, at day 2 visit, patients treated with AD + placebo responded with an additional improvement of 10.53 points on MADRS total scores ( P < .001) for the G-allele carriers compared with 1.39 ( P = .53) for noncarriers.

#### E0296 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[92]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Although not significant, the 2-point (esketamine + AD arm) and 5-point (AD + placebo arm) difference between the AA and AG/GG genotypes with regard to reduction in the MADRS total score on day 28 may be clinically relevant.

#### E0297 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[98]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The mean reduction in MADRS scores was −6 for both doses tested of ETS6103 compared with −11 for amitriptyline.

#### E0298 — embedded_fulltext_window

Source: cache/esketamine-trd-madrs/records.json#/fulltext_by_pmid/32367114#sentence-window[145]. Class: OTHER; MADRS, clinician-rated scale. Binding: **MATCHED_SECONDARY_REPORT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Supplementary Material pyaa030_suppl_Supplementary_Table_1 Click here for additional data file.
> 
> 
> === TABLES (structured; cell boundaries = ' | ') ===
> TABLE Table 1.: Baseline Demographics and Clinical Characteristics of Patients with OPRM1 SNP rs1799971 (A118G) Alleles
>  | Esketamine + AD | AD + placebo
>  | AA (n = 176) | AG/GG (n = 57) | AA (n = 129) | AG/GG (n = 44)
> Age, year |  |  |  | 
> Mean (SD) | 45.6 (11.27) | 46.1 (12.76) | 48.1 (10.65) | 46.1 (11.27)
> Range | 18–64 | 19–64 | 22–64 | 22–63
> Sex, n (%) |  |  |  | 
> Male | 58 (33.0) | 15 (26.3) | 47 (36.4) | 14 (31.8)
> Female | 118 (67.0) | 42 (73.7) | 82 (63.6) | 30 (68.2)
> Race, n (%) |  |  |  | 
> American Indian or Alaskan Native | 1 (0.6) | 0 | 0 | 0
> Asian | 2 (1.1) | 2 (3.5) | 2 (1.6) | 1 (2.3)
> Black or African American | 15 (8.5) | 0 | 5 (3.9) | 1 (2.3)
> White | 142 (80.7) | 52 (91.2) | 117 (90.7) | 36 (81.8)
> Multiple, not reported, other | 16 (9.1) | 3 (5.3) | 5 (3.9) | 6 (13.6)
> Age when diagnosed with MDD, year |  |  |  | 
> Mean (SD) | 31.3 (12.26) | 34.2 (13.97) | 35.9 (13.30) | 32.2 (12.20)
> Range | 9–59 | 10–60 | 9–64 | 5–57
> Duration of current episode, weeks |  |  |  | 
> Mean (SD) | 158.2 (270.06) | 192.4 (210.08) | 126.5 (221.79) | 135.3 (172.51)
> Range | 9–2288 | 15–1080 | 6–1720 | 14–832
> No. of previous antidepressant medications a , n (%) |  |  |  | 
> 1 or 2 | 118 (67.0) | 28 (49.1) | 83 (64.3) | 27 (61.4)
> ≥3 | 58 (33.0) | 29 (50.9) | 46 (35.7) | 17 (38.6)
> Class of oral antidepressant, n (%) |  |  |  | 
> SNRI | 108 (61.4) | 34 (59.6) | 83 (64.3) | 27 (61.4)
> SSRI | 68 (38.6) | 23 (40.4) | 46 (35.7) | 17 (38.6)
> Baseline CGI-S |  |  |  | 
> Mean (SD) | 5.1 (0.71) | 5.2 (0.68) | 5.1 (0.66) | 5.2 (0.76)
> Range | 4–7 | 4–7 | 4–7 | 4–7
> Baseline PHQ-9 total score |  |  |  | 
> Mean (SD) | 20.5 (3.46) | 20.1 (4.46) | 20.4 (3.68) | 21.2 (3.67)
> Range | 9–27 | 5–27 | 10–27 | 10–27
> Baseline MADRS total score |  |  |  | 
> Mean (SD) | 37.7 (5.45) | 37.8 (5.68) | 37.2 (6.14) | 38.2 (5.44)
> Range | 22–49 | 26–48 | 18–52 | 29–53
> 
> TABLE Table 2.: Effects of OPRM1 SNP rs1799971 (A118G) Variation on Improvements in Depression Severity, Assessed as Reductions from Baseline in the MADRS Score
>  |  | Esketamine + AD | AD + placebo
>  | Minor allele frequency | n | Slope | P value | R 2 partial | Minor allele effect | n | Slope | P value | R 2 partial | Minor allele effect
> Day 2 | 0.13 | 229 | −0.63 | .69 | <0.5 % | None | 169 | −6.59 | <.001 | 10% | Greater response
> Day 28 | 0.13 | 232 | −1.81 | .34 | <0.5 % | None | 172 | −4.30 | .07 | 2% | None
> 
> TABLE Table 3.: Effects of OPRM1 SNP rs1799971 (A118G) Variation on Dissociative Symptoms Assessed Using the CADSS a
>  |  | Esketamine + AD | AD + placebo
>  | Minor allele frequency | n | Slope | P value | R 2 partial | Minor allele effect | n | Slope | P value | R 2 partial | Minor allele effect
> Day 1 | 0.13 | 258 | 1.43 | .27 | <0.5 % | None | 182 | 0.27 | .64 | <0.5 % | None
> Day 25 | 0.13 | 228 | 0.68 | .50 | <0.5 % | None | 171 | −0.15 | .64 | <0.5 % | None
> Change | 0.13 | 225 | 0.31 | .74 | <0.5 % | None | 167 | −0.19 | .55 | <0.5 % | None

### melatonin-primary-insomnia-sol — PMID 20712869

Pinned served row:
~~~json
{
  "id": "PMID 20712869",
  "mean1": -19.1,
  "sd1": 47.3,
  "nc1": 137,
  "mean2": -1.7,
  "sd2": 47.8,
  "nc2": 144,
  "source": "ClinicalTrials.gov results (structured, continuous): outcome 'The Change From Baseline in Subjective Sleep Latency.' mean -19.1 (SD 47.3, n=137) [Circadin] vs -1.7 (SD 47.8, n=144) [Placebo] minutes — population: Pre-planned analysis on ITT population age 65-80",
  "timeframe": "Baseline and 3 weeks"
}
~~~

#### E0299 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/84/abstract. Class: DIARY; sleep diary primary result; PSQI separated in full text. Binding: **PRIMARY_REPORT**.

Population: Age 65-80 subgroup served; low-excretor and other populations kept separate. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Melatonin is extensively used in the USA in a non-regulated manner for sleep disorders. Prolonged release melatonin (PRM) is licensed in Europe and other countries for the short term treatment of primary insomnia in patients aged 55 years and over. However, a clear definition of the target patient population and well-controlled studies of long-term efficacy and safety are lacking. It is known that melatonin production declines with age. Some young insomnia patients also may have low melatonin levels. The study investigated whether older age or low melatonin excretion is a better predictor of response to PRM, whether the efficacy observed in short-term studies is sustained during continued treatment and the long term safety of such treatment. METHODS: Adult outpatients (791, aged 18-80 years) with primary insomnia, were treated with placebo (2 weeks) and then randomized, double-blind to 3 weeks with PRM or placebo nightly. PRM patients continued whereas placebo completers were re-randomized 1:1 to PRM or placebo for 26 weeks with 2 weeks of single-blind placebo run-out. Main outcome measures were sleep latency derived from a sleep diary, Pittsburgh Sleep Quality Index (PSQI), Quality of Life (World Health Organzaton-5) Clinical Global Impression of Improvement (CGI-I) and adverse effects and vital signs recorded at each visit. RESULTS: On the primary efficacy variable, sleep latency, the effects of PRM (3 weeks) in patients with low endogenous melatonin (6-sulphatoxymelatonin [6-SMT] <or=8 microg/night) regardless of age did not differ from the placebo, whereas PRM significantly reduced sleep latency compared to the placebo in elderly patients regardless of melatonin levels (-19.1 versus -1.7 min; P = 0.002). The effects on sleep latency and additional sleep and daytime parameters that improved with PRM were maintained or enhanced over the 6-month period with no signs of tolerance. Most adverse events were mild in severity with no clinically relevant differences between PRM and placebo for any safety outcome. CONCLUSIONS: The results demonstrate short- and long-term efficacy and safety of PRM in elderly insomnia patients. Low melatonin production regardless of age is not useful in predicting responses to melatonin therapy in insomnia. The age cut-off for response warrants further investigation.

#### E0300 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/83/abstract. Class: DIARY; sleep diary primary result; PSQI separated in full text. Binding: **SECONDARY_OR_POOLED_REPORT**.

Population: Named subgroup or pooled secondary report; exact population in quote; do not split pooled estimates. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVES: The authors recently reported on efficacy and safety of prolonged-release melatonin formulation (PRM; Circadin 2  mg) in elderly insomnia patients. The age cut-off for response to PRM and the long-term maintenance of efficacy and safety were further evaluated by looking at the total cohort (age 18-80 years) from that study and subsets of patients aged 18-54 and 55-80 years (for whom the drug is currently indicated). DESIGN: Randomised, double-blind, placebo controlled trial. SETTING: Multicentre, outpatients, primary care setting. METHODS: A total of 930 males and females aged 18-80 years with primary insomnia who reported mean nightly sleep latency (SL) >20  min were enrolled and 791 entered the active phase of the study. The study comprised a 2-week, single-blind placebo run-in period followed by 3 week's double-blind treatment with PRM or placebo, one tablet per day at 2 hours before bedtime. PRM patients continued whereas placebo completers were re-randomised 1:1 to PRM or placebo for 26 weeks followed by 2-weeks run-out on placebo. MAIN OUTCOME MEASURES: SL and other sleep variables derived from sleep diary, Pittsburgh Sleep Quality Index (PSQI), Quality of life (WHO-5), Clinical Global Impression of Improvement (CGI-I) and adverse effects, recorded each visit, withdrawal and rebound effects during run-out. RESULTS: In all, 746 patients completed the 3-week and 555 (421 PRM, 134 placebo) completed the 6-month period. The principal reason for drop-out was patient decision. At 3 weeks, significant differences in SL (diary, primary variable) in favour of PRM vs. placebo treatment were found for the 55-80-year group (-15.4 vs. -5.5  min, p = 0.014) but not the 18-80-year cut-off which included younger patients. Other variables (SL-PSQI, PSQI, WHO-5, CGI-I scores) improved significantly with PRM in the 18-80-year population, more so than in the 55-80-year age group. Improvements were maintained or enhanced over the 6-month period with no signs of tolerance. No withdrawal symptoms or rebound insomnia were detected. Most adverse events were mild with no significant differences between PRM and placebo groups in any safety outcome. CONCLUSIONS: The results demonstrate short- and long-term efficacy of PRM in insomnia patients aged 18-80 years, particularly those aged 55 and over. PRM was well-tolerated over the entire 6-month period with no rebound or withdrawal symptoms following discontinuation. Study Registry No: ClinicalTrials.gov ID: NCT00397189.

#### E0301 — registry_arm

Source: cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/0. Class: DIARY; sleep diary / patient log. Binding: **DIRECT**.

Population: Pre-planned analysis on ITT population age 65-80; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "137".

Class evidence:
> Sleep latency (SL) after 3 weeks of treatment was assessed by Patient Daily Sleep Diary (National sleep foundation sleep diary). The patients reported subjectively of their SL. The Sleep Diary question 3 (SL) was summarised at baseline (end of the two-week run-in period) and after three weeks double-blind treatment (actual and change from baseline) for each treatment group using descriptive statistics. At each visit, the mean of the seven days prior to the visit were used. For each treatment group, the mean score at visit 3 was compared, adjusting for the visit 2 score. An ANCOVA model was used. Lower score indicates reduction in sleep latency and thus considered improvement The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.

> {"groupId": "OG000", "value": "-19.1", "spread": "47.3"}

#### E0302 — registry_arm

Source: cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/1. Class: DIARY; sleep diary / patient log. Binding: **DIRECT**.

Population: Pre-planned analysis on ITT population age 65-80; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "144".

Class evidence:
> Sleep latency (SL) after 3 weeks of treatment was assessed by Patient Daily Sleep Diary (National sleep foundation sleep diary). The patients reported subjectively of their SL. The Sleep Diary question 3 (SL) was summarised at baseline (end of the two-week run-in period) and after three weeks double-blind treatment (actual and change from baseline) for each treatment group using descriptive statistics. At each visit, the mean of the seven days prior to the visit were used. For each treatment group, the mean score at visit 3 was compared, adjusting for the visit 2 score. An ANCOVA model was used. Lower score indicates reduction in sleep latency and thus considered improvement The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.

> {"groupId": "OG001", "value": "-1.7", "spread": "47.8"}

#### E0303 — registry_analysis

Source: cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/analyses/0. Class: DIARY; sleep diary / patient log. Binding: **DIRECT**.

Population: Pre-planned analysis on ITT population age 65-80; The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Sleep latency (SL) after 3 weeks of treatment was assessed by Patient Daily Sleep Diary (National sleep foundation sleep diary). The patients reported subjectively of their SL. The Sleep Diary question 3 (SL) was summarised at baseline (end of the two-week run-in period) and after three weeks double-blind treatment (actual and change from baseline) for each treatment group using descriptive statistics. At each visit, the mean of the seven days prior to the visit were used. For each treatment group, the mean score at visit 3 was compared, adjusting for the visit 2 score. An ANCOVA model was used. Lower score indicates reduction in sleep latency and thus considered improvement The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.

> {"groupIds": ["OG000", "OG001"], "groupDescription": "The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.", "nonInferiorityType": "SUPERIORITY_OR_OTHER", "pValue": "<0.05", "statisticalMethod": "ANCOVA", "paramType": "Mean Difference (Final Values)", "paramValue": "-15.6", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-25.3", "ciUpperLimit": "-6", "dispersionType": "STANDARD_DEVIATION", "dispersionValue": "47"}

#### E0304 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[1]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Adult outpatients (791, aged 18-80 years) with primary insomnia, were treated with placebo (2 weeks) and then randomized, double-blind to 3 weeks with PRM or placebo nightly. PRM patients continued whereas placebo completers were re-randomized 1:1 to PRM or placebo for 26 weeks with 2 weeks of single-blind placebo run-out. Main outcome measures were sleep latency derived from a sleep diary, Pittsburgh Sleep Quality Index (PSQI), Quality of Life (World Health Organzaton-5) Clinical Global Impression of Improvement (CGI-I) and adverse effects and vital signs recorded at each visit.

#### E0305 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[2]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> On the primary efficacy variable, sleep latency, the effects of PRM (3 weeks) in patients with low endogenous melatonin (6-sulphatoxymelatonin [6-SMT] ≤8 μg/night) regardless of age did not differ from the placebo, whereas PRM significantly reduced sleep latency compared to the placebo in elderly patients regardless of melatonin levels (-19.1 versus -1.7 min; P = 0.002). The effects on sleep latency and additional sleep and daytime parameters that improved with PRM were maintained or enhanced over the 6-month period with no signs of tolerance. Most adverse events were mild in severity with no clinically relevant differences between PRM and placebo for any safety outcome.

#### E0306 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[5]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Melatonin (N-acetyl-5-methoxytryptamine) is the major hormone produced nocturnally by the pineal gland in a process driven by the biological clock residing in the suprachiasmatic nuclei (SCN). Melatonin is a sleep regulator and signal of darkness in humans [ 1 ]. Thus, the circadian rhythm in the synthesis and secretion of melatonin is closely associated with the sleep rhythm in both sighted and blind subjects [ 2 , 3 ]. Melatonin promotes sleep in humans [ 4 , 5 ], presumably by inhibiting circadian wakefulness mechanisms [ 6 , 7 ] and affects the activity of brain networks compatible with sleep induction [ 8 , 9 ]. Exogenous melatonin has clock-shifting effects and may advance or delay the sleep phase depending on the time of administration according to the Phase-Response Curve [ 10 ].

#### E0307 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[13]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Men and women aged between 18 and 80 years suffering from primary insomnia according to the Diagnostic and Statistical Manual for Mental Disorders (DSM-IV) criteria with sleep latency longer than 20 min were included in the study.

#### E0308 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[20]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The screening and run-in periods were used to wash-out previously administered medicinal products which were incompatible with the trial, for confirmation of a stable disease and compliance with study medication and procedures and for the qualitative and quantitative baseline assessments of patients. Patients with major short-term fluctuations of their condition and non-compliance with study procedures were excluded. A history of sleep latency of >20 min, required for patients inclusion, was assessed once in the telephone interview (SHQ), confirmed at the screening and then at the baseline visits using the PSQI [ 28 - 30 ]. Eligible patients entered the baseline screening run-in period and received 2 weeks of single-blind treatment with placebo. Patients still eligible after the 2-week placebo run-in and who were compliant with respect to treatment, had a negative drug screen and correctly completed study assessment forms were randomized in a 1:1 ratio to receive either PRM 2 mg or placebo for 3 weeks in a double-blind manner. Randomization was stratified by trial site, 6-SMT levels (low ≤8 μg versus high >8 μg/night) and age group (< 65 versus ≥65 years).

#### E0309 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[23]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Patients were instructed to take one tablet daily of study medication orally, 1-2 h before going to bed (preferably between 2100 h and 2200 h) and after food, and were asked to fill in a diary each morning, reporting on sleep latency, sleep maintenance, total sleep time, time going to bed, sleep offset time, refreshed on waking score, morning alertness score, and sleep quality in the previous night).

#### E0310 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[28]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The main objective of this study was to assess the effects of short-term (3-week) therapy with PRM versus placebo on patient reported sleep latency (sleep diary) in their natural setting, in patients with low endogenous melatonin levels (≤8 versus >8 μg urinary 6-SMT/night) and in elderly patients (65-80 years old). Additional sleep and daytime parameters, safety and maintenance of PRM efficacy and safety over a 6-month period were also evaluated.

#### E0311 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[30]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The PSQI has been recommended as an essential measure for global sleep and insomnia symptoms in recent expert consensus recommendations for a standard set of research assessments in insomnia [ 28 ]. It comprises nine questions relating to the patient's usual sleep habits during the previous 2 weeks; the second and third weeks of active treatment. It addresses possible reasons for trouble in sleeping as well as daytime behaviour. An algorithm is used to calculate seven component scores and these are added to give a global PSQI score. The PSQI component scores, Question 2 (Sleep Latency) and Question 4 (Total Sleep Time) after 3 weeks' double-blind treatment, and the change from baseline levels of these parameters. It has been shown that each of the PSQI individual component scores measures a particular aspect of the overall construct. Furthermore, control subjects differ from insomnia patients in all individual components [ 29 ]. However, the correlation between individual items and global score ranged from 0.83 (subjective sleep quality) to 0.07 (cough or snore during sleep) [ 29 ]. In the evaluation of the drug effects it was therefore interesting to look at each component.

#### E0312 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[32]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The predefined primary efficacy variable was the comparison of sleep latency as measured by the sleep diary at 3 weeks treatment weeks with PRM (2 mg) or placebo in the pre-defined subgroups of patients who were low excretors of melatonin regardless of age (primary endpoint) and the patients aged 65-80 years, regardless of melatonin levels. The comparison was done using a linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the primary endpoint). In compliance with US Food Drug Administration regulatory procedures, no correction for multiple comparisons were performed for the primary outcome measure.

#### E0313 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[33]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> All other efficacy endpoints were pre-defined as exploratory and aimed at confirming the results of the primary analysis using additional instruments (for example, PSQI) or adding information on other aspects of the sleep and daytime consequences of the treatment including: (1) time going to bed and sleep offset times, sleep maintenance, total sleep time, sleep quality and morning alertness from the sleep diaries; (2) the PSQI global score; (3) PSQI questions 2 (sleep latency in minutes) and 4 (total sleep time in minutes) and the individual PSQI components; (4) the CGI-I score assessed by the clinician at three to 29 treatment weeks) quality of life derived from the WHO-5 Well-being index covering positive mood, vitality and general interests.

#### E0314 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[34]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Our main conclusion was based on sleep latency, the predefined primary variable. No correction was made for multiple statistical testing for the exploratory variables. Accordingly, the overall conclusions from the results are based on the accumulation of evidence for between-treatment differences which were, in many cases, correlated or complementary, rather than on isolated P -values.

#### E0315 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[35]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Sleep latency as recorded in the sleep diary was summarized for low excretors aged 18-80 years and for patients aged 65-80 years, at baseline after the 2-week run-in period and after 3 weeks double-blind treatment (actual and change from baseline) for each treatment group and, as a whole, using descriptive statistics for continuous variables. At each visit, the mean value of the 7 days prior to the visit was used. Sleep latency as measured by the sleep diary after 3 weeks double-blind treatment was compared using a linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 years).

#### E0316 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[41]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In order to achieve 95% power at the 5% level for the primary objective of assessing the change in sleep latency in the Intention to Treat (ITT) low excretors at Week 3, assuming a treatment effect of 19 min and a residual standard deviation of 40.6 min, 120 participants were required per treatment group. Assuming equal numbers of low and high excretors, 480 patients were required to complete treatment Week 3. Assuming a 10% dropout rate between baseline and Week 3, 540 patients would have to be randomized at baseline. In order to achieve 90% power at the 5% level for the first secondary objective of assessing the change in sleep latency in the ITT dataset of patients aged 65-80 years, assuming a treatment effect of 14 min and a residual standard deviation of 40.7 min, 179 patients ≥65 years were required per group (active and placebo). Therefore, 400 patients in this age range would need to be randomized at baseline. Assuming 45% of 540 patients already randomized would be ≥65 years old (245), an additional 150 patients would need to be randomized at baseline in this age group.

#### E0317 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[53]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The number of patients in the low excretors (86 per treatment group) and 65-80 year-old subgroups (PRM 137; placebo 144) of the FAS was lower than planned. The study failed to meet the design requirements for a 95% statistical power on the primary endpoint (120 low excretors per treatment group) and 90% power on the first secondary endpoint (179 patients ≥65 years per treatment group) involving sleep latency. The power reached with these sample sizes was 86% for the patients with low endogenous melatonin and 82% for the patients aged 65 and older. The 722 patients (225, 31% men; 497 women, 69%) in the FAS had a mean age of 62 years (range 20 to 80 years).

#### E0318 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[55]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The effects of 3 weeks treatment with PRM or placebo on patient reported sleep latency (sleep diary) for low excretors and elderly patients are shown in Table 3 . Sleep latency after 3 weeks of treatment was not significant in low excretors aged 18-80 between the PRM and placebo groups, as measured by the sleep diary, whereas a significant difference in favour of PRM was found for patients aged 65-80 years (-15.6 min; 95% CI -25.3 to -6.0, P = 0.002; Table 3 ; Figure 2 ).

#### E0319 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[56]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients.

#### E0320 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[57]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors).

#### E0321 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[59]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The effect of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep latency in the low excretors and age 65-80 populations . Mean+standard error of mean values of the change from baseline in sleep latency from the sleep diary following 3 weeks of double blind treatment of low excretors ( N = 86 per group) and age 65-80 years ( N = 137 PRM, 144 placebo) populations with PRM and placebo. Asterisks denote significant difference between PRM and placebo groups (** P < 0.01).

#### E0322 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[62]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> *The global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness

#### E0323 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[70]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The results of the diary, PSQI variables, CGI-I and WHO-5 Index for patients aged 65-80 years are presented in Tables 6 and 7 . In patients aged 65-80 years, in the short-term period the PRM group showed significant advantages in sleep latency assessed by PSQI question 2 [-13.7 (-23.5, -3.9), P = 0.006], sleep maintenance assessed by the sleep diary [-0.17 (-0.33, 0.00), P = 0.046], time going to bed (hours relative to midnight) assessed by the sleep diary [-0.22 (-0.39, -0.05), P = 0.012], and quality of sleep as assessed by Global PSQI scores [-0.64 (-1.25, -0.02), P = 0.042; Tables 6 and 7 ].

#### E0324 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[74]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness.

#### E0325 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[82]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In the low excretors (regardless of age) a longer total sleep time was seen with PRM compared to placebo treated patients (estimated difference 13.1 min, 95% CI 1.0 to 25.2, P = 0.035; Table 4 ). PSQI global scores were lower (improved) in the PRM group across study visits with significant global treatment effects [-0.66 (-1.30, -0.01), P = 0.046; Table 5 ]. WHO-5 Index scores were significantly improved in PRM patients for the low excretors [0.91 (0.16, 1.66), P = 0.017; Table 5 ]. CGI-I scores were significantly lower (improved) across study visits in the PRM group compared with placebo for these patients [-0.25 (-0.49, -0.01), p = 0.042; Table 5 ]. Concerning sleep latency, there was a significant improvement with PRM over placebo in the low excretors when measured with the PSQI question 2 [-11.6 (-22.0, -1.1) min, P = 0.030] that was less consistently observed with the diary [-6.7 (-16.4, 3.0) min, P = 0.174; Tables 4 and 5 ].

#### E0326 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[83]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The results of the long-term analyses using MMRM for low excretors aged 18-80 and for patients aged 65-80 years are presented in Tables 6 and 7 . In patients aged 65-80 (regardless of melatonin excretion), sleep latency throughout the long term period was significantly shorter in the PRM group as assessed by the sleep diary with a mean difference from placebo of -14.5 min (-21.4, -7.7; P < 0.001; Table 6 ). Similar results were observed with sleep latency recorded by PSQI component 2 and PSQI question 2 (Table 7 ) The estimated treatment effect differences for sleep latency during the extension period for these patients show incremental difference between PRM and placebo with time of treatment up to 3 months reaching plateau levels that are maintained to the rest of the 6 months period (Figure 3 ). A similar pattern was seen for time going to bed, with PRM patients going to bed significantly earlier than placebo patients (treatment difference -0.21 h over placebo; 95% CI -0.33 to -0.08, P = 0.002; Table 6 and Figure 4 ). There was some indication that PRM patients also woke up somewhat earlier (treatment difference -0.12 h; 95% CI -0.24 to 0.00, P = 0.051).

#### E0327 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[84]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Sleep latency during the treatment period . Mixed Effect Model for Repeated Measures (MMRM) predicted mean values (mean + standard error of mean) for sleep latency from the sleep diary, at baseline and weeks 3-29 of the double blind treatment periods, in those aged 65-80 years. Asterisks denote significant difference between prolonged release melatonin and placebo groups (* P < 0.05 ** P < 0.01). Numbers of patients analysed in each treatment time point are depicted

#### E0328 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[87]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Consistent with the improvements in quality of sleep (PSQI global score) and sleep latency (diary), components 1 (sleep quality) and 2 (sleep latency) of the PSQI were significantly lower (improved) in the PRM group across study visits in patients aged 65-80 years [-0.15 (-0.25, -0.04), P = 0.006, -0.24 (-0.38, -0.10), P = 0.001]. PSQI question 2 (sleep latency) was significantly lower across study visits in the PRM group in the age 65-80 population [-12.1 min (-19.1, -5.1), P = 0.001].

#### E0329 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[100]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> To our knowledge, this is the first double-blind, placebo-controlled randomized trial evaluating the long-term effects of melatonin treatment in insomnia patients. A total of 722 of the 791 randomized patients were analysed in the full analysis set in this study with a DSM IV diagnosis of primary insomnia and a sleep latency of at least 20 min (mean sleep latency 74 min).

#### E0330 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[101]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The main aim of this study, based on the shortening of sleep latency, was to determine if endogenous melatonin level regardless of age is useful to predict response to PRM therapy. The results provide evidence that short-term (3 weeks) treatment with PRM is effective in elderly patients. Notably, the age cutoff for patients >65 years used for the primary analysis in this study, does not preclude response to PRM in younger patients. Rather, there is sufficient evidence in previous studies [ 21 - 25 ] for an equal or greater response to PRM in patients aged 55 and older. Thus, further studies of the age cut-off for response are warranted.

#### E0331 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[103]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The effects of PRM on sleep latency in the 65-80-year-old patients are very similar to those found with current hypnotic drugs, including those developed primarily for patients with difficulty falling asleep [ 36 - 38 ]. The PRM efficacy reported in the present study is not only statistically significant but also clinically relevant. Furthermore, there were no signs of tolerance, as there was no reduction in benefit during the long-term treatment.

#### E0332 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[104]. Class: NOT_STATED; Explicit absence of PSG/actigraphy. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> A limitation of this study was the lack of polysomnographic or actigraphic data. However, in clinical practice, patients with insomnia do not receive overnight sleep recordings and physicians base the success of any given treatment on patient reports of improved sleep and well being [ 39 ]. Furthermore actigraphy is considered less useful for sleep latency in insomnia [ 40 ]. Evidently the hypnotic effect of PRM in this study as measured by subjective means is very much like that documented in the sleep laboratory and previous studies using clinical assessments [ 24 , 25 ]. Therefore, the subjective improvements in this study are relevant and allow a better understanding the efficacy of PRM in the treatment of insomnia.

#### E0333 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[105]. Class: PSG; polysomnography / EEG. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The magnitude of the effects of PRM on sleep latency documented in the present study, agree well with the results of the previous clinical trials with this drug [ 24 ], including a sleep laboratory study using polysomnography [ 25 ] in patients aged 55 and older. The observed effect on sleep latency for patients aged 65-80 years (-15.6 min; 95% CI -25.3 to -6.0, P = 0.002) was larger than would be predicted according to the published meta-analysis on efficacy of exogenous melatonin for primary insomnia [-7.2 min (95% CI -12.0, -2.4; n = 12)] [ 20 ] which was predominantly based on studies in younger patients and their use of immediate release preparations. The apparently weaker efficacy profile of 3 weeks treatment with PRM in the low excretors (18-80 years) may thus be due to the younger patients (aged <55 years) in the population.

#### E0334 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[106]. Class: QUESTIONNAIRE; Pittsburgh Sleep Quality Index (PSQI). Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> There is evidence of improvements of additional sleep and daytime parameters with PRM. Global PSQI scores were improved in PRM patients aged 65 and older, in both the short and long term. Notably, in this trial, patients with poor quality of sleep alone were not entered; patients had also to have some difficulty in falling asleep to be included. It is therefore not surprising that in the short term, these overall effects may mainly be driven by reductions in sleep latency (component 2). In the long term, however, there was evidence of treatment benefits with respect to both sleep latency and sleep quality (component 1). There was also evidence of a delayed effect of PRM treatment in improve morning alertness (as measured by the diary) over the 6-month treatment period. Improvement in sleep quality and morning alertness were consistently found in clinical trials with PRM [ 23 - 25 ] but not in studies with immediate release melatonin formulations or the MT1/MT2 melatonin receptor agonist ramelteon [ 20 , 38 , 41 ]. Such improvements were also difficult to demonstrate with other insomnia drugs. Furthermore, the benefit of PRM in the patients' overall clinical status (as measured by the CGI-I scores) improved after long-term treatment, in patients aged 65-80 years.

#### E0335 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#p[108]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> A rather unexpected aspect of PRM efficacy is the incremental nature of the response with time. In addition, there seems to be a significant urge to advance bedtime with this treatment. These findings may indicate an effect on the treatment on the internal temporal order. There is a great deal of evidence indicating that aging is characterized by a progressive deterioration of circadian timekeeping, including loss of SCN melatonin receptors [ 14 , 42 - 44 ]. Functional disturbances of SCN circadian activity may start already around the age of 50, as evidenced by a decrease in vasopressin rhythmic function, in the expression of melatonin receptors in the SCN and in melatonin production compared to younger adults [ 14 , 16 , 43 ]. Consequently, there is disorganization of the internal temporal order [ 12 , 44 ]. PRM treatment has been shown to delay the nocturnal cortisol production in elderly insomnia patients towards the morning [ 45 ], improve blood pressure rhythms [ 46 ] and, as shown here, progressively advance time to bed in those aged 65-80 years old in addition to the shortening of sleep latency. Improvement in internal temporal order with PRM may explain why the treatment effects are more prominent in older patients and there is a gradual development of response over days or weeks [ 25 ]. Further research will aim at investigating whether the evolution of response to PRM represents a re-activation of the circadian system or reinforcement of responsiveness to melatonin.

#### E0336 — fulltext_table

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#table-wrap[@id=T3]. Class: DIARY; sleep diary. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: Separate low-excretor and age 65-80 populations. Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

#### E0337 — fulltext_table

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#table-wrap[@id=T4]. Class: DIARY; sleep diary. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: Low excretors, ages 18-80. Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 4 Sleep diary parameters in the low excretors. Treatment effects Change from baseline Mean (SD) Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 99 Placebo 86 31 Sleep latency PRM -9.0 (50.5) -23.6 (42.1) -0.6 (-14.0, 12.7) -6.7 (-16.4, 3.0) (min) Placebo -9.0 (48.7) -19.4 (79.5) P = 0.924 P = 0.174 Sleep PRM -0.27 (0.77) -0.31 (1.08) -0.16 (-0.39, 0.08) -0.04 (-0.24, 0.16) maintenance Placebo -0.12 (1.04) -0.34 (0.71) P = 0.185 P = 0.677 Total sleep PRM 0.34 (0.88) 0.70 (1.00) 9.1 (-6.1, 24.4) 13.1 (1.0, 25.2) time (h) Placebo 0.20 (0.91) 0.47 (1.18) P = 0.236 P = 0.035 Sleep onset PRM -0.15 (0.89) -0.46 (0.79) -0.08 (-0.33, 0.17) -0.16 (-0.34, 0.03) (h) Placebo -0.05 (0.80) -0.24 (1.11) P = 0.530 P = 0.096 Sleep offset PRM 0.09 (0.79) 0.08 (0.84) 0.04 (-0.18, 0.25) 0.07 (-0.09, 0.22) (h) Placebo 0.10 (0.75) 0.20 (1.00) P = 0.744 P = 0.392 Refreshed on PRM -0.09 (0.46) -0.23 (0.43) -0.01 (-0.13, 0.11) -0.03 (-0.12, 0.06) waking Placebo -0.09 (0.40) -0.29 (0.47) P = 0.830 P = 0.540 Morning PRM -0.14 (0.67) -0.42 (0.65) 0.01 (-0.18, 0.19) -0.06 (-0.19, 0.08) alertness Placebo -0.19 (0.63) -0.35 (0.73) P = 0.936 P = 0.426 Sleep quality PRM -0.20 (0.67) -0.43 (0.70) -0.04 (-0.24, 0.16) -0.08 (-0.23, 0.06) Placebo -0.16 (0.70) -0.34 (0.60) P = 0.688 P = 0.266 *The global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness C, confidence interval; SD, standard deviation; PRM, prolonged release melatonin.

#### E0338 — fulltext_table

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#table-wrap[@id=T5]. Class: QUESTIONNAIRE; PSQI question 2 (minutes) and component 2 (ordinal score). Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: Low excretors, ages 18-80. Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 5 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the low excretors. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 86 101 Placebo 86 31 PSQI PRM -2.13 (2.89) -3.78 (3.65) -0.40 (-1.19, 0.38) -0.66 (-1.30, -0.01) Global score Placebo -1.62 (2.59) -2.94 (2.91) P = 0.313 P = 0.046 PSQI PRM -0.30 (0.83) -0.72 (0.80) -0.02 (-0.22, 0.19) -0.13 (-0.29, 0.02) Component 1 Placebo -0.26 (0.67) -0.42 (1.06) P = 0.884 P = 0.086 PSQI PRM -0.37 (0.72) -0.90 (1.02) -0.12 (-0.33, 0.10) -0.17 (-0.36, 0.02) Component 2 Placebo -0.26 (0.71) -0.68 (0.79) P = 0.278 P = 0.080 PSQI PRM -0.50 (0.89) -0.87 (1.04) -0.04 (-0.29, 0.21) -0.13 (-0.33, 0.06) Component 3 Placebo -0.44 (0.83) -0.65 (0.88) P = 0.735 P = 0.169 PSQI PRM -0.40 (1.09) -0.89 (1.25) 0.09 (-0.20, 0.39) -0.01 (-0.24, 0.21) Component 4 Placebo -0.45 (0.99) -0.77 (1.12) P = 0.537 P = 0.918 PSQI PRM -0.09 (0.33) -0.01 (0.48) -0.10 (-0.18, -0.03) -0.01 (-0.06, 0.05) Component 5 Placebo 0.03 (0.32) -0.03 (0.31) P = 0.008 P = 0.811 PSQI PRM 0.00 (0.00) 0.00 (0.00) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.47 (0.82) -0.39 (0.99) -0.17 (-0.35, 0.01) -0.06 (-0.17, 0.05) Component 7 Placebo -0.24 (0.87) -0.39 (0.84) P = 0.067 P = 0.283 PSQI PRM -18.3 (52.4) -41.3 (59.0) -0.2 (-13.2, 12.8) -11.6 (-22.0, -1.1) Question 2 Placebo -18.5 (51.7) -33.1 (92.2) P = 0.980 P = 0.030 PSQI PRM 0.63 (1.10) 1.11 (1.33) 0.09 (-0.20, 0.38) 0.17 (-0.07, 0.41) Question 4 Placebo 0.51 (0.94) 0.81 (1.08) P = 0.539 P = 0.164 CGI-I ‡ PRM 3.22 (1.05) 2.50 (1.19) -0.15 (-0.46, 0.16) -0.25 (-0.49, -0.01) Placebo 3.31 (0.98) 3.06 (1.21) P = 0.339 P = 0.042 WHO-5 PRM 1.27 (3.53) 1.79 (4.27) 1.21 (0.22, 2.20), 0.91 (0.16, 1.66) Index Placebo -0.03 (3.45) 1.06 (3.56) P = 0.016 P = 0.017 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported). *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined. CI, confidence interval.

#### E0339 — fulltext_table

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#table-wrap[@id=T6]. Class: DIARY; sleep diary. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: Age 65-80. Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 6 Sleep Diary parameters in the 65-80 age group. Treatment effects Change from baseline Mean (SD) Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 137 159 Placebo 144 61 Sleep latency PRM -19.1 (47.3) -25.9 (46.4) -15.6 (-25.3, -6.0) -14.5 (-21.4, -7.7) (min) Placebo -1.7 (47.8) -8.3 (61.5) P = 0.002 P < 0.001 Sleep PRM -0.24 (0.80) -0.31 (0.94) -0.17 (-0.33, 0.00) -0.09 (-0.22, 0.03) maintenance Placebo -0.09 (0.78) -0.20 (0.70) P = 0.046 P = 0.148 Total sleep PRM 0.34 (0.75) 0.64 (0.99) 7.0 (-3.4, 17.4) 7.5 (-0.7, 15.7) time (h) Placebo 0.20 (0.79) 0.41 (1.06) P = 0.186 P = 0.073 Sleep onset PRM -0.22 (0.80) -0.41 (0.75) -0.22 (-0.39, -0.05) -0.21 (-0.33, -0.08) (hours) Placebo 0.00 (0.71) -0.12 (1.06) P = 0.012 P = 0.002 Sleep offset PRM 0.03 (0.81) 0.03 (0.84) -0.16 (-0.33, 0.02) -0.12 (-0.24, 0.00) (h) Placebo 0.19 (0.79) 0.21 (0.91) P = 0.076 P = 0.051 Refreshed on PRM -0.10 (0.36) -0.22 (0.42) 0.00 (-0.08, 0.08) -0.06 (-0.12, 0.00) waking Placebo -0.09 (0.37) -0.11 (0.42) P = 0.994 P = 0.053 Morning PRM -0.18 (0.52) -0.36 (0.69) -0.04 (-0.16, 0.07) -0.10 (-0.19, -0.01) alertness Placebo -0.11 (0.51) -0.09 (0.60) P = 0.453 P = 0.032 PRM -0.20 (0.56) -0.39 (0.71) -0.06 (-0.19, 0.07) -0.08 (-0.18, 0.01) Sleep quality Placebo -0.12 (0.57) -0.17 (0.54) P = 0.356 P = 0.082 Mean (SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7) sleep latency (diary data) are repeated for completeness. CI, confidence interval

#### E0340 — fulltext_table

Source: cache/melatonin-primary-insomnia-sol/ft_20712869.txt#table-wrap[@id=T7]. Class: QUESTIONNAIRE; PSQI question 2 (minutes) and component 2 (ordinal score). Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: Age 65-80. Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 7 Pittsburgh Sleep Quality Index (PSQI) measures, Clinical Global Impression of Improvement (CGI-I) and World Health Organization-5 Index in the 65-80 age group. Change from baseline Mean (SD) Treatment effects Short term Long term * Visit 3 Visit 7 Estimate (95% CI) P -value Estimate (95% CI) P -value N MAX PRM 136 164 Placebo 144 62 PSQI PRM -1.86 (2.93) -3.34 (3.37) -0.64 (-1.25, -0.02) -0.70 (-1.17, -0.23) Global score Placebo -1.19 (2.53) -2.08 (2.92) P = 0.042 P = 0.003 PSQI PRM -0.32 (0.71) -0.59 (0.82) -0.09 (-0.23, 0.05) -0.15 (-0.25, -0.04) Component 1 Placebo -0.19 (0.65) -0.34 (0.85) P = 0.217 P = 0.006 PSQI PRM -0.43 (0.87) -0.75 (0.99) -0.23 (-0.41, -0.04) -0.24 (-0.38, -0.10) Component 2 Placebo -0.22 (0.74) -0.52 (0.95) P = 0.018 P = 0.001 PSQI PRM -0.48 (0.89) -0.86 (1.08) -0.10 (-0.29, 0.10) -0.10 (-0.25, 0.05) Component 3 Placebo -0.40 (0.89) -0.65 (0.96) P = 0.328 P = 0.177 PSQI PRM -0.32 (0.96) -0.79 (1.22) -0.05 (-0.27, 0.17) -0.10 (-0.26, 0.06) Component 4 Placebo -0.29 (1.04) -0.47 (1.05) P = 0.638 P = 0.236 PSQI PRM 0.01 (0.41) -0.04 (0.43) -0.05 (-0.13, 0.02) 0.00 (-0.05, 0.05) Component 5 Placebo 0.03 (0.39) -0.02 (0.42) P = 0.162 P = 0.973 PSQI PRM -0.01 (0.12) 0.01 (0.18) † † Component 6 Placebo 0.00 (0.00) 0.00 (0.00) PSQI PRM -0.30 (0.95) -0.31 (0.94) -0.04 (-0.19, 0.11) -0.07 (-0.17, 0.02) Component 7 Placebo -0.12 (0.69) -0.10 (0.86) P = 0.636 P = 0.137 PSQI PRM -25.4 (50.9) -32.7 (49.3) -13.7 (-23.5, -3.9) -12.1 (-19.1, -5.1) Question 2 Placebo -8.9 (48.0) -19.0 (65.8) P = 0.006 P = 0.001 PSQI PRM 0.58 (1.03) 1.05 (1.29) 0.10 (-0.13, 0.33) 0.14 (-0.04, 0.32) Question 4 Placebo 0.48 (1.00) 0.71 (1.08) P = 0.381 P = 0.120 PRM 3.34 (1.17) 2.70 (1.17) -0.12 (-0.37, 0.14) -0.20 (-0.38, -0.02) CGI-I ‡ Placebo 3.54 (0.85) 3.19 (1.11) P = 0.364 P = 0.027 WHO-5 PRM 1.02 (3.73) 1.51 (4.05) 0.42 (-0.34, 1.18), 0.55 (-0.02, 1.13) Index Placebo 0.27 (3.15) 0.35 (4.21) P = 0.281 P = 0.058 Mean (standard deviation; SD) changes from baseline at Visits 3 and 7, with estimates of short-term treatment effect (linear regression model, adjusted for baseline value and age) and long-term treatment effect (mixed effects regression model, adjusted for baseline value, age and visit; global treatment effect reported) *Global treatment effect is estimated using a mixed-effect model for repeated measures and takes into account the treatment effect difference over the 26-weeks (at Visits 3, 4, 5, 6 and 7). † Regression models for PSQI Component 6 not fitted due to lack of variability in the data. ‡ Data shown are for values recorded at each visit, and regression models do not include baseline adjustment, since CGI-I at baseline not defined.

### melatonin-primary-insomnia-sol — PMID 33157425

#### E0341 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/15/abstract. Class: PSG; overnight polysomnography. Binding: **PRIMARY_REPORT**.

Population: Full trial: middle-aged primary insomnia; randomized 51/46. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: The aim of this study was to determine the efficacy of exogenous melatonin supplementation for sleep disturbances in patients with middle-aged primary insomnia. METHODS: This is a randomized double-blind, placebo-controlled parallel study. Participants were recruited from Tianlin community, Xuhui district, Shanghai. Ninety-seven consecutive middle-aged patients with primary insomnia were randomized to receive 3 mg fast-release melatonin (n = 51) or placebo (n = 46) for four-weeks. Objective sleep parameters tested by overnight polysomnography, subjective sleep performance and daytime somnolence obtained from the Pittsburgh Sleep Quality Index (PSQI), Insomnia Severity Index (ISI) and Epworth Sleepiness Scale (ESS) were obtained at baseline and after treatment. Treatment was taken daily 1 h before bedtime. Serious adverse events and side-effects were monitored. RESULTS: Melatonin supplementation significantly decreased early wake time [-30.63min (95% CI, -53.92 to -7.34); P = 0.001] and percentage of N2 sleep [-7.07% (95% CI, -13.47% to -0.68%); P = 0.031]. However, melatonin had no significant effect on other objective sleep parameters including sleep latency, sleep efficiency, wake during the sleep and percent of N1, N3 and REM sleep. Melatonin had no effect on insomnia symptoms and severity on the PSQI [1.53(95% CI, -0.55 to 3.61); p = 0.504]; ISI [0.81 (95% CI, -2.27 to 3.88); p = 0.165] and ESS [-0.83 (95% CI, -3.53 to 1.88); p = 0.147]. No serious adverse events were reported. CONCLUSIONS: Melatonin supplementation over a four-week period is effective and safe in improving some aspects of objective sleep quality such as total sleep time, percentage of rapid eye movement and early morning wake time in middle-aged patients with insomnia. TRIAL REGISTRATION: Identifier: ChiCTR-TRC-13003997; Prospectively registered on 2 December 2013.

#### E0342 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[41]. Class: ACTIGRAPHY; actigraphy in misassociated ARE/MLT study. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effect of Interventions on Sleep Onset Latency, Total Sleep Time, WASO, and Time in Bed Actigraphy assessments revealed significant improvements from baseline for all sleep parameters in the active treatment groups compared with placebo, as shown in  Table 2  and  Figure 2 .

#### E0343 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[42]. Class: ACTIGRAPHY; actigraphy in misassociated ARE/MLT study. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Sleep Onset Latency (SOL): At week four, SOL decreased significantly in all active groups: ARE −8.9 ± 2.8 min, MLT −10.1 ± 5.2 min, ARE–MLT −14.6 ± 4.3 min, vs.

#### E0344 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[50]. Class: NOT_STATED; NOT_STATED. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Wake After Sleep Onset (WASO): Week 4 reductions were ARE −4.0 ± 1.1 min, MLT −4.9 ± 4.1 min, ARE–MLT −6.9 ± 5.0 min, PLB −2.6 ± 1.4 min; ANOVA F (3, 184) = 13.74,  p  < 0.0001.

#### E0345 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[56]. Class: ACTIGRAPHY; actigraphy in misassociated ARE/MLT study. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effect sizes (partial η 2 ) for week 8 improvements were large across all sleep log parameters: SOL = 0.61, TST = 0.61, WASO = 0.29, TIB = 0.44, respectively.

#### E0346 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[58]. Class: DIARY; sleep diary / patient log. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Effect on Sleep Log Parameters The effects of all the Sleep Log Parameters are depicted in  Table 3  and  Figure 3 .

#### E0347 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[114]. Class: NOT_STATED; NOT_STATED. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> While melatonin alone is effective in sleep onset, its combination with ARE provides a broader spectrum of benefits, including enhanced sleep maintenance, efficiency, and reduced anxiety, supporting clinical use of this dual approach [ 25 , 26 , 27 ].

#### E0348 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[148]. Class: ACTIGRAPHY; actigraphy in misassociated ARE/MLT study. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The sample size was based on changes in sleep onset latency (SOL) reported in a 5-week randomized, placebo-controlled study of melatonin (5 mg/day) by Smits M.G. et al. (2016) [ 26 ], which reported mean (SD) SOL changes of 28.4 (30.15) for melatonin and 12.1 (32.8) for placebo.

#### E0349 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[161]. Class: NOT_STATED; NOT_STATED. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Eligible participants reported difficulty falling asleep (sleep latency > 30 min), a total sleep time of ≤6.5 h per night (at least three nights per week) and associated daytime complaints.

#### E0350 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/33157425#sentence-window[182]. Class: ACTIGRAPHY; actigraphy in misassociated ARE/MLT study. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Study Outcomes The primary outcome was the change in sleep onset latency (SOL) from baseline to week 8, measured by actigraphy.

### melatonin-primary-insomnia-sol — PMID 22346363

#### E0351 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/37/abstract. Class: DIARY; daily sleep diary. Binding: **PRIMARY_REPORT**.

Population: Post hoc antihypertensive-treated subgroup, age >=55, pooled reports; not an independent new RCT. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Add-on prolonged-release melatonin (PRM) in antihypertensive therapy has been shown to ameliorate nocturnal hypertension. Hypertension is a major comorbidity among insomnia patients. The efficacy and safety of PRM for primary insomnia in patients aged 55 years and older who are treated with antihypertensive drugs were evaluated. METHODS: Post hoc analysis of pooled antihypertensive drug-treated subpopulations from four randomized, double-blind trials of PRM and placebo for 3 weeks (N[PRM] = 195; N[placebo] = 197) or 28 weeks (N[PRM] = 157; N[placebo] = 40). Efficacy measurements included Leeds Sleep Evaluation Questionnaire scores of quality of sleep and alertness and behavioral integrity the following morning after 3 weeks, and sleep latency (daily sleep diary) and Clinical Global Impression of Improvement (CGI-I) after 6 months of treatment. Safety measures included antihypertensive drug-treated subpopulations from these four and three additional single-blind and open-label PRM studies of up to 1 year (N[PRM] = 650; N[placebo] = 632). RESULTS: Quality of sleep and behavior following wakening improved significantly with PRM compared with placebo (P < 0.0001 and P < 0.0008, respectively). Sleep latency (P = 0.02) and CGI-I (P = 0.0003) also improved significantly. No differences were observed between PRM and placebo groups in vital signs, including daytime blood pressure at baseline and treatment phases. The rate of adverse events normalized per 100 patient-weeks was lower for PRM (3.66) than for placebo (8.53). CONCLUSIONS: The findings demonstrate substantive and sustained efficacy of PRM in primary insomnia patients treated with antihypertensive drugs. PRM appears to be safe for insomnia in patients with cardiovascular comorbidity.

#### E0352 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[1]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Post hoc analysis of pooled antihypertensive drug-treated subpopulations from four randomized, double-blind trials of PRM and placebo for 3 weeks (N[PRM] = 195; N[placebo] = 197) or 28 weeks (N[PRM] = 157; N[placebo] = 40). Efficacy measurements included Leeds Sleep Evaluation Questionnaire scores of quality of sleep and alertness and behavioral integrity the following morning after 3 weeks, and sleep latency (daily sleep diary) and Clinical Global Impression of Improvement (CGI-I) after 6 months of treatment. Safety measures included antihypertensive drug-treated subpopulations from these four and three additional single-blind and open-label PRM studies of up to 1 year (N[PRM] = 650; N[placebo] = 632).

#### E0353 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[2]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Quality of sleep and behavior following wakening improved significantly with PRM compared with placebo ( P < 0.0001 and P < 0.0008, respectively). Sleep latency ( P = 0.02) and CGI-I ( P = 0.0003) also improved significantly. No differences were observed between PRM and placebo groups in vital signs, including daytime blood pressure at baseline and treatment phases. The rate of adverse events normalized per 100 patient-weeks was lower for PRM (3.66) than for placebo (8.53).

#### E0354 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[5]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> PRM (Circadin ® , Rad Neurim Pharmaceuticals EEC Ltd, Reading, UK) is a new drug licensed to treat primary insomnia in patients aged 55 years and older. It is designed to mimic the release pattern of endogenous melatonin, a hormone that regulates sleep and circadian rhythms. 17 There is an age-related decline in the robustness of the biological clock and melatonin production, thus depriving the brain of an important sleep regulator. 18 – 21 In patients aged 55 years and over who suffer from poor sleep quality, melatonin production is even lower than in healthy elderly without such a complaint. 22 , 23 PRM (2 mg) has been shown to be effective in improving the patient-reported quality of sleep and morning alertness as well as sleep latency in insomnia patients. 24 – 28 It was thus pertinent to check whether add-on of PRM improves quality of sleep, sleep latency, and next-day alertness in patients aged 55 and older with primary insomnia who are treated with antihypertensive drugs. The safety of PRM in this population was also of interest because of potential drug interactions with medications used for the treatment of CVD, including hypertension.

#### E0355 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[11]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The primary efficacy measures in the short-term (3 weeks) studies were the improvements in quality of sleep and morning alertness as assessed by the Leeds Sleep Evaluation Questionnaire (LSEQ). The LSEQ is a widely used standardized instrument for the measurement of sleep difficulties in clinical settings. 29 It is a retrospective instrument by which the patients are asked to contrast aspects of their current sleep with those at the time before they joined the study. The LSEQ comprises ten individual visual analog scales (100 millimeters) shown by factor analysis to assess four discrete domains that are used independently to assess the following aspects of sleep and daytime behavior: getting to sleep, quality of sleep (QOS), awakening from sleep, and behavior following wakening (BFW). 30 , 31 The QOS domain is the mean of Questions 4 and 5, which relate to the question “How would you describe the quality of your sleep compared with normal sleep?”. Alertness and behavioral integrity the following morning (BFW) is the mean of Questions 8, 9, and 10 (“How do you feel when you wake up?, How do you feel now?, How would you describe your balance and coordination upon awakening?”). The LSEQ is used in a repetitive manner, yielding a series of measurements, and the difference between current and preceding measurements is used in drug efficacy evaluations. 29 Patients were asked to fill in the LSEQ 2 hours after awakening and to evaluate their quality of sleep and morning behaviors as compared with the respective values before starting run-in. Patients in all four studies completed the LSEQ during the last 3 days of the run-in period (baseline measurement) and the last 3 days of the 3-week treatment period. The changes in each parameter averaged over three consecutive days from run-in placebo (baseline) to end of the 3-week treatment were calculated for each patient. In the long-term study, 27 patients completed a daily sleep diary. The main efficacy parameter in this study was the patient-reported time taken to fall asleep (sleep latency) measured over the last 7 days of baseline and treatment period. The global improvement in patients’ health status, assessed in each patient using Clinical Global Impression of Improvement (CGI-I), 32 is also presented as a measure of overall benefit to the patients. The CGI rating scales are commonly used measures of symptom severity, treatment response, and efficacy of treatments. This is a validated subjective scale that requires the user of the scale to compare the subjects with typical patients in the clinician experience. The CGI-I is a seven-point scale that requires the clinician to assess how much the patient’s illness has improved or worsened relative to a baseline state at the beginning of the intervention and can be rated as 1, very much improved; 2, much improved; 3, minimally improved; 4, no change; 5, minimally worse; 6, much worse; or 7, very much worse.

#### E0356 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[16]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> By the end of the 6-month treatment period, the mean improvement (decrease) in patients’ evaluated sleep latency (reported in the daily sleep diary) was significantly higher with PRM (25.89 minutes) than with placebo (7.54 minutes) (df = 1; F = 8.74; P = 0.02, ANCOVA) ( Table 3 ). The Cohen’s d effect size was 0.39.

#### E0357 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[21]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The results of the current post hoc analysis using the primary efficacy endpoints from the individual studies demonstrate that in insomnia patients aged 55 years and older with a history of hypertension and concomitant treatment with antihypertensive drugs, treatment with PRM improves sleep quality and next-day alertness significantly more than placebo. Long-term benefit to these patients was also demonstrated by the significantly greater improvements in sleep latency treated for 6 months with PRM compared with placebo. The effect size of ~0.35 obtained with PRM in these three sleep variables in comparison with placebo is considered medium, 33 quite comparable with those of hypnotics, 34 and well within the range of effect sizes found with central nervous system drugs, 35 , 36 and is therefore of clear clinical relevance. Benefit to patients is confirmed by the higher percentage of patients who improved or very much improved in CGI-I with PRM compared with placebo following 6 months of treatment. The safety profile of PRM in this population is benign compared with placebo. This implies that add-on PRM therapy does not present significant risks of detrimental drug interactions with the main drugs used to treat CVD, including hypertension, for long-term periods.

#### E0358 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#p[31]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Efficacy of prolonged-release melatonin (PRM) compared with placebo (6 months): improvement in sleep latency (daily sleep diary)

#### E0359 — fulltext_table

Source: cache/melatonin-primary-insomnia-sol/ft_22346363.txt#table-wrap[@id=t3-ibpc-5-009]. Class: DIARY; sleep diary / patient log. Binding: **TARGET_ROWS_PLUS_TABLE_CONTEXT**.

Population: Post hoc antihypertensive-treated subgroup, age >=55, pooled reports; not an independent new RCT. Raw/adjusted: MIXED: arm mean/SD raw; treatment effects model-adjusted; medians/ranges retained. n: "See N/N MAX rows; maximum is not outcome-specific n".

> Table 3 Efficacy of prolonged-release melatonin (PRM) compared with placebo (6 months): improvement in sleep latency (daily sleep diary) Daily sleep diary score PRM Placebo N Mean length of time (minutes) SD N Mean length of time (minutes) SD Baseline 134 73.6 5.6 39 73.5 4.3 6 months 121 51.0 3.6 36 65.2 4.4 Mean change from baseline 121 −23.3 2.9 36 −7.5 3.6 Significance for PRM vs placebo P = 0.02 Abbreviations: PRM, prolonged-release melatonin; SD, standard deviation.

#### E0360 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/22346363#sentence-window[14]. Class: NOT_STATED; NOT_STATED. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 22 , 23  PRM (2 mg) has been shown to be effective in improving the patient-reported quality of sleep and morning alertness as well as sleep latency in insomnia patients.

#### E0361 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/22346363#sentence-window[15]. Class: NOT_STATED; NOT_STATED. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 24 – 28  It was thus pertinent to check whether add-on of PRM improves quality of sleep, sleep latency, and next-day alertness in patients aged 55 and older with primary insomnia who are treated with antihypertensive drugs.

#### E0362 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/22346363#sentence-window[52]. Class: NOT_STATED; NOT_STATED. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The main efficacy parameter in this study was the patient-reported time taken to fall asleep (sleep latency) measured over the last 7 days of baseline and treatment period.

#### E0363 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/22346363#sentence-window[76]. Class: DIARY; sleep diary / patient log. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> By the end of the 6-month treatment period, the mean improvement (decrease) in patients’ evaluated sleep latency (reported in the daily sleep diary) was significantly higher with PRM (25.89 minutes) than with placebo (7.54 minutes) (df = 1;  F  = 8.74;  P  = 0.02, ANCOVA) ( Table 3 ).

#### E0364 — embedded_fulltext_window

Source: cache/melatonin-primary-insomnia-sol/records.json#/fulltext_by_pmid/22346363#sentence-window[90]. Class: NOT_STATED; NOT_STATED. Binding: **MATCHED_PRIMARY_TEXT**.

Population: As stated in quote; do not generalize pooled/subgroup data. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Long-term benefit to these patients was also demonstrated by the significantly greater improvements in sleep latency treated for 6 months with PRM compared with placebo.

### melatonin-primary-insomnia-sol — PMID 27559258

#### E0365 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/80/abstract. Class: QUESTIONNAIRE; Athens Insomnia Scale (AIS), aggregate; no isolated SOL result. Binding: **PRIMARY_REPORT**.

Population: Cancer patients with insomnia, age 20-65; 50 randomized, 48 completed. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: The natural hormone melatonin has sleep inducing properties. Insomnia in cancer patients is common. So far, melatonin has been seldom tried for the improvement of sleep in patients with malignancies. Keeping this in mind, we planned and conducted a double-blind study to test the efficacy of melatonin in promoting sleep in patients with malignancies suffering from insomnia. OBJECTIVE: To assess the hypnotic efficacy of oral melatonin in cancer patients with insomnia. MATERIALS AND METHODS: After Ethical Committee approval, 50 patients (age range 20-65 years) from our pain clinic NIVARANE who met the Diagnostic and Statistical Manual of Mental Disorders 4(th) edition criteria for primary insomnia were randomized to receive melatonin 3 mg or placebo at 7 pm orally every day for 14 days from our pharmacist. After 1, 7, 14 days, the patients were reviewed with the Athens insomnia scale oral questionnaire to document the subjective sleep quality. The patients and we, the investigators were blinded to the study drug. RESULTS: There were 2 drop outs (one from each group) as they failed to complete visit on day 14. Significant differences in favor of melatonin treatment were found in clinically relevant improvements in insomnia (46.53%; P = 0.00001 vs. 11.30%; P = 0.1026) There was improvement in sleep from 1 to 7 days (19.91%; P = 0.00001 vs. 0.98%; P = 0.2563). More significant improvements were seen between 7 and 14 days (33.24%; P = 0.00001 vs. 10.42%; P = 0.1469). CONCLUSION: We conclude that daily intake of oral melatonin 2 h before bedtime improves sleep induction and quality in cancer patients with insomnia.

#### E0366 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_27559258.txt#p[4]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> We conclude that daily intake of oral melatonin 2 h before bedtime improves sleep induction and quality in cancer patients with insomnia.

#### E0367 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_27559258.txt#p[15]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The AIS is a self-assessment psychometric instrument designed for quantifying sleep difficulty. It consists of 8 items: The first 5 pertain to sleep induction, awakenings during the night, final awakening, total sleep duration, and sleep quality; while the last 3 refer to well-being, functioning capacity, and sleepiness during the day. The items are measured on 0-3 numeric rating scales. Patients are asked to rate the severity of their insomnia at 0 being “no problem” and 3 being “did not sleep at all.”[ 12 ]

#### E0368 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_27559258.txt#p[35]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Our study results agree with the results of the studies done by Wade et al .,[ 14 ] Haimov et al .,[ 25 ] who administered oral melatonin in elderly insomniacs and observed significant and clinically meaningful improvements in sleep quality, morning alertness, sleep onset latency and quality of life. However, these studies[ 14 25 ] used prolonged release formulations. We administered single dose tablet formulations of melatonin. A meta-analysis done by Ferracioli-Oda et al .[ 26 ] concluded with the same observations along with additional information viz- the effects of melatonin on sleep are modest but do not appear to dissipate with continued melatonin use. Our study did not agree with the results obtained by Almeida Montes et al .[ 10 ] who concluded that melatonin did not produce any sleep benefit in elderly insomniacs. It may be because the doses they used were 0.3 mg and 1 mg which were less compared to our study dose.

#### E0369 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_27559258.txt#p[36]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In addition to sleep induction and maintenance, melatonin produces various effects viz- analgesia, anti-inflammatory and immunological effects, anti-oxidative effects, chronobiosis, and antihypertensive effect.[ 22 ] Melatonin lowers the toxicity of chemotherapeutic agents such as cisplatin, etoposide, anthracyclines, and 5-ﬂuorouracil. It reduces the severity of treatment-related adverse events such as myelosuppression, neurotoxicity, nephrotoxicity, and asthenia. It is also effective in the treatment of major depression and has oncostatic properties.[ 6 ] All these properties of melatonin could prove to be beneficial in patients suffering from cancer.

#### E0370 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_27559258.txt#p[38]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Our study had several limitations. These include points like the inclusion of all stages of cancer in the study. In advanced stages of cancer, insomnia could be related to pain caused by tumor invasion like mass impinging on nerve roots. Patients in the early stages of cancer may have increased depression, anxiety, and fatigue levels following the diagnosis of cancer leading to insomnia. Depressive mood is the main factor influencing the quality of life.[ 27 ] The inclusion of patients suffering from a plethora of cancers was another limitation. The insomnia rates have been found to be variable in different cancer types; nevertheless, breast cancer patients are known to have high insomnia rates possibly because of the disruption of sleep due to increased frequency and severity of hot flashes associated with breast cancer treatment.[ 28 ] We could not standardize all these factors in our study. We did not stratify the effects of melatonin on insomnia as improvement in sleep onset and sleep maintenance, but we propose to do this in further studies.

#### E0371 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_27559258.txt#p[42]. Class: NOT_STATED; NOT_STATED. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> We conclude that regular daily intake of oral melatonin 3 mg 2 h before bedtime along with nonpharmacological measures improves sleep induction and the quality of sleep in cancer patients with insomnia.

### melatonin-primary-insomnia-sol — PMID 19584739

#### E0372 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/85/abstract. Class: NOT_STATED; PSG/EEG and questionnaires; 9-minute effect not explicitly assigned. Binding: **PRIMARY_REPORT**.

Population: Full eligible trial, age >=55; N=40. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> Objectives of this study were to investigate the effects of prolonged-release melatonin 2 mg (PRM) on sleep and subsequent daytime psychomotor performance in patients aged > or =55 years with primary insomnia, as defined by fourth revision of the Diagnostic and Statistical Manual of Mental Disorders of the American Psychiatric Association. Patients (N = 40) were treated nightly single-blind with placebo (2 weeks), randomized double-blind to PRM or placebo (3 weeks) followed by withdrawal period (3 weeks). Sleep was assessed by polysomnography, all-night sleep electroencephalography spectral analysis and questionnaires. Psychomotor performance was assessed by the Leeds Psychomotor Test battery. By the end of the double-blind treatment, the PRM group had significantly shorter sleep onset latency (9 min; P = 0.02) compared with the placebo group and scored significantly better in the Critical Flicker Fusion Test (P = 0.008) without negatively affecting sleep structure and architecture. Half of the patients reported substantial improvement in sleep quality at home with PRM compared with 15% with placebo (P = 0.018). No rebound effects were observed during withdrawal. In conclusion, nightly treatment with PRM effectively induced sleep and improved perceived quality of sleep in patients with primary insomnia aged > or =55 years. Daytime psychomotor performance was not impaired and was consistently better with PRM compared with placebo. PRM was well tolerated with no evidence of rebound effects.

### melatonin-primary-insomnia-sol — PMID 18036082

#### E0373 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/86/abstract. Class: NOT_STATED; No SOL result; LSEQ measures quality/alertness. Binding: **PRIMARY_REPORT**.

Population: Full eligible trial, age >=55; N=170; severity subgroup mentioned. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> Melatonin, secreted nocturnally by the pineal gland, is an endogenous sleep regulator. Impaired melatonin production and complaints on poor quality of sleep are common among the elderly. Non-restorative sleep (perceived poor quality of sleep) and subsequently poor daytime functioning are increasingly recognized as a leading syndrome in the diagnostic and therapeutic process of insomnia complaints. The effects of 3-weeks prolonged-release melatonin 2 mg (PR-melatonin) versus placebo treatment were assessed in a multi-center randomized placebo-controlled study in 170 primary insomnia outpatients aged > or =55 years. Improvements in quality of sleep (QOS) the night before and morning alertness (BFW) were assessed using the Leeds Sleep Evaluation Questionnaire and changes in sleep quality (QON) reported on five categorical unit scales. Rebound insomnia and withdrawal effects following discontinuation were also evaluated. PR-melatonin significantly improved QOS (-22.5 versus -16.5 mm, P = 0.047), QON (0.89 versus 0.46 units; P = 0.003) and BFW (-15.7 versus -6.8 mm; P = 0.002) compared with placebo. The improvements in QOS and BFW were strongly correlated (Rval = 0.77, P < 0.001) suggesting a beneficial treatment effect on the restorative value of sleep. These results were confirmed in a subgroup of patients with a greater symptom severity. There was no evidence of rebound insomnia or withdrawal effects following treatment discontinuation. The incidence of adverse events was low and most side-effects were judged to be of minor severity. PR-melatonin is the first drug shown to significantly improve quality of sleep and morning alertness in primary insomnia patients aged 55 years and older-suggesting more restorative sleep, and without withdrawal symptoms upon discontinuation.

### melatonin-primary-insomnia-sol — PMID 17875243

#### E0374 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/87/abstract. Class: NOT_STATED; PSQI, LSEQ and diary; -24.3/-12.9 not explicitly assigned. Binding: **PRIMARY_REPORT**.

Population: Full eligible trial, age 55-80; randomized 177/177; completers 169/165. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: Melatonin, the hormone produced nocturnally by the pineal gland, serves as a circadian time cue and sleep-anticipating signal in humans. With age, melatonin production declines and the prevalence of sleep disorders, particularly insomnia, increases. The efficacy and safety of a prolonged release melatonin formulation (PR-melatonin; Circadin* 2 mg) were examined in insomnia patients aged 55 years and older. DESIGN: Randomised, double blind, placebo-controlled. SETTING: Primary care. METHODOLOGY: From 1248 patients pre-screened and 523 attending visit 1, 354 males and females aged 55-80 years were admitted to the study, 177 to active medication and 177 to placebo. The study was conducted by primary care physicians in the West of Scotland and consisted of a 2-week, single blind, placebo run-in period followed by a 3-week double blind treatment period with PR-melatonin or placebo, one tablet per day at 2 hours before bedtime. MAIN OUTCOME MEASURES: Responder rate (concomitant improvement in sleep quality and morning alertness on Leeds Sleep Evaluation Questionnaire [LSEQ]), other LSEQ assessments, Pittsburgh Sleep Quality Index (PSQI) global score, other PSQI assessments, Quality of Night and Quality of Day derived from a diary, Clinical Global Improvement scale (CGI) score and quality of life (WHO-5 well being index). RESULTS: Of the 354 patients entering the active phase of the study, 20 failed to complete visit 3 (eight PR-melatonin; 12 Placebo). The principal reasons for drop-out were patient decision and lost to follow-up. Significant differences in favour of PR-melatonin vs. placebo treatment were found in concomitant and clinically relevant improvements in quality of sleep and morning alertness, demonstrated by responder analysis (26% vs. 15%; p = 0.014) as well as on each of these parameters separately. A significant and clinically relevant shortening of sleep latency to the same extent as most frequently used sleep medications was also found (-24.3 vs.-12.9 minutes; p = 0.028). Quality of life also improved significantly (p = 0.034). CONCLUSIONS: PR-melatonin results in significant and clinically meaningful improvements in sleep quality, morning alertness, sleep onset latency and quality of life in primary insomnia patients aged 55 years and over. TRIAL REGISTRATION: The trial was conducted prior to registration being introduced.

### melatonin-primary-insomnia-sol — PMID 12790159

#### E0375 — abstract

Source: cache/melatonin-primary-insomnia-sol/records.json#/records/89/abstract. Class: NOT_STATED; EEG and logs; no numeric SOL result. Binding: **PRIMARY_REPORT**.

Population: Full crossover sample, N=10; age 30-72, mean 50; each receives placebo, 0.3 mg and 1 mg. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> OBJECTIVE: To assess the hypnotic effect of melatonin in patients with primary insomnia. METHOD: Ten patients (mean age 50 yr, range 30-72 yr) who met the DSM-IV criteria for primary insomnia received, in random order, 0.3 mg of melatonin, 1.0 mg of melatonin or placebo 60 minutes before bedtime. A crossover design was used so that each patient received each of the 3 treatments for a 7-day period (with a 5-day washout period between). After each 7-day treatment, night time electroencephalographic (EEG) records were collected, and each morning, subjects completed sleep logs and analogue-visual scales to document the amount and subjective quality of sleep. RESULTS: There were no significant differences in sleep EEG, the amount or subjective quality of sleep or side effects between the placebo, 0.3-mg melatonin or 1.0-mg melatonin treatments. CONCLUSION: Melatonin did not produce any sleep benefit in this sample of patients with primary insomnia.

#### E0376 — fulltext_paragraph

Source: cache/melatonin-primary-insomnia-sol/ft_12790159.txt#p[1]. Class: DIARY; sleep diary / patient log. Binding: **CONTEXT_QUOTE_NOT_ALL_NUMBERS_ARE_TRIAL_RESULTS**.

Population: As explicitly stated in quote; no full-population substitution. Raw/adjusted: As explicitly stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Ten patients (mean age 50 yr, range 30–72 yr) who met the DSM-IV criteria for primary insomnia received, in random order, 0.3 mg of melatonin, 1.0 mg of melatonin or placebo 60 minutes before bedtime. A crossover design was used so that each patient received each of the 3 treatments for a 7-day period (with a 5-day washout period between). After each 7-day treatment, night time electroencephalographic (EEG) records were collected, and each morning, subjects completed sleep logs and analogue-visual scales to document the amount and subjective quality of sleep.

### semaglutide-obesity-weight — PMID 33625476

Pinned served row:
~~~json
{
  "id": "PMID 33625476",
  "mean1": -16.5,
  "sd1": 10.1,
  "nc1": 407,
  "mean2": -5.8,
  "sd2": 7.7,
  "nc2": 204,
  "source": "ClinicalTrials.gov results (structured, continuous): outcome 'Change in Body Weight (%)' mean -16.5 (SD 10.1, n=407) [Semaglutide 2.4 mg] vs -5.8 (SD 7.7, n=204) [Placebo] Percentage — population: Overall number of participants analyzed = full analysis set (FAS) which comprise",
  "timeframe": "Baseline (week 0) to week 68"
}
~~~

#### E0377 — abstract

Source: cache/semaglutide-obesity-weight/records.json#/records/117/abstract. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **PRIMARY_REPORT**.

Population: in-trial / treatment-policy estimand (all randomized), baseline to Week 68. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> IMPORTANCE: Weight loss improves cardiometabolic risk factors in people with overweight or obesity. Intensive lifestyle intervention and pharmacotherapy are the most effective noninvasive weight loss approaches. OBJECTIVE: To compare the effects of once-weekly subcutaneous semaglutide, 2.4 mg vs placebo for weight management as an adjunct to intensive behavioral therapy with initial low-calorie diet in adults with overweight or obesity. DESIGN, SETTING, AND PARTICIPANTS: Randomized, double-blind, parallel-group, 68-week, phase 3a study (STEP 3) conducted at 41 sites in the US from August 2018 to April 2020 in adults without diabetes (N = 611) and with either overweight (body mass index ≥27) plus at least 1 comorbidity or obesity (body mass index ≥30). INTERVENTIONS: Participants were randomized (2:1) to semaglutide, 2.4 mg (n = 407) or placebo (n = 204), both combined with a low-calorie diet for the first 8 weeks and intensive behavioral therapy (ie, 30 counseling visits) during 68 weeks. MAIN OUTCOMES AND MEASURES: The co-primary end points were percentage change in body weight and the loss of 5% or more of baseline weight by week 68. Confirmatory secondary end points included losses of at least 10% or 15% of baseline weight. RESULTS: Of 611 randomized participants (495 women [81.0%], mean age 46 years [SD, 13], body weight 105.8 kg [SD, 22.9], and body mass index 38.0 [SD, 6.7]), 567 (92.8%) completed the trial, and 505 (82.7%) were receiving treatment at trial end. At week 68, the estimated mean body weight change from baseline was -16.0% for semaglutide vs -5.7% for placebo (difference, -10.3 percentage points [95% CI, -12.0 to -8.6]; P < .001). More participants treated with semaglutide vs placebo lost at least 5% of baseline body weight (86.6% vs 47.6%, respectively; P < .001). A higher proportion of participants in the semaglutide vs placebo group achieved weight losses of at least 10% or 15% (75.3% vs 27.0% and 55.8% vs 13.2%, respectively; P < .001). Gastrointestinal adverse events were more frequent with semaglutide (82.8%) vs placebo (63.2%). Treatment was discontinued owing to these events in 3.4% of semaglutide participants vs 0% of placebo participants. CONCLUSIONS AND RELEVANCE: Among adults with overweight or obesity, once-weekly subcutaneous semaglutide compared with placebo, used as an adjunct to intensive behavioral therapy and initial low-calorie diet, resulted in significantly greater weight loss during 68 weeks. Further research is needed to assess the durability of these findings. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT03611582.

#### E0378 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "373".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG000", "value": "-16.5", "spread": "10.1"}

#### E0379 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "189".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG001", "value": "-5.8", "spread": "7.7"}

#### E0380 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/1/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "334".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG000", "value": "-17.6", "spread": "9.6"}

#### E0381 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/1/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "164".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG001", "value": "-6.1", "spread": "7.6"}

#### E0382 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/analyses/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Treatment policy estimand. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-10.27", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-11.97", "ciUpperLimit": "-8.57"}

#### E0383 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/analyses/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Hypothetical estimand. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Hypothetical estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "MMRM (mixed model repeated measurement)", "paramType": "Treatment difference", "paramValue": "-12.67", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-14.34", "ciUpperLimit": "-11.00"}

#### E0384 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/8/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "373".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomisation (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG000", "value": "-17.5", "spread": "11.4"}

#### E0385 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/8/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "189".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomisation (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG001", "value": "-6.2", "spread": "8.6"}

#### E0386 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/24/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "396".

Class evidence:
> Change in body weight from baseline (week 0) to week 8 is presented. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomisation (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG000", "value": "-7.8", "spread": "3.1"}

#### E0387 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/24/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "197".

Class evidence:
> Change in body weight from baseline (week 0) to week 8 is presented. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomisation (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG001", "value": "-6.0", "spread": "3.6"}

### semaglutide-obesity-weight — PMID 33567185

Pinned served row:
~~~json
{
  "id": "PMID 33567185",
  "mean1": -15.6,
  "sd1": 10.1,
  "nc1": 1306,
  "mean2": -2.8,
  "sd2": 6.5,
  "nc2": 655,
  "source": "ClinicalTrials.gov results (structured, continuous): outcome 'Change in Body Weight (%)' mean -15.6 (SD 10.1, n=1306) [Semaglutide 2.4 mg] vs -2.8 (SD 6.5, n=655) [Placebo] Percentage point — population: Overall number of participants analyzed = full analysis set (FAS) which comprise",
  "timeframe": "Baseline (week 0) to week 68"
}
~~~

#### E0388 — abstract

Source: cache/semaglutide-obesity-weight/records.json#/records/118/abstract. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **PRIMARY_REPORT**.

Population: in-trial / treatment-policy estimand (all randomized), baseline to Week 68. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Obesity is a global health challenge with few pharmacologic options. Whether adults with obesity can achieve weight loss with once-weekly semaglutide at a dose of 2.4 mg as an adjunct to lifestyle intervention has not been confirmed. METHODS: In this double-blind trial, we enrolled 1961 adults with a body-mass index (the weight in kilograms divided by the square of the height in meters) of 30 or greater (≥27 in persons with ≥1 weight-related coexisting condition), who did not have diabetes, and randomly assigned them, in a 2:1 ratio, to 68 weeks of treatment with once-weekly subcutaneous semaglutide (at a dose of 2.4 mg) or placebo, plus lifestyle intervention. The coprimary end points were the percentage change in body weight and weight reduction of at least 5%. The primary estimand (a precise description of the treatment effect reflecting the objective of the clinical trial) assessed effects regardless of treatment discontinuation or rescue interventions. RESULTS: The mean change in body weight from baseline to week 68 was -14.9% in the semaglutide group as compared with -2.4% with placebo, for an estimated treatment difference of -12.4 percentage points (95% confidence interval [CI], -13.4 to -11.5; P<0.001). More participants in the semaglutide group than in the placebo group achieved weight reductions of 5% or more (1047 participants [86.4%] vs. 182 [31.5%]), 10% or more (838 [69.1%] vs. 69 [12.0%]), and 15% or more (612 [50.5%] vs. 28 [4.9%]) at week 68 (P<0.001 for all three comparisons of odds). The change in body weight from baseline to week 68 was -15.3 kg in the semaglutide group as compared with -2.6 kg in the placebo group (estimated treatment difference, -12.7 kg; 95% CI, -13.7 to -11.7). Participants who received semaglutide had a greater improvement with respect to cardiometabolic risk factors and a greater increase in participant-reported physical functioning from baseline than those who received placebo. Nausea and diarrhea were the most common adverse events with semaglutide; they were typically transient and mild-to-moderate in severity and subsided with time. More participants in the semaglutide group than in the placebo group discontinued treatment owing to gastrointestinal events (59 [4.5%] vs. 5 [0.8%]). CONCLUSIONS: In participants with overweight or obesity, 2.4 mg of semaglutide once weekly plus lifestyle intervention was associated with sustained, clinically relevant reduction in body weight. (Funded by Novo Nordisk; STEP 1 ClinicalTrials.gov number, NCT03548935).

#### E0389 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "1212".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG000", "value": "-15.6", "spread": "10.1"}

#### E0390 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; In-trial observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "577".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG001", "value": "-2.8", "spread": "6.5"}

#### E0391 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/1/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "1059".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG000", "value": "-16.9", "spread": "9.4"}

#### E0392 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/1/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; On-treatment observation period; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "499".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupId": "OG001", "value": "-3.1", "spread": "6.4"}

#### E0393 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/analyses/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Treatment policy estimand. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-12.44", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-13.37", "ciUpperLimit": "-11.51"}

#### E0394 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/analyses/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.; Hypothetical estimand. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period). Treatment policy estimand Hypothetical estimand

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Hypothetical estimand", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-14.42", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-15.29", "ciUpperLimit": "-13.55"}

#### E0395 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/9/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "1212".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomization (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG000", "value": "-16.1", "spread": "10.6"}

#### E0396 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/9/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "577".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomization (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG001", "value": "-2.9", "spread": "7.2"}

#### E0397 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/32/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "89".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented in DEXA subpopulation. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomization (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG000", "value": "-15.8", "spread": "11.1"}

#### E0398 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/32/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "42".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented in DEXA subpopulation. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomization (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG001", "value": "-3.4", "spread": "6.1"}

#### E0399 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/33/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "89".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented in DEXA subpopulation. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomization (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG000", "value": "-15.5", "spread": "11.4"}

#### E0400 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/33/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: DEXA analysis set (DXA) includes participants in the sub-population of FAS that have had a DEXA scan performed at baseline. 'Overall Number of Participants Analyzed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "42".

Class evidence:
> Change in body weight from baseline (week 0) to week 68 is presented in DEXA subpopulation. The endpoint was evaluated based on the data from in-trial observation period. In-trial observation period: the uninterrupted time interval from start of randomization (week 0) to last trial-related subject-site contact (week 75). 

> {"groupId": "OG001", "value": "-3.2", "spread": "6.1"}

### semaglutide-obesity-weight — PMID 42070571

#### E0401 — abstract

Source: cache/semaglutide-obesity-weight/records.json#/records/11/abstract. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **PRIMARY_REPORT**.

Population: in-trial / treatment-policy estimand (all randomized), baseline to Week 68. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Alcohol use disorder accounts for 5% of deaths worldwide annually, and there is an urgent need for new therapeutic interventions. Preclinical and initial human studies indicate that the GLP-1 receptor agonist semaglutide might reduce alcohol drinking. This study evaluated the efficacy of semaglutide once-weekly in treatment-seeking patients with alcohol use disorder and comorbid obesity. METHODS: In a 26-week, single-centre, randomised, double-blinded, placebo-controlled trial, treatment-seeking participants with moderate to severe alcohol use disorder and comorbid obesity were assigned (1:1) to receive once-weekly semaglutide (2·4 mg subcutaneously) or placebo (saline subcutaneously), in addition to standard cognitive behavioural therapy. The primary endpoint was a reduction in the number of heavy drinking days assessed after 26 weeks of intervention, analysed with an ANCOVA model. Analysis adhered to the intention-to-treat principle, and missing outcome data were addressed using multiple imputations. Safety was assessed in all treated patients. The trial is registered at ClinicalTrials.govNCT05895643, and is complete. FINDINGS: From June 10, 2023, to Feb 4, 2025, 108 participants (53 women and 55 men) were enrolled, with 54 participants in each of the semaglutide and placebo treatment groups, and all were included in the data analysis. Overall, 88 participants (81%) completed the full intervention. Semaglutide was associated with a reduction in heavy drinking days (-41·1 percentage points from baseline, 95% CI -48·7 to -33·5) compared with placebo (-26·4, -34·1 to -18·6; estimated treatment difference -13·7 percentage points, -22·0 to -5·4; p=0·0015), and had substantial effects on multiple secondary alcohol-related and somatic outcomes. Adverse events were transient, generally mild to moderate gastrointestinal effects, and occurred more frequently in the semaglutide group. INTERPRETATION: Semaglutide showed robust therapeutic effects in treatment-seeking participants with obesity and alcohol use disorder and this trial supports previous preclinical and clinical findings suggesting GLP-1 receptor agonists as a potential novel treatment target for alcohol use disorder. FUNDING: The Research Foundation, Mental Health Services (Capital Region of Denmark), the Novo Nordisk Foundation, the Novavi Foundation, the Hartmann Foundation, and the Augustinus Foundation.

### semaglutide-obesity-weight — NCT07731256

No held abstract, registry result measure or attributable fulltext result for this record. Population, n and method: NOT_STATED. Pinned declared-absent row retained in JSON.

### semaglutide-obesity-weight — NCT06390501

No held abstract, registry result measure or attributable fulltext result for this record. Population, n and method: NOT_STATED. Pinned declared-absent row retained in JSON.

### semaglutide-obesity-weight — PMID 40825340

#### E0402 — abstract

Source: cache/semaglutide-obesity-weight/records.json#/records/32/abstract. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **PRIMARY_REPORT**.

Population: in-trial / treatment-policy estimand (all randomized), baseline to Week 68. Raw/adjusted: Raw/adjusted wording retained per quoted result; otherwise NOT_STATED. n: "NOT_STATED".

> BACKGROUND: Consistent with WHO recommendations, obesity is defined as BMI ≥25 kg/m2 in many Asian populations because of increased health risks at lower BMIs than in other populations. We aimed to investigate the efficacy and safety of once-weekly subcutaneous semaglutide 2·4 mg versus placebo in an Asian population with BMI ≥25 kg/m2, together with lifestyle interventions. METHODS: STEP 11 was a 44-week, randomised, double-blind, placebo-controlled, phase 3 trial conducted at 12 clinical sites in South Korea and Thailand. Adults (aged ≥18 years in Thailand and ≥19 years in South Korea) with obesity (BMI ≥25 kg/m2) of Asian descent, without diabetes, were randomly assigned 2:1 with a computer-generated sequence and block randomisation to once-weekly subcutaneous semaglutide 2·4 mg or placebo, with a reduced-calorie diet and increased physical activity. Participants, care providers, investigators, and assessors were masked to allocation. Coprimary endpoints, measured in all randomly assigned participants by intention to treat, were percentage bodyweight change and the proportion of participants reaching ≥5% bodyweight reduction. Confirmatory secondary endpoints were the proportion of participants with ≥10% and ≥15% bodyweight reductions and change in waist circumference. Safety was assessed via the assessment of adverse events in all participants who received at least one dose of semaglutide or placebo. This trial was registered at ClinicalTrials.gov (NCT04998136). FINDINGS: Between Aug 15, 2022, and Nov 20, 2023, 150 participants were randomly assigned (101 to semaglutide 2·4 mg and 49 to placebo). Six (6%) in the semaglutide group and two (4%) in the placebo group discontinued treatment before week 44. 111 (74%) were female and 39 (26%) male, with a mean age of 39 years (SD 11), mean bodyweight of 83·8 kg (18·1), and mean BMI of 31·3 kg/m2 (5·2). At week 44, mean change in bodyweight was -16·0% (SE 0·7) in the semaglutide 2·4 mg group versus -3·1% (0·9) in the placebo group (p<0·0001), and a greater proportion of participants reached bodyweight reductions of ≥5% (96 [96%] vs 12 [25%]; p<0·0001), ≥10% (78 [78%] vs 5 [10%]; p<0·0001), and ≥15% (53 [53·0%] vs 2 [4·2%]; p<0·0001) in the semaglutide 2·4 mg group. Mean change in waist circumference was -11·9 cm (SE 0·7) with semaglutide versus -3·0 cm (1·0) with placebo (p<0·0001). Adverse events were reported by 90 (89%) of 101 participants in the semaglutide 2·4 mg group and 38 (78%) of 49 participants in the placebo group, with 13 (13%) reporting serious adverse events in the semaglutide 2·4 mg group versus four (8%) in the placebo group. Gastrointestinal adverse events were the most common adverse events in participants in the semaglutide group. INTERPRETATION: In this Asian population with obesity (BMI ≥25·0 kg/m2), once-weekly semaglutide 2·4 mg significantly reduced bodyweight and was well tolerated. The results have meaningful clinical and policy implications for Asian countries, where lower BMI thresholds are used to define obesity compared with other populations. The efficacy and safety of semaglutide 2·4 mg support its inclusion in local treatment guidelines. These findings might also inform reimbursement policies and national obesity strategies, highlighting the importance of population-specific approaches. FUNDING: Novo Nordisk. TRANSLATIONS: For the Thai and Korean translations of the abstract see Supplementary Materials section.

#### E0403 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/0/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "100".

Class evidence:
> Change in percentage (%) of body weight from baseline (week 0) to end of treatment (week 44) is presented in this outcome measure and it was evaluated based on the data from in-trial observation period. For end of treatment visit, data collected up to week 49 during the in-trial observation period is included in this Outcome Measure. In-trial observation period: The time period where the participants were assessed in the study. The in-trial observation period begins on the date of randomization (week 0) and ends at the end of study visit (week 49). Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.

> {"groupId": "OG000", "value": "-16.4", "spread": "7.3"}

#### E0404 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/0/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "48".

Class evidence:
> Change in percentage (%) of body weight from baseline (week 0) to end of treatment (week 44) is presented in this outcome measure and it was evaluated based on the data from in-trial observation period. For end of treatment visit, data collected up to week 49 during the in-trial observation period is included in this Outcome Measure. In-trial observation period: The time period where the participants were assessed in the study. The in-trial observation period begins on the date of randomization (week 0) and ends at the end of study visit (week 49). Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.

> {"groupId": "OG001", "value": "-2.6", "spread": "5.8"}

#### E0405 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/0/analyses/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in percentage (%) of body weight from baseline (week 0) to end of treatment (week 44) is presented in this outcome measure and it was evaluated based on the data from in-trial observation period. For end of treatment visit, data collected up to week 49 during the in-trial observation period is included in this Outcome Measure. In-trial observation period: The time period where the participants were assessed in the study. The in-trial observation period begins on the date of randomization (week 0) and ends at the end of study visit (week 49). Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy Estimand. The primary endpoint was analysed using an analysis of covariance (ANCOVA) model with randomized treatment as factor and baseline body weight as covariate. Analysed data is from in-trial observation period.", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-12.99", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-15.28", "ciUpperLimit": "-10.70"}

#### E0406 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/1/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "96".

Class evidence:
> Change in percentage (%) of body weight from baseline (week 0) to end of treatment (week 44) is presented in this endpoint. The endpoint was evaluated based on the data from on-treatment observation period. On-treatment observation period: The time period where participants were treated with trial product. It started from the date of first trial product administration (week 0) to the date of last trial product administration (week 44) including 2 weeks of follow up. It excludes off treatment period which is defined as at least 2 consecutive missed doses. Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.

> {"groupId": "OG000", "value": "-16.4", "spread": "7.4"}

#### E0407 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/1/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "47".

Class evidence:
> Change in percentage (%) of body weight from baseline (week 0) to end of treatment (week 44) is presented in this endpoint. The endpoint was evaluated based on the data from on-treatment observation period. On-treatment observation period: The time period where participants were treated with trial product. It started from the date of first trial product administration (week 0) to the date of last trial product administration (week 44) including 2 weeks of follow up. It excludes off treatment period which is defined as at least 2 consecutive missed doses. Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.

> {"groupId": "OG001", "value": "-2.7", "spread": "5.8"}

#### E0408 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/1/analyses/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in percentage (%) of body weight from baseline (week 0) to end of treatment (week 44) is presented in this endpoint. The endpoint was evaluated based on the data from on-treatment observation period. On-treatment observation period: The time period where participants were treated with trial product. It started from the date of first trial product administration (week 0) to the date of last trial product administration (week 44) including 2 weeks of follow up. It excludes off treatment period which is defined as at least 2 consecutive missed doses. Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Hypothetical Estimand. The primary endpoint was analysed using mixed model for repeated measurements (MMRM). All responses prior to first discontinuation of treatment (or dose reduction, or initiation of other anti-obesity medication or bariatric surgery) were included in MMRM with randomized treatment as factor and baseline body weight as covariate. Analysed data is from on-treatment observation period.", "nonInferiorityType": "SUPERIORITY", "pValue": "<0.0001", "statisticalMethod": "MMRM", "paramType": "Treatment Difference", "paramValue": "-13.40", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-15.70", "ciUpperLimit": "-11.11"}

#### E0409 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/8/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "100".

Class evidence:
> Change in body weight in kilogram (kg) is presented from baseline (week 0) to the end of treatment (week 44) and it was evaluated based on the data from in-trial observation period. For end of treatment visit, data collected up to week 49 during the in-trial observation period is included in this Outcome Measure. In-trial period: The time period where the participants were assessed in the study. The in-trial period begins on the date of randomization (week 0) and ends at the end of study visit (week 49). 

> {"groupId": "OG000", "value": "-13.0", "spread": "5.5"}

#### E0410 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT04998136/8/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomized participants. Here, Overall number of participants analysed (N) = participants with available data for this outcome measure.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "48".

Class evidence:
> Change in body weight in kilogram (kg) is presented from baseline (week 0) to the end of treatment (week 44) and it was evaluated based on the data from in-trial observation period. For end of treatment visit, data collected up to week 49 during the in-trial observation period is included in this Outcome Measure. In-trial period: The time period where the participants were assessed in the study. The in-trial period begins on the date of randomization (week 0) and ends at the end of study visit (week 49). 

> {"groupId": "OG001", "value": "-2.0", "spread": "5.1"}

#### E0411 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[7]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Until recently, pharmacological options for obesity management were limited by modest efficacy and poor tolerability, along with a lack of robust evidence supporting long‐term efficacy and benefits beyond weight loss [ 5 ].

#### E0412 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[9]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Long‐term studies have provided evidence of sustained weight loss, favorable safety profiles, and metabolic and cardiovascular benefits, supporting the use of these newer pharmacotherapies for chronic obesity management [ 7 , 8 , 9 , 10 , 11 ].

#### E0413 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[69]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Long‐term studies conducted under optimal conditions show an average of 2%–4% total weight loss with lifestyle interventions alone [ 14 , 15 ], highlighting that weight regain is largely driven by biological mechanisms rather than lack of adherence or willpower.

#### E0414 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[73]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Following diet‐induced weight loss, ghrelin levels increase whereas anorexigenic hormone levels decrease, and these changes persist for at least 1 year, producing a sustained biological drive to regain weight [ 22 ].

#### E0415 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[74]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> In parallel, resting energy expenditure decreases by approximately 500 kcal/day beyond what would be predicted based on body mass loss, an adaptation that can persist for up to 6 years after initial weight loss [ 23 ].

#### E0416 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[79]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> As in the treatment of other chronic diseases such as hypertension or T2D, weight‐loss response is heterogeneous, ranging from non‐response up to 50% (or more) total weight loss with a given therapy.

#### E0417 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[92]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 3.1 Topic 1: Obesity as a Chronic Disease and the Need for Long‐Term Therapy The panel reached a strong consensus that obesity should be recognized and treated as a chronic disease driven by excess and abnormal adiposity rather than body weight alone and tightly linked to metabolic dysregulation and increased mortality.

#### E0418 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[96]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> A post hoc analysis of the SURMOUNT‐4 trial provided compelling evidence: in adults with obesity who achieved ≥ 10% weight loss by week 36 on tirzepatide and were then switched to placebo ( n = 308), greater weight regain over weeks 36–88 was associated with a dose–response reversal of cardiometabolic improvements: systolic blood pressure increased by 6.8–10.4 mmHg, non‐high‐density lipoprotein cholesterol increased by up to 10.8%, and HbA1c increased by 0.14%–0.35%.

#### E0419 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[101]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The approval was supported by phase 3 OASIS 4 data demonstrating an estimated 16.6% total weight loss, a favorable safety profile, and improvements in cardiometabolic risk factors [ 30 ].

#### E0420 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[103]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Oral formulations may offer adherence and affordability advantages over injectables in long‐term maintenance settings, supporting a potential treatment strategy in which oral agents facilitate sustained weight maintenance following injectable GLP‐1–induced weight loss [ 33 ].

#### E0421 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[105]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> For example, for patients reluctant to undergo bariatric surgery, a 2– to 3‐month trial of GLP‐1‐based pharmacotherapy can identify early responders who may achieve meaningful weight loss without surgery.

#### E0422 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[119]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Tirzepatide also showed potentially favorable changes in muscle fat infiltration, with muscle volume reductions proportional to overall weight loss, supporting its use in achieving substantial fat loss while preserving lean mass [ 38 ].

#### E0423 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[127]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> With newer obesity medications, patients achieve an initial response within the first 3 to 6 months of treatment, with weight loss often reaching a plateau between 6 and 12 months.

#### E0424 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[148]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> From both U.S. and Chinese perspectives, the panel therefore framed obesity treatment as an upstream intervention capable of mitigating the development and progression of multiple obesity‐related complications, rather than merely a strategy for weight reduction (Table 2 ).

#### E0425 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[149]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> For example, in adults with prediabetes and overweight or obesity, the 3‐year SURMOUNT‐1 study showed that once‐weekly tirzepatide reduced the risk of progression to T2D by 94% compared with placebo [ 51 ], demonstrating that obesity treatment can modify long‐term metabolic risk beyond weight reduction alone.

#### E0426 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[150]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> The panel further discussed the relationship between the magnitude of weight loss and graded clinical benefits (Table 3 ).

#### E0427 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[151]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Weight loss exceeding 5% was associated with improvements in multiple metabolic and some nonmetabolic outcomes, while reductions greater than 10% conferred additional benefits in glycemic control, blood pressure, and lipid profiles.

#### E0428 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[152]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Weight loss exceeding 15% was associated with more pronounced cardiovascular benefit, underscoring the relevance of achieving and sustaining larger degrees of weight reduction in selected patients.

#### E0429 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[160]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 16.1% ( p < 0.001) Body weight change: −10.5% vs. −2.0% ( p < 0.001) SYNERGY‐NASH trial (tirzepatide 15 mg) [ 11 ] Randomized, double‐blind, placebo‐controlled phase 2 trial (52 weeks) Patients with MASH and moderate or severe liver fibrosis Resolution of MASH without worsening of fibrosis MASH resolution: 62% vs.

#### E0430 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[161]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 10% ( p < 0.001) ≥ 1‐stage fibrosis improvement without worsening: 51% SURMOUNT‐OSA trial (tirzepatide 10/15 mg) [ 48 ] Randomized, double‐blind, placebo‐controlled phase 3 trial (52 weeks) Adults with moderate‐to‐severe OSA and obesity; baseline mean AHI 50 events/h; mean BMI = 39 kg/m 2 Change in AHI at week 52 No PAP: AHI change −25.3 vs. −5.3 events/h ( p < 0.001) Receiving PAP: AHI change −29.3 vs. −5.5 events/h ( p < 0.001) Significant reductions in body weight, hypoxic burden, hsCRP, and systolic blood pressure, with improvements in sleep‐related patient‐reported outcomes SURPASS‐CVOT trial (tirzepatide up to 15 mg) [ 49 ] Randomized, double‐blind, active‐comparator–controlled, noninferiority trial (median follow‐up 4.0 years) 13,299 patients with type 2 diabetes and atherosclerotic CVD A composite of death from cardiovascular causes, myocardial infarction, or stroke (tested for noninferiority vs. dulaglutide 1.5 mg) Tirzepatide was noninferior to dulaglutide: primary endpoint occurred in 12.2% vs.

#### E0431 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[162]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 13.1% (tirzepatide vs. dulaglutide); HR 0.92 (95.3% CI 0.83–1.01); p = 0.003 for noninferiority; p = 0.09 for superiority TRIUMPH‐4 trial (retatrutide 12 mg) [ 50 ] Randomized, double‐blind, placebo‐controlled phase 3 trial (68 weeks) Adults with overweight or obesity and knee osteoarthritis Percent change in body weight at week 68; change in WOMAC pain score Percentage change in body weight: −26.4% (−29.1 kg; 9 mg), −28.7% (−32.3 kg; 12 mg), and −2.1% (−2.1 kg; placebo) Change in WOMAC pain subscale score: −4.5 points (−75.8%; 9 mg), −4.4 points (−74.3%; 12 mg), and −2.4 points (−40.3%; placebo) Abbreviations: AHI, apnea–hypopnea index; CVD, cardiovascular disease; HR, hazard ratio; hsCRP, high‐sensitivity C‐reactive protein; MACE, major adverse cardiovascular events; MASH, metabolic dysfunction–associated steatohepatitis; OSA, obstructive sleep apnea; PAP, positive airway pressure; WOMAC, Western Ontario and McMaster Universities Osteoarthritis Index.

#### E0432 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[164]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> Retatrutide (GIP/GLP‐1/glucagon) Tirzepatide (GIP/GLP‐1) Semaglutide (GLP‐1) Clinical trial TRIUMPH‐4 (68 weeks) a SURMOUNT‐5 (72 weeks) b 9 mg 12 mg Mean weight loss 26.4% 28.7% 20.2% 13.7% ≥ 10% weight loss / / 81.6% 60.5% ≥ 15% weight loss / / 64.6% 40.1% ≥ 20% weight loss / / 48.4% 27.3% ≥ 25% weight loss 47.7% 58.6% 31.6% 16.1% ≥ 30% weight loss 30.5% 39.4% 19.7% 6.9% ≥ 35% weight loss 18.2% 23.7% / / Abbreviations: GIP, glucose‐dependent insulinotropic polypeptide; GLP‐1, glucagon‐like peptide‐1. a TRIUMPH‐4: adults with overweight or obesity and knee osteoarthritis, retatrutide (9 or 12 mg) once weekly. b SURMOUNT‐5: adults with obesity but without type 2 diabetes, tirzepatide (10 or 15 mg) or semaglutide (1.7 or 2.4 mg) once weekly.

#### E0433 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[191]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 16.1% ( p < 0.001) Body weight change: −10.5% vs. −2.0% ( p < 0.001)
> SYNERGY‐NASH trial (tirzepatide 15 mg) [ 11 ] | Randomized, double‐blind, placebo‐controlled phase 2 trial (52 weeks) | Patients with MASH and moderate or severe liver fibrosis | Resolution of MASH without worsening of fibrosis | MASH resolution: 62% vs.

#### E0434 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[192]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 10% ( p < 0.001) ≥ 1‐stage fibrosis improvement without worsening: 51%
> SURMOUNT‐OSA trial (tirzepatide 10/15 mg) [ 48 ] | Randomized, double‐blind, placebo‐controlled phase 3 trial (52 weeks) | Adults with moderate‐to‐severe OSA and obesity; baseline mean AHI 50 events/h; mean BMI = 39 kg/m 2 | Change in AHI at week 52 | No PAP: AHI change −25.3 vs. −5.3 events/h ( p < 0.001) Receiving PAP: AHI change −29.3 vs. −5.5 events/h ( p < 0.001) Significant reductions in body weight, hypoxic burden, hsCRP, and systolic blood pressure, with improvements in sleep‐related patient‐reported outcomes
> SURPASS‐CVOT trial (tirzepatide up to 15 mg) [ 49 ] | Randomized, double‐blind, active‐comparator–controlled, noninferiority trial (median follow‐up 4.0 years) | 13,299 patients with type 2 diabetes and atherosclerotic CVD | A composite of death from cardiovascular causes, myocardial infarction, or stroke (tested for noninferiority vs. dulaglutide 1.5 mg) | Tirzepatide was noninferior to dulaglutide: primary endpoint occurred in 12.2% vs.

#### E0435 — embedded_fulltext_window

Source: cache/semaglutide-obesity-weight/records.json#/fulltext_by_pmid/40825340#sentence-window[193]. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **MISASSOCIATED_FULLTEXT**.

Population: UNASSIGNED_TO_INCLUDED_TRIAL. Raw/adjusted: As stated in quote; otherwise NOT_STATED. n: "NOT_STATED".

> 13.1% (tirzepatide vs. dulaglutide); HR 0.92 (95.3% CI 0.83–1.01); p = 0.003 for noninferiority; p = 0.09 for superiority
> TRIUMPH‐4 trial (retatrutide 12 mg) [ 50 ] | Randomized, double‐blind, placebo‐controlled phase 3 trial (68 weeks) | Adults with overweight or obesity and knee osteoarthritis | Percent change in body weight at week 68; change in WOMAC pain score | Percentage change in body weight: −26.4% (−29.1 kg; 9 mg), −28.7% (−32.3 kg; 12 mg), and −2.1% (−2.1 kg; placebo) Change in WOMAC pain subscale score: −4.5 points (−75.8%; 9 mg), −4.4 points (−74.3%; 12 mg), and −2.4 points (−40.3%; placebo)
> 
> TABLE TABLE 3: Weight‐loss responses with tirzepatide, semaglutide, and retatrutide across phase 3 trials.
>  | Retatrutide (GIP/GLP‐1/glucagon) | Tirzepatide (GIP/GLP‐1) | Semaglutide (GLP‐1)
> Clinical trial | TRIUMPH‐4 (68 weeks) a | SURMOUNT‐5 (72 weeks) b
> 9 mg | 12 mg
> Mean weight loss | 26.4% | 28.7% | 20.2% | 13.7%
> ≥ 10% weight loss | / | / | 81.6% | 60.5%
> ≥ 15% weight loss | / | / | 64.6% | 40.1%
> ≥ 20% weight loss | / | / | 48.4% | 27.3%
> ≥ 25% weight loss | 47.7% | 58.6% | 31.6% | 16.1%
> ≥ 30% weight loss | 30.5% | 39.4% | 19.7% | 6.9%
> ≥ 35% weight loss | 18.2% | 23.7% | / | /

### semaglutide-obesity-weight — NCT05040971

#### E0436 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/0/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Full analysis set (FAS) included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "129".

Class evidence:
> Change in body weight from randomisation (week 0) to end of treatment (week 52) is presented. The endpoint was evaluated based on the data from in-trial observation period which was defined as the time period where the participant was assessed in the main phase of the study. The 'in-trial' (main phase) observation period for a participant begins on the date of randomisation and ends at the first of the following dates (both inclusive): safety visit, withdrawal of consent, last contact with participant (for participants lost to follow-up), death. Treatment policy estimand

> {"groupId": "OG000", "value": "-14.4", "spread": "7.9"}

#### E0437 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/0/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Full analysis set (FAS) included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "66".

Class evidence:
> Change in body weight from randomisation (week 0) to end of treatment (week 52) is presented. The endpoint was evaluated based on the data from in-trial observation period which was defined as the time period where the participant was assessed in the main phase of the study. The 'in-trial' (main phase) observation period for a participant begins on the date of randomisation and ends at the first of the following dates (both inclusive): safety visit, withdrawal of consent, last contact with participant (for participants lost to follow-up), death. Treatment policy estimand

> {"groupId": "OG001", "value": "-2.7", "spread": "4.3"}

#### E0438 — registry_analysis

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/0/analyses/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: Full analysis set (FAS) included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; Treatment policy estimand. Raw/adjusted: ADJUSTED_MODEL. n: "NOT_SEPARATELY_STATED; measure denominator is not automatically model n".

Class evidence:
> Change in body weight from randomisation (week 0) to end of treatment (week 52) is presented. The endpoint was evaluated based on the data from in-trial observation period which was defined as the time period where the participant was assessed in the main phase of the study. The 'in-trial' (main phase) observation period for a participant begins on the date of randomisation and ends at the first of the following dates (both inclusive): safety visit, withdrawal of consent, last contact with participant (for participants lost to follow-up), death. Treatment policy estimand

> {"groupIds": ["OG000", "OG001"], "groupDescription": "Treatment policy estimand", "nonInferiorityType": "SUPERIORITY", "nonInferiorityComment": "Week 52 responses were analysed using an analysis of covariance model (ANCOVA) with randomised treatment as factor and baseline body weight as covariate.", "pValue": "<0.0001", "statisticalMethod": "ANCOVA", "paramType": "Treatment difference", "paramValue": "-11.19", "ciPctValue": "95", "ciNumSides": "TWO_SIDED", "ciLowerLimit": "-12.97", "ciUpperLimit": "-9.42"}

#### E0439 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/11/classes/0/categories/0/measurements/0. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "129".

Class evidence:
> Change in body weight from randomisation (week 0) to end of treatment (week 52) is presented. The endpoint was evaluated based on the data from in-trial observation period which was defined as the time period where the participant was assessed in the main phase of the study. The 'in-trial' (main phase) observation period for a participant begins on the date of randomisation and ends at the first of the following dates (both inclusive): safety visit, withdrawal of consent, last contact with participant (for participants lost to follow-up), death. 

> {"groupId": "OG000", "value": "-15.8", "spread": "9.3"}

#### E0440 — registry_arm

Source: cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT05040971/11/classes/0/categories/0/measurements/1. Class: NOT_STATED; body-weight ascertainment method/device not stated. Binding: **DIRECT**.

Population: FAS included all randomised participants. 'Overall Number of Participants Analysed' = participants with available data.; ; . Raw/adjusted: RAW_DESCRIPTIVE_ARM. n: "66".

Class evidence:
> Change in body weight from randomisation (week 0) to end of treatment (week 52) is presented. The endpoint was evaluated based on the data from in-trial observation period which was defined as the time period where the participant was assessed in the main phase of the study. The 'in-trial' (main phase) observation period for a participant begins on the date of randomisation and ends at the first of the following dates (both inclusive): safety visit, withdrawal of consent, last contact with participant (for participants lost to follow-up), death. 

> {"groupId": "OG001", "value": "-2.8", "spread": "5.0"}

## Verification and limits

**PASS:** all 440 source-observation quotations and numeric offsets validated; all 66 registry arm/analysis entries accounted for; 213 numeric literals in the named-result ledger checked against their quoted source. Both reports parse/encode correctly; only the two requested report paths are added.

{"pinned_reviews": 32, "trial_rows": 19, "served": 6, "declared_absent": 13, "registry_arm_observations": 48, "registry_analysis_observations": 18, "named_result_groups": 151, "source_hashes_all_match": true, "no_tests_or_harness_run": true}

All read cache bytes match the pinned commit. Source manifests include SHA-256, git blob hashes and fulltext article IDs. Read-only report validation is used; no harness or tests were edited or run.

Unresolved primary-source identities and n are explicitly retained, never filled from another outcome. Held scanned XML for PMID 12790159 has no body: no OCR or unheld images are inferred. The all-adult -11.2 value is not established in the held source boundary.

