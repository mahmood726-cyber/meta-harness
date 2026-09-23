"""Check the second adjudications: every quote must be verbatim in a packet source (same render, same gate as the
first adjudication), then tally AGREE / DISAGREE / CANNOT_TELL per question with n of N. A second opinion whose
quotes do not verify is reported as UNVERIFIED and never counted as agreement or disagreement."""
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT


def main():
    rows = {}
    for p in sorted(q for q in glob.glob(os.path.join(ROOT, "evidence/second_adjudication/*.json")) if not q.endswith("SUMMARY.json")):
        d = json.load(open(p, encoding="utf-8")); k = d.get("key") or os.path.basename(p)[:-5]
        pk = json.load(open(os.path.join(ROOT, f"evidence/packets/{k}.json"), encoding="utf-8"))
        allowed = {s["ref"]: textrep.render(s["ref"]) for s in pk["sources"]}
        bad = []
        for part in ("number", "entry"):
            for q in (d.get(part) or {}).get("quotes") or []:
                if q.get("ref") not in allowed or q.get("span", "") not in allowed[q["ref"]]:
                    bad.append(f"{part}: quote not verbatim in {q.get('ref')}: {q.get('span','')[:80]!r}")
        rows[k] = {"number": (d.get("number") or {}).get("verdict"), "entry": (d.get("entry") or {}).get("verdict"),
                   "entry_ruling": (d.get("entry") or {}).get("your_ruling"), "quote_errors": bad,
                   "number_why": (d.get("number") or {}).get("why"), "entry_why": (d.get("entry") or {}).get("why"), "missed": d.get("missed")}
    N = len(rows)
    ver = {k: v for k, v in rows.items() if not v["quote_errors"]}
    from collections import Counter
    print(f"second adjudications: {N}; quotes verified in {len(ver)} of {N}")
    for part in ("number", "entry"):
        print(f"  {part}: " + ", ".join(f"{a} {b}" for a, b in sorted(Counter(v[part] for v in ver.values()).items())) + f" (of {len(ver)} verified)")
    for k, v in rows.items():
        if v["quote_errors"] or "DISAGREE" in (v["number"], v["entry"]):
            print(f"- {k}: number {v['number']} / entry {v['entry']} ({v['entry_ruling']}) {'UNVERIFIED ' + str(v['quote_errors']) if v['quote_errors'] else ''}")
            print(f"    number: {(v['number_why'] or '')[:300]}\n    entry: {(v['entry_why'] or '')[:300]}\n    missed: {(v['missed'] or '')[:300]}")
    json.dump(rows, open(os.path.join(ROOT, "evidence/second_adjudication/SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
