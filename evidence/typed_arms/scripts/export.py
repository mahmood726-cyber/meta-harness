"""evidence/typed_arms/TYPED_ARMS.json -- the consumable form for the main lane's code: one entry per BOUND served count
row, keyed by (slug, outcome_index, trial_index) and the served row's sha256 (so a consumer can refuse an entry whose
served row has since changed), with {arm_id, f4b_slot, events, total} per arm plus the evidence that binds each number.
SET_ASIDE rows are listed with their reasons and NO arms: a consumer must never type them."""
import glob, json, os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pop = json.load(open(os.path.join(BASE, "population.json"), encoding="utf-8"))
bound, aside = [], []
for p in sorted(glob.glob(os.path.join(BASE, "records", "*.json"))):
    r = json.load(open(p, encoding="utf-8"))
    key = {"slug": r["slug"], "outcome_index": r["outcome_index"], "trial_index": r["trial_index"],
           "outcome_name": r["outcome_name"], "trial_id": r["trial_id"], "served_row_sha256": r["served_row_sha256"]}
    if r["state"] != "BOUND":
        aside.append({**key, "state": r["state"], "reasons": r["reasons"]})
        continue
    arms = []
    for a in sorted(r["arm_observations"], key=lambda a: a["f4b_slot"]):
        def ev(s):
            return {"document": s["document"], "document_sha256": s["document_sha256"], "start": s["start"],
                    "end": s["end"], "text": s["text"]} if s else None
        arms.append({"arm_id": a["arm_id"], "arm_id_basis": a["arm_id_basis"], "arm_label": a["arm_label"],
                     "f4b_slot": a["f4b_slot"], "events": a["events"], "total": a["total"],
                     "total_basis": a["total_basis"], "events_ownership": a["events_ownership"],
                     "total_ownership": a["total_ownership"], "events_evidence": ev(a["events_span"]),
                     "total_evidence": ev(a["total_span"])})
    bound.append({**key, "comparator_direction": r["comparator_direction"], "arms": arms,
                  "outcome_evidence": (r["arm_observations"][0].get("outcome") or {}),
                  "population_evidence": (r["arm_observations"][0].get("population") or {}),
                  "window_evidence": (r["arm_observations"][0].get("window") or {})})
out = {"schema": "evid2.typed_arms/1", "served_ref": pop["ref"], "N": pop["n"], "bound": len(bound), "set_aside": len(aside),
       "f4b_mapping": {"ai/n1i": "experimental arm (events, total)", "ci/n2i": "comparator arm (events, total)"},
       "note": ("The main lane's typed {arm_id, events, total} schema was on no pushed branch when this was built. Each arm "
                "names its F4B slot, so an entry maps onto that shape by (f4b_slot -> slot) without re-extraction. A "
                "consumer must compare served_row_sha256 with the row it is typing and refuse on mismatch."),
       "rows": bound, "set_aside_rows": aside}
json.dump(out, open(os.path.join(BASE, "TYPED_ARMS.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(len(bound), "bound;", len(aside), "set aside")
