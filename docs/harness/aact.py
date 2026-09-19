"""AACT local-snapshot adapter — the structured registry source.

AACT is the ClinicalTrials.gov research database, exported as pipe-delimited tables. A field read
from a column has no phrasing to get wrong, so this is the source that moves extraction off prose
regex (currently ~95% of pooled numbers) toward structured data. It is a FETCH/MEASURE-time source:
its outputs go into the committed cache (recall.json, records, ...) and the offline pipeline replays
from that cache, so a reader without AACT still reproduces the page.

Snapshot rules (see F:/AACT-storage/AACT_SNAPSHOT_README.md): a folder name OVERSTATES its data date
(always in the ghost direction), and surrogate ids are NOT stable across snapshots. We therefore key
only on nct_id/pmid (stable), and record the snapshot folder used for provenance.

Public surface (all local, no network, no rate limit):
* snapshot_dir()                       -> newest snapshot path, or None (fail closed)
* nct_to_pmids(ncts, types)            -> {nct: [pmid,...]} from study_references (RESULT/DERIVED)
* enumerate_nct(cond, intr)            -> [nct,...] whose conditions AND interventions match
* study_dates(ncts)                    -> {nct: {start, completion, results_posted, status, ...}}
"""
from __future__ import annotations

import os
import re

# AACT param_type/units CANNOT be trusted to mean "patients" for recurrent-event outcomes: HEART-FID's
# "Number of Hospitalizations for Heart Failure" is tagged COUNT_OF_PARTICIPANTS/units "Participants",
# but the trial reports "a total of 297 hospitalizations" — EVENTS, not patients. Treating that count
# as a binomial numerator over the arm size would over-count (a patient hospitalised twice is counted
# twice) and produce a wrong RR that passes every downstream gate. This regex flags an outcome whose
# TITLE denotes counts of EVENTS, so a caller must NOT pool it as a binomial (needs person-time / IRR).
_RECURRENT_TITLE = re.compile(
    r"\bnumber of\b.{0,30}\b(?:hospitali|admission|exacerbation|event|episode|visit|occurrence|attack|relapse)"
    r"|\b(?:total|recurrent|annuali[sz]ed|annual|yearly)\b.{0,25}\b(?:hospitali|exacerbation|admission|event|rate)"
    r"|\brate of\b.{0,25}\b(?:hospitali|exacerbation|admission|event|death)"
    r"|\bhospitali[sz]ations\b", re.I)
# A count is PATIENTS (binomial-safe) — not recurrent — when the title says so explicitly.
_PARTICIPANT_TITLE = re.compile(r"\bparticipants? (?:with|who)\b|\bnumber of participants\b|\bpatients? with\b", re.I)


def is_recurrent_event_title(title: str) -> bool:
    """True if the outcome TITLE denotes counts of EVENTS (recurrent), not patients-with-event.
    Such an AACT count must never be pooled as a binomial proportion regardless of its param_type.
    An explicit 'participants with ...' phrasing overrides (that IS a binomial patient count)."""
    t = title or ""
    if _PARTICIPANT_TITLE.search(t):
        return False
    return bool(_RECURRENT_TITLE.search(t))

# Trial's OWN publications: RESULT (a results paper) and DERIVED (PubMed-linked via the NCT).
# BACKGROUND is cited literature, NOT the trial's report, so it is excluded from linkage.
OWN_PUB_TYPES = ("RESULT", "DERIVED")


def snapshot_dir(root: str | None = None) -> str | None:
    """Newest AACT snapshot directory, or None if not present (fail closed). Override with the
    AACT_DIR env var (point it directly at a <date> snapshot folder) or the root argument."""
    env = os.environ.get("AACT_DIR")
    if env and os.path.isdir(env):
        return env
    roots = [root] if root else ["F:/AACT-storage/AACT", "C:/AACT-storage/AACT",
                                  "F:/aact", "C:/aact", "D:/aact"]
    for r in roots:
        if r and os.path.isdir(r):
            subs = [d for d in os.listdir(r) if os.path.isdir(os.path.join(r, d))
                    and d[:4].isdigit()]
            if subs:
                return os.path.join(r, sorted(subs)[-1])  # lexical sort of YYYY-MM-DD = newest
    return None


def _table(name: str, root: str | None = None) -> str | None:
    d = snapshot_dir(root)
    if not d:
        return None
    p = os.path.join(d, name + ".txt")
    return p if os.path.exists(p) else None


def _iter_rows(path: str):
    """Yield header-keyed dict rows from a pipe-delimited AACT export. Streaming (the files are
    up to multi-GB); no field in these tables legitimately contains a raw pipe."""
    with open(path, encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("|")
        n = len(header)
        for line in f:
            parts = line.rstrip("\n").split("|")
            if len(parts) < n:
                continue
            yield dict(zip(header, parts))


def nct_to_pmids(ncts, types=OWN_PUB_TYPES, root: str | None = None) -> dict[str, list[str]]:
    """Map each NCT in `ncts` to its own-publication PMIDs from study_references (ONE streaming
    pass). This is the linkage fix: AACT study_references links publications the CT.gov API's
    referencesModule omits (e.g. SALT PMID 27749094 -> NCT02345486, DERIVED)."""
    want = {str(n).strip().upper() for n in ncts}
    out: dict[str, list[str]] = {n: [] for n in want}
    p = _table("study_references", root)
    if not p or not want:
        return out
    for r in _iter_rows(p):
        nct = (r.get("nct_id") or "").upper()
        if nct in want and (r.get("reference_type") or "").upper() in types:
            pmid = (r.get("pmid") or "").strip()
            if pmid.isdigit() and pmid not in out[nct]:
                out[nct].append(pmid)
    return out


def sponsor_records(ncts, root: str | None = None) -> dict[str, dict[str, list[dict[str, str]]]]:
    """Registry sponsor/collaborator/responsible-party rows for NCTs from the local AACT snapshot.

    This is a disclosure source, not an eligibility gate: if AACT is unavailable or a row is absent, the
    caller gets an empty list and must not infer funding silence from that.
    """
    want = {str(n).strip().upper() for n in ncts if n}
    out: dict[str, dict[str, list[dict[str, str]]]] = {
        n: {"sponsors": [], "responsible_parties": []} for n in want
    }
    if not want:
        return out
    p = _table("sponsors", root)
    if p:
        for r in _iter_rows(p):
            nct = (r.get("nct_id") or "").upper()
            if nct in want:
                out[nct]["sponsors"].append({
                    "agency_class": r.get("agency_class") or "",
                    "lead_or_collaborator": r.get("lead_or_collaborator") or "",
                    "name": r.get("name") or "",
                })
    p = _table("responsible_parties", root)
    if p:
        for r in _iter_rows(p):
            nct = (r.get("nct_id") or "").upper()
            if nct in want:
                out[nct]["responsible_parties"].append({
                    "responsible_party_type": r.get("responsible_party_type") or "",
                    "name": r.get("name") or "",
                    "title": r.get("title") or "",
                    "organization": r.get("organization") or "",
                    "affiliation": r.get("affiliation") or "",
                    "old_name_title": r.get("old_name_title") or "",
                })
    return out


def _nct_set_for_term(table: str, col: str, term: str, root: str | None = None) -> set[str]:
    p = _table(table, root)
    tl = (term or "").lower()
    got: set[str] = set()
    if not p or not tl:
        return got
    for r in _iter_rows(p):
        if tl in (r.get(col) or "").lower():
            got.add((r.get("nct_id") or "").upper())
    return got


def enumerate_nct(cond: str, intr: str, root: str | None = None) -> list[str]:
    """NCTs whose registered condition AND intervention match the query terms (substring, lowercase).
    Broad by design — reach, not precision; the screen enforces eligibility downstream."""
    conds = _nct_set_for_term("conditions", "downcase_name", cond, root)
    intrs = _nct_set_for_term("interventions", "name", intr, root)
    return sorted(conds & intrs)


def outcome_arms(ncts, root: str | None = None) -> dict[str, list]:
    """Structured arm-level results per NCT, reconstructed from AACT (outcomes -> result_groups +
    outcome_measurements [per-arm event counts] + outcome_counts [per-arm denominators]). Returns
    {nct: [{title, type, param_type, arms: [{group, events, denom}]}]}. This is the structured
    extraction path that moves numbers off prose regex; it still needs outcome-identity gating before
    a value is pooled (an AACT primary can be a composite, e.g. AFFIRM-AHF 'HF Hospitalizations and
    CV Death'), so it is a fetch/measure-time source, verified per number, never auto-pooled.
    Four filtered streaming passes over large tables — batch use only."""
    want = {str(n).strip().upper() for n in ncts}
    if not want or not snapshot_dir(root):
        return {}
    # outcomes: id -> (nct, type, title, param_type)
    oc = {}
    for r in _iter_rows(_table("outcomes", root)):
        if (r.get("nct_id") or "").upper() in want:
            oc[r.get("id")] = {"nct": (r.get("nct_id") or "").upper(), "type": r.get("outcome_type"),
                               "title": r.get("title"), "param_type": r.get("param_type"), "arms": {}}
    # result_groups: id -> title
    rg = {}
    for r in _iter_rows(_table("result_groups", root)):
        if (r.get("nct_id") or "").upper() in want:
            rg[r.get("id")] = r.get("title")
    # outcome_measurements: per-arm event value (count outcomes only)
    for r in _iter_rows(_table("outcome_measurements", root)):
        oid = r.get("outcome_id")
        if oid in oc and (r.get("param_type") or "").upper().startswith("COUNT"):
            gid = r.get("result_group_id")
            v = r.get("param_value_num") or r.get("param_value")
            try:
                oc[oid]["arms"].setdefault(gid, {})["events"] = float(v)
            except (TypeError, ValueError):
                pass
    # outcome_counts: per-arm denominator (Participants scope)
    for r in _iter_rows(_table("outcome_counts", root)):
        oid = r.get("outcome_id")
        if oid in oc:
            gid = r.get("result_group_id")
            try:
                oc[oid]["arms"].setdefault(gid, {})["denom"] = float(r.get("count"))
            except (TypeError, ValueError):
                pass
    out: dict[str, list] = {n: [] for n in want}
    for o in oc.values():
        arms = [{"group": rg.get(gid, gid), "events": a.get("events"), "denom": a.get("denom")}
                for gid, a in o["arms"].items()]
        # GUARD: flag recurrent-event outcomes so no caller pools the count as a binomial (the
        # HEART-FID trap). A recurrent-event count needs person-time (IRR), never events/arm-size RR.
        recurrent = is_recurrent_event_title(o["title"])
        out[o["nct"]].append({"title": o["title"], "type": o["type"], "param_type": o["param_type"],
                              "is_recurrent_event": recurrent,
                              "binomial_safe": not recurrent, "arms": arms})
    return out


def _arm_of(title, interv_terms, comp_terms):
    t = (title or "").lower()
    if any(x and x.lower() in t for x in interv_terms or []):
        return "i"
    if any(x and x.lower() in t for x in comp_terms or []):
        return "c"
    return None


def summed_arms(pmid, interv_terms, comp_terms, outcome_terms, root: str | None = None) -> dict | None:
    """DETERMINISTIC per-arm 2x2 for a trial, summed across its NCT registrations, from the committed
    AACT snapshot. Generalises the arm-IDENTITY mechanism: a trial's registrations are discovered from
    study_references (own-publication link to this PMID); within each, the outcome-matching
    COUNT_OF_PARTICIPANTS measure and the arm 'Participants' denominators are aligned to
    intervention/comparator by RESULT-GROUP TITLE (never by magnitude). A registration contributes
    ONLY if it reports BOTH arms for the outcome AND its arm titles match this topic's terms — the
    identity gate that excludes a different trial that merely cites the same paper. Refuses (None) on a
    recurrent-event outcome title (needs person-time, not a binomial). No hand-typed number: the counts
    come from committed AACT, and the caller cross-checks them against the abstract %.

    Returns {"ai","n1i","ci","n2i","registrations":[...],"outcome_title":...,"provenance"} or None.
    """
    pmid = str(pmid).strip()
    # 1) discover this trial's own-publication registrations
    om_p, oc_p, rg_p, sr_p = (_table(t, root) for t in ("outcome_measurements", "outcome_counts",
                                                        "result_groups", "study_references"))
    if not all((om_p, oc_p, rg_p, sr_p)):
        return None
    ncts = set()
    for r in _iter_rows(sr_p):
        if (r.get("pmid") or "").strip() == pmid and (r.get("reference_type") or "").upper() in OWN_PUB_TYPES:
            ncts.add((r.get("nct_id") or "").upper())
    if not ncts:
        return None
    # 2) result-group titles per (nct, code)
    titles = {}
    for r in _iter_rows(rg_p):
        n = (r.get("nct_id") or "").upper()
        if n in ncts and r.get("ctgov_group_code"):
            titles[(n, r["ctgov_group_code"])] = r.get("title") or ""
    # 3) per-arm event counts (outcome-matched COUNT_OF_PARTICIPANTS) + denominators, per registration
    per = {n: {"i": {}, "c": {}, "otitle": None} for n in ncts}
    for r in _iter_rows(om_p):
        n = (r.get("nct_id") or "").upper()
        if n not in ncts:
            continue
        ot = (r.get("title") or "")
        if any(k in ot.lower() for k in outcome_terms) and (r.get("param_type") or "").upper() == "COUNT_OF_PARTICIPANTS":
            if is_recurrent_event_title(ot):
                return None  # recurrent-event outcome -> not a binomial; refuse
            arm = _arm_of(titles.get((n, r.get("ctgov_group_code")), ""), interv_terms, comp_terms)
            if arm:
                try:
                    per[n][arm]["events"] = int(float(r.get("param_value")))
                    per[n]["otitle"] = ot
                except (TypeError, ValueError):
                    pass
    for r in _iter_rows(oc_p):
        n = (r.get("nct_id") or "").upper()
        if n in ncts and (r.get("units") or "").lower().startswith("participant"):
            arm = _arm_of(titles.get((n, r.get("ctgov_group_code")), ""), interv_terms, comp_terms)
            if arm and "denom" not in per[n][arm]:
                try:
                    per[n][arm]["denom"] = int(r.get("count"))
                except (TypeError, ValueError):
                    pass
    # 4) sum only registrations with BOTH arms complete for this outcome (identity gate)
    used, ai = [], 0
    n1i = ci = n2i = 0
    otitle = None
    for n in sorted(ncts):
        a = per[n]
        if all(k in a["i"] for k in ("events", "denom")) and all(k in a["c"] for k in ("events", "denom")):
            ai += a["i"]["events"]; n1i += a["i"]["denom"]
            ci += a["c"]["events"]; n2i += a["c"]["denom"]
            used.append(n); otitle = otitle or a["otitle"]
    if not used or n1i == 0 or n2i == 0:
        return None
    return {"ai": ai, "n1i": n1i, "ci": ci, "n2i": n2i, "registrations": used,
            "outcome_title": otitle, "provenance": "aact_structured_summed"}


def attrition(ncts, root: str | None = None) -> dict[str, dict]:
    """Per-NCT participant-flow attrition from AACT milestones (Overall Study STARTED vs COMPLETED,
    per result group) — the machine-available signal for D3 (missing outcome data). Returns
    {nct: {"overall_pct": float, "differential_pct": float, "groups": [(started, completed), ...]}}.
    Overall = 1 - sum(completed)/sum(started); differential = spread of per-group attrition. Only the
    availability axis is machine-derivable; whether missingness depends on the outcome stays human."""
    want = {str(n).strip().upper() for n in ncts}
    p = _table("milestones", root)
    if not p or not want:
        return {}
    started: dict = {n: {} for n in want}
    completed: dict = {n: {} for n in want}
    for r in _iter_rows(p):
        n = (r.get("nct_id") or "").upper()
        if n not in want or (r.get("period") or "") != "Overall Study":
            continue
        t = (r.get("title") or "").upper()
        g = r.get("ctgov_group_code")
        try:
            c = int(r.get("count"))
        except (TypeError, ValueError):
            continue
        if t == "STARTED":
            started[n][g] = c
        elif t == "COMPLETED":
            completed[n][g] = c
    out: dict = {}
    for n in want:
        groups = [(started[n][g], completed[n].get(g, 0)) for g in started[n] if started[n][g] > 0]
        if not groups:
            continue
        tot_s = sum(s for s, _ in groups)
        tot_c = sum(c for _, c in groups)
        per = [1 - c / s for s, c in groups]
        out[n] = {"overall_pct": round(100 * (1 - tot_c / tot_s), 1) if tot_s else None,
                  "differential_pct": round(100 * (max(per) - min(per)), 1) if per else None,
                  "groups": groups}
    return out


def study_dates(ncts, root: str | None = None) -> dict[str, dict]:
    """Per-NCT registration/enrolment/results dates + status, for the prospective-registration and
    ghost-protocol checks. ONE streaming pass over studies."""
    want = {str(n).strip().upper() for n in ncts}
    out: dict[str, dict] = {}
    p = _table("studies", root)
    if not p or not want:
        return out
    for r in _iter_rows(p):
        nct = (r.get("nct_id") or "").upper()
        if nct in want:
            out[nct] = {
                "start_date": r.get("start_date"),
                "completion_date": r.get("completion_date") or r.get("primary_completion_date"),
                "study_first_submitted_date": r.get("study_first_submitted_date"),
                "results_first_posted_date": r.get("results_first_posted_date"),
                "overall_status": r.get("overall_status"),
            }
    return out
