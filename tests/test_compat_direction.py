from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from harness import compat_direction as CD

ROOT = Path(__file__).resolve().parents[1]
BASE = "ad5e7c66"


def _committed_review(slug: str) -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{BASE}:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
    )
    return json.loads(raw.decode("utf-8"))


def _live_review(slug: str) -> dict:
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _primary(review: dict) -> dict:
    return next(o for o in review["outcomes"] if o.get("primary"))


def _direction(review: dict, dimension: str) -> dict:
    rows = CD.review_directions(review)
    return next(r for r in rows if r["outcome"] == _primary(review)["name"] and r["dimension"] == dimension)


def test_finerenone_underclaim_plant_and_rebuilt_consistent():
    pre = _committed_review("finerenone-ckd-t2d-renal")
    sentence = _primary(pre)["result"]["composite_heterogeneity"]
    assert "component sets differ across trials" in sentence
    assert "40% eGFR-decline threshold" in sentence

    pre_dir = _direction(pre, "endpoint_definition")
    assert pre_dir["key_direction"] == CD.ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS
    assert pre_dir["underlying"]["values"] == [
        "KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH"
    ]

    live = _live_review("finerenone-ckd-t2d-renal")
    live_dir = _direction(live, "endpoint_definition")
    assert live_dir["key_direction"] == CD.CONSISTENT
    assert live_dir["underlying"]["values"] == [
        "KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH"
    ]
    assert "composite_heterogeneity" not in _primary(live)["result"]


def test_endpoint_direction_prefers_source_fact_over_display_label():
    review = {
        "slug": "finerenone-ckd-t2d-renal",
        "outcomes": [
            {
                "name": "Kidney composite outcome",
                "primary": True,
                "result": {"k": 2},
                "compat_key": {"endpoint": "trial-defined Kidney composite outcome"},
                "trials": [
                    {
                        "id": "PMID 33264825",
                        "label": "33264825",
                        "endpoint_definition": "Kidney composite outcome",
                    },
                    {
                        "id": "PMID 34449181",
                        "label": "34449181",
                        "endpoint_definition": "Kidney composite outcome",
                    },
                ],
            }
        ],
    }
    row = _direction(review, "endpoint_definition")
    assert row["underlying"]["values"] == [
        "KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH"
    ]
    assert all(p["basis"] != "trial annotation" for p in row["underlying"]["per_trial"])


def test_spironolactone_effect_model_not_derivable_without_rales_cox_span():
    pre = _committed_review("spironolactone-hfref-mortality")
    rales = next(t for t in _primary(pre)["trials"] if t["id"] == "PMID 10471456")
    assert "relative risk of death, 0.70" in rales["source"]
    assert not re.search(r"\bcox\b|proportional[- ]hazards?", rales["source"], re.I)

    row = _direction(pre, "effect_model_class")
    assert row["key_direction"] == CD.NOT_DERIVABLE
    assert "10471456" in row["underlying"]["missing_trials"]


def test_colchicine_postop_overclaim_fires_on_endpoint_and_analysis_set():
    pre = _committed_review("colchicine-postop-af")
    endpoint = _direction(pre, "endpoint_definition")
    analysis = _direction(pre, "analysis_set")
    assert endpoint["key_direction"] == CD.ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS
    assert endpoint["underlying"]["values"] == [
        "POAF_5_MIN",
        "POAF_GE_10_MIN",
        "POAF_GE_30_SEC",
        "POAF_GE_5_MIN",
    ]
    assert analysis["key_direction"] == CD.ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS
    assert analysis["underlying"]["values"] == ["AVAILABLE_CASE", "INTENTION_TO_TREAT"]


def test_synthetic_controls_for_all_key_direction_classes():
    base = {
        "slug": "synthetic",
        "outcomes": [
            {
                "name": "Synthetic composite",
                "primary": True,
                "result": {"k": 2},
                "compat_key": {"endpoint": "composite"},
                "trials": [
                    {"id": "PMID 1", "endpoint_definition": "A"},
                    {"id": "PMID 2", "endpoint_definition": "B"},
                ],
            }
        ],
    }
    assert _direction(base, "endpoint_definition")["key_direction"] == (
        CD.ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS
    )

    under = json.loads(json.dumps(base))
    under["outcomes"][0]["result"]["composite_heterogeneity"] = "component sets differ across trials"
    under["outcomes"][0]["trials"][1]["endpoint_definition"] = "A"
    assert _direction(under, "endpoint_definition")["key_direction"] == (
        CD.ASSERTED_HETEROGENEOUS_UNDERLYING_HOMOGENEOUS
    )

    consistent = json.loads(json.dumps(base))
    consistent["outcomes"][0]["trials"][1]["endpoint_definition"] = "A"
    assert _direction(consistent, "endpoint_definition")["key_direction"] == CD.CONSISTENT

    nd = json.loads(json.dumps(base))
    del nd["outcomes"][0]["trials"][1]["endpoint_definition"]
    assert _direction(nd, "endpoint_definition")["key_direction"] == CD.NOT_DERIVABLE


def test_sweep_writes_separate_direction_counts():
    subprocess.run(
        ["python", "scripts/compat_direction_sweep.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    out = json.loads((ROOT / "docs" / "compat_direction_sweep.json").read_text(encoding="utf-8"))
    assert "over_claiming" in out["summary"]
    assert "under_claiming" in out["summary"]
    assert "not_derivable" in out["summary"]
