"""Registry-first ClinicalTrials.gov -> PubMed enumeration spike.

The public surface is intentionally small:

* enumerate_nct(cond, intr) lists ClinicalTrials.gov NCT IDs for a condition x
  intervention query.
* nct_to_pmids(nct) resolves one registry trial to PubMed PMIDs from CT.gov
  referencesModule plus PubMed Secondary Source ID search.
* registry_first_pmids(cond, intr) wraps the above in a fail-closed status dict.

No paid APIs are used, and PubMed resolution uses esearch "<NCT>[si]" rather
than elink.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

try:  # Package import in normal use; direct script execution for the demo.
    from .http import get_json, get_text
except ImportError:  # pragma: no cover - convenience path for local spike runs
    ROOT_FOR_IMPORT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ROOT_FOR_IMPORT not in sys.path:
        sys.path.insert(0, ROOT_FOR_IMPORT)
    from harness.http import get_json, get_text


CTGOV = "https://clinicaltrials.gov/api/v2/studies"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "meta-harness"
EMAIL = "meta-harness@example.org"

RAN_OK = "RAN_OK"
RAN_ZERO = "RAN_ZERO"
RAN_ERROR = "RAN_ERROR"

_NCT_RE = re.compile(r"^NCT\d{8}$")
_PMID_RE = re.compile(r"^\d+$")


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _normalise_nct(nct: str) -> str:
    nct = str(nct or "").strip().upper()
    if not _NCT_RE.fullmatch(nct):
        raise ValueError(f"invalid NCT id: {nct!r}")
    return nct


def _normalise_pmid(pmid: object) -> str | None:
    text = str(pmid or "").strip()
    return text if _PMID_RE.fullmatch(text) else None


def enumerate_nct(cond: str, intr: str, page_size: int = 100) -> list[str]:
    """Return deduped NCT IDs from CT.gov v2 /studies query.cond/query.intr.

    HTTP and response-shape problems are allowed to raise; registry_first_pmids()
    converts them to RAN_ERROR so zero-hit searches are not confused with failed
    source access.
    """
    page_size = int(page_size)
    if page_size < 1:
        raise ValueError("page_size must be positive")

    out: list[str] = []
    seen: set[str] = set()
    page_token = None
    seen_tokens: set[str] = set()

    while True:
        params = {
            "query.cond": cond,
            "query.intr": intr,
            "pageSize": page_size,
            "fields": "protocolSection.identificationModule",
        }
        if page_token:
            params["pageToken"] = page_token

        payload = get_json(CTGOV, params)
        if not isinstance(payload, dict):
            raise ValueError("CT.gov /studies response was not a JSON object")
        studies = payload.get("studies", [])
        if not isinstance(studies, list):
            raise ValueError("CT.gov /studies response has non-list studies")

        for idx, study in enumerate(studies):
            if not isinstance(study, dict):
                raise ValueError(f"CT.gov study at index {idx} was not an object")
            nct = (((study.get("protocolSection") or {}).get("identificationModule") or {})
                   .get("nctId"))
            nct = _normalise_nct(nct)
            if nct not in seen:
                seen.add(nct)
                out.append(nct)

        next_token = payload.get("nextPageToken")
        if not next_token:
            break
        if not isinstance(next_token, str):
            raise ValueError("CT.gov nextPageToken was not a string")
        if next_token in seen_tokens:
            raise RuntimeError("CT.gov pagination repeated nextPageToken")
        seen_tokens.add(next_token)
        page_token = next_token
        time.sleep(0.2)

    return out


def _walk_pmids(value: object) -> list[str]:
    pmids: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() == "pmid":
                pmid = _normalise_pmid(child)
                if pmid:
                    pmids.append(pmid)
            elif isinstance(child, (dict, list)):
                pmids.extend(_walk_pmids(child))
    elif isinstance(value, list):
        for child in value:
            pmids.extend(_walk_pmids(child))
    return pmids


def _ctgov_reference_pmids(nct: str) -> list[str]:
    payload = get_json(f"{CTGOV}/{nct}", {"fields": "protocolSection.referencesModule"})
    if not isinstance(payload, dict):
        raise ValueError(f"CT.gov study response for {nct} was not a JSON object")
    protocol = payload.get("protocolSection")
    if not isinstance(protocol, dict):
        raise ValueError(f"CT.gov study response for {nct} has no protocolSection")
    references = protocol.get("referencesModule", {})
    if references in (None, ""):
        return []
    if not isinstance(references, dict):
        raise ValueError(f"CT.gov referencesModule for {nct} was not an object")
    return _dedupe(_walk_pmids(references))


def _pubmed_secondary_id_pmids(nct: str, retmax: int = 200) -> list[str]:
    pmids: list[str] = []
    retstart = 0
    count = None

    while count is None or retstart < count:
        payload = get_json(
            f"{EUTILS}/esearch.fcgi",
            {
                "db": "pubmed",
                "term": f'"{nct}"[si]',
                "retmode": "json",
                "retmax": retmax,
                "retstart": retstart,
                "tool": TOOL,
                "email": EMAIL,
            },
        )
        if not isinstance(payload, dict):
            raise ValueError(f"PubMed esearch response for {nct} was not an object")
        result = payload.get("esearchresult")
        if not isinstance(result, dict):
            raise ValueError(f"PubMed esearch response for {nct} has no esearchresult")
        if count is None:
            count = int(result.get("count", "0"))
        idlist = result.get("idlist")
        if idlist is None and count == 0:
            idlist = []
        if not isinstance(idlist, list):
            raise ValueError(f"PubMed esearch response for {nct} has non-list idlist")

        page_pmids = []
        for raw in idlist:
            pmid = _normalise_pmid(raw)
            if not pmid:
                raise ValueError(f"PubMed esearch returned invalid PMID for {nct}: {raw!r}")
            page_pmids.append(pmid)
        pmids.extend(page_pmids)

        if not page_pmids:
            break
        retstart += len(page_pmids)
        if retstart < count:
            time.sleep(0.34)

    return _dedupe(pmids)


def nct_to_pmids(nct: str) -> list[str]:
    """Return PMIDs linked to one NCT via CT.gov references and PubMed [si]."""
    nct = _normalise_nct(nct)
    pmids = _ctgov_reference_pmids(nct)
    time.sleep(0.2)
    pmids.extend(_pubmed_secondary_id_pmids(nct))
    return _dedupe(pmids)


# --- ISRCTN adapter (multi-registry) -------------------------------------------------
# ISRCTN is a WHO primary registry that indexes many UK/EU trials that never get an NCT.
# The free-text API (https://www.isrctn.com/api/query/format/default?q=...) returns an
# <allTrials> document in the 67bricks namespace; each trial's canonical id lives in the
# <trial publicIdentifierCanonical="ISRCTN########"> attribute. Free text is deliberately
# broad (reach, not precision) -- the screen decides eligibility downstream.

ISRCTN = "https://www.isrctn.com/api/query/format/default"
_ISRCTN_RE = re.compile(r"^ISRCTN\d{8}$")
_ISRCTN_CANONICAL_RE = re.compile(r'publicIdentifierCanonical="(ISRCTN\d{8})"')


def _normalise_isrctn(rid: str) -> str:
    rid = str(rid or "").strip().upper()
    if not _ISRCTN_RE.fullmatch(rid):
        raise ValueError(f"invalid ISRCTN id: {rid!r}")
    return rid


def _parse_isrctn_ids(xml_text: str) -> list[str]:
    """Pure parser: canonical ISRCTN ids from an <allTrials> API document. Namespace-agnostic
    (reads the publicIdentifierCanonical attribute), so a 67bricks-namespace change does not
    silently drop every id. Offline-testable against tests/fixtures/isrctn_sample.xml."""
    ids = _ISRCTN_CANONICAL_RE.findall(xml_text or "")
    if not ids:  # fall back to the <isrctn>NNNN</isrctn> element via ElementTree (namespace-tolerant)
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []
        for el in root.iter():
            if el.tag.rsplit("}", 1)[-1] == "isrctn":
                num = (el.text or "").strip()
                if num.isdigit() and len(num) == 8:
                    ids.append("ISRCTN" + num)
    return _dedupe(ids)


def enumerate_isrctn(cond: str, intr: str, limit: int = 100) -> list[str]:
    """Return deduped ISRCTN ids for a free-text query, paging by offset. ISRCTN's free-text q
    matches only when the whole string co-occurs, so a multi-term intervention+condition query is
    far too strict ('colchicine pericarditis' -> 0 while 'colchicine' -> 31). We therefore query by
    the INTERVENTION alone (the discriminating term) for reach, and let the screen enforce the
    condition downstream -- reach-first, precision-downstream, as everywhere in the harness.
    Raises on HTTP/parse trouble; the union wrapper converts that to a per-registry RAN_ERROR."""
    terms = (intr or cond or "").strip()
    if not terms:
        return []
    out: list[str] = []
    seen: set[str] = set()
    offset = 0
    while True:
        xml = get_text(ISRCTN, {"q": terms, "limit": limit, "offset": offset})
        m = re.search(r'totalCount="(\d+)"', xml or "")
        total = int(m.group(1)) if m else 0
        page = _parse_isrctn_ids(xml)
        for rid in page:
            if rid not in seen:
                seen.add(rid)
                out.append(rid)
        offset += limit
        if offset >= total or not page:
            break
        time.sleep(0.3)
    return out


def registry_id_to_pmids(rid: str) -> list[str]:
    """Resolve ANY WHO-registry id to PMIDs. PubMed's [si] field indexes NCT, ISRCTN, EudraCT,
    ChiCTR ... so the [si] search generalises across registries; for NCT we also read CT.gov
    referencesModule (ISRCTN publication links are not exposed as PMIDs by the API)."""
    rid = str(rid or "").strip().upper()
    pmids: list[str] = []
    if _NCT_RE.fullmatch(rid):
        pmids.extend(_ctgov_reference_pmids(rid))
        time.sleep(0.2)
    pmids.extend(_pubmed_secondary_id_pmids(rid))
    return _dedupe(pmids)


def registry_first_pmids(cond: str, intr: str, include_isrctn: bool = False) -> dict:
    """Return {'status': RAN_OK|RAN_ZERO|RAN_ERROR, 'pmids': [...], 'registries': {...}}.

    Unions enumeration across the enabled WHO registries (CT.gov always; ISRCTN when
    include_isrctn), each resolved to PMIDs via registry_id_to_pmids. Any HTTP or parse failure
    in ANY enabled registry is RAN_ERROR for the whole run, not RAN_ZERO -- a partial harvest must
    never be mistaken for source-complete evidence. Per-registry status is reported in 'registries'
    so a single flaky source is diagnosable (rate-limit != found-nothing)."""
    registries: dict[str, dict] = {}
    pmids: list[str] = []
    any_error = False
    # CT.gov
    try:
        ncts = enumerate_nct(cond, intr)
        cg = []
        for nct in ncts:
            cg.extend(nct_to_pmids(nct))
        cg = _dedupe(cg)
        registries["ctgov"] = {"status": RAN_OK if cg else RAN_ZERO, "n_ids": len(ncts), "n_pmids": len(cg)}
        pmids.extend(cg)
    except Exception:  # noqa: BLE001
        registries["ctgov"] = {"status": RAN_ERROR, "n_ids": 0, "n_pmids": 0}
        any_error = True
    # ISRCTN (optional)
    if include_isrctn:
        try:
            rids = enumerate_isrctn(cond, intr)
            ip = []
            for rid in rids:
                ip.extend(registry_id_to_pmids(rid))
                time.sleep(0.2)
            ip = _dedupe(ip)
            registries["isrctn"] = {"status": RAN_OK if ip else RAN_ZERO, "n_ids": len(rids), "n_pmids": len(ip)}
            pmids.extend(ip)
        except Exception:  # noqa: BLE001
            registries["isrctn"] = {"status": RAN_ERROR, "n_ids": 0, "n_pmids": 0}
            any_error = True
    pmids = _dedupe(pmids)
    if any_error:
        # Fail-closed: an incomplete union must not be mistaken for source-complete evidence.
        # Per-registry status is still reported so the caller can re-run only the flaky source.
        return {"status": RAN_ERROR, "pmids": [], "registries": registries}
    return {"status": RAN_OK if pmids else RAN_ZERO, "pmids": pmids, "registries": registries}


def _txt(el: ET.Element | None) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def _pubmed_titles(pmids: list[str]) -> dict[str, str]:
    titles: dict[str, str] = {}
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        if not chunk:
            continue
        xml = get_text(
            f"{EUTILS}/efetch.fcgi",
            {
                "db": "pubmed",
                "id": ",".join(chunk),
                "retmode": "xml",
                "tool": TOOL,
                "email": EMAIL,
            },
        )
        root = ET.fromstring(xml)
        for article in root.findall(".//PubmedArticle"):
            pmid = _normalise_pmid(_txt(article.find(".//PMID")))
            if pmid:
                titles[pmid] = _txt(article.find(".//ArticleTitle"))
        if i + 100 < len(pmids):
            time.sleep(0.34)
    return titles


def _existing_cache_pmids(path: str) -> set[str]:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    pmids: set[str] = set()
    for record in payload.get("records", []):
        if record.get("id_type") == "pmid":
            pmid = _normalise_pmid(record.get("id"))
            if pmid:
                pmids.add(pmid)
    return pmids


def omega3_demo(progress=None) -> dict:
    """Run the requested omega3 registry-first demo and return structured data."""
    cond = "cardiovascular"
    interventions = ["omega-3 fatty acid", "fish oil", "icosapent"]

    all_ncts: list[str] = []
    per_intervention = []
    for intr in interventions:
        ncts = enumerate_nct(cond, intr)
        per_intervention.append({"intervention": intr, "ncts": ncts, "nct_count": len(ncts)})
        all_ncts.extend(ncts)
        if progress:
            progress(f"{intr!r}: {len(ncts)} NCTs")
    all_ncts = _dedupe(all_ncts)
    if progress:
        progress(f"unique NCTs after synonym union: {len(all_ncts)}")

    nct_pmids: dict[str, list[str]] = {}
    all_pmids: list[str] = []
    for index, nct in enumerate(all_ncts, start=1):
        pmids = nct_to_pmids(nct)
        nct_pmids[nct] = pmids
        all_pmids.extend(pmids)
        if progress and (pmids or index == 1 or index % 25 == 0 or index == len(all_ncts)):
            progress(f"resolved {index}/{len(all_ncts)} {nct}: {len(pmids)} PMID(s)")
    all_pmids = _dedupe(all_pmids)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_path = os.path.join(root, "cache", "omega3-cardiovascular-events", "records.json")
    existing_pmids = _existing_cache_pmids(cache_path)
    delta_pmids = [pmid for pmid in all_pmids if pmid not in existing_pmids]
    if progress:
        progress(f"fetching titles for {len(delta_pmids)} candidate PMID(s)")
    titles = _pubmed_titles(delta_pmids)

    return {
        "condition": cond,
        "interventions": interventions,
        "per_intervention": per_intervention,
        "ncts": all_ncts,
        "nct_count": len(all_ncts),
        "nct_pmids": nct_pmids,
        "resolved_nct_count": sum(1 for pmids in nct_pmids.values() if pmids),
        "pmids": all_pmids,
        "pmid_count": len(all_pmids),
        "cache_path": os.path.relpath(cache_path, root).replace("\\", "/"),
        "cache_pmid_count": len(existing_pmids),
        "delta": [{"pmid": pmid, "title": titles.get(pmid, "")} for pmid in delta_pmids],
    }


def _print_omega3_demo() -> None:
    demo = omega3_demo(progress=lambda message: print(message, flush=True))
    print("registry-first omega3 demo")
    print(f"condition: {demo['condition']!r}")
    for row in demo["per_intervention"]:
        print(f"{row['intervention']!r}: {row['nct_count']} NCTs")
    print(f"unique NCTs enumerated: {demo['nct_count']}")
    print(f"NCTs resolved to >=1 PMID: {demo['resolved_nct_count']}")
    print(f"unique PMIDs resolved: {demo['pmid_count']}")
    print(f"existing cache PMIDs: {demo['cache_pmid_count']} ({demo['cache_path']})")
    print(f"candidate PMIDs not already in cache: {len(demo['delta'])}")
    for item in demo["delta"]:
        title = item["title"] or "(title unavailable)"
        print(f"{item['pmid']}\t{title}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    _print_omega3_demo()
