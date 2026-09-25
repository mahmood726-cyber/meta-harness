"""Documented search for a registry parent of a publication-only trial (POLICY.md, search steps 1-3).

For each PMID: (a) Europe PMC core record (abstract; PMCID; open-access flag); (b) PubMed efetch XML DataBankList
(publisher-supplied accession numbers -- a LOCATOR only); (c) Europe PMC full-text XML where it is served; (d) a
registration-identifier regex over every text fetched. Every request is logged with URL, time, HTTP outcome, sha256 of
the body and what was found. Bodies are held LOCAL-ONLY under --held (never committed; licences vary).

A registration identifier printed in the trial's OWN article text (abstract or full text) is a span of the trial's own
document. An accession found only in PubMed metadata is a locator: it is recorded as such and is not a recovery unless
the registry record it points to is fetched and names the same trial.
Output: JSON on stdout -- one object per PMID."""
import hashlib, json, os, re, sys, time, urllib.request, urllib.error

REG = re.compile(r"\b(NCT\d{8}|ISRCTN\s?\d{8}|ACTRN\d{14}|ANZCTR\d+|EudraCT[\s:]*\d{4}-\d{6}-\d{2}|\d{4}-\d{6}-\d{2}|"
                 r"ChiCTR[-\w]{6,20}|IRCT\d{6,}N?\d*|CTRI/\d{4}/\d{2,3}/\d{6}|DRKS\d{8}|NTR\d{3,5}|UMIN\d{9}|"
                 r"JPRN-\w+|KCT\d{7}|TCTR\d{11}|PACTR\d{15}|SLCTR/\d{4}/\d{3})\b", re.I)


def get(url, held, log, tag):
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "meta-harness-evid2/1.0 (evidence audit)"})
        body = urllib.request.urlopen(req, timeout=60).read()
        status = 200
    except urllib.error.HTTPError as e:
        body, status = b"", e.code
    except Exception as e:
        body, status = b"", f"ERROR {type(e).__name__}"
    sha = hashlib.sha256(body).hexdigest() if body else None
    path = None
    if body:
        path = os.path.join(held, f"{tag}.{sha[:12]}")
        open(path, "wb").write(body)
    log.append({"url": url, "retrieved_utc": t0, "status": status, "bytes": len(body), "sha256": sha, "held_local": path})
    return body


def main():
    held = sys.argv[1]
    os.makedirs(held, exist_ok=True)
    out = []
    for pmid in sys.argv[2:]:
        log, hits = [], []
        core = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}%20AND%20SRC:MED"
                   f"&resultType=core&format=json", held, log, f"epmc_core_{pmid}")
        rec = {}
        try:
            rec = json.loads(core)["resultList"]["result"][0]
        except Exception:
            pass
        abstract = (rec.get("title") or "") + " " + re.sub(r"<[^>]+>", " ", rec.get("abstractText") or "")
        for m in REG.finditer(abstract):
            hits.append({"id": m.group(0), "where": "Europe PMC abstract (the article's own abstract)",
                         "context": abstract[max(0, m.start() - 120): m.end() + 60]})
        pm = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml",
                 held, log, f"pubmed_{pmid}")
        pmx = pm.decode("utf-8", errors="replace")
        for m in re.finditer(r"<AccessionNumber>([^<]+)</AccessionNumber>", pmx):
            hits.append({"id": m.group(1), "where": "PubMed DataBankList (publisher metadata -- LOCATOR ONLY)", "context": ""})
        pmcid = rec.get("pmcid")
        ft_text = ""
        if pmcid:
            ft = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", held, log, f"ft_{pmcid}")
            ft_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", ft.decode("utf-8", errors="replace")))
            for m in REG.finditer(ft_text):
                hits.append({"id": m.group(0), "where": f"full text {pmcid} (the article's own text)",
                             "context": ft_text[max(0, m.start() - 160): m.end() + 80]})
        # a failed fetch is never a zero (review 4, 2026-09-25): a non-200, an empty body, or a core record that did not
        # parse makes the whole PMID FETCH_FAILED, and its 'no registration found' is not a result
        failed = [x for x in log if x["status"] != 200 or not x["bytes"]]
        out.append({"pmid": pmid, "pmcid": pmcid, "open_access": rec.get("isOpenAccess"), "in_epmc": rec.get("inEPMC"),
                    "title": rec.get("title"), "year": rec.get("pubYear"), "full_text_chars": len(ft_text),
                    "registration_hits": hits, "requests": log,
                    "fetch_state": "FETCH_FAILED" if (failed or not rec) else "OK",
                    "failed_requests": [{"url": x["url"], "status": x["status"]} for x in failed]})
        time.sleep(0.5)
    sys.stdout.buffer.write(json.dumps(out, indent=1, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    main()
