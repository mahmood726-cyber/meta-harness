"""The non-PubMed retrieval route: a trial reported only in a journal PubMed does not index is retrieved through a
bibliographic/journal route and enters screening and the trial-family ledger as a typed JOURNAL record, instead of
staying a permanent unresolved item (V1.0.1, external review of the colchicine-POAF topic; fixture: Sarzaeem 2014,
Tehran Univ Med J 72:147-154).

A journal record lives in cache/<slug>/journal_records.json and is bound to a HELD copy of the journal's own article
page (sha256-checked). Every field the pipeline reads -- title, abstract, and any reported numbers -- must be located
verbatim in the rendered held page; a record that fails is refused (never silently dropped, never trusted).

Numbers read from an abstract's percentages are RECONSTRUCTED counts (count = round(percent x n)), checked to
round-trip to the printed percentage. They are recorded as the trial's target-result status RECONSTRUCTED and are
NOT POOLED until the full report is held (`full_report_held` true, with the report bound like any other source).
The record's identity for comparator matching is its bibliographic key, journal:year:volume:first page.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# a TAG is '<' + letter or '/', or a comment/PI/declaration -- a literal '<' in prose ('P< 0.001') is not a tag
_TAG = re.compile(r"<!--.*?-->|<\?.*?\?>|<![A-Za-z\[][^<>]*>|</?[A-Za-z][A-Za-z0-9:_-]*(?:\s[^<>]*)?/?>", re.S)


def render_html(raw: bytes) -> str:
    t = raw.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", t))).strip()


def bib_key(journal: str, year, volume, fpage) -> str:
    return f"bib:{re.sub(r'[^a-z0-9]', '', str(journal or '').lower())}:{year}:{volume}:{fpage}"


class JournalRecordRefused(ValueError):
    pass


def _located(text: str, quote: str, what: str) -> dict:
    i = text.find(quote)
    if i < 0:
        raise JournalRecordRefused(f"{what}: not printed in the held page: {quote[:80]!r}")
    return {"start": i, "end": i + len(quote), "quote": quote}


def validate(rec: dict, root: str = ROOT) -> dict:
    """Refuse a journal record unless its held page hashes, and its title, abstract and numbers are printed in it.
    Returns the record as the pipeline reads it (id, id_type 'journal', title, abstract, year, journal, bib_key...)."""
    held = rec.get("held") or {}
    path = os.path.join(root, held.get("document_ref") or "")
    if not held.get("document_ref") or not os.path.isfile(path):
        raise JournalRecordRefused(f"{rec.get('id')}: held page missing")
    raw = open(path, "rb").read()
    if hashlib.sha256(raw).hexdigest() != held.get("document_sha256"):
        raise JournalRecordRefused(f"{rec.get('id')}: held page hash mismatch")
    text = render_html(raw)
    want = bib_key(rec["journal"], rec["year"], rec["volume"], rec["first_page"])
    if rec.get("bib_key") != want or rec.get("id") != "JOURNAL:" + want[4:]:
        raise JournalRecordRefused(f"{rec.get('id')}: id/bib_key must be derived from journal/year/volume/first page")
    spans = {"title": _located(text, rec["title"], "title"),
             "citation": _located(text, rec["citation_as_printed"], "citation"),
             "abstract": _located(text, rec["abstract"], "abstract")}
    res = rec.get("result")
    if res:
        if res.get("state") not in ("RECONSTRUCTED",):
            raise JournalRecordRefused(f"{rec['id']}: unknown result state {res.get('state')!r}")
        for arm in ("intervention", "comparator"):
            a = res[arm]
            for k in ("percent_quote", "n_quote"):
                if a[k] not in rec["abstract"]:
                    raise JournalRecordRefused(f"{rec['id']}: {arm} {k} not in the held abstract: {a[k]!r}")
            if str(a["percent"]) not in a["percent_quote"] or str(a["n"]) not in a["n_quote"]:
                raise JournalRecordRefused(f"{rec['id']}: {arm} value not in its own quote")
            events = round(a["percent"] / 100 * a["n"])
            if events != a["events"] or round(100 * events / a["n"], 1) != a["percent"]:
                raise JournalRecordRefused(f"{rec['id']}: {arm} reconstruction does not round-trip "
                                           f"({a['events']}/{a['n']} vs {a['percent']}%)")
        if res.get("full_report_held") is not False:
            raise JournalRecordRefused(f"{rec['id']}: a RECONSTRUCTED result must say full_report_held false")
    out = {"id": rec["id"], "id_type": "journal", "title": rec["title"], "abstract": rec["abstract"],
           "year": str(rec["year"]), "journal": rec["journal"], "volume": str(rec["volume"]),
           "first_page": str(rec["first_page"]), "bib_key": want, "doi": rec.get("doi") or "", "nct": "",
           "pubtypes": [], "source": "journal_route", "found_by": [rec.get("route") or "journal_route"],
           "journal_route": {"held": held, "spans": spans, "result": res, "url": rec.get("url"),
                             "retrieval": rec.get("retrieval")}}
    return out


def load(root: str, slug: str) -> list:
    """The topic's validated journal records ([] when the topic declares none). A refused record raises."""
    p = os.path.join(root, "cache", slug, "journal_records.json")
    if not os.path.exists(p):
        return []
    return [validate(r, root) for r in json.load(open(p, encoding="utf-8"))]


def reconstructed(rec: dict) -> dict | None:
    """The RECONSTRUCTED result of a journal record, if any (the counts that stay out of the pool)."""
    res = ((rec or {}).get("journal_route") or {}).get("result")
    return res if res and res.get("state") == "RECONSTRUCTED" and not res.get("full_report_held") else None
