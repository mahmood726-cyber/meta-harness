"""Deterministic topic pipeline: committed cache + screen + extraction + comparator
-> synth (validated method) -> review core (page.py schema). No network, no MCP:
a fresh clone reproduces this byte-for-byte.
"""
from __future__ import annotations
import json
import os

from .synth import Study, pool

METHOD = ("Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; "
          "HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); "
          "prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _read_text(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _pool_outcome(o):
    """Attach a pooled result to an extraction outcome (in place-safe copy)."""
    out = {"name": o["name"], "kind": o.get("kind", "efficacy"),
           "primary": bool(o.get("primary")), "estimand": o.get("estimand"),
           "population": o.get("population"), "timepoint": o.get("timepoint"),
           "method": METHOD,
           "trials": o.get("trials", []), "declared_absent_trials": o.get("declared_absent_trials", [])}
    if isinstance(o.get("result"), dict) and o["result"].get("present") is False:
        out["result"] = o["result"]
        return out
    trials = o.get("trials") or []
    if not trials:
        out["result"] = {"present": False, "reason": "no trials with extractable data for this outcome"}
        return out
    studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"),
                     ci=t.get("ci"), n2i=t.get("n2i"), effect=t.get("effect"),
                     ci_low=t.get("ci_low"), ci_high=t.get("ci_high"),
                     source=t.get("source", "")) for t in trials]
    r = pool(studies, scale=o.get("estimand", "RR"))
    res = {"k": r.k, "estimate": round(r.estimate, 4), "scale": r.scale,
           "ci_low": round(r.ci_low, 4), "ci_high": round(r.ci_high, 4),
           "tau2": round(r.tau2, 5)}
    if r.k > 1:
        res["pi_low"] = round(r.pi_low, 4)
        res["pi_high"] = round(r.pi_high, 4)
        if r.tau2 == 0:
            res["pi_note"] = ("tau^2 estimated as 0, so the prediction interval coincides with "
                              "the confidence interval (no between-study heterogeneity detected).")
    else:
        res["pi_note"] = "prediction interval undefined for k=1"
    out["result"] = res
    return out


def build_review_core(slug: str, protocol_sha: str) -> dict:
    search = _load("cache", slug, "search.json")
    screen = _load("data", slug, "screen.json")
    extraction = _load("data", slug, "extraction.json")
    comparator = _load("data", slug, "comparator.json")
    proto_text = _read_text("protocols", slug + ".md")

    rec_by_id = {r["id"]: r for r in search["records"]}
    screening_records = []
    for d in screen["decisions"]:
        rec = rec_by_id.get(d["id"], {})
        label = rec.get("acronym") or rec.get("id")
        screening_records.append({
            "id": (f"{label} · " if rec.get("acronym") else "") + str(d["id"]),
            "id_type": d.get("id_type"), "decision": d["decision"],
            "rule_id": d["rule_id"], "reason": d["reason"]})

    outcomes = [_pool_outcome(o) for o in extraction["outcomes"]]

    comp = {k: comparator[k] for k in ("name", "year", "journal", "pmid", "doi",
                                       "url", "open_access", "reported", "overlap")}

    title = "Colchicine vs placebo for prevention of pericarditis recurrence"
    return {
        "slug": slug, "title": title,
        "question": ("In patients with pericarditis, does colchicine added to conventional "
                     "anti-inflammatory therapy reduce recurrent pericarditis versus placebo? "
                     "(Double-blind placebo-controlled RCTs.)"),
        "method_declared": METHOD,
        "protocol": {"sha": protocol_sha, "committed_utc": "2026-09-11",
                     "method_declared": METHOD,
                     "eligibility": "RCT; colchicine vs placebo added to conventional therapy; "
                                    "pericarditis; double-blind placebo-controlled (design). "
                                    "Eligibility on P/I/C/design only.",
                     "text": proto_text},
        "search": {"n_records": len(search["records"]),
                   "cache_ref": f"cache/{slug}/search.json",
                   "run_utc": search.get("fetched_utc"),
                   "databases": ["PubMed", "ClinicalTrials.gov"],
                   "sources": search["sources"]},
        "screening": {"records": screening_records,
                      "positive_control": screen.get("positive_control"),
                      "negative_control": screen.get("negative_control")},
        "outcomes": outcomes,
        "comparator": comp,
    }


def build_comparator_core(slug: str) -> dict:
    """The comparator meta rendered in the same tabbed shell (for blind judging)."""
    c = _load("data", slug, "comparator.json")
    outcomes = []
    for i, rep in enumerate(c.get("reported", [])):
        outcomes.append({
            "name": rep["outcome"],
            "kind": "harm" if rep["outcome"].lower() in ("adverse events", "drug withdrawal") else "efficacy",
            "primary": i == 0, "estimand": rep.get("scale"),
            "population": "as reported", "timepoint": "as reported",
            "method": "Random-effects meta-analysis (as reported by the source).",
            "result": {"k": c.get("theirs_k"), "estimate": rep["estimate"], "scale": rep["scale"],
                       "ci_low": rep["ci_low"], "ci_high": rep["ci_high"]},
            "trials": [],
            "declared_absent_trials": []})
    return {
        "slug": slug + "-comparator",
        "title": "Colchicine vs placebo for prevention of pericarditis recurrence",
        "question": ("In patients with pericarditis, does colchicine added to conventional "
                     "therapy reduce recurrent pericarditis versus placebo?"),
        "method_declared": "Random-effects meta-analysis (Mantel-Haenszel / as reported).",
        "protocol": {"present": False,
                     "reason": "This page transcribes a published meta-analysis; a machine-readable "
                               "protocol/registration is not provided by the source."},
        "search": {"n_records": None, "databases": ["PubMed", "EMBASE", "Cochrane Library", "others"],
                   "sources": [{"name": "As reported by the source publication",
                                "queries": ["colchicine AND pericarditis (controlled clinical trials)"]}],
                   "run_utc": str(c.get("year"))},
        "screening": {"present": False,
                      "reason": f"Per-record screening decisions are not reproduced from the source; "
                                f"the source reports {c.get('design')}"},
        "outcomes": outcomes,
        "comparator": {"present": False, "reason": "not applicable on the comparator's own page"},
        "reproduction": {"present": False,
                         "reason": "The source publication does not provide a machine-checkable "
                                   "reproduction census."},
    }
