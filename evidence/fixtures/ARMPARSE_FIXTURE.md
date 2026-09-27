# Arm parser pinned corpus fixture

Source commit: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. Parser: current worktree `harness/arm_parse.py` (unchanged).

All 32 served topics are enumerated, including topics with no qualifying records. The unit is a held occurrence in `records[]` or `ctgov[]` with at least two listed interventions; repeated studies across topics/collections remain separate. These are intervention lists, not guaranteed randomized arms. No inferred arm expansion is performed.

Served decisions come only from `screening.records`. Exact IDs or bounded NCT identifiers in display IDs are joined; missing decisions are null. Registry rows and source SHA-256 hashes are retained. No live registry lookup or screening rerun is used.

| Static input | Dynamic computation |
|---|---|
| Pinned commit, 32-topic coverage contract | Git blobs and SHA-256 manifest |
| Explicit independently authored label-reading tables and rationales | Coverage checked; unknown triggered labels fail closed |
| Synthetic control labels and expected invariants | Actual parser output, excluded from every corpus total |
| README comparison values 15 / 7 / 6 / 2 | Held-record recomputation; disagreement reported, never tuned |

Interest uses `intervention_terms`, falling back to `include.intervention_any`, matching the README measurement and screen caller. Both source term lists are retained; `screen_fallback_every_arm` separately uses folded interest terms. Ordered contrasts use the arm-object caller's `arm_object.contrast.drug_any` override when present, otherwise the primary interest; the effective list is retained as `ordered_contrast_interest`. Each contrast carries the held registry design. The reading column is manually authored independently of parser output; generic placebo is ABSENT, named topic placebo MATCHED_PLACEBO, actual co-administration ACTIVE. UNCERTAIN is a non-equivalent reading, included in disagreement totals. It is not a validated clinical truth label.

## Totals and denominators

| Property | fires | of (N) |
|---|---:|---:|
| held_records_with_multiple_interventions | 451 | 3290 |
| interest_in_every_arm | 16 | 451 |
| served_decision_available | 400 | 451 |
| served_x_contrast_disagrees | 26 | 400 |
| reading_required | 180 | 1325 |
| reading_disagrees | 6 | 180 |
| reading_uncertain | 1 | 180 |
| exposure_ACTIVE | 440 | 1325 |
| exposure_MATCHED_PLACEBO | 18 | 1325 |
| exposure_VARIES_WITHIN_ARM | 17 | 1325 |
| exposure_ABSENT | 850 | 1325 |
| contrast_CLEAN | 163 | 1012 |
| contrast_CONFOUNDED | 849 | 1012 |
| served_x_contrast_all_topics | 15 | 3146 |
| arm_list_fallback_of_x_contrast | 7 | 15 |
| fallback_not_every_arm | 6 | 7 |
| fallback_matched_placebo | 2 | 7 |

N definitions: held-record selection uses all held records; every-arm and availability use qualifying records; decision disagreement uses qualifying records with a served decision; exposure and reading-required use all listed label occurrences; reading disagreements/uncertainty use triggered label occurrences; contrast states use emitted ordered pairs. Served X-CONTRAST uses all served screening records; fallback uses all X-CONTRAST decisions; fallback causes use fallback decisions. Controls are excluded throughout.

## README measurement comparison

- served_x_contrast_all_topics: README 15; observed 15; agrees.
- arm_list_fallback_of_x_contrast: README 7; observed 7; agrees.
- fallback_not_every_arm: README 6; observed 6; agrees.
- fallback_matched_placebo: README 2; observed 2; agrees.

The measurement's six 'wrong' exclusions refer only to the arm-list route. Other-route disagreement with the every-arm predicate does not establish a wrong screening decision. The collapsed fish-oil case is separately VARIES_WITHIN_ARM, not counted as MATCHED_PLACEBO.

## Every served-decision / every-arm disagreement

Both directions are listed: served X-CONTRAST with every-arm false, and other served rules with every-arm true. These are predicate comparisons, not new screening verdicts.

- **balanced-crystalloids-vs-saline-mortality / NCT07189091** (ctgov[15]): exclude / X-CONTRAST; every-arm=False. Served reason: X-CONTRAST(strategy_bundle): balanced fluid and saline appear inside both randomised strategies; no clean intervention-vs-comparator arm contrast.
- **colchicine-secondary-cv-prevention / NCT03376698** (ctgov[23]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest appears in every structured CT.gov arm entry; the randomised difference is another intervention: Colchicine 0.5 mg; Colchicine 0.25 mg; Placebo
- **corticosteroids-cap-mortality / NCT06892197** (ctgov[3]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo', 'control', 'standard care', 'standard therapy', 'usual care', 'conventional therapy']).
- **corticosteroids-covid19-mortality / NCT04513184** (ctgov[14]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo', 'usual care', 'standard care', 'standard therapy', 'standard treatment', 'no hydrocortisone']).
- **corticosteroids-covid19-mortality / NCT04561180** (ctgov[15]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest is present in EVERY arm (background); the randomised contrast is a different intervention (keyword 'dexamethasone' matched AACT arm intervention 'dexamethasone')
- **dapagliflozin-hfpef-hosp / NCT05676684** (ctgov[19]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo', 'matching placebo']).
- **doac-vte-recurrence / NCT04874428** (ctgov[3]): exclude / X2; every-arm=True. Served reason: population not on-topic: title/conditions do not mention any of ['venous thromboembolism', 'VTE', 'deep-vein thrombosis', 'deep vein thrombosis', 'pulmonary embolism', 'DVT', 'PE'] (an incidental abstract mention does not qualify).
- **doac-vte-recurrence / NCT04477837** (ctgov[22]): exclude / X1; every-arm=True. Served reason: not a randomized controlled trial (record: NCT04477837).
- **doac-vte-recurrence / NCT07083609** (ctgov[25]): exclude / X1; every-arm=True. Served reason: not a randomized controlled trial (record: DCVT-VN25).
- **empagliflozin-hfpef-hosp / NCT05138575** (ctgov[6]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest appears in every structured CT.gov arm entry; the randomised difference is another intervention: Empagliflozin + Potassium Chloride; Empagliflozin + Potassium Nitrate; Potassium Chloride + Placebo for Empagliflozin
- **esketamine-trd-madrs / NCT07053345** (ctgov[20]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo']).
- **esketamine-trd-madrs / NCT01998958** (ctgov[29]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest appears in every structured CT.gov arm entry; the randomised difference is another intervention: Esketamine 14 mg; Esketamine 28 mg; Esketamine 56 mg; Esketamine 84 mg; Placebo
- **finerenone-ckd-t2d-renal / NCT01968668** (ctgov[0]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest appears in every structured CT.gov arm entry; the randomised difference is another intervention: BAY94-8862; BAY94-8862; BAY94-8862; BAY94-8862; BAY94-8862; Placebo; BAY 94-8862; BAY 94-8862
- **melatonin-primary-insomnia-sol / NCT00816673** (ctgov[6]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest appears in every structured CT.gov arm entry; the randomised difference is another intervention: placebo Circadin; Circadin
- **metformin-pcos-ovulation / NCT00953355** (ctgov[16]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo group', 'placebo-controlled', 'placebo controlled', 'placebo-treated', 'placebo alone']).
- **metformin-pcos-ovulation / NCT06742710** (ctgov[17]): exclude / X2; every-arm=True. Served reason: wrong population: title/conditions mention 'liraglutide'.
- **noac-vs-warfarin-af-stroke / NCT03153150** (ctgov[17]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: Randomised START vs AVOID anticoagulation (Start arm = DOAC or VKA; control = antiplatelet/nothing) — not a DOAC-vs-warfarin contrast (audit-confirmed non-contrast; evicted at eligibility, not pooled).
- **omega3-cardiovascular-events / NCT01630213** (ctgov[13]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest appears in every structured CT.gov arm entry; the randomised difference is another intervention: Vitamin D3 + fish oil/fish oil placebo; Vitamin D3 placebo + fish oil/fish oil placebo
- **omega3-cardiovascular-events / NCT02285166** (ctgov[27]): exclude / X1; every-arm=True. Served reason: not a randomized controlled trial (record: NCT02285166).
- **probiotics-aad-prevention / NCT01463943** (ctgov[7]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo', 'control', 'no treatment', 'usual care', 'standard care', 'no probiotic', 'not receive', 'not receiving']).
- **sacubitril-valsartan-hfref / NCT07347925** (ctgov[20]): exclude / X1; every-arm=True. Served reason: not a randomized controlled trial (record: NCT07347925).
- **sglt2-ckd-progression / NCT05884866** (ctgov[6]): exclude / X-CONTRAST; every-arm=False. Served reason: X-CONTRAST(background=dapagliflozin 10 mg both arms): the topic intervention is background therapy in both arms, not the randomised contrast.
- **sglt2-ckd-progression / NCT06350123** (ctgov[7]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: all cached registry arms receive Dapagliflozin; randomisation isolates Balcinrenone rather than Dapagliflozin/SGLT2-vs-placebo (audit-confirmed non-contrast; evicted at eligibility, not pooled).
- **statins-primary-prevention-elderly / NCT01646307** (ctgov[7]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo', 'usual care', 'control']).
- **statins-primary-prevention-elderly / NCT07359105** (ctgov[9]): exclude / X3; every-arm=True. Served reason: no eligible comparator (none of ['placebo', 'usual care', 'control']).
- **statins-primary-prevention-elderly / NCT00127218** (ctgov[13]): exclude / X-CONTRAST; every-arm=False. Served reason: CONTRAST_ABSENT: the intervention of interest is present in EVERY arm (background); the randomised contrast is a different intervention (keyword 'statin' matched AACT arm intervention 'any statin')

## Every independent READING disagreement

- **iv-iron-hfref-hosp / NCT06434025** (ctgov[8]): `Placebo of Iron Carboxymaltose` — parser **ABSENT**, READING **MATCHED_PLACEBO**. The label identifies placebo for iron carboxymaltose, read as the topic's ferric carboxymaltose; this is a semantic reading, not an additional parser keyword.
- **sacubitril-valsartan-hfref / NCT02554890** (ctgov[24]): `sacubitril/valsartan (LCZ696) matching placebo` — parser **VARIES_WITHIN_ARM**, READING **MATCHED_PLACEBO**. A placebo replaces the named topic agent; slash in a fixed combination or mg/ml dose does not denote randomized levels.
- **semaglutide-obesity-weight / NCT07357766** (ctgov[22]): `Placebo CagriSema` — parser **ABSENT**, READING **UNCERTAIN**. A placebo is explicit, so no active exposure is stated; the label alone does not expand CagriSema into the topic agent. Matching identity is unresolved without importing external product knowledge.
- **semaglutide-obesity-weight / NCT05078255** (ctgov[26]): `Semaglutide 1.34 mg/ml placebo` — parser **VARIES_WITHIN_ARM**, READING **MATCHED_PLACEBO**. A placebo replaces the named topic agent; slash in a fixed combination or mg/ml dose does not denote randomized levels.
- **sglt2-ckd-progression / NCT06350123** (ctgov[7]): `Balcinrenone/dapagliflozin 15 mg/10 mg and matching placebo for dapagliflozin 10 mg` — parser **VARIES_WITHIN_ARM**, READING **ACTIVE**. The fixed combination supplies dapagliflozin; the additional matching placebo does not remove that exposure. Slashes denote ingredients and doses, not allocation levels.
- **sglt2-ckd-progression / NCT06350123** (ctgov[7]): `Balcinrenone/dapagliflozin 40 mg/10 mg and matching placebo for dapagliflozin 10 mg` — parser **VARIES_WITHIN_ARM**, READING **ACTIVE**. The fixed combination supplies dapagliflozin; the additional matching placebo does not remove that exposure. Slashes denote ingredients and doses, not allocation levels.

## Held records without a served record decision

No same-record screening decision exists for these identifiers in the pinned `screening.records`. A PMID decision sharing a trial family is not substituted for a CT.gov record decision. These records remain in label/contrast totals, with `served_screening: null`, and are excluded only from decision-disagreement denominators.

- balanced-crystalloids-vs-saline-mortality / NCT02875873 (ctgov[7]).
- balanced-crystalloids-vs-saline-mortality / NCT02444988 (ctgov[8]).
- balanced-crystalloids-vs-saline-mortality / NCT02721654 (ctgov[16]).
- colchicine-postop-af / NCT04224545 (ctgov[2]).
- colchicine-postop-af / NCT01552187 (ctgov[5]).
- colchicine-recurrent-pericarditis / NCT00235079 (ctgov[0]).
- colchicine-recurrent-pericarditis / NCT00128453 (ctgov[4]).
- colchicine-recurrent-pericarditis / NCT00128414 (ctgov[6]).
- colchicine-secondary-cv-prevention / NCT03048825 (ctgov[1]).
- colchicine-secondary-cv-prevention / NCT06095765 (ctgov[22]).
- colchicine-secondary-cv-prevention / NCT04848857 (ctgov[29]).
- corticosteroids-cap-mortality / NCT04381936 (ctgov[2]).
- corticosteroids-cap-mortality / NCT02517489 (ctgov[5]).
- dapagliflozin-hfpef-hosp / NCT03030235 (ctgov[9]).
- dapagliflozin-hfpef-hosp / NCT04730947 (ctgov[16]).
- dapagliflozin-hfpef-hosp / NCT03619213 (ctgov[18]).
- doac-vte-recurrence / NCT05351749 (ctgov[7]).
- doac-vte-recurrence / NCT06611319 (ctgov[13]).
- doac-vte-recurrence / NCT03285438 (ctgov[19]).
- doac-vte-recurrence / NCT02664155 (ctgov[24]).
- doac-vte-recurrence / NCT04569279 (ctgov[28]).
- empagliflozin-hfpef-hosp / NCT03057951 (ctgov[12]).
- esketamine-trd-madrs / NCT02418585 (ctgov[15]).
- esketamine-trd-madrs / NCT02918318 (ctgov[27]).
- finerenone-ckd-t2d-renal / NCT02540993 (ctgov[2]).
- finerenone-ckd-t2d-renal / NCT01874431 (ctgov[3]).
- finerenone-ckd-t2d-renal / NCT02545049 (ctgov[14]).
- glp1-ra-mace-t2d / NCT03496298 (ctgov[0]).
- iv-iron-hfref-hosp / NCT03036462 (ctgov[5]).
- melatonin-primary-insomnia-sol / NCT00397189 (ctgov[7]).
- metformin-pcos-ovulation / NCT00151411 (ctgov[4]).
- noac-vs-warfarin-af-stroke / NCT00781391 (ctgov[5]).
- probiotics-aad-prevention / NCT02765217 (ctgov[0]).
- probiotics-aad-prevention / NCT01782755 (ctgov[4]).
- probiotics-aad-prevention / NCT03334604 (ctgov[11]).
- probiotics-aad-prevention / NCT01143272 (ctgov[24]).
- probiotics-aad-prevention / NCT05607056 (ctgov[28]).
- sacubitril-valsartan-hfref / NCT01035255 (ctgov[26]).
- semaglutide-obesity-weight / NCT05564117 (ctgov[8]).
- semaglutide-obesity-weight / NCT06173778 (ctgov[19]).
- sglt2-primary-prevention-hf / NCT03282136 (ctgov[0]).
- sglt2-primary-prevention-hf / NCT03151343 (ctgov[2]).
- sglt2-primary-prevention-hf / NCT03753087 (ctgov[4]).
- sglt2-primary-prevention-hf / NCT05390892 (ctgov[5]).
- sglt2-primary-prevention-hf / NCT03939624 (ctgov[10]).
- sglt2-primary-prevention-hf / NCT04298229 (ctgov[13]).
- sglt2-primary-prevention-hf / NCT02956811 (ctgov[21]).
- statins-primary-prevention-elderly / NCT02099123 (ctgov[19]).
- tranexamic-acid-pph / NCT02805426 (ctgov[1]).
- tranexamic-acid-pph / NCT03431805 (ctgov[14]).
- tranexamic-acid-pph / NCT03475342 (ctgov[15]).

## Controls and limitations

- `__control_matched_0`: ["placebo for empagliflozin"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_1`: ["placebo empagliflozin"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_2`: ["empagliflozin placebo"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_3`: ["empagliflozin-matching placebo"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_4`: ["matching placebo for empagliflozin"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_5`: ["placebo (empagliflozin)"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_6`: ["placebo to match empagliflozin"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_7`: ["placebo Circadin"] → MATCHED_PLACEBO; every-arm=False.
- `__control_matched_8`: ["fish oil placebo"] → MATCHED_PLACEBO; every-arm=False.
- `__control_collapsed`: ["fish oil/fish oil placebo"] → VARIES_WITHIN_ARM; every-arm=False.
- `__control_plain`: ["Placebo"] → ABSENT; every-arm=False.
- `__control_miro`: ["Balcinrenone 15 mg + Dapagliflozin 10 mg", "Placebo + Dapagliflozin 10 mg"] → ACTIVE, ACTIVE; every-arm=True.
- `__control_doac`: ["Dabigatran Etexilate Oral Capsule", "Rivaroxaban Oral Tablet"] → ACTIVE, ACTIVE; every-arm=True.
- `__control_design_phrase`: ["Placebo-controlled empagliflozin 10 mg"] → MATCHED_PLACEBO; every-arm=False.

The design-phrase control is not an arm: its observed result is recorded without asserting a desired answer. The simplified MIRO control stays True, whereas the held MIRO fixed-combination slash labels need separate scrutiny (see readings above). Source labels, topic vocabularies, and parser output have not been repaired to make this fixture pass.

Regenerate: `python evidence/fixtures/build_armparse_fixture.py`.
Validate: `python -m pytest -q tests/test_armparse_corpus_fixture.py tests/test_matched_placebo.py`.
