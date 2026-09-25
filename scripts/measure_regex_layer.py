"""R2 report: per-pattern precision / recall of harness/extract.py's compiled patterns against the recorded labels in
registry/model_proposals/regex_label.json. Read-only; writes outputs/regex_layer/MEASUREMENT.json and .md.

What the numbers are, and are not:
  * The labels are model PROPOSALS (recorded, replayable, gated by regex_layer.measure.verify_label) -- NOT yet
    countersigned. Every figure below is "against recorded proposals", and says so.
  * Only VERIFIER_PASS labels are measured. Every other item of the frozen population is listed by state, so the
    denominator never shrinks silently (n measured of N frozen, per pattern).
  * Sentences are a deterministic SAMPLE per pattern: up to 15 where the pattern fires and up to 15 where only its broad
    trigger fires. Precision is measured on the FIRES sample; recall is SAMPLED recall on the sample, not population
    recall -- sentences outside both pools (no trigger word) are never examined. Pool sizes are printed beside it.

  python scripts/measure_regex_layer.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from regex_layer import measure  # noqa: E402
from regex_layer.specs import ROLES, SPECS  # noqa: E402

# default: every first-reader label (the first 15 per pool, and the deep sample 16-40); a named queue measures it alone
QUEUES = [ROOT / "registry" / "model_proposals" / f"{t}.json"
          for t in ([sys.argv[1]] if len(sys.argv) > 1 else ["regex_label", "regex_label_deep"])]
OUT = ROOT / "outputs" / "regex_layer" / ("reader2" if len(sys.argv) > 1 and "reader2" in sys.argv[1] else "")


def main() -> int:
    items = [e for qp in QUEUES if qp.exists() for e in json.loads(qp.read_text(encoding="utf-8"))["items"]]
    # a labelled item is found by the sha256 of its held sentence over EVERY held sentence -- never through today's
    # sampler, whose pools move when a pattern changes (R4 refuses fragments), which would silently drop frozen items
    by_sha = {}
    for _slug, _rid, _k, sent in measure.held_sentences():
        by_sha.setdefault(hashlib.sha256(sent.encode("utf-8")).hexdigest(), sent)
    pools = {c["pattern"]: c["pool_sizes"] for c in measure.candidates(40)}
    by_pattern: dict[str, dict] = {}
    labelled = []
    for e in items:
        sent = by_sha.get(e.get("held_sha256"))
        pat = (e.get("context") or {}).get("pattern") or e["item_id"].split("::")[0]
        row = by_pattern.setdefault(pat, {"frozen": 0, "measured": 0, "states": {}, "pools": None, "reasked": 0, "stable": 0})
        row["frozen"] += 1
        v = e.get("verification") or {}
        state = v.get("state") if e.get("status") == "PROPOSED" else e.get("status")
        if sent is None:
            state = "HELD_TEXT_MISMATCH"
        row["states"][state] = row["states"].get(state, 0) + 1
        row["pools"] = pools.get(pat)
        rq = e.get("reask")
        if isinstance(rq, dict) and rq.get("records"):
            row["reasked"] += 1
            row["stable"] += bool(rq.get("same_derived_decision"))
        if state == "VERIFIER_PASS":
            row["measured"] += 1
            labelled.append((pat, sent, e["claim"], (e.get("context") or {}).get("sample")))
    per = measure.measure([(p, s, cl) for p, s, cl, _ in labelled])
    rows = []
    for name in sorted(SPECS):
        b = by_pattern.get(name, {"frozen": 0, "measured": 0, "states": {}, "pools": None, "reasked": 0, "stable": 0})
        m = per.get(name, {})
        rows.append({"pattern": name, "kind": SPECS[name]["kind"], "role": ROLES[name], "frozen_N": b["frozen"], "measured_n": b["measured"],
                     "states": b["states"], "pools": b["pools"], "labels_stable_on_reask": f"{b['stable']} of {b['reasked']}",
                     "precision": m.get("precision", "0 of 0"), "sampled_recall": m.get("recall", "0 of 0"),
                     "fp_examples": m.get("fp_examples", []), "fn_examples": m.get("fn_examples", [])})
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"source": [q.relative_to(ROOT).as_posix() for q in QUEUES if q.exists()], "labels": "recorded model proposals, NOT countersigned",
           "patterns": len(rows), "patterns_measured": sum(1 for r in rows if r["measured_n"]), "rows": rows}
    (OUT / "MEASUREMENT.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# Regex layer R2 -- per-pattern precision / recall (harness/extract.py)", "",
          "Labels: recorded model proposals (registry/model_proposals/regex_label.json), gated by "
          "`regex_layer.measure.verify_label`; **not countersigned**. Precision on the sample where the pattern fires; "
          "recall is SAMPLED recall (sentences with no trigger word are never examined).", "",
          f"Patterns measured: {res['patterns_measured']} of {res['patterns']}.", "",
          "| pattern | kind | role in harness/ | measured of frozen | precision | sampled recall | labels stable on re-ask | pools fires / trigger-only |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        pools = f"{r['pools']['FIRES']} / {r['pools']['TRIGGER_ONLY']}" if r["pools"] else "-"
        md.append(f"| `{r['pattern']}` | {r['kind']} | {r['role']} | {r['measured_n']} of {r['frozen_N']} | {r['precision']} | "
                  f"{r['sampled_recall']} | {r['labels_stable_on_reask']} | {pools} |")
    md += ["", "Role: `dead` = no reader in harness/ (its numbers cannot move a served value); `conjunct:P` = read only "
           "together with P, so its standalone precision is not its contract.", "",
           "Unmeasured items by state (never dropped):", ""]
    for r in rows:
        other = {k: v for k, v in r["states"].items() if k != "VERIFIER_PASS"}
        if other:
            md.append(f"- `{r['pattern']}`: {other}")
    (OUT / "MEASUREMENT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"patterns measured {res['patterns_measured']} of {res['patterns']}")
    for r in rows:
        print(f"{r['pattern']:24s} {r['measured_n']:>3} of {r['frozen_N']:<3} P {r['precision']:>10}  R {r['sampled_recall']:>10}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
