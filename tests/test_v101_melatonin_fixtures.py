"""V1.0.1 plants from the melatonin review (comparator: Ferracioli-Oda 2013, PLoS One, PMID 23691095).

(1) SCOPE: 19 studies in adults AND children with primary sleep disorders (14 insomnia, 4 delayed sleep phase, 1 REM
    sleep behaviour), 15 in the latency plot -- 'k 19 vs our 1' is never 18 missing trials; the stated k is read.
(2) only_ours is computed from the POOLED set (Wade), never from the screened inventory (live main listed Xu 33157425
    and the cancer study 27559258).
(3) Wade: one trial at identity level (NCT00397189), different inputs (all adults, PSQI-Q2 vs our 65-80 diary SOL).
(4) DISPLAY vs CALCULATION: swapped row weights (Smits 2003 / Almeida Montes) and the figure's objective-subgroup
    interval (7.81 vs 8.71 in the text and the reconstruction) are COMPARATOR_DISPLAY_ERROR; the pooled calculation
    reproduces (FE 7.0606, 4.38-9.74 vs 7.06, 4.37-9.75) and is a positive control.
(5) '"melatonin"[Title]' is a concept query, not known-item seeding.
(6) The cancer-insomnia study enrolled DSM-IV primary insomnia: 'cancer' does not exclude it; its Athens Insomnia Scale
    is never converted to minutes.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import comparator_display as cd, positive_control as pc  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "melatonin-primary-insomnia-sol"


def _served():
    return json.load(open(ROOT / "docs/reviews" / SLUG / "review.json", encoding="utf-8"))


def _html():
    return (ROOT / "docs/reviews" / SLUG / "index.html").read_text(encoding="utf-8")


# (1) scope and stated k
def test_the_comparators_stated_count_is_read_and_its_scope_is_stated():
    c = _served()["comparator"]
    st = c["overlap_relation"]["theirs_k_stated"]
    assert st["value"] == 19 and "Nineteen studies" in str(st["source"])
    sc = c["display_check"]["scope"]
    assert "four studies on delayed sleep phase syndrome" in sc["stated_total"]["quote"]
    assert "Adults and children" in sc["population"]["quote"] and sc["outcome_rows"]["k"] == 15
    assert "not a list of trials missing from ours" in _html()


# (2) only_ours from the pooled set
def test_only_ours_is_computed_from_the_pooled_set_not_the_screened_inventory():
    o = _served()["comparator"]["overlap_relation"]
    assert o["ours_k"] == 1 and o["shared"] == ["NCT00397189"] and o["only_ours"] == []
    screened_in = {r["id"] for r in _served()["screening"]["records"] if r["decision"] == "include"}
    assert {"33157425", "27559258"} <= screened_in                    # screened in, not pooled: never 'only ours'


# (3) Wade: identity-level match, different inputs
def test_Wade_is_one_trial_with_different_inputs():
    m = _served()["comparator"]["shared_trial_inputs"]
    t = m["trials"][0]
    assert t["family_id"] == "NCT00397189" and t["inputs"] == "INPUT_DIFFERENT"
    assert t["dimensions"]["population"]["state"] == "DIFFERENT"
    assert t["dimensions"]["outcome_definition"]["theirs"] == "PSQI_Q2_SLEEP_LATENCY"


# (4) display vs calculation
def test_display_errors_are_flagged_and_the_calculation_reproduces():
    a = _served()["comparator"]["display_check"]
    kinds = {x["kind"]: x for x in a["display_errors"]}
    assert kinds["ROW_WEIGHTS_SWAPPED"]["rows"] == ["Smits MG, 2003", "Almeida Montes LG, 2002"]
    fp = kinds["FIGURE_POOL_DISAGREES"]
    assert fp["pool"] == "Objective" and fp["figure"][2] == 7.81 and fp["text"][2] == 8.71 and fp["text_agrees_with_reconstruction"]
    assert a["calculation"]["state"] == "CALCULATION_REPRODUCED"
    assert a["calculation"]["reconstructed"][0] == pytest.approx(7.0606, abs=5e-5)
    assert "COMPARATOR_DISPLAY_ERROR" in _html()


def test_PLANT_unswapped_weights_leave_no_row_error_and_a_moved_row_breaks_the_calculation():
    doc = cd.load(ROOT, SLUG)
    ok = copy.deepcopy(doc)
    rows = {r["label"]: r for r in ok["rows"]}
    rows["Smits MG, 2003"]["printed_weight_pct"], rows["Almeida Montes LG, 2002"]["printed_weight_pct"] = 0.29, 3.94
    assert not [x for x in cd.assess(ok)["display_errors"] if x["kind"].startswith("ROW_")]
    bad = copy.deepcopy(doc)
    for k in ("effect", "ci_low", "ci_high"):                           # Kayumov shifted by 5 minutes, interval too
        bad["rows"][2][k] += 5
    assert cd.assess(bad)["calculation"]["state"] == "CALCULATION_NOT_REPRODUCED"


def test_the_pooled_calculation_is_a_positive_control_of_our_engine():
    c = next(c for c in pc.load(ROOT) if c["id"] == "ferracioli-oda-2013-melatonin-sleep-latency")
    got = pc.reproduce(c, ROOT)
    assert pc.compare(c, got) == [] and got["k"] == 15
    moved = dict(c, expected={"CE": [7.30, 4.37, 9.75]})
    assert pc.compare(moved, got)


# (5) search classifier
def test_a_title_field_concept_is_not_known_item_seeding():
    from harness.pipeline import classify_query
    assert classify_query('"melatonin"[Title] AND insomnia AND placebo') == "TITLE_RESTRICTED_CONCEPT"
    kinds = {b["kind"] for b in _served()["search"]["retrieval_class"]["basis"]}
    assert "TITLE_ANCHORED" not in kinds


# (6) population witness and the Athens Insomnia Scale
def test_the_cancer_insomnia_study_enrolled_primary_insomnia_and_is_not_excluded():
    from harness import population_witness as pw
    cfg = json.load(open(ROOT / "topics" / f"{SLUG}.json", encoding="utf-8"))
    recs = json.load(open(ROOT / "cache" / SLUG / "records.json", encoding="utf-8"))["records"]
    rec = next(r for r in recs if str(r.get("id")) == "27559258")
    fam = {"family_id": "PMID:27559258", "population": {}, "reports": [{"report_id": "27559258", "role": "PRIMARY"}],
           "source_records": [rec]}
    assert pw.decide(fam, cfg)["state"] == "ESTABLISHED"
    veto = copy.deepcopy(cfg)
    veto["include"]["population_none"] = veto["include"]["population_none"] + ["cancer"]
    assert pw.decide(fam, veto)["state"] != "EXCLUDED"                  # 'cancer' alone never excludes primary insomnia


def test_the_Athens_Insomnia_Scale_is_never_converted_to_minutes():
    prim = next(o for o in _served()["outcomes"] if o.get("primary"))
    row = next(t for t in prim["declared_absent_trials"] if "27559258" in str(t.get("id")))
    assert "Athens" in json.dumps(row) and "never converted to minutes" in json.dumps(row)
    assert "27559258" not in {str(t.get("label")) for t in prim["trials"]}
