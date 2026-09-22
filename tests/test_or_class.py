import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import estmeasure as em  # noqa: E402
from harness import recovery_recheck as rr  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
CAP_REVIEW = ROOT / "docs" / "reviews" / "corticosteroids-cap-mortality" / "review.json"


def _prefix_cap_review() -> dict:
    blob = subprocess.check_output(
        ["git", "show", "aa8ed28a:docs/reviews/corticosteroids-cap-mortality/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(blob)


def _outcome(review: dict, name: str) -> dict:
    return next(o for o in review["outcomes"] if o.get("name") == name)


def test_prefix_hyperglycaemia_object_was_or_rr_compatible_labels_PLANT():
    pre = _outcome(_prefix_cap_review(), "Hyperglycaemia")
    old = pre["result"]["estmeasure"]
    assert old["status"] == "compatible_labels"
    assert old["classes"] == ["FIRST_EVENT_RATIO"]
    assert set(old["canonicals"]) == {"ODDS_RATIO", "RISK_RATIO"}
    assert set(old["labels"]) == {"OR", "RR"}

    fixed = em.pool_compatibility([em.classify("OR"), em.classify("RR")])
    assert fixed["status"] == "incompatible"
    assert set(fixed["classes"]) == {"FIRST_EVENT_RATIO", "ODDS_RATIO"}


def test_or_only_pool_stays_homogeneous():
    fixed = em.pool_compatibility([em.classify("OR"), em.classify("OR")])
    assert fixed["status"] == "homogeneous"
    assert fixed["classes"] == ["ODDS_RATIO"]
    assert fixed["canonicals"] == ["ODDS_RATIO"]


def test_hr_rr_pool_stays_compatible_labels():
    fixed = em.pool_compatibility([em.classify("HR"), em.classify("RR")])
    assert fixed["status"] == "compatible_labels"
    assert fixed["classes"] == ["FIRST_EVENT_RATIO"]
    assert set(fixed["canonicals"]) == {"HAZARD_RATIO_FIRST_EVENT", "RISK_RATIO"}


def test_rebuilt_hyperglycaemia_is_suppressed_incompatible():
    from _contracts import partition, scale_contract
    review = json.loads(CAP_REVIEW.read_text(encoding='utf-8'))
    cur = _outcome(review, 'Hyperglycaemia')
    partition(CAP_REVIEW.parents[3], CAP_REVIEW.parent.name, cur)
    scale_contract(cur)
    from harness.estmeasure import classify, pool_compatibility
    assert pool_compatibility([classify('OR'), classify('RR')])['status'] == 'incompatible'


def test_or_label_mix_does_not_use_hr_rr_disclosure_text():
    verdict = {
        "hard_incompatible": False,
        "label_mix_small_k": True,
        "effect_measure_labels": ["OR", "RR"],
        "reconstructed_members": [],
    }
    assert rr.disclosure(verdict) is None
