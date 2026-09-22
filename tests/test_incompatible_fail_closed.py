"""INCOMPATIBLE must FAIL CLOSED (audit 23, DETECTED-INVALID-BUT-PUBLISHED).

The most important defect of the 23 audits: a page that detects an estimand-incompatible pool and STILL
renders the pooled effect, common-effect sensitivity, tau^2, forest and manuscript sentence. Detecting the
failure and printing the number is a caption, not a gate — disclosure is not suppression. When the primary
pool mixes incompatible estimand classes, EVERY derived number must be suppressed corpus-wide: pooled effect,
CI, tau^2, prediction interval, leave-one-out, common-effect sensitivity, the forest, the specification curve
(a re-pool), and the manuscript result sentence.

Each synthetic case is a PLANT: the primary trials are genuinely poolable (k>=3 binary counts), so WITHOUT the
fail-closed guards spec_curve would return specs, the page would render effect rows, and the manuscript would
draw a forest. The guards must turn all of those off purely on the suppressed_incompatible flag."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # tests/ on the path for _contracts
import glob
import json
import os

from harness import page, manuscript
from harness.spec_curve import spec_curve

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")

# A leftover pooled estimate deliberately left ON the result object: if any suppression path regresses,
# this exact string surfaces in the rendered output and the assertion catches it.
_LEFTOVER = 0.6137


def _incompatible_review():
    trials = [
        {"label": "A", "ai": 10, "n1i": 100, "ci": 20, "n2i": 100, "source": "hazard ratio for first event"},
        {"label": "B", "ai": 12, "n1i": 110, "ci": 25, "n2i": 108, "source": "rate ratio, recurrent events"},
        {"label": "C", "ai": 8, "n1i": 90, "ci": 18, "n2i": 92, "source": "hazard ratio"},
    ]
    result = {
        "present": True,
        "k": 3,
        "scale": "INCOMPATIBLE (FIRST_EVENT_RATIO + RATE)",
        "suppressed_incompatible": True,
        "estmeasure_incompatible": True,
        "suppressed_reason": "pooled effect SUPPRESSED: the trials mix incompatible estimand classes.",
        "estmeasure": {"status": "incompatible",
                       "canonicals": ["FIRST_EVENT_RATIO", "RATE"], "labels": ["HR", "IRR"]},
        # deliberately-present leftovers a regressed renderer would print:
        "estimate": _LEFTOVER, "ci_low": 0.41, "ci_high": 0.92, "tau2": 0.07,
    }
    return {
        "topic": "__plant_incompatible__",
        "outcomes": [{"name": "Primary", "primary": True, "estimand": "RR",
                      "population": "adults", "timepoint": "12 mo", "method": "RE",
                      "trials": trials, "result": result}],
    }


def test_spec_curve_fails_closed_on_suppressed_primary():
    r = _incompatible_review()
    sc = spec_curve(r)
    # PLANT check: the trials ARE poolable, so a spec_curve blind to the flag would return specs.
    assert sc is not None
    assert sc.get("not_applicable"), "spec_curve re-pooled a suppressed-incompatible primary (detect-and-render)"
    assert sc.get("suppressed_incompatible") is True
    assert "specs" not in sc


def test_page_suppresses_every_pooled_number():
    r = _incompatible_review()
    block = page._outcome_block(r["outcomes"][0])
    assert "SUPPRESSED" in block, "page did not render the suppression banner"
    # No pooled number, CI, tau^2 or forest may appear.
    assert str(_LEFTOVER) not in block, "page rendered the suppressed pooled estimate"
    assert "0.41" not in block and "0.92" not in block, "page rendered the suppressed CI"
    assert "<svg" not in block, "page rendered a forest for a suppressed pool"


def test_manuscript_suppresses_result_and_forest():
    r = _incompatible_review()
    assert manuscript._forest(r) == "", "manuscript drew a forest for a suppressed pool"
    html = manuscript.render(r)
    assert str(_LEFTOVER) not in html, "manuscript rendered the suppressed pooled estimate"
    assert "INCOMPATIBLE estimand classes" in html, "manuscript did not report the suppression"


def test_corpus_incompatible_topics_are_fully_suppressed():
    """Every SHIPPED review whose primary pool is estimand-incompatible must carry no pooled number and must
    fail closed in page / manuscript / spec_curve. List the topics so the invariant is not vacuous."""
    suppressed = []
    for f in glob.glob(os.path.join(DOCS, "reviews", "*", "review.json")):
        r = json.load(open(f, encoding="utf-8"))
        prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None)
        if not prim:
            continue
        from _contracts import scale_contract
        scale_contract(prim)  # derive incompatibility from admitted members, including an empty corpus of suppressions
        res = prim.get("result") or {}
        if not res.get("suppressed_incompatible"):
            continue
        slug = os.path.basename(os.path.dirname(f))
        suppressed.append(slug)
        # no pooled numbers survive on the result object
        for k in ("estimate", "ci_low", "ci_high", "tau2", "leave_one_out", "pi_low", "pi_high"):
            assert res.get(k) is None, f"{slug}: pooled '{k}' survived suppression"
        # renderers fail closed — both the detailed Results block AND the overview summary
        block = page._outcome_block(prim)
        assert "SUPPRESSED" in block and "<svg" not in block, f"{slug}: page did not fail closed"
        ov = page._overview(r, False)
        assert "SUPPRESSED" in ov, f"{slug}: overview did not fail closed"
        assert "Trials pooled (k)" not in ov, f"{slug}: overview still frames suppressed outcome as pooled"
        assert manuscript._forest(r) == "", f"{slug}: manuscript forest not suppressed"
        sc = spec_curve(r) or {}
        assert sc.get("not_applicable"), f"{slug}: spec_curve re-pooled a suppressed primary"
        # GRADE overall must be not_rateable, and the manuscript must not print a downgrade count or a
        # "no domain downgraded" conclusion for an incoherent effect object.
        from harness import grade as _grade
        g = _grade.grade(r) or {}
        assert g.get("certainty") == "provisional" and g.get("not_rateable_reason"), f"{slug}: GRADE rated a suppressed-incompatible pool"
        ms = manuscript.render(r)
        assert "downgrade(s)" not in ms, f"{slug}: manuscript printed a downgrade count for a not-rateable pool"
        assert "No GRADE domain was downgraded" not in ms, f"{slug}: manuscript asserted a GRADE conclusion"
    # iv-iron is the GENUINE incompatible case (first-event HR CONFIRM-HF + recurrent IRR FAIR-HF2, whose
    # source says "occurred 264 times"). omega3 was a FALSE POSITIVE — its only "IRR" trial (ASCEND) is a
    # first-event log-rank rate ratio that the IRR-typing fix (audit 22) correctly reclassified to a
    # first-event ratio, so omega3 is now compatible and pools; it must NOT be suppressed.
    control = _incompatible_review()
    assert "SUPPRESSED" in page._outcome_block(control["outcomes"][0])
    assert str(_LEFTOVER) not in page._outcome_block(control["outcomes"][0])
    assert manuscript._forest(control) == ""
    assert spec_curve(control).get("not_applicable")


def _suppressed_slugs():
    out = []
    for p in glob.glob(os.path.join(DOCS, "reviews", "*", "review.json")):
        r = json.load(open(p, encoding="utf-8"))
        prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None)
        if ((prim or {}).get("result") or {}).get("suppressed_incompatible"):
            out.append(os.path.basename(os.path.dirname(p)))
    return out


def test_aggregate_snapshots_do_not_count_suppressed_as_pooled():
    """The committed aggregate metric snapshots (generated by separate scripts, NOT reproduced by the gate)
    must not count a suppressed-incompatible primary as a pooled evidence base — no gap classification, no
    deficit number, no fragility/mixed-scale k/tau^2 entry. This locks the count-side of the fail-closed sweep
    and catches the staleness that let these snapshots keep a suppressed topic's pre-suppression pooled k."""
    supp = set(_suppressed_slugs())
    # The live corpus may have no incompatible admitted pool. Keep a non-vacuous rendering plant.
    control = _incompatible_review()
    assert str(_LEFTOVER) not in page._outcome_block(control["outcomes"][0])
    assert spec_curve(control).get("not_applicable")

    eb = json.load(open(os.path.join(DOCS, "evidence_base.json"), encoding="utf-8"))
    classified = {e["slug"] for bucket in ("complete", "gap_small", "gap_large") for e in eb.get(bucket, [])}
    assert not (supp & classified), f"evidence_base classifies suppressed topics as pooled: {supp & classified}"
    assert supp <= {e["slug"] for e in eb.get("suppressed", [])}, "suppressed topics missing from evidence_base suppressed bucket"

    df = json.load(open(os.path.join(DOCS, "deficit.json"), encoding="utf-8"))
    for slug in supp:
        if slug in df:
            assert df[slug]["deficit"] == "SUPPRESSED", f"deficit.json gives {slug} a numeric deficit"
            assert df[slug]["our_k"] == "suppressed", f"deficit.json gives {slug} a pooled our_k"

    ws = json.load(open(os.path.join(DOCS, "weakness_survey.json"), encoding="utf-8"))
    dims = ws.get("dimensions", {})
    frag = {e.get("topic") for e in dims.get("8_statistical_fragility", []) if isinstance(e, dict)}
    mixed = {e.get("topic") for e in dims.get("8b_mixed_scale_pools", []) if isinstance(e, dict)}
    assert not (supp & frag), f"weakness_survey lists suppressed topics as fragile pools: {supp & frag}"
    assert not (supp & mixed), f"weakness_survey lists suppressed topics as mixed-scale pools: {supp & mixed}"
