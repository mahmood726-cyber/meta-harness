"""Tracker entry for tocilizumab-covid19-mortality vs WHO REACT 2021, in the G1 tracker schema (kgap/G1_INTERFACES.md
section 4, schema_version 1), built from g1/tocilizumab.py -- the topic's own G1 lane -- instead of the served pool
(which pools k=1) and the secondary tier (which refused REACT: no open JATS). The basis is stated in the file.

  python scripts/g1_toci_tracker.py   -> outputs/k_gap/g1/tocilizumab-covid19-mortality.json, then g1_tracker.py --table
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from g1 import tocilizumab as g  # noqa: E402

SLUG = "tocilizumab-covid19-mortality"
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{SLUG}.json")
ROUTE = {g.ESTABLISHED: "PRIMARY", g.SECONDARY_COUNT: "UNVERIFIED", g.ONE_SOURCE: "UNVERIFIED", g.CONFLICT: "UNVERIFIED", g.NO_SOURCE: "NO_ROW"}


CASCADE = os.path.join(ROOT, "g1", "data", "cascade")


def cascade_summary(label):
    """The acquisition cascade as run for this trial (scripts/g1_toci_cascade.py): what each rung returned."""
    fp = os.path.join(CASCADE, f"{label}.json")
    if not os.path.exists(fp):
        return {"state": "CASCADE_NOT_RUN"}
    c = json.load(open(fp, encoding="utf-8"))
    acq = os.path.join(ROOT, "g1", "data", "acquired")
    pc = [r for r in c["candidates"] if r["screen"] == "PRIMARY_REPORT_CANDIDATE"]

    def bound(p):
        f = os.path.join(acq, f"{p}.json")
        a = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
        return a.get("binding"), label in (a.get("bound_labels") or [])
    return {"run_utc": c["run_utc"],
            "discovery": {d["rung"] + (" " + d["request"].split("term=")[-1][:40] if "term=" in d.get("request", "") else ""):
                          len(d["returned"]) for d in c["discovery"]},
            "candidates_found": len(c["candidates"]),
            "primary_report_candidates": [{"pmid": r["pmid"], "title": r["title"][:90],
                                           "R1_PMC": r["rungs"][0]["outcome"], "R2_EuropePMC": r["rungs"][1]["outcome"],
                                           "R3_Unpaywall": r["rungs"][2]["outcome"] + (
                                               f" ({r['rungs'][2].get('host')}, {r['rungs'][2].get('licence')})"
                                               if r["rungs"][2].get("is_oa") else ""),
                                           "held_open_text": r.get("held"), "binding": bound(r["pmid"])[0],
                                           "read_for_this_trial": bound(r["pmid"])[1]} for r in pc],
            "R4_AACT": c["trial_rungs"][0]["outcome"], "R5_ISRCTN": c["trial_rungs"][1]["outcome"]}


VNH = os.path.join(ROOT, "g1", "data", "verified_not_held.json")
COUNTABLE = ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE")


def _tuple(x):
    return (x["events_t"], x["total_t"], x["events_c"], x["total_c"]) if "events_t" in x else         (x["deaths_t"], x["n_t"], x["deaths_c"], x["n_c"])


def aact_day28_percentages(label):
    """[(arm, posted %, analysed n, group)] for the trial's posted DAY-28 mortality outcome given as percentages (a
    primary, but a percentage: it can type a meta row's timepoint, never supply its counts)."""
    ex = json.load(open(g.AACT_FILE, encoding="utf-8"))
    nct = g.IDENTITY[label][0]
    out = []
    for o in (ex.get("outcomes") or {}).values():
        if o["nct_id"] != nct or not g._DEATH_WORDS.search(o.get("title") or "") or g._OTHER_EVENT.search(o.get("title") or ""):
            continue
        if "percent" not in (o.get("units") or "").lower():
            continue
        for m in o["measurements"]:
            when = m["classification"] or o.get("time_frame") or ""
            if not g._DAY28.search(when) or g._OTHER_DAY.search(when):
                continue
            grp = m["group"] or ""
            arm = "t" if g._TOCI.search(grp) and not re.search(r"free|placebo", grp, re.I) else "c" if g._CONTROL.search(grp) else None
            try:
                out.append((arm, float(m["value"]), int(o["analysed"].get(grp)), grp))
            except (TypeError, ValueError):
                continue
    out = [x for x in out if x[0]]
    # a registration shared by two REACT rows posts one group per POPULATION ('TOCILIZUMAB -- Critical COVID Population
    # (WHO-CPS >5)'): keep this label's population only; with population groups and no rule for this label, none
    # (codex NR-C27: severe and critical groups were mixed for CORIMUNO-TOCI-ICU)
    if any(re.search(r"population", grp, re.I) for *_, grp in out):
        rx = AACT_POPULATION.get(label)
        out = [x for x in out if rx and re.search(rx, x[3], re.I)]
    # it types a timepoint only when it covers BOTH arms, one group each (codex NR-C27: one arm alone was admitted)
    if sorted(a for a, *_ in out) != ["c", "t"]:
        return []
    return out


AACT_POPULATION = {"CORIMUNO-TOCI-1": r"severe|moderate", "CORIMUNO-TOCI-ICU": r"critical"}


def _side(t, route, verdict):
    """Which side a per-trial disagreement falls on (g1_tracker DIVERGENCES_NAMED): a verified PRIMARY row whose counts
    the trial's OWN text states, in a recorded verbatim span, against a comparator row that differs. The comparator row
    is then not the report's count -- what it is instead (another data cut, another population) is not inferred."""
    if route not in ("PRIMARY", "TWO_SOURCE") or verdict not in ("DIFFER", "DENOMINATOR_KIND_DIFFERS") or not t["row"]:
        return None
    rd = next((r for r in t["readings"] if r["values"] == {k: t["row"][k] for k in g._KEY}), None)
    src = next((x for x in (rd or {}).get("sources") or [] if x.get("source", "").startswith("TEXT") and x.get("span")), None)
    if not src:
        return None
    rr = t["react_row"]
    # the OBSERVED difference only: 'SECONDARY_WRONG' would assert the comparator is in error, which the two tuples
    # alone do not show (codex NR-C27)
    return (f"DIFFERENT_REPORTED_TUPLE (the trial's own report states {t['row']['deaths_t']}/{t['row']['n_t']} vs "
            f"{t['row']['deaths_c']}/{t['row']['n_c']} -- {src['source']}: '{src['span'][-160:]}'; the comparator's row "
            f"is {rr['deaths_t']}/{rr['n_t']} vs {rr['deaths_c']}/{rr['n_c']}; why they differ is not inferred)")


def secondary_single(t):
    """SECONDARY_SINGLE (Mahmood decision 3 Oct), for a trial with no primary that STATES its day-28 per-arm deaths after
    the cascade: a row from a published meta that is NOT the comparator counts when
      - the meta is REACT-independent and reproduces its OWN printed pooled result (g1_toci_meta2_forest.py gates
        G1-G4, two readers printing the same counts for the same trial: meta2_rows admits only those),
      - the row binds to this trial through the meta's own reference list,
      - no other non-comparator meta row for the trial contradicts it,
      - its TIMEPOINT is typed as day 28. Neither meta types it per row (35657993: 'All outcomes were measured by authors
        at a timeframe of 14 to 28 days'), so the row is typed only when the trial's own primary states day-28 figures
        the counts reproduce (state SECONDARY_COUNT: day-28 percentages), and it is refused when it equals a count the
        primary states at another timepoint.
    Returns ({"row", "basis"}, None) or (None, why)."""
    rows = [x for x in t.get("meta2_rows") or [] if x["binding"] == "BOUND"]
    if not rows:
        return None, "NO_NON_COMPARATOR_META_ROW"
    tups = sorted({_tuple(x) for x in rows})
    why = []
    if len(tups) > 1:
        why.append("CONTRADICTED: " + "; ".join(f"meta {x['meta_pmid']} '{x['label']}' {_tuple(x)}" for x in rows))
    vnh = json.load(open(VNH, encoding="utf-8")) if os.path.exists(VNH) else {}
    for pm, v in vnh.items():
        hit = [x for x in rows if _tuple(x)[:2] == _tuple(v["counts"])[:2]] if v["label"] == t["label"] else []
        if hit:
            why.append(f"TIMEPOINT: the meta rows' tocilizumab arm {_tuple(hit[0])[:2]} is the primary's "
                       f"{v['timepoint'].upper()} count (PMID {pm}, {v['pmcid']}, VERIFIED_NOT_HELD sha256 "
                       f"{v['body_sha256'][:12]}: '{v['span']}'), not day 28")
    pct = aact_day28_percentages(t["label"]) if not why and t["state"] != g.SECONDARY_COUNT else []
    if pct:
        e = dict(zip(("t", "c"), (tups[0][:2], tups[0][2:])))
        bad = [f"{grp}: posted {v}% of {n}; the row's {e[a][0]}/{e[a][1]} = {round(100 * e[a][0] / e[a][1], 1)}%"
               for a, v, n, grp in pct if abs(100 * e[a][0] / e[a][1] - v) > 0.05 + 1e-9 or e[a][1] != n]
        if bad:
            why.append("TIMEPOINT_NOT_TYPED: AACT posts DAY-28 mortality as percentages and the row does not reproduce "
                       "every arm (" + "; ".join(bad) + ") -- a posted rate no count gives is a Kaplan-Meier estimate")
        else:
            typed_by = "AACT posted day-28 percentages (" + "; ".join(f"{grp} {v}% of {n}" for _, v, n, grp in pct) + ")"
    if not why and t["state"] != g.SECONDARY_COUNT and not pct:
        why.append("TIMEPOINT_NOT_TYPED: the meta states only a 14-28 day window and no primary states day-28 figures "
                   "this row reproduces" + (" (primary states: " + "; ".join(o["timepoint"] for o in
                                                                             t.get("other_timepoint_statements") or []) + ")"
                                            if t.get("other_timepoint_statements") else ""))
    # a SECONDARY_COUNT reading types the meta row only if it IS that row's tuple (codex NR-C27: a different tuple was
    # admitted on the state alone)
    if not why and t["state"] == g.SECONDARY_COUNT and tuple((t.get("row") or {}).get(k) for k in g._KEY) != tups[0]:
        why.append(f"TIMEPOINT_NOT_TYPED: the primary-consistent reading {tuple((t.get('row') or {}).get(k) for k in g._KEY)} "
                   f"is not the meta row {tups[0]}")
    if why:
        return None, " | ".join(why)
    tup = tups[0]
    metas = sorted({x["meta_pmid"] for x in rows})
    return {"row": dict(zip(g._KEY, tup)),
            "basis": (f"SECONDARY_SINGLE: {len(rows)} REACT-independent meta row(s) {', '.join(repr(x['label']) for x in rows)} "
                      f"(metas {', '.join(metas)}; each reproduces its own printed pooled result; two readers agree) "
                      f"print {tup}; " + (f"typed day 28 by {typed_by}" if pct else
                                          "the trial's open primary states day-28 PERCENTAGES these counts reproduce")
                      + ", never the counts -- queued for primary verification")}, None


def _route(t, best):
    """PRIMARY: two primaries (AACT + the trial's own text), or ONE bound primary that STATES the counts (Mahmood 2 Oct:
    one bound PRIMARY source verifies a row; a converted percentage never does). TWO_SOURCE: one primary plus the
    second meta. SECONDARY_SINGLE: see secondary_single. Anything less is not countable."""
    if t["state"] == g.ESTABLISHED:
        return "PRIMARY" if {"AACT", "TEXT"} <= set(best["independent_sources"]) else "TWO_SOURCE"
    if t["state"] == g.ONE_SOURCE and best and best.get("counts_stated_by") and best["denominator_kind"] != g.SAFETY:
        return "PRIMARY"
    if secondary_single(t)[0]:
        return "SECONDARY_SINGLE"
    return ROUTE[t["state"]]


def _row(d):
    return {"measure": "OR", "effect": None, "lower": None, "upper": None, "events_t": d["deaths_t"], "n_t": d["n_t"],
            "events_c": d["deaths_c"], "n_c": d["n_c"]} if d else None


def build():
    r = g.run()
    rx = g.react()
    trials = []
    for t in r["trials"]:
        rv = t["react_row"]
        best = next((x for x in t["readings"] if x["values"] == {k: (t["row"] or {}).get(k) for k in g._KEY}), None) \
            if t["row"] else None
        basis = ("two independent sources: " + " + ".join(best["independent_sources"]) if t["state"] == g.ESTABLISHED else
                 "one primary source: " + " + ".join(best["independent_sources"]) + "; no independent second source held"
                 if t["state"] == g.ONE_SOURCE and best else
                 "primary sources disagree" if t["state"] == g.CONFLICT else
                 "only a SAFETY-population count is held (" + "; ".join(sorted({s["source"] for x in t["readings"]
                 for s in x["sources"]})) + "); no efficacy-population 28-day count stated"
                 if t["readings"] and all(x["denominator_kind"] == g.SAFETY for x in t["readings"]) else
                 "no held primary source states 28-day deaths per arm (" + "; ".join(t["texts_held"]) + ")"
                 if t["texts_held"] else "no primary report held after the full cascade")
        if t["state"] == g.ONE_SOURCE and best and not best.get("counts_stated_by"):
            basis = ("one primary source, and it does not STATE the counts: " + " + ".join(best["independent_sources"])
                     + " gives a posted percentage converted to counts (a rate or a Kaplan-Meier estimate); no source "
                       "states the per-arm deaths")
        if t["state"] == g.SECONDARY_COUNT:
            basis = ("counts printed only by a meta (" + "; ".join(best["counts_stated_by"]) + "); every primary gives a "
                     "percentage consistent with them (a registry rate / Kaplan-Meier estimate, or text percentages) -- "
                     "a primary must state the counts (plant Q15)")
        ots = t.get("other_timepoint_statements") or []
        if ots:
            basis += ("; its open report states deaths only at: " + "; ".join(f"{o['timepoint']} ({o['source'].split(' (')[0]})"
                                                                         for o in ots)
                      + ". REACT's rows are trialist-supplied day-28 data ('All trials supplied data until 28 days after "
                        "randomization'), so this row cannot be matched from open sources")
        verdict = t["vs_react"]["verdict"]
        route = _route(t, best)
        ss, ss_why = secondary_single(t)
        if route == "PRIMARY" and t["state"] == g.ONE_SOURCE:
            basis = ("one bound primary that STATES the counts (" + " + ".join(s["source"] for s in best["sources"]) +
                     "): a verified row (Mahmood 2 Oct)" + (
                         "; a non-comparator meta prints " + "; ".join(f"{x['label']} {_tuple(x)}" for x in t.get('meta2_rows') or [])
                         + " (another data cut), not used" if t.get("meta2_rows") else ""))
        elif route == "SECONDARY_SINGLE":
            basis = ss["basis"]
        elif route not in COUNTABLE:
            basis += f" | SECONDARY_SINGLE refused: {ss_why}"
        value = t["row"] if route != "SECONDARY_SINGLE" else ss["row"]
        trials.append({
            "label": t["label"], "family": t["registration"], "in_our_pool": None, "route": route,
            "basis": basis, "g1_state": t["state"], "identity": t["identity"],
            "comparator_row": _row(rv), "comparator_row_findings": (
                [{"finding": "COMPARATOR_ROW_IS_SAFETY_POPULATION", "source": t["vs_react"].get("safety_source")}]
                if verdict == "REACT_ROW_IS_SAFETY_POPULATION" else []),
            "our_value": _row(value), "our_denominator_kind": (t["row"] or {}).get("denominator_kind"),
            "readings": t["readings"], "g1_countable": route in COUNTABLE,
            "secondary_single": ({"state": "NOT_NEEDED (a primary verifies the row)"} if route in ("PRIMARY", "TWO_SOURCE")
                                 else {"state": "ADMITTED" if ss else "REFUSED", "why": ss_why}),
            "acquisition_cascade": cascade_summary(t["label"]),
            "agreement_with_comparator_row": (("AGREE" if verdict == "AGREE" else "DISAGREE"
                                               if verdict in ("DIFFER", "DENOMINATOR_KIND_DIFFERS") else verdict)
                                              if route != "SECONDARY_SINGLE" else
                                              ("AGREE" if ss["row"] == {k: rv[k] for k in g._KEY} else "DISAGREE"))
            if value else "NO_PRIMARY_ROW",
            "disagreement_side": _side(t, route, verdict)})
    est = [t for t in trials if t["g1_state"] == g.ESTABLISHED]
    mat = [t for t in trials if t["route"] in COUNTABLE]          # matched = a verified typed tuple (k-gap 9abe38d3)
    pe, pr = r["pool_ours_established"], r["pool_react_same_trials"]
    rows_any = [x for x in r["trials"] if x["row"]]
    pa = g.pool_fe([x["row"] for x in rows_any])
    pra = g.pool_fe([x["react_row"] for x in rows_any])
    gv = rx["governing"]
    size = {x["label"]: x["n_t"] + x["n_c"] for x in rx["rows"]}
    n_all, n_est = sum(size.values()), sum(size[t["label"]] for t in est)
    n_mat = sum(size[t["label"]] for t in mat)
    by_route = {r_: sum(1 for t in mat if t["route"] == r_) for r_ in COUNTABLE}
    missing = sorted(((size[t["label"]], t["label"], t["g1_state"]) for t in trials if t["route"] not in COUNTABLE),
                     reverse=True)
    coverage = {"k_matched": len(mat), "k_matched_by_route": by_route, "k_established": len(est),
                "k_comparator": len(trials), "participants_matched": n_mat, "participants_established": n_est,
                "participants_comparator": n_all, "participant_share": round(n_mat / n_all, 3),
                "largest_trials_not_matched": [{"trial": l, "n": n, "state": st} for n, l, st in missing[:4]]}
    label = (f"COVERAGE-LIMITED RECONCILIATION, NOT A FINDING: {len(mat)} of {len(trials)} trials matched ("
             + ", ".join(f"{k} {v}" for k, v in by_route.items()) + f"), {round(100 * n_mat / n_all)}% of REACT's "
             f"participants; missing " + ", ".join(f"{l} (n={n})" for n, l, _ in missing[:2]))
    return {
        "schema_version": 1, "slug": SLUG, "comparator_pmid": rx["comparator_pmid"],
        "basis": ("g1/tocilizumab.py (lane g1/tocilizumab): k matched = trials with a VERIFIED typed day-28 tuple (k-gap "
                  "9abe38d3), by route: PRIMARY (two primaries, or one bound primary that STATES the counts -- 2 Oct), "
                  "TWO_SOURCE (a primary + a REACT-independent meta), SECONDARY_SINGLE (a REACT-independent, "
                  "self-reproducing meta row typed day 28 by the trial's own primary -- 3 Oct; queued for primary "
                  "verification). Agreement with REACT's row is reported per trial, not required. REACT's rows are the "
                  "comparator only (anti-circularity)."),
        "N_comparator_trials": len(trials), "k_matched": len(mat),
        "N_eligible": len(trials), "named_differences": [],
        "open_gaps": [t["label"] for t in trials if t["route"] not in COUNTABLE],
        "comparator_findings": [{"trial": t["label"], "finding": f["finding"], "comparator_row": t["comparator_row"],
                                 "trial_report": next((x["values"] for x in t["readings"] if x["denominator_kind"] == g.SAFETY), None),
                                 "detail": "the comparator's row equals the trial report's SAFETY-population death count",
                                 "basis": f["source"]} for t in trials for f in t["comparator_row_findings"]],
        "k_ours_total": None, "routes": dict(Counter(t["route"] for t in trials)), "trials": trials,
        "per_trial_agreement": dict(Counter(t["agreement_with_comparator_row"] for t in mat)),
        "coverage": coverage,
        "result_label": label,
        "same_trials": {"state": "POOLED" if pe else "NOT_POOLED", "k": pe and pe["k_informative"],
                        "measure": f"OR [{label}]", "is_a_finding": False,
                        "method": "FE",
                        "ours": {"estimate": pe and pe["or"], "ci_low": pe and pe["lo"], "ci_high": pe and pe["hi"]},
                        "theirs": {"estimate": pr and pr["or"], "ci_low": pr and pr["lo"], "ci_high": pr and pr["hi"]},
                        "verdict": {"verdict": "AGREE" if pe == pr else "DIFFER",
                                    "conclusion": "NO_CLEAR_EFFECT" if pe and pe["lo"] < 1 < pe["hi"] else "EFFECT",
                                    "estimate_gap_over_ci_halfwidth": round(abs(pe["or"] - pr["or"]) / ((pr["hi"] - pr["lo"]) / 2), 3) if pe else None},
                        "method_basis": f"comparator positive control reproduced FE: REACT's 19 rows -> OR "
                                        f"{r['positive_control']['or']} ({r['positive_control']['lo']}-{r['positive_control']['hi']})"},
        "same_trials_incl_one_source": {"k": pa and pa["k_informative"], "ours": pa, "theirs": pra,
                                        "note": "established + one-source rows; one-source rows are NOT counted in k"},
        # NO topic result is stated: the pool of the established trials is a reconciliation of OUR rows with REACT's on
        # those trials, not an estimate of tocilizumab's effect, while the two largest trials are not established
        "ours": {"k": len(est), "estimate": None, "ci_low": None, "ci_high": None, "scale": "OR",
                 "state": "NOT_STATED: " + label},
        "comparator": {"outcome": "28-day all-cause mortality (Figure 1, tocilizumab)", "estimate": gv["estimate"],
                       "ci_low": gv["ci_low"], "ci_high": gv["ci_high"], "scale": "OR"},
        "comparator_basis": "REACT abstract/results text (VERIFIED_NOT_HELD, PMC8261689) and Figure 1 rows",
        "ours_not_in_comparator": [], "ours_not_in_comparator_detail": [],
        "secondary_tally": {}, "secondary_skipped": {}, "registry": {"snapshot": json.load(open(g.AACT_FILE, encoding="utf-8"))["snapshot"]},
    }


def main():
    import g1_tracker as gt
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d = build()
    # the SAME citation contract as every topic: every trial matched, an open gap, or named with rule ID + span
    d = gt.cite_or_demote(d, SLUG)
    d["g1_status"] = gt.g1_status(d)
    bad = gt.scope_citation_violations(d)
    if bad:
        raise SystemExit("REFUSED (scope citation): " + "; ".join(bad))
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    s = d["same_trials"]
    print(f"k matched {d['k_matched']} of {d['N_comparator_trials']} | routes {d['routes']} | same trials k={s['k']}: "
          f"ours {s['ours']} vs REACT {s['theirs']} -> {s['verdict']}")
    print("incl. one-source rows:", d["same_trials_incl_one_source"]["k"], d["same_trials_incl_one_source"]["ours"],
          "vs", d["same_trials_incl_one_source"]["theirs"])


if __name__ == "__main__":
    main()
