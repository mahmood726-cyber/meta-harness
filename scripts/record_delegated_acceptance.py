"""Write the delegated bulk acceptance for one proposal queue (reproducible_ai/delegated.py). Writes ONLY
registry/model_proposals/<task>.delegated_acceptance.json and outputs/model_source/DELEGATED_<task>.md; never touches
a queue entry or a countersignature.

  python scripts/record_delegated_acceptance.py screening          write
  python scripts/record_delegated_acceptance.py screening --check  report stale bindings, write nothing
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproducible_ai import delegated, model_source as ms  # noqa: E402


def _pilot():
    spec = importlib.util.spec_from_file_location("_pilot", ROOT / "scripts" / "model_source_pilot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def inputs(task: str):
    pilot = _pilot()
    queue = json.loads((ROOT / ms.PROPOSAL_DIR / f"{task}.json").read_text(encoding="utf-8"))
    held = {i["item_id"]: i["held_text"] for i in pilot.pilot_items(task) if "held_text" in i}
    want = {e.get("record_id") for e in queue["items"] if e.get("record_id")}
    records = {}
    for rid in want:
        p = ROOT / ms.RECORD_DIR / f"{rid}.json"
        if p.exists():
            records[rid] = ms.load_record(p)
    return queue, records, held


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = ROOT / ms.PROPOSAL_DIR / f"{a.task}.delegated_acceptance.json"
    queue, records, held = inputs(a.task)
    if a.check:
        st = delegated.stale(delegated.load(out), queue, records)
        print(f"stale bindings: {len(st)}")
        for s in st:
            print(" ", s)
        return 1 if st else 0
    doc = delegated.build(a.task, queue, records, held)
    out.write_text(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    reasons: dict[str, int] = {}
    for x in doc["not_accepted"]:
        k = x["reason"].split(":")[0]
        reasons[k] = reasons.get(k, 0) + 1
    basis: dict[str, int] = {}
    for x in doc["accepted"]:
        basis[x["basis"]] = basis.get(x["basis"], 0) + 1
    md = [f"# {delegated.STATUS} -- `{a.task}`", "",
          f"**{delegated.DISPLAY}.**", "",
          f"- authorised by: {doc['authorised_by']} ({doc['date']})",
          f"- how it reached the reviewer: {doc['how_it_reached_the_reviewer']}",
          f"- instruction text: \"{doc['instruction_text']}\"",
          f"- context: {doc['instruction_context']}",
          "- this is **not** a human countersignature and satisfies no predicate that requires one", "",
          f"Scope rule: {doc['scope_rule']}", "",
          f"**Accepted: {doc['accepted_n_of_N']}** -- " + ", ".join(f"{k} {v}" for k, v in sorted(basis.items())),
          f"**Not accepted (UNRESOLVED): {doc['not_accepted_n_of_N']}** -- "
          + ", ".join(f"{k} {v}" for k, v in sorted(reasons.items())), "",
          "Every accepted item is bound to its proposal by record id, response sha256 and rendered-block sha256 "
          f"(`{out.relative_to(ROOT).as_posix()}`); `--check` reports any binding that no longer holds.", "",
          "Accepted items whose decision differs from what the page serves (INELIGIBLE against a served inclusion) "
          "change nothing until their served impact has been shown to Mahmood: "
          "`outputs/model_source/DELEGATED_screening_SERVED_IMPACT.md`."]
    (ROOT / "outputs" / "model_source" / f"DELEGATED_{a.task}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"accepted {doc['accepted_n_of_N']} {basis}; not accepted {doc['not_accepted_n_of_N']} {reasons}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
