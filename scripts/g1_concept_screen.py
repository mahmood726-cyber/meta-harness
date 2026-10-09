"""REGEX-FIRST SCREEN of the concept-search records (outputs/k_gap/concept/<slug>.records.json), under the served screen
(harness/screen.run) with the fixed-rule overlay of g1_shadow_rescreen (F1-F5). No model call here: the records the regex
screen INCLUDES become items for the recorded dual codex screen (scripts/g1_dual_screen.py); everything else is recorded
with its rule, reason and span.

    python scripts/g1_concept_screen.py SLUG [SLUG ...] -> outputs/k_gap/concept/<slug>.screen.json + <slug>.dual_items.json
"""
from __future__ import annotations

import collections
import copy
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "concept")


def run(slug):
    from harness import screen, served_comparator as sc
    import g1_shadow_rescreen as sh
    cfg = sc.served_config(slug, json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8")))
    recs = json.load(open(os.path.join(OUT, f"{slug}.records.json"), encoding="utf-8"))
    for r in recs:
        r.setdefault("id_type", "nct" if str(r.get("id", "")).startswith("NCT") else "pmid")
        r.setdefault("pubtypes", [])
        r.setdefault("abstract", "")
    cfg2, applied = sh.overlay_config(cfg)
    recs2, fixes = [], {}
    for r in recs:
        r2, fx = sh.overlay_record(r, [])
        if r2.get("id_type") == "nct" and re.search(r"\bplacebo\b", " ".join(map(str, r2.get("interventions") or [])), re.I):
            cfg2.setdefault("include", {}).setdefault("comparator_overrides", []).append({"key": r2["id"], "term": "placebo"})
            fx.append("F1b")
        fixes[r["id"]] = fx
        recs2.append(r2)
    dec = screen.run(copy.deepcopy(recs2), cfg2)["decisions"]
    byid = {r["id"]: r for r in recs}
    inc = [d for d in dec if d["decision"] == "include"]
    out = {"slug": slug, "n_records": len(recs), "overlay": applied,
           "by_rule": dict(collections.Counter(d["rule_id"] for d in dec)),
           "includes": [{"id": d["id"], "title": (byid.get(d["id"]) or {}).get("title", "")[:220], "reason": d["reason"],
                         "span": d.get("span"), "fixes": fixes.get(d["id"])} for d in inc],
           "decisions": [{k: d.get(k) for k in ("id", "decision", "rule_id", "reason")} for d in dec],
           "writer": "scripts/g1_concept_screen.py"}
    json.dump(out, open(os.path.join(OUT, f"{slug}.screen.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    items = [{"key": f"concept::{slug}::{d['id']}", "slug": slug, "record": byid[d["id"]], "origin": "concept_search"}
             for d in inc if d["id"] in byid]
    json.dump(items, open(os.path.join(OUT, f"{slug}.dual_items.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    return out


def main(argv):
    for s in [a for a in argv if not a.startswith("--")]:
        try:
            o = run(s)
            print(f"{s}: {o['n_records']} new records -> regex includes {len(o['includes'])} | {o['by_rule']}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(s, "ERROR", type(exc).__name__, str(exc)[:300], flush=True)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
