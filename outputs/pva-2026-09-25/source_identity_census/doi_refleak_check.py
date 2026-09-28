"""Hypothesis test: harness/fetch.py::_efetch takes a DOI from `.//ArticleId` (any descendant, INCLUDING the ReferenceList),
so an article with no ELocationID DOI gets a cited reference's DOI. For each suspect PMID, read the raw efetch XML held by the
source census and report: ELocationID DOI, the article's own PubmedData ArticleIdList DOI, the FIRST .//ArticleId DOI (what
the harness would take), and whether that one sits inside a ReferenceList."""
import gzip
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
REPO = "C:/mh-lanes/pva"
BR = "pva/v1-acceptance"
suspects = sys.argv[1].split(",")
names = subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", BR, "outputs/pva-2026-09-25/source_census/raw/"],
                       capture_output=True, text=True).stdout.split()
found = {}
for n in names:
    xml = gzip.decompress(subprocess.run(["git", "-C", REPO, "show", f"{BR}:{n}"], capture_output=True).stdout)
    for art in ET.fromstring(xml).findall(".//PubmedArticle"):
        pm = "".join(art.find(".//MedlineCitation/PMID").itertext()).strip()
        if pm in suspects:
            found[pm] = art
harness_style = {}
for pm in suspects:
    art = found.get(pm)
    if art is None:
        print(pm, "not in census raw XML")
        continue
    eloc = [e.text for e in art.findall(".//ELocationID") if e.get("EIdType") == "doi"]
    own = [a.text for a in art.findall("./PubmedData/ArticleIdList/ArticleId") if a.get("IdType") == "doi"]
    first_any = next((a.text for a in art.findall(".//ArticleId") if a.get("IdType") == "doi"), None)
    in_refs = first_any in {a.text for a in art.findall(".//ReferenceList//ArticleId") if a.get("IdType") == "doi"}
    harness = eloc[0] if eloc else first_any
    print(f"{pm}: ELocationID {eloc or '-'} | own ArticleIdList {own or '-'} | harness would take {harness} "
          f"({'FROM THE REFERENCE LIST' if (not eloc and in_refs and harness not in own) else 'own'})")
