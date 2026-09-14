"""LANE (Codex): ITT invariant, done carefully. For every pooled primary trial with an NCT, fetch
CT.gov participant flow, take STARTED per arm from the FIRST period only (dedup milestone-type
variants), sum, and compare to the pooled analysed denominator (n1i+n2i). randomised != analysed =>
label is not strict ITT-as-randomised. Writes scratchpad/itt_careful.json (OUT-first: stub then fill).
"""
import json, os, sys, io, time, glob, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "itt_careful.json")
json.dump({"status": "STARTED"}, open(OUT, "w", encoding="utf-8"))  # OUT-first contract


def started_per_arm(nct):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "meta-harness/1.0 (research)"})
        j = json.load(urllib.request.urlopen(req, timeout=45))
    except Exception:
        return None
    pf = (j.get("resultsSection") or {}).get("participantFlowModule")
    if not pf or not pf.get("periods"):
        return None
    per = pf["periods"][0]  # FIRST period only -- avoids double-counting across periods
    tot = 0
    for m in per.get("milestones", []):
        if (m.get("type") or "").strip().upper() == "STARTED":
            for a in m.get("achievements", []):
                try:
                    tot += int(a.get("numSubjects") or 0)
                except ValueError:
                    pass
    return tot or None


rows, checked = [], 0
for rp in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
    slug = os.path.basename(os.path.dirname(rp))
    rv = json.load(open(rp, encoding="utf-8"))
    recs = {str(r.get("id")): r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8")).get("records", [])}
    prim = next((o for o in rv.get("outcomes", []) if o.get("primary")), None)
    for t in (prim or {}).get("trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "")
        if t.get("n1i") is None or t.get("n2i") is None:
            continue
        nct = recs.get(pid, {}).get("nct") or (pid if pid.startswith("NCT") else None)
        if not nct:
            continue
        st = started_per_arm(nct)
        time.sleep(0.25)
        if not st:
            continue
        checked += 1
        analysed = t["n1i"] + t["n2i"]
        if abs(st - analysed) > 0:
            rows.append({"slug": slug, "pmid": pid, "nct": nct, "randomised_started": st,
                         "analysed": analysed, "diff": st - analysed})

json.dump({"status": "DONE", "checked": checked, "mismatches": rows,
           "_doc": "randomised(STARTED, first period) vs analysed(n1i+n2i); mismatch => not strict ITT"},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OUT_WRITTEN {OUT} checked={checked} mismatches={len(rows)}")
