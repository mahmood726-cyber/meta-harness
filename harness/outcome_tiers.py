"""The served OUTCOME label is derived from the pooled inputs, never declared; two tiers (external review of colchicine-postop-af,
2026-09-26).

The served label ("ITT, in-hospital / index-admission AF") came from the topic's declared outcome, while the inputs differed:
END-AF >=5 min during hospitalisation, COPPS-2 >30 s within 3 months, a 14-day available-case analysis. Measured at v1/candidate: on
26 of 27 served primary pools the label is not derived from the inputs -- most inputs' window / analysis set / definition were
COPIED onto them from the label itself (compat_dimensions source outcome.timepoint / outcome.name / study_effect.analysis_population,
the last filled from the declared population), so the label was "confirmed" by itself.

Per input and dimension this module records the value and whether it is DERIVED (the input's own committed source text, registry
timeframe, definition audit) or COPIED (from the label). Then:
  derived_label  per dimension: the single derived value; "mixed: a | b" when derived values differ; or
                 "declared <x>: not shown for n of k inputs" when any input's value was copied -- never the bare declared value
  PRIMARY tier   ONLY against a PREDECLARED per-outcome `common_outcome_policy` ({dimension: [allowed values], predeclared: true,
                 decided_by, decided_on, rationale}): the inputs whose DERIVED values satisfy every constrained dimension. A copied
                 value never satisfies a policy. No policy -> no PRIMARY tier (state NO_POLICY_DECLARED).
  EXPLORATORY    every eligible input, titled "Exploratory: trial-defined <name> across <windows>".
A trial can be eligible without every result entering the primary pool: eligibility is not re-decided here."""
from __future__ import annotations

import json
from typing import Any

DIMENSIONS = ("follow_up_window", "analysis_set", "endpoint_definition")
COPIED_SOURCES = {"outcome.timepoint", "outcome.name", "outcome.population", "study_effect.analysis_population"}
_DECLARED = {"follow_up_window": "timepoint", "analysis_set": "population", "endpoint_definition": "name"}


def _norm(v) -> str:
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True)
    return " ".join(str(v or "").split())


def _compat_key_per_trial(compat_key: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    """The harness's own per-input derivations, where it made them: compat_key.<dim>.per_trial (window, analysis set: value +
    PASS / FAIL / UNKNOWN verdict against the declared value) and trial_defined_dimensions.endpoint_definition.per_trial."""
    ck = compat_key or {}
    out: dict[str, dict[str, Any]] = {}
    for d in ("follow_up_window", "analysis_set"):
        for p in ((ck.get(d) or {}).get("per_trial") or []) if isinstance(ck.get(d), dict) else []:
            out.setdefault(str(p.get("trial")), {})[d] = p
    for p in (((ck.get("trial_defined_dimensions") or {}).get("endpoint_definition") or {}).get("per_trial") or []):
        out.setdefault(str(p.get("trial")), {})["endpoint_definition"] = p
    return out


def input_dimensions(trial: dict[str, Any], ck_per_trial: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    out = {}
    tid = str(trial.get("id") or trial.get("label") or "").replace("PMID ", "")
    own = (ck_per_trial or {}).get(tid) or {}
    for d in DIMENSIONS:
        p = own.get(d)
        if p is not None and p.get("value") not in (None, "not_stated"):
            out[d] = {"value": p.get("value"), "source": "compat_key per-input derivation", "derived": True, "verdict": p.get("verdict")}
            continue
        cd = (trial.get("compat_dimensions") or {}).get(d)
        if not isinstance(cd, dict) or not cd.get("source"):
            out[d] = {"value": None, "source": None, "derived": False}
        else:
            out[d] = {"value": cd.get("value"), "source": cd.get("source"), "derived": cd.get("source") not in COPIED_SOURCES}
        if p is not None and p.get("value") == "not_stated":
            out[d].update(derived=False, verdict=p.get("verdict"), note="the input's own source does not state it")
    return out


def common_policy(spec: dict[str, Any] | None) -> dict[str, Any] | None:
    p = (spec or {}).get("common_outcome_policy")
    if not isinstance(p, dict) or p.get("predeclared") is not True or not all(p.get(k) for k in ("decided_by", "decided_on", "rationale")):
        return None
    constrained = {d: sorted({_norm(x).lower() for x in (p.get(d) or [])}) for d in DIMENSIONS if p.get(d)}
    return {**p, "constrained": constrained} if constrained else None


def derived_label(outcome: dict[str, Any], dims: list[dict[str, dict[str, Any]]]) -> dict[str, Any]:
    lab = {}
    k = len(dims)
    for d in DIMENSIONS:
        copied = sum(1 for x in dims if not x[d]["derived"])
        vals = sorted({_norm(x[d]["value"]) for x in dims if x[d]["derived"]})
        declared = outcome.get(_DECLARED[d])
        if copied:
            lab[d] = {"state": "NOT_SHOWN", "label": f"declared {declared!s}: not shown for {copied} of {k} inputs", "declared": declared}
        elif len(vals) > 1:
            lab[d] = {"state": "MIXED", "label": "mixed: " + " | ".join(vals), "values": vals}
        else:
            lab[d] = {"state": "DERIVED", "label": vals[0] if vals else None}
    lab["matches_inputs"] = all(lab[d]["state"] == "DERIVED" for d in DIMENSIONS)
    return lab


def tiers(outcome: dict[str, Any], trials: list[dict[str, Any]], spec: dict[str, Any] | None) -> dict[str, Any]:
    dims = [input_dimensions(t, _compat_key_per_trial(outcome.get("compat_key"))) for t in trials]
    ids = [str(t.get("id") or t.get("label")) for t in trials]
    pol = common_policy(spec)
    windows = sorted({_norm(x["follow_up_window"]["value"]) for x in dims                       # DERIVED windows only: a value copied
                      if x["follow_up_window"]["derived"] and x["follow_up_window"]["value"] is not None})  # from the label never titles
    n_unshown = sum(1 for x in dims if not x["follow_up_window"]["derived"])
    expl = {"tier": "EXPLORATORY", "trials": ids,
            "title": (f"Exploratory: trial-defined {outcome.get('name')} across "
                      + (("windows " + "; ".join(windows)) if len(windows) > 1 else (windows[0] if windows else "windows not stated"))
                      + (f" (window not shown for {n_unshown} of {len(dims)} inputs)" if n_unshown and windows else ""))}
    if pol is None:
        prim = {"tier": "PRIMARY", "state": "NO_POLICY_DECLARED", "trials": [],
                "reason": "no predeclared common_outcome_policy: no input can be shown to satisfy a common window / definition / population"}
    else:
        keep, excluded = [], []
        for i, x in zip(ids, dims):
            why = [f"{d}: {'value not shown by the input (copied from the label or not stated)' if not x[d]['derived'] else repr(x[d]['value']) + ' not in the policy'}"
                   for d, allowed in pol["constrained"].items()
                   if not x[d]["derived"] or _norm(x[d]["value"]).lower() not in allowed]
            (excluded.append({"trial": i, "why": why}) if why else keep.append(i))
        prim = {"tier": "PRIMARY", "state": "POLICY_APPLIED" if keep else "NO_INPUT_SATISFIES_POLICY", "trials": keep,
                "excluded": excluded, "policy": {k: v for k, v in pol.items() if k != "constrained"}}
    return {"derived_label": derived_label(outcome, dims), "primary": prim, "exploratory": expl,
            "per_input": {i: x for i, x in zip(ids, dims)}}
