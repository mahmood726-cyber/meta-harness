# LANE-IN integration report

## 0. Scope and base

MEASURED actual `git rev-parse HEAD`: `dd2403f56a1025c011e6d6a601d25817aab3c9e7`.

The prompt claimed the clone was at `aa8ed28a`, but the checked-out HEAD was `dd2403f56a1025c011e6d6a601d25817aab3c9e7`. I measured against both where useful.

No commit was made. No real `git add` was used; patch application used a temporary index because the real `.git/index.lock` was not writable and the lane standing rules prohibited touching `.git`.

AGENTS session-start files were checked first: `F:\ProjectIndex\INDEX.md` and `F:\E156\rewrite-workbook.txt` were readable. I did not edit them because this lane did not change portfolio status/submission state.

## 1. What was wrong, mechanism, files

This lane integrated harvested patches EX, RX, TE, XS2, SC, SC2, SC3, CP2, CP3, CG2, SH2, CK2, CX, FU, CK3, D5, EN2, SE, and HM.partial. The recurring failure class was "detected hazard without a wired consumer": retrieved-but-unextracted outcomes, false declared absence, stale comparator/parity strings, post-hoc endpoint drift, unconsumable design variance, stale RoB joins, harms panels that rendered absence while sources reported harms, and cross-source endpoint mismatches.

Root mechanisms fixed:

- Absence ontology and consumers: `harness/absence.py`, `harness/pipeline.py`, `harness/page.py`, `harness/limitations.py`, `harness/hazard_consumers.py`.
- Comparator/parity/claim graph: `harness/comparator_truth.py`, `harness/comparator_second_pass.py`, `harness/parity_relation.py`, `harness/claimgraph.py`, `harness/propositions.py`, `harness/gate.py`.
- Endpoint/source hierarchy: `harness/target_endpoint.py`, `harness/second_source.py`, `harness/source_hierarchy.py`, `harness/ctgov_results.py`, `harness/endpoint_canonical.py`, `harness/compat_check.py`, `harness/compat_direction.py`.
- Design/RoB: `harness/design_key.py`, `harness/design_variance.py`, `harness/rob2.py`, `scripts/rob2_build.py`, `cache/*/rob2.json`, `cache/*/registry_designs.json`.
- Screening/contrast: `harness/screen.py`, `harness/screen_entry.py`, `harness/arm_object.py`, `harness/armcontrast.py`.
- Harms: `harness/harms.py`, `scripts/harms_recovery_sweep.py`, `tests/test_harms_recovery.py`, `docs/harms_recovery_sweep.json`.
- Funding/source provenance: `harness/funding.py`, `scripts/funding_sweep.py`, `docs/funding_sweep.json`.

Integrator-note core fixes applied:

- `scripts/rob2_build.py --write` now writes `cache/<slug>/registry_designs.json` for every topic NCT known from records/ctgov/designs.
- `harness/design_key.registry_designs(records)` reads and merges that cache by uppercased NCT.
- Unknown design/unit now yields `DESIGN_UNPROVEN` with gate id `design-key:design-unproven` and decision state containing: `design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify`.
- `DESIGN_UNPROVEN` is rendered as `UNPROVEN`.
- `_match >= 0.45` was retained in `scripts/rob2_build.py` and `scripts/rob_rederivation_sweep.py` per integrator note.

## 2. Conflict resolutions, hand listed

- EX: `harness/absence.py` kept base `OUTCOME_POST_HOC_NOT_POOLED` / `OUTCOME_NOT_REPORTED` plus EX retrieved states. `harness/pipeline.py` kept CK/known-missing path and added EX consumer consistency.
- RX: `harness/pipeline.py` kept `consumer_consistency`, `reason_audit`, `unextracted` imports/calls plus source map.
- XS2: `harness/pipeline.py` import kept `target_endpoint` plus `second_source`.
- SC: `harness/page.py` absent row kept `_id_cell(t)` and added completeness state/basis.
- SC2: `harness/pipeline.py`, `harness/screen.py` kept AACT/screen-entry/armcontrast plus SC2 contrast eviction and `annotate_decision`.
- SC3: `harness/pipeline.py` metadata kept screen-entry extras and arm object fields; `harness/screen.py` kept arm background-only and arm-object refusal; `registry/gate_scorecard.json` kept both additive entries.
- CP2: `harness/pipeline.py` kept AACT/screen-entry/comparator-second-pass/parity-relation.
- CP3: `harness/pipeline.py` comparator annotation kept `comparator_second_pass.apply` then `comparator_truth.annotate_comparator`.
- CG2: `harness/gate.py` imports kept compat check plus propositions; `harness/pipeline.py` kept target endpoint, second source, propositions; `registry/gate_scorecard.json` kept claimgraph/proposition gate entries.
- SH2: `harness/pipeline.py` kept source hierarchy with other imports; `harness/page.py` kept consumer consistency and SH2 source hierarchy block; `docs/error_rate.json` chose SH2 value 118 initially, later refreshed to 119 after current census accounting.
- CK2: kept `gate.py` compat/propositions/eligibility-chain imports/checks; `pipeline.py` compat/known-missing/consumer-consistency/RX audits plus eligibility-chain apply; `screen.py` comparator extras/overrides; `page.py` `_alternative_label` and `_eligibility_chain_block`; `hazard_consumers.py` compat underlying plus eligibility-chain runners; topic and gate-scorecard additions.
- CX: `absence.py` kept prior absence states plus `ENGINE_CANNOT_CONSUME`; `page.py` label and protocol/arm blocks; `pipeline.py` source hierarchy plus design variance, design refusal via `design_variance.refusal_absence`, grade design variance/target endpoint.
- FU: `limitations.py` and `page.py` funding block kept FU held text plus registry-sponsor/source-disagreement wording/evidence table; page imports kept propositions and funding.
- CK3: `pipeline.py` imports kept compat check plus compat direction; `page.py` kept `_alternative_label`, `_eligibility_chain_block`, added `_compat_direction_block`; compatibility section kept compat underlying plus compat direction.
- D5: generated `cache/*/rob2.json` and `docs/rob_rederivation_sweep.json` took D5 blobs; `compat.py` docstring kept parser-confirmed contrast wording; `gate.py` kept embed cosine `_match` and `rob2.rederivation_violations(rev, _match)`; GRADE text merged D5 registry-machine-signal wording; `rob2.py` kept expanded components; `_match >= 0.45` retained.
- EN2: `compat.py` kept endpoint canonical/analysis detail/effect label and D5 parser coverage; endpoint key uses endpoint label if present else component-defined/composite/single; `_apply_trial_annotations` allowed CK3 plus EN2 fields; page trial details kept CK3 plus EN2 fields.
- SE: imports merged; `gate.py` has compat-key-underlying plus scope identity; `pipeline.py` keeps target endpoint, second source, propositions, eligibility chain, scope identity; page keeps propositions/funding/scope identity; gate scorecard kept limitation-decision-links, known-missing, eligibility-chain, scope-identity, verify-all entries.
- HM.partial: added harms module/sweep/tests/docs and kept harms additive. `pipeline.py` calls `harms_mod.annotate_review` after previous annotations; `gate.py` kept proposition and eligibility-chain checks plus `check_harms_complete`; `page.py` absent rows keep completeness fields plus HM `harm_absence_state`; `registry/gate_scorecard.json` has separate proposition and harms-complete gates. HM was not reverted; after fixes full suite passed.

## 3. The plant

Representative plant/failure transitions:

- `tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews`
  - Pre-fix failure: page rendered an extra block not represented as a structured limitation:
    `PAGE: HARMS_INCOMPLETE. HARMS_INCOMPLETE -- 4 known reported outcome(s) unresolved (42132185, 36286314, 32720823, 25172965) ...`
  - Mechanism: `harness/page.py` rendered harms-incomplete blocks for non-absent harm results and no-harm registry-state scans; `harness/limitations.py` only modeled the absent-result shape.
  - Post-fix output: `1 passed in 3.62s`.

- `tests/test_rob_coverage.py::test_every_pooled_primary_trial_is_rob_assessed`
  - Pre-fix failure: `sacubitril-valsartan-hfref: ['NCT02468232'] [98/99]`.
  - Mechanism: PARALLEL-HF entered the primary pool after rebuild, but `cache/sacubitril-valsartan-hfref/rob2.json` only assessed PARADIGM-HF.
  - Post-fix output: `1 passed in 0.74s`; `rob2_build.py --write sacubitril-valsartan-hfref` printed `25176015=some concerns; NCT02468232=low`.

- `tests/test_screen_contrast_and_ledger.py::test_required_prefixed_plants_transition_on_current_replay`
  - Pre-fix failure: `assert 'Balcinrenone' in '... balcinrenone ... dapagliflozin ...'`.
  - Mechanism: curated contrast-eviction basis text was lower-case, while source/title casing was required for visible display.
  - Post-fix output: `1 passed in 21.56s`; paired `tests/test_screen_entry.py::test_miro_ckd_is_evicted_as_absent_sglt2_contrast` also passed after making its content assertion case-insensitive.

- `tests/test_source_hierarchy_regression.py::test_sglt2_abstract_hr_candidates_are_surfaced_and_selected`
  - Pre-fix failure after target-endpoint merge: `assert 0.75 == 0.74`.
  - Mechanism: the abstract HR 0.74 candidate is still surfaced, but the current selector uses CT.gov structured target endpoint HR 0.75 because it matches CV death or HF hospitalization rather than broader worsening HF.
  - Post-fix output: `5 passed in 3.72s`.

- `tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population`
  - Pre-fix failure: `error_rate.json population != committed sample size`, `122 == 121` failed; live recomputation then showed 4 uncensused live rows and 3 unaccounted removed balanced-crystalloid rows.
  - Mechanism: post-merge page rebuilds changed the pooled population/sample accounting.
  - Post-fix output: `1 passed in 2.42s`.

- `tests/test_uoa_sensitivity.py::test_crystalloids_uoa_caveat_matches_post_refusal_factorial_state`
  - Pre-fix failure: expected `["cluster-randomized crossover", "factorial"]`, got `["factorial"]`.
  - Mechanism: cluster-crossover rows now live under typed `design_refusal` / `ENGINE_CANNOT_CONSUME`, while the UOA caveat covers only the remaining pooled factorial marginal design.
  - Post-fix output: `1 passed in 2.29s`.

Additional targeted green checks:

- `python -m pytest tests/test_compat_direction.py -q` -> `6 passed in 1.07s`
- `python -m pytest tests/test_consumer_consistency.py -q` -> `6 passed in 1.10s`
- `python -m pytest tests/test_target_endpoint.py tests/test_cross_source_endpoint.py tests/test_second_source_identity.py -q` -> `15 passed in 55.43s`
- `python -m pytest tests/test_design_key.py -q` -> `5 passed in 0.70s`
- `python -m pytest tests/test_design_variance.py -q` -> `9 passed in 2.70s`
- `python -m pytest tests/test_endpoint_canonical.py -q` -> `7 passed in 1.05s`
- `python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q` -> `1 passed in 21.20s`
- `python -m pytest tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic -q` -> `1 passed in 2.74s`
- `python -m pytest tests/test_harms_recovery.py -q` -> `4 passed in 3.20s`
- `python -m pytest tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews -q` -> `1 passed in 3.62s`

## 4. Pages rebuilt/changed and measured before/after

All 32 review pages were rebuilt and their `docs/reviews/<slug>/index.html` bytes changed relative to actual HEAD:

`balanced-crystalloids-vs-saline-mortality`, `colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `corticosteroids-covid19-mortality`, `dapagliflozin-hfpef-hosp`, `denosumab-vertebral-fracture`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `esketamine-trd-madrs`, `finerenone-ckd-t2d-renal`, `glp1-ra-mace-t2d`, `iv-iron-hfref-hosp`, `melatonin-primary-insomnia-sol`, `metformin-pcos-ovulation`, `noac-vs-warfarin-af-stroke`, `omega3-cardiovascular-events`, `pcsk9-mace`, `probiotics-aad-prevention`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `semaglutide-obesity-weight`, `sglt2-ckd-progression`, `sglt2-hfref-hosp-cvdeath`, `sglt2-primary-prevention-hf`, `spironolactone-hfref-mortality`, `statins-primary-prevention-elderly`, `ticagrelor-vs-clopidogrel-acs`, `tocilizumab-covid19-mortality`, `tranexamic-acid-pph`.

MEASURED primary result object changes:

- Against prompt baseline `aa8ed28a`: 21 of 32 primary result objects changed.
- Against actual HEAD `dd2403f56a1025c011e6d6a601d25817aab3c9e7`: 16 of 32 primary result objects changed.

Against actual HEAD, the changed primary result objects were:

- `balanced-crystalloids-vs-saline-mortality`: scale `RR` -> `HR`, estimate unchanged `0.9774`, served CI still refused.
- `colchicine-recurrent-pericarditis`: estimate `0.4813` -> `0.4643`, k=2 CI refused.
- `colchicine-secondary-cv-prevention`: outcome label `Major adverse cardiovascular events` -> `Trial-defined major coronary/cardiovascular composite`, estimate unchanged `0.8134 HR`.
- `dapagliflozin-hfpef-hosp`: `HR 0.82 (0.73-0.92)` -> `HR 0.88 (0.74-1.05)` for the structured target endpoint.
- `doac-vte-recurrence`: label refined to symptomatic recurrent VTE; `0.9092` -> `0.9091` HR rounding.
- `empagliflozin-hfpef-hosp`: `HR 0.79 (0.69-0.90)` -> `HR 0.91 (0.76-1.09)` for the structured target endpoint.
- `esketamine-trd-madrs`: label refined to `Observed-case Day-28 raw change-score MADRS MD`, estimate unchanged `-3.3445`.
- `metformin-pcos-ovulation`: label refined to `Ovulation with metformin added to clomifene`, estimate unchanged `2.0733 OR`.
- `omega3-cardiovascular-events`: scale/effect `RR 0.943 (0.846-1.051)` -> `HR 0.9602 (0.8551-1.0783)`.
- `pcsk9-mace`: `HR 0.83 (0.7147-0.9638)` -> `HR 0.8106 (0.7032-0.9344)`.
- `probiotics-aad-prevention`: `RR 0.702 (0.5352-0.921)` -> `RR 0.6907 (0.5193-0.9187)`.
- `sacubitril-valsartan-hfref`: k `1` -> `2`, trials `25176015` -> `25176015, PARALLEL-HF`, pooled estimate suppressed/refused at k=2 mixed target state.
- `sglt2-ckd-progression`: label refined to `Trial-defined primary cardiorenal composite`, estimate unchanged `0.6836 HR`.
- `sglt2-hfref-hosp-cvdeath`: `RR 0.7755` -> `HR 0.75`, k=2 CI refused.
- `spironolactone-hfref-mortality`: `RR/HR 0.8685 (0.3062-2.4635)` -> `HR 0.7294 (0.5609-0.9486)`.
- `tocilizumab-covid19-mortality`: `OR 0.83 (0.7285-0.9456)` -> `RR 0.85 (0.76-0.94)`.

MEASURED `before_after.py aa8ed28a C:\mh-r-IN`:

```text
[aa8ed28a] pages N=32; pooled k>=2 with a served estimate: 22
  stale RoB sensitivity (rated trial invisible to the re-pool): 6 of 32: ['colchicine-secondary-cv-prevention', 'esketamine-trd-madrs', 'glp1-ra-mace-t2d', 'iv-iron-hfref-hosp', 'spironolactone-hfref-mortality', 'ticagrelor-vs-clopidogrel-acs']
  false 'fewer trials than the full pool' rendered: 17 of 32: ['balanced-crystalloids-vs-saline-mortality', 'colchicine-postop-af', 'colchicine-recurrent-pericarditis', 'dapagliflozin-hfpef-hosp', 'denosumab-vertebral-fracture', 'dpp4-mace-t2d', 'empagliflozin-hfpef-hosp', 'finerenone-ckd-t2d-renal', 'melatonin-primary-insomnia-sol', 'noac-vs-warfarin-af-stroke', 'pcsk9-mace', 'probiotics-aad-prevention', 'sacubitril-valsartan-hfref', 'semaglutide-obesity-weight', 'sglt2-ckd-progression', 'sglt2-hfref-hosp-cvdeath', 'statins-primary-prevention-elderly']
  k=2 primaries serving a pooled CI: 9 of 32: ['balanced-crystalloids-vs-saline-mortality', 'colchicine-recurrent-pericarditis', 'corticosteroids-cap-mortality', 'finerenone-ckd-t2d-renal', 'pcsk9-mace', 'semaglutide-obesity-weight', 'sglt2-hfref-hosp-cvdeath', 'statins-primary-prevention-elderly', 'ticagrelor-vs-clopidogrel-acs']
  hand 'PARITY*' status word rendered without a computed relation: 8 of 32: ['finerenone-ckd-t2d-renal', 'glp1-ra-mace-t2d', 'noac-vs-warfarin-af-stroke', 'pcsk9-mace', 'semaglutide-obesity-weight', 'sglt2-hfref-hosp-cvdeath', 'spironolactone-hfref-mortality', 'ticagrelor-vs-clopidogrel-acs']
  STALE: 32 of 32; reasons: {'eligible_declared_absent': 27, 'identifier_single_agent_class_pool': 1, 'known_eligible_missing': 6, 'never_considered': 2, 'no_checkable_claim': 1, 'search_not_executed': 32}
```

MEASURED `before_after.py tree C:\mh-r-IN`:

```text
[tree] pages N=32; pooled k>=2 with a served estimate: 21
  stale RoB sensitivity (rated trial invisible to the re-pool): 3 of 32: ['iv-iron-hfref-hosp', 'sacubitril-valsartan-hfref', 'ticagrelor-vs-clopidogrel-acs']
  false 'fewer trials than the full pool' rendered: 0 of 32: []
  k=2 primaries serving a pooled CI: 0 of 32: []
  hand 'PARITY*' status word rendered without a computed relation: 0 of 32: []
  STALE: 32 of 32; reasons: {'eligible_declared_absent': 27, 'known_eligible_missing': 6, 'never_considered': 2, 'no_checkable_claim': 1, 'search_not_executed': 32}
```

MEASURED design-key state after rebuild: design actions in review objects were `{'DESIGN_UNPROVEN': 225, 'ALLOW_WITH_LABEL': 12, 'REFUSE': 10}`. `DESIGN_UNPROVEN` rows carry decision state `design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify`.

## 5. Tests and reproduction

Final full suite:

```text
869 passed in 411.03s (0:06:51)
```

Final reproduction:

```text
32/32 reproduce (all reproducible)
```

Final sweeps/regen run:

- `python scripts/rob_rederivation_sweep.py` -> `0 ratings not reproducible from their own rule of 396 machine ratings over 32 topics`
- `python scripts/d5_rule_sweep.py` -> D1/D2/D4/D5 all `0 of 99`; `19 trials D5 changed of 97 pooled trials`
- `python scripts/harms_recovery_sweep.py` -> `OUT_WRITTEN C:\mh-r-IN\docs\harms_recovery_sweep.json incomplete=36 of 47 harm outcomes; known_debt=153 trials`
- Final regen commands completed: `render_fix_ledger.py`, `rewrite_fixstate_lines.py`, `build_evidence_index.py`, `render_gate_gaps.py`, `render_gate_scorecard.py`, `external_agreement.py`, `python -m harness.index docs`.

## 6. What I did not do and why

- Did not commit. The user explicitly said "Do not commit."
- Did not run `scripts/verify_all.py`. The first part of the prompt asked for it, but the standing rules later explicitly said `Do NOT run scripts/verify_all.py`; I followed the standing rule and report this as not done.
- Did not write acknowledgements for honest-ratchet/verify-all limbs because `verify_all.py` was not run.
- Did not intentionally re-run searches. However, `python scripts/rob2_build.py --write` emitted: `Warning: You are sending unauthenticated requests to the HF Hub... Loading weights...`; this appears to come from the embedding loader. Also `python scripts/integrity_check.py balanced-crystalloids-vs-saline-mortality` was run and may use PubMed efetch by implementation. Both are reported here rather than hidden.
- Did not touch `.git`, did not stop/kill/signal processes, did not run `git commit`, `git stash`, `git checkout`, `git reset`, or `git clean`.

## 7. Changed/added file inventory

Generated by `git diff --name-only HEAD --` plus `git ls-files --others --exclude-standard`; includes pre-existing untracked lane inputs in the clone root where Git reports them as untracked. `LANE-IN-REPORT.md` is included manually because this report is the final artifact.

```text
LANE-IN-REPORT.md
cache/balanced-crystalloids-vs-saline-mortality/arm_contrast.json
cache/balanced-crystalloids-vs-saline-mortality/integrity.json
cache/balanced-crystalloids-vs-saline-mortality/rob2.json
cache/colchicine-postop-af/rob2.json
cache/colchicine-recurrent-pericarditis/rob2.json
cache/colchicine-secondary-cv-prevention/rob2.json
cache/colchicine-secondary-cv-prevention/verified_effects.json
cache/corticosteroids-cap-mortality/rob2.json
cache/corticosteroids-covid19-mortality/rob2.json
cache/dapagliflozin-hfpef-hosp/rob2.json
cache/denosumab-vertebral-fracture/rob2.json
cache/doac-vte-recurrence/rob2.json
cache/dpp4-mace-t2d/rob2.json
cache/embeddings.json
cache/empagliflozin-hfpef-hosp/rob2.json
cache/esketamine-trd-madrs/rob2.json
cache/esketamine-trd-madrs/verified_arms.json
cache/finerenone-ckd-t2d-renal/rob2.json
cache/glp1-ra-mace-t2d/rob2.json
cache/iv-iron-hfref-hosp/rob2.json
cache/melatonin-primary-insomnia-sol/rob2.json
cache/metformin-pcos-ovulation/rob2.json
cache/metformin-pcos-ovulation/verified_arms.json
cache/noac-vs-warfarin-af-stroke/rob2.json
cache/omega3-cardiovascular-events/rob2.json
cache/pcsk9-mace/rob2.json
cache/probiotics-aad-prevention/rob2.json
cache/sacubitril-valsartan-hfref/arm_contrast.json
cache/sacubitril-valsartan-hfref/rob2.json
cache/semaglutide-obesity-mace/rob2.json
cache/semaglutide-obesity-weight/rob2.json
cache/sglt2-ckd-progression/rob2.json
cache/sglt2-ckd-progression/verified_effects.json
cache/sglt2-hfref-hosp-cvdeath/rob2.json
cache/sglt2-primary-prevention-hf/rob2.json
cache/spironolactone-hfref-mortality/rob2.json
cache/spironolactone-hfref-mortality/verified_arms.json
cache/statins-primary-prevention-elderly/rob2.json
cache/ticagrelor-vs-clopidogrel-acs/rob2.json
cache/tocilizumab-covid19-mortality/rob2.json
cache/tranexamic-acid-pph/rob2.json
cache/balanced-crystalloids-vs-saline-mortality/registry_designs.json
cache/colchicine-postop-af/registry_designs.json
cache/colchicine-recurrent-pericarditis/registry_designs.json
cache/colchicine-secondary-cv-prevention/registry_designs.json
cache/corticosteroids-cap-mortality/registry_designs.json
cache/corticosteroids-covid19-mortality/registry_designs.json
cache/dapagliflozin-hfpef-hosp/registry_designs.json
cache/denosumab-vertebral-fracture/registry_designs.json
cache/doac-vte-recurrence/registry_designs.json
cache/dpp4-mace-t2d/registry_designs.json
cache/empagliflozin-hfpef-hosp/registry_designs.json
cache/esketamine-trd-madrs/registry_designs.json
cache/finerenone-ckd-t2d-renal/registry_designs.json
cache/glp1-ra-mace-t2d/registry_designs.json
cache/iv-iron-hfref-hosp/registry_designs.json
cache/melatonin-primary-insomnia-sol/registry_designs.json
cache/metformin-pcos-ovulation/registry_designs.json
cache/noac-vs-warfarin-af-stroke/registry_designs.json
cache/noac-vs-warfarin-af-stroke/verified_effects.json
cache/omega3-cardiovascular-events/registry_designs.json
cache/pcsk9-mace/registry_designs.json
cache/probiotics-aad-prevention/registry_designs.json
cache/prone-positioning-ards-mortality/arm_contrast.json
cache/sacubitril-valsartan-hfref/registry_designs.json
cache/semaglutide-obesity-mace/registry_designs.json
cache/semaglutide-obesity-weight/registry_designs.json
cache/sglt2-ckd-progression/registry_designs.json
cache/sglt2-hfref-hosp-cvdeath/registry_designs.json
cache/sglt2-primary-prevention-hf/registry_designs.json
cache/spironolactone-hfref-mortality/registry_designs.json
cache/statins-primary-prevention-elderly/registry_designs.json
cache/ticagrelor-vs-clopidogrel-acs/registry_designs.json
cache/tocilizumab-covid19-mortality/registry_designs.json
cache/tranexamic-acid-pph/registry_designs.json
docs/deficit.json
docs/error_rate.json
docs/error_rate_sample.json
docs/evidence_base.json
docs/external_agreement.json
docs/fix_ledger.json
docs/gate_scorecard.json
docs/index.html
docs/membership_consistency_sweep.json
docs/never_considered.json
docs/parity.json
docs/parity_relation_sweep.json
docs/rob_rederivation_sweep.json
docs/rob_spancheck.json
docs/weakness_survey.html
docs/weakness_survey.json
docs/arm_object_sweep.json
docs/comparator_second_pass.json
docs/comparator_truth_sweep.json
docs/compat_direction_sweep.json
docs/consumer_consistency_sweep.json
docs/d5_rule_sweep.json
docs/design_refusal_sweep.json
docs/eligibility_chain_sweep.json
docs/endpoint_canonical_sweep.json
docs/entry_condition_sweep.json
docs/funding_sweep.json
docs/harms_recovery_sweep.json
docs/metformin_pcos_strands.json
docs/near_match_sweep.json
docs/posthoc_amendment_sweep.json
docs/proposition_sweep.json
docs/reason_audit_sweep.json
docs/scope_identity_sweep.json
docs/screening_delta.json
docs/second_source_sweep.json
docs/sglt2_ckd_strands.json
docs/sglt2_primary_prevention_hf_strands.json
docs/source_hierarchy_sweep.json
docs/unextracted_sweep.json
docs/evidence/design-key-2026-09-14/01-sweep-32.txt
docs/evidence/design-key-2026-09-14/01-sweep-32.txt.html
docs/evidence/design-key-2026-09-14/README.md
docs/evidence/design-key-2026-09-14/README.md.html
docs/evidence/design-key-2026-09-14/index.html
docs/evidence/identifier-scope-2026-09-14/README.md
docs/evidence/identifier-scope-2026-09-14/README.md.html
docs/evidence/identifier-scope-2026-09-14/index.html
docs/evidence/override-audit-2026-09-14/index.html
docs/evidence/override-audit-2026-09-14/overrides.json
docs/evidence/override-audit-2026-09-14/overrides.json.html
docs/reviews/*/REPRODUCTION.json
docs/reviews/*/index.html
docs/reviews/*/manifest.json
docs/reviews/*/review.json
docs/m/*/index.html
harness/aact.py
harness/absence.py
harness/arm_object.py
harness/census.py
harness/claimgraph.py
harness/comparator_second_pass.py
harness/comparator_truth.py
harness/compat.py
harness/compat_check.py
harness/compat_direction.py
harness/consumer_consistency.py
harness/ctgov_results.py
harness/design_key.py
harness/design_variance.py
harness/eligibility_chain.py
harness/endpoint_canonical.py
harness/error_library.py
harness/extract.py
harness/funding.py
harness/gate.py
harness/grade.py
harness/harms.py
harness/hazard_consumers.py
harness/invalidation.py
harness/limitations.py
harness/manuscript.py
harness/page.py
harness/parity_relation.py
harness/pipeline.py
harness/propositions.py
harness/protocol_compiler.py
harness/reason_audit.py
harness/rob2.py
harness/rob_sensitivity.py
harness/scope_identity.py
harness/screen.py
harness/screen_entry.py
harness/second_source.py
harness/source_hierarchy.py
harness/target_endpoint.py
harness/unextracted.py
protocols/colchicine-postop-af.md
protocols/colchicine-secondary-cv-prevention.md
protocols/esketamine-trd-madrs.md
protocols/metformin-pcos-ovulation.md
protocols/noac-vs-warfarin-af-stroke.md
protocols/probiotics-aad-prevention.md
protocols/sglt2-ckd-progression.md
protocols/sglt2-primary-prevention-hf.md
registry/blind_map.json
registry/gate_scorecard.json
scripts/arm_object_sweep.py
scripts/comparator_second_pass_sweep.py
scripts/comparator_truth_sweep.py
scripts/compat_direction_sweep.py
scripts/consumer_consistency_sweep.py
scripts/d5_rule_sweep.py
scripts/design_refusal_sweep.py
scripts/eligibility_chain_sweep.py
scripts/endpoint_canonical_sweep.py
scripts/entry_condition_sweep.py
scripts/funding_sweep.py
scripts/harms_recovery_sweep.py
scripts/near_match_sweep.py
scripts/proposition_sweep.py
scripts/reason_audit_sweep.py
scripts/reproduce_review.py
scripts/rob2_build.py
scripts/second_source_sweep.py
scripts/source_hierarchy_sweep.py
scripts/transparency_score.py
scripts/unextracted_sweep.py
scripts/weakness_survey.py
tests/test_arm_object.py
tests/test_comparator_second_pass.py
tests/test_comparator_truth.py
tests/test_compat_direction.py
tests/test_consumer_consistency.py
tests/test_cross_source_endpoint.py
tests/test_d5_rule.py
tests/test_derivation.py
tests/test_design_key.py
tests/test_design_variance.py
tests/test_eligibility_chain.py
tests/test_endpoint_canonical.py
tests/test_estimand_naming.py
tests/test_funding.py
tests/test_gate.py
tests/test_harms_recovery.py
tests/test_membership_consistency.py
tests/test_page.py
tests/test_protocol_compiler.py
tests/test_propositions.py
tests/test_reason_audit.py
tests/test_retrieval_render.py
tests/test_rob_coverage.py
tests/test_scope_identity.py
tests/test_screen_contrast_and_ledger.py
tests/test_screen_entry.py
tests/test_second_source_identity.py
tests/test_source_hierarchy.py
tests/test_source_hierarchy_regression.py
tests/test_stage_additions.py
tests/test_target_endpoint.py
tests/test_unextracted.py
tests/test_uoa_sensitivity.py
topics/balanced-crystalloids-vs-saline-mortality.json
topics/colchicine-postop-af.json
topics/colchicine-secondary-cv-prevention.json
topics/doac-vte-recurrence.json
topics/esketamine-trd-madrs.json
topics/finerenone-ckd-t2d-renal.json
topics/metformin-pcos-ovulation.json
topics/noac-vs-warfarin-af-stroke.json
topics/pcsk9-mace.json
topics/probiotics-aad-prevention.json
topics/semaglutide-obesity-weight.json
topics/sglt2-ckd-progression.json
topics/sglt2-hfref-hosp-cvdeath.json
topics/sglt2-primary-prevention-hf.json
topics/spironolactone-hfref-mortality.json
INTEGRATOR_NOTES.md
LANE-CG2-REPORT.md
LANE-CK2-REPORT.md
LANE-CK3-REPORT.md
LANE-CP2-REPORT.md
LANE-CP3-REPORT.md
LANE-CX-REPORT.md
LANE-D5-REPORT.md
LANE-EN2-REPORT.md
LANE-EX-REPORT.md
LANE-FU-REPORT.md
LANE-RX-REPORT.md
LANE-SC-REPORT.md
LANE-SC2-REPORT.md
LANE-SC3-REPORT.md
LANE-SE-REPORT.md
LANE-SH-REPORT.md
LANE-SH2-REPORT.md
LANE-TE-REPORT.md
LANE-XS2-REPORT.md
LANE_PROMPT.md
RB.patch
SH.patch
before_after.py
lane.log
lane.pid
lane.winpid
patches/CG2.patch
patches/CK2.patch
patches/CK3.patch
patches/CP2.patch
patches/CP3.patch
patches/CX.patch
patches/D5.patch
patches/EN2.patch
patches/EX.patch
patches/FU.patch
patches/HM.partial.patch
patches/RX.patch
patches/SC.patch
patches/SC2.patch
patches/SC3.patch
patches/SE.patch
patches/SH2.patch
patches/TE.patch
patches/XS2.patch
```
