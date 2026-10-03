# NOAC same-trials result: second instrument (Codex lane G1NOACST, gpt-5.5) vs the first (harness/g1_noac.py)

The lane was told not to read `harness/g1_noac.py` or `outputs/g1_noac/g1_noac.json`, so it computed its numbers
blind to these. Its outputs are held in the lane clone. They are NOT integrated, because its input selection has the
defect named below.

## Pooled results

| Outcome | First instrument (this branch) | Second instrument | Comparator COMBINE AF |
|---|---|---|---|
| Stroke/SE | k=4, HR 0.804 (0.652-0.992) RE | k=4, HR 0.761 (0.649-0.891) RE | 0.81 (0.74-0.89) |
| Major bleeding | k=4, HR 0.854 (0.644-1.134) RE | k=2, HR 0.982 (0.483-1.997) RE | 0.86 (0.74-1.01) |

## Why they differ: the second instrument's population typing

The comparator's efficacy population is intention-to-treat. That is its own methods sentence:
"Efficacy outcomes were assessed using an intention-to-treat population".

The second instrument "matched" population by comparing raw text strings, not typed populations. It selected these
stroke/SE inputs:

| Trial | Second instrument used | ITT tuple that exists |
|---|---|---|
| ROCKET AF | AACT per-protocol HR 0.79 | the ITT HR 0.88 (0.74-1.03) |
| ENGAGE AF-TIMI 48 | abstract on-treatment HR 0.79 | the ITT HR 0.87 (99% CI 0.709-1.068 -> 95% 0.744-1.017) |
| RE-LY | AACT ITT HR 0.65 | (it used the ITT tuple) |
| ARISTOTLE | abstract HR 0.79 | (population unstated; the AACT ITT tuple is identical) |

Mixing per-protocol and on-treatment estimates into an ITT comparison pulls the pool towards 0.76.

For major bleeding it found only the two FDA tuples. It missed the posted AACT HRs for ARISTOTLE (0.69) and ENGAGE
(0.80), hence k=2.

## What the second instrument does confirm

- Both instruments agree with COMBINE AF on stroke/SE under the tracker rule.
- The RE-LY AACT tuple is HR 0.65 (0.52-0.81).
- The RE-LY and ROCKET FDA bleeding HRs are 0.93 and 1.04.
- The divergence is entirely input selection: the population axis. The first instrument types that axis, and the
  plants `test_same_trials_selection_and_ci_level_plants` and `test_population_never_matches_and_base_does_match`
  hold it.
