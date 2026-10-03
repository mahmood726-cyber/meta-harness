"""G1 tocilizumab: a SECOND META for the two-source rule, read from its mortality forest plot (per-trial death counts are
printed only in the figure). The meta must be open-licence and INDEPENDENT of the comparator: its JATS reference list
must not cite REACT (PMID 34228774 / doi 10.1001/jama.2021.11330) -- a meta that cites REACT may have copied REACT's
rows, and a row confirmed by REACT's own numbers would make REACT verify itself.

Each figure is read by TWO recorded codex readers (reproducible_ai.model_call_live.call, image attached). A reader's
row is admitted only through deterministic gates:
  G1 counts      events <= total in both arms, all integers
  G2 row         the row's printed RR / OR is recomputed from its own counts (within the printed rounding)
  G3 pooled      the plot's pooled triple equals the triple the meta PRINTS IN ITS TEXT (kfp.pooled_in_text)
  G4 recompute   pooling the admitted rows' printed effects (FE/DL/PM, +-HK) reproduces that printed pooled triple
and a row counts only when BOTH readers' gated rows print the same four counts. The label -> REACT trial binding is
by acronym or by first author + year against our own held report of that trial (never by numbers).

  python scripts/g1_toci_meta2_forest.py --run [PMID ...]    (recorded calls)
  python scripts/g1_toci_meta2_forest.py                     (replay + gates, offline) -> g1/data/meta2_forest.json
"""
import hashlib
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_forest_plot as kfp  # noqa: E402
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "g1", "data", "meta2_forest.json")
REACT_IDS = ("34228774", "10.1001/jama.2021.11330")
# candidate second metas: open licence, REACT-independent (checked below from the held JATS), a single-panel
# all-cause mortality forest plot of RCTs, pooled value printed in the text
METAS = {
    "35657993": {"pmcid": "PMC9165853", "href": "pone.0269368.g002.jpg",
                 "why": "PLoS One 2022, CC BY 4.0: 'Effect of tocilizumab on all-cause mortality in RCTs and IPTW cohort "
                        "studies'; RCT subgroup printed in text"},
    "36102463": {"pmcid": "PMC10005468", "href": "1806-9460-1516-3180-2022-0170-R1-01072022-gf03.jpg",
                 "why": "Sao Paulo Med J 2022, CC BY 4.0: 'Mortality ... tocilizumab plus standard care vs standard care'"},
}
READERS = {"reader1": kfp.MODEL, "reader2": "gpt-5.5"}
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["legible", "measure", "subgroup_read", "rows", "pooled", "notes"],
    "properties": {
        "legible": {"type": "boolean"}, "measure": {"type": "string"}, "notes": {"type": "string"},
        "subgroup_read": {"type": "string"},
        "pooled": {"type": "object", "additionalProperties": False, "required": ["effect", "lower", "upper"],
                   "properties": {k: {"type": "string"} for k in ("effect", "lower", "upper")}},
        "rows": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["label", "events_t", "total_t", "events_c", "total_c", "effect", "lower", "upper"],
            "properties": {k: {"type": "string"} for k in ("label", "events_t", "total_t", "events_c", "total_c",
                                                            "effect", "lower", "upper")}}},
    },
}
INSTR = """You are reading ONE forest-plot figure from a published meta-analysis of tocilizumab for COVID-19. Transcribe
what is PRINTED; do not compute, infer, round or correct anything.

- If the figure has subgroups (e.g. RCTs and observational / cohort studies), transcribe ONLY the randomised controlled
  trials subgroup; say which subgroup you read in subgroup_read.
- For every study row, in the order printed: the study label exactly as printed; the tocilizumab arm's Events and Total
  and the control arm's Events and Total exactly as printed; and the printed effect estimate with its lower and upper
  confidence limits exactly as printed (same decimals). Use "" for a value that is not printed.
- pooled: that subgroup's pooled (subtotal / diamond) estimate and limits as printed.
- measure: the effect measure the figure states (e.g. Risk Ratio, Odds Ratio).
- If the numeric columns are not printed or are unreadable, set legible=false and leave rows empty. Never estimate a
  value from the position of a marker.
"""


def held_jats(pmcid):
    """The meta's JATS from Europe PMC (open access), cached under cache/comparators/<pmid>/ like the comparators."""
    pmid = next(p for p, m in METAS.items() if m["pmcid"] == pmcid)
    fp = os.path.join(kfp.COMP, pmid, f"g1_meta2_{pmcid}.xml")
    if not os.path.exists(fp):
        from harness import http
        st, b = http.get_raw(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", tries=2, timeout=90)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb").write(b)
    return open(fp, encoding="utf-8").read()


def independence(x):
    refs = " ".join(re.findall(r"<ref(?=[\s>]).*?</ref>", x, re.S))
    lic = re.search(r"creativecommons\.org/[a-z/]+[0-9.]*", x)
    cites = [i for i in REACT_IDS if i in refs.lower()] + (
        ["title"] if re.search(r"Association Between Administration of IL-6 Antagonists", refs, re.I) else [])
    n = len(re.findall(r"<ref(?=[\s>])", x))          # '<ref' + any whitespace, never '<ref-list' (codex cascade_and_meta2#4)
    return {"licence": lic.group(0) if lic else None, "n_refs": n,
            "state": ("CITATIONS_UNKNOWN" if n == 0 else "CITES_COMPARATOR:" + ",".join(cites) if cites else "INDEPENDENT")}


def text_of(x):
    import html
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x)))


def _int(s):
    s = str(s or "").replace(",", "").strip()
    return int(s) if re.fullmatch(r"\d+", s) else None


def row_effect(r, measure):
    a, n1, c, n2 = (_int(r[k]) for k in ("events_t", "total_t", "events_c", "total_c"))
    if None in (a, n1, c, n2) or n1 == 0 or n2 == 0 or a > n1 or c > n2:
        return None
    if a == 0 or c == 0:
        return None                                   # a zero-cell effect depends on the meta's correction: not checked
    if re.search(r"odds", measure or "", re.I):
        return (a / (n1 - a)) / (c / (n2 - c)) if n1 > a and n2 > c else None
    return (a / n1) / (c / n2)


def gate(resp, text):
    probs, rows = [], []
    if not isinstance(resp, dict) or not resp.get("legible"):
        return {"state": "REFUSED", "problems": ["NOT_LEGIBLE"], "rows": []}
    for r in resp.get("rows") or []:
        a, n1, c, n2 = (_int(r.get(k)) for k in ("events_t", "total_t", "events_c", "total_c"))
        if None in (a, n1, c, n2) or a > n1 or c > n2:
            probs.append(f"G1_COUNTS:{r.get('label')}")
            continue
        e = kfp._num(r.get("effect"))
        rec = row_effect(r, resp.get("measure"))
        # a row whose counts cannot be checked against its OWN printed effect is not admitted: no printed effect = G2
        # unverifiable (codex review cascade_and_meta2#1); a zero-cell row (rec None) is checked by G4 only
        if e is None:
            probs.append(f"G2_NO_PRINTED_EFFECT:{r.get('label')}")
            continue
        g2 = None if rec is None else abs(rec - e) <= kfp._half_unit(r["effect"]) + 0.006
        if g2 is False:
            probs.append(f"G2_ROW_EFFECT_NOT_FROM_COUNTS:{r.get('label')} ({rec:.3f} vs {e})")
            continue
        rows.append({"label": r["label"], "events_t": a, "total_t": n1, "events_c": c, "total_c": n2,
                     "printed": {k: r.get(k) for k in ("effect", "lower", "upper")}, "g2": g2})
    p = resp.get("pooled") or {}
    anchor = kfp.pooled_in_text(p, text)
    if not anchor:
        probs.append("G3_POOLED_NOT_PRINTED_IN_TEXT")
    matched = []
    eff = [{"effect": kfp._num(r["printed"]["effect"]), "lower": kfp._num(r["printed"]["lower"]),
            "upper": kfp._num(r["printed"]["upper"])} for r in rows]
    eff = [x for x in eff if None not in x.values() and min(x.values()) > 0]
    if anchor and len(eff) >= 2:
        rec = kfp.pool_methods(eff, ratio=True)
        pp = {k: kfp._num(p[k]) for k in ("effect", "lower", "upper")}
        extra = kfp._half_unit(p["effect"])
        matched = [k for k, (m, lo, hi) in rec.items() if kfp._close(m, p["effect"], extra)
                   and kfp._close(lo, p["lower"], extra) and kfp._close(hi, p["upper"], extra)]
        if not matched:
            probs.append(f"G4_RECOMPUTATION_FAILS (rows {len(eff)}; printed {pp})")
    elif anchor:
        # fewer than two usable effects: the pooled triple cannot be recomputed, so nothing is admitted on G4's word
        probs.append(f"G4_TOO_FEW_EFFECTS ({len(eff)})")
    return {"state": "PASS" if not probs else "REFUSED", "problems": probs, "rows": rows, "anchor": anchor,
            "methods_reproducing": matched, "subgroup_read": resp.get("subgroup_read"), "measure": resp.get("measure"),
            "pooled_read": p}


def _surname(lab):
    """A forest-plot label's identifying words (first author / acronym and anything else printed), without 'et al.',
    group words, years and reference superscripts: 'Salama et al.18' -> ('salama',), 'Trial A' -> ('trial', 'a').
    The FIRST word alone is not an identity: 'Trial A' and 'Trial B' share it."""
    return tuple(w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", (lab or "").lower())
                 if w not in ("et", "al", "investigators", "collaborative", "group", "writing", "committee"))


def admit(gates, ind):
    """(state, admitted_rows, refused_because). A row is admitted only when BOTH readers' gates PASS and both give the
    same four counts to the SAME trial (first word of its label): the counts alone let two readers assign one tuple to
    opposite trials (codex cascade_and_meta2#2). Independence decides ADMISSION, not only whether new calls are made: a
    REACT-citing meta's replayed rows are never admitted (codex cascade_and_meta2#5)."""
    key = lambda r: (str(r["events_t"]), str(r["total_t"]), str(r["events_c"]), str(r["total_c"]), _surname(r["label"]))  # noqa: E731
    if ind.get("state") != "INDEPENDENT":
        return "REFUSED", [], ind.get("state")
    if not all(x["state"] == "PASS" for x in gates):
        return "REFUSED", [], "A_READER_DID_NOT_PASS"
    r2 = {key(r): r for r in gates[1]["rows"]}
    return "PASS", [dict(r, label_reader2=r2[key(r)]["label"]) for r in gates[0]["rows"] if key(r) in r2], None


def main(argv):
    run = "--run" in argv
    pmids = [a for a in argv if a.isdigit()] or list(METAS)
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    out = {}
    for pmid in pmids:
        m = METAS[pmid]
        x = held_jats(m["pmcid"])
        ind = independence(x)
        fp, b = kfp.fetch_image(pmid, m["pmcid"], m["href"])
        if not fp:
            out[pmid] = {"state": "IMAGE_NOT_FETCHED", "independence": ind}
            continue
        cap = re.search(re.escape(m["href"].rsplit(".", 1)[0]), x)
        figcap = ""
        for f in re.findall(r"<fig[ >].*?</fig>", x, re.S):
            if m["href"].rsplit(".", 1)[0] in f:
                figcap = text_of(" ".join(re.findall(r"<caption>.*?</caption>", f, re.S)))[:400]
        p = (INSTR + f"\nFIGURE CAPTION (from the article): {figcap}\n").encode("utf-8")
        img = {"ref": os.path.relpath(fp, ROOT).replace(os.sep, "/"), "sha256": hashlib.sha256(b).hexdigest()}
        res = {"why": m["why"], "independence": ind, "image": img, "caption": figcap, "readers": {}}
        for rk, model in READERS.items():
            r0 = ((prev.get(pmid) or {}).get("readers") or {}).get(rk, {}).get("run")
            want = (hashlib.sha256(p).hexdigest(), img["sha256"])
            if run and ind["state"] == "INDEPENDENT" and not (r0 and r0["state"] == "RAN_OK" and
                                                               (r0["prompt_sha256"], r0["image_sha256"]) == want):
                rec = mcl.call(p, schema=SCHEMA, model=model, effort=kfp.EFFORT,
                               caller={"file": "scripts/g1_toci_meta2_forest.py", "line": "main",
                                       "purpose": f"G1 tocilizumab second meta {pmid}: mortality forest rows with counts"},
                               input_digests=[{"ref": img["ref"], "sha256": img["sha256"],
                                               "what": "second-meta forest-plot figure attached with -i"}],
                               timeout_s=900, images=(fp,))
                ms.write_record(rec, kfp.REC_DIR)
                r0 = {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": want[0],
                      "image_sha256": want[1], "model": model}
            if not r0 or r0["state"] != "RAN_OK" or (r0["prompt_sha256"], r0["image_sha256"]) != want:
                res["readers"][rk] = {"run": r0, "gate": {"state": "NO_RECORDED_CALL", "rows": []}}
                continue
            resp = json.loads(ms.replay(ms.load_record(os.path.join(kfp.REC_DIR, r0["record_id"] + ".json"))).decode("utf-8"))
            res["readers"][rk] = {"run": r0, "gate": gate(resp, text_of(x))}
        st, rows, why = admit([res["readers"][k]["gate"] for k in READERS], ind)
        res.update(state=st, admitted_rows=rows, refused_because=why)
        out[pmid] = res
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for pmid, r in out.items():
        print(pmid, r.get("independence"), r.get("state"))
        for k, v in (r.get("readers") or {}).items():
            gg = v["gate"]
            print("  ", k, gg["state"], gg.get("problems"), gg.get("subgroup_read"), gg.get("pooled_read"),
                  [(x["label"], x["events_t"], x["total_t"], x["events_c"], x["total_c"]) for x in gg.get("rows", [])])
        print("   admitted:", [(x["label"], x["events_t"], x["total_t"], x["events_c"], x["total_c"]) for x in r.get("admitted_rows", [])])


if __name__ == "__main__":
    main(sys.argv[1:])
