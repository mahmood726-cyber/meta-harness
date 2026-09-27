# Derived label corpus fixture

Pinned served reviews, abstracts, protocols and refusals: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`.
Topics and pure rule implementations are read from this worktree. No pipeline rerun or network access.

| Input | Static or dynamic |
|---|---|
| Commit and historical comparison counts | Static, task-supplied baselines, never used to calculate results |
| Synthetic __control_ cases and expected values | Static test oracles; excluded from every corpus total |
| Review membership and source data | Dynamic git reads at pinned commit; SHA-256 recorded |
| Topic policies | Dynamic worktree reads; SHA-256 recorded |
| Rule outputs and totals | Dynamic pure-function evaluation; no research effect estimates generated |

Coverage: 32 served reviews; 97 outcome records.
PRIMARY is the served outcome's primary flag, not its newly derived tier. NON_PRIMARY retains the original efficacy/harm kind.
Population literals are injected before tiers(). Null literals on present abstracts are evaluated negatives, not missing data.
Preregistration is also directly evaluated for empty outcomes; the pipeline would skip those, recorded separately.
Empty outcomes have a refused measure decision and null derived label/tiers, avoiding vacuous DERIVED labels.
Sensitivity is the rule's restriction target (null if absent); this fixture does not compute pooled effects.

| Rule | Fires | N | What N counts |
|---|---:|---:|---|
| PRIMARY.mixed_measures | 5 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| PRIMARY.measure_refused | 7 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes; empty inputs return UNIDENTIFIED |
| PRIMARY.label_not_derived | 29 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes; empty inputs are unevaluable, not fires |
| PRIMARY.follow_up_window_not_derived | 28 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| PRIMARY.analysis_set_not_derived | 27 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| PRIMARY.endpoint_definition_not_derived | 26 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| PRIMARY.composite_changes | 1 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes; fire = at least one admission changes |
| PRIMARY.not_preregistered | 0 | 32 | all PRIMARY outcome records, including zero-trial and unevaluable outcomes; direct rule evaluated even where pipeline skips |
| PRIMARY.population_literal | 3 | 87 | all admitted trial-outcome occurrences in PRIMARY; repeated trials count per outcome; missing abstracts stay in N |
| NON_PRIMARY.mixed_measures | 2 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| NON_PRIMARY.measure_refused | 38 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes; empty inputs return UNIDENTIFIED |
| NON_PRIMARY.label_not_derived | 17 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes; empty inputs are unevaluable, not fires |
| NON_PRIMARY.follow_up_window_not_derived | 6 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| NON_PRIMARY.analysis_set_not_derived | 10 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| NON_PRIMARY.endpoint_definition_not_derived | 16 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes |
| NON_PRIMARY.composite_changes | 0 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes; fire = at least one admission changes |
| NON_PRIMARY.not_preregistered | 19 | 65 | all NON_PRIMARY outcome records, including zero-trial and unevaluable outcomes; direct rule evaluated even where pipeline skips |
| NON_PRIMARY.population_literal | 5 | 40 | all admitted trial-outcome occurrences in NON_PRIMARY; repeated trials count per outcome; missing abstracts stay in N |

## Historical comparisons

Previous totals alone cannot identify which prior members changed. All current firing outcomes/rows and denominator members follow; no membership is inferred.

### mixed_measures: AGREES
Previous 4/27; measured 4/27.
N: primary outcomes with a served result.estimate (historical measure census definition)

Current fires:

- balanced-crystalloids-vs-saline-mortality :: Mortality
- doac-vte-recurrence :: Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)
- noac-vs-warfarin-af-stroke :: Stroke or systemic embolism
- spironolactone-hfref-mortality :: All-cause mortality

Current denominator members:

- balanced-crystalloids-vs-saline-mortality :: Mortality
- colchicine-postop-af :: Postoperative atrial fibrillation
- colchicine-recurrent-pericarditis :: Recurrent pericarditis
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite
- corticosteroids-cap-mortality :: All-cause mortality
- corticosteroids-covid19-mortality :: 28-day all-cause mortality
- denosumab-vertebral-fracture :: New vertebral fracture
- doac-vte-recurrence :: Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)
- dpp4-mace-t2d :: 3-point major adverse cardiovascular events
- esketamine-trd-madrs :: Observed-case Day-28 raw change-score MADRS MD
- finerenone-ckd-t2d-renal :: Kidney composite outcome
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events
- melatonin-primary-insomnia-sol :: Sleep-onset latency
- metformin-pcos-ovulation :: Ovulation with metformin added to clomifene
- noac-vs-warfarin-af-stroke :: Stroke or systemic embolism
- omega3-cardiovascular-events :: Major vascular events / MACE
- pcsk9-mace :: Major adverse cardiovascular events
- probiotics-aad-prevention :: Antibiotic-associated diarrhoea
- semaglutide-obesity-mace :: 3-point major adverse cardiovascular events
- semaglutide-obesity-weight :: Percent change in body weight
- sglt2-ckd-progression :: Trial-defined primary cardiorenal composite
- sglt2-hfref-hosp-cvdeath :: Composite cardiovascular death or hospitalisation for heart failure
- sglt2-primary-prevention-hf :: Hospitalization for heart failure
- spironolactone-hfref-mortality :: All-cause mortality
- statins-primary-prevention-elderly :: Major vascular events
- tocilizumab-covid19-mortality :: 28-day all-cause mortality
- tranexamic-acid-pph :: Death due to bleeding

### label_not_derived: AGREES
Previous 26/27; measured 26/27.
N: primary outcomes with a served result.estimate

Current fires:

- balanced-crystalloids-vs-saline-mortality :: Mortality
- colchicine-postop-af :: Postoperative atrial fibrillation
- colchicine-recurrent-pericarditis :: Recurrent pericarditis
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite
- corticosteroids-cap-mortality :: All-cause mortality
- corticosteroids-covid19-mortality :: 28-day all-cause mortality
- denosumab-vertebral-fracture :: New vertebral fracture
- doac-vte-recurrence :: Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)
- dpp4-mace-t2d :: 3-point major adverse cardiovascular events
- esketamine-trd-madrs :: Observed-case Day-28 raw change-score MADRS MD
- finerenone-ckd-t2d-renal :: Kidney composite outcome
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events
- metformin-pcos-ovulation :: Ovulation with metformin added to clomifene
- noac-vs-warfarin-af-stroke :: Stroke or systemic embolism
- omega3-cardiovascular-events :: Major vascular events / MACE
- pcsk9-mace :: Major adverse cardiovascular events
- probiotics-aad-prevention :: Antibiotic-associated diarrhoea
- semaglutide-obesity-mace :: 3-point major adverse cardiovascular events
- semaglutide-obesity-weight :: Percent change in body weight
- sglt2-ckd-progression :: Trial-defined primary cardiorenal composite
- sglt2-hfref-hosp-cvdeath :: Composite cardiovascular death or hospitalisation for heart failure
- sglt2-primary-prevention-hf :: Hospitalization for heart failure
- spironolactone-hfref-mortality :: All-cause mortality
- statins-primary-prevention-elderly :: Major vascular events
- tocilizumab-covid19-mortality :: 28-day all-cause mortality
- tranexamic-acid-pph :: Death due to bleeding

Current denominator members:

- balanced-crystalloids-vs-saline-mortality :: Mortality
- colchicine-postop-af :: Postoperative atrial fibrillation
- colchicine-recurrent-pericarditis :: Recurrent pericarditis
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite
- corticosteroids-cap-mortality :: All-cause mortality
- corticosteroids-covid19-mortality :: 28-day all-cause mortality
- denosumab-vertebral-fracture :: New vertebral fracture
- doac-vte-recurrence :: Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)
- dpp4-mace-t2d :: 3-point major adverse cardiovascular events
- esketamine-trd-madrs :: Observed-case Day-28 raw change-score MADRS MD
- finerenone-ckd-t2d-renal :: Kidney composite outcome
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events
- melatonin-primary-insomnia-sol :: Sleep-onset latency
- metformin-pcos-ovulation :: Ovulation with metformin added to clomifene
- noac-vs-warfarin-af-stroke :: Stroke or systemic embolism
- omega3-cardiovascular-events :: Major vascular events / MACE
- pcsk9-mace :: Major adverse cardiovascular events
- probiotics-aad-prevention :: Antibiotic-associated diarrhoea
- semaglutide-obesity-mace :: 3-point major adverse cardiovascular events
- semaglutide-obesity-weight :: Percent change in body weight
- sglt2-ckd-progression :: Trial-defined primary cardiorenal composite
- sglt2-hfref-hosp-cvdeath :: Composite cardiovascular death or hospitalisation for heart failure
- sglt2-primary-prevention-hf :: Hospitalization for heart failure
- spironolactone-hfref-mortality :: All-cause mortality
- statins-primary-prevention-elderly :: Major vascular events
- tocilizumab-covid19-mortality :: 28-day all-cause mortality
- tranexamic-acid-pph :: Death due to bleeding

### composite_changes: DISAGREES
Previous 3/25; measured 3/27.
N: all admitted and composite-refused rows returned by primary composite_compatibility, including NO_DEFINITION

Current fires:

- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 31733140
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 32865380
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 39555823

Current denominator members:

- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 31733140
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 32865380
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 39555823
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 32862667
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 34876021
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 32295417
- dpp4-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 23992601
- dpp4-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 30418475
- dpp4-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 28893244
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 31185157
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 27633186
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 27295427
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 34215025
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 31189511
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 30291013
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 28910237
- glp1-ra-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 40162642
- omega3-cardiovascular-events :: Major vascular events / MACE :: PMID 33190147
- omega3-cardiovascular-events :: Major vascular events / MACE :: PMID 30415637
- omega3-cardiovascular-events :: Major vascular events / MACE :: PMID 30415628
- omega3-cardiovascular-events :: Major vascular events / MACE :: PMID 20929341
- omega3-cardiovascular-events :: Major vascular events / MACE :: PMID 21115589
- pcsk9-mace :: Major adverse cardiovascular events :: PMID 28304224
- pcsk9-mace :: Major adverse cardiovascular events :: PMID 30403574
- semaglutide-obesity-mace :: 3-point major adverse cardiovascular events :: PMID 37952131
- ticagrelor-vs-clopidogrel-acs :: Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke :: PMID 19717846
- ticagrelor-vs-clopidogrel-acs :: Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke :: PMID 26376600

Explicit evaluable subset: 3/25; full denominator above retains these NO_DEFINITION rows:

- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 34876021
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 32295417

### not_preregistered: AGREES
Previous 19/65; measured 19/65.
N: all non-primary outcomes, including zero-trial outcomes

Current fires:

- colchicine-recurrent-pericarditis :: Symptom persistence at 72 hours
- colchicine-recurrent-pericarditis :: Disease-related hospitalisation
- dapagliflozin-hfpef-hosp :: Adverse events
- doac-vte-recurrence :: Major bleeding
- doac-vte-recurrence :: Major or clinically relevant nonmajor bleeding
- doac-vte-recurrence :: Any bleeding
- doac-vte-recurrence :: Adverse events
- doac-vte-recurrence :: Adverse events leading to discontinuation
- dpp4-mace-t2d :: Adverse events
- dpp4-mace-t2d :: Hypoglycemia
- dpp4-mace-t2d :: Acute pancreatitis
- dpp4-mace-t2d :: Hospitalization for heart failure
- esketamine-trd-madrs :: Adverse events
- melatonin-primary-insomnia-sol :: Adverse events
- semaglutide-obesity-weight :: Gastrointestinal adverse events
- sglt2-primary-prevention-hf :: Adverse events
- sglt2-primary-prevention-hf :: Lower-limb amputation
- sglt2-primary-prevention-hf :: Genital infection
- sglt2-primary-prevention-hf :: Diabetic ketoacidosis

Current denominator members:

- balanced-crystalloids-vs-saline-mortality :: Acute kidney injury
- balanced-crystalloids-vs-saline-mortality :: New renal-replacement therapy
- colchicine-postop-af :: Gastrointestinal adverse effects
- colchicine-postop-af :: Treatment discontinuation
- colchicine-recurrent-pericarditis :: Symptom persistence at 72 hours
- colchicine-recurrent-pericarditis :: Disease-related hospitalisation
- colchicine-recurrent-pericarditis :: Adverse events (gastrointestinal)
- colchicine-recurrent-pericarditis :: Treatment discontinuation
- colchicine-secondary-cv-prevention :: Gastrointestinal adverse effects
- colchicine-secondary-cv-prevention :: Non-cardiovascular death
- corticosteroids-cap-mortality :: Hyperglycaemia
- corticosteroids-cap-mortality :: Gastrointestinal bleeding
- corticosteroids-covid19-mortality :: Serious adverse events
- dapagliflozin-hfpef-hosp :: Adverse events
- denosumab-vertebral-fracture :: Nonvertebral fracture
- denosumab-vertebral-fracture :: Hip fracture
- denosumab-vertebral-fracture :: Serious adverse events
- denosumab-vertebral-fracture :: Serious infection
- doac-vte-recurrence :: Major bleeding
- doac-vte-recurrence :: Major or clinically relevant nonmajor bleeding
- doac-vte-recurrence :: Any bleeding
- doac-vte-recurrence :: Adverse events
- doac-vte-recurrence :: Adverse events leading to discontinuation
- dpp4-mace-t2d :: Adverse events
- dpp4-mace-t2d :: Hypoglycemia
- dpp4-mace-t2d :: Acute pancreatitis
- dpp4-mace-t2d :: Hospitalization for heart failure
- esketamine-trd-madrs :: Adverse events
- finerenone-ckd-t2d-renal :: Hyperkalemia
- finerenone-ckd-t2d-renal :: Hyperkalemia-related treatment discontinuation
- glp1-ra-mace-t2d :: Gastrointestinal adverse events
- glp1-ra-mace-t2d :: Adverse events leading to discontinuation
- iv-iron-hfref-hosp :: Injection-site reactions
- iv-iron-hfref-hosp :: Hypersensitivity reactions
- melatonin-primary-insomnia-sol :: Adverse events
- metformin-pcos-ovulation :: Gastrointestinal adverse events
- metformin-pcos-ovulation :: Treatment discontinuation due to adverse events
- noac-vs-warfarin-af-stroke :: Major bleeding
- omega3-cardiovascular-events :: Atrial fibrillation
- omega3-cardiovascular-events :: Bleeding
- pcsk9-mace :: Injection-site reactions
- pcsk9-mace :: Adverse events leading to discontinuation
- probiotics-aad-prevention :: Any adverse events
- probiotics-aad-prevention :: Serious adverse events
- semaglutide-obesity-mace :: Gastrointestinal adverse events
- semaglutide-obesity-mace :: Adverse events leading to permanent discontinuation
- semaglutide-obesity-weight :: Gastrointestinal adverse events
- sglt2-ckd-progression :: Diabetic ketoacidosis
- sglt2-ckd-progression :: Lower-limb amputation
- sglt2-hfref-hosp-cvdeath :: Volume depletion or hypotension
- sglt2-hfref-hosp-cvdeath :: Diabetic ketoacidosis
- sglt2-primary-prevention-hf :: Adverse events
- sglt2-primary-prevention-hf :: Lower-limb amputation
- sglt2-primary-prevention-hf :: Genital infection
- sglt2-primary-prevention-hf :: Diabetic ketoacidosis
- spironolactone-hfref-mortality :: Hyperkalemia
- spironolactone-hfref-mortality :: Gynecomastia or breast pain
- statins-primary-prevention-elderly :: Muscle symptoms/myopathy
- statins-primary-prevention-elderly :: New-onset diabetes
- ticagrelor-vs-clopidogrel-acs :: Major bleeding
- ticagrelor-vs-clopidogrel-acs :: Dyspnea
- tocilizumab-covid19-mortality :: Serious adverse events
- tocilizumab-covid19-mortality :: Secondary infections by 28 days
- tranexamic-acid-pph :: Thromboembolic events
- tranexamic-acid-pph :: Adverse events

## DPP-4 source-backed population checks

Historical expectations: CARMELINA mITT 6979/6991; OMNeON analysed 4192/4202; SAVOR null. Actual held-source results:

- SAVOR: AGREES — dpp4-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 23992601 (Saxagliptin and cardiovascular outcomes in patients with type 2 diabetes mellitus.): null
- CARMELINA: AGREES — dpp4-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 30418475 (Effect of Linagliptin vs Placebo on Major Cardiovascular Events in Adults With Type 2 Diabetes and High Cardiovascular and Renal Risk: The CARMELINA Randomized Clinical Trial.): {"population": "mITT: received at least 1 dose (6979 of 6991 randomised)", "basis": "Of 6991 enrollees, 6979 (mean age, 65.9 years; eGFR, 54.6 mL/min/1.73 m2; 80.1% with UACR >30 mg/g) received at least 1 dose", "all_randomised": false}
- OMNeON: AGREES — dpp4-mace-t2d :: 3-point major adverse cardiovascular events :: PMID 28893244 (A randomized, placebo-controlled study of the cardiovascular safety of the once-weekly DPP-4 inhibitor omarigliptin in patients with type 2 diabetes mellitus.): {"population": "analysed 4192 of 4202 randomised (not all randomised)", "basis": "4202 patients with T2DM and established CV disease were assigned", "all_randomised": false}

## Unevaluable or inapplicable items (retained in denominators)

No declared composite core is inapplicable; no definition or no trials is unevaluable. These are not silently dropped.

- balanced-crystalloids-vs-saline-mortality :: Mortality — composite_compatibility: no declared or MACE-type core (not applicable)
- balanced-crystalloids-vs-saline-mortality :: Acute kidney injury — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- balanced-crystalloids-vs-saline-mortality :: Acute kidney injury — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- balanced-crystalloids-vs-saline-mortality :: Acute kidney injury — tiers: no admitted trials; pipeline tiers loop skips this outcome
- balanced-crystalloids-vs-saline-mortality :: Acute kidney injury — composite_compatibility: no declared or MACE-type core (not applicable)
- balanced-crystalloids-vs-saline-mortality :: New renal-replacement therapy — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-postop-af :: Postoperative atrial fibrillation — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-postop-af :: Gastrointestinal adverse effects — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-postop-af :: Gastrointestinal adverse effects — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-postop-af :: Gastrointestinal adverse effects — tiers: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-postop-af :: Gastrointestinal adverse effects — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-postop-af :: Treatment discontinuation — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-postop-af :: Treatment discontinuation — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-postop-af :: Treatment discontinuation — tiers: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-postop-af :: Treatment discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-recurrent-pericarditis :: Recurrent pericarditis — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-recurrent-pericarditis :: Symptom persistence at 72 hours — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-recurrent-pericarditis :: Disease-related hospitalisation — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Disease-related hospitalisation — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Disease-related hospitalisation — tiers: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Disease-related hospitalisation — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-recurrent-pericarditis :: Adverse events (gastrointestinal) — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Adverse events (gastrointestinal) — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Adverse events (gastrointestinal) — tiers: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Adverse events (gastrointestinal) — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-recurrent-pericarditis :: Treatment discontinuation — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Treatment discontinuation — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Treatment discontinuation — tiers: no admitted trials; pipeline tiers loop skips this outcome
- colchicine-recurrent-pericarditis :: Treatment discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 34876021 — composite_compatibility: no usable component definition: none
- colchicine-secondary-cv-prevention :: Trial-defined major coronary/cardiovascular composite :: PMID 32295417 — composite_compatibility: no usable component definition: none
- colchicine-secondary-cv-prevention :: Gastrointestinal adverse effects — composite_compatibility: no declared or MACE-type core (not applicable)
- colchicine-secondary-cv-prevention :: Non-cardiovascular death — composite_compatibility: no declared or MACE-type core (not applicable)
- corticosteroids-cap-mortality :: All-cause mortality — composite_compatibility: no declared or MACE-type core (not applicable)
- corticosteroids-cap-mortality :: Hyperglycaemia — composite_compatibility: no declared or MACE-type core (not applicable)
- corticosteroids-cap-mortality :: Gastrointestinal bleeding — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- corticosteroids-cap-mortality :: Gastrointestinal bleeding — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- corticosteroids-cap-mortality :: Gastrointestinal bleeding — tiers: no admitted trials; pipeline tiers loop skips this outcome
- corticosteroids-cap-mortality :: Gastrointestinal bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- corticosteroids-covid19-mortality :: 28-day all-cause mortality — composite_compatibility: no declared or MACE-type core (not applicable)
- corticosteroids-covid19-mortality :: Serious adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- dapagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- dapagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- dapagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — tiers: no admitted trials; pipeline tiers loop skips this outcome
- dapagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — composite_compatibility: no declared or MACE-type core (not applicable)
- dapagliflozin-hfpef-hosp :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- denosumab-vertebral-fracture :: New vertebral fracture — composite_compatibility: no declared or MACE-type core (not applicable)
- denosumab-vertebral-fracture :: Nonvertebral fracture — composite_compatibility: no declared or MACE-type core (not applicable)
- denosumab-vertebral-fracture :: Hip fracture — composite_compatibility: no declared or MACE-type core (not applicable)
- denosumab-vertebral-fracture :: Serious adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- denosumab-vertebral-fracture :: Serious adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- denosumab-vertebral-fracture :: Serious adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- denosumab-vertebral-fracture :: Serious adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- denosumab-vertebral-fracture :: Serious infection — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- denosumab-vertebral-fracture :: Serious infection — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- denosumab-vertebral-fracture :: Serious infection — tiers: no admitted trials; pipeline tiers loop skips this outcome
- denosumab-vertebral-fracture :: Serious infection — composite_compatibility: no declared or MACE-type core (not applicable)
- doac-vte-recurrence :: Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) — composite_compatibility: no declared or MACE-type core (not applicable)
- doac-vte-recurrence :: Major bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- doac-vte-recurrence :: Major or clinically relevant nonmajor bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- doac-vte-recurrence :: Any bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- doac-vte-recurrence :: Adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- doac-vte-recurrence :: Adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- doac-vte-recurrence :: Adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- doac-vte-recurrence :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- doac-vte-recurrence :: Adverse events leading to discontinuation — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- doac-vte-recurrence :: Adverse events leading to discontinuation — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- doac-vte-recurrence :: Adverse events leading to discontinuation — tiers: no admitted trials; pipeline tiers loop skips this outcome
- doac-vte-recurrence :: Adverse events leading to discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- dpp4-mace-t2d :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- dpp4-mace-t2d :: Hypoglycemia — composite_compatibility: no declared or MACE-type core (not applicable)
- dpp4-mace-t2d :: Acute pancreatitis — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- dpp4-mace-t2d :: Acute pancreatitis — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- dpp4-mace-t2d :: Acute pancreatitis — tiers: no admitted trials; pipeline tiers loop skips this outcome
- dpp4-mace-t2d :: Acute pancreatitis — composite_compatibility: no declared or MACE-type core (not applicable)
- dpp4-mace-t2d :: Hospitalization for heart failure — composite_compatibility: no declared or MACE-type core (not applicable)
- empagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- empagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- empagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — tiers: no admitted trials; pipeline tiers loop skips this outcome
- empagliflozin-hfpef-hosp :: Composite cardiovascular death or worsening heart failure — composite_compatibility: no declared or MACE-type core (not applicable)
- esketamine-trd-madrs :: Observed-case Day-28 raw change-score MADRS MD :: NCT02422186 — population_literal: no held abstract for this trial ID
- esketamine-trd-madrs :: Observed-case Day-28 raw change-score MADRS MD — composite_compatibility: no declared or MACE-type core (not applicable)
- esketamine-trd-madrs :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- finerenone-ckd-t2d-renal :: Kidney composite outcome — composite_compatibility: no declared or MACE-type core (not applicable)
- finerenone-ckd-t2d-renal :: Hyperkalemia — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- finerenone-ckd-t2d-renal :: Hyperkalemia — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- finerenone-ckd-t2d-renal :: Hyperkalemia — tiers: no admitted trials; pipeline tiers loop skips this outcome
- finerenone-ckd-t2d-renal :: Hyperkalemia — composite_compatibility: no declared or MACE-type core (not applicable)
- finerenone-ckd-t2d-renal :: Hyperkalemia-related treatment discontinuation — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- finerenone-ckd-t2d-renal :: Hyperkalemia-related treatment discontinuation — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- finerenone-ckd-t2d-renal :: Hyperkalemia-related treatment discontinuation — tiers: no admitted trials; pipeline tiers loop skips this outcome
- finerenone-ckd-t2d-renal :: Hyperkalemia-related treatment discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- glp1-ra-mace-t2d :: Gastrointestinal adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- glp1-ra-mace-t2d :: Adverse events leading to discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- iv-iron-hfref-hosp :: Heart-failure hospitalization — composite_compatibility: no declared or MACE-type core (not applicable)
- iv-iron-hfref-hosp :: Injection-site reactions — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- iv-iron-hfref-hosp :: Injection-site reactions — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- iv-iron-hfref-hosp :: Injection-site reactions — tiers: no admitted trials; pipeline tiers loop skips this outcome
- iv-iron-hfref-hosp :: Injection-site reactions — composite_compatibility: no declared or MACE-type core (not applicable)
- iv-iron-hfref-hosp :: Hypersensitivity reactions — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- iv-iron-hfref-hosp :: Hypersensitivity reactions — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- iv-iron-hfref-hosp :: Hypersensitivity reactions — tiers: no admitted trials; pipeline tiers loop skips this outcome
- iv-iron-hfref-hosp :: Hypersensitivity reactions — composite_compatibility: no declared or MACE-type core (not applicable)
- melatonin-primary-insomnia-sol :: Sleep-onset latency — composite_compatibility: no declared or MACE-type core (not applicable)
- melatonin-primary-insomnia-sol :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- metformin-pcos-ovulation :: Ovulation with metformin added to clomifene — composite_compatibility: no declared or MACE-type core (not applicable)
- metformin-pcos-ovulation :: Gastrointestinal adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- metformin-pcos-ovulation :: Gastrointestinal adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- metformin-pcos-ovulation :: Gastrointestinal adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- metformin-pcos-ovulation :: Gastrointestinal adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- metformin-pcos-ovulation :: Treatment discontinuation due to adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- metformin-pcos-ovulation :: Treatment discontinuation due to adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- metformin-pcos-ovulation :: Treatment discontinuation due to adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- metformin-pcos-ovulation :: Treatment discontinuation due to adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- noac-vs-warfarin-af-stroke :: Stroke or systemic embolism — composite_compatibility: no declared or MACE-type core (not applicable)
- noac-vs-warfarin-af-stroke :: Major bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- omega3-cardiovascular-events :: Atrial fibrillation — composite_compatibility: no declared or MACE-type core (not applicable)
- omega3-cardiovascular-events :: Bleeding — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- omega3-cardiovascular-events :: Bleeding — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- omega3-cardiovascular-events :: Bleeding — tiers: no admitted trials; pipeline tiers loop skips this outcome
- omega3-cardiovascular-events :: Bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- pcsk9-mace :: Injection-site reactions — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- pcsk9-mace :: Injection-site reactions — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- pcsk9-mace :: Injection-site reactions — tiers: no admitted trials; pipeline tiers loop skips this outcome
- pcsk9-mace :: Injection-site reactions — composite_compatibility: no declared or MACE-type core (not applicable)
- pcsk9-mace :: Adverse events leading to discontinuation — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- pcsk9-mace :: Adverse events leading to discontinuation — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- pcsk9-mace :: Adverse events leading to discontinuation — tiers: no admitted trials; pipeline tiers loop skips this outcome
- pcsk9-mace :: Adverse events leading to discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- probiotics-aad-prevention :: Antibiotic-associated diarrhoea — composite_compatibility: no declared or MACE-type core (not applicable)
- probiotics-aad-prevention :: Any adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- probiotics-aad-prevention :: Serious adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- sacubitril-valsartan-hfref :: Composite cardiovascular death or heart-failure hospitalization :: NCT02468232 — population_literal: no held abstract for this trial ID
- sacubitril-valsartan-hfref :: Composite cardiovascular death or heart-failure hospitalization — composite_compatibility: no declared or MACE-type core (not applicable)
- semaglutide-obesity-mace :: Gastrointestinal adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- semaglutide-obesity-mace :: Gastrointestinal adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- semaglutide-obesity-mace :: Gastrointestinal adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- semaglutide-obesity-mace :: Gastrointestinal adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- semaglutide-obesity-mace :: Adverse events leading to permanent discontinuation — composite_compatibility: no declared or MACE-type core (not applicable)
- semaglutide-obesity-weight :: Percent change in body weight — composite_compatibility: no declared or MACE-type core (not applicable)
- semaglutide-obesity-weight :: Gastrointestinal adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- semaglutide-obesity-weight :: Gastrointestinal adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- semaglutide-obesity-weight :: Gastrointestinal adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- semaglutide-obesity-weight :: Gastrointestinal adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-ckd-progression :: Trial-defined primary cardiorenal composite — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-ckd-progression :: Diabetic ketoacidosis — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-ckd-progression :: Lower-limb amputation — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-hfref-hosp-cvdeath :: Composite cardiovascular death or hospitalisation for heart failure — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-hfref-hosp-cvdeath :: Volume depletion or hypotension — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-hfref-hosp-cvdeath :: Volume depletion or hypotension — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-hfref-hosp-cvdeath :: Volume depletion or hypotension — tiers: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-hfref-hosp-cvdeath :: Volume depletion or hypotension — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-hfref-hosp-cvdeath :: Diabetic ketoacidosis — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-hfref-hosp-cvdeath :: Diabetic ketoacidosis — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-hfref-hosp-cvdeath :: Diabetic ketoacidosis — tiers: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-hfref-hosp-cvdeath :: Diabetic ketoacidosis — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-primary-prevention-hf :: Hospitalization for heart failure — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-primary-prevention-hf :: Adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-primary-prevention-hf :: Lower-limb amputation — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-primary-prevention-hf :: Genital infection — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Genital infection — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Genital infection — tiers: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Genital infection — composite_compatibility: no declared or MACE-type core (not applicable)
- sglt2-primary-prevention-hf :: Diabetic ketoacidosis — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Diabetic ketoacidosis — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Diabetic ketoacidosis — tiers: no admitted trials; pipeline tiers loop skips this outcome
- sglt2-primary-prevention-hf :: Diabetic ketoacidosis — composite_compatibility: no declared or MACE-type core (not applicable)
- spironolactone-hfref-mortality :: All-cause mortality — composite_compatibility: no declared or MACE-type core (not applicable)
- spironolactone-hfref-mortality :: Hyperkalemia — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- spironolactone-hfref-mortality :: Hyperkalemia — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- spironolactone-hfref-mortality :: Hyperkalemia — tiers: no admitted trials; pipeline tiers loop skips this outcome
- spironolactone-hfref-mortality :: Hyperkalemia — composite_compatibility: no declared or MACE-type core (not applicable)
- spironolactone-hfref-mortality :: Gynecomastia or breast pain — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- spironolactone-hfref-mortality :: Gynecomastia or breast pain — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- spironolactone-hfref-mortality :: Gynecomastia or breast pain — tiers: no admitted trials; pipeline tiers loop skips this outcome
- spironolactone-hfref-mortality :: Gynecomastia or breast pain — composite_compatibility: no declared or MACE-type core (not applicable)
- statins-primary-prevention-elderly :: Major vascular events — composite_compatibility: no evaluable multi-component definition
- statins-primary-prevention-elderly :: Muscle symptoms/myopathy — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- statins-primary-prevention-elderly :: Muscle symptoms/myopathy — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- statins-primary-prevention-elderly :: Muscle symptoms/myopathy — tiers: no admitted trials; pipeline tiers loop skips this outcome
- statins-primary-prevention-elderly :: Muscle symptoms/myopathy — composite_compatibility: no declared or MACE-type core (not applicable)
- statins-primary-prevention-elderly :: New-onset diabetes — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- statins-primary-prevention-elderly :: New-onset diabetes — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- statins-primary-prevention-elderly :: New-onset diabetes — tiers: no admitted trials; pipeline tiers loop skips this outcome
- statins-primary-prevention-elderly :: New-onset diabetes — composite_compatibility: no declared or MACE-type core (not applicable)
- ticagrelor-vs-clopidogrel-acs :: Major bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- ticagrelor-vs-clopidogrel-acs :: Dyspnea — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- ticagrelor-vs-clopidogrel-acs :: Dyspnea — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- ticagrelor-vs-clopidogrel-acs :: Dyspnea — tiers: no admitted trials; pipeline tiers loop skips this outcome
- ticagrelor-vs-clopidogrel-acs :: Dyspnea — composite_compatibility: no declared or MACE-type core (not applicable)
- tocilizumab-covid19-mortality :: 28-day all-cause mortality — composite_compatibility: no declared or MACE-type core (not applicable)
- tocilizumab-covid19-mortality :: Serious adverse events — composite_compatibility: no declared or MACE-type core (not applicable)
- tocilizumab-covid19-mortality :: Secondary infections by 28 days — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- tocilizumab-covid19-mortality :: Secondary infections by 28 days — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- tocilizumab-covid19-mortality :: Secondary infections by 28 days — tiers: no admitted trials; pipeline tiers loop skips this outcome
- tocilizumab-covid19-mortality :: Secondary infections by 28 days — composite_compatibility: no declared or MACE-type core (not applicable)
- tranexamic-acid-pph :: Death due to bleeding — composite_compatibility: no declared or MACE-type core (not applicable)
- tranexamic-acid-pph :: Thromboembolic events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- tranexamic-acid-pph :: Thromboembolic events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- tranexamic-acid-pph :: Thromboembolic events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- tranexamic-acid-pph :: Thromboembolic events — composite_compatibility: no declared or MACE-type core (not applicable)
- tranexamic-acid-pph :: Adverse events — pool_measure_decision: no admitted trials; pipeline tiers loop skips this outcome
- tranexamic-acid-pph :: Adverse events — derived_label: no admitted trials; pipeline tiers loop skips this outcome
- tranexamic-acid-pph :: Adverse events — tiers: no admitted trials; pipeline tiers loop skips this outcome
- tranexamic-acid-pph :: Adverse events — composite_compatibility: no declared or MACE-type core (not applicable)

Controls: one positive and one negative per named rule/dimension, explicitly synthetic and excluded from totals.

Regenerate: `python evidence/fixtures/build_derived_label_fixture.py`

Verify only: `python -m pytest -q tests/test_derived_label_corpus_fixture.py -p no:cacheprovider`
