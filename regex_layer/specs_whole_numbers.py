"""Plants for harness/whole_numbers.py (R4 of the regex layer, owned by this lane). Each pattern looks at the two
characters before a captured number (head) or the five after it (tail) and says whether the capture is PART of a longer
number. The plants state that requirement; tests/test_whole_numbers.py holds the composed behaviour."""

SITE_SPECS: dict = {
    "whole_numbers.py:_GROUPED_BEFORE": {
        "kind": "search", "what": "fragment_groups: the head ends with a digit and a group separator ('48 ' before '488')",
        "plants": {"accept": [("8 ", None), ("1,", None), ("8 ", None)], "refuse": ["a ", "(", "8."]}},
    "whole_numbers.py:_GROUPED_AFTER": {
        "kind": "search", "what": "fragment_groups: the tail starts with a separator and exactly three digits (',523')",
        "plants": {"accept": [(",523 p", None), (" 419)", None)], "refuse": [", 52 ", ",5234", " and "]}},
    "whole_numbers.py:_DEC_BEFORE": {
        "kind": "search", "what": "fragment_groups: the head is a digit and a decimal point ('7.' before '3')",
        "plants": {"accept": [("7.", None)], "refuse": ["7 ", ". "]}},
    "whole_numbers.py:_DEC_AFTER": {
        "kind": "search", "what": "fragment_groups: the tail starts with a decimal point and a digit ('.92')",
        "plants": {"accept": [(".92 ", None)], "refuse": [". The", ", 9"]}},
    "whole_numbers.py:_DIGIT_BEFORE": {
        "kind": "search", "what": "fragment_groups: the head ends with a digit (a capture that starts mid-number)",
        "plants": {"accept": [("a1", None)], "refuse": ["a ", "1 "]}},
    "whole_numbers.py:_DIGIT_AFTER": {
        "kind": "search", "what": "fragment_groups: the tail starts with a digit (a capture that ends mid-number)",
        "plants": {"accept": [("3 pa", None)], "refuse": [" pat", ")"]}},
    "whole_numbers.py:_NUMBER": {
        "kind": "search", "what": "fragment_groups: only a numeric capture is judged (integer or decimal)",
        "plants": {"accept": [("12", None), ("7.3", None)], "refuse": ["placebo", "n = ."]}},
    "whole_numbers.py:fullmatch:10fde6660a": {
        "kind": "search", "what": "fragment_groups: a group after a separator is a thousands fragment only if it is 3 digits",
        "plants": {"accept": [("488", None)], "refuse": ["48", "4.8"]}},
}
