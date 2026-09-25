# Signature queue: served numbers the evidence lane proposes to change (NONE LANDED)

4 of 92 adjudicated rows reject the served candidate. Each block is DERIVED and UNSIGNED. A served number moves only after Mahmood signs the block's sha256 and a rebuild runs.

### P53-23: noac-vs-warfarin-af-stroke / Stroke or systemic embolism / PMID 19717844 (RE-LY, dabigatran 150 mg)
- state: QUEUED_FOR_MAHMOOD_SIGNATURE_NOT_LANDED
- served now: RR 0.66 (0.53-0.82) -- abstract relative risk on an HR-declared outcome
- proposed (derived, unsigned): HR 0.65 (0.52-0.81) -- registry Cox analysis, randomised set
- pooled effect: NOT COMPUTED here: moves only on a rebuild after signature
- mechanism: a relative risk was served on an outcome that declares HR while the same source family prints the HR
- coordination: found by this lane's second, cross-family adjudication; not seen in the main lane's AUDIT_QUEUE (searched 2026-09-24)
- reason: RE-LY, dabigatran 150 mg vs warfarin, stroke or systemic embolism. The outcome declares HR (estimand and served estimand both HR). The served row is the abstract's RELATIVE RISK 0.66 (0.53-0.82). The registry, for the same primary endpoint and contrast in the randomised set, prints a Cox proportional hazard 0.65 (0.52-0.81). The declared hierarchy prefers a published effect on the declared scale, so the RR candidate is rejected for this outcome and the trial is kept. Raised by the second, cross-family adjudication and tested here against the registry line. The difference is small (0.66 -> 0.65), but it IS a served-number change, so it is queued, not landed.
- evidence (verbatim, re-verified against held bytes when the adjudication was written):
  - population: `cache/noac-vs-warfarin-af-stroke/records.json#/records/1` (sha256 6e35e6e53790): "we randomly assigned 18,113 patients who had atrial fibrillation and a risk of stroke"
  - endpoint: `evidence/held/registry/NCT00262600.json` (sha256 9fa0278eeed5): "RESULT OUTCOME 0 [PRIMARY]: Yearly Event Rate for Composite Endpoint of Stroke/SEE"
  - declared_scale_estimate: `evidence/held/registry/NCT00262600.json` (sha256 9fa0278eeed5): "RESULT OUTCOME 0 ANALYSIS 1: groups Dabigatran 150 mg, Warfarin | Cox Proportional Hazard 0.65 (95% CI 0.52 to 0.81)"
  - served_candidate_rr: `cache/noac-vs-warfarin-af-stroke/records.json#/records/1` (sha256 6e35e6e53790): "1.11% per year in the group that received 150 mg of dabigatran (relative risk, 0.66; 95% CI, 0.53 to 0.82; P<0.001 for superiority)"
  - analysis_set: `evidence/held/registry/NCT00262600.json` (sha256 9fa0278eeed5): "POPULATION: Randomized set - The randomized set includes all randomized subjects in the treatment groups to which they were randomized, regardless of whether the subjects took randomized study medication or not."
- block sha256: 847d0411304a75b0c2c13cee90f0767130c7c1cacbc38db2a89942c51a10bef0

### UA-032: semaglutide-obesity-weight / Percent change in body weight / PMID 33625476 (STEP 3)
- state: QUEUED_FOR_MAHMOOD_SIGNATURE_NOT_LANDED
- served now: MD from -16.5 (SD 10.1, n=407) vs -5.8 (SD 7.7, n=204), labelled treatment-policy
- proposed (derived, unsigned): A: MD -10.27 (-11.97 to -8.57) treatment-policy; or B: same means with n=373/189 relabelled observed-case
- pooled effect: NOT COMPUTED here: moves only on a rebuild after signature; the choice A/B is Mahmood's
- mechanism: the outcome-level FAS denominator was attached to class-level observed means; the renderer the harness used did not surface class denominators
- coordination: PREVIOUSLY FOUND, NOT APPLIED: the same defect (and the same analysed n) is item 3 of the LANE-S8 brief (outputs/handover/lanes/LANE-S8.md, on main since 04902ecf, 2026-09-16), with the rule 'the n paired with an SD is the n of the participants that SD describes'. The served page on main (38c04411 and 4c595b4a) still carries the randomised n. A recorded finding that was not consumed; this block adds the held registry spans that bind the analysed n.
- reason: The served row pools CT.gov observed in-trial arm means (-16.5 vs -5.8) with n = 407/204, the full-analysis-set totals. The registry states that the number analysed is those with available data, and the class-level denominators for the in-trial period are 373/189. So the served SE is computed on n inflated by 44 participants, and observed-case means are labelled as the treatment-policy (all-randomised) estimand the outcome declares. The source's treatment-policy estimate for this endpoint is the ANCOVA difference -10.27 (95% CI -11.97 to -8.57), which matches the abstract's -10.3 (-12.0 to -8.6). Candidate rejected; trial kept.
- evidence (verbatim, re-verified against held bytes when the adjudication was written):
  - population: `cache/semaglutide-obesity-weight/records.json#/records/117` (sha256 8779e517b6f0): "Participants were randomized (2:1) to semaglutide, 2.4 mg (n = 407) or placebo (n = 204), both combined with a low-calorie diet for the first 8 weeks and intensive behavioral therapy (ie, 30 counseling visits) during 68 weeks."
  - number_analysed_is_available_data: `evidence/held/registry/NCT03611582.json` (sha256 bdaf55236501): "Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data."
  - class_denominators: `evidence/held/registry/NCT03611582.json` (sha256 bdaf55236501): "RESULT OUTCOME 0 CLASS DENOM In-trial observation period Participants: Semaglutide 2.4 mg=373; Placebo=189"
  - observed_means: `evidence/held/registry/NCT03611582.json` (sha256 bdaf55236501): "RESULT OUTCOME 0 MEASUREMENT In-trial observation period: Semaglutide 2.4 mg=-16.5 (spread 10.1); Placebo=-5.8 (spread 7.7)"
  - treatment_policy_estimate: `evidence/held/registry/NCT03611582.json` (sha256 bdaf55236501): "RESULT OUTCOME 0 ANALYSIS 0: groups Semaglutide 2.4 mg, Placebo | Treatment difference -10.27 (95% CI -11.97 to -8.57) | p <.0001 | METHOD ANCOVA"
  - abstract_estimate: `cache/semaglutide-obesity-weight/records.json#/records/117` (sha256 8779e517b6f0): "At week 68, the estimated mean body weight change from baseline was -16.0% for semaglutide vs -5.7% for placebo (difference, -10.3 percentage points [95% CI, -12.0 to -8.6]; P < .001)."
  - gap_analysis_set: `evidence/held/registry/NCT03611582.json` (sha256 bdaf55236501): "Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data."
  - gap_follow_up: `evidence/held_local/33625476/PMC7905697.html` (sha256 3b7ef04fa8a8): "The co–primary end points, in the order planned for sequential hierarchic testing, were the percentage change in body weight and the proportion of participants who lost at least 5% of baseline weight by week 68"
  - gap_entry_age: `evidence/held_local/33625476/PMC7905697.html` (sha256 3b7ef04fa8a8): "Eligible participants were aged 18 years or older"
- block sha256: eaff6799d1a0e67a5445a608fb9f27acfde3de45a419bcdda962a667fad6b2f6

### UA-033: semaglutide-obesity-weight / Percent change in body weight / PMID 33567185 (STEP 1)
- state: QUEUED_FOR_MAHMOOD_SIGNATURE_NOT_LANDED
- served now: MD from -15.6 (SD 10.1, n=1306) vs -2.8 (SD 6.5, n=655), labelled treatment-policy
- proposed (derived, unsigned): A: MD -12.44 (-13.37 to -11.51) treatment-policy; or B: same means with n=1212/577 relabelled observed-case
- pooled effect: NOT COMPUTED here: moves only on a rebuild after signature; the choice A/B is Mahmood's
- mechanism: as UA-032
- coordination: PREVIOUSLY FOUND, NOT APPLIED: the same defect (and the same analysed n) is item 3 of the LANE-S8 brief (outputs/handover/lanes/LANE-S8.md, on main since 04902ecf, 2026-09-16), with the rule 'the n paired with an SD is the n of the participants that SD describes'. The served page on main (38c04411 and 4c595b4a) still carries the randomised n. A recorded finding that was not consumed; this block adds the held registry spans that bind the analysed n.
- reason: Same defect as STEP 3 (UA-032). The served row pools observed in-trial means (-15.6 vs -2.8) with n = 1306/655 (FAS), while the registry's class-level denominators for those means are 1212/577 (participants with available data). The declared estimand is treatment-policy; the source's treatment-policy estimate is ANCOVA -12.44 (95% CI -13.37 to -11.51), matching the abstract's -12.4 (-13.4 to -11.5). Candidate rejected; trial kept.
- evidence (verbatim, re-verified against held bytes when the adjudication was written):
  - population: `cache/semaglutide-obesity-weight/records.json#/records/118` (sha256 8779e517b6f0): "we enrolled 1961 adults with a body-mass index (the weight in kilograms divided by the square of the height in meters) of 30 or greater (≥27 in persons with ≥1 weight-related coexisting condition), who did not have diabetes"
  - number_analysed_is_available_data: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data."
  - class_denominators: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "RESULT OUTCOME 0 CLASS DENOM In-trial observation period Participants: Semaglutide 2.4 mg=1212; Placebo=577"
  - observed_means: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "RESULT OUTCOME 0 MEASUREMENT In-trial observation period: Semaglutide 2.4 mg=-15.6 (spread 10.1); Placebo=-2.8 (spread 6.5)"
  - treatment_policy_estimate: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "RESULT OUTCOME 0 ANALYSIS 0: groups Semaglutide 2.4 mg, Placebo | Treatment difference -12.44 (95% CI -13.37 to -11.51) | p <.0001 | METHOD ANCOVA"
  - abstract_estimate: `cache/semaglutide-obesity-weight/records.json#/records/118` (sha256 8779e517b6f0): "for an estimated treatment difference of -12.4 percentage points (95% confidence interval [CI], -13.4 to -11.5; P<0.001)"
  - estimand_definition: `cache/semaglutide-obesity-weight/records.json#/records/118` (sha256 8779e517b6f0): "The primary estimand (a precise description of the treatment effect reflecting the objective of the clinical trial) assessed effects regardless of treatment discontinuation or rescue interventions."
  - gap_analysis_set: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data."
  - gap_follow_up: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "Change in body weight from baseline (week 0) to week 68 is presented."
  - gap_entry_age: `evidence/held/registry/NCT03548935.json` (sha256 eea955ece75b): "Male or female, age greater than or equal to 18 years at the time of signing informed consent"
- block sha256: 7279ac0fe2be1eda90aee59767af009b4674e9e36f2a2dbc09950a2cdc6809d1

### UA-042: spironolactone-hfref-mortality / All-cause mortality / PMID 28824029 (J-EMPHASIS-HF)
- state: QUEUED_FOR_MAHMOOD_SIGNATURE_NOT_LANDED
- served now: HR 0.85 (0.53-1.36) -- the primary composite, mis-attributed
- proposed (derived, unsigned): HR 1.77 (0.81-3.87) -- registry all-cause mortality analysis
- pooled effect: NOT COMPUTED here: the pooled estimate moves only on a rebuild after signature
- mechanism: a candidate extraction took the first HR in the abstract, which belongs to a different endpoint
- coordination: SAME DECISION AS the main lane's D01 (enforcement-gate: AUDIT_QUEUE.md item 7; docs/evidence/enforcement-gate-2026-09-21/16-lane-WALK-signing-surface.md, shown NOT SIGNABLE until Mahmood rules and the change is made). Reached independently from held bytes, with the same target number, HR 1.77 (0.81-3.87). Do NOT sign twice: this block is corroborating evidence for D01, not a second notice.
- reason: The served 'All-cause mortality' row carries HR 0.85 (0.53-1.36). The abstract gives that HR for the PRIMARY COMPOSITE (cardiovascular death or HF hospitalisation), not for all-cause death. The registry record of the same trial (NCT01115855) reports a separate all-cause mortality analysis: HR 1.77 (95% CI 0.81 to 3.87), and the abstract gives 17 of 111 vs 10 of 110 deaths. The candidate is rejected; the trial is not.
- evidence (verbatim, re-verified against held bytes when the adjudication was written):
  - served_candidate_is_composite: `cache/spironolactone-hfref-mortality/records.json#/records/220` (sha256 e901036c243c): "The primary endpoint was a composite of death from cardiovascular causes or hospitalization for HF. The primary endpoint occurred in 29.7% of patients in the eplerenone group vs. 32.7% in the placebo group [hazard ratio=0.85 (95% CI: 0.53-1.36)]."
  - population: `cache/spironolactone-hfref-mortality/records.json#/records/220` (sha256 e901036c243c): "HFrEF patients with NYHA functional class II-IV and an EF ≤35% received eplerenone (n=111) or placebo (n=110) on top of standard therapy for at least 12 months."
  - endpoint: `evidence/held/registry/NCT01115855.json` (sha256 adeecf86d9f3): "RESULT OUTCOME 2 [SECONDARY]: Number of Participants With With First Occurrence of All-Cause Mortality"
  - estimate_ci: `evidence/held/registry/NCT01115855.json` (sha256 adeecf86d9f3): "RESULT OUTCOME 2 ANALYSIS 0: groups Eplerenone, Placebo | Hazard Ratio (HR) 1.77 (95% CI 0.81 to 3.87)"
  - analysis_set: `evidence/held/registry/NCT01115855.json` (sha256 adeecf86d9f3): "RESULT OUTCOME 2 DENOM Participants: Eplerenone=111; Placebo=110"
  - counts: `cache/spironolactone-hfref-mortality/records.json#/records/220` (sha256 e901036c243c): "A total of 17 patients (15.3%) in the eplerenone group and 10 patients (9.1%) in the placebo group died."
  - gap_analysis_set: `evidence/held/registry/NCT01115855.json` (sha256 adeecf86d9f3): "Full analysis set included all randomized participants."
  - gap_follow_up: `evidence/held/registry/NCT01115855.json` (sha256 adeecf86d9f3): "Randomization up to the date when the last enrolled participant had been followed up for 1 year (up to 1744 days)"
  - gap_entry_age: `evidence/held/registry/NCT01115855.json` (sha256 adeecf86d9f3): "ELIGIBILITY AGE/SEX: minimum age 55 Years | maximum age None | sex ALL"
- block sha256: 281d19c7f5fbc2f13397ca8b4bb3284433f40022c27ce4e62ac4d42bdd82d11d
