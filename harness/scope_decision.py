"""SCOPE DECISIONS: whether a trial is inside the review is decided from the PROTOCOL'S OWN TEXT, never inherited from
a comparator's trial list (DOAC-VTE review: the committed search queries the six pivotal UIDs of the comparator's
pooled analysis, so J-EINSTEIN and BOTTICELLI -- both eligible by the protocol's I1-I4 -- were never screened).

A declared decision {trial, decision ELIGIBLE | INELIGIBLE, criteria: [{rule, protocol_span, evidence}]} is verified:
  * every protocol_span must occur verbatim (whitespace-normalised) in protocols/<slug>.md -- else
    SCOPE_RULE_NOT_IN_PROTOCOL;
  * every evidence witness is re-hashed and its span required (fail closed);
  * a decision whose stated basis is a comparator's / another review's trial list is SCOPE_INHERITED_FROM_COMPARATOR;
  * a search restriction that makes a trial unreachable is disclosed with the eligible trials it misses.
Declared in docs/scope_decisions.json.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from .comparison_family import _verified

PATH = os.path.join("docs", "scope_decisions.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INHERITED = re.compile(r"comparator'?s? (?:trial )?list|in the comparator|phase[- ]3 trials of the comparator|"
                        r"not in (?:the )?(?:comparator|pooled analysis|other review)", re.I)


def load(root: str, slug: str | None) -> dict[str, Any]:
    p = os.path.join(root, PATH)
    if not slug or not os.path.exists(p):
        return {}
    return ((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or {}


def _protocol_text(root: str, slug: str) -> str:
    p = os.path.join(root, "protocols", slug + ".md")
    return re.sub(r"\s+", " ", open(p, encoding="utf-8").read()) if os.path.exists(p) else ""


def resolve(root: str, slug: str) -> dict[str, Any] | None:
    doc = load(root, slug)
    if not doc:
        return None
    proto = _protocol_text(root, slug)
    out = {"search_limitation": doc.get("search_limitation"), "decisions": [], "problems": []}
    for d in doc.get("decisions") or []:
        crit = []
        for c in d.get("criteria") or []:
            span = re.sub(r"\s+", " ", c.get("protocol_span") or "")
            in_proto = bool(span) and span in proto
            if not in_proto:
                out["problems"].append({"kind": "SCOPE_RULE_NOT_IN_PROTOCOL", "report_id": d.get("trial"),
                                        "detail": f"{d.get('trial')}: {c.get('rule')} span not in the protocol text"})
            ev = (_verified(root, {"witness": c["evidence"]}) or {}).get("text") if c.get("evidence") else None
            crit.append({"rule": c.get("rule"), "protocol_span": span, "in_protocol": in_proto, "evidence": ev,
                         "met": c.get("met")})
        if _INHERITED.search(str(d.get("basis") or "")):
            out["problems"].append({"kind": "SCOPE_INHERITED_FROM_COMPARATOR", "report_id": d.get("trial"),
                                    "detail": f"{d.get('trial')}: the stated basis cites a comparator's trial list"})
        out["decisions"].append({k: d.get(k) for k in ("trial", "ids", "decision", "basis", "not_a_reason",
                                                       "outcome_note")} | {"criteria": crit})
    return out


def attach(review: dict[str, Any], root: str = _ROOT) -> None:
    r = resolve(root, review.get("slug"))
    if r:
        review["scope_decisions"] = r


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    return list((review.get("scope_decisions") or {}).get("problems") or [])
