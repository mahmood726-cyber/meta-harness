"""Comparator references that carry NO PMID and NO DOI: look each up in PubMed by its EXACT title (NCBI E-utilities,
a legitimate open source), then CONFIRM every hit by first-author surname and publication year from the record
itself. Results -- including every miss -- are cached with retrieval time in outputs/k_gap/ref_title_pmid.json, so
the identity step that consumes them runs offline and never guesses.

    python scripts/ref_title_pmid_lookup.py REFS.json      # REFS.json: [{key, title, first_author, year}]
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap", "ref_title_pmid.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
UA = {"User-Agent": "meta-harness ref_title_pmid_lookup (offline cache builder)"}


def norm(s):
    # NFKC first: a PDF text extraction writes 'ﬁrst' (U+FB01 ligature) where PubMed writes 'first'
    import unicodedata
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKC", s or "").lower()).strip()


def fold(s):
    """Diacritics folded for SURNAME comparison only ('Boudhrâa' == 'Boudhraa'); titles are never folded this way."""
    import unicodedata
    # whitespace removed too: a PDF extraction splits surnames ('Finke lstein'); surnames only, never titles
    return re.sub(r"\s+", "", "".join(c for c in unicodedata.normalize("NFKD", s or "")
                                      if not unicodedata.combining(c)).lower())


def same_title(pubmed_title, cited_title):
    """Exact normalised title, or PubMed's title = the cited title + a SUBTITLE after a sentence boundary (a review's
    citation drops '. A randomized, placebo-controlled ... study.'), allowed only for a cited title of >= 8 words."""
    p, c = norm(pubmed_title), norm(cited_title)
    if p == c:
        return True
    if len(c.split()) < 8 or not p.startswith(c + " "):
        return False
    cut = re.match(r"\W*" + r"\W+".join(map(re.escape, c.split())) + r"(?P<next>\W*)(?P<sub>.*)$", pubmed_title,
                   re.I | re.S)
    # only a DESIGN DESCRIPTOR after a full stop ('. A randomized, placebo-controlled ... study.'): a colon subtitle
    # ('...: renal outcomes in the eye disease substudy') names a different, companion paper (IDREVIEW P1)
    return bool(cut and re.match(r"\s*\.", cut.group("next")) and re.match(
        r"\s*(?:an?\s+)?(?:(?:prospective|randomi[sz]ed|double[- ]blind|single[- ]blind|open[- ]label|placebo[- ]"
        r"controlled|controlled|multi-?cent(?:re|er)|parallel[- ]group|crossover|pilot|clinical)[\s,-]*)+"
        r"(?:study|trial)\.?\s*$", cut.group("sub"), re.I))


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
            if body.lstrip()[:1] in (b"<",) and b"<html" in body[:200].lower():
                raise ValueError("HTML error page, not an E-utilities payload")
            return body
        except Exception:  # noqa: BLE001 -- bounded retry, then fail closed
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def lookup(ref):
    # Each title word AND-ed in [ti], UNQUOTED: PubMed's phrase index does not hold long titles, so a quoted title
    # returns 0 with warning 'quotedphrasesnotfound' even for an indexed paper (ROCKET AF's NEJM title did). Precision
    # comes from the confirmation below (exact normalised title + first author + year), never from the query.
    # PubMed stopwords are not indexed: AND-ing 'with'[ti] makes the WHOLE query return 0 ('phrasesnotfound')
    stop = {"the", "and", "with", "for", "from", "into", "its", "are", "was", "were", "not", "but", "that", "this",
            "than", "has", "have", "had", "their", "there", "these", "those", "which", "who", "can", "may", "via", "per",
            "about", "after", "among", "between", "during", "under", "over", "all", "any", "been", "being", "both",
            "each", "more", "most", "such", "other", "some", "only", "also", "out", "off", "how", "what", "when"}
    words = [w for w in norm(ref["title"]).split() if len(w) > 2 and w not in stop and w not in ref.get("_drop", ())][:20]
    term = " AND ".join(f"{w}[ti]" for w in words)
    if ref.get("first_author"):
        au = re.sub(r"\s+", "", ref["first_author"]) if ref.get("_join_author") else ref["first_author"]
        term += f" AND {au}[1au]"
    res = json.loads(get(EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmode": "json", "retmax": 20})))["esearchresult"]
    ids = res["idlist"]
    time.sleep(0.4)
    out = {"query": term, "candidates": ids, "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "warnings": res.get("warninglist") or {}, "errors": res.get("errorlist") or {}}
    if any(out["warnings"].get(k) for k in ("quotedphrasesnotfound", "phrasesignored")) or \
            any(out["errors"].get(k) for k in ("phrasesnotfound", "fieldsnotfound")):
        # PubMed altered or dropped part of the query: a zero here is a statement about the QUERY, not the paper.
        # ONE retry without exactly the words PubMed names as not found (a title word the index lacks, e.g. 'infloran');
        # precision is unchanged -- the confirmation below still demands the exact title, first author and year.
        missing = [w.lower() for w in (out["errors"].get("phrasesnotfound") or [])]
        # the ONE missing token is the first author's whole (single-word) surname: PubMed's author index has no such
        # author, so no paper with that first author is in PubMed. A finding about PubMed, stated as exactly that.
        sur = (ref.get("first_author") or "").strip().lower()
        if missing == [sur] and sur and " " not in sur and not out["errors"].get("fieldsnotfound"):
            return dict(out, state="NOT_IN_PUBMED_FIRST_AUTHOR_NOT_INDEXED")
        # a missing token that belongs to the AUTHOR is a PDF-split surname ('Finke lstein'): retry it joined
        in_author = [w for w in missing if w in (ref.get("first_author") or "").lower().split()]
        if in_author and " " in (ref.get("first_author") or "") and not ref.get("_join_author"):
            again = lookup(dict(ref, _join_author=True))
            return dict(again, first_query=out["query"], joined_author=True)
        if missing and not ref.get("_drop"):
            again = lookup(dict(ref, _drop=tuple(missing)))
            return dict(again, first_query=out["query"], dropped_words=missing)
        return dict(out, state="QUERY_NOT_EXECUTED_AS_WRITTEN")
    if not ids:
        return dict(out, state="NOT_IN_PUBMED_BY_TITLE_WORDS_AND_FIRST_AUTHOR")
    root = ET.fromstring(get(EUTILS + "efetch.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids),
                                                                                  "retmode": "xml"})))
    time.sleep(0.4)
    confirmed = []
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        sur = art.findtext(".//AuthorList/Author/LastName") or ""
        year = art.findtext(".//JournalIssue/PubDate/Year") or (art.findtext(".//JournalIssue/PubDate/MedlineDate") or "")[:4]
        nct = sorted({a.text for a in art.iter("AccessionNumber") if a.text and a.text.startswith("NCT")})
        ok = (same_title(title, ref["title"]) and fold(sur) == fold(ref.get("first_author"))
              and (not ref.get("year") or year == ref["year"]))
        (confirmed if ok else out.setdefault("rejected", [])).append(
            {"pmid": pmid, "title": title, "first_author": sur, "year": year, "databank_ncts": nct})
    if len(confirmed) == 1:
        return dict(out, state="CONFIRMED", **confirmed[0])
    return dict(out, state="AMBIGUOUS" if confirmed else "CANDIDATES_NOT_CONFIRMED", confirmed=confirmed)


def main(path):
    refs = json.load(open(path, encoding="utf-8"))
    cache = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for ref in refs:
        if ref["key"] in cache or not norm(ref.get("title")):
            continue
        cache[ref["key"]] = dict(lookup(ref), ref=ref)
        print(ref["key"], cache[ref["key"]]["state"], cache[ref["key"]].get("pmid", ""))
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cache, fh, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, OUT)


if __name__ == "__main__":
    main(sys.argv[1])
