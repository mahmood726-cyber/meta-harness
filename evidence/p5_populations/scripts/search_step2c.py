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


PUB_FIELDS = ("outputs", "publicationDetails", "results")   # where an ISRCTN record lists its publications


def publication_text(trial_el):
    """The text of the record's PUBLICATION fields only (review 5: the whole record matched its own title, a longer
    title containing the paper's, and an ethics reference '06/16769748')."""
    out = []
    for el in trial_el.iter():
        if el.tag.split("}")[-1] in PUB_FIELDS:
            out.append(ET.tostring(el, encoding="unicode"))
    return " ".join(out)


def names_publication(pub_xml, pmid, doi, title):
    hits = []
    if pmid and re.search(r"(?:pubmed[^\s\"<]*?/|PMID:?\s*)" + pmid + r"(?!\d)", pub_xml, re.I):
        hits.append(f"PMID {pmid}")
    if doi:
        esc = re.escape(doi)
        if re.search(r"(?<![\w.\-/])" + esc + r"(?![\w.\-/])", pub_xml.lower()):
            hits.append(f"DOI {doi}")
    # the title as a whole citation element: its words in order, starting at a word boundary and ENDING where a
    # citation's title ends (punctuation or the field's end) -- a longer title that merely contains it is another paper
    plain = re.sub(r"<[^>]+>", " \n ", pub_xml).lower()
    if title and len(title) > 30:
        pat = r"(?<![a-z0-9])" + r"[^a-z0-9]+".join(map(re.escape, title.split())) + r"(?=[ \t]*(?:[.;:?!]|\n|$))"
        if re.search(pat, plain):
            hits.append("the article's exact title (a whole citation element, in a publication field)")
    return hits


def main(held, out_path):
    os.makedirs(held, exist_ok=True)
    out = {}
    for r in LED["rows"]:
        if not any(f["fact_id"] == "registry_parent" and f["state"] == "UNRESOLVED" for f in r["facts"]):
            continue
        pmid = (re.search(r"PMID (\d+)", r["trial"]) or [None, None])[1]
        log = []
        res = {"trial": r["trial"], "pmid": pmid, "queries": [], "requests": log, "registrations": []}
        if not pmid:
            res["fetch_state"], res["counted"] = "NO_PMID", None
            out[r["key"]] = res
            continue
        rec = core(pmid, held, log)
        if rec is None:
            res["fetch_state"], res["counted"] = "FETCH_FAILED", None
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
                if root.tag != "{%s}allTrials" % NS["i"] or root.get("totalCount") is None:
                    raise ValueError("not an ISRCTN allTrials response")
                trials = root.findall("i:fullTrial", NS)
                total = int(root.get("totalCount"))
                if len(trials) < min(total, 100):
                    raise ValueError(f"{len(trials)} records for totalCount {total}")
                res["queries"].append({"step": label, "query": q, "totalCount": total, "fetched": len(trials),
                                       "fetch_state": "OK"})
            except Exception as e:
                res["queries"].append({"step": label, "query": q, "fetch_state": "FETCH_FAILED", "error": f"{type(e).__name__}: {e}"})
                continue
            for t in trials:
                isrctn = t.find("i:trial/i:isrctn", NS)
                key = isrctn.text if isrctn is not None else None
                if not key or key in seen:
                    continue
                names_it = names_publication(publication_text(t), pmid, doi, title)
                ttl = t.find("i:trial/i:trialDescription/i:title", NS)
                seen[key] = {"isrctn": "ISRCTN" + key, "title": ttl.text if ttl is not None else None, "query": label,
                             "names_the_publication": names_it, "counts": bool(names_it)}
        res["registrations"] = list(seen.values())
        failed = any(q.get("fetch_state") == "FETCH_FAILED" for q in res["queries"])
        res["fetch_state"] = "FETCH_FAILED" if failed else "OK"
        res["counted"] = None if failed else [x["isrctn"] for x in seen.values() if x["counts"]]
        out[r["key"]] = res
        time.sleep(0.5)
    json.dump(out, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(k, v["pmid"], [(q["step"], q.get("totalCount"), q.get("fetch_state")) for q in v["queries"]],
              "counted:", v.get("counted"), "| candidates:", len(v.get("registrations", [])))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
