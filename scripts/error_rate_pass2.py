"""Integrate the scale-agnostic pass2 re-extraction (out_p2_*.json) for the rows pass1 scored NOT_FOUND,
and produce the FINAL adjudicated disagreement set. Scale-agnostic: effect magnitude + CI compared
regardless of the label the lane used (HR/RR/rate ratio), because pass1's NOT_FOUND was dominated by a
label artefact in the pass1 prompt (it passed the topic's declared estimand)."""
import glob
import json
import math
import os

WD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratchpad", "errorrate")


def _close(a, b, tol, rel=0.03):
    if a is None or b is None:
        return None
    return abs(a - b) <= tol or (b != 0 and abs(a - b) / abs(b) <= rel)


def main():
    frame = {r["row_id"]: r for r in json.load(open(os.path.join(WD, "frame.json"), encoding="utf-8"))["rows"]}
    comp = json.load(open(os.path.join(WD, "compare.json"), encoding="utf-8"))
    p1 = {r["row_id"]: r for r in comp["rows"]}
    p2 = {}
    for f in glob.glob(os.path.join(WD, "out_p2_*.json")):
        for r in json.load(open(f, encoding="utf-8-sig")).get("results", []):
            p2[r["row_id"]] = r
    resolved_match, resolved_mismatch, still_nf = [], [], []
    for rid, row in frame.items():
        if p1.get(rid, {}).get("verdict") not in ("NOT_FOUND", "NO_EXTRACTION"):
            continue
        e = p2.get(rid)
        s = row["stored"]
        t = row["rowtype"]
        if not e or not e.get("found"):
            still_nf.append((rid, row["provenance"], (e or {}).get("note", "")))
            continue
        diffs = []
        if t in ("effect",):
            if _close(e.get("effect"), s.get("effect"), 0.02) is False:
                diffs.append(f"effect stored={s.get('effect')} lane={e.get('effect')}")
            if _close(e.get("ci_low"), s.get("ci_low"), 0.03) is False:
                diffs.append(f"ci_low stored={s.get('ci_low')} lane={e.get('ci_low')}")
            if _close(e.get("ci_high"), s.get("ci_high"), 0.03) is False:
                diffs.append(f"ci_high stored={s.get('ci_high')} lane={e.get('ci_high')}")
        elif t == "count2x2":
            for k in ("ai", "n1i", "ci", "n2i"):
                if s.get(k) is not None and e.get(k) is not None and int(s[k]) != int(e[k]):
                    diffs.append(f"{k} stored={s.get(k)} lane={e.get(k)}")
        elif t == "continuous":
            for k in ("mean1", "sd1", "mean2", "sd2"):
                if _close(e.get(k), s.get(k), 0.15) is False:
                    diffs.append(f"{k} stored={s.get(k)} lane={e.get(k)}")
        if diffs:
            resolved_mismatch.append((rid, "; ".join(diffs), (e.get("verbatim_span") or "")[:200], e.get("note", "")))
        else:
            resolved_match.append(rid)
    # combined tallies
    p1_match = sum(1 for r in p1.values() if r["verdict"] == "MATCH")
    p1_mismatch = [r for r in p1.values() if r["verdict"] == "MISMATCH"]
    total_match = p1_match + len(resolved_match)
    total_mismatch = len(p1_mismatch) + len(resolved_mismatch)
    comparable = total_match + total_mismatch

    def wilson(k, n, z=1.96):
        if not n:
            return (0, 0)
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return (max(0, c - h), min(1, c + h))

    lo, hi = wilson(total_mismatch, comparable)
    print(f"POPULATION: {len(frame)} pooled numbers")
    print(f"pass1 MATCH: {p1_match}  pass1 MISMATCH: {len(p1_mismatch)}")
    print(f"pass2 resolved NOT_FOUND -> MATCH: {len(resolved_match)}  MISMATCH: {len(resolved_mismatch)}  still-not-found: {len(still_nf)}")
    print(f"COMBINED comparable: {comparable}  (MATCH {total_match} / MISMATCH {total_mismatch})")
    print(f"pre-adjudication disagreement: {total_mismatch}/{comparable} = {total_mismatch/comparable:.3%}  Wilson95 [{lo:.3%}, {hi:.3%}]")
    print(f"still-not-found (not re-checkable from abstract): {len(still_nf)}")
    print("\n=== pass2 NEW mismatches (hand-adjudicate) ===")
    for rid, d, span, note in resolved_mismatch:
        print(f"[{rid}]\n   {d}\n   span: {span}\n   note: {note}")
    print("\n=== still-not-found by provenance ===")
    from collections import Counter
    print(dict(Counter(p for _, p, _ in still_nf)))
    for rid, prov, note in still_nf:
        print(f"  {rid} [{prov}]: {note[:120]}")
    out = {"population": len(frame), "pass1_match": p1_match, "pass1_mismatch": len(p1_mismatch),
           "pass2_match": len(resolved_match), "pass2_mismatch": len(resolved_mismatch),
           "still_not_found": len(still_nf), "comparable": comparable, "total_match": total_match,
           "total_mismatch": total_mismatch, "disagreement_rate": round(total_mismatch / comparable, 4),
           "wilson95": [round(lo, 4), round(hi, 4)],
           "pass1_mismatch_rows": [r["row_id"] for r in p1_mismatch],
           "pass2_mismatch_rows": [x[0] for x in resolved_mismatch],
           "still_not_found_rows": [x[0] for x in still_nf]}
    json.dump(out, open(os.path.join(WD, "final_error_rate.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
