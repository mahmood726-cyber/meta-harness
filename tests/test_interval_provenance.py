"""INFERENCE_LAYER_BYPASS gate: a rendered CI must be stamped by the canonical PM/HKSJ engine.

The iv-iron strand builder computed its OWN z-interval (exp(mu +/- 1.96s)) and shipped it as the
registered result: the point estimate was right, only the interval's ORIGIN was wrong. A check on
the NUMBER cannot catch that. This gate checks the PROVENANCE of every rendered interval: it must
carry synth.CI_PROVENANCE (engine) or be a single trial's own reported CI at k=1 (verbatim). A
hand-rolled interval carries neither and the build refuses it.

Counterpart to PARITY_BY_SHARED_DEFECT: there we agreed with a published number for the wrong
reason; here we produced a right point estimate with a wrong interval. Both: number right, provenance
wrong -- and 'a check on a value cannot catch a defect in the process that produced it.'
"""
import glob
import json
import os

import harness.census as census
from harness.synth import CI_PROVENANCE, Study, pool

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_every_rendered_ci_in_corpus_is_engine_stamped():
    bad = []
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        core = json.load(open(rp, encoding="utf-8"))
        for item in census._interval_provenance_check(core):
            bad.append(f"{slug}::{item['outcome']} -> {item['ci_provenance']}")
    assert not bad, "rendered CIs not stamped by the canonical engine: " + "; ".join(bad)


def test_engine_stamps_the_token():
    r = pool([Study(label="a", effect=0.8, ci_low=0.6, ci_high=1.06),
              Study(label="b", effect=0.74, ci_low=0.58, ci_high=0.94)], scale="RR")
    assert r.ci_provenance == CI_PROVENANCE


def test_PLANT_hand_rolled_interval_is_refused():
    # PLANT: a pooled outcome whose CI was computed outside the engine (no/blank provenance) -- exactly
    # the strand-builder z-interval shape -- must be flagged by the gate.
    core = {"outcomes": [{"name": "X", "result": {"k": 2, "ci_low": 0.64, "ci_high": 0.92}}]}  # no token
    assert census._interval_provenance_check(core), "gate failed to catch an unstamped interval"
    # a WRONG token (a look-alike from a local reimplementation) is also refused
    core2 = {"outcomes": [{"name": "X", "result": {"k": 2, "ci_low": 0.64, "ci_high": 0.92,
                                                   "ci_provenance": "local:z-inverse-variance"}}]}
    assert census._interval_provenance_check(core2)


def test_engine_and_k1_verbatim_pass():
    ok = {"outcomes": [
        {"name": "pooled", "result": {"k": 2, "ci_low": 0.7, "ci_high": 0.9, "ci_provenance": CI_PROVENANCE}},
        {"name": "single", "result": {"k": 1, "ci_low": 0.5, "ci_high": 1.1,
                                      "ci_provenance": "source-reported-CI:k=1-verbatim"}},
        {"name": "suppressed", "result": {"suppressed_incompatible": True, "ci_low": None, "ci_high": None}},
    ]}
    assert census._interval_provenance_check(ok) == []


def test_strand_pools_carry_engine_token():
    p = os.path.join(_ROOT, "docs", "iv_iron_strands.json")
    if not os.path.exists(p):
        return
    d = json.load(open(p, encoding="utf-8"))
    for s in d.get("strands", []):
        if s.get("pool"):
            assert s["pool"].get("ci_provenance") == CI_PROVENANCE, s["strand"]


def test_PLANT_a_single_trial_interval_is_not_stamped_with_the_pooling_method():
    """At k=1 pool() returns the single trial's Wald (z) interval -- there is no tau2, no HKSJ and no t(k-1) (df 0).
    It used to stamp the PM+HKSJ t(k-1) token anyway, so 15 served k=1 outcomes named a method they did not use.
    The k=1 token must say what was done, be accepted by the interval gate, and leave every number unchanged."""
    from harness.synth import CI_PROVENANCE_K1
    from harness import census
    one = [Study(label="a", effect=0.8, ci_low=0.6, ci_high=1.06)]
    r = pool(one, scale="RR")
    assert r.ci_provenance == CI_PROVENANCE_K1 != CI_PROVENANCE
    assert "HKSJ" not in r.ci_provenance and "t(k-1)" not in r.ci_provenance
    import math
    se = (math.log(1.06) - math.log(0.6)) / (2 * 1.959963984540054)
    assert abs(r.ci_low - math.exp(math.log(0.8) - 1.959963984540054 * se)) < 1e-12   # numbers unchanged: z interval
    assert census._interval_provenance_check({"outcomes": [{"name": "o", "result": {
        "k": 1, "ci_low": r.ci_low, "ci_high": r.ci_high, "ci_provenance": r.ci_provenance}}]}) == []
