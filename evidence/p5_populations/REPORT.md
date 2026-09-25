# The 53 P5-unestablished pooled rows -- population evidence under POLICY.md

Kinds of item: 53 served pooled primary rows (the frozen `evidence/inputs/the53.json`), each carrying the facts of its ordered P5 blocker chain (165 facts). No controls, no split rows. No row is omitted; a row whose facts are UNRESOLVED stays in the population with its served value.

## Rows (of 53)

- ALL_RECOVERED: **38 of 53**
- ESTABLISHED_ABSENT: **3 of 53**
- UNRESOLVED: **12 of 53**

## Facts (of 165)

- ESTABLISHED_ABSENT: 3
- RECOVERED: 147
- UNRESOLVED: 15

By fact:

- `entry_population`: ESTABLISHED_ABSENT 1, RECOVERED 34, UNRESOLVED 1
- `randomized_contrast`: RECOVERED 43, UNRESOLVED 1
- `registry_parent`: RECOVERED 4, UNRESOLVED 12
- `design`: RECOVERED 20, UNRESOLVED 1
- `arms`: RECOVERED 20
- `masking`: RECOVERED 6
- `placebo_control`: ESTABLISHED_ABSENT 2, RECOVERED 20

## The predecessor's citations, re-checked

All 385 EV53 citations re-located by evid2 at checkout `66087f30`: EMPTY_SPAN 1, REVERIFIED_EXACT 384. The one EMPTY_SPAN was labelled a pass by EV53 (an empty string is trivially found); no fact cites it.

## Every fact that is not RECOVERED

| row | trial | fact | state | why |
|---|---|---|---|---|
| P53-05 | PMID 32678530 (corticosteroids-covid19-mortality) | placebo_control | ESTABLISHED_ABSENT | a span of the same trial states the opposite of what the screen requires |
| P53-19 | PMID 19522426 (metformin-pcos-ovulation) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-21 | PMID 11172832 (metformin-pcos-ovulation) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-32 | PMID 32035998 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-32 | PMID 32035998 (probiotics-aad-prevention) | entry_population | UNRESOLVED | Missing element: receipt of antibiotics as an ENTRY criterion. The article's own abstract states the entry population as 'patients aged over 55 years'; antibiotic exposure appears only in the outcome's name, which POLICY.md does not accept as evidence of entry. No open-access full text; two same-tri |
| P53-33 | PMID 24772726 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-35 | PMID 18701826 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-36 | PMID 18410562 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-37 | PMID 15740542 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-38 | PMID 11560298 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-39 | PMID 7872284 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reverse lookup) r |
| P53-39 | PMID 7872284 (probiotics-aad-prevention) | design | UNRESOLVED | Missing element: RANDOM allocation stated by the trial. The article's own abstract says 'A double-blinded, placebo-controlled, parallel group study was performed' and never states randomisation; the only 'randomized' is PubMed's publication-type label, an indexer's classification (POLICY.md: not a t |
| P53-39 | PMID 7872284 (probiotics-aad-prevention) | randomized_contrast | UNRESOLVED | Missing element: RANDOM allocation stated by the trial. The article's own abstract says 'A double-blinded, placebo-controlled, parallel group study was performed' and never states randomisation; the only 'randomized' is PubMed's publication-type label, an indexer's classification (POLICY.md: not a t |
| P53-40 | PMID 21165295 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in the open-access full text scanned (34465 characters); stopping rule of POLICY.md reached. Amendment A (2026-09-25): step 4 (two fixed Europe PMC queries) and 2b (ClinicalTrials.gov ReferencePMID reve |
| P53-41 | PMID 18026577 (probiotics-aad-prevention) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. PMC2658588 exists but its PMC efetch returned front matter only (4,327 characters, no <body>); Europe PMC fullTextXML retu |
| P53-48 | PMID 10471456 (spironolactone-hfref-mortality) | registry_parent | UNRESOLVED | No registration identifier in the article's own abstract (Europe PMC), in PubMed DataBankList, or in any full text (none served open access); stopping rule of POLICY.md reached. RALES (1999) was reported before trial registration was customary; no identifier appears in any source searched. Amendment |
| P53-50 | PMID 20404379 (statins-primary-prevention-elderly) | entry_population | ESTABLISHED_ABSENT | a span of the same trial states the opposite of what the screen requires |
| P53-53 | PMID 33933206 (tocilizumab-covid19-mortality) | placebo_control | ESTABLISHED_ABSENT | a span of the same trial states the opposite of what the screen requires |

## Recovered, with a note a reader must see

- P53-05 PMID 32678530 `entry_population`: evid lane entry ruling: PARTLY
- P53-31 PMID 35727573 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-33 PMID 24772726 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-34 PMID 23932219 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-35 PMID 18701826 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-36 PMID 18410562 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-37 PMID 15740542 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-38 PMID 11560298 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-39 PMID 7872284 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-40 PMID 21165295 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-41 PMID 18026577 `entry_population`: CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)
- P53-48 PMID 10471456 `entry_population`: evid lane entry ruling: PARTLY

## HARMONY

P53-17 (glp1-ra-mace-t2d, family NCT02465515): P5 blocker `ENTRY_POPULATION_NOT_ESTABLISHED`, row state **ALL_RECOVERED**. `entry_population` RECOVERED: "We did a double-blind, randomised, placebo-controlled trial in 610 sites across 28 countries. We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease (at a 1:1 ratio) to grou"

## What this is not

- RECOVERED is evidence for Mahmood's decision D04. It admits no row; no admission route was created or used.
- The P5 screen reads registry conditions; a fact recovered from a report does not turn the screen green, and the probiotics rows additionally carry a config defect (the configured population terms name the outcome).
- UNRESOLVED means the stopping rule of POLICY.md was reached without a span -- not that the fact is false.
