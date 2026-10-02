"""G1 TRACKER: per-topic G1 status, derived only (Mahmood decisions, 2 Oct). SHARED G1 INTERFACE.

    python scripts/g1_tracker.py SLUG [SLUG ...]   -> outputs/k_gap/g1/<slug>.json   (one file per topic: lanes building
                                                      different topics never write the same file)
    python scripts/g1_tracker.py --table           -> outputs/k_gap/G1_TRACKER.md     (rebuilt from every g1/*.json)

Per topic (schema pinned by tests/test_g1_interfaces.py; add keys, never rename them):
  N_comparator_trials / k_matched     comparator trials (k-gap table, other agents excluded) / those in OUR branch pool
  routes                              per comparator trial: PRIMARY (our extraction of the trial's own report or posted
                                      CT.gov results, or a meta row typed-matched to one) / TWO_SOURCE / UNVERIFIED /
                                      NO_ROW (no number from any source; `basis` gives the gap class)
  per_trial_agreement                 our pooled row vs the COMPARATOR's own printed row for that trial (typed, rounding-
                                      aware): AGREE / DISAGREE / NOT_COMPARABLE[:why]
  same_trials                         the RESULT on the SAME trials: our rows and the comparator's rows for exactly the
                                      shared trials, pooled by the method the comparator's own positive control
                                      reproduced -- the like-for-like G1 result comparison
  ours / comparator                   our branch pool vs the comparator's printed pooled result
  ours_not_in_comparator              trials we pool that the comparator does not list (scope or publication date)
Nothing here is typed by hand; every number comes from committed artefacts or the in-memory rebuild.
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
G1_DIR = os.path.join(OUT, "g1")
SCHEMA_VERSION = 1


def _int(v):
    try:
        return int(str(v)[:4])
    except (TypeError, ValueError):
        return None


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _row(d):
    return sm.SecondaryRow(**{k: v for k, v in d.items() if k in sm.SecondaryRow.__dataclass_fields__})


def as_row(primary, label, measure_hint=None):
    """Our primary value dict (secondary_meta_build.our_trials) as a SecondaryRow, so both sides pool identically."""
    if not primary:
        return None
    return sm.SecondaryRow(meta_pmid="OURS", meta_doi="", location={}, source_digest="", provenance="PRIMARY",
                           trial_label=label, measure=(primary.get("measure") or measure_hint or "").upper(),
                           outcome_definition="", effect=primary.get("effect"), lower=primary.get("lower"),
                           upper=primary.get("upper"), events_t=primary.get("events_t"), n_t=primary.get("n_t"),
                           events_c=primary.get("events_c"), n_c=primary.get("n_c"))


def agreement(ours, theirs):
    """Our pooled value vs the comparator's printed row for the same trial: AGREE / DISAGREE / NOT_COMPARABLE[:why]."""
    if not ours or not theirs:
        return "NOT_COMPARABLE:NO_COMPARATOR_ROW" if ours else "NOT_COMPARABLE"
    if ours.get("events_t") is not None and theirs.events_t is not None:
        same = (ours["events_t"], ours["n_t"], ours["events_c"], ours["n_c"]) == \
               (theirs.events_t, theirs.n_t, theirs.events_c, theirs.n_c)
        return "AGREE" if same else "DISAGREE"
    if ours.get("effect") is None or theirs.effect is None:
        return "NOT_COMPARABLE:COUNTS_VS_EFFECT"
    if (ours.get("measure") or "").upper() != theirs.measure.upper():
        return f"NOT_COMPARABLE:{ours.get('measure')}_VS_{theirs.measure}"
    eq = all(sm._eq_printed(a, b) for a, b in ((ours["effect"], theirs.effect), (ours["lower"], theirs.lower),
                                                 (ours["upper"], theirs.upper)))
    return "AGREE" if eq else "DISAGREE"


def same_trials_pool(pairs, method_label):
    """pairs: [(our_row, their_row)] for the shared trials. Both sides pooled by ONE method; None if any side cannot."""
    if len(pairs) < 2:
        return {"state": "FEWER_THAN_2_SHARED_TRIALS", "k": len(pairs)}
    measures = {r.measure.upper() for p in pairs for r in p}
    if len(measures) != 1:
        return {"state": "MIXED_MEASURES", "measures": sorted(measures), "k": len(pairs)}
    measure = measures.pop()
    method, hk = method_label.replace("+HK", ""), method_label.endswith("+HK")
    g = math.exp if measure in sm.RATIO else (lambda x: x)
    out = {"state": "POOLED", "k": len(pairs), "measure": measure, "method": method_label}
    for side, idx in (("ours", 0), ("theirs", 1)):
        yv = [sm.row_yi_vi(p[idx]) for p in pairs]
        if any(v is None for v in yv):
            return {"state": f"{side.upper()}_ROW_NOT_POOLABLE", "k": len(pairs)}
        mu, lo, hi = (g(x) for x in sm.pool([v[0] for v in yv], [v[1] for v in yv], method, hk))
        out[side] = {"estimate": round(mu, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4)}
    out["verdict"] = result_verdict(out["ours"], out["theirs"], measure)
    return out


def no_trial_rows_result(trials, ours, theirs):
    """PROPOSED on g1/noac for the k-gap lane (additive key). A patient-level comparator (COMBINE AF) prints NO per-trial
    rows, so same_trials_pool has nothing to pair. When EVERY comparator trial is in our pool and NONE has a printed row,
    our pool over those trials IS the same-trials pool, and the like-for-like comparison is it vs the comparator's printed
    pooled result -- by the same result_verdict. Any trial missing from our pool, or any printed row, -> None."""
    if not trials or any(not t["in_our_pool"] or t["comparator_row"] for t in trials):
        return None
    if ours.get("k") != len(trials) or ours.get("estimate") is None or theirs.get("estimate") is None:
        return None
    measure = (ours.get("scale") or "").upper()
    if measure != (theirs.get("scale") or "").upper():
        return {"state": "MEASURE_DIFFERS", "ours": ours.get("scale"), "theirs": theirs.get("scale")}
    o = {k: ours[k] for k in ("estimate", "ci_low", "ci_high")}
    t = {k: theirs[k] for k in ("estimate", "ci_low", "ci_high")}
    return {"state": "COMPARATOR_PRINTS_NO_TRIAL_ROWS", "k": len(trials), "measure": measure, "ours": o, "theirs": t,
            "verdict": result_verdict(o, t, measure),
            "note": "ours = our served pool over exactly the comparator's trials; theirs = its printed pooled result; "
                    "estimators differ (theirs is patient-level)"}


def result_verdict(ours, theirs, measure):
    """Like-for-like RESULT agreement on the same trials, typed:
      AGREE     same conclusion about the null (both exclude it on the same side, or both include it) AND the estimates
                differ by less than 10% of the comparator's CI half-width (on the analysis scale: log for ratios)
      SAME_CONCLUSION_DIFFERENT_ESTIMATE / DIFFERENT_CONCLUSION otherwise."""
    null = 1.0 if measure in sm.RATIO else 0.0
    f = math.log if measure in sm.RATIO else (lambda x: x)

    def concl(r):
        return "BENEFIT" if r["ci_high"] < null else "HARM" if r["ci_low"] > null else "NULL_INCLUDED"
    if concl(ours) != concl(theirs):
        return {"verdict": "DIFFERENT_CONCLUSION", "ours": concl(ours), "theirs": concl(theirs)}
    half = (f(theirs["ci_high"]) - f(theirs["ci_low"])) / 2
    rel = abs(f(ours["estimate"]) - f(theirs["estimate"])) / half if half > 0 else float("inf")
    return {"verdict": "AGREE" if rel < 0.10 else "SAME_CONCLUSION_DIFFERENT_ESTIMATE", "conclusion": concl(ours),
            "estimate_gap_over_ci_halfwidth": round(rel, 4)}


def definition_gate(spec_name, registry_title):
    """The harness composite gate (extract.composite_component_mismatch) applied to a REGISTRY OUTCOME TITLE. The gate
    reads a span only when it is a composite-DEFINITION clause ('composite' / 'primary' in it), so that an abstract's
    incidental mention of a component is not read as the outcome. A registry outcome title IS the outcome's definition
    ('Time to First Occurence of CV Event: CV Death, Non-Fatal MI, Non-Fatal Stroke, Hospitalization for Unstable
    Angina or Hospitalization For Heart Failure'), so it is passed AS a definition clause: without that, ELIXA's 5- and
    6-component secondaries passed as bindable 3-point MACE."""
    from harness import extract
    return extract.composite_component_mismatch(spec_name, "composite outcome definition: " + (registry_title or ""))


def registry_binding(nct, spec_name, keywords):
    """BIND A COMPARATOR TRIAL WE DO NOT POOL VIA THE AACT SNAPSHOT (source hierarchy 2a), through the same gates.
    Candidates: the trial's PRIMARY posted outcomes and any outcome whose title names a topic keyword. Gates, in order:
      ESTIMAND  extract.composite_component_mismatch(topic outcome, registry outcome title) -- a different composite
      ARMS      two distinct result groups with people-unit counts (aact_adapter rules 2)
    Returns {"state": "BINDABLE"|"REFUSED"|"NO_POSTED_RESULTS"|"SNAPSHOT_UNAVAILABLE", "candidates": [...]}."""
    from harness import extract
    from kgap import aact_adapter
    try:
        aact_adapter.ensure([nct])
    except FileNotFoundError as exc:
        return {"state": "SNAPSHOT_UNAVAILABLE", "why": str(exc)[:160]}
    reg = aact_adapter.registry_for(nct)
    if not reg:
        return {"state": "NO_POSTED_RESULTS", "nct": nct}
    kws = [k.lower() for k in keywords if k]
    cands = []
    for oid, o in reg["outcomes"].items():
        t = o.get("title") or ""
        if (o.get("type") or "").upper() != "PRIMARY" and not any(k in t.lower() for k in kws):
            continue
        groups = reg["groups"].get(oid) or []
        an = next((a for a in reg["analyses"] if a["outcome_id"] == oid), None)
        c = {"nct": nct, "outcome_id": oid, "title": t, "time_frame": o.get("time_frame"),
             "arms": [dict(g, title=reg["group_titles"].get(str(g["group"]))) for g in groups], "analysis": an,
             "snapshot": reg["_snapshot"]}
        mm = definition_gate(spec_name, t)
        if mm:
            c.update(gate="ESTIMAND", verdict="REFUSED", reason=mm)
        elif len({g["group"] for g in groups}) < 2:
            c.update(gate="ARMS", verdict="REFUSED", reason="fewer than two result groups with people-unit counts")
        else:
            c.update(gate=None, verdict="BINDABLE", reason=None)
        cands.append(c)
    if not cands:
        return {"state": "NO_CANDIDATE_OUTCOME", "nct": nct}
    return {"state": "BINDABLE" if any(c["verdict"] == "BINDABLE" for c in cands) else "REFUSED", "candidates": cands}


def protocol_rule(cfg, term):
    """The registered protocol field that holds an exclusion term: 'include.population_none[20] = liraglutide'."""
    for key, vals in (cfg.get("include") or {}).items():
        if isinstance(vals, list):
            for i, v in enumerate(vals):
                if isinstance(v, str) and v.lower() == (term or "").lower():
                    return f"include.{key}[{i}] = {v!r}"
    return None


def scope_difference(x, cfg):
    """A comparator trial we do not pool, NAMED: PROTOCOL_SCOPE_DIFFERENCE (our registered screen excludes it, rule
    cited) or ESTIMAND_DIFFERENCE (its only available result is a different estimand, gate cited). None when the
    trial is an open gap (it must then stay visible as NO_ROW, never be dropped)."""
    import re as _re
    f = x.get("seeded_funnel") or {}
    if f.get("stage") == "SCREENED_OUT" and f.get("rule_id"):
        m = _re.search(r"mention '([^']+)'", f.get("reason") or "")
        return {"kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": f["rule_id"], "screen_reason": f.get("reason"),
                "protocol_rule": protocol_rule(cfg, m.group(1)) if m else None,
                "registered_eligibility": cfg.get("eligibility_summary"), "pmid": f.get("pmid")}
    rb = x.get("registry_binding") or {}
    ref = [c for c in rb.get("candidates") or [] if c.get("gate") == "ESTIMAND"]
    if rb.get("state") == "REFUSED" and ref:
        c = ref[0]
        return {"kind": "ESTIMAND_DIFFERENCE", "gate": "harness.extract.composite_component_mismatch",
                "reason": c["reason"], "registry_outcome": c["title"], "registry_arms": c["arms"],
                "registry_analysis": c["analysis"], "snapshot": c["snapshot"],
                "comparator_pooled_it_as": x.get("comparator_row")}
    return None


def comparator_findings(trials, comp):
    """Findings ABOUT the comparator's own rows, typed, each with where it sits and what it rests on."""
    out = []
    for x in trials:
        if x.get("disagreement_side", "") and str(x["disagreement_side"]).startswith("SECONDARY_WRONG"):
            out.append({"finding": "COMPARATOR_ROW_DIFFERS_FROM_TRIAL_REPORT", "trial": x["label"], "comparator": comp,
                        "comparator_row": x.get("comparator_row"), "trial_report": x.get("our_value"),
                        "basis": x["disagreement_side"]})
        for f in x.get("comparator_row_findings") or []:
            out.append({"finding": f.get("finding"), "trial": x["label"], "comparator": comp,
                        "comparator_row": x.get("comparator_row"), "detail": f.get("printed_vs_arm_derived")})
    return out


def topic(slug, T):
    import secondary_meta_build as smb
    import k_gap_counterfactual as cfm
    S = _j(os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json"))
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    comp = S["comparator_pmid"]
    ours = smb.our_trials(slug)
    core = cfm.build(slug)
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    pooled_ids = {str(t.get("id")) for t in prim.get("trials", [])}
    absent_by_id = {str(a.get("id")): str(a.get("reason") or a.get("reason_code") or "")[:240]
                    for a in prim.get("declared_absent_trials", [])}
    rows = [_row(d) for d in S["rows"]]
    by_fam = {}
    for r in rows:
        by_fam.setdefault(r.family_id, []).append(r)
    comp_rows = [t for t in T["trials"] if t["slug"] == slug and t.get("drug") != "OTHER_AGENT"]
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    spec_name = (cfg.get("primary_outcome") or {}).get("name") or ""
    kw_all = list((cfg.get("primary_outcome") or {}).get("keywords") or [])
    trials, routes, pairs, matched_ids = [], Counter(), [], set()
    for t in comp_rows:
        mine = next((o for o in ours if (o.get("nct") and o["nct"] in (t.get("ncts") or []))
                     or o["pmid"] in (t.get("pmids") or [])), None)
        fam = mine["id"] if mine else None
        in_pool = bool(mine and str(mine["id"]) in pooled_ids and mine.get("primary"))
        sec = by_fam.get(fam, []) if fam else []
        # the comparator's OWN printed row for this trial, whatever its admission state: agreement asks what the
        # comparator pooled for the trial, not whether we may use its row as data
        theirs = next((r for r in sec if r.meta_pmid == comp), None)
        if in_pool:
            matched_ids.add(str(mine["id"]))
            route, basis = "PRIMARY", mine["primary"]["source"]
            if theirs:
                pairs.append((as_row(mine["primary"], t["label"], theirs.measure), theirs))
        else:
            refusal = absent_by_id.get(str(mine["id"])) if mine else None
            best = sorted(sec, key=lambda r: {"PRIMARY": 0, "TWO_SOURCE": 1}.get(sm.route_of(r), 2))
            if best and best[0].state != sm.REFUSED:
                route = sm.route_of(best[0])
                basis = f"meta {best[0].meta_pmid} {best[0].state} {(best[0].verification or {}).get('route') or ''}".strip()
            else:
                route = "NO_ROW"
                basis = (t.get("gap_class") or "") + (
                    f" (secondary refused: {sorted({x for r in sec for x in r.reasons})[:3]})" if sec else "")
        routes[route] += 1
        trials.append({"label": t["label"][:60], "family": fam, "in_our_pool": in_pool, "route": route, "basis": basis,
                       "our_refusal": None if in_pool else (refusal or (t.get("gap_class") if not mine else None)),
                       "comparator_row": ({k: getattr(theirs, k) for k in ("effect", "lower", "upper", "events_t", "n_t",
                                                                           "events_c", "n_c", "measure")}
                                          if theirs else None),
                       "comparator_row_findings": theirs.findings if theirs else [],
                       "disagreement_side": ((theirs.verification or {}).get("which_side")
                                             if theirs and theirs.state == sm.MISMATCH else None),
                       "our_value": ({k: mine["primary"].get(k) for k in ("measure", "effect", "lower", "upper",
                                                                          "events_t", "n_t", "events_c", "n_c")}
                                     if in_pool else None),
                       "registry_binding": (registry_binding(t["ncts"][0], spec_name, kw_all)
                                            if not in_pool and (t.get("ncts") or []) else None),
                       "g1_countable": route == "PRIMARY" or bool(sm.g1_countable(sec, {comp})),
                       "agreement_with_comparator_row": agreement(mine and mine.get("primary"), theirs) if in_pool
                       else "NOT_IN_OUR_POOL", "comparator_row_state": theirs.state if theirs else None})
    # comparator trials we hold NO record of: seed their held PubMed records through OUR build (in memory) once, so the
    # tracker says what our own screen/extraction does with each -- not just "identification gap"
    screened = {str(r["id"]) for r in core["screening"]["records"]}
    unseen = {p for x, t in zip(trials, comp_rows) if x["route"] == "NO_ROW"
              for p in (t.get("pmids") or [])[:1] if str(p).isdigit() and str(p) not in screened}
    if unseen:
        mp = os.path.join(OUT, "member_records.json")
        held = _j(mp) if os.path.exists(mp) else {}
        recs = [held[p] for p in sorted(unseen) if p in held]
        fun = cfm.funnel(cfm.build(slug, extra_records=recs), [r["id"] for r in recs], recs) if recs else {}
        for x, t in zip(trials, comp_rows):
            p = next((q for q in (t.get("pmids") or [])[:1] if q in fun), None)
            if p and x["route"] == "NO_ROW":
                f = fun[p]
                x["seeded_funnel"] = dict(f, pmid=p)
                x["our_refusal"] = f"SEEDED PMID {p}: {f['stage']}" + (
                    f" {f.get('rule_id')}: {f.get('reason')}" if f.get("rule_id") else
                    f" {f.get('reason_code')}" if f.get("reason_code") else "")
            elif x["route"] == "NO_ROW" and (t.get("pmids") or [None])[0] in unseen:
                x["our_refusal"] = "NO_RECORD_HELD"
    for x in trials:
        x["scope_difference"] = None if x["in_our_pool"] else scope_difference(x, cfg)
    named = [{"trial": x["label"], **x["scope_difference"]} for x in trials if x.get("scope_difference")]
    open_gaps = [x["label"] for x in trials if not x["in_our_pool"] and not x.get("scope_difference")]
    pc = ((S.get("metas") or {}).get(comp) or {}).get("positive_control") or {}
    method = (pc.get("methods") or ["PM"])[0]
    res = prim.get("result") or {}
    rep = ((rev.get("comparator") or {}).get("reported") or [{}])[0]
    comp_basis = "served review comparator.reported" if rep else None
    cm = (S.get("metas") or {}).get(comp) or {}
    if not rep and cm.get("usable") and cm.get("pooled") and cm.get("provenance") == "TYPED_TABLE":
        # the served review typed no comparator result; the comparator's OWN pooled row, typed from its JATS table and
        # reproduced from its rows (positive control), is the comparator result -- with that basis stated
        pr = cm["pooled"]
        rep = {"outcome": cm.get("identity_basis"), "estimate": sm._num(pr["effect"]), "ci_low": sm._num(pr["lower"]),
               "ci_high": sm._num(pr["upper"]), "scale": cm.get("measure")}
        comp_basis = (f"comparator's typed table {cm.get('table')} pooled row, positive control "
                      f"{cm.get('positive_control', {}).get('methods')}")
    extra = sorted(str(t.get("id")) for t in prim.get("trials", []) if str(t.get("id")) not in matched_ids)
    recs = {str(r.get("id")): r for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", [])}
    comp_year = _int((rev.get("comparator") or {}).get("year"))
    extra_detail = []
    for e in extra:
        y = _int((recs.get(e.replace("PMID ", "")) or {}).get("year"))
        extra_detail.append({"id": e, "year": y, "comparator_year": comp_year,
                             "why_not_in_comparator": ("PUBLISHED_AFTER_COMPARATOR" if y and comp_year and y > comp_year
                                                       else "NOT_EXPLAINED_BY_DATE")})
    return {"schema_version": SCHEMA_VERSION, "slug": slug, "comparator_pmid": comp,
            "N_comparator_trials": len(trials), "k_matched": sum(1 for x in trials if x["in_our_pool"]),
            "N_eligible": len(trials) - len(named), "named_differences": named, "open_gaps": open_gaps,
            "comparator_findings": comparator_findings(trials, comp),
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if x["in_our_pool"])),
            "same_trials": dict(same_trials_pool(pairs, method),
                                method_basis=("comparator positive control reproduced " + method) if pc.get("methods")
                                else "comparator positive control not reproduced: PM default"),
            "same_trials_no_trial_rows": no_trial_rows_result(trials, res, rep),
            "ours": {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")},
            "comparator": {k: rep.get(k) for k in ("outcome", "estimate", "ci_low", "ci_high", "scale")},
            "comparator_basis": comp_basis,
            "ours_not_in_comparator": extra, "ours_not_in_comparator_detail": extra_detail,
            "secondary_tally": S["tally"], "secondary_skipped": S["skipped"], "registry": S.get("registry")}


def _fmt(r):
    if not r or r.get("estimate") is None:
        return "not printed"
    lo, hi = r.get("ci_low"), r.get("ci_high")
    ci = f" ({lo:.2f} to {hi:.2f})" if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) else " (no CI)"
    return f"{r.get('scale') or ''} {r['estimate']:.2f}{ci}".strip()


def table():
    out = [_j(os.path.join(G1_DIR, f)) for f in sorted(os.listdir(G1_DIR)) if f.endswith(".json")]
    md = ["# G1 tracker (derived: scripts/g1_tracker.py; one source file per topic in outputs/k_gap/g1/)", "",
          "| topic | k matched | named differences | open gaps | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        r, st = o["routes"], o["same_trials"]
        same = (f"{st['measure']} {_fmt(st['ours'])} vs {_fmt(st['theirs'])}, k={st['k']}, {st['method']}: "
                f"**{(st.get('verdict') or {}).get('verdict')}**" if st.get("state") == "POOLED" else st.get("state"))
        nr = o.get("same_trials_no_trial_rows")
        if st.get("state") != "POOLED" and nr and nr.get("state") == "COMPARATOR_PRINTS_NO_TRIAL_ROWS":
            same = (f"{nr['measure']} {_fmt(nr['ours'])} vs {_fmt(nr['theirs'])}, k={nr['k']} (comparator prints no "
                    f"trial rows; ours on its trials vs its pooled): **{nr['verdict']['verdict']}**")
        nd = o.get("named_differences") or []
        md.append(f"| {o['slug']} | {o['k_matched']} of {o.get('N_eligible', o['N_comparator_trials'])} eligible "
                  f"(comparator N={o['N_comparator_trials']}) | "
                  f"{len(nd)}: " + ", ".join(f"{d['trial']} ({d['kind']})" for d in nd) + f" | {len(o.get('open_gaps') or [])} | "
                  f"{r.get('PRIMARY', 0)} | "
                  f"{r.get('TWO_SOURCE', 0)} | {r.get('UNVERIFIED', 0)} | {r.get('NO_ROW', 0)} | "
                  f"{o['per_trial_agreement']} | {same} | {_fmt(o['ours'])} k={o['ours'].get('k')} | {_fmt(o['comparator'])} |")
    for o in out:
        md += ["", f"## {o['slug']} (comparator PMID {o['comparator_pmid']})", ""]
        for x in o["trials"]:
            md.append(f"- {x['label']}: **{x['route']}** - {x['basis']}; vs comparator row: "
                      f"{x['agreement_with_comparator_row']}"
                      + (f"; our refusal: {x['our_refusal']}" if x.get("our_refusal") else "")
                      + (f"; comparator row finding: {x['comparator_row_findings']}" if x.get("comparator_row_findings") else "")
                      + (f"; side: {x['disagreement_side']}" if x.get("disagreement_side") else ""))
        for d in o.get("named_differences") or []:
            if d["kind"] == "PROTOCOL_SCOPE_DIFFERENCE":
                md.append(f"- NAMED {d['kind']}: {d['trial']} -- screen {d['rule_id']} ({d['screen_reason']}); protocol "
                          f"rule {d['protocol_rule']}; registered eligibility: {d['registered_eligibility']}")
            else:
                an = d.get("registry_analysis") or {}
                md.append(f"- NAMED {d['kind']}: {d['trial']} -- {d['gate']}: {d['reason']}. Registry ({d['snapshot']['id']}): "
                          f"'{d['registry_outcome']}', arms " + ", ".join(f"{a.get('title')} {a['count']}/{a['n']}"
                                                                         for a in d.get("registry_arms") or [])
                          + (f", {an.get('param_type')} {an.get('param_value')} ({an.get('ci_lower')}-{an.get('ci_upper')})"
                             if an else "") + f"; the comparator pooled it as {d.get('comparator_pooled_it_as')}")
        for f in o.get("comparator_findings") or []:
            md.append(f"- COMPARATOR FINDING {f['finding']}: {f['trial']} -- comparator row {f.get('comparator_row')}"
                      + (f" vs trial report {f['trial_report']}" if f.get("trial_report") else "")
                      + (f"; {f['detail']}" if f.get("detail") else "") + (f" ({f['basis']})" if f.get("basis") else ""))
        for e in o.get("ours_not_in_comparator_detail") or []:
            md.append(f"- pooled by us, not listed by the comparator: {e['id']} ({e['year']}; comparator "
                      f"{e['comparator_year']}): {e['why_not_in_comparator']}")
    with open(os.path.join(OUT, "G1_TRACKER.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")
    return md


def main(argv):
    if argv and argv != ["--table"]:
        T = _j(os.path.join(OUT, "k_gap_table.json"))
        os.makedirs(G1_DIR, exist_ok=True)
        for s in [a for a in argv if not a.startswith("--")]:
            with open(os.path.join(G1_DIR, f"{s}.json"), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(topic(s, T), fh, indent=1, ensure_ascii=False)
    print("\n".join(table()[:4 + len(os.listdir(G1_DIR))]))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
