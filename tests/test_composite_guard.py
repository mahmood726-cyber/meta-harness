"""Composite-containment guard: when the declared outcome is SINGLE, a number pulled from a
COMPOSITE-endpoint sentence is the wrong endpoint and is skipped (FAIR-HF2 class). A
composite-declared topic keeps the guard OFF."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.extract import extract_trial, declared_is_composite, _names_composite  # noqa: E402

FAIRHF2 = ("The first primary outcome, cardiovascular death or first heart failure hospitalization, "
           "occurred in 141 vs 166 (hazard ratio, 0.79 [95% CI, 0.63-0.99]). The second primary "
           "outcome, total heart failure hospitalizations, occurred 264 times vs 320 times "
           "(rate ratio, 0.80 [95% CI, 0.60-1.06]).")
KW = ["heart failure hospitalization", "heart failure hospitalisation", "hospitalization for heart failure"]
INTERV = ["ferric carboxymaltose", "iron"]
COMP = ["placebo"]


def test_declared_is_composite_classifier():
    assert declared_is_composite("Composite cardiovascular death or hospitalisation for heart failure")
    assert declared_is_composite("3-point major adverse cardiovascular events")
    assert not declared_is_composite("Heart-failure hospitalization")
    assert not declared_is_composite("All-cause mortality")


def test_names_composite_detector():
    assert _names_composite("cardiovascular death or first heart failure hospitalization")
    assert _names_composite("the composite of death or MI")
    assert not _names_composite("12.5% died (hazard ratio, 0.76)")  # spironolactone EMPHASIS, must NOT trip


def test_single_outcome_skips_composite_sentence_and_takes_the_single_one():
    # declared single => the composite HR 0.79 sentence is skipped; the total-HF-hosp rate ratio is taken
    ex = extract_trial(FAIRHF2, KW, INTERV, COMP, declared_composite=False)
    assert not ex.get("absent"), ex
    # 0.80 is the total-HF-hospitalizations number, NOT the composite 0.79
    assert ex.get("effect") == 0.80 or ex.get("effect") == 0.8


def test_composite_declared_keeps_the_composite():
    ex = extract_trial(FAIRHF2, KW, INTERV, COMP, declared_composite=True)
    assert not ex.get("absent")
    assert ex.get("effect") in (0.79,)  # first matching sentence, composite allowed
