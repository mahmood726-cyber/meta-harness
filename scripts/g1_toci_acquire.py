"""G1 tocilizumab: acquire each REACT trial's OWN report where we hold none (network: NCBI E-utilities + Europe PMC REST,
no paywall or bot check is touched). Writes g1/data/acquired/<pmid>.json per paper:
  {pmid, query, title, abstract, pmcid, license, fulltext (only under an open licence), fulltext_sha256, retrieved_utc}
A non-open full text is never stored; its PMCID and body sha256 are recorded (VERIFIED_NOT_HELD).

  python scripts/g1_toci_acquire.py
"""
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from g1 import tocilizumab as g  # noqa: E402

OUT = os.path.join(ROOT, "g1", "data", "acquired")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
OPEN = re.compile(r"^cc[ -]?by|^cc0|public domain", re.I)

# the trial's own report is searched by its REGISTRATION (secondary-id field), or by its name for one not in AACT
QUERIES = {
    "COV-AID": "NCT04330638[si]", "HMO-020-0224": "NCT04377750[si]", "COVIDSTORM": "NCT04577534[si]",
    "COVITOZ": "NCT04435717[si]", "TOCOVID": "NCT04332094[si]", "ARCHITECTS": "NCT04412772[si]",
    "COVIDOSE2-SS-A": "NCT04479358[si]", "REMAP-CAP": "NCT02735707[si] AND (tocilizumab OR interleukin-6)",
    "PreToVid": "PreToVid[tiab]", "COVINTOC": "COVINTOC[tiab]",
}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness-g1/1.0"}),
                                        timeout=60) as r:
                return r.read()
        except Exception as exc:                     # noqa: BLE001 -- recorded and retried, then raised
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def main():
    os.makedirs(OUT, exist_ok=True)
    log = []
    for label, q in QUERIES.items():
        ids = json.loads(get(f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax=10&term={urllib.parse.quote(q)}"))
        pmids = ids.get("esearchresult", {}).get("idlist", [])
        log.append({"label": label, "query": q, "pmids": pmids})
        for pmid in pmids:
            res = json.loads(get(f"{EPMC}/search?query=EXT_ID:{pmid}%20AND%20SRC:MED&resultType=core&format=json"))
            hits = (res.get("resultList") or {}).get("result") or []
            if not hits:
                continue
            h = hits[0]
            rec = {"pmid": pmid, "label_query": label, "query": q, "title": h.get("title"),
                   "abstract": h.get("abstractText") or "", "pmcid": h.get("pmcid"), "license": h.get("license"),
                   "is_open_access": h.get("isOpenAccess"), "pub_types": (h.get("pubTypeList") or {}).get("pubType"),
                   "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            if rec["pmcid"] and h.get("isOpenAccess") == "Y":
                try:
                    xml = get(f"{EPMC}/{rec['pmcid']}/fullTextXML")
                    rec["fulltext_sha256"] = hashlib.sha256(xml).hexdigest()
                    if OPEN.search(rec["license"] or ""):
                        rec["fulltext"] = xml.decode("utf-8", "replace")
                    else:
                        rec["fulltext_state"] = "VERIFIED_NOT_HELD (licence not open)"
                except Exception as exc:              # noqa: BLE001
                    rec["fulltext_state"] = f"FETCH_FAILED: {type(exc).__name__}"
            open(os.path.join(OUT, f"{pmid}.json"), "w", encoding="utf-8", newline="\n").write(
                json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
            time.sleep(0.4)
        time.sleep(0.4)
    open(os.path.join(OUT, "_queries.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(log, indent=1) + "\n")
    for x in log:
        print(x["label"], x["query"], "->", x["pmids"])


if __name__ == "__main__":
    main()
