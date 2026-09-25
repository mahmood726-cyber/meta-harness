"""Discovery search for the GLP-1 RA / 3-point MACE review (STRATEGY.md). Registered by the commit that adds it; run
AFTER that commit. Retains every record; logs every request (URL, UTC time, status, bytes, sha256); raw bodies are held
LOCAL-ONLY (outside the repo) and only their hashes are committed. A failed fetch is FETCH_FAILED, never a zero.
usage: search.py <held_dir> <out_dir>"""
import gzip, hashlib, json, os, re, sys, time, urllib.parse
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from harness import http  # noqa: E402  (the pipeline's retrying fetcher)
from harness.fetch import _txt, _select_nct, _NCT_RE  # noqa: E402  (the pipeline's PubMed parsing helpers)
from harness.search_v2 import _ctgov_record  # noqa: E402  (the pipeline's registry record shape)

# ---------------------------------------------------------------- the registered queries (STRATEGY.md)
DRUGS = ["exenatide", "liraglutide", "lixisenatide", "dulaglutide", "albiglutide", "semaglutide", "efpeglenatide",
         "taspoglutide", "beinaglutide", "loxenatide", "tirzepatide", "orforglipron", "danuglipron", "retatrutide",
         "survodutide", "cotadutide", "mazdutide", "efinopegdutide", "ecnoglutide", "supaglutide"]
I_PUBMED = ('("Glucagon-Like Peptide-1 Receptor Agonists"[MeSH] OR "Glucagon-Like Peptide-1 Receptor"[MeSH] OR '
            '"Glucagon-Like Peptide 1"[MeSH] OR "GLP-1"[tiab] OR GLP1[tiab] OR "GLP-1RA"[tiab] OR '
            '"glucagon-like peptide-1"[tiab] OR "glucagon like peptide 1"[tiab] OR "glucagon-like peptide 1"[tiab] OR '
            + " OR ".join(f"{d}[tiab]" for d in DRUGS) + ")")
O_PUBMED = ('("Cardiovascular Diseases"[MeSH] OR cardiovascular[tiab] OR MACE[tiab] OR "major adverse cardiac"[tiab] OR '
            '"major adverse cardiovascular"[tiab] OR "myocardial infarction"[tiab] OR stroke[tiab] OR "cardiac death"[tiab])')
P_PUBMED = ('("Diabetes Mellitus, Type 2"[MeSH] OR "type 2 diabetes"[tiab] OR "type II diabetes"[tiab] OR T2D[tiab] OR '
            'T2DM[tiab] OR "non-insulin-dependent"[tiab] OR "diabetes mellitus"[tiab])')
# Cochrane Highly Sensitive Search Strategy, sensitivity-maximising version (2008 revision), PubMed format
RCT_PUBMED = ('(randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR placebo[tiab] OR '
              'drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])')
PUBMED_QUERY = f"{I_PUBMED} AND {O_PUBMED} AND {P_PUBMED} AND {RCT_PUBMED}"

CTGOV_PARAMS = {
    "query.cond": "type 2 diabetes",
    "query.intr": " OR ".join(['"GLP-1"', '"glucagon-like peptide-1"', '"GLP-1 receptor agonist"'] + DRUGS),
    "query.outc": 'cardiovascular OR MACE OR "myocardial infarction" OR stroke',
    "query.term": "AREA[StudyType]INTERVENTIONAL",
}

EPMC_I = "(" + " OR ".join(['"GLP-1"', '"glucagon-like peptide-1"', '"glucagon like peptide 1"'] + DRUGS) + ")"
EPMC_QUERY = (f'(TITLE:{EPMC_I} OR ABSTRACT:{EPMC_I}) AND (TITLE:(cardiovascular OR MACE OR "myocardial infarction" OR '
              f'stroke) OR ABSTRACT:(cardiovascular OR MACE OR "myocardial infarction" OR stroke)) AND '
              f'(ABSTRACT:("type 2 diabetes" OR T2DM OR T2D) OR TITLE:("type 2 diabetes" OR T2DM OR T2D)) AND '
              f'(ABSTRACT:(randomised OR randomized OR randomly OR placebo) OR TITLE:(randomised OR randomized OR '
              f'placebo)) AND NOT SRC:MED')

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
LOG = []


def fetch(url, params, held, tag):
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status, body = http.get_raw(url, params)
    sha = hashlib.sha256(body).hexdigest() if body else None
    if body:
        open(os.path.join(held, f"{tag}.{sha[:12]}"), "wb").write(body)
    LOG.append({"url": url, "params": params, "utc": t0, "status": status, "bytes": len(body or b""), "sha256": sha,
                "held_local": f"LOCAL_ONLY:{tag}.{sha[:12]}" if sha else None})
    if status != 200 or not body:
        raise RuntimeError(f"FETCH_FAILED {tag}: status {status}, {len(body or b'')} bytes")
    return body


def pubmed(held):
    base = {"db": "pubmed", "tool": "meta-harness-evid2", "email": "meta-harness@example.org"}
    d = json.loads(fetch(f"{EUTILS}/esearch.fcgi", dict(base, term=PUBMED_QUERY, usehistory="y", retmax=0,
                                                         retmode="json"), held, "pubmed_esearch"))["esearchresult"]
    count, webenv, qk = int(d["count"]), d["webenv"], d["querykey"]
    pmids = []
    for start in range(0, count, 5000):
        r = json.loads(fetch(f"{EUTILS}/esearch.fcgi", dict(base, WebEnv=webenv, query_key=qk, retstart=start,
                                                            retmax=5000, retmode="json"), held, f"pubmed_ids_{start}"))
        pmids += r["esearchresult"]["idlist"]
        time.sleep(0.4)
    assert len(pmids) == count == len(set(pmids)), f"PubMed paging: {len(pmids)} ids for count {count}"
    recs = []
    for i in range(0, len(pmids), 200):
        xml = fetch(f"{EUTILS}/efetch.fcgi", dict(base, id=",".join(pmids[i:i + 200]), retmode="xml"), held, f"pubmed_efetch_{i}")
        for art in ET.fromstring(xml).findall(".//PubmedArticle"):
            abstract = " ".join((a.get("Label", "") + ": " if a.get("Label") else "") + _txt(a)
                                for a in art.findall(".//Abstract/AbstractText")).strip()
            db_ncts = [v for db in art.findall(".//DataBank") if _txt(db.find("DataBankName")).lower().startswith("clinicaltrials")
                       for v in (_txt(a) for a in db.findall(".//AccessionNumber")) if _NCT_RE.fullmatch(v)]
            doi = next((_txt(a) for a in art.findall(".//ArticleId") if a.get("IdType") == "doi"), "")
            recs.append({"id": _txt(art.find(".//MedlineCitation/PMID")), "id_type": "pmid",
                         "title": _txt(art.find(".//ArticleTitle")), "abstract": abstract,
                         "pubtypes": [_txt(p) for p in art.findall(".//PublicationType")],
                         "year": _txt(art.find(".//JournalIssue/PubDate/Year")) or _txt(art.find(".//JournalIssue/PubDate/MedlineDate"))[:4],
                         "journal": _txt(art.find(".//Journal/ISOAbbreviation")), "doi": doi,
                         "nct": _select_nct(abstract, db_ncts), "databank_ncts": sorted(set(db_ncts)),
                         "abstract_ncts": sorted(set(re.findall(r"NCT\d{8}", abstract))), "source": "pubmed"})
        time.sleep(0.4)
    got = {r["id"] for r in recs}
    missing = sorted(set(pmids) - got)
    return {"query": PUBMED_QUERY, "count": count, "retrieved": len(recs), "missing_on_efetch": missing}, recs


def ctgov(held):
    recs, raw, token, total = [], [], None, None
    while True:
        params = dict(CTGOV_PARAMS, pageSize=1000, countTotal="true", **({"pageToken": token} if token else {}))
        d = json.loads(fetch(CTGOV, params, held, f"ctgov_{len(raw)}"))
        total = d.get("totalCount", total)
        for s in d["studies"]:
            raw.append(s)
            r = _ctgov_record(s)
            refs = ((s.get("protocolSection") or {}).get("referencesModule") or {}).get("references") or []
            r.update(source="ctgov", reference_pmids=sorted({str(x["pmid"]) for x in refs if x.get("pmid")}),
                     reference_types={str(x["pmid"]): x.get("type") for x in refs if x.get("pmid")},
                     outcomes=[o.get("measure") for m in ("primaryOutcomes", "secondaryOutcomes")
                               for o in ((s.get("protocolSection") or {}).get("outcomesModule") or {}).get(m) or []])
            recs.append(r)
        token = d.get("nextPageToken")
        if not token:
            break
        time.sleep(0.4)
    assert total is None or len(recs) == total, f"CT.gov paging: {len(recs)} of {total}"
    return {"params": CTGOV_PARAMS, "count": total, "retrieved": len(recs)}, recs, raw


def epmc(held):
    recs, cursor, total = [], "*", None
    while True:
        d = json.loads(fetch(EPMC, {"query": EPMC_QUERY, "format": "json", "pageSize": 1000, "resultType": "core",
                                    "cursorMark": cursor}, held, f"epmc_{len(recs)}"))
        total = d.get("hitCount", total)
        page = d["resultList"]["result"]
        for x in page:
            recs.append({"id": f"{x.get('source')}:{x.get('id')}", "id_type": "epmc", "pmid": x.get("pmid") or "",
                         "title": x.get("title") or "", "abstract": re.sub(r"<[^>]+>", " ", x.get("abstractText") or ""),
                         "pubtypes": ((x.get("pubTypeList") or {}).get("pubType") or []), "year": x.get("pubYear") or "",
                         "journal": ((x.get("journalInfo") or {}).get("journal") or {}).get("isoabbreviation") or "",
                         "doi": x.get("doi") or "", "source": "europepmc", "epmc_source": x.get("source"),
                         "abstract_ncts": sorted(set(re.findall(r"NCT\d{8}", x.get("abstractText") or "")))})
        nxt = d.get("nextCursorMark")
        if not page or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.4)
    return {"query": EPMC_QUERY, "count": total, "retrieved": len(recs)}, recs


def main(held, out):
    os.makedirs(held, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    summary = {}
    pm_s, pm = pubmed(held)
    ct_s, ct, ct_raw = ctgov(held)
    ep_s, ep = epmc(held)
    summary = {"run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pubmed": pm_s, "ctgov": ct_s, "europepmc": ep_s}
    for name, recs in (("pubmed", pm), ("ctgov", ct), ("europepmc", ep)):
        with gzip.open(os.path.join(out, f"records_{name}.json.gz"), "wt", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False)
    with gzip.open(os.path.join(held, "ctgov_raw_studies.json.gz"), "wt", encoding="utf-8") as f:
        json.dump(ct_raw, f)
    json.dump(summary, open(os.path.join(out, "SEARCH_SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    json.dump(LOG, open(os.path.join(out, "REQUEST_LOG.json"), "w", encoding="utf-8", newline="\n"), indent=0)
    print(json.dumps(summary, indent=1)[:1500])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
