"""G1 READERS_DIFFER adjudication: ONE forest-plot row two earlier readings disagree on, re-read by two model FAMILIES
(codex + agy), decided by arithmetic the figure itself prints -- never by a vote.

A RevMan forest plot prints, for each study, log[Hazard Ratio] and SE beside 'Hazard Ratio IV, Random, 95% CI'; the
printed CI IS exp(logHR -/+ 1.96 SE), rounded. So the disputed limit is settled by the row's own log[HR] and SE:
  1. both readers transcribe the row's log[HR], SE, weight, footnote mark and HR (CI) (recorded calls, replayed);
  2. log[HR] and SE must agree between the readers within their printed rounding (else REFUSED, both shown);
  3. exp(logHR) and exp(logHR - 1.96 SE) must round to the UNDISPUTED printed point and lower limit (the row really is
     the row both readers mean, and the SE is read right); the disputed upper limit is exp(logHR + 1.96 SE), rounded
     to the printed precision -- RESOLVED only if that value is unambiguous at the printed rounding.
Nothing here is a pool input; the resolution is a comparator-row finding for the tracker.

    python scripts/g1_forest_adjudicate.py --run      (recorded calls)
    python scripts/g1_forest_adjudicate.py            (replay + decide, offline)
Writes outputs/k_gap/g1_readers_differ_resolutions.json.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_readers_differ_resolutions.json")
RUNS = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_adjudicate_runs.json")
Z = 1.959963984540054

# each case names the figure (by the comparator's own JATS id, image by sha256) and the ONE row in dispute, with the two
# earlier readings that differ (the tocilizumab lane's recorded readers) -- copied from their committed lane file
CASES = [{
    "case": "sglt2-hfref-hosp-cvdeath::EMPEROR-Reduced",
    "slug": "sglt2-hfref-hosp-cvdeath", "pmid": "35112512", "fig_id": "ehf213805-fig-0002",
    "image": "cache/comparators/35112512/2026-09-29_kgap_EHF2-9-942-g001.jpg",
    "image_sha256": "40be0420b97efe62bc43908ec5605fd7fb1bf73a94a84e13d53e92dc513e617c",
    "row": "EMPEROR-Reduced",
    "where": "panel (A) 'Composite of CV Death or HFH stratified by Baseline Ejection Fraction', subgroup 'EF less than "
             "40% at Baseline' (the FIRST subgroup of panel A)",
    "disputed": "upper", "undisputed": {"effect": "0.75", "lower": "0.65"},
    "earlier": {"source": "origin/g1/tocilizumab:g1/data/sglt2_hfref_forest.json",
                "reader1": {"record_id": "mc-e3d3c2290bc56088a7e27529a8c85084", "upper": "0.87", "mark": "†",
                            "weight_pct": "39.2"},
                "reader2": {"record_id": "mc-02f6f5c4425afd3a6d4ecb17f366fef9", "upper": "0.86", "mark": "‡",
                            "weight_pct": "30.7%"}},
}, {
    # IDENTITY PROBE: the same study in the OTHER panel. If a disagreeing reader's row-identity fields (footnote mark,
    # weight) and its disputed value are this row's, that reader read the wrong row -- shown, not voted
    "case": "sglt2-hfref-hosp-cvdeath::EMPEROR-Reduced::panelB-DM", "probe_for": "sglt2-hfref-hosp-cvdeath::EMPEROR-Reduced",
    "slug": "sglt2-hfref-hosp-cvdeath", "pmid": "35112512", "fig_id": "ehf213805-fig-0002",
    "image": "cache/comparators/35112512/2026-09-29_kgap_EHF2-9-942-g001.jpg",
    "image_sha256": "40be0420b97efe62bc43908ec5605fd7fb1bf73a94a84e13d53e92dc513e617c",
    "row": "EMPEROR-Reduced",
    "where": "panel (B) 'Composite of CV Death or HFH stratified by Diabetes Mellitus at Baseline', subgroup 'DM at "
             "Baseline' (the FIRST subgroup of panel B)",
}]


def identity_resolution(res):
    """A case the arithmetic leaves ambiguous is resolved when the disagreeing earlier reader's row-identity fields AND
    its disputed value are exactly those of the probe row (the same study in another panel), while both new readers
    give the disputed row's own identity and agree on its value: that reader read the wrong row."""
    for c in CASES:
        if c.get("probe_for") or c["case"] not in res:
            continue
        r = res[c["case"]]
        pr = res.get(next((p["case"] for p in CASES if p.get("probe_for") == c["case"]), ""), {})
        if r.get("state") != "REFUSED" or not any(p.startswith("UPPER_AMBIGUOUS") or p.startswith("LOWER_AMBIGUOUS")
                                                  for p in r.get("problems") or []):
            continue
        if pr.get("state") != "READ":
            # the probe row is not legible to both new readers: fall back to the disputed row's OWN identity -- a
            # reading whose footnote mark AND weight both contradict the identity two model families agree on for this
            # row is not a reading of this row (identity, never a vote on the disputed number)
            pr = {"case": "(probe illegible)", "agreed": {"footnote_mark": None, "weight_pct": None, c["disputed"]: None}}
        a, b = r.get("a") or {}, r.get("b") or {}
        mine = {k: gfr.agree_value(a.get(k), b.get(k)) for k in ("footnote_mark", "weight_pct", c["disputed"])}
        if None in mine.values():
            continue
        norm = lambda s: str(s or "").replace("%", "").strip()  # noqa: E731
        wrong, right = [], []
        for rd in ("reader1", "reader2"):
            e = c["earlier"][rd]
            is_probe = (norm(e["mark"]) == norm(pr["agreed"]["footnote_mark"]) and
                        norm(e["weight_pct"]) == norm(pr["agreed"]["weight_pct"]) and
                        e[c["disputed"]] == pr["agreed"][c["disputed"]])
            is_row = (norm(e["mark"]) == norm(mine["footnote_mark"]) and norm(e["weight_pct"]) == norm(mine["weight_pct"])
                      and e[c["disputed"]] == mine[c["disputed"]])
            not_row = norm(e["mark"]) != norm(mine["footnote_mark"]) and norm(e["weight_pct"]) != norm(mine["weight_pct"])
            (wrong if (is_probe or not_row) and not is_row else right if is_row else []).append(rd)
        if wrong and right:
            r.update(state="RESOLVED_BY_ROW_IDENTITY", resolved={c["disputed"]: mine[c["disputed"]]},
                     wrong_row_readers={w: c["earlier"][w]["record_id"] for w in wrong},
                     agrees_with={x: c["earlier"][x]["record_id"] for x in right},
                     basis=f"both new readers (codex + agy) give the disputed row as mark {mine['footnote_mark']}, weight "
                           f"{mine['weight_pct']}, {c['disputed']} {mine[c['disputed']]}; "
                           + "; ".join(f"{w} gave mark {c['earlier'][w]['mark']}, weight {c['earlier'][w]['weight_pct']} "
                                       f"(both contradict that identity: not this row)" for w in wrong)
                           + f"; identity probe {pr['case'].split('::')[-1]}: {pr.get('state', 'not legible to both')}"
                           f"; the arithmetic from the row's printed log[HR] {r.get('log_hr')} / SE {r.get('se')} admits "
                           f"{r.get('rounded', {}).get(c['disputed'])}, which contains the resolved value")
            if mine[c["disputed"]] not in (r.get("rounded") or {}).get(c["disputed"], []):
                r.update(state="REFUSED", problems=r["problems"] + ["IDENTITY_RESOLUTION_CONTRADICTS_ARITHMETIC"])
    return res

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["found", "label", "footnote_mark", "log_hr", "se", "weight_pct", "hr", "lower", "upper", "notes"],
          "properties": {"found": {"type": "boolean"}, "notes": {"type": "string"},
                         **{k: {"type": ["string", "null"]} for k in
                            ("label", "footnote_mark", "log_hr", "se", "weight_pct", "hr", "lower", "upper")}}}


def prompt_bytes(c, reader):
    where = ("The figure is the attached image." if reader == "codex" else
             "The figure is the image file image_0.jpg in the current directory: read that file and nothing else.")
    return (f"You are reading ONE row of a forest-plot figure. Transcribe what is PRINTED; do not compute, infer, round "
            f"or correct anything. Answer with ONE JSON object only, matching this JSON schema exactly:\n"
            f"{json.dumps(SCHEMA, sort_keys=True)}\n\n{where}\n"
            f"Find the study row '{c['row']}' in {c['where']}. Ignore every other panel and subgroup, even if the same "
            f"study appears there. For that ONE row give, exactly as printed: the label, its footnote mark (e.g. a dagger "
            f"or double dagger symbol), the log[Hazard Ratio] column, the SE column, the Weight column, and the hazard "
            f"ratio with its lower and upper 95% CI limits. If the row is not there or a value is not legible, set "
            f"found=false or that value to null and say why in notes.\n").encode("utf-8")


def _key(c, reader):
    return f"{c['case']}::{reader}"


def run_one(c, reader):
    from reproducible_ai import model_call_live as mcl
    p = prompt_bytes(c, reader)
    img = os.path.join(ROOT, *c["image"].split("/"))
    caller = {"file": "scripts/g1_forest_adjudicate.py", "line": f"run_one:{reader}", "lane": gfr.LANE,
              "purpose": f"G1 READERS_DIFFER adjudication ({reader}) {c['case']}"}
    dig = [{"ref": c["image"], "sha256": c["image_sha256"], "what": "comparator forest-plot figure image"}]
    rec = (mcl.call(p, schema=SCHEMA, model=gfr.CODEX_MODEL, effort="high", caller=caller, input_digests=dig,
                    timeout_s=900, images=(img,)) if reader == "codex" else
           mcl.agy_call(p, schema=SCHEMA, caller=caller, input_digests=dig, timeout_s=600, images=(img,)))
    ms.write_record(rec, gfr.REC_DIR)
    return {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": hashlib.sha256(p).hexdigest(),
            "model": rec["model"]["id_reported"], "error": rec.get("error")}


def parse(raw):
    import re
    t = raw.decode("utf-8", "replace").strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    try:
        d = json.loads(m.group(1) if m else t)
    except ValueError:
        return None
    return d if isinstance(d, dict) and all(k in d for k in SCHEMA["required"]) else None


def decide(c, a, b):
    """Two parsed readings of the disputed row -> RESOLVED (with the arithmetic) or REFUSED (with why, both shown)."""
    probs = []
    if not (a and b and a.get("found") and b.get("found")):
        return {"state": "REFUSED", "problems": ["ROW_NOT_FOUND_BY_BOTH"], "a": a, "b": b}
    vals = {}
    for k in ("log_hr", "se"):
        v = gfr.agree_value(a.get(k), b.get(k))
        if v is None or gfr._num(v) is None:
            probs.append(f"{k.upper()}_DISAGREES_OR_NOT_NUMERIC")
        vals[k] = v
    if probs:
        return {"state": "REFUSED", "problems": probs, "a": a, "b": b}
    lhr, se = gfr._num(vals["log_hr"]), gfr._num(vals["se"])
    # the row's printed log[HR] and SE are themselves rounded: carry that rounding through, so the decision is made
    # only when EVERY value consistent with the printed digits gives the same rounded limit
    hl, hs = 0.5 * 10 ** -gfr.fp._dec(vals["log_hr"]), 0.5 * 10 ** -gfr.fp._dec(vals["se"])
    corners = [(lhr + dl, se + ds) for dl in (-hl, hl) for ds in (-hs, hs)]
    dec = gfr.fp._dec(c["undisputed"]["effect"])

    def rng(f):
        xs = [f(l_, s_) for l_, s_ in corners] + [f(lhr, se)]
        return min(xs), max(xs)
    pt, lo, up = rng(lambda l_, s_: math.exp(l_)), rng(lambda l_, s_: math.exp(l_ - Z * s_)), \
        rng(lambda l_, s_: math.exp(l_ + Z * s_))
    rnd = lambda r: sorted({f"{x:.{dec}f}" for x in r})  # noqa: E731
    checks = {"effect": rnd(pt), "lower": rnd(lo), "upper": rnd(up)}
    for k in ("effect", "lower"):
        if c["undisputed"][k] not in checks[k]:
            probs.append(f"COMPUTED_{k.upper()}_{checks[k]}_NE_PRINTED_{c['undisputed'][k]}")
    if len(checks["upper"]) != 1:
        probs.append(f"UPPER_AMBIGUOUS_AT_PRINTED_ROUNDING:{checks['upper']}")
    out = {"log_hr": vals["log_hr"], "se": vals["se"], "computed": {k: [round(x, 5) for x in v] for k, v in
                                                                    (("effect", pt), ("lower", lo), ("upper", up))},
           "rounded": checks, "a": a, "b": b}
    if probs:
        return dict(out, state="REFUSED", problems=probs)
    resolved = checks["upper"][0]
    return dict(out, state="RESOLVED", problems=[], resolved={c["disputed"]: resolved},
                agrees_with={r: c["earlier"][r]["record_id"] for r in ("reader1", "reader2")
                             if c["earlier"][r][c["disputed"]] == resolved})


def main(argv):
    runs = gfr._j(RUNS) if os.path.exists(RUNS) else {}
    if "--run" in argv:
        todo = [(c, r) for c in CASES for r in ("codex", "agy")
                if (runs.get(_key(c, r)) or {}).get("state") != "RAN_OK"
                or runs[_key(c, r)]["prompt_sha256"] != hashlib.sha256(prompt_bytes(c, r)).hexdigest()]
        with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))) as ex:
            futs = {ex.submit(run_one, c, r): (c, r) for c, r in todo}
            for f in cf.as_completed(futs):
                c, r = futs[f]
                runs[_key(c, r)] = f.result()
                gfr._save(RUNS, runs)
                print(_key(c, r), runs[_key(c, r)]["state"], runs[_key(c, r)]["record_id"], flush=True)
    res = {}
    for c in CASES:
        ra, rb = runs.get(_key(c, "codex")), runs.get(_key(c, "agy"))
        if not (ra and rb and ra["state"] == rb["state"] == "RAN_OK"):
            res[c["case"]] = {"state": "NO_TWO_RECORDED_READINGS"}
            continue
        a = parse(ms.replay(ms.load_record(os.path.join(gfr.REC_DIR, ra["record_id"] + ".json"))))
        b = parse(ms.replay(ms.load_record(os.path.join(gfr.REC_DIR, rb["record_id"] + ".json"))))
        if c.get("probe_for"):
            ok = a and b and a.get("found") and b.get("found")
            agreed = {k: gfr.agree_value(a.get(k), b.get(k)) for k in ("footnote_mark", "weight_pct", "hr", "lower",
                                                                       "upper")} if ok else {}
            st = "READ" if ok and None not in agreed.values() else "REFUSED"
            res[c["case"]] = {"state": st, "agreed": agreed, "a": a, "b": b, "case": {k: c[k] for k in c if k != "image"},
                              "records": {"codex": ra["record_id"], "agy": rb["record_id"]}}
            continue
        res[c["case"]] = dict(decide(c, a, b), case={k: c[k] for k in c if k != "image"},
                              records={"codex": ra["record_id"], "agy": rb["record_id"]})
    res = identity_resolution(res)
    gfr._save(OUT, {"lane": gfr.LANE, "resolutions": res})
    print(json.dumps(res, indent=1, ensure_ascii=False)[:3000])
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
