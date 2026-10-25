"""The P3 claim gate: may this bundle claim to MATCH a published meta-analysis?

bundle = {
  "contract": "p3/1.x.y",
  "topic": str,
  "claim": {"kind": "matches_published_meta", "published": str},
  "trials": [{
      "trial_id": str, "measure": "binary"|"continuous"|"ratio",
      "values": [item, ...],          # the SERVED values (what is pooled), each with its passage
      "readings": [reading, reading], # the two independent readings (dual.py)
      "adjudications": [adjudication, ...]
  }, ...]
}
Verdict ALLOW_MATCH_CLAIM only if, for every trial:
  1. every value required by its measure is served, exactly once;
  2. every served value is well-typed, carries a verified passage, and is literally in that passage;
  3. the served values are coherent (events <= total, CI brackets the point, ratios > 0, ...);
  4. every served OUTCOME value is AGREED by independently recorded dual readings and equals
     the resolved value. Differing readings and any proposed human/model adjudication are
     UNRESOLVED until an authenticated, blinded external-review verifier exists; a quoted
     source passage or self-reported reviewer identity alone never promotes a claim.
and the bundle names this contract's major version and has at least one trial. Anything unreadable is REFUSE.
"""
from __future__ import annotations

from . import CONTRACT_MAJOR, CONTRACT_VERSION
from . import fields as F
from .dual import item_problems, resolve, same_value

ALLOW, REFUSE = "ALLOW_MATCH_CLAIM", "REFUSE"


def _label(k):
    return k[0] + (f"[{k[1]}]" if k[1] else "")


def check_trial(trial, docs_root, call_records=None, cache=None) -> dict:
    cache = cache if cache is not None else {}
    tid = str(trial.get("trial_id") or "?")
    measure = trial.get("measure")
    probs = []
    if measure not in F.REQUIRED_BY_MEASURE:
        return {"trial_id": tid, "ok": False, "problems": [f"measure {measure!r} not in {sorted(F.REQUIRED_BY_MEASURE)}"]}
    served = {}
    for it in trial.get("values") or []:
        k = F.key(it)
        if k in served:
            probs.append(f"{_label(k)} served twice")
            continue
        served[k] = it
    for k in F.REQUIRED_BY_MEASURE[measure]:
        if k not in served:
            probs.append(f"{_label(k)} required for a {measure} trial but not served")
    resolved_vals = {}
    for k, it in served.items():
        ip = item_problems(it, docs_root, cache)
        if ip:
            probs += [f"{_label(k)}: {p}" for p in ip]
        else:
            resolved_vals[k] = it["value"]
    probs += F.coherence_problems(resolved_vals)
    dual = resolve(trial.get("readings"), trial.get("adjudications"), docs_root, call_records, cache)
    probs += [f"independence: {p}" for p in dual["independence"]]
    status = {}
    for k, it in served.items():
        spec = F.FIELDS.get(k[0])
        if spec is None or spec.role != "OUTCOME":
            continue
        d = dual["fields"].get(k)
        if d is None:
            probs.append(f"{_label(k)}: OUTCOME value served but neither reader extracted it (no dual reading)")
            status[_label(k)] = "NOT_READ"
            continue
        status[_label(k)] = d["status"]
        if d["status"] == "UNRESOLVED":
            probs.append(f"{_label(k)}: UNRESOLVED -- " + "; ".join(d["problems"]))
        elif not same_value(it.get("value"), d["value"]):
            probs.append(f"{_label(k)}: served {it.get('value')!r} but the dual reading resolved {d['value']!r}")
    return {"trial_id": tid, "ok": not probs, "problems": probs, "dual_status": status}


def check_bundle(bundle, docs_root, call_records=None) -> dict:
    report = {"contract_version": CONTRACT_VERSION, "verdict": REFUSE, "problems": [], "trials": []}
    if not isinstance(bundle, dict):
        report["problems"].append("bundle is not a JSON object")
        return report
    c = str(bundle.get("contract") or "")
    if not (c == CONTRACT_MAJOR or c.startswith(CONTRACT_MAJOR + ".")):
        report["problems"].append(f"bundle contract {c!r} is not {CONTRACT_MAJOR}.x (refused, never coerced)")
        return report
    claim = bundle.get("claim") or {}
    if claim.get("kind") != "matches_published_meta" or not str(claim.get("published") or "").strip():
        report["problems"].append("claim must be {kind: matches_published_meta, published: <which meta-analysis>}")
    trials = bundle.get("trials")
    if not isinstance(trials, list) or not trials:
        report["problems"].append("no trials: an empty bundle cannot support a match claim")
        return report
    ids = [str(t.get("trial_id") or "") for t in trials if isinstance(t, dict)]
    if len(ids) != len(trials) or len(set(ids)) != len(ids) or not all(ids):
        report["problems"].append("every trial needs a unique, non-empty trial_id")
    cache = {}
    for t in trials:
        if isinstance(t, dict):
            report["trials"].append(check_trial(t, docs_root, call_records, cache))
    n_ok = sum(1 for t in report["trials"] if t["ok"])
    report["summary"] = {"trials": len(trials), "trials_ok": n_ok}
    if not report["problems"] and n_ok == len(trials):
        report["verdict"] = ALLOW
    return report
