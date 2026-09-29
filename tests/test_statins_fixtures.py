"""Statins-older-adults fixtures, 2026-09-28: an investigator subgroup report is never an input, ALLHAT is one family
with collection-scoped harms, JUPITER >=70 harms are published HRs never summed (plants included)."""
import copy
import json
import os

from harness import (collection_scope as cs, fetch, multi_trial_report as mtr, pipeline, result_status as rs)

ROOT = pipeline.ROOT
SLUG = "statins-primary-prevention-elderly"
MVE, MUS, DM = "Major vascular events", "Muscle symptoms/myopathy", "New-onset diabetes"
_R = {}


def _cfg():
    return dict(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8")), slug=SLUG)


def _rv():
    if not _R:
        cfg = _cfg()
        _R["rv"] = pipeline.build_review_core(SLUG, cfg, fetch.ensure(cfg, ""), "test")
    return _R["rv"]


def _o(rv, name):
    return next(o for o in rv["outcomes"] if o["name"] == name)


def _row(o, pid, pooled):
    return next(t for t in (o["trials"] if pooled else o["declared_absent_trials"]) if pid in str(t["id"]))


def test_ridker_is_a_report_of_two_trials_its_pool_never_an_input_and_hope3_is_relayed():
    rv = _rv()
    r = next(m for m in rv["multi_trial_reports"] if m["report_id"] == "PMID 28385949")
    assert {t["label"]: t["relevant"] for t in r["trials"]} == {"JUPITER (>= 70)": True, "HOPE-3 (>= 70)": True}
    assert {c["policy"] for c in r["combined_analyses"]} == {"NEVER_IMPORTED"}
    o = _o(rv, MVE)
    assert len(o["trials"]) == 2 and round(o["result"]["estimate"], 4) == 0.6803        # served pool unchanged
    assert not any("28385949" in str(t["id"]) or "NCT00468923" in str(t["id"]) for t in o["trials"])
    # JUPITER >=70 3-point MACE is a DIFFERENT outcome record: relayed beside the served composite, never substituted
    j = _row(o, "20404379", True)
    assert (j["effect"], j["ci_low"], j["ci_high"]) == (0.61, 0.46, 0.82)
    assert "0.61 (0.43-0.86)" in j["relayed_not_held"]["value"]
    k = json.load(open(os.path.join(ROOT, "docs", "known_eligible_missing.json"), encoding="utf-8"))["topics"][SLUG]
    h = next(e for e in k if e["registration"] == "NCT00468923")
    assert "FACTORIAL" in h["design"] and "0.83 (0.64-1.07)" in h["design_note"]
    # PLANT: the letter's pooled estimate entered as a trial row is refused
    rv2 = copy.deepcopy(rv)
    _o(rv2, MVE)["trials"].append({"id": "PMID 28385949", "effect": 0.74})
    assert "COMBINED_POPULATION_IMPORTED" in [p["kind"] for p in mtr.problems(rv2)]


def test_allhat_is_one_family_rmst_is_never_an_hr_and_its_coronary_hr_is_not_mve():
    rv = _rv()
    scr = {str(r["id"]).split("·")[-1].strip(): r for r in rv["screening"]["records"]}
    assert scr["30251369"]["rule_id"] == "X-DEDUP"                                   # Orkaby: the SAME trial
    for o in rv["outcomes"]:
        assert not any("30251369" in str(t["id"]) for t in (o.get("trials") or []) + (o.get("declared_absent_trials") or []))
    a = _row(_o(rv, MVE), "28531241", False)
    assert a["result_status"]["state"] == "EXTRACTED_NOT_ADMITTED"
    assert a["held_out_row"]["effect"] == 0.70 and "without stroke" in a["not_admitted_because"]
    assert "1.34 (0.98-1.84)" in a["reason"]                                         # mortality named, never substituted


def test_allhat_harms_were_not_systematically_collected_never_zero():
    rv = _rv()
    for name in (MUS, DM):
        row = _row(_o(rv, name), "28531241", False)
        assert row["result_status"]["state"] == "NOT_SYSTEMATICALLY_COLLECTED"
    # PLANT: an ALLHAT harm row entering a pool is refused
    rv2 = copy.deepcopy(rv)
    o = _o(rv2, MUS)
    row = _row(o, "28531241", False)
    o["trials"].append(dict(row, ai=1, n1i=10, ci=1, n2i=10))
    assert "COLLECTION_SCOPE_POOLED" in [p["kind"] for p in cs.problems(rv2)]


def test_jupiter_older_harms_are_published_hrs_and_myopathy_is_never_summed():
    rv = _rv()
    m = _row(_o(rv, MUS), "20404379", True)
    assert (m["effect"], m["ci_low"], m["ci_high"], m["scale"]) == (1.04, 0.92, 1.19, "HR")
    assert m["harm_definition_key"] == "MUSCLE_SYMPTOMS" and m.get("ai") is None       # no counts summed with myopathy
    d = _row(_o(rv, DM), "20404379", True)
    assert (d["effect"], d["ci_low"], d["ci_high"], d["scale"]) == (1.25, 0.90, 1.74, "HR")


def test_an_author_manuscript_is_identified_by_its_declared_pmid_not_its_title():
    from harness import source_identity as si
    page = os.path.join(ROOT, "evidence", "acquisition_cascade", "held", "JUPITER-older", "pmc_article.html")
    if not os.path.exists(page):                       # held locally only (not redistributed)
        return
    # the NIH manuscript's pre-publication title differs from the record's; its declared PMID is the record's
    assert si.check_held_document(page, {"pmid": "20404379", "title": "Rosuvastatin ... older persons ..."}) is None
    # PLANT: the same page against another record fails, whatever the titles say
    assert "declares PMID 20404379" in si.check_held_document(page, {"pmid": "99999999", "title": "Rosuvastatin"})
    # PLANT: a one-word 'title' is contained in any title and must never establish identity
    xml = os.path.join(ROOT, "evidence", "acquisition_cascade", "held", "EMPA-KIDNEY-followup", "PMC7616743.xml")
    assert si.check_held_document(xml, {"title": "x"}) is not None


# ------------------------------------------------------------------------------------------------ addendum
def test_the_endpoint_policy_is_recorded_and_a_pending_3_point_input_is_blocked():
    from harness import endpoint_policy as ep
    rv = _rv()
    o = _o(rv, MVE)
    pol = o["result"]["endpoint_policy"]
    assert pol["policy"]["id"] == "TRIAL_DEFINED_BROAD_COMPOSITE"
    assert all(t.get("component_set") for t in o["trials"])                 # every served input typed
    hope = next(p for p in pol["pending"] if p["input"] == "NCT00468923")
    assert hope["state"] == "DECISION_REQUIRED_BEFORE_INTERVAL" and "3-POINT" in hope["mismatch"]
    assert ep.problems(rv) == []
    # PLANT: HOPE-3 pooled before a recorded decision is refused
    rv2 = copy.deepcopy(rv)
    _o(rv2, MVE)["trials"].append({"id": "NCT00468923", "effect": 0.83, "ci_low": 0.64, "ci_high": 1.07})
    assert [p["kind"] for p in ep.problems(rv2)] == ["ENDPOINT_POLICY_VIOLATION"]


def test_preventable_is_eligible_with_typed_status_axes_and_adds_nothing_to_k():
    rv = _rv()
    scr = next(r for r in rv["screening"]["records"] if "NCT04262206" in str(r["id"]))
    assert scr["decision"] == "include"
    fam = next(f for f in rv["trial_families"] if f["family_id"] == "NCT04262206")
    assert fam["eligibility"]["state"] == "ELIGIBLE"
    assert {o["name"]: o["result"].get("k") for o in rv["outcomes"]} == {MVE: 2, MUS: 1, DM: 1}   # k unchanged
    for o in rv["outcomes"]:
        row = _row(o, "NCT04262206", False)
        ax = row["status_axes"]
        assert ax["eligibility"].startswith("ELIGIBLE")
        assert ax["recruitment_completion"]["registry_status"] == "RECRUITING"
        assert ax["publication"] == "NO_PUBLICATION_IN_INVENTORY" and ax["target_outcome"] == "NO_RESULT_YET"
        assert "abstract" not in row["reason"]                               # the generic extractor phrase is gone
    km = _o(rv, MVE).get("known_missing_sensitivity") or {}
    assert not any("NCT04262206" in str(r.get("trial_key")) for r in km.get("rows") or [])  # never a missing HR
    assert [x["trial"] for x in km.get("not_yet_reportable") or []] == ["NCT04262206"]


# (the declared condition-label exemption was withdrawn: the rule is DERIVED from each registration's own criteria --
#  harness/registry_criteria.py; its plants live in tests/test_statins_extractors.py)


def test_the_search_is_labelled_not_demonstrated_complete():
    rv = _rv()
    comp = rv["scope_identity"]["search_scope"]["completeness"]
    assert comp["state"] == "NOT_DEMONSTRATED_COMPLETE"
    from harness import scope_identity as si
    assert "Search completeness: NOT DEMONSTRATED" in si.rendered_block(rv["scope_identity"])
