"""Enumerate a comparator's included-trial table whose rows print only "Surname, year" (V1.0.1, semaglutide-weight review).

Medicine 2026 (PMID 42536519, PMC13433015, CC BY) lists its 4 trials in Table 1 as "O'Neil, 2018", "Rubino, 2021",
"Wadden, 2021", "Wilding, 2021", with no reference link in the row. Each binds to the ONE <ref> of the same held JATS
whose first author and year are the row's -- a bibliographic identity, re-proved by harness/comparator_panel.validate
(author_year_row), including that no other reference shares the key. A row with zero or several matching references is
refused, never guessed.

usage: python scripts/comparator_author_year_rows.py <slug> "<table caption text>" [--write]
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from harness.comparator_panel import ref_author_year, validate, visible_text  # noqa: E402
import comparator_stated_k_members as sk  # noqa: E402


def run(slug, caption, write):
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    ids = json.loads(sk._get(f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids={cfg['comparator_pmid']}&format=json&{sk.TOOL}"))
    pmcid = (ids.get("records") or [{}])[0].get("pmcid")
    if not pmcid:
        return {"state": "NOT_IN_PMC"}
    raw = sk._get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid[3:]}&retmode=xml&{sk.TOOL}")
    xml = raw.decode("utf-8")
    lic = re.search(r"creativecommons\.org/(?:licenses|publicdomain)/[a-z-]+/[0-9.]+", xml)
    if not lic and 'license-type="open-access"' not in xml:
        return {"state": "NOT_OPEN_LICENSE", "pmcid": pmcid}
    tws = [m for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", xml, re.S)
           if caption in visible_text((re.search(r"<caption>(.*?)</caption>", m.group(0), re.S) or [None, ""])[1])]
    if len(tws) != 1:
        return {"state": "REFUSED", "why": f"{len(tws)} tables carry the caption (need exactly one)"}
    tw = tws[0]
    body = re.search(r"<tbody\b[^>]*>.*?</tbody>", tw.group(0), re.S)
    refs = [(m, ref_author_year(m.group(0))) for m in re.finditer(r'<ref id="[^"]+">.*?</ref>', xml, re.S)]
    sha = hashlib.sha256(raw).hexdigest()
    rel = f"cache/{slug}/comparator_pmc_jats.xml"
    members = []
    off = tw.start() + body.start()
    for tr in re.finditer(r"<tr\b[^>]*>.*?</tr>", body.group(0), re.S):
        cell = visible_text(re.search(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(0), re.S).group(1))
        m = re.fullmatch(r"(.+?), (\d{4})", cell.replace("’", "'"))
        if not m:
            return {"state": "REFUSED", "why": f"row {cell!r} does not print 'Surname, year'"}
        hits = [rm for rm, key in refs if key == (m.group(1), m.group(2))]
        if len(hits) != 1:
            return {"state": "REFUSED", "why": f"row {cell!r} names {len(hits)} references (need exactly one)"}
        rm = hits[0]
        pmid = re.search(r'pub-id-type="pmid">(\d+)<', rm.group(0))
        if not pmid:
            return {"state": "REFUSED", "why": f"row {cell!r}: its reference carries no PMID"}
        row = {"start": off + tr.start(), "end": off + tr.end(), "quote": xml[off + tr.start():off + tr.end()]}
        ref = {"start": rm.start(), "end": rm.end(), "quote": rm.group(0)}
        printed = visible_text(re.search(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(0), re.S).group(1)).split(",")[0]
        members.append({"family_id": f"{printed} {m.group(2)}", "name_in_source": printed, "span": row, "endpoint": None,
                        "aliases": [{"id": pmid.group(1), "document_ref": rel, "document_sha256": sha, "span": ref,
                                     "author_year_row": row,
                                     "bound_by": f"table row '{cell}' names the one reference whose first author and year "
                                                 f"are {m.group(1)}, {m.group(2)}; it carries PMID {pmid.group(1)}"}]})
    out = {"state": "BOUND" if write else "WOULD_BIND", "pmcid": pmcid, "license": lic.group(0) if lic else "open-access",
           "k": len(members), "members": [(x["family_id"], x["aliases"][0]["id"]) for x in members]}
    if write:
        open(os.path.join(ROOT, rel), "wb").write(raw)
        p = os.path.join(ROOT, "cache", slug, "comparators.json")
        raw_panel = open(p, encoding="utf-8").read()
        panel = json.loads(raw_panel)
        c = next(x for x in panel if str(x["id"]) == str(cfg["comparator_pmid"]))
        if c.get("trial_set"):
            return {"state": "ALREADY_ENUMERATED", "k": len(c["trial_set"])}
        c["trial_set"] = members
        c["trial_set_document"] = {"document_ref": rel, "document_sha256": sha, "source": "PMC JATS (efetch db=pmc)",
                                   "pmcid": pmcid, "license": out["license"], "row_identity": "AUTHOR_YEAR_TO_REFERENCE",
                                   "table_caption": caption}
        validate(c, ROOT)
        open(p, "w", encoding="utf-8", newline="\n").write(
            json.dumps(panel, indent=2 if raw_panel.startswith("[\n  ") else 1, ensure_ascii=False)
            + ("\n" if raw_panel.endswith("\n") else ""))
    return out


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--write"]
    print(json.dumps(run(a[0], a[1], "--write" in sys.argv), indent=1, ensure_ascii=False))
