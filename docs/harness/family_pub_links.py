"""Recorded registry -> publication links for registry-only trial families (V1.0.1, finerenone review).

cache/<slug>/family_pub_links.json (scripts/family_pub_links.py) holds, per link, the publication's PubMed record and
the binding evidence: a token printed by BOTH the held registry record's title and the publication (ARTS-DN Japan,
NCT01968668 -> Katayama 2017, PMID 28025025). A link whose token is not in both held texts is refused. The linked
publication is added to the build's records as an ordinary PubMed record carrying the registry id, so screening,
the family ledger and the population witness (via the sponsor's registry record) treat it like any other report.
"""
from __future__ import annotations

import json
from pathlib import Path


class LinkRefused(ValueError):
    pass


def links(root, slug) -> list:
    p = Path(root) / "cache" / slug / "family_pub_links.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("links") or []


def merge(root, slug, records: dict) -> dict:
    lk = links(root, slug)
    if not lk:
        return records
    out = dict(records)
    recs = list(out.get("records") or [])
    have = {str(r.get("id")) for r in recs if isinstance(r, dict)}
    by_id = {str(r.get("id")): r for v in records.values() if isinstance(v, list) for r in v if isinstance(r, dict)}
    fam_reg = None
    for x in lk:
        reg = by_id.get(str(x["nct"])) or {}
        # V1.0.1 (sacubitril review): the registry record's acronym field is printed by the registry too ('PARALLEL-HF')
        reg_text = " ".join(str(reg.get(k) or "") for k in ("title", "acronym"))
        sref = (x.get("registry_quote") or {}).get("source_reference")
        if not reg and sref:
            # V1.0.1 (GLP-1 review, PIONEER 8): a registry-only FAMILY whose record lives in the held family registry
            # (the AACT studies row, cited by its source_reference and row sha256), not in records.json -- bound on that
            # row's acronym/titles, and the held row must be the cited one
            if fam_reg is None:
                from .trial_family import load_registry
                fam_reg = load_registry(root, slug)
            st = ((fam_reg.get(str(x["nct"])) or {}).get("raw", {}).get("studies") or [{}])[0]
            if (st.get("source_reference") or {}).get("row_sha256") != sref.get("row_sha256"):
                raise LinkRefused(f"{slug}: link {x['nct']} -> {x['pmid']}: the held registry row is not the cited one")
            reg_text = " ".join(str(st.get(k) or "") for k in ("acronym", "brief_title", "official_title"))
        rec = x["record"]
        tok = str(x.get("binding_token") or "").strip()
        # REV-R1 (codex review, verified): an empty token is 'in' every text, and a record other than the linked PMID
        # would be appended under that PMID's name
        if len(tok) < 3:
            raise LinkRefused(f"{slug}: link {x['nct']} -> {x['pmid']}: binding token is empty or too short to bind")
        if str(rec.get("id")) != str(x["pmid"]):
            raise LinkRefused(f"{slug}: link {x['nct']} -> {x['pmid']}: the held record is PMID {rec.get('id')}, not the linked one")
        paper = " ".join([str(rec.get("title") or ""), str(rec.get("abstract") or ""), *(rec.get("collective_authors") or [])])
        if tok not in reg_text or tok not in paper:
            raise LinkRefused(f"{slug}: link {x['nct']} -> {x['pmid']}: binding token not printed by both held texts")
        link = {"nct": x["nct"], "binding_token": tok, "reported_by": x.get("reported_by")}
        if str(rec["id"]) not in have:
            recs.append(dict(rec, family_link=link))
            have.add(str(rec["id"]))                        # a repeated link never appends a duplicate record
        else:
            # the publication is already held: it still carries the recorded link, so the family binds it
            recs = [dict(r, family_link=link, nct=r.get("nct") or x["nct"])
                    if isinstance(r, dict) and str(r.get("id")) == str(rec["id"]) else r for r in recs]
    out["records"] = recs
    out["family_pub_links"] = [{"nct": x["nct"], "pmid": x["pmid"], "binding_token": x["binding_token"]} for x in lk]
    return out
