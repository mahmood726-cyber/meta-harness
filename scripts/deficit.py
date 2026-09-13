"""MEASURE step of the improvement loop: the deficit table.

For every topic: our pooled primary-outcome k vs the same-scope comparator's stated k, and each
declared-absent primary trial classified by the ACTIONABLE cause of non-recovery:

  AACT_COUNT_AVAILABLE  -> the trial's registered NCT has a posted outcome_measurements row that
                           matches the pooled outcome (embedding) AND is a clean participant COUNT
                           in BOTH arms AND is not a recurrent-event/composite title. This is the
                           addressable EXTRACTION lever: a general AACT-outcome_measurements pooling
                           path would recover it (verified against source before it pools).
  AACT_RATE_OR_COMPOSITE-> the NCT posts the outcome only as a rate/median, or as a composite, or a
                           recurrent-event count (guard) -> the field's wall, not addressable by us.
  NO_NCT_RESULTS        -> no NCT, or NCT has no posted results (ongoing/unpublished) -> reach, not
                           extraction; needs a registry/FDA/EMA/citation lever, not a better parser.
  NO_OUTCOME_ROW        -> NCT has results but none matches this outcome -> reach/identity.

Scope-invalid topics (comparator is a drug CLASS) report deficit=SCOPE (no valid same-scope k).
Read-only; writes docs/deficit.json. Regenerable against the committed snapshot.

  python scripts/deficit.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact, embed  # noqa: E402

_COUNT_TYPES = ("COUNT_OF_PARTICIPANTS", "NUMBER")  # NUMBER often a % -> checked against value range
_RATE_HINT = ("rate", "per 1000", "per 100", "percentage", "median", "mean", "hazard", "geometric",
              "least squares", "change", "score", "days")


def _outcome_ncts(slug):
    """Map each declared-absent PRIMARY trial -> its NCT (from the record), plus the pooled outcome
    spec keywords, so we can probe AACT for a matching clean count."""
    rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if not os.path.exists(rp):
        return None
    rev = json.load(open(rp, encoding="utf-8"))
    recs = {}
    cp = os.path.join(ROOT, "cache", slug, "records.json")
    if os.path.exists(cp):
        recs = {r["id"]: r for r in json.load(open(cp, encoding="utf-8"))["records"]}
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), None)
    if not prim:
        prim = rev.get("outcomes", [None])[0]
    return rev, recs, prim


def _classify(nct, outcome_name, snap_ncts_cache):
    """Classify what AACT holds for this NCT + outcome."""
    if not nct:
        return "NO_NCT_RESULTS", None
    rows = snap_ncts_cache.get(nct)
    if rows is None:
        return "NO_NCT_RESULTS", None  # not fetched into the per-NCT probe (see main)
    if not rows:
        return "NO_NCT_RESULTS", None
    # find the best outcome-title match by embedding
    titles = list({r["title"] for r in rows if r.get("title")})
    if not titles:
        return "NO_OUTCOME_ROW", None
    ranked = embed.rank(outcome_name, titles, allow_model=False)
    best_title, score = (ranked[0] if ranked else (None, 0.0))
    if not best_title or score < 0.45:
        return "NO_OUTCOME_ROW", {"best": best_title, "score": round(score, 3)}
    match = [r for r in rows if r.get("title") == best_title]
    tl = best_title.lower()
    recurrent = aact.is_recurrent_event_title(best_title) if hasattr(aact, "is_recurrent_event_title") else False
    if recurrent or any(h in tl for h in _RATE_HINT) or " or " in tl:
        return "AACT_RATE_OR_COMPOSITE", {"title": best_title, "score": round(score, 3)}
    # need a clean participant count in both arms
    counts = [r for r in match if (r.get("param_type") or "").upper() == "COUNT_OF_PARTICIPANTS"]
    if len(counts) >= 2:
        return "AACT_COUNT_AVAILABLE", {"title": best_title, "score": round(score, 3),
                                        "arms": len(counts)}
    return "AACT_RATE_OR_COMPOSITE", {"title": best_title, "score": round(score, 3),
                                      "note": "no participant-count param_type in both arms"}


def main(argv):
    scope = {}
    sp = os.path.join(ROOT, "docs", "scope_audit.json")
    if os.path.exists(sp):
        scope = json.load(open(sp, encoding="utf-8"))
    slugs = sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
    # First pass: collect the set of NCTs whose outcome rows we need, so AACT is scanned ONCE.
    need = {}  # slug -> list[(trial_id, nct, outcome_name)]
    meta = {}
    for slug in slugs:
        r = _outcome_ncts(slug)
        if not r:
            continue
        rev, recs, prim = r
        meta[slug] = (rev, recs, prim)
        items = []
        for a in (prim.get("declared_absent_trials", []) if prim else []):
            aid = str(a.get("id", "")).replace("PMID ", "")
            rec = recs.get(aid) or {}
            nct = rec.get("nct") or (aid if aid.upper().startswith("NCT") else None)
            items.append((a.get("id"), (nct or "").upper() or None, prim.get("name")))
        need[slug] = items
    want_ncts = {nct for items in need.values() for _, nct, _ in items if nct}
    # One scan of outcome_measurements for all wanted NCTs.
    rowmap = {n: [] for n in want_ncts}
    if want_ncts:
        for row in aact._iter_rows(aact._table("outcome_measurements")):
            n = (row.get("nct_id") or "").upper()
            if n in rowmap:
                rowmap[n].append({"title": row.get("title"), "param_type": row.get("param_type"),
                                  "param_value": row.get("param_value")})
    out = {}
    for slug in slugs:
        if slug not in meta:
            continue
        rev, recs, prim = meta[slug]
        comp = rev.get("comparator") or {}
        ov = comp.get("overlap") or {}
        sc = (comp.get("scope") or {})
        suppressed = bool((prim or {}).get("result", {}).get("suppressed_incompatible"))
        our_k = len(prim.get("trials", []) or []) if prim else 0
        theirs_k = ov.get("theirs_k")
        scope_valid = sc.get("scope_valid", True)
        classes = {}
        for tid, nct, oname in need.get(slug, []):
            cls, info = _classify(nct, oname or "", rowmap)
            classes[str(tid)] = {"nct": nct, "class": cls, "info": info}
        # A suppressed-incompatible primary is not pooled, so a deficit vs the comparator k is undefined:
        # its extractable trials exist but are shown individually, not pooled. Report SUPPRESSED, not a k.
        deficit = (theirs_k - our_k) if (isinstance(theirs_k, int) and scope_valid and not suppressed) else None
        out[slug] = {
            "our_k": "suppressed" if suppressed else our_k, "theirs_k": theirs_k, "scope_valid": scope_valid,
            "deficit": "SUPPRESSED" if suppressed else (deficit if scope_valid else "SCOPE"),
            "primary_outcome": prim.get("name") if prim else None,
            "declared_absent": len(need.get(slug, [])),
            "absent_classes": classes,
            "addressable_extraction": [t for t, v in classes.items() if v["class"] == "AACT_COUNT_AVAILABLE"],
        }
    json.dump(out, open(os.path.join(ROOT, "docs", "deficit.json"), "w", encoding="utf-8", newline=""),
              indent=1, ensure_ascii=False)
    # print table sorted by scope-valid deficit desc
    print(f"{'topic':42} {'our_k':5} {'their_k':7} {'deficit':8} {'absent':6} addressable_AACT_counts")
    def _key(kv):
        d = kv[1]["deficit"]
        return (-d if isinstance(d, int) else 999) if d != "SCOPE" else 1000
    for slug, d in sorted(out.items(), key=_key):
        addr = d["addressable_extraction"]
        print(f"{slug:42} {d['our_k']:<5} {str(d['theirs_k']):7} {str(d['deficit']):8} "
              f"{d['declared_absent']:<6} {addr if addr else ''}")
    tot_addr = sum(len(d["addressable_extraction"]) for d in out.values())
    print(f"\nADDRESSABLE extraction candidates (clean AACT counts, not pooled): {tot_addr}")
    for slug, d in out.items():
        for t in d["addressable_extraction"]:
            print(f"  {slug}  {t}  {d['absent_classes'][t]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
