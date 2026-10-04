"""Registry binding for an effect ESTIMAND (dpp4 TECOS / EXAMINE): a posted analysis on the protocol's measure between
two groups with a two-sided CI binds without arm counts; a one-sided bound is refused as such; a per-protocol analysis
set or an extended composite ('MACE Plus') is a different estimand, never hidden behind the counts gate."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

SPEC, POP = "3-point major adverse cardiovascular events", "intention-to-treat"
KW = ["major adverse cardiovascular events", "MACE"]
TECOS_ITT = {"param_type": "Hazard Ratio (HR)", "param_value": "0.99", "ci_lower": "0.89", "ci_upper": "1.1",
             "groups": ["839356419", "839356420"]}
EXAMINE = {"param_type": "Hazard Ratio (HR)", "param_value": "0.962", "ci_lower": "", "ci_upper": "1.16",
           "groups": ["837533186", "837533187"]}


def _v(title, an):
    return gt.binding_verdict(SPEC, KW, title, 0, analysis=an, estimand="HR", population=POP)


def test_a_two_sided_posted_hr_binds_without_counts():
    v = _v("Percentage of Participants With First Confirmed CV Event of MACE (Intent to Treat Population)", TECOS_ITT)
    assert v["verdict"] == "BINDABLE" and v["basis"] == "POSTED_EFFECT_ON_PROTOCOL_ESTIMAND"


def test_a_one_sided_bound_is_refused_as_such():
    v = _v("Percentage of Participants With Primary Major Adverse Cardiac Events (MACE)", EXAMINE)
    assert v["verdict"] == "REFUSED" and "one-sided bound only" in v["reason"]


def test_per_protocol_and_extended_composites_are_other_estimands():
    assert _v("First Confirmed CV Event of MACE (Per Protocol Population)", TECOS_ITT)["gate"] == "ESTIMAND"
    assert _v("First Confirmed CV Event of MACE Plus (Intent to Treat Population)", TECOS_ITT)["gate"] == "ESTIMAND"


def test_another_measure_or_no_analysis_keeps_the_counts_rule():
    assert _v("MACE (Intent to Treat Population)", dict(TECOS_ITT, param_type="Odds Ratio (OR)"))["gate"] == "ARMS"
    assert _v("MACE (Intent to Treat Population)", None)["reason"] == "fewer than two result groups with people-unit counts"


def test_first_and_recurrent_events_are_not_time_to_first():
    v = gt.binding_verdict("Hospitalization for heart failure", ["hospitalisation for heart failure", "HHF"],
                           "Occurrence of Adjudicated Hospitalisation for Heart Failure (HHF) (First and Recurrent)", 0,
                           analysis=dict(TECOS_ITT, param_value="0.70", ci_lower="0.58", ci_upper="0.85"),
                           estimand="HR", population=POP)
    assert v["gate"] == "ESTIMAND" and "recurrent" in v["reason"]
