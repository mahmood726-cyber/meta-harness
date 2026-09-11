"""Deterministic offline pipeline: committed cache + topic config -> screen -> extract
-> synth -> review core (page.py schema). No network, no hand-typed numbers: every value
is produced from the committed fetched cache. A fresh clone reproduces byte-for-byte.
"""
from __future__ import annotations
import json
import os

from . import extract, screen
from .synth import Study, pool

METHOD = ("Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; "
          "HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); "
          "prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1.")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return json.load(f)


def _read_text(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")


def _dedup(records):
    """Prefer the abstract-bearing PubMed record; drop the CT.gov twin (same NCT)."""
    pubmed = records.get("records", [])
    seen_nct = {r.get("nct") for r in pubmed if r.get("nct")}
    merged = list(pubmed)
    for c in records.get("ctgov", []):
        if c.get("id") not in seen_nct:
            merged.append(c)
    return merged


def _pool_result(studies):
    r = pool(studies, scale="RR")
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


def build_review_core(slug, config, records, protocol_sha):
    merged = _dedup(records)
    scr = screen.run(merged, config)
    rec_by_id = {r["id"]: r for r in merged}
    included = [d for d in scr["decisions"] if d["decision"] == "include"]

    po = config["primary_outcome"]
    interv = config.get("intervention_terms", ["colchicine"])
    comp = config.get("comparator_terms", ["placebo", "control"])
    trials, absent = [], []
    for d in included:
        rec = rec_by_id.get(d["id"], {})
        label = rec.get("acronym") or (d.get("label")) or d["id"]
        ex = extract.extract_trial(rec.get("abstract", ""), po["keywords"], interv, comp)
        idstr = f"PMID {d['id']}" if d["id_type"] == "pmid" else d["id"]
        if ex.get("absent"):
            absent.append({"label": label, "id": idstr, "reason": ex["reason"]})
        else:
            trials.append({"label": label, "id": idstr, **ex})

    outcomes = []
    if trials:
        studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"),
                         n2i=t.get("n2i"), effect=t.get("effect"), ci_low=t.get("ci_low"),
                         ci_high=t.get("ci_high"), source=t.get("source", "")) for t in trials]
        result = _pool_result(studies)
    else:
        result = {"present": False, "reason": "no included trial yielded a corroborated outcome value"}
    outcomes.append({"name": po["name"], "kind": "efficacy", "primary": True,
                     "estimand": po.get("estimand", "RR"), "population": po.get("population"),
                     "timepoint": po.get("timepoint"), "method": METHOD,
                     "trials": trials, "declared_absent_trials": absent, "result": result})
    outcomes.append({"name": "Adverse events / discontinuation (harms)", "kind": "harm",
                     "estimand": "RR",
                     "result": {"present": False,
                                "reason": "harms not auto-extracted from abstracts in this build "
                                          "(harness fix F3 queued); the trials report harms qualitatively."}})

    # comparator (auto from its fetched abstract)
    comp_rec = rec_by_id.get(config.get("comparator_pmid")) or {}
    meta = extract.extract_meta(comp_rec.get("abstract", ""), po["keywords"])
    oa = records.get("comparator_oa") or {}
    ours_k = result.get("k") if isinstance(result, dict) and result.get("k") else len(trials)
    theirs_k = meta.get("k")
    comp_year = comp_rec.get("year")
    only_ours = [t["label"] for t, d in zip(trials, [d for d in included if rec_by_id.get(d["id"], {}).get("abstract")])]
    # publication-date-verifiable only-ours: our trials newer than the comparator year
    newer = []
    for t, d in zip(trials, included):
        ry = rec_by_id.get(d["id"], {}).get("year")
        try:
            if comp_year and ry and int(ry) > int(comp_year):
                newer.append(t["label"])
        except ValueError:
            pass
    comparator = {
        "name": comp_rec.get("title") or "comparator", "year": comp_year,
        "journal": comp_rec.get("journal"), "pmid": comp_rec.get("id"), "doi": comp_rec.get("doi"),
        "url": (f"https://doi.org/{comp_rec.get('doi')}" if comp_rec.get("doi") else None),
        "open_access": bool(oa.get("is_oa")),
        "reported": ([{"outcome": po["name"], "estimate": meta["primary"]["effect"],
                       "scale": meta["primary"]["scale"], "ci_low": meta["primary"]["ci_low"],
                       "ci_high": meta["primary"]["ci_high"]}] if meta.get("primary") else []),
        "overlap": {"ours_k": ours_k, "theirs_k": theirs_k,
                    "shared_k": "not exactly verifiable (comparator trial table not auto-extracted)",
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
                     "eligibility": "RCT; colchicine vs placebo added to conventional therapy; "
                                    "pericarditis; double-blind placebo-controlled. P/I/C/design only.",
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
    meta = extract.extract_meta(comp_rec.get("abstract", ""), config["primary_outcome"]["keywords"])
    outcomes = []
    if meta.get("primary"):
        p = meta["primary"]
        outcomes.append({"name": config["primary_outcome"]["name"], "kind": "efficacy", "primary": True,
                         "estimand": p["scale"], "population": "as reported", "timepoint": "as reported",
                         "method": "Random-effects meta-analysis (as reported by the source).",
                         "result": {"k": meta.get("k"), "estimate": p["effect"], "scale": p["scale"],
                                    "ci_low": p["ci_low"], "ci_high": p["ci_high"]},
                         "trials": [], "declared_absent_trials": []})
    else:
        outcomes.append({"name": config["primary_outcome"]["name"], "kind": "efficacy", "primary": True,
                         "estimand": "RR", "result": {"present": False, "reason": "no pooled effect auto-extracted from the comparator abstract"}})
    return {
        "slug": slug + "-comparator", "title": config["title"], "question": config["question"],
        "method_declared": "Random-effects meta-analysis (as reported).",
        "protocol": {"present": False, "reason": "transcribed from a published meta-analysis abstract; no machine-readable protocol provided by the source."},
        "search": {"n_records": None, "databases": ["as reported by the source"],
                   "sources": [{"name": "source publication", "queries": ["(reported in the article)"]}],
                   "run_utc": comp_rec.get("year")},
        "screening": {"present": False, "reason": "per-record screening not reproduced from the source abstract."},
        "outcomes": outcomes,
        "comparator": {"present": False, "reason": "not applicable on the comparator's own page"},
        "reproduction": {"present": False, "reason": "the source publication provides no machine-checkable reproduction census."},
    }
