"""ARM-LABEL SOURCE CONFLICTS: which arm owns a count, when the source's own renderings disagree.

Wade 2010 (PMID 20712869, NCT00397189): the publisher PDF's Table 8 labels n=394 placebo / 395 melatonin; its Table 9
and the held PMC XML label 394 melatonin (PRM) / 395 placebo. Every COUNT is identical across the formats -- which
settles nothing about OWNERSHIP: two renderings of one article that share every number and swap the labels are the
conflict itself, not corroboration of either side.

  docs/arm_label_conflicts.json declares each conflict: every location (held with a witness, or relayed and not held,
  with the reason), and the corroborating sources offered.
  adjudicate(c)   COMPUTED, never declared: ADJUDICATED only when at least one corroborating source that is
                  INDEPENDENT of the conflicting article (a registry's posted results, a published correction) agrees
                  with exactly one reading; otherwise UNRESOLVED. A corroboration from the article itself (another
                  format, identical counts) is recorded and does not count. Nothing is ever auto-flipped.
  problems(rv)    ARM_LABEL_CONFLICT (blocking): an UNRESOLVED conflict on a trial with an arm-dependent pooled row, or a
                  pooled row whose arm orientation contradicts the adjudicated ownership.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from .report_family import _witness_text

PATH = os.path.join("docs", "arm_label_conflicts.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADJUDICATED, UNRESOLVED = "ADJUDICATED_BY_INDEPENDENT_CORROBORATION", "UNRESOLVED"


def load(root: str = _ROOT) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    return list((json.load(open(p, encoding="utf-8")) or {}).get("conflicts") or []) if os.path.exists(p) else []


def _verify(root: str, w: dict[str, Any]) -> None:
    raw = open(os.path.join(root, w["path"]), "rb").read()
    if hashlib.sha256(raw).hexdigest() != w.get("sha256"):
        raise ValueError(f"arm-label witness digest mismatch: {w['path']}")
    if w.get("representation") == "raw bytes":
        ok = w["span"] in raw.decode("utf-8")
    else:
        ok = " ".join(w["span"].split()) in " ".join(_witness_text(root, w).split())
    if not ok:
        raise ValueError(f"arm-label witness span not in the held bytes: {w['path']}: {w['span'][:80]!r}")


def _reading(says: dict[str, str]) -> tuple:
    return tuple(sorted(says.items()))


def adjudicate(c: dict[str, Any], root: str = _ROOT) -> dict[str, Any]:
    for loc in c.get("locations") or []:
        if loc.get("held"):
            _verify(root, loc["witness"])
    for cor in c.get("corroboration") or []:
        for w in cor.get("witnesses") or []:
            _verify(root, w)
    readings = {_reading(l["says"]) for l in c.get("locations") or []}
    independent = [x for x in c.get("corroboration") or []
                   if x.get("independent_of_article") and _reading(x["says"]) in readings]
    agreed = {_reading(x["says"]) for x in independent}
    if len(readings) > 1 and len(agreed) == 1:
        winner = dict(next(iter(agreed)))
        return {"state": ADJUDICATED, "ownership": winner,
                "basis": "; ".join(x["source"] for x in independent),
                "outvoted": [l["location"] for l in c["locations"] if l["says"] != winner]}
    return {"state": UNRESOLVED, "ownership": None,
            "basis": ("no corroboration independent of the article agrees with exactly one reading"
                      + ("; offered corroboration from the article itself does not count" if any(
                          not x.get("independent_of_article") for x in c.get("corroboration") or []) else ""))}


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    mine = [c for c in load(root) if c.get("topic") == slug]
    if mine:
        review["arm_label_conflicts"] = [{"trial_id": c["trial_id"], "what": c["what"],
                                          "locations": [{k: l.get(k) for k in ("location", "says", "held", "basis")}
                                                        for l in c["locations"]],
                                          "corroboration": [{k: x.get(k) for k in ("source", "says", "independent_of_article")}
                                                            for x in c.get("corroboration") or []],
                                          "arm_counts": c.get("arm_counts"),
                                          "experimental_label": c.get("experimental_label"), **adjudicate(c, root)}
                                         for c in mine]


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for c in review.get("arm_label_conflicts") or []:
        pid = re.sub(r"\D", "", c["trial_id"])
        rows = [(o, t) for o in review.get("outcomes") or [] for t in o.get("trials") or [] if pid in str(t.get("id"))]
        arm_rows = [(o, t) for o, t in rows if t.get("n1i") is not None or t.get("nc1") is not None]
        if c["state"] == UNRESOLVED and arm_rows:
            out.append({"kind": "ARM_LABEL_CONFLICT", "report_id": pid,
                        "detail": f"{c['trial_id']}: arm ownership is unresolved but {len(arm_rows)} arm-dependent row(s) are pooled"})
        own = c.get("ownership") or {}
        exp_n = next((int(n) for n, arm in own.items() if arm == c.get("experimental_label", "melatonin")), None) \
            if own else None
        for o, t in arm_rows:
            n1 = t.get("n1i") if t.get("n1i") is not None else None
            if exp_n and n1 is not None and n1 in {int(k) for k in own} and n1 != exp_n:
                out.append({"kind": "ARM_LABEL_CONFLICT", "report_id": pid,
                            "detail": f"{o.get('name')}: the pooled experimental arm has n={n1}, the adjudicated melatonin arm is n={exp_n}"})
    return out
