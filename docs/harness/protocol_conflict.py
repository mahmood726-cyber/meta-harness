"""PROTOCOL CONFLICTS in a registration record: a positive registry statement that contradicts the protocol leaves the
record UNRESOLVED (awaiting classification, pending decisions named), never 'eligible'.

EMPA-PRED (NCT06249945) was screened in as an "eligible double-blind/placebo-controlled RCT" because its text says
'placebo' (the screener accepts placebo-controlled as evidence of blinding when the record is silent). But the record is
NOT silent: its registry masking is SINGLE, and its intervention is "Empagliflozin 25 MG" against a protocol that says
"Empagliflozin 10 mg daily".

  MASKING_CONFLICT  the protocol requires double-blind (include.design_double_blind) and the registry's masking field
                    says NONE or SINGLE. An unstated masking is no statement and raises nothing.
  DOSE_CONFLICT     the topic declares the protocol's dose (protocol_dose, with the verbatim protocol span) and a
                    registry intervention naming THAT drug states a different dose. Another drug's dose is not this.
"""
from __future__ import annotations

import re
from typing import Any

_DOSE = re.compile(r"(\d+(?:\.\d+)?)\s*(mg|milligrams?)\b", re.I)


def check(rec: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    if rec.get("id_type") != "nct":
        return out
    masking = str(rec.get("masking") or "").upper().strip()
    if (config.get("include") or {}).get("design_double_blind") and masking in ("NONE", "SINGLE"):
        out.append({"kind": "MASKING_CONFLICT", "decision": "MASKING_CONFLICT",
                    "record_span": f"masking: {rec.get('masking')}",
                    "protocol_span": "Design - randomized, double-blind, placebo-controlled trial.",
                    "detail": (f"the registry states masking {masking}; the protocol requires double-blind. Held "
                               "UNRESOLVED: a reviewer decides whether the trial is eligible (e.g. blinding described "
                               "elsewhere), never the screener's 'placebo implies blinded' default.")})
    pd = config.get("protocol_dose") or {}
    drug = str(pd.get("intervention") or "").lower()
    want = pd.get("dose_mg")
    if drug and want is not None:
        for iv in rec.get("interventions") or []:
            s = str(iv)
            if drug not in s.lower():
                continue
            for m in _DOSE.finditer(s):
                if abs(float(m.group(1)) - float(want)) > 1e-9:
                    out.append({"kind": "DOSE_CONFLICT", "decision": "DOSE_CONFLICT", "record_span": s,
                                "protocol_span": pd.get("protocol_span"),
                                "detail": (f"the registered intervention states {m.group(0)}; the protocol's "
                                           f"intervention is {want} mg. Held UNRESOLVED for a reviewer's decision.")})
                    break
    return out
