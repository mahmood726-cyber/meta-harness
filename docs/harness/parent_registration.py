"""A secondary report's PARENT registration, recorded with its evidence (V1.0.1, statins-older-adults review).

The recovery panel called JUPITER's older-adults report (Glynn 2010, PMID 20404379) "unregistered / pre-registration-
era". JUPITER is NCT00239681. The report's PubMed record carries no DataBank entry and AACT links no own publication
to it, so every automatic route saw a BLANK field -- and a blank field is not "unregistered".

cache/<slug>/parent_registrations.json records, per link, a sentence of the report naming its parent trial and a
field of the held registration naming the same trial. A link is refused unless:
  - the report's quote is located in the report's own held title/abstract (records.json) and prints the acronym as a
    whole token;
  - the registry quote is located in the held registration (evidence/held/registry/<NCT>.json, or the topic's
    records.json) and prints the same acronym;
  - the held registration is that NCT.
The linked report then carries the registration (rec['nct']) with the evidence as its identity_source, so the family
ledger places it in its parent trial's family; it never changes the report's own role or numbers.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


class LinkRefused(ValueError):
    pass


def _norm(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def links(root, slug) -> list:
    p = Path(root) / "cache" / slug / "parent_registrations.json"
    return json.loads(p.read_text(encoding="utf-8")).get("links") or [] if p.exists() else []


def _token(acr: str, text: str) -> bool:
    return bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(acr) + r"(?![A-Za-z0-9])", text))


def validate(root, slug, x: dict, by_id: dict) -> None:
    acr, nct, pmid = str(x.get("acronym") or ""), str(x.get("nct") or ""), str(x.get("pmid") or "")
    if len(acr) < 3 or not re.fullmatch(r"NCT\d{8}", nct) or not pmid.isdigit():
        raise LinkRefused(f"{slug}: parent link {pmid} -> {nct}: needs a PMID, an NCT and an acronym of 3+ characters")
    rec = by_id.get(pmid)
    if not rec:
        raise LinkRefused(f"{slug}: parent link {pmid} -> {nct}: the report is not a held record")
    held = _norm(" ".join(str(rec.get(k) or "") for k in ("title", "abstract")))
    pq = _norm(x.get("paper_quote"))
    if len(pq) < 20 or pq not in held or not _token(acr, pq):
        raise LinkRefused(f"{slug}: parent link {pmid} -> {nct}: the report's quote is not located or does not print {acr}")
    rg = x.get("registry_quote") or {}
    doc = Path(root) / str(rg.get("document_ref") or "")
    if not rg.get("document_ref") or not doc.is_file():
        raise LinkRefused(f"{slug}: parent link {pmid} -> {nct}: the registration is not held")
    text = doc.read_text(encoding="utf-8")
    rq = str(rg.get("quote") or "")
    if len(rq) < 10 or rq not in text or not _token(acr, rq) or nct not in text:
        raise LinkRefused(f"{slug}: parent link {pmid} -> {nct}: the registration's quote is not located, "
                          f"does not print {acr}, or the held document is not {nct}")


def merge(root, slug, records: dict) -> dict:
    lk = links(root, slug)
    if not lk:
        return records
    by_id = {str(r.get("id")): r for v in records.values() if isinstance(v, list) for r in v if isinstance(r, dict)}
    parent = {}
    for x in lk:
        validate(root, slug, x, by_id)
        parent[str(x["pmid"])] = x
    out = dict(records)
    recs = []
    for r in out.get("records") or []:
        x = parent.get(str(r.get("id"))) if isinstance(r, dict) else None
        if x and not str(r.get("nct") or "").upper().startswith("NCT"):
            r = dict(r, nct=x["nct"], identity_source={
                "source": "recorded parent registration (cache/<slug>/parent_registrations.json)",
                "acronym": x["acronym"], "nct_id": x["nct"], "paper_quote": x["paper_quote"],
                "registry_quote": x["registry_quote"], "reported_by": x.get("reported_by")})
        recs.append(r)
    out["records"] = recs
    return out


# ------------------------------------------------------------------------------------------------------ the proposer
# A report that describes ITSELF as an analysis of a named trial: "Secondary analysis of JUPITER (Justification ...)",
# "post hoc analysis of the SELECT trial", "Secondary analysis of the Antihypertensive ... Trial (ALLHAT-LLT)". The
# phrase is case-insensitive; the trial NAME must be an upper-case token (an acronym), optionally after its spelled-out
# name and optionally in brackets. A generic abbreviation ("RCT", "ACE") never links: the name must resolve to exactly
# ONE held registration that carries it as its own acronym.
SELF_ANALYSIS = re.compile(
    r"\b(?i:secondary|post[- ]?hoc|pre-?specified|exploratory|ancillary|subgroup|sub-?study)\s+"
    r"(?i:analys[ie]s|stud(?:y|ies)|report)\s+(?i:of|from|in)\s+(?i:data\s+from\s+)?(?i:the\s+)?"
    # the name either follows directly ('analysis of JUPITER') or is BRACKETED after a capitalised expansion ('... Heart
    # Attack Trial-Lipid-Lowering Trial (ALLHAT-LLT)'); 'analysis of subjects with AAD' names no trial
    r"(?:(?P<acr>[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*)(?![A-Za-z0-9])"
    r"|[A-Z][A-Za-z']*(?:[-\s][A-Za-z][A-Za-z']*){0,24}?\s*\((?P<acr2>[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*)\))")
_BRIEF_ACRONYM = re.compile(r"^(?P<acr>[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*)\s+-\s+")
_HELD_REGISTRY = "evidence/held/registry"


def held_registrations(root, slug) -> dict:
    """{ACRONYM: {nct: (document_ref, quote)}} from every held registration this build can read: the topic's registry
    records (their acronym field), its family registry (AACT studies.acronym) and the held CT.gov records
    (identificationModule.acronym, or a brief title that STARTS with the acronym: 'JUPITER - Crestor 20mg ...')."""
    root = Path(root)
    out: dict = {}

    def add(acr, nct, ref, quote):
        if acr and nct and quote:
            out.setdefault(str(acr).strip().upper(), {}).setdefault(str(nct).upper(), (ref, str(quote)))

    rp = root / "cache" / slug / "records.json"
    if rp.exists():
        for r in json.loads(rp.read_text(encoding="utf-8")).get("ctgov") or []:
            add(r.get("acronym"), r.get("id"), f"cache/{slug}/records.json", r.get("acronym"))
    for p in sorted((root / _HELD_REGISTRY).glob("NCT*.json")):
        idm = (json.loads(p.read_text(encoding="utf-8")).get("protocolSection") or {}).get("identificationModule") or {}
        ref = f"{_HELD_REGISTRY}/{p.name}"
        add(idm.get("acronym"), idm.get("nctId"), ref, idm.get("acronym"))
        m = _BRIEF_ACRONYM.match(idm.get("briefTitle") or "")
        if m:
            add(m.group("acr"), idm.get("nctId"), ref, idm.get("briefTitle"))
    return out


def propose(root, slug, records: dict) -> list:
    """One typed row per held report that names itself an analysis of a named trial and carries no registration:
    LINKED (a link row that validate() accepts), WITHHELD_SAME_REGISTRATION (another held report already carries that
    NCT: the build's same-registration de-duplication would fold this report into it with no screening row -- the
    ALLHAT-LLT case -- so no link until that collapse is disclosed), AMBIGUOUS (several registrations carry the name)
    or UNRESOLVED (no held registration carries it)."""
    regs = None
    held_ncts = {}
    for r in records.get("records") or []:
        n = str(r.get("nct") or "").upper()
        if n.startswith("NCT"):
            held_ncts.setdefault(n, []).append(str(r.get("id")))
    rows = []
    for r in records.get("records") or []:
        if str(r.get("nct") or "").upper().startswith("NCT"):
            continue
        text = _norm(" ".join(str(r.get(k) or "") for k in ("title", "abstract")))
        m = SELF_ANALYSIS.search(text)
        if not m:
            continue
        if regs is None:
            regs = held_registrations(root, slug)
        acr = m.group("acr") or m.group("acr2")
        cands = regs.get(acr.upper()) or regs.get(acr.split("-")[0].upper()) or {}
        row = {"pmid": str(r.get("id")), "acronym": acr, "phrase": m.group(0)}
        # the sentence that carries the phrase, as the paper quote
        s0 = text.rfind(". ", 0, m.start()) + 2 if text.rfind(". ", 0, m.start()) >= 0 else 0
        s1 = text.find(". ", m.end())
        row["paper_quote"] = text[s0:(s1 + 1) if s1 >= 0 else len(text)].strip()
        if not cands:
            rows.append(dict(row, state="UNRESOLVED"))
        elif len(cands) > 1:
            rows.append(dict(row, state="AMBIGUOUS", candidates=sorted(cands)))
        else:
            nct, (ref, quote) = next(iter(cands.items()))
            row.update(nct=nct, acronym=acr if _token(acr, quote) else acr.split("-")[0],
                       registry_quote={"document_ref": ref, "field": "acronym / brief title", "quote": quote})
            others = [x for x in held_ncts.get(nct, []) if x != row["pmid"]]
            rows.append(dict(row, state="WITHHELD_SAME_REGISTRATION", held_reports_of_registration=others) if others
                        else dict(row, state="LINKED"))
    return rows


def by_pmid(root, slug) -> dict:
    """{pmid: {nct, acronym}} for the recovery panel (a missed report whose parent is registered is not unregistered)."""
    return {str(x["pmid"]): {"nct": x["nct"], "acronym": x["acronym"]} for x in links(root, slug)}
