"""DUAL CODEX review of the EXPANDED-search records (outputs/search_audit/expanded/<slug>.json, the 4 topics whose cap was
raised to 10,000 on 2026-10-06). Same instrument as scripts/g1_screen_dual_codex.py (reader A gpt-6-astra, reader B
gpt-5.5, adjudicator on disagreement / cannot-tell; decisions derived by verify_screening, quotes gated).

Items per topic (the set is fixed by rule before any call; the sample seed is recorded):
  RULE_INCLUDE    every new record the rule screener includes (precision of the screen's includes)
  COMPARATOR      every newly identified comparator trial screened as a NEW record (its rule decision checked)
  EXCLUDE_SAMPLE  a seeded random sample of SAMPLE_N rule-excluded new records (not dedup-collapsed): the false-exclusion
                  rate, reported with a Wilson 95% interval and an extrapolated count over all rule excludes
Reviewing every one of the ~21,000 excludes twice is ~42,000 calls; the sample measures the same quantity at a stated
precision. Stated, not hidden.

  python scripts/g1_expanded_dual_codex.py --run [--workers 5] [--shard i/n]   -> outputs/search_audit/expanded_dual_codex.json
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_screen_dual_review as D  # noqa: E402
import g1_screen_dual_codex as X  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

SA = ROOT / "outputs" / "search_audit"
EXP = SA / "expanded"
TEXTS = Path(os.environ.get("MH_EXPANDED_TEXTS", str(Path.home() / "mh-expanded-texts")))
SEED, SAMPLE_N = 20261006, 100
TOPICS = ("omega3-cardiovascular-events", "probiotics-aad-prevention", "semaglutide-obesity-mace",
          "sglt2-primary-prevention-hf")


def items():
    """(items, unreviewable). The exclude sample's population is its sampling frame -- rule excludes that are neither
    dedup-collapsed nor comparator trials (comparator trials are reviewed exhaustively and reported by name), so the
    extrapolated count is over that frame only. A selected record with no held text is listed, never dropped (codex
    review mc-0effd237 P0 / P2; plants tests/test_search_audit_codex_review_1006.py)."""
    out, missing = [], []
    for slug in TOPICS:
        e = json.load(open(EXP / f"{slug}.json", encoding="utf-8"))
        recs = {str(r["id"]): r for r in json.load(open(TEXTS / f"{slug}.records.json", encoding="utf-8"))}
        rows = {r["pmid"]: r for r in e["records"]}
        comp = {d["pmid"]: g["label"] for g in e["trials"] for d in g.get("screen_decisions") or []
                if g.get("newly_identified") and d["source"].startswith("rule screen")}
        inc = sorted(p for p, r in rows.items() if r["decision"] == "include" and p not in comp)
        exc = sorted(p for p, r in rows.items() if r["decision"] == "exclude" and r["rule_id"] != "X-DEDUP"
                     and p not in comp)
        sample = sorted(random.Random(f"{SEED}:{slug}").sample(exc, min(SAMPLE_N, len(exc))))
        for kind, pids in (("RULE_INCLUDE", inc), ("COMPARATOR", sorted(comp)), ("EXCLUDE_SAMPLE", sample)):
            for p in pids:
                r, rec = rows[p], recs.get(p)
                if rec is None:
                    missing.append({"slug": slug, "record": p, "sample_kind": kind,
                                    "why": "no held text for this PMID (expanded-search text store)"})
                    continue
                ht = D.P.held_text_screening(rec)
                out.append({"slug": slug, "sample_kind": kind, "label": comp.get(p, f"pmid {p}"), "record": p,
                            "rule_decision": r["decision"], "rule": {k: r.get(k) for k in ("rule_id", "reason", "span")},
                            "item_id": f"{slug}::expanded::{p}", "held_text": ht, "held_sha256": D._sha(ht.encode("utf-8")),
                            "held_ref": f"pubmed:{p} (expanded search 2026-10-06; text sha256 {r['held_sha256'][:12]})",
                            "n_excludes_total": len(exc)})
    return out, missing


def adjudication_counts(need):
    """Adjudications NEEDED (readers disagree or cannot tell), COMPLETED (a recorded adjudicator verdict) and PENDING."""
    done = sum(1 for r in need if r.get("adjudicator"))
    return {"needed": len(need), "completed": done, "pending": len(need) - done}


def wilson(k, n, z=1.959964):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


def main(argv):
    live = "--run" in argv
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 5
    shard = argv[argv.index("--shard") + 1] if "--shard" in argv else None
    its, missing = items()
    if shard:
        i, n = map(int, shard.split("/"))
        its = its[i::n]
        missing = missing[i::n]
    have, known = D._have()
    if live:
        todo = [(pb, dg, m, f"G1 expanded-search dual codex, {tag}, {it['item_id']}", None)
                for it in its for (pb, dg), m, tag in ((X.prompt_a(it), X.MODEL_A, "reader A"), (X.prompt_b(it), X.MODEL_B, "reader B"))
                if D._sha(pb) not in have]
        print(f"readers: {len(todo)} calls for {len(its)} items", flush=True)
        X._run_batch(todo, workers, known)
        have, known = D._have()
    rows = []
    for it in its:
        row = {k: it[k] for k in ("slug", "sample_kind", "label", "record", "rule_decision", "rule", "item_id", "held_ref",
                                  "held_sha256", "n_excludes_total")}
        for tag, (pb, _) in (("A", X.prompt_a(it)), ("B", X.prompt_b(it))):
            hr = have.get(D._sha(pb))
            if hr:
                c = D._claim(hr[1])
                row[f"reader_{tag}"] = {"record": hr[0], "claim": c, "v": ms.verify_screening(c, it["held_text"], it["rule_decision"])}
        rows.append(row)
    byid = {x["item_id"]: x for x in its}
    need = [r for r in rows if r.get("reader_A") and r.get("reader_B") and (
        r["reader_A"]["v"].get("model_decision") != r["reader_B"]["v"].get("model_decision")
        or "CANNOT_TELL" in (r["reader_A"]["v"].get("model_decision"), r["reader_B"]["v"].get("model_decision")))]
    if live and need:
        todo = []
        for r in need:
            pb, dg = X.adj_prompt(byid[r["item_id"]], r["reader_A"]["claim"], r["reader_B"]["claim"])
            if D._sha(pb) not in have:
                todo.append((pb, dg, X.MODEL_ADJ, f"G1 expanded-search dual codex, adjudicator, {r['item_id']}", "high"))
        print(f"adjudicator: {len(todo)} of {len(need)}", flush=True)
        X._run_batch(todo, workers, known)
        have, known = D._have()
    for r in need:
        pb, _ = X.adj_prompt(byid[r["item_id"]], r["reader_A"]["claim"], r["reader_B"]["claim"])
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
    summ = {}
    for slug in TOPICS:
        R = [r for r in rows if r["slug"] == slug and r.get("final")]
        inc = [r for r in R if r["sample_kind"] == "RULE_INCLUDE"]
        ex = [r for r in R if r["sample_kind"] == "EXCLUDE_SAMPLE"]
        exd = [r for r in ex if r["final"] in ("ELIGIBLE", "INELIGIBLE")]
        fe = sum(1 for r in exd if r["final"] == "ELIGIBLE")
        ntot = (ex[0]["n_excludes_total"] if ex else 0)
        rate = (fe / len(exd)) if exd else None
        summ[slug] = {
            "rule_includes_reviewed": len(inc),
            "rule_includes_final": {k: sum(1 for r in inc if r["final"] == k) for k in ("ELIGIBLE", "INELIGIBLE", "UNRESOLVED")},
            "exclude_sample": {"n": len(ex), "decided": len(exd), "false_exclusions": fe, "rate": None if rate is None else round(rate, 4),
                               "wilson95": wilson(fe, len(exd)), "excludes_total": ntot,
                               "extrapolated_false_exclusions": None if rate is None else round(rate * ntot, 1)},
            "comparator_trials": [{"label": r["label"], "rule": r["rule"].get("rule_id"), "final": r["final"]}
                                  for r in R if r["sample_kind"] == "COMPARATOR"],
            "unreviewable": sum(1 for m in missing if m["slug"] == slug),
            "kappa_A_vs_B": X.kappa([(r["reader_A"]["v"].get("model_decision"), r["reader_B"]["v"].get("model_decision")) for r in R]),
        }
    out = {"schema": 1, "seed": SEED, "sample_n": SAMPLE_N, "models": {"reader_A": X.MODEL_A, "reader_B": X.MODEL_B,
           "adjudicator": f"{X.MODEL_ADJ} (effort high)"}, "shard": shard, "n_items": len(rows),
           "n_read_by_both": sum(1 for r in rows if r.get("final")), "adjudication": adjudication_counts(need),
           "unreviewable": missing, "topics": summ, "rows": rows}
    dest = SA / ("expanded_dual_codex.json" if not shard else f"expanded_dual_codex.shard{shard.replace('/', 'of')}.json")
    json.dump(out, open(dest, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n_items", "n_read_by_both", "adjudication")}), len(missing), "unreviewable",
          json.dumps(summ)[:1500])


if __name__ == "__main__":
    main(sys.argv[1:])
