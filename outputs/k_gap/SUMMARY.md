# K-GAP summary (2026-09-28, AACT snapshot 2026-08-30)

1. Topics with a comparator meta: **32**; lines 3-7 count the 24 whose set is CONFIRMED. Comparator trial set enumerated from: citing JATS table 20, gated model proposal 4, open reference-list seed (candidate superset) 7, not enumerable from open sources 1.
2. Held comparator text is a DIFFERENT article than the cited comparator: **2 of 32** (corticosteroids-cap-mortality, doac-vte-recurrence).
3. Comparator units read: 321; resolved, drug-specific trial families: **239** (excluded: 16 other-agent units, 66 unresolved labels; 85 kept with agent unconfirmed).
4. Of those 239: pooled by us **53**, missing **186**.
5. Missing by class: identification 71, screen_or_eligibility 50, acquisition 7, extraction_from_table 14, measure_mismatch 7, scope_mismatch 11, genuinely_unavailable_open 26 (of 186).
6. Missing and not a deliberate measure refusal: 168. Open source that could supply a typed result: AACT_RESULTS 7 of 168, PMC_OA_FULLTEXT 35 of 168, NONE_OPEN_PROBED 126 of 168.
7. AACT-closable by result type: COUNT_OF_PARTICIPANTS 2, other param types 5 (hazard ratios / rates / means need a measure-compatible estimand, not a 2x2).
7b. Reference-seed CANDIDATES (not confirmed members; 7 topics whose comparator set is not enumerable from an open table or quoted text): 50 RCT-typed, agent-named reports cited by the comparator; pooled by us 21, not pooled 29.
8. Largest gaps: probiotics-aad-prevention 29/36; omega3-cardiovascular-events 25/28; metformin-pcos-ovulation 21/23; melatonin-primary-insomnia-sol 18/19; statins-primary-prevention-elderly 12/12; colchicine-secondary-cv-prevention 11/15.
9. NOT probed yet (so absent from 'closable'): Drugs@FDA reviews, EMA EPARs, NICE committee papers, Unpaywall non-PMC OA copies, OA supplements. 'NONE_OPEN_PROBED' means none of AACT posted results / PMC OA held it.
10. Read with: the comparator set is the comparator's DRUG-SPECIFIC included studies (any outcome); a trial missing here may be outside our registered outcome/estimand, which a class of SCREEN_OR_ELIGIBILITY or MEASURE_MISMATCH records rather than hides.

## Proposal instrument vs deterministic table parse (drug-specific resolved counts)

| topic | table | proposal |
|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 4 | 4 |
| colchicine-postop-af | 8 | 8 |
| colchicine-recurrent-pericarditis | 0 | 1 |
| colchicine-secondary-cv-prevention | 15 | 15 |
| dapagliflozin-hfpef-hosp | 0 | 2 |
| empagliflozin-hfpef-hosp | 0 | 0 |
| esketamine-trd-madrs | 6 | 0 |
| finerenone-ckd-t2d-renal | 4 | 2 |
| glp1-ra-mace-t2d | 7 | 7 |
| iv-iron-hfref-hosp | 5 | 5 |
| melatonin-primary-insomnia-sol | 19 | 18 |
| metformin-pcos-ovulation | 0 | 23 |
| noac-vs-warfarin-af-stroke | 0 | 3 |
| omega3-cardiovascular-events | 28 | 22 |
| pcsk9-mace | 12 | 8 |
| probiotics-aad-prevention | 36 | 0 |
| sacubitril-valsartan-hfref | 10 | 5 |
| semaglutide-obesity-mace | 11 | 9 |
| semaglutide-obesity-weight | 3 | 3 |
| sglt2-hfref-hosp-cvdeath | 1 | 1 |
| sglt2-primary-prevention-hf | 8 | 8 |
| spironolactone-hfref-mortality | 3 | 4 |
| statins-primary-prevention-elderly | 12 | 12 |
| tranexamic-acid-pph | 5 | 4 |

Equal counts on 9 of 19 topics where the table resolved >=1 trial.

## Per topic

| topic | our k | comparator set | theirs (drug-specific) | pooled | missing | classes | closable by |
|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 2 | TABLE_ENUMERATED | 4 | 0 | 4 | GENUINELY_UNAVAILABLE_OPEN 2, MEASURE_MISMATCH 2 | NONE_OPEN_PROBED 2 |
| colchicine-postop-af | 3 | TABLE_ENUMERATED | 8 | 4 | 4 | ACQUISITION 1, SCREEN_OR_ELIGIBILITY 3 | AACT_RESULTS 1, NONE_OPEN_PROBED 1, PMC_OA_FULLTEXT 2 |
| colchicine-recurrent-pericarditis | 2 | PROPOSAL_ENUMERATED_GATED | 1 | 1 | 0 |  |  |
| colchicine-secondary-cv-prevention | 3 | TABLE_ENUMERATED | 15 | 4 | 11 | EXTRACTION_FROM_TABLE 2, GENUINELY_UNAVAILABLE_OPEN 4, SCREEN_OR_ELIGIBILITY 5 | NONE_OPEN_PROBED 9, PMC_OA_FULLTEXT 2 |
| corticosteroids-cap-mortality | 2 | REFERENCE_SEED_CANDIDATES | 11 | 2 | 9 | ACQUISITION 2, GENUINELY_UNAVAILABLE_OPEN 2, IDENTIFICATION 3, MEASURE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 1 | NONE_OPEN_PROBED 4, PMC_OA_FULLTEXT 4 |
| corticosteroids-covid19-mortality | 1 | REFERENCE_SEED_CANDIDATES | 5 | 1 | 4 | ACQUISITION 2, GENUINELY_UNAVAILABLE_OPEN 2 | NONE_OPEN_PROBED 2, PMC_OA_FULLTEXT 2 |
| dapagliflozin-hfpef-hosp | None | PROPOSAL_ENUMERATED_GATED | 2 | 0 | 2 | EXTRACTION_FROM_TABLE 1, IDENTIFICATION 1 | PMC_OA_FULLTEXT 2 |
| denosumab-vertebral-fracture | 1 | NOT_ENUMERABLE_OPEN | 0 | 0 | 0 |  |  |
| doac-vte-recurrence | 6 | REFERENCE_SEED_CANDIDATES | 7 | 7 | 0 |  |  |
| dpp4-mace-t2d | 3 | REFERENCE_SEED_CANDIDATES | 5 | 3 | 2 | ACQUISITION 1, MEASURE_MISMATCH 1 | AACT_RESULTS 1 |
| empagliflozin-hfpef-hosp | None | REFERENCE_SEED_CANDIDATES | 3 | 0 | 3 | EXTRACTION_FROM_TABLE 1, SCOPE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 1 | PMC_OA_FULLTEXT 2 |
| esketamine-trd-madrs | 3 | TABLE_ENUMERATED | 6 | 2 | 4 | EXTRACTION_FROM_TABLE 1, SCOPE_MISMATCH 2, SCREEN_OR_ELIGIBILITY 1 | AACT_RESULTS 1, NONE_OPEN_PROBED 1 |
| finerenone-ckd-t2d-renal | 2 | TABLE_ENUMERATED | 4 | 2 | 2 | ACQUISITION 1, IDENTIFICATION 1 | AACT_RESULTS 1, NONE_OPEN_PROBED 1 |
| glp1-ra-mace-t2d | 8 | TABLE_ENUMERATED | 7 | 6 | 1 | ACQUISITION 1 | AACT_RESULTS 1 |
| iv-iron-hfref-hosp | 2 | TABLE_ENUMERATED | 5 | 1 | 4 | ACQUISITION 2, EXTRACTION_FROM_TABLE 1, MEASURE_MISMATCH 1 | NONE_OPEN_PROBED 1, PMC_OA_FULLTEXT 2 |
| melatonin-primary-insomnia-sol | 1 | TABLE_ENUMERATED | 19 | 1 | 18 | GENUINELY_UNAVAILABLE_OPEN 4, IDENTIFICATION 14 | NONE_OPEN_PROBED 17, PMC_OA_FULLTEXT 1 |
| metformin-pcos-ovulation | 3 | PROPOSAL_ENUMERATED_GATED | 23 | 2 | 21 | GENUINELY_UNAVAILABLE_OPEN 3, IDENTIFICATION 15, SCOPE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 2 | NONE_OPEN_PROBED 18, PMC_OA_FULLTEXT 2 |
| noac-vs-warfarin-af-stroke | 4 | PROPOSAL_ENUMERATED_GATED | 3 | 3 | 0 |  |  |
| omega3-cardiovascular-events | 5 | TABLE_ENUMERATED | 28 | 3 | 25 | ACQUISITION 2, EXTRACTION_FROM_TABLE 1, GENUINELY_UNAVAILABLE_OPEN 3, IDENTIFICATION 8, MEASURE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 10 | NONE_OPEN_PROBED 19, PMC_OA_FULLTEXT 5 |
| pcsk9-mace | 2 | TABLE_ENUMERATED | 12 | 2 | 10 | GENUINELY_UNAVAILABLE_OPEN 1, IDENTIFICATION 6, MEASURE_MISMATCH 2, SCOPE_MISMATCH 1 | NONE_OPEN_PROBED 3, PMC_OA_FULLTEXT 4 |
| probiotics-aad-prevention | 11 | TABLE_ENUMERATED | 36 | 7 | 29 | EXTRACTION_FROM_TABLE 8, GENUINELY_UNAVAILABLE_OPEN 8, MEASURE_MISMATCH 1, SCREEN_OR_ELIGIBILITY 12 | AACT_RESULTS 1, NONE_OPEN_PROBED 24, PMC_OA_FULLTEXT 3 |
| sacubitril-valsartan-hfref | 2 | TABLE_ENUMERATED | 10 | 1 | 9 | SCOPE_MISMATCH 2, SCREEN_OR_ELIGIBILITY 7 | NONE_OPEN_PROBED 7 |
| semaglutide-obesity-mace | 1 | TABLE_ENUMERATED | 11 | 2 | 9 | IDENTIFICATION 9 | NONE_OPEN_PROBED 3, PMC_OA_FULLTEXT 6 |
| semaglutide-obesity-weight | 2 | TABLE_ENUMERATED | 3 | 2 | 1 | IDENTIFICATION 1 | AACT_RESULTS 1 |
| sglt2-ckd-progression | 3 | REFERENCE_SEED_CANDIDATES | 12 | 7 | 5 | IDENTIFICATION 3, SCREEN_OR_ELIGIBILITY 2 | AACT_RESULTS 2, NONE_OPEN_PROBED 1, PMC_OA_FULLTEXT 2 |
| sglt2-hfref-hosp-cvdeath | 2 | TABLE_ENUMERATED | 1 | 0 | 1 | IDENTIFICATION 1 | PMC_OA_FULLTEXT 1 |
| sglt2-primary-prevention-hf | 4 | TABLE_ENUMERATED | 8 | 6 | 2 | IDENTIFICATION 2 | NONE_OPEN_PROBED 2 |
| spironolactone-hfref-mortality | 3 | TABLE_ENUMERATED | 3 | 1 | 2 | IDENTIFICATION 1, SCOPE_MISMATCH 1 | AACT_RESULTS 1 |
| statins-primary-prevention-elderly | 2 | TABLE_ENUMERATED | 12 | 0 | 12 | IDENTIFICATION 12 | NONE_OPEN_PROBED 9, PMC_OA_FULLTEXT 3 |
| ticagrelor-vs-clopidogrel-acs | 2 | TABLE_ENUMERATED | 15 | 4 | 11 | GENUINELY_UNAVAILABLE_OPEN 1, SCOPE_MISMATCH 4, SCREEN_OR_ELIGIBILITY 6 | NONE_OPEN_PROBED 7 |
| tocilizumab-covid19-mortality | 1 | REFERENCE_SEED_CANDIDATES | 7 | 1 | 6 | ACQUISITION 5, IDENTIFICATION 1 | PMC_OA_FULLTEXT 6 |
| tranexamic-acid-pph | 1 | TABLE_ENUMERATED | 5 | 1 | 4 | SCREEN_OR_ELIGIBILITY 4 | NONE_OPEN_PROBED 2, PMC_OA_FULLTEXT 2 |
