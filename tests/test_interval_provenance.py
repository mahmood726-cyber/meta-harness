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
