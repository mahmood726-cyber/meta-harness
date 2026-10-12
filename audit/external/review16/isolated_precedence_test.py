"""Isolated control-flow test, NOT a full harness execution.

`audit_pair` is manually transcribed from harness/unextracted.py at
0730234d0b4f (reported Git blob dfb93cbebead3ecb2783cfaae26ebf9d17fcf3ea).
Helper outputs are deliberately stubbed. This tests the ordering of a supplied
numeric-candidate result versus an explicit TIMEPOINT_MISMATCH; it does not test
whether the production candidate detector finds a particular publication span.
"""
from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

EXTRACTED = "EXTRACTED"
HELD_NOT_EXTRACTED = "HELD_NOT_EXTRACTED"
NOT_IN_HELD_SOURCES = "NOT_IN_HELD_SOURCES"
ABSENT_BY_DESIGN = "ABSENT_BY_DESIGN"

# Minimal stubs: no included rows, and only the mismatch type under test.
def _trial_keys(rows):
    return {r["id"] for r in rows}

def _is_design_absent(row):
    return bool(row and row.get("reason_code") == "TIMEPOINT_MISMATCH")

reason_audit = SimpleNamespace(find_value_in_sources=lambda *_: None)

# Transcribed control-flow excerpt; helper implementations above are NOT original.
def audit_pair(
    outcome: dict[str, Any],
    trial_key: str,
    sources: list[dict[str, str]],
    spec: dict[str, Any] | None = None,
    row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec = spec or {}
    pooled = _trial_keys(outcome.get("trials") or [])
    if trial_key in pooled:
        return {"status": EXTRACTED}
    found = reason_audit.find_value_in_sources(sources, spec.get("keywords") or [], outcome.get("name"))
    if found:
        return {
            "status": HELD_NOT_EXTRACTED,
            "source_id": found["source_id"],
            "source_kind": found["source_kind"],
            "source_span": found["span"],
            **({"value_text": found["value_text"]} if found.get("value_text") else {}),
        }
    if _is_design_absent(row):
        return {"status": ABSENT_BY_DESIGN, "reason_code": row.get("reason_code") or row.get("state")}
    return {"status": NOT_IN_HELD_SOURCES}

outcome = {"name": "Percent change in body weight", "trials": []}
spec = {"keywords": ["body weight", "primary outcome"], "timepoint_weeks": 68,
        "timepoint_tolerance_weeks": 8}
row = {"reason_code": "TIMEPOINT_MISMATCH", "reason": "44 weeks, not the 68-week target"}
fixture = {"source_id": "synthetic:wrong_time", "source_kind": "fixture",
           "span": "Synthetic fixture: a numerical body-weight result at week 44."}
results = []
for found in [fixture, None]:
    reason_audit.find_value_in_sources = lambda *_, value=found: value
    result = audit_pair(outcome, "synthetic_trial", [], spec, row)
    results.append({"helper_returns_numeric_candidate": found is not None,
                    "explicit_row_reason": row["reason_code"], "output": result})
assert results[0]["output"]["status"] == HELD_NOT_EXTRACTED
assert results[1]["output"]["status"] == ABSENT_BY_DESIGN
report = {"test_type": "manual excerpt with stub helpers, not end-to-end",
          "source_ref": "0730234d0b4f:harness/unextracted.py:audit_pair",
          "results": results,
          "scope": "Demonstrates branch precedence only. No claim to have executed the production detector, screen, or publication gate."}
Path(__file__).with_name("precedence_results.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
