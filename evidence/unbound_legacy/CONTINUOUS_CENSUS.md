# Continuous-row census at 3876a62d

**Report only.** No harness/tests edits, no commit. All 32 historical `docs/reviews/<slug>/review.json` files and all 97 outcomes were inspected. **N = 6 served continuous rows, all 6 primary**, in 3 reviews; no secondary continuous rows. This is a served-row census, not a census of every continuous result present in the caches. For example, unserved TRANSFORM-1 verified arms are not added to N.

Each `outcomes[].trials[]` occurrence is a row. Inclusion: row/outcome/result scale MD or SMD, or arm `mean1` plus `sd1`. Historical review bytes come from `git show 3876a62d:...`; source evidence is held cache bytes, with SHA-256 and comparison to the historical source files in the companion JSON. No online evidence was substituted. Unlocated rows would remain in N. All six numeric rows were located, but one exact full-analysis-set denominator remains unlocated.

## n of N

Counts are row counts, not arm counts; categories overlap. Primary denominators are reported separately even though every continuous row here is primary.

| Property | All outcomes | Primary only |
|---|---:|---:|
| Located served numbers | 6 of 6 | 6 of 6 |
| UNLOCATED served numeric rows | 0 of 6 | 0 of 6 |
| Arm dispersion labelled SD | 6 of 6 | 6 of 6 |
| Arm dispersion labelled SE | 0 of 6 | 0 of 6 |
| Arm dispersion labelled CI / CI half-width | 0 of 6 | 0 of 6 |
| Arm dispersion labelled IQR | 0 of 6 | 0 of 6 |
| Arm dispersion labelled range | 0 of 6 | 0 of 6 |
| SE_AS_SD | 0 of 6 | 0 of 6 |
| CI_HALF_WIDTH_AS_SD | 0 of 6 | 0 of 6 |
| Raw descriptive arm means; raw reconstructed difference | 6 of 6 | 6 of 6 |
| Served LS/adjusted arm means or adjusted difference | 0 of 6 | 0 of 6 |
| Adjusted comparison also located in source | 6 of 6 | 6 of 6 |
| Source explicitly supplies SE of adjusted difference | 2 of 6 | 2 of 6 |
| Served SE reconstructed from arm SD and nc | 6 of 6 | 6 of 6 |
| Served SE derived from CI width | 0 of 6 | 0 of 6 |
| Served nc matches n attached to descriptive values | 4 of 6 | 4 of 6 |
| N_SCOPE_MISMATCH (overall FAS used for available-data means) | 2 of 6 | 2 of 6 |
| Exact full analysis-set/subgroup n located | 5 of 6 | 5 of 6 |
| Exact full analysis-set n UNLOCATED | 1 of 6 | 1 of 6 |
| Observed/evaluable descriptive values within FAS | 5 of 6 | 5 of 6 |
| ITT subgroup; specific missing-data handling unstated | 1 of 6 | 1 of 6 |
| Served values explicitly LOCF | 0 of 6 | 0 of 6 |
| Served values explicitly per-protocol | 0 of 6 | 0 of 6 |
| Reported source 95% two-sided CI, no special procedure located | 5 of 6 | 5 of 6 |
| Non-standard source CI: median-unbiased / weighted combination | 1 of 6 | 1 of 6 |
| Served SE derived from a non-standard source CI | 0 of 6 | 0 of 6 |
| CI-width / 3.92 conversion certified | 0 of 6 | 0 of 6 |

## What is served

| Review / row | Served treatment mean (SD); nc | Served control mean (SD); nc | n attached to source means | FAS / subgroup n | Raw MD; reconstructed SE |
|---|---|---|---|---|---|
| esketamine-trd-madrs / PMID 37025256 | -10.1 (10.8); 109 | -8.1 (10.26); 106 | [109, 106] | [124, 126] | -2; 1.436378192 |
| esketamine-trd-madrs / PMID 31109201 | -21.4 (12.32); 101 | -17.0 (13.88); 100 | [101, 100] | [114, 109] | -4.4; 1.851847737 |
| esketamine-trd-madrs / NCT02422186 | -10.0 (12.74); 63 | -6.3 (8.86); 60 | [63, 60] | UNLOCATED; other evaluable sets 71/64, 71/65 | -3.7; 1.970948446 |
| melatonin-primary-insomnia-sol / PMID 20712869 | -19.1 (47.3); 137 | -1.7 (47.8); 144 | [137, 144] | [137, 144] | -17.4; 5.674286597 |
| semaglutide-obesity-weight / PMID 33625476 | -16.5 (10.1); 407 | -5.8 (7.7); 204 | [373, 189] | [407, 204] | -10.7; 0.735714670 |
| semaglutide-obesity-weight / PMID 33567185 | -15.6 (10.1); 1306 | -2.8 (6.5); 655 | [1212, 577] | [1306, 655] | -12.8; 0.377640763 |

All six served effects are raw arm-mean subtractions. Their SE is `sqrt(sd1?/nc1 + sd2?/nc2)`; each reproduces the served `study_effect.standard_error` to absolute tolerance 1e-12. None is derived from CI width. The baseline formula was inspected in `3876a62d:harness/synth.py:Study.yi_vi`. All six source measures also report a separate model-adjusted comparison. Those source analyses do not turn the descriptive arm means into LS means.

## Every SE_AS_SD / non-standard-CI row

**SE_AS_SD: none (0 of 6). CI half-width used as arm SD: none (0 of 6).** All matched arm spreads have the explicit registry label `"dispersionType": "Standard Deviation"`.

**NONSTANDARD_SOURCE_CI ? esketamine-trd-madrs / NCT02422186 (TRANSFORM-3), primary ?Observed-case Day-28 raw change-score MADRS MD?.** The held abstract PMID 31734084 says:

> For the primary endpoint, the median-unbiased estimate of the treatment difference (95% CI) was -3.6 (-7.20, 0.07); weighted combination test using MMRM analyses z = 1.89, two-sided p = 0.059.

Source: `cache/esketamine-trd-madrs/records.json`, record 31734084, abstract. The record title names TRANSFORM-3; the registry entry NCT02422186 has acronym TRANSFORM-3, and the endpoint and exact adjusted estimate/CI agree. The abstract NCT field is empty; linkage is disclosed rather than presented as an explicit NCT in the abstract.

The registry analysis labels the same result `Difference of Least Square (LS) Means`, MMRM, 95%, `TWO_SIDED`, ?3.6 [?7.20, 0.07]. That generic 95% label does **not** override the median-unbiased/weighted-combination wording. Treat the source CI as non-standard; do not divide its width by 3.92. Exact stage weights and ?two-stage adaptive?, ?group sequential?, and ?repeated CI? wording were not located in the accepted trial source.

Its **served** numbers are raw ?10.0 (SD 12.74), n=63, versus ?6.3 (SD 8.86), n=60: MD ?3.7 and SE 1.970948446. The non-standard reported CI was not used for that SE. Thus non-standard source CI = 1/6, but served SE derived from a non-standard CI = 0/6.

?Flexible doses?, ?flexibly dosed?, and ?flexible-dose study? describe dosing and are never counted as CI procedures. Repeated-measures models are not repeated confidence intervals; two-stage meta-analysis text is not a trial adaptive-CI procedure.

## Row-by-row evidence and typing

### 1. esketamine-trd-madrs ? PMID 37025256 (NCT03434041)

Outcome: **Observed-case Day-28 raw change-score MADRS MD** (primary). Source: `cache/esketamine-trd-madrs/records.json` at `/ctgov_results/NCT03434041/0`.

Measure: Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28). Timepoint: Baseline up to end of the double-blind treatment phase (Day 28). Units: Units on a Scale.

Matched source cells (group OG000 = treatment, OG001 = control):

```json
{
  "paramType": "MEAN",
  "dispersionType": "Standard Deviation",
  "denoms": [
    {
      "units": "Participants",
      "counts": [
        {
          "groupId": "OG000",
          "value": "109"
        },
        {
          "groupId": "OG001",
          "value": "106"
        }
      ]
    }
  ],
  "value_class": {
    "categories": [
      {
        "measurements": [
          {
            "groupId": "OG000",
            "value": "-10.1",
            "spread": "10.80"
          },
          {
            "groupId": "OG001",
            "value": "-8.1",
            "spread": "10.26"
          }
        ]
      }
    ]
  }
}
```

Population, verbatim:

> Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.

Day-28 evaluable/observed counts 109/106 are not the FAS totals 124/126. The identical rounded raw and adjusted difference (-2.0) does not make the estimators identical; reported MMRM difference SE is 1.32, not either arm SD.

**Typing:** raw descriptive change means; source-labelled arm SD; raw reconstructed difference. Observed/evaluable descriptive values within a FAS definition. No served-value LOCF or per-protocol label is established.

Separate adjusted source analysis (not the served raw effect):

```json
[
  {
    "groupIds": [
      "OG000"
    ],
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "0.123",
    "pValueComment": "2-sided",
    "statisticalMethod": "Mixed-effects Model for Repeated Measure",
    "paramType": "Difference of Least Square (LS) Means",
    "paramValue": "-2.0",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-4.64",
    "ciUpperLimit": "0.55"
  }
]
```

Other measure denominators, retained with their own population qualifiers (not automatically substituted for the target denominator):

- Measure [1] **Change From Baseline in Depressive Symptoms as Measured by the MADRS Total Score to 24 Hours Post First Dose (Day 2)**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "123"}, {"groupId": "OG001", "value": "125"}]}]`. Population: ?Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.?
- Measure [3] **Percentage of Participants With Onset of Clinical Response**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "124"}, {"groupId": "OG001", "value": "126"}]}]`. Population: ?Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase.?
- Measure [6] **Percentage of Participants With Sustained Remission**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "124"}, {"groupId": "OG001", "value": "126"}]}]`. Population: ?Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase.?

Corroborating fulltext `cache/esketamine-trd-madrs/ft_37025256.txt`, table `t0001` (XML text joined in document order):

> Table 1 Demographic and Baseline Clinical Characteristics a Characteristic Esketamine Plus AD (n=124) AD Plus Placebo (n=126) Total (n=250) Age, years – mean (SD) 36.9 (12.04) 37.8 (12.36) 37.3 (12.19) Sex – n (%)  Male 66 (53.2) 71 (56.3) 137 (54.8)  Female 58 (46.8) 55 (43.7) 113 (45.2) Race – n (%)  Asian 110 (88.7) 112 (88.9) 222 (88.8)  White 12 (9.7) 9 (7.1) 21 (8.4)  Black or African American 1 (0.8) 4 (3.2) 5 (2.0)  Multiple 1 (0.8) 0 (0) 1 (0.4)  Not reported 0 (0) 1 (0.8) 1 (0.4) Country – n (%)  China 110 (88.7) 112 (88.9) 222 (88.8)  United States 14 (11.3) 14 (11.1) 28 (11.2) BMI, calculated as kg/m 2 – mean (SD) 24.8 (4.98) 24.2 (4.32) 24.5 (4.66) Employment status – n (%) b  Any type of employment 86 (69.4) 79 (62.7) 165 (66.0)  Any type of unemployment 27 (21.8) 38 (30.2) 65 (26.0)  Other 11 (8.9) 9 (7.1) 20 (8.0) Age when diagnosed with MDD, years – mean (SD) 27.2 (11.53) 28.2 (11.87) 27.7 (11.69) Duration of current episode, weeks – mean (SD) 225.3 (317.75) 218.6 (274.20) 221.9 (296.02) MADRS total score – mean (SD) 36.5 (5.21) 35.9 (4.50) 36.2 (4.87) CGI-S – mean (SD) 5.1 (0.61) 5.2 (0.68) 5.1 (0.65) CGI-S category – n (%)  Mildly ill 1 (0.8) 1 (0.8) 2 (0.8)  Moderately ill 15 (12.1) 16 (12.7) 31 (12.4)  Markedly ill 81 (65.3) 74 (58.7) 155 (62.0)  Severely ill 27 (21.8) 33 (26.2) 60 (24.0)  Most extremely ill 0 (0) 2 (1.6) 2 (0.8) Class of oral AD – n (%)  SNRI 68 (54.8) 69 (54.8) 137 (54.8)  SSRI 56 (45.2) 57 (45.2) 113 (45.2) Oral AD – n (%)  Duloxetine 36 (29.0) 40 (31.7) 76 (30.4)  Escitalopram 30 (24.2) 34 (27.0) 64 (25.6)  Venlafaxine extended release 31 (25.0) 29 (23.0) 60 (24.0)  Sertraline 27 (21.8) 23 (18.3) 50 (20.0) Number of previous treatment failures in current episode – n (%) c  1 38 (30.6) 38 (30.2) 76 (30.4)  2 46 (37.1) 47 (37.3) 93 (37.2)  3 29 (23.4) 31 (24.6) 60 (24.0)  4 7 (5.6) 8 (6.3) 15 (6.0)  5 4 (3.2) 2 (1.6) 6 (2.4) Notes :  a Data generated from the efficacy analysis set.  b Any type of employment includes any category containing “employed”, sheltered work, housewife or dependent husband, and student; any type of unemployment includes any category containing “unemployed”; “other” includes retired or no information available.  c Number of AD medications with nonresponse (defined as ≤25% improvement) taken for at least 6 weeks during the current episode as obtained from MGH-ATRQ at screening. Abbreviations : AD, antidepressant; BMI, body mass index; CGI-S, Clinical Global Impression of Severity; MADRS, Montgomery-Åsberg Depression Rating Scale; MDD, major depressive disorder; MGH-ATRQ, Massachusetts General Hospital – Antidepressant Treatment Response Questionnaire; SD, standard deviation; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

Corroborating fulltext `cache/esketamine-trd-madrs/ft_37025256.txt`, table `t0002` (XML text joined in document order):

> Table 2 Change in MADRS Total Score a  from Baseline to Day 28 in the Double-Blind Treatment Phase Esketamine Plus AD AD Plus Placebo Baseline  N 124 126  Mean (SD) 36.5 (5.21) 35.9 (4.50)  Median (range) 36.0 (25, 50) 36.0 (27, 48) Day 28  N 109 106  Mean (SD) 26.5 (10.33) 27.9 (10.04)  Median (range) 28.0 (0, 43) 30.0 (0, 44) Change from baseline to Day 28  N 109 106  Mean (SD) −10.1 (10.80) −8.1 (10.26)  Median (range) −7.0 (−42, 10) −6.0 (−38, 8) MMRM analysis b  Difference of LS means (SE) −2.0 (1.32)  95% CI on difference −4.64, 0.55  2-sided p-value 0.123 Notes :  a MADRS total score ranges from 0 to 60; a higher score indicates a more severe condition. Negative change in score indicates improvement.  b Test for treatment effect is based on MMRM analysis with change from baseline as the response variable and the fixed effect model terms for treatment (esketamine plus AD, AD plus placebo), day, country, class of oral AD (SNRI or SSRI), and treatment-by-day, and baseline value as a covariate. A negative difference favors esketamine. Abbreviations : AD, antidepressant; LS, least squares; MADRS, Montgomery-Åsberg Depression Rating Scale; MMRM, mixed model for repeated measures; SD, standard deviation; SE, standard error; SNRI, serotonin-norepinephrine reuptake inhibitor; SSRI, selective serotonin reuptake inhibitor.

Table 2 separately reports **Difference of LS means (SE) ?2.0 (1.32)**. This is distinct from both arm SDs and the served reconstructed difference SE 1.436378192.

CI classification: `REPORTED_STANDARD_95_TWO_SIDED_NO_SPECIAL_PROCEDURE_LOCATED`. The source CI is unused by the served SE. No normal-Wald width/3.92 conversion is certified.

Verified-input files: `cache/esketamine-trd-madrs/verified_arms.json` (no matching served continuous override); `cache/esketamine-trd-madrs/verified_effects.json` (no matching served continuous override). The complete matching entries are retained in JSON; harm overrides/refusals are not treated as continuous data.

### 2. esketamine-trd-madrs ? PMID 31109201 (NCT02418585)

Outcome: **Observed-case Day-28 raw change-score MADRS MD** (primary). Source: `cache/esketamine-trd-madrs/records.json` at `/ctgov_results/NCT02418585/0`.

Measure: Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis. Timepoint: Baseline up to Day 28 of Double-blind Induction Phase. Units: Units on a scale.

Matched source cells (group OG000 = treatment, OG001 = control):

```json
{
  "paramType": "MEAN",
  "dispersionType": "Standard Deviation",
  "denoms": [
    {
      "units": "Participants",
      "counts": [
        {
          "groupId": "OG000",
          "value": "101"
        },
        {
          "groupId": "OG001",
          "value": "100"
        }
      ]
    }
  ],
  "value_class": {
    "categories": [
      {
        "measurements": [
          {
            "groupId": "OG000",
            "value": "-21.4",
            "spread": "12.32"
          },
          {
            "groupId": "OG001",
            "value": "-17.0",
            "spread": "13.88"
          }
        ]
      }
    ]
  }
}
```

Population, verbatim:

> Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.

Day-28 evaluable counts 101/100 differ from FAS 114/109 on the onset-of-response measure. ANCOVA evaluable counts are separately 112/109. The source SE 1.69 is the SE of the LS-mean DIFFERENCE, not an arm SD.

**Typing:** raw descriptive change means; source-labelled arm SD; raw reconstructed difference. Observed/evaluable descriptive values within a FAS definition. No served-value LOCF or per-protocol label is established.

Separate adjusted source analysis (not the served raw effect):

```json
[
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "=0.020",
    "statisticalMethod": "Mixed Model for Repeated Measures",
    "paramType": "Difference of Least Square (LS) Means",
    "paramValue": "-4.0",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-7.31",
    "ciUpperLimit": "-0.64",
    "dispersionType": "STANDARD_ERROR_OF_MEAN",
    "dispersionValue": "1.69"
  }
]
```

Other measure denominators, retained with their own population qualifiers (not automatically substituted for the target denominator):

- Measure [1] **Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "112"}, {"groupId": "OG001", "value": "109"}]}]`. Population: ?FAS defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of AD medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.?
- Measure [2] **Percentage of Participants With Onset of Clinical Response on Day 2 and Day 8**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "114"}, {"groupId": "OG001", "value": "109"}]}]`. Population: ?FAS is defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral AD medication during the double-blind induction phase.?

The held abstract explicitly says:

> Change in MADRS score with esketamine plus antidepressant was significantly greater than with antidepressant plus placebo at day 28 (difference of least square means=-4.0, SE=1.69, 95% CI=-7.31, -0.64); likewise, clinically meaningful improvement was observed in the esketamine plus antidepressant arm at earlier time points.

Here 1.69 is an **SE of the adjusted difference**; served arm SDs are 12.32 and 13.88.

CI classification: `REPORTED_STANDARD_95_TWO_SIDED_NO_SPECIAL_PROCEDURE_LOCATED`. The source CI is unused by the served SE. No normal-Wald width/3.92 conversion is certified.

Source limitation: The fulltext_by_pmid entries keyed 31109201 and 31734084 are identical ELLIPSE text, not the named randomized trial reports; not accepted as trial-specific evidence.

Verified-input files: `cache/esketamine-trd-madrs/verified_arms.json` (no matching served continuous override); `cache/esketamine-trd-madrs/verified_effects.json` (no matching served continuous override). The complete matching entries are retained in JSON; harm overrides/refusals are not treated as continuous data.

### 3. esketamine-trd-madrs ? NCT02422186 (NCT02422186)

Outcome: **Observed-case Day-28 raw change-score MADRS MD** (primary). Source: `cache/esketamine-trd-madrs/records.json` at `/ctgov_results/NCT02422186/0`.

Measure: Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis. Timepoint: Baseline up to Endpoint (Double-blind Induction Phase[Day 28]). Units: Units on a scale.

Matched source cells (group OG000 = treatment, OG001 = control):

```json
{
  "paramType": "MEAN",
  "dispersionType": "Standard Deviation",
  "denoms": [
    {
      "units": "Participants",
      "counts": [
        {
          "groupId": "OG000",
          "value": "63"
        },
        {
          "groupId": "OG001",
          "value": "60"
        }
      ]
    }
  ],
  "value_class": {
    "categories": [
      {
        "measurements": [
          {
            "groupId": "OG000",
            "value": "-10.0",
            "spread": "12.74"
          },
          {
            "groupId": "OG001",
            "value": "-6.3",
            "spread": "8.86"
          }
        ]
      }
    ]
  }
}
```

Population, verbatim:

> The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.

Day-28 evaluable counts 63/60 differ from ANCOVA/LOCF evaluable counts 71/64; CGI-S gives 71/65. These other endpoint counts are not proof of the exact complete FAS size, which remains UNLOCATED. The reported adjusted CI is non-standard; the served raw MD does not use it.

**Typing:** raw descriptive change means; source-labelled arm SD; raw reconstructed difference. Observed/evaluable descriptive values within a FAS definition. No served-value LOCF or per-protocol label is established.

Separate adjusted source analysis (not the served raw effect):

```json
[
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "=0.059",
    "statisticalMethod": "Mixed Model for Repeated Measures",
    "paramType": "Difference of Least Square (LS) Means",
    "paramValue": "-3.6",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-7.20",
    "ciUpperLimit": "0.07"
  }
]
```

Other measure denominators, retained with their own population qualifiers (not automatically substituted for the target denominator):

- Measure [1] **Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to Endpoint (Double-blind Induction Phase [Day 28])- Analysis of Covariance (ANCOVA) Analysis**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "71"}, {"groupId": "OG001", "value": "64"}]}]`. Population: ?The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.?
- Measure [2] **Percentage of Participants Who Achieved >=50% Reduction From Baseline in MADRS Total Score at Endpoint (Double-blind Induction Phase [Day 28]) (LOCF Data)**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "71"}, {"groupId": "OG001", "value": "64"}]}]`. Population: ?The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.?
- Measure [3] **Percentage of Participants in Remission (MADRS<=12) at Endpoint (Double-blind Induction Phase [Day 28]) (LOCF Data)**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "71"}, {"groupId": "OG001", "value": "64"}]}]`. Population: ?The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.?
- Measure [4] **Change From Baseline in Clinical Global Impression-Severity (CGI-S) Score to Endpoint (Double-blind Induction Phase [Day 28])- ANCOVA Analysis on Ranks**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "71"}, {"groupId": "OG001", "value": "65"}]}]`. Population: ?The full analysis set was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.?

CI classification: `NONSTANDARD_MEDIAN_UNBIASED_WEIGHTED_COMBINATION`. The source CI is unused by the served SE. No normal-Wald width/3.92 conversion is certified.

Source limitation: The fulltext_by_pmid entries keyed 31109201 and 31734084 are identical ELLIPSE text, not the named randomized trial reports; not accepted as trial-specific evidence.

Verified-input files: `cache/esketamine-trd-madrs/verified_arms.json` (no matching served continuous override); `cache/esketamine-trd-madrs/verified_effects.json` (no matching served continuous override). The complete matching entries are retained in JSON; harm overrides/refusals are not treated as continuous data.

### 4. melatonin-primary-insomnia-sol ? PMID 20712869 (NCT00397189)

Outcome: **Sleep-onset latency** (primary). Source: `cache/melatonin-primary-insomnia-sol/records.json` at `/ctgov_results/NCT00397189/0`.

Measure: The Change From Baseline in Subjective Sleep Latency.. Timepoint: Baseline and 3 weeks. Units: minutes.

Matched source cells (group OG000 = treatment, OG001 = control):

```json
{
  "paramType": "MEAN",
  "dispersionType": "Standard Deviation",
  "denoms": [
    {
      "units": "Participants",
      "counts": [
        {
          "groupId": "OG000",
          "value": "137"
        },
        {
          "groupId": "OG001",
          "value": "144"
        }
      ]
    }
  ],
  "value_class": {
    "categories": [
      {
        "measurements": [
          {
            "groupId": "OG000",
            "value": "-19.1",
            "spread": "47.3"
          },
          {
            "groupId": "OG001",
            "value": "-1.7",
            "spread": "47.8"
          }
        ]
      }
    ]
  }
}
```

Population, verbatim:

> Pre-planned analysis on ITT population age 65-80

Registry calls this the pre-planned age 65-80 ITT analysis; fulltext Table 3 gives these same N and mean (SD). Table 2 also gives 137/144 for this subgroup. Missing-data/imputation handling of these specific descriptive means is not explicitly stated: do not silently label LOCF or per-protocol. Overall trial FAS 373/373 is a different population; the discussion also says 722 overall, conflicting with the results total 746. Neither overall total replaces subgroup N.

**Typing:** raw descriptive change means; source-labelled arm SD; raw reconstructed difference. ITT age subgroup; descriptive-value missingness/imputation unresolved. No served-value LOCF or per-protocol label is established.

Separate adjusted source analysis (not the served raw effect):

```json
[
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "groupDescription": "The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.",
    "nonInferiorityType": "SUPERIORITY_OR_OTHER",
    "pValue": "<0.05",
    "statisticalMethod": "ANCOVA",
    "paramType": "Mean Difference (Final Values)",
    "paramValue": "-15.6",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-25.3",
    "ciUpperLimit": "-6",
    "dispersionType": "STANDARD_DEVIATION",
    "dispersionValue": "47"
  }
]
```

Other measure denominators, retained with their own population qualifiers (not automatically substituted for the target denominator):

- Measure [1] **The Change From Baseline in Subjective Sleep Maintenance.**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "137"}, {"groupId": "OG001", "value": "144"}]}]`. Population: ?None?

Corroborating fulltext `cache/melatonin-primary-insomnia-sol/ft_20712869.txt`, table `T2` (XML text joined in document order):

> Table 2 Baseline characteristics of those aged 65-80, by treatment: age, sex, race, height, weight, BMI and medication use. All First randomization Second randomization PRM Placebo PRM Placebo N 281 137 144 198 75 Characteristic Visit Age (years) 1 Mean (SD) 71.0 (4.1) 71.1 (3.8) 70.9 (4.4) 70.9 (3.9) 70.9 (4.4) Sex N  (%) female 182 (64.8%) 89 (65.0%) 93 (64.6%) 128 (64.6%) 50 (66.7%) Race* N  (%) white 280 (100.0%) 137 (100.0%) 143 (100.0%) 198 (100.0%) 74 (100.0%) Height (m) 1 Mean (SD) 1.65 (0.09) 1.65 (0.09) 1.64 (0.09) 1.65 (0.09) 1.64 (0.09) Weight (kg) 1 Mean (SD) 73.3 (13.0) 73.1 (14.1) 73.6 (11.8) 73.2 (13.2) 74.1 (12.6) BMI (kg/m 2 ) 1 Mean (SD) 27.0 (3.8) 26.8 (3.6) 27.3 (3.9) 26.8 (3.6) 27.7 (4.2) Taking any medications 1 N  (%) 265 (94.3%) 130 (94.9%) 135 (93.8%) 187 (94.4%) 70 (93.3%) Taking codeine† 1 N  (%) 73 (26.2%) 35 (25.7%) 38 (26.6%) 50 (25.5%) 20 (26.7%) Taking codeine 2 N  (%) 58 (20.6%) 28 (20.4%) 30 (20.8%) 40 (20.2%) 16 (21.3%) Confirmed codeine analgesic 2 N  (%) 43 (15.3%) 18 (13.1%) 25 (17.4%) 25 (12.6%) 16 (21.3%) *One patient missed observation †Two patients missed observations at Visit 1 PRM, prolonged release melatonin; SD, standard deviation

Corroborating fulltext `cache/melatonin-primary-insomnia-sol/ft_20712869.txt`, table `T3` (XML text joined in document order):

> Table 3 Effects of 3 weeks treatment with prolonged release melatonin (PRM) and placebo on sleep diary-recorded sleep latency in the low excretors and the elderly patients. Treatment Treatment effect difference PRM - placebo; (95% confidence interval) P  value* effect PRM versus placebo PRM Placebo Low excretor population N 86 86 Baseline: mean (SD) 74.1 (54.9) 75.5 (58.5) Treatment: mean (SD) 65.1 (59.9) 66.5 (51.6) Change from baseline: mean (SD) -9.0 (50.5) -9.0 (48.7) -0.6 (-14.0, 12.7) 0.924 65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8) -15.6 (-25.3, -6.0), 0.002 *Linear regression model with terms for treatment (PRM versus placebo), baseline sleep latency and age group (≥65 or <65 - only for the low excretors). PRM, prolonged release melatonin; SD, standard deviation.

CI classification: `REPORTED_STANDARD_95_TWO_SIDED_NO_SPECIAL_PROCEDURE_LOCATED`. The source CI is unused by the served SE. No normal-Wald width/3.92 conversion is certified.

Verified-input files: `cache/melatonin-primary-insomnia-sol/verified_arms.json` (no matching served continuous override); `cache/melatonin-primary-insomnia-sol/verified_effects.json` (no matching served continuous override). The complete matching entries are retained in JSON; harm overrides/refusals are not treated as continuous data.

### 5. semaglutide-obesity-weight ? PMID 33625476 (NCT03611582)

Outcome: **Percent change in body weight** (primary). Source: `cache/semaglutide-obesity-weight/records.json` at `/ctgov_results/NCT03611582/0`.

Measure: Change in Body Weight (%). Timepoint: Baseline (week 0) to week 68. Units: Percentage.

Matched source cells (group OG000 = treatment, OG001 = control):

```json
{
  "paramType": "MEAN",
  "dispersionType": "Standard Deviation",
  "denoms": [
    {
      "units": "Participants",
      "counts": [
        {
          "groupId": "OG000",
          "value": "407"
        },
        {
          "groupId": "OG001",
          "value": "204"
        }
      ]
    }
  ],
  "value_class": {
    "title": "In-trial observation period",
    "denoms": [
      {
        "units": "Participants",
        "counts": [
          {
            "groupId": "OG000",
            "value": "373"
          },
          {
            "groupId": "OG001",
            "value": "189"
          }
        ]
      }
    ],
    "categories": [
      {
        "measurements": [
          {
            "groupId": "OG000",
            "value": "-16.5",
            "spread": "10.1"
          },
          {
            "groupId": "OG001",
            "value": "-5.8",
            "spread": "7.7"
          }
        ]
      }
    ]
  }
}
```

Population, verbatim:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

N_SCOPE_MISMATCH: served nc 407/204 are overall randomized/FAS counts; the exact In-trial observation period class supplying the means has available-data n 373/189. Raw observed means are not the ANCOVA treatment-policy estimates, even though the served population metadata calls them treatment-policy/all randomized.

**Typing:** raw descriptive change means; source-labelled arm SD; raw reconstructed difference. Observed/evaluable descriptive values within a FAS definition. No served-value LOCF or per-protocol label is established.

Separate adjusted source analysis (not the served raw effect):

```json
[
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "groupDescription": "Treatment policy estimand",
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "<.0001",
    "statisticalMethod": "ANCOVA",
    "paramType": "Treatment difference",
    "paramValue": "-10.27",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-11.97",
    "ciUpperLimit": "-8.57"
  },
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "groupDescription": "Hypothetical estimand",
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "<0.0001",
    "statisticalMethod": "MMRM (mixed model repeated measurement)",
    "paramType": "Treatment difference",
    "paramValue": "-12.67",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-14.34",
    "ciUpperLimit": "-11.00"
  }
]
```

Other measure denominators, retained with their own population qualifiers (not automatically substituted for the target denominator):

- Measure [1] **Participants Who Achieve (Yes/no): Body Weight Reduction More Than or Equal to 5%**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "407"}, {"groupId": "OG001", "value": "204"}]}]`. Population: ?Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.?
- Measure [2] **Participants Who Achieve (Yes/no): Body Weight Reduction More Than or Equal to 10%**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "373"}, {"groupId": "OG001", "value": "189"}]}]`. Population: ?FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.?
- Measure [3] **Participants Who Achieve (Yes/no): Body Weight Reduction More Than or Equal to 15%**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "373"}, {"groupId": "OG001", "value": "189"}]}]`. Population: ?FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.?

CI classification: `REPORTED_STANDARD_95_TWO_SIDED_NO_SPECIAL_PROCEDURE_LOCATED`. The source CI is unused by the served SE. No normal-Wald width/3.92 conversion is certified.

Verified-input files: `cache/semaglutide-obesity-weight/verified_effects.json` (no matching served continuous override). The complete matching entries are retained in JSON; harm overrides/refusals are not treated as continuous data.

### 6. semaglutide-obesity-weight ? PMID 33567185 (NCT03548935)

Outcome: **Percent change in body weight** (primary). Source: `cache/semaglutide-obesity-weight/records.json` at `/ctgov_results/NCT03548935/0`.

Measure: Change in Body Weight (%). Timepoint: Baseline (week 0) to week 68. Units: Percentage point.

Matched source cells (group OG000 = treatment, OG001 = control):

```json
{
  "paramType": "MEAN",
  "dispersionType": "Standard Deviation",
  "denoms": [
    {
      "units": "Participants",
      "counts": [
        {
          "groupId": "OG000",
          "value": "1306"
        },
        {
          "groupId": "OG001",
          "value": "655"
        }
      ]
    }
  ],
  "value_class": {
    "title": "In-trial observation period",
    "denoms": [
      {
        "units": "Participants",
        "counts": [
          {
            "groupId": "OG000",
            "value": "1212"
          },
          {
            "groupId": "OG001",
            "value": "577"
          }
        ]
      }
    ],
    "categories": [
      {
        "measurements": [
          {
            "groupId": "OG000",
            "value": "-15.6",
            "spread": "10.1"
          },
          {
            "groupId": "OG001",
            "value": "-2.8",
            "spread": "6.5"
          }
        ]
      }
    ]
  }
}
```

Population, verbatim:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

N_SCOPE_MISMATCH: served nc 1306/655 are overall randomized/FAS counts; the exact In-trial observation period class supplying the means has available-data n 1212/577. Raw observed means are not the ANCOVA treatment-policy estimates, even though the served population metadata calls them treatment-policy/all randomized.

**Typing:** raw descriptive change means; source-labelled arm SD; raw reconstructed difference. Observed/evaluable descriptive values within a FAS definition. No served-value LOCF or per-protocol label is established.

Separate adjusted source analysis (not the served raw effect):

```json
[
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "groupDescription": "Treatment policy estimand",
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "<.0001",
    "statisticalMethod": "ANCOVA",
    "paramType": "Treatment difference",
    "paramValue": "-12.44",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-13.37",
    "ciUpperLimit": "-11.51"
  },
  {
    "groupIds": [
      "OG000",
      "OG001"
    ],
    "groupDescription": "Hypothetical estimand",
    "nonInferiorityType": "SUPERIORITY",
    "pValue": "<0.0001",
    "statisticalMethod": "ANCOVA",
    "paramType": "Treatment difference",
    "paramValue": "-14.42",
    "ciPctValue": "95",
    "ciNumSides": "TWO_SIDED",
    "ciLowerLimit": "-15.29",
    "ciUpperLimit": "-13.55"
  }
]
```

Other measure denominators, retained with their own population qualifiers (not automatically substituted for the target denominator):

- Measure [1] **Participants Who Achieve 5 or More Percent Body Weight Reduction (Yes/no)**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "1306"}, {"groupId": "OG001", "value": "655"}]}]`. Population: ?Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.?
- Measure [2] **Subjects Who Achieve 10 or More Percent Body Weight Reduction (Yes/no)**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "1212"}, {"groupId": "OG001", "value": "577"}]}]`. Population: ?FAS included all randomized participants. 'Overall Number of Participants Analyzed' = participants with available data.?
- Measure [3] **Participants Who Achieve 15 or More Percent Body Weight Reduction (Yes/no)**: `[{"units": "Participants", "counts": [{"groupId": "OG000", "value": "1212"}, {"groupId": "OG001", "value": "577"}]}]`. Population: ?FAS included all randomised participants. 'Overall Number of Participants Analyzed' = participants with available data.?

CI classification: `REPORTED_STANDARD_95_TWO_SIDED_NO_SPECIAL_PROCEDURE_LOCATED`. The source CI is unused by the served SE. No normal-Wald width/3.92 conversion is certified.

Verified-input files: `cache/semaglutide-obesity-weight/verified_effects.json` (no matching served continuous override). The complete matching entries are retained in JSON; harm overrides/refusals are not treated as continuous data.

## Limits and validation

Five source analyses are reported as ordinary 95% two-sided model CIs with no special CI procedure located. This classification is limited to held evidence; it does not certify a normal-Wald critical value of 1.96. A finite-df t-based CI also cannot be inverted exactly by dividing by 3.92. All six CI-to-SE applicability decisions are **not applicable to the served construction**.

The source n problem is separate from dispersion typing: semaglutide STEP 3 (PMID 33625476) serves 407/204 with observed means whose source n is 373/189; STEP 1 (PMID 33567185) serves 1306/655 with means whose source n is 1212/577. Both rows are explicitly flagged N_SCOPE_MISMATCH. Esketamine Day-28 observed/evaluable counts are distinguished from larger FAS or ANCOVA/LOCF sets; no larger count is silently substituted.

Validation **PASS**: full historical inventory reconciled with the six census rows; each arm mean/spread matched exactly to source cells; each served SE recomputed within 1e-12; matched timepoints and trial identifiers rechecked. JSON includes the entire outcome inventory, original served rows, source measures/analyses, quotes, denominator comparisons, and source hashes. No harness or test files were changed and no repository test suite was run for this report-only task.

| Component | Static vs dynamic | Basis |
|---|---|---|
| Served inventory, numeric matches, denominator comparisons, SE reconstruction, counts and file hashes | dynamic | Computed from git 3876a62d and held cache bytes. |
| Raw/adjusted, population and CI classifications; trial linkage | static adjudication | Manually reviewed source labels and quoted text; no invented measurements, no absence-of-keyword proof of normal-Wald CI. |
