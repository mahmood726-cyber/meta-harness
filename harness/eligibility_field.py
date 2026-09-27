"""EXPLICIT ELIGIBILITY FIELDS from RETROSPECTIVE protocol clarifications (docs/protocol_clarifications.json).

Esketamine-TRD, 2026-09-27: the protocol says esketamine is "added to a newly-initiated oral antidepressant". Mahmood
clarified after seeing the data (two Dispatch-relayed messages, recorded verbatim): esketamine vs placebo is the
randomised intervention; the oral antidepressant is background therapy that may be newly initiated at/after
randomisation OR in a pre-randomisation lead-in, provided it continues unchanged across arms. This is a FIELD
(`oad_initiation`), set per trial from its own held source text with witness spans -- never a keyword rule.

  resolve(slug)       the clarification, each trial's field value with verified witnesses, what the value means under
                      the governing message, and the sensitivity analysis membership (lead-in-initiated trials)
  screen_override()   a trial whose field qualifies but which ANOTHER recorded rule excludes, with a declared conflict
                      (Takahashi: the phase-2 amendment), is held UNRESOLVED (awaiting classification), never silently
                      included or excluded
  problems(review)    ELIGIBILITY_FIELD_CONFLICT (blocking): a pooled trial whose field does not qualify, or that has
                      no declared value for a field its topic declares
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from .report_family import _witness_text

PATH = os.path.join("docs", "protocol_clarifications.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(root: str = _ROOT) -> dict[str, Any]:
    p = os.path.join(root, PATH)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _norm_id(x) -> str:
    m = re.search(r"NCT\d{8}|\b\d{7,8}\b", str(x or ""))
    return m.group(0) if m else str(x or "")


def _verify(root: str, w: dict[str, Any]) -> str:
    text = " ".join(_witness_text(root, w).split())
    if " ".join(w["span"].split()) not in text:
        raise ValueError(f"eligibility-field witness span not in the held bytes: {w['path']}: {w['span'][:80]!r}")
    return w["span"]


def resolve(slug: str | None, root: str = _ROOT) -> dict[str, Any] | None:
    doc = _load(root)
    clar = next((c for c in doc.get("clarifications") or [] if c.get("topic") == slug), None)
    if not clar:
        return None
    _verify(root, clar["clarifies"])
    meanings = clar["values"]
    trials = []
    for t in (doc.get("fields") or {}).get(slug) or []:
        for w in t.get("witnesses") or []:
            _verify(root, w)
        if t.get("other_rule_conflict"):
            _verify(root, t["other_rule_conflict"]["amendment"])
        trials.append({"trial": t["trial"], "ids": t["ids"], "field": clar["field"], "value": t["value"],
                       "meaning": meanings.get(t["value"], "UNRESOLVED"),
                       "witnesses": [w["span"] for w in t.get("witnesses") or []],
                       **({"other_rule_conflict": t["other_rule_conflict"]} if t.get("other_rule_conflict") else {})})
    sens = clar.get("sensitivity_analysis") or {}
    return {"clarification": {k: clar[k] for k in ("clarification_id", "kind", "decided_after_seeing_data", "label",
                                                   "messages", "field", "values")},
            "clarifies_span": clar["clarifies"]["span"], "trials": trials,
            "sensitivity_analysis": {**sens, "members": [t["trial"] for t in trials
                                                         if t["value"] == sens.get("members_by_value")]}}


def _entry_for(rid: str, slug: str | None, root: str) -> dict[str, Any] | None:
    for t in (_load(root).get("fields") or {}).get(slug) or []:
        if _norm_id(rid) in {_norm_id(i) for i in t["ids"]}:
            return t
    return None


def screen_override(rec: dict[str, Any], rule: str, config: dict[str, Any], root: str = _ROOT) -> dict[str, Any] | None:
    """The replacement row fields for a record whose field qualifies but which another recorded rule excludes under a
    DECLARED conflict; None otherwise (the screen decision stands)."""
    t = _entry_for(rec.get("id"), config.get("slug"), root)
    conf = (t or {}).get("other_rule_conflict")
    if not conf or conf.get("screen_rule") != rule:
        return None
    return {"decision": "awaiting_classification", "rule_id": "A-PROTOCOL-CONFLICT",
            "reason": (f"{t['trial']}: meets the oral-antidepressant field under the retrospective clarification "
                       f"({t['value']}), but is excluded by {conf['rule']}; {conf['why_pending']}"),
            "span": conf["amendment"]["span"][:200],
            "pending": [{"kind": conf["state"], "decision": conf["state"], "detail": conf["why_pending"]},
                        *([{"kind": "MULTI_ARM_SELECTION", "decision": "MULTI_ARM_SELECTION", "detail": conf["also_pending"]}]
                          if conf.get("also_pending") else [])]}


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    r = resolve(slug, root)
    if r:
        review["protocol_clarifications"] = r


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    r = review.get("protocol_clarifications")
    if not r:
        return []
    by_id = {_norm_id(i): t for t in r["trials"] for i in t["ids"]}
    out = []
    for o in review.get("outcomes") or []:
        for t in o.get("trials") or []:
            e = by_id.get(_norm_id(t.get("id")))
            if e is None:
                out.append({"kind": "ELIGIBILITY_FIELD_CONFLICT", "report_id": _norm_id(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} is pooled with no declared {r['clarification']['field']} value"})
            elif not str(e["meaning"]).startswith("QUALIFIES"):
                out.append({"kind": "ELIGIBILITY_FIELD_CONFLICT", "report_id": _norm_id(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} is pooled but its {e['field']} is {e['value']} ({e['meaning']})"})
    return out
