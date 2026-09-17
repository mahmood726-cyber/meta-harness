"""Per-trial funding / conflict-of-interest disclosure (ME-32).

The canonical per-trial funding object is:
    {status, sponsor_class, sponsors[], role[], basis_span, source_id}

Legacy page/tests still read {type, span, source, scanned}; scan_pooled emits both shapes so this lane can
be merged without forcing concurrent render lanes to move at the same time. Funding is source-backed:
abstract/full text funding sentences first, registry sponsor rows second. Author affiliations can set
industry_authors_present, but never classify a sponsor.
"""
from __future__ import annotations

import re
from typing import Any

from . import aact

STATUS_STATED = "stated_in_held_text"
STATUS_REGISTRY = "stated_in_registry"
STATUS_NONE = "none_stated_in_held_text"
STATUS_IN_SOURCE_NOT_HELD = "in_source_not_held"

CLASS_INDUSTRY = "industry"
CLASS_PUBLIC = "public"
CLASS_MIXED = "mixed"
CLASS_NONE = "none_stated_in_held_text"
CLASS_IN_SOURCE_NOT_HELD = "in_source_not_held"

_STRONG_ANCHOR = re.compile(
    r"(primary\s+funding\s+source|funded by|funding was provided|funding(?:\s+source)?\s*:"
    r"|financial support|grants?\s+from|sponsored by|study sponsor"
    r"|role of the (?:funding source|sponsor)"
    r"|this (?:study|trial|work|research) was (?:funded|supported|sponsored))",
    re.I,
)
_WEAK_ANCHOR = re.compile(r"supported by", re.I)

_INDUSTRY = re.compile(
    r"\b(pharmaceutical|pharmaceuticals|biopharmaceutical|Inc\.|Incorporated|Ltd\.?|GmbH|LLC"
    r"|Co\.,? Ltd|manufacturer|Novo Nordisk|Pfizer|Janssen|Johnson\s*&\s*Johnson|AstraZeneca"
    r"|Boehringer|Novartis|Bayer|Merck|MSD|Sanofi|GlaxoSmithKline|GSK|Eli Lilly|Lilly"
    r"|AbbVie|Amgen|Bristol[- ]Myers|Takeda|Roche|Genentech|Gilead|Servier|Daiichi"
    r"|Otsuka|Lundbeck|Actelion|Vertex|Vifor|CSL|Mylan|Viatris|Teva|UCB|Grunenthal"
    r"|Astellas|Bausch|Reckitt|Mundipharma|Cipla|Amarin|Viollier|Pharma\b|Pharma,"
    r"|Therapeutics\b|Biosciences\b|Biotech|Laboratories\b|Sciences, Inc"
    r"|(?-i:[A-Z][A-Za-z]+ AG))\b",
    re.I,
)

_PUBLIC = re.compile(
    r"\b(National Institutes of Health|NIH\b|NIHR|National Institute for Health(?: and Care)? Research"
    r"|Medical Research Council|MRC\b|Wellcome|Bill (?:& |and )?Melinda Gates|Gates Foundation"
    r"|foundation|university|college of|government|Ministry of Health|Department of Health"
    r"|European (?:Commission|Union)|Horizon 20\d\d|Canadian Institutes of Health|NHMRC"
    r"|charit(?:y|able)|academic|institutional funds|received no (?:specific |external )?funding"
    r"|no external funding|no specific grant|not (?:externally )?funded)\b",
    re.I,
)

_DRUG_SUPPLY = re.compile(
    r"(study drug|study medication|trial (?:drug|medication)|active drug|investigational "
    r"(?:drug|product|agent)|drugs?|medication|tablets|capsules|treatment|placebo)s?\s+"
    r"(?:and (?:matching )?placebo\s+)?(?:were|was|is|are)?\s*(?:kindly |generously )?"
    r"(?:provided|supplied|donated|manufactured|furnished|gifted)\s+by",
    re.I,
)

_FUNDING_POINTER = re.compile(
    r"funding[^.]{0,90}(supplement|appendix|supporting information|available (?:on request|online))",
    re.I,
)

_INDUSTRY_AUTHORS = re.compile(
    r"\b(?:employees? of|employed by|stockholders? of|hold company equity).*?"
    r"(?:Janssen|Pfizer|Novo Nordisk|Boehringer|AstraZeneca|Bayer|Merck|Johnson\s*&\s*Johnson)"
    r"|(?:Janssen|Pfizer|Novo Nordisk|Boehringer|AstraZeneca|Bayer|Merck|Johnson\s*&\s*Johnson)\s+employees?",
    re.I | re.S,
)

_ROLE_PATTERNS = (
    ("design", re.compile(r"\bdesign(?:ed)?\b", re.I)),
    ("conduct", re.compile(r"\b(?:conduct(?:ed)?|performed)\b", re.I)),
    ("data_collection", re.compile(r"\b(?:collect(?:ed|ion)|gathered)\b", re.I)),
    ("analysis", re.compile(r"\b(?:analys(?:ed|is|es)|analyz(?:ed|es|ing))\b", re.I)),
    ("manuscript_writing", re.compile(r"\b(?:wrote|writing|manuscript|first draft)\b", re.I)),
)

_NCT_RE = re.compile(r"\bNCT\d{8}\b", re.I)


def _clean(text: Any) -> str:
    return re.sub(r"\s+", " ", "" if text is None else str(text)).strip()


def _sentence_window(text: str, at: int, fwd: int = 420) -> str:
    left_candidates = [text.rfind(mark, 0, at) for mark in (".", "!", "?", "\n")]
    lo = max(left_candidates) + 1
    hi = min(len(text), at + fwd)
    m = re.search(r"(?<=[.!?])\s+(?=[A-Z(])", text[at:hi])
    if m:
        hi = at + m.end()
    return _clean(text[lo:hi])


def _roles(span: str) -> list[str]:
    out = []
    for name, pat in _ROLE_PATTERNS:
        if pat.search(span or ""):
            out.append(name)
    return out


def _class_from_markers(text: str) -> str | None:
    ind = bool(_INDUSTRY.search(text or ""))
    pub = bool(_PUBLIC.search(text or ""))
    if ind and pub:
        return CLASS_MIXED
    if ind:
        return CLASS_INDUSTRY
    if pub:
        return CLASS_PUBLIC
    return None


def _legacy_type(status: str, sponsor_class: str, scanned: str = "") -> str:
    if status == STATUS_IN_SOURCE_NOT_HELD:
        return "stated (detail in supplement, not in retrieved source)"
    if sponsor_class == CLASS_INDUSTRY:
        return "industry"
    if sponsor_class == CLASS_PUBLIC:
        return "public/non-profit"
    if sponsor_class == CLASS_MIXED:
        return "mixed"
    if sponsor_class == CLASS_IN_SOURCE_NOT_HELD:
        return "funding in source not held"
    if scanned == "full text":
        return "not stated (full text scanned)"
    return "not stated (abstract only - full text not retrieved)"


def _split_sponsors(span: str) -> list[str]:
    text = _clean(span)
    text = re.sub(
        r"^.*?(?:this (?:study|trial|work|research) was funded by|funded by|funding(?: source)?\s*:"
        r"|grants?\s+from|supported by)\s*",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"^this (?:study|trial|work|research) was funded by\s*", "", text, flags=re.I)
    text = re.split(r";|\.\s|ClinicalTrials\.gov|trial registration", text, maxsplit=1, flags=re.I)[0]
    text = re.sub(r"\band others\b", "", text, flags=re.I)
    parts = re.split(r",|\band\b|&", text)
    out = []
    for part in parts:
        s = _clean(part)
        s = re.sub(r"^(the|a|an)\s+", "", s, flags=re.I)
        s = s.strip(" .;:")
        if len(s) >= 3 and s.lower() not in {"funded", "funding", "support"}:
            out.append(s)
    return out


def _funding_object(
    *,
    status: str,
    sponsor_class: str,
    sponsors: list[str] | None = None,
    role: list[str] | None = None,
    basis_span: str = "",
    source_id: str = "",
    source_kind: str = "",
    scanned: str = "",
    note: str = "",
    industry_authors_present: bool = False,
) -> dict[str, Any]:
    obj = {
        "status": status,
        "sponsor_class": sponsor_class,
        "sponsors": sponsors or [],
        "role": role or [],
        "basis_span": basis_span,
        "source_id": source_id,
        "source_kind": source_kind,
        # Back-compat for older render/tests.
        "type": _legacy_type(status, sponsor_class, scanned),
        "span": basis_span,
        "source": source_kind or source_id,
        "scanned": scanned,
    }
    if note:
        obj["note"] = note
    if industry_authors_present:
        obj["industry_authors_present"] = True
    return obj


def detect(text: str, source_id: str = "", source_kind: str = "", scanned: str = "") -> dict[str, Any] | None:
    """Detect a held-text funding statement. Returns the canonical object plus legacy keys, or None."""
    if not text:
        return None
    fclass = None
    span = ""
    m = _STRONG_ANCHOR.search(text)
    strong = bool(m)
    if not m:
        m = _WEAK_ANCHOR.search(text)
    if m:
        win = _sentence_window(text, m.start())
        ds_in = _DRUG_SUPPLY.search(win)
        fund_win = win[:ds_in.start()] if ds_in else win
        fclass = _class_from_markers(fund_win)
        if not fclass and strong:
            fclass = CLASS_IN_SOURCE_NOT_HELD if _FUNDING_POINTER.search(win) else CLASS_NONE
        if fclass and fclass != CLASS_NONE:
            span = win
    ds = _DRUG_SUPPLY.search(text)
    note = ""
    if ds:
        dwin = _sentence_window(text, ds.start(), fwd=180)
        if _INDUSTRY.search(dwin):
            if fclass and fclass not in (CLASS_INDUSTRY, CLASS_IN_SOURCE_NOT_HELD):
                note = "study drug supplied by industry"
            elif not fclass:
                fclass = CLASS_INDUSTRY
                span = dwin
                note = "study drug supplied by industry"
    if fclass and fclass != CLASS_NONE:
        return _funding_object(
            status=STATUS_IN_SOURCE_NOT_HELD if fclass == CLASS_IN_SOURCE_NOT_HELD else STATUS_STATED,
            sponsor_class=fclass,
            sponsors=[] if fclass == CLASS_IN_SOURCE_NOT_HELD else _split_sponsors(span),
            role=_roles(span),
            basis_span=span,
            source_id=source_id,
            source_kind=source_kind,
            scanned=scanned,
            note=note,
            industry_authors_present=bool(_INDUSTRY_AUTHORS.search(text)),
        )
    p = _FUNDING_POINTER.search(text)
    if p:
        span = _sentence_window(text, p.start(), fwd=160)
        return _funding_object(
            status=STATUS_IN_SOURCE_NOT_HELD,
            sponsor_class=CLASS_IN_SOURCE_NOT_HELD,
            basis_span=span,
            source_id=source_id,
            source_kind=source_kind,
            scanned=scanned,
            industry_authors_present=bool(_INDUSTRY_AUTHORS.search(text)),
        )
    return None


def _registry_class(rows: list[dict[str, str]]) -> str | None:
    leads = [r for r in rows if (r.get("lead_or_collaborator") or "").lower() == "lead"]
    lead_classes = {(r.get("agency_class") or "").upper() for r in leads}
    all_classes = {(r.get("agency_class") or "").upper() for r in rows}
    if "INDUSTRY" in lead_classes:
        return CLASS_INDUSTRY
    if "INDUSTRY" in all_classes:
        return CLASS_MIXED
    if rows:
        return CLASS_PUBLIC
    return None


def registry_detect(nct: str, registry: dict[str, list[dict[str, str]]] | None) -> dict[str, Any] | None:
    rows = (registry or {}).get("sponsors") or []
    sponsor_class = _registry_class(rows)
    if not sponsor_class:
        return None
    parts = []
    sponsors = []
    roles = []
    for row in rows:
        name = _clean(row.get("name"))
        if not name:
            continue
        role = _clean(row.get("lead_or_collaborator"))
        agency = _clean(row.get("agency_class"))
        sponsors.append(name)
        if role:
            roles.append(f"registry_{role}")
        parts.append(f"{role or 'sponsor'} {agency}: {name}".strip())
    for row in (registry or {}).get("responsible_parties") or []:
        rp_type = _clean(row.get("responsible_party_type"))
        org = _clean(row.get("organization") or row.get("name") or row.get("old_name_title"))
        if rp_type:
            roles.append(f"responsible_party:{rp_type.lower()}")
        if org:
            parts.append(f"responsible party {rp_type}: {org}".strip())
    basis = "AACT sponsors: " + "; ".join(parts) if parts else ""
    return _funding_object(
        status=STATUS_REGISTRY,
        sponsor_class=sponsor_class,
        sponsors=sorted(dict.fromkeys(sponsors)),
        role=sorted(dict.fromkeys(roles)),
        basis_span=basis,
        source_id=f"registry:{nct.upper()}",
        source_kind="registry",
        scanned="registry",
    )


def _combine_class(left: str, right: str) -> str:
    vals = {left, right}
    vals.discard("")
    vals.discard(CLASS_NONE)
    vals.discard(CLASS_IN_SOURCE_NOT_HELD)
    if vals == {CLASS_INDUSTRY, CLASS_PUBLIC} or CLASS_MIXED in vals:
        return CLASS_MIXED
    if CLASS_INDUSTRY in vals:
        return CLASS_INDUSTRY
    if CLASS_PUBLIC in vals:
        return CLASS_PUBLIC
    return left or right or CLASS_NONE


def _merge_sources(text_hit: dict[str, Any] | None, registry_hit: dict[str, Any] | None) -> dict[str, Any] | None:
    if not text_hit and not registry_hit:
        return None
    primary = text_hit or registry_hit
    sources = [src for src in (text_hit, registry_hit) if src]
    merged_class = primary["sponsor_class"]
    for src in sources[1:]:
        merged_class = _combine_class(merged_class, src.get("sponsor_class") or "")
    out = dict(primary)
    out["sponsor_class"] = merged_class
    out["type"] = _legacy_type(out["status"], merged_class, out.get("scanned") or "")
    out["sources"] = [
        {
            "status": src.get("status"),
            "sponsor_class": src.get("sponsor_class"),
            "sponsors": src.get("sponsors") or [],
            "role": src.get("role") or [],
            "basis_span": src.get("basis_span") or "",
            "source_id": src.get("source_id") or "",
        }
        for src in sources
    ]
    if len({src.get("sponsor_class") for src in sources if src.get("sponsor_class")}) > 1:
        out["source_disagreement"] = True
    if registry_hit:
        out["registry_source"] = out["sources"][-1]
    return out


def _trial_nct(raw_id: str, row: dict[str, Any], rec: dict[str, Any]) -> str:
    if raw_id.upper().startswith("NCT"):
        return raw_id.upper()
    for source in (row, rec):
        nct = source.get("nct") if isinstance(source, dict) else None
        if nct:
            return str(nct).upper()
    for value in (row.get("source"), row.get("label"), rec.get("abstract")):
        m = _NCT_RE.search(str(value or ""))
        if m:
            return m.group(0).upper()
    return ""


def _pooled_trials(review: dict[str, Any]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for outcome in review.get("outcomes", []) or []:
        for trial in outcome.get("trials", []) or []:
            raw = str(trial.get("id", "")).replace("PMID ", "").strip()
            if raw and raw not in seen:
                seen.add(raw)
                out.append(trial)
    return out


def scan_pooled(
    review: dict[str, Any],
    rec_by_id: dict[str, dict[str, Any]],
    fulltext_by_pmid: dict[str, str] | None = None,
    registry_by_nct: dict[str, dict[str, list[dict[str, str]]]] | None = None,
) -> list[dict[str, Any]]:
    """Classify funding for every pooled trial from held text plus registry sponsor rows."""
    fulltext_by_pmid = fulltext_by_pmid or {}
    trials = _pooled_trials(review)
    ncts = []
    recs: dict[str, dict[str, Any]] = {}
    trial_ncts: dict[str, str] = {}
    for trial in trials:
        raw = str(trial.get("id", "")).replace("PMID ", "").strip()
        rec = rec_by_id.get(raw) or {}
        recs[raw] = rec
        nct = _trial_nct(raw, trial, rec)
        trial_ncts[raw] = nct
        if nct:
            ncts.append(nct)
    if registry_by_nct is None:
        registry_by_nct = aact.sponsor_records(ncts)

    out = []
    for trial in trials:
        raw = str(trial.get("id", "")).replace("PMID ", "").strip()
        rec = recs.get(raw) or {}
        is_pmid = raw.isdigit()
        ft = fulltext_by_pmid.get(raw) if is_pmid else ""
        abstract = _clean((rec.get("title", "") + " " + rec.get("abstract", "")).strip())
        scanned = "full text" if ft else "abstract only"
        ft_hit = detect(ft, f"fulltext:PMID {raw}", "full text", scanned) if ft else None
        abs_hit = detect(abstract, f"abstract:PMID {raw}" if is_pmid else f"abstract:{raw}", "abstract", scanned)
        text_hit = ft_hit or abs_hit
        nct = trial_ncts.get(raw) or ""
        reg_hit = registry_detect(nct, registry_by_nct.get(nct)) if nct else None
        hit = _merge_sources(text_hit, reg_hit)
        if hit:
            row = dict(hit)
            row["id"] = trial.get("id")
            row["nct"] = nct
            out.append(row)
        else:
            row = _funding_object(
                status=STATUS_NONE,
                sponsor_class=CLASS_NONE,
                source_id=("fulltext" if ft else "abstract") + (f":PMID {raw}" if is_pmid else f":{raw}"),
                source_kind="full text" if ft else "abstract only",
                scanned=scanned,
                industry_authors_present=bool(_INDUSTRY_AUTHORS.search((ft or "") + " " + abstract)),
            )
            row["id"] = trial.get("id")
            row["nct"] = nct
            out.append(row)
    return out


def funding_known(item: dict[str, Any]) -> bool:
    typ = item.get("type") or ""
    return (
        item.get("sponsor_class") in {CLASS_INDUSTRY, CLASS_PUBLIC, CLASS_MIXED}
        or typ.startswith("industry")
        or typ == "mixed"
        or typ.startswith("public")
        or typ.startswith("non-profit")
        or bool(item.get("note"))
    )


def industry_tied(item: dict[str, Any]) -> bool:
    typ = item.get("type") or ""
    return item.get("sponsor_class") in {CLASS_INDUSTRY, CLASS_MIXED} or typ.startswith("industry") or typ == "mixed" or bool(item.get("note"))


def unknown_but_recovered(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_after = {str(item.get("id")): item for item in after}
    recovered = []
    for old in before or []:
        old_class = old.get("sponsor_class")
        old_type = old.get("type") or ""
        old_unknown = old_class in (None, "", CLASS_NONE, CLASS_IN_SOURCE_NOT_HELD) or old_type.startswith("not stated")
        new = by_after.get(str(old.get("id")))
        if old_unknown and new and funding_known(new):
            recovered.append(new)
    return recovered


def class_distribution(fund: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in fund or []:
        key = item.get("sponsor_class") or item.get("type") or "unknown"
        out[key] = out.get(key, 0) + 1
    return out
