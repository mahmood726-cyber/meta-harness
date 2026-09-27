"""RESULT STATUS: one derived, mutually exclusive state per trial x outcome, so the page's words about a trial's result
cannot contradict what the review object holds (dapagliflozin HFmrEF/HFpEF: the page said DELIVER's primary result was
"reported but not extractable" while DELIVER's own absent row held the extraction HR 0.82 [0.73-0.92] with its span).

States, first match wins (the order IS the exclusivity):
  ADMITTED_PENDING_SIGNATURE  pooled, and its admission is in an OPEN result-change notice (not yet countersigned)
  ADMITTED                    pooled
  EXTRACTED_NOT_ADMITTED      not pooled, but an extraction exists: an effect+CI or arm counts with a verbatim span
                              on the row (observed_effect / held_out_row / a value the reason audit found held)
  WITHDRAWN                   a result served earlier was withdrawn (reason carried) and no extraction replaces it
  SOURCE_HELD_RESULT_NOT_EXTRACTED  a source is held (abstract / full text / registry) but no extraction exists
  SOURCE_ABSENT               no source is held (not retrieved / not discovered)
A withdrawal is also kept as HISTORY on any row (withdrawn: {value, reason}), whatever its current state.
"""
from __future__ import annotations

import re
from typing import Any

ADMITTED_PENDING_SIGNATURE = "ADMITTED_PENDING_SIGNATURE"
ADMITTED = "ADMITTED"
EXTRACTED_NOT_ADMITTED = "EXTRACTED_NOT_ADMITTED"
WITHDRAWN = "WITHDRAWN"
SOURCE_HELD_RESULT_NOT_EXTRACTED = "SOURCE_HELD_RESULT_NOT_EXTRACTED"
SOURCE_ABSENT = "SOURCE_ABSENT"
STATES = (ADMITTED_PENDING_SIGNATURE, ADMITTED, EXTRACTED_NOT_ADMITTED, WITHDRAWN,
          SOURCE_HELD_RESULT_NOT_EXTRACTED, SOURCE_ABSENT)
_NOT_HELD = {"SOURCE_NOT_RETRIEVED", "DISCOVERED_NOT_RETRIEVED", "NOT_DISCOVERED", "NOT_HELD"}
_NOT_EXTRACTABLE = re.compile(r"not extractable|could not be extracted|no extractable", re.I)


def _pid(x) -> str:
    m = re.search(r"(\d{7,8}|NCT\d{8})", str(x or ""))
    return m.group(1) if m else str(x or "")


def extraction_of(row: dict[str, Any]) -> dict[str, Any] | None:
    """The extraction a NOT-pooled row already holds, with its span, or None."""
    obs = row.get("observed_effect")
    if isinstance(obs, dict) and obs.get("effect") is not None and obs.get("span"):
        return {"kind": "effect", **{k: obs.get(k) for k in ("effect", "ci_low", "ci_high", "scale")}, "span": obs["span"]}
    held = row.get("held_out_row")
    if isinstance(held, dict) and (held.get("effect") is not None or held.get("ai") is not None):
        return {"kind": "held_out_row", **held, "span": row.get("source_span") or row.get("reason")}
    audit = row.get("reason_code_audit") or {}
    if audit.get("verdict") == "REASON_FALSE_VALUE_HELD" and audit.get("value_text"):
        return {"kind": "value_held", "value_text": audit["value_text"], "span": audit.get("source_span")}
    return None


def status_of(row: dict[str, Any], pooled: bool, pending_ids: set[str]) -> dict[str, Any]:
    wd = None
    if row.get("absent_kind") == "result_withdrawn" or row.get("withdrawn_effect"):
        wd = {"value": row.get("withdrawn_effect"), "reason": row.get("reason")}
    if pooled:
        st = ADMITTED_PENDING_SIGNATURE if _pid(row.get("id")) in pending_ids else ADMITTED
        return {"state": st, **({"withdrawn": wd} if wd else {})}
    ex = extraction_of(row)
    if ex:
        code = row.get("reason_code") or row.get("state") or row.get("absent_kind")
        why = code
        if code == "EXTRACTION_NOT_PERFORMED" or (row.get("reason_code_audit") or {}).get("verdict") == "REASON_FALSE_VALUE_HELD":
            # the stored code says no extraction was done; the row holds one -- say what actually happened
            why = ("an extraction is held but was not admitted"
                   + (" after the earlier served value was withdrawn" if wd else "")
                   + f" (stored code {code} is superseded by this state)")
        return {"state": EXTRACTED_NOT_ADMITTED, "extraction": ex, "not_admitted_because": why,
                **({"withdrawn": wd} if wd else {})}
    if wd:
        return {"state": WITHDRAWN, "withdrawn": wd}
    code = str(row.get("reason_code") or row.get("state") or "")
    if code in _NOT_HELD or row.get("absent_kind") == "not_retrieved":
        return {"state": SOURCE_ABSENT, "basis": code}
    return {"state": SOURCE_HELD_RESULT_NOT_EXTRACTED, "basis": code or row.get("absent_kind")}


def _pending_ids(review: dict[str, Any], outcome: str) -> set[str]:
    """Rows whose entry into this outcome's pool is in a result-change notice not yet countersigned. The notices sit
    OUTSIDE the review core (reproduction.result_changes), so in the core build this is empty and the page overlays it
    via effective_state; a countersignature therefore never moves the core hash."""
    out = set()
    for n in ((review.get("reproduction") or {}).get("result_changes") or []):
        if n.get("outcome") == outcome and (n.get("reviewer_countersignature") or {}).get("state") == "OPEN":
            out |= {_pid(x) for x in n.get("entered_pool") or []}
    return out


def effective_state(row: dict[str, Any], review: dict[str, Any], outcome: str) -> str | None:
    """The state a page shows: the derived state, with ADMITTED raised to ADMITTED_PENDING_SIGNATURE while the row's
    entry is in an OPEN notice."""
    st = (row.get("result_status") or {}).get("state")
    if st == ADMITTED and _pid(row.get("id")) in _pending_ids(review, outcome):
        return ADMITTED_PENDING_SIGNATURE
    return st


def derive(review: dict[str, Any]) -> None:
    """Stamp `result_status` on every trial row and rebuild each outcome's not-extracted sentence FROM the states."""
    for o in review.get("outcomes") or []:
        pend = _pending_ids(review, o.get("name"))
        for t in o.get("trials") or []:
            t["result_status"] = status_of(t, True, pend)
        for a in o.get("declared_absent_trials") or []:
            a["result_status"] = status_of(a, False, pend)
        res = o.get("result")
        if isinstance(res, dict) and res.get("reported_not_extracted"):
            by = {_pid(a.get("id")): a["result_status"] for a in o.get("declared_absent_trials") or []}
            rep = [str(x) for x in res.get("reported_by") or []]
            extracted = [x for x in rep if (by.get(_pid(x)) or {}).get("state") == EXTRACTED_NOT_ADMITTED]
            not_extracted = [x for x in rep if x not in extracted]
            parts = []
            if extracted:
                parts.append("EXTRACTED BUT NOT ADMITTED: " + "; ".join(
                    f"{x} ({_value_phrase(by[_pid(x)]['extraction'])}; not admitted: "
                    f"{by[_pid(x)].get('not_admitted_because')})" for x in extracted[:6]))
            if not_extracted:
                parts.append("REPORTED but not extracted as a pooled value: " + ", ".join(not_extracted[:6])
                             + " mention this outcome in the committed abstract without arm counts or an effect+CI "
                               "in an extractable form; full-text acquisition would recover the countable form")
            res["reason"] = ". ".join(parts) + ". This outcome is NOT absent."
            res["status_counts"] = {"EXTRACTED_NOT_ADMITTED": extracted, "SOURCE_HELD_RESULT_NOT_EXTRACTED": not_extracted}


def _value_phrase(ex: dict[str, Any]) -> str:
    if ex.get("kind") == "effect":
        return f"{ex.get('scale') or 'ratio'} {ex.get('effect')} [{ex.get('ci_low')}, {ex.get('ci_high')}] held"
    if ex.get("ai") is not None:
        return f"{ex.get('ai')}/{ex.get('n1i')} vs {ex.get('ci')}/{ex.get('n2i')} held"
    return f"'{ex.get('value_text')}' held in the source"


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Blocking: a sentence that calls a trial's result not extractable while that trial's state says an extraction
    exists (STATUS_VS_EXTRACTION); a row with no derived state or an unknown one (STATUS_MISSING)."""
    out = []
    for o in review.get("outcomes") or []:
        states = {}
        for t in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
            st = (t.get("result_status") or {}).get("state")
            if st not in STATES:
                out.append({"kind": "STATUS_MISSING", "report_id": _pid(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} has no derived result status"})
            states[_pid(t.get("id"))] = st
        texts = [str((o.get("result") or {}).get("reason") or "")]
        texts += [str(a.get("reason") or "") for a in o.get("declared_absent_trials") or []]
        for text in texts:
            for sent in re.split(r"(?<=[.;])\s+", text):
                if not _NOT_EXTRACTABLE.search(sent):
                    continue
                for pid in set(re.findall(r"\d{7,8}|NCT\d{8}", sent)):
                    if states.get(pid) in (EXTRACTED_NOT_ADMITTED, ADMITTED, ADMITTED_PENDING_SIGNATURE):
                        out.append({"kind": "STATUS_VS_EXTRACTION", "report_id": pid,
                                    "detail": f"{o.get('name')}: '{sent.strip()[:140]}' names {pid}, whose state is "
                                              f"{states[pid]}"})
    return out
