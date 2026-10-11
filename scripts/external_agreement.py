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
# A note judges ONE version of the row (A6, lc lane 11 Oct): it carries no numbers -- the row's own values are printed
# beside it -- and records the served (k, estimate, scale) it was written for, as the note's own text stated them. When
# the served row has moved, the note is WITHHELD and the row says it needs re-adjudication (the notes had gone stale:
# 'We are k=1 (Vandermolen OR 8.25)' beside a served k=3 pool at OR 2.07). None = the note did not state that value.
ADJUDICATION = {
    "colchicine-postop-af": {
        "note": "Different trial set: our pool includes null low-dose trials; the comparator pools a different, "
                "more-positive set. Same direction (protective).",
        "written_for": {"k": 5, "estimate": None, "scale": "RR"}},
    "colchicine-recurrent-pericarditis": {
        "note": "Same direction. Our k is smaller (strict double-blind + recurrence-definition).",
        "written_for": {"k": None, "estimate": 0.47, "scale": "RR"}},
    "corticosteroids-cap-mortality": {
        "note": "We pool a single trial (CAPE COD); the comparator pools several. Single-trial vs pool -- our smaller "
                "evidence base, not an extraction error.",
        "written_for": {"k": 1, "estimate": 0.53, "scale": "RR"}},
    "corticosteroids-covid19-mortality": {
        "note": "Scale/set mismatch: our RECOVERY-only rate ratio vs the comparator's pooled REACT odds ratio. "
                "Different estimand and trial set.",
        "written_for": {"k": 1, "estimate": 0.83, "scale": "RR"}},
    "esketamine-trd-madrs": {
        "note": "NOT COMPARABLE: our outcome is MADRS change (a mean difference); the comparator's is response RATE "
                "(a risk ratio). Different outcome/scale.",
        "written_for": {"k": None, "estimate": -4.07, "scale": "MD"}},
    "metformin-pcos-ovulation": {
        "note": "We pool a single trial (Vandermolen, an outlier-high single trial); the Cochrane review pools many. "
                "The Cochrane pool is the reliable value -- our single trial is a small-evidence artefact, exactly "
                "what the larger-evidence-base expansion tier targets. The per-trial Cochrane head-to-head examines "
                "this directly.",
        "written_for": {"k": 1, "estimate": 8.25, "scale": "OR"}},
    "statins-primary-prevention-elderly": {
        "note": "We pool a single pre-specified elderly subgroup; the comparator pools more. Single-subgroup vs pool.",
        "written_for": {"k": 1, "estimate": 0.61, "scale": "HR"}},
}


def _adjudication(slug, ours, osc, k):
    """(note, status, detail) for the served row: the note only while the row is the version it judged."""
    a = ADJUDICATION.get(slug)
    if not a:
        return "", "NONE", ""
    w = a["written_for"]
    moved = []
    if w.get("k") is not None and w["k"] != k:
        moved.append(f"k={w['k']} -> k={k}")
    if w.get("estimate") is not None and (ours is None or round(float(ours), 2) != round(float(w["estimate"]), 2)):
        moved.append(f"estimate {w['estimate']} -> {ours}")
    if w.get("scale") and (osc or "").upper() != w["scale"].upper():
        moved.append(f"scale {w['scale']} -> {osc}")
    if moved:
        return "", "STALE_REQUIRES_READJUDICATION", ("note written for a different served row (" + "; ".join(moved)
                                                     + "); withheld until re-adjudicated")
    return a["note"], "CURRENT", ""


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
                              prel.get("relation"), prel.get("label"), k=res.get("k")))
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


def _classify(slug, ours, osc, theirs, tsc, their_outcome, relation=None, relation_label=None, k=None):
    o = (osc or "").upper()
    t = (tsc or "").upper()
    row = {"slug": slug, "our_estimate": ours, "our_scale": osc,
           "their_estimate": theirs, "their_scale": tsc, "their_outcome": their_outcome,
           "log_ratio_diff": None, "agree_within_12pct": False,
           "k": k,
           "parity_relation": relation, "parity_relation_label": relation_label}
    row["adjudication"], row["adjudication_status"], row["adjudication_stale_detail"] = _adjudication(slug, ours, osc, k)

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
