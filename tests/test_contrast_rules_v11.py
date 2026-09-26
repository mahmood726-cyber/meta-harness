"""Two ordered-contrast rule gaps found by the cross-topic census (evidence/v11_contrast_census on oc/v11-tag-strip), fixed in BOTH
implementations (the verifier's stdlib copy and scripts/contrast_order.py). Each case uses a synthetic clause built from the served
wording, so no corpus edit can move its answer. Each case is also run against the PRE-FIX verifier (blob at 23642e0d), where it must
give the old wrong verdict: a plant that never fired proves nothing.

  1. The rate witness read only "%". RALES writes "386 deaths in the placebo group (46 percent) and 284 in the spironolactone group
     (35 percent; relative risk of death, 0.70 ...)". ORDER_OF_MENTION puts placebo in the numerator; the unread rates (46 vs 35,
     crude 1.31 against an estimate of 0.70) contradict that. Before the fix it was ORDERED with placebo as numerator (served as
     REVERSED); after the fix it is UNORDERED, failing closed. It is NOT promoted to PROVEN: order of mention was wrong, and no rule
     here orders it the other way.
  2. "-treated" was excluded as a non-arm suffix, so "ticagrelor- and clopidogrel-treated patients" lost clopidogrel. The second
     half of a suspended hyphen is now an arm. A plain "metformin-treated patients" (background therapy) is still not an arm."""
import importlib.util
import os
import subprocess
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import verify_bundle as vb          # noqa: E402
import contrast_order as co          # noqa: E402

PRE_FIX = "23642e0d"


def _pre_fix():
    src = subprocess.run(["git", "show", f"{PRE_FIX}:scripts/verify_bundle.py"], cwd=ROOT, capture_output=True, check=True).stdout
    d = tempfile.mkdtemp()
    p = os.path.join(d, "vb_prefix.py")
    open(p, "wb").write(src)
    spec = importlib.util.spec_from_file_location("vb_prefix", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


RALES = ("There were 386 deaths in the placebo group (46 percent) and 284 in the spironolactone group (35 percent; relative risk "
         "of death, 0.70; 95 percent confidence interval, 0.60 to 0.82; P<0.001)")
RALES_VOCAB = {"experimental": ["spironolactone"], "reference": ["placebo"]}
TICA = ("The primary end point occurred in 9.0% and 6.3% of ticagrelor- and clopidogrel-treated patients, respectively "
        "(HR 1.47; 95% CI 1.05-2.07)")
TICA_VOCAB = {"experimental": ["ticagrelor"], "reference": ["clopidogrel"]}
BACKGROUND = ("In metformin-treated patients, sitagliptin reduced HbA1c; hazard ratio 0.98 (95% CI 0.89-1.08)")
BG_VOCAB = {"experimental": ["sitagliptin"], "reference": ["metformin"]}


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
def test_percent_word_is_a_rate_and_contradicts_order_of_mention(impl):
    oc = impl.ordered_contrast(RALES, [0.70, 0.60, 0.82], RALES_VOCAB, None)
    assert oc["state"] == "UNORDERED"
    assert oc["rate_witness"]["state"] == "CONTRADICTS"
    assert oc["rate_witness"]["rates"] == {"numerator": 46.0, "reference": 35.0}


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
def test_suspended_hyphen_names_both_arms(impl):
    oc = impl.ordered_contrast(TICA, [1.47, 1.05, 2.07], TICA_VOCAB, None)
    assert oc["state"] == "ORDERED" and oc["numerator_side"] == "EXPERIMENTAL"
    assert oc["direction_witness"]["rule"] == "ORDER_OF_MENTION"
    assert oc["reference_arm"]["term"] == "clopidogrel"


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
def test_background_therapy_treated_is_still_not_an_arm(impl):
    assert [m[3] for m in impl.arm_mentions(BACKGROUND, BG_VOCAB)] == ["sitagliptin"]
    assert impl.ordered_contrast(BACKGROUND, [0.98, 0.89, 1.08], BG_VOCAB, None)["state"] == "UNORDERED"


def test_plants_fire_against_the_pre_fix_verifier():
    old = _pre_fix()
    r = old.ordered_contrast(RALES, [0.70, 0.60, 0.82], RALES_VOCAB, None)
    assert r["state"] == "ORDERED" and r["numerator_side"] == "REFERENCE"       # the served-census REVERSED
    t = old.ordered_contrast(TICA, [1.47, 1.05, 2.07], TICA_VOCAB, None)
    assert t["state"] == "UNORDERED"                                            # clopidogrel never seen


def test_rules_span_identical_in_both_implementations():
    for name in ("_PCT", "_NOT_AN_ARM", "_SUSPENDED_HYPHEN"):
        assert getattr(vb, name).pattern == getattr(co, name).pattern and getattr(vb, name).flags == getattr(co, name).flags
