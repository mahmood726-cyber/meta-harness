"""Recorded identity searches. Expected PMIDs are comparison targets, never queries.

Hardcode disclosure: static = requested audit targets, supported acronym syntax, and route order;
dynamic = held labels/references/acronyms, registry IDs, and search results.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
CT = "https://clinicaltrials.gov/api/v2/studies"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = "meta-harness k-gap (meta-harness@example.org)"
TARGETS = {"esketamine-trd-madrs": ["31109201"],
           "omega3-cardiovascular-events": ["21115589", "38199870"],
           "semaglutide-obesity-weight": ["33625476", "33567185"]}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verdict(pmids, expected):
    ids = sorted(set(pmids))
    return "NOT_FOUND" if not ids else "AMBIGUOUS" if len(ids) > 1 else "FOUND_SAME" if ids[0] == expected else "FOUND_DIFFERENT"


def found_pmids(slug, root=ROOT):
    p = Path(root) / "registry/identity_searches" / f"{slug}.json"
    if not p.exists():
        return set()
    d = read(p)
    if d.get("slug") != slug:
        return set()
    return {str(e["pmid"]) for e in d.get("entries", [])
            if e.get("verdict") == "FOUND_SAME" and e.get("result_pmids") == [str(e.get("pmid"))]
            and str(e.get("pmid", "")).isdigit() and e.get("requests") and not e.get("error")}


class Http:
    def __init__(self):
        self.requests = []
        self.last = 0.

    def get(self, url, params=None):
        params = dict(params or {})
        if url.startswith(EUTILS):
            params.update(tool="meta-harness", email="meta-harness@example.org")
        url += ("?" + urllib.parse.urlencode(params)) if params else ""
        time.sleep(max(0, .35 - (time.monotonic() - self.last)))
        self.last = time.monotonic()
        row = {"url": url, "when_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45) as response:
                raw = response.read()
                row["status"] = response.status
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            row.update(status=exc.code, error=str(exc))
        except (OSError, TimeoutError) as exc:
            row.update(response_sha256=None, error=str(exc))
            self.requests.append(row)
            raise
        row["response_sha256"] = hashlib.sha256(raw).hexdigest()
        self.requests.append(row)
        if "error" in row:
            raise RuntimeError(row["error"])
        return raw


def reference_matches(xml, label):
    """Parse only reference-list sections, never body or table citations."""
    sections = re.findall(r"<ref-list\b[^>]*>.*?</ref-list>", xml, re.S)
    refs = [r for section in sections for r in ET.fromstring(
        '<root xmlns:xlink="http://www.w3.org/1999/xlink">' + section + '</root>').findall(".//ref")]
    author = re.match(r"[A-Za-z-]+", label)
    year = re.search(r"\b(?:19|20)\d{2}\b", label)
    number = re.search(r"\[(\d+)\]", label)
    if author and year:
        return [r for r in refs if re.search(r"\b" + re.escape(author[0]) + r"\b", " ".join(r.itertext()), re.I)
                and year[0] in " ".join(r.itertext())]
    return [r for r in refs if number and re.sub(r"\D", "", r.findtext("label", "")) == number[1]]


def r1(http, acronyms, ncts=()):
    studies = {}
    for nct in sorted(set(ncts)):
        studies[nct] = json.loads(http.get(CT + "/" + nct))
    for acronym in sorted(set(acronyms)):
        d = json.loads(http.get(CT, {"query.term": 'AREA[Acronym]"' + acronym + '"', "pageSize": 100, "format": "json"}))
        if d.get("nextPageToken"):
            raise ValueError("Registry search truncated")
        for s in d.get("studies", []):
            ident = s["protocolSection"]["identificationModule"]
            normalize = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
            if normalize(ident.get("acronym", "")) == normalize(acronym):
                studies[ident["nctId"]] = s
    candidates = set()
    for nct, s in sorted(studies.items()):
        result = json.loads(http.get(EUTILS + "esearch.fcgi", {"db": "pubmed", "term": nct + "[si]", "retmode": "json", "retmax": 10000}))["esearchresult"]
        if int(result.get("count", len(result["idlist"]))) > len(result["idlist"]):
            raise ValueError("PubMed search truncated")
        candidates.update(result["idlist"])
        refs = s.get("protocolSection", {}).get("referencesModule", {}).get("references", [])
        refs += s.get("derivedSection", {}).get("miscInfoModule", {}).get("derivedReferences", [])
        candidates.update(str(r["pmid"]) for r in refs if r.get("pmid") and r.get("type", "").upper() in {"RESULT", "RESULTS", "DERIVED"})
    if not candidates:
        return []
    xml = ET.fromstring(http.get(EUTILS + "efetch.fcgi", {"db": "pubmed", "id": ",".join(sorted(candidates)), "retmode": "xml"}))
    names = list(studies) + list(acronyms)
    found = []
    for article in xml.findall(".//PubmedArticle"):
        text = " ".join(" ".join(e.itertext()) for e in article.findall(".//ArticleTitle") + article.findall(".//Abstract"))
        if any(re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", text, re.I) for n in names):
            found.append(article.findtext(".//MedlineCitation/PMID"))
    return sorted(set(found))


def r2(http, refs):
    ids = set()
    for ref in refs:
        doi = ref.findtext(".//pub-id[@pub-id-type='doi']")
        if not doi:
            link = ref.find(".//ext-link[@ext-link-type='doi']")
            doi = link.get("{http://www.w3.org/1999/xlink}href") if link is not None else None
        title = ref.findtext(".//article-title")
        if not doi and not title:
            continue
        query = 'DOI:"' + doi + '"' if doi else 'TITLE:"' + title.replace('"', '') + '"'
        d = json.loads(http.get(EPMC, {"query": query + " AND SRC:MED", "format": "json", "pageSize": 1000}))
        results = d.get("resultList", {}).get("result", [])
        if int(d.get("hitCount", len(results))) > len(results):
            raise ValueError("Citation search truncated")
        ids.update(str(r["id"]) for r in results if r.get("source") == "MED")
    return sorted(ids)


def search_identity(http, label, expected, acronyms, ncts, refs, evidence):
    entries = []
    for route, search in [("R1", lambda: r1(http, acronyms, ncts)), ("R2", lambda: r2(http, refs))]:
        start = len(http.requests)
        entry = dict(label=label, pmid=expected, route=route, evidence=evidence)
        try:
            ids = search()
        except (OSError, RuntimeError, ValueError, KeyError, ET.ParseError) as exc:
            ids = []
            entry["error"] = str(exc)
        entry.update(requests=http.requests[start:], result_pmids=ids, verdict=verdict(ids, expected))
        entries.append(entry)
        if entry["verdict"] == "FOUND_SAME":
            break
    return entries


def retire_extras(path, found):
    """Replace only the array span; preserve all other bytes and original newlines."""
    raw = path.read_bytes().decode("utf-8")
    match = re.search(r'"extra_pmids"\s*:\s*(\[[^]]*\])', raw)
    if not match:
        return []
    old = json.loads(match[1]); removed = [p for p in old if str(p) in found]
    if removed:
        new = [p for p in old if str(p) not in found]
        newline = "\r\n" if "\r\n" in match[1] else "\n"
        value = json.dumps(new, indent=2).replace("\n", newline + "  ")
        path.write_bytes((raw[:match.start(1)] + value + raw[match.end(1):]).encode("utf-8"))
    return removed


def run(root=ROOT):
    http = Http()
    for slug, pmids in TARGETS.items():
        topic = read(root / "topics" / f"{slug}.json")
        tracker = read(root / "outputs/k_gap/g1" / f"{slug}.json")
        records = read(root / "cache" / slug / "records.json")["records"]
        sources = sorted((root / "cache/comparators" / topic["comparator_pmid"]).glob("*_kgap_jats.xml"))
        source = sources[-1] if sources else None
        xml = source.read_text(encoding="utf-8") if source else ""
        entries = []
        for pmid in pmids:
            rows = [t for t in tracker["trials"] if t.get("family") == "PMID " + pmid]
            label = rows[0]["label"] if rows else "PMID " + pmid + " (ours_not_in_comparator; no tracker trial label)"
            refs = reference_matches(xml, label)
            rec = next((r for r in records if str(r.get("id")) == pmid), {})
            context = label + " " + rec.get("title", "") + " " + " ".join(" ".join(r.itertext()) for r in refs)
            acronyms = re.findall(r"\b(?:TRANSFORM-\d+|STEP [1-9]\d*|DO-HEALTH)\b", context)
            ncts = re.findall(r"NCT\d{8}", json.dumps(rows))
            evidence = {"tracker": f"outputs/k_gap/g1/{slug}.json", "acronym_source": f"cache/{slug}/records.json",
                        "acronym_source_sha256": hashlib.sha256((root / "cache" / slug / "records.json").read_bytes()).hexdigest(),
                        "acronym_title_span": rec.get("title", ""),
                        "acronyms": sorted(set(acronyms)), "ncts_from_tracker": sorted(set(ncts)),
                        "reference_source": source.relative_to(root).as_posix() if source else None,
                        "reference_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest() if source else None,
                        "matched_references": [ET.tostring(r, encoding="unicode") for r in refs]}
            attempts = search_identity(http, label, pmid, acronyms, ncts, refs, evidence)
            entries.extend(attempts)
            print(slug, pmid, label, "; ".join(e["route"] + " " + e["verdict"] + " " + str(e["result_pmids"]) for e in attempts), flush=True)
        dest = root / "registry/identity_searches" / f"{slug}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({"slug": slug, "entries": entries}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print("Removed extra_pmids:", retire_extras(root / "topics" / f"{slug}.json", found_pmids(slug, root)), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run"])
    parser.parse_args()
    run()
