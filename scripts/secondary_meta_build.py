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
        tables = sm.typed_rows_from_jats(fh.read(), pmid)
    ok = []
    for t in tables:
        probe = sm.SecondaryRow(meta_pmid=pmid, meta_doi="", location={"kind": "table", "id": t["table_id"]},
                                source_digest=t["digest"], provenance="TYPED_TABLE", trial_label="",
                                measure=t["measure"] or "", outcome_definition=t["caption"])
        if not t["pooled"] or sm.outcome_identity(probe, spec["keywords"], (), tuple(spec.get("core") or ())):
            continue
        pc = sm.positive_control(t["rows"], t["pooled"], t["measure"] or "")
        if pc["reproduced"]:
            ok.append({**t, "positive_control": pc})
    return ok[0] if len(ok) == 1 else None


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
                        "upper": str(t["ci_high"]), "source": src, "span": str(t.get("source") or "")}
        elif t.get("ai") is not None:
            prim_val = {"measure": "RR", "events_t": t["ai"], "n_t": t["n1i"], "events_c": t["ci"], "n_c": t["n2i"],
                        "source": src, "span": str(t.get("source") or "")}
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


def family_of_factory(ours):
    toks = lambda x: re.findall(r"[a-z0-9]+", k_gap.fold_dashes(str(x or "")).lower())   # noqa: E731

    def prefix(a, b):
        """a and b name the same trial when one's tokens lead the other's ('HARMONY' / 'Harmony Outcomes'), with a
        distinctive first token; 'STEP' then leads both 'STEP 1' and 'STEP 3' and is refused as ambiguous below."""
        n = min(len(a), len(b))
        return n > 0 and a[:n] == b[:n] and (len(a[0]) >= 4 or n >= 2)

    def within(a, n):
        """the acronym as a contiguous run anywhere in the label ('Rosas (COVACTA)'), distinctive only"""
        return (len(n[0]) >= 4 or len(n) >= 2) and any(a[i:i + len(n)] == n for i in range(len(a) - len(n) + 1))

    def family_of(row):
        lt = toks(re.sub(r"[\[(]\s*\d+\s*[\])]\s*$", "", row.trial_label))
        hits = {}
        for t in ours:
            names = [toks(a) for a in t["acronyms"]] + ([toks(t["label"])] if t["label"] and not t["label"].isdigit() else [])
            if any(n and (prefix(lt, n) or within(lt, n)) for n in names) or (t["author_year"] and t["author_year"][0] in lt and t["author_year"][1] in lt):
                hits[t["id"]] = t
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
        done = {(r["prompt_sha256"], r["image_sha256"]) for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [i for i in items if (hashlib.sha256(fp.prompt_bytes(i)).hexdigest(), i["image_sha256"]) not in done]
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(read_one, todo):
                runs[r["key"]] = r
                print(r["key"], r["state"], r["record_id"], flush=True)
    ours = our_trials(slug)
    fam = family_of_factory(ours)
    rows, metas_out = [], {}
    for pmid, t in typed.items():
        metas_out[pmid] = {"table": t["table_id"], "measure": t["measure"], "provenance": "TYPED_TABLE",
                           "positive_control": t["positive_control"], "rows_read": len(t["rows"]), "usable": True,
                           "is_comparator": pmid == comp}
        for r in t["rows"]:
            rows.append(sm.admit(r, spec, fam))
    for it in items:
        run_r = runs.get(f"{slug}::{it['pmid']}")
        if not run_r or run_r["state"] != "RAN_OK" or run_r["image_sha256"] != it["image_sha256"]:
            metas_out[it["pmid"]] = {"state": "NO_RECORDED_READ"}
            continue
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, run_r["record_id"] + ".json"))).decode("utf-8"))
        g = fp.gate(resp, None, it["held"])                       # rows consistent + pool printed in THIS meta's text
        measure = (resp.get("measure") or "").upper().strip()
        measure = "HR" if "HAZARD" in measure else "RR" if ("RISK R" in measure or measure == "RR") else \
                  "OR" if ("ODDS" in measure or measure == "OR") else "MD" if ("MEAN" in measure or measure in ("MD", "WMD")) else measure
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
        pc = sm.positive_control(mrows, g["printed_pool"], measure) if g.get("printed_pool") and mrows else \
            {"reproduced": False, "why": "NO_PRINTED_POOL_IN_TEXT"}
        usable = g["state"] == "PASS" and pc["reproduced"]
        metas_out[it["pmid"]] = {"figure": it["figure"]["fig_id"], "panel": it["figure"].get("panel"), "measure": measure,
                                 "gate": g["state"], "gate_problems": g["problems"][:6], "positive_control": pc,
                                 "rows_read": len(mrows), "usable": usable, "record_id": run_r["record_id"],
                                 "is_comparator": it["pmid"] == comp}
        if not usable:
            continue
        for r in mrows:
            rows.append(sm.admit(r, spec, fam))
    sm.consolidate(rows)
    sm.cross_check(rows)
    by_id = {t["id"]: t for t in ours}
    for r in rows:
        if r.state == sm.UNVERIFIED:
            sm.verify_against_primary(r, (by_id.get(r.family_id) or {}).get("primary"))
    g1 = sm.g1_countable(rows, {comp})
    out = {"slug": slug, "comparator_pmid": comp, "metas_considered": metas, "skipped": skipped, "metas": metas_out,
           "tally": dict(Counter(r.state for r in rows)),
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
    rp = os.path.join(OUTD, "runs.json")
    runs = _j(rp) if os.path.exists(rp) else {}
    if "--verify-replay" in argv:
        probs = verify_replay(slugs, runs)
        print("REPLAY_OK" if not probs else "REPLAY_PROBLEMS", json.dumps(probs, indent=1))
        return
    for s in slugs:
        o = build(s, run, runs)
        _save(rp, runs)
        print(s, "metas", len(o["metas_considered"]), "usable", sum(1 for v in o["metas"].values() if v.get("usable")),
              "tally", o["tally"], "g1_countable", len(o["g1_countable_vs_comparator"]), "skipped", o["skipped"], flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
