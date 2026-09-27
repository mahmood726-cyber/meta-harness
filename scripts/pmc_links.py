"""Record, per topic, the PubMed->PMC linkset of the comparator PMID (V1.0.1, DOAC-VTE review).

A full text is the comparator's own only when elink returns the SAME-article link 'pubmed_pmc'. When the article is
not in PMC, elink returns only 'pubmed_pmc_refs' (articles that CITE it); before f32c307a the fetcher took the first
PMC link and served a citing article's text under the comparator's PMID. Three caches built before that fix still
hold such text (doac-vte-recurrence, colchicine-recurrent-pericarditis, corticosteroids-cap-mortality).
harness/held_text_identity.py refuses records.json comparator_fulltext unless this record proves an own PMC link.

usage: python scripts/pmc_links.py [slug|all]
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"


def record(slug):
    rp = os.path.join(ROOT, "cache", slug, "records.json")
    pm = str(json.load(open(rp, encoding="utf-8")).get("comparator_pmid") or "")
    if not pm:
        return None
    url = f"{E}?dbfrom=pubmed&db=pmc&id={pm}&retmode=json&tool=meta-harness&email=mahmood726%40gmail.com"
    body = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness"}), timeout=60) as r:
                body = r.read()
            break
        except Exception:  # noqa: BLE001 -- bounded retry; a failure is recorded, never guessed
            time.sleep(2 * (attempt + 1))
    doc = {"schema": "pmc-links-v1", "slug": slug, "pmid": pm, "request": url,
           "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if body is None:
        doc["state"] = "FETCH_FAILED"
    else:
        dbs = (json.loads(body).get("linksets") or [{}])[0].get("linksetdbs") or []
        own = next((ls["links"][0] for ls in dbs if ls.get("linkname") == "pubmed_pmc" and ls.get("links")), None)
        doc.update({"sha256": hashlib.sha256(body).hexdigest(),
                    "linknames": {ls.get("linkname"): len(ls.get("links") or []) for ls in dbs},
                    "own_pmcid": own, "state": "OWN_PMC_LINK" if own else "NO_OWN_PMC_LINK"})
    open(os.path.join(ROOT, "cache", slug, "pmc_links.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, indent=1) + "\n")
    time.sleep(0.4)
    return doc


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    slugs = sorted(d for d in os.listdir(os.path.join(ROOT, "docs", "reviews"))
                   if os.path.exists(os.path.join(ROOT, "docs", "reviews", d, "review.json"))) if target == "all" else [target]
    for s in slugs:
        d = record(s)
        print(s, d and d["state"], d and d.get("own_pmcid"), flush=True)
