"""RECORDED probe: what the standing REVIEW_REFERENCE_LIST route (harness.fetch.review_reference_list_sources +
COMPARATOR_REFERENCES) identifies for each G1 topic, run through the SAME harness functions the search uses.

Other metas per topic (reference_list_metas, at most 2): the non-comparator metas of registry/secondary_meta/<slug>.json
(acq/k-gap, pinned) with the most rows -- metas whose open full text the secondary-meta lane already read -- ties broken
by the higher PMID (newer). The choice is a rule, recorded per topic, and is what the dated amendment declares.

Per source: kind, query, state, funnel (the source's own hitCount, fetched, retained, cap) and the PMIDs (small; kept so
the audit's join replays offline). -> outputs/search_audit/rrl_probe.json

  python scripts/g1_rrl_probe.py [SLUG ...]   (online)
"""
from __future__ import annotations

import collections
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import fetch  # noqa: E402
import g1_search_screen_audit as A  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "search_audit", "rrl_probe.json")


def other_metas(slug, comp):
    d, sha = A._pinned(f"registry/secondary_meta/{slug}.json")
    rows = collections.Counter(str(r.get("meta_pmid")) for r in (d or {}).get("rows") or [] if r.get("meta_pmid"))
    rows.pop(str(comp), None)
    pick = sorted(rows, key=lambda m: (-rows[m], -int(m) if m.isdigit() else 0))[:2]
    return pick, {"rule": "most rows in registry/secondary_meta (acq pinned), ties -> higher PMID", "rows": dict(rows),
                  "secondary_meta_sha256": sha}


def run(fn):
    try:
        raw = fn()
    except Exception as exc:  # noqa: BLE001 -- recorded as the source's outcome
        return {"state": "RAN_ERROR", "error": f"{type(exc).__name__}: {exc}"[:300], "ids": []}
    ids, state, err, funnel, _ = fetch._coerce_source_result(raw)
    return {"state": state, "error": err, "funnel": funnel, "ids": ids}


def main(argv):
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"topics": {}}
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        slug = f[:-5]
        if not os.path.exists(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json")) or (argv and slug not in argv):
            continue
        cfg = json.load(open(os.path.join(ROOT, "topics", f), encoding="utf-8"))
        comp = str(cfg.get("comparator_pmid") or "")
        metas, why = other_metas(slug, comp)
        srcs = [("COMPARATOR_REFERENCES", f"{comp} references (PubMed elink)", lambda p=comp: fetch._refs(p),
                 "harness.fetch._refs")] if comp else []
        srcs += fetch.review_reference_list_sources(dict(cfg, reference_list_metas=metas))
        res = [dict(kind=k, query=q, adapter=ad, **run(c)) for k, q, c, ad in srcs]
        union = sorted({i for r in res for i in r["ids"]})
        prev["topics"][slug] = {"comparator_pmid": comp, "reference_list_metas": metas, "meta_choice": why,
                                "sources": res, "union_n": len(union),
                                "probed_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        print(slug, "metas", metas, "|", [(r["kind"], len(r["ids"]), (r.get("funnel") or {}).get("hits")) for r in res],
              "| union", len(union), flush=True)
    json.dump(prev, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1:])
