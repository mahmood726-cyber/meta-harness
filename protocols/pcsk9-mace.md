# Protocol - PCSK9 inhibitors for major adverse cardiovascular events

**Registration.** The commit that adds/updates this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with established ASCVD or title/registry-supported high ASCVD risk.
- **I** - PCSK9 inhibitor monoclonal antibody therapy: evolocumab or alirocumab.
- **C** - placebo.
- **O (primary)** - major adverse cardiovascular events (MACE), as defined by each trial.
- **O (harms)** - injection-site reactions and adverse events leading to discontinuation.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), PCSK9 inhibitor vs placebo, using published
  trial effect estimates with 95% confidence intervals when arm-level event-time
  data are not available in the abstract.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - longest reported trial follow-up for the primary MACE endpoint.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with established ASCVD or title/registry-supported
  high ASCVD risk;
- **I3** - evolocumab or alirocumab compared with placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or secondary
  analysis not indexed as a primary randomised trial record);
- **X2** - wrong population by title/registry conditions (e.g. kidney disease,
  chronic kidney disease, heart failure, or venous thromboembolism);
- **X3** - wrong intervention/comparison (no evolocumab/alirocumab-vs-placebo
  contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports MACE, or gives
> arm counts vs only an effect+CI, is recorded as target-result status at extraction,
> never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: title-level searches for the primary FOURIER and ODYSSEY OUTCOMES reports.
  Comparator-reference seeding is disabled for this topic because later secondary
  publications share the same trial NCTs and can supersede the primary outcome
  reports in the harness deduplication step.
- ClinicalTrials.gov: condition "ASCVD", intervention "alirocumab".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(HR); **Paule-Mandel** tau^2; **HKSJ** 95% CI
on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. Trial HRs and 95% CIs are transformed to log
scale by the harness. DerSimonian-Laird forbidden. Engine validated vs metafor
5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Xiang et al., *Frontiers in Cardiovascular Medicine* 2022, "Effect of alirocumab
and evolocumab on all-cause mortality and major cardiovascular events: A
meta-analysis focusing on the number needed to treat" (PMID 36531722, DOI
10.3389/fcvm.2022.1016802; Unpaywall is_oa=true; PubMed Central available as
PMC9755489). It reports pooled MACE RR 0.83 (95% CI 0.79-0.87) in patients with
established ASCVD.

## Controls
- **Positive** - the search must recover and include the canonical large
  double-blind placebo-controlled outcome trials FOURIER (PMID 28304224) and
  ODYSSEY OUTCOMES (PMID 30403574).
- **Negative** - FIDELIO-DKD (finerenone in chronic kidney disease and type 2
  diabetes; PMID 33264825) must be recovered and EXCLUDED as wrong population and
  wrong intervention for this topic.

## Amendment 2026-09-16 (external-audit recovery; co-primary endpoint rule)
**Status: retrospective external-audit recovery before extraction/rebuild.** This
amendment does not make the retrieval systematic and does not rename the pinned
slug/URL. The page remains STALE for `search_not_executed`: the added records are
hand-named audit recoveries, not evidence that the original search ran.

- **Added hand-named records.** VESALIUS-CV (PMID 41211925), ODYSSEY LONG TERM
  (PMID 25773378), and GLAGOV (PMID 27846344) are added through `extra_pmids`
  with `discovery_capable=false`, source kind `EXTRA_PMIDS`, on the external audit
  query text `external audit topic 15 (Mahmood, 2026-09-16): VESALIUS-CV;
  ODYSSEY LONG TERM; GLAGOV`.
- **Co-primary endpoint rule.** When a trial registers more than one primary MACE
  definition, pool the prespecified co-primary endpoint whose component set is
  closest to canonical 3-point MACE: cardiovascular/coronary-heart-disease death,
  myocardial infarction, and stroke. If component-set closeness is tied, use the
  co-primary listed first in the registration/publication.
- **Rule disclosure.** VESALIUS-CV reports both co-primary results in its abstract,
  so both the 3-point HR 0.75 (95% CI 0.65 to 0.86) and the 4-point HR 0.81
  (95% CI 0.73 to 0.89) were known when this rule was written. The rule is justified
  only by component-set closeness to canonical 3-point MACE, never by which result
  is larger or more precise.
- **Sensitivity requirement.** The alternative VESALIUS-CV co-primary endpoint is
  always rendered as a sensitivity row when the selected co-primary is pooled; it is
  not hidden.
- **Outcome-layer discipline.** ODYSSEY LONG TERM and GLAGOV screen in on
  P/I/C/design if the record text supports those axes. ODYSSEY LONG TERM reports a
  post-hoc MACE analysis and is typed `outcome_post_hoc_not_pooled`; GLAGOV reports
  surrogate atheroma-volume outcomes and no MACE result and is typed
  `outcome_not_reported`. Neither is pooled.
