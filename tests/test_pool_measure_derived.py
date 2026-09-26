"""The pooled effect measure is DERIVED from the admitted inputs, never declared (external review of balanced-crystalloids, 2026-09-26).

The served headline said HR while the 2-trial pool mixed PLUS's count-reconstructed RR (0.9918) with BaSICS's adjusted HR (0.97):
the pipeline fell back to the topic's declared estimand whenever an input carried no stated scale, and estmeasure's FIRST_EVENT_RATIO
class passed HR+RR as 'compatible_labels'. Now: one measure -> that label; several -> refused (POOL_MEASURE_MIXED) unless a
PREDECLARED per-outcome measure_mixture_policy names exactly that mixture (label 'mixed ratio (HR+RR)', policy shown); ADJUSTED beside
UNADJUSTED -> refused unless the policy allows it; the per-adjustment analysis groups are always reported.

The reviewer's reconstruction is the external control: pooling the two served inputs anyway gives 0.97744, tau2 0, Q 0.10970,
common-effect CI 0.91829-1.04040 -- reproduced here with the producer's own synth.pool from the served rows at the pinned candidate."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import estmeasure as em, synth                # noqa: E402
from harness.known_missing import _study_from_trial        # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"         # v1/candidate: the served rows the review measured
SLUG = "balanced-crystalloids-vs-saline-mortality"


def _served_primary():
    p = subprocess.run(["git", "show", f"{PINNED}:docs/reviews/{SLUG}/review.json"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]} is not in this clone's history (never a skip)", pytrace=False)
    return next(o for o in json.loads(p.stdout)["outcomes"] if o.get("primary"))


POLICY = {"measure_mixture_policy": {"allow": ["HR", "RR"], "predeclared": True, "decided_by": "test", "decided_on": "2026-09-26",
                                     "rationale": "synthetic control"}}


def test_the_served_pool_is_declared_hr_over_an_rr_and_an_hr():
    o = _served_primary()
    assert o["result"]["scale"] == "HR"
    labels = [em.input_label(t, "RR") for t in o["trials"]]
    assert sorted(labels) == ["HR", "RR"]                                          # PLUS counts -> RR; BaSICS -> HR
    assert sorted(em.adjustment_of(t) for t in o["trials"]) == ["ADJUSTED", "UNADJUSTED"]
    assert em.pool_compatibility([em.classify(x) for x in labels])["status"] == "compatible_labels"   # the class let it through


def test_the_reviewers_reconstruction_reproduces_with_the_producers_pool():
    o = _served_primary()
    r = synth.pool([_study_from_trial(t, "RR" if t.get("effect") is None else t["scale"]) for t in o["trials"]], scale="HR")
    assert round(r.estimate, 5) == 0.97744 and round(r.tau2, 6) == 0 and round(r.Q, 5) == 0.10970
    assert (round(r.ci_low_fixed, 5), round(r.ci_high_fixed, 5)) == (0.91829, 1.04040)


def test_default_refuses_the_mix_with_its_own_code():
    o = _served_primary()
    labels = [em.input_label(t, "RR") for t in o["trials"]]
    adj = [em.adjustment_of(t) for t in o["trials"]]
    d = em.pool_measure_decision(labels, adj, em.mixture_policy({}))
    assert d["state"] == "REFUSED" and d["code"] == "POOL_MEASURE_MIXED" and d["label"] == "mixed ratio (HR+RR)"


def test_a_predeclared_policy_names_the_mixture_and_the_label_says_so():
    d = em.pool_measure_decision(["RR", "HR"], ["UNSTATED", "UNSTATED"], em.mixture_policy(POLICY))
    assert d["state"] == "MIXED_BY_POLICY" and d["label"] == "mixed ratio (HR+RR)" and d["policy"]["allow"] == ["HR", "RR"]


def test_the_policy_does_not_license_adjusted_beside_unadjusted_unless_it_says_so():
    pol = em.mixture_policy(POLICY)
    assert em.pool_measure_decision(["RR", "HR"], ["UNADJUSTED", "ADJUSTED"], pol)["code"] == "POOL_ADJUSTMENT_MIXED"
    pol2 = em.mixture_policy({"measure_mixture_policy": {**POLICY["measure_mixture_policy"], "allow_adjustment_mixture": True}})
    assert em.pool_measure_decision(["RR", "HR"], ["UNADJUSTED", "ADJUSTED"], pol2)["state"] == "MIXED_BY_POLICY"


@pytest.mark.parametrize("bad", [
    {"allow": ["HR", "RR"], "decided_by": "x", "decided_on": "d", "rationale": "r"},                          # not predeclared
    {"allow": ["HR", "RR"], "predeclared": True, "decided_on": "d", "rationale": "r"},                         # no decider
    {"allow": ["HR"], "predeclared": True, "decided_by": "x", "decided_on": "d", "rationale": "r"},            # not a mixture
    {"allow": ["HR", "MD"], "predeclared": True, "decided_by": "x", "decided_on": "d", "rationale": "r"},      # not ratios
])
def test_an_incomplete_policy_is_no_policy(bad):
    assert em.mixture_policy({"measure_mixture_policy": bad}) is None
    assert em.pool_measure_decision(["RR", "HR"], ["UNSTATED"] * 2, em.mixture_policy({"measure_mixture_policy": bad}))["state"] == "REFUSED"


def test_a_policy_for_one_mixture_does_not_license_another():
    pol = em.mixture_policy(POLICY)
    assert em.pool_measure_decision(["OR", "HR"], ["UNSTATED"] * 2, pol)["code"] == "POOL_MEASURE_MIXED"
    assert em.pool_measure_decision(["OR", "HR", "RR"], ["UNSTATED"] * 3, pol)["code"] == "POOL_MEASURE_MIXED"


def test_one_measure_is_derived_and_an_unknown_measure_refuses():
    assert em.pool_measure_decision(["HR", "HR"], ["UNSTATED"] * 2, None) == {**em.pool_measure_decision(["HR", "HR"], ["UNSTATED"] * 2, None),
                                                                                "state": "DERIVED", "label": "HR"}
    assert em.pool_measure_decision(["RR", None], ["UNSTATED"] * 2, None)["code"] == "POOL_MEASURE_UNIDENTIFIED"


def test_counts_pool_as_the_engines_count_measure_not_the_declared_estimand():
    assert em.input_label({"ai": 1, "n1i": 10, "ci": 2, "n2i": 10}, "RR") == "RR"
    assert em.input_label({"ai": 1, "n1i": 10, "ci": 2, "n2i": 10, "scale": "HR"}, "RR") == "RR"    # a label on counts is not a model
    assert em.input_label({"effect": 0.9, "ci_low": 0.8, "ci_high": 1.0, "scale": "hr"}, "RR") == "HR"
    assert em.input_label({"e1i": 3, "t1i": 100, "e2i": 4, "t2i": 100}, "RR") == "IRR"
