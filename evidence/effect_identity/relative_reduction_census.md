# Relative-reduction census

Served data: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`.
Pre-patch extractor: `32b4f3a314dd0bdc74a9433393930a8bbf0ee342`. Current extractor used only for patch-radius comparison.

| Input | Static vs dynamic / hardcode disclosure |
|---|---|
| Git pins and lexical scan pattern | Static audit scope, not research data |
| IDs, quotations, values, denominators | Read from pinned review/topic/cache git objects |
| Complements and patch radius | Computed; Decimal arithmetic, no invented effects or CIs |

Inspected 127 served rows across 97 outcomes and 32 pages; 86 rows carry a reported effect. 2 rows derive from captured reduction phrases.

## Every reduction-derived served row

- **colchicine-recurrent-pericarditis / Recurrent pericarditis / PMID 21873705 [outcome 0, row 1]**; served `['RR', 0.44, 0.27, 0.73]`.
  Named measure RR; point exact=True; CI exact=True; measure exact=True; read from held abstract.

> RESULTS: At 18 months, the recurrence rate was 24% in the colchicine group and 55% in the placebo group (absolute risk reduction, 0.31 [95% CI, 0.13 to 0.46]; relative risk reduction, 0.56 [CI, 0.27 to 0.73]; number needed to treat, 3 [CI, 2 to 7]).

- **colchicine-recurrent-pericarditis / Symptom persistence at 72 hours / PMID 21873705 [outcome 1, row 0]**; served `['RR', 0.44, 0.26, 0.73]`.
  Named measure RR; point exact=True; CI exact=True; measure exact=True; read from row quotation.

> abstract effect+CI (RR): Colchicine reduced the persistence of symptoms at 72 hours (absolute risk reduction, 0.30 [CI, 0.13 to 0.45]; relative risk reduction, 0.56 [CI, 0.27 to 0.74]) and mean number of recurrences, increase

## Patch radius

0 of 127 served-row abstract extractions change. 0 of 127 rows change any source-quotation/held-abstract effect match. This is a parser replay; served JSON/pages are not rebuilt.

## Included-trial abstract scan (report only)

210 of 269 screening-included topic/record pairs have held abstracts; 59 unavailable pairs remain in N and are listed below. Repeated trials across topics remain separate pairs. Scope includes included trials with no served effect.

The deliberately broad lexical screen found 224 sentences: 222 of 224 have no captured reduction complement, and the remainder have a captured complement. This denominator counts sentences, not quantitative effects or errors. All are quoted below. A direct ratio in a sentence is separately disclosed; qualitative prose, absolute/continuous changes, endpoint thresholds and trial names are not asserted to be recoverable ratio effects.

### 1. balanced-crystalloids-vs-saline-mortality / 35041780 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Whether the use of balanced multielectrolyte solution (BMES) in preference to 0.9% sodium chloride solution (saline) in critically ill patients reduces the risk of acute kidney injury or death is uncertain.

Baseline effect+CI matches: `[]`.

### 2. balanced-crystalloids-vs-saline-mortality / 34375394 — NO_CAPTURED_COMPLEMENT

> CONCLUSION AND RELEVANCE: Among critically ill patients requiring fluid challenges, use of a balanced solution compared with 0.9% saline solution did not significantly reduce 90-day mortality.

Baseline effect+CI matches: `[]`.

### 3. balanced-crystalloids-vs-saline-mortality / 26444692 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS AND RELEVANCE: Among patients receiving crystalloid fluid therapy in the ICU, use of a buffered crystalloid compared with saline did not reduce the risk of AKI.

Baseline effect+CI matches: `[]`.

### 4. colchicine-postop-af / 42132185 — NO_CAPTURED_COMPLEMENT

> RESULTS: Of 163 analyzed patients (81 colchicine, 82 placebo), POAF incidence was significantly lower in the colchicine group (17.3% vs. 46.3%; RR 0.37, 95% CI 0.21-0.66; p < 0.001), with an absolute risk reduction of 29.0% and number needed to treat (NNT) of 4.

Baseline effect+CI matches: `[['RR', 0.37, 0.21, 0.66]]`.

### 5. colchicine-postop-af / 42132185 — NO_CAPTURED_COMPLEMENT

> Colchicine reduced both early and late POAF (p < 0.001 and p = 0.002).

Baseline effect+CI matches: `[]`.

### 6. colchicine-postop-af / 42132185 — NO_CAPTURED_COMPLEMENT

> No significant reduction was seen in other arrhythmias.

Baseline effect+CI matches: `[]`.

### 7. colchicine-postop-af / 25172965 — NO_CAPTURED_COMPLEMENT

> OBJECTIVE: To determine the efficacy and safety of perioperative use of oral colchicine in reducing postpericardiotomy syndrome, postoperative AF, and postoperative pericardial or pleural effusions.

Baseline effect+CI matches: `[]`.

### 8. colchicine-postop-af / 25172965 — NO_CAPTURED_COMPLEMENT

> There were no significant differences between the colchicine and placebo groups for the secondary end points of postoperative AF (colchicine, 61 patients [33.9%]; placebo, 75 patients [41.7%]; absolute difference, 7.8%; 95% CI, -2.2% to 17.6%) or postoperative pericardial/pleural effusion (colchicine, 103 patients [57.2%]; placebo, 106 patients [58.9%]; absolute difference, 1.7%; 95% CI, -8.5% to 11.7%), although there was a reduction in postoperative AF in the prespecified on-treatment analysis (placebo, 61/148 patients [41.2%]; colchicine, 38/141 patients [27.0%]; absolute difference, 14.2%; 95% CI, 3.3%-24.7%).

Baseline effect+CI matches: `[]`.

### 9. colchicine-postop-af / 25172965 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS AND RELEVANCE: Among patients undergoing cardiac surgery, perioperative use of colchicine compared with placebo reduced the incidence of postpericardiotomy syndrome but not of postoperative AF or postoperative pericardial/pleural effusion.

Baseline effect+CI matches: `[]`.

### 10. colchicine-postop-af / 25172965 — NO_CAPTURED_COMPLEMENT

> The increased risk of gastrointestinal adverse effects reduced the potential benefits of colchicine in this setting.

Baseline effect+CI matches: `[]`.

### 11. colchicine-recurrent-pericarditis / 24694983 — NO_CAPTURED_COMPLEMENT

> INTERPRETATION: Colchicine added to conventional anti-inflammatory treatment significantly reduced the rate of subsequent recurrences of pericarditis in patients with multiple recurrences.

Baseline effect+CI matches: `[]`.

### 12. colchicine-recurrent-pericarditis / 23992557 — NO_CAPTURED_COMPLEMENT

> The primary outcome occurred in 20 patients (16.7%) in the colchicine group and 45 patients (37.5%) in the placebo group (relative risk reduction in the colchicine group, 0.56; 95% confidence interval, 0.30 to 0.72; number needed to treat, 4; P<0.001).

Baseline effect+CI matches: `[]`.

### 13. colchicine-recurrent-pericarditis / 23992557 — NO_CAPTURED_COMPLEMENT

> Colchicine reduced the rate of symptom persistence at 72 hours (19.2% vs. 40.0%, P=0.001), the number of recurrences per patient (0.21 vs. 0.52, P=0.001), and the hospitalization rate (5.0% vs. 14.2%, P=0.02).

Baseline effect+CI matches: `[]`.

### 14. colchicine-recurrent-pericarditis / 23992557 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In patients with acute pericarditis, colchicine, when added to conventional antiinflammatory therapy, significantly reduced the rate of incessant or recurrent pericarditis.

Baseline effect+CI matches: `[]`.

### 15. colchicine-recurrent-pericarditis / 21873705 — CAPTURED_COMPLEMENT

> RESULTS: At 18 months, the recurrence rate was 24% in the colchicine group and 55% in the placebo group (absolute risk reduction, 0.31 [95% CI, 0.13 to 0.46]; relative risk reduction, 0.56 [CI, 0.27 to 0.73]; number needed to treat, 3 [CI, 2 to 7]).

Baseline effect+CI matches: `[['RR', 0.44, 0.27, 0.73]]`.

### 16. colchicine-recurrent-pericarditis / 21873705 — CAPTURED_COMPLEMENT

> Colchicine reduced the persistence of symptoms at 72 hours (absolute risk reduction, 0.30 [CI, 0.13 to 0.45]; relative risk reduction, 0.56 [CI, 0.27 to 0.74]) and mean number of recurrences, increased the remission rate at 1 week, and prolonged the time to subsequent recurrence.

Baseline effect+CI matches: `[['RR', 0.44, 0.26, 0.73]]`.

### 17. colchicine-secondary-cv-prevention / 41670023 — NO_CAPTURED_COMPLEMENT

> Colchicine, an inexpensive anti-inflammatory medication, has shown promising results in reducing cardiovascular events in patients with stable coronary artery disease (CAD).

Baseline effect+CI matches: `[]`.

### 18. colchicine-secondary-cv-prevention / 41670023 — NO_CAPTURED_COMPLEMENT

> Inflammatory markers were reduced with colchicine, but did not achieve statistical significance.

Baseline effect+CI matches: `[]`.

### 19. colchicine-secondary-cv-prevention / 41670023 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: In the EKSTROM trial, low-dose colchicine did not significantly reduce low attenuation plaque volume in patients with stable coronary artery disease over 12 months, but did achieve a significant reduction in total plaque burden (percent atheroma volume) and dense calcified plaque compared to placebo.

Baseline effect+CI matches: `[]`.

### 20. colchicine-secondary-cv-prevention / 41670023 — NO_CAPTURED_COMPLEMENT

> In this stable well-treated CAD population, LAP was rare and not significantly reduced; however, it slowed overall plaque progression, supporting further investigation of its role in secondary prevention of coronary artery disease.

Baseline effect+CI matches: `[]`.

### 21. colchicine-secondary-cv-prevention / 41605493 — NO_CAPTURED_COMPLEMENT

> The study aimed to test the efficacy of colchicine, an anti-inflammatory agent, to reduce left ventricular mass in patients with CAD and LVH.

Baseline effect+CI matches: `[]`.

### 22. colchicine-secondary-cv-prevention / 41605493 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: The study failed to demonstrate a treatment benefit of colchicine over placebo regarding LVMI reduction at 48 weeks.

Baseline effect+CI matches: `[]`.

### 23. colchicine-secondary-cv-prevention / 40263680 — NO_CAPTURED_COMPLEMENT

> Colchicine was found to fail to reduce the incidence of ischemia-RI (51.5% vs. 42.4%; p = 0.437).

Baseline effect+CI matches: `[]`.

### 24. colchicine-secondary-cv-prevention / 40263680 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Colchicine administration in STEMI patients undergoing PPCI failed to reduce RI.

Baseline effect+CI matches: `[]`.

### 25. colchicine-secondary-cv-prevention / 39189611 — NO_CAPTURED_COMPLEMENT

> AIMS: Low-dose colchicine reduces the risk of cardiovascular events after myocardial infarction (MI).

Baseline effect+CI matches: `[]`.

### 26. colchicine-secondary-cv-prevention / 39166327 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Colchicine has been approved to reduce cardiovascular risk in patients with coronary heart disease on the basis of its potential benefits demonstrated in the COLCOT (Colchicine Cardiovascular Outcomes Trial) and LoDoCo2 (Low-Dose Colchicine 2) studies.

Baseline effect+CI matches: `[]`.

### 27. colchicine-secondary-cv-prevention / 39166327 — NO_CAPTURED_COMPLEMENT

> Compared with placebo, colchicine therapy significantly increased the minimal fibrous cap thickness (51.9 [95% CI, 32.8 to 71.0] μm versus 87.2 [95% CI, 69.9 to 104.5] μm; difference, 34.2 [95% CI, 9.7 to 58.6] μm; P=0.006), and reduced average lipid arc (-25.2° [95% CI, -30.6° to -19.9°] versus -35.7° [95% CI, -40.5° to -30.8°]; difference, -10.5° [95% CI, -17.7° to -3.4°]; P=0.004), mean angular extension of macrophages (-8.9° [95% CI, -13.3° to -4.6°] versus -14.0° [95% CI, -18.0° to -10.0°]; difference, -6.0° [95% CI, -11.8° to -0.2°]; P=0.044), high-sensitivity C-reactive protein level (geometric mean ratio, 0.6 [95% CI, 0.4 to 1.0] versus 0.3 [95% CI, 0.2 to 0.5]; difference, 0.5 [95% CI, 0.3 to 1.0]; P=0.046), interleukin-6 level (geometric mean ratio, 0.8 [95% CI, 0.6 to 1.1] versus 0.5 [95% CI, 0.4 to 0.7]; difference, 0.6 [95% CI, 0.4 to 0.9]; P=0.025), and myeloperoxidase level (geometric mean ratio, 1.0 [95% CI, 0.8 to 1.2] versus 0.8 [95% CI, 0.7 to 0.9]; difference, 0.8 [95% CI, 0.6 to 1.0]; P=0.047).

Baseline effect+CI matches: `[]`.

### 28. colchicine-secondary-cv-prevention / 39115262 — NO_CAPTURED_COMPLEMENT

> Recent landmark trials showed that colchicine provides a substantial benefit in reducing major cardiovascular events in patients with coronary artery disease.

Baseline effect+CI matches: `[]`.

### 29. colchicine-secondary-cv-prevention / 39115262 — NO_CAPTURED_COMPLEMENT

> Overall, our study suggests that treatment with colchicine affects neutrophil function, particularly by reducing neutrophil recruitment, lowering concentrations of NGAL, and changing the expression of various genes with immunomodulatory potential, whereas the effect on monocytes is limited.

Baseline effect+CI matches: `[]`.

### 30. colchicine-secondary-cv-prevention / 34876021 — NO_CAPTURED_COMPLEMENT

> So in order to find out the effects of this drug we conducted this trial to know whether it reduces major adverse cardiac events (MACE) in ACS patients or not.

Baseline effect+CI matches: `[]`.

### 31. colchicine-secondary-cv-prevention / 34876021 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: The addition of colchicine to standard medical therapy in ACS patients significantly reduces MACE occurrence and improves survival rate over the time.

Baseline effect+CI matches: `[]`.

### 32. colchicine-secondary-cv-prevention / 34420373 — NO_CAPTURED_COMPLEMENT

> We hypothesized that colchicine, a potent anti-inflammatory agent, may reduce infarct size (IS) and left ventricular (LV) remodeling at the acute phase of ST-segment-elevation myocardial infarction.

Baseline effect+CI matches: `[]`.

### 33. colchicine-secondary-cv-prevention / 34420373 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In this randomized, placebo-controlled trial, oral administration of high-dose colchicine at the time of reperfusion and for 5 days did not reduce IS assessed by cardiac magnetic resonance imaging.

Baseline effect+CI matches: `[]`.

### 34. colchicine-secondary-cv-prevention / 32865380 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Evidence from a recent trial has shown that the antiinflammatory effects of colchicine reduce the risk of cardiovascular events in patients with recent myocardial infarction, but evidence of such a risk reduction in patients with chronic coronary disease is limited.

Baseline effect+CI matches: `[]`.

### 35. colchicine-secondary-cv-prevention / 31284074 — NO_CAPTURED_COMPLEMENT

> Colchicine is a unique anti-inflammatory medication that has shown promise in reducing such events in patients with stable coronary heart disease.

Baseline effect+CI matches: `[]`.

### 36. colchicine-secondary-cv-prevention / 31284074 — NO_CAPTURED_COMPLEMENT

> The current study tested the ability of low dose colchicine to reduce CRP levels at 30 days after an acute MI, a key marker of future outcome, and its safety and tolerability in this setting.

Baseline effect+CI matches: `[]`.

### 37. colchicine-secondary-cv-prevention / 31284074 — NO_CAPTURED_COMPLEMENT

> The median absolute reduction in CRP levels was -4.3 mg/L (IQR -1.1 to -14.1) among colchicine treated patients and -3.3 mg/L (IQR -0.9 to -14.4, P = .44) in placebo treated patients.

Baseline effect+CI matches: `[]`.

### 38. colchicine-secondary-cv-prevention / 31284074 — NO_CAPTURED_COMPLEMENT

> The relative reduction was a fall of 78% compared to a fall of 64% (P = .09).

Baseline effect+CI matches: `[]`.

### 39. colchicine-secondary-cv-prevention / 31284074 — NO_CAPTURED_COMPLEMENT

> Low dose colchicine was well tolerated and did not reduce compliance with other secondary preventative medications at 30-days.

Baseline effect+CI matches: `[]`.

### 40. colchicine-secondary-cv-prevention / 26265659 — NO_CAPTURED_COMPLEMENT

> The purpose of this study was to test the hypothesis that a short course of colchicine treatment could lead to reduced infarct size.

Baseline effect+CI matches: `[]`.

### 41. colchicine-secondary-cv-prevention / 1593057 — NO_CAPTURED_COMPLEMENT

> The quantitative mean lumen diameter stenosis before angioplasty was 67% both in the 152 lesions in the placebo-treated group and in the 241 lesions in the colchicine-treated group; this value was reduced to 24% immediately after angioplasty in the lesions in both treatment groups.

Baseline effect+CI matches: `[]`.

### 42. corticosteroids-cap-mortality / 15557131 — NO_CAPTURED_COMPLEMENT

> We hypothesize that hydrocortisone infusion in severe community-acquired pneumonia attenuates systemic inflammation and leads to earlier resolution of pneumonia and a reduction in sepsis-related complications.

Baseline effect+CI matches: `[]`.

### 43. corticosteroids-cap-mortality / 15557131 — NO_CAPTURED_COMPLEMENT

> Primary end-points of the study were improvement in Pa(O(2)):FI(O(2)) (Pa(O(2)):FI(O(2)) > 300 or >/= 100 increase from study entry) and multiple organ dysfunction syndrome (MODS) score by Study Day 8 and reduction in delayed septic shock.

Baseline effect+CI matches: `[]`.

### 44. corticosteroids-cap-mortality / 15557131 — NO_CAPTURED_COMPLEMENT

> By Study Day 8, treated patients had, compared with control subjects, a significant improvement in Pa(O(2)):FI(O(2)) (p = 0.002) and chest radiograph score (p < 0.0001), and a significant reduction in C-reactive protein levels (p = 0.01), MODS score (p = 0.003), and delayed septic shock (p = 0.001).

Baseline effect+CI matches: `[]`.

### 45. corticosteroids-cap-mortality / 15557131 — NO_CAPTURED_COMPLEMENT

> Hydrocortisone treatment was associated with a significant reduction in length of hospital stay (p = 0.03) and mortality (p = 0.009).

Baseline effect+CI matches: `[]`.

### 46. corticosteroids-cap-mortality / 35723686 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In patients with severe CAP, prolonged low-dose methylprednisolone treatment did not significantly reduce 60-day mortality.

Baseline effect+CI matches: `[]`.

### 47. corticosteroids-cap-mortality / 25688779 — NO_CAPTURED_COMPLEMENT

> Corticosteroid treatment reduced the risk of treatment failure (odds ratio, 0.34 [95% CI, 0.14 to 0.87]; P = .02).

Baseline effect+CI matches: `[['OR', 0.34, 0.14, 0.87]]`.

### 48. corticosteroids-cap-mortality / 33446608 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Adjunctive intravenous corticosteroid treatment has been shown to reduce length of stay (LOS) in adults hospitalised with community-acquired pneumonia (CAP).

Baseline effect+CI matches: `[]`.

### 49. corticosteroids-cap-mortality / 33446608 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Oral dexamethasone reduced LOS and ICU admission rate in adults hospitalised with CAP.

Baseline effect+CI matches: `[]`.

### 50. corticosteroids-cap-mortality / 25608756 — NO_CAPTURED_COMPLEMENT

> We assessed whether short-term corticosteroid treatment reduces time to clinical stability in patients admitted to hospital for community-acquired pneumonia.

Baseline effect+CI matches: `[]`.

### 51. corticosteroids-cap-mortality / 21636122 — NO_CAPTURED_COMPLEMENT

> INTERPRETATION: Dexamethasone can reduce length of hospital stay when added to antibiotic treatment in non-immunocompromised patients with community-acquired pneumonia.

Baseline effect+CI matches: `[]`.

### 52. corticosteroids-covid19-mortality / 32678530 — NO_CAPTURED_COMPLEMENT

> Glucocorticoids may modulate inflammation-mediated lung injury and thereby reduce progression to respiratory failure and death.

Baseline effect+CI matches: `[]`.

### 53. corticosteroids-covid19-mortality / 32876689 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS AND RELEVANCE: In this study of critically ill patients with COVID-19 and acute respiratory failure, low-dose hydrocortisone, compared with placebo, did not significantly reduce treatment failure (defined as death or persistent respiratory support) at day 21.

Baseline effect+CI matches: `[]`.

### 54. corticosteroids-covid19-mortality / 32785710 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: The findings of this study suggest that a short course of MP in hospitalized patients with COVID-19 did not reduce mortality in the overall population.

Baseline effect+CI matches: `[]`.

### 55. dapagliflozin-hfpef-hosp / 36027570 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Sodium-glucose cotransporter 2 (SGLT2) inhibitors reduce the risk of hospitalization for heart failure and cardiovascular death among patients with chronic heart failure and a left ventricular ejection fraction of 40% or less.

Baseline effect+CI matches: `[]`.

### 56. dapagliflozin-hfpef-hosp / 36027570 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Dapagliflozin reduced the combined risk of worsening heart failure or cardiovascular death among patients with heart failure and a mildly reduced or preserved ejection fraction.

Baseline effect+CI matches: `[]`.

### 57. dapagliflozin-hfpef-hosp / 34711976 — NO_CAPTURED_COMPLEMENT

> Dapagliflozin also improved 6MWT (mean effect size of 20.1 m (95% CI 5.6-34.7, P = 0.007)), KCCQ-OS (4.5 points (95% CI 1.1-7.8, P = 0.009)), proportion of participants with 5-point or greater improvements in KCCQ-OS (odds ratio (OR) = 1.73 (95% CI 1.05-2.85, P = 0.03)) and reduced weight (mean effect size, 0.72 kg (95% CI 0.01-1.42, P = 0.046)).

Baseline effect+CI matches: `[['OR', 1.73, 1.05, 2.85]]`.

### 58. dapagliflozin-hfpef-hosp / 37534453 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Sodium-glucose cotransporter-2 inhibitors reduce risk of hospitalization for heart failure in patients who have heart failure with preserved ejection fraction (HFpEF), but the hemodynamic mechanisms underlying these benefits remain unclear.

Baseline effect+CI matches: `[]`.

### 59. dapagliflozin-hfpef-hosp / 37534453 — NO_CAPTURED_COMPLEMENT

> Treatment with dapagliflozin resulted in reduction in the primary end point of change in PCWP at rest and during exercise at 24 weeks relative to treatment with placebo (likelihood ratio test for overall changes in PCWP; P<0.001), with lower PCWP at rest (estimated treatment difference [ETD], -3.5 mm Hg [95% CI, -6.6 to -0.4]; P=0.029) and maximal exercise (ETD, -5.7 mm Hg [95% CI, -10.8 to -0.7]; P=0.027).

Baseline effect+CI matches: `[]`.

### 60. dapagliflozin-hfpef-hosp / 37534453 — NO_CAPTURED_COMPLEMENT

> Body weight was reduced with dapagliflozin (ETD, -3.5 kg [95% CI, -5.9 to -1.1]; P=0.006), as was plasma volume (ETD, -285 mL [95% CI, -510 to -60]; P=0.014), but there was no significant effect on red blood cell volume.

Baseline effect+CI matches: `[]`.

### 61. dapagliflozin-hfpef-hosp / 37534453 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In patients with HFpEF, treatment with dapagliflozin reduces resting and exercise PCWP, along with the favorable effects on plasma volume and body weight.

Baseline effect+CI matches: `[]`.

### 62. denosumab-vertebral-fracture / 19671655 — NO_CAPTURED_COMPLEMENT

> RESULTS: As compared with placebo, denosumab reduced the risk of new radiographic vertebral fracture, with a cumulative incidence of 2.3% in the denosumab group, versus 7.2% in the placebo group (risk ratio, 0.32; 95% confidence interval [CI], 0.26 to 0.41; P<0.001)--a relative decrease of 68%.

Baseline effect+CI matches: `[['RR', 0.32, 0.26, 0.41]]`.

### 63. denosumab-vertebral-fracture / 19671655 — NO_CAPTURED_COMPLEMENT

> Denosumab reduced the risk of hip fracture, with a cumulative incidence of 0.7% in the denosumab group, versus 1.2% in the placebo group (hazard ratio, 0.60; 95% CI, 0.37 to 0.97; P=0.04)--a relative decrease of 40%.

Baseline effect+CI matches: `[['HR', 0.6, 0.37, 0.97]]`.

### 64. denosumab-vertebral-fracture / 19671655 — NO_CAPTURED_COMPLEMENT

> Denosumab also reduced the risk of nonvertebral fracture, with a cumulative incidence of 6.5% in the denosumab group, versus 8.0% in the placebo group (hazard ratio, 0.80; 95% CI, 0.67 to 0.95; P=0.01)--a relative decrease of 20%.

Baseline effect+CI matches: `[['HR', 0.8, 0.67, 0.95]]`.

### 65. denosumab-vertebral-fracture / 19671655 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Denosumab given subcutaneously twice yearly for 36 months was associated with a reduction in the risk of vertebral, nonvertebral, and hip fractures in women with osteoporosis.

Baseline effect+CI matches: `[]`.

### 66. dpp4-mace-t2d / 23992601 — NO_CAPTURED_COMPLEMENT

> Although saxagliptin improves glycemic control, other approaches are necessary to reduce cardiovascular risk in patients with diabetes.

Baseline effect+CI matches: `[]`.

### 67. dpp4-mace-t2d / 30418475 — NO_CAPTURED_COMPLEMENT

> DESIGN, SETTING, AND PARTICIPANTS: Randomized, placebo-controlled, multicenter noninferiority trial conducted from August 2013 to August 2016 at 605 clinic sites in 27 countries among adults with type 2 diabetes, hemoglobin A1c of 6.5% to 10.0%, high CV risk (history of vascular disease and urine-albumin creatinine ratio [UACR] >200 mg/g), and high renal risk (reduced eGFR and micro- or macroalbuminuria).

Baseline effect+CI matches: `[]`.

### 68. empagliflozin-hfpef-hosp / 34449189 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Sodium-glucose cotransporter 2 inhibitors reduce the risk of hospitalization for heart failure in patients with heart failure and a reduced ejection fraction, but their effects in patients with heart failure and a preserved ejection fraction are uncertain.

Baseline effect+CI matches: `[]`.

### 69. empagliflozin-hfpef-hosp / 34449189 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Empagliflozin reduced the combined risk of cardiovascular death or hospitalization for heart failure in patients with heart failure and a preserved ejection fraction, regardless of the presence or absence of diabetes.

Baseline effect+CI matches: `[]`.

### 70. esketamine-trd-madrs / 37025256 — NO_CAPTURED_COMPLEMENT

> Rapid reduction in depressive symptoms within 24 hours was observed for TRD patients treated with esketamine plus AD in the overall population and China sub-population.

Baseline effect+CI matches: `[]`.

### 71. finerenone-ckd-t2d-renal / 33264825 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Finerenone, a nonsteroidal, selective mineralocorticoid receptor antagonist, reduced albuminuria in short-term trials involving patients with chronic kidney disease (CKD) and type 2 diabetes.

Baseline effect+CI matches: `[]`.

### 72. finerenone-ckd-t2d-renal / 26325557 — NO_CAPTURED_COMPLEMENT

> IMPORTANCE: Steroidal mineralocorticoid receptor antagonists, when added to a renin-angiotensin system blocker, further reduce proteinuria in patients with chronic kidney disease but may be underused because of a high risk of adverse events.

Baseline effect+CI matches: `[]`.

### 73. finerenone-ckd-t2d-renal / 26325557 — NO_CAPTURED_COMPLEMENT

> Finerenone demonstrated a dose-dependent reduction in UACR.

Baseline effect+CI matches: `[]`.

### 74. finerenone-ckd-t2d-renal / 26325557 — NO_CAPTURED_COMPLEMENT

> The primary outcome, the placebo-corrected mean ratio of the UACR at day 90 relative to baseline, was reduced in the finerenone 7.5-, 10-, 15-, and 20-mg/d groups (for 7.5 mg/d, 0.79 [90% CI, 0.68-0.91; P = .004]; for 10 mg/d, 0.76 [90% CI, 0.65-0.88; P = .001]; for 15 mg/d, 0.67 [90% CI, 0.58-0.77; P<.001]; for 20 mg/d, 0.62 [90% CI, 0.54-0.72; P < .001]).

Baseline effect+CI matches: `[]`.

### 75. glp1-ra-mace-t2d / 34215025 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Four glucagon-like peptide-1 (GLP-1) receptor agonists that are structurally similar to human GLP-1 have been shown to reduce the risk of adverse cardiovascular events among persons with type 2 diabetes.

Baseline effect+CI matches: `[]`.

### 76. glp1-ra-mace-t2d / 31189511 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Three different glucagon-like peptide-1 (GLP-1) receptor agonists reduce cardiovascular outcomes in people with type 2 diabetes at high cardiovascular risk with high glycated haemoglobin A1c (HbA1c) concentrations.

Baseline effect+CI matches: `[]`.

### 77. glp1-ra-mace-t2d / 30291013 — NO_CAPTURED_COMPLEMENT

> Evidence-based glucagon-like peptide 1 receptor agonists should therefore be considered as part of a comprehensive strategy to reduce the risk of cardiovascular events in patients with type 2 diabetes.

Baseline effect+CI matches: `[]`.

### 78. iv-iron-hfref-hosp / 40159390 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS AND RELEVANCE: In patients with heart failure and iron deficiency, ferric carboxymaltose did not significantly reduce the time to first heart failure hospitalization or cardiovascular death in the overall cohort or in patients with a transferrin saturation less than 20%, or reduce the total number of heart failure hospitalizations vs placebo.

Baseline effect+CI matches: `[]`.

### 79. iv-iron-hfref-hosp / 33197395 — NO_CAPTURED_COMPLEMENT

> INTERPRETATION: In patients with iron deficiency, a left ventricular ejection fraction of less than 50%, and who were stabilised after an episode of acute heart failure, treatment with ferric carboxymaltose was safe and reduced the risk of heart failure hospitalisations, with no apparent effect on the risk of cardiovascular death.

Baseline effect+CI matches: `[]`.

### 80. iv-iron-hfref-hosp / 36347265 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: For patients with heart failure, reduced left ventricular ejection fraction and iron deficiency, intravenous ferric carboxymaltose administration improves quality of life and exercise capacity in the short-term and reduces hospital admissions for heart failure up to 1 year.

Baseline effect+CI matches: `[]`.

### 81. iv-iron-hfref-hosp / 36347265 — NO_CAPTURED_COMPLEMENT

> INTERPRETATION: For a broad range of patients with heart failure, reduced left ventricular ejection fraction and iron deficiency, intravenous ferric derisomaltose administration was associated with a lower risk of hospital admissions for heart failure and cardiovascular death, further supporting the benefit of iron repletion in this population.

Baseline effect+CI matches: `[]`.

### 82. iv-iron-hfref-hosp / 37632463 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Ferric carboxymaltose therapy reduces symptoms and improves quality of life in patients who have heart failure with a reduced ejection fraction and iron deficiency.

Baseline effect+CI matches: `[]`.

### 83. iv-iron-hfref-hosp / 37632463 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Among ambulatory patients who had heart failure with a reduced ejection fraction and iron deficiency, there was no apparent difference between ferric carboxymaltose and placebo with respect to the hierarchical composite of death, hospitalizations for heart failure, or 6-minute walk distance.

Baseline effect+CI matches: `[]`.

### 84. iv-iron-hfref-hosp / 28701470 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Iron deficiency is common in patients with heart failure (HF) and is associated with reduced exercise capacity and poor outcomes.

Baseline effect+CI matches: `[]`.

### 85. iv-iron-hfref-hosp / 25176939 — NO_CAPTURED_COMPLEMENT

> Treatment with FCM was associated with a significant reduction in the risk of hospitalizations for worsening HF [hazard ratio (95% confidence interval): 0.39 (0.19-0.82), P = 0.009].

Baseline effect+CI matches: `[]`.

### 86. iv-iron-hfref-hosp / 25176939 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Treatment of symptomatic, iron-deficient HF patients with FCM over a 1-year period resulted in sustainable improvement in functional capacity, symptoms, and QoL and may be associated with risk reduction of hospitalization for worsening HF (ClinicalTrials.gov number NCT01453608).

Baseline effect+CI matches: `[]`.

### 87. iv-iron-hfref-hosp / 19920054 — NO_CAPTURED_COMPLEMENT

> This study aimed to determine whether treatment with intravenous iron (ferric carboxymaltose) would improve symptoms in patients who had heart failure, reduced left ventricular ejection fraction, and iron deficiency, either with or without anemia.

Baseline effect+CI matches: `[]`.

### 88. melatonin-primary-insomnia-sol / 20712869 — NO_CAPTURED_COMPLEMENT

> RESULTS: On the primary efficacy variable, sleep latency, the effects of PRM (3 weeks) in patients with low endogenous melatonin (6-sulphatoxymelatonin [6-SMT] <or=8 microg/night) regardless of age did not differ from the placebo, whereas PRM significantly reduced sleep latency compared to the placebo in elderly patients regardless of melatonin levels (-19.1 versus -1.7 min; P = 0.002).

Baseline effect+CI matches: `[]`.

### 89. metformin-pcos-ovulation / 19522426 — NO_CAPTURED_COMPLEMENT

> Metformin effect was, in our study, his only insulinosensitizer property consequence far away a 'making thinner' or Hyperandrogenism reducing ones.

Baseline effect+CI matches: `[]`.

### 90. metformin-pcos-ovulation / 11473953 — NO_CAPTURED_COMPLEMENT

> There was no improvement in the ovulation rate despite a significant reduction of body mass index, serum testosterone and fasting leptin concentrations in the metformin group.

Baseline effect+CI matches: `[]`.

### 91. noac-vs-warfarin-af-stroke / 21830957 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: The use of warfarin reduces the rate of ischemic stroke in patients with atrial fibrillation but requires frequent monitoring and dose adjustment.

Baseline effect+CI matches: `[]`.

### 92. noac-vs-warfarin-af-stroke / 21830957 — NO_CAPTURED_COMPLEMENT

> Major and nonmajor clinically relevant bleeding occurred in 1475 patients in the rivaroxaban group (14.9% per year) and in 1449 in the warfarin group (14.5% per year) (hazard ratio, 1.03; 95% CI, 0.96 to 1.11; P=0.44), with significant reductions in intracranial hemorrhage (0.5% vs. 0.7%, P=0.02) and fatal bleeding (0.2% vs. 0.5%, P=0.003) in the rivaroxaban group.

Baseline effect+CI matches: `[['HR', 1.03, 0.96, 1.11]]`.

### 93. noac-vs-warfarin-af-stroke / 19717844 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Warfarin reduces the risk of stroke in patients with atrial fibrillation but increases the risk of hemorrhage and is difficult to use.

Baseline effect+CI matches: `[]`.

### 94. noac-vs-warfarin-af-stroke / 21870978 — NO_CAPTURED_COMPLEMENT

> Apixaban is a novel oral direct factor Xa inhibitor that has been shown to reduce the risk of stroke in a similar population in comparison with aspirin.

Baseline effect+CI matches: `[]`.

### 95. omega3-cardiovascular-events / 33190147 — NO_CAPTURED_COMPLEMENT

> IMPORTANCE: It remains uncertain whether the omega-3 fatty acids eicosapentaenoic acid (EPA) and docosahexaenoic acid (DHA) reduce cardiovascular risk.

Baseline effect+CI matches: `[]`.

### 96. omega3-cardiovascular-events / 33190147 — NO_CAPTURED_COMPLEMENT

> These findings do not support use of this omega-3 fatty acid formulation to reduce major adverse cardiovascular events in high-risk patients.

Baseline effect+CI matches: `[]`.

### 97. omega3-cardiovascular-events / 30415637 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Higher intake of marine n-3 (also called omega-3) fatty acids has been associated with reduced risks of cardiovascular disease and cancer in several observational studies.

Baseline effect+CI matches: `[]`.

### 98. omega3-cardiovascular-events / 30415628 — NO_CAPTURED_COMPLEMENT

> (Funded by Amarin Pharma; REDUCE-IT ClinicalTrials.gov number, NCT01492361 .).

Baseline effect+CI matches: `[]`.

### 99. omega3-cardiovascular-events / 30146932 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Increased intake of n-3 fatty acids has been associated with a reduced risk of cardiovascular disease in observational studies, but this finding has not been confirmed in randomized trials.

Baseline effect+CI matches: `[]`.

### 100. omega3-cardiovascular-events / 23839902 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Despite an inverse relationship between plasma n-3 PUFA levels and prevalent AF, this study found no evidence that 1 g daily n-3 PUFA supplementation in patients with chronic HF reduces incident AF.

Baseline effect+CI matches: `[]`.

### 101. omega3-cardiovascular-events / 23656645 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In a large general-practice cohort of patients with multiple cardiovascular risk factors, daily treatment with n-3 fatty acids did not reduce cardiovascular mortality and morbidity.

Baseline effect+CI matches: `[]`.

### 102. omega3-cardiovascular-events / 22686415 — NO_CAPTURED_COMPLEMENT

> Triglyceride levels were reduced by 14.5 mg per deciliter (0.16 mmol per liter) more among patients receiving n-3 fatty acids than among those receiving placebo (P<0.001), without a significant effect on other lipids.

Baseline effect+CI matches: `[]`.

### 103. omega3-cardiovascular-events / 22686415 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Daily supplementation with 1 g of n-3 fatty acids did not reduce the rate of cardiovascular events in patients at high risk for cardiovascular events.

Baseline effect+CI matches: `[]`.

### 104. omega3-cardiovascular-events / 20929341 — NO_CAPTURED_COMPLEMENT

> Neither EPA-DHA nor ALA reduced this primary end point (hazard ratio with EPA-DHA, 1.01; 95% confidence interval [CI], 0.87 to 1.17; P=0.93; hazard ratio with ALA, 0.91; 95% CI, 0.78 to 1.05; P=0.20).

Baseline effect+CI matches: `[['HR', 1.01, 0.87, 1.17], ['HR', 0.91, 0.78, 1.05]]`.

### 105. omega3-cardiovascular-events / 20929341 — NO_CAPTURED_COMPLEMENT

> In the prespecified subgroup of women, ALA, as compared with placebo and EPA-DHA alone, was associated with a reduction in the rate of major cardiovascular events that approached significance (hazard ratio, 0.73; 95% CI, 0.51 to 1.03; P=0.07).

Baseline effect+CI matches: `[['HR', 0.73, 0.51, 1.03]]`.

### 106. omega3-cardiovascular-events / 20929341 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Low-dose supplementation with EPA-DHA or ALA did not significantly reduce the rate of major cardiovascular events among patients who had had a myocardial infarction and who were receiving state-of-the-art antihypertensive, antithrombotic, and lipid-modifying therapy.

Baseline effect+CI matches: `[]`.

### 107. omega3-cardiovascular-events / 20146881 — NO_CAPTURED_COMPLEMENT

> Thus, n-3 PUFA can reduce levels of plasma inflammatory markers and NT-proBNP as biomarkers of risk stratification in patients with heart failure. n-3 PUFA may offer a novel therapy for heart failure.

Baseline effect+CI matches: `[]`.

### 108. omega3-cardiovascular-events / 11451717 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Results of epidemiologic studies and clinical trials indicate that moderate doses of n-3 fatty acids reduce the risk of cardiovascular disease and may improve prognosis.

Baseline effect+CI matches: `[]`.

### 109. omega3-cardiovascular-events / 20389249 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: We observed a tendency toward reduction in all-cause mortality in the n-3 PUFA groups that, despite a low number of participants, reached borderline statistical significance.

Baseline effect+CI matches: `[]`.

### 110. omega3-cardiovascular-events / 20389249 — NO_CAPTURED_COMPLEMENT

> The magnitude of risk-reduction suggests that a larger trial should be considered in similar populations.

Baseline effect+CI matches: `[]`.

### 111. omega3-cardiovascular-events / 21060071 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Guideline-adjusted treatment of acute myocardial infarction results in a low rate of sudden cardiac death and other clinical events within 1 year of follow-up, which could not be shown to be further reduced by the application of omega-3 fatty acids.

Baseline effect+CI matches: `[]`.

### 112. omega3-cardiovascular-events / 38184150 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Omega-3 polyunsaturated fatty acids (O3-FA) have been shown to reduce inflammation and adverse cardiac remodeling after acute myocardial infarction (AMI).

Baseline effect+CI matches: `[]`.

### 113. omega3-cardiovascular-events / 38184150 — NO_CAPTURED_COMPLEMENT

> By intention-to-treat analysis, O3-FA treatment assignment did not reduce MACE (HR = 1.014; 95%CI = 0.716-1.436; p = 0.938), or its individual components.

Baseline effect+CI matches: `[['HR', 1.014, 0.716, 1.436]]`.

### 114. omega3-cardiovascular-events / 38184150 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: In long-term follow-up of the OMEGA-REMODEL randomized trial, O3-FA did not reduce MACE after AMI by intention to treat principle, however, patients who achieved a ≥ 5% increase of O3I subsequent to treatment had favorable outcomes.

Baseline effect+CI matches: `[]`.

### 115. omega3-cardiovascular-events / 38199870 — NO_CAPTURED_COMPLEMENT

> However, neither omega-3 (adjustedHR 1.00, 95%CI 0.64-1.56), nor vitamin D3 (aHR 1.37, 95%CI 0.88-2.14), nor SHEP (aHR 1.18, 95%CI 0.76-1.84) reduced risk of MACE or incident hypertension compared to control.

Baseline effect+CI matches: `[]`.

### 116. pcsk9-mace / 28304224 — NO_CAPTURED_COMPLEMENT

> RESULTS: At 48 weeks, the least-squares mean percentage reduction in LDL cholesterol levels with evolocumab, as compared with placebo, was 59%, from a median baseline value of 92 mg per deciliter (2.4 mmol per liter) to 30 mg per deciliter (0.78 mmol per liter) (P<0.001).

Baseline effect+CI matches: `[]`.

### 117. pcsk9-mace / 28304224 — NO_CAPTURED_COMPLEMENT

> Relative to placebo, evolocumab treatment significantly reduced the risk of the primary end point (1344 patients [9.8%] vs. 1563 patients [11.3%]; hazard ratio, 0.85; 95% confidence interval [CI], 0.79 to 0.92; P<0.001) and the key secondary end point (816 [5.9%] vs. 1013 [7.4%]; hazard ratio, 0.80; 95% CI, 0.73 to 0.88; P<0.001).

Baseline effect+CI matches: `[['HR', 0.85, 0.79, 0.92], ['HR', 0.8, 0.73, 0.88]]`.

### 118. pcsk9-mace / 28304224 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In our trial, inhibition of PCSK9 with evolocumab on a background of statin therapy lowered LDL cholesterol levels to a median of 30 mg per deciliter (0.78 mmol per liter) and reduced the risk of cardiovascular events.

Baseline effect+CI matches: `[]`.

### 119. pcsk9-mace / 41211925 — NO_CAPTURED_COMPLEMENT

> The proprotein convertase subtilisin-kexin type 9 (PCSK9) inhibitor evolocumab reduces the risk of major adverse cardiovascular events (MACE) among patients with a previous myocardial infarction, stroke, or symptomatic peripheral artery disease.

Baseline effect+CI matches: `[]`.

### 120. pcsk9-mace / 25773378 — NO_CAPTURED_COMPLEMENT

> Alirocumab, a monoclonal antibody that inhibits proprotein convertase subtilisin-kexin type 9 (PCSK9), has been shown to reduce low-density lipoprotein (LDL) cholesterol levels in patients who are receiving statin therapy.

Baseline effect+CI matches: `[]`.

### 121. pcsk9-mace / 25773378 — NO_CAPTURED_COMPLEMENT

> Over a period of 78 weeks, alirocumab, when added to statin therapy at the maximum tolerated dose, significantly reduced LDL cholesterol levels.

Baseline effect+CI matches: `[]`.

### 122. pcsk9-mace / 25773378 — NO_CAPTURED_COMPLEMENT

> In a post hoc analysis, there was evidence of a reduction in the rate of cardiovascular events with alirocumab.

Baseline effect+CI matches: `[]`.

### 123. pcsk9-mace / 27846344 — NO_CAPTURED_COMPLEMENT

> Reducing levels of low-density lipoprotein cholesterol (LDL-C) with intensive statin therapy reduces progression of coronary atherosclerosis in proportion to achieved LDL-C levels.

Baseline effect+CI matches: `[]`.

### 124. probiotics-aad-prevention / 41699149 — NO_CAPTURED_COMPLEMENT

> This hypothesis is supported by the participants who used broad spectrum penicillins had a significantly higher rate of diarrhea compared to narrow spectrum antibiotic users, 9.1% and 0.51% respectively, (p=0.004)This study suggests that prescribing short-course, narrow spectrum antibiotics can reduce microbiome disruptions, concomitant AAD, and the need for probiotic intervention. .

Baseline effect+CI matches: `[]`.

### 125. probiotics-aad-prevention / 40548185 — NO_CAPTURED_COMPLEMENT

> LA85 supplementation was associated with a trend toward a reduction in the incidence of AAD; however, this difference did not reach statistical significance.

Baseline effect+CI matches: `[]`.

### 126. probiotics-aad-prevention / 40548185 — NO_CAPTURED_COMPLEMENT

> Importantly, exploratory subgroup analysis revealed that in younger participants (< 53 years age), LA85 supplementation significantly reduced the incidence of AAD (p = 0.008) and effectively eliminated persistent diarrhea episodes.

Baseline effect+CI matches: `[]`.

### 127. probiotics-aad-prevention / 40488914 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: This first study with L. reuteri DSM 17938 in a large pediatric outpatient setting showed significant reduction of AAD during the first 14 days of antibiotic use and the 8-week follow-up period.

Baseline effect+CI matches: `[]`.

### 128. probiotics-aad-prevention / 40488914 — NO_CAPTURED_COMPLEMENT

> WHAT IS NEW: • Limosilactobacillus reuteri DSM 17938 significantly reduced the incidence of AAD in children at 14-, 21-, and 56- days follow-up. • The effect is mainly observed in children aged between 6 and 24 months or children with AOM.

Baseline effect+CI matches: `[]`.

### 129. probiotics-aad-prevention / 39935568 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Results of this pilot study indicate that LGG is safe and could potentially reduce the incidence of AAD in the critically ill pediatric patients at this academic institution.

Baseline effect+CI matches: `[]`.

### 130. probiotics-aad-prevention / 39529939 — NO_CAPTURED_COMPLEMENT

> AAD occurred less frequently in the studied probiotic mix versus placebo group (9.2% vs 25.3%, P < .001), resulting in an absolute risk reduction of 16% and a number needed to treat of 6 (95% confidence interval, 4.55-10.49).

Baseline effect+CI matches: `[]`.

### 131. probiotics-aad-prevention / 39497860 — NO_CAPTURED_COMPLEMENT

> OBJECTIVE: The aim of this investigation was to assess the efficacy of probiotics in reducing AAD in adult patients when compared to a placebo.

Baseline effect+CI matches: `[]`.

### 132. probiotics-aad-prevention / 39497860 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Probiotics significantly reduced the incidence and duration of AAD compared to placebo, with high adherence and favorable patient-reported outcomes.

Baseline effect+CI matches: `[]`.

### 133. probiotics-aad-prevention / 39429834 — NO_CAPTURED_COMPLEMENT

> Further, yogurt intervention was found to be effective in terms of increasing the consistency of the stool (p. 001*), decreasing the duration and onset of diarrhea (P ≤ .001*), reducing the frequency and amount of loose stool (P ≤ .001*), reducing the urgency of defecation (P ≤ .001*), the presence of abdominal discomfort (P ≤ .001*), and dehydration (P ≤ .001*).

Baseline effect+CI matches: `[]`.

### 134. probiotics-aad-prevention / 38258024 — NO_CAPTURED_COMPLEMENT

> An important role in the prevention of antibiotic-associated diarrhea is carried out by some probiotic strains such as Lactobacillus GG or the yeast Saccharomyces boulardii that showed good efficacy and a significant reduction in antibiotic-associated diarrhea.

Baseline effect+CI matches: `[]`.

### 135. probiotics-aad-prevention / 38258024 — NO_CAPTURED_COMPLEMENT

> Similarly, the Limosilactobacillus reuteri DSM 17938 showed significant benefits in acute diarrhea, reducing its duration and abdominal pain.

Baseline effect+CI matches: `[]`.

### 136. probiotics-aad-prevention / 38258024 — NO_CAPTURED_COMPLEMENT

> AIM: The aim of this study was to test the efficacy of a mix of two probiotic strains (Limosilactobacillus reuteri LMG P-27481 and Lacticaseibacillus rhamnosus GG ATCC 53103; Reuterin GG®, NOOS, Italy), in association with antibiotics (compared to antibiotics used alone), in reducing antibiotic-associated diarrhea, clostridium difficile infection, and other gastrointestinal symptoms in adult hospitalized patients.

Baseline effect+CI matches: `[]`.

### 137. probiotics-aad-prevention / 38258024 — NO_CAPTURED_COMPLEMENT

> RESULTS: Patients treated with Reuterin GG® showed a significant reduction in diarrhea and clostridium difficile infection.

Baseline effect+CI matches: `[]`.

### 138. probiotics-aad-prevention / 35727573 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS AND RELEVANCE: A multispecies probiotic did not reduce the risk of AAD in children when analyzed according to the most stringent definition.

Baseline effect+CI matches: `[]`.

### 139. probiotics-aad-prevention / 35727573 — NO_CAPTURED_COMPLEMENT

> However, it reduced the overall risk of diarrhea during and for 7 days after antibiotic treatment.

Baseline effect+CI matches: `[]`.

### 140. probiotics-aad-prevention / 33032474 — NO_CAPTURED_COMPLEMENT

> There was a significantly higher reduction in the AAD incidence, and an improvement in the stool consistency in the active group.

Baseline effect+CI matches: `[]`.

### 141. probiotics-aad-prevention / 33032474 — NO_CAPTURED_COMPLEMENT

> A higher reduction in both the frequency and duration of the diarrhoea episodes in the active group was also observed, as it was an improved perception of the diarrhoea severity.

Baseline effect+CI matches: `[]`.

### 142. probiotics-aad-prevention / 32035998 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Antibiotic-associated diarrhoea (AAD) is a side-effect of antibiotic consumption and probiotics have been shown to reduce AAD.

Baseline effect+CI matches: `[]`.

### 143. probiotics-aad-prevention / 32035998 — NO_CAPTURED_COMPLEMENT

> METHODS: A multicentre, double-blind, placebo-controlled, randomized trial was conducted to evaluate the role of Lactobacillus casei DN114001 (combined as a drink with two regular yoghurt bacterial strains) in reducing AAD and Clostridioides difficile infection in patients aged over 55 years.

Baseline effect+CI matches: `[]`.

### 144. probiotics-aad-prevention / 30439760 — NO_CAPTURED_COMPLEMENT

> The rate of diarrhea was 23.0% in the probiotic group versus 17.6% in the placebo group, absolute risk reduction -5.35% (95% confidence interval, -15.4% to 4.7%; P=0.30).

Baseline effect+CI matches: `[]`.

### 145. probiotics-aad-prevention / 30149135 — NO_CAPTURED_COMPLEMENT

> Using the strictest definition (i.e. definition (i)), the occurrence of diarrhoea in the L. reuteri group was 25 (20%) compared with 16 (13%) in the placebo group (absolute risk reduction -0.07 (-0.17 to 0.02).

Baseline effect+CI matches: `[]`.

### 146. probiotics-aad-prevention / 30149135 — NO_CAPTURED_COMPLEMENT

> The occurrence of AAD was 14 (11.4%) in the L. reuteri group compared with 8 (6.5%) in the placebo group (absolute risk reduction -0.05 (-0.13 to 0.02)).

Baseline effect+CI matches: `[]`.

### 147. probiotics-aad-prevention / 28871492 — NO_CAPTURED_COMPLEMENT

> Our study confirmed that the use of probiotic L. rhamnosus GG associated with antibiotics significantly reduced the incidence and the duration of postoperative AAD.

Baseline effect+CI matches: `[]`.

### 148. probiotics-aad-prevention / 28871492 — NO_CAPTURED_COMPLEMENT

> In addition, the use of probiotics LGG reduced the frequency of dressing changes and the incidence of postoperative complications, such as urethral fistula and foreskin dehiscence.

Baseline effect+CI matches: `[]`.

### 149. probiotics-aad-prevention / 27169634 — NO_CAPTURED_COMPLEMENT

> A post hoc analysis on the duration of diarrhoea-like defecations showed that probiotic intervention reduced the length of these events by 1 full day (probiotic, 2·70 (sem 0·36) d; placebo, 3·71 (sem 0·36) d; P=0·037; effect size=0·52).

Baseline effect+CI matches: `[]`.

### 150. probiotics-aad-prevention / 27169634 — NO_CAPTURED_COMPLEMENT

> In conclusion, this study provides novel evidence that L. helveticus R0052 and L. rhamnosus R0011 supplementation significantly reduced the duration of diarrhoea-like defecations in healthy adults receiving antibiotics.

Baseline effect+CI matches: `[]`.

### 151. probiotics-aad-prevention / 24772726 — NO_CAPTURED_COMPLEMENT

> However, compared to placebo the duration of diarrhoea in the probiotic group was significantly reduced.

Baseline effect+CI matches: `[]`.

### 152. probiotics-aad-prevention / 18701826 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: The administration of the 3 probiotics did not significantly alter the rate of diarrhea, although it reduced the frequency of stools per day.

Baseline effect+CI matches: `[]`.

### 153. probiotics-aad-prevention / 18410562 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Administration of L. rhamnosus (strains E/N, Oxy and Pen) to children receiving antibiotics reduced the risk of any diarrhoea, as defined in this study.

Baseline effect+CI matches: `[]`.

### 154. probiotics-aad-prevention / 16572062 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: The results implied that prophylactic use of Saccharomyces boulardii resulted in reduced, with no serious side effects, antibiotic-associated diarrhea in hospitalized patients.

Baseline effect+CI matches: `[]`.

### 155. probiotics-aad-prevention / 15740542 — NO_CAPTURED_COMPLEMENT

> S. boulardii also reduced the risk of antibiotic-associated diarrhoea (diarrhoea caused by Clostridium difficile or otherwise unexplained diarrhoea) compared with placebo [four of 119 (3.4%) vs. 22 of 127 (17.3%), relative risk: 0.2; 95% confidence interval: 0.07-0.5].

Baseline effect+CI matches: `[['RR', 0.2, 0.07, 0.5]]`.

### 156. probiotics-aad-prevention / 15740542 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: This is the first randomized-controlled trial evidence that S. boulardii effectively reduces the risk of antibiotic-associated diarrhoea in children.

Baseline effect+CI matches: `[]`.

### 157. probiotics-aad-prevention / 11560298 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Lactobacillus GG in a dose of 20 x 10(9) CFU/d did not reduce the rate of occurrence of diarrhea in this sample of 267 adult patients taking antibiotics initially administered in the hospital setting.

Baseline effect+CI matches: `[]`.

### 158. probiotics-aad-prevention / 10547243 — NO_CAPTURED_COMPLEMENT

> OBJECTIVE: The objective of this study was to determine the efficacy of Lactobacillus casei sps. rhamnosus (Lactobacillus GG) (LGG) in reducing the incidence of antibiotic-associated diarrhea when coadministered with an oral antibiotic in children with acute infectious disorders.

Baseline effect+CI matches: `[]`.

### 159. probiotics-aad-prevention / 10547243 — NO_CAPTURED_COMPLEMENT

> Lactobacillus GG overall significantly reduced stool frequency and increased stool consistency during antibiotic therapy by the tenth day compared with the placebo group.

Baseline effect+CI matches: `[]`.

### 160. probiotics-aad-prevention / 10547243 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: Lactobacillus GG reduces the incidence of antibiotic-associated diarrhea in children treated with oral antibiotics for common childhood infections.

Baseline effect+CI matches: `[]`.

### 161. probiotics-aad-prevention / 9570649 — NO_CAPTURED_COMPLEMENT

> Saccharomyces boulardii is a non-pathogenic yeast which has been demonstrated to reduce the frequency of diarrhoea in patients due to a variety of causes.

Baseline effect+CI matches: `[]`.

### 162. probiotics-aad-prevention / 7872284 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: The prophylactic use of S. boulardii given with a beta-lactam antibiotic resulted in a significant reduction of AAD with no serious adverse reactions.

Baseline effect+CI matches: `[]`.

### 163. probiotics-aad-prevention / 24456384 — NO_CAPTURED_COMPLEMENT

> OBJECTIVE: The objective of the study was to evaluate effectiveness of probiotic supplementation in reducing antibiotic-associated diarrhoea (AAD).

Baseline effect+CI matches: `[]`.

### 164. probiotics-aad-prevention / 24456384 — NO_CAPTURED_COMPLEMENT

> METHOD: A double-blind randomised controlled trial (registration number: ACTRN 12609000429257); with primary outcome prevention of AAD and secondary outcome reduction in diarrhoea duration, patients were randomised to receive probiotic supplementation with Lactobacillus casei, Shirota strain or placebo.

Baseline effect+CI matches: `[]`.

### 165. probiotics-aad-prevention / 24044687 — NO_CAPTURED_COMPLEMENT

> The present study aimed to assess (1) the efficacy of consuming a commercially produced probiotic containing at least 6·5 × 10⁹ live Lactobacillus casei Shirota (LcS) in reducing the incidence of AAD/CDAD, and (2) whether undernutrition and proton pump inhibitors (PPI) are risk factors for AAD/CDAD.

Baseline effect+CI matches: `[]`.

### 166. probiotics-aad-prevention / 24044687 — NO_CAPTURED_COMPLEMENT

> The present study indicated that LcS could reduce the incidence of AAD in hospitalised SCI patients.

Baseline effect+CI matches: `[]`.

### 167. probiotics-aad-prevention / 23618760 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: VSL#3 is associated with a significant reduction in the incidence of AAD in average-risk hospital inpatients exposed to systemic antibiotics.

Baseline effect+CI matches: `[]`.

### 168. probiotics-aad-prevention / 22371721 — NO_CAPTURED_COMPLEMENT

> Adjusted multivariate linear regression results showed that the duration of diarrhea for BIO-K+CL1285 (®)vs. placebo was reduced by 51.5% (b[SE] = 0.515 [0.256], p = 0.045).

Baseline effect+CI matches: `[]`.

### 169. probiotics-aad-prevention / 22371721 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: BIO-K+ is effective for preventing and reducing the severity of AAD in patients receiving antibiotic therapy in a hospital setting.

Baseline effect+CI matches: `[]`.

### 170. probiotics-aad-prevention / 21871144 — NO_CAPTURED_COMPLEMENT

> To investigate matrix-specifity of probiotic effects and particularly of the reduction of antibiotics-associated diarrhea, a controlled, randomized, double-blind study was performed, in which 88 Helicobacter pylori-infected but otherwise healthy subjects were given for eight weeks either a) a probiotic fruit yoghurt "mild" containing Lactobacillus acidophilus LA-5 plus Bifidobacterium lactis BB-12, n = 30), b) the same product but pasteurized after fermentation (n = 29) or c) milk acidified with lactic acid (control, n = 29).

Baseline effect+CI matches: `[]`.

### 171. probiotics-aad-prevention / 21165295 — NO_CAPTURED_COMPLEMENT

> Although the Lacidofil® cap does not reduce the rate of occurrence of AAD in adult patients with respiratory tract infection who have taken antibiotics, the Lactobacillus group maintains their bowel habits to a greater extent than the placebo group.

Baseline effect+CI matches: `[]`.

### 172. probiotics-aad-prevention / 20145608 — NO_CAPTURED_COMPLEMENT

> Probiotic prophylaxis is a promising alternative for reduction of AAD and CDAD incidence.

Baseline effect+CI matches: `[]`.

### 173. probiotics-aad-prevention / 20145608 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: The proprietary probiotic blend used in this study was well tolerated and effective for reducing risk of AAD and, in particular, CDAD in hospitalized patients on antibiotics.

Baseline effect+CI matches: `[]`.

### 174. sacubitril-valsartan-hfref / 25176015 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: We compared the angiotensin receptor-neprilysin inhibitor LCZ696 with enalapril in patients who had heart failure with a reduced ejection fraction.

Baseline effect+CI matches: `[]`.

### 175. sacubitril-valsartan-hfref / 25176015 — NO_CAPTURED_COMPLEMENT

> As compared with enalapril, LCZ696 also reduced the risk of hospitalization for heart failure by 21% (P<0.001) and decreased the symptoms and physical limitations of heart failure (P=0.001).

Baseline effect+CI matches: `[]`.

### 176. sacubitril-valsartan-hfref / 25176015 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: LCZ696 was superior to enalapril in reducing the risks of death and of hospitalization for heart failure.

Baseline effect+CI matches: `[]`.

### 177. semaglutide-obesity-mace / 37952131 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Semaglutide, a glucagon-like peptide-1 receptor agonist, has been shown to reduce the risk of adverse cardiovascular events in patients with diabetes.

Baseline effect+CI matches: `[]`.

### 178. semaglutide-obesity-mace / 37952131 — NO_CAPTURED_COMPLEMENT

> Whether semaglutide can reduce cardiovascular risk associated with overweight and obesity in the absence of diabetes is unknown.

Baseline effect+CI matches: `[]`.

### 179. semaglutide-obesity-mace / 37952131 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In patients with preexisting cardiovascular disease and overweight or obesity but without diabetes, weekly subcutaneous semaglutide at a dose of 2.4 mg was superior to placebo in reducing the incidence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke at a mean follow-up of 39.8 months.

Baseline effect+CI matches: `[]`.

### 180. semaglutide-obesity-weight / 42070571 — NO_CAPTURED_COMPLEMENT

> Preclinical and initial human studies indicate that the GLP-1 receptor agonist semaglutide might reduce alcohol drinking.

Baseline effect+CI matches: `[]`.

### 181. semaglutide-obesity-weight / 42070571 — NO_CAPTURED_COMPLEMENT

> The primary endpoint was a reduction in the number of heavy drinking days assessed after 26 weeks of intervention, analysed with an ANCOVA model.

Baseline effect+CI matches: `[]`.

### 182. semaglutide-obesity-weight / 42070571 — NO_CAPTURED_COMPLEMENT

> Semaglutide was associated with a reduction in heavy drinking days (-41·1 percentage points from baseline, 95% CI -48·7 to -33·5) compared with placebo (-26·4, -34·1 to -18·6; estimated treatment difference -13·7 percentage points, -22·0 to -5·4; p=0·0015), and had substantial effects on multiple secondary alcohol-related and somatic outcomes.

Baseline effect+CI matches: `[]`.

### 183. semaglutide-obesity-weight / 40825340 — NO_CAPTURED_COMPLEMENT

> Adults (aged ≥18 years in Thailand and ≥19 years in South Korea) with obesity (BMI ≥25 kg/m2) of Asian descent, without diabetes, were randomly assigned 2:1 with a computer-generated sequence and block randomisation to once-weekly subcutaneous semaglutide 2·4 mg or placebo, with a reduced-calorie diet and increased physical activity.

Baseline effect+CI matches: `[]`.

### 184. semaglutide-obesity-weight / 40825340 — NO_CAPTURED_COMPLEMENT

> Coprimary endpoints, measured in all randomly assigned participants by intention to treat, were percentage bodyweight change and the proportion of participants reaching ≥5% bodyweight reduction.

Baseline effect+CI matches: `[]`.

### 185. semaglutide-obesity-weight / 40825340 — NO_CAPTURED_COMPLEMENT

> Confirmatory secondary endpoints were the proportion of participants with ≥10% and ≥15% bodyweight reductions and change in waist circumference.

Baseline effect+CI matches: `[]`.

### 186. semaglutide-obesity-weight / 40825340 — NO_CAPTURED_COMPLEMENT

> At week 44, mean change in bodyweight was -16·0% (SE 0·7) in the semaglutide 2·4 mg group versus -3·1% (0·9) in the placebo group (p<0·0001), and a greater proportion of participants reached bodyweight reductions of ≥5% (96 [96%] vs 12 [25%]; p<0·0001), ≥10% (78 [78%] vs 5 [10%]; p<0·0001), and ≥15% (53 [53·0%] vs 2 [4·2%]; p<0·0001) in the semaglutide 2·4 mg group.

Baseline effect+CI matches: `[]`.

### 187. semaglutide-obesity-weight / 40825340 — NO_CAPTURED_COMPLEMENT

> INTERPRETATION: In this Asian population with obesity (BMI ≥25·0 kg/m2), once-weekly semaglutide 2·4 mg significantly reduced bodyweight and was well tolerated.

Baseline effect+CI matches: `[]`.

### 188. semaglutide-obesity-weight / 33567185 — NO_CAPTURED_COMPLEMENT

> The coprimary end points were the percentage change in body weight and weight reduction of at least 5%.

Baseline effect+CI matches: `[]`.

### 189. semaglutide-obesity-weight / 33567185 — NO_CAPTURED_COMPLEMENT

> More participants in the semaglutide group than in the placebo group achieved weight reductions of 5% or more (1047 participants [86.4%] vs. 182 [31.5%]), 10% or more (838 [69.1%] vs. 69 [12.0%]), and 15% or more (612 [50.5%] vs. 28 [4.9%]) at week 68 (P<0.001 for all three comparisons of odds).

Baseline effect+CI matches: `[]`.

### 190. semaglutide-obesity-weight / 33567185 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In participants with overweight or obesity, 2.4 mg of semaglutide once weekly plus lifestyle intervention was associated with sustained, clinically relevant reduction in body weight.

Baseline effect+CI matches: `[]`.

### 191. sglt2-hfref-hosp-cvdeath / 31535829 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: In patients with type 2 diabetes, inhibitors of sodium-glucose cotransporter 2 (SGLT2) reduce the risk of a first hospitalization for heart failure, possibly through glucose-independent mechanisms.

Baseline effect+CI matches: `[]`.

### 192. sglt2-hfref-hosp-cvdeath / 31535829 — NO_CAPTURED_COMPLEMENT

> More data are needed regarding the effects of SGLT2 inhibitors in patients with established heart failure and a reduced ejection fraction, regardless of the presence or absence of type 2 diabetes.

Baseline effect+CI matches: `[]`.

### 193. sglt2-hfref-hosp-cvdeath / 31535829 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Among patients with heart failure and a reduced ejection fraction, the risk of worsening heart failure or death from cardiovascular causes was lower among those who received dapagliflozin than among those who received placebo, regardless of the presence or absence of diabetes.

Baseline effect+CI matches: `[]`.

### 194. sglt2-hfref-hosp-cvdeath / 32865377 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Sodium-glucose cotransporter 2 (SGLT2) inhibitors reduce the risk of hospitalization for heart failure in patients regardless of the presence or absence of diabetes.

Baseline effect+CI matches: `[]`.

### 195. sglt2-hfref-hosp-cvdeath / 32865377 — NO_CAPTURED_COMPLEMENT

> More evidence is needed regarding the effects of these drugs in patients across the broad spectrum of heart failure, including those with a markedly reduced ejection fraction.

Baseline effect+CI matches: `[]`.

### 196. sglt2-hfref-hosp-cvdeath / 32865377 — NO_CAPTURED_COMPLEMENT

> (Funded by Boehringer Ingelheim and Eli Lilly; EMPEROR-Reduced ClinicalTrials.gov number, NCT03057977.).

Baseline effect+CI matches: `[]`.

### 197. sglt2-primary-prevention-hf / 28605608 — NO_CAPTURED_COMPLEMENT

> Background Canagliflozin is a sodium-glucose cotransporter 2 inhibitor that reduces glycemia as well as blood pressure, body weight, and albuminuria in people with diabetes.

Baseline effect+CI matches: `[]`.

### 198. sglt2-primary-prevention-hf / 28605608 — NO_CAPTURED_COMPLEMENT

> Although on the basis of the prespecified hypothesis testing sequence the renal outcomes are not viewed as statistically significant, the results showed a possible benefit of canagliflozin with respect to the progression of albuminuria (hazard ratio, 0.73; 95% CI, 0.67 to 0.79) and the composite outcome of a sustained 40% reduction in the estimated glomerular filtration rate, the need for renal-replacement therapy, or death from renal causes (hazard ratio, 0.60; 95% CI, 0.47 to 0.77).

Baseline effect+CI matches: `[['HR', 0.73, 0.67, 0.79], ['HR', 0.6, 0.47, 0.77]]`.

### 199. sglt2-primary-prevention-hf / 26378978 — NO_CAPTURED_COMPLEMENT

> There were no significant between-group differences in the rates of myocardial infarction or stroke, but in the empagliflozin group there were significantly lower rates of death from cardiovascular causes (3.7%, vs. 5.9% in the placebo group; 38% relative risk reduction), hospitalization for heart failure (2.7% and 4.1%, respectively; 35% relative risk reduction), and death from any cause (5.7% and 8.3%, respectively; 32% relative risk reduction).

Baseline effect+CI matches: `[]`.

### 200. sglt2-primary-prevention-hf / 35061894 — NO_CAPTURED_COMPLEMENT

> Treatment with the sodium-glucose cotransporter 2 inhibitor (SGLT-2i) empagliflozin significantly reduces cardiovascular events in patients with type 2 diabetes (T2D); however, the mechanisms behind the reduction in cardiovascular (CV) events are unknown.

Baseline effect+CI matches: `[]`.

### 201. sglt2-primary-prevention-hf / 35061894 — NO_CAPTURED_COMPLEMENT

> Treatment with empagliflozin for 13 weeks in patients with T2D at high CV risk did not reduce left heart filling pressure more than placebo at submaximal exercise.

Baseline effect+CI matches: `[]`.

### 202. sglt2-primary-prevention-hf / 35061894 — NO_CAPTURED_COMPLEMENT

> At rest, we observed that empagliflozin reduced PCWP at a magnitude of clinical significance.

Baseline effect+CI matches: `[]`.

### 203. sglt2-primary-prevention-hf / 31434508 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Among people with type 2 diabetes mellitus and coronary artery disease, SGLT2 inhibition with empagliflozin was associated with significant reduction in LV mass indexed to body surface area after 6 months, which may account in part for the beneficial cardiovascular outcomes observed in the EMPA-REG OUTCOME (BI 10773 [Empagliflozin] Cardiovascular Outcome Event Trial in Type 2 Diabetes Mellitus Patients) trial.

Baseline effect+CI matches: `[]`.

### 204. spironolactone-hfref-mortality / 10471456 — NO_CAPTURED_COMPLEMENT

> This 30 percent reduction in the risk of death among patients in the spironolactone group was attributed to a lower risk of both death from progressive heart failure and sudden death from cardiac causes.

Baseline effect+CI matches: `[]`.

### 205. spironolactone-hfref-mortality / 10471456 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Blockade of aldosterone receptors by spironolactone, in addition to standard therapy, substantially reduces the risk of both morbidity and death among patients with severe heart failure.

Baseline effect+CI matches: `[]`.

### 206. spironolactone-hfref-mortality / 21073363 — NO_CAPTURED_COMPLEMENT

> Hospitalizations for heart failure and for any cause were also reduced with eplerenone.

Baseline effect+CI matches: `[]`.

### 207. spironolactone-hfref-mortality / 21073363 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: Eplerenone, as compared with placebo, reduced both the risk of death and the risk of hospitalization among patients with systolic heart failure and mild symptoms.

Baseline effect+CI matches: `[]`.

### 208. statins-primary-prevention-elderly / 20404379 — NO_CAPTURED_COMPLEMENT

> Although no significant heterogeneity was found in treatment effects by age, absolute reductions in event rates associated with rosuvastatin were greater in older persons.

Baseline effect+CI matches: `[]`.

### 209. statins-primary-prevention-elderly / 20404379 — NO_CAPTURED_COMPLEMENT

> CONCLUSION: In apparently healthy older persons without hyperlipidemia but with elevated high-sensitivity C-reactive protein levels, rosuvastatin reduces the incidence of major cardiovascular events.

Baseline effect+CI matches: `[]`.

### 210. statins-primary-prevention-elderly / 28531241 — NO_CAPTURED_COMPLEMENT

> IMPORTANCE: While statin therapy for primary cardiovascular prevention has been associated with reductions in cardiovascular morbidity, the effect on all-cause mortality has been variable.

Baseline effect+CI matches: `[]`.

### 211. ticagrelor-vs-clopidogrel-acs / 19717846 — NO_CAPTURED_COMPLEMENT

> The rate of death from any cause was also reduced with ticagrelor (4.5%, vs. 5.9% with clopidogrel; P<0.001).

Baseline effect+CI matches: `[]`.

### 212. ticagrelor-vs-clopidogrel-acs / 19717846 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In patients who have an acute coronary syndrome with or without ST-segment elevation, treatment with ticagrelor as compared with clopidogrel significantly reduced the rate of death from vascular causes, myocardial infarction, or stroke without an increase in the rate of overall major bleeding but with an increase in the rate of non-procedure-related bleeding.

Baseline effect+CI matches: `[]`.

### 213. tocilizumab-covid19-mortality / 33332779 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS: In hospitalized patients with Covid-19 pneumonia who were not receiving mechanical ventilation, tocilizumab reduced the likelihood of progression to the composite outcome of mechanical ventilation or death, but it did not improve survival.

Baseline effect+CI matches: `[]`.

### 214. tocilizumab-covid19-mortality / 33080017 — NO_CAPTURED_COMPLEMENT

> CONCLUSIONS AND RELEVANCE: In this randomized clinical trial of patients with COVID-19 and pneumonia requiring oxygen support but not admitted to the intensive care unit, TCZ did not reduce WHO-CPS scores lower than 5 at day 4 but might have reduced the risk of NIV, MV, or death by day 14.

Baseline effect+CI matches: `[]`.

### 215. tranexamic-acid-pph / 32143721 — NO_CAPTURED_COMPLEMENT

> BACKGROUND: Oral tranexamic acid (TXA), if effective in reducing blood loss after delivery for women experiencing primary PPH, could be administered where parenteral administration is not feasible.

Baseline effect+CI matches: `[]`.

### 216. tranexamic-acid-pph / 36243576 — NO_CAPTURED_COMPLEMENT

> Tranexamic Acid to Reduce Blood Loss in Hemorrhagic Cesarean Delivery (TRACES) was a double-blind, placebo-controlled, randomised, multicentre dose-ranging study to determine the dose-effect relationship for two regimens of intravenous tranexamic acid vs placebo.

Baseline effect+CI matches: `[]`.

### 217. tranexamic-acid-pph / 36243576 — NO_CAPTURED_COMPLEMENT

> Biomarkers of fibrinolytic activation were assayed at five time points, with inhibition of hyperfibrinolysis defined as reductions in the increase over baseline in D-dimer and plasmin-antiplasmin levels and in the plasmin peak time.

Baseline effect+CI matches: `[]`.

### 218. tranexamic-acid-pph / 36243576 — NO_CAPTURED_COMPLEMENT

> A dose of tranexamic acid 0.5 g was less potent, with non-significant reductions (D-dimers: 58% [32-84] [P=0.06 vs placebo]; plasmin-antiplasmin: 13% [18-43] [P=0.051]).

Baseline effect+CI matches: `[]`.

### 219. tranexamic-acid-pph / 36243576 — NO_CAPTURED_COMPLEMENT

> Although both tranexamic acid doses reduced the plasmin peak, reduction in plasmin peak time was significant only for the 1 g dose of tranexamic acid.

Baseline effect+CI matches: `[]`.

### 220. tranexamic-acid-pph / 28456509 — NO_CAPTURED_COMPLEMENT

> Early administration of tranexamic acid reduces deaths due to bleeding in trauma patients.

Baseline effect+CI matches: `[]`.

### 221. tranexamic-acid-pph / 28456509 — NO_CAPTURED_COMPLEMENT

> Death due to bleeding was significantly reduced in women given tranexamic acid (155 [1·5%] of 10 036 patients vs 191 [1·9%] of 9985 in the placebo group, risk ratio [RR] 0·81, 95% CI 0·65-1·00; p=0·045), especially in women given treatment within 3 h of giving birth (89 [1·2%] in the tranexamic acid group vs 127 [1·7%] in the placebo group, RR 0·69, 95% CI 0·52-0·91; p=0·008).

Baseline effect+CI matches: `[['RR', 0.81, 0.65, 1.0], ['RR', 0.69, 0.52, 0.91]]`.

### 222. tranexamic-acid-pph / 28456509 — NO_CAPTURED_COMPLEMENT

> Hysterectomy was not reduced with tranexamic acid (358 [3·6%] patients in the tranexamic acid group vs 351 [3·5%] in the placebo group, RR 1·02, 95% CI 0·88-1·07; p=0·84).

Baseline effect+CI matches: `[['RR', 1.02, 0.88, 1.07]]`.

### 223. tranexamic-acid-pph / 28456509 — NO_CAPTURED_COMPLEMENT

> The composite primary endpoint of death from all causes or hysterectomy was not reduced with tranexamic acid (534 [5·3%] deaths or hysterectomies in the tranexamic acid group vs 546 [5·5%] in the placebo group, RR 0·97, 95% CI 0·87-1·09; p=0·65).

Baseline effect+CI matches: `[['RR', 0.97, 0.87, 1.09]]`.

### 224. tranexamic-acid-pph / 28456509 — NO_CAPTURED_COMPLEMENT

> INTERPRETATION: Tranexamic acid reduces death due to bleeding in women with post-partum haemorrhage with no adverse effects.

Baseline effect+CI matches: `[]`.

## Missing included abstracts

- colchicine-postop-af / NCT07611019
- colchicine-postop-af / NCT07287345
- colchicine-secondary-cv-prevention / CLEAR SYNERGY · 39555823
- colchicine-secondary-cv-prevention / NCT05739929
- colchicine-secondary-cv-prevention / NCT06215989
- colchicine-secondary-cv-prevention / PROACT 2 · NCT05850091
- colchicine-secondary-cv-prevention / COLCOHIV · NCT07704164
- colchicine-secondary-cv-prevention / NCT01709981
- colchicine-secondary-cv-prevention / COOL · NCT00754819
- colchicine-secondary-cv-prevention / CODEN · NCT02095522
- colchicine-secondary-cv-prevention / NCT07143136
- corticosteroids-covid19-mortality / COVIDICUS · NCT04344730
- dapagliflozin-hfpef-hosp / STADIA-HFpEF · NCT04475042
- dapagliflozin-hfpef-hosp / NCT03877224
- empagliflozin-hfpef-hosp / EMPA-PRED · NCT06249945
- empagliflozin-hfpef-hosp / NCT03448406
- esketamine-trd-madrs / TRANSFORM-3 · NCT02422186
- esketamine-trd-madrs / TRANSFORM-1 · NCT02417064
- finerenone-ckd-t2d-renal / NCT07775846
- finerenone-ckd-t2d-renal / FineCaRe · NCT07026539
- glp1-ra-mace-t2d / SOUL · 40162642
- noac-vs-warfarin-af-stroke / NCT00504556
- noac-vs-warfarin-af-stroke / NCT00806624
- noac-vs-warfarin-af-stroke / NCT00829933
- omega3-cardiovascular-events / NCT06720662
- omega3-cardiovascular-events / OMEMI · NCT01841944
- omega3-cardiovascular-events / FFAME · NCT01048502
- probiotics-aad-prevention / PROBIO · NCT06990568
- probiotics-aad-prevention / NCT04529980
- probiotics-aad-prevention / NCT02993419
- probiotics-aad-prevention / NCT02722993
- probiotics-aad-prevention / NCT03516409
- probiotics-aad-prevention / YOBIOTIC · NCT03755765
- probiotics-aad-prevention / Probiotics · NCT02589964
- probiotics-aad-prevention / NCT07234448
- probiotics-aad-prevention / PANDA · NCT05845073
- sacubitril-valsartan-hfref / EVALUATE-HF · NCT02874794
- sacubitril-valsartan-hfref / OUTSTEP-HF · NCT02900378
- sacubitril-valsartan-hfref / ANSWER-HF · NCT04853758
- sacubitril-valsartan-hfref / PRESENT-HF · NCT05487261
- sacubitril-valsartan-hfref / PARALLEL-HF · NCT02468232
- sacubitril-valsartan-hfref / PIONEER-HF · NCT02554890
- semaglutide-obesity-weight / STEP 10 · NCT05040971
- semaglutide-obesity-weight / NCT07731256
- semaglutide-obesity-weight / NCT06390501
- sglt2-ckd-progression / NCT05735197
- sglt2-ckd-progression / NCT07344922
- sglt2-ckd-progression / EMPA-CKD · NCT07060417
- sglt2-ckd-progression / ZODIAC · NCT05570305
- sglt2-ckd-progression / NCT05614115
- sglt2-ckd-progression / DIAMOND · NCT03190694
- sglt2-hfref-hosp-cvdeath / NCT04304560
- sglt2-hfref-hosp-cvdeath / NCT06229678
- sglt2-hfref-hosp-cvdeath / NCT04385589
- spironolactone-hfref-mortality / J-EMPHASIS-HF · 28824029
- ticagrelor-vs-clopidogrel-acs / PHILO · 26376600
- tocilizumab-covid19-mortality / ARCHITECTS · NCT04412772
- tocilizumab-covid19-mortality / CORON-ACT · NCT04335071
- tranexamic-acid-pph / TA TEG · NCT02026297

Reproduce: `python evidence/effect_identity/measure_relative_reduction.py`.
