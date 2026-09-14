"""iv-iron HF-hospitalisation as declared strands, and the leakscan carve-out that permits a
within-strand pool for a suppressed topic WITHOUT re-opening the combined-pool leak.

The topic is suppressed because its estimands are incompatible (first-event HR vs recurrent
rate ratio). The three/four strands are the honest decomposition; each within-strand pool is a
legitimate compatible estimand. The carve-out must permit those pools yet STILL fire on:
  (P1) a derived pooled stat attributed to the slug OUTSIDE the strands (the historical iv-iron
       tau^2 leak) -- positive control,
  (P2) a 'strand' whose members cross event_process/endpoint (a disguised combined pool),
  (P3) an artefact that omits the honest-disclosure structure (no suppression reason).
"""
import json
import math
import os

import harness.leakscan as LS

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(_ROOT, "docs")
_ART = os.path.join(_DOCS, "iv_iron_strands.json")
_SLUG = "iv-iron-hfref-hosp"


def _load():
    return json.load(open(_ART, encoding="utf-8"))


def _se(lo, hi):
    return (math.log(hi) - math.log(lo)) / (2 * 1.96)


def test_strand_pools_reproduce_from_members():
    doc = _load()
    for s in doc["strands"]:
        if not s.get("pool"):
            continue
        ys = [math.log(m["effect"]) for m in s["members"]]
        ws = [1.0 / _se(m["ci_low"], m["ci_high"]) ** 2 for m in s["members"]]
        W = sum(ws)
        mu = math.exp(sum(w * y for w, y in zip(ws, ys)) / W)
        assert abs(mu - s["pool"]["effect"]) < 0.005, (s["strand"], mu, s["pool"]["effect"])


def test_strand_ci_is_canonical_hksj_not_z():
    # The strand CI MUST come from the canonical PM/HKSJ engine, never a bespoke z interval.
    # PLANT: a z-based common-effect interval (the shipped bug) would be far narrower and would flip
    # 'crosses null' to 'significant' at k=2. Assert the served CI equals HKSJ and NOT the z-fixed one.
    from harness.synth import Study, pool
    doc = _load()
    checked = 0
    for s in doc["strands"]:
        p = s.get("pool")
        if not p:
            continue
        studies = [Study(label=m["trial"], effect=m["effect"], ci_low=m["ci_low"], ci_high=m["ci_high"])
                   for m in s["members"]]
        r = pool(studies, scale="RR")
        assert abs(p["ci_low"] - round(r.ci_low, 3)) < 0.002, (s["strand"], p["ci_low"], r.ci_low)
        assert abs(p["ci_high"] - round(r.ci_high, 3)) < 0.002, (s["strand"], p["ci_high"], r.ci_high)
        # must NOT be the z-fixed common-effect interval (the bug)
        assert not (abs(p["ci_low"] - round(r.ci_low_fixed, 3)) < 0.002
                    and abs(p["ci_high"] - round(r.ci_high_fixed, 3)) < 0.002), s["strand"]
        # at k=2 with t(1)=12.7 both strands cross the null under the registered method
        assert p["crosses_null"] is True, s["strand"]
        checked += 1
    assert checked == 2


def test_endpoint_split_is_declared_and_cross_pool_refused():
    doc = _load()
    # Strand B (HF-alone) and Strand C (composite) are distinct endpoints.
    b = next(s for s in doc["strands"] if s["strand"] == "B")
    c = next(s for s in doc["strands"] if s["strand"] == "C")
    assert b["endpoint"] != c["endpoint"]
    # the refused cross-endpoint pool is carried as a STRING (never machine-readable derived stats)
    assert isinstance(doc["refused_cross_endpoint_pool"]["if_forced_it_would_be"], str)
    assert "0.783" in doc["refused_cross_endpoint_pool"]["if_forced_it_would_be"]


def test_every_member_has_source_span():
    doc = _load()
    for s in doc["strands"]:
        for m in s["members"]:
            assert m.get("source") and len(m["source"]) > 40, m


def test_leakscan_clean_on_real_artifact():
    # iv-iron is the suppressed topic; the real artefact must pass the leak scan.
    assert _SLUG in LS.suppressed_states(_DOCS)
    leaks = [lk for lk in LS.scan(_DOCS) if lk["artefact"] == "iv_iron_strands.json"]
    assert leaks == [], leaks


# --- the carve-out MUST still fail (gate can fail) ---

def _permitted_and_leaks(doc):
    permitted = LS._strand_permitted_ids(doc)
    # the doc is attributed to the slug via its top-level 'slug' field
    return LS._derived_here(doc, permitted)


def test_P1_out_of_strand_pool_still_leaks():
    doc = _load()
    doc["stray_combined_pool"] = {"estimate": 0.78, "tau2": 0.178, "ci_low": 0.66, "ci_high": 0.92}
    found = _permitted_and_leaks(doc)
    assert any("tau2" in f for f in found), found  # historical iv-iron leak still caught


def test_P2_cross_endpoint_strand_still_leaks():
    doc = _load()
    # inject a composite-endpoint member into the HF-alone strand B -> not homogeneous
    b = next(s for s in doc["strands"] if s["strand"] == "B")
    b["members"].append({"trial": "PLANT", "effect": 0.82, "ci_low": 0.66, "ci_high": 1.02,
                         "event_process": "RATE",
                         "endpoint": "HF hospitalisation + cardiovascular death (composite)"})
    found = _permitted_and_leaks(doc)
    assert found, "a cross-endpoint strand must not be permitted"


def test_P3_missing_disclosure_disables_carveout():
    doc = _load()
    del doc["why_topic_is_suppressed"]
    found = _permitted_and_leaks(doc)
    assert found, "without the suppression-reason disclosure the carve-out must not activate"
