# LANE AUD1B — route repairs measured; integration remains blocked

HEAD: `3f8add72d50b84eae2000625387e3194137a06ea`. No commit, reset, checkout, stash, push, or network retrieval. The supplied dirty worktree was retained. Session-start ProjectIndex and rewrite-workbook context were read. No project/submission promotion was made, so those files were not updated.

## Measured result and denominators

**MEASURED:** 5 of 5 candidate routes were exercised before production edits. Three original plants rendered a number without an admissibility receipt (legacy cache, CT.gov second source, sensitivity fact). Two narrower claims were refuted for the tested production routes: the wholly source-less GLP-1 main row failed admission, and `compute_spec` rejected the incompatible source-less specification. Two supplementary probes exposed the neighbouring holes: an admitted main row with an empty-source co-primary alternative pooled, and direct `calculate` pooled source-less HR studies under RR.

**MEASURED:** all five final adversarial route contracts pass; the new file contains 10 passing tests including compatible positive controls, stale-receipt rejection, and regulatory path/digest checks. Final focused suite: 148 of 148 passed. Additional GS suite: 4 of 11 passed, 7 failed. The HTTP UI contract is one of the four passing GS tests. This is not a green full-repository result.

**MEASURED:** GLP-1 rebuild with `--now 2026-09-11` fails after the regulatory adapter repair, at the protected fragility caller's untyped hypothetical null study. The GLP-1 gate refuses the existing served artifacts. No successful rebuild, publication, certification, or release readiness is claimed.

## Candidate-by-candidate evidence

| Candidate | Before edits | Final behaviour / stopping path |
|---|---|---|
| 1. Cached legacy strand | Cached pool `0.123456` rendered despite having no admission receipt. | Members go through `type_rows`; all cached legacy pools are refused pending regeneration, including missing-primary/missing-identity cases. Members move to refusals, pool becomes null, k becomes zero; no cache number renders. |
| 2. Empty-source alternative co-primary | Literal all-empty-source GLP-1 plant did **not** fire: main row was refused by `type_rows` for missing endpoint-of-result evidence. With a valid main source and an empty alternative source, the alternative RR `0.123456` pooled. | Replacement row is built from its own evidence, not inherited main receipts/spans; complete alternative set goes through `type_rows` then strict pooling. Any refusal suppresses the entire alternative pool. A nonnumeric typed refusal uses the existing trial-alternatives renderer. Compatible HR alternative remains computable. |
| 3. Envelope specification | `compute_spec` did **not** fire: it checks row scale and `claimgraph.verify_fact` before calling `calculate`. Direct `calculate` did pool source-less HR Study inputs under RR. | `calculate` requires existing permitted admission receipts and calls `pool(..., require_study_effect=True)`. Never-typed alternatives stay NOT_COMPUTABLE through the existing exception handler in `compute_spec`. Stale and wrong-pool-scale receipts also refuse; typed positive control computes. |
| 4. CT.gov second source | The count-based registry payload rendered RR `0.123` / implied effect `0.123457` in the trial's cross-source judgement beside the main HR. Its different-endpoint warning did not suppress the numeric object. | `_build_outcome` types the registry extraction against the same outcome target. On refusal the displayed cross-source object contains state, reason and unification only; no registry number or numeric span is rendered. |
| 5. Sensitivity fact | Source-backed HR `1.02` rendered as FACT without an admission receipt. | `strands.build` types sensitivity rows against the target. Rejected sensitivity rows are kept in `sensitivity_refusals` and displayed, labelled `Sensitivity value: ...`, in the existing strand refusal tables; only admitted rows remain in the fact-rendered sensitivity list. Valid source-backed HR control retains FACT and permitted receipt. |

### Fixture and interpretation disclosures

All planted identifiers/numbers are explicit test fixtures. No synthetic cache was written over a real cache. The helpers read copied GLP-1 configuration and synthetic records under `.tmp/aud1b-*`. The sensitivity fixture copies held ELIXA evidence and uses a synthetic identifier to test source verification independently from effect compatibility; it is not a research result.

The first CT.gov probe used an analysis-only Odds Ratio payload; it did not enter `extract_ctgov`, whose second-source route expects structured groups/counts (or supported continuous data). Before any production edit it was replaced by a count-based RR payload; that successful output is pasted below. An initial test harness import typo was also corrected before production edits.

The original cache/sensitivity probes supplied an RR configured target without a protocol binding block. Existing compiler semantics intentionally treat configuration alone as non-binding (the source-hierarchy regression enforces this). Those pre-fix outputs prove missing mandatory receipts and numeric rendering, not a pre-fix binding-axis REFUSE. Final regression fixtures explicitly bind the measure axis to test semantic incompatibility as well. No claim is made that the strengthened fixture bytes are identical to the first probes. The compatible-main co-primary variant and the direct calculate probe are separately labelled rather than being described as successful literal versions of the two refuted claims.

## Implementation and ownership

- `harness/effect_type.py`: `type_rows` now makes unification refusal/unknown status non-permitted in the transported admission receipt while preserving axis metadata. Admission compares explicitly binding effect measures. `typed_studies` transports row receipts and constructs the required study-effect objects. `type_attached_strands` refuses untrusted legacy cached pools rather than reusing their summaries.
- `harness/pipeline.py::_build_outcome`: small call-site changes type CT.gov second-source rows and co-primary alternatives; alternative pools use strict synthesis. The original main-pool call remains strict.
- `harness/envelope.py::calculate`: no implicit admission of new alternative trials; require an existing permitted receipt and use strict pooling. It does not manufacture a target from an alternative's own label.
- `harness/strands.py::build`: sensitivity admission plus existing refusal-table transport; declared strand pooling uses typed studies and `require_study_effect=True`. No renderer change remains.
- `harness/claimgraph.py::regulatory_fact`: four-line schema adaptation under the prompt's explicit regulatory-path repair instruction. FLOW's flat `extracted_text_path` / `document_path` were ignored because only `held.extracted_text` / `held.held_in_tree` were read. The missing value, not an actual absolute manifest path, triggered the misleading repository-relative error. The fix preserves both manifest strings as relative paths; it does not resolve or rewrite them to absolute paths.
- `tests/test_admissibility_routes.py`: ten scoped route/positive/source tests. Existing test expectations were not weakened or edited.

The shared admission boundary is `type_rows -> admissibility`; production pools touched by the lane use `require_study_effect=True`. A refusal is preserved as data and rendered without the rejected number. Cached legacy pools take the explicitly permitted refusal option rather than attempting an undocumented source/eligibility reconstruction.

## Static versus dynamic disclosure

| Item | Static / declared | Dynamic / measured |
|---|---|---|
| Policy | Existing binding-axis semantics; verdict names; cache refusal | Each row's local source, numeric inputs, target and type/admission result |
| Adversarial fixtures | Synthetic IDs and values; RR/HR contrasts | Production outcome/strand/specification calculations and rendered HTML |
| Regulatory adapter | Two supported schema key layouts | Manifest relative paths, held bytes, SHA-256, located spans |
| Source review | Three EXTRACTED source decisions selected from manifest | IDs/NCTs joined to held records and held PubMed XML augmentation; date syntax; interval values relocated in production spans |
| Build | Required `--now 2026-09-11` label | Actual local build and gate output; no claim of historical as-of completeness |
| Test counts | None taken from prior report/memory | Process output pasted below |

## Integration blockers and bounded verification

The original path error is fixed. The previously missing FLOW PDF is present and its bytes and extraction match the manifest. Nevertheless `claimgraph.verify_fact` refuses FLOW because the held bytes do not satisfy the committed-byte check in this supplied snapshot. The no-commit instruction was respected; no provenance bypass was introduced.

The build next reaches `harness/fragility.py::build`, which constructs `Study('hypothetical null', ...)` and passes it to `envelope.calculate` without a receipt or exception handling. The strict API now refuses that input. `fragility.py` is outside the lane's exclusive ownership. The integration repair must retain explicit counterfactual status and handle refusal (or provide a properly typed counterfactual contract); silently exempting this caller from admission would reopen the audited boundary.

GS failures are reported, not labelled all pre-existing: four tests supply untyped/stale Study inputs to the now-strict envelope API; one expects untyped regulatory rows to be computable in decomposer replay; one hardcodes three regulatory alternatives whereas the restored FLOW source makes four; one corpus render-contract test encounters unrebuildable/stale statistical layers in another topic. No portfolio repair was attempted. The GLP-1 gate additionally reports stale receipt/certificate/transformation artifacts because the required rebuild cannot finish.

Verification processes use a 900-second cap. Build attempts were bounded to three: original schema failure, post-adapter fragility failure, and final-code confirmation. Focused tests were rerun for material changes and added positive controls; the final output is authoritative. No broader repository test run was represented as green. Compile checks and scoped `git diff --check` passed. The GS HTTP test binds `127.0.0.1:8000` and checks the existing served page; it does not prove a newly rebuilt page exists.

**INFERRED:** future callers that use the same mandatory admission transport and strict synthesis flag cannot exploit the missing-receipt routes shown here. This is a source-level argument, not exhaustive testing of every caller or renderer.

**CLAIMED / not established:** a successful GLP-1 rebuild, green gate, green full repository, or shipped result. These remain unestablished. `STUCK_FAILURES.md` records the concrete remaining integration work.

## Exact verification output

### Final focused suite

```text
COMMAND: C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe -m pytest -q tests/test_admissibility_routes.py tests/test_compat_direction.py tests/test_compat_key.py tests/test_compat_underlying.py tests/test_effect_type.py tests/test_extract_class.py tests/test_in2_verified_inputs.py tests/test_iv_iron_strands.py tests/test_protocol_compiler.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py tests/test_strands.py tests/test_synth.py tests/test_target_endpoint.py tests/test_wrong_endpoint_acceptance.py
........................................................................ [ 48%]
........................................................................ [ 97%]
....                                                                     [100%]
148 passed in 27.32s

EXIT: 0
```

### Final GLP-1 rebuild

```text
COMMAND: C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11
Traceback (most recent call last):
  File "C:\mh-r-AUD1\scripts\build_topic.py", line 106, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-AUD1\scripts\build_topic.py", line 53, in main
    core = build_review_core(slug, config, records, protocol_sha)
  File "C:\mh-r-AUD1\harness\aact_cache.py", line 47, in wrapped
    review = function(slug, *args, **kwargs)
  File "C:\mh-r-AUD1\harness\pipeline.py", line 2295, in build_review_core
    review['statistical_layers'] = statistical_layers.build(review)
                                   ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "C:\mh-r-AUD1\harness\statistical_layers.py", line 7, in build
    return {'envelope': env, 'fragility': fragility.build(review, env, root),
                                          ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-AUD1\harness\fragility.py", line 80, in build
    result = envelope.calculate(studies + [null], scale)
  File "C:\mh-r-AUD1\harness\envelope.py", line 47, in calculate
    raise ValueError('EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict')
ValueError: EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict

EXIT: 1
```

### Final GLP-1 gate

```text
COMMAND: C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe -m harness.gate docs/reviews/glp1-ra-mace-t2d
GATE REFUSE docs/reviews/glp1-ra-mace-t2d
    - L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects
    - CERTIFICATE.json release_sha256 mismatch: recomputed b9f4b8ad8b9de259a3a0ed2ba592a92d7255093d158a8c22bc475153e015d05b vs saved 9c9edd5cd8fcdd6ad5a0f48150aa4fbcef93b7c4cd3b178f8e02523f553aa40f
    - L1: offline replay could not execute (EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict) — cannot confirm reproduction
    - GS: statistical layer objects missing or not re-derivable
    - GS: REFUSED envelope/fragility rendering not generated from re-derived objects
    - GS: REFUSED unbound envelope/fragility sentence outside object rendering
    - GS: envelope cache missing or differs from re-derived object
    - GS: fragility cache missing or differs from re-derived object
    - GS: decomposer cache missing or differs from re-derived object
    - L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-fa86d769130b8e1d1f74: 
    - L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-a9128e6d180a88bc2c08: 
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 31185157: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 31185157: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 27633186: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 27633186: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 27295427: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 27295427: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 31189511: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 31189511: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 28910237: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 28910237: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 26630143: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 26630143: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED 3-point major adverse cardiovascular events / PMID 40162642: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE 3-point major adverse cardiovascular events / PMID 40162642: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED Gastrointestinal adverse events / PMID 31189511: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE Gastrointestinal adverse events / PMID 31189511: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED Adverse events leading to discontinuation / PMID 27295427: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE Adverse events leading to discontinuation / PMID 27295427: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 31185157: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 31185157: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 27633186: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 27633186: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 27295427: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 27295427: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 31189511: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 31189511: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 28910237: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 28910237: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 26630143: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 26630143: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED CONVENTIONAL_GLP1RA / PMID 40162642: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE CONVENTIONAL_GLP1RA / PMID 40162642: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 31185157: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 31185157: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 27633186: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 27633186: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 27295427: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 27295427: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 31189511: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 31189511: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 28910237: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 28910237: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 26630143: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 26630143: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 40162642: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 40162642: missing, stale or refused admissibility verdict
    - L1(effect_type): EFFECT_TYPE_REFUSED GLP1RA_ANY_DELIVERY / PMID 34873344: missing or stale type verdict
    - L1(effect_type): RESULT_INCOMPATIBLE GLP1RA_ANY_DELIVERY / PMID 34873344: missing, stale or refused admissibility verdict

EXIT: 1
```

### Additional GS suite (failures retained)

```text
COMMAND: C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe -m pytest -q tests/test_gs_layers.py
.F.FFFF.FF.                                                              [100%]
================================== FAILURES ===================================
_______________________ test_fragility_direction_plant ________________________

    def test_fragility_direction_plant():
        module = importlib.import_module('harness.fragility')
        from harness.synth import Study
        studies = [Study('a', effect=.1, ci_low=.09, ci_high=.11),
                   Study('b', effect=1.2, ci_low=1.1, ci_high=1.3),
                   Study('c', effect=1.2, ci_low=1.1, ci_high=1.3)]
>       table = module.leave_one_out(studies, 'HR')
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_gs_layers.py:29: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
harness\fragility.py:24: in leave_one_out
    baseline = envelope.calculate(studies, scale)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

studies = [Study(label='a', ai=None, n1i=None, ci=None, n2i=None, effect=0.1, ci_low=0.09, ci_high=0.11, e1i=None, t1i=None, e2i...e, sd2=None, nc2=None, source='', measure='RR', derivation='', design=None, design_adjustment=None, study_effect=None)]
scale = 'HR', method = 'PM', interval = 'HKSJ', model = 'random'

    def calculate(studies, scale, method='PM', interval='HKSJ', model='random'):
        """Canonical PM path; explicit alternative models retain log-scale pooling."""
        if len(studies) < 2:
            raise ValueError('at least two trials required for an envelope pool')
        if scale.upper() not in {'HR', 'RR', 'OR', 'IRR', 'MD', 'SMD'}:
            raise ValueError('unsupported effect scale')
        if method not in {'PM', 'REML'} or interval not in {'HKSJ', 'Wald'} or model not in {'random', 'fixed'}:
            raise ValueError('unsupported model specification')
        from . import effect_type
        from dataclasses import asdict
        rows = [dict(asdict(s), scale=s.measure, id=s.label) for s in studies]
        # A specification may only consume already-admitted effects. Do not infer
        # an endpoint target from the very alternative whose compatibility is at issue.
        if any(not (s.design or {}).get('effect_admissibility', {}).get('permitted') for s in studies):
>           raise ValueError('EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict')
E           ValueError: EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict

harness\envelope.py:47: ValueError
________ test_real_regulatory_positive_controls_and_duplicate_refusal _________

    def test_real_regulatory_positive_controls_and_duplicate_refusal():
        from harness import envelope, claimgraph
        alternatives = envelope._regulatory_alternatives(ROOT)
>       assert len(alternatives) == 3
E       AssertionError: assert 4 == 3
E        +  where 4 = len([{'choice': 'strict 3-point, end of study', 'name': 'ELIXA', 'row': {'ci_high': 1.172, 'ci_low': 0.887, 'effect': 1.02...'effect': 0.82, 'endpoint': '3-point MACE (CV death, non-fatal MI, non-fatal stroke), time to first occurrence', ...}}])

tests\test_gs_layers.py:44: AssertionError
________ test_served_primary_numerical_reproduction_at_page_precision _________

    def test_served_primary_numerical_reproduction_at_page_precision():
        """Numerical positive control is distinct from provenance certification."""
        from harness import envelope
        from harness.known_missing import _study_from_trial
        from harness.synth import pool
        p = envelope.primary(glp1())
        studies = [_study_from_trial(row, 'HR') for row in p['trials']]
>       result = envelope.calculate(studies, 'HR')
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_gs_layers.py:61: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

studies = [Study(label='31185157', ai=None, n1i=None, ci=None, n2i=None, effect=0.79, ci_low=0.57, ci_high=1.11, e1i=None, t1i=N...esign phrase); UNKNOWN is not PARALLEL', 'validity_critical': False}}, design_adjustment=None, study_effect=None), ...]
scale = 'HR', method = 'PM', interval = 'HKSJ', model = 'random'

    def calculate(studies, scale, method='PM', interval='HKSJ', model='random'):
        """Canonical PM path; explicit alternative models retain log-scale pooling."""
        if len(studies) < 2:
            raise ValueError('at least two trials required for an envelope pool')
        if scale.upper() not in {'HR', 'RR', 'OR', 'IRR', 'MD', 'SMD'}:
            raise ValueError('unsupported effect scale')
        if method not in {'PM', 'REML'} or interval not in {'HKSJ', 'Wald'} or model not in {'random', 'fixed'}:
            raise ValueError('unsupported model specification')
        from . import effect_type
        from dataclasses import asdict
        rows = [dict(asdict(s), scale=s.measure, id=s.label) for s in studies]
        # A specification may only consume already-admitted effects. Do not infer
        # an endpoint target from the very alternative whose compatibility is at issue.
        if any(not (s.design or {}).get('effect_admissibility', {}).get('permitted') for s in studies):
>           raise ValueError('EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict')
E           ValueError: EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict

harness\envelope.py:47: ValueError
___________________ test_reml_floor_and_zero_tau_pi_refusal ___________________

    def test_reml_floor_and_zero_tau_pi_refusal():
        from harness.envelope import calculate
        from harness.synth import Study
        studies = [Study(str(i), effect=.8, ci_low=.7, ci_high=.9) for i in range(3)]
>       reml = calculate(studies, 'HR', method='REML')
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_gs_layers.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

studies = [Study(label='0', ai=None, n1i=None, ci=None, n2i=None, effect=0.8, ci_low=0.7, ci_high=0.9, e1i=None, t1i=None, e2i=N...e, sd2=None, nc2=None, source='', measure='RR', derivation='', design=None, design_adjustment=None, study_effect=None)]
scale = 'HR', method = 'REML', interval = 'HKSJ', model = 'random'

    def calculate(studies, scale, method='PM', interval='HKSJ', model='random'):
        """Canonical PM path; explicit alternative models retain log-scale pooling."""
        if len(studies) < 2:
            raise ValueError('at least two trials required for an envelope pool')
        if scale.upper() not in {'HR', 'RR', 'OR', 'IRR', 'MD', 'SMD'}:
            raise ValueError('unsupported effect scale')
        if method not in {'PM', 'REML'} or interval not in {'HKSJ', 'Wald'} or model not in {'random', 'fixed'}:
            raise ValueError('unsupported model specification')
        from . import effect_type
        from dataclasses import asdict
        rows = [dict(asdict(s), scale=s.measure, id=s.label) for s in studies]
        # A specification may only consume already-admitted effects. Do not infer
        # an endpoint target from the very alternative whose compatibility is at issue.
        if any(not (s.design or {}).get('effect_admissibility', {}).get('permitted') for s in studies):
>           raise ValueError('EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict')
E           ValueError: EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict

harness\envelope.py:47: ValueError
________ test_reml_equal_variance_analytic_solution_and_fixed_control _________

    def test_reml_equal_variance_analytic_solution_and_fixed_control():
        import math
        from scipy.stats import norm
        from harness.envelope import calculate
        from harness.synth import Study, pool
        z = norm.ppf(.975)
        studies = [Study(str(i), effect=math.exp(y), ci_low=math.exp(y-z*.1), ci_high=math.exp(y+z*.1)) for i, y in enumerate([-.5, 0., .5])]
>       reml = calculate(studies, 'HR', method='REML')
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_gs_layers.py:88: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

studies = [Study(label='0', ai=None, n1i=None, ci=None, n2i=None, effect=0.6065306597126334, ci_low=0.49857741863748806, ci_high...e, sd2=None, nc2=None, source='', measure='RR', derivation='', design=None, design_adjustment=None, study_effect=None)]
scale = 'HR', method = 'REML', interval = 'HKSJ', model = 'random'

    def calculate(studies, scale, method='PM', interval='HKSJ', model='random'):
        """Canonical PM path; explicit alternative models retain log-scale pooling."""
        if len(studies) < 2:
            raise ValueError('at least two trials required for an envelope pool')
        if scale.upper() not in {'HR', 'RR', 'OR', 'IRR', 'MD', 'SMD'}:
            raise ValueError('unsupported effect scale')
        if method not in {'PM', 'REML'} or interval not in {'HKSJ', 'Wald'} or model not in {'random', 'fixed'}:
            raise ValueError('unsupported model specification')
        from . import effect_type
        from dataclasses import asdict
        rows = [dict(asdict(s), scale=s.measure, id=s.label) for s in studies]
        # A specification may only consume already-admitted effects. Do not infer
        # an endpoint target from the very alternative whose compatibility is at issue.
        if any(not (s.design or {}).get('effect_admissibility', {}).get('permitted') for s in studies):
>           raise ValueError('EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict')
E           ValueError: EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict

harness\envelope.py:47: ValueError
_________ test_decomposer_adjacent_deltas_require_two_verified_steps __________

    def test_decomposer_adjacent_deltas_require_two_verified_steps():
        from harness import envelope, decomposer
        rows = [a['row'] for a in envelope._regulatory_alternatives(ROOT)[:2]]
        steps = decomposer.replay([rows, rows, rows, rows], 'HR', {'method': 'PM', 'interval': 'HKSJ'})
>       assert all(s['computable'] for s in steps)
E       assert False
E        +  where False = all(<generator object test_decomposer_adjacent_deltas_require_two_verified_steps.<locals>.<genexpr> at 0x00000213E251FE00>)

tests\test_gs_layers.py:113: AssertionError
______________ test_corpus_render_contract_and_tampered_sentence ______________

tmp_path = WindowsPath('C:/mh-r-AUD1/.tmp/pytest-of-mahmo/pytest-22/test_corpus_render_contract_an0')

    def test_corpus_render_contract_and_tampered_sentence(tmp_path):
        from harness.gate import check_statistical_layers
        from harness.canonical import review_sha256, sha256_text
        for path in sorted((ROOT / 'docs/reviews').glob('*/review.json')):
>           assert check_statistical_layers(path.parent) == [], path.parent.name
E           AssertionError: balanced-crystalloids-vs-saline-mortality
E           assert ['GS: statist...rived object'] == []
E             
E             Left contains 6 more items, first extra item: 'GS: statistical layer objects missing or not re-derivable'
E             Use -v to get more diff

tests\test_gs_layers.py:124: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_gs_layers.py::test_fragility_direction_plant - ValueError: ...
FAILED tests/test_gs_layers.py::test_real_regulatory_positive_controls_and_duplicate_refusal
FAILED tests/test_gs_layers.py::test_served_primary_numerical_reproduction_at_page_precision
FAILED tests/test_gs_layers.py::test_reml_floor_and_zero_tau_pi_refusal - Val...
FAILED tests/test_gs_layers.py::test_reml_equal_variance_analytic_solution_and_fixed_control
FAILED tests/test_gs_layers.py::test_decomposer_adjacent_deltas_require_two_verified_steps
FAILED tests/test_gs_layers.py::test_corpus_render_contract_and_tampered_sentence
7 failed, 4 passed in 14.75s

EXIT: 1
```

### Second-pass source/identifier/date/numeric review

```text
{
  "review": [
    {
      "trial": "ELIXA",
      "source_id": "FDA_NDA208471_StatR_2016",
      "id": "PMID 26630143",
      "id_in_held_records": true,
      "record_nct": "NCT01147250",
      "manifest_nct": "NCT01147250",
      "document_digest_matches": true,
      "text_digest_matches": true,
      "relative_paths": true,
      "retrieved_utc": "2026-09-16T18:33:00Z",
      "retrieved_utc_iso_valid": true,
      "adapter_span_located": true,
      "production_span_located": true,
      "effect_and_bounds_in_span": true,
      "fact_verdict": {
        "verified": true,
        "class": "FACT",
        "document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38",
        "retrieved_utc": "2026-09-16T18:33:00Z",
        "retrieved_precision": "instant",
        "span": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02."
      }
    },
    {
      "trial": "FREEDOM-CVO",
      "source_id": "FDA_NDA209053_EMDAC_briefing_2023",
      "id": "PMID 34873344",
      "id_in_held_records": true,
      "record_nct": "NCT01455896",
      "manifest_nct": "NCT01455896",
      "document_digest_matches": true,
      "text_digest_matches": true,
      "relative_paths": true,
      "retrieved_utc": "2026-09-16T18:36:00Z",
      "retrieved_utc_iso_valid": true,
      "adapter_span_located": false,
      "production_span_located": true,
      "effect_and_bounds_in_span": true,
      "fact_verdict": {
        "verified": true,
        "class": "FACT",
        "document_sha256": "719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103",
        "retrieved_utc": "2026-09-16T18:36:00Z",
        "retrieved_precision": "instant",
        "span": "Table 19. Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke) and 4-Point MACE (CV \r\nDeath, Nonfatal MI, Nonfatal Stroke, Unstable Angina) \u2013 ITT Population End of Study, FREEDOM (CLP-107) \r\nMACE Type \r\nITCA 650 Number of \r\nEvents/Total No. (%) \r\nIR (n/100 PY) \r\nControl Number of \r\nEvents/Total No. (%) \r\nIR (n/100 PY) HR (95% CI)** \r\n3-Point MACE* 85/2075 (4.1%) \r\n2.94 \r\n69/2081 (3.3%) \r\n2.37 1.24 (0.90, 1.70) \r\n4-Point MACE 95/2075 (4.6%) \r\n3.29 \r\n79/2081 (3.8%) \r\n2.72 1.21 (0.90, 1.63) \r\nSource: CDER Review staff. Analysis: R v. 4.2 (MACE.R); data: adef.xpt from SDN0000. \r\n* One hundred fifty-four positively adjudicated 3-point MACE events. \r\n** Based on a Cox proportional hazards regression model. \r\nAbbreviations: CV, cardiovascular; HR, hazard ratio; IR, incidence rate; ITCA 650, exenatide in DUROS device; ITT, intent-to-treat; MACE, major adverse \r\ncardiovascular event; MI, myocardial infarction; PY, patient-years \r\n\r\n### PAGE 59\r\n59 \r\nFigure 13. Kaplan-Meier Plot for Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke) ) \u2013 \r\nITT Population End of Study, CLP-107 (FREEDOM) \r\n \r\nSource: CDER Review staff; software: R v. 4.2; script: MACE_analysis.R; data: adef.xpt (SDN0000); subgroup HR estimated using primary analysis model on \r\nsubsetted data (Cox proportional hazards model with treatment [ITCA 650 or control], study and CV risk as strata). \r\nOn-study analysis. \r\nAbbreviations: CV, cardiovascular; HR, hazard ratio; ITCA 650, exenatide in DUROS device; ITT, intent-to-treat; MACE, major adverse cardiovascular event; \r\nMI, myocardial infarction \r\nTable 20. Key Subgroup Analyses: Studies CLP-103, CLP-105 and CLP-107 Pooled Analyses and Study CLP-107 (FREEDOM) \r\nSubgroup \r\n3-Point MACE \r\n(Pooled) \r\n4-Point MACE \r\n(Pooled) \r\n3-Point MACE \r\n(FREEDOM) \r\n4-Point MACE \r\n(FREEDOM) \r\nAge \u226565 years \r\nDrug, n (%) \r\nComparator, n (%) \r\nHR (95% CI) \r\n41 (4.4) \r\n23 (2.6) \r\n1.79 (1.08, 2.99) \r\n43 (4.7) \r\n26 (3.0) \r\n1.67 (1.02, 2.71) \r\n41 (5.0) \r\n22 (2.7) \r\n1.88 (1.12, 3.15) \r\n43 (5.2) \r\n25 (3.1) \r\n1.73 (1.06, 2.84) \r\neGFR <60 mL/min/1.73m2 \r\nDrug, n (%) \r\nComparator, n (%) \r\nHR (95% CI) \r\n13 (6.2) \r\n6 (2.6) \r\n2.32 (0."
      }
    },
    {
      "trial": "FLOW",
      "source_id": "FDA_NDA209637_s025_label_2025",
      "id": "PMID 38785209",
      "id_in_held_records": true,
      "record_nct": "NCT03819153",
      "manifest_nct": "NCT03819153",
      "document_digest_matches": true,
      "text_digest_matches": true,
      "relative_paths": true,
      "retrieved_utc": "2026-09-18T07:58:00Z",
      "retrieved_utc_iso_valid": true,
      "adapter_span_located": true,
      "production_span_located": true,
      "effect_and_bounds_in_span": true,
      "fact_verdict": {
        "verified": false,
        "class": "UNVERIFIED_FACT",
        "reason": "held document or extraction differs from committed bytes"
      }
    }
  ],
  "checked": 3
}
```

### Pre-fix production plants — captured before production changes

```text
{"html": "<div class='banner'><h3>Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions)</h3><p></p><ul><li><strong>Strand SYNTHETIC</strong> — Synthetic cached strand [<code></code>]: pooled 0.123456 (0.1–0.2), k=1, HKSJ/PM &tau;&sup2;=, <strong>significant</strong></li></ul><p class='note'>Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.</p></div>", "plant": "legacy", "strand": {"members": [{"ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "effect_type_id": "effect-type:110ba7592081b76824823cdf1868e7824df1b2abdee4c5345c1be75d8a3160b9", "pmid": "99999999", "scale": "HR", "source": "The primary outcome was 3-point MACE. The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "trial": "SYNTHETIC-AUD1B", "unification": {"coercion_ids": [], "disclosures": ["axis 1 unstated", "axis 2 unstated", "axis 3 unstated", "axis 4 unstated", "axis 5 unstated", "axis 6 unstated", "axis 7 unstated", "axis 8 unstated", "axis 10 unstated", "axis 11 unstated", "axis 12 unstated"], "intercurrent_events": "UNRESOLVED", "status": "MATCH"}}], "name": "Synthetic cached strand", "pool": {"ci_high": 0.2, "ci_low": 0.1, "effect": 0.123456, "k": 1}, "strand": "SYNTHETIC"}}
{"plant": "alternative", "refused": [{"absent_kind": "refused_on_evidence", "admissibility": {"component_distance": 3, "definition_span": "", "effect_measure": "HR", "extra_components": [], "inputs": {"ai": null, "ci": null, "ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "n1i": null, "n2i": null}, "missing_components": ["cardiovascular death", "myocardial infarction", "stroke"], "permitted": false, "reason": "RESULT_INCOMPATIBLE: endpoint-of-result differs from target; definition_span and result_span attached", "result_span": "", "source": "", "target_components": [], "target_endpoint_class": "DIFFERENT_OUTCOME", "verdict": "INCOMPATIBLE"}, "alternative_co_primary": {"ci_high": 0.2, "ci_low": 0.1, "effect": 0.123456, "scale": "RR", "source": ""}, "alternatives": [], "ci_high": 0.8, "ci_low": 0.3, "definition_span": "", "derivation": "reported", "design": {"adjustment_axis": {"status": "UNRESOLVED"}, "adjustment_status": "UNRESOLVED", "basis": [], "correlation_handling": {"evidence": [], "method": "none"}, "design": "UNKNOWN", "design_action": {"action": "DESIGN_UNPROVEN", "decision_state": "design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify", "gate_id": "design-key:design-unproven", "reason": "no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL", "validity_critical": false}, "effect_admissibility": {"component_distance": 3, "definition_span": "", "effect_measure": "HR", "extra_components": [], "inputs": {"ai": null, "ci": null, "ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "n1i": null, "n2i": null}, "missing_components": ["cardiovascular death", "myocardial infarction", "stroke"], "permitted": false, "reason": "RESULT_INCOMPATIBLE: endpoint-of-result differs from target; definition_span and result_span attached", "result_span": "", "source": "", "target_components": [], "target_endpoint_class": "DIFFERENT_OUTCOME", "verdict": "INCOMPATIBLE"}, "estimator_source": "PUBLISHED_HR", "se_provenance": "synth.Study.yi_vi:reported-effect-ci", "unit_of_randomisation": "UNKNOWN"}, "effect": 0.5, "effect_type_id": "effect-type:84ffd21f386df41ed81a23caeced9fbb09b749427cc2696f9c1b4c83a7491655", "id": "PMID 99999999", "intercurrent_events": "UNRESOLVED", "label": "SYNTHETIC-AUD1", "outcome": "3-point major adverse cardiovascular events", "provenance": "fulltext_verified", "reason": "RESULT_INCOMPATIBLE: endpoint-of-result differs from target; definition_span and result_span attached", "result_span": "", "scale": "HR", "se_source": "derived_from_ci", "selected_estimator": "published_effect_ci", "selection_rule": "KEEP_REPORTED_EFFECT", "source": "", "state": "EFFECT_TYPE_REFUSED", "unification": {"reason": "RESULT_INCOMPATIBLE: endpoint-of-result differs from target; definition_span and result_span attached", "status": "REFUSE"}, "verified": "not-yet", "verify_basis": "effect not located in committed source"}], "result": {"k": 0, "present": false, "reason": "RESULT_INCOMPATIBLE: endpoint-of-result differs from target; definition_span and result_span attached"}}
{"calculate": {"ci": [0.05279968671842359, 4.734876578590883], "estimate": 0.5, "i2": 0.0, "interval": "HKSJ", "k": 2, "method": "PM", "model": "random", "pi": null, "pi_reason": "NOT_COMPUTABLE: tau2=0 collapses the prescribed PI onto the CI; no distinct PI is served", "scale": "RR", "tau2": 0.0}, "plant": "specification", "specification": {"axis": "source", "choice": "source-less HR in RR", "computable": false, "inputs": [{"ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "id": "synthetic-0", "label": "0", "scale": "HR", "source": ""}, {"ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "id": "synthetic-1", "label": "1", "scale": "HR", "source": ""}], "options": {}, "reason": "NOT_COMPUTABLE: 0: incompatible effect scale; 0: missing full document_sha256; 1: incompatible effect scale; 1: missing full document_sha256", "result": null, "spec_id": "synthetic"}}
{"cross_source": {"agree": null, "corroborates_endpoint": false, "ctgov_rr": 0.123, "ctgov_source": "ClinicalTrials.gov results (structured): outcome '3-point MACE' COUNT_OF_PARTICIPANTS 10/100 (Liraglutide) vs 81/100 (Placebo)", "endpoint_match": "SECOND_SOURCE_DIFFERENT_ENDPOINT", "endpoint_match_reason": "registry component set does not match the pooled trial component set (expected ['cardiovascular death', 'myocardial infarction', 'stroke']; observed none)", "endpoint_match_tolerance_log": 0.12, "identity": {"component_match": false, "measure_type": "risk ratio from counts", "population_match": true, "title_match": true, "verdict": "SECOND_SOURCE_DIFFERENT_ENDPOINT"}, "note": "SECOND_SOURCE_DIFFERENT_ENDPOINT: registry component set does not match the pooled trial component set (expected ['cardiovascular death', 'myocardial infarction', 'stroke']; observed none)", "pooled_effect_for_endpoint_match": 0.5, "pooled_scale_for_endpoint_match": "HR", "registry_comparator_value": 81.0, "registry_description": "", "registry_effect_label": "CT.gov risk ratio from counts", "registry_implied_effect": 0.123457, "registry_intervention_value": 10.0, "registry_measure_type": "COUNT_OF_PARTICIPANTS", "registry_param_type": "COUNT_OF_PARTICIPANTS", "registry_population": "", "registry_selected_timepoint": "", "registry_timeframe": "", "registry_title": "3-point MACE", "registry_type": "PRIMARY", "second_source_verdict": "SECOND_SOURCE_DIFFERENT_ENDPOINT"}, "html": "<table class='arms'><tr><th>Trial</th><th>Id</th><th>Input</th><th>Source</th></tr><tr><td colspan=\"4\"><p><span data-claim-id=\"fact-1d0ec4f03770ef23\" data-claim-class=\"UNVERIFIED_FACT\"><strong>[UNVERIFIED_FACT]</strong> PMID 99999999: HR 0.5 (0.3, 0.8).</span></p><p><span data-claim-id=\"page-cb38972ec1d036b142d6\" data-claim-class=\"UNVERIFIED_FACT\"><strong>[UNVERIFIED_FACT]</strong> PMID 99999999: document None; SHA-256 None; retrieved None; located span: None</span></p><p><span data-claim-id=\"page-4fadf955bcd3be1b3b33\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> design: {\"adjustment_axis\":{\"status\":\"UNRESOLVED\"},\"adjustment_status\":\"UNRESOLVED\",\"basis\":[{\"source\":\"trial reported estimate label\",\"span\":\"HR 0.50 (95% CI 0.30-0.80\"}],\"correlation_handling\":{\"evidence\":[],\"method\":\"none\"},\"design\":\"UNKNOWN\",\"design_action\":{\"action\":\"DESIGN_UNPROVEN\",\"decision_state\":\"design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify\",\"gate_id\":\"design-key:design-unproven\",\"reason\":\"no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL\",\"validity_critical\":false},\"effect_admissibility\":{\"component_distance\":0,\"definition_span\":\"The primary outcome was 3-point MACE.\",\"effect_measure\":\"HR\",\"extra_components\":[],\"inputs\":{\"ai\":null,\"ci\":null,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"n1i\":null,\"n2i\":null},\"missing_components\":[],\"permitted\":true,\"result_span\":\"The primary outcome had HR 0.50 (95% CI 0.30-0.80).\",\"source\":\"abstract source-reported HR (registered estimand): The primary outcome had HR 0.50 (95% CI 0.30-0.80).\",\"target_components\":[\"cardiovascular death\",\"myocardial infarction\",\"stroke\"],\"target_endpoint_class\":\"EXACT_TARGET\",\"verdict\":\"EXACT\"},\"estimator_source\":\"PUBLISHED_HR\",\"published_alternative\":{\"adjusted\":false,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"scale\":\"HR\",\"span\":\"HR 0.50 (95% CI 0.30-0.80\"},\"se_provenance\":\"synth.Study.yi_vi:reported-effect-ci\",\"unit_of_randomisation\":\"UNKNOWN\"} [adjudication: OWED]</span></p><p><span data-claim-id=\"page-74915ffc2fb2ffc2c961\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> derivation: reported [adjudication: OWED]</span></p><p><span data-claim-id=\"page-bce00d6f0fbb0c82e719\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> selection_rule: KEEP_REPORTED_EFFECT [adjudication: OWED]</span></p><p><span data-claim-id=\"page-3e252ce007b3d4dba11c\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> target_endpoint_class: EXACT_TARGET [adjudication: OWED]</span></p><p><span data-claim-id=\"page-2297c3478b454d8ce3c2\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> target_endpoint_alternatives: [{\"candidate_id\":\"ctgov:0\",\"registry_title\":\"3-point MACE\",\"registry_type\":\"PRIMARY\",\"source_kind\":\"reconstruction\",\"source_rank_kind\":\"reconstruction\",\"source_type\":\"ctgov_results\",\"target_endpoint_class\":\"EXACT_TARGET\"}] [adjudication: OWED]</span></p><p><span data-claim-id=\"page-1bfbccd0180fd07082cc\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> cross_source: {\"agree\":null,\"corroborates_endpoint\":false,\"ctgov_rr\":0.123,\"ctgov_source\":\"ClinicalTrials.gov results (structured): outcome '3-point MACE' COUNT_OF_PARTICIPANTS 10/100 (Liraglutide) vs 81/100 (Placebo)\",\"endpoint_match\":\"SECOND_SOURCE_DIFFERENT_ENDPOINT\",\"endpoint_match_reason\":\"registry component set does not match the pooled trial component set (expected ['cardiovascular death', 'myocardial infarction', 'stroke']; observed none)\",\"endpoint_match_tolerance_log\":0.12,\"identity\":{\"component_match\":false,\"measure_type\":\"risk ratio from counts\",\"population_match\":true,\"title_match\":true,\"verdict\":\"SECOND_SOURCE_DIFFERENT_ENDPOINT\"},\"note\":\"SECOND_SOURCE_DIFFERENT_ENDPOINT: registry component set does not match the pooled trial component set (expected ['cardiovascular death', 'myocardial infarction', 'stroke']; observed none)\",\"pooled_effect_for_endpoint_match\":0.5,\"pooled_scale_for_endpoint_match\":\"HR\",\"registry_comparator_value\":81.0,\"registry_description\":\"\",\"registry_effect_label\":\"CT.gov risk ratio from counts\",\"registry_implied_effect\":0.123457,\"registry_intervention_value\":10.0,\"registry_measure_type\":\"COUNT_OF_PARTICIPANTS\",\"registry_param_type\":\"COUNT_OF_PARTICIPANTS\",\"registry_population\":\"\",\"registry_selected_timepoint\":\"\",\"registry_timeframe\":\"\",\"registry_title\":\"3-point MACE\",\"registry_type\":\"PRIMARY\",\"second_source_verdict\":\"SECOND_SOURCE_DIFFERENT_ENDPOINT\"} [adjudication: OWED]</span></p><p><span data-claim-id=\"page-9d03b5b79db522432783\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> components: [\"cardiovascular death\",\"myocardial infarction\",\"stroke\"] [adjudication: OWED]</span></p></td></tr></table>", "plant": "cross_source"}
{"html": "<div class='banner'><h3>Declared strands: primary and any delivery</h3><ul><li><strong>Strand CONVENTIONAL_GLP1RA</strong> — Conventional GLP-1RA delivery [<code></code>]: <code>REFUSED</code>: No admitted source-backed typed effects</li><li><strong>Strand GLP1RA_ANY_DELIVERY</strong> — GLP-1RA, any delivery [<code></code>]: <code>REFUSED</code>: No admitted source-backed typed effects</li></ul></div><h4>Conventional GLP-1RA delivery: membership and refusals</h4><table><tr><th>Trial</th><th>Status</th><th>Axis</th><th>Reason</th></tr></table><h4>GLP-1RA, any delivery: membership and refusals</h4><table><tr><th>Trial</th><th>Status</th><th>Axis</th><th>Reason</th></tr></table><h4>Sensitivity values (never pooled)</h4><span data-claim-id=\"sensitivity-99999999\" data-claim-class=\"FACT\"><strong>[FACT]</strong> PMID 99999999: HR 1.02 (0.887, 1.172).</span>", "plant": "sensitivity", "row": {"adjudication_id": "ADJ-GLP1-005", "ci_high": 1.172, "ci_low": 0.887, "conflicting_spans": {"definition_3p": {"offset": 47019, "span": "MACE, defined as cardiovascular death, non-fatal \nMI, and non-fatal stroke"}, "executive_summary_3p": {"offset": 16629, "span": "There were 792 secondary MACE events observed in the study for the ITT population, 400 in \nthe lixisenatide group and 392 in the placebo group. The pre-specified Cox proportional hazards \nanalysis resulted in a hazard ratio estimate of 1.02 with an associated 95% confidence interval of \n(0.89, 1.17)."}, "primary_4p_table6": {"offset": 45391, "span": "Table 6: Analysis of the Primary CV endpoint (On-study Analysis) \n Placebo \n(N=3,034) \nLixisenatide \n(N=3,034) \nHazard ratio \n(95% CI) \nPrimary CV endpoint 1.02 \n(0.89, 1.17) \n No. of patients with event (%) 399 (13.2%) 406 (13.4%)"}, "primary_4p_text": {"offset": 63374, "span": "By the end of the study, there were 805 MACE+ events, 406 in \nthe lixisenatide group and 399 in the placebo group. The 95% confidence level for MACE+ is \n1.02 (0.89, 1.17)."}, "table8_onstudy_3p": {"offset": 47684, "span": "Table 8: Analysis of the MACE Endpoint \n Placebo \n(N=3,034) \nLixisenatide \n(N=3,034) \nHazard ratio \n(95% CI) \nMACE endpoint (on-study) 1.02 \n(0.89, 1.18) \n No. of patients with event (%) 392 (12.9%) 400 (13.2%)"}, "table8_ontreatment_3p": {"offset": 47957, "span": "MACE endpoint (on-treatment) 1.01 \n(0.87, 1.17) \n No. of patients with event (%) 342 (11.3%) 334 (11.0%)"}, "text_unrounded_3p": {"offset": 47274, "span": "For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \n1.172) with a point estimate of 1.02."}}, "definition_span": "MACE, defined as cardiovascular death, non-fatal \nMI, and non-fatal stroke", "document_path": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf", "document_ref": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf", "document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38", "effect": 1.02, "extracted_text": "outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt", "extracted_text_sha256": "952b8088e14b457d97364f13bb0f9407803bf875faed5fa30d995972e2687a26", "id": "PMID 99999999", "label": "SYNTHETIC-AUD1B", "outcome": "3-point major adverse cardiovascular events", "override": true, "pooled": false, "result_span": "For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \n1.172) with a point estimate of 1.02.", "retrieved_utc": "2026-09-16T18:33:00Z", "scale": "HR", "source": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.", "source_level": 2, "span": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.", "span_offset": 47847, "state": "SOURCE_CONFLICT (adjudicated: ADJ-GLP1-005)", "trial": "SYNTHETIC-AUD1B"}}
{"plant": "alternative_valid_main", "refused": [], "result": {"Q": 0.0, "ci_high": 0.8, "ci_low": 0.3, "ci_note": "k=1: point estimate and 95% CI are the single trial's reported values, verbatim.", "ci_provenance": "source-reported-CI:k=1-verbatim", "co_primary_sensitivities": [{"alternative": null, "pool": {"Q": 0.0, "ci_high": 0.2, "ci_low": 0.1, "ci_note": "k=1: point estimate and 95% CI are the single trial's reported values, verbatim.", "ci_provenance": "source-reported-CI:k=1-verbatim", "estimate": 0.123456, "k": 1, "pi_note": "prediction interval undefined for k=1", "scale": "RR", "tau2": 0.0}, "rule": "alternative prespecified co-primary endpoint sensitivity", "selected": null, "trial": "SYNTHETIC-AUD1"}], "estimate": 0.5, "estmeasure": {"canonicals": ["HAZARD_RATIO_FIRST_EVENT"], "classes": ["FIRST_EVENT_RATIO"], "labels": ["HR"], "status": "homogeneous"}, "k": 1, "leave_one_out": {"note": "not assessable at k=1 (leave-one-out needs k>=3)"}, "pi_note": "prediction interval undefined for k=1", "scale": "HR"}}
```

### Post-fix production plants — explicitly bound final fixtures

```text
{"html": "<div class='banner'><h3>Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions)</h3><p></p><ul><li><strong>Strand SYNTHETIC</strong> — Synthetic cached strand [<code></code>]: <code>EFFECT_TYPE_REFUSED</code>: Legacy cached pool refused; regenerate from declared source-backed typed rows</li></ul><p class='note'>Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.</p></div>", "plant": "legacy", "strand": {"k": 0, "members": [], "name": "Synthetic cached strand", "pool": null, "reason": "Legacy cached pool refused; regenerate from declared source-backed typed rows", "refused": [{"absent_kind": "refused_on_evidence", "admissibility": {"definition_span": "The primary outcome was 3-point MACE.", "effect_measure": "HR", "inputs": {"ai": null, "ci": null, "ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "n1i": null, "n2i": null}, "permitted": false, "reason": "axis 9: HR differs from target RR; no valid declared coercion", "result_span": "The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "source": "The primary outcome was 3-point MACE. The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "verdict": "INCOMPATIBLE"}, "ci_high": 0.8, "ci_low": 0.3, "definition_span": "The primary outcome was 3-point MACE.", "design": {"effect_admissibility": {"definition_span": "The primary outcome was 3-point MACE.", "effect_measure": "HR", "inputs": {"ai": null, "ci": null, "ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "n1i": null, "n2i": null}, "permitted": false, "reason": "axis 9: HR differs from target RR; no valid declared coercion", "result_span": "The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "source": "The primary outcome was 3-point MACE. The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "verdict": "INCOMPATIBLE"}}, "effect": 0.5, "effect_type_id": "effect-type:110ba7592081b76824823cdf1868e7824df1b2abdee4c5345c1be75d8a3160b9", "id": "PMID 99999999", "intercurrent_events": "UNRESOLVED", "pmid": "99999999", "reason": "axis 9: HR differs from target RR; no valid declared coercion", "result_span": "The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "scale": "HR", "se_source": "derived_from_ci", "source": "The primary outcome was 3-point MACE. The primary outcome had HR 0.50 (95% CI 0.30-0.80).", "state": "EFFECT_TYPE_REFUSED", "status": "EFFECT_TYPE_REFUSED", "trial": "SYNTHETIC-AUD1B", "unification": {"axis": 9, "axis_name": "effect_measure", "reason": "axis 9: HR differs from target RR; no valid declared coercion", "status": "REFUSE"}}], "status": "EFFECT_TYPE_REFUSED", "strand": "SYNTHETIC"}}
{"html": "<table class='arms'><tr><th>Trial</th><th>Id</th><th>Input</th><th>Source</th></tr><tr><td colspan=\"2\"><span data-claim-id=\"page-e7abc692487f1ec6d04f\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> Recorded trial identity: {\"id\":\"PMID 99999999\",\"label\":\"SYNTHETIC-AUD1\"} [adjudication: OWED]</span></td><td colspan=\"2\"><span data-claim-id=\"page-c8a7588bc94fa30ddee8\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> Recorded non-pooling assessment: {\"design\":{\"adjustment_axis\":{\"status\":\"UNRESOLVED\"},\"adjustment_status\":\"UNRESOLVED\",\"basis\":[],\"correlation_handling\":{\"evidence\":[],\"method\":\"none\"},\"design\":\"UNKNOWN\",\"design_action\":{\"action\":\"DESIGN_UNPROVEN\",\"decision_state\":\"design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify\",\"gate_id\":\"design-key:design-unproven\",\"reason\":\"no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL\",\"validity_critical\":false},\"effect_admissibility\":{\"component_distance\":3,\"definition_span\":\"\",\"effect_measure\":\"HR\",\"extra_components\":[],\"inputs\":{\"ai\":null,\"ci\":null,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"n1i\":null,\"n2i\":null},\"missing_components\":[\"cardiovascular death\",\"myocardial infarction\",\"stroke\"],\"permitted\":false,\"reason\":\"UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE\",\"result_span\":\"\",\"source\":\"\",\"target_components\":[],\"target_endpoint_class\":\"DIFFERENT_OUTCOME\",\"verdict\":\"INCOMPATIBLE\"},\"estimator_source\":\"PUBLISHED_HR\",\"se_provenance\":\"synth.Study.yi_vi:reported-effect-ci\",\"unit_of_randomisation\":\"UNKNOWN\"},\"reason\":\"UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE\",\"state\":\"EFFECT_TYPE_REFUSED\"} [adjudication: OWED]</span></td></tr></table>", "plant": "alternative", "refused": [{"absent_kind": "refused_on_evidence", "admissibility": {"component_distance": 3, "definition_span": "", "effect_measure": "HR", "extra_components": [], "inputs": {"ai": null, "ci": null, "ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "n1i": null, "n2i": null}, "missing_components": ["cardiovascular death", "myocardial infarction", "stroke"], "permitted": false, "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "result_span": "", "source": "", "target_components": [], "target_endpoint_class": "DIFFERENT_OUTCOME", "verdict": "INCOMPATIBLE"}, "alternative_co_primary": {"ci_high": 0.2, "ci_low": 0.1, "effect": 0.123456, "scale": "RR", "source": ""}, "alternatives": [], "ci_high": 0.8, "ci_low": 0.3, "definition_span": "", "derivation": "reported", "design": {"adjustment_axis": {"status": "UNRESOLVED"}, "adjustment_status": "UNRESOLVED", "basis": [], "correlation_handling": {"evidence": [], "method": "none"}, "design": "UNKNOWN", "design_action": {"action": "DESIGN_UNPROVEN", "decision_state": "design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify", "gate_id": "design-key:design-unproven", "reason": "no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL", "validity_critical": false}, "effect_admissibility": {"component_distance": 3, "definition_span": "", "effect_measure": "HR", "extra_components": [], "inputs": {"ai": null, "ci": null, "ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "n1i": null, "n2i": null}, "missing_components": ["cardiovascular death", "myocardial infarction", "stroke"], "permitted": false, "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "result_span": "", "source": "", "target_components": [], "target_endpoint_class": "DIFFERENT_OUTCOME", "verdict": "INCOMPATIBLE"}, "estimator_source": "PUBLISHED_HR", "se_provenance": "synth.Study.yi_vi:reported-effect-ci", "unit_of_randomisation": "UNKNOWN"}, "effect": 0.5, "effect_type_id": "effect-type:84ffd21f386df41ed81a23caeced9fbb09b749427cc2696f9c1b4c83a7491655", "id": "PMID 99999999", "intercurrent_events": "UNRESOLVED", "label": "SYNTHETIC-AUD1", "outcome": "3-point major adverse cardiovascular events", "provenance": "fulltext_verified", "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "result_span": "", "scale": "HR", "se_source": "derived_from_ci", "selected_estimator": "published_effect_ci", "selection_rule": "KEEP_REPORTED_EFFECT", "source": "", "state": "EFFECT_TYPE_REFUSED", "unification": {"axis": 9, "axis_name": "effect_measure", "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "status": "UNKNOWN_FAILS_CLOSED"}, "verified": "not-yet", "verify_basis": "effect not located in committed source"}], "result": {"k": 0, "present": false, "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE"}}
{"calculate": {"refused": "EFFECT_TYPE_REFUSED: missing or refused effect admissibility verdict"}, "plant": "specification", "specification": {"axis": "source", "choice": "source-less HR in RR", "computable": false, "inputs": [{"ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "id": "synthetic-0", "label": "0", "scale": "HR", "source": ""}, {"ci_high": 0.8, "ci_low": 0.3, "effect": 0.5, "id": "synthetic-1", "label": "1", "scale": "HR", "source": ""}], "options": {}, "reason": "NOT_COMPUTABLE: 0: incompatible effect scale; 0: missing full document_sha256; 1: incompatible effect scale; 1: missing full document_sha256", "result": null, "spec_id": "synthetic"}}
{"cross_source": {"corroborates_endpoint": false, "reason": "axis 9: RR differs from target HR; no valid declared coercion", "state": "EFFECT_TYPE_REFUSED", "unification": {"axis": 9, "axis_name": "effect_measure", "reason": "axis 9: RR differs from target HR; no valid declared coercion", "status": "REFUSE"}}, "html": "<table class='arms'><tr><th>Trial</th><th>Id</th><th>Input</th><th>Source</th></tr><tr><td colspan=\"4\"><p><span data-claim-id=\"fact-f63d4a5d6194a2c4\" data-claim-class=\"UNVERIFIED_FACT\"><strong>[UNVERIFIED_FACT]</strong> PMID 99999999: HR 0.5 (0.3, 0.8).</span></p><p><span data-claim-id=\"page-87c208e18131617756da\" data-claim-class=\"UNVERIFIED_FACT\"><strong>[UNVERIFIED_FACT]</strong> PMID 99999999: document None; SHA-256 None; retrieved None; located span: None</span></p><p><span data-claim-id=\"page-4fadf955bcd3be1b3b33\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> design: {\"adjustment_axis\":{\"status\":\"UNRESOLVED\"},\"adjustment_status\":\"UNRESOLVED\",\"basis\":[{\"source\":\"trial reported estimate label\",\"span\":\"HR 0.50 (95% CI 0.30-0.80\"}],\"correlation_handling\":{\"evidence\":[],\"method\":\"none\"},\"design\":\"UNKNOWN\",\"design_action\":{\"action\":\"DESIGN_UNPROVEN\",\"decision_state\":\"design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify\",\"gate_id\":\"design-key:design-unproven\",\"reason\":\"no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL\",\"validity_critical\":false},\"effect_admissibility\":{\"component_distance\":0,\"definition_span\":\"The primary outcome was 3-point MACE.\",\"effect_measure\":\"HR\",\"extra_components\":[],\"inputs\":{\"ai\":null,\"ci\":null,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"n1i\":null,\"n2i\":null},\"missing_components\":[],\"permitted\":true,\"result_span\":\"The primary outcome had HR 0.50 (95% CI 0.30-0.80).\",\"source\":\"abstract source-reported HR (registered estimand): The primary outcome had HR 0.50 (95% CI 0.30-0.80).\",\"target_components\":[\"cardiovascular death\",\"myocardial infarction\",\"stroke\"],\"target_endpoint_class\":\"EXACT_TARGET\",\"verdict\":\"EXACT\"},\"estimator_source\":\"PUBLISHED_HR\",\"published_alternative\":{\"adjusted\":false,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"scale\":\"HR\",\"span\":\"HR 0.50 (95% CI 0.30-0.80\"},\"se_provenance\":\"synth.Study.yi_vi:reported-effect-ci\",\"unit_of_randomisation\":\"UNKNOWN\"} [adjudication: OWED]</span></p><p><span data-claim-id=\"page-74915ffc2fb2ffc2c961\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> derivation: reported [adjudication: OWED]</span></p><p><span data-claim-id=\"page-bce00d6f0fbb0c82e719\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> selection_rule: KEEP_REPORTED_EFFECT [adjudication: OWED]</span></p><p><span data-claim-id=\"page-3e252ce007b3d4dba11c\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> target_endpoint_class: EXACT_TARGET [adjudication: OWED]</span></p><p><span data-claim-id=\"page-2297c3478b454d8ce3c2\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> target_endpoint_alternatives: [{\"candidate_id\":\"ctgov:0\",\"registry_title\":\"3-point MACE\",\"registry_type\":\"PRIMARY\",\"source_kind\":\"reconstruction\",\"source_rank_kind\":\"reconstruction\",\"source_type\":\"ctgov_results\",\"target_endpoint_class\":\"EXACT_TARGET\"}] [adjudication: OWED]</span></p><p><span data-claim-id=\"page-2e1f644cae5d44a0aa1f\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> cross_source: {\"corroborates_endpoint\":false,\"reason\":\"axis 9: RR differs from target HR; no valid declared coercion\",\"state\":\"EFFECT_TYPE_REFUSED\",\"unification\":{\"axis\":9,\"axis_name\":\"effect_measure\",\"reason\":\"axis 9: RR differs from target HR; no valid declared coercion\",\"status\":\"REFUSE\"}} [adjudication: OWED]</span></p><p><span data-claim-id=\"page-9d03b5b79db522432783\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> components: [\"cardiovascular death\",\"myocardial infarction\",\"stroke\"] [adjudication: OWED]</span></p></td></tr></table>", "plant": "cross_source"}
{"html": "<div class='banner'><h3>Declared strands: primary and any delivery</h3><ul><li><strong>Strand CONVENTIONAL_GLP1RA</strong> — Conventional GLP-1RA delivery [<code></code>]: <code>REFUSED</code>: No admitted source-backed typed effects</li><li><strong>Strand GLP1RA_ANY_DELIVERY</strong> — GLP-1RA, any delivery [<code></code>]: <code>REFUSED</code>: No admitted source-backed typed effects</li></ul></div><h4>Conventional GLP-1RA delivery: membership and refusals</h4><table><tr><th>Trial</th><th>Status</th><th>Axis</th><th>Reason</th></tr><tr><td>Sensitivity value: SYNTHETIC-AUD1B</td><td>EFFECT_TYPE_REFUSED</td><td>effect_measure</td><td>axis 9: HR differs from target RR; no valid declared coercion</td></tr></table><h4>GLP-1RA, any delivery: membership and refusals</h4><table><tr><th>Trial</th><th>Status</th><th>Axis</th><th>Reason</th></tr><tr><td>Sensitivity value: SYNTHETIC-AUD1B</td><td>EFFECT_TYPE_REFUSED</td><td>effect_measure</td><td>axis 9: HR differs from target RR; no valid declared coercion</td></tr></table><h4>Sensitivity values (never pooled)</h4>", "plant": "sensitivity", "row": {"absent_kind": "refused_on_evidence", "adjudication_id": "ADJ-GLP1-005", "admissibility": {"definition_span": "MACE, defined as cardiovascular death, non-fatal \nMI, and non-fatal stroke", "effect_measure": "HR", "inputs": {"ai": null, "ci": null, "ci_high": 1.172, "ci_low": 0.887, "effect": 1.02, "n1i": null, "n2i": null}, "permitted": false, "reason": "axis 9: HR differs from target RR; no valid declared coercion", "result_span": "For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \n1.172) with a point estimate of 1.02.", "source": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.", "verdict": "INCOMPATIBLE"}, "axis": "effect_measure", "ci_high": 1.172, "ci_low": 0.887, "conflicting_spans": {"definition_3p": {"offset": 47019, "span": "MACE, defined as cardiovascular death, non-fatal \nMI, and non-fatal stroke"}, "executive_summary_3p": {"offset": 16629, "span": "There were 792 secondary MACE events observed in the study for the ITT population, 400 in \nthe lixisenatide group and 392 in the placebo group. The pre-specified Cox proportional hazards \nanalysis resulted in a hazard ratio estimate of 1.02 with an associated 95% confidence interval of \n(0.89, 1.17)."}, "primary_4p_table6": {"offset": 45391, "span": "Table 6: Analysis of the Primary CV endpoint (On-study Analysis) \n Placebo \n(N=3,034) \nLixisenatide \n(N=3,034) \nHazard ratio \n(95% CI) \nPrimary CV endpoint 1.02 \n(0.89, 1.17) \n No. of patients with event (%) 399 (13.2%) 406 (13.4%)"}, "primary_4p_text": {"offset": 63374, "span": "By the end of the study, there were 805 MACE+ events, 406 in \nthe lixisenatide group and 399 in the placebo group. The 95% confidence level for MACE+ is \n1.02 (0.89, 1.17)."}, "table8_onstudy_3p": {"offset": 47684, "span": "Table 8: Analysis of the MACE Endpoint \n Placebo \n(N=3,034) \nLixisenatide \n(N=3,034) \nHazard ratio \n(95% CI) \nMACE endpoint (on-study) 1.02 \n(0.89, 1.18) \n No. of patients with event (%) 392 (12.9%) 400 (13.2%)"}, "table8_ontreatment_3p": {"offset": 47957, "span": "MACE endpoint (on-treatment) 1.01 \n(0.87, 1.17) \n No. of patients with event (%) 342 (11.3%) 334 (11.0%)"}, "text_unrounded_3p": {"offset": 47274, "span": "For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \n1.172) with a point estimate of 1.02."}}, "definition_span": "MACE, defined as cardiovascular death, non-fatal \nMI, and non-fatal stroke", "design": {"effect_admissibility": {"definition_span": "MACE, defined as cardiovascular death, non-fatal \nMI, and non-fatal stroke", "effect_measure": "HR", "inputs": {"ai": null, "ci": null, "ci_high": 1.172, "ci_low": 0.887, "effect": 1.02, "n1i": null, "n2i": null}, "permitted": false, "reason": "axis 9: HR differs from target RR; no valid declared coercion", "result_span": "For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \n1.172) with a point estimate of 1.02.", "source": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.", "verdict": "INCOMPATIBLE"}}, "document_path": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf", "document_ref": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf", "document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38", "effect": 1.02, "effect_type_id": "effect-type:c5c8ce198a61cd20c2f653f7ab458a01eb4fa05ed21f99c70bd4c6d76db1bcc0", "extracted_text": "outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt", "extracted_text_sha256": "952b8088e14b457d97364f13bb0f9407803bf875faed5fa30d995972e2687a26", "id": "PMID 99999999", "intercurrent_events": "UNRESOLVED", "label": "SYNTHETIC-AUD1B", "outcome": "3-point major adverse cardiovascular events", "override": true, "pooled": false, "reason": "axis 9: HR differs from target RR; no valid declared coercion", "result_span": "For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \n1.172) with a point estimate of 1.02.", "retrieved_utc": "2026-09-16T18:33:00Z", "scale": "HR", "se_source": "derived_from_ci", "source": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.", "source_level": 2, "span": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.", "span_offset": 47847, "state": "EFFECT_TYPE_REFUSED", "status": "EFFECT_TYPE_REFUSED", "trial": "Sensitivity value: SYNTHETIC-AUD1B", "unification": {"axis": 9, "axis_name": "effect_measure", "reason": "axis 9: HR differs from target RR; no valid declared coercion", "status": "REFUSE"}}}
{"html": "<table class='arms'><tr><th>Trial</th><th>Id</th><th>Input</th><th>Source</th></tr><tr><td colspan=\"4\"><p><span data-claim-id=\"fact-b197ca04c0c42c76\" data-claim-class=\"UNVERIFIED_FACT\"><strong>[UNVERIFIED_FACT]</strong> PMID 99999999: HR 0.5 (0.3, 0.8).</span></p><p><span data-claim-id=\"page-c15e5cb2c81452d740f8\" data-claim-class=\"UNVERIFIED_FACT\"><strong>[UNVERIFIED_FACT]</strong> PMID 99999999: document None; SHA-256 None; retrieved None; located span: None</span></p><p><span data-claim-id=\"page-936c8ccf1bfb81a38220\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> design: {\"adjustment_axis\":{\"status\":\"UNRESOLVED\"},\"adjustment_status\":\"UNRESOLVED\",\"basis\":[{\"source\":\"trial reported estimate label\",\"span\":\"HR 0.50 (95% CI 0.30-0.80\"}],\"correlation_handling\":{\"evidence\":[],\"method\":\"none\"},\"design\":\"UNKNOWN\",\"design_action\":{\"action\":\"DESIGN_UNPROVEN\",\"decision_state\":\"design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify\",\"gate_id\":\"design-key:design-unproven\",\"reason\":\"no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL\",\"validity_critical\":false},\"effect_admissibility\":{\"component_distance\":0,\"definition_span\":\"The primary outcome was 3-point MACE.\",\"effect_measure\":\"HR\",\"extra_components\":[],\"inputs\":{\"ai\":null,\"ci\":null,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"n1i\":null,\"n2i\":null},\"missing_components\":[],\"permitted\":true,\"result_span\":\"The primary outcome had HR 0.50 (95% CI 0.30-0.80).\",\"source\":\"The primary outcome was 3-point MACE. The primary outcome had HR 0.50 (95% CI 0.30-0.80).\",\"target_components\":[\"cardiovascular death\",\"myocardial infarction\",\"stroke\"],\"target_endpoint_class\":\"EXACT_TARGET\",\"verdict\":\"EXACT\"},\"estimator_source\":\"PUBLISHED_HR\",\"published_alternative\":{\"adjusted\":false,\"ci_high\":0.8,\"ci_low\":0.3,\"effect\":0.5,\"scale\":\"HR\",\"span\":\"HR 0.50 (95% CI 0.30-0.80\"},\"se_provenance\":\"synth.Study.yi_vi:reported-effect-ci\",\"unit_of_randomisation\":\"UNKNOWN\"} [adjudication: OWED]</span></p><p><span data-claim-id=\"page-74915ffc2fb2ffc2c961\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> derivation: reported [adjudication: OWED]</span></p><p><span data-claim-id=\"page-bce00d6f0fbb0c82e719\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> selection_rule: KEEP_REPORTED_EFFECT [adjudication: OWED]</span></p><p><span data-claim-id=\"page-98df306278d4f9e219b6\" data-claim-class=\"JUDGEMENT\"><strong>[JUDGEMENT]</strong> alternatives: [{\"derivation\":\"alternative co-primary\",\"not_selected_reason\":\"UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE\",\"state\":\"EFFECT_TYPE_REFUSED\"}] [adjudication: OWED]</span></p></td></tr></table>", "plant": "alternative_valid_main", "refused": [], "result": {"Q": 0.0, "ci_high": 0.8, "ci_low": 0.3, "ci_note": "k=1: point estimate and 95% CI are the single trial's reported values, verbatim.", "ci_provenance": "source-reported-CI:k=1-verbatim", "co_primary_sensitivities": [{"alternative": null, "pool": {"k": 0, "present": false, "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "refused": [{"absent_kind": "refused_on_evidence", "admissibility": {"definition_span": "", "effect_measure": "RR", "inputs": {"ai": null, "ci": null, "ci_high": 0.2, "ci_low": 0.1, "effect": 0.123456, "n1i": null, "n2i": null}, "permitted": false, "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "result_span": "", "source": "", "verdict": "INCOMPATIBLE"}, "ci_high": 0.2, "ci_low": 0.1, "definition_span": "", "design": {"effect_admissibility": {"definition_span": "", "effect_measure": "RR", "inputs": {"ai": null, "ci": null, "ci_high": 0.2, "ci_low": 0.1, "effect": 0.123456, "n1i": null, "n2i": null}, "permitted": false, "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "result_span": "", "source": "", "verdict": "INCOMPATIBLE"}}, "effect": 0.123456, "effect_type_id": "effect-type:f9df8869c71b6e89ac2d6576e7b125c528d28f2624faa61b5ccd1522cde61026", "id": "PMID 99999999", "intercurrent_events": "UNRESOLVED", "label": "SYNTHETIC-AUD1", "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "result_span": "", "scale": "RR", "se_source": "derived_from_ci", "source": "", "state": "EFFECT_TYPE_REFUSED", "unification": {"axis": 9, "axis_name": "effect_measure", "reason": "UNTYPED — axis 9 unknown: NO_ROW_EVIDENCE", "status": "UNKNOWN_FAILS_CLOSED"}}], "state": "EFFECT_TYPE_REFUSED"}, "rule": "alternative prespecified co-primary endpoint sensitivity", "selected": null, "trial": "SYNTHETIC-AUD1"}], "estimate": 0.5, "estmeasure": {"canonicals": ["HAZARD_RATIO_FIRST_EVENT"], "classes": ["FIRST_EVENT_RATIO"], "labels": ["HR"], "status": "homogeneous"}, "k": 1, "leave_one_out": {"note": "not assessable at k=1 (leave-one-out needs k>=3)"}, "pi_note": "prediction interval undefined for k=1", "scale": "HR"}}
```
