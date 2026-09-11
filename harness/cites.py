"""Citation-chasing reach adapter.

Given a comparator paper, fetch its bibliography from Europe PMC and Crossref,
resolve cited works to PubMed IDs where possible, and return a deduped PMID list.

The module is intentionally side-effect-free and stdlib-only. Network/source
failures contribute no records for that source; use cite_chase_with_status() to
distinguish a true zero from RAN_ERROR.
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request

EPMC_REFERENCES = "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/references"
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF_WORK = "https://api.crossref.org/works/{doi}"

UA = "meta-harness/1.0 (citation-chase; mailto:meta-harness@example.org)"
SOURCE_EPMC_REFS = "europepmc-refs"
SOURCE_CROSSREF = "crossref"

RAN_OK = "RAN_OK"
RAN_ZERO = "RAN_ZERO"
RAN_ERROR = "RAN_ERROR"

_PMID_RE = re.compile(r"^\d+$")
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_RESOLUTION_CACHE: dict[tuple[str, str], dict[str, str] | None] = {}


def _get_json(url: str, params: dict[str, object] | None = None, timeout: int = 30) -> dict:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8"))
    finally:
        time.sleep(0.2)


def _clean_text(value: object) -> str:
    text = _TAG_RE.sub(" ", str(value or ""))
    return " ".join(html.unescape(text).replace("\xa0", " ").split())


def _normalise_pmid(value: object) -> str | None:
    text = str(value or "").strip()
    return text if _PMID_RE.fullmatch(text) else None


def _normalise_doi(value: object) -> str | None:
    text = str(value or "").strip()
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    text = text.strip().strip("<>\"' \t\r\n").rstrip(".,;")
    return text.lower() or None


def _reference_doi(reference: dict) -> str | None:
    doi = _normalise_doi(reference.get("doi") or reference.get("DOI"))
    if doi:
        return doi
    match = _DOI_RE.search(_clean_text(reference.get("unstructured")))
    return _normalise_doi(match.group(0)) if match else None


def _reference_title(reference: dict) -> str:
    for key in ("title", "article-title", "articleTitle", "citationTitle"):
        title = _clean_text(reference.get(key))
        if title:
            return title
    return ""


def _normalise_title(value: str) -> str:
    text = _clean_text(value).lower()
    text = text.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _title_matches(reference_title: str, candidate_title: str) -> bool:
    ref = _normalise_title(reference_title)
    cand = _normalise_title(candidate_title)
    if not ref or not cand:
        return False
    return ref == cand or (len(ref) >= 40 and (ref in cand or cand in ref))


def _title_query_variants(title: str) -> list[str]:
    cleaned = _clean_text(title).rstrip(".")
    variants = [cleaned]
    first_sentence = re.split(r"\.\s+", cleaned, maxsplit=1)[0].strip()
    if len(_normalise_title(first_sentence)) >= 20:
        variants.append(first_sentence)
    return list(dict.fromkeys(variants))


def _is_low_value_pubtype(result: dict) -> bool:
    pubtypes = ((result.get("pubTypeList") or {}).get("pubType") or [])
    bad = {"letter", "comment", "editorial", "news"}
    return any(str(pubtype).lower() in bad for pubtype in pubtypes)


def _epmc_search(query: str, page_size: int = 5, result_type: str = "core") -> list[dict]:
    payload = _get_json(
        EPMC_SEARCH,
        {
            "query": f"({query}) AND SRC:MED",
            "format": "json",
            "pageSize": page_size,
            "resultType": result_type,
        },
    )
    results = (payload.get("resultList") or {}).get("result") or []
    return results if isinstance(results, list) else []


def resolve_doi_to_pmid(doi: object) -> dict[str, str] | None:
    """Resolve a DOI to a PubMed-indexed Europe PMC record."""
    normalised = _normalise_doi(doi)
    if not normalised:
        return None
    key = ("doi", normalised)
    if key not in _RESOLUTION_CACHE:
        record = None
        for result in _epmc_search(f"DOI:{normalised}", page_size=1, result_type="lite"):
            pmid = _normalise_pmid(result.get("pmid") or result.get("id"))
            if pmid:
                record = {"pmid": pmid, "title": _clean_text(result.get("title"))}
                break
        _RESOLUTION_CACHE[key] = record
    return _RESOLUTION_CACHE[key]


def resolve_title_to_pmid(title: object) -> dict[str, str] | None:
    """Conservatively resolve a cited-reference title to a PubMed ID."""
    cleaned = _clean_text(title).rstrip(".")
    if len(_normalise_title(cleaned)) < 20:
        return None
    key = ("title", _normalise_title(cleaned))
    if key not in _RESOLUTION_CACHE:
        matches: list[dict] = []
        for variant in _title_query_variants(cleaned):
            safe_title = variant.replace('"', " ")
            for result in _epmc_search(f'TITLE:"{safe_title}"', page_size=5, result_type="core"):
                pmid = _normalise_pmid(result.get("pmid") or result.get("id"))
                if pmid and (
                    _title_matches(cleaned, _clean_text(result.get("title")))
                    or _title_matches(variant, _clean_text(result.get("title")))
                ):
                    matches.append(result)
            if matches:
                break
        preferred = [result for result in matches if not _is_low_value_pubtype(result)]
        chosen = (preferred or matches or [None])[0]
        if chosen:
            _RESOLUTION_CACHE[key] = {
                "pmid": str(chosen.get("pmid") or chosen.get("id")),
                "title": _clean_text(chosen.get("title")),
            }
        else:
            _RESOLUTION_CACHE[key] = None
    return _RESOLUTION_CACHE[key]


def _dedupe_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    by_pmid: dict[str, dict[str, str]] = {}
    for record in records:
        pmid = _normalise_pmid(record.get("pmid"))
        if not pmid:
            continue
        source = record.get("source", "")
        title = _clean_text(record.get("title"))
        if pmid not in by_pmid:
            merged = {"pmid": pmid, "title": title, "source": source}
            by_pmid[pmid] = merged
            out.append(merged)
            continue
        merged = by_pmid[pmid]
        if title and not merged.get("title"):
            merged["title"] = title
        sources = [part.strip() for part in merged.get("source", "").split(";") if part.strip()]
        if source and source not in sources:
            sources.append(source)
        merged["source"] = "; ".join(sources)
    return out


def _europepmc_reference_records(pmid: str, resolve_titles: bool = True) -> dict[str, object]:
    records: list[dict[str, str]] = []
    references_fetched = 0
    page_size = 1000

    for page in range(1, 4):
        payload = _get_json(
            EPMC_REFERENCES.format(pmid=pmid),
            {"format": "json", "pageSize": page_size, "page": page},
        )
        references = ((payload.get("referenceList") or {}).get("reference") or [])
        if not isinstance(references, list):
            references = []
        references_fetched += len(references)
        for reference in references:
            if not isinstance(reference, dict):
                continue
            ref_pmid = _normalise_pmid(reference.get("pmid"))
            if not ref_pmid and str(reference.get("source") or "").upper() == "MED":
                ref_pmid = _normalise_pmid(reference.get("id"))
            title = _reference_title(reference)
            if not ref_pmid:
                resolved = resolve_doi_to_pmid(_reference_doi(reference))
                if not resolved and resolve_titles and title:
                    resolved = resolve_title_to_pmid(title)
                if resolved:
                    ref_pmid = resolved["pmid"]
                    title = resolved.get("title") or title
            if ref_pmid:
                records.append({"pmid": ref_pmid, "title": title, "source": SOURCE_EPMC_REFS})
        if len(references) < page_size:
            break

    deduped = _dedupe_records(records)
    return {
        "records": deduped,
        "references_fetched": references_fetched,
        "resolved_to_pmid": len(records),
        "unique_pmids": len(deduped),
    }


def _crossref_reference_records(doi: str, resolve_titles: bool = True) -> dict[str, object]:
    quoted = urllib.parse.quote(doi, safe="")
    payload = _get_json(CROSSREF_WORK.format(doi=quoted))
    references = ((payload.get("message") or {}).get("reference") or [])
    if not isinstance(references, list):
        references = []

    records: list[dict[str, str]] = []
    for reference in references:
        if not isinstance(reference, dict):
            continue
        title = _reference_title(reference)
        resolved = resolve_doi_to_pmid(_reference_doi(reference))
        if not resolved and resolve_titles and title:
            resolved = resolve_title_to_pmid(title)
        if resolved:
            records.append(
                {
                    "pmid": resolved["pmid"],
                    "title": resolved.get("title") or title,
                    "source": SOURCE_CROSSREF,
                }
            )

    deduped = _dedupe_records(records)
    return {
        "records": deduped,
        "references_fetched": len(references),
        "resolved_to_pmid": len(records),
        "unique_pmids": len(deduped),
    }


def _source_result(source_fn, *args, **kwargs) -> dict[str, object]:
    try:
        result = source_fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - source reach fails closed
        return {
            "status": RAN_ERROR,
            "records": [],
            "references_fetched": 0,
            "resolved_to_pmid": 0,
            "unique_pmids": 0,
            "error": repr(exc)[:240],
        }
    status = RAN_OK if result.get("records") else RAN_ZERO
    return {"status": status, **result}


def cite_chase_with_status(
    pmid: object | None = None,
    doi: object | None = None,
    resolve_titles: bool = True,
) -> dict[str, object]:
    """Return deduped records plus per-source diagnostics.

    Records have the public shape {"pmid", "title", "source"}. Source errors are
    visible under "sources" and contribute no partial guesses.
    """
    clean_pmid = _normalise_pmid(pmid)
    clean_doi = _normalise_doi(doi)
    if not clean_pmid and not clean_doi:
        raise ValueError("cite_chase requires a PMID, a DOI, or both")

    sources: dict[str, dict[str, object]] = {}
    records: list[dict[str, str]] = []

    if clean_pmid:
        source = _source_result(_europepmc_reference_records, clean_pmid, resolve_titles=resolve_titles)
        sources[SOURCE_EPMC_REFS] = {k: v for k, v in source.items() if k != "records"}
        records.extend(source.get("records", []))

    if clean_doi:
        source = _source_result(_crossref_reference_records, clean_doi, resolve_titles=resolve_titles)
        sources[SOURCE_CROSSREF] = {k: v for k, v in source.items() if k != "records"}
        records.extend(source.get("records", []))

    deduped = _dedupe_records(records)
    status = RAN_ERROR if any(s.get("status") == RAN_ERROR for s in sources.values()) else (
        RAN_OK if deduped else RAN_ZERO
    )
    return {
        "status": status,
        "records": deduped,
        "sources": sources,
        "references_fetched": sum(int(s.get("references_fetched", 0)) for s in sources.values()),
        "resolved_to_pmid": sum(int(s.get("resolved_to_pmid", 0)) for s in sources.values()),
        "unique_pmids": len(deduped),
    }


def cite_chase(pmid: object | None = None, doi: object | None = None) -> list[dict[str, str]]:
    """Return cited references resolved to PMID, deduped by PMID."""
    result = cite_chase_with_status(pmid=pmid, doi=doi)
    records = result.get("records", [])
    return records if isinstance(records, list) else []


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Resolve comparator references to PubMed IDs.")
    parser.add_argument("--pmid")
    parser.add_argument("--doi")
    parser.add_argument("--no-title-resolve", action="store_true")
    args = parser.parse_args()
    result = cite_chase_with_status(args.pmid, args.doi, resolve_titles=not args.no_title_resolve)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
