"""External-standard agreement (VALIDATION, the weak side): compare our pooled PRIMARY estimate to the
PUBLISHED comparator meta-analysis's own reported pooled estimate on the same question. This is our
synthesis vs an external hand-built synthesis -- the closest pooled-level ground truth we hold for every
topic (the per-trial Cochrane head-to-head, scripts feeding docs/cochrane_headtohead.json, is the deeper
check where a review tabulates per-trial data). Object-derived from review.json (comparator.reported)."""
import glob
import json
import math
import os
import sys

sys.path.insert(0, ROOT := os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import parity_relation  # noqa: E402

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
        prow = parity_relation.load_parity_row(ROOT, slug)
        prel = parity_relation.compute(prow, r) if prow else {}
        rows.append(_classify(slug, ours, osc, theirs, tsc, rep.get("outcome"),
                              prel.get("relation"), prel.get("label")))
    n = len(rows)
    same_agree = sum(1 for x in rows if x["category"] == "same_estimand_agree")
    same_replication = sum(1 for x in rows if x["category"] == "same_estimand_replication")
    same_diverge = sum(1 for x in rows if x["category"] == "same_estimand_diverge")
    cross_pending = sum(1 for x in rows if x["category"] == "cross_estimand_pending")
    cross_opp = sum(1 for x in rows if x["category"] == "cross_estimand_opposite")
    noncomp = sum(1 for x in rows if x["category"] == "non_comparable")
    return {"_doc": "Our pooled primary estimate vs the published comparator meta's reported pooled estimate. "
                    "COMPARATOR_RESULT_CONTEXT_MISMATCH rebuild: a 'same-question agreement' is asserted ONLY "
                    "when the two estimates share the SAME estimand (scale) — comparing an RR to an OR or an HR "
                    "on the log scale is comparing different quantities (OR is further from 1 for common events; "
                    "HR is a rate, RR a risk), so a cross-estimand match is NOT a same-question agreement and its "
                    "'agrees' claim is SUPPRESSED until a scale-matched conversion is verified with the "
                    "comparator's event rate. Cross-estimand pairs are still shown with their direction "
                    "consistency (a weaker, honest signal). IDENTICAL_SET comparisons are arithmetic "
                    "replication, not independent corroboration, so their 'agrees' claim is suppressed. "
                    "Pooled-level only (not per-trial).",
            "n_topics": n,
            "same_estimand_agree": same_agree, "same_estimand_replication": same_replication,
            "same_estimand_diverge": same_diverge,
            "cross_estimand_pending": cross_pending, "cross_estimand_opposite": cross_opp,
            "non_comparable": noncomp,
            # back-compat field: same-question agreement is now ONLY the same-estimand agreements
            "agree_within_12pct": same_agree,
            "rows": rows}


# The estimand KEY: an agreement is "the same question" only when the two effect measures are the same
# quantity. Ratios of different kinds (RR/OR/HR/IRR) are NOT interchangeable in general; a MIXED pool on
# our side has no single estimand to match. Cross-estimand pairs are classified by DIRECTION only.
_RATIO = {"RR", "OR", "HR", "IRR", "RATE_RATIO"}


def _classify(slug, ours, osc, theirs, tsc, their_outcome, relation=None, relation_label=None):
    o = (osc or "").upper()
    t = (tsc or "").upper()
    row = {"slug": slug, "our_estimate": ours, "our_scale": osc,
           "their_estimate": theirs, "their_scale": tsc, "their_outcome": their_outcome,
           "log_ratio_diff": None, "agree_within_12pct": False,
           "adjudication": ADJUDICATION.get(slug, ""),
           "parity_relation": relation, "parity_relation_label": relation_label}
    def _stamp_relation():
        if relation == "IDENTICAL_SET":
            row.setdefault("agreement_basis", "arithmetic_replication")
            row.setdefault(
                "replication_note",
                relation_label or
                "arithmetic replication -- same trials; agreement is not independent corroboration")
        return row

    # a continuous vs ratio (or any non-ratio) comparison is not comparable at all
    if o not in _RATIO or t not in _RATIO:
        row["category"] = "non_comparable"
        row["same_question"] = False
        return _stamp_relation()
    try:
        logdiff = abs(math.log(ours) - math.log(theirs))
    except (ValueError, TypeError):
        row["category"] = "non_comparable"
        row["same_question"] = False
        return _stamp_relation()
    row["log_ratio_diff"] = round(logdiff, 3)
    try:
        row["direction_consistent"] = (ours < 1.0) == (theirs < 1.0)
    except TypeError:
        row["direction_consistent"] = None
    if o == t:
        # SAME estimand: a genuine same-question comparison.
        if logdiff < 0.12:
            if relation == "IDENTICAL_SET":
                row["category"] = "same_estimand_replication"
                row["agreement_basis"] = "arithmetic_replication"
                row["replication_note"] = (
                    relation_label or
                    "arithmetic replication -- same trials; agreement is not independent corroboration")
            else:
                row["category"] = "same_estimand_agree"
                row["agree_within_12pct"] = True
            row["same_question"] = True
        else:
            row["category"] = "same_estimand_diverge"
            row["same_question"] = True
    else:
        # CROSS estimand: the 'same question' / 'agrees' claim is SUPPRESSED (pending a scale-matched,
        # event-rate-justified conversion). We keep only the direction-consistency signal.
        row["same_question"] = False
        row["category"] = "cross_estimand_pending" if row.get("direction_consistent") else "cross_estimand_opposite"
        row["cross_estimand_note"] = (f"scale differs (ours {o} vs theirs {t}); a same-question agreement is not "
                                      f"asserted — HR/RR/OR are not interchangeable without an event-rate-justified "
                                      f"conversion. Direction is "
                                      + ("consistent" if row.get("direction_consistent") else "OPPOSITE") + ".")
    return _stamp_relation()


if __name__ == "__main__":
    d = build()
    json.dump(d, open(os.path.join(ROOT, "docs", "external_agreement.json"), "w", encoding="utf-8"), indent=1)
    print(f"same-ESTIMAND agreement (different evidence base only): {d['same_estimand_agree']}/{d['n_topics']}")
    print(f"  same-estimand arithmetic replication: {d['same_estimand_replication']}")
    print(f"  same-estimand diverge: {d['same_estimand_diverge']}; cross-estimand pending (suppressed): "
          f"{d['cross_estimand_pending']}; cross-estimand opposite: {d['cross_estimand_opposite']}; "
          f"non-comparable: {d['non_comparable']}")
    for x in d["rows"]:
        if x["category"].startswith("cross_estimand"):
            print(f"  CROSS {x['slug']}: ours {x['our_estimate']}{x['our_scale']} vs theirs "
                  f"{x['their_estimate']}{x['their_scale']} -- same-question SUPPRESSED (scale differs)")
