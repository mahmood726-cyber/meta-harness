"""Corpus n of N for round 8 (ticagrelor-ACS and tocilizumab-COVID reviews), each over the served pages at a pinned
commit (a control pinned to an immutable version, never a live ref):

  comparator_term   N = served X3 'no eligible comparator' exclusions; n = those the normalised comparator wording
                    (harness/term_normal.py) would pass
  nesting           N = comparators whose trial set or analysis rows resolve to registrations; n = those with two or
                    more rows of ONE registration, and of those, how many are a proved SUBGROUP_OF
  date_claims       N = served pages; n = pages serving a membership or uniqueness decided by a publication date
  (the D5 identity sweep is scripts/d5_identity_sweep.py)

  python scripts/round8_sweeps.py [--base SHA] [--write]  -> evidence/v101_integrated/round8_sweeps.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import comparator_nesting, date_membership, screen, term_normal  # noqa: E402

OUT = ROOT / "evidence" / "v101_integrated" / "round8_sweeps.json"


def show(base, path, as_json=True):
    try:
        b = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{base}:{path}"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    return json.loads(b.decode("utf-8")) if as_json else b.decode("utf-8")


def main(argv):
    base = argv[argv.index("--base") + 1] if "--base" in argv else "HEAD"
    slugs = sorted(p.name for p in (ROOT / "docs" / "reviews").iterdir())
    term_rows, nest_rows, date_rows = [], [], []
    for slug in slugs:
        r = show(base, f"docs/reviews/{slug}/review.json") or {}
        cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
        inc = cfg.get("include") or {}
        terms = list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])
        recs = {str(x.get("id")): x for v in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8")).values()
                if isinstance(v, list) for x in v if isinstance(x, dict)}
        for d in (r.get("screening") or {}).get("records") or []:
            if d.get("rule_id") != "X3" or not str(d.get("reason") or "").startswith("no eligible comparator"):
                continue
            rid = str(d["id"]).split("·")[-1].strip()
            rec = recs.get(rid)
            if not rec:
                continue
            raw = screen._text_raw(rec)
            flips = bool(screen._has(term_normal.comparator_text(raw, terms), terms))
            term_rows.append({"slug": slug, "id": rid, "flips": flips,
                              "matched": screen._has(term_normal.comparator_text(raw, terms), terms) if flips else None})
        # nesting over the comparator panel's trial set (every row with a PMID alias resolving to one registration)
        cp = ROOT / "cache" / slug / "comparators.json"
        panel = next(iter(json.loads(cp.read_text(encoding="utf-8"))), None) if cp.exists() else None
        if panel and panel.get("trial_set"):
            held = comparator_nesting._held_pubmed(ROOT, slug)
            by_reg = {}
            for t in panel["trial_set"]:
                regs = sorted({n for a in t.get("aliases") or [] if str(a.get("id")).isdigit()
                               for n in (held.get(str(a["id"])) or {}).get("ncts") or []})
                if len(regs) == 1:
                    by_reg.setdefault(regs[0], []).append(t["family_id"])
            multi = {k: v for k, v in by_reg.items() if len(v) > 1}
            nest_rows.append({"slug": slug, "rows_resolved": sum(len(v) for v in by_reg.values()),
                              "registrations_with_several_rows": multi})
        page = show(base, f"docs/reviews/{slug}/index.html", as_json=False) or ""
        c = date_membership.claims(page)
        date_rows.append({"slug": slug, "claims": c})
    # proved subgroup pairs: the analyses served at HEAD with a nesting object
    proved = {}
    for slug in slugs:
        rv = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        n = (rv.get("comparator") or {}).get("nesting")
        if n:
            proved[slug] = n.get("state")
    doc = {"schema": "round8-sweeps-v1", "base": base,
           "comparator_term": {"N": len(term_rows), "n_flip": sum(x["flips"] for x in term_rows),
                               "flipped": [x for x in term_rows if x["flips"]]},
           "nesting": {"N_comparators_with_resolved_rows": sum(1 for x in nest_rows if x["rows_resolved"]),
                       "n_with_rows_of_one_registration": sum(1 for x in nest_rows if x["registrations_with_several_rows"]),
                       "rows": [x for x in nest_rows if x["registrations_with_several_rows"]],
                       "analysis_nesting_state_at_head": proved},
           "date_claims": {"N_pages": len(date_rows), "n_pages_with_claims": sum(1 for x in date_rows if x["claims"]),
                           "rows": [x for x in date_rows if x["claims"]]}}
    if "--write" in argv:
        OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"comparator_term": {k: doc["comparator_term"][k] for k in ("N", "n_flip")},
                      "nesting": {k: v for k, v in doc["nesting"].items() if k != "rows"},
                      "date_claims": {k: doc["date_claims"][k] for k in ("N_pages", "n_pages_with_claims")}}))
    for x in doc["comparator_term"]["flipped"]:
        print("FLIP", x["slug"], x["id"], x["matched"])
    for x in doc["nesting"]["rows"]:
        print("NEST", x["slug"], x["registrations_with_several_rows"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
