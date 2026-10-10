"""FAMILY-ELIGIBILITY RECONCILE COUNT (reviews 7, 12, 13; k-gap 10 Oct). Read-only over the served review.json of every topic.

The rule the reviews ask for: a trial family is ELIGIBLE iff
  (1) at least one of its records (its report PMIDs and its registry ids) is INCLUDED by the protocol's record-level
      screen (review.json screening.records, decision == include), AND
  (2) no trial-level exclusion applies: the family's own structural screen (harness.trial_family.screen_family) did not
      return INELIGIBLE.
A family the structural screen calls ELIGIBLE with NO included record is the r13 defect (noac 12 -> 7); a family with an
included record that the structural screen left UNKNOWN is listed separately (it is not counted eligible by this rule
either, because (2) needs the structural screen to have run without excluding it -- UNKNOWN is reported, not resolved).

Nothing is changed: this prints the before/after count per topic and writes the per-family table.

    python scripts/g1_family_reconcile.py -> outputs/k_gap/family_reconcile.json + .md
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ids_of(f):
    a = f.get("aliases") or {}
    out = {str(r.get("report_id")) for r in f.get("reports") or []}
    out |= {str(x) for x in (a.get("registry_ids") or []) + (a.get("report_ids") or [])}
    ib = f.get("identity_basis") or {}
    out |= {str(x) for x in (ib.get("primary_report_ids") or []) + (ib.get("registry_ids") or [])}
    out.discard("None")
    return out


def topic(slug):
    p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if not os.path.exists(p):
        return None
    r = json.load(open(p, encoding="utf-8"))
    inc = {str(x["id"]) for x in (r.get("screening") or {}).get("records") or [] if x.get("decision") == "include"}
    fams = r.get("trial_families") or []
    rows = []
    for f in fams:
        if f.get("is_trial_family") is False:
            continue
        st = (f.get("eligibility") or {}).get("state") or (f.get("eligibility") or {}).get("code")
        hit = sorted(ids_of(f) & inc)
        rec = "ELIGIBLE" if hit and st != "INELIGIBLE" and st == "ELIGIBLE" else (
            "INCLUDED_RECORD_STRUCTURAL_UNKNOWN" if hit and st != "INELIGIBLE" else
            "STRUCTURAL_ONLY_NO_INCLUDED_RECORD" if st == "ELIGIBLE" else "NOT_ELIGIBLE")
        rows.append({"family_id": f.get("family_id"), "served_state": st, "included_records": hit, "reconciled": rec})
    chain = r.get("family_count_chain") or {}
    return {"slug": slug, "served_eligible_families": chain.get("eligible_families"),
            "reconciled_eligible": sum(1 for x in rows if x["reconciled"] == "ELIGIBLE"),
            "structural_only_no_included_record": [x["family_id"] for x in rows
                                                   if x["reconciled"] == "STRUCTURAL_ONLY_NO_INCLUDED_RECORD"],
            "included_record_structural_unknown": [x["family_id"] for x in rows
                                                   if x["reconciled"] == "INCLUDED_RECORD_STRUCTURAL_UNKNOWN"],
            "families": rows}


def main():
    ab = {t["slug"] for t in json.load(open(os.path.join(ROOT, "registry", "g1_abandoned.json"), encoding="utf-8"))
          .get("topics", [])}
    out, md = {"writer": "scripts/g1_family_reconcile.py", "applied": False, "topics": {}}, []
    md += ["# Family-eligibility reconcile count (read-only; nothing applied)", "",
           "Rule: ELIGIBLE iff >=1 family record is INCLUDED by the record-level screen AND the structural family screen "
           "says ELIGIBLE (never INELIGIBLE / UNKNOWN). Source: each topic's served docs/reviews/<slug>/review.json.", "",
           "| topic | active | served eligible | reconciled | structural-only (no included record) | included record, structural UNKNOWN |",
           "|---|---|---|---|---|---|"]
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        t = topic(slug)
        if not t:
            continue
        out["topics"][slug] = t
        md.append(f"| {slug} | {'no' if slug in ab else 'yes'} | {t['served_eligible_families']} | {t['reconciled_eligible']} | "
                  f"{len(t['structural_only_no_included_record'])} | {len(t['included_record_structural_unknown'])} |")
    json.dump(out, open(os.path.join(ROOT, "outputs", "k_gap", "family_reconcile.json"), "w", encoding="utf-8",
                        newline="\n"), indent=1, ensure_ascii=False)
    open(os.path.join(ROOT, "outputs", "k_gap", "family_reconcile.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
