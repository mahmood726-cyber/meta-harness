# Melatonin continuous rules (2026-09-27) -- RETROSPECTIVE, decided by Dispatch under Mahmood's delegation (NOT landed)

Branch `oc/v101-melatonin-continuous`, from the V1.0.1 candidate stack (c15ed111). Rules (1), (2), (3) and (5) are here. Rule (4),
continuous sign orientation in the ordered-contrast rules, is on `oc/cx-contrast-sign`.

## Served now (3876a62d)

Primary "Sleep-onset latency": **MD -17.4 (-28.52 to -6.28), k 1**, from Wade 2010 (PMID 20712869, NCT00397189). The input is
the registry measure "The Change From Baseline in Subjective Sleep Latency", whose population is the "Pre-planned analysis on ITT
population age 65-80" (137 vs 144). Protocol line 26 made that subgroup the pooled input.

## (1) Population default

- `population_default: FULL_ELIGIBLE` (topic, retrospective). A subgroup is a separate analysis, never the primary input, and
  never pooled as independent of its own trial.
- `continuous_identity.population_class` reads the subgroup from the row's own population statement or the topic annotation.
- **The full-population values the review cites are not held.** The all-adult diary MD -6.70 (-13.63 to +0.23), the 55-80
  -9.90 and the PSQI -11.2 appear in no held melatonin file: not records.json, ft_20712869.txt, the snapshots, or any cache
  file. Wade's held full text (Table 3) reports only low excretors (-0.6) and ages 65-80 (raw -19.1 vs -1.7; adjusted -15.6).
- So the primary is **not held**. It is not filled from the review's text; the -6.70 enters once its source document is
  added to the cache.
- **Served move (a notice):**
  - The primary goes from -17.4 to **no pooled number**, with the reason "the held inputs are SUBGROUPS (20712869: age
    65-80 ITT subgroup) and the question is the full eligible population; the full-population result is not in the held
    sources".
  - Wade is listed as `FULL_POPULATION_INPUT_NOT_HELD`.
  - The 65-80 result is shown as a separate subgroup analysis.

## (2) Measurement class

- `measurement_classes.separate_by_class` (topic, retrospective). `measurement_class` reads PSG, DIARY, QUESTIONNAIRE or
  ACTIGRAPHY from the words the source uses for THIS number. It is never inferred from the outcome's name.
- Wade's registry title alone says only "Subjective" (SUBJECTIVE_UNSPECIFIED). Its analysis says "as measured by the sleep
  diary", so it is DIARY.
- Mixed classes with no declared primary class: every class is a separate analysis and the primary is refused. With a
  declared class, only that class is primary. The choice is never made on the more favourable number (plant: diary -6.7 vs
  PSQI -11.2).
- **No primary class is declared.** The decision did not name one.

## (3) Crossover

- `crossover_state`: a crossover (registry intervention_model CROSSOVER, or held text such as "received, in random order") given
  as per-arm mean/SD is refused as `CROSSOVER_PAIRED_VARIANCE_REQUIRED`. A paired difference with its SD or SE is admitted.
- Almeida Montes (PMID 12790159, 10 people, placebo / 0.3 mg / 1 mg) is a crossover by its held abstract. It holds no
  sleep-onset numbers, so it stays absent for that reason; the guard stops a future per-arm entry.

## (5) Raw vs adjusted

- Wade's registry analysis is an ANCOVA ("linear regression model with terms for treatment ... and baseline sleep latency"),
  **-15.6 (-25.3 to -6.0)**. It is now typed ADJUSTED_DIFFERENCE on its method and description, not only on "LS mean".
- The analysis's "STANDARD_DEVIATION 47" is never used as an SE; the SE (4.92) comes from the standard 95% CI.
- The subgroup analysis shows raw -17.4 and adjusted -15.6 side by side, never merged.

## Also fixed here

- `consumer_consistency.annotate_review` re-labelled any absent row with a visible source value as "extraction debt". That
  would have told the reader Wade was "not yet extracted" when it was excluded by rule. Decided exclusions now keep their own
  code and record the visible value.
- The absence layer preserves the two new codes.

## Checks

- **Builds** on c15ed111 with these files: melatonin as above; esketamine and semaglutide unchanged.
- **Tests:** `tests/test_continuous_melatonin_rules.py` (16) and `tests/test_continuous_identity.py` (15) pass.
- **Guard removal:** no subgroup detection turns 2 tests red; crossover never detected turns 1 red.
