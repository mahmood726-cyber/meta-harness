"""Melatonin and metformin-PCOS fixtures, 2026-09-28 (plants included)."""
import copy
import json
import os

from harness import (arm_label_conflict as alc, family_invariant as fi, fetch, multi_trial_report as mtr, pipeline,
                     result_status as rs)

ROOT = pipeline.ROOT
MEL, MET = "melatonin-primary-insomnia-sol", "metformin-pcos-ovulation"
_R = {}


def _rv(slug):
    if slug not in _R:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        _R[slug] = pipeline.build_review_core(slug, cfg, fetch.ensure(cfg, ""), "test")
    return _R[slug]


def _row(slug, outcome, pid, pooled=False):
    o = next(o for o in _rv(slug)["outcomes"] if o["name"] == outcome)
    return next(t for t in (o["trials"] if pooled else o["declared_absent_trials"]) if pid in str(t["id"]))


# ------------------------------------------------------------------------------------------------ melatonin
def test_wade_2011_is_a_companion_in_the_same_family_never_a_second_trial():
    fam = next(f for f in _rv(MEL)["trial_families"] if f["family_id"] == "NCT00397189")
    assert {"20712869", "21091391"} <= {r["report_id"] for r in fam["reports"]}
    assert not any("21091391" in str(t["id"]) for o in _rv(MEL)["outcomes"] for t in o["trials"])


def test_the_all_adult_result_is_a_relayed_version_the_subgroup_still_governs_pending():
    ch = next(c for c in _rv(MEL)["source_versions"] if c["chain_id"] == "NCT00397189:SOL-diary-3wk")
    assert ch["governing"]["state"] == "PENDING" and ch["governing"]["version_id"] == "v0-2010-subgroup-65-80"
    v1 = next(v for v in ch["versions"] if v["version_id"] == "v1-2011-all-adults-18-80")
    assert v1["held"] is False and v1["value"] is None and v1["relayed_value"]["nc1"] == 360
    row = _row(MEL, "Sleep-onset latency", "20712869", pooled=True)
    assert (row["mean1"], row["sd1"], row["nc1"]) == (-19.1, 47.3, 137)      # the served value is untouched


def test_lemoine_is_a_pooled_secondary_report_linked_to_its_four_trials():
    scr = next(r for r in _rv(MEL)["screening"]["records"] if r["id"] == "22346363")
    assert scr["decision"] == "exclude" and scr["rule_id"] == "X-DEDUP"
    r = next(m for m in _rv(MEL)["multi_trial_reports"] if m["report_id"] == "PMID 22346363")
    assert [t["label"] for t in r["trials"]] == ["Lemoine 2007", "Luthringer 2009", "Wade 2010", "Wade 2007"]
    # PLANT: its pooled estimate added as a trial
    rv = copy.deepcopy(_rv(MEL))
    o = next(o for o in rv["outcomes"] if o["name"] == "Sleep-onset latency")
    o["trials"] = o["trials"] + [{"id": "PMID 22346363", "mean1": -1, "sd1": 1, "nc1": 195, "mean2": 0, "sd2": 1, "nc2": 197}]
    assert "COMBINED_POPULATION_IMPORTED" in [p["kind"] for p in mtr.problems(rv)]


def test_arm_ownership_is_adjudicated_only_by_an_independent_source():
    c = next(x for x in alc.load(ROOT) if x["trial_id"] == "PMID 20712869")
    a = alc.adjudicate(c)
    assert a["state"] == alc.ADJUDICATED and a["ownership"] == {"394": "melatonin", "395": "placebo"}
    assert a["outvoted"] == ["publisher PDF, Table 8"]
    # PLANT: identical counts across formats never establish ownership -- same-article corroboration only
    same = dict(c, corroboration=[x for x in c["corroboration"] if not x["independent_of_article"]])
    assert alc.adjudicate(same)["state"] == alc.UNRESOLVED
    # PLANT: no corroboration at all
    assert alc.adjudicate(dict(c, corroboration=[]))["state"] == alc.UNRESOLVED


def test_a_pooled_row_against_the_adjudicated_ownership_or_an_unresolved_conflict_blocks():
    rv = copy.deepcopy(_rv(MEL))
    assert alc.problems(rv) == []
    ae = next(o for o in rv["outcomes"] if o["name"] == "Adverse events")
    wade = next(t for t in ae["trials"] if "20712869" in t["id"])
    wade["n1i"], wade["n2i"] = 395, 394                                         # PLANT: flipped
    assert [p["kind"] for p in alc.problems(rv)] == ["ARM_LABEL_CONFLICT"]
    rv2 = copy.deepcopy(_rv(MEL))
    rv2["arm_label_conflicts"][0]["state"] = alc.UNRESOLVED                    # PLANT: unresolved but pooled
    assert "ARM_LABEL_CONFLICT" in [p["kind"] for p in alc.problems(rv2)]


def test_luthringer_is_reported_with_extraction_pending_and_no_invented_sd():
    row = _row(MEL, "Sleep-onset latency", "19584739")
    assert row["result_status"]["state"] == rs.REPORTED_UNRESOLVED
    assert "extraction pending" in row["reason"] and "3 weeks" in row["reason"]
    assert row.get("sd1") is None and row.get("mean1") is None


# ------------------------------------------------------------------------------------------------ metformin
def test_moll_discontinuation_is_reported_unresolved_and_never_gi_incidence():
    disc = _row(MET, "Treatment discontinuation due to adverse events", "16769748")
    assert disc["result_status"]["state"] == rs.REPORTED_UNRESOLVED
    assert disc["reason_code_audit"]["verdict"] == "REASON_TRUE"                 # the auditor no longer calls it absent
    gi = _row(MET, "Gastrointestinal adverse events", "16769748")
    assert gi["result_status"]["state"] == rs.RETRIEVED_NOT_REPORTED           # its mention is discontinuation, not GI
    assert "18/111" in disc["relayed_not_held"]["value"] and "relayed_not_held" not in gi   # recorded, on its outcome only
    pooled = [t for o in _rv(MET)["outcomes"] for t in o["trials"] if "16769748" in t["id"]]
    assert all((t.get("ai"), t.get("ci")) != (18, 6) for t in pooled)          # relayed counts are never data


def test_every_input_belongs_to_one_family_and_the_count_matches_the_populations():
    rv = _rv(MET)
    assert rv["family_count_chain"]["contributing"] == 3 and fi.problems(rv) == []
    ids = {t["family_id"] for o in rv["outcomes"] for t in o["trials"]}
    assert ids == {"ISRCTN55906981", "PMID:19522426", "PMID:11172832"}
    # PLANTS: an input with no family; a miscount; one family pooled twice
    a = copy.deepcopy(rv)
    next(o for o in a["outcomes"] if o["trials"])["trials"][0]["family_id"] = None
    b = copy.deepcopy(rv)
    b["family_count_chain"]["contributing"] = 1
    c = copy.deepcopy(rv)
    o = next(o for o in c["outcomes"] if o["trials"])
    o["trials"].append(dict(o["trials"][0], id="PMID 99999999"))
    for plant in (a, b, c):
        assert [p["kind"] for p in fi.problems(plant)] and all(p["kind"] == "FAMILY_INVARIANT" for p in fi.problems(plant))
