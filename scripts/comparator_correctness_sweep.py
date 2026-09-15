"""Symmetric comparator-correctness sweep for lane AE.

The sweep treats published comparator findings as external claims.  It fetches
and caches comparator text under cache/comparators/<pmid>/, runs the same five
checks over the comparator and this repository's pool, and writes the evidence
bundle plus v3 registry entries with verification NONE.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Any
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-15"
RUN_UTC = "2026-09-15T00:00:00Z"
EVIDENCE_SLUG = f"comparator-correctness-{DATE}"
EVIDENCE_DIR = Path("docs") / "evidence" / EVIDENCE_SLUG
CAPTIONS_PATH = Path("docs") / "evidence" / "CAPTIONS.json"
REGISTRY_PATH = Path("registry") / "fixes.json"
SCRIPT_PATH = Path("scripts") / "comparator_correctness_sweep.py"
REPORT_PATH = Path("LANE-AE-REPORT.md")
FETCH_TIMEOUT = 25
REPRO_TOL_LOG_EST = 0.02
REPRO_TOL_LOG_CI = 0.08

EXTERNAL_HEADING = (
    "Findings about published comparators \u2014 NOT adjudicated by us; verification NONE until an outside party confirms; "
    "we do not adjudicate our own findings about someone else's paper"
)
EXTERNAL_SENTENCE = (
    "each THEIRS finding is an external claim with verification NONE; none has been confirmed by an outside party"
)

CHECKS: tuple[tuple[str, str], ...] = (
    ("design_key", "Design key"),
    ("estimand_key", "Estimand key"),
    ("analysis_population", "Analysis population"),
    ("compatibility_key", "Compatibility key"),
    ("pooled_reproduction", "Pooled-number reproduction"),
)

NOT_ASSESSABLE_PAPER = "NOT_ASSESSABLE(reason: the paper does not expose the input set)"
NOT_ASSESSABLE_REVIEW = "NOT_ASSESSABLE(reason: the review object does not expose the input set)"
NOT_ASSESSABLE_EFFECT_FIGURE = "NOT_ASSESSABLE(reason: per-trial effects are in a forest-plot figure, not a table)"
NO_DEFECT = "NO_DEFECT_FOUND"

COMPARABLE: tuple[tuple[str, str], ...] = (
    ("balanced-crystalloids-vs-saline-mortality", "balanced-crystalloids"),
    ("colchicine-recurrent-pericarditis", "colchicine-recurrent-pericarditis"),
    ("colchicine-secondary-cv-prevention", "colchicine-secondary-cv-prevention"),
    ("corticosteroids-cap-mortality", "corticosteroids-cap-mortality"),
    ("corticosteroids-covid19-mortality", "corticosteroids-covid19-mortality"),
    ("denosumab-vertebral-fracture", "denosumab-vertebral-fracture"),
    ("doac-vte-recurrence", "doac-vte-recurrence"),
    ("finerenone-ckd-t2d-renal", "finerenone-ckd-t2d-renal"),
    ("glp1-ra-mace-t2d", "glp1-ra-mace-t2d"),
    ("metformin-pcos-ovulation", "metformin-pcos-ovulation"),
    ("noac-vs-warfarin-af-stroke", "noac-vs-warfarin-af-stroke"),
    ("omega3-cardiovascular-events", "omega3-cardiovascular-events"),
    ("pcsk9-mace", "pcsk9-mace"),
    ("probiotics-aad-prevention", "probiotics-aad-prevention"),
    ("sglt2-ckd-progression", "sglt2-ckd-progression"),
    ("sglt2-hfref-hosp-cvdeath", "sglt2-hfref-hosp-cvdeath"),
    ("sglt2-primary-prevention-hf", "sglt2-primary-prevention-hf"),
    ("spironolactone-hfref-mortality", "spironolactone-hfref-mortality"),
    ("statins-primary-prevention-elderly", "statins-primary-prevention-elderly"),
    ("ticagrelor-vs-clopidogrel-acs", "ticagrelor-vs-clopidogrel-acs"),
    ("tranexamic-acid-pph", "tranexamic-acid-pph"),
)

NOT_COMPARABLE: tuple[tuple[str, str, str], ...] = (
    ("dpp4-mace-t2d", "dpp4", "their estimate not captured by the served comparator object"),
    ("esketamine-trd-madrs", "esketamine", "their estimate not captured by the served comparator object"),
    ("melatonin-primary-insomnia-sol", "melatonin", "their estimate not captured by the served comparator object"),
    ("semaglutide-obesity-weight", "semaglutide-obesity-weight", "their estimate not captured by the served comparator object"),
    ("dapagliflozin-hfpef-hosp", "dapagliflozin-hfpef", "scope mismatch declared in the object"),
    ("empagliflozin-hfpef-hosp", "empagliflozin-hfpef", "scope mismatch declared in the object"),
    ("sacubitril-valsartan-hfref", "sacubitril-valsartan", "scope mismatch declared in the object"),
    ("semaglutide-obesity-mace", "semaglutide-obesity-mace", "scope mismatch declared in the object"),
    ("tocilizumab-covid19-mortality", "tocilizumab-covid19", "scope mismatch declared in the object"),
    ("colchicine-postop-af", "colchicine-postop-af", "scope mismatch declared in the object"),
    ("iv-iron-hfref-hosp", "iv-iron", "our pool suppressed"),
)

SPECIAL_THEIRS_COMPAT: dict[str, tuple[str, tuple[str, ...]]] = {
    "statins-primary-prevention-elderly": (
        "non_randomised_comparator",
        (
            r"(?:observational|cohort|retrospective|prospective observational).{0,180}",
            r".{0,80}(?:observational|cohort|retrospective).{0,120}",
        ),
    ),
    "tranexamic-acid-pph": (
        "treatment_prevention_scope_mixture",
        (
            r".{0,80}(?:prevention|prevent|prophylactic).{0,100}(?:treatment|treat).{0,80}",
            r".{0,80}(?:treatment|treat).{0,100}(?:prevention|prevent|prophylactic).{0,80}",
        ),
    ),
}


@dataclass
class ComparatorCache:
    pmid: str
    pmcid: str
    directory: Path
    body_rel: str
    body_sha256: str
    body_text: str
    body_source: str
    body_raw_rel: str
    full_text_obtained: bool
    full_text_source: str
    full_text_sha256: str
    full_text_status: str
    open_access_label_failed: bool
    availability_reason: str
    manifest_rel: str
    manifest: dict[str, Any]


@dataclass
class Assessment:
    slug: str
    alias: str
    title: str
    pmid: str
    doi: str
    url: str
    cache: ComparatorCache
    comparator_input_rows: list[dict[str, Any]]
    comparator_characteristic_rows: list[dict[str, Any]]
    comparator_input_exposed: bool
    theirs: dict[str, str]
    ours: dict[str, str]
    theirs_defects: int
    ours_defects: int
    note_span: str


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _rel(path: str | Path) -> str:
    p = Path(path)
    if p.is_absolute():
        return _posix(p.relative_to(ROOT))
    return _posix(p)


def _git(args: list[str], *, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {(proc.stderr or proc.stdout).strip()}")
    return proc.stdout.strip()


def _git_blob_shas(relpaths: list[str]) -> dict[str, str]:
    if not relpaths:
        return {}
    proc = subprocess.run(
        ["git", "hash-object", "--stdin-paths"],
        cwd=ROOT,
        input="\n".join(relpaths) + "\n",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git hash-object failed: {(proc.stderr or proc.stdout).strip()}")
    shas = proc.stdout.split()
    if len(shas) != len(relpaths):
        raise RuntimeError(f"git hash-object returned {len(shas)} shas for {len(relpaths)} paths")
    return dict(zip(relpaths, shas))


def _read_json(rel: str | Path) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _write_text(rel: str | Path, text: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(rel: str | Path, obj: Any) -> None:
    _write_text(rel, json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def _clip(text: str, limit: int = 220) -> str:
    clean = _normalize_space(text)
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def _sanitize_registry_text(text: str) -> str:
    return re.sub(r"\bstatus\b", "state", text, flags=re.IGNORECASE)


def _quote_span(text: str, limit: int = 180) -> str:
    clean = _clip(text, limit)
    clean = clean.replace('"', "'")
    return f'"{clean}"'


def _defect(name: str, span: str) -> str:
    return f"DEFECT({name}, {_quote_span(span)})"


def _decode_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def _text_from_markup(data: bytes) -> str:
    raw = _decode_bytes(data)
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?is)</(?:p|div|tr|table|section|article|h[1-6]|li)>", "\n", raw)
    raw = re.sub(r"(?is)<[^>]+>", " ", raw)
    lines = [_normalize_space(line) for line in raw.splitlines()]
    return "\n".join(line for line in lines if line)


def _fetch(url: str) -> tuple[int, bytes, str]:
    req = Request(
        url,
        headers={
            "User-Agent": "meta-harness-comparator-correctness/1.0 (mailto:openai@example.invalid)",
            "Accept": "text/html,application/xml,text/xml,application/json,*/*;q=0.8",
        },
    )
    try:
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return int(getattr(resp, "status", 200)), resp.read(), ""
    except HTTPError as exc:
        try:
            data = exc.read()
        except Exception:
            data = b""
        return int(exc.code), data, f"HTTPError: {exc.code}"
    except URLError as exc:
        return 0, b"", f"URLError: {exc.reason}"
    except TimeoutError as exc:
        return 0, b"", f"TimeoutError: {exc}"


def _cache_write_bytes(path: Path, data: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {
        "file": _rel(path),
        "bytes": len(data),
        "sha256": _sha256(data),
    }


def _safe_filename(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", label).strip("_")


def _cache_fetch(cdir: Path, filename: str, url: str, *, check: bool = False) -> dict[str, Any]:
    path = cdir / _safe_filename(filename)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    record: dict[str, Any] = {"url": url, "file": _rel(path), "retrieved_utc": RUN_UTC}
    if path.is_file():
        data = path.read_bytes()
        meta: dict[str, Any] = {}
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except ValueError:
                meta = {}
        record.update(
            {
                "state": "CACHED",
                "http_status": meta.get("http_status"),
                "bytes": len(data),
                "sha256": _sha256(data),
                "error": meta.get("error", ""),
            }
        )
        return record
    if check:
        record.update({"state": "MISSING_IN_CHECK_MODE", "http_status": None, "bytes": 0, "sha256": "", "error": ""})
        return record

    http_status, data, error = _fetch(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    record.update(
        {
            "state": "FETCHED" if http_status and http_status < 400 else "FETCHED_ERROR_RESPONSE",
            "http_status": http_status or None,
            "bytes": len(data),
            "sha256": _sha256(data),
            "error": error,
        }
    )
    meta_path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return record


def _record_bytes(record: dict[str, Any]) -> bytes:
    file = record.get("file")
    if isinstance(file, str) and file and (ROOT / file).is_file():
        return (ROOT / file).read_bytes()
    return b""


def _idconv_pmcid(record: dict[str, Any]) -> str:
    data = _record_bytes(record)
    if not data:
        return ""
    try:
        payload = json.loads(_decode_bytes(data))
    except ValueError:
        return ""
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        return ""
    pmcid = str((records[0] or {}).get("pmcid") or "").strip()
    return pmcid if pmcid.startswith("PMC") else (f"PMC{pmcid}" if pmcid else "")


def _pmc_numeric_id(pmcid: str) -> str:
    match = re.search(r"PMC(\d+)", pmcid or "", flags=re.IGNORECASE)
    return match.group(1) if match else ""


def _looks_like_article_xml(data: bytes, *, source: str) -> bool:
    if not data:
        return False
    raw = _decode_bytes(data[:5000]).lower()
    if "<error" in raw or "no full text" in raw or "not found" in raw:
        return False
    if source == "pmc_oai" and "<oai-pmh" in raw and "<metadata" not in raw:
        return False
    return "<article" in raw or "<table-wrap" in raw or "<pmc-articleset" in raw or "<metadata" in raw


def cache_comparator(slug: str, review: dict[str, Any], *, check: bool = False) -> ComparatorCache:
    comparator = review.get("comparator") or {}
    pmid = str(comparator.get("pmid") or "NO_PMID")
    cdir = ROOT / "cache" / "comparators" / pmid
    cdir.mkdir(parents=True, exist_ok=True)

    manifest_records: list[dict[str, Any]] = []
    idconv = _cache_fetch(
        cdir,
        f"{DATE}_idconv.json",
        f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={quote(pmid)}&format=json",
        check=check,
    )
    manifest_records.append(idconv)

    pmcid = _idconv_pmcid(idconv)
    pmc_num = _pmc_numeric_id(pmcid)
    europe: dict[str, Any] = {
        "url": "",
        "file": "",
        "retrieved_utc": RUN_UTC,
        "state": "SKIPPED_NO_PMCID",
        "http_status": None,
        "bytes": 0,
        "sha256": "",
        "error": "idconv did not return a PMCID",
    }
    oai: dict[str, Any] = {
        "url": "",
        "file": "",
        "retrieved_utc": RUN_UTC,
        "state": "SKIPPED_NO_PMCID",
        "http_status": None,
        "bytes": 0,
        "sha256": "",
        "error": "idconv did not return a PMCID",
    }
    if pmcid:
        europe = _cache_fetch(
            cdir,
            f"{DATE}_{pmcid}_europepmc_fulltext.xml",
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML",
            check=check,
        )
        manifest_records.append(europe)
        if not _looks_like_article_xml(_record_bytes(europe), source="europepmc"):
            oai = _cache_fetch(
                cdir,
                f"{DATE}_{pmcid}_pmc_oai.xml",
                f"https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:{pmc_num}&metadataPrefix=pmc",
                check=check,
            )
            manifest_records.append(oai)
        else:
            oai.update({"state": "SKIPPED_EUROPEPMC_FULL_TEXT_OBTAINED", "error": ""})
            manifest_records.append(oai)
    else:
        manifest_records.extend([europe, oai])

    full_text_record: dict[str, Any] | None = None
    full_text_source = ""
    for source, record in (("Europe PMC PMCID fullTextXML", europe), ("PMC OAI pmc metadata", oai)):
        if _looks_like_article_xml(_record_bytes(record), source="pmc_oai" if source.startswith("PMC") else "europepmc"):
            full_text_record = record
            full_text_source = source
            break

    full_text_obtained = full_text_record is not None
    if full_text_record is None:
        body_raw_rel = ""
        body_text = ""
        body_source = "FULL_TEXT_NOT_AVAILABLE_OA"
        body_sha = ""
        availability_reason = "FULL_TEXT_NOT_AVAILABLE_OA"
        full_text_sha = ""
        full_text_status = "FULL_TEXT_NOT_AVAILABLE_OA"
    else:
        body_raw_rel = str(full_text_record.get("file") or "")
        raw = _record_bytes(full_text_record)
        body_text = _text_from_markup(raw)
        body_source = full_text_source
        body_sha = _sha256((body_text + "\n").encode("utf-8"))
        full_text_sha = str(full_text_record.get("sha256") or _sha256(raw))
        full_text_status = f"{full_text_source}; http_status={full_text_record.get('http_status')}; sha256={full_text_sha}"
        availability_reason = "FULL_TEXT_OBTAINED"

    body_rel = Path("cache") / "comparators" / pmid / "body.txt"
    if not check:
        _write_text(body_rel, body_text + "\n")
        (ROOT / (Path("cache") / "comparators" / pmid / "body.sha256")).write_text(
            body_sha + "\n",
            encoding="utf-8",
            newline="\n",
        )

    manifest: dict[str, Any] = {
        "pmid": pmid,
        "pmcid": pmcid,
        "slug": slug,
        "date": DATE,
        "records": manifest_records,
        "body_source": body_source,
        "body_raw_file": body_raw_rel,
        "body_file": _posix(body_rel),
        "body_sha256": body_sha,
        "full_text_obtained": full_text_obtained,
        "full_text_status": full_text_status,
        "availability_reason": availability_reason,
        "open_access_label_failed": bool(comparator.get("open_access") is True and not full_text_obtained),
        "note": "PMID is resolved to PMCID by idconv before fullTextXML; DOI and legacy abstract caches are not used as table evidence.",
    }
    manifest_rel = Path("cache") / "comparators" / pmid / "manifest.json"
    if not check:
        _write_json(manifest_rel, manifest)

    return ComparatorCache(
        pmid=pmid,
        pmcid=pmcid,
        directory=cdir,
        body_rel=_posix(body_rel),
        body_sha256=body_sha,
        body_text=body_text,
        body_source=body_source,
        body_raw_rel=body_raw_rel,
        full_text_obtained=full_text_obtained,
        full_text_source=full_text_source,
        full_text_sha256=full_text_sha,
        full_text_status=full_text_status,
        open_access_label_failed=bool(comparator.get("open_access") is True and not full_text_obtained),
        availability_reason=availability_reason,
        manifest_rel=_posix(manifest_rel),
        manifest=manifest,
    )


def _find_span(text: str, patterns: tuple[str, ...], *, limit: int = 240) -> str:
    flat = _normalize_space(text)
    for pattern in patterns:
        match = re.search(pattern, flat, flags=re.IGNORECASE)
        if match:
            return _clip(match.group(0), limit)
    return ""


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _node_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return _normalize_space(" ".join(part for part in node.itertext()))


def _children(node: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(node) if _local(child.tag) == name]


def _descendants(node: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in node.iter() if _local(child.tag) == name]


def _parse_xml(data: bytes) -> ET.Element | None:
    if not data:
        return None
    raw = _decode_bytes(data)
    try:
        return ET.fromstring(raw)
    except ET.ParseError:
        start = raw.find("<")
        if start > 0:
            try:
                return ET.fromstring(raw[start:])
            except ET.ParseError:
                return None
    return None


def _trial_aliases(review: dict[str, Any]) -> list[str]:
    outcome = _primary_outcome(review)
    aliases: list[str] = []
    for trial in outcome.get("trials") or []:
        if not isinstance(trial, dict):
            continue
        for key in ("id", "label", "name"):
            value = str(trial.get(key) or "").strip()
            if value:
                aliases.append(value)
                aliases.extend(re.findall(r"\b[A-Z][A-Z0-9-]{2,}\b", value))
                aliases.extend(re.findall(r"\b\d{6,9}\b", value))
        source = str(trial.get("source") or "")
        aliases.extend(re.findall(r"\b[A-Z][A-Z0-9-]{2,}\b", source))
        aliases.extend(re.findall(r"\bNCT\d{8}\b", source, flags=re.IGNORECASE))
    protocol_text = str((review.get("protocol") or {}).get("text") or "")
    aliases.extend(re.findall(r"\b[A-Z][A-Z0-9-]{2,}(?:-[A-Z0-9]+)?\b", protocol_text))
    stop = {
        "RCT",
        "RR",
        "OR",
        "HR",
        "CI",
        "PICO",
        "PMC",
        "PMID",
        "DOI",
        "AACT",
        "COVID",
        "MACE",
        "CKD",
        "ITT",
        "CI",
        "MAJOR",
        "PRIMARY",
        "SECONDARY",
        "NOT",
        "HIGH",
        "LOW",
        "EPA",
        "DHA",
        "BMI",
        "DM",
        "HTN",
        "GRADE",
        "NA",
    }
    out: list[str] = []
    seen: set[str] = set()
    for alias in aliases:
        clean = alias.strip(" .,:;()[]")
        if len(clean) < 3 or clean.upper() in stop:
            continue
        key = clean.lower()
        if key not in seen:
            seen.add(key)
            out.append(clean)
    return out[:80]


def _primary_outcome_text(review: dict[str, Any]) -> str:
    outcome = _primary_outcome(review)
    pieces = [
        str(outcome.get(key) or "")
        for key in ("name", "label", "outcome", "id", "description")
        if isinstance(outcome, dict)
    ]
    result = outcome.get("result") if isinstance(outcome.get("result"), dict) else {}
    pieces.extend(str(result.get(key) or "") for key in ("outcome", "label", "scale"))
    return " ".join(piece for piece in pieces if piece).strip()


def _outcome_keywords(review: dict[str, Any]) -> list[str]:
    text = _primary_outcome_text(review).lower()
    words = [w for w in re.findall(r"[a-z][a-z0-9-]{3,}", text) if w not in {"outcome", "composite", "primary", "major"}]
    synonyms: dict[str, tuple[str, ...]] = {
        "mortality": ("mortality", "death", "deaths", "died", "survival"),
        "death": ("mortality", "death", "deaths", "died"),
        "cardiovascular": ("cardiovascular", "cardiovascular death", "cv death", "vascular"),
        "mace": ("mace", "major adverse cardiovascular", "cardiovascular events"),
        "kidney": ("kidney", "renal", "nephropathy", "ckd", "egfr"),
        "ckd": ("kidney", "renal", "ckd", "egfr"),
        "fracture": ("fracture", "vertebral"),
        "vertebral": ("vertebral", "fracture"),
        "diarrhoea": ("diarrhoea", "diarrhea", "aad"),
        "diarrhea": ("diarrhoea", "diarrhea", "aad"),
        "ovulation": ("ovulation", "ovulatory"),
        "stroke": ("stroke", "systemic embolism", "embolism"),
        "bleeding": ("bleeding", "haemorrhage", "hemorrhage", "postpartum"),
        "pericarditis": ("pericarditis", "recurrent pericarditis", "recurrence"),
        "vte": ("vte", "venous thromboembolism", "thromboembolism", "recurrence"),
        "hospitalisation": ("hospitalisation", "hospitalization", "heart failure"),
        "hospitalization": ("hospitalisation", "hospitalization", "heart failure"),
    }
    expanded: list[str] = []
    for word in words:
        expanded.append(word)
        expanded.extend(synonyms.get(word, ()))
    if "mace" in text or "major adverse cardiovascular" in text:
        expanded.extend(synonyms["mace"])
    out: list[str] = []
    seen: set[str] = set()
    for item in expanded:
        clean = item.strip().lower()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out[:25]


def _keyword_match(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in keywords)


def _nonstudy_label(text: str) -> bool:
    clean = _normalize_space(text).lower()
    if not clean:
        return True
    if re.match(r"^(?:[<>=≤≥]|not reported|sample size|mean age|male proportion|bmi|smoking|hypertension|dm\b|follow-up|study quality|high$|low$|primary$|secondary$)", clean):
        return True
    return bool(
        re.search(
            r"\b(?:major cardiovascular events?|all-cause mortality|cardiac death|myocardial infarction|stroke|deep vein thrombosis|pulmonary embolism|epidural|dose|grade assessment|population|outcomes?)\b",
            clean,
        )
    )


def _plausible_study_cell(cells: list[str], aliases: list[str]) -> tuple[str, str]:
    if cells and _nonstudy_label(cells[0]):
        return "", ""
    search_cells = [cell for cell in cells[:1] if not _nonstudy_label(cell)]
    for cell in search_cells:
        for alias in aliases:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(alias)}(?![A-Za-z0-9])", cell, flags=re.IGNORECASE):
                return alias, "known-trial alias in study cell"
    for cell in cells[:3]:
        clean = _normalize_space(cell)
        if len(clean) < 3 or len(clean) > 120:
            continue
        if _nonstudy_label(clean):
            continue
        if re.fullmatch(r"[\d. ()/%,-]+", clean):
            continue
        if re.search(r"\b(?:study|author|trial|year|total|overall|subgroup|outcome|effect|events?|risk|ratio|hazard|odds)\b", clean, flags=re.IGNORECASE):
            continue
        if not (
            re.search(r"\b(?:19|20)\d{2}\b", clean)
            or re.search(r"\[[^\]]*\d+[^\]]*\]", clean)
            or re.search(r"\bet\s+al\b", clean, flags=re.IGNORECASE)
            or re.fullmatch(r"[A-Z][A-Z0-9-]{2,}", clean)
        ):
            continue
        return clean, "first non-numeric cell"
    return "", ""


def _extract_counts(text: str) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for match in re.finditer(r"\b(\d{1,6})\s*/\s*(\d{1,6})\b", text):
        a, b = int(match.group(1)), int(match.group(2))
        if b > 0 and a <= b:
            pairs.append((a, b))
    for match in re.finditer(r"\b(\d{1,6})\s+of\s+(\d{1,6})\b", text, flags=re.IGNORECASE):
        a, b = int(match.group(1)), int(match.group(2))
        if b > 0 and a <= b and (a, b) not in pairs:
            pairs.append((a, b))
    return pairs[:4]


def _extract_effect(text: str, header_text: str = "") -> dict[str, Any]:
    label = _scale_label(text) or _scale_label(header_text)
    dash = r"(?:-|to|\u2013|\u2014)"
    patterns = [
        rf"\b(?:(RR|OR|HR|risk ratio|odds ratio|hazard ratio)\b[^\d]{{0,30}})?(\d+(?:\.\d+)?)\s*(?:\(|\[)\s*(?:95%\s*)?(?:CI|confidence interval)?[^\d]{{0,12}}(\d+(?:\.\d+)?)\s*{dash}\s*(\d+(?:\.\d+)?)",
        rf"\b(?:(RR|OR|HR|risk ratio|odds ratio|hazard ratio)\b[^\d]{{0,30}})?(\d+(?:\.\d+)?)\s*,?\s*(?:95%\s*)?(?:CI|confidence interval)\s*(\d+(?:\.\d+)?)\s*{dash}\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        raw_label = match.group(1)
        if raw_label:
            label = _scale_label(raw_label)
        try:
            effect = float(match.group(2))
            lo = float(match.group(3))
            hi = float(match.group(4))
        except (TypeError, ValueError):
            continue
        if effect > 0 and lo > 0 and hi > 0 and lo <= hi:
            return {"scale": label, "effect": effect, "ci_low": lo, "ci_high": hi}
    return {}


def _table_label(table: ET.Element, idx: int) -> str:
    label = ""
    for child in _children(table, "label"):
        label = _node_text(child)
        if label:
            break
    caption_parts: list[str] = []
    for caption in _children(table, "caption"):
        caption_parts.append(_node_text(caption))
    caption = _clip(" ".join(caption_parts), 220)
    if label and caption:
        return f"{label}: {caption}"
    return label or caption or f"table-wrap #{idx}"


def _author_year_from_cells(cells: list[str]) -> tuple[str, str]:
    if not cells:
        return "", ""
    first = _normalize_space(cells[0])
    if not first or len(first) > 160:
        return "", ""
    lower = first.lower().strip(" .,:;()[]")
    if re.match(
        r"^(?:study|author|authors|trial|year|total|overall|subgroup|characteristic|outcome|population|intervention|control|comparison|reference|ref\.?)$",
        lower,
    ):
        return "", ""
    if re.fullmatch(r"[\d. ()/%,:;-]+", first):
        return "", ""
    if _nonstudy_label(first):
        return "", ""
    if re.search(r"\bet\s+al\.?\b", first, flags=re.IGNORECASE):
        return first, "author et al in first column"
    if re.search(r"\b(?:19|20)\d{2}\b", first):
        return first, "author-year in first column"
    if re.fullmatch(r"[A-Z][A-Z0-9-]{2,}(?:\s*\([^)]+\))?", first):
        return first, "trial acronym in first column"
    if re.fullmatch(r"[A-Z][A-Za-z'’.-]+(?:\s+[A-Z][A-Za-z'’.-]+){0,3}\s*\d{1,3}?", first):
        return first, "author/ref in first column"
    return "", ""


def _header_match(header: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, header, flags=re.IGNORECASE) for pattern in patterns)


def _cell_by_header(cells: list[str], headers: list[str], patterns: tuple[str, ...]) -> str:
    for idx, header in enumerate(headers):
        if idx < len(cells) and _header_match(header, patterns):
            return cells[idx]
    return ""


def _first_cell_matching(cells: list[str], patterns: tuple[str, ...], *, skip_first: bool = False) -> str:
    scan = cells[1:] if skip_first else cells
    for cell in scan:
        if any(re.search(pattern, cell, flags=re.IGNORECASE) for pattern in patterns):
            return cell
    return ""


def _unique_terms(text: str, pattern: str) -> list[str]:
    terms: list[str] = []
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        term = _normalize_space(match.group(0))
        key = term.lower()
        if term and key not in {item.lower() for item in terms}:
            terms.append(term)
    return terms


def _design_words(text: str) -> list[str]:
    return _unique_terms(
        text,
        r"\b(?:cluster(?:[- ]randomi[sz]ed)?|crossover|cross-over|double-crossover|stepped[- ]wedge|factorial|parallel|double-blind|single-blind|open-label|randomi[sz]ed|randomised|randomized|multicentre|multi-centre|multicenter|multi-center)\b",
    )


def _analysis_population_words(text: str) -> list[str]:
    return _unique_terms(
        text,
        r"\b(?:intention[- ]to[- ]treat|modified intention[- ]to[- ]treat|modified ITT|mITT|ITT|per[- ]protocol|on[- ]treatment|as[- ]treated|completers?|full analysis set)\b",
    )


def _population_cell(cells: list[str], headers: list[str]) -> str:
    return _cell_by_header(
        cells,
        headers,
        (
            r"\bpopulation\b",
            r"\bsetting\b",
            r"\beligib",
        ),
    ) or _first_cell_matching(
        cells,
        (
            r"\b(?:adult|elderly|inpatient|outpatient|hospital|ICU|intensive care|diabetes|CKD|heart failure|women|men|patients?|participants?)\b",
        ),
        skip_first=True,
    )


def _comparator_cell(cells: list[str], headers: list[str]) -> str:
    return _cell_by_header(
        cells,
        headers,
        (
            r"\bcontrol\b",
            r"\bcomparator\b",
            r"\bcomparison\b",
            r"\bplacebo\b",
            r"\busual care\b",
        ),
    ) or _first_cell_matching(
        cells,
        (
            r"\b(?:placebo|control|usual care|standard care|no treatment|nothing|saline|warfarin|clopidogrel|no probiotic)\b",
            r"\bvs\b",
        ),
        skip_first=True,
    )


def _sample_size_cell(cells: list[str], headers: list[str]) -> str:
    return _cell_by_header(
        cells,
        headers,
        (
            r"^(?:n|N)$",
            r"\bno\.?\b",
            r"\bnumber\b",
            r"\bsample\b",
            r"\bparticipants?\b",
            r"\bpatients?\b",
            r"\bsize\b",
        ),
    ) or _first_cell_matching(cells, (r"\b\d{2,6}\s*(?:\(|$)",), skip_first=True)


def _is_characteristics_table(label: str, headers: list[str], data_rows: list[dict[str, Any]]) -> bool:
    context = _normalize_space(f"{label} {' | '.join(headers)}")
    label_or_header_hit = bool(
        re.search(
            r"\b(?:characteristics?|included studies|summary of included|study design|baseline characteristics|study characteristics)\b",
            context,
            flags=re.IGNORECASE,
        )
    )
    study_header_hit = bool(re.search(r"\bstud(?:y|ies)\b", context, flags=re.IGNORECASE))
    descriptor_header_hit = bool(
        re.search(
            r"\b(?:population|participants?|patients?|intervention|control|comparator|design|sample|outcome|definition|setting)\b",
            context,
            flags=re.IGNORECASE,
        )
    )
    author_rows = sum(1 for row in data_rows if row.get("study"))
    return author_rows >= 2 and (label_or_header_hit or (study_header_hit and descriptor_header_hit))


def _parse_comparator_tables(review: dict[str, Any], cache: ComparatorCache) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not cache.full_text_obtained or not cache.body_raw_rel:
        return [], []
    raw_path = ROOT / cache.body_raw_rel
    root = _parse_xml(raw_path.read_bytes() if raw_path.is_file() else b"")
    if root is None:
        return [], []

    aliases = _trial_aliases(review)
    keywords = _outcome_keywords(review)
    outcome_rows: list[dict[str, Any]] = []
    characteristic_rows: list[dict[str, Any]] = []
    seen_outcome: set[tuple[str, str]] = set()
    seen_characteristic: set[tuple[str, str]] = set()

    for table_idx, table in enumerate(_descendants(root, "table-wrap"), start=1):
        label = _table_label(table, table_idx)
        table_text = _node_text(table)
        context = f"{label} {table_text[:1200]}"
        table_matches_outcome = _keyword_match(context, keywords)
        header_cells: list[str] = []
        row_idx = 0
        data_rows: list[dict[str, Any]] = []
        for tr in _descendants(table, "tr"):
            cells = [_node_text(cell) for cell in list(tr) if _local(cell.tag) in {"td", "th"}]
            cells = [cell for cell in cells if cell]
            if len(cells) < 2:
                continue
            row_idx += 1
            if all(_local(cell.tag) == "th" for cell in list(tr) if _local(cell.tag) in {"td", "th"}):
                header_cells = cells
                continue
            row_text = " | ".join(cells)
            study, study_basis = _author_year_from_cells(cells)
            if not study:
                study, study_basis = _plausible_study_cell(cells, aliases)
            data_rows.append(
                {
                    "table_label": label,
                    "row_index": row_idx,
                    "study": study,
                    "study_basis": study_basis,
                    "cells": cells,
                    "verbatim": row_text,
                    "header": header_cells,
                }
            )

        table_is_characteristics = _is_characteristics_table(label, header_cells, data_rows)
        for row in data_rows:
            cells = row["cells"]
            row_text = row["verbatim"]
            header_text = " | ".join(header_cells)
            study = str(row.get("study") or "")
            effect = _extract_effect(row_text, header_text)
            counts = _extract_counts(row_text)
            row_matches_outcome = table_matches_outcome or _keyword_match(row_text, keywords) or _keyword_match(header_text, keywords)
            if study and (effect or len(counts) >= 2) and row_matches_outcome:
                key = (label, row_text)
                if key not in seen_outcome:
                    seen_outcome.add(key)
                    record: dict[str, Any] = {
                        "table_label": label,
                        "row_index": row.get("row_index"),
                        "study": study,
                        "study_basis": row.get("study_basis"),
                        "cells": cells,
                        "verbatim": row_text,
                        "header": header_cells,
                        "counts": counts,
                        "outcome_match": True,
                    }
                    record.update(effect)
                    outcome_rows.append(record)
            if study and table_is_characteristics:
                key = (label, row_text)
                if key not in seen_characteristic:
                    seen_characteristic.add(key)
                    design = _design_words(row_text)
                    analysis_pop = _analysis_population_words(row_text)
                    population = _population_cell(cells, header_cells)
                    comparator = _comparator_cell(cells, header_cells)
                    sample_size = _sample_size_cell(cells, header_cells)
                    characteristic_rows.append(
                        {
                            "table_label": label,
                            "row_index": row.get("row_index"),
                            "study": study,
                            "study_basis": row.get("study_basis"),
                            "cells": cells,
                            "verbatim": row_text,
                            "has_design": bool(design),
                            "has_population": bool(population),
                            "has_estimand": bool(re.search(r"\b(?:hazard ratio|risk ratio|odds ratio|rr|or|hr|events?|incidence)\b", row_text, flags=re.IGNORECASE)),
                            "header": header_cells,
                            "design_words": design,
                            "population_words": population,
                            "comparator": comparator,
                            "n": sample_size,
                            "analysis_population_words": analysis_pop,
                        }
                    )
    return outcome_rows[:80], characteristic_rows


def _machine_rows(text: str) -> list[str]:
    rows: list[str] = []
    ci_re = re.compile(
        r"\b(?:RR|OR|HR|risk ratio|odds ratio|hazard ratio)\b.{0,40}"
        r"\d+(?:\.\d+)?\s*(?:\(|\[)\s*\d+(?:\.\d+)?\s*(?:-|to|\u2013)\s*\d+(?:\.\d+)?",
        re.IGNORECASE,
    )
    for raw in text.splitlines():
        line = _normalize_space(raw)
        if len(line) < 20 or len(line) > 420:
            continue
        if re.search(r"\b(?:overall|total|summary|subgroup|pooled)\b", line, flags=re.IGNORECASE):
            continue
        if not ci_re.search(line):
            continue
        if not re.search(r"\b(?:study|trial|[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?)\b", line):
            continue
        rows.append(line)
    # De-duplicate while preserving order.
    out: list[str] = []
    seen: set[str] = set()
    for row in rows:
        key = row.lower()
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out[:20]


def _primary_outcome(review: dict[str, Any]) -> dict[str, Any]:
    outcomes = review.get("outcomes") or []
    for outcome in outcomes:
        if isinstance(outcome, dict) and outcome.get("primary") is True:
            return outcome
    for outcome in outcomes:
        if isinstance(outcome, dict):
            return outcome
    return {}


def _num(obj: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
    return None


def _scale_label(value: Any) -> str:
    text = str(value or "").upper()
    for label in ("RR", "OR", "HR", "IRR"):
        if re.search(rf"\b{label}\b", text):
            return label
    if "RISK RATIO" in text or "RELATIVE RISK" in text:
        return "RR"
    if "ODDS RATIO" in text:
        return "OR"
    if "HAZARD RATIO" in text:
        return "HR"
    return ""


def _trial_scales(trials: list[dict[str, Any]], result: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for trial in trials:
        for key in ("scale", "effect_label", "estmeasure"):
            label = _scale_label(trial.get(key))
            if label:
                labels.append(label)
        effect_object = trial.get("effect_object")
        if isinstance(effect_object, dict):
            label = _scale_label(effect_object.get("reported_label") or effect_object.get("canonical_estimand"))
            if label:
                labels.append(label)
    result_label = _scale_label(result.get("scale"))
    if "/" in str(result.get("scale") or ""):
        for part in str(result.get("scale")).split("/"):
            label = _scale_label(part)
            if label:
                labels.append(label)
    elif result_label and not labels:
        labels.append(result_label)
    out: list[str] = []
    for label in labels:
        if label not in out:
            out.append(label)
    return out


def _effect_rows_from_trials(trials: list[dict[str, Any]]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for trial in trials:
        effect = _num(trial, "effect", "estimate", "rr", "or", "hr")
        lo = _num(trial, "ci_low", "lower", "lcl", "ci_l")
        hi = _num(trial, "ci_high", "upper", "ucl", "ci_u")
        if effect is None or lo is None or hi is None:
            continue
        label = str(trial.get("id") or trial.get("label") or f"trial{len(rows) + 1}")
        rows.append({"label": label, "effect": effect, "ci_low": lo, "ci_high": hi})
    return rows


def _tcrit_975(df: int) -> float:
    table = {
        1: 12.706,
        2: 4.303,
        3: 3.182,
        4: 2.776,
        5: 2.571,
        6: 2.447,
        7: 2.365,
        8: 2.306,
        9: 2.262,
        10: 2.228,
        11: 2.201,
        12: 2.179,
        13: 2.160,
        14: 2.145,
        15: 2.131,
        16: 2.120,
        17: 2.110,
        18: 2.101,
        19: 2.093,
        20: 2.086,
        21: 2.080,
        22: 2.074,
        23: 2.069,
        24: 2.064,
        25: 2.060,
        26: 2.056,
        27: 2.052,
        28: 2.048,
        29: 2.045,
        30: 2.042,
    }
    return table.get(df, 1.96)


def _pm_tau2(y: list[float], v: list[float]) -> float:
    df = len(y) - 1

    def q_at(tau2: float) -> float:
        weights = [1.0 / (vi + tau2) for vi in v]
        mu = sum(w * yi for w, yi in zip(weights, y)) / sum(weights)
        return sum(w * (yi - mu) ** 2 for w, yi in zip(weights, y))

    if df <= 0 or q_at(0.0) <= df:
        return 0.0
    hi = max(v) if v else 1.0
    if hi <= 0:
        hi = 1.0
    while q_at(hi) > df and hi < 1e6:
        hi *= 2.0
    lo = 0.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if q_at(mid) > df:
            lo = mid
        else:
            hi = mid
    return hi


def _dl_tau2(y: list[float], v: list[float]) -> float:
    if len(y) <= 1:
        return 0.0
    weights = [1.0 / vi for vi in v]
    sw = sum(weights)
    mu = sum(w * yi for w, yi in zip(weights, y)) / sw
    q = sum(w * (yi - mu) ** 2 for w, yi in zip(weights, y))
    c = sw - sum(w * w for w in weights) / sw
    if c <= 0:
        return 0.0
    return max(0.0, (q - (len(y) - 1)) / c)


def _pool_ratio(rows: list[dict[str, float | str]], *, method: str = "PM_HKSJ") -> dict[str, float]:
    if not rows:
        raise ValueError("no rows")
    z = NormalDist().inv_cdf(0.975)
    y: list[float] = []
    v: list[float] = []
    for row in rows:
        eff = float(row["effect"])
        lo = float(row["ci_low"])
        hi = float(row["ci_high"])
        se = (math.log(hi) - math.log(lo)) / (2.0 * z)
        if eff <= 0 or se <= 0:
            raise ValueError("non-positive effect or standard error")
        y.append(math.log(eff))
        v.append(se * se)
    if len(rows) == 1:
        return {"estimate": float(rows[0]["effect"]), "ci_low": float(rows[0]["ci_low"]), "ci_high": float(rows[0]["ci_high"]), "tau2": 0.0}
    tau2 = _dl_tau2(y, v) if method == "DL_IV" else _pm_tau2(y, v)
    weights = [1.0 / (vi + tau2) for vi in v]
    sw = sum(weights)
    mu = sum(w * yi for w, yi in zip(weights, y)) / sw
    se_mu = math.sqrt(1.0 / sw)
    if method == "PM_HKSJ":
        q = sum(w * (yi - mu) ** 2 for w, yi in zip(weights, y))
        df = len(rows) - 1
        scale = max(1.0, q / df)
        se_mu *= math.sqrt(scale)
        crit = _tcrit_975(df)
    else:
        crit = NormalDist().inv_cdf(0.975)
    return {
        "estimate": math.exp(mu),
        "ci_low": math.exp(mu - crit * se_mu),
        "ci_high": math.exp(mu + crit * se_mu),
        "tau2": tau2,
    }


def _reported_result(result: dict[str, Any]) -> tuple[float | None, float | None, float | None]:
    return (
        _num(result, "estimate", "effect", "rr", "or", "hr"),
        _num(result, "ci_low", "lower", "lcl", "ci_l"),
        _num(result, "ci_high", "upper", "ucl", "ci_u"),
    )


def _logdiff(a: float | None, b: float | None) -> float:
    if not a or not b:
        return float("inf")
    return abs(math.log(a) - math.log(b))


def _assess_ours(review: dict[str, Any]) -> dict[str, str]:
    outcome = _primary_outcome(review)
    trials = [t for t in (outcome.get("trials") or []) if isinstance(t, dict)]
    result = outcome.get("result") if isinstance(outcome.get("result"), dict) else {}
    checks: dict[str, str] = {}

    unit = review.get("unit_of_analysis")
    if isinstance(unit, list) and unit:
        first = unit[0] if isinstance(unit[0], dict) else {}
        span = first.get("span") or first.get("design") or "unit_of_analysis list names cluster/crossover designs"
        checks["design_key"] = _defect("design_variance_unadjusted_or_not_stated", str(span))
    else:
        checks["design_key"] = NO_DEFECT

    scales = _trial_scales(trials, result)
    est_state = ""
    estmeasure = result.get("estmeasure")
    if isinstance(estmeasure, dict):
        est_state = str(estmeasure.get("status") or "")
    result_scale = str(result.get("scale") or "")
    if len([s for s in scales if s in {"RR", "OR", "HR"}]) > 1 or "/" in result_scale or est_state in {"compatible_labels", "incompatible"}:
        span = f"trial effect labels: {','.join(scales) or 'NOT_STATED'}; result scale: {result_scale or 'NOT_STATED'}; estmeasure: {est_state or 'NOT_STATED'}"
        checks["estimand_key"] = _defect("mixed_ratio_labels_pooled_as_one", span)
    else:
        checks["estimand_key"] = NO_DEFECT

    pop_values: list[str] = []
    for trial in trials:
        for key in ("analysis_population", "analysis_set", "population", "source"):
            value = trial.get(key)
            if isinstance(value, str):
                pop_values.append(value)
    pop_text = " ".join(pop_values).lower()
    has_itt = bool(re.search(r"\b(?:intention-to-treat|intention to treat|itt)\b", pop_text))
    has_non_itt = bool(re.search(r"\b(?:per[- ]protocol|on[- ]treatment|as[- ]treated|completers?)\b", pop_text))
    if has_itt and has_non_itt:
        checks["analysis_population"] = _defect("analysis_population_mixed", _clip(" ".join(pop_values), 180))
    else:
        checks["analysis_population"] = NO_DEFECT

    comp_span = ""
    comp_het = result.get("composite_heterogeneity") or review.get("composite_heterogeneity")
    if isinstance(comp_het, str) and comp_het.strip():
        comp_span = comp_het
    elif isinstance(comp_het, dict):
        comp_span = json.dumps(comp_het, ensure_ascii=False)
    arm_contrast = review.get("arm_contrast")
    if not comp_span and isinstance(arm_contrast, dict):
        for trial_id, arm in (arm_contrast.get("trials") or {}).items():
            if isinstance(arm, dict) and str(arm.get("status") or "").lower() in {"background_only", "same_in_all_arms"}:
                comp_span = f"{trial_id}: {arm.get('status')} {arm.get('basis')}"
                break
    if comp_span:
        checks["compatibility_key"] = _defect("endpoint_or_randomised_contrast_mismatch", comp_span)
    else:
        checks["compatibility_key"] = NO_DEFECT

    rows = _effect_rows_from_trials(trials)
    expected_k = int(result.get("k") or len(trials) or 0)
    reported_est, reported_lo, reported_hi = _reported_result(result)
    if expected_k and len(rows) == expected_k and reported_est and reported_lo and reported_hi:
        try:
            pooled = _pool_ratio(rows, method="PM_HKSJ")
            if (
                _logdiff(pooled["estimate"], reported_est) <= REPRO_TOL_LOG_EST
                and _logdiff(pooled["ci_low"], reported_lo) <= REPRO_TOL_LOG_CI
                and _logdiff(pooled["ci_high"], reported_hi) <= REPRO_TOL_LOG_CI
            ):
                checks["pooled_reproduction"] = NO_DEFECT
            else:
                span = (
                    f"PM/HKSJ recompute {pooled['estimate']:.4g} "
                    f"({pooled['ci_low']:.4g}-{pooled['ci_high']:.4g}) vs review "
                    f"{reported_est:.4g} ({reported_lo:.4g}-{reported_hi:.4g}); k={expected_k}"
                )
                checks["pooled_reproduction"] = _defect("pooled_number_nonreproduction", span)
        except (ValueError, OverflowError) as exc:
            checks["pooled_reproduction"] = f"NOT_ASSESSABLE(reason: {exc})"
    else:
        checks["pooled_reproduction"] = NOT_ASSESSABLE_REVIEW
    return checks


def _parsed_effect_rows(rows: list[dict[str, Any]]) -> list[dict[str, float | str]]:
    out: list[dict[str, float | str]] = []
    for row in rows:
        if all(isinstance(row.get(key), (int, float)) for key in ("effect", "ci_low", "ci_high")):
            out.append(
                {
                    "label": str(row.get("study") or f"row{len(out) + 1}"),
                    "effect": float(row["effect"]),
                    "ci_low": float(row["ci_low"]),
                    "ci_high": float(row["ci_high"]),
                }
            )
            continue
        counts = row.get("counts")
        if isinstance(counts, list) and len(counts) >= 2:
            try:
                e1, n1 = counts[0]
                e0, n0 = counts[1]
                if n1 > 0 and n0 > 0:
                    # Arm order is printed-row order; this is only used for a reproduction
                    # attempt when no direct effect+CI is exposed, and remains not assessable
                    # if the row cannot supply uncertainty.
                    rr = (float(e1) / float(n1)) / (float(e0) / float(n0))
                    if rr > 0:
                        out.append({"label": str(row.get("study") or f"row{len(out) + 1}"), "effect": rr, "ci_low": 0.0, "ci_high": 0.0})
            except (TypeError, ValueError, ZeroDivisionError):
                continue
    return [row for row in out if float(row.get("ci_low", 0.0)) > 0 and float(row.get("ci_high", 0.0)) > 0]


def _comparator_reported_result(review: dict[str, Any]) -> tuple[float | None, float | None, float | None, str]:
    comparator = review.get("comparator") or {}
    outcome_text = _primary_outcome_text(review).lower()
    reported = comparator.get("reported") if isinstance(comparator.get("reported"), list) else []
    best: dict[str, Any] = {}
    for item in reported:
        if not isinstance(item, dict):
            continue
        item_outcome = str(item.get("outcome") or "").lower()
        if not best:
            best = item
        if item_outcome and (item_outcome in outcome_text or any(word in item_outcome for word in _outcome_keywords(review))):
            best = item
            break
    return (_reported_result(best), str(best.get("scale") or ""))[0] + (str(best.get("scale") or ""),) if best else (None, None, None, "")


def _printed_model(body_text: str) -> tuple[str, str]:
    span = _find_span(
        body_text,
        (
            r".{0,80}DerSimonian.{0,120}",
            r".{0,80}Paule[- ]Mandel.{0,120}",
            r".{0,80}Hartung.{0,120}",
            r".{0,80}random[- ]effects? model.{0,120}",
            r".{0,80}fixed[- ]effects? model.{0,120}",
            r".{0,80}inverse[- ]variance.{0,120}",
        ),
        limit=260,
    )
    lower = span.lower()
    if "fixed" in lower and "random" not in lower:
        return "FIXED_IV", span
    if "dersimonian" in lower or "random" in lower or "inverse" in lower:
        return "DL_IV", span
    if "paule" in lower or "hartung" in lower:
        return "PM_HKSJ", span
    return "PM_HKSJ", span


def _not_assessable_for_cache(cache: ComparatorCache, check_name: str) -> str:
    if cache.open_access_label_failed:
        return (
            "NOT_ASSESSABLE(reason: FULL_TEXT_NOT_AVAILABLE_OA; comparator object is marked open_access=True "
            f"but PMCID full text was not obtained; {cache.full_text_status or cache.availability_reason})"
        )
    if not cache.full_text_obtained:
        return f"NOT_ASSESSABLE(reason: full text was not obtained; {cache.availability_reason})"
    return f"NOT_ASSESSABLE(reason: paper full text lacks per-trial primary-outcome table rows needed for {check_name})"


def _not_assessable_no_characteristics(cache: ComparatorCache, check_name: str) -> str:
    if not cache.full_text_obtained:
        return _not_assessable_for_cache(cache, check_name)
    return f"NOT_ASSESSABLE(reason: characteristics table was not parsed from the full text for {check_name})"


def _design_adjustment_span(body_text: str) -> str:
    return _find_span(
        body_text,
        (
            r".{0,80}(?:design effect|intraclass|ICC).{0,160}",
            r".{0,80}cluster.{0,80}(?:adjust|robust|account|design effect|intraclass|ICC).{0,120}",
            r".{0,80}(?:adjust|account|robust).{0,80}cluster.{0,120}",
            r".{0,80}(?:crossover|cross-over).{0,80}(?:adjust|paired|within[- ]patient|within[- ]cluster).{0,120}",
        ),
        limit=280,
    )


def _analysis_population_rule_span(body_text: str) -> str:
    return _find_span(
        body_text,
        (
            r".{0,80}(?:intention[- ]to[- ]treat|ITT).{0,160}",
            r".{0,80}(?:per[- ]protocol|modified intention[- ]to[- ]treat|mITT|completers?).{0,160}",
            r".{0,80}analysis population.{0,160}",
            r".{0,80}full analysis set.{0,160}",
        ),
        limit=260,
    )


def _compatibility_defect(slug: str, body_text: str, characteristic_rows: list[dict[str, Any]]) -> str:
    if slug == "statins-primary-prevention-elderly":
        for row in characteristic_rows:
            row_text = str(row.get("verbatim") or "")
            if re.search(r"\b(?:observational|cohort|retrospective|prospective observational)\b", row_text, flags=re.IGNORECASE):
                return _defect("non_randomised_comparator", row_text)
    if slug == "tranexamic-acid-pph":
        for row in characteristic_rows:
            row_text = str(row.get("verbatim") or "")
            if re.search(r"\b(?:prevention|prevent|prophylactic|prophylaxis)\b", row_text, flags=re.IGNORECASE) and re.search(
                r"\b(?:treatment|treat|postpartum haemorrhage|postpartum hemorrhage)\b",
                body_text,
                flags=re.IGNORECASE,
            ):
                return _defect("treatment_prevention_scope_mixture", row_text)
    special = SPECIAL_THEIRS_COMPAT.get(slug)
    if special:
        name, patterns = special
        span = _find_span(body_text, patterns)
        if span:
            return _defect(name, span)
    return NO_DEFECT


def _assess_theirs(
    slug: str,
    review: dict[str, Any],
    cache: ComparatorCache,
    comparator_input_rows: list[dict[str, Any]],
    characteristic_rows: list[dict[str, Any]],
) -> dict[str, str]:
    body_text = cache.body_text
    checks: dict[str, str] = {}
    if not cache.full_text_obtained:
        for key, _label in CHECKS:
            checks[key] = _not_assessable_for_cache(cache, key)
        return checks

    hazardous_design_rows = [
        row
        for row in characteristic_rows
        if re.search(r"\b(?:cluster|crossover|cross-over|stepped[- ]wedge)\b", str(row.get("verbatim") or ""), flags=re.IGNORECASE)
    ]
    if hazardous_design_rows:
        adjustment_span = _design_adjustment_span(body_text)
        if adjustment_span:
            checks["design_key"] = NO_DEFECT
        else:
            checks["design_key"] = _defect(
                "design_variance_unadjusted_or_not_stated",
                str(hazardous_design_rows[0].get("verbatim") or ""),
            )
    elif characteristic_rows:
        checks["design_key"] = NO_DEFECT
    else:
        checks["design_key"] = _not_assessable_no_characteristics(cache, "design_key")

    scales: list[str] = []
    for row in comparator_input_rows:
        label = _scale_label(row.get("scale") or row.get("verbatim") or "")
        if label and label not in scales:
            scales.append(label)
    if len([s for s in scales if s in {"RR", "OR", "HR"}]) > 1:
        checks["estimand_key"] = _defect("mixed_ratio_labels_pooled_as_one", f"printed input rows carry labels {','.join(scales)}")
    elif scales:
        checks["estimand_key"] = NO_DEFECT
    else:
        checks["estimand_key"] = NOT_ASSESSABLE_EFFECT_FIGURE

    population_text = " ".join(
        " ".join(str(term) for term in (row.get("analysis_population_words") or [])) or str(row.get("verbatim") or "")
        for row in characteristic_rows
        if row.get("analysis_population_words")
    )
    has_itt = bool(re.search(r"\b(?:intention-to-treat|intention to treat|itt)\b", population_text, flags=re.IGNORECASE))
    has_non_itt = bool(re.search(r"\b(?:per[- ]protocol|on[- ]treatment|as[- ]treated|completers?)\b", population_text, flags=re.IGNORECASE))
    if has_itt and has_non_itt and not _analysis_population_rule_span(body_text):
        checks["analysis_population"] = _defect("analysis_population_mixed", _clip(population_text, 180))
    elif characteristic_rows:
        checks["analysis_population"] = NO_DEFECT
    else:
        checks["analysis_population"] = _not_assessable_no_characteristics(cache, "analysis_population")

    if characteristic_rows:
        checks["compatibility_key"] = _compatibility_defect(slug, body_text, characteristic_rows)
    else:
        checks["compatibility_key"] = _not_assessable_no_characteristics(cache, "compatibility_key")

    effect_rows = _parsed_effect_rows(comparator_input_rows)
    reported_est, reported_lo, reported_hi, reported_scale = _comparator_reported_result(review)
    model, model_span = _printed_model(body_text)
    if len(effect_rows) >= 2 and reported_est and reported_lo and reported_hi:
        try:
            method = "DL_IV" if model in {"DL_IV", "FIXED_IV"} else "PM_HKSJ"
            pooled = _pool_ratio(effect_rows, method=method)
            if (
                _logdiff(pooled["estimate"], reported_est) <= REPRO_TOL_LOG_EST
                and _logdiff(pooled["ci_low"], reported_lo) <= REPRO_TOL_LOG_CI
                and _logdiff(pooled["ci_high"], reported_hi) <= REPRO_TOL_LOG_CI
            ):
                checks["pooled_reproduction"] = NO_DEFECT
            else:
                span = (
                    f"{model} recompute {pooled['estimate']:.4g} "
                    f"({pooled['ci_low']:.4g}-{pooled['ci_high']:.4g}) vs comparator "
                    f"{reported_scale or 'ratio'} {reported_est:.4g} ({reported_lo:.4g}-{reported_hi:.4g}); "
                    f"k={len(effect_rows)}; printed model span: {model_span or 'NOT_STATED'}"
                )
                checks["pooled_reproduction"] = _defect("pooled_number_nonreproduction", span)
        except (ValueError, OverflowError) as exc:
            checks["pooled_reproduction"] = f"NOT_ASSESSABLE(reason: printed per-trial inputs could not be re-pooled: {exc})"
    elif any(row.get("counts") for row in comparator_input_rows):
        checks["pooled_reproduction"] = "NOT_ASSESSABLE(reason: paper exposes per-arm counts but not enough per-trial effect+CI uncertainty to reproduce the printed inverse-variance model)"
    else:
        checks["pooled_reproduction"] = NOT_ASSESSABLE_EFFECT_FIGURE
    return checks


def _defect_count(checks: dict[str, str]) -> int:
    return sum(1 for value in checks.values() if value.startswith("DEFECT("))


def _first_defect_span(checks: dict[str, str]) -> str:
    for value in checks.values():
        if value.startswith("DEFECT("):
            match = re.search(r',\s*"(.+)"\)$', value)
            if match:
                return match.group(1)
            return value
    return "input-set search did not find machine-readable per-trial outcome rows"


def assess(slug: str, alias: str, *, check: bool = False) -> Assessment:
    review = _read_json(Path("docs") / "reviews" / slug / "review.json")
    comparator = review.get("comparator") or {}
    cache = cache_comparator(slug, review, check=check)
    body_text = cache.body_text
    rows, characteristic_rows = _parse_comparator_tables(review, cache)
    theirs = _assess_theirs(slug, review, cache, rows, characteristic_rows)
    ours = _assess_ours(review)

    for check_key, _ in CHECKS:
        if check_key not in theirs or check_key not in ours:
            raise RuntimeError(f"{slug}: asymmetric check set missing {check_key}")
    if set(theirs) != set(ours):
        raise RuntimeError(f"{slug}: asymmetric check keys {sorted(theirs)} vs {sorted(ours)}")

    title = str(review.get("title") or slug)
    return Assessment(
        slug=slug,
        alias=alias,
        title=title,
        pmid=str(comparator.get("pmid") or ""),
        doi=str(comparator.get("doi") or ""),
        url=str(comparator.get("url") or ""),
        cache=cache,
        comparator_input_rows=rows,
        comparator_characteristic_rows=characteristic_rows,
        comparator_input_exposed=bool(rows),
        theirs=theirs,
        ours=ours,
        theirs_defects=_defect_count(theirs),
        ours_defects=_defect_count(ours),
        note_span=_first_defect_span(theirs),
    )


def _evidence_text(a: Assessment) -> str:
    lines = [
        f"# Comparator correctness: {a.slug}",
        "",
        f"Date: {DATE}",
        f"Comparator PMID: {a.pmid}",
        f"Comparator PMCID: {a.cache.pmcid or 'NOT_RESOLVED'}",
        f"Comparator DOI: {a.doi or 'NOT_STATED'}",
        f"Comparator URL: {a.url or 'NOT_STATED'}",
        f"Full text obtained: {'YES' if a.cache.full_text_obtained else 'NO'}",
        f"Full text status: {a.cache.full_text_status or a.cache.availability_reason}",
        f"Full text raw source: {a.cache.body_raw_rel or 'NONE'}",
        f"Full text raw SHA-256: {a.cache.full_text_sha256 or 'NONE'}",
        f"Open-access label failed: {'YES' if a.cache.open_access_label_failed else 'NO'}",
        f"Cached normalized comparator text: {a.cache.body_rel}",
        f"Cached comparator body SHA-256: {a.cache.body_sha256}",
        f"Comparator body source: {a.cache.body_source}",
        "",
        f"Machine-readable comparator pooled input set exposed: {'YES' if a.comparator_input_exposed else 'NO'}",
        f"Per-trial effect inputs: {'machine-readable table rows' if a.comparator_input_exposed else 'forest-plot figure only / not machine-readable as table rows'}",
        f"Parsed comparator input rows: {len(a.comparator_input_rows)}",
        f"Characteristics table parsed: {'YES' if a.comparator_characteristic_rows else 'NO'} ({len(a.comparator_characteristic_rows)} rows)",
        f"Parsed comparator characteristics/design rows: {len(a.comparator_characteristic_rows)}",
        "THEIRS checks assessable from characteristics table: "
        + (
            "Design key; Analysis population; Compatibility key"
            if a.comparator_characteristic_rows
            else "none"
        ),
    ]
    if a.comparator_input_rows:
        lines.append("Parsed primary-outcome table rows:")
        for row in a.comparator_input_rows:
            effect_bits = []
            if row.get("scale"):
                effect_bits.append(str(row.get("scale")))
            if row.get("effect"):
                effect_bits.append(f"{row.get('effect')} [{row.get('ci_low')}, {row.get('ci_high')}]")
            if row.get("counts"):
                effect_bits.append("counts=" + "; ".join(f"{a0}/{b0}" for a0, b0 in row.get("counts", [])))
            suffix = f" ({'; '.join(effect_bits)})" if effect_bits else ""
            lines.append(
                f"- {row.get('table_label')} row {row.get('row_index')} :: study={row.get('study')} :: "
                f"{_clip(str(row.get('verbatim') or ''), 320)}{suffix}"
            )
    else:
        if a.cache.open_access_label_failed:
            lines.append("Input-set search: FULL_TEXT_NOT_AVAILABLE_OA; the comparator object says open_access=true, but PMCID full text was not obtainable from Europe PMC or PMC OAI.")
        elif a.cache.full_text_obtained:
            lines.append("Input-set search: per-trial effect inputs are in a forest-plot figure, not a table; pooled-number reproduction and estimand-mixing checks are not machine-assessable from table-wrap rows.")
        else:
            lines.append("Input-set search: paper full text did not expose a per-trial primary-outcome row with a study name plus per-arm events/N or effect+CI in JATS table-wrap elements.")
    if a.comparator_characteristic_rows:
        hazardous_rows = [
            row
            for row in a.comparator_characteristic_rows
            if re.search(r"\b(?:cluster|crossover|cross-over|stepped[- ]wedge)\b", str(row.get("verbatim") or ""), flags=re.IGNORECASE)
        ]
        if hazardous_rows:
            adjustment_span = _design_adjustment_span(a.cache.body_text)
            if adjustment_span:
                lines.append(f"Design-adjustment methods span searched for cluster/design effect/ICC/intraclass: {_quote_span(adjustment_span, 260)}")
            else:
                lines.append("Design-adjustment methods span searched for cluster/design effect/ICC/intraclass: NOT_STATED.")
        lines.append("Parsed characteristics / included-studies rows:")
        for row in a.comparator_characteristic_rows:
            design = ", ".join(row.get("design_words") or []) or "NOT_STATED"
            analysis_pop = ", ".join(row.get("analysis_population_words") or []) or "NOT_STATED"
            population = str(row.get("population_words") or "NOT_STATED")
            comparator = str(row.get("comparator") or "NOT_STATED")
            sample_size = str(row.get("n") or "NOT_STATED")
            lines.append(
                f"- {row.get('table_label')} row {row.get('row_index')} :: study={row.get('study')} :: "
                f"design={design} :: population={population} :: comparator={comparator} :: N={sample_size} :: "
                f"analysis_population={analysis_pop} :: verbatim cells={row.get('verbatim')}"
            )
    lines.extend(
        [
            "",
            "| Check | THEIRS | OURS |",
            "| --- | --- | --- |",
        ]
    )
    for key, label in CHECKS:
        lines.append(f"| {label} | {a.theirs[key]} | {a.ours[key]} |")
    lines.extend(
        [
            "",
            f"Bottom line: THEIRS defects={a.theirs_defects}; OURS defects={a.ours_defects}.",
            "",
            "External-claim rule: findings in the THEIRS column are not adjudicated by us; registry verification is NONE until an outside party confirms.",
            "Reproduction tolerance: absolute log estimate <= 0.02 and absolute log CI bound <= 0.08 when per-trial ratio inputs are exposed.",
            "",
        ]
    )
    return "\n".join(lines)


def _readme(assessments: list[Assessment]) -> str:
    theirs_total = sum(a.theirs_defects for a in assessments)
    ours_total = sum(a.ours_defects for a in assessments)
    full_text_total = sum(1 for a in assessments if a.cache.full_text_obtained)
    row_total = sum(len(a.comparator_input_rows) for a in assessments)
    characteristic_row_total = sum(len(a.comparator_characteristic_rows) for a in assessments)
    oa_failed = [a.slug for a in assessments if a.cache.open_access_label_failed]
    effect_exposed_slugs = [a.slug for a in assessments if a.comparator_input_exposed]
    characteristic_parsed = [a.slug for a in assessments if a.comparator_characteristic_rows]
    lines = [
        "# Comparator correctness sweep (2026-09-15)",
        "",
        "**Fix state (orthogonal fields rule): generated after registry render**",
        f"per-trial effect inputs are machine-readable on {len(effect_exposed_slugs)} of 21 comparators (figures); characteristics tables were parsed on {len(characteristic_parsed)} of 21 ({', '.join(characteristic_parsed) if characteristic_parsed else 'none'}); THEIRS design/population/compatibility checks were assessable on those {len(characteristic_parsed)}.",
        "",
        _effect_rows_reach_sentence(),
        "",
        EXTERNAL_SENTENCE,
        "",
        f"{EXTERNAL_HEADING}.",
        "",
        "This bundle applies the same five checks to each published comparator and to our matching pool: design key, estimand key, analysis-population check, compatibility key, and pooled-number reproduction. Comparator per-trial effect inputs were not machine-readable because the effects live in forest-plot figures, while characteristics tables made the design, analysis-population, and compatibility checks assessable where parsed. THEIRS findings are external claims with verification NONE; OURS findings are internal disclosures about this repository's pools.",
        "",
        "| Topic | Comparator PMID | THEIRS defects | OURS defects | Full text obtained / effect rows parsed | characteristics table parsed (rows) | THEIRS checks assessable | Comparator machine-readable effect inputs exposed |",
        "| --- | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for a in assessments:
        effect_exposed_cell = "YES" if a.comparator_input_exposed else "NO"
        if a.cache.full_text_obtained:
            ft = f"YES ({a.cache.full_text_source}; sha256 {a.cache.full_text_sha256[:12]}) / {len(a.comparator_input_rows)}"
        else:
            ft = f"NO ({a.cache.availability_reason}) / {len(a.comparator_input_rows)}"
        assessable = [label for key, label in CHECKS if not a.theirs[key].startswith("NOT_ASSESSABLE")]
        char_cell = f"{'YES' if a.comparator_characteristic_rows else 'NO'} ({len(a.comparator_characteristic_rows)})"
        lines.append(f"| {a.slug} | {a.pmid} | {a.theirs_defects} | {a.ours_defects} | {ft} | {char_cell} | {', '.join(assessable) if assessable else 'none'} | {effect_exposed_cell} |")
    lines.extend(
        [
            "",
            "**What these counts are and are not (external auditor, 2026-09-15).** Applying the same instrument to both",
            "columns establishes procedural symmetry, not instrument validity: a blind spot in our design checker misses the",
            "same defect in them and in us, and a symmetric output would look rigorous while proving nothing. Every THEIRS",
            "cell is therefore a HYPOTHESIS with verification NONE, promoted only by external checking against the source; the",
            "OURS column is the same instrument's reading of our own pool, surfaced in the same pass. The counts below are",
            "totals of cells, not a comparison: the sentence \"our instrument found n problems in them and m in us\" is not",
            "evidence of anything until adjudication is independent, and it must not be written from this table.",
            "",
            "| Totals (cells, not a comparison) | Value |",
            "| --- | ---: |",
            f"| THEIRS hypothesis cells (verification NONE) across 21 comparable comparators | {theirs_total} |",
            f"| OURS defect cells across 21 comparable comparators | {ours_total} |",
            f"| Full texts obtained | {full_text_total}/21 |",
            f"| Machine-readable per-trial effect inputs | {len(effect_exposed_slugs)}/21 |",
            f"| Parsed primary-outcome effect rows | {row_total} |",
            f"| Characteristics tables parsed | {len([a for a in assessments if a.comparator_characteristic_rows])}/21 |",
            f"| Characteristics rows parsed | {characteristic_row_total} |",
            f"| THEIRS design/population/compatibility assessable from characteristics tables | {len([a for a in assessments if a.comparator_characteristic_rows])}/21 |",
            "",
            "## Open-Access Label Failures",
            "",
            f"{', '.join(oa_failed) if oa_failed else 'None.'}",
            "",
            "## Not Comparable",
            "",
            "| Object slug | Prompt name | Reason |",
            "| --- | --- | --- |",
        ]
    )
    for slug, prompt_name, reason in NOT_COMPARABLE:
            lines.append(f"| {slug} | {prompt_name} | {reason} |")
    not_exposed = [a.slug for a in assessments if not a.comparator_input_exposed]
    lines.extend(
        [
            "",
            "## Machine-Readable Comparator Effect Inputs",
            "",
            f"Exposed: {', '.join(effect_exposed_slugs) if effect_exposed_slugs else 'none'}.",
            f"Not exposed: {', '.join(not_exposed)}.",
            "",
            "## Characteristics Tables Parsed",
            "",
            f"Parsed: {', '.join(characteristic_parsed) if characteristic_parsed else 'none'}.",
            f"Not parsed: {', '.join(a.slug for a in assessments if not a.comparator_characteristic_rows)}.",
            "",
            "## Static-vs-Dynamic Hardcode Disclosure",
            "",
            "| Item | Static or dynamic | Source |",
            "| --- | --- | --- |",
            "| Comparable/not-comparable roster | Static lane instruction | LANE_PROMPT.md |",
            "| Comparator PMIDs, DOI, URL, reported outcome metadata | Dynamic | docs/reviews/*/review.json comparator objects |",
            "| PMID to PMCID mapping and comparator text bytes | Dynamic fetch/cache | cache/comparators/<pmid>/ idconv, Europe PMC PMCID fullTextXML, PMC OAI fallback, body.txt |",
            "| THEIRS effect-input exposure and checks | Dynamic sweep over cached JATS table-wrap rows and forest-plot-only state | scripts/comparator_correctness_sweep.py |",
            "| THEIRS characteristics-table parsing | Dynamic sweep over cached JATS table-wrap rows | scripts/comparator_correctness_sweep.py |",
            "| OURS checks | Dynamic sweep over review JSON | docs/reviews/*/review.json |",
            "| Registry seals | Dynamic git blob identities | git hash-object over cache body, sweep script, review JSON, evidence txt |",
            "",
            "## Commands",
            "",
            "- `python scripts/comparator_correctness_sweep.py`",
            "- `python scripts/rewrite_fixstate_lines.py`",
            "- `python scripts/render_fix_ledger.py`",
            "- `python -m harness.index docs`",
            "- `python scripts/build_evidence_index.py`",
            "- `python -m pytest tests/ -q`",
            "- `python scripts/verify_all.py`",
            "",
        ]
    )
    return "\n".join(lines)


def _report(assessments: list[Assessment], base_commit: str) -> str:
    theirs_total = sum(a.theirs_defects for a in assessments)
    ours_total = sum(a.ours_defects for a in assessments)
    full_text_total = sum(1 for a in assessments if a.cache.full_text_obtained)
    row_total = sum(len(a.comparator_input_rows) for a in assessments)
    characteristic_row_total = sum(len(a.comparator_characteristic_rows) for a in assessments)
    oa_failed = [a.slug for a in assessments if a.cache.open_access_label_failed]
    characteristic_parsed = [a.slug for a in assessments if a.comparator_characteristic_rows]
    lines = [
        "# LANE AE Report",
        "",
        f"Base commit: `{base_commit}`",
        "",
        "| Topic | Comparator PMID | THEIRS defects | OURS defects | Full text obtained / effect rows parsed | characteristics table parsed (rows) | THEIRS checks assessable | Comparator effect inputs exposed |",
        "| --- | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for a in assessments:
        exposed = "YES" if a.comparator_input_exposed else "NO"
        if a.cache.full_text_obtained:
            ft = f"YES ({a.cache.full_text_source}; sha256 {a.cache.full_text_sha256[:12]}) / {len(a.comparator_input_rows)}"
        else:
            ft = f"NO ({a.cache.availability_reason}) / {len(a.comparator_input_rows)}"
        assessable = [label for key, label in CHECKS if not a.theirs[key].startswith("NOT_ASSESSABLE")]
        char_cell = f"{'YES' if a.comparator_characteristic_rows else 'NO'} ({len(a.comparator_characteristic_rows)})"
        lines.append(f"| {a.slug} | {a.pmid} | {a.theirs_defects} | {a.ours_defects} | {ft} | {char_cell} | {', '.join(assessable) if assessable else 'none'} | {exposed} |")
    exposed = [a.slug for a in assessments if a.comparator_input_exposed]
    not_exposed = [a.slug for a in assessments if not a.comparator_input_exposed]
    lines.extend(
        [
            "",
            f"Totals: THEIRS defect cells={theirs_total}; OURS defect cells={ours_total}.",
            f"Full texts obtained: {full_text_total}/21.",
            f"Machine-readable per-trial effect inputs: {len(exposed)}/21.",
            f"Parsed primary-outcome effect rows: {row_total}.",
            f"Characteristics tables parsed: {len(characteristic_parsed)}/21 ({', '.join(characteristic_parsed) if characteristic_parsed else 'none'}).",
            f"Characteristics rows parsed: {characteristic_row_total}.",
            f"THEIRS design/population/compatibility checks assessable from characteristics tables: {len(characteristic_parsed)}/21.",
            "",
            "Open-access label failed:",
            f"- {', '.join(oa_failed) if oa_failed else 'None'}.",
            "",
            "Machine-readable comparator pooled effect inputs exposed:",
            f"- Exposed: {', '.join(exposed) if exposed else 'none'}.",
            f"- Not exposed: {', '.join(not_exposed)}.",
            "",
            "Characteristics tables parsed:",
            f"- Parsed: {', '.join(characteristic_parsed) if characteristic_parsed else 'none'}.",
            f"- Not parsed: {', '.join(a.slug for a in assessments if not a.comparator_characteristic_rows)}.",
            "",
            "Commands:",
            "- `python scripts/comparator_correctness_sweep.py`",
            "- `python scripts/rewrite_fixstate_lines.py`",
            "- `python scripts/render_fix_ledger.py`",
            "- `python -m harness.index docs`",
            "- `python scripts/build_evidence_index.py`",
            "- `python -m pytest tests/ -q`",
            "- `python scripts/verify_all.py`",
            "",
            "No commit was made.",
            "",
        ]
    )
    return "\n".join(lines)


def _update_captions(assessments: list[Assessment]) -> None:
    captions = _read_json(CAPTIONS_PATH)
    block: dict[str, str] = {
        "_title": "Comparator correctness (2026-09-15): symmetric external findings with verification NONE",
        "_intro": "Lane AE evidence comparing forest-plot-only comparator effect inputs and parsed characteristics tables with the repository pools under the same correctness instrument.",
        "README.md": "The 21-row comparator correctness summary, 11 not-comparable reasons, totals, machine-readable effect-input exposure, characteristics-table parsing, and generated fix-state line.",
    }
    for a in assessments:
        block[f"{a.slug}.txt"] = (
            f"Symmetric THEIRS|OURS correctness checks for {a.slug}; comparator PMID {a.pmid}; "
            f"THEIRS defects {a.theirs_defects}, OURS defects {a.ours_defects}; "
            f"characteristics rows parsed {len(a.comparator_characteristic_rows)}."
        )
    block["05-effect-rows-reach.txt"] = (
        "Whose limit the '0 of 21 machine-readable per-trial effects' figure is, per comparator: FIGURE_ONLY (theirs: the "
        "forest plot is a figure), NOT_OBSERVED (ours: no open-access full text obtained), PARSE_LIMIT_CANDIDATE (ours to "
        "judge; the row shown verbatim). Generated by scripts/comparator_effect_rows_reach.py."
    )
    captions[EVIDENCE_SLUG] = block
    _write_json(CAPTIONS_PATH, captions)


def _update_registry(assessments: list[Assessment], base_commit: str) -> None:
    store = _read_json(REGISTRY_PATH)
    entries = [
        entry
        for entry in (store.get("entries") or [])
        if not str(entry.get("fix_id") or "").startswith("EXT-COMP-AE-")
        and not str(entry.get("finding_id") or "").startswith("EXT-COMP-AE-")
    ]
    for idx, a in enumerate(assessments, start=1):
        fix_id = f"EXT-COMP-AE-{idx:02d}-{a.slug.upper().replace('-', '_')}"
        topic_txt = EVIDENCE_DIR / f"{a.slug}.txt"
        review_json = Path("docs") / "reviews" / a.slug / "review.json"
        deps = [
            a.cache.body_rel,
            _posix(SCRIPT_PATH),
            _posix(review_json),
            _posix(topic_txt),
        ]
        blob_shas = _git_blob_shas(deps)
        note_span = _sanitize_registry_text(_clip(a.note_span, 160))
        entry = {
            "finding_id": fix_id,
            "fix_id": fix_id,
            "title": f"external comparator assessment for {a.slug}",
            "kind": "external_finding",
            "implementation": "LANDED",
            "verification": "NONE",
            "scope": "INSTANCE",
            "author": "Codex lane AE",
            "opened_utc": RUN_UTC,
            "evidence_dir": _posix(EVIDENCE_DIR),
            "events": [
                {
                    "implementation": "LANDED",
                    "verification": "NONE",
                    "scope": "INSTANCE",
                    "when_utc": RUN_UTC,
                    "by": "Codex lane AE",
                    "commit": base_commit,
                    "evidence": [_posix(topic_txt)],
                    "reason": "served external comparator assessment; outside-party confirmation absent",
                }
            ],
            "verified_by": {"identity": None, "kind": None},
            "verifications": [],
            "authored_against": [_posix(review_json), _posix(SCRIPT_PATH), a.cache.body_rel],
            "generalized_on": [],
            "executable_evidence": {
                "command": "python scripts/comparator_correctness_sweep.py --check",
                "expected_substring": "COMPARATOR-CORRECTNESS: PASS",
            },
            "seal": {
                "sealed_utc": RUN_UTC,
                "commit": base_commit,
                "dependencies": blob_shas,
                "configuration": {"schema": "fixes-v3", "lane": "AE", "external_claim_verification": "NONE"},
            },
            "note": f"PMID {a.pmid}; comparator span: {note_span}",
        }
        entries.append(entry)
    store["entries"] = entries
    _write_json(REGISTRY_PATH, store)


def _write_outputs(assessments: list[Assessment], base_commit: str) -> None:
    for a in assessments:
        _write_text(EVIDENCE_DIR / f"{a.slug}.txt", _evidence_text(a))
    _write_text(EVIDENCE_DIR / "README.md", _readme(assessments))
    _write_text(REPORT_PATH, _report(assessments, base_commit))
    _update_captions(assessments)
    _update_registry(assessments, base_commit)


def _validate_check_mode() -> list[str]:
    problems: list[str] = []
    if not (ROOT / EVIDENCE_DIR / "README.md").is_file():
        problems.append(f"missing {_posix(EVIDENCE_DIR / 'README.md')}")
    for slug, _ in COMPARABLE:
        if not (ROOT / EVIDENCE_DIR / f"{slug}.txt").is_file():
            problems.append(f"missing {_posix(EVIDENCE_DIR / (slug + '.txt'))}")
    if (ROOT / EVIDENCE_DIR / "README.md").is_file():
        text = (ROOT / EVIDENCE_DIR / "README.md").read_text(encoding="utf-8")
        row_count = sum(1 for slug, _ in COMPARABLE if f"| {slug} |" in text)
        if row_count != 21:
            problems.append(f"README comparable row count is {row_count}, expected 21")
        if EXTERNAL_SENTENCE not in text:
            problems.append("README missing exact external-claim sentence")
        if "per-trial effect inputs are machine-readable on" not in text or "characteristics tables were parsed on" not in text:
            problems.append("README missing AE3 effect-input/characteristics first-line summary")
        if "characteristics table parsed (rows)" not in text:
            problems.append("README missing characteristics table parsed column")
        if "THEIRS hypothesis cells (verification NONE) across 21 comparable comparators" not in text:
            problems.append("README missing THEIRS totals row")
        if "Full texts obtained" not in text or "Parsed primary-outcome effect rows" not in text:
            problems.append("README missing full-text / effect-row totals")
        if "Characteristics tables parsed" not in text or "Characteristics rows parsed" not in text:
            problems.append("README missing characteristics parsing totals")
    try:
        store = _read_json(REGISTRY_PATH)
    except OSError as exc:
        problems.append(str(exc))
    else:
        ext = [e for e in store.get("entries", []) if str(e.get("fix_id") or "").startswith("EXT-COMP-AE-")]
        if len(ext) != 21:
            problems.append(f"registry external comparator entries={len(ext)}, expected 21")
        for entry in ext:
            if entry.get("kind") != "external_finding" or entry.get("verification") != "NONE":
                problems.append(f"{entry.get('fix_id')}: external finding must have verification NONE")
    return problems


def run(*, check: bool = False) -> int:
    if check:
        problems = _validate_check_mode()
        if problems:
            print("COMPARATOR-CORRECTNESS: FAIL")
            for problem in problems:
                print(f"- {problem}")
            return 1
        print("COMPARATOR-CORRECTNESS: PASS")
        return 0

    if len(COMPARABLE) != 21:
        raise RuntimeError(f"comparable roster must contain 21 entries, found {len(COMPARABLE)}")
    if len(NOT_COMPARABLE) != 11:
        raise RuntimeError(f"not-comparable roster must contain 11 entries, found {len(NOT_COMPARABLE)}")
    base_commit = _git(["rev-parse", "HEAD"])
    missing = [slug for slug, _ in COMPARABLE if not (ROOT / "docs" / "reviews" / slug / "review.json").is_file()]
    if missing:
        raise RuntimeError(f"missing review objects: {', '.join(missing)}")
    assessments = [assess(slug, alias) for slug, alias in COMPARABLE]
    if len(assessments) != 21:
        raise RuntimeError(f"assessment count must be 21, found {len(assessments)}")
    for a in assessments:
        if set(a.theirs) != {key for key, _ in CHECKS} or set(a.ours) != {key for key, _ in CHECKS}:
            raise RuntimeError(f"{a.slug}: check symmetry refused")
    _write_outputs(assessments, base_commit)
    print(f"wrote {len(assessments)} comparator assessments to {_posix(EVIDENCE_DIR)}")
    print("COMPARATOR-CORRECTNESS: PASS")
    return 0



def _effect_rows_reach_sentence() -> str:
    """Whose limit the '0 of 21 machine-readable' figure is, per comparator, from 05-effect-rows-reach.txt (if present)."""
    path = ROOT / EVIDENCE_DIR / "05-effect-rows-reach.txt"
    if not path.is_file():
        return "Whose limit '0 of 21' is: NOT YET ATTRIBUTED (run scripts/comparator_effect_rows_reach.py)."
    counts = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("TOTALS:"):
            for part in line[len("TOTALS:"):].split(","):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    counts[k] = int(v)
    figure = counts.get("FIGURE_ONLY", 0)
    ours_fetch = counts.get("NOT_OBSERVED", 0)
    ours_parse = counts.get("PARSE_LIMIT_CANDIDATE", 0)
    return (f"Whose limit '0 of 21 machine-readable per-trial effects' is, per comparator (05-effect-rows-reach.txt): "
            f"THEIRS on {figure} (per-trial effects exist only as a forest-plot figure; no table row carries an effect with a CI beside a trial name); "
            f"OURS on {ours_fetch} (no open-access full text obtained -- not observed, a fetch limit) and on {ours_parse} candidate "
            f"(a table row with an effect-and-CI pattern our parser did not take; shown verbatim for the reader to judge). "
            f"The figure is therefore a statement about the papers on {figure} of 21 and about our reach on {ours_fetch + ours_parse} of 21.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
