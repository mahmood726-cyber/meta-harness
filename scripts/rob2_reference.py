"""CALIBRATION REFERENCE for the formal RoB 2: the comparator meta's own PUBLISHED per-trial risk-of-bias judgements,
transcribed from its risk-of-bias figure by two RECORDED model readings (codex + agy, blind to each other), each cell
admitted only when both readings agree; a recorded adjudicator (codex, high effort) reads the disputed cells; a cell
still unresolved is left out of the calibration and counted.

The reference is a TRANSCRIPTION of what the comparator printed (colours / symbols per its legend), never a judgement.
Row labels are bound to trials through the comparator's OWN reference list (first-author surname + year -> the cited
PMID), never by guessing.

    python scripts/rob2_reference.py --run [SLUG ...]   (fetch figures; recorded calls)
    python scripts/rob2_reference.py [SLUG ...]         (replay)
Writes outputs/robgrade/reference/<slug>.json.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from reproducible_ai import model_source as ms  # noqa: E402

REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "rob2_reference")
OUT_DIR = os.path.join(ROOT, "outputs", "robgrade", "reference")
RUNS = os.path.join(ROOT, "registry", "model_proposals", "rob2_reference_runs.json")
LANE = "robgrade"

# (slug) -> the comparator's per-trial risk-of-bias figure (caption-checked against its own JATS before reading)
FIGURES = {
    "probiotics-aad-prevention": {"pmid": "34385227", "fig_id": "F2", "caption_has": "Risk of bias summary"},
    # NOT calibration figures (read 10 Oct): glp1 34526024 Fig2 is a percentage graph across trials (per_study=false);
    # colchicine-secondary 36176989 F2 is ROBINS-I (non-randomised studies), not comparable with RoB 2
    # metformin-pcos 31845767 (Cochrane CD013505): NOT CC in any held copy -> refused by comparator_open (D8)
    "metformin-pcos-ovulation": {"pmid": "31845767", "fig_id": "CD013505-fig-0003", "caption_has": "Risk of bias' summary"},
    # esketamine 37377288 f2: both readers (10 Oct) -- a bespoke checklist, not per-study rows: not a calibration figure
    "balanced-crystalloids-vs-saline-mortality": {"pmid": "30140441", "fig_id": "Fig2", "caption_has": "Risk of bias summary"},
    "ticagrelor-vs-clopidogrel-acs": {"pmid": "28545073", "fig_id": "pone.0177872.g003", "caption_has": "Risk of bias summary"},
    "iv-iron-hfref-hosp": {"pmid": "39727669", "fig_id": "diseases-12-00339-f002", "caption_has": "risk of bias assessment"},
}

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["legible", "per_study", "tool", "columns", "legend", "rows", "notes"],
    "properties": {
        "legible": {"type": "boolean"}, "per_study": {"type": "boolean"},
        "tool": {"type": "string"}, "legend": {"type": "string"}, "notes": {"type": "string"},
        "columns": {"type": "array", "items": {"type": "string"}},
        "rows": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["label", "cells"],
            "properties": {"label": {"type": "string"},
                           "cells": {"type": "array", "items": {"type": "string",
                                                                "enum": ["low", "unclear", "some concerns", "high",
                                                                         "not shown"]}}}}}}}

INSTR = """You are reading ONE risk-of-bias figure from a published meta-analysis. TRANSCRIBE what it shows; judge nothing.

- per_study: true only if the figure shows a judgement for EACH study (a 'summary' grid / traffic-light plot). A graph of
  percentages across studies is not per-study: then per_study=false and rows=[].
- columns: the risk-of-bias items/domains exactly as labelled, left to right (add 'Overall' only if the figure has it).
- rows: one per study, top to bottom: the study label exactly as printed, and one cell per column in the same order.
- cells: map each mark through the figure's OWN legend: low (usually green / '+'), unclear (yellow / '?'),
  some concerns (yellow / '-' in RoB 2 plots that say so), high (red / 'x' or '-'), not shown (empty).
- tool: what the figure or legend says it is (e.g. 'Cochrane RoB 1', 'RoB 2'); legend: the legend text as printed.
- If the figure cannot be read reliably, legible=false.
Reply with ONE JSON object with EXACTLY these keys (every row MUST have "label" and as many "cells" as "columns"):
{"legible": true, "per_study": true, "tool": "...", "legend": "...", "columns": ["..."],
 "rows": [{"label": "<study label as printed>", "cells": ["low" | "unclear" | "some concerns" | "high" | "not shown", ...]}],
 "notes": ""}
"""

ADJ = """Two readers transcribed this risk-of-bias figure and DISAGREE on the cells listed below. Look at the figure and
give, for each listed cell, what the figure shows (low / unclear / some concerns / high / not shown), using the figure's
own legend. Either reader may be wrong. Reply with ONE JSON object:
{"cells": [{"label": <study label as printed>, "column": <column label>, "value": <one of the five>}], "notes": ""}
"""
ADJ_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["cells", "notes"],
              "properties": {"notes": {"type": "string"}, "cells": {"type": "array", "items": {
                  "type": "object", "additionalProperties": False, "required": ["label", "column", "value"],
                  "properties": {"label": {"type": "string"}, "column": {"type": "string"},
                                 "value": {"type": "string", "enum": ["low", "unclear", "some concerns", "high",
                                                                      "not shown"]}}}}}}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = f"{p}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, p)


def norm_label(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\[[^\]]*\]", "", s))


# ------------------------------------------------------------------------------------------------ figure and references

def comparator_open(pmid):
    """D8 for a FIGURE: a figure is part of its article, so it may be shown to a model only when one of the comparator's
    held JATS copies names a Creative Commons licence in its own <permissions> (record_licence.jats_licence). 10 Oct:
    the metformin Cochrane review 31845767 (no licence statement in any held copy) was read before this gate existed;
    its records are quarantined outside the repo."""
    import glob
    from reproducible_ai import record_licence as rl
    fs = sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", str(pmid), "*.xml")))
    return any(rl.jats_licence(f) == "CC" for f in fs)


def figure(slug, run):
    import g1_forest_reader as gfr
    f = FIGURES[slug]
    if not comparator_open(f["pmid"]):
        return None, "D8_COMPARATOR_NOT_CC"
    jp = gfr.jats_path(f["pmid"])
    if not jp:
        return None, "NO_JATS"
    for el in ET.parse(jp).getroot().iter("fig"):
        if el.get("id") != f["fig_id"]:
            continue
        cap = " ".join("".join(x.itertext()) for x in el.iter("caption"))
        g = el.find(".//graphic")
        if g is None or f["caption_has"].lower() not in re.sub(r"\s+", " ", cap).lower():
            return None, "CAPTION_MISMATCH"
        href = g.get("{http://www.w3.org/1999/xlink}href")
        ip, meta = gfr.acquire_image(f["pmid"], gfr.pmcid_of(f["pmid"]), href) if run else gfr.cached_image(f["pmid"], href)
        if not ip:
            return None, "IMAGE_NOT_HELD:" + str((meta or {}).get("why"))
        with open(ip, "rb") as fh:
            b = fh.read()
        return {"slug": slug, **f, "caption": cap.strip()[:300], "image_path": ip,
                "image_ref": os.path.relpath(ip, ROOT).replace(os.sep, "/"), "image_sha256": hashlib.sha256(b).hexdigest(),
                "image_url": (meta or {}).get("url"), "jats": os.path.relpath(jp, ROOT).replace(os.sep, "/")}, "SELECTED"
    return None, "FIGURE_ABSENT"


def references(pmid):
    """[(surname, year, pmid, ref text)] from the comparator's own JATS reference list."""
    import g1_forest_reader as gfr
    jp = gfr.jats_path(pmid)
    out = []
    if not jp:
        return out
    for r in ET.parse(jp).getroot().iter("ref"):
        sn = r.find(".//surname")
        yr = r.find(".//year")
        pm = [x for x in r.iter("pub-id") if x.get("pub-id-type") == "pmid"]
        txt = " ".join("".join(r.itertext()).split())
        y = (yr.text if yr is not None else None) or (re.search(r"\b(19|20)\d\d\b", txt) or [None])[0]
        out.append(((sn.text if sn is not None else "") or "", str(y or ""), pm[0].text.strip() if pm else None, txt[:200]))
    return out


AUTHORS = os.path.join(ROOT, "outputs", "robgrade", "pubmed_first_authors.json")


def pool_authors(pmids, run):
    """[(first-author surname, year, pmid, basis)] for OUR pool trials, from PubMed esummary (cached with the response
    sha256): the fallback binding when the comparator's held JATS has no reference list (a PMC-page-derived file)."""
    cache = _j(AUTHORS) if os.path.exists(AUTHORS) else {}
    need = [p for p in pmids if p not in cache]
    if need and run:
        from harness import http
        raw = None
        for attempt in range(5):                 # PubMed answers 429 to bursts: back off, never fail silently
            try:
                st, raw = http.get_raw("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                                       {"db": "pubmed", "id": ",".join(need), "retmode": "json"}, tries=1, timeout=60)
                break
            except RuntimeError:
                time.sleep(5 * 2 ** attempt)
        if raw is None:
            raise RuntimeError(f"PubMed esummary failed after back-off for {need}")
        d = json.loads(raw.decode("utf-8"))
        for p in need:
            e = (d.get("result") or {}).get(p) or {}
            au = (e.get("authors") or [{}])[0].get("name") or ""
            cache[p] = {"first_author": au, "pubdate": e.get("pubdate"), "response_sha256": hashlib.sha256(raw).hexdigest()}
        _save(AUTHORS, cache)
    out = []
    for p in pmids:
        e = cache.get(p)
        if e:
            sur = (e["first_author"] or "").split(" ")[0]
            yr = (re.search(r"(19|20)\d\d", e.get("pubdate") or "") or [None])[0]
            out.append((sur, str(yr or ""), p, f"PubMed esummary: first author {e['first_author']}, {e.get('pubdate')}"))
    return out


def bind_label(label, refs):
    """A figure label ('Arvola 1999', 'Arvola et al., 1999 [12]') -> (pmid, basis) through the reference list: the one
    reference whose first-author surname and year both match; none or several -> (None, why)."""
    m = re.match(r"\s*([A-Za-zÀ-ɏ'\- ]+?)(?:\s+et\s+al\.?)?,?\s*\(?((?:19|20)\d\d)", label or "")
    if not m:
        return None, "LABEL_HAS_NO_SURNAME_YEAR"
    sur, yr = norm_label(m.group(1).split()[-1] if m.group(1).split() else ""), m.group(2)
    hits = [r for r in refs if norm_label(r[0]) == sur and r[1] == yr]
    if len(hits) != 1:
        return None, f"REFERENCE_MATCHES_{len(hits)}"
    return (hits[0][2], f"reference list: {hits[0][3][:120]}") if hits[0][2] else (None, "REFERENCE_HAS_NO_PMID")


# ------------------------------------------------------------------------------------------------ calls

def _call(item, who, prompt, schema):
    from reproducible_ai import model_call_live as mcl
    caller = {"file": "scripts/rob2_reference.py", "line": f"call:{who}", "lane": LANE,
              "purpose": f"RoB calibration reference ({who}): {item['slug']} comparator {item['pmid']} fig {item['fig_id']}"}
    dig = [{"ref": item["image_ref"], "sha256": item["image_sha256"], "what": "comparator risk-of-bias figure image",
            "source_url": item.get("image_url")}]
    for attempt in range(4):
        if who == "agy":
            rec = mcl.agy_call(prompt, schema=schema, caller=caller, input_digests=dig, timeout_s=900,
                               images=(item["image_path"],))
        else:
            rec = mcl.call(prompt, schema=schema, model="gpt-6-astra", effort="high" if who == "adjudicator" else "medium",
                           caller=caller, input_digests=dig, timeout_s=1200, images=(item["image_path"],))
        ms.write_record(rec, REC_DIR)
        if rec["state"] == "RAN_OK" or attempt == 3:
            break
        time.sleep(30 * 3 ** attempt)
    return {"record_id": rec["record_id"], "state": rec["state"], "error": rec.get("error"),
            "prompt_sha256": hashlib.sha256(prompt).hexdigest(), "model": rec["model"]["id_reported"]}


def _parse(run):
    if not run or run.get("state") != "RAN_OK":
        return None
    t = ms.replay(ms.load_record(os.path.join(REC_DIR, run["record_id"] + ".json"))).decode("utf-8", "replace").strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    try:
        return json.loads(m.group(1) if m else t)
    except ValueError:
        return None


def prompt(item):
    extra = ("\n" + item["instruction"] + "\n") if item.get("instruction") else ""
    where = "The figure is the attached image."
    return (INSTR + extra + f"\n{where}\nFIGURE CAPTION (from the article): {item['caption']}\n").encode("utf-8")


def prompt_agy(item):
    ext = os.path.splitext(item["image_path"])[1].lower()
    extra = ("\n" + item["instruction"] + "\n") if item.get("instruction") else ""
    return (INSTR + extra + f"\nThe figure is the image file image_0{ext} in the current directory: read that file and "
            f"nothing else.\nFIGURE CAPTION (from the article): {item['caption']}\n").encode("utf-8")


# ------------------------------------------------------------------------------------------------ comparison

def shape_problems(reading):
    """A reading is usable only if every row has a label and one cell per column (2026-10-10: agy rows came back with no
    'label' key, nothing paired, and every cell fell to the adjudicator -- a single reading posing as a dual one)."""
    if not reading:
        return ["NO_READING"]
    if not reading.get("legible") or not reading.get("per_study"):
        return []
    cols = reading.get("columns") or []
    probs = []
    for i, r in enumerate(reading.get("rows") or []):
        if not isinstance(r, dict) or not str(r.get("label") or "").strip():
            probs.append(f"ROW_{i}_NO_LABEL")
        elif len(r.get("cells") or []) != len(cols):
            probs.append(f"ROW_{i}_CELLS_{len(r.get('cells') or [])}_NE_COLUMNS_{len(cols)}")
    return probs


def cells(reading):
    """{(norm label, column index): value} + the label/column text; a malformed reading yields nothing."""
    out, labels = {}, {}
    if not reading or not reading.get("legible") or not reading.get("per_study") or shape_problems(reading):
        return out, labels
    for r in reading.get("rows") or []:
        k = norm_label(r.get("label"))
        labels[k] = r.get("label")
        for i, v in enumerate(r.get("cells") or []):
            out[(k, i)] = v
    return out, labels


def compare(a, b):
    ca, la = cells(a)
    cb, lb = cells(b)
    cols_a, cols_b = [norm_label(c) for c in (a or {}).get("columns") or []], [norm_label(c) for c in (b or {}).get("columns") or []]
    agreed, disputed = {}, {}
    if cols_a != cols_b:
        return agreed, {"__columns__": (a and a.get("columns"), b and b.get("columns"))}, la
    for k in sorted(set(ca) | set(cb)):
        x, y = ca.get(k), cb.get(k)
        if x == y and x is not None:
            agreed[k] = x
        else:
            disputed[k] = (x, y)
    return agreed, disputed, la or lb


def process(slug, runs, live, pools):
    item, why = figure(slug, live)
    if not item:
        return {"slug": slug, "state": why}
    r = dict(runs.get(slug) or {})
    P = {"codex": prompt(item), "agy": prompt_agy(item)}
    if live:
        futs = {w: pools[w].submit(_call, item, w, P[w], SCHEMA) for w in ("codex", "agy")
                if not ((r.get(w) or {}).get("state") == "RAN_OK" and r[w]["prompt_sha256"] == hashlib.sha256(P[w]).hexdigest())}
        for w, f in futs.items():
            r[w] = f.result()
    a, b = _parse(r.get("codex")), _parse(r.get("agy"))
    malformed = {w: shape_problems(x) for w, x in (("codex", a), ("agy", b)) if shape_problems(x)}
    if malformed:
        return {"slug": slug, "state": "READINGS_MALFORMED", "problems": malformed, "runs": r}
    agreed, disputed, labels = compare(a, b)
    cols = (a or {}).get("columns") or []
    adjud = {}
    if "__columns__" not in disputed and len(disputed) > len(agreed):
        # the readers diverge on most of the figure: a structural disagreement, never settled by one more reading
        return {"slug": slug, "state": "READERS_DIVERGE", "cells": {"agreed": len(agreed), "disputed": len(disputed)},
                "runs": r}
    if disputed and "__columns__" not in disputed:
        ask = [{"label": labels.get(k[0], k[0]), "column": cols[k[1]] if k[1] < len(cols) else str(k[1]),
                "reader 1": v[0], "reader 2": v[1]} for k, v in disputed.items()]
        pa = (ADJ + "\nCELLS:\n" + json.dumps(ask, indent=1, ensure_ascii=False) +
              f"\n\nThe figure is the attached image. CAPTION: {item['caption']}\n").encode("utf-8")
        if live and not ((r.get("adjudicator") or {}).get("state") == "RAN_OK"
                         and r["adjudicator"]["prompt_sha256"] == hashlib.sha256(pa).hexdigest()):
            r["adjudicator"] = pools["codex"].submit(_call, item, "adjudicator", pa, ADJ_SCHEMA).result()
        d = _parse(r.get("adjudicator")) or {}
        colidx = {norm_label(c): i for i, c in enumerate(cols)}
        for c in d.get("cells") or []:
            k = (norm_label(c.get("label")), colidx.get(norm_label(c.get("column"))))
            if k in disputed and c.get("value"):
                adjud[k] = c["value"]
    refs = references(item["pmid"])
    import rob2_dual
    pool = pool_authors(rob2_dual.served_primary(slug)[1], live)
    rows = {}
    for lk, lab in labels.items():
        pm, basis = bind_label(lab, refs)
        if pm is None:                       # the comparator's reference list did not bind it: try OUR pool's PubMed records
            pm2, basis2 = bind_label(lab, pool)
            if pm2:
                pm, basis = pm2, basis2 + f" (comparator reference list: {basis})"
        rows[lab] = {"pmid": pm, "binding": basis,
                     "cells": {cols[i] if i < len(cols) else str(i): (agreed.get((lk, i)) or adjud.get((lk, i)))
                               for i in range(len(cols))},
                     "how": {cols[i] if i < len(cols) else str(i): ("agreed" if (lk, i) in agreed else
                                                                    "adjudicated" if (lk, i) in adjud else "unresolved")
                             for i in range(len(cols))}}
    return {"slug": slug, "state": "READ" if a and b else "NO_TWO_READINGS", "figure": {k: item[k] for k in (
        "pmid", "fig_id", "caption", "image_ref", "image_sha256", "image_url", "jats")}, "tool": (a or {}).get("tool"),
            "legend": (a or {}).get("legend"), "columns": cols, "rows": rows,
            "cells": {"agreed": len(agreed), "adjudicated": len(adjud),
                      "unresolved": len([k for k in disputed if k not in adjud])},
            "runs": r}


def main(argv):
    live = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")] or sorted(FIGURES)
    runs = _j(RUNS) if os.path.exists(RUNS) else {}
    pools = {"codex": cf.ThreadPoolExecutor(8), "agy": cf.ThreadPoolExecutor(4)}
    import rob2_dual
    for s in slugs:                              # PubMed first-author records, fetched serially BEFORE the threads (429)
        pool_authors(rob2_dual.served_primary(s)[1], live)
    with cf.ThreadPoolExecutor(5) as drv:
        for slug, res in zip(slugs, drv.map(lambda s: process(s, runs, live, pools), slugs)):
            runs[slug] = res.get("runs") or runs.get(slug) or {}
            _save(os.path.join(OUT_DIR, f"{slug}.json"), res)
            print(slug, res.get("state"), res.get("tool"), res.get("cells"), flush=True)
    _save(RUNS, runs)
    for p in pools.values():
        p.shutdown()


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
