"""The pre-triage's local check decides whether a model's BIND stands. It must reject a span not in the bytes shown and
any number not in the span (a reader's inferred or computed number is never a binding)."""
import os
import sys

sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")]
import m2_pretriage as t  # noqa: E402

SRC = "TITLE: X\nABSTRACT: Death at 90 days occurred in 530 of 2433 patients (21.8%) and 530 of 2413 (22.0%); HR 0.99 (95% CI, 0.89 to 1.10)."


def test_a_verbatim_span_with_its_own_numbers_binds():
    ok, _ = t.check_bind({"decision": "BIND", "span": "HR 0.99 (95% CI, 0.89 to 1.10)",
                          "numbers": {"effect": 0.99, "ci_low": 0.89, "ci_high": 1.1}}, SRC)
    assert ok


def test_a_span_not_in_the_source_shown_never_binds():
    ok, why = t.check_bind({"decision": "BIND", "span": "HR 0.98 (95% CI, 0.89 to 1.10)", "numbers": {}}, SRC)
    assert not ok and "span" in why


def test_a_number_not_in_the_span_never_binds():
    ok, why = t.check_bind({"decision": "BIND", "span": "HR 0.99 (95% CI, 0.89 to 1.10)",
                            "numbers": {"effect": 0.99, "ci_low": 0.88, "ci_high": 1.1}}, SRC)
    assert not ok and "ci_low" in why


def test_a_refuse_is_not_a_bind():
    assert not t.check_bind({"decision": "REFUSE", "span": "", "numbers": {}}, SRC)[0]


# ---------------------------------------------------------------- codex / agy m2pre-cap-r1 (each failed on d9367bded)
import pytest  # noqa: E402

_N = dict.fromkeys(["effect", "ci_low", "ci_high", "measure", "events_t", "n_t", "events_c", "n_c"])


def test_PLANT_a_bind_with_no_numbers_is_not_a_bind():
    assert not t.check_bind({"decision": "BIND", "span": "Death occurred in", "numbers": dict(_N)}, SRC)[0]


def test_PLANT_signs_and_leading_dot_decimals_are_read():
    s = "TITLE: x\nABSTRACT: mean difference -0.5 (95% CI -1.2 to 0.2); hazard ratio was .75 (95% CI .60 to .95)."
    assert t.check_bind({"decision": "BIND", "span": "mean difference -0.5 (95% CI -1.2 to 0.2)",
                         "numbers": dict(_N, effect=-0.5, ci_low=-1.2, ci_high=0.2)}, s)[0]
    assert not t.check_bind({"decision": "BIND", "span": "mean difference -0.5 (95% CI -1.2 to 0.2)",
                             "numbers": dict(_N, effect=0.5, ci_low=-1.2, ci_high=0.2)}, s)[0]
    assert t.check_bind({"decision": "BIND", "span": "hazard ratio was .75 (95% CI .60 to .95)",
                         "numbers": dict(_N, effect=0.75, ci_low=0.6, ci_high=0.95)}, s)[0]


def test_PLANT_a_percentage_is_never_an_event_count():
    s = "TITLE: x\nABSTRACT: Kaplan-Meier mortality was 12% versus 8%."
    assert not t.check_bind({"decision": "BIND", "span": "Kaplan-Meier mortality was 12% versus 8%.",
                             "numbers": dict(_N, events_t=12, events_c=8)}, s)[0]


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex m2pre-cap-r1 #2): arm denominators from different analysis "
                                       "populations inside one span are not detected; the human signer sees the span")
def test_known_limit_mixed_population_denominators():
    s = "Randomised: treatment 100, control 100. Safety population: treatment 90, control 80. Safety deaths: treatment 9, control 8."
    assert not t.check_bind({"decision": "BIND", "span": s, "numbers": dict(_N, events_t=9, n_t=100, events_c=8, n_c=80)},
                            "TITLE: x\nABSTRACT: " + s)[0]


# ---------------------------------------------------------------- codex / agy m2pre-cap-r2 (each failed on 74fe46beb)
def _b(span, **nums):
    return t.check_bind({"decision": "BIND", "span": span, "numbers": dict(_N, **nums)}, "TITLE: x\nABSTRACT: " + span)[0]


def test_PLANT_word_percent_and_percentage_ranges_are_not_counts():
    assert not _b("Kaplan-Meier mortality was 12 percent in treatment and 8 percent in control", events_t=12, events_c=8)
    assert not _b("mortality was 12-15%", events_t=12)


def test_PLANT_scientific_notation_and_unspaced_commas_are_not_split():
    assert not _b("Treatment deaths: 1e2 of 500; control deaths: 80 of 500.", events_t=2, n_t=500, events_c=80, n_c=500)
    assert not _b("grades 1,2 adverse events", events_t=12)
    assert _b("deaths 1,234 of 5,000 versus 1,100 of 5,001", events_t=1234, n_t=5000, events_c=1100, n_c=5001)


def test_PLANT_a_denominator_only_answer_is_not_a_bind():
    assert not _b("We randomized 100 patients per arm. Mortality results are not yet available.", n_t=100, n_c=100)


# ---------------------------------------------------------------- codex / agy m2pre-cap-r3 (the last round; failed on 90f56cc7a)
def test_PLANT_counts_are_whole_numbers_and_ranges_with_to_are_percentages():
    assert not _b("Kaplan-Meier mortality probability: treatment 0.12; control 0.15.", events_t=0.12, events_c=0.15)
    assert not _b("Mortality was 12 to 15% in the intervention arm", events_t=12)


def test_PLANT_signed_exponents_and_thousands_decimals():
    assert not _b("Hazard ratio 1e-2.", effect=2)
    assert not _b("Difference was significant at p < 1e-5 across all cohorts", events_t=5)
    assert _b("Mean difference 1,234.5.", effect=1234.5)
    assert not _b("Mean difference 1,234.5.", effect=0.5)


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex m2pre-cap-r3 #1): a percentage named only in a HEADING "
                                       "('Deaths (%): treatment 12') is read as a count; the signer sees the span")
def test_known_limit_percentage_heading():
    assert not _b("Deaths (%): treatment 12; control 15.", events_t=12, events_c=15)
