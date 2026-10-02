"""G1 FOCUS REPORT (Mahmood decisions, 2 Oct): the four focus topics, per topic --
  k matched n of N   comparator trials (k-gap table, other agents excluded) that are in OUR pool, rebuilt on this branch
  rows by route      PRIMARY (our extraction of the trial's own report / posted CT.gov results, or a meta row typed-
                     matched to one) / TWO_SOURCE (two independent metas agree) / UNVERIFIED (secondary only, queued,
                     mismatched or blocked) / NO_ROW (no number from any source; the gap class says why)
  per-trial agreement our pooled row vs the COMPARATOR's own row for the same trial, typed (rounding-aware)
  result vs comparator our branch pool vs the comparator's printed pooled result
Everything is derived from committed artefacts + the in-memory rebuild; nothing is typed by hand.

    python scripts/g1_focus_report.py   -> outputs/k_gap/G1_FOCUS.json + G1_FOCUS.md
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402

FOCUS = ["glp1-ra-mace-t2d", "semaglutide-obesity-weight", "noac-vs-warfarin-af-stroke", "tocilizumab-covid19-mortality"]
OUT = os.path.join(ROOT, "outputs", "k_gap")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _row(d):
    return sm.SecondaryRow(**{k: v for k, v in d.items() if k in sm.SecondaryRow.__dataclass_fields__})


def agreement(ours, theirs):
    """Our pooled value vs the comparator's printed row for the same trial: AGREE / DISAGREE / NOT_COMPARABLE."""
    if not ours or not theirs:
        return "NOT_COMPARABLE"
    if ours.get("events_t") is not None and theirs.events_t is not None:
        same = (ours["events_t"], ours["n_t"], ours["events_c"], ours["n_c"]) == \
               (theirs.events_t, theirs.n_t, theirs.events_c, theirs.n_c)
        return "AGREE" if same else "DISAGREE"
    if ours.get("effect") is None or theirs.effect is None:
        return "NOT_COMPARABLE"
    if (ours.get("measure") or "").upper() != theirs.measure.upper():
        return f"NOT_COMPARABLE:{ours.get('measure')}_VS_{theirs.measure}"
    eq = all(sm._eq_printed(a, b) for a, b in ((ours["effect"], theirs.effect), (ours["lower"], theirs.lower),
                                                 (ours["upper"], theirs.upper)))
    return "AGREE" if eq else "DISAGREE"


def topic(slug, T):
    import secondary_meta_build as smb
    import k_gap_counterfactual as cfm
    S = _j(os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json"))
    comp = S["comparator_pmid"]
    ours = smb.our_trials(slug)
    core = cfm.build(slug)
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    pooled_ids = {str(t.get("id")) for t in prim.get("trials", [])}
    rows = [_row(d) for d in S["rows"]]
    by_fam = {}
    for r in rows:
        by_fam.setdefault(r.family_id, []).append(r)
    comp_rows = [t for t in T["trials"] if t["slug"] == slug and t.get("drug") != "OTHER_AGENT"]
    trials, routes = [], Counter()
    for t in comp_rows:
        mine = next((o for o in ours if (o.get("nct") and o["nct"] in (t.get("ncts") or []))
                     or o["pmid"] in (t.get("pmids") or [])), None)
        fam = mine["id"] if mine else None
        in_pool = bool(mine and str(mine["id"]) in pooled_ids and mine.get("primary"))
        sec = by_fam.get(fam, []) if fam else []
        theirs = next((r for r in sec if r.meta_pmid == comp), None)
        if in_pool:
            route, basis = "PRIMARY", mine["primary"]["source"]
        else:
            best = sorted(sec, key=lambda r: {"PRIMARY": 0, "TWO_SOURCE": 1}.get(sm.route_of(r), 2))
            if best and best[0].state != sm.REFUSED:
                route = sm.route_of(best[0])
                basis = f"meta {best[0].meta_pmid} {best[0].state} {(best[0].verification or {}).get('route') or ''}".strip()
            else:
                route = "NO_ROW"
                basis = t.get("gap_class") + (f" (secondary refused: {sorted({x for r in sec for x in r.reasons})[:3]})"
                                              if sec else "")
        routes[route] += 1
        trials.append({"label": t["label"][:60], "family": fam, "in_our_pool": in_pool, "route": route, "basis": basis,
                       "g1_countable": route in ("PRIMARY",) or bool(sm.g1_countable(sec, {comp})),
                       "agreement_with_comparator_row": agreement(mine and mine.get("primary"), theirs) if in_pool
                       else "NOT_IN_OUR_POOL", "comparator_row_state": theirs.state if theirs else None})
    res = prim.get("result") or {}
    rep = ((_j(os.path.join(ROOT, "docs", "reviews", slug, "review.json")).get("comparator") or {}).get("reported")
           or [{}])[0]
    n = sum(1 for x in trials if x["in_our_pool"])
    return {"slug": slug, "comparator_pmid": comp, "N_comparator_trials": len(trials), "k_matched": n,
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if x["in_our_pool"])),
            "ours": {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")},
            "comparator": {k: rep.get(k) for k in ("outcome", "estimate", "ci_low", "ci_high", "scale")},
            "secondary_tally": S["tally"], "secondary_skipped": S["skipped"]}


def _fmt(r):
    if r.get("estimate") is None:
        return "not printed"
    lo, hi = r.get("ci_low"), r.get("ci_high")
    ci = f" ({lo:.2f} to {hi:.2f})" if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) else " (no CI)"
    return f"{r.get('scale')} {r['estimate']:.2f}{ci}"


def main():
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    out = [topic(s, T) for s in FOCUS]
    with open(os.path.join(OUT, "G1_FOCUS.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"topics": out}, fh, indent=1, ensure_ascii=False)
    md = ["# G1 focus topics (derived by scripts/g1_focus_report.py)", "",
          "| topic | k matched | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | ours | comparator |",
          "|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        r = o["routes"]
        md.append(f"| {o['slug']} | {o['k_matched']} of {o['N_comparator_trials']} | {r.get('PRIMARY', 0)} | "
                  f"{r.get('TWO_SOURCE', 0)} | {r.get('UNVERIFIED', 0)} | {r.get('NO_ROW', 0)} | "
                  f"{o['per_trial_agreement']} | {_fmt(o['ours'])} k={o['ours'].get('k')} | {_fmt(o['comparator'])} |")
    for o in out:
        md += ["", f"## {o['slug']} (comparator PMID {o['comparator_pmid']})", ""]
        for x in o["trials"]:
            md.append(f"- {x['label']}: **{x['route']}** - {x['basis']}; vs comparator row: "
                      f"{x['agreement_with_comparator_row']}")
    with open(os.path.join(OUT, "G1_FOCUS.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md[:8]))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
