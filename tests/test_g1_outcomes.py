"""D10 inventory R1 (regex over held comparator text): the phrasings seen in the 12 comparators, 7 Oct."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_outcomes as go  # noqa: E402


def _one(text):
    hits, _ = go.regex_inventory(text)
    return [(h["family"], h["estimate"], h["lower"], h["upper"]) for h in hits]


def test_lancet_middle_dot_and_bracketed_abbreviation():
    t = "Thromboembolic events occurred (pooled odds ratio [OR] 0·96 [95% CI 0·65–1·41]; low-quality evidence)."
    assert _one(t) == [("HARM", "0.96", "0.65", "1.41")]
    hits, _ = go.regex_inventory(t)
    assert "0·96" in hits[0]["span"]                      # the span is the ORIGINAL text


def test_pdf_equals_glyph_and_ci_without_95():
    assert _one("more cases of drug withdrawals (RR ¼1.85, 95% CI 1.04 to 3.29, p for effect 0.04).") == \
        [("HARM", "1.85", "1.04", "3.29")]
    assert _one("this primary outcome showed a tendency to favor DOACs (OR 0.88, CI 0.75–1.03).") == \
        [("OTHER", "0.88", "0.75", "1.03")]


def test_spelled_measure_with_parenthesised_abbreviations():
    t = "DOAC recipients had a lower risk of stroke [Pooled Odds Ratio (OR) 0.76, 95% Confidence Interval (CI) (0.68–0.84)]."
    assert _one(t) == [("OTHER", "0.76", "0.68", "0.84")]


def test_all_cause_mortality_family():
    assert _one("the two groups did not differ in death from any cause (OR 0.94, 95% CI 0.79-1.12).") == \
        [("ALL_CAUSE_MORTALITY", "0.94", "0.79", "1.12")]
