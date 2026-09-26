"""Acquire one article by PMID (or resolve a title query to a PMID first): Europe PMC core record (abstract) into
evidence/held/<pid>/, open-access full-text XML when OA, else the PMC free HTML into evidence/held_local/<pid>/
(not redistributed; URL + sha256 in LOCAL_ACQUISITIONS.json). Usage:
  python acquire_pid.py 26819227 [more pmids]
  python acquire_pid.py --title "Effect of Dapagliflozin on Heart Failure and Mortality in Type 2 Diabetes Mellitus"
"""
import datetime, hashlib, json, os, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import acquire as A
ROOT = A.ROOT


def title_to_pid(title):
    u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=lite&query="
         + urllib.parse.quote(f'TITLE:"{title}" AND SRC:MED'))
    st, b = A.get(u)
    res = json.loads(b)["resultList"]["result"] if st == 200 else []
    return res[0]["pmid"] if res else None


def acquire(pid):
    led = json.load(open(A.LEDGER, encoding="utf-8"))
    u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="
         + urllib.parse.quote(f"EXT_ID:{pid} AND SRC:MED"))
    st, b = A.get(u)
    if st != 200:
        return f"{pid}: europepmc status {st}"
    r = (json.loads(b)["resultList"]["result"] or [{}])[0]
    if f"{pid}/europepmc_core.json" not in led:
        A.store(f"{pid}/europepmc_core.json", b, u, led, "europepmc_core_record")
    out = f"{pid}: {r.get('title', '')[:90]} | pmcid {r.get('pmcid')} OA {r.get('isOpenAccess')}"
    if r.get("pmcid") and r.get("isOpenAccess") == "Y":
        u2 = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{r['pmcid']}/fullTextXML"
        st2, b2 = A.get(u2)
        if st2 == 200 and b"<article" in b2[:5000]:
            A.store(f"{pid}/{r['pmcid']}.xml", b2, u2, led, "europepmc_oa_fulltext_xml"); out += " -> OA XML held"
    elif r.get("pmcid"):
        u3 = f"https://pmc.ncbi.nlm.nih.gov/articles/{r['pmcid']}/"
        try:
            b3 = urllib.request.urlopen(urllib.request.Request(u3, headers={"User-Agent": "Mozilla/5.0 evidence-lane"}), timeout=60).read()
        except Exception as e:
            b3 = b""; out += f" -> PMC html failed {e}"
        if b"<article" in b3 or b"citation_title" in b3:
            rel = f"{pid}/{r['pmcid']}.html"; p = os.path.join(ROOT, "evidence", "held_local", rel)
            os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(b3)
            lp = os.path.join(ROOT, "evidence", "LOCAL_ACQUISITIONS.json"); ll = json.load(open(lp, encoding="utf-8"))
            ll[rel] = {"url": u3, "sha256": hashlib.sha256(b3).hexdigest(), "bytes": len(b3),
                       "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "licence": "PMC free full text, not in the OA subset"}
            json.dump(ll, open(lp, "w", encoding="utf-8", newline="\n"), indent=1); out += " -> PMC html held LOCAL"
    json.dump(led, open(A.LEDGER, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--title":
        pid = title_to_pid(args[1]); print("resolved", pid); args = [pid] if pid else []
    for p in args:
        print(acquire(p)); time.sleep(0.5)
