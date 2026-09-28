import gzip
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
REPO = "C:/mh-lanes/pva"
BR = "pva/v1-acceptance"
held = {"27737646": ("vitamin-d-acute-respiratory-infection", "10.2307/2533164"), "24159237": ("azithromycin-copd-exacerbation", "10.1056/nejmoa1300799"),
        "15499830": ("zinc-common-cold-duration", "10.1016/s0008-6215(00)80664-3"), "27826955": ("vitamin-d-acute-respiratory-infection", "10.1002/14651858.cd008824"),
        "27749986": ("omega3-cardiovascular-events", "10.1002/14651858.cd012151")}
names = subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", BR, "outputs/pva-2026-09-25/source_census/raw/"], capture_output=True, text=True).stdout.split()
arts = {}
for n in names:
    for a in ET.fromstring(gzip.decompress(subprocess.run(["git", "-C", REPO, "show", f"{BR}:{n}"], capture_output=True).stdout)).findall(".//PubmedArticle"):
        pm = "".join(a.find(".//MedlineCitation/PMID").itertext()).strip()
        if pm in held:
            arts[pm] = a
for pm, (slug, bad) in held.items():
    a = arts.get(pm)
    refs = [x.text.lower() for x in a.findall(".//ReferenceList//ArticleId") if x.get("IdType") == "doi"] if a is not None else []
    pos = refs.index(bad.lower()) + 1 if bad.lower() in refs else None
    f = f"cache/{slug}/records.json"
    commits = subprocess.run(["git", "-C", REPO, "log", "--format=%h|%ad|%s", "--date=format:%Y-%m-%d", "--reverse", "9eacfe09", "--", f],
                             capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    first = None
    for line in commits:
        c = line.split("|")[0]
        d = json.loads(subprocess.run(["git", "-C", REPO, "show", f"{c}:{f}"], capture_output=True, text=True, encoding="utf-8").stdout or "{}")
        r = next((r for r in d.get("records", []) if str(r.get("id")) == pm), None)
        if r and (r.get("doi") or "").lower() == bad.lower():
            first = line
            break
    print(f"{pm} held doi {bad}: in today's ReferenceList at position {pos} of {len(refs)} | first commit holding it: {first[:120] if first else '?'}")
