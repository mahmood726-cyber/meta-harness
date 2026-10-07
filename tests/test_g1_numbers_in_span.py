"""Plants (codex binding-v8-fe3ed2a7, reproduced on the binding branch): numbers_in_span accepted a REVERSED SIGN and
PERCENTAGES AS COUNTS; it gates typed_comparator_rows and the no-rows adoption."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402


def test_a_reversed_sign_is_refused():
    assert not gt.numbers_in_span({"effect": "1.7"}, "Mean difference: -1.7", ("effect",))
    assert gt.numbers_in_span({"effect": "-1.7"}, "Mean difference: -1.7", ("effect",))


def test_a_range_dash_is_not_a_minus():
    assert gt.numbers_in_span({"effect": "0.85", "lower": "0.80", "upper": "1.01"}, "RR 0.85 (0.80-1.01)",
                              ("effect", "lower", "upper"))


def test_percentages_are_not_counts():
    row = {"events_t": 10, "n_t": 200, "events_c": 20, "n_c": 200}
    assert not gt.numbers_in_span(row, "Treatment: N=200, deaths 10%; Control: N=200, deaths 20%.",
                                  ("events_t", "n_t", "events_c", "n_c"))
    assert gt.numbers_in_span(row, "Treatment: 10/200 deaths; Control: 20/200 deaths.", ("events_t", "n_t", "events_c", "n_c"))


def test_a_percent_effect_still_matches_a_non_count_field():
    assert gt.numbers_in_span({"effect": "-12.4"}, "weight change -12.4% vs placebo", ("effect",))


def test_codex_re_review_v8_p0_fixes():
    # g1#1: 'percent' / 'per cent' is a percentage too, never a count
    row = {"events_t": 10, "n_t": 200, "events_c": 20, "n_c": 200}
    assert not gt.numbers_in_span(row, "N=200, 10 percent died; N=200, 20 per cent died", ("events_t", "n_t", "events_c", "n_c"))
    # g1#4: a spaced range dash is not a minus; a dash after ':' is a sign
    assert gt.numbers_in_span({"effect": "0.85", "lower": "0.80", "upper": "1.01"}, "RR 0.85 (0.80 - 1.01)",
                              ("effect", "lower", "upper"))
    assert not gt.numbers_in_span({"effect": "1.7"}, "difference: -1.7", ("effect",))
    # a leading decimal is 0.85, never 85
    assert gt.numbers_in_span({"effect": "0.85"}, "RR .85", ("effect",))
    assert not gt.numbers_in_span({"effect": "85"}, "RR .85", ("effect",))
