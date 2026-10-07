"""EXPANDED SEARCH for the 4 topics whose blind concept query gained recall only above the original 5,000-record cap
(decision 2026-10-06, under Mahmood's delegation: cap raised to 10,000 for omega3-cardiovascular-events,
probiotics-aad-prevention, semaglutide-obesity-mace, sglt2-primary-prevention-hf).

Per topic, the accepted query is the smallest-volume blind proposal that recovered every missed eligible trial (rule
fixed before running: min volume among proposals with the maximal recall_union, volume <= 10,000). It is run in full
(harness.acquisition.esearch_all, the source's own count recorded); records NOT already held (cache/<slug>/records.json)
are fetched (harness.fetch._efetch) and screened by this branch's rule screener (harness.screen.run over
pipeline._dedup). Recall gain: which ELIGIBLE comparator trials (SEARCH_SCREEN_AUDIT.json) the expanded set newly
identifies, and how the rule screen decides them.

Committed: outputs/search_audit/expanded/<slug>.json -- query + record id of the proposal, count, every new PMID with its
held-text sha256 and rule decision (rule_id, reason, span), and the per-trial gain. The record TEXTS are kept out of the
repo (a temp directory outside the tree, env MH_EXPANDED_TEXTS; re-fetchable by PMID; each verified by its
sha256).

  python scripts/g1_expanded_search.py [SLUG ...]   (online)
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
SA = os.path.join(ROOT, "outputs", "search_audit")
OUT = os.path.join(SA, "expanded")
TEXTS = os.environ.get("MH_EXPANDED_TEXTS", os.path.join(os.path.expanduser("~"), "mh-expanded-texts"))
TOPICS = ("omega3-cardiovascular-events", "probiotics-aad-prevention", "semaglutide-obesity-mace",
          "sglt2-primary-prevention-hf")
CAP = 10000


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def chosen(slug):
    """The smallest-volume proposal with the maximal recall_union, volume <= CAP (the rule, fixed before running)."""
    c = []
    for f in ("query_audit.json", "query_audit_r2.json", "query_audit_precise.json"):
        q = (_j(os.path.join(SA, f))["topics"].get(slug) or {})
        v = q.get("validation") or {}
        if v.get("proposed_pubmed_count") and v["proposed_pubmed_count"] <= CAP:
            c.append((v["recall_union"]["n"], -v["proposed_pubmed_count"], f, q))
    best = max(c)
    return {"source": best[2], "record": best[3]["record"], "query": best[3]["proposal"]["pubmed_query"],
            "volume_at_audit": -best[1], "recall_union_at_audit": best[3]["validation"]["recall_union"],
            "recall_current_at_audit": best[3]["validation"]["recall_current"]}


def held_text(rec):
    return "\n".join(f"{lab}: {rec.get(k) if rec.get(k) not in (None, '') else '(none)'}"
                     for lab, k in (("TITLE", "title"), ("PUBLICATION TYPES", "pubtypes"), ("ABSTRACT", "abstract")))


def chosen_active(slug):
    """Active topics (7 Oct): the same rule over every recorded blind proposal RE-VALIDATED against the CURRENT comparator
    (outputs/search_audit/active/query_revalidation.json + the precise10k rounds), volume <= CAP."""
    c = []
    rv = _j(os.path.join(SA, "active", "query_revalidation.json"))["topics"].get(slug) or {}
    cands = [(p["round"], p["record"], p["query"], p["validation"]) for p in rv.get("proposals") or []]
    for tag in ("precise10k", "precise10k-b"):
        f = os.path.join(SA, f"query_audit_{tag}.json")
        q = (_j(f)["topics"].get(slug) if os.path.exists(f) else None) or {}
        if q.get("validation"):
            cands.append((tag, q["record"], q["proposal"]["pubmed_query"], q["validation"]))
    for tag, rec, query, v in cands:
        if v.get("proposed_pubmed_count") and v["proposed_pubmed_count"] <= CAP:
            c.append((v["recall_union"]["n"], -v["proposed_pubmed_count"], tag, rec, query, v))
    best = max(c, key=lambda x: (x[0], x[1]))
    return {"source": f"{best[2]} (re-validated against the current comparator)", "record": best[3], "query": best[4],
            "volume_at_audit": -best[1], "recall_union_at_audit": best[5]["recall_union"],
            "recall_current_at_audit": best[5]["recall_current"],
            "candidates": [{"round": x[2], "record": x[3], "volume": -x[1], "recall_union": x[5]["recall_union"]} for x in c],
            "over_cap": [{"round": t, "record": r, "volume": v.get("proposed_pubmed_count"), "recall_union": v["recall_union"]}
                         for t, r, _, v in cands if (v.get("proposed_pubmed_count") or 0) > CAP]}


def run(slug, active=False):
    from harness import acquisition as acq, fetch, pipeline, screen
    ch = chosen_active(slug) if active else chosen(slug)
    res = acq.esearch_all(ch["query"], sleep=0.34)
    ids = [str(x) for x in res.get("ids") or []]
    have = {str(r["id"]) for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records") or []}
    new = [p for p in ids if p not in have]
    os.makedirs(TEXTS, exist_ok=True)
    tp = os.path.join(TEXTS, f"{slug}.records.json")
    cached = {str(r["id"]): r for r in (_j(tp) if os.path.exists(tp) else [])}
    todo = [p for p in new if p not in cached]
    for i in range(0, len(todo), 200):
        for r in fetch._efetch(todo[i:i + 200]):
            cached[str(r["id"])] = r
        print(f"  {slug}: fetched {min(i + 200, len(todo))}/{len(todo)}", flush=True)
    recs = [cached[p] for p in new if p in cached]
    json.dump(recs, open(tp, "w", encoding="utf-8"), ensure_ascii=False)
    cfg = copy.deepcopy(_j(os.path.join(ROOT, "topics", f"{slug}.json")))
    with redirect_stdout(io.StringIO()):
        merged = pipeline._dedup({"records": recs, "ctgov": []}, cfg.get("pivotal_trials"))
        dec = {str(d["id"]): d for d in screen.run(merged, cfg)["decisions"]}
    kept = {str(r["id"]) for r in merged}

    def _d(r):
        rid = str(r["id"])
        if rid in dec:
            return {k: dec[rid].get(k) for k in ("decision", "rule_id", "reason", "span")}
        if rid not in kept:   # pipeline._dedup collapsed it into the most-primary record sharing its NCT (as the pipeline does)
            return {"decision": "exclude", "rule_id": "X-DEDUP", "reason": "collapsed by pipeline._dedup into the "
                    "most-primary record sharing its NCT", "span": f"nct {r.get('nct') or '(record field)'}"}
        return {"decision": None, "rule_id": None, "reason": "NO_DECISION", "span": None}
    rows = [{"pmid": str(r["id"]), "held_sha256": hashlib.sha256(held_text(r).encode("utf-8")).hexdigest(), **_d(r)}
            for r in recs]
    not_fetched = sorted(set(new) - {str(r["id"]) for r in recs})
    src = os.path.join(SA, "active", "ACTIVE_AUDIT.json") if active else os.path.join(SA, "SEARCH_SCREEN_AUDIT.json")
    audit = next(t for t in _j(src)["topics"] if t["slug"] == slug)
    # identified by the expanded query = a PMID of the trial is among the query's HITS (held already or new); a trial
    # whose record was held only because it was hand-named is identified by this query only if the query returns it.
    # Its screen decision: this branch's rule screen for a new record; the served screen for a record already held.
    hits = set(ids)
    new_set, fetched_ids = set(new), {str(r["id"]) for r in recs}
    gain = []
    for t in audit["trials"]:
        if t["kind"] != "ELIGIBLE":
            continue
        hit = sorted(set(t["pmids"]) & hits)
        # before = identified by the search as registered NOW (active: the current registered queries, recorded probe)
        before = (t["search_current"] == "IDENTIFIED") if active else t["search"].startswith("IDENTIFIED")
        if hit or before:
            decs = []
            for p in hit:
                if p in dec:
                    decs.append({"pmid": p, "source": "rule screen (new record)", **{k: dec[p].get(k) for k in ("decision", "rule_id")}})
                elif p in new_set:
                    # a NEW record without its own decision: collapsed by dedup, or never returned by efetch. It never
                    # inherits the trial's served decision, which belongs to a record already held (codex review
                    # mc-0effd237 P1; plant tests/test_search_audit_codex_review_1006.py)
                    decs.append({"pmid": p, "source": "new record", **({"decision": "exclude", "rule_id": "X-DEDUP"}
                                 if p in fetched_ids else {"decision": None, "rule_id": "NOT_RETURNED_BY_EFETCH"})})
                else:
                    sv = (t.get("screen_include") or t.get("screen_exclusion") or {})
                    decs.append({"pmid": p, "source": "served screen (record already held)",
                                 "decision": {"INCLUDED": "include", "EXCLUDED": "exclude"}.get(t.get("screen")),
                                 "rule_id": sv.get("rule_id") or ("INCLUDE" if t.get("screen") == "INCLUDED" else None)})
            gain.append({"label": t["label"], "identified_before": before, "identified_by_expanded_query": bool(hit),
                         "newly_identified": bool(hit) and not before, "hit_pmids": hit, "screen_decisions": decs})
    n_el = sum(1 for t in audit["trials"] if t["kind"] == "ELIGIBLE")
    dec_txt = ("active topic short on search recall against its current comparator: blind query re-validated, cap 10,000 "
               "(2026-10-07, captain under Mahmood's delegation, amendment A6)" if active else
               "volume cap raised to 10,000 (2026-10-06, under Mahmood's delegation)")
    out = {"slug": slug, "decision": dec_txt, "chosen": ch,
           "esearch": {"count": res.get("count"), "ids": len(ids), "state": res.get("state"), "funnel": res.get("funnel")},
           "new_records": len(new), "fetched": len(recs), "not_returned_by_efetch": not_fetched,
           "rule_screen": {"include": sum(1 for r in rows if r["decision"] == "include"),
                           "exclude": sum(1 for r in rows if r["decision"] == "exclude" and r["rule_id"] != "X-DEDUP"),
                           "dedup_collapsed": sum(1 for r in rows if r["rule_id"] == "X-DEDUP"),
                           "no_decision": sum(1 for r in rows if r["decision"] is None)},
           "recall": {"eligible": n_el, "identified_before": sum(1 for g in gain if g["identified_before"]),
                      "newly_identified": sum(1 for g in gain if g["newly_identified"]),
                      "newly_identified_and_screen_included": sum(1 for g in gain if g["newly_identified"] and any(
                          d["decision"] == "include" for d in g["screen_decisions"])),
                      "identified_after": sum(1 for g in gain if g["identified_before"] or g["newly_identified"])},
           "trials": gain, "records": rows}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(slug, json.dumps({k: out[k] for k in ("esearch", "new_records", "rule_screen", "recall")})[:600], flush=True)


def relabel(slug):
    """Offline repair of an output written before 7 Oct: a trial hit that is a NEW record without its own rule decision
    (dedup-collapsed) had been labelled with the trial's served decision. Same rule as run(); no search re-run."""
    p = os.path.join(OUT, f"{slug}.json")
    e = _j(p)
    rows = {r["pmid"]: r for r in e["records"]}
    n = 0
    for t in e["trials"]:
        for d in t["screen_decisions"]:
            if d["source"].startswith("served") and d["pmid"] in rows:
                d.update(source="new record", decision=rows[d["pmid"]]["decision"], rule_id=rows[d["pmid"]]["rule_id"])
                n += 1
    e["recall"]["newly_identified_and_screen_included"] = sum(1 for g in e["trials"] if g["newly_identified"] and any(
        d["decision"] == "include" for d in g["screen_decisions"]))
    json.dump(e, open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(slug, "relabelled", n)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--relabel"]:
        for s in (sys.argv[2:] or TOPICS):
            relabel(s)
    elif sys.argv[1:2] == ["--active"]:
        for s in sys.argv[2:]:
            run(s, active=True)
    else:
        for s in (sys.argv[1:] or TOPICS):
            run(s)
