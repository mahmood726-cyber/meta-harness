"""Timepoints (pass 16; codex P16c + age guard): decimals and years are read; a stated follow-up duration meets a trial-end claim,
not a fixed-time claim; an unstated time never meets a trial-end claim; an age is never a timepoint."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from harness.evidence_identity import _timepoint_in, leading_timepoint, timepoint_of


@pytest.mark.parametrize("number,unit", [("26.2", "months"), ("2.3", "years"), ("1.5", "days"), ("2.5", "hours")])
def test_decimal_fixed_assessment(number, unit):
    sentence = f"At {number} {unit}, the outcome was assessed."
    expected = f"{number} {unit}"
    assert timepoint_of(sentence) == expected
    assert leading_timepoint(sentence) == expected
    assert _timepoint_in(expected, expected)
    assert not _timepoint_in(f"{number.split('.')[-1]} {unit}", expected)


@pytest.mark.parametrize("phrase,expected", [
    ("Over a median of 26.2 months", "follow-up: 26.2 months"),
    ("Over a median of 2.3 years", "follow-up: 2.3 years"),
    ("During a mean follow-up of 7.4 years", "follow-up: 7.4 years"),
    ("after a median follow-up of 26 months", "follow-up: 26 months"),
    ("During a median follow-up 26.2 months", "follow-up: 26.2 months"),
])
def test_followup_duration_is_distinct_and_leading(phrase, expected):
    sentence = phrase + ", the primary outcome occurred."
    assert timepoint_of(sentence) == expected
    assert leading_timepoint(sentence) == expected


def test_bare_median_years():
    assert timepoint_of("a median of 2.3 years") == "follow-up: 2.3 years"


@pytest.mark.parametrize("claim", [
    "trial end", "study end", "longest reported trial follow-up",
    "end of study", "end of the trial", "end of follow-up",
])
def test_stated_followup_meets_terminal_claim(claim):
    assert _timepoint_in(claim, timepoint_of("Over a median of 2.3 years, the primary outcome occurred."))


@pytest.mark.parametrize("claim", ["28 days", "12 months", "26 months", "2.3 years", "trial end at 12 months"])
def test_followup_never_substitutes_for_fixed_time(claim):
    assert not _timepoint_in(claim, "follow-up: 26 months")
    assert not _timepoint_in(claim, "follow-up: 2.3 years")


def test_no_stated_time_does_not_meet_terminal_claim():
    assert timepoint_of("The primary outcome occurred.") is None
    assert not _timepoint_in("trial end", timepoint_of("The primary outcome occurred."))


def test_fixed_years_do_not_become_terminal_followup():
    assert timepoint_of("5-year Kaplan-Meier estimate") == "5 years"
    assert not _timepoint_in("longest reported trial follow-up", "5 years")


def test_all_qualifiers_must_fit_and_later_followup_does_not_lead():
    assert not _timepoint_in("trial end", "follow-up: 26 months; 12 months")
    assert leading_timepoint("The outcome occurred after a median follow-up of 26 months.") is None


def test_decimal_day_range():
    assert _timepoint_in("1.2-1.8 days", "1.5 days")
    assert not _timepoint_in("1.2-1.8 days", "2 days")


@pytest.mark.parametrize("text", ["Among 38 patients (median age 68 years; 66% women) 37 completed",
                                  "patients aged 70 years or older", "a 68 years old man"])
def test_PLANT_an_age_is_never_a_timepoint(text):
    assert timepoint_of(text) is None


def test_a_time_in_years_is_still_a_timepoint():
    assert timepoint_of("at 5 years, 12 deaths had occurred") == "5 years"
