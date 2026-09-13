"""Derivation provenance: a pooled number is labelled reported (source gave the effect+CI) vs
reconstructed (harness computed it from arm counts/means) -- the melatonin '-17.4 = trial's own
effect' defect. Tested on the committed corpus objects."""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _prim_trials(slug):
    d = json.load(open(os.path.join(_ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    o = next(x for x in d["outcomes"] if x.get("primary"))
    return o.get("trials") or []


def test_reconstructed_number_labelled():
    # melatonin primary is a harness-computed MD from arm means -> reconstructed.
    ts = _prim_trials("melatonin-primary-insomnia-sol")
    assert ts and all(t.get("derivation") == "reconstructed" for t in ts if t.get("mean1") is not None)


def test_reported_number_labelled():
    # glp1 pools source-reported HRs -> reported.
    ts = _prim_trials("glp1-ra-mace-t2d")
    assert ts and all(t.get("derivation") == "reported" for t in ts if t.get("effect") is not None)


def test_every_pooled_trial_has_a_derivation():
    import glob
    for f in glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json")):
        d = json.load(open(f, encoding="utf-8"))
        for o in d.get("outcomes", []):
            for t in o.get("trials", []):
                if any(t.get(k) is not None for k in ("ai", "mean1", "e1i", "effect")):
                    assert t.get("derivation") in ("reported", "reconstructed"), (f, t.get("id"))
