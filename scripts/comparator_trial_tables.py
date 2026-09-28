"""Enumerate each registered comparator's INCLUDED-TRIAL TABLE from its PMC full text (JATS), wherever the article is
in PMC under an open licence, and store it as the comparator panel's located trial_set -- replacing the "comparator
trial table not machine-exposed" state wherever the table can in fact be fetched (V1.0.1, external review of the
colchicine-POAF topic).

For each topic (topics/<slug>.json with a comparator_pmid) the outcome is exactly one named state:
  ALREADY_ENUMERATED  the panel already carries a located trial_set (left untouched)
  NOT_IN_PMC          the PMC ID converter maps the PMID to no PMCID
  FETCH_FAILED        a request failed (status recorded; never read as "no table")
  NOT_OPEN_LICENSE    the JATS carries no Creative Commons / open-access licence: not held, not enumerated
  NO_INCLUDED_TABLE   no table whose first column links >= 2 rows to references
  AMBIGUOUS_TABLES    several such tables with DIFFERENT reference sets: nothing written
  WRITTEN             the table's rows were written as the trial_set (validated by comparator_panel.validate)

A row is one included trial. It is located as its raw <tr> in the held JATS; its identity is the reference(s) its
first cell links to: PMID and DOI become panel aliases (each a located <ref> span); a reference with neither is keyed
bibliographically (journal:year:volume:first page, each printed in the located <ref>). Endpoint membership is not in
the table, so it is left unknown (never guessed).
usage: python scripts/comparator_trial_tables.py [--write] [--only SLUG]"""
import hashlib, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import comparator_panel  # noqa: E402

TOOL = "tool=meta-harness&email=meta-harness@example.org"
LOG = []


def get(url):
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness"}), timeout=60) as r:
            body, status = r.read(), r.status
    except Exception as exc:  # noqa: BLE001 -- recorded, never swallowed into a "no table"
        body, status = b"", f"ERROR {type(exc).__name__}: {exc}"
    LOG.append({"url": url, "utc": t0, "status": status, "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest() if body else None})
    time.sleep(0.4)
    return status, body


INCLUDED_CAPTION = re.compile(r"(?:characteristic|summar)\w*\b.{0,60}\b(?:included|eligible)\b|"
                              r"\bincluded (?:stud|trial|rct|citation)", re.I)


def norm_journal(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _text(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x or "")).strip()


def refs(xml):
    out = {}
    for m in re.finditer(r'<ref id="([^"]+)">.*?</ref>', xml, re.S):
        r = m.group(0)
        g = lambda t: _text((re.search(rf"<{t}[^>]*>(.*?)</{t}>", r, re.S) or [None, ""])[1])
        out[m.group(1)] = {"span": {"start": m.start(), "end": m.end(), "quote": r},
                           "ids": dict(re.findall(r'<pub-id pub-id-type="(pmid|doi)">([^<]+)</pub-id>', r)),
                           "surname": g("surname"), "year": g("year")[:4], "source": g("source"),
                           "volume": g("volume"), "fpage": g("fpage")}
    return out


def bibr_rids(cell):
    """Reference ids a cell links to, whatever the attribute order (<xref ref-type="bibr" rid=..> or <xref rid=..
    ref-type="bibr">); a multi-id rid ("CR3 CR4") yields each id."""
    out = []
    for tag in re.findall(r"<xref\b[^>]*>", cell):
        if re.search(r'ref-type="bibr"', tag):
            m = re.search(r'rid="([^"]+)"', tag)
            if m:
                out += m.group(1).split()
    return out


def printed_name(cell_head, row_raw):
    """The row's label as printed: the longest leading run of words of the first cell (before its reference link)
    that occurs verbatim in the raw row; None if even the first word is not verbatim (markup inside it)."""
    words = _text(cell_head).strip(" [(,;").split()
    for n in range(len(words), 0, -1):
        cand = " ".join(words[:n]).strip(" [(,;.")
        if cand and cand in row_raw:
            return cand
    return None


def trial_tables(xml):
    """(caption, [(row_match, first_cell_raw, rids)]) for tables whose first column links >= 2 rows to references."""
    found = []
    for tw in re.finditer(r"<table-wrap\b.*?</table-wrap>", xml, re.S):
        cap = _text((re.search(r"<caption>(.*?)</caption>", tw.group(0), re.S) or [None, ""])[1])
        rows = []
        for tr in re.finditer(r"<tr\b[^>]*>.*?</tr>", tw.group(0), re.S):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(0), re.S)
            if not cells:
                continue
            rids = bibr_rids(cells[0])
            if rids:
                rows.append(((tw.start() + tr.start(), tw.start() + tr.end()), cells[0], rids))
        if len(rows) >= 2:
            found.append((cap, rows))
    return found


# V1.0.1 (PCSK9 review): an included-trial table may identify its rows by the REGISTRATION it prints, not by a
# reference link (Wang 2022, PMC9755489: "ODYSSEY COMBO I<break/> NCT01644175"). Accepted only when the caption names
# the included studies and every data row's first cell prints exactly one NCT; the row's <tr> is the alias span, so
# the identifier and the printed name are bound by the same located row, never by a name match.
_NCT = re.compile(r"(?<![A-Za-z0-9])NCT\d{8}(?!\d)")


def registry_tables(xml):
    """(caption, [(row_match, first_cell_raw, nct)]) for included-caption tables whose data rows print one NCT each."""
    found = []
    for tw in re.finditer(r"<table-wrap\b.*?</table-wrap>", xml, re.S):
        cap = _text((re.search(r"<caption>(.*?)</caption>", tw.group(0), re.S) or [None, ""])[1])
        if not INCLUDED_CAPTION.search(cap):
            continue
        body = re.search(r"<tbody\b[^>]*>.*?</tbody>", tw.group(0), re.S)     # REV-R2: <tbody valign="top">
        if not body:
            continue
        rows, bad = [], False
        off = tw.start() + body.start()
        for tr in re.finditer(r"<tr\b[^>]*>.*?</tr>", body.group(0), re.S):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(0), re.S)
            ncts = sorted(set(_NCT.findall(_text(cells[0])))) if cells else []
            if len(ncts) != 1:
                bad = True
                break
            rows.append(((off + tr.start(), off + tr.end()), cells[0], ncts[0]))
        if not bad and len(rows) >= 2:
            found.append((cap, rows))
    return found


def choose_route(xml):
    """('REFERENCE_LINKED', reference tables) or ('REGISTRY_ID_IN_ROW', registry tables). REV-R2 (codex review,
    reproduced): a reference-linked table whose caption does not name the included studies (e.g. an excluded-studies
    table) must not win over an included-caption registry table."""
    tables = trial_tables(xml)
    if tables and not (not any(INCLUDED_CAPTION.search(c) for c, _ in tables) and registry_tables(xml)):
        return "REFERENCE_LINKED", tables
    return "REGISTRY_ID_IN_ROW", registry_tables(xml)


def build_registry_rows(xml, xml_raw, rel, rows):
    sha = hashlib.sha256(xml_raw).hexdigest()
    entries = []
    for (s, e), cell, nct in rows:
        head = _text(re.split(r"<break\s*/>|<ext-link|NCT\d{8}", cell)[0]).strip()
        name = head if head and head in xml[s:e] else None
        span = {"start": s, "end": e, "quote": xml[s:e]}
        m = {"family_id": f"{name or nct} [{nct}]", "span": span, "endpoint": None,
             "aliases": [{"id": nct, "document_ref": rel, "document_sha256": sha, "span": span,
                          "bound_by": "registration printed in the same table row"}]}
        if name:
            m["name_in_source"] = name
        entries.append(m)
    return entries


def build(slug, write):
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    pmid = str(cfg.get("comparator_pmid") or "")
    ppath = os.path.join(ROOT, "cache", slug, "comparators.json")
    if not pmid or not os.path.exists(ppath):
        return {"state": "NO_REGISTERED_COMPARATOR"}
    raw_panel = open(ppath, encoding="utf-8").read()
    panel = json.loads(raw_panel)
    entry = next((c for c in panel if pmid in str(c.get("citation") or "") or pmid == str(c.get("id") or "")), None)
    if entry is None:
        return {"state": "NO_PANEL_ENTRY"}
    if entry.get("trial_set"):
        return {"state": "ALREADY_ENUMERATED", "k": len(entry["trial_set"])}
    st, body = get(f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids={pmid}&format=json&{TOOL}")
    if st != 200:
        return {"state": "FETCH_FAILED", "step": "idconv", "status": st}
    pmcid = (json.loads(body).get("records") or [{}])[0].get("pmcid")
    if not pmcid:
        return {"state": "NOT_IN_PMC"}
    st, xml_raw = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}&retmode=xml&{TOOL}")
    if st != 200 or b"<article" not in xml_raw:
        return {"state": "FETCH_FAILED", "step": "efetch", "status": st, "pmcid": pmcid}
    xml = xml_raw.decode("utf-8")
    lic = (re.search(r"creativecommons\.org/(?:licenses|publicdomain)/[a-z-]+/[0-9.]+", xml) or [None])[0] \
        if re.search(r"creativecommons\.org/(?:licenses|publicdomain)/", xml) else None
    if not lic and 'license-type="open-access"' not in xml:
        return {"state": "NOT_OPEN_LICENSE", "pmcid": pmcid}
    route, tables = choose_route(xml)
    if route == "REGISTRY_ID_IN_ROW":
        reg = tables
        if len(reg) != 1:
            return {"state": "NO_INCLUDED_TABLE" if not reg else "AMBIGUOUS_TABLES", "pmcid": pmcid, "license": lic}
        cap, rows = reg[0]
        rel = f"cache/{slug}/comparator_pmc_jats.xml"
        entries = build_registry_rows(xml, xml_raw, rel, rows)
        result = {"state": "WRITTEN" if write else "WOULD_WRITE", "route": "REGISTRY_ID_IN_ROW", "pmcid": pmcid,
                  "license": lic, "caption": cap, "k": len(entries), "bound": len(entries),
                  "rows": [m["family_id"] for m in entries], "notes": []}
        if write:
            open(os.path.join(ROOT, rel), "wb").write(xml_raw)
            entry["trial_set"] = entries
            entry["trial_set_document"] = {"document_ref": rel, "document_sha256": hashlib.sha256(xml_raw).hexdigest(),
                                           "source": "PMC JATS (efetch db=pmc)", "pmcid": pmcid, "license": lic,
                                           "fetched_utc": LOG[-1]["utc"], "table_caption": cap,
                                           "row_identity": "REGISTRY_ID_IN_ROW"}
            comparator_panel.validate(entry, ROOT)
            open(ppath, "w", encoding="utf-8", newline="\n").write(
                json.dumps(panel, indent=2 if raw_panel.startswith("[\n  ") else 1, ensure_ascii=False)
                + ("\n" if raw_panel.endswith("\n") else ""))
        return result
    sets = {tuple(sorted({r for _, _, rids in rows for r in rids})) for _, rows in tables}
    if len(sets) > 1:
        # several reference-linked tables with different sets: take the ONE whose caption names the included (or
        # eligible) studies/trials; otherwise refuse rather than pick
        named = [t for t in tables if INCLUDED_CAPTION.search(t[0])]
        if len({tuple(sorted({r for _, _, rids in rows for r in rids})) for _, rows in named}) != 1:
            return {"state": "AMBIGUOUS_TABLES", "pmcid": pmcid, "tables": [c for c, _ in tables]}
        tables = named
    cap, rows = tables[0]
    rf = refs(xml)
    rel = f"cache/{slug}/comparator_pmc_jats.xml"
    sha = hashlib.sha256(xml_raw).hexdigest()
    entries, notes = [], []
    for (s, e), cell, rids in rows:
        name = printed_name(cell.split("<xref")[0], xml[s:e])
        r0 = rf.get(rids[0]) or {}
        family_id = f"{name or r0.get('surname') or rids[0]} {r0.get('year') or ''} [{rids[0]}]".replace("  ", " ")
        m = {"family_id": family_id, "name_in_source": name, "references": rids,
             "span": {"start": s, "end": e, "quote": xml[s:e]}, "endpoint": None, "aliases": []}
        for rid in rids:
            ref = rf.get(rid)
            if not ref:
                notes.append(f"{family_id}: reference {rid} not in the reference list")
                continue
            for kind in ("pmid", "doi"):
                if ref["ids"].get(kind):
                    # bound by the row's own reference link (rid), never by matching names
                    m["aliases"].append({"id": ref["ids"][kind], "document_ref": rel, "document_sha256": sha,
                                         "span": ref["span"], "linked_rid": rid})
            if not ref["ids"] and ref["source"] and ref["year"] and ref["volume"] and ref["fpage"]:
                m["bib_key"] = f"bib:{norm_journal(ref['source'])}:{ref['year']}:{ref['volume']}:{ref['fpage']}"
                m["bib_key_span"] = ref["span"]
        if not name:
            m.pop("name_in_source")
        entries.append(m)
    result = {"state": "WRITTEN" if write else "WOULD_WRITE", "pmcid": pmcid, "license": lic, "caption": cap,
              "k": len(entries), "bound": sum(bool(m["aliases"] or m.get("bib_key")) for m in entries),
              "rows": [m["family_id"] for m in entries], "notes": notes}
    if write:
        open(os.path.join(ROOT, rel), "wb").write(xml_raw)
        entry["trial_set"] = entries
        entry["trial_set_document"] = {"document_ref": rel, "document_sha256": sha, "source": "PMC JATS (efetch db=pmc)",
                                       "pmcid": pmcid, "license": lic, "fetched_utc": LOG[-1]["utc"],
                                       "table_caption": cap}
        comparator_panel.validate(entry, ROOT)
        open(ppath, "w", encoding="utf-8", newline="\n").write(
            json.dumps(panel, indent=2 if raw_panel.startswith("[\n  ") else 1, ensure_ascii=False)
            + ("\n" if raw_panel.endswith("\n") else ""))
    return result


# ---------------------------------------------------------------------------------------------------------------
# TEXT TRANSCRIPTION ROUTE (V1.0.1, pericarditis review): a comparator whose table is not in PMC but IS in our
# committed full-text transcription. The only curated input is cache/<slug>/comparator_table_spec.json -- the table's
# anchor text and each row's label AS PRINTED. Everything else is mechanical and validated: each row is located as
# the text from its label to the next label; a row binds to a trial only through the unique PRIMARY-role report
# among our records whose title (or registry acronym field) carries the row's name as a whole token (CORP never
# matches CORP-2); anything else stays unbound and is disclosed.
def _record_blocks(rec_text):
    """(record id, start, end) of every record object in a records.json text (brace-matched, strings respected)."""
    out, i = [], 0
    for m in re.finditer(r'\{\s*"id": "([^"]+)"', rec_text):
        if m.start() < i:
            continue
        depth, in_str, esc = 0, False, False
        for j in range(m.start(), len(rec_text)):
            ch = rec_text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    out.append((m.group(1), m.start(), j + 1))
                    i = j + 1
                    break
    return out


def _cited_aliases(spec, row, all_names):
    """The comparator's own citation of a transcription row: in the held JATS (spec['refs_document']), the printed
    name followed -- with no other row's name and no other citation between -- by an xref to row['cited_ref'], whose
    <ref> carries a PMID or DOI. Returns {'aliases', 'citation'} or the reason it cannot."""
    rel = spec.get("refs_document")
    if not rel:
        return "cited_ref needs the spec's refs_document (the held JATS)"
    raw = open(os.path.join(ROOT, rel), "rb").read()
    xml = raw.decode("utf-8")
    ref = refs(xml).get(row["cited_ref"])
    if not ref or not (ref["ids"].get("pmid") or ref["ids"].get("doi")):
        return f"reference {row['cited_ref']} has no PMID/DOI in {rel}"
    hits = []
    for mm in re.finditer(r"(?<![A-Za-z0-9-])" + re.escape(row["name_in_source"]) + r"(?![A-Za-z0-9]|-\d)", xml):
        tail = xml[mm.end():mm.end() + 400]
        x = re.search(r"<xref\b[^>]*>", tail)
        if not x or row["cited_ref"] not in bibr_rids(x.group(0)):
            continue
        between = _text(tail[:x.start()])
        if any(n != row["name_in_source"] and n in between for n in all_names):
            continue
        hits.append((mm.start(), mm.end() + x.end()))
    if not hits:
        return f"{row['name_in_source']} is never followed by a citation of {row['cited_ref']}"
    a, b = hits[0]
    sha = hashlib.sha256(raw).hexdigest()
    cn = {"start": a, "end": b, "quote": xml[a:b]}
    return {"aliases": [{"id": ref["ids"][k], "document_ref": rel, "document_sha256": sha, "span": ref["span"],
                         "linked_rid": row["cited_ref"], "cited_name_span": cn} for k in ("pmid", "doi") if ref["ids"].get(k)],
            "citation": {"document_ref": rel, "span": cn}}


def from_text_spec(slug, write):
    spec_p = os.path.join(ROOT, "cache", slug, "comparator_table_spec.json")
    if not os.path.exists(spec_p):
        return {"state": "NO_TEXT_SPEC"}
    from harness import trial_family
    spec = json.load(open(spec_p, encoding="utf-8"))
    doc = spec["document_ref"]
    raw = open(os.path.join(ROOT, doc), "rb").read()
    text = raw.decode("utf-8")
    t0 = text.index(spec["table_anchor"])
    if text.count(spec["table_anchor"]) != 1:
        return {"state": "AMBIGUOUS_TABLES", "why": "table anchor not unique"}
    t1 = text.index(spec["end_anchor"], t0)
    starts = []
    for row in spec["rows"]:
        i = text.find(row["label"], t0, t1)
        if i < 0 or text.find(row["label"], i + 1, t1) >= 0:
            return {"state": "ROW_NOT_LOCATED", "row": row["label"]}
        starts.append(i)
    if starts != sorted(starts):
        return {"state": "ROW_ORDER", "why": "row labels are not in table order"}
    ends = starts[1:] + [t1]
    rec_path = f"cache/{slug}/records.json"
    rec_raw = open(os.path.join(ROOT, rec_path), "rb").read()
    rec_text = rec_raw.decode("utf-8")
    recs = {str(r.get("id")): r for k, v in json.loads(rec_text).items() if isinstance(v, list)
            for r in v if isinstance(r, dict) and r.get("id")}
    blocks = {rid: (a, b) for rid, a, b in _record_blocks(rec_text)}
    entries, notes = [], []
    for row, a, b in zip(spec["rows"], starts, ends):
        name = row["name_in_source"]
        # V1.0.1 (SGLT2-HFrEF review): a transcription prints 'DAPA‐HF' with a Unicode hyphen; compare as '-'
        _hy = {c: "-" for c in (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2212)}
        pat = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(name.translate(_hy)) + r"(?![A-Za-z0-9]|-\d)")
        prim = [rid for rid, r in recs.items()
                if pat.search(((r.get("title") or "") + " " + (r.get("acronym") or "")).translate(_hy))
                and trial_family.report_role(r)[0] in ("PRIMARY", "PRIMARY_WITH_POOLED_ANALYSIS")]
        m = {"family_id": f"{name} (row {len(entries) + 1})", "name_in_source": name,
             "span": {"start": a, "end": a + len(text[a:b].rstrip()), "quote": text[a:b].rstrip()},
             "endpoint": None, "aliases": []}
        if row.get("cited_ref"):
            # V1.0.1 (MRA-HFrEF review): a row may bind through the comparator's OWN citation of it -- the reference
            # its prose cites right after the printed name (RALES ... ( <xref rid="B1"> )) -- when the held JATS carries
            # that reference's PMID/DOI. Never by matching names across documents; a pre-registration trial (RALES)
            # has no acronym in our records, so its name cannot bind it.
            cit = _cited_aliases(spec, row, [r["name_in_source"] for r in spec["rows"]])
            if isinstance(cit, str):
                return {"state": "CITATION_NOT_LOCATED", "row": row["label"], "why": cit}
            m["aliases"] += cit["aliases"]
            m["references"] = [row["cited_ref"]]
            m["citation"] = cit["citation"]
        if m["aliases"]:
            pass
        elif len(prim) == 1 and prim[0] in blocks:
            ba, bb = blocks[prim[0]]
            m["aliases"].append({"id": prim[0], "document_ref": rec_path,
                                 "document_sha256": hashlib.sha256(rec_raw).hexdigest(),
                                 "span": {"start": ba, "end": bb, "quote": rec_text[ba:bb]}})
        else:
            notes.append(f"{name}: {len(prim)} primary report(s) among our records carry the name -- not bound")
        entries.append(m)
    result = {"state": "WRITTEN" if write else "WOULD_WRITE", "source": "text transcription", "k": len(entries),
              "bound": sum(bool(m["aliases"]) for m in entries), "rows": [m["family_id"] for m in entries],
              "notes": notes}
    if write:
        ppath = os.path.join(ROOT, "cache", slug, "comparators.json")
        raw_panel = open(ppath, encoding="utf-8").read()
        panel = json.loads(raw_panel)
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        pmid = str(cfg.get("comparator_pmid") or "")
        entry = next(c for c in panel if pmid in str(c.get("citation") or "") or pmid == str(c.get("id") or ""))
        if entry.get("trial_set"):
            return {"state": "ALREADY_ENUMERATED", "k": len(entry["trial_set"])}
        entry["trial_set"] = entries
        entry["trial_set_document"] = {"document_ref": doc, "document_sha256": hashlib.sha256(raw).hexdigest(),
                                       "source": "committed full-text transcription + cache/<slug>/comparator_table_spec.json",
                                       "table_caption": spec["table_anchor"]}
        comparator_panel.validate(entry, ROOT)
        open(ppath, "w", encoding="utf-8", newline="\n").write(
            json.dumps(panel, indent=2 if raw_panel.startswith("[\n  ") else 1, ensure_ascii=False)
            + ("\n" if raw_panel.endswith("\n") else ""))
    return result


def main(argv):
    write = "--write" in argv
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    slugs = sorted(os.path.basename(p)[:-5] for p in os.listdir(os.path.join(ROOT, "topics")) if p.endswith(".json")) \
        if not only else [only]
    slugs = [s if not s.endswith(".json") else s[:-5] for s in slugs]
    report = {}
    for slug in slugs:
        if not os.path.isdir(os.path.join(ROOT, "docs", "reviews", slug)):
            continue
        report[slug] = build(slug, write)
        if report[slug]["state"] in ("NOT_IN_PMC", "NOT_OPEN_LICENSE", "NO_INCLUDED_TABLE") and \
                os.path.exists(os.path.join(ROOT, "cache", slug, "comparator_table_spec.json")):
            report[slug] = dict(from_text_spec(slug, write), pmc_state=report[slug]["state"])
        print(slug, report[slug]["state"], {k: v for k, v in report[slug].items() if k in ("pmcid", "k", "bound", "license")})
    out = os.path.join(ROOT, "evidence", "comparator_tables")
    os.makedirs(out, exist_ok=True)
    if write:
        json.dump({"run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "topics": report, "requests": LOG},
                  open(os.path.join(out, "COMPARATOR_TABLES.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    return report


if __name__ == "__main__":
    main(sys.argv)
