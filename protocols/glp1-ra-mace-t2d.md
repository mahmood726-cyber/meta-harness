# Protocol - GLP-1 receptor agonists for 3-point MACE in type 2 diabetes

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with type 2 diabetes.
- **I** - GLP-1 receptor agonist therapy (liraglutide, semaglutide, dulaglutide,
  albiglutide, efpeglenatide, exenatide, or lixisenatide) added to usual care.
- **C** - placebo added to usual care.
- **O (primary)** - 3-point major adverse cardiovascular events, defined as cardiovascular
  death, nonfatal myocardial infarction, or nonfatal stroke.
- **O (harms / secondary)** - gastrointestinal adverse events, discontinuation for adverse
  events, and any further harm outcome the resolved comparator reports.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), GLP-1 receptor agonist vs placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest primary cardiovascular outcome follow-up.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with type 2 diabetes, judged from the title or registry
  conditions;
- **I3** - a GLP-1 receptor agonist vs placebo contrast;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. obesity without diabetes, type 1 diabetes, or gestational
  diabetes);
- **X3** - wrong intervention/comparison (no GLP-1 receptor agonist-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives
> a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as
> an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: exact-title sweeps for the large GLP-1 receptor agonist cardiovascular outcome
  trials in type 2 diabetes (LEADER, SUSTAIN-6, REWIND, HARMONY Outcomes, AMPLITUDE-O,
  PIONEER-6, EXSCEL, and ELIXA).
- ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention
  "efpeglenatide".
- Fixed-screen note: several PubMed abstracts for verified double-blind CVOTs do not use
  the literal phrase "double-blind"; the config therefore does not require that literal
  abstract/title string, while the protocol eligibility criterion remains double-blind
  placebo-controlled design.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI
path on the same ratio/log scale; 2x2 extraction is available but is not required when a
trial reports an HR + CI.

## Comparator (resolved; open-access confirmed)
Giugliano et al., *Cardiovascular Diabetology* 2021, "GLP-1 receptor agonists and
cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs" (PMID
34526024, DOI 10.1186/s12933-021-01366-8; Unpaywall is_oa=true; PubMed Central
PMC8442438). It reports pooled MACE HR 0.86 (95% CI 0.79-0.94) over 8 cardiovascular
outcome trials.

## Controls
- **Positive** - the search must recover and include LEADER, SUSTAIN-6, and REWIND.
- **Negative** - SELECT (semaglutide, double-blind, placebo-controlled, but obesity without
  diabetes - another disease population) must be recovered and EXCLUDED by the population
  rule.
