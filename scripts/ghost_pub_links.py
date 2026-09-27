"""Resolve registry IDs against PUBLICATIONS before anything is labelled results-only or ghost (V1.0.1, denosumab review).

scripts/ghost_census.py links an NCT to its paper only through AACT study_references of type RESULT/DERIVED. A trial
whose paper is not linked there (Koh 2016, PMID 27189284, reports NCT01457950) was labelled results_only. For every
NCT in cache/<slug>/ghost.json results_only_ncts / ghost_ncts this script holds the publications that name it:
  - held records of the topic whose nct field or abstract carries the NCT, and
  - PubMed secondary-identifier search '<NCT>[si]', each hit fetched (title, year, publication types),
  - Europe PMC search for the quoted NCT (full text and text-mined accessions; PubMed [si] missed Koh 2016),
with the request URL, time and response sha256, in cache/<slug>/ghost_pub_links.json. harness/pipeline._load_ghost
applies it; the census's own counts are kept beside the resolved ones.

usage: python scripts/ghost_pub_links.py [slug|all]
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = "tool=meta-harness&email=mahmood726%40gmail.com"
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "meta-harness (mailto:mahmood726@gmail.com)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            time.sleep(0.4)
            return body
        except Exception:  # noqa: BLE001 -- bounded retry, then the failure is recorded, never guessed
            time.sleep(2 * (attempt + 1))
    return None


def resolve(slug):
    g = json.load(open(os.path.join(ROOT, "cache", slug, "ghost.json"), encoding="utf-8"))
    ncts = sorted(set(g.get("results_only_ncts") or []) | set(g.get("ghost_ncts") or []))
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    held = [r for v in recs.values() if isinstance(v, list) for r in v if isinstance(r, dict) and r.get("id_type") != "nct"]
    out = {}
    for n in ncts:
        local = [{"pmid": str(r["id"]), "title": r.get("title"), "year": r.get("year"), "pubtypes": r.get("pubtypes"),
                  "source": "held topic record (nct field)" if r.get("nct") == n else "held topic record (abstract)"}
                 for r in held if r.get("nct") == n or n in str(r.get("abstract") or "")]
        url = f"{E}esearch.fcgi?db=pubmed&retmode=json&retmax=20&{TOOL}&term={n}%5Bsi%5D"
        body = _get(url)
        entry = {"held_records": local}
        if body is None:
            entry["pubmed_si"] = {"state": "FETCH_FAILED", "request": url}
        else:
            ids = json.loads(body).get("esearchresult", {}).get("idlist", [])
            hits = []
            if ids:
                sb = _get(f"{E}esummary.fcgi?db=pubmed&retmode=json&{TOOL}&id={','.join(ids)}")
                res = json.loads(sb).get("result", {}) if sb else {}
                for i in ids:
                    x = res.get(i) or {}
                    hits.append({"pmid": i, "title": x.get("title"), "year": str(x.get("pubdate") or "")[:4],
                                 "pubtypes": x.get("pubtype")})
            entry["pubmed_si"] = {"request": url, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                  "sha256": hashlib.sha256(body).hexdigest(), "hits": hits}
        # Europe PMC searches full text and text-mined accession numbers: Koh 2016 (PMID 27189284) names
        # NCT01457950 in its text but PubMed does not index it under [si]
        eu = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22{n}%22&format=json&resultType=lite&pageSize=25"
        eb = _get(eu)
        if eb is None:
            entry["europepmc"] = {"state": "FETCH_FAILED", "request": eu}
        else:
            res = json.loads(eb).get("resultList", {}).get("result", [])
            entry["europepmc"] = {"request": eu, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                  "sha256": hashlib.sha256(eb).hexdigest(),
                                  "hits": [{"pmid": x.get("pmid"), "title": x.get("title"), "year": x.get("pubYear"),
                                            "pubtypes": [t.strip() for t in str(x.get("pubType") or "").split(";") if t.strip()]}
                                           for x in res if x.get("pmid")]}
        out[n] = entry
    doc = {"schema": "ghost-pub-links-v1", "slug": slug, "census_source": g.get("source"), "ncts": out}
    p = os.path.join(ROOT, "cache", slug, "ghost_pub_links.json")
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    linked = sum(1 for e in out.values() if e["held_records"] or (e.get("pubmed_si") or {}).get("hits")
                 or (e.get("europepmc") or {}).get("hits"))
    return len(ncts), linked


def add_registry_titles(slugs):
    """Registry titles of every target NCT, from the local AACT snapshot (studies.brief_title / official_title): a
    Europe PMC full-text hit is accepted only when its title matches the trial's registry title
    (harness/pipeline._load_ghost), because full text can merely CITE a trial."""
    sys.path.insert(0, ROOT)
    from harness import aact
    docs = {s: json.load(open(os.path.join(ROOT, "cache", s, "ghost_pub_links.json"), encoding="utf-8")) for s in slugs}
    want = {n for d in docs.values() for n in d["ncts"]}
    titles = {}
    for r in aact._iter_rows(aact._table("studies")):
        n = (r.get("nct_id") or "").upper()
        if n in want:
            titles[n] = [t for t in (r.get("brief_title"), r.get("official_title")) if t]
    for s, d in docs.items():
        d["registry_titles_source"] = f"AACT {os.path.basename(aact.snapshot_dir())} studies.brief_title/official_title"
        for n, e in d["ncts"].items():
            e["registry_titles"] = titles.get(n) or []
        open(os.path.join(ROOT, "cache", s, "ghost_pub_links.json"), "w", encoding="utf-8", newline="\n").write(
            json.dumps(d, indent=1, ensure_ascii=False) + "\n")
        print(s, sum(1 for e in d["ncts"].values() if e["registry_titles"]), "of", len(d["ncts"]), "titled", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--titles"]:
        add_registry_titles(sorted(os.path.basename(os.path.dirname(p)) for p in
                                   __import__("glob").glob(os.path.join(ROOT, "cache", "*", "ghost_pub_links.json"))))
        sys.exit(0)
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    slugs = sorted(os.path.basename(os.path.dirname(p)) for p in __import__("glob").glob(os.path.join(ROOT, "cache", "*", "ghost.json"))) \
        if target == "all" else [target]
    for s in slugs:
        if os.path.exists(os.path.join(ROOT, "docs", "reviews", s, "review.json")):
            print(s, *resolve(s), flush=True)
