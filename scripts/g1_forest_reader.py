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
# bound HERE, with the repo root first on sys.path: scripts/kgap.py (a CLI) shadows the kgap PACKAGE whenever another
# importer has put scripts/ first, and a later lazy 'from kgap import k_gap' then fails (seen under pytest collection)
from kgap import k_gap  # noqa: E402
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
    # captions without the word 'forest' (the deterministic selector requires it, or a ratio phrase)
    "colchicine-secondary-cv-prevention": {"fig_id": "F3", "caption_has": "on the risks of (A) MACE", "panel": "A",
                                           "panel_title": "MACE"},
    "sglt2-primary-prevention-hf": {"fig_id": "f2", "caption_has": "Heart failure hospitalization in type 2 diabetes "
                                    "patients receiving SGLT2 inhibitors versus control"},
    # one figure, several outcomes stacked without panel letters: the readers are told which block
    "iv-iron-hfref-hosp": {
        "fig_id": "diseases-12-00339-f003",
        "caption_has": "forest plot comparing FCM versus placebo on HF and non-HF hospitalization rates",
        # the block's title as the figure prints it (the rows' outcome definition; not used in the prompt)
        "panel_title": "Forest plot for total heart failure hospitalizations",
        "instruction": "The figure stacks several outcomes. Transcribe ONLY the block for heart-failure (HF) "
                       "hospitalization: its study rows and its own pooled row. Ignore non-HF hospitalization, the "
                       "composite, all-cause mortality and any overall row."},
    "pcsk9-mace": {
        "fig_id": "F2", "caption_has": "Efficacy endpoints for PCSK9 inhibitors vs. control",
        "instruction": "Transcribe ONLY the major adverse cardiovascular events (MACE) part: its study rows and its own "
                       "pooled row. Report row_kind honestly: if the figure has one row per outcome rather than per "
                       "trial, say row_kind=\"outcome\"."},
    # refused BEFORE any model call, for a reason the comparator's own caption states (checked like any target)
    # free-to-read PMC articles (JATS-like file derived from the PMC article page): per-trial plots without 'forest'
    "corticosteroids-covid19-mortality": {
        "fig_id": "joi200104f2", "caption_has": "Association Between Corticosteroids and 28-Day All-Cause Mortality in "
                                                "Each Trial",
        "instruction": "Rows: every trial row, once each (the trials are grouped by corticosteroid drug; do not give "
                       "the drug subtotals as rows). Pooled: the OVERALL row for all trials."},
    "metformin-pcos-ovulation": {
        "fig_id": "CD013505-fig-0024", "caption_has": "Comparison 2 Metformin and clomiphene citrate versus clomiphene "
                                                      "citrate alone, Outcome 4 Ovulation rate",
        "instruction": "Rows: every study row (if the analysis is split into subgroups, every study row of every "
                       "subgroup, once each; never a subtotal). Pooled: the overall 'Total (95% CI)' row; if there is no "
                       "overall total, the pooled row printed last, and say so in notes."},
    "sglt2-ckd-progression": {"fig_id": "joi250094f1", "caption_has": "CKD Progression According to Baseline eGFR",
                              "refuse": "NO_PER_TRIAL_TOPIC_FIGURE: the comparator's figures are CKD-progression / eGFR "
                                        "outcomes by baseline eGFR or UACR SUBGROUP, not per-trial rows of the "
                                        "trial-defined cardiorenal composite"},
    "dapagliflozin-hfpef-hosp": {"fig_id": "fig1", "caption_has": "Risk of composite cardiovascular outcomes of "
                                                                  "CVD/HHF in patients with HFpEF"},
    "empagliflozin-hfpef-hosp": {"fig_id": "F2", "caption_has": "Primary composite outcome (composite of first HFH or "
                                                                "cardiovascular death)"},
    "esketamine-trd-madrs": {"fig_id": "f4", "caption_has": "Acute induction: MADRS change from baseline to day 28"},
    "statins-primary-prevention-elderly": {
        "fig_id": "S3.F2", "caption_has": "Forrest plots for the primary outcomes",
        "instruction": "The figure has several primary outcomes. Transcribe ONLY the block for the composite of major "
                       "cardiovascular / vascular events (MACE / major vascular events): its study rows and its own "
                       "pooled row. If there is no such composite block, set legible=false and say so in notes."},
    # the topic population is LVEF <= 40%: the comparator prints that pool ONLY as panel (A)'s subgroup (its own text:
    # 'LVEF <=40% (n = 9199, HR: 0.74, 95% CI: 0.68, 0.81)'); figure 1 is all patients, mixed LVEF
    "sglt2-hfref-hosp-cvdeath": {
        "fig_id": "ehf213805-fig-0002", "caption_has": "stratified by (A) LVEF at baseline", "panel": "A",
        "panel_title": "LVEF <= 40% subgroup of panel (A)",
        "instruction": "Transcribe ONLY panel (A) (stratified by LVEF at baseline), and within it ONLY the subgroup of "
                       "patients with LVEF <= 40% (reduced ejection fraction): its study rows, and its SUBTOTAL row as the "
                       "pooled row. effect/lower/upper come only from the 'Hazard Ratio ... 95% CI' column, never from "
                       "log[Hazard Ratio] or SE. Ignore the LVEF > 40% subgroup, any overall row, and panel (B)."},
    "denosumab-vertebral-fracture": {"fig_id": "fig4", "caption_has": "direct and indirect results of vertebral fractures",
                                     "refuse": "NETWORK_META_ANALYSIS_FIGURE: direct and indirect head-to-head estimates "
                                               "(treatments), not trial rows"},
    # OTHER metas from the two-source sweep (keyed '<slug>::<pmid>'): their captions name the outcome in their own words
    "colchicine-secondary-cv-prevention::40314333": {
        "fig_id": "ehaf174-F1", "caption_has": "Forest plot of clinical efficacy endpoints (hazard ratios)",
        "instruction": "The figure has several efficacy endpoints. Transcribe ONLY the block for the PRIMARY composite "
                       "(major adverse cardiovascular events): its study rows and its own pooled row."},
    "melatonin-primary-insomnia-sol::32580450": {"fig_id": "jcm-09-01949-f008",
                                                 "caption_has": "Sleep onset latency measured through physiological"},
    "ticagrelor-vs-clopidogrel-acs::35155618": {"fig_id": "F2", "caption_has": "Comparison of the primary efficacy "
                                                "outcomes (MACE) between ticagrelor and clopidogrel treatment in clinical"},
    "dpp4-mace-t2d": {"fig_id": "F1", "caption_has": "A: Fatal and non-fatal myocardial infarction",
                      "refuse": "NO_TOPIC_OUTCOME_PANEL: the comparator's only forest figure (panels A-F: MI, stroke, "
                                "HHF, unstable angina, revascularisation, CV mortality) has no 3-point MACE panel"},
    "sacubitril-valsartan-hfref": {"fig_id": "ehf214298-fig-0003",
                                   "caption_has": "available interventions for the composite outcome",
                                   "refuse": "NETWORK_META_ANALYSIS_FIGURE: rows are treatments (network estimates), "
                                             "not trials"},
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
    """The comparator's JATS as k_gap fetched it; else the JATS-like file derived from its PMC article page."""
    d = os.path.join(COMP, pmid)
    if not os.path.isdir(d):
        return None
    fs = sorted(os.listdir(d), reverse=True)
    return next((os.path.join(d, f) for f in fs if f.endswith("_kgap_jats.xml")), None) or \
        next((os.path.join(d, f) for f in fs if f.endswith("_forest_pmcpage_jats.xml")), None)


def _strip(h):
    import html as _html
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def pmc_page_jats(pmid, pmcid):
    """A free-to-read PMC article outside the OA subset has no JATS from Europe PMC (empty body) and no images in the
    OA bucket, but its PMC article page is public. The page bytes are stored with URL + sha256; a JATS-LIKE file is
    DERIVED from them (abstract, body text before the references, and every <figure>: id, caption text, image file
    name) so the same caption-based selector and model-text typing run on it. Returns the derived path or None."""
    from harness import http
    from xml.sax.saxutils import escape, quoteattr
    d = os.path.join(COMP, pmid)
    page = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    hp = os.path.join(d, f"{FETCH_DATE}_forest_pmcpage.html")
    if not os.path.exists(hp):
        try:
            st, b = http.get_raw(page, tries=2, timeout=60)
        except Exception:  # noqa: BLE001 - recorded as NO_JATS by the caller
            return None
        if b"POW_CHALLENGE" in b or b"<figure" not in b:
            return None                         # a bot gate or a page without figures: not solved, not used
        os.makedirs(d, exist_ok=True)
        with open(hp, "wb") as fh:
            fh.write(b)
        _save(hp + ".meta.json", {"url": page, "http_status": st, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                                  "fetched": FETCH_DATE, "why": "free-to-read PMC article outside the OA subset"})
    with open(hp, "rb") as fh:
        b = fh.read()
    h = b.decode("utf-8", "replace")
    art = h[h.find("<article"):] if "<article" in h else h
    cut = min([i for i in (art.find('id="ref-list'), art.find('class="ref-list')) if i > 0] or [len(art)])
    figs, body_h = [], art[:cut]
    for m in re.finditer(r'<figure[^>]*\bid="([^"]+)"[^>]*>(.*?)</figure>', body_h, re.S):
        img = re.search(r'src="https://cdn\.ncbi\.nlm\.nih\.gov/pmc/blobs/[^"]+/([^"/]+\.(?:jpe?g|png|gif))"', m.group(2))
        if img:
            cap = _strip(re.sub(r"<img[^>]*>|<a[^>]*>\s*Open in a new tab\s*</a>", " ", m.group(2)))
            figs.append((m.group(1), img.group(1), cap))
    abstract = _strip(next(iter(re.findall(r'<section[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</section>', body_h, re.S)), ""))
    text = _strip(re.sub(r"<figure.*?</figure>", " ", body_h, flags=re.S))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<article xmlns:xlink="http://www.w3.org/1999/xlink" derived-from={quoteattr(page)} '
           f'derived-from-sha256="{hashlib.sha256(b).hexdigest()}">',
           f"<front><article-meta><abstract><p>{escape(abstract)}</p></abstract></article-meta></front>",
           f"<body><p>{escape(text)}</p>"]
    for fid, name, cap in figs:
        xml.append(f'<fig id={quoteattr(fid)}><caption><p>{escape(cap)}</p></caption>'
                   f'<graphic xlink:href={quoteattr(name)}/></fig>')
    xml.append("</body></article>")
    out = os.path.join(d, f"{FETCH_DATE}_forest_pmcpage_jats.xml")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(xml) + "\n")
    return out


def held_text(pmid):
    jp = jats_path(pmid)
    if not jp:
        return ""
    with open(jp, "rb") as fh:
        return k_gap.jats_body_text(fh.read())


def figure_for(slug, pmid):
    """(figure dict, why). A TARGETS entry is honoured only if its figure exists and its caption contains the words."""
    jp = jats_path(pmid)
    if not jp:
        return None, "NO_JATS"
    # a TARGETS entry keyed by the slug names the COMPARATOR's figure; another meta's is keyed '<slug>::<pmid>'
    t = TARGETS.get(f"{slug}::{pmid}") or (TARGETS.get(slug) if pmid == comparator_of(slug) else None)
    if t:
        for f in ET.parse(jp).getroot().iter("fig"):
            if f.get("id") != t["fig_id"]:
                continue
            cap = " ".join("".join(x.itertext()) for x in f.iter("caption"))
            g = f.find(".//graphic")
            if g is None or t["caption_has"].lower() not in re.sub(r"\s+", " ", cap).lower():
                return None, "TARGET_CAPTION_MISMATCH"
            if t.get("refuse"):
                return None, "REFUSED_BEFORE_READING:" + t["refuse"]
            return {"fig_id": t["fig_id"], "href": g.get(fp.XL), "caption": cap.strip()[:300], "panel": t.get("panel"),
                    "panel_title": t.get("panel_title"), "instruction": t.get("instruction"),
                    "selected_by": f"TARGETS (caption contains {t['caption_has']!r})"}, "SELECTED"
        return None, "TARGET_FIGURE_ABSENT"
    # a caption that says "forest" first; the broader pooled/ratio captions only when no forest caption qualifies (a
    # broad match alone picked COMBINE AF's HR-by-age curve)
    fig, why = fp.select_figure(slug, pmid, jats_file=jp)
    if not fig:
        fig, why2 = fp.select_figure(slug, pmid, jats_file=jp, caption_re=CAPTION)
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
    held = os.path.join(COMP, pmid, f"{FETCH_DATE}_forest_pmcpage.html")
    if os.path.exists(held):                    # the page already stored (with its sha256) by pmc_page_jats
        with open(held, "rb") as fh:
            html = fh.read()
    else:
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

def _nfkc(s):
    """Compatibility-folded text: a footnote superscript 'COV-AIDᵃ' reads as 'COV-AIDa' (REACT, PMID 34228774)."""
    import unicodedata
    return unicodedata.normalize("NFKC", str(s or ""))


def _norm_label(s):
    return re.sub(r"[^a-z0-9]", "", _nfkc(s).lower())


def _num(s):
    """A printed number; a leading '+' ('+0.50', esketamine MD rows) is a sign, not text."""
    return fp._num(re.sub(r"^\s*\+", "", _nfkc(s))) if s is not None else None


_NOT_ESTIMABLE = re.compile(r"^(?:na[a-z]?|n/a|ne|not estimable|not estimated|not applicable|[-–—]+)$", re.I)


def _keyed(rows):
    """[(key, row)]: the normalised label, with its occurrence number when a meta prints one trial label twice (REACT
    lists REMAP-CAP once per drug): rows are matched by (label, k-th occurrence), in print order."""
    seen, out = {}, []
    for r in rows or []:
        lab = _norm_label(r.get("label"))
        seen[lab] = seen.get(lab, 0) + 1
        out.append((lab if seen[lab] == 1 else f"{lab}#{seen[lab]}", r))
    return out


def agree_value(a, b):
    """Two printed numbers agree within the figure's printed rounding: |a-b| <= half a unit of the finer printing.
    Returns the agreed printed string (the finer one) or None."""
    x, y = _num(a), _num(b)
    if x is None and y is None and a and b and \
            " ".join(_nfkc(a).lower().split()) == " ".join(_nfkc(b).lower().split()):
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
    ka, kb = _keyed(ra.get("rows")), _keyed(rb.get("rows"))
    la, lb = [k for k, _ in ka], [k for k, _ in kb]
    key_a = {id(r): k for k, r in ka}
    key_b = {id(r): k for k, r in kb}
    by_b = dict(kb)
    not_estimable = []
    for ka_, r in ka:
        s = by_b.pop(ka_, None)
        if s is None:
            refused.append({"label": r.get("label"), "why": "ONLY_IN_READING_A", "a": r, "b": None})
            continue
        vals, why = {}, []
        for k in ("effect", "lower", "upper"):
            if r.get(k) is None and s.get(k) is None:
                vals[k] = None              # both readers: nothing printed there (REACT's 'NA' rows print no CI)
                continue
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
        elif all(_num(vals[k]) is None and _NOT_ESTIMABLE.match(_nfkc(vals[k]).strip())
                 for k in ("effect", "lower", "upper")) and not has_counts([vals]):
            # both readers print the row as not estimable ('NA'): agreed, but it carries no number -- never pooled,
            # never a secondary row (with counts it stays a row: the counts decide estimability)
            not_estimable.append({"label": r.get("label"), **vals})
        else:
            proposed.append({"label": r.get("label"), **vals})
    for s in by_b.values():
        refused.append({"label": s.get("label"), "why": "ONLY_IN_READING_B", "a": None, "b": s})
    # a row the readers transcribe with the SAME numbers at the SAME position but a different label is one row whose
    # LABEL disagrees ('Newton N' / 'Mewton N'): still refused -- a label decides which trial a row is -- but typed so
    nums = ("effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")
    only_a = [x for x in refused if x["why"] == "ONLY_IN_READING_A"]
    only_b = [x for x in refused if x["why"] == "ONLY_IN_READING_B"]
    pos_a = {id(x): la.index(key_a[id(x["a"])]) for x in only_a}
    pos_b = {id(x): lb.index(key_b[id(x["b"])]) for x in only_b}
    for x in only_a:
        y = next((y for y in only_b if pos_b[id(y)] == pos_a[id(x)] and all(
            (agree_value(x["a"].get(k), y["b"].get(k)) is not None) if k in ("effect", "lower", "upper")
            else agree_count(x["a"].get(k), y["b"].get(k))[0] for k in nums)), None)
        if y is not None:
            refused.remove(x)
            refused.remove(y)
            only_b.remove(y)
            refused.append({"label": f"{x['a'].get('label')} / {y['b'].get('label')}", "why": "LABEL_DISAGREES",
                            "a": x["a"], "b": y["b"]})
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
    return proposed, refused, pooled, probs, not_estimable


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
    # the meta's OWN use ('We used individual patient data'); a background sentence about others' IPD work is not it
    # (esketamine PMID 42490943: 'Recent efforts have also leveraged individual participant data ...')
    data = next((s for s in sents if _IPD_SENT.search(s) and not _IPD_NEG.search(s)
                 and re.search(r"\b(?:we|our)\b", s, re.I)), None)
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
    # typographic hyphens folded first: Cochrane prints 'Mantel‐Haenszel' and 'fixed‐effect' (U+2010)
    t = re.sub(r"\s+", " ", re.sub(r"[\u2010-\u2015\u2212]", "-", text or ""))
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
    iv = re.search(r"inverse[- ]variance[- ]?weighted (?:fixed[- ]effects? )?meta-analys", t, re.I)
    if iv and "RE" not in quotes and not methods:
        # 'pooled using inverse variance-weighted meta-analysis' and no random effects named: fixed-effect IV
        quotes["FE"] = t[max(0, iv.start() - 80): iv.end() + 80]
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


def printed_matches(x, printed):
    """A computed value against what the figure prints: a number within its printed rounding, or a printed BOUND
    ('<0.01', '>100': REACT prints COVIDOSE2-SS-A's lower limit as '<0.01') that the value satisfies."""
    p = _nfkc(printed).strip() if printed is not None else ""
    m = re.fullmatch(r"([<>])\s*(\d+(?:\.\d+)?)", p)
    if m:
        lim = float(m.group(2))
        return x < lim + 1e-12 if m.group(1) == "<" else x > lim - 1e-12
    return _num(printed) is not None and fp._close(x, re.sub(r"^\s*\+", "", p), 1e-4)


def row_problems(r, ratio, measure=None):
    """A proposed row must be internally consistent. With printed counts (RR/OR): the effect and CI recomputed from the
    counts must round to the printed ones (a lower limit printed 0.00 is checked this way too). Otherwise (gate G3 of
    k_gap_forest_plot): lower <= point <= upper, and the point is the CI's midpoint (log scale for a ratio) within the
    printed rounding of all three."""
    m = (measure or "").upper()
    if ratio and m in ("RR", "OR") and has_counts([r]):
        yv = counts_yv(r, m)
        if yv is None:
            # no events in either arm: not estimable by the counts; the figure must say so ('Not estimable', 'NA'),
            # never print a number for it
            return [] if (_num(r.get("effect")) is None and
                          (not str(r.get("effect") or "").strip() or
                           _NOT_ESTIMABLE.match(_nfkc(r.get("effect")).strip()))) else ["ROW_NOT_ESTIMABLE_BUT_PRINTED"]
        y, v = yv
        z = 1.959963984540054
        calc = (math.exp(y), math.exp(y - z * math.sqrt(v)), math.exp(y + z * math.sqrt(v)))
        bad = [k for k, x in zip(("effect", "lower", "upper"), calc) if not printed_matches(x, r.get(k))]
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
    proposed, refused, pooled, probs, not_estimable = agree(reading_a, reading_b)
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
            "agreed_rows_not_trials": agreed_not_trials, "agreed_rows_not_estimable": not_estimable,
            "acceptance": acc, "secondary_rows": rows,
            "anti_circularity": f"rows of meta {item['pmid']}: never pool inputs; never count toward agreement with "
                                f"meta {item['pmid']} (secondary_meta.g1_countable)"}


# ------------------------------------------------------------------ driver

def comparator_of(slug):
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    m = re.search(r"PMID (\d+)", c.get("citation", ""))
    return m.group(1) if m else str(c.get("id"))


def key_of(slug, pmid):
    """Results key: the slug for the topic's COMPARATOR (unchanged interface, read by g1_tracker), '<slug>::<pmid>' for
    any other meta of the topic."""
    return slug if pmid == comparator_of(slug) else f"{slug}::{pmid}"


def items(slugs, run, pairs=None):
    """slugs -> each topic's comparator; pairs [(slug, pmid)] -> those metas (the two-source sweep's selection)."""
    out, skipped = [], {}
    todo = list(pairs or [])
    for slug in slugs:
        try:
            todo.append((slug, comparator_of(slug)))
        except Exception as exc:  # noqa: BLE001
            skipped[slug] = f"NO_COMPARATOR:{type(exc).__name__}"
    for slug, pmid in todo:
        key = key_of(slug, pmid)
        role = "comparator" if key == slug else "meta"
        if run and not jats_path(pmid):
            k_gap.fetch_comparator_jats(pmid, FETCH_DATE)
            if not jats_path(pmid) and pmcid_of(pmid):
                pmc_page_jats(pmid, pmcid_of(pmid))
        fig, why = figure_for(slug, pmid)
        if not fig:
            skipped[key] = {"pmid": pmid, "why": why, "role": role, "slug": slug}
            if why == "NO_JATS" and not pmcid_of(pmid) and role == "comparator":
                skipped[key]["open_access"] = oa_probe(slug, pmid, run)
            continue
        pmcid = pmcid_of(pmid)
        if not pmcid:
            skipped[key] = {"pmid": pmid, "why": "NO_PMCID", "figure": fig["fig_id"], "role": role, "slug": slug}
            continue
        ip, meta = acquire_image(pmid, pmcid, fig["href"]) if run else cached_image(pmid, fig["href"])
        if not ip:
            skipped[key] = {"pmid": pmid, "why": (meta or {}).get("why", "IMAGE_NOT_HELD"), "figure": fig["fig_id"],
                            "role": role, "slug": slug}
            continue
        with open(ip, "rb") as fh:
            b = fh.read()
        fig = dict(fig, image_name=os.path.basename(ip))
        out.append({"slug": slug, "pmid": pmid, "pmcid": pmcid, "key": key, "role": role, "figure": fig,
                    "image_path": ip, "image_ref": os.path.relpath(ip, ROOT).replace(os.sep, "/"),
                    "image_sha256": hashlib.sha256(b).hexdigest(), "image_url": (meta or {}).get("url"),
                    "image_via": (meta or {}).get("via") or "PMC OA bucket (pmc-oa-opendata)"})
    return out, skipped


SWEEP = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_reader_sweep.json")


def unmatched_trial_ids(slug):
    """The comparator trials of a topic that are NOT matched (route neither PRIMARY nor TWO_SOURCE in the tracker), as
    the PMIDs/NCTs the k-gap table holds for them -- the trials a second meta could supply a two-source row for."""
    tp = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json")
    if not os.path.exists(tp):
        return {}
    tr = _j(tp)
    open_labels = {x["label"][:60] for x in tr.get("trials") or [] if x.get("route") not in ("PRIMARY", "TWO_SOURCE")}
    T = _j(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"))
    return {t["label"][:60]: {str(p) for p in (t.get("pmids") or [])} | {str(n).lower() for n in (t.get("ncts") or [])}
            for t in T["trials"] if t["slug"] == slug and t["label"][:60] in open_labels}


def sweep(slugs, run, wide=False):
    """The k-gap lane's two-source sweep (secondary_meta_build.metas_for: the topic's recorded Europe PMC search of
    open-access full-text metas), restricted DETERMINISTICALLY to the metas worth a dual read: not the comparator (read
    separately), not already usable by another route (typed table / single read that passed), and CITING -- in its own
    JATS reference list -- at least one comparator trial we have not matched. Returns [(slug, pmid)] and records why
    every candidate was or was not selected (registry/model_proposals/g1_forest_reader_sweep.json)."""
    import secondary_meta_build as smb
    table = _j(SWEEP) if os.path.exists(SWEEP) else {}
    pairs = []
    for slug in slugs:
        try:
            metas, comp = smb.metas_for(slug, offline=not run)
            if wide:
                # every hit of the topic's RECORDED search (up to 25), not only the k-gap list's top N
                metas = list(dict.fromkeys(metas + [h["pmid"] for h in smb.candidates(slug, not run)["hits"]
                                                    if h.get("pmid")]))
        except Exception as exc:  # noqa: BLE001 - recorded, never fatal
            table[slug] = {"error": f"{type(exc).__name__}:{str(exc)[:120]}"}
            continue
        sp = os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json")
        usable = {m for m, v in ((_j(sp).get("metas") or {}) if os.path.exists(sp) else {}).items()
                  if v.get("usable") and v.get("provenance") != "MODEL_PROPOSAL_DUAL"}
        want = unmatched_trial_ids(slug)
        rows = {}
        for pm in metas:
            if pm == comp:
                continue
            if pm in usable:
                rows[pm] = {"selected": False, "why": "ALREADY_USABLE_BY_ANOTHER_ROUTE"}
                continue
            if run and not jats_path(pm):
                k_gap.fetch_comparator_jats(pm, FETCH_DATE)
            refs = smb.refs_of(pm)
            if refs is None:
                rows[pm] = {"selected": False, "why": "NO_OPEN_JATS_REFERENCE_LIST"}
                continue
            refs = {str(r).lower() for r in refs}
            cites = sorted(lab for lab, ids in want.items() if ids & refs)
            rows[pm] = {"selected": bool(cites), "cites_unmatched": cites,
                        "why": "CITES_UNMATCHED_COMPARATOR_TRIALS" if cites else "CITES_NO_UNMATCHED_TRIAL"}
            if cites:
                pairs.append((slug, pm))
        table[slug] = {"comparator": comp, "n_unmatched": len(want), "candidates": rows}
    _save(SWEEP, table)
    return pairs


def oa_probe(slug, pmid, run):
    """A comparator with no PMC full text: is it open anywhere? Unpaywall's best OA location, and ONE plain request for
    its PDF. A bot challenge (403 HTML) is recorded as such and never worked around. Cached; offline reads the cache."""
    p = os.path.join(COMP, pmid, f"{FETCH_DATE}_forest_oa_probe.json")
    if os.path.exists(p):
        return _j(p)
    if not run:
        return None
    from harness import http
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    m = re.search(r"DOI (\S+?);", (c.get("citation") or "") + ";")
    if not m:
        return None
    try:
        st, b = http.get_raw(f"https://api.unpaywall.org/v2/{m.group(1)}", {"email": "meta-harness@example.org"}, tries=2)
        d = json.loads(b.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"doi": m.group(1), "state": f"UNPAYWALL_FAILED:{type(exc).__name__}"}
    best = d.get("best_oa_location") or {}
    out = {"doi": m.group(1), "is_oa": d.get("is_oa"), "oa_status": d.get("oa_status"), "license": best.get("license"),
           "host_type": best.get("host_type"), "url": best.get("url_for_pdf") or best.get("url_for_landing_page")}
    if out["url"]:
        try:
            st2, b2 = http.get_raw(out["url"], tries=1, timeout=60)
            out["fetch"] = "PDF" if b2[:4] == b"%PDF" else f"NOT_A_PDF (HTTP {st2})"
        except Exception as exc:  # noqa: BLE001 - a 403 bot challenge lands here
            out["fetch"] = f"REFUSED_BY_HOST ({str(exc)[:60]}): a bot challenge is not solved"
    out["state"] = ("OPEN_BUT_NOT_SCRIPT_READABLE" if out.get("is_oa") and out.get("fetch") != "PDF" else
                    "OPEN_PDF" if out.get("fetch") == "PDF" else "NOT_OPEN")
    _save(p, out)
    return out


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
        base = {"pmid": it["pmid"], "slug": it["slug"], "role": it.get("role", "comparator"), "figure": {k: it["figure"].get(k) for k in ("fig_id", "caption", "panel", "selected_by")},
                "image": {"ref": it["image_ref"], "sha256": it["image_sha256"], "url": it["image_url"], "via": it["image_via"]}}
        ok = [r for r in (ra, rb) if r and r["state"] == "RAN_OK" and r["image_sha256"] == it["image_sha256"]]
        if len(ok) < 2:
            res[it.get("key", it["slug"])] = dict(base, state="NO_TWO_RECORDED_READINGS",
                                   readings={"codex": ra and {k: ra.get(k) for k in ("record_id", "state", "error")},
                                             "agy": rb and {k: rb.get(k) for k in ("record_id", "state", "error")}})
            continue
        (_, (da, wa)), (_, (db, wb)) = replay_reading(ra), replay_reading(rb)
        if da is None or db is None:
            res[it.get("key", it["slug"])] = dict(base, state="REFUSED", problems=[f"READING_UNPARSEABLE:codex={wa},agy={wb}"],
                                   readings={"codex": ra["record_id"], "agy": rb["record_id"]})
            continue
        v = judge(it, da, db, ra["record_id"], rb["record_id"], held_text(it["pmid"]), model_text(it["pmid"]))
        res[it.get("key", it["slug"])] = dict(base, readings={"codex": {"record_id": ra["record_id"], "model": ra.get("model"),
                                                         "rows": len(da["rows"]), "row_kind": da["row_kind"],
                                                         "pooled": da["pooled"], "measure": da["measure"]},
                                               "agy": {"record_id": rb["record_id"], "model": rb.get("model"),
                                                       "rows": len(db["rows"]), "row_kind": db["row_kind"],
                                                       "pooled": db["pooled"], "measure": db["measure"]}}, **v)
    return res


def accepted_rows(slug):
    """The ACCEPTED secondary rows of a topic -- its comparator's and every other meta's (replay output, no model): for
    secondary_meta_build, where each meta's rows count toward the two-source rule but never against that meta."""
    if not os.path.exists(OUT):
        return []
    d = _j(OUT)
    rs = [(d.get("results") or {}).get(slug) or {}] + \
         [v for v in (d.get("meta_results") or {}).values() if v.get("slug") == slug]
    return [row for r in rs if r.get("state") == "ACCEPTED" for row in (r.get("secondary_rows") or [])]


REPORT = os.path.join(ROOT, "outputs", "k_gap", "G1_FOREST_READER.md")


def report(out):
    """outputs/k_gap/G1_FOREST_READER.md, derived from the proposals file only (nothing typed by hand)."""
    allres = {**out["results"], **(out.get("meta_results") or {})}
    sk = {**out["skipped"], **(out.get("meta_skipped") or {})}

    def summary(res, label):
        n_read = sum(1 for v in res.values() if v.get("readings"))
        acc = sum(1 for v in res.values() if v["state"] == "ACCEPTED")
        rows = {k: sum(len(v.get(f) or []) for v in res.values())
                for k, f in (("p", "proposed_rows"), ("r", "refused_rows"), ("a", "secondary_rows"))}
        return (f"- {label}: figures read by both models {n_read}; ACCEPTED {acc}, REFUSED "
                f"{sum(1 for v in res.values() if v['state'] == 'REFUSED')} (pooled-reconstruction pass rate {acc} of "
                f"{n_read}); rows proposed {rows['p']}, refused (readings disagree) {rows['r']}, accepted as secondary "
                f"{rows['a']}")

    def table_of(res, head):
        t = [f"| {head} | meta | figure | state | rows proposed / refused | stated model | printed pool | reconstructed | why |",
             "|---|---|---|---|---|---|---|---|---|"]
        for s in sorted(res):
            v = res[s]
            a = v.get("acceptance") or {}
            rec = "; ".join(f"{k} {x[0]:.4f} ({x[1]:.4f}-{x[2]:.4f})" for k, x in (a.get("recomputed") or {}).items())
            pp = v.get("pooled_agreed") or {}
            t.append(f"| {v.get('slug', s)} | PMID {v['pmid']} | {v['figure']['fig_id']} | **{v['state']}** | "
                     f"{len(v.get('proposed_rows') or [])} / {len(v.get('refused_rows') or [])} | "
                     f"{(v.get('stated_model') or {}).get('state', '')} {(v.get('stated_model') or {}).get('methods', '')} | "
                     f"{pp.get('effect', '')} ({pp.get('lower', '')}-{pp.get('upper', '')}) | {rec} | "
                     f"{', '.join(v.get('problems') or []) or '-'} |")
        return t
    md = ["# G1 dual-model forest-plot reader (derived: scripts/g1_forest_reader.py)", "",
          "Two model families read each forest figure (codex `gpt-6-astra`; agy `Gemini 3.1 Pro (High)`), every call "
          "recorded under evidence/model_calls/forest/ and replayed byte-identically. A row is PROPOSED only when both "
          "readings agree within the printed rounding; a figure is ACCEPTED only when the agreed rows, pooled by the "
          "meta's STATED model, reproduce its printed pool and CI. Accepted rows are SECONDARY rows: never pool inputs, "
          "never counted toward agreement with their own meta; another meta's rows feed the two-source rule.", "",
          f"- comparators of {len(out['results']) + len(out['skipped'])} tracker topics; other metas selected by the "
          f"two-source sweep: {len(out.get('meta_results') or {}) + len(out.get('meta_skipped') or {})}",
          summary(allres, "ALL"), summary(out["results"], "comparators"),
          summary(out.get("meta_results") or {}, "other metas (two-source sweep)"), "",
          "## Comparators", ""] + table_of(out["results"], "topic") + \
         ["", "## Other open-access metas citing unmatched comparator trials (two-source sweep)", ""] + \
         table_of(out.get("meta_results") or {}, "topic")
    res = allres
    md += ["", "## Not read (typed reason)", ""]
    for s in sorted(sk):
        x = sk[s]
        oa = (x.get("open_access") or {}) if isinstance(x, dict) else {}
        md.append(f"- {s}: " + (f"PMID {x.get('pmid')}: {x.get('why')}" if isinstance(x, dict) else str(x)) +
                  (f" -- no PMC full text; {oa.get('state')} ({oa.get('oa_status')}, {oa.get('url')}: {oa.get('fetch')})"
                   if oa else ""))
    md += ["", "## Disagreements (both readings shown)", ""]
    for s in sorted(res):
        for r in res[s].get("refused_rows") or []:
            md.append(f"- {s} / {r['label']}: {r['why']}; codex {json.dumps(r['a'], ensure_ascii=False)}; "
                      f"agy {json.dumps(r['b'], ensure_ascii=False)}")
    with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")


def main(argv):
    """SLUG ... reads each topic's comparator; --metas reads instead the OTHER metas the two-source sweep selects for
    those topics (--all: every topic in the tracker)."""
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        slugs = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1"))
                       if f.endswith(".json") and ".tmp" not in f)
    runs = _j(RUNS) if os.path.exists(RUNS) else {}
    if "--metas" in argv:
        its, skipped = items([], run, pairs=sweep(slugs, run, wide="--wide" in argv))
    else:
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
    # comparators under 'results'/'skipped' (keyed by slug: the interface g1_tracker reads); other metas under
    # 'meta_results'/'meta_skipped' (keyed '<slug>::<pmid>')
    sec = {"results": dict(prev.get("results") or {}), "skipped": dict(prev.get("skipped") or {}),
           "meta_results": dict(prev.get("meta_results") or {}), "meta_skipped": dict(prev.get("meta_skipped") or {})}
    for k, v in res.items():
        r, s = ("results", "skipped") if "::" not in k else ("meta_results", "meta_skipped")
        sec[r][k] = v
        sec[s].pop(k, None)
    for k, v in skipped.items():
        r, s = ("results", "skipped") if "::" not in k else ("meta_results", "meta_skipped")
        sec[s][k] = v
        sec[r].pop(k, None)
    results = sec["results"]
    from collections import Counter

    def rows_of(d):
        return {"proposed": sum(len(v.get("proposed_rows") or []) for v in d.values()),
                "refused": sum(len(v.get("refused_rows") or []) for v in d.values()),
                "accepted_as_secondary": sum(len(v.get("secondary_rows") or []) for v in d.values())}
    out = {"lane": LANE, **sec,
           "tally": dict(Counter(v["state"] for v in results.values())), "rows": rows_of(results),
           "meta_tally": dict(Counter(v["state"] for v in sec["meta_results"].values())),
           "meta_rows": rows_of(sec["meta_results"])}
    _save(OUT, out)
    report(out)
    print(json.dumps({"tally": out["tally"], "rows": out["rows"], "meta_tally": out["meta_tally"],
                      "meta_rows": out["meta_rows"], "skipped_this_run": skipped}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
