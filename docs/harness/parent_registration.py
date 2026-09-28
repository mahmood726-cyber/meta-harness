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


def by_pmid(root, slug) -> dict:
    """{pmid: {nct, acronym}} for the recovery panel (a missed report whose parent is registered is not unregistered)."""
    return {str(x["pmid"]): {"nct": x["nct"], "acronym": x["acronym"]} for x in links(root, slug)}
