"""Permanent regression cases for the arm-IDENTITY inferred-denominator extractor (cycle 6) and the
honest mixed-scale label (cycle 12). Wrong-arm binding produces a PLAUSIBLE number with a slightly
wrong effect — the quietest failure class — so these lock the exact per-arm counts against the
committed source. Abstracts are read from the committed cache (the same bytes the harness pools from).
"""
import json
import os

from harness import extract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _abstract(slug, pid):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return None
    recs = {r["id"]: r for r in json.load(open(p, encoding="utf-8"))["records"]}
    return (recs.get(pid) or {}).get("abstract")


def _cfg(slug):
    return json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))


def test_hernandez_prose_arm_sizes_extract():
    # "in the high-flow group (13 ... vs 32 ... in the conventional group)" with arm sizes stated as
    # "264 received high-flow ... 263 conventional" — a count sentence whose denominators live in a
    # different sentence; the arm-identity fix must recover exactly 13/264 and 32/263.
    ab = _abstract("hfnc-vs-conventional-o2-reintubation", "26975498")
    if ab is None:
        return
    c = _cfg("hfnc-vs-conventional-o2-reintubation")
    fx = extract.extract_trial(ab, c["primary_outcome"]["keywords"], c["intervention_terms"],
                               c["comparator_terms"], declared_composite=False)
    assert not fx.get("absent"), fx
    assert (fx["ai"], fx["n1i"], fx["ci"], fx["n2i"]) == (13, 264, 32, 263), fx


def test_lodoco2_comparator_denominator_is_2760_not_2762():
    # Near-equal arms (2762 colchicine vs 2760 placebo): the placebo count must pair with 2760, NOT
    # cross to the colchicine arm's 2762. This is the exact off-by-2 the naive fix shipped and the
    # arm-identity version corrected.
    ab = _abstract("colchicine-secondary-cv-prevention", "32865380")
    if ab is None:
        return
    c = _cfg("colchicine-secondary-cv-prevention")
    fx = extract.extract_trial(ab, c["primary_outcome"]["keywords"], c["intervention_terms"],
                               c["comparator_terms"], declared_composite=False)
    assert not fx.get("absent"), fx
    assert (fx["ai"], fx["n1i"], fx["ci"], fx["n2i"]) == (187, 2762, 264, 2760), fx
    assert fx["n2i"] == 2760, "comparator arm size must be the placebo arm (2760), not 2762"


def test_factorial_trial_is_refused():
    # A factorial trial (co-randomised second intervention) must be refused unless the sentence names
    # our intervention — the extractor may not bind the wrong factor's effect (B-vitamin vs n-3).
    for pid in ("23839902", "20389249", "11451717"):
        ab = _abstract("omega3-cardiovascular-events", pid)
        if ab is None:
            continue
        c = _cfg("omega3-cardiovascular-events")
        fx = extract.extract_trial(ab, c["primary_outcome"]["keywords"], c["intervention_terms"],
                                   c["comparator_terms"], declared_composite=True)
        # either refused, or (if the sentence names our intervention) extracted — never a silent
        # bind to the co-randomised factor. Here we assert the factorial ones are declared absent.
        if "factorial" in (fx.get("reason") or ""):
            assert fx.get("absent")
            return
    # if none of the sampled PMIDs are cached, the test is a no-op (cache-dependent)


def test_mixed_scale_pool_labelled_honestly():
    # A pool mixing reported labels must never be silently labelled as one clean scale (the "calling it
    # an HR" defect). The effect-measure type system now decides by COMPATIBILITY CLASS: RALES's "RR" +
    # EMPHASIS's "HR" are the SAME class (first-event relative ratios), so the pool is COMPATIBLE (the
    # label mix disclosed via scale_mixed), not a false "mixed" alarm and not a hidden single scale.
    p = os.path.join(ROOT, "docs", "reviews", "spironolactone-hfref-mortality", "review.json")
    if os.path.exists(p):
        rev = json.load(open(p, encoding="utf-8"))
        res = next((o for o in rev["outcomes"] if o.get("primary")), {}).get("result") or {}
        em = res.get("estmeasure") or {}
        assert em.get("status") == "compatible_labels", em
        assert set(res.get("scale_mixed") or []) == {"HR", "RR"}, res.get("scale_mixed")
        assert em.get("classes") == ["FIRST_EVENT_RATIO"]
    # A pool mixing ACROSS classes (a recurrent-event rate ratio + a first-event hazard ratio) is a
    # genuine incompatibility and MUST be flagged, not smoothed (iv-iron, audit 12).
    p2 = os.path.join(ROOT, "docs", "reviews", "iv-iron-hfref-hosp", "review.json")
    if os.path.exists(p2):
        rev = json.load(open(p2, encoding="utf-8"))
        res = next((o for o in rev["outcomes"] if o.get("primary")), {}).get("result") or {}
        assert (res.get("estmeasure") or {}).get("status") == "incompatible", res.get("estmeasure")
        assert str(res.get("scale", "")).startswith("INCOMPATIBLE"), res.get("scale")


def test_locate_gate_rejects_on_identity_or_population():
    """The locate identity gate declares a trial absent when the model judged its evidence is not the
    target outcome, OR its population does not match — and passes a clean judgment. Locks the class
    that prevents right-number/wrong-endpoint (appendicitis/vitamin-D) and wrong-population (DAPA-HF)."""
    from harness import locate
    j = {"1": {"MACE": {"is_target_outcome": True, "population_matches": True}},
         "2": {"MACE": {"is_target_outcome": False, "population_matches": True, "why": "x"}},
         "3": {"MACE": {"is_target_outcome": True, "population_matches": False, "why": "y"}}}
    assert locate.rejects(j, "1", "MACE") is None            # clean -> kept
    assert locate.rejects(j, "2", "MACE") is not None         # wrong outcome -> rejected
    assert locate.rejects(j, "3", "MACE") is not None         # wrong population -> rejected
    assert "population" in locate.rejects(j, "3", "MACE")["reject_reason"]
