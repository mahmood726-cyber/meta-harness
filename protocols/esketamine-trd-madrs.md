# Esketamine nasal spray vs placebo for depressive symptoms in treatment-resistant depression

## PICO
- **Population:** adults with treatment-resistant depression (major depressive disorder, inadequate response to ≥2 antidepressants).
- **Intervention:** intranasal esketamine, added to a newly-initiated oral antidepressant.
- **Comparator:** intranasal placebo, added to a newly-initiated oral antidepressant.
- **Primary outcome:** change from baseline in the Montgomery–Åsberg Depression Rating Scale (MADRS) total score at ~4 weeks (mean difference in points; a lower/more-negative MADRS change = greater improvement, so a negative mean difference favours esketamine).

## Eligibility - P/I/C/design only
Include randomized controlled trials when all of the following are true:
- The population is adults with treatment-resistant depression, judged from the title or registry conditions.
- The randomized intervention is intranasal esketamine plus an oral antidepressant.
- The randomized comparator is intranasal placebo plus an oral antidepressant.
- The trial is double-blind or placebo-controlled.

Exclude records for wrong population (bipolar depression, acute suicidality/psychiatric-emergency indication where the design/estimand differs, non-TRD major depression), wrong intervention (racemic ketamine, intravenous ketamine, esketamine for anaesthesia/analgesia/sedation), wrong comparator, non-randomized design, reviews, protocol-only reports, relapse-prevention/maintenance-withdrawal designs (a different estimand), and open-label safety studies.

Eligibility is not based on whether the abstract reports the target outcome. If an otherwise eligible trial does not report the MADRS change from baseline as a per-arm mean and standard deviation (in the abstract or in eligible structured registry results), it is declared absent rather than substituted with another endpoint or timepoint or an imputed variance.

## Outcomes
Primary outcome:
- Change from baseline in MADRS total score at approximately 4 weeks (Day 28 of the double-blind induction phase), including phrasings such as MADRS, Montgomery-Asberg / Montgomery-Åsberg Depression Rating Scale, change from baseline in MADRS, and the double-blind induction endpoint.

The estimand is the mean difference (MADRS points) in the change from baseline, esketamine versus placebo, at the induction endpoint. Pooling is random-effects inverse-variance on the mean difference; a single included trial is presented as that trial's own effect, not a random-effects pool.

## Sources and verification
- Per-arm change-from-baseline mean and standard deviation are taken verbatim from the trial's primary report or its structured ClinicalTrials.gov posted results (paramType MEAN with a Standard-Deviation dispersion), never a least-squares mean with a standard error, and never imputed from a figure. The full-analysis-set (FAS/mITT) induction-endpoint values are used; a trial reporting only a least-squares-mean difference with a standard error, or only a mixed-model estimate, is declared absent rather than pooled (the reported model estimate is noted where it differs).
- The estimand is the CHANGE from baseline (not the final value); a final-value mean is not mixed with a change-from-baseline mean. All timepoints are aligned to the induction endpoint (~Day 28).
- Every pooled number is verified against the committed source span before it is pooled.

## Comparator
- Published open-access meta-analysis of intranasal esketamine for treatment-resistant depression reporting the MADRS change, for trial-set overlap and reporting comparison only. An identical estimate on an identical trial set is arithmetic, not corroboration; the overlap is stated on the page.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that the
structured exclusion of phase 2 / phase II trials was declared in the protocol but
not executable in the topic config. The config now excludes phase 2/II contexts at
screening while leaving the phase 3 treatment-resistant-depression esketamine
trials eligible. This amendment changes screening only.
