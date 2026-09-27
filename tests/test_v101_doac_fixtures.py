"""V1.0.1 plants from the DOAC-VTE review.

(0) Found while doing it: the comparator full text held under van Es 2014's PMID was a CITING article (a review of DOAC
    interference with thrombophilia testing), fetched before the same-article PMC link rule; likewise Imazio 2012
    (colchicine-recurrent-pericarditis) and Cheema 2024 (CAP). Such text is refused unless PubMed->PMC proves an own link.
(1) Identical membership is not identical inputs: 6 of 6 trials shared by name, but Hokusai-VTE enters van Es with its
    ON-TREATMENT counts and ours with the overall-study result -- recorded per trial on population / outcome / window /
    analysis set.
(2) Positive control: van Es's recurrence meta-analysis reproduced by our engine -> RR 0.901688 (0.766115-1.061252),
    tau2 0, Q 4.155222, conditional on the one row that is not held.
(3) The comparator's scope (phase 3 only; phase II dose-finding excluded) never becomes our eligibility rule.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import comparator_panel, held_text_identity as hti, outcome_match as om, positive_control as pc, screen  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "doac-vte-recurrence"


def _served():
    return json.load(open(ROOT / "docs/reviews" / SLUG / "review.json", encoding="utf-8"))


# ---------------------------------------------------------------- (0) held text identity
@pytest.mark.parametrize("slug", ["doac-vte-recurrence", "colchicine-recurrent-pericarditis", "corticosteroids-cap-mortality"])
def test_a_citing_articles_text_is_refused(slug):
    recs = json.load(open(ROOT / "cache" / slug / "records.json", encoding="utf-8"))
    assert recs["comparator_fulltext"], "the misfiled bytes are still in the cache; the refusal must hold"
    out = hti.sanitize(str(ROOT), slug, recs)
    assert out["comparator_fulltext"] == "" and out["comparator_fulltext_identity"]["state"] == hti.REFUSED


def test_served_doac_page_discloses_the_refusal():
    c = _served()["comparator"]
    assert c["fulltext_identity"]["state"] == hti.REFUSED
    html = open(ROOT / "docs/reviews" / SLUG / "index.html", encoding="utf-8").read()
    assert "Held comparator full text refused" in html


def test_PLANT_identity_rules(tmp_path):
    slug = "__control_identity"
    (tmp_path / "cache" / slug).mkdir(parents=True)
    recs = {"comparator_pmid": "1", "comparator_fulltext": "some text"}
    assert hti.comparator_text_state(str(tmp_path), slug, recs)["state"] == hti.REFUSED        # no proof -> refused
    p = tmp_path / "cache" / slug / "pmc_links.json"
    p.write_text(json.dumps({"pmid": "1", "state": "NO_OWN_PMC_LINK", "own_pmcid": None}), encoding="utf-8")
    assert hti.comparator_text_state(str(tmp_path), slug, recs)["state"] == hti.REFUSED
    p.write_text(json.dumps({"pmid": "2", "state": "OWN_PMC_LINK", "own_pmcid": "9"}), encoding="utf-8")
    assert hti.comparator_text_state(str(tmp_path), slug, recs)["state"] == hti.REFUSED        # proof for another PMID
    p.write_text(json.dumps({"pmid": "1", "state": "OWN_PMC_LINK", "own_pmcid": "9"}), encoding="utf-8")
    assert hti.comparator_text_state(str(tmp_path), slug, recs)["state"] == "OWN_TEXT"


def test_PLANT_a_panel_cannot_name_the_refused_bytes_as_its_held_document(tmp_path):
    slug = "__control_panel"
    d = tmp_path / "cache" / slug
    d.mkdir(parents=True)
    raw = json.dumps({"comparator_pmid": "1", "comparator_fulltext": "citing article"})
    (d / "records.json").write_text(raw, encoding="utf-8")
    (d / "pmc_links.json").write_text(json.dumps({"pmid": "1", "state": "NO_OWN_PMC_LINK"}), encoding="utf-8")
    import hashlib
    panel = [{"id": "1", "citation": "x", "scope_note": "x", "held": True, "document_ref": f"cache/{slug}/records.json",
              "document_field": "comparator_fulltext", "document_sha256": hashlib.sha256(raw.encode()).hexdigest(),
              "trial_set": [], "k": None, "effect": None, "ci": None, "i2": None, "pi": None, "method": None}]
    (d / "comparators.json").write_text(json.dumps(panel), encoding="utf-8")
    with pytest.raises(ValueError, match="not the comparator's own text"):
        comparator_panel.attach(slug, {"outcomes": []}, tmp_path)


# ---------------------------------------------------------------- (1) outcome-level matching
def test_identical_membership_is_not_identical_inputs():
    m = _served()["comparator"]["shared_trial_inputs"]
    assert (m["shared_by_name"], m["input_identical"], m["input_different"], m["not_established"]) == (6, 5, 1, 0)
    hok = next(t for t in m["trials"] if t["name"] == "Hokusai-VTE")
    assert hok["inputs"] == "INPUT_DIFFERENT"
    assert hok["dimensions"]["window"] == {"state": "DIFFERENT", "ours": "OVERALL_STUDY_12_MONTHS", "theirs": "ON_TREATMENT",
                                           "theirs_evidence": "REPORTED_NOT_HELD"}
    assert hok["dimensions"]["analysis_set"]["state"] == "DIFFERENT"
    assert hok["theirs_counts"] == {"events_int": 66, "n_int": 4118, "events_ctl": 80, "n_ctl": 4122}


def test_PLANT_a_quote_not_in_the_held_bytes_is_refused(tmp_path, monkeypatch):
    doc = json.loads((ROOT / "cache" / SLUG / "comparator_member_inputs.json").read_text(encoding="utf-8"))
    doc["trials"][0]["theirs"]["sources"][0]["quote"] = doc["trials"][0]["theirs"]["sources"][0]["quote"].replace("30 of", "31 of")
    with pytest.raises(om.InputsRefused, match="quote not located"):
        for src in doc["trials"][0]["theirs"]["sources"]:
            om.check_source(ROOT, src)


def test_PLANT_a_registry_cell_with_another_value_is_refused():
    src = copy.deepcopy(json.loads((ROOT / "cache" / SLUG / "comparator_member_inputs.json").read_text(encoding="utf-8"))
                        ["trials"][2]["theirs"]["sources"][1])
    src["value"] = "1730"
    with pytest.raises(om.InputsRefused, match="registry cell"):
        om.check_source(ROOT, src)


def test_PLANT_our_side_must_be_the_served_row():
    doc = om.load(ROOT, SLUG)
    doc = copy.deepcopy(doc)
    doc["trials"][0]["ours"]["effect"] = 1.11
    with pytest.raises(om.InputsRefused, match="not the served row"):
        om.compare(doc, _served())


def test_PLANT_a_not_held_side_can_show_a_difference_but_never_an_equality():
    doc = copy.deepcopy(om.load(ROOT, SLUG))
    hok = next(t for t in doc["trials"] if t["name"] == "Hokusai-VTE")
    hok["theirs"]["window"]["value"] = hok["ours"]["window"]["value"]
    got = next(t for t in om.compare(doc)["trials"] if t["name"] == "Hokusai-VTE")
    assert got["dimensions"]["window"]["state"] == "NOT_ESTABLISHED"


# ---------------------------------------------------------------- (2) positive control
def test_van_Es_reproduced_by_our_engine_conditional_on_the_not_held_row():
    c = {x["id"]: x for x in pc.load(ROOT)}["van-es-2014-doac-vte-recurrence"]
    got = pc.reproduce(c, ROOT)
    assert pc.compare(c, got) == []
    assert abs(got["Q"] - 4.155222) < 5e-7 and got["tau2"] == 0.0
    assert got["conditional_on"] == ["Hokusai-VTE"]              # never an unconditional pass


def test_the_analysis_set_difference_moves_the_comparator_pool():
    # the comparator's pool with OUR held Hokusai row: fully held, and not the published number
    c = copy.deepcopy({x["id"]: x for x in pc.load(ROOT)}["van-es-2014-doac-vte-recurrence"])
    c["rows_from"]["use_ours_for"] = ["Hokusai-VTE"]
    got = pc.reproduce(c, ROOT)
    assert got["conditional_on"] == []
    assert [round(x, 6) for x in got["CE"]] == [0.913907, 0.78938, 1.05808]
    assert pc.compare(c, got)                                    # a real input difference, not rounding


# ---------------------------------------------------------------- (3) comparator scope does not leak
def test_the_comparators_phase_restriction_is_not_our_eligibility_rule():
    cfg = json.load(open(ROOT / "topics" / f"{SLUG}.json", encoding="utf-8"))
    assert "phase" not in json.dumps(cfg["include"]).lower()
    rec = {"id": "__control_phase2_dose_finding", "id_type": "pmid", "year": 2008,
           "title": "A randomized phase II dose-finding study of rivaroxaban versus enoxaparin followed by warfarin in "
                    "acute symptomatic deep vein thrombosis",
           "abstract": "In this randomized, double-blind, dose-finding phase II trial, patients with acute symptomatic deep "
                       "vein thrombosis were randomized to rivaroxaban at one of three doses or to enoxaparin followed by "
                       "warfarin (vitamin K antagonist) for 12 weeks. The primary outcome was recurrent venous "
                       "thromboembolism.", "pubtypes": ["Randomized Controlled Trial", "Clinical Trial, Phase II"]}
    d = screen.run([rec], cfg)["decisions"][0]
    assert d["decision"] == "include", d


def test_no_served_exclusion_cites_phase():
    import re
    rows = _served()["screening"]["records"]
    assert not [r for r in rows if r.get("decision") == "exclude" and re.search(r"(?i)\bphase (?:ii|2)\b|dose[- ]finding",
                                                                                 str(r.get("reason") or ""))]


def test_the_comparator_scope_is_recorded_as_the_comparators():
    s = _served()["comparator"]["shared_trial_inputs"]["comparator_scope"]
    assert s["statement"]["quote"].startswith("We included the phase 3 trials") and "not an eligibility rule" in s["applies_to"]


def test_the_second_pass_outcome_match_is_not_overwritten():
    # the shared-trial comparison lives under its own key; comparator.outcome_match is comparator_second_pass's field
    c = _served()["comparator"]
    assert c["outcome_match"] == {"status": "NEAR_MATCH",
                                  "note": "recurrent VTE composite; trial definitions differ on VTE-related death"}
    assert c["shared_trial_inputs"]["shared_by_name"] == 6
