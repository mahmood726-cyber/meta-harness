# Semaglutide 2.4 mg vs placebo for percent body-weight change in overweight/obesity without diabetes

## PICO
- **Population:** adults with overweight or obesity (BMI thresholds per trial) WITHOUT type 2 diabetes.
- **Intervention:** once-weekly subcutaneous semaglutide 2.4 mg plus lifestyle intervention.
- **Comparator:** placebo plus lifestyle intervention.
- **Primary outcome:** percent change in body weight from baseline to Week 68 (mean difference in percentage points; a more-negative value = greater weight loss, so a negative mean difference favours semaglutide).

## Eligibility - P/I/C/design only
Include randomized controlled trials when all of the following are true:
- The population is adults with overweight or obesity without type 2 diabetes, judged from the title or registry conditions.
- The randomized intervention is once-weekly semaglutide 2.4 mg for weight management.
- The randomized comparator is placebo (both arms with the same lifestyle intervention).
- The trial is double-blind or placebo-controlled.

Exclude records for wrong population (type 2 diabetes, adolescents/children), wrong intervention (a different GLP-1 agonist, a different semaglutide dose or an oral formulation as the randomized arm, tirzepatide), wrong comparator, non-randomized design, reviews, protocol-only reports, **weight-loss-MAINTENANCE / continued-treatment-vs-withdrawal designs** (a different estimand: change measured from a post-run-in randomization, not from the untreated baseline — e.g. STEP-4), and fixed-dose multi-arm trials without a pre-specified dose comparison.

Eligibility is not based on whether the abstract reports the target outcome. If an otherwise eligible trial does not report the Week-68 percent body-weight change as a per-arm mean and standard deviation (in the abstract or in eligible structured registry results), it is declared absent rather than substituted with another endpoint or timepoint or an imputed variance.

## Outcomes
Primary outcome:
- Percent change in body weight from baseline to Week 68, including phrasings such as change in body weight (%), percent/percentage change in body weight, and the Week-68 body-weight-change endpoint.

The estimand is the mean difference (percentage points) in the Week-68 percent body-weight change, semaglutide 2.4 mg versus placebo. Pooling is random-effects inverse-variance on the mean difference; a single included trial is presented as that trial's own effect.

## Sources and verification
- Per-arm change-from-baseline mean and standard deviation are taken verbatim from the trial's structured ClinicalTrials.gov posted results (paramType MEAN with a Standard-Deviation dispersion), never a least-squares mean with a standard error, and never imputed. **A single estimand is used consistently across trials** (the ClinicalTrials.gov *in-trial / treatment-policy* observation-period row, all-randomized denominator, from baseline to Week 68); the on-treatment row is a sensitivity analysis, not mixed into the primary pool. The estimand actually pooled is stated on the page, and it may differ slightly from a trial publication's headline treatment-policy number, which is noted where it differs.
- The change is measured from the UNTREATED baseline (Week 0), never from a post-run-in randomization; a maintenance/withdrawal design is excluded rather than mixed.
- Every pooled number is verified against the committed source span before it is pooled.

## Comparator
- Published open-access meta-analysis of semaglutide 2.4 mg for weight reduction in non-diabetic overweight/obesity, for trial-set overlap and reporting comparison only. An identical estimate on an identical trial set is arithmetic, not corroboration; the overlap is stated on the page.

## Amendment 2026-09-28 (semaglutide-weight review e209c1d5; primary analysis, estimand label, comparison-level screening)
**Status: RETROSPECTIVE, decided by Dispatch under Mahmood's delegation, after the trials reported.** It does not
rewrite the text above; it records where that text was wrong and what replaces it.

- **Correction to the paragraph above.** The ClinicalTrials.gov "in-trial observation period" row is **observed data**:
  its n is the participants with a measurement at Week 68 (STEP 1 1,212/577; STEP 3 373/189), not the all-randomized
  full analysis set (1,306/655; 407/204), and a raw observed summary is **not** a treatment-policy estimate. A full-analysis-
  set heading does not establish observed contribution; a registry summary that states imputation is held unless its method
  and variance are established.
- **Primary analysis.** Each trial's published model-based **treatment-policy** difference, by generic inverse variance
  with the SE from its reported standard two-sided 95% CI (never used as an arm SD): STEP 1 -12.44 (-13.37 to -11.51),
  STEP 3 -10.27 (-11.97 to -8.57), both ANCOVA as posted in the registry results. A trial without a reported difference for
  this estimand is named, never replaced by its raw row. The missing-data method behind each treatment-policy estimate is
  not held in the source text; the reported interval carries the trial's own variance.
- **Sensitivity analysis.** Raw observed per-arm mean/SD with the n that contributed the observations, labelled as observed
  data.
- **Estimand label.** Derived per input from the analysis actually used, never from the declared population string.
- **Comparison-level screening; pooled vs matched placebo.** A term naming a randomised arm (STEP 8's liraglutide) is not a
  population exclusion. The eligible contrast is semaglutide vs its MATCHED placebo; a pooled placebo that includes the
  placebo matched to once-daily liraglutide is at most a labelled supportive figure. One trial never contributes both, and
  no placebo arm is counted twice. STEP 8's held registry reports weight only against the pooled placebo, so STEP 8 is
  named (POOLED_PLACEBO_NOT_THE_ELIGIBLE_CONTRAST) with the pooled figure shown as supportive; it is not pooled.
- **Declared unit.** The primary outcome declares unit_class PERCENT; a measure in kilograms is not this outcome.
