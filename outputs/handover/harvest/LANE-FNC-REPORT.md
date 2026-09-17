# Lane FNC report

**Compaction and source preservation verified. The complete requested finish condition is BLOCKED by the base/FN membership conflict below.**

`git rev-parse HEAD`: `443d8a645f61c140116b7bba12eff31acd96865e` (required base `refs/lanes/landing4-wip-typg`). No commit, staging, push, or deployment. No network retrieval was used; browser verification used loopback. `harness/membership.py`, `harness/synth.py`, `harness/gate.py`, topic configurations, and held records remain unchanged. Generated `effect_types.json` rewrites were restored to HEAD after validation.

## MEASURED: storage and source preservation

Across **32 of 32 FN held r3 topics**, all family-cache files shrank from **178,576,227 bytes** to **14,674,568 bytes**. The after total is below **15,000,000 bytes**, includes every gzip sidecar and both GLP-1 query/discovery files, and excludes temporary full-registry regeneration outputs. Per-topic measurements are below and in `docs/trial_family_compaction.json`.

- All **67,785 of 67,785 topic row references** resolve to their recorded SHA-256 in the local AACT snapshot. All **32 of 32 regenerated registries** exactly equal the full FN originals, including all columns and duplicated evidence structures. See `docs/trial_family_preservation.json`.
- `python scripts/build_families.py glp1-ra-mace-t2d`: **15,467 of 15,467 referenced rows verified**, full registry written to `.tmp/glp1-ra-mace-t2d/family_registry.full.json`.
- `family_registry.json` references deterministic gzip JSON catalogues containing `{table, nct_id, row_key, row_sha256, snapshot: "2026-08-30", inline}`. Registry and family evidence use row references, not repeated verbatim AACT rows. All family-table display values remain inline in `families.json`.
- Regeneration uses `harness.aact` offline and refuses altered hashes, unavailable rows/tables, ambiguous keys, altered inline projections, and snapshot mismatches with `NOT PRESERVED`. The snapshot label is an identifier, not an independently verified historical cutoff date.

## MEASURED: finish-condition conflict

The corrected `python scripts/trial_family_sweep.py` covered **32 of 32 held r3 topics**, with 0 execution/pool-invariance failures. It checks current-HEAD baseline membership and numeric primary/secondary/harms results against compact replay. This is **not** a claim of exact FN count-chain parity.

Requested FN GLP-1 chain: **13 publications + 234 registry records → 238 families → 143 eligible → 8 contributing**.
Base-preserving measured GLP-1 chain: **13 publications + 234 registry records → 238 families → 143 eligible → 3 contributing**.

The newer base refuses effect rows for `AXIS_DOCUMENT_DIGEST_MISMATCH`, `NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD`, and an endpoint-component mismatch without valid coercion. The primary retained PMIDs are `27295427`, `28910237`, and `26630143`; these are measured pipeline outputs, not replacements selected by this lane. Exact refusal records are retained in `docs/trial_family_base_conflict.json`. Reaching FN’s 8 by changing membership or overriding the base evidence gate would violate the explicit lane constraints. No such changes were made. This unresolved condition is also logged in `STUCK_FAILURES.md`.

Count-chain differences against the imported FN reference occur in **1 of 32 topic chains**: glp1-ra-mace-t2d.

The first sweep found a scoped-AACT inventory omission because the newer base adds FLOW/FREEDOM-CVO from held local documents. The inventory was corrected to include those actual records and compact registry IDs; the fresh full sweep is the final result. A related integration repair keeps GLP-1 publication joins and PMID-labelled fields keyed by source PMIDs after adding family IDs. It changes no pooled members.

## Validation

- FN tests plus FNC tests: **41 of 41 distinct targeted tests passed** across the final non-browser run and isolated browser rerun. The combined run had 40 passes and one browser timeout while the full suite’s other local server also used port 8000. The isolated family browser contract subsequently passed, with an exact response-body check and external requests blocked.
- FNC-specific tests: **11 of 11 passed**, including altered source/hash/inline values, missing rows/tables, wrong snapshot, ambiguous keys, exact reconstruction, deterministic sidecars, batch refusal, rendered-table equivalence across all topics, and typed publication joins.
- Final source audit: 9,026 of 9,026 field/source assertions passed across 32 of 32 topic artifacts.
- Full canonical `tests/` suite: **944 passed, 12 failed (956 collected tests; 1,634.98 seconds)**. The root-wide collection attempt additionally failed on duplicate `test_search_v2_isrctn` module names in `outputs/` and `tests/`; that is why the full run uses the canonical `tests/` directory.
- Full-suite failure follow-up: All 12 failing test IDs reproduced against HEAD modules with the same local inputs (12 failed in 193.53 seconds), and all 12 reproduced on final current modules (12 failed in 236.57 seconds). The GLP-1 PMID-field port regression was corrected; its remaining failure is the same base 3-versus-expected-membership conflict. These diagnostic runs are not a separate full clean-checkout baseline suite.
- Compile and whitespace checks: PASS: compileall on changed/new modules, scripts and tests; git diff --check; protected files unchanged.

Full-suite failing tests:

- `tests/test_effect_type.py::test_current_glp1_baseline_plant`
- `tests/test_fixstate.py::test_real_store_validates`
- `tests/test_gate.py::test_valid_page_passes_non_replay_limbs`
- `tests/test_gate_scorecard.py::test_real_registry_passes`
- `tests/test_glp1_lane.py::test_glp1_elixa_located_and_primary_membership`
- `tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews`
- `tests/test_override_audit.py::test_override_audit_covers_every_committed_override`
- `tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review`
- `tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population`
- `tests/test_ty2_protocol_binding.py::test_glp1_rebuild_membership`
- `tests/test_typg_axis_evidence.py::test_all_registered_spans_locate_and_only_binding_axes_are_curated`
- `tests/test_typg_axis_evidence.py::test_flow_does_not_borrow_component_censoring`

## Plants FIRST: captured failing output

Before importing FN, command `python -c "import harness.trial_family"`:

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import harness.trial_family
ModuleNotFoundError: No module named 'harness.trial_family'
```

After importing FN, the new hash-refusal test initially failed before its implementation:

```text
tests/test_family_compact.py:7: in test_mutated_row_hash_refuses_regeneration
    from harness.family_compact import compact_registry, regenerate
E   ModuleNotFoundError: No module named 'harness.family_compact'
1 failed in 1.17s
```

After implementation, the explicit fixture plant mutates `row_sha256` to 64 zeroes and calls regeneration without catching the exception. Captured terminal refusal (exit 1):

```text
    raise ValueError('NOT PRESERVED: row hash mismatch ' + table + ' ' + ref['nct_id'])
ValueError: NOT PRESERVED: row hash mismatch studies NCT00000001
```

Fixtures are labelled synthetic and never enter research caches.

## Hardcode disclosure

| Component | Static policy | Dynamic evidence / validation |
|---|---|---|
| References | Snapshot identifier; canonical JSON/SHA-256; snapshot-scoped row-key rule | Every key/hash/value taken from FN rows and checked against local AACT |
| Inline projection | Explicit columns required by existing consumers; page-field schema | Values derived from held registries and the unchanged membership pipeline |
| Compression | Object interning; gzip `mtime=0` | Lossless full registry reconstruction equals FN for every topic |
| Test plants | Explicit synthetic records and corruption cases | No simulated research findings or substituted effect values |
| Counts and sizes | Named cohort and 15,000,000-byte target from lane prompt | Counts from executed sweep; byte sizes from disk |

**INFERRED:** the requested 8-contributor finish cannot coexist with the required current-base membership freeze. The measured before/after pooling comparison and refusal records support this conclusion. **CLAIMED scope:** compact offline preservation and current-base replay only; exact FN contributor parity and a green full suite are not claimed.

## Per-topic byte measurements

| Topic | FN before bytes | Compact after bytes |
|---|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 1683458 | 127312 |
| colchicine-postop-af | 1365257 | 162328 |
| colchicine-recurrent-pericarditis | 2247987 | 202267 |
| colchicine-secondary-cv-prevention | 4363405 | 402513 |
| corticosteroids-cap-mortality | 2700523 | 309822 |
| corticosteroids-covid19-mortality | 3865927 | 281554 |
| dapagliflozin-hfpef-hosp | 2633609 | 246390 |
| denosumab-vertebral-fracture | 2502967 | 225146 |
| doac-vte-recurrence | 11471906 | 879490 |
| dpp4-mace-t2d | 3245955 | 207697 |
| empagliflozin-hfpef-hosp | 2851535 | 266361 |
| esketamine-trd-madrs | 6210476 | 414609 |
| finerenone-ckd-t2d-renal | 2147478 | 139525 |
| glp1-ra-mace-t2d | 40574030 | 3585988 |
| iv-iron-hfref-hosp | 1446297 | 134306 |
| melatonin-primary-insomnia-sol | 2486597 | 277676 |
| metformin-pcos-ovulation | 3668591 | 337697 |
| noac-vs-warfarin-af-stroke | 3195578 | 195569 |
| omega3-cardiovascular-events | 5237666 | 422534 |
| pcsk9-mace | 1867570 | 109050 |
| probiotics-aad-prevention | 8684875 | 1139926 |
| sacubitril-valsartan-hfref | 6887406 | 402434 |
| semaglutide-obesity-mace | 1385889 | 133432 |
| semaglutide-obesity-weight | 10357784 | 601776 |
| sglt2-ckd-progression | 3316444 | 232648 |
| sglt2-hfref-hosp-cvdeath | 1871096 | 136178 |
| sglt2-primary-prevention-hf | 25743775 | 1761330 |
| spironolactone-hfref-mortality | 4198472 | 534979 |
| statins-primary-prevention-elderly | 2106771 | 147064 |
| ticagrelor-vs-clopidogrel-acs | 1540827 | 124166 |
| tocilizumab-covid19-mortality | 3444796 | 252117 |
| tranexamic-acid-pph | 3271280 | 280684 |

## FN import inventory

Existing-module FN deltas were applied while preserving newer base changes:

- `harness/claimgraph.py`
- `harness/grade.py`
- `harness/identity.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/rob_sensitivity.py`

FN additions copied into this base (subsequently compacted or adapted as described):

- `cache/balanced-crystalloids-vs-saline-mortality/families.json`
- `cache/balanced-crystalloids-vs-saline-mortality/family_registry.json`
- `cache/colchicine-postop-af/families.json`
- `cache/colchicine-postop-af/family_registry.json`
- `cache/colchicine-recurrent-pericarditis/families.json`
- `cache/colchicine-recurrent-pericarditis/family_registry.json`
- `cache/colchicine-secondary-cv-prevention/families.json`
- `cache/colchicine-secondary-cv-prevention/family_registry.json`
- `cache/corticosteroids-cap-mortality/families.json`
- `cache/corticosteroids-cap-mortality/family_registry.json`
- `cache/corticosteroids-covid19-mortality/families.json`
- `cache/corticosteroids-covid19-mortality/family_registry.json`
- `cache/dapagliflozin-hfpef-hosp/families.json`
- `cache/dapagliflozin-hfpef-hosp/family_registry.json`
- `cache/denosumab-vertebral-fracture/families.json`
- `cache/denosumab-vertebral-fracture/family_registry.json`
- `cache/doac-vte-recurrence/families.json`
- `cache/doac-vte-recurrence/family_registry.json`
- `cache/dpp4-mace-t2d/families.json`
- `cache/dpp4-mace-t2d/family_registry.json`
- `cache/empagliflozin-hfpef-hosp/families.json`
- `cache/empagliflozin-hfpef-hosp/family_registry.json`
- `cache/esketamine-trd-madrs/families.json`
- `cache/esketamine-trd-madrs/family_registry.json`
- `cache/finerenone-ckd-t2d-renal/families.json`
- `cache/finerenone-ckd-t2d-renal/family_registry.json`
- `cache/glp1-ra-mace-t2d/families.json`
- `cache/glp1-ra-mace-t2d/family_discovery.json`
- `cache/glp1-ra-mace-t2d/family_query.json`
- `cache/glp1-ra-mace-t2d/family_registry.json`
- `cache/iv-iron-hfref-hosp/families.json`
- `cache/iv-iron-hfref-hosp/family_registry.json`
- `cache/melatonin-primary-insomnia-sol/families.json`
- `cache/melatonin-primary-insomnia-sol/family_registry.json`
- `cache/metformin-pcos-ovulation/families.json`
- `cache/metformin-pcos-ovulation/family_registry.json`
- `cache/noac-vs-warfarin-af-stroke/families.json`
- `cache/noac-vs-warfarin-af-stroke/family_registry.json`
- `cache/omega3-cardiovascular-events/families.json`
- `cache/omega3-cardiovascular-events/family_registry.json`
- `cache/pcsk9-mace/families.json`
- `cache/pcsk9-mace/family_registry.json`
- `cache/probiotics-aad-prevention/families.json`
- `cache/probiotics-aad-prevention/family_registry.json`
- `cache/sacubitril-valsartan-hfref/families.json`
- `cache/sacubitril-valsartan-hfref/family_registry.json`
- `cache/semaglutide-obesity-mace/families.json`
- `cache/semaglutide-obesity-mace/family_registry.json`
- `cache/semaglutide-obesity-weight/families.json`
- `cache/semaglutide-obesity-weight/family_registry.json`
- `cache/sglt2-ckd-progression/families.json`
- `cache/sglt2-ckd-progression/family_registry.json`
- `cache/sglt2-hfref-hosp-cvdeath/families.json`
- `cache/sglt2-hfref-hosp-cvdeath/family_registry.json`
- `cache/sglt2-primary-prevention-hf/families.json`
- `cache/sglt2-primary-prevention-hf/family_registry.json`
- `cache/spironolactone-hfref-mortality/families.json`
- `cache/spironolactone-hfref-mortality/family_registry.json`
- `cache/statins-primary-prevention-elderly/families.json`
- `cache/statins-primary-prevention-elderly/family_registry.json`
- `cache/ticagrelor-vs-clopidogrel-acs/families.json`
- `cache/ticagrelor-vs-clopidogrel-acs/family_registry.json`
- `cache/tocilizumab-covid19-mortality/families.json`
- `cache/tocilizumab-covid19-mortality/family_registry.json`
- `cache/tranexamic-acid-pph/families.json`
- `cache/tranexamic-acid-pph/family_registry.json`
- `docs/trial_family_evidence_audit.json`
- `docs/trial_family_held_plants.json`
- `docs/trial_family_sweep.json`
- `harness/trial_family.py`
- `scripts/trial_family_audit.py`
- `scripts/trial_family_registry.py`
- `scripts/trial_family_sweep.py`
- `tests/test_trial_family.py`
- `tests/test_trial_family_ui.py`

Additional FNC implementation: `harness/family_compact.py`, `scripts/build_families.py`, `scripts/compact_families.py`, `scripts/verify_family_preservation.py`, `tests/test_family_compact.py`, and `docs/trial_family_storage.md`. `harness/glp1.py` has the source-PMID join correction described above. Measurement, preservation, FN-reference, and conflict JSON files accompany this report.
