# Protocol - finerenone for kidney outcomes in CKD and type 2 diabetes

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with chronic kidney disease and type 2 diabetes, including diabetic
  kidney disease / diabetic nephropathy terminology.
- **I** - finerenone (including development-code synonym BAY94-8862) added to
  background standard care.
- **C** - placebo added to background standard care.
- **O (primary)** - kidney composite outcome: kidney failure, sustained eGFR decline,
  or renal death, using the trial-reported composite definition.
- **O (harms)** - hyperkalemia and hyperkalemia-related treatment discontinuation.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), finerenone vs placebo, pooled on the log ratio scale.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is chronic kidney disease with type 2 diabetes / diabetic kidney
  disease / diabetic nephropathy;
- **I3** - finerenone/BAY94-8862 vs placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or meta-analysis);
- **X2** - wrong population (for example heart failure without the target CKD/T2D
  population, type 1 diabetes, nondiabetic CKD, pericarditis, or atrial fibrillation);
- **X3** - wrong intervention/comparison (no finerenone-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports the kidney
composite, and whether it reports arm counts or only an effect plus confidence interval,
is recorded at extraction. A published effect plus 95% CI is a poolable input.

## Search
- PubMed: narrow title/year queries for FIDELIO-DKD, FIGARO-DKD, and ARTS-DN primary
  reports, plus meta-analysis resolution.
- ClinicalTrials.gov: condition "diabetic kidney disease", intervention "finerenone".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 for the binary RR path; published HR inputs are pooled on the same log
ratio scale.

## Comparator (resolved; OA confirmed)
Sarafidis et al., *Frontiers in Endocrinology* 2023, "Finerenone in type 2 diabetes and
renal outcomes: A random-effects model meta-analysis" (PMID 36742404, PMC9895809,
DOI 10.3389/fendo.2023.1114894; Unpaywall is_oa=true). It reports renal composite HR
0.84 (95% CI 0.77-0.92) and hyperkalaemia RR 2.22 (95% CI 1.93-2.24).

## Controls
- **Positive** - the search must recover and include FIDELIO-DKD (PMID 33264825),
  FIGARO-DKD (PMID 34449181), and ARTS-DN (PMID 26325557).
- **Negative** - FINEARTS-HF (finerenone for heart failure, PMID 39225278, another topic
  population) must be recovered and EXCLUDED as wrong population.
