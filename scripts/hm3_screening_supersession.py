"""Generate docs/evidence/hm3-held-source-audit/screening_roles_supersession.json: the DECLARED supersession of the HM3
controls by the V1.0.1 screening-roles landing. The pinned HM3 snapshot (primary-baseline-f6f7b14c.json) is never
rewritten; this file names, row by row, every screening record the landing changed (before -> after decision, rule and
reason; the added per-report `screening_record` key), and every harms outcome it made HARMS_INCOMPLETE with the reports
that did it. tests/test_hm3_pages.py accepts exactly these changes and nothing else.
  python scripts/hm3_screening_supersession.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "docs", "evidence", "hm3-held-source-audit")
LANDING = "evid/v1.0.1-screening-roles + evid/v1.0.1-acquisition-cascade"
# keys a landing ADDS to every screened row (never a changed value): the per-report screening record, and for a platform
# / multi-comparison registration its per-comparison screening and pending decisions
ADDED_KEYS = ("screening_record", "comparisons", "pending_decisions")
# a DECIDED harm row (decisions.json) that a later landing moved, named with its new state and the reason
HARM_DECISIONS_SUPERSEDED = {
    ("melatonin-primary-insomnia-sol", "Adverse events", "22346363"): {
        "before": "POPULATION_MISMATCH (absent)", "after": "LINKED_NOT_A_TRIAL",
        "reason": ("Lemoine (22346363) is a post-hoc pooled analysis of four already-counted RCTs (its own text: 'A post hoc, "
                   "pooled analysis of four randomized, double-blind trials'; refs 25-28), with a safety set that also pools "
                   "single-blind and open-label studies: it is linked to its constituent trials (X-DEDUP, "
                   "docs/multi_trial_reports.json), never a trial row. The refusal's own reason (pooled safety set) stands.")},
    ("denosumab-vertebral-fracture", "Serious infection", "19671655"): {
        "before": "REFUSED_ON_EVIDENCE (absent)", "after": "POOLED",
        "values_after": {"ai": 159, "n1i": 3886, "ci": 133, "n2i": 3876},
        "reason": ("the refusal was true of the abstract and the registry's unaggregated infection terms; the aggregate is in "
                   "Table 1 of FREEDOM's own infection report (PMID 21892677, open access), a companion report of the same "
                   "trial, bound (EXACT_TARGET); result-change notice OPEN")},
    ("semaglutide-obesity-weight", "Gastrointestinal adverse events", "33567185"): {
        "before": "REFUSED_ON_EVIDENCE (absent)", "after": "POOLED",
        "values_after": {"ai": 969, "n1i": 1306, "ci": 314, "n2i": 655},
        "reason": ("the refusal was true of the abstract (GI discontinuations, not all GI events); the aggregate -- PATIENTS "
                   "with any GI disorder, on-treatment -- is in STEP 1's own safety table (repository copy held; excerpt "
                   "committed), never the adjacent EVENTS column (4309 vs 739); result-change notice OPEN")},
    ("semaglutide-obesity-weight", "Gastrointestinal adverse events", "33625476"): {
        "before": "REFUSED_ON_EVIDENCE (absent)", "after": "POOLED",
        "values_after": {"ai": 337, "n1i": 407, "ci": 129, "n2i": 204},
        "reason": ("the refusal was true of the abstract (percentages, no numerators); the aggregate -- PATIENTS with any GI "
                   "disorder, on-treatment -- is in STEP 3's Table 3 (PMC page held; excerpt committed); result-change "
                   "notice OPEN")},
    ("sglt2-ckd-progression", "Lower-limb amputation", "30990260"): {
        "before": "REFUSED_ON_EVIDENCE (absent)", "after": "POOLED",
        "values_after": {"ai": 70, "n1i": 2200, "ci": 63, "n2i": 2197},
        "reason": ("the refusal was true of the abstract ('no significant differences in rates of amputation', no counts); the "
                   "counts are in CREDENCE's own Table (accepted manuscript held; excerpt committed), ON-STUDY window (all "
                   "treated patients through the end of the trial), unlike its on-treatment safety events; result-change "
                   "notice OPEN")},
}


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
        dk = ("decision", "rule_id", "reason")

        def other(rid):
            # EVERY other field that differs, named with its before and after value (a bare 'changed' flag would let any
            # field move unseen once a row is declared); tests/test_hm3_pages.py requires exactly these
            ks = sorted((set(b[rid]) | set(a[rid])) - set(dk))
            return {k: [b[rid].get(k), a[rid].get(k)] for k in ks if b[rid].get(k) != a[rid].get(k)}
        changed = {rid: {"before": {k: b[rid].get(k) for k in dk},
                         "after": {k: a[rid].get(k) for k in dk},
                         "other_fields_unchanged": not other(rid),
                         **({"other_fields_changed": other(rid)} if other(rid) else {})}
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
        superseded = {f"{o}|{t}": v for (sl, o, t), v in HARM_DECISIONS_SUPERSEDED.items() if sl == slug}
        if changed or harms or superseded:
            pages[slug] = {"screening_rows_changed": changed, "added_keys": list(ADDED_KEYS),
                           "harms_incomplete_by_entered_reports": harms,
                           **({"harm_decisions_superseded": superseded} if superseded else {})}
    out = {"landing": LANDING, "pinned_control": "primary-baseline-f6f7b14c.json (never rewritten)",
           "reason": ("V1.0.1 screening roles: every screened report carries ONE screening record (parent eligibility, report "
                      "relevance, result admissibility); secondary reports are linked to their parent family instead of "
                      "X1 'not a randomized controlled trial'; X1 reasons name their cause; protocol/design papers are "
                      "X-NO-RESULTS. A secondary report newly screened in can make a harms outcome HARMS_INCOMPLETE when "
                      "it reports that harm and is not yet extracted. V1.0.1 acquisition cascade: platform / multi-comparison "
                      "registrations are screened per comparison (REMAP-CAP awaits classification instead of X2 on its "
                      "registration's COVID label); a decided harm row is superseded where the cascade bound the result. "
                      "Record-identity fix (2026-09-27): the registry-design merge had overwritten every registration "
                      "record's NCT id with the AACT design row id, so identity lookups failed and fell back to the row "
                      "id -- trial_family_id now follows the identity module's own key (the trial acronym where there is "
                      "one), which also re-joins a registration to its publication; registrations carry a typed lifecycle "
                      "(planned vs actual completion); a published report reads completed with results whatever its "
                      "registry status; registrations whose registry masking or dose contradicts the protocol are held "
                      "awaiting classification (A-PROTOCOL-CONFLICT)."),
           "pages": pages}
    open(os.path.join(EV, "screening_roles_supersession.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    n = sum(len(p["screening_rows_changed"]) for p in pages.values())
    print(f"pages with declared changes: {len(pages)}; screening rows changed: {n}; harms outcomes incomplete: "
          f"{sum(len(p['harms_incomplete_by_entered_reports']) for p in pages.values())}")


if __name__ == "__main__":
    main()
