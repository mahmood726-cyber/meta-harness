"""Sample what the screener REJECTED among newly-retrieved records, weighted to high-retrieval-growth
topics, so a human can adjudicate whether '0 newly-eligible' means the corpus is complete (rejections
sound) or the screener is the bottleneck (rejections wrong). For each topic, esearch the concept query,
take NEW PMIDs (not held), screen each, and collect the first N REJECTED with {pmid, rule, reason,
title}. Writes scratchpad/reject_sample.json for hand-adjudication against registered P/I/C/design."""
import json, os, sys, io, time, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts.search_rebuild import build_query, esearch_all
from harness import screen
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "scratchpad", "reject_sample.json")

TOPICS = ["omega3-cardiovascular-events", "sglt2-primary-prevention-hf", "noac-vs-warfarin-af-stroke",
          "glp1-ra-mace-t2d", "dpp4-mace-t2d", "colchicine-secondary-cv-prevention"]
N_PER = 6


def held(slug):
    r = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8")).get("records", [])
    return {str(x.get("id")) for x in r if str(x.get("id", "")).isdigit()}


def efetch(pmid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text"})
    for attempt in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mh/1.0"}), timeout=30).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return ""


sample = []
for slug in TOPICS:
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    inc = cfg.get("include", {})
    ids, total = esearch_all(build_query(cfg), cap=6000)
    h = held(slug)
    new = [i for i in ids if i not in h]
    got = 0
    for pmid in new:
        if got >= N_PER:
            break
        ab = efetch(pmid)
        time.sleep(0.2)
        if not ab:
            continue
        title = ab.split("\n\n")[0].replace("\n", " ")[:160]
        rec = {"id": pmid, "id_type": "pmid", "title": title, "abstract": ab,
               "pubtypes": ["Randomized Controlled Trial"] if "randomized controlled trial" in ab.lower() else []}
        try:
            decision, rule, reason, span = screen.screen_record(rec, inc, [])
        except Exception as e:
            decision, rule, reason = "error", "?", str(e)
        if decision != "include":
            sample.append({"slug": slug, "pmid": pmid, "rule": rule, "reason": reason[:150],
                           "title": title, "abstract_head": " ".join(ab.split())[:400]})
            got += 1
    print(f"{slug}: retrieved={total} held={len(h)} new={len(new)} sampled_rejections={got}", flush=True)
    json.dump({"n_sampled": len(sample), "topics": TOPICS, "sample": sample}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)  # incremental

print(f"OUT_WRITTEN {OUT} n_sampled={len(sample)}")
