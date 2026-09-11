"""Compute registry-first RECALL for EVERY topic locally from the AACT snapshot, in 3 streaming
passes (conditions, interventions, study_references) instead of rate-limited per-topic CT.gov calls.

For each topic with a committed registry_first{cond,intr}:
  enumerated NCT = {conditions.downcase_name contains cond} INTERSECT {interventions.name contains intr}
  resolved PMID = study_references(RESULT|DERIVED) for those NCTs
  recall        = |known ∩ resolved| / |known|,  known = pooled trials UNION positive controls
Writes cache/<slug>/recall.json (committed, rendered on the page). Records the AACT snapshot for
provenance; regenerable by re-running this against the same snapshot.

    python scripts/recall_aact.py            # all topics with a committed query
    python scripts/recall_aact.py --write     # also write cache/<slug>/recall.json
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact  # noqa: E402


def _known(slug):
    pmids = set()
    tp = os.path.join(ROOT, "topics", slug + ".json")
    cfg = json.load(open(tp, encoding="utf-8"))
    pmids.update(str(p) for p in cfg.get("positive_control_pmids", []))
    rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if os.path.exists(rp):
        rev = json.load(open(rp, encoding="utf-8"))
        for o in rev.get("outcomes", []):
            for t in o.get("trials", []) or []:
                pmids.add(str(t.get("id", "")).replace("PMID ", ""))
    return cfg, {p for p in pmids if p.isdigit()}


def main(argv):
    snap = aact.snapshot_dir()
    if not snap:
        print("AACT snapshot not found (set AACT_DIR)"); return 2
    topics = []
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        if not os.path.exists(os.path.join(ROOT, "docs", "reviews", slug, "review.json")):
            continue
        cfg, known = _known(slug)
        rf = cfg.get("registry_first") or {}
        if rf.get("cond") or rf.get("intr"):
            inc = cfg.get("include", {})
            # OR over the topic's full committed term lists so AACT's specific condition/intervention
            # names (Plasmalyte, Icosapent, ...) match — mirrors the synonym breadth the CT.gov API
            # applies. Lowercased; deduped. These lists are committed, so recall stays reproducible.
            cond_terms = [t.lower() for t in ([rf.get("cond", "")] + (inc.get("population_any") or [])) if t]
            intr_terms = [t.lower() for t in ([rf.get("intr", "")] + (inc.get("intervention_any") or [])
                          + (cfg.get("intervention_terms") or [])) if t]
            topics.append((slug, sorted(set(cond_terms)), sorted(set(intr_terms)), known))
    if not topics:
        print("no topics with a committed registry_first query"); return 0

    # Pass 1 + 2: NCT sets per topic for cond and intr (one stream each).
    cond_sets = {s: set() for s, *_ in topics}
    intr_sets = {s: set() for s, *_ in topics}
    cp = aact._table("conditions")
    for r in aact._iter_rows(cp):
        dn = (r.get("downcase_name") or "")
        nct = (r.get("nct_id") or "").upper()
        for s, cond_terms, intr_terms, _ in topics:
            if any(c in dn for c in cond_terms):
                cond_sets[s].add(nct)
    ip = aact._table("interventions")
    for r in aact._iter_rows(ip):
        nm = (r.get("name") or "").lower()
        nct = (r.get("nct_id") or "").upper()
        for s, cond_terms, intr_terms, _ in topics:
            if any(i in nm for i in intr_terms):
                intr_sets[s].add(nct)
    enum = {s: (cond_sets[s] & intr_sets[s]) for s, *_ in topics}

    # Pass 3: resolve every enumerated NCT (union across topics) to own-publication PMIDs.
    all_ncts = set().union(*enum.values()) if enum else set()
    want = all_ncts
    all_known = set().union(*[k for *_, k in topics]) if topics else set()
    nct_pmids = {n: [] for n in want}
    # Reverse index for every KNOWN pmid: which NCTs cite it, and with what reference_type. This
    # lets a MISSED trial be classified by WHY the registry-first route did not reach it, instead of
    # collapsing three different causes into one scalar. Captured for ALL reference types (a trial's
    # own NCT is by definition NOT in the enumerated set, so we cannot restrict to `want` here).
    known_ref = {p: [] for p in all_known}
    sp = aact._table("study_references")
    for r in aact._iter_rows(sp):
        nct = (r.get("nct_id") or "").upper()
        typ = (r.get("reference_type") or "").upper()
        pmid = (r.get("pmid") or "").strip()
        if nct in want and typ in aact.OWN_PUB_TYPES and pmid.isdigit():
            nct_pmids[nct].append(pmid)
        if pmid in known_ref:
            known_ref[pmid].append((nct, typ))

    snap_name = os.path.basename(snap)
    print(f"{'topic':42} {'enumNCT':8} {'recall':10} recovered/known   (AACT {snap_name})")
    rows = []
    for s, cond, intr, known in topics:
        resolved = set()
        for n in enum[s]:
            resolved.update(nct_pmids.get(n, []))
        found = known & resolved
        rec = round(len(found) / len(known), 3) if known else None
        # Classify each missed trial by the CAUSE of non-recovery (the metric otherwise reads a
        # non-recovery as a search failure even when the trial predates trial registration):
        #   no_registry_link       -> no own-publication (RESULT/DERIVED) NCT anywhere; the trial has
        #                              no registry entry to reach (pre-registration-era/unregistered),
        #                              or is only cited as BACKGROUND by other trials. A registry-first
        #                              search CANNOT recover it — this is a property of the literature.
        #   registered_not_enumerated -> an own-publication NCT exists but the committed cond&intr query
        #                              did not enumerate it (registry vocabulary/precision limit) -> the
        #                              improvable bucket; a broader committed query could reach it.
        missed_reasons = {}
        for p in sorted(known - resolved):
            own_pub = [n for n, t in known_ref.get(p, []) if t in aact.OWN_PUB_TYPES]
            missed_reasons[p] = "registered_not_enumerated" if own_pub else "no_registry_link"
        reachable_ceiling = len(found) + sum(1 for v in missed_reasons.values() if v == "registered_not_enumerated")
        no_link = sum(1 for v in missed_reasons.values() if v == "no_registry_link")
        rows.append((s, cond, intr, known, enum[s], resolved, found, rec))
        print(f"{s:42} {len(enum[s]):<8} {str(rec):10} {len(found)}/{len(known)}"
              + (f"  [ceiling {reachable_ceiling}/{len(known)}, {no_link} unregistered/unlinked]" if (known - resolved) else ""))
        if "--write" in argv:
            out = {"status": "RAN_OK", "source": f"AACT {snap_name} (local snapshot)",
                   "enumerated": len(enum[s]), "known": len(known), "recovered": len(found),
                   "recall": rec, "missed": sorted(known - resolved),
                   "missed_reasons": missed_reasons,
                   "reachable_ceiling": reachable_ceiling, "no_registry_link": no_link,
                   "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            json.dump(out, open(os.path.join(ROOT, "cache", s, "recall.json"), "w",
                                encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
    if "--write" in argv:
        print("\nwrote cache/<slug>/recall.json for", len(rows), "topics")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
