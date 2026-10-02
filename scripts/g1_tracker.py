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
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if x["in_our_pool"])),
            "same_trials": dict(same_trials_pool(pairs, method),
                                method_basis=("comparator positive control reproduced " + method) if pc.get("methods")
                                else "comparator positive control not reproduced: PM default"),
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
          "| topic | k matched | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        r, st = o["routes"], o["same_trials"]
        same = (f"{st['measure']} {_fmt(st['ours'])} vs {_fmt(st['theirs'])}, k={st['k']}, {st['method']}: "
                f"**{(st.get('verdict') or {}).get('verdict')}**" if st.get("state") == "POOLED" else st.get("state"))
        md.append(f"| {o['slug']} | {o['k_matched']} of {o['N_comparator_trials']} | {r.get('PRIMARY', 0)} | "
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
