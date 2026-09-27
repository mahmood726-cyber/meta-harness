# Served registry route audit

Pinned served data: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. Report only; no harness/test edits, regeneration, or commit.

**Confirmed declaration/component mismatches: 4 of 13 registry-route served rows; primary outcomes: 4 of 11.** UNLOCATED: 0. Three additional primary MADRS rows have unresolved analysis qualifiers, not established wrong clinical outcomes. Counting every unresolved full declaration as non-confirmed gives 7/13 overall and 7/11 primary; that is distinct from the confirmed-mismatch numerator.

Census: 32 reviews, 97 outcomes, 127 top-level outcomes[].trials[] rows. All outcomes are included, even the served omega3 atrial-fibrillation row whose result is HARMS_INCOMPLETE (no displayed pooled estimate). Candidates, sensitivity copies and reproduction copies are not extra trial rows. Twelve broad ClinicalTrials.gov hits are abstract results with registration prose, listed in JSON and excluded from N. Two CT.gov references describe superseded count reconstructions in fulltext-verified overrides (PARADIGM-HF PMID 25176015; DAPA-CKD PMID 32970396); their served estimates are not registry extractions.

The balanced-crystalloid MAKE30 candidates are not served. Mortality contains PMID 35041780 and PMID 34375394, both abstract routes; new renal-replacement therapy contains PMID 35041780, also abstract.

## Method and disclosure

Read every review, topic and registry object from git show at the pinned ref. Match outcome names in primary_outcome, secondary_outcomes, harm_outcomes, then comparator_outcomes (primary takes precedence over a duplicate comparator name). Primary status is the served outcome.primary flag. Locate effect rows using the zero-based outcome measure number, exact title, and analysis point plus both CI limits. Locate reconstructed rows uniquely using every arm count or mean/SD/n value and the complete extractor source. Quote held objects, never current online records.

Run the unchanged current classify_registry_measure on each located measure and the unchanged declared spec, without injected kind, synonyms or annotations. Human reading separately accepts ordinary semantic equivalents and checks trial-specific declared components. UNBOUND is abstention, not proof of mismatch. Timepoints are interpreted in the supplied trial-follow-up context; vague trial-end declarations do not define a common numeric duration.

Instrument head: `a65878d0813e3c8edfe53191ba84657b4a7926be`. target_endpoint.py SHA-256: `590ba3c267a4df9501ec5875d084c81502d9af2080b49fda665cf4f6473a7bea`.

| Item | Static / dynamic |
|---|---|
| Route scan, tuple/analysis equality, zero-based numbering | Static audit rules |
| Membership, specs, identifiers, values, measure quotes | Dynamic pinned git evidence |
| Human judgments | Explicit case-by-case interpretation; no classifier tuning |
| Counts / removal k | Computed from served membership and result.k; no re-pooling |

## Named mismatches and primary pool effects

| Review / row | Missing declared components | Removal |
|---|---|---|
| omega3: STRENGTH, PMID 33190147 / NCT02104817 #2 | Coronary revascularization; unstable-angina hospitalization | k 5 to 4 alone |
| omega3: REDUCE-IT, PMID 30415628 / NCT01492361 #1 | Coronary revascularization; unstable angina | k 5 to 4 alone; both removed: k 3 |
| pcsk9: FOURIER, PMID 28304224 / NCT01764633 #1 | Unstable-angina hospitalization; coronary revascularization | k 2 to 1; multi-study pool withdrawn |
| sglt2-hfref: DAPA-HF, PMID 31535829 / NCT03036124 #1 | Urgent HF visit requiring IV therapy in trial annotation | k 2 to 1; multi-study pool withdrawn |

DAPA-HF matches the generic review name but not its own declared trial annotation. These findings concern the complete declaration, not a claim that three-point composites cannot be called MACE. Withdrawal means loss of a multi-study pool; the engine can still report a single-study estimate at k=1. No counterfactual CI or replacement estimate is asserted.

## Instrument versus reading

Instrument: 2 EXACT_TARGET, 11 ENDPOINT_UNBOUND. Four disagreements (human outcome-name/timepoint MATCH versus instrument UNBOUND): melatonin PMID 20712869; semaglutide PMIDs 33625476 and 33567185; sacubitril NCT02468232. The two harm rows agree as matches. Four human component mismatches receive instrument abstentions, consistent with not confirming identity but not diagnosing those errors. The three MADRS full analysis qualifiers remain unresolved.

All five registry effect rows carried served EXACT_TARGET; four are component mismatches here. The three unresolved MADRS rows each have k 3 to 2 if individually removed; removing all three would leave k=0 and withdraw that result. They are excluded from the confirmed-mismatch numerator.

## Every served registry measure

### 1. esketamine-trd-madrs / PMID 37025256 / Observed-case Day-28 raw change-score MADRS MD

Primary: True. Reading: **UNRESOLVED_QUALIFIER**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0`. Served: `docs/reviews/esketamine-trd-madrs/review.json#/outcomes/0/trials/0`.

Declared spec:

```json
{
  "name": "Observed-case Day-28 raw change-score MADRS MD",
  "keywords": [
    "montgomery",
    "madrs",
    "montgomery-asberg",
    "montgomery-åsberg",
    "depression rating scale",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "MD",
  "population": "full analysis set (FAS/mITT)",
  "timepoint": "Day 28 double-blind induction endpoint",
  "trial_annotations": {
    "37025256": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "31109201": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "NCT02422186": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "NCT02417064": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    }
  }
}
```

Title:

> Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28)

Description:

> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement.

Time frame:

> Baseline up to end of the double-blind treatment phase (Day 28)

Population:

> Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.

Served numeric source:

> ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery Asberg Depression Rating Scale (MAD' mean -10.1 (SD 10.8, n=109) [Intranasal Esketamine ] vs -8.1 (SD 10.26, n=106) [Intranasal Placebo + O] Units on a Scale — population: Full analysis set included all randomized participants who received a least 1 do

MADRS change from baseline to Day 28 is explicitly named. Observed-case raw change-score handling is not explicit in the title/description. MEAN/Standard Deviation cells support raw summaries but do not independently prove observed-case handling.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 3 to 2; withdraw multi-study pool: False.

### 2. esketamine-trd-madrs / PMID 31109201 / Observed-case Day-28 raw change-score MADRS MD

Primary: True. Reading: **UNRESOLVED_QUALIFIER**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0`. Served: `docs/reviews/esketamine-trd-madrs/review.json#/outcomes/0/trials/1`.

Declared spec:

```json
{
  "name": "Observed-case Day-28 raw change-score MADRS MD",
  "keywords": [
    "montgomery",
    "madrs",
    "montgomery-asberg",
    "montgomery-åsberg",
    "depression rating scale",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "MD",
  "population": "full analysis set (FAS/mITT)",
  "timepoint": "Day 28 double-blind induction endpoint",
  "trial_annotations": {
    "37025256": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "31109201": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "NCT02422186": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "NCT02417064": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    }
  }
}
```

Title:

> Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis

Description:

> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.

Time frame:

> Baseline up to Day 28 of Double-blind Induction Phase

Population:

> Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.

Served numeric source:

> ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery-Asberg Depression Rating Scale (MAD' mean -21.4 (SD 12.32, n=101) [Intranasal Esketamine ] vs -17.0 (SD 13.88, n=100) [Intranasal Placebo Plu] Units on a scale — population: Full analysis set (FAS) defined as all randomized participants who received at l

MADRS change from baseline to Day 28 is explicitly named. Observed-case raw change-score handling is not explicit in the title/description. MEAN/Standard Deviation cells support raw summaries but do not independently prove observed-case handling. The title says MMRM analysis; neither certify observed-case identity nor assume the extracted mean/SD cells themselves are model-adjusted from that title.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 3 to 2; withdraw multi-study pool: False.

### 3. esketamine-trd-madrs / NCT02422186 / Observed-case Day-28 raw change-score MADRS MD

Primary: True. Reading: **UNRESOLVED_QUALIFIER**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0`. Served: `docs/reviews/esketamine-trd-madrs/review.json#/outcomes/0/trials/2`.

Declared spec:

```json
{
  "name": "Observed-case Day-28 raw change-score MADRS MD",
  "keywords": [
    "montgomery",
    "madrs",
    "montgomery-asberg",
    "montgomery-åsberg",
    "depression rating scale",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "MD",
  "population": "full analysis set (FAS/mITT)",
  "timepoint": "Day 28 double-blind induction endpoint",
  "trial_annotations": {
    "37025256": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "31109201": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "NCT02422186": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    },
    "NCT02417064": {
      "analysis_set_literal": "observed-case Day-28 full analysis set",
      "endpoint_event_time": "DAY28_CHANGE_FROM_BASELINE"
    }
  }
}
```

Title:

> Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis

Description:

> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement.

Time frame:

> Baseline up to Endpoint (Double-blind Induction Phase[Day 28])

Population:

> The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.

Served numeric source:

> ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery Asberg Depression Rating Scale (MAD' mean -10.0 (SD 12.74, n=63) [Intranasal Esketamine ] vs -6.3 (SD 8.86, n=60) [Oral AD Plus Intranasa] Units on a scale — population: The full analysis set (FAS) was defined as all randomized participants who recei

MADRS change from baseline to Day 28 is explicitly named. Observed-case raw change-score handling is not explicit in the title/description. MEAN/Standard Deviation cells support raw summaries but do not independently prove observed-case handling. The title says MMRM analysis; neither certify observed-case identity nor assume the extracted mean/SD cells themselves are model-adjusted from that title.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 3 to 2; withdraw multi-study pool: False.

### 4. melatonin-primary-insomnia-sol / PMID 20712869 / Sleep-onset latency

Primary: True. Reading: **MATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: True.

Held: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0`. Served: `docs/reviews/melatonin-primary-insomnia-sol/review.json#/outcomes/0/trials/0`.

Declared spec:

```json
{
  "name": "Sleep-onset latency",
  "keywords": [
    "sleep onset latency",
    "sleep-onset latency",
    "sleep latency",
    "latency to sleep onset",
    "polysomnographic sleep latency",
    "subjective sleep latency",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "MD",
  "population": "pre-specified age 65-80 ITT subgroup (of an 18-80 enrolment)",
  "timepoint": "end of treatment",
  "trial_annotations": {
    "20712869": {
      "evidence_unit": "prespecified_subgroup",
      "evidence_unit_detail": "age 65-80 ITT subgroup"
    }
  }
}
```

Title:

> The Change From Baseline in Subjective Sleep Latency.

Description:

> Sleep latency (SL) after 3 weeks of treatment was assessed by Patient Daily Sleep Diary (National sleep foundation sleep diary). The patients reported subjectively of their SL. The Sleep Diary question 3 (SL) was summarised at baseline (end of the two-week run-in period) and after three weeks double-blind treatment (actual and change from baseline) for each treatment group using descriptive statistics. At each visit, the mean of the seven days prior to the visit were used. For each treatment group, the mean score at visit 3 was compared, adjusting for the visit 2 score. An ANCOVA model was used. Lower score indicates reduction in sleep latency and thus considered improvement

Time frame:

> Baseline and 3 weeks

Population:

> Pre-planned analysis on ITT population age 65-80

Served numeric source:

> ClinicalTrials.gov results (structured, continuous): outcome 'The Change From Baseline in Subjective Sleep Latency.' mean -19.1 (SD 47.3, n=137) [Circadin] vs -1.7 (SD 47.8, n=144) [Placebo] minutes — population: Pre-planned analysis on ITT population age 65-80

Subjective sleep latency names time to sleep onset by ordinary reading. Description places it after three weeks of double-blind treatment; population explicitly names the pre-planned ITT age 65-80 subgroup. This is semantic interpretation, not treating retrieval keywords as formal synonyms.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

### 5. omega3-cardiovascular-events / PMID 33190147 / Major vascular events / MACE

Primary: True. Reading: **MISMATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT02104817/2`. Served: `docs/reviews/omega3-cardiovascular-events/review.json#/outcomes/0/trials/0`.

Declared spec:

```json
{
  "name": "Major vascular events / MACE",
  "keywords": [
    "major vascular event",
    "major vascular events",
    "major cardiovascular event",
    "major cardiovascular events",
    "major adverse cardiovascular event",
    "major adverse cardiovascular events",
    "MACE",
    "serious vascular event",
    "serious vascular events",
    "primary end point event",
    "primary end-point event",
    "primary endpoint event",
    "primary outcome",
    "primary end point",
    "primary endpoint"
  ],
  "estimand": "RR",
  "population": "intention-to-treat",
  "timepoint": "trial end / longest randomized follow-up",
  "trial_annotations": {
    "33190147": {
      "components": [
        "cardiovascular death",
        "nonfatal myocardial infarction",
        "nonfatal stroke",
        "coronary revascularization",
        "unstable angina requiring hospitalization"
      ]
    },
    "30415637": {
      "components": [
        "myocardial infarction",
        "stroke",
        "death from cardiovascular causes"
      ]
    },
    "30415628": {
      "components": [
        "cardiovascular death",
        "nonfatal myocardial infarction",
        "nonfatal stroke",
        "coronary revascularization",
        "unstable angina"
      ]
    },
    "30146932": {
      "components": [
        "nonfatal myocardial infarction",
        "stroke",
        "transient ischemic attack",
        "vascular death excluding confirmed intracranial hemorrhage"
      ]
    },
    "20929341": {
      "components": [
        "fatal cardiovascular events",
        "nonfatal cardiovascular events",
        "cardiac interventions"
      ]
    },
    "21115589": {
      "components": [
        "non-fatal myocardial infarction",
        "stroke",
        "death from cardiovascular disease"
      ]
    }
  }
}
```

Title:

> The Composite of CV Events

Description:

> CV events include: cardiovascular (CV) death, non-fatal myocardial infarction (MI) and non-fatal stroke. Participants with no observed events are censored at the earliest of withdrawal of consent date and last study contact (defined as the latest of the dates of assessments contributing to an opportunity to assess as to whether the participant has had every component of the endpoint being analyzed).

Time frame:

> From the date of randomization and up to completion of the end-of-treatment visit (Month 60) or at study closure

Population:

> Full Analysis Set

Served numeric source:

> ClinicalTrials.gov results (structured target endpoint): outcome 'The Composite of CV Events' HR 1.05 (95% CI 0.93 to 1.19); endpoint counts 541/6539 (Epanova) vs 517/6539 (Placebo)

The located measure omits coronary revascularization and unstable-angina hospitalization, explicitly included in this trial-specific declared component annotation. The follow-up is compatible with the declared trial-end/longest follow-up; the mismatch is components.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 5 to 4; withdraw multi-study pool: False.

### 6. omega3-cardiovascular-events / PMID 30415628 / Major vascular events / MACE

Primary: True. Reading: **MISMATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT01492361/1`. Served: `docs/reviews/omega3-cardiovascular-events/review.json#/outcomes/0/trials/2`.

Declared spec:

```json
{
  "name": "Major vascular events / MACE",
  "keywords": [
    "major vascular event",
    "major vascular events",
    "major cardiovascular event",
    "major cardiovascular events",
    "major adverse cardiovascular event",
    "major adverse cardiovascular events",
    "MACE",
    "serious vascular event",
    "serious vascular events",
    "primary end point event",
    "primary end-point event",
    "primary endpoint event",
    "primary outcome",
    "primary end point",
    "primary endpoint"
  ],
  "estimand": "RR",
  "population": "intention-to-treat",
  "timepoint": "trial end / longest randomized follow-up",
  "trial_annotations": {
    "33190147": {
      "components": [
        "cardiovascular death",
        "nonfatal myocardial infarction",
        "nonfatal stroke",
        "coronary revascularization",
        "unstable angina requiring hospitalization"
      ]
    },
    "30415637": {
      "components": [
        "myocardial infarction",
        "stroke",
        "death from cardiovascular causes"
      ]
    },
    "30415628": {
      "components": [
        "cardiovascular death",
        "nonfatal myocardial infarction",
        "nonfatal stroke",
        "coronary revascularization",
        "unstable angina"
      ]
    },
    "30146932": {
      "components": [
        "nonfatal myocardial infarction",
        "stroke",
        "transient ischemic attack",
        "vascular death excluding confirmed intracranial hemorrhage"
      ]
    },
    "20929341": {
      "components": [
        "fatal cardiovascular events",
        "nonfatal cardiovascular events",
        "cardiac interventions"
      ]
    },
    "21115589": {
      "components": [
        "non-fatal myocardial infarction",
        "stroke",
        "death from cardiovascular disease"
      ]
    }
  }
}
```

Title:

> Composite of CV Death, Nonfatal MI (Including Silent MI), or Nonfatal Stroke.

Description:

> The key secondary outcome measure was the number of patients with a first occurrence of any component of the composite of CV death, nonfatal MI (including silent MI), or nonfatal stroke during the follow-up period.

Time frame:

> Total follow-up time of up to approximately 6 years.

Population:

> [absent]

Served numeric source:

> ClinicalTrials.gov results (structured target endpoint): outcome 'Composite of CV Death, Nonfatal MI (Including Silent MI), or Nonfatal Stroke.' HR 0.74 (95% CI 0.65 to 0.83); endpoint counts 459/4089 (AMR101) vs 606/4090 (Placebo)

The located measure omits coronary revascularization and unstable angina, explicitly included in this trial-specific declared component annotation. The follow-up is compatible with the declared trial-end/longest follow-up; the mismatch is components.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 5 to 4; withdraw multi-study pool: False.

### 7. omega3-cardiovascular-events / PMID 30146932 / Atrial fibrillation

Primary: False. Reading: **MATCH**. Instrument: **EXACT_TARGET**. Disagreement: False.

Held: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22`. Served: `docs/reviews/omega3-cardiovascular-events/review.json#/outcomes/1/trials/0`.

Declared spec:

```json
{
  "name": "Atrial fibrillation",
  "keywords": [
    "atrial fibrillation",
    "atrial flutter",
    "new-onset atrial fibrillation",
    "incident atrial fibrillation"
  ],
  "estimand": "RR"
}
```

Title:

> Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only)

Description:

> Includes fatal and non-fatal events.

Time frame:

> Randomized treatment phase during a mean of 7.4 years

Population:

> [absent]

Served numeric source:

> ClinicalTrials.gov results (structured): outcome 'Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only)' COUNT_OF_PARTICIPANTS 166/7740 (Omega-3) vs 135/7740 (Placebo Omega-3)

Title directly names the declared harm outcome. This outcome spec supplies no timepoint restriction.

Instrument reason: registry measure: full declared outcome phrase and declared qualifiers match

### 8. pcsk9-mace / PMID 28304224 / Major adverse cardiovascular events

Primary: True. Reading: **MISMATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/pcsk9-mace/records.json#/ctgov_results/NCT01764633/1`. Served: `docs/reviews/pcsk9-mace/review.json#/outcomes/0/trials/0`.

Declared spec:

```json
{
  "name": "Major adverse cardiovascular events",
  "keywords": [
    "major adverse cardiovascular events",
    "MACE",
    "primary outcome",
    "primary end point",
    "primary endpoint",
    "primary efficacy end point",
    "risk of the primary end point",
    "primary end-point event",
    "composite primary end-point",
    "cardiovascular death",
    "myocardial infarction",
    "stroke",
    "unstable angina"
  ],
  "estimand": "HR",
  "population": "intention-to-treat",
  "timepoint": "longest reported trial follow-up",
  "trial_annotations": {
    "28304224": {
      "endpoint_definition": "CV_DEATH | MI | STROKE | UNSTABLE_ANGINA_HOSPITALIZATION | CORONARY_REVASCULARIZATION",
      "components": [
        "CV_DEATH",
        "MI",
        "STROKE",
        "UA_HOSP",
        "CORONARY_REVASCULARIZATION"
      ]
    },
    "30403574": {
      "endpoint_definition": "CHD_DEATH | MI | ISCHEMIC_STROKE | UNSTABLE_ANGINA_HOSPITALIZATION",
      "components": [
        "CHD_DEATH",
        "MI",
        "ISCHEMIC_STROKE",
        "UA_HOSP"
      ]
    },
    "41211925": {
      "components": [
        "CHD_DEATH",
        "MI",
        "ISCHEMIC_STROKE"
      ],
      "co_primary_selected": "3-point MACE: death from coronary heart disease, myocardial infarction, or ischemic stroke",
      "co_primary_selection_rule": "Selected by the 2026-09-16 protocol amendment: prespecified co-primary closest to canonical 3-point MACE; alternative 4-point co-primary rendered as sensitivity."
    }
  },
  "component_compat_key": true
}
```

Title:

> Time to Cardiovascular Death, Myocardial Infarction, or Stroke

Description:

> All deaths and potential endpoint events were adjudicated by an independent external CEC led by the TIMI Study Group, using standardized definitions based on the "Standardized Definitions for Cardiovascular and Stroke End Point Events in Clinical Trials and the Third Universal Definition of Myocardial Infarction". Time to cardiovascular death, myocardial infarction, or stroke was defined as the time from randomization to the first occurrence of any component of the composite endpoint and was analyzed using Kaplan-Meier (KM) survival analysis. KM estimates of the percentage of participants with an event are reported. Participants with no event were censored based on last non-fatal potential endpoint collection date.

Time frame:

> Events that occurred from randomization to the last confirmed survival status date; the median duration of follow-up was 26 months. KM estimates at 6, 12, 18, 24, 30 and 36 months are reported.

Population:

> All randomized participants; The number of participants entered at each time point represents the number of participants at risk.

Served numeric source:

> ClinicalTrials.gov results (structured target endpoint): outcome 'Time to Cardiovascular Death, Myocardial Infarction, or Stroke' HR 0.8 (95% CI 0.73 to 0.88)

The located measure omits unstable-angina hospitalization and coronary revascularization, explicitly included in this trial-specific declared component annotation. The follow-up is compatible with the declared trial-end/longest follow-up; the mismatch is components.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 2 to 1; withdraw multi-study pool: True.

### 9. sacubitril-valsartan-hfref / NCT02468232 / Composite cardiovascular death or heart-failure hospitalization

Primary: True. Reading: **MATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: True.

Held: `cache/sacubitril-valsartan-hfref/records.json#/ctgov_results/NCT02468232/1`. Served: `docs/reviews/sacubitril-valsartan-hfref/review.json#/outcomes/0/trials/1`.

Declared spec:

```json
{
  "name": "Composite cardiovascular death or heart-failure hospitalization",
  "components": [
    "cardiovascular death",
    "heart failure hospitalization"
  ],
  "keywords": [
    "death from cardiovascular causes or hospitalization for heart failure",
    "cardiovascular death or hospitalization for heart failure",
    "cardiovascular death or hospitalisation for heart failure",
    "cardiovascular death or heart-failure hospitalization",
    "cardiovascular death or heart failure hospitalization",
    "cardiovascular (CV) death or heart failure (HF) hospitalization",
    "composite of death from cardiovascular causes or hospitalization for heart failure",
    "primary composite outcome",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "HR",
  "population": "intention-to-treat",
  "timepoint": "trial end / longest randomized follow-up"
}
```

Title:

> Exposure-adjusted Incident Rate (EAIR) of CEC Confirmed Composite Endpoints

Description:

> Composite endpoint is defined as either cardiovascular (CV) death or heart failure (HF) hospitalization in Japanese patients with chronic heart failure (CHF) and reduced ejection fraction. EAIR = n/T where n = Total number of events included in the analysis. T (100 patient years) = total up-to-event/censoring duration-time summarized over participants in the respective treatment group. The composite endpoint events occurred on and after EOS declaration were reported by investigators but those events were not required to be adjudicated by CEC and not included in the efficacy analysis.

Time frame:

> up to 40 months

Population:

> FAS consists of all randomized patients with the exception for those patients who have not been qualified for randomization and have not received investigational drug, but have been inadvertently randomized into the study.

Served numeric source:

> ClinicalTrials.gov results (structured target endpoint): outcome 'Exposure-adjusted Incident Rate (EAIR) of CEC Confirmed Composite Endpoints' HR 1.0881 (95% CI 0.6501 to 1.8212)

Description explicitly defines cardiovascular (CV) death or heart failure (HF) hospitalization: the two declared components through trial follow-up (up to 40 months). Abbreviations interrupt literal phrasing, not meaning. EAIR/estimand and FAS exclusions are separate qualifications, not a different clinical outcome.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

### 10. semaglutide-obesity-weight / PMID 33625476 / Percent change in body weight

Primary: True. Reading: **MATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: True.

Held: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0`. Served: `docs/reviews/semaglutide-obesity-weight/review.json#/outcomes/0/trials/0`.

Declared spec:

```json
{
  "name": "Percent change in body weight",
  "keywords": [
    "change in body weight (%)",
    "percent change in body weight",
    "percentage change in body weight",
    "change in body weight",
    "body weight",
    "percent weight change",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "MD",
  "population": "in-trial / treatment-policy estimand (all randomized), baseline to Week 68",
  "timepoint": "Week 68",
  "timepoint_weeks": 68,
  "timepoint_tolerance_weeks": 8,
  "trial_annotations": {
    "33625476": {
      "background_lifestyle_intensity": "INTENSIVE_BEHAVIORAL_THERAPY_30_VISITS_LOW_CALORIE_DIET"
    },
    "33567185": {
      "background_lifestyle_intensity": "STANDARD_LIFESTYLE_INTERVENTION_STEP1"
    }
  }
}
```

Title:

> Change in Body Weight (%)

Description:

> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period).

Time frame:

> Baseline (week 0) to week 68

Population:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

Served numeric source:

> ClinicalTrials.gov results (structured, continuous): outcome 'Change in Body Weight (%)' mean -16.5 (SD 10.1, n=407) [Semaglutide 2.4 mg] vs -5.8 (SD 7.7, n=204) [Placebo] Percentage — population: Overall number of participants analyzed = full analysis set (FAS) which comprise

Change in Body Weight (%) names percent change in body weight, at baseline to week 68. Both in-trial and on-treatment periods are described; the extracted first class is in-trial. Identity matching does not validate the extractor using overall rather than class-specific denominators.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

### 11. semaglutide-obesity-weight / PMID 33567185 / Percent change in body weight

Primary: True. Reading: **MATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: True.

Held: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0`. Served: `docs/reviews/semaglutide-obesity-weight/review.json#/outcomes/0/trials/1`.

Declared spec:

```json
{
  "name": "Percent change in body weight",
  "keywords": [
    "change in body weight (%)",
    "percent change in body weight",
    "percentage change in body weight",
    "change in body weight",
    "body weight",
    "percent weight change",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "MD",
  "population": "in-trial / treatment-policy estimand (all randomized), baseline to Week 68",
  "timepoint": "Week 68",
  "timepoint_weeks": 68,
  "timepoint_tolerance_weeks": 8,
  "trial_annotations": {
    "33625476": {
      "background_lifestyle_intensity": "INTENSIVE_BEHAVIORAL_THERAPY_30_VISITS_LOW_CALORIE_DIET"
    },
    "33567185": {
      "background_lifestyle_intensity": "STANDARD_LIFESTYLE_INTERVENTION_STEP1"
    }
  }
}
```

Title:

> Change in Body Weight (%)

Description:

> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period).

Time frame:

> Baseline (week 0) to week 68

Population:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

Served numeric source:

> ClinicalTrials.gov results (structured, continuous): outcome 'Change in Body Weight (%)' mean -15.6 (SD 10.1, n=1306) [Semaglutide 2.4 mg] vs -2.8 (SD 6.5, n=655) [Placebo] Percentage point — population: Overall number of participants analyzed = full analysis set (FAS) which comprise

Change in Body Weight (%) names percent change in body weight, at baseline to week 68. Both in-trial and on-treatment periods are described; the extracted first class is in-trial. Identity matching does not validate the extractor using overall rather than class-specific denominators.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

### 12. sglt2-hfref-hosp-cvdeath / PMID 31535829 / Composite cardiovascular death or hospitalisation for heart failure

Primary: True. Reading: **MISMATCH**. Instrument: **ENDPOINT_UNBOUND**. Disagreement: False.

Held: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1`. Served: `docs/reviews/sglt2-hfref-hosp-cvdeath/review.json#/outcomes/0/trials/0`.

Declared spec:

```json
{
  "name": "Composite cardiovascular death or hospitalisation for heart failure",
  "keywords": [
    "cardiovascular death or hospitalization for heart failure",
    "cardiovascular death or hospitalisation for heart failure",
    "cardiovascular death or hospitalization",
    "cardiovascular death or hospitalisation",
    "worsening heart failure or cardiovascular death",
    "cardiovascular death or worsening heart failure",
    "primary outcome",
    "primary endpoint",
    "primary end point"
  ],
  "estimand": "RR",
  "population": "intention-to-treat",
  "timepoint": "trial end",
  "trial_annotations": {
    "31535829": {
      "components": [
        "worsening heart failure hospitalization",
        "urgent visit requiring intravenous therapy for heart failure",
        "cardiovascular death"
      ]
    },
    "32865377": {
      "components": [
        "cardiovascular death",
        "hospitalization for worsening heart failure"
      ]
    }
  }
}
```

Title:

> Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure.

Description:

> Secondary

Time frame:

> Up to 27.8 months.

Population:

> [absent]

Served numeric source:

> ClinicalTrials.gov results (structured target endpoint): outcome 'Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure.' HR 0.75 (95% CI 0.65 to 0.85); endpoint counts 382/2373 (Dapa 10 mg) vs 495/2371 (Placebo)

The located measure omits urgent HF visits requiring intravenous therapy, explicitly included in this trial-specific declared component annotation. The follow-up is compatible with the declared trial-end/longest follow-up; the mismatch is components. It matches the generic review outcome name but not the full trial-specific annotation. The broader measure is index 0 (HR 0.74); served index 1 supplies HR 0.75.

Instrument reason: registry measure: no full declared outcome phrase in this measure's title/description

Individual removal: k 2 to 1; withdraw multi-study pool: True.

### 13. ticagrelor-vs-clopidogrel-acs / PMID 19717846 / Major bleeding

Primary: False. Reading: **MATCH**. Instrument: **EXACT_TARGET**. Disagreement: False.

Held: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/ctgov_results/NCT00391872/1`. Served: `docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json#/outcomes/1/trials/0`.

Declared spec:

```json
{
  "name": "Major bleeding",
  "keywords": [
    "major bleeding",
    "PLATO major bleeding",
    "TIMI major bleeding",
    "primary safety outcome",
    "primary safety endpoint"
  ],
  "estimand": "RR"
}
```

Title:

> Participants With Any Major Bleeding Event

Description:

> Participants with major (fatal/life-threatening or other) bleed by a study protocol scale based on need for treatment, number of transfusions, hemoglobin decrease, and other factors. Events were adjudicated by an endpoint committee.

Time frame:

> First dosing up to 12 months

Population:

> The population was the safety analysis set, which included all randomized patients who took at least one dose of study drug

Served numeric source:

> ClinicalTrials.gov results (structured): outcome 'Participants With Any Major Bleeding Event' COUNT_OF_PARTICIPANTS 961/9235 (TICAGRELOR) vs 929/9186 (CLOPIDOGREL)

Title directly names the declared harm outcome. This outcome spec supplies no timepoint restriction.

Instrument reason: registry measure: full declared outcome phrase and declared qualifiers match

The two `aact_verified` rows (probiotics PMIDs 15740542 and 18026577) also originate in quoted abstract counts, not a held CT.gov outcome measure; their labels do not add registry-route rows.

## Verification

Pinned row pointers, specs, primary flags, measure quotes, complete reconstructed tuples/source strings, and numbered effect/CI matches were checked. All 13 measures located. JSON and Markdown totals agree. UTF-8 without BOM. This is an identity audit, not certification of extraction arithmetic; semaglutide overall versus class-specific denominators remain a separate issue.

Final report validation: **PASS** for all 13 pinned row/measure/spec comparisons, reconstruction source/tuple matches, numbered effect matches, classifier rerun equality, totals and UTF-8 checks. `git diff --check`: PASS. Harness/tests diff: empty. No tests were added or changed.
