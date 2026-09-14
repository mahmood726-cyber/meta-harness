# Query structure classification (2026-09-14)

**Fix state (four-state rule): LANDED** - classification evidence.

Denominator: 32 of 32 live review pages, named: balanced-crystalloids-vs-saline-mortality, colchicine-postop-af, colchicine-recurrent-pericarditis, colchicine-secondary-cv-prevention, corticosteroids-cap-mortality, corticosteroids-covid19-mortality, dapagliflozin-hfpef-hosp, denosumab-vertebral-fracture, doac-vte-recurrence, dpp4-mace-t2d, empagliflozin-hfpef-hosp, esketamine-trd-madrs, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, iv-iron-hfref-hosp, melatonin-primary-insomnia-sol, metformin-pcos-ovulation, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace, probiotics-aad-prevention, sacubitril-valsartan-hfref, semaglutide-obesity-mace, semaglutide-obesity-weight, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf, spironolactone-hfref-mortality, statins-primary-prevention-elderly, ticagrelor-vs-clopidogrel-acs, tocilizumab-covid19-mortality, tranexamic-acid-pph.

New structural classes: KNOWN_ITEM_RETRIEVAL 11 of 32 (dapagliflozin-hfpef-hosp, doac-vte-recurrence, dpp4-mace-t2d, empagliflozin-hfpef-hosp, glp1-ra-mace-t2d, noac-vs-warfarin-af-stroke, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf, spironolactone-hfref-mortality, ticagrelor-vs-clopidogrel-acs); TITLE_SEEDED_RETRIEVAL 17 of 32 (balanced-crystalloids-vs-saline-mortality, colchicine-secondary-cv-prevention, corticosteroids-covid19-mortality, denosumab-vertebral-fracture, esketamine-trd-madrs, finerenone-ckd-t2d-renal, iv-iron-hfref-hosp, melatonin-primary-insomnia-sol, metformin-pcos-ovulation, omega3-cardiovascular-events, pcsk9-mace, sacubitril-valsartan-hfref, semaglutide-obesity-mace, semaglutide-obesity-weight, statins-primary-prevention-elderly, tocilizumab-covid19-mortality, tranexamic-acid-pph); HAND_WRITTEN_KEYWORD_SEARCH 4 of 32 (colchicine-postop-af, colchicine-recurrent-pericarditis, corticosteroids-cap-mortality, probiotics-aad-prevention); CONCEPT_SEARCH 0 of 32 (none).

Changed class: 4 of 32 (colchicine-postop-af, colchicine-recurrent-pericarditis, corticosteroids-cap-mortality, probiotics-aad-prevention).

Retraction sentence present on non-concept pages: 32 of 32 (balanced-crystalloids-vs-saline-mortality, colchicine-postop-af, colchicine-recurrent-pericarditis, colchicine-secondary-cv-prevention, corticosteroids-cap-mortality, corticosteroids-covid19-mortality, dapagliflozin-hfpef-hosp, denosumab-vertebral-fracture, doac-vte-recurrence, dpp4-mace-t2d, empagliflozin-hfpef-hosp, esketamine-trd-madrs, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, iv-iron-hfref-hosp, melatonin-primary-insomnia-sol, metformin-pcos-ovulation, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace, probiotics-aad-prevention, sacubitril-valsartan-hfref, semaglutide-obesity-mace, semaglutide-obesity-weight, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf, spironolactone-hfref-mortality, statins-primary-prevention-elderly, ticagrelor-vs-clopidogrel-acs, tocilizumab-covid19-mortality, tranexamic-acid-pph).

| slug | old class | new class | n queries by kind | retraction sentence present on page |
|---|---|---|---|---|
| `balanced-crystalloids-vs-saline-mortality` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=4 | yes |
| `colchicine-postop-af` | `TITLE_SEEDED_RETRIEVAL` | `HAND_WRITTEN_KEYWORD_SEARCH` | FREE_TEXT_KEYWORD=3 | yes |
| `colchicine-recurrent-pericarditis` | `TITLE_SEEDED_RETRIEVAL` | `HAND_WRITTEN_KEYWORD_SEARCH` | FREE_TEXT_KEYWORD=3 | yes |
| `colchicine-secondary-cv-prevention` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | NAME_SEEDED=2, FREE_TEXT_KEYWORD=2 | yes |
| `corticosteroids-cap-mortality` | `TITLE_SEEDED_RETRIEVAL` | `HAND_WRITTEN_KEYWORD_SEARCH` | FREE_TEXT_KEYWORD=4 | yes |
| `corticosteroids-covid19-mortality` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=3, FREE_TEXT_KEYWORD=1 | yes |
| `dapagliflozin-hfpef-hosp` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `denosumab-vertebral-fracture` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | PMID_ENUMERATION=2, TITLE_ANCHORED=1 | yes |
| `doac-vte-recurrence` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `dpp4-mace-t2d` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `empagliflozin-hfpef-hosp` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=2 | yes |
| `esketamine-trd-madrs` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=2, FREE_TEXT_KEYWORD=2 | yes |
| `finerenone-ckd-t2d-renal` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=4 | yes |
| `glp1-ra-mace-t2d` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `iv-iron-hfref-hosp` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | IDENTIFIER_SEEDED=2, NAME_SEEDED=2 | yes |
| `melatonin-primary-insomnia-sol` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=2, FREE_TEXT_KEYWORD=2 | yes |
| `metformin-pcos-ovulation` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=4 | yes |
| `noac-vs-warfarin-af-stroke` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=3 | yes |
| `omega3-cardiovascular-events` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=3 | yes |
| `pcsk9-mace` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=3 | yes |
| `probiotics-aad-prevention` | `TITLE_SEEDED_RETRIEVAL` | `HAND_WRITTEN_KEYWORD_SEARCH` | FREE_TEXT_KEYWORD=4 | yes |
| `sacubitril-valsartan-hfref` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | PMID_ENUMERATION=2, TITLE_ANCHORED=2 | yes |
| `semaglutide-obesity-mace` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | PMID_ENUMERATION=2, TITLE_ANCHORED=2 | yes |
| `semaglutide-obesity-weight` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=2, NAME_SEEDED=1, FREE_TEXT_KEYWORD=1 | yes |
| `sglt2-ckd-progression` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `sglt2-hfref-hosp-cvdeath` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `sglt2-primary-prevention-hf` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `spironolactone-hfref-mortality` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=4 | yes |
| `statins-primary-prevention-elderly` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=4 | yes |
| `ticagrelor-vs-clopidogrel-acs` | `KNOWN_ITEM_RETRIEVAL` | `KNOWN_ITEM_RETRIEVAL` | PMID_ENUMERATION=3 | yes |
| `tocilizumab-covid19-mortality` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | TITLE_ANCHORED=4 | yes |
| `tranexamic-acid-pph` | `TITLE_SEEDED_RETRIEVAL` | `TITLE_SEEDED_RETRIEVAL` | NAME_SEEDED=3, FREE_TEXT_KEYWORD=1 | yes |
