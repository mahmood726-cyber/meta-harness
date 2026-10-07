"""Acquire a SIGNED replacement comparator's own records into cache/<slug>/comparator_records.json (V8 applied, 7 Oct).

The comparator switches changed topics/<slug>.json comparator_pmid and cache/<slug>/comparators.json, but the topic's
held records still carried the OLD comparator's full text and Unpaywall status, and four of the five new comparators had
no PubMed record held. The served pages then named the new comparator with pmid null and read its 'reported' numbers from
the old comparator's text (harness.pipeline.comparator_records_problem now refuses that build).

For each slug whose SERVED comparator (harness.served_comparator.served_config: only a signed switch moves it) differs
from the held one, this writes, with the same code paths the full fetch uses (harness.fetch):
  comparator_record     the comparator's PubMed record (efetch: title, abstract, year, journal, doi, pubtypes)
  comparator_pmid       the served comparator's PMID
  comparator_oa         Unpaywall status of its DOI
  comparator_fulltext   its PMC open full text ('' when PMC holds none)
into cache/<slug>/comparator_records.json (harness.fetch.ensure overlays it on records.json), and keeps the replaced
comparator's identity under comparator_replaced {pmid, oa, fulltext_sha256}. records.json, the search cache, is never
rewritten: other evidence digests it. Refuses unless the switch is signed.

    python scripts/acquire_comparator_record.py [--write] SLUG...
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def acquire(slug, write=False):
    from harness import fetch, http
    from harness import served_comparator as sc
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    served = str(sc.served_config(slug, cfg).get("comparator_pmid") or "")
    adopted = str(cfg.get("comparator_pmid") or "")
    if served != adopted:
        raise SystemExit(f"REFUSED {slug}: the switch to {adopted} is not signed (served comparator is {served})")
    # held = what the pipeline will see: records.json with any comparator_records.json overlay (harness.fetch)
    cache_dir = os.path.join(ROOT, "cache", slug)
    d = fetch._with_comparator_records(json.load(open(os.path.join(cache_dir, "records.json"), encoding="utf-8")),
                                       cfg, cache_dir)
    held = str(d.get("comparator_pmid") or "")
    # already held only when the held record really IS this comparator's (codex v8-apply-r8 #3: a record with no id passed
    # this shortcut while the build guard refused the same cache)
    held_rec = (str((d.get("comparator_record") or {}).get("id") or "") == served
                or any(str(r.get("id")) == served for r in d.get("records") or []))
    if held == served and held_rec:
        return {"slug": slug, "state": "ALREADY_HELD", "pmid": served}
    recs = fetch._efetch([served])
    rec = next((r for r in recs if str(r.get("id")) == served), None)
    if not rec or not rec.get("title"):
        raise SystemExit(f"REFUSED {slug}: PubMed returned no record for {served}")
    oa = None
    if rec.get("doi"):
        try:
            u = http.get_json(f"https://api.unpaywall.org/v2/{rec['doi']}", {"email": "meta-harness@example.org"})
            loc = u.get("best_oa_location") or {}
            oa = {"is_oa": bool(u.get("is_oa")), "oa_url": loc.get("url", "")}
        except Exception as exc:  # noqa: BLE001 - recorded, as the full fetch records it
            oa = {"is_oa": None, "error": str(exc)[:200]}
    ft = fetch._pmc_fulltext(served)
    old_ft = d.get("comparator_fulltext") or ""
    out = {"slug": slug, "state": "ACQUIRED", "pmid": served, "replaced": held, "title": rec["title"][:120],
           "oa": oa, "fulltext_chars": len(ft), "fulltext_sha256": hashlib.sha256(ft.encode("utf-8")).hexdigest()}
    if write:
        when = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cr = {"_doc": ("The SIGNED replacement comparator's own records, acquired by scripts/acquire_comparator_record.py "
                       "through harness.fetch's code paths; harness.fetch.ensure overlays them on records.json when this "
                       "file names the configured comparator. records.json (the search cache) is never rewritten."),
              "comparator_pmid": served, "comparator_record": rec, "comparator_oa": oa, "comparator_fulltext": ft,
              "comparator_replaced": {"pmid": held, "oa": d.get("comparator_oa"),
                                      "fulltext_sha256": hashlib.sha256(old_ft.encode("utf-8")).hexdigest(),
                                      "replaced_utc": when,
                                      "by": "scripts/acquire_comparator_record.py (signed switch, packet V8)"},
              "comparator_acquired_utc": when}
        with open(os.path.join(cache_dir, fetch.COMPARATOR_RECORDS), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cr, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return out


def main(argv):
    write = "--write" in argv
    for s in [a for a in argv if not a.startswith("--")]:
        print(json.dumps(acquire(s, write), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
