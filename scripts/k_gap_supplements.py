"""Fetch every comparator's supplementary files (Europe PMC supplementaryFiles ZIP) and extract TYPED text.

Per topic: the supplement filenames come from the comparator's own cached JATS (<supplementary-material xlink:href>),
the PMCID from the cached idconv record. Text is cached at cache/comparators/<pmid>/<date>_kgap_supplements.txt with
the ZIP's sha256 recorded in outputs/k_gap/comparator_supplements.json. No OCR: images are listed and skipped, and a
legacy binary .doc is listed as unparsed. A number never comes from a model.

Usage: python scripts/k_gap_supplements.py [--offline] [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402

XLINK = "{http://www.w3.org/1999/xlink}href"
OUT = os.path.join(ROOT, "outputs", "k_gap", "comparator_supplements.json")


def comparator_pmid(slug: str) -> str:
    with open(os.path.join(ROOT, "cache", slug, "comparators.json"), encoding="utf-8") as fh:
        c = json.load(fh)[0]
    m = re.search(r"PMID (\d+)", c.get("citation", ""))
    return m.group(1) if m else str(c["id"])


def pmcid_of(pmid: str) -> str:
    for f in sorted(glob.glob(os.path.join(k_gap.COMP_DIR, pmid, "*idconv.json"))):
        with open(f, encoding="utf-8") as fh:
            m = re.search(r'"pmcid"\s*:\s*"(PMC\d+)"', fh.read())
        if m:
            return m.group(1)
    return ""


def supplement_hrefs(pmid: str, jats_date: str) -> list:
    p = os.path.join(k_gap.COMP_DIR, pmid, f"{jats_date}_kgap_jats.xml")
    if not os.path.exists(p):
        return []
    root = ET.parse(p).getroot()
    out = []
    for el in root.iter():
        if el.tag in ("supplementary-material", "media") and el.get(XLINK):
            out.append(el.get(XLINK))
    return list(dict.fromkeys(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--date", default="2026-09-29")
    ap.add_argument("--jats-date", default="2026-09-28")
    ap.add_argument("--pause", type=float, default=20.0, help="seconds between live fetches (EPMC throttles)")
    a = ap.parse_args()
    with open(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"), encoding="utf-8") as fh:
        slugs = [t["slug"] for t in json.load(fh)["topics"]]
    topics, tally = {}, {}
    for slug in slugs:
        pmid = comparator_pmid(slug)
        pmcid = pmcid_of(pmid)
        hrefs = supplement_hrefs(pmid, a.jats_date)
        r = k_gap.comparator_supplements(pmid, pmcid, hrefs, a.date, offline=a.offline)
        row = {"pmid": pmid, "pmcid": pmcid, "listed": [h.rsplit("/", 1)[-1] for h in hrefs], "state": r["state"],
               "text_chars": len(r.get("text") or ""), "text_sha256": r.get("sha256")}
        for k in ("route", "zip_sha256", "files", "error", "http_status", "head"):
            if k in r:
                row[k] = r[k]
        topics[slug] = row
        tally[r["state"]] = tally.get(r["state"], 0) + 1
        if r["state"] not in ("CACHED", "NO_SUPPLEMENTS", "NOT_CACHED_OFFLINE"):
            time.sleep(a.pause)
        print(f"{slug:44s} {r['state']:24s} chars={row['text_chars']}", flush=True)
    prev = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            prev = json.load(fh)
    routes = prev.get("_routes", {})
    routes["europepmc_supplementaryFiles"] = (f"{a.date}: HTTP 200 application/zip for OA articles (earlier 503 was "
                                              "transient); the primary route")
    doc = {"_routes": routes, "date": a.date, "tally": tally, "n_topics": len(slugs), "topics": topics}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    print("TALLY", json.dumps(tally), f"of {len(slugs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
