"""32-TOPIC SWEEP for a screen.py change: the served screen re-run on each topic's own pristine inputs (exactly as the
pipeline screens: served config, fetch.ensure cache replay, pipeline._dedup), decisions dumped per record. Run once on the
old code and once on the new, then diff. Read-only; served pages move only on the captain's regeneration.

    python scripts/g1_screen_sweep.py dump OUT.json        (all 32 topics)
    python scripts/g1_screen_sweep.py diff OLD.json NEW.json -> markdown table of every changed decision
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def dump(out_p):
    from harness import pipeline, screen, served_comparator as sc, fetch
    res = {}
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        tp = os.path.join(ROOT, "topics", slug + ".json")
        if not os.path.exists(tp):
            continue
        try:
            config = sc.served_config(slug, json.load(open(tp, encoding="utf-8")))
            records = fetch.ensure(config, "2026-10-09T00:00:00Z")
            cfg = pipeline.outcome_inputs(slug, config, copy.deepcopy(records))["config"]
            merged = pipeline._dedup(copy.deepcopy(records), cfg.get("pivotal_trials"))
            res[slug] = {d["id"]: [d["decision"], d.get("rule_id"), (d.get("reason") or "")[:200]]
                         for d in screen.run(copy.deepcopy(merged), cfg)["decisions"]}
            print(slug, len(res[slug]), flush=True)
        except Exception as exc:  # noqa: BLE001 - named per topic, never dropped
            res[slug] = {"__error__": f"{type(exc).__name__}: {str(exc)[:200]}"}
            print(slug, "ERROR", exc, flush=True)
    json.dump(res, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


def diff(old_p, new_p):
    old, new = json.load(open(old_p, encoding="utf-8")), json.load(open(new_p, encoding="utf-8"))
    md = ["| topic | record | old | new | new reason |", "|---|---|---|---|---|"]
    n = 0
    for slug in sorted(set(old) | set(new)):
        o, w = old.get(slug, {}), new.get(slug, {})
        for rid in sorted(set(o) | set(w)):
            ov, wv = o.get(rid, ["-", "-"]), w.get(rid, ["-", "-"])
            # an error is a whole STRING ('__error__': 'ValueError: ...'): slicing it [:2] made every failure 'Va', so two
            # different failures read as equal (codex pr65-cap-r1 #5). Compare and print it whole.
            key = lambda v: v if isinstance(v, str) else list(v[:2])
            if key(ov) != key(wv):
                n += 1
                show = lambda v: v if isinstance(v, str) else "/".join(map(str, v[:2]))
                reason = wv if isinstance(wv, str) else (list(wv) + ["", "", ""])[2][:120]
                md.append(f"| {slug} | {rid} | {show(ov)} | {show(wv)} | {reason} |")
    print(f"{n} changed decisions over {len(set(old) | set(new))} topics")
    print("\n".join(md))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    dump(a[1]) if a[0] == "dump" else diff(a[1], a[2])
