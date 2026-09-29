"""Small-k refusal helpers.

The synthesis engine still computes PM/HKSJ exactly as registered. This module decides what may be
served when k=2: no registered HKSJ CI is served, and a two-trial direction conflict refuses the pooled
row entirely.
"""
from __future__ import annotations

import math
import re
from typing import Any

try:
    from scipy.stats import norm as _norm
    _Z = _norm.ppf(0.975)
except Exception:  # pragma: no cover
    _Z = 1.959963984540054

K2_SINGLE_DF = "K2_SINGLE_DF"
K2_SINGLE_DF_CI_SERVED = "K2_SINGLE_DF_CI_SERVED"
WITHHELD_BY_POLICY = "COMPUTED_WITHHELD_BY_PRESENTATION_POLICY"
NOT_COMPUTED = "NOT_COMPUTED"


def withheld_phrase(result: dict[str, Any]) -> str:
    """How a surface names the k=2 registered interval: 'computed, withheld by presentation policy' when the interval
    exists (ci_hksj_unserved), otherwise 'not computed'. Derived from the result, never from a fixed string."""
    ref = (result or {}).get("pooled_ci_refused") or {}
    state = ref.get("state") or (WITHHELD_BY_POLICY if (result or {}).get("ci_hksj_unserved") else NOT_COMPUTED)
    return "computed, withheld by presentation policy" if state == WITHHELD_BY_POLICY else "not computed"


ANCHOR_SCOPE = ("shown alone: one of the two eligible trials, pre-named as the anchor; not the review-wide conclusion, "
                "which is that the two trials conflict in direction")


def pool_withheld_heading(result: dict[str, Any]) -> str:
    """Heading for a k=2 direction-conflict pooled row: a DISPLAY policy, derived from whether the row was computed."""
    ref = (result or {}).get("pool_refused") or {}
    cf = (result or {}).get("counterfactual") or {}
    computed = ref.get("state") == WITHHELD_BY_POLICY or cf.get("would_be_estimate") is not None
    return ("Pooled result computed, withheld by display policy (k=2 direction conflict)" if computed else
            "Pooled result not computed (k=2 direction conflict)")


def anchor_heading(anchor: dict[str, Any]) -> str:
    """How a pre-named single trial is introduced: alone, with its scope, never as the review's conclusion."""
    return f"{anchor.get('name') or anchor.get('label')} alone ({anchor.get('scope') or ANCHOR_SCOPE})"


# Two trials with opposite directions support NO explanatory claim and NO equivalence / no-benefit reading (ticagrelor
# review: PLATO HR 0.84 vs PHILO HR 1.47). A generated sentence that explains the conflict by region / ethnicity, or reads
# it as equivalence or absence of benefit, is refused. Quoted source text is not a generated claim and is not scanned.
_POPULATION_FACTOR = re.compile(
    r"\b(?:region(?:al|s)?|ethnic(?:ity|ities)?|east[\s-]+asian|asian|japanese|korean|taiwanese|chinese|race|racial|"
    r"geograph(?:y|ic|ical)|populations?\s+(?:differences?|effects?)|differences?\s+in\s+(?:the\s+)?(?:trial\s+)?"
    r"populations?|patient\s+populations?)\b", re.I)
_EXPLAINS = re.compile(
    r"\b(?:explain(?:s|ed|ing)?|account(?:s|ed)?\s+for|attribut(?:e|es|ed|able)|driven\s+by|due\s+to|because\s+of|"
    r"owing\s+to|reflect(?:s|ed|ing)?|stem(?:s|med)?\s+from|caused\s+by|may\s+be\s+related\s+to|consistent\s+with)\b",
    re.I)
# the explanation must be ABOUT the conflict / difference, not a description ('the regional recruitment table reflects the
# trial locations' explains nothing about the effects)
_CONFLICT_SUBJECT = re.compile(
    r"\b(?:conflict(?:s|ing)?|discordan(?:t|ce)|disagree(?:s|ment)?|differen(?:t|ce|ces)|heterogeneity|inconsisten(?:t|cy)|"
    r"opposite|direction|diverg(?:e|ent|ence))\b", re.I)
# a withheld or negated proposition is not the claim ('cannot be explained by ethnicity', 'no conclusion can be drawn
# about equivalence', 'the treatments are not equivalent')
_NEGATED = re.compile(
    r"\b(?:cannot|can\s*not|could\s+not|not|no\s+evidence\s+that|without)\s+(?:be\s+)?(?:explain|attribut|equivalen|"
    r"account)|\bno\s+conclusion\b|\bcannot\s+(?:be\s+)?conclude|\bnot\s+(?:possible|appropriate)\s+to\s+conclude\b|"
    r"\bdoes\s+not\s+establish\b", re.I)
_EQUIVALENCE = re.compile(
    r"\b(?:equivalen(?:t|ce)|non-?inferior(?:ity)?|not\s+superior|no\s+(?:statistically\s+)?(?:significant\s+|clear\s+|"
    r"meaningful\s+|overall\s+)?(?:benefit|difference|effect|advantage)|similar\s+(?:efficacy|effect)|"
    r"comparable\s+(?:efficacy|effect)|neutral\s+(?:result|effect|finding)|did\s+not\s+differ|"
    r"neither\s+(?:trial|study)\s+(?:demonstrated|showed|found)\s+(?:a\s+)?benefit)\b", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.;!?])\s+")
_WS = re.compile(r"\s+")


def conflict_claim_violations(text: str) -> list[dict[str, str]]:
    """Generated sentences that explain a k=2 direction conflict by a population factor, or read it as equivalence / no
    benefit. A negated or withheld proposition is not the claim (codex NR-C19 cases, each reproduced by execution)."""
    bad = []
    for s in _SENT_SPLIT.split(_WS.sub(" ", text or "")):
        if _NEGATED.search(s):
            continue
        if _POPULATION_FACTOR.search(s) and _EXPLAINS.search(s) and _CONFLICT_SUBJECT.search(s):
            bad.append({"kind": "EXPLANATORY_CLAIM", "sentence": s.strip()})
        elif _EQUIVALENCE.search(s):
            bad.append({"kind": "EQUIVALENCE_OR_NO_BENEFIT", "sentence": s.strip()})
    return bad


def common_effect_promotion_violations(result: dict[str, Any]) -> list[str]:
    """The common-effect (z-based) interval is a sensitivity row only: it is never the served primary interval, however
    much narrower it is. When the registered interval is withheld, the served primary interval must be empty."""
    if not isinstance(result, dict) or result.get("ci_low_fixed") is None:
        return []
    bad = []
    lo, hi = result.get("ci_low"), result.get("ci_high")
    if result.get("pooled_ci_refused") and (lo is not None or hi is not None):
        bad.append("registered interval withheld at k=2 but a primary interval is served")
    if lo is not None and hi is not None and (lo, hi) == (result.get("ci_low_fixed"), result.get("ci_high_fixed")):
        bad.append("the served primary interval IS the common-effect interval")
    return bad
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
    computed = old_lo is not None or old_hi is not None
    # PRESENTATION POLICY, not a computational failure: the PM/HKSJ interval IS computed (kept in ci_hksj_unserved) and
    # withheld because t(1)=12.71 on one degree of freedom is not a reliable basis for a served pooled interval. The state
    # is derived from whether the interval exists, never asserted (lane NR V1.0.1, statins-older-adults addendum).
    result["pooled_ci_refused"] = {
        "code": K2_SINGLE_DF,
        "state": WITHHELD_BY_POLICY if computed else NOT_COMPUTED,
        "detail": (("Registered PM/HKSJ interval computed (t(1)=12.71 at k=2) and withheld by presentation policy: a "
                    "single degree of freedom is not a reliable basis for a served pooled confidence interval. This is "
                    "not a computational failure; the computed interval is kept for audit.") if computed else
                   ("Registered PM/HKSJ interval not computed at k=2; no pooled confidence interval is served.")),
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
            "note": ("computed, withheld by display policy: the two k=2 trials conflict in direction or interval "
                     "support, so the row is not a served pooled result"),
        }
        anchor, remainders = _match_anchor(trials or [], anchor_config, result.get("scale"))
        computed = old.get("would_be_estimate") is not None
        if anchor:
            # the anchor is ONE trial shown alone; it is never the review-wide conclusion (ticagrelor review: PLATO)
            anchor["scope"] = ANCHOR_SCOPE
        # a DISPLAY policy, not a computational failure: the pooled row is computed (kept in `counterfactual`) and
        # withheld; the state is derived from whether it exists (lane NR V1.0.1, ticagrelor review)
        result["pool_refused"] = {
            "code": DIRECTION_CONFLICT_K2,
            "policy": "DISPLAY",
            "state": WITHHELD_BY_POLICY if computed else NOT_COMPUTED,
            "detail": (("k=2 pooled row computed, withheld by display policy because " if computed else
                        "k=2 pooled row not computed because ") + "; ".join(diag.get("reasons") or [])),
            "rule": ("At k=2, if point estimates are on opposite sides of the null or trial CIs do not "
                     "overlap, the pooled row is withheld from display. A single trial is shown alone only when it is "
                     "explicitly pre-named in the topic configuration/protocol metadata, and never as the review's "
                     "conclusion; otherwise both trials are shown only as named individual results."),
            "diagnostics": diag,
            **({"honest_k1_anchor": anchor, "named_remainders": remainders} if anchor else {}),
        }
        result["counterfactual"] = old
        if old.get("would_be_ci_low") is not None or old.get("would_be_ci_high") is not None:
            result["ci_hksj_unserved"] = {
                "ci_low": old.get("would_be_ci_low"),
                "ci_high": old.get("would_be_ci_high"),
                "method": "PM tau^2 + HKSJ on t(1)",
                "note": "computed; withheld by display policy with the k=2 pooled row (kept for audit)",
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
