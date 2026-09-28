"""RESULT STATUS: one derived, mutually exclusive state per trial x outcome, so the page's words about a trial's result
cannot contradict what the review object holds (dapagliflozin HFmrEF/HFpEF: the page said DELIVER's primary result was
"reported but not extractable" while DELIVER's own absent row held the extraction HR 0.82 [0.73-0.92] with its span).

States, first match wins (the order IS the exclusivity):
  ADMITTED_PENDING_SIGNATURE  pooled, and its admission is in an OPEN result-change notice (not yet countersigned)
  ADMITTED                    pooled
  REPORTED_ZERO_EVENTS        reported with ZERO events in every arm (a witnessed statement or a 0-vs-0 extraction):
                              reported, never "not reported"; not estimable on a ratio scale
  EXTRACTED_NOT_ADMITTED      not pooled, but an extraction exists: an effect+CI or arm counts with a verbatim span
                              on the row (observed_effect / held_out_row / a value the reason audit found held)
  WITHDRAWN                   a result served earlier was withdrawn (reason carried) and no extraction replaces it
  REPORTED_UNRESOLVED         the held source REPORTS the outcome but no admissible value is resolved from it
                              (timepoint / estimand / multi-arm / population mismatch, an internally inconsistent
                              source, a whole-trial row across comparisons, a result located in an unheld supplement,
                              an outcome discussed without an aggregate)
  NOT_MEASURED                the trial did not measure it -- ONLY from a witnessed declaration (`not_measured_span`),
                              never inferred, and never while any held source reports the outcome
  RETRIEVED_NOT_REPORTED      a source is held and the outcome was not found in it -- a SCOPED statement ("not found in
                              the inspected abstract"), never promoted to "absent by design"
  NOT_YET_RETRIEVED           no source is held (not retrieved / not discovered)
A withdrawal is also kept as HISTORY on any row (withdrawn: {value, reason}), whatever its current state.
(Vocabulary refined 2026-09-27 from the denosumab review: SOURCE_ABSENT is now NOT_YET_RETRIEVED, and the former
SOURCE_HELD_RESULT_NOT_EXTRACTED is split into REPORTED_UNRESOLVED / REPORTED_ZERO_EVENTS / RETRIEVED_NOT_REPORTED.)
"""
from __future__ import annotations

import re
from typing import Any

ADMITTED_PENDING_SIGNATURE = "ADMITTED_PENDING_SIGNATURE"
ADMITTED = "ADMITTED"
EXTRACTED_NOT_ADMITTED = "EXTRACTED_NOT_ADMITTED"
WITHDRAWN = "WITHDRAWN"
REPORTED_ZERO_EVENTS = "REPORTED_ZERO_EVENTS"
REPORTED_UNRESOLVED = "REPORTED_UNRESOLVED"
NOT_MEASURED = "NOT_MEASURED"
# the trial's own collection rules did not ascertain this outcome (SELECT: selective safety collection -- serious AEs,
# AEs leading to discontinuation, AEs of special interest). Not 'not reported', not 'not retrieved', never zero.
NOT_SYSTEMATICALLY_COLLECTED = "NOT_SYSTEMATICALLY_COLLECTED"
RETRIEVED_NOT_REPORTED = "RETRIEVED_NOT_REPORTED"
NOT_YET_RETRIEVED = "NOT_YET_RETRIEVED"
SOURCE_ABSENT = NOT_YET_RETRIEVED          # the earlier name of the same state (one state, one string)
STATES = (ADMITTED_PENDING_SIGNATURE, ADMITTED, REPORTED_ZERO_EVENTS, EXTRACTED_NOT_ADMITTED, WITHDRAWN,
          REPORTED_UNRESOLVED, NOT_MEASURED, RETRIEVED_NOT_REPORTED, NOT_YET_RETRIEVED, NOT_SYSTEMATICALLY_COLLECTED)
_NOT_HELD = {"SOURCE_NOT_RETRIEVED", "DISCOVERED_NOT_RETRIEVED", "NOT_DISCOVERED", "NOT_HELD"}
# codes that say the outcome IS reported but no admissible value was resolved from it
_REPORTED_CODES = {"TIMEPOINT_MISMATCH", "MULTI_ARM_UNRESOLVED", "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH",
                   "POPULATION_MISMATCH", "SOURCE_INTERNALLY_INCONSISTENT", "WHOLE_TRIAL_ACROSS_COMPARISONS",
                   "ENDPOINT_UNBOUND", "RESULT_INCOMPATIBLE", "KNOWN_REPORTED_NOT_YET_EXTRACTED"}
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


def _scope(row: dict[str, Any]) -> str:
    """What was inspected, for a scoped 'not found' statement."""
    rep = str(((row.get("held_document") or {}).get("representation")) or "")
    text = f"{row.get('reason') or ''} {row.get('state_basis') or ''}".lower()
    if rep in ("xml", "text") or "full text" in text or "full-text" in text:
        return "the inspected full text"
    if "abstract" in text or rep == "abstract" or not rep:
        return "the inspected abstract"
    return "the held sources"


def status_of(row: dict[str, Any], pooled: bool, pending_ids: set[str], mentioned: bool = False,
              verbatim_mentions: bool = False) -> dict[str, Any]:
    """`mentioned`: the outcome is named in this trial's held source (the outcome's reported_by).
    `verbatim_mentions`: the held VERBATIM original names it (matters when the inspected record is abridged)."""
    wd = None
    if row.get("absent_kind") == "result_withdrawn" or row.get("withdrawn_effect"):
        wd = {"value": row.get("withdrawn_effect"), "reason": row.get("reason")}
    if pooled:
        st = ADMITTED_PENDING_SIGNATURE if _pid(row.get("id")) in pending_ids else ADMITTED
        return {"state": st, **({"withdrawn": wd} if wd else {})}
    cs = row.get("collection_scope") or {}
    if cs.get("state") == NOT_SYSTEMATICALLY_COLLECTED:
        return {"state": NOT_SYSTEMATICALLY_COLLECTED, "span": cs.get("rule_span"), "collected": cs.get("collected"),
                "statement": ("not systematically collected: the trial's own safety-collection rules did not ascertain "
                              "this outcome, so no count from it is a count of this outcome (not 'not reported', not zero)")}
    ex = extraction_of(row)
    zero_span = row.get("zero_events_span")
    # a 0-vs-0 extraction is a zero for THIS outcome only when it is this outcome's: a row held out because it measures a
    # NARROWER outcome (J-EMPHASIS-HF 'gynaecomastia 0 vs 0' for 'gynaecomastia OR breast pain') is not a zero event
    # count of the composite -- it stays EXTRACTED_NOT_ADMITTED with its reason
    if zero_span or (ex and ex.get("ai") == 0 and ex.get("ci") == 0 and not row.get("not_admitted_because")):
        return {"state": REPORTED_ZERO_EVENTS, "span": zero_span or ex.get("span"),
                "note": (f"zero events in {row['zero_events_scope']}: reported; not estimable on a ratio scale"
                         if row.get("zero_events_scope") else
                         "zero events in every arm: reported; not estimable on a ratio scale")}
    if ex:
        code = row.get("reason_code") or row.get("state") or row.get("absent_kind")
        why = row.get("not_admitted_because") or code
        if code == "EXTRACTION_NOT_PERFORMED" or (row.get("reason_code_audit") or {}).get("verdict") == "REASON_FALSE_VALUE_HELD":
            # the stored code says no extraction was done; the row holds one -- say what actually happened
            why = ("an extraction is held but was not admitted"
                   + (" after the earlier served value was withdrawn" if wd else "")
                   + f" (stored code {code} is superseded by this state)")
        return {"state": EXTRACTED_NOT_ADMITTED, "extraction": ex, "not_admitted_because": why,
                **({"withdrawn": wd} if wd else {})}
    if wd:
        return {"state": WITHDRAWN, "withdrawn": wd}
    code = str(row.get("reason_code") or row.get("state") or row.get("provenance") or "")
    if code in _NOT_HELD or row.get("absent_kind") == "not_retrieved":
        return {"state": NOT_YET_RETRIEVED, "basis": code}
    if code == "SIGNAL_SPURIOUS":
        # the outcome's keywords matched text about ANOTHER outcome (Moll: 'discontinued treatment because of side
        # effects' is not gastrointestinal incidence): the source does not report THIS outcome -- never 'reported'
        return {"state": RETRIEVED_NOT_REPORTED, "scope": _scope(row), "basis": code,
                "statement": (f"not reported in {_scope(row)}: its mention matched this outcome's keywords but is about a "
                              "different outcome (a scoped statement, not a claim about the trial's design)")}
    acq = row.get("acquisition_state") or {}
    if (code in _REPORTED_CODES or mentioned or row.get("reported_unresolved_span")
            or "PROTOCOL_PREFERRED_ANALYSIS_IN_SUPPLEMENT" in (acq.get("states") or [])):
        return {"state": REPORTED_UNRESOLVED, "basis": code or row.get("absent_kind"),
                **({"span": row["reported_unresolved_span"]} if row.get("reported_unresolved_span") else {})}
    if "MAIN_RESULT_NOT_HELD" in (acq.get("states") or []):
        # the report that holds this result is not held (GLAGOV: its Table 4 is in the full report; the abstract is
        # silent): the inspected abstract's silence is never 'not reported'
        return {"state": NOT_YET_RETRIEVED, "basis": code or row.get("absent_kind"),
                "statement": "the report that holds this result is not held; " + str(acq.get("basis") or "")}
    cov = (row.get("source_coverage") or {}).get("coverage")
    if cov in ("EXCERPT", "ALTERED"):
        # the inspected text is an abridged excerpt of the publication: it can support no absence claim at all
        if verbatim_mentions:
            return {"state": REPORTED_UNRESOLVED, "basis": code or row.get("absent_kind"), "coverage": cov,
                    "statement": (f"the inspected record is {cov} (not the verbatim abstract); the verbatim original "
                                  "held by the cascade reports this outcome")}
        return {"state": NOT_YET_RETRIEVED, "basis": code or row.get("absent_kind"), "coverage": cov,
                "statement": f"only an abridged ({cov}) record was inspected; the publication itself was not"}
    if row.get("not_measured_span"):
        return {"state": NOT_MEASURED, "span": row["not_measured_span"]}
    cov_note = {"VERBATIM": "verbatim", "UNVERIFIED": "coverage UNVERIFIED: no verbatim original held"}.get(cov or "")
    return {"state": RETRIEVED_NOT_REPORTED, "scope": _scope(row), "basis": code or row.get("absent_kind"),
            **({"coverage": cov} if cov else {}),
            "statement": (f"not found in {_scope(row)}" + (f" ({cov_note})" if cov_note else "")
                          + " (a scoped statement, not a claim about the trial's design)")}


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


def derive(review: dict[str, Any], keywords: dict[str, list[str]] | None = None) -> None:
    """Stamp `result_status` on every trial row and rebuild each outcome's not-extracted sentence FROM the states.
    `keywords`: outcome name -> its keywords, to ask whether a held verbatim original names the outcome."""
    from . import source_coverage
    for o in review.get("outcomes") or []:
        pend = _pending_ids(review, o.get("name"))
        mentioned = {_pid(x) for x in ((o.get("result") or {}).get("reported_by") or [])}
        # a pooled outcome keeps the same evidence for its NOT-pooled trials (pipeline: mentioned_by_not_pooled)
        mentioned |= {_pid(x) for x in (o.get("mentioned_by_not_pooled") or [])}
        kws = (keywords or {}).get(o.get("name")) or [o.get("name") or ""]
        for t in o.get("trials") or []:
            t["result_status"] = status_of(t, True, pend)
        for a in o.get("declared_absent_trials") or []:
            abridged = (a.get("source_coverage") or {}).get("coverage") in ("EXCERPT", "ALTERED")
            a["result_status"] = status_of(a, False, pend, mentioned=_pid(a.get("id")) in mentioned,
                                           verbatim_mentions=abridged and source_coverage.mentions(_pid(a.get("id")), kws))
            # a HELD, examined registry result declared for this outcome (docs/multi_trial_reports.json per_outcome)
            # upgrades 'not yet retrieved': the source IS retrieved, and says what it says. Only that upgrade: a
            # declaration never overrides a state a held extraction or a pool decided.
            decl = (((a.get("multi_trial_report") or {}).get("registry_results") or {}).get("per_outcome") or {}).get(o.get("name"))
            if decl and a["result_status"].get("state") == NOT_YET_RETRIEVED and decl.get("state") in (
                    RETRIEVED_NOT_REPORTED, REPORTED_UNRESOLVED, NOT_MEASURED):
                a["result_status"] = {"state": decl["state"], "coverage": decl.get("coverage"), "basis": decl.get("basis"),
                                      "source": {k: a["multi_trial_report"]["registry_results"].get(k) for k in ("path", "sha256")},
                                      "supersedes": a["result_status"],
                                      "statement": (f"{a.get('id')}: {o.get('name')} -- {decl['state']}: {decl.get('basis')} "
                                                    f"(coverage: {decl.get('coverage')})")}
        res = o.get("result")
        # rebuild ONLY the generic sentence the false-absence guard wrote; a reason another mechanism set (e.g. a
        # HARMS_INCOMPLETE reason naming the unresolved report) is never replaced
        if (isinstance(res, dict) and res.get("reported_not_extracted")
                and str(res.get("reason") or "").startswith("REPORTED but not extractable")):
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
            res["status_counts"] = {EXTRACTED_NOT_ADMITTED: extracted, REPORTED_UNRESOLVED: not_extracted}


def _value_phrase(ex: dict[str, Any]) -> str:
    if ex.get("kind") == "effect":
        return f"{ex.get('scale') or 'ratio'} {ex.get('effect')} [{ex.get('ci_low')}, {ex.get('ci_high')}] held"
    if ex.get("ai") is not None:
        return f"{ex.get('ai')}/{ex.get('n1i')} vs {ex.get('ci')}/{ex.get('n2i')} held"
    return f"'{ex.get('value_text')}' held in the source"


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Blocking: a sentence that calls a trial's result not extractable while that trial's state says an extraction
    exists (STATUS_VS_EXTRACTION); a row with no derived state or an unknown one (STATUS_MISSING); a design-absence
    claim (NOT_MEASURED / absent by design) on a row whose held source holds or reports the result
    (DESIGN_ABSENCE_VS_HELD_RESULT) -- a held result always invalidates it."""
    out = []
    for o in review.get("outcomes") or []:
        states = {}
        mentioned = {_pid(x) for x in ((o.get("result") or {}).get("reported_by") or [])}
        for t in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
            st = (t.get("result_status") or {}).get("state")
            if st not in STATES:
                out.append({"kind": "STATUS_MISSING", "report_id": _pid(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} has no derived result status"})
            states[_pid(t.get("id"))] = st
            claims_design = bool(t.get("not_measured_span")) or t.get("absence_status") == "ABSENT_BY_DESIGN"
            held_result = (t in (o.get("trials") or []) or extraction_of(t) or t.get("zero_events_span")
                           or _pid(t.get("id")) in mentioned or t.get("reported_unresolved_span"))
            if claims_design and held_result:
                out.append({"kind": "DESIGN_ABSENCE_VS_HELD_RESULT", "report_id": _pid(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} is claimed not measured / absent by design while "
                                      "a held source holds or reports its result"})
            cov = (t.get("source_coverage") or {}).get("coverage")
            if st in (RETRIEVED_NOT_REPORTED, NOT_MEASURED) and cov in ("EXCERPT", "ALTERED"):
                out.append({"kind": "ABSENCE_ON_EXCERPT", "report_id": _pid(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} is stated {st} on an inspected record that is "
                                      f"{cov}, not the publication"})
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
