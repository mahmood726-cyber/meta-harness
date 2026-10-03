"""G1 sglt2-hfref-hosp-cvdeath: the comparator's (PMID 35112512) per-trial rows for its LVEF <=40% pool, which it prints
ONLY in Figure 2 panel A. The shared reader (scripts/k_gap_forest_plot.py) skips subgroup figures by design and read
Figure 1 (all patients, mixed LVEF -- not this topic's population), which it refused as illegible. This lane reuses
that reader's recorded call and deterministic gate UNCHANGED (imported, not edited) on the subgroup panel the
comparator's own text names as the LVEF <=40% result:

  "sub-groups of patients with LVEF <=40% (n = 9199, HR: 0.74, 95% CI: 0.68, 0.81 ...)"   -> Figure 2 (A)

Rows count only if the gate RECOMPUTES 0.74 (0.68-0.81) from them; the pooled triple must be printed verbatim in the
comparator's held text. A number never comes from the model alone.

  python scripts/g1_sglt2_forest.py --run --run-reader2    (recorded codex image calls: two independent readers)
  python scripts/g1_sglt2_forest.py          (replay + gate, offline) -> g1/data/sglt2_hfref_forest.json
"""
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_forest_plot as kfp  # noqa: E402
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
from kgap import k_gap  # noqa: E402

SLUG, PMID = "sglt2-hfref-hosp-cvdeath", "35112512"
OUT = os.path.join(ROOT, "g1", "data", "sglt2_hfref_forest.json")
# the subgroup whose subtotal the reader must transcribe -- the comparator's own words for the topic population
SUBGROUP_RE = re.compile(r"stratified by \(A\) LVEF", re.I)
PANEL_EXTRA = ("\nTranscribe ONLY panel (A) (stratified by LVEF at baseline), and within it ONLY the subgroup of "
               "patients with LVEF <= 40% (reduced ejection fraction): its study rows and its SUBTOTAL row as the pooled "
               "row. Ignore the LVEF > 40% subgroup, any overall row, the test for subgroup differences, and panel (B).\n")
# attempt 2 (attempt 1 is kept on record under earlier_attempts): attempt 1's two readers disagreed on the subtotal row
# and one transcribed the log[Hazard Ratio] and SE columns into the HR fields -- the columns are now named
PANEL_EXTRA_2 = PANEL_EXTRA + (
    "The panel prints several numeric columns (e.g. log[Hazard Ratio], SE, Weight, and 'Hazard Ratio ... 95% CI'). "
    "effect/lower/upper must come ONLY from the 'Hazard Ratio ... 95% CI' column (values like 0.75 [0.65, 0.85]); "
    "never from log[Hazard Ratio] or SE. The pooled row is the 'Subtotal (95% CI)' row of the LVEF <= 40% subgroup, "
    "from that same column, digit by digit as printed.\n")
ATTEMPT = 2


# the comparator's LVEF <=40% result, PRINTED in its own text -- the gate's anchor (the number comes from the text)
TEXT_POOL = re.compile(r"LVEF\s*≤40%\s*\(\s*n\s*=\s*9199,\s*HR:\s*(0\.74),\s*95%\s*CI:\s*(0\.68),\s*(0\.81)")


def text_pool():
    t = k_gap.held_text(SLUG)[0]
    ms_ = [m for m in TEXT_POOL.finditer(t)]
    if not ms_:
        return None
    m = ms_[0]
    return {"effect": m.group(1), "lower": m.group(2), "upper": m.group(3), "k": None, "method": None,
            "quote": t[max(0, m.start() - 40): m.end() + 20], "n_printed": len(ms_),
            "anchored_by": "the comparator's held text, LVEF <=40% subgroup sentence"}


def figure():
    jp = os.path.join(kfp.COMP, PMID, "2026-09-28_kgap_jats.xml")
    hits = []
    for f in ET.parse(jp).getroot().iter("fig"):
        cap = " ".join("".join(x.itertext()) for x in f.iter("caption"))
        g = f.find(".//graphic")
        if g is not None and SUBGROUP_RE.search(cap):
            hits.append({"fig_id": f.get("id"), "href": g.get(kfp.XL), "caption": re.sub(r"\s+", " ", cap).strip()[:300],
                         "panel": "A", "panel_title": "LVEF at baseline, subgroup LVEF <= 40%"})
    if len(hits) != 1:
        raise SystemExit(f"REFUSED: {len(hits)} figures match the LVEF-stratified caption (need exactly 1)")
    return hits[0]


def item():
    _, pmid, pmcid = kfp.comparator(SLUG)
    assert pmid == PMID
    fig = figure()
    fp, b = kfp.fetch_image(pmid, pmcid, fig["href"])
    if not fp:
        raise SystemExit("REFUSED: image not fetched")
    return {"slug": SLUG, "pmid": pmid, "pmcid": pmcid, "figure": fig, "printed_pool": None, "image_path": fp,
            "image_ref": os.path.relpath(fp, ROOT).replace(os.sep, "/"), "image_sha256": hashlib.sha256(b).hexdigest()}


def prompt(it, attempt=None):
    extra = PANEL_EXTRA_2 if (attempt or ATTEMPT) == 2 else PANEL_EXTRA
    return (kfp.INSTR + f"\nFIGURE CAPTION (from the article): {it['figure']['caption']}\n" + extra).encode("utf-8")


READERS = {"run": kfp.MODEL, "run_reader2": "gpt-5.5"}   # two readers, each read gated on its own


def read(it, p, run, model, go):
    want = (hashlib.sha256(p).hexdigest(), it["image_sha256"])
    if go and not (run and run["state"] == "RAN_OK" and (run["prompt_sha256"], run["image_sha256"]) == want):
        rec = mcl.call(p, schema=kfp.SCHEMA, model=model, effort=kfp.EFFORT,
                       caller={"file": "scripts/g1_sglt2_forest.py", "line": "main",
                               "purpose": "G1 sglt2-hfref: comparator Figure 2A LVEF<=40% rows (g1/tocilizumab lane)"},
                       input_digests=[{"ref": it["image_ref"], "sha256": it["image_sha256"],
                                       "what": "comparator forest-plot figure attached with -i"}],
                       timeout_s=900, images=(it["image_path"],))
        ms.write_record(rec, kfp.REC_DIR)
        run = {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": want[0], "image_sha256": want[1],
               "model": model}
    if not run or run["state"] != "RAN_OK" or (run["prompt_sha256"], run["image_sha256"]) != want:
        res = {"state": "NO_RECORDED_CALL"}
    else:
        resp = json.loads(ms.replay(ms.load_record(os.path.join(kfp.REC_DIR, run["record_id"] + ".json"))).decode("utf-8"))
        # the plot's subtotal as READ is only a proposal; the anchor is the triple the comparator PRINTS in its text,
        # and the rows count only if pooling them reproduces that triple (G5). The read subtotal is kept and compared.
        pp = text_pool()
        g = kfp.gate(resp, pp, k_gap.held_text(SLUG)[0]) if pp else {"state": "REFUSED", "problems": ["TEXT_POOL_NOT_FOUND"]}
        g["read_subtotal"] = resp.get("pooled")
        g["read_subtotal_equals_text"] = bool(pp) and all(
            str((resp.get("pooled") or {}).get(k)) == pp[k] for k in ("effect", "lower", "upper"))
        res = {"rows_read": resp.get("rows"), "state": g["state"], "measure": resp.get("measure"), "notes": resp.get("notes"), "gate": g,
               "provenance": "FOREST_PLOT_MODEL_READ_RECOMPUTED" if g["state"] == "PASS" else None}
    return run, res


def main(argv):
    it = item()
    p = prompt(it)
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    out = {"slug": SLUG, "comparator_pmid": PMID, "figure": it["figure"], "image_ref": it["image_ref"],
           "image_sha256": it["image_sha256"], "attempt": ATTEMPT}
    # every earlier attempt stays on record, re-gated from its recorded call (a refused read is not deleted)
    out["earlier_attempts"] = prev.get("earlier_attempts") or []
    if prev.get("attempt", 1) != ATTEMPT and prev.get("run"):
        p1 = prompt(it, prev.get("attempt", 1))
        out["earlier_attempts"].append({"attempt": prev.get("attempt", 1), **{
            k: {"run": prev.get(k), "result": read(it, p1, prev.get(k), m, False)[1]} for k, m in READERS.items()}})
        prev = {}
    for key, model in READERS.items():
        go = ("--run" if key == "run" else "--" + key.replace("_", "-")) in argv
        run, res = read(it, p, prev.get(key), model, go)
        out[key], out["result" if key == "run" else "result_" + key.split("_", 1)[1]] = run, res
    passed = [k for k in ("result", "result_reader2") if (out.get(k) or {}).get("state") == "PASS"]
    rows = {k: [(r["label"], r["effect"], r["lower"], r["upper"]) for r in (out.get(k) or {}).get("rows_read") or []]
            for k in ("result", "result_reader2")}
    out["admitted"] = {"state": "PASS" if passed else "REFUSED", "by": passed,
                       "readers_rows_identical": bool(rows["result"]) and rows["result"] == rows["result_reader2"],
                       "rows": (out[passed[0]]["gate"]["rows"] if passed else [])}
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for k in ("result", "result_reader2"):
        r = out.get(k) or {}
        g = r.get("gate") or {}
        print(k, r.get("state"), g.get("problems"), "subtotal read", g.get("read_subtotal"), "rows", r.get("rows_read") and
              [(x["label"], x["effect"], x["lower"], x["upper"]) for x in r["rows_read"]], "methods", g.get("methods_reproducing"))
    print("ADMITTED:", {k: v for k, v in out["admitted"].items() if k != "rows"})


if __name__ == "__main__":
    main(sys.argv[1:])
