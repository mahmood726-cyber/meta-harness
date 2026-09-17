# Protocol - direct oral anticoagulants versus warfarin for stroke prevention in atrial fibrillation

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page's Protocol tab and Reproducibility tab. The protocol is committed before
the synthesis is run.

## PICO
- **P** - adults with non-valvular atrial fibrillation treated for stroke prevention.
- **I** - a direct oral anticoagulant: dabigatran, rivaroxaban, apixaban, or edoxaban.
- **C** - warfarin or other vitamin K antagonist anticoagulation.
- **O (primary)** - stroke or systemic embolism.
- **O (harms)** - major bleeding.

## Estimand / population / timepoint
- **Estimand** - ratio-scale effect, labelled HR when trials report hazard ratios and RR
  when the trial abstract reports a relative risk.
- **Population** - intention-to-treat as randomised where the trial abstract reports it.
- **Timepoint** - trial end / longest reported follow-up in the pivotal trial abstract.

## Amendment 2026-09-12 (POST-HOC — dose/analysis selection rule, added after trial data were known)
**Status: retrospective.** This rule was NOT in the protocol at the original registration SHA; it
is recorded here as a dated amendment so the analysis is labelled post-amendment, not presented as
prespecified. It formalises what the pooled analysis already does and aligns with the registered
comparator, which is the **standard-dose** DOAC-vs-warfarin comparison (Carnicelli 2022, standard-dose
HR 0.81).
- **Dose rule.** For a multi-dose trial, pool the **approved/marketed higher dose** vs warfarin, not
  the lower dose: dabigatran **150 mg** (RE-LY, not the 110 mg arm), edoxaban **60 mg** high-dose
  (ENGAGE AF-TIMI 48, not the 30 mg arm). Rationale: the higher dose is the licensed stroke-prevention
  regimen and matches the standard-dose comparator.
- **Analysis-set rule.** Use the **intention-to-treat** estimate to match the ITT basis of ROCKET-AF
  and ARISTOTLE in the pool (ENGAGE high-dose ITT HR 0.87, not the on-treatment 0.79).
- **Confidence-level rule.** Where a trial reports a non-95% CI (ENGAGE 97.5%), recover the log-scale
  SE at the **stated** level before pooling; the conversion is disclosed on the row.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is atrial fibrillation, judged from title or registry conditions;
- **I3** - direct oral anticoagulant versus warfarin / vitamin K antagonist comparator;
- **design** - randomised DOAC-vs-warfarin allocation; double-blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. mechanical heart valves, venous thromboembolism,
  antiphospholipid syndrome, catheter ablation, cardioversion, device-procedure studies);
- **X3** - wrong intervention/comparison (no direct oral anticoagulant versus
  warfarin / vitamin K antagonist contrast);
- **X5** - off-topic: a primary trial of another disease/topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports stroke or systemic
> embolism, or gives a 2x2 table versus only an effect+CI, is recorded as target-result
> status at extraction - never as an exclusion. A published effect + CI is a poolable
> input when the fixed extractor can corroborate it from the abstract.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: UID searches for the four pivotal direct DOAC-vs-warfarin AF RCTs: RE-LY,
  ROCKET AF, ARISTOTLE, and ENGAGE AF-TIMI 48.
- ClinicalTrials.gov: condition "atrial fibrillation", intervention "edoxaban warfarin".
- Comparator-reference seeding is disabled because the resolved 2022 IPD/NMA cites later
  subgroup publications that share NCT IDs with the pivotal trials; the UID searches
  intentionally preserve the primary trial abstracts as the extraction source.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log ratio effects; **Paule-Mandel** tau^2; **HKSJ**
95% CI on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a
study only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6).

This topic is network-shaped in the literature, but this harness synthesis is explicitly
the direct pairwise DOAC-vs-warfarin comparison. No indirect treatment comparison or
network estimate is calculated by the harness.

## Comparator (resolved; open-access confirmed)
Carnicelli et al., *Circulation* 2022, "Direct Oral Anticoagulants Versus Warfarin in
Patients With Atrial Fibrillation: Patient-Level Network Meta-Analyses of Randomized
Clinical Trials With Interaction Testing by Age and Sex" (PMID 34985309, PMCID
PMC8800560, DOI 10.1161/CIRCULATIONAHA.121.056355; Unpaywall is_oa=true). It reports
standard-dose DOAC versus warfarin for stroke or systemic embolism as HR 0.81
(95% CI 0.74-0.89), and reports major bleeding.

Ruff et al. 2014 in *Lancet* was checked because it is the classic direct trial-level
meta-analysis (PMID 24315724, DOI 10.1016/S0140-6736(13)62343-0), but Unpaywall reported
is_oa=false, so it was not used as the comparator.

## Controls
- **Positive** - the search must recover and include RE-LY (PMID 19717844), ROCKET AF
  (PMID 21830957), and ARISTOTLE (PMID 21870978).
- **Negative** - RE-ALIGN, dabigatran versus warfarin in mechanical heart valves
  (PMID 23991661), must be recovered and excluded as the wrong population.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found two protocol
phrases that the executable config did not enforce. The perioperative exclusion is
made executable for cardiac surgery / cardiac surgical populations, and ORGANON
NCT02935855 is source-backed as non-randomized because the cached registry record
describes consecutive patients already receiving anticoagulants, not a randomized
DOAC-vs-warfarin allocation. This amendment changes screening only; it does not
change extraction or pooling.
