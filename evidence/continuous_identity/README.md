# Continuous-outcome identity -- esketamine review f5b8f4cb (NOT for landing without Mahmood's signature)

External review of `esketamine-trd-madrs`, 2026-09-27. Branch `oc/v101-continuous-identity`, from `oc/v101-effect-identity`
(e11c7613, which carries the typed CI). Served state read at the pinned candidate 3876a62d.

## 1. Typed fields (`harness/continuous_identity.py`)

`typed_measure(om)` types every number in a registry outcome measure without converting any of them:

| field | TRANSFORM-2 (NCT02418585) |
|---|---|
| arm mean change / arm SD / kind | -21.4 / 12.32 / SD; -17.0 / 13.88 / SD (raw arm means) |
| n observed at Day 28 vs n in the analysis set | 101 / 100 (FAS 114 / 109 is the analysis set, not these rows' n) |
| raw difference vs adjusted | raw -4.4; MMRM LS-mean difference -4.0 |
| SE of the difference vs arm SD | SE of the difference **1.69** (the registry analysis); arm SDs 12.32 / 13.88 |
| CI procedure | 95% two-sided, standard (TRANSFORM-2's "flexible doses" is dosing, not an interval procedure) |

The rules, with a plant for each in `tests/test_continuous_identity.py`:

- `arm_sd` raises `NotAnArmSD` for anything that is not an SD. **An SE is never an arm SD**: TRANSFORM-2's 1.69 offered as
  an arm SD is refused, and a registry measure whose dispersion is labelled SE is refused by the extractor.
- `se_from_ci` gives CI width / (2 z) **only** for a `STANDARD_FIXED_LEVEL_TWO_SIDED` interval.
- `ci_procedure` returns `STAGE_WEIGHTED_FLEXIBLE` when the trial's held text names the procedure, or when the topic
  declares it with a source.
  - TRANSFORM-3's held abstract (PMID 31734084): "the median-unbiased estimate of the treatment difference (95% CI) was
    -3.6 (-7.20, 0.07); weighted combination test". The registry calls the same interval "95% TWO_SIDED", and that
    label does not override the held procedure.
  - TRANSFORM-1's stage-weighted procedure is in the EMA footnote the review cites. That footnote is **not held**, so it
    is a declaration in the topic with its source, not a held fact.

## 2. Combined doses (`combine_eligible_doses`)

- **Without a rule**, the multi-arm guard in `ctgov_results` refuses TRANSFORM-1 (56 mg, 84 mg, placebo), as before.
- **With the declared rule**, `combined_contrast`:
  - combines every experimental arm the rule names (Cochrane 6.5.2.10: pooled mean; the SD includes the between-arm
    spread) against the one placebo, **counted once** (209 + 108 = 317 participants);
  - refuses rather than drops an experimental arm the rule does not name.
- **Result from the held registry arms:** -19.0 (SD 13.86, n=111) and -18.8 (SD 14.12, n=98) give **-18.9062
  (SD 13.9491, n=209)**, against placebo -14.8 (SD 15.07, n=108).
- **Where the rule sits in the pipeline.** Previously the hand override in `verified_arms.json` (-18.91 / 13.95 / 209)
  won the precedence, and its computed tuple is in no held document, so the hand binder correctly abstained and
  TRANSFORM-1 was set aside. Now, when the rule is declared and the registry reproduces the override (within 0.01), the
  row is the registry's, and the override is recorded as `hand_override_corroborated`.
- **Status of the rule:** declared 2026-09-27, AFTER registration, so it is not demonstrably prospective. The TRANSFORM-1
  paper calls the combination post hoc. Both facts are on the page.

**The served move (a notice):** k 3 -> 4. MD **-3.1004 (-7.3323 to 1.1315) -> -3.3436 (-6.0691 to -0.6180)**; the
interval stops including 0.

- The review's diagnostic -3.342 (-6.068 to -0.616) reproduces exactly from the paper's rounded Table 4 inputs (-18.9,
  13.95, 209). The held registry arms give -3.344 (-6.069 to -0.618).
- `tests/test_continuous_multiarm.py` records that k = 4 was served until 2026-09-20. The hand-binding gate then set
  TRANSFORM-1 aside, so this restores it through a held source.
- TRANSFORM-1 enters as `UNBOUND_LEGACY`, like the other three esketamine rows. Under the fail-closed UNBOUND_LEGACY option
  the whole pool withdraws. That decision is separate and still Mahmood's.

## 3. Primary vs sensitivity (`analysis_plan`)

- **Primary** (registered protocol, quoted in the topic): raw per-arm mean/SD, "never a least-squares mean with a standard
  error", observed at Day 28 within the FAS.
- **Missing-data assumption: NOT DECLARED.** The protocol does not state one, and the page says so
  (`MISSING_DATA_ASSUMPTION_NOT_DECLARED`). An observed-case analysis is valid only under ignorable missingness. Stating
  the assumption is a protocol amendment, and Mahmood's to make.
- **Model-based sensitivity** (reported adjusted differences; SE only from a stated SE or a standard CI):

| trial | state |
|---|---|
| 37025256 (NCT03434041) | ADMITTED: -2.0, SE 1.324 from a standard 95% two-sided CI |
| TRANSFORM-2 | ADMITTED: -4.0, stated SE 1.69 |
| TRANSFORM-3 | SE_NOT_ESTABLISHED: stage-weighted CI |
| TRANSFORM-1 | PER_DOSE_ADJUSTED_ONLY: no combined adjusted difference is reported, and none is constructed |

  Pooled k=2: -2.76 (-16.00 to 10.48). That is correct under PM + HKSJ with t on 1 df, and it says little.
- `synth` gained an additive effect+CI path for MD/SMD. Before this, an MD given as effect+CI fell into the log branch.
  0 of 6 served MD rows use it, so no served number moves from that change.

## 4. n observed vs n in the analysis set -- corpus finding (Codex census, verified here)

A registry class can carry its **own** denominators. STEP 1 (NCT03548935) serves the class "In-trial observation period"
mean/SD (-15.6, 10.1 vs -2.8, 6.5), whose n is **1212/577**, with the measure-level FAS n **1306/655**. That understates the
SE. `_extract_ctgov_continuous` now uses the class-level n and keeps the measure-level n as `n_analysis_set`.

- **2 of 6** served continuous rows are affected, both semaglutide: STEP 1 1306/655 -> 1212/577; STEP 3 407/204 -> 373/189.
- **0** binary rows are affected. The one other class-level mismatch among the 13 served registry rows is FOURIER, an HR
  row whose n is unused.
- Rebuilt: the semaglutide pooled MD moves -11.8449 -> -11.8523. Its CI is suppressed on the page in both builds, a
  pre-existing state not caused here. **A notice.**

## Builds (`scripts/build_topic.py`, e11c7613 with and without this branch's files)

| topic | before | after |
|---|---|---|
| esketamine-trd-madrs | k 3, -3.1004 (-7.3323 to 1.1315) | k 4, -3.3436 (-6.0691 to -0.6180) |
| semaglutide-obesity-weight | k 2, -11.8449, n 407/204 and 1306/655 | k 2, -11.8523, n 373/189 and 1212/577 |
| melatonin-primary-insomnia-sol | unchanged | unchanged |

Tests: `tests/test_continuous_identity.py` passes 13 of 13. Across the ctgov, continuous, synth and effect-identity suites
79 pass. The 2 failures (`test_continuous_multiarm.py`) read `docs/`, which is not in this sparse tree.
