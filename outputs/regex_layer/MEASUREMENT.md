# Regex layer R2 -- per-pattern precision / recall (harness/extract.py)

Labels: recorded model proposals (registry/model_proposals/regex_label.json), gated by `regex_layer.measure.verify_label`; **not countersigned**. Precision on the sample where the pattern fires; recall is SAMPLED recall (sentences with no trigger word are never examined).

Patterns measured: 23 of 23.

| pattern | kind | role in harness/ | measured of frozen | precision | sampled recall | labels stable on re-ask | pools fires / trigger-only |
|---|---|---|---|---|---|---|---|
| `_ANCHOR_RX` | classifier | conjunct:_DEF_CUE | 80 of 80 | 31 of 40 | 31 of 34 | 80 of 80 | 879 / 3072 |
| `_ARM` | extractor | standalone | 80 of 80 | 69 of 75 | 69 of 80 | 80 of 80 | 46 / 4768 |
| `_ARM2` | extractor | standalone | 65 of 65 | 51 of 54 | 51 of 64 | 54 of 65 | 25 / 196 |
| `_ARM3` | extractor | standalone | 80 of 80 | 72 of 72 | 72 of 83 | 79 of 80 | 90 / 1555 |
| `_ARM4` | extractor | standalone | 80 of 80 | 62 of 69 | 62 of 66 | 79 of 80 | 78 / 311 |
| `_ARMP` | extractor | standalone | 80 of 80 | 48 of 79 | 48 of 54 | 80 of 80 | 574 / 4240 |
| `_COMPOSITE_ENDPOINT` | classifier | standalone | 80 of 80 | 37 of 40 | 37 of 37 | 79 of 80 | 717 / 4736 |
| `_DEF_CUE` | classifier | conjunct:_ANCHOR_RX | 80 of 80 | 1 of 40 | 1 of 2 | 80 of 80 | 19533 / 16140 |
| `_DENOM_EACH` | extractor | standalone | 43 of 43 | 3 of 3 | 3 of 4 | 43 of 43 | 3 / 394 |
| `_DOSE_ARM` | extractor | dead | 47 of 47 | 53 of 60 | 53 of 58 | 47 of 47 | 1089 / 7 |
| `_EFFECT` | extractor | standalone | 80 of 80 | 69 of 69 | 69 of 82 | 78 of 80 | 1448 / 940 |
| `_FACTORIAL` | classifier | standalone | 66 of 66 | 23 of 26 | 23 of 23 | 66 of 66 | 26 / 3465 |
| `_K` | extractor | standalone | 80 of 80 | 11 of 41 | 11 of 27 | 76 of 80 | 1168 / 3738 |
| `_MEAN_SD` | extractor | standalone | 80 of 80 | 87 of 100 | 87 of 133 | 77 of 80 | 359 / 139 |
| `_MED_IQR` | extractor | standalone | 41 of 41 | 1 of 1 | 1 of 50 | 41 of 41 | 1 / 127 |
| `_MORT_D` | classifier | dead | 80 of 80 | 40 of 40 | 40 of 40 | 80 of 80 | 852 / 84 |
| `_MORT_Y` | classifier | dead | 40 of 40 | 40 of 40 | 40 of 40 | 40 of 40 | 1410 / 0 |
| `_NEQ` | extractor | standalone | 80 of 80 | 54 of 56 | 54 of 64 | 79 of 80 | 564 / 272 |
| `_NULL_RESULT` | classifier | standalone | 80 of 80 | 39 of 40 | 39 of 48 | 80 of 80 | 686 / 4117 |
| `_RATE_EVPT` | extractor | standalone | 55 of 55 | 0 of 0 | 0 of 4 | 55 of 55 | 0 / 69 |
| `_RATE_UNIT` | extractor | dead | 78 of 78 | 61 of 70 | 61 of 86 | 77 of 78 | 38 / 473 |
| `_RECURRENT_PERSONTIME` | classifier | standalone | 80 of 80 | 28 of 40 | 28 of 33 | 80 of 80 | 113 / 1987 |
| `_SUBGROUP` | classifier | standalone | 80 of 80 | 24 of 40 | 24 of 27 | 80 of 80 | 583 / 2028 |

Role: `dead` = no reader in harness/ (its numbers cannot move a served value); `conjunct:P` = read only together with P, so its standalone precision is not its contract.

Unmeasured items by state (never dropped):

