"""OUTCOME RESTRICTIONS: what an outcome's number may and may not be (docs/outcome_restrictions.json).

An outcome declares its RESTRICTION -- e.g. PCSK9 'Adverse events leading to discontinuation' is UNRESTRICTED: any
adverse event that led to discontinuation, whatever its attribution or cause. A row whose bound span restricts it (FOURIER
Table 3 'Thought to be related to the study agent and leading to discontinuation': the investigator's ATTRIBUTION field,
226 vs 201; ODYSSEY OUTCOMES 'Injection-site reactions ... led to discontinuation ... in 26 patients ... and in 3': a
single CAUSE) is a different outcome and is never pooled into the unrestricted one. Declared per outcome as verbatim
markers; a pooled row whose span or declared attribution carries one fails (OUTCOME_RESTRICTION_MISMATCH).

Two rules hold for every outcome, declared or not:
  POST_HOC_POOLED           a pooled row whose own bound span labels its analysis post hoc (ODYSSEY LONG TERM MACE: the
                            refusal is about the analysis, so pointing at its HR does not lift it)
  COMPONENT_SUM_AS_COMPOSITE a pooled row built by summing component rows (GLAGOV Table 4 lists MI, stroke, ... : patients
                            with several components would be counted more than once; a patient composite is the first
                            event per patient, never a sum)"""
from __future__ import annotations

import json
import os
import re
from typing import Any

PATH = os.path.join("docs", "outcome_restrictions.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_POST_HOC = re.compile(r"\bpost[\s-]?hoc\b", re.I)
_COMPONENT_SUM = re.compile(r"\bsum(?:med)?\s+of\s+(?:the\s+)?(?:component|individual)", re.I)


def load(slug: str | None, root: str = _ROOT) -> dict[str, Any]:
    p = os.path.join(root, PATH)
    if not slug or not os.path.exists(p):
        return {}
    return ((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or {}


def _spans(row: dict[str, Any]) -> str:
    # the BOUND spans only -- never the free-text `source`, which may describe OUR protocol ('amendment, post-hoc')
    return " ".join(" ".join(str(row.get(k) or "").split()) for k in
                    ("source_span", "verbatim_span", "endpoint_result_span"))


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    decl = load(slug, root)
    if decl:
        review["outcome_restrictions"] = decl


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    decl = review.get("outcome_restrictions") or {}
    for o in review.get("outcomes") or []:
        d = decl.get(o.get("name")) or {}
        for row in o.get("trials") or []:
            rid = str(row.get("id"))
            text = _spans(row)
            att = str(row.get("attribution") or "").upper()
            if d.get("restriction") == "UNRESTRICTED":
                hit = next((m for m in d.get("refuse_markers") or [] if re.search(m, text, re.I)), None)
                if hit or (att and att != "ANY"):
                    out.append({"kind": "OUTCOME_RESTRICTION_MISMATCH", "report_id": rid,
                                "detail": f"{o.get('name')}: pooled row is restricted "
                                          f"({'attribution ' + att if att and att != 'ANY' else 'marker ' + repr(hit)}); "
                                          f"the outcome is {d.get('definition')}"})
            if _POST_HOC.search(text):
                out.append({"kind": "POST_HOC_POOLED", "report_id": rid,
                            "detail": f"{o.get('name')}: pooled row's own span labels the analysis post hoc"})
            if row.get("components_summed") or _COMPONENT_SUM.search(str(row.get("derivation") or "")):
                out.append({"kind": "COMPONENT_SUM_AS_COMPOSITE", "report_id": rid,
                            "detail": f"{o.get('name')}: pooled counts were summed from component rows; a patient "
                                      "composite counts each patient's first event once"})
    return out
