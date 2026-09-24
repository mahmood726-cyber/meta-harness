"""PREREG_blind_reextraction.md, primary measure: per ARM, does the blind pass report the same (events, total) as the
first pass for the arm with the same arm_id? The blind output goes through the same gate (G1-G3, G5, G7); G4 and G6
read the served slots and are NOT applied to it (their reasons are dropped, and named as dropped).
Output: evidence/typed_arms/BLIND_COMPARISON.json."""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import check_typed_arms as cta  # noqa: E402

blind_jobs = sys.argv[1]
pop = json.load(open(os.path.join(BASE, "population.json"), encoding="utf-8"))
rows, arm_n, arm_agree, row_agree, arm_both_unstated = [], 0, 0, 0, 0
for r in pop["rows"]:
    first = json.load(open(os.path.join(BASE, "records", r["row_id"] + ".json"), encoding="utf-8"))
    rb = copy.deepcopy(r)
    rb["served"] = {"ai": None, "n1i": None, "ci": None, "n2i": None}
    b = cta.check_row(rb, blind_jobs)
    b_reasons = [x for x in b["reasons"] if not x.startswith(("G4", "G6"))]
    b_by_id = {a["arm_id"]: a for a in b["arm_observations"] if a.get("arm_id")}
    arms = []
    for a in first["arm_observations"]:
        arm_n += 1
        ba = b_by_id.get(a["arm_id"])
        numbers = isinstance(a["events"], int) and isinstance(a["total"], int)
        same = bool(ba) and numbers and (ba["events"], ba["total"]) == (a["events"], a["total"])
        both_unstated = (not numbers) and (ba is None or not isinstance(ba.get("events"), int))
        arm_agree += same
        arm_both_unstated += both_unstated
        arms.append({"arm_id": a["arm_id"], "first": [a["events"], a["total"], a["total_basis"]],
                     "blind": [ba["events"], ba["total"], ba["total_basis"]] if ba else None, "agree": same,
                     "blind_events_span": (ba or {}).get("events_span", {}) and ba["events_span"]["text"][:200] if ba else None})
    both = bool(arms) and all(x["agree"] for x in arms)
    row_agree += both
    rows.append({"row_id": r["row_id"], "first_state": first["state"],
                 "blind_gate_passes_without_G4_G6": b["state"] != "NOT_EXTRACTED" and not b_reasons,
                 "blind_reasons_excluding_G4_G6": b_reasons, "arms": arms, "row_agrees": both,
                 "blind_notes": b.get("extractor_notes"), "classification": None})
out = {"prereg": "evidence/typed_arms/PREREG_blind_reextraction.md", "N_rows": len(rows), "N_arms": arm_n,
       "arms_agree": arm_agree, "rows_agree": row_agree, "arms_both_passes_find_no_printed_number": arm_both_unstated,
       "first_bound_blind_not_passing": [x["row_id"] for x in rows if x["first_state"] == "BOUND" and not x["blind_gate_passes_without_G4_G6"]],
       "first_set_aside_blind_passing": [x["row_id"] for x in rows if x["first_state"] != "BOUND" and x["blind_gate_passes_without_G4_G6"]],
       "rows": rows}
json.dump(out, open(os.path.join(BASE, "BLIND_COMPARISON.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(f"arms agree {arm_agree} of {arm_n}; rows agree {row_agree} of {len(rows)}; arms where neither pass finds a printed number {arm_both_unstated}")
print("first BOUND, blind not passing:", out["first_bound_blind_not_passing"])
print("first SET_ASIDE, blind passing:", out["first_set_aside_blind_passing"])
