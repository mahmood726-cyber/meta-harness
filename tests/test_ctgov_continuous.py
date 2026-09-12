"""ClinicalTrials.gov structured CONTINUOUS extraction (MEAN + per-arm SD -> mean-difference input).
Modelled on the real NCT00397189 (melatonin, subjective sleep-onset latency) posted results."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.ctgov_results import extract_ctgov  # noqa: E402


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
