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
        rv = _j("docs", "reviews", s, "review.json")["comparator"]
        ov = rv["overlap"]
        if rv["reported"]:
            assert ov["theirs_k"] == pr["k"], (s, ov["theirs_k"], pr["k"])
        else:                                   # the adopted analysis is not this outcome: its k is not this outcome's k
            assert isinstance(ov["theirs_k"], str) and "not stated" in ov["theirs_k"], (s, ov["theirs_k"])


def test_PLANT_the_adopted_number_stands_only_for_its_rules_primary_outcome():
    """codex v8-apply #1: a valid estimate for one endpoint must never become the reported number for another."""
    a = {"rule_primary_outcome": "Stroke"}
    assert not sc.adopted_outcome_matches(a, "All-cause mortality")
    assert sc.adopted_outcome_matches({"rule_primary_outcome": "new vertebral fracture"}, "New vertebral fracture")
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": "3-point major adverse cardiovascular events (CV death)"},
                                          "3-point major adverse cardiovascular events")
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": None}, "anything")


def test_PLANT_a_broken_adoption_register_refuses(tmp_path):
    import pytest
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    (d / "x.adoption.json").mkdir()                       # exists, not a file (codex v8-apply #3)
    with pytest.raises(ValueError):
        sc.adopted_pooled("x", {"comparator_pmid": "1"}, str(tmp_path))


def test_PLANT_a_composite_is_not_its_component():
    """codex v8-apply-r2 #1: containment assigned a mortality estimate to 'mortality or hospitalization'."""
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": "All-cause mortality"},
                                          "All-cause mortality or hospitalization")
    assert sc.adopted_outcome_matches({"rule_primary_outcome": "Major vascular events"},
                                      "Total cardiovascular events / major vascular events")


def test_PLANT_a_signed_adoption_without_its_pooled_result_refuses(tmp_path):
    import pytest
    s = "dpp4-mace-t2d"
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    a = _j("registry", "comparator_selection", f"{s}.adoption.json")
    a.pop("pooled_result")
    (d / f"{s}.adoption.json").write_text(json.dumps(a), encoding="utf-8")
    (tmp_path / "registry" / "comparator_switch_signatures.json").write_text(
        json.dumps(_j("registry", "comparator_switch_signatures.json")), encoding="utf-8")
    with pytest.raises(ValueError):
        sc.adopted_pooled(s, {"comparator_pmid": a["comparator_pmid"]}, str(tmp_path))


def test_PLANT_a_timepoint_qualifier_defines_a_different_endpoint():
    """codex v8-apply-r3 #1: '(30 days)' and '(1 year)' are different endpoints; a digit-free definition is not."""
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": "All-cause mortality (30 days)"},
                                          "All-cause mortality (1 year)")
    # names that differ only by a qualifier are NOT matched: absent, never guessed (codex v8-apply-r4 #1)
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": "3-point MACE (CV death, nonfatal MI, nonfatal stroke)"},
                                          "3-point MACE")
    assert not sc.adopted_outcome_matches({"rule_primary_outcome": "Myocardial infarction (fatal)"},
                                          "Myocardial infarction (nonfatal)")


def test_PLANT_a_signed_adoption_without_its_rule_refuses(tmp_path):
    import pytest
    s = "dpp4-mace-t2d"
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    a = _j("registry", "comparator_selection", f"{s}.adoption.json")
    (d / f"{s}.adoption.json").write_text(json.dumps(a), encoding="utf-8")       # no rule file beside it (codex r3 #3)
    (tmp_path / "registry" / "comparator_switch_signatures.json").write_text(
        json.dumps(_j("registry", "comparator_switch_signatures.json")), encoding="utf-8")
    with pytest.raises(ValueError):
        sc.adopted_pooled(s, {"comparator_pmid": a["comparator_pmid"]}, str(tmp_path))


def test_PLANT_an_adoption_without_a_retired_identity_refuses(tmp_path):
    import pytest
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    (d / "x.adoption.json").write_text(json.dumps({"comparator_pmid": "222", "pooled_result": {
        "measure": "RR", "estimate": 0.8, "ci_low": 0.7, "ci_high": 0.9}}), encoding="utf-8")   # codex r5 #3
    with pytest.raises(ValueError):
        sc.adopted_pooled("x", {"comparator_pmid": "222"}, str(tmp_path))


def test_PLANT_adopted_numbers_must_be_verbatim_in_their_span(tmp_path):
    """codex v8-apply-r8 #1: a pooled_result contradicting its own quoted span is broken, never served."""
    import pytest
    s = "denosumab-vertebral-fracture"
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    a = _j("registry", "comparator_selection", f"{s}.adoption.json")
    for f in ("rule",):
        (d / f"{s}.{f}.json").write_text(json.dumps(_j("registry", "comparator_selection", f"{s}.{f}.json")), encoding="utf-8")
    (tmp_path / "registry" / "comparator_switch_signatures.json").write_text(
        json.dumps(_j("registry", "comparator_switch_signatures.json")), encoding="utf-8")
    good = dict(a)
    (d / f"{s}.adoption.json").write_text(json.dumps(good), encoding="utf-8")
    assert sc.adopted_pooled(s, {"comparator_pmid": a["comparator_pmid"]}, str(tmp_path))["estimate"] == 0.32
    bad = dict(a, pooled_result=dict(a["pooled_result"], estimate=99))
    (d / f"{s}.adoption.json").write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        sc.adopted_pooled(s, {"comparator_pmid": a["comparator_pmid"]}, str(tmp_path))


def test_every_signed_adoption_passes_its_own_span_check():
    """All five V8 adoptions (esketamine's span prints a Unicode minus) load without error."""
    for s in SWITCHED:
        cfg = _j("topics", f"{s}.json")
        assert sc.adopted_pooled(s, cfg) is not None, s


def test_PLANT_the_span_must_state_estimate_then_lower_then_upper():
    """codex v8-apply-r9 #1: number membership alone let a swapped estimate and bound through."""
    span = "All-cause mortality: RR 0.8 (0.7-0.9)"
    assert sc._span_states(span, 0.8, 0.7, 0.9)
    assert not sc._span_states(span, 0.7, 0.8, 0.9)          # swapped
    assert not sc._span_states(span, 0.8, 0.9, 0.7)          # bounds reversed
    assert not sc._span_states("RR 0.2 (0.7-0.9)", 0.8, 0.7, 0.9)
    assert sc._span_states("MD=-4.09, 95%CI -5.73 to -2.45", -4.09, -5.73, -2.45)
