"""Metadata fields REBOUND between two full rebuilds (read-only).

  python scripts/nr_v101_metadata_diff.py A_DIR B_DIR [--out REPORT.json]

For every served row (pooled AND declared-absent) of every topic, the outcome-DEFINITION and TIMEPOINT fields a reader
sees: row.follow_up_window, row.endpoint_definition, compat_dimensions.{follow_up_window,endpoint_definition}.{value,source},
admission.follow_up_window.{trial_value,verdict}. A field is REBOUND when its value (or the source it cites) differs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FIELDS = (("follow_up_window",), ("endpoint_definition",),
          ("compat_dimensions", "follow_up_window", "value"), ("compat_dimensions", "follow_up_window", "source"),
          ("compat_dimensions", "endpoint_definition", "value"), ("compat_dimensions", "endpoint_definition", "source"),
          ("admission", "follow_up_window", "trial_value"), ("admission", "follow_up_window", "verdict"))


def _get(d, path):
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def _rows(rv):
    out = {}
    for o in (rv or {}).get("outcomes") or []:
        for kind in ("trials", "declared_absent_trials"):
            for t in o.get(kind) or []:
                out[f"{o['name']}|{t.get('id')}|{kind}"] = t
    return out


def main(argv):
    a, b = Path(argv[0]), Path(argv[1])
    rep = {"fields_compared": 0, "fields_present": 0, "rebound": [], "by_field": {}}
    for fb in sorted(b.glob("*.review.json")):
        fa = a / fb.name
        if not fa.exists():
            continue
        slug = fb.name[:-len(".review.json")]
        ra = _rows(json.loads(fa.read_text(encoding="utf-8")))
        rb = _rows(json.loads(fb.read_text(encoding="utf-8")))
        for key in sorted(set(ra) & set(rb)):
            for path in FIELDS:
                va, vb = _get(ra[key], path), _get(rb[key], path)
                rep["fields_compared"] += 1
                rep["fields_present"] += (va is not None or vb is not None)
                if va != vb:
                    name = ".".join(path)
                    rep["rebound"].append({"slug": slug, "row": key, "field": name, "a": va, "b": vb})
                    rep["by_field"][name] = rep["by_field"].get(name, 0) + 1
    print(f"metadata fields rebound: {len(rep['rebound'])} of {rep['fields_present']} present "
          f"({rep['fields_compared']} compared); by field: {rep['by_field']}")
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
