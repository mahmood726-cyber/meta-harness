"""ENDPOINT POLICY: which trial-defined component sets an outcome's pool admits, recorded BEFORE an input is added.

Statins in older adults (2026-09-28): the served 'major vascular events' pool holds JUPITER's and STAREE's own broad
trial-defined composites. HOPE-3's >= 70 result is a 3-POINT outcome (CV death, MI, stroke) -- a different component
set. Admitting it is an endpoint-policy decision, and it must be made and recorded before anyone looks at whether the
resulting interval excludes 1 (a decision taken after seeing the interval is a decision about the interval).

The POLICY is a recorded decision (docs/endpoint_policies.json: id, statement, who decided, basis) and so are PENDING
inputs whose component set no held text types (HOPE-3 >= 70: relayed). Every pooled input's component set is DERIVED
from its own held definition sentence (harness/component_typing.py), never declared.

  attach(review, slug, rec_by_id) -> result['endpoint_policy'] and row['component_set'] on pooled rows
  problems(review)                -> blocking ENDPOINT_POLICY_VIOLATION for a pooled row the policy does not admit:
                                     no derivable component set, or a pending input
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PID = lambda x: (re.search(r"NCT\d{8}|\b\d{7,8}\b", str(x or "")) or re.search("", "")).group(0)
# what each recorded policy admits, as a rule over the DERIVED typing
ADMITS = {"TRIAL_DEFINED_BROAD_COMPOSITE": lambda typed: bool(typed and typed.get("components"))}


def load(root: str = _ROOT) -> dict[str, Any]:
    p = os.path.join(root, "docs", "endpoint_policies.json")
    return (json.load(open(p, encoding="utf-8")).get("topics") or {}) if os.path.exists(p) else {}


def attach(review: dict[str, Any], slug: str | None, rec_by_id: dict[str, Any] | None = None, root: str = _ROOT) -> None:
    from . import component_typing
    decl = load(root).get(slug or "") or {}
    for o in review.get("outcomes") or []:
        d = decl.get(o.get("name"))
        if not d:
            continue
        admits = ADMITS.get((d.get("policy") or {}).get("id"), lambda typed: False)
        pending = {_PID(p.get("input")) for p in d.get("pending") or []}
        inputs = {}
        for t in o.get("trials") or []:
            pid = _PID(t.get("id"))
            typed = component_typing.derive(((rec_by_id or {}).get(pid) or {}).get("abstract"))
            t["component_set"] = typed
            inputs[pid] = {"label": t.get("label") or pid, "component_set": (typed or {}).get("components"),
                           "untyped": (typed or {}).get("untyped"), "definition_span": (typed or {}).get("definition_span"),
                           "admitted_under_policy": pid not in pending and admits(typed)}
        o.setdefault("result", {})["endpoint_policy"] = {"policy": d.get("policy"), "inputs": inputs,
                                                         "pending": d.get("pending") or []}


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for o in review.get("outcomes") or []:
        ep = (o.get("result") or {}).get("endpoint_policy")
        if not ep:
            continue
        pending = {_PID(p.get("input")): p for p in ep.get("pending") or []}
        for t in o.get("trials") or []:
            pid = _PID(t.get("id"))
            inp = (ep.get("inputs") or {}).get(pid) or {}
            if inp.get("admitted_under_policy"):
                continue
            why = (f"its component set {pending[pid].get('component_set')} awaits an endpoint-policy decision "
                   f"({pending[pid].get('state')})" if pid in pending
                   else "no component set could be derived from its held definition sentence")
            out.append({"kind": "ENDPOINT_POLICY_VIOLATION", "report_id": pid,
                        "detail": f"{o.get('name')}: {t.get('id')} is pooled but {why}; policy: "
                                  f"{(ep.get('policy') or {}).get('id')}"})
    return out
