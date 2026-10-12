"""DEV-only evaluation of the typed RoB 2 rules against SILVER labels: the recorded dual reading (codex + agy, and the
recorded adjudicator) of DEV trials whose CC full text the readers saw. Never run on TEST (outputs/robgrade/split.json).

Per rule: fires / agrees on the side with the silver answer / disagrees (each disagreement listed with both spans).
Per question: silver answered from the FULL TEXT while no rule fired -- the recall gap, with the readers' verbatim
quotes (CC text) as the material for the next rule.

    python scripts/rob2_rule_eval.py SLUG ...   -> outputs/robgrade/dev/rule_eval.json + RULE_EVAL.md
"""
import io
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_dual as rd  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402
from robgrade import rob2_typed as rt  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "robgrade", "dev")


def silver(item, runs):
    """{qid: answer} from the recorded readings alone (agreed or adjudicated), with quotes -- never the typed layer."""
    r = runs.get(item["key"]) or {}
    a = rd.verify_answers(rd.replay(r.get("codex")), item)
    b = rd.verify_answers(rd.replay(r.get("agy")), item)
    agreed, dis = rd.agree(a, b)
    adj = rd.verify_answers(rd.replay(r.get("adjudicator")), item, allowed=set(dis)) if dis else {}
    out = {}
    for q in rf.QUESTIONS:
        x = adj.get(q) or agreed.get(q)
        if x and x["answer"] in ("Y", "PY", "PN", "N"):
            out[q] = x
    return out


def main(argv):
    split = json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))
    dev = set(split["dev"])
    runs = json.load(open(rd.RUNS, encoding="utf-8"))
    per_rule = defaultdict(Counter)
    disagreements, gaps = [], defaultdict(list)
    n_items = 0
    slugs = [a for a in argv if not a.startswith("--")]
    rd.prefetch_registry([(slug, rd.dev_pmids(slug)) for slug in slugs])
    for slug in slugs:
        pm = rd.dev_pmids(slug)
        for it in (rd.items(slug, pm) if pm else []):
            if it["pmid"] not in dev:
                raise SystemExit(f"REFUSED: PMID {it['pmid']} is not DEV")
            # the same selection as the DEV silver-label run (scripts/rob2_dual.py --dev)
            if not any(s["kind"] == "fulltext" and s["open_for_prompt"] and s.get("local_store") for s in it["sources"]):
                continue
            n_items += 1
            typed, _ = rt.typed_answers(it["sources"], it.get("machine_d5"), outcome=it.get("outcome"))
            sv = silver(it, runs)
            for q, a in typed.items():
                rid = a.get("rule_id") or a["how"]
                s = sv.get(q)
                if s is None:
                    per_rule[rid]["fires_silver_silent"] += 1
                elif rf.side(s["answer"]) == rf.side(a["answer"]):
                    per_rule[rid]["agrees"] += 1
                else:
                    per_rule[rid]["disagrees"] += 1
                    disagreements.append({"pmid": it["pmid"], "q": q, "rule": rid, "rule_answer": a["answer"],
                                          "rule_span": a.get("span"), "silver": s["answer"], "silver_quote": s["quote"]})
            for q, s in sv.items():
                if q not in typed and str(s.get("source_id", "")).startswith("fulltext"):
                    gaps[q].append({"pmid": it["pmid"], "answer": s["answer"], "quote": s["quote"]})
    os.makedirs(OUT, exist_ok=True)
    res = {"dev_items_with_open_full_text": n_items, "per_rule": {k: dict(v) for k, v in per_rule.items()},
           "disagreements": disagreements, "recall_gaps": gaps}
    with open(os.path.join(OUT, "rule_eval.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    lines = [f"# DEV rule evaluation v silver labels ({n_items} DEV trials with an open full text)", "",
             "| rule | agrees | disagrees | fires, silver silent |", "|---|---|---|---|"]
    for k, v in sorted(per_rule.items()):
        lines.append(f"| {k} | {v['agrees']} | {v['disagrees']} | {v['fires_silver_silent']} |")
    lines += ["", "Recall gaps (silver answered from full text, no rule): " +
              ", ".join(f"{q}: {len(v)}" for q, v in sorted(gaps.items()))]
    with open(os.path.join(OUT, "RULE_EVAL.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
