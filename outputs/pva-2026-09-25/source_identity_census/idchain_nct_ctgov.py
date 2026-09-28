"""For family links PubMed cannot confirm (the report's PubMed record names no NCT), ask the registry: does ClinicalTrials.gov's
record for the family's NCT list the report PMID among its references? Raw responses kept gzipped with sha256 and UTC time.
  CTGOV_LISTS_PMID   the registry links this report to the NCT            -> confirmed
  CTGOV_NOT_LISTED   the registry's references do not include the PMID    -> reported with titles, for a person to judge"""
import datetime
import gzip
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path("C:/mh-lanes/tmp-pva/idcensus")
RAW = D / "raw_ctgov"
RAW.mkdir(exist_ok=True)
rows = [r for r in json.load(open(D / "nct_families.json")) if r["class"] == "NCT_UNSTATED"]
PM = json.load(open(D / "resolved.json", encoding="utf-8"))["pm"]
ledger, out = [], []
for r in rows:
    nct = r["family_registry_ids"][0]
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct}?fields=NCTId,BriefTitle,Acronym,ReferencesModule"
    body = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                body = resp.read()
            json.loads(body)
            break
        except Exception as e:  # noqa: BLE001 -- bounded retry; a non-JSON body is never accepted
            body = None
            time.sleep(3 * (attempt + 1))
    if body is None:
        out.append({**r, "ctgov": "UNREACHABLE"})
        continue
    (RAW / f"{nct}.json.gz").write_bytes(gzip.compress(body))
    ledger.append({"nct": nct, "url": url, "sha256": hashlib.sha256(body).hexdigest(),
                   "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
    d = json.loads(body)
    ps = d.get("protocolSection", {})
    title = ps.get("identificationModule", {}).get("briefTitle")
    refs = [str(x.get("pmid")) for x in ps.get("referencesModule", {}).get("references", []) if x.get("pmid")]
    cls = "CTGOV_LISTS_PMID" if r["report_pmid"] in refs else "CTGOV_NOT_LISTED"
    out.append({**r, "ctgov": cls, "ctgov_title": title, "ctgov_ref_pmids": refs,
                "report_title": (PM.get(r["report_pmid"]) or {}).get("title")})
    time.sleep(0.4)
json.dump({"rows": out, "ledger": ledger}, open(D / "nct_ctgov.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for o in out:
    print(f"{o['ctgov']:17} {o['slug'][:28]:28} {o['family_registry_ids'][0]} = {str(o.get('ctgov_title'))[:60]:60} | report {o['report_pmid']}: {str(o.get('report_title'))[:70]}")
