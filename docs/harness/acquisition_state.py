"""ACQUISITION STATES: what the acquisition cascade established about a trial's result for one outcome, when that is
more than 'not in the abstract' -- e.g. METCOVID: the report's main table is mITT, the protocol wants ITT-as-randomised,
and the report says the ITT analysis is in Supplementary Table 2. Declared in docs/acquisition_states.json, attached
to the trial's declared-absent row for that outcome, and rendered beside its reason. It never admits a number: a
state is a statement about where the result is and whether we hold it.

States (combinable):
  MAIN_RESULT_RECOVERED / MAIN_RESULT_NOT_HELD
  PROTOCOL_PREFERRED_ANALYSIS_IN_SUPPLEMENT / SUPPLEMENT_NOT_HELD / SUPPLEMENT_HELD
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

PATH = os.path.join("docs", "acquisition_states.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pid(x) -> str:
    m = re.search(r"(\d{7,8})", str(x or ""))
    return m.group(1) if m else ""


def load(slug: str | None, root: str = _ROOT) -> dict[str, list[dict[str, Any]]]:
    p = os.path.join(root, PATH)
    if not slug or not os.path.exists(p):
        return {}
    return ((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or {}


def annotate(slug: str | None, outcome_name: str, absent: list[dict[str, Any]], root: str = _ROOT) -> None:
    states = load(slug, root)
    for row in absent:
        for st in states.get(_pid(row.get("id"))) or []:
            if st.get("outcome") == outcome_name:
                row["acquisition_state"] = {k: st.get(k) for k in ("states", "basis", "analysis_sets", "attempts")}
