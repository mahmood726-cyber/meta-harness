# Protocol - probiotics for prevention of antibiotic-associated diarrhoea

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page. Committed before the synthesis runs. Same machinery as the colchicine
template topics.

## PICO
- **P** - patients receiving antibiotics, with the AAD-prevention population identified
  from title-level terms or registry conditions.
- **I** - probiotics, including named probiotic genera, strains, fermented probiotic
  products, probiotic yogurt/yoghurt, kefir, or synbiotics.
- **C** - placebo, no probiotic, usual care, standard care, or no-treatment control.
- **O (primary)** - antibiotic-associated diarrhoea/diarrhea (AAD).
- **O (harms)** - any adverse events; serious adverse events.

## Estimand / population / timepoint
- RR of AAD, intention-to-treat as randomised, at study end.

## Eligibility - P/I/C/DESIGN only
- **I1** RCT;
- **I2** AAD-prevention population, judged from title/registry-condition terms rather
  than incidental abstract mentions;
- **I3** probiotic vs placebo/no-probiotic/usual-care/no-treatment control;
- **design** placebo-controlled or no-probiotic controlled RCT. Double-blind status is
  not required for this topic.

Exclude (reason must be true of the record):
- **X1** not RCT (review, guideline, observational, protocol-only);
- **X2** wrong population (animal/in-vitro/mechanistic model; acute/nosocomial diarrhea
  not framed as antibiotic-associated; post hoc subgroup or secondary-analysis record);
- **X3** wrong intervention/comparison (no probiotic-vs-control contrast, active
  probiotic comparator only, or no eligible placebo/no-probiotic/usual-care control);
- **X5** off-topic: a primary trial of another topic/disease in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an included trial reports AAD in the
abstract, reports counts, or reports only a published effect with CI is target-result
status at extraction, not an exclusion.

## Search
- PubMed: high-retmax probiotic x antibiotic-associated diarrhoea/diarrhea x RCT/placebo
  queries, with strain/product expansions for Lactobacillus, Saccharomyces,
  Bifidobacterium, Bacillus, kefir, yogurt/yoghurt, BIO-K/CL1285, and synbiotics.
- ClinicalTrials.gov: condition "antibiotic-associated diarrhea", intervention
  "probiotic".
- Comparator-reference seeding is left enabled for recall; screening remains offline and
  config driven.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1}
(floor max(1,Q/(k-1))); PI mu +/- t_{k-1}*sqrt(tau^2+se^2). DerSimonian-Laird forbidden.
metafor-validated by the fixed harness.

## Comparator (resolved; OA confirmed)
Goodman et al., *BMJ Open* 2021, "Probiotics for the prevention of
antibiotic-associated diarrhoea: a systematic review and meta-analysis" (PMID 34385227,
PMCID PMC8362734, DOI 10.1136/bmjopen-2020-043054; Unpaywall is_oa=true). It reports
AAD RR 0.63 (95% CI 0.54 to 0.73) across 42 studies in adults and states that 32 of the
42 studies reported adverse events, with no serious adverse events reported.

## Controls
- **Positive** - PLACIDE (PMID 23932219), the multicentre adult hospital RCT by
  Ouwehand et al. (PMID 32035998), and the pediatric Saccharomyces boulardii RCT
  (PMID 15740542) must be recovered and included.
- **Negative** - the randomized synbiotic yogurt child-health trial (PMID 25841539) must
  be recovered and EXCLUDED because its title/conditions are not the antibiotic-associated
  diarrhoea population.
