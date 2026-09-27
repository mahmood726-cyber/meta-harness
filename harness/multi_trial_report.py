"""MULTI-TRIAL REPORTS: one article reporting several registered trials (McMurray et al., Circulation 2024: DETERMINE-
Preserved n=504 and DETERMINE-Reduced n=313, plus an exploratory combined 'DETERMINE-Pooled' analysis).

  * the article is linked to EVERY registration it reports -- never filed under whichever NCT a record lists first;
  * each trial's relevance to a review is DERIVED from its own witnessed population span against the review's own
    population rules (Preserved in, Reduced out, for an HFmrEF/HFpEF review), never from the article as a whole;
  * a combined analysis is recorded and NEVER imported: a pooled row carrying the combined population (its n, or a
    source naming it) is a blocking problem (COMBINED_POPULATION_IMPORTED), as is a pooled row from a trial the review
    derives as not relevant.
Declared in docs/multi_trial_reports.json; witnesses re-hashed, spans required (fail closed).
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from .comparison_family import _terms_in, _verified

PATH = os.path.join("docs", "multi_trial_reports.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(root: str = _ROOT) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    return list((json.load(open(p, encoding="utf-8")) or {}).get("reports") or []) if os.path.exists(p) else []


def _relevance(root: str, trial: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    inc = config.get("include") or {}
    pop = (_verified(root, trial.get("population")) or {}).get("text")
    if trial.get("registration_witness"):
        _verified(root, {"witness": trial["registration_witness"]})
    none = _terms_in(pop, inc.get("population_none"))
    anyp = _terms_in(pop, list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or []))
    if none:
        return {"relevant": False, "basis": f"its own population ({pop!r}) names {none[0]!r}, outside this review"}
    if anyp:
        return {"relevant": True, "basis": f"its own population ({pop!r}) names {anyp[0]!r}"}
    return {"relevant": False, "basis": f"its own population ({pop!r}) names none of this review's populations"}


def _verify_raw(root: str, w: dict[str, Any]) -> None:
    """A witness of a JSON NUMBER field (e.g. seriousNumAffected): the span is checked in the file's raw bytes."""
    import hashlib
    raw = open(os.path.join(root, w["path"]), "rb").read()
    if hashlib.sha256(raw).hexdigest() != w.get("sha256"):
        raise ValueError(f"multi-trial report witness digest mismatch: {w['path']}")
    if w["span"] not in raw.decode("utf-8"):
        raise ValueError(f"multi-trial report witness span not in the held bytes: {w['path']}: {w['span'][:80]!r}")


def resolve(root: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for rep in load(root):
        for c in rep.get("combined_analyses") or []:
            _verified(root, c)
        for t in rep.get("trials") or []:
            if t.get("report_population"):
                _verified(root, t["report_population"])
            for x in ((t.get("registry_results") or {}).get("exploratory_harms") or {}).get("rows") or []:
                for w in x.get("witnesses") or []:
                    if w.get("representation") == "raw bytes":
                        _verify_raw(root, w)
                    else:
                        _verified(root, {"witness": w})
        trials = [{"label": t["label"], "registration": t["registration"], "n_randomised": t.get("n_randomised"),
                   **({"reports": t["reports"]} if t.get("reports") else {}),
                   "population": (_verified(root, t.get("population")) or {}).get("text"),
                   **_relevance(root, t, config),
                   **({"registry_results": t["registry_results"]} if t.get("registry_results") else {})}
                  for t in rep.get("trials") or []]
        out.append({"report_id": rep["report_id"], "citation": rep.get("citation"), "trials": trials,
                    "combined_analyses": [{k: c.get(k) for k in ("label", "n", "policy")} for c in rep.get("combined_analyses") or []],
                    "full_text_state": rep.get("full_text_state")})
    return out


def _nct(x) -> str:
    m = re.search(r"NCT\d{8}", str(x or ""))
    return m.group(0) if m else ""


def _pid(x) -> str:
    m = re.search(r"\b(\d{7,8})\b", str(x or ""))
    return m.group(1) if m else ""


def _fam_ncts(f: dict[str, Any]) -> set[str]:
    """A family's registrations: its id when that is an NCT, and every member report that is one. The family id is the
    identity module's key -- the trial ACRONYM where there is one -- so it is never parsed for an NCT alone."""
    return {x for x in [_nct(f.get("family_id"))] + [_nct(r.get("report_id")) for r in f.get("reports") or []] if x}


def attach(review: dict[str, Any], config: dict[str, Any], root: str = _ROOT) -> None:
    """review['multi_trial_reports'] for any declared report touching this review, and the report link on each
    registration's family object and absent/pooled rows."""
    # a trial is found by its registration OR by its own report PMIDs (a trial with no registry link -- Lemoine's
    # constituent RCTs -- is keyed by its publication)
    keys = lambda t: {t["registration"]} | {_pid(p) for p in t.get("reports") or []}
    regs = set()
    for o in review.get("outcomes") or []:
        for t in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
            regs |= {x for x in (_nct(t.get("id")) or _nct(t.get("nct")), _pid(t.get("id"))) if x}
    for f in review.get("trial_families") or []:
        regs |= _fam_ncts(f) | {_pid(r.get("report_id")) for r in f.get("reports") or []}
    rel = [r for r in resolve(root, config) if any(keys(t) & regs for t in r["trials"])]
    if not rel:
        return
    review["multi_trial_reports"] = rel
    for r in rel:
        shared = [t["registration"] for t in r["trials"]]
        for t in r["trials"]:
            link = {"report_id": r["report_id"], "shared_with": [s for s in shared if s != t["registration"]],
                    "relevant_to_this_review": t["relevant"], "basis": t["basis"]}
            for f in review.get("trial_families") or []:
                if keys(t) & (_fam_ncts(f) | {_pid(x.get("report_id")) for x in f.get("reports") or []}):
                    f["multi_trial_report"] = {**link, "registration": t["registration"]}
            for o in review.get("outcomes") or []:
                for row in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
                    if {x for x in ((_nct(row.get("id")) or _nct(row.get("nct"))), _pid(row.get("id"))) if x} & keys(t):
                        row["multi_trial_report"] = {**link, **({"registry_results": t["registry_results"]}
                                                               if t.get("registry_results") else {})}


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in review.get("multi_trial_reports") or []:
        combined_n = {c.get("n") for c in r.get("combined_analyses") or [] if c.get("n")}
        combined_labels = [c.get("label") for c in r.get("combined_analyses") or [] if c.get("label")]
        not_relevant = {t["registration"] for t in r["trials"] if not t["relevant"]}
        linked = {t["registration"] for t in r["trials"]}
        # a trial's own report PMIDs link its rows too (rows are often keyed by PMID, not by registration)
        linked_rows = linked | {_pid(p) for t in r["trials"] for p in t.get("reports") or []}
        for f in review.get("trial_families") or []:
            mtr = f.get("multi_trial_report")
            if mtr and mtr.get("report_id") == r["report_id"] and set([mtr.get("registration") or _nct(f.get("family_id"))]
                                                                      + mtr.get("shared_with", [])) != linked:
                out.append({"kind": "REPORT_TRIAL_UNLINKED", "report_id": _pid(r["report_id"]),
                            "detail": f"{r['report_id']} is linked to {mtr.get('shared_with')} from {f.get('family_id')}, not to all of {sorted(linked)}"})
        for o in review.get("outcomes") or []:
            for t in o.get("trials") or []:
                ids = {_nct(t.get("id")), _nct(t.get("nct")), _pid(t.get("id"))}
                if not (ids & (linked_rows | {_pid(r["report_id"])})):
                    continue
                n = (t.get("n1i") or 0) + (t.get("n2i") or 0)
                src = str(t.get("source") or "")
                if (n and n in combined_n) or any(lbl and lbl in src for lbl in combined_labels) or \
                        (_pid(t.get("id")) == _pid(r["report_id"]) and not (ids & linked_rows)):
                    out.append({"kind": "COMBINED_POPULATION_IMPORTED", "report_id": _pid(r["report_id"]),
                                "detail": f"{o.get('name')}: {t.get('id')} carries the combined population of {r['report_id']}"})
                if ids & not_relevant:
                    out.append({"kind": "COMBINED_POPULATION_IMPORTED", "report_id": _pid(r["report_id"]),
                                "detail": f"{o.get('name')}: {t.get('id')} is a trial of {r['report_id']} that this "
                                          "review derives as not relevant"})
    return out
