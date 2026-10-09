"""Independent recompute of every served pooled outcome -- a SECOND implementation, written apart from harness/synth.py.

It never imports the harness (tests/test_independent_recompute.py checks the import graph). It reads only:
  * the served trial tuples in docs/reviews/<slug>/review.json (outcome.trials: effect+CI, 2x2 counts, events + person-time,
    or arm means/SDs/n), and
  * the outcome's declared method string (outcome.method).
It then recomputes the pooled estimate and interval itself and compares with the served result.

Method (from the declared method text): inverse-variance random effects, Paule-Mandel tau^2 (own root-finder),
modified Hartung-Knapp-Sidik-Jonkman interval on t(k-1) with variance factor max(1, Q_gen/(k-1)); ratio measures on the
log scale, mean differences on the raw scale. Input conventions are the published ones the method text names:
SE from a 95% CI = width / (2 * z_0.975); a 2x2 gets +0.5 on all cells only when it has a zero cell; an incidence-rate
ratio has variance 1/e1 + 1/e2. At k=1 the interval is the single study's own (a reported CI verbatim, else Wald z).
At k=2 the review withholds the interval, so only the point estimate is compared.

    python audit/independent_recompute.py [--json]
Exit 0 iff every recomputable served outcome agrees (|recomputed - served| <= 1.5e-4 on the printed 4-dp values).
Rows it cannot rebuild from the served tuple alone (design-adjusted variance) are listed as NOT_RECOMPUTABLE, never passed.
"""
from __future__ import annotations

import glob
import json
import math
import os
import sys

from scipy.stats import norm, t as student_t

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z = float(norm.ppf(0.975))
TOL = 1.5e-4


def _is_md(scale):
    s = str(scale or "").upper().strip()
    return s == "MD" or s.startswith("MD ") or s.startswith("MD(") or s == "MEAN DIFFERENCE"


RATIO = {"RR", "OR", "HR", "IRR"}
# Which explicit row measures may sit inside an outcome of a given served scale. RR and HR share the first-event ratio class
# (the source hierarchy serves a published HR beside a counts RR); an OR, an IRR or an MD row must match exactly.
COMPATIBLE = {"RR": {"RR", "HR"}, "HR": {"RR", "HR"}, "OR": {"OR"}, "IRR": {"IRR"}, "MD": {"MD"}}


def _supported(scale):
    """Only the measures the declared method names and this check rebuilds: log ratios (RR/OR/HR/IRR) and the RAW mean
    difference. A standardised mean difference, a risk difference or an unlabelled scale is NOT_RECOMPUTABLE -- never read
    as a ratio or as a raw MD (codex ext-audit-r1/r2 P0)."""
    s = str(scale or "").upper().strip()
    return _is_md(s) or s in RATIO


def _scale_class(scale):
    return "MD" if _is_md(scale) else str(scale or "").upper().strip()


def _finite(*xs):
    return all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in xs)


def study_y_v(row, outcome_scale):
    """(y, v) for one served trial tuple, or raises ValueError naming why it cannot be rebuilt."""
    g = row.get
    if g("design_adjustment") or (g("design") or {}).get("design_adjustment"):
        raise ValueError("design-adjusted variance is not carried in the served tuple")
    if g("mean1") is not None and g("sd1") is not None and g("nc1"):
        # the TUPLE KIND must match the outcome (codex ext-audit-r3 P0): arm means build a raw MD only
        if not _is_md(outcome_scale):
            raise ValueError(f"arm means cannot rebuild an outcome served as {outcome_scale}")
        return g("mean1") - g("mean2"), g("sd1") ** 2 / g("nc1") + g("sd2") ** 2 / g("nc2")
    if _is_md(outcome_scale) and g("effect") is None:
        raise ValueError("a count or rate tuple cannot rebuild a mean difference")
    if g("e1i") is not None and g("t1i") and g("e2i") is not None and g("t2i"):
        e1, e2 = float(g("e1i")), float(g("e2i"))
        if min(e1, e2) == 0:
            e1, e2 = e1 + 0.5, e2 + 0.5
        return math.log((e1 / g("t1i")) / (e2 / g("t2i"))), 1 / e1 + 1 / e2
    if g("ai") is not None and g("n1i"):
        a, n1, c, n2 = (float(g(k)) for k in ("ai", "n1i", "ci", "n2i"))
        if not (0 <= a <= n1 and 0 <= c <= n2 and n1 > 0 and n2 > 0):
            raise ValueError(f"impossible 2x2: {a}/{n1} v {c}/{n2}")   # codex ext-audit-r3 P0
        if min(a, c, n1 - a, n2 - c) == 0:
            a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1, n2 + 1
        measure = str(g("measure") or g("scale") or outcome_scale or "").upper()
        if measure in ("HR", "IRR"):
            measure = "RR"          # a first-event / rate outcome's 2x2 row is a reconstructed risk ratio
        if measure not in ("RR", "OR"):
            raise ValueError(f"a 2x2 row on measure {measure or '<none>'} is not a log ratio this check rebuilds")
        if measure == "OR":
            b, d = n1 - a, n2 - c
            return math.log(a * d / (b * c)), 1 / a + 1 / b + 1 / c + 1 / d
        return math.log((a / n1) / (c / n2)), 1 / a - 1 / n1 + 1 / c - 1 / n2
    if g("effect") is not None and g("ci_low") is not None and g("ci_high") is not None:
        if not (g("ci_low") <= g("effect") <= g("ci_high")) or g("ci_low") == g("ci_high"):
            raise ValueError("reported interval is reversed, degenerate or excludes its own point")   # codex ext-audit-r3 P0
        if _is_md(g("scale") or outcome_scale):
            return float(g("effect")), ((g("ci_high") - g("ci_low")) / (2 * Z)) ** 2
        return math.log(g("effect")), ((math.log(g("ci_high")) - math.log(g("ci_low"))) / (2 * Z)) ** 2
    raise ValueError("no effect+CI, 2x2, rate or arm-means tuple")


def paule_mandel(y, v):
    k = len(y)

    def q_gen(tau2):
        w = [1 / (vi + tau2) for vi in v]
        mu = sum(wi * yi for wi, yi in zip(w, y)) / sum(w)
        return sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y))

    if k < 2 or q_gen(0.0) <= k - 1:
        return 0.0
    # bracket relative to the data's own scale (codex ext-audit-r3 P2: an absolute cap failed large-unit MDs)
    spread = max(y) - min(y)
    lo, hi = 0.0, max(1.0, spread * spread)
    while q_gen(hi) > k - 1:
        hi *= 2.0
        if not math.isfinite(hi) or hi > 1e6 * max(1.0, spread * spread):
            raise ArithmeticError("PM root not bracketed")
    for _ in range(200):
        mid = (lo + hi) / 2
        if q_gen(mid) > k - 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pool(y, v):
    k = len(y)
    tau2 = paule_mandel(y, v)
    w = [1 / (vi + tau2) for vi in v]
    sw = sum(w)
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    if k == 1:
        return mu, mu - Z * math.sqrt(1 / sw), mu + Z * math.sqrt(1 / sw)
    qg = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y))
    se = math.sqrt(max(1.0, qg / (k - 1)) / sw)
    tc = float(student_t.ppf(0.975, k - 1))
    return mu, mu - tc * se, mu + tc * se


def recompute_outcome(o):
    res = o.get("result") or {}
    scale = res.get("scale") or o.get("served_estimand") or o.get("estimand")
    if not _supported(scale):
        return {"state": "NOT_RECOMPUTABLE", "why": f"served scale {scale!r} is not a measure the declared method names"}
    method = str(o.get("method") or "")
    trials = o.get("trials") or []
    single = method.startswith("Single included trial") and "own effect" in method
    if single and len(trials) != 1:
        return {"state": "DISAGREE", "why": f"declared single-trial method but {len(trials)} trial tuples served"}
    if not single and ("Paule-Mandel" not in method or "HKSJ" not in method):
        return {"state": "NOT_RECOMPUTABLE", "why": "declared method is neither PM + HKSJ nor single-trial: " + method[:80]}
    allowed = COMPATIBLE.get(_scale_class(scale), set())
    for t in trials:
        m = t.get("measure") or t.get("scale")
        if m and _scale_class(m) not in allowed:
            return {"state": "DISAGREE", "why": f"a trial row on {m} sits in an outcome served as {scale} (incompatible measures)"}
    try:
        yv = [study_y_v(t, scale) for t in trials]
    except ValueError as exc:
        return {"state": "NOT_RECOMPUTABLE", "why": str(exc)}
    if not yv:
        return {"state": "NOT_RECOMPUTABLE", "why": "no trial tuples served"}
    if not all(_finite(y, v) and v > 0 for y, v in yv):
        return {"state": "DISAGREE", "why": "a served trial tuple gives a non-finite effect or non-positive variance"}
    mu, lo, hi = pool([y for y, _ in yv], [v for _, v in yv])
    back = (lambda x: x) if _is_md(scale) else math.exp
    est, cl, ch = back(mu), back(lo), back(hi)
    if len(trials) == 1 and trials[0].get("effect") is not None and trials[0].get("ci_low") is not None:
        # declared: the single trial's OWN effect -- a reported effect + CI is served verbatim, never re-derived
        t0 = trials[0]
        est, cl, ch = t0["effect"], t0["ci_low"], t0["ci_high"]
    compared = {"estimate": (est, res.get("estimate"))}
    if (res.get("ci_low") is None) != (res.get("ci_high") is None):
        return {"state": "DISAGREE", "why": "the served interval has one bound only (withholding needs both absent)"}
    if res.get("ci_low") is not None and res.get("ci_high") is not None:
        compared["ci_low"] = (cl, res["ci_low"])
        compared["ci_high"] = (ch, res["ci_high"])
    elif len(trials) != 2:
        return {"state": "DISAGREE", "why": f"served CI absent at k={len(trials)} (only k=2 withholds it)",
                "recomputed": {"estimate": est, "ci_low": cl, "ci_high": ch}}
    # fail closed: a non-finite side never agrees (abs(nan - x) > TOL is False -- codex ext-audit-r1 P0)
    bad = {f: (a, b) for f, (a, b) in compared.items()
           if not _finite(a) or not _finite(b) or not abs(float(a) - float(b)) <= TOL}
    return {"state": "DISAGREE" if bad else "AGREE", "k": len(trials), "scale": scale,
            "compared": {f: (round(a, 6), b) for f, (a, b) in compared.items()}, "mismatch": bad}


def run(root=ROOT):
    rows = []
    for f in sorted(glob.glob(os.path.join(root, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(f))
        r = json.load(open(f, encoding="utf-8"))
        for o in r.get("outcomes") or []:
            if (o.get("result") or {}).get("estimate") is None:
                continue
            rows.append({"slug": slug, "outcome": o.get("name"), **recompute_outcome(o)})
    return rows


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    rows = run()
    if "--json" in argv:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            if r["state"] != "AGREE":
                print(f"[{r['state']}] {r['slug']} | {r['outcome']} | {r.get('why') or r.get('mismatch')} "
                      f"{r.get('compared') or r.get('recomputed') or ''}")
        n = {s: sum(1 for r in rows if r["state"] == s) for s in ("AGREE", "DISAGREE", "NOT_RECOMPUTABLE")}
        print(f"INDEPENDENT-RECOMPUTE: {len(rows)} served pooled outcomes: {n}")
    # fail closed: an outcome this check could not rebuild is unverified, not passed (codex ext-audit-r1 P1)
    return 1 if (not rows or any(r["state"] != "AGREE" for r in rows)) else 0


if __name__ == "__main__":
    sys.exit(main())
