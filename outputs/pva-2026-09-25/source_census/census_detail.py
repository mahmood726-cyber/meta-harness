"""Second pass over census.json: strip section labels on BOTH sides, then diff at word level, so a record that only lost its
'BACKGROUND:'-style labels is not called abridged, and a real edit is shown as the exact words removed/added."""
import difflib
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
LABEL = re.compile(r"(?:(?<=^)|(?<=\s))(?:[A-Z][A-Z ,/&-]{2,60}):\s")
d = json.load(open(sys.argv[1], encoding="utf-8"))
commit = d["commit"]
xml_cache = {}


def held_text(r):
    rec = json.loads(subprocess.run(["git", "-C", "C:/mh-lanes/pva", "show", f"{commit}:{r['file']}"], capture_output=True,
                                    text=True, encoding="utf-8").stdout)
    return next(x["abstract"] for x in rec["records"] if str(x.get("id")) == r["pmid"])


sys.path.insert(0, "C:/mh-lanes/pva/v1")
import source_census as sc  # noqa: E402
import xml.etree.ElementTree as ET  # noqa: E402

out = []
for r in d["rows"]:
    if r["class"] in ("IDENTICAL", "FORMAT_ONLY"):
        continue
    raw = d.get("_rawdir", sys.argv[2]) + "/" + r["raw"]
    if raw not in xml_cache:
        xml_cache[raw] = {sc._txt(a.find(".//MedlineCitation/PMID")): sc.rebuild(a)
                          for a in ET.fromstring(open(raw, "rb").read()).findall(".//PubmedArticle")}
    pub, held = xml_cache[raw][r["pmid"]], held_text(r)
    ph, hh = sc.norm(LABEL.sub("", pub)), sc.norm(LABEL.sub("", held))
    labels_only = ph == hh
    sm = difflib.SequenceMatcher(None, ph.split(), hh.split(), autojunk=False)
    removed, added = [], []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op in ("delete", "replace"):
            removed.append(" ".join(ph.split()[a0:a1]))
        if op in ("insert", "replace"):
            added.append(" ".join(hh.split()[b0:b1]))
    words_removed = sum(len(x.split()) for x in removed)
    words_added = sum(len(x.split()) for x in added)
    cls = ("LABELS_ONLY" if labels_only else
           "ABRIDGED_AND_EDITED" if words_removed > 20 and words_removed > 3 * max(words_added, 1) else
           "ABRIDGED" if not added else "TEXT_DIFFERS")
    out.append({"slug": r["slug"], "pmid": r["pmid"], "class2": cls, "pubmed_words": len(ph.split()), "held_words": len(hh.split()),
                "words_removed": words_removed, "words_added": words_added, "removed_spans": removed, "added_spans": added})
    print(f"\n===== {cls} {r['slug']} {r['pmid']} pubmed {len(ph.split())} words, held {len(hh.split())}; "
          f"removed {words_removed}, added {words_added}")
    for x in removed[:12]:
        print("  - ", x[:260])
    for x in added[:8]:
        print("  + ", x[:260])
json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
