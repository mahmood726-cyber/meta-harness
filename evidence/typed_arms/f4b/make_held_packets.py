"""Extraction packets for HELD count entries (cache/<slug>/verified_arms.json objects carrying ai/n1i/ci/n2i -- the F4
schema's population of 34). Same isolated-job design as ../scripts/make_packets.py; the held entry's own tuple sits in
the `served` slot (it is what the entry claims), and the documents are the entry's document_ref / document_candidates,
its record's title+abstract, its ft_<pid>.txt, and the registry results held for the record's NCT id(s).

usage: python make_held_packets.py <jobs dir> [key ...]      (keys as slug/pid[/index]; default: all 34)"""
import hashlib, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.abspath(os.path.join(HERE, ".."))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def held_entries():
    for slug in sorted(os.listdir(os.path.join(ROOT, "cache"))):
        p = os.path.join(ROOT, "cache", slug, "verified_arms.json")
        if not os.path.isfile(p):
            continue
        for pid, v in json.load(open(p, encoding="utf-8")).items():
            items = v if isinstance(v, list) else [v]
            for i, e in enumerate(items):
                if isinstance(e, dict) and all(isinstance(e.get(k), (int, float)) and not isinstance(e.get(k), bool)
                                               for k in ("ai", "n1i", "ci", "n2i")):
                    yield f"{slug}/{pid}" + (f"/{i}" if isinstance(v, list) else ""), slug, pid, e


def job_id(key):
    return "HE-" + re.sub(r"[^A-Za-z0-9]+", "-", key)


def main():
    jobs, want = sys.argv[1], set(sys.argv[2:])
    os.makedirs(jobs, exist_ok=True)
    made = []
    for key, slug, pid, e in held_entries():
        if want and key not in want:
            continue
        cdir = os.path.join(ROOT, "cache", slug)
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        job = os.path.join(jobs, job_id(key))
        os.makedirs(job, exist_ok=True)
        docs = []
        recbytes = open(os.path.join(cdir, "records.json"), "rb").read()
        recj = json.loads(recbytes)
        ncts = set()
        for i, rec in enumerate(recj["records"]):
            if str(rec.get("id")) == pid:
                b = f"TITLE: {rec.get('title') or ''}\n\n{rec.get('abstract') or ''}\n".encode("utf-8")
                name = f"doc_records_pmid_{pid}.txt"
                open(os.path.join(job, name), "wb").write(b)
                docs.append({"file": name, "sha256": sha(b), "origin": f"cache/{slug}/records.json#records[{i}] (title+abstract)",
                             "origin_sha256": sha(recbytes)})
                ncts |= {x.strip() for x in str(rec.get("nct") or "").split(",") if x.strip().startswith("NCT")}
        for nct in sorted(ncts):
            ctr = (recj.get("ctgov_results") or {}).get(nct)
            if ctr is not None:
                b = json.dumps(ctr, indent=1, ensure_ascii=False).encode("utf-8")
                name = f"doc_ctgov_results_{nct}.json"
                open(os.path.join(job, name), "wb").write(b)
                docs.append({"file": name, "sha256": sha(b), "origin": f"cache/{slug}/records.json#ctgov_results.{nct} (re-serialised indent=1)",
                             "origin_sha256": sha(recbytes)})
        refs = {f"cache/{slug}/ft_{pid}.txt"} if os.path.exists(os.path.join(cdir, f"ft_{pid}.txt")) else set()
        for ref in [e.get("document_ref")] + list(e.get("document_candidates") or []):
            if ref and not ref.split("#")[0].endswith("records.json"):
                refs.add(ref.split("#")[0])
        for ref in sorted(refs):
            p = os.path.join(ROOT, ref)
            if not os.path.exists(p):
                docs.append({"file": None, "origin": ref, "state": "NOT_HELD_IN_TREE"})
                continue
            b = open(p, "rb").read()
            name = "doc_" + os.path.basename(ref)
            open(os.path.join(job, name), "wb").write(b)
            docs.append({"file": name, "sha256": sha(b), "origin": ref, "origin_sha256": sha(b)})
        row = {"row_id": job_id(key), "held_key": key, "slug": slug, "outcome_name": e.get("outcome"),
               "trial_id": f"PMID {pid}", "served": {k: e[k] for k in ("ai", "n1i", "ci", "n2i")},
               "source": e.get("source"), "intervention_terms": cfg.get("intervention_terms"),
               "comparator_terms": cfg.get("comparator_terms"), "registry_arms": None, "documents": docs}
        json.dump(row, open(os.path.join(job, "row.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
        shutil.copy(os.path.join(TA, "BRIEF.md"), os.path.join(job, "BRIEF.md"))
        shutil.copy(os.path.join(TA, "LANE_CONTEXT.md"), os.path.join(job, "LANE_CONTEXT.md"))
        made.append((job_id(key), [d.get("file") for d in docs]))
    for m in made:
        print(m[0][:52].ljust(52), m[1])
    print(len(made), "packets")


if __name__ == "__main__":
    main()
