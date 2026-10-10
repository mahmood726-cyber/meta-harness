# Family-eligibility reconcile count (read-only; nothing applied)

Rule: ELIGIBLE iff >=1 family record is INCLUDED by the record-level screen AND the structural family screen says ELIGIBLE (never INELIGIBLE / UNKNOWN). Source: each topic's served docs/reviews/<slug>/review.json.

| topic | active | served eligible | reconciled | structural-only (no included record) | included record, structural UNKNOWN |
|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | no | 2 | 2 | 0 | 3 |
| colchicine-postop-af | no | 4 | 4 | 0 | 2 |
| colchicine-recurrent-pericarditis | yes | 3 | 3 | 0 | 0 |
| colchicine-secondary-cv-prevention | no | 12 | 7 | 5 | 6 |
| corticosteroids-cap-mortality | no | 3 | 3 | 0 | 4 |
| corticosteroids-covid19-mortality | yes | 1 | 0 | 1 | 5 |
| dapagliflozin-hfpef-hosp | yes | 4 | 4 | 0 | 0 |
| denosumab-vertebral-fracture | yes | 0 | 0 | 0 | 1 |
| doac-vte-recurrence | yes | 3 | 2 | 1 | 3 |
| dpp4-mace-t2d | yes | 7 | 4 | 3 | 1 |
| empagliflozin-hfpef-hosp | yes | 1 | 0 | 1 | 2 |
| esketamine-trd-madrs | yes | 2 | 1 | 1 | 1 |
| finerenone-ckd-t2d-renal | yes | 4 | 3 | 1 | 1 |
| glp1-ra-mace-t2d | yes | 145 | 8 | 137 | 0 |
| iv-iron-hfref-hosp | yes | 2 | 2 | 0 | 6 |
| melatonin-primary-insomnia-sol | yes | 3 | 1 | 2 | 0 |
| metformin-pcos-ovulation | no | 8 | 0 | 8 | 1 |
| noac-vs-warfarin-af-stroke | yes | 12 | 7 | 5 | 0 |
| omega3-cardiovascular-events | no | 2 | 2 | 0 | 10 |
| pcsk9-mace | no | 2 | 2 | 0 | 3 |
| probiotics-aad-prevention | no | 10 | 7 | 3 | 8 |
| sacubitril-valsartan-hfref | yes | 7 | 1 | 6 | 0 |
| semaglutide-obesity-mace | yes | 0 | 0 | 0 | 1 |
| semaglutide-obesity-weight | yes | 20 | 6 | 14 | 1 |
| sglt2-ckd-progression | yes | 7 | 5 | 2 | 1 |
| sglt2-hfref-hosp-cvdeath | yes | 2 | 2 | 0 | 1 |
| sglt2-primary-prevention-hf | yes | 7 | 2 | 5 | 3 |
| spironolactone-hfref-mortality | yes | 1 | 0 | 1 | 0 |
| statins-primary-prevention-elderly | yes | 1 | 1 | 0 | 1 |
| ticagrelor-vs-clopidogrel-acs | no | 2 | 1 | 1 | 0 |
| tocilizumab-covid19-mortality | no | 4 | 2 | 2 | 5 |
| tranexamic-acid-pph | yes | 5 | 2 | 3 | 1 |
