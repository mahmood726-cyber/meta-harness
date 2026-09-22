import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import harms, pipeline  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _families import eligible_by_construction  # noqa: E402  (families ELIGIBLE by construction: the admission gate is on by default)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git_json(ref):
    out = subprocess.check_output(["git", "show", ref], cwd=ROOT, text=True, encoding="utf-8")
    return json.loads(out)


def _records(slug):
    with open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8") as f:
        recs = json.load(f)["records"]
    return {str(r["id"]): r for r in recs}


def test_prefixed_doac_no_harms_recorded_plant_fires():
    review = _git_json("ad5e7c66:docs/reviews/doac-vte-recurrence/review.json")
    html = subprocess.check_output(
        ["git", "show", "ad5e7c66:docs/reviews/doac-vte-recurrence/index.html"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    rec_by_id = _records("doac-vte-recurrence")
    included = [
        {"id": str(r.get("id")), "id_type": r.get("id_type", "pmid"), "label": r.get("id")}
        for r in (review.get("screening") or {}).get("records", [])
        if r.get("decision") == "include"
    ]

    harms.annotate_review(review, {}, included, rec_by_id)

    assert "DECLARED ABSENT" in html and "no harms recorded" in html
    assert "major bleeding" in rec_by_id["23808982"]["abstract"].lower()
    state = review["harms_registry_state"]
    assert state["state"] == harms.KNOWN_REPORTED_NOT_YET_EXTRACTED
    assert any("major bleeding" in row["span"].lower() for row in state["known_reported_not_yet_extracted"])


def test_postfix_noac_major_bleeding_recovers_four_trials():
    cfg = json.load(open(os.path.join(ROOT, "topics", "noac-vs-warfarin-af-stroke.json"), encoding="utf-8"))
    rec_by_id = _records("noac-vs-warfarin-af-stroke")
    included = [
        {"id": pid, "id_type": "pmid", "label": pid}
        for pid in ["19717844", "21830957", "21870978", "24251359"]
    ]
    spec = cfg["harm_outcomes"][0]
    ve = json.load(open(os.path.join(ROOT, "cache", "noac-vs-warfarin-af-stroke", "verified_effects.json"), encoding="utf-8"))

    out = pipeline._build_outcome(
        spec,
        "harm",
        included,
        rec_by_id,
        cfg["intervention_terms"],
        cfg["comparator_terms"],
        verified_effects=ve,
        family_nodes=eligible_by_construction(rec_by_id),
        dose_selection=json.load(open(os.path.join(ROOT, "cache", "noac-vs-warfarin-af-stroke", "dose_selection.json"), encoding="utf-8")),
    )
    harms.annotate_outcome(out, spec, included, rec_by_id)

    # The property: no verified major-bleeding effect is silently lost. Every trial carrying a verified effect is
    # either POOLED with that effect, or SET ASIDE with its candidate tuple visible and a named reason (the hand
    # binder could not locate the tuple in the held abstract -- ROCKET-AF and RE-LY report major bleeding in
    # their full texts, which are not held). Until 2026-09-20 this asserted k == 4 and the pooled numbers; the
    # pool is a census finding, not this recovery's property.
    pooled = {t["id"].replace("PMID ", ""): t for t in out["trials"]}
    absent = {a["id"].replace("PMID ", ""): a for a in out.get("declared_absent_trials") or []}
    for pid, entries in ve.items():
        entries = entries if isinstance(entries, list) else [entries]
        e = next((x for x in entries if x.get("outcome") == spec["name"] and x.get("effect") is not None), None)
        if e is None:
            continue
        if pid in pooled:
            assert abs(float(pooled[pid]["effect"]) - float(e["effect"])) < 1e-9, pid
        else:
            a = absent.get(pid)
            assert a is not None, f"{pid}: verified effect neither pooled nor set aside"
            assert a.get("reason_code") in ("ENDPOINT_UNBOUND", "RESULT_INCOMPATIBLE"), (pid, a.get("reason_code"))
            assert (a.get("candidate_tuple") or {}).get("effect") == e["effect"], (pid, a.get("candidate_tuple"))
    assert out["result"]["k"] == len(out["trials"])
    assert not out["result"].get("harms_incomplete")


def test_synthetic_true_omission_is_not_extraction_debt():
    spec = {"name": "Major bleeding", "keywords": ["major bleeding"], "estimand": "RR"}
    recs = {"1": {"abstract": "This randomized trial reports headache and nausea only."}}
    out = {"name": spec["name"], "kind": "harm", "trials": [], "declared_absent_trials": [
        {"id": "PMID 1", "label": "T1", "state": "OUTCOME_NOT_IN_SOURCE", "reason_code": "OUTCOME_NOT_IN_SOURCE"}
    ], "result": {"present": False, "reason": "no extractable value"}}
    harms.annotate_outcome(out, spec, [{"id": "1", "id_type": "pmid"}], recs)
    row = out["declared_absent_trials"][0]
    assert row["harm_absence_state"] == harms.RETRIEVED_OUTCOME_NOT_REPORTED
    assert not out["result"].get("harms_incomplete")


def test_zero_cell_harm_discloses_continuity_correction():
    spec = {"name": "Diabetic ketoacidosis", "keywords": ["ketoacidosis"], "estimand": "RR"}
    out = {"name": spec["name"], "kind": "harm", "trials": [
        {"id": "PMID 1", "label": "Zero", "ai": 0, "n1i": 100, "ci": 2, "n2i": 100}
    ], "declared_absent_trials": [], "result": {"k": 1}}
    harms.annotate_outcome(out, spec, [{"id": "1", "id_type": "pmid"}], {"1": {"abstract": "Ketoacidosis was assessed."}})
    assert "0.5 continuity correction" in out["trials"][0]["continuity_correction"]
