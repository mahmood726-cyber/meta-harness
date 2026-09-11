# Protocol - HFNC versus conventional oxygen after ICU extubation

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and Reproducibility tab.
Committed before the synthesis is run.

## PICO
- **P** - adults extubated in an ICU or comparable critical-care post-extubation setting.
- **I** - high-flow nasal cannula / high-flow nasal oxygen applied after extubation.
- **C** - conventional oxygen therapy, standard oxygen therapy, Venturi mask, or comparable
  low-flow/non-positive-pressure oxygen delivery.
- **O (primary)** - reintubation after extubation.
- **O (harms)** - mortality; adverse events or complications.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), HFNC vs conventional oxygen.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - within 48 hours to 7 days after extubation, using the trial's protocol-defined
  reintubation window.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - adults after extubation in ICU/critical-care post-extubation care;
- **I3** - high-flow nasal cannula/high-flow nasal oxygen vs conventional oxygen therapy,
  standard oxygen therapy, Venturi mask, or comparable conventional oxygen delivery;
- **design** - parallel or crossover RCT; double blinding is not required and is not expected.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or wrong PubMed type);
- **X2** - wrong population (e.g. paediatric/neonatal patients, no title-level post-extubation
  or reintubation population signal);
- **X3** - wrong intervention/comparison (no HFNC/HFNO-vs-conventional oxygen contrast);
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports reintubation,
> gives a 2x2 table, gives only a published effect+CI, or reports only percentages is
> recorded as target-result status at extraction, never as an exclusion. A published
> effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: postextubation/high-flow nasal cannula/conventional oxygen/reintubation RCT
  queries, plus Venturi-mask wording to recover older and hypoxaemic-patient trials.
- ClinicalTrials.gov: condition "extubation failure", intervention "high-flow nasal cannula".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study
only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1
(<1e-6).

This is an NMA topic externally, but the harness synthesis is declared as the direct
pairwise HFNC-vs-conventional oxygen contrast only. No indirect NMA evidence is borrowed.

## Comparator (resolved; open-access confirmed)
Boscolo et al., *European Respiratory Review* 2023, "Noninvasive respiratory support after
extubation: a systematic review and network meta-analysis" (PMID 37019458, DOI
10.1183/16000617.0196-2022; Unpaywall is_oa=true; PubMed Central full text available).
It reports the NMA primary outcome as post-extubation respiratory failure, defined as
re-intubation secondary to post-extubation respiratory failure, and reports HFNO vs COT
OR 0.60 (95% CI 0.43-0.84) in the overall population.

## Controls
- **Positive** - the search must recover and include the landmark direct HFNC-vs-conventional
  post-extubation RCTs by Hernandez et al. 2016 (PMID 26975498), Maggiore et al. 2014
  (PMID 25003980), and Grieco et al. 2022 (PMID 35849787).
- **Negative** - FLORALI (PMID 25981908; high-flow oxygen for acute hypoxaemic respiratory
  failure before intubation, another disease/state) must be recovered and EXCLUDED as the
  wrong population.
