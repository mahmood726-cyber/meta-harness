"""RoB-stratified sensitivity re-pool of a review's PRIMARY outcome (Stage RISK OF BIAS, plan R2).

Operates on the finished review dict (outcomes + rob2 attached) and re-pools the primary outcome with the
SAME validated pooler (harness.synth.pool) restricted by risk-of-bias stratum:
  drop_high : exclude overall == 'high' (the standard RoB sensitivity)
  low_only  : keep only overall == 'low'  (strict)
An UNRATED pooled trial cannot be placed in a stratum, so it is excluded from low_only and disclosed via
n_rob_rated. The Study construction and pooled-scale selection are identical to harness.pipeline, and a
test asserts the 'full' re-pool reproduces the shipped primary result (so this cannot drift from it)."""
from __future__ import annotations

from .claimgraph import _stamp, input_set_version, trial_key
from .membership import canonical_trial_key, lookup_by_trial_key, outcome_membership  # noqa: F401
from .synth import Study, pool

LOW_ONLY_IDENTICAL_TO_FULL = "identical_to_full"
LOW_ONLY_FEWER_TRIALS = "fewer_trials"
LOW_ONLY_EMPTY = "empty"
LOW_ONLY_NOT_ASSESSABLE = "not_assessable"
LOW_ONLY_BIAS_SENSITIVITY = "bias_sensitivity"
LOW_ONLY_INFORMATION_AVAILABILITY = "information_availability_sensitivity"
LOW_ONLY_MIXED = "mixed"
LOW_ONLY_RELATIONS = {
    LOW_ONLY_IDENTICAL_TO_FULL,
    LOW_ONLY_FEWER_TRIALS,
    LOW_ONLY_EMPTY,
    LOW_ONLY_NOT_ASSESSABLE,
}
LOW_ONLY_KINDS = {
    LOW_ONLY_BIAS_SENSITIVITY,
    LOW_ONLY_INFORMATION_AVAILABILITY,
    LOW_ONLY_MIXED,
}


def _norm(overall):
    if not overall:
        return None
    o = overall.lower()
    if o.startswith("high"):
        return "high"
    if o.startswith("low"):
        return "low"
    if "some concern" in o:
        return "some_concerns"
    return "other"


def _rob_entry(rob, trial):
    keys = [
        str(trial.get("label") or "").strip(),
        str(trial.get("id") or "").replace("PMID ", "").replace("PMID:", "").strip(),
    ]
    for key in keys:
        if key and key in rob:
            return rob[key]
    return {}


def _studies_and_scale(trials, declared_estimand):
    """Identical to harness.pipeline: Study build + pooled_scale selection."""
    meas = declared_estimand if declared_estimand in ("RR", "OR") else "RR"

    def _meas(t):
        if t.get("e1i") is not None:
            return "IRR"
        if t.get("mean1") is not None:
            return "MD"
        return meas

    studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"),
                     n2i=t.get("n2i"), effect=t.get("effect"), ci_low=t.get("ci_low"),
                     ci_high=t.get("ci_high"), e1i=t.get("e1i"), t1i=t.get("t1i"),
                     e2i=t.get("e2i"), t2i=t.get("t2i"), mean1=t.get("mean1"), sd1=t.get("sd1"),
                     nc1=t.get("nc1"), mean2=t.get("mean2"), sd2=t.get("sd2"), nc2=t.get("nc2"),
                     source=t.get("source", ""), measure=_meas(t),
                     derivation=t.get("derivation", ""), design=t.get("design"),
                     design_adjustment=t.get("design_adjustment"),
                     study_effect=t.get("study_effect")) for t in trials]
    if trials and all(t.get("e1i") is not None for t in trials):
        scale = "IRR"
    elif trials and all(t.get("mean1") is not None for t in trials):
        scale = "MD"
    elif trials and all(t.get("scale") for t in trials) and len({t["scale"] for t in trials}) == 1:
        scale = trials[0]["scale"]
    else:
        scale = declared_estimand or "RR"
    return studies, scale


def _pool(trials, declared_estimand):
    if not trials:
        return None
    studies, scale = _studies_and_scale(trials, declared_estimand)
    r = pool(studies, scale=scale, require_study_effect=all(t.get("study_effect") for t in trials))
    return {"k": r.k, "estimate": round(r.estimate, 4), "scale": r.scale,
            "ci_low": round(r.ci_low, 4), "ci_high": round(r.ci_high, 4), "tau2": round(r.tau2, 5)}


def low_only_relation(full, low_only) -> str:
    """Classify the low-risk-only re-pool against the full primary-outcome pool."""
    if not full:
        return LOW_ONLY_NOT_ASSESSABLE
    if not low_only:
        return LOW_ONLY_EMPTY
    try:
        full_k = int(full.get("k"))
        low_k = int(low_only.get("k"))
    except (TypeError, ValueError):
        return LOW_ONLY_NOT_ASSESSABLE
    if low_k <= 0:
        return LOW_ONLY_EMPTY
    if low_k == full_k:
        return LOW_ONLY_IDENTICAL_TO_FULL
    if 1 <= low_k < full_k:
        return LOW_ONLY_FEWER_TRIALS
    return LOW_ONLY_NOT_ASSESSABLE


def relation_from_sensitivity(sens: dict | None) -> str:
    """Read the stored relation, falling back for legacy review objects."""
    sens = sens or {}
    relation = sens.get("low_only_relation")
    if relation in LOW_ONLY_RELATIONS:
        return relation
    return low_only_relation(sens.get("full"), sens.get("low_only"))


def low_only_relation_note_html(sens: dict | None) -> str:
    relation = relation_from_sensitivity(sens)
    if relation == LOW_ONLY_IDENTICAL_TO_FULL:
        return " <em>(all pooled trials are low risk; the re-pool is the full pool)</em>"
    if relation == LOW_ONLY_FEWER_TRIALS:
        return " <em>(fewer trials than the full pool &mdash; see coverage)</em>"
    return ""


def low_only_relation_context_html(sens: dict | None) -> str:
    relation = relation_from_sensitivity(sens)
    prefix = low_only_kind_context_html(sens)
    if relation == LOW_ONLY_IDENTICAL_TO_FULL:
        return (prefix + "All pooled trials are low risk, so the low-only re-pool is the full pool; "
                "there is no coverage-driven k reduction in this stratum.")
    if relation == LOW_ONLY_FEWER_TRIALS:
        return (prefix + "An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials "
                "than the full pool reflects both risk of bias and assessment coverage &mdash; read the "
                "widened interval with that caveat, not as instability of the effect.")
    if relation == LOW_ONLY_EMPTY:
        return (prefix + "No pooled trial qualifies as low risk, so the low-only stratum is not estimable; "
                "an empty subgroup is not agreement with the full pool.")
    return prefix + "The low-risk-only relation to the full pool is not assessable from the stored object."


def low_only_relation_context_text(sens: dict | None) -> str:
    relation = relation_from_sensitivity(sens)
    prefix = low_only_kind_context_text(sens)
    if relation == LOW_ONLY_IDENTICAL_TO_FULL:
        return prefix + "all pooled trials are low risk, so the re-pool is the full pool."
    if relation == LOW_ONLY_FEWER_TRIALS:
        return prefix + "read the widened interval with the coverage caveat."
    if relation == LOW_ONLY_EMPTY:
        return prefix + "a low-risk-only subpool was not estimable."
    return prefix + "the low-risk-only relation to the full pool was not assessable."


def _low_only_kind_from_counts(adverse: int, unassessed: int) -> str:
    if adverse and unassessed:
        return LOW_ONLY_MIXED
    if unassessed and not adverse:
        return LOW_ONLY_INFORMATION_AVAILABILITY
    return LOW_ONLY_BIAS_SENSITIVITY


def low_only_kind_context_html(sens: dict | None) -> str:
    sens = sens or {}
    kind = sens.get("low_only_kind")
    if kind not in LOW_ONLY_KINDS:
        return ""
    adverse = int(sens.get("low_only_excluded_adverse") or 0)
    unassessed = int(sens.get("low_only_excluded_unassessed") or 0)
    return (f"Low-only kind: <code>{kind}</code> "
            f"({adverse} adverse rating exclusion(s), {unassessed} unassessed-domain exclusion(s)). ")


def low_only_kind_context_text(sens: dict | None) -> str:
    sens = sens or {}
    kind = sens.get("low_only_kind")
    if kind not in LOW_ONLY_KINDS:
        return ""
    adverse = int(sens.get("low_only_excluded_adverse") or 0)
    unassessed = int(sens.get("low_only_excluded_unassessed") or 0)
    return f"low-only kind {kind} ({adverse} adverse rating exclusions, {unassessed} unassessed-domain exclusions); "


def sensitivity(review):
    """Return the primary-outcome RoB-stratified sensitivity, or None if not applicable."""
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    if not prim or not prim.get("trials"):
        return None
    trials = prim["trials"]
    estimand = prim.get("estimand", "RR")
    rob = (review.get("rob2") or {}).get("trials") or {}
    membership = outcome_membership(prim, review)
    pooled_keys = membership.get("pooled") or [str(t.get("id")) for t in trials]

    def _lvl(t):
        return _norm((rob.get(trial_key(t)) or {}).get("overall"))

    levels = {trial_key(t): _lvl(t) for t in trials}
    n_rated = sum(1 for v in levels.values() if v)
    excluded_levels = [v for v in levels.values() if v != "low"]
    excluded_adverse = sum(1 for v in excluded_levels if v in {"high", "some_concerns", "other"})
    excluded_unassessed = sum(1 for v in excluded_levels if v is None)
    low_only_kind = _low_only_kind_from_counts(excluded_adverse, excluded_unassessed)
    full = _pool(trials, estimand)
    drop_high = _pool([t for t in trials if _lvl(t) != "high"], estimand)
    low_only = _pool([t for t in trials if _lvl(t) == "low"], estimand)
    relation = low_only_relation(full, low_only)
    # One relation object drives every renderer (FP); the claim graph reads the same relation under
    # its own name so a consumer cannot disagree with the producer (CG).
    low_only_predicate = {LOW_ONLY_FEWER_TRIALS: "fewer_trials",
                          LOW_ONLY_IDENTICAL_TO_FULL: "same_trial_set"}.get(relation, "not_estimable")
    version = input_set_version(prim)
    out = {"outcome": prim["name"], "estimand": estimand, "levels": levels,
           "input_set_version": version,
           "n_trials": len(trials), "n_rob_rated": n_rated, "rob_covered": n_rated == len(trials),
           "any_high": any(v == "high" for v in levels.values()),
           "full": full, "drop_high": drop_high, "low_only": low_only,
           "drop_high_informative": bool(drop_high and full and drop_high["k"] < full["k"] and drop_high["k"] >= 1),
           "low_only_relation": relation,
           "low_only_kind": low_only_kind,
           "low_only_excluded_adverse": excluded_adverse,
           "low_only_excluded_unassessed": excluded_unassessed,
           "low_only_informative": relation == LOW_ONLY_FEWER_TRIALS,
           "low_only_predicate": low_only_predicate}
    # At k=2 the registered CI is refused (K2_SINGLE_DF) on the primary; the stratified re-pools carry
    # the same refusal so the block renders strata + point estimates and no t(1) interval. Marked HERE so
    # a recompute of sensitivity(review) reproduces the stored object byte for byte.
    _refused = ((prim.get("result") or {}).get("pooled_ci_refused") or {}).get("code")
    if _refused:
        for kind in ("full", "drop_high", "low_only"):
            point = out.get(kind)
            if isinstance(point, dict):
                point["ci_hksj_unserved"] = {"ci_low": point.get("ci_low"), "ci_high": point.get("ci_high")}
                point["ci_low"] = None
                point["ci_high"] = None
                point["ci_refused"] = _refused
        out["ci_refused"] = _refused
    if review.get("claimgraph") or (prim.get("result") or {}).get("input_set_version"):
        for kind in ("full", "drop_high", "low_only"):
            point = out.get(kind)
            if isinstance(point, dict):
                _stamp(point, f"rob_sensitivity.{kind}", prim["name"], version)
    return out
