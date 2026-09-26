# R2 on held sentences 41-80 per pool -- blind Claude labels

**Labels by blind Claude subagents (no regex, no model CLI); NOT recorded model calls, not replayable; gated by regex_layer.measure.verify_label; never mixed with the recorded-proposal measurement.**

Items 1473; labelled 1473; verifier pass 1473; refused 0; missing 0.

Calibration -- the same blind labeller on items the recorded first reader already labelled: agrees on **132 of 138**.

| pattern | sample fires / trigger-only | precision | sampled recall | calibration agreement |
|---|---|---|---|---|
| `_ANCHOR_RX` | 40 / 40 | 40 of 40 | 40 of 46 | 6 of 6 |
| `_ARM` | 6 / 40 | 11 of 11 | 11 of 11 | 6 of 6 |
| `_ARM2` | 0 / 40 | undefined (no firing items in 41-80) | n/a -- 59 misses found | 5 of 6 |
| `_ARM3` | 40 / 40 | 84 of 84 | 84 of 88 | 6 of 6 |
| `_ARM4` | 38 / 40 | 64 of 64 | 64 of 80 | 5 of 6 |
| `_ARMP` | 40 / 40 | 48 of 68 | 48 of 53 | 5 of 6 |
| `_COMPOSITE_ENDPOINT` | 40 / 40 | 39 of 40 | 39 of 42 | 6 of 6 |
| `_DEF_CUE` | 40 / 40 | 2 of 40 | 2 of 2 | 6 of 6 |
| `_DENOM_EACH` | 0 / 40 | undefined (no firing items in 41-80) | n/a -- 4 misses found | 6 of 6 |
| `_DOSE_ARM` | 40 / 0 | 41 of 61 | 41 of 45 | 6 of 6 |
| `_EFFECT` | 40 / 40 | 68 of 72 | 68 of 94 | 6 of 6 |
| `_FACTORIAL` | 0 / 40 | undefined (no firing items in 41-80) | n/a -- 0 misses found | 6 of 6 |
| `_K` | 40 / 40 | 15 of 48 | 15 of 17 | 6 of 6 |
| `_MEAN_SD` | 40 / 40 | 91 of 94 | 91 of 133 | 6 of 6 |
| `_MED_IQR` | 0 / 40 | undefined (no firing items in 41-80) | n/a -- 59 misses found | 6 of 6 |
| `_MORT_D` | 40 / 40 | 40 of 40 | 40 of 40 | 6 of 6 |
| `_MORT_Y` | 40 / 0 | 40 of 40 | 40 of 40 | 6 of 6 |
| `_NEQ` | 40 / 40 | 59 of 59 | 59 of 67 | 5 of 6 |
| `_NULL_RESULT` | 40 / 40 | 38 of 40 | 38 of 42 | 6 of 6 |
| `_RATE_EVPT` | 0 / 29 | undefined (no firing items in 41-80) | n/a -- 2 misses found | 6 of 6 |
| `_RATE_UNIT` | 0 / 40 | undefined (no firing items in 41-80) | n/a -- 18 misses found | 4 of 6 |
| `_RECURRENT_PERSONTIME` | 40 / 40 | 31 of 40 | 31 of 33 | 6 of 6 |
| `_SUBGROUP` | 40 / 40 | 26 of 40 | 26 of 28 | 6 of 6 |

Where the firing pool was exhausted before item 41, every item here is one the regex does not fire on: precision is undefined and each labelled instance is a MISS FOUND, not a recall -- combine with the recorded first-15/16-40 samples (MEASUREMENT.md) for a sampled recall.
