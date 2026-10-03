"""G1-R REPRODUCTION: does OUR ENGINE reproduce each comparator's printed pooled result from the comparator's OWN
per-trial rows? A separate metric from G1 (Mahmood 3 Oct): G1 asks whether we match the comparator trial for trial;
G1-R asks whether our pooling engine, fed the comparator's own rows under the comparator's STATED model, gives the
comparator's printed pool.

  rows    the comparator's own per-trial rows, best source first:
            TYPED_TABLE   the secondary tier's regex-typed JATS table of the comparator (registry/secondary_meta)
            DUAL_READ     the dual-model forest reader's agreed rows (codex + agy agree within printed rounding;
                          registry/model_proposals/g1_forest_reader.json), only when EVERY row agreed and the rows are
                          trials (a figure with disagreeing or non-trial rows gives no G1-R rows)
  printed the comparator's printed pooled estimate + CI: its span-quoted text value, else the typed table's pooled row,
          else the figure's agreed pooled row (whether that triple is also printed in the meta's text is recorded)
  model   the comparator's STATED model (g1_forest_reader.stated_model: the figure's RevMan label, else its own text)
  engine  harness.secondary_meta.row_yi_vi + pool (FE / DL / PM / REML, +/- Hartung-Knapp) -- the engine the tracker uses --
          and pool_mh (Mantel-Haenszel fixed / RevMan random from the printed counts; checked against R meta::metabin
          and metafor::rma.mh). A stated method the engine does not implement is reported ENGINE_LACKS_METHOD,
          never substituted; what the implemented methods give is shown beside it.
  verdict REPRODUCED (a stated method, in our engine, gives the printed estimate AND CI within printed rounding + one
          half-unit of row-rounding propagation -- the tier's tolerance) / NOT_REPRODUCED / ENGINE_LACKS_METHOD /
          NOT_RECONSTRUCTABLE (one-stage IPD) / NO_COMPARATOR_ROWS (why)

    python scripts/g1r_reproduction.py     -> outputs/k_gap/G1R_REPRODUCTION.json + .md   (offline; no model)
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402
import k_gap_forest_plot as fp  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "G1R_REPRODUCTION.json")
MD = os.path.join(ROOT, "outputs", "k_gap", "G1R_REPRODUCTION.md")
ENGINE = {"FE": ("FE", False), "DL": ("DL", False), "PM": ("PM", False), "FE+HK": ("FE", True),
          "DL+HK": ("DL", True), "PM+HK": ("PM", True), "REML": ("REML", False), "REML+HK": ("REML", True),
          # Mantel-Haenszel from the printed counts (harness.secondary_meta.pool_mh, RevMan 5 / meta::metabin)
          "MH-FE": ("MH", False), "MH-RE": ("MH", True)}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def topics():
    d = os.path.join(ROOT, "outputs", "k_gap", "g1")
    return sorted(f[:-5] for f in os.listdir(d) if f.endswith(".json") and ".tmp" not in f)


def engine_pool(rows, measure, method):
    if ENGINE[method][0] == "MH":
        got = sm.pool_mh(rows, measure, random=ENGINE[method][1])
        return None if got is None else tuple(math.exp(x) for x in got)
    yv = [sm.row_yi_vi(r) for r in rows]
    yv = [x for x in yv if x is not None]
    if len(yv) < 2:
        return None
    m, hk = ENGINE[method]
    g = math.exp if measure.upper() in sm.RATIO else (lambda x: x)
    return tuple(g(x) for x in sm.pool([a for a, _ in yv], [b for _, b in yv], m, hk))


def close(rec, printed):
    extra = fp._half_unit(printed["effect"])
    return all(fp._close(x, printed[k], extra) for x, k in zip(rec, ("effect", "lower", "upper")))


def as_rows(dicts, measure, pmid):
    out = []
    for d in dicts:
        r = sm.SecondaryRow(meta_pmid=pmid, meta_doi="", location={}, source_digest="", provenance="G1R",
                            trial_label=d.get("label") or d.get("trial_label") or "", measure=measure,
                            outcome_definition="", effect=d.get("effect"), lower=d.get("lower"), upper=d.get("upper"),
                            events_t=d.get("events_t"), n_t=d.get("n_t"), events_c=d.get("events_c"), n_c=d.get("n_c"))
        if gfr._num(r.effect) is None:          # an 'NA' / not-estimable row carries no number: never pooled
            r.effect = r.lower = r.upper = None
        out.append(r)
    return out


def comparator_rows(slug, comp, dual):
    """(source, rows, measure, printed pool, printed-pool basis, stated model) or (None, why)."""
    sp = os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json")
    S = _j(sp) if os.path.exists(sp) else {}
    m = (S.get("metas") or {}).get(comp) or {}
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    text_pool = fp.printed_pool(c)
    if m.get("provenance") == "TYPED_TABLE" and m.get("pooled"):
        rows = [sm.SecondaryRow(**{k: v for k, v in r.items() if k in sm.SecondaryRow.__dataclass_fields__})
                for r in S.get("rows") or [] if r.get("meta_pmid") == comp]
        pp = text_pool or {k: m["pooled"][k] for k in ("effect", "lower", "upper")}
        model = gfr.stated_model(gfr.model_text(comp), measure=m.get("measure"))
        return ("TYPED_TABLE " + str(m.get("table")), rows, m.get("measure") or "", pp,
                "comparator text (span-quoted)" if text_pool else "the typed table's pooled row", model)
    if not dual:
        return None, "NOT_READ: no comparator figure read"
    if not dual.get("readings") or not isinstance(dual["readings"].get("codex"), dict):
        return None, "NOT_READ: " + str(dual.get("why") or dual.get("state") or "no two recorded readings")
    if dual.get("refused_rows") or dual.get("agreed_rows_not_trials") or not dual.get("proposed_rows") \
            or not dual.get("pooled_agreed"):
        why = [p for p in dual.get("problems") or [] if p.startswith(("ROWS_", "POOLED_", "NOT_LEGIBLE"))]
        return None, "ROWS_NOT_AGREED_AS_TRIALS: " + ", ".join(why or ["no agreed trial rows / pooled row"])
    rows = as_rows(dual["proposed_rows"], dual["measure"], comp)
    anchor = (dual.get("acceptance") or {}).get("pooled_anchor") or ""
    pp = text_pool or dual["pooled_agreed"]
    basis = ("comparator text (span-quoted)" if text_pool else
             "figure pooled row, also printed in the meta's text" if anchor.startswith("PRINTED_IN_META_TEXT") else
             "figure pooled row (both readers agree)")
    return ("DUAL_READ " + dual["figure"]["fig_id"], rows, dual["measure"], pp, basis, dual.get("stated_model") or {})


def g1r(slug, fr):
    comp = gfr.comparator_of(slug)
    dual = (fr.get("results") or {}).get(slug)
    if dual is None and slug in (fr.get("skipped") or {}):
        dual = {"why": (fr["skipped"][slug] or {}).get("why") if isinstance(fr["skipped"][slug], dict) else fr["skipped"][slug]}
    got = comparator_rows(slug, comp, dual)
    if got[0] is None:
        return {"slug": slug, "comparator_pmid": comp, "verdict": "NO_COMPARATOR_ROWS", "why": got[1]}
    src, rows, measure, pp, basis, model = got
    out = {"slug": slug, "comparator_pmid": comp, "rows_source": src, "k_rows": len(rows),
           "k_poolable": sum(1 for r in rows if sm.row_yi_vi(r) is not None), "measure": measure,
           "printed_pool": {k: pp.get(k) for k in ("effect", "lower", "upper")}, "printed_pool_basis": basis,
           "stated_model": {k: model.get(k) for k in ("state", "methods", "basis")},
           "rows": [{k: getattr(r, k) for k in ("trial_label", "effect", "lower", "upper", "events_t", "n_t",
                                                  "events_c", "n_c")} for r in rows]}
    if model.get("state") == "NOT_RECONSTRUCTABLE":
        return dict(out, verdict="NOT_RECONSTRUCTABLE", why="one-stage IPD model: not a function of trial rows")
    if any(gfr._num(pp.get(k)) is None for k in ("effect", "lower", "upper")):
        return dict(out, verdict="NO_COMPARATOR_ROWS", why="printed pool not numeric")
    stated = model.get("methods") or []
    engine_all = {m: engine_pool(rows, measure, m) for m in ENGINE}
    out["engine"] = {m: (None if v is None else [round(float(x), 4) for x in v]) for m, v in engine_all.items()}
    out["engine_reproduces"] = sorted(m for m, v in engine_all.items() if v and close(v, pp))
    in_engine = [m for m in stated if m in ENGINE]
    lacks = [m for m in stated if m not in ENGINE]
    out["stated_in_engine"], out["engine_lacks"] = in_engine, lacks
    ok = [m for m in in_engine if engine_all.get(m) and close(engine_all[m], pp)]
    if ok:
        return dict(out, verdict="REPRODUCED", by=ok)
    if not in_engine and lacks:
        return dict(out, verdict="ENGINE_LACKS_METHOD", why=f"stated {lacks}; our engine implements FE/DL/PM/REML (+HK) and Mantel-Haenszel (from counts)")
    if not stated:
        return dict(out, verdict="NOT_REPRODUCED", why="no pooling model stated by the comparator")
    return dict(out, verdict="NOT_REPRODUCED", why=f"stated {stated}: our engine gives "
                + "; ".join(f"{m} {out['engine'][m]}" for m in in_engine))


def main():
    fr = _j(gfr.OUT)
    res = [g1r(s, fr) for s in topics()]
    tally = dict(Counter(r["verdict"] for r in res))
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"metric": "G1-R", "tally": tally, "topics": res}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    md = ["# G1-R reproduction (derived: scripts/g1r_reproduction.py)", "",
          "Does OUR engine (harness.secondary_meta.pool: FE / DL / PM / REML, +/- HK; pool_mh: Mantel-Haenszel from counts) reproduce each comparator's printed pooled "
          "result from the comparator's OWN per-trial rows, under the comparator's STATED model? A separate metric from G1.",
          "", f"- tally: {tally}", "",
          "| topic | comparator | rows (source) | stated model | printed pool | our engine (stated) | verdict | note |",
          "|---|---|---|---|---|---|---|---|"]
    for r in res:
        pp = r.get("printed_pool") or {}
        eng = "; ".join(f"{m} {r['engine'][m]}" for m in r.get("stated_in_engine") or [] if r.get("engine"))
        md.append(f"| {r['slug']} | PMID {r['comparator_pmid']} | {r.get('k_rows', '-')} ({r.get('rows_source', '-')}) | "
                  f"{(r.get('stated_model') or {}).get('methods', '')} | {pp.get('effect', '')} ({pp.get('lower', '')}-"
                  f"{pp.get('upper', '')}) | {eng} | **{r['verdict']}** | "
                  f"{r.get('why') or ('by ' + ', '.join(r.get('by') or []))} |")
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")
    print(json.dumps(tally))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
