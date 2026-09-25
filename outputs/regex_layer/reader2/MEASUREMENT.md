# Regex layer R2 -- per-pattern precision / recall (harness/extract.py)

Labels: recorded model proposals (registry/model_proposals/regex_label.json), gated by `regex_layer.measure.verify_label`; **not countersigned**. Precision on the sample where the pattern fires; recall is SAMPLED recall (sentences with no trigger word are never examined).

Patterns measured: 23 of 23.

| pattern | kind | role in harness/ | measured of frozen | precision | sampled recall | labels stable on re-ask | pools fires / trigger-only |
|---|---|---|---|---|---|---|---|
| `_ANCHOR_RX` | classifier | conjunct:_DEF_CUE | 30 of 30 | 10 of 15 | 10 of 10 | 0 of 0 | 879 / 3072 |
| `_ARM` | extractor | standalone | 30 of 30 | 26 of 27 | 26 of 30 | 0 of 0 | 47 / 4767 |
| `_ARM2` | extractor | standalone | 30 of 30 | 34 of 34 | 34 of 51 | 0 of 0 | 25 / 196 |
| `_ARM3` | extractor | standalone | 30 of 30 | 29 of 29 | 29 of 31 | 0 of 0 | 90 / 1555 |
| `_ARM4` | extractor | standalone | 30 of 30 | 18 of 21 | 18 of 20 | 0 of 0 | 78 / 311 |
| `_ARMP` | extractor | standalone | 30 of 30 | 19 of 29 | 19 of 25 | 0 of 0 | 605 / 4209 |
| `_COMPOSITE_ENDPOINT` | classifier | standalone | 30 of 30 | 12 of 15 | 12 of 12 | 0 of 0 | 717 / 4736 |
| `_DEF_CUE` | classifier | conjunct:_ANCHOR_RX | 30 of 30 | 1 of 15 | 1 of 1 | 0 of 0 | 19533 / 16140 |
| `_DENOM_EACH` | extractor | standalone | 18 of 18 | 3 of 3 | 3 of 3 | 0 of 0 | 3 / 394 |
| `_DOSE_ARM` | extractor | dead | 22 of 22 | 7 of 23 | 7 of 22 | 0 of 0 | 1089 / 7 |
| `_EFFECT` | extractor | standalone | 30 of 30 | 24 of 26 | 24 of 30 | 0 of 0 | 1448 / 940 |
| `_FACTORIAL` | classifier | standalone | 30 of 30 | 15 of 15 | 15 of 15 | 0 of 0 | 26 / 3465 |
| `_K` | extractor | standalone | 29 of 30 | 2 of 14 | 2 of 12 | 0 of 0 | 1168 / 3738 |
| `_MEAN_SD` | extractor | standalone | 30 of 30 | 32 of 34 | 32 of 51 | 0 of 0 | 360 / 138 |
| `_MED_IQR` | extractor | standalone | 16 of 16 | 1 of 1 | 1 of 18 | 0 of 0 | 1 / 127 |
| `_MORT_D` | classifier | dead | 30 of 30 | 15 of 15 | 15 of 15 | 0 of 0 | 852 / 84 |
| `_MORT_Y` | classifier | dead | 15 of 15 | 15 of 15 | 15 of 15 | 0 of 0 | 1410 / 0 |
| `_NEQ` | extractor | standalone | 30 of 30 | 15 of 22 | 15 of 17 | 0 of 0 | 647 / 226 |
| `_NULL_RESULT` | classifier | standalone | 30 of 30 | 14 of 15 | 14 of 18 | 0 of 0 | 686 / 4117 |
| `_RATE_EVPT` | extractor | standalone | 30 of 30 | 0 of 28 | 0 of 13 | 0 of 0 | 15 / 54 |
| `_RATE_UNIT` | extractor | dead | 30 of 30 | 20 of 25 | 20 of 31 | 0 of 0 | 38 / 473 |
| `_RECURRENT_PERSONTIME` | classifier | standalone | 30 of 30 | 10 of 15 | 10 of 13 | 0 of 0 | 113 / 1987 |
| `_SUBGROUP` | classifier | standalone | 30 of 30 | 11 of 15 | 11 of 15 | 0 of 0 | 583 / 2028 |

Role: `dead` = no reader in harness/ (its numbers cannot move a served value); `conjunct:P` = read only together with P, so its standalone precision is not its contract.

Unmeasured items by state (never dropped):

- `_K`: {'VERIFIER_REFUSED': 1}
