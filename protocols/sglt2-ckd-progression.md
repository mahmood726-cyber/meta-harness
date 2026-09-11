# Protocol - SGLT2 inhibitors for CKD progression in chronic kidney disease

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with chronic kidney disease, including diabetic nephropathy terminology.
- **I** - an SGLT2 inhibitor, specifically dapagliflozin, canagliflozin, or
  empagliflozin, added to background standard care.
- **C** - placebo added to background standard care.
- **O (primary)** - CKD progression / kidney composite outcome, using the
  trial-reported composite definition.
- **O (harms)** - diabetic ketoacidosis and lower-limb amputation.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), SGLT2 inhibitor vs placebo, pooled on the log
  ratio scale when trial-reported HRs are extractable; percentage-corroborated arm
  counts are accepted by the harness as poolable ratio inputs when the abstract
  presents them.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - adult chronic kidney disease / kidney disease / diabetic nephropathy
  population, judged from title or registry conditions;
- **I3** - dapagliflozin, canagliflozin, or empagliflozin versus placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population (for example heart failure, myocardial infarction,
  pericarditis, atrial fibrillation, or another non-CKD population);
- **X3** - wrong intervention/comparison (no eligible SGLT2-inhibitor-vs-placebo
  contrast);
- **X-DESIGN** - not double-blind and placebo-controlled in the machine-readable
  record;
- **X5** - off-topic: a primary trial of another topic in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports CKD
progression, and whether it reports arm counts or only an effect plus confidence
interval, is recorded at extraction. A published effect plus 95% CI is a poolable
input.

## Search
- PubMed: UID-anchored queries for the DAPA-CKD, CREDENCE, and EMPA-KIDNEY
  primary reports, plus the resolved open-access comparator.
- ClinicalTrials.gov: condition "chronic kidney disease", intervention "SGLT2
  inhibitor".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 for the binary RR path; published HR inputs are pooled on the same
log ratio scale.

## Comparator (resolved; OA confirmed)
The SMART-C collaborative meta-analysis in *JAMA* 2026, "SGLT2 Inhibitors and Kidney
Outcomes by Glomerular Filtration Rate and Albuminuria: A Meta-Analysis" (PMID
41203232, PMC12595549, DOI 10.1001/jama.2025.20834; Unpaywall is_oa=true). It reports
CKD progression HR 0.62 (95% CI 0.57-0.68) across 10 randomized trials.

## Controls
- **Positive** - the search must recover the landmark CKD SGLT2 inhibitor trials:
  DAPA-CKD (PMID 32970396), CREDENCE (PMID 30990260), and EMPA-KIDNEY (PMID
  36331190).
- **Negative** - DAPA-HF (dapagliflozin, placebo-controlled, but HFrEF rather than
  CKD; PMID 31535829) must be recovered and EXCLUDED as wrong population.
