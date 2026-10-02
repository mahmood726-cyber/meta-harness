# G1 tracker (derived: scripts/g1_tracker.py; one source file per topic in outputs/k_gap/g1/)

| topic | k matched | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator |
|---|---|---|---|---|---|---|---|---|---|
| glp1-ra-mace-t2d | 7 of 8 | 8 | 0 | 0 | 0 | {'AGREE': 6, 'DISAGREE': 1} | HR 0.85 (0.80 to 0.90) vs 0.85 (0.80 to 0.90), k=7, DL | HR 0.86 (0.81 to 0.91) k=8 | HR 0.86 (0.79 to 0.94) |
| semaglutide-obesity-weight | 2 of 3 | 2 | 0 | 0 | 1 | {'NOT_COMPARABLE:NO_COMPARATOR_ROW': 2} | FEWER_THAN_2_SHARED_TRIALS | MD -11.47 (no CI) k=2 | not printed |

## glp1-ra-mace-t2d (comparator PMID 34526024)

- ELIXA: **PRIMARY** - meta 34526024 PRIMARY_VERIFIED PRIMARY_TEXT; vs comparator row: NOT_IN_OUR_POOL
- LEADER: **PRIMARY** - our branch extraction PMID 27295427 (abstract); vs comparator row: AGREE
- SUSTAIN-6: **PRIMARY** - our branch extraction PMID 27633186 (abstract); vs comparator row: AGREE
- EXSCEL: **PRIMARY** - our branch extraction PMID 28910237 (abstract); vs comparator row: AGREE
- HARMONY: **PRIMARY** - our branch extraction PMID 30291013 (abstract); vs comparator row: AGREE
- REWIND: **PRIMARY** - our branch extraction PMID 31189511 (abstract); vs comparator row: AGREE
- PIONEER 6: **PRIMARY** - our branch extraction PMID 31185157 (abstract); vs comparator row: DISAGREE
- AMPLITUDE-O: **PRIMARY** - our branch extraction PMID 34215025 (abstract); vs comparator row: AGREE
- pooled by us, not listed by the comparator: PMID 40162642

## semaglutide-obesity-weight (comparator PMID 42536519)

- Rubino, 2021: **NO_ROW** - IDENTIFICATION; vs comparator row: NOT_IN_OUR_POOL
- Wadden, 2021: **PRIMARY** - our branch extraction PMID 33625476 (abstract); vs comparator row: NOT_COMPARABLE:NO_COMPARATOR_ROW
- Wilding, 2021: **PRIMARY** - our branch extraction PMID 33567185 (abstract); vs comparator row: NOT_COMPARABLE:NO_COMPARATOR_ROW
