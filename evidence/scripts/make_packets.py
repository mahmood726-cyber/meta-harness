"""One extraction packet per worklist row: the served row, the served outcome's declared estimand, and every
source we hold for the trial rendered by textrep.render (the exact text a span will be checked against)."""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT


def sources(w):
    refs = []
    for h in w["held"]:
        p = h["path"]
        if p.endswith(".txt") or "records.json#" in p:
            refs.append(p)
    if w["pid"]:
        for p in sorted(glob.glob(os.path.join(ROOT, "evidence", "held", w["pid"], "*"))):
            refs.append(os.path.relpath(p, ROOT).replace("\\", "/"))
    ncts = {w.get("family_id"), w["trial"]} | {h.get("nct") for h in w["held"]}
    for n in sorted(x for x in ncts if x and str(x).startswith("NCT")):
        p = f"evidence/held/registry/{n}.json"
        if os.path.exists(os.path.join(ROOT, p)):
            refs.append(p)
    out = []
    for r in refs:
        try:
            out.append({"ref": r, "text": textrep.render(r)})
        except Exception as e:
            out.append({"ref": r, "render_error": repr(e)})
    return out


def main():
    wl = json.load(open(os.path.join(ROOT, "evidence", "worklist.json"), encoding="utf-8"))
    od = os.path.join(ROOT, "evidence", "packets"); os.makedirs(od, exist_ok=True)
    for w in wl["rows"]:
        rev = json.load(open(os.path.join(ROOT, f"docs/reviews/{w['slug']}/review.json"), encoding="utf-8"))
        s = w["served"][0]
        oi = int(s["json_ref"].split("/outcomes/")[1].split("/")[0])
        o = rev["outcomes"][oi]
        pk = {"key": w["key"], "slug": w["slug"], "question": rev.get("question"), "trial": w["trial"],
              "served_outcome": {k: o.get(k) for k in ("name", "estimand", "population", "timepoint", "served_estimand")},
              "served_row": s["row"], "json_ref": s["json_ref"], "sources": sources(w)}
        json.dump(pk, open(os.path.join(od, f"{w['key']}.json"), "w", encoding="utf-8"), indent=1)
    print("packets", len(wl["rows"]))


if __name__ == "__main__":
    main()
