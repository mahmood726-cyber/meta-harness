"""SOURCE-IDENTITY CHAIN CENSUS, step 2: resolve every harvested PMID and PMCID with NCBI (ID converter + E-utilities
esummary). Raw responses kept gzipped with sha256 and UTC time; a non-JSON or error payload is never accepted."""
from __future__ import annotations

import datetime
import gzip
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/mh-lanes/tmp-pva/idcensus")
RAW = OUT / "raw"
RAW.mkdir(exist_ok=True)
h = json.load(open(OUT / "harvest.json", encoding="utf-8"))
pmids = sorted({x for c in h["citations"] for x in c["pmids"]} | {f["filed_pmid"] for f in h["fulltext_self_ids"]}
               | {f["embedded"].get("pmid") for f in h["fulltext_self_ids"] if f["embedded"].get("pmid")})
pmcids = sorted({x for c in h["citations"] for x in c["pmcids"]}
                | {f["embedded"]["pmcid"] for f in h["fulltext_self_ids"] if f["embedded"].get("pmcid")})
ledger = []
TOOL = {"tool": "meta-harness-pva-idcensus", "email": "meta-harness@example.org"}


def get(url, name):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                body = r.read()
            d = json.loads(body)
            if isinstance(d, dict) and (d.get("status") == "error" or "error" in d and not d.get("result") and not d.get("records")):
                raise ValueError(f"error payload: {str(d)[:200]}")
            (RAW / (name + ".json.gz")).write_bytes(gzip.compress(body))
            ledger.append({"file": name + ".json.gz", "url": url, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
                           "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
            time.sleep(0.4)
            return d
        except Exception as e:  # noqa: BLE001 -- bounded retry; an error or non-JSON body is never accepted
            if attempt == 4:
                raise SystemExit(f"REFUSED: {name}: {e}")
            time.sleep(3 * (attempt + 1))


# 1) PubMed esummary for every PMID: title, DOI, PMCID as PubMed records them
pm_meta = {}
for i in range(0, len(pmids), 180):
    b = pmids[i:i + 180]
    d = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" +
            urllib.parse.urlencode({"db": "pubmed", "id": ",".join(b), "retmode": "json", **TOOL}), f"esum_pubmed_{i // 180:03d}")
    for u in d.get("result", {}).get("uids", []):
        r = d["result"][u]
        ids = {a.get("idtype"): a.get("value") for a in r.get("articleids", [])}
        pm_meta[u] = {"title": r.get("title"), "source": r.get("source"), "pubdate": r.get("pubdate"),
                      "doi": (ids.get("doi") or "").lower() or None, "pmcid": ids.get("pmc") or None,
                      "error": r.get("error")}
# 2) NCBI ID converter for every PMCID: which PMID/DOI it names
pmc_meta = {}
for i in range(0, len(pmcids), 180):
    b = pmcids[i:i + 180]
    d = get("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?" +
            urllib.parse.urlencode({"ids": ",".join(b), "format": "json", **TOOL}), f"idconv_{i // 180:03d}")
    for rec in d.get("records", []):
        pmc_meta[rec.get("pmcid") or rec.get("requested-id")] = {"pmid": str(rec["pmid"]) if rec.get("pmid") else None, "doi": (rec.get("doi") or "").lower() or None,
                                                                 "status": rec.get("status"), "errmsg": rec.get("errmsg")}
# 3) titles for PMIDs that a PMCID resolves to but that were not cited (so a wrong PMCID can be named)
extra = sorted({v["pmid"] for v in pmc_meta.values() if v.get("pmid") and v["pmid"] not in pm_meta})
for i in range(0, len(extra), 180):
    b = extra[i:i + 180]
    d = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" +
            urllib.parse.urlencode({"db": "pubmed", "id": ",".join(b), "retmode": "json", **TOOL}), f"esum_extra_{i // 180:03d}")
    for u in d.get("result", {}).get("uids", []):
        r = d["result"][u]
        ids = {a.get("idtype"): a.get("value") for a in r.get("articleids", [])}
        pm_meta[u] = {"title": r.get("title"), "source": r.get("source"), "pubdate": r.get("pubdate"),
                      "doi": (ids.get("doi") or "").lower() or None, "pmcid": ids.get("pmc") or None, "error": r.get("error")}
json.dump({"pm": pm_meta, "pmc": pmc_meta, "ledger": ledger}, open(OUT / "resolved.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"PMIDs resolved {sum(1 for v in pm_meta.values() if v.get('title'))} of {len(pmids)} cited (+{len(extra)} reached via PMCIDs); "
      f"PMCIDs resolved {sum(1 for v in pmc_meta.values() if v.get('pmid'))} of {len(pmcids)}; raw responses {len(ledger)}")
print("control PMC9761906 ->", pmc_meta.get("PMC9761906"), "|", (pm_meta.get((pmc_meta.get("PMC9761906") or {}).get("pmid") or "") or {}).get("title"))
