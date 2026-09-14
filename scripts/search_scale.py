"""Scale the concept-query search across ALL live topics and surface the prize: eligible-looking
records the rebuilt search finds that are NOT already in our committed corpus. Retrieval pass:
for each topic, build the concept query (registered P/I/C/design + class expansion), esearch the
full boolean set (paginated), and diff against the PMIDs we already hold. Reports
retrieved / already-held / NEW per topic. Screening the NEW set (retrieved->screened->eligible) is
the next pass; this pass isolates what the query alone recovers.
"""
import json, os, sys, io, time, glob, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts.search_rebuild import build_query, esearch_all  # reuse the engine
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")  # safe: rebuild no longer re-wraps on import


def held_pmids(slug):
    """PMIDs already in the topic's committed cache (records.json)."""
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return set()
    r = json.load(open(p, encoding="utf-8"))
    r = r.get("records", r) if isinstance(r, dict) else r
    out = set()
    for rec in r:
        pid = str(rec.get("id") or rec.get("pmid") or "")
        if pid.isdigit():
            out.add(pid)
    return out


live = sorted({os.path.basename(os.path.dirname(f))
               for f in glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))})
summary = {}
for slug in live:
    cfgp = os.path.join(ROOT, "topics", slug + ".json")
    if not os.path.exists(cfgp):
        continue
    cfg = json.load(open(cfgp, encoding="utf-8"))
    q = build_query(cfg)
    ids, total = esearch_all(q, cap=6000)
    held = held_pmids(slug)
    new = [i for i in ids if i not in held]
    summary[slug] = {"retrieved": total, "fetched": len(ids), "held": len(held),
                     "held_retrieved": len([i for i in ids if i in held]), "new": len(new),
                     "new_ids_sample": new[:15]}
    print(f"{slug:40s} retrieved={total:5d} held={len(held):3d} held∩retrieved="
          f"{summary[slug]['held_retrieved']:3d} NEW={len(new):5d}")
    time.sleep(0.34)

json.dump(summary, open(os.path.join(ROOT, "scratchpad", "search_scale.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
tot_new = sum(s["new"] for s in summary.values())
print(f"\nTOTAL new (retrieved, not yet held) across {len(summary)} topics: {tot_new}")
print("Wrote scratchpad/search_scale.json. NEXT: screen the NEW sets (retrieved->screened->eligible).")
