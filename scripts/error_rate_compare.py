"""Deterministic compare of the BLIND re-extraction (scratchpad/errorrate/out_*.json) against the stored
pooled values (scratchpad/errorrate/frame.json). Emits a per-row verdict and a corpus error rate with a
Wilson 95% interval. Disagreements are printed for HAND adjudication (our-error vs checker-error) — the
script does not decide that; a human resolves each MISMATCH against source.

Tolerances (rounding only, both sides came from the same printed source):
  ratio effect / CI : within 0.02 absolute OR 3% relative (abstracts print 2 sig figs)
  continuous mean/SD: within 0.15 absolute (1 dp printing)
  counts (integers) : exact
A row is MATCH if every compared field agrees, MISMATCH if any disagrees, NOT_FOUND if the lane could not
find the value in source (adjudicated separately: a true not-in-source is our-error only if we pooled a
number that isn't there)."""
import json
import math
import os
import sys

WD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratchpad", "errorrate")


def _close(a, b, tol=0.02, rel=0.03):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol or (b != 0 and abs(a - b) / abs(b) <= rel)


def _cmp(row, ext):
    """Return (verdict, detail). row['stored'] vs ext (lane extraction)."""
    if not ext.get("found"):
        return "NOT_FOUND", "lane did not find the value in source"
    s = row["stored"]
    t = row["rowtype"]
    diffs = []
    if t == "effect":
        for k, tol in (("effect", 0.02), ("ci_low", 0.03), ("ci_high", 0.03)):
            if not _close(ext.get(k), s.get(k if k != "effect" else "effect"), tol=tol):
                diffs.append(f"{k}: stored={s.get(k if k!='effect' else 'effect')} lane={ext.get(k)}")
        if ext.get("scale") and s.get("scale") and ext["scale"].upper() != s["scale"].upper():
            diffs.append(f"scale: stored={s.get('scale')} lane={ext.get('scale')}")
    elif t == "continuous":
        for k, tol in (("mean1", 0.15), ("sd1", 0.15), ("mean2", 0.15), ("sd2", 0.15)):
            if not _close(ext.get(k), s.get(k), tol=tol):
                diffs.append(f"{k}: stored={s.get(k)} lane={ext.get(k)}")
        for k in ("nc1", "nc2"):
            if s.get(k) is not None and ext.get(k) is not None and int(s[k]) != int(ext[k]):
                diffs.append(f"{k}: stored={s.get(k)} lane={ext.get(k)}")
    elif t == "count2x2":
        for k in ("ai", "n1i", "ci", "n2i"):
            if s.get(k) is not None and ext.get(k) is not None and int(s[k]) != int(ext[k]):
                diffs.append(f"{k}: stored={s.get(k)} lane={ext.get(k)}")
            elif (s.get(k) is None) != (ext.get(k) is None):
                diffs.append(f"{k}: stored={s.get(k)} lane={ext.get(k)}")
    return ("MATCH", "") if not diffs else ("MISMATCH", "; ".join(diffs))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def main():
    frame = {r["row_id"]: r for r in json.load(open(os.path.join(WD, "frame.json"), encoding="utf-8"))["rows"]}
    ext = {}
    for f in os.listdir(WD):
        if f.startswith("out_") and f.endswith(".json"):
            for r in json.load(open(os.path.join(WD, f), encoding="utf-8-sig")).get("results", []):
                ext[r["row_id"]] = r
    rows = []
    counts = {"MATCH": 0, "MISMATCH": 0, "NOT_FOUND": 0, "NO_EXTRACTION": 0}
    for rid, row in frame.items():
        e = ext.get(rid)
        if e is None:
            counts["NO_EXTRACTION"] += 1
            rows.append({"row_id": rid, "verdict": "NO_EXTRACTION", "detail": "lane produced no row"})
            continue
        v, d = _cmp(row, e)
        counts[v] += 1
        rows.append({"row_id": rid, "verdict": v, "detail": d, "provenance": row["provenance"],
                     "stored": row["stored"], "lane_span": e.get("verbatim_span", "")[:200], "lane_note": e.get("note", "")})
    n = len(frame)
    # residual-error denominator: rows where the lane produced a comparable extraction
    comparable = counts["MATCH"] + counts["MISMATCH"]
    lo, hi = wilson(counts["MISMATCH"], comparable) if comparable else (0, 0)
    summary = {"n_population": n, "counts": counts, "comparable": comparable,
               "mismatch_rate": round(counts["MISMATCH"] / comparable, 4) if comparable else None,
               "mismatch_wilson95": [round(lo, 4), round(hi, 4)],
               "note": "MISMATCH and NOT_FOUND require HAND adjudication vs source to split our-error "
                       "from checker-error; the rate above is pre-adjudication disagreement."}
    json.dump({"summary": summary, "rows": rows}, open(os.path.join(WD, "compare.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary, indent=1))
    print("\n--- rows needing hand adjudication (MISMATCH / NOT_FOUND / NO_EXTRACTION) ---")
    for r in rows:
        if r["verdict"] != "MATCH":
            print(f"[{r['verdict']}] {r['row_id']}")
            print(f"    {r.get('detail','')}")
            if r.get("lane_span"):
                print(f"    lane span: {r['lane_span']}")


if __name__ == "__main__":
    main()
