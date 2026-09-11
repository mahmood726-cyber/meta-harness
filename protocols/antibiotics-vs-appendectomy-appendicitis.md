# Protocol - antibiotics vs appendectomy for uncomplicated appendicitis in adults

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with uncomplicated/simple acute appendicitis, matched on title or registry conditions.
- **I** - antibiotic therapy as initial treatment.
- **C** - appendectomy/appendicectomy or operative management.
- **O (primary)** - treatment failure or complication at 1 year.
- **O (harms)** - any trial-reported complication, and delayed appendectomy or recurrent appendicitis.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), antibiotics vs appendectomy.
- **Population** - intention-to-treat as randomised when reported.
- **Timepoint** - 1 year for the primary outcome.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised trial;
- **I2** - population is acute appendicitis, targeted to adult uncomplicated/simple disease where the title or registry conditions specify it;
- **I3** - initial antibiotic therapy versus appendectomy/appendicectomy/surgery;
- **design** - randomised comparison; double-blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not a randomised trial (review, guideline, observational study, protocol-only when not a trial results record);
- **X2** - wrong population/topic (e.g. pediatric/child population, pregnancy, abscess/phlegmon/rupture, postoperative-only, drainage-only, or microbiota/etiology records);
- **X3** - wrong intervention/comparison (no antibiotics-vs-appendectomy contrast);
- **X-DESIGN** - not randomised;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 1-year treatment
> failure/complications, or gives a 2x2 vs only an effect+CI, is recorded as
> *target-result status* at extraction - never as an exclusion. A published effect +
> 95% CI is a poolable input. Trial-reported complications at other timepoints are
> tracked under harms rather than used as the primary 1-year endpoint.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: narrow title/journal/year searches for CODA, APPAC, Vons, Styrud, Hansson, and Eriksson/Granstrom reports; comments and letters are excluded in the query.
- ClinicalTrials.gov: condition "acute appendicitis", intervention "ertapenem appendectomy".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study only if
it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Gavriilidis et al., *World Journal of Emergency Surgery* 2024, "A meta-analysis and
trial sequential analysis comparing nonoperative versus operative management for
uncomplicated appendicitis: a focus on randomized controlled trials" (PMID 38218862,
DOI 10.1186/s13017-023-00531-6; Unpaywall is_oa=true; PMC10787963). It reports eight
RCTs in adults with uncomplicated appendicitis, treatment complications RR 0.66
(95% CI 0.61-1.04), and 1-year treatment success RR 0.69 (95% CI 0.61-0.77).

## Controls
- **Positive** - CODA (PMID 33017106), APPAC (PMID 26080338), and Vons et al. (PMID 21550483) must be recovered and included by P/I/C/design.
- **Negative** - CORP colchicine for recurrent pericarditis (PMID 21873705), a real RCT from another disease topic, must be recovered and EXCLUDED as wrong population.
