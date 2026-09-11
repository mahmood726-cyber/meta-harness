"""Deterministic offline pipeline: committed cache + topic config -> screen -> extract
(primary + secondary + harms) -> synth -> review core. No network, no hand-typed numbers;
a fresh clone reproduces byte-for-byte.
"""
from __future__ import annotations
import json
import os

from . import extract, screen
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


def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=None,
                   fulltext_by_pmid=None, outcome_judgments=None):
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
        ex = extract.extract_trial(rec.get("abstract", ""), spec["keywords"], interv, comp)
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
        fx = extract.extract_trial(ft, spec["keywords"], interv, comp) if ft else None
        if fx and not fx.get("absent"):
            fx["provenance"] = "pmc_fulltext"
            trials.append({"label": label, "id": idstr, **fx})
        else:
            absent.append({"label": label, "id": idstr, "reason": ex["reason"]})
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
        else:
            pooled_scale = spec.get("estimand", "RR")
        out["result"] = _pool_result(studies, scale=pooled_scale)
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
    outcomes = [_build_outcome(spec, kind, included, rec_by_id, interv, comp, cgr, ftbp,
                               outcome_judgments=ojudg)
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
                               {"name": "ClinicalTrials.gov", "queries": [json.dumps(records.get("ctgov_query"))]}]},
        "screening": {"records": [{"id": (f"{rec_by_id.get(d['id'],{}).get('acronym')} · " if rec_by_id.get(d['id'],{}).get('acronym') else "") + str(d["id"]),
                                   "id_type": d["id_type"], "decision": d["decision"],
                                   "rule_id": d["rule_id"], "reason": d["reason"],
                                   "span": d.get("span", "")} for d in scr["decisions"]],
                      "positive_control": scr["positive_control"], "negative_control": scr["negative_control"]},
        "outcomes": outcomes,
        "comparator": comparator,
        "estimand_exclusions": config.get("estimand_exclusions", []),
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
