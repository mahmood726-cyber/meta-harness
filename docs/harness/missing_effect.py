"""Classify the effect of source-verified known-missing evidence.

This is an invalidation adjunct: if a stale page names an eligible missing
trial and the cache holds that trial's verified effect, re-pool with the missing
trial under the same synth.pool engine and say whether the missing evidence
would move the conclusion across the null.
"""
from __future__ import annotations

import json
import math
import os
from copy import deepcopy
from typing import Any

from .synth import Study, pool

NOT_ESTIMABLE = "not_estimable"
TOWARD_NULL = "toward_null"
AWAY_FROM_NULL = "away_from_null"
REVERSES_TO_EFFECT = "reverses_significance_to_effect"
REVERSES_TO_NULL = "reverses_significance_to_null"


def _ratio_scale(scale: str | None) -> bool:
    return (scale or "").upper() not in {"MD", "SMD"}


def _null(scale: str | None) -> float:
    return 1.0 if _ratio_scale(scale) else 0.0


def _significant(res: dict[str, Any]) -> bool | None:
    if not isinstance(res, dict):
        return None
    if res.get("pool_refused") or res.get("pooled_ci_refused") or res.get("suppressed_incompatible"):
        return False
    lo, hi = res.get("ci_low"), res.get("ci_high")
    if lo is None or hi is None:
        return None
    n = _null(res.get("scale"))
    return bool(hi < n or lo > n)


def _magnitude(estimate: float | None, scale: str | None) -> float | None:
    if estimate is None:
        return None
    if _ratio_scale(scale):
        if estimate <= 0:
            return None
        return abs(math.log(float(estimate)))
    return abs(float(estimate))


def _study_from_trial(t: dict[str, Any]) -> Study:
    return Study(
        label=str(t.get("label") or t.get("trial") or t.get("id") or "trial"),
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
        measure=(t.get("scale") or t.get("measure") or "RR"),
    )


def _result_from_pool(studies: list[Study], scale: str) -> dict[str, Any]:
    r = pool(studies, scale=scale)
    return {
        "k": r.k,
        "scale": r.scale,
        "estimate": r.estimate,
        "ci_low": r.ci_low,
        "ci_high": r.ci_high,
        "tau2": r.tau2,
        "pi_low": r.pi_low,
        "pi_high": r.pi_high,
    }


def classify(primary: dict[str, Any], missing: dict[str, Any]) -> dict[str, Any]:
    """Return missing_evidence_effect + re-pooled details for one missing trial."""
    if not missing.get("effect") or not missing.get("ci_low") or not missing.get("ci_high"):
        return {
            "missing_evidence_effect": NOT_ESTIMABLE,
            "missing_evidence_basis": "no source-verified effect+CI is available for the missing trial",
        }
    trials = list(primary.get("trials") or [])
    if not trials:
        return {
            "missing_evidence_effect": NOT_ESTIMABLE,
            "missing_evidence_basis": "the current page has no poolable primary-trial set",
        }
    scale = missing.get("scale") or (primary.get("result") or {}).get("scale") or primary.get("estimand") or "RR"
    studies = [_study_from_trial(t) for t in trials]
    miss_trial = {
        "label": missing.get("trial") or missing.get("label") or missing.get("id") or "missing trial",
        "effect": missing.get("effect"),
        "ci_low": missing.get("ci_low"),
        "ci_high": missing.get("ci_high"),
        "scale": scale,
        "source": missing.get("source", ""),
    }
    studies.append(_study_from_trial(miss_trial))
    try:
        post = _result_from_pool(studies, scale)
    except Exception as exc:  # noqa: BLE001 - invalidation must never crash a build.
        return {
            "missing_evidence_effect": NOT_ESTIMABLE,
            "missing_evidence_basis": f"re-pool failed: {exc}",
        }

    pre = primary.get("result") or {}
    pre_sig = _significant(pre)
    post_sig = _significant(post)
    if pre_sig is False and post_sig is True:
        klass = REVERSES_TO_EFFECT
    elif pre_sig is True and post_sig is False:
        klass = REVERSES_TO_NULL
    else:
        pre_mag = _magnitude(pre.get("estimate"), pre.get("scale") or scale)
        post_mag = _magnitude(post.get("estimate"), scale)
        if pre_mag is None or post_mag is None:
            klass = NOT_ESTIMABLE
        else:
            klass = AWAY_FROM_NULL if post_mag > pre_mag else TOWARD_NULL
    return {
        "missing_evidence_effect": klass,
        "missing_evidence_basis": (
            f"re-pooled k={post['k']} with {miss_trial['label']} under synth.pool; "
            f"pre_significant={pre_sig}, post_significant={post_sig}"
        ),
        "missing_evidence_repool": {
            "k": post["k"],
            "estimate": round(post["estimate"], 4),
            "ci_low": round(post["ci_low"], 4),
            "ci_high": round(post["ci_high"], 4),
            "tau2": round(post["tau2"], 6),
            "pi_low": round(post["pi_low"], 4),
            "pi_high": round(post["pi_high"], 4),
            "scale": post["scale"],
        },
    }


def primary_outcome(core: dict[str, Any]) -> dict[str, Any] | None:
    outcomes = core.get("outcomes") or []
    return next((o for o in outcomes if o.get("primary")), (outcomes[0] if outcomes else None))


def annotate(core: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    primary = primary_outcome(core)
    out = []
    for row in rows or []:
        item = deepcopy(row)
        item.update(classify(primary or {}, item))
        out.append(item)
    return out


def _load_json(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _candidate_keys(row: dict[str, Any]) -> set[str]:
    keys = set()
    for key in ("id", "pmid", "trial", "nct"):
        value = row.get(key)
        if value:
            keys.add(str(value).replace("PMID ", "").strip())
    return {k for k in keys if k}


def enrich_from_cache(root: str, slug: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy verified effect fields from cache/<slug>/verified_effects.json into matching rows."""
    from .verified_inputs import load
    effects = load(slug, cache_root=os.path.join(root, "cache"))["verified_effects.json"]
    if not effects:
        return rows or []
    primary_name = (_load_json(os.path.join(root, "topics", slug + ".json"))
                    .get("primary_outcome") or {}).get("name")
    out = []
    for row in rows or []:
        item = dict(row)
        hit = None
        for key in _candidate_keys(row):
            from .verified_inputs import entries
            candidates = entries(effects.get(key))
            target = row.get("outcome") or primary_name
            if target:
                # Never borrow an unrelated harm effect, including singleton inputs.
                candidates = [e for e in candidates if e.get("outcome") == target]
            if len(candidates) == 1:
                hit = candidates[0]
                break
        if hit and hit.get("effect") is not None:
            for key in ("effect", "ci_low", "ci_high", "scale", "source", "verification"):
                if key in hit and key not in item:
                    item[key] = hit[key]
        out.append(item)
    return out
