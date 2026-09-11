"""FDA reach adapter for drug-label and Drugs@FDA evidence records.

The public surface is intentionally small:

* fda_trials(drug_name) -> list of dictionaries with nct_or_id, title,
  indication, and source_url.

The adapter is stdlib-only and side-effect-free. It reads openFDA label and
drugsfda endpoints, which are cache-friendly HTTP GETs, and returns [] on
network or response-shape failure so an upstream reach run fails closed instead
of being mistaken for complete evidence.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request

LABEL_API = "https://api.fda.gov/drug/label.json"
DRUGSFDA_API = "https://api.fda.gov/drug/drugsfda.json"
UA = "meta-harness/1.0 (fda-reach; mailto:meta-harness@example.org)"

_NCT_RE = re.compile(r"\bNCT\d{8}\b", re.IGNORECASE)
_SECTION_RE = re.compile(
    r"\b(14(?:\.\d+)?)\s+(.+?)(?=\s+\b14(?:\.\d+)?\s+[A-Z]|$)",
    re.DOTALL,
)
def _url(base: str, params: dict[str, object]) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def _get_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"results": []}
        raise


def _dedupe_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        nct_or_id = record.get("nct_or_id", "")
        if nct_or_id.startswith("NCT"):
            key = ("NCT", nct_or_id, record.get("title", ""))
        elif nct_or_id.startswith("FDA_LABEL_"):
            key = ("FDA_LABEL", record.get("title", ""), record.get("indication", ""))
        else:
            key = (nct_or_id, record.get("title", ""), record.get("source_url", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(record)
    return out


def _clean(text: object) -> str:
    return " ".join(str(text or "").replace("\xa0", " ").split())


def _first(values: object) -> str:
    if isinstance(values, list) and values:
        return _clean(values[0])
    return _clean(values)


def _search_terms(drug_name: str) -> list[str]:
    drug = _clean(drug_name)
    if not drug:
        return []
    fields = ("openfda.brand_name", "openfda.generic_name", "openfda.substance_name")
    return [f'{field}:"{drug}"' for field in fields]


def _openfda_results(base: str, drug_name: str, limit: int = 100) -> list[dict]:
    out: list[dict] = []
    seen_payload_ids: set[str] = set()
    for search in _search_terms(drug_name):
        url = _url(base, {"search": search, "limit": limit})
        payload = _get_json(url)
        results = payload.get("results", [])
        if not isinstance(results, list):
            raise ValueError(f"openFDA response has non-list results for {base}")
        for item in results:
            if not isinstance(item, dict):
                raise ValueError(f"openFDA response item is not an object for {base}")
            stable_id = _clean(item.get("id")) or _clean(item.get("application_number"))
            if not stable_id:
                stable_id = json.dumps(item, sort_keys=True)[:300]
            if stable_id in seen_payload_ids:
                continue
            seen_payload_ids.add(stable_id)
            out.append(item)
    return out


def _record_url_for_label(label: dict) -> str:
    label_id = _clean(label.get("id"))
    if label_id:
        return _url(LABEL_API, {"search": f'id:"{label_id}"', "limit": 1})
    set_id = _clean(label.get("set_id"))
    if set_id:
        return _url(LABEL_API, {"search": f'set_id:"{set_id}"', "limit": 1})
    brand = _first((label.get("openfda") or {}).get("brand_name"))
    if brand:
        return _url(LABEL_API, {"search": f'openfda.brand_name:"{brand}"', "limit": 1})
    return LABEL_API


def _label_identifier(label: dict) -> str:
    return _clean(label.get("id")) or _clean(label.get("set_id")) or "unknown-label"


def _section_title(section_text: str) -> str:
    text = _clean(section_text)
    if not text:
        return "Clinical studies"
    text = _NCT_RE.sub("", text).replace("()", " ")
    for marker in (" Study 1 ", " Study 2 ", " Study 3 ", " The effects ", " In "):
        if marker in text:
            candidate = _clean(text.split(marker, 1)[0])
            if candidate:
                return candidate.strip(" .;:")
    stop_words = {
        "A",
        "An",
        "In",
        "Patients",
        "Subjects",
        "The",
        "This",
        "Two",
        "VASCEPA",
    }
    words = text.split()
    title_words: list[str] = []
    for word in words:
        bare = word.strip(" ,.;:")
        if title_words and (bare in stop_words or bare.lower() in {"was", "were", "is"}):
            break
        title_words.append(word)
        if len(title_words) >= 12:
            break
    title = _clean(" ".join(title_words)).strip(" .;:")
    return title or text[:120].strip()


def _trial_name_and_indication(section_body: str, nct_start: int) -> tuple[str, str]:
    left = _clean(section_body[:nct_start]).rstrip(" (")
    name_match = re.search(r"\b([A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+|[A-Z]{3,})\s*$", left)
    if not name_match:
        return "", _section_title(section_body)
    trial_name = name_match.group(1)
    indication = _clean(left[:name_match.start()]).strip(" .;:")
    return trial_name, indication or _section_title(section_body)


def _label_records(label: dict) -> list[dict[str, str]]:
    text = _first(label.get("clinical_studies"))
    if not text:
        return []

    source_url = _record_url_for_label(label)
    records: list[dict[str, str]] = []
    for section_number, section_body in _SECTION_RE.findall(text):
        section_body = _clean(section_body)
        if not section_body or section_body.upper() == "CLINICAL STUDIES":
            continue
        indication = _section_title(section_body)

        nct_hits = list(_NCT_RE.finditer(section_body))
        seen_ncts: set[str] = set()
        for match in nct_hits:
            nct = match.group(0).upper()
            if nct in seen_ncts:
                continue
            seen_ncts.add(nct)
            trial_name, nct_indication = _trial_name_and_indication(section_body, match.start())
            title = f"{trial_name}: {nct_indication}" if trial_name else ""
            if not title:
                title = f"{nct_indication} ({nct})"
            records.append(
                {
                    "nct_or_id": nct,
                    "title": title,
                    "indication": nct_indication,
                    "source_url": source_url,
                }
            )

        if not nct_hits:
            label_id = _label_identifier(label)
            records.append(
                {
                    "nct_or_id": f"FDA_LABEL_{label_id}_{section_number}",
                    "title": f"FDA label clinical-study section {section_number}: {indication}",
                    "indication": indication,
                    "source_url": source_url,
                }
            )

    return records


def _application_docs_records(application: dict) -> list[dict[str, str]]:
    app_no = _clean(application.get("application_number"))
    records: list[dict[str, str]] = []
    submissions = application.get("submissions", [])
    if not isinstance(submissions, list):
        raise ValueError("drugsfda response has non-list submissions")

    for submission in submissions:
        if not isinstance(submission, dict):
            raise ValueError("drugsfda submission is not an object")
        sub_type = _clean(submission.get("submission_type"))
        sub_no = _clean(submission.get("submission_number"))
        sub_class = _clean(submission.get("submission_class_code"))
        sub_desc = _clean(submission.get("submission_class_code_description"))
        is_evidence_submission = (
            sub_type == "ORIG"
            or sub_class == "EFFICACY"
            or sub_desc.lower() in {"efficacy", "type 5 - new formulation or new manufacturer"}
        )
        if not is_evidence_submission:
            continue
        docs = submission.get("application_docs", [])
        if not isinstance(docs, list):
            raise ValueError("drugsfda application_docs is not a list")
        for doc in docs:
            if not isinstance(doc, dict):
                raise ValueError("drugsfda application_doc is not an object")
            doc_type = _clean(doc.get("type"))
            if doc_type not in {"Review", "Summary Review", "Medical Review", "Statistical Review", "Label"}:
                continue
            doc_url = _clean(doc.get("url"))
            if not doc_url:
                continue
            doc_id = _clean(doc.get("id")) or "doc"
            stable_id = "-".join(part for part in [app_no, f"{sub_type}{sub_no}", doc_id] if part)
            records.append(
                {
                    "nct_or_id": stable_id,
                    "title": f"Drugs@FDA {doc_type} for {app_no} {sub_type}{sub_no}",
                    "indication": sub_desc or sub_class or "FDA approval evidence",
                    "source_url": doc_url,
                }
            )
    return records


def fda_trials(drug_name: str) -> list[dict[str, str]]:
    """Return FDA-reached trial/evidence records for a drug name.

    Each record has:
      * nct_or_id: NCT id when FDA labeling reports one, otherwise a stable
        FDA label/application document id.
      * title: trial/evidence title as recoverable from labeling or
        Drugs@FDA application metadata.
      * indication: FDA label section or submission class context.
      * source_url: openFDA record URL or Drugs@FDA document URL.

    The function returns [] for empty input, zero-hit searches, network errors,
    and unexpected source shapes. Callers that need diagnostics should wrap the
    lower-level helpers in this module; the public adapter fails closed by
    design.
    """
    if not _clean(drug_name):
        return []
    try:
        records: list[dict[str, str]] = []
        for label in _openfda_results(LABEL_API, drug_name):
            records.extend(_label_records(label))
        for application in _openfda_results(DRUGSFDA_API, drug_name):
            records.extend(_application_docs_records(application))
        return _dedupe_records(records)
    except Exception:  # noqa: BLE001 - fail closed; source completeness matters
        return []
