# LANE SH2 Report

## 1. What was wrong, mechanism, files

MEASURED problems fixed:

- `sglt2-hfref-hosp-cvdeath`: the SH selector inherited the extractor's count-first behavior and did not surface same-sentence published HRs. DAPA-HF and EMPEROR-Reduced stayed as reconstructed count RRs with empty alternatives. I added a source-hierarchy candidate pass over committed abstract/full-text/verified-effect source text, outside `harness/extract.py`.
- `colchicine-postop-af`: a published OR was treated as selectable under an RR/first-event outcome. `ODDS_RATIO` is now a non-target class candidate and is retained only as an alternative with `NOT_TARGET_CLASS`.
- Outcome scale was still row-local. I added outcome-level `estimand_decision` and `served_estimand`, then used that decision before row selection, pooling, and rendering. Tocilizumab remains declared `OR`, but the served target scale is `RR` because the only target published effect is RR.
- Balanced crystalloids now records source-limit mixing: PLUS has counts only in the committed abstract while BaSICS supplies a published HR. PLUS gets `MIXED_BY_SOURCE_LIMIT` with citation `SOURCE_NOT_RETRIEVED_FULL_TEXT_NEEDED`.
- Metformin PCOS proportion-derived rows now carry `derivation: reconstructed_from_proportions`.

Main implementation files:

- `harness/source_hierarchy.py`: new candidate surfacing, outcome estimand decision, mixed-source limitation helpers.
- `harness/pipeline.py`: calls the outcome decision and source-hierarchy helper before selection/pooling; preserves explicit derivation subtypes.
- `harness/design_key.py`: OR is no longer target class for RR/HR outcomes; reconstructed subtypes are treated as reconstructed for design gates without overwriting their explicit label.
- `harness/page.py`: renders the estimand decision in overview/results method rows.

Static-vs-dynamic hardcode disclosure:

| Item | Type | Reason |
| --- | --- | --- |
| `PMID 35041780` PLUS source-limit message | Static identifier with dynamic source result | Named by the lane; text records that the committed abstract lacks HR and full text is needed. |
| `reconstructed_from_proportions` labels in metformin cache | Static provenance label | Applied only to rows whose counts already come from committed proportion x N entries. |
| Source-effect candidates | Dynamic | Parsed from committed abstracts/full text/verified effects at build time. |
| Sweep counts, changed rows, pooled estimates | Dynamic | Recomputed by `scripts/source_hierarchy_sweep.py` and rebuilt review objects. |
| Error-rate/fix-ledger/integrity derived artifacts | Dynamic | Refreshed because tests refused stale derived state after the corpus rebuild. |

## 2. Plant checks

Added `tests/test_source_hierarchy_regression.py`.

Pre-fix plants read committed objects with `git show ad5e7c66:...`:

- `test_sglt2_abstract_hr_candidates_are_surfaced_and_selected`: asserts the pre-fix SGLT2 rows have `effect is None`, then asserts the committed DAPA-HF abstract contains `hazard ratio, 0.74` and the new candidate pass finds HR 0.74. Post-fix asserts both rebuilt rows select HRs, result scale `HR`, estimate `0.7448`, audit HKSJ CI `0.3975-1.3954`.
- `test_colchicine_or_is_non_target_alternative_under_rr_outcome`: asserts the 32720823 count row remains 13/81 vs 13/71 and the OR 0.85 is an alternative with `NOT_TARGET_CLASS`.
- `test_tocilizumab_estimand_decision_controls_served_scale_and_renders`: asserts declared `OR`, served `RR`, decision `cumulative_risk_at_trial_end`, result scale `RR`, and rendered Methods text includes `Estimand decision`, `declared OR`, `Target scale RR`.
- Synthetic controls assert a RATE/IRR effect is never selected for a first-event RR outcome, and a counts-only row keeps `KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT`.

Related SH plant retained/updated in `tests/test_source_hierarchy.py`: J-EMPHASIS-HF pre-prefix limitation fires on the committed old object and passes on the rebuilt object.

Post-fix targeted outputs:

- `python -m pytest tests/test_derivation.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py -q` -> `16 passed in 11.13s`
- `python -m pytest tests/test_uoa_sensitivity.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py -q` -> `14 passed in 13.56s`

## 3. Pages, numbers, and corpus sweep

All 32 live review pages were rebuilt from committed cache with `--now 2026-09-11` and reproduced.

MEASURED source-hierarchy sweep:

- `12 rows changed of 118 pooled rows over 32 topics`
- The prompt's SH baseline was CLAIMED as `5 of 115`; the final current denominator is MEASURED as 118 live pooled rows.

Changed rows:

1. `balanced-crystalloids-vs-saline-mortality | PMID 34375394`: counts RR 0.9707 -> HR 0.97 [0.90, 1.05]; pool RR 0.9725 [0.8650, 1.0932] -> HR 0.9725 [0.8508, 1.1117].
2. `balanced-crystalloids-vs-saline-mortality | PMID 26444692` mortality: counts RR 0.8824 -> RR 0.88 [0.67, 1.17]; pool RR 0.9727 [0.8509, 1.1119] -> HR 0.9725 [0.8508, 1.1117].
3. `balanced-crystalloids-vs-saline-mortality | PMID 26444692` AKI: counts RR 1.0424 -> RR 1.04 [0.80, 1.36]; pool RR 1.0424 [0.7983, 1.3611] -> RR 1.04 [0.80, 1.36].
4. `balanced-crystalloids-vs-saline-mortality | PMID 26444692` RRT: counts RR 0.9635 -> RR 0.96 [0.62, 1.50]; pool RR 0.9814 [0.3963, 2.4303] -> RR 0.981 with k=2 CI refused.
5. `colchicine-recurrent-pericarditis | PMID 24694983`: counts RR 0.5098 -> RR 0.49 [0.24, 0.65]; pool RR 0.4813 [0.0640, 3.6169] -> RR 0.4643 with k=2 CI refused.
6. `doac-vte-recurrence | PMID 23808982`: counts RR 0.8393 -> RR 0.84 [0.60, 1.18]; pool HR 0.9092 [0.7478, 1.1054] -> HR 0.9091 [0.7479, 1.1050].
7. `omega3-cardiovascular-events | PMID 33190147`: counts RR 0.9874 -> HR 0.99 [0.90, 1.09]; pool RR 0.9430 [0.8460, 1.0510] -> HR 0.9433 [0.8461, 1.0517].
8. `probiotics-aad-prevention | PMID 7872284`: counts RR 0.4948 -> RR 0.29 [0.08, 0.98]; pool RR 0.7020 [0.5352, 0.9210] -> RR 0.6907 [0.5193, 0.9187].
9. `sglt2-hfref-hosp-cvdeath | PMID 31535829`: counts RR 0.7683 -> HR 0.74 [0.65, 0.85]; pool RR 0.7605 [0.4215, 1.3722] -> HR 0.7448; audit HKSJ CI 0.3975-1.3954.
10. `sglt2-hfref-hosp-cvdeath | PMID 32865377`: counts RR 0.7831 -> HR 0.75 [0.65, 0.86]; pool RR 0.7633 [0.4254, 1.3695] -> HR 0.7448; audit HKSJ CI 0.3975-1.3954.
11. `spironolactone-hfref-mortality | PMID 28824029`: counts RR 1.6847 -> HR 0.85 [0.53, 1.36]; pool RR/HR 0.8685 [0.3062, 2.4635] -> HR 0.7294 [0.5609, 0.9486].
12. `tocilizumab-covid19-mortality | PMID 33933206`: counts OR 0.83 [0.7285, 0.9456] -> RR 0.85 [0.76, 0.94]; pool OR 0.83 [0.7285, 0.9456] -> RR 0.85 [0.76, 0.94].

Named lane checks:

- SGLT2 primary result is `HR 0.7448`, k=2, tau2 0.0, audit HKSJ CI `0.3975-1.3954`; both rows `PUBLISHED_EFFECT_TARGET_CLASS`.
- Colchicine postop-AF PMID 32720823 remains count reconstructed 13/81 vs 13/71; OR 0.85 [0.37, 1.99] is alternative `NOT_TARGET_CLASS`, detail `ODDS_RATIO!=FIRST_EVENT_RATIO`.
- Tocilizumab outcome carries `estimand_decision`: declared `OR`, target `RR`, served scale changed because only published effect+CI is RR.
- Balanced crystalloids primary result is `HR 0.9725 [0.8508, 1.1117]`, k=3, with `scale_mixed: HR, RR`. PLUS has `MIXED_BY_SOURCE_LIMIT` and `SOURCE_NOT_RETRIEVED_FULL_TEXT_NEEDED`.
- Metformin PCOS rows `PMID 19522426` and `PMID 16769748` have `derivation: reconstructed_from_proportions`.

Corpus-wide estimand decision count:

- MEASURED: `12 of 83` outcomes have `estimand_decision.served_scale_changed = true`.
- Changed served-scale outcomes: balanced mortality; corticosteroids COVID mortality; denosumab hip/new-vertebral/nonvertebral fracture; IV iron HF hospitalization; omega-3 MACE; SGLT2 HFrEF composite; spironolactone mortality; statins elderly major vascular events; ticagrelor major bleeding; tocilizumab mortality.

Pages rebuilt: balanced-crystalloids-vs-saline-mortality, colchicine-postop-af, colchicine-recurrent-pericarditis, colchicine-secondary-cv-prevention, corticosteroids-cap-mortality, corticosteroids-covid19-mortality, dapagliflozin-hfpef-hosp, denosumab-vertebral-fracture, doac-vte-recurrence, dpp4-mace-t2d, empagliflozin-hfpef-hosp, esketamine-trd-madrs, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, iv-iron-hfref-hosp, melatonin-primary-insomnia-sol, metformin-pcos-ovulation, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace, probiotics-aad-prevention, sacubitril-valsartan-hfref, semaglutide-obesity-mace, semaglutide-obesity-weight, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf, spironolactone-hfref-mortality, statins-primary-prevention-elderly, ticagrelor-vs-clopidogrel-acs, tocilizumab-covid19-mortality, tranexamic-acid-pph.

## 4. Verification

Commands run after SH2 work:

- `python -m pytest tests/test_source_hierarchy.py -q` after applying SH patch and resolving rejects -> `8 passed in 7.03s`
- `python scripts/source_hierarchy_sweep.py` -> `12 rows changed of 118 pooled rows over 32 topics`
- `python scripts/reproduce_review.py` -> `32/32 reproduce (all reproducible)`
- `python -m pytest tests/test_derivation.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py -q` -> `16 passed in 11.13s`
- `python -m pytest tests/test_uoa_sensitivity.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py -q` -> `14 passed in 13.56s`
- `python -m pytest tests/test_fixstate.py::test_real_store_validates -q` -> `1 passed in 376.52s (0:06:16)`
- `python -m pytest tests -x -q` -> `726 passed in 997.07s (0:16:37)`

Derived artifact repairs needed to keep tests honest:

- `python scripts/render_fix_ledger.py`
- `python scripts/rewrite_fixstate_lines.py`
- `python -m harness.index docs`
- `python scripts/integrity_check.py balanced-crystalloids-vs-saline-mortality` because `test_integrity` refused stale integrity after SPLIT became live again. This was the only networked refresh; no search/retrieval was rerun.

## 5. What I did not do

- Did not commit, stage, stash, checkout, reset, or clean.
- Did not edit `harness/extract.py`, `harness/synth.py`, `harness/estmeasure.py`, `harness/rob_sensitivity.py`, `harness/grade.py`, or search code.
- Did not rerun discovery searches or add new trials by search. All review rebuilds used committed cache.
- Did not write ratchet acknowledgements; any new/reworded generated limitation text is left for integrator review/signoff.

## 6. Files changed or added

Code/tests added or changed:

- `harness/source_hierarchy.py` (added)
- `harness/pipeline.py`
- `harness/design_key.py`
- `harness/page.py`
- `scripts/source_hierarchy_sweep.py` (added from SH patch)
- `tests/test_source_hierarchy.py`
- `tests/test_source_hierarchy_regression.py` (added)
- `tests/test_derivation.py`
- `tests/test_uoa_sensitivity.py`

Source/derived data changed:

- `cache/metformin-pcos-ovulation/verified_arms.json`
- `cache/spironolactone-hfref-mortality/verified_arms.json`
- `cache/balanced-crystalloids-vs-saline-mortality/integrity.json`
- `docs/source_hierarchy_sweep.json`
- `docs/error_rate.json`
- `docs/fix_ledger.json`
- `docs/evidence/design-key-2026-09-14/README.md`
- `docs/index.html`
- `registry/blind_map.json`
- `LANE-SH2-REPORT.md`

Generated review artifacts changed for all 32 live slugs listed above:

- `docs/reviews/<slug>/review.json`
- `docs/reviews/<slug>/index.html`
- `docs/reviews/<slug>/manifest.json`
- `docs/reviews/<slug>/REPRODUCTION.json`

Generated blind mirror artifacts changed:

- `docs/m/*/index.html` for the live blind mirrors regenerated by the 32 page rebuilds.

Existing untracked lane inputs left untouched:

- `LANE_PROMPT.md`
- `SH.patch`
- `LANE-SH-REPORT.md`
- `lane.log`, `lane.pid`, `lane.winpid`
