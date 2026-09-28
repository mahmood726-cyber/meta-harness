"""Semaglutide (MACE + weight), SGLT2-CKD, SGLT2-HFrEF and ticagrelor fixtures, 2026-09-28 (plants included)."""
import copy
import json
import os
import sys

import pytest

from harness import (collection_scope as cs, family_invariant as fi, fetch, lifecycle, outcome_restriction as orx, pipeline,
                     registry_publications as rp, result_status as rs, screen, source_identity as si,
                     source_versions as sv)

ROOT = pipeline.ROOT
_R = {}


def _rv(slug):
    if slug not in _R:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        _R[slug] = pipeline.build_review_core(slug, cfg, fetch.ensure(cfg, ""), "test")
    return _R[slug]


def _o(rv, name):
    return next(o for o in rv["outcomes"] if o["name"] == name)


def _row(rv, outcome, pid, pooled=False):
    o = _o(rv, outcome)
    return next(t for t in (o["trials"] if pooled else o["declared_absent_trials"]) if pid in str(t["id"]))


# ------------------------------------------------------------------------------------------------ semaglutide MACE
SM = "semaglutide-obesity-mace"


def test_select_any_gi_event_is_not_systematically_collected_never_zero_never_summed():
    rv = _rv(SM)
    g = _row(rv, "Gastrointestinal adverse events", "37952131")
    assert g["result_status"]["state"] == rs.NOT_SYSTEMATICALLY_COLLECTED
    assert "systematically recorded" in g["result_status"]["span"]
    # PLANT: the GI outcome pooled for SELECT anyway -> blocking
    rv2 = copy.deepcopy(rv)
    _o(rv2, "Gastrointestinal adverse events")["trials"].append(dict(g, ai=1222, n1i=8803, ci=495, n2i=8801))
    assert "COLLECTION_SCOPE_POOLED" in [p["kind"] for p in cs.problems(rv2)]
    # PLANT: manufactured by summing the serious-GI and GI-discontinuation rows -> blocking
    rv3 = copy.deepcopy(rv)
    _o(rv3, "Serious gastrointestinal adverse events")["trials"].append(
        {"id": "PMID 37952131", "ai": 342 + 880, "n1i": 8803, "ci": 323 + 172, "n2i": 8801, "components_summed": True})
    assert "COMPONENT_SUM_AS_COMPOSITE" in [p["kind"] for p in orx.problems(rv3)]


def test_select_table4_rows_are_their_own_outcomes_and_mace_is_unchanged():
    rv = _rv(SM)
    for outcome, a, c in (("Serious adverse events", 2941, 3204), ("Serious gastrointestinal adverse events", 342, 323),
                          ("Gastrointestinal adverse events leading to permanent discontinuation", 880, 172)):
        t = _row(rv, outcome, "37952131", pooled=True)
        assert (t["ai"], t["n1i"], t["ci"], t["n2i"]) == (a, 8803, c, 8801)
    m = _row(rv, "3-point major adverse cardiovascular events", "37952131", pooled=True)
    assert (m["effect"], m["ci_low"], m["ci_high"]) == (0.8, 0.72, 0.9)   # the 2025 safety paper supersedes nothing here


def test_hba1c_analysis_is_a_secondary_report_of_select_and_the_family_is_source_established():
    rv = _rv(SM)
    s = next(x for x in rv["screening"]["records"] if x["id"] == "38907684")
    assert s["rule_id"] == "X-DEDUP"
    assert not any("38907684" in str(t["id"]) for o in rv["outcomes"] for t in o["trials"])     # subgroup HRs never pooled
    f = next(x for x in rv["trial_families"] if x["family_id"] == "NCT03574597")
    assert f["eligibility"]["state"] == "ELIGIBLE" and f["eligibility"]["span"]["population_basis"] == "SOURCE_WITNESS"
    assert rv["family_count_chain"]["contributing_without_structural_eligibility"] == []


def test_a_future_start_is_never_completed():
    assert lifecycle.lifecycle({"overall_status": "COMPLETED", "completion_date": "2020-01-01", "start_date": "2026-10-01"},
                               "2026-09-28")["state"] == "CONFLICT"                         # PLANT
    assert lifecycle.lifecycle({"overall_status": "COMPLETED", "completion_date": "2020-01-01", "start_date": "2015-10-01"},
                               "2026-09-28")["state"] == "COMPLETED"


# ------------------------------------------------------------------------------------------------ semaglutide weight
SW = "semaglutide-obesity-weight"


def test_step_10_and_11_are_available_at_their_own_timepoints_not_missing_week_68():
    rv = _rv(SW)
    c = next(x for x in rv["completeness_by_outcome"] if x["outcome"] == "Percent change in body weight")
    st = {f["family"]: f["state"] for f in c["families"]}
    assert st["40825340"] == "AVAILABLE_AT_OTHER_TIMEPOINT" and "week 44" in _row(rv, "Percent change in body weight", "40825340")["timepoint_availability"]["available"]
    assert st["STEP 10 · NCT05040971"] == "AVAILABLE_AT_OTHER_TIMEPOINT"


def test_step_8_is_decided_per_comparison_and_step_4_stays_excluded():
    rv = _rv(SW)
    s = next(x for x in rv["screening"]["records"] if "NCT04074161" in x["id"])
    assert s["decision"] == "include" and "comparison-level" in s["reason"]
    cfg = json.load(open(os.path.join(ROOT, "topics", SW + ".json"), encoding="utf-8"))
    step4 = {"id": "33755728", "id_type": "pmid", "pubtypes": ["Randomized Controlled Trial"], "abstract": "",
             "title": ("Effect of Continued Weekly Subcutaneous Semaglutide vs Placebo on Weight Loss Maintenance in Adults "
                       "With Overweight or Obesity: The STEP 4 Randomized Clinical Trial")}
    dec = screen.screen_record(step4, cfg["include"], cfg.get("negative_terms") or [])
    assert dec[0] == "exclude"                                                         # PLANT: an initiation question


def test_gi_aggregates_are_patients_with_windows_never_events_never_symptom_sums():
    rv = _rv(SW)
    got = {t["id"]: (t["ai"], t["n1i"], t["ci"], t["n2i"], t["safety_window"]) for t in _o(rv, "Gastrointestinal adverse events")["trials"]}
    assert got["PMID 33567185"][:4] == (969, 1306, 314, 655) and got["PMID 33625476"][:4] == (337, 407, 129, 204)
    assert got["NCT04074161"][:4] == (106, 126, 47, 85) and all("49 days" in v[4] for v in got.values())
    # PLANT: STEP 1's EVENTS column (4309 vs 739) read as patients -> blocking
    rv2 = copy.deepcopy(rv)
    t = next(t for t in _o(rv2, "Gastrointestinal adverse events")["trials"] if t["id"] == "PMID 33567185")
    t.update(ai=4309, ci=739)
    assert "COUNT_EXCEEDS_DENOMINATOR" in [p["kind"] for p in orx.problems(rv2)]
    # the non-pooled trials that DO report GI events stay 'reported'
    assert _row(rv, "Gastrointestinal adverse events", "40825340")["result_status"]["state"] == rs.REPORTED_UNRESOLVED


# ------------------------------------------------------------------------------------------------ SGLT2-CKD
SC = "sglt2-ckd-progression"


def test_source_identity_fails_when_identifiers_resolve_to_different_publications():
    rec = si.record_identity(os.path.join(ROOT, "evidence/acquisition_cascade/held/EMPA-KIDNEY/europepmc_record_36331190.json"))
    assert si.check_citation({"pmid": "36331190", "pmcid": "PMC9761906"}, rec)                     # PLANT: the starfish paper
    assert si.check_citation({"pmid": "36331190", "pmcid": "PMC7614055", "doi": "10.1056/NEJMoa2204233"}, rec) == []
    assert si.check_citation({"pmid": "36331190", "doi": "10.1002/ejhf.2084"}, rec)                 # PLANT: another DOI
    r = si.ledger_check()
    assert r["mismatch"] == []                                  # every present held article is its record's publication


def test_the_cascade_quarantines_what_a_wrong_doi_fetched(tmp_path, monkeypatch):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import acquisition_cascade as ac
    monkeypatch.setattr(ac, "D", str(tmp_path))
    monkeypatch.setattr(ac, "HELD", str(tmp_path / "held"))
    monkeypatch.setattr(ac, "ATTEMPTS", str(tmp_path / "ATTEMPTS.jsonl"))
    upw = json.dumps({"oa_locations": [{"url": "https://example.org/wrong.pdf", "host_type": "repository"}]}).encode()
    rec = json.dumps({"resultList": {"result": [{"pmid": "1", "doi": "10.1/right", "isOpenAccess": "N", "title": "t"}]}}).encode()

    def fake_get(url, accept=None):
        if "unpaywall" in url:
            return 200, upw
        if "wrong.pdf" in url:
            return 200, b"%PDF-1.4 another paper"
        if "search?" in url:
            return 200, rec
        return 404, b""
    monkeypatch.setattr(ac, "_get", fake_get)
    t = tmp_path / "t.json"
    t.write_text(json.dumps({"topic": "x", "drug": "", "indication": "", "skip_regulatory": True,
                             "trials": [{"trial": "T", "pmid": "1", "doi": "10.1/WRONG", "aliases": []}]}), encoding="utf-8")
    ac.main(["fetch", "--targets", str(t)])
    rows = [json.loads(l) for l in open(tmp_path / "ATTEMPTS.jsonl", encoding="utf-8")]
    assert any(r["status"] == "IDENTITY_MISMATCH" for r in rows)
    led = json.load(open(tmp_path / "held" / "HELD.json", encoding="utf-8"))
    assert led["T/unpaywall.pdf"].get("identity_quarantine")


def test_ckd_safety_rows_carry_their_own_windows_and_definitions():
    rv = _rv(SC)
    dka = _o(rv, "Diabetic ketoacidosis")
    assert dka["result"]["suppressed_incompatible"] and set(dka["result"]["definition_strata"]) == {
        "DKA_ADJUDICATED", "KETOACIDOSIS_ANY_INCL_NONDIABETIC"}
    dapa = _row(rv, "Diabetic ketoacidosis", "32970396", pooled=True)
    assert (dapa["ai"], dapa["ci"]) == (0, 2) and "0.5" in dapa["continuity_correction"]
    assert dka["result"]["sparse_data_method"]["rows"] == ["PMID 32970396"]      # the method, declared for the outcome
    cr_dka = _row(rv, "Diabetic ketoacidosis", "30990260", pooled=True)
    cr_amp = _row(rv, "Lower-limb amputation", "30990260", pooled=True)
    assert "ON-TREATMENT" in cr_dka["safety_window"] and "ON-STUDY" in cr_amp["safety_window"]   # differs WITHIN a trial
    assert (cr_amp["ai"], cr_amp["n1i"], cr_amp["ci"], cr_amp["n2i"]) == (70, 2200, 63, 2197)


def test_empa_kidney_follow_up_is_a_separate_policy_never_a_silent_replacement():
    rv = _rv(SC)
    row = _row(rv, "Trial-defined primary cardiorenal composite", "36331190", pooled=True)
    ch = row["version_chain"]
    assert ch["governing"]["state"] == "DECIDED" and ch["governing"]["version_id"] == "v0-active-trial-2022"
    assert "SEPARATE FOLLOW-UP POLICY" in ch["versions"][1]["relation"]
    rv2 = copy.deepcopy(rv)
    r2 = _row(rv2, "Trial-defined primary cardiorenal composite", "36331190", pooled=True)
    r2.update(effect=0.79, ci_low=0.72, ci_high=0.87)                                  # PLANT: silent replacement
    assert "VERSION_SUPERSEDED_SERVED" in [p["kind"] for p in sv.problems(rv2)]


def test_diamond_is_linked_and_its_crossover_sequences_are_never_parallel_arms():
    rv = _rv(SC)
    d = _row(rv, "Trial-defined primary cardiorenal composite", "NCT03190694")
    assert d["linked_publication"]["pmid"] == "32559474"
    rv2 = copy.deepcopy(rv)
    _o(rv2, "Diabetic ketoacidosis")["trials"].append({"id": "NCT03190694", "ai": 0, "n1i": 27, "ci": 0, "n2i": 26})  # PLANT
    assert "CROSSOVER_AS_PARALLEL" in [p["kind"] for p in rp.problems(rv2)]
    e = next(x for x in rv["screening"]["records"] if "NCT07060417" in x["id"])
    assert e["lifecycle"]["state"] != "COMPLETED"


# ------------------------------------------------------------------------------------------------ SGLT2-HFrEF
SH = "sglt2-hfref-hosp-cvdeath"


def test_define_hf_and_emperial_reduced_are_known_trials_with_no_target_outcome():
    rv = _rv(SH)
    km = _o(rv, "Composite cardiovascular death or hospitalisation for heart failure")["known_missing_sensitivity"]
    st = {r["trial_key"]: r["result_status"]["state"] for r in km["rows"] if r.get("result_status")}
    assert st["DEFINE-HF"] == st["EMPERIAL-Reduced"] == "PUBLISHED_NO_TARGET_OUTCOME"
    assert not any(k in ("DEFINE-HF", "EMPERIAL-Reduced") for o in rv["outcomes"] for k in [t["id"] for t in o["trials"]])


def test_dapa_hf_and_emperor_harms_are_reported_never_absent_never_remembered():
    rv = _rv(SH)
    for outcome in ("Volume depletion or hypotension", "Diabetic ketoacidosis"):
        d = _row(rv, outcome, "31535829")
        assert d["result_status"]["state"] == rs.REPORTED_UNRESOLVED and d["relayed_not_held"]
        e = _row(rv, outcome, "32865377")
        assert e["result_status"]["state"] == rs.REPORTED_UNRESOLVED and "Table S2" in e["result_status"]["span"]
        assert e.get("ai") is None                                                   # no counts from memory


# ------------------------------------------------------------------------------------------------ ticagrelor
def test_plato_diabetes_substudy_is_a_subgroup_report_with_one_design_decision():
    rv = _rv("ticagrelor-vs-clopidogrel-acs")
    s = next(x for x in rv["screening"]["records"] if x["id"] == "20802246")
    assert s["rule_id"] == "X-DEDUP"
    assert fi.problems(rv) == []


def test_a_held_whole_trial_row_has_the_same_shape_as_every_absent_row():
    # STEP 8 is the first included multi-comparison family: its whole-trial weight row is held out, and a held row
    # without a label crashed the build (every consumer reads t['label'])
    from harness import comparison_family as cf
    keep, held = cf.hold_whole_trial(None, "Percent change in body weight",
                                     [{"label": "STEP 8", "id": "NCT04074161", "effect": -10.0}])
    assert keep == [] and held and all(h.get("label") == "STEP 8" and h.get("absent_kind") for h in held)
