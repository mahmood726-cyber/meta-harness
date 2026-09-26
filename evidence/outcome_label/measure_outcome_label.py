"""Is each served PRIMARY pool's outcome label derived from its inputs? (report only; external review of colchicine-postop-af, 2026-09-26)

usage: python evidence/outcome_label/measure_outcome_label.py <ref of the served tree> <out.json>
The served label states a follow-up window (outcome.timepoint), an analysis set (outcome.population) and an outcome under one name.
Every pooled input carries compat_dimensions: for each dimension a value AND the `source` it came from. A value whose source is the
label itself -- outcome.timepoint, outcome.name, or study_effect.analysis_population (which the pipeline fills from the topic's
declared population) -- was COPIED onto the input from the label: it cannot confirm the label (circular). A value from the input's
own committed source text, its registry timeframe or the definition audit is DERIVED.

Per primary pool, per dimension (window, analysis set, definition):
  CONTRADICTED   the harness's own per-input verdict (compat_key.<dim>.per_trial) says an input FAILS the declared value
  ASSERTED       at least one input's value was copied from the label (the label is not shown to describe that input)
  MIXED          every value is derived, but the inputs' values differ (one label over several windows / sets / definitions)
  DERIVED_MATCH  every value is derived and all are the same
A pool's label MATCHES its inputs only if every dimension is DERIVED_MATCH."""
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COPIED = {"outcome.timepoint", "outcome.name", "outcome.population", "study_effect.analysis_population"}
DIMS = ("follow_up_window", "analysis_set", "endpoint_definition")


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def _norm(v):
    return json.dumps(v, sort_keys=True).lower() if isinstance(v, (dict, list)) else " ".join(str(v or "").lower().split())


def dimension_state(o, dim):
    trials = o.get("trials") or []
    ck = (o.get("compat_key") or {}).get(dim)
    fails = [p.get("trial") for p in (ck.get("per_trial") or [])] if isinstance(ck, dict) else []
    if isinstance(ck, dict) and any(p.get("verdict") == "FAIL" for p in ck.get("per_trial") or []):
        return "CONTRADICTED", [p for p in ck["per_trial"] if p.get("verdict") == "FAIL"]
    vals, copied = [], []
    for t in trials:
        cd = (t.get("compat_dimensions") or {}).get(dim)
        if not isinstance(cd, dict) or cd.get("source") in COPIED or not cd.get("source"):
            copied.append({"trial": t.get("id"), "source": (cd or {}).get("source") if isinstance(cd, dict) else None})
        else:
            vals.append(_norm(cd.get("value")))
    if copied:
        return "ASSERTED", copied
    return ("MIXED", sorted(set(vals))) if len(set(vals)) > 1 else ("DERIVED_MATCH", sorted(set(vals)))


def main(ref, out_path):
    names = [n for n in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().splitlines()
             if n.count("/") == 3 and n.endswith("/review.json")]
    rows = []
    for n in sorted(names):
        slug = n.split("/")[2]
        o = next((x for x in json.loads(_git("show", f"{ref}:{n}")).get("outcomes") or [] if x.get("primary")), None)
        if not o or (o.get("result") or {}).get("estimate") is None:
            continue
        dims = {d: dimension_state(o, d) for d in DIMS}
        states = {d: s for d, (s, _) in dims.items()}
        overall = ("CONTRADICTED" if "CONTRADICTED" in states.values() else "ASSERTED" if "ASSERTED" in states.values()
                   else "MIXED" if "MIXED" in states.values() else "DERIVED_MATCH")
        rows.append({"slug": slug, "k": len(o.get("trials") or []),
                     "label": {"name": o.get("name"), "timepoint": o.get("timepoint"), "population": o.get("population")},
                     "overall": overall, "dimensions": states, "detail": {d: det for d, (_, det) in dims.items()}})
    res = {"served_tree": ref, "primary_pools": len(rows), "overall": dict(Counter(r["overall"] for r in rows)),
           "label_matches_inputs": sum(r["overall"] == "DERIVED_MATCH" for r in rows),
           "label_does_not_match_inputs": sum(r["overall"] != "DERIVED_MATCH" for r in rows),
           "per_dimension": {d: dict(Counter(r["dimensions"][d] for r in rows)) for d in DIMS}, "rows": rows}
    json.dump(res, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    for r in rows:
        print(f"  {r['slug']:42s} {r['overall']:14s} k={r['k']:2d} {r['dimensions']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
