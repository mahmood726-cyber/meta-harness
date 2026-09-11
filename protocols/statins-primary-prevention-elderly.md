# Protocol - statins for primary prevention in older adults

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page's Protocol tab and Reproducibility tab. The protocol is committed before
the synthesis is run.

## PICO
- **P** - older adults (>=70 years) without established cardiovascular disease.
- **I** - statin therapy, including rosuvastatin, pravastatin, or atorvastatin.
- **C** - placebo, usual care, or no-statin control.
- **O (primary)** - major vascular events / major cardiovascular events.
- **O (harms)** - muscle symptoms/myopathy; new-onset diabetes.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), statin vs placebo/control.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial or randomised trial analysis;
- **I2** - title-level or registry-condition population is older/elderly adults;
- **I3** - title-level or registry intervention is a statin or statin name;
- **I4** - comparator is placebo, usual care, or control;
- **design** - randomised statin allocation; double-blinding is not required because
  usual-care trials are eligible.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or PubMed record
  not indexed as a randomized controlled trial by the fixed screen);
- **X2** - wrong population (e.g. heart failure, atrial fibrillation, prior stroke,
  acute coronary syndrome, coronary disease, perioperative/non-cardiovascular disease);
- **X3** - wrong intervention/comparison (no statin-vs-placebo/usual-care/control contrast);
- **X5** - off-topic: a primary trial of another disease/topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether an included trial reports major
> vascular events, or gives a 2x2 table vs only an effect+CI, is recorded as
> target-result status at extraction - never as an exclusion. A published effect + 95% CI
> is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: focused statin-title searches for JUPITER older-person analyses, ALLHAT-LLT
  older-adult primary-prevention analyses, and STAREE older-adult atorvastatin reports.
- ClinicalTrials.gov: condition "Elderly", intervention "Atorvastatin".
- Comparator reference seeding is disabled for this topic because the resolved open-access
  comparator is an observational review; its reference list is not an RCT recall set for
  a randomized statin-vs-control harness.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study
only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1
(<1e-6).

## Comparator (resolved; open-access confirmed)
Huang, Zhu, and Ya, *Reviews in Cardiovascular Medicine* 2022, "Statin use in older
people primary prevention on cardiovascular disease: an updated systematic review and
meta-analysis" (PMID 39076238, PMCID PMC11273788, DOI 10.31083/j.rcm2304114; Unpaywall
is_oa=true). It reports total cardiovascular events HR 0.75 (95% CI 0.66-0.85) in older
primary-prevention statin users versus no-statin users. This is an external benchmark,
not an RCT-only comparator; exact RCT-only elderly primary-prevention meta-analyses
found during resolution were not open access.

## Controls
- **Positive** - the search must recover and include the JUPITER older-person rosuvastatin
  analysis (PMID 20404379) and ALLHAT-LLT older-adult pravastatin analyses (PMIDs
  28531241 and 30251369).
- **Negative** - CORONA (rosuvastatin in older patients with systolic heart failure,
  PMID 17984166 - different disease/topic) must be recovered and EXCLUDED as wrong
  population.
