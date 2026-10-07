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

## Amendment 2026-10-07 (D10 multi-outcome: outcomes the comparator also reports)
**Status: registered BEFORE any extraction of these outcomes; retrospective with respect to the trial pool**
(the pool, search and eligibility were fixed before D10 and are unchanged). Decision: Mahmood D10 (relayed
2026-10-07): add outcomes the comparator meta also reports -- all-cause mortality, key harms and its
prespecified secondaries. Rule `registry/outcome_amendments/D10_rule.json` (commit a40e00850); proposal
`registry/outcome_amendments/statins-primary-prevention-elderly.proposal.json` (commit 10878e620). The outcomes were chosen from the
comparator's (PMID 32529863) own text by that rule alone; no trial-level result for them
was extracted or viewed by this lane before this amendment.

- **New secondary outcome: All-cause mortality** (P1_ALL_CAUSE_MORTALITY). Estimand OR; timepoint trial-reported follow-up;
  keywords all-cause mortality, all-cause death, death from any cause, deaths from any cause, any-cause death, any-cause mortality, total mortality, overall mortality. The comparator prints OR 0.94
  (0.76 to 1.16): "For the primary prevention subgroup, four trials (14,821 patients in total) 37 – 40 found that statins had no statistically significant effect on all-cause mortality compared with the control group (OR: 0.94, 95% CI: …" [R1 regex over the held comparator text].
- **Extraction.** The served ladder is unchanged (abstract, CT.gov results, held open full texts, verified
  inputs); trials it leaves without a value may be read by recorded codex over open sources only (CC BY / CC0
  full text, abstracts, AACT, FDA, EMA with acknowledgement, NICE OGL/CC), every value quote-gated.
- **Comparison.** Each outcome's pooled result is compared with the comparator's printed result on the
  comparator's measure; a measure difference is reported, never converted. Nothing is served until
  Mahmood signs its notice.
