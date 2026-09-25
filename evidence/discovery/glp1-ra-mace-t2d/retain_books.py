"""Amendment 1: retain the PubmedBookArticle hits search.py did not parse (the missing_on_efetch list)."""
import gzip, json, os, sys, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search as S  # noqa: E402  (the same logged fetcher)


def main(held, out):
    s = json.load(open(os.path.join(out, "SEARCH_SUMMARY.json"), encoding="utf-8"))
    missing = s["pubmed"]["missing_on_efetch"]
    xml = S.fetch(f"{S.EUTILS}/efetch.fcgi", {"db": "pubmed", "id": ",".join(missing), "retmode": "xml",
                                               "tool": "meta-harness-evid2", "email": "meta-harness@example.org"}, held, "pubmed_books")
    recs = []
    for b in ET.fromstring(xml).findall(".//PubmedBookArticle"):
        pmid = S._txt(b.find(".//BookDocument/PMID"))
        title = S._txt(b.find(".//BookDocument/ArticleTitle")) or S._txt(b.find(".//BookDocument/Book/BookTitle"))
        abstract = " ".join(S._txt(a) for a in b.findall(".//BookDocument/Abstract/AbstractText")).strip()
        recs.append({"id": pmid, "id_type": "pmid", "title": title, "abstract": abstract, "pubtypes": ["Book"],
                     "year": S._txt(b.find(".//Book/PubDate/Year")), "journal": "", "doi": "", "nct": "",
                     "databank_ncts": [], "abstract_ncts": [], "source": "pubmed", "record_kind": "PubmedBookArticle"})
    p = os.path.join(out, "records_pubmed.json.gz")
    allr = json.load(gzip.open(p, "rt", encoding="utf-8"))
    have = {r["id"] for r in allr}
    allr += [r for r in recs if r["id"] not in have]
    json.dump(allr, gzip.open(p, "wt", encoding="utf-8"), ensure_ascii=False)
    s["pubmed"]["retrieved"] = len(allr)
    s["pubmed"]["books_retained_by_amendment_1"] = sorted(r["id"] for r in recs)
    s["pubmed"]["missing_on_efetch"] = sorted(set(missing) - {r["id"] for r in recs})
    json.dump(s, open(os.path.join(out, "SEARCH_SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    log = json.load(open(os.path.join(out, "REQUEST_LOG.json"), encoding="utf-8")) + S.LOG
    json.dump(log, open(os.path.join(out, "REQUEST_LOG.json"), "w", encoding="utf-8", newline="\n"), indent=0)
    print(len(recs), "books retained; pubmed records now", len(allr), "; still missing", s["pubmed"]["missing_on_efetch"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
