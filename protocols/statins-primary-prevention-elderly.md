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

## Retrospective protocol erratum (2026-09-28) -- an RCT-only elderly analysis exists; conditions are not diagnoses
**Labelled retrospective: written after data were seen; the sections above are left unchanged as registered.**
- The comparator section says RCT-only elderly primary-prevention meta-analyses "were not open access". An external
  review reproduced one: Ridker 2017 (Circulation 135:1979-81, PMID 28385949), JUPITER + HOPE-3 participants aged
  >= 70, MI/stroke/CV death, HR 0.74 (0.61-0.91). It is free to read at the publisher but is not under an open
  licence, is not in PMC, and the publisher page answers automated requests with a bot check (not bypassed), so it
  is not held here. It is registered as an RCT checkpoint (registry/positive_controls.json, PENDING_SOURCE), never as
  the comparator; Huang 2022 stays the registered comparator and is observational (shared RCT inputs: none).
- The letter's HOPE-3 age >= 70 stratum is the same kind of input as JUPITER's older-adults report; the
  title-seeded search could not find it. It is recorded as a discovery case, not added, while the letter is not held.
- A registry "conditions" entry can be what a trial PREVENTS. The X2 population exclusions are read against the
  trial's own eligibility criteria: a registered condition that the trial's exclusion criteria refuse at entry is
  never a baseline diagnosis (harness/condition_role.py). PREVENTABLE (NCT04262206; aged >= 75 without
  cardiovascular disease, disability or dementia) is therefore eligible; it is ongoing (RECRUITING) with no results,
  so it adds no pooled input.
- A secondary report's registration is its parent trial's: JUPITER's older-adults report (PMID 20404379) is
  NCT00239681 and ALLHAT-LLT's older-adults report (PMID 30251369) is NCT00000542, recorded with located evidence in
  cache/statins-primary-prevention-elderly/parent_registrations.json. A blank registry link is not "unregistered".
- Scope: screening and the family ledger only. The pooled trials and the pooled result are unchanged.
