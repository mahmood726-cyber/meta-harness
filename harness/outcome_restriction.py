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


_POP = ("estimate", "ci_low", "ci_high", "tau2", "estimate_fixed", "ci_low_fixed", "ci_high_fixed", "pi_low", "pi_high",
        "leave_one_out", "pi_note", "fixed_note", "ci_note")


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    """Record the declarations; for a DEFINITION_TYPED outcome, type every pooled row (its own harm_definition_key, else
    the witnessed per-trial declaration, else UNTYPED) and SUPPRESS a pool whose rows carry more than one definition --
    the per-trial estimates stay, the would-be number is quarantined as a counterfactual (the estmeasure pattern)."""
    decl = load(slug, root)
    if not decl:
        return
    review["outcome_restrictions"] = decl
    from .comparison_family import _verified
    for o in review.get("outcomes") or []:
        d = decl.get(o.get("name")) or {}
        if d.get("restriction") != "DEFINITION_TYPED":
            continue
        by_trial = d.get("definitions_by_trial") or {}
        for row in o.get("trials") or []:
            if row.get("harm_definition_key"):
                continue
            pid = re.sub(r"^PMID\s*", "", str(row.get("id") or ""))
            dt = by_trial.get(pid)
            if dt:
                _verified(root, {"witness": dt["witness"]})        # fail closed: the definition is held
                row["harm_definition_key"], row["harm_definition"] = dt["key"], dt["definition"]
            else:
                row["harm_definition_key"] = "UNTYPED"
        strata = {}
        for row in o.get("trials") or []:
            strata.setdefault(row["harm_definition_key"], []).append(str(row.get("id")))
        res = o.get("result") or {}
        if len(strata) > 1 and not res.get("suppressed_incompatible"):
            res["counterfactual"] = {"reason_code": "INCOMPATIBLE_DEFINITIONS", "would_be_estimate": res.get("estimate"),
                                     "would_be_ci_low": res.get("ci_low"), "would_be_ci_high": res.get("ci_high"),
                                     "note": ("what pooling these different definitions would have yielded; INVALID, shown "
                                              "only so the refusal is auditable, never as a result")}
            for k in _POP:
                res.pop(k, None)
            res["suppressed_incompatible"] = True
            res["definition_strata"] = strata
            res["suppressed_reason"] = (
                "pooled effect SUPPRESSED: the trials define this harm differently ("
                + "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(strata.items()))
                + ") -- different definitions are different quantities. The per-trial estimates are shown; a pool "
                  "within one definition is a decision for the reviewer.")
            o["result"] = res
        elif strata:
            res["definition_strata"] = strata


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
        # DEFINITION_MIX_POOLED: harm rows carry a typed definition (sacubitril-HFrEF: symptomatic hypotension vs a
        # reported AE with SBP <90 vs symptomatic SBP <=85; laboratory K >5.5 vs >=5.5 vs a CODED hyperkalaemia AE).
        # Different definitions are different quantities and are never pooled into one number without a decision.
        keys = sorted({str(r.get("harm_definition_key")) for r in o.get("trials") or [] if r.get("harm_definition_key")})
        if (len(keys) > 1 and not (o.get("result") or {}).get("suppressed_incompatible")
                and not (d.get("definition_pooling_decided") or {}).get("keys") == keys):
            out.append({"kind": "DEFINITION_MIX_POOLED", "report_id": ";".join(str(r.get("id")) for r in o["trials"]),
                        "detail": f"{o.get('name')}: pooled rows carry different definitions {keys}; no pooling "
                                  "decision covers them"})
    return out
