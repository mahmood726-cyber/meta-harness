"""R8-4: why a trial we pool is absent from the comparator is decided by DATES, never by years. The comparator's
search END date (typed from its own abstract, else its full text -- regex only, a short verbatim span recorded) is
compared with the trial's FIRST PUBLIC date: its earliest PubMed electronic / entrez / issue date, or its registry
results-posting date (AACT studies.results_first_posted_date) when earlier AND the comparator's own search names a
trial registry. The old rule compared publication YEARS (with the served page's comparator year, which can belong to a
previous comparator). Chen 2023 (esketamine) shows why both dates are recorded: published 2023, after the comparator's
December 2022 search end (why_by_publication_only = AFTER_COMPARATOR_SEARCH_END), but its NCT03434041 results were
posted 2022-05-24 and the comparator searched ClinicalTrials.gov, so the verdict is NOT_EXPLAINED_BY_DATE.

  AFTER_COMPARATOR_SEARCH_END   first public after the search end (month precision; year precision when only a year
                                is stated)
  NOT_EXPLAINED_BY_DATE         first public before the search end
  SAME_PERIOD_AS_SEARCH_END     same month (or same year at year precision): undetermined
  PUBLISHED_AFTER_COMPARATOR    no search end stated; first public after the comparator's own first public date
  SEARCH_END_NOT_STATED         no search end stated and not after the comparator's publication: undetermined

    python scripts/r8_4_search_dates.py --from-tracker  current tracker list -> registry/comparator_search_dates_targets.json
    python scripts/r8_4_search_dates.py --fetch   PubMed XML for comparators + trials -> cache/r8_4/pubmed/<pmid>.xml
    python scripts/r8_4_search_dates.py           -> registry/comparator_search_dates.json (typed, from the cache)
"""
from __future__ import annotations

import csv
import glob
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "r8_4", "pubmed")
OUT = os.path.join(ROOT, "registry", "comparator_search_dates.json")
G1 = os.path.join(ROOT, "outputs", "k_gap", "g1")
MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                          "dec"])}
_MONTH = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
_DATE = re.compile(r"(?:(\d{1,2})(?:st|nd|rd|th)?\s+)?\b" + _MONTH + r"\.?\s*(?:(\d{1,2})(?:st|nd|rd|th)?,?\s+)?(\d{4})\b",
                   re.I)
_SEARCH = re.compile(r"\b(?:search(?:ed|es|ing)?|databases?|medline|pubmed|embase|cochrane\s+(?:library|central)|"
                     r"central|web\s+of\s+science|scopus|cinahl|clinicaltrials\.gov)\b", re.I)
_TO = re.compile(r"\b(?:to|until|till|through|thru|up\s+to|before|ending|end(?:ed)?\s+(?:on|in)?)\b|[-\u2010-\u2015]",
                 re.I)
_REGISTRY = re.compile(r"\bclinical\s*trials?\.gov\b|\bictrp\b|\btrials?\s+regist|\bregistr(?:y|ies)\b", re.I)
# a sentence about follow-up, enrolment or publication windows of the TRIALS is not the search period
_NOT_SEARCH = re.compile(r"\b(?:enrol(?:l)?(?:ed|ment)|follow(?:ed)?[- ]up|recruit|randomi[sz]ed\s+between|"
                         r"registered\s+(?:with|in|at)\s+prospero|prospero\s*(?:id|registration|number|:))\b", re.I)


def _sentences(text):
    return [s for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", re.sub(r"\s+", " ", text or "")) if s]


def _clause_before(s, start):
    """The text of the date's own clause before it: back to the previous ',', ';' or ' and '."""
    pre = s[max(0, start - 160):start]
    cut = max((m.end() for m in re.finditer(r"[,;]|\band\b", pre)), default=0)
    return pre[cut:]


# the review's OWN publication/acceptance in the date's clause ('and the review was published in March 2022')
_OWN_PUBLICATION = re.compile(r"\b(?:review|meta-analys[ie]s|article|manuscript|paper|study|protocol)\s+(?:was|is|has\s+"
                              r"been|were)\s+(?:first\s+)?(?:published|accepted|submitted|posted|registered|updated)\b",
                              re.I)


def _not_search_clause(s, at):
    """True when the date at offset `at` sits in a clause about enrolment, follow-up, PROSPERO registration or the
    review's own publication -- one rule for every date shape (month, numeric, year-only)."""
    c = _clause_before(s, at)
    return bool(_NOT_SEARCH.search(c) or _OWN_PUBLICATION.search(c))


def search_end(text):
    """(YYYY-MM or YYYY, precision, span) for the latest date in a sentence about the literature search that is
    reached by a 'to/until/through' connector, or None. Year-only ('inception to 2022') gives year precision. A date
    whose OWN clause is about enrolment, follow-up or PROSPERO registration is skipped -- not the whole sentence
    ('registered in PROSPERO in May 2021 and databases were searched up to April 2021' -> April 2021)."""
    best = None
    for s in _sentences(text):
        if not _SEARCH.search(s):
            continue
        for m in _DATE.finditer(s):
            pre = s[max(0, m.start() - 40):m.start()]
            if _not_search_clause(s, m.start()):
                continue
            if not _TO.search(pre) and not re.search(r"\b(?:on|in|as\s+of)\s*$", pre, re.I):
                continue
            y, mo = int(m.group(4)), MONTHS[m.group(2).lower()[:3]]
            if not 1980 <= y <= 2100:
                continue
            key = (y, mo)
            if best is None or key > best[0]:
                best = (key, "month", s[max(0, m.start() - 120):m.end() + 10].strip())
        # numeric dates: 'up to 02.02.2021' (D.M.Y; month taken only when day and month cannot be swapped or are
        # equal), 'before 2022.4.20' (Y.M.D)
        for m in re.finditer(r"\b(\d{4})[./-](\d{1,2})[./-](\d{1,2})\b|\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", s):
            pre = s[max(0, m.start() - 40):m.start()]
            if not _TO.search(pre) or _not_search_clause(s, m.start()):
                continue
            if m.group(1):
                y, mo = int(m.group(1)), int(m.group(2))
            else:
                a, b, y = int(m.group(4)), int(m.group(5)), int(m.group(6))
                mo = b if (a == b or a > 12) else None
            if not 1980 <= y <= 2100 or (mo is not None and not 1 <= mo <= 12):
                continue
            key, prec = ((y, mo), "month") if mo else ((y, 12), "year")
            if best is None or key > best[0]:
                best = (key, prec, s[max(0, m.start() - 120):m.end() + 10].strip())
        # year-only windows ('inception to 2022', 'during 2007 to 2015') are ALWAYS candidates: a later updated search
        # stated by year outranks an earlier month-dated one
        for m in re.finditer(r"\b(?:(?:inception|start)\s+(?:to|until|through)|(?:from|during|between)\s+(?:19|20)"
                             r"\d{2}\s*(?:to|until|through|and|-|–))\s*(\d{4})\b(?!\s*[./-]\d)", s, re.I):
            y = int(m.group(1))
            if _not_search_clause(s, m.end(1)):
                continue
            if 1980 <= y <= 2100 and (best is None or (y, 12) > best[0]):
                best = ((y, 12), "year", s[max(0, m.start() - 120):m.end() + 10].strip())
    if not best:
        return None
    (y, mo), prec, span = best
    return {"date": f"{y:04d}-{mo:02d}" if prec == "month" else f"{y:04d}", "precision": prec, "span": span[:200]}


_NEGATED = re.compile(r"\b(?:not|no|never|nor|without|excluding|except)\b", re.I)


def searched_registry(texts):
    """True when a search sentence names a trial registry in a clause that does not negate it ('We did not search
    ClinicalTrials.gov' -> False)."""
    for t in texts:
        for s in _sentences(t):
            if not _SEARCH.search(s):
                continue
            for c in re.split(r"[;,]|\bbut\b|\bwhile\b|\bwhereas\b", s):
                if _REGISTRY.search(c) and not _NEGATED.search(c):
                    return True
    return False


def _txt(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def _ymd(el):
    if el is None:
        return None
    y = _txt(el.find("Year"))
    m = _txt(el.find("Month"))
    d = _txt(el.find("Day"))
    if not y.isdigit():
        md = _txt(el.find("MedlineDate"))
        mm = re.match(r"(\d{4})\s*" + _MONTH + r"?", md, re.I)
        if not mm:
            return None
        y, m = mm.group(1), mm.group(2) or ""
    mo = int(m) if m.isdigit() else MONTHS.get(m.lower()[:3]) if m else None
    return (int(y), mo, int(d) if d.isdigit() else None)


def pubmed_dates(xml):
    """{'first_public': 'YYYY-MM[-DD]', 'basis': which date, 'abstract': text} from one PubMed XML record."""
    root = ET.fromstring(xml)
    art = root.find(".//PubmedArticle")
    if art is None:
        return None
    cands = []
    for ad in art.findall(".//ArticleDate"):
        v = _ymd(ad)
        if v:
            cands.append((v, f"ArticleDate:{ad.get('DateType') or ''}"))
    for pd in art.findall(".//PubmedData/History/PubMedPubDate"):
        if pd.get("PubStatus") in ("entrez", "pubmed"):
            v = _ymd(pd)
            if v:
                cands.append((v, f"PubMedPubDate:{pd.get('PubStatus')}"))
    v = _ymd(art.find(".//JournalIssue/PubDate"))
    if v:
        cands.append((v, "JournalIssue/PubDate"))
    if not cands:
        return {"first_public": None, "basis": None, "abstract": _abstract(art)}
    full = [c for c in cands if c[0][1]]
    yonly = [c for c in cands if not c[0][1]]
    best = min(full, key=lambda c: (c[0][0], c[0][1], c[0][2] or 99)) if full else None
    # a YEAR-only date earlier than every full date ('PubDate 2020', entrez 2021-02) is the first public date, at year
    # precision -- discarding it would date the report later than it was
    if yonly and (best is None or min(c[0][0] for c in yonly) < best[0][0]):
        (y, _, _), basis = min(yonly, key=lambda c: c[0][0])
        return {"first_public": f"{y:04d}", "basis": basis, "abstract": _abstract(art)}
    (y, mo, d), basis = best
    return {"first_public": f"{y:04d}-{mo:02d}" + (f"-{d:02d}" if d else ""), "basis": basis, "abstract": _abstract(art)}


def _abstract(art):
    return " ".join(_txt(a) for a in art.findall(".//Abstract/AbstractText"))


def fulltext_for(pmid, slug=None):
    """The comparator's cached full text (JATS or repository text) under cache/comparators/<pmid>/ ONLY -- regex
    only, never sent anywhere. The topic-level cache/<slug>/comparator_fulltext.txt is never read: it can hold a
    different (earlier or later) comparator's text, whose search dates are not this comparator's. (slug is unused.)"""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", str(pmid), "*"))):
        if f.endswith((".xml", ".txt")):
            t = open(f, encoding="utf-8", errors="replace").read()
            out.append((os.path.relpath(f, ROOT).replace("\\", "/"), re.sub(r"<[^>]+>", " ", t) if f.endswith(".xml") else t))
    return out


def results_posted(ncts, snap=None):
    snap = snap or os.environ.get("AACT_SNAPSHOT") or "F:/AACT-storage/AACT/2026-08-30"
    p = os.path.join(snap, "studies.txt")
    if not ncts:
        return {}
    if not os.path.isfile(p):
        # registry evidence that could not be checked is never 'no results posted'
        raise FileNotFoundError(f"{p}: AACT snapshot needed for registry results dates of {sorted(ncts)[:5]}")
    csv.field_size_limit(10 ** 9)
    out = {}
    with open(p, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh, delimiter="|")
        if "results_first_posted_date" not in (rd.fieldnames or []):
            raise ValueError(f"{p}: lacks results_first_posted_date")
        for r in rd:
            if r["nct_id"] in ncts and r.get("results_first_posted_date"):
                out[r["nct_id"]] = r["results_first_posted_date"][:10]
    return out


def _ym(s):
    p = [int(x) for x in s.split("-")]
    return p[0], (p[1] if len(p) > 1 else None)


def classify(first_public, end, comparator_public):
    """The verdict for one trial: first_public 'YYYY-MM[-DD]'; end {'date','precision'} or None."""
    if not first_public:
        return "TRIAL_DATE_NOT_RECORDED"
    ty, tm = _ym(first_public)
    if end:
        ey, em = _ym(end["date"])
        if end["precision"] == "year" or em is None or tm is None:
            return ("AFTER_COMPARATOR_SEARCH_END" if ty > ey else "NOT_EXPLAINED_BY_DATE" if ty < ey
                    else "SAME_PERIOD_AS_SEARCH_END")
        return ("AFTER_COMPARATOR_SEARCH_END" if (ty, tm) > (ey, em) else "NOT_EXPLAINED_BY_DATE" if (ty, tm) < (ey, em)
                else "SAME_PERIOD_AS_SEARCH_END")
    if comparator_public:
        cy, cm = _ym(comparator_public)
        if ty > cy or (ty == cy and tm and cm and tm > cm):
            return "PUBLISHED_AFTER_COMPARATOR"
    return "SEARCH_END_NOT_STATED"


TARGETS = os.path.join(ROOT, "registry", "comparator_search_dates_targets.json")


def targets():
    """(slug, comparator, ids) from the served G1 outputs UNION the recorded current-tracker list
    (registry/comparator_search_dates_targets.json, written by --from-tracker): main's code can pool a trial the
    served output does not list yet (colchicine-postop-af PMID 36286314), and it must have dates too."""
    acc = {}
    for f in sorted(glob.glob(os.path.join(G1, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        ids = [e["id"] for e in d.get("ours_not_in_comparator_detail") or []]
        if ids and d.get("comparator_pmid"):
            acc.setdefault((d["slug"], str(d["comparator_pmid"])), []).extend(ids)
    if os.path.isfile(TARGETS):
        for t in json.load(open(TARGETS, encoding="utf-8"))["targets"]:
            acc.setdefault((t["slug"], str(t["comparator"])), []).extend(t["ids"])
    return [(s, c, sorted(set(ids))) for (s, c), ids in sorted(acc.items())]


def tracker_targets():
    """The current tracker's own 'ours not in comparator' list for every served G1 topic (no network)."""
    sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
    import g1_tracker as gt
    T = gt.with_identity_chain(gt._j(os.path.join(gt.OUT, "k_gap_table.json")))
    out = []
    for f in sorted(glob.glob(os.path.join(G1, "*.json"))):
        s = json.load(open(f, encoding="utf-8"))["slug"]
        o = gt.topic(s, T)
        if o.get("ours_not_in_comparator") and o.get("comparator_pmid"):
            out.append({"slug": s, "comparator": str(o["comparator_pmid"]), "ids": list(o["ours_not_in_comparator"])})
    with open(TARGETS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"source": "g1_tracker.topic() on the current code", "targets": out}, fh, indent=1)
    return out


def fetch(pmids):
    sys.path.insert(0, ROOT)
    from harness import http
    os.makedirs(CACHE, exist_ok=True)
    for p in sorted(set(pmids)):
        f = os.path.join(CACHE, f"{p}.xml")
        if os.path.isfile(f):
            continue
        xml = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                            {"db": "pubmed", "id": p, "retmode": "xml", "tool": "meta-harness",
                             "email": "meta-harness@example.org"})
        if "<PubmedArticle" not in xml:
            raise RuntimeError(f"PMID {p}: efetch returned no PubmedArticle")
        with open(f, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(xml)


def _pm(p):
    f = os.path.join(CACHE, f"{p}.xml")
    return pubmed_dates(open(f, encoding="utf-8").read()) if os.path.isfile(f) else None


def build():
    T = targets()
    comps, trials = {}, {}
    nct_of = {}
    for slug, comp, ids in T:
        recs = {str(r.get("id")): r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"),
                                                             encoding="utf-8")).get("records", [])}
        for i in ids:
            p = i.replace("PMID ", "")
            if (recs.get(p) or {}).get("nct"):
                nct_of[p] = recs[p]["nct"]
    posted = results_posted(set(nct_of.values()))
    for slug, comp, ids in T:
        if comp not in comps:
            pm = _pm(comp)
            end = search_end(pm["abstract"]) if pm else None
            src = f"PubMed {comp} abstract" if end else None
            if not end:
                for path, text in fulltext_for(comp, slug):
                    end = search_end(text)
                    if end:
                        src = path
                        break
            texts = ([pm["abstract"]] if pm else []) + [t for _, t in fulltext_for(comp, slug)]
            reg_searched = searched_registry(texts)
            comps[comp] = {"comparator_first_public": pm and pm["first_public"], "first_public_basis": pm and pm["basis"],
                           "searched_trial_registry": reg_searched,
                           "search_end": end and end["date"], "precision": end and end["precision"],
                           "span": end and end["span"], "source": src, "topics": []}
        comps[comp]["topics"].append(slug)
        for i in ids:
            p = i.replace("PMID ", "")
            pm = _pm(p) if p.isdigit() else None
            cands = []
            if pm and pm["first_public"]:
                cands.append((pm["first_public"], f"PubMed {pm['basis']}"))
            n = nct_of.get(p)
            # registry results count only when the comparator's own search names a trial registry
            if n and posted.get(n) and comps[comp]["searched_trial_registry"]:
                cands.append((posted[n], f"AACT results_first_posted_date {n}"))
            fp = min(cands) if cands else (None, None)
            end = {"date": comps[comp]["search_end"], "precision": comps[comp]["precision"]} if comps[comp]["search_end"] else None
            trials[f"{slug}|{i}"] = {"slug": slug, "id": i, "comparator": comp, "first_public": fp[0], "basis": fp[1],
                                     "published": pm and pm["first_public"], "nct": n,
                                     # the verdict on the PUBLICATION date alone, beside the registry-inclusive one:
                                     # they differ when the registry posted results before the search end
                                     "why_by_publication_only": classify(pm and pm["first_public"], end,
                                                                         comps[comp]["comparator_first_public"]),
                                     "registry_results_posted": posted.get(n) if n else None,
                                     "why_not_in_comparator": classify(fp[0], end, comps[comp]["comparator_first_public"])}
    return {"rule": "R8-4: first public date (earliest of PubMed electronic/entrez/issue and registry results "
                    "posting) against the comparator's stated search end; never the year",
            "comparators": comps, "trials": trials}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--from-tracker" in argv:
        tracker_targets()
    if "--fetch" in argv:
        fetch([c for _, c, _ in targets()] + [i.replace("PMID ", "") for _, _, ids in targets() for i in ids
                                                if i.replace("PMID ", "").isdigit()])
    out = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    from collections import Counter
    print(json.dumps(Counter(t["why_not_in_comparator"] for t in out["trials"].values()), indent=1))
    for c, v in out["comparators"].items():
        print(c, v["search_end"], v["precision"], v["source"], "|", (v["span"] or "")[:110])
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
