"""Record the Europe PMC title of every meta the forest-reader lane has read (registry/model_proposals/
g1_lane_meta_titles.json: title + the response's sha256 + query), so secondary_meta_build.lane_intervention_refusal can
read a meta's own title offline. Titles only; never text.

    python scripts/g1_lane_meta_titles.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402
import secondary_meta_build as smb  # noqa: E402


def main():
    from harness import http
    o = gfr._j(gfr.OUT)
    pmids = sorted({str(v.get("pmid") or k.split("::", 1)[1]) for sec in ("results", "meta_results")
                    for k, v in (o.get(sec) or {}).items() if "::" in k})
    rec = gfr._j(smb.LANE_TITLES) if os.path.exists(smb.LANE_TITLES) else {"source": "Europe PMC REST search "
                                                                                     "(EXT_ID:<pmid> AND SRC:MED, lite)",
                                                                           "titles": {}}
    new = 0
    for p in pmids:
        if p in rec["titles"]:
            continue
        time.sleep(0.2)
        try:
            st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                                 {"query": f"EXT_ID:{p} AND SRC:MED", "format": "json", "resultType": "lite"}, tries=3)
        except Exception as e:  # noqa: BLE001 - not recorded; retried next run
            print("failed", p, str(e)[:80])
            continue
        r = (json.loads(b.decode("utf-8")).get("resultList") or {}).get("result") or []
        rec["titles"][p] = {"title": r[0].get("title") if r else None, "sha256": hashlib.sha256(b).hexdigest()}
        new += 1
    gfr._save(smb.LANE_TITLES, rec)
    print(f"{len(pmids)} lane metas; {new} titles recorded now; {sum(1 for v in rec['titles'].values() if v['title'])} "
          f"with a title")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
