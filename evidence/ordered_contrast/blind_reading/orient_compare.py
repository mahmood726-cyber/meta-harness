"""Compare the parser (both copies) with the blind reader on the 27 items; the estimate passed is the clause's own ratio value."""
import json
import re
import sys

sys.path.insert(0, "./scripts")
import contrast_order as co  # noqa: E402
import verify_bundle as vb  # noqa: E402

V = vb.contrast_vocabulary(json.load(open("./topics/glp1-ra-mace-t2d.json", encoding="utf-8")))
items = json.load(open("evidence/ordered_contrast/blind_reading/items.json", encoding="utf-8"))["items"]
reader = {a["id"]: a for a in json.load(open("evidence/ordered_contrast/blind_reading/orient_reader.json", encoding="utf-8"))["answers"]}
pre = json.load(open("evidence/ordered_contrast/blind_reading/orient_parser_prechange.json", encoding="utf-8"))
key = {k["id"]: k for k in json.load(open("evidence/ordered_contrast/blind_reading/orient_key.json", encoding="utf-8"))}


def side(name):
    return vb.side_of(name or "", V) if name else None


rows = []
for it in items:
    m = re.search(r"(?:hazard ratio|HR\])[^0-9]{0,14}(\d+\.\d+)", it["clause"])
    est = float(m.group(1)) if m else None
    a = vb.ordered_contrast(it["clause"], [est, None, None], V, None)
    b = co.ordered_contrast(it["clause"], [est, None, None], V, None)
    same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    now = a["numerator_side"] if a["state"] == "ORDERED" else None
    r = reader[it["id"]]
    r_num = side(r["numerator"]) or ("EXPERIMENTAL" if r["numerator"] is None and side(r["reference"]) == "REFERENCE" and False else None)
    pre_num = side(pre[it["id"]]["verifier"]) if pre[it["id"]]["verifier"] not in ("EXPERIMENTAL", "REFERENCE") else pre[it["id"]]["verifier"]
    rows.append({"id": it["id"], "source": key[it["id"]]["source"], "reader_numerator": r_num, "reader_confidence": r["confidence"],
                 "parser_before": pre_num, "parser_after": now, "rule_after": (a["direction_witness"] or {}).get("rule"),
                 "rate_witness": (a["rate_witness"] or {}).get("state"), "copies_identical": same,
                 "reason_after": a.get("reason")})
json.dump(rows, open("evidence/ordered_contrast/blind_reading/orient_compare.json", "w", encoding="utf-8"), indent=1)
for x in rows:
    flag = "" if x["reader_numerator"] == x["parser_after"] else "  <-- DIFFERS"
    print(x["id"], x["source"][:4], "reader", x["reader_numerator"], "| before", x["parser_before"], "| after", x["parser_after"],
          x["rule_after"], x["rate_witness"], "same" if x["copies_identical"] else "COPIES DIFFER", flag)
