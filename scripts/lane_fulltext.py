"""LANE (Codex, network): full-text fetch for abstract-only pooled/declared-absent trials across all
32. Unblocks the ITT invariant (paper-level randomised N per arm), the harms re-check, the override
review, and analysis-population work. For each such trial with a PMID, resolve PubMed->PMC (open
access) and fetch the PMC full text; store cache/<slug>/ft_<pmid>.txt. Skips trials we already hold
full text for. Writes scratchpad/fulltext_fetch.json (OUT-first)."""
import json, os, sys, io, time, glob, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "fulltext_fetch.json")
json.dump({"status": "STARTED"}, open(OUT, "w", encoding="utf-8"))
UA = {"User-Agent": "meta-harness/1.0 (research; mahmood726@gmail.com)"}


def pmc_id(pmid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?" + urllib.parse.urlencode(
        {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "retmode": "json", "linkname": "pubmed_pmc"})
    try:
        j = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        ls = j.get("linksets", [{}])[0].get("linksetdbs", [])
        for d in ls:
            if d.get("linkname") == "pubmed_pmc" and d.get("links"):
                return d["links"][0]
    except Exception:
        return None
    return None


def pmc_text(pmcid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pmc", "id": pmcid, "rettype": "full", "retmode": "text"})
    try:
        t = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read().decode("utf-8", "replace")
        return t if len(t) > 500 else None  # a stub is not full text
    except Exception:
        return None


# collect pooled + declared-absent PMIDs per topic
targets = {}
for rp in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
    slug = os.path.basename(os.path.dirname(rp))
    rv = json.load(open(rp, encoding="utf-8"))
    pids = set()
    for o in rv.get("outcomes", []):
        for key in ("trials", "declared_absent_trials"):
            for t in o.get(key, []) or []:
                pid = str(t.get("id", "")).replace("PMID ", "")
                if pid.isdigit():
                    pids.add(pid)
    if pids:
        targets[slug] = sorted(pids)

fetched, skipped, no_pmc, total = 0, 0, 0, 0
per = {}
for slug, pids in targets.items():
    got = 0
    for pid in pids:
        total += 1
        dest = os.path.join(ROOT, "cache", slug, f"ft_{pid}.txt")
        if os.path.exists(dest):
            skipped += 1
            continue
        pc = pmc_id(pid)
        time.sleep(0.2)
        if not pc:
            no_pmc += 1
            continue
        txt = pmc_text(pc)
        time.sleep(0.2)
        if txt:
            open(dest, "w", encoding="utf-8").write(txt)
            fetched += 1
            got += 1
    per[slug] = got
    print(f"{slug}: fetched {got} new full texts", flush=True)
    json.dump({"status": "RUNNING", "fetched": fetched, "skipped": skipped, "no_pmc": no_pmc,
               "total": total, "per_topic": per}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

json.dump({"status": "DONE", "fetched": fetched, "already_had": skipped, "no_open_access": no_pmc,
           "total_trials": total, "per_topic": per}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OUT_WRITTEN {OUT} fetched={fetched} no_pmc={no_pmc} total={total}")
