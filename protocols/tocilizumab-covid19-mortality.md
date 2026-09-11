# Protocol - tocilizumab for 28-day mortality in hospitalised COVID-19

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs.

## PICO
- **P** - adults hospitalised with COVID-19.
- **I** - tocilizumab, an interleukin-6 receptor antagonist, added to usual or
  standard care.
- **C** - usual care, standard care, supportive care, or placebo added to standard care.
- **O (primary)** - 28-day all-cause mortality.
- **O (harms)** - serious adverse events and secondary infections by 28 days.

## Estimand / population / timepoint
- **Estimand** - odds ratio (OR), tocilizumab vs usual care/placebo. Published
  abstract effect estimates with 95% CIs are poolable as reported when
  abstract-extractable 2x2 counts are absent.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - 28 days.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - hospitalised COVID-19 population by title or registry conditions;
- **I3** - tocilizumab vs usual care, standard care, supportive care, or placebo;
- **design** - randomised comparison; double-blinding is not required because the
  target comparator includes open-label usual-care trials as well as placebo trials.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, meta-analysis, guideline, observational study,
  protocol-only, or secondary/post-hoc analysis);
- **X2** - wrong population (for example post-COVID sequelae, paediatric MIS-C,
  giant-cell arteritis, rheumatoid arthritis, polymyalgia rheumatica, cytokine-release
  syndrome outside COVID-19, cancer, or transplant);
- **X3** - wrong intervention/comparison (no tocilizumab-vs-control contrast, or an
  active-drug comparison without usual-care/placebo control);
- **X5** - off-topic: a primary trial of another topic/disease in this set
  (negative control).

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> 28-day all-cause mortality in an abstract-extractable form is recorded as
> target-result status at extraction, never as an exclusion. A published effect
> plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/tocilizumab-covid19-mortality/records.json; screening replays offline)
- PubMed: title-token queries for original tocilizumab COVID-19 randomised trial
  reports, with PubMed-side filters to avoid reviews, meta-analyses, letters,
  observational cohorts, post-hoc biomarker reports, and active-drug comparisons.
- ClinicalTrials.gov: condition "COVID-19", intervention "tocilizumab".
- Comparator-reference seeding is enabled so the WHO REACT trial references, where
  PubMed exposes them, are replayed through the same P/I/C/design screen.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on the configured log ratio scale; for the primary
outcome this is log(OR). Paule-Mandel tau^2; HKSJ 95% CI on `t_{k-1}` with variance
floor `max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`.
0.5 continuity correction to all four cells of a study only if it has a zero cell.
DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
WHO Rapid Evidence Appraisal for COVID-19 Therapies (REACT) Working Group, *JAMA*
2021, "Association Between Administration of IL-6 Antagonists and Mortality Among
Patients Hospitalized for COVID-19: A Meta-analysis" (PMID 34228774, DOI
10.1001/jama.2021.11330; Unpaywall is_oa=true; PubMed Central PMCID PMC8261689).
Its abstract reports 27 randomised trials and 28-day all-cause mortality summary OR
0.86 (95% CI 0.79-0.95) for all IL-6 antagonists versus usual care or placebo; the
tocilizumab subgroup summary OR is 0.83 (95% CI 0.74-0.92).

## Controls
- **Positive** - the search must recover and include RECOVERY tocilizumab
  (PMID 33933206), EMPACTA (PMID 33332779), and COVACTA (PMID 33631066).
- **Negative** - GiACTA tocilizumab for giant-cell arteritis (PMID 28745999) must
  be recovered and excluded as the wrong population.
