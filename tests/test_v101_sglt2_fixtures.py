"""V1.0.1 (SGLT2 CKD, HFrEF and HHF-in-CVOTs reviews). Served fixtures read the committed pages; plants are synthetic.

CKD: SMART-C is a CONSORTIUM analysis whose methods state its 10 members (shared 3 of our 3); its harmonised outcome is
not ours. HFrEF: the participant total derives from the SAME contributing set as the pool; Ibrahim's "Placebo group" is
background-only; Pandey 2022 bound row by row. HHF: Zhang's EMPA-REG row is arm-reversed (positive controls as printed
and corrected); Kosiborod 2017 is a pooled analysis; the CVOT setting is never established by a background sentence."""
import json
from pathlib import Path

import pytest

from harness import comparator_analysis as ca
from harness import comparator_panel as cp
from harness import comparator_truth as ct
from harness import comparison_contrast as cc
from harness import positive_control as pc
from harness import screen
from harness import setting_scope

ROOT = Path(__file__).resolve().parents[1]
CKD, HFREF, HHF = "sglt2-ckd-progression", "sglt2-hfref-hosp-cvdeath", "sglt2-primary-prevention-hf"


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _page(slug):
    return (ROOT / "docs" / "reviews" / slug / "index.html").read_text(encoding="utf-8")


def _ov(slug):
    ov = _review(slug)["comparator"]["overlap"]
    return ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"], ov["only_ours"]


# ---- CKD ------------------------------------------------------------------------------------------------------------
def test_smart_c_is_a_consortium_and_its_stated_membership_shares_our_three():
    assert _ov(CKD) == ("SUBSET", 3, 10, 3, [])
    a = _review(CKD)["comparator"]["analysis"]
    assert a["comparator_type"] == "CONSORTIUM_ANALYSIS"
    assert a["named_membership"]["statement"]["state"] == "VERIFIED_NOT_HELD"
    assert "never used as a discovery substitute" in _page(CKD)


def test_smart_c_outcome_is_not_ours_and_agreement_validates_nothing():
    r, page = _review(CKD), _page(CKD)
    row = r["comparator"]["reported"][0]
    assert row["replaces_protocol_benchmark"]["state"] == "DIFFERENT_OUTCOME" and row["analysis"] == "CKD progression (harmonised)"
    assert r["comparator"]["scope"]["same_question"]["label"] != "SAME_QUESTION"
    assert "neither agreement nor disagreement validates anything" in page
    assert cp.gate_reasons(r, page) == []


def test_a_consortium_list_is_never_a_discovery_source():
    from harness import comparator_named
    assert comparator_named.panel_rows(ROOT, CKD) == []


# ---- HFrEF ----------------------------------------------------------------------------------------------------------
def test_hfref_participant_total_is_the_whole_pooled_set():
    ov = _review(HFREF)["comparator"]["overlap"]
    assert ov["ours_n"] == 8474 and "excess=725" in ov["n_reconciliation"]


def test_plant_dropping_one_contributing_trial_from_ours_n_fails_the_invariant():
    rows = [{"label": "A", "n1i": 100, "n2i": 100}, {"label": "B", "n1i": 50, "n2i": 50}]
    parts = [{"trial": "A", "n": 200}, {"trial": "B", "n": 100}]
    assert ct.set_sum_invariant(rows, parts, 300)
    assert not ct.set_sum_invariant(rows, parts[:1], 200)                 # one pooled trial dropped from the sum
    rec = ct.participant_reconciliation(500, rows + [{"label": "C", "effect": 0.8}])
    assert rec["code"] == "OURS_N_INCOMPLETE" and rec["ours_n"] is None and rec["ours_n_missing_for"] == ["C"]


def test_plant_an_effect_only_row_counts_its_arms_from_its_own_result_sentence():
    row = {"label": "E", "endpoint_result_span": "an event occurred in 361 of 1863 patients (19.4%) in the drug group and "
                                                  "in 462 of 1867 patients (24.7%) in the placebo group"}
    assert ct.participant_reconciliation(4000, [row])["ours_n"] == 3730


def test_hfref_pandey_is_bound_row_by_row_shared_2():
    assert _ov(HFREF) == ("SUBSET", 2, 4, 2, [])
    assert "is not evidence missing from our pool" in _page(HFREF)


def test_ibrahim_is_refused_at_the_comparison_level():
    rows = [d for d in _review(HFREF)["screening"]["records"] if str(d["id"]) in ("33426003", "NCT04385589")]
    assert rows and all(d["decision"] == "exclude" and d["rule_id"] == "X3-CONTRAST" for d in rows)
    assert "an arm LABEL is not a placebo" in rows[0]["reason"]


def _node(ctl_ints, pub_text):
    return ({"family_id": "F", "reports": [{"report_id": "111"}],
             "arms": [{"label": {"value": "Drug group"}, "active_interventions": ["dapagliflozin", "insulin"],
                       "background_therapy": ["insulin"]},
                      {"label": {"value": "Placebo group"}, "active_interventions": ctl_ints, "background_therapy": ["insulin"]}]},
            lambda rid: pub_text)


CFG = {"include": {"comparator_any": ["placebo"], "intervention_any": ["dapagliflozin"]}}


def test_plant_a_background_only_arm_labelled_placebo_is_refused_only_with_the_publication_evidence():
    node, txt = _node(["insulin"], "Dapagliflozin added to furosemide; patients were randomly divided into two arms.")
    assert cc.refusal(node, CFG, txt)["rule_id"] == "X3-CONTRAST"
    node, txt = _node(["insulin"], "a double-blind, placebo-controlled trial")          # its own report says placebo
    assert cc.refusal(node, CFG, txt) is None
    node, txt = _node(["insulin"], None)                                                   # no held publication
    assert cc.refusal(node, CFG, txt) is None
    node, txt = _node(["placebo", "insulin"], "randomly divided")                          # a placebo product
    assert cc.refusal(node, CFG, txt) is None


# ---- HHF in CVOTs ---------------------------------------------------------------------------------------------------
def test_hhf_all_four_programme_inputs_are_shared():
    r = _review(HHF)
    assert _ov(HHF) == ("SUBSET", 4, 8, 4, [])
    ids = {m["name"].split(" [")[0]: m["identity"] for m in r["comparator"]["overlap_relation"]["theirs"]["members"]}
    assert "identical to the title of our report" in ids["Zinman 2016"]
    assert "NCT01032629" in ids["Radholm 2018"]


def test_hhf_empa_reg_row_is_arm_reversed_and_kosiborod_is_a_pooled_analysis():
    mem = {m["label"]: m for m in _review(HHF)["comparator"]["analysis"]["membership"]["members"]}
    assert mem["Zinman 2016"]["source_check"]["state"] == "COMPARATOR_ARM_REVERSAL"
    assert mem["Kosiborod 2017"]["input_type"]["type"] == "POOLED_ANALYSIS"
    # our EMPA-REG hazard ratio is never altered to match the comparator's reversed row
    o = next(o for o in _review(HHF)["outcomes"] if o.get("primary"))
    er = next(t for t in o["trials"] if str(t["label"]) == "26378978")
    assert (er["effect"], er["ci_low"], er["ci_high"]) == (0.65, 0.5, 0.85)


@pytest.mark.parametrize("cid", ["zhang-2020-sglt2-hhf-as-printed", "zhang-2020-sglt2-hhf-empa-reg-corrected"])
def test_zhang_positive_controls_reproduce(cid):
    c = next(x for x in pc.load(ROOT) if x["id"] == cid)
    assert pc.compare(c, pc.reproduce(c, ROOT)) == []


def test_plant_arm_reversal_is_detected_against_the_trials_own_counts(tmp_path):
    c = tmp_path / "cache" / "s"
    c.mkdir(parents=True)
    (c / "own.txt").write_text("events occurred in 126/4687 patients on drug and 95/2333 on placebo", encoding="utf-8")
    (c / "cap.txt").write_text("forest plot of the outcome here", encoding="utf-8")
    cap = {"document_ref": "cache/s/cap.txt", "quote": "forest plot of the outcome"}
    src = {"document_ref": "cache/s/own.txt", "quote": "126/4687 patients on drug and 95/2333 on placebo",
           "counts": [126, 4687, 95, 2333]}
    for printed, want in (([95, 4687, 126, 2333], "COMPARATOR_ARM_REVERSAL"), ([126, 4687, 95, 2333], "SAME_COUNTS_AS_ITS_OWN_REPORT"),
                          ([100, 4687, 95, 2333], "COMPARATOR_ROW_UNRECONCILED")):
        doc = {"outcome": "o", "governing": dict(cap, k=1, n=7020, scale="RR"),
               "membership": {"figure": {"caption": cap, "url": "u", "sha256": "0" * 64, "why_not_held": "w", "read_by": "r"},
                              "rows": [{"label": "T", "counts": printed, "source_check": src}]}}
        (c / "comparator_analysis.json").write_text(json.dumps(doc), encoding="utf-8")
        got = ca.assess(ca.load(tmp_path, "s"), {"outcomes": []})
        assert got["membership"]["members"][0]["source_check"]["state"] == want


def test_simple_and_empa_heart_are_refused_on_setting_not_outcome():
    rows = {str(d["id"]): d for d in _review(HHF)["screening"]["records"]}
    for pmid in ("35061894", "31434508"):
        assert rows[pmid]["decision"] == "exclude" and rows[pmid]["rule_id"] == "X-SETTING", pmid


def test_plant_a_background_sentence_never_establishes_a_cvot():
    terms = ["cardiovascular events", "cardiovascular outcomes"]
    background = {"title": "Effect of drug X on cardiac filling pressures: a randomized trial",
                  "abstract": "BACKGROUND: Drug X reduces cardiovascular events in type 2 diabetes. METHODS: We randomised "
                              "40 patients. The primary end point was change in wedge pressure at 13 weeks."}
    assert setting_scope.setting_hit(background, terms, screen._has) is None
    own = dict(background, abstract=background["abstract"] + " RESULTS: The primary composite of cardiovascular events occurred less often.")
    assert setting_scope.setting_hit(own, terms, screen._has) == "cardiovascular events"
    titled = {"title": "Drug X and Cardiovascular Outcomes in Type 2 Diabetes", "abstract": ""}
    assert setting_scope.setting_hit(titled, terms, screen._has) == "cardiovascular outcomes"


# ---- binding guards (caught during this round: esketamine TRANSFORM-1, balanced-crystalloids SMART) ----------------
def test_served_bindings_the_guards_protect():
    eske = {m["name"]: m for m in _review("esketamine-trd-madrs")["comparator"]["overlap_relation"]["theirs"]["members"]}
    b = next(m for k, m in eske.items() if "[B20]" in k)
    assert b["family"] == "NCT02417064" and "TRANSFORM-1" in b["identity"]
    smart = next(m for m in _review("balanced-crystalloids-vs-saline-mortality")["comparator"]["overlap_relation"]["theirs"]["members"]
                 if m["name"] == "SMART")
    assert smart["family"] == "SYN-7ef776f99091"          # the SMART programme paper, never narrowed to SMART-MED


def _fam(fid, acr=(), reg=(), mentioned=(), reports=()):
    return {"family_id": fid, "aliases": {"acronym": list(acr), "registry_ids": list(reg),
                                          "mentioned_registry_ids": list(mentioned), "report_ids": list(reports)}}


def test_plant_a_borrowed_acronym_never_makes_an_owned_one_ambiguous():
    from harness import overlap_relation as orl
    review = {"trial_families": [_fam("NCT1", acr=["TRANSFORM-1"], reg=["NCT1"]),
                                 _fam("SYN-x", mentioned=["NCT1"], reports=["99"])]}
    idx = orl._acronym_index(review, lambda r: "TRANSFORM-1" if r == "NCT1" else None)
    assert idx[orl.norm_name("TRANSFORM-1")] == {"NCT1"}
    review = {"trial_families": [_fam("SYN-c", mentioned=["NCT2"], reports=["98"])]}
    idx = orl._acronym_index(review, lambda r: "CANVAS" if r == "NCT2" else None)
    assert idx[orl.norm_name("CANVAS")] == {"SYN-c"}     # no family owns it: the programme family borrows it
