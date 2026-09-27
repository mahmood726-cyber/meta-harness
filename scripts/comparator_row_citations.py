"""Bind NAME-ONLY comparator trial rows to the publication each row cites (V1.0.1).

Once the publication-year rule was removed from the overlap relation (a trial's own paper can post-date a comparator
that already analysed it), a comparator row with no identifier -- "Young 2015", "COPE study" -- could no longer be told
apart from our pooled trials, and the relation fell to NOT_ENUMERABLE. The identity was always available: each row
cites a numbered reference in the comparator's own text. This script binds the row to that reference's PMID:

  jats       the comparator's PMC JATS (held only under an open licence): the included-trials table row whose first cell
             carries the row's surname and year links, by its own xref, to a <ref> with a PMID/DOI
  ecitmatch  the row's printed reference number -> the numbered entry of the held text's reference list -> PubMed's
             citation matcher (journal|year|volume|first page|author), whose response line is held and carries the PMID

Each alias is a located span holding the identifier (harness/comparator_panel.validate). A row that cannot be bound is
left name-only and reported; nothing is matched by name similarity.

usage: python scripts/comparator_row_citations.py <slug> {jats|ecitmatch} [--write]
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("ctt", os.path.join(ROOT, "scripts", "comparator_trial_tables.py"))
ctt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctt)
TOOL = "tool=meta-harness&email=mahmood726%40gmail.com"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "meta-harness (mailto:mahmood726@gmail.com)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = r.read()
    time.sleep(0.4)
    return body


def _panel(slug):
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    p = os.path.join(ROOT, "cache", slug, "comparators.json")
    raw = open(p, encoding="utf-8").read()
    panel = json.loads(raw)
    pmid = str(cfg["comparator_pmid"])
    entry = next(c for c in panel if pmid in str(c.get("citation") or "") or pmid == str(c.get("id") or ""))
    return cfg, p, raw, panel, entry


def _save(p, raw, panel):
    open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(panel, indent=2 if raw.startswith("[\n  ") else 1, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))


def _surname_year(member):
    name = (member.get("name_in_source") or member["family_id"]).split()[0].lower()
    y = re.search(r"\b(19|20)\d{2}\b", member["family_id"])
    return re.sub(r"[^a-z]", "", name), (y.group(0) if y else None)


def jats(slug, write):
    cfg, p, raw, panel, entry = _panel(slug)
    ids = json.loads(_get(f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids={cfg['comparator_pmid']}&format=json&{TOOL}"))
    pmcid = (ids.get("records") or [{}])[0].get("pmcid")
    if not pmcid:
        return {"state": "NOT_IN_PMC"}
    xml_raw = _get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}&retmode=xml&{TOOL}")
    xml = xml_raw.decode("utf-8")
    lic = re.search(r"creativecommons\.org/(?:licenses|publicdomain)/[a-z-]+/[0-9.]+", xml)
    if not lic and 'license-type="open-access"' not in xml:
        return {"state": "NOT_OPEN_LICENSE", "pmcid": pmcid}
    rel = f"cache/{slug}/comparator_pmc_jats.xml"
    refs = ctt.refs(xml)
    rows = [(re.sub(r"<[^>]+>", " ", label), rids, sp) for _cap, trows in ctt.trial_tables(xml) for sp, label, rids in trows]
    out = []
    for m in entry.get("trial_set") or []:
        if m.get("aliases"):
            continue
        sn, yr = _surname_year(m)
        # the table row names the surname and links its reference; the YEAR is the reference's own (Zayed's rows
        # print 'Young [10]' and 'Young [17]'; CR10 is 2015, CR17 is 2014)
        hits = [(label, rids, sp) for label, rids, sp in rows if sn in re.sub(r"[^a-z ]", " ", label.lower()).split()]
        rids = sorted({r for _, rs, _sp in hits for r in rs if r in refs and (not yr or str(refs[r].get("year")) == yr)})
        pm = [(r, refs[r]) for r in rids if refs[r]["ids"].get("pmid") or refs[r]["ids"].get("doi")]
        hits = [h for h in hits if set(h[1]) & set(rids)] or hits
        if len(pm) == 1:
            r, ref = pm[0]
            ident = ref["ids"].get("pmid") or ref["ids"].get("doi")
            row = next(h for h in hits if r in h[1])
            a, b = row[2]
            m["name_in_source"] = m.get("name_in_source") or m["family_id"].split()[0]
            m["aliases"] = [{"id": ident, "document_ref": rel, "document_sha256": hashlib.sha256(xml_raw).hexdigest(),
                             "span": ref["span"], "linked_rid": r,
                             "table_row_span": {"start": a, "end": b, "quote": xml[a:b]},
                             "bound_by": f"JATS table row {row[0].strip()!r} -> {r} (year {yr} from the reference)"}]
            out.append((m["family_id"], ident))
        else:
            out.append((m["family_id"], f"NOT BOUND ({len(pm)} candidate references)"))
    if write:
        open(os.path.join(ROOT, rel), "wb").write(xml_raw)
        _save(p, raw, panel)
    return {"state": "BOUND" if write else "WOULD_BIND", "pmcid": pmcid, "license": lic.group(0) if lic else "open-access",
            "rows": out}


_REF_ENTRY = re.compile(r"(?:^|\s)(\d{1,3})\.\s+(.+?)(?=\s\d{1,3}\.\s+[A-Z][a-z]|\Z)", re.S)
_CITE = re.compile(r"([A-Z][A-Za-z .&]+?)\s+((?:19|20)\d{2});\s*(\d+)(?:\(\d+\))?:\s*[A-Za-z]?(\d+)")


def ecitmatch(slug, write):
    cfg, p, raw, panel, entry = _panel(slug)
    doc = (entry.get("trial_set_document") or {}).get("document_ref") or entry["document_ref"]
    text = open(os.path.join(ROOT, doc), encoding="utf-8").read()
    ref_block = text[text.index("REFERENCES"):]
    entries = {int(n): re.sub(r"\s+", " ", body).strip() for n, body in _REF_ENTRY.findall(ref_block)}
    queries, keys = [], {}
    for m in entry.get("trial_set") or []:
        if m.get("aliases"):
            continue
        q = m["span"]["quote"]
        num = re.search(r"\b(\d{1,3})\s+[A-Z][A-Za-z ]+/(?:19|20)\d{2}\b", q)
        ref = entries.get(int(num.group(1))) if num else None
        c = _CITE.search(ref or "")
        if not c:
            keys[m["family_id"]] = ("NOT BOUND", f"reference {num.group(1) if num else '?'} not parsed")
            continue
        # author left blank: journal + year + volume + first page identify the article, and a transcription can
        # split a surname ('Finke lstein')
        key = f"{m['family_id']}"
        journal = c.group(1).strip().split(". ")[-1].strip()       # the segment after the title: 'Herz', not 'Colchicine ... Herz'
        line = "|".join([journal, c.group(2), c.group(3), c.group(4), "", key]) + "|"
        queries.append(line)
        keys[m["family_id"]] = (line, ref)
    if not queries:
        return {"state": "NOTHING_TO_BIND", "rows": keys}
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?db=pubmed&retmode=xml&" + TOOL
           + "&bdata=" + urllib.parse.quote("\r".join(queries)))
    body = _get(url)
    rel = f"cache/{slug}/comparator_ref_ecitmatch.txt"
    held = (f"# PubMed ecitmatch, {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n# request: {url}\n"
            + body.decode("utf-8"))
    held_raw = held.encode("utf-8")
    out = []
    for m in entry.get("trial_set") or []:
        if m.get("aliases") or m["family_id"] not in keys or keys[m["family_id"]][0] == "NOT BOUND":
            if m["family_id"] in keys:
                out.append((m["family_id"], keys[m["family_id"]][1]))
            continue
        resp = next((ln for ln in held.splitlines() if ln.split("|")[-2:-1] == [m["family_id"]] or
                     (len(ln.split("|")) >= 7 and ln.split("|")[5] == m["family_id"])), None)
        pmid = resp.split("|")[-1].strip() if resp else ""
        if resp and pmid.isdigit():
            start = held.index(resp)
            m["aliases"] = [{"id": pmid, "document_ref": rel, "document_sha256": hashlib.sha256(held_raw).hexdigest(),
                             "span": {"start": start, "end": start + len(resp), "quote": resp},
                             "bound_by": f"row reference -> held reference entry “{keys[m['family_id']][1][:160]}” -> PubMed ecitmatch"}]
            out.append((m["family_id"], pmid))
        else:
            out.append((m["family_id"], f"NOT BOUND (ecitmatch: {resp!r})"))
    if write:
        open(os.path.join(ROOT, rel), "wb").write(held_raw)
        _save(p, raw, panel)
    return {"state": "BOUND" if write else "WOULD_BIND", "rows": out}


if __name__ == "__main__":
    slug, route = sys.argv[1], sys.argv[2]
    res = {"jats": jats, "ecitmatch": ecitmatch}[route](slug, "--write" in sys.argv)
    print(json.dumps(res, indent=1, ensure_ascii=False)[:3000])
