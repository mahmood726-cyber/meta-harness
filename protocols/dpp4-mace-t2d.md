# Protocol - DPP-4 inhibitors for 3-point MACE in type 2 diabetes

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with type 2 diabetes.
- **I** - DPP-4 inhibitors, including sitagliptin, saxagliptin, alogliptin, and
  linagliptin.
- **C** - placebo.
- **O (primary)** - 3-point major adverse cardiovascular events, using the
  trial-reported cardiovascular death, myocardial infarction, or stroke composite.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), DPP-4 inhibitor vs placebo, pooled on the log
  ratio scale.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with type 2 diabetes;
- **I3** - sitagliptin, saxagliptin, alogliptin, linagliptin, or a DPP-4 inhibitor
  as the randomised intervention;
- **I4** - placebo comparator;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population, including type 1 diabetes;
- **X3** - wrong intervention/comparison, including active-comparator DPP-4 CVOTs
  such as CAROLINA;
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports 3-point
MACE, and whether it reports arm counts or only an effect plus confidence interval,
is recorded at extraction. A published effect plus 95% CI is a poolable input.

## Search
- PubMed: direct UID queries for SAVOR-TIMI 53, EXAMINE, TECOS, CARMELINA, and
  CAROLINA primary reports, plus a DPP-4 cardiovascular-outcome-trial
  meta-analysis comparator.
- ClinicalTrials.gov: condition "type 2 diabetes", intervention "DPP-4 inhibitor".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Published HR inputs
are pooled on the log ratio scale.

## Comparator (resolved; OA confirmed)
Patoulias et al., *World Journal of Cardiology* 2021, "Cardiovascular efficacy and
safety of dipeptidyl peptidase-4 inhibitors: A meta-analysis of cardiovascular
outcome trials" (PMID 34754403, PMC8554356, DOI 10.4330/wjc.v13.i10.585).

## Pivotal
- **TECOS** - NCT00790205; positive-control PMID 26052984.

## Controls
- **Positive** - the search must recover and include TECOS (PMID 26052984).
- **Negative** - DECLARE-TIMI 58 (dapagliflozin in type 2 diabetes, PMID 30415602)
  must be recovered and EXCLUDED as wrong intervention.
