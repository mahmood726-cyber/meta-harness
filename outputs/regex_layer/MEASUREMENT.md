# Regex layer R2 -- per-pattern precision / recall (harness/extract.py)

Labels: recorded model proposals (registry/model_proposals/regex_label.json), gated by `regex_layer.measure.verify_label`; **not countersigned**. Precision on the sample where the pattern fires; recall is SAMPLED recall (sentences with no trigger word are never examined).

Patterns measured: 23 of 23.

| pattern | kind | role in harness/ | measured of frozen | precision | sampled recall | labels stable on re-ask | pools fires / trigger-only |
|---|---|---|---|---|---|---|---|
| `_ANCHOR_RX` | classifier | conjunct:_DEF_CUE | 30 of 30 | 11 of 15 | 11 of 11 | 30 of 30 | 879 / 3072 |
| `_ARM` | extractor | standalone | 30 of 30 | 26 of 27 | 26 of 30 | 30 of 30 | 47 / 4767 |
| `_ARM2` | extractor | standalone | 30 of 30 | 34 of 34 | 34 of 34 | 30 of 30 | 25 / 196 |
| `_ARM3` | extractor | standalone | 30 of 30 | 29 of 29 | 29 of 31 | 30 of 30 | 90 / 1555 |
| `_ARM4` | extractor | standalone | 30 of 30 | 20 of 21 | 20 of 22 | 30 of 30 | 78 / 311 |
| `_ARMP` | extractor | standalone | 30 of 30 | 19 of 29 | 19 of 21 | 30 of 30 | 605 / 4209 |
| `_COMPOSITE_ENDPOINT` | classifier | standalone | 30 of 30 | 13 of 15 | 13 of 13 | 29 of 30 | 717 / 4736 |
| `_DEF_CUE` | classifier | conjunct:_ANCHOR_RX | 30 of 30 | 1 of 15 | 1 of 1 | 30 of 30 | 19533 / 16140 |
| `_DENOM_EACH` | extractor | standalone | 18 of 18 | 3 of 3 | 3 of 3 | 18 of 18 | 3 / 394 |
| `_DOSE_ARM` | extractor | dead | 22 of 22 | 21 of 23 | 21 of 22 | 22 of 22 | 1089 / 7 |
| `_EFFECT` | extractor | standalone | 30 of 30 | 26 of 26 | 26 of 33 | 29 of 30 | 1448 / 940 |
| `_FACTORIAL` | classifier | standalone | 30 of 30 | 15 of 15 | 15 of 15 | 30 of 30 | 26 / 3465 |
| `_K` | extractor | standalone | 30 of 30 | 3 of 15 | 3 of 9 | 29 of 30 | 1168 / 3738 |
| `_MEAN_SD` | extractor | standalone | 30 of 30 | 33 of 34 | 33 of 54 | 29 of 30 | 360 / 138 |
| `_MED_IQR` | extractor | standalone | 16 of 16 | 1 of 1 | 1 of 18 | 16 of 16 | 1 / 127 |
| `_MORT_D` | classifier | dead | 30 of 30 | 15 of 15 | 15 of 15 | 30 of 30 | 852 / 84 |
| `_MORT_Y` | classifier | dead | 15 of 15 | 15 of 15 | 15 of 15 | 15 of 15 | 1410 / 0 |
| `_NEQ` | extractor | standalone | 30 of 30 | 16 of 22 | 16 of 18 | 30 of 30 | 647 / 226 |
| `_NULL_RESULT` | classifier | standalone | 30 of 30 | 14 of 15 | 14 of 18 | 30 of 30 | 686 / 4117 |
| `_RATE_EVPT` | extractor | standalone | 30 of 30 | 0 of 28 | 0 of 1 | 30 of 30 | 15 / 54 |
| `_RATE_UNIT` | extractor | dead | 30 of 30 | 20 of 25 | 20 of 31 | 29 of 30 | 38 / 473 |
| `_RECURRENT_PERSONTIME` | classifier | standalone | 30 of 30 | 10 of 15 | 10 of 13 | 30 of 30 | 113 / 1987 |
| `_SUBGROUP` | classifier | standalone | 30 of 30 | 8 of 15 | 8 of 8 | 30 of 30 | 583 / 2028 |

Role: `dead` = no reader in harness/ (its numbers cannot move a served value); `conjunct:P` = read only together with P, so its standalone precision is not its contract.

Unmeasured items by state (never dropped):

