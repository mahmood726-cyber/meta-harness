"""Acquire a SIGNED replacement comparator's own records into cache/<slug>/records.json (V8 applied, 7 Oct).

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
and keeps the replaced comparator's identity under comparator_replaced {pmid, oa, fulltext_sha256}. The search's own
record set ('records') is NOT touched: the comparator is not a search result. Refuses unless the switch is signed.

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


def _style(p):
    """The file's own JSON style (indent, ascii escaping, separators, trailing newline), found by re-serialising it: the
    rewrite changes only the comparator fields, never 60k lines of formatting."""
    raw = open(p, encoding="utf-8").read()
    obj = json.loads(raw)
    body, tail = (raw[:-1], "\n") if raw.endswith("\n") else (raw, "")
    for indent in (1, 2, None, 4):
        for asc in (False, True):
            for seps in ((", ", ": "), (",", ": "), (",", ":")):
                kw = {"indent": indent, "ensure_ascii": asc, "separators": seps}
                if json.dumps(obj, **kw) == body:
                    return {"kw": kw, "tail": tail}
    raise SystemExit(f"REFUSED: {p} is in no JSON style this writer can reproduce; not rewritten")


def acquire(slug, write=False):
    from harness import fetch, http
    from harness import served_comparator as sc
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    served = str(sc.served_config(slug, cfg).get("comparator_pmid") or "")
    adopted = str(cfg.get("comparator_pmid") or "")
    if served != adopted:
        raise SystemExit(f"REFUSED {slug}: the switch to {adopted} is not signed (served comparator is {served})")
    p = os.path.join(ROOT, "cache", slug, "records.json")
    d = json.load(open(p, encoding="utf-8"))
    held = str(d.get("comparator_pmid") or "")
    if held == served and str((d.get("comparator_record") or {}).get("id") or "") in ("", served):
        if any(str(r.get("id")) == served for r in d.get("records") or []) or d.get("comparator_record"):
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
        d["comparator_replaced"] = {"pmid": held, "oa": d.get("comparator_oa"),
                                    "fulltext_sha256": hashlib.sha256(old_ft.encode("utf-8")).hexdigest(),
                                    "replaced_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "by": "scripts/acquire_comparator_record.py (signed switch, packet V8)"}
        d["comparator_record"] = rec
        d["comparator_pmid"] = served
        d["comparator_oa"] = oa
        d["comparator_fulltext"] = ft
        d["comparator_acquired_utc"] = d["comparator_replaced"]["replaced_utc"]
        style = _style(p)
        text = json.dumps(d, **style["kw"]) + style["tail"]
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return out


def main(argv):
    write = "--write" in argv
    for s in [a for a in argv if not a.startswith("--")]:
        print(json.dumps(acquire(s, write), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
