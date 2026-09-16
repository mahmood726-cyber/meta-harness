"""Priority-1 audit artefact: every pooled per-trial value on every pooled page with the source span it was
extracted from, machine-readable, so an auditor checks value-against-source without re-deriving anything.
usage: python extraction_audit_table.py <repo_root> <out_json> <out_md>
Rows are read from docs/reviews/<slug>/review.json (the committed objects); nothing is recomputed."""
import csv
import glob
import io
import json
import os
import sys

ROOT, OUT_JSON, OUT_MD = sys.argv[1], sys.argv[2], sys.argv[3]
rows = []
pages_pooled = 0
for p in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
    slug = os.path.basename(os.path.dirname(p))
    r = json.load(open(p, encoding="utf-8"))
    for o in r.get("outcomes", []):
        res = o.get("result") or {}
        trials = o.get("trials") or []
        if not trials:
            continue
        if o.get("primary") and (res.get("k") or 0) >= 1:
            pages_pooled += 1
        for t in trials:
            rows.append({
                "slug": slug,
                "outcome": o.get("name"),
                "primary": bool(o.get("primary")),
                "trial_id": t.get("id"),
                "label": t.get("label"),
                "trial_key": t.get("trial_key"),
                "scale": t.get("scale") or res.get("scale"),
                "effect": t.get("effect"),
                "ci_low": t.get("ci_low"),
                "ci_high": t.get("ci_high"),
                "ai": t.get("ai"), "n1i": t.get("n1i"), "ci": t.get("ci"), "n2i": t.get("n2i"),
                "m1i": t.get("m1i"), "sd1i": t.get("sd1i"), "m2i": t.get("m2i"), "sd2i": t.get("sd2i"),
                "provenance": t.get("provenance"),
                "effect_source_id": t.get("effect_source_id") or t.get("report_id"),
                "selection_rule": t.get("selection_rule"),
                "source_span": t.get("source") or t.get("source_span"),
                "cross_source": (t.get("cross_source") or {}).get("ctgov_source") if isinstance(t.get("cross_source"), dict) else None,
                "cross_source_value": (t.get("cross_source") or {}).get("ctgov_rr") if isinstance(t.get("cross_source"), dict) else None,
                "analysis_set": t.get("analysis_set"),
                "timepoint": t.get("timepoint") or t.get("follow_up"),
                "design_key": (t.get("design_key") or {}).get("design") if isinstance(t.get("design_key"), dict) else t.get("design_key"),
                "pooled_result_k": res.get("k"),
                "pooled_estimate": res.get("estimate"),
            })
with_span = sum(1 for x in rows if x["source_span"])
with_digits_in_span = 0
for x in rows:
    sp = str(x["source_span"] or "")
    vals = [x[k] for k in ("effect", "ai", "ci", "n1i", "n2i", "m1i", "m2i") if x[k] is not None]
    if sp and vals and any(str(v).rstrip("0").rstrip(".") in sp or str(v) in sp for v in vals):
        with_digits_in_span += 1
summary = {
    "generated_from": ROOT,
    "pages_with_a_pooled_primary": pages_pooled,
    "per_trial_value_rows": len(rows),
    "rows_with_a_source_span": with_span,
    "rows_whose_span_contains_at_least_one_of_their_own_digits": with_digits_in_span,
    "note": "A row with no span, or a span containing none of its digits, is where value-against-source cannot be checked from this table alone -- start the audit there.",
}
json.dump({"summary": summary, "rows": rows}, open(OUT_JSON, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
buf = io.StringIO(); w = csv.writer(buf)
w.writerow(["slug", "outcome", "primary", "trial_id", "label", "scale", "effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i", "provenance", "selection_rule", "source_span"])
for x in rows:
    w.writerow([x["slug"], x["outcome"], x["primary"], x["trial_id"], x["label"], x["scale"], x["effect"], x["ci_low"], x["ci_high"], x["ai"], x["n1i"], x["ci"], x["n2i"], x["provenance"], x["selection_rule"], (x["source_span"] or "")[:400]])
open(OUT_MD, "w", encoding="utf-8", newline="\n").write(
    "# Extraction audit table -- every pooled per-trial value with its claimed source span\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary.items()) + "\n\nCSV (first 400 chars of each span):\n\n```csv\n" + buf.getvalue() + "```\n")
print(json.dumps(summary, indent=1))
