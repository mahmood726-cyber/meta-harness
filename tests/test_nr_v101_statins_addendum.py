"""Lane NR V1.0.1 plants: statins-older-adults review addendum.

(1) A served pooled composite never acquires an unqualified '3-point MACE' label; the label derives from the typed
    component sets of its inputs (harness/composite_label.py).
(2) At k=2 the registered PM/HKSJ interval is labelled 'computed, withheld by presentation policy' -- never as a
    computational failure -- and the narrower common-effect interval is never promoted to primary (harness/k2.py).
(3) Outcome-specific RoB and certainty for statins stay marked unfinished; the pre-release qualifications remain.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from harness import composite_label as cl
from harness import gate, grade, k2

ROOT = Path(__file__).resolve().parents[1]
SLUG = "statins-primary-prevention-elderly"


def _row(pid, comps, span="The primary composite end point was a composite of the listed components."):
    return {"id": f"PMID {pid}", "label": pid, "components": comps, "endpoint_definition_span": span}


def _live():
    return json.load(open(ROOT / "docs" / "reviews" / SLUG / "review.json", encoding="utf-8"))


def _page_text():
    t = open(ROOT / "docs" / "reviews" / SLUG / "index.html", encoding="utf-8").read()
    return t, re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", t)))


def _primary(rev):
    return next(o for o in rev["outcomes"] if o.get("primary"))


# ---- (1) composite label ----------------------------------------------------------------------------------------

THREE_P = ["cardiovascular death", "myocardial infarction", "stroke"]


def test_identical_canonical_sets_earn_the_3_point_label():
    d = cl.derive("3-point major adverse cardiovascular events", [_row("1", THREE_P), _row("2", THREE_P)], {})
    assert d["kind"] == cl.IDENTICAL_3P and cl.THREE_POINT_CLAIM.search(d["label"])
    o = {"name": "3-point major adverse cardiovascular events", "composite_label": d}
    assert cl.served_name(o) == o["name"] and cl.violations({"outcomes": [o]}, "") == []


def test_differing_sets_never_carry_an_unqualified_3_point_label():
    d = cl.derive("3-point major adverse cardiovascular events",
                  [_row("1", THREE_P), _row("2", THREE_P + ["coronary revascularization"])], {})
    assert d["kind"] == cl.DIFFER and not cl.THREE_POINT_CLAIM.search(d["label"])
    o = {"name": "3-point major adverse cardiovascular events", "composite_label": d}
    served = cl.served_name(o)
    assert served != o["name"] and "not a common 3-point set" in served
    # a page that shows only the bare 3-point name is refused; the qualified name passes
    assert cl.violations({"outcomes": [o]}, "<h4>3-point major adverse cardiovascular events</h4>")
    assert cl.violations({"outcomes": [o]}, f"<h4>{served}</h4>") == []


def test_ischaemic_stroke_is_not_silently_all_stroke():
    d = cl.derive("Major adverse cardiovascular events",
                  [_row("1", THREE_P), _row("2", ["CHD_DEATH", "MI", "ISCHEMIC_STROKE"])], {})
    assert d["kind"] == cl.DIFFER and "ischaemic stroke" in d["label"] and "CHD death" in d["label"]


def test_untyped_input_is_stated_not_guessed():
    d = cl.derive("Major vascular events", [_row("1", THREE_P), {"id": "PMID 2", "label": "2"}], {})
    assert d["kind"] == cl.UNTYPED and "not typed for PMID 2" in d["label"]


def test_statins_label_is_trial_defined_composites_that_differ():
    o = _primary(_live())
    lab = o["composite_label"]
    assert lab["kind"] == cl.DIFFER, lab
    assert not cl.THREE_POINT_CLAIM.search(lab["label"])
    by = {i["trial"]: set(i["components"]) for i in lab["inputs"]}
    assert by["PMID 20404379"] == {"cardiovascular death", "coronary revascularization", "myocardial infarction",
                                   "stroke", "unstable angina"}                         # JUPITER, 5 components
    assert by["PMID 42670961"] == {"cardiovascular death", "coronary revascularization", "myocardial infarction",
                                   "stroke"}                                            # STAREE, 4 components
    assert all(i["span"] for i in lab["inputs"])                                        # each from a definition span
    raw, text = _page_text()
    assert "Composite (derived from its inputs' typed component sets) trial-defined composites that differ" in text
    assert not cl.THREE_POINT_CLAIM.search(text)
    assert gate.check_composite_label(str(ROOT / "docs" / "reviews" / SLUG), raw) == []


# ---- (2) the k=2 interval: computed, withheld by presentation policy ---------------------------------------------

def _k2_result(**kw):
    base = {"k": 2, "estimate": 0.68, "ci_low": 0.29, "ci_high": 1.60, "scale": "HR",
            "estimate_fixed": 0.68, "ci_low_fixed": 0.60, "ci_high_fixed": 0.78}
    base.update(kw)
    return base


def test_withheld_interval_is_labelled_computed_not_failed():
    res = k2.refuse_k2_ci(_k2_result())
    ref = res["pooled_ci_refused"]
    assert ref["code"] == k2.K2_SINGLE_DF and ref["state"] == k2.WITHHELD_BY_POLICY
    assert "not a computational failure" in ref["detail"]
    assert res["ci_hksj_unserved"]["ci_low"] == 0.29                       # the computed interval is kept
    assert k2.withheld_phrase(res) == "computed, withheld by presentation policy"


def test_an_interval_that_was_never_computed_is_not_called_computed():
    res = k2.refuse_k2_ci(_k2_result(ci_low=None, ci_high=None))
    assert res["pooled_ci_refused"]["state"] == k2.NOT_COMPUTED
    assert k2.withheld_phrase(res) == "not computed"


def test_common_effect_interval_is_never_promoted_to_primary():
    res = k2.refuse_k2_ci(_k2_result())
    assert k2.common_effect_promotion_violations(res) == []
    promoted = dict(res, ci_low=res["ci_low_fixed"], ci_high=res["ci_high_fixed"])   # narrower, so tempting
    assert k2.common_effect_promotion_violations(promoted)
    k3 = {"k": 3, "ci_low": 0.60, "ci_high": 0.78, "ci_low_fixed": 0.60, "ci_high_fixed": 0.78}
    assert k2.common_effect_promotion_violations(k3) == ["the served primary interval IS the common-effect interval"]


def test_statins_page_says_withheld_by_policy_and_keeps_common_effect_as_sensitivity():
    res = _primary(_live())["result"]
    assert res["ci_low"] is None and res["ci_high"] is None
    assert res["pooled_ci_refused"]["state"] == k2.WITHHELD_BY_POLICY
    assert res["ci_hksj_unserved"]["ci_low"] is not None
    raw, text = _page_text()
    assert "Pooled point estimate (registered CI computed, withheld by presentation policy)" in text
    assert "Registered PM/HKSJ CI computed, withheld by presentation policy (K2_SINGLE_DF)" in text
    for bad in ("REFUSED at k=2", "registered CI refused", "CI refused at k=2", "served pooled CI (refused)"):
        assert bad not in text, bad
    assert "Common-effect sensitivity (z-based; not the registered interval)" in text
    assert gate.check_common_effect_not_promoted(str(ROOT / "docs" / "reviews" / SLUG)) == []


# ---- (3) RoB and certainty stay unfinished; pre-release qualifications remain ------------------------------------

def test_statins_rob_and_certainty_stay_marked_unfinished():
    rev = _live()
    g = rev["grade"]
    assert g["certainty"] == "provisional" and g["certainty_state"] == grade.PROVISIONAL
    rob = g["domains"]["risk_of_bias"]
    assert rob["assessed"] is False and rob["state"] == "NOT_ASSESSABLE"
    assert rob["basis"].startswith("FORMAL RoB 2 NOT YET ASSESSED")
    assert "indirectness" in g["unassessed_domains"] and "risk_of_bias" in g["unassessed_domains"]
    # JUPITER's machine-signal 'some concerns' (post-hoc subgroup) does not turn into a rated certainty
    assert rev["rob2"]["trials"]["20404379"]["overall"] == "some concerns"
    assert g["certainty"] not in {"high", "moderate", "low", "very_low"}


def test_statins_page_keeps_pre_release_and_unfinished_qualifications():
    raw, text = _page_text()
    assert "data-release-status='PRE-RELEASE'" in raw and "PRE-RELEASE — not the reference release." in text
    assert "GRADE provisional -- not yet fully assessable" in text
    assert "formal rob 2 not yet assessed" in text.lower()
    assert "RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed" in text
