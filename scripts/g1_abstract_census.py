"""ABRIDGED-ABSTRACT CENSUS + RE-ACQUISITION (external audit R6 P1 SOURCE PRESERVATION, PRIORITY 1: the cached 'abstract' of
omarigliptin / OMNeON 28893244 is 1,138 chars and drops HHF 20/2092 v 33/2100, HR 0.60 (0.35-1.05) and the early-termination
disclosure; PubMed's own is 2,124 chars).

For every PubMed record held in cache/<slug>/records.json, the CURRENT PubMed record is fetched (efetch XML, read-only) and
the held abstract is labelled by COVERAGE:
  FULL_ABSTRACT     the held text equals PubMed's abstract (whitespace-normalised)
  EXCERPT           the held text is a strict, shorter part of PubMed's abstract (an abridgement)
  DIFFERS           the held text is not contained in PubMed's (revised record, or another record)
  METADATA_ONLY     nothing held, PubMed has an abstract
  NO_ABSTRACT       PubMed has none either
Each EXCERPT / METADATA_ONLY gets the full abstract preserved as a SEPARATE object (bytes, sha256, fetched date) and the
numbers / sentences the held copy is missing, so an outcome-absence judgement can be made conditional on coverage.
The served cache (records.json) is never rewritten here: replacing it moves served pages, a captain decision.

    python scripts/g1_abstract_census.py SLUG [SLUG ...] -> outputs/k_gap/abstract_census/<slug>.json + _summary.json
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "abstract_census")


def _n(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def fetch_abstracts(pmids):
    """{pmid: (abstract_text, xml_sha256)} from PubMed efetch, the harness's own AbstractText assembly."""
    from harness import http
    out = {}
    for i in range(0, len(pmids), 150):
        batch = pmids[i:i + 150]
        for attempt in range(3):
            try:
                x = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                                  {"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "tool": "meta-harness",
                                   "email": "meta-harness@example.org"})
                break
            except Exception:  # noqa: BLE001 - retried; an unanswered batch is reported as not fetched
                x = None
                time.sleep(2 + 3 * attempt)
        time.sleep(0.4)
        if not x:
            continue
        root = ET.fromstring(x)
        for art in root.findall(".//PubmedArticle"):
            pmid = "".join(art.find(".//PMID").itertext()).strip()
            ab = " ".join((a.get("Label", "") + ": " if a.get("Label") else "") + "".join(a.itertext()).strip()
                          for a in art.findall(".//Abstract/AbstractText")).strip()
            out[pmid] = (ab, hashlib.sha256(ET.tostring(art)).hexdigest())
    return out


_NUM = re.compile(r"\d+(?:[.·]\d+)?(?:\s*/\s*\d+)?")


def run(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    recs = [r for r in (json.load(open(p, encoding="utf-8")).get("records") or []) if r.get("id_type", "pmid") == "pmid"
            and str(r.get("id", "")).isdigit()]
    fresh = fetch_abstracts([str(r["id"]) for r in recs])
    rows, today = [], datetime.date.today().isoformat()
    for r in recs:
        pid, held = str(r["id"]), _n(r.get("abstract"))
        if pid not in fresh:
            rows.append({"pmid": pid, "coverage": "NOT_FETCHED"})
            continue
        full, xsha = fresh[pid]
        fn = _n(full)
        if not fn:
            cov = "NO_ABSTRACT" if not held else "DIFFERS"
        elif held == fn:
            cov = "FULL_ABSTRACT"
        elif not held:
            cov = "METADATA_ONLY"
        elif held in fn or (len(held) < len(fn) and all(s in fn for s in re.split(r"(?<=[.;])\s+", held) if len(s) > 30)):
            cov = "EXCERPT"
        else:
            cov = "DIFFERS"
        row = {"pmid": pid, "title": (r.get("title") or "")[:160], "coverage": cov, "held_chars": len(held),
               "pubmed_chars": len(fn)}
        if cov in ("EXCERPT", "METADATA_ONLY", "DIFFERS"):
            missing_sents = [s for s in re.split(r"(?<=\.)\s+", fn) if s and s not in held]
            missing_nums = sorted({m for s in missing_sents for m in _NUM.findall(s)} - set(_NUM.findall(held)))
            row.update(full_abstract=full, full_sha256=hashlib.sha256(full.encode("utf-8")).hexdigest(),
                       pubmed_record_sha256=xsha, fetched=today, missing_sentences=missing_sents[:12],
                       missing_numbers=missing_nums[:40])
        rows.append(row)
    from collections import Counter
    out = {"slug": slug, "written": today, "writer": "scripts/g1_abstract_census.py", "n": len(rows),
           "coverage": dict(Counter(x["coverage"] for x in rows)), "rows": rows}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    return out


def main(argv):
    slugs = [a for a in argv if not a.startswith("--")]
    summ = {}
    for s in slugs:
        try:
            o = run(s)
            summ[s] = o["coverage"]
            print(s, o["n"], o["coverage"], flush=True)
        except Exception as exc:  # noqa: BLE001
            summ[s] = {"error": str(exc)[:200]}
            print(s, "ERROR", str(exc)[:200], flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(summ, open(os.path.join(OUT, "_summary.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
