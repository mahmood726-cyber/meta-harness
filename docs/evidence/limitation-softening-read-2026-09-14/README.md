SOFTENED PAIRS FOUND: 15; first example corticosteroids-cap-mortality b8925e04 pair 1: BEFORE "Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RUN ; its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications (UID/PMID-anchored queries for pre-identified trials), which cannot discover an unknown eligible trial. A fetch of named identifiers is not a systematic search. We retract any claim of a registry-first or systematic search for this topic." AFTER "TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH an auditable screening ledger attached to an unauditable retrieval process."

# Limitation softening read 2026-09-14

**Fix state (four-state rule): LANDED** - a one-time read; superseded by the structured-object design.

Method: I used `harness.honest_ratchet.blocks()` on local `git show` output for `b8925e04^` -> `b8925e04` and `f928a536^` -> `f928a536` for all 32 `docs/reviews/<slug>/index.html` pages. Identical block SHA-256 values were treated as anchors; within changed regions, BEFORE blocks were paired to AFTER blocks by class and relative position. Additions with no BEFORE block were counted in the per-topic files but not judged as softening pairs. The verdicts are a model's semantic reading, not a mechanical check; this is exactly the human step the limitations-as-objects design is meant to replace.

| slug | pairs changed regen-1 | softened | pairs changed regen-2 | softened |
| --- | ---: | ---: | ---: | ---: |
| balanced-crystalloids-vs-saline-mortality | 0 | 0 | 1 | 0 |
| colchicine-postop-af | 0 | 0 | 1 | 0 |
| colchicine-recurrent-pericarditis | 0 | 0 | 1 | 0 |
| colchicine-secondary-cv-prevention | 0 | 0 | 1 | 0 |
| corticosteroids-cap-mortality | 1 | 1 | 1 | 0 |
| corticosteroids-covid19-mortality | 0 | 0 | 1 | 0 |
| dapagliflozin-hfpef-hosp | 1 | 1 | 1 | 0 |
| denosumab-vertebral-fracture | 0 | 0 | 1 | 0 |
| doac-vte-recurrence | 1 | 1 | 1 | 0 |
| dpp4-mace-t2d | 1 | 1 | 1 | 0 |
| empagliflozin-hfpef-hosp | 1 | 1 | 1 | 0 |
| esketamine-trd-madrs | 1 | 1 | 1 | 0 |
| finerenone-ckd-t2d-renal | 0 | 0 | 1 | 0 |
| glp1-ra-mace-t2d | 0 | 0 | 1 | 0 |
| iv-iron-hfref-hosp | 1 | 1 | 1 | 0 |
| melatonin-primary-insomnia-sol | 1 | 1 | 1 | 0 |
| metformin-pcos-ovulation | 1 | 1 | 1 | 0 |
| noac-vs-warfarin-af-stroke | 0 | 0 | 1 | 0 |
| omega3-cardiovascular-events | 0 | 0 | 1 | 0 |
| pcsk9-mace | 0 | 0 | 1 | 0 |
| probiotics-aad-prevention | 0 | 0 | 1 | 0 |
| sacubitril-valsartan-hfref | 1 | 1 | 1 | 0 |
| semaglutide-obesity-mace | 0 | 0 | 1 | 0 |
| semaglutide-obesity-weight | 1 | 1 | 1 | 0 |
| sglt2-ckd-progression | 1 | 1 | 1 | 0 |
| sglt2-hfref-hosp-cvdeath | 1 | 1 | 1 | 0 |
| sglt2-primary-prevention-hf | 1 | 1 | 1 | 0 |
| spironolactone-hfref-mortality | 1 | 1 | 1 | 0 |
| statins-primary-prevention-elderly | 0 | 0 | 1 | 0 |
| ticagrelor-vs-clopidogrel-acs | 0 | 0 | 1 | 0 |
| tocilizumab-covid19-mortality | 0 | 0 | 1 | 0 |
| tranexamic-acid-pph | 0 | 0 | 1 | 0 |

Summary: regen-1 (`b8925e04`) has 15 softened paired replacements, all in the old Search provenance block that was replaced by shorter retrieval-class prose. Regen-2 (`f928a536`) has one changed paired block on each page, but every change is a retrieval-class query-count update with the same force.
