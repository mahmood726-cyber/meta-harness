"""Root-cause census for DOI_NOT_PUBMEDS: harness/fetch.py::_efetch's DOI fallback loops over EVERY .//ArticleId without a
break, so with no ELocationID DOI it keeps the LAST DOI in the record -- in PubMed XML that is the last cited reference's.
Simulate that exact logic on today's efetch XML (source census raw), and compare with (a) the held record's DOI and (b) the
article's own PubmedData DOI, for every held PMID record at V1."""
import gzip
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
REPO = "C:/mh-lanes/pva"
BR = "pva/v1-acceptance"


def txt(e):
    return "".join(e.itertext()).strip() if e is not None else ""


def harness_doi(art):                     # verbatim logic of harness/fetch.py::_efetch lines 111-118 at 9eacfe09
    doi = ""
    for eid in art.findall(".//ELocationID"):
        if eid.get("EIdType") == "doi":
            doi = txt(eid)
    if not doi:
        for aid in art.findall(".//ArticleId"):
            if aid.get("IdType") == "doi":
                doi = txt(aid)
    return doi


arts = {}
for n in subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", BR, "outputs/pva-2026-09-25/source_census/raw/"],
                        capture_output=True, text=True).stdout.split():
    for a in ET.fromstring(gzip.decompress(subprocess.run(["git", "-C", REPO, "show", f"{BR}:{n}"], capture_output=True).stdout)).findall(".//PubmedArticle"):
        arts[txt(a.find(".//MedlineCitation/PMID"))] = a
rows = []
files = [p for p in subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", "9eacfe09", "--", "cache"], capture_output=True,
                                   text=True).stdout.split() if re.fullmatch(r"cache/[^/]+/records\.json", p)]
for f in files:
    d = json.loads(subprocess.run(["git", "-C", REPO, "show", f"9eacfe09:{f}"], capture_output=True, text=True, encoding="utf-8").stdout)
    for r in d.get("records", []):
        if r.get("id_type") != "pmid":
            continue
        pm, held = str(r["id"]), (r.get("doi") or "").lower()
        a = arts.get(pm)
        if a is None:
            rows.append({"slug": f.split("/")[1], "pmid": pm, "class": "NO_XML"})
            continue
        own = next((txt(x).lower() for x in a.findall("./PubmedData/ArticleIdList/ArticleId") if x.get("IdType") == "doi"), "")
        refs = {txt(x).lower() for x in a.findall(".//ReferenceList//ArticleId") if x.get("IdType") == "doi"}
        sim = harness_doi(a).lower()
        cls = ("OK" if held == own else
               "HELD_IS_A_CITED_REFERENCE" if held in refs else
               "HELD_EMPTY" if not held else
               "OTHER_DIFFERENCE")
        rows.append({"slug": f.split("/")[1], "pmid": pm, "held_doi": held, "own_doi": own, "harness_today": sim,
                     "harness_today_is_ref": sim in refs and sim != own, "class": cls, "title": (r.get("title") or "")[:90]})
json.dump(rows, open("C:/mh-lanes/tmp-pva/idcensus/doi_lastref.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
c = Counter(r["class"] for r in rows)
print("held PubMed records:", len(rows), dict(c))
print("today, the harness logic would take a REFERENCE's DOI for:", sum(1 for r in rows if r.get("harness_today_is_ref")), "records")
for r in rows:
    if r["class"] not in ("OK", "NO_XML"):
        print(f"  {r['class']:26} {r['slug'][:34]:34} {r['pmid']:>9} held {r['held_doi'][:40]:40} own {r['own_doi'][:36]}")
