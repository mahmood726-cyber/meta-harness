"""SUBGROUP PROVENANCE, derived: whether a pooled input's subgroup/secondary analysis was PRE-SPECIFIED or POST HOC, read
from its own held text with typed spans -- never from the topic's annotation alone.

Statins in older adults (2026-09-28): the topic annotates JUPITER's >= 70 analysis as a 'prespecified_subgroup', while
the report's own abstract says 'exploratory analysis' and 'age cut-point chosen after trial completion'. A protocol claim
the source contradicts is a blocking conflict (SUBGROUP_PROVENANCE_CONFLICT), shown on the row with both spans.

  classify(text) -> {'state': POST_HOC | PRESPECIFIED | CONFLICTING_STATEMENTS | UNSTATED, 'spans': [...]}
  attach(review, config, rec_by_id) -> row['subgroup_provenance'] on pooled rows
  problems(review) -> SUBGROUP_PROVENANCE_CONFLICT where the annotation says prespecified and the source says post hoc
"""
from __future__ import annotations

import re
from typing import Any

POST_HOC = [re.compile(p, re.I) for p in (
    r"\bpost[\s-]?hoc\b", r"\bexploratory (?:\w+\s){0,2}?analys[ie]s\b",
    r"\b(?:age\s+)?(?:cut-?point|cut-?off|threshold)s?\s+(?:was\s+|were\s+)?chosen after\b",
    r"\bnot (?:a\s+)?pre-?specified\b", r"\bnon-?pre-?specified\b")]
PRESPECIFIED = [re.compile(p, re.I) for p in (
    r"\bpre-?specified (?:\w+\s){0,3}?(?:subgroup|analys[ie]s|secondary analys[ie]s)\b",)]
_PID = lambda x: (re.search(r"NCT\d{8}|\b\d{7,8}\b", str(x or "")) or re.search("", "")).group(0)


def classify(text: str | None) -> dict[str, Any]:
    t = text or ""
    post = [m.group(0) for rx in POST_HOC for m in [rx.search(t)] if m]
    pre = [m.group(0) for rx in PRESPECIFIED for m in [rx.search(t)] if m]
    state = ("CONFLICTING_STATEMENTS" if post and pre else "POST_HOC" if post else "PRESPECIFIED" if pre else "UNSTATED")
    return {"state": state, "spans": post + pre}


def attach(review: dict[str, Any], config: dict[str, Any], rec_by_id: dict[str, Any] | None = None) -> None:
    ann = ((config.get("primary_outcome") or {}).get("trial_annotations") or {})
    for o in review.get("outcomes") or []:
        for t in o.get("trials") or []:
            pid = _PID(t.get("id"))
            rec = (rec_by_id or {}).get(pid) or {}
            c = classify(f"{rec.get('title') or ''} {rec.get('abstract') or ''}")
            declared = (ann.get(pid) or {}).get("evidence_unit")
            if c["state"] != "UNSTATED" or (declared and "subgroup" in str(declared)):
                t["subgroup_provenance"] = {**c, "declared_by_topic": declared,
                                            "source": "harness.subgroup_provenance on the report's held title/abstract"}


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for o in review.get("outcomes") or []:
        for t in o.get("trials") or []:
            sp = t.get("subgroup_provenance") or {}
            if str(sp.get("declared_by_topic") or "").startswith("prespecified") and sp.get("state") in (
                    "POST_HOC", "CONFLICTING_STATEMENTS"):
                out.append({"kind": "SUBGROUP_PROVENANCE_CONFLICT", "report_id": _PID(t.get("id")),
                            "detail": (f"{o.get('name')}: the topic calls {t.get('id')} a pre-specified subgroup; its own "
                                       f"text says {sp.get('spans')}")})
    return out
