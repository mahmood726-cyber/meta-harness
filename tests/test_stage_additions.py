"""Regression tests for the cycle-76 stage additions:
- absent-override tier (declare a trial absent for one outcome when the extractor grabbed a wrong endpoint)
- object-derived partial GRADE
- RoB-stratified sensitivity re-pool (its 'full' pool MUST reproduce the shipped primary result)
- the index error-rate banner numbers are derived from docs/error_rate.json (anti-drift)
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import grade as grade_mod  # noqa: E402
from harness import rob_sensitivity as rs  # noqa: E402
from harness import index as IDX  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


def _reviews():
    for f in sorted(glob.glob(os.path.join(DOCS, "reviews", "*", "review.json"))):
        yield os.path.basename(os.path.dirname(f)), json.load(open(f, encoding="utf-8"))


# ---- absent-override ------------------------------------------------------------------------------
def test_absent_override_declared_and_flag_gated():
    """The semaglutide GI-AE wrong-endpoint fix: the flagged absent-override declares the trial absent,
    and the trial is NOT pooled. An UNFLAGGED entry (no override/absent) would not."""
    r = json.load(open(os.path.join(DOCS, "reviews", "semaglutide-obesity-weight", "review.json"), encoding="utf-8"))
    gi = next(o for o in r["outcomes"] if "astrointestinal" in o["name"])
    assert "42575111" not in [str(t.get("label")) for t in gi.get("trials", [])], "wrong-endpoint trial still pooled"
    da = [t for t in gi.get("declared_absent_trials", []) if str(t.get("label")) == "42575111"]
    assert da, "STEP-12 not declared absent"
    assert "override" in da[0]["reason"].lower() or "overall" in da[0]["reason"].lower()
    # the committed override entry carries both flags (flag-gated: absent requires override AND absent)
    ve = json.load(open(os.path.join(ROOT, "cache", "semaglutide-obesity-weight", "verified_effects.json"), encoding="utf-8"))
    e = ve["42575111"]
    assert e.get("override") is True and e.get("absent") is True and e.get("outcome") == gi["name"]


# ---- GRADE ---------------------------------------------------------------------------------------
def test_grade_present_and_valid_for_every_primary():
    for slug, r in _reviews():
        prim = next((o for o in r["outcomes"] if o.get("primary")), None)
        if not prim or not prim.get("result", {}).get("k"):
            continue
        g = r.get("grade")
        assert g, f"{slug}: no grade"
        assert g["certainty"] in ("high", "moderate", "low", "very_low"), slug
        # downgrades must equal the sum of domain downgrades (object-derived, not typed)
        s = sum(d.get("downgrade", 0) for d in g["domains"].values())
        assert g["downgrades"] == s, f"{slug}: downgrade total {g['downgrades']} != sum {s}"


def test_grade_recomputes_from_object():
    """grade() run again on the committed review + ghost must equal the stored grade (regenerates)."""
    for slug, r in _reviews():
        if not r.get("grade"):
            continue
        gp = os.path.join(ROOT, "cache", slug, "ghost.json")
        ghost = json.load(open(gp, encoding="utf-8")) if os.path.exists(gp) else None
        assert grade_mod.grade(r, ghost)["certainty"] == r["grade"]["certainty"], slug


def test_grade_imprecision_downgrades_iff_ci_crosses_null():
    for slug, r in _reviews():
        g = r.get("grade")
        if not g:
            continue
        prim = next(o for o in r["outcomes"] if o.get("primary"))
        res = prim["result"]
        scale = (res.get("scale") or "")
        # skip mixed-scale labels (null is ambiguous); check clean ratio/MD pools
        if scale.upper() in ("RR", "OR", "HR", "IRR", "MD"):
            null = 0.0 if scale.upper() == "MD" else 1.0
            crosses = res.get("ci_low") <= null <= res.get("ci_high")
            imp = g["domains"]["imprecision"]
            if crosses and res.get("k", 0) > 1:
                assert imp["downgrade"] >= 1, f"{slug}: CI crosses null but imprecision not downgraded"


# ---- RoB sensitivity -----------------------------------------------------------------------------
def test_rob_sensitivity_full_repool_matches_shipped():
    """The 'full' stratum re-pool MUST reproduce the shipped primary result — this is what guarantees the
    sensitivity re-pool uses the identical estimator and cannot drift from the page's number."""
    for slug, r in _reviews():
        sens = r.get("rob_sensitivity")
        if not sens:
            continue
        prim = next(o for o in r["outcomes"] if o.get("primary"))
        shipped = prim["result"]
        full = sens["full"]
        assert full["k"] == shipped["k"], f"{slug}: full k {full['k']} != shipped {shipped['k']}"
        assert abs(full["estimate"] - shipped["estimate"]) < 0.0011, f"{slug}: full estimate drifted"


def test_rob_sensitivity_recomputes():
    for slug, r in _reviews():
        if not r.get("rob_sensitivity"):
            continue
        again = rs.sensitivity(r)
        assert again["full"] == r["rob_sensitivity"]["full"], slug
        assert again["n_rob_rated"] == r["rob_sensitivity"]["n_rob_rated"], slug


# ---- error-rate index banner ---------------------------------------------------------------------
def test_error_rate_banner_numbers_are_object_derived():
    if not os.path.exists(os.path.join(DOCS, "error_rate.json")):
        return
    d = json.load(open(os.path.join(DOCS, "error_rate.json"), encoding="utf-8"))
    html = IDX.build_index(DOCS)
    assert "measured our own error rate" in html
    assert f"{d['independently_reverified']} of {d['population']}" in html
    assert f"{d['exact_match']} of {d['independently_reverified']} matched exactly" in html


def test_error_rate_passes_prose_guard():
    """build_index runs _validate_prose_numbers over the error-rate banner; it must not raise."""
    assert IDX.build_index(DOCS)
