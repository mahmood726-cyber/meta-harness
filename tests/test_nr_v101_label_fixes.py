"""Lane NR V1.0.1 pre-fix-firing plants for the label fixes (Mahmood: 'fix all in harness'), statins-older-adults and
ticagrelor reviews. Each detector is run on the PRE-FIX served output (the committed pages at HEAD, read with git show)
and must FIRE there, then on the rebuilt page in docs/ and must be SILENT. The detectors derive their answer from rows
and held records, never from a field the fixes add, so the same instrument measures both sides.
Corpus n of N: scripts/nr_v101_label_audit.py (HEAD vs a rebuild directory).
"""
from __future__ import annotations

import html as _html
import json
import re
import subprocess
from pathlib import Path

from harness import composite_label, gate, k2, rob2, subgroup_provenance as sp

ROOT = Path(__file__).resolve().parents[1]


def _head(path):
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT).decode("utf-8")


def _pre(slug):
    return json.loads(_head(f"docs/reviews/{slug}/review.json")), _head(f"docs/reviews/{slug}/index.html")


def _live(slug):
    d = ROOT / "docs" / "reviews" / slug
    return json.load(open(d / "review.json", encoding="utf-8")), open(d / "index.html", encoding="utf-8").read()


def _records(slug):
    return {str(r.get("id")): r for r in json.loads(_head(f"cache/{slug}/records.json")).get("records", [])}


def _text(h):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h)))


def _prim(rev):
    return next(o for o in rev["outcomes"] if o.get("primary"))


# ---- A: a post-hoc subgroup served as pre-specified ---------------------------------------------------------------

def test_A_statins_post_hoc_subgroup_called_prespecified_fires_pre_fix_and_not_after():
    recs = _records("statins-primary-prevention-elderly")
    pre_rev, pre_page = _pre("statins-primary-prevention-elderly")
    pre = sp.prespecified_claim_violations(pre_rev, recs, pre_page)
    assert [(v["trial"], v["derived"]) for v in pre] == [("PMID 20404379", "post_hoc_subgroup")]
    assert set(pre[0]["served_as_prespecified_in"]) == {"evidence_unit", "question/population prose", "page unit label"}
    rev, page = _live("statins-primary-prevention-elderly")
    assert sp.prespecified_claim_violations(rev, recs, page) == []
    # the topic still ASSERTS it (no hand edit); the harness serves the derived value and records the correction
    topic = json.load(open(ROOT / "topics" / "statins-primary-prevention-elderly.json", encoding="utf-8"))
    assert "pre-specified JUPITER" in topic["question"]
    assert "pre-specified" not in rev["question"] and "pre-specified" not in _prim(rev)["population"]
    assert {c["rule_id"] for c in rev["served_prose_corrections"]} == {sp.PROSE_RULE_ID}
    assert _prim(rev)["trials"][0]["subgroup_provenance"]["value"] == sp.POST_HOC


def test_A_melatonin_unresolved_subgroup_called_prespecified_fires_pre_fix_and_not_after():
    recs = _records("melatonin-primary-insomnia-sol")
    pre_rev, pre_page = _pre("melatonin-primary-insomnia-sol")
    assert [v["derived"] for v in sp.prespecified_claim_violations(pre_rev, recs, pre_page)] == ["unresolved"]
    rev, page = _live("melatonin-primary-insomnia-sol")
    assert sp.prespecified_claim_violations(rev, recs, page) == []
    assert "pre-specification not stated in the source" in _text(page)


# ---- B: an unqualified MACE / 3-point label ----------------------------------------------------------------------

def test_B_unqualified_mace_label_fires_pre_fix_and_not_after():
    for slug in ("statins-primary-prevention-elderly", "pcsk9-mace", "ticagrelor-vs-clopidogrel-acs"):
        recs = _records(slug)
        pre_rev, pre_page = _pre(slug)
        assert composite_label.audit(pre_rev, recs, pre_page)["unqualified"], slug
        rev, page = _live(slug)
        assert composite_label.audit(rev, recs, page)["unqualified"] == [], slug
        assert gate.check_composite_label(str(ROOT / "docs" / "reviews" / slug), page) == [], slug


def test_B_identical_3_point_pools_keep_their_label():
    rev, page = _live("glp1-ra-mace-t2d")
    lab = _prim(rev)["composite_label"]
    assert lab["kind"] == composite_label.IDENTICAL_3P and composite_label.served_name(_prim(rev)) == _prim(rev)["name"]


# ---- C: a computed-but-withheld k=2 registered CI worded as a refusal ----------------------------------------------

def test_C_k2_interval_worded_as_refusal_fires_pre_fix_and_not_after():
    _, pre_page = _pre("statins-primary-prevention-elderly")
    assert "Registered pooled CI REFUSED at k=2" in _text(pre_page)
    rev, page = _live("statins-primary-prevention-elderly")
    t = _text(page)
    assert "REFUSED at k=2" not in t and "Registered PM/HKSJ CI computed, withheld by presentation policy" in t
    assert _prim(rev)["result"]["pooled_ci_refused"]["state"] == k2.WITHHELD_BY_POLICY


# ---- E: ticagrelor direction conflict ----------------------------------------------------------------------------

def test_E_ticagrelor_primary_reproduces():
    cf = _prim(_live("ticagrelor-vs-clopidogrel-acs")[0])["result"]["counterfactual"]
    assert (round(cf["would_be_estimate"], 3), round(cf["would_be_tau2"], 4), cf["would_be_i2"]) == (1.048, 0.1217, 77.7)
    assert (round(cf["would_be_ci_low"], 3), round(cf["would_be_ci_high"], 1)) == (0.032, 33.9)


def test_E_withholding_is_a_display_policy_and_plato_alone_is_not_the_conclusion():
    _, pre_page = _pre("ticagrelor-vs-clopidogrel-acs")
    pt = _text(pre_page)
    assert "Pooled result REFUSED (k=2 direction conflict)" in pt and "Honest k=1 anchor: PLATO HR 0.84" in pt
    rev, page = _live("ticagrelor-vs-clopidogrel-acs")
    t = _text(page)
    ref = _prim(rev)["result"]["pool_refused"]
    assert ref["policy"] == "DISPLAY" and ref["state"] == k2.WITHHELD_BY_POLICY
    assert "Pooled result computed, withheld by display policy (k=2 direction conflict)" in t
    assert "Pooled result REFUSED" not in t and "Honest k=1 anchor" not in t
    assert "PLATO alone (shown alone: one of the two eligible trials" in t and "not the review-wide conclusion" in t
    assert gate.direction_conflict_claim_violations(rev) == []


def test_E_anchor_read_as_conclusion_is_refused():
    rev, _ = _live("ticagrelor-vs-clopidogrel-acs")
    bad = json.loads(json.dumps(rev))
    anchor = _prim(bad)["result"]["pool_refused"]["honest_k1_anchor"]
    anchor["scope"] = "the review's answer"          # a surface that drops 'alone'
    import harness.k2 as _k2
    orig = _k2.anchor_heading
    try:
        _k2.anchor_heading = lambda a: f"{a.get('name')}"
        assert any(v.startswith("ANCHOR_AS_CONCLUSION") for v in gate.direction_conflict_claim_violations(bad))
    finally:
        _k2.anchor_heading = orig


def test_E_opposite_directions_generate_no_explanatory_or_equivalence_claim():
    fire = ["The discordance between PLATO and PHILO may be explained by the East Asian population of PHILO.",
            "PHILO's harm signal is attributable to regional differences in practice.",
            "Ticagrelor was equivalent to clopidogrel.", "There was no significant difference between the drugs.",
            "Overall there is no benefit of ticagrelor."]
    for s in fire:
        assert k2.conflict_claim_violations(s), s
    quiet = ["The two eligible trials conflict in direction, so the computed pooled effect is withheld by display policy.",
             "PHILO enrolled Japanese, Korean and Taiwanese patients."]   # a population description is not an explanation
    for s in quiet:
        assert k2.conflict_claim_violations(s) == [], s
    rev, _ = _live("ticagrelor-vs-clopidogrel-acs")
    assert k2.conflict_claim_violations(gate.direction_conflict_generated_text(rev)) == []


# ---- F: a provisional RoB signal whose evidence fails the identity check -----------------------------------------

def test_F_plato_d5_similarity_match_is_withdrawn_not_provisional():
    pre = _pre("ticagrelor-vs-clopidogrel-acs")[0]["rob2"]["trials"]["19717846"]["domains"]["D5_selective_reporting"]
    assert pre["level"] == "low" and rob2.identity_check_failed(pre)                # the pre-fix page showed it
    assert "Non-CABG" in pre["inputs"]["comparison"]["registered_label"]
    rev, _ = _live("ticagrelor-vs-clopidogrel-acs")
    d5 = rev["rob2"]["trials"]["19717846"]["domains"]["D5_selective_reporting"]
    assert d5["level"] == rob2.WITHDRAWN and d5["basis"].startswith("WITHDRAWN")
    fails = {f["registered_label"]: f["identity_check"] for f in d5["inputs"]["comparison"]["identity_failures"]}
    assert any("Non-CABG" in k and v == "FAILED" for k, v in fails.items())          # the bleeding 'match'
    assert any("Death From Vascular Causes" in k and v == "UNDECIDABLE" for k, v in fails.items())   # its own primary
    assert rob2.rederive_domain(d5, lambda a, b: True)["level"] == rob2.WITHDRAWN   # a lenient matcher cannot revive it
    assert gate.check_rob_rederivable(str(ROOT / "docs" / "reviews" / "ticagrelor-vs-clopidogrel-acs")) == []


def test_F_philo_no_match_on_an_undecidable_registered_mace_is_withdrawn():
    pre = _pre("ticagrelor-vs-clopidogrel-acs")[0]["rob2"]["trials"]["26376600"]["domains"]["D5_selective_reporting"]
    assert pre["level"] == "some concerns" and rob2.identity_check_failed(pre)
    d5 = _live("ticagrelor-vs-clopidogrel-acs")[0]["rob2"]["trials"]["26376600"]["domains"]["D5_selective_reporting"]
    assert d5["level"] == rob2.WITHDRAWN
    fails = {f["registered_label"]: f["identity_check"] for f in d5["inputs"]["comparison"]["identity_failures"]}
    assert fails.get("Major Adverse Cardiac Events (MACE)") == "UNDECIDABLE"


def test_F_order_independent_and_codex_cases():
    # codex NR-C19, each reproduced by execution before the fix
    T = lambda a, b: True                                                            # noqa: E731
    M = "Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke"
    cases = [("All-cause mortality", ["Major bleeding", "All-cause mortality"], T, "low"),     # identity later in the list
             ("All-cause mortality", ["Number of participants who died from any cause"], T, "low"),
             (M, ["Death from vascular causes, myocardial infarction, or stroke", "Major bleeding"], None, rob2.WITHDRAWN),
             (M, ["Major bleeding", "Death from cancer or myocardial infarction"], None, "some concerns"),
             (M, ["Major bleeding", "Death from vascular causes, myocardial infarction, stroke, or revascularization"],
              None, "some concerns"),
             ("Cardiovascular death", ["Death from vascular causes"], None, rob2.WITHDRAWN),
             ("Nonfatal myocardial infarction or nonfatal stroke",
              ["Death from vascular causes, myocardial infarction, or stroke"], None, rob2.WITHDRAWN),
             ("Fatal cardiac events", ["Major bleeding"], T, rob2.WITHDRAWN),
             ("All-cause mortality", ["All cause"], None, "some concerns"),
             ("Antibiotic-associated diarrhoea", ["Incidence of antibiotic associated diarrhea"], None, "low"),
             ("Percent change in body weight", ["Change in Body Weight (%)"], None, "low"),
             ("Major vascular events", ["Major cardiovascular events"], T, rob2.WITHDRAWN)]
    for pooled, regs, m, want in cases:
        got = rob2.derive_d5([{"measure": r} for r in regs], pooled, m)
        assert got["level"] == want, (pooled, regs, got["level"])
        assert rob2.rederive_domain(got, m)["level"] == want


# ---- G: tocilizumab k=1 --------------------------------------------------------------------------------------------

def test_G_k1_is_the_trials_own_result_in_its_own_population():
    pre_rev, pre_page = _pre("tocilizumab-covid19-mortality")
    recs = _records("tocilizumab-covid19-mortality")
    from harness import population_qualifier as pq
    kinds = {v["kind"] for v in pq.single_trial_violations(pre_rev, recs, _text(pre_page), ["tocilizumab"])}
    assert kinds == {"K1_SERVED_AS_SYNTHESIS", "K1_POPULATION_UNQUALIFIED"}                   # fires pre-fix
    rev, page = _live("tocilizumab-covid19-mortality")
    t = _text(page)
    assert pq.single_trial_violations(rev, recs, t, ["tocilizumab"]) == []
    st = _prim(rev)["result"]["single_trial"]
    assert st["presentation"] == "the trial's own result, not a synthesis"
    assert st["population_qualifier"]["restrictions"] == [
        "hypoxia (oxygen saturation <92% on air or requiring oxygen therapy)",
        "systemic inflammation (C-reactive protein ≥75 mg/L)"]
    assert st["population_qualifier"]["co_treatment"]["share_pct"] == 82.0
    assert "The trial's own result (one trial; not a synthesis)" in t and "Trials pooled (k) 1" not in t
    assert "Population of this result the trial's own population: only participants with hypoxia" in t
    assert "82% receiving systemic corticosteroids" in t and "not every patient the question covers" in t
    assert gate.check_single_trial_presentation(str(ROOT / "docs" / "reviews" / "tocilizumab-covid19-mortality"), page) == []


def test_G_intervention_is_not_a_co_treatment():
    from harness import population_qualifier as pq
    rec = {"abstract": "Patients were eligible if they had pneumonia. Overall 57% received dexamethasone in the trial."}
    assert pq.derive(rec, ["dexamethasone", "corticosteroid"]) is None
    assert pq.derive(rec, ["tocilizumab"])["co_treatment"]["share_pct"] == 57.0


def test_G_tocilizumab_safety_pool_stays_k2_withheld():
    rev, page = _live("tocilizumab-covid19-mortality")
    sae = next(o for o in rev["outcomes"] if o["name"] == "Serious adverse events")["result"]
    assert sae["k"] == 2 and sae["ci_low"] is None and sae["ci_high"] is None
    assert sae["pooled_ci_refused"]["code"] == k2.K2_SINGLE_DF
    assert sae["pooled_ci_refused"]["state"] == k2.WITHHELD_BY_POLICY
    assert "REFUSED at k=2" not in _text(page)


def test_F_identity_controls():
    pooled = "Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke"
    same = [{"measure": "Composite of cardiovascular death, myocardial infarction or stroke"}]
    assert rob2.derive_d5(same, pooled, lambda a, b: True)["level"] == "low"             # typed identity survives
    bleed = [{"measure": "Major Bleeding"}]
    assert rob2.derive_d5(bleed, pooled, lambda a, b: True)["level"] == rob2.WITHDRAWN    # similarity is not identity
    decidable = [{"measure": "Fatal and Nonfatal MI"}]                                   # MI only: a real no-match
    assert rob2.derive_d5(decidable, pooled, None)["level"] == "some concerns"
    assert rob2.overall({"D5_selective_reporting": {"level": rob2.WITHDRAWN}, "D1_randomisation": {"level": "low"}}
                        ).startswith("low")                                              # withdrawn is not assessed
