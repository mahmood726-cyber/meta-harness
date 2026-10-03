"""PMID -> EVERY ClinicalTrials.gov accession the PubMed record itself lists (DataBankList), plus every NCT written in
its abstract. outputs/k_gap/pubmed_ncts.json keeps only ONE NCT per paper (harness.fetch._select_nct picks the first),
which is wrong evidence for a paper that reports SEVERAL trials (CANVAS + CANVAS-R; a pooled RE-COVER/RE-MEDY bleeding
analysis): 'the paper names this registration' must mean 'the paper names ONLY this one among the candidates'.
NCBI E-utilities (a legitimate open source); cached with retrieval time in outputs/k_gap/pubmed_databank_ncts.json.

    python scripts/pubmed_databank_lookup.py PMIDS.json     # PMIDS.json: ["12345678", ...]
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap", "pubmed_databank_ncts.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
UA = {"User-Agent": "meta-harness pubmed_databank_lookup (offline cache builder)"}
NCT = re.compile(r"NCT\d{8}")


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
            if b"<html" in body[:300].lower():
                raise ValueError("HTML error page, not an E-utilities payload")
            return body
        except Exception:  # noqa: BLE001 -- bounded retry, then fail closed
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def parse(xml_bytes):
    out = {}
    for art in ET.fromstring(xml_bytes).iter("PubmedArticle"):
        pmid = art.findtext(".//MedlineCitation/PMID")
        db = []
        for bank in art.iter("DataBank"):
            if (bank.findtext("DataBankName") or "").strip() == "ClinicalTrials.gov":
                db += [a.text.strip().upper() for a in bank.iter("AccessionNumber") if a.text]
        abstract = " ".join("".join(t.itertext()) for t in art.iter("AbstractText"))
        out[pmid] = {"databank": sorted(set(n for n in db if NCT.fullmatch(n))),
                     "abstract": sorted(set(NCT.findall(abstract.upper())))}
    return out


def main(path):
    pmids = sorted({p for p in json.load(open(path, encoding="utf-8")) if str(p).isdigit()})
    cache = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    todo = [p for p in pmids if p not in cache]
    for i in range(0, len(todo), 100):
        chunk = todo[i:i + 100]
        got = parse(get(EUTILS + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"})))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for p in chunk:
            # a PMID PubMed returned no record for is recorded as such, never as 'lists no NCT'
            cache[p] = dict(got[p], retrieved_utc=now) if p in got else {"state": "NO_RECORD_RETURNED",
                                                                           "retrieved_utc": now}
        time.sleep(0.4)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cache, fh, indent=1, sort_keys=True)
    os.replace(tmp, OUT)
    print(f"{len(todo)} fetched, {len(cache)} cached")


if __name__ == "__main__":
    main(sys.argv[1])
