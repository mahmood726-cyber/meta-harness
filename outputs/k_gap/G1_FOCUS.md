# G1 focus topics (derived by scripts/g1_focus_report.py)

| topic | k matched | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | ours | comparator |
|---|---|---|---|---|---|---|---|---|
| glp1-ra-mace-t2d | 7 of 8 | 8 | 0 | 0 | 0 | {'AGREE': 6, 'DISAGREE': 1} | HR 0.86 (0.81 to 0.91) k=8 | HR 0.86 (0.79 to 0.94) |
| semaglutide-obesity-weight | 2 of 3 | 2 | 0 | 0 | 1 | {'NOT_COMPARABLE': 2} | MD -11.47 (no CI) k=2 | not printed |
| noac-vs-warfarin-af-stroke | 3 of 4 | 3 | 0 | 0 | 1 | {'NOT_COMPARABLE': 3} | HR 0.81 (0.66 to 0.98) k=4 | HR 0.81 (0.74 to 0.89) |
| tocilizumab-covid19-mortality | 1 of 7 | 1 | 0 | 0 | 6 | {'NOT_COMPARABLE': 1} | RR 0.85 (0.76 to 0.94) k=1 | OR 0.86 (0.79 to 0.95) |

## glp1-ra-mace-t2d (comparator PMID 34526024)

- ELIXA: **PRIMARY** - meta 34526024 PRIMARY_VERIFIED PRIMARY_TEXT; vs comparator row: NOT_IN_OUR_POOL
- LEADER: **PRIMARY** - our branch extraction PMID 27295427 (abstract); vs comparator row: AGREE
- SUSTAIN-6: **PRIMARY** - our branch extraction PMID 27633186 (abstract); vs comparator row: AGREE
- EXSCEL: **PRIMARY** - our branch extraction PMID 28910237 (abstract); vs comparator row: AGREE
- HARMONY: **PRIMARY** - our branch extraction PMID 30291013 (abstract); vs comparator row: AGREE
- REWIND: **PRIMARY** - our branch extraction PMID 31189511 (abstract); vs comparator row: AGREE
- PIONEER 6: **PRIMARY** - our branch extraction PMID 31185157 (abstract); vs comparator row: DISAGREE
- AMPLITUDE-O: **PRIMARY** - our branch extraction PMID 34215025 (abstract); vs comparator row: AGREE

## semaglutide-obesity-weight (comparator PMID 42536519)

- Rubino, 2021: **NO_ROW** - IDENTIFICATION; vs comparator row: NOT_IN_OUR_POOL
- Wadden, 2021: **PRIMARY** - our branch extraction PMID 33625476 (abstract); vs comparator row: NOT_COMPARABLE
- Wilding, 2021: **PRIMARY** - our branch extraction PMID 33567185 (abstract); vs comparator row: NOT_COMPARABLE

## noac-vs-warfarin-af-stroke (comparator PMID 34985309)

- RE-LY: **PRIMARY** - our branch extraction PMID 19717844 (pre_specified_dose); vs comparator row: NOT_COMPARABLE
- ROCKET AF: **NO_ROW** - UNRESOLVED_IDENTITY; vs comparator row: NOT_IN_OUR_POOL
- ARISTOTLE: **PRIMARY** - our branch extraction PMID 21870978 (abstract); vs comparator row: NOT_COMPARABLE
- ENGAGE AF-TIMI 48: **PRIMARY** - our branch extraction PMID 24251359 (pre_specified_dose); vs comparator row: NOT_COMPARABLE

## tocilizumab-covid19-mortality (comparator PMID 34228774)

- Effect of Tocilizumab vs Usual Care in Adults Hospitalized W: **NO_ROW** - ACQUISITION; vs comparator row: NOT_IN_OUR_POOL
- Tocilizumab in patients admitted to hospital with COVID-19 (: **PRIMARY** - our branch extraction PMID 33933206 (abstract); vs comparator row: NOT_COMPARABLE
- Effect of tocilizumab on clinical outcomes at 15 days in pat: **NO_ROW** - ACQUISITION (secondary refused: ['TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL
- Tocilizumab plus standard care versus standard care in patie: **NO_ROW** - IDENTIFICATION (secondary refused: ['TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL
- Efficacy of Tocilizumab in Patients Hospitalized with Covid-: **NO_ROW** - ACQUISITION; vs comparator row: NOT_IN_OUR_POOL
- Tocilizumab in Hospitalized Patients with Severe Covid-19 Pn: **NO_ROW** - ACQUISITION (secondary refused: ['TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL
- Tocilizumab in Patients Hospitalized with Covid-19 Pneumonia: **NO_ROW** - ACQUISITION (secondary refused: ['TIMEPOINT_NOT_STATED_BY_META']); vs comparator row: NOT_IN_OUR_POOL
