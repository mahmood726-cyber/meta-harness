"""Plant: a signed replacement comparator's REPORTED result on the served page is its gated pooled result from the
adoption record (registry/comparator_selection/<slug>.adoption.json: read from the comparator's own text, numbers
verbatim in a quoted span) -- the value Mahmood saw in packet V8. The regex comparator extractor misattributed on two of
the five: dpp4 served 0.88 (the SGLT-2 inhibitors' MACE OR in the same sentence) for an adopted DPP-4 OR of 1.00, and
statins served 0.72 for an adopted primary-prevention OR of 0.88."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import served_comparator as sc  # noqa: E402

SWITCHED = ["dpp4-mace-t2d", "esketamine-trd-madrs", "melatonin-primary-insomnia-sol", "denosumab-vertebral-fracture",
            "statins-primary-prevention-elderly"]


def _j(*p):
    return json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))


def test_PLANT_each_switched_page_reports_its_adopted_pooled_result():
    for s in SWITCHED:
        pr = _j("registry", "comparator_selection", f"{s}.adoption.json")["pooled_result"]
        rep = _j("docs", "reviews", s, "review.json")["comparator"]["reported"]
        cos = _j("topics", f"{s}.json")["comparator_outcomes"]
        rule_o = _j("registry", "comparator_selection", f"{s}.rule.json")["protocol_reference"]["primary_outcome"]
        if not any(sc.adopted_outcome_matches({"rule_primary_outcome": rule_o}, co["name"]) for co in cos):
            assert rep == [], (s, "no comparator outcome is the rule's primary outcome: nothing reported", rep)
            continue
        assert len(rep) == 1, (s, rep)
        r = rep[0]
        assert (r["estimate"], r["ci_low"], r["ci_high"], r["scale"]) == (pr["estimate"], pr["ci_low"], pr["ci_high"],
                                                                           pr["measure"]), (s, r, pr)
        assert "adoption" in r.get("source", ""), s


def test_adopted_pooled_needs_a_signed_switch(tmp_path):
    s = "dpp4-mace-t2d"
    (tmp_path / "registry" / "comparator_selection").mkdir(parents=True)
    a = _j("registry", "comparator_selection", f"{s}.adoption.json")
    (tmp_path / "registry" / "comparator_selection" / f"{s}.adoption.json").write_text(json.dumps(a), encoding="utf-8")
    cfg = {"comparator_pmid": a["comparator_pmid"]}
    assert sc.adopted_pooled(s, cfg, str(tmp_path)) is None          # no signature file: not served
    assert sc.adopted_pooled(s, cfg)["estimate"] == a["pooled_result"]["estimate"]    # the committed signature
    assert sc.adopted_pooled(s, {"comparator_pmid": "999"}) is None   # a different comparator configured


def test_PLANT_theirs_k_is_the_adopted_pooled_analysis_k():
    for s in SWITCHED:
        pr = _j("registry", "comparator_selection", f"{s}.adoption.json")["pooled_result"]
        ov = _j("docs", "reviews", s, "review.json")["comparator"]["overlap"]
        assert ov["theirs_k"] == pr["k"], (s, ov["theirs_k"], pr["k"])


def test_PLANT_the_adopted_number_stands_only_for_its_rules_primary_outcome():
    """codex v8-apply #1: a valid estimate for one endpoint must never become the reported number for another."""
    a = {"rule_primary_outcome": "Stroke"}
    assert not sc.adopted_outcome_matches(a, "All-cause mortality")
    assert sc.adopted_outcome_matches({"rule_primary_outcome": "new vertebral fracture"}, "New vertebral fracture")
    assert sc.adopted_outcome_matches({"rule_primary_outcome": "3-point major adverse cardiovascular events (CV death)"},
                                      "3-point major adverse cardiovascular events")
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": None}, "anything")


def test_PLANT_a_broken_adoption_register_refuses(tmp_path):
    import pytest
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    (d / "x.adoption.json").mkdir()                       # exists, not a file (codex v8-apply #3)
    with pytest.raises(ValueError):
        sc.adopted_pooled("x", {"comparator_pmid": "1"}, str(tmp_path))
