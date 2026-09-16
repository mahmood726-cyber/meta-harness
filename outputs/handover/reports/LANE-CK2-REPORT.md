# LANE CK2 Report

## 1. What was wrong, mechanism, files

The defect was an eligibility chain split across disconnected surfaces. On `colchicine-postop-af`, the prose protocol stated a design/masking rule, the executable topic config did not enforce it, the rendered compatibility key asserted a broader matched pool, and pooled trial rows carried values that contradicted the asserted key. The concrete pre-lane page also claimed protocol/config agreement on design masking while END-AF was pooled as open-label.

Implemented mechanism:

| Surface | Change |
|---|---|
| Protocol/config contract | Added `harness/eligibility_chain.py` and `harness.protocol_compiler.typed_criteria()` to compile typed protocol criteria, compare them to executable config rules, and emit `PROTOCOL_CONFIG_DIVERGENCE`, `CONFIG_WITHOUT_PROTOCOL`, `TRIAL_FAILS_CONTRACT`, `ELIGIBILITY_STATE_INCONSISTENT`, and `PROSE_PREDICATE_FALSE`. |
| Per-trial admission | `harness/pipeline.py` now applies CK2 admission records to `colchicine-postop-af`; pooled rows carry per-dimension `trial_value`, `span`, `contract_value`, and `verdict`. |
| Rendered key | `harness/page.py` renders admission-derived heterogeneous `follow_up_window`, `analysis_set`, and `endpoint_definition` values; the old agreement sentence now names only actually agreed dimensions. |
| Gate | `harness/gate.py` refuses hard eligibility-chain violations. `harness/limitations.py` and `harness/hazard_consumers.py` wire the visible eligibility-chain refusal block to that gate. |
| Zarpelon vocabulary | `topics/colchicine-postop-af.json` adds non-query `population_any_extra` and `comparator_any_extra`; `harness/screen.py` reads comparator extras. This preserves the sealed search vocabulary while making “myocardial revascularization” screen as cardiac surgery. |
| Sweep | Added `scripts/eligibility_chain_sweep.py`, writing `docs/eligibility_chain_sweep.json`. |

Measured sweep output:

- MEASURED: `17 of 32` pages had at least one `PROTOCOL_CONFIG_DIVERGENCE`; denominator is all `32` review topics in `docs/reviews`.
- MEASURED: divergence dimensions were `design_masking=16`, `design_population_context=1`, `population_context=1`.
- MEASURED: `100 of 115` pooled rows failed their current page contract; denominator is pooled rows across the `32` topics. This is a defect/instrument-breadth report, not a claim that CK2 resolved the corpus.
- MEASURED: `0 of 2837` excluded rows were `ELIGIBILITY_STATE_INCONSISTENT` after the CK2 annotation pass; denominator is excluded rows across the `32` topics.
- MEASURED: `colchicine-postop-af` had `5 of 5` pooled rows failing at least one contract dimension in the sweep; this is reported as a remaining page-level defect pending integrator decision.

Static-vs-dynamic hardcode disclosure:

| Item | Static or dynamic | Disclosure |
|---|---:|---|
| Protocol criterion parser | Static recognizers over protocol prose | Hand-coded phrase recognition for dimensions such as design masking, comparator, follow-up, analysis set, and population context. It fails closed by emitting divergence/config-without-protocol rather than silently certifying agreement. |
| CK2 trial value extraction | Static/source-backed recognizers | Named trial values such as END-AF open-label, COPPS-2 three-month follow-up, and the 2026 CABG available-case row are source-backed from committed review/cache text, not simulated outputs. |
| Sweep counts | Dynamic | Recomputed from current committed review objects, protocols, and topic configs by `scripts/eligibility_chain_sweep.py`; no network. |
| Topic extras | Static topic config | `population_any_extra=["myocardial revascularization"]` and `comparator_any_extra=["control"]` are explicit screening terms and are intentionally outside sealed search-vocabulary fields. |

## 2. Plants

All plants are in `tests/test_eligibility_chain.py`.

| Test | Exact assertion shape | Pre-fix object output | Post-fix/current output |
|---|---|---|---|
| `test_prefix_protocol_states_masking_but_config_has_no_masking_rule_and_page_claims_agreement` | `any(... design_masking ...)`; `"agree on the checked dimensions" in html`; `"PROTOCOL_CONFIG_DIVERGENCE" in _codes(annotated)` | MEASURED: pre-fix protocol states `double_blind_or_placebo_controlled`; pre-fix config has no design-masking rule; pre-fix HTML contains the false agreement sentence. | MEASURED: current review records `PROTOCOL_CONFIG_DIVERGENCE(design_masking)` and agreed dimensions are only `analysis_set`, `comparator`, `follow_up_window`. |
| `test_prefix_end_af_pooled_open_label_fails_protocol_contract` | END-AF admission has `trial_value == open_label` and `verdict == FAIL` | MEASURED: pre-fix END-AF is pooled and its cached text contains “open-label”. | MEASURED: current page remains unrenderable/REFUSED until an integrator excludes END-AF or amends the protocol; the violation is rendered and gate-refused. |
| `test_prefix_zarpelon_has_two_rationales_but_current_vocab_reaches_single_design_rationale` | pre-fix rationales include population and parity ambiguity; current `single_rationale == design_masking` | MEASURED: pre-fix Zarpelon had `population not on-topic` plus `multi-arm/dose-timing ambiguity`. | MEASURED: current Zarpelon is declared absent as `REFUSED_ON_EVIDENCE`, `reason_code=REFUSED_ON_EVIDENCE`, `eligibility_chain_rationale=design_masking`, `eligibility_refusal_code=TRIAL_FAILS_CONTRACT`. |
| `test_prefix_copps2_followup_key_violates_protocol_window` | `trial_value == "3 months"`, `verdict == "FAIL"`, compatibility key `matched is False` | MEASURED: pre-fix key asserted a matched broad follow-up sentence. | MEASURED: current key is heterogeneous with `14 days / postoperative admission`, `3 months`, and `in-hospital / until discharge`. |
| `test_prefix_2026_trial_is_available_case_not_itt` | `trial_value == "AVAILABLE_CASE"` and `verdict == "FAIL"` | MEASURED: pre-fix key promoted the row to ITT. | MEASURED: current admission records `AVAILABLE_CASE` for PMID `42132185` and the analysis-set key is `matched: false`. |
| `test_prefix_shipped_prose_predicates_are_false` | `{"reach_vs_screening", "extraction_debt"} <= dims` | MEASURED: pre-fix prose predicates are false against committed objects. | MEASURED: corpus sweep records both false predicates for the topic; current page object carries `reach_vs_screening`, while sweep also catches `extraction_debt`. |
| `test_synthetic_clean_contract_has_no_violations` | `EC.check_review(annotated) == []` | MEASURED: clean synthetic contract has no violations. | MEASURED: still passes. |
| `test_synthetic_config_rule_without_protocol_sentence_is_divergence` | `CONFIG_WITHOUT_PROTOCOL(design_masking)` exists | MEASURED: synthetic config-only rule fires. | MEASURED: still passes. |
| `test_additional_protocol_config_divergence_plants` | per-topic `PROTOCOL_CONFIG_DIVERGENCE` exists for the named dimension | MEASURED: extra planted divergences fire for `sglt2-primary-prevention-hf`, `colchicine-secondary-cv-prevention`, `metformin-pcos-ovulation`, and `colchicine-postop-af`. | MEASURED: still passes. |

Targeted output:

- MEASURED: `python -m pytest tests/test_eligibility_chain.py -q` -> `9 passed in 17.44s`.
- MEASURED: `python -m pytest tests/test_hazard_consumers.py::test_every_wired_mapping_has_a_plant_that_changes_gate_verdict -q` -> `1 passed in 9.34s`.

## 3. Rebuilt pages

Pages whose rebuilt bytes changed:

| Page | Before | After |
|---|---|---|
| `docs/reviews/colchicine-postop-af/index.html` | MEASURED: primary pool `k=4`, RR `0.6735` with CI `[0.376, 1.2067]`; declared absent list had `4` entries; compatibility key `matched: true`, follow-up scalar `postoperative, in-hospital to 30 days...`, analysis set `intention-to-treat`; protocol/config divergences were empty. | MEASURED: primary pool still `k=4`, RR `0.6735` with CI `[0.376, 1.2067]`; declared absent list has `5` entries including PMID `27223641`; compatibility key `matched: false`; follow-up, analysis set, and endpoint definition enumerate per-trial values; `PROTOCOL_CONFIG_DIVERGENCE(design_masking)` is rendered; gate refuses the page pending integrator decision. |
| `docs/m/mb6ceb13c/index.html` | MEASURED: blind mirror had the same pre-lane canonical content. | MEASURED: blind mirror now carries the same eligibility-chain block, compatibility-key heterogeneity, and Zarpelon declared-absent refusal as the canonical page. |
| `docs/index.html` | MEASURED: generated site index bytes did not include the new gate-scorecard entry or refreshed generated artefact digests. | MEASURED: regenerated index reflects the refreshed generated artefacts; the served `docs/gate_scorecard.json` includes `gate.check_eligibility_chain`. |

Other measured artefact changes:

- MEASURED: `python scripts/reproduce_review.py colchicine-postop-af` -> `1/1 reproduce (all reproducible)`.
- MEASURED: `python -m harness.gate docs/reviews/colchicine-postop-af` exits with `GATE REFUSE` and the remaining reason is `L1: executable eligibility-chain violation(s) remain`.

## 4. Tests

Final required test command:

- MEASURED: `python -m pytest tests -x -q` -> `725 passed in 960.77s (0:16:00)`.

Other checks run:

- MEASURED: `python -m pytest tests/test_eligibility_chain.py tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews -q` -> `10 passed in 37.89s`.
- MEASURED: `python -m pytest tests/test_search_v2_guard.py::test_p4_both_answers_guard_alone_refuses_sealed_exemption_allows[colchicine-postop-af] tests/test_search_v2_guard.py::test_seal_registry_matches_working_tree_for_every_sealed_slug -q` -> `2 passed in 15.50s`.
- MEASURED: `python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate tests/test_fixstate.py::test_real_store_validates tests/test_gate_scorecard.py::test_real_registry_passes -q` -> `3 passed in 440.36s (0:07:20)`.
- MEASURED: `git diff --check` passed with no output.

## 5. What I did not do

- Did not commit, stage, stash, checkout, reset, clean, or touch `.git`.
- Did not run `scripts/verify_all.py`; the lane prompt excludes it.
- Did not run network searches or refresh source retrieval.
- Did not change pooling arithmetic, `harness/synth.py`, `harness/estmeasure.py`, extractor logic, or search engine logic.
- Did not add or remove pooled trials. END-AF remains pooled but now makes the page unrenderable/refused until the integrator decides whether to amend the protocol or exclude it.
- Did not adopt the exploratory larger colchicine pool or collapse harm constructs.
- Did not update `INDEX.md` or the rewrite workbook because this lane did not change project submission status.

## 6. Files changed or added

Added:

- `LANE-CK2-REPORT.md`
- `docs/eligibility_chain_sweep.json`
- `harness/eligibility_chain.py`
- `scripts/eligibility_chain_sweep.py`
- `tests/test_eligibility_chain.py`

Modified:

- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/fix_ledger.json`
- `docs/gate_scorecard.json`
- `docs/index.html`
- `docs/m/mb6ceb13c/index.html`
- `docs/reviews/colchicine-postop-af/REPRODUCTION.json`
- `docs/reviews/colchicine-postop-af/index.html`
- `docs/reviews/colchicine-postop-af/manifest.json`
- `docs/reviews/colchicine-postop-af/review.json`
- `harness/gate.py`
- `harness/hazard_consumers.py`
- `harness/limitations.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/protocol_compiler.py`
- `harness/screen.py`
- `registry/blind_map.json`
- `registry/gate_scorecard.json`
- `topics/colchicine-postop-af.json`

Untracked lane-runner inputs/logs visible in `git status` but not edited by this lane: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
