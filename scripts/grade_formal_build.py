"""Formal GRADE for each topic's served PRIMARY outcome, from its served review object and the formal RoB 2 objects
(outputs/robgrade/rob2/<slug>.json, scripts/rob2_dual.py). Writes outputs/robgrade/grade/<slug>.json and, beside it,
the CHANGE against the served (partial) GRADE -- every change of certainty is a signing-packet item, never applied here.

    python scripts/grade_formal_build.py [SLUG ...]
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from robgrade import grade_formal as gf  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "robgrade", "grade")


def build(slug):
    rv = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    o = next((x for x in rv["outcomes"] if x.get("primary")), rv["outcomes"][0])
    rp = os.path.join(ROOT, "outputs", "robgrade", "rob2", f"{slug}.json")
    rob = {}
    if os.path.exists(rp):
        for pmid, obj in json.load(open(rp, encoding="utf-8"))["trials"].items():
            if obj.get("outcome") == o["name"]:
                rob[f"PMID {pmid}"] = obj
    served = rv.get("grade") or {}
    stale = any("STALE" in str((d or {}).get("basis") or "") for d in (served.get("domains") or {}).values())
    g = gf.grade(o, rob, stale=stale)
    g["served_partial_grade"] = {"certainty": served.get("certainty"), "downgrades": served.get("downgrades"),
                                 "unassessed_domains": served.get("unassessed_domains")}
    g["certainty_change"] = None if served.get("certainty") == g["certainty"] else \
        {"from": served.get("certainty"), "to": g["certainty"], "state": "UNSIGNED -- for the signing packet"}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(g, fh, indent=1, ensure_ascii=False, sort_keys=True)
    return g


def main(argv):
    for s in [a for a in argv if not a.startswith("--")]:
        g = build(s)
        print(s, "certainty", g["certainty"], "(assessed domains only:", g["certainty_from_assessed_domains_only"], ")",
              {k: (d["downgrade"], d["state"]) for k, d in g["domains"].items()}, "served:", g["served_partial_grade"]["certainty"])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
