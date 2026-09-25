"""POLICY.md amendment C: ISRCTN for every UNRESOLVED registry_parent. Two fixed queries per trial, built from the
trial's own Europe PMC core record (title words; first author). A registration recovers the fact only if its own record
names the trial's publication (PMID, DOI or exact title); anything else is a CANDIDATE, never counted. Every request is
logged; bodies held LOCAL-ONLY; a failed fetch is FETCH_FAILED, never a zero.
usage: search_step2c.py <held_dir> <out.json>"""
import json, os, re, sys, time, urllib.parse
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from search_registry_parent import get  # noqa: E402  (the same logged fetcher)
from search_step4 import core, STOP  # noqa: E402

LED = json.load(open(os.path.join(HERE, "..", "ledger.json"), encoding="utf-8"))
API = "https://www.isrctn.com/api/query/format/default?limit=100&q="
NS = {"i": "http://www.67bricks.com/isrctn"}


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def main(held, out_path):
    os.makedirs(held, exist_ok=True)
    out = {}
    for r in LED["rows"]:
        if not any(f["fact_id"] == "registry_parent" and f["state"] == "UNRESOLVED" for f in r["facts"]):
            continue
        pmid = (re.search(r"PMID (\d+)", r["trial"]) or [None, None])[1]
        log = []
        rec = core(pmid, held, log) if pmid else None
        res = {"trial": r["trial"], "pmid": pmid, "queries": [], "requests": log, "registrations": []}
        if rec is None:
            res["fetch_state"] = "FETCH_FAILED"
            out[r["key"]] = res
            continue
        doi, title = (rec.get("doi") or "").lower(), norm(rec.get("title"))
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]+", rec.get("title") or "") if w.lower() not in STOP][:5]
        surname = ((rec.get("authorList") or {}).get("author") or [{}])[0].get("lastName") or ""
        seen = {}
        for label, q in (("2c-i", " ".join(words)), ("2c-ii", surname)):
            if not q:
                res["queries"].append({"step": label, "query": None, "why_none": "no title/author in the core record"})
                continue
            b = get(API + urllib.parse.quote(q), held, log, f"isrctn_{label}_{pmid}")
            try:
                root = ET.fromstring(b)
                trials = root.findall("i:fullTrial", NS)
                res["queries"].append({"step": label, "query": q, "totalCount": root.get("totalCount"),
                                       "fetched": len(trials), "fetch_state": "OK"})
            except Exception as e:
                res["queries"].append({"step": label, "query": q, "fetch_state": "FETCH_FAILED", "error": type(e).__name__})
                continue
            for t in trials:
                isrctn = t.find("i:trial/i:isrctn", NS)
                key = isrctn.text if isrctn is not None else None
                if not key or key in seen:
                    continue
                text = ET.tostring(t, encoding="unicode")
                flat = norm(re.sub(r"<[^>]+>", " ", text))
                names_it = []
                if pmid and re.search(r"(?<!\d)" + pmid + r"(?!\d)", text):
                    names_it.append(f"PMID {pmid}")
                if doi and doi in text.lower():
                    names_it.append(f"DOI {doi}")
                if title and len(title) > 30 and title in flat:
                    names_it.append("the article's exact title")
                ttl = t.find("i:trial/i:trialDescription/i:title", NS)
                seen[key] = {"isrctn": "ISRCTN" + key, "title": ttl.text if ttl is not None else None, "query": label,
                             "names_the_publication": names_it, "counts": bool(names_it)}
        res["registrations"] = list(seen.values())
        res["counted"] = [x["isrctn"] for x in seen.values() if x["counts"]]
        out[r["key"]] = res
        time.sleep(0.5)
    json.dump(out, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(k, v["pmid"], [(q["step"], q.get("totalCount"), q.get("fetch_state")) for q in v["queries"]],
              "counted:", v.get("counted"), "| candidates:", len(v.get("registrations", [])))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
