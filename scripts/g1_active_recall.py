"""SEARCH + SCREEN RECALL of the ACTIVE G1 topics against their CURRENT comparators (V8 adoptions included), 7 Oct.

Active = the G1 topics neither G1_MATCHED nor abandoned under the pre-registered rule G1-ABANDON-v1
(outputs/k_gap/g1_abandon_rank.json, Mahmood 6 Oct "abandon the ten most unworkable topics"); derived, never listed.
Comparator = the tracker row set outputs/k_gap/g1/<slug>.json on this branch (V8: statins 32529863, melatonin 35691474,
denosumab 32492050 adopted 5-6 Oct).

Per eligible comparator trial (kinds enumerated as in g1_search_screen_audit: ELIGIBLE / SCREEN_NAMED / NAMED_OTHER):
  search_served    the served retrieval (cache/<slug>/records.json) identifies a record of the trial (forced ids excluded)
  search_current   the CURRENT registered PubMed queries (topics/<slug>.json, every dated amendment included) return a
                   PMID of the trial -- measured by a recorded esearch probe of each query (count, sha256 of the full id
                   list, the trial hits); --probe runs it
  screen           the served screen decision where the served retrieval held the record; otherwise this branch's rule
                   screener on the held record (cache) or on the record fetched by PMID for this audit (abstract only:
                   PubMed metadata, licence-safe; the texts stay outside the tree, env MH_ACTIVE_TEXTS)

  python scripts/g1_active_recall.py [--probe]   -> outputs/search_audit/active/ACTIVE_AUDIT.json (+ .md, probe json)
The ACTIVE_AUDIT.json rows carry the same fields as SEARCH_SCREEN_AUDIT.json, so the dual Codex review
(g1_screen_dual_codex.py --audit ...) reads them unchanged.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_search_screen_audit as A  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "search_audit", "active")
PROBE = os.path.join(OUT, "current_query_probe.json")
TEXTS = os.environ.get("MH_ACTIVE_TEXTS", os.path.join(os.path.expanduser("~"), "mh-active-texts"))


def active_topics():
    """Every G1 tracker topic that is neither G1_MATCHED nor in the abandon list (both read from committed artefacts)."""
    ab = A._j(os.path.join(ROOT, "outputs", "k_gap", "g1_abandon_rank.json"))
    abandoned = set(ab["abandon"])
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1"))):
        if not f.endswith(".json"):
            continue
        g = A._j(os.path.join(ROOT, "outputs", "k_gap", "g1", f))
        if g["slug"] in abandoned or (g.get("g1_status") or {}).get("state") == "G1_MATCHED":
            continue
        if not os.path.exists(os.path.join(ROOT, "docs", "reviews", g["slug"], "review.json")):
            continue
        out.append(g["slug"])
    return out, {"abandon_rule": ab.get("rule_id"), "abandon_rule_sha256": ab.get("rule_sha256"),
                 "abandoned": sorted(abandoned)}


def probe(slugs, trial_pmids):
    """Run every current registered PubMed query in full; record count, id-list sha256 and the comparator-trial hits."""
    from harness import acquisition as acq
    import datetime
    res = {}
    for s in slugs:
        cfg = A._j(os.path.join(ROOT, "topics", f"{s}.json"))
        qs, union = [], set()
        for q in cfg.get("pubmed_queries") or []:
            r = acq.esearch_all(q, sleep=0.34)
            ids = sorted(str(x) for x in r.get("ids") or [])
            union |= set(ids)
            qs.append({"query_sha256": hashlib.sha256(q.encode("utf-8")).hexdigest(), "query": q, "count": r.get("count"),
                       "n_ids": len(ids), "state": r.get("state"),
                       "ids_sha256": hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()})
        hits = {lab: sorted(set(p) & union) for lab, p in trial_pmids[s].items()}
        res[s] = {"run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "queries": qs, "union_n": len(union), "hits": hits}
        print(f"  {s}: {len(qs)} queries, union {len(union)}, trials hit "
              f"{sum(1 for v in hits.values() if v)}/{len(hits)}", flush=True)
    return res


def _texts():
    p = os.path.join(TEXTS, "records.json")
    return {str(r["id"]): r for r in (A._j(p) if os.path.exists(p) else [])}


def fetch_missing(pmids):
    """Fetch by PMID (PubMed metadata + abstract) the comparator-trial records no cache holds; kept outside the tree."""
    from harness import fetch
    have = _texts()
    todo = sorted(set(pmids) - set(have))
    for i in range(0, len(todo), 200):
        for r in fetch._efetch(todo[i:i + 200]):
            have[str(r["id"])] = r
    os.makedirs(TEXTS, exist_ok=True)
    json.dump(list(have.values()), open(os.path.join(TEXTS, "records.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return have


def _held(slug):
    rec = A._j(os.path.join(ROOT, "cache", slug, "records.json"))
    return {str(r["id"]).upper() if str(r["id"]).upper().startswith("NCT") else str(r["id"]): r
            for r in (rec.get("records") or []) + (rec.get("ctgov") or [])}


def main(argv):
    import g1_screen_dual_codex as X
    os.makedirs(OUT, exist_ok=True)
    slugs, rule = active_topics()
    acq = A.load_acq()
    with redirect_stdout(io.StringIO()):
        topics = [A.topic(s, acq) for s in slugs]
    tp = {t["slug"]: {r["label"]: r["pmids"] for r in t["trials"]} for t in topics}
    if "--probe" in argv:
        json.dump({"schema": 1, "topics": probe(slugs, tp)}, open(PROBE, "w", encoding="utf-8", newline="\n"), indent=1,
                  ensure_ascii=False)
    pr = A._j(PROBE)["topics"] if os.path.exists(PROBE) else {}
    need = sorted({p for t in topics for r in t["trials"] for p in r["pmids"]} - set().union(*(_held(s) for s in slugs)))
    extra = fetch_missing(need) if ("--probe" in argv or "--fetch" in argv) else _texts()
    for t in topics:
        held, hits = _held(t["slug"]), (pr.get(t["slug"]) or {}).get("hits") or {}
        for r in t["trials"]:
            r["search_served"] = r["search"]
            r["search_current"] = ("IDENTIFIED" if r["search"].startswith("IDENTIFIED") or hits.get(r["label"]) else
                                   "PROBE_PENDING" if t["slug"] not in pr else "NOT_IDENTIFIED")
            r["search_current_hits"] = hits.get(r["label"]) or []
            if r["screen"] in ("INCLUDED", "EXCLUDED"):
                r["screen_current"] = r["screen_branch"]
                continue
            rid = next((x for x in r["pmids"] + r["ncts"] if x in held), None) or next((x for x in r["pmids"] if x in extra), None)
            rec = held.get(rid) or extra.get(rid) if rid else None
            r["held_record"] = ({"record": rid, "where": "cache" if rid in held else "fetched for this audit (PubMed, by PMID)"}
                                if rec else None)
            d = X._branch_decision(t["slug"], rec) if rec else None
            r["screen_current"] = ("NO_HELD_RECORD" if not rec else "NO_DECISION" if not d else
                                   "INCLUDED" if d["decision"] == "include" else "EXCLUDED")
            r["screen_current_rule"] = {k: d.get(k) for k in ("rule_id", "reason", "span")} if d else None
        el = [r for r in t["trials"] if r["kind"] == "ELIGIBLE"]
        cur = [r for r in el if r["search_current"] == "IDENTIFIED"]
        t["search_recall_current"] = {"n": len(cur), "N": len(el)}
        t["screen_recall_current"] = {"n": sum(1 for r in cur if r["screen_current"] == "INCLUDED"), "N": len(cur)}
        t["screen_recall_all_eligible"] = {"n": sum(1 for r in el if r["screen_current"] == "INCLUDED"), "N": len(el),
                                           "note": "the screen on every eligible trial's held record, identified or not"}
        t["short"] = [r["label"] for r in el if r["search_current"] != "IDENTIFIED"]
    tot = lambda k: {"n": sum(t[k]["n"] for t in topics), "N": sum(t[k]["N"] for t in topics)}  # noqa: E731
    out = {"schema": 1, "active": slugs, "selection": rule,
           "inputs": {"tracker": "outputs/k_gap/g1/*.json (this branch: V8 comparators)", **acq["pins"],
                      "probe": "outputs/search_audit/active/current_query_probe.json"},
           "kinds": {k: sum(1 for t in topics for r in t["trials"] if r["kind"] == k)
                     for k in ("ELIGIBLE", "SCREEN_NAMED", "NAMED_OTHER")},
           "denominator_mismatch": [t["slug"] for t in topics if t["N_eligible"] != t["N_eligible_tracker"]],
           "totals": {k: tot(k) for k in ("search_recall", "search_recall_current", "screen_recall", "screen_recall_current",
                                          "screen_recall_all_eligible")},
           "topics": topics}
    json.dump(out, open(os.path.join(OUT, "ACTIVE_AUDIT.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    open(os.path.join(OUT, "ACTIVE_AUDIT.md"), "w", encoding="utf-8", newline="\n").write(render(out))
    print(json.dumps({k: out[k] for k in ("kinds", "denominator_mismatch", "totals")}))
    for t in topics:
        print(f"  {t['slug']}: served {t['search_recall']}, current {t['search_recall_current']}, screen "
              f"{t['screen_recall_current']}, all-eligible screen {t['screen_recall_all_eligible']['n']}/"
              f"{t['screen_recall_all_eligible']['N']}, short {t['short']}")
    return 1 if out["denominator_mismatch"] else 0


def render(o):
    L = [f"# Search + screen recall, {len(o['active'])} active G1 topics, current comparators", "",
         f"Active = not G1_MATCHED and not abandoned under {o['selection']['abandon_rule']} (rule sha256 "
         f"{str(o['selection']['abandon_rule_sha256'])[:12]}). Kinds of comparator trial: {o['kinds']}. Eligible-set "
         f"mismatch vs tracker: {o['denominator_mismatch'] or 'none'}.", "",
         f"**Totals:** search recall, served retrieval {o['totals']['search_recall']['n']}/{o['totals']['search_recall']['N']}; "
         f"current registered queries {o['totals']['search_recall_current']['n']}/{o['totals']['search_recall_current']['N']}; "
         f"screen recall of the identified {o['totals']['screen_recall_current']['n']}/{o['totals']['screen_recall_current']['N']}.",
         "", "| Topic | Comparator | Eligible | Search (served) | Search (current queries) | Screen (of identified) | "
             "Screen (all eligible, held record) | Short |", "|---|---|---|---|---|---|---|---|"]
    for t in o["topics"]:
        L.append(f"| {t['slug']} | {t['comparator_pmid']} | {t['N_eligible']} | {t['search_recall']['n']}/{t['search_recall']['N']} | "
                 f"{t['search_recall_current']['n']}/{t['search_recall_current']['N']} | "
                 f"{t['screen_recall_current']['n']}/{t['screen_recall_current']['N']} | "
                 f"{t['screen_recall_all_eligible']['n']}/{t['screen_recall_all_eligible']['N']} | {', '.join(t['short']) or '-'} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
