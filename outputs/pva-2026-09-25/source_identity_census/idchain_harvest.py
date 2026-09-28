"""SOURCE-IDENTITY CHAIN CENSUS, step 1: harvest every citation of a source across the V1 tree, streamed from git objects
(no checkout, no disk). A CITATION is one place where the project asserts that identifiers belong together:
  - a text string naming a PMID together with a PMCID and/or DOI (e.g. "EMPA-KIDNEY (PMID 36331190, PMC9761906) full text: '...'")
  - a JSON object whose fields carry a PMID together with a PMCID and/or DOI (pmid/pmcid/doi/pmc keys)
  - a held full-text file (ft_<pmid>.txt / JATS) whose EMBEDDED article-ids are compared with the PMID it is filed under
Quoted text that follows a citation ("... full text: '<quote>'") is kept so step 3 can check it occurs in that publication."""
from __future__ import annotations

import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "C:/mh-lanes/pva"
COMMIT = sys.argv[1] if len(sys.argv) > 1 else "9eacfe09"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "C:/mh-lanes/tmp-pva/idcensus")
OUT.mkdir(parents=True, exist_ok=True)
ROOTS = ("docs/reviews", "cache", "evidence", "registry", "docs/m")

PMID = re.compile(r"(?:PMID[:\s#]*|pubmed/|pmid=)(\d{6,9})\b", re.I)
PMCID = re.compile(r"\bPMC(\d{5,9})\b")
DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>;,)\]}]+[^\s\"'<>;,.)\]}])")
NCT = re.compile(r"\bNCT\d{8}\b")
QUOTE_AFTER = re.compile(r"(?:full text|abstract|text)\s*:\s*['\"‘“](.{20,400}?)['\"’”]", re.I)


def blobs():
    ls = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", COMMIT, "--", *ROOTS], capture_output=True, text=True).stdout
    items = []
    for line in ls.splitlines():
        meta, path = line.split("\t", 1)
        mode, typ, sha = meta.split()
        if typ == "blob" and "/snapshots/" not in path:
            items.append((sha, path))
    p = subprocess.Popen(["git", "-C", REPO, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha, path in items:
        p.stdin.write((sha + "\n").encode())
        p.stdin.flush()
        hdr = p.stdout.readline().split()
        size = int(hdr[2])
        data = p.stdout.read(size)
        p.stdout.read(1)
        yield path, data
    p.stdin.close()
    p.wait()


def slug_of(path):
    m = re.match(r"(?:docs/reviews|cache)/([^/]+)/", path)
    if m:
        return m.group(1)
    m = re.search(r"(?:CD|HE)-([a-z0-9-]+?)-(?:\d|3\d{7})", path)
    return m.group(1) if m else ""


cites, ft_self = [], []
n_files = 0


def from_string(s, path, jpath):
    pm, pc, do = PMID.findall(s), PMCID.findall(s), DOI.findall(s)
    if pm and (pc or do):
        q = QUOTE_AFTER.search(s)
        cites.append({"kind": "text", "file": path, "slug": slug_of(path), "jpath": jpath, "pmids": sorted(set(pm)),
                      "pmcids": sorted({"PMC" + x for x in pc}), "dois": sorted({d.lower() for d in do}),
                      "ncts": sorted(set(NCT.findall(s))), "quote": q.group(1) if q else None, "context": s[:400]})


KEYS_PMID = ("pmid", "PMID", "pubmed_id")
KEYS_PMC = ("pmcid", "pmc", "PMCID", "pmc_id")
KEYS_DOI = ("doi", "DOI")


def walk(o, path, jpath):
    if isinstance(o, dict):
        pm = next((str(o[k]) for k in KEYS_PMID if o.get(k)), None)
        if not pm and str(o.get("id_type", "")).lower() == "pmid":
            pm = str(o.get("id"))
        if pm:
            pm = re.sub(r"\D", "", pm)
        pc = next((str(o[k]) for k in KEYS_PMC if o.get(k)), None)
        do = next((str(o[k]) for k in KEYS_DOI if o.get(k)), None)
        if pm and (pc or do):
            cites.append({"kind": "fields", "file": path, "slug": slug_of(path), "jpath": jpath, "pmids": [pm],
                          "pmcids": [("PMC" + re.sub(r"\D", "", pc))] if pc and re.search(r"\d", pc) else [],
                          "dois": [re.sub(r"^https?://(dx\.)?doi\.org/", "", do).lower()] if do else [],
                          "ncts": [str(o["nct"])] if str(o.get("nct", "")).startswith("NCT") else [],
                          "title": str(o.get("title") or "")[:200], "quote": None, "context": json.dumps(o, ensure_ascii=False)[:300]})
        for k, v in o.items():
            walk(v, path, f"{jpath}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path, f"{jpath}[{i}]")
    elif isinstance(o, str):
        if len(o) < 200000:
            from_string(o, path, jpath)


ART = re.compile(r'<article-id pub-id-type="(pmid|pmcid|pmc|doi)"[^>]*>([^<]+)</article-id>')
for path, data in blobs():
    n_files += 1
    if path.endswith(".gz"):
        try:
            data = gzip.decompress(data)
        except OSError:
            continue
        path_eff = path[:-3]
    else:
        path_eff = path
    if not path_eff.endswith((".json", ".jsonl", ".txt", ".html", ".md")):
        continue
    text = data.decode("utf-8", "replace")
    m = re.search(r"/ft_(\d{6,9})\.txt$", path_eff)
    if m:
        ids = {}
        for t, v in ART.findall(text[:20000]):
            ids.setdefault("pmcid" if t in ("pmc", "pmcid") else t, v.strip())
        ft_self.append({"file": path, "slug": slug_of(path), "filed_pmid": m.group(1), "embedded": ids,
                        "is_jats": "<article-id" in text[:20000]})
    if path_eff.endswith(".json"):
        try:
            walk(json.loads(text), path, "")
        except ValueError:
            pass
    elif path_eff.endswith(".jsonl"):
        for i, line in enumerate(text.splitlines()):
            try:
                walk(json.loads(line), path, f"#{i}")
            except ValueError:
                pass
    elif path_eff.endswith((".html", ".md")):
        import html as H
        flat = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", text)))
        for seg in re.split(r"(?<=[.;])\s+(?=[A-Z])", flat):
            from_string(seg, path, "(text)")

json.dump({"commit": COMMIT, "files_read": n_files, "citations": cites, "fulltext_self_ids": ft_self},
          open(OUT / "harvest.json", "w", encoding="utf-8"), ensure_ascii=False)
ids_pm = {x for c in cites for x in c["pmids"]} | {f["filed_pmid"] for f in ft_self}
ids_pc = {x for c in cites for x in c["pmcids"]} | {f["embedded"].get("pmcid") for f in ft_self if f["embedded"].get("pmcid")}
ids_do = {x for c in cites for x in c["dois"]}
print(f"files read {n_files}; citations {len(cites)} (text {sum(c['kind'] == 'text' for c in cites)}, fields "
      f"{sum(c['kind'] == 'fields' for c in cites)}); full-text files {len(ft_self)} (JATS {sum(f['is_jats'] for f in ft_self)}); "
      f"distinct PMIDs {len(ids_pm)}, PMCIDs {len(ids_pc)}, DOIs {len(ids_do)}")
