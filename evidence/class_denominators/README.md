# Registry class denominators

Measured at `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`, before changing the readers. Both cache records and served reviews were read with `git show`; no live registry calls or regenerated reviews enter this census.

**93 of 1,684 outcome-measure occurrences across all 32 topics** have different denominators in a selected class. Occurrences are counted per topic/NCT/measure index (the same registry measure cached in two topics counts twice). **3 of 127 served trial rows** reference an affected measure: STEP 1, STEP 3, and FOURIER. **0 of 35 served rows with binary count inputs** have an affected selected measure; **2 of 6 continuous rows** have wrong n. FOURIER is one of 86 reported-effect rows: its HR has no denominator input, but its served second-source text has the wrong n.

## Scope and reproducibility

Run `python evidence/class_denominators/measure.py` from this checkout to regenerate [measurement.json](measurement.json). Missing pinned files fail rather than skip. The topic universe is the 32 pinned `docs/reviews/*/review.json` files. Every `ctgov_results` outcome measure in those topics is inspected, including irrelevant/off-topic cached trials. Such a cache occurrence does not establish eligibility.

The direct binary/continuous readers, typed continuous reader and target-endpoint reader select class 0/category 0. The consumer consistency reader selects the first category with measurements, potentially in a later class. The census takes the union of those selected classes, independently of endpoint eligibility; it does not count differences confined to unselected later classes. All 93 mismatches here are class 0. Counts are joined by groupId, not array position. Served trial objects are searched recursively for exact registry titles and the readers' quoted title spans, with NCT identity checked against the row. This includes harms, nested cross-source panels and target-endpoint alternatives; alternatives are disclosed separately, not counted as additional pooled rows.

| Input/choice | Static or dynamic | Evidence / transformation |
|---|---|---|
| Pinned commit and class-selection rules | Static | Explicit audit scope; mirrors inspected reader code |
| Topic universe, identifiers, titles, denominators, served rows | Dynamic | `git ls-tree` / `git show`; raw groupId counts numerically compared |
| Counts and inventories below | Derived | Full census in measurement.json; no inferred trial IDs or research outputs |
| Test counts and synthetic arms | Static plants | Deliberately artificial test inputs, never served research data |

## Every affected served row

All n pairs in this table are intervention/comparator, validated against the cached group titles.

| Topic / trial / source identifier | Selected measure / class | Pinned served n | Class n | Wrong? / effect of this patch |
|---|---|---|---|---|
| semaglutide-obesity-weight / STEP 1 / PMID 33567185, NCT03548935 | #0 Change in Body Weight (%) / In-trial observation period | 1306 / 655 | 1212 / 577 | Yes, continuous input. Already corrected by the preceding continuous-identity implementation; retained here. Analysis-set n remains 1306 / 655. |
| semaglutide-obesity-weight / STEP 3 / PMID 33625476, NCT03611582 | #0 Change in Body Weight (%) / In-trial observation period | 407 / 204 | 373 / 189 | Yes, continuous input. Already corrected by the preceding continuous-identity implementation; retained here. Analysis-set n remains 407 / 204. |
| pcsk9-mace / FOURIER / PMID 28304224, NCT01764633 | #1 Time to Cardiovascular Death, Myocardial Infarction, or Stroke / KM estimate at 6 months | No n in pooled HR; cross_source.ctgov_source says 13784 / 13780 | 13499 / 13447 | Yes in the second-source text; this patch corrects it and retains analysis-set n. HR 0.80 (0.73 to 0.88), KM values 1.65 / 1.86, and their ratio remain unchanged. No binary reconstruction is introduced. |

FOURIER also lists four affected, unselected target-endpoint alternatives: #2 **Time to Cardiovascular Death**; #0 **Time to Cardiovascular Death, Myocardial Infarction, Hospitalization for Unstable Angina, Stroke, or Coronary Revascularization**; #4 **Time to First Myocardial Infarction**; #5 **Time to First Stroke**. These alternative summaries carry no n and therefore contain no wrong denominator. The complete paths and source text of all eight matching objects (three selected trial objects, one cross-source object and four alternatives) are in measurement.json.

The earlier statement that FOURIER's n is unused applies to its pooled HR only. It misses the wrong count displayed in its second-source evidence. No served review or HTML has been rebuilt in this task.

## Route changes

- `ctgov_results.extract_ctgov`: count values, denominator units, range checks, enrollment floor and implied effect all use the selected class denominators. Measure-level n is retained as `n_analysis_set` when a class block exists.
- `target_endpoint._counts_from_om` / `_ctgov_candidates` / `row_from_candidate`: same rule for reconstructed rows and endpoint counts accompanying reported effects, with analysis-set metadata retained.
- `consumer_consistency._ctgov_continuous_candidate`: denominator follows the actual first nonempty class rather than an assumed class 0.
- `continuous_identity.typed_measure` and the existing continuous extractor: class blocks replace rather than merge/fall back to measure counts when an arm is missing; the STEP 1 contract remains intact.
- Harms use `pipeline._build_outcome` and the shared extractors. `harms.py` does not read registry denominators. Second-source extraction uses `pipeline._cross_source` -> `extract_ctgov`; `second_source.py` classifies identity, rather than reading denominators. The cross-source row now retains analysis-set metadata. Both indirect routes have integration plants.
- No class denominator block: existing denominator values, source strings and row shape are preserved. A partial nonempty class block never borrows a missing arm from the analysis set.

## Topic coverage

| Topic | Affected / cached measures | Served trial rows |
|---|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 0 / 26 | 3 |
| colchicine-postop-af | 0 / 0 | 3 |
| colchicine-recurrent-pericarditis | 0 / 0 | 3 |
| colchicine-secondary-cv-prevention | 0 / 0 | 5 |
| corticosteroids-cap-mortality | 3 / 21 | 6 |
| corticosteroids-covid19-mortality | 0 / 0 | 2 |
| dapagliflozin-hfpef-hosp | 0 / 37 | 1 |
| denosumab-vertebral-fracture | 14 / 100 | 3 |
| doac-vte-recurrence | 0 / 0 | 13 |
| dpp4-mace-t2d | 0 / 0 | 6 |
| empagliflozin-hfpef-hosp | 0 / 35 | 0 |
| esketamine-trd-madrs | 22 / 164 | 4 |
| finerenone-ckd-t2d-renal | 0 / 0 | 2 |
| glp1-ra-mace-t2d | 0 / 0 | 10 |
| iv-iron-hfref-hosp | 3 / 15 | 2 |
| melatonin-primary-insomnia-sol | 0 / 26 | 2 |
| metformin-pcos-ovulation | 0 / 8 | 3 |
| noac-vs-warfarin-af-stroke | 0 / 0 | 6 |
| omega3-cardiovascular-events | 3 / 172 | 6 |
| pcsk9-mace | 11 / 30 | 2 |
| probiotics-aad-prevention | 0 / 0 | 14 |
| sacubitril-valsartan-hfref | 24 / 303 | 2 |
| semaglutide-obesity-mace | 1 / 45 | 2 |
| semaglutide-obesity-weight | 12 / 619 | 2 |
| sglt2-ckd-progression | 0 / 0 | 5 |
| sglt2-hfref-hosp-cvdeath | 0 / 23 | 2 |
| sglt2-primary-prevention-hf | 0 / 0 | 5 |
| spironolactone-hfref-mortality | 0 / 26 | 3 |
| statins-primary-prevention-elderly | 0 / 0 | 2 |
| ticagrelor-vs-clopidogrel-acs | 0 / 34 | 4 |
| tocilizumab-covid19-mortality | 0 / 0 | 3 |
| tranexamic-acid-pph | 0 / 0 | 1 |

## Every affected cached measure

Indices are zero-based, as in the source arrays. Each denominator map is keyed by registry groupId; group titles are preserved in measurement.json. A zero is the source count, not a missing value.

| Topic / NCT / measure index | Outcome measure (paramType) | Selected class | Measure n -> class n |
|---|---|---|---|
| corticosteroids-cap-mortality / NCT04988087 / #9 | SjS Participants: Change From Baseline to the Salivary Flow Rate (MEAN) | #0 Week 4 | OG000=12, OG001=14 -> OG000=8, OG001=12 |
| corticosteroids-cap-mortality / NCT04988087 / #10 | SjS Participants: Change From Baseline to the Schirmer's Test (MEAN) | #0 Week 4, right eye | OG000=12, OG001=14 -> OG000=8, OG001=12 |
| corticosteroids-cap-mortality / NCT04988087 / #19 | MCTD Participants: Change From Baseline in Raynaud's Condition Score (RCS) (MEAN) | #0 Week 4 | OG000=2, OG001=2 -> OG000=2, OG001=1 |
| denosumab-vertebral-fracture / NCT03164928 / #1 | Change From Baseline in Lumbar Spine BMD Z-score as Assessed by DXA at 6, 18, 24, and 36 Months (LEAST_SQUARES_MEAN) | #0 Month 6 | OG000=15, OG001=8 -> OG000=14, OG001=6 |
| denosumab-vertebral-fracture / NCT03164928 / #2 | Change From Baseline in Proximal Femur BMD Z-score as Assessed by DXA at 6, 12, 18, 24, and 36 Months (LEAST_SQUARES_MEAN) | #0 Month 6 (Total Hip) | OG000=15, OG001=7 -> OG000=13, OG001=5 |
| denosumab-vertebral-fracture / NCT03164928 / #6 | Change From Baseline in Child Health Questionnaire-Parent Form-50 (CHQ-PF-50) Physical Summary Score at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=14, OG001=7 -> OG000=12, OG001=7 |
| denosumab-vertebral-fracture / NCT03164928 / #7 | Change From Baseline in CHQ-PF-50 Psychological Summary Score at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=14, OG001=7 -> OG000=12, OG001=7 |
| denosumab-vertebral-fracture / NCT03164928 / #8 | Change From Baseline in Childhood Health Assessment Questionnaire (CHAQ) Disability Index Score at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=14, OG001=7 -> OG000=12, OG001=7 |
| denosumab-vertebral-fracture / NCT03164928 / #9 | Change From Baseline in Wong-Baker FACES Pain Rating Scale (WBFPRS) at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=14, OG001=7 -> OG000=11, OG001=7 |
| denosumab-vertebral-fracture / NCT03164928 / #10 | Change From Baseline in Growth Velocity Z-score (Height) at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=15, OG001=8 -> OG000=13, OG001=8 |
| denosumab-vertebral-fracture / NCT03164928 / #11 | Change From Baseline in Growth Velocity Z-score (Weight) at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=16, OG001=8 -> OG000=15, OG001=8 |
| denosumab-vertebral-fracture / NCT03164928 / #12 | Change From Baseline in Growth Velocity Z-score (BMI) at 12, 24, and 36 Months (MEAN) | #0 Month 12 | OG000=15, OG001=8 -> OG000=13, OG001=8 |
| denosumab-vertebral-fracture / NCT03164928 / #13 | Mean Serum Concentration of Denosumab (MEAN) | #0 Day 1 | OG000=15, OG001=8 -> OG000=14, OG001=0 |
| denosumab-vertebral-fracture / NCT00896532 / #7 | Percent Change From Baseline in Procollagen Type 1 N-telopeptide (P1NP) (LEAST_SQUARES_MEAN) | #0 Month 1 | OG000=50, OG001=51, OG002=49, OG003=49, OG004=53, OG005=48, OG006=53, OG007=50 -> OG000=50, OG001=0, OG002=0, OG003=49, OG004=52, OG005=48, OG006=52, OG007=50 |
| denosumab-vertebral-fracture / NCT00896532 / #8 | Percent Change From Baseline in Type 1 Collagen C-telopeptide (CTX) (LEAST_SQUARES_MEAN) | #0 Month 1 | OG000=50, OG001=51, OG002=49, OG003=49, OG004=53, OG005=48, OG006=53, OG007=50 -> OG000=50, OG001=0, OG002=0, OG003=49, OG004=51, OG005=48, OG006=52, OG007=50 |
| denosumab-vertebral-fracture / NCT00896532 / #9 | Percent Change From Baseline in Osteocalcin (LEAST_SQUARES_MEAN) | #0 Month 1 | OG000=50, OG001=51, OG002=49, OG003=49, OG004=53, OG005=48, OG006=53, OG007=50 -> OG000=50, OG001=0, OG002=0, OG003=49, OG004=52, OG005=48, OG006=52, OG007=50 |
| denosumab-vertebral-fracture / NCT00896532 / #10 | Percent Change From Baseline in Bone-specific Alkaline Phosphatase (BSAP) (LEAST_SQUARES_MEAN) | #0 Month 1 | OG000=50, OG001=51, OG002=49, OG003=49, OG004=53, OG005=48, OG006=53, OG007=50 -> OG000=50, OG001=0, OG002=0, OG003=49, OG004=52, OG005=48, OG006=52, OG007=50 |
| esketamine-trd-madrs / NCT02918318 / #1 | DB Induction Phase: Percentage of Participants With Response Based on MADRS Total Score (NUMBER) | #0 Day 2 | OG000=41, OG001=40, OG002=41, OG003=80 -> OG000=41, OG001=38, OG002=40, OG003=79 |
| esketamine-trd-madrs / NCT02918318 / #2 | DB Induction Phase: Percentage of Participants With Remission Based on MADRS Total Score (NUMBER) | #0 Day 2 | OG000=41, OG001=40, OG002=41, OG003=80 -> OG000=41, OG001=38, OG002=40, OG003=78 |
| esketamine-trd-madrs / NCT04829318 / #14 | Change From Baseline of Study 54135419TRD3013 in European Quality of Life (EuroQol) 5 Dimension 5-Level (EQ-5D-5L): Health Status Index (MEAN) | #0 Week 4 | OG000=178 -> OG000=177 |
| esketamine-trd-madrs / NCT04829318 / #15 | Change From Baseline of Study 54135419TRD3013 in European Quality of Life (EuroQol) 5 Dimension 5-Level (EQ-5D-5L): Visual Analogue Scale (VAS) (MEAN) | #0 Week 4 | OG000=175 -> OG000=174 |
| esketamine-trd-madrs / NCT04338321 / #2 | Change From Baseline in Clinician-rated Overall MADRS Score (MEAN) | #0 Week 1 | OG000=327, OG001=330 -> OG000=325, OG001=326 |
| esketamine-trd-madrs / NCT04338321 / #4 | Change From Baseline in Clinician-rated Overall Severity of Depressive Illness as Assessed by Clinical Global Impression - Severity (CGI-S) Scale Score (MEAN) | #0 Week 1 | OG000=327, OG001=331 -> OG000=326, OG001=327 |
| esketamine-trd-madrs / NCT04338321 / #6 | Clinician-rated Overall Severity of Depressive Illness as Assessed by Clinical Global Impression - Change (CGI-C) Scale Score (MEAN) | #0 Week 1 | OG000=327, OG001=331 -> OG000=326, OG001=327 |
| esketamine-trd-madrs / NCT04338321 / #8 | Change From Baseline in Participant-reported Depressive Symptoms as Assessed by Patient Health Questionnaire (PHQ) 9-item Total Score (MEAN) | #0 Week 2 | OG000=322, OG001=316 -> OG000=319, OG001=310 |
| esketamine-trd-madrs / NCT04338321 / #9 | Change From Baseline in Participant-reported Depressive Symptoms as Assessed by PHQ 9-item Total Score at LOCF (MEAN) | #0 Week 2 | OG000=322, OG001=316 -> OG000=319, OG001=310 |
| esketamine-trd-madrs / NCT04338321 / #10 | Change From Baseline in Participant-reported Functional Impairment and Associated Disability as Assessed by Sheehan Disability Scale (SDS) Total Score (MEAN) | #0 Week 4 | OG000=310, OG001=303 -> OG000=307, OG001=298 |
| esketamine-trd-madrs / NCT04338321 / #11 | Change From Baseline in Participant-reported Functional Impairment and Associated Disability as Assessed by SDS Total Score at LOCF (MEAN) | #0 Week 4 | OG000=310, OG001=303 -> OG000=307, OG001=298 |
| esketamine-trd-madrs / NCT04338321 / #12 | Change From Baseline in Participant-reported Health-related Quality of Life (HRQoL) and Health Status as Assessed by 36-item Short-Form Health Survey (SF-36) Scale Score (MEAN) | #0 Physical Functioning Week 4 | OG000=319, OG001=308 -> OG000=310, OG001=295 |
| esketamine-trd-madrs / NCT04338321 / #13 | Change From Baseline in Participant-reported HRQoL and Health Status as Assessed by SF-36 Scale Score at LOCF (MEAN) | #0 Physical Functioning Week 8 | OG000=319, OG001=308 -> OG000=308, OG001=300 |
| esketamine-trd-madrs / NCT04338321 / #14 | Change From Baseline in Participant-reported Quality of Life as Assessed by Quality of Life in Depression Scale (QLDS) Total Score (MEAN) | #0 Week 4 | OG000=318, OG001=305 -> OG000=315, OG001=300 |
| esketamine-trd-madrs / NCT04338321 / #15 | Change From Baseline in Participant-reported Quality of Life as Assessed by QLDS Total Score at LOCF (MEAN) | #0 Week 4 | OG000=318, OG001=305 -> OG000=315, OG001=300 |
| esketamine-trd-madrs / NCT04338321 / #16 | Change From Baseline in Participant-reported Health-related Quality of Life as Assessed by EuroQol-5 Dimension-5 Level (EQ-5D-5L) Score: Health Status Index (MEAN) | #0 Week 4 | OG000=320, OG001=308 -> OG000=318, OG001=306 |
| esketamine-trd-madrs / NCT04338321 / #17 | Change From Baseline in Participant-reported Health-related Quality of Life Group, as Assessed by EQ-5D-5L Score: Health Status Index at LOCF (MEAN) | #0 Week 4 | OG000=320, OG001=308 -> OG000=318, OG001=306 |
| esketamine-trd-madrs / NCT04338321 / #18 | Change From Baseline in Participant-reported Health Status as Assessed by EQ-5D-5L Score: VAS (MEAN) | #0 Week 4 | OG000=318, OG001=310 -> OG000=317, OG001=308 |
| esketamine-trd-madrs / NCT04338321 / #19 | Change From Baseline in Participant-reported Health Status as Assessed by EQ-5D-5L Score: VAS at LOCF (MEAN) | #0 Week 4 | OG000=318, OG001=310 -> OG000=317, OG001=308 |
| esketamine-trd-madrs / NCT04338321 / #20 | Change From Baseline in Participant-reported Work Productivity as Assessed by Work Productivity and Activity Impairment (WPAI): Depression Questionnaire (MEAN) | #0 Absenteeism Week 4 | OG000=310, OG001=307 -> OG000=115, OG001=112 |
| esketamine-trd-madrs / NCT04338321 / #21 | Change From Baseline in Participant-reported Work Productivity as Assessed by WPAI: Depression Questionnaire at LOCF (MEAN) | #0 Absenteeism Week 4 | OG000=310, OG001=307 -> OG000=115, OG001=112 |
| esketamine-trd-madrs / NCT04338321 / #24 | Number of Participants With Suicidal Ideation or Behavior as Assessed by Columbia-Suicide Severity Rating Scale (C-SSRS) Score (COUNT_OF_PARTICIPANTS) | #0 Suicidal Ideation Week 1 | OG000=317, OG001=295 -> OG000=277, OG001=282 |
| iv-iron-hfref-hosp / NCT02937454 / #9 | Change From Baseline in NYHA Functional Class (COUNT_OF_PARTICIPANTS) | #0 Baseline | OG000=558, OG001=550 -> OG000=557, OG001=547 |
| iv-iron-hfref-hosp / NCT02937454 / #10 | Change From Baseline in the EQ-5D-5L Questionnaire Indexed Value (MEAN) | #0 Week 6 | OG000=558, OG001=550 -> OG000=476, OG001=465 |
| iv-iron-hfref-hosp / NCT02937454 / #11 | KCCQ-12 Repeated-Measures Model for Analysis of Treatment Difference (MEAN) | #0 Week 2 | OG000=558, OG001=550 -> OG000=490, OG001=484 |
| omega3-cardiovascular-events / NCT02642159 / #20 | Absolute Change From Baseline in Hemoglobin A1c (HbA1c) at Week 12 and 24 : Overall ITT Analysis (MEAN) | #0 Change at Week 12 | OG000=273, OG001=136 -> OG000=265, OG001=133 |
| omega3-cardiovascular-events / NCT02642159 / #21 | Absolute Change From Baseline in Fasting Plasma Glucose (FPG) at Week 12 and 24 : Overall ITT Analysis (MEAN) | #0 Change at Week 12 | OG000=273, OG001=136 -> OG000=262, OG001=133 |
| omega3-cardiovascular-events / NCT02642159 / #22 | Absolute Change From Baseline in Number of Glucose-Lowering Treatments at Week 12 and 24 : Overall ITT Analysis (MEAN) | #0 Change at Week 12 | OG000=273, OG001=136 -> OG000=271, OG001=136 |
| pcsk9-mace / NCT01764633 / #0 | Time to Cardiovascular Death, Myocardial Infarction, Hospitalization for Unstable Angina, Stroke, or Coronary Revascularization (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13276, OG001=13349 |
| pcsk9-mace / NCT01764633 / #1 | Time to Cardiovascular Death, Myocardial Infarction, or Stroke (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13447, OG001=13499 |
| pcsk9-mace / NCT01764633 / #2 | Time to Cardiovascular Death (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13688, OG001=13698 |
| pcsk9-mace / NCT01764633 / #3 | Time to All Cause Death (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13688, OG001=13698 |
| pcsk9-mace / NCT01764633 / #4 | Time to First Myocardial Infarction (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13497, OG001=13536 |
| pcsk9-mace / NCT01764633 / #5 | Time to First Stroke (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13587, OG001=13631 |
| pcsk9-mace / NCT01764633 / #6 | Time to First Coronary Revascularization (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13390, OG001=13454 |
| pcsk9-mace / NCT01764633 / #7 | Time to Cardiovascular Death or First Hospitalization for Worsening Heart Failure (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13592, OG001=13635 |
| pcsk9-mace / NCT01764633 / #8 | Time to First Ischemic Fatal or Non-Fatal Stroke or Transient Ischemic Attack (NUMBER) | #0 KM estimate at 6 months | OG000=13780, OG001=13784 -> OG000=13569, OG001=13614 |
| pcsk9-mace / NCT01663402 / #13 | Percent Change From Baseline in Calculated LDL-C at Months 4, 12, and 48: ITT Analysis (LEAST_SQUARES_MEAN) | #0 Month 4 | OG000=9462, OG001=9462 -> OG000=8750, OG001=8602 |
| pcsk9-mace / NCT01663402 / #14 | Percent Change From Baseline in Calculated LDL-C at Months 4, 12, and 48: On-Treatment Analysis (LEAST_SQUARES_MEAN) | #0 Month 4 | OG000=9443, OG001=9451 -> OG000=8647, OG001=8486 |
| sacubitril-valsartan-hfref / NCT01920711 / #2 | Change From Baseline to Month 8 in New York Heart Association (NYHA) Functional Class (NUMBER) | #0 Improved (n=2316, 2302) | OG000=2407, OG001=2389 -> OG000=2316, OG001=2302 |
| sacubitril-valsartan-hfref / NCT02874794 / #1 | Pearson Correlation Coefficient Between Change From Baseline in Aortic Characteristic Impedance and Biomarker Levels: B-type Natriuretic Peptide (BNP) During Both Trough and 4 Hours Post-dose at Week 4 (NUMBER) | #0 Week 4 (pre-dose) | OG000=233, OG001=231 -> OG000=213, OG001=200 |
| sacubitril-valsartan-hfref / NCT02874794 / #2 | Pearson Correlation Coefficient Between Change From Baseline in Aortic Characteristic Impedance and Biomarker Levels: cGMP/U-creatinine During Both Trough and 4 Hours Post-dose at Week 4 (NUMBER) | #0 Week 4 (pre-dose) | OG000=233, OG001=231 -> OG000=209, OG001=196 |
| sacubitril-valsartan-hfref / NCT02900378 / #0 | Change From Baseline (Week 0) in the Six Minute Walk Test (6MWT) at End of Study (Week 12) (MEAN) | #0 Baseline (FAS) | OG000=302, OG001=302 -> OG000=301, OG001=300 |
| sacubitril-valsartan-hfref / NCT02900378 / #8 | Change From Baseline (Week 0) in the Six Minute Walk Test (6MWT) at Weeks 4 and 8 (MEAN) | #0 Baseline (FAS) | OG000=302, OG001=302 -> OG000=301, OG001=300 |
| sacubitril-valsartan-hfref / NCT02900378 / #12 | Change From Baseline in Mean Daily Non-sedentary Daytime Activity in Weekly Intervals (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=259, OG001=257 |
| sacubitril-valsartan-hfref / NCT02900378 / #13 | Change From Baseline in Mean Daily Non-sedentary Daytime Activity in Two-weekly Intervals (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=259, OG001=257 |
| sacubitril-valsartan-hfref / NCT02900378 / #14 | Change From Baseline in Mean Daily Light Non-sedentary Daytime Physical Activity (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=259, OG001=257 |
| sacubitril-valsartan-hfref / NCT02900378 / #15 | Change From Baseline in Mean Daily Moderate-to-Vigorous Non-sedentary Daytime Physical Activity (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=259, OG001=257 |
| sacubitril-valsartan-hfref / NCT02900378 / #16 | Total Weekly Time Spent in Non-sedentary Daytime Physical Activity (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=264, OG001=263 |
| sacubitril-valsartan-hfref / NCT02900378 / #17 | Total Weekly Time Spent in Light Non-sedentary Daytime Physical Activity (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=264, OG001=263 |
| sacubitril-valsartan-hfref / NCT02900378 / #18 | Total Weekly Time Spent in Moderate-to-Vigorous Non-sedentary Daytime Physical Activity (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=264, OG001=263 |
| sacubitril-valsartan-hfref / NCT02900378 / #19 | Change From Baseline in Peak Six Minutes of Daytime Physical Activity (MEAN) | #0 Baseline | OG000=302, OG001=302 -> OG000=259, OG001=257 |
| sacubitril-valsartan-hfref / NCT02468232 / #2 | Key Secondary: Change From Baseline to the Pre-defined Time-points in Log-transformed Concentration of N-terminal Pro-brain Natriuretic Peptide (NT-proBNP) (GEOMETRIC_MEAN) | #0 Week 4 (n = 111, 110, 0, 0) | OG000=111, OG001=112, OG002=0, OG003=0 -> OG000=111, OG001=110, OG002=0, OG003=0 |
| sacubitril-valsartan-hfref / NCT02468232 / #5 | Key Secondary: Number of Participants by Changes in New York Heart Association (NYHA) Classification From Baseline at Predefined Timepoints (COUNT_OF_PARTICIPANTS) | #0 Week 4 Improved (n = 111, 111, 0, 0) | OG000=111, OG001=112, OG002=0, OG003=0 -> OG000=111, OG001=111, OG002=0, OG003=0 |
| sacubitril-valsartan-hfref / NCT02468232 / #6 | Key Secondary: Change From Baseline in Clinical Summary Score for Heart Failure Symptoms and Physical Limitations Assessed by Kansas City Cardiomyopathy Questionnaire (KCCQ). (LEAST_SQUARES_MEAN) | #0 Week 8 (n = 111, 111, 0, 0) | OG000=111, OG001=112, OG002=0, OG003=0 -> OG000=111, OG001=111, OG002=0, OG003=0 |
| sacubitril-valsartan-hfref / NCT02468232 / #16 | Change in Blood NT-proBNP From Baseline (MEAN) | #0 Week 2 (n = 111, 108, 0, 0) | OG000=111, OG001=112, OG002=0, OG003=0 -> OG000=111, OG001=108, OG002=0, OG003=0 |
| sacubitril-valsartan-hfref / NCT02468232 / #18 | Changes in Urine Cyclic Guanosine 3',5'-Monophosphate (cGMP) From Baseline (MEAN) | #0 Week 4 (n = 110, 109, 0, 0) | OG000=111, OG001=112, OG002=0, OG003=0 -> OG000=110, OG001=109, OG002=0, OG003=0 |
| sacubitril-valsartan-hfref / NCT02468232 / #21 | Change in Key Echocardiographic Parameters From OLE Baseline at Month 12 (OLE) (MEAN) | #0 LAVi (n = 0, 0, 67, 55) | OG000=0, OG001=0, OG002=79, OG003=71 -> OG000=0, OG001=0, OG002=67, OG003=55 |
| sacubitril-valsartan-hfref / NCT02468232 / #23 | Change in B-type Natriuretic Peptide (BNP) From OLE Baseline to Predefined Timepoints (OLE) (MEAN) | #0 Weeks 2-4 (n = 0, 0, 78, 70) | OG000=0, OG001=0, OG002=79, OG003=71 -> OG000=0, OG001=0, OG002=78, OG003=70 |
| sacubitril-valsartan-hfref / NCT02468232 / #24 | Change in N-terminal Pro-brain Natriuretic Peptide (NT-proBNP) From OLE Baseline to Predefined Timepoints (OLE) (MEAN) | #0 Weeks 2-4 (n = 0, 0, 78, 70) | OG000=0, OG001=0, OG002=79, OG003=71 -> OG000=0, OG001=0, OG002=78, OG003=70 |
| sacubitril-valsartan-hfref / NCT02468232 / #25 | Change in Urine cGMP From OLE Baseline to Predefined Timepoints (OLE) (MEAN) | #0 Weeks 2-4 (n = 0, 0, 78, 69) | OG000=0, OG001=0, OG002=79, OG003=71 -> OG000=0, OG001=0, OG002=78, OG003=69 |
| sacubitril-valsartan-hfref / NCT02468232 / #26 | Association Between Change in NT-proBNP Concentration and Change in Echocardiographic Parameters From OLE Baseline at Month 12 (OLE) (NUMBER) | #0 NT-proBNP / LAVi( =0,0, 67, 55) | OG000=0, OG001=0, OG002=79, OG003=71 -> OG000=0, OG001=0, OG002=67, OG003=55 |
| sacubitril-valsartan-hfref / NCT02690974 / #5 | Time to Each Up-titration to LCZ696 100 mg and LCZ696 200 mg (MEAN) | #0 50- 100 mg bid level | OG000=302 -> OG000=248 |
| semaglutide-obesity-mace / NCT03574597 / #14 | Participants With HbA1c < 39 mmol/Mol (5.7%) (for Participants With a Screening HbA1c ≥ 39 mmol/Mol [5.7%]) (COUNT_OF_PARTICIPANTS) | #0 Week 52 | OG000=5877, OG001=5819 -> OG000=5112, OG001=5078 |
| semaglutide-obesity-weight / NCT05616013 / #7 | Change From Baseline in Visceral Adipose Tissue (VAT), Subcutaneous Adipose Tissue (SAT) and Trunk Fat Mass by DXA at Week 48 (LEAST_SQUARES_MEAN) | #0 VAT | OG000=30, OG001=30, OG002=36, OG003=45, OG004=47, OG005=42, OG006=40, OG007=42, OG008=43 -> OG000=29, OG001=30, OG002=32, OG003=44, OG004=45, OG005=41, OG006=40, OG007=41, OG008=41 |
| semaglutide-obesity-weight / NCT05616013 / #8 | Change From Baseline in VAT, SAT and Trunk Fat Mass by DXA at Week 72 (LEAST_SQUARES_MEAN) | #0 VAT | OG000=19, OG001=23, OG002=27, OG003=38, OG004=43, OG005=32, OG006=38, OG007=41, OG008=34 -> OG000=18, OG001=23, OG002=24, OG003=37, OG004=42, OG005=31, OG006=37, OG007=40, OG008=32 |
| semaglutide-obesity-weight / NCT03574597 / #14 | Participants With HbA1c < 39 mmol/Mol (5.7%) (for Participants With a Screening HbA1c ≥ 39 mmol/Mol [5.7%]) (COUNT_OF_PARTICIPANTS) | #0 Week 52 | OG000=5877, OG001=5819 -> OG000=5112, OG001=5078 |
| semaglutide-obesity-weight / NCT05646706 / #40 | Semaglutide 7.2 mg Versus Placebo: Number of Participants With Change in Glycaemic Category (Normo-glycaemia, Pre-diabetes) (COUNT_OF_PARTICIPANTS) | #0 Normo-glycaemia (week 0) | OG000=951, OG001=168 -> OG000=595, OG001=97 |
| semaglutide-obesity-weight / NCT05564117 / #23 | Number of Participants With Change in Glycaemic Status (COUNT_OF_PARTICIPANTS) | #0 Normo-glycaemia (week 0) | OG000=190, OG001=86 -> OG000=97, OG001=46 |
| semaglutide-obesity-weight / NCT03611582 / #0 | Change in Body Weight (%) (MEAN) | #0 In-trial observation period | OG000=407, OG001=204 -> OG000=373, OG001=189 |
| semaglutide-obesity-weight / NCT03611582 / #1 | Participants Who Achieve (Yes/no): Body Weight Reduction More Than or Equal to 5% (COUNT_OF_PARTICIPANTS) | #0 In-trial observation period | OG000=407, OG001=204 -> OG000=373, OG001=189 |
| semaglutide-obesity-weight / NCT03611582 / #7 | Change in Short Form-36 (SF-36) - Physical Functioning Score (MEAN) | #0 Change in physical functioning score (SF-36) | OG000=407, OG001=204 -> OG000=364, OG001=181 |
| semaglutide-obesity-weight / NCT03548935 / #0 | Change in Body Weight (%) (MEAN) | #0 In-trial observation period | OG000=1306, OG001=655 -> OG000=1212, OG001=577 |
| semaglutide-obesity-weight / NCT03548935 / #1 | Participants Who Achieve 5 or More Percent Body Weight Reduction (Yes/no) (COUNT_OF_PARTICIPANTS) | #0 In-trial observation period | OG000=1306, OG001=655 -> OG000=1212, OG001=577 |
| semaglutide-obesity-weight / NCT03552757 / #0 | Change in Body Weight (%) - Semaglutide 2.4 mg Versus Placebo (MEAN) | #0 In-trial observation period | OG000=404, OG001=403 -> OG000=388, OG001=376 |
| semaglutide-obesity-weight / NCT03552757 / #1 | Participants Who Achieve (Yes/no): Body Weight Reduction ≥5% - Semaglutide 2.4 mg Versus Placebo (COUNT_OF_PARTICIPANTS) | #0 In-trial observation period | OG000=404, OG001=403 -> OG000=388, OG001=376 |

By source paramType: 10/303 COUNT_OF_PARTICIPANTS, 15/432 NUMBER, 56/524 MEAN, 11/167 LEAST_SQUARES_MEAN, 1/177 GEOMETRIC_MEAN; 0/1 COUNT_OF_UNITS, 0/56 MEDIAN, 0/24 unspecified. These are source types, not assertions that percentages or KM estimates are binary counts.

## Validation

Passed **53/53** tests:

```text
python -m pytest -q tests/test_registry_class_denominators.py tests/test_continuous_identity.py tests/test_ctgov_continuous.py tests/test_target_endpoint.py tests/test_consumer_consistency.py tests/test_harms_recovery.py tests/test_second_source_identity.py
```

The first run of the two required files passed 24/24. The first route-file run passed 27 tests and failed two on absent `docs/reviews` fixtures in this sparse worktree. For the bounded rerun above, the three required review.json fixtures (sglt2-hfref-hosp-cvdeath, colchicine-secondary-cv-prevention, esketamine-trd-madrs) were temporarily read from `HEAD` with `git show`, then removed. No test was skipped or weakened.

Second-pass source review passed: every one of the 93 inventory titles and class count maps was checked against its pinned raw measure; all three PMID/NCT joins were checked against pinned records. Actual extraction confirmed STEP 1 1212/577 and STEP 3 373/189. FOURIER's actual second-source output now says 13499/13447, retains 13784/13780 as analysis-set n, and has the identical KM estimate ratio as the pinned served row. `git diff --check` passed.

No full-suite run, commit, push, or deployment.
