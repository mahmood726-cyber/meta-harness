# Typed per-arm observations for the served count rows -- report

Population: **35** served count rows (`outcomes[*].trials[*]` with `ai`/`ci`) at `1aaeb80c`, frozen in `population.json`. Kinds of item in the population: served count rows only -- no synthetic controls (those live in `tests/test_typed_arms.py`), no split rows, no refused-at-intake rows.

Before this work: comparator_direction carried by 0 of 35; typed arm ownership carried by 0 of 35.

## Result

- **BOUND: 32 of 35**
- **SET_ASIDE: 3 of 35**
- **SOURCE_DIFFERS: 0 of 35**
- **NOT_EXTRACTED: 0 of 35**

`SOURCE_DIFFERS` is the only state that would change a served number; it goes to Mahmood's signature queue, never landed. `SET_ASIDE` changes nothing served: the row keeps its served value and is not typed.

## Bound rows: how each arm's identity and ownership were established

Arm identity, over the 64 arms of the 32 bound rows:
- REGISTRY_ARM: 41
- SOURCE_LABEL (no registry arms held): 18
- SOURCE_LABEL (registry non-discriminating): 2
- FACTORIAL_MARGIN: 2
- REGISTRY_ARM (gate-derived): 1

Ownership of the events (G7), over the same 64 arms:
- ADJACENT_LABEL: 43
- PARALLEL_ORDER: 10
- TABLE_COLUMN: 6
- GROUP_ID: 4
- VERSUS_ORDER: 1

Ownership of the denominator (G7), over the same 64 arms:
- ADJACENT_LABEL: 47
- PARALLEL_ORDER: 11
- GROUP_ID: 4
- TABLE_COLUMN: 2

Denominator basis as the source states it, over the same 64 arms (a percentage never stands in):
- RANDOMISED: 34
- SAFETY_TREATED: 12
- STATED_UNQUALIFIED: 10
- ANALYSED: 8

## Every row not bound, with its named reasons

### CD-dapagliflozin-hfpef-hosp-1-0 -- SET_ASIDE
dapagliflozin-hfpef-hosp / Adverse events / PMID 34711976; served {'ai': 44, 'n1i': 162, 'ci': 38, 'n2i': 162}
- G1 arm 0 total: no span
- G3 arm 0: denominator not stated as a number (basis NOT_STATED; a percentage '27.2%' does not stand in)
- G1 arm 1 total: no span
- G3 arm 1: denominator not stated as a number (basis NOT_STATED; a percentage '23.5%' does not stand in)
- G4 not evaluated: an arm's events or denominator is not bound to a printed number (G1-G3), so no comparison with the served slots is made -- SET_ASIDE, not a served-number difference
- extractor note: The abstract reports patients with adverse events, and its counts and percentages match the served event counts. NOT_IN_PACKET: outcome-specific per-arm adverse-event denominators. The abstract states 324 patients randomized in total but no per-arm totals. The held registry document states 162 participants per arm for several efficacy outcomes, but contains no adverse-event results or safety-population denominators; those efficacy denominators were not transferred to this outcome. The AACT serious-adverse-event denominator excerpt in row.json is not present in either held doc file. The quoted 

### CD-metformin-pcos-ovulation-0-0 -- SET_ASIDE
metformin-pcos-ovulation / Ovulation with metformin added to clomifene / PMID 19522426; served {'ai': 10, 'n1i': 16, 'ci': 6, 'n2i': 16}
- G1 arm 0 events: no span
- G1 arm 0 total: no span
- G2 arm 0: events not an integer (None)
- G3 arm 0: denominator not stated as a number (basis NOT_STATED; a percentage '62.5%' does not stand in)
- G1 arm 1 events: no span
- G1 arm 1 total: no span
- G2 arm 1: events not an integer (None)
- G3 arm 1: denominator not stated as a number (basis NOT_STATED; a percentage '37.5%' does not stand in)
- G4 not evaluated: an arm's events or denominator is not bound to a printed number (G1-G3), so no comparison with the served slots is made -- SET_ASIDE, not a served-number difference
- extractor note: Both arms received clomifene citrate; the randomized additions were placebo or metformin 850 mg two times a day all ovulatory cycle for three trials maximum. The source prints only ovulation percentages (62.5% metformin; 37.5% placebo), with 32 women equally allocated overall. It does not print arm-specific event counts or numeric denominators. Served events 10 and 6 and denominators 16 and 16 require calculation and are therefore not extracted.

### CD-metformin-pcos-ovulation-0-1 -- SET_ASIDE
metformin-pcos-ovulation / Ovulation with metformin added to clomifene / PMID 16769748; served {'ai': 71, 'n1i': 111, 'ci': 82, 'n2i': 114}
- G1 arm 0 events: no span
- G2 arm 0: events not an integer (None)
- G1 arm 1 events: no span
- G2 arm 1: events not an integer (None)
- G4 not evaluated: an arm's events or denominator is not bound to a printed number (G1-G3), so no comparison with the served slots is made -- SET_ASIDE, not a served-number difference
- extractor note: NOT_IN_PACKET: Per-arm ovulation event counts and assessment window are not stated in the held documents. Only ovulation rates of 64% and 72% are printed; served event counts 71 and 82 are reconstructed in row.json and are not source-stated counts. The allocated arm totals 111 and 114 match the served denominators. The abstract reports 228 participants but does not explain the discrepancy with the stated arm allocations. The held XML contains the abstract, not the full study body, and references a correction whose text is not in the packet.

## Bound rows

| row | outcome | experimental (ai/n1i) | comparator (ci/n2i) | events own. | total own. |
|---|---|---|---|---|---|
| CD-balanced-crystalloids-vs-saline-mortality-0-0 | Mortality | BMES group `NCT02721654:433771710` 530/2433 | saline group `NCT02721654:433771711` 530/2413 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-balanced-crystalloids-vs-saline-mortality-2-0 | New renal-replacement therapy | BMES group `NCT02721654:433771710` 306/2403 | saline group `NCT02721654:433771711` 310/2394 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-colchicine-postop-af-0-1 | Postoperative atrial fibrillation | colchicine group `NCT03015831:434536836` 13/81 | placebo group `NCT03015831:434536837` 13/71 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-colchicine-postop-af-0-2 | Postoperative atrial fibrillation | colchicine `NCT01552187:433747261` 61/180 | placebo `NCT01552187:433747260` 75/180 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-colchicine-secondary-cv-prevention-1-0 | Gastrointestinal adverse effects | colchicine group `SYN-981b057cb68a#arm:colchicine-group` 15/120 | placebo group `SYN-981b057cb68a#arm:placebo-group` 3/129 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-corticosteroids-cap-mortality-0-0 | All-cause mortality | hydrocortisone group `NCT02517489:433866255` 25/400 | placebo group `NCT02517489:433866256` 47/395 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-corticosteroids-cap-mortality-0-1 | All-cause mortality | methylprednisolone group `NCT00908713:434377096` 6/61 | placebo group `NCT00908713:434377097` 9/59 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-corticosteroids-cap-mortality-1-0 | Hyperglycaemia | methylprednisolone group `NCT00908713:434377096` 11/61 | placebo group `NCT00908713:434377097` 7/59 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-corticosteroids-cap-mortality-1-1 | Hyperglycaemia | dexamethasone `NCT01743755:433658679` 14/203 | placebo `NCT01743755:433658680` 1/198 | ADJACENT_LABEL, VERSUS_ORDER | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-corticosteroids-cap-mortality-1-3 | Hyperglycaemia | dexamethasone group `NCT00471640#arm:dexamethasone-group` 67/151 | placebo group `NCT00471640#arm:placebo-group` 35/153 | ADJACENT_LABEL, ADJACENT_LABEL | PARALLEL_ORDER, ADJACENT_LABEL |
| CD-corticosteroids-covid19-mortality-1-0 | Serious adverse events | hydrocortisone `NCT04348305:434478834` 1/16 | placebo `NCT04348305:434478835` 0/14 | PARALLEL_ORDER, PARALLEL_ORDER | PARALLEL_ORDER, PARALLEL_ORDER |
| CD-dpp4-mace-t2d-1-0 | Adverse events | linagliptin `NCT01897532:434163212` 2697/3494 | placebo `NCT01897532:434163213` 2723/3485 | PARALLEL_ORDER, PARALLEL_ORDER | PARALLEL_ORDER, ADJACENT_LABEL |
| CD-dpp4-mace-t2d-2-0 | Hypoglycemia | linagliptin `NCT01897532:434163212` 1036/3494 | placebo `NCT01897532:434163213` 1024/3485 | PARALLEL_ORDER, PARALLEL_ORDER | PARALLEL_ORDER, ADJACENT_LABEL |
| CD-esketamine-trd-madrs-1-0 | Adverse events | Esketamine Plus AD `NCT03434041:433784606` 120/126 | AD Plus Placebo `NCT03434041:433784607` 89/126 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-glp1-ra-mace-t2d-1-0 | Gastrointestinal adverse events | dulaglutide `NCT01394952:433943174` 2347/4949 | placebo `NCT01394952:433943175` 1687/4952 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-glp1-ra-mace-t2d-2-0 | Adverse events leading to discontinuation | Liraglutide `NCT01179048:433876840` 444/4668 | Placebo `NCT01179048:433876841` 339/4672 | TABLE_COLUMN, TABLE_COLUMN | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-melatonin-primary-insomnia-sol-1-0 | Adverse events | PRM `NCT00397189:434062718` 136/394 | Placebo `NCT00397189:434062719` 142/395 | TABLE_COLUMN, TABLE_COLUMN | TABLE_COLUMN, TABLE_COLUMN |
| CD-metformin-pcos-ovulation-0-2 | Ovulation with metformin added to clomifene | metformin `SYN-90e1fc6ced9d#arm:metformin` 9/12 | placebo `SYN-90e1fc6ced9d#arm:placebo` 4/15 | PARALLEL_ORDER, PARALLEL_ORDER | PARALLEL_ORDER, PARALLEL_ORDER |
| CD-omega3-cardiovascular-events-1-0 | Atrial fibrillation | Omega-3 `NCT00135226:434281137+NCT00135226:434281139` 166/7740 | Placebo Omega-3 `NCT00135226:434281138+NCT00135226:434281140` 135/7740 | GROUP_ID, GROUP_ID | GROUP_ID, GROUP_ID |
| CD-probiotics-aad-prevention-0-1 | Antibiotic-associated diarrhoea | probiotic group `SYN-0419eae8aeb8#arm:probiotic-group` 106/549 | placebo group `SYN-0419eae8aeb8#arm:placebo-group` 103/577 | ADJACENT_LABEL, ADJACENT_LABEL | PARALLEL_ORDER, ADJACENT_LABEL |
| CD-probiotics-aad-prevention-0-10 | Antibiotic-associated diarrhoea | lactobacilli group `SYN-750512ad72a7#arm:lactobacilli-group` 7/44 | placebo group `SYN-750512ad72a7#arm:placebo-group` 16/45 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-probiotics-aad-prevention-0-6 | Antibiotic-associated diarrhoea | S. boulardii `SYN-962dc41d54af#arm:s-boulardii` 4/119 | placebo `SYN-962dc41d54af#arm:placebo` 22/127 | PARALLEL_ORDER, PARALLEL_ORDER | PARALLEL_ORDER, PARALLEL_ORDER |
| CD-probiotics-aad-prevention-0-7 | Antibiotic-associated diarrhoea | Lactobacillus GG `SYN-0b772df8adc9#arm:lactobacillus-gg` 39/133 | placebo `SYN-0b772df8adc9#arm:placebo` 40/134 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-probiotics-aad-prevention-0-9 | Antibiotic-associated diarrhoea | Lactobacillus group `SYN-2163745e2514#arm:lactobacillus-group` 4/103 | placebo group `SYN-2163745e2514#arm:placebo-group` 8/111 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-probiotics-aad-prevention-1-0 | Any adverse events | Active `SYN-dd9903025721#arm:active` 64/125 | Control `SYN-dd9903025721#arm:control` 69/130 | TABLE_COLUMN, TABLE_COLUMN | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-probiotics-aad-prevention-1-1 | Any adverse events | studied probiotic mix `NCT05607056:433809091` 7/285 | placebo group `NCT05607056:433809092` 3/279 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-probiotics-aad-prevention-2-0 | Serious adverse events | LcS group `SYN-23fe0dd26422#arm:lcs-group` 4/181 | Placebo group `SYN-23fe0dd26422#arm:placebo-group` 6/178 | ADJACENT_LABEL, ADJACENT_LABEL | PARALLEL_ORDER, ADJACENT_LABEL |
| CD-semaglutide-obesity-mace-2-0 | Adverse events leading to permanent discontinuation | semaglutide group `NCT03574597:434483400` 1461/8803 | placebo group `NCT03574597:434483401` 718/8801 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-sglt2-ckd-progression-1-0 | Diabetic ketoacidosis | empagliflozin group `NCT03594110:434295166` 6/3304 | placebo group `NCT03594110:434295167` 1/3305 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-ticagrelor-vs-clopidogrel-acs-1-0 | Major bleeding | TICAGRELOR `NCT00391872:434047372` 961/9235 | CLOPIDOGREL `NCT00391872:434047371` 929/9186 | GROUP_ID, GROUP_ID | GROUP_ID, GROUP_ID |
| CD-tocilizumab-covid19-mortality-1-0 | Serious adverse events | tocilizumab group `NCT04320615:434518319` 103/295 | placebo group `NCT04320615:434518320` 55/143 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |
| CD-tocilizumab-covid19-mortality-1-1 | Serious adverse events | tocilizumab group `NCT04372186:434660337` 38/250 | placebo group `NCT04372186:434660336` 25/127 | ADJACENT_LABEL, ADJACENT_LABEL | ADJACENT_LABEL, ADJACENT_LABEL |

## Limits

- Ownership relations are text heuristics with named rules (`scripts/ownership.py`), tested on synthetic plants; they refuse rather than guess, and a refusal is a SET_ASIDE, not a finding about the trial.
- `SOURCE_LABEL` arm ids are identities within the trial's own report, not registry identities; they are typed as such and counted separately above.
- The main lane's typed schema was on no pushed branch when this was built; each arm names its served F4B slot so the records can be re-keyed onto that schema without re-extraction.
