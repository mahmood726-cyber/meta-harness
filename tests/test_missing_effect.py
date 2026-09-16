import json
import os
import subprocess

from harness import missing_effect
from harness.synth import Study, pool


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = "ad5e7c66e97cf0e328daf7b3e15e7e4d4dda3b1d"


def _pcsk9_baseline_review():
    got = subprocess.run(
        ["git", "show", f"{BASELINE}:docs/reviews/pcsk9-mace/review.json"],
        cwd=ROOT,
        check=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    return json.loads(got.stdout)


def _primary_from_effects(effects, scale="HR"):
    trials = [
        {
            "label": f"S{i}",
            "effect": effect,
            "ci_low": lo,
            "ci_high": hi,
            "scale": scale,
        }
        for i, (effect, lo, hi) in enumerate(effects, start=1)
    ]
    r = pool(
        [
            Study(label=t["label"], effect=t["effect"], ci_low=t["ci_low"], ci_high=t["ci_high"])
            for t in trials
        ],
        scale=scale,
    )
    return {
        "outcomes": [
            {
                "primary": True,
                "estimand": scale,
                "trials": trials,
                "result": {
                    "k": r.k,
                    "scale": r.scale,
                    "estimate": r.estimate,
                    "ci_low": r.ci_low,
                    "ci_high": r.ci_high,
                    "tau2": r.tau2,
                },
            }
        ]
    }


def test_baseline_has_no_missing_effect_panel():
    baseline = _pcsk9_baseline_review()
    payload = json.dumps(baseline)
    assert "missing_evidence_effect" not in payload
    assert "reverses_significance_to_effect" not in payload


def test_vesalius_missing_effect_reverses_pcsk9_baseline_to_effect():
    baseline = _pcsk9_baseline_review()
    rows = missing_effect.annotate(
        baseline,
        [
            {
                "trial": "VESALIUS-CV",
                "pmid": "41211925",
                "effect": 0.75,
                "ci_low": 0.65,
                "ci_high": 0.86,
                "scale": "HR",
            }
        ],
    )
    assert rows[0]["missing_evidence_effect"] == missing_effect.REVERSES_TO_EFFECT
    assert rows[0]["missing_evidence_repool"]["k"] == 3


def test_concordant_significant_missing_effect_stays_directional():
    core = _primary_from_effects(
        [
            (0.70, 0.60, 0.82),
            (0.72, 0.62, 0.84),
            (0.69, 0.58, 0.82),
        ]
    )
    rows = missing_effect.annotate(
        core,
        [{"trial": "concordant", "effect": 0.68, "ci_low": 0.58, "ci_high": 0.80, "scale": "HR"}],
    )
    assert rows[0]["missing_evidence_effect"] in {
        missing_effect.AWAY_FROM_NULL,
        missing_effect.TOWARD_NULL,
    }


def test_missing_without_source_verified_effect_is_not_estimable():
    core = _primary_from_effects(
        [
            (0.70, 0.60, 0.82),
            (0.72, 0.62, 0.84),
            (0.69, 0.58, 0.82),
        ]
    )
    rows = missing_effect.annotate(core, [{"trial": "unverified"}])
    assert rows[0]["missing_evidence_effect"] == missing_effect.NOT_ESTIMABLE
