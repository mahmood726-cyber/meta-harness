# Search + screen recall audit (G1, 32 topics)

Inputs: tracker outputs/k_gap/g1 (this branch), acq/k-gap pinned 8febcb3c1b. Kinds of comparator trial: {'ELIGIBLE': 235, 'SCREEN_NAMED': 83, 'NAMED_OTHER': 30}. Eligible-set mismatch vs tracker: none.

**Totals:** search recall 172 of 235; search or another meta's reference list 177 of 235; screen recall 141 of 172 (of eligible trials our search identified). Miss types: {'IDENTITY_FAILURE': 18, 'QUERY_GAP': 32, 'RETRIEVED_NOT_RETAINED': 12, 'DATABASE_NOT_SEARCHED': 1}.

**After the class fixes on this branch** (counterfactual, from the recorded probes): the standing REVIEW_REFERENCE_LIST route alone identifies 198 of 235; registered search + that route + uncapped retrieval identify 216 of 235. **Circular part stated:** the comparator's own reference list contains its trials by construction, so as a recall measure against that comparator it proves nothing; without the comparator's backward lists (other metas + forward citation only) the fixed identification is 193 of 235.

| Topic | Eligible | Search n/N | +other metas | RRL route | Fixed ident. | Screen n/N | Misses | Screen-named to recheck |
|---|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | - | 0 |
| colchicine-postop-af | 5 | 4/5 | 4/5 | 4/5 | 4/5 | 2/4 | IDENTITY_FAILURE 1 | 4 |
| colchicine-recurrent-pericarditis | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | - | 4 |
| colchicine-secondary-cv-prevention | 11 | 11/11 | 11/11 | 11/11 | 11/11 | 10/11 | - | 4 |
| corticosteroids-cap-mortality | 10 | 7/10 | 8/10 | 10/10 | 10/10 | 7/7 | QUERY_GAP 3 | 1 |
| corticosteroids-covid19-mortality | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | - | 0 |
| dapagliflozin-hfpef-hosp | 3 | 1/3 | 1/3 | 1/3 | 1/3 | 1/1 | IDENTITY_FAILURE 2 | 1 |
| denosumab-vertebral-fracture | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | - | 0 |
| doac-vte-recurrence | 6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | - | 1 |
| dpp4-mace-t2d | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | - | 0 |
| empagliflozin-hfpef-hosp | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | - | 1 |
| esketamine-trd-madrs | 5 | 4/5 | 4/5 | 5/5 | 5/5 | 2/4 | RETRIEVED_NOT_RETAINED 1 | 1 |
| finerenone-ckd-t2d-renal | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | - | 0 |
| glp1-ra-mace-t2d | 7 | 7/7 | 7/7 | 7/7 | 7/7 | 7/7 | - | 0 |
| iv-iron-hfref-hosp | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | - | 0 |
| melatonin-primary-insomnia-sol | 12 | 5/12 | 7/12 | 12/12 | 12/12 | 5/5 | QUERY_GAP 7 | 7 |
| metformin-pcos-ovulation | 33 | 12/33 | 12/33 | 26/33 | 26/33 | 6/12 | RETRIEVED_NOT_RETAINED 3, IDENTITY_FAILURE 7, QUERY_GAP 11 | 8 |
| noac-vs-warfarin-af-stroke | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | - | 0 |
| omega3-cardiovascular-events | 18 | 16/18 | 16/18 | 18/18 | 18/18 | 11/16 | RETRIEVED_NOT_RETAINED 1, QUERY_GAP 1 | 6 |
| pcsk9-mace | 11 | 5/11 | 5/11 | 9/11 | 10/11 | 5/5 | QUERY_GAP 5, DATABASE_NOT_SEARCHED 1 | 1 |
| probiotics-aad-prevention | 41 | 36/41 | 36/41 | 36/41 | 36/41 | 24/36 | IDENTITY_FAILURE 5 | 0 |
| sacubitril-valsartan-hfref | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/2 | - | 7 |
| semaglutide-obesity-mace | 2 | 1/2 | 1/2 | 2/2 | 2/2 | 1/1 | QUERY_GAP 1 | 1 |
| semaglutide-obesity-weight | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | - | 2 |
| sglt2-ckd-progression | 6 | 3/6 | 5/6 | 6/6 | 6/6 | 3/3 | QUERY_GAP 3 | 6 |
| sglt2-hfref-hosp-cvdeath | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | - | 2 |
| sglt2-primary-prevention-hf | 5 | 4/5 | 4/5 | 5/5 | 5/5 | 4/4 | QUERY_GAP 1 | 3 |
| spironolactone-hfref-mortality | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | - | 1 |
| statins-primary-prevention-elderly | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | - | 12 |
| ticagrelor-vs-clopidogrel-acs | 4 | 3/4 | 3/4 | 3/4 | 3/4 | 3/3 | IDENTITY_FAILURE 1 | 6 |
| tocilizumab-covid19-mortality | 19 | 10/19 | 10/19 | 0/19 | 17/19 | 8/10 | RETRIEVED_NOT_RETAINED 7, IDENTITY_FAILURE 2 | 0 |
| tranexamic-acid-pph | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | - | 4 |
