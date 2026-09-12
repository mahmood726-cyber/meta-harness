"""Screening reproducibility (Stage SCREENING, forward plan SC1). Compare an INDEPENDENT blind screener
(scratchpad/screen/out_scr_*.json) against the committed rule-screener decision in each review.json, over
the pooled record set, and report agreement + Cohen's kappa + sensitivity/specificity treating our
include/exclude as the reference. This measures screening REPRODUCIBILITY between two independent screeners
(the blind one is model-assisted, NOT a human gold standard — stated as such), not accuracy against truth.
'unclear' from the blind screener is reported separately (abstention), not forced to a class."""
import glob
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(ROOT, "scratchpad", "screen")


def _ours(slug):
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    out = {}
    for d in r["screening"]["records"]:
        rid = str(d["id"]).split(" ")[-1].strip()
        out[rid] = "include" if d["decision"] == "include" else "exclude"
    return out


def kappa(tp, fp, fn, tn):
    n = tp + fp + fn + tn
    if not n:
        return None
    po = (tp + tn) / n
    p_inc = ((tp + fn) / n) * ((tp + fp) / n)
    p_exc = ((fp + tn) / n) * ((fn + tn) / n)
    pe = p_inc + p_exc
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def main():
    tp = fp = fn = tn = unclear = missing = 0
    per_topic = {}
    for f in sorted(glob.glob(os.path.join(SCR, "out_scr_*.json"))):
        slug = os.path.basename(f)[len("out_scr_"):-len(".json")]
        try:
            blind = {str(d["id"]): d for d in json.load(open(f, encoding="utf-8-sig")).get("decisions", [])}
        except (OSError, ValueError):
            continue
        ours = _ours(slug)
        t = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "unclear": 0}
        for rid, od in ours.items():
            b = blind.get(rid)
            if not b:
                missing += 1
                continue
            bd = b.get("decision")
            if bd == "unclear":
                unclear += 1
                t["unclear"] += 1
                continue
            if od == "include" and bd == "include":
                tp += 1; t["tp"] += 1
            elif od == "exclude" and bd == "include":
                fp += 1; t["fp"] += 1
            elif od == "include" and bd == "exclude":
                fn += 1; t["fn"] += 1
            else:
                tn += 1; t["tn"] += 1
        per_topic[slug] = t
    decided = tp + fp + fn + tn
    agree = (tp + tn) / decided if decided else None
    k = kappa(tp, fp, fn, tn)
    sens = tp / (tp + fn) if (tp + fn) else None       # blind recovers our includes
    spec = tn / (tn + fp) if (tn + fp) else None       # blind agrees on our excludes
    out = {"_doc": "Independent blind (model-assisted) screener vs the committed rule-screener over pooled "
                   "records. Screening REPRODUCIBILITY, not accuracy vs a human gold standard.",
           "n_decided": decided, "n_unclear_blind": unclear, "n_missing_from_blind": missing,
           "tp_both_include": tp, "fp_blind_include_ours_exclude": fp,
           "fn_blind_exclude_ours_include": fn, "tn_both_exclude": tn,
           "raw_agreement": round(agree, 4) if agree is not None else None,
           "cohens_kappa": round(k, 4) if k is not None else None,
           "sensitivity_blind_vs_ours": round(sens, 4) if sens is not None else None,
           "specificity_blind_vs_ours": round(spec, 4) if spec is not None else None}
    json.dump(out, open(os.path.join(ROOT, "docs", "screen_reproducibility.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))
    # topics with the most disagreement (for inspection)
    dis = sorted(per_topic.items(), key=lambda kv: kv[1]["fp"] + kv[1]["fn"], reverse=True)[:6]
    print("\ntop-disagreement topics (fp+fn):")
    for slug, t in dis:
        print(f"  {slug}: {t}")


if __name__ == "__main__":
    main()
