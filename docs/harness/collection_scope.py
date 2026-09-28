"""COLLECTION SCOPE: what a trial's safety collection could and could not ascertain (docs/collection_scope.json).

SELECT collected safety SELECTIVELY -- serious adverse events, adverse events leading to discontinuation, and
prespecified adverse events of special interest; "Nonserious AEs not fulfilling any of the listed criteria were not
systematically collected" (Kushner et al., Obesity 2025). So "any gastrointestinal adverse event" was never
comprehensively ascertained in SELECT. That is a fourth thing, distinct from:
  RETRIEVED_NOT_REPORTED  (the held source does not report it -- it may have been collected)
  NOT_YET_RETRIEVED       (the source that would report it is not held)
  REPORTED_ZERO_EVENTS    (it was ascertained and none occurred)
NOT_SYSTEMATICALLY_COLLECTED says: the trial's own collection rules did not ascertain this outcome; no count from it
is a count of this outcome.

Declared per (trial, outcome) with a held witness of the COLLECTION RULE (fail closed). Never manufactured by summing
overlapping rows -- the serious GI adverse events plus the GI discontinuations are not 'any GI adverse event': a patient
can be in both, and a non-serious GI event that did not lead to discontinuation was never recorded.
  problems(review) -> blocking COLLECTION_SCOPE_POOLED: a pooled row for an outcome its trial did not collect."""
from __future__ import annotations

import json
import os
import re
from typing import Any

PATH = os.path.join("docs", "collection_scope.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pid(x) -> str:
    m = re.search(r"NCT\d{8}|\d{7,8}", str(x or ""))
    return m.group(0) if m else str(x or "")


def load(slug: str | None, root: str = _ROOT) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    if not slug or not os.path.exists(p):
        return []
    return list(((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or [])


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    from .comparison_family import _verified
    decl = load(slug, root)
    if not decl:
        return
    review["collection_scope"] = []
    for d in decl:
        for w in d.get("collection_rule_witnesses") or []:
            _verified(root, {"witness": w})                        # fail closed: the collection rule is held
        review["collection_scope"].append({k: d.get(k) for k in ("trial", "outcome", "collected", "not_collected")}
                                          | {"rule_spans": [w["span"] for w in d.get("collection_rule_witnesses") or []]})
        for o in review.get("outcomes") or []:
            if o.get("name") != d["outcome"]:
                continue
            for row in (o.get("declared_absent_trials") or []) + (o.get("trials") or []):
                if _pid(row.get("id")) == _pid(d["trial"]):
                    row["collection_scope"] = {"state": "NOT_SYSTEMATICALLY_COLLECTED",
                                               "collected": d.get("collected"),
                                               "rule_span": (d.get("collection_rule_witnesses") or [{}])[0].get("span"),
                                               "why": d.get("why")}


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for o in review.get("outcomes") or []:
        for row in o.get("trials") or []:
            if (row.get("collection_scope") or {}).get("state") == "NOT_SYSTEMATICALLY_COLLECTED":
                out.append({"kind": "COLLECTION_SCOPE_POOLED", "report_id": str(row.get("id")),
                            "detail": f"{o.get('name')}: a pooled row for an outcome its trial did not systematically "
                                      "collect (summing overlapping rows never manufactures it)"})
    return out
