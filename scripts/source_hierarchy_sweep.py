"""Corpus sweep for source-hierarchy estimator switches.

Offline only: reads the served review corpus and committed cache, rebuilds each
core, and reports pooled rows where the source-hierarchy selector chose a
published effect+CI over a reconstruction.
"""
from __future__ import annotations

import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import fetch  # noqa: E402
from harness.pipeline import build_review_core, _pool_result  # noqa: E402
from harness.registration import protocol_sha  # noqa: E402
from harness.synth import Study  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _span(text, limit=200):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def _trial_value(t):
    if t.get("effect") is not None:
        return {
            "effect": t.get("effect"),
            "scale": t.get("scale"),
            "ci_low": t.get("ci_low"),
            "ci_high": t.get("ci_high"),
        }
    if t.get("ai") is not None:
        return {
            "ai": t.get("ai"),
            "n1i": t.get("n1i"),
            "ci": t.get("ci"),
            "n2i": t.get("n2i"),
            "implied_rr": t.get("implied_rr"),
        }
    return {k: t.get(k) for k in ("derivation", "scale") if t.get(k) is not None}


def _pooled_scale(trials, declared):
    meas = (declared or "RR").upper()
    meas = meas if meas in ("RR", "OR") else "RR"
    if trials and all(t.get("e1i") is not None for t in trials):
        return "IRR"
    if trials and all(t.get("mean1") is not None for t in trials):
        return "MD"
    if trials and all(t.get("scale") for t in trials) and len({t["scale"] for t in trials}) == 1:
        return trials[0]["scale"]
    return declared or "RR"


def _measure_for_trial(t, declared):
    meas = (declared or "RR").upper()
    meas = meas if meas in ("RR", "OR") else "RR"
    if t.get("e1i") is not None:
        return "IRR"
    if t.get("mean1") is not None:
        return "MD"
    return meas


def _pool(trials, declared):
    scale = _pooled_scale(trials, declared)
    studies = [
        Study(
            label=t.get("label"),
            ai=t.get("ai"),
            n1i=t.get("n1i"),
            ci=t.get("ci"),
            n2i=t.get("n2i"),
            effect=t.get("effect"),
            ci_low=t.get("ci_low"),
            ci_high=t.get("ci_high"),
            e1i=t.get("e1i"),
            t1i=t.get("t1i"),
            e2i=t.get("e2i"),
            t2i=t.get("t2i"),
            mean1=t.get("mean1"),
            sd1=t.get("sd1"),
            nc1=t.get("nc1"),
            mean2=t.get("mean2"),
            sd2=t.get("sd2"),
            nc2=t.get("nc2"),
            source=t.get("source", ""),
            measure=_measure_for_trial(t, declared),
            derivation=t.get("derivation", ""),
        )
        for t in trials
    ]
    return _pool_result(studies, scale=scale)


def _with_alternative(trial, alt):
    repl = copy.deepcopy(trial)
    for key in (
        "effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i",
        "e1i", "t1i", "e2i", "t2i", "mean1", "sd1", "nc1", "mean2", "sd2", "nc2",
    ):
        repl.pop(key, None)
    for key, val in alt.items():
        if key in {
            "effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i",
            "e1i", "t1i", "e2i", "t2i", "mean1", "sd1", "nc1", "mean2", "sd2", "nc2",
        }:
            repl[key] = val
    repl["derivation"] = alt.get("derivation", repl.get("derivation"))
    repl["source"] = alt.get("source_span") or repl.get("source", "")
    return repl


def main():
    review_root = os.path.join(ROOT, "docs", "reviews")
    slugs = sorted(name for name in os.listdir(review_root) if os.path.isdir(os.path.join(review_root, name)))
    changed = []
    limitations = []
    pooled_rows = 0

    for slug in slugs:
        cfg_path = os.path.join(ROOT, "topics", slug + ".json")
        if not os.path.exists(cfg_path):
            continue
        config = json.load(open(cfg_path, encoding="utf-8"))
        records = fetch.ensure(config, "")
        core = build_review_core(slug, config, records, protocol_sha(slug))
        for outcome in core.get("outcomes", []):
            trials = outcome.get("trials") or []
            pooled_rows += len(trials)
            for idx, trial in enumerate(trials):
                for lim in trial.get("source_hierarchy_limitations") or []:
                    limitations.append({
                        "slug": slug,
                        "outcome": outcome.get("name"),
                        "trial_key": trial.get("id") or trial.get("label"),
                        "code": lim.get("code"),
                        "reason": lim.get("reason"),
                        "citation": lim.get("citation"),
                    })
                if trial.get("selection_rule") != "PUBLISHED_EFFECT_TARGET_CLASS":
                    continue
                alt = next((a for a in trial.get("alternatives") or []
                            if a.get("derivation") == "reconstructed"), None)
                if not alt:
                    continue
                before_trials = list(copy.deepcopy(trials))
                before_trials[idx] = _with_alternative(trial, alt)
                before = _pool(before_trials, outcome.get("estimand"))
                after = outcome.get("result") or {}
                changed.append({
                    "slug": slug,
                    "outcome": outcome.get("name"),
                    "trial_key": trial.get("id") or trial.get("label"),
                    "selection_rule": trial.get("selection_rule"),
                    "reconstructed_value": _trial_value(alt),
                    "published_value": _trial_value(trial),
                    "source_span": _span(trial.get("source")),
                    "before_pool": {
                        "estimate": before.get("estimate"),
                        "scale": before.get("scale"),
                        "ci_low": before.get("ci_low"),
                        "ci_high": before.get("ci_high"),
                    },
                    "after_pool": {
                        "estimate": after.get("estimate"),
                        "scale": after.get("scale"),
                        "ci_low": after.get("ci_low"),
                        "ci_high": after.get("ci_high"),
                    },
                    "pool_changed": (
                        before.get("estimate") != after.get("estimate")
                        or before.get("ci_low") != after.get("ci_low")
                        or before.get("ci_high") != after.get("ci_high")
                        or before.get("scale") != after.get("scale")
                    ),
                })

    out = {
        "summary": {
            "topics": len(slugs),
            "pooled_rows": pooled_rows,
            "rows_changed": len(changed),
            "limitation_rows": len(limitations),
        },
        "changed_rows": changed,
        "limitation_rows": limitations,
    }
    out_path = os.path.join(ROOT, "docs", "source_hierarchy_sweep.json")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"{len(changed)} rows changed of {pooled_rows} pooled rows over {len(slugs)} topics")
    print(f"wrote {os.path.relpath(out_path, ROOT)}")


if __name__ == "__main__":
    main()
