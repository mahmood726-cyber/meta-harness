# Protocol - systemic corticosteroids for mortality in hospitalised community-acquired pneumonia

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs.

## PICO
- **P** - adults hospitalised with community-acquired pneumonia (CAP).
- **I** - systemic corticosteroids added to standard antimicrobial/supportive care.
- **C** - placebo, usual care, standard care, or conventional therapy.
- **O (primary)** - all-cause mortality at 30 days or in hospital.
- **O (harms)** - hyperglycaemia; gastrointestinal bleeding.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), systemic corticosteroid vs placebo/usual care.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - 30-day mortality preferred; in-hospital mortality accepted when
  that is the trial's reported short-term mortality window.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - adult hospitalised CAP or severe CAP population by title or registry conditions;
- **I3** - systemic corticosteroid vs placebo/usual/standard care;
- **design** - randomised comparison; double-blinding is not required because the
  target comparator includes placebo or standard-care controls.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational study, protocol-only);
- **X2** - wrong population (for example COVID-19/SARS-CoV-2 pneumonia, influenza,
  paediatric CAP, Pneumocystis pneumonia, scrub typhus pneumonitis, or ARDS without
  CAP as the title/condition population);
- **X3** - wrong intervention/comparison (no systemic corticosteroid-vs-control contrast);
- **X5** - off-topic: a primary trial of another topic/disease in this set
  (negative control).

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> 30-day or in-hospital all-cause mortality in an abstract-extractable form is
> recorded as target-result status at extraction, never as an exclusion. A
> published effect plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/corticosteroids-cap-mortality/records.json; screening replays offline)
- PubMed: targeted corticosteroid x community-acquired pneumonia x randomised
  placebo/control queries for hydrocortisone, methylprednisolone, prednisone, and
  dexamethasone trial reports.
- ClinicalTrials.gov: condition "community-acquired pneumonia", intervention
  "hydrocortisone".
- Comparator-reference seeding is disabled for this topic because the fixed NCT
  deduplication rule can let later secondary/subgroup reports replace the original
  trial report. Recall is instead checked with named positive controls.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells
of a study only if it has a zero cell. DerSimonian-Laird forbidden. Engine
validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Wu et al., *Journal of Critical Care* 2024, "Efficacy and safety of corticosteroids
for the treatment of community-acquired pneumonia: A systematic review and
meta-analysis of randomized controlled trials" (PMID 38128217, DOI
10.1016/j.jcrc.2023.154507; Unpaywall is_oa=true; no direct PubMed Central full
text resolved). Its abstract reports 15 RCTs and all-cause mortality RR 0.69
(95% CI 0.53-0.89).

## Controls
- **Positive** - the search must recover and include CAPE COD hydrocortisone
  (PMID 36942789), Torres/JAMA methylprednisolone severe CAP (PMID 25688779),
  and STEP prednisone CAP (PMID 25608756).
- **Negative** - RECOVERY dexamethasone for COVID-19 (PMID 32678530) must be
  recovered and excluded as the wrong population.
