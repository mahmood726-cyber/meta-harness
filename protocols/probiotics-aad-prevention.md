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

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found prevention
scope and no-probiotic-control wording that were not executable enough. The config
now excludes protocol-only reports before RCT publication-type acceptance, excludes
treatment/therapeutic-efficacy records rather than AAD prevention records, and
accepts explicit "not receive" no-probiotic controls for yogurt/probiotic
prevention trials. This amendment changes screening only.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 34385227) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 29868585, 24348885; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 36 of 41 of the comparator's eligible trials; with this route and the full retrieval below, 36 of 41 (36 of 41 without the comparator's own reference list, which contains its trials by construction). The route retrieves 244 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "antibiotic-associated diarrhea", "intr": "probiotic"} is unchanged. It returns 53 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query: not adopted** (KEEP_CURRENT: volume 9373 > cap 5000; recorded call mc-0d7e34731554c42fc839333fdbd37c55.json).
