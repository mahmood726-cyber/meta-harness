"""Build SECONDARY-TIER rows (harness/secondary_meta.py) for a topic from previously published, open-access metas.

    python scripts/secondary_meta_build.py --run SLUG [SLUG ...]   (recorded model reads of forest figures)
    python scripts/secondary_meta_build.py SLUG [SLUG ...]         (replay: no network, no model)

Per topic:
  1. candidates  a RECORDED Europe PMC search (OA + full text, meta-analysis in the title, the topic's drug and outcome
                 words), ranked by citations; the topic's own comparator is added (it is a meta too; anti-circularity
                 keeps its rows out of G1 against itself) and any explicitly named meta (WHO REACT for tocilizumab)
  2. figure      the meta's forest figure for the topic outcome, chosen from ITS OWN JATS captions (scripts/
                 k_gap_forest_plot.select_figure: subgroup / secondary / ambiguous figures refused before any call)
  3. read        one recorded image call per figure -> rows as PRINTED strings (a proposal)
  4. control     the plot's pooled row must be printed verbatim in the meta's own text, and the rows must reproduce it
                 (secondary_meta.positive_control); a meta that fails contributes no row
  5. admit       secondary_meta.admit against the topic spec; family = OUR trial (label / acronym / author+year join)
  6. cross-check two metas on one trial must agree, else BLOCKED
  7. verify      against our own PRIMARY extraction of that trial (served row + its source span): match -> PRIMARY_VERIFIED,
                 mismatch -> typed finding; no primary value -> stays in the verification queue
Writes registry/secondary_meta/<slug>.json. Nothing is served; a served change is a derived notice for signature.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402
from kgap import k_gap  # noqa: E402
from kgap import aact_adapter  # noqa: E402
from kgap import runs_store  # noqa: E402
import k_gap_forest_plot as fp  # noqa: E402
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUTD = os.path.join(ROOT, "registry", "secondary_meta")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "secondary")   # the tier's recorded calls (named by Mahmood)
DATE = "2026-09-30"
N_CANDIDATES = 8
CAPTION = re.compile(r"forest|pooled|hazard ratio|risk ratio|odds ratio|relative risk|meta-analys[ie]s of", re.I)
NAMED = {"tocilizumab-covid19-mortality": ["34228774"]}      # WHO REACT (JAMA 2021), named by Mahmood
QUERY = {
    "glp1-ra-mace-t2d": '(TITLE:"GLP-1" OR TITLE:"glucagon-like peptide") AND (TITLE:"cardiovascular" OR TITLE:"MACE")',
    "semaglutide-obesity-weight": 'TITLE:"semaglutide" AND (TITLE:"weight" OR TITLE:"obesity")',
    "noac-vs-warfarin-af-stroke": '(TITLE:"non-vitamin K" OR TITLE:"direct oral anticoagulant" OR TITLE:"NOAC" OR '
                                  'TITLE:"DOAC") AND TITLE:"warfarin" AND TITLE:"atrial fibrillation"',
    "tocilizumab-covid19-mortality": '(TITLE:"interleukin-6" OR TITLE:"IL-6" OR TITLE:"tocilizumab") AND TITLE:"COVID" '
                                     'AND (TITLE:"mortality" OR TITLE:"randomized" OR TITLE:"randomised" OR TITLE:"trials")',
}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


def default_query(slug):
    """A topic without a hand-set query: its own registered intervention agents (config), in the title. Built from the
    config so it is reproducible; recorded with its response digest like every search."""
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    agents = [a for a in (cfg.get("intervention_agents") or cfg.get("intervention_terms") or []) if len(a) >= 4][:3]
    return " OR ".join(f'TITLE:"{a}"' for a in agents)


# topics with shared comparator trials, beyond the first four (Mahmood 2026-09-30: saturate the tier)
MORE = ["probiotics-aad-prevention", "omega3-cardiovascular-events", "colchicine-postop-af", "sglt2-hfref-hosp-cvdeath",
        "pcsk9-mace", "finerenone-ckd-t2d-renal", "ticagrelor-vs-clopidogrel-acs", "melatonin-primary-insomnia-sol",
        "semaglutide-obesity-mace", "colchicine-secondary-cv-prevention"]


def candidates(slug, offline):
    """The recorded search, cached as its raw response digest + the hit list (small)."""
    p = os.path.join(OUTD, f"search_{slug}.json")
    if os.path.exists(p):
        return _j(p)
    if offline:
        return {"hits": []}
    from harness import http
    q = f'(TITLE:"meta-analysis" OR TITLE:"meta analysis") AND ({QUERY.get(slug) or default_query(slug)}) AND OPEN_ACCESS:y AND HAS_FT:y'
    st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                         {"query": q, "format": "json", "pageSize": "25", "sort": "CITED desc", "resultType": "lite"})
    d = json.loads(b.decode("utf-8"))
    hits = [{"pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "cited": r.get("citedByCount"), "year": r.get("pubYear"),
             "title": r.get("title")} for r in d.get("resultList", {}).get("result", []) if r.get("pmid")]
    out = {"query": q, "http_status": st, "response_sha256": hashlib.sha256(b).hexdigest(), "hits": hits}
    _save(p, out)
    return out


def comparator_pmid(slug):
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    m = re.search(r"PMID (\d+)", c.get("citation", ""))
    return m.group(1) if m else str(c["id"])


def metas_for(slug, offline):
    comp = comparator_pmid(slug)
    hits = [h["pmid"] for h in candidates(slug, offline)["hits"] if h["pmid"] != comp][:N_CANDIDATES]
    return list(dict.fromkeys([comp] + NAMED.get(slug, []) + hits)), comp


def meta_item(slug, pmid, offline):
    """JATS -> figure -> image, for one meta. Returns (item or None, why)."""
    man = k_gap.fetch_comparator_jats(pmid, DATE) if not offline else {"state": "OFFLINE"}
    jp = next((os.path.join(k_gap.COMP_DIR, pmid, f) for f in sorted(os.listdir(os.path.join(k_gap.COMP_DIR, pmid)))
               if f.endswith("_kgap_jats.xml")), None) if os.path.isdir(os.path.join(k_gap.COMP_DIR, pmid)) else None
    if not jp:
        return None, "NO_OPEN_JATS:" + str(man.get("state"))
    jdate = os.path.basename(jp)[:10]
    # a secondary meta may caption its forest plot without the word "forest" ("Pooled hazard ratios for ...")
    fig, why = fp.select_figure(slug, pmid, jats_date=jdate, caption_re=CAPTION)
    if not fig:
        return None, why
    pmcid = fp.comparator(slug)[2] if pmid == comparator_pmid(slug) else None
    if not pmcid:
        idc = os.path.join(k_gap.COMP_DIR, pmid, f"{DATE}_kgap_idconv.json")
        for f in sorted(os.listdir(os.path.join(k_gap.COMP_DIR, pmid))):
            m = re.search(r'"pmcid"\s*:\s*"(PMC\d+)"', open(os.path.join(k_gap.COMP_DIR, pmid, f), encoding="utf-8",
                                                            errors="ignore").read()) if f.endswith("idconv.json") else None
            if m:
                pmcid = m.group(1)
    if not pmcid:
        return None, "NO_PMCID"
    ip, b = fp.fetch_image(pmid, pmcid, fig["href"]) if not offline else (None, None)
    if offline:
        name = fig["href"] if re.search(r"\.(jpe?g|png|gif)$", fig["href"], re.I) else fig["href"] + ".jpg"
        cands = [os.path.join(k_gap.COMP_DIR, pmid, f) for f in os.listdir(os.path.join(k_gap.COMP_DIR, pmid)) if f.endswith(name)]
        ip = cands[0] if cands else None
        b = open(ip, "rb").read() if ip else None
    if not ip:
        return None, "IMAGE_NOT_FETCHED"
    with open(jp, "rb") as fh:
        held = k_gap.jats_body_text(fh.read())
    return {"slug": slug, "pmid": pmid, "pmcid": pmcid, "figure": fig, "image_path": ip,
            "image_ref": os.path.relpath(ip, ROOT).replace(os.sep, "/"), "image_sha256": hashlib.sha256(b).hexdigest(),
            "held": held}, "SELECTED"


def typed_table(slug, pmid, spec, run):
    """The ONE JATS table of this meta that is usable by regex for the topic outcome, with its positive control."""
    d = os.path.join(k_gap.COMP_DIR, pmid)
    if run and not os.path.isdir(d):
        k_gap.fetch_comparator_jats(pmid, DATE)
    jp = next((os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith("_kgap_jats.xml")), None)         if os.path.isdir(d) else None
    if not jp:
        return None
    with open(jp, "rb") as fh:
        jb = fh.read()
    tables = sm.typed_rows_from_jats(jb, pmid)
    # the meta's own words (abstract + body, markup stripped) for identity by its pooled sentence
    text = re.sub(r"<[^>]+>", " ", jb.decode("utf-8", "replace"))
    terms = list(spec["keywords"]) + (comparator_terms(slug) if pmid == comparator_pmid(slug) else [])
    ok = []
    for t in tables:
        probe = sm.SecondaryRow(meta_pmid=pmid, meta_doi="", location={"kind": "table", "id": t["table_id"]},
                                source_digest=t["digest"], provenance="TYPED_TABLE", trial_label="",
                                measure=t["measure"] or "", outcome_definition=t["caption"])
        if not t["pooled"]:
            continue
        if not sm.outcome_identity(probe, spec["keywords"], (), tuple(spec.get("core") or ())):
            basis = "CAPTION"
        else:
            sent = sm.pooled_sentence(text, t["pooled"], terms)
            if not sent:
                continue
            basis = "POOLED_SENTENCE: " + sent
        pc = sm.positive_control(t["rows"], t["pooled"], t["measure"] or "")
        if pc["reproduced"]:
            ok.append({**t, "positive_control": pc, "identity_basis": basis})
    return ok[0] if len(ok) == 1 else None


def comparator_terms(slug):
    """The topic's REGISTERED wording of the comparator's efficacy outcome (topics/<slug>.json comparator_outcomes)."""
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    return [k for co in cfg.get("comparator_outcomes") or [] if co.get("kind") == "efficacy" for k in co.get("keywords") or []]


LOCATE_SCHEMA = {"type": "object", "additionalProperties": False,
                 "required": ["state", "quote", "measure", "point", "lower", "upper", "events_t", "n_t", "events_c", "n_c"],
                 "properties": {"state": {"type": "string", "enum": ["REPORTED", "NOT_REPORTED"]},
                                **{k: {"type": ["string", "null"]} for k in ("quote", "measure", "point", "lower", "upper",
                                                                           "events_t", "n_t", "events_c", "n_c")}}}
LOCATE_INSTR = """You are given the abstract (and, if available, full text) of ONE randomised trial report and ONE outcome.
Quote, character for character, the shortest passage that states the trial's RESULT for that outcome comparing the
intervention with the control. Copy the numbers exactly as printed in your quote: the effect measure with its point estimate
and confidence limits, and/or events and totals per arm. Use null for anything not printed in your quote; never compute.
If the text does not report a between-arm result for this outcome, state=NOT_REPORTED.
"""


def _trial_text(slug, pmid, run):
    rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    rec = next((x for x in rj.get("records", []) if str(x.get("id")) == pmid), None)
    mp = os.path.join(ROOT, "outputs", "k_gap", "member_records.json")
    mrec = _j(mp) if os.path.exists(mp) else {}
    rec = rec or mrec.get(pmid)
    if rec is None and run:
        from harness import fetch
        got = fetch._efetch([pmid])
        if got:
            rec = got[0]
            mrec[pmid] = rec
            _save(mp, mrec)
    return rec


def _norm_ws(t):
    return re.sub(r"\s+", " ", (t or "").replace("\u2212", "-")).strip()


def primary_value(slug, pmid, run, runs, want=None):
    """(primary dict with span, how) for one trial from ITS OWN report: regex on the abstract, then the typed full-text
    rung, then a recorded locator whose quote must be verbatim in the report and must contain every number it copies
    (the model only LOCATES; each number is a string the report itself prints)."""
    import k_gap_counterfactual as cfm
    from harness import extract, pipeline
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    po = cfg.get("primary_outcome") or {}
    interv, comp = cfg.get("intervention_terms"), cfg.get("comparator_terms")
    dc = extract.declared_is_composite(po.get("name", ""))
    rec = _trial_text(slug, pmid, run)
    if not rec:
        return None, "NO_RECORD"

    def as_prim(r, how):
        if r and not r.get("absent") and r.get("effect") is not None and r.get("ci_low") is not None:
            return {"measure": (r.get("scale") or "").upper(), "effect": str(r["effect"]), "lower": str(r["ci_low"]),
                    "upper": str(r["ci_high"]), "source": f"PMID {pmid} {how}", "span": str(r.get("source") or "")}, how
        if r and not r.get("absent") and r.get("ai") is not None:
            return {"measure": "RR", "events_t": r["ai"], "n_t": r["n1i"], "events_c": r["ci"], "n_c": r["n2i"],
                    "source": f"PMID {pmid} {how}", "span": str(r.get("source") or "")}, how
        return None, None
    got = as_prim(extract.extract_trial(rec.get("abstract") or "", po.get("keywords") or [], interv, comp,
                                        declared_composite=dc, estimand=po.get("estimand")), "REGEX_ABSTRACT")
    if got[0] and (want != "counts" or got[0].get("events_t") is not None):
        return got
    ft = cfm.pmc_fulltext_cached(pmid, offline=not run)
    if ft:
        got = as_prim(pipeline._fulltext_extract(ft, po, interv, comp, dc), "TYPED_FULLTEXT")
        if got[0] and (want != "counts" or got[0].get("events_t") is not None):
            return got
    if not ft and rec.get("doi"):
        # a further legitimate open route: Unpaywall's OA copy as typed text (never OCR)
        u = k_gap.unpaywall_text(rec["doi"], os.path.join(ROOT, "outputs", "k_gap", "_upw"),
                                 os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json"), offline=not run)
        ft = (u.get("text") or "")[:120000]
    text = (rec.get("title") or "") + "\n" + (rec.get("abstract") or "") + ("\n\n" + ft if ft else "")
    wanted = ("" if not want else
              "\nWANTED: the number of participants WITH the outcome and the number randomised, in EACH arm (events_t, n_t, "
              "events_c, n_c), copied as printed.\n" if want == "counts" else
              f"\nWANTED: the {want} with its 95% confidence interval, copied as printed.\n")
    p = (LOCATE_INSTR + wanted + f"\nOUTCOME: {po.get('name')}\n<<<TEXT\n{text}\nTEXT>>>\n").encode("utf-8")
    key = f"locate::{slug}::{pmid}" + (f"::{want}" if want else "")
    r = runs.get(key)
    if (not r or r.get("prompt_sha256") != hashlib.sha256(p).hexdigest()) and run:
        rec_c = mcl.call(p, schema=LOCATE_SCHEMA, model=fp.MODEL, effort=fp.EFFORT,
                         caller={"file": "scripts/secondary_meta_build.py", "line": "primary_value",
                                 "purpose": f"secondary-tier primary verification locate {slug} PMID {pmid} (acq/k-gap lane)"},
                         input_digests=[{"ref": f"trial report PMID {pmid} (abstract + PMC OA full text if held)",
                                         "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                         "what": "held text shown whole"}],
                         timeout_s=1200)
        ms.write_record(rec_c, REC_DIR)
        r = runs[key] = {"record_id": rec_c["record_id"], "state": rec_c["state"],
                         "prompt_sha256": hashlib.sha256(p).hexdigest()}
    if not r or r.get("state") != "RAN_OK":
        return None, "LOCATOR_NOT_RUN"
    claim = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
    # the deterministic gate is harness code (secondary_meta.gate_locator_claim): one implementation, typed reasons
    val, why = sm.gate_locator_claim(claim, text, prefer="counts" if want == "counts" else None)
    if val:
        return {**val, "source": f"PMID {pmid} LOCATOR:{r['record_id']}"}, "LOCATOR_QUOTE"
    return None, f"LOCATOR_{why}"
    if claim.get("state") != "REPORTED" or not claim.get("quote"):   # (superseded; unreachable)
        return None, "LOCATOR_NOT_REPORTED"
    q = _norm_ws(claim["quote"])
    if q not in _norm_ws(text):
        return None, "LOCATOR_QUOTE_NOT_IN_TEXT"
    nums = {k: claim.get(k) for k in ("point", "lower", "upper", "events_t", "n_t", "events_c", "n_c") if claim.get(k)}
    if not nums or not all(re.search(r"(?<![\d.])" + re.escape(_norm_ws(v)) + r"(?![\d])", q) for v in nums.values()):
        return None, "LOCATOR_NUMBER_NOT_IN_QUOTE"
    if not all(re.fullmatch(r"-?\d+(?:\.\d+)?", _norm_ws(v)) for v in nums.values()):
        return None, "LOCATOR_NON_NUMERIC"                   # e.g. '0:31' (h:mm): a string in the quote, not a number
    meas = (claim.get("measure") or "").upper()
    meas = ("HR" if "HAZARD" in meas else "RR" if ("RISK" in meas or meas == "RR") else
            "OR" if ("ODDS" in meas or meas == "OR") else meas)
    if claim.get("point") and claim.get("lower") and claim.get("upper"):
        return {"measure": meas, "effect": claim["point"], "lower": claim["lower"], "upper": claim["upper"],
                "source": f"PMID {pmid} LOCATOR:{r['record_id']}", "span": claim["quote"]}, "LOCATOR_QUOTE"
    if all(claim.get(k) for k in ("events_t", "n_t", "events_c", "n_c")):
        return {"measure": "RR", "events_t": int(claim["events_t"]), "n_t": int(claim["n_t"]),
                "events_c": int(claim["events_c"]), "n_c": int(claim["n_c"]),
                "source": f"PMID {pmid} LOCATOR:{r['record_id']}", "span": claim["quote"]}, "LOCATOR_QUOTE"
    return None, "LOCATOR_INCOMPLETE"


def read_one(item):
    p = fp.prompt_bytes(item)
    rec = mcl.call(p, schema=fp.SCHEMA, model=fp.MODEL, effort=fp.EFFORT,
                   caller={"file": "scripts/secondary_meta_build.py", "line": "read_one",
                           "purpose": f"secondary-tier forest read {item['slug']} meta {item['pmid']} (acq/k-gap lane)"},
                   input_digests=[{"ref": item["image_ref"], "sha256": item["image_sha256"],
                                   "what": "secondary meta forest-plot figure attached with -i"}],
                   timeout_s=900, images=(item["image_path"],))
    ms.write_record(rec, REC_DIR)
    return {"key": f"{item['slug']}::{item['pmid']}", "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": hashlib.sha256(p).hexdigest(), "image_sha256": item["image_sha256"]}


# ------------------------------------------------------------------ our trials (family resolution + primary values)

def our_trials(slug):
    """One entry per TRIAL (keyed by NCT where registered): our branch extraction of the trial's own report (the PRIMARY
    value + span, the verification side), else a comparator-resolved k-gap family with no primary value yet."""
    # the verification side is OUR extraction of the trial's own report, as this branch builds it (in memory, fixes 3-4
    # applied): the served semaglutide-weight rows are CT.gov observed means, the quantity fix 3 showed is not the
    # trial's reported result, so the served page is not the primary reference for them
    import k_gap_counterfactual as cfm
    import k_gap_identity_reader2 as r2
    import k_gap_result_agreement as ra
    rev = cfm.build(slug)
    prim = next((o for o in rev["outcomes"] if o.get("primary")), {})
    T = _j(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"))
    rows = [r for r in T["trials"] if r["slug"] == slug]
    acr_nct, acr_pmid, nct_pmid = {}, {}, {}
    for r in rows:
        names = {v["acronym"] for v in (r.get("study") or {}).values() if (v or {}).get("acronym")}
        for n in r["ncts"]:
            acr_nct.setdefault(n, set()).update(names)
        for p in r["pmids"]:
            acr_pmid.setdefault(p, set()).update(names)
            for n in r["ncts"]:
                nct_pmid.setdefault(p, n)
    # acronyms the REGISTRY or the PUBLICATION itself gives: a registry title's '(EXSCEL)' (AACT store acr_title), and
    # the trial report's own PubMed title '(Harmony Outcomes)' -- the self-naming rule, never a guess from outside
    store_p = os.path.join(ROOT, "outputs", "k_gap", "_aact_store.json")
    store = _j(store_p) if os.path.exists(store_p) else {}
    for a, ncts in (store.get("acr_title") or {}).items():
        for n in ncts:
            acr_nct.setdefault(n, set()).add(a)

    def title_acronyms(pmid):
        t = pubmed_title(pmid)
        return {m.group(1).strip() for m in re.finditer(r"\(([A-Z][A-Za-z0-9‐-― -]{2,40})\)", t or "")
                if re.search(r"[A-Z]{2,}|[A-Z][a-z]+ [A-Z][a-z]+", m.group(1))}

    out, seen_nct, seen_pid = [], set(), set()
    for t in prim.get("trials", []):
        pid = str(t.get("id", "")).replace("PMID ", "")
        fam = str(t.get("trial_family_id") or "")
        nct = fam if fam.startswith("NCT") else nct_pmid.get(pid)
        prim_val = None
        src = f"our branch extraction {t.get('id')} ({t.get('provenance')})"
        if t.get("effect") is not None and t.get("ci_low") is not None:
            prim_val = {"measure": (t.get("scale") or "").upper(), "effect": str(t["effect"]), "lower": str(t["ci_low"]),
                        "upper": str(t["ci_high"]), "source": src, "span": str(t.get("source") or ""),
                        "report_text": report_text(slug, pid)}
        elif t.get("ai") is not None:
            prim_val = {"measure": "RR", "events_t": t["ai"], "n_t": t["n1i"], "events_c": t["ci"], "n_c": t["n2i"],
                        "source": src, "span": str(t.get("source") or ""), "report_text": report_text(slug, pid)}
        out.append({"id": t.get("id"), "pmid": pid, "nct": nct, "label": str(t.get("label") or ""),
                    "acronyms": sorted(acr_pmid.get(pid, set()) | acr_nct.get(nct, set()) |
                                       (title_acronyms(pid) if pid.isdigit() else set())),
                    "author_year": ra.first_author_year(pid) if pid.isdigit() else None, "primary": prim_val})
        seen_pid.add(pid)
        if nct:
            seen_nct.add(nct)
    # trials we do NOT pool are families too (the tier exists for them): the topic's comparator-resolved k-gap rows.
    # Their report is the RESULT-typed PMID for the NCT (never pmids[0]: ELIXA's first linked PMID is a rat study).
    # No primary value of ours -> their rows wait in the verification queue.
    for r in rows:
        if r["drug"] == "OTHER_AGENT" or not r["pmids"] or r["status"] == "UNRESOLVED":
            continue
        nct = (r["ncts"] or [None])[0]
        pid = r2.shown_pmid(r)
        if (nct and nct in seen_nct) or pid in seen_pid:
            continue
        seen_pid.add(pid)
        if nct:
            seen_nct.add(nct)
        out.append({"id": f"PMID {pid}", "pmid": pid, "nct": nct, "label": r["label"],
                    "acronyms": sorted(acr_pmid.get(pid, set()) | acr_nct.get(nct, set()) | title_acronyms(pid)),
                    "author_year": ra.first_author_year(pid), "primary": None})
    return out


def pubmed_title(pmid):
    """PubMed title of one PMID, cached in outputs/k_gap/pubmed_titles.json (the identity reader's cache)."""
    cp = os.path.join(ROOT, "outputs", "k_gap", "pubmed_titles.json")
    c = _j(cp) if os.path.exists(cp) else {}
    if pmid not in c:
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                              {"db": "pubmed", "id": pmid, "retmode": "json"}, tries=2)
            c[pmid] = (d.get("result", {}).get(pmid) or {}).get("title", "")
        except Exception:  # noqa: BLE001 - no title means no acronym from it, never a guess
            return ""
        _save(cp, c)
    return c.get(pmid) or ""


def report_text(slug, pmid):
    """The trial report's own title + abstract (topic cache, else the member-record cache): the text a primary value is
    anchored against when its stored span is clipped."""
    rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    rec = next((x for x in rj.get("records", []) if str(x.get("id")) == str(pmid)), None)
    if rec is None:
        mp = os.path.join(ROOT, "outputs", "k_gap", "member_records.json")
        rec = (_j(mp) if os.path.exists(mp) else {}).get(str(pmid))
    return ((rec or {}).get("title") or "") + " " + ((rec or {}).get("abstract") or "")


_AACT = {"state": "NOT_ENSURED"}


def ensure_registry(ncts):
    """Index the topic's NCTs from the AACT snapshot (shared adapter). A missing snapshot is RECORDED on the topic
    output (registry route unavailable for this run), never a silent empty registry."""
    try:
        st = aact_adapter.ensure(ncts)
        _AACT.update(state="READY", snapshot=st["snapshot"])
    except FileNotFoundError as exc:
        _AACT.update(state="SNAPSHOT_UNAVAILABLE", why=str(exc)[:200])
    return dict(_AACT)


def primary_sources(slug, pmid, nct=None):
    """Every held primary source for one trial, offline: [(kind, ref, payload)]. Texts: abstract, PMC OA, the held
    cache/<slug>/ft_<pmid>.txt (markup stripped), the Unpaywall copy. Registry: posted CT.gov results for its NCT(s) from
    the local AACT index (scripts/k_gap_bulk_acquire.py)."""
    import hashlib as _h
    out = []
    mp = os.path.join(ROOT, "outputs", "k_gap", "member_records.json")
    rec = None
    rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    rec = next((x for x in rj.get("records", []) if str(x.get("id")) == str(pmid)), None)
    if rec is None and os.path.exists(mp):
        rec = _j(mp).get(str(pmid))
    if rec:
        out.append(("text", f"PMID {pmid} abstract", (rec.get("title") or "") + " " + (rec.get("abstract") or "")))
    for ref, fpth in ((f"PMID {pmid} PMC OA", os.path.join(ROOT, "outputs", "k_gap", "_ft", f"{pmid}.txt")),
                      (f"PMID {pmid} held cache/{slug}/ft_{pmid}.txt", os.path.join(ROOT, "cache", slug, f"ft_{pmid}.txt"))):
        if os.path.exists(fpth) and os.path.getsize(fpth) > 0:
            with open(fpth, encoding="utf-8", errors="replace") as fh:
                out.append(("text", ref, re.sub(r"<[^>]+>", " ", fh.read())))
    doi = ((rec or {}).get("doi") or "").lower()
    if doi:
        up = os.path.join(ROOT, "outputs", "k_gap", "_upw", _h.sha1(doi.encode("utf-8")).hexdigest()[:16] + ".txt")
        if os.path.exists(up) and os.path.getsize(up) > 0:
            with open(up, encoding="utf-8", errors="replace") as fh:
                out.append(("text", f"PMID {pmid} Unpaywall OA (doi {doi})", fh.read()))
    if _AACT.get("state") == "READY":           # build() ran aact_adapter.ensure for this topic's NCTs
        for n in sorted({x for x in (nct, (rec or {}).get("nct")) if x}):
            reg = aact_adapter.registry_for(n)
            if reg:
                out.append(("registry", f"{n} CT.gov posted results ({reg['_snapshot']['id']})", reg))
    return out


_REFS = {}


def meta_aliases(pmid):
    """One candidate meta under every id it can be cited by: its PMID and the DOI its own JATS front declares."""
    d = os.path.join(k_gap.COMP_DIR, str(pmid))
    ids = {str(pmid)}
    jp = next((os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith("_kgap_jats.xml")), None)         if os.path.isdir(d) else None
    if jp:
        with open(jp, "rb") as fh:
            front = fh.read().split(b"<body", 1)[0]
        m = re.search(rb"<article-id[^>]*pub-id-type=[\"']doi[\"'][^>]*>\s*([^<\s]+)", front)
        if m:
            ids.add(m.group(1).decode("utf-8", "replace").strip().lower())
    return ids


def refs_of(pmid):
    """The PMIDs/DOIs a meta cites (its held JATS reference list), or None when no JATS / no reference list is held."""
    if pmid not in _REFS:
        d = os.path.join(k_gap.COMP_DIR, str(pmid))
        jp = next((os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith("_kgap_jats.xml")), None) \
            if os.path.isdir(d) else None
        if jp:
            with open(jp, "rb") as fh:
                _REFS[pmid] = sm.cited_ids_from_jats(fh.read())
        else:
            _REFS[pmid] = None
    return _REFS[pmid]


def family_of_factory(ours):
    # a year glued to its acronym ('RALES2000', 'EPHESUS2003') is split before tokenising, or the acronym never leads
    import unicodedata

    def _fold(x):
        # accents folded ('Alpérovitch' -> alperovitch), so an accented letter never splits a name into two tokens
        return "".join(c for c in unicodedata.normalize("NFKD", k_gap.fold_dashes(str(x or ""))) if not unicodedata.combining(c))

    toks = lambda x: re.findall(r"[a-z0-9]+", re.sub(r"(?<=[a-z])(?=(?:19|20)\d\d\b)", " ",   # noqa: E731
                                                       _fold(x).lower()))

    def prefix(a, b):
        """a and b name the same trial when one's tokens lead the other's ('HARMONY' / 'Harmony Outcomes'), with a
        distinctive first token; 'STEP' then leads both 'STEP 1' and 'STEP 3' and is refused as ambiguous below."""
        n = min(len(a), len(b))
        return n > 0 and a[:n] == b[:n] and (len(a[0]) >= 4 or n >= 2)

    def within(a, n):
        """the acronym as a contiguous run anywhere in the label ('Rosas (COVACTA)'), distinctive only"""
        return (len(n[0]) >= 4 or len(n) >= 2) and any(a[i:i + len(n)] == n for i in range(len(a) - len(n) + 1))

    def core(label):
        """(surname core, year) of an author label: tokens up to 'et al' / a reference number / the year, single-letter
        initials dropped, spacing folded ('Helps et al52' -> helps; 'Mewton N-2019' -> mewton, 2019; 'Re faie 2005' ->
        refaie). None unless it is a short (<= 3 token) name of >= 4 letters."""
        tt = toks(label)
        yr = next((m.group(0) for x in tt for m in [re.match(r"(?:19|20)\d\d", x)] if m), None)
        name = []
        for x in tt:
            if x == "et" or x[0].isdigit() or re.fullmatch(r"al\d*", x):
                break
            if len(x) > 1:
                name.append(x)
        c = "".join(name)
        return (c, yr) if 1 <= len(name) <= 3 and len(c) >= 4 else (None, yr)

    def cores(label, forename_first=False):
        """Every surname core a label can carry: as printed (accents folded), with non-ASCII letters DROPPED (a reader
        that lost the 'ö' of 'Lönnermark' printed 'Lnnermark'), and -- for a row only -- each single name token
        ('Mehdi Akrami-2012': forename first)."""
        out = set()
        for lab in (label, re.sub(r"[^\x00-\x7f]", "", str(label or ""))):
            c, _ = core(lab)
            if c:
                out.add(c)
            if forename_first:
                tt = [x for x in toks(lab) if not x[0].isdigit()]
                if len(tt) == 2 and all(len(x) >= 4 for x in tt):
                    out |= set(tt)
        return out

    def acronym(label):
        return bool(re.match(r"\s*[A-Z][A-Z0-9-]{3,}", str(label or "")))

    def same_author(row_label, t_label):
        # a comparator's trial list labelled 'Helps et al52' and its forest row 'Helps 2015' name one trial; never when
        # both carry a year and the years differ ('Palomba 2004' / 'Palomba 2005a') -- except by ONE year for an
        # all-caps acronym ('RALES2000' / 'RALES1999': an acronym names the trial, its year is a publication date)
        ya, yb = core(row_label)[1], core(t_label)[1]
        if ya and yb and ya != yb and not (abs(int(ya) - int(yb)) == 1 and acronym(row_label) and acronym(t_label)):
            return False
        return bool(cores(row_label, forename_first=True) & cores(t_label))
    ref_rx = re.compile(r"\s*[\[(]\s*(\d+)\s*[\])]\s*$")

    def compact(label):
        """The label with spacing and punctuation gone and its trailing citation furniture removed -- reference numbers
        glued or standalone ('SCALEMaintenance25,38', 'SURMOUNT-1 39'), a year (', 2013'), bracketed numbers -- so a
        table cell that lost its spaces meets the figure row that kept them. A trial NUMBER stays ('STEP 8'): a
        standalone trailing number is stripped only after another number."""
        x = _fold(label)
        x = re.sub(r"[\[(]\s*[\d,\s\u2013-]+\s*[\])]", " ", x)          # [12] (12) (19,20)
        x = re.sub(r",?\s*(?:19|20)\d\d[a-z]?\b", " ", x)                    # a year
        x = re.sub(r"(?<=[A-Za-z])\d+(?:,\d+)*\s*$", "", x.strip())          # glued ref numbers 'Maintenance25,38'
        tt = x.split()
        while len(tt) >= 2 and re.fullmatch(r"\d+(?:,\d+)*", tt[-1]) and re.search(r"\d$", tt[-2]):
            tt.pop()                                                          # 'SURMOUNT-1 39' -> 'SURMOUNT-1'
        c = re.sub(r"[^a-z0-9]", "", " ".join(tt).lower())
        return c if len(c) >= 6 else None

    def years_ok(row_label, t):
        """the year rule of every tier: when both sides carry a year (the label's, else the entry's PMID year) they are
        equal -- or one apart for an all-caps acronym; an author's year is never relaxed (Nagtegaal 1995 vs 1998)"""
        ya = core(row_label)[1]
        yb = core(t["label"])[1] or (t.get("author_year") or (None, None))[1]
        if not (ya and yb) or ya == yb:
            return True
        return abs(int(ya) - int(yb)) == 1 and acronym(row_label) and acronym(t["label"])

    def ay_hit(t, lt):
        # the PMID's first author is accented ('garzón'); the row's tokens are folded ('garzon')
        a = t.get("author_year")
        sur = toks(a[0]) if a else []
        return bool(sur) and sur[0] in lt and str(a[1]) in lt

    def family_of(row):
        lt = toks(ref_rx.sub("", row.trial_label or ""))
        hits = {}
        for t in ours:
            # the TRIAL-LIST label's trailing reference number is stripped like the row's: 'Zinman (8)' tokenised to
            # ['zinman', '8'] and could never lead the figure's 'Zinman 2016' (sglt2-primary-prevention-hf: 8 accepted
            # rows read, none joined). Reference numbers are NOT compared (melatonin: figure 'Wade AG, 2011 [21]' is list
            # 'Wade AG [22]'). A generic clinical abbreviation ('HFPEF', 'MACE') is never a trial's name (acq/k-gap
            # f34580f9: 'HFpEF' joined a row to DELIVER) -- consolidated 2026-10-04 onto finish-line's scored join
            lab = ref_rx.sub("", t["label"] or "")
            names = [toks(a) for a in t["acronyms"] if re.sub(r"[^A-Z0-9]", "", str(a).upper()) not in k_gap._NOT_ACRO] + \
                ([toks(lab)] if lab and not lab.isdigit() else [])
            matched = sorted((n for n in names if n and (prefix(lt, n) or within(lt, n))), key=len)
            score, name = (len(matched[-1]), matched[-1]) if matched else (0, None)
            if ay_hit(t, lt):
                # first author AND year confirmed outranks a bare name ('Young [10]' / 'Young [17]', balanced-crystalloids);
                # the author is accent-folded ('garzon')
                score, name = score + 10, (name or toks(t["author_year"][0]))
            if score:
                hits[t["id"]] = (t, score, name)
        if not hits:
            # FALLBACK tier only (acq/k-gap e89dfe86): the surname core never adds a hit to (and so never dilutes or
            # overrides) a join the rules above already made ('Young [10]' / 'Young [17]' by their PMIDs' author-year).
            # Consolidated 2026-10-04 with g1/finish-line's scored join: a fallback hit scores 1 and names its core, so
            # two fallback hits on one surname tie and bind to neither.
            for t in ours:
                yr = (t.get("author_year") or (None, None))[1]
                if t["label"] and same_author(row.trial_label, t["label"] + (f" {yr}" if yr and not core(t["label"])[1] else "")):
                    hits[t["id"]] = (t, 1, [core(t["label"])[0]])
        if not hits:
            # last tier: the compact label (spacing lost in table extraction: 'SCALEMaintenance25,38'), unique or nothing
            rc = compact(row.trial_label)
            if rc:
                hits = {t["id"]: (t, 1, [rc]) for t in ours
                        if t["label"] and compact(t["label"]) == rc and years_ok(row.trial_label, t)}
                if len(hits) > 1:
                    return None
        if len(hits) > 1:
            # two trials share an acronym ('CORIMUNO' names CORIMUNO-TOCI-1 and CORIMUNO-TOCI-ICU): the ONE whose full
            # label tokens EQUAL the row's label wins; else the one whose matching name is LONGEST ('Semler (SALT trial)'
            # over a bare 'Semler'), unique or nothing
            exact = [i for i, (t, _, _) in hits.items() if t["label"] and toks(ref_rx.sub("", t["label"])) == lt]
            if len(exact) == 1:
                return exact[0]
            # a bare family acronym ('ODYSSEY') hits every trial of the family: the ONE label the row's tokens LEAD
            # ('ODYSSEY FH II' -> 'ODYSSEY FH II NCT01709500') wins (acq/k-gap 63119c57; consolidated 2026-10-04)
            lead = [i for i, (t, _, _) in hits.items() if len(lt) >= 2 and t["label"] and toks(t["label"])[:len(lt)] == lt]
            if len(lead) == 1:
                return lead[0]
            # the compact label breaks a tie the surname tier made ('SURMOUNT-1, 2022' hits SURMOUNT-1 and SURMOUNT-3)
            rc = compact(row.trial_label)
            same = [i for i, (t, _, _) in hits.items() if rc and t["label"] and compact(t["label"]) == rc
                    and years_ok(row.trial_label, t)]
            if len(same) == 1:
                return same[0]
            # ...and only when every other hit's name LEADS the winner's (a bare 'Semler' inside 'Semler (SALT trial)'):
            # a row naming two different trials ('SOLOIST-WHF/SCORED') is a combined row and binds to neither
            top = max(s for _, s, _ in hits.values())
            best = [i for i, (_, s, _) in hits.items() if s == top]
            if len(best) != 1 or hits[best[0]][2] is None:
                return None
            win = hits[best[0]][2]
            ok = all(n is not None and win[:len(n)] == n for i, (_, _, n) in hits.items() if i != best[0])
            return best[0] if ok else None
        return next(iter(hits)) if len(hits) == 1 else None
    return family_of


def spec_of(slug):
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    po = cfg.get("primary_outcome") or {}
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    kw = list(po.get("keywords") or []) + [str(x) for x in list((c.get("outcome_endpoints") or {}).keys()) +
                                           list((c.get("outcome_endpoints") or {}).values())] + [po.get("name") or ""]
    est = (po.get("estimand") or "").upper()
    est = {"HAZARD RATIO": "HR", "RISK RATIO": "RR", "ODDS RATIO": "OR", "MEAN DIFFERENCE": "MD"}.get(est, est)
    # a CORE word lets 'mortality' match '28-day all-cause mortality' (the timepoint is then checked on its own). Only for
    # a single-noun outcome: for a composite, 'cardiovascular' would admit a cardiovascular-DEATH figure as MACE.
    name = (po.get("name") or "").lower()
    core = [w for w in ("mortality", "death") if w in name]
    return {"estimand": est, "keywords": [k for k in kw if k], "components": [], "core": core,
            "timepoint": po.get("timepoint")}


_TP = re.compile(r"(\d+)[- ]day (?:all[- ]cause )?mortality|mortality (?:at|by|within) (?:day )?(\d+)(?:[- ]days?)?|"
                 r"day[- ](\d+) (?:all[- ]cause )?mortality", re.I)


def meta_timepoint(held):
    """The mortality timepoint the meta itself states, only when it states exactly ONE (else unknown -> refused by
    the timepoint check for a topic that registers one)."""
    vals = {next(g for g in m.groups() if g) for m in _TP.finditer(held or "")}
    return f"{vals.pop()} days" if len(vals) == 1 else None


# ------------------------------------------------------------------ driver

def normalize_measure(text):
    """A forest read's measure wording as a typed measure. 'Fixed effect relative risk (95% CI)' is RR (it was left as
    printed and refused as 'not the estimand RR'); a RATE ratio is IRR, never a ratio of risks; a STANDARDISED mean
    difference is SMD, never MD. Unknown wording stays as printed (and is refused downstream)."""
    m = (text or "").upper().strip()
    if "HAZARD" in m or re.fullmatch(r"HRS?", m):
        return "HR"
    if "RATE RATIO" in m or "INCIDENCE RATE" in m or re.fullmatch(r"IRR", m):
        return "IRR"
    if "RISK RATIO" in m or "RELATIVE RISK" in m or re.fullmatch(r"RRS?", m) or re.match(r"RR\b", m):
        return "RR"
    if "ODDS" in m or re.fullmatch(r"ORS?", m) or re.match(r"OR\b", m):
        return "OR"
    if re.search(r"STD\.?\s*MEAN|STANDARDI[SZ]ED MEAN|\bSMD\b", m):
        return "SMD"
    if "MEAN" in m or m in ("MD", "WMD"):
        return "MD"
    return (text or "").upper().strip()


def figure_rows(slug, it, run_r, spec, comp):
    """The rows of ONE recorded forest-plot read of a meta (secondary tier), through its deterministic gates: rows
    consistent, the pool printed in the meta's text (or, failing that, in the figure), and the rows reproducing it
    (positive control). Returns (rows or [], meta entry). Shared by build() and scripts/g1_two_source_sweep.py so both
    use exactly one gate."""
    resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, run_r["record_id"] + ".json"))).decode("utf-8"))
    g = fp.gate(resp, None, it["held"])                       # rows consistent + pool printed in THIS meta's text
    control_basis = "POOL_PRINTED_IN_META_TEXT"
    _fp_ok = all(re.fullmatch(r"-?\d+(?:\.\d+)?", str((resp.get("pooled") or {}).get(k) or "").strip())
                 for k in ("effect", "lower", "upper"))
    if g["state"] != "PASS" and g["problems"] == ["PLOT_POOLED_NOT_PRINTED_IN_TEXT"] and _fp_ok:
        # The meta does not repeat its pooled result in the text: the control target is the pooled row PRINTED in
        # the figure. Recomputation from the rows is still required (a misread row still fails it); what this
        # weaker basis cannot catch -- a wrong-analysis figure -- is left to primary verification, which every row
        # must pass before it counts. The basis is recorded on the meta.
        fig_pool = resp.get("pooled") or {}
        g = fp.gate(resp, {"effect": fig_pool.get("effect"), "lower": fig_pool.get("lower"),
                           "upper": fig_pool.get("upper"), "k": None, "quote": None, "method": None}, it["held"])
        control_basis = "POOL_PRINTED_IN_FIGURE"
    measure = normalize_measure(resp.get("measure"))
    mrows = []
    for x in (g.get("rows") or []):
        pr = x.get("printed") or {}
        mrows.append(sm.SecondaryRow(
            meta_pmid=it["pmid"], meta_doi="", source_digest=it["image_sha256"],
            location={"kind": "figure", "id": it["figure"]["fig_id"], "panel": it["figure"].get("panel"),
                      "row_label": x["label"]},
            provenance=f"MODEL_PROPOSAL:{run_r['record_id']}", trial_label=x["label"], measure=measure,
            outcome_definition=(it["figure"].get("panel_title") or it["figure"]["caption"])[:300],
            timepoint=meta_timepoint(it["held"]) if spec.get("core") else None,   # mortality/death outcomes only
            effect=pr.get("effect"), lower=pr.get("lower"), upper=pr.get("upper")))
    pc = sm.positive_control(mrows, g["printed_pool"], measure,
                             stated_model=" ".join(str(resp.get(k) or "") for k in ("measure", "notes", "model"))) \
        if g.get("printed_pool") and mrows else \
        {"reproduced": False, "why": "NO_PRINTED_POOL_IN_TEXT"}
    usable = g["state"] == "PASS" and pc["reproduced"]
    entry = {"figure": it["figure"]["fig_id"], "panel": it["figure"].get("panel"), "measure": measure,
                             "gate": g["state"], "gate_problems": g["problems"][:6], "positive_control": pc,
                             "control_basis": control_basis, "pooled": g.get("printed_pool"),
                             "rows_read": len(mrows), "usable": usable, "record_id": run_r["record_id"],
                             "is_comparator": it["pmid"] == comp}
    return (mrows if usable else []), entry


def build(slug, run, runs):
    metas, comp = metas_for(slug, offline=not run)
    spec = spec_of(slug)
    items, skipped, typed = [], {}, {}
    for pmid in metas:
        # TYPED FIRST: a meta that prints its per-trial results in a JATS table is read by regex, and its figure is
        # never sent to a model. A table counts only if it names the topic outcome, carries its own pooled row, and its
        # rows reproduce that pooled row; exactly one such table, or none is used.
        t = typed_table(slug, pmid, spec, run)
        if t:
            typed[pmid] = t
            continue
        try:
            it, why = meta_item(slug, pmid, offline=not run)
        except Exception as exc:  # noqa: BLE001 - one meta's failure is recorded, never fatal to the topic
            it, why = None, f"ERROR:{type(exc).__name__}:{str(exc)[:80]}"
        if it:
            items.append(it)
        else:
            skipped[pmid] = why
    if run:
        done = {(r["prompt_sha256"], r.get("image_sha256")) for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [i for i in items if (hashlib.sha256(fp.prompt_bytes(i)).hexdigest(), i["image_sha256"]) not in done]
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(read_one, todo):
                runs[r["key"]] = r
                print(r["key"], r["state"], r["record_id"], flush=True)
    ours = our_trials(slug)
    registry_state = ensure_registry([t["nct"] for t in ours if t.get("nct")])
    fam = family_of_factory(ours)
    rows, metas_out = [], {}
    for pmid, t in typed.items():
        metas_out[pmid] = {"table": t["table_id"], "measure": t["measure"], "provenance": "TYPED_TABLE",
                           "identity_basis": t.get("identity_basis"), "pooled": t.get("pooled"),
                           "row_findings": {r.trial_label: r.findings for r in t["rows"] if r.findings},
                           "positive_control": t["positive_control"], "rows_read": len(t["rows"]), "usable": True,
                           "is_comparator": pmid == comp}
        for r in t["rows"]:
            rows.append(sm.admit(r, spec, fam))
    for it in items:
        run_r = runs.get(f"{slug}::{it['pmid']}")
        if not run_r or run_r["state"] != "RAN_OK" or run_r["image_sha256"] != it["image_sha256"]:
            metas_out[it["pmid"]] = {"state": "NO_RECORDED_READ"}
            continue
        mrows, metas_out[it["pmid"]] = figure_rows(slug, it, run_r, spec, comp)
        for r in mrows:
            rows.append(sm.admit(r, spec, fam))
    # DUAL-MODEL figure rows (scripts/g1_forest_reader.py; its replayed output, no model here): a meta whose own route
    # above gave no usable row contributes the rows two model families (codex + agy) agreed on, from a figure whose
    # printed pool the meta's STATED model reproduced from those rows. They are the meta's own numbers -- SECONDARY,
    # verified like any row below, and never counted toward G1 agreement with that meta (sm.g1_countable).
    import g1_forest_reader as gfr
    dual = {}
    for d in gfr.accepted_rows(slug):
        dual.setdefault(d["meta_pmid"], []).append(d)
    for pm, ds in sorted(dual.items()):
        if (metas_out.get(pm) or {}).get("usable"):
            continue
        if str(pm) == str(comp):
            # the COMPARATOR's own dual read is not secondary evidence for our pool: g1_tracker.lane_comparator_rows
            # consumes it under the COMPARATOR_SOURCED gate (its own outcome by definition, its own labels, any measure).
            # Ingested here it went through the secondary admission meant for OTHER metas (outcome vocabulary, estimand,
            # family join) and lost 27 comparator-sourced rows (pcsk9 'major vascular events' RR; iv-iron 'total heart
            # failure hospitalizations'): a semantic conflict between g1/forest-reader 99e1c0a8 and acq/k-gap's coverage,
            # found when the lanes were consolidated (2026-10-04).
            continue
        # the timepoint the FIGURE's own caption states ('28-Day All-Cause Mortality in Each Trial', REACT) is the most
        # specific statement of it; else, as for every figure row, the meta's text for a core (mortality) outcome
        tp_text = meta_timepoint(gfr.held_text(pm)) if spec.get("core") else None
        for d in ds:
            r = sm.SecondaryRow(**{k: v for k, v in d.items() if k in sm.SecondaryRow.__dataclass_fields__})
            r.timepoint = meta_timepoint(r.outcome_definition) or tp_text
            rows.append(sm.admit(r, spec, fam))
        metas_out[pm] = {"figure": ds[0]["location"]["id"], "panel": ds[0]["location"].get("panel"),
                         "measure": ds[0]["measure"], "provenance": "MODEL_PROPOSAL_DUAL", "usable": True,
                         "rows_read": len(ds), "record_ids": ds[0]["provenance"].split(":", 1)[1].split("+"),
                         # a SECOND_SOURCE_ONLY figure (no printed pool) did NOT self-reproduce: say so (decision 5 Oct)
                         "positive_control": ({"reproduced": False, "why": sm.POOL_UNCHECKABLE,
                                               "basis": "g1_forest_reader: rows agreed, no printed pooled row"}
                                              if any(sm.pool_uncheckable(r) for r in rows if r.meta_pmid == pm) else
                                              {"reproduced": True, "basis": "g1_forest_reader acceptance (stated model)"}),
                         "is_comparator": pm == comp, "earlier_route": metas_out.get(pm) or skipped.get(pm)}
        skipped.pop(pm, None)
    sm.consolidate(rows)
    sm.cross_check(rows)
    # CROSS-CHECK BLOCKS ARE REFEREED BY THE TRIAL'S OWN REPORT: two metas that disagree on a trial block each other
    # 'until resolved', and the resolution is the trial's own report -- so blocked rows go through the same primary
    # verification as unblocked ones (a row matching the primary is verified; the other is a MISMATCH that names its
    # side). Without a primary they stay BLOCKED. Before this, a blocked row was never compared with the primary:
    # PIONEER 6 (glp1) lost its 'SECONDARY_WRONG' side once a second meta's dual-read row (upper 1.11 vs 1.10) blocked
    # the comparator's row, and G1_MATCHED fell on DIVERGENCES_NAMED (consolidation 2026-10-04).
    refereed = {id(r) for r in rows if r.state == sm.BLOCKED}
    for r in rows:
        if id(r) in refereed:
            r.state = sm.UNVERIFIED
    by_id = {t["id"]: t for t in ours}
    # DETERMINISTIC VERIFICATION FIRST (no model, no network): the meta's exact printed numbers found by regex in the
    # trial's held primary sources -- abstract, PMC OA text, held cache/<slug>/ft_<pmid>.txt, Unpaywall text -- or in its
    # posted CT.gov results (local AACT index). Only the residue goes on to our extraction and the recorded locator.
    import time as _time
    _t0 = _time.time()
    terms = [k for k in (spec.get("keywords") or []) if k] + list(spec.get("core") or [])
    nct_of = {t["id"]: t.get("nct") for t in ours}
    typed_n = 0
    for r in rows:
        if r.state == sm.UNVERIFIED and str(r.family_id or "").startswith("PMID "):
            pid = r.family_id[5:]
            sm.verify_typed(r, primary_sources(slug, pid, nct_of.get(r.family_id)), terms)
            typed_n += r.state == sm.VERIFIED
    typed_secs = round(_time.time() - _t0, 2)
    tried = {}
    for r in rows:
        if r.state == sm.UNVERIFIED:
            prim = (by_id.get(r.family_id) or {}).get("primary")
            why = None
            if prim is None and str(r.family_id or "").startswith("PMID "):
                # the VERIFICATION QUEUE: no primary value of ours -> derive it from the trial's OWN report (once per trial)
                if r.family_id not in tried:
                    tried[r.family_id] = primary_value(slug, r.family_id.replace("PMID ", ""), run, runs)
                prim, how = tried[r.family_id]
                why = None if prim else f"NO_PRIMARY:{how}"
                if prim:
                    by_id.setdefault(r.family_id, {})["primary"] = prim
            elif prim is None:
                why = "NO_PRIMARY:FAMILY_NOT_KEYED_BY_PMID"
            sm.verify_against_primary(r, prim, queue_reason=why)
            pid = str(r.family_id or "").replace("PMID ", "")
            if r.state == sm.UNVERIFIED and pid.isdigit():
                v = r.verification or {}
                want = ("counts" if v.get("result") == "MEASURE_DIFFERS" and r.measure.upper() in ("RR", "OR")
                        else r.measure.upper() if v.get("result") == "QUEUED" else None)
                if want:
                    k2 = (r.family_id, want)
                    if k2 not in tried:
                        tried[k2] = primary_value(slug, pid, run, runs, want=want)
                    prim2, how2 = tried[k2]
                    if prim2:
                        r.verification = None
                        sm.verify_against_primary(r, prim2, queue_reason=f"NO_PRIMARY:{how2}")
                    else:
                        r.verification = dict(v, queue_reason=v.get("queue_reason", "") + f" | {want}:{how2}")
    for r in rows:
        if id(r) in refereed and r.state == sm.UNVERIFIED:
            r.state = sm.BLOCKED             # no primary to referee: the disagreement stays a block
    # TWO-SOURCE RULE (2 Oct): the residue with no primary match is verified when two INDEPENDENT metas print the same
    # typed tuple. Independence is read from each meta's own JATS reference list (fail-closed when it has none).
    # every meta that contributed a row is a KNOWN meta of the topic (incl. dual-read metas beyond the search's top N):
    # the common-cited-meta independence check must see all of them
    sm.two_source(rows, refs_of, [meta_aliases(m) for m in dict.fromkeys(list(metas) + sorted({r.meta_pmid for r in rows}))])
    broken = sm.queue_complete(rows)
    if broken:
        raise RuntimeError(f"{slug}: {len(broken)} SECONDARY_UNVERIFIED row(s) with no queue entry: "
                           f"{[(x.trial_label, x.family_id) for x in broken][:5]}")
    queue = [{"trial": r.trial_label, "family": r.family_id, "meta": r.meta_pmid,
              "reason": r.verification["queue_reason"]} for r in rows if r.state == sm.UNVERIFIED]
    g1 = sm.g1_countable(rows, {comp})
    out = {"slug": slug, "comparator_pmid": comp, "metas_considered": metas, "skipped": skipped, "metas": metas_out,
           "tally": dict(Counter(r.state for r in rows)),
           "typed_verification": {"verified": typed_n, "secs": typed_secs}, "registry": registry_state,
           "verification_queue": queue, "verification_queue_reasons": dict(Counter(q["reason"] for q in queue)),
           "g1_countable_vs_comparator": sorted({r.family_id for r in g1}),
           "refusal_reasons": dict(Counter(x.split(":")[0] for r in rows for x in r.reasons)),
           "rows": [r.to_dict() for r in rows]}
    _save(os.path.join(OUTD, f"{slug}.json"), out)
    return out


def verify_replay(slugs, runs):
    """Byte-identical replay, checked: (1) every record the tier uses replays to exactly the response bytes it recorded
    (sha256 of model_source.replay == the stored response digest); (2) rebuilding each topic twice from the records alone
    (no network, no model) gives byte-identical output rows. Returns a list of problems (empty = replayable)."""
    probs = []
    for key, r in sorted(runs.items()):
        if r.get("state") != "RAN_OK":
            continue
        fpth = os.path.join(REC_DIR, r["record_id"] + ".json")
        if not os.path.exists(fpth):
            probs.append(f"{key}: record {r['record_id']} not in {os.path.relpath(REC_DIR, ROOT)}")
            continue
        rec = ms.load_record(fpth)
        if hashlib.sha256(ms.replay(rec)).hexdigest() != rec["response"]["sha256"]:
            probs.append(f"{key}: replay bytes differ from the recorded response")
    for s in slugs:
        a = build(s, False, runs)
        b = build(s, False, runs)
        ha = hashlib.sha256(json.dumps(a["rows"], sort_keys=True).encode("utf-8")).hexdigest()
        hb = hashlib.sha256(json.dumps(b["rows"], sort_keys=True).encode("utf-8")).hexdigest()
        if ha != hb:
            probs.append(f"{s}: two offline rebuilds differ ({ha[:12]} vs {hb[:12]})")
    return probs


def main(argv):
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")] or (list(QUERY) + MORE)
    runs = runs_store.load()          # per-topic ledger: registry/secondary_meta/runs/<slug>.json
    if "--verify-replay" in argv:
        probs = verify_replay(slugs, runs)
        print("REPLAY_OK" if not probs else "REPLAY_PROBLEMS", json.dumps(probs, indent=1))
        return
    for s in slugs:
        try:
            o = build(s, run, runs)
        finally:
            # a build that fails AFTER recorded calls completed must still ledger them, or they are paid for twice
            runs_store.save(runs, slugs={s})
        print(s, "metas", len(o["metas_considered"]), "usable", sum(1 for v in o["metas"].values() if v.get("usable")),
              "tally", o["tally"], "g1_countable", len(o["g1_countable_vs_comparator"]), "skipped", o["skipped"], flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
