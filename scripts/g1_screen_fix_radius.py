"""RADIUS of a screen-rule fix, measured over EVERY held record of every G1 topic (not just the trials that motivated it).

Each topic's committed records (cache/<slug>/records.json, plus the acq member records our screen was run on for
comparator trials the search never retrieved) go through the real screener (harness.screen.run over pipeline._dedup)
IN MEMORY; nothing under cache/, topics/ or docs/ is written. A snapshot taken at the base commit and one taken with
the fix are diffed: every flipped record is listed with both decisions, its rule and span, and whether the recorded
dual review (outputs/search_audit/screen_dual_review.json) endorses the new decision.

  python scripts/g1_screen_fix_radius.py snap OUT.json        decisions under the CURRENT code
  python scripts/g1_screen_fix_radius.py diff BASE.json NEW.json [-> outputs/search_audit/screen_fix_radius.json]
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def snap(out_path):
    from harness import pipeline, screen
    import g1_screen_dual_review as D
    mem, _ = D._members()
    a = _j(os.path.join(ROOT, "outputs", "search_audit", "SEARCH_SCREEN_AUDIT.json"))
    named_pm = {t["slug"]: {p for r in t["trials"] if r["kind"] == "SCREEN_NAMED" for p in r["pmids"]} for t in a["topics"]}
    out = {}
    for t in a["topics"]:
        s = t["slug"]
        config = copy.deepcopy(_j(os.path.join(ROOT, "topics", s + ".json")))
        records = copy.deepcopy(_j(os.path.join(ROOT, "cache", s, "records.json")))
        have = {str(r.get("id")) for r in records.get("records") or []}
        extra = [dict(mem[p]) for p in sorted(named_pm.get(s, set())) if p in mem and p not in have]
        records["records"] = list(records.get("records") or []) + extra
        with redirect_stdout(io.StringIO()):
            merged = pipeline._dedup(records, config.get("pivotal_trials"))
            scr = screen.run(merged, config)
        out[s] = {str(d["id"]): {k: d.get(k) for k in ("decision", "rule_id", "reason", "span")} for d in scr["decisions"]}
    json.dump(out, open(out_path, "w", encoding="utf-8"), indent=0, ensure_ascii=False)
    print(out_path, sum(len(v) for v in out.values()), "decisions over", len(out), "topics")


def diff(base_p, new_p, out_p=None):
    b, n = _j(base_p), _j(new_p)
    dr_p = os.path.join(ROOT, "outputs", "search_audit", "screen_dual_review.json")
    dr = {}
    if os.path.exists(dr_p):
        for it in _j(dr_p)["items"]:
            if it.get("state") == "READ":
                dr[(it["slug"], str(it["record"]))] = it
    flips = []
    for s in sorted(b):
        for rid, d0 in b[s].items():
            d1 = (n.get(s) or {}).get(rid)
            if not d1 or (d0["decision"], d0["rule_id"]) == (d1["decision"], d1["rule_id"]):
                continue
            it = dr.get((s, rid))
            want = None
            if it:
                want = {"ELIGIBLE": "include", "INELIGIBLE": "exclude"}.get(it.get("final"))
            flips.append({"slug": s, "record": rid, "before": d0, "after": d1,
                          "dual_review_final": (it or {}).get("final"),
                          "endorsed": None if want is None else want == d1["decision"]})
    res = {"n_decisions": sum(len(v) for v in b.values()), "n_flips": len(flips),
           "endorsed": sum(1 for f in flips if f["endorsed"] is True),
           "contradicted": sum(1 for f in flips if f["endorsed"] is False),
           "unreviewed": sum(1 for f in flips if f["endorsed"] is None), "flips": flips}
    if out_p:
        json.dump(res, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print({k: res[k] for k in ("n_decisions", "n_flips", "endorsed", "contradicted", "unreviewed")})
    for f in flips:
        print(f"  {f['slug']} {f['record']}: {f['before']['decision']}/{f['before']['rule_id']} -> "
              f"{f['after']['decision']}/{f['after']['rule_id']} | dual review: {f['dual_review_final']}")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "snap":
        snap(sys.argv[2])
    else:
        diff(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
