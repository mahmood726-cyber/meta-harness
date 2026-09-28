# Semaglutide-weight review: denominators, estimand label, model-based primary, comparison-level screening

Rule hash `e209c1d5`, 2026-09-28. **RETROSPECTIVE, decided by Dispatch under Mahmood's delegation.** Branch
`oc/v101-semaglutide` off candidate stack `c15ed111`, with `oc/cx-step8-comparison` merged in. Nothing is landed; every
served move below is a notice for Mahmood's hash-bound signature. The topic protocol carries a dated amendment
(`protocols/semaglutide-obesity-weight.md`, "Amendment 2026-09-28"). The original text is not rewritten.

## What the held sources contain (read before building)

| Trial | Held source | Figure |
|---|---|---|
| STEP 1 NCT03548935 | registry results analysis, "Treatment policy estimand", ANCOVA | -12.44 (-13.37 to -11.51) |
| STEP 1 | registry results analysis, "Hypothetical estimand", ANCOVA | -14.42 (-15.29 to -13.55) (not used) |
| STEP 1 | abstract 33567185 | -12.4 (-13.4 to -11.5), rounded |
| STEP 3 NCT03611582 | registry results analysis, "Treatment policy estimand", ANCOVA | -10.27 (-11.97 to -8.57) |
| STEP 3 | abstract 33625476 | -10.3 (-12.0 to -8.6), rounded |
| STEP 8 NCT04074161 | registry primary: semaglutide vs **liraglutide** only | -9.38 (-11.97 to -6.80), ANCOVA |
| STEP 8 | registry secondary: semaglutide vs **pooled** placebo, raw observed | -16.4 (SD 10.5, n=117) vs -1.6 (SD 8.6, n=78) |

- **STEP 3.** The review quoted -10.3 (-12.0 to -8.6). That is the abstract's rounding of the same analysis. The registry
  value is used so that both trials come from one source.
- **STEP 8 figures not held.** No held source has the matched-placebo comparison or the model-based pooled-placebo
  -13.9 (-16.7 to -11.0). The STEP 8 publication is not in the corpus.
- **The review's diagnostic is therefore not served.** The 3-trial model-based -12.04 (-16.24 to -7.84) reproduces
  exactly from those three figures (PM tau^2 2.02, HKSJ on t(2)), but it needs the -13.9, which is not held. Adding the STEP 8
  publication to the corpus is Mahmood's decision.

## (1) Denominators

The registry "in-trial observation period" class carries its own n: STEP 1 1,212/577 under a full analysis set of
1,306/655; STEP 3 373/189 under 407/204. The candidate stack already used the class n (one of its 31 moves). New here:

- `continuous_identity.observed_contribution`. OBSERVED when the measure says the analysed number is participants with
  available data. IMPUTED when it names imputation; such a row is held as `IMPUTED_SUMMARY_METHOD_NOT_ESTABLISHED`.
  NOT_ESTABLISHED otherwise. A full-analysis-set heading never establishes observed contribution.
- **Census (held data, 38 topics):** 918 mean-type registry measures: 315 OBSERVED, 109 IMPUTED (mostly denosumab
  LOCF bone-density measures), 494 NOT_ESTABLISHED. **0 served rows are held** by this rule (full rebuild).

## (2) Estimand label

A continuous input's label is derived from the analysis actually used:
- a raw observed row is "observed data ... not a treatment-policy estimate";
- a model-based row names the estimand its own registry analysis states;
- the page's "Analysis population" now shows that derived label.

The topic's population string no longer claims an estimand.

## (3) Primary = published model-based treatment-policy difference

- **Method.** Generic inverse variance, with the SE from the reported standard two-sided 95% CI and never used as an arm
  SD. Raw observed data is a labelled sensitivity analysis.
- **Estimand selection.** The registry reader now selects the analysis by the ESTIMAND it names. Two analyses on the same
  arms were previously misreported as "per dose", and an ANCOVA "Treatment difference" was untyped.

| | before (served stack) | after |
|---|---|---|
| primary | raw observed, k=2, MD -11.8523 (CI withheld, k=2) | model-based, k=2, MD **-11.4765** (CI withheld, k=2); common-effect -11.94 (-12.76 to -11.12) |
| sensitivity | none | raw observed, k=2, n 1,212/577 and 373/189 |

## (4) Comparison-level screening; pooled vs matched placebo

- **Screening.** STEP 8 (X2 for "liraglutide") is screened at comparison level and included with the contrast semaglutide
  vs Placebo (semaglutide). Codex slot 1 built this; I reviewed and corrected it on `oc/cx-step8-comparison`. It changes
  1 of 4,080 screening decisions.
- **Decision: matched, not pooled.** The pooled placebo includes the placebo matched to once-daily liraglutide, which is
  not blinded against once-weekly semaglutide. The two are alternatives: one trial never contributes both, and no placebo
  is counted twice.
- **What STEP 8 shows.** The held registry reports weight only against the pooled placebo. STEP 8 is named
  `POOLED_PLACEBO_NOT_THE_ELIGIBLE_CONTRAST`, with the pooled figure shown as supportive; it is in neither the primary nor
  the sensitivity.

## Defects found on the way (each fixed at its source)

- **Comparator fallback took an active arm.** `ctgov_results._classify_arms` used "the other arm" as comparator whatever it
  was, so STEP 8's semaglutide-vs-liraglutide measure became a semaglutide-vs-placebo row with liraglutide as placebo.
  Across held 2-arm registry measures, the fallback assigned the comparator in 161 of 1,208, mostly active agents
  (liraglutide, valsartan, ASA 100 mg, vitamin D doses, quetiapine, semaglutide itself). It now fills the comparator only
  with an arm that reads as a control. **0 served numbers move** elsewhere (full rebuild). The intervention-side fallback
  is unchanged and is not audited here.
- **Unit.** STEP 8's kilogram measure matched "body weight" before its percent measure. The outcome now declares
  `unit_class: PERCENT`, and a kilogram measure is not this outcome. Only a declaring topic is gated.
- **Measure of an effect-based MD.** It was decided in two duplicated helpers (pipeline, rob_sensitivity), and both sent it
  down the log-ratio path. There is now one `estmeasure.row_measure`; behaviour for every other row is unchanged.
- **Typed refusal overwritten.** `consumer_consistency` re-labelled the refusal as `KNOWN_REPORTED_NOT_YET_EXTRACTED` with
  boilerplate because its value is visible. Decided exclusions now keep their own code and reason: the same
  `_DECIDED_EXCLUSIONS` structure as the melatonin branch, extended.

- **The continuous-analysis page block had no limitation object** (a stack defect from the continuous-identity branch). Any
  rebuilt continuous page (esketamine on c15ed111 itself; semaglutide here) failed the legacy page/object comparison.
  `limitations.build_limitations` now registers it, rendered by the page's own function so the two cannot drift.
- **`evidence/fixtures/derived_label_corpus.json`** pins the topic file's hash. It was regenerated, and exactly one line
  changed (that hash); every derived label in the fixture is identical.

## Served moves (full 32-topic rebuild against a c15ed111 baseline)

- **semaglutide-obesity-weight primary:** MD -11.8523 -> -11.4765 (k=2 both); inputs change from raw rows to model-based
  differences. **NOTICE.**
- **semaglutide-obesity-weight screening:** STEP 8 X2 -> include; named absent in the primary
  (POOLED_PLACEBO_NOT_THE_ELIGIBLE_CONTRAST) and in GI adverse events (SOURCE_NOT_RETRIEVED). **NOTICE.**
- **Analysis-population label (served text):** semaglutide (see (2)); esketamine "not shown for 4 of 4 inputs" -> "raw
  per-arm mean/SD as reported; whether the n is observed or imputed is not established". **NOTICE.**
- **No other topic moves.** The baseline's corticosteroids-COVID SAE difference is the pcsk9 branch's known move, not this
  branch.
