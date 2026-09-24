"""PREREG_blind_reextraction.md, addendum A: the same per-arm measure over the 18 held-entry extractions.
usage: python compare_blind_held.py <blind held jobs dir>   -> f4b/BLIND_COMPARISON_HELD.json"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import check_typed_arms as cta  # noqa: E402

jobs = sys.argv[1]
pop = {r["row_id"]: r for r in json.load(open(os.path.join(HERE, "held_population.json"), encoding="utf-8"))["rows"]}
rows, n, agree, unstated = [], 0, 0, 0
for f in sorted(os.listdir(os.path.join(HERE, "records"))):
    first = json.load(open(os.path.join(HERE, "records", f), encoding="utf-8"))
    r = copy.deepcopy(pop[first["row_id"]])
    r["served"] = {k: None for k in ("ai", "n1i", "ci", "n2i")}
    b = cta.check_row(r, jobs)
    by = {a["arm_id"]: a for a in b["arm_observations"] if a.get("arm_id")}
    arms = []
    for a in first["arm_observations"]:
        n += 1
        ba = by.get(a["arm_id"])
        nums = isinstance(a["events"], int) and isinstance(a["total"], int)
        same = bool(ba) and nums and (ba["events"], ba["total"]) == (a["events"], a["total"])
        agree += same
        unstated += (not nums) and (ba is None or not isinstance(ba.get("events"), int))
        arms.append({"arm_id": a["arm_id"], "first": [a["events"], a["total"]],
                     "blind": [ba["events"], ba["total"]] if ba else None, "agree": same})
    rows.append({"row_id": first["row_id"], "first_state": first["state"], "arms": arms,
                 "blind_reasons_excluding_G4_G6": [x for x in b["reasons"] if not x.startswith(("G4", "G6"))],
                 "blind_notes": b.get("extractor_notes")})
out = {"prereg": "PREREG_blind_reextraction.md addendum A", "N_rows": len(rows), "N_arms": n, "arms_agree": agree,
       "arms_neither_pass_prints_a_number": unstated, "rows": rows}
json.dump(out, open(os.path.join(HERE, "BLIND_COMPARISON_HELD.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(f"arms agree {agree} of {n}; neither pass prints a number {unstated}")
for x in rows:
    if not all(a["agree"] for a in x["arms"]):
        print(" ", x["row_id"], x["first_state"], [(a["first"], a["blind"]) for a in x["arms"]])
