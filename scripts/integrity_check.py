"""Run the trial-integrity (retraction / expression-of-concern) check for every live topic's POOLED
trials and write cache/<slug>/integrity.json (committed, replayed offline, gated). Measure-time only.

    python scripts/integrity_check.py [<slug> ...]   # default: all live topics
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import integrity  # noqa: E402
from harness import aact  # noqa: E402


def pooled_pmids(slug):
    rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if not os.path.exists(rp):
        return []
    rev = json.load(open(rp, encoding="utf-8"))
    pmids = set()
    for o in rev.get("outcomes", []):
        for t in o.get("trials", []) or []:
            p = str(t.get("id", "")).replace("PMID ", "")
            if p.isdigit():
                pmids.add(p)
    return sorted(pmids)


def _pmid_to_nct(slug):
    cp = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(cp):
        return {}
    recs = json.load(open(cp, encoding="utf-8")).get("records", [])
    return {str(r.get("id")): r.get("nct") for r in recs if r.get("nct")}


def _prospective(pmids, slug, dates):
    """Per pooled trial with an NCT: was it registered BEFORE enrolment started? Retrospective
    registration is a documented reporting-bias signal. `dates` is a pre-fetched AACT study_dates map
    (one pass for all topics). None = undeterminable (missing dates or no NCT)."""
    p2n = _pmid_to_nct(slug)
    out = {}
    for p in pmids:
        nct = p2n.get(p)
        d = dates.get((nct or "").upper()) if nct else None
        reg = (d or {}).get("study_first_submitted_date")
        start = (d or {}).get("start_date")
        prospective = None
        if reg and start and len(reg) >= 7 and len(start) >= 7:
            prospective = reg[:7] <= start[:7]  # registered no later than the enrolment-start month
        out[p] = {"nct": nct, "registered": reg, "start": start, "prospective": prospective}
    return out


def main(argv):
    slugs = argv or [s for s in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
                     if os.path.exists(os.path.join(ROOT, "docs", "reviews", s, "review.json"))]
    # ONE AACT pass for every pooled trial's NCT across all topics (studies.txt is 400MB+).
    all_ncts = set()
    for slug in slugs:
        p2n = _pmid_to_nct(slug)
        for p in pooled_pmids(slug):
            if p2n.get(p):
                all_ncts.add(p2n[p])
    all_dates = aact.study_dates(all_ncts) if (aact.snapshot_dir() and all_ncts) else {}
    for slug in slugs:
        pmids = pooled_pmids(slug)
        if not pmids:
            continue
        try:
            status = integrity.retraction_status(pmids)
        except Exception as exc:  # noqa: BLE001 - a check that cannot run must not pass silently
            print(f"{slug}: RETRACTION CHECK FAILED ({exc}) — not writing", file=sys.stderr)
            continue
        retracted = [p for p in pmids if status.get(p, {}).get("retracted")]
        concern = [p for p in pmids if status.get(p, {}).get("concern")]
        prospective = _prospective(pmids, slug, all_dates) if all_dates else {}
        retro = [p for p in prospective if prospective[p].get("prospective") is False]
        out = {"checked_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "source": "PubMed efetch (PublicationType + CommentsCorrections)",
               "n_pooled": len(pmids), "retracted": retracted, "concern": concern,
               "retrospectively_registered": retro, "prospective": prospective,
               "per_pmid": status}
        json.dump(out, open(os.path.join(ROOT, "cache", slug, "integrity.json"), "w",
                            encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
        flag = f" RETRACTED={retracted}" if retracted else ""
        flag += f" CONCERN={concern}" if concern else ""
        flag += f" RETRO-REG={retro}" if retro else ""
        print(f"{slug}: {len(pmids)} pooled checked{flag or ' — clean'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
