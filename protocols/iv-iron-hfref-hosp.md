# Protocol - intravenous iron for heart-failure hospitalization in HFrEF with iron deficiency

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. The protocol is committed before the synthesis is run.

## PICO
- **P** - adults with heart failure with reduced or mildly reduced ejection fraction and iron deficiency.
- **I** - intravenous iron, including ferric carboxymaltose, ferric derisomaltose, or iron sucrose.
- **C** - placebo, usual care, standard care, or no-treatment control.
- **O (primary)** - heart-failure hospitalization at trial end / longest reported follow-up.
- **O (harms)** - injection-site/administration-site reactions; hypersensitivity reactions.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), intravenous iron vs placebo/standard care.
- **Population** - intention-to-treat as randomized.
- **Timepoint** - trial end / longest reported follow-up.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomized controlled trial;
- **I2** - population is heart failure with reduced or mildly reduced ejection fraction and iron deficiency;
- **I3** - intravenous iron vs placebo, usual care, standard care, or no-treatment control;
- **design** - placebo-controlled or standard-care-controlled RCT; double blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (for example HFpEF, COPD, pulmonary hypertension, dialysis, pregnancy/postpartum, inflammatory bowel disease, or restless legs);
- **X3** - wrong intervention/comparison (no intravenous iron vs eligible control contrast);
- **X5** - off-topic: a primary trial of another disease area in this set (negative control).

> Eligibility is NOT on the outcome axis. Whether a trial reports heart-failure
> hospitalization, or gives a 2x2 vs only an effect+CI, is recorded as target-result
> status at extraction - never as an exclusion. A published effect + 95% CI is a
> poolable input. Composite cardiovascular-death/heart-failure-hospitalization effects
> are not treated as standalone heart-failure hospitalization for the primary outcome.

## Search (fetch-once; raw results committed under cache/iv-iron-hfref-hosp/records.json; screening replays offline)
- PubMed: targeted primary-report searches for FAIR-HF2, AFFIRM-AHF, and IRONMAN.
- PubMed comparator-reference seeding: trials cited by the resolved comparator are fetched and screened by the same rules.
- ClinicalTrials.gov: condition "heart failure reduced ejection fraction iron deficiency", intervention "intravenous iron".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a
study only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Parmananda et al., *Diseases* 2024, "The Efficacy and Safety of Ferric
Carboxymaltose in Heart Failure with Reduced Ejection Fraction and Iron Deficiency:
An Updated Systematic Review and Meta-Analysis of Randomized Controlled Trials"
(PMID 39727669, PMC11727542, DOI 10.3390/diseases12120339; Unpaywall is_oa=true).
It reports total HF hospitalizations OR 0.59 (95% CI 0.40 to 0.88) over six RCTs,
plus serious adverse events and qualitative angioedema/hypersensitivity detail.

## Controls
- **Positive** - the search must recover FAIR-HF2 (PMID 40159390), AFFIRM-AHF
  (PMID 33197395), and IRONMAN (PMID 36347265).
- **Negative** - the COPD intravenous-iron RCT (PMID 32565444) must be recovered
  and EXCLUDED as wrong population.
