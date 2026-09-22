import json
import os
import subprocess

from harness import grade, k2, page
from harness.pipeline import _pool_result
from harness.synth import Study


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _prefix(slug):
    raw = subprocess.check_output(
        ["git", "show", f"aa8ed28a:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def _live(slug):
    return json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))


def _primary(review):
    return next(o for o in review["outcomes"] if o.get("primary"))


def test_plant_prefixed_corticosteroids_served_k2_ci_and_live_refuses_it():
    pre = _primary(_prefix("corticosteroids-cap-mortality"))["result"]
    assert pre["k"] == 2 and pre["ci_low"] == 0.0361 and pre["ci_high"] == 8.2605
    assert k2.k2_check(pre) == k2.K2_SINGLE_DF_CI_SERVED

    live = _primary(_live("corticosteroids-cap-mortality"))["result"]
    assert live["k"] == 2 and live["ci_low"] is None and live["ci_high"] is None
    assert live["pooled_ci_refused"]["code"] == k2.K2_SINGLE_DF
    assert live["ci_hksj_unserved"]["ci_low"] == 0.0361
    assert k2.k2_check(live) is None


def test_plant_prefixed_ticagrelor_direction_conflict_and_live_refuses_pool_row():
    pre_o = _primary(_prefix("ticagrelor-vs-clopidogrel-acs"))
    assert k2.k2_check(pre_o["result"], pre_o["trials"]) == k2.DIRECTION_CONFLICT_K2

    import copy
    from _contracts import partition
    served = _primary(_live("ticagrelor-vs-clopidogrel-acs"))
    partition(ROOT, "ticagrelor-vs-clopidogrel-acs", served)
    assert k2.k2_check(served["result"], served["trials"]) is None
    # Preserve the actual k=2 conflict control independently of today's membership.
    live_o = copy.deepcopy(pre_o)
    with open(os.path.join(ROOT, "topics", "ticagrelor-vs-clopidogrel-acs.json"), encoding="utf-8") as f:
        config = json.load(f)
    live = k2.apply_k2_policy(live_o["result"], live_o["trials"], config.get("k2_direction_conflict_anchor"))
    assert live["pool_refused"]["code"] == k2.DIRECTION_CONFLICT_K2
    assert live.get("estimate") is None and live.get("ci_low") is None and live.get("ci_high") is None
    assert live["pool_refused"]["honest_k1_anchor"]["name"] == "PLATO"
    assert [x["label"] for x in live["pool_refused"]["named_remainders"]] == ["PHILO"]
    html = page.render_outcome_block(live_o)
    assert "Pooled result REFUSED" in html and "Honest k=1 anchor" in html
    assert "PLATO" in html and "PHILO" in html


def test_plant_prefixed_ticagrelor_grade_inconsistency_missing_and_live_has_state():
    pre = _prefix("ticagrelor-vs-clopidogrel-acs")
    pre_inc = pre["grade"]["domains"]["inconsistency"]
    assert pre_inc["downgrade"] == 0 and pre_inc["assessed"] is True
    assert k2.k2_grade_check(_primary(pre)["result"], pre_inc) == k2.INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY

    live = _live("ticagrelor-vs-clopidogrel-acs")
    from _contracts import partition
    primary = _primary(live)
    pooled, _ = partition(ROOT, "ticagrelor-vs-clopidogrel-acs", primary)
    if not pooled:
        assert "grade" not in live
    else:
        live_inc = live["grade"]["domains"]["inconsistency"]
        assert k2.k2_grade_check(primary["result"], live_inc) is None
    # Non-vacuous k=2 unassessed-domain control, independent of the current primary pool.
    import copy
    controlled = copy.deepcopy(_primary(pre))
    k2.apply_k2_policy(controlled["result"], controlled["trials"])
    inc = grade._inconsistency_domain(controlled["result"])
    assert inc["not_assessable_automatically"] is True and inc["assessed"] is False


def test_synthetic_k3_pool_serves_ci_unchanged():
    studies = [
        Study(label="a", effect=0.80, ci_low=0.68, ci_high=0.94),
        Study(label="b", effect=0.82, ci_low=0.70, ci_high=0.96),
        Study(label="c", effect=0.78, ci_low=0.66, ci_high=0.92),
    ]
    res = _pool_result(studies, scale="RR")
    assert res["k"] == 3 and res["ci_low"] is not None and res["ci_high"] is not None
    assert "pooled_ci_refused" not in res and k2.k2_check(res) is None


def test_synthetic_k2_concordant_refuses_registered_ci_and_caveats_material_common_effect():
    studies = [
        Study(label="a", effect=0.80, ci_low=0.68, ci_high=0.94),
        Study(label="b", effect=0.82, ci_low=0.70, ci_high=0.96),
    ]
    trials = [{"label": "a", "effect": 0.80, "ci_low": 0.68, "ci_high": 0.94},
              {"label": "b", "effect": 0.82, "ci_low": 0.70, "ci_high": 0.96}]
    res = k2.apply_k2_policy(_pool_result(studies, scale="RR"), trials)
    assert res["ci_low"] is None and res["pooled_ci_refused"]["code"] == k2.K2_SINGLE_DF
    html = page.render_outcome_block({"name": "Synthetic", "result": res, "trials": trials})
    assert "Common-effect sensitivity (z-based; not the registered interval)" in html
    assert "heterogeneity caveat" not in html

    material = dict(res, tau2=0.02, i2=60.0, ci_low=0.1, ci_high=2.0)
    material.pop("pooled_ci_refused", None)
    material.pop("ci_hksj_unserved", None)
    material = k2.refuse_k2_ci(material)
    html2 = page.render_outcome_block({"name": "Synthetic material", "result": material, "trials": trials})
    assert "heterogeneity caveat" in html2


def test_k2_grade_concordant_is_not_assessed_as_clean():
    inc = grade._inconsistency_domain({"k": 2, "tau2": 0.0, "Q": 0.1, "i2": 0.0})
    # Integration 2026-09-16: two concordant trials are an ASSESSABLE state (direction + I^2 computed),
    # so they do not draw the conservative floor; the requirement kept here is that k=2 is never an
    # automatic "no inconsistency" -- assessed stays False and the k2 flag is set.
    assert inc["not_assessable_automatically"] is False
    assert inc["k2_not_automatic"] is True
    assert inc["assessed"] is False
    assert "two concordant trials" in inc["basis"]
