"""Served diff between two full rebuilds (or a rebuild and the committed pages). Read-only.

  python scripts/nr_v101_served_diff.py A_DIR B_DIR [--out REPORT.json]
      A_DIR / B_DIR: directories of <slug>.review.json produced by rebuilding every served topic with
      scripts/build_topic_recorded.py <slug> --now 2026-09-11; the literal COMMITTED:<ref> reads docs/reviews/<slug>/review.json
      at that git ref instead.

Per outcome: the pooled result (k, estimate, CI, state) and the pooled trial set. Per row (pooled AND declared-absent):
its endpoint class, admissibility verdict and reason code. A row FLIPS when its admissibility or class changes, or when it
moves between pooled and declared-absent.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(src: str, slug: str):
    if src.startswith("COMMITTED:"):
        p = subprocess.run(["git", "-C", str(ROOT), "show", f"{src.split(':', 1)[1]}:docs/reviews/{slug}/review.json"],
                           capture_output=True)
        return json.loads(p.stdout) if p.returncode == 0 else None
    f = Path(src) / f"{slug}.review.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def _slugs(src: str):
    return sorted(p.name[:-len(".review.json")] for p in Path(src).glob("*.review.json"))


def _rows(rv):
    out, res = {}, {}
    for o in (rv or {}).get("outcomes") or []:
        r = o.get("result") or {}
        res[o["name"]] = {"k": r.get("k"), "estimate": r.get("estimate"), "ci_low": r.get("ci_low"),
                          "ci_high": r.get("ci_high"), "state": r.get("state"),
                          "trials": sorted(str(t.get("id")) for t in o.get("trials") or [])}
        for kind, rows in (("pooled", o.get("trials") or []), ("absent", o.get("declared_absent_trials") or [])):
            for t in rows:
                out[f"{o['name']}|{t.get('id')}"] = {
                    "where": kind, "class": t.get("target_endpoint_class"),
                    "admissibility": t.get("endpoint_admissibility"),
                    "reason_code": t.get("reason_code") if kind == "absent" else None}
    return res, out


def main(argv):
    a, b = argv[0], argv[1]
    slugs = _slugs(b) if not b.startswith("COMMITTED:") else _slugs(a)
    rep = {"topics": len(slugs), "outcome_changes": [], "row_flips": [], "rows_compared": 0, "missing": []}
    for s in slugs:
        ra, rb = _load(a, s), _load(b, s)
        if ra is None or rb is None:
            rep["missing"].append(s)
            continue
        (res_a, rows_a), (res_b, rows_b) = _rows(ra), _rows(rb)
        for name in sorted(set(res_a) | set(res_b)):
            if res_a.get(name) != res_b.get(name):
                rep["outcome_changes"].append({"slug": s, "outcome": name, "a": res_a.get(name), "b": res_b.get(name)})
        keys = sorted(set(rows_a) | set(rows_b))
        rep["rows_compared"] += len(keys)
        for k in keys:
            x, y = rows_a.get(k), rows_b.get(k)
            if x != y:
                rep["row_flips"].append({"slug": s, "row": k, "a": x, "b": y})
    print(f"topics {rep['topics']} (missing {rep['missing']}); outcome results changed: {len(rep['outcome_changes'])}; "
          f"rows that flip: {len(rep['row_flips'])} of {rep['rows_compared']}")
    for c in rep["outcome_changes"]:
        print(f"  OUTCOME {c['slug']} / {c['outcome']}: {c['a']} -> {c['b']}")
    for f in rep["row_flips"]:
        print(f"  ROW {f['slug']} / {f['row']}: {f['a']} -> {f['b']}")
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
