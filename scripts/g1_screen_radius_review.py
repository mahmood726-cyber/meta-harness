"""Recorded per-record check of a screen fix's RADIUS: every record a fix flipped that the dual review did not already
cover (non-comparator records) is read by the same recorded second screener (instrument v2 of
scripts/g1_screen_dual_review.py), with the adjudicator on disagreement / cannot-tell, against the BRANCH decision.
A flip is ENDORSED when the final reading agrees with the branch decision, CONTRADICTED when it agrees with the old one.

  python scripts/g1_screen_radius_review.py --run [--workers 5]   -> outputs/search_audit/screen_radius_review.json
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_screen_dual_review as D  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

SA = ROOT / "outputs" / "search_audit"
OUT = SA / "screen_radius_review.json"
FIXES = {"A_ENROLLED_POPULATION": "screen_fix_radius_A.json", "D_CONDITION_IS_OUTCOME": "screen_fix_radius_D.json"}


def items():
    mem, _ = D._members()
    out = []
    for fix, f in FIXES.items():
        for fl in json.load(open(SA / f, encoding="utf-8"))["flips"]:
            if fl.get("endorsed") is not None:
                continue
            recs = D._records(fl["slug"])
            rec = recs.get(fl["record"]) or mem.get(fl["record"])
            if rec is None:
                continue
            ht = D.P.held_text_screening(rec)
            out.append({"fix": fix, "slug": fl["slug"], "label": f"radius:{fl['record']}", "record": fl["record"],
                        "kind": "RADIUS_FLIP", "rule_decision": fl["after"]["decision"],
                        "rule": {"rule_id": fl["after"]["rule_id"], "reason": fl["after"].get("reason")},
                        "before": fl["before"], "after": fl["after"], "item_id": f"{fl['slug']}::radius::{fl['record']}",
                        "held_text": ht, "held_sha256": D._sha(ht.encode("utf-8")),
                        "held_ref": f"cache/{fl['slug']}/records.json#{rec.get('id_type')}:{rec.get('id')}"})
    return out


def main(argv):
    live = "--run" in argv
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 5
    its = items()
    have, known = D._have()
    if live:
        todo = [(i, *D.reader_prompt(i)) for i in its]
        todo = [(i, pb, dg) for i, pb, dg in todo if D._sha(pb) not in have]
        print(f"radius reader: {len(todo)} of {len(its)}", flush=True)
        with cf.ThreadPoolExecutor(workers) as ex:
            futs = {ex.submit(D.call, pb, dg, D.READER_MODEL, f"G1 screen fix radius check, reader, {i['item_id']}"): pb
                    for i, pb, dg in todo}
            for f in cf.as_completed(futs):
                name, rec = f.result()
                known[D._sha(futs[f])] = name
        json.dump(known, open(SA / "screen_dual_review_records.json", "w", encoding="utf-8"), indent=0)
        have, known = D._have()
    rows = []
    for i in its:
        pb, _ = D.reader_prompt(i)
        hr = have.get(D._sha(pb))
        row = {k: i[k] for k in ("fix", "slug", "record", "before", "after", "item_id", "held_ref", "held_sha256")}
        if not hr:
            rows.append(dict(row, state="READER_NOT_CALLED"))
            continue
        claim = D._claim(hr[1])
        v = ms.verify_screening(claim, i["held_text"], i["rule_decision"])
        row.update(state="READ", reader_record=hr[0], reader=v, reader_claim=claim)
        if str(v.get("agreement", "")).startswith(("RULE_MODEL_DISAGREE", "MODEL_CANNOT_TELL")):
            apb, adg = D.adj_prompt(i, claim)
            ahr = have.get(D._sha(apb))
            if not ahr and live:
                name, rec = D.call(apb, adg, D.ADJ_MODEL, f"G1 screen fix radius check, adjudicator, {i['item_id']}")
                known[D._sha(apb)] = name
                json.dump(known, open(SA / "screen_dual_review_records.json", "w", encoding="utf-8"), indent=0)
                ahr = (name, rec)
            if ahr:
                row.update(adjudicator_record=ahr[0],
                           adjudicator=ms.verify_screening(D._claim(ahr[1]), i["held_text"], i["rule_decision"]))
        md = row["reader"].get("model_decision")
        bd = {"include": "ELIGIBLE", "exclude": "INELIGIBLE"}[i["rule_decision"]]
        final = md if md == bd else (row.get("adjudicator") or {}).get("model_decision")
        old = {"include": "ELIGIBLE", "exclude": "INELIGIBLE"}[i["before"]["decision"]]
        row["final"] = final
        row["verdict"] = ("ENDORSED" if final == bd and bd != old else "CONTRADICTED" if final == old and bd != old else
                          "RULE_CHANGE_ONLY" if bd == old else "UNRESOLVED")
        rows.append(row)
    tally = {}
    for r in rows:
        tally[(r["fix"], r.get("verdict") or r["state"])] = tally.get((r["fix"], r.get("verdict") or r["state"]), 0) + 1
    out = {"n": len(rows), "tally": {f"{a}:{b}": n for (a, b), n in sorted(tally.items())}, "items": rows}
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(out["tally"])


if __name__ == "__main__":
    main(sys.argv[1:])
