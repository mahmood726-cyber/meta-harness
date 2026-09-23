"""Documented registry search for rows whose registry parent is unresolved. For each row: the abstract's own
registration mentions (regex over held text), then ClinicalTrials.gov v2 full-text queries built from the
title. Every query URL, hit count and hit list is recorded in evidence/held/registry_search/<key>.json so a
'no registration found' is a stated search, not an assumption."""
import json, os, re, sys, time, urllib.parse, urllib.request, datetime, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT
REG = re.compile(r"\b(NCT\d{8}|ISRCTN\d{8}|ACTRN\d{14}|EudraCT[: ]*\d{4}-\d{6}-\d{2}|\d{4}-\d{6}-\d{2}|ChiCTR[-\w]+|DRKS\d{8}|NTR\d{3,5}|CTRI/\d{4}/\d+/\d+|JPRN-\w+|UMIN\d{9})\b")


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness-evidence-lane/1"}), timeout=60) as r:
            return r.status, r.read()
    except Exception as e:
        return getattr(e, "code", None), b""


def main(keys):
    pk_dir = os.path.join(ROOT, "evidence/packets")
    out_dir = os.path.join(ROOT, "evidence/held/registry_search"); os.makedirs(out_dir, exist_ok=True)
    meta = json.load(open(os.path.join(ROOT, "evidence/held/europepmc_meta.json"), encoding="utf-8"))
    for k in keys:
        pk = json.load(open(os.path.join(pk_dir, f"{k}.json"), encoding="utf-8"))
        pid = pk["trial"].replace("PMID ", "")
        mentions = sorted({m.group(0) for s in pk["sources"] if "text" in s for m in REG.finditer(s["text"])})
        title = (meta.get(pid) or {}).get("title") or ""
        year = (meta.get(pid) or {}).get("pubYear")
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", title) if w.lower() not in
                 {"with", "from", "versus", "compared", "randomized", "randomised", "trial", "study", "effect", "effects",
                  "patients", "placebo", "controlled", "double", "blind", "clinical", "results", "prevention", "multicentre", "multicenter"}][:6]
        queries = []
        for q in ([" ".join(words[:4])] + ([" ".join(words[:2])] if len(words) > 2 else [])):
            url = "https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode({"query.term": q, "pageSize": 25, "fields": "NCTId,BriefTitle,StartDate,OverallStatus"})
            st, body = get(url)
            hits = []
            try:
                for s in json.loads(body).get("studies", []):
                    ps = s["protocolSection"]
                    hits.append({"nct": ps["identificationModule"]["nctId"], "title": ps["identificationModule"].get("briefTitle"),
                                 "start": ps.get("statusModule", {}).get("startDateStruct", {}).get("date")})
            except Exception:
                pass
            queries.append({"registry": "ClinicalTrials.gov", "query": q, "url": url, "status": st, "n_hits": len(hits), "hits": hits,
                            "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
            time.sleep(0.5)
        rec = {"key": k, "pid": pid, "pub_year": year, "title": title, "registration_mentions_in_held_text": mentions,
               "queries": queries,
               "note": "ICMJE prospective registration became a condition of publication for trials starting from July 2005; an absent record for an earlier trial is expected, not evidence of concealment."}
        json.dump(rec, open(os.path.join(out_dir, f"{k}.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
        print(k, year, "mentions", mentions, "| ctgov hits", [q["n_hits"] for q in queries])


if __name__ == "__main__":
    main(sys.argv[1:])
