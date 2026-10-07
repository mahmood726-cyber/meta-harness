"""DUAL CODEX SCREEN REVIEW of every screen decision on the G1 comparator trials (all 32 topics, all 348 rows):
two INDEPENDENT recorded Codex readers on different models read each trial's held record against the registered
criteria (instrument v2 of scripts/g1_screen_dual_review.py: reader prompt, per-axis schema, verify_screening quote
gate -- the decision is DERIVED, never taken from the model), and an ADJUDICATOR reads every item where the two readers
disagree or either cannot decide.

Coverage -- the kind of every comparator row is enumerated, never assumed:
  SERVED          our served screen decided a record of the trial (review.json): that decision is the rule decision
  COUNTERFACTUAL  our search never retrieved the trial; its held record (cache records, or acq member_records pinned) is
                  screened IN MEMORY by this branch's screener (harness.screen.run): what our screen WOULD decide
  NO_HELD_RECORD  no record of the trial is held (identity unresolved / not in PubMed / no member record): listed by name

Readers: A = gpt-6-astra (v2 reader, reused when already recorded), B = gpt-5.5 (independent, new); adjudicator =
gpt-6-astra at effort high with the adjudication prompt (it sees both readers' verdicts with quotes; disclosed: it shares
a model family with reader A). Agreement: Cohen's kappa A vs B (inter-reader), rule vs A, rule vs B, rule vs final.

  python scripts/g1_screen_dual_codex.py --run [--workers 5] [--shard i/n]   (live; skips items already RAN_OK)
  python scripts/g1_screen_dual_codex.py                                   (offline: re-derive from the records)
  -> outputs/search_audit/screen_dual_codex.json
"""
from __future__ import annotations

import concurrent.futures as cf
import copy
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_screen_dual_review as D  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

SA = ROOT / "outputs" / "search_audit"
OUT = SA / "screen_dual_codex.json"
MODEL_A, MODEL_B, MODEL_ADJ = "gpt-6-astra", "gpt-5.5", "gpt-6-astra"
B_HEADER = "INDEPENDENT READER. Other readers assess this record; you do not see their assessment.\n\n"


def _branch_decision(slug, rec):
    from harness import pipeline, screen
    cfg = copy.deepcopy(json.load(open(ROOT / "topics" / f"{slug}.json", encoding="utf-8")))
    with redirect_stdout(io.StringIO()):
        merged = pipeline._dedup({"records": [rec] if rec.get("id_type") == "pmid" else [],
                                  "ctgov": [rec] if rec.get("id_type") == "nct" else []}, cfg.get("pivotal_trials"))
        d = screen.run(merged, cfg)["decisions"]
    d = [x for x in d if str(x["id"]).upper() == str(rec["id"]).upper()] or d
    return d[0] if d else None


def items():
    a = json.load(open(SA / "SEARCH_SCREEN_AUDIT.json", encoding="utf-8"))
    mem, msha = D._members()
    out = []
    for t in a["topics"]:
        recs = D._records(t["slug"])
        for r in t["trials"]:
            base = {"slug": t["slug"], "label": r["label"], "trial_kind": r["kind"]}
            if r["screen"] in ("INCLUDED", "EXCLUDED"):
                if r["screen"] == "INCLUDED":
                    rid, dec, rule = r["screen_include"]["record"], "include", {"rule_id": "INCLUDE"}
                else:
                    e = r["screen_exclusion"]
                    rid, dec, rule = e["record"], "exclude", {k: e.get(k) for k in ("rule_id", "reason", "span")}
                rec, cov, where = recs.get(rid), "SERVED", f"cache/{t['slug']}/records.json"
            else:
                rid = next((x for x in r["pmids"] + r["ncts"] if x in recs), None)
                where = f"cache/{t['slug']}/records.json"
                if rid is None:
                    rid = next((x for x in r["pmids"] if x in mem), None)
                    where = f"outputs/k_gap/member_records.json@acq:{msha[:12]}"
                rec = recs.get(rid) or mem.get(rid) if rid else None
                if rec is None:
                    out.append(dict(base, coverage="NO_HELD_RECORD", pmids=r["pmids"], ncts=r["ncts"]))
                    continue
                d = _branch_decision(t["slug"], rec)
                if not d:
                    out.append(dict(base, coverage="NO_HELD_RECORD", why="screen returned no decision"))
                    continue
                cov, dec = "COUNTERFACTUAL", d["decision"]
                rule = {k: d.get(k) for k in ("rule_id", "reason", "span")}
            if rec is None:
                out.append(dict(base, coverage="NO_HELD_RECORD", record=rid))
                continue
            ht = D.P.held_text_screening(rec)
            out.append(dict(base, coverage=cov, record=rid, rule_decision=dec, rule=rule,
                            item_id=f"{t['slug']}::{r['label']}::{rid}", held_text=ht, held_sha256=D._sha(ht.encode("utf-8")),
                            held_ref=f"{where}#{rec.get('id_type')}:{rec.get('id')}"))
    return out


def prompt_a(it):
    return D.reader_prompt(it)


def prompt_b(it):
    pb, dg = D.reader_prompt(it)
    return B_HEADER.encode("utf-8") + pb[len(D.P.READER2_HEADER.encode("utf-8")):], dg


def adj_prompt(it, ca, cb):
    """Both readers' per-axis verdicts with quotes, labelled A and B (neither presumed right)."""
    def fmt(c):
        return "; ".join(f"{ax}: {v.get('verdict')}" + (f" (quote: {v.get('quote')})" if v.get("quote") else "")
                         for ax, v in ((c or {}).get("axes") or {}).items())
    crit, cd = D.criteria(it["slug"])
    body = (D.ADJ_INSTR.replace("Screener A is a rule-based screener; screener B is a reader.",
                                "Screeners A and B are two independent readers.")
            + "\n=== REGISTERED CRITERIA ===\n" + crit + "\n\n=== SCREENER A ===\n" + fmt(ca)
            + "\n\n=== SCREENER B ===\n" + fmt(cb) + f"\n\n=== RECORD item=R1 ===\n{it['held_text']}\n")
    return body.encode("utf-8"), cd + [{"ref": it["held_ref"], "sha256": it["held_sha256"], "what": "held record"}]


def _call(pb, dg, model, purpose, effort=None):
    from reproducible_ai import model_call_live
    rec = model_call_live.call(pb, schema=D.P._schema("screening"), model=model, effort=effort or D.EFFORT,
                               caller={"file": "scripts/g1_screen_dual_codex.py", "lane": "search-screen-audit",
                                       "line": "call", "purpose": purpose}, input_digests=dg)
    return ms.write_record(rec, D.REC_DIR).name, rec


def _run_batch(todo, workers, known):
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(_call, pb, dg, m, p, e): pb for pb, dg, m, p, e in todo}
        for f in cf.as_completed(futs):
            try:
                name, rec = f.result()
                if rec.get("state") == "RAN_OK":
                    known[D._sha(futs[f])] = name
                print(f"  {rec['state']} {name}", flush=True)
            except Exception as exc:  # noqa: BLE001 -- reported; the item stays uncalled
                print(f"  FAILED {exc}", flush=True)
    json.dump(known, open(SA / "screen_dual_review_records.json", "w", encoding="utf-8", newline="\n"), indent=0)


def kappa(pairs):
    return D.kappa([p for p in pairs if p[0] in ("ELIGIBLE", "INELIGIBLE") and p[1] in ("ELIGIBLE", "INELIGIBLE")])


def main(argv):
    live = "--run" in argv
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 5
    shard = argv[argv.index("--shard") + 1] if "--shard" in argv else None
    its = items()
    if shard:
        i, n = map(int, shard.split("/"))
        slugs = sorted({x["slug"] for x in its})
        mine = set(slugs[i::n])
        its = [x for x in its if x["slug"] in mine]
    callable_ = [x for x in its if "held_text" in x]
    have, known = D._have()
    if live:
        todo = []
        for it in callable_:
            for (pb, dg), m, tag in ((prompt_a(it), MODEL_A, "reader A"), (prompt_b(it), MODEL_B, "reader B")):
                if D._sha(pb) not in have:
                    todo.append((pb, dg, m, f"G1 dual codex screen review, {tag}, {it['item_id']}", None))
        print(f"readers: {len(todo)} calls for {len(callable_)} items (workers {workers})", flush=True)
        _run_batch(todo, workers, known)
        have, known = D._have()
    rows = []
    for it in its:
        row = {k: it.get(k) for k in ("slug", "label", "trial_kind", "coverage", "record", "rule_decision", "rule",
                                      "item_id", "held_ref", "held_sha256", "pmids", "ncts", "why")}
        if "held_text" not in it:
            rows.append(row)
            continue
        for tag, (pb, _) in (("A", prompt_a(it)), ("B", prompt_b(it))):
            hr = have.get(D._sha(pb))
            if hr:
                c = D._claim(hr[1])
                row[f"reader_{tag}"] = {"record": hr[0], "claim": c,
                                        "v": ms.verify_screening(c, it["held_text"], it["rule_decision"])}
        rows.append(row)
    need = [r for r in rows if r.get("reader_A") and r.get("reader_B") and (
        r["reader_A"]["v"].get("model_decision") != r["reader_B"]["v"].get("model_decision")
        or "CANNOT_TELL" in (r["reader_A"]["v"].get("model_decision"), r["reader_B"]["v"].get("model_decision")))]
    byid = {x["item_id"]: x for x in callable_}
    if live and need:
        todo = []
        for r in need:
            pb, dg = adj_prompt(byid[r["item_id"]], r["reader_A"]["claim"], r["reader_B"]["claim"])
            if D._sha(pb) not in have:
                todo.append((pb, dg, MODEL_ADJ, f"G1 dual codex screen review, adjudicator, {r['item_id']}", "high"))
        print(f"adjudicator: {len(todo)} of {len(need)}", flush=True)
        _run_batch(todo, workers, known)
        have, known = D._have()
    for r in need:
        pb, _ = adj_prompt(byid[r["item_id"]], r["reader_A"]["claim"], r["reader_B"]["claim"])
        hr = have.get(D._sha(pb))
        if hr:
            r["adjudicator"] = {"record": hr[0], "v": ms.verify_screening(D._claim(hr[1]), byid[r["item_id"]]["held_text"],
                                                                         r["rule_decision"])}
    for r in rows:
        if not (r.get("reader_A") and r.get("reader_B")):
            continue
        a, b = r["reader_A"]["v"].get("model_decision"), r["reader_B"]["v"].get("model_decision")
        adj = (r.get("adjudicator") or {}).get("v", {}).get("model_decision")
        r["final"] = a if a == b and a != "CANNOT_TELL" else (adj if adj in ("ELIGIBLE", "INELIGIBLE") else "UNRESOLVED")
        rd = {"include": "ELIGIBLE", "exclude": "INELIGIBLE"}[r["rule_decision"]]
        r["screen_error"] = ("FALSE_EXCLUSION" if rd == "INELIGIBLE" and r["final"] == "ELIGIBLE" else
                             "FALSE_INCLUSION" if rd == "ELIGIBLE" and r["final"] == "INELIGIBLE" else None)
    read = [r for r in rows if r.get("final")]
    rd = lambda r: {"include": "ELIGIBLE", "exclude": "INELIGIBLE"}[r["rule_decision"]]  # noqa: E731
    A = lambda r: r["reader_A"]["v"].get("model_decision")  # noqa: E731
    B = lambda r: r["reader_B"]["v"].get("model_decision")  # noqa: E731
    cov = {}
    for r in rows:
        cov[r["coverage"]] = cov.get(r["coverage"], 0) + 1
    out = {"schema": 1, "models": {"reader_A": MODEL_A, "reader_B": MODEL_B, "adjudicator": f"{MODEL_ADJ} (effort high)"},
           "shard": shard, "n_rows": len(rows), "coverage": cov, "n_read_by_both": len(read),
           "kappa": {"reader_A_vs_reader_B": kappa([(A(r), B(r)) for r in read]),
                     "rule_vs_reader_A": kappa([(rd(r), A(r)) for r in read]),
                     "rule_vs_reader_B": kappa([(rd(r), B(r)) for r in read]),
                     "rule_vs_final": kappa([(rd(r), r["final"]) for r in read])},
           "readers_agree": sum(1 for r in read if A(r) == B(r)), "adjudicated": len(need),
           "final": {k: sum(1 for r in read if r["final"] == k) for k in ("ELIGIBLE", "INELIGIBLE", "UNRESOLVED")},
           "screen_errors": {k: sum(1 for r in read if r["screen_error"] == k) for k in ("FALSE_EXCLUSION", "FALSE_INCLUSION")},
           "rows": rows}
    dest = OUT if not shard else SA / f"screen_dual_codex.shard{shard.replace('/', 'of')}.json"
    json.dump(out, open(dest, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n_rows", "coverage", "n_read_by_both", "kappa", "readers_agree", "adjudicated",
                                          "final", "screen_errors")}))


if __name__ == "__main__":
    main(sys.argv[1:])
