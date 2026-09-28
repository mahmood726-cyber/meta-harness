"""Acquire the PubMed reports of every trial a held comparator names that we do not hold (V1.0.1, PCSK9 review).

Writes cache/<slug>/comparator_named.json and cache/<slug>/comparator_named_pubmed.xml; harness/comparator_named.py
re-derives the records from the held XML at build time. Row states:
  ALREADY_HELD   one of the row's identifiers (PMID, NCT, DOI) is already among our records or families
  CANDIDATE      its PubMed report(s): the PMID it cites, else every PubMed record indexed with its NCT ([si]),
                 else the record its DOI resolves to ([aid])
  NOT_IN_PUBMED  it has an identifier, and no PubMed record is registered as that trial (the query is recorded)
  NO_IDENTIFIER  the comparator row carries no PMID, NCT or DOI: named, not screened
usage: python scripts/comparator_named.py [--write] --only SLUG | --all"""
import hashlib, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import comparator_named as cn, family_pub_links, http  # noqa: E402
from harness.fetch import EUTILS, parse_pubmed_xml  # noqa: E402

P = {"tool": "meta-harness", "email": "meta-harness@example.org"}


def esearch(term):
    d = http.get_json(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", "term": term, "retmode": "json", "retmax": 50, **P})
    time.sleep(0.4)
    return d.get("esearchresult", {}).get("idlist", []), term


def build(slug, write):
    rows = cn.panel_rows(ROOT, slug)
    if not rows:
        return {"state": "NO_ENUMERATED_COMPARATOR"}
    records = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    records = family_pub_links.merge(ROOT, slug, records)
    fp = os.path.join(ROOT, "cache", slug, "families.json")
    fams = json.load(open(fp, encoding="utf-8"))["families"] if os.path.exists(fp) else []
    have = cn.held_keys(records, fams)
    named_ncts = {i for _, _, ids in rows for i in ids if cn._is_nct(i)}
    out, want = [], []
    for cid, fid, ids in rows:
        row = {"comparator": cid, "row": fid, "identifiers": ids}
        held = [i for i in ids if cn._norm_id(i) in have]
        if held:
            out.append(dict(row, state="ALREADY_HELD", held_by=held))
            continue
        if not ids:
            out.append(dict(row, state="NO_IDENTIFIER"))
            continue
        pmids = [i for i in ids if i.isdigit()]
        query = None
        if not pmids:
            nct = next((i for i in ids if cn._is_nct(i)), None)
            doi = next((i for i in ids if i.startswith("10.")), None)
            pmids, query = esearch(f"{nct}[si]") if nct else esearch(f"{doi}[aid]")
        if not pmids:
            out.append(dict(row, state="NOT_IN_PUBMED", query=query))
            continue
        out.append(dict(row, state="CANDIDATE", pmids=sorted(pmids, key=int), **({"query": query} if query else {})))
        want += pmids
    want = sorted(set(want), key=int)
    xml = http.get_text(f"{EUTILS}/efetch.fcgi", {"db": "pubmed", "id": ",".join(want), "retmode": "xml", **P}) if want else ""
    parsed = {r["id"]: r for r in parse_pubmed_xml(xml)} if xml else {}
    dbl = cn.databank_ncts(xml) if xml else {}
    for r in out:
        if r["state"] == "CANDIDATE":
            ncts = [i for i in r["identifiers"] if cn._is_nct(i)]
            # an NCT search can return a paper that merely mentions the id: keep only records registered AS that trial
            # and attributed (fetch._select_nct) to a trial some comparator row names -- a pooled analysis that lists this
            # trial among others is attributed elsewhere
            keep = [p for p in r["pmids"] if p in parsed and (not ncts or (set(ncts) & set(dbl.get(p) or [])
                                                                          and parsed[p].get("nct") in named_ncts))]
            dropped = [p for p in r["pmids"] if p not in keep]
            r["pmids"] = keep
            if dropped:
                r["not_this_trial"] = dropped
            if not keep:
                r["state"] = "NOT_IN_PUBMED"
    rel = f"cache/{slug}/comparator_named_pubmed.xml"
    doc = {"schema": "comparator-named-v1", "slug": slug, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "reported_by": "external review of the pcsk9-mace topic (28 Sep 2026): every trial named in a held comparator "
                          "must become a screened candidate",
           "rows": out}
    if xml:
        raw = xml.encode("utf-8")
        doc["pubmed_xml"] = {"document_ref": rel, "sha256": hashlib.sha256(raw).hexdigest(),
                             "request": f"{EUTILS}/efetch.fcgi?db=pubmed&id={','.join(want)}&retmode=xml"}
    res = {"state": "WRITTEN" if write else "WOULD_WRITE",
           "rows": {s: sum(r["state"] == s for r in out) for s in ("ALREADY_HELD", "CANDIDATE", "NOT_IN_PUBMED", "NO_IDENTIFIER")},
           "records": sum(len(r.get("pmids") or []) for r in out if r["state"] == "CANDIDATE")}
    if write:
        if xml:
            open(os.path.join(ROOT, rel), "wb").write(xml.encode("utf-8"))
        open(os.path.join(ROOT, "cache", slug, "comparator_named.json"), "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        cn.load(ROOT, slug)
    return res


def main(argv):
    write = "--write" in argv
    if "--only" in argv:
        slugs = [argv[argv.index("--only") + 1]]
    else:
        slugs = sorted(os.path.basename(os.path.dirname(p)) for p in
                       [os.path.join(ROOT, "cache", d, "comparators.json") for d in os.listdir(os.path.join(ROOT, "cache"))]
                       if os.path.exists(p))
    for s in slugs:
        print(s, json.dumps(build(s, write)), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
