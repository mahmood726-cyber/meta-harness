"""Served exposure of the estimator-label defect: for every pooled trial row on every LIVE page (review.json fetched from Pages,
never the repo), compare the stored estimator label (trial 'scale') with the measure the row's own effect clause states.

Measured with the verifier's own stdlib functions (clause_with_effect, clause_measure, scale_measure), so the census is the same
rule a gate check would apply -- and therefore also the false-refusal count such a check would have on today's corpus.
usage: python evidence/ordered_contrast/estimator_owner/estimator_label_census.py <slugs.txt> <out.json>"""
import collections
import json
import os
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import verify_bundle as vb  # noqa: E402

BASE = "https://mahmood726-cyber.github.io/meta-harness/"


def main(slugs_file, out):
    slugs = [line.split(":")[0] for line in open(slugs_file, encoding="utf-8").read().split() if line]
    rows, errors = [], {}
    for s in slugs:
        try:
            req = urllib.request.Request(BASE + f"reviews/{s}/review.json", headers={"Cache-Control": "no-cache", "User-Agent": "oc-census/1"})
            with urllib.request.urlopen(req, timeout=300) as r:
                rev = json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errors[s] = str(e)[:200]
            continue
        for o in rev.get("outcomes") or []:
            res = o.get("result") or {}
            if res.get("estimate") is None:
                continue                                   # only rows that entered a served pooled number
            for t in o.get("trials") or []:
                vals = [t.get("effect"), t.get("ci_low"), t.get("ci_high")]
                label = vb.scale_measure(t.get("scale"))
                span = t.get("endpoint_result_span") or ""
                clause = vb.clause_with_effect(span, vals) if span and all(v is not None for v in vals) else None
                cm = vb.clause_measure(clause) if clause else {"state": "NO_CLAUSE", "measure": None}
                if t.get("scale") in ("MD", "SMD") or (t.get("mean1") is not None):
                    kind = "CONTINUOUS (not a ratio; outside this check)"
                elif t.get("ai") is not None and t.get("effect") is None:
                    kind = "COUNTS_ONLY (the harness computes the ratio from 2x2; no stated estimator to bind)"
                elif cm["state"] == "NO_CLAUSE":
                    kind = "NO_CLAUSE_LOCATED"
                elif cm["state"] != "STATED":
                    kind = f"CLAUSE_{cm['state']}"
                elif label == cm["measure"]:
                    kind = "MATCH"
                else:
                    kind = "LABEL_DISAGREES_WITH_CLAUSE"
                rows.append({"slug": s, "outcome": o.get("name"), "primary": bool(o.get("primary")), "trial": t.get("id"),
                             "label": t.get("scale"), "clause_measure": cm.get("measure"), "clause_state": cm["state"], "kind": kind,
                             "clause": (clause or "")[:300]})
    summary = collections.Counter(r["kind"] for r in rows)
    json.dump({"base": BASE, "slugs": len(slugs), "errors": errors, "summary": dict(summary), "rows": rows},
              open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print("slugs", len(slugs), "errors", len(errors), "pooled trial rows", len(rows))
    for k, v in summary.most_common():
        print(f"  {v:4d} {k}")
    for r in rows:
        if r["kind"] == "LABEL_DISAGREES_WITH_CLAUSE":
            print("  DISAGREES:", r["slug"], "|", r["outcome"], "|", r["trial"], "| label", r["label"], "| clause", r["clause_measure"], "|", r["clause"][:140])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
