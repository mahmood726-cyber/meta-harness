# Protocol - systemic corticosteroids for 28-day mortality in hospitalised COVID-19

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs.

## PICO
- **P** - adults hospitalised with COVID-19.
- **I** - systemic corticosteroids, including dexamethasone, hydrocortisone,
  methylprednisolone, prednisone, or prednisolone.
- **C** - usual care, standard care, standard treatment, no hydrocortisone, or placebo.
- **O (primary)** - 28-day all-cause mortality.
- **O (harms)** - serious adverse events.

## Estimand / population / timepoint
- **Estimand** - odds ratio (OR), systemic corticosteroid vs usual care/placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - 28 days.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - hospitalised, severe, ICU, hypoxic, or pneumonia/ARDS COVID-19 population by
  title or registry conditions;
- **I3** - systemic corticosteroid vs usual care, standard care, no hydrocortisone, or
  placebo;
- **design** - randomised comparison; double-blinding is not required because the
  target comparator includes open-label usual-care trials as well as placebo trials.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, meta-analysis, guideline, observational study, or
  protocol-only);
- **X2** - wrong population (for example post-COVID sequelae, non-COVID community-
  acquired pneumonia, influenza, paediatric MIS-C, pericarditis, or atrial fibrillation);
- **X3** - wrong intervention/comparison (no systemic corticosteroid-vs-control
  contrast, or a steroid-dose/active-steroid comparison without usual-care/placebo
  control);
- **X5** - off-topic: a primary trial of another topic/disease in this set
  (negative control).

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> 28-day all-cause mortality in an abstract-extractable form is recorded as
> target-result status at extraction, never as an exclusion. A published effect
> plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/corticosteroids-covid19-mortality/records.json; screening replays offline)
- PubMed: targeted trial-report queries for dexamethasone, hydrocortisone, and
  methylprednisolone COVID-19 randomised trials.
- ClinicalTrials.gov: condition "COVID-19", intervention "dexamethasone".
- Comparator-reference seeding is enabled so the WHO REACT trial references are
  replayed through the same P/I/C/design screen.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on the configured log ratio scale; for the primary
outcome this is log(OR). Paule-Mandel tau^2; HKSJ 95% CI on `t_{k-1}` with variance
floor `max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`.
0.5 continuity correction to all four cells of a study only if it has a zero cell.
DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
WHO REACT Working Group, *JAMA* 2020, "Association Between Administration of
Systemic Corticosteroids and Mortality Among Critically Ill Patients With COVID-19:
A Meta-analysis" (PMID 32876694, DOI 10.1001/jama.2020.17023; Unpaywall
is_oa=true; PubMed Central PMCID PMC7489434). Its abstract reports 7 randomised
clinical trials and 28-day all-cause mortality summary OR 0.66 (95% CI 0.53-0.82)
by fixed-effect meta-analysis, with a random-effects OR 0.70 (95% CI 0.48-1.01).

## Controls
- **Positive** - the search must recover and include RECOVERY dexamethasone
  (PMID 32678530), REMAP-CAP hydrocortisone (PMID 32876697), and METCOVID
  methylprednisolone (PMID 32785710).
- **Negative** - Torres/JAMA methylprednisolone for severe community-acquired
  pneumonia (PMID 25688779) must be recovered and excluded as the wrong population.
