"""Attach every locally held full text (evidence/held_local/<pid>/*.html) to the packets of the rows for that PMID,
as a companion with a stated reason. Idempotent."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT


def main():
    cp = os.path.join(ROOT, "evidence", "companions.json")
    c = json.load(open(cp, encoding="utf-8"))
    wl = json.load(open(os.path.join(ROOT, "evidence", "worklist.json"), encoding="utf-8"))["rows"]
    added = 0
    for p in glob.glob(os.path.join(ROOT, "evidence", "held_local", "*", "*.html")):
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        pid = rel.split("/")[-2]
        for w in wl:
            if w["pid"] == pid:
                lst = c.setdefault(w["key"], [])
                if rel not in [x["ref"] for x in lst]:
                    lst.append({"ref": rel, "why": "the trial's own full text (PMC free, not OA): held LOCAL-ONLY, "
                                                   "URL + sha256 in evidence/LOCAL_ACQUISITIONS.json"})
                    added += 1
    json.dump(c, open(cp, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print("companions added", added)


if __name__ == "__main__":
    main()
