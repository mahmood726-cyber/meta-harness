"""MEASURE GUARD: a restricted-mean-survival-time (RMST) DIFFERENCE is never a hazard ratio, risk ratio or odds ratio.

Statins in older adults (2026-09-28): Orkaby 2018 re-analysed ALLHAT-LLT as RMST differences in DAYS (-33.7 days,
95% CI -67.0 to -0.5). A difference in event-free time and a ratio of hazards are different measures on different
scales; a number from one entering a pool of the other is a unit error the pool cannot see.

  measure_of(row) -> 'RMST_DIFFERENCE' when the row's own span / source names RMST, else None
  problems(review) -> blocking MEASURE_CLASS_MISMATCH for a pooled row whose span is an RMST difference while its
                      scale is a ratio (HR / RR / OR / IRR)
"""
from __future__ import annotations

import re
from typing import Any

_RMST = re.compile(r"restricted mean survival time|\bRMST\b|restricted mean (?:event-free )?time", re.I)
_RATIO = {"HR", "RR", "OR", "IRR", "RATE RATIO", "HAZARD RATIO", "RISK RATIO", "ODDS RATIO"}


def measure_of(row: dict[str, Any]) -> str | None:
    text = " ".join(str(row.get(k) or "") for k in ("source_span", "source", "span", "verbatim_span"))
    return "RMST_DIFFERENCE" if _RMST.search(text) else None


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for o in review.get("outcomes") or []:
        scale_default = str((o.get("result") or {}).get("scale") or o.get("estimand") or "").upper()
        for t in o.get("trials") or []:
            if measure_of(t) == "RMST_DIFFERENCE" and (str(t.get("scale") or scale_default).upper() in _RATIO):
                out.append({"kind": "MEASURE_CLASS_MISMATCH", "report_id": str(t.get("id")),
                            "detail": (f"{o.get('name')}: {t.get('id')} carries an RMST difference (a difference in "
                                       f"event-free time) on a ratio scale ({t.get('scale') or scale_default})")})
    return out
