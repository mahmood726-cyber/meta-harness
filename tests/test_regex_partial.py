"""R4 partial-number detection (regex_layer.partial): a group that reads a fragment of a digit-grouped number is found,
and the refusing wrapper is identical to the original pattern wherever nothing is partial."""
from __future__ import annotations

import pytest

from harness import extract
from regex_layer.partial import RefusePartial, partial_groups
from regex_layer.specs import SPECS

GROUPED = [
    ("_ARM", "in 48 488 (98.1%) of 49 419 participants"),   # thin space
    ("_ARM", "in 1,234 (5.0%) of 24,680 patients"),                   # comma
    ("_ARMP", "compared to 1,211 patients (12.0%)"),
    ("_NEQ", "trials (n = 2,523 patients)"),
    ("_NEQ", "(n=13 125) were included"),                        # nbsp
]
CLEAN = [
    ("_ARM", "Death occurred in 20 (9%) of 220 patients."),
    ("_ARMP", "compared to 211 patients (12.0%)"),
    ("_NEQ", "(n = 2523) and (n = 400)"),
    ("_EFFECT", "HR 0.80 (95% CI 0.70, 0.90)"),                          # ', 0.90' is a list, not a grouped number
]


@pytest.mark.parametrize("name,s", GROUPED)
def test_a_fragment_of_a_grouped_number_is_found(name, s):
    assert partial_groups(name, s), f"{name} read a fragment of {s!r} and it was not flagged"


@pytest.mark.parametrize("name,s", GROUPED)
def test_the_refusing_wrapper_never_returns_the_fragment(name, s):
    frags = {h["value"] for h in partial_groups(name, s)}
    w = RefusePartial(getattr(extract, name))
    for m in w.finditer(extract._norm(s)):
        assert not frags & set(g for g in m.groups() if g), m.groups()


@pytest.mark.parametrize("name,s", CLEAN)
def test_clean_text_is_untouched(name, s):
    rx = getattr(extract, name)
    w = RefusePartial(rx)
    assert partial_groups(name, s) == []
    assert w.findall(s) == rx.findall(s)
    assert [m.span() for m in w.finditer(s)] == [m.span() for m in rx.finditer(s)]
    assert (w.search(s) and w.search(s).span()) == (rx.search(s) and rx.search(s).span())


def test_every_extractor_is_covered_by_the_scan():
    from regex_layer import partial
    src = open(partial.__file__, encoding="utf-8").read()
    assert 'SPECS.items() if s["kind"] == "extractor"' in src
    assert sum(1 for s in SPECS.values() if s["kind"] == "extractor") == 14


@pytest.mark.parametrize("name,s", [
    ("_RATE_EVPT", "occurred in 136 participants (22.7%; 7.3 events per 100 person-years)"),   # '3' out of '7.3'
])
def test_a_fragment_of_a_decimal_is_found(name, s):
    # plant #16: found by R2 (_RATE_EVPT precision 0 of 28) -- the thousands-only detector passed it
    assert any(h["value"] == "3" for h in partial_groups(name, s)), partial_groups(name, s)
