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
REC_DIR = os.path.join(ROOT, "registry", "model_calls")
DATE = "2026-09-30"
N_CANDIDATES = 3
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


def candidates(slug, offline):
    """The recorded search, cached as its raw response digest + the hit list (small)."""
    p = os.path.join(OUTD, f"search_{slug}.json")
    if os.path.exists(p):
        return _j(p)
    if offline:
        return {"hits": []}
    from harness import http
    q = f'(TITLE:"meta-analysis" OR TITLE:"meta analysis") AND ({QUERY[slug]}) AND OPEN_ACCESS:y AND HAS_FT:y'
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
    fig, why = fp.select_figure(slug, pmid, jats_date=jdate)
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


def read_one(item):
    p = fp.prompt_bytes(item)
    rec = mcl.call(p, schema=fp.SCHEMA, model=fp.MODEL, effort=fp.EFFORT,
                   caller={"file": "scripts/secondary_meta_build.py", "line": "read_one",
                           "purpose": f"secondary-tier forest read {item['slug']} meta {item['pmid']} (acq/k-gap lane)"},
                   input_digests=[{"ref": item["image_ref"], "sha256": item["image_sha256"],
                                   "what": "secondary meta forest-plot figure attached with -i"}],
                   timeout_s=900, runner=fp.image_runner(item["image_path"]))
    ms.write_record(rec, REC_DIR)
    return {"key": f"{item['slug']}::{item['pmid']}", "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": hashlib.sha256(p).hexdigest(), "image_sha256": item["image_sha256"]}


# ------------------------------------------------------------------ our trials (family resolution + primary values)

def our_trials(slug):
    """Our served primary trials, each with its identity tokens and its PRIMARY value + span (the verification side)."""
    # the verification side is OUR extraction of the trial's own report, as this branch builds it (in memory, fixes 3-4
    # applied): the served semaglutide-weight rows are CT.gov observed means, the quantity fix 3 showed is not the
    # trial's reported result, so the served page is not the primary reference for them
    import k_gap_counterfactual as cfm
    rev = cfm.build(slug)
    prim = next((o for o in rev["outcomes"] if o.get("primary")), {})
    T = _j(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"))
    acr = {}
    for r in T["trials"]:
        if r["slug"] == slug:
            for p in r["pmids"]:
                for v in (r.get("study") or {}).values():
                    if (v or {}).get("acronym"):
                        acr.setdefault(p, set()).add(v["acronym"])
    import k_gap_result_agreement as ra
    out = []
    for t in prim.get("trials", []):
        pid = str(t.get("id", "")).replace("PMID ", "")
        fa = ra.first_author_year(pid) if pid.isdigit() else None
        prim_val = None
        if t.get("effect") is not None and t.get("ci_low") is not None:
            prim_val = {"measure": (t.get("scale") or "").upper(), "effect": str(t["effect"]), "lower": str(t["ci_low"]),
                        "upper": str(t["ci_high"]), "source": f"our branch extraction {t.get('id')} ({t.get('provenance')})",
                        "span": str(t.get("source") or "")}
        elif t.get("ai") is not None:
            prim_val = {"measure": "RR", "events_t": t["ai"], "n_t": t["n1i"], "events_c": t["ci"], "n_c": t["n2i"],
                        "source": f"our branch extraction {t.get('id')} ({t.get('provenance')})", "span": str(t.get("source") or "")}
        out.append({"id": t.get("id"), "pmid": pid, "label": str(t.get("label") or ""), "acronyms": sorted(acr.get(pid, [])),
                    "author_year": fa, "primary": prim_val})
    # trials we do NOT serve are families too (the tier exists for them): the topic's comparator-resolved k-gap rows,
    # identified by acronym or first author + year. No primary value of ours -> their rows wait in the queue.
    have = {t["pmid"] for t in out}
    for r in T["trials"]:
        if r["slug"] != slug or r["drug"] == "OTHER_AGENT" or not r["pmids"] or r["status"] == "UNRESOLVED":
            continue
        pid = r["pmids"][0]
        if pid in have:
            continue
        have.add(pid)
        out.append({"id": f"PMID {pid}", "pmid": pid, "label": r["label"], "acronyms": sorted(acr.get(pid, [])),
                    "author_year": ra.first_author_year(pid), "primary": None})
    return out


def family_of_factory(ours):
    toks = lambda x: re.findall(r"[a-z0-9]+", k_gap.fold_dashes(str(x or "")).lower())   # noqa: E731

    def family_of(row):
        lt = toks(row.trial_label)
        hits = []
        for t in ours:
            names = [toks(a) for a in t["acronyms"]] + ([toks(t["label"])] if t["label"] and not t["label"].isdigit() else [])
            if any(n and lt[:len(n)] == n for n in names):
                hits.append(t)
            elif t["author_year"] and t["author_year"][0] in lt and t["author_year"][1] in lt:
                hits.append(t)
        return hits[0]["id"] if len(hits) == 1 else None
    return family_of


def spec_of(slug):
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    po = cfg.get("primary_outcome") or {}
    c = _j(os.path.join(ROOT, "cache", slug, "comparators.json"))[0]
    kw = list(po.get("keywords") or []) + [str(x) for x in list((c.get("outcome_endpoints") or {}).keys()) +
                                           list((c.get("outcome_endpoints") or {}).values())] + [po.get("name") or ""]
    est = (po.get("estimand") or "").upper()
    est = {"HAZARD RATIO": "HR", "RISK RATIO": "RR", "ODDS RATIO": "OR", "MEAN DIFFERENCE": "MD"}.get(est, est)
    return {"estimand": est, "keywords": [k for k in kw if k], "components": [], "timepoint": None}


# ------------------------------------------------------------------ driver

def build(slug, run, runs):
    metas, comp = metas_for(slug, offline=not run)
    items, skipped = [], {}
    for pmid in metas:
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
    spec = spec_of(slug)
    ours = our_trials(slug)
    fam = family_of_factory(ours)
    rows, metas_out = [], {}
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


def main(argv):
    run = "--run" in argv
    slugs = [a for a in argv if not a.startswith("--")] or list(QUERY)
    rp = os.path.join(OUTD, "runs.json")
    runs = _j(rp) if os.path.exists(rp) else {}
    for s in slugs:
        o = build(s, run, runs)
        _save(rp, runs)
        print(s, "metas", len(o["metas_considered"]), "usable", sum(1 for v in o["metas"].values() if v.get("usable")),
              "tally", o["tally"], "g1_countable", len(o["g1_countable_vs_comparator"]), "skipped", o["skipped"], flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
