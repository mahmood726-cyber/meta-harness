"""Every trial a held comparator NAMES enters screening (V1.0.1, PCSK9 review).

PACMAN-AMI (NCT03067844; Raber, JAMA 2022, PMID 35368058) is a row of Wang 2022's included-trial table, a comparator
we hold, and was absent from our screened inventory: nothing had ever put it in front of screening. A comparator's
enumerated rows are therefore candidates. A row that is already among our records (by PMID, NCT or DOI) is left
alone; any other row with an identifier gets its PubMed report(s) -- the PMID it cites, or every PubMed record indexed
with the NCT it prints (a trial's substudies are reports of the SAME trial, and the family ledger groups them) -- and
those records enter screening like any other, found by COMPARATOR_NAMED. Screening decides; this module never includes.

A candidate never displaces a record we hold: a fetched record whose NCT or PMID is already held is not added
(the reason reference seeding was disabled -- a secondary report sharing an NCT overwrote the primary in dedup --
cannot arise). Rows with no identifier are listed by name as not screened; the count is reach, not coverage.

cache/<slug>/comparator_named.json + cache/<slug>/comparator_named_pubmed.xml (scripts/comparator_named.py). The
records are re-derived from the held XML bytes at build time; its sha256 must match.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


class NamedRefused(ValueError):
    pass


def _is_nct(s) -> bool:
    s = str(s or "")
    return len(s) == 11 and s[:3] == "NCT" and s[3:].isdigit()


def panel_rows(root, slug) -> list:
    """(comparator id, row family_id, [identifiers]) for every enumerated row of every held comparator panel."""
    p = Path(root) / "cache" / slug / "comparators.json"
    if not p.exists():
        return []
    # V1.0.1 (SGLT2-CKD review): a CONSORTIUM analysis pools its own member trials; its list is membership, not a search
    # result, and is never used as a discovery source
    ap = Path(root) / "cache" / slug / "comparator_analysis.json"
    if ap.exists() and json.loads(ap.read_text(encoding="utf-8")).get("comparator_type") == "CONSORTIUM_ANALYSIS":
        return []
    out = []
    for c in json.loads(p.read_text(encoding="utf-8")):
        for m in c.get("trial_set") or []:
            out.append((str(c.get("id")), m["family_id"], [str(a["id"]) for a in m.get("aliases") or []]))
    return out


def held_keys(records: dict, families: list = ()) -> set:
    keys = set()
    for v in records.values():
        if isinstance(v, list):
            for r in v:
                if isinstance(r, dict):
                    keys.add(str(r.get("id")))
                    if r.get("nct"):
                        keys.add(str(r["nct"]))
                    if r.get("doi"):
                        keys.add(str(r["doi"]).lower())
    for f in families or []:
        keys.add(str(f.get("family_id")))
        al = f.get("aliases") or {}
        keys.update(str(x) for k in ("report_ids", "registry_ids") for x in al.get(k) or [])
        keys.update(str(x).lower() for x in al.get("dois") or [])
    return keys


def _norm_id(i) -> str:
    return str(i).lower() if str(i).startswith("10.") else str(i)


def databank_ncts(xml: str) -> dict:
    """PMID -> every ClinicalTrials.gov accession its PubMed DataBank lists (a joint report, e.g. ODYSSEY FH I and FH
    II, lists both; the record's own 'nct' is only the one fetch._select_nct picked)."""
    import xml.etree.ElementTree as ET
    out = {}
    for art in ET.fromstring(xml).findall(".//PubmedArticle"):
        pmid = "".join(art.find(".//PMID").itertext()).strip()
        out[pmid] = [("".join(a.itertext())).strip() for db in art.findall(".//DataBank")
                     if "".join(db.find("DataBankName").itertext()).lower().startswith("clinicaltrials")
                     for a in db.findall(".//AccessionNumber")]
    return out


def load(root, slug):
    p = Path(root) / "cache" / slug / "comparator_named.json"
    if not p.exists():
        return None, []
    doc = json.loads(p.read_text(encoding="utf-8"))
    parsed = []
    if doc.get("pubmed_xml"):
        raw = (Path(root) / doc["pubmed_xml"]["document_ref"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != doc["pubmed_xml"]["sha256"]:
            raise NamedRefused(f"{slug}: held PubMed XML changed since it was recorded")
        from .fetch import parse_pubmed_xml
        dbl = databank_ncts(raw.decode("utf-8"))
        parsed = [dict(r, _databank=dbl.get(str(r["id"])) or []) for r in parse_pubmed_xml(raw.decode("utf-8"))]
    return doc, parsed


def merge(root, slug, records: dict) -> dict:
    doc, parsed = load(root, slug)
    if not doc:
        return records
    by_pmid = {str(r["id"]): r for r in parsed}
    live = {(cid, fid): ids for cid, fid, ids in panel_rows(root, slug)}
    named_ncts = {i for ids in live.values() for i in ids if _is_nct(i)}
    have = held_keys(records)
    _fk = []

    def fam_keys():
        # the certified family map holds registry-only families (e.g. a trial held by its AACT row, not a record)
        if not _fk:
            fp = Path(root) / "cache" / slug / "families.json"
            fams = json.loads(fp.read_text(encoding="utf-8")).get("families") if fp.exists() else []
            _fk.append(held_keys({}, fams))
        return _fk[0]
    recs = list(records.get("records") or [])
    added, rows = [], []
    for row in doc["rows"]:
        key = (row["comparator"], row["row"])
        if key not in live or not set(row["identifiers"]) <= set(live[key]):
            raise NamedRefused(f"{slug}: row {row['row']} is not (or no longer) an enumerated comparator row with those identifiers")
        state = row["state"]
        if state == "CANDIDATE":
            got, shared = [], []
            for pmid in row["pmids"]:
                r = by_pmid.get(str(pmid))
                if r is None:
                    raise NamedRefused(f"{slug}: PMID {pmid} of row {row['row']} is not in the held PubMed XML")
                ncts = [i for i in row["identifiers"] if _is_nct(i)]
                if ncts and not set(ncts) & set(r["_databank"]):
                    raise NamedRefused(f"{slug}: PMID {pmid} is not registered as the row's trial {ncts} ({r['_databank']})")
                if ncts and r.get("nct") not in named_ncts:
                    # a pooled analysis listing this trial among others is attributed to a trial NO row names: it
                    # would open a family the comparator never named
                    raise NamedRefused(f"{slug}: PMID {pmid} is attributed to {r.get('nct')}, which no comparator row names")
                dois = {str(i).lower() for i in row["identifiers"] if str(i).startswith("10.")}
                # REV-R2: a DOI-only row (resolved by the acquisition script's [aid] search) binds the record whose own
                # DOI is the row's; before, every such candidate was refused here
                if not ncts and str(pmid) not in row["identifiers"] and str(r.get("doi") or "").lower() not in dois:
                    raise NamedRefused(f"{slug}: PMID {pmid} is neither the row's cited report, nor its DOI, nor indexed with its NCT")
                if str(pmid) in added:
                    shared.append(str(pmid))                   # a joint report already entered for another row
                    continue
                if (str(pmid) in have or (r.get("nct") and r["nct"] in have)
                        or (r.get("doi") and str(r["doi"]).lower() in have)):    # REV-R2: a held DOI is a held record
                    continue                                   # never displaces a held record or a held trial
                rec = {k: v for k, v in r.items() if k != "_databank"}
                recs.append(dict(rec, found_by=["COMPARATOR_NAMED"],
                                 comparator_named={"comparator": row["comparator"], "row": row["row"]}))
                have.add(str(pmid))
                got.append(str(pmid))
            state = "ENTERED_SCREENING" if got else "JOINT_REPORT_ENTERED" if shared else "ALREADY_HELD"
            added += got
            rows.append(dict(row, state=state, entered=got or shared))
        elif state == "ALREADY_HELD":
            # REV-R2: recorded at acquisition time; if nothing of ours carries the row any longer it must be re-acquired,
            # never reported as held
            if not any(_norm_id(i) in have or _norm_id(i) in fam_keys() for i in row["identifiers"]):
                raise NamedRefused(f"{slug}: row {row['row']} was recorded ALREADY_HELD but none of {row['identifiers']} "
                                   "is held now -- re-run scripts/comparator_named.py")
            rows.append(dict(row))
        else:
            rows.append(dict(row))
    out = dict(records)
    out["records"] = recs
    out["comparator_named"] = {"rows": rows, "entered": added}
    return out


def summary(named: dict) -> dict:
    rows = (named or {}).get("rows") or []
    by = {}
    for r in rows:
        by.setdefault(r["state"], []).append(r["row"])
    return {"named": len(rows), "by_state": {k: len(v) for k, v in sorted(by.items())},
            "not_screened": {k: v for k, v in by.items() if k in ("NO_IDENTIFIER", "NOT_IN_PUBMED")},
            "entered_records": list((named or {}).get("entered") or [])}


def render(named: dict) -> str:
    import html
    if not named or not named.get("rows"):
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    s = summary(named)
    items = "".join(f"<li><strong>{e(r['row'])}</strong>: <code>{e(r['state'])}</code>"
                    + (f" &mdash; PMID {e(', '.join(r['entered']))} screened" if r.get("entered") else "") + "</li>"
                    for r in named["rows"] if r["state"] != "ALREADY_HELD")
    return (f"<div class='comparator-named'><h5>Trials named by the held comparator</h5><p>{e(s['named'])} enumerated "
            f"comparator rows; " + "; ".join(f"{e(v)} {e(k)}" for k, v in s["by_state"].items())
            + ". A row we did not hold enters screening (found by <code>COMPARATOR_NAMED</code>); screening decides, "
            "and no candidate replaces a record we hold. Rows without an identifier are not screened.</p>"
            + (f"<ul>{items}</ul>" if items else "") + "</div>")
