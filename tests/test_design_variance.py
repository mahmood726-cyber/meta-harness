import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import design_key as D  # noqa: E402
from harness import design_variance as DV  # noqa: E402
from harness.synth import Study  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
BASE = "ad5e7c66e97cf0e328daf7b3e15e7e4d4dda3b1d"
SLUG = "balanced-crystalloids-vs-saline-mortality"
REVIEW_REL = f"docs/reviews/{SLUG}/review.json"


def _review_at_ref(ref=BASE):
    proc = subprocess.run(
        ["git", "show", f"{ref}:{REVIEW_REL}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return json.loads(proc.stdout)


def _current_review():
    return json.loads((ROOT / REVIEW_REL).read_text(encoding="utf-8"))


def _primary(review):
    return next(o for o in review["outcomes"] if o.get("primary"))


def _row_by_id(rows, pmid):
    return next((r for r in rows if pmid in str(r.get("id") or "")), None)


def test_prefix_object_fires_and_rebuilt_object_passes_design_variance_check():
    pre = _review_at_ref()
    assert {
        "HEADLINE_MISSING_DESIGN_CONSUMPTION",
        "DESIGN_REFUSAL_NOT_ENGINE_CODE",
        "GRADE_MISSING_DESIGN_VARIANCE_RATIONALE",
        "STALE_ARM_CONTRAST_DENOMINATOR",
        "STALE_PROTOCOL_CONTROL_EXPECTATION",
    }.issubset(set(DV.check_review(pre)))

    post = _current_review()
    assert DV.check_review(post) == []


def test_split_raw_2x2_refused_before_and_after_fix():
    pre = _primary(_review_at_ref())
    split_pre = _row_by_id(pre.get("design_refusals") or [], "26444692")
    assert split_pre is not None
    assert split_pre["design"] == "CLUSTER_CROSSOVER"

    trial = {"id": "PMID 26444692", "label": "SPLIT", "ai": 87, "n1i": 1152, "ci": 95, "n2i": 1110}
    rec = {"title": "SPLIT", "abstract": "a double-crossover cluster randomized clinical trial"}
    D.stamp_trial(trial, {"26444692": rec}, {}, "RR")
    assert D.needs_design_refusal(trial)
    with pytest.raises(ValueError, match="design action REFUSE|no evidence-backed correlation"):
        Study(
            label="SPLIT",
            ai=trial["ai"],
            n1i=trial["n1i"],
            ci=trial["ci"],
            n2i=trial["n2i"],
            derivation="reconstructed",
            design=trial["design"],
        ).yi_vi()

    post = _primary(_current_review())
    split_post = _row_by_id(post.get("declared_absent_trials") or [], "26444692")
    assert split_post["state"] == DV.ENGINE_CANNOT_CONSUME


def test_balanced_cluster_crossover_rows_are_engine_cannot_consume_or_design_adjusted():
    primary = _primary(_current_review())
    pooled = {str(t.get("id")): t for t in primary.get("trials") or []}
    absent = primary.get("declared_absent_trials") or []
    for pmid in ("29485925", "27749094", "26444692"):
        pooled_row = next((t for key, t in pooled.items() if pmid in key), None)
        if pooled_row:
            corr = ((pooled_row.get("design") or {}).get("correlation_handling") or {}).get("method")
            assert pooled_row.get("selected_estimator") in {"published_adjusted", "reconstructed_with_ICC"}
            assert corr in {"published_model", "published_adjusted_SE", "reconstructed_with_ICC"}
        else:
            row = _row_by_id(absent, pmid)
            assert row["state"] == DV.ENGINE_CANNOT_CONSUME
            assert row["missing"] == DV.MISSING_DESIGN_VARIANCE


def test_icc_design_effect_inflates_variance_by_closed_form_and_becomes_consumable():
    trial = {
        "id": "PMID 11111111",
        "label": "ICC fixture",
        "ai": 20,
        "n1i": 100,
        "ci": 30,
        "n2i": 100,
        "derivation": "reconstructed",
        "design_adjustment": {
            "kind": "ICC_DESIGN_EFFECT",
            "cluster_size": 50,
            "icc": 0.02,
            "source": "fixture",
            "span": "ICC 0.02; average cluster size 50",
        },
    }
    trial["design"] = {
        "design": "CLUSTER",
        "unit_of_randomisation": "CLUSTER",
        "correlation_handling": {"method": "none", "evidence": []},
    }
    yi0, vi0 = DV.raw_log_effect_variance(trial, "RR")
    assert DV.apply_design_adjustment(trial, "RR")
    yi, vi = Study(
        label=trial["label"],
        effect=trial["effect"],
        ci_low=trial["ci_low"],
        ci_high=trial["ci_high"],
        derivation=trial["derivation"],
        design=trial["design"],
        design_adjustment=trial["design_adjustment"],
    ).yi_vi()
    assert yi == pytest.approx(yi0)
    assert vi == pytest.approx(vi0 * (1 + (50 - 1) * 0.02))
    assert trial["design"]["design_action"]["action"] == "ADJUST"


def test_synthetic_parallel_trial_variance_unchanged():
    trial = {
        "id": "PMID 22222222",
        "label": "parallel fixture",
        "ai": 20,
        "n1i": 100,
        "ci": 30,
        "n2i": 100,
        "derivation": "reconstructed",
        "design": {
            "design": "PARALLEL",
            "unit_of_randomisation": "INDIVIDUAL",
            "correlation_handling": {"method": "none", "evidence": []},
            "design_action": {"action": "ALLOW"},
        },
    }
    yi0, vi0 = DV.raw_log_effect_variance(trial, "RR")
    assert DV.apply_design_adjustment(trial, "RR") is False
    yi, vi = Study(
        label=trial["label"],
        ai=trial["ai"],
        n1i=trial["n1i"],
        ci=trial["ci"],
        n2i=trial["n2i"],
        derivation=trial["derivation"],
        design=trial["design"],
    ).yi_vi()
    assert yi == pytest.approx(yi0)
    assert vi == pytest.approx(vi0)


def test_design_consumption_headline_sentence_generated():
    outcome = {
        "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}],
        "design_refusals": [{"id": "PMID 3"}, {"id": "PMID 4"}, {"id": "PMID 5"}],
    }
    assert DV.consumption_summary(outcome)["headline"] == (
        "pooled: the subset this engine can safely consume "
        "(k=2 of 5 eligible with mortality data; 3 refused for want of a variance model)"
    )


def test_factorial_renal_source_reported_marginal_effect_is_usable():
    trial = {
        "id": "PMID 34375394",
        "label": "BaSICS renal fixture",
        "ai": 100,
        "n1i": 1000,
        "ci": 120,
        "n2i": 1000,
        "source": "The balanced-vs-saline marginal renal outcome adjusted risk ratio, 0.97 [95% CI, 0.90-1.05].",
    }
    rec = {
        "title": "BaSICS renal outcome",
        "abstract": (
            "Double-blind, factorial, randomized clinical trial. "
            "There was no significant interaction between fluid type and infusion speed; P = .98."
        ),
    }
    D.stamp_trial(trial, {"34375394": rec}, {}, "RR")
    assert trial["design"]["design"] == "FACTORIAL"
    assert trial["design"]["design_action"]["action"] == "REFUSE"
    assert D.maybe_use_published_adjusted(trial, "RR")
    assert trial["selected_estimator"] == "published_adjusted"
    assert trial["design"]["design_action"]["action"] == "ALLOW_WITH_LABEL"


def test_page_renders_stale_contrast_and_protocol_controls_unrenderable():
    html = (ROOT / "docs" / "reviews" / SLUG / "index.html").read_text(encoding="utf-8")
    assert "UNRENDERABLE stale contrast block" in html
    assert "UNRENDERABLE protocol control expectation" in html
    assert "2 of 2</strong> pooled trials have a parser-confirmed contrast" in html
    assert "2 of 5</strong> pooled trials have a parser-confirmed contrast" not in html
    assert "Eligible with outcome retrieved but refused" in html


def test_design_refusal_sweep_json_shape():
    data = json.loads((ROOT / "docs" / "design_refusal_sweep.json").read_text(encoding="utf-8"))
    assert data["n_pages"] == 32
    assert data["design_refused_trials_of_eligible_with_outcome_trials"]["N"] >= data["design_refused_trials_of_eligible_with_outcome_trials"]["n"]
    assert data["n_pages_headline_k_is_consumable_subset_of_32"]["N"] == 32
    row = next(p for p in data["pages"] if p["slug"] == SLUG)
    assert row["design_refused"] == 3
    assert row["headline_k_is_consumable_subset"] is True
