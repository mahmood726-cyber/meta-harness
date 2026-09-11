# Protocol - semaglutide for 3-point MACE in obesity without diabetes

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with overweight or obesity and established cardiovascular disease but
  without diabetes.
- **I** - once-weekly subcutaneous semaglutide 2.4 mg added to standard care.
- **C** - placebo added to standard care.
- **O (primary)** - 3-point major adverse cardiovascular events, defined as
  cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke.
- **O (harms / secondary)** - gastrointestinal adverse events, adverse events leading to
  permanent discontinuation, and any further outcome the resolved comparator reports.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), semaglutide vs placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / mean follow-up 39.8 months.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - adults with overweight or obesity and established cardiovascular disease but
  without diabetes, judged from the title or registry conditions;
- **I3** - semaglutide vs placebo contrast;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. type 2 diabetes, type 1 diabetes, chronic kidney
  disease, heart failure, sleep apnea, or obesity trials without established
  cardiovascular disease);
- **X3** - wrong intervention/comparison (no semaglutide-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives
> a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as
> an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: exact SELECT title/PMID sweeps for the main MACE report. Later SELECT secondary
  analyses are not configured as positive controls because they share NCT03574597 and the
  fixed harness deduplicates same-NCT PubMed records to the latest-year publication.
- ClinicalTrials.gov: condition "cardiovascular disease obesity without diabetes",
  intervention "semaglutide".
- Comparator/reference seeding is disabled so the broader comparator's reference list does
  not pull in semaglutide obesity trials outside the established-CVD SELECT population.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI
path on the same ratio/log scale; 2x2 extraction is available but is not required when a
trial reports an HR + CI.

## Comparator (resolved; open-access confirmed)
Stefanou et al., *Therapeutic Advances in Neurological Disorders* 2024, "Risk of major
adverse cardiovascular events and all-cause mortality under treatment with GLP-1 RAs or
the dual GIP/GLP-1 receptor agonist tirzepatide in overweight or obese adults without
diabetes: a systematic review and meta-analysis" (PMID 39345822, DOI
10.1177/17562864241281903; Unpaywall is_oa=true; PubMed Central PMC11437580). It reports
pooled MACE OR 0.79 (95% CI 0.71-0.89) over 16 RCTs in overweight or obese adults
without diabetes. This comparator is broader than the registered lane's semaglutide-only
SELECT population; the exact registered lane has one landmark eligible RCT.

## Controls
- **Positive** - SELECT main MACE report (PMID 37952131), the verified eligible landmark
  trial report. Only this positive control is configured to avoid same-NCT secondary
  SELECT reports superseding the main MACE paper during fixed harness deduplication.
- **Negative** - SUSTAIN-6 (PMID 27633186: semaglutide, randomized, placebo-controlled,
  but type 2 diabetes rather than obesity without diabetes) must be recovered and
  EXCLUDED by the population rule.
