"""The REINSTATEMENT notice kind (V8-06, 7 Oct): a result-change notice that re-enters a trial an earlier signed notice
set aside. A CI check only (tests/test_result_change_notice.py) -- nothing that builds, renders or gates a page imports
it, so it sits outside every page certificate's pinned code closure (harness/certificate.py) and a fix to it never
forces a rebuild of the served pages."""
from __future__ import annotations

import json
import re
import os
from typing import Any

from .result_changes import ROOT, not_applied


def _instant(t: Any):
    """A notice's when_utc as an aware datetime (UTC 'Z' or an offset, fractional seconds allowed), or None."""
    import datetime as _dt
    try:
        d = _dt.datetime.fromisoformat(str(t).strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else None


REINSTATEMENTS = os.path.join("registry", "result_change_reinstatements.json")


def _key(n: dict[str, Any]) -> tuple:
    """A notice's identity by CONTENT (slug, outcome, instant, pools), never by object identity (codex v8-apply-r7 #2)."""
    return (n.get("slug"), n.get("outcome"), _instant(n.get("when_utc")),
            tuple(sorted(map(str, n.get("left_pool") or []))), tuple(sorted(map(str, n.get("entered_pool") or []))))


def _declared(n: dict[str, Any], root: str | None = None) -> dict[str, str]:
    """{trial: reversed set-aside's when_utc} DECLARED for this notice in registry/result_change_reinstatements.json."""
    p = os.path.join(root or ROOT, REINSTATEMENTS)
    if not os.path.lexists(p):
        return {}
    if not os.path.isfile(p):     # a dangling link / directory is a broken register, never 'none declared' (codex r9 #3)
        raise ValueError(f"REINSTATEMENTS: {p} exists but is not a readable file")
    rows = (json.load(open(p, encoding="utf-8")).get("reinstatements") or [])
    t = _instant(n.get("when_utc"))
    return {str(r["trial"]): str(r["reverses_when_utc"]) for r in rows
            if r.get("slug") == n.get("slug") and r.get("outcome") == n.get("outcome") and t is not None
            and _instant(r.get("notice_when_utc")) == t and r.get("trial") and r.get("reverses_when_utc")}


def reversed_setasides(n: dict[str, Any], notices: list[dict[str, Any]], root: str | None = None,
                       declared: dict[str, str] | None = None) -> dict[str, dict[str, Any]] | None:
    """A REINSTATEMENT (V8-06, 7 Oct): a notice that only ENTERS trials, each one DECLARED (registry/
    result_change_reinstatements.json: slug, outcome, the notice's instant, the trial, and the instant of the set-aside it
    reverses) and each declaration true of the record:
      - the reversed notice exists at exactly that instant for the same outcome, is signed and applied, moved exactly ONE
        trial out (this one) and none in, and made the set-aside claim ('eligible evidence awaiting adjudication'; 'the
        numbers are not asserted wrong'; nothing asserted wrong);
      - it is the LATEST signed movement of the trial before this notice, and no other signed movement of the trial is at
        or after this notice's instant (the order would be unknown).
    {trial: reversed notice} when every entering trial qualifies, else None. Nothing is read from this notice's own reason:
    seven review rounds showed a reason's wording cannot be attributed to a trial by text (codex v8-apply r1-r7)."""
    ent = [str(t) for t in n.get("entered_pool") or []]
    t_n = _instant(n.get("when_utc"))
    if not ent or n.get("left_pool") or t_n is None:
        return None
    decl = _declared(n, root) if declared is None else declared
    me = _key(n)
    signed = ("SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED")
    out = {}
    for tid in ent:
        rev_t = _instant(decl.get(tid))
        if rev_t is None:
            return None
        cands = [p for p in notices if _key(p) != me and p.get("slug") == n.get("slug") and p.get("outcome") == n.get("outcome")
                 and tid in [str(x) for x in (p.get("left_pool") or []) + (p.get("entered_pool") or [])]
                 and not not_applied(p) and (p.get("reviewer_countersignature") or {}).get("state") in signed]
        if any(_instant(p.get("when_utc")) is None or _instant(p.get("when_utc")) >= t_n for p in cands):
            return None
        at = [p for p in cands if _instant(p.get("when_utc")) == rev_t]
        later = [p for p in cands if _instant(p.get("when_utc")) > rev_t]
        if len(at) != 1 or later:
            return None
        p = at[0]
        r = str(p.get("reason") or "")
        # the set-aside claim, with 'eligible' a WHOLE word ('ineligible evidence awaiting adjudication' is not it; codex
        # v8-apply-r8 #2) and nothing asserted wrong or ineligible
        if [str(x) for x in p.get("left_pool") or []] != [tid] or (p.get("entered_pool") or []):
            return None
        if not re.search(r"(?<![A-Za-z])eligible evidence awaiting adjudication", r) or "ineligible" in r.lower() \
                or re.search(r"\b(not|no longer|never|non)\b[^.;:]{0,40}\beligible\b", r, re.I) \
                or "the numbers are not asserted wrong" not in r \
                or "asserted wrong" in r.lower().replace("not asserted wrong", ""):   # case-insensitive (codex r12 #3)
            return None        # ... and no negated eligibility ('not eligible evidence'; codex v8-apply-r9 #2)
        out[tid] = p
    return out
