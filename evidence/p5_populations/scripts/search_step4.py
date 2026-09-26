"""POLICY.md amendment A: step 4 (two fixed Europe PMC queries for a same-trial protocol/design/baseline paper) and
step 2b (ClinicalTrials.gov reverse lookup by ReferencePMID) for every UNRESOLVED fact's trial.
Queries are built mechanically from the trial's own Europe PMC core record (first author, year, title) -- nothing is
chosen after a result is seen. Every request is logged (URL, time, status, bytes, sha256); bodies held LOCAL-ONLY.
usage: search_step4.py <held_dir> <out.json>"""
import json, os, re, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from search_registry_parent import get, REG  # noqa: E402  (same logged fetcher, same identifier regex)

LED = json.load(open(os.path.join(HERE, "..", "ledger.json"), encoding="utf-8"))
STOP = set("a an and the of in on for with to by or vs versus from at as is are was were its their after before "
           "during between among into than trial study randomised randomized controlled double blind placebo".split())
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=25&resultType=lite&query="


def core(pmid, held, log):
    b = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}%20AND%20SRC:MED"
            f"&resultType=core&format=json", held, log, f"epmc_core_{pmid}")
    try:
        return json.loads(b)["resultList"]["result"][0]
    except Exception:
        return None   # a FAILED fetch, not an empty record (review 4)


def epmc_all(q, held, log, tag, limit):
    """Every hit of a Europe PMC query, paged by cursorMark up to `limit`; (hitCount, hits, fetch_ok)."""
    hits, cursor, total = [], "*", None
    while True:
        b = get(EPMC + urllib.parse.quote(q) + "&cursorMark=" + urllib.parse.quote(cursor), held, log, tag)
        try:
            d = json.loads(b)
            total = d["hitCount"]
            page = d["resultList"]["result"]
        except Exception:
            return total, hits, False
        hits += page
        nxt = d.get("nextCursorMark")
        if not page or not nxt or nxt == cursor or len(hits) >= min(total, limit):
            return total, hits[:limit], True
        cursor = nxt
        time.sleep(0.3)


def queries(rec):
    surname = ((rec.get("authorList") or {}).get("author") or [{}])[0].get("lastName") or ""
    year = int(rec.get("pubYear") or 0)
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]+", rec.get("title") or "") if w.lower() not in STOP][:5]
    q4a = (f'AUTH:"{surname}" AND PUB_YEAR:[{year - 4} TO {year + 1}] AND (TITLE:protocol OR TITLE:design OR '
           f'TITLE:rationale OR TITLE:baseline OR TITLE:methods)') if surname and year else None
    q4b = (" AND ".join(words) + " AND (protocol OR design OR rationale OR baseline)") if words else None
    return q4a, q4b


def main(held, out_path):
    os.makedirs(held, exist_ok=True)
    targets = {}
    for r in LED["rows"]:
        for f in r["facts"]:
            if f["state"] == "UNRESOLVED":
                targets.setdefault(r["key"], {"trial": r["trial"], "facts": []})["facts"].append(f["fact_id"])
    out = {}
    for key, t in sorted(targets.items()):
        pmid = (re.search(r"PMID (\d+)", t["trial"]) or [None, None])[1]
        log, rec = [], {}
        res = {"trial": t["trial"], "facts": t["facts"], "pmid": pmid, "queries": [], "requests": log}
        if pmid:
            rec = core(pmid, held, log)
            if rec is None:
                res["fetch_state"] = "FETCH_FAILED"
                res["queries"].append({"step": "core", "error": "the trial's own core record did not fetch; 4a/4b not run"})
                rec = {}
            # 4a (author-limited) is paged to EVERY hit; 4b (title words, very broad) is the first 25 by relevance --
            # stated in POLICY.md amendment B and in every record (review 4, 2026-09-25)
            for label, q, limit in zip(("4a", "4b"), queries(rec), (5000, 25)):
                if not q:
                    res["queries"].append({"step": label, "query": None, "why_none": "no author/year/title in core record"})
                    continue
                total, raw, ok = epmc_all(q, held, log, f"epmc_q{label}_{pmid}", limit)
                hits = [{"pmid": x.get("pmid"), "pmcid": x.get("pmcid"), "title": x.get("title"), "year": x.get("pubYear"),
                         "journal": x.get("journalTitle"), "is_the_trial_report": x.get("pmid") == pmid} for x in raw]
                res["queries"].append({"step": label, "query": q, "hitCount": total, "hits": hits,
                                       "coverage": ("all hits" if limit >= 5000 else f"first {limit} by relevance"),
                                       "fetch_state": "OK" if ok else "FETCH_FAILED"})
                time.sleep(0.4)
            url = ("https://clinicaltrials.gov/api/v2/studies?format=json&pageSize=100&fields=NCTId,BriefTitle,ReferencesModule"
                   "&query.term=" + urllib.parse.quote(f"AREA[ReferencePMID]{pmid}"))
            regs, studies, token, ok = [], [], None, True
            while True:
                b = get(url + (f"&pageToken={token}" if token else ""), held, log, f"ctgov_refpmid_{pmid}")
                try:
                    d = json.loads(b)
                    studies += d["studies"]          # a JSON error body has no 'studies': a failure, not a zero
                except Exception:
                    ok = False
                    break
                token = d.get("nextPageToken")
                if not token:
                    break
            try:
                if not ok:
                    raise ValueError("FETCH_FAILED")
                for s in studies:
                    ps = s.get("protocolSection", {})
                    nct = ps.get("identificationModule", {}).get("nctId")
                    refs = [x for x in ps.get("referencesModule", {}).get("references", []) if str(x.get("pmid")) == pmid]
                    regs.append({"nct": nct, "title": ps.get("identificationModule", {}).get("briefTitle"),
                                 "reference_types": [x.get("type") for x in refs],
                                 "counts": any(x.get("type") in ("RESULT", "DERIVED") for x in refs)})
                res["step2b"] = {"url": url, "registrations": regs, "fetch_state": "OK", "pages": "all"}
            except Exception as e:
                res["step2b"] = {"url": url, "error": type(e).__name__, "fetch_state": "FETCH_FAILED"}
        else:
            res["why_none"] = "trial has no PMID (registry-identified row)"
        res["title"] = rec.get("title")
        out[key] = res
        time.sleep(0.4)
    json.dump(out, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(k, v["pmid"], [(q["step"], q.get("hitCount")) for q in v["queries"]],
              [(x["nct"], x["reference_types"]) for x in (v.get("step2b") or {}).get("registrations", [])])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
