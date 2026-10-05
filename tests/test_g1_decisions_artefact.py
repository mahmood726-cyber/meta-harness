"""The G1 decisions as RECORDED in the tracker artefact (registry/g1_decisions.json, outputs/k_gap/g1/*.json, the page),
checked from the artefact alone -- this file runs on main, where the tracker code that applies D2/D3 is not yet merged
(code plants: tests/test_g1_decisions.py on the consolidation). D1 is the page renderer's own rule and is planted here."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import render_g1_tracker as rg  # noqa: E402

G1 = os.path.join(ROOT, "outputs", "k_gap", "g1")
DEC = json.load(open(os.path.join(ROOT, "registry", "g1_decisions.json"), encoding="utf-8"))["decisions"]
D3 = next(d for d in DEC if d["id"] == "D3-COMPARATOR-POOLS-NO-RCT")


def _topics():
    for f in sorted(os.listdir(G1)):
        if f.endswith(".json"):
            yield json.load(open(os.path.join(G1, f), encoding="utf-8"))


def _binding():
    return {"label": "DELIVER", "route": "SWEEP_AACT_PRIMARY",
            "sweep": {"value": {"events_t": 512, "n_t": 3131, "events_c": 610, "n_c": 3132},
                      "basis": {"nct": "NCT03619213", "outcome": "CV death or worsening HF",
                                "snapshot": {"id": "AACT 2026-08-30", "digest": "0" * 63 + "1"},
                                "guard": "POSTED_N_EQUALS_RANDOMISED_N (6263)"}}}


def test_D1_PLANT_posted_results_count_only_with_the_full_recorded_binding():
    assert rg.counts(_binding(), set())[0]
    for k in ("nct", "outcome", "guard"):
        t = _binding()
        t["sweep"]["basis"].pop(k)
        assert not rg.counts(t, set())[0], k
    t = _binding()
    t["sweep"]["basis"]["snapshot"]["digest"] = "short"
    assert not rg.counts(t, set())[0]


def test_D2_every_one_comparable_trial_verdict_follows_its_recorded_share():
    seen = 0
    for d in _topics():
        st = d.get("same_trials") or {}
        if st.get("state") != "ONE_COMPARABLE_TRIAL":
            continue
        seen += 1
        sh = st.get("participant_share") or {}
        per = sh.get("per_trial") or []
        assert sh.get("decision") == "D2-ONE-TRIAL-SHARE" and per, d["slug"]
        total = sum(p["participants"] or 0 for p in per)
        agree = sum(p["participants"] or 0 for p in per if p["kind"] == "COMPARABLE")
        complete = all(p["participants"] for p in per) and not any(p["kind"] == "NOT_ESTIMABLE" for p in per)
        ok = complete and total and agree / total >= sh["min"]
        v = (st.get("verdict") or {}).get("verdict")
        if not ok:
            assert v != "AGREE", (d["slug"], v)
        assert sh["passes"] == bool(ok) or v != "AGREE", d["slug"]
    assert seen >= 1


def test_D3_a_comparator_pooling_no_rct_is_named_with_its_own_words_and_stays_counted():
    page = open(os.path.join(ROOT, "docs", "g1", "index.html"), encoding="utf-8").read()
    for slug, t in D3["topics"].items():
        d = json.load(open(os.path.join(G1, f"{slug}.json"), encoding="utf-8"))
        g = d["g1_status"]
        assert g["state"] == "COMPARATOR_POOLS_NO_RCT" and g["decision"] == D3["id"]
        src = open(os.path.join(ROOT, t["span"]["source"]), encoding="utf-8", errors="replace").read()
        norm = lambda x: re.sub(r"\s+", " ", x)  # noqa: E731
        assert norm(t["span"]["text"]) in norm(src)
        assert "id='not-attainable'" in page and slug in page.split("id='not-attainable'")[1].split("</ul>")[0]
    assert "of 32 topics" in page                                   # the denominator is not shrunk


def test_every_decision_is_listed_on_the_page():
    page = open(os.path.join(ROOT, "docs", "g1", "index.html"), encoding="utf-8").read()
    assert all(d["id"] in page for d in DEC)
