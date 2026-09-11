# Protocol - mineralocorticoid receptor antagonists for all-cause mortality in HFrEF

**Registration.** The commit that adds/updates this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with heart failure with reduced ejection fraction (HFrEF) / systolic heart failure.
- **I** - a steroidal mineralocorticoid receptor antagonist, specifically spironolactone or eplerenone, added to recommended therapy.
- **C** - placebo added to recommended therapy.
- **O (primary)** - all-cause mortality.
- **O (harms)** - hyperkalemia; gynecomastia or breast pain.

## Estimand / population / timepoint
- **Estimand** - published RR/HR with 95% CI when reported, or risk ratio (RR) when only percentage-corroborated arm counts are extractable.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest randomised follow-up reported for all-cause mortality.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - adult HFrEF / systolic heart-failure population, judged from title or registry conditions;
- **I3** - spironolactone or eplerenone versus placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or post-hoc analysis not indexed as an RCT);
- **X2** - wrong population (e.g. HFpEF, mildly reduced EF, post-myocardial-infarction LV dysfunction, CKD, diabetes, dialysis, hypertension, cirrhosis, or other non-HFrEF population);
- **X3** - wrong intervention/comparison (no eligible spironolactone/eplerenone-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled in the machine-readable record;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports all-cause
> mortality, or gives a 2x2 vs only an effect+CI, is recorded as *target-result status*
> at extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: UID-anchored queries for RALES, EMPHASIS-HF, and the resolved open-access comparator.
- ClinicalTrials.gov: condition "HFrEF", intervention "mineralocorticoid receptor antagonist".
- Citation chasing: enabled from the comparator and positive-control trials; every retrieved record is still screened on P/I/C/design.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on the log ratio (RR/HR as configured for the outcome);
**Paule-Mandel** tau^2; **HKSJ** 95% CI on `t_{k-1}` with variance floor
`max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`.
0.5 continuity correction to all four cells of a study only if it has a zero cell.
DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Zhang et al., *Frontiers in Cardiovascular Medicine* 2025, "Mineralocorticoid receptor
antagonists in heart failure: a systematic review and meta-analysis" (PMID 40959489,
DOI 10.3389/fcvm.2025.1667236; PubMed links PubMed Central/free full text). The
comparator reports the HFrEF subgroup for all-cause mortality.

## Controls
- **Positive** - the search must recover the canonical HFrEF MRA trials:
  RALES (spironolactone) and EMPHASIS-HF (eplerenone).
- **Negative** - EPHESUS (eplerenone after acute myocardial infarction complicated by
  LV dysfunction and heart failure) must be recovered and EXCLUDED as same-drug but wrong-topic.
