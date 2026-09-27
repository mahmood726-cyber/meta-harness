"""TRIAL LIFECYCLE: typed, from the held registry row, dated by the source's own snapshot.

EMPA-PRED (NCT06249945) was served as "eligible, completed, awaiting results". Its held AACT row (snapshot 2026-08-30)
says RECRUITING with completion 2030-12-31 -- a planned date four years after the source was taken. The old rule fell
through to 'completed' whenever the status was missing or UNKNOWN.

Fields (each carries its value and where it came from):
  recruitment_status            the registry's overall_status, verbatim (or None)
  completion_date               the registry's completion date, verbatim (or None)
  planned_vs_actual_completion  PLANNED when the completion date is AFTER the source date (the registry cannot have
                                observed it), ACTUAL when on/before it, UNKNOWN when there is no date
  source_date                   the snapshot date of the source the row was read from
  state                         ONGOING / NOT_YET_RECRUITING / COMPLETED / TERMINATED / WITHDRAWN / SUSPENDED /
                                CONFLICT / UNKNOWN
Rules: a PLANNED completion never yields COMPLETED (a 'COMPLETED' status with a future date is CONFLICT); a missing or
UNKNOWN status is UNKNOWN, never 'completed'.
"""
from __future__ import annotations

from typing import Any

_ONGOING = {"RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION"}
_ENDED = {"COMPLETED": "COMPLETED", "TERMINATED": "TERMINATED", "WITHDRAWN": "WITHDRAWN", "SUSPENDED": "SUSPENDED"}


def _field(value, source):
    return {"value": value or None, "source": source}


def lifecycle(row: dict[str, Any] | None, source_date: str | None,
              source: str = "AACT studies row (held, digest-matched in cache/<slug>/aact_inputs.json)") -> dict[str, Any]:
    row = row or {}
    status = str(row.get("overall_status") or "").upper().strip()
    comp = str(row.get("completion_date") or "").strip()[:10]
    dtype = str(row.get("completion_date_type") or "").upper()
    if not comp:
        pva = "UNKNOWN"
    elif dtype in ("ESTIMATED", "ANTICIPATED"):
        pva = "PLANNED"            # the registry itself says the date is a plan, whatever the calendar says
    elif dtype == "ACTUAL":
        pva = "ACTUAL"
    elif source_date and comp > str(source_date)[:10]:
        pva = "PLANNED"
    elif source_date:
        pva = "ACTUAL"
    else:
        pva = "UNKNOWN"            # a date with no source date cannot be placed in time
    if status == "NOT_YET_RECRUITING":
        state = "NOT_YET_RECRUITING"
    elif status in _ONGOING:
        state = "ONGOING"
    elif status in _ENDED:
        state = _ENDED[status]
        if state == "COMPLETED" and pva == "PLANNED":
            state = "CONFLICT"     # the registry says completed, but its own completion date has not happened
    else:
        state = "UNKNOWN"          # '' / UNKNOWN / anything unrecognised: never 'completed'
    return {"state": state,
            "recruitment_status": _field(status or None, source),
            "completion_date": _field(comp or None, source),
            "planned_vs_actual_completion": {"value": pva, "basis": (
                f"completion date {comp} is after the source date {source_date}" if pva == "PLANNED" else
                f"completion date {comp} is on or before the source date {source_date}" if pva == "ACTUAL" else
                "no completion date, or no source date to place it")},
            "source_date": source_date}


_COMPLETENESS = {"ONGOING": "eligible+ongoing", "NOT_YET_RECRUITING": "eligible+not_yet_recruiting",
                 "UNKNOWN": "eligible+lifecycle_unknown", "CONFLICT": "eligible+lifecycle_conflict",
                 "SUSPENDED": "eligible+ongoing"}


def completeness_state(lc: dict[str, Any], has_results: bool) -> str:
    """The screening row's completeness label, derived from the lifecycle (never defaulting to 'completed')."""
    if lc["state"] in _COMPLETENESS:
        return _COMPLETENESS[lc["state"]]
    return "eligible+completed+results_available" if has_results else "eligible+completed+results_unavailable"
