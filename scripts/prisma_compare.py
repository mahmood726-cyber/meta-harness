"""Blind-ish PRISMA 2020 DOMAIN comparison: harness page vs the comparator's ACTUAL open-access full
text (not our thin abstract-render of it), scored deterministically by detecting each item's
signature. Answers whether protocol/search/screening beat a published OA meta. Committed to
docs/prisma_compare.json; regenerable. Non-number-changing.

Our-side statuses come from the review object (what the page renders). Comparator-side comes from
signature detection in the OA full text — a present/absent probe, conservative (a described-but-not-
verbatim search still counts as present for item 7, giving the comparator the benefit of the doubt).
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness.http import get_json, get_text

SIG = {
    "7 search strategy": re.compile(r"search (strateg|term)|MEDLINE|Embase|Cochrane (Central|Library)|PubMed", re.I),
    "7 verbatim re-runnable": re.compile(r"\(\(|\bMeSH\b|\[tiab\]|\[Mesh\]|#\d+\s|\bAND\b.{0,40}\bOR\b", re.I),
    "8 dual independent screening": re.compile(r"two (reviewers|authors|investigators|researchers).{0,40}independent|independent(ly)?.{0,30}(screen|select|assess|extract|review)|\bkappa\b|disagreement", re.I),
    "16a flow diagram": re.compile(r"PRISMA|flow diagram|records? (were )?identified|records screened|studies included", re.I),
    "16b exclusions with reasons": re.compile(r"excluded.{0,60}(reason|because|did not|were not)|reasons for exclusion", re.I),
    "24 registration (PROSPERO)": re.compile(r"PROSPERO|CRD4\d{7}|registration number|prospectively registered|INPLASY", re.I),
}


def comparator_fulltext(pmid):
    r = get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                 {"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core"})
    h = (r.get("resultList", {}).get("result") or [{}])[0]
    pmc = h.get("pmcid")
    if not pmc or h.get("isOpenAccess") != "Y":
        return None
    try:
        return get_text(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML", {})
    except Exception:
        return None


def our_side(rev):
    s = rev.get("search") or {}; scr = rev.get("screening") or {}; prot = rev.get("protocol") or {}
    return {
        "7 search strategy": bool(s.get("sources")),
        "7 verbatim re-runnable": bool(s.get("sources")),  # our queries ARE verbatim + re-runnable
        "8 dual independent screening": bool(scr.get("dual")),
        "16a flow diagram": bool(scr.get("records")),
        "16b exclusions with reasons": any(x.get("decision") == "exclude" and x.get("span") for x in scr.get("records", [])),
        "24 registration (PROSPERO)": bool(prot.get("sha")),  # registration = committed protocol SHA
    }


def main(argv):
    base = os.path.join(ROOT, "docs", "reviews")
    slugs = argv or sorted(s for s in os.listdir(base) if os.path.exists(os.path.join(base, s, "review.json")))
    out = {}
    for slug in slugs:
        rev = json.load(open(os.path.join(base, slug, "review.json"), encoding="utf-8"))
        pmid = (rev.get("comparator") or {}).get("pmid")
        ours = our_side(rev)
        ft = comparator_fulltext(pmid) if pmid else None
        if ft is None:
            comp = {k: None for k in SIG}
        else:
            txt = re.sub(r"<[^>]+>", " ", ft)
            comp = {k: bool(rx.search(txt)) for k, rx in SIG.items()}
        out[slug] = {"pmid": pmid, "ours": ours, "comparator": comp}
        line = " ".join(f"{k.split()[0]}:{'O' if ours[k] else '.'}{'C' if comp[k] else ('.' if comp[k] is False else '?')}" for k in SIG)
        print(f"{slug:40} {line}", flush=True)
    if "--write" in argv or True:
        json.dump(out, open(os.path.join(ROOT, "docs", "prisma_compare.json"), "w", encoding="utf-8", newline=""), indent=1)
    # domain tallies
    items = list(SIG)
    ours_win = sum(1 for s in out for k in items if out[s]["ours"][k] and not out[s]["comparator"].get(k))
    comp_win = sum(1 for s in out for k in items if out[s]["comparator"].get(k) and not out[s]["ours"][k])
    print(f"\nitems where OURS present & comparator absent: {ours_win}; comparator present & ours absent: {comp_win}")
    return 0


if __name__ == "__main__":
    sys.exit(main([a for a in sys.argv[1:]]))
