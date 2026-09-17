import json
import os
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness import source_hierarchy  # noqa: E402
from harness.page import render_page  # noqa: E402
from harness.pipeline import _build_outcome  # noqa: E402


def _load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _git_json(path):
    data = subprocess.check_output(["git", "show", f"ad5e7c66:{path}"], cwd=ROOT)
    return json.loads(data)


def _primary(review):
    return next(o for o in review["outcomes"] if o.get("primary"))


def _record(records, pmid):
    return next(r for r in records["records"] if r.get("id") == pmid)


def test_sglt2_abstract_hr_candidates_are_surfaced_and_selected():
    pre = _primary(_git_json("docs/reviews/sglt2-hfref-hosp-cvdeath/review.json"))
    pre_rows = {t["id"]: t for t in pre["trials"]}
    assert pre_rows["PMID 31535829"].get("effect") is None
    assert pre_rows["PMID 32865377"].get("effect") is None

    spec = _load("topics/sglt2-hfref-hosp-cvdeath.json")["primary_outcome"]
    records = _load("cache/sglt2-hfref-hosp-cvdeath/records.json")
    dapa = _record(records, "31535829")
    assert "hazard ratio, 0.74" in dapa["abstract"]
    cands = source_hierarchy.source_effect_candidates(spec, abstract=dapa["abstract"])
    assert any(c["scale"] == "HR" and c["effect"] == 0.74 for c in cands)

    post = _primary(_load("docs/reviews/sglt2-hfref-hosp-cvdeath/review.json"))
    rows = {t["id"]: t for t in post["trials"]}
    assert rows["PMID 31535829"]["effect"] == 0.75
    assert rows["PMID 32865377"]["effect"] == 0.75
    assert rows["PMID 31535829"]["selection_rule"] == "KEEP_REPORTED_EFFECT"
    assert rows["PMID 31535829"]["provenance"] == "ctgov_results"
    assert "ClinicalTrials.gov results (structured target endpoint)" in rows["PMID 31535829"]["source"]
    assert rows["PMID 32865377"]["selection_rule"] == "KEEP_REPORTED_EFFECT"
    assert post["result"]["scale"] == "HR"
    assert post["result"]["estimate"] == pytest.approx(0.75, abs=5e-4)
    hksj = post["result"]["ci_hksj_unserved"]
    assert hksj["ci_low"] == pytest.approx(0.4003, abs=5e-4)
    assert hksj["ci_high"] == pytest.approx(1.4052, abs=5e-4)


def test_colchicine_or_is_non_target_alternative_under_rr_outcome():
    pre = _primary(_git_json("docs/reviews/colchicine-postop-af/review.json"))
    pre_row = next(t for t in pre["trials"] if "32720823" in t["id"])
    assert pre_row["ai"] == 13 and pre_row.get("effect") is None

    post = _primary(_load("docs/reviews/colchicine-postop-af/review.json"))
    row = next(t for t in post["trials"] if "32720823" in t["id"])
    assert row["ai"] == 13 and row["n1i"] == 81
    assert row["ci"] == 13 and row["n2i"] == 71
    assert row.get("effect") is None
    alt = next(a for a in row["alternatives"] if a.get("scale") == "OR")
    assert alt["effect"] == 0.85
    assert alt["not_selected_reason"] == "NOT_TARGET_CLASS"


def test_tocilizumab_estimand_decision_controls_served_scale_and_renders():
    review = _load("docs/reviews/tocilizumab-covid19-mortality/review.json")
    outcome = _primary(review)
    decision = outcome["estimand_decision"]
    assert outcome["estimand"] == "OR"
    assert outcome["served_estimand"] == "RR"
    assert decision["decision"] == "cumulative_risk_at_trial_end"
    assert decision["target_scale"] == outcome["result"]["scale"] == "RR"
    html = render_page(review)
    assert "Estimand decision" in html
    assert "declared OR" in html
    assert "Target scale RR" in html


def _one_trial(abstract, estimand="RR"):
    spec = {"name": "Death", "keywords": ["death"], "estimand": estimand, "primary": True}
    included = [{"id": "1", "id_type": "pmid", "label": "SYNTH"}]
    recs = {"1": {"id": "1", "abstract": abstract}}
    return _build_outcome(spec, "efficacy", included, recs, ["drug"], ["placebo"])


def test_synthetic_rate_effect_for_first_event_outcome_never_selected():
    abstract = (
        "Outcome death occurred in 20 (20.0%) of 100 patients receiving drug and "
        "25 (25.0%) of 100 patients receiving placebo; recurrent events rate ratio, "
        "0.80; 95% CI, 0.64 to 1.00."
    )
    row = _one_trial(abstract, estimand="RR")["trials"][0]
    assert row["ai"] == 20 and row.get("effect") is None
    alt = row["alternatives"][0]
    assert alt["scale"] == "IRR"
    assert alt["not_selected_reason"] == "NOT_TARGET_CLASS"


def test_synthetic_counts_only_row_keeps_reconstruction():
    abstract = (
        "Outcome death occurred in 20 (20.0%) of 100 patients receiving drug and "
        "25 (25.0%) of 100 patients receiving placebo."
    )
    row = _one_trial(abstract, estimand="RR")["trials"][0]
    assert row["ai"] == 20 and row.get("effect") is None
    assert row["selection_rule"] == "KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT"
