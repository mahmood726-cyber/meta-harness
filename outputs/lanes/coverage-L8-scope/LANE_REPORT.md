# L8 report — 15 October 2026

Implemented the scope restriction in LANE_PROMPT.md. No network, commit, or push.
Initial tracked worktree was clean; pre-existing untracked LANE_PROMPT.md and lane.log were left alone.

## Fix

- `_arm_ns(..., analysed_group_form=False)` excludes the analysed-group form by default. The conditional pattern keeps its original precedence when enabled.
- Only `percentage_implied_counts` opts in, with a comment explaining that it is a consistency check, not admission to pooling. Other existing callers retain the default.
- Added three synthetic scope plants in test_reported_vs_derived.py.
- Updated the held PICU assertion to test both opt-in and default behavior.
- Updated the extractor inventory expectation to 18 and recorded the coverage lane's supplied 15 Oct evidence: each of `_RATIO_VALUE`, `_NEXT_ESTIMATE`, `_PCT_PAIR` yielded 0 fragment groups in 35,673 held sentences, with 18 extractors scanned. This scan was not rerun here.

## Red then green

Command, before and after the implementation fix:

```text
python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py -k 'analysed_group_sizes or cocs_shaped'
```

Each plant's observed failing output:

```text
test_PLANT_analysed_group_sizes_are_not_extraction_denominators
E AssertionError: assert {'c': 127, 'i': 113} == {}

test_PLANT_analysed_group_sizes_are_available_only_by_opt_in
E TypeError: _arm_ns() got an unexpected keyword argument 'analysed_group_form'

test_PLANT_cocs_shaped_counts_are_not_newly_admitted
E AssertionError: {'ai': 21, 'ci': 39, 'n1i': 113, 'n2i': 127, ...}
E assert None is True

3 failed, 32 deselected in 2.44s
```

Passing output after the fix:

```text
... [100%]
3 passed, 32 deselected in 2.59s
```

The cache-independent subset of tests/test_a7_picu.py also passed:
`12 passed, 5 deselected in 4.18s`. The five deselected tests are listed below.
`git diff --check` passed.

## Unavailable checks

The clone has no cache/ directory. No records or fixtures were fabricated. These tests in tests/test_a7_picu.py could not be run against their required held records and were explicitly deselected:

- test_arm_sizes_stated_as_n_in_the_group_are_read
- test_the_extractor_admits_neither_picu_value
- test_percentages_and_arm_sizes_imply_counts_only_when_they_reproduce_the_printed_percentages
- test_PLANT_picu_reason_is_the_typed_disagreement_not_outcome_not_in_source
- test_PLACIDE_aad_and_cdd_counts_are_never_bound_to_aad

## Oracle mismatch

The requested suite exposes an existing caller in tests/test_a7_oracle.py: `oracle_percent` calls `_arm_ns` with the default. Its expected percentage counts therefore disappear when the requested default becomes False, whereas the production consistency check correctly opts in. Per the instruction that every other existing caller retains the default, this helper was not changed.

Diagnostic command: `python -m pytest -q -p no:cacheprovider tests/test_a7_oracle.py -x --tb=short`

```text
test_hand_stated_expectations[truncation]
tests/test_a7_oracle.py:238: assert oracle(case) == expected
E AssertionError: assert None == (3, 10, 5, 9)
1 failed, 30 passed in 6.16s
```

This is not a missing-cache failure. A green full-suite result is not claimed.

## Completed suite results

Requested command:

```text
python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py tests/test_a7_oracle.py tests/test_regex_partial.py tests/test_regex_plants.py tests/test_regex_inventory.py
561 failed, 4969 passed, 58 xfailed in 460.13s (0:07:40)
```

All 561 failure summary entries belong to tests/test_a7_oracle.py (percentage hand expectations and differential cases). There were no missing-cache errors in this command; the held-record PICU tests are in the separate file listed above. The unresolved oracle/default mismatch is the blocker to a green requested suite. Updating the oracle consistency helper to opt in would require relaxing the lane's explicit instruction to keep other existing callers at the default.

To isolate the non-oracle checks, ran:

```text
python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py tests/test_regex_partial.py tests/test_regex_plants.py tests/test_regex_inventory.py
2238 passed, 58 xfailed in 374.10s (0:06:14)
```

Final patch validation: `git apply --reverse --check lane.patch` and `git diff --check` both passed. The four-file diff was reviewed for caller scope and synthetic-data disclosure; no source-backed clinical claims were added. The requested held-corpus scan and full served-pool gates were not run without cache data.

## Static versus dynamic disclosure

| Item | Kind | Evidence / limitation |
| --- | --- | --- |
| New abstract text and counts | Static synthetic contract plants | Supplied by lane prompt; not clinical evidence |
| 18 extractor expectation | Static regression assertion | Checked against live SPECS by pytest |
| 35,673 sentences and zero fragments | Supplied historical evidence | Attributed to coverage lane, 15 Oct; not rerun locally |
| Plant and suite results | Dynamic | Actual local pytest output |
| PICU held-record values | Unverified locally | Required cache absent; tests listed above |

`lane.patch` contains only the four changed implementation/test files. No release or portfolio status is promoted.
