# LANE STR report

## Scope and status

MEASURED base HEAD: `443d8a645f61c140116b7bba12eff31acd96865e` (matches the requested landing4-wip-typg base).
No commit or push. No network acquisition. `harness/synth.py` and `harness/gate.py`
were not edited. Other pages were not rebuilt and their membership declarations
were not edited. This is an implementation/audit result, **not a shipping PASS**.

## Plants first

MEASURED: on the unmodified base, the requested command did **not** throw the
predicted `ValueError('FREEDOM source refused')`. Its actual output was:

```text
python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11
protocol_sha=cf270cd9240e41c5263d208a1976bc163c35a053
PRIMARY: 3-point major adverse cardiovascular events  k=3  HR=0.9224 (0.7644-1.113)  tau2=0.00246
included trials: ['27295427', '28910237', '26630143']
declared-absent trials: ['31185157', '27633186', '34215025', '31189511', '30291013', 'SOUL', 'FLOW']
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

CLAIMED by the lane prompt: the base would crash. That failure was not reproduced;
there is no traceback to paste, and none has been invented.

MEASURED synthetic pre-fix plant (fixture values are synthetic test data only):

```text
python -m pytest tests/test_strands.py::test_two_strands_render_refused_source -q
___________________ test_two_strands_render_refused_source ____________________
    def test_two_strands_render_refused_source():
>       from harness.strands import build, render
E       ModuleNotFoundError: No module named 'harness.strands'
tests/test_strands.py:10: ModuleNotFoundError
1 failed in 1.38s
```

After implementation the same two-strand plant pools the admitted fixture rows
(k=1 and k=2), renders the refused source in both strands, and is deterministic.
Separate tests cover eligibility refusal, binding-axis refusal and selection of
the primary strand before outcome pooling.

## Implementation and hardcode disclosure

| Item | Static / dynamic | Evidence / implementation |
|---|---|---|
| Strand IDs, labels and delivery boundary | Static declaration | Topic JSON, mirrored in B-prime protocol text |
| Primary delivery exclusion | Static protocol rule | FREEDOM-CVO PMID 34873344 is continuous delivery; any-delivery includes it only if eligible, source-verified and typed |
| Membership and refused rows | Dynamic | Eligibility decisions plus source verification plus `effect_type.type_rows` |
| Estimates, CIs, tau², PIs | Dynamic | Unchanged `synth.pool`; no target estimates inserted |
| Held supplemental publication records | Static source-derived inputs | Existing held PubMed XML, copied from the former source adapter |
| Sensitivity effect object | Static source extraction, dynamically verified | Held FDA span; `pooled=False`; never enters candidate assembly |
| Legacy identifier registry | Static identifiers only | Existing policies preserved; ten modules have identical runtime ASTs after resolving registry references |
| Synthetic test effects | Static test fixtures | Explicitly synthetic; not clinical output |

`harness/strands.py` builds and renders declared strands without naming a topic.
Primary membership is selected before the existing outcome synthesis, so the
primary result and its dependent analyses use the declared primary strand.
Strand members and primary members are checked for equality. Source failures
render `UNVERIFIED_FACT/REFUSED`; typed failures render `REFUSED` with the binding
axis and reason. Typed strand verdicts are persisted in `effect_types.json`.

The page-specific `harness/glp1.py` was deleted. Its offline source acquisition
recipes now live in `scripts/glp1_sources.py`; existing scripts import that helper.
The old page-specific pipeline/renderer branches were replaced with configuration
checks. The no-topic-slug grep test covers every Python file under `harness/`.
Existing identifiers elsewhere in the harness were moved to
`registry/topic_identifiers.json`; this is identifier externalization, not a claim
that every historical policy has been redesigned as general machinery.

## Source validation and digest repair

MEASURED: five axis references pinned SHA-256
`3a38e606a533211291b120eb18f9c0c8f82142c1fe9ce7f8f6b597ab40e6bd1f`,
but the committed `outputs/handover/typg/outcomes.json` bytes hash to
`539e622e2882841a4fd3a56e68d9c36ae6892fa66975998324b5e20f7864be10`.
Converting the held file's LF line endings to CRLF reproduces the old digest
exactly. Each declared JSON-path span was checked against the held record before
updating the digest reference. The held source file, axis values, JSON paths,
study identifiers and effects were not changed.

Affected fields: censoring for PMIDs 27633186, 31185157, 31189511 and 40162642;
endpoint components for PMID 38785209. This explains the extra digest-related
refusals in the first build. No missing binding value was filled from a target,
and no coercion was authored.

## Measured GLP1 strands

| Strand | k | HR | 95% CI | tau² | Prediction interval |
|---|---:|---:|---|---:|---|
| CONVENTIONAL_GLP1RA | 7 | 0.8883956805 | 0.8283927970–0.9527447462 | 0.0012001907 | 0.7959414242–0.9915891561 |
| GLP1RA_ANY_DELIVERY | 8 | 0.8984083249 | 0.8158230341–0.9893536767 | 0.0067262248 | 0.7234584966–1.1156652691 |

MEASURED: FLOW (PMID 38785209) is REFUSED on axis 8, censoring:
`FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR`.
AMPLITUDE-O (PMID 34215025) is REFUSED on axis 8, censoring:
`NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD`.
Harmony Outcomes (PMID 30291013) is REFUSED on axis 4, endpoint components:
MI and stroke fatality are unspecified; no declared coercion maps them to
nonfatal components. These identifiers/names are present in the held trial
records. All three refused rows appear in both strand tables.

MEASURED: the FREEDOM-CVO end-of-treatment HR 1.36 (0.96–1.92) is displayed as a
source-verified sensitivity value and is never pooled. Its separately evidenced
end-of-study row is admitted only to the any-delivery strand.

## Verification

Final build output:

```text
protocol_sha=cf270cd9240e41c5263d208a1976bc163c35a053
PRIMARY: 3-point major adverse cardiovascular events  k=7  HR=0.8884 (0.8284-0.9527)  tau2=0.0012
included trials: ['31185157', '27633186', '27295427', '31189511', '28910237', '26630143', 'SOUL']
declared-absent trials: ['34215025', '30291013', 'FLOW']
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

Focused strand/lane/browser UI tests:

```text
........                                                                 [100%]
8 passed in 143.21s (0:02:23)
```

Final dictionary-order regression and general-module checks:

```text
.....                                                                    [100%]
5 passed in 6.33s
```

The full-suite process began before the final dictionary-rendering ordering fix.
The final targeted regression, rebuild and reproduction were run after that fix.
The byte-order fix changes presentation of structured axis metadata, not membership.

Second-pass source/identifier/statistical validation:

```text
CONVENTIONAL_GLP1RA unique source-verified members: 31185157, 27633186, 27295427, 31189511, 28910237, 26630143, 40162642
GLP1RA_ANY_DELIVERY unique source-verified members: 31185157, 27633186, 27295427, 31189511, 28910237, 26630143, 40162642, 34873344
Verified, never pooled sensitivity: PMID 34873344 1.36 0.96 1.92
Typed review check: PASS; no identifiers, dates or effect values were authored by the strand engine.
```

Required gate call: `scripts.verify_all.limb_gate_every_page('glp1-ra-mace-t2d')`.
Exact verdict and measured diagnostic counts:

```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=443d8a645f61c140116b7bba12eff31acd96865e base=none tree=dirty:46 files files=1 docs/reviews/glp1-ra-mace-t2d/review.json
SENTENCE_WITHOUT_OBJECT occurrences: 1394
HARMS_INCOMPLETE occurrences: 7
Full, exact return value: LANE-STR-GATE.txt
```

The complete, unabridged return value is in [LANE-STR-GATE.txt](LANE-STR-GATE.txt).
The gate is not bypassed. Its diagnostics include claim-registry coverage of
served prose, manuscript numeric coverage and unresolved harms. No PASS or
submission-ready claim is made.

Required reproduction command:

```text
python scripts/reproduce_review.py glp1-ra-mace-t2d
OK  glp1-ra-mace-t2d

1/1 reproduce (all reproducible)
```

Full suite (`python -m pytest tests/ -q`, the command used by verify_all):

```text
14 failed, 915 passed in 1332.84s (0:22:12)
FAILED tests/test_compat_key.py::test_positive_controls_still_pool_with_matched_keys
FAILED tests/test_effect_type.py::test_current_glp1_baseline_plant - Assertio...
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_manuscript_limb_REFUSES_a_fabricated_number
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
FAILED tests/test_ty2_protocol_binding.py::test_glp1_rebuild_membership - Ass...
FAILED tests/test_typg_axis_evidence.py::test_evidence_cannot_transfer_to_another_effect_or_document
FAILED tests/test_typg_axis_evidence.py::test_flow_does_not_borrow_component_censoring
```

Follow-up after updating obsolete GLP1 count expectations and imports of the
deleted page-specific module (the full suite was not rerun after these test-only
updates):

```text
.............                                                            [100%]
13 passed in 45.69s
```

The other nine full-suite failures remain unresolved in this lane and are listed
in `STUCK_FAILURES.md`. The original full-suite totals above are retained; no
inferred combined pass total is presented as a measured full-suite run.

The initial repository-root `pytest -q` hit a duplicate-module collection error
between archived and live `test_search_v2_isrctn.py`. A root importlib-mode attempt
was superseded after confirming the canonical suite is `tests/`; archived test
copies are not the canonical suite. The canonical run is recorded above.

External sockets were denied for the full-suite and final-validation subprocesses;
the browser contract served only `http://127.0.0.1:8000/` and blocked external requests.
Full test logs remain in `.tmp/full-suite-tests.log`. Registry parity audit:

```text
comparator_second_pass: runtime AST identical after resolving registry references
comparator_truth: runtime AST identical after resolving registry references
compat_direction: runtime AST identical after resolving registry references
eligibility_chain: runtime AST identical after resolving registry references
endpoint_canonical: runtime AST identical after resolving registry references
index: runtime AST identical after resolving registry references
known_missing: runtime AST identical after resolving registry references
registry_first: runtime AST identical after resolving registry references
scope_identity: runtime AST identical after resolving registry references
search_v2: runtime AST identical after resolving registry references
```

## Limits

MEASURED results are the values and command outputs above. The lane prompt's
expected results were treated as CLAIMED until independently reproduced.
No Overmind PASS was obtained and no release was attempted. Changes remain
uncommitted for review. Any failed validation above remains a blocker, not an
inferred success.
