V-spironolactone-hfref-mortality VERDICTS: NEW 73; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 2; NOT_RCT 6; WRONG_* 22; DUPLICATE_OF_ACCOUNTED 19; UNDECIDABLE 9; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 15
automated screen agreed on 2 of 73 verified
r2 includes 76 of 8105; already accounted for 3; NEW 73
MEASURED: n_records=8105; r2 include decisions=76; already-accounted r2 includes=3; NEW=73; no NOT_VERIFIED_CAP was applied.
INFERRED: verdict categories interpret title/abstract/registry-record spans against the protocol PICO; no pooling decision is made here.

## ELIGIBLE_RCT ids with titles
- none

## ELIGIBLE_RCT_NO_PRIMARY ids
- 33175088 - Efficacy and Safety of Early Initiation of Eplerenone Treatment in Patients with Acute Heart Failure (EARLIER trial): a multicentre, randomized, double-blind, placebo-controlled trial.
- 20299607 - Randomized, double-blind, multicenter, placebo-controlled study evaluating the effect of aldosterone antagonism with eplerenone on ventricular remodeling in patients with mild-to-moderate heart failure and left ventricular systolic dysfunction.

## DUPLICATE_OF_ACCOUNTED pairs
- 38739064 -> 10471456/21073363
- 37370197 -> 21073363
- 35867859 -> 21073363
- 31926854 -> 10471456/21073363
- 29997240 -> 21073363
- 27868385 -> 21073363
- 28303624 -> 21073363
- 26093641 -> 21073363
- 24297687 -> 21073363
- 24812304 -> 10471456
- 23625945 -> 21073363
- 23810881 -> 21073363
- 23864130 -> 21073363
- 23940307 -> 10471456
- 22538330 -> 21073363
- 23083787 -> 10471456
- 20388647 -> 21073363
- 12427411 -> 10471456
- 11094035 -> 10471456

## Commands Run
- Get-Content Raw LANE_PROMPT.md
- Get-Content Raw F drive ProjectIndex INDEX.md
- Get-Content Raw F drive E156 rewrite-workbook.txt
- git status short
- Get-Content Raw protocol markdown
- Get-Content Raw topic json
- Get-Content Raw served review json
- python exact legacy include command from LANE_PROMPT.md
- python measured r2 snapshot shape
- FAILED python heredoc review structure exploration in PowerShell
- python review outcome declared_absent structure walk
- FAILED python denominator sorted list f-string SyntaxError
- python measured denominator and sorted NEW list
- python dump NEW records 1 to 73 terminal output truncated
- python dump NEW records 9 to 25
- python dump NEW records 26 to 50 terminal output truncated
- python dump NEW records 35 to 41
- python dump NEW records 51 to 65
- python identify NEW PMIDs with empty or truncated abstracts
- python PubMed efetch for PMIDs 37370197 and 7503007 saved XML bodies
- python extract abstracts from saved PubMed XML
- python inspect NCT-only snapshot record fields
- rg search for NCT07281014 overall_status overallStatus
- FAILED python generate lane artefacts f-string TypeError
- FAILED python generate lane artefacts command-log SyntaxError
- python generate lane JSON and report
- python final artefact validation
- git status short final

## Raw HTTP bodies relied on
- lane_v/spironolactone-hfref-mortality-raw/37370197.xml (PubMed efetch, MEASURED because snapshot abstract was truncated)
- lane_v/spironolactone-hfref-mortality-raw/7503007.xml (PubMed efetch, MEASURED because snapshot abstract was truncated)

## Verdict Table
- NCT07281014 (2026): REGISTRY_ONLY_NO_PUBLICATION - Unmitigated Aldosterone Signaling During Standard Clinical MRA Dosing
- 39566872 (2025): WRONG_INTERVENTION - Sodium Zirconium Cyclosilicate for Management of Hyperkalemia During Spironolactone Optimization in Patients With Heart Failure.
- 38739064 (2024): DUPLICATE_OF_ACCOUNTED - Mineralocorticoid Receptor Antagonists in Patients With Heart Failure and Impaired Renal Function.
- 38986838 (2024): NOT_RCT - Increased Spironolactone Dosing in Acute Heart Failure Alters Potassium Homeostasis but Does not Enhance Decongestion.
- 39181408 (2024): NOT_RCT - Adverse events associated with early initiation of Eplerenone in patients hospitalized for acute heart failure.
- NCT06033950 (2024): REGISTRY_ONLY_NO_PUBLICATION - A Study to Evaluate Finerenone on Clinical Efficacy and Safety in Patients With Heart Failure Who Are Intolerant or Not Eligible for Treatment With Steroidal Mineralocorticoid Receptor Antagonists
- 37062878 (2023): WRONG_POPULATION - A machine learning-derived echocardiographic algorithm identifies people at risk of heart failure with distinct cardiac structure, function, and response to spironolactone: Findings from the HOMAGE trial.
- 37370197 (2023): DUPLICATE_OF_ACCOUNTED - Time to clinical benefit of eplerenone among patients with heart failure and reduced ejection fraction: A subgroups analysis from the EMPHASIS-HF trial.
- 37540060 (2023): WRONG_INTERVENTION - Mineralocorticoid receptor antagonist use and the effects of empagliflozin on clinical outcomes in patients admitted for acute heart failure: Findings from EMPULSE.
- NCT06005259 (2023): REGISTRY_ONLY_NO_PUBLICATION - Effect of Spironolactone in the Prevention of Anthracycline-induced Cardiotoxicity (SPIROTOX)
- 33175088 (2022): ELIGIBLE_RCT_NO_PRIMARY - Efficacy and Safety of Early Initiation of Eplerenone Treatment in Patients with Acute Heart Failure (EARLIER trial): a multicentre, randomized, double-blind, placebo-controlled trial.
- 34315691 (2022): WRONG_POPULATION - Prospective clinical trial evaluating spironolactone in Doberman pinschers with congestive heart failure due to dilated cardiomyopathy.
- 35867859 (2022): DUPLICATE_OF_ACCOUNTED - Effects of steroidal mineralocorticoid receptor antagonists on acute and chronic estimated glomerular filtration rate slopes in patients with chronic heart failure.
- 33549554 (2021): WRONG_INTERVENTION - Dapagliflozin in HFrEF Patients Treated With Mineralocorticoid Receptor Antagonists: An Analysis of DAPA-HF.
- 33736821 (2021): WRONG_INTERVENTION - Interplay of Mineralocorticoid Receptor Antagonists and Empagliflozin in Heart Failure: EMPEROR-Reduced.
- 34569641 (2021): WRONG_POPULATION - NR3C2 genotype is associated with response to spironolactone in diastolic heart failure patients from the Aldo-DHF trial.
- NCT04676646 (2021): REGISTRY_ONLY_NO_PUBLICATION - Study to Assess Efficacy and Safety of SZC for the Management of High Potassium in Patients With Symptomatic HFrEF Receiving Spironolactone
- 31926854 (2020): DUPLICATE_OF_ACCOUNTED - Mineralocorticoid Receptor Antagonists, Blood Pressure, and Outcomes in Heart Failure With Reduced Ejection Fraction.
- 32237012 (2020): NOT_RCT - Spironolactone metabolite concentrations in decompensated heart failure: insights from the ATHENA-HF trial.
- NCT04465123 (2020): REGISTRY_ONLY_NO_PUBLICATION - Early Sequential Nephron Blockade in Acute Heart Failure Patients: A Randomised, Controlled Study
- 31779923 (2019): WRONG_POPULATION - Influence of Age on Efficacy and Safety of Spironolactone in Heart Failure.
- 29277469 (2018): WRONG_POPULATION - The SEISICAT study: a pilot study assessing efficacy and safety of spironolactone in cats with congestive heart failure secondary to cardiomyopathy.
- 29997240 (2018): DUPLICATE_OF_ACCOUNTED - Data-Driven Approach to Identify Subgroups of Heart Failure With Reduced Ejection Fraction Patients With Different Prognoses and Aldosterone Antagonist Response Patterns.
- 27868385 (2017): DUPLICATE_OF_ACCOUNTED - Impact of eplerenone on cardiovascular outcomes in heart failure patients with hypokalaemia.
- 28303624 (2017): DUPLICATE_OF_ACCOUNTED - Effect of eplerenone in patients with heart failure and reduced ejection fraction: potential effect modification by abdominal obesity. Insight from the EMPHASIS-HF trial.
- 28700781 (2017): WRONG_POPULATION - Efficacy and Safety of Spironolactone in Acute Heart Failure: The ATHENA-HF Randomized Clinical Trial.
- 28855452 (2017): WRONG_INTERVENTION - Galectin-3 and the Mineralocorticoid Receptor Antagonist Canrenone in Mild Heart Failure.
- 26962133 (2016): WRONG_POPULATION - Impact of Spironolactone on Longitudinal Changes in Health-Related Quality of Life in the Treatment of Preserved Cardiac Function Heart Failure With an Aldosterone Antagonist Trial.
- 25406305 (2015): WRONG_POPULATION - Regional variation in patients and outcomes in the Treatment of Preserved Cardiac Function Heart Failure With an Aldosterone Antagonist (TOPCAT) trial.
- 25566817 (2015): NOT_RCT - Rationale and Design of the Double-Blind, Randomized, Placebo-Controlled Multicenter Trial on Efficacy of Early Initiation of Eplerenone Treatment in Patients with Acute Heart Failure (EARLIER).
- 26093641 (2015): DUPLICATE_OF_ACCOUNTED - Clinical benefits of eplerenone in patients with systolic heart failure and mild symptoms when initiated shortly after hospital discharge: analysis from the EMPHASIS-HF trial.
- NCT02299726 (2015): REGISTRY_ONLY_NO_PUBLICATION - Early Aldosterone Blockade in Acute Heart Failure: An Exploratory Safety Study
- 24196866 (2014): NOT_RCT - Effects of spironolactone on long-term mortality and morbidity in patients with heart failure and mild or no symptoms.
- 24297687 (2014): DUPLICATE_OF_ACCOUNTED - Incidence, determinants, and prognostic significance of hyperkalemia and worsening renal function in patients with heart failure receiving the mineralocorticoid receptor antagonist eplerenone or placebo in addition to optimal medical therapy: results from the Eplerenone in Mild Patients Hospitalization and Survival Study in Heart Failure (EMPHASIS-HF).
- 24405838 (2014): UNDECIDABLE_FROM_RECORD - Spironolactone, not furosemide, improved insulin resistance in patients with chronic heart failure.
- 24812304 (2014): DUPLICATE_OF_ACCOUNTED - Incidence, predictors, and outcomes related to hypo- and hyperkalemia in patients with severe heart failure treated with a mineralocorticoid receptor antagonist.
- 24905296 (2014): WRONG_POPULATION - Effects of spironolactone treatment in elderly women with heart failure and preserved left ventricular ejection fraction.
- NCT02235077 (2014): REGISTRY_ONLY_NO_PUBLICATION - Study of High-dose Spironolactone vs. Placebo Therapy in Acute Heart Failure
- 22892123 (2013): WRONG_INTERVENTION - Influence of background treatment with mineralocorticoid receptor antagonists on ivabradine's effects in patients with chronic heart failure.
- 23258572 (2013): WRONG_POPULATION - Baseline characteristics of patients in the treatment of preserved cardiac function heart failure with an aldosterone antagonist trial.
- 23625945 (2013): DUPLICATE_OF_ACCOUNTED - Clinical benefit of eplerenone in patients with mild symptoms of systolic heart failure already receiving optimal best practice background drug therapy: analysis of the EMPHASIS-HF study.
- 23810881 (2013): DUPLICATE_OF_ACCOUNTED - Safety and efficacy of eplerenone in patients at high risk for hyperkalemia and/or worsening renal function: analyses of the EMPHASIS-HF study subgroups (Eplerenone in Mild Patients Hospitalization And SurvIval Study in Heart Failure).
- 23864130 (2013): DUPLICATE_OF_ACCOUNTED - The impact of eplerenone at different levels of risk in patients with systolic heart failure and mild symptoms: insight from a novel risk score for prognosis derived from the EMPHASIS-HF trial.
- 23866347 (2013): NOT_RCT - Eplerenone and chronic heart failure. No comparison with spironolactone.
- 23869534 (2013): WRONG_POPULATION - Safety of spironolactone in dogs with chronic heart failure because of degenerative valvular disease: a population-based, longitudinal study.
- 23940307 (2013): DUPLICATE_OF_ACCOUNTED - Race influences the safety and efficacy of spironolactone in severe heart failure.
- 22538330 (2012): DUPLICATE_OF_ACCOUNTED - Eplerenone and atrial fibrillation in mild systolic heart failure: results from the EMPHASIS-HF (Eplerenone in Mild Patients Hospitalization And SurvIval Study in Heart Failure) study.
- 23083787 (2012): DUPLICATE_OF_ACCOUNTED - Influence of baseline and worsening renal function on efficacy of spironolactone in patients With severe heart failure: insights from RALES (Randomized Aldactone Evaluation Study).
- 20950346 (2011): WRONG_POPULATION - Lack of efficacy of low-dose spironolactone as adjunct treatment to conventional congestive heart failure treatment in dogs.
- 21467028 (2011): WRONG_INTERVENTION - Neurohumoral effects of aliskiren in patients with symptomatic heart failure receiving a mineralocorticoid receptor antagonist: the Aliskiren Observation of Heart Failure Treatment study.
- 20299607 (2010): ELIGIBLE_RCT_NO_PRIMARY - Randomized, double-blind, multicenter, placebo-controlled study evaluating the effect of aldosterone antagonism with eplerenone on ventricular remodeling in patients with mild-to-moderate heart failure and left ventricular systolic dysfunction.
- 20388647 (2010): DUPLICATE_OF_ACCOUNTED - Rationale and design of the Eplerenone in Mild Patients Hospitalization And SurvIval Study in Heart Failure (EMPHASIS-HF).
- 20538867 (2010): WRONG_POPULATION - Rationale and design of the 'aldosterone receptor blockade in diastolic heart failure' trial: a double-blind, randomized, placebo-controlled, parallel group study to determine the effects of spironolactone on exercise capacity and diastolic function in patients with symptomatic diastolic heart failure (Aldo-DHF).
- 21029826 (2010): UNDECIDABLE_FROM_RECORD - Effect of spironolactone on left ventricular ejection fraction and volumes in patients with class I or II heart failure.
- NCT01069510 (2010): REGISTRY_ONLY_NO_PUBLICATION - Spironolactone in Adult Congenital Heart Disease
- NCT01115855 (2010): REGISTRY_ONLY_NO_PUBLICATION - Clinical Study Of Eplerenone In Japanese Patients With Chronic Heart Failure
- 18242128 (2008): WRONG_INTERVENTION - Efficacy and tolerability of adding an angiotensin receptor blocker in patients with heart failure already receiving an angiotensin-converting inhibitor plus aldosterone antagonist, with or without a beta blocker. Findings from the Candesartan in Heart failure: Assessment of Reduction in Mortality and morbidity (CHARM)-Added trial.
- NCT00604006 (2008): REGISTRY_ONLY_NO_PUBLICATION - SCREEN-HFI (SCReening Evaluation of the Evolution of New Heart Failure Intervention Study)
- 17448413 (2007): UNDECIDABLE_FROM_RECORD - Spironolactone reduced arrhythmia and maintained magnesium homeostasis in patients with congestive heart failure.
- NCT00523757 (2007): REGISTRY_ONLY_NO_PUBLICATION - Aldosterone Blockade in Heart Failure
- 16504579 (2006): WRONG_POPULATION - Evaluation of eplerenone in the subgroup of EPHESUS patients with baseline left ventricular ejection fraction <or=30%.
- NCT00094302 (2006): REGISTRY_ONLY_NO_PUBLICATION - Aldosterone Antagonist Therapy for Adults With Heart Failure and Preserved Systolic Function
- NCT00232180 (2006): REGISTRY_ONLY_NO_PUBLICATION - A Comparison Of Outcomes In Patients In New York Heart Association (NYHA) Class II Heart Failure When Treated With Eplerenone Or Placebo In Addition To Standard Heart Failure Medicines
- 15618072 (2005): UNDECIDABLE_FROM_RECORD - Spironolactone improves lung diffusion in chronic heart failure.
- NCT00123955 (2005): REGISTRY_ONLY_NO_PUBLICATION - PIE II: Pharmacological Intervention in the Elderly II
- 15201246 (2004): UNDECIDABLE_FROM_RECORD - Effects of spironolactone on endothelial function, vascular angiotensin converting enzyme activity, and other prognostic markers in patients with mild heart failure already taking optimal treatment.
- NCT00108251 (2004): REGISTRY_ONLY_NO_PUBLICATION - Aldosterone Antagonism in Diastolic Heart Failure
- 12427411 (2002): DUPLICATE_OF_ACCOUNTED - Beneficial neurohormonal profile of spironolactone in severe congestive heart failure: results from the RALES neurohormonal substudy.
- 11300427 (2001): UNDECIDABLE_FROM_RECORD - Effect of spironolactone on plasma brain natriuretic peptide and left ventricular remodeling in patients with congestive heart failure.
- 10673249 (2000): UNDECIDABLE_FROM_RECORD - Spironolactone increases nitric oxide bioactivity, improves endothelial vasodilator dysfunction, and suppresses vascular angiotensin I/angiotensin II conversion in patients with chronic heart failure.
- 11094035 (2000): DUPLICATE_OF_ACCOUNTED - Limitation of excessive extracellular matrix turnover may contribute to survival benefit of spironolactone therapy in patients with congestive heart failure: insights from the randomized aldactone evaluation study (RALES). Rales Investigators.
- 8888663 (1996): UNDECIDABLE_FROM_RECORD - Effectiveness of spironolactone added to an angiotensin-converting enzyme inhibitor and a loop diuretic for severe chronic congestive heart failure (the Randomized Aldactone Evaluation Study [RALES]).
- 7503007 (1995): UNDECIDABLE_FROM_RECORD - Effects of adding spironolactone to an angiotensin-converting enzyme inhibitor in chronic congestive heart failure secondary to coronary artery disease.
