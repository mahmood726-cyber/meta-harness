"""Formal GRADE preview for each topic's served PRIMARY outcome, from its served review object and the best
available outcome-matched formal RoB 2 tier. Writes outputs/robgrade/grade/<slug>.json and, beside it,
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
TIERS = [
    ("served contextual (A3)", os.path.join(ROOT, "outputs", "robgrade", "served", "rob2_ctx")),
    ("contextual (A3)", os.path.join(ROOT, "outputs", "robgrade", "rob2_ctx")),
    ("v3.1 (current replay)", os.path.join(ROOT, "outputs", "robgrade", "rob2_current")),
]


def rob_for(slug, outcome_name, pooled_trial_ids):
    """Select each pooled trial's first outcome- and identity-matched object."""
    pooled_trial_ids = set(pooled_trial_ids)
    rob, sources = {}, {}
    for label, directory in TIERS:
        path = os.path.join(directory, f"{slug}.json")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("outcome") != outcome_name:
            continue
        for pmid, obj in data["trials"].items():
            trial_id = f"PMID {pmid}"
            if trial_id not in pooled_trial_ids:
                continue
            if "outcome" in obj and obj["outcome"] != outcome_name:
                continue
            if "trial" in obj and obj["trial"] != trial_id:
                continue
            if trial_id not in rob:
                rob[trial_id] = obj
                sources[trial_id] = label
    return rob, sources


def build(slug):
    rv = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    o = next((x for x in rv["outcomes"] if x.get("primary")), rv["outcomes"][0])
    rob, sources = rob_for(slug, o["name"], [t.get("id") for t in o.get("trials") or []])
    served = rv.get("grade") or {}
    stale = any("STALE" in str((d or {}).get("basis") or "") for d in (served.get("domains") or {}).values())
    g = gf.grade(o, rob, stale=stale)
    g["rob_sources"] = dict(sorted(sources.items()))
    g["served_partial_grade"] = {"certainty": served.get("certainty"), "downgrades": served.get("downgrades"),
                                 "unassessed_domains": served.get("unassessed_domains")}
    g["certainty_change"] = None if served.get("certainty") == g["certainty"] else \
        {"from": served.get("certainty"), "to": g["certainty"], "state": "UNSIGNED -- for the signing packet"}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(g, fh, indent=1, ensure_ascii=False, sort_keys=True)
    return g


def main(argv):
    slugs = [a for a in argv if not a.startswith("--")]
    if not slugs:
        reviews = os.path.join(ROOT, "docs", "reviews")
        slugs = sorted(s for s in os.listdir(reviews)
                       if os.path.isfile(os.path.join(reviews, s, "review.json")))
    for s in slugs:
        g = build(s)
        print(s, "certainty", g["certainty"], "(assessed domains only:", g["certainty_from_assessed_domains_only"], ")",
              {k: (d["downgrade"], d["state"]) for k, d in g["domains"].items()}, "served:", g["served_partial_grade"]["certainty"])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
