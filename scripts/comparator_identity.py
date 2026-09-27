"""Hold the RESOLVED identity of each topic's registered comparator (V1.0.1): what its PMID and DOI actually point to.

For every topic with a `comparator_pmid`, fetch once and hold under cache/<slug>/comparator_identity.json:
  - PubMed esummary for the PMID (authors, title, journal, year, the DOI PubMed records), and
  - Crossref for the DOI (authors, title, container), when a DOI is known,
each with its request URL, UTC time and the sha256 of the response bytes. harness/comparator_identity.py then
compares the protocol's NAMED comparator (first author, title) with this metadata offline, and flags
COMPARATOR_IDENTITY_MISMATCH. Fetches are logged; nothing else is fetched.

usage: python scripts/comparator_identity.py [slug|all] [--refresh]
"""
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "meta-harness comparator-identity (mailto:mahmood726@gmail.com)"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
        return r.status, body


def _held(url):
    status, body = _get(url)
    time.sleep(0.4)
    return {"url": url, "status": status, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sha256": hashlib.sha256(body).hexdigest(), "body": json.loads(body.decode("utf-8"))}


def build(slug, refresh=False):
    cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    pmid = str(cfg.get("comparator_pmid") or "")
    if not pmid:
        return None
    out = ROOT / "cache" / slug / "comparator_identity.json"
    if out.exists() and not refresh:
        return "HELD"
    pm = _held("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&tool=meta-harness"
               f"&email=mahmood726%40gmail.com&id={pmid}")
    res = (pm["body"].get("result") or {}).get(pmid) or {}
    doi = next((x["value"] for x in res.get("articleids") or [] if x.get("idtype") == "doi"), None)
    cr = None
    if doi:
        try:
            cr = _held("https://api.crossref.org/works/" + doi)
            msg = cr["body"].get("message") or {}
            cr["body"] = {"message": {k: msg.get(k) for k in ("DOI", "title", "author", "container-title", "issued",
                                                                 "license", "reference-count")}}
        except Exception as exc:  # noqa: BLE001 -- a failed Crossref fetch is recorded, never guessed
            cr = {"state": "FETCH_FAILED", "error": str(exc)[:200]}
    pm["body"] = {"result": {pmid: {k: res.get(k) for k in ("uid", "title", "authors", "source", "pubdate",
                                                            "articleids", "fulljournalname")}}}
    doc = {"schema": "comparator-identity-v1", "slug": slug, "comparator_pmid": pmid,
           "note": "fetched once; response sha256 is of the full response bytes, body trimmed to identity fields",
           "pubmed": pm, "crossref": cr}
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return "WRITTEN"


def main(argv):
    target = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else "all"
    slugs = sorted(p.stem for p in (ROOT / "topics").glob("*.json")) if target == "all" else [target]
    for s in slugs:
        if (ROOT / "docs" / "reviews" / s / "review.json").exists():
            print(s, build(s, "--refresh" in argv), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
