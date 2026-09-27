"""Finerenone (CKD + T2D) review fixtures, 2026-09-27.
(1) FIGARO Table 2 hyperkalaemia rows bound; FIDELIO stays REPORTED_UNRESOLVED on its own evidence (never absent).
(2) FIVE-STAR / CONFIDENCE screening gaps; CONFIDENCE judged per ARM PAIR with 'placebo for X' parsing.
(3) FIDELITY is a pooled report of the two existing families, never a third trial, never imported.
(4) Completeness is claimed per outcome; a planned-completion registration makes a pool PROVISIONAL, not incomplete."""
import copy
import json
import os

from harness import arm_pairs, comparison_family as cf, completeness, fetch, multi_trial_report as mtr, pipeline

ROOT = pipeline.ROOT
SLUG = "finerenone-ckd-t2d-renal"
CONFIG = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
_REV = {}


def _review():
    if "rv" not in _REV:
        _REV["rv"] = pipeline.build_review_core(SLUG, CONFIG, fetch.ensure(CONFIG, ""), "test")
    return _REV["rv"]


def _outcome(name):
    return next(o for o in _review()["outcomes"] if o["name"] == name)


def test_figaro_table2_rows_are_bound_and_fidelio_stays_reported_unresolved():
    for name, a, c in (("Hyperkalemia", 396, 193), ("Hyperkalemia-related treatment discontinuation", 46, 13)):
        o = _outcome(name)
        fig = next(t for t in o["trials"] if "34449181" in t["id"])
        assert (fig["ai"], fig["n1i"], fig["ci"], fig["n2i"]) == (a, 3683, c, 3658)
        assert fig["target_endpoint_class"] == "EXACT_TARGET" and fig["hand_binding_state"] == "BOUND"
        fid = next(x for x in o["declared_absent_trials"] if "33264825" in x["id"])
        assert fid["result_status"]["state"] == "REPORTED_UNRESOLVED"       # never absent-by-design, never 'not reported'


def test_confidence_is_judged_per_arm_pair():
    got = cf.screen_registration({"id": "NCT05254002", "id_type": "nct", "title": "CONFIDENCE"}, CONFIG)
    e = {c["comparison_id"].split(" ")[0]: c for c in got["comparisons"]}
    assert e["CONFIDENCE:A-vs-C"]["eligibility"] == cf.ELIGIBLE
    assert e["CONFIDENCE:A-vs-C"]["arm_contrast"]["background"] == ["empagliflozin"]
    assert e["CONFIDENCE:B-vs-C"]["eligibility"] == e["CONFIDENCE:A-vs-B"]["eligibility"] == cf.INELIGIBLE
    assert got["decision"] == "include"


def test_placebo_for_x_is_never_the_active_drug_x():
    for label in ("Empagliflozin and Finerenone placebo", "Empagliflozin + placebo for finerenone",
                  "Empagliflozin with matching placebo for finerenone"):
        assert arm_pairs.parse_arm(label)["active"] == ["empagliflozin"], label
    assert cf._active("Empagliflozin and Finerenone placebo", ["finerenone"]) == []
    assert cf._active("standard-dose dexamethasone", ["dexamethasone"]) == ["dexamethasone"]   # the COVIDICUS case holds
    # PLANT: a dose-comparison pair (the drug in BOTH arms) is not a drug-vs-placebo contrast
    j = arm_pairs.judge("Finerenone 20 mg", "Finerenone 10 mg and placebo", ["finerenone"])
    assert j["eligible_contrast"] is False and j["contrast"]["background"] == ["finerenone"]


def test_fidelity_is_a_pooled_report_never_a_third_trial():
    r = next(x for x in mtr.resolve(ROOT, CONFIG) if x["report_id"] == "PMID 35023547")
    assert [t["label"] for t in r["trials"]] == ["FIDELIO-DKD", "FIGARO-DKD"]
    assert {c["policy"] for c in r["combined_analyses"]} == {"NEVER_IMPORTED"}
    assert not any("35023547" in str(x["id"]) for x in _review()["screening"]["records"])
    # PLANT: the pooled estimate pooled as a trial, and a FIDELIO row carrying the pooled population
    rv = copy.deepcopy(_review())
    rv["multi_trial_reports"] = [r]
    o = next(o for o in rv["outcomes"] if o["name"] == "Kidney composite outcome")
    o["trials"] = [{"id": "PMID 35023547", "effect": 0.77}, {"id": "PMID 33264825", "n1i": 6519, "n2i": 6507}]
    kinds = [p["kind"] for p in mtr.problems(rv)]
    assert kinds.count("COMBINED_POPULATION_IMPORTED") == 2


def test_completeness_is_per_outcome_and_planned_trials_make_it_provisional_not_incomplete():
    c = {x["outcome"]: x for x in _review()["completeness_by_outcome"]}
    kidney = c["Kidney composite outcome"]
    assert kidney["claim"] == "PROVISIONAL"
    st = {f["family"]: f["state"] for f in kidney["families"]}
    assert st["FineCaRe · NCT07026539"] == st["NCT07775846"] == "ONGOING"
    assert st["FIVE-STAR (known missing: not in the inventory)"] == "PUBLISHED_NO_TARGET_OUTCOME"
    assert c["Hyperkalemia"]["claim"] == "INCOMPLETE"          # FIDELIO / ARTS-DN report it, unresolved
    # PLANT: the same family ONGOING vs COMPLETED_AWAITING changes the claim
    rv = copy.deepcopy(_review())
    for r in rv["screening"]["records"]:
        if "NCT07775846" in r["id"]:
            r["lifecycle"]["state"] = "UNKNOWN"
    kid = next(x for x in completeness.build(rv, []) if x["outcome"] == "Kidney composite outcome")
    assert kid["claim"] == "INCOMPLETE"
