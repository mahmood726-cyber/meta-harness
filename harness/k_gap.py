"""K-GAP measurement: the comparator's INCLUDED-STUDIES set vs our pool, trial by trial.

A comparator's headline k is a number; its included-studies table is a SET. Parity on the number
hides which trials are missing and why. This module reads the comparator's own JATS (PMC OA) where
table cells cite the reference list by `<xref ref-type="bibr" rid=...>`, and the reference list
carries `<pub-id pub-id-type="pmid">` -- so the comparator's trial set is extracted by PARSING, with
no model and no prose regex over trial names. Every row keeps the table label, the verbatim cell text
and the rid it cited, so each membership claim has a span.

Fetch (network, once, cached with sha256 under cache/comparators/<pmid>/) is separated from the
parse/classify steps, which are pure functions of cached bytes.

Nothing here admits a trial or changes a pool. The output is a MEASUREMENT: which comparator trials we
lack, and which open source could supply an admissible, typed result for each.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP_DIR = os.path.join(ROOT, "cache", "comparators")

_WS = re.compile(r"\s+")
NCT_RE = re.compile(r"\bNCT\d{8}\b")

# A table is an included-studies table when its caption says so. Deliberately narrow: an outcome table
# ("Subgroup analysis of ...") also cites trials, but its rows are analyses, not the included set.
INCLUDED_CAPTION = re.compile(
    r"characteristic|included (?:stud|trial|rct)|baseline|summary of (?:the )?(?:included )?(?:stud|trial)"
    r"|(?:stud|trial)s? included|description of (?:the )?(?:included )?(?:stud|trial)|study design|overview of|summary of (?:the )?(?:cvot|outcome trial|rct|randomi)",
    re.I)


def _flat(s: str | None) -> str:
    return _WS.sub(" ", s or "").strip()


def _text(el) -> str:
    return _flat("".join(el.itertext())) if el is not None else ""


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ----------------------------------------------------------------------------------------------- fetch

def _cache_write(pmid: str, name: str, body: bytes) -> dict:
    d = os.path.join(COMP_DIR, pmid)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "wb") as fh:
        fh.write(body)
    return {"file": os.path.relpath(p, ROOT).replace(os.sep, "/"), "bytes": len(body), "sha256": sha256(body)}


def fetch_comparator_jats(pmid: str, date: str) -> dict:
    """idconv PMID->PMCID, then Europe PMC fullTextXML, falling back to NCBI efetch db=pmc.

    Returns a manifest dict; state is JATS_FULL (has <body> or table-wrap and ref-list), JATS_FRONT_ONLY
    (publisher withholds the body), NO_PMCID, or FETCH_FAILED. Never raises on a missing source."""
    from harness import http
    man: dict[str, Any] = {"pmid": pmid, "date": date, "records": []}
    name = f"{date}_kgap_jats.xml"
    existing = os.path.join(COMP_DIR, pmid, name)
    if os.path.exists(existing):
        body = open(existing, "rb").read()
        man.update(_classify_jats(body))
        man["records"].append({"state": "CACHED", **_rel(existing, body)})
        return man
    try:
        st, b = http.get_raw("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/",
                             {"ids": pmid, "format": "json", "tool": "meta-harness", "email": "meta-harness@example.org"})
        rec = _cache_write(pmid, f"{date}_kgap_idconv.json", b)
        man["records"].append({"url": "idconv", "http_status": st, **rec})
        recs = json.loads(b.decode("utf-8")).get("records") or [{}]
        pmcid = recs[0].get("pmcid") or ""
    except Exception as exc:  # noqa: BLE001
        man.update({"state": "FETCH_FAILED", "error": f"idconv: {exc}"[:300]})
        return man
    man["pmcid"] = pmcid
    if not pmcid:
        man["state"] = "NO_PMCID"
        return man
    for url, params in (
        (f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", None),
        ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", {"db": "pmc", "id": pmcid, "retmode": "xml"}),
    ):
        try:
            st, b = http.get_raw(url, params, tries=2)
        except Exception as exc:  # noqa: BLE001
            man["records"].append({"url": url, "error": str(exc)[:200]})
            continue
        cls = _classify_jats(b)
        if cls["state"] == "JATS_FULL":
            rec = _cache_write(pmid, name, b)
            man["records"].append({"url": url, "http_status": st, **rec})
            man.update(cls)
            return man
        man["records"].append({"url": url, "http_status": st, "state": cls["state"], "bytes": len(b)})
    man["state"] = "JATS_FRONT_ONLY"
    return man


def _rel(p, body):
    return {"file": os.path.relpath(p, ROOT).replace(os.sep, "/"), "bytes": len(body), "sha256": sha256(body)}


def _classify_jats(body: bytes) -> dict:
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return {"state": "NOT_XML"}
    has_refs = root.find(".//ref-list") is not None
    has_tab = root.find(".//table-wrap") is not None
    has_body = root.find(".//body") is not None
    return {"state": "JATS_FULL" if (has_refs and (has_tab or has_body)) else "JATS_FRONT_ONLY",
            "has_tables": has_tab, "has_refs": has_refs}


# ----------------------------------------------------------------------------------------------- parse

def parse_refs(root) -> dict[str, dict]:
    out = {}
    for ref in root.iter("ref"):
        rid = ref.get("id")
        if not rid:
            continue
        ids = {}
        for pid in ref.iter("pub-id"):
            t = (pid.get("pub-id-type") or "").lower()
            if t in ("pmid", "doi", "pmcid") and pid.text:
                ids[t] = pid.text.strip()
        txt = _text(ref)
        if "doi" not in ids:
            m = re.search(r"\b(10\.\d{4,9}/[^\s\"<>]+[^\s\"<>.,;])", txt)
            if m:
                ids["doi"] = m.group(1)
        title = ""
        at = ref.find(".//article-title")
        if at is not None:
            title = _text(at)
        year = ""
        y = ref.find(".//year")
        if y is not None and y.text:
            year = y.text.strip()
        surname = ""
        sn = ref.find(".//surname")
        if sn is not None and sn.text:
            surname = sn.text.strip()
        out[rid] = {"rid": rid, **ids, "title": title, "year": year, "first_author": surname,
                    "text": txt[:400], "ncts": sorted(set(NCT_RE.findall(txt)))}
    return out


def _cell_rids(cell) -> list[str]:
    rids = []
    for x in cell.iter("xref"):
        if (x.get("ref-type") or "") == "bibr":
            for r in (x.get("rid") or "").split():
                rids.append(r)
    return rids


def parse_tables(root) -> list[dict]:
    tabs = []
    for tw in root.iter("table-wrap"):
        label = _text(tw.find("label"))
        caption = _text(tw.find("caption"))
        header = []
        rows = []
        for tr in tw.iter("tr"):
            cells = [c for c in tr if c.tag in ("td", "th")]
            if not cells:
                continue
            texts = [_text(c) for c in cells]
            if all(c.tag == "th" for c in cells) and not rows:
                # keep each header cell's citations: a TRANSPOSED table (trials as columns, e.g. the
                # tranexamic comparator's "WOMAN | WOMAN-2 | TRAAP ...") cites its trials only here.
                header.append([{"text": t, "rids": _cell_rids(c)} for t, c in zip(texts, cells)])
                continue
            rids = []
            for c in cells:
                rids.extend(_cell_rids(c))
            rows.append({"cells": texts, "rids": rids, "row_text": " | ".join(texts)})
        tabs.append({"label": label, "caption": caption, "header": header, "rows": rows,
                     "is_included_table": bool(INCLUDED_CAPTION.search(caption or "") or INCLUDED_CAPTION.search(label))})
    return tabs


def parse_jats(body: bytes) -> dict:
    root = ET.fromstring(body)
    title = _text(root.find(".//article-meta//article-title"))
    return {"title": title, "refs": parse_refs(root), "tables": parse_tables(root)}


# ------------------------------------------------------------------------------ included-set extraction

# A trial label is a row's first cell. Labels that are table furniture (a sub-header, a units row, a
# "Year" continuation row) are not trials; they carry neither a citation, an NCT, nor a name token.
_FURNITURE = re.compile(r"^(?:study|trial|author|year|\d{4}|n|total|overall|reference|characteristics?|"
                        r"participants?|treatment|control|intervention|placebo|mean|median|[-–— ]*)$", re.I)
_ACRO = re.compile(r"\b([A-Z][A-Z0-9]{2,}(?:[- ][A-Z0-9]{1,}){0,3})\b")
_AUTHOR_YEAR = re.compile(r"^([A-Z][A-Za-z'À-ſ-]+)(?:\s+et\s+al\.?)?,?\s*\(?((?:19|20)\d\d)\)?")
_NOT_ACRO = {"RCT", "RCTS", "USA", "UK", "NA", "NR", "HR", "RR", "OR", "CI", "BMI", "LDL", "HDL", "CKD", "HF",
             "HFREF", "HFPEF", "LVEF", "NYHA", "ACS", "MI", "CAD", "PCI", "CABG", "DM", "T2DM", "AF", "VTE",
             "DVT", "PE", "ITT", "MACE", "COVID", "SARS", "ICU", "ARDS", "CAP", "PPH", "MADRS", "TRD",
             "EGFR", "UACR", "SBP", "DBP", "BID", "QD", "IV", "PO", "SC", "EPA", "DHA", "IU", "TID", "NCT",
             "DOAC", "DOACS", "VKA", "NOAC", "SGLT2", "SGLT2I", "GLP", "GLP1", "RA", "DPP4", "PCSK9", "FCM",
             "IPD", "HFPEF", "LCZ696", "ARNI", "ACEI", "ARB", "MRA", "MRAS", "NR", "NS", "YES", "NO", "ALL"}


def _label_tokens(label: str) -> dict:
    lab = _flat(label)
    acr = [a for a in _ACRO.findall(lab) if a.replace("-", "").replace(" ", "").upper() not in _NOT_ACRO
           and not NCT_RE.match(a)]
    m = _AUTHOR_YEAR.match(lab)
    return {"acronyms": acr[:3], "author": m.group(1) if m else "", "year": m.group(2) if m else "",
            "ncts": sorted(set(NCT_RE.findall(lab)))}


def _units_from_table(t: dict) -> list[dict]:
    """A table's trial units: its ROWS normally; its header COLUMNS when the header cites trials
    (transposed layout). A row with no citation still counts when its first cell carries an NCT, an
    acronym or an Author-Year label -- that is a trial named without a reference link."""
    units = []
    hdr = t["header"][0] if t["header"] else []
    hdr_cited = [h for h in hdr[1:] if h["rids"]]
    if len(hdr_cited) >= 2 or (hdr and not any(r["rids"] for r in t["rows"]) and len(hdr) >= 3
                               and all(_label_tokens(h["text"])["acronyms"] for h in hdr[1:] if h["text"])):
        for i, h in enumerate(hdr[1:], start=1):
            if not h["text"] and not h["rids"]:
                continue
            col = " | ".join(r["cells"][i] for r in t["rows"] if len(r["cells"]) > i)
            units.append({"layout": "column", "label": h["text"], "rids": h["rids"], "context": col[:600]})
        return units
    for r in t["rows"]:
        first = r["cells"][0] if r["cells"] else ""
        toks = _label_tokens(first)
        if not r["rids"] and not toks["ncts"] and not toks["acronyms"] and not toks["author"]:
            continue
        if _FURNITURE.match(_flat(first)) and not r["rids"]:
            continue
        units.append({"layout": "row", "label": first, "rids": r["rids"], "context": r["row_text"][:600]})
    return units


def included_trials(parsed: dict, agent_terms: list[str]) -> dict:
    """Units (rows, or columns of a transposed table) of the comparator's included-studies table(s).

    Each unit keeps the verbatim label, the table it came from, the reference-list entries it cites
    (pmid/doi from the JATS ref-list), NCTs written in it, and acronym / Author-Year tokens for the
    identity resolver. agent_terms: the topic's agent names. A unit is DRUG_MATCH when its text names
    one; when NO unit names any topic agent the table is single-agent (the agent is in the paper's title,
    not a column) and units are AGENT_IMPLICIT -- recorded as such, never silently promoted.
    """
    refs = parsed["refs"]
    agent_re = re.compile("|".join(re.escape(a) for a in agent_terms), re.I) if agent_terms else None
    units, used, seen = [], [], set()
    for t in parsed["tables"]:
        if not t["is_included_table"]:
            continue
        tu = _units_from_table(t)
        if not tu:
            continue
        used.append(t["label"] or t["caption"][:60])
        for u in tu:
            toks = _label_tokens(u["label"])
            key = tuple(sorted(set(u["rids"]))) or ("L", _flat(u["label"]).upper())
            if key in seen:
                continue
            seen.add(key)
            cited = [refs[x] for x in dict.fromkeys(u["rids"]) if x in refs]
            text = u["label"] + " | " + u["context"]
            units.append({
                "table": t["label"] or t["caption"][:40],
                "layout": u["layout"],
                "label": _flat(u["label"])[:160],
                "context": _flat(u["context"])[:600],
                "rids": list(dict.fromkeys(u["rids"])),
                "cited": [{k: c.get(k) for k in ("rid", "pmid", "doi", "pmcid", "title", "year", "first_author", "ncts")}
                          for c in cited],
                "ncts": sorted(set(NCT_RE.findall(text)) | {n for c in cited for n in c.get("ncts", [])}),
                "acronyms": toks["acronyms"], "author": toks["author"], "year": toks["year"],
                "agent_hit": bool(agent_re and agent_re.search(text)),
            })
    any_hit = any(u["agent_hit"] for u in units)
    for u in units:
        u["drug_match"] = "DRUG_MATCH" if u["agent_hit"] else ("OTHER_AGENT" if any_hit else "AGENT_IMPLICIT")
    return {"tables_used": used, "units": units,
            "state": "ENUMERATED" if units else "NO_INCLUDED_TABLE_ENUMERABLE"}


# ------------------------------------------------------------------------------------ AACT local index

def norm_acronym(a: str) -> str:
    """'RALES1999' -> 'RALES'; 'EMPEROR-Preserved' -> 'EMPERORPRESERVED'; 'PIONEER 6' -> 'PIONEER6'."""
    a = re.sub(r"(?<=[A-Za-z])((?:19|20)\d\d)$", "", _flat(a))
    return re.sub(r"[^A-Z0-9]", "", a.upper().replace("‐", "-"))


def aact_index(pmids, ncts, acronyms, agent_terms, root: str | None = None) -> dict:
    """ONE streaming pass per AACT table, restricted to the identifiers asked for.

    Returns pmid->ncts (study_references, any reference_type: a comparator citing a trial's PMID is a
    link claim we then check against RESULT/DERIVED), acronym->ncts (studies.acronym, INTERVENTIONAL
    only), per-NCT study facts, per-NCT intervention names, and per-NCT registered outcomes with
    results-posted flags. Fails closed (empty index + snapshot=None) when no snapshot is present."""
    from harness import aact
    snap = aact.snapshot_dir(root)
    idx = {"snapshot": snap, "pmid_nct": {}, "acr_nct": {}, "study": {}, "interventions": {}, "outcomes": {}}
    if not snap:
        return idx
    want_p = {str(p) for p in pmids if str(p).isdigit()}
    want_a = {norm_acronym(a) for a in acronyms if norm_acronym(a)}
    for r in aact._iter_rows(os.path.join(snap, "study_references.txt")):
        p = (r.get("pmid") or "").strip()
        if p in want_p:
            idx["pmid_nct"].setdefault(p, [])
            n = r["nct_id"].upper()
            if n not in [x[0] for x in idx["pmid_nct"][p]]:
                idx["pmid_nct"][p].append((n, (r.get("reference_type") or "").upper()))
    nct_set = {n.upper() for n in ncts} | {n for v in idx["pmid_nct"].values() for n, _ in v}
    for r in aact._iter_rows(os.path.join(snap, "studies.txt")):
        n = r["nct_id"].upper()
        acr = norm_acronym(r.get("acronym") or "")
        if acr and acr in want_a and (r.get("study_type") or "").upper() == "INTERVENTIONAL":
            idx["acr_nct"].setdefault(acr, []).append(n)
            nct_set.add(n)
    agent_re = re.compile("|".join(re.escape(a) for a in agent_terms), re.I) if agent_terms else None
    for r in aact._iter_rows(os.path.join(snap, "interventions.txt")):
        n = r["nct_id"].upper()
        if n in nct_set:
            idx["interventions"].setdefault(n, []).append(r.get("name") or "")
    for r in aact._iter_rows(os.path.join(snap, "studies.txt")):
        n = r["nct_id"].upper()
        if n in nct_set:
            idx["study"][n] = {k: r.get(k) or "" for k in (
                "acronym", "brief_title", "overall_status", "phase", "enrollment", "results_first_posted_date",
                "completion_date", "study_type")}
    for r in aact._iter_rows(os.path.join(snap, "outcomes.txt")):
        n = r["nct_id"].upper()
        if n in nct_set:
            idx["outcomes"].setdefault(n, []).append({k: (r.get(k) or "")[:300] for k in (
                "id", "outcome_type", "title", "time_frame", "population", "param_type", "units")})
    idx["agent_nct"] = {n: bool(agent_re and any(agent_re.search(x) for x in v))
                        for n, v in idx["interventions"].items()}
    return idx


# ------------------------------------------------------- model PROPOSAL of a comparator's members + the gate

MEMBERS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["state", "studies"],
    "properties": {
        "state": {"type": "string", "enum": ["ENUMERATED", "NOT_ENUMERATED"]},
        "studies": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["label", "quote", "design_stated"],
            "properties": {"label": {"type": "string"}, "quote": {"type": "string"},
                           "design_stated": {"type": "string", "enum": ["RCT", "NOT_RCT", "NOT_STATED"]}}}},
    },
}

MEMBERS_PROMPT = (
    "Below, between <<<TEXT and TEXT>>>, is the text of a published systematic review / meta-analysis.\n"
    "List EVERY individual study the review INCLUDED in its quantitative synthesis (any outcome). For each study give:\n"
    "- label: the study's name EXACTLY as the text writes it (a trial acronym such as 'RECOVERY', or a first-author "
    "label such as 'Meijvis 2011'). Copy it character for character.\n"
    "- quote: one verbatim passage (at most 300 characters) copied character for character from the text that "
    "contains the label and shows the study was included. Do not paraphrase, do not join passages, do not fix typos.\n"
    "- design_stated: RCT if the text says that study was randomised, NOT_RCT if it says otherwise, else NOT_STATED.\n"
    "Do not list excluded studies, ongoing studies, or studies only mentioned in the background/discussion. Do not use "
    "outside knowledge: a study the text does not name is not listed. If the text does not name its included studies, "
    "return state NOT_ENUMERATED with an empty list.\n<<<TEXT\n")


def _norm_ws(s: str) -> str:
    return _WS.sub(" ", (s or "").replace(" ", " ")).strip()


def verify_members(claim, held_text: str) -> dict:
    """Gate for a members PROPOSAL. Each study is admitted to the measurement only when its quote is in the
    WHOLE held text (whitespace-normalised on both sides -- the same bytes the model was shown) and its label
    is inside its own quote. A refused study is kept, with its reason, never dropped silently."""
    if not isinstance(claim, dict) or claim.get("state") not in ("ENUMERATED", "NOT_ENUMERATED"):
        return {"state": "VERIFIER_REFUSED", "problems": ["NOT_TYPED"], "admitted": [], "refused": []}
    held = _norm_ws(held_text)
    admitted, refused = [], []
    for s in claim.get("studies") or []:
        q, lab = _norm_ws(s.get("quote")), _norm_ws(s.get("label"))
        probs = []
        if not q or q not in held:
            probs.append("SPAN_NOT_IN_SOURCE")
        if not lab or lab not in q:
            probs.append("LABEL_NOT_IN_QUOTE")
        (refused if probs else admitted).append({**s, "problems": probs})
    return {"state": "VERIFIER_PASS" if admitted or claim["state"] == "NOT_ENUMERATED" else "VERIFIER_REFUSED",
            "claim_state": claim["state"], "admitted": admitted, "refused": refused}


def jats_body_text(body: bytes) -> str:
    """Plain text of a JATS article body + tables (the held text for a comparator with no citing table)."""
    root = ET.fromstring(body)
    b = root.find(".//body")
    parts = [_text(b)] if b is not None else []
    for tw in root.iter("table-wrap"):
        parts.append(_text(tw))
    return "\n".join(parts)
