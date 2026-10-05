"""SIGNED SERVED-POOL ADDITIONS: the only route by which a trial the G1 tracker verified outside the served pool may
enter a served pool. registry/served_pool_additions.json is GENERATED (scripts/build_served_pool_additions.py) and
never hand-edited; this loader re-checks it at build time and admits a row only when ALL hold:

  * the register entry names a notice in docs/result_changes.json for this slug and outcome, by when_utc;
  * that notice is SIGNED (SEEN_AND_SIGNED / BATCH_SEEN_AND_SIGNED), and its signature names the same rendered_sha256
    the register recorded (a re-signed or rebuilt notice invalidates the register entry until it is regenerated);
  * the notice's entered_pool names the row's id.

Anything else admits nothing -- fail closed. The rows then pass through every downstream pipeline gate (estimand,
locate, per-trial verification, design), and the publication gate still requires the served result to match the
signed notice's 'after' exactly (result_changes.notice_for)."""
from __future__ import annotations

import copy
import json
import os
from typing import Any

from . import result_changes as rc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join(ROOT, "registry", "served_pool_additions.json")


def _load_register(path: str | None = None) -> list[dict[str, Any]]:
    p = path or REGISTER
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return list((json.load(fh) or {}).get("additions") or [])


def admitted_rows(slug: str | None, outcome: str | None, *, register: list[dict[str, Any]] | None = None,
                  notices: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Rows a SIGNED notice admits to this slug's outcome (deep copies), else []."""
    if not slug or not outcome:
        return []
    reg = _load_register() if register is None else register
    entries = [e for e in reg if e.get("slug") == slug and e.get("outcome") == outcome]
    if not entries:
        return []
    ns = rc.load() if notices is None else notices
    out = []
    for e in entries:
        n = next((n for n in ns if n.get("slug") == slug and n.get("outcome") == outcome
                  and n.get("when_utc") == e.get("notice_when_utc")), None)
        sig = (n or {}).get("reviewer_countersignature") or {}
        if not n or sig.get("state") not in rc.SIGNED_STATES or rc._delegation_problem(sig, n):
            continue
        if not e.get("rendered_sha256") or sig.get("rendered_sha256") != e["rendered_sha256"]:
            continue
        entered = {str(x) for x in n.get("entered_pool") or []}
        for row in e.get("rows") or []:
            if str(row.get("id")) in entered:
                out.append(copy.deepcopy(row))
    return out


# An admitted row SUPERSEDES the pipeline's own absence of the same trial only when that absence says the value was
# not found or was the wrong estimand in what the pipeline read (the signed row supplies the target value from another
# held source). Any other absence -- ineligible, withdrawn, population, timepoint, unit-of-analysis, a refusal on
# evidence -- stands, and the row is dropped instead: the served result then cannot match the signed 'after', and the
# ratchet refuses the page loudly.
SUPERSEDABLE = {"OUTCOME_NOT_IN_SOURCE", "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH", "EXTRACTION_NOT_PERFORMED",
                "SOURCE_NOT_RETRIEVED", "outcome_not_reported", "MACHINE_ABSENT_VALUE_NOT_FOUND"}


def _norm(x: Any) -> str:
    return str(x or "").replace("PMID ", "").strip()


def _code(a: dict[str, Any]) -> str | None:
    """The absence's code; a generic REFUSED_ON_EVIDENCE is read through the absence layer's own reason hints (the
    same classification it is published under), so a population/timepoint/multi-arm refusal never reads as superseded."""
    from . import absence
    code = a.get("reason_code") or a.get("state")
    if not code and a.get("absent_kind") == "machine_absent" and str(a.get("reason") or "").startswith("no "):
        return "MACHINE_ABSENT_VALUE_NOT_FOUND"     # the extractor found no value in what it read -- nothing refused
    if code == absence.REFUSED_ON_EVIDENCE:
        return absence._reason_hint_code(a.get("reason")) or code
    return code


def signed_entry(slug: str | None, outcome: str | None) -> dict | None:
    """The signed notice (when_utc, rendered_sha256, state) whose rows admitted_rows would admit here, or None."""
    if not admitted_rows(slug, outcome):
        return None
    e = next(e for e in _load_register() if e.get("slug") == slug and e.get("outcome") == outcome)
    return {"notice_when_utc": e.get("notice_when_utc"), "rendered_sha256": e.get("rendered_sha256"),
            "signature_state": e.get("signature_state"), "after": e.get("after"),
            "register": "registry/served_pool_additions.json"}


def reconcile(trials: list[dict[str, Any]], absent: list[dict[str, Any]], corrected_withdrawal: bool = False):
    """(trials, absent) with each admitted row either superseding its own supersedable absences or dropped. In a
    WITHDRAWN outcome whose corrected selection was signed (corrected_withdrawal), the signed row also supersedes the
    RESULT_WITHDRAWN entry of the same trial -- it is the correction that withdrawal waited for -- and says so."""
    keep, drop_absent = [], set()
    for t in trials:
        if t.get("provenance") != "served_pool_signed_notice":
            keep.append(t)
            continue
        ids = {_norm(t.get("id"))} | {_norm(r) for r in (t.get("served_pool_admission") or {}).get("report_ids") or []}
        mine = [i for i, a in enumerate(absent) if _norm(a.get("id")) in ids]
        states = {_code(absent[i]) for i in mine}
        allowed = SUPERSEDABLE | ({"RESULT_WITHDRAWN"} if corrected_withdrawal else set())
        if states - allowed:
            continue
        t.setdefault("served_pool_admission", {})["supersedes_absence"] = [
            {"id": absent[i].get("id"), "state": _code(absent[i]), "reason": absent[i].get("reason"),
             **({"withdrawn_effect": absent[i]["withdrawn_effect"]} if absent[i].get("withdrawn_effect") else {})}
            for i in mine]
        drop_absent.update(mine)
        keep.append(t)
    return keep, [a for i, a in enumerate(absent) if i not in drop_absent]
