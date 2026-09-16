# LANE KM2 Report

Default evidence label for this report: MEASURED. Every unprefixed numeral or quoted value below was measured from commands or files in this clone. Values not measured here are explicitly tagged CLAIMED or INFERRED.

## 1. What Was Wrong, Mechanism, Files

MEASURED base HEAD: `ad5e7c66`.

MEASURED defect: GRADE imprecision text did not name the quantity being graded. At k=2, the K2 policy already refused the registered PM/HKSJ interval, but the rendered imprecision rationale stayed generic and did not show the refused random-effects audit interval beside the observed-evidence common-effect caveat interval.

MEASURED mechanism: `harness/grade.py` computed imprecision in-place from the served interval or the K2 refusal flag. The new `harness/grade_quantity.py` makes the two quantities explicit:

| Static/dynamic item | Disclosure |
| --- | --- |
| `RE_SUPERPOPULATION_INTERVAL`, `OBSERVED_EVIDENCE_COMMON_EFFECT`, `ENGINE_CANNOT_CONSUME` | Static labels only; not evidence. |
| Interval estimates and limits | Dynamic, read from the result object produced by the build. |
| Participant shares in small-k notes | Dynamic, read from trial rows and held cache/source text. Approximate only when inferred from rounded source percentages. |
| Effect-modifier cue vocabulary | Static phrase list; emitted only when the exact held text contains the cue. |
| `panel_shape` enum | Static merge contract; classification is dynamic from before/after intervals. |

MEASURED files with executable logic:

- `harness/grade_quantity.py`: new quantity-specific GRADE helper, small-k prediction-interval note generator, `ENGINE_CANNOT_CONSUME` text, and known-missing panel shape classifier.
- `harness/grade.py`: routes imprecision and indirectness domain text through `grade_quantity`.
- `harness/pipeline.py`: attaches generated small-k prediction-interval notes to outcome results.
- `scripts/grade_quantity_sweep.py`: writes `docs/grade_quantity_sweep.json`.
- `tests/test_grade_quantity.py`: plant and synthetic tests.

MEASURED VS state: `harness/missing_effect.py` is absent (`Test-Path` returned `False`), so I did not duplicate VS's module. I added only the merge-facing `panel_shape` classifier and enum values in `harness/grade_quantity.py`.

## 2. The Plant

MEASURED test file: `tests/test_grade_quantity.py`.

MEASURED tests and assertions:

- `test_plant_finerenone_pre_fix_lacked_quantity_basis_and_live_names_both_intervals`
  - Pre-fix object: `git show ad5e7c66:docs/reviews/finerenone-ckd-t2d-renal/review.json`.
  - Assertion: pre-fix basis contains `registered pooled CI refused at k=2 (K2_SINGLE_DF)`, has no `imprecision_basis`, and does not contain `0.4625` or `0.7666`.
  - Post-fix assertion: live basis names `OBSERVED_EVIDENCE_COMMON_EFFECT`, stores RE audit interval `0.4625` and common-effect caveat interval `0.7666`, and the live PI note states `33264825 contributes 5734 of about 13076 participants (43.9%; denominator partly inferred from rounded source percentages)`.
- `test_plant_semaglutide_k2_uses_common_effect_caveat_not_refused_hksj_for_basis`
  - Assertion: live semaglutide weight imprecision basis is `OBSERVED_EVIDENCE_COMMON_EFFECT`, with common-effect `MD -12.3621 [-13.0206, -11.7036]` and refused audit interval `MD -11.8449 [-25.1318, 1.442]`.
- `test_synthetic_k2_tau2_zero_large_n_basis_sentence`
  - Assertion: synthetic k=2 tau2=0 large-n result labels the basis as `OBSERVED_EVIDENCE_COMMON_EFFECT` and says the PM/HKSJ interval is refused at k=2.
- `test_synthetic_engine_cannot_consume_is_refusal_not_unavailable_evidence`
  - Assertion: imprecision says `different from evidence being unavailable`; indirectness says `not that evidence is unavailable`.
- `test_synthetic_k3_tiny_discordant_prediction_note_names_it`
  - Assertion: synthetic k=3 note states `Tiny C contributes 20 of 2020 participants (1.0%)` and `at least one trial is discordant in direction`.
- `test_live_spironolactone_prediction_note_names_tiny_discordant_third_trial`
  - Assertion: live spironolactone note states `J-EMPHASIS-HF contributes 221 of 4621 participants (4.8%)` and discordance.
- `test_panel_shape_tightens_and_reverses_to_effect`
  - Assertion: synthetic classifications return `TIGHTENS` and `REVERSES_TO_EFFECT`.

MEASURED pre-fix finerenone quote: `registered pooled CI refused at k=2 (K2_SINGLE_DF); imprecision requires human judgement and is not read from the quarantined HKSJ interval | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty)`.

MEASURED post-fix finerenone quote: `imprecision_basis=OBSERVED_EVIDENCE_COMMON_EFFECT; registered PM/HKSJ interval is refused at k=2 (K2_SINGLE_DF) and shown only for audit as HR 0.8407 [0.4625, 1.5281]; observed-evidence common-effect caveat interval is HR 0.8407 [0.7666, 0.9218], excludes the null (1); imprecision is not read from the refused random-effects superpopulation interval | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty)`.

MEASURED plant output: `44 passed in 13.56s` for `python -m pytest tests/test_grade_quantity.py tests/test_grade_integration_floor.py tests/test_grade_global_fixes.py tests/test_stage_additions.py tests/test_k2_refusal.py -x -q`.

## 3. Pages Whose Rebuilt Bytes Changed

MEASURED changed review pages: 32 of 32 `docs/reviews/*` review directories. Each changed directory has the generated `REPRODUCTION.json`, `index.html`, `manifest.json`, and `review.json`. MEASURED changed blind pages: 32 `docs/m/*/index.html` files. MEASURED generated ledger updated: `docs/fix_ledger.json`.

MEASURED imprecision block changes:

| Page | Before | After |
| --- | --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `RR 0.9774 [0.6521, 1.465]`; common-effect `RR 0.9774 [0.9183, 1.0404]`, crosses null. |
| `colchicine-postop-af` | `95% CI [0.376, 1.2067]`. | `RE_SUPERPOPULATION_INTERVAL`; `RR 0.6735 [0.376, 1.2067]`. |
| `colchicine-recurrent-pericarditis` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `RR 0.4813 [0.064, 3.6169]`; common-effect `RR 0.4813 [0.3526, 0.6569]`, excludes null. |
| `colchicine-secondary-cv-prevention` | `95% CI [0.5074, 1.3039]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.8134 [0.5074, 1.3039]`. |
| `corticosteroids-cap-mortality` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `RR 0.5458 [0.0361, 8.2605]`; common-effect `RR 0.5458 [0.3589, 0.8299]`, excludes null. |
| `corticosteroids-covid19-mortality` | `95% CI [0.75, 0.93]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `RR 0.83 [0.75, 0.93]`; single-trial sentence retained. |
| `dapagliflozin-hfpef-hosp` | `95% CI [0.73, 0.92]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.82 [0.73, 0.92]`; single-trial sentence retained. |
| `denosumab-vertebral-fracture` | `95% CI [0.26, 0.41]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `RR 0.32 [0.26, 0.41]`; single-trial sentence retained. |
| `doac-vte-recurrence` | `95% CI [0.7478, 1.1054]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.9092 [0.7478, 1.1054]`. |
| `dpp4-mace-t2d` | `95% CI [0.8391, 1.2094]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 1.0074 [0.8391, 1.2094]`. |
| `empagliflozin-hfpef-hosp` | `95% CI [0.69, 0.9]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.79 [0.69, 0.9]`; single-trial sentence retained. |
| `esketamine-trd-madrs` | `95% CI [-6.0701, -0.6189]`. | `RE_SUPERPOPULATION_INTERVAL`; `MD -3.3445 [-6.0701, -0.6189]`. |
| `finerenone-ckd-t2d-renal` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `HR 0.8407 [0.4625, 1.5281]`; common-effect `HR 0.8407 [0.7666, 0.9218]`, excludes null. |
| `glp1-ra-mace-t2d` | `95% CI [0.8086, 0.9061]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.856 [0.8086, 0.9061]`. |
| `iv-iron-hfref-hosp` | `no confidence interval available`. | Basis text unchanged; metadata now carries quantity interval fields and the PI note is rendered. |
| `melatonin-primary-insomnia-sol` | `95% CI [-28.5214, -6.2786]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `MD -17.4 [-28.5214, -6.2786]`; single-trial sentence retained. |
| `metformin-pcos-ovulation` | `95% CI [0.0922, 46.6008]`. | `RE_SUPERPOPULATION_INTERVAL`; `OR 2.0733 [0.0922, 46.6008]`. |
| `noac-vs-warfarin-af-stroke` | `95% CI [0.6611, 0.985]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.8069 [0.6611, 0.985]`. |
| `omega3-cardiovascular-events` | `95% CI [0.846, 1.051]`. | `RE_SUPERPOPULATION_INTERVAL`; `RR 0.943 [0.846, 1.051]`. |
| `pcsk9-mace` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `HR 0.85 [0.5852, 1.2346]`; common-effect `HR 0.85 [0.8024, 0.9004]`, excludes null. |
| `probiotics-aad-prevention` | `95% CI [0.5352, 0.921]`. | `RE_SUPERPOPULATION_INTERVAL`; `RR 0.702 [0.5352, 0.921]`. |
| `sacubitril-valsartan-hfref` | `95% CI [0.73, 0.87]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.8 [0.73, 0.87]`; single-trial sentence retained. |
| `semaglutide-obesity-mace` | `95% CI [0.72, 0.9]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.8 [0.72, 0.9]`; single-trial sentence retained. |
| `semaglutide-obesity-weight` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `MD -11.8449 [-25.1318, 1.442]`; common-effect `MD -12.3621 [-13.0206, -11.7036]`, excludes null. |
| `sglt2-ckd-progression` | `95% CI [0.5537, 0.844]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.6836 [0.5537, 0.844]`. |
| `sglt2-hfref-hosp-cvdeath` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `RR 0.7755 [0.4457, 1.3493]`; common-effect `RR 0.7755 [0.712, 0.8447]`, excludes null. |
| `sglt2-primary-prevention-hf` | `95% CI [0.5763, 0.8397]`. | `RE_SUPERPOPULATION_INTERVAL`; `HR 0.6956 [0.5763, 0.8397]`. |
| `spironolactone-hfref-mortality` | `95% CI [0.3062, 2.4635]`. | `RE_SUPERPOPULATION_INTERVAL`; `RR/HR 0.8685 [0.3062, 2.4635]`. |
| `statins-primary-prevention-elderly` | Generic K2 refusal. | `OBSERVED_EVIDENCE_COMMON_EFFECT`; refused RE audit `HR 0.6803 [0.2897, 1.5975]`; common-effect `HR 0.6803 [0.5964, 0.776]`, excludes null. |
| `ticagrelor-vs-clopidogrel-acs` | `pooled row refused (DIRECTION_CONFLICT_K2)`. | Basis text unchanged; PI note now states k, share, and discordance. |
| `tocilizumab-covid19-mortality` | `95% CI [0.7285, 0.9456]`; single-trial sentence. | `RE_SUPERPOPULATION_INTERVAL`; `OR 0.83 [0.7285, 0.9456]`; single-trial sentence retained. |
| `tranexamic-acid-pph` | `95% CI [0.65, 1.0]`; rounded-null and single-trial sentences. | `RE_SUPERPOPULATION_INTERVAL`; `RR 0.81 [0.65, 1]`; rounded-null and single-trial sentences retained. |

MEASURED prediction-interval note changes on small-k pages:

| Page | Before | After |
| --- | --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | Generic k=2 no-PI note. | k=2; smallest trial `35041780` contributes `4846 of 15898` participants (`30.5%`); no discordant direction. |
| `colchicine-recurrent-pericarditis` | Generic k=2 no-PI note. | k=2; smallest trial `21873705` contributes `120 of 360` participants (`33.3%`); no discordant direction. |
| `colchicine-secondary-cv-prevention` | No note. | k=3; smallest trial `31733140` contributes `4745 of about 17307` participants (`27.4%`; denominator partly inferred); no discordant direction. |
| `corticosteroids-cap-mortality` | Generic k=2 no-PI note. | k=2; smallest trial `25688779` contributes `120 of 915` participants (`13.1%`); no discordant direction; held cue `36942789: standard therapy`. |
| `corticosteroids-covid19-mortality` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `dapagliflozin-hfpef-hosp` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `denosumab-vertebral-fracture` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `dpp4-mace-t2d` | Tau2=0 note said the PI coincides with the CI. | k=3; smallest trial `28893244` contributes `4202 of 27673` participants (`15.2%`); no discordant direction; small-sample forecast wording. |
| `empagliflozin-hfpef-hosp` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `finerenone-ckd-t2d-renal` | Generic k=2 no-PI note. | k=2; smallest trial `33264825` contributes `5734 of about 13076` participants (`43.9%`; denominator partly inferred); no discordant direction. |
| `iv-iron-hfref-hosp` | No note. | k=2; smallest trial `25176939` contributes `304 of 1409` participants (`21.6%`); no discordant direction. |
| `melatonin-primary-insomnia-sol` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `metformin-pcos-ovulation` | No note. | k=3; smallest trial `11172832` contributes `27 of 284` participants (`9.5%`); discordant direction; tiny discordant trial wording. |
| `sacubitril-valsartan-hfref` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `semaglutide-obesity-mace` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `semaglutide-obesity-weight` | Generic k=2 no-PI note. | k=2; smallest trial `33625476` contributes `611 of 2572` participants (`23.8%`); no discordant direction. |
| `sglt2-ckd-progression` | No note. | k=3; smallest trial `32970396` contributes `4304 of 15314` participants (`28.1%`); no discordant direction; small-sample forecast wording. |
| `sglt2-hfref-hosp-cvdeath` | Generic k=2 no-PI note. | k=2; smallest trial `32865377` contributes `3730 of 8474` participants (`44.0%`); no discordant direction; held cues `31535829: NYHA class II, recommended therapy; 32865377: recommended therapy`. |
| `spironolactone-hfref-mortality` | No note. | k=3; `J-EMPHASIS-HF` contributes `221 of 4621` participants (`4.8%`); discordant direction; tiny discordant trial wording; held cues only from held text: `10471456: severe heart failure, standard therapy; 21073363: NYHA class II, recommended therapy; J-EMPHASIS-HF: NYHA class II-IV, standard therapy`. |
| `statins-primary-prevention-elderly` | Generic k=2 no-PI note. | k=2; smallest trial `20404379` contributes `5695 of about 15325` participants (`37.2%`; denominator partly inferred); no discordant direction. |
| `ticagrelor-vs-clopidogrel-acs` | No note. | k=2; smallest trial `PHILO` contributes `801 of 19425` participants (`4.1%`); discordant direction. |
| `tocilizumab-covid19-mortality` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |
| `tranexamic-acid-pph` | `prediction interval undefined for k=1`. | Adds `small-k context: k=1, single trial`. |

MEASURED final small-k denominator check: no k=2 or k=3 page still contains `share not estimable`.

MEASURED sweep output: `0 pages whose imprecision downgrade rests on the RE superpopulation interval while the common-effect interval excludes the null of 14 pages downgraded for imprecision`; output written to `docs/grade_quantity_sweep.json`.

## 4. Tests And Replay

MEASURED final test commands:

- `python -m pytest tests/test_grade_quantity.py tests/test_grade_integration_floor.py tests/test_grade_global_fixes.py tests/test_stage_additions.py tests/test_k2_refusal.py -x -q` -> `44 passed in 13.56s`.
- `python -m pytest tests -x -q` -> `723 passed in 211.17s (0:03:31)`.
- `git diff --check` -> no output.
- `python scripts/reproduce_review.py <slug>` over all 32 `docs/reviews` slugs -> every invocation printed `1/1 reproduce (all reproducible)` in the final loop.

MEASURED intermediate note: an earlier full pytest run failed with `docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py`. I ran `python scripts/render_fix_ledger.py`, which printed `rendered docs/fix_ledger.json`, and the final full pytest above passed on the refreshed artefacts.

## 5. What I Did Not Do And Why

- No commit, no staging, no stash, no checkout/reset/clean.
- No network or live search.
- Did not run `scripts/verify_all.py`.
- Did not touch `harness/synth.py`, the K2 refusal policy, pooling inputs, membership, or screening.
- Did not write ratchet acknowledgements. The reworded blocks are listed above for the integrator to sign.
- Did not duplicate VS's missing-evidence module because `harness/missing_effect.py` is absent in this clone. I added only merge-compatible `panel_shape` fields in `harness/grade_quantity.py`.
- Did not infer beta-blocker facts for spironolactone unless the held text contained beta-blocker wording; the final held cues do not include a beta-blocker claim.

## 6. Files Changed Or Added

MEASURED code/test/script/report additions or edits:

- `harness/grade.py`
- `harness/pipeline.py`
- `harness/grade_quantity.py`
- `tests/test_grade_quantity.py`
- `scripts/grade_quantity_sweep.py`
- `LANE-KM2-REPORT.md`

MEASURED generated data/ledger:

- `docs/grade_quantity_sweep.json`
- `docs/fix_ledger.json`
- `registry/blind_map.json`

MEASURED generated review outputs: for each of these 32 slugs, the changed files are `REPRODUCTION.json`, `index.html`, `manifest.json`, and `review.json`: `balanced-crystalloids-vs-saline-mortality`, `colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `dapagliflozin-hfpef-hosp`, `denosumab-vertebral-fracture`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `esketamine-trd-madrs`, `finerenone-ckd-t2d-renal`, `glp1-ra-mace-t2d`, `iv-iron-hfref-hosp`, `melatonin-primary-insomnia-sol`, `metformin-pcos-ovulation`, `noac-vs-warfarin-af-stroke`, `omega3-cardiovascular-events`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-ckd-progression`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `spironolactone-hfref-mortality`, `statins-primary-prevention-elderly`, `ticagrelor-vs-clopidogrel-acs`, `tocilizumab-covid19-mortality`, `tranexamic-acid-pph`.

MEASURED generated blind-page outputs: `docs/m/m0594e053/index.html`, `docs/m/m078be06c/index.html`, `docs/m/m0c0e2bf1/index.html`, `docs/m/m175bd0c3/index.html`, `docs/m/m22bf81d5/index.html`, `docs/m/m24cd09bc/index.html`, `docs/m/m250220c2/index.html`, `docs/m/m2da64325/index.html`, `docs/m/m3c1155fb/index.html`, `docs/m/m5384fd3c/index.html`, `docs/m/m586876fa/index.html`, `docs/m/m5b3fd56c/index.html`, `docs/m/m5e5590d5/index.html`, `docs/m/m612a48aa/index.html`, `docs/m/m6dd4233b/index.html`, `docs/m/m6e7e8ab7/index.html`, `docs/m/m87167438/index.html`, `docs/m/m89f8021b/index.html`, `docs/m/m8db5253b/index.html`, `docs/m/m979b0810/index.html`, `docs/m/ma0b91971/index.html`, `docs/m/maf69923c/index.html`, `docs/m/mb53e1ed5/index.html`, `docs/m/mb6ceb13c/index.html`, `docs/m/mc16cd596/index.html`, `docs/m/md68c6ad6/index.html`, `docs/m/mdd4bf0ae/index.html`, `docs/m/me0751432/index.html`, `docs/m/me17c0a34/index.html`, `docs/m/me5d639f4/index.html`, `docs/m/me79cb3b0/index.html`, `docs/m/mf6cd36c2/index.html`.

MEASURED pre-existing untracked lane-control files present and not authored by this work: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
