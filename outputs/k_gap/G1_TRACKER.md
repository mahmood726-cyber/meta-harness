# G1 tracker (derived: scripts/g1_tracker.py; one source file per topic in outputs/k_gap/g1/)

| topic | k matched | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator |
|---|---|---|---|---|---|---|---|---|---|
| glp1-ra-mace-t2d | 7 of 8 | 8 | 0 | 0 | 0 | {'AGREE': 6, 'DISAGREE': 1} | HR 0.85 (0.80 to 0.90) vs 0.85 (0.80 to 0.90), k=7, DL: **AGREE** | HR 0.86 (0.81 to 0.91) k=8 | HR 0.86 (0.79 to 0.94) |
| semaglutide-obesity-weight | 2 of 4 | 2 | 0 | 0 | 2 | {'AGREE': 2} | MD -11.47 (-13.52 to -9.43) vs -11.49 (-13.58 to -9.41), k=2, DL: **AGREE** | MD -11.47 (no CI) k=2 | MD -11.85 (-12.81 to -10.90) |

## glp1-ra-mace-t2d (comparator PMID 34526024)

- ELIXA: **PRIMARY** - meta 34526024 PRIMARY_VERIFIED PRIMARY_TEXT; vs comparator row: NOT_IN_OUR_POOL; our refusal: no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract
- LEADER: **PRIMARY** - our branch extraction PMID 27295427 (abstract); vs comparator row: AGREE
- SUSTAIN-6: **PRIMARY** - our branch extraction PMID 27633186 (abstract); vs comparator row: AGREE
- EXSCEL: **PRIMARY** - our branch extraction PMID 28910237 (abstract); vs comparator row: AGREE
- HARMONY: **PRIMARY** - our branch extraction PMID 30291013 (abstract); vs comparator row: AGREE
- REWIND: **PRIMARY** - our branch extraction PMID 31189511 (abstract); vs comparator row: AGREE
- PIONEER 6: **PRIMARY** - our branch extraction PMID 31185157 (abstract); vs comparator row: DISAGREE; side: SECONDARY_WRONG (primary numbers are in the primary's own span)
- AMPLITUDE-O: **PRIMARY** - our branch extraction PMID 34215025 (abstract); vs comparator row: AGREE
- pooled by us, not listed by the comparator: PMID 40162642 (2025; comparator 2021): PUBLISHED_AFTER_COMPARATOR

## semaglutide-obesity-weight (comparator PMID 42536519)

- O’Neil, 2018: **NO_ROW** - IDENTIFICATION (secondary refused: ['OUTCOME_NOT_THE_TOPICS', 'TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL; our refusal: SEEDED PMID 30122305: SCREENED_OUT X2: wrong population: title/conditions mention 'liraglutide'.
- Rubino, 2021: **NO_ROW** - IDENTIFICATION (secondary refused: ['OUTCOME_NOT_THE_TOPICS', 'TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL; our refusal: SEEDED PMID 33755728: SCREENED_OUT X2: wrong population: title/conditions mention 'maintenance'.; comparator row finding: [{'finding': 'ROW_CI_NOT_FROM_ARMS', 'printed_vs_arm_derived': {'lower': ['-14.75', -13.75], 'upper': ['-10.05', -11.05]}}]
- Wadden, 2021: **PRIMARY** - our branch extraction PMID 33625476 (abstract); vs comparator row: AGREE
- Wilding, 2021: **PRIMARY** - our branch extraction PMID 33567185 (abstract); vs comparator row: AGREE
