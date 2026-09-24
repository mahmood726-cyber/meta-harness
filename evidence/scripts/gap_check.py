"""Verify gap extractions (evidence/gaps/<KEY>.json): every span must be verbatim in a packet source (same render,
same gate as everything else). Prints, per gap field, n FOUND-and-verified / n NOT_FOUND / n refused, of N rows
extracted, and writes evidence/gaps/SUMMARY.json. A refused span is never used."""
import glob, json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT
FIELDS = ("analysis_set", "follow_up", "entry_age", "entry_other")


def main():
    rows, c = {}, collections.Counter()
    files = [p for p in sorted(glob.glob(os.path.join(ROOT, "evidence", "gaps", "*.json"))) if not p.endswith("SUMMARY.json")]
    for p in files:
        d = json.load(open(p, encoding="utf-8")); k = d.get("key") or os.path.basename(p)[:-5]
        pk = json.load(open(os.path.join(ROOT, "evidence", "packets", f"{k}.json"), encoding="utf-8"))
        allowed = {s["ref"]: textrep.render(s["ref"]) for s in pk["sources"]}
        r = {}
        for f in FIELDS:
            v = d.get(f)
            if isinstance(v, dict) and v.get("span"):
                ok = v.get("ref") in allowed and v["span"] in allowed[v["ref"]]
                r[f] = {"state": "VERIFIED" if ok else "REFUSED", **v}
            else:
                r[f] = {"state": "NOT_FOUND" if f != "entry_other" else "NONE", "raw": v}
            c[(f, r[f]["state"])] += 1
        r["notes"] = d.get("notes")
        rows[k] = r
    N = len(rows)
    print(f"gap extractions: {N}")
    for f in FIELDS:
        print(f"  {f}: " + ", ".join(f"{s} {c[(f, s)]}" for s in ("VERIFIED", "NOT_FOUND", "NONE", "REFUSED") if c[(f, s)]) + f" (of {N})")
    json.dump(rows, open(os.path.join(ROOT, "evidence", "gaps", "SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
