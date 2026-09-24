# Signature queue: served numbers the evidence lane proposes to change (NONE LANDED)

3 of 76 adjudicated rows reject the served candidate. Each block is DERIVED and UNSIGNED. A served number moves only after Mahmood signs the block's sha256 and a rebuild runs.

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
- block sha256: 7e58827c63f90ed1ff3b719b9c9a0374b727b1d614d10cacae45fcccbf39941d

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
- block sha256: 1f03ad71c3e1a6a2e95eb5616a506a9edce317261f36e30763e72d59b644179b

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
- block sha256: 208bb628c87421f243e06ecaa74d38d89c6723731e8a8c5872c9c1aeb042c4c3
