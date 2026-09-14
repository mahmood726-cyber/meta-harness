"""LANE (Codex, network): scale the rebuilt concept search to all 32 and measure the PRIZE column.
Per topic: build the concept query (P/I/C/design + class expansion), paginate the full boolean set,
take the PMIDs NOT already held, fetch each abstract (capped), run the deterministic screen, and count
how many are eligible -> NEWLY-FOUND ELIGIBLE NOT PREVIOUSLY HELD. That is the only evidence the search
WORKS rather than recalls what someone already named. Writes scratchpad/search_screen.json (OUT-first).
"""
import json, os, sys, io, time, glob, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts.search_rebuild import build_query, esearch_all
from harness import screen
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "search_screen.json")
json.dump({"status": "STARTED"}, open(OUT, "w", encoding="utf-8"))

CAP = 120  # per topic, new-PMID abstracts fetched+screened (keeps the lane bounded)


def held(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return set()
    r = json.load(open(p, encoding="utf-8"))
    r = r.get("records", r) if isinstance(r, dict) else r
    return {str(x.get("id")) for x in r if str(x.get("id", "")).isdigit()}


def efetch_abstract(pmid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text"})
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness/1.0 (research)"}), timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return ""


summary = {}
for cfgp in sorted(glob.glob(os.path.join(ROOT, "topics", "*.json"))):
    slug = os.path.basename(cfgp)[:-5]
    if not os.path.exists(os.path.join(ROOT, "docs", "reviews", slug, "review.json")):
        continue
    cfg = json.load(open(cfgp, encoding="utf-8"))
    inc = cfg.get("include", {})
    ids, total = esearch_all(build_query(cfg), cap=6000)
    h = held(slug)
    new = [i for i in ids if i not in h][:CAP]
    screened = eligible = 0
    newly = []
    for pmid in new:
        ab = efetch_abstract(pmid)
        time.sleep(0.2)
        if not ab:
            continue
        screened += 1
        rec = {"id": pmid, "id_type": "pmid", "title": ab.split("\n\n")[0][:300], "abstract": ab,
               "pubtypes": ["Randomized Controlled Trial"] if "randomized controlled trial" in ab.lower() else []}
        try:
            decision, rule, reason, span = screen.screen_record(rec, inc, [])
        except Exception:
            continue
        if decision == "include":
            eligible += 1
            newly.append(pmid)
    summary[slug] = {"retrieved": total, "new_fetched": len(new), "screened": screened,
                     "newly_found_eligible": eligible, "newly_ids": newly[:25]}
    print(f"{slug}: retrieved={total} new_fetched={len(new)} screened={screened} newly_eligible={eligible}", flush=True)
    json.dump({"status": "RUNNING", "topics": summary}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

tot_new = sum(s["newly_found_eligible"] for s in summary.values())
json.dump({"status": "DONE", "cap_per_topic": CAP, "total_newly_found_eligible": tot_new, "topics": summary},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OUT_WRITTEN {OUT} total_newly_found_eligible={tot_new}")
