"""Regression tests for the negated-exclusion-term defect (melatonin cold audit, cycle 84):
lexical matching created a false EXCLUSION when an exclusion term appeared only in a NEGATED form
('no withdrawal effects', 'without diabetes'). The mirror of the false-inclusion class.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.screen import _has  # noqa: E402


def test_negated_exclusion_term_does_not_fire():
    # The exact melatonin/Lemoine title phrase: 'withdrawal' present only as 'no withdrawal effects'.
    title = ("Prolonged-release melatonin improves sleep quality and morning alertness in insomnia "
             "patients aged 55 years and older and has no withdrawal effects.")
    assert _has(title, ["withdrawal"]) is None
    assert _has("adults with obesity but without diabetes", ["diabetes"]) is None
    assert _has("with no dependence or rebound", ["dependence"]) is None  # cue adjacent (within window)


def test_negation_window_is_conservative():
    # The guard only suppresses when the negation cue is NEAR the term (~18 chars). A cue far away
    # (scoping over a long conjunction) is NOT treated as negation -- deliberately conservative so a
    # genuine excluded population is never silently let through.
    assert _has("no evidence of rebound insomnia or withdrawal effects", ["withdrawal"]) == "withdrawal"


def test_non_negated_exclusion_term_still_fires():
    # A genuine excluded population must STILL be caught (the guard must not over-suppress).
    assert _has("patients with benzodiazepine withdrawal insomnia", ["withdrawal"]) == "withdrawal"
    assert _has("adults with type 2 diabetes mellitus", ["diabetes"]) == "diabetes"
    assert _has("a randomized trial in children with insomnia", ["children"]) == "children"


def test_mixed_negated_and_plain_fires_on_the_plain_one():
    # If a term appears negated once AND plainly elsewhere, the plain occurrence must still exclude.
    txt = "no withdrawal effects were seen; however this was a benzodiazepine withdrawal population"
    assert _has(txt, ["withdrawal"]) == "withdrawal"
