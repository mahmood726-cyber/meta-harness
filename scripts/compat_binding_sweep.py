"""Sweep the compatibility-panel fields of every served trial row (all 32 topics) and diff two snapshots.

The panel fields (analysis set, follow-up window, endpoint definition, and the exposure / length-of-stay / schedule
fields added with outcome binding) are derived by harness.compat_check.derive_trial_dimensions from each served row,
its record and the definition audit. A snapshot holds, per (topic, outcome, trial), every field's value and source.

  python scripts/compat_binding_sweep.py snap OUT.json
  python scripts/compat_binding_sweep.py diff BEFORE.json AFTER.json [-> outputs/compat_binding/sweep.json + .md]
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FIELDS = ("analysis_set", "follow_up_window", "endpoint_definition", "exposure_duration", "length_of_stay", "schedule")


def _j(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return json.load(fh)


def snap(out_path):
    from harness import compat_check as cc
    rows = {}
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        if not os.path.exists(rp):
            continue
        review = _j("docs", "reviews", slug, "review.json")
        recp = os.path.join(ROOT, "cache", slug, "records.json")
        records = _j("cache", slug, "records.json") if os.path.exists(recp) else {}
        audit = cc._topic_definition_audit(slug, review)
        for o in review.get("outcomes") or []:
            for t in o.get("trials") or []:
                dims = cc.derive_trial_dimensions(review, o, t, records, audit)
                key = f"{slug}::{o.get('name')}::{dims.get('trial_id')}"
                rows[key] = {f: {k: (dims.get(f) or {}).get(k) for k in ("value", "source", "span")} for f in FIELDS
                             if f in dims}
    json.dump(rows, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(out_path, len(rows), "rows")


def diff(before_p, after_p, out_dir=None):
    a, b = json.load(open(before_p, encoding="utf-8")), json.load(open(after_p, encoding="utf-8"))
    changes, per_topic = [], {}
    for key in sorted(set(a) | set(b)):
        slug = key.split("::")[0]
        for f in FIELDS:
            va, vb = (a.get(key) or {}).get(f) or {}, (b.get(key) or {}).get(f) or {}
            if va.get("value") != vb.get("value") or va.get("source") != vb.get("source"):
                changes.append({"row": key, "field": f, "before": va, "after": vb,
                                "value_changed": va.get("value") != vb.get("value")})
                per_topic.setdefault(slug, set()).add(key)
    out = {"rows": len(set(a) | set(b)), "rows_changed": len({c["row"] for c in changes}),
           "field_changes": len(changes), "value_changes": sum(c["value_changed"] for c in changes),
           "per_topic_rows_changed": {k: len(v) for k, v in sorted(per_topic.items())}, "changes": changes}
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        json.dump(out, open(os.path.join(out_dir, "sweep.json"), "w", encoding="utf-8", newline="\n"), indent=1,
                  ensure_ascii=False)
        L = ["# Compatibility-panel fields bound to the selected outcome: sweep of all 32 topics", "",
             f"Rows: {out['rows']}; rows changed: {out['rows_changed']}; field changes: {out['field_changes']} "
             f"(value changes {out['value_changes']}; the rest change only the source the value is bound to).", "",
             "| Topic | Rows changed |", "|---|---|"]
        L += [f"| {k} | {v} |" for k, v in out["per_topic_rows_changed"].items()]
        L += ["", "| Row | Field | Before (source) | After (source) |", "|---|---|---|---|"]
        for c in changes:
            fmt = lambda d: f"{str(d.get('value'))[:90]} ({d.get('source')})".replace("|", "/")  # noqa: E731
            L.append(f"| {c['row'][:90]} | {c['field']} | {fmt(c['before'])} | {fmt(c['after'])} |")
        open(os.path.join(out_dir, "sweep.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print({k: v for k, v in out.items() if k != "changes"})
    return out


if __name__ == "__main__":
    if sys.argv[1] == "snap":
        snap(sys.argv[2])
    else:
        diff(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
