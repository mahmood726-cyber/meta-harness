"""IRR-mistyping fix (audit 22): a bare "rate ratio" is a person-time / recurrent INCIDENCE-rate ratio ONLY
when the source carries an explicit recurrence/person-time footprint (an event count in "N times", a
per-person-time denominator, a total/recurrent-events phrasing). A "rate ratio" reported for a FIRST event or
mortality (one per person, no person-time) is a first-event relative ratio (FIRST_EVENT_RATIO class), NOT a
person-time IRR. Typing RECOVERY's "age-adjusted rate ratio" and ASCEND's "log-rank rate ratio" as IRR was
the mislabel that manufactured omega3's estimand-incompatibility. iv-iron's FAIR-HF2 ("total ... occurred 264
times") is a genuine recurrent rate ratio and must stay IRR."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # tests/ on the path for _contracts
from harness import extract


def _scale(sentence):
    e = extract.extract_effect(sentence)
    return e[0] if e else None


def test_recovery_first_event_rate_ratio_is_not_irr():
    s = ("Overall, 482 patients (22.9%) in the dexamethasone group and 1110 (25.7%) in the usual care group "
         "died within 28 days (age-adjusted rate ratio, 0.83; 95% confidence interval, 0.75 to 0.93).")
    assert _scale(s) == "RR", "a first-event mortality rate ratio must not be typed IRR"


def test_ascend_first_event_rate_ratio_is_not_irr():
    s = ("a serious vascular event occurred in 689 patients (8.9%) in the fatty acid group and in 712 (9.2%) "
         "in the placebo group (rate ratio, 0.97; 95% confidence interval, 0.87 to 1.08).")
    assert _scale(s) == "RR", "a first-event log-rank rate ratio must not be typed IRR"


def test_recurrent_rate_ratio_stays_irr_by_times():
    s = ("The second primary outcome, total heart failure hospitalizations, occurred 264 times in the ferric "
         "carboxymaltose group vs 320 times in placebo (rate ratio, 0.80; 95% CI, 0.60 to 1.06).")
    assert _scale(s) == "IRR", "a genuine recurrent-event rate ratio ('occurred 264 times') must stay IRR"


def test_person_time_rate_ratio_stays_irr():
    s = ("Ketoacidosis occurred at 0.09 versus 0.02 per 100 person-years (rate ratio, 4.5; 95% CI, 1.2 to 9.9).")
    assert _scale(s) == "IRR", "an explicit per-person-time rate ratio must stay IRR"


def test_explicit_incidence_rate_label_stays_irr():
    s = "The incidence rate ratio was 1.20 (95% CI 1.05 to 1.40)."
    assert _scale(s) == "IRR"


def test_omega3_pools_and_iv_iron_stays_suppressed():
    """Suppression follows the effect classes of admitted members; source IRR typing remains covered above."""
    import json
    from pathlib import Path
    from _contracts import partition, scale_contract
    root = Path(__file__).resolve().parents[1]
    for slug in ('omega3-cardiovascular-events', 'iv-iron-hfref-hosp'):
        review = json.loads((root/'docs/reviews'/slug/'review.json').read_text(encoding='utf-8'))
        outcome = next(o for o in review['outcomes'] if o.get('primary'))
        partition(root, slug, outcome)
        scale_contract(outcome)
