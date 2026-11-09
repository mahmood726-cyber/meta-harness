# Lane L7 — one confirmed review finding in harness/extract.py (plant FIRST)

A recorded Claude Sonnet second review of A7 part 1 found, and the coverage lane CONFIRMED by execution:
`_RATIO_LABEL` (used by `_RATIO_VALUE` and `_NEXT_ESTIMATE`) is compiled with re.I, so its abbreviation alternatives
match ordinary lowercase words: the conjunction "or" is read as the OR label. In
`reported_vs_count_derived((20,100,30,100), ("RR",0.50,0.30,0.80), s, s)` with
`s = "Mortality: RR 0.50 (95% CI 0.30-0.80) for death or transplant, adjusted for age."` the reported value's clause is cut
at "or", so "adjusted" is never seen and an adjusted estimate becomes a false TERMINAL refusal (it should return None).

Fix it the way `_EFFECT` already does (see its comment: "(?-i:\bRR\b)", "(?-i:\bOR\b)"): the ABBREVIATIONS RR / OR / HR / IRR
match CASE-SENSITIVELY; the full words (relative risk, odds ratio, hazard ratio, rate ratio, risk ratio) stay
case-insensitive. Keep `_LABEL_SCALE` lookups working (they lowercase the matched label).

## Do
1. Add to `tests/test_reported_vs_derived.py`: the input above must return None (SEE IT FAIL first); also
   `extract._reported_occurrence(0.5, "the rate of death or 0.5 per year; RR 0.50", "RR")[0] == "0.50"` style check that a
   lowercase "or" before a number is not a label; and that "OR 0.25 (95% CI ...)" and "odds ratio 0.25" are still labels.
2. Fix harness/extract.py only (the `_RATIO_LABEL` pattern). Then run
   `python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py tests/test_a7_oracle.py tests/test_regex_plants.py tests/test_regex_inventory.py`
   -- all must pass. If the regex inventory reports a changed site key, update regex_layer/specs.py so the SAME plants
   are keyed to the new site (do not delete plants) and say so in the report.
3. Do not touch any other file. No network.

## Finish condition / artefact
`LANE_REPORT.md` (plant, failing output, fix, passing output, any spec key moves) and `lane.patch`. Do not commit/push.
