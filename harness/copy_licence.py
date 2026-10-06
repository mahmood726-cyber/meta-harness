"""Which held copies a MODEL may read (5 Oct; reproducible_ai/record_licence.py is the after-the-fact check, this is the
before-the-call rule). A recorded model call stores its prompt in the public repo, so a prompt may carry a trial's full
text only when that copy is marked CC:
  PMC copy       the PMC permissions name a Creative Commons licence -> CC (cached in outputs/k_gap/fulltext_index.json as
                 copy_licence / copy_statement, terms only, the same field record_licence reads); an author manuscript,
                 a COVID-19 emergency deposit, 'all rights reserved' or unread terms -> not CC
  Unpaywall copy the location's license is cc-* or public-domain -> CC; anything else (None, publisher-specific, implied)
                 -> UPW_NOT_CC
Deterministic typed reading of a held copy (regex rungs) is unaffected: nothing it reads enters a record."""
from __future__ import annotations

import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")


def classify_permissions(xml: str) -> tuple:
    """(licence, statement) from a PMC article XML's <permissions> -- the rule g1_trial_acquire.pmc_copy applies."""
    perm = " ".join(re.findall(r"<permissions>.*?</permissions>", xml or "", re.S))
    stmt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", perm)).strip()[:300] or None
    if re.search(r"creativecommons\.org/(?:licenses|publicdomain)/", perm):
        return "CC", stmt
    if re.search(r"available for text mining", stmt or "", re.I) and re.search(r"\bmanuscript\b", xml or "", re.I):
        return "PMC_AUTHOR_MANUSCRIPT", stmt
    return "NOT_OPEN", stmt


def _pmcid(pmid):
    from harness import http
    b = http.get_text("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                      {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "lite"})
    r = (json.loads(b).get("resultList") or {}).get("result") or []
    return r[0].get("pmcid") if r else None


def pmc_licence(pmid, run=True, index_path=INDEX):
    """'CC' / 'PMC_AUTHOR_MANUSCRIPT' / 'NOT_OPEN' / 'NO_PMCID' for a PMID's PMC copy; unread terms are never open."""
    pmid = str(pmid)
    idx = json.load(open(index_path, encoding="utf-8")) if os.path.exists(index_path) else {}
    e = idx.get(pmid) or {}
    if e.get("copy_licence"):
        return e["copy_licence"]
    if not run:
        return "NOT_OPEN"
    from harness import http, fetch
    try:
        pmcid = e.get("pmcid") or _pmcid(pmid)
    except Exception:  # noqa: BLE001
        return "NOT_OPEN"
    if not pmcid:
        lic, stmt = "NO_PMCID", None
    else:
        xml = ""
        for attempt in range(3):
            try:
                time.sleep(0.4 + attempt)
                xml = http.get_text(f"{fetch.EUTILS}/efetch.fcgi", {"db": "pmc", "id": pmcid, "retmode": "xml",
                                                                    "tool": "meta-harness",
                                                                    "email": "meta-harness@example.org"})
                break
            except Exception:  # noqa: BLE001
                xml = ""
        if not xml:
            return "NOT_OPEN"
        lic, stmt = classify_permissions(xml)
    idx = json.load(open(index_path, encoding="utf-8")) if os.path.exists(index_path) else {}
    idx.setdefault(pmid, {}).update(copy_licence=lic, copy_statement=stmt, **({"copy_pmcid": pmcid} if pmcid else {}))
    # ATOMIC: concurrent readers (the licence guard, other jobs) must never see a half-written index
    tmp = f"{index_path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(idx, fh, indent=1, sort_keys=True)
    os.replace(tmp, index_path)
    return lic


def upw_open(u: dict) -> bool:
    lic = str((u or {}).get("license") or "").lower()
    return lic.startswith("cc") or lic in ("public-domain", "pd")


def locator_text(rec: dict, ft: str, licence, pmid) -> tuple:
    """(text shown to the locator, its input-digest ref). Full text only from a CC copy; otherwise title + abstract."""
    base = (rec.get("title") or "") + "\n" + (rec.get("abstract") or "")
    if ft and licence == "CC":
        return base + "\n\n" + ft, f"trial report PMID {pmid} (abstract + CC full text)"
    return base, f"trial report PMID {pmid} (abstract only; held copy not CC: {licence})"


TYPED_OPEN = ("CC", "PMC_AUTHOR_MANUSCRIPT")


def typed_may_read(licence) -> bool:
    """A deterministic (typed / regex) reader admits a value from a held full text only when the copy is CC or a PMC
    author manuscript (text mining permitted) -- the rule g1/finish-line's table reader applies (HELD_COPY_NOT_OPEN)."""
    return licence in TYPED_OPEN
