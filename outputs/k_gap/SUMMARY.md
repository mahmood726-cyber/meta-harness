# K-GAP summary (2026-09-28, AACT snapshot 2026-08-30)

1. Topics with a comparator meta: **32**; lines 3-7 count the 24 whose set is CONFIRMED. Comparator trial set enumerated from: citing JATS table 20, gated model proposal 4, open reference-list seed (candidate superset) 7, not enumerable from open sources 1.
2. Held comparator text is a DIFFERENT article than the cited comparator: **2 of 32** (corticosteroids-cap-mortality, doac-vte-recurrence).
3. Comparator units read: 321; resolved, drug-specific trial families: **237** (excluded: 17 other-agent units, 67 unresolved labels; 89 kept with agent unconfirmed).
4. Of those 237: pooled by us **48**, missing **189**.
5. Missing by class: identification 71, screen_or_eligibility 55, acquisition 18, extraction_from_table 13, measure_mismatch 7, scope_mismatch 11, genuinely_unavailable_open 14 (of 189).
6. Missing and not a deliberate measure refusal: 171. Open source that could supply a typed result: AACT_RESULTS 8 of 171, PMC_OA_FULLTEXT 24 of 171, UNPAYWALL_OA_COPY 61 of 171, PUBMED_ABSTRACT_OUTCOME 8 of 171, NONE_OPEN_PROBED 70 of 171.
7. AACT-closable by result type: COUNT_OF_PARTICIPANTS 2, other param types 6 (hazard ratios / rates / means need a measure-compatible estimand, not a 2x2).
7b. Reference-seed CANDIDATES (not confirmed members; 7 topics whose comparator set is not enumerable from an open table or quoted text): 50 RCT-typed, agent-named reports cited by the comparator; pooled by us 16, not pooled 34.
8. Largest gaps: probiotics-aad-prevention 29/36; metformin-pcos-ovulation 22/24; omega3-cardiovascular-events 19/23; melatonin-primary-insomnia-sol 18/19; colchicine-secondary-cv-prevention 13/15; ticagrelor-vs-clopidogrel-acs 13/15.
9. NOT probed yet (so absent from 'closable'): Drugs@FDA reviews, EMA EPARs, NICE committee papers, OA supplements. 'NONE_OPEN_PROBED' = no AACT posted result for the outcome, no PMC OA, no Unpaywall OA copy, and (for a trial not yet extracted) no abstract sentence naming the outcome with a number. PUBMED_ABSTRACT_OUTCOME is counted only for trials never yet extracted (identification / screened out).
10. Read with: the comparator set is the comparator's DRUG-SPECIFIC included studies (any outcome); a trial missing here may be outside our registered outcome/estimand, which a class of SCREEN_OR_ELIGIBILITY or MEASURE_MISMATCH records rather than hides.

## Proposal instrument vs deterministic table parse (drug-specific resolved counts)

| topic | table | proposal |
|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 5 | 4 |
| colchicine-postop-af | 8 | 8 |
| colchicine-recurrent-pericarditis | 0 | 1 |
| colchicine-secondary-cv-prevention | 15 | 15 |
| dapagliflozin-hfpef-hosp | 0 | 2 |
| empagliflozin-hfpef-hosp | 0 | 0 |
| esketamine-trd-madrs | 6 | 0 |
| finerenone-ckd-t2d-renal | 4 | 2 |
| glp1-ra-mace-t2d | 8 | 8 |
| iv-iron-hfref-hosp | 5 | 5 |
| melatonin-primary-insomnia-sol | 19 | 18 |
| metformin-pcos-ovulation | 0 | 24 |
| noac-vs-warfarin-af-stroke | 0 | 3 |
| omega3-cardiovascular-events | 23 | 23 |
| pcsk9-mace | 12 | 8 |
| probiotics-aad-prevention | 36 | 0 |
| sacubitril-valsartan-hfref | 9 | 9 |
| semaglutide-obesity-mace | 10 | 9 |
| semaglutide-obesity-weight | 3 | 3 |
| sglt2-hfref-hosp-cvdeath | 3 | 3 |
| sglt2-primary-prevention-hf | 8 | 8 |
| spironolactone-hfref-mortality | 3 | 4 |
| statins-primary-prevention-elderly | 12 | 12 |
| tranexamic-acid-pph | 5 | 4 |

Equal counts on 10 of 19 topics where the table resolved >=1 trial.

## Per topic

| topic | our k | comparator set | theirs (drug-specific) | pooled | missing | classes | closable by |
|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 2 | TABLE_ENUMERATED | 5 | 0 | 5 | GENUINELY_UNAVAILABLE_OPEN 2, MEASURE_MISMATCH 3 | NONE_OPEN_PROBED 2 |
| colchicine-postop-af | 3 | TABLE_ENUMERATED | 8 | 2 | 6 | SCREEN_OR_ELIGIBILITY 6 | AACT_RESULTS 1, NONE_OPEN_PROBED 1, PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 3 |
| colchicine-recurrent-pericarditis | 2 | PROPOSAL_ENUMERATED_GATED | 1 | 1 | 0 |  |  |
| colchicine-secondary-cv-prevention | 3 | TABLE_ENUMERATED | 15 | 2 | 13 | ACQUISITION 6, EXTRACTION_FROM_TABLE 2, SCREEN_OR_ELIGIBILITY 5 | PMC_OA_FULLTEXT 3, PUBMED_ABSTRACT_OUTCOME 2, UNPAYWALL_OA_COPY 8 |
| corticosteroids-cap-mortality | 2 | REFERENCE_SEED_CANDIDATES | 11 | 2 | 9 | GENUINELY_UNAVAILABLE_OPEN 4, IDENTIFICATION 3, MEASURE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 1 | NONE_OPEN_PROBED 6, PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 1 |
| corticosteroids-covid19-mortality | 1 | REFERENCE_SEED_CANDIDATES | 5 | 1 | 4 | ACQUISITION 4 | PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 3 |
| dapagliflozin-hfpef-hosp | None | PROPOSAL_ENUMERATED_GATED | 2 | 0 | 2 | EXTRACTION_FROM_TABLE 1, IDENTIFICATION 1 | PMC_OA_FULLTEXT 2 |
| denosumab-vertebral-fracture | 1 | NOT_ENUMERABLE_OPEN | 0 | 0 | 0 |  |  |
| doac-vte-recurrence | 6 | REFERENCE_SEED_CANDIDATES | 7 | 6 | 1 | IDENTIFICATION 1 | UNPAYWALL_OA_COPY 1 |
| dpp4-mace-t2d | 3 | REFERENCE_SEED_CANDIDATES | 5 | 3 | 2 | ACQUISITION 1, MEASURE_MISMATCH 1 | AACT_RESULTS 1 |
| empagliflozin-hfpef-hosp | None | REFERENCE_SEED_CANDIDATES | 3 | 0 | 3 | EXTRACTION_FROM_TABLE 1, SCOPE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 1 | UNPAYWALL_OA_COPY 2 |
| esketamine-trd-madrs | 3 | TABLE_ENUMERATED | 6 | 2 | 4 | EXTRACTION_FROM_TABLE 1, SCOPE_MISMATCH 2, SCREEN_OR_ELIGIBILITY 1 | AACT_RESULTS 1, UNPAYWALL_OA_COPY 1 |
| finerenone-ckd-t2d-renal | 2 | TABLE_ENUMERATED | 4 | 2 | 2 | ACQUISITION 1, IDENTIFICATION 1 | AACT_RESULTS 1, UNPAYWALL_OA_COPY 1 |
| glp1-ra-mace-t2d | 8 | TABLE_ENUMERATED | 8 | 7 | 1 | ACQUISITION 1 | AACT_RESULTS 1 |
| iv-iron-hfref-hosp | 2 | TABLE_ENUMERATED | 5 | 1 | 4 | ACQUISITION 2, EXTRACTION_FROM_TABLE 1, MEASURE_MISMATCH 1 | NONE_OPEN_PROBED 1, PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 1 |
| melatonin-primary-insomnia-sol | 1 | TABLE_ENUMERATED | 19 | 1 | 18 | GENUINELY_UNAVAILABLE_OPEN 4, IDENTIFICATION 14 | NONE_OPEN_PROBED 17, PMC_OA_FULLTEXT 1 |
| metformin-pcos-ovulation | 3 | PROPOSAL_ENUMERATED_GATED | 24 | 2 | 22 | ACQUISITION 1, GENUINELY_UNAVAILABLE_OPEN 2, IDENTIFICATION 15, SCOPE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 3 | NONE_OPEN_PROBED 7, PMC_OA_FULLTEXT 2, PUBMED_ABSTRACT_OUTCOME 4, UNPAYWALL_OA_COPY 8 |
| noac-vs-warfarin-af-stroke | 4 | PROPOSAL_ENUMERATED_GATED | 3 | 3 | 0 |  |  |
| omega3-cardiovascular-events | 5 | TABLE_ENUMERATED | 23 | 4 | 19 | ACQUISITION 2, GENUINELY_UNAVAILABLE_OPEN 1, IDENTIFICATION 7, SCREEN_OR_ELIGIBILITY 9 | NONE_OPEN_PROBED 7, PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 11 |
| pcsk9-mace | 2 | TABLE_ENUMERATED | 12 | 2 | 10 | GENUINELY_UNAVAILABLE_OPEN 1, IDENTIFICATION 6, MEASURE_MISMATCH 2, SCOPE_MISMATCH 1 | NONE_OPEN_PROBED 3, PMC_OA_FULLTEXT 4 |
| probiotics-aad-prevention | 11 | TABLE_ENUMERATED | 36 | 7 | 29 | ACQUISITION 4, EXTRACTION_FROM_TABLE 8, GENUINELY_UNAVAILABLE_OPEN 4, MEASURE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 12 | AACT_RESULTS 1, NONE_OPEN_PROBED 15, PMC_OA_FULLTEXT 3, PUBMED_ABSTRACT_OUTCOME 1, UNPAYWALL_OA_COPY 8 |
| sacubitril-valsartan-hfref | 2 | TABLE_ENUMERATED | 9 | 1 | 8 | SCOPE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 7 | NONE_OPEN_PROBED 4, UNPAYWALL_OA_COPY 3 |
| semaglutide-obesity-mace | 1 | TABLE_ENUMERATED | 10 | 2 | 8 | IDENTIFICATION 8 | NONE_OPEN_PROBED 4, PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 3 |
| semaglutide-obesity-weight | 2 | TABLE_ENUMERATED | 3 | 2 | 1 | IDENTIFICATION 1 | AACT_RESULTS 1 |
| sglt2-ckd-progression | 3 | REFERENCE_SEED_CANDIDATES | 12 | 3 | 9 | IDENTIFICATION 8, SCREEN_OR_ELIGIBILITY 1 | AACT_RESULTS 4, NONE_OPEN_PROBED 1, UNPAYWALL_OA_COPY 4 |
| sglt2-hfref-hosp-cvdeath | 2 | TABLE_ENUMERATED | 3 | 2 | 1 | IDENTIFICATION 1 | PMC_OA_FULLTEXT 1 |
| sglt2-primary-prevention-hf | 4 | TABLE_ENUMERATED | 8 | 3 | 5 | IDENTIFICATION 4, SCREEN_OR_ELIGIBILITY 1 | AACT_RESULTS 1, NONE_OPEN_PROBED 1, PMC_OA_FULLTEXT 1, UNPAYWALL_OA_COPY 2 |
| spironolactone-hfref-mortality | 3 | TABLE_ENUMERATED | 3 | 1 | 2 | IDENTIFICATION 1, SCOPE_MISMATCH 1 | AACT_RESULTS 1 |
| statins-primary-prevention-elderly | 2 | TABLE_ENUMERATED | 12 | 0 | 12 | IDENTIFICATION 12 | NONE_OPEN_PROBED 3, PMC_OA_FULLTEXT 3, PUBMED_ABSTRACT_OUTCOME 1, UNPAYWALL_OA_COPY 5 |
| ticagrelor-vs-clopidogrel-acs | 2 | TABLE_ENUMERATED | 15 | 2 | 13 | ACQUISITION 1, SCOPE_MISMATCH 5, SCREEN_OR_ELIGIBILITY 7 | NONE_OPEN_PROBED 4, UNPAYWALL_OA_COPY 4 |
| tocilizumab-covid19-mortality | 1 | REFERENCE_SEED_CANDIDATES | 7 | 1 | 6 | ACQUISITION 5, IDENTIFICATION 1 | PMC_OA_FULLTEXT 4, UNPAYWALL_OA_COPY 2 |
| tranexamic-acid-pph | 1 | TABLE_ENUMERATED | 5 | 1 | 4 | SCREEN_OR_ELIGIBILITY 4 | NONE_OPEN_PROBED 1, UNPAYWALL_OA_COPY 3 |
