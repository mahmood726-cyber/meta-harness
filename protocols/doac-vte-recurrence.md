# Protocol - direct oral anticoagulants for recurrent VTE in acute symptomatic venous thromboembolism

**Registration.** This topic is preregistered in `PREREGISTRATION_v2.md` before
search, screening, extraction, or synthesis. The per-topic protocol records the
same P/I/C/design-only eligibility and is committed with the generated review
artifacts. Outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with acute symptomatic venous thromboembolism (deep-vein
  thrombosis and/or pulmonary embolism).
- **I** - direct oral anticoagulants: dabigatran, rivaroxaban, apixaban, or
  edoxaban.
- **C** - warfarin or another vitamin-K antagonist strategy, including initial
  parenteral anticoagulation followed by VKA.
- **O (primary)** - trial-reported recurrent VTE. RE-COVER, RE-COVER II, and
  AMPLIFY include VTE-related death in the primary recurrent-VTE composite; the
  EINSTEIN and Hokusai acute-treatment reports count recurrent VTE as reported.

## Estimand / population / timepoint
- **Estimand** - trial-reported ratio-scale effect for DOAC vs VKA, pooled on the
  log-ratio scale. Five pivotal trials report HRs and AMPLIFY reports an RR; this
  mixed HR/RR pool is declared because recurrent-event rates are low but the
  estimand labels are not identical.
- **Population** - intention-to-treat as randomised / full analysis set, as
  reported by each pivotal acute-treatment trial.
- **Timepoint** - trial end / longest randomized acute-treatment follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with acute symptomatic VTE, DVT, and/or PE;
- **I3** - dabigatran, rivaroxaban, apixaban, edoxaban, or a DOAC/NOAC as the
  randomised intervention;
- **I4** - warfarin / VKA / conventional anticoagulant therapy comparator;
- **design** - randomised DOAC-vs-VKA allocation; double-blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population, including cancer-only, thrombophilia-only,
  antiphospholipid-only, cerebral-vein thrombosis, postoperative prophylaxis,
  pediatric, or extended/secondary-prevention populations;
- **X3** - wrong intervention/comparison, including placebo, aspirin, no-treatment,
  enoxaparin-only prophylaxis, or active comparators other than VKA/warfarin;
- **X5** - off-topic: a primary trial of another topic in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an eligible acute-treatment trial
reports recurrent VTE, and whether it reports arm counts or only an effect plus
confidence interval, is recorded at extraction. A published HR/RR plus 95% CI is
a poolable input.

## Search
- PubMed: direct UID queries for RE-COVER, RE-COVER II, EINSTEIN-DVT,
  EINSTEIN-PE, AMPLIFY, and Hokusai-VTE primary acute-treatment reports.
- ClinicalTrials.gov: condition "venous thromboembolism", intervention "direct
  oral anticoagulant".
- Comparator-reference seeding is disabled; the six pivotal PubMed records are
  specified directly so the embedded EINSTEIN placebo-extension substudy cannot
  enlarge the DOAC-vs-VKA evidence set.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Published HR and
RR inputs are pooled on the log ratio scale and the mixed effect-label is shown.

## Comparator (resolved; OA confirmed by build gate)
van Es et al., *Blood* 2014, "Direct oral anticoagulants compared with vitamin K
antagonists for acute venous thromboembolism: evidence from phase 3 trials"
(PMID 24963045, DOI 10.1182/blood-2014-04-571232). This is a scope-matched
open-access pooled analysis of the six phase-3 acute symptomatic VTE DOAC-vs-VKA
trials and reports recurrent VTE, including VTE-related death, as RR 0.90 (95%
CI 0.77-1.06). van der Hulle et al. 2014 (PMID 24330006) was checked first as
the canonical JTH systematic review/meta-analysis, but Unpaywall reported it
closed access during the build, so it was not used as the comparator.

## Pivotal
- **RE-COVER** - PMID 19966341; NCT00291330; dabigatran; HR 1.10 (0.65-1.84).
- **RE-COVER II** - PMID 24344086; NCT00680186; dabigatran; HR 1.08 (0.64-1.80).
- **EINSTEIN-DVT** - PMID 21128814; NCT00440193; rivaroxaban; HR 0.68
  (0.44-1.04) for the acute DVT VKA comparison.
- **EINSTEIN-PE** - PMID 22449293; NCT00439777; rivaroxaban; HR 1.12
  (0.75-1.68).
- **AMPLIFY** - PMID 23808982; NCT00643201; apixaban; RR 0.84 (0.60-1.18).
- **Hokusai-VTE** - PMID 23991658; NCT00986154; edoxaban; HR 0.89 (0.70-1.13).

## Controls
- **Positive** - the search must recover and include RE-COVER (PMID 19966341),
  RE-COVER II (PMID 24344086), EINSTEIN-DVT (PMID 21128814), EINSTEIN-PE
  (PMID 22449293), AMPLIFY (PMID 23808982), and Hokusai-VTE (PMID 23991658).
- **Negative** - AMPLIFY-EXT (PMID 23216615), apixaban vs placebo for extended
  treatment after completion of anticoagulation, must be recovered and EXCLUDED
  as wrong comparator / wrong phase of therapy.

## Estimand exclusions
- **EINSTEIN-Extension** - the continued-treatment substudy embedded in PMID
  21128814 (NCT00439725) reports rivaroxaban vs placebo, 8/602 vs 42/594, HR
  0.18 (0.09-0.39). It is excluded from the DOAC-vs-VKA pool because the
  comparator is placebo and the phase is extended/secondary prevention, not
  acute VTE treatment.
