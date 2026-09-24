"""Verify gap extractions (evidence/gaps/<KEY>.json) plus the lane's hand bindings (evidence/gaps/MANUAL.json): every
span must be verbatim in a packet source (same render, same gate). The source scope of every verified span is
DERIVED here, deterministically, so re-running can never drop it:
  OWN_REPORT               the row's own report, its abstract record or its registry entry
  SAME_TRIAL_OTHER_REPORT  another report on the same trial (a companion)
  ..._PLANNED              the span is protocol / analysis-plan language ('will be')
Writes evidence/gaps/SUMMARY.json. A refused span is never used; a hand binding overrides a codex NOT_FOUND and
records who bound it."""
import glob, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT
FIELDS = ("analysis_set", "follow_up", "entry_age", "entry_other")


def source_scope(ref, span, own_pid):
    own = bool(own_pid and own_pid in ref) or "records.json" in ref or "/registry/" in ref
    return ("OWN_REPORT" if own else "SAME_TRIAL_OTHER_REPORT") + ("_PLANNED" if re.search(r"\bwill be\b", span) else "")


def main():
    wl = {w["key"]: w for w in json.load(open(os.path.join(ROOT, "evidence", "worklist.json"), encoding="utf-8"))["rows"]}
    mp = os.path.join(ROOT, "evidence", "gaps", "MANUAL.json")
    manual = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    rows, c = {}, collections.Counter()
    files = [p for p in sorted(glob.glob(os.path.join(ROOT, "evidence", "gaps", "*.json")))
             if os.path.basename(p) not in ("SUMMARY.json", "MANUAL.json")]
    for p in files:
        d = json.load(open(p, encoding="utf-8")); k = d.get("key") or os.path.basename(p)[:-5]
        for f, v in (manual.get(k) or {}).items():
            d[f] = v
        pk = json.load(open(os.path.join(ROOT, "evidence", "packets", f"{k}.json"), encoding="utf-8"))
        allowed = {s["ref"]: textrep.render(s["ref"]) for s in pk["sources"]}
        r = {}
        for f in FIELDS:
            v = d.get(f)
            if isinstance(v, dict) and v.get("span"):
                ok = v.get("ref") in allowed and v["span"] in allowed[v["ref"]]
                r[f] = {**v, "state": "VERIFIED" if ok else "REFUSED",
                        "source_scope": source_scope(v.get("ref", ""), v["span"], wl[k]["pid"]) if ok else None}
            else:
                r[f] = {"state": "NOT_FOUND" if f != "entry_other" else "NONE", "raw": v}
            c[(f, r[f]["state"])] += 1
        r["notes"] = d.get("notes")
        rows[k] = r
    N = len(rows)
    print(f"gap extractions: {N} (hand bindings merged: {sum(len(v) for v in manual.values())})")
    for f in FIELDS:
        print(f"  {f}: " + ", ".join(f"{s} {c[(f, s)]}" for s in ("VERIFIED", "NOT_FOUND", "NONE", "REFUSED") if c[(f, s)]) + f" (of {N})")
    json.dump(rows, open(os.path.join(ROOT, "evidence", "gaps", "SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
