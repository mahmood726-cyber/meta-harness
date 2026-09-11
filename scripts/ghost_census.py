"""GHOST-PROTOCOL census — direct publication-bias measurement from the local AACT snapshot.

Registry enumeration gives every REGISTERED trial for a PICO; publication resolution says which ever
produced a paper. The difference is completed-but-unpublished trials — the missing evidence measured
directly, not inferred from funnel asymmetry. Four states per enumerated interventional trial:

  published            - has an own-publication PMID (study_references RESULT/DERIVED)
  results_only         - CT.gov results posted but no publication -> DATA WE CAN POOL (in AACT), that
                         no published meta in the topic has
  ghost                - completed >=12 months before the snapshot, no results posted, no publication
  ongoing_or_recent    - not yet completed, or completed <12 months ago (too soon to call)

HONESTY (per the mandate): a ghost is a NON-PUBLICATION candidate AND a linkage-failure candidate --
a trial can be published under a title our NCT->PMID linkage missed. So the ghost count is an UPPER
BOUND, labelled as such, with the linkage method named. We do NOT turn a resolution failure into a
publication-bias claim. Writes cache/<slug>/ghost.json (committed, rendered).

    python scripts/ghost_census.py [--write]
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact  # noqa: E402

INTERVENTIONAL_STATUSES_DONE = ("COMPLETED", "TERMINATED")


def _year_month(s):
    # AACT dates are 'YYYY-MM-DD' or 'YYYY-MM' or ''.
    if not s or len(s) < 7:
        return None
    try:
        return int(s[:4]) * 12 + int(s[5:7])
    except ValueError:
        return None


def main(argv):
    snap = aact.snapshot_dir()
    if not snap:
        print("AACT snapshot not found"); return 2
    snap_name = os.path.basename(snap)
    # snapshot data-month as the reference "now" (folder overstates; use the tables' own recency proxy)
    now_ym = _year_month(snap_name)

    topics = []
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        if not os.path.exists(os.path.join(ROOT, "docs", "reviews", slug, "review.json")):
            continue
        cfg = json.load(open(os.path.join(ROOT, "topics", f), encoding="utf-8"))
        rf = cfg.get("registry_first") or {}
        if not (rf.get("cond") or rf.get("intr")):
            continue
        inc = cfg.get("include", {})
        cond_terms = [t.lower() for t in ([rf.get("cond", "")] + (inc.get("population_any") or [])) if t]
        intr_terms = [t.lower() for t in ([rf.get("intr", "")] + (inc.get("intervention_any") or [])
                      + (cfg.get("intervention_terms") or [])) if t]
        topics.append((slug, sorted(set(cond_terms)), sorted(set(intr_terms))))

    # enumerate (2 passes)
    cond_sets = {s: set() for s, *_ in topics}
    intr_sets = {s: set() for s, *_ in topics}
    for r in aact._iter_rows(aact._table("conditions")):
        dn = r.get("downcase_name") or ""
        nct = (r.get("nct_id") or "").upper()
        for s, ct, it in topics:
            if any(c in dn for c in ct):
                cond_sets[s].add(nct)
    for r in aact._iter_rows(aact._table("interventions")):
        nm = (r.get("name") or "").lower()
        nct = (r.get("nct_id") or "").upper()
        for s, ct, it in topics:
            if any(i in nm for i in it):
                intr_sets[s].add(nct)
    enum = {s: (cond_sets[s] & intr_sets[s]) for s, *_ in topics}
    all_ncts = set().union(*enum.values()) if enum else set()

    # studies pass: status + completion + results-posted for enumerated NCTs
    dates = {n: {} for n in all_ncts}
    for r in aact._iter_rows(aact._table("studies")):
        nct = (r.get("nct_id") or "").upper()
        if nct in all_ncts:
            dates[nct] = {"status": (r.get("overall_status") or "").upper(),
                          "completion": r.get("completion_date") or r.get("primary_completion_date"),
                          "results_posted": r.get("results_first_posted_date"),
                          "study_type": (r.get("study_type") or "").upper()}
    # references pass: own-publication linkage
    pubs = {n: False for n in all_ncts}
    for r in aact._iter_rows(aact._table("study_references")):
        nct = (r.get("nct_id") or "").upper()
        if nct in all_ncts and (r.get("reference_type") or "").upper() in aact.OWN_PUB_TYPES:
            if (r.get("pmid") or "").strip().isdigit():
                pubs[nct] = True

    print(f"{'topic':42} {'enum':5} {'pub':4} {'res-only':8} {'ghost':6} (AACT {snap_name})")
    for s, ct, it in topics:
        ncts = enum[s]
        published = results_only = ghost = ongoing = 0
        ghost_list, res_list = [], []
        for n in ncts:
            d = dates.get(n, {})
            has_pub = pubs.get(n, False)
            has_res = bool(d.get("results_posted"))
            done = d.get("status") in INTERVENTIONAL_STATUSES_DONE
            comp_ym = _year_month(d.get("completion"))
            old = (now_ym and comp_ym and (now_ym - comp_ym) >= 12)
            if has_pub:
                published += 1
            elif has_res:
                results_only += 1; res_list.append(n)
            elif done and old:
                ghost += 1; ghost_list.append(n)
            else:
                ongoing += 1
        print(f"{s:42} {len(ncts):<5} {published:<4} {results_only:<8} {ghost:<6}")
        if "--write" in argv:
            out = {"source": f"AACT {snap_name} (local snapshot)",
                   "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "enumerated": len(ncts), "published": published, "results_only": results_only,
                   "ghost_upper_bound": ghost, "ongoing_or_recent": ongoing,
                   "results_only_ncts": sorted(res_list)[:50], "ghost_ncts": sorted(ghost_list)[:50],
                   "caveat": ("ghost = completed >=12mo before snapshot with no CT.gov results and no "
                              "linked publication; an UPPER BOUND (a paper under a title our NCT->PMID "
                              "linkage missed reads as ghost). Linkage = AACT study_references RESULT/DERIVED.")}
            json.dump(out, open(os.path.join(ROOT, "cache", s, "ghost.json"), "w",
                                encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
    if "--write" in argv:
        print("\nwrote cache/<slug>/ghost.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
