"""G1 tocilizumab vs WHO REACT 2021 (g1/tocilizumab.py): the positive control, the anti-circularity and two-source
rules, denominator kinds, and the plants (each must fire with its guard removed and not as built)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from g1 import tocilizumab as g  # noqa: E402

R = g.run()


def test_react_rows_reproduce_reacts_printed_pool():
    pc, pr = R["positive_control"], R["comparator"]["printed"]
    assert (round(pc["or"], 2), round(pc["lo"], 2), round(pc["hi"], 2)) == (pr["estimate"], pr["ci_low"], pr["ci_high"])
    assert pr["k"] == 19 and len(R["trials"]) == 19


def test_a_react_row_is_never_a_source_and_k_matched_counts_established_primary_rows_only():
    assert not any("REACT" in s.get("source", "") for t in R["trials"] for x in t["readings"] for s in x["sources"])
    est_agree = [t for t in R["trials"] if t["state"] == g.ESTABLISHED and t["vs_react"]["verdict"] == "AGREE"]
    assert R["k_matched"] == len(est_agree)
    one = [t["label"] for t in R["trials"] if t["state"] == g.ONE_SOURCE]
    assert one and not set(one) & {t["label"] for t in est_agree}   # one-source rows never counted


def test_established_means_two_independent_sources_one_primary():
    for t in R["trials"]:
        if t["state"] == g.ESTABLISHED:
            kinds = next(x["independent_sources"] for x in t["readings"] if x["values"] == {k: t["row"][k] for k in g._KEY})
            assert len(kinds) >= 2 and set(kinds) & {"AACT", "TEXT"}, t["label"]


def test_the_pool_on_established_rows_equals_reacts_on_the_same_trials():
    assert R["pool_ours_established"] == R["pool_react_same_trials"]


def test_unique_count_refuses_an_undetermined_percentage():
    assert g.unique_count("19.7", 294) == 58 and g.unique_count("31", 2022) is None


def test_plants_fire_only_with_their_guard_removed():
    out = json.loads(subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "plants_g1_tocilizumab.py")],
                                    capture_output=True, text=True, encoding="utf-8", check=True).stdout)
    assert not any(v["fired_as_built"] for v in out.values())
    assert all(v["fires_with_guard_removed"] for k, v in out.items() if "fires_with_guard_removed" in v)


def test_a_safety_population_count_is_shown_never_established_and_react_bacc_row_is_one():
    bacc = next(t for t in R["trials"] if t["label"] == "BACC-Bay")
    assert bacc["vs_react"]["verdict"] == "REACT_ROW_IS_SAFETY_POPULATION" and bacc["state"] != g.ESTABLISHED
    s = [x for x in bacc["readings"] if x["denominator_kind"] == g.SAFETY]
    assert s and s[0]["values"] == {"deaths_t": 9, "n_t": 161, "deaths_c": 4, "n_c": 82}
    assert all((t["row"] or {}).get("denominator_kind") != g.SAFETY for t in R["trials"])


def test_every_trial_has_a_logged_cascade_with_every_rung():
    for label in g.IDENTITY:
        c = json.load(open(os.path.join(ROOT, "g1", "data", "cascade", f"{label}.json"), encoding="utf-8"))
        # every per-trial rung was RUN and logged (R6 preprints added 2026-10-02): a rung may be added, never dropped
        assert {"R4 AACT", "R5 ISRCTN", "R6 Europe PMC preprints"} <= {r["rung"] for r in c["trial_rungs"]}
        assert all(r.get("outcome") for r in c["trial_rungs"])
        assert any(d["rung"].startswith("D") or "esearch" in d["rung"] or "Europe PMC" in d["rung"] for d in c["discovery"]) \
            or label == "PreToVid" or c["discovery"]
        for r in c["candidates"]:
            if r["screen"] == "PRIMARY_REPORT_CANDIDATE":
                assert [x["rung"] for x in r["rungs"]] == ["R1 PMC", "R2 Europe PMC", "R3 Unpaywall"]


def test_recovery_own_open_full_text_is_held_and_read():
    a = json.load(open(os.path.join(ROOT, "g1", "data", "acquired", "33933206.json"), encoding="utf-8"))
    assert "<body" in a["fulltext"] and "RECOVERY" in a["bound_labels"] and "by/4.0" in (a["license"] or "")
    rec = next(t for t in R["trials"] if t["label"] == "RECOVERY")
    assert any("33933206" in r for r in rec["texts_held"])


def test_second_metas_are_independent_of_react_and_two_reader_admitted():
    m = json.load(open(os.path.join(ROOT, "g1", "data", "meta2_forest.json"), encoding="utf-8"))
    for pmid, r in m.items():
        assert r["independence"]["state"] == "INDEPENDENT" and r["state"] == "PASS"
        assert all(v["gate"]["state"] == "PASS" for v in r["readers"].values())


def test_the_pool_is_labelled_coverage_limited_and_no_topic_result_is_stated():
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "tocilizumab-covid19-mortality.json"), encoding="utf-8"))
    assert o["same_trials"]["is_a_finding"] is False and "COVERAGE-LIMITED" in o["same_trials"]["measure"]
    assert o["ours"]["estimate"] is None and "NOT_STATED" in o["ours"]["state"]
    assert [x["trial"] for x in o["coverage"]["largest_trials_not_established"][:2]] == ["RECOVERY", "REMAP-CAP"]
    md = open(os.path.join(ROOT, "g1", "TOCILIZUMAB_G1.md"), encoding="utf-8").read()
    assert "NOT a finding" in md
