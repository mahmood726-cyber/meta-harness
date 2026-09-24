"""Build one isolated codex job directory per count row: LANE_CONTEXT.md, BRIEF.md, row.json and copies of every held
document the row can mean (records.json entries for its PMID / family NCT, ft_<pmid>.txt, its document_ref file).
Each copied document is recorded with the sha256 of the bytes copied AND of the repo file it came from, so a span
verified against the copy is verified against held repo bytes. Nothing outside the job dir is context for the model."""
import json, os, sys, hashlib, shutil, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POP = os.path.join(HERE, "..", "population.json")
JOBS = sys.argv[1]  # e.g. C:/mh-lanes/evid2-codex/typed_arms
BRIEF = os.path.join(HERE, "..", "BRIEF.md")
LANE = os.path.join(HERE, "..", "LANE_CONTEXT.md")

def sha(b): return hashlib.sha256(b).hexdigest()

pop = json.load(open(POP, encoding="utf-8"))
os.makedirs(JOBS, exist_ok=True)
index = []
for r in pop["rows"]:
    slug = r["slug"]; cdir = os.path.join(ROOT, "cache", slug)
    pid = re.sub(r"\D", "", str(r["trial_id"] or r["label"] or "")) or None
    fam = r.get("family_id") or ""
    job = os.path.join(JOBS, r["row_id"]); os.makedirs(job, exist_ok=True)
    docs = []
    recpath = os.path.join(cdir, "records.json")
    recbytes = open(recpath, "rb").read()
    recs = json.loads(recbytes)["records"]
    for i, rec in enumerate(recs):
        rid = str(rec.get("id") or ""); nct = str(rec.get("nct") or "")
        if (pid and rid == pid) or (fam.startswith("NCT") and (rid == fam or fam in nct.split(","))):
            text = f"TITLE: {rec.get('title') or ''}\n\n{rec.get('abstract') or ''}\n"
            name = f"doc_records_{rec.get('id_type','X')}_{rid}.txt"
            b = text.encode("utf-8"); open(os.path.join(job, name), "wb").write(b)
            docs.append({"file": name, "sha256": sha(b), "origin": f"cache/{slug}/records.json#records[{i}] (title+abstract)",
                         "origin_sha256": sha(recbytes), "id": rid, "id_type": rec.get("id_type")})
    ctr = (json.loads(recbytes).get("ctgov_results") or {}).get(fam) if fam.startswith("NCT") else None
    if ctr is not None:
        b = json.dumps(ctr, indent=1, ensure_ascii=False).encode("utf-8"); name = f"doc_ctgov_results_{fam}.json"
        open(os.path.join(job, name), "wb").write(b)
        docs.append({"file": name, "sha256": sha(b), "origin": f"cache/{slug}/records.json#ctgov_results.{fam} (re-serialised indent=1)",
                     "origin_sha256": sha(recbytes), "id": fam, "id_type": "NCT_RESULTS"})
    cands = set()
    if pid and os.path.exists(os.path.join(cdir, f"ft_{pid}.txt")): cands.add(f"cache/{slug}/ft_{pid}.txt")
    for ref in [r.get("document_ref")] + list(r.get("document_candidates") or []):
        if ref and not ref.split("#")[0].endswith("records.json"): cands.add(ref.split("#")[0])
    for ref in sorted(cands):
        p = os.path.join(ROOT, ref)
        if not os.path.exists(p): docs.append({"file": None, "origin": ref, "state": "NOT_HELD_IN_TREE"}); continue
        b = open(p, "rb").read(); name = "doc_" + os.path.basename(ref)
        open(os.path.join(job, name), "wb").write(b)
        docs.append({"file": name, "sha256": sha(b), "origin": ref, "origin_sha256": sha(b)})
    row = {k: r[k] for k in ("row_id", "slug", "outcome_name", "outcome_kind", "served_estimand", "outcome_population",
                             "outcome_timepoint", "trial_id", "family_id", "served", "source", "endpoint_result_span",
                             "analysis_set", "follow_up_window", "registry_arms")}
    row["documents"] = docs
    json.dump(row, open(os.path.join(job, "row.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    shutil.copy(BRIEF, os.path.join(job, "BRIEF.md")); shutil.copy(LANE, os.path.join(job, "LANE_CONTEXT.md"))
    index.append({"row_id": r["row_id"], "docs": [d.get("file") for d in docs], "n_docs": sum(1 for d in docs if d.get("file"))})
json.dump(index, open(os.path.join(JOBS, "INDEX.json"), "w"), indent=1)
print(len(index), "jobs;", sum(1 for i in index if i["n_docs"] == 0), "with no held document")
for i in index:
    if i["n_docs"] == 0: print("  NO DOC:", i["row_id"])
