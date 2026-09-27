# Continuous corpus fixture

Served reviews and held records are pinned to `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`.
Current working-tree topic declarations and harness functions are used; their behavior is frozen by fixture equality.
Source hashes and the complete review/outcome inventory are in `continuous_corpus.json`.

## Static versus dynamic disclosure

| Input | Status |
|---|---|
| Commit, MD/SMD selection rule, README comparison claims | Static, explicit |
| Synthetic `__control_` values | Invented test inputs only; excluded from every total |
| Review membership, IDs, registry arms, abstracts, verified arms | Read from pinned git objects |
| Topic combine rules, CI declarations, analysis plans | Read from current topic files; SHA-256 recorded |
| Extractor, typed arms, model states, CI procedures, counts | Recomputed with current harness |

## Coverage and interpretation

Scanned 32 reviews, all outcomes. Selected 3 continuous outcomes and 19 included trial–outcome items.
Membership is checked against each review's included screening records; ABSENT is outcome-level extraction status, not trial exclusion.
Served title recovery requires a unique source-title prefix plus raw means/SDs; denominators are deliberately not part of that match.
Absent rows use the title selected by the current extractor. No title is guessed when selection fails.
Registry extraction success is not full pipeline admission. The k comparison checks the registry combination and held override corroboration, not a rebuild or release verdict.
CI procedures are recorded per registry analysis, with held abstracts and declarations kept separate. No analysis means the CI property is unevaluable.
The pipeline emits continuous_analysis only for declared plans with continuous trials; this census evaluates every selected outcome regardless of that display gate.

## Totals

`fires` counts true observations; `of` retains unevaluable items. Unknown is not a negative finding.

| Property | fires | of (N) | Denominator | Unevaluable |
|---|---:|---:|---|---:|
| registry_measure_evaluable | 9 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| wrapper_returns_any_without_rule | 9 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| wrapper_returns_any_with_rule | 9 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| continuous_extracts_without_rule | 8 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| continuous_extracts_with_rule | 9 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| wrapper_noncontinuous_fallback | 1 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| combine_rule_rescues | 1 | 19 | all included continuous trial-outcome items; unevaluable retained | 10 |
| class_n_differs | 2 | 19 | all included continuous trial-outcome items; unevaluable retained | 10 |
| non_sd_dispersion | 0 | 19 | all included continuous trial-outcome items; unevaluable retained | 10 |
| flexible_ci | 2 | 19 | all included continuous trial-outcome items; unevaluable retained | 10 |
| model_based_admitted | 2 | 19 | all included continuous trial-outcome items; unevaluable retained | 10 |
| hand_override_corroborated | 1 | 19 | all included continuous trial-outcome items; unevaluable retained | 0 |
| served_continuous | 6 | 19 | all included continuous trial-outcome items | 0 |
| served_class_n_differs | 2 | 6 | served continuous rows only; unevaluable retained | 0 |
| served_effect_ci_path | 0 | 6 | served continuous rows only | 0 |
| esketamine_model_admitted | 2 | 4 | all included esketamine continuous items, including served ABSENT | 0 |
| analysis_plan_DECLARED | 0 | 3 | continuous outcomes, not trials | 0 |
| analysis_plan_MISSING_DATA_ASSUMPTION_NOT_DECLARED | 1 | 3 | continuous outcomes, not trials | 0 |
| analysis_plan_PRIMARY_ANALYSIS_NOT_DECLARED | 2 | 3 | continuous outcomes, not trials | 0 |

## Unevaluable items

- `melatonin-primary-insomnia-sol::0::PMID 33157425`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `melatonin-primary-insomnia-sol::0::PMID 22346363`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `melatonin-primary-insomnia-sol::0::PMID 27559258`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `melatonin-primary-insomnia-sol::0::PMID 19584739`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `melatonin-primary-insomnia-sol::0::PMID 18036082`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `melatonin-primary-insomnia-sol::0::PMID 17875243`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `melatonin-primary-insomnia-sol::0::PMID 12790159`: NO_REGISTRY_ID; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `semaglutide-obesity-weight::0::PMID 42070571`: NO_HELD_REGISTRY_RESULTS; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `semaglutide-obesity-weight::0::NCT07731256`: NO_HELD_REGISTRY_RESULTS; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.
- `semaglutide-obesity-weight::0::NCT06390501`: NO_HELD_REGISTRY_RESULTS; properties: combine_rule_rescues, class_n_differs, non_sd_dispersion, flexible_ci, model_based_admitted.

## README comparison

| Claim | README | Observed | Agreement |
|---|---|---|---|
| served continuous rows | 6 | 6 | yes |
| served rows with class-level n mismatch | {"fires": 2, "of": 6} | {"fires": 2, "of": 6} | yes |
| TRANSFORM-1 k before -> after registry/override corroboration | [3, 4] | [3, 4] | yes |
| esketamine model-based admitted | {"fires": 2, "of": 4} | {"fires": 2, "of": 4} | yes |
| served continuous effect+CI path | {"fires": 0, "of": 6} | {"fires": 0, "of": 6} | yes |

### Extractor scope finding

The README multi-arm refusal is correct for `_extract_ctgov_continuous`, but must not be generalized to the broad `extract_ctgov` call.
The fixture records both APIs. Broad non-continuous fallbacks are excluded from continuous-extraction counts.
- `esketamine-trd-madrs::0::NCT02417064`: without a rule the continuous measure is refused, but the wrapper returns PERCENTAGE: Percentage of Participants Who Achieved at Least 50% Reduction From Baseline in MADRS Total Score at Day 28 of Double-blind Induction Phase (Observed Data).

No disagreements with the listed README counts.
This comparison does not validate README pooled-effect/CI estimates, binary-row claims, or historical builds.
