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
    for x in lk:
        reg = by_id.get(str(x["nct"])) or {}
        rec = x["record"]
        paper = " ".join([str(rec.get("title") or ""), str(rec.get("abstract") or ""), *(rec.get("collective_authors") or [])])
        if x["binding_token"] not in str(reg.get("title") or "") or x["binding_token"] not in paper:
            raise LinkRefused(f"{slug}: link {x['nct']} -> {x['pmid']}: binding token not printed by both held texts")
        if str(rec["id"]) not in have:
            recs.append(dict(rec, family_link={"nct": x["nct"], "binding_token": x["binding_token"],
                                               "reported_by": x.get("reported_by")}))
    out["records"] = recs
    out["family_pub_links"] = [{"nct": x["nct"], "pmid": x["pmid"], "binding_token": x["binding_token"]} for x in lk]
    return out
