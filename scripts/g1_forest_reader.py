"""G1 DUAL-MODEL FOREST-PLOT READER: a comparator's per-trial rows, read twice by two model FAMILIES, admitted only by
agreement AND by deterministic reconstruction of the figure's printed pool under the meta's STATED model.

    python scripts/g1_forest_reader.py --run SLUG [SLUG ...]   (fetch figures; recorded codex + agy calls; then gate)
    python scripts/g1_forest_reader.py SLUG [SLUG ...]         (replay only: no network, no model)
    python scripts/g1_forest_reader.py --verify-replay [SLUG ...]

  figure     the comparator's forest figure for the topic outcome, chosen from ITS OWN JATS captions
             (k_gap_forest_plot.select_figure), or a TARGETS entry naming the figure, whose caption must contain the
             quoted words (checked against the JATS, never trusted). Image bytes: NCBI's PMC OA bucket, else the PMC
             article page's own figure URL (author manuscripts are not in the bucket). URL + sha256 are recorded.
  reading A  codex (`codex exec`, image attached with -i)       reproducible_ai.model_call_live.call
  reading B  agy   (`agy --print`, Gemini; image in the workdir) reproducible_ai.model_call_live.agy_call
             each call is a model_call_record/1 under evidence/model_calls/forest/, replayed byte-identically.
  agree      a row is PROPOSED only when both readings carry it (normalised label) and every printed number agrees
             within the figure's printed rounding; the pooled row must agree the same way. Disagreements are
             refused with BOTH readings shown.
  stated     the meta's pooling model, typed from ITS OWN text (DerSimonian-Laird / Paule-Mandel / REML / fixed /
             Mantel-Haenszel / Hartung-Knapp). A one-stage IPD model (stratified Cox) is not reconstructable from
             aggregate rows: the figure is refused, never approximated.
  accept     the agreed rows, pooled by the stated model(s) only, reproduce the figure's printed pooled estimate AND
             CI within rounding (printed half-unit + one half-unit of row-rounding propagation). Otherwise the WHOLE
             figure is refused.
Accepted rows are SECONDARY-source comparator rows (provenance MODEL_PROPOSAL_DUAL:<codex>+<agy>): the comparator's
own numbers, for per-trial comparison. They are NEVER pool inputs, and a row sourced only from meta X never counts
toward agreement with X (harness.secondary_meta.g1_countable). Nothing here is in the served-number path: replay
reads records; only --run reaches a model (tests/test_no_model_call_in_pinned_path.py).
Writes registry/model_proposals/g1_forest_reader.json (+ _runs.json ledger).
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_forest_plot as fp  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_reader.json")
RUNS = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_reader_runs.json")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "forest")
COMP = fp.COMP
LANE = "g1/forest-reader"
CODEX_MODEL, CODEX_EFFORT = fp.MODEL, "medium"
FETCH_DATE = "2026-10-02"
CAPTION = re.compile(r"forest|pooled|hazard ratio|risk ratio|odds ratio|relative risk|meta-analys[ie]s of", re.I)

# A figure named by hand when the deterministic selector cannot choose. The caption must CONTAIN `caption_has`
# (checked against the comparator's JATS); `instruction` tells both readers which panel/subgroup to transcribe.
TARGETS: dict = {
    # COMBINE AF (Circulation 2022, PMC8800560, an author manuscript): its only forest plot is F1 (F3 is covariate
    # strata, F4 an HR-by-age curve the broadened caption match would otherwise pick). F1's rows may be outcomes, not
    # trials: the readers are asked to say so (row_kind), and the gate refuses non-study rows.
    "noac-vs-warfarin-af-stroke": {
        "fig_id": "F1", "caption_has": "Forest plots showing hazard ratios comparing standard-dose",
        "instruction": "Transcribe ONLY the left panel ('Efficacy Outcomes'). Report row_kind honestly: if each row "
                       "is an outcome rather than a trial, say row_kind=\"outcome\". For rows, give the standard-dose "
                       "DOAC vs warfarin row of each entry; for pooled, the 'Stroke or Systemic Embolism' standard-dose "
                       "row."},
}

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["legible", "row_kind", "measure", "model_printed", "rows", "pooled", "notes"],
    "properties": {
        "legible": {"type": "boolean"},
        "row_kind": {"type": "string", "enum": ["study", "outcome", "subgroup", "mixed", "none"]},
        "measure": {"type": "string"},
        "model_printed": {"type": ["string", "null"]},
        "notes": {"type": "string"},
        "pooled": {"type": "object", "additionalProperties": False, "required": ["label", "effect", "lower", "upper"],
                   "properties": {k: {"type": ["string", "null"]} for k in ("label", "effect", "lower", "upper")}},
        "rows": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["label", "effect", "lower", "upper", "weight_pct", "events_t", "n_t", "events_c", "n_c"],
            "properties": {k: {"type": ["string", "null"]} for k in
                           ("label", "effect", "lower", "upper", "weight_pct", "events_t", "n_t", "events_c", "n_c")}}},
    },
}
INSTR = """You are reading ONE forest-plot figure from a published meta-analysis. Transcribe what is PRINTED; do not
compute, infer, round or correct anything. Answer with ONE JSON object only, matching this JSON schema exactly:
{schema}

- row_kind: what the figure's rows are -- "study" (one row per trial/study), "outcome" (one row per outcome, each
  already pooled), "subgroup" (one row per subgroup), "mixed", or "none".
- rows: every study row of the panel you are asked for, in the order printed: the study label exactly as printed,
  and the point estimate and lower and upper confidence limits exactly as printed in the numeric column (same
  decimals, e.g. "0.81"). If the figure prints events and totals per arm, give them (events_t/n_t = the
  experimental arm, events_c/n_c = the control arm, as printed); else null. weight_pct as printed, else null.
- pooled: the pooled (overall / total / summary / diamond) row of that panel: its label and printed estimate and
  limits the same way.
- measure: the effect measure the figure states (e.g. HR, RR, OR, MD). model_printed: the pooling model words the
  figure prints (e.g. "M-H, Random, 95% CI", "Fixed effect"), else null.
- If the numeric column is not printed or not readable, set legible=false and leave rows empty. Never estimate a
  value from the position of a marker.
- notes: anything a checker needs (e.g. two pooled rows printed; which one you gave).
"""


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")


# ------------------------------------------------------------------ figure: selection and image acquisition

def jats_path(pmid):
    d = os.path.join(COMP, pmid)
    return next((os.path.join(d, f) for f in sorted(os.listdir(d), reverse=True) if f.endswith("_kgap_jats.xml")),
                None) if os.path.isdir(d) else None


def held_text(pmid):
    jp = jats_path(pmid)
    if not jp:
        return ""
    from kgap import k_gap
    with open(jp, "rb") as fh:
        return k_gap.jats_body_text(fh.read())


def figure_for(slug, pmid):
    """(figure dict, why). A TARGETS entry is honoured only if its figure exists and its caption contains the words."""
    jp = jats_path(pmid)
    if not jp:
        return None, "NO_JATS"
    t = TARGETS.get(slug)
    if t:
        for f in ET.parse(jp).getroot().iter("fig"):
            if f.get("id") != t["fig_id"]:
                continue
            cap = " ".join("".join(x.itertext()) for x in f.iter("caption"))
            g = f.find(".//graphic")
            if g is None or t["caption_has"].lower() not in re.sub(r"\s+", " ", cap).lower():
                return None, "TARGET_CAPTION_MISMATCH"
            return {"fig_id": t["fig_id"], "href": g.get(fp.XL), "caption": cap.strip()[:300], "panel": t.get("panel"),
                    "panel_title": t.get("panel_title"), "instruction": t.get("instruction"),
                    "selected_by": f"TARGETS (caption contains {t['caption_has']!r})"}, "SELECTED"
        return None, "TARGET_FIGURE_ABSENT"
    # a caption that says "forest" first; the broader pooled/ratio captions only when no forest caption qualifies (a
    # broad match alone picked COMBINE AF's HR-by-age curve)
    fig, why = fp.select_figure(slug, pmid, jats_date=os.path.basename(jp)[:10])
    if not fig:
        fig, why2 = fp.select_figure(slug, pmid, jats_date=os.path.basename(jp)[:10], caption_re=CAPTION)
        why = why if fig is None and why2.startswith("NO_OUTCOME") else why2
    if fig:
        fig["selected_by"] = "k_gap_forest_plot.select_figure (comparator's own captions)"
    return fig, why


def pmcid_of(pmid):
    for f in sorted(os.listdir(os.path.join(COMP, pmid))) if os.path.isdir(os.path.join(COMP, pmid)) else []:
        if f.endswith("idconv.json"):
            m = re.search(r'"pmcid"\s*:\s*"(PMC\d+)"', open(os.path.join(COMP, pmid, f), encoding="utf-8", errors="ignore").read())
            if m:
                return m.group(1)
    return None


def _image_name(href):
    return href if re.search(r"\.(jpe?g|png|gif|tiff?)$", href, re.I) else href + ".jpg"


def cached_image(pmid, href):
    """The held image for this figure (bucket fetch or article-page fetch), with its provenance; offline."""
    name = _image_name(href)
    d = os.path.join(COMP, pmid)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith("_" + name) and ("_kgap_" in f or "_forest_" in f):
            p = os.path.join(d, f)
            meta = _j(p + ".meta.json") if os.path.exists(p + ".meta.json") else {}
            return p, meta
    return None, None


def acquire_image(pmid, pmcid, href):
    """Bucket first (k_gap_forest_plot.fetch_image), then the figure URL the PMC article page itself links."""
    p, meta = cached_image(pmid, href)
    if p:
        return p, meta
    fpth, b = fp.fetch_image(pmid, pmcid, href)
    if fpth:
        return fpth, _j(fpth + ".meta.json")
    from harness import http
    name = _image_name(href)
    page = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    try:
        st, html = http.get_raw(page, tries=2, timeout=60)
    except Exception as exc:  # noqa: BLE001 - recorded as the refusal reason
        return None, {"why": f"ARTICLE_PAGE_FETCH_FAILED:{type(exc).__name__}"}
    urls = sorted(set(re.findall(r'https://cdn\.ncbi\.nlm\.nih\.gov/pmc/blobs/[^"\s]+/' + re.escape(name),
                                 html.decode("utf-8", "replace"))))
    if len(urls) != 1:
        return None, {"why": f"ARTICLE_PAGE_FIGURE_URL_COUNT_{len(urls)}", "page": page}
    try:
        st2, b = http.get_raw(urls[0], tries=2, timeout=60)
    except Exception as exc:  # noqa: BLE001
        return None, {"why": f"IMAGE_FETCH_FAILED:{type(exc).__name__}", "url": urls[0]}
    if not (b[:3] == b"\xff\xd8\xff" or b[:4] == b"\x89PNG"):
        return None, {"why": "IMAGE_NOT_AN_IMAGE", "url": urls[0]}
    fpth = os.path.join(COMP, pmid, f"{FETCH_DATE}_forest_{name}")
    os.makedirs(os.path.dirname(fpth), exist_ok=True)
    with open(fpth, "wb") as fh:
        fh.write(b)
    meta = {"url": urls[0], "http_status": st2, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "via": "PMC article page figure link (not in the PMC OA bucket)", "article_page": page,
            "article_page_sha256": hashlib.sha256(html).hexdigest(), "fetched": FETCH_DATE}
    _save(fpth + ".meta.json", meta)
    return fpth, meta


# ------------------------------------------------------------------ the two recorded readings

def prompt_bytes(fig, reader):
    extra = ""
    if fig.get("instruction"):
        extra = "\n" + fig["instruction"].strip() + "\n"
    elif fig.get("panel"):
        extra = (f"\nThis figure has several panels. Transcribe ONLY panel ({fig['panel']}), which the caption titles "
                 f"'{fig['panel_title']}'. Ignore every other panel; its rows and pooled row are not wanted.\n")
    where = ("The figure is the attached image." if reader == "codex" else
             "The figure is the image file image_0" + os.path.splitext(fig.get("image_name") or ".jpg")[1].lower() +
             " in the current directory: read that file and nothing else.")
    return (INSTR.replace("{schema}", json.dumps(SCHEMA, sort_keys=True)) + f"\n{where}\nFIGURE CAPTION (from the "
            f"article): {fig['caption']}\n" + extra).encode("utf-8")


def run_reader(item, reader):
    from reproducible_ai import model_call_live as mcl
    p = prompt_bytes(item["figure"], reader)
    caller = {"file": "scripts/g1_forest_reader.py", "line": f"run_reader:{reader}", "lane": LANE,
              "purpose": f"G1 dual forest read ({reader}) {item['slug']} meta {item['pmid']} fig {item['figure']['fig_id']}"}
    dig = [{"ref": item["image_ref"], "sha256": item["image_sha256"], "what": "comparator forest-plot figure image",
            "source_url": item.get("image_url")}]
    if reader == "codex":
        rec = mcl.call(p, schema=SCHEMA, model=CODEX_MODEL, effort=CODEX_EFFORT, caller=caller, input_digests=dig,
                       timeout_s=900, images=(item["image_path"],))
    else:
        rec = mcl.agy_call(p, schema=SCHEMA, caller=caller, input_digests=dig, timeout_s=600, images=(item["image_path"],))
    ms.write_record(rec, REC_DIR)
    return {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": hashlib.sha256(p).hexdigest(),
            "image_sha256": item["image_sha256"], "model": rec["model"]["id_reported"], "error": rec.get("error")}


def parse_reading(raw: bytes):
    """The model's final message -> a reading dict, or (None, why). Deterministic: one JSON object, optionally fenced."""
    t = raw.decode("utf-8", "replace").strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    if m:
        t = m.group(1)
    try:
        d = json.loads(t)
    except ValueError:
        return None, "NOT_JSON"
    probs = shape_problems(d)
    return (d, None) if not probs else (None, "SCHEMA:" + ";".join(probs[:3]))


def shape_problems(d):
    if not isinstance(d, dict):
        return ["not an object"]
    out = [f"missing {k}" for k in SCHEMA["required"] if k not in d]
    if out:
        return out
    if not isinstance(d["rows"], list) or not isinstance(d["pooled"], dict) or not isinstance(d["legible"], bool):
        return ["rows/pooled/legible types"]
    for r in d["rows"]:
        if not isinstance(r, dict) or any(k not in r for k in SCHEMA["properties"]["rows"]["items"]["required"]):
            return ["row shape"]
        if any(v is not None and not isinstance(v, str) for v in r.values()):
            return ["row value not a string"]
    return []


# ------------------------------------------------------------------ agreement (two readings -> proposed rows)

def _norm_label(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def _num(s):
    return fp._num(s) if s is not None else None


def agree_value(a, b):
    """Two printed numbers agree within the figure's printed rounding: |a-b| <= half a unit of the finer printing.
    Returns the agreed printed string (the finer one) or None."""
    x, y = _num(a), _num(b)
    if x is None and y is None and a and b and " ".join(str(a).lower().split()) == " ".join(str(b).lower().split()):
        return a           # the same printed words ('Not estimable'): agreed as text, never pooled as a number
    if x is None or y is None:
        return None
    if abs(x - y) > 0.5 * 10 ** (-max(fp._dec(a), fp._dec(b))) + 1e-9:
        return None
    return a if fp._dec(a) >= fp._dec(b) else b


def agree_count(a, b):
    """Integers equal exactly; a thousands separator (comma, space, thin space) is not a digit ('10 637' = '10637')."""
    if a is None and b is None:
        return True, None
    sa, sb = (re.sub(r"[,\s   ]", "", str(x or "")) for x in (a, b))
    return (sa == sb and sa.isdigit()), (int(sa) if sa.isdigit() else None)


def agree(ra, rb):
    """Readings A and B -> (proposed rows, refused rows, pooled or None, problems). Rows are matched by normalised
    label (order-preserving); every refusal carries BOTH readings."""
    probs, proposed, refused = [], [], []
    for k in ("legible",):
        if not (ra.get(k) and rb.get(k)):
            probs.append("NOT_LEGIBLE_IN_BOTH")
    if ra.get("row_kind") != "study" or rb.get("row_kind") != "study":
        probs.append(f"ROWS_ARE_NOT_STUDIES:{ra.get('row_kind')}/{rb.get('row_kind')}")
    la = [_norm_label(r.get("label")) for r in ra.get("rows") or []]
    lb = [_norm_label(r.get("label")) for r in rb.get("rows") or []]
    if len(set(la)) != len(la) or len(set(lb)) != len(lb):
        probs.append("DUPLICATE_ROW_LABELS")
    by_b = {_norm_label(r.get("label")): r for r in rb.get("rows") or []}
    for r in ra.get("rows") or []:
        s = by_b.pop(_norm_label(r.get("label")), None)
        if s is None:
            refused.append({"label": r.get("label"), "why": "ONLY_IN_READING_A", "a": r, "b": None})
            continue
        vals, why = {}, []
        for k in ("effect", "lower", "upper"):
            v = agree_value(r.get(k), s.get(k))
            if v is None:
                why.append(f"{k.upper()}_DISAGREES")
            vals[k] = v
        for k in ("events_t", "n_t", "events_c", "n_c"):
            ok, v = agree_count(r.get(k), s.get(k))
            if not ok:
                why.append(f"{k.upper()}_DISAGREES")
            vals[k] = v
        if why:
            refused.append({"label": r.get("label"), "why": ",".join(why), "a": r, "b": s})
        else:
            proposed.append({"label": r.get("label"), **vals})
    for s in by_b.values():
        refused.append({"label": s.get("label"), "why": "ONLY_IN_READING_B", "a": None, "b": s})
    pa, pb = ra.get("pooled") or {}, rb.get("pooled") or {}
    pooled = {k: agree_value(pa.get(k), pb.get(k)) for k in ("effect", "lower", "upper")}
    if None in pooled.values():
        probs.append("POOLED_ROW_DISAGREES")
        pooled = None
    if refused:
        probs.append(f"ROWS_DISAGREE:{len(refused)}")
    ma, mb = fp.is_ratio(ra.get("measure")), fp.is_ratio(rb.get("measure"))
    if ma != mb:
        probs.append("MEASURE_DISAGREES")
    return proposed, refused, pooled, probs


# ------------------------------------------------------------------ the meta's STATED model, from its own text

# a one-stage IPD analysis: a sentence that names individual patient/participant data AND a one-stage or Cox model, and
# does not negate having it ("we did not have individual patient data" is an aggregate meta's limitation)
_IPD_SENT = re.compile(r"individual[- ](?:patient|participant)(?:[- ]level)?[- ]data", re.I)
_IPD_MODEL = re.compile(r"one[- ]stage|stratified Cox|Cox (?:proportional[- ]hazards? )?model", re.I)
_IPD_NEG = re.compile(r"\b(?:not|no|without|lack(?:ed|ing)?|unavailab\w*|unable)\b", re.I)


def _ipd_sentence(t):
    """The evidence that the meta pooled individual patient data with a one-stage / Cox model: a non-negated sentence
    naming IPD use, AND a sentence naming the model (COMBINE AF: the abstract says 'used individual patient data ...
    stratified Cox model'; its body 'Cox models were stratified by trial allowing random effects'). Returns the
    quoted sentence(s), else None."""
    sents = re.split(r"(?<=[.;])\s+", t)
    data = next((s for s in sents if _IPD_SENT.search(s) and not _IPD_NEG.search(s)), None)
    model = next((s for s in sents if _IPD_MODEL.search(s) and not _IPD_NEG.search(s)), None)
    if not (data and model):
        return None
    return data if data == model else data + " [...] " + model


def model_text(pmid):
    """Where the meta states its pooling model: its OWN abstract + body (JATS), the reference list excluded."""
    jp = jats_path(pmid)
    if not jp:
        return ""
    root = ET.parse(jp).getroot()
    parts = ["".join(a.itertext()) for a in root.iter("abstract")]
    return re.sub(r"\s+", " ", " ".join(parts) + " " + held_text(pmid))
_TWO_STAGE = re.compile(r"two[- ]stage", re.I)
_METHOD_WORDS = [
    ("DL", re.compile(r"DerSimonian|\bD\s*-?\s*L\b(?= method| estimator| random)", re.I)),
    ("PM", re.compile(r"Paule[- ]Mandel", re.I)),
    ("REML", re.compile(r"restricted maximum[- ]likelihood|\bREML\b", re.I)),
    ("MH", re.compile(r"Mantel[- ]Haenszel|\bM-H\b", re.I)),
    ("FE", re.compile(r"fixed[- ]effects?\b|common[- ]effects?\b", re.I)),
    ("RE", re.compile(r"random[- ]effects?\b", re.I)),
    ("HK", re.compile(r"Hartung|Knapp|HKSJ", re.I)),
]


# A RevMan-style model label printed ON the figure ('M-H, Random, 95% CI') states the model for THAT analysis exactly,
# which the methods text usually does not ('random-effects if I2 > 50%, else fixed'): when both readers agree on such a
# label, it is the stated model. RevMan's 'IV, Random' is DerSimonian-Laird; 'M-H, Random' is DL about the M-H estimate.
_REVMAN = {("IV", "FIXED"): ["FE"], ("IV", "RANDOM"): ["DL"], ("M-H", "FIXED"): ["MH-FE"], ("M-H", "RANDOM"): ["MH-RE"]}


def revman_label(model_printed):
    m = re.search(r"\b(IV|M-H|MH|Inverse Variance|Mantel-Haenszel)\b\s*,\s*(Fixed|Random)\b", model_printed or "", re.I)
    if not m:
        return None
    meth = "IV" if m.group(1).upper() in ("IV", "INVERSE VARIANCE") else "M-H"
    return _REVMAN[(meth, m.group(2).upper())]


def stated_model(text, model_printed=None):
    """{methods: [...], quotes: {...}, state}. State NOT_RECONSTRUCTABLE for a one-stage IPD model; NOT_STATED when the
    text names no pooling model. Methods: the figure's own RevMan label when both readers agree on one; else the
    estimators the text names; a random-effects model with no named estimator is {DL, PM, REML} (each in the record)."""
    t = re.sub(r"\s+", " ", text or "")
    ipd0 = _ipd_sentence(t)
    rl = revman_label(model_printed)
    if rl and not ipd0:
        return {"state": "STATED", "methods": rl, "quotes": {"FIGURE_LABEL": model_printed},
                "basis": "the model label printed on the figure (both readings agree)"}
    quotes = {}
    for name, rx in _METHOD_WORDS:
        m = rx.search(t)
        if m:
            quotes[name] = t[max(0, m.start() - 80): m.end() + 80]
    if model_printed:
        for name, rx in _METHOD_WORDS:
            if name not in quotes and rx.search(model_printed):
                quotes[name] = f"[figure model label] {model_printed}"
        if re.search(r"\bRandom\b", model_printed) and "RE" not in quotes:
            quotes["RE"] = f"[figure model label] {model_printed}"
        if re.search(r"\bFixed\b", model_printed) and "FE" not in quotes:
            quotes["FE"] = f"[figure model label] {model_printed}"
    ipd = _ipd_sentence(t)
    if ipd and not _TWO_STAGE.search(t):
        return {"state": "NOT_RECONSTRUCTABLE", "methods": [], "quotes": {"IPD": ipd[:400]},
                "why": "one-stage individual-patient-data model: the pool is not a function of the printed per-trial rows"}
    methods = set()
    if "RE" in quotes or any(k in quotes for k in ("DL", "PM", "REML")):
        named = {k for k in ("DL", "PM", "REML") if k in quotes}
        methods |= named or {"DL", "PM", "REML"}
    if "FE" in quotes:
        methods.add("FE")
    if "MH" in quotes:
        methods.add("MH-FE" if "RE" not in quotes else "MH-RE")
        if "FE" in quotes:
            methods.add("MH-FE")
    if "HK" in quotes:
        methods |= {m + "+HK" for m in list(methods) if m in ("DL", "PM", "REML")}
    if not methods:
        return {"state": "NOT_STATED", "methods": [], "quotes": quotes}
    return {"state": "STATED", "methods": sorted(methods), "quotes": quotes}


# ------------------------------------------------------------------ reconstruction under the stated model

def has_counts(rows):
    return bool(rows) and all(isinstance(r.get(k), int) for r in rows for k in ("events_t", "n_t", "events_c", "n_c"))


def counts_yv(r, measure):
    """Per-study log RR / log OR and its variance from the printed 2x2 counts, as RevMan computes them: 0.5 added to
    every cell only when a cell is zero; a study with no events in either arm is not estimable (None)."""
    a, n1, c, n2 = r["events_t"], r["n_t"], r["events_c"], r["n_c"]
    if not (0 <= a <= n1 and 0 <= c <= n2) or n1 == 0 or n2 == 0 or (a == 0 and c == 0) or (a == n1 and c == n2):
        return None
    b, d = n1 - a, n2 - c
    if 0 in (a, b, c, d):
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    if measure == "OR":
        return math.log(a * d / (b * c)), 1 / a + 1 / b + 1 / c + 1 / d
    return math.log((a / (a + b)) / (c / (c + d))), 1 / a - 1 / (a + b) + 1 / c - 1 / (c + d)


def _yv(r, ratio, z=1.959963984540054):
    f = math.log if ratio else (lambda x: x)
    e, lo, hi = _num(r["effect"]), _num(r["lower"]), _num(r["upper"])
    if None in (e, lo, hi) or (ratio and min(e, lo, hi) <= 0):
        return None
    return f(e), ((f(hi) - f(lo)) / (2 * z)) ** 2


def _reml_tau2(y, v, iters=200):
    t2 = max(0.0, sum((a - sum(y) / len(y)) ** 2 for a in y) / max(1, len(y) - 1) - sum(v) / len(v))
    for _ in range(iters):
        w = [1 / (vi + t2) for vi in v]
        mu = sum(a * b for a, b in zip(w, y)) / sum(w)
        num = sum(wi ** 2 * ((yi - mu) ** 2 - vi) for wi, yi, vi in zip(w, y, v)) + sum(w2 for w2 in (wi ** 2 for wi in w)) / sum(w)
        new = max(0.0, num / sum(wi ** 2 for wi in w))
        if abs(new - t2) < 1e-12:
            return new
        t2 = new
    return t2


def _mh(rows, measure):
    """Mantel-Haenszel fixed-effect RR or OR from printed counts (Greenland-Robins variance). None without counts."""
    if any(r.get(k) is None for r in rows for k in ("events_t", "n_t", "events_c", "n_c")):
        return None
    num = den = 0.0
    pr = ps = qs = rr_p = rr_q = rr_r = 0.0
    for r in rows:
        a, n1, c, n2 = r["events_t"], r["n_t"], r["events_c"], r["n_c"]
        b, d = n1 - a, n2 - c
        if 0 in (a, b, c, d):
            # RevMan 5 (and R meta's default, MH.exact=FALSE): 0.5 added to the cells of a zero-cell study in the M-H
            # estimate too (checked against meta::metabin on PMID 34385227's 42 rows)
            a, b, c, d = a + .5, b + .5, c + .5, d + .5
            n1, n2 = a + b, c + d
        n = n1 + n2
        if measure == "OR":
            num += a * d / n
            den += b * c / n
            P, Q = (a + d) / n, (b + c) / n
            R, S = a * d / n, b * c / n
            pr += P * R
            ps += P * S + Q * R
            qs += Q * S
            rr_p, rr_q = rr_p + R, rr_q + S
        else:
            num += a * n2 / n
            den += c * n1 / n
            rr_r += (n1 * n2 * (a + c) - a * c * n) / n ** 2
    if num <= 0 or den <= 0:
        return None
    est = math.log(num / den)
    var = (pr / (2 * rr_p ** 2) + ps / (2 * rr_p * rr_q) + qs / (2 * rr_q ** 2)) if measure == "OR" else rr_r / (num * den)
    return est, var


def reconstruct(rows, ratio, measure, methods, z=1.959963984540054):
    """{method: (est, lo, hi)} for every stated method that can be computed from the agreed rows."""
    from scipy import stats
    from harness.synth import _paule_mandel_tau2
    g = math.exp if ratio else (lambda x: x)
    if ratio and measure.upper() in ("RR", "OR") and has_counts(rows):
        # dichotomous data printed per arm: the meta pooled the COUNTS; a not-estimable study (no events in either arm)
        # carries no weight, exactly as RevMan prints it
        rows = [r for r in rows if counts_yv(r, measure.upper()) is not None]
        yv = [counts_yv(r, measure.upper()) for r in rows]
    else:
        yv = [_yv(r, ratio) for r in rows]
    if any(x is None for x in yv) or len(rows) < 2:
        return {}
    y, v = [a for a, _ in yv], [b for _, b in yv]
    if any(b <= 0 for b in v):
        return {}
    k = len(y)
    w = [1 / b for b in v]
    fe = sum(a * b for a, b in zip(w, y)) / sum(w)
    q = sum(a * (b - fe) ** 2 for a, b in zip(w, y))
    c = sum(w) - sum(a * a for a in w) / sum(w)
    tau = {"FE": 0.0, "DL": max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0, "REML": _reml_tau2(y, v)}
    try:
        tau["PM"] = float(_paule_mandel_tau2(y, v))
    except Exception:  # noqa: BLE001 - PM not computable: not reconstructed by PM
        pass
    out = {}
    for m in methods:
        base, hk = m.replace("+HK", ""), m.endswith("+HK")
        if base in ("MH-FE", "MH-RE"):
            mh = _mh(rows, measure.upper()) if ratio and measure.upper() in ("RR", "OR") else None
            if mh is None:
                continue
            if base == "MH-FE":
                est, var = mh
                out[m] = (g(est), g(est - z * math.sqrt(var)), g(est + z * math.sqrt(var)))
                continue
            # RevMan random effects for M-H data: DerSimonian-Laird with Q taken about the M-H estimate
            qmh = sum(a * (b - mh[0]) ** 2 for a, b in zip(w, y))
            t2 = max(0.0, (qmh - (k - 1)) / c) if c > 0 else 0.0
        elif base in tau:
            t2 = tau[base]
        else:
            continue
        ww = [1 / (b + t2) for b in v]
        mu = sum(a * b for a, b in zip(ww, y)) / sum(ww)
        if hk:
            se = math.sqrt(sum(a * (b - mu) ** 2 for a, b in zip(ww, y)) / (k - 1) / sum(ww))
            crit = stats.t.ppf(0.975, k - 1)
        else:
            se, crit = math.sqrt(1 / sum(ww)), z
        out[m] = (g(mu), g(mu - crit * se), g(mu + crit * se))
    return out


def row_problems(r, ratio, measure=None):
    """A proposed row must be internally consistent. With printed counts (RR/OR): the effect and CI recomputed from the
    counts must round to the printed ones (a lower limit printed 0.00 is checked this way too). Otherwise (gate G3 of
    k_gap_forest_plot): lower <= point <= upper, and the point is the CI's midpoint (log scale for a ratio) within the
    printed rounding of all three."""
    m = (measure or "").upper()
    if ratio and m in ("RR", "OR") and has_counts([r]):
        yv = counts_yv(r, m)
        if yv is None:
            return [] if str(r.get("effect") or "").strip().lower() in ("", "not estimable", "none") else ["ROW_NOT_ESTIMABLE_BUT_PRINTED"]
        y, v = yv
        z = 1.959963984540054
        calc = (math.exp(y), math.exp(y - z * math.sqrt(v)), math.exp(y + z * math.sqrt(v)))
        bad = [k for k, x in zip(("effect", "lower", "upper"), calc)
               if _num(r.get(k)) is None or not fp._close(x, r[k], 1e-4)]
        return [f"ROW_COUNTS_DO_NOT_GIVE_PRINTED_{'_'.join(k.upper() for k in bad)}"] if bad else []
    e, lo, hi = _num(r["effect"]), _num(r["lower"]), _num(r["upper"])
    if None in (e, lo, hi) or (ratio and min(e, lo, hi) <= 0):
        return ["ROW_NOT_NUMERIC"]
    p = []
    if not (lo <= e <= hi):
        p.append("ROW_ORDER")
    if ratio:
        mid = math.exp((math.log(lo) + math.log(hi)) / 2)
        tol = fp._half_unit(r["effect"]) + e * 0.5 * (fp._half_unit(r["lower"]) / lo + fp._half_unit(r["upper"]) / hi) + 0.005
    else:
        mid = (lo + hi) / 2
        tol = fp._half_unit(r["effect"]) + 0.5 * (fp._half_unit(r["lower"]) + fp._half_unit(r["upper"])) + 1e-9
    if abs(mid - e) > tol:
        p.append("ROW_CI_ASYMMETRIC")
    return p


def accept(proposed, pooled, model, measure, held=None):
    """The deterministic acceptance check over AGREED rows: every row consistent, the stated model reconstructable,
    and the stated model reproducing the printed pooled estimate AND CI within rounding. Any failure refuses the
    WHOLE figure. Returns {state, problems, recomputed, methods_reproducing, pooled_anchor}."""
    ratio = fp.is_ratio(measure)
    probs = []
    for r in proposed:
        for x in row_problems(r, ratio, measure):
            probs.append(f"{x}:{r['label']}")
    if not pooled:
        probs.append("NO_AGREED_POOLED_ROW")
    if model["state"] != "STATED":
        probs.append(f"STATED_MODEL_{model['state']}")
    anchor = fp.pooled_in_text(pooled, held) if pooled and held else None
    rec, matched = {}, []
    if pooled and model["state"] == "STATED" and len(proposed) >= 2:
        rec = reconstruct(proposed, ratio, measure, model["methods"])
        extra = fp._half_unit(pooled["effect"])
        for name, (m, lo, hi) in rec.items():
            if fp._close(m, pooled["effect"], extra) and fp._close(lo, pooled["lower"], extra) and \
                    fp._close(hi, pooled["upper"], extra):
                matched.append(name)
        if not rec:
            probs.append("STATED_MODEL_NOT_COMPUTABLE_FROM_ROWS")
        elif not matched:
            probs.append("RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL")
    elif len(proposed) < 2:
        probs.append("FEWER_THAN_2_AGREED_ROWS")
    return {"state": "ACCEPTED" if not probs else "REFUSED", "problems": probs,
            "recomputed": {k: [round(x, 4) for x in v] for k, v in rec.items()}, "methods_reproducing": matched,
            "pooled_anchor": ("PRINTED_IN_META_TEXT: " + anchor) if anchor else "PRINTED_IN_FIGURE_ONLY"}


def measure_code(m):
    m = (m or "").upper()
    return "HR" if "HAZARD" in m or m == "HR" else "RR" if ("RISK R" in m or "RELATIVE RISK" in m or m == "RR") else \
        "OR" if ("ODDS" in m or m == "OR") else "MD" if ("MEAN" in m or m in ("MD", "WMD")) else m.strip()


def judge(item, reading_a, reading_b, rid_a, rid_b, held, mtext=None):
    """Two parsed readings -> the figure's verdict, the proposed/refused rows, and (if ACCEPTED) the secondary rows."""
    proposed, refused, pooled, probs = agree(reading_a, reading_b)
    agreed_not_trials = []
    if any(p.startswith("ROWS_ARE_NOT_STUDIES") for p in probs):
        # rows both readers agree on but which are NOT trials (outcomes / subgroups) are never per-trial proposals
        agreed_not_trials, proposed = proposed, []
    measure = measure_code(reading_a.get("measure"))
    model = stated_model(mtext if mtext is not None else held, reading_a.get("model_printed") if reading_a.get("model_printed") ==
                         reading_b.get("model_printed") else None)
    # the reconstruction runs on the AGREED rows even when other rows disagree: the record shows what they alone give
    acc = accept(proposed, pooled, model, measure, held) if pooled else \
        {"state": "REFUSED", "problems": [], "recomputed": {}, "methods_reproducing": [], "pooled_anchor": None}
    problems = probs + acc["problems"]
    state = "ACCEPTED" if not problems else "REFUSED"
    fig = item["figure"]
    rows = []
    if state == "ACCEPTED":
        for r in proposed:
            rows.append({"meta_pmid": item["pmid"], "meta_doi": "", "source_digest": item["image_sha256"],
                         "location": {"kind": "figure", "id": fig["fig_id"], "panel": fig.get("panel"), "row_label": r["label"]},
                         "provenance": f"MODEL_PROPOSAL_DUAL:{rid_a}+{rid_b}", "trial_label": r["label"],
                         "measure": measure, "outcome_definition": (fig.get("panel_title") or fig["caption"])[:300],
                         "effect": r["effect"], "lower": r["lower"], "upper": r["upper"],
                         **{k: r[k] for k in ("events_t", "n_t", "events_c", "n_c")}})
    return {"state": state, "problems": problems, "measure": measure, "stated_model": model,
            "proposed_rows": proposed, "refused_rows": refused, "pooled_agreed": pooled,
            "agreed_rows_not_trials": agreed_not_trials,
            "acceptance": acc, "secondary_rows": rows,
            "anti_circularity": f"comparator-side rows of meta {item['pmid']}: never pool inputs; never count toward "
                                f"agreement with meta {item['pmid']} (secondary_meta.g1_countable)"}


# ------------------------------------------------------------------ driver

def comparator_of(slug):
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    m = re.search(r"PMID (\d+)", c.get("citation", ""))
    return m.group(1) if m else str(c.get("id"))


def items(slugs, run):
    out, skipped = [], {}
    for slug in slugs:
        try:
            pmid = comparator_of(slug)
        except Exception as exc:  # noqa: BLE001
            skipped[slug] = f"NO_COMPARATOR:{type(exc).__name__}"
            continue
        if run and not jats_path(pmid):
            from kgap import k_gap
            k_gap.fetch_comparator_jats(pmid, FETCH_DATE)
        fig, why = figure_for(slug, pmid)
        if not fig:
            skipped[slug] = {"pmid": pmid, "why": why}
            continue
        pmcid = pmcid_of(pmid)
        if not pmcid:
            skipped[slug] = {"pmid": pmid, "why": "NO_PMCID", "figure": fig["fig_id"]}
            continue
        ip, meta = acquire_image(pmid, pmcid, fig["href"]) if run else cached_image(pmid, fig["href"])
        if not ip:
            skipped[slug] = {"pmid": pmid, "why": (meta or {}).get("why", "IMAGE_NOT_HELD"), "figure": fig["fig_id"]}
            continue
        with open(ip, "rb") as fh:
            b = fh.read()
        fig = dict(fig, image_name=os.path.basename(ip))
        out.append({"slug": slug, "pmid": pmid, "pmcid": pmcid, "figure": fig, "image_path": ip,
                    "image_ref": os.path.relpath(ip, ROOT).replace(os.sep, "/"),
                    "image_sha256": hashlib.sha256(b).hexdigest(), "image_url": (meta or {}).get("url"),
                    "image_via": (meta or {}).get("via") or "PMC OA bucket (pmc-oa-opendata)"})
    return out, skipped


def _key(it, reader):
    return f"{it['slug']}::{it['pmid']}::{it['figure']['fig_id']}::{reader}"


def replay_reading(run_r):
    rec = ms.load_record(os.path.join(REC_DIR, run_r["record_id"] + ".json"))
    raw = ms.replay(rec)
    return raw, parse_reading(raw)


def evaluate(its, runs):
    res = {}
    for it in its:
        ra, rb = runs.get(_key(it, "codex")), runs.get(_key(it, "agy"))
        base = {"pmid": it["pmid"], "figure": {k: it["figure"].get(k) for k in ("fig_id", "caption", "panel", "selected_by")},
                "image": {"ref": it["image_ref"], "sha256": it["image_sha256"], "url": it["image_url"], "via": it["image_via"]}}
        ok = [r for r in (ra, rb) if r and r["state"] == "RAN_OK" and r["image_sha256"] == it["image_sha256"]]
        if len(ok) < 2:
            res[it["slug"]] = dict(base, state="NO_TWO_RECORDED_READINGS",
                                   readings={"codex": ra and {k: ra.get(k) for k in ("record_id", "state", "error")},
                                             "agy": rb and {k: rb.get(k) for k in ("record_id", "state", "error")}})
            continue
        (_, (da, wa)), (_, (db, wb)) = replay_reading(ra), replay_reading(rb)
        if da is None or db is None:
            res[it["slug"]] = dict(base, state="REFUSED", problems=[f"READING_UNPARSEABLE:codex={wa},agy={wb}"],
                                   readings={"codex": ra["record_id"], "agy": rb["record_id"]})
            continue
        v = judge(it, da, db, ra["record_id"], rb["record_id"], held_text(it["pmid"]), model_text(it["pmid"]))
        res[it["slug"]] = dict(base, readings={"codex": {"record_id": ra["record_id"], "model": ra.get("model"),
                                                         "rows": len(da["rows"]), "row_kind": da["row_kind"],
                                                         "pooled": da["pooled"], "measure": da["measure"]},
                                               "agy": {"record_id": rb["record_id"], "model": rb.get("model"),
                                                       "rows": len(db["rows"]), "row_kind": db["row_kind"],
                                                       "pooled": db["pooled"], "measure": db["measure"]}}, **v)
    return res


def accepted_rows(slug):
    """The ACCEPTED secondary rows for a topic's comparator (replay output, no model): for secondary_meta_build."""
    if not os.path.exists(OUT):
        return []
    r = (_j(OUT).get("results") or {}).get(slug) or {}
    return list(r.get("secondary_rows") or []) if r.get("state") == "ACCEPTED" else []


def main(argv):
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")]
    runs = _j(RUNS) if os.path.exists(RUNS) else {}
    its, skipped = items(slugs, run)
    if "--verify-replay" in argv:
        probs = []
        for k, r in sorted(runs.items()):
            if r["state"] != "RAN_OK":
                continue
            rec = ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))
            if hashlib.sha256(ms.replay(rec)).hexdigest() != rec["response"]["sha256"]:
                probs.append(f"{k}: replay bytes differ")
        a, b = evaluate(its, runs), evaluate(its, runs)
        if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
            probs.append("two offline evaluations differ")
        print("REPLAY_OK" if not probs else "REPLAY_PROBLEMS", json.dumps(probs, indent=1))
        return 0 if not probs else 1
    if run:
        todo = [(it, rd) for it in its for rd in ("codex", "agy")
                if not (runs.get(_key(it, rd)) or {}).get("state") == "RAN_OK"
                or runs[_key(it, rd)]["image_sha256"] != it["image_sha256"]
                or runs[_key(it, rd)]["prompt_sha256"] != hashlib.sha256(prompt_bytes(it["figure"], rd)).hexdigest()]
        print(f"figures {len(its)}, calls to run {len(todo)}, skipped {len(skipped)}", flush=True)
        with cf.ThreadPoolExecutor(max_workers=3) as cx, cf.ThreadPoolExecutor(max_workers=3) as ag:
            futs = {(cx if rd == "codex" else ag).submit(run_reader, it, rd): (it, rd) for it, rd in todo}
            for f in cf.as_completed(futs):
                it, rd = futs[f]
                r = f.result()
                runs[_key(it, rd)] = r
                _save(RUNS, runs)
                print(_key(it, rd), r["state"], r["record_id"], r.get("error") or "", flush=True)
    res = evaluate(its, runs)
    prev = _j(OUT) if os.path.exists(OUT) else {}
    results = dict(prev.get("results") or {}, **res)
    skipped_all = dict(prev.get("skipped") or {}, **skipped)
    for s in res:
        skipped_all.pop(s, None)
    for s in skipped:
        results.pop(s, None)
    from collections import Counter
    out = {"lane": LANE, "results": results, "skipped": skipped_all,
           "tally": dict(Counter(v["state"] for v in results.values())),
           "rows": {"proposed": sum(len(v.get("proposed_rows") or []) for v in results.values()),
                    "refused": sum(len(v.get("refused_rows") or []) for v in results.values()),
                    "accepted_as_secondary": sum(len(v.get("secondary_rows") or []) for v in results.values())}}
    _save(OUT, out)
    print(json.dumps({"tally": out["tally"], "rows": out["rows"], "skipped": skipped}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
