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

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 42536519) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 1 other open meta-analysis (PMID 40732345; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 2 of 2 of the comparator's eligible trials; with this route and the full retrieval below, 2 of 2 (2 of 2 without the comparator's own reference list, which contains its trials by construction). The route retrieves 73 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "obesity", "intr": "semaglutide"} is unchanged. It returns 355 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query: not adopted** (KEEP_CURRENT: no recall gain; recorded call mc-1c55956243fa0debf701303edc2c6a66.json).
