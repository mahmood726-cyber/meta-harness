# evid2 DATA for the F4 count-observation schema v1 -- report

Population: **34** held count entries (`objects in cache/<slug>/verified_arms.json carrying ai, n1i, ci, n2i (the F4 schema's 34)`) at `1aaeb80c` -- the F4 lane's 34, reproduced exactly (18 files; 0 carried comparator_direction, 0 carried observations). Kinds: hand entries only; no controls. 19 of them are also served count rows typed in `../records/`; 15 are hand entries not served today. (The 35 served rows typed earlier include 16 machine-extracted rows that have no held entry.)

## What evid2 supplies per entry

- `comparator_direction`: `"<intervention arm> vs <comparator arm>"` in the SOURCE's own arm names -- only where evid2's independent gate BOUND both arms (G1-G7).
- `observations`: the F4 producer's OWN computed objects, byte for byte, and only where (a) the producer bound the entry with that direction and (b) every arm's (role, events, n) equals evid2's (slot, events, total). `observation_mismatch()` compares supplied to re-extracted by equality, so a hand-built object would be refused.
- nothing else: `contrast` is a policy statement about the configured orientation, the F4 lane's to set.

## Counts

evid2's own evidence, over the 34: BOUND 27, SET_ASIDE 7
comparator_direction supplied: **27 of 34**
observations supplied (two instruments agree): **5 of 34**
F4 producer with evid2's directions: NOT_POOLED/None/['COUNT_EVENT_ARM_UNBOUND']: 15; NOT_POOLED/None/['ENDPOINT_UNBOUND']: 11; POOLED/BOUND/None: 5; NOT_POOLED/None/['RESULT_INCOMPATIBLE']: 1; NOT_POOLED/None/['COUNT_DENOMINATOR_UNBOUND']: 1; POOLED/None/None: 1

## Where the F4 grammar abstains but evid2's gate binds (the shapes, for the F4 lane)

| entry | producer code | evid2 events ownership | events span (evid2) |
|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality/29485925 | ['ENDPOINT_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | A total of 818 patients (10.3%) in the balanced-crystalloids group died before hospital discharge and within 30 days of ICU admission as compared with 875 patie |
| colchicine-postop-af/27502857 | ['ENDPOINT_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | 26 (14.5%) in the colchicine group |
| colchicine-postop-af/32720823 | ['COUNT_EVENT_ARM_UNBOUND'] | EACH_GROUP, EACH_GROUP | Diarrhea occurred in two patients in each group and necessitated treatment discontinuation in one patient in each group. |
| colchicine-recurrent-pericarditis/24694983 | ['ENDPOINT_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | gastrointestinal intolerance (nine patients in the colchicine group vs nine in the placebo group) |
| corticosteroids-cap-mortality/33446608 | ['COUNT_EVENT_ARM_UNBOUND'] | ADJACENT_LABEL, VERSUS_ORDER | In the dexamethasone group the rate of hospital readmission tended to be higher (20 (10%) versus 9 (5%); p=0.051) and hyperglycaemia (14 (7%) versus 1 (1%); p=0 |
| corticosteroids-covid19-mortality/34138478 | ['COUNT_EVENT_ARM_UNBOUND'] | PARALLEL_ORDER, PARALLEL_ORDER | hydrocortisone vs placebo group were 7 vs 10 (adjusted mean difference: -1.1 days, 95% CI -9.5 to 7.3, P = .79); mortality was 6/16 vs 2/14; and the number of s |
| dpp4-mace-t2d/30418475/0 | ['COUNT_EVENT_ARM_UNBOUND'] | PARALLEL_ORDER, PARALLEL_ORDER | Adverse events occurred in 2697 (77.2%) and 2723 (78.1%) patients in the linagliptin and placebo groups |
| dpp4-mace-t2d/30418475/1 | ['COUNT_EVENT_ARM_UNBOUND'] | PARALLEL_ORDER, PARALLEL_ORDER | Adverse events occurred in 2697 (77.2%) and 2723 (78.1%) patients in the linagliptin and placebo groups; 1036 (29.7%) and 1024 (29.4%) had 1 or more episodes of |
| esketamine-trd-madrs/37025256 | ['COUNT_EVENT_ARM_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | Overall, 120 (95.2%) esketamine-treated patients and 89 (70.6%) placebo-treated patients experienced 1 or more TEAEs in the double-blind phase |
| glp1-ra-mace-t2d/27295427 | ['COUNT_EVENT_ARM_UNBOUND'] | TABLE_COLUMN, TABLE_COLUMN | Any adverse event</td><td align="center" valign="top" rowspan="1" colspan="1">444 (9.5)</td><td align="center" valign="top" rowspan="1" colspan="1">339 (7.3) |
| melatonin-primary-insomnia-sol/20712869 | ['COUNT_EVENT_ARM_UNBOUND'] | TABLE_COLUMN, TABLE_COLUMN | <td align="left" colspan="1" rowspan="1">Any AE</td><td align="left" colspan="1" rowspan="1">136 (34.5%)</td> |
| pcsk9-mace/41211925 | ['RESULT_INCOMPATIBLE'] | ADJACENT_LABEL, ADJACENT_LABEL | A 3-point MACE event occurred in 336 patients (5-year Kaplan-Meier estimate, 6.2%) in the evolocumab group |
| pcsk9-mace/25773378 | ['ENDPOINT_UNBOUND'] | AACT_GROUP, AACT_GROUP | "subjects_affected": "91",
      "subjects_at_risk": "1550" |
| probiotics-aad-prevention/39529939/0 | ['COUNT_EVENT_ARM_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | Of the participants receiving the studied probiotic mix, 9.2% (26/282) developed AAD |
| probiotics-aad-prevention/39529939/1 | ['COUNT_EVENT_ARM_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | 2.5% (7/285) in the studied probiotic mix |
| probiotics-aad-prevention/39529939/2 | ['COUNT_EVENT_ARM_UNBOUND'] | ADJACENT_LABEL, TABLE_COLUMN | One participant in the studied probiotic mix group (0.4%; 1/285) experienced a serious AE of total hysterectomy for which hospitalization was required. |
| probiotics-aad-prevention/15740542/0 | ['ENDPOINT_UNBOUND'] | PARALLEL_ORDER, PARALLEL_ORDER | S. boulardii also reduced the risk of antibiotic-associated diarrhoea (diarrhoea caused by Clostridium difficile or otherwise unexplained diarrhoea) compared wi |
| probiotics-aad-prevention/18026577/0 | ['ENDPOINT_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | seven of 44 patients (15.9%) in the lactobacilli group |
| probiotics-aad-prevention/34541475/0 | ['COUNT_EVENT_ARM_UNBOUND'] | TABLE_COLUMN, TABLE_COLUMN | AAD – Abx+30d (n, %)</td><td valign="top" colspan="1" rowspan="1">257 (102, 28.4%)</td><td valign="top" colspan="1" rowspan="1">45% (59 / 131)</td><td valign="t |
| sglt2-ckd-progression/36331190 | ['COUNT_DENOMINATOR_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | Ketoacidosis occurred in 6 patients in the empagliflozin group versus 1 patient in the placebo group (0.09 versus 0.02 per 100 patient-years). |
| spironolactone-hfref-mortality/28824029 | None | ADJACENT_LABEL, ADJACENT_LABEL | A total of 17 patients (15.3%) in the eplerenone group and 10 patients (9.1%) in the placebo group died. |
| tocilizumab-covid19-mortality/33085857 | ['ENDPOINT_UNBOUND'] | ADJACENT_LABEL, ADJACENT_LABEL | There were 36 serious adverse events in the tocilizumab group, occurring in a total of 28 patients. |

## Entries without a direction, with evid2's reasons

- **dapagliflozin-hfpef-hosp/34711976** (Adverse events; SET_ASIDE): G1 arm 0 total: no span; G3 arm 0: denominator not stated as a number (basis NOT_STATED; a percentage '27.2%' does not stand in); G1 arm 1 total: no span
- **metformin-pcos-ovulation/16769748** (Ovulation with metformin added to clomifene; SET_ASIDE): G1 arm 0 events: no span; G2 arm 0: events not an integer (None); G1 arm 1 events: no span
- **metformin-pcos-ovulation/19522426** (Ovulation with metformin added to clomifene; SET_ASIDE): G1 arm 0 events: no span; G1 arm 0 total: no span; G2 arm 0: events not an integer (None)
- **probiotics-aad-prevention/24456384** (Antibiotic-associated diarrhoea; SET_ASIDE): G1 arm 0 events: no span; G2 arm 0: events not an integer (None); G1 arm 1 events: no span
- **probiotics-aad-prevention/26973849/0** (Antibiotic-associated diarrhoea; SET_ASIDE): EVID2 RULING (by eye): EVENTS_DERIVED_NOT_PRINTED: the extracted 21 and 19 are AAD EPISODES ('with 21 and 19 AADs in the respective groups'), not participants. The held 17 is participants with >=1 epi; G4 source (events,total) pairs do not map one-to-one onto the served F4B slots -- a served number or the arm direction differs from the held source
- **probiotics-aad-prevention/26973849/1** (Any adverse events; SET_ASIDE): G7 arm 0: events 18 are printed in the span but the text does not tie them to 'S boulardii group' (OWNERSHIP_UNVERIFIED)
- **tranexamic-acid-pph/28456509** (Thromboembolic events; SET_ASIDE): G1 arm 0 events: no span; G2 arm 0: events not an integer (None); G1 arm 1 events: no span

## Limits

- The producer run is a RECONSTRUCTION of the F4 tree (RECONSTRUCTION.md: 72 of 74 of its tests, both failures explained); the F4 lane's own code re-derives every observation when it lands.
- Nothing here edits `cache/`: `F4B_DATA.json` is an overlay for the F4 lane to apply with its code. Supplying a direction can change which rows bind, and therefore a served page -- that landing is theirs and is a result change to be noticed and signed, not evid2's to make.
