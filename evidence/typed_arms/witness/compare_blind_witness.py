"""PREREG addendum B: blind token-witness pass vs the first witness pass, per arm FIELD (events, total).
Value agreement: same number. Occurrence agreement: same (file, start, end). Arms matched by role.
usage: python compare_blind_witness.py <first packets dir> <blind packets dir>  -> witness/BLIND_WITNESS_COMPARISON.json"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_witness as cw  # noqa: E402

first_dir, blind_dir = sys.argv[1:3]
rows, n, val, occ = [], 0, 0, 0
for j in sorted(os.listdir(first_dir)):
    a, b = cw.check_job(os.path.join(first_dir, j)), cw.check_job(os.path.join(blind_dir, j))
    fa = {x["role"]: x for x in a["arms"]}
    fb = {x["role"]: x for x in b["arms"]}
    fields = []
    for role in ("intervention", "comparator"):
        for fld, wk in (("events", "event_witness"), ("total", "total_witness")):
            x, y = fa.get(role) or {}, fb.get(role) or {}
            if x.get(fld) is None:
                continue
            n += 1
            same_v = y.get(fld) == x.get(fld)
            wx, wy = x.get(wk) or {}, y.get(wk) or {}
            same_o = bool(wx) and bool(wy) and (wx["file"], wx["start"], wx["end"]) == (wy["file"], wy["start"], wy["end"])
            val += same_v
            occ += same_o
            fields.append({"field": f"{role}.{fld}", "first": x.get(fld), "blind": y.get(fld),
                           "same_value": same_v, "same_occurrence": same_o,
                           "first_file": wx.get("file"), "blind_file": wy.get("file")})
    rows.append({"job": j, "first_state": a["state"], "blind_state": b["state"],
                 "first_source": a.get("ownership_source"), "blind_source": b.get("ownership_source"),
                 "fields": fields, "blind_notes": (b.get("notes") or "")[:600]})
out = {"prereg": "PREREG_blind_reextraction.md addendum B", "N_fields": n, "same_value": val, "same_occurrence": occ, "rows": rows}
json.dump(out, open(os.path.join(HERE, "BLIND_WITNESS_COMPARISON.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(f"fields {n}: same value {val}, same occurrence {occ}")
for r in rows:
    bad = [f for f in r["fields"] if not f["same_value"]]
    if bad:
        print(" ", r["job"][3:50], r["first_state"], "->", r["blind_state"], r["first_source"], "/", r["blind_source"],
              [(f["field"], f["first"], f["blind"]) for f in bad])
