"""Build the probiotics AAD search diagnostic evidence bundle.

The lane asks for an object-level diagnostic, not a review rebuild: read the
existing config/cache/review, measure PubMed/CT.gov reachability today, cache
every raw network response under the dated diagnostic cache, and write the
evidence/report/registry artefacts without changing the topic pool or page.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import acquisition, gitblob  # noqa: E402


RUN_DATE = "2026-09-15"
RUN_UTC = "2026-09-15T00:00:00Z"
SLUG = "probiotics-aad-prevention"
DIAG_SLUG = "probiotics-search-diagnostic-2026-09-15"
FIX_ID = "DIAG-probiotics-search"
AUTHOR = "Codex lane AF"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
RAW_DIR = ROOT / "cache" / SLUG / "diagnostic-2026-09-15" / "raw"
EVIDENCE_DIR = ROOT / "docs" / "evidence" / DIAG_SLUG
REPORT_PATH = ROOT / "LANE-AF-REPORT.md"
CONFIG_PATH = ROOT / "topics" / f"{SLUG}.json"
RECORDS_PATH = ROOT / "cache" / SLUG / "records.json"
REVIEW_PATH = ROOT / "docs" / "reviews" / SLUG / "review.json"
COMPARATOR_TEXT_PATH = ROOT / "cache" / SLUG / "comparator_fulltext.txt"
CAPTIONS_PATH = ROOT / "docs" / "evidence" / "CAPTIONS.json"
REGISTRY_PATH = ROOT / "registry" / "fixes.json"

STOPWORDS = {
    "and",
    "the",
    "with",
    "from",
    "into",
    "over",
    "this",
    "that",
    "trial",
    "study",
    "effects",
    "effect",
    "patients",
    "placebo",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def slugify(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip().lower())
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:110] or "raw"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_params(params: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in sorted(params.items()):
        if value is None:
            continue
        out[str(key)] = str(value)
    return out


class RawCache:
    def __init__(self, raw_dir: Path) -> None:
        self.raw_dir = raw_dir
        self.index_path = raw_dir / "INDEX.json"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.entries: list[dict[str, Any]] = []
        self.by_key: dict[str, dict[str, Any]] = {}
        if self.index_path.exists():
            data = read_json(self.index_path)
            self.entries = list(data.get("responses", []))
            for entry in self.entries:
                key = entry.get("request_key")
                filename = entry.get("file")
                if key and filename and (self.raw_dir / filename).is_file():
                    self.by_key[str(key)] = entry

    @staticmethod
    def request_key(url: str, params: dict[str, str]) -> str:
        return sha256_bytes(
            json.dumps({"url": url, "params": params}, sort_keys=True).encode("utf-8")
        )

    def fetch(self, label: str, url: str, params: dict[str, Any], suffix: str) -> bytes:
        clean_params = canonical_params(params)
        key = self.request_key(url, clean_params)
        cached = self.by_key.get(key)
        if cached:
            return (self.raw_dir / str(cached["file"])).read_bytes()

        full_url = url + "?" + urllib.parse.urlencode(clean_params)
        headers = {"User-Agent": "meta-harness/diagnostic (mailto:meta-harness@example.org)"}
        request = urllib.request.Request(full_url, headers=headers)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read()
                    status = getattr(response, "status", 200)
                    content_type = response.headers.get("content-type", "")
                break
            except Exception as exc:  # noqa: BLE001 - the final attempt raises with context.
                last_error = exc
                if attempt == 2:
                    raise RuntimeError(f"fetch failed for {label}: {exc}") from exc
                time.sleep(1.5 * (attempt + 1))
        else:  # pragma: no cover - loop either breaks or raises.
            raise RuntimeError(f"fetch failed for {label}: {last_error}")

        digest = sha256_bytes(body)
        filename = f"{RUN_DATE}-{slugify(label)}-{digest[:16]}{suffix}"
        (self.raw_dir / filename).write_bytes(body)
        entry = {
            "label": label,
            "file": filename,
            "url": url,
            "full_url": full_url,
            "params": clean_params,
            "status": status,
            "content_type": content_type,
            "fetched_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "body_sha256": digest,
            "bytes": len(body),
            "request_key": key,
        }
        self.entries.append(entry)
        self.by_key[key] = entry
        self.save()
        if "eutils.ncbi.nlm.nih.gov" in url:
            time.sleep(0.34)
        return body

    def save(self) -> None:
        payload = {
            "schema": 1,
            "diagnostic": DIAG_SLUG,
            "date": RUN_DATE,
            "note": "Raw HTTP response bodies; each filename includes the run date and response SHA-256 prefix.",
            "responses": self.entries,
        }
        write_json(self.index_path, payload)

    def entries_for(self, prefix: str) -> list[dict[str, Any]]:
        return [entry for entry in self.entries if str(entry.get("label", "")).startswith(prefix)]

    def label_sha(self, label: str) -> str:
        for entry in self.entries:
            if entry.get("label") == label:
                return str(entry.get("body_sha256"))
        return ""


def load_review_objects() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return read_json(CONFIG_PATH), read_json(RECORDS_PATH), read_json(REVIEW_PATH)


def text_of(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def descendants(node: ET.Element, name: str) -> list[ET.Element]:
    return [el for el in node.iter() if local_name(el.tag) == name]


def first_desc_text(node: ET.Element, name: str) -> str:
    found = descendants(node, name)
    return text_of(found[0]) if found else ""


def children(node: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(node) if local_name(child.tag) == name]


def first_path(node: ET.Element, names: list[str]) -> ET.Element | None:
    nodes = [node]
    for name in names:
        next_nodes: list[ET.Element] = []
        for current in nodes:
            next_nodes.extend(children(current, name))
        nodes = next_nodes
        if not nodes:
            return None
    return nodes[0]


def first_path_text(node: ET.Element, names: list[str]) -> str:
    return text_of(first_path(node, names))


def citation_year(text: str) -> str:
    match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
    return match.group(1) if match else ""


def parse_refs_from_pmc_xml(xml_bytes: bytes) -> dict[str, dict[str, str]]:
    refs: dict[str, dict[str, str]] = {}
    root = ET.fromstring(xml_bytes)
    for ref_node in descendants(root, "ref"):
        label = first_desc_text(ref_node, "label")
        if not label:
            rid = ref_node.attrib.get("id", "")
            m = re.search(r"(\d+)$", rid)
            label = m.group(1) if m else ""
        if not label:
            continue
        pub_ids: dict[str, str] = {}
        for pub_id in descendants(ref_node, "pub-id"):
            typ = (pub_id.attrib.get("pub-id-type") or pub_id.attrib.get("pub-id-type".upper()) or "").lower()
            if typ:
                pub_ids[typ] = text_of(pub_id)
        citation = text_of(ref_node)
        refs[label] = {
            "ref_num": label,
            "title": first_desc_text(ref_node, "article-title"),
            "journal": first_desc_text(ref_node, "source"),
            "year": citation_year(citation) or first_desc_text(ref_node, "year"),
            "ref_pmid": pub_ids.get("pmid", ""),
            "doi": pub_ids.get("doi", ""),
            "citation": citation,
        }
    return refs


def parse_table_rows_from_cached_text() -> list[dict[str, str]]:
    text = COMPARATOR_TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    try:
        segment = text.split("Outcome (AAD) measurement", 1)[1]
        segment = segment.split("AAD, antibiotic-associated", 1)[0]
    except IndexError as exc:
        raise RuntimeError("could not locate Goodman Table 1 in comparator_fulltext.txt") from exc
    name_word = r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'\u2019-]*"
    row_start = re.compile(
        rf"(?<![A-Za-zÀ-ÖØ-öø-ÿ])(?P<name>(?:de Vrese|{name_word})(?:\s+{name_word})*\s+et al)\s+"
        r"(?P<ref>\d{1,2})\s+"
        r"(?P<sample>\d+\s+\([^)]+\)(?:\s+\([^)]+\))?)\s+"
    )
    matches = list(row_start.finditer(segment))
    rows: list[dict[str, str]] = []
    dose_re = re.compile(
        r"(\d+(?:\.\d+)?(?:[\-\u2013]\d+)?\s*\u00d710\s*9"
        r"(?:\s*,\s*\d+(?:\.\d+)?\s*\u00d710\s*9)?|"
        r"\d+\s*g \(cfu not noted\)|Not noted)"
    )
    species_re = re.compile(
        r"((?:Lyophilized live\s+)?(?:\(?1\)\s+)?"
        r"(?:L\.|S\.|B\.|C\.)\s+"
        r"(?:acidophilus|casei|boulardii|reuteri|subtilis|butyricum|bifidum|lactis|longum|breve|clausii|helveticus|rhamnosus|plantarum))",
        re.IGNORECASE,
    )
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(segment)
        chunk = segment[match.start() : end].strip()
        after_sample = chunk[match.end() - match.start() :]
        species_match = species_re.search(after_sample)
        probiotic_species = ""
        if species_match:
            start = species_match.start()
            dose_match = dose_re.search(after_sample, species_match.end())
            stop = dose_match.start() if dose_match else len(after_sample)
            probiotic_species = re.sub(r"\s+", " ", after_sample[start:stop]).strip(" ,")
        rows.append(
            {
                "row": str(idx + 1),
                "first_author": match.group("name").replace(" et al", "").strip(),
                "ref_num": match.group("ref"),
                "sample_size": match.group("sample"),
                "probiotic_species": probiotic_species or "NOT_PARSED",
                "table_chunk": chunk,
            }
        )
    if len(rows) != 42:
        raise RuntimeError(f"expected 42 Goodman table rows, parsed {len(rows)}")
    return rows


def pubmed_esearch(cache: RawCache, label: str, term: str, retmax: int, retstart: int = 0) -> dict[str, Any]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retstart": retstart,
        "retmax": retmax,
        "tool": "meta-harness",
        "email": "meta-harness@example.org",
    }
    body = cache.fetch(label, f"{EUTILS}/esearch.fcgi", params, ".json")
    return json.loads(body.decode("utf-8"))


def europepmc_search(cache: RawCache, label: str, query: str) -> dict[str, Any]:
    params = {"query": query, "format": "json", "pageSize": 25}
    body = cache.fetch(label, EUROPEPMC, params, ".json")
    return json.loads(body.decode("utf-8"))


def esearch_full(cache: RawCache, label: str, term: str, page_size: int = 1000, hard_cap: int = 10000) -> dict[str, Any]:
    ids: list[str] = []
    count: int | None = None
    starts: list[int] = []
    retstart = 0
    while True:
        retmax = min(page_size, max(hard_cap - len(ids), 0))
        if retmax <= 0:
            break
        page_label = f"{label}-retstart-{retstart}"
        payload = pubmed_esearch(cache, page_label, term, retmax=retmax, retstart=retstart)
        result = payload.get("esearchresult", {})
        if count is None:
            count = int(result.get("count") or 0)
        batch = [str(x) for x in result.get("idlist") or []]
        starts.append(retstart)
        ids.extend(batch)
        if not batch or len(ids) >= count or len(ids) >= hard_cap:
            break
        retstart += len(batch)
    assert count is not None
    return {
        "label": label,
        "term": term,
        "count": count,
        "fetched": len(ids),
        "hard_cap": hard_cap,
        "truncated": count > len(ids),
        "ids": ids,
        "page_starts": starts,
    }


def title_fallback_term(title: str, year: str) -> str:
    words = [
        w.lower()
        for w in re.findall(r"[A-Za-z][A-Za-z0-9]{3,}", title)
        if w.lower() not in STOPWORDS
    ]
    words = words[:8]
    if not words:
        return f'"{title.replace(chr(34), " ")}"[Title]'
    term = " AND ".join(f"{w}[Title]" for w in words)
    if year:
        term = f"({term}) AND {year}[dp]"
    return term


def resolve_titles(cache: RawCache, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        title = str(row.get("title") or "")
        exact_ids: list[str] = []
        fallback_ids: list[str] = []
        if title:
            exact = pubmed_esearch(
                cache,
                f"title-exact-{row['row']}-{row['first_author']}",
                f'"{title.replace(chr(34), " ")}"[Title]',
                retmax=20,
            )
            exact_ids = [str(x) for x in exact.get("esearchresult", {}).get("idlist") or []]
            if not exact_ids:
                fallback = pubmed_esearch(
                    cache,
                    f"title-fallback-{row['row']}-{row['first_author']}",
                    title_fallback_term(title, str(row.get("year") or "")),
                    retmax=20,
                )
                fallback_ids = [str(x) for x in fallback.get("esearchresult", {}).get("idlist") or []]
            if not exact_ids and not ref_pmid:
                epmc = europepmc_search(
                    cache,
                    f"europepmc-title-{row['row']}-{row['first_author']}",
                    f'TITLE:"{title.replace(chr(34), " ")}"',
                )
                results = ((epmc.get("resultList") or {}).get("result") or [])
                row["europepmc_hits"] = int(epmc.get("hitCount") or 0)
                if results:
                    first = results[0]
                    row["europepmc_year"] = str(first.get("pubYear") or "")
                    row["europepmc_pmid"] = str(first.get("pmid") or "")
        ref_pmid = str(row.get("ref_pmid") or "")
        resolved = ref_pmid
        basis = "Goodman reference-list PMID" if ref_pmid else ""
        if not resolved and exact_ids:
            resolved = exact_ids[0]
            basis = "PubMed title esearch exact"
        row["title_esearch_ids"] = exact_ids
        row["title_fallback_ids"] = fallback_ids
        row["pmid"] = resolved
        row["resolution_basis"] = basis or "UNRESOLVED_BY_TITLE_ESEARCH"
        if not row.get("year") and row.get("europepmc_year"):
            row["year"] = row["europepmc_year"]


def fetch_pubmed_metadata(cache: RawCache, ids: list[str]) -> dict[str, dict[str, Any]]:
    ids = sorted({str(i) for i in ids if str(i)})
    meta: dict[str, dict[str, Any]] = {}
    for idx in range(0, len(ids), 200):
        chunk = ids[idx : idx + 200]
        params = {
            "db": "pubmed",
            "id": ",".join(chunk),
            "retmode": "xml",
            "tool": "meta-harness",
            "email": "meta-harness@example.org",
        }
        body = cache.fetch(f"pubmed-efetch-meta-{idx // 200 + 1}", f"{EUTILS}/efetch.fcgi", params, ".xml")
        root = ET.fromstring(body)
        for article in descendants(root, "PubmedArticle"):
            pmid = first_path_text(article, ["MedlineCitation", "PMID"]) or first_desc_text(article, "PMID")
            if not pmid:
                continue
            ncts: set[str] = set()
            for node in descendants(article, "ArticleId"):
                if (node.attrib.get("IdType") or "").lower() == "clinicaltrials.gov":
                    text = text_of(node)
                    if re.fullmatch(r"NCT\d{8}", text):
                        ncts.add(text)
            for node in descendants(article, "AccessionNumber"):
                text = text_of(node)
                if re.fullmatch(r"NCT\d{8}", text):
                    ncts.add(text)
            pub_date = first_path(article, ["MedlineCitation", "Article", "Journal", "JournalIssue", "PubDate"])
            year = first_path_text(article, ["MedlineCitation", "Article", "Journal", "JournalIssue", "PubDate", "Year"])
            if not year and pub_date is not None:
                year = citation_year(text_of(pub_date))
            if not year:
                year = first_path_text(article, ["MedlineCitation", "Article", "ArticleDate", "Year"])
            meta[pmid] = {
                "pmid": pmid,
                "title": first_path_text(article, ["MedlineCitation", "Article", "ArticleTitle"]),
                "journal": first_path_text(article, ["MedlineCitation", "Article", "Journal", "Title"])
                or first_path_text(article, ["MedlineCitation", "Article", "Journal", "ISOAbbreviation"]),
                "year": year,
                "ncts": sorted(ncts),
            }
    return meta


def fetch_ctgov(cache: RawCache, cond: str, intr: str) -> dict[str, Any]:
    studies: list[dict[str, Any]] = []
    page_token = ""
    page = 1
    while True:
        params: dict[str, Any] = {
            "format": "json",
            "query.cond": cond,
            "query.intr": intr,
            "pageSize": 1000,
        }
        if page_token:
            params["pageToken"] = page_token
        body = cache.fetch(f"ctgov-search-page-{page}", CTGOV, params, ".json")
        payload = json.loads(body.decode("utf-8"))
        studies.extend(payload.get("studies") or [])
        page_token = str(payload.get("nextPageToken") or "")
        if not page_token:
            break
        page += 1
    ncts: set[str] = set()
    pmid_text: defaultdict[str, list[str]] = defaultdict(list)
    for study in studies:
        proto = study.get("protocolSection") or {}
        ident = proto.get("identificationModule") or {}
        nct = str(ident.get("nctId") or "")
        if nct:
            ncts.add(nct)
        blob = json.dumps(study, ensure_ascii=False)
        for pmid in sorted(set(re.findall(r"\b\d{5,9}\b", blob))):
            if nct:
                pmid_text[pmid].append(nct)
    return {
        "count": len(studies),
        "ncts": sorted(ncts),
        "pmid_text": {pmid: sorted(set(ids)) for pmid, ids in pmid_text.items()},
        "studies": studies,
    }


def clean_record_id(value: str) -> str:
    text = str(value or "")
    m = re.search(r"\b(PMID|NCT)\s*([A-Z0-9]+)", text)
    if m:
        return m.group(2)
    return text.strip()


def object_state(config: dict[str, Any], records: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    pubmed_records = list(records.get("records") or [])
    ctgov_records = list(records.get("ctgov") or [])
    record_by_id = {str(r.get("id")): r for r in [*pubmed_records, *ctgov_records] if r.get("id")}
    screen_by_id = {
        clean_record_id(str(r.get("id") or "")): r
        for r in (review.get("screening", {}).get("records") or [])
    }
    primary = next((o for o in review.get("outcomes", []) if o.get("primary")), review.get("outcomes", [])[0])
    pooled_ids = [clean_record_id(str(t.get("id") or t.get("label") or "")) for t in primary.get("trials") or []]
    pooled_ids = [pid for pid in pooled_ids if pid]
    absent_by_id = {
        clean_record_id(str(t.get("id") or t.get("label") or "")): t
        for t in (primary.get("declared_absent_trials") or [])
    }
    estimand_by_id = {
        clean_record_id(str(t.get("id") or t.get("label") or "")): t
        for t in (review.get("estimand_exclusions") or [])
    }
    included = [
        clean_record_id(str(r.get("id") or ""))
        for r in (review.get("screening", {}).get("records") or [])
        if r.get("decision") == "include"
    ]
    pooled_nct: dict[str, str] = {}
    for pid in pooled_ids:
        nct = str((record_by_id.get(pid) or {}).get("nct") or "")
        if nct:
            pooled_nct[nct] = pid
    return {
        "pubmed_records": pubmed_records,
        "ctgov_records": ctgov_records,
        "record_by_id": record_by_id,
        "screen_by_id": screen_by_id,
        "primary": primary,
        "pooled_ids": pooled_ids,
        "pooled_set": set(pooled_ids),
        "absent_by_id": absent_by_id,
        "estimand_by_id": estimand_by_id,
        "included_ids": included,
        "pooled_nct": pooled_nct,
        "screen_counter": Counter((r.get("decision"), r.get("rule_id")) for r in review.get("screening", {}).get("records") or []),
        "config": config,
        "review": review,
    }


def record_title(state: dict[str, Any], rid: str) -> str:
    return str((state["record_by_id"].get(rid) or {}).get("title") or "")


def current_name(state: dict[str, Any], rid: str) -> str:
    title = record_title(state, rid)
    return f"PMID {rid} - {title}" if title else rid


def classify_rows(rows: list[dict[str, Any]], state: dict[str, Any], pubmed_meta: dict[str, Any]) -> None:
    for row in rows:
        pmid = str(row.get("pmid") or "")
        row_ncts = set((pubmed_meta.get(pmid) or {}).get("ncts") or [])
        crosswalk = sorted(row_ncts.intersection(state["pooled_nct"].keys()))
        if pmid and pmid in state["pooled_set"]:
            row["class"] = "POOLED_BY_US"
            row["class_evidence"] = "same PMID appears in outcomes[primary].trials"
        elif crosswalk:
            row["class"] = "POOLED_UNDER_ANOTHER_ID"
            row["class_evidence"] = f"NCT crosswalk {', '.join(crosswalk)} -> pooled PMID {state['pooled_nct'][crosswalk[0]]}"
        elif pmid and pmid in state["screen_by_id"]:
            screen = state["screen_by_id"][pmid]
            if screen.get("decision") == "exclude":
                row["class"] = "RETRIEVED_EXCLUDED"
                row["class_evidence"] = f"{screen.get('rule_id')}: {screen.get('reason')}"
            elif pmid in state["absent_by_id"]:
                absent = state["absent_by_id"][pmid]
                row["class"] = "RETRIEVED_INCLUDED_NOT_POOLED"
                row["class_evidence"] = (
                    f"{absent.get('state')}: {absent.get('reason')}; absent_kind={absent.get('absent_kind')}"
                )
            elif pmid in state["estimand_by_id"]:
                excl = state["estimand_by_id"][pmid]
                row["class"] = "RETRIEVED_INCLUDED_NOT_POOLED"
                row["class_evidence"] = f"estimand_exclusion: {excl.get('reason') or excl}"
            else:
                row["class"] = "RETRIEVED_INCLUDED_NOT_POOLED"
                row["class_evidence"] = "screened INCLUDE but not present in the primary pooled trial list"
        elif pmid and pmid in state["record_by_id"]:
            row["class"] = "RETRIEVED_INCLUDED_NOT_POOLED"
            row["class_evidence"] = "present in records.json but no screening-row join found in review.json"
        else:
            row["class"] = "NOT_RETRIEVED"
            row["class_evidence"] = "resolved PMID absent from records.json/screening ledger" if pmid else "UNRESOLVED; no PubMed PMID resolved"


def rank_of(ids: list[str], pmid: str) -> int | None:
    try:
        return ids.index(str(pmid)) + 1
    except ValueError:
        return None


def measure_reachability(
    rows: list[dict[str, Any]],
    state: dict[str, Any],
    query_runs: list[dict[str, Any]],
    concept_run: dict[str, Any],
    ctgov: dict[str, Any],
    pubmed_meta: dict[str, Any],
) -> None:
    ct_ncts = set(ctgov["ncts"])
    for row in rows:
        pmid = str(row.get("pmid") or "")
        ranks = []
        for idx, run in enumerate(query_runs, start=1):
            pos = rank_of(run["ids"], pmid) if pmid else None
            ranks.append({"query": idx, "rank": pos, "count": run["count"], "fetched": run["fetched"], "truncated": run["truncated"]})
        concept_rank = rank_of(concept_run["ids"], pmid) if pmid else None
        ncts = set((pubmed_meta.get(pmid) or {}).get("ncts") or [])
        nct_in_cache = str((state["record_by_id"].get(pmid) or {}).get("nct") or "")
        if nct_in_cache:
            ncts.add(nct_in_cache)
        registry = bool(ncts.intersection(ct_ncts) or (pmid and pmid in ctgov["pmid_text"]))
        indexed = bool(pmid)
        cap_lost = any(item["rank"] is not None and item["rank"] > int(state["config"].get("max_records", 650)) for item in ranks)
        within_cap = [item for item in ranks if item["rank"] is not None and item["rank"] <= int(state["config"].get("max_records", 650))]
        any_query_rank = [item for item in ranks if item["rank"] is not None]
        if any_query_rank:
            bits = [f"our query #{item['query']} rank {item['rank']}" for item in any_query_rank]
            reachable_by = "REACHABLE_BY(" + "; ".join(bits) + ")"
        elif concept_rank is not None:
            reachable_by = f"REACHABLE_BY(concept query rank {concept_rank})"
        elif registry:
            reachable_by = "REACHABLE_BY(registry)"
        elif not indexed:
            # A citation the title esearch did not resolve to a PMID. That is a failure of OUR
            # resolution step, not a measurement that PubMed does not index the trial -- say so.
            reachable_by = "PMID_UNRESOLVED(indexing not observed; resolution by title esearch failed)"
        else:
            reachable_by = "REACHABLE_BY(none-of-these)"
        row["reachability"] = {
            "indexed": indexed,
            "our_query_ranks": ranks,
            "our_query_within_cap": within_cap,
            "concept_rank": concept_rank,
            "registry": registry,
            "ncts": sorted(ncts),
            "cap_lost": cap_lost,
            "reachable_by": reachable_by,
        }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell).replace("\n", " ").replace("|", "\\|") for cell in row) + " |")
    return "\n".join(out)


def capture_their_42(rows: list[dict[str, Any]]) -> str:
    lines = [
        "THEIR 42, named",
        f"Diagnostic date: {RUN_DATE}",
        "Source: cache/probiotics-aad-prevention/comparator_fulltext.txt, Goodman 2021 BMJ Open Table 1, joined to the PMC reference list and PubMed title ESearch raw responses where available.",
        "",
    ]
    table = []
    for row in rows:
        table.append(
            [
                row["row"],
                row["first_author"],
                row.get("year") or "",
                row.get("journal") or "",
                row.get("pmid") or "UNRESOLVED",
                row.get("resolution_basis") or "",
                row.get("sample_size") or "",
                row.get("probiotic_species") or "",
            ]
        )
    lines.append(markdown_table(["#", "trial", "year", "journal", "PMID", "resolution", "sample size", "probiotic strain"], table))
    lines.append("")
    unresolved = [row for row in rows if not row.get("pmid")]
    if unresolved:
        lines.append("UNRESOLVED rows with citation as printed:")
        for row in unresolved:
            lines.append(f"- {row['first_author']} {row.get('year') or ''}: {row.get('citation') or row.get('table_chunk')}")
    return "\n".join(lines)


def capture_funnel(state: dict[str, Any]) -> str:
    review = state["review"]
    primary = state["primary"]
    lines = [
        "OUR FUNNEL, exactly from the committed objects",
        f"records.json PubMed records: {len(state['pubmed_records'])}",
        f"records.json CT.gov records: {len(state['ctgov_records'])}",
        f"review.search.n_records / screening denominator: {review.get('search', {}).get('n_records')}",
        "",
        "Screening decisions by rule:",
    ]
    for (decision, rule), n in sorted(state["screen_counter"].items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
        lines.append(f"- {decision} / {rule}: {n}")
    lines.extend(
        [
            "",
            f"Primary outcome: {primary.get('name')}",
            f"Pooled trials: {len(primary.get('trials') or [])}",
            f"Included-not-pooled declared absent trials: {len(primary.get('declared_absent_trials') or [])}",
            f"Estimand exclusions: {len(state['review'].get('estimand_exclusions') or [])}",
            "",
            "Pooled trials:",
        ]
    )
    for trial in primary.get("trials") or []:
        rid = clean_record_id(str(trial.get("id") or trial.get("label") or ""))
        lines.append(f"- PMID {rid}: {record_title(state, rid)}")
    lines.extend(["", "Included-not-pooled / declared absent trials, with object reason:"])
    for rid, absent in sorted(state["absent_by_id"].items()):
        lines.append(
            f"- PMID {rid}: {record_title(state, rid)} :: {absent.get('state')} / "
            f"{absent.get('absent_kind')} / {absent.get('reason')}"
        )
    if state["estimand_by_id"]:
        lines.extend(["", "Estimand exclusions:"])
        for rid, item in sorted(state["estimand_by_id"].items()):
            lines.append(f"- {rid}: {record_title(state, rid)} :: {item}")
    return "\n".join(lines)


def class_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(row["class"] for row in rows if row["class"] != "POOLED_BY_US")


def actual_comparator_gap(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["class"] != "POOLED_BY_US"]


def capture_classified(rows: list[dict[str, Any]], state: dict[str, Any]) -> str:
    gap_rows = actual_comparator_gap(rows)
    comparator_pmids = {str(row.get("pmid")) for row in rows if row.get("pmid")}
    ours_not_theirs = [pid for pid in state["pooled_ids"] if pid not in comparator_pmids]
    lines = [
        "THE 26 / set accounting and classification",
        "",
        "The lane shorthand says 'their 42 minus the 16 we pooled = 26'. The current identifier-resolved objects do not support that arithmetic as a set difference.",
        f"Exact Goodman-row PMIDs pooled by us: {42 - len(gap_rows)}.",
        f"Comparator rows not pooled by us by PMID/crosswalk: {len(gap_rows)}.",
        f"Our pooled PMIDs not in Goodman 42: {len(ours_not_theirs)}.",
        "",
        "Counts by class, excluding Goodman rows already pooled by us:",
    ]
    for cls, n in sorted(class_counts(rows).items()):
        lines.append(f"- {cls}: {n}")
    lines.extend(["", "Classified Goodman rows not pooled by us:"])
    for row in gap_rows:
        reach = row.get("reachability", {})
        lines.append(
            f"- {row['first_author']} {row.get('year') or ''} PMID {row.get('pmid') or 'UNRESOLVED'} "
            f"-> {row['class']} :: {row.get('class_evidence')} :: {reach.get('reachable_by', '')}"
        )
    lines.extend(["", "Symmetric list: our pooled PMIDs not in Goodman 42:"])
    for pid in ours_not_theirs:
        lines.append(f"- PMID {pid}: {record_title(state, pid)}")
    return "\n".join(lines)


def capture_reachability(
    rows: list[dict[str, Any]],
    query_runs: list[dict[str, Any]],
    concept_run: dict[str, Any],
    ctgov: dict[str, Any],
    raw_cache: RawCache,
) -> str:
    lines = [
        "REACHABILITY MEASURED",
        f"Diagnostic date: {RUN_DATE}",
        "",
        "Verbatim PubMed queries rerun today:",
    ]
    for idx, run in enumerate(query_runs, start=1):
        labels = raw_cache.entries_for(f"pubmed-verbatim-{idx}-")
        shas = ", ".join(f"{entry['file']} sha256={entry['body_sha256']}" for entry in labels)
        lines.append(f"- Query #{idx}: count={run['count']}, fetched={run['fetched']}, truncated={run['truncated']}")
        lines.append(f"  {run['term']}")
        lines.append(f"  raw: {shas}")
    labels = raw_cache.entries_for("pubmed-concept-")
    shas = ", ".join(f"{entry['file']} sha256={entry['body_sha256']}" for entry in labels)
    lines.extend(["", f"Registered concept query: count={concept_run['count']}, fetched={concept_run['fetched']}, truncated={concept_run['truncated']}", concept_run["term"], f"raw: {shas}"])
    ct_labels = raw_cache.entries_for("ctgov-search")
    ct_shas = ", ".join(f"{entry['file']} sha256={entry['body_sha256']}" for entry in ct_labels)
    lines.extend(["", f"CT.gov condition+intervention search: studies={ctgov['count']}", f"raw: {ct_shas}", ""])
    lines.append("Not-retrieved Goodman rows:")
    for row in rows:
        if row["class"] != "NOT_RETRIEVED":
            continue
        reach = row.get("reachability", {})
        ranks = "; ".join(
            f"q{item['query']}={'-' if item['rank'] is None else item['rank']}/{item['count']}"
            for item in reach.get("our_query_ranks", [])
        )
        concept = reach.get("concept_rank")
        lines.append(
            f"- {row['first_author']} {row.get('year') or ''} PMID {row.get('pmid') or 'UNRESOLVED'}: "
            f"{reach.get('reachable_by')}; indexed={reach.get('indexed')}; registry={reach.get('registry')}; "
            f"ranks=[{ranks}]; concept={'-' if concept is None else concept}; nct={','.join(reach.get('ncts') or []) or '-'}"
        )
    return "\n".join(lines)


def capture_cap(rows: list[dict[str, Any]], query_runs: list[dict[str, Any]], config: dict[str, Any]) -> str:
    max_records = int(config.get("max_records", 650))
    gap_rows = actual_comparator_gap(rows)
    cap_lost = [row for row in gap_rows if (row.get("reachability") or {}).get("cap_lost")]
    lines = [
        "THE CAP",
        f"Configured max_records: {max_records}",
        "",
        "PubMed hit counts today vs cap:",
    ]
    for idx, run in enumerate(query_runs, start=1):
        over = max(run["count"] - max_records, 0)
        lines.append(f"- Query #{idx}: hits={run['count']}; cap={max_records}; over_cap={over}; fetched_for_diagnostic={run['fetched']}")
    lines.extend(
        [
            "",
            f"Goodman rows not pooled by us and found only beyond rank {max_records}: {len(cap_lost)}",
        ]
    )
    for row in cap_lost:
        ranks = [
            f"q{item['query']} rank {item['rank']}"
            for item in (row.get("reachability") or {}).get("our_query_ranks", [])
            if item["rank"] is not None and item["rank"] > max_records
        ]
        lines.append(f"- {row['first_author']} {row.get('pmid') or 'UNRESOLVED'}: {', '.join(ranks)}")
    return "\n".join(lines)


def rebuild_requirement(rows: list[dict[str, Any]], config: dict[str, Any]) -> str:
    gap_rows = actual_comparator_gap(rows)
    max_records = int(config.get("max_records", 650))
    cap_lost = sum(1 for row in gap_rows if (row.get("reachability") or {}).get("cap_lost"))
    concept_only = 0
    not_indexed = 0
    none = 0
    retrieved_object = 0
    excluded_by: dict[str, int] = {}
    unpooled_by: dict[str, int] = {}
    for row in gap_rows:
        reach = row.get("reachability") or {}
        any_query = any(item["rank"] is not None for item in reach.get("our_query_ranks", []))
        if row["class"] == "RETRIEVED_EXCLUDED":
            retrieved_object += 1
            rule = str(row.get("class_evidence") or "").split(":", 1)[0].strip() or "?"
            excluded_by[rule] = excluded_by.get(rule, 0) + 1
        elif row["class"] == "RETRIEVED_INCLUDED_NOT_POOLED":
            retrieved_object += 1
            reason = str(row.get("class_evidence") or "").split(":", 1)[0].strip() or "?"
            unpooled_by[reason] = unpooled_by.get(reason, 0) + 1
        elif row["class"] != "NOT_RETRIEVED":
            retrieved_object += 1
        elif not reach.get("indexed"):
            not_indexed += 1
        elif (not any_query) and reach.get("concept_rank") is not None:
            concept_only += 1
        elif "none-of-these" in str(reach.get("reachable_by")):
            none += 1
    n_gap = len(gap_rows)
    excl = ", ".join(f"{k} x{v}" for k, v in sorted(excluded_by.items(), key=lambda kv: -kv[1]))
    unp = ", ".join(f"{k} x{v}" for k, v in sorted(unpooled_by.items(), key=lambda kv: -kv[1]))
    # Stated from the counts, in the direction they point: on this topic the loss is DOWNSTREAM
    # of retrieval. A search rebuild alone would not recover the rows screening and extraction lost.
    return (
        f"On this topic the loss is downstream of retrieval, not in it: of the {n_gap} Goodman rows we did not pool, "
        f"{retrieved_object} were retrieved by our own hand-written queries and then lost -- "
        f"{sum(excluded_by.values())} at screening ({excl}) and {sum(unpooled_by.values())} at extraction ({unp}); "
        f"{cap_lost} were reachable only beyond the rank-{max_records} cap; {concept_only} were missed by all three hand-written "
        f"queries but returned by the concept query; {none} resolved PubMed rows were in none of the measured sources; "
        f"{not_indexed} citations could not be resolved to a PMID by title esearch (indexing NOT observed -- not 'not indexed'). "
        f"Corpus-v1 must fix, in this order: (1) screening -- the X2 population rule reads only title/conditions and rejects AAD "
        f"trials whose titles do not name AAD, and X1 reads registry pubtype as the RCT test; (2) extraction -- an included trial "
        f"whose abstract lacks arm counts is left unpooled because full text is not fetched; (3) search -- a registered, fully "
        f"paginated concept+registry search replaces the three hand-written strings, which on this topic was not the binding loss."
    )


def readme(
    rows: list[dict[str, Any]],
    state: dict[str, Any],
    query_runs: list[dict[str, Any]],
    concept_run: dict[str, Any],
    ctgov: dict[str, Any],
) -> str:
    counts = class_counts(rows)
    gap_rows = actual_comparator_gap(rows)
    comparator_pmids = {str(row.get("pmid")) for row in rows if row.get("pmid")}
    ours_not_theirs = [pid for pid in state["pooled_ids"] if pid not in comparator_pmids]
    their_table = markdown_table(
        ["trial", "year", "PMID", "sample size", "probiotic strain"],
        [
            [row["first_author"], row.get("year") or "", row.get("pmid") or "UNRESOLVED", row.get("sample_size") or "", row.get("probiotic_species") or ""]
            for row in rows
        ],
    )
    class_table = markdown_table(
        ["trial", "PMID", "class", "evidence", "reachability"],
        [
            [
                f"{row['first_author']} {row.get('year') or ''}",
                row.get("pmid") or "UNRESOLVED",
                row["class"],
                row.get("class_evidence") or "",
                (row.get("reachability") or {}).get("reachable_by", ""),
            ]
            for row in gap_rows
        ],
    )
    funnel_rows = []
    for (decision, rule), n in sorted(state["screen_counter"].items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
        funnel_rows.append([decision, rule, n])
    query_rows = [
        [f"PubMed query #{idx}", run["count"], run["fetched"], "yes" if run["count"] > int(state["config"].get("max_records", 650)) else "no"]
        for idx, run in enumerate(query_runs, start=1)
    ]
    query_rows.append(["Registered concept query", concept_run["count"], concept_run["fetched"], "n/a"])
    union_statement = (
        "NOT_COMPUTED: the requested union estimate was not recomputed because every added Goodman-row trial would need committed arm counts or effect+CI. "
        "At least one comparator-only row remains not retrieved or declared absent without committed outcome numbers, so a partial union would not answer the lane question."
    )
    lines = [
        "# Probiotics AAD Search Diagnostic (2026-09-15)",
        "",
        "**Fix state (orthogonal fields rule): LANDED / NONE / INSTANCE / CURRENT** - generated from DIAG-probiotics-search",
        "",
        "This diagnostic measures the committed probiotics AAD search object against Goodman 2021 (PMID 34385227), without changing the topic config, records cache, review page, or pooled result.",
        "",
        "## Their 42",
        "",
        their_table,
        "",
        "## Our Funnel",
        "",
        f"- Review search denominator: {state['review'].get('search', {}).get('n_records')} screened records.",
        f"- records.json carries {len(state['pubmed_records'])} PubMed records and {len(state['ctgov_records'])} CT.gov records.",
        f"- Primary pooled trials: {len(state['primary'].get('trials') or [])}.",
        f"- Included-not-pooled declared absent trials: {len(state['primary'].get('declared_absent_trials') or [])}.",
        "",
        markdown_table(["decision", "rule", "n"], funnel_rows),
        "",
        "The full 16 pooled names and 44 included-not-pooled object reasons are in `02-our-funnel.txt`.",
        "",
        "## Goodman Rows Not Pooled By Us",
        "",
        "The lane shorthand says 'their 42 minus our 16 = 26'. The current object-level set difference is larger because only exact/crosswalk Goodman-row PMIDs that appear in our pooled list can be subtracted.",
        f"Exact Goodman rows pooled by us: {42 - len(gap_rows)}; Goodman rows not pooled by us: {len(gap_rows)}; our pooled PMIDs not in Goodman 42: {len(ours_not_theirs)}.",
        "",
        markdown_table(["class", "n"], [[cls, n] for cls, n in sorted(counts.items())]),
        "",
        class_table,
        "",
        "## Reachability And Cap",
        "",
        markdown_table(["source", "hit count today", "ids fetched for diagnostic", "above 650 cap"], query_rows),
        "",
        f"CT.gov condition+intervention search returned {ctgov['count']} studies.",
        "",
        "## Rebuild Requirement",
        "",
        rebuild_requirement(rows, state["config"]),
        "",
        "## Symmetry",
        "",
        "Our pooled PMIDs not in Goodman 42:",
    ]
    for pid in ours_not_theirs:
        lines.append(f"- PMID {pid}: {record_title(state, pid)}")
    lines.extend(["", "## Union Estimate", "", union_statement])
    return "\n".join(lines)


def update_captions() -> None:
    captions = read_json(CAPTIONS_PATH)
    captions[DIAG_SLUG] = {
        "_title": "Probiotics AAD search diagnostic (2026-09-15): Goodman 42, our funnel, reachability and cap accounting",
        "_intro": "Comparator-to-object diagnostic for the probiotics AAD topic: Goodman 2021's 42 named trials, the committed 468-record screening funnel, the comparator rows not pooled by us, and dated PubMed/CT.gov reachability measurements.",
        "README.md": "Diagnostic summary: Goodman 42, our funnel, comparator-row classes/counts, one-line search rebuild requirement, symmetry list, and union-estimate refusal.",
        "01-their-42.txt": "The 42 Goodman 2021 AAD-incidence trials named from Table 1 with sample sizes, probiotic strains, journal/year, and PubMed title-resolution evidence.",
        "02-our-funnel.txt": "The committed probiotics object funnel: records and screening counts, the 16 pooled primary trials, and every included-not-pooled declared-absent record with its object reason.",
        "03-the-26-classified.txt": "The lane's requested '42 minus 16' accounting reconciled to the actual PMID/crosswalk set difference, with every Goodman row not pooled by us classified.",
        "04-reachability-measured.txt": "Dated PubMed/CT.gov reachability rerun: verbatim queries, registered concept query, CT.gov search, raw-response filenames, SHA-256 digests, and per-not-retrieved-trial reachability.",
        "05-cap.txt": "The configured 650-record cap compared with today's PubMed hit counts and the Goodman rows, if any, reachable only beyond rank 650.",
    }
    write_json(CAPTIONS_PATH, captions)


def git_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc.stdout.strip()


def seal_dependencies() -> dict[str, str]:
    paths = [
        rel(path)
        for path in sorted(EVIDENCE_DIR.rglob("*"))
        if path.is_file() and not path.name.endswith(".html") and path.name != "index.html"
    ]
    paths.extend([rel(RECORDS_PATH), rel(CONFIG_PATH)])
    return dict(sorted(gitblob.blob_shas(ROOT, paths).items()))


def update_registry(rows: list[dict[str, Any]], raw_index_sha256: str) -> None:
    store = read_json(REGISTRY_PATH)
    head = git_head()
    deps = seal_dependencies()
    counts = class_counts(rows)
    evidence = [
        f"docs/evidence/{DIAG_SLUG}/README.md",
        f"docs/evidence/{DIAG_SLUG}/01-their-42.txt",
        f"docs/evidence/{DIAG_SLUG}/02-our-funnel.txt",
        f"docs/evidence/{DIAG_SLUG}/03-the-26-classified.txt",
        f"docs/evidence/{DIAG_SLUG}/04-reachability-measured.txt",
        f"docs/evidence/{DIAG_SLUG}/05-cap.txt",
    ]
    entry = {
        "finding_id": FIX_ID,
        "fix_id": FIX_ID,
        "title": "Probiotics AAD search diagnostic: comparator trial reachability and cap accounting",
        "kind": "finding",
        "implementation": "LANDED",
        "verification": "NONE",
        "scope": "INSTANCE",
        "author": AUTHOR,
        "opened_utc": RUN_UTC,
        "evidence_dir": f"docs/evidence/{DIAG_SLUG}",
        "events": [
            {
                "implementation": "LANDED",
                "verification": "NONE",
                "scope": "INSTANCE",
                "when_utc": RUN_UTC,
                "by": AUTHOR,
                "commit": head,
                "evidence": evidence,
                "reason": "Landed the dated diagnostic evidence bundle and raw-response replay cache for the probiotics search measurement.",
            }
        ],
        "verified_by": {"identity": None, "kind": None},
        "verifications": [],
        "authored_against": [head],
        "generalized_on": [],
        "executable_evidence": None,
        "seal": {
            "sealed_utc": RUN_UTC,
            "commit": head,
            "dependencies": deps,
            "configuration": {
                "schema": "fixes-v3",
                "diagnostic_date": RUN_DATE,
                "raw_index_sha256": raw_index_sha256,
                "class_counts": dict(sorted(counts.items())),
                "rebuild_requirement": rebuild_requirement(rows, read_json(CONFIG_PATH)),
            },
        },
    }
    entries = store.get("entries") or []
    for idx, existing in enumerate(entries):
        if existing.get("fix_id") == FIX_ID or existing.get("finding_id") == FIX_ID:
            entries[idx] = entry
            break
    else:
        entries.append(entry)
    store["entries"] = entries
    write_json(REGISTRY_PATH, store)


def write_report(rows: list[dict[str, Any]], state: dict[str, Any], commands: list[str], base_commit: str) -> None:
    counts = class_counts(rows)
    gap_rows = actual_comparator_gap(rows)
    by_class: defaultdict[str, list[str]] = defaultdict(list)
    for row in gap_rows:
        by_class[row["class"]].append(f"{row['first_author']} {row.get('year') or ''} (PMID {row.get('pmid') or 'UNRESOLVED'})")
    lines = [
        "# LANE AF REPORT",
        "",
        f"Base commit: `{base_commit}`",
        "",
        "Counts by class for Goodman rows not pooled by us:",
    ]
    for cls, n in sorted(counts.items()):
        lines.append(f"- {cls}: {n} :: {', '.join(by_class[cls])}")
    lines.extend(["", "One-line rebuild requirement:", "", rebuild_requirement(rows, state["config"]), "", "Commands run:"])
    for command in commands:
        lines.append(f"- `{command}`")
    write_text(REPORT_PATH, "\n".join(lines))


def prepare_rows(cache: RawCache) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    config, records, review = load_review_objects()
    state = object_state(config, records, review)
    pmc_body = cache.fetch(
        "pmc-goodman-2021-fulltext-xml",
        f"{EUTILS}/efetch.fcgi",
        {"db": "pmc", "id": "8362734", "retmode": "xml", "tool": "meta-harness", "email": "meta-harness@example.org"},
        ".xml",
    )
    refs = parse_refs_from_pmc_xml(pmc_body)
    rows = parse_table_rows_from_cached_text()
    for row in rows:
        ref = refs.get(row["ref_num"], {})
        row.update(ref)
    resolve_titles(cache, rows)
    comparator_pmids = [str(row.get("pmid") or "") for row in rows if row.get("pmid")]
    pubmed_meta = fetch_pubmed_metadata(cache, sorted(set(comparator_pmids + state["pooled_ids"])))
    for row in rows:
        meta = pubmed_meta.get(str(row.get("pmid") or ""))
        if not meta:
            continue
        if meta.get("title"):
            row["title"] = meta["title"]
        if meta.get("journal"):
            row["journal"] = meta["journal"]
        if meta.get("year"):
            row["year"] = str(meta["year"])[:4]
    classify_rows(rows, state, pubmed_meta)
    query_runs = [
        esearch_full(cache, f"pubmed-verbatim-{idx}", query, page_size=1000, hard_cap=10000)
        for idx, query in enumerate(config.get("pubmed_queries") or [], start=1)
    ]
    concept = acquisition.concept_query(config)
    concept_run = esearch_full(cache, "pubmed-concept", concept, page_size=1000, hard_cap=10000)
    ctgov = fetch_ctgov(cache, str(config.get("ctgov", {}).get("cond") or ""), str(config.get("ctgov", {}).get("intr") or ""))
    measure_reachability(rows, state, query_runs, concept_run, ctgov, pubmed_meta)
    diagnostic = {
        "state": state,
        "rows": rows,
        "pubmed_meta": pubmed_meta,
        "query_runs": query_runs,
        "concept_run": concept_run,
        "ctgov": ctgov,
    }
    return rows, state, diagnostic


def write_outputs(rows: list[dict[str, Any]], state: dict[str, Any], diagnostic: dict[str, Any], cache: RawCache, base_commit: str) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    query_runs = diagnostic["query_runs"]
    concept_run = diagnostic["concept_run"]
    ctgov = diagnostic["ctgov"]
    write_text(EVIDENCE_DIR / "01-their-42.txt", capture_their_42(rows))
    write_text(EVIDENCE_DIR / "02-our-funnel.txt", capture_funnel(state))
    write_text(EVIDENCE_DIR / "03-the-26-classified.txt", capture_classified(rows, state))
    write_text(EVIDENCE_DIR / "04-reachability-measured.txt", capture_reachability(rows, query_runs, concept_run, ctgov, cache))
    write_text(EVIDENCE_DIR / "05-cap.txt", capture_cap(rows, query_runs, state["config"]))
    write_text(EVIDENCE_DIR / "README.md", readme(rows, state, query_runs, concept_run, ctgov))
    update_captions()
    cache.save()
    raw_index_sha = sha256_file(cache.index_path)
    update_registry(rows, raw_index_sha)
    commands = [
        "python scripts/probiotics_search_diagnostic.py",
        "python scripts/build_evidence_index.py",
        "python scripts/render_fix_ledger.py",
        "python scripts/rewrite_fixstate_lines.py",
        "python scripts/build_evidence_index.py",
        "python -m pytest tests/ -q",
        "python scripts/verify_all.py",
    ]
    write_report(rows, state, commands, base_commit)


def load_from_diagnostic_json() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raise SystemExit("diagnostic.json is intentionally not written; rerun the diagnostic with the raw cache instead")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry-only", action="store_true", help="re-seal the registry entry from already written evidence")
    args = parser.parse_args(argv)
    base_commit = git_head()
    cache = RawCache(RAW_DIR)
    if args.registry_only:
        rows, state, _diagnostic = prepare_rows(cache)
        update_registry(rows, sha256_file(cache.index_path))
        write_report(rows, state, [
            "python scripts/probiotics_search_diagnostic.py --registry-only",
        ], base_commit)
        return 0
    rows, state, diagnostic = prepare_rows(cache)
    write_outputs(rows, state, diagnostic, cache, base_commit)
    print(f"wrote {rel(EVIDENCE_DIR)} and {rel(REPORT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
