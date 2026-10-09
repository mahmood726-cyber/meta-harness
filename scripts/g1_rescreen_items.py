"""Dual-screen items for the shadow re-screen's FLIPS (outputs/k_gap/rescreen/<slug>.json): each flip's pristine record,
as the served screen saw it (pipeline._dedup over a deep copy of the held records)."""
from __future__ import annotations

import copy
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def main():
    from harness import pipeline, served_comparator as sc, fetch
    items = []
    d = os.path.join(ROOT, "outputs", "k_gap", "rescreen")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        r = json.load(open(os.path.join(d, f), encoding="utf-8"))
        if not r.get("flips"):
            continue
        slug = r["slug"]
        cfg = sc.served_config(slug, json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8")))
        recs = fetch.ensure(cfg, "x")
        inp = pipeline.outcome_inputs(slug, cfg, copy.deepcopy(recs))
        merged = {x["id"]: x for x in pipeline._dedup(copy.deepcopy(recs), inp["config"].get("pivotal_trials"))}
        for fl in r["flips"]:
            if fl["id"] in merged:
                items.append({"key": f"rescreen::{slug}::{fl['id']}", "slug": slug, "record": merged[fl["id"]],
                              "origin": "shadow_rescreen", "fixes": fl["fixes"], "before": fl["before"]})
    json.dump(items, open(os.path.join(d, "_dual_items.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False, default=str)
    print(len(items), "flip items")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
