# LANE TY2 report

**Finish condition: NOT MET. No commit, push, deployment, or network acquisition performed.**

MEASURED `git rev-parse HEAD`: `c57e8727afe8a7cce757b879fea76cec337c4298`. This matches the requested base `refs/lanes/landing4-wip`.
The initial tree contained only untracked LANE_PROMPT.md and lane process/log files. Existing lane files were preserved.

## Implemented

- The protocol compiler parses one validated `effect-type-binding` JSON block, scoped by exact outcome name. Unknown axes, malformed/duplicate blocks and invalid target enums fail closed.
- Real protocol text controls binding; outcome defaults no longer imply binding. Absent declarations produce an empty binding set and the rendered disclosure says all axes are non-binding. Missing row evidence stays UNKNOWN with its absence code.
- Only the GLP1 protocol was amended, retrospectively dated 2026-09-17. Its endpoint components, HR scale and end-of-study censoring are binding. Other axes are disclosed and non-binding.
- The primary membership filter now reads the existing strand membership object. No topic slug or trial ID appears in that filter. Existing GLP1-specific augmentation/rendering adapters elsewhere were not generalized.
- Empty GLP1 strands no longer call the synthesizer with zero studies. Additional any-delivery evidence passes through the same binding gate instead of bypassing it; refusals render with typed evidence.

## Static versus dynamic disclosure

| Component | Static policy/input | Dynamic measurement |
|---|---|---|
| Binding policy | Axis names, schema version, explicit GLP1 target values in its protocol | Parsed by protocol compiler for each outcome |
| Membership | Existing docs/*_strands.json member identities | Generic selection intersects candidate rows with declared strand members |
| Effect evidence | Existing held records/regulatory documents | Existing extractor, provenance checks, unification and canonical synthesis |
| Research outputs | No new hardcoded HR, CI, k, identifiers or dates | Sweep, replay and source-digit audit read held bytes |
| Synthetic plant | Explicit synthetic IDs and numeric fixtures, tests only | Generic loader, selection and canonical pool produce k=2/k=3 |

## Baseline plants FIRST

MEASURED on the unchanged implementation at the base, after adding only the plant test file:
`python -m pytest tests/test_ty2_protocol_binding.py -q --tb=short`
The GLP1 rebuild reached `no studies to pool` in its primary strand. The undeclared protocol refused both synthetic rows. The generic strand selector did not exist.

Verbatim failing output:
```text

================================== FAILURES ===================================
___________________ test_no_declaration_pools_unknown_axes ____________________
tests\test_ty2_protocol_binding.py:13: in test_no_declaration_pools_unknown_axes
    assert len(kept) == 2, f'accepted={len(kept)} refused={len(refused)} target={target}'
E   AssertionError: accepted=0 refused=2 target={'binding_axes': ['analysis_set', 'effect_measure'], 'axes': {'analysis_set': {'value': 'ITT', 'basis': {'rule_id': 'protocol:outcome.population'}}, 'effect_measure': {'value': 'HR', 'basis': {'rule_id': 'protocol:outcome.estimand'}}}, 'disclosure': 'Only explicit machine-readable declarations compiled; no additional binding policy inferred.'}
E   assert 0 == 2
E    +  where 0 = len([])
________________________ test_glp1_rebuild_membership _________________________
tests\test_ty2_protocol_binding.py:21: in test_glp1_rebuild_membership
    review = replay_core('glp1-ra-mace-t2d')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\reproduce_review.py:47: in replay_core
    return build_review_core(slug, config, records, protocol_sha or _protocol_sha(slug))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
harness\pipeline.py:1979: in build_review_core
    review['strands'] = glp1.strands(primary, veffs)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
harness\glp1.py:160: in strands
    r = pool([Study(label=m['trial'], effect=m['effect'], ci_low=m['ci_low'],
harness\synth.py:265: in pool
    raise ValueError("no studies to pool")
E   ValueError: no studies to pool
___________________ test_synthetic_second_topic_two_strands ___________________
tests\test_ty2_protocol_binding.py:35: in test_synthetic_second_topic_two_strands
    selected = pipeline.strand_members(rows, doc, strand)
               ^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'harness.pipeline' has no attribute 'strand_members'
=========================== short test summary info ===========================
FAILED tests/test_ty2_protocol_binding.py::test_no_declaration_pools_unknown_axes
FAILED tests/test_ty2_protocol_binding.py::test_glp1_rebuild_membership - Val...
FAILED tests/test_ty2_protocol_binding.py::test_synthetic_second_topic_two_strands
3 failed in 24.63s
```

## Before/after sweep, same held page inputs

Command in both states: `python scripts/effect_type_sweep.py`. Each sweep ran across 32 topics. The denominator is candidate rows in currently served, non-suppressed pooled outcomes, not all screened studies. The failed build did not replace served pages; the denominators are identical.

MEASURED before: 96 of 114 refused; after: 10 of 114 refused.

| Topic | Before refused n of N | After refused n of N |
|---|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 2 of 2 | 0 of 2 |
| colchicine-postop-af | 5 of 5 | 0 of 5 |
| colchicine-recurrent-pericarditis | 0 of 3 | 0 of 3 |
| colchicine-secondary-cv-prevention | 4 of 5 | 0 of 5 |
| corticosteroids-cap-mortality | 2 of 2 | 0 of 2 |
| corticosteroids-covid19-mortality | 1 of 1 | 0 of 1 |
| dapagliflozin-hfpef-hosp | 1 of 1 | 0 of 1 |
| denosumab-vertebral-fracture | 3 of 3 | 0 of 3 |
| doac-vte-recurrence | 6 of 6 | 0 of 6 |
| dpp4-mace-t2d | 3 of 3 | 0 of 3 |
| empagliflozin-hfpef-hosp | 1 of 1 | 0 of 1 |
| esketamine-trd-madrs | 0 of 4 | 0 of 4 |
| finerenone-ckd-t2d-renal | 2 of 2 | 0 of 2 |
| glp1-ra-mace-t2d | 10 of 10 | 10 of 10 |
| iv-iron-hfref-hosp | 0 of 0 | 0 of 0 |
| melatonin-primary-insomnia-sol | 0 of 1 | 0 of 1 |
| metformin-pcos-ovulation | 3 of 3 | 0 of 3 |
| noac-vs-warfarin-af-stroke | 4 of 8 | 0 of 8 |
| omega3-cardiovascular-events | 7 of 7 | 0 of 7 |
| pcsk9-mace | 3 of 3 | 0 of 3 |
| probiotics-aad-prevention | 14 of 16 | 0 of 16 |
| sacubitril-valsartan-hfref | 2 of 2 | 0 of 2 |
| semaglutide-obesity-mace | 2 of 2 | 0 of 2 |
| semaglutide-obesity-weight | 0 of 2 | 0 of 2 |
| sglt2-ckd-progression | 4 of 4 | 0 of 4 |
| sglt2-hfref-hosp-cvdeath | 2 of 2 | 0 of 2 |
| sglt2-primary-prevention-hf | 4 of 4 | 0 of 4 |
| spironolactone-hfref-mortality | 3 of 3 | 0 of 3 |
| statins-primary-prevention-elderly | 2 of 2 | 0 of 2 |
| ticagrelor-vs-clopidogrel-acs | 2 of 2 | 0 of 2 |
| tocilizumab-covid19-mortality | 3 of 3 | 0 of 3 |
| tranexamic-acid-pph | 1 of 2 | 0 of 2 |

The remaining sweep refusals are exclusively GLP1 rows failing its declared binding endpoint/censoring axes. Other protocols were not edited. Machine detail: `.tmp/ty2/sweep-before.json`, `.tmp/ty2/sweep-after.json` and `docs/effect_type_sweep.json`.

## GLP1 rebuild and source review

MEASURED core after implementation: CONVENTIONAL_GLP1RA k=0, GLP1RA_ANY_DELIVERY k=0. The required k=10/k=11 return is **not achieved**. No replacement evidence or optimistic acceptance was manufactured.

MEASURED independently by canonical synthesis from the held lane GL member objects (WITHOUT binding-axis acceptance):
- CONVENTIONAL_GLP1RA: k=10, HR 0.8613 (0.8069–0.9194); every member passed held-document digest/span verification.
- GLP1RA_ANY_DELIVERY: k=11, HR 0.8673 (0.7999–0.9404); every member passed held-document digest/span verification.

These reproduce the values CLAIMED in the lane prompt, but are not new accepted pools. A source-verified HR does not establish a source-verified censoring rule. The existing GLP1 source adapter explicitly labels FLOW censoring UNKNOWN. The generic component parser also sees ambiguous/mixed endpoint spans. Changing missing binding evidence into acceptance would contradict the stated fail-closed policy.

The held adjudication at `outputs/handover/glp1_reviewerB/ADJUDICATIONS.json:67` explicitly states that the censoring axis for FLOW HR 0.82 must be typed from the publication before FLOW pools, and must not be assumed. Its registry composite describes an on-treatment period while component rows describe an in-trial period. This is a documented evidence obligation, not merely the absence of a matching parser keyword. Additional held full texts exist for other trials; no exhaustive new source adjudication is claimed here.

Second-pass identifier/date check: FLOW PMID 38785209 / NCT03819153 / publication year 2024 and FREEDOM-CVO PMID 34873344 / NCT01455896 / publication year 2022 were read from the held PubMed XML records. No source identifiers or dates were edited. Source-digit audit: `.tmp/ty2/source-audit.json`.

INFERRED blocker resolution: supply evidence bearing on the declared axes, or explicitly revise the requested missing-binding-evidence policy. Restoring k=10/k=11 merely by copying protocol targets into rows would be invalid.

Build command: `python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-17`.
Verbatim build failure:
```text
Traceback (most recent call last):
  File "C:\mh-r-TY2\scripts\build_topic.py", line 106, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-TY2\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)
  File "C:\mh-r-TY2\harness\census.py", line 197, in build_review_dir
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
                                     ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TY2\harness\census.py", line 115, in _parity_row
    return parity_relation.enrich(row, review_core_obj)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TY2\harness\parity_relation.py", line 239, in enrich
    raise ValueError(
    ...<3 lines>...
    )
ValueError: PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation OVERLAPPING for glp1-ra-mace-t2d
```

## Required gate

`scripts.verify_all.limb_gate_every_page("glp1-ra-mace-t2d")` returned this verdict (verbatim):
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=c57e8727afe8a7cce757b879fea76cec337c4298 base=none tree=dirty:13 files files=1 docs/reviews/glp1-ra-mace-t2d/review.json
```

The build was refused before publishing a replacement, so this gate checked the existing served artefacts against changed code; it is not a gate pass on a rebuilt page. Full verbatim gate details are in `.tmp/ty2/gate.txt`. They include replay mismatch, unregistered prose, unresolved harms and missing typed effect objects on the old served page. The gate implementation was not edited.

## Tests

### Targeted/UI suite

```text
short test summary info ===========================
FAILED tests/test_ty2_protocol_binding.py::test_glp1_rebuild_membership - Ass...
FAILED tests/test_effect_type.py::test_current_glp1_baseline_plant - Assertio...
2 failed, 30 passed in 58.04s
```

Full output: `.tmp/ty2/final-targeted.txt`.

### Full unit suite

```text
short test summary info ===========================
FAILED tests/test_effect_type.py::test_current_glp1_baseline_plant - Assertio...
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_glp1_lane.py::test_glp1_elixa_located_and_primary_membership
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_source_hierarchy.py::test_published_target_effect_beats_reconstructed_counts
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
FAILED tests/test_ty2_protocol_binding.py::test_glp1_rebuild_membership - Ass...
11 failed, 909 passed in 824.89s (0:13:44)
```

Full output: `.tmp/ty2/suite.txt`.

### Source hierarchy contract follow-up

```text
...................                                                      [100%]
19 passed, 1 deselected in 3.58s
```

Full output: `.tmp/ty2/source-hierarchy-final.txt`.

The full run exposed a source-hierarchy test that depended on the removed default RR binding. Its fixture was updated afterwards to assert both no-declaration acceptance and explicit protocol RR refusal; no production code changed for that correction. The full suite was not rerun after this test-only correction. Other full-run failures are recorded, not asserted to be resolved. The full run also overlapped the final legacy-renderer fallback fix; the separate targeted/UI run exercised that final renderer.

Full suite command: `python -m pytest tests -q --tb=short`. Verification child processes were given an offline socket guard permitting loopback for the UI server. No package installation was performed. Standalone binding/compiler/membership contracts: `11 passed, 1 deselected in 3.75s`; only the unmet GLP1 acceptance-count test was deselected in this additional focused run, not in the full suite.

`git diff --check`: PASS (line-ending conversion warnings only). Forbidden files (`harness/gate.py`, `harness/synth.py`, search and screening) were not edited. No portfolio status/submission promotion was made.

## Remaining work / bounded stop

The declared-binding contract and requested GLP1 acceptance counts are not jointly satisfied by the current held evidence. The new k=10/k=11 plant remains a deliberate failing acceptance test, not skipped or weakened. The production rebuild also refuses the stored parity relation. These blockers are recorded in STUCK_FAILURES.md; this lane is not complete or shippable.
