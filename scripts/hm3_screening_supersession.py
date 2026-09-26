"""Generate docs/evidence/hm3-held-source-audit/screening_roles_supersession.json: the DECLARED supersession of the HM3
controls by the V1.0.1 screening-roles landing. The pinned HM3 snapshot (primary-baseline-f6f7b14c.json) is never
rewritten; this file names, row by row, every screening record the landing changed (before -> after decision, rule and
reason; the added per-report `screening_record` key), and every harms outcome it made HARMS_INCOMPLETE with the reports
that did it. tests/test_hm3_pages.py accepts exactly these changes and nothing else.
  python scripts/hm3_screening_supersession.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "docs", "evidence", "hm3-held-source-audit")
LANDING = "evid/v1.0.1-screening-roles"
ADDED_KEYS = ("screening_record",)


def _strip(r):
    return {k: v for k, v in r.items() if k not in ADDED_KEYS}


def main():
    snap = json.load(open(os.path.join(EV, "primary-baseline-f6f7b14c.json"), encoding="utf-8"))
    decisions = json.load(open(os.path.join(EV, "decisions.json"), encoding="utf-8"))
    pages = {}
    for slug, before in sorted(snap["pages"].items()):
        after = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
        b = {str(r["id"]): r for r in before["screening_records"]}
        a = {str(r["id"]): _strip(r) for r in after["screening"]["records"]}
        if set(b) != set(a):
            raise SystemExit(f"REFUSED: {slug}: the set of screened records changed ({sorted(set(a) ^ set(b))[:5]}); "
                             "a screening-roles landing changes decisions, never the screened population")
        changed = {rid: {"before": {k: b[rid].get(k) for k in ("decision", "rule_id", "reason")},
                         "after": {k: a[rid].get(k) for k in ("decision", "rule_id", "reason")},
                         "other_fields_unchanged": {k: v for k, v in b[rid].items() if k not in ("decision", "rule_id", "reason")}
                         == {k: v for k, v in a[rid].items() if k not in ("decision", "rule_id", "reason")}}
                   for rid in sorted(b) if b[rid] != a[rid]}
        harms = {}
        for d in decisions:
            if d["topic"] != slug:
                continue
            o = next(x for x in after["outcomes"] if x["name"] == d["outcome"])
            if (o.get("result") or {}).get("harms_incomplete"):
                m = re.search(r"unresolved \(([^)]*)\)", o["result"].get("reason") or "")
                if not m:
                    raise SystemExit(f"REFUSED: {slug}/{d['outcome']} is HARMS_INCOMPLETE but names no unresolved reports")
                harms[d["outcome"]] = sorted(x.strip() for x in m.group(1).split(","))
        if changed or harms:
            pages[slug] = {"screening_rows_changed": changed, "added_keys": list(ADDED_KEYS),
                           "harms_incomplete_by_entered_reports": harms}
    out = {"landing": LANDING, "pinned_control": "primary-baseline-f6f7b14c.json (never rewritten)",
           "reason": ("V1.0.1 screening roles: every screened report carries ONE screening record (parent eligibility, report "
                      "relevance, result admissibility); secondary reports are linked to their parent family instead of "
                      "X1 'not a randomized controlled trial'; X1 reasons name their cause; protocol/design papers are "
                      "X-NO-RESULTS. A secondary report newly screened in can make a harms outcome HARMS_INCOMPLETE when "
                      "it reports that harm and is not yet extracted."),
           "pages": pages}
    open(os.path.join(EV, "screening_roles_supersession.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    n = sum(len(p["screening_rows_changed"]) for p in pages.values())
    print(f"pages with declared changes: {len(pages)}; screening rows changed: {n}; harms outcomes incomplete: "
          f"{sum(len(p['harms_incomplete_by_entered_reports']) for p in pages.values())}")


if __name__ == "__main__":
    main()
