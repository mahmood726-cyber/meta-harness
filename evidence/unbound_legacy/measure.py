"""Corpus-wide impact of the UNBOUND_LEGACY fail-closed fix, measured BEFORE any landing (report only; nothing served changes).

usage: python evidence/unbound_legacy/measure.py <ref of the served tree> <out.json>
For every served review.json under docs/reviews/ at <ref> (read from git objects, no checkout), for every outcome:
  N = rows the outcome pools; n = those admitted by the legacy branch (endpoint_admissibility == "UNBOUND_LEGACY").
Each served pooled result is first RECOMPUTED from its full row set with the producer's own synth.pool (PM tau2 + HKSJ with the
max(1, Q/(k-1)) floor, the pipeline's Study construction). Only if that reproduces the served estimate and CI at the served
rounding is the pool recomputed WITHOUT the legacy rows and the move reported. A pool that does not reproduce is listed as
NOT_REPRODUCED and no move is claimed for it. The derived moves are what a fail-closed rebuild would serve, pending notices."""
import json
import math
import os
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import synth                                  # noqa: E402
from harness.known_missing import _study_from_trial         # noqa: E402  the pipeline's Study construction


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def served_reviews(ref):
    out = {}
    for line in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().splitlines():
        parts = line.split("/")
        if len(parts) == 4 and parts[3] == "review.json":
            out[parts[2]] = json.loads(_git("show", f"{ref}:{line}"))
    return out


def _pool(rows, scale):
    if not rows:
        return None
    r = synth.pool([_study_from_trial(t, scale) for t in rows], scale=scale)
    return {"k": r.k, "estimate": r.estimate, "ci_low": r.ci_low, "ci_high": r.ci_high}


def _matches(served, got, digits=4):
    return all(served.get(k) is not None and round(got[k], digits) == round(float(served[k]), digits) for k in ("estimate", "ci_low", "ci_high"))


def main(ref, out_path):
    reviews = served_reviews(ref)
    report = {"served_tree": ref, "pages": len(reviews), "outcomes": [], "per_topic": {}, "totals": Counter()}
    per_topic = defaultdict(Counter)
    for slug, rev in sorted(reviews.items()):
        for o in rev.get("outcomes") or []:
            rows = o.get("trials") or []
            res = o.get("result") or {}
            legacy = [t for t in rows if t.get("endpoint_admissibility") == "UNBOUND_LEGACY"]
            kind = "primary" if o.get("primary") else (o.get("kind") or "other")
            per_topic[slug]["rows"] += len(rows)
            per_topic[slug]["unbound_legacy"] += len(legacy)
            per_topic[slug][f"unbound_legacy_{kind}"] += len(legacy)
            report["totals"]["rows"] += len(rows)
            report["totals"]["unbound_legacy"] += len(legacy)
            if not legacy:
                continue
            entry = {"slug": slug, "outcome": o.get("name"), "kind": kind, "N": len(rows), "n_unbound_legacy": len(legacy),
                     "legacy_rows": [{"id": t.get("id"), "label": t.get("label"), "provenance": t.get("provenance"),
                                      "effect": [t.get("effect"), t.get("ci_low"), t.get("ci_high")], "scale": t.get("scale"),
                                      "counts": [t.get("ai"), t.get("n1i"), t.get("ci"), t.get("n2i")],
                                      "source": (t.get("source") or "")[:160]} for t in legacy]}
            if res.get("estimate") is None:
                entry["served_pool"] = None
                entry["move"] = "NO_SERVED_POOL"
            else:
                scale = res.get("scale") or "RR"
                try:
                    full = _pool(rows, scale)
                except Exception as e:  # noqa: BLE001
                    full, entry["recompute_error"] = None, f"{type(e).__name__}: {e}"
                entry["served_pool"] = {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")}
                if len(legacy) == len(rows):
                    # every pooled row is legacy: the pool is withdrawn by MEMBERSHIP alone, whatever its arithmetic
                    entry["move"] = "POOL_WITHDRAWN (k -> 0)"
                    entry["derived_from"] = "membership (n == N); no arithmetic needed"
                    entry["recomputed_full_reproduces_served"] = bool(full and full["k"] == res.get("k") and _matches(res, full))
                    report["totals"]["pools_moving"] += 1
                elif not full or full["k"] != res.get("k") or not _matches(res, full):
                    entry["move"] = "NOT_REPRODUCED"
                    entry["recomputed_full"] = full
                    report["totals"]["not_reproduced"] += 1
                else:
                    kept = [t for t in rows if t.get("endpoint_admissibility") != "UNBOUND_LEGACY"]
                    after = _pool(kept, scale)
                    entry["after_fail_closed"] = after and {k: (round(v, 4) if isinstance(v, float) else v) for k, v in after.items()}
                    if after is None:
                        entry["move"] = "POOL_WITHDRAWN (k -> 0)"
                    else:
                        entry["move"] = ("CROSSES_NULL" if (full["ci_low"] < 1 < full["ci_high"]) != (after["ci_low"] < 1 < after["ci_high"])
                                         and scale.upper() not in ("MD", "SMD") else "MOVES")
                        entry["delta_log_estimate"] = (round(math.log(after["estimate"]) - math.log(full["estimate"]), 4)
                                                       if scale.upper() not in ("MD", "SMD") else None)
                    report["totals"]["pools_moving"] += 1
            report["outcomes"].append(entry)
    report["per_topic"] = {s: dict(c) for s, c in sorted(per_topic.items())}
    report["topics_with_unbound_legacy"] = sorted(s for s, c in per_topic.items() if c["unbound_legacy"])
    report["totals"] = dict(report["totals"])
    report["totals"]["pooled_outcomes_with_legacy"] = len([e for e in report["outcomes"] if e.get("served_pool")])
    report["totals"]["primary_pools_withdrawn"] = len([e for e in report["outcomes"] if e["kind"] == "primary" and e["move"].startswith("POOL_WITHDRAWN")])
    report["totals"]["primary_pools_crossing_null"] = len([e for e in report["outcomes"] if e["kind"] == "primary" and e["move"] == "CROSSES_NULL"])
    json.dump(report, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: report[k] for k in ("served_tree", "pages", "totals", "topics_with_unbound_legacy")}, indent=1))
    for e in report["outcomes"]:
        print(f"  {e['slug']:40s} {e['kind']:9s} {e['n_unbound_legacy']} of {e['N']:2d}  {e['move']:24s} "
              f"{e.get('served_pool') and (e['served_pool']['estimate'], e['served_pool']['ci_low'], e['served_pool']['ci_high'])} -> "
              f"{e.get('after_fail_closed') and (e['after_fail_closed']['estimate'], e['after_fail_closed']['ci_low'], e['after_fail_closed']['ci_high'])}  [{e['outcome'][:50]}]")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
