# Protocol - SGLT2 inhibitors for hospitalization for heart failure in type 2 diabetes or cardiovascular risk

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with type 2 diabetes or cardiovascular risk enrolled in broad
  cardiovascular outcome trials, not trials whose entry criterion is HFrEF/HFpEF
  or chronic kidney disease.
- **I** - SGLT2 inhibitors, including empagliflozin, canagliflozin,
  dapagliflozin, and ertugliflozin.
- **C** - placebo.
- **O (primary)** - hospitalization for heart failure, using the trial-reported
  time-to-first-event effect for HHF.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), SGLT2 inhibitor vs placebo, pooled on the log
  ratio scale.
- **Population** - intention-to-treat as randomised / full analysis set, as
  reported by each cardiovascular outcome trial.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with type 2 diabetes or cardiovascular risk in a
  broad cardiovascular outcome trial;
- **I3** - empagliflozin, canagliflozin, dapagliflozin, ertugliflozin, or SGLT2
  inhibitor as the randomised intervention;
- **I4** - placebo comparator;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population, including heart failure with reduced or preserved
  ejection fraction as an entry criterion, chronic kidney disease / diabetic
  nephropathy as an entry criterion, type 1 diabetes, or no diabetes/CV-risk
  population;
- **X3** - wrong intervention/comparison, including active comparators;
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports HHF,
and whether it reports arm counts or only an effect plus confidence interval, is
recorded at extraction. A published HR plus 95% CI is a poolable input; crude
event counts from CT.gov or labels are not substituted for HRs.

## Search
- PubMed: direct UID queries for EMPA-REG OUTCOME, CANVAS Program,
  DECLARE-TIMI 58, VERTIS CV, and an OA SGLT2 heart-failure-hospitalization
  meta-analysis comparator.
- ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention
  "SGLT2 inhibitor".
- Registry-first enumeration: condition "type 2 diabetes", intervention
  "SGLT2 inhibitor".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Published HR
inputs are pooled on the log ratio scale.

## Comparator (resolved; OA confirmed)
Zhang et al., *Frontiers in Endocrinology* 2021, "Sodium Glucose Cotransporter 2
Inhibitors Reduce the Risk of Heart Failure Hospitalization in Patients With Type
2 Diabetes Mellitus: A Systematic Review and Meta-Analysis of Randomized
Controlled Trials" (PMID 33519713, PMCID PMC7843571, DOI
10.3389/fendo.2020.604250). Zelniker et al. 2019 (PMID 30424892) was considered
first for CVOT scope, but Unpaywall reported the article closed access.

## Pivotal
- **DECLARE-TIMI 58** - NCT01730534; positive-control PMID 30415602.

## Controls
- **Positive** - the search must recover and include DECLARE-TIMI 58 (PMID
  30415602).
- **Negative** - FIDELIO-DKD (finerenone in CKD and type 2 diabetes, PMID
  33264825) must be recovered and EXCLUDED as wrong intervention.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that the
protocol's broad cardiovascular-outcome-trial scope was not executable. The config
now requires cardiovascular-outcome / cardiovascular-events / MACE wording, so
short glycaemic or imaging-marker diabetes trials are not included merely because
they are randomized SGLT2 placebo trials. This amendment changes screening only.
