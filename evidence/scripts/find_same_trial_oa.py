"""For rows whose analysis set is still unsupported, find OPEN-ACCESS papers that cite the trial's own registration
number (Europe PMC full-text search), acquire them (OA XML is redistributable, held in-tree) and attach them as
same-trial companions. A paper that merely cites the NCT in passing is still attached; the gap extractor must quote
a span that is about THIS trial's analysis, and the lane reads it. Usage: python find_same_trial_oa.py KEY [KEY...]"""
import json, os, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import acquire as A
from acquire_pid import acquire
ROOT = A.ROOT


def main(keys):
    wl = {w["key"]: w for w in json.load(open(os.path.join(ROOT, "evidence", "worklist.json"), encoding="utf-8"))["rows"]}
    cp = os.path.join(ROOT, "evidence", "companions.json"); comp = json.load(open(cp, encoding="utf-8"))
    for k in keys:
        w = wl[k]
        ncts = sorted({x for x in [w.get("family_id"), w["trial"]] + [h.get("nct") for h in w["held"]] if x and str(x).startswith("NCT")})
        for nct in ncts:
            u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=8&resultType=lite&query="
                 + urllib.parse.quote(f'ABSTRACT:"{nct}" AND OPEN_ACCESS:Y'))
            st, b = A.get(u)
            hits = json.loads(b)["resultList"]["result"] if st == 200 else []
            for h in hits[:2]:
                pid = h.get("pmid")
                if not pid or pid == w["pid"]:
                    continue
                print(k, nct, acquire(pid))
                ref_dir = os.path.join(ROOT, "evidence", "held", pid)
                for f in sorted(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else []:
                    if f.endswith(".xml"):
                        ref = f"evidence/held/{pid}/{f}"
                        lst = comp.setdefault(k, [])
                        if ref not in [x["ref"] for x in lst]:
                            lst.append({"ref": ref, "why": f"open-access paper citing this trial's registration {nct} (Europe PMC full-text search); same-trial relevance judged per span"})
                time.sleep(0.4)
    json.dump(comp, open(cp, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1:])
