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
        out[o["nct"]].append({"title": o["title"], "type": o["type"],
                              "param_type": o["param_type"], "arms": arms})
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
