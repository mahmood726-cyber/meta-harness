"""SOURCE-IDENTITY CHAIN CENSUS, step 3: compare every harvested citation with NCBI's resolution, and every cited quote with
the held text of the cited PMID. Mismatch kinds:
  PMCID_NAMES_OTHER_PMID   the cited PMCID resolves to a PMID that is not among the PMIDs cited with it
  PMCID_UNRESOLVED         NCBI does not resolve the cited PMCID
  DOI_NOT_PUBMEDS          the cited DOI is not the DOI PubMed records for the cited PMID (PubMed has one)
  FT_SELF_ID_MISMATCH      a held full text's embedded pmid/pmcid/doi disagrees with the PMID it is filed under / PubMed
  QUOTE_NOT_IN_CITED_SOURCE a quoted passage is not in the held text of the cited PMID
  PMID_UNRESOLVED          the cited PMID does not resolve
Pairing inside a text citation that lists several PMIDs: a PMCID/DOI passes if it belongs to ANY PMID in the same string."""
from __future__ import annotations

import gzip
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = "C:/mh-lanes/pva"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/mh-lanes/tmp-pva/idcensus")
COMMIT = sys.argv[2] if len(sys.argv) > 2 else "9eacfe09"
h = json.load(open(OUT / "harvest.json", encoding="utf-8"))
R = json.load(open(OUT / "resolved.json", encoding="utf-8"))
PM, PMC = R["pm"], R["pmc"]


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def normdoi(d):
    d = (d or "").lower().strip().rstrip(".")
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


# held text per PMID: every records.json abstract + fulltext_by_pmid + ft_<pmid>.txt at the commit (tags stripped)
held = defaultdict(list)
ls = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", COMMIT, "--", "cache"], capture_output=True, text=True).stdout.split()
for p in ls:
    if "/snapshots/" in p:
        continue
    if re.fullmatch(r"cache/[^/]+/records\.json", p):
        d = json.loads(subprocess.run(["git", "-C", REPO, "show", f"{COMMIT}:{p}"], capture_output=True, text=True, encoding="utf-8").stdout or "{}")
        for r in d.get("records", []) if isinstance(d, dict) else []:
            if str(r.get("id_type")) == "pmid":
                held[str(r.get("id"))].append(ws(r.get("abstract") or ""))
        for k, v in (d.get("fulltext_by_pmid") or {}).items() if isinstance(d, dict) else []:
            held[str(k)].append(ws(v if isinstance(v, str) else json.dumps(v)))
    m = re.fullmatch(r"cache/[^/]+/ft_(\d+)\.txt", p)
    if m:
        t = subprocess.run(["git", "-C", REPO, "show", f"{COMMIT}:{p}"], capture_output=True, text=True, encoding="utf-8").stdout
        held[m.group(1)].append(ws(re.sub(r"<[^>]+>", " ", t)))


def quote_in_held(q, pmids):
    qn = ws(q).rstrip(".").replace("·", ".")
    for pm in pmids:
        for t in held.get(pm, []):
            if qn in t.replace("·", ".") or qn[:120] in t.replace("·", "."):
                return pm
    return None


rows = []
for c in h["citations"]:
    probs = []
    for pm in c["pmids"]:
        if not (PM.get(pm) or {}).get("title"):
            probs.append(("PMID_UNRESOLVED", pm, None))
    for pc in c["pmcids"]:
        rp = (PMC.get(pc) or {}).get("pmid")
        if not rp:
            probs.append(("PMCID_UNRESOLVED", pc, None))
        elif rp not in c["pmids"]:
            probs.append(("PMCID_NAMES_OTHER_PMID", pc, rp))
    for do in c["dois"]:
        owners = [pm for pm in c["pmids"] if normdoi((PM.get(pm) or {}).get("doi")) == normdoi(do)]
        known = [pm for pm in c["pmids"] if (PM.get(pm) or {}).get("doi")]
        if not owners and known:
            probs.append(("DOI_NOT_PUBMEDS", do, ",".join(f"{pm}:{PM[pm]['doi']}" for pm in known)))
    if c.get("quote"):
        if not quote_in_held(c["quote"], c["pmids"]):
            probs.append(("QUOTE_NOT_IN_CITED_SOURCE", c["quote"][:120], ",".join(c["pmids"])))
    rows.append({**{k: c[k] for k in ("kind", "file", "slug", "jpath", "pmids", "pmcids", "dois")}, "quote": c.get("quote"),
                 "problems": probs})
ft_rows = []
for f in h["fulltext_self_ids"]:
    e, pm = f["embedded"], f["filed_pmid"]
    probs = []
    if e.get("pmid") and e["pmid"] != pm:
        probs.append(("FT_SELF_ID_MISMATCH", f"embedded pmid {e['pmid']}", f"filed {pm}"))
    want = (PM.get(pm) or {}).get("pmcid")
    if e.get("pmcid") and want and e["pmcid"] != want:
        probs.append(("FT_SELF_ID_MISMATCH", f"embedded pmcid {e['pmcid']}", f"PubMed pmcid {want}"))
    if e.get("pmcid") and (PMC.get(e["pmcid"]) or {}).get("pmid") not in (None, pm):
        probs.append(("FT_SELF_ID_MISMATCH", f"embedded pmcid {e['pmcid']} -> PMID {PMC[e['pmcid']]['pmid']}", f"filed {pm}"))
    if e.get("doi") and (PM.get(pm) or {}).get("doi") and normdoi(e["doi"]) != normdoi(PM[pm]["doi"]):
        probs.append(("FT_SELF_ID_MISMATCH", f"embedded doi {e['doi']}", f"PubMed doi {PM[pm]['doi']}"))
    ft_rows.append({**f, "problems": probs})

# distinct asserted pairs with problems
pairs = defaultdict(lambda: {"instances": 0, "files": set(), "slugs": set()})
for r in rows:
    for kind, ident, other in r["problems"]:
        key = (kind, ident, ",".join(r["pmids"]), other)
        pairs[key]["instances"] += 1
        pairs[key]["files"].add(r["file"])
        pairs[key]["slugs"].add(r["slug"])
out = {"commit": COMMIT, "citations": len(rows), "citations_with_problem": sum(1 for r in rows if r["problems"]),
       "by_kind_instances": {}, "distinct": [], "fulltext": ft_rows}
for (kind, ident, pms, other), v in sorted(pairs.items(), key=lambda kv: (-kv[1]["instances"], kv[0])):
    out["by_kind_instances"][kind] = out["by_kind_instances"].get(kind, 0) + v["instances"]
    out["distinct"].append({"kind": kind, "cited": ident, "cited_pmids": pms, "resolves_to": other, "instances": v["instances"],
                            "slugs": sorted(v["slugs"]), "files": sorted(v["files"])[:12]})
json.dump(out, open(OUT / "compare.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
print(f"citations {len(rows)}; with any problem {out['citations_with_problem']}; distinct problem pairs {len(out['distinct'])}")
print("by kind (instances):", out["by_kind_instances"])
print("distinct by kind:", {k: sum(1 for d in out['distinct'] if d['kind'] == k) for k in out['by_kind_instances']})
print("full texts:", len(ft_rows), "with self-id problems:", sum(1 for f in ft_rows if f["problems"]))
