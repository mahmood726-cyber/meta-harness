"""R4: harness/whole_numbers.py refuses a match that reads a fragment of a number; extract.py's in-module extractors
are wrapped with it. Plants for each fragment kind, and proof that clean text is untouched."""
from __future__ import annotations

import re

import pytest

from harness import extract
from harness.whole_numbers import WholeNumbers, fragment_groups, whole_numbers

FRAGMENTS = [
    ("_NEQ", "trials (n = 2,523 patients)"),                       # grouped (thin space + comma)
    ("_NEQ", "median n = 12.5 per arm"),                                    # decimal: 12 read out of 12.5
    ("_ARMP", "compared to 1,211 patients (12.0%)"),                        # grouped (comma)
    ("_RATE_EVPT", "7.3 events per 100 person-years"),                      # decimal
    ("_ARM", "in 48 488 (98.1%) of 49 419 participants"),         # grouped (thin space)
]
CLEAN = [
    ("_NEQ", "(n = 2523) and (n = 40)"),
    ("_ARM", "Death occurred in 20 (9%) of 220 patients."),
    ("_ARMP", "compared to 211 patients (12.0%)"),
]


@pytest.mark.parametrize("name,s", FRAGMENTS)
def test_a_fragment_is_refused_by_the_served_pattern(name, s):
    rx = getattr(extract, name)
    assert isinstance(rx, WholeNumbers), f"{name} is not wrapped"
    raw = [m for m in rx.rx.finditer(s) if fragment_groups(m)]
    assert raw, f"plant does not contain a fragment for {name}: {s!r}"           # the plant can fire
    assert not any(fragment_groups(m) for m in rx.finditer(s))                    # the served pattern refuses it


@pytest.mark.parametrize("name,s", CLEAN)
def test_clean_text_reads_exactly_as_before(name, s):
    rx = getattr(extract, name)
    assert [m.span() for m in rx.finditer(s)] == [m.span() for m in rx.rx.finditer(s)]
    assert rx.findall(s) == rx.rx.findall(s)


def test_effect_is_left_unwrapped_because_other_modules_read_it():
    assert isinstance(extract._EFFECT, re.Pattern)


def test_the_measurement_and_the_harness_share_one_definition():
    from regex_layer import partial
    assert partial.fragment_groups is fragment_groups or partial.fragment_groups.__module__ == "harness.whole_numbers"


def test_wrapper_findall_shapes_match_re():
    rx = re.compile(r"(\d+)-(\d+)")
    assert whole_numbers(rx).findall("1-2 and 3-4") == rx.findall("1-2 and 3-4")
    one = re.compile(r"n=(\d+)")
    assert whole_numbers(one).findall("n=1 n=2") == ["1", "2"]
