# LANE AE Report

Base commit: `41a466fb35bdc470d73c479e878bbbc9f0979f9a`

| Topic | Comparator PMID | THEIRS defects | OURS defects | Full text obtained / effect rows parsed | characteristics table parsed (rows) | THEIRS checks assessable | Comparator effect inputs exposed |
| --- | ---: | ---: | ---: | --- | ---: | --- | --- |
| balanced-crystalloids-vs-saline-mortality | 30140441 | 1 | 2 | YES (Europe PMC PMCID fullTextXML; sha256 97f7c59cf9b1) / 0 | YES (8) | Design key, Analysis population, Compatibility key | NO |
| colchicine-recurrent-pericarditis | 22442198 | 0 | 0 | NO (FULL_TEXT_NOT_AVAILABLE_OA) / 0 | NO (0) | none | NO |
| colchicine-secondary-cv-prevention | 36176989 | 0 | 1 | YES (Europe PMC PMCID fullTextXML; sha256 9954db2eddf8) / 0 | YES (15) | Design key, Analysis population, Compatibility key | NO |
| corticosteroids-cap-mortality | 38128217 | 0 | 0 | NO (FULL_TEXT_NOT_AVAILABLE_OA) / 0 | NO (0) | none | NO |
| corticosteroids-covid19-mortality | 32876694 | 0 | 0 | NO (FULL_TEXT_NOT_AVAILABLE_OA) / 0 | NO (0) | none | NO |
| denosumab-vertebral-fracture | 36852077 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 8dad63285d82) / 0 | NO (0) | none | NO |
| doac-vte-recurrence | 24963045 | 0 | 1 | NO (FULL_TEXT_NOT_AVAILABLE_OA) / 0 | NO (0) | none | NO |
| finerenone-ckd-t2d-renal | 36742404 | 0 | 1 | YES (Europe PMC PMCID fullTextXML; sha256 19c44382b2d6) / 0 | YES (4) | Design key, Analysis population, Compatibility key | NO |
| glp1-ra-mace-t2d | 34526024 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 a9b78d5db601) / 0 | YES (8) | Design key, Analysis population, Compatibility key | NO |
| metformin-pcos-ovulation | 31845767 | 0 | 0 | NO (FULL_TEXT_NOT_AVAILABLE_OA) / 0 | NO (0) | none | NO |
| noac-vs-warfarin-af-stroke | 34985309 | 0 | 1 | YES (PMC OAI pmc metadata; sha256 c9cf8143dd9c) / 0 | YES (3) | Design key, Analysis population, Compatibility key | NO |
| omega3-cardiovascular-events | 35905212 | 0 | 3 | YES (Europe PMC PMCID fullTextXML; sha256 e78edc5b0ded) / 0 | YES (28) | Design key, Analysis population, Compatibility key | NO |
| pcsk9-mace | 36531722 | 0 | 1 | YES (Europe PMC PMCID fullTextXML; sha256 73bf6b5f63b3) / 0 | YES (7) | Design key, Analysis population, Compatibility key | NO |
| probiotics-aad-prevention | 34385227 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 886efbca5d98) / 0 | YES (42) | Design key, Analysis population, Compatibility key | NO |
| sglt2-ckd-progression | 41203232 | 0 | 1 | NO (FULL_TEXT_NOT_AVAILABLE_OA) / 0 | NO (0) | none | NO |
| sglt2-hfref-hosp-cvdeath | 35112512 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 fddad0b72174) / 0 | NO (0) | none | NO |
| sglt2-primary-prevention-hf | 33519713 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 e1a01a870664) / 0 | NO (0) | none | NO |
| spironolactone-hfref-mortality | 40959489 | 0 | 1 | YES (Europe PMC PMCID fullTextXML; sha256 fed4122ee988) / 0 | YES (9) | Design key, Analysis population, Compatibility key | NO |
| statins-primary-prevention-elderly | 39076238 | 1 | 1 | YES (Europe PMC PMCID fullTextXML; sha256 139b25a42c12) / 0 | YES (12) | Design key, Analysis population, Compatibility key | NO |
| ticagrelor-vs-clopidogrel-acs | 28545073 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 ecd40ef97b43) / 0 | YES (22) | Design key, Analysis population, Compatibility key | NO |
| tranexamic-acid-pph | 39461793 | 0 | 0 | YES (Europe PMC PMCID fullTextXML; sha256 395e9b48be67) / 0 | NO (0) | none | NO |

Totals: THEIRS defect cells=2; OURS defect cells=13.
Full texts obtained: 15/21.
Machine-readable per-trial effect inputs: 0/21.
Parsed primary-outcome effect rows: 0.
Characteristics tables parsed: 11/21 (balanced-crystalloids-vs-saline-mortality, colchicine-secondary-cv-prevention, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace, probiotics-aad-prevention, spironolactone-hfref-mortality, statins-primary-prevention-elderly, ticagrelor-vs-clopidogrel-acs).
Characteristics rows parsed: 158.
THEIRS design/population/compatibility checks assessable from characteristics tables: 11/21.

Open-access label failed:
- colchicine-recurrent-pericarditis, corticosteroids-cap-mortality, corticosteroids-covid19-mortality, doac-vte-recurrence, metformin-pcos-ovulation, sglt2-ckd-progression.

Machine-readable comparator pooled effect inputs exposed:
- Exposed: none.
- Not exposed: balanced-crystalloids-vs-saline-mortality, colchicine-recurrent-pericarditis, colchicine-secondary-cv-prevention, corticosteroids-cap-mortality, corticosteroids-covid19-mortality, denosumab-vertebral-fracture, doac-vte-recurrence, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, metformin-pcos-ovulation, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace, probiotics-aad-prevention, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf, spironolactone-hfref-mortality, statins-primary-prevention-elderly, ticagrelor-vs-clopidogrel-acs, tranexamic-acid-pph.

Characteristics tables parsed:
- Parsed: balanced-crystalloids-vs-saline-mortality, colchicine-secondary-cv-prevention, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace, probiotics-aad-prevention, spironolactone-hfref-mortality, statins-primary-prevention-elderly, ticagrelor-vs-clopidogrel-acs.
- Not parsed: colchicine-recurrent-pericarditis, corticosteroids-cap-mortality, corticosteroids-covid19-mortality, denosumab-vertebral-fracture, doac-vte-recurrence, metformin-pcos-ovulation, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf, tranexamic-acid-pph.

Commands:
- `python scripts/comparator_correctness_sweep.py`
- `python scripts/rewrite_fixstate_lines.py`
- `python scripts/render_fix_ledger.py`
- `python -m harness.index docs`
- `python scripts/build_evidence_index.py`
- `python -m pytest tests/ -q`
- `python scripts/verify_all.py`

No commit was made.
