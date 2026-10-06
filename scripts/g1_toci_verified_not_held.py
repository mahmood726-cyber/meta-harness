"""G1 tocilizumab: facts read from a primary full text the shared cascade (scripts/fulltext_cascade.py, captain lane)
fetched but whose licence is not open, so the text is never committed. Recorded per paper: PMCID, the body's sha256, the
licence statement the bytes carry, and the short verbatim span the lane relies on (VERIFIED_NOT_HELD). A replay
re-fetches the PMCID and checks the sha256 and that the span is still verbatim in it.

  python scripts/g1_toci_verified_not_held.py STAGE_DIR    (STAGE_DIR = fulltext_cascade.py --stage output)
"""
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "g1", "data", "verified_not_held.json")
SLUG = "tocilizumab-covid19-mortality"
# what the lane reads from each text: (pmid, pmcid, label, timepoint, regex locating the span)
WANT = [("33631065", "PMC7953461", "REMAP-CAP", "in-hospital",
         r"In-hospital death\s*[\u2014-]+\s*no\./total no\. \(%\)\s*98/350 \(28\)\s*10/45 \(22\)\s*142/397 \(36\)")]
OPEN = re.compile(r"creativecommons\.org/(?:licenses/by|publicdomain)", re.I)


def main(stage):
    out = {}
    for pmid, pmcid, label, tp, rx in WANT:
        x = open(os.path.join(stage, SLUG, f"ft_{pmid}.txt"), encoding="utf-8").read()
        lic = re.search(r"<license[^>]*>.*?</license>", x, re.S)
        lic_s = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", lic.group(0))).strip() if lic else None
        if lic and OPEN.search(lic.group(0)):
            raise SystemExit(f"{pmid}: open licence -- hold the text instead (g1/data/acquired)")
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x)))
        m = re.search(rx, t)
        if not m:
            raise SystemExit(f"REFUSED: {pmid} span not found in the fetched body")
        out[pmid] = {"pmcid": pmcid, "label": label, "state": "VERIFIED_NOT_HELD",
                     "body_sha256": hashlib.sha256(x.encode("utf-8")).hexdigest(),
                     "fetched_by": "scripts/fulltext_cascade.py (captain lane), route NCBI_EFETCH_PMC",
                     "licence_in_bytes": lic_s, "why_not_held": "the licence the bytes state is not an open (CC) licence",
                     "timepoint": tp, "span": m.group(0),
                     "counts": dict(zip(("deaths_t", "n_t", "deaths_c", "n_c"),
                                        map(int, re.findall(r"(\d+)/(\d+)", m.group(0))[0] + re.findall(r"(\d+)/(\d+)", m.group(0))[2])))}
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=1, ensure_ascii=False)[:1200])


if __name__ == "__main__":
    main(sys.argv[1])
