"""PubMed COLLECTIVE-AUTHOR names ('Eplerenone Post-Acute Myocardial Infarction Heart Failure Efficacy and Survival
Study Investigators') for the PMIDs of comparator references, via NCBI E-utilities efetch (a legitimate open source).
A trial's long form often appears ONLY there, never in the title or abstract. Cached with retrieval time in
outputs/k_gap/pubmed_collective.json; the identity chain reads the cache offline.

    python scripts/pubmed_collective_lookup.py PMID [PMID ...]
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap", "pubmed_collective.json")
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"


def fetch(pmids):
    url = EFETCH + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness collective lookup"}),
                                timeout=60) as r:
        body = r.read()
    if b"<PubmedArticleSet" not in body[:2000]:
        raise ValueError("not a PubMed efetch payload")       # an error page is never data
    root = ET.fromstring(body)
    out = {}
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//MedlineCitation/PMID")
        out[pmid] = sorted({"".join(c.itertext()).strip() for c in art.iter("CollectiveName")
                            if "".join(c.itertext()).strip()})
    return out


def main(pmids):
    cache = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    todo = sorted({p for p in pmids if p.isdigit() and p not in cache})
    for i in range(0, len(todo), 100):
        chunk = todo[i:i + 100]
        got = fetch(chunk)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for p in chunk:
            if p not in got:
                raise ValueError(f"PMID {p} missing from the efetch payload")   # fail closed, never record a gap as []
            cache[p] = {"collective": got[p], "retrieved_utc": stamp}
        time.sleep(0.4)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cache, fh, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, OUT)
    print(len(todo), "fetched;", sum(1 for v in cache.values() if v["collective"]), "of", len(cache), "carry a name")


if __name__ == "__main__":
    main(sys.argv[1:])
