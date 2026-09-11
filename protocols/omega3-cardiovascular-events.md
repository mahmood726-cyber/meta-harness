# Protocol - marine omega-3 fatty acids for major cardiovascular events

**Registration.** The commit that adds this file is the registration of this review; its
SHA is embedded in the page's Protocol tab and its Reproducibility tab. Committed BEFORE
the synthesis is run.

## PICO
- **P** - adults at cardiovascular risk, including established cardiovascular disease,
  diabetes or dysglycemia, prior myocardial infarction, heart failure, coronary disease,
  dyslipidemia, hypertriglyceridemia, or other title-level cardiovascular-risk populations.
- **I** - marine omega-3 fatty acid supplementation, including EPA, DHA, EPA+DHA, fish oil,
  omega-3 carboxylic acids, or icosapent ethyl.
- **C** - placebo or inert control, including corn oil, olive oil, mineral oil, or usual-care
  control where the randomized comparison is otherwise eligible.
- **O (primary)** - major vascular events / MACE.
- **O (harms)** - atrial fibrillation; bleeding.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), omega-3 vs placebo/control. Published ratio effects with
  95% CI are poolable when arm counts are not abstract-extractable.
- **Population** - intention-to-treat as randomized.
- **Timepoint** - trial end / longest randomized follow-up reported in the abstract.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomized controlled trial;
- **I2** - adult cardiovascular-risk population, judged from title or registry conditions;
- **I3** - marine omega-3 fatty acid supplement vs placebo/control;
- **design** - double-blind, placebo-controlled or blinded inert-control RCT.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, subgroup-only report);
- **X2** - wrong population (for example depression, pregnancy, eye disease, dementia,
  inflammatory bowel disease, osteoarthritis, or atrial-fibrillation recurrence);
- **X3** - wrong intervention/comparison (no randomized marine omega-3-vs-control contrast);
- **X-DESIGN** - not double-blind and placebo/inert-control;
- **X5** - off-topic: a primary trial of another topic/disease in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports major vascular events
> / MACE, or gives a 2x2 vs only an effect+CI, is recorded as target-result status at
> extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: two deterministic title-word query blocks covering VITAL, ASCEND, REDUCE-IT,
  STRENGTH, Alpha Omega, ORIGIN, Risk and Prevention, GISSI-HF, and related omega-3
  cardiovascular trial records.
- ClinicalTrials.gov: condition "cardiovascular disease", intervention "omega-3 fatty acids".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study
only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1
(<1e-6).

## Comparator (resolved; open-access confirmed)
Li et al., *Medicine (Baltimore)* 2022, "Effects of omega-3 fatty acid on major
cardiovascular outcomes: A systematic review and meta-analysis" (PMID 35905212, PMCID
PMC9333496, DOI 10.1097/MD.0000000000029556; Unpaywall is_oa=true). It reports major
cardiovascular events RR 0.94 (95% CI 0.89-1.00) over 28 randomized controlled trials.
No comparator harm effect is declared because the fetched comparator abstract/PMC text
does not expose atrial-fibrillation or bleeding effects.

## Controls
- **Positive** - the search must recover and include landmark double-blind omega-3 trials:
  REDUCE-IT (PMID 30415628), STRENGTH (PMID 33190147), and ORIGIN omega-3 (PMID 22686415).
- **Negative** - Grenyer et al. fish oil for major depression (PMID 17659823; a different
  disease area) must be recovered and EXCLUDED as wrong population.
