# Lane TY report

Base / HEAD: `f6f7b14c820bdadd258122ac0bb54c7e4d2a989a`. LANE_BASE.txt is absent; SHA matches the brief. No commit.

## Plants fired pre-fix

Command: `python -m pytest tests/test_effect_type.py -q --tb=short -p no:cacheprovider`

```text
FFFF                                                                     [100%]
================================== FAILURES ===================================
________________________ test_freedom_censoring_plant _________________________
tests\test_effect_type.py:28: in test_freedom_censoring_plant
    ty = api()
         ^^^^^
tests\test_effect_type.py:15: in api
    return importlib.import_module("harness.effect_type")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1324: in _find_and_load_unlocked
    ???
E   ModuleNotFoundError: No module named 'harness.effect_type'
____________________ test_elixa_components_coercion_plant _____________________
tests\test_effect_type.py:42: in test_elixa_components_coercion_plant
    ty = api()
         ^^^^^
tests\test_effect_type.py:15: in api
    return importlib.import_module("harness.effect_type")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1324: in _find_and_load_unlocked
    ???
E   ModuleNotFoundError: No module named 'harness.effect_type'
_________________________ test_unstated_binding_plant _________________________
tests\test_effect_type.py:58: in test_unstated_binding_plant
    ty = api()
         ^^^^^
tests\test_effect_type.py:15: in api
    return importlib.import_module("harness.effect_type")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1324: in _find_and_load_unlocked
    ???
E   ModuleNotFoundError: No module named 'harness.effect_type'
______________________ test_current_glp1_baseline_plant _______________________
tests\test_effect_type.py:76: in test_current_glp1_baseline_plant
    ty = api()
         ^^^^^
tests\test_effect_type.py:15: in api
    return importlib.import_module("harness.effect_type")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1324: in _find_and_load_unlocked
    ???
E   ModuleNotFoundError: No module named 'harness.effect_type'
=========================== short test summary info ===========================
FAILED tests/test_effect_type.py::test_freedom_censoring_plant - ModuleNotFou...
FAILED tests/test_effect_type.py::test_elixa_components_coercion_plant - Modu...
FAILED tests/test_effect_type.py::test_unstated_binding_plant - ModuleNotFoun...
FAILED tests/test_effect_type.py::test_current_glp1_baseline_plant - ModuleNo...
4 failed in 1.02s
```

## Implementation and scope

Implemented `harness/effect_type.py`, integrated typing after extraction and before pooling in `harness/pipeline.py`, added gate re-unification and a rendered twelve-axis table plus coercion register in `harness/page.py`. `harness/synth.py`, search, screening, protocol files, topic configs, and served review/page files were not edited. No network and no commit.

Each type is content-addressed, records its twelve axis bases, and leaves unsupported values UNKNOWN. Legacy protocol-inherited ITT/timepoint/model labels are deliberately not evidence. Component recognition does not silently turn unspecified MI/stroke fatality into nonfatal events. An HR never becomes RR merely because the legacy compatibility class groups them. Reconstructed measures are supported by an explicit engine rule, not an assumed default.

Schema: `docs/effect_type_schema.json`. External decisions are loaded from `cache/<slug>/coercions.json`, checked for required signed/cited fields, valid date, exact axis/from/to scope, optional effect-type scope and duplicate IDs. UNKNOWN cannot be coerced into known. No production coercion register or decision was authored; the only coercion is a clearly marked test fixture. `signed_by` is a required attestation field, not cryptographic signature verification.

Type artefacts: `cache/<slug>/effect_types.json` for all measured topics. These files are written for integrator review but intentionally uncommitted. `scripts/effect_type_sweep.py --write-types` writes the measurement and type files without rebuilding pages. Each topic measurement records input SHA-256 digests.

## Plants passing post-fix

The initial failures above are missing-module failures on the exact base, not a claim that old code already exposed the twelve-axis API. Post-fix plants exercise the held-source values and behavioral assertions; further tests exercise extraction ? typing ? membership/counts ? rendering, gate refusal, coercion validation, deterministic sweep and held FDA document hashes.

Command: `python -m pytest tests/test_effect_type.py -q --tb=short -p no:cacheprovider`

```text
..........                                                               [100%]
10 passed in 4.38s
```

## MEASURED: corpus before/after

N means candidate effect rows in currently served, non-suppressed pooled outcomes, across all outcomes (not unique trials). The before/after comparison holds source bytes constant: before = current served membership assessed with the new type builder; after = dry-run target unification. It is not a claim that pages were rebuilt or that missing evidence was acquired.

- Topics measured: 32 of 32 served topics.
- Fully typed before and after: 0 of 112 candidate rows.
- At least one UNKNOWN binding axis before and after: 85 of 112 candidate rows.
- Would be refused on rebuild: 94 of 112 candidate rows.
- Would match the compiled targets: 18 of 112 candidate rows.
- Served membership changed by this lane: 0 of 32 pages.

Per-topic before/after denominators and individual verdicts are in `docs/effect_type_sweep.json`. MATCH does not mean fully typed: nonbinding UNKNOWN axes remain disclosed.

## MEASURED: current GLP-1 primary pool

Names below are joined by PMID to the held reviewer extraction; all eight rows are the current served primary pool. UNKNOWN describes what this conservative adapter establishes today, not proof that no fuller source contains the field.

| Trial / source ID | Known axes of 12 | UNKNOWN axes |
|---|---:|---|
| PIONEER 6 / PMID 31185157 | 3 of 12 | population, randomised_contrast, analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator |
| SUSTAIN-6 / PMID 27633186 | 3 of 12 | population, randomised_contrast, analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator |
| LEADER / PMID 27295427 | 4 of 12 | population, randomised_contrast, analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| AMPLITUDE-O / PMID 34215025 | 3 of 12 | population, randomised_contrast, analysis_set, endpoint_components, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| REWIND / PMID 31189511 | 5 of 12 | population, randomised_contrast, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| Harmony Outcomes / PMID 30291013 | 4 of 12 | population, randomised_contrast, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator |
| EXSCEL / PMID 28910237 | 5 of 12 | population, randomised_contrast, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| SOUL / PMID 40162642 | 3 of 12 | population, randomised_contrast, analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator |

Axes 6 (time origin), 10 (adjustment) and 11 (estimator) are UNKNOWN for every current GLP-1 primary row; axis 7 (follow-up) is UNKNOWN where listed. They were not filled from memory, trial names or a requested estimand. The cohort currently served does not include the FREEDOM-CVO regulatory row; the FREEDOM plants assess the held candidate analyses separately.

FREEDOM evidence: `outputs/handover/glp1_regulatory/regulatory_sources_glp1.json` end-of-study row 1.24 versus `outputs/handover/glp1_reviewerB/reviewB_extraction.json` end-of-treatment row 1.36. Tests verify the FDA held PDF digest, extracted-text digest, both table headings and both effect/CI strings. The censoring-only B-prime plant matches the former and refuses the latter on axis 8. This isolated test does not claim either row is fully typed on all twelve axes.

ELIXA evidence: reviewer B's four-point primary is 1.02 [0.89, 1.17]. It refuses the three-component target on axis 4. The test-only signed decision allows the exact fixture mismatch and renders its citation. No clinical authorization is inferred from that test.

## Contract limits / cannot-build-today

- General API accepts explicit `effect_type_target` with any of the twelve binding axes. The legacy adapter compiles declared analysis set, exact effect scale and explicit canonical components; for primary outcomes it also recognizes the exact held B-prime amendment phrases for first event, components and censoring. Other prose is not a general natural-language protocol compiler. Population phenotype constraints and arm targets require explicit normalized target declarations from the integrator; absent declarations are not secretly made binding.
- Population and contrast can consume provenance-bearing axis fields or structured SC3 arm/population evidence. Contrast requires exactly two evidenced arms, one drug-of-interest occurrence and equal evidenced backgrounds. This lane does not create missing AACT arm joins or assert them from names. Current corpus evidence often cannot establish these axes.
- For held documents supplied via `report_source`, the builder computes and checks SHA-256. Abstract provenance uses the existing source-level hierarchy rule; no PDF digest is fabricated. Sparse or ambiguous source spans remain insufficient for row-level censoring, estimator or adjustment. Richer full-text adapters remain integrator follow-up work.
- The gate deliberately refuses existing pooled rows without attached type verdicts. Rebuilding under declared targets changes count chains through existing membership machinery; this lane did not migrate served pages. The result is implementation and measured coverage, not publication certification or an Overmind PASS.
- No coercion is proposed as authorized. If the integrator wants different binding policy or an equivalence such as on-study ? end-of-study, it must be declared with evidence rather than silently normalized here.

## Static-vs-dynamic hardcode disclosure

| Item | Static / dynamic | Basis and limit |
|---|---|---|
| Twelve-axis names, enums, verdict states, source-level map | Static contract | Lane brief and existing source hierarchy |
| Protocol adapter | Static rules over dynamic topic/protocol bytes | Exact declarations only; no broad policy inference |
| Component/analysis/follow-up recognition | Static literal rules over held row/abstract text | Conservative adapter coverage, not absence proof |
| Effects, CIs, identifiers, names, counts and known-axis totals | Dynamic | Held source/review JSON and replayable sweep; no invented study output |
| Coercion fixture | Static TEST-ONLY decision | Exercises validation/rendering, never written to a production register |
| Production coercions | External input only | Required signed/cited permanent records; lane authors none |

## Verification

First broader run: 90 passed, 4 failed. Failures identified legacy expectations that a missing-type served page passes and HR may enter an RR target, plus missing measure evidence for count reconstructions. The count path now cites its actual engine rule; two legacy assertions were updated to expect the required refusals. No served data were edited to make tests green.

Bounded regression command:
`python -m pytest tests/test_gate.py tests/test_gate_controls.py tests/test_page.py tests/test_effect_type.py tests/test_compat_key.py tests/test_compat_underlying.py tests/test_compat_direction.py tests/test_design_key.py tests/test_design_variance.py tests/test_target_endpoint.py tests/test_source_hierarchy.py -q --tb=short -p no:cacheprovider`

```text
........................................................................ [ 75%]
........................                                                 [100%]
96 passed in 56.84s
```

The final focused run above was repeated after coercion validation tightening. The renderer integration test is the equivalent UI contract: actual extraction, refusal, k=0, twelve cells and the required UNTYPED text; it also checks the accepted nonbinding path and forged-verdict rejection. No browser rendering or full portfolio release certification is claimed. `git diff --check` passes.
