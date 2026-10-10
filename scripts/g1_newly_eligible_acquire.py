"""TYPED ACQUISITION for the trials the sprint's dual screen made newly eligible (k-gap, 10 Oct). No model call: every value
is a verbatim span from an open source the licence guard always admits (the PubMed abstract record; CT.gov posted results).
Nothing here is applied to a served page -- the file is the V14 input.

Per trial: the protocol's outcome (cortico-covid: 28-day all-cause mortality; doac: recurrent VTE at trial end), every
abstract sentence carrying a number beside the outcome's terms (the SPAN), the abstract's COVERAGE label against the
current PubMed record, and for an NCT the CT.gov posted primary-outcome titles + whether results are posted. A span is a
CANDIDATE, not a bound value: binding goes through the existing gates (binding lane / V14).

    python scripts/g1_newly_eligible_acquire.py -> outputs/k_gap/newly_eligible_acquired.json
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

TARGETS = {
    "corticosteroids-covid19-mortality": {
        "outcome": "28-day all-cause mortality",
        "terms": r"mortalit|death|died|dead|surviv",
        "ids": ["32943404", "35295605", "35361632", "39086948", "42079491", "NCT04244591", "NCT04438980",
                "NCT04673162", "NCT04360876"]},
    "doac-vte-recurrence": {
        "outcome": "recurrent VTE at trial end",
        "terms": r"recurren|venous thromboembol|\bVTE\b|deep vein|pulmonary embol|thrombus",
        "ids": ["18541000", "31455473", "NCT02506985"]},
    "semaglutide-obesity-weight": {
        "outcome": "percent body-weight change, Week 68",
        "terms": r"body weight|weight change|week 68|68 weeks|week 104|104 weeks",
        "ids": ["36216945", "NCT03693430"]},
}
NUM = re.compile(r"\d")


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", t or "") if s.strip()]


def ctgov(nct):
    from harness import http
    st, b = http.get_raw(f"https://clinicaltrials.gov/api/v2/studies/{nct}",
                         {"fields": "NCTId,OverallStatus,EnrollmentInfo,OutcomeMeasuresModule,ReferencesModule,HasResults"},
                         tries=3, timeout=60)
    if st != 200:
        return {"state": "FETCH_FAILED", "status": st}
    d = json.loads(b)
    ps = d.get("protocolSection") or {}
    oms = ((d.get("resultsSection") or {}).get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []
    return {"state": "OK", "response_sha256": hashlib.sha256(b).hexdigest(),
            "overall_status": ps.get("statusModule", {}).get("overallStatus"),
            "enrollment": (ps.get("designModule") or {}).get("enrollmentInfo"),
            "has_results": bool(d.get("hasResults")),
            "result_refs": [r.get("pmid") for r in (ps.get("referencesModule") or {}).get("references", [])
                            if r.get("type") == "RESULT"],
            "posted_outcomes": [{"type": o.get("type"), "title": o.get("title"), "timeFrame": o.get("timeFrame")}
                                for o in oms]}


def main():
    import g1_abstract_census as cen
    out, today = {"writer": "scripts/g1_newly_eligible_acquire.py", "written": datetime.date.today().isoformat(),
                  "applied": False, "trials": {}}, None
    for slug, t in TARGETS.items():
        pm = [i for i in t["ids"] if i.isdigit()]
        fresh = cen.fetch_abstracts(pm) if pm else {}
        held = {}
        p = os.path.join(ROOT, "outputs", "k_gap", "concept", f"{slug}.records.json")
        if os.path.exists(p):
            held = {str(r.get("id")): r for r in json.load(open(p, encoding="utf-8"))}
        for i in t["ids"]:
            row = {"slug": slug, "protocol_outcome": t["outcome"]}
            if i.isdigit():
                ab, xsha = fresh.get(i, ("", None))
                h = cen._n((held.get(i) or {}).get("abstract"))
                cov = ("NO_ABSTRACT" if not cen._n(ab) else "FULL_ABSTRACT" if h == cen._n(ab)
                       else "EXCERPT" if h and h in cen._n(ab) else "PUBMED_ONLY")
                spans = [s for s in sentences(ab) if re.search(t["terms"], s, re.I) and NUM.search(s)]
                row.update(source="PUBMED_ABSTRACT", pubmed_record_sha256=xsha, coverage=cov,
                           abstract_sha256=hashlib.sha256(ab.encode("utf-8")).hexdigest() if ab else None,
                           candidate_spans=spans,
                           state="CANDIDATE_SPANS" if spans else "OUTCOME_NOT_IN_ABSTRACT")
                ncts = sorted(set(re.findall(r"NCT\d{8}", json.dumps(held.get(i) or {}) + ab)))
                if ncts:
                    row["stated_registrations"] = ncts
            else:
                row.update(source="CTGOV", **ctgov(i))
                row["state"] = ("POSTED_RESULTS" if row.get("has_results") else
                                "NO_PARTICIPANTS" if (row.get("enrollment") or {}).get("count") == 0 else
                                "NO_POSTED_RESULTS")
            out["trials"][i] = row
            print(slug, i, row["state"], row.get("coverage", ""), len(row.get("candidate_spans") or []), flush=True)
    dst = os.path.join(ROOT, "outputs", "k_gap", "newly_eligible_acquired.json")
    json.dump(out, open(dst, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(dst)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
