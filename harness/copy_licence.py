"""Which held copies a MODEL may read (5 Oct; reproducible_ai/record_licence.py is the after-the-fact check, this is the
before-the-call rule). A recorded model call stores its prompt in the public repo, so a prompt may carry a trial's full
text only when that copy is marked CC:
  PMC copy       the PMC permissions name a Creative Commons licence -> CC (cached in outputs/k_gap/fulltext_index.json as
                 copy_licence / copy_statement, terms only, the same field record_licence reads); an author manuscript,
                 a COVID-19 emergency deposit, 'all rights reserved' or unread terms -> not CC
  Unpaywall copy the location's license is cc-* or public-domain -> CC; anything else (None, publisher-specific, implied)
                 -> UPW_NOT_CC
Deterministic typed reading of a held copy (regex rungs) is unaffected: nothing it reads enters a record.
D8 (13 Oct): only CC BY / CC0 is 'CC' here. A NonCommercial / NoDerivatives / ShareAlike copy is CC_RESTRICTED, by the
ONE restriction pattern defined below and shared with reproducible_ai/record_licence (this module called every Creative Commons copy 'CC' in
three places: the PMC classifier, the cached index, Unpaywall -- pmc_licence('21115589'), CC BY-NC, returned 'CC')."""
from __future__ import annotations

import json
import os
import re
import time


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# The ONE licence rule (D8: only CC BY / CC0 enters a prompt). It lives HERE, in harness, because harness modules may
# not import the reproducible_ai package (tests/test_model_source.py); reproducible_ai/record_licence imports it from
# this module, so every licence reader still applies exactly one pattern (codex/agy d8lic-cap-r1).
# ONE restriction pattern for every licence reader (jats_licence, licences(), g1_trial_acquire.pmc_copy): three diverging
# copies let 'Non Commercial' (spaced) and 'no commercial reuse' through one reader or another (codex/agy d8lic-cap-r1)
_RESTRICTED_RE = re.compile(r"creativecommons\.org/licenses/by-(?:nc|nd|sa)|Non[- ]?Commercial|No[- ]?Deriv|Share[- ]?Alike|"
                            r"\bCC[ -]BY[ -](?:NC|ND|SA)\b|no[- ]commercial[- ]re-?use", re.I)
_HYPHENS = re.compile("[‐‑‒–—−­]")


class _Restricted:
    """search() on the statement as a READER sees it: entities unescaped ('Non&#x2011;Commercial') and every Unicode hyphen
    folded to '-' before matching -- the raw XML hid an NC licence behind a non-breaking hyphen (codex d8lic-cap-r2 #2)."""

    @staticmethod
    def search(text):
        import html as _html
        t = _HYPHENS.sub("-", _html.unescape(str(text or "")))
        # a line break inside the licence name ('Non\nCommercial', 'BY-\nNC') is no boundary (codex d8lic-cap-r3 #1)
        t = re.sub(r"-\s+", "-", re.sub(r"\s+", " ", t))
        return _RESTRICTED_RE.search(t)


_RESTRICTED = _Restricted()

_CC_URL = re.compile(r"creativecommons\.org/", re.I)
_CC_WORDS = re.compile(r"Creative\s+Commons|\bCC[ -]BY", re.I)
_NEGATED = re.compile(r"\b(?:not|no|neither|nor|without|never|isn't|aren't)\b[^.;]{0,40}$", re.I)


def names_creative_commons(perm: str) -> bool:
    """True when a permissions statement GRANTS a Creative Commons licence: a creativecommons.org licence link, or the
    words with no negation before them in the same clause. 'not distributed under a Creative Commons licence' names it
    only to deny it (codex d8x-cap-r2 #1): such a copy is closed, never CC_RESTRICTED (which typed readers accept)."""
    t = str(perm or "")
    if _CC_URL.search(t):
        return True
    return any(not _NEGATED.search(t[max(0, m.start() - 60):m.start()]) for m in _CC_WORDS.finditer(t))


def _is_open(licence):
    """D8: CC BY or CC0 only. Any string starting with 'cc' let Unpaywall's 'cc-by-nc' / 'cc-by-nc-nd' / 'cc-by-sa' open a
    prompt (D8 incident #2, 12 Oct)."""
    lic = str(licence or "").strip().lower()
    return lic == "cc" or bool(re.fullmatch(r"cc[- ]?by(?:[- ]\d(?:\.\d)?)?|cc0(?:[- ]\d(?:\.\d)?)?", lic))

INDEX = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")


def classify_permissions(xml: str) -> tuple:
    """(licence, statement) from a PMC article XML's <permissions> -- the rule g1_trial_acquire.pmc_copy applies."""
    perm = " ".join(re.findall(r"<permissions>.*?</permissions>", xml or "", re.S))
    stmt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", perm)).strip()[:300] or None
    # CC_RESTRICTED is a Creative Commons licence that restricts reuse: the permissions must NAME Creative Commons. A closed
    # copy that merely says 'Non-commercial use only' is NOT_OPEN (agy d8x-cap-r1-agy: typed readers accept
    # CC_RESTRICTED, so the closed copy would have been read)
    if _RESTRICTED.search(perm) and names_creative_commons(perm):
        return "CC_RESTRICTED", stmt
    if re.search(r"creativecommons\.org/(?:licenses/by/|publicdomain/)", perm):
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
        # a cached 'CC' whose own recorded statement names a restriction is CC_RESTRICTED (record_licence.licences)
        if e["copy_licence"] == "CC" and _RESTRICTED.search(str(e.get("copy_statement") or "")):
            return "CC_RESTRICTED"
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
    with open(index_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(idx, fh, indent=1, sort_keys=True)
    return lic


def upw_open(u: dict) -> bool:
    """CC BY / CC0 / public domain only ('cc-by-nc', 'cc-by-nd', 'cc-by-sa' started with 'cc' and were open)."""
    lic = str((u or {}).get("license") or "").lower()
    return _is_open(lic) or lic in ("public-domain", "pd")


def locator_text(rec: dict, ft: str, licence, pmid) -> tuple:
    """(text shown to the locator, its input-digest ref). Full text only from a CC copy; otherwise title + abstract."""
    base = (rec.get("title") or "") + "\n" + (rec.get("abstract") or "")
    if ft and licence == "CC":
        return base + "\n\n" + ft, f"trial report PMID {pmid} (abstract + CC full text)"
    return base, f"trial report PMID {pmid} (abstract only; held copy not CC: {licence})"


TYPED_OPEN = ("CC", "CC_RESTRICTED", "PMC_AUTHOR_MANUSCRIPT")   # D8 governs model prompts, not typed reads


def typed_may_read(licence) -> bool:
    """A deterministic (typed / regex) reader admits a value from a held full text only when the copy is CC or a PMC
    author manuscript (text mining permitted) -- the rule g1/finish-line's table reader applies (HELD_COPY_NOT_OPEN)."""
    return licence in TYPED_OPEN
