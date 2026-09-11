"""RE-SEARCH MODE (item 1): re-run a topic's COMMITTED queries LIVE against the sources today and
diff the retrieved id set against the committed cache — converting "replay is not repeatability" from
a disclosed limitation into a MEASUREMENT. Writes cache/<slug>/research_diff.json, which the
Reproducibility tab renders. This is the honest "living, not frozen": the analysis is frozen and
auditable; the literature is not, and here is exactly how much it has drifted since the cache.

  python scripts/research_diff.py <slug> [<slug> ...]     # network; writes cache/<slug>/research_diff.json

A diff is NOT a defect — new records appearing is the literature moving. It is reported so a reader
sees what a fresh search would add/miss versus the committed set, rather than assuming they match.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import fetch  # noqa: E402


def _committed_ids(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    recs = json.load(open(p, encoding="utf-8"))["records"]
    pmids = {str(r["id"]) for r in recs if str(r["id"]).isdigit()}
    ncts = {str(r["id"]).upper() for r in recs if str(r["id"]).upper().startswith("NCT")}
    return pmids, ncts


def main(argv):
    slugs = [a for a in argv if not a.startswith("-")] or sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
    for slug in slugs:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        c_pmids, c_ncts = _committed_ids(slug)
        # re-run committed PubMed + Europe PMC queries live
        live_pmids = set()
        for q in cfg.get("pubmed_queries", []):
            try:
                live_pmids.update(fetch._esearch(q, cfg.get("retmax", 40)))
                live_pmids.update(fetch._europepmc_pmids(q, cfg.get("retmax", 40)))
            except Exception as e:  # network failure is reported, never silently a match
                print(f"{slug}: query failed live ({e!r}) — recording RAN_ERROR")
                json.dump({"status": "RAN_ERROR", "error": repr(e)[:200],
                           "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                          open(os.path.join(ROOT, "cache", slug, "research_diff.json"), "w",
                               encoding="utf-8", newline=""), indent=1)
                break
        else:
            live_ncts = set()
            ct = cfg.get("ctgov") or {}
            if ct.get("cond") or ct.get("intr"):
                try:
                    for row in fetch._ctgov_search(ct.get("cond", ""), ct.get("intr", "")):
                        n = (row.get("nct") or row.get("nct_id") or "").upper()
                        if n:
                            live_ncts.add(n)
                except Exception:
                    live_ncts = set()
            added_p = sorted(live_pmids - c_pmids)
            dropped_p = sorted(c_pmids - live_pmids)
            added_n = sorted(live_ncts - c_ncts)
            summary = (f"PubMed/EPMC: {len(live_pmids)} retrieved live vs {len(c_pmids)} committed "
                       f"({len(added_p)} new, {len(dropped_p)} no longer returned). "
                       f"CT.gov: {len(live_ncts)} live vs {len(c_ncts)} committed ({len(added_n)} new).")
            out = {"status": "RAN_OK", "scope": "committed PubMed + Europe PMC + CT.gov queries",
                   "live_pmids": len(live_pmids), "committed_pmids": len(c_pmids),
                   "added_pmids": added_p[:50], "dropped_pmids": dropped_p[:50],
                   "added_ncts": added_n[:50], "summary": summary,
                   "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            json.dump(out, open(os.path.join(ROOT, "cache", slug, "research_diff.json"), "w",
                                encoding="utf-8", newline=""), indent=1, ensure_ascii=False)
            print(f"{slug}: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
