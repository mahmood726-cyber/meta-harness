"""Seventh gate — categorical/membership + methodological proposition contradictions.

The canonical-claim gate closes the NUMERICAL family. This gate closes the other two: a contradiction
that is categorical (a trial BOTH pooled and declared-absent; a suppressed pool that still renders an
estimate; a record BOTH eligible and excluded) or methodological (current headline on an invalidated
topic; a preregistration-precedence claim it cannot support). Each family has a PLANT that fires on the
contradiction, and each check must pass on the clean object (no false positive).
"""
import glob
import json
import os

from harness import proposition as PR

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clean():
    return {
        "outcomes": [{"name": "O", "primary": True,
                      "trials": [{"id": "111"}, {"id": "222"}],
                      "declared_absent_trials": [{"id": "333"}],
                      "result": {"k": 2, "estimate": 0.8, "scale": "RR"}}],
        "screening": {"records": [{"id": "111", "decision": "include"},
                                  {"id": "444", "decision": "exclude"}]},
        "invalidation": {"stale": False},
        "reproduction": {},
    }


def test_clean_object_has_no_contradiction():
    assert PR.contradictions(_clean()) == []


def _fams(cs):
    return {c["proposition"] for c in cs}


def test_PLANT_membership_pooled_and_declared_absent():
    core = _clean()
    core["outcomes"][0]["declared_absent_trials"].append({"id": "111"})  # 111 is also pooled
    cs = PR.contradictions(core)
    assert "pooled_and_declared_absent" in _fams(cs), cs


def test_PLANT_membership_suppressed_and_pooled():
    core = _clean()
    core["outcomes"][0]["result"] = {"suppressed_incompatible": True, "estimate": 0.61, "scale": "RR"}
    cs = PR.contradictions(core)
    assert "suppressed_and_pooled" in _fams(cs), cs


def test_PLANT_membership_eligible_and_excluded():
    core = _clean()
    core["screening"]["records"].append({"id": "111", "decision": "exclude"})  # 111 also included
    cs = PR.contradictions(core)
    assert "eligible_and_excluded" in _fams(cs), cs


def test_PLANT_methodological_current_while_invalidated():
    core = _clean()
    core["invalidation"] = {"stale": True}
    core["headline_current"] = True
    cs = PR.contradictions(core)
    assert "current_while_invalidated" in _fams(cs), cs


def test_PLANT_methodological_prereg_precedence_unsupported():
    core = _clean()
    core["reproduction"] = {"preregistered_before_synthesis": True, "precedence_demonstrated": False}
    cs = PR.contradictions(core)
    assert "prereg_precedence_unsupported" in _fams(cs), cs


def test_stale_topic_alone_is_not_a_contradiction():
    # A STALE topic that does NOT assert current-validity is honest, not contradictory: staleness is
    # disclosed, and byte-reproducibility (deterministic replay) is compatible with staleness. The gate
    # must not fire merely because a topic is stale (iv-iron is legitimately stale and reproducible).
    core = _clean()
    core["invalidation"] = {"stale": True}
    core["reproduction"] = {"reproduces": True}
    assert PR.contradictions(core) == []


def test_GATE_census_refuses_a_planted_contradiction(tmp_path):
    # Every gate must be able to FAIL: plant a pooled-and-declared-absent contradiction into a real,
    # otherwise-valid review object and confirm build_review_dir REFUSES (raises), not just that the
    # detector returns a list. Uses a live review as the renderable base.
    import pytest
    from harness import census
    base = None
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        core = json.load(open(rp, encoding="utf-8"))
        core.pop("reproduction", None)
        prim = next((o for o in core.get("outcomes", []) if o.get("primary") and o.get("trials")), None)
        if prim:
            base = (core, prim, os.path.basename(os.path.dirname(rp)))
            break
    assert base, "no live review with a pooled primary outcome to plant into"
    core, prim, slug = base
    # plant: the first pooled trial is ALSO declared-absent for the same outcome
    prim.setdefault("declared_absent_trials", []).append({"id": prim["trials"][0]["id"], "reason": "PLANT"})
    with pytest.raises(ValueError, match="PROPOSITION CONTRADICTION"):
        census.build_review_dir(core, {"slug": slug}, str(tmp_path), "deadbeef")


def test_corpus_is_contradiction_free():
    bad = {}
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        cs = PR.contradictions(json.load(open(rp, encoding="utf-8")))
        if cs:
            bad[slug] = cs
    assert not bad, "proposition contradictions on the live corpus: " + json.dumps(bad)[:400]
