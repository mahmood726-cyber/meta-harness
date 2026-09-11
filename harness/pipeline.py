"""Deterministic offline pipeline: committed cache + topic config -> screen -> extract
(primary + secondary + harms) -> synth -> review core. No network, no hand-typed numbers;
a fresh clone reproduces byte-for-byte.
"""
from __future__ import annotations
import json
import os

from . import extract, screen, scope, verify, locate
from .ctgov_results import extract_ctgov
from .synth import Study, pool

METHOD = ("Random-effects inverse-variance on the log ratio (log RR/OR/HR as configured "
          "for the outcome); Paule-Mandel tau^2; "
          "HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); "
          "prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1.")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_text(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")


_NONPRIMARY = ("letter", "comment", "editorial", "erratum", "news", "biography")


def _primacy(r):
    """How primary a PubMed record is as a trial report. A Letter/Comment/Erratum that shares
    a trial's NCT must NOT displace the trial's own RCT report during dedup — that dropped the
    canonical SMART RCT (PMID 29485925) in favour of a Comment (29768150) and lost the trial."""
    pts = [p.lower() for p in r.get("pubtypes", [])]
    if any("randomized controlled trial" in p for p in pts):
        return 3
    if any(x in p for p in pts for x in _NONPRIMARY):
        return 0
    return 2  # an ordinary journal article


def _dedup(records):
    """Drop the CT.gov twin of a PubMed record (same NCT); then collapse PubMed records that
    share an NCT to the most-primary, latest-year one: a trial's RCT report beats a
    Letter/Comment/Erratum on the same NCT, and among peers the results paper (latest year)
    supersedes an earlier design/rationale paper."""
    pubmed = list(records.get("records", []))
    by_nct = {}
    for r in pubmed:
        n = r.get("nct")
        if n:
            keep = by_nct.get(n)
            r_key = (_primacy(r), str(r.get("year") or "0"))
            keep_key = (_primacy(keep), str(keep.get("year") or "0")) if keep else None
            if keep is None or r_key > keep_key:
                by_nct[n] = r
    deduped = []
    for r in pubmed:
        n = r.get("nct")
        if n and by_nct.get(n) is not r:
            continue  # superseded duplicate of the same NCT
        deduped.append(r)
    seen_nct = {r.get("nct") for r in deduped if r.get("nct")}
    for c in records.get("ctgov", []):
        if c.get("id") not in seen_nct:
            deduped.append(c)
    return deduped


import re as _re
_ENROLL = _re.compile(r"([\d,]{2,})\s+(?:adults?|patients?|participants?|subjects?|women|men)\b", _re.I)


def _enrollment_floor(abstract):
    """~0.6x the trial's abstract-stated enrollment, used to reject a CT.gov SUBGROUP outcome
    measure from being pooled as the whole trial (see extract_ctgov min_total). Returns None
    when no enrollment count is stated (then no floor is applied)."""
    ns = []
    for m in _ENROLL.finditer(abstract or ""):
        try:
            ns.append(int(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return int(0.6 * max(ns)) if ns else None


def _rr_cs(ai, n1, ci, n2):
    if None in (ai, n1, ci, n2) or ai in (0,) or ci in (0,) or not n1 or not n2:
        return None
    return (ai / n1) / (ci / n2)


def _cross_source(ex, nct, ctgov_results, spec, interv, comp):
    """SECOND INDEPENDENT EXTRACTOR + adjudication. A trial pooled from its abstract is corroborated
    against CT.gov structured results (a different source, extracted independently) when the trial
    has both. Count-vs-count gets an agree verdict within tolerance; a gross DIRECTION FLIP is a
    flagged discrepancy (not auto-refused, because a difference can be a legitimate timepoint/
    definition mismatch — it is surfaced for the reader and for hand-investigation). The cross-source
    number NEVER replaces the pooled number; it only corroborates it."""
    oms = ctgov_results.get(nct)
    if not oms:
        return None
    cg = extract_ctgov(oms, spec["keywords"], interv, comp)
    if not cg:
        return None
    c_rr = _rr_cs(cg.get("ai"), cg.get("n1i"), cg.get("ci"), cg.get("n2i"))
    a_rr = _rr_cs(ex.get("ai"), ex.get("n1i"), ex.get("ci"), ex.get("n2i"))
    out = {"ctgov_rr": round(c_rr, 3) if c_rr else None, "ctgov_source": cg.get("source", "")}
    if a_rr and c_rr:
        import math
        ratio = a_rr / c_rr
        flip = (a_rr - 1) * (c_rr - 1) < 0 and abs(math.log(ratio)) > 0.2
        gross = ratio > 1.5 or ratio < (1 / 1.5)
        out["abstract_rr"] = round(a_rr, 3)
        out["agree"] = not (flip and gross)
        out["note"] = ("independently corroborated by CT.gov structured results"
                       if out["agree"] else
                       "DISCREPANCY vs CT.gov structured results (direction flip) — investigate before trusting")
    else:
        out["agree"] = None
        out["note"] = ("CT.gov structured result present; measures are not both count-derived "
                       "(abstract effect vs registry counts), shown for corroboration only")
    return out


def _pool_result(studies, scale="RR"):
    r = pool(studies, scale=scale)
    res = {"k": r.k, "estimate": round(r.estimate, 4), "scale": r.scale,
           "ci_low": round(r.ci_low, 4), "ci_high": round(r.ci_high, 4), "tau2": round(r.tau2, 5)}
    if r.k > 1:
        res["pi_low"], res["pi_high"] = round(r.pi_low, 4), round(r.pi_high, 4)
        if r.tau2 == 0:
            res["pi_note"] = ("tau^2 estimated as 0, so the prediction interval coincides with the "
                              "confidence interval (no between-study heterogeneity detected).")
    else:
        res["pi_note"] = "prediction interval undefined for k=1"
    return res


def _load_ghost(slug):
    """Committed ghost-protocol / registry-landscape census (cache/<slug>/ghost.json) from AACT."""
    p = os.path.join(ROOT, "cache", slug, "ghost.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_integrity(slug):
    """Committed trial-integrity (retraction / expression-of-concern) snapshot for this topic's
    pooled trials (cache/<slug>/integrity.json), produced by scripts/integrity_check.py. Rendered on
    the page and enforced by the gate. Absent => not yet checked."""
    p = os.path.join(ROOT, "cache", slug, "integrity.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_recall(slug):
    """Committed registry-first RECALL snapshot for this topic (cache/<slug>/recall.json), if
    measured. Recall is network-derived (registry enumeration), so — like the cache and the
    outcome-identity judgments — it is a COMMITTED INPUT the page renders, regenerable by re-running
    scripts/recall.py against the committed registry_first query. Absent => not yet measured."""
    p = os.path.join(ROOT, "cache", slug, "recall.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_outcome_judgments(slug):
    """Committed outcome-identity judgments (the model-as-source cache). Present only for topics
    that opted into the gate and had judgments produced by scripts/outcome_judgments.py. Absent =>
    None => extract_ctgov keeps its deterministic substring selection (backward-compatible)."""
    p = os.path.join(ROOT, "cache", slug, "outcome_judgments.json")
    if not os.path.exists(p):
        return None
    data = json.load(open(p, encoding="utf-8"))
    # stored as {"judgments": {title: {...}}, "model": ..., "produced_utc": ...}
    return data.get("judgments", data)


def _load_rob2(slug):
    """Committed per-trial RoB2 assessment (cache/<slug>/rob2.json) from AACT + registry-vs-pooled."""
    import os, json
    fp = os.path.join(ROOT, "cache", slug, "rob2.json")
    if not os.path.exists(fp):
        return None
    try:
        return json.load(open(fp, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_verified_arms(slug):
    """Committed hand-verified structured arm-level counts (cache/<slug>/verified_arms.json):
    {pmid: {outcome, ai, n1i, ci, n2i, source}}. The bottom of the source hierarchy — a number a
    human verified against a structured source (AACT) and the published rate, for a trial whose
    abstract/single-NCT/full-text did not yield it. Absent => none."""
    p = os.path.join(ROOT, "cache", slug, "verified_arms.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _with_model_adjudication(slug, dual, decisions):
    """Attach the committed independent-model adjudication of the rule-screener disagreements
    (cache/<slug>/screen_adjudication.json) to the dual block, with the model-vs-served agreement.
    ADVISORY only — the served decision is the rule screener's; this is the genuinely-independent
    third reader (different information + method) that earns the PRISMA item-8 independence claim."""
    p = os.path.join(ROOT, "cache", slug, "screen_adjudication.json")
    if not os.path.exists(p):
        return dual
    try:
        j = json.load(open(p, encoding="utf-8")).get("judgments", {})
    except (OSError, ValueError):
        return dual
    served = {str(d["id"]): d["decision"] for d in decisions}
    n = agree = 0
    flags = []
    for pid, jr in j.items():
        if pid not in served:
            continue
        n += 1
        model_inc = jr.get("is_eligible") is True
        if model_inc == (served[pid] == "include"):
            agree += 1
        else:
            flags.append({"id": pid, "served": served[pid],
                          "model": "include" if model_inc else "exclude", "rationale": jr.get("rationale")})
    dual["model_adjudication"] = {
        "n": n, "agree_with_served": agree, "flags": flags,
        "note": "an independent capable-model reader adjudicated the rule-screener disagreements "
                "(different information + method than the two correlated rule sets). Advisory: the rule "
                "screener remains the served decision; flags are surfaced for review."}
    return dual


def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=None,
                   fulltext_by_pmid=None, outcome_judgments=None, verified_arms=None,
                   locate_judgments=None):
    ctgov_results = ctgov_results or {}
    fulltext_by_pmid = fulltext_by_pmid or {}
    trials, absent = [], []
    for d in included:
        rec = rec_by_id.get(d["id"], {})
        label = rec.get("acronym") or d.get("label") or d["id"]
        idstr = f"PMID {d['id']}" if d["id_type"] == "pmid" else d["id"]
        # SOURCE HIERARCHY: the ABSTRACT headline (the authors' primary-outcome result, unambiguous)
        # first; CT.gov structured results as the FALLBACK when the abstract yields no extractable
        # number (bare %, composite-only). CT.gov-first was tried and REJECTED: outcome-measure
        # selection is ambiguous (abbreviated OM titles) and it overrode EMPEROR's correct 361-event
        # composite with a 15-event secondary. Both are primary-source; the abstract headline is safer.
        nct = rec.get("nct") or (d["id"] if d["id_type"] == "nct" else None)
        dc = extract.declared_is_composite(spec.get("name", ""))
        ex = extract.extract_trial(rec.get("abstract", ""), spec["keywords"], interv, comp,
                                   declared_composite=dc)
        if not ex.get("absent"):
            ex["provenance"] = "abstract"
            t = {"label": label, "id": idstr, **ex}
            if nct and nct in ctgov_results:
                cs = _cross_source(ex, nct, ctgov_results, spec, interv, comp)
                if cs:
                    t["cross_source"] = cs
            trials.append(t)
            continue
        cg = (extract_ctgov(ctgov_results.get(nct), spec["keywords"], interv, comp,
                            min_total=_enrollment_floor(rec.get("abstract", "")),
                            judgments=outcome_judgments)
              if nct and nct in ctgov_results else None)
        if cg:
            cg["provenance"] = "ctgov_results"
            trials.append({"label": label, "id": idstr, **cg})
            continue
        # FULL-TEXT FALLBACK: per-arm SD / person-time / rate-ratio+CI that the abstract omits
        # often live in the PMC OA full text (Albert's azithromycin IRR 0.73). Same extractors,
        # same round-trip + refuse-on-ambiguity guards; keyword-scoped so it reads the outcome's
        # own sentences, not the whole document.
        ft = fulltext_by_pmid.get(d["id"]) if d["id_type"] == "pmid" else None
        fx = extract.extract_trial(ft, spec["keywords"], interv, comp, declared_composite=dc) if ft else None
        if fx and not fx.get("absent"):
            fx["provenance"] = "pmc_fulltext"
            trials.append({"label": label, "id": idstr, **fx})
            continue
        # BOTTOM OF THE SOURCE HIERARCHY: a committed, HAND-VERIFIED structured arm-level entry
        # (e.g. AACT counts summed across a trial's two registrations, verified against the
        # published rate). Used only when the primary report / single-NCT registry / full text do
        # NOT yield the number, and only for the matching outcome. Carries its own provenance +
        # verification, rendered on the page so a reader sees which numbers we took from where.
        va = (verified_arms or {}).get(d["id"])
        if va and va.get("outcome") == spec.get("name") and all(
                va.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
            trials.append({"label": label, "id": idstr, "ai": va["ai"], "n1i": va["n1i"],
                           "ci": va["ci"], "n2i": va["n2i"], "provenance": "aact_verified",
                           "source": va.get("source", "hand-verified structured arm-level counts")})
            continue
        absent.append({"label": label, "id": idstr, "reason": ex["reason"]})
    # LOCATE IDENTITY GATE (opt-in, model-derived): a cached judgment that a trial's located evidence
    # is NOT the target outcome forces it to declared-absent — the safeguard against the right-number/
    # wrong-endpoint class. It can only REMOVE a mis-identified number, never add one.
    if locate_judgments:
        kept = []
        for t in trials:
            pid = str(t.get("id", "")).replace("PMID ", "")
            j = locate.rejects(locate_judgments, pid, spec["name"])
            if j:
                absent.append({"label": t["label"], "id": t["id"],
                               "reason": (f"model outcome-identity gate (model-derived) — {j.get('reject_reason','')}: "
                                          + j.get("why", "")),
                               "locate_judgment": j})
            else:
                kept.append(t)
        trials = kept
    # PER-TRIAL VERIFICATION against committed source, computed at build and rendered (not assumed):
    # each pooled number's digits must be present in the committed abstract / structured source.
    for t in trials:
        pid = str(t.get("id", "")).replace("PMID ", "")
        ab = (rec_by_id.get(pid) or {}).get("abstract", "")
        t["verified"], t["verify_basis"] = verify.verify_pooled(t, ab)
    out = {"name": spec["name"], "kind": kind, "primary": bool(spec.get("primary")),
           "estimand": spec.get("estimand", "RR"), "population": spec.get("population"),
           "timepoint": spec.get("timepoint"), "method": METHOD,
           "trials": trials, "declared_absent_trials": absent}
    if trials:
        meas = (spec.get("estimand") or "RR").upper()
        meas = meas if meas in ("RR", "OR") else "RR"  # 2x2 pools as RR/OR; HR only via effect+CI
        def _meas(t):
            if t.get("e1i") is not None:
                return "IRR"
            if t.get("mean1") is not None:
                return "MD"
            return meas
        studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"),
                         n2i=t.get("n2i"), effect=t.get("effect"), ci_low=t.get("ci_low"),
                         ci_high=t.get("ci_high"),
                         e1i=t.get("e1i"), t1i=t.get("t1i"), e2i=t.get("e2i"), t2i=t.get("t2i"),
                         mean1=t.get("mean1"), sd1=t.get("sd1"), nc1=t.get("nc1"),
                         mean2=t.get("mean2"), sd2=t.get("sd2"), nc2=t.get("nc2"),
                         source=t.get("source", ""), measure=_meas(t)) for t in trials]
        # The pooled scale reflects the data actually pooled: IRR if all rate-based, MD if all
        # continuous, else the topic's ratio estimand.
        if all(t.get("e1i") is not None for t in trials):
            pooled_scale = "IRR"
        elif all(t.get("mean1") is not None for t in trials):
            pooled_scale = "MD"
        elif all(t.get("scale") for t in trials) and len({t["scale"] for t in trials}) == 1:
            # Every pooled trial reported an explicit effect on the SAME scale -> display that scale,
            # not the topic's declared estimand. This stops a rate ratio (FAIR-HF2 total HF
            # hospitalizations, scale IRR) being labelled a risk ratio just because the topic
            # declared RR. Mixed scales fall through to the declared estimand (and are a known
            # heterogeneity the label makes visible, e.g. spironolactone RR/HR).
            pooled_scale = trials[0]["scale"]
        else:
            pooled_scale = spec.get("estimand", "RR")
        out["result"] = _pool_result(studies, scale=pooled_scale)
        # HONEST MIXED-SCALE LABEL (estimand homogeneity): if the pooled trials do NOT share one
        # ratio estimand, the label must SAY so — never present a heterogeneous pool as a single
        # clean scale ("calling it an HR" when it mixed a count-RR and a Cox HR is the shipped defect
        # this kills). The pooling math is unchanged (per-study log-effects); only the displayed scale
        # becomes truthful, and scale_mixed flags it for the page and the weakness survey.
        eff = set()
        for t in trials:
            if t.get("e1i") is not None:
                eff.add("IRR")
            elif t.get("mean1") is not None:
                eff.add("MD")
            elif t.get("ai") is not None:
                eff.add(meas)
            elif t.get("scale"):
                eff.add(t["scale"])
        if len(eff) > 1:
            out["result"]["scale"] = "mixed (" + "/".join(sorted(eff)) + ")"
            out["result"]["scale_mixed"] = sorted(eff)
        if out["result"].get("k") == 1:
            # A single trial is not a random-effects meta-analysis: present it honestly as the
            # trial's own effect, and do not display tau^2 / HKSJ / prediction-interval machinery.
            out["method"] = ("Single included trial that reported this outcome — the estimate is that "
                             "trial's own effect; no random-effects pooling (tau^2, HKSJ and prediction "
                             "interval are not applicable at k=1).")
            out["result"].pop("tau2", None)
    else:
        out["result"] = {"present": False,
                         "reason": "no included trial reported this outcome with a percentage-corroborated "
                                   "count or an effect+CI in its abstract"}
    return out


def _outcome_specs(config):
    specs = [(dict(config["primary_outcome"], primary=True), "efficacy")]
    for s in config.get("secondary_outcomes", []):
        specs.append((s, "efficacy"))
    for s in config.get("harm_outcomes", []):
        specs.append((s, "harm"))
    return specs


def _source_status(slug, config, records, merged):
    """Four-state (RAN_OK / RAN_ZERO / RAN_ERROR / NOT_RUN) per search source, so a reader can see
    which adapters ran, which returned nothing, and which were not attempted for this topic. Prefers
    the status fetch actually recorded (records.source_status) and fills the rest DETERMINISTICALLY
    from committed artifacts (recall.json, fulltext_by_pmid, ctgov presence) — replay-safe, no network,
    process-metadata only (never a pooled number)."""
    committed = records.get("source_status") or {}
    ft = records.get("fulltext_by_pmid") or {}
    rc = _load_recall(slug) or {}
    has_ctgov = bool(records.get("ctgov") or records.get("ctgov_results"))
    return {
        "PubMed": committed.get("pubmed") or ("RAN_OK" if merged else "RAN_ZERO"),
        "Europe PMC (OA + metadata)": committed.get("europepmc") or ("RAN_OK" if merged else "RAN_ZERO"),
        "ClinicalTrials.gov": "RAN_OK" if has_ctgov else ("RAN_ZERO" if config.get("ctgov") else "NOT_RUN"),
        "Citation chase": committed.get("citation_chase") or ("RAN_OK" if config.get("cite_chase") else "NOT_RUN"),
        "Registry-first (AACT)": (rc.get("status") if rc else None) or ("RAN_ERROR" if config.get("registry_first") else "NOT_RUN"),
        "PMC full text": "RAN_OK" if ft else ("RAN_ZERO" if config.get("fulltext") else "NOT_RUN"),
    }


def build_review_core(slug, config, records, protocol_sha):
    merged = _dedup(records)
    scr = screen.run(merged, config)
    rec_by_id = {r["id"]: r for r in merged}
    included = [d for d in scr["decisions"] if d["decision"] == "include"]
    interv = config.get("intervention_terms", ["colchicine"])
    comp = config.get("comparator_terms", ["placebo", "control"])

    cgr = records.get("ctgov_results") or {}
    ftbp = records.get("fulltext_by_pmid") or {}
    # Outcome-identity gate is OPT-IN per topic (config.outcome_identity) AND requires a committed
    # judgments cache; absent either, judgments=None and ctgov selection is the deterministic
    # substring match. This keeps every existing topic byte-identical until it opts in.
    ojudg = _load_outcome_judgments(slug) if config.get("outcome_identity") else None
    varms = _load_verified_arms(slug)
    ljudg = locate.load(slug) if config.get("locate_gate") else None
    outcomes = [_build_outcome(spec, kind, included, rec_by_id, interv, comp, cgr, ftbp,
                               outcome_judgments=ojudg, verified_arms=varms, locate_judgments=ljudg)
                for spec, kind in _outcome_specs(config)]
    primary = outcomes[0]

    comp_rec = rec_by_id.get(config.get("comparator_pmid")) or {}
    comp_abstract = comp_rec.get("abstract", "")
    comp_full = records.get("comparator_fulltext") or ""

    reported = []
    for co in config.get("comparator_outcomes", []):
        eff = extract.comparator_effect(comp_abstract, comp_full, co["keywords"])
        if eff:
            reported.append({"outcome": co["name"], "estimate": eff["effect"], "scale": eff["scale"],
                             "ci_low": eff["ci_low"], "ci_high": eff["ci_high"]})
    theirs_k = (extract.extract_meta(comp_abstract, config["primary_outcome"]["keywords"]).get("k")
                or extract.extract_meta(comp_full, config["primary_outcome"]["keywords"]).get("k")
                or "not stated in the comparator abstract/full text")
    oa = records.get("comparator_oa") or {}
    comp_year = comp_rec.get("year")
    ours_k = primary["result"].get("k") if isinstance(primary["result"], dict) and primary["result"].get("k") else len(primary["trials"])
    newer = []
    for d in included:
        ry = rec_by_id.get(d["id"], {}).get("year")
        try:
            if comp_year and ry and int(ry) > int(comp_year):
                newer.append(rec_by_id.get(d["id"], {}).get("acronym") or d["id"])
        except ValueError:
            pass
    comparator = {
        "name": comp_rec.get("title") or "comparator", "year": comp_year,
        "journal": comp_rec.get("journal"), "pmid": comp_rec.get("id"), "doi": comp_rec.get("doi"),
        "url": (f"https://doi.org/{comp_rec.get('doi')}" if comp_rec.get("doi") else None),
        "open_access": bool(oa.get("is_oa")), "reported": reported,
        "scope": scope.assess(config, comp_rec.get("title") or "", comp_abstract),
        "overlap": {"ours_k": ours_k, "theirs_k": theirs_k,
                    "shared_k": "not exactly verifiable (comparator trial table not machine-exposed)",
                    "only_ours": newer, "only_theirs": [],
                    "method": "publication-date + design identity (comparator trial list not extracted from source)",
                    "note": (f"Trials newer than the comparator ({comp_year}) cannot be in it (only-ours, "
                             f"verifiable by date). Exact shared count not asserted.")},
    }

    return {
        "slug": slug, "title": config["title"], "question": config["question"],
        "method_declared": METHOD,
        "protocol": {"sha": protocol_sha, "committed_utc": records.get("fetched_utc"),
                     "method_declared": METHOD,
                     # Eligibility is GENERATED from the include object the screen enforces, so the
                     # declared eligibility on the page cannot drift from the code that screens.
                     "eligibility": screen.describe_eligibility(config.get("include", {})),
                     "text": _read_text("protocols", slug + ".md")},
        "search": {"n_records": len(merged), "cache_ref": f"cache/{slug}/records.json",
                   "run_utc": records.get("fetched_utc"), "databases": ["PubMed", "ClinicalTrials.gov"],
                   "sources": [{"name": "PubMed", "queries": records.get("pubmed_queries", [])},
                               {"name": "ClinicalTrials.gov", "queries": [json.dumps(records.get("ctgov_query"))]}],
                   "source_status": _source_status(slug, config, records, merged),
                   **({"recall": _rc} if (_rc := _load_recall(slug)) else {}),
                   **({"ghost": _gh} if (_gh := _load_ghost(slug)) else {})},
        "screening": {"records": [{"id": (f"{rec_by_id.get(d['id'],{}).get('acronym')} · " if rec_by_id.get(d['id'],{}).get('acronym') else "") + str(d["id"]),
                                   "id_type": d["id_type"], "decision": d["decision"],
                                   "rule_id": d["rule_id"], "reason": d["reason"],
                                   "span": d.get("span", "")} for d in scr["decisions"]],
                      "positive_control": scr["positive_control"], "negative_control": scr["negative_control"],
                      "dual": _with_model_adjudication(slug, screen.run_dual(merged, config), scr["decisions"])},
        "outcomes": outcomes,
        "comparator": comparator,
        "estimand_exclusions": config.get("estimand_exclusions", []),
        **({"comparator_scope_note": config["comparator_scope_note"]} if config.get("comparator_scope_note") else {}),
        **({"rob2": _rb} if (_rb := _load_rob2(slug)) else {}),
        **({"integrity": _integ} if (_integ := _load_integrity(slug)) else {}),
    }


def build_comparator_core(slug, config, records):
    comp_rec = {r["id"]: r for r in _dedup(records)}.get(config.get("comparator_pmid")) or {}
    comp_abstract = comp_rec.get("abstract", "")
    comp_full = records.get("comparator_fulltext") or ""
    k = (extract.extract_meta(comp_abstract, config["primary_outcome"]["keywords"]).get("k")
         or extract.extract_meta(comp_full, config["primary_outcome"]["keywords"]).get("k"))
    outcomes = []
    for i, co in enumerate(config.get("comparator_outcomes", [])):
        eff = extract.comparator_effect(comp_abstract, comp_full, co["keywords"])
        if eff:
            outcomes.append({"name": co["name"], "kind": co.get("kind", "efficacy"), "primary": i == 0,
                             "estimand": eff["scale"], "population": "as reported", "timepoint": "as reported",
                             "method": "Random-effects meta-analysis (as reported by the source).",
                             "result": {"k": k, "estimate": eff["effect"], "scale": eff["scale"],
                                        "ci_low": eff["ci_low"], "ci_high": eff["ci_high"]},
                             "trials": [], "declared_absent_trials": []})
        else:
            outcomes.append({"name": co["name"], "kind": co.get("kind", "efficacy"), "primary": i == 0,
                             "estimand": "RR", "result": {"present": False, "reason": "not reported/extractable from the source text"}})
    if not outcomes:
        outcomes = [{"name": config["primary_outcome"]["name"], "kind": "efficacy", "primary": True,
                     "estimand": "RR", "result": {"present": False, "reason": "no pooled effect extractable"}}]
    return {
        "slug": slug + "-comparator", "title": config["title"], "question": config["question"],
        "method_declared": "Random-effects meta-analysis (as reported).",
        "protocol": {"present": False, "reason": "transcribed from a published meta-analysis; no machine-readable protocol provided by the source."},
        "search": {"n_records": None, "databases": ["as reported by the source"],
                   "sources": [{"name": "source publication", "queries": ["(reported in the article)"]}],
                   "run_utc": comp_rec.get("year")},
        "screening": {"present": False, "reason": "per-record screening not reproduced from the source."},
        "outcomes": outcomes,
        "comparator": {"present": False, "reason": "not applicable on the comparator's own page"},
        "reproduction": {"present": False, "reason": "the source publication provides no machine-checkable reproduction census."},
    }
