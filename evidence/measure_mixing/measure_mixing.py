"""Which served pools mix effect measures today? (report only; external review of balanced-crystalloids, 2026-09-26)

usage: python evidence/measure_mixing/measure_mixing.py <ref of the served tree> <out.json>
For every served review.json at <ref> (git objects), every outcome with a served pooled estimate, each admitted input's measure is
what the ENGINE pooled, not what a label says:
  a stated effect (effect + CI)                -> its scale (HR / RR / OR / IRR / MD / SMD)
  arm counts with no stated effect             -> the ratio the engine reconstructs: RR or OR per the outcome's estimand (the
                                                  pipeline's `meas`: 2x2 pools as RR/OR only; HR is never reconstructed)
  events over person-time / means              -> IRR / MD
Each input is also tagged by ADJUSTMENT: reconstructed from counts -> UNADJUSTED; a stated effect whose own source quotation says
"adjusted" -> ADJUSTED; otherwise UNSTATED (the source does not say, and this script does not guess).
A pool MIXES MEASURES when its inputs carry more than one measure; it MIXES ADJUSTMENT when it combines ADJUSTED and UNADJUSTED.
The served label is compared with the derived one: a label that names one measure over a mixed pool is DECLARED, not derived."""
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from harness import estmeasure  # noqa: E402  the SAME readers the gate uses: the count and the refusal cannot disagree


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def input_measure(t, outcome_estimand):
    m = (outcome_estimand or "RR").upper()
    return estmeasure.input_label(t, m if m in ("RR", "OR") else "RR") or "UNKNOWN"


def adjustment(t):
    return estmeasure.adjustment_of(t)


def main(ref, out_path):
    names = [n for n in _git("ls-tree", "-r", "--name-only", ref, "docs/reviews").decode().splitlines()
             if n.count("/") == 3 and n.endswith("/review.json")]
    rows, per_topic = [], defaultdict(lambda: {"primary_mixed": False, "any_mixed": False, "primary_adjustment_mixed": False})
    pooled_primary_topics = set()
    for n in sorted(names):
        slug = n.split("/")[2]
        rev = json.loads(_git("show", f"{ref}:{n}"))
        for o in rev.get("outcomes") or []:
            res = o.get("result") or {}
            if res.get("estimate") is None:
                continue
            trials = o.get("trials") or []
            meas = [input_measure(t, o.get("estimand")) for t in trials]
            adj = [adjustment(t) for t in trials]
            kinds = sorted(set(meas))
            mixed = len(kinds) > 1
            adj_mixed = "ADJUSTED" in adj and "UNADJUSTED" in adj
            served = str(res.get("scale") or "").upper()
            label_state = ("DERIVED" if not mixed and kinds == [served] else
                           "DECLARED_OVER_MIXED" if mixed else "DECLARED_DIFFERS")
            primary = bool(o.get("primary"))
            if primary:
                pooled_primary_topics.add(slug)
            per_topic[slug]["any_mixed"] |= mixed
            if primary:
                per_topic[slug]["primary_mixed"] |= mixed
                per_topic[slug]["primary_adjustment_mixed"] |= adj_mixed
            rows.append({"slug": slug, "outcome": o.get("name"), "primary": primary, "k": len(trials), "served_label": served,
                         "input_measures": dict(Counter(meas)), "mixed_measures": mixed, "adjustment": dict(Counter(adj)),
                         "mixed_adjustment": adj_mixed, "label_state": label_state,
                         "estmeasure_status": (res.get("estmeasure") or {}).get("status"),
                         "served": {k: res.get(k) for k in ("estimate", "ci_low", "ci_high", "ci_low_fixed", "ci_high_fixed", "tau2", "Q")},
                         "inputs": [{"id": t.get("id"), "measure": m, "adjustment": a, "effect": t.get("effect"),
                                     "counts": [t.get("ai"), t.get("n1i"), t.get("ci"), t.get("n2i")]}
                                    for t, m, a in zip(trials, meas, adj)]})
    topics = sorted(per_topic)
    res = {"served_tree": ref, "pages": len(names),
           "topics_with_a_served_pool": len(topics),
           "topics_with_a_served_primary_pool": len(pooled_primary_topics),
           "topics_primary_pool_mixes_measures": sorted(s for s in topics if per_topic[s]["primary_mixed"]),
           "topics_any_pool_mixes_measures": sorted(s for s in topics if per_topic[s]["any_mixed"]),
           "topics_primary_pool_mixes_adjustment": sorted(s for s in topics if per_topic[s]["primary_adjustment_mixed"]),
           "pools": len(rows), "pools_mixing_measures": sum(r["mixed_measures"] for r in rows),
           "pools_label_declared_over_mixed": sum(r["label_state"] == "DECLARED_OVER_MIXED" for r in rows),
           "pools_label_differs_from_unmixed_inputs": sum(r["label_state"] == "DECLARED_DIFFERS" for r in rows),
           "rows": rows}
    json.dump(res, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    for r in rows:
        if r["mixed_measures"] or r["label_state"] != "DERIVED" or r["mixed_adjustment"]:
            print(f"  {r['slug']:40s} {'P' if r['primary'] else ' '} k={r['k']:2d} served {r['served_label']:4s} inputs {r['input_measures']} "
                  f"adj {r['adjustment']} {r['label_state']} est={r['served']['estimate']}  [{(r['outcome'] or '')[:40]}]")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
