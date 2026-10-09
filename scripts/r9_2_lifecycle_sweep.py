"""R9-2 sweep: every served review's completeness_state annotation (docs/reviews/<slug>/review.json) against the state
the corrected lifecycle rule (harness.pipeline._completeness_for_record) gives for the same record and the topic's
cached AACT study dates. Read-only: nothing is regenerated here (the captain regenerates); the count per topic says
what the regeneration will change on the pages.

    python scripts/r9_2_lifecycle_sweep.py   -> outputs/k_gap/g1_binding/r9_2_lifecycle_sweep.json
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "r9_2_lifecycle_sweep.json")


def old_state(rec, dates, screen):
    """main@beb73a487's rule, verbatim in effect: SUSPENDED / UNKNOWN counted as completed, any PMID record completed
    with results. Kept ONLY to attribute: old rule v new rule on the same inputs is what R9-2 changes; served v new
    also includes drift between the served pages and the current inputs."""
    nct = screen._nct_id(rec or {})
    d = dates.get(nct or "") if nct else {}
    status = str((d or {}).get("overall_status") or (rec or {}).get("overall_status") or (rec or {}).get("status") or "").upper()
    has_results = bool((rec or {}).get("has_results") or (d or {}).get("results_first_posted_date"))
    if status in {"NOT_YET_RECRUITING"}:
        return "eligible+not_yet_recruiting"
    if status in {"RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION", "APPROVED_FOR_MARKETING"}:
        return "eligible+ongoing"
    if (rec or {}).get("id_type") == "pmid" or status in {"COMPLETED", "TERMINATED", "WITHDRAWN", "SUSPENDED", "UNKNOWN"} \
            or has_results:
        return "eligible+completed+results_available" if (has_results or (rec or {}).get("id_type") == "pmid") \
            else "eligible+completed+results_unavailable"
    return "eligible+completed+results_unavailable"


def main():
    from harness import aact_cache, pipeline, screen
    res, total, by_rule = {}, Counter(), Counter()
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        cp = os.path.join(ROOT, "cache", slug, "records.json")
        if not (os.path.exists(rp) and os.path.exists(cp)):
            continue
        review = json.load(open(rp, encoding="utf-8"))
        recs = {pipeline._clean_record_id(r.get("id")): r for r in pipeline._dedup(json.load(open(cp, encoding="utf-8")))}
        try:
            dates = (aact_cache.load(slug) or {}).get("values", {}).get("study_dates", {})
        except Exception:  # noqa: BLE001 - no cache: the record's own fields only, recorded
            dates = {}
        # only the pipeline's own lifecycle vocabulary: a topic-config label ('target outcome absent by design ...',
        # screen_entry.completeness_state) is set first and never overridden by the pipeline (setdefault)
        own = lambda r: str(r.get("completeness_state") or "").startswith("eligible+")  # noqa: E731
        rows = [r for r in (review.get("screening") or {}).get("records") or [] if own(r)]
        for o in review.get("outcomes") or []:
            rows += [r for r in o.get("declared_absent_trials") or [] if own(r)]
        changes, rule = [], []
        for r in rows:
            rec = recs.get(pipeline._clean_record_id(r.get("id")))
            if not rec:
                continue
            new = pipeline._completeness_for_record(rec, dates)["completeness_state"]
            old = old_state(rec, dates, screen)
            if new != r["completeness_state"]:
                changes.append({"id": r.get("id"), "served": r["completeness_state"], "corrected": new,
                                "cause": "R9-2_RULE" if old != new else "SERVED_PAGE_DRIFT (the old rule gives this too)"})
            if old != new:
                rule.append((old, new))
        by_rule.update(f"{a} -> {b}" for a, b in rule)
        c = Counter((x["served"], x["corrected"]) for x in changes)
        res[slug] = {"annotated": len(rows), "changed": len(changes), "changed_by_r9_2_rule": len(rule),
                     "by_transition": {f"{a} -> {b}": n for (a, b), n in sorted(c.items())}, "rows": changes}
        total.update({f"{a} -> {b}": n for (a, b), n in c.items()})
    out = {"topics": res, "total_changed": sum(t["changed"] for t in res.values()),
           "changed_by_r9_2_rule": sum(t["changed_by_r9_2_rule"] for t in res.values()), "by_rule_transition": dict(by_rule),
           "topics_changed": sum(1 for t in res.values() if t["changed"]), "by_transition": dict(total)}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("total_changed", "topics_changed", "by_transition", "changed_by_r9_2_rule",
                                          "by_rule_transition")}, indent=1))
    print({s: t["changed"] for s, t in res.items() if t["changed"]})


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
