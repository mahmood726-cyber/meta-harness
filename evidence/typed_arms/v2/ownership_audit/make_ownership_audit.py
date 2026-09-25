"""Ownership audit packets for every written v2 row: for each of its four witnesses, a context window of the held
document (normalized exactly as the writer reads it) with the witnessed token marked, plus the row's outcome and arm
names. The auditor never sees the other rows or any state. usage: make_ownership_audit.py <jobs_dir>"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("write_v2", os.path.join(HERE, "..", "write_v2.py"))
wv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wv)
W = 700


def window(ref, s, e):
    _, text, _ = wv.held(ref)
    assert 0 <= s < e <= len(text)
    return text[max(0, s - W):s] + "«" + text[s:e] + "»" + text[e:e + W]


def main(out):
    items = []
    for pop in ("held", "served"):
        d = json.load(open(os.path.join(HERE, "..", f"OBSERVATIONS_{pop}.json"), encoding="utf-8"))
        for key, row in sorted(d["rows"].items()):
            obs = row["observations"]
            wit = []
            for o in obs:
                for fld in ("events", "total"):
                    w = o[f"{'event' if fld == 'events' else 'total'}_witness"]
                    wit.append({"id": f"{o['role']}.{fld}", "claimed_arm": o["arm_name"], "claimed_field": fld,
                                "claimed_value": o[fld], "document_ref": w["document_ref"],
                                "context": window(w["document_ref"], w["start"], w["end"])})
            items.append({"audit_id": f"{pop}::{key}", "outcome": obs[0]["outcome"],
                          "arms": [{"role": o["role"], "arm_name": o["arm_name"]} for o in obs], "witnesses": wit})
    os.makedirs(out, exist_ok=True)
    half = (len(items) + 1) // 2
    for i, chunk in enumerate((items[:half], items[half:])):
        json.dump(chunk, open(os.path.join(out, f"batch{i + 1}.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(len(items), "rows,", sum(len(x["witnesses"]) for x in items), "witnesses")


if __name__ == "__main__":
    main(sys.argv[1])
