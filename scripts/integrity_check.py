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


def main(argv):
    slugs = argv or [s for s in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
                     if os.path.exists(os.path.join(ROOT, "docs", "reviews", s, "review.json"))]
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
        out = {"checked_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "source": "PubMed efetch (PublicationType + CommentsCorrections)",
               "n_pooled": len(pmids), "retracted": retracted, "concern": concern,
               "per_pmid": status}
        json.dump(out, open(os.path.join(ROOT, "cache", slug, "integrity.json"), "w",
                            encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
        flag = f" RETRACTED={retracted}" if retracted else ""
        flag += f" CONCERN={concern}" if concern else ""
        print(f"{slug}: {len(pmids)} pooled checked{flag or ' — clean'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
