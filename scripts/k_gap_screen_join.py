"""Join the k-gap SCREEN_OR_ELIGIBILITY rows (comparator trials our screener EXCLUDED from a corpus we already hold)
to the model readings the repo already recorded for those exclusions (registry/model_proposals/screening_excluded*.json,
produced by scripts/model_source_pilot.py and gated by reproducible_ai.model_source.verify_screening). No new model
calls: this reuses recorded, verified proposals and says, per comparator trial, whether the reader agreed.

    python scripts/k_gap_screen_join.py   -> outputs/k_gap/screen_join.json
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap")
PROPS = ("screening_excluded", "screening_excluded_x1", "screening_excluded_reader2", "screening_excluded_x1_reader2")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    by_item = {}
    for task in PROPS:
        p = os.path.join(ROOT, "registry", "model_proposals", task + ".json")
        if not os.path.exists(p):
            continue
        for it in _j(p).get("items", []):
            v = it.get("verification") or {}
            by_item.setdefault(it.get("item_id"), []).append(
                {"task": task, "state": v.get("state"), "agreement": v.get("agreement"),
                 "model_decision": v.get("model_decision"), "rule_id": (it.get("context") or {}).get("rule_id")})
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    rows = [r for r in t["trials"] if r["gap_class"] == "SCREEN_OR_ELIGIBILITY" and r["unit_source"] != "REFERENCE_SEED"]
    out, tally = [], Counter()
    for r in rows:
        hits = []
        for pm in r["pmids"]:
            hits += by_item.get(f"{r['slug']}::pmid:{pm}", [])
        for n in r["ncts"]:
            hits += [h for k, v in by_item.items() if k.startswith(f"{r['slug']}::nct:") and n in k for h in v]
        passed = [h for h in hits if h["state"] == "VERIFIER_PASS"]
        if not passed:
            verdict = "NO_RECORDED_READING"
        elif any(str(h["agreement"]).startswith("RULE_MODEL_DISAGREE") for h in passed):
            verdict = "READER_DISAGREES_WITH_EXCLUSION"
        elif all(str(h["agreement"]).startswith("RULE_MODEL_AGREE") for h in passed):
            verdict = "READER_AGREES"
        else:
            verdict = "READER_CANNOT_TELL"
        tally[verdict] += 1
        out.append({"slug": r["slug"], "label": r["label"], "pmids": r["pmids"][:3], "ncts": r["ncts"],
                    "verdict": verdict, "readings": passed[:4]})
    res = {"N": len(rows), "tally": dict(tally), "rows": out,
           "source": "registry/model_proposals/" + "|".join(PROPS)}
    with open(os.path.join(OUT, "screen_join.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False, sort_keys=True)
    return res


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    r = main()
    print(json.dumps({"N": r["N"], "tally": r["tally"]}, indent=1))
    for x in r["rows"]:
        if x["verdict"] == "READER_DISAGREES_WITH_EXCLUSION":
            print(x["slug"], x["label"][:40], x["pmids"], [h["agreement"][:70] for h in x["readings"]])
