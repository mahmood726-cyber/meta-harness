"""ITT invariant sweep (external audit): ITT_AS_RANDOMISED requires randomised N == analysed
(effect) N. CAPE COD randomised 401/399 but analysed 400/395 (a hydrocortisone patient died before
treatment and was excluded on a MORTALITY endpoint). Compare, per pooled primary trial with an NCT
in the local AACT snapshot, total RANDOMISED (participant-flow STARTED, summed over arms) against
total ANALYSED (sum of pooled n1i+n2i). A mismatch means the label ITT-as-randomised is not strict.
Total-level (robust; no arm-matching guesswork). Writes scratchpad/itt_sweep.json.
"""
import json, os, sys, io, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import aact
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def analysed_total(trials):
    tot = 0
    for t in trials:
        if t.get("n1i") is not None and t.get("n2i") is not None:
            tot += t["n1i"] + t["n2i"]
    return tot


rows, checked, mism = [], 0, []
# collect all pooled-primary trials per topic with their NCT
per_topic = {}
alln = set()
for rp in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
    slug = os.path.basename(os.path.dirname(rp))
    rv = json.load(open(rp, encoding="utf-8"))
    recs = {str(r.get("id")): r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8")).get("records", [])}
    prim = next((o for o in rv.get("outcomes", []) if o.get("primary")), None)
    lst = []
    for t in (prim or {}).get("trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "")
        nct = (recs.get(pid, {}).get("nct") or (pid if pid.startswith("NCT") else None))
        if nct and t.get("n1i") is not None and t.get("n2i") is not None:
            lst.append((pid, nct.upper(), t["n1i"] + t["n2i"]))
            alln.add(nct.upper())
    if lst:
        per_topic[slug] = lst

# one pass over AACT participant-flow milestones for STARTED per NCT
started = {}
try:
    flow = aact.attrition(alln)  # returns per-nct attrition incl started? fall back below
except Exception:
    flow = {}
# aact.attrition may not expose 'started' totals directly; read milestones for STARTED
for r in aact._iter_rows(aact._table("milestones")) if hasattr(aact, "_iter_rows") else []:
    nct = (r.get("nct_id") or "").upper()
    if nct in alln and (r.get("title") or "").strip().upper() == "STARTED":
        started[nct] = started.get(nct, 0) + int(r.get("count") or 0)

for slug, lst in per_topic.items():
    for pid, nct, analysed in lst:
        st = started.get(nct)
        if not st:
            continue
        checked += 1
        if abs(st - analysed) > 0:
            mism.append({"slug": slug, "pmid": pid, "nct": nct, "randomised_started": st,
                         "analysed": analysed, "diff": st - analysed})

out = {"_doc": "ITT_AS_RANDOMISED requires randomised==analysed; mismatch => label is MODIFIED_ITT / "
               "SOURCE_PRIMARY_ANALYSIS, not strict ITT. Total-level (participant-flow STARTED vs pooled n).",
       "checked": checked, "mismatches": mism}
json.dump(out, open(os.path.join(ROOT, "scratchpad", "itt_sweep.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"ITT invariant checked (pooled trials with AACT STARTED): {checked}")
print(f"MISMATCHES (randomised != analysed -> not strict ITT-as-randomised): {len(mism)}")
for m in mism:
    print(f"  {m['slug']:38s} {m['pmid']:12s} randomised={m['randomised_started']} analysed={m['analysed']} diff={m['diff']}")
