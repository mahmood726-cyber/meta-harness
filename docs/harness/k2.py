"""Small-k refusal helpers.

The synthesis engine still computes PM/HKSJ exactly as registered. This module decides what may be
served when k=2: no registered HKSJ CI is served, and a two-trial direction conflict refuses the pooled
row entirely.
"""
from __future__ import annotations

import math
from typing import Any

try:
    from scipy.stats import norm as _norm
    _Z = _norm.ppf(0.975)
except Exception:  # pragma: no cover
    _Z = 1.959963984540054

K2_SINGLE_DF = "K2_SINGLE_DF"
K2_SINGLE_DF_CI_SERVED = "K2_SINGLE_DF_CI_SERVED"
DIRECTION_CONFLICT_K2 = "DIRECTION_CONFLICT_K2"
INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY = "INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY"

MATERIAL_I2_THRESHOLD = 25.0
AUTO_INCONSISTENCY_I2_THRESHOLD = 50.0
_EPS = 1e-9


def null_value(scale: str | None) -> float:
    s = (scale or "").upper()
    return 0.0 if s in ("MD", "SMD", "MEAN DIFFERENCE") else 1.0


def is_additive(scale: str | None) -> bool:
    return null_value(scale) == 0.0


def i2_from_q(q: Any, k: Any) -> float | None:
    try:
        qf = float(q)
        ki = int(k)
    except (TypeError, ValueError):
        return None
    if ki < 2:
        return None
    if qf <= 0:
        return 0.0
    return max(0.0, (qf - (ki - 1)) / qf * 100.0)


def material_heterogeneity(result: dict[str, Any]) -> bool:
    tau2 = result.get("tau2")
    i2 = result.get("i2")
    try:
        return float(tau2) > 0 and float(i2) > MATERIAL_I2_THRESHOLD
    except (TypeError, ValueError):
        return False


def _round(x: Any) -> Any:
    return round(x, 4) if isinstance(x, float) else x


def trial_effect_interval(trial: dict[str, Any], scale: str | None) -> dict[str, Any]:
    se_obj = trial.get("study_effect") or {}
    effect = trial.get("effect")
    if effect is None:
        effect = se_obj.get("effect_estimate")
    lo, hi = trial.get("ci_low"), trial.get("ci_high")
    se = se_obj.get("standard_error")
    if effect is not None and (lo is None or hi is None) and se is not None:
        try:
            e = float(effect)
            sef = float(se)
            if is_additive(scale):
                lo, hi = e - _Z * sef, e + _Z * sef
            elif e > 0:
                le = math.log(e)
                lo, hi = math.exp(le - _Z * sef), math.exp(le + _Z * sef)
        except (TypeError, ValueError):
            pass
    return {
        "label": trial.get("label"),
        "id": trial.get("id"),
        "effect": _round(effect),
        "ci_low": _round(lo),
        "ci_high": _round(hi),
        "scale": trial.get("scale") or scale,
    }


def direction_conflict(trials: list[dict[str, Any]], scale: str | None) -> dict[str, Any]:
    infos = [trial_effect_interval(t, scale) for t in (trials or [])]
    out = {"conflict": False, "reasons": [], "trials": infos}
    if len(infos) != 2:
        return out
    null = null_value(scale)
    e1, e2 = infos[0].get("effect"), infos[1].get("effect")
    if e1 is not None and e2 is not None:
        try:
            if (float(e1) < null - _EPS and float(e2) > null + _EPS) or (
                float(e2) < null - _EPS and float(e1) > null + _EPS
            ):
                out["conflict"] = True
                out["reasons"].append("point estimates are on opposite sides of the null")
        except (TypeError, ValueError):
            pass
    lo1, hi1 = infos[0].get("ci_low"), infos[0].get("ci_high")
    lo2, hi2 = infos[1].get("ci_low"), infos[1].get("ci_high")
    if None not in (lo1, hi1, lo2, hi2):
        try:
            if max(float(lo1), float(lo2)) > min(float(hi1), float(hi2)):
                out["conflict"] = True
                out["reasons"].append("trial confidence intervals do not overlap")
        except (TypeError, ValueError):
            pass
    return out


def _match_anchor(trials: list[dict[str, Any]], anchor_config: dict[str, Any] | None,
                  scale: str | None) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if not anchor_config:
        return None, []
    wanted = str(anchor_config.get("id") or anchor_config.get("pmid") or anchor_config.get("label") or "")
    wanted = wanted.replace("PMID ", "").strip()
    if not wanted:
        return None, []
    anchor = None
    remainders = []
    for t in trials or []:
        ids = {str(t.get("label") or ""), str(t.get("id") or ""), str(t.get("id") or "").replace("PMID ", "")}
        info = trial_effect_interval(t, scale)
        if wanted in ids:
            anchor = {
                **info,
                "name": anchor_config.get("name") or anchor_config.get("label") or info.get("label"),
                "basis": anchor_config.get("basis"),
                "rule": anchor_config.get("rule"),
            }
        else:
            remainders.append(info)
    return anchor, remainders


def refuse_k2_ci(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("k") != 2 or result.get("pool_refused"):
        return result
    old_lo, old_hi = result.get("ci_low"), result.get("ci_high")
    result["pooled_ci_refused"] = {
        "code": K2_SINGLE_DF,
        "detail": ("Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a "
                   "pooled confidence interval because a single degree of freedom is not reliable here."),
    }
    if old_lo is not None or old_hi is not None:
        result["ci_hksj_unserved"] = {
            "ci_low": old_lo,
            "ci_high": old_hi,
            "method": "PM tau^2 + HKSJ on t(1)",
            "note": "computed for auditability only; not served as the registered interval at k=2",
        }
    result["ci_low"] = None
    result["ci_high"] = None
    if result.get("ci_low_fixed") is not None:
        result["fixed_note"] = ("common-effect sensitivity (z-based; not the registered interval): this "
                                "uses inverse-variance common-effect weights and a normal quantile, not the "
                                "registered PM/HKSJ interval.")
        if material_heterogeneity(result):
            result["fixed_heterogeneity_caveat"] = (
                f"heterogeneity caveat: tau^2={result.get('tau2')} and I^2={result.get('i2')}% exceed the "
                f"material threshold (tau^2 > 0 and I^2 > {MATERIAL_I2_THRESHOLD:g}%), so the common-effect "
                "interval assumes one common effect and is not a robustness sensitivity to the registered "
                "random-effects model."
            )
    return result


def apply_k2_policy(result: dict[str, Any], trials: list[dict[str, Any]] | None = None,
                    anchor_config: dict[str, Any] | None = None) -> dict[str, Any]:
    if result.get("k") != 2 or result.get("suppressed_incompatible"):
        return result
    diag = direction_conflict(trials or [], result.get("scale"))
    if diag.get("trials"):
        result["k2_trial_diagnostics"] = diag
    if diag.get("conflict"):
        old = {
            "reason_code": DIRECTION_CONFLICT_K2,
            "would_be_estimate": result.get("estimate"),
            "would_be_ci_low": result.get("ci_low"),
            "would_be_ci_high": result.get("ci_high"),
            "would_be_tau2": result.get("tau2"),
            "would_be_i2": result.get("i2"),
            "note": "invalid as a pooled row because the two k=2 trials conflict in direction or interval support",
        }
        anchor, remainders = _match_anchor(trials or [], anchor_config, result.get("scale"))
        result["pool_refused"] = {
            "code": DIRECTION_CONFLICT_K2,
            "detail": "k=2 pooled row refused because " + "; ".join(diag.get("reasons") or []),
            "rule": ("At k=2, if point estimates are on opposite sides of the null or trial CIs do not "
                     "overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly "
                     "pre-named in the topic configuration/protocol metadata; otherwise both trials are "
                     "shown only as named individual results."),
            "diagnostics": diag,
            **({"honest_k1_anchor": anchor, "named_remainders": remainders} if anchor else {}),
        }
        result["counterfactual"] = old
        if old.get("would_be_ci_low") is not None or old.get("would_be_ci_high") is not None:
            result["ci_hksj_unserved"] = {
                "ci_low": old.get("would_be_ci_low"),
                "ci_high": old.get("would_be_ci_high"),
                "method": "PM tau^2 + HKSJ on t(1)",
                "note": "computed for auditability only; not served because the k=2 pooled row is refused",
            }
        for key in ("estimate", "ci_low", "ci_high", "tau2", "estimate_fixed", "ci_low_fixed",
                    "ci_high_fixed", "pi_low", "pi_high", "pi_note", "fixed_note", "leave_one_out"):
            result.pop(key, None)
        return result
    return refuse_k2_ci(result)


def k2_check(result: dict[str, Any], trials: list[dict[str, Any]] | None = None) -> str | None:
    if not isinstance(result, dict) or result.get("k") != 2:
        return None
    if result.get("pool_refused", {}).get("code") == DIRECTION_CONFLICT_K2:
        return None
    if trials and direction_conflict(trials, result.get("scale")).get("conflict"):
        return DIRECTION_CONFLICT_K2
    if (result.get("ci_low") is not None or result.get("ci_high") is not None) and not result.get("pooled_ci_refused"):
        return K2_SINGLE_DF_CI_SERVED
    if result.get("pooled_ci_refused", {}).get("code") == K2_SINGLE_DF:
        return None
    return None


def k2_grade_check(result: dict[str, Any], inconsistency_domain: dict[str, Any] | None) -> str | None:
    if not isinstance(result, dict) or result.get("k") != 2:
        return None
    domain = inconsistency_domain or {}
    if domain.get("not_assessable_automatically"):
        return None
    return INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY
