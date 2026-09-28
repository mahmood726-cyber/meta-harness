"""Sacubitril-HFrEF fixtures, 2026-09-28 (plants included)."""
import copy
import json
import os
import sys

from harness import (family_invariant as fi, fetch, outcome_restriction as orx, pipeline, registry_publications as rp,
                     result_status as rs)
from harness.synth import Study, pool

ROOT = pipeline.ROOT
SLUG = "sacubitril-valsartan-hfref"
PRIM = "Composite cardiovascular death or heart-failure hospitalization"
HYPO, HYPK = "Hypotension", "Hyperkalemia"
_R = {}


def _rv():
    if SLUG not in _R:
        cfg = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
        _R[SLUG] = pipeline.build_review_core(SLUG, cfg, fetch.ensure(cfg, ""), "test")
    return _R[SLUG]


def _o(rv, name):
    return next(o for o in rv["outcomes"] if o["name"] == name)


def test_life_is_a_known_eligible_trial_reported_but_not_pooled_on_relayed_values():
    rv = _rv()
    km = _o(rv, PRIM)["known_missing_sensitivity"]
    life = next(r for r in km["rows"] if r["trial_key"] == "LIFE")
    assert life["result_status"]["state"] == rs.REPORTED_UNRESOLVED and "eTable 4" in life["result_status"]["span"]
    assert "48/167 vs 37/168" in life["result_status"]["relayed_not_held"]["value"]
    for distinct in ("first HF hospitalisation HR 1.24", "61 vs 50 EVENTS", "335", "NOT all randomised"):
        assert distinct in life["design_note"] or distinct in json.dumps(life)
    assert not any("34730769" in str(t["id"]) or "NCT02816736" in str(t["id"]) for o in rv["outcomes"] for t in o["trials"])
    # the stated diagnostic reproduces (relayed values: a diagnostic, never served)
    S = lambda l, e, a, b: Study(label=l, effect=e, ci_low=a, ci_high=b, measure="HR")
    r3 = pool([S("PARADIGM", 0.80, 0.73, 0.87), S("PARALLEL", 1.0881, 0.6501, 1.8212), S("LIFE", 1.32, 0.86, 2.03)], scale="HR")
    assert (round(r3.estimate, 4), round(r3.ci_low, 4), round(r3.ci_high, 4)) == (0.9724, 0.5024, 1.882)


def test_prespecified_harms_are_recorded_with_typed_definitions_never_one_number_across_them():
    rv = _rv()
    for name, keys in ((HYPO, {"HYPOTENSION_AE_TERM_WITH_SBP_LT_90", "SYMPTOMATIC_HYPOTENSION"}),
                       (HYPK, {"SERUM_K_GE_5_5_LAB", "SERUM_K_GT_5_5_LAB"})):
        o = _o(rv, name)
        assert {t["harm_definition_key"] for t in o["trials"]} == keys
        assert o["result"]["suppressed_incompatible"] and o["result"].get("estimate") is None
        assert set(o["result"]["definition_strata"]) == keys
        para = next(t for t in o["declared_absent_trials"] if "25176015" in t["id"])
        assert para["result_status"]["state"] == rs.REPORTED_UNRESOLVED and para["relayed_not_held"]
    p = next(t for t in _o(rv, HYPO)["trials"] if t["id"] == "NCT02468232")
    assert (p["ai"], p["n1i"], p["ci"], p["n2i"]) == (13, 111, 5, 112) and "reconstructed" in p["effect_reconstructed_from_counts"]
    assert "mis-randomised" in p["safety_population"]
    k = next(t for t in _o(rv, HYPK)["trials"] if t["id"] == "NCT02468232")
    assert (k["ai"], k["n1i"], k["ci"], k["n2i"]) == (8, 111, 6, 112)


def test_definition_plants():
    rv = copy.deepcopy(_rv())
    o = _o(rv, HYPO)
    # PLANT: the suppression bypassed -> a mixed-definition pooled number is blocking
    o["result"] = {"k": 2, "estimate": 1.5, "scale": "RR"}
    assert "DEFINITION_MIX_POOLED" in [p["kind"] for p in orx.problems(rv)]
    # PLANT: one definition only -> nothing to refuse
    rv2 = copy.deepcopy(_rv())
    o2 = _o(rv2, HYPO)
    o2["trials"] = [t for t in o2["trials"] if t["id"] == "NCT02468232"]
    o2["result"] = {"k": 1, "estimate": 2.6, "scale": "RR"}
    assert orx.problems(rv2) == []


def test_parallel_publication_is_a_report_of_its_registry_family_with_one_design_decision():
    rv = _rv()
    scr = next(s for s in rv["screening"]["records"] if s["id"] == "33731544")
    assert scr["rule_id"] == "X-DEDUP"
    fam = next(f for f in rv["trial_families"] if f["family_id"] == "NCT02468232")
    assert {"33731544", "NCT02468232"} <= {r["report_id"] for r in fam["reports"]}
    assert not any(f["family_id"] == "PMID:33731544" for f in rv["trial_families"])
    assert fi.problems(rv) == []
    # PLANT: the publication excluded for its DESIGN while its family contributes -> blocking
    rv2 = copy.deepcopy(rv)
    s2 = next(s for s in rv2["screening"]["records"] if s["id"] == "33731544")
    s2.update(decision="exclude", rule_id="X-DESIGN", reason="not double-blind/placebo-controlled")
    assert "FAMILY_DESIGN_CONFLICT" in [p["kind"] for p in fi.problems(rv2)]


def test_pioneer_hf_reports_are_one_family_and_the_12_week_hr_is_never_the_8_week_contrast():
    rv = _rv()
    row = next(t for t in _o(rv, PRIM)["declared_absent_trials"] if t["id"] == "NCT02554890")
    assert row["linked_publication"]["pmid"] == "30415601"
    assert [r["pmid"] for r in row["linked_publication"]["reports"]] == ["30955360", "31825471"]
    assert row["result_status"]["state"] == rs.NOT_YET_RETRIEVED and "not extracted" in row["publication_statement"]
    assert rp.problems(rv) == []
    # PLANT: the extension's 12-week HR pooled as PIONEER-HF's primary result
    rv2 = copy.deepcopy(rv)
    span = rv2["registry_publications_not_this"][0]["span"]
    _o(rv2, PRIM)["trials"].append({"id": "NCT02554890", "effect": 0.69, "ci_low": 0.49, "ci_high": 0.97, "source_span": span})
    assert "WRONG_WINDOW" in [p["kind"] for p in rp.problems(rv2)]


def test_the_cascade_attempts_supplements_for_a_non_open_pmc_article_and_records_not_held(tmp_path, monkeypatch):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import acquisition_cascade as ac
    monkeypatch.setattr(ac, "D", str(tmp_path))
    monkeypatch.setattr(ac, "HELD", str(tmp_path / "held"))
    monkeypatch.setattr(ac, "ATTEMPTS", str(tmp_path / "ATTEMPTS.jsonl"))
    rec = json.dumps({"resultList": {"result": [{"pmid": "1", "pmcid": "PMC1", "isOpenAccess": "N", "title": "t"}]}}).encode()

    def fake_get(url, accept=None):
        if "search?" in url:
            return 200, rec
        if "supplementaryFiles" in url:
            return 200, b"<?xml version='1.0'?><error/>"
        return 404, b""
    monkeypatch.setattr(ac, "_get", fake_get)
    targets = tmp_path / "t.json"
    targets.write_text(json.dumps({"topic": "x", "drug": "", "indication": "", "skip_regulatory": True,
                                   "trials": [{"trial": "T", "pmid": "1", "aliases": []}]}), encoding="utf-8")
    ac.main(["fetch", "--targets", str(targets)])
    rows = [json.loads(l) for l in open(tmp_path / "ATTEMPTS.jsonl", encoding="utf-8")]
    assert any(r["route"] == "supplements" for r in rows)                 # attempted without an opt-in flag
    assert any(r["route"] == "supplements_state" and r["status"] == "SUPPLEMENT_NOT_HELD" for r in rows)
