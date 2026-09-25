"""Step-4 screening packets (POLICY.md amendment A): per UNRESOLVED trial, the trial's own Europe PMC core record and
every hit of queries 4a/4b, for a reader to name which hits could be THIS trial's protocol/design/baseline paper.
usage: make_step4_packets.py <step4.json> <held_dir> <jobs_dir>"""
import glob, json, os, re, sys

step4, held, out = json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2], sys.argv[3]
for key, v in step4.items():
    if not v.get("pmid"):
        continue
    core = sorted(glob.glob(os.path.join(held, f"epmc_core_{v['pmid']}.*")))
    rec = json.load(open(core[-1], encoding="utf-8"))["resultList"]["result"][0] if core else {}
    j = os.path.join(out, key)
    os.makedirs(j, exist_ok=True)
    trial = {"key": key, "pmid": v["pmid"], "title": rec.get("title"), "authors": rec.get("authorString"),
             "journal": (rec.get("journalInfo") or {}).get("journal", {}).get("title"), "year": rec.get("pubYear"),
             "abstract": re.sub(r"<[^>]+>", " ", rec.get("abstractText") or ""), "facts_unresolved": v["facts"]}
    hits = [dict(h, query=q["step"]) for q in v["queries"] for h in q.get("hits", []) if not h.get("is_the_trial_report")]
    json.dump({"trial": trial, "hits": hits}, open(os.path.join(j, "row.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(key, len(hits))
