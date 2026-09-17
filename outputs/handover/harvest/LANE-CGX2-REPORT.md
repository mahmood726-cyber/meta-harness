# LANE CGX2 report

**Finish condition NOT met.** This is a partial prose migration, not a release or a claim that the remaining units cannot ever be objects.

MEASURED: `git rev-parse HEAD` = `e3b70bfa36dc65a3920b20fd4e2d628a270e7d28`. No commit, push, deployment or network source acquisition.

## Base and GL patch application

The requested GL.patch was copied into this clone before application. The first `git apply --3way .tmp-GL.patch` was refused because `.git/index.lock` is not writable. A temporary index and object directory under `.tmp/cgx2` allowed the same three-way command to run while leaving the actual Git index untouched. The initial temporary-index attempt needed an index refresh. The resulting application had one content conflict in `harness/pipeline.py`; it was resolved by retaining both TY coercion/protocol loading and GL conventional-delivery selection. The GL patch itself includes pipeline/cache/topic changes; CGX2 did not alter synthesis, membership, search or screening algorithms.

GL was based on an earlier commit than this lane. Its supplied report says the TY binding-axis gate was absent on that base. On this lane the gate exists and rejects GL rows with absent/invalid protocol binding axes; replay reaches `ValueError: no studies to pool`. No binding axes or clinical evidence were invented to bypass that refusal.

## MEASURED implementation and coverage

- General GRADE domain judgements render through ClaimGraph with recorded basis and RULE/OWED adjudication. Assessed domains without basis are unrenderable; missing assessment is never treated as no concern.
- GRADE downgrade totals are recomputed from domain rows, rather than the stored total. Certainty remains start minus downgrades, or provisional when a required assessment is absent; invalid downgrade values are refused.
- Reported-effect strand summaries are TRANSFORMATION objects. They rerun the unchanged synthesis engine on source-verified member rows and compare the result with the registered value. This registers numerical provenance, not permission to bypass TY admission checks.
- Short semantic table headers are STRUCTURAL by markup and grammar rule. No exact-text whitelist is used. Sentence-like headers, numeric data cells and unregistered prose remain debt.
- Scan output now records structural units, DOM context, stable scan-order unit names and registered renderings by class. Identical committed-byte comparisons are reused only inside a synchronous validation batch; changed bytes and subsequent calls are rechecked.

GL supplied baseline: 18 of 1,289 units registered; 1,271 unregistered. Final MEASURED served and fresh coverage: **27 registered of 1129**; **157 STRUCTURAL** units excluded by rule; **1102 unresolved factual/prose units**. Before structural rules the final page has 1286 units. The denominator changed because table furniture is now classified and GRADE rows were combined; this is not 100% coverage.

| Registered rendered class | Units |
|---|---:|
| FACT | 12 |
| TRANSFORMATION | 8 |
| JUDGEMENT | 6 |
| INTERPRETATION | 1 |

Registry object counts (distinct objects, not rendered occurrences): `{"FACT": 23, "INTERPRETATION": 1, "JUDGEMENT": 6, "TRANSFORMATION": 8}`.

MEASURED typed-object violations: 0; certainty contradictions: 0. These checks cover migrated objects only.

## Named unresolved units

Every final unresolved text run is named, quoted verbatim, given its DOM context, and assigned a reason in [LANE-CGX2-UNREGISTERED.md](LANE-CGX2-UNREGISTERED.md) and [the JSON inventory](LANE-CGX2-UNREGISTERED.json). Exact matching review scalar paths are included where available. Candidate FACT / TRANSFORMATION / JUDGEMENT / INTERPRETATION classes are explicitly **INFERRED triage**, not validated registration. Composite prose still needs clause-level source or computation bindings. These are unfinished work, not approved exceptions to the finish condition.

All 1,271 original GL debt units are also individually enumerated in [LANE-CGX2-BASELINE-INVENTORY.json](LANE-CGX2-BASELINE-INVENTORY.json). Their order and exact text were checked against the original GL HTML recovered from the temporary application index. Original structural classifications are based on that DOM, not matches against a whitelist of current strings.

The scan does not silently call short table data cells structural. An identifier, endpoint, decision state or numerical value remains auditable unless registered. Existing review text is not independent source evidence. No arbitrary alternative or adjudication was added merely to raise coverage.

## Static versus dynamic disclosure

| Surface | Static | Dynamic evidence / computation |
|---|---|---|
| Structural classifier | HTML header role and short-label grammar | Parsed DOM/text; all exclusions enumerated |
| GRADE domains | Renderer wording and rule identifiers | Recorded per-domain assessment and basis |
| Certainty and downgrade total | Five required domains and category order | Domain states, start and downgrade arithmetic |
| Strand estimates | Formatting and existing engine choice | Source-verified member estimates; unchanged synth.pool |
| Debt classes | Triage regex rules | Exact rendered units and review-field matches; INFERRED only |
| Legacy prose | Existing templates and stored prose | Still unregistered where named; no certification implied |

## Base plants: failing output verbatim

```text
Base HEAD: e3b70bfa36dc65a3920b20fd4e2d628a270e7d28
Executed before applying GL.patch or editing implementation.

{'rendered_units': 1, 'with_object': 0, 'unit_contract': 'conservative visible prose/table text runs; not an exact linguistic sentence count', 'violations': [{'code': 'SENTENCE_WITHOUT_OBJECT', 'kind': 'unregistered', 'claim_id': '', 'detail': 'The typed estimate is 0.87.'}]}
<span data-claim-id="plant-judgement" data-claim-class="UNRENDERABLE"><strong>[UNRENDERABLE]</strong> JUDGEMENT_WITHOUT_BASIS</span>
<span data-claim-id="plant-interpretation" data-claim-class="UNRENDERABLE"><strong>[UNRENDERABLE]</strong> INTERPRETATION_WITHOUT_ALTERNATIVE</span>
```

## Rebuild and gate

MEASURED offline prose rebuild used `census.build_review_dir(review_core(existing_review), existing_manifest, ...)`, without fetch, membership or screening changes. It rendered the supplied GL review object and rewrote its page/manifest/reproduction artifacts. This is not a successful pipeline replay.

```text
Offline prose rebuild: 2f670544f736fdd3c38eba3af2479822dc8071987fd2fc8e53b87ca675beb070
```

Executed `scripts.verify_all.limb_gate_every_page("glp1-ra-mace-t2d")`; the optional slug parameter filters both the target and gated directories and leaves the default whole-corpus call unchanged.

Verbatim verdict:

```text
REFUSED
```

Full verbatim gate output: [LANE-CGX2-GATE.txt](LANE-CGX2-GATE.txt). Refusals include uncovered prose, no-studies pipeline replay, unresolved harms, and TY binding-axis failures. No release claim is made.

## Tests

First focused run: `2 failed, 16 passed in 72.30s (0:01:12)`; both failures are GL replay tests reaching no studies to pool. Subsequent focused typed-prose/provenance run: `23 passed in 299.10s (0:04:59)`. The final suite below includes the additional provenance-batch regression test.

Final incremental verification, including the sensitivity-preservation guard added during the full-suite run: `python -m pytest -q tests/test_cgx2_prose.py tests/test_glp1_ui.py --tb=short` -> `11 passed in 56.46s`. The full-suite process loaded the preceding implementation; this final guard and its new test were verified in the incremental run. The browser contract exercised all tabs, sourced FACT markers, FLOW caveat and both delivery strands at 127.0.0.1:8000; its screenshot was inspected.

An initial unscoped pytest run encountered a duplicate module basename in archived outputs. The repository-defined full command is `python -m pytest tests/ -q`; the final run adds `--tb=short`. An intermediate run was stopped after renderer batching changed so that final verification uses one code version.

Full-suite summary (MEASURED):

```text
    assert _origin_effect(None) == 0.98
E   assert None == 0.98
E    +  where None = _origin_effect(None)
_______________ test_override_corrects_to_major_vascular_events _______________
tests\test_verified_override.py:39: in test_override_corrects_to_major_vascular_events
    assert _origin_effect(ve) == 1.01
E   AssertionError: assert None == 1.01
E    +  where None = _origin_effect({'22686415': {'ci_high': 1.1, 'ci_low': 0.93, 'effect': 1.01, 'outcome': 'Major vascular events / MACE', ...}})
______________ test_unflagged_verified_effect_does_not_override _______________
tests\test_verified_override.py:44: in test_unflagged_verified_effect_does_not_override
    assert _origin_effect(ve) == 0.98, "an UNFLAGGED verified_effect must not override the abstract"
E   AssertionError: an UNFLAGGED verified_effect must not override the abstract
E   assert None == 0.98
E    +  where None = _origin_effect({'22686415': {'effect': 1.01, 'outcome': 'Major vascular events / MACE', 'scale': 'HR'}})
=========================== short test summary info ===========================
FAILED tests/test_cross_source_endpoint.py::test_rebuilt_fourier_row_is_different_measure_not_corroboration
FAILED tests/test_effect_type.py::test_current_glp1_baseline_plant - Assertio...
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_glp1_lane.py::test_glp1_elixa_located_and_primary_membership
FAILED tests/test_glp1_lane.py::test_glp1_freedom_sensitivity_never_pooled - ...
FAILED tests/test_harms_recovery.py::test_postfix_noac_major_bleeding_recovers_four_trials
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_second_source_identity.py::test_postfix_pcsk9_second_source_rows_are_different_measure_not_corroboration
FAILED tests/test_second_source_identity.py::test_served_fourier_0666_is_value_not_reproducible_from_current_cache
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
FAILED tests/test_verified_effects.py::test_verified_effect_pooled_and_verified
FAILED tests/test_verified_effects.py::test_dose_selection_overrides_abstract_dose_and_verifies
FAILED tests/test_verified_override.py::test_without_override_abstract_selects_the_wrong_endpoint
FAILED tests/test_verified_override.py::test_override_corrects_to_major_vascular_events
FAILED tests/test_verified_override.py::test_unflagged_verified_effect_does_not_override
19 failed, 888 passed in 652.92s (0:10:52)
```

Full log: [LANE-CGX2-FULL.txt](LANE-CGX2-FULL.txt).

## Other pages measured, not migrated

| Page | Served registered / factual units | Fresh registered / factual units |
|---|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 0 / 931 | 15 / 932 |
| colchicine-postop-af | 0 / 1469 | 17 / 1470 |
| colchicine-recurrent-pericarditis | 0 / 1075 | 15 / 1076 |
| colchicine-secondary-cv-prevention | 0 / 2465 | 17 / 2466 |
| corticosteroids-cap-mortality | 0 / 1929 | 16 / 1930 |
| corticosteroids-covid19-mortality | 0 / 1026 | 13 / 1027 |
| dapagliflozin-hfpef-hosp | 0 / 1267 | 13 / 1268 |
| denosumab-vertebral-fracture | 0 / 1021 | 14 / 1021 |
| doac-vte-recurrence | 0 / 2584 | 17 / 2584 |
| dpp4-mace-t2d | 0 / 799 | 15 / 800 |
| empagliflozin-hfpef-hosp | 0 / 1298 | 13 / 1299 |
| esketamine-trd-madrs | 0 / 1685 | 15 / 1685 |
| finerenone-ckd-t2d-renal | 0 / 772 | 14 / 773 |
| glp1-ra-mace-t2d | 27 / 1129 | 27 / 1129 |
| iv-iron-hfref-hosp | 0 / 1028 | 10 / 1023 |
| melatonin-primary-insomnia-sol | 0 / 1658 | 13 / 1659 |
| metformin-pcos-ovulation | 0 / 1995 | 15 / 1996 |
| noac-vs-warfarin-af-stroke | 0 / 882 | 20 / 883 |
| omega3-cardiovascular-events | 0 / 2301 | 20 / 2302 |
| pcsk9-mace | 0 / 678 | 15 / 679 |
| probiotics-aad-prevention | 0 / 7118 | 28 / 7119 |
| sacubitril-valsartan-hfref | 0 / 1138 | 14 / 1139 |
| semaglutide-obesity-mace | 0 / 947 | 13 / 947 |
| semaglutide-obesity-weight | 0 / 1852 | 14 / 1853 |
| sglt2-ckd-progression | 0 / 1113 | 16 / 1114 |
| sglt2-hfref-hosp-cvdeath | 0 / 749 | 14 / 750 |
| sglt2-primary-prevention-hf | 0 / 3080 | 16 / 3081 |
| spironolactone-hfref-mortality | 0 / 2490 | 14 / 2490 |
| statins-primary-prevention-elderly | 0 / 773 | 14 / 774 |
| ticagrelor-vs-clopidogrel-acs | 0 / 686 | 15 / 687 |
| tocilizumab-covid19-mortality | 0 / 1295 | 15 / 1296 |
| tranexamic-acid-pph | 0 / 1169 | 14 / 1170 |

Full measurements: [LANE-CGX2-SCOPE.json](LANE-CGX2-SCOPE.json), [LANE-CGX2-ALL-SCOPE.json](LANE-CGX2-ALL-SCOPE.json).

CLAIMED: no completion, universal coverage, successful pipeline replay, certification or shipping. Remaining work is the exact prose queue plus GL/TY integration through source-backed protocol bindings; statistical admission changes are outside this prose lane.
