# Regex layer scorecard (derived by `python -m regex_layer.scorecard`)

| property | harness/extract.py (23 compiled patterns) |
|---|---|
| R1 | **9 of 23 (14 not applicable, 0 open)** |
| R2 | **23 of 23** |
| R3 | **23 of 23** |
| R4 | **11 of 23 (12 not applicable, 0 open)** |

Harness-wide: R3_harness_sites_planted 407 of 407; R2_other_sites_measured 95 of 367

| pattern | kind / role | R1 | R2 | R3 | R4 |
|---|---|---|---|---|---|
| `_ANCHOR_RX` | classifier / conjunct:_DEF_CUE | n/a: classifier: returns a bool | yes: P 31 of 40, sampled R 31 of 34 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
| `_ARM` | extractor / standalone | yes: extract_arm_counts builds ArmHit | yes: P 69 of 75, sampled R 69 of 80 (80 labels) | yes: 1 accept / 2 refuse plants | yes: number fragments refused (whole_numbers) |
| `_ARM2` | extractor / standalone | yes: extract_arm_counts builds ArmHit | yes: P 51 of 54, sampled R 51 of 64 (65 labels) | yes: 1 accept / 2 refuse plants | yes: number fragments refused (whole_numbers) |
| `_ARM3` | extractor / standalone | yes: extract_arm_counts builds ArmHit | yes: P 72 of 72, sampled R 72 of 83 (80 labels) | yes: 1 accept / 2 refuse plants | yes: number fragments refused (whole_numbers) |
| `_ARM4` | extractor / standalone | yes: extract_arm_counts builds ArmHit | yes: P 62 of 69, sampled R 62 of 66 (80 labels) | yes: 1 accept / 2 refuse plants | yes: number fragments refused (whole_numbers) |
| `_ARMP` | extractor / standalone | yes: extract_arm_counts builds ArmPercentHit | yes: P 48 of 79, sampled R 48 of 54 (80 labels) | yes: 1 accept / 2 refuse plants | yes: number fragments refused (whole_numbers) |
| `_COMPOSITE_ENDPOINT` | classifier / standalone | n/a: classifier: returns a bool | yes: P 37 of 40, sampled R 37 of 37 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
| `_DEF_CUE` | classifier / conjunct:_ANCHOR_RX | n/a: classifier: returns a bool | yes: P 1 of 40, sampled R 1 of 2 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
| `_DENOM_EACH` | extractor / standalone | n/a: one integer (a denominator), not a tuple | yes: P 3 of 3, sampled R 3 of 4 (43 labels) | yes: 1 accept / 1 refuse plants | yes: number fragments refused (whole_numbers) |
| `_DOSE_ARM` | extractor / dead | n/a: dead: no reader in harness/ | yes: P 53 of 60, sampled R 53 of 58 (47 labels) | yes: 1 accept / 1 refuse plants | n/a: dead: no reader in harness/ |
| `_EFFECT` | extractor / standalone | yes: extract_effect>_effect_from_match builds Effect | yes: P 69 of 69, sampled R 69 of 82 (80 labels) | yes: 1 accept / 2 refuse plants | n/a: left unwrapped: also read by absence.py / reason_audit.py (other lane); 0 fragments in held text |
| `_FACTORIAL` | classifier / standalone | n/a: classifier: returns a bool | yes: P 23 of 26, sampled R 23 of 23 (66 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
| `_K` | extractor / standalone | n/a: one integer (a trial count), not a tuple | yes: P 11 of 41, sampled R 11 of 27 (80 labels) | yes: 1 accept / 1 refuse plants | yes: number fragments refused (whole_numbers) |
| `_MEAN_SD` | extractor / standalone | yes: extract_continuous builds MeanSDHit | yes: P 87 of 100, sampled R 87 of 133 (80 labels) | yes: 2 accept / 1 refuse plants | yes: number fragments refused (whole_numbers) |
| `_MED_IQR` | extractor / standalone | yes: extract_continuous builds MeanSDHit | yes: P 1 of 1, sampled R 1 of 50 (41 labels) | yes: 1 accept / 1 refuse plants | yes: number fragments refused (whole_numbers) |
| `_MORT_D` | classifier / dead | n/a: dead: no reader in harness/ | yes: P 40 of 40, sampled R 40 of 40 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: dead: no reader in harness/ |
| `_MORT_Y` | classifier / dead | n/a: dead: no reader in harness/ | yes: P 40 of 40, sampled R 40 of 40 (40 labels) | yes: 1 accept / 1 refuse plants | n/a: dead: no reader in harness/ |
| `_NEQ` | extractor / standalone | n/a: integers (sample sizes), not a tuple | yes: P 54 of 56, sampled R 54 of 64 (80 labels) | yes: 1 accept / 4 refuse plants | yes: number fragments refused (whole_numbers) |
| `_NULL_RESULT` | classifier / standalone | n/a: classifier: returns a bool | yes: P 39 of 40, sampled R 39 of 48 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
| `_RATE_EVPT` | extractor / standalone | yes: extract_rate builds RateHit | yes: P 0 of 0, sampled R 0 of 4 (55 labels) | yes: 1 accept / 1 refuse plants | yes: number fragments refused (whole_numbers) |
| `_RATE_UNIT` | extractor / dead | n/a: dead: no reader in harness/ | yes: P 61 of 70, sampled R 61 of 86 (78 labels) | yes: 1 accept / 1 refuse plants | n/a: dead: no reader in harness/ |
| `_RECURRENT_PERSONTIME` | classifier / standalone | n/a: classifier: returns a bool | yes: P 28 of 40, sampled R 28 of 33 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
| `_SUBGROUP` | classifier / standalone | n/a: classifier: returns a bool | yes: P 24 of 40, sampled R 24 of 27 (80 labels) | yes: 1 accept / 1 refuse plants | n/a: classifier: captures no number |
