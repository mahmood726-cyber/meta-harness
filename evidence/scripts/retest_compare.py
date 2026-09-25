"""Score the pre-registered extractor test-retest (evidence/PREREG_extractor_agreement.md). Primary: agreement on the
bound numbers, compared as numbers. Rows whose packet gained sources between the passes are reported separately by
name (their disagreement may be new evidence, not noise)."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import verify_records as V
ROOT = V.ROOT
NUM = ("estimate", "ci_low", "ci_high", "events_t", "n_t", "events_c", "n_c", "mean_t", "sd_t", "mean_c", "sd_c")


def nums(rec):
    bv = rec.get("bound_values") or {}
    return {k: V.canon(bv.get(k)) for k in NUM if V.canon(bv.get(k)) is not None}


def main():
    sample_file = sys.argv[1] if len(sys.argv) > 1 else "retest_sample.txt"
    sample = open(os.path.join(ROOT, "evidence", "extractions", sample_file)).read().split()
    comp = json.load(open(os.path.join(ROOT, "evidence", "companions.json"), encoding="utf-8"))
    rows, c = {}, collections.Counter()
    for k in sample:
        a_p = os.path.join(ROOT, "evidence", "extractions", "raw", f"{k}.json")
        b_p = os.path.join(ROOT, "evidence", "extractions", "retest", f"{k}.json")
        if not os.path.exists(b_p):
            rows[k] = {"state": "RETEST_MISSING"}; c["RETEST_MISSING"] += 1; continue
        a, b = json.load(open(a_p, encoding="utf-8")), json.load(open(b_p, encoding="utf-8"))
        na, nb = nums(a), nums(b)
        shared = set(na) & set(nb)
        if not na or not nb or not shared:
            state = "NOT_COMPARABLE"
        else:
            state = "AGREE" if all(abs(na[x] - nb[x]) < 1e-9 for x in shared) else "DISAGREE"
        pk = json.load(open(os.path.join(ROOT, "evidence", "packets", f"{k}.json"), encoding="utf-8"))
        vb = V.verify(b, pk)
        packet_changed = k in comp
        rows[k] = {"state": state, "first": na, "retest": nb, "verdict_first": a.get("verdict"), "verdict_retest": b.get("verdict"),
                   "entry_first": (a.get("entry_population_matches_question") or {}).get("value"),
                   "entry_retest": (b.get("entry_population_matches_question") or {}).get("value"),
                   "retest_spans_verify": not vb["errors"], "packet_changed_between_passes": packet_changed}
        c[state] += 1
        c["verdict_" + ("AGREE" if a.get("verdict") == b.get("verdict") else "DISAGREE")] += 1
        c["entry_" + ("AGREE" if rows[k]["entry_first"] == rows[k]["entry_retest"] else "DISAGREE")] += 1
        c["spans_verify_" + str(not vb["errors"])] += 1
    N = len(sample)
    out = {"N": N, "primary_bound_numbers": {s: c[s] for s in ("AGREE", "DISAGREE", "NOT_COMPARABLE", "RETEST_MISSING")},
           "verdict": {"AGREE": c["verdict_AGREE"], "DISAGREE": c["verdict_DISAGREE"]},
           "entry_reading": {"AGREE": c["entry_AGREE"], "DISAGREE": c["entry_DISAGREE"]},
           "retest_spans_verify": {"yes": c["spans_verify_True"], "no": c["spans_verify_False"]},
           "packet_changed_rows": sorted(k for k, r in rows.items() if r.get("packet_changed_between_passes")), "rows": rows}
    json.dump(out, open(os.path.join(ROOT, "evidence", "extractions", "RETEST_RESULT.json" if sample_file == "retest_sample.txt" else ("RETEST_EXTENSION_U23.json" if "u23" in sample_file else "RETEST_S16.json")), "w", encoding="utf-8", newline="\n"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for k, r in rows.items():
        if r["state"] == "DISAGREE":
            print("DISAGREE", k, r["first"], "vs", r["retest"], "packet_changed" if r["packet_changed_between_passes"] else "")


if __name__ == "__main__":
    main()
