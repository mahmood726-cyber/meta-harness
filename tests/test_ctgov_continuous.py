"""ClinicalTrials.gov structured CONTINUOUS extraction (MEAN + per-arm SD -> mean-difference input).
Modelled on the real NCT00397189 (melatonin, subjective sleep-onset latency) posted results."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.ctgov_results import extract_ctgov, endpoint_weeks  # noqa: E402


def _om(dispersion="Standard Deviation"):
    return [{
        "type": "PRIMARY",
        "title": "The Change From Baseline in Subjective Sleep Latency.",
        "paramType": "MEAN",
        "dispersionType": dispersion,
        "unitOfMeasure": "minutes",
        "groups": [{"id": "OG000", "title": "Circadin"}, {"id": "OG001", "title": "Placebo"}],
        "classes": [{"categories": [{"measurements": [
            {"groupId": "OG000", "value": "-19.1", "spread": "47.3"},
            {"groupId": "OG001", "value": "-1.7", "spread": "47.8"},
        ]}]}],
        "denoms": [{"units": "Participants", "counts": [
            {"groupId": "OG000", "value": "137"}, {"groupId": "OG001", "value": "144"}]}],
    }]


KWS = ["sleep onset latency", "sleep-onset latency", "sleep latency", "subjective sleep latency"]


def test_continuous_mean_sd_extracted_and_arms_assigned():
    out = extract_ctgov(_om(), KWS, ["melatonin", "circadin"], ["placebo"])
    assert out is not None
    assert out["scale"] == "MD"
    # intervention arm = Circadin, comparator = Placebo (by title + 2-arm fallback)
    assert out["mean1"] == -19.1 and out["sd1"] == 47.3 and out["nc1"] == 137
    assert out["mean2"] == -1.7 and out["sd2"] == 47.8 and out["nc2"] == 144
    assert "-19.1" in out["source"] and "47.3" in out["source"]  # verbatim source span


def test_continuous_refuses_non_sd_dispersion():
    # Standard Error / 95% CI / range need a conversion we do not do silently here -> refuse
    assert extract_ctgov(_om("Standard Error"), KWS, ["melatonin"], ["placebo"]) is None
    assert extract_ctgov(_om("Inter-Quartile Range"), KWS, ["melatonin"], ["placebo"]) is None


def test_continuous_refuses_when_a_spread_is_missing():
    om = _om()
    om[0]["classes"][0]["categories"][0]["measurements"][0].pop("spread")
    assert extract_ctgov(om, KWS, ["melatonin"], ["placebo"]) is None


def test_continuous_refuses_when_title_does_not_match_outcome():
    om = _om()
    om[0]["title"] = "Change in total sleep time"  # not our outcome
    assert extract_ctgov(om, KWS, ["melatonin"], ["placebo"]) is None


def _multiarm_om():
    om = _om()  # start from a valid 2-arm MEAN+SD MADRS-style measure
    om[0]["groups"] = [{"id": "OG000", "title": "Esketamine 56 mg"},
                       {"id": "OG001", "title": "Esketamine 84 mg"},
                       {"id": "OG002", "title": "Placebo"}]
    om[0]["classes"][0]["categories"][0]["measurements"] = [
        {"groupId": "OG000", "value": "-18.8", "spread": "14.1"},
        {"groupId": "OG001", "value": "-21.4", "spread": "12.3"},
        {"groupId": "OG002", "value": "-14.8", "spread": "15.0"}]
    om[0]["denoms"] = [{"units": "Participants", "counts": [
        {"groupId": "OG000", "value": "98"}, {"groupId": "OG001", "value": "101"},
        {"groupId": "OG002", "value": "108"}]}]
    return om


def test_continuous_refuses_multi_arm_dose_trial():
    # two esketamine dose arms + placebo -> ambiguous which dose to pool -> REFUSE
    assert extract_ctgov(_multiarm_om(), KWS, ["esketamine"], ["placebo"]) is None


def _two_estimand_oms(on_treatment_first):
    """A trial posting the SAME %-change outcome under two estimands (in-trial / on-treatment),
    like the Korean STEP trial NCT04998136. On-treatment values are made systematically larger so a
    wrong pick is detectable in the returned mean."""
    def om(label, mean_iv):
        o = _om()[0]
        o["title"] = f"Change in Body Weight (%) : {label}"
        o["groups"] = [{"id": "OG000", "title": "Semaglutide 2.4 mg"}, {"id": "OG001", "title": "Placebo"}]
        o["classes"][0]["categories"][0]["measurements"] = [
            {"groupId": "OG000", "value": str(mean_iv), "spread": "7.3"},
            {"groupId": "OG001", "value": "-2.6", "spread": "5.8"}]
        o["denoms"] = [{"units": "Participants", "counts": [
            {"groupId": "OG000", "value": "100"}, {"groupId": "OG001", "value": "48"}]}]
        return o
    in_trial = om("In-trial Observation Period", -16.4)      # treatment-policy: what we must pick
    on_treat = om("On-treatment Observation Period", -19.9)  # supplementary: larger, must NOT pick
    return [on_treat, in_trial] if on_treatment_first else [in_trial, on_treat]


BW_KWS = ["change in body weight (%)", "body weight", "percent change in body weight"]


def test_prefers_treatment_policy_estimand_regardless_of_ctgov_order():
    """The treatment-policy (in-trial) estimand must be chosen over the supplementary on-treatment
    estimand no matter which CT.gov lists first — otherwise the pick is order luck and two trials can
    be pooled on different estimands. Before the tiebreak, on-treatment-first returned -19.9."""
    for on_first in (True, False):
        out = extract_ctgov(_two_estimand_oms(on_first), BW_KWS, ["semaglutide"], ["placebo"])
        assert out is not None
        assert out["mean1"] == -16.4, f"picked wrong estimand (on_treatment_first={on_first})"


def test_endpoint_weeks_parses_ctgov_timeframes():
    # the exact timeFrame strings from the semaglutide trials
    assert endpoint_weeks("Baseline (week 0) to week 68") == 68
    assert endpoint_weeks("Baseline (week 0), end of treatment (week 44)") == 44
    assert endpoint_weeks("baseline to 6 months") == 6 * 4.345
    assert endpoint_weeks("day 28") == 28 / 7.0
    assert endpoint_weeks("") is None  # no duration parseable -> guard cannot fire (refuse on absence)
    assert endpoint_weeks("change from baseline") is None
