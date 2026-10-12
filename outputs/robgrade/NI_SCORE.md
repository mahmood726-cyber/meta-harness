# NI policy on TEST: agreement with the published per-trial risk-of-bias judgements, n of N

Pre-registered policy: commit c2a27057db2222fdd1f56f0674a784c35ca4fa71 (outputs/robgrade/NI_POLICY.md). Engine v3.1 = v3 with the three algorithm corrections the review found against the RoB 2 guidance tables (D2 2.4/2.7 NI, D4 4.1 NI).

Comparators and their tools (a RoB 1 table mapped to RoB 2 domains is an approximation, Handbook 8.8): balanced-crystalloids-vs-saline-mortality: ?; iv-iron-hfref-hosp: Not stated; probiotics-aad-prevention: ?; ticagrelor-vs-clopidogrel-acs: ?.
Coverage: 40 trial-domain records excluded (ours INSUFFICIENT_OPEN_SOURCE, or the reference cell unresolved), 9 trials not bound to exactly one reference row. Not counted in any N below.

A comparator row is matched to our trial by PMID only: result identity (the same outcome, time point and numerical result) is NOT verified, so these counts do not establish agreement on the same result (RoB 2 rates a result; Handbook 8.2.1).

Excluding NI-driven pairs is a STRATUM, not an improvement: it is always shown with the full count and the NI-driven pairs themselves. The policy changes no judgement (each pair's judgement and label are recomputed from its stored answers).

| domain | all pairs | excluding NI-driven | NI-driven only |
|---|---|---|---|
| D1 | 25 / 45 | 3 / 5 | 22 / 40 |
| D2 | 15 / 47 | 14 / 15 | 1 / 32 |
| D3 | 12 / 37 | 8 / 9 | 4 / 28 |
| D4 | 15 / 46 | 14 / 14 | 1 / 32 |
| D5 | 2 / 35 | 0 / 0 | 2 / 35 |
| all | 69 / 210 | 39 / 43 | 30 / 167 |

Algorithm corrections v3 -> v3.1, on the identical 210 pairs: 35 judgements moved; agreement 71 / 210 under v3, 69 / 210 under v3.1 (0 scored pairs have no identical v3 pair).
- balanced-crystalloids-vs-saline-mortality 23732264 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- balanced-crystalloids-vs-saline-mortality 27604335 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- iv-iron-hfref-hosp 19920054 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- iv-iron-hfref-hosp 33197395 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- iv-iron-hfref-hosp 33197395 D4: SOME_CONCERNS -> LOW (comparator LOW)
- iv-iron-hfref-hosp 37632463 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 111546 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 14627358 D2: SOME_CONCERNS -> HIGH (comparator HIGH)
- probiotics-aad-prevention 15179608 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 16292090 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
- probiotics-aad-prevention 16572062 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 17356555 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 17669103 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 17900321 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 18402597 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
- probiotics-aad-prevention 18949181 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 19138244 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 20145608 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 22472744 D4: SOME_CONCERNS -> LOW (comparator LOW)
- probiotics-aad-prevention 23932219 D4: SOME_CONCERNS -> LOW (comparator LOW)
- probiotics-aad-prevention 24456384 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 24772726 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 2494098 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 32035998 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 32944084 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
- probiotics-aad-prevention 7872284 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- probiotics-aad-prevention 7872284 D4: SOME_CONCERNS -> LOW (comparator LOW)
- probiotics-aad-prevention 9570649 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- ticagrelor-vs-clopidogrel-acs 17980250 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
- ticagrelor-vs-clopidogrel-acs 19717846 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- ticagrelor-vs-clopidogrel-acs 19923168 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- ticagrelor-vs-clopidogrel-acs 23500251 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
- ticagrelor-vs-clopidogrel-acs 24333493 D2: SOME_CONCERNS -> HIGH (comparator LOW)
- ticagrelor-vs-clopidogrel-acs 24482383 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
- ticagrelor-vs-clopidogrel-acs 26440227 D2: SOME_CONCERNS -> HIGH (comparator SOME_CONCERNS)
