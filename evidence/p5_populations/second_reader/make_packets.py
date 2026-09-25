"""Blind second-reader packets for the 53 P5 rows: one job per row, every fact of its chain.
The reader sees the review's topic requirements and the held documents cited for (or searched for) the row, each
projected to the trial's own record -- never evid2's state, EV53's interpretation, or which span was cited.
Usage: make_packets.py <jobs_dir>"""
import gzip, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LED = json.load(open(os.path.join(HERE, "..", "ledger.json"), encoding="utf-8"))
EV = json.load(open(os.path.join(ROOT, "evidence", "inputs", "ev53.json"), encoding="utf-8"))
SEARCH = json.load(open(os.path.join(HERE, "..", "searches.json"), encoding="utf-8"))
LOCAL = r"C:\mh-lanes\evid2-held"
PROJECTION = "one line per JSON string value, '<pointer>: <value>'; non-JSON files verbatim"
FACTS = {
    "entry_population": "participants entered the trial belonging to the population the review requires (see population_any / population_none)",
    "randomized_contrast": "participants were RANDOMLY assigned between the review's intervention and its comparator",
    "registry_parent": "the trial has a registration identifier (e.g. NCT/ISRCTN/ACTRN/EudraCT number) stated in a document of THIS trial",
    "placebo_control": "the comparator arm received a placebo (not usual care / no treatment / an active drug)",
    "masking": "the trial was blinded/masked as the review requires",
    "design": "the trial is a randomized controlled trial of the design the review requires (e.g. parallel groups)",
    "arms": "the trial's arms are the review's intervention and its comparator",
}


def doc_path(ref):
    """document + record-level pointer (first two components), e.g. cache/x/records.json#/records/0"""
    ref = ref or ""
    if "#/" not in ref:
        return ref
    p, ptr = ref.split("#", 1)
    return p + "#/" + "/".join(ptr.strip("/").split("/")[:2])


def strings(o, path=""):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k in sorted(o):
            yield from strings(o[k], f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f"{path}/{i}")


def origin_file(fp):
    return os.path.join(LOCAL, fp[6:]) if fp.startswith("LOCAL:") else os.path.join(ROOT, fp)


def project(src, ptr, pmid):
    """(raw bytes, text shown to the reader). JSON: the pointed object, or the trial's own records; else verbatim."""
    raw = open(src, "rb").read()
    dec = gzip.decompress(raw) if src.endswith(".gz") else raw
    if not (src.endswith(".json") or src.endswith(".json.gz")):
        return raw, dec.decode("utf-8", "replace")
    o = json.loads(dec)
    if ptr:
        for part in ptr.strip("/").split("/"):
            o = o[int(part)] if isinstance(o, list) else o[part]
        objs = [(ptr, o)]
    elif isinstance(o, dict) and isinstance(o.get("records"), list):
        objs = [(f"/records/{i}", r) for i, r in enumerate(o["records"])
                if pmid and str(r.get("id") or r.get("pmid")) == pmid]
    else:
        objs = [("", o)]
    lines = [f"{base}{k}: {v}" for base, ob in objs for k, v in strings(ob)]
    return raw, "\n".join(lines) + "\n"


def row_documents(r):
    paths = []
    for f in r["facts"]:
        for e in f["evidence"]:
            p = doc_path(e.get("document_ref") or e.get("ref"))
            if p and p not in paths:
                paths.append(p)
            m = re.search(r"LOCAL_ONLY:(\S+)", e.get("document") or "")
            if m and ("LOCAL:" + m.group(1)) not in paths:
                paths.append("LOCAL:" + m.group(1))
        for d in (SEARCH.get(f"{r['key']}/{f['fact_id']}") or {}).get("step1_held_documents_scanned", []):
            if d["path"] not in paths:
                paths.append(d["path"])
    return paths


def main(out):
    rows = {r["index"]: r for r in EV["rows"]}
    for r in LED["rows"]:
        j = os.path.join(out, r["key"])
        os.makedirs(j, exist_ok=True)
        pmid = (re.search(r"PMID (\d+)", r["trial"]) or [None, None])[1]
        docs = []
        for i, p in enumerate(row_documents(r)):
            fp, _, ptr = p.partition("#")
            src = origin_file(fp)
            if not os.path.exists(src):
                continue
            raw, text = project(src, ptr, pmid)
            if not text.strip():
                continue
            name = f"doc{i:02d}_" + re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(fp)) + ".txt"
            open(os.path.join(j, name), "w", encoding="utf-8", newline="\n").write(text)
            docs.append({"file": name, "origin": p, "origin_sha256": hashlib.sha256(raw).hexdigest(), "projection": PROJECTION})
        row = {"key": r["key"], "trial": r["trial"], "family_id": r.get("family_id"), "slug": r["slug"],
               "topic_requirements": rows[r["index"]].get("topic_requirements"),
               "facts": [{"fact_id": f["fact_id"], "question": FACTS.get(f["fact_id"], f["fact_id"])} for f in r["facts"]],
               "documents": docs}
        json.dump(row, open(os.path.join(j, "row.json"), "w", encoding="utf-8"), indent=1)
    print(len(LED["rows"]), "packets")


if __name__ == "__main__":
    main(sys.argv[1])
