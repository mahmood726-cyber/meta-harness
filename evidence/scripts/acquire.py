"""Acquire authentic sources for worklist rows: Europe PMC (web, current) for PMCID + open-access full text,
ClinicalTrials.gov v2 for the registry record. Every file is stored with its URL, fetch time and sha256 in
evidence/held/ACQUISITIONS.json. Fails closed: an HTML/error payload or a non-XML/JSON body is never stored."""
import json, os, sys, time, hashlib, urllib.request, urllib.parse, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HELD = os.path.join(ROOT, "evidence", "held")
LEDGER = os.path.join(HELD, "ACQUISITIONS.json")
UA = "meta-harness-evidence-lane/1 (mailto:mahmood726@gmail.com)"


def get(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 400):
                return e.code, b""
            time.sleep(2 * (k + 1))
        except Exception:
            time.sleep(2 * (k + 1))
    return None, b""


def store(rel, body, url, ledger, kind):
    """A held file is pinned by adjudications, so it is written ONCE: a re-fetch with identical bytes keeps the first
    ledger entry (the true provenance), and a re-fetch whose bytes differ is refused, never overwritten."""
    p = os.path.join(HELD, rel)
    digest = hashlib.sha256(body).hexdigest()
    if os.path.exists(p):
        held = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if held != digest:
            print(f"REFUSED: {rel} is held with different bytes; the source changed since it was pinned -- not overwritten")
            return
        if rel in ledger:
            return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(body)
    ledger[rel] = {"url": url, "kind": kind,
                   "fetched_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "sha256": digest, "bytes": len(body)}


def main():
    wl = json.load(open(os.path.join(ROOT, "evidence", "worklist.json"), encoding="utf-8"))
    ledger = json.load(open(LEDGER, encoding="utf-8")) if os.path.exists(LEDGER) else {}
    meta = {}
    pids = sorted({w["pid"] for w in wl["rows"] if w["pid"]})
    ncts = set()
    for w in wl["rows"]:
        for x in (w.get("family_id"), w["trial"]):
            if x and str(x).startswith("NCT"):
                ncts.add(x)
        for h in w["held"]:
            if h.get("nct") and str(h["nct"]).startswith("NCT"):
                ncts.add(h["nct"])
    for pid in pids:
        url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="
               + urllib.parse.quote(f"EXT_ID:{pid} AND SRC:MED"))
        st, body = get(url)
        try:
            res = json.loads(body)["resultList"]["result"]
        except Exception:
            meta[pid] = {"error": f"europepmc search status {st}"}; continue
        r = res[0] if res else {}
        m = {k: r.get(k) for k in ("pmcid", "doi", "title", "isOpenAccess", "inPMC", "hasTextMinedTerms", "journalTitle", "pubYear")}
        m["abstract_chars"] = len(r.get("abstractText") or "")
        meta[pid] = m
        rel = f"{pid}/europepmc_core.json"
        if rel not in ledger:
            store(rel, body, url, ledger, "europepmc_core_record")
        if m.get("pmcid") and m.get("isOpenAccess") == "Y":
            rel = f"{pid}/{m['pmcid']}.xml"
            if rel not in ledger:
                u = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{m['pmcid']}/fullTextXML"
                st, body = get(u)
                if st == 200 and body.lstrip().startswith(b"<") and b"<article" in body[:5000]:
                    store(rel, body, u, ledger, "europepmc_oa_fulltext_xml")
                else:
                    m["fulltext_error"] = f"status {st}"
        time.sleep(0.4)
        print(pid, m.get("pmcid"), m.get("isOpenAccess"), file=sys.stderr)
    for nct in sorted(ncts):
        rel = f"registry/{nct}.json"
        if rel in ledger:
            continue
        u = f"https://clinicaltrials.gov/api/v2/studies/{nct}"
        st, body = get(u)
        if st == 200 and body.lstrip().startswith(b"{"):
            store(rel, body, u, ledger, "ctgov_v2_study")
        else:
            meta[nct] = {"error": f"ctgov status {st}"}
        time.sleep(0.4)
    # held/** is -text (bytes kept as written), so the writer itself must emit LF like the rest of the tree
    json.dump(ledger, open(LEDGER, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    json.dump(meta, open(os.path.join(HELD, "europepmc_meta.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    oa = sum(1 for m in meta.values() if m.get("isOpenAccess") == "Y")
    print(f"pmids {len(pids)}; OA full text {oa}; ncts {len(ncts)}; ledger files {len(ledger)}")


if __name__ == "__main__":
    main()
