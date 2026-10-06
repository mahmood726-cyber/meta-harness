"""COUNTERFACTUAL k: rebuild a topic's review core IN MEMORY from its pinned cache, optionally with extra records
appended, and report the primary pool. Writes nothing to cache/ or docs/.

Purpose: measure an acquisition adapter's conversion (identified -> admitted) topic by topic BEFORE any corpus-moving
pin. The added records go through the unchanged screen -> extract -> admission gate; nothing is admitted by this
script. A baseline run (no extra records) must reproduce the served k, or the counterfactual is not comparable and
the topic is refused.

    python scripts/k_gap_counterfactual.py --baseline [SLUG ...]
    python scripts/k_gap_counterfactual.py --members  [SLUG ...]   # + comparator members the k-gap table found
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "outputs", "k_gap")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


_VALS = ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i", "mean1", "sd1", "mean2", "sd2")


def _values(prim):
    """Every number the served primary shows: the pooled estimate/CI and each trial's effect or arm counts.
    Identity equality alone cannot see a changed VALUE (a guard that swaps which candidate a trial uses)."""
    res = prim.get("result") or {}
    return {"pool": [res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")],
            "trials": {t.get("id"): [t.get(k) for k in _VALS] for t in prim.get("trials", [])}}


def served_primary(slug):
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    prim = next((o for o in rev["outcomes"] if o.get("primary")), {})
    return {"k": (prim.get("result") or {}).get("k"), "trials": sorted(t.get("id") for t in prim.get("trials", [])),
            "values": _values(prim)}


def core_primary(core):
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    res = prim.get("result") or {}
    # A k is only a gain when the pool it sits in is VALID. Admitting one OR into an RR pool (colchicine-postop-af,
    # COCS from its full text) raised k 3->4 and SUPPRESSED the pooled effect entirely (INCOMPATIBLE estimands).
    valid = bool(res.get("k")) and not res.get("suppressed_incompatible") and res.get("estimate") is not None
    return {"k": res.get("k"), "valid_pool": valid, "k_valid": res.get("k") if valid else 0, "values": _values(prim),
            "scale": res.get("scale"), "estimate": res.get("estimate"),
            "trials": sorted(t.get("id") for t in prim.get("trials", [])),
            "declared_absent": sorted(d.get("id") for d in prim.get("declared_absent_trials", []))}


def funnel(core, pmids, recs=None, topic_records=None):
    """Where each added PMID ended: screen decision + rule id, then (if included) pooled / declared-absent reason.

    A seeded report that _dedup collapsed onto ANOTHER report of the same NCT did enter screening, as that trial:
    it is SCREENED_VIA_OTHER_REPORT (with the report that carried it), not NOT_IN_SCREEN. Counting PMIDs rather
    than trials reported 98 'never screened' of 180 when 94 were extra reports of trials that were screened."""
    scr = {r["id"]: r for r in core["screening"]["records"]}
    # screening records carry no nct: map each screened id to its NCT from the records themselves (the seeded ones
    # plus the topic's pinned ones), falling back to an NCT-keyed trial family
    nct_of = {r["id"]: r.get("nct") for r in (recs or []) + list(topic_records or []) if r.get("nct")}
    screened_by_nct = {}
    for r in core["screening"]["records"]:
        n = nct_of.get(r["id"]) or (r.get("trial_family_id") if str(r.get("trial_family_id") or "").startswith("NCT") else None)
        if n:
            screened_by_nct.setdefault(n, r["id"])
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    pooled = {str(t.get("id", "")).replace("PMID ", "") for t in prim.get("trials", [])}
    absent = {str(d.get("id", "")).replace("PMID ", ""): d.get("reason_code") for d in prim.get("declared_absent_trials", [])}
    out = {}
    for p in pmids:
        r = scr.get(p)
        if r is None and nct_of.get(p) and screened_by_nct.get(nct_of[p]):
            via = scr[screened_by_nct[nct_of[p]]]
            out[p] = {"stage": "SCREENED_VIA_OTHER_REPORT", "via": via["id"], "nct": nct_of[p],
                      "via_decision": via["decision"], "via_rule_id": via.get("rule_id")}
        elif r is None:
            out[p] = {"stage": "NOT_IN_SCREEN"}
        elif r["decision"] != "include":
            out[p] = {"stage": "SCREENED_OUT", "rule_id": r.get("rule_id"), "reason": (r.get("reason") or "")[:140]}
        elif p in pooled:
            out[p] = {"stage": "POOLED"}
        elif p in absent:
            out[p] = {"stage": "DECLARED_ABSENT", "reason_code": absent[p]}
        else:
            out[p] = {"stage": "INCLUDED_NOT_IN_PRIMARY", "family": r.get("trial_family_id")}
    return out


FT_DIR = os.path.join(OUT, "_ft")          # bodies (gitignored); FT_INDEX (committed) holds sha256 + bytes


def committed_open_fulltext(pmid, idx=None):
    """The COMMITTED held copy of an OPEN (CC) full text -- cache/<slug>/ft_<pmid>.txt -- for a clone without the
    gitignored _ft cache, returned ONLY when its bytes' sha256 equals the one fulltext_index.json recorded and the copy
    is marked open (copy_licence CC); else None. A non-open body is never committed, so it is never found here."""
    import glob
    import hashlib
    if idx is None:
        ip = os.path.join(OUT, "fulltext_index.json")
        idx = _j(ip) if os.path.exists(ip) else {}
    e = idx.get(str(pmid)) or {}
    if e.get("copy_licence") != "CC" or not e.get("sha256"):
        return None
    for fp in sorted(glob.glob(os.path.join(ROOT, "cache", "*", f"ft_{pmid}.txt"))):
        b = open(fp, "rb").read()
        if hashlib.sha256(b).hexdigest() == e["sha256"]:
            return b.decode("utf-8")
    return None


def pmc_fulltext_cached(pmid, offline=False):
    """PMC OA JATS body + structured tables + supplements for one PMID, via the harness's own fetch._pmc_fulltext
    (so the text is exactly what the pipeline would hold). Cached by PMID; '' when PMC holds no OA text."""
    # harness.fetch._pmc_fulltext returns '' on ANY exception, a rate limit (HTTP 429) included, and this wrapper used to
    # cache that '' for ever: 121 of 160 cached full texts were empty and 'no OA full text' could not be told from 'NCBI
    # said slow down'. Now: the PMCID is resolved here (paced, retried) and NO_PMCID is recorded only when PMC's own ID
    # converter says there is none; an empty body for a PMCID that exists is FETCH_EMPTY and is NOT cached (retried).
    import hashlib
    import time
    os.makedirs(FT_DIR, exist_ok=True)
    fp = os.path.join(FT_DIR, pmid + ".txt")
    idx_p = os.path.join(OUT, "fulltext_index.json")
    idx = _j(idx_p) if os.path.exists(idx_p) else {}
    if os.path.exists(fp) and os.path.getsize(fp) > 0:
        return open(fp, encoding="utf-8").read()
    held = committed_open_fulltext(pmid, idx)
    if held is not None:
        return held
    if (idx.get(pmid) or {}).get("state") in ("NO_PMCID", "PUBLISHER_DISALLOWS_XML") or offline:
        return ""
    from harness import fetch, http
    pmcid = None
    for attempt in range(4):
        try:
            time.sleep(0.4 + attempt * 2)                  # NCBI: <= 3 requests/s without a key
            d = http.get_json("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/",
                              {"ids": pmid, "format": "json", "tool": "meta-harness", "email": "meta-harness@example.org"},
                              tries=1)
            pmcid = ((d.get("records") or [{}])[0]).get("pmcid") or ""
            break
        except Exception:  # noqa: BLE001 - a failed lookup is retried, never recorded as 'no PMCID'
            pmcid = None
    if pmcid is None:
        idx[pmid] = {"state": "IDCONV_FAILED", "note": "not cached; retried on the next run"}
        txt = ""
    elif pmcid == "":
        idx[pmid] = {"state": "NO_PMCID", "source": "PMC idconv"}
        txt = ""
    else:
        time.sleep(0.4)
        txt = fetch._pmc_fulltext(pmid, with_supplements=True)
        if txt:
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(txt)
            idx[pmid] = {"state": "HELD", "pmcid": pmcid, "bytes": len(txt.encode("utf-8")),
                         "sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                         "source": "harness.fetch._pmc_fulltext(with_supplements=True)"}
        elif fetch.LAST_PMC_STATE.get(pmid) == "PUBLISHER_DISALLOWS_XML":
            idx[pmid] = {"state": "PUBLISHER_DISALLOWS_XML", "pmcid": pmcid,
                         "note": "PMC efetch serves front matter only: 'The publisher of this article does not allow "
                                 "downloading of the full text in XML form.' Not an open machine-readable source"}
        else:
            idx[pmid] = {"state": "FETCH_EMPTY", "pmcid": pmcid,
                         "note": "PMCID exists but harness.fetch._pmc_fulltext returned '' (it swallows errors); not cached"}
    if os.path.exists(fp) and os.path.getsize(fp) == 0:
        os.remove(fp)
    # write ONLY this PMID's entry into the index as it is NOW (another writer may have added entries during the
    # network calls), and keep the copy's recorded licence (copy_*, harness.copy_licence) -- replacing the whole entry
    # dropped EFFECT-HF's CC mark (5 Oct)
    new = idx[pmid]
    idx = _j(idx_p) if os.path.exists(idx_p) else {}
    idx[pmid] = {**{k: v for k, v in (idx.get(pmid) or {}).items() if k.startswith("copy_")}, **new}
    with open(idx_p, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, indent=1, sort_keys=True)
    return txt


CG_DIR = os.path.join(OUT, "_ctgov")       # bodies (gitignored); CG_INDEX (committed) holds sha256 + bytes


def ctgov_results_cached(nct, offline=False):
    """CT.gov API v2 posted outcome measures for one NCT via the harness's own fetch._ctgov_results (so the object
    is exactly what the pipeline's structured-results rung would hold). Cached; None when nothing is posted."""
    import hashlib
    os.makedirs(CG_DIR, exist_ok=True)
    fp = os.path.join(CG_DIR, nct + ".json")
    if os.path.exists(fp):
        return _j(fp)
    if offline:
        return None
    from harness import fetch
    oms = fetch._ctgov_results(nct)
    body = json.dumps(oms, sort_keys=True).encode("utf-8")
    with open(fp, "wb") as fh:
        fh.write(body)
    idx_p = os.path.join(OUT, "ctgov_index.json")
    idx = _j(idx_p) if os.path.exists(idx_p) else {}
    idx[nct] = {"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "posted": oms is not None,
                "source": "harness.fetch._ctgov_results (CT.gov API v2 resultsSection.outcomeMeasuresModule)"}
    with open(idx_p, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, indent=1, sort_keys=True)
    return oms


def build(slug, extra_records=None, extra_fulltext=None, extra_ctgov=None):
    from harness.pipeline import build_review_core
    from harness.registration import protocol_sha
    config = _j(os.path.join(ROOT, "topics", slug + ".json"))
    records = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    records = copy.deepcopy(records)
    if extra_records:
        have = {r.get("id") for r in records["records"]}
        records["records"] += [r for r in extra_records if r.get("id") not in have]
    if extra_ctgov:
        cg = dict(records.get("ctgov_results") or {})
        for k, v in extra_ctgov.items():
            cg.setdefault(k, v)          # never replace results the pinned cache already holds
        records["ctgov_results"] = cg
    if extra_fulltext:
        ft = dict(records.get("fulltext_by_pmid") or {})
        for k, v in extra_fulltext.items():
            ft.setdefault(k, v)          # never replace full text the pinned cache already holds
        records["fulltext_by_pmid"] = ft
    return build_review_core(slug, config, records, protocol_sha(slug))


def all_with_screen_hypothesis(slug):
    """Every adapter PLUS the screening hypothesis (the comparator trials both recorded readers judge eligible are
    flipped to include, in memory). Acquisition targets are taken from the HYPOTHESIS core's declared-absent list,
    so a flipped record gets its full text / registry results too. Returns (base_core, cf_core, details)."""
    from harness import fetch, fulltext as _ftm
    from harness import pipeline as _pl
    from kgap import k_gap as _kg
    sj = _j(os.path.join(OUT, "screen_join.json"))
    flip = {p for r in sj["rows"] if r["slug"] == slug and r["verdict"] == "READER_DISAGREES_WITH_EXCLUSION"
            for p in r["pmids"]}
    orig = _pl.screen.run

    def _hyp(recs, cfg, _orig=orig, _flip=flip):
        out = _orig(recs, cfg)
        for d in out["decisions"]:
            if str(d.get("id")) in _flip and d.get("decision") != "include":
                d.update({"decision": "include", "rule_id": "HYPOTHESIS_ADJUDICATED_ELIGIBLE",
                          "reason": "k-gap counterfactual: two recorded readers judged eligible (not a decision)"})
        return out
    base_core = build(slug)
    rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    pm, _ = member_pmids(slug)
    mrec_p = os.path.join(OUT, "member_records.json")
    mrec = _j(mrec_p) if os.path.exists(mrec_p) else {}
    recs = [mrec[p] for p in pm if p in mrec] + (fetch._efetch([p for p in pm if p not in mrec]) if
                                                 [p for p in pm if p not in mrec] else [])
    _pl.screen.run = _hyp
    try:
        hyp_core = build(slug, extra_records=recs)
        prim = next((o for o in hyp_core["outcomes"] if o.get("primary")), {})
        held_ft = set(rj.get("fulltext_by_pmid") or {})
        ft_t = sorted({str(d.get("id", "")).replace("PMID ", "") for d in prim.get("declared_absent_trials", [])
                       if str(d.get("id", "")).startswith("PMID ")} - held_ft)
        doi_of = {r.get("id"): (r.get("doi") or "").strip() for r in list(rj.get("records", [])) + recs}
        fts, n_upw = {}, 0
        for p in ft_t:
            t = pmc_fulltext_cached(p)
            if t:
                fts[p] = t
            elif doi_of.get(p):
                u = _kg.unpaywall_text(doi_of[p], os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"))
                if u.get("text"):
                    fts[p] = _ftm.UNSTRUCTURED_MARKER + "\n" + u["text"]
                    n_upw += 1
        recnct = {r.get("id"): r.get("nct") for r in list(rj.get("records", [])) + recs}
        cg_t = set()
        for d in prim.get("declared_absent_trials", []):
            for n in (d.get("trial_family_id"), recnct.get(str(d.get("id", "")).replace("PMID ", "")), d.get("id")):
                if n and str(n).startswith("NCT"):
                    cg_t.add(str(n))
        cgs = {n: o for n in sorted(cg_t - set(rj.get("ctgov_results") or {})) for o in [ctgov_results_cached(n)] if o}
        cf_core = build(slug, extra_records=recs, extra_fulltext=fts, extra_ctgov=cgs)
    finally:
        _pl.screen.run = orig
    return base_core, cf_core, {"flipped": len(flip), "members_added": len(recs), "fulltext_added": len(fts) - n_upw,
                                "unpaywall_added": n_upw, "ctgov_added": len(cgs),
                                "flip_funnel": funnel(cf_core, sorted(flip))}


def held_open_sources(slug, base_core, fetch_missing=False):
    """Every OPEN primary source this lane already holds for a topic, no new network unless fetch_missing:
      records    the comparator's member trials' PubMed records (member_records.json; efetch the rest if fetch_missing)
      full text  PMC OA (_ft cache), else the Unpaywall OA copy typed UNSTRUCTURED, for each declared-absent PMID
      registry   posted CT.gov results (_ctgov cache) for each declared-absent trial's NCT
    Returns (records, fulltext_by_pmid, ctgov_by_nct, n_unpaywall)."""
    prim = next((o for o in base_core["outcomes"] if o.get("primary")), {})
    rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
    pm, _nct_only = member_pmids(slug)
    mrec_p = os.path.join(OUT, "member_records.json")
    mrec = _j(mrec_p) if os.path.exists(mrec_p) else {}
    recs = [mrec[p] for p in pm if p in mrec]
    missing = [p for p in pm if p not in mrec]
    if missing and fetch_missing:
        from harness import fetch
        recs += fetch._efetch(missing)
    held_ft = set(rj.get("fulltext_by_pmid") or {})
    # texts are offered for the base build's declared-absent trials AND for the seeded comparator members: a member
    # enters only in the final build, so it is never on the base declared-absent list (EMPEROR-Preserved, PMID 34449189,
    # was offered no text at all)
    ft_t = sorted(({str(d.get("id", "")).replace("PMID ", "") for d in prim.get("declared_absent_trials", [])
                    if str(d.get("id", "")).startswith("PMID ")} | {str(r.get("id")) for r in recs}) - held_ft)
    fts = {p: t for p in ft_t for t in [pmc_fulltext_cached(p, offline=True)] if t}
    # the topic's own held texts (cache/<slug>/ft_<pmid>.txt) were never offered by this build
    for p in ft_t:
        cp = os.path.join(ROOT, "cache", slug, f"ft_{p}.txt")
        if p not in fts and os.path.exists(cp) and os.path.getsize(cp) > 0:
            fts[p] = open(cp, encoding="utf-8", errors="replace").read()
    from kgap import k_gap as _kg
    from harness import fulltext as _ftm
    # a trial's DOI from the topic's records OR the held member records: EMPEROR-Preserved's Unpaywall copy was never
    # offered to the pool because its DOI is only in member_records.json
    doi_of = {str(p): (r.get("doi") or "").strip() for p, r in mrec.items()}
    doi_of.update({r.get("id"): (r.get("doi") or "").strip() for r in rj.get("records", []) if (r.get("doi") or "").strip()})
    n_upw = 0
    for p in ft_t:
        if p in fts or not doi_of.get(p):
            continue
        u = _kg.unpaywall_text(doi_of[p], os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"),
                               offline=True)
        if u.get("text"):
            fts[p] = _ftm.UNSTRUCTURED_MARKER + "\n" + u["text"]
            n_upw += 1
    recnct = {r.get("id"): r.get("nct") for r in rj.get("records", [])}
    # seeded members' registrations too: their posted results were never read (a member is absent from the base build)
    cg_t = {str(r.get("nct")) for r in recs if str(r.get("nct") or "").startswith("NCT")}
    for d in prim.get("declared_absent_trials", []):
        for n in (d.get("trial_family_id"), recnct.get(str(d.get("id", "")).replace("PMID ", "")), d.get("id")):
            if n and str(n).startswith("NCT"):
                cg_t.add(str(n))
    cgs = {n: o for n in sorted(cg_t - set(rj.get("ctgov_results") or {}))
           for o in [ctgov_results_cached(n, offline=True)] if o}
    return recs, fts, cgs, n_upw


def build_with_held_sources(slug, base_core=None, fetch_missing=False):
    """The branch build of a topic WITH every held open primary source injected (the --all counterfactual): what this
    harness pools given everything it has acquired. Returns (core, (records, fulltext, ctgov, n_unpaywall))."""
    base_core = base_core or build(slug)
    src = held_open_sources(slug, base_core, fetch_missing=fetch_missing)
    return build(slug, extra_records=src[0], extra_fulltext=src[1], extra_ctgov=src[2]), src


def member_pmids(slug):
    """Comparator members the k-gap table marks IDENTIFICATION (never in our corpus), confirmed-set only.

    The REPORT the comparator cited is added, not every PMID registered to the trial's NCT: adding all NCT-linked
    reports let dedup keep a design paper over the results paper (DECLARE-TIMI 58 -> X1 'not an RCT' on
    PMID 29693360), which measures our dedup, not the adapter. A member with no cited PMID (resolved by acronym or
    NCT only) contributes its NCT-linked PMIDs, and is counted apart as `nct_only`."""
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    cited, nct_only = [], []
    for r in t["trials"]:
        if (r["slug"] == slug and r["unit_source"] != "REFERENCE_SEED" and r["gap_class"] == "IDENTIFICATION"
                and r["drug"] != "OTHER_AGENT"):
            if r.get("cited_pmids") and set(r["cited_pmids"]) & set(r["pmids"]):
                cited += r["cited_pmids"]
            elif r.get("cited_pmids") and r["pmids"]:
                # the cited PMID is NOT the resolved report: the table's xrefs were distrusted (omega-3 is numbered
                # one off from its reference list) and the row was resolved by author+year. Seeding cited_pmids
                # added the REJECTED link -- Eritsland 1996 was seeded as DART. Seed the resolved report.
                cited += r["pmids"]
            else:
                nct_only += r["pmids"]
    return sorted(set(cited) | set(nct_only)), sorted(set(nct_only))


def main(argv):
    mode = argv[0]
    slugs = argv[1:] or sorted(x["slug"] for x in _j(os.path.join(OUT, "k_gap_table.json"))["topics"])
    res = {}
    for slug in slugs:
        t0 = time.time()
        s = served_primary(slug)
        try:
            if mode == "--all-hyp":
                b, c, det = all_with_screen_hypothesis(slug)
                base, cf = core_primary(b), core_primary(c)
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "baseline_k_valid": base["k_valid"],
                             "counterfactual_k": cf["k"], "counterfactual_k_valid": cf["k_valid"],
                             "counterfactual_scale": cf["scale"], **det,
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "secs": round(time.time() - t0, 1)}
            elif mode == "--screen-hypothesis":
                # WHAT WOULD ADJUDICATION BE WORTH? For the comparator trials we exclude where the repo's two recorded
                # readers both say ELIGIBLE (outputs/k_gap/screen_join.json), flip ONLY those decisions in memory and
                # rebuild. Hypothetical by construction (rule id says so); the screener is not changed.
                from harness import pipeline as _pl
                sj = _j(os.path.join(OUT, "screen_join.json"))
                flip = {p for r in sj["rows"] if r["slug"] == slug and r["verdict"] == "READER_DISAGREES_WITH_EXCLUSION"
                        for p in r["pmids"]}
                base = core_primary(build(slug))
                if not flip:
                    res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "flipped": 0}
                    print(slug, res[slug], flush=True)
                    continue
                orig = _pl.screen.run

                def _hyp(recs, cfg, _orig=orig, _flip=flip):
                    out = _orig(recs, cfg)
                    for d in out["decisions"]:
                        if str(d.get("id")) in _flip and d.get("decision") != "include":
                            d.update({"decision": "include", "rule_id": "HYPOTHESIS_ADJUDICATED_ELIGIBLE",
                                      "reason": "k-gap counterfactual: two recorded readers judged eligible (not a decision)"})
                    return out
                _pl.screen.run = _hyp
                try:
                    cfc = build(slug)
                finally:
                    _pl.screen.run = orig
                cf = core_primary(cfc)
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "baseline_k_valid": base["k_valid"],
                             "flipped": len(flip), "counterfactual_k": cf["k"], "counterfactual_k_valid": cf["k_valid"],
                             "counterfactual_scale": cf["scale"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "funnel": funnel(cfc, sorted(flip)), "secs": round(time.time() - t0, 1)}
            elif mode == "--unpaywall":
                from kgap import k_gap
                base_core = build(slug)
                base = core_primary(base_core)
                prim = next((o for o in base_core["outcomes"] if o.get("primary")), {})
                rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
                held = set(rj.get("fulltext_by_pmid") or {})
                doi_of = {r.get("id"): (r.get("doi") or "").strip() for r in rj.get("records", [])}
                targets = sorted({str(d.get("id", "")).replace("PMID ", "") for d in prim.get("declared_absent_trials", [])
                                  if str(d.get("id", "")).startswith("PMID ")} - held)
                got, tried = {}, 0
                for p in targets:
                    if pmc_fulltext_cached(p, offline=True):
                        continue                   # PMC OA is adapter 2's; this adapter is for the rest
                    doi = doi_of.get(p)
                    if not doi:
                        continue
                    tried += 1
                    u = k_gap.unpaywall_text(doi, os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"))
                    if u.get("text"):
                        from harness import fulltext as _ftm
                        got[p] = _ftm.UNSTRUCTURED_MARKER + "\n" + u["text"]   # typed: no table delimiters
                cfc = build(slug, extra_fulltext=got)
                cf = core_primary(cfc)
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "declared_absent_pmids": len(targets),
                             "unpaywall_tried": tried, "unpaywall_text_found": len(got), "counterfactual_k": cf["k"],
                             "baseline_k_valid": base["k_valid"], "counterfactual_k_valid": cf["k_valid"],
                             "counterfactual_scale": cf["scale"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "secs": round(time.time() - t0, 1)}
            elif mode == "--all":
                # every adapter at once, from the caches the single-adapter runs filled (no new network): the
                # combined number is MEASURED, not summed -- two routes can admit the same trial.
                base_core = build(slug)
                base = core_primary(base_core)
                cfc, (recs, fts, cgs, n_upw) = build_with_held_sources(slug, base_core=base_core, fetch_missing=True)
                cf = core_primary(cfc)
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "baseline_k_valid": base["k_valid"],
                             "counterfactual_k": cf["k"], "counterfactual_k_valid": cf["k_valid"],
                             "counterfactual_scale": cf["scale"], "members_added": len(recs),
                             "fulltext_added": len(fts) - n_upw, "unpaywall_added": n_upw, "ctgov_added": len(cgs),
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "secs": round(time.time() - t0, 1)}
            elif mode == "--ctgov":
                base_core = build(slug)
                base = core_primary(base_core)
                prim = next((o for o in base_core["outcomes"] if o.get("primary")), {})
                rj = _j(os.path.join(ROOT, "cache", slug, "records.json"))
                held = set(rj.get("ctgov_results") or {})
                recnct = {r.get("id"): r.get("nct") for r in rj.get("records", [])}
                targets = set()
                for d in prim.get("declared_absent_trials", []):
                    for n in (d.get("trial_family_id"), recnct.get(str(d.get("id", "")).replace("PMID ", "")), d.get("id")):
                        if n and str(n).startswith("NCT"):
                            targets.add(str(n))
                targets = sorted(targets - held)
                got = {n: o for n in targets for o in [ctgov_results_cached(n)] if o}
                cfc = build(slug, extra_ctgov=got)
                cf = core_primary(cfc)
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "declared_absent_ncts": len(targets),
                             "ctgov_results_found": len(got), "counterfactual_k": cf["k"],
                             "baseline_k_valid": base["k_valid"], "counterfactual_k_valid": cf["k_valid"],
                             "counterfactual_scale": cf["scale"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "secs": round(time.time() - t0, 1)}
            elif mode == "--fulltext":
                base_core = build(slug)
                base = core_primary(base_core)
                prim = next((o for o in base_core["outcomes"] if o.get("primary")), {})
                held = set((_j(os.path.join(ROOT, "cache", slug, "records.json")).get("fulltext_by_pmid") or {}))
                targets = sorted({str(d.get("id", "")).replace("PMID ", "") for d in prim.get("declared_absent_trials", [])
                                  if str(d.get("id", "")).startswith("PMID ")} - held)
                fts = {p: pmc_fulltext_cached(p) for p in targets}
                got = {p: t for p, t in fts.items() if t}
                cfc = build(slug, extra_fulltext=got)
                cf = core_primary(cfc)
                prim_cf = next((o for o in cfc["outcomes"] if o.get("primary")), {})
                why_b = {d.get("id"): d.get("reason_code") for d in prim.get("declared_absent_trials", [])}
                why_c = {d.get("id"): d.get("reason_code") for d in prim_cf.get("declared_absent_trials", [])}
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "declared_absent_pmids": len(targets),
                             "pmc_fulltext_found": len(got), "counterfactual_k": cf["k"],
                             "baseline_k_valid": base["k_valid"], "counterfactual_k_valid": cf["k_valid"],
                             "counterfactual_scale": cf["scale"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "reason_changed": {k: [why_b.get(k), why_c.get(k)] for k in why_b
                                                if k in why_c and why_b.get(k) != why_c.get(k)},
                             "secs": round(time.time() - t0, 1)}
            elif mode == "--held-ft":
                # the topic's HELD full texts (cache/<slug>/ft_<pmid>.txt), which pool construction never reads: it
                # takes full text only from records.json#fulltext_by_pmid (captain's finding, 2026-09-30)
                import glob as _glob
                base_core = build(slug)
                base = core_primary(base_core)
                held = {}
                for fp in _glob.glob(os.path.join(ROOT, "cache", slug, "ft_*.txt")):
                    pid = os.path.basename(fp)[3:-4]
                    with open(fp, encoding="utf-8") as fh:
                        held[pid] = fh.read()
                cfc = build(slug, extra_fulltext=held) if held else base_core
                cf = core_primary(cfc)
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "held_ft": len(held),
                             "baseline_k_valid": base["k_valid"], "counterfactual_k": cf["k"],
                             "counterfactual_k_valid": cf["k_valid"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "values_changed": sorted(k for k in set(base["values"]["trials"]) & set(cf["values"]["trials"])
                                                      if base["values"]["trials"][k] != cf["values"]["trials"][k]),
                             "secs": round(time.time() - t0, 1)}
            elif mode == "--baseline":
                c = core_primary(build(slug))
                vdiff = {k: [s["values"]["trials"].get(k), c["values"]["trials"].get(k)]
                         for k in set(s["values"]["trials"]) | set(c["values"]["trials"])
                         if s["values"]["trials"].get(k) != c["values"]["trials"].get(k)}
                res[slug] = {"served_k": s["k"], "rebuilt_k": c["k"], "same_trials": s["trials"] == c["trials"],
                             "same_values": s["values"]["pool"] == c["values"]["pool"] and not vdiff,
                             "value_diff": vdiff or None,
                             "pool_diff": None if s["values"]["pool"] == c["values"]["pool"]
                             else [s["values"]["pool"], c["values"]["pool"]],
                             "secs": round(time.time() - t0, 1)}
            else:
                from harness import fetch
                pm, nct_only = member_pmids(slug)
                recs = fetch._efetch(pm) if pm else []
                base = core_primary(build(slug))
                cfc = build(slug, recs)
                cf = core_primary(cfc)
                fn = funnel(cfc, [r["id"] for r in recs], recs,
                            _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", []))
                res[slug] = {"served_k": s["k"], "baseline_k": base["k"], "members_added": len(pm),
                             "baseline_k_valid": base["k_valid"], "counterfactual_k_valid": cf["k_valid"],
                             "nct_only_pmids": len(nct_only),
                             "records_fetched": len(recs), "counterfactual_k": cf["k"],
                             "admitted": sorted(set(cf["trials"]) - set(base["trials"])),
                             "lost": sorted(set(base["trials"]) - set(cf["trials"])),
                             "funnel": fn,
                             "secs": round(time.time() - t0, 1)}
        except Exception as exc:  # noqa: BLE001
            res[slug] = {"error": f"{type(exc).__name__}: {exc}"[:300]}
        print(slug, res[slug], flush=True)
    return res


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    r = main(sys.argv[1:])
    name = {"--baseline": "counterfactual_baseline.json", "--members": "counterfactual_members.json",
            "--fulltext": "counterfactual_fulltext.json", "--ctgov": "counterfactual_ctgov.json",
            "--all": "counterfactual_all.json", "--held-ft": "counterfactual_held_ft.json", "--unpaywall": "counterfactual_unpaywall.json",
            "--screen-hypothesis": "counterfactual_screen_hypothesis.json",
            "--all-hyp": "counterfactual_all_screen_hypothesis.json"}[sys.argv[1]]
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, sort_keys=True)
