# L7 lane report

Completed the scoped LANE_PROMPT.md task without network access, commit, or push.

## Plant and observed failure

Added regression plants to tests/test_reported_vs_derived.py before changing production code. The supplied mortality sentence must return None despite the conjunction 'or' before its trailing adjustment. A second plant checks both the requested RR occurrence and the actual label matches, since scale filtering already makes the requested RR occurrence assertion pass before the fix. Controls cover uppercase RR/OR/HR/IRR, rejected lowercase abbreviations, all five full-word labels across case variants, and OR scale lookup.

Pre-fix command:
```
python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py
```
Exit code: 1. Observed output (failure details and summary):
```
.............FFFFFF......                                         [100%]
================================== FAILURES ===================================
_________ test_PLANT_lowercase_or_does_not_hide_a_trailing_adjustment _________

    def test_PLANT_lowercase_or_does_not_hide_a_trailing_adjustment():
        s = "Mortality: RR 0.50 (95% CI 0.30-0.80) for death or transplant, adjusted for age."
        out = extract.reported_vs_count_derived((20, 100, 30, 100), ("RR", 0.50, 0.30, 0.80), s, s)
>       assert out is None, out
E       AssertionError: {'absent': True, 'count_derived': {'ai': 20, 'ci': 30, 'effect': 0.6666666666666667, 'n1i': 100, ...}, 'gross': False,...0/100 v 30/100 give RR 0.6667 -- beyond the reported value's rounding; neither value is pooled until adjudicated", ...}
E       assert {'absent': True, 'count_derived': {'ai': 20, 'ci': 30, 'effect': 0.6666666666666667, 'n1i': 100, ...}, 'gross': False,...0/100 v 30/100 give RR 0.6667 -- beyond the reported value's rounding; neither value is pooled until adjudicated", ...} is None

tests\test_reported_vs_derived.py:196: AssertionError
________ test_PLANT_lowercase_or_before_a_number_is_not_a_ratio_label _________

    def test_PLANT_lowercase_or_before_a_number_is_not_a_ratio_label():
        s = "the rate of death or 0.5 per year; RR 0.50"
        assert extract._reported_occurrence(0.5, s, "RR")[0] == "0.50"
>       assert [m.group(1) for m in extract._RATIO_VALUE.finditer(s)] == ["RR"]
E       AssertionError: assert ['or', 'RR'] == ['RR']
E         
E         At index 0 diff: 'or' != 'RR'
E         Left contains one more item: 'RR'
E         Use -v to get more diff

tests\test_reported_vs_derived.py:202: AssertionError
_____________ test_ratio_abbreviations_remain_case_sensitive[RR] ______________

label = 'RR'

    @pytest.mark.parametrize("label", ["RR", "OR", "HR", "IRR"])
    def test_ratio_abbreviations_remain_case_sensitive(label):
        assert extract._RATIO_VALUE.search(label + " 0.25 (95% CI 0.10-0.60)")
>       assert extract._RATIO_VALUE.search(label.lower() + " 0.25") is None
E       AssertionError: assert <re.Match object; span=(0, 7), match='rr 0.25'> is None
E        +  where <re.Match object; span=(0, 7), match='rr 0.25'> = <built-in method search of re.Pattern object at 0x000002215C909190>(('rr' + ' 0.25'))
E        +    where <built-in method search of re.Pattern object at 0x000002215C909190> = re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE).search
E        +      where re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE) = extract._RATIO_VALUE
E        +    and   'rr' = <built-in method lower of str object at 0x0000022160586550>()
E        +      where <built-in method lower of str object at 0x0000022160586550> = 'RR'.lower

tests\test_reported_vs_derived.py:208: AssertionError
_____________ test_ratio_abbreviations_remain_case_sensitive[OR] ______________

label = 'OR'

    @pytest.mark.parametrize("label", ["RR", "OR", "HR", "IRR"])
    def test_ratio_abbreviations_remain_case_sensitive(label):
        assert extract._RATIO_VALUE.search(label + " 0.25 (95% CI 0.10-0.60)")
>       assert extract._RATIO_VALUE.search(label.lower() + " 0.25") is None
E       AssertionError: assert <re.Match object; span=(0, 7), match='or 0.25'> is None
E        +  where <re.Match object; span=(0, 7), match='or 0.25'> = <built-in method search of re.Pattern object at 0x000002215C909190>(('or' + ' 0.25'))
E        +    where <built-in method search of re.Pattern object at 0x000002215C909190> = re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE).search
E        +      where re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE) = extract._RATIO_VALUE
E        +    and   'or' = <built-in method lower of str object at 0x000002215CA607E0>()
E        +      where <built-in method lower of str object at 0x000002215CA607E0> = 'OR'.lower

tests\test_reported_vs_derived.py:208: AssertionError
_____________ test_ratio_abbreviations_remain_case_sensitive[HR] ______________

label = 'HR'

    @pytest.mark.parametrize("label", ["RR", "OR", "HR", "IRR"])
    def test_ratio_abbreviations_remain_case_sensitive(label):
        assert extract._RATIO_VALUE.search(label + " 0.25 (95% CI 0.10-0.60)")
>       assert extract._RATIO_VALUE.search(label.lower() + " 0.25") is None
E       AssertionError: assert <re.Match object; span=(0, 7), match='hr 0.25'> is None
E        +  where <re.Match object; span=(0, 7), match='hr 0.25'> = <built-in method search of re.Pattern object at 0x000002215C909190>(('hr' + ' 0.25'))
E        +    where <built-in method search of re.Pattern object at 0x000002215C909190> = re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE).search
E        +      where re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE) = extract._RATIO_VALUE
E        +    and   'hr' = <built-in method lower of str object at 0x00000221605BA670>()
E        +      where <built-in method lower of str object at 0x00000221605BA670> = 'HR'.lower

tests\test_reported_vs_derived.py:208: AssertionError
_____________ test_ratio_abbreviations_remain_case_sensitive[IRR] _____________

label = 'IRR'

    @pytest.mark.parametrize("label", ["RR", "OR", "HR", "IRR"])
    def test_ratio_abbreviations_remain_case_sensitive(label):
        assert extract._RATIO_VALUE.search(label + " 0.25 (95% CI 0.10-0.60)")
>       assert extract._RATIO_VALUE.search(label.lower() + " 0.25") is None
E       AssertionError: assert <re.Match object; span=(0, 8), match='irr 0.25'> is None
E        +  where <re.Match object; span=(0, 8), match='irr 0.25'> = <built-in method search of re.Pattern object at 0x000002215C909190>(('irr' + ' 0.25'))
E        +    where <built-in method search of re.Pattern object at 0x000002215C909190> = re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE).search
E        +      where re.compile('\\b(RR|OR|HR|IRR|relative\\s+risk|risk\\s+ratio|odds\\s+ratio|hazard\\s+ratio|rate\\s+ratio)\\b[^\\d;().]{0,30}?(?<![\\d.])(\\d+(?:\\.\\d+)?|\\.\\d+)(?!\\d|\\.\\d)', re.IGNORECASE) = extract._RATIO_VALUE
E        +    and   'irr' = <built-in method lower of str object at 0x00000221605BA6D0>()
E        +      where <built-in method lower of str object at 0x00000221605BA6D0> = 'IRR'.lower

tests\test_reported_vs_derived.py:208: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_reported_vs_derived.py::test_PLANT_lowercase_or_does_not_hide_a_trailing_adjustment
FAILED tests/test_reported_vs_derived.py::test_PLANT_lowercase_or_before_a_number_is_not_a_ratio_label
FAILED tests/test_reported_vs_derived.py::test_ratio_abbreviations_remain_case_sensitive[RR]
FAILED tests/test_reported_vs_derived.py::test_ratio_abbreviations_remain_case_sensitive[OR]
FAILED tests/test_reported_vs_derived.py::test_ratio_abbreviations_remain_case_sensitive[HR]
FAILED tests/test_reported_vs_derived.py::test_ratio_abbreviations_remain_case_sensitive[IRR]
6 failed, 26 passed in 16.55s

```

## Fix

Only the _RATIO_LABEL pattern changed in harness/extract.py: its abbreviation branch is now `(?-i:RR|OR|HR|IRR)`. Full-word alternatives retain the consumers' re.I behavior; capture groups and _LABEL_SCALE lowercasing remain unchanged. Added a direct capture assertion to the full-word controls to ensure fallback numeric matching cannot make them pass vacuously.

## Passing verification

```
python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py tests/test_a7_oracle.py tests/test_regex_plants.py tests/test_regex_inventory.py
5511 passed, 58 xfailed in 338.83s (0:05:38)
```
Exit code: 0. Expected failures are reported separately from passes.

## Spec keys and scope

No spec keys moved: the regex inventory and existing plants passed unchanged. regex_layer/specs.py was not modified. lane.patch contains only the production pattern change and regression tests. Pre-existing untracked LANE_PROMPT.md and lane.log were left untouched.

| Item | Static or dynamic | Disclosure |
| --- | --- | --- |
| Regression inputs and expected behavior | Static | Constructed test fixtures, including the exact lane-provided sentence; not research findings. |
| Failure and passing results | Dynamic | Observed local pytest execution, with exit codes recorded above. |
| Regex alternatives | Static | Parser vocabulary required by the lane. |
