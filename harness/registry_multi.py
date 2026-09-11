"""Multi-registry reach adapter for condition x intervention searches.

Public surface:

* registry_multi(cond, intr) -> list of {registry, id, title, url}

Source posture:

* ISRCTN has an unauthenticated XML API and is parsed directly.
* EU-CTR has a public search/results website; this adapter uses conservative
  public HTML parsing because no stable JSON API is exposed there.
* ICTRP documents an XML web service, but WHO describes it as an agreed-partner
  cost-recovery service; the adapter only probes the public HTML search page and
  treats errors or unsupported markup as zero records for that source.

The module is side-effect-free and stdlib-only. Per-source failures do not raise
from registry_multi(); use registry_multi_with_status() for diagnostics.
"""
from __future__ import annotations

import html
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ISRCTN_API = "https://www.isrctn.com/api/query/format/who"
ISRCTN_RECORD = "https://www.isrctn.com/{trial_id}"
EUCTR_SEARCH = "https://www.clinicaltrialsregister.eu/ctr-search/search"
EUCTR_ROOT = "https://www.clinicaltrialsregister.eu"
ICTRP_SEARCH = "https://trialsearch.who.int/"
ICTRP_RECORD = "https://trialsearch.who.int/Trial2.aspx?TrialID={trial_id}"
UA = "meta-harness/1.0 (registry-multi; mailto:meta-harness@example.org)"

RAN_OK = "RAN_OK"
RAN_ZERO = "RAN_ZERO"
RAN_ERROR = "RAN_ERROR"

REGISTRY_NOTES = {
    "ISRCTN": "Unauthenticated XML API at https://www.isrctn.com/api/query/format/who.",
    "EU-CTR": "Public HTML search/results pages; no stable unauthenticated JSON API used here.",
    "ICTRP": "WHO web service/crawling access requires prior arrangement; public HTML probe only.",
}

_EUDRACT_RE = re.compile(r"\b\d{4}-\d{6}-\d{2}\b")
_ICTRP_ROW_RE = re.compile(r'<tr valign="top".*?</tr>', re.DOTALL)


def _url(base: str, params: dict[str, object]) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def _get_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8", "replace")


def _clean_text(value: object) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return " ".join(html.unescape(text).replace("\xa0", " ").split())


def _dedupe_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        registry = record.get("registry", "")
        trial_id = record.get("id", "")
        if not registry or not trial_id:
            continue
        key = (registry, trial_id)
        if key in seen:
            continue
        seen.add(key)
        out.append(record)
    return out


def _query_variants(cond: str, intr: str) -> list[str]:
    base = _clean_text(f"{intr} {cond}")
    if not base:
        return []

    variants = [base]
    replacements = [
        ("haemorrhage", "hemorrhage"),
        ("hemorrhage", "haemorrhage"),
        ("postpartum", "post-partum"),
        ("post-partum", "postpartum"),
        ("caesarean", "cesarean"),
        ("cesarean", "caesarean"),
    ]
    for old, new in replacements:
        for query in list(variants):
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            if pattern.search(query):
                variants.append(pattern.sub(new, query))
    return list(dict.fromkeys(variants))


def _parse_isrctn_xml(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    records: list[dict[str, str]] = []
    for trial in root.findall(".//trial"):
        main = trial.find("main")
        if main is None:
            continue
        trial_id = _clean_text(main.findtext("trial_id"))
        title = _clean_text(main.findtext("public_title")) or _clean_text(main.findtext("scientific_title"))
        url = _clean_text(main.findtext("url")) or ISRCTN_RECORD.format(trial_id=trial_id)
        if trial_id and title:
            records.append({"registry": "ISRCTN", "id": trial_id, "title": title, "url": url})
    return _dedupe_records(records)


def _isrctn_records(query: str, limit: int = 100, max_pages: int = 3) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for page in range(max_pages):
        offset = page * limit
        xml_text = _get_text(_url(ISRCTN_API, {"q": query, "limit": limit, "offset": offset}))
        page_records = _parse_isrctn_xml(xml_text)
        if not page_records:
            break
        out.extend(page_records)
        if len(page_records) < limit:
            break
        time.sleep(0.2)
    return _dedupe_records(out)


def _euctr_link(block: str, trial_id: str) -> str:
    hrefs = re.findall(r'href="([^"]+)"', block)
    trial_links = [href for href in hrefs if f"/ctr-search/trial/{trial_id}/" in href]
    result_links = [href for href in trial_links if href.endswith("/results")]
    chosen = (result_links or trial_links or [f"/ctr-search/trial/{trial_id}/results"])[0]
    if chosen.startswith("http"):
        return chosen
    return urllib.parse.urljoin(EUCTR_ROOT, chosen)


def _euctr_full_title(protocol_url: str) -> str:
    text = _clean_text(_get_text(protocol_url))
    match = re.search(r"Full title of the trial\s+(.+?)\s+A\.3\.1\b", text)
    return _clean_text(match.group(1)) if match else ""


def _parse_euctr_html(html_text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for block in html_text.split('<table class="result">')[1:]:
        id_match = re.search(r"EudraCT Number:</span>\s*([^<\s]+)", block)
        if not id_match:
            continue
        trial_id = _clean_text(id_match.group(1))
        if not _EUDRACT_RE.fullmatch(trial_id):
            continue
        title_match = re.search(r"Full Title:</span>\s*(.*?)\s*</td>", block, re.DOTALL)
        title = _clean_text(title_match.group(1)) if title_match else ""
        url = _euctr_link(block, trial_id)
        protocol_links = [
            urllib.parse.urljoin(EUCTR_ROOT, href)
            for href in re.findall(r'href="([^"]+)"', block)
            if f"/ctr-search/trial/{trial_id}/" in href and not href.endswith("/results")
        ]
        if ("..." in title or not title) and protocol_links:
            try:
                full_title = _euctr_full_title(protocol_links[0])
                if full_title:
                    title = full_title
            except Exception:  # noqa: BLE001 - detail enrichment only
                pass
        if title:
            records.append({"registry": "EU-CTR", "id": trial_id, "title": title, "url": url})
    return _dedupe_records(records)


def _euctr_records(query: str) -> list[dict[str, str]]:
    return _parse_euctr_html(_get_text(_url(EUCTR_SEARCH, {"query": query})))


def _parse_ictrp_html(html_text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row in _ICTRP_ROW_RE.findall(html_text):
        id_match = re.search(r"<span[^>]*Label1[^>]*>(.*?)</span>", row, re.DOTALL)
        title_match = re.search(
            r'<a[^>]+href="[^"]*Trial2\.aspx\?TrialID=([^"]+)"[^>]*>(.*?)</a>',
            row,
            re.DOTALL,
        )
        if not id_match or not title_match:
            continue
        trial_id = _clean_text(id_match.group(1))
        title = _clean_text(title_match.group(2))
        if trial_id and title:
            records.append(
                {
                    "registry": "ICTRP",
                    "id": trial_id,
                    "title": title,
                    "url": ICTRP_RECORD.format(trial_id=urllib.parse.quote(trial_id, safe="")),
                }
            )
    return _dedupe_records(records)


def _ictrp_records(query: str) -> list[dict[str, str]]:
    return _parse_ictrp_html(_get_text(_url(ICTRP_SEARCH, {"q": query})))


def registry_multi_with_status(cond: str, intr: str) -> dict[str, object]:
    """Return records plus per-source status diagnostics.

    This helper keeps source failures visible without changing the requested
    registry_multi(cond, intr) list-returning contract.
    """
    records: list[dict[str, str]] = []
    statuses: dict[str, dict[str, object]] = {}
    variants = _query_variants(cond, intr)
    if not variants:
        return {"records": [], "registries": {}, "queries": []}

    sources = {
        "ISRCTN": _isrctn_records,
        "EU-CTR": _euctr_records,
        "ICTRP": _ictrp_records,
    }
    for registry, search_fn in sources.items():
        source_records: list[dict[str, str]] = []
        source_error = ""
        for query in variants:
            try:
                source_records.extend(search_fn(query))
            except Exception as exc:  # noqa: BLE001 - fail closed per source
                source_error = repr(exc)[:200]
                break
            time.sleep(0.1)
        source_records = _dedupe_records(source_records)
        if source_error:
            statuses[registry] = {"status": RAN_ERROR, "n": 0, "note": source_error}
        else:
            statuses[registry] = {"status": RAN_OK if source_records else RAN_ZERO, "n": len(source_records)}
            records.extend(source_records)
    return {"records": _dedupe_records(records), "registries": statuses, "queries": variants}


def registry_multi(cond: str, intr: str) -> list[dict[str, str]]:
    """Return deduped registry records for condition x intervention.

    Per-registry network or parse errors are swallowed and visible through
    registry_multi_with_status(); this public function never raises for source
    reach failures.
    """
    result = registry_multi_with_status(cond, intr)
    records = result.get("records", [])
    return records if isinstance(records, list) else []

