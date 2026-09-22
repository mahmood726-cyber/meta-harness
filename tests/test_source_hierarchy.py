import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _families import eligible_by_construction  # noqa: E402  (families ELIGIBLE by construction: the admission gate is on by default)

from harness import extract  # noqa: E402
from harness.pipeline import _build_outcome  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ABSTRACT = ("Colchicine reduced recurrent pericarditis during follow-up "
            "(RR=0.40, 95% CI 0.30 to 0.54). Adverse events were not increased.")
FULLTEXT = ("In a sensitivity analysis of recurrent pericarditis the risk ratio was "
            "RR 0.46 (95% CI 0.37 to 0.58). Gastrointestinal adverse events occurred more often "
            "with colchicine (RR 1.85, 95% CI 1.04 to 3.29).")


def test_abstract_headline_wins_over_fulltext():
    eff = extract.comparator_effect(ABSTRACT, FULLTEXT, ["recurren"])
    assert eff is not None and abs(eff["effect"] - 0.40) < 1e-9, eff
    assert abs(eff["ci_low"] - 0.30) < 1e-9 and abs(eff["ci_high"] - 0.54) < 1e-9, eff


def test_fulltext_fills_outcome_absent_from_abstract():
    eff = extract.comparator_effect(ABSTRACT, FULLTEXT, ["gastrointestinal", "adverse"])
    assert eff is not None and abs(eff["effect"] - 1.85) < 1e-9, eff


def test_absent_everywhere_returns_none():
    assert extract.comparator_effect(ABSTRACT, FULLTEXT, ["mortality", "death"]) is None


def _one_trial(abstract, estimand="RR"):
    spec = {"name": "Death", "keywords": ["death"], "estimand": estimand, "primary": True}
    included = [{"id": "1", "id_type": "pmid", "label": "SYNTH"}]
    recs = {"1": {"id": "1", "abstract": abstract}}
    return _build_outcome(spec, "efficacy", included, recs, ["drug"], ["placebo"], family_nodes=eligible_by_construction(recs))


def test_published_target_effect_beats_reconstructed_counts():
    abstract = (
        "Outcome death occurred in 20 (20.0%) of 100 patients receiving drug and "
        "25 (25.0%) of 100 patients receiving placebo; hazard ratio, 0.80; "
        "95% CI, 0.64 to 1.00."
    )
    pre_fix = extract.extract_trial(abstract, ["death"], ["drug"], ["placebo"], estimand="RR")
    assert pre_fix.get("ai") == 20 and pre_fix.get("effect") is None

    out = _one_trial(abstract, estimand="RR")
    trial = out["trials"][0]
    assert trial["effect"] == 0.80
    assert trial["scale"] == "HR"
    assert trial["selection_rule"] == "PUBLISHED_EFFECT_TARGET_CLASS"
    assert trial["alternatives"][0]["ai"] == 20


def test_counts_remain_when_no_published_effect_exists():
    abstract = (
        "Outcome death occurred in 20 (20.0%) of 100 patients receiving drug and "
        "25 (25.0%) of 100 patients receiving placebo."
    )
    trial = _one_trial(abstract, estimand="RR")["trials"][0]
    assert trial["ai"] == 20 and trial.get("effect") is None
    assert trial["selection_rule"] == "KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT"


def test_different_estimand_class_does_not_override_counts():
    abstract = (
        "Outcome death occurred in 20 (20.0%) of 100 patients receiving drug and "
        "25 (25.0%) of 100 patients receiving placebo; recurrent events rate ratio, "
        "0.80; 95% CI, 0.64 to 1.00."
    )
    trial = _one_trial(abstract, estimand="RR")["trials"][0]
    assert trial["ai"] == 20 and trial.get("effect") is None
    assert trial["selection_rule"] == "KEEP_RECONSTRUCTION_EFFECT_CLASS_MISMATCH"
    assert trial["alternatives"][0]["not_selected_reason"] == "NOT_TARGET_CLASS"
    assert trial["alternatives"][0]["not_selected_detail"] == "RATE!=FIRST_EVENT_RATIO"


def _load_prefix_spironolactone_review():
    res = subprocess.run(
        ["git", "show", "aa8ed28a:docs/reviews/spironolactone-hfref-mortality/review.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(res.stdout)


def _load_current_spironolactone_review():
    with open(os.path.join(ROOT, "docs", "reviews", "spironolactone-hfref-mortality", "review.json"),
              encoding="utf-8") as f:
        return json.load(f)


def _j_emphasis_limitation_violations(review):
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    row = next(t for t in primary["trials"] if "28824029" in t.get("id", ""))
    codes = {lim.get("code") for lim in row.get("source_hierarchy_limitations") or []}
    if row.get("derivation") == "reconstructed" and "PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE" not in codes:
        return ["J-EMPHASIS-HF reconstructed row lacks PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE"]
    return []


def test_prefix_j_emphasis_limitation_check_fires():
    assert _j_emphasis_limitation_violations(_load_prefix_spironolactone_review()) == [
        "J-EMPHASIS-HF reconstructed row lacks PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE"
    ]


def test_rebuilt_j_emphasis_limitation_check_passes():
    assert _j_emphasis_limitation_violations(_load_current_spironolactone_review()) == []
