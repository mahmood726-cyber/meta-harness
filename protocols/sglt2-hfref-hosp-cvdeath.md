# Protocol - SGLT2 inhibitors for cardiovascular death or heart-failure hospitalisation in HFrEF

**Registration.** The commit that adds/updates this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with heart failure with reduced ejection fraction (HFrEF).
- **I** - an SGLT2 inhibitor, specifically dapagliflozin or empagliflozin, added to recommended therapy.
- **C** - placebo added to recommended therapy.
- **O (primary)** - composite cardiovascular death or hospitalisation for heart failure.
- **O (harms)** - volume depletion or hypotension; diabetic ketoacidosis.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR) when arm counts are extractable, or published HR/RR with 95% CI when that is the source-reported poolable input.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest randomised follow-up reported for the composite endpoint.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - adult HFrEF / reduced-ejection-fraction heart-failure population, judged from title or registry conditions;
- **I3** - dapagliflozin or empagliflozin versus placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or post-hoc analysis not indexed as an RCT);
- **X2** - wrong population (e.g. HFpEF, mildly reduced/preserved EF, diabetes-only, CKD-only, post-MI, or other non-HFrEF population);
- **X3** - wrong intervention/comparison (no eligible SGLT2-inhibitor-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled in the machine-readable record;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports the composite
> endpoint, or gives a 2x2 vs only an effect+CI, is recorded as *target-result status* at
> extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: UID-anchored queries for the DAPA-HF and EMPEROR-Reduced primary reports, plus the resolved open-access comparator.
- ClinicalTrials.gov: condition "HFrEF", intervention "SGLT2 inhibitor".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study only if
it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Li et al., *ESC Heart Failure* 2022, "Sodium-glucose cotransporter 2 inhibitors in heart
failure with reduced or preserved ejection fraction: a meta-analysis" (PMID 35112512,
DOI 10.1002/ehf2.13805; Unpaywall is_oa=true; PMC8934917 available). The comparator's
LVEF <=40% subgroup reports the assigned HFrEF composite endpoint.

## Controls
- **Positive** - the search must recover the canonical HFrEF SGLT2 inhibitor trials:
  DAPA-HF and EMPEROR-Reduced.
- **Negative** - EMPA-REG OUTCOME (empagliflozin, double-blind, placebo-controlled, but
  type 2 diabetes rather than HFrEF) must be recovered and EXCLUDED.
