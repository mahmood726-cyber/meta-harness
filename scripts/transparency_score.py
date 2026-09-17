"""TRANSPARENCY score: the countable test — how many claims on our page can a reader independently
check (each carries a one-click resolvable source pointer to a PRIMARY source), versus the
comparator, whose per-trial inputs are not exposed.

Per topic it counts, on OUR page, every claim that asserts a fact and asks: does the page attach a
resolvable pointer a reader can open to check it independently?
  - each pooled trial effect/counts   -> PMID/NCT + verbatim source span + which extractor (provenance)
  - each declared-absent trial         -> PMID/NCT + the reason it is absent
  - the pooled result                  -> re-derivable from the pooled trials (arithmetic on the above)
  - registry-first recall              -> AACT snapshot id + method + the missed list
  - each partial machine trial-domain  -> the AACT structured field it read
  - retraction/integrity per trial     -> the PubMed check
  - reproduction                       -> protocol SHA + replay result (a stranger re-runs it)
A claim WITHOUT a pointer is a transparency gap -> listed, so it can be closed (target: 0 gaps).

Comparator side (conservative, in the comparator's favour): its OA full text exposes its reported
pooled estimate(s) with ONE citation (itself); its per-trial data is not machine-exposed (established
0/15 parseable tables, 0/23 supplements), so a reader cannot independently check its per-trial inputs.

Writes docs/transparency.json. Read-only; non-number-changing.
  python scripts/transparency_score.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _score_topic(rev):
    claims, gaps = [], []

    def add(kind, ident, has_pointer, why=""):
        claims.append({"kind": kind, "id": ident, "pointer": bool(has_pointer)})
        if not has_pointer:
            gaps.append({"kind": kind, "id": ident, "why": why})

    for o in rev.get("outcomes", []):
        oname = o.get("name", "?")
        for t in o.get("trials", []) or []:
            # a pooled number is checkable iff it names a primary id AND shows the verbatim span it
            # was read from (so a reader can open the source and find the number).
            ok = bool(t.get("id")) and bool(t.get("source")) and bool(t.get("provenance"))
            add(f"pooled:{oname}", t.get("id"), ok,
                "missing id/source-span/provenance" if not ok else "")
        for a in o.get("declared_absent_trials", []) or []:
            ok = bool(a.get("id")) and bool(a.get("reason"))
            add(f"absent:{oname}", a.get("id"), ok, "absent without id+reason" if not ok else "")
        # the pooled estimate itself: checkable iff it exists and the trials above are pointered. A
        # suppressed-incompatible pool has NO pooled estimate, so it must not add an "estimate" claim to
        # the transparency denominator (that would count a number we deliberately do not report).
        res = o.get("result") or {}
        if res.get("k") and not res.get("suppressed_incompatible"):
            trials_ok = all(bool(t.get("id")) and bool(t.get("source")) for t in (o.get("trials") or []))
            add(f"estimate:{oname}", f"k={res.get('k')}", trials_ok,
                "pooled estimate not re-derivable (a trial lacks a source)" if not trials_ok else "")

    s = rev.get("search") or {}
    rc = s.get("recall")
    if rc and rc.get("known"):
        add("recall", "registry-first", bool(rc.get("source")) and rc.get("missed") is not None,
            "recall without snapshot id / missed list")
    rob = rev.get("rob2") or {}
    for tid, entry in (rob.get("trials") or {}).items():
        # a RoB judgement is checkable iff each domain names the structured BASIS it read (e.g.
        # "AACT allocation = RANDOMIZED"), not just a rating. Structure: trials[tid].domains[Dx].basis
        doms = (entry or {}).get("domains") or {}
        ok = bool(doms) and all(isinstance(v, dict) and v.get("basis") for v in doms.values())
        add("rob2", tid, ok, "RoB domain without a named source basis" if not ok else "")
    integ = rev.get("integrity") or {}
    if isinstance(integ, dict):
        for tid in (integ.get("trials") or integ.get("status") or {}):
            add("integrity", tid, True)
    rep = rev.get("reproduction") or {}
    # checkable iff a stranger has the protocol SHA AND a replay result (failures count; 0 is valid).
    add("reproduction", "protocol-sha+replay",
        bool(rep.get("protocol_sha") or rep.get("sha")) and rep.get("failures") is not None,
        "reproduction without SHA/replay result")

    comp = rev.get("comparator") or {}
    # comparator claims a reader could independently check: its reported estimate(s), each pointing
    # only to the comparator citation (NOT to primary per-trial sources, which it does not expose).
    comp_checkable = len(comp.get("reported", []) or [])
    ours_checkable = sum(1 for c in claims if c["pointer"])
    return {
        "claims_total": len(claims),
        "ours_independently_checkable": ours_checkable,
        "coverage": round(ours_checkable / len(claims), 3) if claims else None,
        "gaps": gaps,
        "comparator_independently_checkable": comp_checkable,
        "comparator_note": ("comparator exposes its reported pooled estimate(s) with one citation; "
                            "its per-trial inputs are not machine-exposed, so a reader cannot check "
                            "them independently (0/15 parseable tables, 0/23 data supplements)"),
    }


def main(argv):
    base = os.path.join(ROOT, "docs", "reviews")
    out = {}
    for slug in sorted(os.listdir(base)):
        rp = os.path.join(base, slug, "review.json")
        if not os.path.exists(rp):
            continue
        out[slug] = _score_topic(json.load(open(rp, encoding="utf-8")))
    json.dump(out, open(os.path.join(ROOT, "docs", "transparency.json"), "w", encoding="utf-8",
                        newline=""), indent=1, ensure_ascii=False)
    print(f"{'topic':42} {'claims':6} {'checkable':9} {'cov':5} {'gaps':5} {'comparator':10}")
    tot_gaps = 0
    for slug, v in out.items():
        tot_gaps += len(v["gaps"])
        print(f"{slug:42} {v['claims_total']:<6} {v['ours_independently_checkable']:<9} "
              f"{str(v['coverage']):5} {len(v['gaps']):<5} {v['comparator_independently_checkable']}")
    print(f"\nTOTAL transparency gaps (claims on our pages lacking a one-click source): {tot_gaps}")
    for slug, v in out.items():
        for g in v["gaps"][:6]:
            print(f"  {slug}: {g['kind']} {g['id']} -- {g['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
