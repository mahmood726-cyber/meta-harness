"""Comparator IDENTITY check (V1.0.1): is the comparator the protocol NAMES the one its PMID / DOI resolve to?

From the CAP-corticosteroids review: the protocol names "Wu et al., Journal of Critical Care 2024" but PMID 38128217
and DOI 10.1016/j.jcrc.2023.154507 resolve to Cheema HA et al. (13 authors, none named Wu). Every comparator number
the page quotes is read from what the PMID resolves to, so a wrong name is a wrong claim about the source.

Inputs, offline: protocols/<slug>.md ("## Comparator" section) and cache/<slug>/comparator_identity.json (the PubMed
and Crossref metadata held by scripts/comparator_identity.py, each with its response sha256). Checks:
  pmid    the protocol's PMID(s) include the configured comparator_pmid
  doi     the protocol's DOI equals the DOI PubMed records for that PMID
  title   the protocol's quoted title equals the resolved title (or is its leading part, e.g. without a subtitle)
  author  the protocol's named author is the resolved FIRST author; one listed but not first is a citation defect
          (COMPARATOR_CITATION_AUTHOR_NOT_FIRST); one not among the resolved authors is an identity mismatch
state: COMPARATOR_IDENTITY_MISMATCH when any check fails outright; MATCH when every named field agrees;
PROTOCOL_DOES_NOT_NAME when the protocol names no author, title or PMID for the comparator (nothing to check);
NOT_HELD when no resolved metadata is held.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

MISMATCH = "COMPARATOR_IDENTITY_MISMATCH"
NOT_FIRST = "COMPARATOR_CITATION_AUTHOR_NOT_FIRST"
_NON_PERSON = re.compile(r"^(?:Frontiers|The|Published|Comparator|WHO|A|An|This|It)\b")


def fold(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def section(md: str) -> str:
    m = re.search(r"^## Comparator[^\n]*\n(.*?)(?=^## |\Z)", md or "", re.M | re.S)
    return m.group(1) if m else ""


def named_author(sec: str):
    head = re.sub(r"\s+", " ", sec.strip())[:300]
    m = re.search(r"(?:^|\bis )([A-Z][A-Za-z'’\-]+(?: (?:van|de|von|der|den|du|da) [A-Z][A-Za-z'’\-]+)?)"
                  r"(?: et al\.?|,| and )", head)
    if m and not _NON_PERSON.match(m.group(1)):
        return m.group(1)
    return None


def _doi(sec: str):
    m = re.search(r"\bDOI:?\s*(10\.\d{4,9}/[^\s;,]+)", sec)
    if not m:
        return None
    d = m.group(1).rstrip(".")
    while d.endswith(")") and d.count(")") > d.count("("):
        d = d[:-1]
    return d


def _surname(pubmed_name: str) -> str:
    parts = str(pubmed_name or "").split(" ")
    # PubMed style 'Cheema HA' / 'van Es N': drop the trailing initials token
    if len(parts) > 1 and re.fullmatch(r"[A-Z]{1,4}", parts[-1]):
        parts = parts[:-1]
    return fold(" ".join(parts))


def governing(root, slug: str, protocol_pmids, served_pmid) -> dict:
    """V1.0.1 (empagliflozin-HFpEF review): ONE governing comparator. The registered protocol governs; the comparator
    the pages serve (topic config -> review -> manifest) must be it, or a replacement recorded in
    registry/comparator_replacements.json (who, when, why). Otherwise the page states UNRECORDED_REPLACEMENT."""
    served = str(served_pmid) if served_pmid is not None else None
    if not protocol_pmids:
        return {"state": "PROTOCOL_DOES_NOT_NAME", "governing_pmid": served, "served_pmid": served}
    if served in protocol_pmids:
        return {"state": "GOVERNING", "governing_pmid": served, "served_pmid": served}
    p = Path(root) / "registry" / "comparator_replacements.json"
    recs = (json.loads(p.read_text(encoding="utf-8")).get("replacements") or {}) if p.exists() else {}
    r = recs.get(slug) or {}
    if str(r.get("from_pmid")) in protocol_pmids and str(r.get("to_pmid")) == served and r.get("why") and r.get("recorded_by"):
        return {"state": "REPLACED_RECORDED", "governing_pmid": served, "protocol_pmid": str(r["from_pmid"]),
                "served_pmid": served, "record": r}
    return {"state": "UNRECORDED_REPLACEMENT", "governing_pmid": protocol_pmids[0], "served_pmid": served,
            "why": ("the protocol names PMID " + ", ".join(protocol_pmids) + f" but the pages serve PMID {served}, and no "
                    "replacement is recorded; the protocol's comparator governs and the served one is not it")}


def check(root, slug: str, comparator_pmid) -> dict:
    root = Path(root)
    held = root / "cache" / slug / "comparator_identity.json"
    if not held.exists():
        return {"state": "NOT_HELD"}
    doc = json.loads(held.read_text(encoding="utf-8"))
    res = list(((doc.get("pubmed") or {}).get("body") or {}).get("result", {}).values())
    pm = res[0] if res else {}
    authors = [a.get("name") for a in pm.get("authors") or [] if a.get("name")]
    surnames = [_surname(a) for a in authors]
    rdoi = next((x["value"] for x in pm.get("articleids") or [] if x.get("idtype") == "doi"), None)
    proto = root / "protocols" / f"{slug}.md"
    sec = section(proto.read_text(encoding="utf-8") if proto.exists() else "")
    pmids = re.findall(r"PMID\s*(\d{6,9})", sec)
    pdoi = _doi(sec)
    ptitle = (re.search(r"[\"“]([^\"”]{20,})[\"”]", sec) or [None, None])[1]
    na = named_author(sec)
    checks, fails, notes = {}, [], []
    if pmids:
        checks["pmid"] = "MATCH" if str(comparator_pmid) in pmids else f"PROTOCOL {pmids} / CONFIGURED {comparator_pmid}"
    if pdoi:
        checks["doi"] = "MATCH" if rdoi and pdoi.lower() == rdoi.lower() else f"PROTOCOL {pdoi} / RESOLVED {rdoi}"
    if ptitle:
        ft, rt = fold(ptitle), fold(pm.get("title"))
        checks["title"] = "MATCH" if ft == rt else ("LEADING_PART_MATCH" if rt.startswith(ft) and len(ft) > 30 else
                                                   f"PROTOCOL '{ptitle.strip()}' / RESOLVED '{pm.get('title')}'")
    if na:
        f = fold(na)
        checks["author"] = ("FIRST_AUTHOR" if surnames and f == surnames[0] else
                            f"{NOT_FIRST}: '{na}' is author {surnames.index(f) + 1} of {len(authors)}" if f in surnames else
                            f"NOT_AMONG_RESOLVED: '{na}' is not one of the {len(authors)} authors (first: {authors[0] if authors else None})")
    for k, v in checks.items():
        if v in ("MATCH", "FIRST_AUTHOR", "LEADING_PART_MATCH"):
            continue
        (notes if v.startswith(NOT_FIRST) else fails).append(f"{k}: {v}")
    state = (MISMATCH if fails else "PROTOCOL_DOES_NOT_NAME" if not checks else "MATCH")
    return {"state": state, "checks": checks, "failures": fails, "citation_defects": notes,
            "governing": governing(root, slug, pmids, comparator_pmid),
            "protocol": {"named_author": na, "title": ptitle and ptitle.strip(), "pmids": pmids, "doi": pdoi},
            "resolved": {"pmid": pm.get("uid"), "first_author": authors[0] if authors else None, "n_authors": len(authors),
                         "title": pm.get("title"), "doi": rdoi, "journal": pm.get("fulljournalname") or pm.get("source"),
                         "pubdate": pm.get("pubdate")},
            "held": {"document_ref": f"cache/{slug}/comparator_identity.json",
                     "pubmed_sha256": (doc.get("pubmed") or {}).get("sha256"),
                     "crossref_sha256": (doc.get("crossref") or {}).get("sha256")}}


def render_block(identity: dict) -> str:
    import html as _h
    gov = (identity or {}).get("governing") or {}
    if not identity or identity.get("state") in (None, "NOT_HELD", "MATCH", "PROTOCOL_DOES_NOT_NAME") \
            and not identity.get("citation_defects") and gov.get("state") in (None, "GOVERNING", "PROTOCOL_DOES_NOT_NAME"):
        return ""
    e = lambda s: _h.escape(str(s), quote=True)  # noqa: E731
    r = identity.get("resolved") or {}
    head = (f"<p><code>{e(identity['state'])}</code>: the comparator the protocol names is not the one its identifiers "
            f"resolve to. PMID {e(r.get('pmid'))} / DOI {e(r.get('doi'))} resolve to <strong>{e(r.get('first_author'))} et "
            f"al.</strong>, &ldquo;{e(r.get('title'))}&rdquo; ({e(r.get('journal'))}, {e(r.get('pubdate'))}). Every comparator "
            "number on this page is read from that resolved paper.</p>" if identity["state"] == MISMATCH else "")
    items = "".join(f"<li>{e(x)}</li>" for x in (identity.get("failures") or []) + (identity.get("citation_defects") or []))
    if gov.get("state") == "UNRECORDED_REPLACEMENT":
        head += (f"<p><code>UNRECORDED_REPLACEMENT</code>: governing comparator PMID {e(gov['governing_pmid'])} (the "
                 f"protocol's); served comparator PMID {e(gov['served_pmid'])}. {e(gov['why'])}.</p>")
    elif gov.get("state") == "REPLACED_RECORDED":
        rr = gov["record"]
        head += (f"<p><code>REPLACED_RECORDED</code>: the protocol's PMID {e(gov['protocol_pmid'])} was replaced by PMID "
                 f"{e(gov['served_pmid'])} ({e(rr.get('recorded_by'))}, {e(rr.get('when'))}): {e(rr.get('why'))}.</p>")
    return ("<div class='comparator-identity'><h5>Comparator identity (protocol name vs resolved PMID/DOI)</h5>" + head
            + f"<ul>{items}</ul><p class='small'>Resolved metadata held in {e(identity['held']['document_ref'])} "
              f"(PubMed sha256 {e(identity['held']['pubmed_sha256'])}).</p></div>")
