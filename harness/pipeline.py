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


def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=None):
    ctgov_results = ctgov_results or {}
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
            trials.append({"label": label, "id": idstr, **ex})
            continue
        cg = (extract_ctgov(ctgov_results.get(nct), spec["keywords"], interv, comp,
                            min_total=_enrollment_floor(rec.get("abstract", "")))
              if nct and nct in ctgov_results else None)
        if cg:
            cg["provenance"] = "ctgov_results"
            trials.append({"label": label, "id": idstr, **cg})
        else:
            absent.append({"label": label, "id": idstr, "reason": ex["reason"]})
    out = {"name": spec["name"], "kind": kind, "primary": bool(spec.get("primary")),
           "estimand": spec.get("estimand", "RR"), "population": spec.get("population"),
           "timepoint": spec.get("timepoint"), "method": METHOD,
           "trials": trials, "declared_absent_trials": absent}
    if trials:
        meas = (spec.get("estimand") or "RR").upper()
        meas = meas if meas in ("RR", "OR") else "RR"  # 2x2 pools as RR/OR; HR only via effect+CI
        studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"),
                         n2i=t.get("n2i"), effect=t.get("effect"), ci_low=t.get("ci_low"),
                         ci_high=t.get("ci_high"), source=t.get("source", ""), measure=meas) for t in trials]
        out["result"] = _pool_result(studies, scale=spec.get("estimand", "RR"))
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
    outcomes = [_build_outcome(spec, kind, included, rec_by_id, interv, comp, cgr)
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
                     "eligibility": config.get("eligibility_summary", "RCT; intervention vs placebo; "
                                    "on-topic population; double-blind placebo-controlled. P/I/C/design only."),
                     "text": _read_text("protocols", slug + ".md")},
        "search": {"n_records": len(merged), "cache_ref": f"cache/{slug}/records.json",
                   "run_utc": records.get("fetched_utc"), "databases": ["PubMed", "ClinicalTrials.gov"],
                   "sources": [{"name": "PubMed", "queries": records.get("pubmed_queries", [])},
                               {"name": "ClinicalTrials.gov", "queries": [json.dumps(records.get("ctgov_query"))]}]},
        "screening": {"records": [{"id": (f"{rec_by_id.get(d['id'],{}).get('acronym')} · " if rec_by_id.get(d['id'],{}).get('acronym') else "") + str(d["id"]),
                                   "id_type": d["id_type"], "decision": d["decision"],
                                   "rule_id": d["rule_id"], "reason": d["reason"]} for d in scr["decisions"]],
                      "positive_control": scr["positive_control"], "negative_control": scr["negative_control"]},
        "outcomes": outcomes,
        "comparator": comparator,
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
