"""Comparator FOREST-PLOT rows as a RECORDED, REPLAYABLE model proposal, admitted only by RECOMPUTATION.

Per-trial numbers the comparator prints only inside a forest-plot figure are not in any text, so a model reads the
figure. What the model reads is a PROPOSAL; none of it counts until a deterministic gate recomputes the comparator's
own PRINTED pooled result from the proposed rows:

  select   the figure whose JATS caption names a forest plot for the topic's primary outcome, skipping subgroup /
           sensitivity figures (deterministic, from the comparator's own captions)
  image    fetched from NCBI's public PMC OA bucket (pmc-oa-opendata), cached under cache/comparators/<pmid>/ with
           its sha256 (the recorded call's input digest)
  read     one codex exec call with the image attached (-i), recorded by reproducible_ai.model_call_live.call
  gate     G1 typed and legible; G2 the plot's pooled row equals the pooled estimate the comparator PRINTS IN ITS TEXT
           (comparators.json, span-quoted) within rounding; G3 every row is internally consistent (lower < point
           < upper; the point is the log-midpoint of its CI within rounding); G4 the rows' count equals the printed
           k; G5 RECOMPUTATION: pooling the proposed rows (log scale, SE from the CI) with FE, DL or PM (each with
           and without Hartung-Knapp) reproduces the printed pooled estimate AND CI within rounding
  admit    only rows from a figure that passes every gate, tagged FOREST_PLOT_MODEL_READ_RECOMPUTED

    python scripts/k_gap_forest_plot.py --run [SLUG ...]     (model calls; concurrency 3)
    python scripts/k_gap_forest_plot.py [SLUG ...]           (replay recorded calls + gate; no network)
Writes registry/model_proposals/k_gap_forest_plot.json.
"""
from __future__ import annotations

import concurrent.futures as cf
import glob
import hashlib
import io
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
COMP = os.path.join(ROOT, "cache", "comparators")
PROP = os.path.join(ROOT, "registry", "model_proposals", "k_gap_forest_plot.json")
REC_DIR = os.path.join(ROOT, "registry", "model_calls")
MODEL, EFFORT = "gpt-6-astra", "medium"
XL = "{http://www.w3.org/1999/xlink}href"
SUBGROUP = re.compile(r"subgroup|sensitivity|in patients with|without such|stratified|by (?:baseline|dose|duration)"
                      r"|with different|with respect to|according to", re.I)
FOREST = re.compile(r"forest", re.I)
MULTIPANEL = re.compile(r"\(\s*[A-D]\s*\)|\b[A-D]\)\s", re.S)
SECONDARY = re.compile(r"secondary (?:outcome|end ?point)", re.I)

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["legible", "measure", "rows", "pooled", "notes"],
    "properties": {
        "legible": {"type": "boolean"},
        "measure": {"type": "string"},
        "notes": {"type": "string"},
        "pooled": {"type": "object", "additionalProperties": False, "required": ["effect", "lower", "upper"],
                   "properties": {k: {"type": "string"} for k in ("effect", "lower", "upper")}},
        "rows": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["label", "effect", "lower", "upper", "weight_pct"],
            "properties": {"label": {"type": "string"}, "effect": {"type": "string"}, "lower": {"type": "string"},
                           "upper": {"type": "string"}, "weight_pct": {"type": ["string", "null"]}}}},
    },
}
INSTR = """You are reading ONE forest-plot figure from a published meta-analysis. Transcribe what is PRINTED; do not
compute, infer, round or correct anything.

- For every study row, in the order printed: the study label exactly as printed, and the point estimate and the lower
  and upper confidence limits exactly as printed in the numeric column (same decimals). Give the weight in percent
  if it is printed, else null.
- Give the pooled (overall / summary / diamond) row's printed estimate and limits the same way.
- measure: the effect measure the figure states (e.g. HR, RR, OR).
- If the numeric column is not printed or is unreadable, set legible=false and leave rows empty. Never estimate a
  value from the position of a marker.
- notes: anything a checker needs (e.g. two pooled rows printed; which one you gave).
"""


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ figure selection and image acquisition

def comparator(slug):
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    pmid = re.search(r"PMID (\d+)", c.get("citation", "")).group(1)
    pmcid = None
    for f in glob.glob(os.path.join(COMP, pmid, "*idconv.json")):
        m = re.search(r'"pmcid"\s*:\s*"(PMC\d+)"', open(f, encoding="utf-8").read())
        if m:
            pmcid = m.group(1)
    return c, pmid, pmcid


def printed_pool(c):
    """The comparator's pooled result as PRINTED in its text (span-quoted in comparators.json), never model-read."""
    ts = c                                   # k / effect / ci / method are top-level, span-quoted
    eff, ci, k = (ts.get("effect") or {}), (ts.get("ci") or {}), (ts.get("k") or {})
    if eff.get("value") is None or not ci.get("value"):
        return None
    return {"effect": eff["value"], "lower": ci["value"][0], "upper": ci["value"][1], "k": k.get("value"),
            "quote": (eff.get("span") or {}).get("quote"), "method": (ts.get("method") or {}).get("value")}


def select_figure(slug, pmid, jats_date="2026-09-28", caption_re=None, jats_file=None):
    # jats_file: an explicit JATS(-like) file (scripts/g1_forest_reader.py derives one from a PMC article page)
    jp = jats_file or os.path.join(COMP, pmid, f"{jats_date}_kgap_jats.xml")
    if not os.path.exists(jp):
        return None, "NO_JATS"
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    # The COMPARATOR's own endpoint names dominate: the topic's keyword list for a composite also lists its
    # components ("myocardial infarction" for MACE), which scored the nonfatal-MI figure above the MACE figure.
    # An acronym the comparator uses (MACE, HHF) or its full endpoint phrase scores 10; a keyword word scores 1.
    eps = [str(x) for x in list((c.get("outcome_endpoints") or {}).keys()) + list((c.get("outcome_endpoints") or {}).values())]
    strong = {a for e in eps for a in re.findall(r"\b[A-Z]{3,}\b", e)} | {e.lower() for e in eps if len(e) > 6}
    words = {w.lower() for k in (cfg.get("primary_outcome") or {}).get("keywords") or [] for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", k)}
    words -= {"point", "major", "adverse", "events", "event", "outcome", "outcomes", "with", "from", "rate", "risk"}
    inc = cfg.get("include") or {}

    def outcome_score(t):
        sc = 10 * sum(1 for s in strong if (re.search(r"\b" + re.escape(s) + r"\b", t) if s.isupper() else s in t.lower()))
        return sc + sum(1 for w in words if re.search(r"\b" + re.escape(w) + r"\b", t, re.I))

    cands, refused = [], []
    for f in ET.parse(jp).getroot().iter("fig"):
        cap = " ".join("".join(x.itertext()) for x in f.iter("caption"))
        g = f.find(".//graphic")
        if g is None or not (caption_re or FOREST).search(cap) or SUBGROUP.search(cap):
            continue
        # The gate anchors the plot's pool to the comparator's TEXT, but a wrong-outcome figure's pool is printed there
        # too, so a figure whose outcome is not unambiguous is refused here, before any model call: a multi-panel
        # figure ('(A) ... (B) ...', one panel per outcome) or a figure the caption calls a SECONDARY outcome.
        if SECONDARY.search(cap):
            refused.append((f.get("id"), "SECONDARY_OUTCOME"))
            continue
        # figure-level text (before any '(A)'): the POPULATION the figure is about. The topic's own population terms
        # score +5 and its excluded populations -5 (spironolactone: F4 'in hFrEF patients' over F2 'in hFpEF ...').
        head = MULTIPANEL.split(cap, maxsplit=1)[0]
        pop = 5 * sum(1 for t in inc.get("population_any") or [] if len(t) > 3 and re.search(r"\b" + re.escape(t.rstrip("*")) + r"\b", head, re.I))
        pop -= 5 * sum(1 for t in inc.get("population_none") or [] if len(t) > 3 and re.search(r"\b" + re.escape(t.rstrip("*")) + r"\b", head, re.I))
        if MULTIPANEL.search(cap):
            # A multi-panel figure is usable only when its CAPTION names exactly one panel as our outcome: the panel
            # comes from the article's own text, and the reader is then told to transcribe that panel alone.
            # a panel title ends at ';', '(' or a sentence stop -- the caption's trailing abbreviation list ('... All-cause
            # mortality. CI, confidence interval; ...') is not part of panel (D)'s title
            panels = [(m.group(1), re.split(r"\.\s", m.group(2).strip())[0])
                      for m in re.finditer(r"\(([A-E])\)\s*([^();]+)", cap)]
            scored = sorted(((outcome_score(t), L, t) for L, t in panels), reverse=True)
            if not scored or scored[0][0] == 0 or (len(scored) > 1 and scored[1][0] == scored[0][0]):
                refused.append((f.get("id"), "MULTIPANEL_NO_UNIQUE_PANEL"))
                continue
            sc, letter, title = scored[0]
            cands.append((sc + pop, f.get("id"), g.get(XL), cap.strip()[:300], letter, title))
            continue
        cands.append((outcome_score(cap) + pop, f.get("id"), g.get(XL), cap.strip()[:300], None, None))
    cands.sort(key=lambda x: -x[0])
    if not cands or cands[0][0] <= 0:
        return None, "NO_OUTCOME_FOREST_FIGURE" + (":refused " + ",".join(f"{a}={b}" for a, b in refused) if refused else "")
    if len(cands) > 1 and cands[1][0] == cands[0][0]:
        return None, "AMBIGUOUS_FIGURE:" + ",".join(x[1] for x in cands[:3])
    s, fid, href, cap, letter, title = cands[0]
    return {"fig_id": fid, "href": href, "caption": cap, "panel": letter, "panel_title": title}, "SELECTED"


def fetch_image(pmid, pmcid, href, date="2026-09-29"):
    from harness import http
    name = href if re.search(r"\.(jpe?g|png|gif|tiff?)$", href, re.I) else href + ".jpg"
    fp = os.path.join(COMP, pmid, f"{date}_kgap_{name}")
    if os.path.exists(fp):
        b = open(fp, "rb").read()
        return fp, b
    for v in (1, 2, 3):
        url = f"https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.{v}/{name}"
        try:
            st, b = http.get_raw(url, tries=2, timeout=60)
        except Exception:  # noqa: BLE001 - try the next article version
            continue
        if b[:3] == b"\xff\xd8\xff" or b[:4] == b"\x89PNG":
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, "wb").write(b)
            json.dump({"url": url, "http_status": st, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()},
                      open(fp + ".meta.json", "w", encoding="utf-8"), indent=1)
            return fp, b
    return None, None


# ------------------------------------------------------------------ recorded model call with an image

# The figure is shown to the model ONLY through reproducible_ai.model_call_live.call(images=...): that module is the
# repository's one model caller (tests/test_model_inventory.py). An earlier private runner here built its own
# codex argv; the inventory test refused it, rightly.

def prompt_bytes(item):
    fig = item["figure"]
    extra = ""
    if fig.get("panel"):
        extra = (f"\nThis figure has several panels. Transcribe ONLY panel ({fig['panel']}), which the caption titles "
                 f"'{fig['panel_title']}'. Ignore every other panel; its rows and pooled row are not wanted.\n")
    return (INSTR + f"\nFIGURE CAPTION (from the article): {fig['caption']}\n" + extra).encode("utf-8")


def run_one(item):
    p = prompt_bytes(item)
    rec = mcl.call(p, schema=SCHEMA, model=MODEL, effort=EFFORT,
                   caller={"file": "scripts/k_gap_forest_plot.py", "line": "run_one",
                           "purpose": f"G1 forest-plot row transcription {item['slug']} (acq/k-gap lane)"},
                   input_digests=[{"ref": item["image_ref"], "sha256": item["image_sha256"],
                                   "what": "comparator forest-plot figure attached with -i"}],
                   timeout_s=900, images=(item["image_path"],))
    ms.write_record(rec, REC_DIR)
    return {"slug": item["slug"], "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": hashlib.sha256(p).hexdigest(), "image_sha256": item["image_sha256"]}


# ------------------------------------------------------------------ the deterministic gate

def _dec(s):
    m = re.search(r"\.(\d+)", str(s))
    return len(m.group(1)) if m else 0


def _num(s):
    s = str(s).replace("−", "-").replace("·", ".").strip()
    return float(s) if re.fullmatch(r"-?\d+(?:\.\d+)?", s) else None


def _half_unit(s):
    return 0.5 * 10 ** (-_dec(s))


RATIO = re.compile(r"\b(?:HR|RR|OR|IRR|hazard|risk ratio|odds|rate ratio|relative risk)", re.I)


def is_ratio(measure):
    return bool(RATIO.search(measure or ""))


def pool_methods(rows, ratio=True, z=1.959963984540054):
    """Recompute the pool from (point, lower, upper) rows -- log scale for a ratio, raw for a difference -- with FE,
    DL and PM, each with and without Hartung-Knapp (t, k-1 df)."""
    from scipy import stats
    from harness.synth import _paule_mandel_tau2
    f = math.log if ratio else (lambda x: x)
    g = math.exp if ratio else (lambda x: x)
    yi = [f(r["effect"]) for r in rows]
    vi = [((f(r["upper"]) - f(r["lower"])) / (2 * z)) ** 2 for r in rows]
    if any(v <= 0 for v in vi):
        return {}
    k = len(yi)
    w = [1 / v for v in vi]
    fe = sum(a * b for a, b in zip(w, yi)) / sum(w)
    q = sum(a * (b - fe) ** 2 for a, b in zip(w, yi))
    c = sum(w) - sum(a * a for a in w) / sum(w)
    taus = {"FE": 0.0, "DL": max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0}
    try:
        taus["PM"] = float(_paule_mandel_tau2(yi, vi))
    except Exception:  # noqa: BLE001
        pass
    out = {}
    for name, t2 in taus.items():
        ww = [1 / (v + t2) for v in vi]
        mu = sum(a * b for a, b in zip(ww, yi)) / sum(ww)
        se = math.sqrt(1 / sum(ww))
        out[name] = (g(mu), g(mu - z * se), g(mu + z * se))
        if k >= 2:
            qhk = sum(a * (b - mu) ** 2 for a, b in zip(ww, yi)) / (k - 1)
            seh = math.sqrt(qhk / sum(ww))
            tq = stats.t.ppf(0.975, k - 1)
            out[name + "+HK"] = (g(mu), g(mu - tq * seh), g(mu + tq * seh))
    return out


def _close(x, printed, extra=0.0):
    """x rounds to the printed value, allowing the printed rounding plus `extra` (row-rounding propagation)."""
    return abs(x - float(printed)) <= _half_unit(printed) + extra + 1e-9


_TRIPLE_SEP = r"[\s,;:()\[\]%]*(?:95\s*%\s*)?(?:CI|confidence interval)?[\s,;:()\[\]]*"


def pooled_in_text(p, text):
    """The plot's pooled triple as PRINTED in the comparator's own text: point, then lower and upper within a short
    window (dash, 'to' or comma between). Returns the verbatim quote, else None. The number comes from the TEXT."""
    if not text:
        return None
    t = text.replace("\u2212", "-").replace("\u00b7", ".").replace("\u2013", "-").replace("\u2014", "-")
    e, lo, hi = (str(p.get(k) or "").replace("\u2212", "-") for k in ("effect", "lower", "upper"))
    if not all(re.fullmatch(r"-?\d+(?:\.\d+)?", x) for x in (e, lo, hi)):
        return None
    num = lambda x: r"(?<![\d.])" + re.escape(x) + r"(?![\d])"   # noqa: E731
    # a '95% CI' between the point and its bounds is normal, so '95%' is allowed inside the window
    pat = num(e) + r"(?:[^\d]|95\s?%){0,40}?" + num(lo) + r"\s*(?:-|to|,|;)\s*" + num(hi)
    m = re.search(pat, t)
    return t[max(0, m.start() - 60): m.end() + 20] if m else None


def gate(resp, pp, text=None):
    probs = []
    if not isinstance(resp, dict) or not resp.get("legible"):
        return {"state": "REFUSED", "problems": ["NOT_LEGIBLE_OR_UNTYPED"]}
    ratio = is_ratio(resp.get("measure"))
    rows, excluded = [], []
    for r in resp.get("rows") or []:
        e, lo, hi = _num(r.get("effect")), _num(r.get("lower")), _num(r.get("upper"))
        if ratio and None not in (e, lo, hi) and lo == 0 and e > 0 and hi > e:
            # a ratio's lower limit PRINTED as 0.00 is a tiny value rounded away (Selinger 2013, weight 0.3%): it cannot
            # be put on the log scale, so the row is neither admitted nor pooled -- it is listed, and the recomputation
            # over the remaining rows must still reproduce the printed pool
            excluded.append({"label": r.get("label"), "why": "RATIO_LOWER_PRINTED_AS_ZERO", "weight_pct": r.get("weight_pct")})
            continue
        if None in (e, lo, hi) or (ratio and min(e, lo, hi) <= 0):
            probs.append(f"ROW_NOT_NUMERIC:{r.get('label')}")
            continue
        if not (lo <= e <= hi):
            probs.append(f"ROW_ORDER:{r.get('label')}")
        # the point is the midpoint of its CI (log scale for a ratio), within the printed rounding of all three
        if ratio:
            mid = math.exp((math.log(lo) + math.log(hi)) / 2)
            tol = _half_unit(r["effect"]) + e * 0.5 * (_half_unit(r["lower"]) / lo + _half_unit(r["upper"]) / hi) + 0.005
        else:
            mid = (lo + hi) / 2
            tol = _half_unit(r["effect"]) + 0.5 * (_half_unit(r["lower"]) + _half_unit(r["upper"])) + 1e-9
        if abs(mid - e) > tol:
            probs.append(f"ROW_CI_ASYMMETRIC:{r.get('label')}")
        rows.append({"label": r.get("label"), "effect": e, "lower": lo, "upper": hi, "raw": r})
    p = resp.get("pooled") or {}
    anchor = None
    if pp is None:
        # no pre-typed pooled value: the plot's pooled triple must be printed, verbatim, in the comparator's text
        anchor = pooled_in_text(p, text)
        if anchor is None:
            probs.append("PLOT_POOLED_NOT_PRINTED_IN_TEXT")
        else:
            pp = {"effect": p["effect"], "lower": p["lower"], "upper": p["upper"], "k": None, "quote": anchor,
                  "method": None, "anchored_by": "verbatim triple in the comparator's held text"}
    else:
        for key in ("effect", "lower", "upper"):
            v = _num(p.get(key))
            if v is None or not _close(v, pp[key]):
                probs.append(f"PLOT_POOLED_{key.upper()}_NE_TEXT")
    if pp and pp.get("k") and len(rows) + len(excluded) != int(pp["k"]):
        probs.append(f"ROW_COUNT_{len(rows)}_NE_PRINTED_K_{pp['k']}")
    recomputed, matched = {}, []
    if len(rows) >= 2 and pp:
        recomputed = pool_methods(rows, ratio=ratio)
        extra = _half_unit(pp["effect"])              # row rounding propagates into the pool
        for name, (m, lo, hi) in recomputed.items():
            if _close(m, pp["effect"], extra) and _close(lo, pp["lower"], extra) and _close(hi, pp["upper"], extra):
                matched.append(name)
        if not matched:
            probs.append("RECOMPUTATION_DOES_NOT_REPRODUCE_PRINTED_POOL")
    elif len(rows) < 2:
        probs.append("FEWER_THAN_2_ROWS")
    return {"state": "PASS" if not probs else "REFUSED", "problems": probs, "ratio": ratio, "excluded_rows": excluded,
            "rows": [{**{k: v for k, v in r.items() if k != "raw"},
                      "printed": {k: str(r["raw"].get(k)) for k in ("effect", "lower", "upper")}} for r in rows],
            "recomputed": {k: [round(x, 4) for x in v] for k, v in recomputed.items()}, "methods_reproducing": matched,
            "printed_pool": pp}


# ------------------------------------------------------------------ driver

def items(slugs):
    out, skipped = [], {}
    for slug in slugs:
        try:
            c, pmid, pmcid = comparator(slug)
        except Exception as exc:  # noqa: BLE001
            skipped[slug] = f"NO_COMPARATOR:{exc}"[:120]
            continue
        pp = printed_pool(c)
        fig, why = select_figure(slug, pmid)
        if not fig:
            skipped[slug] = why
            continue
        if not pmcid:
            skipped[slug] = "NO_PMCID"
            continue
        fp, b = fetch_image(pmid, pmcid, fig["href"])
        if not fp:
            skipped[slug] = "IMAGE_NOT_FETCHED"
            continue
        out.append({"slug": slug, "pmid": pmid, "pmcid": pmcid, "figure": fig, "printed_pool": pp,
                    "image_path": fp, "image_ref": os.path.relpath(fp, ROOT).replace(os.sep, "/"),
                    "image_sha256": hashlib.sha256(b).hexdigest()})
    return out, skipped


def main(argv):
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")] or sorted(
        t["slug"] for t in _j(os.path.join(OUT, "k_gap_table.json"))["topics"])
    its, skipped = items(slugs)
    data = _j(PROP) if os.path.exists(PROP) else {}
    runs = data.get("runs", {})
    if run:
        done = {(r["prompt_sha256"], r["image_sha256"]) for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [i for i in its if (hashlib.sha256(prompt_bytes(i)).hexdigest(), i["image_sha256"]) not in done]
        print(f"figures {len(its)}, to run {len(todo)}, skipped {len(skipped)}", flush=True)
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(run_one, todo):
                runs[r["slug"]] = r
                print(r["slug"], r["state"], r["record_id"], flush=True)
    res = {}
    for i in its:
        r = runs.get(i["slug"])
        if not r or r["state"] != "RAN_OK" or r["image_sha256"] != i["image_sha256"]:
            res[i["slug"]] = {"state": "NO_RECORDED_CALL", "figure": i["figure"]}
            continue
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
        from kgap import k_gap
        g = gate(resp, i["printed_pool"], k_gap.held_text(i["slug"])[0])
        res[i["slug"]] = {"state": g["state"], "figure": i["figure"], "image_ref": i["image_ref"],
                          "image_sha256": i["image_sha256"], "record_id": r["record_id"], "measure": resp.get("measure"),
                          "gate": g, "provenance": "FOREST_PLOT_MODEL_READ_RECOMPUTED" if g["state"] == "PASS" else None}
    from collections import Counter
    out = {"n_topics": len(slugs), "n_figures": len(its), "skipped": skipped, "runs": runs, "results": res,
           "tally": dict(Counter(v["state"] for v in res.values()))}
    json.dump(out, open(PROP, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, sort_keys=True)
    print(json.dumps({"n_figures": len(its), "tally": out["tally"], "skipped": skipped}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
