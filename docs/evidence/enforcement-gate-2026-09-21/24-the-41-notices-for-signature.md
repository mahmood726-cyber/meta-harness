# The 41 re-judged result-change notices — for Mahmood's signature

Re-judged 2026-09-24 under Decision B (anchor every notice to the exact version it judged, then
redo the 41 judgements once). Anchored on 41 of 41: `judged_commit` = `1fa77f2c4852ee79e55d540083e3c35bbff0cecc`.

**Nothing here is signed and no served number has moved.** The bulk acceptance Mahmood gave covers
the AI screening proposals only — not result-change notices. Each of these needs his own signature.

The hash to sign against is `notice_block_sha256`: sha256 of the rendered notice block,
whitespace-normalised, as it stands on the pinned page. Verified independently — for each notice
exactly one block on its pinned page carries that digest, and that block carries the heading built
from the notice's own outcome and date. Pages hold up to 6 blocks, so uniqueness is not automatic.


## NEEDS MAHMOOD'S JUDGEMENT — individual review required — 10 of 41

**N06  corticosteroids-cap-mortality / Hyperglycaemia**
- (k=4, INCOMPATIBLE (ODDS_RATIO + RISK_RATIO), estimate=None, CI=[None, None]) -> (k=2, RR, estimate=3.7445, CI=[None, None])
- direction: RESULT_ADDED; conclusion changed: True
- hash to sign: `5b493d9239d46094aa01528209915e28849c4185fde007a16a31dc35b09b08a3`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/corticosteroids-cap-mortality/index.html` (sha256 `7f83b7f5bf06ba2a…`)

**N17  dpp4-mace-t2d / 3-point major adverse cardiovascular events**
- (k=3, HR, estimate=1.0074, CI=[0.8391, 1.2094]) -> (k=1, HR, estimate=1.0, CI=[0.89, 1.12])
- direction: AWAY_FROM_NULL; conclusion changed: False; triggers: AWAY_FROM_NULL
- hash to sign: `2fa781b661905c03ea0708a0ff7b0676ad93a4dc1e40a30bcec59f6f94e1bd11`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/dpp4-mace-t2d/index.html` (sha256 `8ca0bec12cebf398…`)

**N20  esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD**
- (k=3, MD, estimate=-3.1004, CI=[-7.3323, 1.1315]) -> (k=1, MD, estimate=-4.4, CI=[-8.0296, -0.7704])
- direction: AWAY_FROM_NULL; conclusion changed: True; triggers: AWAY_FROM_NULL, NEW_FAVOURABLE_CI
- hash to sign: `c798e39df2834a16d461a646b8512469f51228ce41fd2088d7156bbf78d9ec46`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/esketamine-trd-madrs/index.html` (sha256 `e114dce97125421d…`)

**N23  iv-iron-hfref-hosp / Heart-failure hospitalization**
- (k=2, INCOMPATIBLE (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO), estimate=None, CI=[None, None]) -> (k=1, HR, estimate=0.39, CI=[0.19, 0.82])
- direction: RESULT_ADDED; conclusion changed: True; triggers: NEW_FAVOURABLE_CI
- hash to sign: `a756a601fe1512d95acf8ae7e652633c3202da441ee1b9f8aca80b7c7feb03a2`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/iv-iron-hfref-hosp/index.html` (sha256 `14ec695f1c6124be…`)

**N26  omega3-cardiovascular-events / Major vascular events / MACE**
- (k=5, HR, estimate=0.937, CI=[0.7726, 1.1364]) -> (k=1, HR, estimate=0.92, CI=[0.8, 1.06])
- direction: AWAY_FROM_NULL; conclusion changed: False; triggers: AWAY_FROM_NULL, OPPOSITE_POOLED_DIRECTION_TRIAL_REMOVED
- hash to sign: `4321fe0612f041924e2fd562a27c8f76fc19e463cb5347a1ef921d6a524b9623`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/omega3-cardiovascular-events/index.html` (sha256 `e416d398208e27d5…`)

**N28  pcsk9-mace / Major adverse cardiovascular events**
- (k=2, HR, estimate=0.8261, CI=[None, None]) -> (k=1, HR, estimate=0.85, CI=[0.78, 0.93])
- direction: AWAY_FROM_NULL; conclusion changed: True; triggers: AWAY_FROM_NULL, NEW_FAVOURABLE_CI
- hash to sign: `e74f1437ed2dc9e5a6d3b6da7aa24ff5173ce300bc762c25be0d8117f15046e3`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/pcsk9-mace/index.html` (sha256 `605d40f0957d301e…`)
- **changed by the re-judgement:** `{"gate_requires_per_notice_signature": {"before": false, "after": true}}`

**N30  probiotics-aad-prevention / Any adverse events**
- (k=2, RR, estimate=None, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: NO_DIRECTION; conclusion changed: False
- hash to sign: `a5083e8448a338085d16c78d004a89cb7ba9228227536aa8acfdd47b8d01a6f8`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/probiotics-aad-prevention/index.html` (sha256 `48a74a043a0b97c7…`)

**N32  sacubitril-valsartan-hfref / Composite cardiovascular death or heart-failure hospitalization**
- (k=2, HR, estimate=None, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: NO_DIRECTION; conclusion changed: False
- hash to sign: `c0bf1e693beaf2b104af3e8391085c2236c2e1831c6b6740aa1add22e9176260`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/sacubitril-valsartan-hfref/index.html` (sha256 `496e032dbd39c896…`)

**N38  statins-primary-prevention-elderly / Major vascular events**
- (k=2, HR, estimate=0.6803, CI=[None, None]) -> (k=1, HR, estimate=0.7, CI=[0.61, 0.82])
- direction: AWAY_FROM_NULL; conclusion changed: True; triggers: AWAY_FROM_NULL, NEW_FAVOURABLE_CI
- hash to sign: `6f503cd8fe2fc65b64343441de1a22a7d7047f962740dfbf081b4143d5383a1a`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/statins-primary-prevention-elderly/index.html` (sha256 `136bfbaaec819afa…`)
- **changed by the re-judgement:** `{"gate_requires_per_notice_signature": {"before": false, "after": true}}`

**N39  ticagrelor-vs-clopidogrel-acs / Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke**
- (k=2, HR, estimate=None, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: NO_DIRECTION; conclusion changed: False
- hash to sign: `11cf90c04c148e604be8007ccd191118952aeac795271eeef0cee5a18e98ffcf`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html` (sha256 `d1ba1810955a85e6…`)


## NOT SIGNABLE — mechanism cannot be judged from the pinned bytes — 1 of 41

**N27  omega3-cardiovascular-events / Atrial fibrillation**
- (k=None, no scale, estimate=None, CI=[None, None]) -> (k=1, RR, estimate=1.2296, CI=[0.9819, 1.5398])
- direction: RESULT_ADDED; conclusion changed: True
- hash to sign: `f8d44302027be1bf182b7bbed29833975e3517cb0b36313cf77992ec80c980c9`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/omega3-cardiovascular-events/index.html` (sha256 `e416d398208e27d5…`)
- **changed by the re-judgement:** `{"recommendation": {"before": "NEEDS_MAHMOOD_JUDGEMENT", "after": "UNJUDGEABLE"}}`


## RESTORE BY EVIDENCE — 1 of 41

**N37  spironolactone-hfref-mortality / All-cause mortality**
- (k=3, HR, estimate=0.7294, CI=[0.5609, 0.9486]) -> (k=1, HR, estimate=0.85, CI=[0.53, 1.36])
- direction: TOWARD_NULL; conclusion changed: True
- hash to sign: `6b0a23a030f53c9216f960a2af3ba7ca42a5d1bf6b70b6a03df9c079a2fd96e7`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/spironolactone-hfref-mortality/index.html` (sha256 `9ceaad4b7d38493b…`)


## COUNTERSIGN AS IS — 29 of 41

**N01  balanced-crystalloids-vs-saline-mortality / Mortality**
- (k=2, HR, estimate=0.9774, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `2b86cd169fad9d8097b14067fdb5ce1653e77297870530e20eae588bdadf80b2`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html` (sha256 `c1e56b207f6ab853…`)

**N02  colchicine-postop-af / Postoperative atrial fibrillation**
- (k=3, RR, estimate=0.6509, CI=[0.2063, 2.0538]) -> (k=2, RR, estimate=0.8211, CI=[None, None])
- direction: TOWARD_NULL; conclusion changed: False
- hash to sign: `3690431114d72de2fa5a318f5963918028bfd930e9e491856dfd4e85d51c74fc`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/colchicine-postop-af/index.html` (sha256 `9ecf0dc57230897e…`)

**N03  colchicine-secondary-cv-prevention / Trial-defined major coronary/cardiovascular composite**
- (k=3, HR, estimate=0.8134, CI=[0.5074, 1.3039]) -> (k=2, HR, estimate=0.8855, CI=[None, None])
- direction: TOWARD_NULL; conclusion changed: False
- hash to sign: `e3a424b71025d731310fb187708c9c070af75263f759604c414170d043f2b908`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/colchicine-secondary-cv-prevention/index.html` (sha256 `2da4712213a717b0…`)

**N04  colchicine-secondary-cv-prevention / Gastrointestinal adverse effects**
- (k=1, RR, estimate=5.375, CI=[1.5958, 18.1047]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/colchicine-secondary-cv-prevention/index.html` (sha256 `2da4712213a717b0…`)

**N05  colchicine-secondary-cv-prevention / Non-cardiovascular death**
- (k=1, HR, estimate=1.51, CI=[0.99, 2.31]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `c37ca3b953b5bb40d797d09b1a39e627877739cbed681cb43b2a1708c12fefdb`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/colchicine-secondary-cv-prevention/index.html` (sha256 `2da4712213a717b0…`)

**N07  corticosteroids-covid19-mortality / 28-day all-cause mortality**
- (k=1, RR, estimate=0.83, CI=[0.75, 0.93]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `d614bce51c695ce4a03183ad619bcecb242cd338032e4f56df26177143ce4236`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/corticosteroids-covid19-mortality/index.html` (sha256 `f9888ce941fa571d…`)

**N08  corticosteroids-covid19-mortality / Serious adverse events**
- (k=1, OR, estimate=2.8065, CI=[0.1056, 74.5638]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `0598e8b7596d23b2e1549a5f70625e4ef9c0eb2f98f23c58f87c8eb554937bc8`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/corticosteroids-covid19-mortality/index.html` (sha256 `f9888ce941fa571d…`)

**N09  dapagliflozin-hfpef-hosp / Adverse events**
- (k=1, RR, estimate=1.1579, CI=[0.7954, 1.6855]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `edf44d6a7f4379e2d843d69bc4b364d10d5d8814e7b8e71a2b96760ca44eba28`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/dapagliflozin-hfpef-hosp/index.html` (sha256 `aa151507ffefb9fb…`)

**N10  denosumab-vertebral-fracture / New vertebral fracture**
- (k=1, RR, estimate=0.32, CI=[0.26, 0.41]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `95dd9b4646712d4f3445a3aafe0021e2de9a3463cdddf28bce9f1074298aad96`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/denosumab-vertebral-fracture/index.html` (sha256 `f68d3239cf456ecf…`)

**N11  denosumab-vertebral-fracture / Nonvertebral fracture**
- (k=1, HR, estimate=0.8, CI=[0.67, 0.95]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `4943555b8c1f964c6a0bbb14f76e51b31396a7f99223a0e4f9f08d4a288dae84`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/denosumab-vertebral-fracture/index.html` (sha256 `f68d3239cf456ecf…`)

**N12  denosumab-vertebral-fracture / Hip fracture**
- (k=1, HR, estimate=0.6, CI=[0.37, 0.97]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `a54538da135fd19653552c00e6654557e8c4c9d7d85f5439a5c0fce0026507a1`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/denosumab-vertebral-fracture/index.html` (sha256 `f68d3239cf456ecf…`)

**N13  doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)**
- (k=6, HR, estimate=0.9091, CI=[0.7479, 1.105]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: OPPOSITE_POOLED_DIRECTION_TRIAL_REMOVED
- hash to sign: `31026af2f4b7dd5c743a81d36d65d685e8e1bdfc72c3776a82ae21660f2baef2`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/doac-vte-recurrence/index.html` (sha256 `2b35cc21e8fba547…`)

**N14  doac-vte-recurrence / Major bleeding**
- (k=3, HR, estimate=0.6179, CI=[0.306, 1.2475]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `81e8c9bb43e75c896680f56f2754e70e4386e58f93ff1d1be7fa7b7064a7d8f3`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/doac-vte-recurrence/index.html` (sha256 `2b35cc21e8fba547…`)

**N15  doac-vte-recurrence / Major or clinically relevant nonmajor bleeding**
- (k=2, HR, estimate=0.8451, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `b1c40017b581d6f7ddf3d4f79c5c1f37a91ee39a3156c9105dec97768cfade7e`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/doac-vte-recurrence/index.html` (sha256 `2b35cc21e8fba547…`)

**N16  doac-vte-recurrence / Any bleeding**
- (k=2, HR, estimate=0.6899, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `0d8530a50a44be5e7a37a16e36379fef7d121f1eb1ec281930a542343248b736`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/doac-vte-recurrence/index.html` (sha256 `2b35cc21e8fba547…`)

**N18  dpp4-mace-t2d / Adverse events**
- (k=1, RR, estimate=0.9879, CI=[0.9633, 1.0131]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `51bce4eea7aa71923e858e04fc137157c35652c561de87bb83cb273bcb237eb3`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/dpp4-mace-t2d/index.html` (sha256 `8ca0bec12cebf398…`)

**N19  dpp4-mace-t2d / Hypoglycemia**
- (k=1, RR, estimate=1.0091, CI=[0.9385, 1.085]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `0930b057ff6a2a11d6b5c7335055d6ebf1b674b303b1c6dad59945d6af6fb854`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/dpp4-mace-t2d/index.html` (sha256 `8ca0bec12cebf398…`)

**N21  esketamine-trd-madrs / Adverse events**
- (k=1, RR, estimate=1.3483, CI=[1.1969, 1.5189]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `13f747773d3ace542789ecd24483b3bd3121dc9cc97a11df0ce2b7541d8beed2`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/esketamine-trd-madrs/index.html` (sha256 `e114dce97125421d…`)

**N22  glp1-ra-mace-t2d / 3-point major adverse cardiovascular events**
- (k=8, HR, estimate=0.856, CI=[0.8086, 0.9061]) -> (k=7, HR, estimate=0.8664, CI=[0.8142, 0.9218])
- direction: TOWARD_NULL; conclusion changed: False
- hash to sign: `d08802f24fa082652dc45a011f29b08edd49030c2429d9c1b0062d27094ae694`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/glp1-ra-mace-t2d/index.html` (sha256 `a887d6e56fe8ec4c…`)

**N24  metformin-pcos-ovulation / Ovulation with metformin added to clomifene**
- (k=3, OR, estimate=2.0733, CI=[0.0922, 46.6008]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: OPPOSITE_POOLED_DIRECTION_TRIAL_REMOVED
- hash to sign: `1c9acaf64e31e52cf02127e55758e702277c6e2f2e357b296a95ab8226aea944`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/metformin-pcos-ovulation/index.html` (sha256 `c88bee677278d44e…`)

**N25  noac-vs-warfarin-af-stroke / Stroke or systemic embolism**
- (k=4, HR, estimate=0.8069, CI=[0.6611, 0.985]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `96bb274b31cd7b87ad1c6b915c825ebb01c6714de82dde2a22df8c10566bc301`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/noac-vs-warfarin-af-stroke/index.html` (sha256 `0a12d820a039dd31…`)

**N29  probiotics-aad-prevention / Antibiotic-associated diarrhoea**
- (k=11, RR, estimate=0.6874, CI=[0.4803, 0.9839]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: OPPOSITE_POOLED_DIRECTION_TRIAL_REMOVED
- hash to sign: `f7e6067da30ae61a647d04f07e01607869533ff71f658c7277044bac317f1367`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/probiotics-aad-prevention/index.html` (sha256 `48a74a043a0b97c7…`)

**N31  probiotics-aad-prevention / Serious adverse events**
- (k=1, RR, estimate=0.6556, CI=[0.1882, 2.284]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `2cd6d6b932556d19c2545dc292f0ed279e8d770d3bd20b9337fcdd83cb1a7e31`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/probiotics-aad-prevention/index.html` (sha256 `48a74a043a0b97c7…`)

**N33  semaglutide-obesity-mace / 3-point major adverse cardiovascular events**
- (k=1, HR, estimate=0.8, CI=[0.72, 0.9]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `53fbdc2855f72801f2ae3c421f3eecff3a7aac637ed697e5045666f4d3e9ac19`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/semaglutide-obesity-mace/index.html` (sha256 `7e9f048c07fb318b…`)

**N34  semaglutide-obesity-mace / Adverse events leading to permanent discontinuation**
- (k=1, RR, estimate=2.0344, CI=[1.8699, 2.2133]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `e74270fdaec8ee61ff67a5896ec876bad4dfe4bbee5f869fdf917bd090c0112b`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/semaglutide-obesity-mace/index.html` (sha256 `7e9f048c07fb318b…`)

**N35  sglt2-primary-prevention-hf / Hospitalization for heart failure**
- (k=4, HR, estimate=0.6956, CI=[0.5763, 0.8397]) -> (k=1, HR, estimate=0.7, CI=[0.54, 0.9])
- direction: TOWARD_NULL; conclusion changed: False
- hash to sign: `76fc6c707cac742d9b0ab8d04fd69ef2b6a21e231ba1bec09b9c4f5af37a2704`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/sglt2-primary-prevention-hf/index.html` (sha256 `80ac4092b72fd8cc…`)

**N36  sglt2-primary-prevention-hf / Lower-limb amputation**
- (k=1, HR, estimate=1.97, CI=[1.41, 2.75]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `79240a2fdba179f2d7fd25a21885eaebd6a0e92a9ab0dea6a6e4ebdada3dea57`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/sglt2-primary-prevention-hf/index.html` (sha256 `80ac4092b72fd8cc…`)

**N40  ticagrelor-vs-clopidogrel-acs / Major bleeding**
- (k=2, HR, estimate=1.1658, CI=[None, None]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True; triggers: UNFAVOURABLE_HARM_ESTIMATE_REMOVED
- hash to sign: `4b9137866f1904beed6c1a1eedc01d07b3720f7b196560c6443ac24703f4a697`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html` (sha256 `d1ba1810955a85e6…`)

**N41  tocilizumab-covid19-mortality / 28-day all-cause mortality**
- (k=1, RR, estimate=0.85, CI=[0.76, 0.94]) -> (k=None, no scale, estimate=None, CI=[None, None])
- direction: RESULT_REMOVED; conclusion changed: True
- hash to sign: `dac4bf59ed5f659ed5e2fc8399c8a0de7d5543f9c006785f7c717bb20ccec970`
- page: `git:1fa77f2c4852ee79e55d540083e3c35bbff0cecc:docs/reviews/tocilizumab-covid19-mortality/index.html` (sha256 `19f3aab6a690d3d5…`)

