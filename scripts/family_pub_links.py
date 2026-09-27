"""Link a REGISTRY-ONLY trial family to its publication when no search route finds it (V1.0.1, finerenone review).

ARTS-DN Japan (NCT01968668) sat in the ledger as a registry record only. Its report -- Katayama et al., J Diabetes
Complications 2017, PMID 28025025 -- is not indexed under the NCT ([si]) and Europe PMC's full-text search returns only
papers that mention it. The link is therefore RECORDED, with its binding evidence: a token (here the trial acronym
'ARTS-DN Japan') that the held registry record's title and the held publication both print. The publication's PubMed
record is held (request, time, response sha256) and enters the build as a report of that family.

usage: python scripts/family_pub_links.py <slug> <NCT> <PMID> "<binding token>" "<reported by>"
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def main(slug, nct, pmid, token, reported_by):
    url = f"{E}?db=pubmed&id={pmid}&retmode=xml&tool=meta-harness&email=meta-harness%40example.org"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness"}), timeout=60) as r:
        body = r.read()
    art = ET.fromstring(body).find(".//PubmedArticle")
    title = "".join(art.find(".//ArticleTitle").itertext()).strip()
    abstract = " ".join("".join(a.itertext()).strip() for a in art.findall(".//Abstract/AbstractText"))
    collective = [c.text for c in art.findall(".//AuthorList/Author/CollectiveName") if c.text]
    doi = next((x.text for x in art.findall(".//ArticleIdList/ArticleId") if x.get("IdType") == "doi"), None)
    year = (art.find(".//PubDate/Year").text if art.find(".//PubDate/Year") is not None else None)
    pubtypes = [p.text for p in art.findall(".//PublicationTypeList/PublicationType")]
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    reg = next(r for v in recs.values() if isinstance(v, list) for r in v if isinstance(r, dict) and str(r.get("id")) == nct)
    paper_text = " ".join([title, abstract, *collective])
    if token not in str(reg.get("title") or "") or token not in paper_text:
        raise SystemExit(f"REFUSED: binding token {token!r} not printed by both the registry record and the paper")
    link = {"nct": nct, "pmid": pmid, "binding_token": token,
            "registry_quote": {"document_ref": f"cache/{slug}/records.json", "record_id": nct, "field": "title",
                               "quote": reg["title"]},
            "paper_quote": next(q for q in collective + [title, abstract] if token in q),
            "reported_by": reported_by,
            "request": url, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "response_sha256": hashlib.sha256(body).hexdigest(),
            "record": {"id": pmid, "id_type": "pmid", "title": title, "abstract": abstract, "year": year,
                       "doi": doi, "pubtypes": pubtypes, "nct": nct, "collective_authors": collective,
                       "retrieved_via": "family_pub_links (recorded link; no search route indexes it)"}}
    p = os.path.join(ROOT, "cache", slug, "family_pub_links.json")
    doc = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"schema": "family-pub-links-v1", "slug": slug, "links": []}
    doc["links"] = [x for x in doc["links"] if x["nct"] != nct] + [link]
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("LINKED", nct, "->", pmid, "|", title[:90], "| token in paper:", link["paper_quote"][:60])


if __name__ == "__main__":
    main(*sys.argv[1:6])
