"""NCT leg of the identity-chain census: for every served trial family (review.json trial_families[].identity_basis at V1),
each report PMID is checked against the NCT ids ITS OWN PubMed record names (DataBank accession numbers, SecondaryIds, and
NCT mentions in its abstract), read from the source census's raw efetch XML.
  NCT_OTHER      the PubMed record names NCT id(s), none of which is the family's registry id  -> identity mismatch
  NCT_CONFIRMED  the PubMed record names the family's registry id
  NCT_UNSTATED   the PubMed record names no NCT id                                             -> cannot be verified here
  NO_XML         the report PMID is not among the held PubMed records"""
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
NCT = re.compile(r"NCT\d{8}")
own = {}
for n in subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", BR, "outputs/pva-2026-09-25/source_census/raw/"], capture_output=True, text=True).stdout.split():
    for a in ET.fromstring(gzip.decompress(subprocess.run(["git", "-C", REPO, "show", f"{BR}:{n}"], capture_output=True).stdout)).findall(".//PubmedArticle"):
        pm = "".join(a.find(".//MedlineCitation/PMID").itertext()).strip()
        ids = set()
        for acc in a.findall(".//DataBank/AccessionNumberList/AccessionNumber"):
            ids |= set(NCT.findall(acc.text or ""))
        for s in a.findall(".//OtherID") + a.findall(".//SecondaryId"):
            ids |= set(NCT.findall(s.text or ""))
        ids |= set(NCT.findall(" ".join("".join(x.itertext()) for x in a.findall(".//Abstract/AbstractText"))))
        own[pm] = ids
slugs = [p.split("/")[-1] for p in subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", "9eacfe09", "docs/reviews/"], capture_output=True, text=True).stdout.split() if "." not in p.split("/")[-1]]
rows = []
for s in slugs:
    r = json.loads(subprocess.run(["git", "-C", REPO, "show", f"9eacfe09:docs/reviews/{s}/review.json"], capture_output=True, text=True, encoding="utf-8").stdout)
    for i, fam in enumerate(r.get("trial_families") or []):
        ib = fam.get("identity_basis") or {}
        regs = [x for x in ib.get("registry_ids") or [] if str(x).startswith("NCT")]
        if not regs:
            continue
        for pm in ib.get("primary_report_ids") or []:
            pm = re.sub(r"\D", "", str(pm))
            if pm not in own:
                cls = "NO_XML"
            elif set(regs) & own[pm]:
                cls = "NCT_CONFIRMED"
            elif own[pm]:
                cls = "NCT_OTHER"
            else:
                cls = "NCT_UNSTATED"
            rows.append({"slug": s, "family_index": i, "family_registry_ids": regs, "report_pmid": pm, "pubmed_ncts": sorted(own.get(pm, [])),
                         "class": cls})
json.dump(rows, open("C:/mh-lanes/tmp-pva/idcensus/nct_families.json", "w", encoding="utf-8"), indent=1)
print("family report links checked:", len(rows), dict(Counter(r["class"] for r in rows)))
for r in rows:
    if r["class"] == "NCT_OTHER":
        print(f"  NCT_OTHER {r['slug'][:34]:34} fam#{r['family_index']:<3} registry {','.join(r['family_registry_ids'])[:40]:40} report {r['report_pmid']:>9} PubMed names {','.join(r['pubmed_ncts'])[:60]}")
