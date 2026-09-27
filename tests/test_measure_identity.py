"""Effect-identity COUNTERCHECK (NOAC-AF review, 2026-09-27, hash f1867881; retrospective, Dispatch under Mahmood's delegation).

The measure comes from the statistical MODEL and the outcome process, never from the abbreviation alone -- so the rule does not
over-refuse. RE-LY's "relative risk, 0.66 (0.53-0.82)" is a Cox hazard ratio in substance (its held registry analysis of the
same outcome is "Cox Proportional Hazard"); an ordinary count-based RR stays an RR. ENGAGE's 97.5% CI keeps its level, interval,
transform and SE; the pooled ~95% interval is derived, never a published 95% CI. Held bytes at the pinned candidate 3876a62d."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import measure_identity as mi   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "noac-vs-warfarin-af-stroke"


def _show(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


@pytest.fixture(scope="module")
def served():
    return next(o for o in json.loads(_show(f"docs/reviews/{SLUG}/review.json"))["outcomes"] if o.get("primary"))


@pytest.fixture(scope="module")
def recs():
    return {str(r["id"]): r for r in json.loads(_show(f"cache/{SLUG}/records.json"))["records"]}


def _row(served, pid):
    return next(t for t in served["trials"] if t["id"] == f"PMID {pid}")


def test_plant_the_served_page_calls_the_pool_three_hr_plus_one_rr(served):
    assert served["result"]["scale_mixed"] == ["HR", "RR"] and _row(served, "19717844")["scale"] == "RR"


def test_re_ly_is_a_hazard_ratio_from_its_cox_model_with_the_source_term_kept(served, recs):
    reg = mi.registry_models(SLUG)
    c = mi.classify(_row(served, "19717844"), served["name"], recs["19717844"]["nct"], reg, recs["19717844"]["abstract"])
    assert (c["measure"], c["scale"], c["source_term"], c["model"]) == ("HAZARD_RATIO", "HR", "relative risk", "COX")
    assert "NCT00262600" in c["model_basis"] and "Stroke/SEE" in c["model_basis"] and c["outcome_process"] == "TIME_TO_EVENT_RATE"


def test_an_ordinary_count_rr_stays_rr_and_the_word_alone_never_decides():
    count_rr = {"source": "abstract arm-level counts: 20 of 100 vs 25 of 100 (relative risk, 0.80; 95% CI, 0.48 to 1.34)",
                "effect": 0.8, "ci_low": 0.48, "ci_high": 1.34, "scale": "RR"}
    c = mi.classify(count_rr, "Stroke or systemic embolism", None, {}, "")
    assert (c["measure"], c["model"]) == ("RISK_RATIO", "NOT_STATED")
    # a registry analysis of a DIFFERENT outcome of the same trial does not transfer its Cox model
    reg = {"NCT1": [{"outcome_id": "9", "outcome_title": "Major Bleeding", "model": "COX", "param_type": "Cox Proportional Hazard",
                     "value": "0.8", "analysis_id": "1"}]}
    assert mi.classify(count_rr, "Stroke or systemic embolism", "NCT1", reg, "")["measure"] == "RISK_RATIO"
    # a model stated in the row's own source decides
    logistic = dict(count_rr, source="logistic regression odds ratio 0.80 (0.48 to 1.34)")
    assert mi.classify(logistic, "x", None, {}, "")["measure"] == "ODDS_RATIO"


def test_engage_keeps_its_97_5_percent_interval_and_the_95_percent_one_is_derived(served):
    cp = mi.ci_level_provenance(_row(served, "24251359"))
    assert cp["published"] == {"level": 97.5, "ci_low": 0.73, "ci_high": 1.04, "span": "97.5% CI, 0.73 to 1.04"}
    assert cp["se"] == 0.078953 and cp["derived_95"] == {"ci_low": 0.7453, "ci_high": 1.0156}
    assert cp["state"] == "DERIVED_95_FROM_PUBLISHED_LEVEL" and "not a published 95% CI" in cp["presentation"]
    as_is = dict(_row(served, "24251359"), ci_low=0.73, ci_high=1.04)
    assert mi.ci_level_provenance(as_is)["state"] == "PUBLISHED_NON_95_SERVED_AS_IS"
    assert mi.ci_level_provenance(_row(served, "21870978")) is None           # ARISTOTLE: a 95% CI


def test_corpus_n_of_n_matches_the_recorded_measurement():
    sys.path.insert(0, os.path.join(ROOT, "evidence", "effect_identity"))
    import measure_measure_identity as m
    got = m.measure(PINNED)
    assert (got["served_effect_rows"], got["measure_changed"], got["rr_time_to_event_model_not_held"], got["ci_level_not_95"]) == (86, 1, 2, 1)
