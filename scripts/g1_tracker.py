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
    return out


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
    trials, routes, pairs, matched_ids = [], Counter(), [], set()
    for t in comp_rows:
        mine = next((o for o in ours if (o.get("nct") and o["nct"] in (t.get("ncts") or []))
                     or o["pmid"] in (t.get("pmids") or [])), None)
        fam = mine["id"] if mine else None
        in_pool = bool(mine and str(mine["id"]) in pooled_ids and mine.get("primary"))
        sec = by_fam.get(fam, []) if fam else []
        theirs = next((r for r in sec if r.meta_pmid == comp and r.state != sm.REFUSED), None)
        if in_pool:
            matched_ids.add(str(mine["id"]))
            route, basis = "PRIMARY", mine["primary"]["source"]
            if theirs:
                pairs.append((as_row(mine["primary"], t["label"], theirs.measure), theirs))
        else:
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
                       "g1_countable": route == "PRIMARY" or bool(sm.g1_countable(sec, {comp})),
                       "agreement_with_comparator_row": agreement(mine and mine.get("primary"), theirs) if in_pool
                       else "NOT_IN_OUR_POOL", "comparator_row_state": theirs.state if theirs else None})
    pc = ((S.get("metas") or {}).get(comp) or {}).get("positive_control") or {}
    method = (pc.get("methods") or ["PM"])[0]
    res = prim.get("result") or {}
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    rep = ((rev.get("comparator") or {}).get("reported") or [{}])[0]
    extra = sorted(str(t.get("id")) for t in prim.get("trials", []) if str(t.get("id")) not in matched_ids)
    return {"schema_version": SCHEMA_VERSION, "slug": slug, "comparator_pmid": comp,
            "N_comparator_trials": len(trials), "k_matched": sum(1 for x in trials if x["in_our_pool"]),
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if x["in_our_pool"])),
            "same_trials": dict(same_trials_pool(pairs, method),
                                method_basis=("comparator positive control reproduced " + method) if pc.get("methods")
                                else "comparator positive control not reproduced: PM default"),
            "ours": {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")},
            "comparator": {k: rep.get(k) for k in ("outcome", "estimate", "ci_low", "ci_high", "scale")},
            "ours_not_in_comparator": extra,
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
        same = (f"{st['measure']} {_fmt(st['ours'])} vs {_fmt(st['theirs'])}, k={st['k']}, {st['method']}"
                if st.get("state") == "POOLED" else st.get("state"))
        md.append(f"| {o['slug']} | {o['k_matched']} of {o['N_comparator_trials']} | {r.get('PRIMARY', 0)} | "
                  f"{r.get('TWO_SOURCE', 0)} | {r.get('UNVERIFIED', 0)} | {r.get('NO_ROW', 0)} | "
                  f"{o['per_trial_agreement']} | {same} | {_fmt(o['ours'])} k={o['ours'].get('k')} | {_fmt(o['comparator'])} |")
    for o in out:
        md += ["", f"## {o['slug']} (comparator PMID {o['comparator_pmid']})", ""]
        for x in o["trials"]:
            md.append(f"- {x['label']}: **{x['route']}** - {x['basis']}; vs comparator row: "
                      f"{x['agreement_with_comparator_row']}")
        if o["ours_not_in_comparator"]:
            md.append(f"- pooled by us, not listed by the comparator: {', '.join(o['ours_not_in_comparator'])}")
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
