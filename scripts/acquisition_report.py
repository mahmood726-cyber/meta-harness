"""Per-target report of the acquisition cascade: which provenance tier was found, from where, with hashes; what was
refused and why; every route attempted and its status. Offline: reads ATTEMPTS.jsonl, CANDIDATES.json, targets.json.
  python scripts/acquisition_report.py        # writes evidence/acquisition_cascade/REPORT.json + REPORT.md"""
from __future__ import annotations

import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import design_key, provenance_tiers  # noqa: E402

D = os.path.join(ROOT, "evidence", "acquisition_cascade")


def main():
    spec = json.load(open(os.path.join(D, "targets.json"), encoding="utf-8"))
    cands = json.load(open(os.path.join(D, "CANDIDATES.json"), encoding="utf-8"))["candidates"]
    attempts = [json.loads(l) for l in open(os.path.join(D, "ATTEMPTS.jsonl"), encoding="utf-8")]
    held = json.load(open(os.path.join(D, "held", "HELD.json"), encoding="utf-8"))
    routes = collections.defaultdict(list)
    for a in attempts:
        routes[a["target"]].append(a)
    results = []
    for t in spec["trials"]:
        for tg in t["targets"]:
            r = provenance_tiers.evaluate(t, tg, cands)
            r["expected_by_reviewer"] = tg.get("expected_by_reviewer")
            results.append(r)
    # what CORP-2's printed '0.49' is: audited against its own counts in the same sentence
    corp2 = next(r for r in results if r["trial"] == "CORP-2")
    audit = None
    if corp2["served_counts"]:
        (a, n1), (c, n2) = corp2["served_counts"]
        audit = design_key.ratio_label_audit(a, n1, c, n2, 0.49, 0.24, 0.65)
    per_route = {t: dict(collections.Counter(f"{a['route']}:{a['status']}" for a in rows)) for t, rows in routes.items()}
    out = {"topic": spec["topic"], "held_documents": len(held),
           "held_by_tier": dict(collections.Counter(v.get("tier_document") for v in held.values())),
           "attempts": len(attempts), "attempts_by_trial": per_route, "targets": results,
           "corp2_0_49": {"printed": "relative risk 0.49; 95% CI 0.24-0.65", "audit": audit}}
    json.dump(out, open(os.path.join(D, "REPORT.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    L = ["# Acquisition cascade report: colchicine-recurrent-pericarditis fixtures", "",
         f"{len(attempts)} recorded attempts; {len(held)} held open-access documents "
         f"({out['held_by_tier']}). Legitimate open routes only; every attempt is in `ATTEMPTS.jsonl` with URL, time, "
         "status and sha256.", "", "| Trial | Target | Status | Tier served | Counts | Conflict | Reviewer expected |",
         "|---|---|---|---|---|---|---|"]
    for r in results:
        L.append(f"| {r['trial']} | {r['outcome']} | **{r['status']}** | {r['served_tier'] or '—'} | "
                 f"{r['served_counts'] or '—'} | {r['conflict'] or '—'} | {r['expected_by_reviewer']} |")
    L += ["", "## Per target"]
    for r in results:
        L += ["", f"### {r['trial']} — {r['outcome']}: {r['status']}"]
        for w in r["primary_witnesses"] + r["secondary_witnesses"]:
            L.append(f"- {w['tier']} `{w['document']}` sha256 `{(w['document_sha256'] or '')[:16]}…` "
                     f"{('table ' + str(w.get('table')) + ' row ' + str(w.get('row'))) if w.get('row') else ('“' + (w.get('sentence') or '')[:220] + '”')} → {w['counts']}")
        for w in r["percent_corroboration"]:
            L.append(f"- corroboration only (percentages, no counts): {w['tier']} `{w['document']}` {w.get('table')} "
                     f"row {w.get('row')} → {w['percents']}")
        for w in r["not_this_row"]:
            L.append(f"- NOT this endpoint (excluded row): {w['tier']} `{w['document']}` → {w['counts']}")
        for w in r["refused"][:6]:
            L.append(f"- refused: `{w['document']}` — {w['reason']}")
        if len(r["refused"]) > 6:
            L.append(f"- … {len(r['refused']) - 6} more refused rows (REPORT.json)")
    L += ["", "## What CORP-2's '0.49' is", ""]
    if audit:
        L.append(f"The abstract prints 'relative risk 0.49; 95% CI 0.24-0.65' beside 26/120 vs 51/120. The counts give "
                 f"RR {audit['counts_rr']:.3f} (95% CI {audit['counts_ci'][0]:.3f}-{audit['counts_ci'][1]:.3f}). Read as "
                 f"a relative risk the printed figure is {audit['distance_as_rr']} log-units away; read as a relative "
                 f"risk REDUCTION (1 - RR, interval flipped) it is {audit['distance_as_rrr']} away. Verdict: "
                 f"**{audit['verdict']}**: 0.49 is the relative risk reduction under the label 'relative risk'.")
    L += ["", "## Routes attempted, per trial", ""]
    for t, c in per_route.items():
        L.append(f"- {t}: " + "; ".join(f"{k} ×{v}" for k, v in sorted(c.items())))
    open(os.path.join(D, "REPORT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    for r in results:
        print(f"{r['trial']:7} {r['outcome'][:34]:34} {r['status']:22} {r['served_tier'] or '-':17} {r['served_counts']}")
    print("corp2 0.49:", audit and audit["verdict"])


if __name__ == "__main__":
    main()
