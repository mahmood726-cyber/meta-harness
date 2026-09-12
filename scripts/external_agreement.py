"""External-standard agreement (VALIDATION, the weak side): compare our pooled PRIMARY estimate to the
PUBLISHED comparator meta-analysis's own reported pooled estimate on the same question. This is our
synthesis vs an external hand-built synthesis -- the closest pooled-level ground truth we hold for every
topic (the per-trial Cochrane head-to-head, scripts feeding docs/cochrane_headtohead.json, is the deeper
check where a review tabulates per-trial data). Object-derived from review.json (comparator.reported)."""
import glob
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# divergences (|log-ratio| >= 0.12) adjudicated against the record: why our pooled differs from theirs.
ADJUDICATION = {
    "colchicine-postop-af": "Different trial set: we pool k=5 (incl. null low-dose trials); the comparator's "
                            "0.62 pools a different, more-positive set. Same direction (protective).",
    "colchicine-recurrent-pericarditis": "Same direction; 0.47 vs 0.40 (|log|=0.16). Our k is smaller "
                            "(strict double-blind + recurrence-definition).",
    "corticosteroids-cap-mortality": "We are k=1 (CAPE-COD RR 0.53); the comparator pools several (0.69). "
                            "Single-trial vs pool -- our smaller evidence base, not an extraction error.",
    "corticosteroids-covid19-mortality": "Scale/set mismatch: our RECOVERY-only rate ratio (IRR 0.83) vs the "
                            "comparator's pooled REACT odds ratio (0.66). Different estimand and trial set.",
    "esketamine-trd-madrs": "NOT COMPARABLE: our outcome is MADRS change (MD -4.07); the comparator's is "
                            "response RATE (RR 1.44). Different outcome/scale.",
    "metformin-pcos-ovulation": "We are k=1 (Vandermolen OR 8.25, an outlier-high single trial); the Cochrane "
                            "review pools many (OR 2.64). The Cochrane pool is the reliable value -- our k=1 is "
                            "a small-evidence artefact, exactly what the larger-evidence-base expansion tier "
                            "targets. The per-trial Cochrane head-to-head examines this directly.",
    "statins-primary-prevention-elderly": "We are k=1 (a pre-specified elderly subgroup HR 0.61); the "
                            "comparator pools more (0.75). Single-subgroup vs pool.",
}


def build():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(f))
        r = json.load(open(f, encoding="utf-8"))
        prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None)
        if not prim:
            continue
        res = prim.get("result") or {}
        ours, osc = res.get("estimate"), res.get("scale")
        reps = (r.get("comparator") or {}).get("reported") or []
        if ours is None or not reps:
            continue
        rep = reps[0]
        theirs, tsc = rep.get("estimate"), rep.get("scale")
        if theirs is None:
            continue
        ratio = (osc or "").upper() not in ("MD", "SMD") and (tsc or "").upper() not in ("MD", "SMD")
        try:
            logdiff = abs(math.log(ours) - math.log(theirs)) if ratio else None
        except (ValueError, TypeError):
            logdiff = None
        rows.append({"slug": slug, "our_estimate": ours, "our_scale": osc,
                     "their_estimate": theirs, "their_scale": tsc, "their_outcome": rep.get("outcome"),
                     "log_ratio_diff": round(logdiff, 3) if logdiff is not None else None,
                     "agree_within_12pct": bool(logdiff is not None and logdiff < 0.12),
                     "adjudication": ADJUDICATION.get(slug, "")})
    n = len(rows)
    agree = sum(1 for x in rows if x["agree_within_12pct"])
    return {"_doc": "Our pooled primary estimate vs the published comparator meta's reported pooled estimate, "
                    "same question. Pooled-level external agreement (not per-trial). Divergences (|log|>=0.12) "
                    "adjudicated: overwhelmingly our smaller-k / single-trial pools or scale/scope mismatches, "
                    "not extraction errors.",
            "n_topics": n, "agree_within_12pct": agree, "rows": rows}


if __name__ == "__main__":
    d = build()
    json.dump(d, open(os.path.join(ROOT, "docs", "external_agreement.json"), "w", encoding="utf-8"), indent=1)
    print(f"pooled external agreement: {d['agree_within_12pct']}/{d['n_topics']} within ~12% (log) of the published meta")
    for x in d["rows"]:
        if not x["agree_within_12pct"]:
            print(f"  DIVERGE {x['slug']}: ours {x['our_estimate']}{x['our_scale']} vs theirs "
                  f"{x['their_estimate']}{x['their_scale']} -- {x['adjudication'][:70]}")
