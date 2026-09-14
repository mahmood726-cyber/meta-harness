# Search provenance restored 2026-09-14

**Fix state (orthogonal fields rule): LANDED / NONE / INSTANCE / CURRENT** - generated from TRANCHE-search-provenance-restored

This evidence bundle restores the Search provenance absent block from `search.retrieval_class.search_provenance`, not from page-local inference.

| slug | class | registry_first_status | in the fifteen? | lost-text vs new-text |
| --- | --- | --- | --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `colchicine-postop-af` | `HAND_WRITTEN_KEYWORD_SEARCH` | `RAN_OK` | no | not compared |
| `colchicine-recurrent-pericarditis` | `HAND_WRITTEN_KEYWORD_SEARCH` | `RAN_OK` | no | not compared |
| `colchicine-secondary-cv-prevention` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `corticosteroids-cap-mortality` | `HAND_WRITTEN_KEYWORD_SEARCH` | `NOT_RUN` | yes | differs-in-class-statement |
| `corticosteroids-covid19-mortality` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `dapagliflozin-hfpef-hosp` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | yes | identical |
| `denosumab-vertebral-fracture` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `doac-vte-recurrence` | `KNOWN_ITEM_RETRIEVAL` | `RAN_ERROR` | yes | identical |
| `dpp4-mace-t2d` | `KNOWN_ITEM_RETRIEVAL` | `RAN_ERROR` | yes | identical |
| `empagliflozin-hfpef-hosp` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | yes | identical |
| `esketamine-trd-madrs` | `TITLE_SEEDED_RETRIEVAL` | `RAN_ERROR` | yes | differs-in-class-statement |
| `finerenone-ckd-t2d-renal` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `glp1-ra-mace-t2d` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | no | not compared |
| `iv-iron-hfref-hosp` | `TITLE_SEEDED_RETRIEVAL` | `NOT_RUN` | yes | differs-in-class-statement |
| `melatonin-primary-insomnia-sol` | `TITLE_SEEDED_RETRIEVAL` | `RAN_ERROR` | yes | differs-in-class-statement |
| `metformin-pcos-ovulation` | `TITLE_SEEDED_RETRIEVAL` | `NOT_RUN` | yes | differs-in-class-statement |
| `noac-vs-warfarin-af-stroke` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | no | not compared |
| `omega3-cardiovascular-events` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `pcsk9-mace` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `probiotics-aad-prevention` | `HAND_WRITTEN_KEYWORD_SEARCH` | `RAN_OK` | no | not compared |
| `sacubitril-valsartan-hfref` | `TITLE_SEEDED_RETRIEVAL` | `NOT_RUN` | yes | differs-in-class-statement |
| `semaglutide-obesity-mace` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `semaglutide-obesity-weight` | `TITLE_SEEDED_RETRIEVAL` | `RAN_ERROR` | yes | differs-in-class-statement |
| `sglt2-ckd-progression` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | yes | identical |
| `sglt2-hfref-hosp-cvdeath` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | yes | identical |
| `sglt2-primary-prevention-hf` | `KNOWN_ITEM_RETRIEVAL` | `RAN_ERROR` | yes | identical |
| `spironolactone-hfref-mortality` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | yes | identical |
| `statins-primary-prevention-elderly` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `ticagrelor-vs-clopidogrel-acs` | `KNOWN_ITEM_RETRIEVAL` | `RAN_OK` | no | not compared |
| `tocilizumab-covid19-mortality` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |
| `tranexamic-acid-pph` | `TITLE_SEEDED_RETRIEVAL` | `RAN_OK` | no | not compared |

The `differs-in-class-statement` rows are the topics where the structural classifier now reads the query set as TITLE-SEEDED or HAND-WRITTEN rather than the lost emitter's blanket KNOWN-ITEM wording; `03-the-fifteen-compared.txt` also names the paired discovery-statement changes.
