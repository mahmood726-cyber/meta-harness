# Protocol - prone positioning for mortality in moderate-to-severe ARDS

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page's Protocol tab and Reproducibility tab. Committed before the synthesis is
run.

## PICO
- **P** - adults with moderate-to-severe acute respiratory distress syndrome (ARDS)
  receiving invasive mechanical ventilation.
- **I** - prone positioning / prone ventilation.
- **C** - supine positioning / conventional supine ventilation.
- **O (primary)** - all-cause mortality.
- **O (harms)** - pressure sores; endotracheal-tube complications.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), prone positioning vs supine positioning.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - 28-90 day mortality, or ICU/hospital mortality when that is the
  abstract-reported mortality timepoint.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial, or randomized interventional registry record;
- **I2** - title or registry conditions identify acute respiratory distress syndrome
  (ARDS), with adult moderate/severe ARDS trials in scope;
- **I3** - prone positioning / prone ventilation is the randomized intervention;
- **I4** - the comparator is supine positioning / conventional supine ventilation;
- **design** - randomised, parallel or otherwise controlled allocation. Double-blinding
  is not required because positioning cannot be blinded.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational study, protocol-only record);
- **X2** - wrong population or duplicate/non-primary population report (e.g. pediatric,
  neonatal, awake/non-intubated COVID, survivor follow-up, pressure-ulcer prevention
  while already prone);
- **X3** - wrong intervention/comparison (no randomized prone-vs-supine contrast);
- **X-DESIGN** - not a randomized controlled design;
- **X5** - off-topic: a primary trial of another topic/disease in this set (negative
  control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports mortality, and
> whether it reports a 2x2 table versus only an effect+CI, is recorded as target-result
> status at extraction - never as an exclusion. A published effect + 95% CI is a
> poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: title-focused prone-positioning/prone-ventilation ARDS randomized-trial
  searches, plus comparator-reference seeding.
- ClinicalTrials.gov: condition "acute respiratory distress syndrome", intervention
  "prone positioning".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a
study only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
*CMAJ* 2014, "Effect of prone positioning during mechanical ventilation on mortality
among patients with acute respiratory distress syndrome: a systematic review and
meta-analysis" (PMID 24863923, PMCID PMC4081236, DOI 10.1503/cmaj.140081; Unpaywall
is_oa=true). It reports mortality RR 0.74 (95% CI 0.59-0.95) in the protective
ventilation subgroup of 6 trials.

## Controls
- **Positive** - PubMed-verified landmark prone-vs-supine ARDS trials must be recovered
  and included: PROSEVA (PMID 23688302), Prone-Supine II (PMID 19903918), and Mancebo
  prolonged prone ventilation (PMID 16556697).
- **Negative** - CORP, colchicine for recurrent pericarditis (PMID 21873705; another
  disease/topic), must be recovered and EXCLUDED.
